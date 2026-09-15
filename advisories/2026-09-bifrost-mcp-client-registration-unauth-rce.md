---
id: 2026-09-bifrost-mcp-client-registration-unauth-rce
title: "Bifrost (8K-star Go AI gateway) — one unauthenticated POST /api/mcp/client registers a stdio MCP client and runs it as the gateway process (CVE-2026-90898, CVSS 9.8); authentication is off by default"
date_disclosed: 2026-09-14
last_updated: 2026-09-15
severity: critical
status: patched
ecosystems: [go, ai-gateways, llm-routers, mcp, self-hosted]
tools_affected: [bifrost, "maximhq/bifrost", "any AI coding agent or app routing model calls through a self-hosted Bifrost"]
tags: [cve, rce, missing-authentication, mcp, ai-gateway, llm-router, credential-theft, default-config, ssrf]
---

## TL;DR
**Bifrost** (Maxim AI, Go, ~8.1K GitHub stars) is a self-hosted AI gateway that fronts "23+ providers" behind one OpenAI-compatible endpoint and can attach MCP servers as tools. Its management API registers MCP clients, and a **stdio** MCP client is a command plus arguments that Bifrost **starts the moment the client is added — no MCP handshake required**. The default configuration ships with `governance.auth_config.is_enabled=false`, which the disclosing researchers summarise as "every caller is a local admin." So **one unauthenticated `POST /api/mcp/client`** runs an attacker's program as the Bifrost process user (`appuser` on the official image), inside the container that holds every provider key you configured. **CVE-2026-90898**, CVSS 3.1 **9.8** (`AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`), CNA JFrog, published 2026-09-14. Fixed in **transports/v2.1.0** (released 2026-09-08): unauthenticated callers can no longer register stdio clients or private-address targets. Upgrade, turn authentication on, and rotate the keys.

## What happened

JFrog Security Research (advisory JFSA-2026-001686326, published 2026-09-14, JFrog acting as CNA) found that Bifrost's MCP client-registration endpoint enforced no authentication when the governance auth flag was off — which is the shipped default. Registering a client of type stdio hands the gateway a command line; Bifrost launches it immediately to establish the MCP connection, so registration *is* execution. No valid MCP server needs to answer, and nothing about the request requires an existing session.

