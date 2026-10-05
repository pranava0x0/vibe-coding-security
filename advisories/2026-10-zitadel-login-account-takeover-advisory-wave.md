---
id: 2026-10-zitadel-login-account-takeover-advisory-wave
title: "ZITADEL (the open-source identity provider behind many self-hosted app logins): twenty vendor advisories between 2026-06-08 and 09-28, ten of them account takeovers that need only the victim's login name — unauthenticated passkey enrollment on identify-only sessions (CVE-2026-105212), external-IdP linking before any factor is verified (CVE-2026-105207, 9.8), cross-organisation enrollment codes (CVE-2026-105209, 9.6), forged IdP callbacks (CVE-2026-105215, 9.1), predictable session IDs and SAML provider confusion (unassigned, 4.19.2) — VulnCheck assigned ten CVEs on 10-04; fixed in 4.19.2, 3.x is end-of-life"
date_disclosed: 2026-07-29
last_updated: 2026-10-05
severity: critical
status: patched
ecosystems: [auth, oidc, saml, self-hosted, go]
tools_affected: ["ZITADEL 4.x before 4.19.2 (self-hosted and any cloud tenant that was not yet upgraded)", "ZITADEL 3.x (end-of-life 2026-08-31; several bugs have no 3.x fix)", "any application that delegates login to a ZITADEL instance via OIDC or SAML", "ZITADEL hosted Login V1 and Login V2 UIs"]
tags: [auth-bypass, account-takeover, passkey, mfa-bypass, oidc, saml, idp-confusion, session-fixation, identity-provider, self-hosted, cve, vulncheck, vendor-ghsa-batch]
---

## TL;DR

**ZITADEL** is the Go-based open-source identity provider that a lot of self-hosted and "I don't want Auth0's bill" stacks put in front of their apps. Between **2026-06-08 and 2026-09-28** its maintainers published **twenty GitHub Security Advisories**, and on **2026-10-04** VulnCheck (as CNA) assigned **ten CVEs** to the most serious ones. The common shape: ZITADEL's hosted login UIs accepted account-changing operations on an **"identify-only" session** — after the username was typed, before any password, passkey or second factor was checked. That gave an attacker who knew only a victim's **login name** the ability to **enroll their own passkey** (CVE-2026-105212, affected ≤ 4.16.1), **bind their own external identity to the victim's account** and sign in through the federated provider (CVE-2026-105207, CVSS 9.8, ≤ 4.17.2), **pre-hijack an account through a forged external-IdP callback** (CVE-2026-105215, 9.1, ≤ 4.16.1), **enroll TOTP/SMS factors and overwrite the victim's phone number** (CVE-2026-105210, 8.2), **rename any user including admins** (unassigned, ≤ 4.17.3), and — because session cookies were unsigned and session IDs time-ordered — **guess another user's live session** (unassigned, 8.1, fixed 4.19.2). Multi-tenant deployments got **cross-organisation account takeover via enrollment codes** (CVE-2026-105209, 9.6), and anyone with two SAML providers configured got **IdP confusion** (8.7, 4.19.2). **Upgrade to 4.19.2** (skip 4.18.0, which the vendor says fails setup; 4.19.2 also requires setting `ZITADEL_SESSION_COOKIE_SECRET` on every Login UI replica before upgrading). **3.x reached end-of-life on 2026-08-31** and does not get the September fixes — the vendor's own advisories say "no patch available" for that line. If your app's login page is a ZITADEL instance, this is the auth-stack equivalent of the [better-auth](2026-07-better-auth-oauth-oidc-mcp-vulnerabilities.md) and [NextAuth](2026-07-nextauth-magic-link-homoglyph-bypass.md) waves this repo already tracks, with higher scores and a longer tail.

## What happened

ZITADEL discloses through its own repository advisory tab, with no blog post and, until 10-04, no CVEs; nothing here ranked in a search query. The tab's two pages (fetched 2026-10-05) show **twenty advisories from 2026-06-08 to 09-28**. The CVE records VulnCheck published on 10-04 each reference exactly one GHSA, which is the mapping used below; scores are the vendor's where the GHSA page shows one, and VulnCheck's CVSS 4.0 / 3.1 pairs from the CVE records otherwise.

### Account takeover with only a login name (unauthenticated)

