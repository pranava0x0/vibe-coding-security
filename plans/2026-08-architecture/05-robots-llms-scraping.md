# Spec 05 — robots.txt / llms.txt: a deliberate, tested contract with AI crawlers

**Goal.** Maximize legitimate scraping and LLM ingestion of this site — the opposite of
most sites' posture, and on purpose: our mission is to be inside every coding agent's
context when it decides whether to install something.

**Motivated by.** Glasswing/Daybreak mean the highest-value reader is now an agent.
If ClaudeBot/GPTBot/PerplexityBot index us — and if training runs ingest us — a coding
agent may refuse a malicious install *without ever visiting the site*. That is the
distribution channel.

> **Measured 2026-08-03 against `d32a766` (168 advisories).** Section 2 was rewritten
> after building the current tree and measuring marginal growth empirically. The
> original acceptance criterion — "no cap bump needed for ≥6 months" — is already
> violated at the time of writing, by roughly 19×. Numbers below are reproducible;
> the method is given so they can be re-run.

## 1. robots.txt: explicit allowlist, not just permissive silence

Enumerate known AI crawlers with explicit `Allow: /` stanzas plus a default
`User-agent: * / Allow: /`: GPTBot, OAI-SearchBot, ChatGPT-User, ClaudeBot,
Claude-User, Claude-SearchBot, anthropic-ai, Google-Extended, PerplexityBot,
Perplexity-User, CCBot, Bytespider, Amazonbot, Applebot-Extended, cohere-ai,
meta-externalagent. Explicit stanzas are robust against operators who treat silence
as ambiguous, and they document intent. Add `Sitemap:` line (verify present).
Add a comment header stating the policy in one sentence ("scrape this; it exists to
be scraped") — humans read robots.txt too.

Keep the list as a module constant in `build.py` so the emitter and the test read one
source:

```python
# Verified against vendor crawler docs on YYYY-MM-DD.
ALLOWED_AI_CRAWLERS: list[str] = ["GPTBot", "OAI-SearchBot", ...]
```

- **Test:** `tests/test_robots.py` checks that every name in `ALLOWED_AI_CRAWLERS` has
  a `User-agent` stanza with `Allow: /` under it, and that **no `Disallow:` line exists
  anywhere**. The second test is the important one: it makes reducing scrapability
  require a deliberate, reviewable test edit rather than a silent build change.
- **Verify at impl time** (names drift): current UA strings per vendor docs. Do not
  copy the list above from memory — vendors split training / retrieval / user-triggered
  fetch into separate tokens and rename them.

## 2. llms.txt family: the cap treadmill is still running

### The trim shipped. It did not fix this.

The 2026-07-15 note in `tests/test_llms.py` correctly diagnosed the problem and
proposed the fix: *"the real fix is broadening the trim to more statuses (e.g.
patched/contained advisories past some age), not another cap bump."*

That fix **shipped** — `build_llms_full_txt` now trims `historical`, plus
`patched`/`contained`/`mitigated` older than 90 days (added 2026-07-14, broadened
07-17, threshold tightened 120→90 days on 07-29).

Current state on `d32a766`, with that trim active:

| File | Size | Cap | % of cap | Headroom |
|---|---|---|---|---|
| `llms.txt` | 79,820 B | 81,920 B | **97.4%** | 2,100 B |
| `llms-ctx.txt` | 146,774 B | 155,648 B | 94.3% | 8,874 B |
| `llms-full.txt` | 1,146,412 B | 1,179,648 B | **97.2%** | 33,236 B |

All three sit at 94–97% of cap *after* the fix. The trim bought time; it did not
change the shape of the curve.

### Marginal cost per advisory, measured

Method — reproducible in a scratch worktree, takes about a minute:

```bash
git worktree add /tmp/growth origin/main && cd /tmp/growth
python3 site/build.py && stat -f%z dist/llms*.txt          # baseline
rm $(ls advisories/2026-07-*.md | tail -10)
python3 site/build.py && stat -f%z dist/llms*.txt          # minus 10
```

