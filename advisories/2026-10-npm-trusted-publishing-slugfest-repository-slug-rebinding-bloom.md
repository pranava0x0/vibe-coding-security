---
id: 2026-10-npm-trusted-publishing-slugfest-repository-slug-rebinding-bloom
title: "npm trusted publishing bound packages to a repository name, not its ID; a freed slug could publish 1,500+ packages (SlugFest); fixed 2026-10-02"
date_disclosed: 2026-10-13
last_updated: 2026-10-14
severity: high
status: patched
ecosystems: [npm, github-actions, gitlab-ci, supply-chain]
tools_affected: ["npm packages with a trusted publishing configuration whose bound repository slug was renamed, transferred or deleted before the package's first trusted publish", "npm trusted publishing via GitLab CI/CD (same binding model, per the researchers)"]
tags: [npm, trusted-publishing, oidc, repository-slug, resurrection, supply-chain, registry-fix, no-cve, patched]
---

## TL;DR
npm's trusted publishing stored the GitHub repository a package trusts as an `owner/repo` name and ignored the numeric `repository_id` and `repository_owner_id` claims in GitHub's OIDC token until the package's first successful publish. Bloom Security (published 2026-10-13, reported to GitHub 2026-06-06) showed that when a bound repository or its owner was renamed, transferred or deleted, anyone who registered the freed slug and added a workflow with the same filename could exchange a token for a publish credential and ship a release, with no stolen secret. They count 1,500+ packages with 10M+ total downloads in that state and withheld the names. GitHub's changelog of 2026-10-02 carries the fix without crediting it: unvalidated trusted publishing configurations now expire 48 hours after creation, a configuration is validated by its first publish and then tied to the repository's immutable identity, and tokens from `issue_comment` workflow events are rejected. Maintainers: run `npm trust list` on every package and delete any binding whose slug you no longer control.

## What happened

### The binding

`npm trust github --allow-publish` stores three things: the repository slug, the workflow filename, and an optional environment name. GitHub's OIDC token for a workflow run carries the slug and also the numeric repository and owner ids, which survive renames and are never reused. Per Bloom's write-up, npm compared the slug and the workflow filename at exchange time and stored the numeric ids only after the first successful publish from that repository. A binding that had never published was therefore a name, and names on GitHub are reusable the moment the original is renamed, transferred, or deleted.

The attack, as the researchers describe running it end to end against a scope they own: find a package whose trusted-publisher slug no longer resolves, create a repository at that slug, add a workflow with the bound filename, run it, exchange the token, publish. No maintainer credential, no phishing, no npm account takeover. The same binding model applied to npm's GitLab trusted publishing. The researchers note PyPI's Warehouse resolves the numeric ids at trust creation and requires exact matches, which is the fix they recommend.

### The numbers, and what they are not

Bloom states 1,500+ vulnerable packages, 10M+ total downloads and more than 1M monthly, relative to packages with trusted publishing configured, and withheld the list because the condition "was still prevalent" at publication. The headline's "millions of AI agents" is not a count in the article; the agent material is a separate measurement "across dozens of organizations" (0.3 to 1.2 new packages installed per agent per day, three agents on an average endpoint, about 70 agent-installed packages per endpoint per month, direct installs only), offered as the reason a hijacked package reaches machines faster than before. The Hacker News pickup prints "1,500+" in one place and "thousands" in another. This file carries Bloom's figures as Bloom states them.

### The fix and the timeline

