# Issues

> Audit trail of bugs, broken links, factual corrections, performance issues, and UAT findings.
> Each entry: date, area, description, root cause (**code bug** vs. **content bug** vs. **infra**), status, resolution commit.
> Newest entries first within each section.

## Open

_None open._

## Fixed

### Supply-chain coverage gap + CI self-hardening — 2026-06-01
Prompted by a personalized exposure audit of the maintainer's other repos, which surfaced pathway categories this knowledge base didn't yet represent or practice.
- **Coverage gap: no CI/CD prevention guide.** Added [`prevention/ci-cd-hardening.md`](prevention/ci-cd-hardening.md) (SHA-pin actions, least-privilege `permissions:`, third-party-action-with-write-token anti-pattern, dangerous triggers, script injection, OIDC publishing) and [`prevention/supply-chain-attack-surface.md`](prevention/supply-chain-attack-surface.md) (a map of all 11 pathways external code/data enters, each linked to its deep guide). Wired both into `prevention/README.md`, `README.md`, `npm-hardening.md`, and `CHANGELOG.md`. Root cause: content gap — GitHub Actions is a top supply-chain vector (Megalodon, elementary-data, Comment-and-Control advisories) but had no dedicated guide.
- **Practice-what-we-preach: the project's own `deploy-site.yml` had the exact gap it documents.** Pinned all four actions to commit SHAs (were floating `@vN`) and scoped `permissions:` per job (`build`: `contents: read`; `deploy`: `pages: write` + `id-token: write`, previously granted to both jobs). Root cause: infra hygiene. Regression guard: a future test could assert no floating `@vN` action tags remain in `.github/workflows/` (logged to BACKLOG).

### Low-severity UAT follow-ups — 2026-06-01
- **[UAT-001] Homepage meta/OG description started mid-list** ("1. Hit by something right now?…"). `derive_description()` now prefers a page's leading `>` blockquote summary (the llmstxt.org convention the README/ALERTS/playbooks already use), falling through to paragraph extraction otherwise. Homepage description is now "A living index of supply-chain attacks…". Bonus: 20 other pages (alerts, playbooks, prevention, sources, tools) improved from list/code fragments to their real summaries — verified with a full before/after description diff; **no advisory descriptions changed, no regressions**. Root cause: code (deriver heuristic).
- **[UAT-002] `.page-action` touch target ~30px → 44px** (`site/style.css` `min-height`). "View raw markdown" / "Edit on GitHub" are now 44px tall, single-line at desktop width (verified in preview). Root cause: code (CSS).
- **[UAT-003] node-ipc "10M weekly" → "~822K weekly"** in `README.md`, matching the sourced figure in `advisories/2026-05-node-ipc-compromise.md` (single source of truth). Root cause: content.

### Data-freshness + llms.txt-accuracy pass — 2026-06-01
- **`README.md` "Last full sweep: 2026-05-28" → "2026-05-31"** — was stale vs the actual last sweep (recorded in the skill `runs.log.md` and reflected by ALERTS.md "Last refreshed: 2026-05-31"). Root cause: content (field not bumped by recent daily sweeps).
- **`README.md` node-ipc "two days ago" → "May 14"** — a relative date frozen at the 2026-05-16 seed (node-ipc disclosed 2026-05-14); 18 days stale. Replaced with an absolute date so it can't rot. Root cause: content.
- **llms.txt size annotations were badly stale** — generated `llms.txt` advertised `llms-full.txt (~230KB)` / `llms-ctx.txt (~10KB)`; real sizes were ~505KB / ~71KB. Made the figures **dynamic** in `build.py` (`_human_size()` computes from the actual built bytes) so the index can never drift again; README/CHANGELOG prose updated to match. Root cause: hardcoded magic numbers (code/content).
- **`tests/test_llms.py` `LLMS_FULL_MAX_BYTES` 512KB → 640KB** — `llms-full.txt` was at ~505KB (98.7% of the cap); the next daily sweep would have broken the build/deploy. Bumped with a dated comment + a note to trim historical advisories rather than keep raising the cap. Root cause: corpus growth against a guardrail (maintenance).

---

## UAT log

### 2026-06-01 — UAT pass (local `dist/` build) + freshness/perf/llms.txt audit

Run against a local server of `dist/` (browser walkthrough at 1280px desktop, 375px mobile, dark mode) + `python3 site/validate.py` + `pytest tests/` + a live HTTP sweep of all artifact URLs.

**Findings:**

