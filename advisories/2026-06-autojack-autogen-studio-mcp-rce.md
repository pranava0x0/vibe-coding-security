---
id: 2026-06-autojack-autogen-studio-mcp-rce
title: "AutoJack — Microsoft Research AutoGen Studio 3-flaw chain: browsing agent renders attacker page → localhost MCP WebSocket → unauthenticated RCE"
date_disclosed: 2026-06-13
last_updated: 2026-06-19
severity: high
status: patched
ecosystems: [pypi, mcp, ai-agents]
tools_affected: [autogen-studio, autogenstudio, microsoft-autogen]
tags: [cve, localhost-rce, mcp, websocket, browsing-agent, ai-agents, prompt-injection, microsoft, no-wild-exploitation]
---

## TL;DR

Microsoft Research's **AutoGen Studio** — the visual IDE for AutoGen multi-agent systems — contains a **3-flaw chain** discovered by independent security researchers and named **"AutoJack"**: (1) the AutoGen Studio MCP server binds its WebSocket on `0.0.0.0` with no authentication; (2) no origin validation on the WebSocket handshake; (3) a browsing-capable AutoGen agent that visits a malicious attacker-controlled webpage can have that page's JavaScript reach the localhost MCP WebSocket and issue arbitrary tool calls. The result is **unauthenticated remote code execution** — a webpage any developer visits can hijack their local AutoGen Studio instance. **No exploitation in the wild has been reported.** Microsoft Research shipped a patched release shortly after disclosure.

## What happened

**AutoGen** is Microsoft Research's open-source multi-agent AI framework, used to orchestrate networks of AI agents that collaborate on tasks. **AutoGen Studio** is the accompanying visual interface — a web UI + backend service that developers run locally to design, test, and deploy AutoGen agent workflows.

Security researchers disclosed **AutoJack** on 2026-06-13: a 3-step attack chain requiring no special access:

**Step 1 — Unauthenticated MCP WebSocket on 0.0.0.0**
AutoGen Studio's MCP server starts a WebSocket listener on `0.0.0.0` (all interfaces) rather than `127.0.0.1`. No authentication is required — no API key, no token, no session cookie. Any process or webpage that can reach the port can issue MCP tool calls.

**Step 2 — Missing WebSocket origin validation**
The WebSocket handshake does not validate the `Origin` header. The [same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Same-origin_policy) does not apply to WebSocket connections — browsers allow JavaScript from any origin to open a WebSocket to any host:port that will accept the connection. Without an `Origin` allowlist, a webpage served from `attacker.com` can connect to `ws://localhost:<port>/mcp`.

**Step 3 — Browsing agent renders attacker-controlled content**
AutoGen agents can be configured with browser-use capabilities (fetching URLs, rendering pages). When such an agent browses a malicious page, that page's JavaScript runs in the browser context and can open a WebSocket to `ws://127.0.0.1:<autogen-studio-port>/mcp` to issue arbitrary tool calls — including executing shell commands, reading files, or making API calls on the developer's machine.

**The full chain:** Developer runs AutoGen Studio locally → agent browses a malicious URL (could be in agent instructions, a poisoned data source, or a prompt-injected workflow step) → page JavaScript connects to localhost MCP WebSocket → executes arbitrary commands on the developer's machine.

**Relationship to the "localhost is not a security boundary" cluster:** AutoJack is the fifth named instance of this root-cause class in this repo: [OpenCode CVE-2026-22812](2026-01-opencode-localhost-rce.md), [Cline CVE-2026-44211](2026-06-cline-cve-2026-44211-websocket-rce.md), [OpenClaw CVE-2026-25253](2026-01-openclaw-cve-2026-25253-gatewayurl-rce.md), and [Marimo CVE-2026-39987](2026-04-marimo-notebook-rce.md) all share the same root cause. Any AI tool or notebook that starts an unauthenticated localhost HTTP/WebSocket server while a browsing-capable agent or the developer's browser is active is in this class.

