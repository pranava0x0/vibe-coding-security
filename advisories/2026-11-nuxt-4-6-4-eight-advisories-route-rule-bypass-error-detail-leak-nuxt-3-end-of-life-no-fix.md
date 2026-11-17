---
id: 2026-11-nuxt-4-6-4-eight-advisories-route-rule-bypass-error-detail-leak-nuxt-3-end-of-life-no-fix
title: "Nuxt: eight advisories on 2026-11-02, route-rule bypasses and server error details sent to clients; fixed in 4.6.4, no fix for Nuxt 3"
date_disclosed: 2026-11-02
last_updated: 2026-11-17
severity: medium
status: patched
ecosystems: [npm, nuxt, vue, nitro, vite]
tools_affected: ["nuxt 4.0.0 before 4.6.4", "nuxt 3.x, end of life, no fixed release", "@nuxt/nitro-server before 4.6.4", "@nuxt/vite-server 4.6.0 before 4.6.4", "@nuxt/schema 3.5.0 before 4.6.4", "@nuxt/webpack-builder and @nuxt/rspack-builder before 4.6.4"]
tags: [cve, ghsa, nuxt, route-rules, authorization-bypass, incomplete-fix, information-disclosure, dev-server, dns-rebinding, end-of-life, no-fix-for-old-line, web-framework]
---

