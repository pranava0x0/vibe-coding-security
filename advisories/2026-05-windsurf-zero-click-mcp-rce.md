---
id: 2026-05-windsurf-zero-click-mcp-rce
title: "Windsurf zero-click MCP prompt-injection RCE (CVE-2026-30615)"
date_disclosed: 2026-05
last_updated: 2026-05-17
severity: critical
status: patched
ecosystems: [windsurf, mcp]
tools_affected: [windsurf]
tags: [windsurf, mcp, prompt-injection, rce, cve, zero-click]
---

## TL;DR
**CVE-2026-30615** (CVSS 8.0 High, but called out as zero-click) lets a remote attacker achieve RCE on a host running Windsurf ≤ 1.9544.26 by injecting instructions that cause unauthorized modification of `mcp.json` and **automatic registration of an attacker-controlled MCP server — with no user interaction**. Of the four major AI IDEs OX Security tested (Windsurf, Cursor, Claude Code, Gemini-CLI), only Windsurf had a fully zero-click path.

## What happened
OX Security audited the MCP write-paths in major AI coding tools and found a class-wide vulnerability — prompt-injectable content read by the agent could trigger writes to the user's MCP configuration file (`mcp.json`), which is then auto-loaded and the new server's `command` executed.

- **Windsurf:** zero user interaction required. Filed as CVE-2026-30615. Patched in versions > 1.9544.26.
- **Cursor / Claude Code / Gemini-CLI:** the same class of write-path bug existed; Google, Microsoft, and Anthropic declined to issue CVEs, arguing that "explicit user permission" is required to modify the files. Researchers contest this — the path is exploitable in practice with realistic agent configurations.

This is the same class as [Cursor's CurXecute/MCPoison](2025-07-cursor-curxecute-mcpoison.md). The MCP trust model — *the user must approve any new server entry* — keeps getting bypassed because the trust check runs after the file write, not before.

## Am I affected?

```bash
# Check Windsurf version
windsurf --version
# Or via the IDE: Help → About
```

If Windsurf ≤ 1.9544.26 was ever connected to an MCP server that ingests content from the public internet, public Slack channels, GitHub issues, customer-submitted data, or similar — assume the path could have been exploited. Update.

```bash
# Audit your mcp.json for entries you didn't add
cat ~/.windsurf/mcp.json 2>/dev/null
cat ~/.codeium/mcp.json 2>/dev/null   # older config location
```

## If you are affected
1. **Update Windsurf** past 1.9544.26 immediately.
2. **Audit `mcp.json` for unknown entries.** Delete anything you don't actively use; for entries you keep, confirm the `command` matches what you originally approved.
3. **Treat outbound activity from any unknown MCP as compromise.** Rotate credentials handled by that MCP and any cloud creds reachable from the host.
4. If you also use Cursor / Claude Code / Gemini-CLI: same audit applies — even though vendors didn't issue CVEs, the pattern (MCP-injected `mcp.json` modification) is real. Keep all four tools current and avoid connecting MCPs to user-generated-content surfaces.

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run agents in a devcontainer so even a successful RCE is sandboxed.

**Pattern to internalize:** any AI tool that writes to its own configuration file based on instructions in fetched content is a candidate for this class. Defense: lock down what content the agent can fetch, and review every `mcp.json` change.

## Sources
- [PolicyLayer — CVE-2026-30615: Windsurf Zero-Click MCP Prompt Injection RCE](https://policylayer.com/mcp-incidents/windsurf-zero-click-mcp-rce-cve-2026-30615)
- [OX Security — The Mother of All AI Supply Chains: Critical, Systemic Vulnerability at the Core of MCP](https://www.ox.security/blog/the-mother-of-all-ai-supply-chains-critical-systemic-vulnerability-at-the-core-of-the-mcp/)
- [VentureBeat — 200,000 MCP servers expose a command execution flaw](https://venturebeat.com/security/mcp-stdio-flaw-200000-ai-agent-servers-exposed-ox-security-audit)
- [Witness AI — Windsurf security: risks, CVEs, and enterprise governance](https://witness.ai/blog/windsurf-security/)
- [Tom's Hardware — Anthropic's Model Context Protocol includes a critical RCE vulnerability](https://www.tomshardware.com/tech-industry/artificial-intelligence/anthropics-model-context-protocol-has-critical-security-flaw-exposed)
