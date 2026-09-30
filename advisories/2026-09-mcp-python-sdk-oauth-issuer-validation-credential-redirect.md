---
id: 2026-09-mcp-python-sdk-oauth-issuer-validation-credential-redirect
title: "Official MCP Python SDK (`mcp` 1.9.1–1.29.1, 2.0.0–2.1.1): the OAuth client let the MCP server choose the authorization server, so a malicious or compromised server received the client secret, authorization code, PKCE verifier or signed assertion meant for the real login provider (GHSA-qx49-fqc8-xw99, CVSS 7.5); fixed 1.30.0 / 2.2.0 — and two providers need an explicit issuer= after upgrading"
date_disclosed: 2026-09-28
last_updated: 2026-09-30
severity: high
status: patched
ecosystems: [pypi, mcp, python]
tools_affected: ["mcp (modelcontextprotocol/python-sdk) OAuthClientProvider", "ClientCredentialsOAuthProvider", "PrivateKeyJWTOAuthProvider", "deprecated 1.x RFC7523OAuthClientProvider", "every MCP client, agent and gateway built on the Python SDK that connects to remote HTTP MCP servers with OAuth"]
tags: [cve-pending, ghsa, mcp, oauth, account-takeover, credential-theft, issuer-validation, sdk, silent-fix, configuration-required-after-upgrade]
---

## TL;DR

The reference Python implementation of the Model Context Protocol shipped an OAuth client that **did not check who the authorization server was**. An MCP server the client connected to could name its own authorization server in its protected-resource metadata — or publish none and serve metadata that presented the user's real provider as the issuer on a fallback path — and the SDK would send that server the **client secret, the authorization code, the PKCE `code_verifier`, or the signed JWT assertion** it should only ever have sent to the real login provider. That is account takeover of whatever the client used those credentials for. The vendor advisory (published **2026-09-28**) rates it **High, CVSS 7.5** for the unattended providers and 6.5 for the interactive one; there is no CVE yet. Fixes are **`mcp` 1.30.0 and 2.2.0** — both on PyPI since **2026-09-07**, three weeks before disclosure, with the issuer checks listed in release notes as behaviour changes. **Upgrading alone is not enough** for `ClientCredentialsOAuthProvider` and `PrivateKeyJWTOAuthProvider`: you must pass `issuer=`, or the check has nothing to compare against until 3.0 makes the argument mandatory. Servers built on the SDK, stdio clients, and clients that manage their own tokens are not affected.

## What happened

The SDK's OAuth client support performs discovery: connect to an MCP server, read its protected-resource metadata to learn which authorization server to use, fetch that server's metadata, then run the flow. The advisory describes two gaps:

- **1.9.1 through 1.29.1** — no issuer validation and no credential binding on *any* discovery path. The MCP server decides where credentials go.
- **2.0.0 through 2.1.1** — checks were added on the main path but were **missing on the 404-fallback path and the 403 step-up path**. Cycode's write-up: "when a malicious MCP server returns a 404 to discovery requests, the SDK never verifies the login provider's identity before accepting its configuration."

Impact by provider (advisory wording): a compromised or malicious server "could intercept client secrets, authorization codes, PKCE verifiers, or signed assertions by either advertising its own authorization server or manipulating metadata responses." For the **interactive** `OAuthClientProvider` the user must complete a login, hence 6.5; for the **unattended** `ClientCredentialsOAuthProvider` and `PrivateKeyJWTOAuthProvider` the credential is sent with no interaction, hence 7.5. The deprecated 1.x `RFC7523OAuthClientProvider` is in the affected list too.

Who this reaches: every MCP *client* built on the Python SDK that talks to remote HTTP servers with OAuth — agent frameworks, gateways, and the "connect your agent to this SaaS" integrations that hold a real client secret for the SaaS. Connecting to one untrusted or later-compromised MCP server was enough. **Not affected:** MCP servers built with the SDK, stdio transports, and clients that obtain and manage tokens themselves.

Timeline, as the sources state it: reported through Anthropic's security process by eight researchers (credited on the advisory); **1.30.0 and 2.2.0 published 2026-09-07** (PyPI upload dates confirmed this sweep) with the issuer checks described as behaviour changes rather than a security fix; **vendor advisory and Cycode's analysis on 2026-09-28**; The Hacker News on 09-29. No exploitation is reported. Note the pattern this repo keeps recording: a three-week window in which the fix was public, the reason was not, and anyone pinning an older `mcp` had no signal to move.

