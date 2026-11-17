---
id: 2026-10-sveltekit-october-29-eight-advisories-server-secrets-in-client-bundle-fixed-3-1-1-2-70-4
title: "SvelteKit: eight advisories on 2026-10-29, server secrets in the client bundle (CVE-2026-128118); fixed in 3.1.1, part-fixed in 2.70.4"
date_disclosed: 2026-10-29
last_updated: 2026-11-17
severity: high
status: patched
ecosystems: [npm, sveltekit, svelte, vercel, cloudflare, node]
tools_affected: ["@sveltejs/kit 3.0.0 through 3.1.0", "@sveltejs/kit before 2.70.4", "@sveltejs/kit 2.42.0 and later on the 2.x line with experimental remote functions", "@sveltejs/adapter-node 5.5.7 and 6.0.x before 6.0.1", "@sveltejs/adapter-vercel before 6.3.5 and 7.0.x before 7.0.2", "@sveltejs/adapter-static before 3.0.11 and 4.0.x before 4.0.1", "@sveltejs/adapter-cloudflare 4.7.0 before 7.2.10 and 8.0.x before 8.0.2"]
tags: [cve, ghsa, sveltekit, secret-exposure, client-bundle, remote-functions, denial-of-service, prerender, adapter, web-framework, older-line-release-in-range]
---

