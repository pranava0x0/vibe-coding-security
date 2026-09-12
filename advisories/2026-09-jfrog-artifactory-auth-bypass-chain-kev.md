---
id: 2026-09-jfrog-artifactory-auth-bypass-chain-kev
title: "JFrog Artifactory — CVE-2026-42018 + CVE-2026-42016 chained in the wild for unauthenticated admin tokens since mid-August; Rust backdoors and Groovy plugins planted; CISA KEV (Sept 11); ~60% of instances still unpatched"
date_disclosed: 2026-09-10
last_updated: 2026-09-12
severity: critical
status: active
ecosystems: [jfrog-artifactory, self-hosted, package-registry, ci-cd]
tools_affected: ["JFrog Artifactory self-hosted < 7.133.11 (CVE-2026-42016)", "JFrog Artifactory self-hosted before the 7.111.20-line fixes (CVE-2026-42018)", "JFrog Artifactory 7.111.4 – 7.161.19 (CVE-2026-82329)"]
tags: [cve, cisa-kev, auth-bypass, privilege-escalation, package-registry, supply-chain, backdoor, groovy-plugin, rapid-exploitation, self-hosted]
---

## TL;DR

Wiz Research reported on **2026-09-10** that attackers have been **chaining two JFrog Artifactory bugs since 2026-08-15** to go from nothing to an administrator token in two requests: **CVE-2026-42018** (CVSS 7.5 — an unauthenticated `POST /access/api/v1/aws/token/` returns an internal anonymous-user JWT even with anonymous access disabled) followed by **CVE-2026-42016** (CVSS 8.1 — token *scope* is not enforced, so that low-privilege JWT can mint an admin-scoped token at `/access/api/v1/tokens`). A third, already-tracked bug, **CVE-2026-82329** (CVSS 9.8, unauthenticated admin via a phantom join key), was exploited by "several" actors between 2026-09-01 and 09-08. Post-exploitation: persistent admin accounts, **malicious Groovy plugins for code execution**, **Rust backdoors with C2**, cluster-key theft, SSH keys attached to new accounts, configuration exfiltration. **CISA added CVE-2026-42016 and CVE-2026-42018 to KEV on 2026-09-11.** Six weeks after disclosure, Wiz measured **59% / 62% / 49%** of instances still vulnerable to the three bugs respectively. Artifactory is the private npm/PyPI/Maven proxy in front of many CI pipelines; an attacker with admin on it controls what your builds install.

## What happened

**The chain.** Artifactory's Access service exposes an endpoint intended for AWS-token exchange. With a trailing slash, an unauthenticated request to `/access/api/v1/aws/token/` returned HTTP 200 with an internal anonymous-user JWT — even when the instance had anonymous access switched off (CVE-2026-42018, disclosed 2026-08-12). Artifactory then validated only a token's signature and issuer, not its authorised scope, when it was presented to `/access/api/v1/tokens`; a valid low-privilege token could therefore request elevated permissions (CVE-2026-42016, disclosed 2026-07-27). Wiz observed the two used together from **2026-08-15 through 2026-09-08**, with account creation or other malicious activity typically following within minutes.

**The third bug.** CVE-2026-82329 (2026-08-28) is the unauthenticated join-key bypass this repo already tracks as an update inside the [OpenAI/Hugging Face intrusion advisory](2026-07-huggingface-agentic-intrusion.md), which has served as the home for Artifactory tracking because that intrusion abused Artifactory zero-days. Wiz saw several distinct actors exploiting it 2026-09-01 → 09-08; The Register notes watchTowr documented attacks beginning four days after disclosure. Wiz's affected range for it is 7.111.4 – 7.161.19 with per-branch fixes starting at 7.111.21 (the full per-branch list is in the Hugging Face advisory's 2026-09-02 update).