- **[INFO]** Renders cleanly at 1280px (3-column: nav + sidebar + right-rail TOC), 634px (single-column, hamburger), and 375px mobile. Dark mode (`prefers-color-scheme: dark`) themes the whole page; severity colors intact.
- **[INFO]** Mobile hamburger menu works — `body.nav-open` toggled by an inline `onclick` (no external JS); opens a full-screen nav with all 7 sections. `aria-expanded` flips correctly; toggle button is 44×44px.
- **[INFO]** No console errors/warnings anywhere (site ships zero external JS; only inline JSON-LD + the menu `onclick`).
- **[INFO]** All 9 `validate.py` checks pass; **86/86 pytest** pass (incl. build determinism after the dynamic-size change).
- **[INFO]** Live HTTP sweep: all 32 sampled URLs (HTML, `.md` mirrors, all `llms*.txt`, per-section `llms.txt`, JSON/API endpoints, feed, sitemap, robots, security.txt) return 200.
- **[FRESH]** Fixed two stale date strings in README (see Fixed: `2026-05-28`→`2026-05-31`, and node-ipc "two days ago"→"May 14"). ALERTS.md "Last refreshed: 2026-05-31" is current (1 day old, inside the 7-day window). `.well-known/security.txt` `Expires: 2027-12-31` — valid. Build/feed/sitemap dates are generated via `date.today()` — always fresh.
- **[PERF]** HTML pages 5–22KB gzipped (alerts.html largest at 72KB raw / 22KB gz); `style.css` 17KB raw / 4.3KB gz. A typical page = 2 requests (HTML + CSS), no JS/fonts/images/third-parties. Excellent.
- **[PERF]** **Fixed:** `llms-full.txt` (~505KB) was at 98.7% of its 512KB test cap — one sweep from breaking the deploy. Cap bumped to 640KB. `llms-ctx.txt` ~71KB (cap 96KB).
- **[LLMS]** **Fixed:** the index's size annotations were wrong (`~230KB`/`~10KB` vs real `~505KB`/`~71KB`); now computed dynamically. `llms.txt` validated: starts with `# title`, `> summary`, has all required sections, lists every advisory, Optional section links the alternates.
- **[OPEN]** Logged UAT-001 (homepage meta description starts mid-list), UAT-002 (`.page-action` ~30px touch target), UAT-003 (node-ipc download-count discrepancy) — all low severity.

**No regressions.** Build, validators, and full test suite green after the fixes.

### 2026-05-17 — UAT pass on deployed site

Run against <https://pranava0x0.github.io/vibe-coding-security/>. Manual walkthrough + automated tests (`python3 site/validate.py` + `pytest tests/`).

**Findings:**

- **[INFO]** Site loads cleanly at 375×667 (iPhone SE), 414×896 (iPhone Pro Max), 768×1024 (iPad portrait), 1024×768 (iPad landscape), 1280×800, 1920×1080. No layout breakage at any breakpoint.
- **[INFO]** Sidebar appears at ≥900px; right-rail TOC at ≥1200px. Below those breakpoints, content stays single-column with hamburger menu.
- **[INFO]** All 9 build-validator checks pass (required outputs, no leftover .md links, all internal links resolve, HTML metadata present, heading hierarchy OK, advisory frontmatter complete, llms.txt format, sitemap.xml well-formed, advisories.json sane).
- **[INFO]** All pytest checks pass (advisory frontmatter schema, link integrity, no committed secrets, advisory ID uniqueness, llms.txt format, JSON-LD parses, sitemap parses, atom feed parses, build determinism, etc.).
- **[INFO]** Light + dark themes render correctly under `prefers-color-scheme`. `prefers-reduced-motion` honored.
- **[PERF]** Average page weight (HTML + CSS) under 30KB gzipped. No JS bundles. No web fonts. No third-party requests.
- **[PERF]** `llms-full.txt` is ~145KB (well under the 200K-token Mintlify recommendation).
- **[PERF]** `llms-ctx.txt` is ~12KB — fits in any context window.
- **[PERF]** `feed.xml` truncated to 25 most recent advisories to keep size sane.
- **[A11Y]** Skip-link present and works. 44px touch targets on all interactive elements. ARIA labels on nav landmarks. `<time datetime>` on all dates. Focus-visible outlines on every link and button.

**No regressions detected.** Site, build, and skill are all in known-good state.

---

## Repo-specific issues

_Bugs in the build pipeline, skill, or site go here, not in `advisories/`._

_None at this time._
