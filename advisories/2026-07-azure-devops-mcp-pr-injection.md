---
id: 2026-07-azure-devops-mcp-pr-injection
title: "Azure DevOps MCP server — invisible HTML comments in PR descriptions hijack AI review agents across projects (MSRC triaged, no fix yet)"
date_disclosed: 2026-07-21
last_updated: 2026-07-22
severity: high
status: active
ecosystems: [mcp, azure-devops, microsoft]
tools_affected: ["Azure DevOps MCP server (microsoft/azure-devops-mcp)", "GitHub Copilot CLI", "Claude Code"]
tags: [prompt-injection, indirect-prompt-injection, mcp, confused-deputy, comment-and-control, microsoft]
---

## TL;DR

Manifold Security disclosed a **confused-deputy prompt-injection flaw** in Microsoft's official `azure-devops-mcp` server: the tool that returns pull-request descriptions to an AI agent (`repo_get_pull_request_by_id`) doesn't apply the "spotlighting" delimiters Microsoft already uses to mark untrusted content in its other tools (wikis, pipelines). An attacker with only contributor access to **one** Azure DevOps project can hide instructions inside **invisible HTML comments** in a PR description — rendered as nothing in the Azure DevOps web UI, but returned verbatim to the AI agent via the API — and hijack a reviewer's agent (validated against both **GitHub Copilot CLI** and **Claude Code**) into taking actions in **other projects** the attacker can't reach directly, using the victim's own credentials. Microsoft (MSRC) acknowledged and triaged the report; no CVE and no shipped fix as of 2026-07-21/22.

## What happened

Microsoft's official `microsoft/azure-devops-mcp` server exposes tools that let an AI coding agent read and act on Azure DevOps projects — pull requests, wikis, pipelines — on a developer's behalf. Microsoft had already applied a guardrail called **"spotlighting"** to several of these tools: wrapping untrusted, externally-supplied content (wiki pages, pipeline output) in explicit delimiters so the underlying model can distinguish "this is data from an untrusted source" from "this is an instruction I should follow."

Manifold Security found that this guardrail was **not applied to the `repo_get_pull_request_by_id` tool**, which returns a pull request's description raw. Since Azure DevOps' own web UI renders **HTML comments** (`<!-- ... -->`) as invisible, a human reviewer sees a normal-looking PR description — but the REST API (and therefore the MCP tool) returns the hidden comment text verbatim, with no delimiters marking it as untrusted. An AI agent invoked to summarize or review that PR receives the hidden instructions as if they were part of the same trusted context as the rest of its conversation, and — because there's no spotlighting on this specific tool — treats them as commands rather than data to be skeptical of.

The researchers validated the attack end-to-end against **GitHub Copilot CLI** and **Claude Code**, both configured to use the Azure DevOps MCP server: an attacker with contributor access to Project A plants a hidden instruction in a PR description; when a developer with broader access (including to Project B, which the attacker cannot reach directly) asks their agent to review or summarize that PR, the agent — using the victim's own MCP-authenticated credentials — carries out attacker-directed actions scoped to whatever the victim's account can reach, not just Project A.

Manifold reported the finding to Microsoft, who **acknowledged and triaged** it via MSRC and characterized it as a "known class of AI risk" informing ongoing safeguard work, but recommended interim mitigations (limiting project access scope, reviewing PR content before invoking AI tools on it) rather than committing to an immediate structural fix. **No CVE has been assigned**, and as of the 2026-07-21/22 disclosure the vulnerable code path — including in the MCP server's `v2.8.0` release (2026-06-24) — remains unpatched.

This is the same underlying vulnerability class this repo already tracks as **["Comment and Control"](2026-04-comment-and-control-pr-injection.md)** (hidden instructions in GitHub PR/issue text hijacking Claude Code Security Review, Gemini CLI Action, and GitHub Copilot Agent) and **[GitLost](2026-07-gitlost-github-agentic-workflows-injection.md)** (public GitHub Issue text prompt-injecting GitHub Agentic Workflows into leaking private-repo content) — confirming the pattern generalizes beyond GitHub to **Microsoft's own separate Azure DevOps product and its own official MCP server**, and specifically to the "confused deputy" shape where the injected instruction causes the agent to act *across* trust boundaries the attacker themselves cannot cross (compare also [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md), the Sentry-MCP instance of "any MCP server returning user-controlled content is an indirect-prompt-injection surface").

## Am I affected?

You are affected if you use the **Azure DevOps MCP server** (`microsoft/azure-devops-mcp`) with any AI coding agent (Copilot CLI, Claude Code, or others) and:

- The agent's Azure DevOps credentials/PAT have access to more than one project, or to any project the PR author shouldn't be able to reach.
- Your workflow includes asking an agent to summarize, review, or act on pull requests from external or lower-trust contributors.

```bash
# Check for HTML comments in PR descriptions before letting an agent process them
# (Azure DevOps CLI) — inspect raw PR description for hidden <!-- --> content
az repos pr show --id <PR_ID> --query "description" -o tsv | grep -o '<!--.*-->'
```

## If you are affected

1. Scope the Azure DevOps PAT/credential used by your AI agent to the **minimum set of projects** it actually needs — never a broad, org-wide token.
2. Review pull request descriptions for hidden HTML comments (`grep -o '<!--.*-->'`) before invoking an AI agent on unfamiliar or external-contributor PRs.
3. Avoid combining an agent with cross-project access with auto-review/auto-summarize triggers on PRs from contributors you don't fully trust.
4. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) if you suspect this has already been exploited against your organization.

## Prevention

→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — the "lethal trifecta" (untrusted content + privileged access + ability to act) applies here exactly as it does to GitHub-hosted agents.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

- Split trust domains: don't let one agent identity hold both "can read PRs from any contributor" and "can act across every project in the org."
- Treat any MCP tool that returns externally-editable text (PR/issue descriptions, comments, wiki content) as untrusted input requiring explicit delimiting — don't assume a vendor has applied this consistently across every tool in their own MCP server just because they've done it for some.

## Sources

- [Manifold Security — Azure DevOps MCP Server Vulnerability](https://www.manifold.security/blog/azure-devops-mcp-server-vulnerability) — primary technical disclosure; root cause, PoC against Copilot CLI and Claude Code, MSRC response.
- [The Hacker News — Microsoft Azure DevOps MCP Flaw Lets Hackers Hijack AI Agents via Hidden PR Comments](https://thehackernews.com/2026/07/microsoft-azure-devops-mcp-flaw-lets.html) — independent corroboration, 2026-07-22.