The TypeScript SDK's advisory tab (checked 2026-09-30) carries no equivalent entry; that is not evidence it is unaffected, only that nothing has been published.

## Am I affected?

```bash
# Which mcp is installed, and does anything you run use an OAuth provider?
pip show mcp 2>/dev/null | grep -i '^version'
pip index versions mcp | head -1                     # 2.2.0 is latest as of 2026-09-30
grep -rn "OAuthClientProvider\|ClientCredentialsOAuthProvider\|PrivateKeyJWTOAuthProvider\|RFC7523OAuthClientProvider" --include=*.py . | head

# Affected: 1.9.1 <= mcp <= 1.29.1, or 2.0.0 <= mcp <= 2.1.1, AND one of the providers above is used
# AND the client connects over HTTP to servers you do not fully control.
# After upgrading: do the two unattended providers pass issuer=?
grep -rn "ClientCredentialsOAuthProvider(\|PrivateKeyJWTOAuthProvider(" --include=*.py -A6 . | grep -c "issuer="
```

Stored client registrations from before the upgrade were made under the old rules; the advisory says to clear them.

## If you are affected

1. Upgrade to **`mcp` ≥ 2.2.0** (or ≥ 1.30.0 on the 1.x line).
2. **Add `issuer="https://<your-real-authorization-server>"`** to every `ClientCredentialsOAuthProvider` and `PrivateKeyJWTOAuthProvider` — without it the patched versions emit a deprecation warning and the binding is incomplete; 3.0 will refuse to start without it.
3. **Clear stored OAuth client registrations** so clients re-register against a validated issuer.
4. If the client ever connected to an MCP server you did not control: **rotate the client secret, rotate the private key behind the JWT assertion, and revoke tokens** at the real provider — the credential may already be in someone else's hands. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Treat every remote MCP server as an attacker-controlled peer in the OAuth flow: the client must **pin the issuer** and bind credentials to it, never learn it from the resource it is about to authenticate to. This is the client-side twin of the [mcp-remote discovery SSRF batch](2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md) and the [Obot dynamic-client-registration bug](2026-08-agent-framework-mcp-cve-batch.md) — the same protocol edge, three implementations.
- Keep `mcp` on latest, unpinned within a major: the fix shipped 21 days before the advisory did.
- Give agent integrations **per-server client credentials** so a compromised server can only redeem its own; see [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

- [modelcontextprotocol/python-sdk — GHSA-qx49-fqc8-xw99: OAuth client could send credentials to an authorization server chosen by the MCP server](https://github.com/modelcontextprotocol/python-sdk/security/advisories/GHSA-qx49-fqc8-xw99) — vendor advisory, published 2026-09-28: High / CVSS 7.5, the two affected ranges, patched 1.30.0 / 2.2.0, the provider list, the `issuer=` requirement and 3.0 note, the clear-registrations and rotate guidance, eight credited reporters. Fetched 2026-09-30.
- [Cycode — MCP SDK OAuth Flaw Enabled Account Takeover](https://cycode.com/blog/mcp-python-sdk-oauth-account-takeover/) — researcher analysis, 2026-09-28: the 404-fallback and 403 step-up paths, "no issuer validation or credential binding on any path" for 1.x, 7.5 vs 6.5 rationale, the "reported through Anthropic's security process" note. Fetched 2026-09-30.
- [The Hacker News — Official MCP Python SDK Flaw Can Let Malicious Servers Steal OAuth Credentials](https://thehackernews.com/2026/09/official-mcp-python-sdk-flaw-can-let.html) — 2026-09-29: the 09-07 release-notes-as-behaviour-change detail, the version table, "no attacks exploiting this flaw reported to date." Fetched 2026-09-30.
- PyPI `mcp` release metadata (`pypi.org/pypi/mcp/json`, queried 2026-09-30): 1.29.1 uploaded 2026-08-24, 2.1.1 2026-08-25, **1.30.0 and 2.2.0 both 2026-09-07**; latest 2.2.0.
- [modelcontextprotocol/typescript-sdk — security advisories](https://github.com/modelcontextprotocol/typescript-sdk/security/advisories) — checked 2026-09-30: three entries (Dec 2025 – Feb 2026), none about OAuth issuer validation.
- Related in this corpus: [mcp-remote OAuth-discovery SSRF CVE batch](2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md), [Bifrost unauthenticated client registration](2026-09-bifrost-mcp-client-registration-unauth-rce.md), [systemic MCP stdio RCE](2026-05-mcp-stdio-systemic-rce.md).
