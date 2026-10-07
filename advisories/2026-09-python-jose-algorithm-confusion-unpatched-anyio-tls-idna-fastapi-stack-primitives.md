---
id: 2026-09-python-jose-algorithm-confusion-unpatched-anyio-tls-idna-fastapi-stack-primitives
title: "Two Python primitives under FastAPI-stack apps, both scored 9.3: python-jose (the JWT library older FastAPI tutorials import) accepts a DER-encoded public key as an HMAC secret, so anyone holding the service's public key forges HS256 tokens when algorithms aren't pinned — CVE-2026-85394, an incomplete fix of CVE-2024-33663, reported 2026-06-04, CVE 09-03, still unpatched at 3.5.0 with the fix PR unanswered; and AnyIO (under Starlette/FastAPI/httpx) validated TLS host names after IDNA-2003 encoding, letting a hijacked connection to a non-ASCII domain present a certificate for the wrong name — CVE-2026-63374, fixed 4.14.2 on 2026-07-07"
date_disclosed: 2026-09-03
last_updated: 2026-10-07
severity: high
status: active
ecosystems: [pypi, fastapi, python]
tools_affected: ["python-jose ≤ 3.5.0 (no fix)", "anyio < 4.14.2", "FastAPI / Starlette apps verifying RS256/ES256 tokens with python-jose and no algorithms= pin", "httpx / Starlette / FastAPI clients connecting to internationalised domain names"]
tags: [cve, jwt, algorithm-confusion, token-forgery, incomplete-fix, unpatched, fastapi, tls, certificate-validation, idna, supply-chain-primitive, backfill]
---

## TL;DR
**python-jose** — the `from jose import jwt` library that a generation of FastAPI auth tutorials and generated backends still use — has a **critical, unpatched** algorithm-confusion bug. Its guard against "public key used as HMAC secret" (added for CVE-2024-33663) checks only PEM armor and OpenSSH prefixes, so a **DER-encoded public key passes** and is used as the HS256 secret; an attacker who has the service's public key (which is public) can **forge any token** against a verifier that does not pin `algorithms=`. **CVE-2026-85394** (VulnCheck CNA, CVSS 4.0 **9.3** / 3.1 9.1) was published 2026-09-03 after the reporter emailed the maintainer on 2026-06-04 without response and opened issue #414 on 07-06; a community fix (PR #422, 2026-09-16) is still open with no maintainer reply as of 2026-10-07, and `pip index versions python-jose` shows **3.5.0** as the latest release. Separately, **AnyIO** < 4.14.2 — the async layer under Starlette, FastAPI and httpx — validated TLS host names after the standard library's IDNA-2003 conversion, so a hijacked connection to a non-ASCII domain could present a legitimate certificate for a differently-encoded name (**CVE-2026-63374**, 9.3, fixed **4.14.2** on 2026-07-07). Pin `algorithms=[...]` everywhere you call `jwt.decode`, migrate off python-jose, and let `anyio` float to ≥ 4.14.2.

## What happened

### python-jose — CVE-2026-85394 (critical, no fix)

