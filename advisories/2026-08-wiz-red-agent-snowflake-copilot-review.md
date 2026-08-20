---
id: 2026-08-wiz-red-agent-snowflake-copilot-review
title: "An autonomous agent found and exploited a Snowflake CI flaw that Copilot's review and GitHub Advanced Security both passed as clean"
date_disclosed: 2026-06-23
last_updated: 2026-08-20
severity: high
status: patched
ecosystems: [github-actions, ci-cd]
tools_affected: [github-copilot, github-advanced-security, github-actions, "snowflakedb/snowflake-connector-net"]
tags: [ci-cd, script-injection, github-actions, agentic-threat-actor, ai-code-review, pwn-request, credential-theft]
---

## TL;DR

A GitHub Actions **script-injection** flaw was merged into `snowflakedb/snowflake-connector-net` on 2026-06-18 — a refactor replaced a safe env-var pattern with direct interpolation of an untrusted **GitHub issue title** into a shell script, so anyone could run commands on the runner by opening an issue. Five days later **Wiz's autonomous "Red Agent" found it, exploited it, stole a Jira token, and mapped the blast radius with no human involvement**. The uncomfortable part for anyone shipping AI-reviewed code: **Copilot reviewed the merged PR and marked it all-clear**, and **GitHub Advanced Security scanned the exact vulnerable revision and did not flag it**.

## What happened

**The bug.** PR #1218, merged **2026-06-18**, replaced a previously safe pattern (passing values through environment variables and parsing with `jq`) with **direct interpolation of the issue title into a shell script** in the `jira_issue.yml` workflow. Because GitHub Actions template expansion happens *before* shell escaping, a single quote in an issue title is enough to break out and inject arbitrary commands. An **unauthenticated** user could execute arbitrary commands in the Actions runner by opening a crafted issue ([Wiz](https://www.wiz.io/blog/red-agent-snowflake-copilot-cicd-bug)).

This is the classic **"pwn request"** CI misconfiguration class this repo already tracks via [Cordyceps](2026-06-cordyceps-cicd-github-actions.md) and the [AsyncAPI compromise](2026-07-asyncapi-miasma-npm-github-actions.md) — untrusted, externally-controlled input reaching a trusted CI context.

**The exploitation.** Wiz found it on **2026-06-23** while researching under Snowflake's HackerOne program. Notably, the discovery and exploitation were performed by **Wiz Red Agent**, an autonomous AI security-research agent: it independently found the bug, exploited it, exfiltrated the runner's token, validated access to Snowflake's internal Jira (read access to internal engineering, security, and bug-bounty tickets), and assessed blast radius — "all without human intervention." Wiz notes Red Agent's **first attempt failed, it read the error, adjusted, and succeeded** — the self-correction signature that distinguishes an [agentic threat actor](2026-07-jadepuffer-langflow-agentic-ransomware.md) from a human running AI-assisted tooling.

Snowflake **patched the same day (2026-06-23)** and rotated the affected Jira token on 2026-06-24.

