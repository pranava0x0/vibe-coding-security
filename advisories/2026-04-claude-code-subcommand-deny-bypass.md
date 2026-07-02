---
id: 2026-04-claude-code-subcommand-deny-bypass
title: "Claude Code deny-rule bypass via 50-subcommand parser cap (silently patched in v2.1.90)"
date_disclosed: 2026-04-02
last_updated: 2026-07-02
severity: high
status: patched
ecosystems: [claude-code, anthropic]
tools_affected: [claude-code]
tags: [claude-code, permission-bypass, deny-rule, silent-patch, source-leak]
---

## TL;DR
Adversa AI found that Claude Code's bash-command permission checker (`bashPermissions.ts`) **stopped enforcing configured deny rules entirely** on any compound shell command with more than **50 subcommands** — instead of blocking, it fell back to a generic "allow?" prompt. Discovered via the leaked Claude Code source, disclosed **2026-04-02**, and traced to the same release — **v2.1.90 (2026-04-01/04)** — that silently fixed the unrelated [SOCKS5 null-byte sandbox bypass](2026-05-claude-code-sandbox-socks5-bypass.md). No CVE assigned.

## What happened
Claude Code lets users configure **deny rules** — commands the agent should never be allowed to run regardless of what it's asked to do. The legacy regex-based parser in `bashPermissions.ts` analyzed each subcommand in a compound shell string (chained with `&&`, `||`, or `;`) individually against those rules. Anthropic's internal ticket **CC-643** documents that this per-subcommand analysis caused the UI to freeze on very long compound commands, so a **hard cap of 50 subcommands** was added: past that threshold, the parser **stops enforcing deny rules and falls back to a generic permission prompt** instead of refusing the command.

Adversa AI's proof of concept: a shell command consisting of 50 harmless no-op subcommands followed by a `curl` command that should have hit a deny rule. Claude Code, having exhausted its 50-subcommand analysis budget, presented a normal "allow this?" prompt instead of blocking outright — meaning any deny rule a developer or org configured could be defeated simply by padding the command with enough no-ops. Anthropic's codebase reportedly already contained a safer **tree-sitter**-based parser that handles this correctly regardless of command length, but it had not shipped to public builds at time of disclosure.

This is a **different bug** from the [SOCKS5 sandbox null-byte bypass](2026-05-claude-code-sandbox-socks5-bypass.md) disclosed by a different researcher (Aonan Guan) — different root cause (parser resource cap vs. hostname-matcher/OS disagreement), different subsystem (deny-rule permission checks vs. network egress allowlist) — but both were fixed in the **same release, v2.1.90**, and neither shipped with a CVE, public advisory, or changelog note. This is now the **third** silently-patched Claude Code security-relevant bug tracked in this repo (after CVE-2025-66479 and the SOCKS5 bypass), reinforcing the standing guidance: assume "latest" carries undisclosed fixes and don't pin old Claude Code versions.

## Am I affected?
```bash
claude --version   # fixed in v2.1.90 and later
```
If you relied on `permissions.deny` rules in `.claude/settings.json` as a hard security boundary on any version before v2.1.90, and ever ran (or an agent ever constructed) a compound command with 50+ chained subcommands, treat any deny-listed action from that session as **potentially having executed**.

## If you are affected
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if a denied command could have exfiltrated credentials.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — deny-list permission checks inside an agent are not a substitute for OS/network-level enforcement; a single parser limitation can silently disable them.
→ Keep Claude Code on auto-update. See also the [SOCKS5 sandbox bypass](2026-05-claude-code-sandbox-socks5-bypass.md) for the pattern of silently-shipped security fixes in this tool.

## Sources
- [Adversa AI — Critical Claude Code vulnerability: Deny rules silently bypassed because security checks cost too many tokens](https://adversa.ai/blog/claude-code-security-bypass-deny-rules-disabled/)
- [The Register — Claude Code bypasses safety rule if given too many commands](https://www.theregister.com/software/2026/04/01/claude-code-bypasses-safety-rule-if-given-too-many-commands/5220992)
- [SC Media — Claude Code vulnerable to prompt injection due to subcommand limit](https://www.scworld.com/brief/claude-code-vulnerable-to-prompt-injection-due-to-subcommand-limit)
- [Cybersecurity News — Critical Claude Code Vulnerability Silently Bypasses Developer-Configured Security Rules](https://cybersecuritynews.com/claude-code-vulnerability/)