| File | Baseline | −10 advisories | Marginal cost each |
|---|---|---|---|
| `llms.txt` | 79,820 | 75,325 | **449 B** |
| `llms-ctx.txt` | 146,774 | 137,766 | **901 B** |
| `llms-full.txt` | 1,146,412 | 1,074,919 | **7,149 B** |

### Time to breach

At the repo's own stated growth rate of ~15 advisories/month:

| File | Headroom | Advisories left | **Days left** |
|---|---|---|---|
| `llms.txt` | 2,100 B | 4.7 | **~9** |
| `llms-ctx.txt` | 8,874 B | 9.9 | ~20 |
| `llms-full.txt` | 33,236 B | 4.6 | **~9** |

The acceptance criterion at the bottom of this spec asked for six months. The measured
answer is nine days for two of the three files — off by a factor of ~19.

*Caveat, stated honestly:* this ignores the relief the age-trim provides as existing
advisories cross 90 days. That relief is real but bounded — it never applies to
`status: active` (32 of 168 advisories today), so there is a growing floor the trim
cannot touch. The empirical record supports the pessimistic reading: nine cap bumps
between 2026-05-30 and 2026-07-15, with the last five only 1–6 days apart, and the
files back at 97% two weeks after the most recent trim tightening.

### Why cap bumps and trimming both fail

Both are constant-factor fixes to a linear-growth problem:

- **Cap bumps** raise a constant. The corpus grows without bound. Each bump buys less
  time than the last — the log above shows the interval collapsing from ~3 weeks to
  ~3 days.
- **Age-trimming** lowers the slope. It does not flatten it. Trimmed advisories still
  contribute their TL;DR, `active` ones contribute in full forever, and the slope stays
  positive.

Nothing with a positive slope stays under a fixed ceiling. The fix has to make the
output size **independent of corpus size**.

### The fix: two-tier, count-bounded output

Bound the number of full entries, not the age of entries. Everything beyond the bound
becomes a one-line pointer.

| File | Tier 1 — full detail | Tier 2 — one line | Expected size |
|---|---|---|---|
| `llms.txt` | 60 most recent, with descriptions | `- [title](url) — severity/date` | ~48 KB |
| `llms-ctx.txt` | 40 most recent: TL;DR + "Am I affected?" | title + URL + severity | ~56 KB |
| `llms-full.txt` | 60 most recent, full body | title + URL + link to `.md` mirror | ~560 KB |

Rules:

- **Tier 1 = (N most recent by `last_updated`) ∪ (all `status: active` or `ongoing`).**
  A live incident is exactly what an agent needs in full, and there are only ~34.
  Sort by `last_updated`, matching `build_atom_feed`, so an old incident with fresh
  analysis ranks correctly.
- **Nothing disappears.** Tier 2 is a pointer. Every advisory keeps its page, its `.md`
  mirror, its `advisories.json` row, its per-section `llms.txt` entry, and its sitemap
  entry. Say so in each file's header so a consuming model knows more exists and how
  to reach it.
- Size now depends on N, which is a constant. The files become O(1) in corpus size.

This **supersedes** the age-based trim rather than stacking on it — keeping both means
two interacting rules and no clear control surface. Remove the age check when Tier
1/2 lands.

### Budget policy, in one place

Replace the archaeology at the top of `tests/test_llms.py` with a policy:

