# Spec 04 — Search, landing pages, filter chips, JSON-LD

> **Theme:** frontend & discoverability · **Effort:** medium · **Depends on:** Spec 01 (`attack_class`), Spec 02 (`affected_packages`, `cves`)
> **Status:** proposed

## Problem

**`search.json` ships to nobody.** `build_search_index()`
([site/build.py:1005](../../site/build.py)) emits a 137-entry index with title,
url, section, description, severity, status, and date on every build. No page
loads it. The data has been published and unused for the whole life of the site.

**There is no way to answer the most common question.** A reader wants to know
"is axios affected?" or "what is CVE-2026-30615?". Today: browse 107 advisory
filenames, or use the browser's in-page find on the advisories index. Both fail.
Those are also the two highest-volume search queries this content could ever
rank for, and the site has no page that targets either.

**Filtering doesn't exist.** 107 advisories render as one flat list. A reader who
only cares about PyPI, or only about `critical`, reads all of them.

**JSON-LD is thin.** `build_jsonld()` ([site/build.py:474](../../site/build.py))
emits `TechArticle` for advisories with headline, description, keywords, and
dates. It never expresses what the advisory is *about* — no affected software, no
CVE identifiers — because until Spec 02 that data wasn't structured.

## Constraint: this is the site's first JavaScript

`site/template.html` currently contains exactly one line of JS — an inline
`onclick` on the menu toggle. No bundler, no framework, no `.js` file, no build
step beyond Python. That is a feature: the site is 137 static pages that work with
JS disabled, load instantly, and have no supply chain of their own.

**A repo about supply-chain security must not acquire a JS dependency tree to
build a search box.** This is not aesthetic preference — shipping a bundler and
30 transitive dev-dependencies to a project that publishes npm advisories would
be indefensible.

Rules for everything in this spec:

- Vanilla JS, one hand-written file, no dependencies, no build step.
- `site/search.js` copied verbatim into `dist/` the way `style.css` already is.
- Every feature degrades to working HTML with JS off.
- No third-party requests at runtime — no CDN, no analytics, no font fetch. The
  site's own CSP posture should stay "everything is same-origin."

---

## Deliverable 1 — Client-side search

### Behaviour

- `/` anywhere on the page focuses the search input. `Esc` clears and blurs.
- Results appear as you type, under the input, replacing nothing on the page.
- `↑`/`↓` move through results, `Enter` navigates, `Tab` works normally.
- Under ~50 ms per keystroke on the full index.
- Results show title, section badge, and severity badge — enough to choose
  without clicking.

### Implementation

`search.json` is currently 137 entries with short descriptions. Fetch it once on
first focus (not on page load — most visitors never search), cache in memory.

Matching: case-insensitive substring across title, description, and — once Spec
02 lands — package names and CVE IDs. Rank by field weight: title hit > package
or CVE hit > description hit. Resist adding fuzzy matching until substring
demonstrably falls short; a 137-item corpus does not need a scoring library, and
"fuzzy" mostly produces confusing near-misses at this size.

### Accessibility

This is the part that is usually skipped and is not optional here:

- `role="combobox"` on the input with `aria-expanded`, `aria-controls`,
  `aria-activedescendant`.
- Results in `role="listbox"`, each `role="option"` with a stable id.
- An `aria-live="polite"` region announcing "7 results" — debounced, so
  fast typing doesn't flood a screen reader.
- Visible focus ring on the active result; never rely on colour alone.

### Degradation

Render the input inside `<noscript>`-aware markup: with JS off, the search box is
replaced by a plain link to `/advisories/index.html`. Never show a dead input.

### Tests

`tests/test_html.py`: every page contains the search input with correct ARIA
attributes; `search.js` exists in `dist/`; `search.json` parses and every `url`
in it resolves to a real file in `dist/`. That last one is a genuine bug class —
the index is generated separately from the pages and could drift.

---

## Deliverable 2 — Per-package and per-CVE landing pages

Both are already in BACKLOG.md under Medium. Spec 02 is what makes them
buildable from data rather than from prose scraping.

### `/packages/<ecosystem>/<name>.html`

Namespaced by ecosystem, because `pypi/requests` and `npm/requests` are different
packages and a flat `/packages/requests.html` silently merges them.

Generated for every distinct package in any advisory's `affected_packages`.
Content:

- Package name, ecosystem, purl.
- Affected versions and fixed version, as a table — the fact the reader came for,
  above the fold.
- Every advisory mentioning it, newest first.
- A copy-pasteable check command, per ecosystem:
  `npm ls axios` / `pip show requests`.

Slug carefully. `@tanstack/react-router` must become a safe path — recommend
`packages/npm/@tanstack/react-router.html` written as a nested directory, or a
flattened `packages/npm/tanstack__react-router.html`. Pick one, write it down,
and test it, because scoped names are where this will break.

