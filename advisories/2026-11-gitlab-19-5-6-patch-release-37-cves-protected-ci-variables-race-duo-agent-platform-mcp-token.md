---
id: 2026-11-gitlab-19-5-6-patch-release-37-cves-protected-ci-variables-race-duo-agent-platform-mcp-token
title: "GitLab 19.5.6, 19.4.8 and 19.3.9 fix 37 CVEs: protected CI/CD variable race, Kubernetes Secrets read, ten Duo and MCP authorization bugs"
date_disclosed: 2026-11-16
last_updated: 2026-11-18
severity: high
status: patched
ecosystems: [gitlab, ci-cd, mcp, self-hosted]
tools_affected: ["GitLab CE/EE self-managed before 19.3.9, 19.4.8 and 19.5.6", "GitLab Duo Agent Platform", "GitLab MCP server", "GitLab agent for Kubernetes"]
tags: [cve, gitlab, ci-cd, protected-variables, duo-agent-platform, mcp, authorization, xss, vendor-batch]
---

## TL;DR
[GitLab's patch release of 2026-11-16](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-5-6-released/) fixes 37 CVEs in self-managed GitLab CE and EE. The highest let an authenticated user read protected CI/CD variables (CVE-2026-18241, 8.2), read Kubernetes Secrets from other namespaces (CVE-2026-97187, 7.6), or run script in other users' browsers (two at 8.7). Ten more are authorization bugs in GitLab Duo and the GitLab MCP server. Upgrade to 19.5.6, 19.4.8 or 19.3.9. GitLab.com and GitLab Dedicated are already patched.

## What the release fixes

The release post lists 37 CVE ids: 4 High, 24 Medium and 9 Low. The counts were made in code against the post on 2026-11-18. Every id is fixed in 19.5.6, 19.4.8 and 19.3.9.

### High

| CVE | What an authenticated user could do | Affected from | CVSS |
|---|---|---|---|
| CVE-2026-105739 | run JavaScript in the browser of anyone who views a wiki page | 17.2 | 8.7 |
| CVE-2026-108153 | run JavaScript in the browser of anyone who views Error Tracking pages | 16.1 | 8.7 |
| CVE-2026-18241 | "access protected CI/CD variables and resources due to a race condition in pipeline job authorization" | 9.3 | 8.2 |
| CVE-2026-97187 | read Kubernetes Secrets from other namespaces in clusters connected through the GitLab agent, through workspaces | 17.6 | 7.6 |

The scores are GitLab's, as CNA. CVE-2026-18241 has attack complexity High and CVE-2026-97187 needs high privileges.

### Duo, Amazon Q and MCP

Ten of the 37 titles name GitLab Duo, Duo with Amazon Q or the GitLab MCP server. None scores above 4.3. The four that change what an agent or a token can do:

| CVE | What it allowed | Affected from | CVSS |
|---|---|---|---|
| [CVE-2026-123142](https://cveawg.mitre.org/api/cve/CVE-2026-123142) | a user with an MCP-scoped OAuth token could change issue and merge request state, "including approving and merging" | 18.4, CE/EE | 4.3 |
| [CVE-2026-115736](https://cveawg.mitre.org/api/cve/CVE-2026-115736) | view unredacted secret values from secret detection findings through Duo Agent Platform | 19.1, EE | 4.3 |
| [CVE-2026-129253](https://cveawg.mitre.org/api/cve/CVE-2026-129253) | a developer-role user could bypass admin-configured AI tool governance controls in a governed namespace | 19.1, EE | 4.3 |
| [CVE-2026-128849](https://cveawg.mitre.org/api/cve/CVE-2026-128849) | start a Duo Workflow session with privileges beyond those the foundational flow declares | 19.5 only, EE | 4.3 |

The other six cover Duo seat management, usage analytics, group settings, Code Review consent, access rules, and the Amazon Q automatic code review lock (CVE-2026-115219).

CVE-2026-112203 (5.9, EE from 18.2) is a package-integrity bug. A party that controls one upstream repository could alter cached Maven packages from other repositories in the same virtual registry.

## Am I affected?

Self-managed GitLab CE or EE on a version before 19.3.9, 19.4.8 or 19.5.6 is affected. Read the version from the instance's Help page or Admin area.

Lines older than 19.3 are inside the affected ranges of most ids. This release publishes no version for them.

## If you are affected

- Upgrade to 19.5.6, 19.4.8 or 19.3.9. GitLab asks that self-managed installations "be upgraded to one of these versions immediately".
- If untrusted developers can run pipelines on the instance, rotate the protected CI/CD variables. CVE-2026-18241 goes back to 9.3.
- If workspaces and the GitLab agent for Kubernetes are in use, review access to cluster Secrets and rotate the ones other namespaces held.
- Review merge request approvals and merges made with MCP-scoped OAuth tokens since 18.4.
- See [CI/CD hardening](../prevention/ci-cd-hardening.md).

## Prevention

- Follow the GitLab patch release feed. Scheduled patch releases carry most security fixes.
- Scope MCP and agent tokens to read access where the workflow allows it, and require human approval for merges. See [MCP hygiene](../prevention/mcp-hygiene.md).

## Sources

- [GitLab Patch Release: 19.5.6, 19.4.8, 19.3.9](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-5-6-released/): vendor post, 2026-11-16, read 2026-11-18. Single source: the vendor.
- CNA records (GitLab, published 2026-11-17) read for [CVE-2026-18241](https://cveawg.mitre.org/api/cve/CVE-2026-18241), [CVE-2026-97187](https://cveawg.mitre.org/api/cve/CVE-2026-97187), CVE-2026-123142, CVE-2026-115736, CVE-2026-129253, CVE-2026-128849 and CVE-2026-115219.
- [GitLab patch release feed](https://docs.gitlab.com/releases/patch-releases.xml): release dates.
- Not opened: the other 30 CNA records and the HackerOne reports.
