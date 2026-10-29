---
id: 2026-10-github-issues-hidden-html-comment-workflow-injection-campaign-61-repos-radware
title: "Hidden commands in GitHub issues hit workflows of 61 public repositories in 45 minutes on 2026-09-01; agno, qwen-code, MLflow, LangExtract named"
date_disclosed: 2026-10-29
last_updated: 2026-10-29
severity: high
status: unconfirmed
ecosystems: [github-actions, ci-cd, open-source]
tools_affected: ["any public repository whose workflow runs on issues, issue_comment or pull_request_target events and interpolates the issue or comment body into a shell step", "named by the researchers: Google LangExtract, Trivy, Brave browser, MLflow, agno, ToolJet, CopilotKit, Podman, qwen-code, discord.js, Cilium, dotnet/maui, Homebrew cask, github/docs, Apache Doris, PX4-Autopilot"]
tags: [github-actions, workflow-injection, pwn-request, html-comment, credential-theft, supply-chain, ci-cd, single-outlet, radware, agno, qwen-code, mlflow]
---

## TL;DR
The Register reports (2026-10-29) that Radware researchers found at least 83 GitHub issues, pull requests and comments across 61 public repositories carrying shell commands hidden in HTML comments, 77 of them posted within a 43-minute window on 2026-09-01 from 74 accounts the researchers believe were compromised; where a workflow interpolated the text into a shell step, the command ran within a second, collected environment variables and tried to send them to an attacker server, and logs from two runs show it executed. The named targets include agno, qwen-code, CopilotKit, MLflow and LangExtract; most maintainers fixed or closed the workflows, and the researchers could not confirm whether any repository was modified. Radware's primary report was not found this run, so the status is unconfirmed; the fix is the same as for every pwn request: never put event text in a shell string.

## What happened

**The outlet's account.** Jessica Lyons, The Register, 2026-10-29 12:00 UTC, quoting Radware threat hunters Gabi Nakibly and Zvika Babo. The researchers found the campaign while measuring prompt injection against coding agents on GitHub. Figures as the article states them: at least 83 attacks against 61 repositories as of 2026-10-13; 77 items in a 43-minute window on 2026-09-01 and six more in the next two minutes; 74 GitHub accounts, many with legitimate development histories; one individual suspected. The hidden command was invisible on the rendered page because it sat inside an HTML comment. Repositories whose workflows triggered on the event and wrote the attacker's text into shell source ran it. The researchers observed the command collecting environment variables and attempting exfiltration, saw evidence in two runs' logs that it executed in the automation environment, and could not confirm repository write access, code modification or downstream compromise; their stated reading is that the goal was credentials for a later supply-chain attack. They disclosed to all affected maintainers; most repositories were closed or fixed, not all confirmed.

**No AI agent in the chain.** The article does not place a coding agent or triage bot in the attack path. The mechanism is the GitHub Actions expression-injection class (untrusted event fields in `run:` steps), which predates agents. It belongs here because the named repositories include four agent and AI frameworks the audience installs (agno, qwen-code, CopilotKit, MLflow, LangExtract), because hidden HTML comments in issues are also the carrier the same researchers' prompt-injection census tracks, and because a credential stolen from a framework's CI is the start of a release hijack of the kind this corpus has recorded repeatedly.

**What was not found.** Radware's public repository `rdwr-gabin/github-ipi-in-the-wild` (Nakibly and Babo, "Prompt injection on GitHub, in the wild") is a census of about 145 million GitHub items from 2026-06-01 to 09-30 reporting 2,281 findings, 43 of them attacks in issues, pull requests and comments; it does not describe this campaign, its repository list or its figures, and links no report. A search found no Radware post. Until a primary appears, every figure above is the outlet's rendering of the researchers' statements.

## Am I affected?

- You maintain a public repository with a workflow that triggers on `issues`, `issue_comment`, `pull_request_target` or `discussion` events and uses `${{ github.event.issue.body }}`, `${{ github.event.comment.body }}`, a title, or a PR body inside a `run:` step. That is the vulnerable shape regardless of this campaign.

```bash
grep -rnE 'github\.event\.(issue|comment|pull_request|discussion)\.(body|title)' .github/workflows/ | grep -v 'env:'
git log --all --since=2026-08-31 --until=2026-09-03 --format='%h %an %s' -- .github/workflows/   # workflow changes around the campaign day
```

- Check the Actions run history for 2026-09-01 on repositories with such workflows: a run triggered by an issue or comment from an account you do not recognise, lasting seconds, is the signal the researchers describe.

## If you are affected

1. Rotate every secret the triggered workflow could read, and the runner's environment variables (cloud keys, registry tokens, `GITHUB_TOKEN`-adjacent PATs): [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md), [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
2. Move event text out of `run:` into an `env:` variable and quote it, or use an action input; set the job's `permissions:` to the minimum; split externally triggered jobs from jobs holding secrets.
3. Review the repository for commits, releases or workflow files you did not author in September.

## Prevention

- [CI/CD hardening](../prevention/ci-cd-hardening.md): untrusted event fields never reach a shell; least privilege per job; egress controls on runners.
- [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources
- [The Register — Attackers turn GitHub issues into supply chain campaign against 61 public repos in less than an hour](https://www.theregister.com/security/2026/10/29/attackers-turn-github-issues-into-supply-chain-campaign-against-61-public-repos-in-less-than-an-hour/5306153) — fetched 2026-10-29 (Jessica Lyons, 12:00 UTC): the figures, the named repositories, the HTML-comment mechanism, the two runs with execution evidence, the 74 accounts, the disclosure and remediation statements.
- [rdwr-gabin/github-ipi-in-the-wild — Prompt injection on GitHub, in the wild](https://github.com/rdwr-gabin/github-ipi-in-the-wild) — fetched 2026-10-29: the same researchers' census (June to September 2026, 2,281 findings, 43 attacks in issues, PRs and comments); it does not contain this campaign and is cited for what it does not hold.
- Related in this corpus: [GhostAction workflow credential theft](2026-10-ghostaction-returns-github-actions-workflow-credential-theft-git-history-sweep.md), [Gheist ci-sync branches](2026-10-gheist-stolen-github-tokens-ci-sync-branches-actions-log-secret-exfiltration.md), [Gemini CLI issue-triage injection](2026-04-gemini-cli-trustissues-cve-2026-12537.md).
