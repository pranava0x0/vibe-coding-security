---
id: 2026-10-strapi-kev-relational-filter-admin-hash-leak-2026-recurrence
title: "Strapi: CISA adds the 2023 relational-filter hash leak to KEV (CVE-2023-22894); the same class returned in 2026 as unauthenticated admin takeover (CVE-2026-27886, fixed 5.37.0)"
date_disclosed: 2026-10-08
last_updated: 2026-10-12
severity: high
status: active
ecosystems: [npm, strapi, headless-cms, nodejs]
tools_affected: ["Strapi 3.2.1 through 4.7.1 (CVE-2023-22894, now in KEV)", "Strapi 4.0.0 through 5.36.1 (CVE-2026-27886)", "@strapi/content-type-builder 5.0.0 through 5.33.1 and @strapi/plugin-content-type-builder 4.0.0 through 4.26.0 (CVE-2026-22599)", "@strapi/core 5.0.0 through 5.5.1 (CVE-2024-56143) and before 5.20.0 (CVE-2025-53092)", "@strapi/upload, @strapi/admin, @strapi/plugin-users-permissions before 5.33.3 and 5.45.0", "any app whose AI-generated backend scaffolds a Strapi content API"]
tags: [cve, kev, exploited-in-the-wild, headless-cms, strapi, query-filter, information-disclosure, admin-takeover, sql-injection, cors, rate-limit, zero-files-large-tab, recurrence]
---

## TL;DR
On 2026-10-08 CISA added **CVE-2023-22894** to the Known Exploited Vulnerabilities catalog with a 2026-10-11 due date and the forensic-triage flag. The bug let a caller filter Strapi's REST API on private fields of related admin users and infer password hashes and reset tokens one character at a time; the researcher showed it works with no account on any site that has a public collection with an admin relation, and it chains with CVE-2023-22621 into unauthenticated remote code execution on 4.5.5 and earlier. It was fixed in Strapi 4.8.0 on 2023-03-15, so an instance still exploitable today is three and a half years behind. The reason this file exists for a 2023 CVE is the vendor's own tab: **the same class came back twice**, as CVE-2024-56143 (Strapi 5.0.0 through 5.5.1, published 2025-10-16, 8.2) and as **CVE-2026-27886** (4.0.0 through 5.36.1, published 2026-05-13, CVSS 4.0 9.2, unauthenticated, reset-token oracle through `updatedBy`), alongside an authenticated SQL injection in the Content-Type Builder (CVE-2026-22599, 9.3) and a CORS misconfiguration that reflects any origin with credentials (CVE-2025-53092, 7.5). Strapi had no file in this corpus before today. Current release is 5.57.0; anything below 5.37.0 has the 2026 oracle.

## What happened

### The exploited one: CVE-2023-22894
Strapi's REST API removed private fields (password hash, `resetPasswordToken`, email on admin accounts) from responses but not from the query. A request could still filter on them. Filtering a public collection by a relation to `admin_users` with prefix comparisons on the hash field turns the API into a boolean oracle: each request confirms or denies one more character. GhostCcamm's write-up (2023-04-17) states the attack needs no account when a public collection references an admin user, which Strapi populates automatically when an administrator creates or edits an entry, and that the leaked reset token takes over a Super Administrator, after which CVE-2023-22621 (template injection in the users-permissions email templates, fixed 4.5.6) gives code execution. Strapi's disclosure post says the report was first rated Medium because the first vector needed admin access, was escalated to Critical on 2023-01-18 when the unauthenticated path was found, and was fixed in 4.8.0 on 2023-03-15.

The records disagree on the affected range and the score, and both disagreements matter for a reader deciding whether to act:

| Source | Affected | Score | Note |
|---|---|---|---|
| CVE description (NVD, 2023-04-19) | "through 4.5.5" | NVD 4.9 (PR:H) | the description predates the unauthenticated finding |
| NVD CPE range and Strapi blog | `>= 3.2.1, < 4.8.0` | CISA-ADP 7.2 | fixed 4.8.0 |
| GhostCcamm | `<= 4.7.1` | author's vector 9.8 | same endpoint as NVD, inclusive form |
| CISA KEV (2026-10-08) | "could be end-of-life"; "can be chained with CVE-2023-22621" | none | CWE-312, due 2026-10-11, forensic triage: Yes |