- 2026-06-06: reported to GitHub via HackerOne; 06-09 triaged and validated; 07-08 last substantive response; six follow-ups and a mediation request unanswered, per Bloom.
- 2026-10-02: GitHub changelog, "Unvalidated npm trusted publishing configurations now expire": 48 hours after creation unless a successful publish validates it; a validated configuration is exempt and bound to the repository's immutable identity; changing the repository or project identity requires a new trust relationship with a fresh window; tokens from GitHub Actions `issue_comment` events are rejected, alongside the existing `pull_request_target` restriction. No researcher is credited and no vulnerability is named; the entry says the expiry "limits the risk of trusting a repository or project name that changes ownership". The page carried a "Retired" label when read on 2026-10-14, which the page does not explain.
- 2026-10-13: Bloom publishes, after retesting and finding the fix shipped; npm replied, apologised for the communication and said the fix landed in its 2.10 release. "Over 120 days" from report to fix is Bloom's figure.

What an upgrade with no further action gives the reader: nothing, because this is a registry-side change. What the change gives: a binding created from now on dies in 48 hours unless used, and a used binding follows the repository's id, not its name. What it does not state: whether bindings that existed before 10-02, were never used, and are older than 48 hours were expired retroactively. The audit below assumes not.

### Why this belongs here

Trusted publishing is the control this corpus has recommended since the [Shai-Hulud](2025-11-shai-hulud-second-coming.md) waves: no long-lived token on the maintainer's machine. SlugFest does not weaken that advice; it shows the trust binding itself is a credential with a lifetime, and that a repository rename is a security event. It is also the second registry-identity bug this month after [Docker Hub's token transfer](2026-10-docker-hub-ghostpat-pat-transfer-account-conversion-cve-2026-105445.md).

## Am I affected?

```bash
# For each package you maintain: what repository is trusted, and does it still resolve to you?
npm trust list <package>
# For every slug printed: open https://github.com/<owner>/<repo>. A 404, a redirect to a
# different name, or a repository you do not own means the binding must be deleted.

# Have you renamed, transferred or deleted a repository that publishes to npm since 2025-07-31?
# GitHub keeps no list of former names you can query; your own records and the audit log are the source.

# Publishes you did not initiate: the registry's time field, newest first
npm view <package> time --json | python3 -c 'import json,sys; t=json.load(sys.stdin); [print(v,k) for k,v in sorted(t.items(), key=lambda kv: kv[1], reverse=True)[:10]]'
```

A release in your package's timeline from a date no workflow of yours ran, after a rename or transfer of the bound repository, is the artefact.

## If you are affected

Delete the stale binding and recreate it against the current slug, then publish once so the new binding validates. If a release you did not make exists, deprecate it, publish a clean version, and follow [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md) for the downstream notification steps even though no token was involved; the effect on consumers is the same.

## Prevention

- Create the trust binding and publish within the same hour. An unused binding is now a 48-hour object by design; treat it that way.
- Remove the binding before deleting, renaming or transferring a repository, and recreate it after.
- Consumers: [npm-hardening](../prevention/npm-hardening.md) and [package-vetting-checklist](../prevention/package-vetting-checklist.md); a trusted-publishing provenance badge attests which repository built the release, and this bug is precisely a case where that repository was not the maintainer's.

## Sources
- [Bloom Security — SlugFest: millions of AI agents download exposed npm packages](https://bloom.security/blog/slugfest-millions-of-ai-agents-download-exposed-npm-packages) (2026-10-13 09:41 UTC; mechanism, counts, disclosure timeline, GitLab scope, PyPI comparison, maintainer checks)
- [GitHub changelog — Unvalidated npm trusted publishing configurations now expire](https://github.blog/changelog/2026-10-02-unvalidated-npm-trusted-publishing-configurations-now-expire/) (2026-10-02; 48-hour expiry, validation by first publish, immutable-identity binding, `issue_comment` rejection; no credit, no CVE)
- [The Hacker News — GitHub tightens npm publishing after flaw left 1,500+ packages vulnerable to hijacking](https://thehackernews.com/2026/10/github-tightens-npm-publishing-after.html) (2026-10-13; pickup of the above two, with the npm docs links)
- [npm docs — Trusted publishers: configuration expiry](https://docs.npmjs.com/trusted-publishers#trusted-publisher-configuration-expiry) (the documented behaviour after the change)
