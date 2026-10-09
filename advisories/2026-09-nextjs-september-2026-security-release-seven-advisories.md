---
id: 2026-09-nextjs-september-2026-security-release-seven-advisories
title: "Next.js September 2026 security release (2026-09-30, 16.3.8 / 15.5.27): seven advisories — Image Optimization SSRF through an allow-listed remote pattern (CVE-2026-94483, High 8.3), two SSG/ISR cache-poisoning bugs, a Draft Mode `use cache` leak, a root-param cache leak, a `dynamicParams` bypass on OG-image routes, and a `next dev` MCP endpoint any website the developer visits can read (CVE-2026-94486) — while the pre-announced *critical* and one *high* were postponed for an upstream dependency; sharp 0.35.5 separately fixes a librsvg RCE (CVE-2026-96889, 8.9)"
date_disclosed: 2026-09-30
last_updated: 2026-10-09
severity: high
status: patched
ecosystems: [npm, javascript, nextjs, react, sharp]
tools_affected: ["Next.js 16.0.0 – 16.3.7 (Active LTS) → 16.3.8", "Next.js 15.0.0 – 15.5.26 (Maintenance LTS) → 15.5.27 (cache-poisoning fixes only)", "self-hosted Pages Router SSG/ISR apps", "App Router apps with images.remotePatterns", "apps with Cache Components / experimental.useCache and Draft Mode", "webpack-built App Router apps with opengraph-image / twitter-image routes", "any developer running `next dev` on Next.js 16", "sharp < 0.35.5 (librsvg)"]
tags: [cve, nextjs, security-release-program, ssrf, cache-poisoning, information-disclosure, draft-mode, mcp, next-dev, image-optimization, sharp, librsvg, upstream-dependency, postponed-fix]
---

## TL;DR

Vercel shipped its scheduled **September 2026 security release** on **2026-09-30** — **Next.js 16.3.8** (Active LTS) and **15.5.27** (Maintenance LTS), both on npm at 16:07–16:19 UTC — with **seven advisories: one High, five Medium, one Low**. That is two fewer than the nine (one critical, two high) pre-announced on 09-23: the release post says "a fix for one critical vulnerability and one high severity vulnerability was postponed due to upstream dependency delays," and no id, range or date has been published for either. The High is **CVE-2026-94483 (CVSS 8.3)** — if your `next.config` has `images.remotePatterns`, an attacker-controlled URL that matches a pattern can make the Image Optimization endpoint fetch private addresses. Two Medium bugs let a single unauthenticated request poison the shared SSG/ISR cache so every later visitor gets the wrong page (self-hosted only for one; Vercel-hosted apps are not affected by it). Two more Medium bugs leak content across `use cache` keys — one of them **serves unpublished Draft Mode content to anonymous visitors** and can persist it into the prerendered page. The Low, **CVE-2026-94486**, is the one this audience should read twice: **`next dev` on Next.js 16 exposes a Model Context Protocol endpoint that does not check where a request came from**, so any website a developer visits while the dev server is up can read the project's path on disk, source snippets from error overlays, the route inventory and dev logs. Production never serves it. Separately, the image stack's native dependency **sharp** published **CVE-2026-96889 (High 8.9)** the same day: a use-after-free in bundled **librsvg** that is "possible remote code execution on glibc-based Linux," fixed in **sharp 0.35.5** (npm 2026-09-27). Upgrade `next` and `sharp`, and keep watching the Next.js blog for the postponed critical.

## What happened

**Timeline.** 2026-09-22: out-of-band 16.3.6 / 15.5.26 for the [Satori `next/og` RCE](2026-09-nextjs-og-imageresponse-satori-svg-rce.md). 09-23: pre-announcement of a 09-30 scheduled release for "nine vulnerabilities: one critical, two high, five medium, one low" as 16.3.7 / 15.5.27. 09-29 09:04 UTC: `next@16.3.7` published (a regular release). 09-30 16:07 / 16:19 UTC: `16.3.8` and `15.5.27` published; the seven vendor advisories on `vercel/next.js` are dated 09-30 and the CVE records (CNA GitHub) 10-02. The release post's authors are Josh Story, Karim Rahal and Sebastian Silbermann; every advisory credits **eps1lon** (Sebastian Silbermann, a Next.js core maintainer) as finder — this batch is the vendor auditing itself.

**The seven, in the release post's order:**

