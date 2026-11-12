---
id: 2026-11-github-hijacked-accounts-wfx-docs-pull-requests-ci-workflow-changes-remove-and-rotate
title: "GitHub repositories with `wfx-docs` pull requests or unexpected CI workflow commits since 2026-11-10: remove the changes and rotate CI secrets"
kind: malicious-artifact
date_disclosed: 2026-11-12
last_updated: 2026-11-12
severity: critical
status: active
ecosystems: [github, github-actions, ci-cd, npm, packagist, go]
tools_affected: ["any GitHub repository that a compromised account could write to on or after 2026-11-10", "GitHub Actions workflows and their secrets, variables and OIDC cloud roles", "Packagist digitalelvis/neuronai-studio 3.14.3", "Go github.com/onuragtas/docker-env v1.0.278 and v1.0.280", "Go github.com/vkuznet/gocurl pseudo-version v0.0.0-20261111095532-8d5aad0cb0da", "developer machines that ran npm install on an affected commit"]
tags: [supply-chain, malicious-workflow, github-actions, compromised-accounts, ci-secrets, oidc, packagist, go-modules, postinstall]
---

## TL;DR
If a repository you can write to has a pull request titled "docs: dependency audit notes" from a branch named `wfx-docs`, or the commits and files listed below, dated 2026-11-10 or later, close and delete them and revoke the account that made them. If a workflow run followed one of those commits, rotate every secret and cloud role that repository's workflows could reach, and check your cloud accounts for access added in that window.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub repository | any repository | pull request "docs: dependency audit notes" from branch `wfx-docs`, with file `docs/wfx-audit.md` | close the pull request, delete the branch, revoke the author account's tokens and sessions | not applicable | Aikido, SafeDep, StepSecurity |
| GitHub repository | any repository | commits titled "ci: refresh build cache", "ci: restore", "ci: cleanup", "chore: add ci helper", "chore: add dependency audit workflow", or "chore: initial commit" in an empty repository | review, revert, then follow "If you are affected" | not applicable | Aikido, StepSecurity |
| GitHub repository | any repository | files `.github/workflows/build-audit-<six characters>.yml`, a hidden `.ci-<six characters>.sh` at the root, a new `postinstall` entry in `package.json`, new steps in existing workflows | remove, then follow "If you are affected" | not applicable | Aikido, StepSecurity |
| GitHub repository | any repository | branches `chore/<eight lowercase letters or digits>` and `ci-check-<four digits>` | delete after review | not applicable | Aikido, StepSecurity |
| Packagist | `digitalelvis/neuronai-studio` | 3.14.3 (published 2026-11-11 12:29 UTC) | pin 3.14.2 or earlier, per StepSecurity. 3.14.4 exists and no source read here calls it clean | 3.14.3 still listed, 3.14.4 published 2026-11-12 07:50 UTC (2026-11-12) | no OSV record (2026-11-12) |
| Go | `github.com/onuragtas/docker-env` | v1.0.278, v1.0.280 | remove these versions. Later versions were not assessed by any source read here | proxy latest v1.0.287, 2026-11-12 12:47 UTC (2026-11-12) | no OSV record (2026-11-12) |
| Go | `github.com/vkuznet/gocurl` | pseudo-version v0.0.0-20261111095532-8d5aad0cb0da | do not resolve this pseudo-version. StepSecurity said the repository was still affected when it published | the proxy's latest is this pseudo-version (2026-11-12) | not queried |

Notes on the table. Three firms published on 2026-11-12 and say the activity began on 2026-11-10. Their counts measure different things and are not added together here.

- Aikido: 4,837 compromised accounts opened probe pull requests in 61,764 repositories. The same post says "at least 1,835 repositories ran the payload" and, separately, "indications that the payload ran in at least 1,806 repositories, but this number may understate impact". Both figures are printed as written. 10,431 of the pull requests were in repositories the account does not own.
- SafeDep: 8,093 repositories received commits between 2026-11-10 12:46 UTC and 2026-11-12 04:36 UTC. SecurityWeek notes that this does not necessarily mean the code ran. SafeDep says the campaign was still active when it searched, and it publishes a list of affected repositories.
- StepSecurity: more than 63,000 probe pull requests as of 07:40 UTC on 2026-11-12, about 90% still open. It names repositories where the change was reverted, among them `nextcloud/docker` and `webdriverio/webdriverio`, and counts 56 commits across 28 WebdriverIO repositories from one bot account. SafeDep says no WebdriverIO package release was affected.
- StepSecurity traced 173 probe pull requests from 19 accounts to tokens issued to the Fly.io GitHub App. It says it has not established how the tokens were obtained and has no evidence that Fly.io's infrastructure was breached. No statement from Fly.io or GitHub appears in any source read here.
- For the two Go modules, Aikido and SafeDep say `go get` and `go build` do not run workflow files. For the Packagist package, SafeDep says exposure comes from running `npm install` inside the package's directory, not from `composer`.
- Aikido sees overlap with the October GhostAction campaign, tracked in [this corpus](2026-10-ghostaction-returns-github-actions-workflow-credential-theft-git-history-sweep.md), and assesses the two as probably different actors.

## Am I affected?