## TL;DR
SvelteKit 3.0.0 through 3.1.0 could put server-only imports made through `src/params.js` into the client bundle, "potentially exposing secrets" ([GHSA-m9j8-jcmv-hp69](https://github.com/sveltejs/kit/security/advisories/GHSA-m9j8-jcmv-hp69), CVE-2026-128118, High 7.5). It is one of eight advisories the SvelteKit team published on 2026-10-29. Upgrade `@sveltejs/kit` to 3.1.1 or later and the adapters to the versions in the table. On the 2.x line, 2.70.4 fixes two of the eight, and two remote-function advisories list no 2.x fix. If a 3.0.0 to 3.1.0 build imported server-only modules through `src/params.js`, rotate the secrets it could reach.

## What happened

The SvelteKit advisory tab shows eight advisories dated 2026-10-29, read 2026-11-17. The GitHub Advisory Database published them on 2026-11-13 and 2026-11-16, with CVE ids CVE-2026-128116 through CVE-2026-128123. The table takes ranges from the database records and scores from the vendor pages that were opened.

| Advisory | CVE | Severity | Package and affected range | Fixed in |
|---|---|---|---|---|
| [GHSA-m9j8-jcmv-hp69](https://github.com/sveltejs/kit/security/advisories/GHSA-m9j8-jcmv-hp69): server-only import guard could fail, secrets in the client bundle | CVE-2026-128118 | High 7.5 | `@sveltejs/kit` 3.0.0 through 3.1.0 | 3.1.1 |
| [GHSA-3r8g-jcqq-3p5j](https://github.com/sveltejs/kit/security/advisories/GHSA-3r8g-jcqq-3p5j): denial of service while parsing remote function form data | CVE-2026-128120 | High 7.5 | `@sveltejs/kit` 2.42.0 through 3.1.0 | 3.1.1 |
| [GHSA-6cf5-gc4q-fm3x](https://github.com/sveltejs/kit/security/advisories/GHSA-6cf5-gc4q-fm3x): private `query.batch` functions could share a batch | CVE-2026-128119 | Moderate 5.9 | `@sveltejs/kit` 2.60.1 through 3.1.0 | 3.1.1 |
| GHSA-rqp5-r3wg-vg35: protocol-relative module import with `router.resolution: 'server'` | CVE-2026-128116 | Moderate | `@sveltejs/kit` before 2.70.4, and 3.0.0 through 3.1.0 | 2.70.4, 3.1.1 |
| GHSA-mw6w-2fmv-pvw3: `reroute` on a malformed pathname crashes adapter-node | CVE-2026-128117 | Moderate | `@sveltejs/kit` before 2.70.4, and 3.0.0 through 3.1.0 | 2.70.4, 3.1.1 |
| GHSA-rqw3-x7hx-mm3p: adapter-node crashes when proxying certain requests through `fetch` | CVE-2026-128123 | Moderate | `@sveltejs/adapter-node` 5.5.7, and 6.0.x before 6.0.1 | 5.5.8, 6.0.1 |
| GHSA-jf9x-2fg2-hx4w: prerendered paths read as regular expressions in Vercel route config | CVE-2026-128121 | Moderate | `@sveltejs/adapter-vercel` before 6.3.5 and 7.0.x before 7.0.2, `@sveltejs/adapter-static` before 3.0.11 and 4.0.x before 4.0.1 | 6.3.5, 7.0.2, 3.0.11, 4.0.1 |
| GHSA-5wg4-q3ww-283h: prerendered redirect paths can add rules to the Cloudflare `_redirects` file | CVE-2026-128122 | Moderate | `@sveltejs/adapter-cloudflare` 4.7.0 before 7.2.10, and 8.0.x before 8.0.2 | 7.2.10, 8.0.2 |

**The secrets advisory.** The vendor page says the leak "could only occur when those server-only imports were made through `src/params.js`". It lists no workaround. SvelteKit 2.x is outside its range.

**Remote functions.** The two remote-function advisories apply only to apps that set the experimental remote functions flag. The denial-of-service one needs the `form`, `query` or `command` remote functions. The batch one needs non-exported `query.batch` functions.

**The 2.x line.** The npm registry shows 3.1.1 and the 3.x-line adapters published on 2026-10-29, and 2.70.4 with the 2.x-line adapters on 2026-11-05. The `version-2` dist-tag points at 2.70.4. The vendor pages for CVE-2026-128120 and CVE-2026-128119 list 3.1.1 as the only patched version, and their ranges include 2.70.4. No source names a 2.x backport for either, so treat 2.70.4 as affected by both when remote functions are on.

**Prerender advisories.** Both need an attacker who can influence a link that the prerender crawl follows, such as user-submitted content included in the build.

## Am I affected?

```bash
npm ls @sveltejs/kit @sveltejs/adapter-node @sveltejs/adapter-vercel @sveltejs/adapter-static @sveltejs/adapter-cloudflare
ls src/params.js src/params.ts 2>/dev/null                       # the file named in CVE-2026-128118
grep -rn "experimental" svelte.config.* 2>/dev/null             # the experimental remote functions flag
grep -rn "query.batch" src 2>/dev/null
grep -rn "resolution" svelte.config.* 2>/dev/null               # router.resolution: 'server'
```

- `@sveltejs/kit` 3.0.0 through 3.1.0 with server-only imports reached from `src/params.js`: affected by the secrets advisory.
- Any 2.x version from 2.42.0 with remote functions enabled, including 2.70.4: inside the range of CVE-2026-128120.
- A lockfile written before 2026-10-29 on the 3.x line, or before 2026-11-05 on the 2.x line, predates the fixes.

## If you are affected

- Upgrade to `@sveltejs/kit` 3.1.1 or later. `latest` was 3.2.1 on 2026-11-17. Upgrade the adapter you deploy with to the version in the table.
- On 2.x, upgrade to 2.70.4. If you use remote functions, move to 3.1.1 or turn the experimental flag off.
- For CVE-2026-128118, search the built client output for values of your private environment variables. Rotate any secret you find and any secret the leaked module could read.
- Rebuild and redeploy prerendered sites after upgrading the adapter, because the route and redirect files are generated at build time.
- See [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Search the built client bundle for the values of server secrets in CI and fail the build on a match. See [credential hygiene](../prevention/credential-hygiene.md).
- Treat experimental framework flags as unsupported surface in production.
- Read the SvelteKit advisory tab on release days. These advisories were on the tab 15 days before the database listed them.

## Sources

- [SvelteKit advisory tab](https://github.com/sveltejs/kit/security/advisories): eight rows dated 2026-10-29, read 2026-11-17.
- [GHSA-m9j8-jcmv-hp69](https://github.com/sveltejs/kit/security/advisories/GHSA-m9j8-jcmv-hp69): range, score and description of the secrets advisory.
- [GHSA-3r8g-jcqq-3p5j](https://github.com/sveltejs/kit/security/advisories/GHSA-3r8g-jcqq-3p5j): range 2.42.0 through 3.1.0, patched 3.1.1 only.
- [GHSA-6cf5-gc4q-fm3x](https://github.com/sveltejs/kit/security/advisories/GHSA-6cf5-gc4q-fm3x): range 2.60.1 through 3.1.0, patched 3.1.1 only.
- [GitHub Advisory Database, reviewed npm listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Anpm+sort%3Apublished-desc): the eight rows, their CVE ids and database dates.
- OSV records for the eight GHSA ids (`api.osv.dev/v1/vulns/<id>`): per-package ranges and fixed versions for the five advisories whose vendor pages were not opened.
- npm registry `time` and `dist-tags` for `@sveltejs/kit` and the four adapters, read 2026-11-17: publish dates of the fixed versions.
