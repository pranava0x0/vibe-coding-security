---
id: 2026-07-nextauth-magic-link-homoglyph-bypass
title: "NextAuth.js / Auth.js — 4 advisories including a homoglyph bypass that redirects magic-link sign-in to an attacker's inbox (no CVE yet, patch to 4.24.15 / 5.0.0-beta.32)"
date_disclosed: 2026-07-20
last_updated: 2026-07-22
severity: high
status: unconfirmed
ecosystems: [npm, nextjs, auth]
tools_affected: ["next-auth", "@auth/core", "Auth.js"]
tags: [authentication, account-takeover, magic-link, oauth, denial-of-service, auth-framework]
---

## TL;DR

**NextAuth.js / Auth.js** — the auth library shipped by Vercel and used as the default authentication layer in a large share of Next.js "vibe coded" stacks — published **4 security advisories on 2026-07-20**. The most serious: a **homoglyph "@" bypass** (GHSA-7rqj-j65f-68wh, high) where the email provider validates an address *before* Unicode-normalizing it, so an attacker can craft an address that passes validation but normalizes to contain a second `@` — redirecting another user's passwordless magic-link sign-in email to the attacker's own inbox, with no victim interaction required. Also fixed: an unauthenticated **denial-of-service** in `getToken()` via a malformed `Authorization: Bearer` header (GHSA-xmf8-cvqr-rfgj, CVSS 7.5), an **OAuth state/nonce/PKCE cookie** that isn't bound to the provider that created it (GHSA-x445-f3h2-j279, moderate), and a **fail-open** existence-based auth check on configuration errors (GHSA-8fpg-xm3f-6cx3, low). All four are fixed in **`next-auth` 4.24.15 / 5.0.0-beta.32** and **`@auth/core` 0.41.3**. No CVE has been assigned to any of the four as of this writing, and only the vendor's own GitHub Security Advisories page has published details — no independent aggregator coverage found yet, so this entry is marked `unconfirmed` pending a second source.

## What happened

NextAuth.js (published as `@auth/core` under the newer Auth.js branding, still widely installed as `next-auth`) shipped four advisories in one batch on its own GitHub Security Advisories page on **2026-07-20**:

- **GHSA-7rqj-j65f-68wh** (high) — "Email normalizer validates the address before Unicode normalization, allowing a homoglyph @ bypass." The built-in email provider's default address normalizer runs input validation *before* applying Unicode (NFKC-style) normalization. An attacker can submit an address containing Unicode characters that visually or semantically resemble, but aren't, an ASCII `@` — the address passes validation in its raw form, but after normalization resolves to a string containing **two `@` separators**, which can cause the mail-delivery step to route the passwordless ("magic link") sign-in email to a **different, attacker-controlled mailbox** than the one the victim intended to use. No password, no OAuth, and no victim click is required beyond the victim initiating their own sign-in flow. Affects `next-auth` 4.10.3–4.24.14 and 5.0.0-beta.1–beta.31, and `@auth/core` 0.1.0–0.41.2.
- **GHSA-xmf8-cvqr-rfgj** (high, CVSS 7.5) — `getToken()` throws an unhandled exception when it attempts to URL-decode a malformed `Authorization: Bearer` header before validating it, rather than treating a malformed token as simply invalid. Any app that calls `getToken()` in a route handler or middleware without wrapping it in its own try/catch can be knocked over by a single unauthenticated request carrying a malformed header — an availability-only bug, no credential or session exposure.
- **GHSA-x445-f3h2-j279** (moderate) — OAuth `state`, `nonce`, and PKCE verifier cookies are not bound to the specific provider that created them, which can allow cross-provider confusion in multi-provider setups.
- **GHSA-8fpg-xm3f-6cx3** (low) — certain configuration errors cause existence-based authentication checks to fail open rather than closed.

All four affect the same version ranges (`next-auth` up to 4.24.14 / 5.0.0-beta.31, `@auth/core` up to 0.41.2) and are fixed in the same releases (`next-auth` 4.24.15 / 5.0.0-beta.32, `@auth/core` 0.41.3). **No CVE has been assigned to any of the four** as of this writing. This entry is sourced solely from the vendor's own GitHub Security Advisories page — no independent aggregator (The Hacker News, BleepingComputer, etc.) coverage was found as of 2026-07-22, so it is marked `unconfirmed` per this repo's two-independent-source bar; it will be promoted to `patched` once a second source or CVE assignment appears, or on confirmation the facts hold up.

## Am I affected?

```bash
# Check installed version
npm ls next-auth @auth/core 2>/dev/null
cat package.json | grep -A1 -E '"next-auth"|"@auth/core"'
```

You are affected if you run **`next-auth` < 4.24.15** (v4) or **< 5.0.0-beta.32** (v5), or **`@auth/core` < 0.41.3**. You are specifically exposed to the magic-link redirect bug if you use the built-in **Email provider** for passwordless sign-in; the DoS bug affects any app calling `getToken()` without its own error handling.

## If you are affected

1. Update `next-auth`/`@auth/core` to the patched versions above.
2. If you use the Email (magic-link) provider, review recent sign-in email logs for addresses containing unusual Unicode characters near the `@` symbol.
3. Wrap any direct `getToken()` calls in your own middleware/route handlers in a try/catch until you've confirmed the upgrade is deployed.
4. See [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) if you find evidence of magic-link redirection having already occurred.

## Prevention

- Validate/canonicalize untrusted input in the correct order: normalize first, then validate the normalized form — never validate a raw string and assume that guarantees anything about its canonicalized equivalent. This is the same "two parsers, one string" root cause this repo tracks across argv-smuggling, SOCKS5 null-byte, and Starlette BadHost findings, just applied to Unicode email-address canonicalization instead of network/path parsing.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources

- [GitHub — nextauthjs/next-auth security advisories](https://github.com/nextauthjs/next-auth/security/advisories) — vendor's own advisory index; all four listed with dates and severities.
- [GitHub Security Advisory — GHSA-7rqj-j65f-68wh](https://github.com/nextauthjs/next-auth/security/advisories/GHSA-7rqj-j65f-68wh) — homoglyph `@` bypass, affected/fixed versions.
- [GitHub Security Advisory — GHSA-xmf8-cvqr-rfgj](https://github.com/nextauthjs/next-auth/security/advisories/GHSA-xmf8-cvqr-rfgj) — `getToken()` DoS, CVSS 7.5, affected/fixed versions.
