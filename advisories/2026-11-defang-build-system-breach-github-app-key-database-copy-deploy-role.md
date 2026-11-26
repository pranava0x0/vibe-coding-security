---
id: 2026-11-defang-build-system-breach-github-app-key-database-copy-deploy-role
title: "Defang: attacker copied production credentials and the main database on 2026-11-12; GitHub App key and stored GitHub tokens usable until 2026-11-23"
date_disclosed: 2026-11-24
last_updated: 2026-11-26
severity: high
status: active
ecosystems: [saas, defang, github-apps, github-actions, aws, gcp, azure, ci-cd]
tools_affected: ["Defang Portal accounts", "repositories with the Defang GitHub App installed", "cloud accounts with the Defang GitHub Actions deploy role", "Defang deployments made between 2026-10-12 and 2026-11-19"]
tags: [incident, vendor-incident, saas-breach, github-app, ci-cd, release-tag-trust, deployment-state, cloud-deploy-role, stripe-key, investigation-open]
---

## TL;DR

[Defang says](https://defang.io/blog/post/security-incident-november-2026/) an attacker copied its production credentials and its main database on 2026-11-12. The credentials included the Defang GitHub App's key and the key that encrypts stored GitHub sign-in tokens. Until Defang replaced them on 2026-11-23, a holder could push commits, change workflows and overwrite Actions secrets in connected repositories. Deployment state from deploys between 2026-10-12 and 2026-11-19 was exposed, per the post, and can hold database passwords. Audit connected repositories and the cloud deploy role, then rotate those passwords.

## What happened

Defang published the post on 2026-11-24. All times are UTC and come from the post.

| Time | Event, per Defang |
|---|---|
| 2026-11-12 06:05 | The first workflow that copied build credentials ran, against development and staging. |
| 2026-11-12 06:26 | Production credentials were copied. |
| 2026-11-12 07:57 to 08:10 | The database was copied. |
| 2026-11-15 | Defang "were made aware of a security issue with a dependency and installed the update". |
| 2026-11-19 | Defang stopped keeping copies of deployment state. It also deleted the copies it had, with no date given. |
| 2026-11-23 | A routine security scan found suspicious activity in Defang's repositories. Defang confirmed the database copy, replaced production credentials and emailed affected users. |

Defang says the activity it can see "ran from about 06:00 to 10:30 UTC on November 12". The post lists the deployment state under what the attacker could see and does not say how state from deploys after 2026-11-12 was reached.

Defang says it ran a separate GitHub App for development and testing. The app was installed on two of Defang's own repositories and could change deployment environments. Acting as that app, the attacker pushed a commit and tagged it as a release. Production trusted release tags, so the attacker's code ran in CI with production credentials.

The post does not say how the attacker came to act as the development app. It does not name the dependency in the 2026-11-15 line or link it to the intrusion.

Defang says the credentials "stayed valid until we replaced them on November 23" and that it is "still checking whether they were used after November 12". It says some logs are not detailed enough to rule that out.

What the attacker could see, per the post:

- Name and email address, GitHub or GitLab username and organization names, and sign-up answers
- Names of the repositories the Defang GitHub App can access, private ones included
- Connected cloud account, project or subscription IDs and regions, with no credentials
- Compose files deployed or generated with Defang
- Deployment state from deploys between 2026-10-12 and 2026-11-19, which "can include database passwords and any environment variable built from a defang config value"

The post lists what a holder of the GitHub App key and sign-in tokens could do in connected repositories until 2026-11-23:

- push commits and branches
- change workflow files and start workflow runs
- overwrite Actions secrets and variables
- change deployment environments and their protection rules
- open and merge pull requests
- change repository settings, including branch protection, deploy keys and collaborators

Defang adds that a workflow run started this way "can receive your cloud credentials", because the deploy role trusts workflows in the repository. It says the role or identity it set up for GitHub deploys "has administrator access to your account".

The copied credentials also included Defang's Stripe key. Defang says a holder could read names, billing addresses, tax IDs, card brand, last four digits and expiry, and invoice history. Full card numbers were not available through the key.

Defang says it holds no user passwords and no cloud credentials, and that repository contents are not in its database.

## Am I affected?

- Every Defang Portal account is in the copied database, per the post.
- You are in the higher-risk group if you installed the Defang GitHub App, deploy from GitHub Actions with the role Defang set up, or deployed between 2026-10-12 and 2026-11-19.
- In each connected repository, look from 2026-11-11 onward for commits, branches or tags you do not recognize, and for changes under `.github/workflows`.
- Look for workflow runs you did not start, changed Actions secrets or variables, new deploy keys or collaborators, and changed branch protection.
- Defang says to look in particular at activity from `defang-app[bot]`.
- On AWS, Defang says the deploy role is usually `defang-cd-CIRole`. Search CloudTrail for `AssumeRoleWithWebIdentity` calls on it since 2026-11-11. A token from a branch or workflow you do not deploy from is a sign of misuse.
- On Google Cloud, check the workload identity pool's token exchanges. On Azure, check the sign-in logs for the managed identity.

## If you are affected

1. In each connected repository, open Settings, then Environments. For every environment whose name starts with `defang-`, restrict deployment branches and tags to your deploy branch.
2. In GitHub Settings, under Applications and Authorized GitHub Apps, revoke Defang. Sign in to Defang again afterwards. Uninstall the app if you no longer deploy from GitHub with it.
3. Narrow the deploy role's trust to the branch or environment you deploy from.
4. If you deployed between 2026-10-12 and 2026-11-19, change database passwords and any secret that was part of another environment variable, then redeploy. Defang says to use `defang config set <NAME>` for each one. Change secrets written directly in a Compose file too.
5. If a check finds something you do not recognize, rotate that repository's Actions secrets and the cloud credentials its workflows can reach, then tell Defang. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
6. Send new cloud invite links. Defang cancelled every pending one.

Defang says card replacement is not needed.

## Prevention

- A GitHub App that can push and edit workflows holds what your CI holds. Review each installed app's permissions and repository list. See [CI/CD hardening](../prevention/ci-cd-hardening.md).
- Scope cloud deploy roles to one branch or environment, and avoid administrator access for CI. See [credential hygiene](../prevention/credential-hygiene.md).
- Do not let a release tag alone grant a workflow production secrets. Require a protected environment with reviewers.

## Sources

Single source: the vendor.

- [Defang: Security incident: November 2026](https://defang.io/blog/post/security-incident-november-2026/), dated 2026-11-24, read 2026-11-26 with `curl`. Timeline, data lists, quotations and user steps.
- [Hacker News item 50648035](https://news.ycombinator.com/item?id=50648035): where the post surfaced, 76 points when read on 2026-11-26.
- Not found: outlet coverage on the three front pages read on 2026-11-26.
