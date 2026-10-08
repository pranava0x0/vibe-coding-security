---
id: 2026-09-payload-cms-thirty-advisory-wave-form-builder-rce-sqli-mcp-plugin-takeover
title: "Payload CMS (the Next.js-native headless CMS; 1.1M weekly downloads): 32 vendor advisories between 2026-09-18 and 10-06, 29 CVEs assigned 10-06 — unauthenticated RCE through the Form Builder plugin (CVE-2026-105857, 10.0), unauthenticated SQL injection in the Postgres/SQLite adapters (CVE-2026-105845, 9.8), unauthenticated document update on orderable collections (CVE-2026-105859, 9.8), forged auth-token claims (CVE-2026-105863, 9.2), prototype-pollution RCE in Import/Export (CVE-2026-105844, 9.3), and three MCP-plugin bugs including account takeover through the MCP password-recovery tool; fixed 3.88.0 → 3.90.0"
date_disclosed: 2026-09-18
last_updated: 2026-10-08
severity: critical
status: patched
ecosystems: [npm, nextjs, react, postgres, sqlite, mcp]
tools_affected: [payload, "@payloadcms/plugin-form-builder", "@payloadcms/plugin-import-export", "@payloadcms/plugin-mcp", "@payloadcms/db-postgres", "@payloadcms/db-sqlite", "@payloadcms/db-vercel-postgres", "@payloadcms/db-d1-sqlite", "@payloadcms/db-mongodb", "@payloadcms/plugin-multi-tenant", "@payloadcms/plugin-ecommerce", "@payloadcms/plugin-stripe", "@payloadcms/storage-s3", "@payloadcms/storage-vercel-blob", "@payloadcms/next", "Next.js apps generated with Payload as the backend (v0, Lovable, Cursor, Claude Code templates)"]
tags: [cve, headless-cms, nextjs, rce, sql-injection, prototype-pollution, authorization-bypass, mcp, account-takeover, vendor-advisory-wave, silent-fix-then-disclosure, backfill]
---

## TL;DR
Payload — the TypeScript headless CMS that installs *inside* a Next.js app and is the backend AI app builders reach for when a prompt says "add a CMS/admin panel" — published **32 security advisories on its own GitHub tab between 2026-09-18 and 2026-10-06**, and GitHub (as CNA) assigned **29 CVEs to them on 2026-10-06**. Five are critical and three of those need **no authentication**: a crafted form submission to the **Form Builder plugin executes code on the server** (CVE-2026-105857, CVSS 10.0), a dynamic filter or join on any readable collection is a **SQL injection in the Postgres and SQLite adapters** (CVE-2026-105845, 9.8), and an update endpoint on collections with `orderable: true` lets anyone **modify documents past access control** (CVE-2026-105859, 9.8). The **MCP plugin** that lets agents drive the CMS has three bugs of its own, one an **account takeover through the MCP password-recovery tool**. Everything is fixed in **payload 3.90.0** (released 2026-09-18; registry `latest` 3.90.2) or `4.0.0-canary.34`; several of the September-22 advisories describe fixes that had shipped silently in **3.88.0 on 2026-08-11**. If your generated Next.js app has a `payload.config.ts`, upgrade every `payload` and `@payloadcms/*` package together and rotate the auth secret.

## What happened

**Who Payload is for.** Payload is a code-first CMS/application framework: collections are TypeScript config, the admin UI and REST/GraphQL API mount inside the host Next.js app, and the database adapter is a package you pick (`@payloadcms/db-postgres`, `db-sqlite`, `db-mongodb`, `db-vercel-postgres`, Cloudflare `db-d1-sqlite`). The registry shows **1,108,564 weekly downloads of `payload`** and 754,955 of `db-postgres` for the week ending 2026-10-04 (`api.npmjs.org`). The plugins named below are the ones generated apps pull in by default: Form Builder (157,562/week), Multi-Tenant (122,780), MCP (164,918), Import/Export (56,623). It is the backend of the official Next.js "website" template that v0, Lovable and the coding agents reach for, so an app whose author never typed `payload` can still be running it.

