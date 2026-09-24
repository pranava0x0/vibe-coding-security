---
id: 2026-09-gitlab-incoming-email-token-push-to-main
title: "GitLab's 'email this project' address is an account-wide, non-expiring credential: anyone holding your incoming+…-glimt-…@incoming.gitlab.com address can change the -issue suffix to -merge-request, attach a .patch, and GitLab commits it as you and runs CI on it — in every project you can reach, past IP allow-lists and 2FA; GitLab closed the HackerOne report as intended behaviour (Aikido, 2026-09-23)"
date_disclosed: 2026-09-23
last_updated: 2026-09-24
severity: high
status: mitigated
ecosystems: [gitlab, self-hosted, ci-cd, source-hosting]
tools_affected: ["GitLab.com (all users; incoming email is on by default)", "self-managed GitLab CE/EE with incoming email enabled", "GitLab Dedicated (reported unaffected, not tested)"]
tags: [gitlab, credential-exposure, design-flaw, wont-fix, ci-cd, impersonation, merge-request, incoming-email, secret-detection, leaked-token]
---

## TL;DR
On **2026-09-23** Aikido Security published "Send GitLab an email, push to main": the private address GitLab gives every user for filing issues by email — `incoming+<project>-<id>-glimt-<token>-issue@incoming.gitlab.com` — embeds an **account-level token** (`glimt-…`) that is the same for every project, **never expires**, and is accepted **without any check on who sent the email**. Change `-issue` to `-merge-request`, put a branch name in the subject and a `.patch` in the body, and GitLab **commits the patch under the victim's identity and runs the pipeline** — including a modified `.gitlab-ci.yml` — in **any project the victim can reach**, public or private, and "GitLab blocked our browser and rejected our git clone commands. But it still accepted a merge request email" from a project behind an IP allow-list. Confirmed impact: pushing to protected branches behind IP restrictions, exfiltrating private source, reading CI/CD variables and secrets and confidential issues, and lateral movement with `CI_JOB_TOKEN`. Aikido reported it via HackerOne in **May 2026** (closed as intended behaviour) and as a confidential issue in **June**; GitLab's position is that the token is "like any other" credential. What changed: the UI no longer says the address "cannot be used to access any other data," now mentions merge requests, and the docs state "incoming email is not subject to IP restrictions." What did not: the token still does not expire, the sender is still not checked, and **no user can turn the feature off**. Aikido found a dozen live addresses published in READMEs and contributing guides. Rotate yours today (profile → *Reset incoming email token*) and add the `glimt-` pattern to secret scanning.

## What happened

