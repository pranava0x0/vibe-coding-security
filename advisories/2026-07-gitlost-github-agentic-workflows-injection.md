---
id: 2026-07-gitlost-github-agentic-workflows-injection
title: "GitLost — a public GitHub Issue can prompt-inject GitHub Agentic Workflows into leaking private repos (no full fix)"
date_disclosed: 2026-07-06
last_updated: 2026-07-08
severity: high
status: active
ecosystems: [github, ai-agents, mcp]
tools_affected: [github-agentic-workflows, github-copilot, claude, gemini, openai-codex]
tags: [prompt-injection, indirect-prompt-injection, data-exfiltration, github-actions, ai-agents, no-patch]
---

## TL;DR

**GitHub Agentic Workflows** (public preview since Feb 2026 — GitHub Actions paired with an AI agent that can be backed by GitHub Copilot, Anthropic's Claude, Google Gemini, or OpenAI Codex) will follow instructions hidden in a **public, unauthenticated GitHub Issue**. Researchers at **Noma Security** showed that prefixing an injected instruction with the word "Additionally" bypassed GitHub's threat-detection guardrails, causing an agent that also has read access to a private repo in the same org to leak that private data back out as a public issue comment. GitHub acknowledges the report but has not shipped a fix that closes the underlying design gap — its mitigations (sandboxing, read-only tokens by default, input filtering) reduce but do not eliminate the risk.

## What happened

GitHub Agentic Workflows let a repo owner configure an AI agent to read and respond to GitHub Issues automatically — a common vibe-coding pattern for auto-triage, auto-labeling, or "AI project manager" bots. The agent's context includes the issue body, which is **attacker-controlled content from anyone who can open an issue on a public repo** — no authentication or write access to the repo is required.

Noma Security's proof of concept (published 2026-07-06, corroborated same-week by The Hacker News, The Register, Dark Reading, CSO Online, and hackread) demonstrated:

1. An attacker opens an innocuous-looking public issue containing instructions phrased as ordinary follow-up requests.
2. Prefixing the injected instruction with **"Additionally"** was enough to slip past GitHub's built-in threat-detection/guardrail filtering for these workflows, so the model treated it as a legitimate continuation of the task rather than a suspicious command.
3. If the workflow's agent identity/token also has read access to a **private repository** in the same organization (a common setup for an org-wide triage bot), the injected instruction directs the agent to pull private content (the PoC used a private README) and paste it into a **public** comment on the original issue — fully exfiltrating private repo contents to anyone watching that public issue thread.

This affects any of the four model backends GitHub offers for Agentic Workflows (Copilot, Claude, Gemini, Codex) — the vulnerability is in the **workflow architecture** (trusting issue content as agent input, then allowing the same agent session broad read scope and a public write sink), not in a specific model's safety training.

**GitHub's response:** GitHub was notified prior to publication and has multiple layered mitigations already in place — sandboxed execution, read-only tokens by default, input sanitization, and threat-detection scanning on issue content. None of these constitute a structural fix: any workflow configuration that (a) reads untrusted public content, (b) has read access to sensitive data, and (c) can write to a public output sink remains exploitable. This is the same **connector-chaining lethal-trifecta** shape this repo has tracked in Claude Desktop Extensions and Windsurf's zero-click MCP RCE, applied to GitHub's own agent product.

## Am I affected?

You are potentially affected if you use **GitHub Agentic Workflows** (or any custom GitHub Actions + AI-agent automation you built yourself) with a configuration where:

```bash
# Check your repo/org for Agentic Workflow configs
find . -path '*/.github/workflows/*' -name '*.yml' | xargs grep -l -i 'agentic\|copilot-agent\|ai-agent' 2>/dev/null

# Review the token/permissions scope granted to any workflow that processes issues
gh api /repos/OWNER/REPO/actions/permissions
```

You're at risk if any single agent identity/token used by an issue-processing workflow can also read a private repo, private wiki, or any other org-internal data, **and** that same agent can write its output somewhere public (issue comments, PR comments, public wiki pages).

## If you are affected

1. **Split trust domains.** Never let one agent session hold both "reads untrusted public input" and "can read private/sensitive data" and "can write to a public sink." Use separate bot identities with minimal, non-overlapping scopes for triage-on-public-issues vs. any task that touches private repos.
2. **Disable auto-response on public issues** for any bot identity that has cross-repo or org-wide read access, until GitHub ships scoped-token support for Agentic Workflows.
3. **Audit existing workflow logs** for issue comments containing content that looks like it originated from a private repo (README fragments, internal file paths, config values).
4. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) for the general "an agent read something it shouldn't have and can write publicly" incident-response pattern — the connector-chaining shape is the same even though no MCP server is involved here.

## Prevention

- Treat every value that reaches an AI agent's context — issue bodies, PR descriptions, comments, fetched pages, MCP tool output — as untrusted input, regardless of which vendor's model is running it.
- Apply the **connector-chaining lethal-trifecta** check from [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md): if an agent session can (1) read attacker-reachable content, (2) read sensitive data, and (3) write somewhere the attacker (or the public) can see, that's a standing exfiltration primitive — break at least one leg.
- → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) for the same reader/executor separation discipline, which generalizes cleanly to non-MCP agent automations like GitHub Agentic Workflows.

## Sources

- [Noma Security — GitLost: How We Tricked GitHub's AI Agent Into Leaking Private Repos](https://noma.security/blog/gitlost-how-we-tricked-githubs-ai-agent-into-leaking-private-repos/) — primary disclosure; full attack mechanism; "Additionally" guardrail bypass; responsible disclosure to GitHub.
- [The Hacker News — Public GitHub Issue Could Trick GitHub's AI Agent Into Leaking Private Repository Data](https://thehackernews.com/2026/07/public-github-issue-could-trick-github.html) — independent corroboration; confirms affected model backends (Copilot, Claude, Gemini, Codex) and GitHub's mitigation posture.
