---
id: 2026-07-nextjs-july-security-release
title: "Next.js July 2026 Security Release — 9 CVEs (4 high, 5 medium): middleware bypass, SSRF, cache confusion (patch to 16.2.11 / 15.5.21)"
date_disclosed: 2026-07-20
last_updated: 2026-07-21
severity: high
status: patched
ecosystems: [npm, javascript]
tools_affected: [nextjs, vercel, any-nextjs-project]
tags: [cve, ssrf, middleware-bypass, cache-poisoning, dos, nextjs, security-release-program]
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

## Sources
- [Next.js — Security Release and Our Next Patch Release (announcement, 2026-07-13)](https://nextjs.org/blog/next-security-release-program)
- [Next.js — July 2026 Security Release (full CVE list, published 2026-07-20)](https://nextjs.org/blog/july-2026-security-release)
- [GitHub Security Advisories — vercel/next.js (GHSA-6gpp-xcg3-4w24, GHSA-p9j2-gv94-2wf4, GHSA-89xv-2m56-2m9x, GHSA-m99w-x7hq-7vfj, GHSA-4c39-4ccg-62r3, GHSA-68g3-v927-f742, GHSA-4633-3j49-mh5q, GHSA-q8wf-6r8g-63ch, GHSA-955p-x3mx-jcvp)](https://github.com/vercel/next.js/security/advisories)
- [Cybersecurity News — Next.js Launches Monthly Security Release Program as First Update Patches 9 Vulnerabilities](https://cybersecuritynews.com/next-js-monthly-security-updates/)
- [GBHackers — Next.js Announces July Security Release to Fix 4 High-Severity and 5 Medium Flaws](https://gbhackers.com/next-js-announces-july-security-release/)
