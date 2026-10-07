---
id: 2026-10-mcp-protocol-pivoting-ssrf-same-flaw-google-toolbox-jpmorgan-dinum-five-vendors
title: "\"Protocol pivoting\": one researcher's SSRF pattern — an MCP server fetches whatever URL the agent (or the data it reads) hands it — confirmed and fixed at Google (MCP Toolbox CVE-2026-14540, 8.0), JPMorgan Chase, Weaviate, France's DINUM and an Indonesian city government, with a Rapid7 MCP GraphQL injection alongside and five US federal MCP servers still in triage (update published 2026-10-05)"
date_disclosed: 2026-10-05
last_updated: 2026-10-07
severity: high
status: patched
ecosystems: [mcp, go, python, ai-agents]
tools_affected: ["Google MCP Toolbox for Databases (mcp-toolbox 0.3.0–1.4.0)", "JPMorgan Chase documentation-search MCP server (jpmorgan-payments/ai)", "Weaviate Google module", "datagouv/datagouv-mcp (France, DINUM)", "INFOKOM-KI/Wazuh-MCP-Server (Tangerang City, Indonesia)", "Rapid7 Bulk Export MCP 0.2.5–0.6.1", "any MCP server with a URL-, path- or endpoint-taking tool"]
tags: [mcp, ssrf, cross-vendor-pattern, dns-rebinding, cloud-metadata, agent-to-agent, prompt-injection, cve, researcher-disclosure]
---

## TL;DR
Independent researcher **Syed Anas Mohiuddin** published a four-months-later update on 2026-10-05 to his "Protocol Pivoting" work: the same server-side request forgery mistake — an MCP server builds an outbound HTTP request from a URL, path or endpoint that an agent supplies, without checking where it resolves — has now been **confirmed and fixed by five unrelated organisations**: Google's **MCP Toolbox for Databases** (CVE-2026-14540, CVSS 4.0 8.0, versions 0.3.0–1.4.0, fixed 1.5.0 on 2026-06-18), **JPMorgan Chase**'s documentation-search MCP server, **Weaviate**'s Google module, **France's DINUM** `datagouv-mcp` (fixed 2026-09-04) and **Tangerang City**'s Wazuh MCP server (advisory 2026-09-03). A sixth, Rapid7's Bulk Export MCP, had a GraphQL query injection through an unvalidated tool argument (CVE-2026-97228, 2.7). Five **US federal MCP servers** under GSA's Technology Transformation Services were reported privately on 2026-09-02 and, per the researcher as relayed by two outlets, remain in triage. The lesson for anyone wiring an agent to a "fetch this URL" tool: the server's network identity — its VPC, its cloud-metadata endpoint, its internal services — becomes the agent's, and the agent's input is whatever the last web page said.

## What happened

**The class.** Mohiuddin's May 2026 preprint named "protocol pivoting": injected text that one agent reads as data arrives at the next hop (an MCP tool call, an A2A task) as an instruction, and a server-side tool then performs it with the server's privileges. The October update reports the concrete, boring form that keeps recurring: an MCP tool takes a URL (a documentation link, an OpenAPI spec location, a "check this webshell" target, a configurable API endpoint) and the server fetches it. No allowlist, no resolution-time IP check, redirects followed, so loopback, RFC1918 ranges and `169.254.169.254` are all one tool call away. The outlets that covered the update both quote the researcher's view that the bug is **structural** — the same mistake in servers written by teams sharing no code, industry, country or owner.

**The confirmed rows.** Each is from the primary record this sweep opened; where only outlet coverage was available, that is stated.