## TL;DR
Nuxt 4 before 4.6.4 lets an unauthenticated request skip route rules and path-based server middleware on page routes, and sends the message and data of unhandled server errors to the client. The Nuxt team published [eight advisories](https://github.com/nuxt/nuxt/security/advisories) on 2026-11-02, all fixed in 4.6.4. Five also affect Nuxt 3, and four of those say "Nuxt 3 has reached end of life and will not receive a fix". Upgrade to `nuxt` 4.6.4. On Nuxt 3, move to Nuxt 4 or apply the workaround in each advisory.

## What happened

The Nuxt advisory tab shows eight advisories dated 2026-11-02, read 2026-11-17. The npm registry shows `nuxt` 4.6.4 published on 2026-11-02. The GitHub Advisory Database listed seven of them on 2026-11-13 and 2026-11-16 with CVE ids. The eighth, GHSA-p4h3-4h99-9665, printed "No known CVE" when read.

| Advisory | CVE | Severity | Affected | Nuxt 3 |
|---|---|---|---|---|
| [GHSA-r99w-jh2x-3mg9](https://github.com/nuxt/nuxt/security/advisories/GHSA-r99w-jh2x-3mg9): a leading `//` in the path bypasses `server/middleware` path checks and server route rules | CVE-2026-128077 | Moderate 6.5 | `@nuxt/nitro-server` 4.6.0 before 4.6.4 | not affected |
| GHSA-f3x9-2chm-73c8: an encoded slash (`%2F`) bypasses route rules on catch-all page routes | CVE-2026-128071 | Moderate | `nuxt` 4.0.0 before 4.6.4, and 3.x | affected, no fix |
| [GHSA-96x6-fvhx-49hg](https://github.com/nuxt/nuxt/security/advisories/GHSA-96x6-fvhx-49hg): message and data of unhandled server-rendering errors reach the client | CVE-2026-128075 | Moderate 5.3 | `nuxt` 4.0.0 before 4.6.4, and 3.x | affected, no fix |
| GHSA-mjrq-cffv-q4qc: dev server serves files from a parent directory that holds a stray lockfile or workspace file | CVE-2026-128070 | Moderate | `@nuxt/schema` 3.5.0 before 4.6.4 | affected from 3.5.0 |
| GHSA-r9jc-w898-3fv6: quadratic cost for repeated slashes in the request path | CVE-2026-128074 | Moderate in the database, Low on the vendor tab | `nuxt` 4.6.0 before 4.6.4 | not listed |
| GHSA-hf59-9xwc-2g4p: colliding island props share one `/__nuxt_island` path | CVE-2026-128076 | Low | `nuxt` 4.4.6 before 4.6.4, and 3.21.6 onward | affected, no fix |
| GHSA-x2wv-5868-p7v2: webpack and rspack dev servers serve built source to DNS-rebinding pages | CVE-2026-128072 | Low | `@nuxt/webpack-builder`, `@nuxt/rspack-builder` 4.0.0 before 4.6.4, and 3.x | affected, no fix |
| [GHSA-p4h3-4h99-9665](https://github.com/nuxt/nuxt/security/advisories/GHSA-p4h3-4h99-9665): Vite server builder wildcard redirect rules can redirect to another origin | none when read | Low 3.1 | `@nuxt/vite-server` 4.6.0 before 4.6.4 | not affected |

**Route-rule bypasses.** Two are incomplete fixes of earlier advisories. CVE-2026-128077 says the 4.6.3 fix for GHSA-9v7c-q64q-vv33 "covered dot segments but not this form". A request to `//x/admin` renders the page at `/admin` while server checks keyed on `/admin` do not run. CVE-2026-128071 says a request that spells a slash as `%2F` renders a catch-all page without the rules for the path it resolves to. The skipped rules include `redirect`, `headers` and `appMiddleware`.

**Error details.** For a failed server-side `$fetch`, the client receives the requested URL with its query string and the upstream error body. A token in that URL reaches anyone who can make the request fail.

**Dev server.** CVE-2026-128070 and CVE-2026-128072 affect `nuxt dev` only. The first lets anyone who can reach the dev server read files under a parent directory. The advisory says running `npm install` once in the home directory creates the lockfile that triggers it. Nuxt credits Anthropic for reporting CVE-2026-128072.

**Nuxt 3.** The newest 3.x release on npm is 3.21.11, published 2026-08-05. The `3x` dist-tag points at it. No 3.x release carries these fixes.

**Dist-tags.** On 2026-11-17 `latest` was 4.6.4 and the `4x` tag was 4.6.3. An install pinned to the `4x` tag gets the affected version.

## Am I affected?

```bash
npm ls nuxt @nuxt/nitro-server @nuxt/vite-server @nuxt/schema @nuxt/webpack-builder @nuxt/rspack-builder
grep -rn "routeRules" nuxt.config.* 2>/dev/null                    # rules that guard paths
ls server/middleware 2>/dev/null                                    # path checks on event.path
ls app/pages/**/\[...*\].vue pages/**/\[...*\].vue 2>/dev/null      # catch-all page routes
ls ~/package-lock.json ~/pnpm-lock.yaml ~/yarn.lock ~/pnpm-workspace.yaml 2>/dev/null   # stray files above the project
```

- `nuxt` 4.x before 4.6.4: affected by all eight, subject to each advisory's conditions.
- `nuxt` 3.x at any version: affected by the encoded-slash bypass, the error-detail leak, the island collision and the webpack or rspack dev-server issue. From 3.5.0 the parent-directory dev-server issue applies too. No upgrade on the 3.x line fixes them.
- Access control that lives only in `routeRules` or in `server/middleware` path checks is the exposed part. Checks inside the page's own data handlers still run.

## If you are affected

- Upgrade to `nuxt` 4.6.4. Check `npm ls @nuxt/nitro-server` afterwards, because the fix for CVE-2026-128077 is in that package.
- On Nuxt 3, plan the move to Nuxt 4. Until then, reject page requests whose path contains `%2f` in a server middleware, and catch server-side `$fetch` errors and rethrow them with `createError` and a generic message.
- Rotate tokens that server-side requests carried in a URL, if those requests could fail in production.
- The dev port may have been reachable from an untrusted network while a stray lockfile sat above the project. In that case the advisory says to treat files in that parent directory as exposed and rotate SSH keys and cloud tokens.
- See [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

- Enforce authorization in the server handler that returns the data, not only in a route rule or a path prefix check.
- Do not put tokens in URLs of server-side requests. Send them in headers.
- Do not expose `nuxt dev` beyond localhost. See [agent sandboxing](../prevention/agent-sandboxing.md) for running dev servers that an agent starts.
- Track the end-of-life date of the framework major you deploy.

## Sources

- [Nuxt advisory tab](https://github.com/nuxt/nuxt/security/advisories): eight rows dated 2026-11-02, read 2026-11-17.
- [GHSA-r99w-jh2x-3mg9](https://github.com/nuxt/nuxt/security/advisories/GHSA-r99w-jh2x-3mg9): range, score, workaround, Nuxt 3 not affected.
- [GHSA-96x6-fvhx-49hg](https://github.com/nuxt/nuxt/security/advisories/GHSA-96x6-fvhx-49hg): range, score, the Nuxt 3 end-of-life sentence.
- [GHSA-p4h3-4h99-9665](https://github.com/nuxt/nuxt/security/advisories/GHSA-p4h3-4h99-9665): the advisory with no CVE.
- [GitHub Advisory Database, reviewed npm listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+sort%3Apublished-desc): seven rows, CVE ids and database dates.
- OSV records for the seven GHSA ids with a CVE (`api.osv.dev/v1/vulns/<id>`): ranges, patch and workaround text for the advisories whose vendor pages were not opened.
- npm registry `time` and `dist-tags` for `nuxt`, read 2026-11-17: 4.6.4 on 2026-11-02, 3.21.11 on 2026-08-05, `4x` at 4.6.3.
