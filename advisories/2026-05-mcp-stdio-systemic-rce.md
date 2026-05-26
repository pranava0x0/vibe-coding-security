---
id: 2026-05-mcp-stdio-systemic-rce
title: "Systemic MCP stdio RCE class — 200,000+ servers exposed (May 2026)"
date_disclosed: 2026-05
last_updated: 2026-05-26
severity: high
status: mitigated
ecosystems: [mcp, anthropic-mcp]
tools_affected: [any-mcp-server-using-stdio, claude-code, cursor, windsurf, gemini-cli]
tags: [mcp, rce, stdio, systemic, ox-security, supply-chain]
---

## TL;DR
OX Security disclosed a **systemic, class-level vulnerability in the Model Context Protocol's stdio transport** in May 2026. Audit of public-facing instances found 7,000 vulnerable MCP servers on public IPs running stdio transport; extrapolation puts the **total exposed population at ~200,000** servers across the ecosystem (~150M+ downloads of affected packages). Anthropic classifies it as a feature, not a bug; defenders should treat it as a class issue and harden accordingly.

## What happened
The MCP stdio transport assumes a trust boundary that doesn't actually exist in many deployments. When MCP servers are exposed network-side (or trigger-able through composition with other tools), prompt-injectable content can reach the server's stdin, and instructions interpreted there execute as the host process — Arbitrary Command Execution.

Headline numbers:
- **7,000 vulnerable servers** found on public IPs with stdio transport active.
- **~200,000 total** estimated from sampling ratios.
- **150M+ downloads** of affected MCP packages.

Three database-targeting MCPs were also disclosed by the same researcher on **2026-05-13** with concrete impact:
- **Apache Doris MCP** — unintended SQL execution. Apache issued a patch and CVE tracker.
- **Alibaba RDS MCP** — sensitive metadata exfiltration. **Alibaba declined to patch.**
- **Apache Pinot MCP** — instance takeover for internet-exposed Pinot instances.

Microsoft's own MCP server has now had **two** disclosures in this class:
- **CVE-2026-26118** — Server-Side Request Forgery in Azure MCP Server letting an authorized attacker elevate privileges over the network (patched in the March 2026 update).
- **CVE-2026-32211 (CVSS 9.1)** — **missing authentication** on a critical Azure MCP Server function: any unauthenticated network-reachable attacker can read sensitive data (config, API keys, auth tokens, project data). Published 2026-04-03; at disclosure **no patch** was available, only network-control mitigation. Same root failure as nginx-ui MCPwn — an MCP surface trusted by default.

**Named instance — Atlassian `mcp-atlassian` "MCPwnfluence" (CVE-2026-27825 + CVE-2026-27826):** Pluto Security chained two flaws in the most widely used Atlassian MCP server (**4M+ downloads, 4.4K+ stars**) into **unauthenticated RCE as root in two requests**. `mcp-atlassian`'s HTTP transport (`--transport streamable-http`) **defaults to binding `0.0.0.0` with zero authentication**, so anyone who can reach the port can invoke any tool.
- **CVE-2026-27826 (CVSS 8.2)** — SSRF: middleware honors the `X-Atlassian-Jira-Url` / `X-Atlassian-Confluence-Url` headers without validation, letting an attacker point requests at arbitrary internal destinations.
- **CVE-2026-27825 (CVSS 9.1)** — arbitrary file write: the `confluence_download_attachment` tool lacks directory-boundary enforcement, so the attacker writes content to any path the server process can reach.
- Chained (SSRF → arbitrary write of an executable/cron/config), this is unauthenticated host takeover. Affects **< 0.17.0**; fixed in **0.17.0**, which adds `validate_safe_path()` and `validate_url_for_ssrf()` (path confinement + scheme/domain allowlisting + redirect/localhost/private-IP blocking).

**Named instance — `network-ai` empty-default-secret (CVE-2026-46701):** the MCP SSE server in `network-ai` (npm) **defaults to an empty shared secret**, so its authorization check passes for everyone — an **unauthenticated cross-origin attacker can invoke any MCP tool** (and a sibling path-traversal lets it write arbitrary files on the host). Published 2026-05-21; affects **< 5.4.5**, fixed in **5.4.5**. Same root failure as the others — an MCP surface that ships **open by default** (here the "auth" is real but the default credential is blank).