```python
# ─── llms.txt size budget policy ────────────────────────────────────────────
# These caps are a CONTRACT, not a high-water mark. They are not to be raised to
# make a failing build pass. That loop ran nine times between 2026-05-30 and
# 2026-07-15, with the interval collapsing from ~3 weeks to ~3 days. Broadened
# age-trimming (2026-07-14/17/29) lowered the slope but left it positive; by
# 2026-08-03 all three files were back at 94-97% of cap.
#
# The outputs are two-tier and count-bounded: the N most recent advisories plus
# all active/ongoing ones appear in full, everything older is a one-line
# pointer. Size is therefore O(1) in corpus size, not O(n).
#
# If a cap is breached, the correct fixes, in order:
#   1. Lower the Tier-1 count. That is the intended control surface.
#   2. Tighten per-advisory truncation limits.
#   3. Only then, and only with a written rationale here, raise a cap.
#
# HEADROOM_FRACTION makes the test fail while there is still room to think. A
# build at 88% of budget is a warning; the previous regime only reported failure
# at 100%, one advisory too late.

LLMS_TXT_MAX_BYTES  =   80 * 1024
LLMS_CTX_MAX_BYTES  =  152 * 1024
LLMS_FULL_MAX_BYTES = 1152 * 1024
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
        f"{name} is {size:,} B — over the {budget:,} B budget ({size/cap:.0%} of the "
        f"{cap:,} B cap). Lower the Tier-1 count; do not raise the cap. "
        f"See the budget policy at the top of this file."
    )
```

The failure message carries the policy. Someone hitting this at 23:00 mid-sweep should
not have to find this document to know what to do.

Plus a test that stops the bound from being quietly removed:

```python
def test_llms_outputs_are_count_bounded():
    """Tier-1 counts are what bound these files. If this fails, someone removed
    the bound and the caps became load-bearing again."""
    assert LLMS_TXT_TIER1 <= 60
    assert LLMS_CTX_TIER1 <= 40
    assert LLMS_FULL_TIER1 <= 60
```

Note that all three caps stay at their current values. Tier 1/2 should drop the files
to roughly 50–60% of cap; if it does not, the Tier-1 counts are too high.

### Remaining smaller items

- **Apply description truncation to per-section `llms.txt`** (BACKLOG notes it is
  untested/ungated today) and add cap tests for them. They are unbounded today for the
  same reason the main files were.
- **`llms.txt` freshness header:** `Last-updated: <date>` plus a one-line "how often
  this changes" hint so agents can cache sensibly.
- **`llms.txt` usage header:** CC0, freely usable, attribution appreciated — and a note
  that advisories are dated and should be checked for currency. That last clause
  matters: a model surfacing a March advisory as current advice is the most likely way
  this data does harm.

## 3. Machine-discovery completeness

- `<link rel="alternate" type="text/markdown">` exists; also advertise llms.txt via
  a `<link>` on every page and in the Atom feed (some indexers discover it that way).
- `.well-known/` additions: keep security.txt current (check `Expires:`); consider
  `ai.txt` only if a real consumer standard emerges — skip speculative files.
- Sitemap `lastmod` accuracy audit (drives recrawl priority for all bots).
- HTTP headers are off the table on GitHub Pages — document that constraint in
  security.html (already the pattern for CSP) rather than fighting it.

## 4. What we deliberately do NOT do

No crawler traps, no rate-limiting games, no "AI training: no" signals anywhere
(CITATION.cff + permissive license already align). No cloaking: agents and humans get
identical bytes.

## Acceptance criteria

- robots.txt enumerates the current major AI crawlers; `tests/test_robots.py` locks the
  list and asserts no `Disallow:` line exists anywhere.
- All llms.txt variants — **including per-section** — gated by tests with documented
  budgets.
- Tier 1/2 structure implemented; age-based trim removed in the same change.
- **All three files land under 85% of cap** (`HEADROOM_FRACTION`), and re-running the
  marginal-cost measurement above shows Tier-2 advisories costing < 150 B each.
- `test_llms_outputs_are_count_bounded` present, so the bound cannot be silently
  dropped.
- Every HTML page advertises both its .md mirror and the site llms.txt.

~~no cap bump needed for ≥6 months at current advisory growth rate (~15/month)~~ —
replaced. That criterion was unmeasurable as written and was already violated when
this spec was merged; the budget-fraction test above is the checkable version.

**Effort.** Small for §1 and §3. §2 is a real emitter change — half a day — but it is
the one that stops the recurring deploy breakage.

**Priority.** Ship §2 first. `llms.txt` and `llms-full.txt` have roughly nine days of
headroom at current cadence.
