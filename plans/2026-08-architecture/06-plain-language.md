# Spec 06 — Plain language: ASD-STE100 house style + CI lint ratchet

> **Theme:** content quality · **Effort:** medium · **Blocks:** nothing
> **Status:** proposed

## Problem

The repo's stated audience is people who build with AI coding tools and are not
security specialists. README.md is explicit: *"If an LLM has ever suggested a
package and you installed it without reading the source, this repo is for you."*

The advisory template sets a hard bar — `## TL;DR` is specified as *"Two
sentences. A vibe coder should grok it in 5 seconds"* — and `## Am I affected?`
promises a yes/no answer in under 60 seconds.

Nothing enforces either. Across 107 advisories written over many sweeps, mostly
under time pressure, the prose has drifted toward the register of the sources it
summarises. Vendor security blogs are written for security teams; when an
advisory paraphrases one closely, it inherits that vocabulary. The reader who
needed 5 seconds gets a paragraph about lateral movement via OAuth pivot.

This matters more here than in most docs. These pages are read by someone who
has just discovered they might be compromised — a bad time to parse a
subordinate clause.

## Why ASD-STE100

[ASD-STE100 Simplified Technical English](https://asd-ste100.org/) is a
controlled language written for aircraft maintenance manuals: procedures that
must be unambiguous to a non-native reader working under time pressure with
consequences for misreading. That is the same problem this repo has.

It is a real standard with a real rule set, not a vibe. The parts worth adopting:

- One meaning per word. Approved words have exactly one approved sense.
- Short sentences — 20 words for procedures, 25 for description.
- Active voice in instructions. Never "the token should be rotated."
- One instruction per sentence.
- No noun stacks longer than three words.

The parts to skip: the full ~900-word approved dictionary, and STE's ban on
technical vocabulary. This repo *needs* "postinstall", "lockfile", "OAuth". The
answer is a glossary, not avoidance.

**This is a house style informed by ASD-STE100, not a certification.** Saying so
in the doc prevents a reviewer from ever arguing a rule from the standard that
the repo has deliberately not adopted.

## Proposal

Three deliverables: a style guide, a glossary, and a lint ratchet.

---

## Deliverable 1 — `CONTRIBUTING.md` house style section

Add to `CONTRIBUTING.md`, next to the advisory template so it is read at the
moment of writing. Keep it short enough to actually be read — one screen.

### The rules

**1. One instruction per sentence.**
> ✗ Rotate your npm token and check for unauthorized publishes, then enable 2FA.
> ✓ Rotate your npm token. Check for unauthorized publishes. Enable 2FA.

**2. Active voice for anything the reader must do.**
> ✗ The affected packages should be removed.
> ✓ Remove the affected packages.

**3. Sentences under 25 words. Under 20 in `## Am I affected?`.**

**4. Lead with the answer.**
> ✗ Following the compromise of the maintainer account, versions 5.6.1 and 5.6.2 were published containing…
> ✓ If you installed chalk 5.6.1 or 5.6.2, you are affected.

**5. One term, one meaning.** Pick one and use it everywhere: "malicious
package", not "bad package" / "trojanized package" / "poisoned dependency" as
free variants.

**6. Expand any acronym on first use per page.** Pages are read out of order and
via `llms-full.txt`; per-page is the right scope, not per-repo.

**7. No noun stacks over three words.**
> ✗ npm registry credential exfiltration payload
> ✓ a payload that steals npm registry credentials

**8. Say what to do, not what it is.** A `## TL;DR` that describes an attack
without saying whether to act has failed its job.

---

## Deliverable 2 — Glossary

`prevention/glossary.md` — every term the audience might not know, one plain
sentence each, linked from anywhere it is first used.

Seed from terms already load-bearing in the corpus: postinstall / lifecycle
script, lockfile, transitive dependency, typosquatting, slopsquatting,
dependency confusion, provenance, attestation, C2, exfiltration, lateral
movement, OAuth token vs. PAT, MCP server, prompt injection (direct vs.
indirect), supply chain, IOC, CVE / GHSA / OSV, blast radius.

Entry shape — definition first, then why the reader cares:

```markdown
### Postinstall script
Code that runs automatically when you install a package, before you use it.
`npm install` executes it with your user's full permissions. This is why
`ignore-scripts` matters: a malicious package does not need you to import it.
```

Two rules that keep it useful: **no term is defined using another undefined
term**, and **every entry ends with a consequence**. A definition that doesn't
say why it matters won't be read.

Wire it in: row in `prevention/README.md`; a build-time check (or review habit)
that glossary terms are linked on first use in advisories.

---

## Deliverable 3 — CI lint ratchet

### Design constraints

This is where a plain-language initiative usually dies. Two failure modes:

- **Retroactive enforcement.** Turn on a strict linter over 107 existing
  advisories, get 800 warnings, turn it off.
- **Prose linters are opinionated and often wrong.** They flag "simply" and
  "just" — fine — but also flag passive voice in places where it is correct
  ("the package was published by an attacker" has no better active form).

So: **error only on changed files, warn everywhere else.** A contributor is
responsible for the prose they wrote, not for prose written eight months ago.
This is the same ratchet pattern as Spec 01's coverage counter, and it converges
without a big-bang cleanup.

### Scope tiers

| Scope | Level | Rationale |
|---|---|---|
| `## TL;DR` in changed files | **error** | The 5-second promise. Non-negotiable. |
| `## Am I affected?` in changed files | **error** | The 60-second promise. |
| Rest of changed files | warn | Body prose gets latitude for technical precision. |
| Unchanged files | report only | Tracked, never blocking. |

### Implementation

`tools/lint-plain-language.py`, in the style of the existing
`tools/check-external-links.py`. Pure standard library — no new dependency, in
keeping with the repo's posture.

Checks, in rough order of value:

1. Sentence length over the section threshold.
2. Passive voice in imperative sections — heuristic (`be`-verb + past
   participle), reported as a warning, never an error outside TL;DR.
3. Unexpanded acronym on first use, against a known-acronym list.
4. Noun stacks over three words.
5. Banned vague intensifiers: "simply", "just", "obviously", "of course" — these
   tell a frightened reader their problem is easy.
6. Undefined glossary terms not linked on first use.

```bash
# Default: changed vs. main.
python3 tools/lint-plain-language.py

# Whole corpus, non-blocking, for tracking.
python3 tools/lint-plain-language.py --all --report
```

Determine changed files with `git diff --name-only origin/main...HEAD`, filtered
to `advisories/`, `playbooks/`, `prevention/`. On `main`, or when the diff is
empty, fall back to `--all --report` so the job still produces a number.

### Wiring

Add a step to `.github/workflows/ci.yml`. It must **not** block the deploy
workflow — this is a content-quality gate on PRs, and a style warning should
never stop a security advisory from publishing. That tradeoff is deliberate and
should be noted in the workflow file.

### The ratchet

```python
# tests/test_plain_language.py
MAX_TOTAL_WARNINGS = 812   # ← measure on first run, then only ever lower

def test_plain_language_warnings_do_not_regress():
    """Corpus-wide count may fall, never rise. Lower the number when you
    improve a batch of files. This is the only enforcement on old content."""
    count = run_linter(all_files=True).warning_count
    assert count <= MAX_TOTAL_WARNINGS, (
        f"Plain-language warnings rose to {count} (ceiling {MAX_TOTAL_WARNINGS}). "
        f"New content should be clean; see CONTRIBUTING.md house style."
    )
```

Measure the real number on first run and set it there. Do not guess it, and do
not set it aspirationally low — a ratchet that fails on day one gets deleted.

### Rollout

1. Ship the linter with everything at `--report`. Record the baseline.
2. Ship the style guide + glossary. Nothing blocks yet.
3. Turn on **error** for TL;DR in changed files only.
4. Extend error to `## Am I affected?` in changed files.
5. Lower `MAX_TOTAL_WARNINGS` opportunistically — when a sweep touches an
   advisory, clean it and drop the ceiling.

Do not compress these into one PR. The point of the ratchet is that it never
requires a large cleanup.

---

## Interaction with other specs

The `## TL;DR` and `## Am I affected?` sections are exactly what Spec 05's
`llms-ctx.txt` extracts (`_extract_section`,
[site/build.py:904](../../site/build.py)), truncated to 500 and 450 characters.
Tightening those two sections improves the compact LLM output and reduces its
size at the same time — so this spec makes Spec 05's budget easier to hold.

Worth stating in the style guide: **a TL;DR over 500 characters is silently
truncated in `llms-ctx.txt`.** That is a concrete reason to be brief, and more
persuasive than a style rule.

---

## Done when

- [ ] House style section in `CONTRIBUTING.md`, one screen, with examples.
- [ ] `prevention/glossary.md` covering the seed terms, linked from the index.
- [ ] `tools/lint-plain-language.py`, standard library only, `--all` / `--report`.
- [ ] Baseline warning count measured and recorded.
- [ ] CI step on PRs; error on TL;DR + "Am I affected?" in changed files only.
- [ ] Linter does not gate the deploy workflow.
- [ ] `tests/test_plain_language.py` ratchet at the measured baseline.
- [ ] `build.py` → `validate.py` → `pytest` all green.

## Explicitly out of scope

- Rewriting existing advisories in bulk. The ratchet handles this incrementally.
- The full ASD-STE100 approved dictionary. House style only.
- A readability score (Flesch-Kincaid etc.) as a gate. They reward short words
  over clear structure and would penalise correct technical vocabulary.
- Translation (BACKLOG, Medium). Plain source English makes it cheaper later,
  but it is separate work.
- Applying the linter to `README.md` / `BACKLOG.md` / `ISSUES.md`. Reader-facing
  content only.