Two properties combine, the same two that turned [OmniRoute's ACP endpoint](2026-09-omniroute-acp-agent-unauth-rce.md) into a one-request RCE eleven days earlier:

- **Auth is opt-in.** The project's quick-start is "zero-config startup" with a built-in web UI; the enterprise OIDC/OAuth login is a feature you enable. With `governance.auth_config.is_enabled=false`, the management API treats anonymous callers as administrators.
- **The dangerous capability is one API call away from the network.** An MCP stdio client definition is a command line. Any product that lets a network caller add one has a remote-execution feature; the only question is who may call it.

**What the fix does.** Bifrost PR #6757 (merged for the transports/v2.1.0 release, 2026-09-08 per the release page) — described in the release notes as "SSRF Hardening for MCP" — makes the gateway refuse unauthenticated stdio registrations with a 403, refuse unauthenticated registrations that point at private addresses, route all MCP HTTP-client dials through the SSRF guard, and block the Teredo (IPv6 tunnelling) prefix. NVD's record states the point plainly: "Version 2.1.0 addresses this by enforcing authentication; version 2.0.0 remains vulnerable." JFrog's affected range is "before 2.1.0, including the entire 1.6.x line through 1.6.11." Note that with authentication enabled, an *authenticated administrator* can still register stdio clients — that is the feature working as designed; treat admin credentials for the gateway as equivalent to shell on the gateway host.

**Version naming.** Bifrost tags its HTTP transport releases as `transports/vX.Y.Z`; the fixed tag is `transports/v2.1.0`. The GitHub Advisory Database's copy (GHSA-gqjq-cgxr-8c7c) lists no package and no version range because the module is Go and the DB entry is CVE-sourced — do not read its empty "patched versions" field as "no fix."

**Context from the vendor's own advisory tab.** Bifrost had published one earlier advisory, GHSA-w98g-5w9p-p3rc (2026-07-21, High): its SSRF deny-list `isPublicIP` permitted CGNAT, 6to4/NAT64 and site-local ranges in `FetchAndEncodeURL`. The v2.1.0 dial-time guard closes the family rather than the instance.

**Impact for this audience.** A gateway exists to hold provider keys and sit in the request path of every model call an agent makes. Code execution in it yields the key ring, the ability to read or rewrite prompts and completions in transit, and — because MCP clients are configured *in* the gateway — the tool surface the connected agents trust. This is the third self-hosted AI gateway in this repo with an unauthenticated-by-default control plane in five months ([LiteLLM](2026-04-litellm-sql-injection.md), [OmniRoute](2026-09-omniroute-acp-agent-unauth-rce.md), now Bifrost), and the second where the unauthenticated primitive is "register an MCP server."

No exploitation in the wild is reported by JFrog or NVD as of 2026-09-15.

## Am I affected?

```bash
# Version — the fixed HTTP transport release is transports/v2.1.0
docker images | grep -i bifrost; bifrost-http --version 2>/dev/null
# Is governance auth on?  (config.json / env vary by install — look for the flag)
grep -rn 'is_enabled\|auth_config' config.json ~/.bifrost* /app/data 2>/dev/null
# Is the management API reachable beyond loopback?
ss -tlnp 2>/dev/null | grep -i bifrost
# Any MCP clients you did not add?  (management API; adjust host/port)
curl -s http://127.0.0.1:8080/api/mcp/clients 2>/dev/null
```

You are affected if you ran any Bifrost HTTP transport below 2.1.0 (including 1.6.x) with `governance.auth_config.is_enabled=false` — the default — anywhere a browser, a LAN host, a mesh peer or the internet could reach the management port. A deployment that only ever bound to `127.0.0.1` on a single-user machine is still exposed to a DNS-rebinding page unless the UI enforces an origin/host check; treat "local" as a weak boundary.

## If you are affected

1. Upgrade to **transports/v2.1.0 or later**, enable governance authentication with strong credentials, and restrict the management API to trusted networks.
2. **Rotate every provider key the gateway held** — OpenAI, Anthropic, Bedrock, Vertex and the rest — and any virtual keys Bifrost issued to clients. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
3. List the registered MCP clients and remove anything you did not add; inspect the container for unexpected processes and modified config or database state. → [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
4. If the instance was reachable from the internet, treat the host as compromised. → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

- → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — an MCP stdio definition is a command line; the ability to add one is the ability to run code. Gate it behind the strongest auth the product has, and behind the network.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — scope provider keys per gateway and cap spend, so a compromised gateway is a bounded loss.
- Never run an AI gateway with authentication off outside a throwaway sandbox; "zero-config" quick-starts are for evaluation, not for the box that holds your keys.

## Sources

- [JFrog Security Research — Bifrost is vulnerable to Unauthenticated Remote Code Execution via MCP Stdio Client Registration (JFSA-2026-001686326, CVE-2026-90898)](https://research.jfrog.com/vulnerabilities/bifrost-is-vulnerable-to-unauthenticated-remote-code-execution-via-mcp-stdio-client-registration-cve-2026-90898/) — fetched 2026-09-15; primary: published 2026-09-14, CVSS 9.8, affected "before 2.1.0 including 1.6.x through 1.6.11," the default `governance.auth_config.is_enabled=false`, mitigation guidance.
- [NVD — CVE-2026-90898](https://nvd.nist.gov/vuln/detail/CVE-2026-90898) — fetched via the NVD API 2026-09-15; published 2026-09-14, CNA `reefs@jfrog.com`, CVSS 3.1 9.8 vector, CWE-284/306, references to the fix commit, PR #6757 and the transports/v2.1.0 release.
- [Bifrost — transports/v2.1.0 release](https://github.com/maximhq/bifrost/releases/tag/transports/v2.1.0) — fetched 2026-09-15; released 2026-09-08: "SSRF Hardening for MCP (PR #6757): unauthenticated callers cannot register stdio MCP clients or private addresses, all MCP HTTP clients dial through the SSRF guard, and the Teredo prefix is blocked."
- [GitHub Advisory Database — GHSA-gqjq-cgxr-8c7c (CVE-2026-90898)](https://github.com/advisories/GHSA-gqjq-cgxr-8c7c) — fetched 2026-09-15; CVE-sourced copy published 2026-09-14, no package/version fields populated.
- [Bifrost — repository](https://github.com/maximhq/bifrost) and [security advisories index](https://github.com/maximhq/bifrost/security/advisories) — fetched 2026-09-15; the "50x faster than LiteLLM" tagline, ~8.1K stars, Go, 23+ providers, MCP tool support, "zero-config startup"; one prior advisory (GHSA-w98g-5w9p-p3rc, 2026-07-21, incomplete SSRF deny-list).
