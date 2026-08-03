# Spec 01 — Threat taxonomy + architectural anti-patterns

> **Theme:** content & schema · **Effort:** medium · **Blocks:** Spec 02, Spec 04
> **Status:** proposed

## Problem

Two gaps, one root cause: the repo classifies incidents by *what happened* but
never by *what class of system failure allowed it*.

### 1. The tag vocabulary has drifted

`tags:` is a free-text array with no controlled vocabulary. Across 107 advisories
it has fragmented into near-synonyms:

| Concept | Spellings in use | Counts |
|---|---|---|
| AI agent systems | `ai-agent`, `ai-agents`, `ai-agent-framework` | 4 / 7 / 8 |
| Prompt injection | `prompt-injection`, `indirect-prompt-injection` | 28 / 5 |
| Credential exposure | `credential-theft`, `token-theft` | 50 / 3 |

A consumer filtering on `ai-agent` misses 15 of 19 relevant advisories. This is
not a tagging-discipline problem that better review catches — it is the expected
outcome of an uncontrolled vocabulary, and it gets worse monotonically.

The fix is *not* to police `tags:`. Free-text tags are genuinely useful for the
long tail (`miasma-lineage`, `teampcp`, `cisa-kev` are all doing real work). The
fix is to add one controlled axis alongside them.

### 2. Prevention covers tactics, not architecture

`prevention/` has eight guides, all tactical: pin this, disable that, rotate the
other. Every one is good advice. None of them describe the *structural* choices
that make an incident possible in the first place.

The 2026 incident record makes this gap expensive. When agents autonomously
discover and chain vulnerabilities — as in the July 2026 Hugging Face intrusion,
where evaluation models under test moved laterally out of their harness — the
failure is not "someone forgot to pin a dependency." The failure is that the
harness was on a flat network with ambient credentials and a shared execution
surface. No amount of `npm config set ignore-scripts true` addresses that.

Similarly, `prevention/` has nothing on model and dataset supply chain. The repo
covers npm and PyPI thoroughly, but a `.safetensors` file pulled from a model hub
is also untrusted code from the internet, and the advisory corpus now includes
incidents where that was the vector.

## Proposal

Three deliverables:

1. A controlled `attack_class` frontmatter enum, additive to `tags:`.
2. `prevention/architectural-anti-patterns.md` — a catalog of five structural
   patterns that convert a single compromise into a breach.
3. `prevention/model-supply-chain.md` — the model/dataset counterpart to
   `npm-hardening.md`.

---

## Deliverable 1 — `attack_class` enum

### Design

One value per advisory. Not a list — the point is a single, mutually exclusive
axis you can group by. If an incident genuinely spans two classes, pick the one
that describes the *initial* failure and put the second in `tags:`.

The enum is deliberately small. Seven values, chosen so that every one of the 107
existing advisories maps cleanly to exactly one, and so that a reader can hold the
whole list in their head:

| Value | Definition | Representative advisories |
|---|---|---|
| `package-supply-chain` | Malicious or compromised package in a language registry (npm, PyPI, crates, VS Code marketplace). | `2025-09-shai-hulud-original`, `2025-09-qix-compromise` |
| `model-supply-chain` | Malicious or compromised model weights, datasets, or model-hub artifacts. | New advisories from the 2026 model-hub incidents |
| `dataset-poisoning` | Training or fine-tuning data manipulated to alter model behavior. | — (none yet; reserved, see "empty classes" below) |
| `sandbox-escape` | Code escapes its intended execution boundary — container, VM, extension host, eval harness. | `2025-10-glassworm-vscode-worm` |
| `agent-runtime` | The agent's own runtime is subverted: tool-call manipulation, approval-dialog bypass, MCP server compromise, indirect prompt injection reaching a tool. | `2025-09-postmark-mcp-backdoor`, `2025-09-litl-ai-approval-dialog-bypass` |
| `credential-exposure` | Secrets leaked, stolen, or over-scoped, where credential access is the *initial* failure rather than a downstream consequence. | `2025-08-salesloft-drift-oauth-breach` |
| `application-vulnerability` | A conventional CVE in a tool the audience uses — RCE, path traversal, SSRF, deserialization. | `2025-10-windsurf-cve-2025-62353-path-traversal` |

**On empty classes.** `dataset-poisoning` has no current advisories. Include it
anyway. An enum that only describes the past forces the *next* incident into a
wrong bucket, and the cost of an unused value is one line. But cap this: do not
add speculative values beyond ones the threat model clearly anticipates.

**On `credential-exposure` vs everything else.** Half the corpus involves stolen
credentials *somewhere* — 50 advisories carry the `credential-theft` tag. The
enum value is narrower: it applies only when credential handling is the initial
failure. Shai-Hulud steals credentials, but its `attack_class` is
`package-supply-chain` because the credential theft is what the malicious package
*did*, not how it got in. Write this rule into the schema description; it is the
distinction reviewers will get wrong most often.

