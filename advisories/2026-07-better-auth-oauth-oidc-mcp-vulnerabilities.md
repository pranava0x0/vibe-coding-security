---
id: 2026-07-better-auth-oauth-oidc-mcp-vulnerabilities
title: "better-auth — 13+ OAuth/OIDC/SSO/SCIM advisories including a critical MCP-plugin refresh-token bypass (CVE-2026-53512)"
date_disclosed: 2026-06-02
last_updated: 2026-07-18
severity: high
status: patched
ecosystems: [npm, nextjs, auth]
tools_affected: [better-auth, better-auth-sso, better-auth-oauth-provider, better-auth-scim, better-auth-stripe, better-auth-mcp]
tags: [cve, oauth, oidc, account-takeover, auth-framework, mcp, deprecated-plugin]
---

## TL;DR

**better-auth** — a widely-adopted TypeScript auth library commonly paired with Next.js and Supabase-style "vibe coded" stacks as an alternative to NextAuth.js/Auth.js — published **13 security advisories on 2026-06-02** (2 critical, 9 high, 1 medium, 1 low) and **4 more on 2026-06-26**, spanning account takeover via SSO/SAML/OIDC, SCIM provider-ID collisions, magic-link/OTP pre-account hijacking, cross-organization billing tampering, and OAuth refresh-token flaws. The most severe for AI-tool users: **CVE-2026-53512** (CVSS 9.1, critical) — the deprecated `oidcProvider` and `mcp` plugins issue OAuth refresh tokens without verifying the client's secret, so anyone who obtains a valid refresh token (via log capture, DB read, or XSS) can mint fresh access tokens indefinitely. Update to **better-auth ≥ 1.6.11** (≥ 1.6.22 for the SCIM plugin); the `mcp` and `oidcProvider` plugins are deprecated and slated for removal in 1.7 — better-auth's own guidance is to migrate off them rather than keep patching.

## What happened

better-auth positions itself as a framework-agnostic, TypeScript-first alternative to NextAuth.js/Auth.js, and ships a plugin architecture covering SSO, SAML, OIDC, SCIM provisioning, Stripe billing, and — relevant to AI coding agents — an MCP (Model Context Protocol) OAuth-provider plugin for authenticating MCP clients. It runs a formal internal security-review process (triage → code review → scanning → patch review → advisory), which is how this batch surfaced.

**2026-06-02 batch (13 advisories, 2 critical + 9 high):** covers issues across `@better-auth/sso`, `@better-auth/oauth-provider`, and the deprecated `oidcProvider`/`mcp` plugins. The standout for this repo's audience:

- **CVE-2026-53512** (critical, CVSS 9.1) — the deprecated `oidcProvider` and `mcp` plugins each expose an OAuth 2.0 token endpoint whose `refresh_token` grant authenticates purely on possession of the bound refresh-token database row plus a matching (public, non-secret) `client_id` — the plugin never verifies the confidential client's `client_secret` on the refresh path. Anyone who obtains a valid refresh token — via a database read, a log line, browser-side XSS, or (specific to the `mcp` plugin) a CORS-amplified script — can mint fresh access tokens and rotated refresh tokens indefinitely, until the token chain is explicitly revoked. This directly affects any app that stood up better-auth's MCP OAuth provider to authenticate MCP clients. Fixed in **1.6.11**.
- **GHSA-p2fr-6hmx-4528** (moderate) — `@better-auth/oauth-provider` access tokens aren't audience-bound to the authorization grant (RFC 8707), letting a token issued for one resource be replayed against another.
- **GHSA-392p-2q2v-4372 / GHSA-7w99-5wm4-3g79** (high) — OAuth refresh-token rotation race conditions that fork the token family or allow concurrent redemption, undermining rotation-based revocation.
- **GHSA-86j7-9j95-vpqj** (moderate) — stored XSS in the deprecated `oidc-provider`'s auth-server origin via a `javascript:` redirect URI.

**2026-06-26 batch (4 more advisories):** extends the same theme —

- **GHSA-rjg6-39jm-rgg4** (critical, CVSS 9.9) — `@better-auth/scim` used the same logical provider ID for SCIM configuration and account ownership, letting an authenticated user mint a SCIM token that matches an existing SSO/SAML/OIDC/social provider ID and act through a provider namespace they don't own; also missing SCIM-`active` deactivation modeling and email-uniqueness checks on update. Fixed in **1.6.22** / **1.7.0-beta.10**.
- **GHSA-qq9h-g4jm-xgf3** (high) — account takeover via pre-account hijacking on magic-link and email-OTP sign-in.
- **GHSA-prpr-5gj3-qqhg** (high) — account takeover via multiple SSO flaws.
- **GHSA-h3rm-78g3-j7cp** (high) — `@better-auth/stripe` cross-organization billing tampering in organization-subscription actions.

**Vendor guidance:** better-auth's own June 2026 security-update post recommends updating to the latest 1.6.x release (1.6.14 at time of posting) for both the core package and any scoped plugin packages in use, and explicitly recommends **migrating off the deprecated `oidcProvider` and `mcp` plugins to `@better-auth/oauth-provider`** rather than continuing to rely on patches to legacy code slated for removal in 1.7.

## Am I affected?

```bash
# Check installed version
npm ls better-auth 2>/dev/null
cat package.json | grep -A2 '"better-auth"'

# Check whether you use the deprecated MCP or OIDC provider plugins
grep -rE "oidcProvider|mcp\(\)|@better-auth/(sso|scim|stripe|oauth-provider)" src/ 2>/dev/null
```

You are affected if you run **better-auth < 1.6.11** (core OAuth/OIDC issues), **`@better-auth/scim` < 1.6.22** (SCIM collision), or use the deprecated `oidcProvider`/`mcp` plugins at all — those are being removed in 1.7 and should be migrated off regardless of patch status.