| Organisation / product | What the tool did | Record | Fix |
|---|---|---|---|
| **Google — MCP Toolbox for Databases** (`googleapis/mcp-toolbox`, formerly `genai-toolbox`) | The generic HTTP source and tool built requests from configured/parameterised URLs; the HTTP client "fails to safely regulate request redirection boundaries" (no restrictive redirect policy, no target-IP check) | **CVE-2026-14540**, CNA Google, published 2026-07-31; CVSS 4.0 **8.0** (`AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H`); affected **0.3.0 through 1.4.0** | PR #3448 "fix(source/http): implement SSRF guard" — DNS-rebinding (TOCTOU) protection, `allowPrivateNetworks` / `allowedIpRanges` / `customBlockedIpRanges`, early BaseURL validation; opened 06-16, merged **2026-06-18**, shipped **1.5.0** the same day |
| **JPMorgan Chase** — documentation-search MCP server in `jpmorgan-payments/ai` | Two URL-fetching tools validated inconsistently; one fetched unprotected | No CVE; reported through JPMC's Responsible Disclosure team; researcher rates it Medium (outlet-relayed) | Deployed fix confirmed (outlet-relayed) |
| **Weaviate** — Google module | Module API endpoint setting was unrestricted, so a configured endpoint could point anywhere | No CVE; Security Hall of Fame listing (outlet-relayed) | Restricted to Google API hosts; merged **2026-08-25** (outlet-relayed) |
| **France — DINUM, `datagouv/datagouv-mcp`** (official MCP server for data.gouv.fr) | `get_dataservice_openapi_spec` made unvalidated GET requests to the `machine_documentation_url` field that *data producers* supply — i.e. any dataset publisher could aim the government's MCP server at an internal address | PR #126 "SSRF hardening for external APIs," reporter credited | Merged **2026-09-04**: HTTP/HTTPS only, destination IP validated at connect time incl. IPv6-mapped forms, every redirect hop re-validated, proxies blocked |
| **Indonesia — Tangerang City, `INFOKOM-KI/Wazuh-MCP-Server`** | `blueteam_check_webshell` advertised "SSRF Protection: Private/reserved IPs in the URL host are rejected" but only rejected literal IPs; a hostname skipped validation and `curl` resolved it (wildcard-DNS services, attacker domains, redirect chains) — response exfiltration up to 1,500 characters | **GHSA-pw2j-pj4h-f5vg** on the vendor's tab, High, no CVE, published **2026-09-03**, reporter credited | Commit 2bbfe12 (vendor advisory) |
| **Rapid7 — Bulk Export MCP** | `export_id`, an unvalidated MCP tool argument reaching `get_export_status` via the `check_rapid7_export_status` / `download_rapid7_export` tools, interpolated into a GraphQL query | **CVE-2026-97228**, CNA Rapid7, published 2026-09-25; CVSS 3.1 **2.7** (`PR:H`); affected **0.2.5 through 0.6.1** | **0.6.2** |

