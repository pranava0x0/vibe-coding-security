---
id: 2026-07-nuxt-security-release-server-island-rce
title: "Nuxt July 2026 security release — 7 advisories including server-side RCE via Server Island prop injection and a critical DevTools RCE"
date_disclosed: 2026-07-27
last_updated: 2026-07-27
severity: high
status: patched
ecosystems: [npm, javascript, vue]
tools_affected: ["nuxt", "@nuxt/devtools", "@nuxt/ui"]
tags: [rce, server-islands, template-injection, auth-bypass, devtools, dos, cache-poisoning]
---

## TL;DR

Nuxt shipped a coordinated **7-advisory security release** on **2026-07-27** (patched in **Nuxt 4.5.1 / 3.21.10**, plus `@nuxt/devtools` 3.3.1), headlined by **GHSA-9473-5f9j-94wq** — a **server-side remote code execution** in Nuxt's "Server Island" feature: if `vue.runtimeCompiler: true` is enabled and a server island component forwards attacker-controlled props into Vue's dynamic component resolution (`<component :is>`, `resolveDynamicComponent`, `h()` — a common pattern in `@nuxt/ui`-based apps), an attacker can inject a `template` key that Vue's runtime compiler executes on the server. The batch also includes a **critical, dev-only DevTools RCE** (GHSA-279x-mwfv-vcqv) and a **route-rule authorization bypass** (GHSA-hxvh-4h3w-prp9). Upgrade with `npx nuxt upgrade --dedupe`.

## What happened

Nuxt's own security post ([nuxt.com/blog/v4-5-security](https://nuxt.com/blog/v4-5-security), published 2026-07-27) discloses seven advisories together:

| Advisory | Severity | Summary |
|---|---|---|
| **GHSA-9473-5f9j-94wq** | High (CVSS 8.1) | Server-side RCE: attacker-supplied `template` prop reaches Vue's runtime compiler in the Nitro server process. Requires `vue.runtimeCompiler: true` (off by default) plus a server island forwarding props into dynamic component resolution. |
| **GHSA-48hr-524c-v5w3** | Moderate (CVSS 4.8) | Unauthorized component instantiation: a plain string prop via `/__nuxt_island/` can instantiate any globally-registered Vue component or native HTML element — **does not require the runtime compiler**, so it's reachable in more configurations than the RCE above. Information disclosure / unintended rendering, not code execution. |
| **GHSA-hxvh-4h3w-prp9** | High | Route-rule authorization bypass. |
| **GHSA-hxcr-hm88-mpq6 / GHSA-9pgf-384g-p7mv** | High | Server-component denial of service. |
| **GHSA-wm8w-6qjm-cv43** | High | Cross-user payload disclosure (Nuxt ≥4.4.0) — Nuxt's own remediation advice includes purging any CDN/edge cache that may hold a leaked `_payload.json`. |
| **GHSA-7c4v-fwgw-9rf7** | Low | Dev-server path disclosure. |
| **GHSA-279x-mwfv-vcqv** | Critical (dev-tooling only) | Remote code execution in `@nuxt/devtools`, all versions — fixed in `@nuxt/devtools` 3.3.1. |

No CVE numbers have been assigned to any of these as of this sweep; all are tracked by GHSA ID only. Vercel received advance notice and deployed platform-wide WAF mitigations for apps hosted on Vercel ahead of public disclosure ([Vercel changelog](https://vercel.com/changelog/nuxt-july-2026-security-advisory)); Netlify also published guidance for its users ([Netlify changelog](https://www.netlify.com/changelog/2026-07-27-nuxt-security-vulnerabilities/)). Socket.dev additionally released free backport patches for older Nuxt release lines that won't receive an official fix.

## Am I affected?

```bash
grep -E '"nuxt":' package.json
npm ls nuxt @nuxt/devtools 2>/dev/null
```

- **Nuxt 3.4.0–3.21.9 or 4.0.0–4.5.0**, with `vue.runtimeCompiler: true` set and any server island/component forwarding untrusted props into dynamic component resolution (especially via `@nuxt/ui`'s polymorphic `as`/`asChild` props): exposed to the RCE (GHSA-9473-5f9j-94wq).
- Same version range regardless of the runtime-compiler setting: exposed to the lower-severity component-instantiation issue (GHSA-48hr-524c-v5w3).
- Any `@nuxt/devtools` version, in development only: exposed to the critical DevTools RCE (GHSA-279x-mwfv-vcqv) — not a production-facing risk, but treat any exposed dev server as untrusted until patched.

## If you are affected

1. Upgrade: `npx nuxt upgrade --dedupe` to reach **Nuxt 4.5.1 / 3.21.10**, and update `@nuxt/devtools` to **3.3.1**.
2. If you're on Nuxt ≥4.4.0, purge any CDN/edge cache that may hold a leaked `_payload.json` after upgrading (per Nuxt's own remediation guidance for GHSA-wm8w-6qjm-cv43).
3. If you can't upgrade immediately, disable `vue.runtimeCompiler` if you don't need it, and check Socket's backport patches for your release line.
4. See [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) if you find evidence of exploitation predating your patch.

## Prevention

→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
→ Treat any framework feature that forwards request-controlled data into a template/dynamic-component-resolution API as a code-execution boundary, not a rendering convenience — the same "decorator/annotation-as-documentation" lesson this repo tracks elsewhere applies to `<component :is>`/`resolveDynamicComponent` accepting untrusted input.
→ Subscribe to `nuxt.com/blog` if you run Nuxt in production, the same way this repo already recommends for Next.js's monthly security-release cadence.

## Why this matters for vibe coders

Nuxt (and its companion `@nuxt/ui` component library) is a major Vue-based alternative to Next.js/React for AI-assisted app scaffolding, and Server Islands are exactly the kind of feature a vibe-coded app is likely to adopt via a copy-pasted example without understanding the `vue.runtimeCompiler` precondition. The DevTools RCE is also a reminder that dev-only tooling shipped alongside a framework is still part of its attack surface if a dev server is ever exposed beyond localhost.

## Sources

- [Nuxt — "Nuxt Security Patch Releases" (v4.5 security post)](https://nuxt.com/blog/v4-5-security) — primary vendor disclosure, published 2026-07-27: full advisory table, severities, affected/fixed versions, remediation guidance.
- [GitHub Security Advisory — GHSA-9473-5f9j-94wq](https://github.com/nuxt/nuxt/security/advisories/GHSA-9473-5f9j-94wq) — canonical advisory for the headline RCE: CVSS 8.1, exact preconditions, affected version ranges.
- [GitHub Security Advisory — GHSA-48hr-524c-v5w3](https://github.com/nuxt/nuxt/security/advisories/GHSA-48hr-524c-v5w3) — companion advisory: CVSS 4.8, confirms no runtime-compiler precondition needed.
- [Vercel — Nuxt July 2026 security advisory](https://vercel.com/changelog/nuxt-july-2026-security-advisory) — independent corroboration from a hosting platform that received advance notice and deployed WAF mitigations.
