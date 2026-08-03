# Spec 05 — Crawler policy + llms.txt size budget

> **Theme:** policy & build · **Effort:** low-medium · **Blocks:** nothing
> **Status:** proposed · **⚠ Ship this first — see below**

## Why this is urgent

Measured 2026-08-03 on a clean build:

| File | Size | Cap | Headroom | Growth per advisory |
|---|---|---|---|---|
| `llms-ctx.txt` | 130,989 B | 131,072 B | **83 B** | ~1,200 B |
| `llms.txt` | 64,719 B | 65,536 B | 817 B | ~600 B |
| `llms-full.txt` | 927,321 B | 983,040 B | 55,719 B | ~7,700 B |

**The next advisory breaks the build.** `llms-ctx.txt` has 83 bytes of headroom
and gains roughly 1,200 bytes per advisory. `llms.txt` survives one more, maybe.
Any sweep fails CI before it fails review.

## The actual problem

This has happened four times. From the comment block at the top of
`tests/test_llms.py`:

- 2026-05-30 — ctx 64KB → 96KB
- 2026-06-01 — full 512KB → 640KB
- 2026-06-19 — index 50→64KB, full 640→896KB, ctx 96→128KB
- 2026-07-01 — full 896KB → 960KB

Each entry is more apologetic than the last. The 2026-07-01 note calls itself "a
stopgap per BACKLOG.md's own guidance."

The diagnosis in BACKLOG.md is that the caps are too low. **That diagnosis is
wrong.** The caps are constants; the files are `O(n)` in the advisory count. No
constant is large enough for an unbounded series. Raising it buys weeks, and the
gap between bumps shrinks as the sweep cadence rises.

### The logged fix does not work

BACKLOG.md line 79 states the real fix as: *"exclude `status: historical` (and
maybe `patched` older than N months) from the concatenated files."*

There are **zero advisories with `status: historical`.** The status distribution
across all 107:

| Status | Count | Bytes |
|---|---|---|
| `patched` | 39 | 302,132 |
| `active` | 32 | 255,317 |
| `contained` | 25 | 187,717 |
| `mitigated` | 6 | 48,122 |
| `ongoing` | 2 | 14,687 |
| `unconfirmed` | 2 | 13,184 |
| `historical` | **0** | **0** |

`historical` is a valid enum value in the schema that nothing has ever used.
Implementing the logged fix as written would trim nothing and the next sweep
would still fail. Anyone who picks up that backlog item will lose an afternoon
before discovering this — which is the main reason this spec exists.

## Proposal

Two independent deliverables:

1. **Bounded LLM outputs** — make the files `O(1)`, then set a budget policy with
   enforced headroom so the test fails weeks before the deploy does.
2. **An explicit crawler allowlist** — turn "AI training explicitly allowed" from
   an implicit consequence of `Allow: /` into a stated, test-locked contract.

---

## Deliverable 1 — Bounded outputs and a real budget policy

### The rule: full detail for recent, one-liners for the rest

Every LLM output gets a two-tier structure. Recent advisories appear in full;
older ones become a single navigable line. Total size stops depending on corpus
size.

| File | Tier 1 (full) | Tier 2 (one-line) | Bounded at |
|---|---|---|---|
| `llms.txt` | 60 most recent, with descriptions | remainder: `- [title](url) — severity/date` | ~48 KB |
| `llms-ctx.txt` | 40 most recent: TL;DR + "Am I affected?" | remainder: title + URL + severity | ~64 KB |
| `llms-full.txt` | 60 most recent, full body | remainder: title + URL + link to `.md` mirror | ~560 KB |

Nothing disappears. Every advisory keeps its own page, its `.md` mirror, its
`advisories.json` row, its per-section `llms.txt` entry, and its sitemap entry.
Tier 2 is a pointer, not a deletion — and that distinction should be stated in
each file's header so a consuming model knows more exists and how to reach it.

**Ordering.** Sort by `last_updated` descending, not `date_disclosed`. An old
incident that got substantive new analysis this week is more relevant than a
quiet one disclosed last month, and `build_atom_feed()`
([site/build.py:961](../../site/build.py)) already uses this ordering — matching
it keeps the two consistent.

**Always-include override.** Anything with `status: active` or `ongoing` stays in
Tier 1 regardless of age. A live incident is exactly what a model needs in full,
and there are only 34 of them. Implement as: Tier 1 = (N most recent) ∪ (all
active/ongoing).

