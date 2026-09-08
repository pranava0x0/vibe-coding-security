---
id: 2026-03-openai-codex-branch-name-command-injection
title: "OpenAI Codex — unsanitized GitHub branch names inject shell commands, stealing GitHub tokens (BeyondTrust, disclosed Mar 2026)"
date_disclosed: 2026-03-30
last_updated: 2026-09-08
severity: critical
status: patched
ecosystems: [openai-codex, github]
tools_affected: ["OpenAI Codex (ChatGPT web integration)", "Codex CLI", "Codex SDK", "Codex IDE Extension"]
tags: [command-injection, github-token-theft, unicode-obfuscation, ifs-bypass, ai-coding-agent, openai, github-oauth]
---

## TL;DR
BeyondTrust's Phantom Labs found that OpenAI Codex passed a task's GitHub branch name unsanitized into shell commands (`git fetch` and related container-setup steps) during task creation. By encoding spaces as Bash's `${IFS}` variable — which GitHub's branch-naming rules don't block but Bash still expands — an attacker who could create a branch (including via GitHub's API alone, no direct Codex interaction required) could smuggle a multi-word shell command into the branch name and have it execute inside the victim's Codex container, exfiltrating the GitHub OAuth token embedded in the container's git remote URL. A separate path via `@codex` mentions in pull-request comments exposed higher-privilege GitHub Installation Access tokens. Attackers also demonstrated hiding the payload from the UI using 94 repeated Unicode Ideographic Space characters (U+3000). OpenAI classified the finding Critical/Priority-1 internally and completed remediation by 2026-02-05; BeyondTrust published publicly on 2026-03-30. No CVE was assigned — consistent with OpenAI's practice for server-side SaaS fixes shipped before disclosure.

## What happened
Codex tasks are created from a GitHub branch reference. Instead of treating that branch name as inert data, Codex's container-initialization path interpolated it directly into shell commands run during setup (a `git fetch`-class operation). GitHub itself blocks literal space characters in branch names, but Bash's `${IFS}` (Internal Field Separator) variable expands to whitespace at execution time — so an attacker could write a branch name containing `${IFS}` in place of spaces, pass GitHub's validation, and have Bash reassemble and execute a full multi-word command once Codex ran it.

BeyondTrust demonstrated three exploitation paths: (1) directly creating a task against a malicious branch through the ChatGPT Codex web UI, (2) creating the malicious branch purely through GitHub's API with no direct Codex interaction, and (3) triggering execution via an `@codex` mention in a pull-request comment — a path that exposed a GitHub **Installation Access token** carrying broader organizational permissions than the per-task OAuth token used in the other two paths. Researchers also embedded payloads using 94 repeated Unicode Ideographic Space characters (U+3000) so the malicious portion of the branch name scrolled off-screen in the UI and was not visually obvious to a reviewer.

Successful exploitation exfiltrated the GitHub OAuth token embedded in the container's git remote URL, granting read/write access to the victim's repositories, workflows, and — per BeyondTrust — potential lateral movement across companies sharing Codex execution environments.

**Timeline (per BeyondTrust):** submitted via HackerOne/BugCrowd 2025-12-16 → initial hotfix 2025-12-23 → branch shell-escape fix deployed 2026-01-22 → additional hardening 2026-01-30 → OpenAI classified Critical/Priority-1 and completed remediation 2026-02-05 → BeyondTrust public disclosure 2026-03-30. All fixes were server-side (input validation for branch names, stronger shell escaping, tighter in-container token scope and lifetime); no user action was required.

## Am I affected?
This was a server-side vulnerability in OpenAI's own Codex infrastructure, fully remediated before public disclosure — there is no client-side version to check or upgrade. If you used Codex against a repository between the disclosure date (2025-12-16) and the final remediation (2026-02-05), and untrusted collaborators could create branches or comment on PRs in that repository during that window, treat any GitHub tokens Codex had access to at the time as potentially exposed.

```bash
# Review recent branch names for suspicious Unicode/whitespace obfuscation
git branch -a | cat -A | grep -P '\xe3\x80\x80'   # U+3000 Ideographic Space in UTF-8

# Review GitHub audit log for unexpected OAuth/Installation token usage
# (GitHub org settings → Audit log → filter by action:oauth_authorization or action:integration_installation)
```

## If you are affected
1. If you have reason to believe a Codex-connected GitHub OAuth or Installation token was exposed during the December 2025–February 2026 window, rotate it: revoke the OpenAI GitHub App/OAuth authorization from your GitHub account settings and re-authorize.
2. → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
3. Audit repository and organization activity (new branches, workflow file changes, unexpected commits) for the affected window.

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — treat any agent-controlled token embedded in a build/container environment as a high-value target; scope and time-limit tokens issued to agentic tooling.
→ Review pull requests and branch names for non-printing or repeated Unicode whitespace characters before trusting an `@codex`-triggered automated review.

## Sources
- [BeyondTrust — OpenAI Codex Command Injection Vulnerability](https://www.beyondtrust.com/blog/entry/openai-codex-command-injection-vulnerability-github-token) — primary disclosure (fetch blocked by a 403 in this sweep; corroborated in full technical detail via the Barrack AI writeup below, which cites BeyondTrust as its source).
- [Barrack AI — OpenAI Codex: How a Branch Name Stole GitHub Tokens](https://blog.barrack.ai/openai-codex-command-injection-github-token/) — full technical breakdown: `${IFS}` bypass mechanism, Unicode obfuscation, disclosure timeline, affected products.
- [SecurityWeek — Critical Vulnerability in OpenAI Codex Allowed GitHub Token Compromise](https://www.securityweek.com/critical-vulnerability-in-openai-codex-allowed-github-token-compromise/) — independent secondary coverage confirming researcher (BeyondTrust Phantom Labs), timeline, and severity classification.
