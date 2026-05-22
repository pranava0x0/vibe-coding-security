---
id: 2026-04-comment-and-control-pr-injection
title: "'Comment and Control' — prompt injection via GitHub PRs/issues hits Claude Code Security Review, Gemini CLI Action, Copilot Agent (April 2026)"
date_disclosed: 2026-04
last_updated: 2026-05-22
severity: critical
status: patched
ecosystems: [claude-code, gemini-cli, github-copilot, github-actions]
tools_affected: [claude-code-security-review, gemini-cli-action, github-copilot-agent]
tags: [prompt-injection, indirect-prompt-injection, github-actions, cve, exfiltration, comment-and-control]
---

## TL;DR
Researcher Aonan Guan (with JHU's Zhengyu Liu and Gavin Zhong) disclosed **"Comment and Control"** in April 2026: a class of prompt-injection attack where a payload in a GitHub **PR title, issue body, or comment** is processed by an AI coding agent that treats the attacker's text as trusted and executes it — typically exfiltrating API keys and access tokens from the Actions runner. Hit Anthropic's Claude Code Security Review (CVSS **9.4 Critical**), Google's Gemini CLI Action, and GitHub Copilot Agent. All patched.

## What happened
A new contributor (or any internet stranger, on a public repo) opens a PR or issue containing crafted natural-language instructions. When the AI agent later processes that text — for security review, code review, summarization, triage — it follows the embedded instructions as if they came from the repo owner. Typical payloads:

- Read environment variables / secrets from the Actions runner.
- Print them as innocuous-looking artifacts (rendered into a PR comment, written to logs, embedded in a summary).
- Or: rewrite code in the PR to install a backdoor before the human reviewer signs off.

Anthropic's own system card explicitly noted Claude Code Security Review was **"not hardened against prompt injection"** — which is exactly what got exploited.

Bounty awards (a useful proxy for vendor seriousness): Anthropic $100 (despite the CVSS 9.4 rating), Google $1,337, GitHub $500.

### Sibling: Gemini CLI GitHub-issue RCE (CVSS 10.0)
A separate but mechanically identical flaw in **Google Gemini CLI** earned a full **CVSS 10.0**. In headless mode Gemini CLI **auto-trusts any workspace folder** it's active in for loading config and env vars, and in `--yolo` mode it **ignores tool allowlists and auto-approves every tool call**. An attacker who plants hidden instructions in a **public GitHub issue** on a repo whose auto-triage agent runs in that mode gets arbitrary host command execution — the same "untrusted issue text → AI agent runs commands" shape as Comment and Control. Discovered by Elad Meged (Novee Security) and Dan Lisichkin (Pillar Security); **fixed in `@google/gemini-cli` 0.39.1 and 0.40.0-preview.3**. If you run Gemini CLI in CI, never combine `--yolo` with untrusted workspace content.

## Am I affected?

You are affected if **any** of these are true and the runner has access to repo secrets:

- You use **Claude Code Security Review** (a GitHub Action) on a public or open-to-contributor repo.
- You use **Gemini CLI Action** to process PR/issue content automatically.
- You use **GitHub Copilot Coding Agent** with auto-triage / auto-review on a public repo.
- You use any *other* AI agent on Actions that reads PR/issue/comment text and has access to repo secrets, cloud OIDC, or write tokens.

```bash
# Find AI-agent workflows in your repos
grep -rE "claude-code-security-review|gemini-cli|copilot-agent|anthropic-action" .github/workflows/

# Check which workflows run on `issue_comment` / `pull_request` / `pull_request_target` triggers
grep -lE "on:.*(issue_comment|pull_request)" .github/workflows/*.yml
```

## If you are affected
1. **Update to patched versions** of Claude Code Security Review, Gemini CLI Action, and Copilot Agent.
2. **Audit Actions logs** for the period the vulnerable version was running. Look for unexpected env-var-printing, network calls, or comment posts.
3. **Rotate every secret** the agent's workflow had access to. Especially: cloud OIDC roles, third-party API keys, npm tokens, deployment keys.
4. **Restrict the trigger.** For PR-triggered AI workflows, prefer `pull_request` (no secrets) over `pull_request_target` (has secrets). If you must use the latter, require manual approval (`environments` with required reviewers) before the agent runs.
5. **Don't let agents read attacker-controllable content with access to secrets.** This is the "lethal trifecta" applied to CI: untrusted content + privileged context + external communication = exfiltration.

## Prevention going forward
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — "lethal trifecta" framing applies to CI too.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

Specific to GitHub Actions:
- Use `permissions: contents: read` by default; only grant write or `id-token: write` where necessary.
- Use `actions/dependency-review-action` and [`zizmor`](https://github.com/woodruffw/zizmor) to scan workflows.
- For AI review agents, prefer running on a **trusted post-merge step** rather than on every PR comment from the public.

## Why it matters even after the patch
The CVE is fixed, but the **pattern is permanent**. Every "AI reads our issues and helps triage" feature is potentially this attack. As more orgs wire Claude / Gemini / Copilot into their issue tracker, the surface grows. Vendor hardening helps; thoughtful trigger configuration helps more.

## Sources
- [VentureBeat — Three AI coding agents leaked secrets through a single prompt injection](https://venturebeat.com/security/ai-agent-runtime-security-system-card-audit-comment-and-control-2026)
- [SecurityWeek — Claude Code, Gemini CLI, GitHub Copilot Agents Vulnerable to Prompt Injection via Comments](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/)
- [Microsoft Security Blog — When prompts become shells: RCE vulnerabilities in AI agent frameworks](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)
- [Waxell — AI Coding Agent Prompt Injection: CI/CD Risk](https://waxell.ai/blog/ai-coding-agent-prompt-injection-cicd-2026)
- [Palo Alto Unit 42 — Fooling AI Agents: Web-Based Indirect Prompt Injection Observed in the Wild](https://unit42.paloaltonetworks.com/ai-agent-prompt-injection/)
- [TechRepublic — Indirect Prompt Injection Is Now a Real-World AI Security Threat](https://www.techrepublic.com/article/news-ai-agents-prompt-injection-data-security/)
- [Dark Reading — 'TrustFall' Convention Exposes Claude Code Execution Risk](https://www.darkreading.com/application-security/trustfall-exposes-claude-code-execution-risk)
- [SecurityWeek — Critical Gemini CLI Flaw Enabled Host Code Execution, Supply Chain Attacks](https://www.securityweek.com/critical-gemini-cli-flaw-enabled-host-code-execution-supply-chain-attacks/) — Gemini CLI CVSS 10.0 sibling, fixed 0.39.1.
- [Pillar Security — My Agentic Trust Issues: From Prompt Injection to Supply-Chain Compromise on gemini-cli](https://www.pillar.security/blog/my-agentic-trust-issues-from-prompt-injection-to-supply-chain-compromise-on-gemini-cli) — canonical research (Novee + Pillar).