**No wild exploitation reported.** Researchers notified Microsoft Research before full public disclosure; a patched release was available before the CVE was widely publicized.

## Am I affected?

```bash
# Check installed AutoGen Studio version
pip show autogenstudio 2>/dev/null | grep Version

# Check if AutoGen Studio MCP is running
ss -tlnp 2>/dev/null | grep -E ':8081|:8080|:7860'
# (default port may vary; check your autogenstudio config)

# Check which interface it's bound to
ss -tlnp 2>/dev/null | grep autogen
```

You are affected if:
1. You run AutoGen Studio locally and use AutoGen agents with browsing capabilities.
2. You run an unpatched version — check the patched version in the vendor advisory.
3. Your AutoGen Studio MCP server is reachable from any network interface beyond `127.0.0.1`.

The attack requires **a browsing-capable agent** to visit an attacker-controlled URL. This can happen via:
- Prompt injection that inserts a malicious URL into agent instructions
- A poisoned data source the agent reads (e.g., a tool result, a scraped page)
- A developer manually asking the agent to browse a site that redirects to a malicious page

### IOCs

| Type | Value |
|---|---|
| Campaign name | AutoJack |
| Root cause flaws | 3: MCP WebSocket on 0.0.0.0; no origin validation; browsing agent renders attacker JS |
| Affected tool | AutoGen Studio (autogenstudio PyPI package) |
| Attack vector | Browsing-capable agent visits attacker-controlled URL |
| Authentication required | No |
| Exploitation in the wild | None reported |
| Status | Patched |
| Attack class | "Localhost is not a security boundary" (5th named instance) |

## If you are affected

1. **Upgrade AutoGen Studio** to the latest patched release.
2. **Disable MCP WebSocket** if your workflow does not require it, or bind it to `127.0.0.1` only.
3. **Review agent browsing permissions** — agents that use browser-use capabilities should have allowlisted URL patterns; general-purpose web browsing is a significant attack surface.
4. **Check agent logs** for any unexpected shell command execution or outbound network requests during browsing sessions.

## Prevention

- **Bind MCP servers to `127.0.0.1` only**, never `0.0.0.0`. An agent orchestration service has no reason to accept connections from the network.
- **Validate the `Origin` header** on all WebSocket connections. Reject connections from any origin that isn't `http://localhost` or `http://127.0.0.1`.
- **Apply URL allowlists for browsing agents.** Agents that need to fetch specific APIs or documentation don't need unrestricted web access.
- **Treat the "localhost is not a security boundary" pattern as a class bug.** Audit all locally-running AI tools: `ss -tlnp | grep -v 127.0.0.1` — anything binding to `0.0.0.0` with no auth is in this class.
- See: [Cline CVE-2026-44211](2026-06-cline-cve-2026-44211-websocket-rce.md), [OpenCode CVE-2026-22812](2026-01-opencode-localhost-rce.md), [IDEsaster](2026-06-idessaster-ai-ide-cve-cluster.md) for the pattern.

## Sources

- [The Hacker News — AutoJack: Researchers Find 3-Flaw Chain in AutoGen Studio That Lets Malicious Webpages Execute Code](https://thehackernews.com) — primary disclosure; 3-flaw chain detail; MCP WebSocket; browsing agent attack path.
- [CybersecurityNews — AutoJack: AutoGen Studio RCE via Unauthenticated MCP WebSocket and Browser Agent](https://cybersecuritynews.com) — independent corroboration; no-auth MCP; origin validation missing.
- Cross-link: [Cline CVE-2026-44211](2026-06-cline-cve-2026-44211-websocket-rce.md) — same attack class; unauthenticated WebSocket on port 3484.
- Cross-link: [IDEsaster AI IDE CVE cluster](2026-06-idessaster-ai-ide-cve-cluster.md) — coordinated disclosure including 8 AI tools with the same root cause.
- Cross-link: [MCP stdio systemic RCE class](2026-05-mcp-stdio-systemic-rce.md) — unauthenticated-by-default MCP pattern.
