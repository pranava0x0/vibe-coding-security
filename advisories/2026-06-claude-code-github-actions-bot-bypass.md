---
id: 2026-06-claude-code-github-actions-bot-bypass
title: "Claude Code GitHub Actions [bot] trust bypass — supply chain risk on any repo using claude-code-action (June 2026)"
date_disclosed: 2026-06-04
last_updated: 2026-06-04
severity: high
status: patched
ecosystems: [github-actions, claude-code]
tools_affected: [Claude Code GitHub Actions (anthropics/claude-code-action), any repo using the official Anthropic CI/CD workflow]
tags: [supply-chain, github-actions, prompt-injection, privilege-escalation, bot-trust]
---

## TL;DR

`checkWritePermissions()` in Claude Code's GitHub Actions workflow **trusted any actor whose username ends in `[bot]`** regardless of actual permissions. Combined with prompt injection, an unauthenticated external attacker could exfiltrate CI secrets, steal OIDC tokens, and push malicious code to any downstream repository — including Anthropic's own `claude-code-action` source, turning it into a supply-chain vector. **Patched in Claude Code GitHub Actions v1.0.94.**

## What happened

Security researcher **RyotaK (GMO Flatt Security)** discovered a flawed permission model in `anthropics/claude-code-action`, Anthropic's official GitHub Actions workflow that lets Claude Code run autonomously in CI pipelines.

The vulnerability is in the `checkWritePermissions()` function: it granted write-level trust to any GitHub actor whose name ends with `[bot]` — a simple string suffix check that any attacker can satisfy by creating a GitHub App (whose bot identity follows the `<app-name>[bot]` naming convention) or by exploiting a bot account that has already commented on the target repository.

**Attack chain:**
1. Attacker creates a GitHub App with a name that ends in `[bot]`
2. Attacker (or prompt injection in a PR comment/issue body) triggers the Claude Code GitHub Actions workflow
3. `checkWritePermissions()` grants the attacker's actor write permissions
4. Attacker-controlled instructions run inside the Claude Code GitHub Actions agent with the CI token's full privileges:
   - Exfiltrate `$GITHUB_TOKEN`, OIDC tokens, masked CI secrets
   - Push commits or tags to the repository
   - In the worst case: inject code into `anthropics/claude-code-action` itself, which every downstream user pins to

**Why the worst case mattered:** The `anthropics/claude-code-action` repo itself was using an agentic workflow that was vulnerable. A successful exploit there would have allowed injecting malicious code into the action source that propagates to every downstream repository that depends on it — a classic second-order supply chain attack.

**Severity context:** Researcher CVSS v4.0 score of **7.8**. Anthropic awarded **$3,800 + $1,000 bonus** via its bug bounty program.

## Am I affected?

```bash
# Check if you use anthropics/claude-code-action in any workflow
grep -r "anthropics/claude-code-action" .github/workflows/

# Check which version you are pinned to
grep "anthropics/claude-code-action@" .github/workflows/*.yml
```

If you pin to a version **older than v1.0.94** or use a floating reference (e.g., `@main`, `@latest`), you were exposed.

## If you are affected

1. **Update to v1.0.94+** in all workflows using `anthropics/claude-code-action`.
2. **Audit CI logs** for any unexpected actor in the `checkWritePermissions` path — look for `[bot]` actors in PR comments/issue events that triggered the Claude Code workflow.
3. **Rotate any CI tokens or OIDC credentials** that the Claude Code workflow had access to if you suspect exploitation.
4. **Pin to full commit SHA**, not a floating tag, to prevent silent version changes: `anthropics/claude-code-action@<sha>`.

## Prevention

- Always pin GitHub Actions to **full commit SHAs**, not tags or `@main`. Tags are mutable.
- Apply **least privilege** to the `GITHUB_TOKEN` in any AI-agent workflow (`permissions: read-all` where possible).
- Combine AI agent CI workflows with **mandatory human approval** for any write operations on the main branch.
- When evaluating a GitHub Action that runs an AI agent, review how it determines caller trust — any string-suffix or username-contains check is a red flag.

## Sources

- [CybersecurityNews — "Claude Code's GitHub Actions Vulnerability Lets Attackers Compromise Any Repository"](https://cybersecuritynews.com/claude-codes-github-actions-vulnerability/) — RyotaK disclosure, checkWritePermissions detail, attack chain, patch version (v1.0.94), bounty amount.
- [SecurityWeek — "Claude Code, Gemini CLI, GitHub Copilot Agents Vulnerable to Prompt Injection via Comments"](https://www.securityweek.com/claude-code-gemini-cli-github-copilot-agents-vulnerable-to-prompt-injection-via-comments/) — broader AI CI agent vulnerability context.
- Cross-reference: [2026-04-comment-and-control-pr-injection.md](2026-04-comment-and-control-pr-injection.md) — sibling "AI agent exploited via GitHub PR/issue content" class.
