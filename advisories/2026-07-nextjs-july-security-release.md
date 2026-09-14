---
id: 2026-07-nextjs-july-security-release
title: "Next.js July + August 2026 Security Releases — 9 CVEs in July, then two critical unauthenticated RCEs in August (AVIF, Windows CVE-2026-75604)"
date_disclosed: 2026-07-20
last_updated: 2026-09-14
severity: critical
status: patched
ecosystems: [npm, javascript]
tools_affected: [nextjs, vercel, any-nextjs-project, self-hosted-nextjs, windows-hosted-nextjs, sharp, libheif, astro]
tags: [cve, ssrf, middleware-bypass, cache-poisoning, dos, nextjs, security-release-program, rce, image-optimization, avif, path-traversal, windows]
---

## TL;DR
Vercel shipped the **first entry in Next.js's new formal Security Release Program**: **9 CVEs** (4 high, 5 medium) fixed in **Next.js 16.2.11** (Active LTS) and **15.5.21** (Maintenance LTS), published 2026-07-20 (one day later than the originally announced 2026-07-20 target — the post itself was updated to say "now expected on July 21"). The headline issue, **CVE-2026-64642**, is a **middleware/proxy bypass** for App Router apps built with **Turbopack and a single locale** — any auth or security check your middleware performs is silently skipped. Also in the batch: an unauthenticated **SSRF/open-redirect via attacker-controlled rewrite/redirect destination hostnames** (CVE-2026-64645), an **SSRF in Server Actions on custom servers** (CVE-2026-64649), a **Server Actions CPU-exhaustion DoS** (CVE-2026-64641), and four cache-confusion / disclosure issues. Upgrade now — this is the first release under Vercel's new pre-announced monthly cadence (see [advisories/2026-05-nextjs-react-security-release.md](2026-05-nextjs-react-security-release.md) for the May 2026 predecessor rollup).

## What happened
On 2026-07-13, Vercel announced it was moving Next.js to a formal, pre-announced monthly security release program — publishing severity counts (and only severity counts) a week ahead of the actual patch, so defenders get lead time without handing attackers a target list before a fix exists. The first release under this program landed 2026-07-20/21, fixing 9 issues:

### CVE-2026-64642 — Middleware/Proxy bypass (Turbopack + single locale) — High
App Router applications built with **Turbopack** and exactly one entry in `config.i18n.locales` bypass middleware entirely. Any authentication or authorization check implemented in Next.js middleware is skipped for affected requests — the same "auth relies solely on middleware" failure mode this repo has flagged repeatedly (see the May 2026 rollup's `CVE-2026-44574` middleware bypass, and the original `CVE-2025-29927` middleware-auth-bypass class).

### CVE-2026-64645 — SSRF/Open Redirect via rewrite/redirect destination hostname — High
A `rewrites()` or `redirects()` rule that builds its external destination hostname from request-controlled input can be redirected to an **arbitrary hostname**, regardless of the rule's intended hostname suffix. For `rewrites()` this is server-side request forgery (the Next.js server itself makes the outbound request); for `redirects()` it's an open redirect against the end user.

### CVE-2026-64649 — SSRF in Server Actions on custom servers — High
When a Server Action forwards or redirects a request on a **custom server** deployment, an attacker who controls Host-associated request headers can steer the server's outbound request to an attacker-chosen host.

### CVE-2026-64641 — Server Actions CPU-exhaustion DoS — High
Crafted requests against any App Router app with at least one Server Action cause excessive CPU usage that blocks the whole process from serving further requests — an unauthenticated denial-of-service, similar in shape to the CVE-2026-23869 Server Action DoS from the May 2026 rollup but a distinct code path.

### Medium-severity cluster
- **CVE-2026-64644** — Image Optimization API DoS via malicious remotely-hosted SVGs (only applies to self-hosted deployments with remote image loading configured — not on by default).
- **CVE-2026-64646** — Unbounded Server Action payload causes memory exhaustion in the Edge runtime.
- **CVE-2026-64643** — Server Action / `use cache` endpoint IDs can be globally disclosed to an unauthenticated caller, aiding reconnaissance for a broader attack chain.
- **CVE-2026-64648** and **CVE-2026-64647** — Two variants of the same bug: a server-side `fetch(new Request(init), aDifferentInit)` call can return a **cached response body from a different request** to the same URL, either for requests with different bodies (`-64648`) or specifically when the body contains invalid UTF-8 byte sequences (`-64647`) — a cache-confusion class that could leak one user's response to another.

## Am I affected?
```bash
grep -E '"next":' package.json
npm ls next 2>/dev/null | head -3
```
- **Using Turbopack (`next build --turbo` / `next dev --turbo`) with App Router and exactly one `i18n.locales` entry?** You're exposed to the middleware bypass (CVE-2026-64642) until patched — treat any middleware-enforced auth as currently bypassable.
- **Using `rewrites()`/`redirects()` with a destination hostname built from request data (headers, query params, path segments)?** Check for CVE-2026-64645 exposure.
- **Running on a custom server (not `next start` alone) with Server Actions that forward/redirect requests?** Check CVE-2026-64649.
- Any App Router app with Server Actions enabled is potentially exposed to the CPU/memory DoS pair (CVE-2026-64641, CVE-2026-64646) regardless of hosting provider.

## If you are affected
1. **Upgrade immediately**: `npm install next@15.5.21` (15.5.x LTS) or `npm install next@16.2.11` (16.2.x LTS). The fixes are also in `16.3.0-canary.92` / `16.3.0-preview.7` ahead of the 16.3.0 stable release.
2. If you use Turbopack + single-locale i18n, re-verify that middleware-enforced auth actually returns 401/403 for protected routes after upgrading.
3. Audit `rewrites()`/`redirects()` configs for any destination hostname derived from request-controlled input; hardcode destinations where possible instead of deriving them dynamically.
4. No IOCs to check — these are unauthenticated logic/DoS bugs, not an active campaign; there's no indication of in-the-wild exploitation prior to this disclosure.

## Why this matters for vibe coders
Next.js is the default framework behind a large fraction of Lovable, Bolt, v0, and Cursor/Claude Code-generated web apps. This is also the **first release under Vercel's new monthly security-release cadence** — expect a similar batch roughly every month going forward, each pre-announced a week ahead with only a severity count, then followed by the actual CVE details on release day. Bookmark [nextjs.org/blog](https://nextjs.org/blog) or subscribe to Vercel's changelog if you run Next.js in production; treat the pre-announcement as your signal to plan an upgrade window, not as something to act on before the patch exists.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — defense-in-depth even when your framework is patched.
→ Don't rely on middleware as your sole auth boundary; enforce authorization again in the route handler / Server Action itself.
→ Pin a Dependabot / Renovate auto-merge policy for `next` security releases now that they're on a predictable monthly cadence.
→ Avoid building `rewrites()`/`redirects()` destination hostnames from any request-controlled value (headers, query params, path segments).

## Update — 2026-08-21: Vercel pre-announces an **August 26** release fixing one **critical** vulnerability

On **2026-08-20**, Vercel published the second pre-announcement under the same Security Release Program described above. Everything it discloses (fetched directly from the Next.js blog):

- **Release date:** 2026-08-26.
- **Scope:** **one critical-severity vulnerability.** No CVE id, no affected-version range, and no technical detail are disclosed yet — that is the program working as designed, since publishing a target list before a patch exists helps attackers more than defenders.
- **Versions that will ship:** **16.3.3** and **15.5.24**, published alongside the full advisory.

**What to do before 2026-08-26.** There is nothing to patch yet and no way to tell whether your app is in scope, so the useful work is preparation rather than mitigation: confirm which Next.js line each of your apps is on, make sure you can cut an upgrade to 16.3.3 / 15.5.24 the same day rather than waiting for a sprint boundary, and note that this is the **first critical-rated** Next.js issue since the [May 2026 13-CVE rollup](2026-05-nextjs-react-security-release.md) — the July batch topped out at high. Given this repo's tracked history of Next.js middleware-auth bypasses (CVE-2025-29927, CVE-2026-44574, CVE-2026-64642 above), an app whose authorization lives *only* in middleware is worth reviewing now regardless of what the 26th turns out to bring.

This entry will be updated with the actual CVE detail once the release publishes.

## Update — 2026-09-10: the August release shipped a day early (2026-08-25) with **two** critical unauthenticated RCEs, not one — patch self-hosted apps to 16.3.3 / 15.5.24

The pre-announced release was pulled forward to **2026-08-25** after Vercel "identified an additional critical severity vulnerability in one of our upstream dependencies" (its own words on the release post). Both issues are **unauthenticated remote code execution**, both fixed in **Next.js 16.3.3** (Active LTS) and **15.5.24** (Maintenance LTS), and the severity of this advisory is bumped from high to **critical** accordingly.

### Unauthenticated RCE in the Image Optimization API via AVIF — Critical, CVSS 4.0 **9.5**, no CVE
**GHSA-2xp9-vwfh-vxw4** (Next.js) tracking **GHSA-g89c-p67h-r497** in **libheif**, the HEIF/AVIF decoder that `sharp` uses under Next.js's `next/image` optimizer. When the optimizer processes an attacker-controlled AVIF image, a flaw in libheif can lead to code execution on the server. Affects **Next.js ≥ 10.0.0 < 15.5.24** and **all 16.x < 16.3.3**. The patched releases **disable AVIF optimization entirely** until the upstream fix propagates — so if you rely on AVIF output, expect a format change, not just a security fix. The Hacker News' coverage narrows exposure to deployments that explicitly added `image/avif` to the `images.formats` configuration and credits rootxharsh (finder) and KarimPwnz (coordinator), with Vercel's changelog crediting the Hacktron team; the GHSA itself lists no credits.

### Unauthenticated RCE on Windows-hosted servers — Critical, CVSS 3.1 **9.0**, **CVE-2026-75604**
**GHSA-p293-qw3h-jr36**. Applications that use **both the Pages Router and App Router without Cache Components**, served from a **Windows filesystem**, are vulnerable to a path-traversal (CWE-22) issue that escalates to remote code execution. Affects **≥ 13.4 < 15.5.24** and **≥ 16.0 < 16.3.3**. Linux and macOS are not affected. Vercel's advisory: *"There is no known workaround for affected windows-hosted applications. You should upgrade immediately if your server is hosted on Windows."* Credited to evolutionstorm and B0RI.

**Vercel-hosted apps are protected from both without upgrading** (per The Hacker News' summary of the release post); everyone self-hosting — Docker, Node on a VM, a Windows IIS box, the "deploy anywhere" template a vibe-coding platform emitted — has to ship the version bump.

```bash
# Which line are you on, and are you below the fix?
node -e 'console.log(require("next/package.json").version)'
grep -n 'avif' next.config.* 2>/dev/null                       # AVIF exposure check
node -e 'console.log(process.platform)'                        # win32 = the CVE-2026-75604 case
npm install next@15.5.24   # 15.x line
npm install next@16.3.3    # 16.x line
```

Two program notes. First, this is the second consecutive release where the pre-announcement's count was **lower than what shipped** (July pre-announced 9 and shipped 9; August pre-announced 1 critical and shipped 2) — treat the pre-announced count as a floor. Second, the AVIF issue is the first Next.js critical whose root cause is a transitive native dependency (`sharp` → `libheif`), which `npm audit` on `next` alone would not have flagged; it is the same "the framework's image pipeline is a C library" exposure that the [React2Shell / RSC cluster](2025-12-react2shell-rce.md) is not, and it will recur.

## Update — 2026-09-14: it recurred — the same libheif bug is a CVSS 9.8 unauthenticated RCE in **Astro < 7.2.8**

**GHSA-26w7-cxv4-gfx2** (Astro, published 2026-08-27, reviewed into the advisory database 2026-09-08, no CVE): "Remote code execution through AVIF image optimization." The root cause is the identical upstream **libheif GHSA-g89c-p67h-r497**, reached through Astro's **default Sharp image service** when it processes untrusted AVIF input. CVSS 3.1 **9.8** (network, no privileges, no interaction; CWE-125/CWE-787). Affects **all Astro < 7.2.8**; fixed in **7.2.8** (npm 2026-08-26), which requires **`sharp` ≥ 0.35.4**. Astro is the other framework vibe-coding platforms emit for content sites, and it fixed the bug one day *after* Next.js's 08-25 release without a matching announcement of its own.

The generalisable point is the one flagged above: a native-dependency bug fans out across every framework that bundles the same library. When one framework ships a `sharp`/`libheif` fix, search the advisory database for the upstream id, not the framework name — and check anything else with an image-optimisation step (Nuxt Image, Gatsby, SvelteKit's `@sveltejs/enhanced-img`, and any hand-rolled `sharp` route) against `sharp` ≥ 0.35.4.

```bash
node -e 'console.log(require("astro/package.json").version)' 2>/dev/null   # need >= 7.2.8
npm ls sharp 2>/dev/null                                                    # need >= 0.35.4 everywhere it resolves
```

## Sources
- [Next.js — Security Release and Our Next Patch Release (announcement, 2026-07-13)](https://nextjs.org/blog/next-security-release-program)
- [Next.js — July 2026 Security Release (full CVE list, published 2026-07-20)](https://nextjs.org/blog/july-2026-security-release)
- [GitHub Security Advisories — vercel/next.js (GHSA-6gpp-xcg3-4w24, GHSA-p9j2-gv94-2wf4, GHSA-89xv-2m56-2m9x, GHSA-m99w-x7hq-7vfj, GHSA-4c39-4ccg-62r3, GHSA-68g3-v927-f742, GHSA-4633-3j49-mh5q, GHSA-q8wf-6r8g-63ch, GHSA-955p-x3mx-jcvp)](https://github.com/vercel/next.js/security/advisories)
- [Cybersecurity News — Next.js Launches Monthly Security Release Program as First Update Patches 9 Vulnerabilities](https://cybersecuritynews.com/next-js-monthly-security-updates/)
- [GBHackers — Next.js Announces July Security Release to Fix 4 High-Severity and 5 Medium Flaws](https://gbhackers.com/next-js-announces-july-security-release/)
- [Next.js — Upcoming Next.js August Security Release (pre-announcement, published 2026-08-20)](https://nextjs.org/blog/upcoming-nextjs-security-release-august-2026) — added 2026-08-21: the 2026-08-26 date, the single critical-severity count, and the 16.3.3 / 15.5.24 target versions.
- [Next.js — August 2026 Security Release (published 2026-08-25)](https://nextjs.org/blog/august-2026-security-release) — fetched 2026-09-10 for the 2026-09-10 update: the pulled-forward date, both vulnerabilities, the AVIF-disabled mitigation, "no known workaround" for Windows, the 16.3.3 / 15.5.24 versions.
- [GitHub Security Advisory — GHSA-p293-qw3h-jr36: Unauthenticated Remote Code Execution on windows-hosted servers (CVE-2026-75604)](https://github.com/vercel/next.js/security/advisories/GHSA-p293-qw3h-jr36) — fetched 2026-09-10: CVSS 9.0, CWE-22, affected ranges ≥13.4 <15.5.24 and ≥16.0 <16.3.3, reporter credits, published 2026-08-25.
- [GitHub Security Advisory — GHSA-2xp9-vwfh-vxw4: Unauthenticated Remote Code Execution in Image Optimization API when AVIF files are used](https://github.com/vercel/next.js/security/advisories/GHSA-2xp9-vwfh-vxw4) — fetched 2026-09-10: CVSS 4.0 9.5, no CVE, affected ranges ≥10.0.0 <15.5.24 and <16.3.3, libheif GHSA-g89c-p67h-r497 reference.
- [The Hacker News — Next.js Patches Critical AVIF and Windows Flaws Enabling Unauthenticated RCE](https://thehackernews.com/2026/08/nextjs-patches-critical-avif-and.html) — fetched 2026-09-10; published 2026-08-27: the `image/avif`-in-`formats` exposure condition, researcher credits, and the "Vercel-hosted applications are protected … and require no upgrade" statement.
- [GitHub Advisory Database — GHSA-26w7-cxv4-gfx2: Astro remote code execution through AVIF image optimization](https://github.com/advisories/GHSA-26w7-cxv4-gfx2) — fetched 2026-09-14 for the 2026-09-14 update: CVSS 9.8, affected < 7.2.8 / fixed 7.2.8, `sharp` ≥ 0.35.4 requirement, upstream libheif GHSA-g89c-p67h-r497 reference, published 2026-08-27 / reviewed 2026-09-08.
- [npm registry — `astro`](https://registry.npmjs.org/astro) — queried 2026-09-14 (`npm view astro time`): 7.2.7 published 2026-08-25, 7.2.8 published 2026-08-26.