1. **Pull requests.** In each organisation: `gh search prs "docs: dependency audit notes" --owner <org> --created ">=2026-11-10"`. Any hit is a probe from a compromised account with write access.
2. **Branches.** `git ls-remote --heads origin | grep -E 'wfx-docs|ci-check-[0-9]{4}|chore/[a-z0-9]{8}$'`.
3. **Commits.** `git log --all --since=2026-11-10 --format='%h %an %s' | grep -E 'ci: (refresh build cache|restore|cleanup)|chore: add (ci helper|dependency audit workflow)'`. The commit is usually reverted afterwards, so search all refs and the pull request history, not only the default branch.
4. **Files.** `git log --all --since=2026-11-10 --name-only --format= | grep -E 'build-audit-.{6}\.yml|^\.ci-.{6}\.sh|docs/wfx-audit\.md' | sort -u`, and `git log --all --since=2026-11-10 -p -- package.json | grep -n postinstall`.
5. **Workflow runs.** Aikido and StepSecurity both say run logs are often deleted, and that a gap in the workflow run numbers right after a suspect commit is the most reliable sign that a run happened. Check the organisation audit log for deleted runs.
6. **Status checks.** Aikido reports forged success statuses on commit SHAs. Confirm nothing was merged on a check you cannot trace to your own CI.
7. **Cloud accounts.** Per SafeDep and StepSecurity: Azure federated identity credentials named `wfx-ci-*`, AWS sessions named `wfx-*`, AWS access keys and role trust policy edits made since 2026-11-10, unexpected GCP token-generation calls through workload identity pools, and Vault or Kubernetes logins that used a GitHub Actions token.
8. **Packages.** `composer show digitalelvis/neuronai-studio`, and `grep -n 'onuragtas/docker-env\|vkuznet/gocurl' go.mod go.sum`.
9. **Developer machines.** Anyone who ran `npm install` on a checkout containing one of the commits above, before the revert.

## If you are affected

- **The account first.** Revoke the commit author's personal access tokens, OAuth grants, GitHub App authorisations, SSH keys and sessions, and turn on two-factor sign-in. Remove collaborator or organisation access the account does not need. [If your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) has the order of work.
- **Clean the repository.** Close the probe pull request, delete the `wfx-docs` and other listed branches, and remove the listed files and workflow steps.
- **If a run happened, or you cannot rule it out, rotate.** Repository, environment and organisation secrets and variables available to the job. Package registry tokens. Long-lived cloud keys stored as secrets. Credentials on self-hosted runners. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md).
- **Remove added access, not only keys.** SafeDep and StepSecurity say rotation alone is not enough where OIDC is used. Review AWS role trust policies and recently created access keys, Azure federated identity credentials on app registrations, and GCP workload identity pool bindings, and delete what you did not create.
- **Packages you publish.** Rebuild and republish any version produced between a listed commit and its cleanup.
- **Developer machines** in step 9: treat as compromised and follow [if you ran a malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md).

## Prevention

- [CI/CD hardening](../prevention/ci-cd-hardening.md): require review for changes under `.github/workflows/`, scope OIDC trust policies to a repository and branch, keep bot accounts out of branch-protection bypass lists, and restrict CI egress to an allowlist.
- [Credential hygiene](../prevention/credential-hygiene.md): fine-grained, expiring tokens per repository, so one stolen token does not write to every repository an account can reach.
- Review which GitHub Apps hold write access to your repositories and remove the ones you no longer use.

## Sources

- [Aikido: Compromised GitHub accounts push CI secret stealer to tens of thousands of repositories](https://www.aikido.dev/blog/compromised-github-accounts-push-ci-secret-stealer-to-tens-of-thousands-of-repositories), fetched 2026-11-12: published 2026-11-12 by Oliver Smith; the account, repository and pull-request counts, both run counts, the identifiers, the two packages, credential categories and remediation.
- [SafeDep: wfx GitHub Actions credential stealer](https://safedep.io/blog/github-actions-wfx-credential-stealer), fetched 2026-11-12: published 2026-11-12 by Kunal Singh; 8,093 repositories and the UTC window, the three packages, the cloud-account checks, remediation. A second firm's own count.
- [StepSecurity: WFX Phantom](https://www.stepsecurity.io/blog/wfx-phantom-the-github-actions-secret-stealer), fetched 2026-11-12: published 2026-11-12 by Owais Shaikh; the 63,000 figure with its read time, the Fly.io GitHub App observation and its limits, named repositories, identifiers, remediation. A third firm.
- [SecurityWeek: Attacker Targets 60,000 GitHub Repositories in Credential Theft Campaign](https://www.securityweek.com/attacker-targets-60000-github-repositories-in-credential-theft-campaign/), fetched 2026-11-12 (2026-11-12): the three firms' counts side by side, the note on SafeDep's unit, no GitHub statement.
- [The Hacker News: Attacker Used 4,837 Hijacked GitHub Accounts](https://thehackernews.com/2026/11/4837-hijacked-github-accounts-ran-ci.html), front-page summary read 2026-11-12: the 1,806 figure and the pull request title. The article body was read only for its links.
- Packagist metadata for `digitalelvis/neuronai-studio`, read 2026-11-12 through `repo.packagist.org/p2/`: 3.14.2 on 2026-10-19, 3.14.3 on 2026-11-11 12:29 UTC, 3.14.4 on 2026-11-12 07:50 UTC.
- Go module proxy, read 2026-11-12 through `proxy.golang.org`: `docker-env` latest v1.0.287 dated 2026-11-12 12:47 UTC; `gocurl` latest is the listed pseudo-version dated 2026-11-11 09:55 UTC.
- OSV, queried 2026-11-12 through `api.osv.dev/v1/query` for the Packagist package and `docker-env`: no record for either.
