# Backlog

> Ideas for future improvements to this repo. Priority: high / medium / low.

## High

- **Weekly sweep cadence.** Document who refreshes ALERTS.md weekly and how. Add `last_swept` date to README so staleness is visible.
- **`scripts/check-lockfile.sh`** — a shell script that reads `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` and greps for IOCs from advisories. Output: `OK` or list of matches with advisory links.
- **MCP-server advisory subdirectory.** As more malicious MCPs appear, split `advisories/mcp/` from `advisories/npm/`. Probably wait until we have 5+ MCP entries.

## Medium

- **GitHub Action: RSS-to-issue.** Poll Socket / Snyk / GHSA RSS, file an issue with the `new-advisory` template when a relevant item appears. Filter by package popularity (>100k weekly downloads) or specific ecosystems to keep noise down.
- **CLI tool** that wraps `npm install` and checks the package name against ALERTS.md before allowing the install. (Subset of what `npq` does, but specifically tied to this advisory list.)
- **Static site** (GitHub Pages, no JS) for browsing. Probably hugo or 11ty with one page per advisory.
- **Per-tool quick reference cards.** "If you use Cursor, read these 4 advisories." "If you use Claude Code, these 5." Reduces cognitive load.
- **PyPI parity.** Most current advisories are npm. Add coverage for Python supply-chain attacks (already have slopsquatting; could use a Python-specific hardening doc).

## Low

- **JSON export** of the advisory metadata (frontmatter only) so third parties can build dashboards.
- **OSV.dev contribution.** Where possible, push our IOC data back into OSV so the broader ecosystem benefits.
- **Translations.** At least Spanish / Mandarin / Hindi. Big vibe-coding audiences in those languages.
- **Stickers / printables.** A laminated 1-pager of the "60-second package vetting checklist" you can tape to a monitor.
- **`bin/new-advisory`** scaffold script that copies the template and pre-fills the frontmatter from CLI args.
