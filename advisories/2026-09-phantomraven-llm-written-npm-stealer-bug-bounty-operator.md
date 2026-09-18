---
id: 2026-09-phantomraven-llm-written-npm-stealer-bug-bounty-operator
title: "PhantomRaven, revisited — CrowdStrike attributes the 126-package npm stealer (remote dynamic dependencies, slopsquatted names, CI/CD secret theft) to a self-described bug-bounty hunter who likely had an LLM write the malware and uses stolen developer data to find bounty targets rather than selling it"
date_disclosed: 2026-09-18
last_updated: 2026-09-18
severity: medium
status: ongoing
ecosystems: [npm, ci-cd, github-actions, gitlab-ci, jenkins, circleci]
tools_affected: ["npm install in CI runners (GitHub Actions, GitLab CI, Jenkins, CircleCI)", "developers who take package names from AI assistants (slopsquatting)"]
tags: [supply-chain, npm, remote-dynamic-dependency, slopsquatting, typosquatting, credential-theft, ci-cd, llm-generated-malware, attribution]
---

## TL;DR
**PhantomRaven** was the October 2025 Koi Security find: **126 npm packages, ~86,000 installs**, each advertising "zero dependencies" while listing a dependency as an **HTTP URL** on an attacker server — npm fetches the tarball at install time, scanners that only read the registry never see it, and a `preinstall` hook steals npm tokens, GitHub credentials and CI/CD environment variables. Package names were chosen to match what LLMs *hallucinate* when asked for a package (slopsquatting). On 2026-09-18 **CrowdStrike Counter Adversary Operations** published the actor profile: a financially-motivated operator active since November 2022 who **claims to be a bug-bounty hunter** with payouts from at least nine companies via Bugcrowd, Intigriti, YesWeHack, HackenProof and HackerOne; CrowdStrike assesses "with high confidence" that the stealer was **LLM-generated** (verbose per-line comments, placeholder code such as a hardcoded `wss://yourserver.com/socket`, redundant GET-and-POST exfil, statistical token patterns); and none of the stolen data has surfaced in stealer-log shops, suggesting it is used to find "vulnerabilities" to submit as bounties. Two more packages and eight npm handles (`jpd*`, `npmhell`, `jpdhackerone11`…) are attributed. The technique still works against any pipeline that lets `npm install` resolve URL dependencies with lifecycle scripts on.

## What happened

**The 2025 campaign.** Koi Security (Oren Yomtov, 2025-10-30) named PhantomRaven after finding packages that declared a dependency as `"pkg": "http://<attacker-host>/npm/<name>"` instead of a registry reference. npm resolves it, downloads the tarball from the attacker, and runs its `preinstall`. "Security scanners don't fetch them. Dependency analysis tools ignore them." The payload collected email addresses from Git/npm config, CI environment, GitHub tokens and system fingerprints. Names were typosquats *and* slopsquats — "PhantomRaven created those non-existent packages" that Copilot/ChatGPT tend to suggest. The Hacker News (2025-10-30) put the count at 126 packages and 86,000+ installs. This repo's [ongoing slopsquatting entry](ongoing-slopsquatting.md) covers the naming tactic; PhantomRaven itself was not previously written up here.

**What CrowdStrike adds (2026-09-18).**
- **Mechanism, restated:** "The threat actor distributes the malware via typosquatted npm packages that contain minimal, non-malicious code; typically, a simple `Hello, world!` script. However, the packages also specify a dependency via an HTTP URL rather than a standard npm package reference." Two attributed packages: `transform-jsbi-to-bigint` (publisher `jpdhellonpm1`) and `sort-imports-es6-autofix` (publisher `jpd15`); both accounts now inaccessible. Related handles: `jpd12`, `jpd13`, `npmhell`, `npmpackagejpd`, `npmtestdharsh`, `jpdhackerone11`, `packagedharsh`.
- **What it steals, precisely:** CI variables `GITHUB_ACTION`, `GITHUB_ACTIONS`, `GITHUB_ACTOR`, `GITHUB_REPOSITORY`, `GITHUB_RUN_ID`, `GITHUB_WORKFLOW`, `GITLAB_CI`, `CI_PROJECT_ID`, `CI_PROJECT_NAME`, `CI_SERVER_NAME`, `JENKINS_URL`, `JOB_NAME`, `CIRCLE_BUILD_URL`, `CIRCLE_PROJECT_REPONAME`, `CIRCLE_USERNAME`; npm registry config; package name/version; `PATH`; OS, architecture, hostname, IPs, PID, Node version, argv, username, Git/npm email, timestamps. The point is fingerprinting *which* organisation's pipeline installed the package.
- **LLM authorship:** "This assessment is made with high confidence based on statistical token-analysis patterns as well as verbose comments and placeholder code, which indicate the text is highly consistent with a generated LLM token stream." Examples: a comment before every variable ("Function to detect user email from various sources"), a placeholder WebSocket exfil URL left in production, duplicate HTTP GET and POST exfiltration.
- **Actor:** active as a bounty hunter since November 2022; in August 2025 claimed to have found an RCE via a malicious npm package; November 2025 initial contact with a potential victim; a GitHub account identified December 2025; a PyPI upload-failure issue filed under the same identity. CrowdStrike: no stolen data on underground markets, "suggesting sole use for identifying bounty opportunities."
- **Registry response:** npm 12 (June 2026) restricts preinstall scripts, which blunts the *execution* leg; URL dependencies still resolve.

