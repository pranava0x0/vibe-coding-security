---
id: 2026-09-gitlab-19-4-1-regex-rce-duo-mcp-batch
title: "GitLab 19.4.1 / 19.3.3 / 19.2.7 (2026-09-23): two CVSS 9.9 authenticated RCEs from a crafted regular expression in a CI/CD configuration (CVE-2026-89078 double free, CVE-2026-93577 integer overflow), plus four AI-feature bugs — Duo troubleshooting leaks CI/CD variable values, an MCP-scoped token acts beyond its scope, Duo Workflow governance bypass, MCP search returns another user's results"
date_disclosed: 2026-09-23
last_updated: 2026-09-24
severity: critical
status: patched
ecosystems: [gitlab, self-hosted, ci-cd, source-hosting, mcp]
tools_affected: ["GitLab CE/EE 19.2.0 – 19.2.6, 19.3.0 – 19.3.2, 19.4.0 (the two RCEs)", "GitLab EE 18.7+ Duo AI job troubleshooting (CVE-2026-92470)", "GitLab CE/EE 18.3+ MCP API scope enforcement (CVE-2026-92874)", "GitLab EE 19.1+ Duo Workflow Service (CVE-2026-92529)", "GitLab CE/EE 18.6+ MCP gitlab_search tool (CVE-2026-92628)"]
tags: [cve, rce, regex, ci-cd, gitlab, duo, mcp, ai-feature, secrets-exposure, authorization-bypass, patch-release]
---

## TL;DR
GitLab's **critical patch release of 2026-09-23** — **19.4.1, 19.3.3, 19.2.7** — fixes eleven vulnerabilities, two of them **CVSS 9.9 Critical** and both the same shape: an **authenticated user could execute arbitrary code on the GitLab server** by putting **a specially crafted regular expression in a CI/CD configuration** — **CVE-2026-89078** (a double free in the regex parser, CWE-415) and **CVE-2026-93577** (an integer overflow in the regex compiler, CWE-190), both reported by joaxcar via HackerOne, both affecting **19.2 before 19.2.7, 19.3 before 19.3.3 and 19.4 before 19.4.1**. NVD scored both 9.9 on 2026-09-24 (`AV:N/AC:L/PR:L/UI:N/S:C`). Any user who can push a `.gitlab-ci.yml` — every developer on a self-managed instance, every external contributor whose merge-request pipelines run — is "authenticated." The same release carries **four AI-feature fixes** the headline hides: **CVE-2026-92470** (7.7) — the **Duo AI job-troubleshooting** feature let an authenticated user read **sensitive CI/CD variable values from debug-mode job traces**; **CVE-2026-92874** (5.4) — an **MCP-scoped token** could "perform actions beyond the intended scope of that token" (18.3+); **CVE-2026-92529** (4.3) — a developer could bypass admin-configured **AI tool governance** for Duo Workflow; **CVE-2026-92628** (3.1) — a race in the **MCP `gitlab_search` tool** "could cause results to return under incorrect user context." Also fixed: an 8.7 stored XSS in the merge-request diff viewer (CVE-2026-84739, 13.11+) and an unauthenticated read of CI job traces with variable values (CVE-2026-4523, 15.11+). GitLab.com is patched; "we strongly recommend all installations upgrade immediately." Second critical GitLab release in two weeks after [CVE-2026-85706's KEV entry](2026-09-gitlab-cve-2026-85706-unauth-file-read-kev.md).

## What happened

**The two RCEs.** GitLab's patch post describes them in near-identical words. CVE-2026-89078: "An authenticated user could execute arbitrary code on the GitLab server due to a double free issue when parsing a specially crafted regular expression" in a CI/CD configuration; CVE-2026-93577: "…due to an integer overflow when compiling a specially crafted regular expression in a CI/CD configuration." Both are `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H` (the double free is `A:L`, the overflow `A:H`), both are scope-changed — code runs on the GitLab server, not in a runner — and both were found by the same HackerOne researcher (joaxcar; reports #4019059 and #3995696). The affected range is narrow (the regex engine path was introduced in 19.2, so 19.1 and earlier are not listed), but 19.2–19.4 is the current release train. The vector is the CI/CD configuration itself: `.gitlab-ci.yml` `rules:`/`only:`/`except:` regexes and similar fields are evaluated **on the server** when a pipeline is created, so the exploit is a commit, a merge request from a fork with pipelines enabled, or an API call that creates a pipeline with an inline configuration.

