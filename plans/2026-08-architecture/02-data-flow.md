# Spec 02 — Data flow: one validated source of truth, many machine-readable views

**Goal.** Make advisory frontmatter the canonical, schema-validated data model, and make
every published artifact (HTML, llms*.txt, JSON, feeds, future OSV/IOC exports) a pure,
deterministic function of it.

**Motivated by.** Glasswing/Daybreak-class agent defenders consume structured data, not
prose. Today, IOCs and affected-package facts live only in advisory prose, so a
downstream tool must scrape markdown — noisy and lossy (citation domains mix with real
C2). This spec consolidates and sequences the BACKLOG items "Structured IOC
frontmatter", "iocs.json", "OSV export", and "integrity manifest" into one flow.

## Target flow

```
advisories/*.md  playbooks/*.md  prevention/*.md      (authoring: markdown + frontmatter)
        │
        ▼
  parse + schema-validate (advisory-schema.json, fail build on violation)
        │
        ▼
   CORPUS (in-memory list of typed records — the only data model)
        │
        ├─► HTML pages (+ JSON-LD, OG, .md mirrors)
        ├─► llms.txt / llms-full.txt / llms-ctx.txt / per-section indexes
        ├─► advisories.json + api/v1/*  (existing)
        ├─► iocs.json / .ndjson / .csv  (new — one row per indicator)
        ├─► osv/<id>.json + all.zip     (new — OSV-format, registerable with osv.dev)
        ├─► feed.xml, sitemap.xml, robots.txt, search.json
        └─► integrity.txt               (new — SHA-256 of every file, written last)
```

## Changes

1. **Structured frontmatter (the enabler).** Optional fields: `cves`, `cwes`, `cvss`
   (vector string), `affected_packages` (ecosystem/name/purl/bad_versions/fixed),
   `affected_models` (hub/repo_id/revision — new, per Spec 01's model supply chain
   class), `iocs` (domains/ips/sha256/accounts). Purl gotchas from BACKLOG apply
   (npm `@`→`%40`, PyPI lowercase). Front-load on new advisories; back-fill top-20
   by severity first.
2. **Validation is a build stage, not a separate script.** `build.py` refuses to emit
   from records that fail the schema; `validate.py` keeps post-emit checks (links,
   required outputs). Today validation is advisory-shaped only at test time.
3. **`iocs.json` + `.ndjson` + `.csv`.** One record per indicator with
   `advisory_id`, `url`, `first_seen`, `severity`, `tags`. This is the artifact a
   Daybreak-style pipeline or a plain `curl | jq` can consume directly.
4. **OSV export.** Emit only for incidents with a real `package@version`; minimal
   records elsewhere. Then register as an osv.dev data source (they invite third-party
   DBs). This gets our data into OSV-Scanner, deps.dev, and every SCA tool for free.
5. **`integrity.txt`.** SHA-256 of every published file, written last; linked from
   security.html; completeness asserted in validate.py. A "trust what you download"
   site should let you verify what you downloaded.
6. **Freshness metadata everywhere.** Every generated artifact embeds
   `generated_at` + source git SHA. Agents deciding whether to re-crawl need this;
   it also kills the recurring "Last full sweep" drift class of bugs (derive
   README's date in build or assert it in validate).

## Ordering & dependencies

Frontmatter (1) blocks 3 and 4. 2, 5, 6 are independent and small. Spec 03's
modularization should land before 3–4 add two more emitters to the monolith.

## Acceptance criteria

- New advisories with `affected_packages` appear in iocs.json and osv/ without manual steps.
- Build fails loudly on schema-invalid frontmatter.
- `sha256sum -c` against integrity.txt passes on a fresh `dist/`.
- Determinism test still passes (two builds → identical bytes, modulo `generated_at`
  policy: embed the commit date, not wall-clock, to preserve reproducibility).

**Effort.** Medium overall; item 1 is the long pole (schema + back-fill).
