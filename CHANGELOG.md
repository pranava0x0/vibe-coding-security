# Changelog

> User-facing changes to the repo, the site, and the advisory corpus.
> Per-sweep details live in [`.claude/skills/vibe-security-update/runs.log.md`](.claude/skills/vibe-security-update/runs.log.md).

The format is loosely based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Newest entries first.

---

## [Unreleased]

### Added
- **LLM-friendly outputs (Mintlify / Anthropic pattern):**
  - **Per-page `.md` mirrors** alongside every `.html` page — replace `.html` with `.md` in any URL to get the raw markdown source without re-parsing HTML.
  - **Per-section `llms.txt`** at `advisories/llms.txt`, `playbooks/llms.txt`, `prevention/llms.txt`, `sources/llms.txt`, `tools/llms.txt`.
  - **Compact `llms-ctx.txt`** — alerts + per-advisory TL;DRs + "am I affected?" only (compact per-advisory digest, ~70KB at ~50 advisories) for mid-context-window ingestion.
- **`feed.xml`** — Atom feed of advisories for RSS readers.
- **`advisory-schema.json`** — JSON Schema (draft 2020-12) for advisory frontmatter.
- **Versioned API** at `api/v1/advisories.json` and `api/v1/index.json`.
- **JSON-LD ItemList** schema on the advisories index page.
- **Sitemap hints** — `changefreq` + `priority` per URL.
- **Page actions** — "View raw markdown" + "Edit on GitHub" on every page.
- **`<link rel="alternate" type="text/markdown">`** on every page so tools can discover the markdown variant.
- **CITATION.cff** — academic citation metadata.
- **SECURITY.md** (renamed from lowercase `security.md` for the standard GitHub convention).
- **CHANGELOG.md** — this file.
- **Comprehensive pytest test suite** under `tests/` — frontmatter schema, link integrity, no-secrets, determinism, accessibility, llms.txt format, advisory ID uniqueness, etc. Wired into the deploy workflow.

### Changed
- **Site title** displayed as "Vibe Coding · Security Issue Tracking" (was "vibe-coding-security"). Repo URL slug unchanged.
- **Footer** now exposes the full set of LLM/feed format links.
- **`robots.txt`** explicit comment: AI/LLM training allowed.

---

## 2026-05-17

### Added
- 3 new advisories from the 2026-05-17 sweep:
  - **Windsurf zero-click MCP RCE** (CVE-2026-30615)
  - **"Comment and Control" PR prompt injection** (CVSS 9.4) — Claude Code Security Review, Gemini CLI Action, Copilot Agent
  - **Systemic MCP stdio RCE class** — OX Security, ~200k servers exposed
- Authoritative-source citations added to every prevention doc and playbook (OWASP, Anthropic, npm Docs, AWS Customer Playbook Framework, GitHub Docs, MCP spec, OpenSSF, CISA, Karpathy).

### Changed
- `node-ipc` advisory: corrected to 822K weekly downloads (was 10M+); added specific bad versions (9.1.6, 9.2.3, 12.0.1), DNS C2 IOCs, shasum, forensic markers.
- `TanStack Mini Shai-Hulud` advisory: broadened to full 172-package / 403-version wave including Mistral, UiPath, OpenSearch namespaces; attributed to TeamPCP; noted first valid SLSA-provenance abuse.
- `Claude Code InversePrompt` advisory: added 4 more CVEs (CVE-2025-52882, CVE-2025-59536, CVE-2026-21852, CVE-2026-33068) + TrustFall reference.

---

## 2026-05-16

### Added
- Initial repo: 13 advisories backfilled, 6 playbooks, 5 prevention docs, sources + tools indexes.
- `vibe-security-update` skill at [`.claude/skills/vibe-security-update/`](.claude/skills/vibe-security-update/) with tiered sweep procedure (deep 24h / medium 3d / shallow 7d) and self-learning source-priority list.
- Static site generator (`site/build.py`), template, CSS, validator.
- GitHub Actions deploy workflow.
- Initial 78-source priority list seeded from first-run findings.