**The AI-feature batch.** Four of the eleven fixes are in Duo or MCP surfaces, none critical on its own but each a scope failure of the kind this corpus tracks for [GitLab's MCP server](2026-07-gitlab-mcp-account-takeover-cve-cluster.md) and [Duo Chat](2026-09-gitlab-cve-2026-85706-unauth-file-read-kev.md):

| CVE | CVSS | Component | GitLab's description |
|---|---|---|---|
| CVE-2026-92470 | 7.7 High | Duo AI job troubleshooting (EE 18.7+) | "An authenticated user could access sensitive CI/CD variable values from debug-mode job traces through the Duo AI troubleshooting feature" |
| CVE-2026-92874 | 5.4 Medium | MCP API scope enforcement (CE/EE 18.3+) | "An authenticated user with an MCP-scoped token could perform actions beyond the intended scope" |
| CVE-2026-92529 | 4.3 Medium | Duo Workflow Service token governance (EE 19.1+) | "A developer could bypass admin-configured AI tool governance controls for workflows" |
| CVE-2026-92628 | 3.1 Low | MCP `gitlab_search` tool (CE/EE 18.6+) | "Race condition in MCP search tool could cause results to return under incorrect user context" |

The Duo troubleshooting bug is the one to act on: a debug-mode job trace contains the values of masked variables, and the feature that summarises "why did this job fail?" for the model was reading traces its caller could not. The MCP-scope bug matters for anyone who minted a narrow token for a coding agent — the narrowing did not hold. All four were found internally (Daniel Prause, Amr Taha, Rahul Barnwal, Chris Bonk).

**The rest.** CVE-2026-84739 (8.7 High, 13.11+): stored XSS in the merge-request diff viewer — "an authenticated user could execute arbitrary JavaScript in another user's browser session," which on a source host is a session-theft primitive. CVE-2026-4523 (3.7 Low, 15.11+): "an unauthenticated user could read CI/CD job trace contents with sensitive variable values" through the GraphQL job-trace API — low CVSS because of the high attack complexity, but the payload is secrets. Plus authorship spoofing in Direct Transfer imports (CVE-2026-92530), private child-issue reads via the Epic Issues API (CVE-2026-8937), and a GraphQL resolver leaking security-policy content to guests (CVE-2026-10518).

**Why it matters for vibe coders.** A self-managed GitLab is the CI, the registry proxy and increasingly the agent host (Duo agents, the MCP server) for teams that left GitHub; a 9.9 reachable from a `.gitlab-ci.yml` means any contributor with a merge request — or any coding agent with push rights — can run code on the box that holds every project's secrets. And the four AI-feature bugs are all the same lesson as the corpus's other agent-platform entries: the new surface (a troubleshooting summariser, an MCP scope, a workflow governance switch) was wired to data the caller should not have had.

## Am I affected?

- **RCE-affected if:** self-managed GitLab CE/EE **19.2.0–19.2.6, 19.3.0–19.3.2 or 19.4.0**, with any user or bot able to create pipelines (including fork merge-request pipelines).
- **Duo/MCP-affected if:** EE with Duo enabled on 18.7–19.4.0 (troubleshooting leak), any edition 18.3+ using MCP-scoped tokens, EE 19.1+ using Duo Workflow governance, any edition 18.6+ with the MCP `gitlab_search` tool.
- **Not affected:** 19.4.1 / 19.3.3 / 19.2.7 and later; GitLab.com (already patched); GitLab Dedicated per GitLab's standard patch process.

```bash
# Version
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.example.com/api/v4/version"
# Who can create pipelines from forks? (MR pipelines from forks run the fork's .gitlab-ci.yml on your instance)
# Settings → CI/CD → "Pipelines for merge requests from forks" — review per project.
# Debug-mode job traces (CI_DEBUG_TRACE) that Duo troubleshooting could have read
grep -rn "CI_DEBUG_TRACE" --include=.gitlab-ci.yml . 2>/dev/null
# MCP-scoped tokens minted for agents
curl -s -H "PRIVATE-TOKEN: $GITLAB_TOKEN" "https://gitlab.example.com/api/v4/personal_access_tokens?state=active" | grep -i mcp
```

## If you are affected

1. **Upgrade now** to 19.4.1, 19.3.3 or 19.2.7. There is no listed workaround for the RCEs.
2. If the instance ran an affected version with external contributors or agents able to create pipelines, review pipeline creation events for the window (from whenever the instance first ran a 19.2.x release) for CI configurations containing unusual regexes, and treat a suspicious hit as server compromise: → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md), then rotate every CI/CD variable, runner registration token and integration secret the instance held — → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. If Duo troubleshooting was enabled with debug-mode traces (CVE-2026-92470) or the GraphQL job-trace API was reachable unauthenticated (CVE-2026-4523), rotate the masked variables those jobs used; masking does not survive `CI_DEBUG_TRACE`.
4. Re-mint MCP-scoped tokens after upgrading and audit what they were used for; the scope was advisory until 19.4.1.