| Bug | Ids | Affected → fixed | What an attacker with only a username could do |
|---|---|---|---|
| **Passkey enrollment on an identify-only session** (Login V1 and V2) | GHSA-45f2-5q3r-xgg6, **CVE-2026-105212** (VulnCheck 4.0 **8.7** / 3.1 7.5; vendor: Critical) | 4.0.0–4.16.1 → **4.16.2**; 3.0.0–3.4.13 → 3.4.14 | Enroll an attacker-controlled passkey "after the username was submitted, but before any password or other primary factor was verified," then log in — "without knowing the password, using an existing passkey, completing MFA, or interacting with the victim." Published 2026-07-29. |
| **Account pre-hijacking via forged external-IdP callback** (Login V1) | GHSA-738m-7888-jfv8, **CVE-2026-105215** (4.0 **9.3** / 3.1 9.1; vendor: Critical) | ≤ 4.16.1 → 4.16.2; ≤ 3.4.13 → 3.4.14 | Published 2026-07-29 alongside the passkey bug; the CVE title is the vendor's. |
| **External-IdP linking before verification** (Login V2 + API) | GHSA-g8gj-gq47-xgf4, **CVE-2026-105207** (4.0 **9.3** / 3.1 **9.8**; vendor: Critical 9.8) | 4.0.0–4.17.2 → **4.17.3**; 3.x: **no patch (EOL)** | "Bind their own external identity to the victim's account" through Login V2's identify-only session, then authenticate as the victim through the federated provider; an authenticated user could also pre-claim arbitrary external identities via the API. Disabling IdP linking closes the UI vector but not the API one. Published 2026-09-04. |
| **OTP-Email / OTP-SMS return-code bypass** (Login V2) | GHSA-3gwm-5wx8-4gm6, **CVE-2026-105211** (4.0 9.2 / 3.1 8.1; vendor: High 8.1) | 4.0.0–4.17.0 → **4.17.1** | The server action "exposed OTP codes directly in responses"; a victim with both OTP-Email and OTP-SMS enrolled could be fully authenticated by an attacker with only the login name. Published 2026-08-14. |
| **Unauthenticated MFA enrollment and phone-number overwrite** (Login V1) | GHSA-72q5-mv5c-vxv4, **CVE-2026-105210** (4.0 8.8 / 3.1 8.2; vendor: High 8.2) | 4.0.0–4.17.0 → 4.17.1; 3.0.0–3.4.14 → 3.4.15 | Enroll TOTP/OTP/U2F factors and change a verified phone number before the password step; also enumerates valid accounts via differential errors. Not a takeover on its own. Published 2026-08-14. |
| **Rename any user, including admins** (Login V1) | GHSA-4hgj-wm6c-q7p2 (no CVE; vendor: High 8.2) | 4.0.0–4.17.3 → **4.19.1** (skip 4.18.0); 3.x: no patch | The change-username request "acted on the account bound to the login flow as soon as a login name had been entered" — lock users out, free usernames for squatting. Published 2026-09-24. |
| **Predictable session IDs + unsigned session cookies** (Login V2) | GHSA-jh92-5mrj-p2w2 (no CVE; vendor: High 8.1) | 4.0.0–4.19.1 → **4.19.2**; 3.x: no patch | Guess time-ordered session IDs to obtain "valid session tokens for other users' authenticated sessions," complete OAuth/SAML flows as them, and for admin sessions take over the instance. Rate limiting is only partial mitigation. Published 2026-09-28. |
| **Login V2 lets users of deactivated organisations log in** | GHSA-558c-v5wc-9w4q, **CVE-2026-105213** (4.0 8.8 / 3.1 8.2; vendor: High) | ≤ 4.17.0 → 4.17.1 | Published 2026-08-14. |

### Cross-tenant and federated-provider bugs (authenticated or multi-provider)

| Bug | Ids | Affected → fixed | Detail |
|---|---|---|---|
| **Cross-organisation account takeover via passkey/passwordless enrollment codes** | GHSA-pq2q-2c6r-75c4, **CVE-2026-105209** (4.0 9.3 / 3.1 **9.6**; vendor: Critical 9.6) | 4.0.0–4.17.0 → 4.17.1; 3.0.0–3.4.14 → 3.4.15 | Issuing an enrollment code "did not verify that the caller was authorized in the organization that owns the target user" — user-write permission in one tenant takes over users in another. Published 2026-08-14. |
| **SAML identity-provider confusion** | GHSA-x4c7-fpcx-w9q6 (no CVE; vendor: High 8.7) | 4.0.0–4.19.1 → 4.19.2; 3.x: no patch | With two or more SAML providers configured, an attacker controlling one provider's signing key "could complete a login intent aimed at a second SAML identity provider and obtain an authenticated session as any user linked to that second provider." Published 2026-09-28. |
| **Forgeable IdP intent tokens → cross-user session hijack and IdP token theft** | GHSA-jh3m-cr2x-qp88, **CVE-2026-105208** (4.0 8.7 / 3.1 7.7; vendor: High 7.7) | 4.0.0–4.17.2 → 4.17.3; 3.x: no patch | Intent tokens lacked integrity protection; the vendor estimates ~1.25% success in a 15-second window per attempt, so a brute-forceable race rather than a deterministic bypass. Published 2026-09-04. |
| **Cross-organisation authentication-method enumeration** | GHSA-j344-gqv4-84ff, **CVE-2026-105206** (4.0 5.3) | ≤ 4.17.2 → 4.17.3 | Published 2026-09-04. |
| **SSRF in organisation-domain HTTP verification** | GHSA-93hm-8q29-c8cr, **CVE-2026-105214** (4.0 2.3; vendor: Low) | ≤ 4.16.1 → 4.16.2 | Published 2026-07-29. |

