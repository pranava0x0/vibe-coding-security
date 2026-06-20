---
id: 2025-09-litl-ai-approval-dialog-bypass
title: "'Lies in the Loop' (LITL) — approval-dialog padding hides malicious commands below the fold in Claude Code and VS Code Copilot (Sept 2025, no vendor fix)"
date_disclosed: 2025-09-01
last_updated: 2026-06-20
severity: high
status: active
ecosystems: [claude-code, vscode-copilot]
tools_affected: [Claude Code (Anthropic), GitHub Copilot Chat in VS Code (Microsoft)]
tags: [prompt-injection, indirect-prompt-injection, approval-dialog, hitl-dialog-forging, rce, claude-code, vendor-wont-fix]
---

## TL;DR

**Checkmarx Zero** disclosed **"Lies in the Loop" (LITL)**, also called **HITL Dialog Forging**, in September 2025: attacker-controlled content delivered via indirect prompt injection can pad an AI coding agent's approval dialog with hundreds of blank lines or zero-width Unicode characters, pushing the malicious part of a compound shell command **below the visible fold**. The developer sees and approves what looks like a safe command; the hidden payload executes simultaneously. Affects **Claude Code** (Anthropic) and **GitHub Copilot Chat** in VS Code (Microsoft). **Anthropic classified the finding as "Informative" and outside its current threat model. Microsoft acknowledged the report but closed it without implementing a fix.** Neither vendor has shipped a structural fix as of **2026-06-14**.

## What happened

Checkmarx Zero researchers discovered that AI coding agents that use **Human-in-the-Loop (HITL) confirmation dialogs** — the approval prompts that ask developers "OK to run this command?" before executing potentially dangerous shell operations — can be manipulated via indirect prompt injection to show the developer a **truncated, safe-looking portion** of a command, while the **full command** (including malicious additions) executes when the developer clicks "approve."

### The attack mechanism

**Indirect prompt injection is the delivery vehicle.** An attacker plants a malicious instruction in content the AI agent will read: a public GitHub issue, a repository README, a malicious dependency's documentation, an LLM-fetched web page, or any other attacker-controlled text that enters the agent's context. The injected instruction tells the agent to construct a compound shell command containing:

1. A **visible, harmless-looking portion** (e.g., `npm install && npm test`) — what the developer sees.
2. **Hundreds of blank lines or zero-width Unicode characters** — padding that fills the dialog window.
3. A **malicious payload** appended after the padding (e.g., credential exfiltration, backdoor installation, data destruction) — what scrolls below the visible area.

The developer, reviewing the approval dialog, sees a benign-looking command at the top. The dialog appears complete. They approve. The entire compound command — including the hidden payload — executes.

In Claude Code (which runs in a VS Code terminal), the HITL dialog is distinguished from surrounding terminal output only by a thin 1-pixel border, making it easy to miss that the dialog's content extends beyond the visible window. The same truncation attack applies to VS Code's Copilot Chat approval prompts.

### Vendor responses

**Anthropic (Claude Code):** Checkmarx disclosed the LITL attack to Anthropic in **August 2025**. Anthropic classified both the underlying command injection primitive and the HITL Dialog Forging technique as **"Informative"** and **"outside our current threat model."**

**Microsoft (VS Code Copilot Chat):** Microsoft acknowledged the report in **October 2025** but **marked it as completed without implementing fixes** by November 2025.

As a result, **neither tool has a structural fix as of June 2026**. The attack remains viable against both tools whenever an attacker can inject content into the agent's context.

### Why this matters for vibe coders

LITL compounds **any** indirect prompt injection finding. If attacker-controlled text can reach the agent's context — via a poisoned README, a malicious MCP tool response ([Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md)), a GitHub issue, or fetched web content — LITL can then manipulate the approval dialog to make dangerous commands appear safe. The combination means:

- Even when `--dangerously-skip-permissions` is NOT set, approval dialogs do not provide robust protection.
- The LITL attack is particularly dangerous in agentic pipelines where the agent processes external content (issues, PRs, web pages, MCP data) before making tool calls.
- Removing the approval dialog (via `--dangerously-skip-permissions`) eliminates LITL as an attack surface, but also removes all human oversight — a tradeoff that helps attackers in the opposite direction.

