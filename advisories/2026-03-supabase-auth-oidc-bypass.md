---
id: 2026-03-supabase-auth-oidc-bypass
title: "Supabase Auth OIDC issuer-validation bypass — CVE-2026-31813 (March 2026)"
date_disclosed: 2026-03-11
last_updated: 2026-06-08
severity: high
status: patched
ecosystems: [supabase, auth]
tools_affected: [supabase, gotrue, lovable, bolt, v0, any-supabase-auth-app]
tags: [cve, authentication-bypass, oidc, account-takeover, vibe-platform, self-hosted]
---

## TL;DR
**CVE-2026-31813** (CWE-290, GitHub advisory **GHSA-v36f-qvww-8w8m**) — Supabase Auth (`gotrue`) before **2.185.0** fails to strictly validate the **issuer (`iss`) of OIDC ID tokens** when the **Apple or Azure** providers are enabled. An attacker who stands up their own OIDC-compliant identity provider can mint signed ID tokens for **any victim email**, submit them to the Supabase Auth token endpoint, and receive valid session tokens — i.e., **log in as anyone**. Since Supabase is the default backend/auth layer for huge swaths of vibe-coded apps (Lovable, Bolt, v0, and countless Cursor/Claude Code projects), this is a full account-takeover primitive for any affected, self-hosted deployment. Fix: upgrade `gotrue`/Supabase Auth to **2.185.0+**.