### Schema change

In `build_advisory_schema()` in [site/build.py:1043](../../site/build.py), add to
`properties`:

```python
"attack_class": {
    "enum": [
        "package-supply-chain",
        "model-supply-chain",
        "dataset-poisoning",
        "sandbox-escape",
        "agent-runtime",
        "credential-exposure",
        "application-vulnerability",
    ],
    "description": (
        "Single controlled classification of the initial system failure. "
        "Choose by what allowed the compromise to begin, not by what the "
        "attacker did afterward — a package that steals credentials is "
        "package-supply-chain, not credential-exposure."
    ),
},
```

Leave it out of `required`. See "Rollout" below.

### Data flow

`attack_class` must reach every consumer that already sees `tags`:

- `build_advisories_json()` ([site/build.py:1021](../../site/build.py)) — add the key.
- `build_search_index()` ([site/build.py:1005](../../site/build.py)) — add the key;
  Spec 04's filter chips read it from here.
- `build_jsonld()` ([site/build.py:474](../../site/build.py)) — fold into the
  `keywords` string for advisory pages.
- The meta bar (`build_meta_bar()`, [site/build.py:366](../../site/build.py)) —
  render as a labeled chip so it's visible to human readers, not just machines.

### Tests

In `tests/test_frontmatter.py`:

```python
def test_attack_class_is_valid_enum(parsed_advisories, advisory_schema):
    """attack_class, when present, must be one of the controlled values."""
    allowed = set(advisory_schema["properties"]["attack_class"]["enum"])
    for path, fm, _ in parsed_advisories:
        if "attack_class" not in fm:
            continue
        assert fm["attack_class"] in allowed, (
            f"{path.name}: attack_class={fm['attack_class']!r} not in {sorted(allowed)}"
        )


def test_attack_class_is_scalar(parsed_advisories):
    """One class per advisory — a list means the author dodged the choice."""
    for path, fm, _ in parsed_advisories:
        if "attack_class" in fm:
            assert isinstance(fm["attack_class"], str), (
                f"{path.name}: attack_class must be a single string, not {type(fm['attack_class']).__name__}"
            )
```

Read the enum from the generated schema rather than duplicating the list — one
source of truth, and the test fails if the schema and the docs drift apart.

Add a coverage-ratchet test that prevents backsliding during rollout:

```python
def test_attack_class_coverage_does_not_regress(parsed_advisories):
    """Ratchet: coverage may rise, never fall. Raise MIN_COVERED as you back-fill."""
    MIN_COVERED = 0  # ← raise this as advisories are back-filled; target 107
    covered = sum(1 for _, fm, _ in parsed_advisories if "attack_class" in fm)
    assert covered >= MIN_COVERED, (
        f"attack_class coverage fell to {covered}, below ratchet {MIN_COVERED}"
    )
```

### Rollout

1. Ship the schema, the tests, and the data-flow changes with `attack_class`
   optional and `MIN_COVERED = 0`.
2. Back-fill in batches by class — all `package-supply-chain` advisories in one
   pass, etc. Grouping by class is much faster than going file-by-file, because
   you make one classification decision and apply it to a known set. Raise
   `MIN_COVERED` after each batch.
3. When coverage hits 107, move `attack_class` into the schema's `required` array
   and into `REQUIRED_KEYS` in `tests/conftest.py`. Delete the ratchet test — the
   required-keys test subsumes it.

Do not skip step 3. An optional field that never becomes required is a field
half the corpus will silently lack.

---

## Deliverable 2 — `prevention/architectural-anti-patterns.md`

A catalog of structural patterns. Each entry follows a fixed shape so the page
is skimmable:

- **The pattern** — one sentence, phrased as the thing people actually do.
- **Why it's tempting** — non-judgmental; every one of these exists because it
  solved a real problem.
- **What it costs you** — the specific escalation it enables, tied to advisories
  in this repo where possible.
- **What to do instead** — concrete, with commands or config where they exist.

### The five patterns

**1. Flat-network agents.** An agent sandbox that can reach the rest of your
network. The container boundary stops filesystem access but the agent still has a
route to your metadata endpoint, your internal registry, and every other host on
the subnet. Cost: converts "the agent ran something bad" into lateral movement.
Instead: default-deny egress, explicit allowlist of registry and API hosts, block
link-local metadata addresses (`169.254.169.254`) outright.

**2. Ambient credentials.** Credentials available to any process by virtue of
running on the machine — `~/.aws/credentials`, a logged-in `gh` CLI, a populated
`~/.npmrc`, an unlocked keychain. Cost: every advisory in this repo that mentions
credential theft relied on this; the malware didn't phish anyone, it read a file.
Instead: short-lived credentials injected per-command, `op run` / `aws-vault` /
OIDC, and treat any long-lived token on disk as already leaked.