**Still open, per the researcher via the outlets.** Five findings filed 2026-09-02 as private GitHub Security Advisories against US federal MCP servers under GSA TTS — Veterans Affairs benefits-claims, CMS Blue Button, regulations.gov, USASpending, CDC PLACES — "remain in triage, are not fixed, and are not presented as confirmed outcomes" (the researcher's own caveat as quoted by Unite.AI). TNW adds an unauthenticated Japan Digital Agency grants server as a further open item. This advisory does not restate them as confirmed vulnerabilities, and it does not name endpoints.

**Why the Google row matters most for this audience.** MCP Toolbox for Databases is the server coding agents are pointed at to give them Postgres/MySQL/BigQuery access, and this is its **third** CVE in this corpus: CVE-2026-19202 (cross-audience ID-token cache, 9.1) and CVE-2026-102242 (lexical `allowedLocalRoots` check, 8.6) are in [the agent-framework MCP batch](2026-08-agent-framework-mcp-cve-batch.md). Neither `googleapis/mcp-toolbox` nor `googleapis/mcp-toolbox-sdk-python` publishes anything on its GitHub security tab ("There aren't any published security advisories," both checked 2026-10-07); Google's CNA records are the only vendor channel, and this one sat untracked here for nine weeks.

**What is not established.** Nobody reports exploitation in the wild. The researcher's own update page returned HTTP 403 to this sweep, so his framing is quoted only as the two outlets relay it; every version, date and id in the table comes from a CNA record, a vendor advisory or a merged pull request opened directly. The JPMorgan and Weaviate rows have no public artefact beyond the outlets and are marked as such.

## Am I affected?

- Running **MCP Toolbox for Databases** below **1.5.0** with an HTTP source or tool configured → upgrade; after 1.5.0 the SSRF guard is on and `allowPrivateNetworks` defaults closed — check your `tools.yaml` for anything that re-opens it.
- Running **Rapid7 Bulk Export MCP** 0.2.5–0.6.1 → 0.6.2.
- **Any MCP server you wrote or generated** with a tool that takes a URL, hostname, path or "endpoint" argument:

```bash
# tools whose arguments reach an HTTP client — the shape every row above shares
grep -rnE 'fetch\(|requests\.(get|post)|httpx\.|urllib\.request|axios\.|http\.NewRequest|curl ' --include=*.py --include=*.ts --include=*.js --include=*.go . | grep -iE 'url|endpoint|host|uri' | head -40
```

For each hit ask: is the destination resolved to an IP *at connect time* and checked against loopback / RFC1918 / link-local (incl. IPv6-mapped forms)? Are redirects re-validated per hop? Is the agent, or data the agent read, the source of the string? If the agent can be prompt-injected, the server can be pointed at `169.254.169.254`.

## If you are affected
- [if-an-mcp-server-was-malicious](../playbooks/if-an-mcp-server-was-malicious.md) — the triage shape is the same even though these servers are not malicious: what the server's network identity could reach, and what credentials the metadata endpoint would have handed over. Then [rotating-cloud-credentials](../playbooks/rotating-cloud-credentials.md) if the server ran with an instance role.

## Prevention
- [mcp-hygiene](../prevention/mcp-hygiene.md) — run URL-taking tools in an egress-restricted network; treat a tool argument as attacker input because the agent will, sooner or later, be told what to type.
- [agent-sandboxing](../prevention/agent-sandboxing.md) — block the cloud-metadata endpoint from anything an agent can reach.

## Sources
- [Unite.AI — Researcher Discloses Same MCP Flaw at Google, JPMorgan, Two Governments](https://www.unite.ai/researcher-discloses-same-mcp-flaw-at-google-jpmorgan-two-governments/) — 2026-10-05; the six organisations, dates and the researcher's "in triage, not fixed, not presented as confirmed" caveat on the US federal findings; names the researcher's update page and the May preprint (Zenodo DOI 10.5281/zenodo.20371152), neither of which this sweep could open.
- [TNW — Google, JPMorgan and two governments fixed the same MCP flaw](https://thenextweb.com/news/mcp-flaw-ssrf-google-jpmorgan-dinum-protocol-pivoting) — 2026-10-06; the "protocol pivoting" framing, the JPMorgan two-tool inconsistency, the Weaviate restriction, the Japan Digital Agency open item.
- [CVE Services — CVE-2026-14540](https://cveawg.mitre.org/api/cve/CVE-2026-14540) — Google CNA, published 2026-07-31: title, 0.3.0 through 1.4.0, CVSS 4.0 8.0 and vector, the `internal/sources/http/http.go` description, reference to PR #3448.
- [googleapis/mcp-toolbox — PR #3448, fix(source/http): implement SSRF guard](https://github.com/googleapis/mcp-toolbox/pull/3448) — opened 2026-06-16, merged 2026-06-18, shipped 1.5.0; the guard's options; reporter credited.
- [googleapis/mcp-toolbox — Security Advisories](https://github.com/googleapis/mcp-toolbox/security/advisories) and [googleapis/mcp-toolbox-sdk-python — Security Advisories](https://github.com/googleapis/mcp-toolbox-sdk-python/security/advisories) — both "There aren't any published security advisories," checked 2026-10-07.
- [CVE Services — CVE-2026-97228](https://cveawg.mitre.org/api/cve/CVE-2026-97228) — Rapid7 CNA, published 2026-09-25: the `export_id` GraphQL interpolation, 0.2.5–0.6.1, CVSS 3.1 2.7, fixed 0.6.2.
- [INFOKOM-KI/Wazuh-MCP-Server — GHSA-pw2j-pj4h-f5vg](https://github.com/INFOKOM-KI/Wazuh-MCP-Server/security/advisories/GHSA-pw2j-pj4h-f5vg) — vendor advisory, 2026-09-03, High: the literal-IP-only check, hostname bypass, 1,500-character exfiltration bound, commit 2bbfe12, reporter credit.
- [datagouv/datagouv-mcp — PR #126, SSRF hardening for external APIs](https://github.com/datagouv/datagouv-mcp/pull/126) — merged 2026-09-04: `get_dataservice_openapi_spec`, the producer-supplied `machine_documentation_url`, connect-time IP validation and per-hop redirect checks; reporter credited.