**Post-exploitation, as observed by Wiz:** creation of persistent administrator accounts; deployment of **Groovy plugins** (Artifactory's server-side extension mechanism) for arbitrary code execution; **Rust-based backdoors** with command-and-control; theft of the cluster join key via `/access/api/v1/system/security/join_key`; SSH keys attached to attacker-created accounts; configuration exfiltration. TechTimes' headline claim that the backdoors "survive patching" is consistent with that list — a Groovy plugin or an extra admin account is not removed by upgrading — but this repo has not verified that article and cites Wiz's list only.

**Patch-rate.** Wiz's exposure telemetry at each disclosure date was 67% / 69% / 67% vulnerable; six weeks later **59%** for CVE-2026-42016, **62%** for CVE-2026-42018 (four weeks), **49%** for CVE-2026-82329 (two weeks). JFrog did not respond to The Register's inquiries about any of the three.

**KEV.** Confirmed directly in CISA's JSON feed: **CVE-2026-42016** ("JFrog Artifactory Incorrect Authorization") and **CVE-2026-42018** ("JFrog Artifactory Improper Authentication") both carry `dateAdded` **2026-09-11**. CVE-2026-82329 was not in the feed as of this sweep.

**Versions.** NVD states CVE-2026-42016 affects Artifactory self-hosted **before 7.133.11**; Wiz lists 7.133.11+ as fixed. For CVE-2026-42018 NVD's record gives no version; Wiz's table lists **7.111.20+** as fixed with an affected range described as "< 7.111.20 through 7.146.8". Artifactory ships several maintained branches, so "7.111.20+" is the floor of the oldest fixed branch, not a statement that 7.140.x is safe — **use the latest patch release of whichever branch you run**, and check JFrog's own advisory for your branch (this sweep did not open it and does not cite a per-branch table for the two newer CVEs).

## Am I affected?

Self-hosted Artifactory only; JFrog's SaaS platform is stated as unaffected for CVE-2026-82329 and is not in Wiz's exposure data.

```bash
# Version
curl -s -u "$USER:$TOKEN" https://artifactory.example.com/artifactory/api/system/version
# Exposure: is the Access API reachable from the internet at all?
curl -s -o /dev/null -w '%{http_code}\n' https://artifactory.example.com/access/api/v1/system/ping
```

**Exploitation indicators (Wiz):**
- CVE-2026-42018: a `401` followed by a `200` on `/access/api/v1/aws/token/` from the same client.
- CVE-2026-42016: low-privilege identities performing admin actions — minting tokens, enumerating users, touching plugins.
- CVE-2026-82329: `POST /access/api/v1/registry/join` returning 200/201, correlated with user/token enumeration or account creation.
- Usernames matching `svc_[a-zA-Z0-9]{8}`, `Nxploited_*`, `labadmin_*`, or JFrog-service-account look-alikes.

```bash
# Quick hunts in the access/request logs
grep -E '/access/api/v1/aws/token/' $ARTIFACTORY_HOME/var/log/access-request.log 2>/dev/null | grep -E ' 200 ' | head
grep -E '/access/api/v1/registry/join' $ARTIFACTORY_HOME/var/log/access-request.log 2>/dev/null | head
# New Groovy plugins you did not deploy
ls -la $ARTIFACTORY_HOME/var/etc/artifactory/plugins/ 2>/dev/null
```

## If you are affected

1. Upgrade every branch you run to its latest patch release. Then **do not stop there**: remove admin accounts you did not create, delete unknown Groovy plugins, rotate the cluster join key, and revoke all access tokens — the observed persistence survives the upgrade.
2. Treat every credential Artifactory held or proxied as exposed: upstream registry tokens (npm, PyPI, Docker Hub), cloud credentials in system configuration, CI service accounts. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), → [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
3. Audit what was published or cached in the registry during the exposure window: an admin can replace artifacts your builds resolve. → [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) if any build pulled from it.
4. Restrict the Access API (`/access/`) to trusted networks; Wiz's first recommendation is network restriction, not just patching.

## Prevention

- → [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — a private registry is the single highest-leverage supply-chain asset you run: it is where "trusted internal mirror" becomes "attacker-controlled upstream" for every developer and every agent that installs through it.
- → [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — verify artifacts by digest/provenance from the source, not by trusting the mirror; pin lockfiles so a swapped artifact fails integrity checks.
- Do not expose Artifactory's Access API to the internet. Three unauthenticated or pre-auth bugs in six weeks, each exploited within days, argue that the API's own authentication is not a boundary you can rely on.

## Sources

- [Wiz — Artifactory Under Attack: In-the-Wild Exploitation of CVE-2026-42016, CVE-2026-42018 & CVE-2026-82329](https://www.wiz.io/blog/artifactory-under-attack-in-the-wild-exploitation-of-cve-2026-42016-cve-2026-4201) — fetched 2026-09-12; primary researcher report, 2026-09-10: chain mechanics, exploitation windows, post-exploitation list, exposure percentages, detection indicators, username patterns.
- [The Register — More JFrog Artifactory bugs under attack, and all 3 have patches](https://www.theregister.com/security/2026/09/11/more-jfrog-artifactory-bugs-under-attack-and-all-3-have-patches/5295943) — fetched 2026-09-12; 2026-09-11: independent coverage, watchTowr's four-day figure for CVE-2026-82329, JFrog's non-response.
- [NVD — CVE-2026-42016](https://nvd.nist.gov/vuln/detail/CVE-2026-42016) and [NVD — CVE-2026-42018](https://nvd.nist.gov/vuln/detail/CVE-2026-42018) — fetched via the NVD API 2026-09-12: CVSS 3.1 8.1 (published 2026-07-27) and 7.5 (published 2026-08-12); "before 7.133.11" for 42016.
- [CISA — Known Exploited Vulnerabilities Catalog (JSON feed)](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) — fetched 2026-09-12; both CVEs `dateAdded` 2026-09-11.
- [advisories/2026-07-huggingface-agentic-intrusion.md](2026-07-huggingface-agentic-intrusion.md) — this repo's existing CVE-2026-82329 tracking (2026-09-02 update: per-branch fixed versions, watchTowr honeypot timeline).