**3. Shared execution surfaces.** One environment where evaluation, development,
and production tooling coexist — the classic being an eval harness that runs on
the same host as the CI runner that holds publish rights. Cost: this is the
structural precondition for the 2026 model-evaluation incidents; the model under
test only had to escape into an environment that was already privileged.
Instead: one-purpose environments, ephemeral by default, with the blast radius of
each sized to what it actually needs.

**4. Writable agent configuration.** Agent config that the agent itself, or any
code it runs, can modify — `.mcp.json`, `.cursorrules`, `CLAUDE.md`, allowlist
files, hook definitions. Cost: turns a one-time code execution into persistence,
because the payload rewrites the rules that were supposed to contain it. This is
the mechanism behind several of the IDE-extension advisories here. Instead: treat
agent config as code — committed, reviewed, and read-only at runtime; verify it
hasn't changed as a pre-flight check.

**5. Publish rights from a dev box.** The laptop that runs `npm install` on
LLM-suggested packages also holds the token that can publish to the registry.
Cost: this is the exact escalation path of every self-replicating worm in the
corpus — Shai-Hulud's propagation step is precisely "read the maintainer's npm
token, publish to everything they own." Instead: publishing happens only from CI,
via OIDC/trusted publishing with no long-lived token anywhere; the dev box holds
a read-only token or none.

### Integration

- Add a row to the table in `prevention/README.md`.
- Add to "The 6 highest-leverage habits" — likely replacing or extending item 2,
  since the sandboxing habit and the flat-network anti-pattern are two halves of
  one idea. Renumber if the list grows past six, or keep six and pick the
  strongest; a list called "the 6" with seven items is worse than a hard choice.
- Cross-link from `prevention/supply-chain-attack-surface.md`, which is the
  designated entry point and should route architectural questions here.
- Link from advisories whose `attack_class` is `sandbox-escape` or `agent-runtime`
  in their `## Prevention` section.

---

## Deliverable 3 — `prevention/model-supply-chain.md`

The model/dataset counterpart to `npm-hardening.md`. Same house shape as the other
prevention docs: a short "why this is different" framing, then concrete checks.

Cover:

- **Format risk.** Why `.safetensors` is the safe default, and why the legacy
  serialization formats (`.bin`, `.pt`, `.ckpt`) execute arbitrary code at load
  time by design. This is the single highest-value fact on the page — lead with it.
- **Provenance.** Verifying which account published a model, whether the repo is
  the canonical one for that model family, and how to spot the model-hub
  equivalent of typosquatting (an org name one character off from the real lab).
- **Pinning.** Model revisions are mutable by default. Pin to a commit SHA, not a
  branch or tag — the direct analogue of the repo's existing "pin Actions to a
  SHA" advice, and worth drawing that parallel explicitly.
- **Dataset provenance.** What you can and cannot verify about a dataset, and why
  "it's on a well-known hub" is not provenance.
- **Loading untrusted models.** If you must load a legacy-format model, do it in
  the same kind of isolation you'd use for untrusted code — which is the bridge
  to Deliverable 2.

**Verification caution.** This doc will contain the most post-cutoff-sensitive
claims in the repo — hub security features, scanner coverage, and format defaults
all move fast. Every tool claim needs a check against current vendor docs at
authoring time, and a dated source line. Follow the existing convention: cite
inline, and put the date in the `## Sources` entry.

### Integration

- Row in `prevention/README.md`.
- Cross-link from `prevention/package-vetting-checklist.md` — a reader vetting a
  package and a reader vetting a model are asking the same question.
- Add `model-supply-chain` and `dataset-poisoning` to the ecosystems vocabulary
  where relevant.

---

## Done when

- [ ] `attack_class` in `advisory-schema.json` with the seven-value enum.
- [ ] Enum value flows into `advisories.json`, `search.json`, JSON-LD keywords,
      and the rendered meta bar.
- [ ] Three tests in `tests/test_frontmatter.py`: valid-enum, scalar, coverage
      ratchet.
- [ ] `prevention/architectural-anti-patterns.md` with all five patterns.
- [ ] `prevention/model-supply-chain.md` with sourced, date-checked claims.
- [ ] Both docs linked from `prevention/README.md` and from the attack-surface map.
- [ ] `build.py` → `validate.py` → `pytest` all green.

## Explicitly out of scope

- Back-filling all 107 advisories. That is follow-up work tracked by the ratchet.
- Changing or pruning `tags:`. The free-text vocabulary stays as-is; this spec
  adds an axis rather than replacing one.
- Making `attack_class` required. That is step 3 of rollout, after back-fill.
