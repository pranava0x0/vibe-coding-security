---
id: 2026-10-ghostaction-returns-github-actions-workflow-credential-theft-git-history-sweep
title: "GhostAction returns: compromised maintainer accounts push a \"Security Audit\" GitHub Actions workflow to 345 repositories in two sixteen-minute windows, and the new variant searches the working tree and the full git history for AWS, Anthropic, OpenAI, OpenRouter, GitHub, GitLab, Slack and Firebase keys (2026-10-08; 772 repositories in the August to September wave)"
date_disclosed: 2026-10-08
last_updated: 2026-10-10
severity: high
status: active
ecosystems: [github-actions, ci-cd, github, pypi, crates-io, npm, ai-provider-keys]
tools_affected: ["any repository a compromised maintainer account can push to, including forks", "GitHub Actions secrets referenced in existing workflows", "credentials ever committed to any branch or tag, including deleted ones", "pyxel (kitao) and its author's 26 other repositories", "uber/athenadriver and the 317 other repositories reachable from its original author's account"]
tags: [credential-theft, github-actions, ci-cd, supply-chain, compromised-maintainer, git-history, ai-api-keys, anthropic-key, openai-key, campaign, active]
---

## TL;DR
GhostAction, the GitHub Actions credential-theft campaign GitGuardian first documented in September 2025, is running again with two changes that matter to anyone who keeps an AI provider key near a repository. On 2026-10-08 two compromised maintainer accounts pushed a workflow disguised as a security audit to 345 repositories in two automated bursts: the author of the pyxel game engine's account hit 27 repositories between 13:20 and 13:44 UTC, and the original author of `uber/athenadriver`'s account hit 318 between 21:10 and 21:26 UTC, 279 of them forks. The workflow still sends the repository's named Actions secrets, as the 2025 version did, but the October variant also checks out the full history and searches every branch and tag, including deleted lines, for thirteen credential patterns: AWS access keys with their paired secrets and session tokens, Anthropic, OpenAI and OpenRouter API keys, GitHub classic and fine-grained tokens, GitLab tokens, Google and Firebase API keys, Slack bot tokens and SendGrid keys. Deleting a key from the current tree no longer helps. GitGuardian separately counts 772 public repositories at 373 users and organisations hit between 2026-08-31 and 2026-09-30 with 2,577 secrets targeted, of which 26 were confirmed stolen from 13 repositories because GitHub's approval gate held most runs. StepSecurity found roughly 378 public repositories still carrying a live malicious workflow on 2026-10-09. The one control observed stopping an execution was "require approval for workflow runs." No malicious package release had been published with a stolen publishing token as of the sources' dates. If either workflow file has been in a repository you own since 2026-08-31, treat every Actions secret and every credential ever committed to any branch as exposed.

## What happened

**The 2025 campaign.** GitGuardian's September 2025 report described 817 public repositories at 327 GitHub users whose Actions secrets, including PyPI, npm and DockerHub tokens, were sent to an attacker endpoint by an injected workflow: 3,325 secrets in total. The injection path was then, and is now, a stolen GitHub credential, most likely a personal access token from infostealer logs or credential dumps, used to commit a workflow file straight to the default branch under the victim's identity.

**The August to September 2026 wave (GitGuardian, published 2026-10-07, updated 10-09).** Between 2026-08-31 and 2026-09-30 the campaign pushed its workflow to 772 public repositories belonging to 373 users and organisations, in three bursts on 08-31, 09-02 to 09-05 (294 on 09-05 alone) and 09-15. The workflow hard-codes the names of the secrets the attacker found referenced in the repository's own legitimate workflows, rather than dumping the whole environment, and collects hostnames and usernames alongside them; the most targeted categories were SSH and deployment keys, Azure credentials, container-registry logins, database credentials and AWS keys. Of 3,669 runs across 605 repositories, 499 executed in 32 repositories and 336 completed, exfiltrating 26 secrets from 13 repositories; GitHub's requirement that first-time contributor runs be approved held most of the rest, and because the workflow fires on every push, many of those runs were triggered by later legitimate commits. Only 124 repositories (16 percent) showed effective cleanup in public history by 2026-10-05.

