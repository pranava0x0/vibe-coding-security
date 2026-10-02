# mcp-remote: evidence review

> Checked 2026-10-02. Public evidence supporting the [advisory correction and severity review](../advisories/2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md).

## Mapping correction

[Issue #114](https://github.com/pranava0x0/vibe-coding-security/issues/114) correctly identified a mapping error: CVE-2026-51995 references F-02, not F-10. The decisive field is `containers.cna.references` in the CVE record. The other four mappings also match their finding-specific references.

The original sweep introduced the error on 2026-09-25. The old F-10 research score and CISA's F-02 score both read 7.5, but that does **not** establish how the mistake happened. The failure we can establish is that the table did not follow the cited reference. NVD, GitHub and OSV repeat the same upstream record; agreement among those copies is not independent verification.

## Registry evidence

Snapshots below preserve the responses fetched on 2026-10-02. These are public source records, not proof that every upstream claim is correct. Live endpoints: [CVE Services](https://cveawg.mitre.org/api/cve/CVE-2026-51995), [NVD](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-51995), [OSV](https://api.osv.dev/v1/vulns/CVE-2026-51995). Substitute the CVE ID to retrieve a sibling record.

| CVE | Finding | Saved CVE record | Saved NVD response | Saved OSV response |
|---|---|---|---|---|
| CVE-2026-51994 | F-01 | [CVE](cve-evidence/CVE-2026-51994.cve.json) | [NVD](cve-evidence/CVE-2026-51994.nvd.json) | [OSV](cve-evidence/CVE-2026-51994.osv.json) |
| CVE-2026-51995 | F-02 | [CVE](cve-evidence/CVE-2026-51995.cve.json) | [NVD](cve-evidence/CVE-2026-51995.nvd.json) | [OSV](cve-evidence/CVE-2026-51995.osv.json) |
| CVE-2026-51996 | F-04 | [CVE](cve-evidence/CVE-2026-51996.cve.json) | [NVD](cve-evidence/CVE-2026-51996.nvd.json) | [OSV](cve-evidence/CVE-2026-51996.osv.json) |
| CVE-2026-51997 | F-08 | [CVE](cve-evidence/CVE-2026-51997.cve.json) | [NVD](cve-evidence/CVE-2026-51997.nvd.json) | [OSV](cve-evidence/CVE-2026-51997.osv.json) |
| CVE-2026-52001 | F-11 | [CVE](cve-evidence/CVE-2026-52001.cve.json) | [NVD](cve-evidence/CVE-2026-52001.nvd.json) | [OSV](cve-evidence/CVE-2026-52001.osv.json) |

Exact fields to inspect:

- Mapping: CVE `containers.cna.references[].url`.
- Attribution and score: CVE `containers.adp[].providerMetadata`, `title`, and `metrics[].cvssV3_1` (score, severity and full vector). MITRE supplied no CNA metrics in these records.
- NVD status: `vulnerabilities[0].cve.vulnStatus` is `Deferred`; the four `metrics.cvssMetricV31[]` entries identify CISA's provider UUID and type `Secondary`.
- OSV conflict: `affected[].ranges[].database_specific.extracted_events[]` marks 0.1.38 as fixed, with source `DESCRIPTION`. The corresponding CVE descriptions include 0.1.38 in the affected range. None of those inferred boundaries establishes a vendor fix.

## Impact and severity

The [advisory's dated score table](../advisories/2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md#severity-review-2026-10-02) reproduces CISA-ADP's 9.1, 7.5, 9.8 and 8.8 scores; F-11 has none. The site keeps **high / unconfirmed**, an editorial rating distinct from the external CVSS scores. The trade-off is a headline below two Critical scores, with the disagreement visible rather than silently resolved.

The versioned researcher pages support narrower claims:

| Finding | Source and locator | Evidence limit |
|---|---|---|
| F-01 | [Research, Security impact / Evidence](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-01-resource-metadata-ssrf.md) | Local canary received requests; no response exfiltration demonstrated. |
| F-02 | [Research, Security impact / Evidence](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-02-authorization-server-ssrf.md) | Blind probing demonstrated; no response exfiltration. |
| F-04 | [Research, Correction and limitations](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-04-md5-token-isolation.md) | No token namespace takeover or real-token access demonstrated; weak-hash hardening does not itself prove code execution. Research starts at 0.0.14; CVE starts at 0.1.16. |
| F-08 | [Research, Evidence and limitations](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-08-browser-url-validation.md) | Source/dependency review; no internal service contacted. Browser and destination controls affect impact. |
| F-10 | [Research, Evidence and limitations](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-10-redirect-validation-bypass.md) | Separate redirect-following finding, source review only; no CVE in this batch. |
| F-11 | [Research, Current positive controls](https://github.com/playb0t/mcp-remote-oauth-security/blob/v1.0.1/advisories/F-11-sse-token-origin-scope.md) | SDK origin validation and redirect credential stripping refute the originally claimed forwarding path in the reviewed dependencies. Research starts at 0.0.18; CVE starts at 0.1.18. |

These limits do not establish that stronger impact is impossible, nor reject or formally dispute a CVE. They establish what the cited research demonstrates. New vendor confirmation, a reproducible stronger impact, or changed records should trigger another review. No exploit was run for this review.

## Validation and limits

`python tools/validate_cve_evidence.py` checks every ID-first `F-<number>` finding table in the corpus against a required evidence manifest. It rejects missing snapshots, wrong record IDs, unpublished CVEs, ambiguous finding references, moved or missing CVEs, stale score tables, and unreviewed inclusive-end/fixed-version conflicts. The build validator and pytest run this offline.

`python tools/validate_cve_evidence.py --live` re-fetches only fixed registry endpoints and fails on changed records or network errors. It never follows researcher URLs, redirects, or instructions inside fetched data. `--refresh` explicitly replaces snapshots after all requests for a bundle succeed; it does not rewrite advisory prose or choose severity. Review the diff, then use `--scores <advisory-id>` to print the updated score block.

Coverage is intentionally bounded: other advisory formats still require manual primary-source review. Snapshot checks detect disagreement with captured evidence, not false statements inside that evidence. Live checks detect record changes, not every possible vendor release. The version check recognizes inclusive `through X` text versus an OSV `fixed` boundary; it is not a general version-range parser. Reference URLs with no unique finding require manual resolution, not score matching.

Private session transcripts, reporter profiling, unverified literature summaries, and workflow deliberations are not published here. The original local research file remains ignored. Only rechecked public evidence and the resulting editorial decisions are included.