### IOCs

| Type | Value |
|---|---|
| Critical CVE | `CVE-2026-53512` — MCP/OIDC refresh-token client-secret bypass, CVSS 9.1 |
| Critical GHSA | `GHSA-rjg6-39jm-rgg4` — SCIM provider-ID collision, CVSS 9.9 |
| Affected | better-auth < 1.6.11 (core); `@better-auth/scim` < 1.6.22 |
| Fixed | better-auth ≥ 1.6.11; `@better-auth/scim` ≥ 1.6.22 |
| Deprecated, migrate off | `oidcProvider` and `mcp` plugins (removed in 1.7) |
| Total advisories | 13 (2026-06-02) + 4 (2026-06-26) |

## Update — 2026-07-18: two more `@better-auth/sso` CVEs, published the same day, fixed in the same 1.6.11 you should already be on

Two additional CVEs in `@better-auth/sso` were published on **2026-07-15** — both patched in the **same 1.6.11 release** already recommended above, so anyone who updated in response to CVE-2026-53512 is already fixed, but anyone still on an older build has more exposure than previously documented here:

- **CVE-2026-53513** (GHSA-5rr4-8452-hf4v, CVSS 9.6, critical) — the `POST /sso/register` endpoint accepts attacker-controlled `oidcConfig.userInfoEndpoint`, `tokenEndpoint`, and `jwksEndpoint` URLs when `skipDiscovery: true` is set, persists them on the `ssoProvider` row with no origin validation, then issues **server-side fetches to those URLs** during the OIDC callback and reflects the response body back through the user profile — a non-blind SSRF reachable by any authenticated session. This reaches internal-only endpoints: cloud metadata services (AWS IMDS), Redis, admin panels bound to localhost. Worse, if `trustEmailVerified: true` is configured (a common convenience setting), a crafted `userInfo` response with `emailVerified: true` and an attacker-chosen email triggers OAuth auto-linking against any pre-existing account with that email — turning the SSRF into full **account takeover**. Mitigate immediately by setting `sso({ providersLimit: 0 })` to block self-registration, gating `/sso/register` at your reverse proxy, and setting `trustEmailVerified: false`.
- **CVE-2026-53515** (GHSA-gv74-j8m3-fg5f, CVSS 7.1, high) — from `1.2.10` until `1.6.11`, `registerSSOProvider` checked only for organization-membership when handling `POST /sso/register`, not an owner/admin role — **any** organization member could attach an attacker-controlled OIDC/SAML provider to the organization, which then drives `/sso/callback/{providerId}` provisioning for that org.

Both are fixed in **better-auth ≥ 1.6.11**, same as CVE-2026-53512. If you already updated for the June batch, you're covered; if not, these two raise the urgency — CVE-2026-53513 in particular is a higher CVSS than the original headline CVE.

## If you are affected

1. **Update `better-auth` and every scoped plugin package you use** to the versions above.
2. **If you use the `mcp` or `oidcProvider` plugins to authenticate MCP clients, migrate to `@better-auth/oauth-provider`** — these plugins are deprecated and won't receive further security attention beyond 1.7 removal.
3. **Revoke and rotate all outstanding refresh tokens** issued by an affected instance if you were on a pre-1.6.11 build and can't rule out token exposure (logs, DB access, XSS reports).
4. **Audit SCIM-provisioned accounts** for provider-ID collisions if you run `@better-auth/scim` pre-1.6.22 — look for SCIM-provisioned users that unexpectedly share identifiers with SSO/SAML/OIDC/social-login accounts.
5. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Treat auth-library plugin architectures the same as any other dependency surface — audit which plugins you actually use, and remove ones you don't (each additional plugin, especially a deprecated one, is additional attack surface with a shrinking patch commitment).
- When wiring MCP OAuth into any auth library, verify the token endpoint enforces `client_secret` (or PKCE for public clients) on every grant type, not just the initial authorization — refresh-token grants are a common place for this check to be silently dropped.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources

- [better-auth — Security update: June 2026](https://better-auth.com/blog/security-update-june-2026) — vendor's own disclosure post; 13 advisories, severity breakdown, migration guidance for `oidcProvider`/`mcp`.
- [GitHub — better-auth/better-auth security advisories](https://github.com/better-auth/better-auth/security) — full advisory index with GHSA IDs and severities.
- [GitLab Advisory Database — CVE-2026-53512](https://advisories.gitlab.com/npm/better-auth/CVE-2026-53512/) — canonical CVE record for the MCP/OIDC refresh-token bypass; CVSS 9.1, CWE-287/306/345/863, fixed version 1.6.11.
- [GitHub Security Advisory — GHSA-rjg6-39jm-rgg4](https://github.com/better-auth/better-auth/security/advisories/GHSA-rjg6-39jm-rgg4) — SCIM provider-ID collision advisory; affected/fixed versions, disclosure date 2026-06-26.
- [GitHub Security Advisory — GHSA-5rr4-8452-hf4v (CVE-2026-53513)](https://github.com/better-auth/better-auth/security/advisories/GHSA-5rr4-8452-hf4v) — `@better-auth/sso` SSRF via unvalidated OIDC endpoints on provider registration; vendor advisory, CVSS 9.6.
- [GitLab Advisory Database — CVE-2026-53513](https://advisories.gitlab.com/npm/@better-auth/sso/CVE-2026-53513/) — independent corroboration of the SSRF advisory.
- [Security Online — Better Auth SSRF Flaw CVE-2026-53513 (CVSS 9.6) Threatens 19M-Download Auth Library](https://securityonline.info/better-auth-ssrf-cve-2026-53513/) — independent write-up with attack-chain detail (SSRF → account takeover via `trustEmailVerified`).