**The wave, by date the vendor published it.** The tab has five pages; the September-18 page alone is twenty entries. Mapped by the GitHub-as-CNA records (each CVE's single GHSA reference) and the NVD keyword window 2026-09-15 → 10-07, which returned exactly 29 Payload CVEs, all published 2026-10-06:

| Vendor date | Advisory | CVE | Score (GitHub-as-CNA) | Auth needed | Fixed |
|---|---|---|---|---|---|
| 2026-09-18 | **RCE in Payload Form Builder** (`@payloadcms/plugin-form-builder`) | **CVE-2026-105857** | **10.0** (3.1, `AV:N/AC:L/PR:N/UI:N/S:C`) | **No** | 3.90.0 |
| 2026-09-18 | **Unauthorized update to collection documents** (`orderable: true` on a collection or join field) | **CVE-2026-105859** | **9.8** (3.1) | **No** | 3.90.0 (affects 3.32.0+) |
| 2026-09-18 | **Payload authentication token field handling issue** — a custom field option mapped to a reserved auth claim name puts attacker-shaped values into the JWT | **CVE-2026-105863** | **9.2** (4.0, `AT:P`) | No | 3.90.0 |
| 2026-09-18 | **Field access control bypass on auth collections** — `duplicate` copies hidden / `access.read`-denied / `access.create`-denied fields; `disableDuplicate` (default on auth collections) did not stop it | **CVE-2026-105851** | **9.3** (4.0) | No | 3.90.0 |
| 2026-09-18 | **Remote Code Execution through first-register** — the public first-user operation, exploitable while a local-auth app has no users yet | CVE-2026-105858 | 8.1 (3.1, `AC:H`) | No | 3.90.0 |
| 2026-09-18 | **ReDoS in multipart Content-Type validation** | CVE-2026-105854 | 8.7 | No | 3.90.0 |
| 2026-09-18 | **Uploaded XML files could execute same-origin JavaScript** (XML uploads are accepted by default) | CVE-2026-105868 | 8.6 | Yes (upload) | 3.90.0 |
| 2026-09-18 | **Bypassed sanitization of user-uploaded SVGs** (stored XSS on download) | CVE-2026-105862 | 8.7 (3.1) | Yes | 3.90.0 |
| 2026-09-18 | **SQL injection in SQLite/Postgres** via `json` / `blocksAsJSON` field paths and operators | CVE-2026-105856 | 8.6 | Yes (read + create/update) | db-sqlite / d1 **3.90.0**; db-postgres / vercel-postgres **3.73.0** |
| 2026-09-18 | **Order confirmation processed more than once** (Ecommerce + Stripe adapter) | CVE-2026-105850 | 8.8 | No | 3.90.0 |
| 2026-09-18 | **Incomplete validation during the upload file lifecycle** (path traversal in cleanup → deletes other files) | CVE-2026-105865 | 8.1 (3.1) | Yes | 3.90.0 |
| 2026-09-18 | **API key disclosure through ordinary document reads** | CVE-2026-105849 | 7.7 | Yes | 3.90.0 |
| 2026-09-18 | **Field-level password update restrictions were not enforced** | CVE-2026-105855 | 7.6 | Yes | 3.90.0 |
| 2026-09-18 | **Polymorphic join queries could disclose hidden fields** (incl. password-reset tokens) | CVE-2026-105847 | 7.1 | Yes | 3.90.0 |
| 2026-09-18 | **Token refresh and password reset responses expose restricted user fields** | CVE-2026-105853 | 7.1 | Yes | 3.90.0 |
| 2026-09-18 | **Tenant authorization bypass in Multi-Tenant Plugin** (self-assign to other tenants) | CVE-2026-105860 | 7.1 | Yes | 3.90.0 |
| 2026-09-18 | **Client uploads could overwrite S3 objects** of another collection (`@payloadcms/storage-s3`) | CVE-2026-105867 | 7.1 | Yes | 3.90.0 |
| 2026-09-18 | **External upload trust validation issue** — auth headers forwarded to unverified destinations | CVE-2026-105861 | 7.2 | Yes | 3.90.0 |
| 2026-09-18 | Unauthenticated account-lockout denial of service | CVE-2026-105866 | 6.9 | No | 3.90.0 |
| 2026-09-18 | Relationship-query authorization bypass | CVE-2026-105852 | 6.9 | Yes | 3.90.0 |
| 2026-09-18 | Insufficient access control in Stripe REST proxy | CVE-2026-105848 | 6.4 | Yes | 3.90.0 |
| 2026-09-18 | Cross-tenant create in Multi-Tenant Plugin | CVE-2026-105864 | 5.3 | Yes | 3.90.0 |
| 2026-09-22 | **SQL Injection in SQLite and Postgres** via dynamic filters / joins on any readable collection | **CVE-2026-105845** | **9.8** (3.1, `PR:N`) | **No** (any caller who can query a readable collection) | **3.88.0** |
| 2026-09-22 | **Prototype pollution in Import/Export plugin → RCE** | **CVE-2026-105844** | **9.3** (4.0, `PR:N`) | **No** | **3.88.0** |
| 2026-09-22 | **Improper access control for MCP API keys** (`@payloadcms/plugin-mcp` 3.61.0+) — manage another account's keys → account takeover | CVE-2026-105806 | 8.6 | Yes | 3.88.0 |
| 2026-09-22 | Sort queries expose protected field information | CVE-2026-105805 | 6.9 | No | 3.88.0 |
| 2026-09-22 | Untrusted redirect URL parameter (`@payloadcms/next`) | CVE-2026-105846 | 6.1 (3.1) | No | 3.88.0 |
| 2026-09-25 | Access control bypass of client uploads in Vercel Blob adapter | — (no CVE) | 5.3 | Yes | 3.90.0 |
| 2026-09-29 | Password hashes use insufficient PBKDF2 iterations (hashes upgraded on next login) | CVE-2026-105804 | 5.7 | — | 3.90.0 |
| 2026-10-06 | **Account takeover through MCP password recovery** (`plugin-mcp`, experimental auth tools enabled) | — (no CVE as of 10-07) | 7.6 (`AT:P`) | Yes (MCP user) | **3.90.0** |
| 2026-10-06 | **Hidden-field leak in MCP login responses** (`plugin-mcp`) | — | 7.1 | Yes | 3.88.0 |
| 2026-10-06 | **Access bypass of Payload Jobs** — read/modify job records past configured permissions | — | 8.7 | Yes | 3.89.0 |
| 2026-08-27 (DB 10-06) | Field-level write access bypass on MongoDB (`@payloadcms/db-mongodb`) | CVE-2026-106100 | 7.1 | Yes | 3.87.0 |

Reporter credits on the vendor pages are mostly one independent researcher (**Zerotistic**, named on the 10.0, both 9.8s, the 9.3 field bypass, the 9.2 token bug, first-register and the Jobs bypass) plus Payload's own maintainer (DanRibbens, the SQL injection), iamnoooob (Import/Export), mufeedvh (MCP password recovery), georgelzrc, wsparks-vc and pavelkohout396.

**Three things to notice about how it was disclosed.**

1. **Fixes shipped weeks before the advisories.** Payload's own release post for **3.88.0 (2026-08-11)** describes three "hardening" changes — multipart parsing "no longer backtracks," tighter clipboard matching, and "the API keys collection now ships with safer access-control defaults" for the MCP plugin — with no CVE and no severity. The 2026-09-22 advisories are those fixes: CVE-2026-105845 and CVE-2026-105844 (both `PR:N` criticals) and CVE-2026-105806 all say "fixed in 3.88.0." Anyone who read the August release notes as routine had six weeks of exposure they did not know about. The **3.90.0** release page (2026-09-18) does say "⚠️ This release contains a set of critical security fixes … upgrade as soon as possible," and that "exploit details, attack surface descriptions, and severity are intentionally omitted" with "CVE and GHSA identifiers … published separately" — which they were, eighteen days later.
2. **The database lagged the vendor by 14–18 days.** All 29 CVE records carry `datePublished` 2026-10-06; the vendor pages are 09-18 to 09-29. A sweep that dates by the database would file a September wave as October news (this repo's §19/§39 rule). The three 10-06 MCP-plugin / Jobs advisories genuinely are new, and carry no CVE yet.
3. **The MCP plugin is now an attack surface in its own right.** `@payloadcms/plugin-mcp` (165k weekly downloads) exposes CMS operations to agents through API keys; three of the 32 advisories are about it — key management outside your own account (takeover, 8.6), a password-recovery tool that recovers *other* accounts (7.6), and login responses that return fields the caller may not read (7.1). The second is only reachable when the "experimental authentication tools" are enabled, and the vendor's own workaround is to revoke the forgot-password tool from MCP API keys. An agent with a Payload MCP key is an authenticated user; every `PR:L` row above is in its reach.

**What is not established.** No source opened for this advisory reports in-the-wild exploitation; EPSS was not checked. The Form Builder RCE page gives no mechanism beyond "a crafted form submission," and this write-up does not speculate. Scores are GitHub-as-CNA's (the vendor's own CVSS on the advisory pages); NVD had not yet added its own analysis to the 10-06 records at fetch time.

## Am I affected?

You are running Payload if any of these hit:

```bash
# any payload / @payloadcms package below 3.90.0 (db-postgres below 3.73.0 for CVE-2026-105856)
grep -E '"(payload|@payloadcms/[a-z0-9-]+)"\s*:' package.json
npm ls payload @payloadcms/plugin-form-builder @payloadcms/plugin-import-export @payloadcms/plugin-mcp @payloadcms/db-postgres @payloadcms/db-sqlite 2>/dev/null | grep -v 3.90
ls payload.config.* src/payload.config.* 2>/dev/null
grep -rl "@payloadcms/plugin-mcp\|formBuilderPlugin\|importExportPlugin" --include=*.ts --include=*.tsx . 2>/dev/null | head
```

- **Form Builder plugin on any version < 3.90.0** → unauthenticated RCE (10.0). Treat the server as compromised if the form endpoint was internet-reachable; check for unexpected processes, cron entries, new users in the `users` collection and outbound connections from the host during the window.
- **Postgres / SQLite / Vercel Postgres / D1 adapter < 3.88.0** and any collection readable by unauthenticated or low-trust users → SQL injection (9.8). Review database logs for `UNION`, stacked statements or unusual `where`/`joins` query parameters against `/api/<collection>`.
- **Any collection or join field with `orderable: true` on 3.32.0 – 3.89.x** → anyone could update documents (9.8). Diff recent `updatedAt` values against your audit expectations.
- **`plugin-mcp` with experimental auth tools or API keys issued to agents** → review the `payload-mcp-api-keys` collection for keys you did not create and for keys attached to the wrong user; revoke and re-issue.
- **Import/Export plugin < 3.88.0** → unauthenticated prototype pollution → RCE (9.3).
- **Local auth with field options mapped to reserved claim names** (CVE-2026-105863) → rotate `PAYLOAD_SECRET`; every existing JWT becomes invalid, which is the point.

## If you are affected

1. **Upgrade every `payload` and `@payloadcms/*` package to the same version, ≥ 3.90.0** (or `4.0.0-canary.34`+). Mixed versions across the monorepo packages are unsupported and leave adapter fixes unapplied.
2. **Rotate `PAYLOAD_SECRET`** (invalidates all sessions and API keys — CVE-2026-105863 and the MCP key bugs both touch token material), then re-issue agent API keys with the minimum collections.
3. If Form Builder or Import/Export was exposed below 3.88/3.90, follow [if-your-webapp-was-compromised](../playbooks/if-your-webapp-was-compromised.md) and [rotating-cloud-credentials](../playbooks/rotating-cloud-credentials.md) — the CMS process holds the database URL, storage credentials and (for Ecommerce) the Stripe secret.
4. For an app a coding agent generated for you, run [auditing-a-vibe-coded-repo](../playbooks/auditing-a-vibe-coded-repo.md): check which plugins the agent enabled (Form Builder and MCP are often added "because the template has them") and remove the ones you do not use.

## Prevention

- Pin and float: keep `payload` and `@payloadcms/*` on one caret range and reinstall monthly; Payload's advisories now land on its GitHub tab weeks before CVEs exist, so watch `github.com/payloadcms/payload/security/advisories`, not the CVE feed.
- Treat an MCP API key to your CMS as a user account with the same blast radius; scope it to the collections the agent needs and leave experimental auth tools off ([mcp-hygiene](../prevention/mcp-hygiene.md)).
- Disable XML/XSL and SVG uploads unless you need them; serve uploads with attachment headers and a strict CSP.
- [supply-chain-attack-surface](../prevention/supply-chain-attack-surface.md) — the admin panel a generator added is a second application with its own CVE stream.

## Update 2026-10-08 — the tab keeps producing: eight more advisories (2026-10-06/08), including a High improper-authentication bug in the MCP plugin's custom-auth path (fixed 3.88.0) and a CSV formula-injection in Import/Export

Payload's security tab added eight advisories on **2026-10-06 and 10-08**, after the 29-CVE wave above — the pattern this file opened with (the generator's admin panel is a second application with its own continuous CVE stream) continuing:

- **[GHSA-cqr4-hjg9-833p](https://github.com/payloadcms/payload/security/advisories/GHSA-cqr4-hjg9-833p) — improper authentication in MCP when using custom authentication** (`@payloadcms/plugin-mcp` 3.64.0 – 3.87.x → **3.88.0**, High, CVSS 4.0 7.6, published 2026-10-08). Under non-default MCP auth configurations the access restriction may not be enforced, so an authenticated user reaches MCP functionality that should be unavailable; default MCP auth configs are unaffected. Fix makes custom MCP auth use the configured credential.
- **[GHSA-jjm7-864w-gg8q](https://github.com/payloadcms/payload/security/advisories/GHSA-jjm7-864w-gg8q) — hidden-field leak in MCP login responses** (High, published 2026-10-06).
- Six Moderate advisories dated **2026-10-08**: incorrect authorization for framework collections (GHSA-8j2x-hjh9-3ff8), **CSV formula injection in `@payloadcms/plugin-import-export`** (GHSA-97w9-jq7h-73pq), excessive-authentication-attempts (GHSA-m35c-r5p5-c3w8), authorization bypass of client uploads (GHSA-g6p9-6gm4-cj6m), insufficient session expiration after password changes (GHSA-wvw7-x9pg-w4cc), and improper privilege management in scheduled publishing (GHSA-mg7r-jhr9-m745).

No CVE ids were shown on the tab for these yet; the two MCP-plugin bugs are the ones that matter most for a generated backend that exposes an MCP endpoint. Status stays `patched` (all carry fix versions, with the MCP custom-auth fix in 3.88.0 the same floor as the September wave). Upgrade `payload` and every `@payloadcms/*` plugin together to the current line.

## Related
- [Next.js September 2026 security release](2026-09-nextjs-september-2026-security-release-seven-advisories.md) and [next/og ImageResponse RCE](2026-09-nextjs-og-imageresponse-satori-svg-rce.md) — the host framework's own wave the same month.
- [npm core-library critical batch](2026-09-npm-core-library-critical-batch-shell-quote-proxy-addr-seroval.md) — the same disclosure shape (vendor tab weeks ahead of the CVE) in libraries one layer down.

## Sources
- [payloadcms/payload — Security Advisories (pages 1–5)](https://github.com/payloadcms/payload/security/advisories) — walked 2026-10-07: the 32 entries from 2026-02-05 onward, titles, severities and vendor dates used above.
- Vendor advisory pages opened 2026-10-07 (title, CVSS, affected/patched, description, credit): [GHSA-r488-j9vj-wx3q — RCE in Payload Form Builder, CVE-2026-105857](https://github.com/payloadcms/payload/security/advisories/GHSA-r488-j9vj-wx3q); [GHSA-f7hx-52q9-hcrf — Unauthorized update to collection documents, CVE-2026-105859](https://github.com/payloadcms/payload/security/advisories/GHSA-f7hx-52q9-hcrf); [GHSA-66wr-7vmr-p5jq — authentication token field handling, CVE-2026-105863](https://github.com/payloadcms/payload/security/advisories/GHSA-66wr-7vmr-p5jq); [GHSA-97rh-rhh2-7vjv — RCE through first-register, CVE-2026-105858](https://github.com/payloadcms/payload/security/advisories/GHSA-97rh-rhh2-7vjv); [GHSA-pj7x-6wpf-pgvp — SQL injection in SQLite/Postgres (json/blocks), CVE-2026-105856](https://github.com/payloadcms/payload/security/advisories/GHSA-pj7x-6wpf-pgvp); [GHSA-fx49-4h83-wjv9 — field-level password update, CVE-2026-105855](https://github.com/payloadcms/payload/security/advisories/GHSA-fx49-4h83-wjv9); [GHSA-xgv3-crq2-6f69 — token refresh / password reset responses, CVE-2026-105853](https://github.com/payloadcms/payload/security/advisories/GHSA-xgv3-crq2-6f69); [GHSA-p96c-xwx8-3cqj — Multi-Tenant authorization bypass, CVE-2026-105860](https://github.com/payloadcms/payload/security/advisories/GHSA-p96c-xwx8-3cqj); [GHSA-2g7p-5934-q4w7 — multipart ReDoS, CVE-2026-105854](https://github.com/payloadcms/payload/security/advisories/GHSA-2g7p-5934-q4w7); [GHSA-r9v2-gg2j-22q5 — Stripe REST proxy, CVE-2026-105848](https://github.com/payloadcms/payload/security/advisories/GHSA-r9v2-gg2j-22q5); [GHSA-fpww-c55p-cjv6 — polymorphic join hidden fields, CVE-2026-105847](https://github.com/payloadcms/payload/security/advisories/GHSA-fpww-c55p-cjv6); [GHSA-7vg8-29qx-jgj8 — S3 object overwrite, CVE-2026-105867](https://github.com/payloadcms/payload/security/advisories/GHSA-7vg8-29qx-jgj8); [GHSA-9qpg-3cf8-w33x — XML same-origin JavaScript, CVE-2026-105868](https://github.com/payloadcms/payload/security/advisories/GHSA-9qpg-3cf8-w33x); [GHSA-2pwp-2369-8fg3 — SVG sanitization bypass, CVE-2026-105862](https://github.com/payloadcms/payload/security/advisories/GHSA-2pwp-2369-8fg3); [GHSA-p223-2wr2-j562 — upload lifecycle validation, CVE-2026-105865](https://github.com/payloadcms/payload/security/advisories/GHSA-p223-2wr2-j562); [GHSA-xhm9-gwgw-3q2q — cross-tenant create, CVE-2026-105864](https://github.com/payloadcms/payload/security/advisories/GHSA-xhm9-gwgw-3q2q); [GHSA-8r29-2mp2-pmrw — Ecommerce order confirmation, CVE-2026-105850](https://github.com/payloadcms/payload/security/advisories/GHSA-8r29-2mp2-pmrw); [GHSA-v5gf-vpjc-pc7w — account-lockout DoS, CVE-2026-105866](https://github.com/payloadcms/payload/security/advisories/GHSA-v5gf-vpjc-pc7w); [GHSA-w84c-53h3-mc2g — untrusted redirect, CVE-2026-105846](https://github.com/payloadcms/payload/security/advisories/GHSA-w84c-53h3-mc2g); [GHSA-9g87-32v6-3c2r — sort queries, CVE-2026-105805](https://github.com/payloadcms/payload/security/advisories/GHSA-9g87-32v6-3c2r); [GHSA-pj5h-5q6c-3pfx — external upload trust, CVE-2026-105861](https://github.com/payloadcms/payload/security/advisories/GHSA-pj5h-5q6c-3pfx); [GHSA-q6mq-ch85-c8mm — PBKDF2 iterations, CVE-2026-105804](https://github.com/payloadcms/payload/security/advisories/GHSA-q6mq-ch85-c8mm); [GHSA-mc8m-rr6c-r5qr — Vercel Blob client uploads](https://github.com/payloadcms/payload/security/advisories/GHSA-mc8m-rr6c-r5qr); [GHSA-h5rh-4jwf-738p — account takeover through MCP password recovery](https://github.com/payloadcms/payload/security/advisories/GHSA-h5rh-4jwf-738p); [GHSA-jjm7-864w-gg8q — hidden-field leak in MCP login responses](https://github.com/payloadcms/payload/security/advisories/GHSA-jjm7-864w-gg8q); [GHSA-2qw6-cm49-277x — access bypass of Payload Jobs](https://github.com/payloadcms/payload/security/advisories/GHSA-2qw6-cm49-277x).
- Database copies opened 2026-10-07: [GHSA-v49j-62m6-pgrr — SQL Injection in SQLite and Postgres, CVE-2026-105845](https://github.com/advisories/GHSA-v49j-62m6-pgrr); [GHSA-qf28-8hc6-vwrp — prototype pollution in Import/Export, CVE-2026-105844](https://github.com/advisories/GHSA-qf28-8hc6-vwrp); [GHSA-vc4h-q48j-5hcx — field access control bypass on auth collections, CVE-2026-105851](https://github.com/advisories/GHSA-vc4h-q48j-5hcx); [GHSA-2q76-m6w6-qgc6 — MCP API keys, CVE-2026-105806](https://github.com/advisories/GHSA-2q76-m6w6-qgc6).
- [CVE Services — CVE-2026-105857](https://cveawg.mitre.org/api/cve/CVE-2026-105857), [CVE-2026-105845](https://cveawg.mitre.org/api/cve/CVE-2026-105845), [CVE-2026-105844](https://cveawg.mitre.org/api/cve/CVE-2026-105844), [CVE-2026-105851](https://cveawg.mitre.org/api/cve/CVE-2026-105851), [CVE-2026-105806](https://cveawg.mitre.org/api/cve/CVE-2026-105806), [CVE-2026-105856](https://cveawg.mitre.org/api/cve/CVE-2026-105856), [CVE-2026-105804](https://cveawg.mitre.org/api/cve/CVE-2026-105804) — GitHub-as-CNA records, all `datePublished` 2026-10-06; the GHSA reference on each is the mapping used above.
- [NVD API — keyword `payloadcms`, published 2026-09-15 → 2026-10-07](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=payloadcms&pubStartDate=2026-09-15T00:00:00.000&pubEndDate=2026-10-07T23:59:59.000) — 29 records, every one published 2026-10-06, each with one GHSA reference; CVE-2026-106100 (MongoDB, vendor 08-27) is the only one outside the September wave.
- [Payload — New in Payload: hardening uploads, copy/paste, and MCP defaults (3.88.0)](https://payloadcms.com/posts/releases/new-in-payload-hardening-uploads-copypaste-and-mcp-defaults) — 2026-08-11 release post; the three "hardening" lines quoted above, no CVE or severity.
- [payloadcms/payload — Release v3.90.0](https://github.com/payloadcms/payload/releases/tag/v3.90.0) — 2026-09-18; the "critical security fixes … identifiers published separately" notice quoted above.
- Registry: [`api.npmjs.org` weekly downloads](https://api.npmjs.org/downloads/point/last-week/payload) for `payload`, `@payloadcms/plugin-mcp`, `plugin-form-builder`, `plugin-import-export`, `plugin-multi-tenant`, `db-postgres`, `db-sqlite` (week 2026-09-28 → 10-04); `npm view payload dist-tags.latest` → 3.90.2 on 2026-10-07.
- **2026-10-08 update source** — [payloadcms/payload — Security Advisories (page 1)](https://github.com/payloadcms/payload/security/advisories) (walked 2026-10-08: the eight 2026-10-06/08 entries, GHSA ids, severities and the 3.88.0 MCP custom-auth fix quoted above; CVE ids not yet shown).
