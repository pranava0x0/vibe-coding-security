---
id: 2026-10-nextjs-react-october-14-out-of-band-use-cache-rsc-rce-svg-sharp-server-actions-dos
title: "Next.js 16.4.1 and 15.5.28, React 19.3.1: unauthenticated RCE through `use cache` typed arrays and SVG image optimization, Server Actions DoS (2026-10-14)"
date_disclosed: 2026-10-14
last_updated: 2026-10-15
severity: critical
status: patched
ecosystems: [npm, javascript, nextjs, react, sharp]
tools_affected: ["Next.js 16.0.0 – 16.4.0 → 16.4.1", "Next.js 10.0.0 – 15.5.27 → 15.5.28 (SVG Image Optimization RCE)", "Next.js 13.0.0 – 15.5.27 → 15.5.28 (Server Actions DoS)", "react-server-dom-webpack / -turbopack / -parcel 19.0.0 – 19.0.8, 19.1.0 – 19.1.9, 19.2.0 – 19.2.8, 19.3.0 → 19.0.9, 19.1.10, 19.2.9, 19.3.1", "App Router apps with Cache Components and a `use cache` function returning typed arrays", "Image Optimization with `dangerouslyAllowSVG` or `next/og` on the Node.js runtime, on glibc Linux, with sharp < 0.35.5", "App Router apps with at least one Server Action"]
tags: [cve, nextjs, react, react-server-components, rce, use-cache, cache-components, image-optimization, sharp, librsvg, server-actions, dos, out-of-band-release, upstream-dependency, partial-cve-coverage]
---

## TL;DR
Next.js shipped an out-of-band release on 2026-10-14, `16.4.1` and `15.5.28`, for three advisories: an unauthenticated remote code execution in App Router apps that have Cache Components on and a `use cache` function returning more than one typed array (GHSA-673q-mjm6-r5xr, CVSS 4.0 9.5, Next.js 16.0.0 through 16.4.0, no workaround, no CVE), an unauthenticated remote code execution in the Image Optimization API when SVG input reaches `sharp` on glibc Linux (GHSA-2464-fhr4-w9xw, 9.5, Next.js 10.0.0 through 15.5.27 and 16.0.0 through 16.4.0, carrying the upstream librsvg id CVE-2026-96889), and a Server Actions denial of service where crafted requests pin one process at full CPU (GHSA-p3m5-59mp-jv5r, 8.2, 13.0.0 through 15.5.27 and 16.0.0 through 16.4.0). The `use cache` bug is React's: React published GHSA-xqc2-xf4c-x3h3 (9.5) and a Server Functions DoS (GHSA-h3gv-c5rc-p453, 8.2) the same day for `react-server-dom-webpack`, `-turbopack` and `-parcel`, fixed in 19.0.9, 19.1.10, 19.2.9 and 19.3.1. Upgrade both, then run `npm ls sharp`: `next@15.5.28` still accepts `sharp` 0.34.x, which carries the SVG bug.

## What happened

Next.js's September security release ([the 2026-09-30 file](2026-09-nextjs-september-2026-security-release-seven-advisories.md)) had pre-announced one critical and one high fix and then postponed them for an upstream dependency. The postponed fixes arrived on 2026-10-14 as an out-of-band release. npm shows `next@15.5.28` published at 17:36 UTC and `next@16.4.1` at 17:43 UTC; the React packages went out about an hour earlier, `react-server-dom-webpack@19.3.1` at 16:49 UTC with 19.2.9, 19.0.9 and 19.1.10 within the following six minutes.

The three Next.js advisories, published by eps1lon on the vendor tab:

1. **`use cache` RCE, GHSA-673q-mjm6-r5xr, CVSS 4.0 9.5, no CVE.** "A vulnerability in applications using App router with Cache Component can lead to remote code execution." Exploitation requires a `use cache` function that returns multiple typed arrays. Affected 16.0.0 through 16.4.0, patched 16.4.1. The advisory says there is no known workaround and recommends upgrading "even if the application has no similar functions". The upstream is React's GHSA-xqc2-xf4c-x3h3, "Unauthenticated Remote Code Execution in React Server Components", which says the issue "only affects extremely rare cases where responses transport multiple typed arrays and an attacker-controlled value", affects `react-server-dom-parcel`, `-turbopack` and `-webpack` at 19.0.0 through 19.0.8, 19.1.0 through 19.1.9, 19.2.0 through 19.2.8 and 19.3.0, and is fixed in 19.0.9, 19.1.10, 19.2.9 and 19.3.1. Apps whose React code does not use a server, or that use no framework or bundler plugin supporting React Server Components, are not affected. Neither advisory lists a reporter.

2. **SVG Image Optimization RCE, GHSA-2464-fhr4-w9xw, CVSS 4.0 9.5, CVE-2026-96889.** "A memory-related vulnerability in an upstream library used for Image Optimization can allow possible remote code execution when Next.js runs on glibc-based Linux." Affected 10.0.0 through 15.5.27 and 16.0.0 through 16.4.0, patched 15.5.28 and 16.4.1, credited to randomguy6407 and rafabd1. The workaround is to make sure the `sharp` Next.js uses is 0.35.5 or later. The CVE id belongs to Red Hat's record for librsvg (published 2026-09-23, a use-after-free when nested XML inclusions carry duplicate entity declarations, CVSS 3.1 7.8 with a local vector and user interaction), which sharp fixed in `0.35.5` on 2026-09-27; the September file already carried that fix under the OG-image route. The Next.js tab is where the id gains a network vector and a 9.5. The Hacker News adds, from the advisory and the researcher, that SVG is not optimized by default and needs `dangerouslyAllowSVG`, that `next/og` on the Node.js runtime is also a path, and that Netlify said its platform does not run the image-optimizer code path. Those three statements are the outlet's.

3. **Server Actions DoS, GHSA-p3m5-59mp-jv5r, CVSS 4.0 8.2, no CVE.** Crafted requests to an App Router app with at least one Server Action cause excessive CPU use that blocks further requests in the same process. Affected 13.0.0 through 15.5.27 and 16.0.0 through 16.4.0, patched 15.5.28 and 16.4.1, "no workaround exists besides upgrading". Pages Router apps and apps without Server Actions are not affected. React's matching advisory, GHSA-h3gv-c5rc-p453 "Denial of Service in Server Functions" (8.2, no CVE), lists the same three packages and the same patched versions; its affected-versions list ends at 19.0.8, 19.1.9, 19.2.8 and 19.3.0 while its Impact paragraph says 19.0.7, 19.1.8 and 19.2.7. Treat the list as authoritative and upgrade past both.

Two things to carry. First, the registry pins: `next@16.4.1` declares `optionalDependencies.sharp` as `^0.35.5` while `next@15.5.28` declares `^0.34.3 || ^0.35.5`, so a 15.x upgrade over an existing install can keep a 0.34.x `sharp` in place and leave the SVG path open. Second, as of 2026-10-15 the `use cache` and Server Actions advisories have no CVE, and The Hacker News reports they are absent from the feed `npm audit` reads, so a clean audit does not mean a fixed app. No exploitation had been reported as of 2026-10-15.

## Am I affected?

```bash
# Next.js version and which router you run
npm ls next 2>/dev/null | head -3
ls app pages 2>/dev/null          # app/ present = App Router

# RCE 1: Cache Components plus a `use cache` function returning typed arrays
grep -nE 'cacheComponents|useCache' next.config.* 2>/dev/null
grep -rln --include='*.ts' --include='*.tsx' --include='*.js' "'use cache'\|\"use cache\"" app src 2>/dev/null

# RCE 2: SVG reaches sharp
grep -nE 'dangerouslyAllowSVG' next.config.* 2>/dev/null
grep -rln 'next/og' app src 2>/dev/null
npm ls sharp 2>/dev/null          # 0.34.x anywhere in the tree = still vulnerable

# React packages behind the framework
npm ls react-server-dom-webpack react-server-dom-turbopack react-server-dom-parcel 2>/dev/null

# DoS: any Server Action
grep -rln "'use server'\|\"use server\"" app src 2>/dev/null
```