**The 2026-10-08 wave (StepSecurity, published 2026-10-09; The Hacker News, 2026-10-09; OpenSourceMalware, 2026-10-09).** Two accounts, both high-profile maintainers, pushed the new variant: `kitao` (Takashi Kitao, author of pyxel, about 18,400 stars) to 27 repositories, after which the attacker manually re-ran the workflow from the same session; and `henrywoo` (Henry Wu, original author of Uber's athenadriver) to 318 repositories including 279 forks and one organisation-owned repository, `uber/athenadriver`, which was the last repository in the sweep and where run logs show the exfiltration request acknowledged four seconds after the run started. Socket's threat research team opened issues on the victims' repositories the same day; the one on `uber/athenadriver` (issue 83, 2026-10-09) names the campaign and tells the maintainer not to cut a release until the repository is clean. A third account, `xxyangyoulin`, had pushed empty commits on 10-07 to re-trigger a workflow injected on 09-05; those runs stalled for approval. The Hacker News adds Socket's wider count: more than 500 accounts committing the workflow to tens of thousands of repositories since 2026-10-07, most of them forks. The campaign's collection endpoint has changed since at least 2026-09-04 and is a raw IP reached over plain HTTP, so no DNS lookup occurs and domain-based egress controls do not see it; this advisory does not reproduce it.

**What the October workflow does, one clause each.** It triggers on manual dispatch and on any push to any branch or tag; it checks out with `fetch-depth: 0`; in a single step it appends the named Actions secrets gathered during reconnaissance, scans the working tree for the thirteen credential patterns, searches the full git history for the same patterns so that credentials committed and later deleted are recovered, captures surrounding lines so that AWS access key ids are paired with their secrets (and, per OpenSourceMalware, regions and roles), and posts the result out, every run, even when it finds nothing, so the operator learns which repositories give them execution. The workflow's own `GITHUB_TOKEN` was read-only in the observed runs, so the workflow cannot push code itself; everything after exfiltration depends on what the stolen secrets unlock. Victims' publishing credentials were among the targets: PyPI, crates.io and a Gitee mirror token in the October wave.

**Forks and the private-repository angle.** A fork carries the workflow file, and enabling Actions on the fork runs it under the fork owner's context. Socket's warning, carried by The Hacker News, is that private forks are the larger exposure: private repositories are where committed credentials usually sit, and forks inherit the workflow through synchronisation.

**Related but separate.** The `kuafuai/DevOpsGPT` repository was altered on 2026-08-30 to embed a cryptocurrency miner in its Docker image; OpenSourceMalware treats it as unrelated activity that happens to share a compromised identity. OpenSourceMalware also lists two code-host-themed lookalike domains registered in September and October as a watchlist, one tied to the collector and one lower-confidence, and says neither is proven part of the campaign; they are not reproduced here.

**Two-source note.** StepSecurity (the 10-08 wave and the workflow's behaviour) and GitGuardian (the 08-31 to 09-30 wave) are independent primaries with their own telemetry; The Hacker News carries both plus Socket's counts; OpenSourceMalware adds its own recovery of 790 repositories through 2026-10-09; the `uber/athenadriver` issue is the victim-side record. StepSecurity's GitHub issue on the pyxel repository could not be opened this sweep (the cited issue number returned 404), so it is not cited.

## Am I affected?

The hunting signals below are the ones StepSecurity and OpenSourceMalware publish; both note that the filenames are common, so treat a filename hit as a reason to read the file, and the job, step and payload strings as the confirmation.

```bash
# 1. Workflow files on ANY branch or tag, not just the default branch
for b in $(git for-each-ref --format='%(refname:short)' refs/remotes refs/tags); do
  git ls-tree -r --name-only "$b" 2>/dev/null | grep -E '^\.github/workflows/(security-audit|github_actions_security|security-check)\.ya?ml$' | sed "s|^|$b: |"
done

# 2. Job, step and workflow names the campaign uses
git grep -nE 'name: *"?(Security Audit|Github Actions Security)"?|^\s*(audit|send-secrets):|Prepare Cache Busting' -- '.github/workflows/' $(git for-each-ref --format='%(refname:short)' refs/remotes)

# 3. Payload markers (the history-mining variant)
git grep -nE 'AKIA_CTX_START|AKIA_CTX_END' $(git for-each-ref --format='%(refname:short)' refs/remotes)
# Across an organisation, GitHub code search for the same two strings finds infected repositories and forks.

# 4. Commits that added a workflow file directly to the default branch without a pull request, since 2026-08-31
git log --since=2026-08-31 --diff-filter=A --format='%h %ad %an %s' --date=short -- .github/workflows/
# Commit messages seen: "Add security audit workflow", "Update security audit workflow",
# "Add security check workflow", "Trigger security scan"

# 5. Actions run history: any completed run of one of these workflows is confirmed exfiltration
gh run list --workflow security-audit.yml --limit 50 2>/dev/null
gh run list --workflow github_actions_security.yml --limit 50 2>/dev/null

# 6. Runner egress: plain-HTTP POSTs from CI runners to a raw IP address (ports 80 and 3000 seen), early September onward
```

Also check every fork you own of an affected upstream, and the audit log for bursts of unsigned commits across many repositories within minutes and `workflow_dispatch` runs on newly added "audit" workflows.

## If you are affected
1. **Assume a confirmed breach** if either workflow was present since 2026-08-31: every configured Actions secret and every credential ever committed to any branch, including ones deleted years ago, is exposed. Preserve the workflow files, run logs, commits and audit log before removing anything.
2. **Revoke the compromised GitHub credential** that made the push: personal access tokens, OAuth grants, app credentials, deploy keys and sessions on the affected account. GitGuardian's line is the one to remember: "Rotating the secrets exfiltrated by the malicious workflow is not enough." [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).
3. **Rotate everything the workflow could read,** starting with publishing tokens (PyPI, npm, crates.io, container registries), cloud keys, AI provider keys (Anthropic, OpenAI, OpenRouter), source-control tokens, SSH and deploy keys, and messaging keys; search full history for the same patterns and rotate those too. [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
4. **Remove the workflow from every branch and tag,** then audit packages, releases, images and deployments produced during the window and rebuild trusted artifacts from a verified pre-compromise commit. Freeze releases until the repository is clean; if publishing tokens were configured, assume the attacker can publish as the project until they are rotated.
5. **Check forks and mirrors.** Delete the workflow from forks you own; warn downstream mirrors.

## Prevention
- Require approval for workflow runs from outside contributors and for any run triggered by a new or changed workflow file; it is the only control observed stopping an execution in this wave. [ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- Protect `.github/workflows/` with branch protection so workflow changes need a reviewed pull request, and alert on new workflow files landing on default branches.
- Restrict runner egress to an allowlist; raw-IP, plain-HTTP exfiltration is invisible to domain-based controls.
- Stop keeping long-lived secrets anywhere a workflow can read them: short-lived or OIDC-issued cloud credentials, and a full-history secret scan of every repository, because the attacker now reads history and you should have read it first. [credential-hygiene.md](../prevention/credential-hygiene.md).
- Maintainers: a session cookie or token stolen by an infostealer is the whole campaign's entry point. Hardware-key 2FA on the GitHub account, and no long-lived PAT on a machine that also runs untrusted packages.

## Sources
- [StepSecurity — GhostAction Returns: Malicious "Security Audit" Workflows Now Mine Credentials from Entire Git Histories](https://www.stepsecurity.io/blog/ghostaction-returns) (fetched 2026-10-10; published 2026-10-09; the 10-08 timeline for both accounts, 345 repositories, the workflow filenames, job and step names, the thirteen credential categories, the full-history search, the read-only `GITHUB_TOKEN`, the `uber/athenadriver` run log, the approval-gate observation, the 378 / 182 / 88 counts on 10-09, hunting signals and remediation)
- [GitGuardian — GhostAction Returns: 772 Repos Hit in New GitHub Actions Wave](https://blog.gitguardian.com/ghostaction-github-actions-supply-chain-attack-returns/) (fetched 2026-10-10; published 2026-10-07, updated 2026-10-09; the 08-31 to 09-30 window, 772 repositories at 373 owners, 2,577 secrets targeted, the three bursts, 3,669 / 499 / 336 runs and 26 secrets from 13 repositories, the 124-repository remediation count, the 2025 campaign figures, the "rotating ... is not enough" guidance)
- [The Hacker News — Credential-Stealing GitHub Actions Workflows Planted in Tens of Thousands of Repositories](https://thehackernews.com/2026/10/credential-stealing-github-actions.html) (fetched 2026-10-10; published 2026-10-09; the pyxel and athenadriver attributions, Socket's 500-account and 279-fork counts, the four-action step description, the private-fork warning, the DevOpsGPT miner, "no malicious package releases ... as of" publication)
- [OpenSourceMalware — GhostAction Attack Escalates By Targeting GitHub Users](https://opensourcemalware.com/blog/ghostaction-attack-escalates) (fetched 2026-10-10; published 2026-10-09; the 790-repository recovery through 10-09, the paired-context detail around AWS keys, the credential-category list, the watchlist-domain caveat, the DevOpsGPT separation, the contain / revoke / rotate / audit / harden sequence)
- [uber/athenadriver issue 83 — "Repo infected by bad workflow"](https://github.com/uber/athenadriver/issues/83) (fetched 2026-10-10; opened 2026-10-09 by the Socket Threat Research Team account; names the GhostAction campaign and asks the maintainer to rotate secrets and hold releases)