LITL is the **approval-dialog analogue** of CSS invisible-text injection in fetched web pages (the [InversePrompt](2025-08-claude-code-inverseprompt.md) class) — the same "make the AI do something the human can't see" shape, applied to the human-approval surface instead of the agent's input.

## Am I affected?

You are at elevated risk if you:

- Use **Claude Code** or **VS Code GitHub Copilot Chat** with approval dialogs enabled.
- Regularly process **external content** in the agent's context: public GitHub issues/PRs, web pages fetched by the agent, MCP server outputs that contain user-generated data (Sentry error events, GitHub issue bodies, Slack messages, etc.).
- Work in **agentic pipelines** where the agent reads untrusted content autonomously and then proposes shell commands.

```bash
# Test your own exposure: check if your terminal/dialog renders long commands truncated
# In Claude Code, run a test with a long compound command to see how the approval dialog renders
# If the dialog scrolls, content below the initial viewport is hidden by default

# Audit your workflow for LITL-susceptible patterns:
# - Any AI agent that reads GitHub issues/PRs and then runs shell commands
# - Any MCP tool that returns user-controlled content (Sentry, Slack, Linear, Jira)
# - Any agentic pipeline that fetches external URLs before proposing commands
```

There is **no reliable way to detect if you have already been exploited** via LITL — the attack leaves the same footprint as any normally-approved command execution.

## If you are affected

If you believe you approved a command that turned out to be malicious:

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — treat as a full agent compromise, rotate all credentials the agent had access to.

## Prevention

Neither Anthropic nor Microsoft has implemented a structural fix. The practical mitigations are procedural:

1. **Always scroll to the bottom of the approval dialog before approving.** If the dialog is long or you cannot see where it ends, use your terminal's scroll capability to inspect the full command before clicking approve. In Claude Code, look for the 1-pixel border that delimits the HITL dialog.

2. **Reject all compound commands (`;`, `&&`, `||` chains, backtick substitution, piped commands) that you haven't reviewed in full.** LITL requires a compound command to hide the malicious payload after padding. A single, simple command can't be exploited this way — only compound commands with content after the padding.

3. **Distrust AI-agent commands when the agent has recently processed external content.** If your agent just fetched a GitHub issue, a web page, or an MCP tool response containing user-generated data, treat its next proposed command as potentially injected.

4. **Limit the agent's MCP connections when operating in autonomous mode.** Remove MCP servers that return user-controlled content (Sentry, Slack, email, GitHub issues) when the agent is also permitted to execute shell commands. The [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md) attack delivers injection payloads through exactly these servers.

5. **`--dangerously-skip-permissions` removes the approval dialog entirely** — it eliminates LITL as an attack surface but also removes all human-in-the-loop oversight. Don't use this mode with untrusted workspace content.

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — structural approach to limiting what a compromised agent can execute.

## Sources

- [Checkmarx Zero — "Bypassing AI Agent Defenses With Lies-In-The-Loop"](https://checkmarx.com/zero-post/bypassing-ai-agent-defenses-with-lies-in-the-loop/) — primary researcher disclosure, LITL mechanism, vendor responses.
- [Security Boulevard — "Checkmarx Surfaces Lies-in-the-Middle Attack to Compromise AI Tools"](https://securityboulevard.com/2025/09/checkmarx-surfaces-lies-in-the-middle-attack-to-compromise-ai-tools/) — September 2025 publication date confirmation, vendor response timeline.
- [Dark Reading — "'Lies-in-the-Loop' Attack Defeats AI Coding Agents"](https://www.darkreading.com/application-security/-lies-in-the-loop-attack-ai-coding-agents) — audience-appropriate framing, impact assessment.
- [Infosecurity Magazine — "New 'Lies-in-the-Loop' Attack Undermines AI Safety Dialogs"](https://www.infosecurity-magazine.com/news/lies-loop-attack-ai-safety-dialogs/) — independent coverage confirming attack class.
- Cross-reference: [2026-06-agentjacking-sentry-mcp-injection.md](2026-06-agentjacking-sentry-mcp-injection.md) — Agentjacking is the primary indirect-injection delivery surface for LITL payloads.
- Cross-reference: [2025-08-claude-code-inverseprompt.md](2025-08-claude-code-inverseprompt.md) — sibling class: invisible-text injection in agent input vs. approval-dialog padding.