Affected if `next` is 16.0.0 through 16.4.0, or 10.0.0 through 15.5.27 with SVG input or Server Actions, or any `react-server-dom-*` is below 19.0.9, 19.1.10, 19.2.9 or 19.3.1. A `sharp` at 0.34.x after upgrading to 15.5.28 keeps the SVG path open.

## If you are affected

Upgrade to `next@16.4.1` or `next@15.5.28`, rebuild and redeploy; the fix is in the build output, not only in the running process. On 15.x, update `sharp` to 0.35.5 or later explicitly if `npm ls sharp` still shows 0.34.x. If an upgrade has to wait, block the SVG loader as the advisory describes (`sharp.block({ operation: ["VipsForeignLoadSvg"] })` per The Hacker News, or set `sharp` to 0.35.5), and know that the `use cache` and Server Actions bugs have no interim mitigation. For a self-hosted App Router app that may have served crafted traffic, follow [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) and [auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md).

## Prevention

- Treat the Next.js vendor tab and the React tab as the advisory source, not `npm audit`; two of this release's three advisories had no CVE on the day and were invisible to scanners.
- Pin `sharp` explicitly in apps that accept image uploads or generate OG images, and check `npm ls sharp` after every framework upgrade.
- Keep Cache Components and `dangerouslyAllowSVG` off unless the app needs them. See [supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Sources
- [GHSA-673q-mjm6-r5xr, Next.js vendor tab](https://github.com/vercel/next.js/security/advisories/GHSA-673q-mjm6-r5xr) — `use cache` RCE, 9.5, affected and patched versions, no workaround.
- [GHSA-2464-fhr4-w9xw, Next.js vendor tab](https://github.com/vercel/next.js/security/advisories/GHSA-2464-fhr4-w9xw) — SVG Image Optimization RCE, CVE-2026-96889, sharp 0.35.5 workaround, credits.
- [GHSA-p3m5-59mp-jv5r, Next.js vendor tab](https://github.com/vercel/next.js/security/advisories/GHSA-p3m5-59mp-jv5r) — Server Actions DoS, 8.2, versions.
- [GHSA-xqc2-xf4c-x3h3, React vendor tab](https://github.com/facebook/react/security/advisories/GHSA-xqc2-xf4c-x3h3) — RSC RCE, the three packages and their ranges, "extremely rare cases" wording.
- [GHSA-h3gv-c5rc-p453, React vendor tab](https://github.com/facebook/react/security/advisories/GHSA-h3gv-c5rc-p453) — Server Functions DoS, the two differing ranges.
- [CVE-2026-96889, CVE Services record (Red Hat CNA)](https://cveawg.mitre.org/api/cve/CVE-2026-96889) — librsvg use-after-free, 2026-09-23, 7.8 local vector.
- [The Hacker News, 2026-10-15](https://thehackernews.com/2026/10/nextjs-ships-out-of-band-patch-for-two.html) — `dangerouslyAllowSVG` and `next/og` paths, the `sharp.block` interim step, the 15.5.28 `sharp` range, the `npm audit` gap, Netlify's statement, no exploitation as of 2026-10-15.
- [Next.js September 2026 release file](2026-09-nextjs-september-2026-security-release-seven-advisories.md) — the postponed critical and high this release closes, and the sharp 0.35.5 fix date.
- npm registry `time` for `next` and `react-server-dom-webpack`, fetched 2026-10-15 — publish timestamps; `npm view next@<v> optionalDependencies.sharp` — the sharp pins.