The 2024 fix for CVE-2024-33663 taught `python-jose` to refuse an HMAC key that *looks like* an asymmetric key. The check is textual: `is_pem_format()` and `is_ssh_key()`. George Chen (geo-chen) reported on 2026-07-06 in [issue #414](https://github.com/mpdavis/python-jose/issues/414) — after an email on **2026-06-04** that, per the issue, got no response — that "a DER-encoded (binary SubjectPublicKeyInfo) public key matches neither … so it passes the guard." VulnCheck, as CNA, published **CVE-2026-85394** on **2026-09-03**: "python-jose through 3.5.0 fails to properly validate asymmetric keys in HMAC initialization, accepting DER-encoded public keys that lack PEM armor or SSH prefixes. Attackers holding the service's public key can forge HS256 tokens that pass verification when algorithms are not explicitly restricted. This is an incomplete fix for CVE-2024-33663." Scores: CVSS 4.0 **9.3** (`AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N`), CVSS 3.1 9.1 — both VulnCheck's; GitHub's database copy (GHSA-3qf3-8w2g-rqmx) lists **"Patched versions: None."**

**Fix status, 2026-10-07.** A contributor PR, [#422 "Reject DER-encoded asymmetric keys as HMAC secrets (CVE-2026-85394)"](https://github.com/mpdavis/python-jose/pull/422), opened 2026-09-16, adds ASN.1-structural DER detection to both the native and `cryptography` backends; the only activity is a community "Any updates on this fix?" on 2026-10-07. The repository is not archived (1.8k stars, open issues and PRs, CI configured), but there is no maintainer response on the issue or the PR, and no release since 3.5.0. This repo's status for the library is therefore **`active`**: a known-exploitable, publicly documented bypass with no fix available.

**Who is actually exposed — read before panicking.** The precondition is in the CVE text: *when algorithms are not explicitly restricted*. The attack needs a verifier that (a) is given an asymmetric **public** key to verify RS256/ES256 tokens and (b) calls `jwt.decode(token, public_key)` without `algorithms=["RS256"]`, so the library honours the token's own `alg: HS256` header and treats the public key bytes as the HMAC secret. Two common FastAPI shapes are **not** affected: an app that signs and verifies **HS256 with a shared secret** (the key is not an asymmetric key, so there is nothing to confuse), and an app that verifies an identity provider's RS256 tokens **with `algorithms` pinned**. FastAPI's current security tutorial installs **PyJWT**, not python-jose, and shows `algorithms=[ALGORITHM]` — but older tutorials, Stack Overflow answers and a large fraction of agent-generated `auth.py` files still `from jose import JWTError, jwt`, and the `algorithms` argument is the line most often dropped. That precondition, and the fact that it is a configuration many apps do get right, is why this advisory is **`high`** rather than the CNA's critical: the 9.3 is accurate for the vulnerable configuration and does not describe every python-jose user.

### AnyIO — CVE-2026-63374 (critical score, fixed)

[GHSA-82r6-8w77-94w6](https://github.com/agronholm/anyio/security/advisories/GHSA-82r6-8w77-94w6) (vendor advisory, 2026-07-07; CVE record by GitHub-as-CNA 2026-09-22; CVSS 4.0 **9.3**): "Prior to 4.14.2, `connect_tcp()` and `TLSStream.wrap()` can validate internationalized host names after the standard library converts them with IDNA 2003 instead of IDNA 2008. When a connection to a non-ASCII domain is hijacked or redirected, an attacker can obtain a legitimate certificate" for the IDNA-2003 encoding of the name and have it pass validation. Fixed in **4.14.2** (PR #1208); `pip index versions anyio` shows 4.15.1 current. AnyIO sits under Starlette, FastAPI's test client, httpx and the MCP Python SDK, so most FastAPI projects carry it transitively; the exposure needs the *target* to be an internationalised domain and the attacker on-path, which is why the CNA's 9.3 overstates it for a typical API that talks to ASCII hostnames. It is in this file because it reached the reviewed-critical `pip` listing (database 2026-09-18) two months after the fix and had never been logged here — the same backfill shape as PyJWT and tinypool.

### Why these two are one advisory

Both are **primitives**: nobody chooses them, a framework or a tutorial does, and neither shows up in an "AI tools CVE" search. Both carry a 9.3 that is right for one configuration and wrong for most. And together with [PyJWT's September batch](2026-09-pyjwt-hmac-key-confusion-token-forgery-cve-batch.md) (CVE-2026-102268: the *same* asymmetric-key-as-HMAC guard, bypassed by whitespace mutation, fixed 2.14.0) they show that the JWT algorithm-confusion guard is being re-broken across every Python JOSE library at once — and only one of the two libraries has a maintainer answering.

## Am I affected?

```bash
# which JWT library is installed, and is anyio current?
pip show python-jose anyio 2>/dev/null | grep -E '^(Name|Version)'
grep -rn "from jose\|import jose" --include=*.py . | head
# the dangerous call shape: decode with a key but no algorithms= pin
grep -rnE "jwt\.decode\([^)]*\)" --include=*.py . | grep -v "algorithms=" 
```

- `python-jose` present **and** a `jwt.decode(...)` without `algorithms=` **and** the key passed is a public key / JWKS → **forgeable today**; there is no upgrade that fixes it.
- `python-jose` present with `algorithms=["HS256"]` and a shared secret → not this bug; still migrate (unmaintained).
- `anyio` < 4.14.2 → `pip install -U anyio`; only matters if you connect to IDN hostnames, but the upgrade is free.

## If you are affected
1. **Pin algorithms on every decode today** — `jwt.decode(token, key, algorithms=["RS256"])` closes CVE-2026-85394 regardless of library version; PyJWT ≥ 2.0 already makes `algorithms` mandatory.
2. **Migrate to PyJWT ≥ 2.14.0** (`pyjwt[crypto]`), the library FastAPI's own tutorial now installs; the API is one import away.
3. If a verifier ran unpinned against a public key on an internet-facing service, assume tokens may have been forged: rotate the signing key pair (invalidating all tokens), review for sessions whose claims don't match a real login, and follow [if-your-webapp-was-compromised](../playbooks/if-your-webapp-was-compromised.md).
4. Agent-generated backend → [auditing-a-vibe-coded-repo](../playbooks/auditing-a-vibe-coded-repo.md); auth code is where generators copy the oldest tutorial.

## Prevention
- [credential-hygiene](../prevention/credential-hygiene.md) — treat "which algorithms may this verifier accept" as configuration you set, never something the token announces.
- [package-vetting-checklist](../prevention/package-vetting-checklist.md) — a security-critical dependency whose last release predates its open critical CVE, with an unanswered fix PR, fails the checklist whatever its download count.

## Sources
- [CVE Services — CVE-2026-85394](https://cveawg.mitre.org/api/cve/CVE-2026-85394) — VulnCheck CNA, published 2026-09-03: title, "through 3.5.0," CVSS 4.0 9.3 and 3.1 9.1 with vectors, the "incomplete fix for CVE-2024-33663" description, references to issue #414, the native/utils source files and GHSA-6c5p-j8vq-pqhj.
- [VulnCheck — python-jose through 3.5.0 Algorithm Confusion via DER-encoded Public Key as HMAC Secret](https://www.vulncheck.com/advisories/python-jose-through-3.5.0-algorithm-confusion-via-der-encoded-public-key-as-hmac-secret) — 2026-09-03; CWE-347; credit George Chen.
- [GitHub Advisory Database — GHSA-3qf3-8w2g-rqmx](https://github.com/advisories/GHSA-3qf3-8w2g-rqmx) — database copy, published 2026-09-03, last updated 2026-10-05: "Patched versions: None."
- [mpdavis/python-jose — issue #414](https://github.com/mpdavis/python-jose/issues/414) — opened 2026-07-06 by geo-chen; the 2026-06-04 unanswered email; the PEM/SSH-only guard description; no maintainer response visible 2026-10-07.
- [mpdavis/python-jose — PR #422](https://github.com/mpdavis/python-jose/pull/422) — opened 2026-09-16 by emgaurav, open; `is_der_format()` via ASN.1 structure; test counts; the 2026-10-07 "Any updates?" comment.
- [mpdavis/python-jose — repository](https://github.com/mpdavis/python-jose) — not archived, 1.8k stars, 23 open PRs / 100 issues on 2026-10-07; `pip index versions python-jose` → 3.5.0 latest (queried 2026-10-07).
- [FastAPI — OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) — the current tutorial installs PyJWT (`uv add pyjwt`), not python-jose; fetched 2026-10-07.
- [agronholm/anyio — GHSA-82r6-8w77-94w6](https://github.com/agronholm/anyio/security/advisories/GHSA-82r6-8w77-94w6) and the [database copy](https://github.com/advisories/GHSA-82r6-8w77-94w6) — vendor advisory 2026-07-07, CVSS 4.0 9.3, `connect_tcp()` / `TLSStream.wrap()`, fixed 4.14.2, the `idna` workaround; CWE-295/297.
- [CVE Services — CVE-2026-63374](https://cveawg.mitre.org/api/cve/CVE-2026-63374) — GitHub-as-CNA record, published 2026-09-22, the IDNA-2003 description quoted above, references to PR #1208 and the 4.14.2 release; `pip index versions anyio` → 4.15.1 (queried 2026-10-07).
- [GitHub Advisory Database — reviewed critical `pip` listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Apip+severity%3Acritical) — where both rows surfaced (python-jose 09-03, anyio 09-18); fetched 2026-10-07.
- Related in this corpus: [PyJWT September 2026 batch](2026-09-pyjwt-hmac-key-confusion-token-forgery-cve-batch.md) (the same guard, different bypass, fixed).
