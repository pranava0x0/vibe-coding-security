---
id: 2026-01-sveltespill-sveltekit-vercel-cache-deception
title: "SvelteSpill — SvelteKit + Vercel cache deception exposes authenticated responses (CVE-2026-27118, Jan 2026)"
date_disclosed: 2026-01-20
last_updated: 2026-07-04
severity: high
status: patched
ecosystems: [npm, svelte, vercel]
tools_affected: ["@sveltejs/adapter-vercel", "SvelteKit on Vercel"]
tags: [cache-deception, svelte, sveltekit, vercel, session-hijack, frontend]
---

## TL;DR

**CVE-2026-27118** ("SvelteSpill", GHSA-9pq4-5hcf-288c) — SvelteKit's Vercel adapter accepted an unrestricted `__pathname` query parameter used for internal routing. Combined with Vercel's aggressive immutable-asset caching for `/_app/immutable/` paths, an attacker could craft a URL that gets a protected, authenticated API response cached as if it were a public static asset — leaking session tokens and private data to any other visitor who requests that cached URL. Fixed automatically for all users by Vercel on 2026-02-19.

## What happened

Aikido Security's AI-assisted pentesting tooling discovered on **2026-01-20** that `@sveltejs/adapter-vercel` accepted a `__pathname` query parameter intended purely for internal routing/rewriting, without restricting where it could point ([Aikido Security](https://www.aikido.dev/blog/sveltespill-cache-deception-sveltekit-vercel)). Vercel caches everything under `/_app/immutable/` extremely aggressively (these paths are normally content-hashed, genuinely immutable JS/CSS bundles). By requesting a URL like `https://example.vercel.app/_app/immutable/x?__pathname=/api/session`, an attacker could get SvelteKit to internally rewrite the request to a protected endpoint (e.g., a session/API route) while Vercel's edge cache treated the *response* as belonging to the public, immutable `/_app/immutable/` path and cached it — meaning the next visitor who hit that cached URL received someone else's authenticated response, including session tokens ([Cyberpress](https://cyberpress.org/cache-deception-vulnerability-found-in-sveltekit-and-vercel-combo-exposes-user-data-to-attackers/)).

Any SvelteKit application deployed on Vercel that uses cookie-based authentication was vulnerable to this class of cache deception — the flaw sits in the framework/platform integration, not in application code, so vulnerable apps had no code-level way to detect or opt out short of the vendor fix.

Reported to Vercel on **2026-01-21**; Vercel shipped a fix for **all users automatically** on **2026-02-19** by forcing `/_app/immutable/` paths to 404 when a `__pathname` override is present and stripping the parameter — no manual application patch was required ([Aikido Security](https://www.aikido.dev/blog/sveltespill-cache-deception-sveltekit-vercel)). A related denial-of-service issue was tracked separately as GHSA-vrhm-gvg7-fpcf.

## Am I affected?

This was fixed platform-side by Vercel for every hosted SvelteKit application — there is no per-project version check. If you deployed a SvelteKit app on Vercel with the `@sveltejs/adapter-vercel` adapter before **2026-02-19** and used cookie-based sessions, you were exposed during that window.

```bash
# Sanity check: confirm you're on a current adapter-vercel release
npm ls @sveltejs/adapter-vercel
```

## If you are affected

1. No application-level patch is required — the fix was deployed by Vercel to the platform. Confirm your deployment predates 2026-02-19 was not actively exploited by reviewing edge/CDN cache logs for unusual `__pathname` query parameters on `/_app/immutable/` paths during the exposure window.
2. If you find evidence of exploitation (unexpected session reuse, reports of account takeover with no other explanation), rotate session secrets and force re-authentication for all users. See [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).
3. If you self-host SvelteKit with a similar CDN/cache layer in front of it (not Vercel), audit whether your CDN's caching rules can be tricked by rewrite/routing query parameters into caching authenticated responses under a "public" path.

## Prevention

- When deploying behind any CDN, never let a caching rule's "is this path public/immutable" decision depend on a request-controllable query parameter — route-rewrite parameters and cache-eligibility decisions should be independently validated.
- Keep framework adapters (`@sveltejs/adapter-vercel` and equivalents) current; platform-side fixes like this one still require you to be aware the exposure window existed. See [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- See [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) for broader framework/platform-integration hardening guidance.

## Sources

- [Aikido Security — "SvelteSpill: Critical Cache Deception Bug in SvelteKit + Vercel"](https://www.aikido.dev/blog/sveltespill-cache-deception-sveltekit-vercel) — original disclosure, root cause, timeline, fix confirmation.
- [Cyberpress — "Cache Deception Vulnerability Found in SvelteKit and Vercel Combo Exposes User Data to Attackers"](https://cyberpress.org/cache-deception-vulnerability-found-in-sveltekit-and-vercel-combo-exposes-user-data-to-attackers/) — independent confirmation of exploitation mechanics and impact.
- [GitHub Security Advisory — GHSA-9pq4-5hcf-288c](https://github.com/sveltejs/kit/security/advisories/GHSA-9pq4-5hcf-288c) — canonical advisory record.
- [NVD — CVE-2026-27118](https://nvd.nist.gov/vuln/detail/CVE-2026-27118) — official CVE record.
