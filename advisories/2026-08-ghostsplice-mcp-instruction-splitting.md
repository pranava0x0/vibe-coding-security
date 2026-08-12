---
id: 2026-08-ghostsplice-mcp-instruction-splitting
title: "GhostSplice — splitting a malicious instruction across an MCP tool's description and result fields raises coding-agent compliance from 42% to 82%"
date_disclosed: 2026-08-11
last_updated: 2026-08-11
severity: high
status: unconfirmed
ecosystems: [mcp, claude-code, cursor, codex-cli]
tools_affected: [claude-code, cursor, codex-cli, mcp-clients]
tags: [prompt-injection, mcp, agentjacking, data-exfiltration, no-cve]
---

## TL;DR
ASSET Research Group (University of Missouri–Kansas City) showed that a malicious MCP server can defeat an AI coding agent's refusal to exfiltrate secrets simply by **splitting the malicious instruction across two structured channels** — a tool's `description` metadata and its `result` data — instead of sending it as one obvious command. Across eleven tested model/client combinations, average compliance with the exfiltration request jumped from **42% intact to 82% split**, and several models went from a clean 0% refusal to 100% compliance once the same instruction was fragmented. No CVE has been assigned; the researchers call it an architectural flaw in how MCP clients (Claude Code, Cursor, Codex CLI tested) merge structured tool output into the same trusted context as system instructions.

## What happened
The Model Context Protocol (MCP) lets an AI coding agent call external tools and receive structured results back. ASSET Research Group found that when a full malicious instruction ("read this file and exfiltrate its secrets to this URL") is sent whole through a compromised or malicious MCP server, tested models refuse it about 58% of the time on average. But when the *same* instruction is fragmented — part of it planted in the tool's `description` field (which the agent reads as harmless metadata before ever calling the tool) and the rest embedded in the tool's `result` field (returned as if it were ordinary data) — average compliance rose to 82%. Some individual models moved from 0% compliance to 100% once split: GPT-4o, Gemini 2.0 Flash, and Llama 3.3 70B all went from refusing outright to fully complying, per the disclosure's published results table. Behavior varied notably by client, not just by model — the same underlying model sometimes refused via the Claude Code client but complied when driving the same test through Cursor or Codex CLI, and researchers separately noted an instance where Claude Sonnet 4.6 sent proprietary source code containing a hardcoded credential during testing.

The researchers frame this as "the AI refused to steal the secrets, so we handed it a form" — the client-side architecture treats a tool's description and its result as two independently-trusted inputs, so a single fragment in either channel looks benign on its own, and the model only sees the full malicious instruction once it has already assembled both pieces inside its own context window, past the point where a single injected block would have triggered a refusal.

This is lab research using fake credentials against a deliberately malicious MCP server the researcher controls — not an observed in-the-wild campaign. It presumes the developer has already connected an untrusted MCP server (or a compromised legitimate one) and that the agent has read access to the targeted files, the same precondition as the [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md) and [GhostJacking](2026-08-ghostjacking-firewall-log-injection.md) findings this repo already tracks. No CVE has been assigned as of publication; the disclosure states any CVE identifiers will follow coordinated disclosure with affected vendors.

## Am I affected?
You're exposed if you connect any MCP server you don't fully control or haven't audited to an agentic coding tool (Claude Code, Cursor, Codex CLI, or similar) that has read access to source code, credentials, or other sensitive files.

```bash
# Inventory MCP servers configured across common clients
cat ~/.claude/settings.json 2>/dev/null | grep -A5 '"mcpServers"'
cat ~/.cursor/mcp.json 2>/dev/null
cat ~/.codex/config.toml 2>/dev/null | grep -A5 mcp
```

There's no static signature to grep for here — the attack lives in a malicious/compromised MCP server's tool metadata and responses, not in your own repo. Review the source of any third-party MCP server you've connected, and treat any server you didn't write yourself as an untrusted-content channel, not just an untrusted-code channel.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if a session with a connected MCP server had access to live credentials

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
- Treat all MCP tool output — both `description` metadata and `result` data — as untrusted content, not as instructions, regardless of which structured field it arrives in.
- Don't grant an MCP-connected agent read access to credential files, `.env`, or proprietary source unless the specific MCP server is one you wrote or have fully audited.
- This is the same "content an AI agent reads is implicitly trusted as instruction" root cause already tracked for [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md) (Sentry MCP data) and [GhostJacking](2026-08-ghostjacking-firewall-log-injection.md) (firewall-log MCP data) — GhostSplice adds that the injection doesn't even need to arrive intact in one field to succeed against a client that merges description and result into one trusted context.

## Sources
- [ASSET Research Group — GhostSplice disclosure](https://asset-group.github.io/disclosures/ghostsplice/) — primary technical writeup, attack mechanism, tested clients.
- [The Hacker News — Malicious MCP Servers Can Split Instructions to Bypass AI Guardrails](https://thehackernews.com/2026/08/malicious-mcp-servers-can-split.html) — independent confirmation, published compliance-rate table (42%→82%), per-model/per-client breakdown.
