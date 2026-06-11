---
id: 2026-05-nextjs-react-security-release
title: "Next.js + React May 2026 security release — 13 CVEs, including unauth SSRF (CVE-2026-44578)"
date_disclosed: 2026-05-06
last_updated: 2026-06-11
severity: high
status: patched
ecosystems: [npm, javascript]
tools_affected: [nextjs, react, vercel, netlify, cloudflare-pages, any-react-project]
tags: [cve, ssrf, dos, middleware-bypass, xss, cache-poisoning, react-server-components, nextjs]
---

## TL;DR
On **2026-05-06 → 05-07**, Vercel published Next.js **15.5.18** and **16.2.6**, rolling up **13 advisories** — 7 high, 4 moderate, 2 low, including one upstream React Server Components vuln (**CVE-2026-23870**). The headline issue is **CVE-2026-44578 (CVSS 8.6)**, an **unauthenticated SSRF** in the WebSocket upgrade handler that lets a single crafted HTTP request make the Next.js process issue arbitrary internal GETs and read the response — including cloud metadata. Affects all **self-hosted** Next.js from 13.4.13 onward (Vercel-hosted apps are not vulnerable). Shodan estimates ~**79,000 internet-exposed vulnerable instances**. Cloudflare and Netlify shipped WAF/adapter mitigations on 05-06 before most teams patched.

## What happened
A coordinated security release covering 13 advisories across:

- Denial of service (server-side memory exhaustion)
- Middleware / proxy bypass (auth bypass via crafted `.rsc` and segment-prefetch URLs)
- Server-side request forgery (the WebSocket SSRF — see below)
- Cache poisoning
- Cross-site scripting

### The headline: CVE-2026-44578 — WebSocket-upgrade SSRF
The Next.js built-in Node.js server handled WebSocket upgrade requests in a way that let an unauthenticated attacker, with a single crafted HTTP `Upgrade` request, cause the server to issue an internal `GET` to any host reachable on port 80 and return the body. That includes:

- AWS / GCP / Azure **instance metadata endpoints** (`169.254.169.254`, `metadata.google.internal`) — IAM credentials, project-id, instance attributes.
- Internal admin panels, databases, message brokers, and other plaintext services bound to private interfaces.
- Cluster service-mesh endpoints.

**Self-hosted Next.js only** (anyone running `next start` behind a reverse proxy, in a container, or on a VM). **Vercel-hosted apps are not affected** because the Vercel edge layer terminates Upgrade requests differently.

### The headline #2: CVE-2026-23870 — React Server Components DoS
`react-server-dom` (RSC runtime in React 19.x) accepts a crafted POST to a Server Function endpoint that forces the deserializer into pathological CPU work. Any framework using React 19 RSC is in scope. Patched in `react-server-dom-{parcel,webpack,turbopack} == 19.0.6 | 19.1.7 | 19.2.6`.

### Middleware-bypass cluster
Three of the high-severity advisories are middleware-bypass variants where specially crafted `.rsc` URLs and segment-prefetch paths slipped past Next.js middleware-based authentication, returning protected content without enforcement. Anyone using Next.js middleware as an auth gate (a common pattern in vibe-coded auth stacks layered over NextAuth.js / Supabase / Clerk) needs to upgrade.

### CVE-2026-23869 — App Router Server Action CPU exhaustion (CVSS 7.5)
Unauthenticated requests with a crafted payload sent to any **App Router Server Action endpoint** trigger quadratic CPU work in the Next.js request parser. A single attacker can pin a Node.js process to 100% CPU, causing denial of service for all concurrent requests. Affects all Next.js 13.x–16.x with App Router Server Actions enabled. Patched in the same **15.5.18 / 16.2.6** rollup.

### CVE-2026-23864 — React + Next.js Server Components memory/CPU DoS
Distinct from CVE-2026-23870: a crafted multi-part RSC streaming request causes the `react-server-dom` runtime to allocate unbounded memory before the streaming buffer is drained, producing out-of-memory kills on constrained containers. Akamai catalogued this as the memory-exhaustion companion to the CPU-exhaustion class. Patched in `react-server-dom-*` alongside the May 2026 release.

**Net effect**: three independent DoS surfaces — CPU exhaustion via Server Actions (CVE-2026-23869), unbounded memory in the RSC streamer (CVE-2026-23864), and pathological RSC deserializer CPU (CVE-2026-23870). Any internet-exposed App Router endpoint is potentially unauthenticated-DoS-able until the May 2026 patch is applied.

## Am I affected?

