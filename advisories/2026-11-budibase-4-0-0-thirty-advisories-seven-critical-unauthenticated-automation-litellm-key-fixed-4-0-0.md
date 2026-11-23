---
id: 2026-11-budibase-4-0-0-thirty-advisories-seven-critical-unauthenticated-automation-litellm-key-fixed-4-0-0
title: "Budibase: 30 vendor advisories on 2026-11-10, seven critical, including unauthenticated automation execution and a LiteLLM key exposure; fixed 4.0.0"
date_disclosed: 2026-11-10
last_updated: 2026-11-23
severity: critical
status: patched
ecosystems: [npm, docker, budibase, low-code, self-hosted]
tools_affected: ["Budibase self-hosted below 4.0.0", "`@budibase/server` (npm), newest 3.38.1, no fixed release", "Budibase tenants that stored a LiteLLM key in the legacy `liteLLM` global settings field"]
tags: [budibase, low-code, app-builder, unauthenticated, authorization-bypass, ssti, sql-injection, ssrf, litellm, secret-exposure, vendor-batch, patched]
---

## TL;DR
[Budibase's advisory tab](https://github.com/Budibase/budibase/security/advisories) holds 30 advisories dated 2026-11-10, seven rated Critical and 23 High, plus four Moderate dated 2026-11-12. The three opened for this file list every version below 4.0.0 as affected and 4.0.0 as patched, with no CVE. One lets an unauthenticated caller run builder-authored automations. One returns a stored LiteLLM key to anyone who can reach the tenant. Run the `v4.0.0` image or later and rotate any LiteLLM key Budibase stored.

## What happened

The tab has 13 pages and 125 rows. The rows are not in date order, so every page was read on 2026-11-23 and the rows counted by date.

| Published | Rows | Critical | High | Moderate |
|---|---|---|---|---|
| 2026-11-10 | 30 | 7 | 23 | 0 |
| 2026-11-12 | 4 | 0 | 0 | 4 |

Three advisories were opened. Each lists package `@budibase/server`, affected `< 4.0.0`, patched `4.0.0`, and no CVE.

| Advisory | Severity | What the advisory says |
|---|---|---|
| [GHSA-5rq2-4mjm-m7q2](https://github.com/Budibase/budibase/security/advisories/GHSA-5rq2-4mjm-m7q2) | Critical 9.1 | `POST /api/automations/:id/test` runs builder-authored automations at service privilege with no builder check. Where a builder's step invokes a shell, that is command execution as root. |
| [GHSA-wr7j-r9v4-6rjh](https://github.com/Budibase/budibase/security/advisories/GHSA-wr7j-r9v4-6rjh) | Critical 9.9 | A user-supplied attachment key is not bound to the app, so a low-privilege user can delete other tenants' files in the shared object-store bucket. Reading a file needs its random filename. |
| [GHSA-c24r-7gmq-4rgm](https://github.com/Budibase/budibase/security/advisories/GHSA-c24r-7gmq-4rgm) | High 7.5 | `GET /api/global/configs/public` needs no login and returns the full global settings object. On tenants with a legacy `liteLLM` field, that includes a LiteLLM virtual key and secret. |

The other five Critical rows dated 2026-11-10 are GHSA-p7c8-m379-jf3x, GHSA-x4w8-596q-fmh7, GHSA-6wc7-w493-mw5m, GHSA-jm85-crv2-88px and GHSA-q4f7-c337-92c9. Their pages were not opened. The tab titles for the first three describe privilege escalation to server-side code execution, an anonymous MongoDB filter bypass in public query templates, and authenticated code execution as root through a datasource plugin.

Two advisories from the batch have CVE records, published by the GitHub CNA on 2026-11-20. [CVE-2026-122247](https://cveawg.mitre.org/api/cve/CVE-2026-122247) (8.2) lets an unauthenticated caller create a global-admin record in an unused tenant namespace on a single-tenant install. [CVE-2026-122244](https://cveawg.mitre.org/api/cve/CVE-2026-122244) (7.7) is stored script execution in the Builder. Both records say "fixed in versions 3.50.0 and 4.0.0" and give the affected range as `< 3.50.0`. The three advisories opened here name only 4.0.0.

GHSA-c24r-7gmq-4rgm's body says no fixed version was identified in the commit the reporter tested. Its metadata lists 4.0.0 as patched.

### Where the fix is

- npm: `npm view @budibase/server versions` ends at 3.38.1, published 2026-05-12. The advisories name this package and a patched version the registry does not carry.
- Docker Hub: `budibase/budibase` has tags `v3.50.0` (pushed 2026-10-19), `v4.0.0` (2026-11-10) and `v4.1.0` (2026-11-23), read 2026-11-23.

### Earlier advisories

[OSV](https://api.osv.dev/v1/query) returned 44 records for `@budibase/server` on 2026-11-23. This repo had no Budibase file before this one. The tab also holds nine rows dated 2026-09-10, four of them Critical, and batches from 2026-07-22 and earlier. Those pages were not opened.

## Am I affected?

Check the running image tag, not the npm package:

```bash
docker ps --format '{{.Image}}' | grep -i budibase
```

- A tag below `v4.0.0` is affected by the three advisories opened here.
- A scanner keyed on CVE ids flags two of the 30.

For the LiteLLM key, request `/api/global/configs/public` on your own tenant without a session and look for a `liteLLM` field in the response.

## If you are affected

1. Move to the `v4.0.0` image or later.
2. If the public settings response held a `liteLLM` field, revoke that LiteLLM key. The advisory says to treat keys stored there as possibly exposed.
3. Review automations that include a shell step, and the run history of `/api/automations/:id/test`, for runs no builder started. This step is this file's advice.
4. Check the user list for global administrators you did not create.

See [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Do not expose a self-hosted builder to the internet. Put it behind a VPN or an authenticating proxy.
- Keep provider keys in the gateway, not in the app builder's settings. See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

Single source: the vendor, plus the GitHub CNA records.

- [Budibase security advisories](https://github.com/Budibase/budibase/security/advisories), pages 1 to 13, fetched 2026-11-23: GHSA id, severity and date per row. Counts were made in code.
- [GHSA-5rq2-4mjm-m7q2](https://github.com/Budibase/budibase/security/advisories/GHSA-5rq2-4mjm-m7q2), [GHSA-wr7j-r9v4-6rjh](https://github.com/Budibase/budibase/security/advisories/GHSA-wr7j-r9v4-6rjh), [GHSA-c24r-7gmq-4rgm](https://github.com/Budibase/budibase/security/advisories/GHSA-c24r-7gmq-4rgm), fetched 2026-11-23 through a summarizing fetch: score, vector, range, patched version, impact. Paraphrased, not quoted.
- [CVE-2026-122247](https://cveawg.mitre.org/api/cve/CVE-2026-122247) and [CVE-2026-122244](https://cveawg.mitre.org/api/cve/CVE-2026-122244), CNA GitHub, published 2026-11-20: descriptions, ranges, scores.
- `npm view @budibase/server versions` and `time`, run 2026-11-23.
- Docker Hub tag API for `budibase/budibase`, read 2026-11-23.
- OSV package query for `@budibase/server`, run 2026-11-23: 44 records.
- Not covered: the other 27 advisories dated 2026-11-10, the four dated 2026-11-12, the 4.0.0 release notes, and which of the 30 the 3.50.0 image fixes.