## What happened
GitHub published advisory **GHSA-v36f-qvww-8w8m** on **2026-03-11** (rated Moderate by GitHub; high-impact in practice because it's an authentication bypass). The bug: when Supabase Auth processes an ID token for the **Apple** or **Azure** sign-in flow, it verifies the token's cryptographic signature and OIDC compliance but **does not enforce that the token's `iss` (issuer) claim matches the legitimate provider**.

Exploitation path:
1. Identify a target app using Supabase Auth with Apple or Azure providers enabled.
2. Stand up a malicious OIDC-compliant identity provider you control.
3. Generate validly (asymmetrically) signed ID tokens for each victim email address, issued by your malicious issuer.
4. Submit those crafted ID tokens to the Supabase Auth token endpoint via the ID-token flow.
5. Receive valid **AAL1 session tokens** for the victim account — no prior authentication or user interaction required.

The flaw is in the self-hostable `gotrue`/`supabase-auth` server component. Supabase's hosted platform was updated by the vendor, but **anyone running self-hosted Supabase Auth must upgrade**.

## Am I affected?

```bash
# Self-hosted: check your gotrue / supabase-auth image tag (need >= 2.185.0)
docker ps --format '{{.Image}}' | grep -iE 'gotrue|supabase.*auth'
docker inspect <auth-container> --format '{{.Config.Image}}'

# In a docker-compose / supabase stack:
grep -iE 'gotrue|supabase/auth' docker-compose*.yml supabase/*.yml 2>/dev/null
```

You are affected if you run **self-hosted Supabase Auth < 2.185.0** with the **Apple or Azure** OIDC providers enabled. If those providers are disabled, the specific attack path does not apply — but upgrade anyway.

### IOCs / fix

| Type | Value |
|---|---|
| CVE | `CVE-2026-31813` |
| GHSA | `GHSA-v36f-qvww-8w8m` |
| Weakness | CWE-290 (Authentication Bypass by Spoofing) |
| Precondition | Apple or Azure OIDC provider enabled |
| Affected component | `supabase/gotrue` / `supabase-auth` < 2.185.0 |
| Fixed version | 2.185.0 |

## If you are affected
1. Upgrade Supabase Auth / `gotrue` to **2.185.0+** immediately.
2. Treat all sessions issued before the upgrade as suspect, especially on accounts using Apple/Azure sign-in. **Invalidate existing sessions / rotate JWT signing secret** to force re-authentication.
3. Review auth logs for ID-token grants from unexpected issuers or impossible-travel logins.
4. Audit Row Level Security — an attacker who logged in as a victim inherits that user's data access; if your RLS is weak (a [recurring vibe-coding failure](ongoing-vibe-platform-exposure.md)), the blast radius is larger.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [advisories/ongoing-vibe-platform-exposure.md](ongoing-vibe-platform-exposure.md) — Supabase/RLS misconfiguration context.
→ Keep self-hosted auth components on a patch cadence; subscribe to the [supabase/auth GitHub security advisories](https://github.com/supabase/auth/security/advisories). Don't assume a managed-platform fix covers your self-hosted stack.

## June 2026 update — Email link poisoning via forwarded-host header (GHSA-3529-5m8x-rpv3)

**GHSA-3529-5m8x-rpv3** (CVSS 7.3) — A separate vulnerability in Supabase Auth's **email verification and magic-link flows**. When the auth server sits behind a reverse proxy and the proxy forwards `X-Forwarded-Host` or `X-Forwarded-Proto` headers, Supabase Auth incorporates those header values directly into confirmation and magic-link URLs embedded in outgoing email. An attacker who can manipulate those proxy headers — or who operates a misconfigured shared proxy — can redirect the URL in auth emails to an attacker-controlled domain.

**Attack path:**
1. User requests a password reset, email change confirmation, or magic-link sign-in.
2. The request passes through a reverse proxy that forwards attacker-controlled `X-Forwarded-Host` / `X-Forwarded-Proto` headers to the Supabase Auth process.
3. Supabase Auth embeds the attacker-supplied host in the confirmation link in the outgoing email.
4. User clicks the link → browser sends the one-time auth code to the attacker's server → attacker completes the authentication flow → **full account takeover with no password required**.

Primarily affects **self-hosted Supabase deployments** where the reverse proxy is not configured to strip or validate forwarded host headers (a common misconfiguration in Docker Compose stacks). Hosted Supabase was patched by the vendor.

**Fix:** Upgrade `supabase/auth` to the patched version listed in the [GHSA advisory](https://github.com/supabase/auth/security/advisories/GHSA-3529-5m8x-rpv3), and configure your reverse proxy to strip `X-Forwarded-Host` from untrusted upstream sources. For nginx, add `proxy_set_header X-Forwarded-Host $host;` to prevent header injection.

| Type | Value |
|---|---|
| GHSA | `GHSA-3529-5m8x-rpv3` |
| CVSS | 7.3 |
| Affected | Self-hosted `supabase/auth` before the patched release |
| Fix | Upgrade per GHSA + strip `X-Forwarded-Host` in proxy config |

## Sources
- [GitHub Advisory — GHSA-v36f-qvww-8w8m: Insecure Apple and Azure authentication with ID tokens (supabase/auth)](https://github.com/supabase/auth/security/advisories/GHSA-v36f-qvww-8w8m)
- [NVD — CVE-2026-31813](https://nvd.nist.gov/vuln/detail/CVE-2026-31813)
- [SentinelOne — CVE-2026-31813: Supabase Auth Bypass Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-31813/)
- [Red Hat — CVE-2026-31813](https://access.redhat.com/security/cve/cve-2026-31813)
- [OffSeq Threat Radar — CVE-2026-31813 (CWE-290 Authentication Bypass by Spoofing in supabase auth)](https://radar.offseq.com/threat/cve-2026-31813-cwe-290-authentication-bypass-by-sp-c3c5f69f)
- [GitHub Advisory — GHSA-3529-5m8x-rpv3: Email link poisoning via X-Forwarded-Host header manipulation (supabase/auth)](https://github.com/supabase/auth/security/advisories/GHSA-3529-5m8x-rpv3)
- [NVD — GHSA-3529-5m8x-rpv3 cross-reference](https://nvd.nist.gov/vuln/search/results?query=GHSA-3529-5m8x-rpv3)