The June–July advisories on page 2 of the tab — **MFA bypass via session reuse in Login V2** (GHSA-9993-rfwp-rhwf, High, 07-17), **Actions V1 sandbox escape: host file read via `require()`** (GHSA-fgmf-7rf8-m6vf, High, 07-17), **stored XSS via default URI redirect in Login V2** (GHSA-5wcj-9wj4-j65h, High, 06-22), **OAuth2 token-exchange privilege escalation** (GHSA-vrh8-c9cm-wh8v, High, 06-22), **users can self-verify email/phone via API** (GHSA-jq8w-8q2f-ffm9, High, 06-08), **improper role revocation on granted projects** (GHSA-v859-c572-qh5p, Moderate, 07-10) and **cross-tenant user leakage via recycled identifiers** (GHSA-6x8v-2fq5-2229, Low, 06-17) — have no CVE and were not opened individually by this sweep; they are listed from the tab index and are all fixed in 4.19.2 by version ordering.

**Why the scores differ.** Every GHSA page says "No known CVE" because the vendor never requested one; VulnCheck assigned the ten ids on 2026-10-04 and scored them in CVSS 4.0 and 3.1 independently of the vendor's label. The two disagree in both directions — the passkey-enrollment bug is "Critical" on the vendor page but 8.7/7.5 at VulnCheck, while the deactivated-organisation login is 8.8 at VulnCheck against the vendor's "High" — so the table carries both and this file's `critical` rests on the three unauthenticated takeovers the vendor itself rates Critical.

## Am I affected?

- You run ZITADEL **below 4.19.2** (any 4.x), or **any 3.x** — the vendor's September advisories state "3.x: no patch available (end-of-life as of 2026-08-31)."
- Your users log in through the **hosted Login V1 or Login V2 UI** (the default). Pure API/token deployments without the hosted login are exposed to fewer of these but still to the IdP-linking API vector (CVE-2026-105207) and the cross-organisation enrollment codes (CVE-2026-105209).
- You have **external identity providers** with account linking enabled, **two or more SAML providers**, or **multiple organisations** with delegated user administration — each adds a row above.

```bash
# Version check (API) — replace with your instance
curl -s "$ZITADEL_URL/debug/healthz"; curl -s "$ZITADEL_URL/admin/v1/healthz"
# Or from the container image tag / Helm values
grep -rn 'zitadel' docker-compose*.yml values*.yaml | grep -i 'image\|tag'
```

## If you are affected

1. **Upgrade to 4.19.2.** Set `ZITADEL_SESSION_COOKIE_SECRET` (identical, ≥ 32 characters, on every Login UI replica) before the upgrade — the 4.19.2 session-cookie fix depends on it — and skip 4.18.0 per the vendor's note on GHSA-4hgj-wm6c-q7p2. On 3.x, migrate; there is no 3.x fix for the September bugs.
2. **Audit for takeover artefacts** since the first affected version was deployed: passkeys and U2F/TOTP factors enrolled without a matching user action, external-IdP links added to accounts that never used federation, phone-number changes, username changes on admin accounts, and sessions from unfamiliar networks completing OAuth or SAML flows. ZITADEL's event store makes these queryable; the vendor pages do not supply a query, so use your audit-log export.
3. **Force re-authentication and rotate** admin credentials and any OAuth client secrets an instance-level takeover could have read, per [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). If your app stores ZITADEL-issued tokens, invalidate them.
4. If you use the SAML path with multiple providers, verify the provider in every callback matches the intent — the 4.19.2 fix does this; before it, assume any provider operator could have logged in as any user linked to another.

## Prevention

