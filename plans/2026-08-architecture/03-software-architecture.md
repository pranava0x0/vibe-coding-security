# Spec 03 — Software architecture: split the build monolith, keep it boring

**Goal.** Restructure `site/build.py` (1,245 lines, single file) into small modules with
an emitter registry, so Spec 02's new outputs and Spec 04's search/SEO work land as
additive plugins instead of edits to one god-file.

**Motivated by.** The llms.txt cap-bump saga (four cap bumps in five weeks, fixed only
when trimming logic finally landed) shows the cost of tangled emit logic: every change
risks every output. The Anthropic/Irregular lesson applies to us too — misconfiguration
in one flat thing is the failure mode; small components with narrow contracts are the fix.

## Target layout

```
site/
  build.py            # thin orchestrator: load → validate → run emitters → integrity
  validate.py         # post-emit checks (unchanged role)
  lib/
    corpus.py         # frontmatter parsing, schema validation, typed records
    markdown.py       # md→HTML rendering, TOC, heading ids
    templates.py      # page chrome, JSON-LD, OG/Twitter meta
    emitters/
      html.py         # pages + .md mirrors
      llms.py         # llms.txt family incl. trimming/caps logic (self-contained)
      json_api.py     # advisories.json, api/v1/*, search.json
      iocs.py         # (new, Spec 02)
      osv.py          # (new, Spec 02)
      feeds.py        # atom, sitemap, robots
      integrity.py    # (new, Spec 02 — must run last)
```

Emitter contract: `emit(corpus, outdir) -> list[Path]`. `build.py` runs them in a
declared order, collects produced paths, and hands the list to `integrity.py` and
`validate.py` (which can then assert "every emitter produced its declared outputs"
instead of a hardcoded file list).

## Rules

- **No behavior change in the first PR.** Pure mechanical move + imports; the existing
  determinism test is the safety net (two builds → identical `dist/`). Byte-identical
  output before/after the refactor is the merge gate.
- **Tests move with code.** Unit-test `corpus.py` and `llms.py` trimming directly
  (today they're only tested through full builds — slow and coarse).
- **No new dependencies.** Static + boring; stdlib + the existing requirements only.
- **CI stays the same three commands** (`build.py`, `validate.py`, `pytest`) so the
  sweep skill and deploy workflow need zero changes.

## Follow-ups unlocked (not in scope here)

- Incremental builds (hash frontmatter → skip unchanged pages) if build time ever hurts.
- A `--only <emitter>` dev flag for fast iteration on one output.
- Per-emitter output caps/budgets declared next to the emitter (formalizes the
  llms.txt cap policy instead of constants in a test file).

## Acceptance criteria

- `git diff --stat` on `dist/` between pre- and post-refactor builds is empty.
- `build.py` under ~150 lines; no module over ~300.
- New-emitter HOWTO paragraph in CONTRIBUTING.md (add file, register, declare outputs).

**Effort.** Medium — one focused day plus review; do it before Spec 02 items 3–4.