## Prevention

- **Treat CI configuration as server-side code.** A `.gitlab-ci.yml` is parsed by the GitLab server; restrict who can create pipelines (disable fork MR pipelines, or require approval) and keep the instance on the current patch. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Never run `CI_DEBUG_TRACE` in jobs that hold real secrets** — two of this release's eleven bugs are "someone could read a debug trace." [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- **Scope tokens, then verify the scope.** An MCP-scoped or agent-scoped token is only as narrow as the server enforces; test a minted token against an out-of-scope call before trusting it in an agent's config. [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).
- Subscribe to GitLab's patch-release feed (`docs.gitlab.com/releases/patches/`); this is the second critical in two weeks and GitLab ships fixes on a fixed cadence with no pre-announcement of severity.

## Sources
- [GitLab — GitLab Critical Patch Release: 19.4.1, 19.3.3, 19.2.7](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-4-1-released) — vendor patch post, 2026-09-23: all eleven CVEs with titles, CVSS vectors, affected ranges, reporters and descriptions quoted above; "we strongly recommend all installations upgrade immediately." Fetched 2026-09-24.
- [NVD API — CVE-2026-93577](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-93577) and [CVE-2026-89078](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-89078) — both published 2026-09-24, CVSS 3.1 9.9 Critical, descriptions matching the vendor post. Queried 2026-09-24.
- [GitHub Advisory Database — GHSA-wqwg-376r-c226 (CVE-2026-93577)](https://github.com/advisories/GHSA-wqwg-376r-c226), [GHSA-9chr-4x58-948m (CVE-2026-89078)](https://github.com/advisories/GHSA-9chr-4x58-948m), [GHSA-c3rm-3hqr-4qwm (CVE-2026-92874)](https://github.com/advisories/GHSA-c3rm-3hqr-4qwm) — mirrors of the GitLab CNA records, published 2026-09-24; HackerOne report numbers and GitLab work-item links. The MCP-scope entry surfaced through the advisory database's `mcp` recency listing. Fetched 2026-09-24.
- Not fetched: SecurityOnline's coverage (503 at fetch time). No independent researcher write-up exists yet; every technical fact above is from GitLab's own post and the CNA records it authored.
- Related in this corpus: [GitLab CVE-2026-85706 unauthenticated file read (KEV) + Duo Chat / Duo Claude agent](2026-09-gitlab-cve-2026-85706-unauth-file-read-kev.md), [GitLab MCP server account-takeover cluster](2026-07-gitlab-mcp-account-takeover-cve-cluster.md), and the [GitLab incoming-email token](2026-09-gitlab-incoming-email-token-push-to-main.md) design flaw disclosed the same day.