**Named instance — `aws-mcp-server` unauthenticated RCE (CVE-2026-5058 + CVE-2026-5059, CVSS 9.8 each):** Two sibling **command-injection** flaws in `aws-mcp-server` let a network-reachable, **unauthenticated** attacker run arbitrary code as the server process (CWE-78). Both reside in the server's handling of the **allowed-commands list**: user-supplied strings flow into a system call without proper neutralization, so the "allowlist" is bypassable. Published 2026-04-11; tracked by Zero Day Initiative as **ZDI-26-245 / ZDI-26-246**; patches at disclosure were still pending — pull the server off the network and monitor vendor channels for a fixed release. Critically, this is *not* AWS's official "AWS API MCP" product (which has its own, separate **CVE-2026-4270** file-access-restriction bypass); `aws-mcp-server` is a popular community/third-party project. Treat as the AWS-credential analogue of the nginx-ui MCPwn class: an MCP surface shipped without auth that runs shell-style commands on input.

**Named instance — `n8n-mcp` post-auth SSRF (CVE-2026-39974):** The multi-tenant HTTP mode of **`n8n-mcp`** (a popular MCP server that exposes n8n node documentation/operations to AI assistants) takes user-controlled URLs from multi-tenant HTTP headers and issues server-side requests **without adequate validation**, **reflecting the response body back through JSON-RPC**. An authenticated attacker (valid `AUTH_TOKEN`) can read the contents of any URL the server can reach — most damagingly the **cloud instance metadata services** (AWS IMDS, GCP, Azure, Alibaba, Oracle) to harvest temporary credentials. Affects **≤ 2.47.3**, fixed in **2.47.4**, which adds SSRF protection that validates and rejects embedded-credential URLs and requests to restricted destinations. Lower severity than the unauthenticated MCP class (post-auth, no RCE), but a clean named instance of "MCP server reflects arbitrary HTTP responses back to the client."

**Named instance — `@mcpjam/inspector` zero-auth RCE (CVE-2026-23744):** the MCPJam Inspector (an MCP-server dev/debug tool) **binds `0.0.0.0` by default** and ships **no authentication** on its server-management endpoint, so any network-reachable attacker can send a crafted HTTP request that **installs and runs a malicious MCP server → RCE**, with **no user interaction**. Unlike the related CVE-2025-49596 (which bound `127.0.0.1` and needed user interaction), this one is exposed on all interfaces. Affects **≤ 1.4.2**, fixed in **1.4.3** (disclosed Feb 2026; surfaced in this sweep). Same root failure: an MCP dev surface trusted-by-default and reachable off-host.

**Named, KEV-listed instance — nginx-ui "MCPwn" (CVE-2026-33032, CVSS 9.8):** the clearest real-world example of the "MCP endpoint shipped without auth" class. nginx-ui exposes two HTTP MCP endpoints, `/mcp` and `/mcp_message`. `/mcp` requires IP-allowlisting **and** `AuthRequired()` middleware; `/mcp_message` only gets IP-allowlisting — and the **default IP allowlist is empty, which the middleware treats as "allow all."** So an unauthenticated network attacker can invoke all **12 MCP tools** (including `nginx_config_add` with auto-reload) and achieve **full nginx takeover in two HTTP requests**. ~**2,600** exposed instances (Pluto Security / Shodan), **actively exploited**, added to **VulnCheck KEV (2026-04-13)** and named in Recorded Future's most-exploited-CVE list for March 2026. Fixed in **nginx-ui 2.3.4** (2026-03-15); workaround is to add `middleware.AuthRequired()` to `/mcp_message` or flip the IP-allowlist default from allow-all to deny-all. This is an **HTTP-transport** auth-bypass rather than stdio, but it's the same root failure — an MCP surface treated as trusted-by-default.

## Am I affected?
You are exposed by the class issue if:

- You run any MCP server **listening on a network socket** (most MCPs are stdio-only by design, but composition with proxies / HTTP wrappers / web gateways changes this).
- You connect your AI tool to an MCP that exposes any of: Apache Doris, Alibaba RDS, Apache Pinot, or similar DB engines.
- You use Microsoft's **Azure MCP Server** — check against **CVE-2026-26118** (SSRF, patched) **and CVE-2026-32211** (missing auth, CVSS 9.1); restrict it to trusted networks until patched.
- You run **`mcp-atlassian` < 0.17.0** with its HTTP transport reachable (CVE-2026-27825 / -27826 / "MCPwnfluence") — it binds `0.0.0.0` with no auth by default; upgrade to **≥ 0.17.0** now.
- You run **nginx-ui < 2.3.4** with its MCP endpoint reachable (CVE-2026-33032 / "MCPwn") — patch now; it's in CISA/VulnCheck KEV and exploited in the wild.
- You run **`network-ai` < 5.4.5** (CVE-2026-46701) — its MCP SSE server ships an **empty default secret**; upgrade to **≥ 5.4.5** and set a non-empty secret.
- You run **`@mcpjam/inspector` ≤ 1.4.2** (CVE-2026-23744) — it binds `0.0.0.0` with no auth → zero-interaction RCE; upgrade to **≥ 1.4.3** and bind it to `127.0.0.1`.
- You run **`aws-mcp-server`** (community/third-party project) — CVE-2026-5058 / CVE-2026-5059 are **unauthenticated, CVSS 9.8 command-injection RCEs**; patches were pending at disclosure (2026-04-11), so remove it from any network-reachable path and watch the project + ZDI-26-245/-246 for a fixed release.
- You run **`n8n-mcp` ≤ 2.47.3** in multi-tenant HTTP mode (CVE-2026-39974) — authenticated SSRF that reflects responses back, including cloud IMDS; upgrade to **≥ 2.47.4**.