| Id | Title (vendor) | Severity | Affected → fixed | Who is exposed |
|---|---|---|---|---|
| **CVE-2026-94483** / GHSA-cjq9-62q9-8jv4 | Server-Side Request Forgery in Image Optimization | **High 8.3** | 16.0.0 – 16.3.7 → **16.3.8** | "An attacker-controlled, allow-listed remote URL can lead to SSRF (for example to private IP ranges) during Image Optimization. If no `images.remotePatterns` are configured, your application is not affected." |
| CVE-2026-94543 / GHSA-4jqv-mc3x-m676 | Cache poisoning of SSG and ISR pages in self-hosted Next.js applications | Medium 6.3 | 15.0.0+ → 15.5.27; 16.0.0+ → 16.3.8 | Pages Router with SSG/ISR, **self-hosted**: "a page's cache entry replaced with content from a different route … until the entry is revalidated. Applications deployed on Vercel are not affected." |
| CVE-2026-94484 / GHSA-mcj8-r9mp-w47p | Cache poisoning in SSG/ISR rendering leads to cross-user content substitution and persistent denial of service | Medium 6.3 | 15.0.0+ → 15.5.27; 16.0.0+ → 16.3.8 | Apps with "a root-level catch-all page together with statically generated or ISR routes … poisoned by a single unauthenticated crafted request." |
| **CVE-2026-94485** / GHSA-f87g-xv8r-7p7x | Information disclosure in App Router metadata image routes via `dynamicParams` bypass | Medium 6.3 | 16.0.0+ → 16.3.8 | **webpack** builds only: `opengraph-image` / `twitter-image` ignore `dynamicParams`, so segments "deliberately excluded from `generateStaticParams()`" can be requested. Turbopack builds are not affected. |
| **CVE-2026-103004** / GHSA-h694-7cp9-m8p3 | Cache leak across root param values in nested `use cache` functions | Medium 6.3 | 16.3.0 – 16.3.7 → 16.3.8 | Cache Components: an outer `'use cache'` function calling an inner one that reads a root param is keyed without that param, so "content produced for one root param value can be served for a different value." Not attacker-selectable. |
| **CVE-2026-94544** / GHSA-3w37-wq28-93x7 | Pending `use cache` fill can leak Draft Mode content into regular responses and persisted pages | Medium 6.3 | 16.3.0 – 16.3.7 → 16.3.8 | Cache Components or `experimental.useCache` **plus Draft Mode previews**: "a regular request that overlaps an editor's Draft Mode request receives unpublished content without any authentication; if that request prerenders a page, the unpublished content can be persisted … and served to all later visitors until the page is revalidated." |
| **CVE-2026-94486** / GHSA-39w2-rjm5-chcv | Information disclosure in the development server's Model Context Protocol endpoint | Low 2.3 | 16.0.0 – 16.3.7 → 16.3.8 | `next dev` only: the MCP endpoint "does not verify which website a request originates from, allowing a malicious website visited by the developer to read … the project's location on disk, source code snippets from error reports, the route inventory, and development logs." |

**What was postponed.** The 09-23 pre-announcement counted nine; the 09-30 post shipped seven and says the critical and one high were "postponed due to upstream dependency delays." Nothing further is published: no id, no component, no date. This corpus's own rule after August's `libheif` critical and September's Satori critical is not to guess the dependency. What *is* on the record the same day is adjacent: **sharp** — the native image library Next.js's Image Optimization uses — published **GHSA-wq5f-xc86-pv6w / CVE-2026-96889 (High, CVSS 4.0 8.9, CWE-416)** on 09-30: a memory bug in the bundled **librsvg** that can lead to "possible remote code execution (RCE) on glibc-based Linux" under certain runtime conditions, fixed in **sharp ≥ 0.35.5** (ships librsvg 2.63.2; npm 2026-09-27). The advisory's workarounds are a PIE-compiled Node binary or `sharp.block({ operation: ["VipsForeignLoadSvg"] })`. Whether that is the postponed High, or unrelated, is not stated anywhere this sweep read; treat it as its own upgrade.

**Why the dev-server MCP bug matters more than its 2.3.** Next.js 16's dev server ships an MCP endpoint so coding agents can introspect the running app. The advisory describes the classic "localhost service with no origin check" shape — the same class as the [Cline hub CSWSH](2026-08-agent-framework-mcp-cve-batch.md), the [mcp-chrome-bridge native server](2026-08-agent-framework-mcp-cve-batch.md) and the [DBHub DNS-rebinding](2026-08-agent-framework-mcp-cve-batch.md) entries — but on a port that is open on every Next.js 16 developer's laptop for most of the working day. The score is low because the data is development data; the lesson is that **agent-facing local endpoints are now a standard component of frontend tooling** and need the same origin discipline as any other local server. Netlify's 10-04 changelog notes the metadata-image bug still applies to webpack builds on its platform, that its Image CDN takes the SSRF out of band for its customers, and recommends `@netlify/plugin-nextjs` 5.16.1 plus a redeploy.