Use `< 4.8.0`. The KEV name, "Cleartext Storage of Sensitive Information," is CISA's CWE label and not a description of the mechanism, which is a filter-side information leak. CISA does not say who is exploiting it or where; the catalog entry is the only public evidence of exploitation this sweep found, and no outlet had covered the addition on 2026-10-12.

### The recurrences on the vendor tab
Strapi publishes on `github.com/strapi/strapi/security/advisories`, which had no file here and had never been opened by a sweep. Its ten entries:

| Advisory | CVE | Published | Affected | Fixed | Score (provider) | What it is |
|---|---|---|---|---|---|---|
| GHSA-rjg2-95x7-8qmx | CVE-2026-27886 | 2026-05-13 | `@strapi/strapi` 4.0.0 through 5.36.1 | 5.37.0 | 9.2 CVSS 4.0 (vendor page shows 9.3 in one place and 9.2 in another; CNA record 9.2) | **The 2023 bug again.** An unauthenticated caller uses the `where` parameter on a public content type with an admin-relation field such as `updatedBy` to run a boolean oracle against `admin_users`, including `resetPasswordToken`, then takes over the account. Fix adds `strictParam`, `addQueryParams` and `addBodyParams` sanitisers at controller and service layers. Reporter WildWestCyberSecurity. |
| GHSA-3xcq-8mjw-h6mx | CVE-2026-22599 | 2026-05-13 | `@strapi/content-type-builder` 5.0.0 through 5.33.1; `@strapi/plugin-content-type-builder` 4.0.0 through 4.26.0 | 5.33.2; 4.26.1 | 9.3 CVSS 4.0 (PR:H) | An administrator passes a raw tuple in `column.defaultTo` when creating or editing a content type and it reaches Knex's raw query during migration. File read, crash, or code execution on the database host depending on engine. Fix returns 404 from all Content-Type Builder write endpoints outside development mode. |
| GHSA-pcw7-5633-82vv | CVE-2026-22707 | 2026-05-13 | `@strapi/upload` through 5.33.2 | 5.33.3 | 5.3 | Content API uploads skipped the MIME allow and deny lists the admin path enforced; HTML or SVG served from the admin origin runs as the admin who opens it. |
| GHSA-7mqx-wwh4-f9fw | CVE-2025-64526 | 2026-05-13 | `@strapi/plugin-users-permissions` (CNA: `< 5.45.0`) | 5.45.0 per the CNA record; the vendor page prints `<= 5.44.0` affected beside `>= 5.25.0` patched and a literal `<PATCHED_VERSION>` placeholder | 6.9 | Rate-limit key on `/auth/local`, `/auth/reset-password` and `/auth/change-password` included the request body's `email`, so each request gets a fresh key. Use the CNA's 5.45.0. |
| GHSA-hvp3-26wx-g2w4 | CVE-2026-22706 | 2026-05-13 | `@strapi/admin`, `@strapi/plugin-users-permissions` through 5.33.2 | 5.33.3 | 2.1 | Password reset did not revoke existing refresh tokens unless a `deviceId` was sent; a stolen refresh token survives the reset for its 30-day lifetime. |
| GHSA-9329-mxxw-qwf8 | CVE-2025-53092 | 2025-10-16 | `@strapi/core` before 5.20.0 | 5.20.0 | 7.5 CVSS 3.1 | Default install reflects the request `Origin` into `Access-Control-Allow-Origin` with `Allow-Credentials: true`, so any page the admin visits reads the API as the admin. |
| GHSA-495j-h493-42q2 | CVE-2024-56143 | 2025-10-16 | `@strapi/core` 5.0.0 through 5.5.1 | 5.5.2 | 8.2 CVSS 3.1 | Strapi 5's document-service `lookup` operator did not sanitise private fields; a list-view URL filters on a related user's password hash prefix by prefix. The first recurrence of the 2023 class, in the rewritten v5 query layer. |
| GHSA-2cjv-6wg9-f4f3 | not shown | 2025-10-16 | | | Low | Weak password length validation. |
| GHSA-v8wj-f5c7-pvxf | not shown | 2025-05-27 | | | Moderate | SSRF in the webhook function. |
| GHSA-wrvh-rcmr-9qfc | not shown | 2024-06-12 | | | High | Third-party token leak and authentication bypass. |

The last three rows are listed from the tab index only; their pages were not opened this sweep, so no ranges are given.