**The feature.** GitLab's "Email a new issue / work item to this project" gives each user, per project, an address of the form above. The documentation has always said the holder of the incoming email token can create issues and merge requests as the token owner. Aikido's contribution is showing what that means in practice and that the project-scoped presentation is false: "Although the interface presents a project-specific address, Aikido found that addresses generated for different projects embed the same account-level token" (THN's summary). So one leaked address is authority over every project the account can see.

**The attack, as Aikido describes it.** Three properties combine: (1) the token grants account-wide scope; (2) the `-issue` / `-merge-request` suffix selects the action, and merge-request emails accept attached `.patch` files targeting a named source branch — "attackers can attach `.patch` files containing malicious code modifications (like `.gitlab-ci.yml` changes) that GitLab automatically applies"; (3) email is not subject to the instance's IP allow-list, and "the token does not expire." The result, per the researchers: "Anyone holding that address can push code and run CI/CD jobs in every project your account can reach." The demonstration pushed to a protected branch of an IP-restricted private project whose web UI and git endpoints had refused them. Once a pipeline runs attacker-authored CI, the rest follows — CI/CD variables, `CI_JOB_TOKEN` for lateral movement, confidential issues, source of every private project.

**GitLab's response.** HackerOne, May 2026: closed as intended behaviour. Confidential issue, June 2026, with fuller analysis: the position was "that this is a token like any other, and that any leaked credential leads to bad outcomes" (Aikido). GitLab then shipped UI and documentation edits — the misleading "cannot be used to access any other data" line is gone, "and merge requests" was added, and the docs note the IP-restriction exemption — but "the behavior has not changed. The token still does not expire, GitLab still does not check who sent the email, and there is still no switch for an individual user to turn off the feature." GitLab.com and self-managed instances with incoming email enabled (the default) are affected; Dedicated appears unaffected but was not tested.

**Why the token leaks.** It is designed to be pasted into a mail client, so it ends up in mail archives, shared inboxes, screenshots, and — Aikido found "a dozen live incoming email addresses deliberately published in open-source project documentation, READMEs, and contributing guides." Users treat it as a project mailbox address because that is what the UI called it. Secret scanners did not flag it because nobody had told them `glimt-` was a secret. "This is not user error."

**Why it matters for vibe coders.** An AI coding agent with repo read access will happily quote a CONTRIBUTING.md that says "email issues to incoming+…"; a bot that mirrors issues or triages email will store the address; and a `.patch`-by-email merge request is precisely the kind of input a CI pipeline configured by an assistant will build without a human looking at the diff. The credential is also invisible to the controls this audience is told to rely on — 2FA, IP allow-lists, protected branches with push rules — because the email path was never wired to them. Same lesson as [the KEV'd GitLab file read](2026-09-gitlab-cve-2026-85706-unauth-file-read-kev.md) and the [MCP account-takeover cluster](2026-07-gitlab-mcp-account-takeover-cve-cluster.md): the source host has more front doors than the one your policy guards.

## Am I affected?

- **Affected if:** you have a GitLab.com account, or a self-managed instance with incoming email configured (the default in Omnibus/Helm installs), **and** your incoming email address has ever been shared, archived, or committed.
- **Practically everyone on GitLab holds the credential;** the question is whether it leaked.

```bash
# Has the token ever been committed to any repo you control?
git log -p --all -S 'glimt-' -- . | grep -m5 'glimt-'
grep -rnE 'incoming\+[A-Za-z0-9._-]+-glimt-[A-Za-z0-9]+' . --include='*.md' --include='*.txt' --include='*.yml' 2>/dev/null
# Mailboxes, wikis, ticketing exports, Slack — search for "incoming+" and "@incoming.gitlab.com" (or your instance's incoming domain)
# Self-managed: is incoming email on?
grep -n "incoming_email" /etc/gitlab/gitlab.rb 2>/dev/null | grep -v '^#'
```

## If you are affected

1. **Reset the token now:** GitLab → user profile → *Reset incoming email token*. This invalidates every address that embedded the old token; anything that legitimately used one (an issue-by-email integration) must be re-issued.
2. If an address had leaked, review merge requests and pipelines created **from email** under your identity in every project you can reach (MRs created via email carry no browser session; look for `.gitlab-ci.yml` changes in MRs you do not remember opening), and treat the CI/CD variables of any project where such a pipeline ran as exposed → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) (the PAT playbook's inventory-and-rotate order applies to a GitLab token).
3. Remove the address from every README, CONTRIBUTING.md, wiki and support template; the feature has no per-project address that is safe to publish.
4. Self-managed admins: if issue-by-email is not needed, disable incoming email for the instance — it is the only way to close the path; there is no per-user switch.

## Prevention

- **Add `glimt-` and `incoming+…@incoming.gitlab.com` to secret detection** (pre-commit hooks, CI secret scanning, and your mail DLP). Aikido has shipped a detection; add the regex to whatever scanner you run. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- **Don't treat IP allow-lists or 2FA as the boundary for a source host.** Email-to-MR, deploy keys, CI job tokens and MCP tokens each bypass one of them. Protected branches should require an approval that an emailed MR cannot self-satisfy. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Review every MR's CI changes before the pipeline runs** — a `.gitlab-ci.yml` change in a merge request is code execution on your runners; require approval for pipeline changes from any source.

## Sources
- [Aikido Security — Send GitLab an email, push to main](https://www.aikido.dev/blog/gitlab-email-push-to-main) — primary, 2026-09-23: the address format and account-level scope, the `-merge-request` suffix and `.patch` attachment, the IP-allow-list bypass demonstration, the May (HackerOne, closed as intended) and June (confidential issue) timeline, GitLab's "like any other" position, the UI/doc changes, the dozen published addresses, and the mitigation list. Fetched 2026-09-24.
- [The Hacker News — A Leaked GitLab Issue Email Address Lets Anyone Push Code and Run CI Jobs as You](https://thehackernews.com/2026/09/a-leaked-gitlab-issue-email-address.html) — 2026-09-23: independent write-up of the Aikido report; "the private email address GitLab gives you for filing issues by email is a credential," the non-expiry and no-sender-check properties, the 2FA/IP-restriction bypass, the reset-token mitigation. Fetched 2026-09-24. (THN is reporting Aikido's research, not independent verification; GitLab's own documentation, as quoted by both, confirms the token's stated capabilities.)
- Related in this corpus: [GitLab 19.4.1 critical patch release](2026-09-gitlab-19-4-1-regex-rce-duo-mcp-batch.md) (same day), [GitLab CVE-2026-85706 (KEV)](2026-09-gitlab-cve-2026-85706-unauth-file-read-kev.md), [GitLab MCP account-takeover cluster](2026-07-gitlab-mcp-account-takeover-cve-cluster.md).