- Treat the identity provider as the highest-value service in the stack and keep it on the vendor's current minor; a login page that has not been upgraded in a quarter now carries ten CVEs — [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- Watch the vendor's advisory tab, not only CVE feeds: the first critical here was public for **67 days** before any CVE existed.
- Rate-limit and bot-protect the login UI and API in front of the instance; the vendor names this as partial mitigation for two of the bugs, and it is the only control that works before you can upgrade.
- Do not give delegated organisation admins user-write permission they do not need; CVE-2026-105209 turns that permission into cross-tenant takeover.
- For vibe-coded apps: if an agent scaffolded your login against a ZITADEL instance it also deployed, the instance version is in your `docker-compose.yml` or Helm values and nobody has bumped it since — check it the same way you would check `next` — [auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md).

## Why this matters for vibe coders

The auth layer is the one piece of a generated app that is almost never written by the generator: it is delegated to a library (better-auth, NextAuth, Clerk) or to an identity server like this one, and then forgotten. This repo now has a same-quarter account-takeover wave in all four. An identity server differs from a library in one way that matters: it is a running service with its own version, not a dependency `npm audit` will ever flag, so the only signal is the vendor's advisory tab or a CNA assigning ids months later — which is what happened here.

## Sources

- [zitadel/zitadel — Security Advisories index, page 1](https://github.com/zitadel/zitadel/security/advisories) and [page 2](https://github.com/zitadel/zitadel/security/advisories?page=2) — fetched 2026-10-05; the twenty advisories, titles, severities and dates used above.
- Vendor advisory pages, fetched 2026-10-05: [GHSA-45f2-5q3r-xgg6 — passkey enrollment on Login V1/V2](https://github.com/zitadel/zitadel/security/advisories/GHSA-45f2-5q3r-xgg6) (ranges, the "identify-only" quote, no-workaround statement, credits); [GHSA-g8gj-gq47-xgf4 — external IdP linking](https://github.com/zitadel/zitadel/security/advisories/GHSA-g8gj-gq47-xgf4) (9.8, 3.x EOL, UI-vs-API workaround limit); [GHSA-pq2q-2c6r-75c4 — cross-organisation enrollment codes](https://github.com/zitadel/zitadel/security/advisories/GHSA-pq2q-2c6r-75c4) (9.6); [GHSA-jh92-5mrj-p2w2 — predictable session IDs](https://github.com/zitadel/zitadel/security/advisories/GHSA-jh92-5mrj-p2w2) (8.1, unsigned cookies, rate-limit partial); [GHSA-x4c7-fpcx-w9q6 — SAML IdP confusion](https://github.com/zitadel/zitadel/security/advisories/GHSA-x4c7-fpcx-w9q6) (8.7, two-provider prerequisite); [GHSA-4hgj-wm6c-q7p2 — rename any user](https://github.com/zitadel/zitadel/security/advisories/GHSA-4hgj-wm6c-q7p2) (8.2, skip 4.18.0); [GHSA-jh3m-cr2x-qp88 — forgeable IdP intent tokens](https://github.com/zitadel/zitadel/security/advisories/GHSA-jh3m-cr2x-qp88) (7.7, the 1.25% estimate); [GHSA-72q5-mv5c-vxv4 — MFA enrollment / phone overwrite](https://github.com/zitadel/zitadel/security/advisories/GHSA-72q5-mv5c-vxv4) (8.2); [GHSA-3gwm-5wx8-4gm6 — OTP return-code bypass](https://github.com/zitadel/zitadel/security/advisories/GHSA-3gwm-5wx8-4gm6) (8.1, both-OTP prerequisite).
- [CVE Services records CVE-2026-105206 through CVE-2026-105215](https://cveawg.mitre.org/api/cve/CVE-2026-105212) — fetched 2026-10-05; each record's single GHSA reference is the mapping above; VulnCheck's CVSS 4.0 and 3.1 vectors; `datePublished` 2026-10-04.
- [VulnCheck — advisories index](https://www.vulncheck.com/advisories) — fetched 2026-10-05; the ten ZITADEL entries dated 2026-10-04; [VulnCheck — ZITADEL before 3.4.14 and 4.16.2 Account Takeover via Passkey Enrollment (CVE-2026-105212)](https://www.vulncheck.com/advisories/zitadel-before-3.4.14-and-4.16.2-account-takeover-via-passkey-enrollment) — the only per-CVE page opened (CVSS 4.0 8.7, credits).
- The `ZITADEL_SESSION_COOKIE_SECRET` upgrade prerequisite appears in search-result summaries of third-party release trackers and was not confirmed on a vendor page by this sweep; verify against the 4.19.2 release notes before upgrading.
- Related in this repo: [better-auth OAuth/OIDC wave](2026-07-better-auth-oauth-oidc-mcp-vulnerabilities.md), [NextAuth magic-link homoglyph bypass](2026-07-nextauth-magic-link-homoglyph-bypass.md), [Clerk middleware bypass](2026-04-clerk-sdk-middleware-bypass-cve-batch.md).