### Immediate relief

For `llms-ctx.txt`, capping Tier 1 at 40 advisories takes it from 107 × ~1,200 B
to roughly 40 × ~1,200 B + 67 × ~120 B ≈ **56 KB**, against a 128 KB cap. From 83
bytes of headroom to ~72 KB, and it stops growing.

### The budget policy

Write it into `tests/test_llms.py`, replacing the archaeology of bump notes:

```python
# ─── llms.txt size budget policy ────────────────────────────────────────────
#
# These caps are a CONTRACT, not a high-water mark. They are not to be raised
# to make a failing build pass — that loop ran four times (2026-05-30, 06-01,
# 06-19, 07-01) and each bump bought less time than the last.
#
# The outputs are two-tier and bounded (see build_llms_*): the N most recent
# advisories plus all active/ongoing ones appear in full; everything older is a
# one-line pointer. Size is therefore O(1) in corpus size, not O(n).
#
# If a cap is breached, the correct fixes, in order:
#   1. Lower the Tier-1 count. That is the intended control surface.
#   2. Tighten per-advisory truncation limits.
#   3. Only then, and only with a written rationale here, raise a cap.
#
# HEADROOM_FRACTION makes the test fail while there is still room to think.
# A build at 88% of budget is a warning; the previous regime only ever
# reported failure at 100%, one advisory too late.

LLMS_TXT_MAX_BYTES  =  64 * 1024
LLMS_CTX_MAX_BYTES  = 128 * 1024
LLMS_FULL_MAX_BYTES = 960 * 1024
HEADROOM_FRACTION   = 0.15   # must stay under 85% of cap
```

```python
@pytest.mark.parametrize("name,cap", [
    ("llms.txt", LLMS_TXT_MAX_BYTES),
    ("llms-ctx.txt", LLMS_CTX_MAX_BYTES),
    ("llms-full.txt", LLMS_FULL_MAX_BYTES),
])
def test_llms_output_within_budget(dist_dir, name, cap):
    size = (dist_dir / name).stat().st_size
    budget = int(cap * (1 - HEADROOM_FRACTION))
    assert size <= budget, (
        f"{name} is {size:,} B — over the {budget:,} B budget ({size/cap:.0%} of "
        f"the {cap:,} B cap). Lower the Tier-1 count; do not raise the cap. "
        f"See the budget policy at the top of this file."
    )
```

The failure message carries the policy. Someone hitting this at 23:00 during a
sweep should not have to find this document to know what to do.

### The test that stops the treadmill

```python
def test_llms_outputs_are_bounded_not_linear():
    """Tier-1 counts are what bound these files. If this test fails, someone
    removed the bound and the caps became load-bearing again."""
    assert LLMS_TXT_TIER1 <= 60
    assert LLMS_CTX_TIER1 <= 40
    assert LLMS_FULL_TIER1 <= 60
```

Also: **delete `historical` from the status enum**, or use it. A never-used enum
value is what produced a backlog item that would have shipped a no-op. Given the
corpus, deleting is right — `patched` and `contained` already cover it.

---

## Deliverable 2 — Explicit AI crawler allowlist

### Current state

`build_robots()` ([site/build.py:951](../../site/build.py)) emits nine lines:

```
# Crawlers welcome. AI/LLM training: explicitly allowed.
User-agent: *
Allow: /
Sitemap: https://pranava0x0.github.io/vibe-coding-security/sitemap.xml
```

The intent is right and the comment says so. But the permission is *implicit* —
it follows from the wildcard, not from a decision. Three consequences:

- A future edit narrowing the wildcard would silently revoke it, with no test
  failing.
- Crawlers that look for their own named `User-agent` block before falling back
  to `*` get no explicit signal.
- The repo's most distinctive editorial stance — **this security data should be
  maximally reachable by AI systems, because the audience *is* people using AI
  coding tools** — is expressed in a comment rather than in the artifact.

### Proposal: state it, then lock it

```
# ── Crawler policy ──────────────────────────────────────────────────────────
# This is a public-interest security corpus, CC0 / public domain.
# AI training, retrieval, and agent browsing are EXPLICITLY ALLOWED and
# actively desired: the audience for this data is people building with AI
# coding tools, and the fastest path to them is often through the model
# they are already talking to.
#
# Named agents below are redundant with "User-agent: *" and intentionally so —
# they make the permission explicit rather than inferred, and site/build.py
# has a test asserting each one stays allowed.
# ────────────────────────────────────────────────────────────────────────────

User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ClaudeBot
Allow: /

... (one block per allowlisted agent)

Sitemap: https://pranava0x0.github.io/vibe-coding-security/sitemap.xml
```

