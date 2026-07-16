---
id: 2026-07-mcp-scanning-campaign-sans
title: "SANS ISC documents internet-wide scanning for exposed MCP servers and AI-coding-tool credential files"
date_disclosed: 2026-07-13
last_updated: 2026-07-16
severity: medium
status: active
ecosystems: [mcp]
tools_affected: [mcp-servers, claude-code, cursor, vscode, ollama]
tags: [reconnaissance, mcp, ssrf, credential-scanning, internet-scanning, honeypot]
---

## TL;DR
SANS Internet Storm Center documented a **distributed, protocol-aware reconnaissance campaign** — 49 distinct source IPs sending ~200 requests over a 14-day window against a low-value honeypot-style web server — specifically probing for exposed **MCP servers**, AI-coding-tool config/credential files, and unauthenticated local LLM endpoints, plus SSRF attempts aimed at cloud metadata services. This is not a compromise by itself, but it's hard evidence that attackers are now building target inventories of AI-agent infrastructure ahead of exploitation — directly validating this repo's standing "MCP servers are unauthenticated network services by default" caution.

## What happened
A SANS ISC handler analyzed 14 days of Apache/ModSecurity logs from a deliberately low-traffic web server (WordPress + custom backends + static content — not a high-value target) and found scanning traffic specifically shaped around AI-agent infrastructure rather than generic web recon ([SANS ISC Diary #33150](https://isc.sans.edu/diary/33150)):

- **MCP protocol handshakes**: ~200 requests, from **49 distinct source IPs**, sending well-formed `POST /mcp` requests with valid JSON-RPC 2.0 bodies and the correct MCP protocol version string (`"2025-03-26"`) — i.e., not blind fuzzing, but protocol-aware probes checking whether an MCP server is listening.
- **AI-coding-tool config/credential fishing**: HEAD/GET requests for predictable config paths — `/.claude/mcp.json`, `/.cursor/mcp.json`, `/.vscode/mcp.json`, and specifically `/.claude/.credentials.json` (checked via lightweight HEAD requests for efficiency before attempting a full GET).
- **LLM endpoint enumeration**: `GET /v1/models` (OpenAI-compatible endpoint probe) and `GET /api/tags` (Ollama model-listing probe), looking for unauthenticated local inference servers exposed to the internet.
- **Cloud-metadata SSRF attempts**: requests rotating parameter names (`url`, `uri`, `path`, `dest`) aimed at `169.254.169.254` and `metadata.google.internal` — the same SSRF-to-cloud-IMDS pattern already documented in the [Miasma](2026-06-miasma-redhat-cloud-services-compromise.md) and [n8n-mcp](2026-05-mcp-stdio-systemic-rce.md) advisories, here used as a generic probe rather than tied to one known vulnerable server.

The handler characterizes this as a "broad, distributed scan" reflecting mature campaign infrastructure, and notes the scanning **predates widespread production MCP deployment** — i.e., attackers are inventorying exposed AI-agent surface area now, ahead of the exploitation that will follow as more MCP servers go into production. Independent coverage from [Cyberpress](https://cyberpress.org/hackers-scan-exposed-ai/) and [Cybersecurity News](https://cybersecuritynews.com/internet-wide-scans-target-mcp-servers-claude-credentials/) corroborates the same source count and probe categories.

No specific vulnerability, CVE, or named threat actor is attached to this campaign — it is reconnaissance, not (yet) documented exploitation. There is no "patch" for being scanned; the actionable takeaway is not exposing the probed surfaces in the first place.

## Am I affected?
You're a live target for this class of scan if you run any of the probed surfaces reachable from the public internet:
```bash
# Check your web/app server logs for these exact probe patterns
grep -E '"jsonrpc":"2\.0".*"initialize"|/\.claude/mcp\.json|/\.cursor/mcp\.json|/\.vscode/mcp\.json|/\.claude/\.credentials\.json|GET /v1/models|GET /api/tags' \
  /var/log/{apache2,nginx}/access.log* 2>/dev/null

# Confirm nothing under a web-servable root exposes AI-tool config
find / -xdev \( -path '*/.claude/mcp.json' -o -path '*/.cursor/mcp.json' -o -path '*/.vscode/mcp.json' -o -path '*/.claude/.credentials.json' \) 2>/dev/null | \
  xargs -I{} sh -c 'echo {}: $(stat -c "%a" {})'
```
If you have deployed any MCP server with its HTTP transport bound to `0.0.0.0` or otherwise internet-reachable, or if a `.claude/`, `.cursor/`, or `.vscode/` directory is accidentally served from a public web root, treat this campaign as actively probing you today, not a hypothetical.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — if a log hit confirms a probe actually reached a live credential file or MCP endpoint.
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — bind MCP server HTTP transports to `127.0.0.1`, never `0.0.0.0`; require authentication on any MCP surface reachable off-host.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — never serve `.claude/`, `.cursor/`, or `.vscode/` directories from a public web root.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Why this matters for vibe coders
This repo has repeatedly tracked individual MCP servers shipping unauthenticated-by-default network surfaces (mcp-atlassian, Azure MCP Server, `n8n-mcp`, `fast-mcp-telegram`, `@andrea9293/mcp-documentation-server`, and more — see the [systemic MCP stdio RCE advisory](2026-05-mcp-stdio-systemic-rce.md)). This is the first sweep-tracked evidence, from independent telemetry rather than a single vendor's incident report, that attackers are treating exposed MCP servers and AI-tool credential files as a distinct, already-being-scanned target category — the same way port scanners have long inventoried exposed databases and admin panels. Assume any MCP surface you expose is already on someone's target list.

## Sources
- [SANS Internet Storm Center — Diary #33150: AI/MCP scanning activity](https://isc.sans.edu/diary/33150) — primary telemetry, source-IP count, probe categories.
- [Cyberpress — Hackers Scan for Exposed AI Infrastructure](https://cyberpress.org/hackers-scan-exposed-ai/) — independent corroboration.
- [Cybersecurity News — Internet-Wide Scans Target MCP Servers, Claude Credentials](https://cybersecuritynews.com/internet-wide-scans-target-mcp-servers-claude-credentials/) — independent corroboration.
