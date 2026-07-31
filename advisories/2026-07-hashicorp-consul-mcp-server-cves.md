---
id: 2026-07-hashicorp-consul-mcp-server-cves
title: "HashiCorp Consul MCP Server — SSRF and cross-tenant credential-reuse CVEs (CVE-2026-16328, CVE-2026-16326)"
date_disclosed: 2026-07-29
last_updated: 2026-07-29
severity: high
status: patched
ecosystems: [mcp]
tools_affected: ["consul-mcp-server"]
tags: [cve, mcp, ssrf, credential-theft, cross-tenant, hashicorp]
---

## TL;DR

HashiCorp's own **consul-mcp-server** — the official Model Context Protocol server for its Consul service-mesh/service-discovery product — shipped two vulnerabilities patched in **0.1.4** (versions 0.1.0–0.1.3 affected): an **SSRF** (CVE-2026-16328, CVSS 8.6) that lets a connected MCP client override the server's configured Consul backend address and exfiltrate the server's Consul token, and a **cross-tenant credential-reuse** bug (CVE-2026-16326) that, in stateless deployment mode, can let one client's authenticated Consul session be reused for a different client's requests. Update to 0.1.4 if you run this MCP server.

## What happened

HashiCorp disclosed both issues in security bulletin **HCSEC-2026-24** on **2026-07-29** ([HashiCorp Discuss](https://discuss.hashicorp.com/t/hcsec-2026-24-multiple-vulnerabilities-impacting-hashicorp-consul-mcp-server/77612)).

**CVE-2026-16328 (SSRF, CVSS 8.6, High)** — `consul-mcp-server` did not validate the Consul backend address a connected client could supply via request header, allowing that client to **redirect the server's own Consul API traffic to an attacker-controlled endpoint** — and, in the process, potentially exfiltrate the Consul token the server was configured with. Confirmed directly on [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-16328): CVSS 3.1 vector `AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N`, published 2026-07-29.

**CVE-2026-16326 (Cross-tenant credential reuse)** — in the server's **stateless operation mode**, per-client session state was not properly isolated, so one client's Consul authentication token could end up being used to serve a different client's requests when multiple clients connect concurrently.

Both affect `consul-mcp-server` **0.1.0 through 0.1.3**; both are fixed in **0.1.4**.

## Am I affected?

```bash
# Check your consul-mcp-server version
consul-mcp-server --version 2>/dev/null
npm ls consul-mcp-server 2>/dev/null
```

You're affected if you run `consul-mcp-server` below 0.1.4. The SSRF (CVE-2026-16328) is reachable by any client connected to the server; the cross-tenant issue (CVE-2026-16326) only matters if you run the server in stateless mode with more than one concurrent client.

## If you are affected

1. Upgrade to `consul-mcp-server` **0.1.4**.
2. Rotate the Consul token the server was configured with, since the SSRF could have exfiltrated it to an attacker-controlled endpoint before you patched.
3. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

This fits this repo's standing "MCP servers are unauthenticated network services by default" pattern: an MCP server that proxies a backend API and holds a privileged token for it needs the same input-validation discipline as any other network service accepting client-supplied destination addresses. See [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) and [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources

- [HashiCorp Discuss — HCSEC-2026-24: Multiple Vulnerabilities Impacting HashiCorp Consul MCP Server](https://discuss.hashicorp.com/t/hcsec-2026-24-multiple-vulnerabilities-impacting-hashicorp-consul-mcp-server/77612) — primary vendor advisory, published 2026-07-29: both CVE descriptions, affected/fixed versions.
- [NVD — CVE-2026-16328](https://nvd.nist.gov/vuln/detail/CVE-2026-16328) — canonical CVE record, published 2026-07-29: CVSS 8.6 (AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:N/A:N), SSRF description confirming the vendor advisory.