**Why it belongs here.** Three of this repo's standing themes meet in one actor: slopsquatting (names an assistant will suggest), install-time execution outside the registry's view, and CI credential theft — with the new wrinkle that the malware itself was, in CrowdStrike's assessment, vibe-coded. The "bounty hunter" framing does not change the impact: an unauthorised `preinstall` that reads your CI secrets is a compromise whatever the operator intends to do with the results.

**Two-source note.** Koi's 2025 research (via The Hacker News, 2025-10-30) and CrowdStrike's 2026 analysis are independent; SecurityWeek's 2026-09-18 roundup links CrowdStrike's post. Koi's original blog URL now redirects to a Palo Alto Networks product page (Koi was acquired), so the 2025 figures are cited through THN. Download counts are the 2025 figures; CrowdStrike gives none.

## Am I affected?

```bash
# URL-valued dependencies anywhere in the tree — the PhantomRaven signature
grep -rhoE '"[^"]+":\s*"https?://[^"]+"' package.json package-lock.json 2>/dev/null | grep -v '"resolved"' | sort -u
jq -r '.packages | to_entries[] | select(.value.resolved != null and (.value.resolved | startswith("https://registry.npmjs.org/") | not)) | "\(.key) -> \(.value.resolved)"' package-lock.json 2>/dev/null
# Were the attributed packages ever installed?
grep -E 'transform-jsbi-to-bigint|sort-imports-es6-autofix' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
# Did an AI assistant suggest a package you never verified exists?  Check before install:
npm view <name> time --json 2>/dev/null | head -5
```

## If you are affected

- Treat the runner's `GITHUB_TOKEN`, npm token and any secrets exposed as environment variables as stolen: [`playbooks/if-you-installed-a-bad-npm-package.md`](../playbooks/if-you-installed-a-bad-npm-package.md), [`playbooks/if-your-npm-token-leaked.md`](../playbooks/if-your-npm-token-leaked.md), [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md).
- Remove the package and rebuild the lockfile from a clean registry-only resolution.

## Prevention

- `npm config set ignore-scripts true` for CI and dev; upgrade to npm 12; block non-registry `resolved` URLs in lockfile review. [`prevention/npm-hardening.md`](../prevention/npm-hardening.md), [`prevention/ci-cd-hardening.md`](../prevention/ci-cd-hardening.md).
- Verify every package an assistant names before installing it — [`prevention/package-vetting-checklist.md`](../prevention/package-vetting-checklist.md), [`ongoing-slopsquatting.md`](ongoing-slopsquatting.md).

## Sources
- [CrowdStrike — PhantomRaven: LLM-Generated Information Stealer for Bug Bounty Hunting](https://www.crowdstrike.com/en-us/blog/phantomraven-llm-generated-information-stealer-for-bug-bounty-hunting/) — primary for the 2026 attribution; the RDD mechanism quote, the CI variable list, the LLM-authorship assessment, actor timeline, npm handles. Fetched 2026-09-18.
- [The Hacker News — Claimed Bug Bounty Hunter Likely Used LLM to Build PhantomRaven npm Stealer](https://thehackernews.com/2026/09/claimed-bug-bounty-hunter-likely-used.html) — 2026-09-18; independent summary of CrowdStrike's report, the "over 100 packages" figure, Koi/DCODX prior credit. Fetched 2026-09-18.
- [SecurityWeek — In Other News (2026-09-18)](https://www.securityweek.com/in-other-news-ransomware-developer-sentenced-plugin4shell-ai-attack-critical-sap-flaw/) — "LLM-generated information stealer distributed through typosquatted npm packages targeting CI/CD environment variables." Fetched 2026-09-18.
- [The Hacker News — PhantomRaven Malware Found in 126 npm Packages Stealing GitHub Tokens From Devs](https://thehackernews.com/2025/10/phantomraven-malware-found-in-126-npm.html) — 2025-10-30; the original Koi Security figures (126 packages, 86,000+ installs), Oren Yomtov's "scanners don't fetch them" quote, slopsquatting angle. Fetched 2026-09-18.
