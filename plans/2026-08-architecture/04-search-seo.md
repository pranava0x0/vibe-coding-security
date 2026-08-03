# Spec 04 — Searchability & SEO: findable by humans, navigable by crawlers

**Goal.** Someone who just saw a scary package name — or an agent resolving "is X
compromised?" — reaches the right advisory in one hop.

**Motivated by.** Glasswing/Daybreak normalize "ask an agent first"; agents cite pages
they can crawl and rank. Humans still arrive via Google with a package name or CVE id.
Both paths are underserved: no on-site search, no per-package/per-CVE landing pages.

## 1. Client-side search (BACKLOG high — confirmed, concretized)

- Build-time index (existing `search.json`) + a small hand-rolled scorer, or
  Pagefind if we accept one build-time dev dependency (it emits static assets, no
  runtime service — compatible with "static + boring"). Decision point at impl time;
  default to hand-rolled (~200 lines) to keep zero deps.
- UX: topbar box, `/` focuses, arrow keys navigate, instant on type, ARIA live region.
- Index fields: title, TL;DR, package names, CVE ids, `attack_class` (Spec 01),
  ecosystems. Weight package/CVE exact matches to the top.

## 2. Entity landing pages (the SEO workhorse)

- `/packages/<name>.html` — every advisory mentioning the package, current verdict
  ("known-bad versions: …"), IOC rows, link to the playbook. Generated from
  `affected_packages` frontmatter (Spec 02) — no scraping prose.
- `/cve/<id>.html` — same for CVEs.
- These match the two highest-intent query shapes ("<package> malware",
  "<CVE-id>") that today land on generic index pages, and they're what
  shields.io badges and external tools will deep-link to.

## 3. Filter chips on alerts + advisories indexes (BACKLOG high — confirmed)

Facets: severity, status, ecosystem, `attack_class`. State in URL hash so filtered
views are shareable/bookmarkable (each shared link is an SEO signal too).

## 4. On-page SEO hardening (small, do opportunistically)

- BreadcrumbList JSON-LD + visible breadcrumbs on advisory pages.
- `FAQPage` JSON-LD for the "Am I affected?" section (it is literally Q&A).
- Descriptive `<title>` pattern: `<package/incident> — <severity> — Vibe Coding Security`.
- Build-time OG image per advisory (title + severity badge) — BACKLOG low item;
  it earns its keep on social/Slack unfurls where advisories actually spread.
- Related-advisories block (same package, same class) — internal linking for
  crawlers, recirculation for humans.

## Acceptance criteria

- Search returns the right advisory for a package name in <50ms locally, keyboard-only.
- Package/CVE pages exist for everything with structured frontmatter; sitemap includes them.
- Lighthouse SEO score ≥ 95 on advisory pages (add to the CI-gates backlog item).

**Dependencies.** 2 depends on Spec 02 frontmatter; all page generation lands as
emitters per Spec 03. Chips/search are independent and can start anytime.

**Effort.** Medium–large; search and entity pages are separately shippable.
