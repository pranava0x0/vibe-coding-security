---
id: 2026-02-claude-desktop-extensions-rce
title: "Claude Desktop Extensions (DXT) zero-click RCE — Anthropic declines to fix (Feb 2026)"
date_disclosed: 2026-02-09
last_updated: 2026-05-21
severity: critical
status: active
ecosystems: [claude-code, anthropic, mcp]
tools_affected: [claude-desktop, claude-desktop-extensions, mcp]
tags: [prompt-injection, rce, zero-click, mcp, dxt, lethal-trifecta, wont-fix]
---

## TL;DR
**Claude Desktop Extensions (DXT)** — the local, MCP-based extensions you install into the Claude desktop app — run **unsandboxed with full user privileges**. LayerX showed a **zero-click RCE (CVSS 10.0)**: an attacker plants plain-text instructions in a **Google Calendar event** (or any content a connector can read); later the user types something innocuous like *"check my calendar and take care of it,"* and Claude autonomously **chains a low-risk connector to a high-risk local executor** and runs attacker code — no confirmation prompt, no warning. **~10,000+ users / 50 DXT extensions** are in scope. **Anthropic declined to fix it**, calling it "outside our current threat model," so there is **no patch**.

## What happened
LayerX disclosed (report dated **2026-02-09**, with renewed coverage around RSAC in May 2026) that DXT extensions are **not sandboxed** and execute with the **user's full local privileges**. Claude can autonomously **compose connectors** — and it will happily pipe a low-trust *reader* connector (Google Calendar, email, Drive) into a high-trust *executor* connector (a local MCP server that runs shell commands), without the user realizing a calendar event just became code execution.

The exploit is the textbook **"lethal trifecta"** (private-data access + untrusted content + exfil/act ability), collapsed into one app:

1. Attacker creates/sends a **calendar event** with a benign title (e.g., "Task Management") whose description contains plain-text instructions: *fetch code from this Git repo and run it locally.*
2. Victim issues a vague, common prompt: *"Please check my latest events and take care of it for me."*
3. Claude reads the event, **invokes a local MCP extension with execution privileges**, downloads the attacker's code, and runs it — **zero clicks, no approval dialog**.

Result: **full local RCE**, scored **CVSS 10.0**. Anthropic **declined to act**, calling DXT "a local development tool that operates within the user's own environment" where "users explicitly configure and grant permissions to MCP servers they choose to run locally." The trust boundary is unchanged, so **status is `active` (won't-fix), not patched/mitigated.**

This is **distinct** from [ClaudeBleed](2026-05-claudebleed-chrome-extension.md) (the Claude *Chrome* extension's `externally_connectable` hijack) — same vendor/researcher, different surface — and a desktop-app instance of the [Supabase MCP lethal-trifecta](2025-07-supabase-mcp-lethal-trifecta.md) and [Windsurf zero-click MCP RCE](2026-05-windsurf-zero-click-mcp-rce.md) pattern.

## Am I affected?
You're exposed if you run **Claude Desktop** with **any DXT / MCP extension that can execute code or run shell commands locally**, *and* you also have a connector that reads attacker-reachable content (calendar, email, shared docs, issues).

```bash
# macOS: list installed Claude Desktop extensions / MCP config
ls ~/Library/Application\ Support/Claude/ 2>/dev/null
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json 2>/dev/null

# Linux/Windows: locate the desktop config and review mcpServers
find ~ -name 'claude_desktop_config.json' 2>/dev/null
```

Look at every entry under `mcpServers`: any server that can run commands, write files, or spawn processes is a **high-risk executor**. Any server that reads external content (calendar/email/web/Drive) is an **untrusted-content source**. Having both wired into the same Claude is the vulnerable configuration.

### IOCs / facts

| Type | Value |
|---|---|
| Product | Claude Desktop Extensions (DXT), local MCP-based |
| Mechanism | Connector-chaining: untrusted reader → privileged local executor |
| Trigger | Malicious calendar/email/doc content + a vague user prompt |
| Severity | **CVSS 10.0**, zero-click |
| Scope | ~10,000+ users, ~50 DXT extensions |
| Vendor response | **Declined to fix** — "outside our current threat model" |
| CVE | None assigned |

## If you are affected
There is **no vendor patch**. Reduce blast radius yourself:

1. **Don't co-locate readers and executors.** Remove privileged-executor MCP servers from any Claude profile that also has calendar/email/Drive/web-reading connectors.
2. **Require human approval** for any tool that executes code; never run "take care of it"-style prompts against untrusted inboxes/calendars.
3. Run executor MCP servers as an unprivileged user, in a container, with strict egress allowlists.
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources
- [LayerX — Claude Desktop Extensions Exposes Over 10,000 Users to Remote Code Execution Vulnerability](https://layerxsecurity.com/blog/claude-desktop-extensions-rce/)
- [Infosecurity Magazine — New Zero-Click Flaw in Claude Extensions, Anthropic Declines Fix](https://www.infosecurity-magazine.com/news/zeroclick-flaw-claude-dxt/)
- [eSecurity Planet — 10K Claude Desktop Users Exposed by Zero-Click Vulnerability](https://www.esecurityplanet.com/threats/10k-claude-desktop-users-exposed-by-zero-click-vulnerability/)
- [TechRepublic — 10K Claude Desktop Users Exposed by Zero-Click Vulnerability](https://www.techrepublic.com/article/news-claude-desktop-zero-click-vulnerability/)
- [SC Media — LayerX reports vulnerability in Claude Desktop Extensions, Anthropic declines to fix](https://www.scworld.com/brief/layerx-reports-vulnerability-in-claude-desktop-extensions-anthropic-declines-to-fix)
- [Security Boulevard — Flaw in Anthropic Claude Extensions Can Lead to RCE in Google Calendar: LayerX](https://securityboulevard.com/2026/02/flaw-in-anthropic-claude-extensions-can-lead-to-rce-in-google-calendar-layerx/)