### Why this is in a vibe-coding feed
Strapi is the headless CMS that Next.js and Nuxt starters, and the app builders that generate them, reach for when a project needs an editable content backend with a REST and GraphQL API. The exposed surface is exactly the one the 2023 and 2026 bugs use: a public content type with an admin relation, served by a Node process that also holds the admin panel. The same shape produced the [Payload CMS wave](2026-09-payload-cms-thirty-advisory-wave-form-builder-rce-sqli-mcp-plugin-takeover.md) a month ago, and the lesson is the same: the CMS behind a generated frontend is a privileged service with its own advisory tab, and a `npm audit` on the frontend will not show it.

### Status and severity
`active` because CISA says the 2023 bug is being exploited now, with a three-day due date and a forensic-triage requirement for federal agencies. `high` rather than `critical`: the exploited CVE has had a fix for three and a half years, the 2026 oracle (9.2) has had one since 2026-05-13 and no exploitation is reported for it, and the 9.3 SQL injection needs an administrator. The 9.2 and 9.3 are the CNA's CVSS 4.0 base scores as published 2026-05-14; NVD's 4.9 for the 2023 CVE reflects the pre-escalation admin-only vector and CISA's ADP 7.2 was added later. None of the three numbers is this advisory's assessment.

## Am I affected?

```bash
# Version in a project
npm ls @strapi/strapi @strapi/core @strapi/content-type-builder @strapi/upload @strapi/plugin-users-permissions 2>/dev/null
jq -r '.dependencies["@strapi/strapi"] // .dependencies.strapi' package.json 2>/dev/null
# Anything below 5.37.0 has CVE-2026-27886; anything below 4.8.0 has the KEV-listed CVE-2023-22894
# Public collections with an admin relation (the precondition for both oracles)
grep -rln '"updatedBy"\|"createdBy"\|admin::user' src/api/*/content-types/*/schema.json 2>/dev/null
# Request logs: Strapi's own 2023 detection looks for bracketed filter parameters naming
# password, resetPasswordToken or email fields; repeated requests of that shape over minutes
# are the oracle running. Strapi's disclosure post carries the exact regex.
grep -iE 'filters?\[.*\](password|resetPasswordToken|email)' /var/log/strapi/*.log 2>/dev/null | head
```

- **3.x:** end of life since 2022-12-31 and never fixed for CVE-2023-22894 or CVE-2023-22893. CISA's "discontinue use" clause applies.
- **4.0.0 to 4.7.1:** exposed to the KEV-listed bug and, on 4.5.5 and earlier, to the RCE chain.
- **4.8.0 to 5.36.1:** clear of the 2023 bug, exposed to CVE-2026-27886 if any public content type carries an admin relation.
- **5.37.0 and later:** clear of both oracles. Check the plugin versions in the table separately; the Content-Type Builder fix is 5.33.2 and the rate-limit fix 5.45.0.

## If you are affected