```bash
# Project version
grep -E '"next":' package.json
npm ls next 2>/dev/null | head -3

# Self-hosted or Vercel?
# If you deploy to Vercel: CVE-2026-44578 doesn't apply, but the middleware bypasses and React RSC DoS still do.
# If you deploy to Netlify / Cloudflare Pages / self-host: WAF mitigations help short-term, but patch.

# Quick check of exposed Node Next.js servers (self-hosted)
# Adapt to your infra: are any Next.js processes reachable from the public internet?
ss -tlnp 2>/dev/null | grep -E ':3000|:8080'
```

### Affected & patched versions

| Item | Affected | Patched |
|---|---|---|
| Next.js (CVE-2026-44578) | `13.4.13+, 14.x, 15.x < 15.5.16, 16.0.0 < 16.2.5` (self-hosted only) | **`15.5.16`** or **`16.2.5`** for SSRF; **`15.5.18`** / **`16.2.6`** for the full 13-CVE rollup |
| React Server Components (CVE-2026-23870) | React 19.x with `react-server-dom-*` | `19.0.6`, `19.1.7`, `19.2.6` |

## If you are affected
1. **Upgrade Next.js to 15.5.18 or 16.2.6.** Do not stop at 15.5.16 / 16.2.5 — there are 11 other issues in the same rollup.
2. **Upgrade React Server Components** to the matching patched version of `react-server-dom-{parcel,webpack,turbopack}`.
3. **Self-hosted on Cloudflare or Netlify?** WAF / adapter mitigations were live from 2026-05-06; they reduce SSRF exposure but are not a substitute for the package upgrade.
4. If a self-hosted Next.js was internet-exposed before patching, audit cloud audit logs for unexpected metadata-endpoint reads (e.g., AWS `GetInstanceProfile` from your own instances) and rotate any IAM roles those instances held.
5. Audit any auth that depends on Next.js middleware — confirm protected routes returned 401/403 for crafted `.rsc` / `_rsc` URLs after the patch.

## Why this matters for vibe coders
Next.js is the de facto front-end for Lovable, Bolt, v0, and a large fraction of Cursor / Claude Code projects. If you've vibe-coded a Next.js app and shipped it to a custom Node host (Render, Fly, Railway, a VM, Docker) the SSRF is **directly exploitable from the public internet with no authentication**. Middleware-based auth bypasses also hit vibe-coded stacks hard: it's the most common pattern an AI agent will reach for when you ask "make this route logged-in-only."

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — defense-in-depth even when your framework is patched
→ Pin a Dependabot / Renovate auto-merge policy for `next` and `react` security releases.
→ Don't rely on middleware as your sole auth boundary; enforce per-route in the handler too.
→ Block instance-metadata egress at the network layer (cloud-side IMDSv2 + hop-limit 1, Kubernetes NetworkPolicy denying `169.254.169.254`).
→ If self-hosting, put a real reverse proxy (NGINX, Caddy, or a CDN with WAF) in front; don't expose `next start` directly.

## Sources
- [Vercel — Next.js May 2026 security release](https://vercel.com/changelog/next-js-may-2026-security-release)
- [Vercel — Summary of CVE-2026-23869](https://vercel.com/changelog/summary-of-cve-2026-23869)
- [Netlify — Next.js & React security release (May 2026)](https://www.netlify.com/changelog/2026-05-08-react-nextjs-security-vulnerabilities/)
- [Cloudflare — WAF and framework adapter mitigations for React and Next.js vulnerabilities](https://developers.cloudflare.com/changelog/post/2026-05-06-react-nextjs-vulnerabilities/)
- [Akamai — CVE-2026-23864: React and Next.js Denial of Service via Memory Exhaustion](https://www.akamai.com/blog/security-research/cve-2026-23864-react-nextjs-denial-of-service)
- [Hadrian — Next.js WebSocket SSRF: Unauthenticated Access to Internal Resources (CVE-2026-44578)](https://hadrian.io/blog/next-js-websocket-ssrf-unauthenticated-access-to-internal-resources-cve-2026-44578-2)
- [GitHub Advisory — Denial of Service with Server Components (GHSA-q4gf-8mx6-v5v3)](https://github.com/vercel/next.js/security/advisories/GHSA-q4gf-8mx6-v5v3)
- [Cybersecurity News — Multiple Critical Vulnerabilities Patched in Next.js and React Server Components](https://cybersecuritynews.com/next-js-react-server-vulnerabilities/)
- [Endor Labs — Critical Remote Code Execution Vulnerabilities in React and Next.js](https://www.endorlabs.com/learn/critical-remote-code-execution-rce-vulnerabilities-in-react-and-next-js)
- [DevOps Daily — Next.js 16.2.6 and 15.5.18 Ship 13 Security Fixes](https://devops-daily.com/posts/nextjs-16-2-6-15-5-18-security-release)
