---
id: 2026-04-github-git-push-injection-rce
title: "GitHub.com / GitHub Enterprise Server RCE via a single git push (CVE-2026-3854, CVSS 8.7, patched)"
date_disclosed: 2026-04-01
last_updated: 2026-04-01
severity: critical
status: patched
ecosystems: [github]
tools_affected: [github.com, github-enterprise-server]
tags: [git, rce, header-injection, shared-infrastructure, backfill]
---

## TL;DR
Wiz found that GitHub's internal `git push` handling embedded unsanitized push-option values into an internal service header using a delimiter character an attacker could also supply — letting anyone with push access to any repository inject additional header fields, override security-critical configuration, and run arbitrary commands as the git service user. On GitHub.com this reached **shared storage infrastructure serving millions of other users' and organizations' public and private repositories**. GitHub.com was patched within 2 hours of the report; GitHub Enterprise Server needed a version upgrade. A genuine gap in this repo's coverage — found only during a routine GitHub Advisory Database sweep four months after disclosure.

## What happened
During a `git push`, GitHub's backend passes user-supplied push-option values into an internal `X-Stat` service header used between backend components. The header format used a delimiter character that could also legally appear inside a push-option value — so an attacker who included that delimiter in a crafted push option could inject **additional metadata fields** into the header that the receiving service had not expected ([Wiz](https://www.wiz.io/blog/github-rce-vulnerability-cve-2026-3854); [Orca Security](https://orca.security/resources/blog/github-enterprise-server-rce-cve-2026-3854-injection/)). Those injected fields could override security-critical configuration and bypass sandboxing on the backend component processing the push, resulting in **command injection and arbitrary code execution as the git service user** — triggerable with nothing more than push access to any one repository.

On GitHub.com, exploitation reached **shared storage nodes** that host repository data for many unrelated users and organizations simultaneously — meaning a single attacker with push access to their own repository could potentially pivot to code execution on infrastructure also serving other customers' public and private repos. Wiz reported the issue to GitHub on **2026-03-04**; GitHub validated it and deployed a fix to GitHub.com within **2 hours** of the report. GitHub Enterprise Server required a version upgrade, fixed in **3.14.25, 3.15.20, 3.16.16, 3.17.13, 3.18.8, 3.19.4, and 3.20.0** and later. **CVE-2026-3854**, CVSS **8.7**.

No public evidence of pre-disclosure in-the-wild exploitation has been reported. This advisory is a backfill — the vulnerability and fix are both several months old — added after a routine GitHub Advisory Database sweep surfaced it as a gap in this repo's coverage of GitHub-platform-level (not just GitHub Actions or Codespaces) infrastructure risk.

## Am I affected?
This was a GitHub-side infrastructure vulnerability, not something detectable from your own repo or dependency tree.

- **GitHub.com users:** no action needed — GitHub patched the shared platform within hours of the report; the exposure window (2026-03-04 report → fix) predates this advisory.
- **GitHub Enterprise Server operators:** check your running version against the fixed releases above.
```bash
# On a GHES instance, check the installed version
ghe-version
# Compare against fixed releases: 3.14.25, 3.15.20, 3.16.16, 3.17.13, 3.18.8, 3.19.4, 3.20.0+
```
If your GHES instance predates the relevant fixed release for its minor version line, it was vulnerable until upgraded.

## If you are affected
GitHub Enterprise Server operators still running an unpatched minor version line should upgrade immediately to the fixed release for that line (see versions above). No credential rotation is indicated by the public disclosure — GitHub has not reported evidence that this was exploited before the fix — but if you have reason to believe your GHES instance was exploited during the exposure window, treat it per standard infrastructure-compromise response.

→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)
- Keep self-hosted GitHub Enterprise Server on a current, supported minor version line — this class of internal-header-injection bug is exactly what a several-months-stale on-prem instance misses while GitHub.com gets patched in hours.
- This is a reminder that "GitHub" as a trust anchor spans more than the Actions pipeline and the Advisory Database this repo already tracks closely — the core git-push handling path on shared infrastructure is itself an attack surface with a blast radius spanning unrelated tenants.

## Sources
- [Wiz — GitHub RCE Vulnerability: CVE-2026-3854 Breakdown](https://www.wiz.io/blog/github-rce-vulnerability-cve-2026-3854) — primary technical writeup: root cause (unsanitized push-option values in internal `X-Stat` header), discovery/report/patch timeline, shared-storage-node impact on GitHub.com.
- [Orca Security — Remote Code Execution in GitHub Enterprise Server via Git Push Injection (CVE-2026-3854)](https://orca.security/resources/blog/github-enterprise-server-rce-cve-2026-3854-injection/) — independent corroboration, GitHub Enterprise Server fixed-version list, CVSS score.
- [The Hacker News — Researchers Discover Critical GitHub CVE-2026-3854 RCE Flaw Exploitable via Single Git Push](https://thehackernews.com/2026/04/researchers-discover-critical-github.html) — independent corroboration and disclosure-timeline summary.