**A record-keeping note for anyone reading the CVE JSON.** The CNA record for **CVE-2026-94485** carries the *title* and GHSA reference of the `dynamicParams` bug but its *description* is the `next dev` MCP text (identical to CVE-2026-94486's); NVD's copy inherits the error. The vendor advisory GHSA-f87g-xv8r-7p7x, the release post and the title all agree on the pairing used in the table above. Scanners keyed on description text will mis-describe 94485.

## Am I affected?

```bash
# Version
npm ls next 2>/dev/null | grep ' next@'      # fixed: 16.3.8 (16.x) or 15.5.27 (15.x)
npm view next time --json | grep -E '"(16\.3\.8|15\.5\.27)"'   # both 2026-09-30

# Which of the seven apply to you
grep -n "remotePatterns" next.config.* 2>/dev/null          # CVE-2026-94483 (SSRF) only if set
grep -rln "draftMode\|useCache\|cacheComponents" --include=*.{js,ts,tsx,mjs} . | head   # 94544 / 103004
ls app/**/opengraph-image* app/**/twitter-image* 2>/dev/null   # 94485 (webpack builds only)
ls pages 2>/dev/null | head -1 && echo "Pages Router present: check 94543/94484 if self-hosted SSG/ISR"

# sharp (bundled by Next.js image optimization; also direct installs)
npm ls sharp 2>/dev/null | grep ' sharp@'    # fixed: 0.35.5+
```

Vercel-hosted apps are not affected by CVE-2026-94543; Netlify says its Image CDN removes the SSRF for its customers. Everyone else self-hosting is the target population for the cache bugs.

## If you are affected

1. **Upgrade to `next@16.3.8` or `next@15.5.27` and redeploy.** 16.3.7 is *not* a security release.
2. **Upgrade `sharp` to ≥ 0.35.5** wherever it is installed directly, and rebuild any Docker image that pins an older Next.js (the bundled copy moves with `next`).
3. If you self-host SSG/ISR pages: **revalidate or purge the page cache** after upgrading — a poisoned entry persists until revalidation.
4. If you use Draft Mode with Cache Components: check whether any prerendered output since 16.3.0 contains unpublished content (CVE-2026-94544 can persist it); regenerate affected pages.
5. For the SSRF: review every `images.remotePatterns` entry for wildcard hosts or hosts that redirect; tighten to exact hostnames and paths.
6. Developers: restart `next dev` after upgrading; until then do not browse untrusted sites with a Next.js 16 dev server running.
7. **Watch for the postponed critical.** Subscribe to `vercel/next.js` advisories or the Next.js blog; this corpus will update this file when it ships.

## Update 2026-10-09: the postponed fixes have a date

On 2026-10-08 Vercel pre-announced an out-of-band security update for **Wednesday 2026-10-14**. The post says it "will address three vulnerabilities in upstream dependencies: two **Critical** and one **High**" and that "two of these fixes were postponed from the September security release due to upstream coordination." No ids, components or affected versions are published yet; the advisories ship with the update. Status here stays `patched` for the seven September advisories; the October items get their own entry when they land.

## Prevention

- This is the fourth Next.js security release in six weeks (08-25 criticals, 09-22 Satori, 09-30 scheduled, plus the pending one). Keep `next` **unpinned within a minor** and on the LTS line the Security Release Program targets; see [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- Local agent endpoints — MCP servers in dev tooling, IDE bridges, Hub dashboards — need origin/host validation like any other localhost service; see [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).
- Cache poisoning via a single crafted request is a shared-cache design problem; put a CDN with its own cache key normalisation in front of self-hosted ISR, and alert on `revalidate` storms. [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) covers the purge-and-verify steps.

## Sources

- [Next.js — Upcoming Next.js Security Update for Upstream Vulnerabilities](https://nextjs.org/blog/upcoming-nextjs-security-update-october-2026) — 2026-10-08 (Josh Story, Karim Rahal, Sebastian Silbermann): out-of-band update planned for 2026-10-14, three upstream-dependency vulnerabilities (two Critical, one High), two postponed from September.
- [Next.js — September 2026 Security Release](https://nextjs.org/blog/september-2026-security-release) — 2026-09-30 (Josh Story, Karim Rahal, Sebastian Silbermann): the seven advisories with CVE/GHSA ids, severities, exclusions, the 16.3.8 / 15.5.27 versions, and the "one critical vulnerability and one high severity vulnerability was postponed due to upstream dependency delays" statement. Fetched 2026-10-04.
- [vercel/next.js — GHSA-cjq9-62q9-8jv4](https://github.com/vercel/next.js/security/advisories/GHSA-cjq9-62q9-8jv4) (CVE-2026-94483, High 8.3, `remotePatterns` precondition), [GHSA-4jqv-mc3x-m676](https://github.com/vercel/next.js/security/advisories/GHSA-4jqv-mc3x-m676) (CVE-2026-94543, self-hosted Pages Router SSG/ISR, Vercel not affected), [GHSA-mcj8-r9mp-w47p](https://github.com/vercel/next.js/security/advisories/GHSA-mcj8-r9mp-w47p) (CVE-2026-94484, root catch-all + SSG/ISR), [GHSA-f87g-xv8r-7p7x](https://github.com/vercel/next.js/security/advisories/GHSA-f87g-xv8r-7p7x) (CVE-2026-94485, webpack-only `dynamicParams` bypass), [GHSA-h694-7cp9-m8p3](https://github.com/vercel/next.js/security/advisories/GHSA-h694-7cp9-m8p3) (CVE-2026-103004, nested `use cache` root-param key, fixed 16.3.8), [GHSA-3w37-wq28-93x7](https://github.com/vercel/next.js/security/advisories/GHSA-3w37-wq28-93x7) (CVE-2026-94544, Draft Mode pending-fill leak, vector `AV:N/AC:H/AT:P/PR:N/UI:N/VC:L`), [GHSA-39w2-rjm5-chcv](https://github.com/vercel/next.js/security/advisories/GHSA-39w2-rjm5-chcv) (CVE-2026-94486, Low 2.3, `next dev` MCP endpoint, `UI:P`) — all published 2026-09-30, all credit eps1lon. Fetched 2026-10-04. [vercel/next.js advisory tab](https://github.com/vercel/next.js/security/advisories?state=published) — the seven 09-30 entries beside the 09-22 and 08-25 criticals.
- CVE records (CNA GitHub, published 2026-10-02): [CVE-2026-94485](https://cveawg.mitre.org/api/cve/CVE-2026-94485) and [CVE-2026-94486](https://cveawg.mitre.org/api/cve/CVE-2026-94486) — affected `>= 16.0.0, < 16.3.8`, CVSS 4.0 6.3 / 2.3, both referencing commit `2d9f50a4` and the v16.3.8 tag; 94485's description duplicates 94486's text (noted above). [NVD API keyword window 10-01 → 10-04](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=Next.js&pubStartDate=2026-10-01T00:00:00.000&pubEndDate=2026-10-04T23:59:59.999) — CVE-2026-94483 (8.3), 94484, 94485, 94486, 94543, 94544, 103004 with the ranges quoted. Queried 2026-10-04.
- [lovell/sharp — GHSA-wq5f-xc86-pv6w: Vulnerability in librsvg dependency CVE-2026-96889](https://github.com/lovell/sharp/security/advisories/GHSA-wq5f-xc86-pv6w) — published 2026-09-30: High 8.9, CWE-416, "possible remote code execution (RCE) on glibc-based Linux," fixed sharp ≥ 0.35.5 (librsvg 2.63.2), the PIE and `sharp.block` workarounds, upstream reference GNOME/librsvg work item 1241. Fetched 2026-10-04.
- [Netlify changelog — Next.js and React security vulnerabilities (2026-09-30)](https://www.netlify.com/changelog/2026-09-30-nextjs-react-security-vulnerabilities.md) — independent platform note (dated 10-04): the seven ids and severities, Image CDN taking the SSRF out of band, webpack builds still exposed to the metadata-image bug, `@netlify/plugin-nextjs` 5.16.1, delete vulnerable branch deploys. Fetched 2026-10-04.
- npm registry `time` for `next` (queried 2026-10-04): 16.3.6 2026-09-22, **16.3.7 2026-09-29**, **16.3.8 2026-09-30 16:07 UTC**, 15.5.26 2026-09-22, **15.5.27 2026-09-30 16:19 UTC**; `sharp` 0.35.4 2026-08-26, **0.35.5 2026-09-27**.
- Related in this corpus: [Satori `next/og` RCE (09-22)](2026-09-nextjs-og-imageresponse-satori-svg-rce.md) — carries the 09-23 pre-announcement; [July 2026 release](2026-07-nextjs-july-security-release.md); [May 2026 release](2026-05-nextjs-react-security-release.md).