### The agent list needs verifying at implementation time

Crawler user-agent tokens change, get renamed, and get split (training vs.
retrieval vs. user-triggered fetch are often distinct tokens from the same
vendor). **Do not copy a list from memory or from this document.** At
implementation time, check each vendor's current published crawler documentation
and record the check date in a comment.

Agents to look up and include, if their current tokens confirm: OpenAI's crawlers,
Anthropic's, Google's AI-specific tokens (distinct from Googlebot), Meta's,
Perplexity's, Common Crawl's `CCBot`, Amazon's, ByteDance's, Mistral's,
DuckDuckGo's, and Apple's.

Keep the list in one place in `build.py` as a module constant so the emitter and
the test read the same source:

```python
# Verified against vendor crawler docs on YYYY-MM-DD.
ALLOWED_AI_CRAWLERS: list[str] = ["GPTBot", "ClaudeBot", ...]
```

### `llms.txt` policy header

`llms.txt` is read by models directly, so state the same contract there — a short
block near the top: CC0, freely usable, attribution appreciated, and a note that
advisories are dated and should be checked for currency before being acted on.
That last clause matters: a model surfacing a March advisory as current advice is
the most likely way this data does harm.

### Tests

New `tests/test_robots.py`:

```python
def test_every_allowlisted_crawler_has_an_allow_block(dist_dir):
    """Locks the max-scrapability contract. If you are here because this failed,
    the question is whether the policy changed on purpose."""
    robots = (dist_dir / "robots.txt").read_text()
    for agent in ALLOWED_AI_CRAWLERS:
        block = re.search(
            rf"^User-agent:\s*{re.escape(agent)}\s*$\n(.*?)(?=^User-agent:|\Z)",
            robots, re.MULTILINE | re.DOTALL,
        )
        assert block, f"robots.txt has no User-agent block for {agent}"
        assert re.search(r"^Allow:\s*/\s*$", block.group(1), re.MULTILINE), (
            f"{agent} is named in robots.txt but not allowed"
        )


def test_robots_has_no_disallow_anywhere(dist_dir):
    """Max scrapability is the contract. A Disallow line is a policy change and
    must be a deliberate edit to this test, not a silent build change."""
    robots = (dist_dir / "robots.txt").read_text()
    assert "Disallow:" not in robots


def test_robots_declares_sitemap(dist_dir):
    assert "Sitemap: " in (dist_dir / "robots.txt").read_text()
```

`test_robots_has_no_disallow_anywhere` is the important one. It makes reducing
scrapability require an explicit, reviewable test edit — which is exactly the
weight that decision deserves.

---

## Done when

- [ ] Tier-1/Tier-2 structure in all three LLM outputs; `active`/`ongoing` always
      Tier 1.
- [ ] `llms-ctx.txt` under 85% of its cap with room to grow (~56 KB expected).
- [ ] Budget policy comment replaces the bump log in `tests/test_llms.py`.
- [ ] `HEADROOM_FRACTION` test with an actionable failure message.
- [ ] `test_llms_outputs_are_bounded_not_linear` asserting the Tier-1 caps.
- [ ] Tier-2 entries link to the full `.md` mirror; each file's header explains
      the two tiers.
- [ ] `historical` removed from the status enum (schema + `tests/conftest.py`).
- [ ] `ALLOWED_AI_CRAWLERS` verified against vendor docs, with the date recorded.
- [ ] `robots.txt` emits a policy header + a block per allowlisted crawler.
- [ ] `llms.txt` carries the usage/currency policy header.
- [ ] `tests/test_robots.py` green.
- [ ] BACKLOG.md's "trim historical" item corrected — it is a no-op as written.
- [ ] `build.py` → `validate.py` → `pytest` all green.

## Explicitly out of scope

- Blocking any crawler. The contract is maximum reachability; this spec makes
  that explicit and harder to reverse by accident.
- `ai.txt`, `.well-known/ai-policy`, or similar proposals — none are settled
  enough to commit to. Revisit if one gains real adoption.
- Paginating `llms-full.txt` into numbered parts. Tier-2 pointers are simpler and
  solve the same problem.
- Rewriting advisories to be shorter. Length is a content decision; Spec 06 is
  where prose quality lives.
