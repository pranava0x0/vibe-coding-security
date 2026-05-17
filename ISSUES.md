# Issues

> Audit trail of bugs, broken links, factual corrections, performance issues, and UAT findings.
> Each entry: date, area, description, root cause (**code bug** vs. **content bug** vs. **infra**), status, resolution commit.
> Newest entries first within each section.

## Open

_See UAT log below; promote any open items here as they're triaged._

## Fixed

_Move closed items here with a Fixed-in commit SHA._

---

## UAT log

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
