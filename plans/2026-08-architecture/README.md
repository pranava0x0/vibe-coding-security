# Architecture review — August 2026

> Six specs from a full-repo architecture review. Written 2026-08-03 against
> commit `0871393`. Each spec is independently shippable; the order below is the
> recommended sequence, not a hard dependency chain.

## Why now

The repo has grown from a handful of markdown files into a small publishing
system: 107 advisories, 137 built pages, a 1,178-line build script, 302 tests,
and a machine-readable API that other tools consume. Three strains are showing.

**The data is trapped in prose.** Indicators of compromise — package versions,
C2 domains, file hashes, attacker-controlled npm accounts — live only in advisory
body text. Anything that wants to *use* this data (a lockfile checker, an OSV
export, a SIEM import) has to scrape prose, and prose is noisy: citation domains
sit right next to real C2 domains with nothing distinguishing them. Spec 02
fixes this.

**The vocabulary is uncontrolled.** `tags:` is a free-text array and has drifted
into near-synonyms that fragment the corpus — `ai-agent` (4 uses) vs `ai-agents`
(7) vs `ai-agent-framework` (8); `prompt-injection` (28) vs
`indirect-prompt-injection` (5). No consumer can filter reliably on a vocabulary
where the same concept has three spellings. Spec 01 adds one controlled axis
without disturbing the free-text tags.

**The size caps are about to fail.** As measured on 2026-08-03:

| File | Size | Cap | Headroom |
|---|---|---|---|
| `llms-ctx.txt` | 130,989 B | 131,072 B | **83 B** |
| `llms.txt` | 64,719 B | 65,536 B | 817 B |
| `llms-full.txt` | 927,321 B | 983,040 B | 55.7 KB |

`llms-ctx.txt` has 83 bytes of headroom. A single new advisory breaks the deploy.
This has happened four times (see the comment block at the top of
`tests/test_llms.py`), and each time the fix was to raise the cap. Spec 05 ends
that loop by making the *content* bounded instead of the ceiling adjustable.

## The specs

| # | Spec | Theme | Effort | Blocks |
|---|---|---|---|---|
| 01 | [Threat taxonomy + anti-patterns](01-threat-taxonomy-and-anti-patterns.md) | Content & schema | Medium | 02, 04 |
| 02 | [Data flow: IOC frontmatter as source of truth](02-data-flow-ioc-frontmatter.md) | Data architecture | Medium-high | 04 |
| 03 | [Software architecture: emitter registry](03-build-emitter-registry.md) | Refactor | Medium | — |
| 04 | [Search + SEO](04-search-and-seo.md) | Frontend | Medium | — |
| 05 | [Crawler policy + llms.txt size budget](05-crawler-policy-and-llms-budget.md) | Policy & build | Low-medium | — |
| 06 | [Plain language (ASD-STE100)](06-plain-language.md) | Content quality | Medium | — |

### Recommended order

**Spec 05 first if a sweep is imminent.** The 83-byte headroom on
`llms-ctx.txt` means the next content addition fails CI. Spec 05's trimming rule
buys back roughly 40% of that file immediately. Everything else can wait; this
cannot.

**Then Spec 01.** It is pure content and schema — no build-system changes — and
it defines the `attack_class` vocabulary that Spec 02's IOC records and Spec 04's
filter chips both key off. Doing it first means the other two don't have to
invent a taxonomy in passing and then reconcile it later.

**Then 02 → 04.** Spec 02 makes IOCs structured; Spec 04 spends that structure on
per-package and per-CVE landing pages. Running 04 before 02 means building those
pages from prose scraping and then rebuilding them.

**Spec 03 and 06 are independent.** Spec 03 (the `build.py` split) touches no
content and is gated on byte-identical output, so it can land at any point
without coordination. Spec 06 is a content-quality ratchet that only ever
tightens; it can start whenever.

## Conventions these specs share

**Back-compatibility is non-negotiable.** `advisories.json`, `api/v1/`, the Atom
feed, and `advisory-schema.json` are consumed by tools outside this repo. Every
spec adds fields; none removes or renames one. `additionalProperties: true` stays
in the schema.

**New frontmatter is optional at first.** Adding a required key to
`advisory-schema.json` means back-filling 107 files before anything builds. The
pattern in every spec here is: add the field as optional, back-fill new advisories
as they're written, then flip to required in a later change once coverage is
complete. Specs state their own promotion threshold.

**Determinism is a hard requirement.** `build.py` deliberately avoids
`datetime.now()` in the Atom feed so consecutive builds are byte-identical (see
the comment in `build_atom_feed`). Any new emitter must hold that line — sort
every collection explicitly, never iterate a set, never embed a timestamp that
isn't derived from source content.

**Tests are the specification.** Each spec lists the tests that must exist before
it is considered done. A spec that adds a policy without a test that fails when
the policy is violated has not shipped its policy.

## Verification

Every spec verifies the same way:

```bash
python3 site/build.py && python3 site/validate.py && python3 -m pytest -q
```

Baseline at time of writing: build emits 137 pages, `validate.py` passes all 9
check groups, 302 tests pass.