1. **Upgrade to the current 5.x** (5.57.0 on 2026-10-07). For a 4.x project that cannot move majors today, 4.8.0 removes the exploited bug and 4.26.1 the Content-Type Builder injection, but the 2026 oracle has no 4.x fix and the CNA range for it starts at 4.0.0.
2. **If logs show the filter pattern, treat every admin account as taken over.** Reset every admin password and invalidate sessions, rotate the API tokens and transfer tokens the admin panel manages, rotate the database credential and any provider keys in `.env`, and look for new admin users, new API tokens and edited email templates (the CVE-2023-22621 chain). [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. **Audit the exposed surface** with [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md): which content types are public, which carry `createdBy`/`updatedBy` populated, and whether the admin panel shares the public origin.
4. **Set an explicit CORS origin list** if you are below 5.20.0 or inherited a reflected-origin config.

## Prevention

- **The CMS behind a generated frontend is a privileged backend.** Give it its own dependency audit and watch its advisory tab, not only the frontend's: [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- **Keep the admin panel off the public origin** and behind an allowlist or VPN; both oracles and the CORS bug need a request to reach the admin's API from outside.
- **A KEV addition years after the fix is a version-age signal.** If a 2023 CVE is being exploited in 2026, there are enough unpatched Strapi 4.x hosts to be worth scanning for. Pin a floor in CI and fail builds below it: [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Rate-limit by IP, not by a request field,** and revoke sessions on password change; both were defaults Strapi had to fix.

## Sources
- [CISA Known Exploited Vulnerabilities catalog (JSON feed)](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) — fetched 2026-10-12, catalog version 2026.10.08: the CVE-2023-22894 entry, `dateAdded` 2026-10-08, `dueDate` 2026-10-11, `knownRansomwareCampaignUse` Unknown, `forensicTriage` Yes, CWE-312, the end-of-life and CVE-2023-22621 chaining notes, and the BOD 26-04 required action.
- [NVD — CVE-2023-22894](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2023-22894) — fetched 2026-10-12: description ("through 4.5.5", admin-panel access), CPE range `< 4.8.0`, NVD 4.9 (PR:H) and CISA-ADP 7.2, `cisaExploitAdd` 2026-10-08, last modified 2026-10-09.
- [Strapi — Security disclosure of vulnerabilities (CVE-2023-22621, -22893, -22894)](https://strapi.io/blog/security-disclosure-of-vulnerabilities-cve) — fetched 2026-10-12: the affected ranges, 4.8.0 on 2023-03-15, the Medium-to-Critical escalation on 2023-01-18, the 3.x end-of-life statement, the detection regex and the incident-response advice.
- [GhostCcamm — Multiple Strapi vulnerabilities](https://www.ghostccamm.com/blog/multi_strapi_vulns/) — fetched 2026-10-12: the unauthenticated precondition (a public collection referencing an admin user), the `<= 4.7.1` range, the chain into CVE-2023-22621, the 280-file fix scope. The researcher withheld the exploit script.
- [Strapi security advisories tab](https://github.com/strapi/strapi/security/advisories) — fetched 2026-10-12: the ten rows above. Opened: [GHSA-rjg2-95x7-8qmx](https://github.com/strapi/strapi/security/advisories/GHSA-rjg2-95x7-8qmx) (CVE-2026-27886), [GHSA-3xcq-8mjw-h6mx](https://github.com/strapi/strapi/security/advisories/GHSA-3xcq-8mjw-h6mx) (CVE-2026-22599), [GHSA-pcw7-5633-82vv](https://github.com/strapi/strapi/security/advisories/GHSA-pcw7-5633-82vv) (CVE-2026-22707), [GHSA-7mqx-wwh4-f9fw](https://github.com/strapi/strapi/security/advisories/GHSA-7mqx-wwh4-f9fw) (CVE-2025-64526, with the `<PATCHED_VERSION>` placeholder), [GHSA-hvp3-26wx-g2w4](https://github.com/strapi/strapi/security/advisories/GHSA-hvp3-26wx-g2w4) (CVE-2026-22706), [GHSA-9329-mxxw-qwf8](https://github.com/strapi/strapi/security/advisories/GHSA-9329-mxxw-qwf8) (CVE-2025-53092), [GHSA-495j-h493-42q2](https://github.com/strapi/strapi/security/advisories/GHSA-495j-h493-42q2) (CVE-2024-56143).
- CVE Services (CNA: GitHub), fetched 2026-10-12, the ranges and CVSS 4.0 scores in the table: [CVE-2026-27886](https://cveawg.mitre.org/api/cve/CVE-2026-27886) (`>= 4.0.0, < 5.37.0`, 9.2), [CVE-2026-22599](https://cveawg.mitre.org/api/cve/CVE-2026-22599) (9.3), [CVE-2026-22707](https://cveawg.mitre.org/api/cve/CVE-2026-22707), [CVE-2025-64526](https://cveawg.mitre.org/api/cve/CVE-2025-64526) (`< 5.45.0`), [CVE-2026-22706](https://cveawg.mitre.org/api/cve/CVE-2026-22706); all published 2026-05-14.
- Registry, checked 2026-10-12: `npm view @strapi/strapi time` shows 4.5.5 on 2022-12-28, 4.5.6 on 2023-01-11, 4.8.0 on 2023-03-15, latest 5.57.0 on 2026-10-07.
- Related in this corpus: [Payload CMS thirty-advisory wave](2026-09-payload-cms-thirty-advisory-wave-form-builder-rce-sqli-mcp-plugin-takeover.md) (the other headless CMS under generated frontends, same zero-files-large-tab shape), [UpGuard: 16,000 exposed Supabase databases](2026-09-upguard-supabase-16k-exposed-databases-rls-systemic.md) (the backend-exposure pattern the CMS case repeats).