```bash
# Find MCP servers configured in your tools
cat ~/.cursor/mcp.json 2>/dev/null
cat ~/.windsurf/mcp.json 2>/dev/null
cat ~/.config/claude/*.json 2>/dev/null | grep -A2 mcp
ls ~/Library/Application\ Support/Claude/ 2>/dev/null

# Audit network-facing MCP exposure (a tool surface, not a default)
lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -iE 'mcp|model-context'
```

## If you are affected
1. **Remove any MCP server you don't actively use.** Each is attack surface.
2. **Update Microsoft Azure MCP server** if you run it (CVE-2026-26118 + CVE-2026-32211); until patched for the latter, put it behind network ACLs / a reverse proxy that enforces auth.
3. **Update `mcp-atlassian` to ≥ 0.17.0** (MCPwnfluence, CVE-2026-27825/-27826); never expose its HTTP transport on `0.0.0.0` without an auth proxy. Pluto Security ships a [detection/auto-update script](https://github.com/plutosecurity/MCPwnfluence).
4. **Update nginx-ui to ≥ 2.3.4** (CVE-2026-33032 / MCPwn), or add `middleware.AuthRequired()` to `/mcp_message` and set the IP allowlist to deny-all.
5. **Update `@mcpjam/inspector` to ≥ 1.4.3** (CVE-2026-23744) and never run an MCP inspector/dev tool bound to `0.0.0.0`; keep it on `127.0.0.1`.
5a. **For `aws-mcp-server` (CVE-2026-5058 / -5059):** treat as unfixed-in-the-wild. Remove from any reachable network path; restrict to loopback; rotate AWS credentials that were exposed to the host. Track ZDI-26-245 / -246 for the vendor patch.
5b. **Update `n8n-mcp` to ≥ 2.47.4** (CVE-2026-39974). Until upgraded, block egress from the MCP host to cloud IMDS endpoints (`169.254.169.254`, `metadata.google.internal`, etc.) and restrict `AUTH_TOKEN` to trusted callers.
6. **For Apache Doris MCP:** apply the patch + the CVE tracker recommendations.
7. **For Alibaba RDS MCP:** since Alibaba declined to patch, do not deploy without an isolating proxy that filters MCP messages.
8. **Do not expose stdio MCPs to network sockets.** If you've wrapped one with a proxy / HTTP gateway, audit the proxy's input validation.
9. **Run MCP servers as their own unprivileged user**, in a container with read-only credentials, on a host with strict egress allowlists.

## The OX Security framing
OX Security calls this "The Mother of All AI Supply Chains" — making the case that the MCP standard's permissive trust posture is a *systemic* risk, not an implementation bug. Anthropic disagrees, arguing the protocol assumes explicit user trust in installed servers.

**Practically, both can be right.** The protocol is what it is. Defenders must treat MCP installation as equivalent to `npm install -g` of arbitrary code — because that's what it functionally is. → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources
- [OX Security — The Mother of All AI Supply Chains: Critical, Systemic Vulnerability at the Core of MCP](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/)
- [VentureBeat — 200,000 MCP servers expose a command execution flaw that Anthropic calls a feature](https://venturebeat.com/security/mcp-stdio-flaw-200000-ai-agent-servers-exposed-ox-security-audit)
- [The Register — Bug hunter tracks down three massive MCP flaws and one vendor won't fix theirs](https://www.theregister.com/security/2026/05/13/bug-hunter-tracks-down-three-serious-mcp-database-flaws-one-left-unpatched/5238916)
- [The Hacker News — Anthropic MCP Design Vulnerability Enables RCE, Threatening AI Supply Chain](https://thehackernews.com/2026/04/anthropic-mcp-design-vulnerability.html)
- [Tom's Hardware — Anthropic's Model Context Protocol includes a critical RCE vulnerability](https://www.tomshardware.com/tech-industry/artificial-intelligence/anthropics-model-context-protocol-has-critical-security-flaw-exposed)
- [Bitsight — Exposed MCP Servers: New AI Vulnerabilities & What to Do](https://www.bitsight.com/blog/exposed-mcp-servers-reveal-new-ai-vulnerabilities)
- [PointGuard AI — Microsoft MCP Server Vulnerability (CVE-2026-26118)](https://www.pointguardai.com/ai-security-incidents/microsoft-mcp-server-vulnerability-opens-door-to-ai-tool-hijacking-cve-2026-26118)
- [Adversa AI — Top MCP security resources — May 2026](https://adversa.ai/blog/top-mcp-security-resources-may-2026/)
- [The Hacker News — Actively Exploited nginx-ui Flaw (CVE-2026-33032) Enables Full Nginx Server Takeover](https://thehackernews.com/2026/04/critical-nginx-ui-vulnerability-cve.html)
- [Picus Security — CVE-2026-33032 (MCPwn): How a Missing Middleware Call in nginx-ui Hands Attackers Full Web Server Takeover](https://www.picussecurity.com/resource/blog/cve-2026-33032-mcpwn-how-a-missing-middleware-call-in-nginx-ui-hands-attackers-full-web-server-takeover)
- [Endor Labs — CVE-2026-33032, nginx-ui's Unauthenticated MCP Endpoint Allows Remote Nginx Takeover](https://www.endorlabs.com/vulnerability/cve-2026-33032)
- [BleepingComputer — Critical Nginx UI auth bypass flaw now actively exploited in the wild](https://www.bleepingcomputer.com/news/security/critical-nginx-ui-auth-bypass-flaw-now-actively-exploited-in-the-wild/)
- [Pluto Security — MCPwnfluence: Critical Unauthenticated SSRF to RCE in the Most Widely Used Atlassian MCP Server](https://pluto.security/blog/mcpwnfluence-cve-2026-27825-critical/) — canonical research, attack chain, fixed version.
- [Arctic Wolf — CVE-2026-27825: Critical Unauthenticated RCE and SSRF in mcp-atlassian](https://arcticwolf.com/resources/blog-uk/cve-2026-27825-critical-unauthenticated-rce-and-ssrf-in-mcp-atlassian/)
- [GitHub — plutosecurity/MCPwnfluence (detection + auto-update script)](https://github.com/plutosecurity/MCPwnfluence)
- [GitHub Advisory Database — CVE-2026-26118: Azure MCP Server SSRF privilege escalation](https://github.com/advisories/GHSA-hhfx-wfvq-7g9c)
- [Windows News — CVE-2026-32211: Critical Azure MCP Server Authentication Flaw (CVSS 9.1)](https://windowsnews.ai/article/cve-2026-32211-critical-azure-mcp-server-authentication-flaw-exposes-sensitive-data-cvss-91.409622)
- [GitLab Advisory Database — CVE-2026-46701: network-ai Unauthenticated Cross-Origin MCP Tool Invocation via Empty Default Secret](https://advisories.gitlab.com/npm/network-ai/CVE-2026-46701/)
- [GitHub Advisory Database — CVE-2026-23744: RCE in MCPJam inspector due to exposed HTTP endpoint (GHSA-232v-j27c-5pp6)](https://github.com/advisories/GHSA-232v-j27c-5pp6)
- [The Vulnerable MCP Project — MCPJam Inspector RCE (CVE-2026-23744)](https://vulnerablemcp.info/vuln/cve-2026-23744-mcpjam-inspector-rce.html) — binds 0.0.0.0, no auth, no user interaction; fixed 1.4.3.
- [SentinelOne — CVE-2026-5058: aws-mcp-server RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-5058/) — unauthenticated command injection in allowed-commands handling, CVSS 9.8.
- [SentinelOne — CVE-2026-5059: aws-mcp-server Command Injection RCE Flaw](https://www.sentinelone.com/vulnerability-database/cve-2026-5059/) — sibling vulnerability, same root cause.
- [NVD — CVE-2026-5058](https://nvd.nist.gov/vuln/detail/CVE-2026-5058)
- [NVD — CVE-2026-5059](https://nvd.nist.gov/vuln/detail/CVE-2026-5059)
- [TheHackerWire — aws-mcp-server Remote Code Execution via Command Injection (CVE-2026-5058)](https://www.thehackerwire.com/aws-mcp-server-remote-code-execution-via-command-injection-cve-2026-5058/) — exploit context, ZDI-CAN-27968 attribution.
- [Zero Day Initiative — ZDI-26-245](https://www.zerodayinitiative.com/advisories/ZDI-26-245/) — ZDI tracking for the aws-mcp-server RCE cluster.
- [SentinelOne — CVE-2026-39974: n8n-MCP Server SSRF Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-39974/) — post-auth SSRF, IMDS targeting, fixed in 2.47.4.
- [NVD — CVE-2026-39974](https://nvd.nist.gov/vuln/detail/CVE-2026-39974)
- [Shenlong CVE Platform — n8n-mcp Post-Auth SSRF Vulnerability and Mitigation Guide](https://cve.imfht.com/intel/579223?lang=en) — mitigation specifics, version range.