**The AI-review failure — and the attribution walk-back.** The vulnerable commit listed "Copilot Autofix powered by AI" as a co-author, and early framing of the story implied the AI had *written* the flaw. That framing was subsequently narrowed by Wiz itself. Wiz CTO **Ami Luttwak** clarified that "the specific lines of code that caused the vulnerability, were not created by copilot (although it is mentioned as a co-author)," adding that attribution between humans and AI "is becoming a bit harder to establish" and that "looking at co-authors of the PR is not enough." A Hacker News investigation cited in the same coverage determined the flawed section was attributable to a Snowflake engineer, with Copilot having changed certain other aspects ([IT Pro](https://www.itpro.com/security/wiz-cto-speaks-out-amid-snowflake-github-flaw-confusion)).

What is **not** disputed is the review failure. Wiz **updated its post on 2026-08-17** to state its narrowed claim: **Copilot was a co-author that checked the merged PR and code change and identified it as all-clear without noticing the critical vulnerability**. Independently, Infosecurity Magazine reports that the **GitHub Advanced Security scan — which uses Copilot Autofix — analyzed the final PR revision including the vulnerable workflow and "did not flag the critical injection"** ([Infosecurity Magazine](https://www.infosecurity-magazine.com/news/wiz-ai-agent-finds-snowflake/), [Forbes](https://www.forbes.com/sites/timkeary/2026/08/17/github-copilot-missed-a-vulnerability-that-wizs-ai-agent-found/)).

**Why this matters for vibe coders.** Two lessons, independent of who wrote the line:

1. **An AI review that returns "all clear" is not a security gate.** The failure here was on a well-known, well-documented vulnerability class (Actions script injection) in a small diff, and both the AI reviewer and the vendor's own static analysis missed it. If your workflow is "agent writes it, agent reviews it, merge," you have no independent check.
2. **The offense/defense asymmetry is now measurable.** Five days from merge to autonomous discovery-and-exploitation, by a bot, on a public repo. The window in which a CI misconfiguration sits unnoticed is closing much faster than review cadence.

## Am I affected?

The specific flaw is patched. The *class* is what to check. Audit your workflows for untrusted input interpolated into a `run:` block:

```bash
# Untrusted GitHub context values interpolated directly into shell — the core bug
grep -rn -E '\$\{\{\s*github\.event\.(issue|pull_request|comment|discussion)\.(title|body|head_ref)' .github/workflows/

# The higher-risk trigger this class lives on
grep -rn -E 'pull_request_target|issue_comment|issues:' .github/workflows/
```

You are exposed if a workflow interpolates any of `github.event.issue.title`, `.body`, `github.event.pull_request.title`, `.body`, or `github.head_ref` **directly into a `run:` script**, especially on a trigger reachable by non-collaborators.

The safe pattern is to pass the value through an environment variable and quote it, so it is never expanded by the Actions templating engine into shell source:

```yaml
- env:
    TITLE: ${{ github.event.issue.title }}
  run: |
    echo "$TITLE" | jq -R .
```

## If you are affected

1. Fix the interpolation using the env-var pattern above, then **rotate every secret that workflow had access to** — assume the runner's token was reachable.
2. Review the workflow's run history for issues/comments from unrecognized accounts around the exposure window.
3. Restrict `permissions:` on the workflow to the minimum, and avoid `pull_request_target` unless you genuinely need secrets on untrusted PRs.
4. See [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) and [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).

## Prevention

- **Never interpolate `github.event.*` user-controlled fields into `run:`.** Use environment variables and quote them.
- **Do not treat an AI code review as a security gate.** Keep a deterministic check (a linter for this exact class — `actionlint`, `zizmor`, or similar) in the required-checks list, and require human review on workflow-file changes specifically.
- **Review `.github/workflows/` changes as privileged changes**, on protected branches with signed commits — the same guidance this repo gives for [source-repo publish-time compromise](2026-05-megalodon-github-actions-mass-campaign.md).
- See [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).

## Sources

- [Red Agent Exploits Snowflake Vuln Missed by Github Copilot — Wiz](https://www.wiz.io/blog/red-agent-snowflake-copilot-cicd-bug) — primary disclosure: the `jira_issue.yml` script injection, PR #1218 timeline (merged 06-18, found/patched 06-23, token rotated 06-24), autonomous Red Agent exploitation, and the 2026-08-17 clarification that Copilot reviewed the merged PR and marked it all-clear.
- [Wiz CTO speaks out amid confusion over Snowflake-GitHub Copilot flaw — IT Pro](https://www.itpro.com/security/wiz-cto-speaks-out-amid-snowflake-github-flaw-confusion) — Wiz CTO Ami Luttwak's narrowed claim (Copilot did not create the vulnerable lines despite the co-author line) and the difficulty of human/AI attribution.
- [Wiz AI Agent Finds Critical Snowflake GitHub Repo Flaw Advanced Security Missed — Infosecurity Magazine](https://www.infosecurity-magazine.com/news/wiz-ai-agent-finds-snowflake/) — states the GitHub Advanced Security scan analyzed the final PR revision including the vulnerable workflow and did not flag the critical injection; corroborates the fully autonomous discovery-to-blast-radius chain.
- [GitHub Copilot Missed A Vulnerability That Wiz's AI Agent Found — Forbes](https://www.forbes.com/sites/timkeary/2026/08/17/github-copilot-missed-a-vulnerability-that-wizs-ai-agent-found/) — independent mainstream coverage of the finding and the AI-review failure.
