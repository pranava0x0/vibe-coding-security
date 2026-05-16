---
id: 2025-08-claude-code-inverseprompt
title: "Claude Code InversePrompt (CVE-2025-54794, CVE-2025-54795)"
date_disclosed: 2025-08
last_updated: 2026-05-16
severity: medium
status: patched
ecosystems: [claude-code]
tools_affected: [claude-code]
tags: [prompt-injection, claude-code, mcp, indirect-prompt-injection]
---

## TL;DR
Two CVEs in Claude Code (CVE-2025-54794 and CVE-2025-54795), disclosed by Cymulate, demonstrated that indirect prompt injection in content Claude Code reads (web pages, repo READMEs, MCP-fetched content) could be chained to invoke its own tools against the user. Patched, but the **class of attack is permanent**: any agent that mixes trusted instructions with untrusted content is vulnerable.

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
- [Lasso Security — Detecting Indirect Prompt Injection in Claude Code](https://www.lasso.security/blog/the-hidden-backdoor-in-claude-coding-assistant)
- [Checkmarx — Claude Code Security: Top 6 Risks, Controls, and Best Practices](https://checkmarx.com/learn/ai-security/claude-code-security-top-6-risks-controls-and-best-practices/)
- [The Register — Claude Code bypasses safety rule if given too many commands](https://www.theregister.com/2026/04/01/claude_code_rule_cap_raises/)
- [Anthropic — Claude Code Security docs](https://code.claude.com/docs/en/security)
- [TrueFoundry — Claude Code --dangerously-skip-permissions](https://www.truefoundry.com/blog/claude-code-dangerously-skip-permissions)