### `/cve/<CVE-ID>.html`

Generated for every ID in any advisory's `cves`. Content: the ID, which
advisories reference it, the CVSS vector if present, and outbound links to NVD
and the relevant ecosystem advisory database. Keep it thin — this page exists to
be *found*, and to route to the advisory that has the real analysis. Do not
restate the advisory.

### Index pages

`/packages/index.html` and `/cve/index.html`, both alphabetical, both in the
sitemap. These are what make the individual pages crawlable.

### Build integration

New emitter in Spec 03's registry (`emitters/landing.py`), or a new
`build_*` function plus a `main()` line if Spec 03 hasn't landed. It must:

- Feed `discover_pages()`-equivalent metadata into the sitemap.
- Appear in `search.json`.
- **Not** appear in `llms.txt` / `llms-full.txt`. These pages are derived views of
  advisories that are already in the corpus; including them would duplicate every
  advisory N times and blow the size budget Spec 05 is fixing. This exclusion is
  a hard requirement and needs its own test.

### Tests

Every package/CVE page resolves from every advisory that references it and back;
no orphans in either direction; scoped-name slugs round-trip; no landing page
appears in any `llms*.txt`.

---

## Deliverable 3 — Filter chips

On `/advisories/index.html` and `/alerts.html`.

Facets: `severity`, `status`, `ecosystem`, `attack_class` (Spec 01).

- Chips are toggle buttons; multiple selections within a facet are OR, across
  facets are AND.
- **State in the URL hash** — `#severity=critical&ecosystem=npm` — so a filtered
  view is shareable and back/forward work. This is the whole reason to prefer
  hash state over in-memory state.
- Filtering hides rows client-side; with JS off, all rows show and the chips are
  hidden. Never render a chip that does nothing.
- Live region announcing "23 of 107 advisories".

`attack_class` is the facet that makes this worth building — it is the only one
with a controlled vocabulary, so its chip set is finite, stable, and complete.
Free-text `tags` deliberately gets no chips; see Spec 01 on why that vocabulary
can't back a UI.

---

## Deliverable 4 — JSON-LD upgrades

Once Spec 02 lands, `build_jsonld()` can express what advisories are actually
about.

**Advisory pages** — extend the existing `TechArticle`:

```python
data["about"] = [
    {"@type": "SoftwareApplication", "name": pkg["name"],
     "applicationCategory": pkg["ecosystem"]}
    for pkg in fm.get("affected_packages", [])
]
data["identifier"] = fm.get("cves", [])
```

**Package pages** — `SoftwareApplication` with the affected versions.

**CVE pages** — `TechArticle` with `identifier` set to the CVE ID.

**Every page** — add `BreadcrumbList`. The breadcrumb is already rendered by
`build_breadcrumb()` ([site/build.py:433](../../site/build.py)); the structured
form is the same data and search engines use it directly.

**Site root** — `WebSite` with `SearchAction` pointing at the search page, now
that search exists.

### Validation

Add a `validate.py` check: every page's JSON-LD parses, has `@context` and
`@type`, and every URL in it resolves. Malformed JSON-LD fails silently in the
wild — it needs a test, not a manual paste into a validator.

---

## Sequencing

1. **Search** — standalone, needs nothing from other specs, immediately useful.
2. **JSON-LD breadcrumbs + `WebSite`/`SearchAction`** — small, no dependencies.
3. **Landing pages** — after Spec 02.
4. **Filter chips** — after Spec 01.
5. **JSON-LD `about`/`identifier`** — after Spec 02.

Steps 1–2 can ship immediately; do not block them on the data specs.

---

## Done when

- [ ] `site/search.js` — vanilla, dependency-free, copied to `dist/`.
- [ ] Search works: `/` to focus, keyboard nav, `< 50 ms`, full ARIA, degrades
      to a link with JS off.
- [ ] `/packages/<ecosystem>/<name>.html` + index, for every affected package.
- [ ] `/cve/<ID>.html` + index, for every referenced CVE.
- [ ] Landing pages in sitemap and `search.json`, **excluded** from `llms*.txt`,
      with a test enforcing the exclusion.
- [ ] Filter chips on advisories + alerts, hash-backed, degrading cleanly.
- [ ] JSON-LD: `about`, `identifier`, `BreadcrumbList`, `WebSite`/`SearchAction`.
- [ ] `validate.py` parses and link-checks every page's JSON-LD.
- [ ] No new runtime dependency, no bundler, no third-party request.
- [ ] `build.py` → `validate.py` → `pytest` all green.

## Explicitly out of scope

- Any JS framework, bundler, or npm dependency. See "Constraint" above.
- Server-side search. The site is static and stays static.
- Fuzzy/typo-tolerant matching in v1.
- OG image generation (BACKLOG, Low) — related but separate.
- `Cmd-K` palette (BACKLOG, Low) — build it on the search index later if wanted.
