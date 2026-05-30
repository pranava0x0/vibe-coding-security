---
id: 2026-01-opencode-localhost-rce
title: "OpenCode AI coding agent — twin localhost RCEs (CVE-2026-22812 + CVE-2026-22813)"
date_disclosed: 2026-01-12
last_updated: 2026-05-30
severity: critical
status: patched
ecosystems: [ai-agents, ai-ide, npm]
tools_affected: [opencode, anomalyco-opencode, sst-opencode]
tags: [cve, rce, localhost, browser-attacker-model, xss, websocket, ai-ide, lethal-trifecta]
---

## TL;DR
**OpenCode** — the **71K-star** open-source AI coding agent ("the open source coding agent" from anomalyco / SST) — shipped two unauth RCEs in the same release window. **[CVE-2026-22812](https://nvd.nist.gov/vuln/detail/CVE-2026-22812)** (CVSS 8.8): OpenCode's local HTTP server binds **`0.0.0.0` with permissive CORS** and exposes `POST /session/{id}/shell` with **no authentication** — any web page the developer visits sends one fetch and runs arbitrary commands. **[CVE-2026-22813](https://nvd.nist.gov/vuln/detail/CVE-2026-22813)** (CVSS 9.4): the chat UI inserts LLM markdown responses straight into the DOM with no sanitization, so a malicious LLM response (or **any attacker-controlled content the agent ever reads**) → XSS → WebSocket → shell command. **Both fixed in v1.0.216** (adds a per-session auth token to the HTTP server). **~220,000 instances exposed**; **public PoCs on GitHub** (three modes: command exec, file r/w, interactive shell). Same "localhost is not a security boundary in the browser-attacker model" root cause as [OpenClaw CVE-2026-25253](2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md) — and a clean **connector-chaining lethal-trifecta-in-one-app** for the markdown-renderer variant.

## What happened
OpenCode is an open-source AI coding agent ([anomalyco/opencode](https://github.com/anomalyco/opencode), 71K+ GitHub stars) — comparable to aider, Claude Code, Cursor, Cline, Codex CLI, and the OpenHands/OpenClaw family. Developers run it locally; it spawns a local HTTP server + a WebSocket UI and drives an LLM through the user's coding workflow.

**[CVE-2026-22812](https://nvd.nist.gov/vuln/detail/CVE-2026-22812) — Unauthenticated HTTP shell endpoint (CWE-306 + CWE-942)**

OpenCode prior to **v1.0.216** auto-starts an HTTP server **bound to `0.0.0.0`** with **CORS `*`**, exposing endpoints including `POST /session/{id}/shell`. There is **no authentication token**. Any local process — or any web page the developer's browser loads, anywhere — issues a single `fetch()` and the OpenCode server happily runs the supplied shell command with the developer's user privileges. ([Lilting Channel writeup](https://lilting.ch/en/articles/opencode-cve-2026-22812-22813-rce); [Dharanis (researcher) Medium writeup](https://medium.com/@dhxrxx/cve-2026-22812-how-i-got-rce-on-a-71k-star-ai-coding-tool-with-zero-authentication-7524fbc3317f); [CVE Reports](https://cvereports.com/reports/CVE-2026-22812)). Reported to `support@sst.dev` on **2025-11-17**; CVE assigned and **published to NVD on 2026-01-12** ([cvedetails.com](https://www.cvedetails.com/cve/CVE-2026-22812/)).

**[CVE-2026-22813](https://nvd.nist.gov/vuln/detail/CVE-2026-22813) — RCE via XSS in markdown renderer (CVSS 9.4)**

The chat web UI **inserts LLM markdown responses directly into the DOM without sanitization** (no DOMPurify, no CSP) — and any LLM-emitted HTML/JS executes in the same WebSocket-authorized origin as the privileged shell endpoint. So **any path that gets attacker-controlled text into an LLM response** — a malicious file the agent reads, a poisoned web page the agent fetches, a malicious git remote, a malicious PR comment — pivots to **shell command execution** via the WebSocket. ([PointGuard AI writeup](https://www.pointguardai.com/ai-security-incidents/opencode-ai-ui-turns-chat-output-into-code-cve-2026-22813); [Lilting Channel](https://lilting.ch/en/articles/opencode-cve-2026-22812-22813-rce)).

**Both CVEs were fixed in v1.0.216** ([release notes](https://github.com/anomalyco/opencode/releases/tag/v1.0.216)), which adds a **per-session auth token** to the HTTP server (every request must include a token only the legitimate OpenCode process generates at startup). PoCs for both are publicly available on GitHub ([0xgh057r3c0n/CVE-2026-22812](https://github.com/0xgh057r3c0n/CVE-2026-22812), [0xBlackash/CVE-2026-22812](https://github.com/0xBlackash/CVE-2026-22812)) — three modes: command execution, file read/write, and interactive shell acquisition. **~220,000 OpenCode instances were exposed on the public internet at disclosure**.

**Why both bugs are vibe-coding-relevant:**

1. **CVE-2026-22812** is the cleanest 2026 example of the "**localhost is not a security boundary in the browser-attacker model**" class — exact same root cause as [OpenClaw CVE-2026-25253](2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md) and the [Marimo notebook unauth `/terminal/ws`](2026-04-marimo-notebook-rce.md). Binding to localhost does **not** stop a browser tab from reaching localhost, and the `0.0.0.0` bind here makes it strictly worse: any device on the same LAN is also in the attacker model.
2. **CVE-2026-22813** is a **connector-chaining lethal-trifecta packed into one app**. The reader connector (LLM markdown response, an inherently untrusted text channel) feeds the privileged executor connector (the WebSocket-authorized `/shell` endpoint) with **no trust boundary between them**. Same lethal-trifecta shape as [Claude Desktop Extensions](2026-02-claude-desktop-extensions-rce.md), [Windsurf zero-click MCP](2026-05-windsurf-zero-click-mcp-rce.md), and [Cursor CurXecute / MCPoison](2025-07-cursor-curxecute-mcpoison.md) — but here the "executor" connector is **built into the same process** as the chat UI.

## Am I affected?

```bash
# Check OpenCode version
opencode --version 2>/dev/null

# Or npm install
npm list -g opencode-ai 2>/dev/null | grep opencode

# Is OpenCode running with an exposed HTTP port?
ss -tlnp 2>/dev/null | grep -E ':3030|opencode'  # default port; verify against your install
# CVE-2026-22812 instances bind 0.0.0.0 — check for non-loopback binds:
ss -tlnp4 2>/dev/null | grep -E '^tcp.*0\.0\.0\.0.*opencode'
```

If your version is `< 1.0.216` **and** the OpenCode process was running while you browsed the web, treat the host as **potentially compromised** — a single visit to a malicious page (delivered by ad, phishing email, Slack/Discord link, AI-tool chat) is enough. The `0.0.0.0` bind also means any device on the same Wi-Fi can hit the shell endpoint.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-22812` (CVSS 8.8), `CVE-2026-22813` (CVSS 9.4) |
| GHSA | `GHSA-vxw4-wv6m-9hhh` (CVE-2026-22812) |
| Affected versions | `OpenCode < 1.0.216` |
| Fixed version | `OpenCode 1.0.216` |
| Vendor | anomalyco / SST (`sst.dev`) |
| Disclosure | reported 2025-11-17; CVE published NVD 2026-01-12 |
| Vulnerable endpoint (812) | `POST /session/{id}/shell` (unauthenticated, CORS `*`) |
| Vulnerable surface (813) | LLM markdown chat response → DOM (no DOMPurify, no CSP) |
| CWE | 306 (Missing Auth), 749 (Exposure of Dangerous Method), 942 (Permissive CORS); 79 (XSS), 1336 (Improper Neutralization in Output Used by a Downstream Component) |
| Exposed instances | ~220,000 (researcher scan) |
| Public PoCs | `0xgh057r3c0n/CVE-2026-22812`, `0xBlackash/CVE-2026-22812` (GitHub) |

## If you are affected
1. **Upgrade OpenCode to `1.0.216` or later immediately.**
2. **Treat the host as compromised** if OpenCode ran on a vulnerable version with browser access in the same session. Rotate:
   - Local SSH keys (`~/.ssh/`).
   - Cloud credentials in `~/.aws/`, `~/.config/gcloud/`, `~/.azure/`.
   - GitHub PAT / npm token / 1Password CLI session / Vault tokens.
   - Any LLM provider key OpenCode could read from env or config.
   - Any AI-tool config file (`~/.claude/`, `~/.cursor/`, `~/.aider/`, OpenCode's own config) — see [the AI-tool-config-as-credential-store pattern](2026-05-nx-console-vscode-compromise.md).
3. **Bind OpenCode to `127.0.0.1` only**, behind the new auth token. If you run on a workstation with anyone else on the LAN, this is non-negotiable.
4. Review browser history for the exposure window — visits to ad-supported sites, third-party CDN-loaded pages, or anything cached during `opencode` sessions are candidates for the delivery vector.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ **Never expose a local-agent UI on `0.0.0.0`.** Bind `127.0.0.1` only, plus auth. Same rule as [OpenClaw CVE-2026-25253](2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md), [Marimo CVE-2026-39987](2026-04-marimo-notebook-rce.md), and the [systemic MCP stdio class](2026-05-mcp-stdio-systemic-rce.md).
→ Treat the markdown renderer in any local-agent UI as **part of the security boundary**. LLM responses are untrusted text — render them in a sandboxed `<iframe>` or sanitize with DOMPurify + strict CSP **before** they reach the privileged WebSocket-authorized origin.
→ If you build a local AI tool: don't co-locate the *reader* connector (anything that can ingest untrusted text — LLM responses, fetched pages, files, MCP tool replies) and the *executor* connector (shell, file write, network call) in the same WebSocket-authorized origin. Same lesson as [Claude Desktop DXT](2026-02-claude-desktop-extensions-rce.md), [Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md), [Windsurf zero-click MCP](2026-05-windsurf-zero-click-mcp-rce.md).

## Sources
- [NVD CVE-2026-22812 Detail](https://nvd.nist.gov/vuln/detail/CVE-2026-22812) — canonical CVE record.
- [GitHub Advisory Database — GHSA-vxw4-wv6m-9hhh (CVE-2026-22812)](https://github.com/advisories/GHSA-vxw4-wv6m-9hhh) — vendor advisory.
- [anomalyco/opencode release v1.0.216](https://github.com/anomalyco/opencode/releases/tag/v1.0.216) — vendor fix.
- [Lilting Channel — Two cases of unauthenticated RCE and RCE via XSS, over 220,000 instances exposed in OpenCode](https://lilting.ch/en/articles/opencode-cve-2026-22812-22813-rce) — researcher writeup covering both CVEs + exposure scale.
- [PointGuard AI — CVE-2026-22813 OpenCode AI XSS Vulnerability](https://www.pointguardai.com/ai-security-incidents/opencode-ai-ui-turns-chat-output-into-code-cve-2026-22813) — CVE-2026-22813 walk-through.
- [SentinelOne — CVE-2026-22812 OpenCode RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-22812/) — CVE catalog entry.
- [SentinelOne — CVE-2026-22813 OpenCode AI Coding Agent XSS Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-22813/) — CVE catalog entry.
- [CVE Reports — CVE-2026-22812 OpenCode RCE: When Localhost Becomes Public Enemy #1](https://cvereports.com/reports/CVE-2026-22812) — researcher framing of the localhost-attacker class.
- [Securify — CVE-2026-22812: When an Internal Developer Tool Becomes an RCE Exposure](https://securifyai.co/blog/cve-2026-22812-when-an-internal-developer-tool-becomes-an-rce-exposure/) — exposure framing.
- [CVE Feed — CVE-2026-22812](https://cvefeed.io/vuln/detail/CVE-2026-22812) — CVE tracker.
- [Dharanis (Medium) — CVE-2026-22812: How I Got RCE on a 71k-Star AI Coding Tool With Zero Authentication](https://medium.com/@dhxrxx/cve-2026-22812-how-i-got-rce-on-a-71k-star-ai-coding-tool-with-zero-authentication-7524fbc3317f) — researcher first-person.
- [0xgh057r3c0n/CVE-2026-22812 (GitHub) — public PoC](https://github.com/0xgh057r3c0n/CVE-2026-22812) — exploit code.
- [0xBlackash/CVE-2026-22812 (GitHub) — public PoC](https://github.com/0xBlackash/CVE-2026-22812) — exploit code.
- [Offseq Radar — CVE-2026-22812 threat detail](https://radar.offseq.com/threat/cve-2026-22812-cwe-306-missing-authentication-for--06adb808) — live threat-intel feed.
