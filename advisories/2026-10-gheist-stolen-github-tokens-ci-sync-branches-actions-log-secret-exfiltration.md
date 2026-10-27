---
id: 2026-10-gheist-stolen-github-tokens-ci-sync-branches-actions-log-secret-exfiltration
title: "Gheist: stolen GitHub tokens push ci-sync branches whose workflow prints every secret into the run log, then deletes the run; 13,500 branches, 850 accounts"
date_disclosed: 2026-10-25
last_updated: 2026-10-26
severity: high
status: active
ecosystems: [github, github-actions, npm, pypi, aws]
tools_affected: ["any GitHub account whose personal access token or OAuth token was stolen by an infostealer or an earlier supply-chain compromise", "repositories with Actions secrets, environment secrets, or self-hosted runners", "private repositories and GitHub Enterprise Server, where GitHub's hold-for-approval control does not apply"]
tags: [github-actions, stolen-tokens, secret-exfiltration, run-log, deleted-runs, self-hosted-runners, environment-secrets, megalodon, ghostaction, cryptomining, polinrider, wiz]
---

## TL;DR
Wiz (2026-10-25) describes a campaign it calls Gheist: an operator holding stolen GitHub tokens pushes a branch named `ci-sync-` plus six characters, with a commit "ci: sync config" attributed to the token owner, adding `.github/workflows/sync-check.yml`. The workflow encodes every secret the job can see and prints it to the run log, because GitHub's masking only matches verbatim values; the operator downloads the log through the API and deletes the run seconds later. There is no command-and-control, so the only signals are the branch, the run and audit-log entries. Wiz counts more than 13,500 branches across more than 850 accounts since 2026-09-15, with a second tool adding environment matrices for environment-scoped secrets and, since 10-19, a buggy job aimed at self-hosted runners. GitHub's hold-for-approval control stopped the public-repository runs (`action_required`) but not private repositories or Enterprise Server. Cloud logs later showed assumed AWS roles and Secrets Manager enumeration from the leaked values. Deleting the branch and run does not undo the leak: rotate everything the workflow could read.

## What happened

**Mechanics (Wiz).** The branch matches `^ci-sync-[0-9a-z]{6}$`; the commit is unsigned and carries the token owner's identity. The workflow dumps the secrets context in an encoded form so no verbatim secret string appears, and echoes it; the operator reads the log via the API with a `gheist` user agent and deletes the run, usually within seconds. Two tools are visible: one with hex suffixes; a second with base36 suffixes, an `environment` matrix so every environment's secrets are read, and from 10-19 a `sync-host` job for self-hosted runners that writes `.gdmp_pat`, `.gdmp_patg`, `.gdmp_sweep` and a `gdmp-pivot` marker and is, per Wiz, buggy.

**Scale and timeline.** Tracked since 2026-09-15; the second tool first ran 09-28. On 10-06, 391 accounts renamed about 1,461 repositories to cracked-software lures, wiping 610 branches. On 10-18, 25 accounts created "Windows RDP Runner" repositories used for mining. On 10-19 and 10-20 three victims were re-pushed with PolinRider loaders in `vite.config.js` and `api.js`. 57 accounts overlap with [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md); Wiz says this is distinct from [GhostAction](2026-10-ghostaction-returns-github-actions-workflow-credential-theft-git-history-sweep.md). Token sources are infostealers and the [March Trivy compromise](2026-03-trivy-litellm-supply-chain.md). About two-thirds of the accounts were gone by 10-24. The Hacker News (10-26) carries the same figures and the hold-for-approval detail.

**What the secrets bought.** Wiz saw AWS role assumptions on `ci-sync` branches in customer cloud logs and later AWS Secrets Manager enumeration.

Why it is here: the pattern is the LiteLLM `ci-tmp-` workflow at scale ([root cause](2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0.md)), it needs nothing but a token an infostealer already took from a developer laptop, and the secrets it prints are the npm, PyPI, cloud and AI-provider keys a vibe-coded project keeps in Actions.

## Am I affected?

- Branches: `git ls-remote --heads origin | grep -E 'refs/heads/ci-sync-[0-9a-z]{6}$'` on every repository; also look for a `sync-check.yml` workflow in any branch's history.
- Audit log (organisation or enterprise): `workflows.deleted_workflow_run`, branch creation or pushes for `ci-sync-*`, `repo.rename` bursts on 10-06, API calls with user agent `gheist`.
- Workflow runs: any run on a `ci-sync` branch, including `action_required` holds, which mean an attempt GitHub blocked.
- Self-hosted runners: the `.gdmp_*` files and the `gdmp-pivot` marker in the runner work directory.
- Cloud: role assumptions from GitHub OIDC on an unknown branch, and Secrets Manager `ListSecrets`/`GetSecretValue` bursts after them.

## If you are affected

1. Rotate every repository, organisation and environment secret the workflow could read, and every cloud role the OIDC trust allowed, from a clean machine; deleting the branch or run does not retract the log. [If your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), then [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md).
2. Revoke the token that pushed the branch (the commit author's PATs and OAuth app grants) and treat that person's machine as infostealer-infected.
3. Rebuild any self-hosted runner that ran the `sync-host` job.

## Prevention

- [CI/CD hardening](../prevention/ci-cd-hardening.md): ephemeral runners, OIDC trust scoped to protected branches, environments with required reviewers, fine-grained tokens or GitHub Apps instead of classic PATs, alerts on deleted runs.
- [Credential hygiene](../prevention/credential-hygiene.md): a token on a laptop is an infostealer target; short expiry and SSO-enforced tokens limit the window.

## Sources
- [Wiz — Gheist: attempted scaled abuse of stolen GitHub tokens stumbles](https://www.wiz.io/blog/gheist-attempted-scaled-abuse-of-stolen-github-tokens-stumbles) — fetched 2026-10-26 (Rami McCarthy, Hila Ramati): branch regex, workflow name and commit message, log encoding, user agent, the two tools, counts, the 10-06, 10-18 and 10-19 events, Megalodon overlap, token sources, hold-for-approval behaviour, cloud observations, hunting and response guidance.
- [The Hacker News — Gheist uses stolen GitHub tokens to steal private repository secrets via Actions logs](https://thehackernews.com/2026/10/gheist-uses-stolen-github-tokens-to.html) — fetched 2026-10-26 (Swati Khandelwal): independent report of the same campaign and figures.
- Related in this corpus: [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md), [GhostAction returns](2026-10-ghostaction-returns-github-actions-workflow-credential-theft-git-history-sweep.md), [LiteLLM root cause](2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0.md).
