---
id: 2025-07-cursor-curxecute-mcpoison
title: "Cursor CurXecute (CVE-2025-54135) + MCPoison (CVE-2025-54136) + case-sensitivity bypass (CVE-2025-59944)"
date_disclosed: 2025-07
last_updated: 2026-05-16
severity: high
status: patched
ecosystems: [cursor, mcp]
tools_affected: [cursor]
tags: [prompt-injection, mcp, cursor, rce, configuration-bypass]
---

## TL;DR
Three Cursor IDE vulnerabilities, all patched, all worth understanding because the patterns recur. **CurXecute** (CVE-2025-54135, CVSS 8.6) let prompt injection from an MCP server modify `mcp.json` and auto-execute attacker code. **MCPoison** (CVE-2025-54136) bound trust to the MCP server *name* not its command — flip the command later, get persistent backdoor. **CVE-2025-59944** was a case-sensitivity bypass on file protections enabling RCE via untrusted content.

## What happened

### CurXecute (CVE-2025-54135, CVSS 8.6)
- Attacker sends a crafted prompt injection through an MCP source (the PoC used a public Slack channel that Cursor was connected to via the Slack MCP).
- The injection instructs Cursor to modify `mcp.json` to add a new MCP server pointing at an attacker-controlled command.
- New MCP entries are **auto-started without confirmation**.
- The attacker now has command execution on the dev machine.
- Reported 2025-07-07. Patched in Cursor 1.3 (released 2025-07-29).

### MCPoison (CVE-2025-54136)
- Cursor's trust model for MCP servers was keyed on the **MCP server name**, not on `command` + `args`.
- An attacker (or compromised teammate) could approve a benign MCP at one command, then later change the command in `mcp.json` to something malicious.
- Trust persisted across the change. Result: persistent, user-approved backdoor.
- Patched: trust now reflects command and args.

### CVE-2025-59944 (case-sensitivity bypass)
- File-protection checks were case-sensitive while the underlying filesystem (macOS HFS+, default APFS, NTFS) was case-insensitive.
- Untrusted content could write to protected configuration paths via a different-case path and bypass the check.
- Patched in Cursor 1.7.

## Am I affected?
You are affected if you ran a vulnerable Cursor version (pre-1.3 for CurXecute/MCPoison, pre-1.7 for the case-sensitivity bug) **and** connected MCP servers that ingest untrusted content (Slack, GitHub issues, public docs, user-submitted data).

```bash
# Check Cursor version
cursor --version
```

If pre-1.7, update. Also audit your `~/.cursor/mcp.json` and project-level `.cursor/mcp.json` for entries you don't recognize:

```bash
cat ~/.cursor/mcp.json
find . -name "mcp.json" -not -path "*/node_modules/*"
```

## If you are affected
1. Update Cursor to ≥1.7.
2. Review every `mcp.json` for unknown server entries; delete anything you don't actively use.
3. For each MCP server, verify the `command` is what you originally approved.
4. Treat any data fetched from MCP-connected SaaS (Slack, GitHub issues, Notion) as untrusted user input — never let the agent act on it without review.

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)

General pattern: **Any time an agent reads from a source where strangers can write, you have a prompt-injection surface.** Public Slack channels, GitHub issues, support tickets, contact forms — all are write-by-anyone. Don't let the agent take privileged action on data from those sources.

## Sources
- [Check Point Research — Cursor IDE's MCP Vulnerability](https://research.checkpoint.com/2025/cursor-vulnerability-mcpoison/)
- [Check Point Blog — Cursor IDE: Persistent Code Execution via MCP Trust Bypass](https://blog.checkpoint.com/research/cursor-ide-persistent-code-execution-via-mcp-trust-bypass/)
- [Tenable — FAQ: CVE-2025-54135, CVE-2025-54136](https://www.tenable.com/blog/faq-cve-2025-54135-cve-2025-54136-vulnerabilities-in-cursor-curxecute-mcpoison)
- [Aim Security — CurXecute: RCE in Cursor via MCP Auto-Start](https://www.aim.security/post/when-public-prompts-turn-into-local-shells-rce-in-cursor-via-mcp-auto-start)
- [Lakera — Cursor Vulnerability (CVE-2025-59944)](https://www.lakera.ai/blog/cursor-vulnerability-cve-2025-59944)
- [GitHub Advisory — GHSA-4cxx-hrm3-49rm](https://github.com/cursor/cursor/security/advisories/GHSA-4cxx-hrm3-49rm)
- [Bleeping Computer — AI-powered Cursor IDE vulnerable to prompt-injection attacks](https://www.bleepingcomputer.com/news/security/ai-powered-cursor-ide-vulnerable-to-prompt-injection-attacks/)
