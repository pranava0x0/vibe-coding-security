---
id: 2026-08-gitea-diffpatch-git-hook-rce
title: "Gitea diffpatch API git-hook RCE — CVE-2026-60004, actively exploited, added to CISA KEV (Aug 2026)"
date_disclosed: 2026-07-28
last_updated: 2026-08-28
severity: critical
status: active
ecosystems: [gitea, self-hosted-git]
tools_affected: [gitea]
tags: [rce, self-hosted-dev-infra, cisa-kev, git-hook-abuse, code-injection, unauthenticated-if-self-registration-enabled]
---

## TL;DR
Gitea before 1.27.1 lets an attacker with repository write access — or, on the many self-hosted instances that leave open self-registration on, an anonymous visitor who just signs up — turn a crafted `diffpatch` API request into a Git hook that executes shell commands as the Gitea service account. It's CVSS 9.8, was patched quietly in July, and CISA added it to its Known Exploited Vulnerabilities catalog on 2026-08-25 after confirming real-world exploitation, including at least one report of an outdated instance being compromised in about 11 seconds and turned into a cryptominer. Gitea is a common self-hosted git server for teams whose AI coding agents (Claude Code, Cursor, etc.) push, pull, and open PRs against it — an unpatched instance is a direct path from "agent commits code" to "attacker runs commands on your git server."

## What happened
Gitea's `POST /api/v1/repos/{owner}/{repo}/diffpatch` endpoint applies an attacker-supplied patch inside a temporary bare Git clone. On affected Git versions, submitting a duplicate, specially crafted patch induces an add/add collision that falls back to a Git three-way merge — and because the temporary clone's working directory is also its Git directory, attacker-controlled content from that merge gets materialized as an executable `post-index-change` hook. The hook fires on a subsequent index operation and runs arbitrary shell commands with the privileges of the OS account running Gitea ([Help Net Security](https://www.helpnetsecurity.com/2026/08/26/gitea-cve-2026-60004-exploited-in-the-wild/); [SecurityWeek](https://www.securityweek.com/cisa-warns-of-exploited-gitea-vulnerability/)).

Normally this requires repository **write** access — but Gitea ships with open self-registration enabled by default in many deployments, so on a default-configured instance an unauthenticated remote attacker can register an account, create a repository, and trigger the chain without any prior credentials, per Gitea's own advisory as cited by SecurityWeek.

- **CVE:** CVE-2026-60004 (CWE-94, code injection)
- **CVSS:** 3.1 base score 9.8 (`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`), confirmed via the NVD API record for this CVE.
- **GHSA:** GHSA-rcr6-4jqh-j84m
- **Affected:** Gitea 1.17.0 through 1.27.0
- **Patched:** 1.27.1, released 2026-07-28
- **Exploited in the wild:** confirmed; added to CISA's KEV catalog 2026-08-25, with a federal-agency remediation deadline of 2026-08-28. Help Net Security reports one documented case where an outdated, self-registration-enabled instance was compromised in roughly 11 seconds and used to deploy a cryptocurrency-mining payload. As of SecurityWeek's reporting, threat-actor identity and objectives beyond that observed cryptomining case remain unconfirmed, and roughly 8,300 internet-exposed Gitea servers were still reachable and unpatched at time of reporting.

**Why this matters for AI-agent workflows specifically.** Gitea is a popular self-hosted alternative to GitHub/GitLab for teams running their own infrastructure, and it's frequently the git remote that coding agents (Claude Code, Cursor, OpenHands, and CI pipelines built around them) are configured to push branches to and open PRs against. An agent — or a human — merely interacting normally with a vulnerable, internet-exposed Gitea instance (cloning, diffing, or reviewing a PR that itself contains the crafted patch) can trigger server-side RCE with no separate exploit delivery needed beyond the patch content itself.

## Am I affected?
```bash
# Check your Gitea version
gitea --version
# or, via the web UI/API:
curl -s https://your-gitea-host/api/v1/version

# Vulnerable: 1.17.0 through 1.27.0
# Patched: 1.27.1 and later

# Check whether open self-registration is enabled (widens the bug to unauthenticated)
grep -i 'DISABLE_REGISTRATION' /path/to/gitea/custom/conf/app.ini
```

## If you are affected
1. Upgrade to Gitea 1.27.1 or later immediately — this is a KEV-listed, actively exploited RCE.
2. If you cannot patch immediately, disable self-registration (`DISABLE_REGISTRATION = true` in `app.ini`) and restrict repository write access to trusted accounts only, to at least require write access rather than anonymous registration.
3. Take the instance off the public internet (VPN/allowlist access) until patched if it's currently internet-exposed.
4. Treat any pre-patch instance that was internet-exposed with self-registration on as potentially compromised — check for unexpected processes, cron jobs, or outbound connections consistent with cryptomining, and review Gitea's own access/audit logs for anonymous account creation followed by repository creation and diffpatch API calls.
5. Rotate any credentials (deploy keys, CI tokens, secrets stored in Gitea Actions) the Gitea service account or its host had access to, since RCE as that account can reach them.

→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — keep self-hosted git/CI infrastructure patched and off the open internet where possible; disable open self-registration on internal tooling.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources
- [Help Net Security — Critical Gitea vulnerability now exploited in the wild (CVE-2026-60004)](https://www.helpnetsecurity.com/2026/08/26/gitea-cve-2026-60004-exploited-in-the-wild/) — vulnerability mechanics, KEV addition, exploitation details.
- [SecurityWeek — CISA Warns of Exploited Gitea Vulnerability](https://www.securityweek.com/cisa-warns-of-exploited-gitea-vulnerability/) — CISA KEV confirmation, patch timeline, exposure scale, self-registration caveat.
- [CISA KEV JSON feed](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) — authoritative KEV listing (dateAdded confirmation), fetched directly this sweep.
- [NVD API record for CVE-2026-60004](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-60004) — CVSS score/vector, affected range, GHSA cross-reference.
