# Spec 06 — Plain technical English (ASD-STE100-inspired) with CI enforcement

**Goal.** Every advisory is readable under stress, by non-native English speakers, and
by small LLMs — using a house style inspired by ASD-STE100 (Simplified Technical
English, the aerospace/defense controlled-language standard).

**Motivated by.** Our readers are often mid-incident (stressed, skimming), global
(BACKLOG already flags Spanish/Mandarin/Hindi audiences), or machines (a 7B model
triaging an install decision parses simple sentences far more reliably). STE was
designed for exactly this: maintenance instructions that must not be misread. We adopt
its principles, not the full certified standard (the official STE dictionary is
licensed; we write our own small word list).

## 1. House style rules (`CONTRIBUTING.md` + new `docs/style-guide.md`)

Adapted STE core rules:

- One instruction per sentence. Procedural sentences ≤ 20 words; descriptive ≤ 25.
- Active voice, imperative mood for actions ("Rotate the token", not "the token
  should be rotated").
- One term, one meaning, everywhere: it's always *advisory* (not bulletin/report),
  *attacker* (not threat actor/adversary), *malicious package* (not trojanized
  artifact), *credentials* (not secrets material). Build the approved-terms table
  from the corpus's actual variance (quick grep pass).
- No noun stacks over 3 words ("npm supply chain compromise campaign wave" → ban).
- Verbs over nominalizations ("exfiltrates" not "performs exfiltration of").
- Paragraphs ≤ 6 sentences; every procedure is a numbered list.
- Jargon policy: first use of a term of art links to a one-line definition
  (glossary page, see §3).

Sections with hard rules vs. advisory prose: **TL;DR and "Am I affected?" are
strict-STE zones** (they're what llms-ctx.txt ships and what people read mid-incident);
background/timeline sections get the relaxed rules.

## 2. Enforcement (ratchet, not flag-day)

- **Vale** (prose linter, single static binary — CI-friendly, no runtime deps) with a
  custom style package encoding: sentence length, passive voice, banned/preferred
  terms, noun-stack heuristic. Alternative if Vale is unwanted: ~150-line Python
  checker in `tools/` reusing the frontmatter parser; decide at impl time.
- Ratchet: warn-only on existing files, **error on files new or modified in the PR**
  (same pattern as the external-link checker plan). No mass rewrite; the corpus
  converges as sweeps touch files.
- Readability gate: Flesch-Kincaid grade ≤ 9 on TL;DR sections (computed in the
  checker; it's a 20-line formula, no dependency needed).
- Wire into `ci.yml` beside the existing gate; sweep skill (SKILL.md) gains a step:
  "run the style checker on new advisories before committing."

## 3. Glossary page

`/glossary.html` (+ glossary.md, + inclusion in llms-full.txt): one-line plain-English
definitions of every term of art we use — IOC, C2, typosquat, slopsquat, purl, MCP,
postinstall, exfiltration, lethal trifecta, egress, provenance, attestation.
Advisory templates link terms on first use. This is also an SEO asset (definitional
queries) and helps small-model comprehension (definitions travel with the corpus).

## Acceptance criteria

- Style guide published; CONTRIBUTING links it; advisory template updated.
- Checker runs in CI, error-level on changed files, and the sweep skill invokes it.
- 3 sample advisories rewritten to strict style as exemplars (pick the 3 most-linked).
- Glossary live and linked from at least the TL;DR template.

**Effort.** Small–medium. Guide + glossary 1 day; checker 1 day; ratchet is free.
