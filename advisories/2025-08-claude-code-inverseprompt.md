---
id: 2025-08-claude-code-inverseprompt
title: "Claude Code InversePrompt and follow-on CVEs (multiple)"
date_disclosed: 2025-08
last_updated: 2026-05-18
severity: medium
status: patched
ecosystems: [claude-code]
tools_affected: [claude-code]
tags: [prompt-injection, claude-code, mcp, indirect-prompt-injection, cve, trustfall]
---

## TL;DR
A growing collection of Claude Code CVEs — **CVE-2025-54794, CVE-2025-54795** (Cymulate's "InversePrompt", Aug 2025), **CVE-2025-52882** (information disclosure), **CVE-2025-59536**, **CVE-2026-21852** ("Leaks Data via Malicious Environment Configuration Before Trust Confirmation"), **CVE-2026-33068**, the **"TrustFall" convention exposure** (early 2026), plus the May 2026 cluster: **CVE-2026-24887** (find-command confirmation-bypass RCE; patched in Claude Code 2.0.72), **CVE-2026-35021** (OS-command injection via prompt-editor file path), **CVE-2026-39861** (symlink-following sandbox escape — arbitrary file write outside the workspace), and **CVE-2026-35603** (Claude Code privilege escalation). All patched by Anthropic — update Claude Code to the latest version. Lasso Security and Dark Reading have both covered the broader pattern: **the class of attack is permanent**, because any agent that mixes trusted instructions with untrusted content is fundamentally vulnerable. See also the related [Comment and Control](2026-04-comment-and-control-pr-injection.md) chain (CVSS 9.4 Critical) and the [Claude Code source-map leak](2026-03-claude-code-source-map-leak.md) that preceded much of this CVE cluster.

## What happened
The InversePrompt research showed several routes to indirect prompt injection in Claude Code:

- **Hidden text in fetched web pages.** Claude reads a URL for research; the page contains attacker instructions in invisible CSS or off-screen elements.
- **Malicious READMEs in cloned repos.** Cloning a repo and asking Claude to "explore" it loads attacker-controlled markdown into context.
- **MCP-delivered prompts.** A connector that returns user-generated content (Slack, Notion, GitHub issues) can deliver attacker instructions.
- **Document smuggling.** Later, in early 2026, PromptArmor demonstrated 1-point white-on-white text in `.docx` files manipulating Claude into exfiltrating files via the Anthropic Files API.

A separate, related class: in December 2025 a user asked Claude Code to clean up packages and Claude generated `rm -rf tests/ patches/ plan/ ~/`. The shell expanded `~/` to the home directory and wiped it. Not strictly InversePrompt, but the same root cause — agent tool calls without sufficient confirmation.

## Am I affected?

You are affected by the *class* if any of these are true:
- You run Claude Code with `--dangerously-skip-permissions` outside a sandbox.
- You let Claude Code fetch arbitrary URLs without pre-approval.
- You've connected MCP servers that return user-generated content (Slack, Notion, GitHub issues, email).
- You let Claude Code execute `rm -rf`, `git push`, or destructive shell commands without manual review.

You are affected by the *specific CVEs* only if you ran Claude Code at the affected version before the patch shipped — update to the latest version.

## If you are affected
1. Update Claude Code to the latest version (`npm i -g @anthropic-ai/claude-code` or `claude update`).
2. Stop using `--dangerously-skip-permissions` on the host. If you need it, run inside a devcontainer or VM — see [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
3. Treat anything Claude fetches from outside your repo as untrusted input.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — sandbox everything that can shell out
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — limit MCP servers' read scope

The general defensive posture from Anthropic's own [Claude Code security docs](https://code.claude.com/docs/en/security):
- Never run agents with elevated permissions on the host.
- Review every shell command and file edit before approving.
- Limit the URLs and MCP sources the agent can read.
- Run untrusted exploration inside a container.

## Sources
- [Cymulate — InversePrompt: Turning Claude Against Itself (CVE-2025-54794 & CVE-2025-54795)](https://cymulate.com/blog/cve-2025-547954-54795-claude-inverseprompt/)
- [SentinelOne — CVE-2025-52882: Claude Code Information Disclosure Flaw](https://www.sentinelone.com/vulnerability-database/cve-2025-52882/)
- [GitHub Advisory — CVE-2026-21852: Claude Code Leaks Data via Malicious Environment Configuration Before Trust Confirmation](https://github.com/advisories/GHSA-jh7p-qr78-84p7)
- [Dark Reading — 'TrustFall' Convention Exposes Claude Code Execution Risk](https://www.darkreading.com/application-security/trustfall-exposes-claude-code-execution-risk)
- [Dark Reading — Flaws in Claude Code Put Developers' Machines at Risk](https://www.darkreading.com/application-security/flaws-claude-code-developer-machines-risk)
- [Lasso Security — Detecting Indirect Prompt Injection in Claude Code](https://www.lasso.security/blog/the-hidden-backdoor-in-claude-coding-assistant)
- [Checkmarx — Claude Code Security: Top 6 Risks, Controls, and Best Practices](https://checkmarx.com/learn/ai-security/claude-code-security-top-6-risks-controls-and-best-practices/)
- [The Register — Claude Code bypasses safety rule if given too many commands](https://www.theregister.com/2026/04/01/claude_code_rule_cap_raises/)
- [Anthropic — Claude Code Security docs](https://code.claude.com/docs/en/security)
- [TrueFoundry — Claude Code --dangerously-skip-permissions](https://www.truefoundry.com/blog/claude-code-dangerously-skip-permissions)
- [SentinelOne — CVE-2026-24887: Claude Code RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-24887/)
- [SentinelOne — CVE-2026-35021: Claude Code CLI OS Command Injection RCE](https://www.sentinelone.com/vulnerability-database/cve-2026-35021/)
- [SentinelOne — CVE-2026-39861: Anthropic Claude Code RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-39861/)
- [SentinelOne — CVE-2026-35603: Claude Code Privilege Escalation Flaw](https://www.sentinelone.com/vulnerability-database/cve-2026-35603/)
- [GitHub Advisory — CVE-2026-24887: Command Injection in find Command Bypasses User Approval Prompt (GHSA-qgqw-h4xq-7w8w)](https://github.com/advisories/GHSA-qgqw-h4xq-7w8w)
- [GitHub Advisory — CVE-2026-39861: Sandbox Escape via Symlink Following (GHSA-vp62-r36r-9xqp)](https://github.com/advisories/GHSA-vp62-r36r-9xqp)
- [Phoenix Security — Claude Code leak to vulnerability: Three CVEs in Claude Code CLI and the Chain That Connects Them](https://phoenix.security/claude-code-leak-to-vulnerability-three-cves-in-claude-code-cli-and-the-chain-that-connects-them/)
- [CSO Online — Claude Code is still vulnerable to an attack Anthropic has already fixed](https://www.csoonline.com/article/4154201/claude-code-is-still-vulnerable-to-an-attack-anthropic-has-already-fixed-2.html)
- [DevOps.com — Security Flaws in Anthropic's Claude Code Risk Stolen Data, System Takeover](https://devops.com/security-flaws-in-anthropics-claude-code-risk-stolen-data-system-takeover/)
