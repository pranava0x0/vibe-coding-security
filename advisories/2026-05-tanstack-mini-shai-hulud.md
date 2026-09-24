---
id: 2026-05-tanstack-mini-shai-hulud
title: "Mini Shai-Hulud wave — TanStack, Mistral, UiPath, OpenSearch (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-09-24
severity: critical
status: active
ecosystems: [npm, pypi]
tools_affected: [any-react-project, cursor, claude-code, lovable, bolt, v0, llm-tooling]
tags: [supply-chain, worm, ci-cd, github-actions, oidc, credential-theft, slsa-provenance, teampcp, cve, cisa-kev]
---

## TL;DR
Over a 48-hour window on **2026-05-11 → 2026-05-12**, the Mini Shai-Hulud worm — operated by threat actor group **TeamPCP** — compromised **172 unique packages across 403 malicious versions** on npm and PyPI. High-profile scopes hit: **`@tanstack`, `@mistralai`, `@uipath`, `@opensearch-project`**, plus Guardrails AI. Cumulative downloads of affected packages exceed **518 million**. The TanStack subset (~84 versions across 42 `@tanstack/*` packages, including `@tanstack/react-router` ~12.7M weekly downloads) was assigned **CVE-2026-45321 (CVSS 9.6)**. This is the **first documented case of a malicious npm package carrying valid SLSA provenance** — published by the legitimate release pipeline after attacker-controlled code hijacked the runner mid-workflow. Same threat actor is now confirmed to have launched the [PyTorch Lightning compromise](2026-04-pytorch-lightning-compromise.md) on April 30, 2026, and went on to hit the [@antv ecosystem + Microsoft `durabletask` on May 19](2026-05-mini-shai-hulud-may19-wave.md) and to breach [GitHub's own internal repos on May 20](2026-05-teampcp-github-breach.md).

> **Update 2026-06-11 — ACTION REQUIRED BY 2026-06-12:** OpenAI's **macOS code-signing certificate revocation takes effect tomorrow**. macOS users of **ChatGPT Desktop, Codex, Codex-cli, and Atlas** who have not yet updated will be **blocked from launching the apps** after the certificate is revoked. Update immediately. The Hades Campaign (June 8) is the latest downstream wave of the same threat-actor cluster; see the 2026-05-31 update below for full cert-rotation context.

> **Update 2026-06-02:** the campaign has a third documented worm-source-public copycat. **[Miasma — `@redhat-cloud-services` (2026-06-01)](2026-06-miasma-redhat-cloud-services-compromise.md)** is a lightly reskinned Mini Shai-Hulud derivative (Greek-mythology theming replaces Dune markers; added GCP/Azure identity collectors; exfil camouflaged as `api.anthropic.com/v1/api`) that hit **32 packages / 96 versions** of Red Hat's official OpenShift / Hybrid Cloud Console / Insights client scope in a ~72-second automated burst. Initial access was a compromised Red Hat employee GitHub account → existing GitHub Actions OIDC publish path (no separate npm credential theft) — same shape as [Megalodon's `@tiledesk` arm](2026-05-megalodon-github-actions-mass-campaign.md). This is the **first copycat to land on a major legitimate npm scope** rather than typosquats, and the first to disguise exfil as AI-vendor API traffic.
>
> **Update 2026-05-31:** **CISA added CVE-2026-45321 to the Known Exploited Vulnerabilities catalog on 2026-05-27** alongside [CVE-2026-48027 (Nx Console)](2026-05-nx-console-vscode-compromise.md) and CVE-2026-8398 (DAEMON Tools Lite) — **federal-agency remediation deadline 2026-06-10**. **OpenAI** disclosed on **2026-05-14** that this wave reached **two OpenAI employee devices**, exfiltrated **"limited credential material" from internal source-code repos**, and forced **re-signing of the macOS, Windows, iOS, and Android desktop apps** (ChatGPT Desktop, Codex, Codex-cli, Atlas). **Old certificates are revoked on 2026-06-12** — unupdated macOS users will be blocked from launching the apps. OpenAI's own postmortem notes the compromised devices had not yet received post-[Axios](2026-03-axios-compromise.md) supply-chain hardening (pinned commit hashes + `minimumReleaseAge` floor) that would have blocked the malicious dependency. Two AI-vendor code-signing-cert rotations in five weeks (Axios → 2026-05-08, TanStack → 2026-06-12) — track this as a recurring named-instance pattern.
>
> **Campaign context (updated 2026-05-23):** TeamPCP (aka PCPcat / DeadCatx3 / UNC6780, per Google Threat Intelligence) has been the most active supply-chain actor of 2026. The Mini Shai-Hulud campaign began in early March with **Aqua's Trivy** scanner, then cascaded through **Checkmarx KICS**, **LiteLLM**, **Telnyx**, the **["Shai-Hulud: The Third Coming" Checkmarx-channel wave](2026-04-bitwarden-cli-shai-hulud-third-coming.md)** that backdoored **`@bitwarden/cli`** (Apr 22 — the first payload to specifically hunt **AI-coding-tool credentials**), the [SAP scope](2026-04-mini-shai-hulud-sap.md) (April), [PyTorch Lightning](2026-04-pytorch-lightning-compromise.md) (Apr 30), this TanStack/Mistral/UiPath/OpenSearch wave (May 11), [node-ipc](2026-05-node-ipc-compromise.md) (May 14), the [@antv + durabletask wave](2026-05-mini-shai-hulud-may19-wave.md) (May 19), and a **Checkmarx Jenkins AST Plugin** backdoor (May). **Campaign total to date: ~1,055 malicious versions across ~502 unique packages** (npm 1,048, PyPI 6, Composer 1). Separately, the same *"hijack the real release pipeline via GitHub Actions"* TTP showed up in the [elementary-data PyPI/GHCR compromise](2026-04-elementary-data-pypi-ghcr-compromise.md) (Apr 24) — script injection → forged signed release → legitimate publish pipeline.

## What happened
The worm chained three vulnerabilities in GitHub Actions:

1. **`pull_request_target` Pwn Request.** A fork-triggered workflow on the TanStack monorepo (and analogous workflows on the other affected scopes) ran attacker-controlled code with elevated privileges.
2. **GitHub Actions cache poisoning.** The malicious workflow wrote a poisoned pnpm store into the Actions cache.
3. **OIDC token theft.** When a legitimate maintainer's PR was merged, the trusted release workflow restored the poisoned cache; attacker-controlled binaries then **extracted OIDC tokens directly from the runner's process memory**.

Result: packages were published by the **legitimate release pipeline, with valid SLSA provenance**, while carrying a credential-stealing payload.

The payload follows the Mini Shai-Hulud playbook: scan the runner for npm/GitHub/cloud credentials, exfiltrate to attacker-controlled GitHub repos with Dune-themed names (e.g., `kralizec-phibian-314`, descriptions like *"A Mini Shai-Hulud has Appeared"*), then attempt to publish trojanized versions of every package the harvested tokens can reach.

## Am I affected?

```bash
# All four major affected scopes
npm ls --all 2>/dev/null | grep -E '@tanstack/|@mistralai/|@uipath/|@opensearch-project/'

# Plus PyPI side (mistralai is on both)
pip list 2>/dev/null | grep -iE 'mistralai|guardrails|opensearch'

# Install dates within the window
ls -la node_modules/@tanstack/*/package.json 2>/dev/null | head
```

If any affected package landed on a dev machine or CI runner between 2026-05-11 and the takedown, treat that host as compromised — credentials, OIDC tokens in CI cache, and downstream publish authority all suspect.

```bash
# Look for Dune-themed exfil repos planted in your accounts/orgs
gh api /user/repos --paginate --jq '.[] | select(.description // "" | test("Shai-Hulud|Mini Shai-Hulud"; "i")) | .full_name'
gh api /user/repos --paginate --jq '.[] | select(.created_at > "2026-05-10") | {name, private, description}'
```

### IOCs

| Type | Value |
|---|---|
| CVE (TanStack subset) | `CVE-2026-45321` (CVSS 9.6) — **CISA KEV 2026-05-27**, federal deadline **2026-06-10** |
| Downstream AI-vendor impact | **OpenAI**: 2 employee devices compromised, internal source-code credential exfil; macOS/Windows/iOS/Android signing certs rotated; old certs revoked **2026-06-12** |
| Worm commit-message prefix | `EveryBoiWeBuildIsAWormyBoi` |
| Exfil repo description | `"A Mini Shai-Hulud has Appeared"` / `"Shai-Hulud: Here We Go Again"` |
| C2 / staging hosts | `git-tanstack[.]com`, `*.getsession.org`, `filev2.getsession.org`, `api.masscan.cloud` |
| C2 IP | `83.142.209[.]194` |
| Postinstall artifact (cross-ecosystem) | `.claude/settings.json`, `.claude/setup.mjs`, `.claude/router_runtime.js`, `.vscode/tasks.json` (`runOn: folderOpen`) |
| Total packages compromised | 172 (npm + PyPI), 403 malicious versions |
| Exfil repos created | 400+ |

Block `git-tanstack[.]com`, `*.getsession.org`, and `83.142.209[.]194` at the DNS/proxy level. Audit outbound flows for connections to `filev2.getsession.org` and `api.masscan.cloud`.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — especially for CI runners
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Why valid SLSA provenance matters here
SLSA provenance is meant to prove "this artifact was built by this pipeline from this source." It worked exactly as designed — the pipeline really did publish the package. The problem is that the *pipeline itself* was compromised mid-build. Provenance attestation can't tell you whether a build runner's process memory was being scraped.

**Lesson:** provenance is a *necessary but insufficient* signal. Combine with: signed source commits, restricted PR-triggered workflows (don't grant `pull_request_target` write access), short-lived OIDC, and runtime hardening (StepSecurity Harden-Runner egress allowlist).

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Restrict `pull_request_target` workflows. Use [`zizmor`](https://github.com/woodruffw/zizmor) to scan workflows for the Pwn Request pattern. Add [StepSecurity Harden-Runner](https://github.com/step-security/harden-runner) for runtime egress alerting.

**Status update 2026-09-10:** re-triaged from `active` to `historical`. The incident window closed in May 2026; no new malicious versions, IOCs, or vendor updates have been reported since this advisory was last touched (2026-06-11). The *technique* is not retired — successor waves are tracked as live entries in ALERTS.md — but this specific compromise is over, and "active" here should mean "still propagating," not "was bad once."

## Update 2026-09-19 — four months later, a victim files the blast radius: CrowdSec says a TanStack-infected laptop's GitHub OAuth token was used to clone ~170 private repositories, and the archive surfaced on a forum on 2026-09-16

CrowdSec (the French open-source IDS/IPS vendor) published its incident analysis on **2026-09-18**, and The Hacker News covered it on 09-19. The chain, per CrowdSec: a **former employee's laptop was infected by the May 11 TanStack packages** ("The ex-employee got compromised by the TanStack supply chain attack, matching the methodology" — the CEO); the stealer took, among other things, a **GitHub OAuth token** (`gho_…` format); on **2026-05-22, 05:52–06:01 UTC**, that token was used from Toronto to clone **~170 private repositories** (130+ public and private repos in total over May 22–23); the employee's GitHub access was revoked on **2026-05-25**, three days after the clones. Nothing else happened for months — then on **2026-08-17** the attacker tested the one usable credential in the loot, an AWS token restricted to SNS publishing (`assertible-zapier-sns-sender`), and failed; on **2026-09-16** the archive appeared on a forum, and CrowdSec rotated credentials on 09-16/17 and published on 09-18.

What leaked: source for the Console, data-science scripts, automation and the consensus algorithm; **83 user email addresses** (under 0.05% of ~150K users); and the names, emails and investment context of **51 prospective investors from 2020**. CrowdSec says its infrastructure and databases were not accessed, no code was changed, and no customer data was taken. Its changes: **EDR on developer laptops** (Aikido), expanded GitHub logging, a sub-24-hour IR target, tighter on/offboarding. Its own framing of the gap: universal 2FA, hardware keys, token scoping and audit logging were all in place — and a stolen OAuth token walks past every one of them, because "the developer machine" was the one asset without endpoint coverage.

Why it belongs in this file: **the stealer's take from May is still being cashed in September.** A package compromise's downstream victims disclose months after the wave, from their own blogs, and the token that mattered was a GitHub OAuth grant — the same class the [Mandiant SaaS case](2026-09-mandiant-hijacked-coding-assistant-session-shai-hulud-saas.md) and the [OpenAI TanStack response](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/) turn on. If a machine of yours ran a poisoned TanStack version in May and you rotated npm/SSH/cloud keys but not **GitHub OAuth app grants and personal tokens**, do that now (`Settings → Applications → Authorized OAuth Apps`; [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)), and check your org's audit log for clones from unfamiliar locations in the week after 2026-05-11.

## Update 2026-09-21 — CrowdSec's formal statement: ~300 repositories in the archive (130+ of them already public), the private ones being the SaaS Console, AWS Cloud routines, connectors and automations; the vector described as a TanStack component "backdoored to extract an API key with authorization to read the private codebase"

CrowdSec published a shorter [official statement](https://www.crowdsec.net/blog/crowdsec-statement-source-code-exposure) on **2026-09-17**, a day before the analysis above, and SecurityWeek covered it on 09-21. The statement's numbers: **approximately 300 repositories** in the leaked archive, of which **130+ are public open-source repos** — the private remainder is source for the SaaS Console, AWS Cloud routines, connectors and automations. On the vector it says a TanStack component "was used in our organization in May and appears to have been backdoored to extract an API key with authorization to read the private codebase"; the 09-18 analysis identifies that credential as a GitHub OAuth token (`gho_…`). The two descriptions are the same credential seen from different distances — a "key with authorization to read the private codebase" is what a stolen OAuth grant with repo scope *is* — but readers comparing the two posts should not conclude there were two credentials. CrowdSec was informed on **09-16**, verified the report, "immediately rotated all required tokens and credentials," and repeats that no customer data, credentials or PII were involved and that the code "has evolved significantly over those four months." SecurityWeek adds nothing beyond the statement but is the first mainstream write-up of the confirmation.

## Update 2026-09-24 — still propagating: SafeDep finds six repositories newly infected between 2026-09-20 and 09-24 through two GitHub Actions whose **tags were moved to a malicious commit in May and never moved back**

SafeDep (2026-09-24) reports that the May wave is **not over on GitHub**: six repositories with 139 to 6,254 stars were infected between **2026-09-20 and 09-24** — "GitHub code search produced this list, so it can miss other repositories." The vector is the one this campaign planted on **2026-05-18 (19:10–19:31 UTC)**: the attacker "moved all 53 tags of `actions-cool/issues-helper`" (and 15 tags of `actions-cool/maintain-one-comment`) to a malicious commit, and "four months later, the tags still point to the malicious commit." Any workflow that references those actions by tag — `@v2.1.1`, `@v3` — runs the payload every time it fires, and five of the six new infections came from **scheduled or event-driven issue-management workflows** ("Close Inactive Issue," "Release," "Issue Open Check," "Issue Inactive") that run daily with no human involved, so reinfection needs no attacker action at all. Once running, "the payload reads the `ghs_` token from `Runner.Worker` memory" and uses it to commit files that appear "as verified, by `github-actions[bot]`": `.claude/settings.json` (a hook), `.claude/index.js` (the payload), `.claude/setup.mjs` (a Bun downloader) and `.vscode/tasks.json` — the same coding-agent-config persistence this file and the [Miasma wave](2026-06-miasma-leoplatform-go-wave.md) documented in May and June — so the next developer who opens the repo in an AI-enabled editor executes it on their own machine, where it can install the `kitty-monitor` backdoor, a `gh-token-monitor` script and a wiper armed on a deprecation check. SafeDep's IOCs: payload blob `2931c1be43b0d04174636ddbff54963aec92bdeb` (500,143 bytes); exfiltration to `t.m-kosche[.]com/api/public/otel/v1/traces` (OpenTelemetry-shaped, so it passes as telemetry); commit markers **`firedalazer`** and **`thebeautifulmarchoftime`**. **Status returns to `active`**: the campaign's own infrastructure is dormant, but a hijacked action tag is a self-running re-infection mechanism and it is firing this week.

**Do now:** `grep -rn "actions-cool/" .github/workflows/` — any hit by tag is an infection path; pin to a commit SHA you have inspected or remove the action. Search every repository for the two commit markers and for `.claude/settings.json` / `.claude/setup.mjs` / `.vscode/tasks.json` commits authored by `github-actions[bot]` that no workflow of yours writes. Rotate CI tokens for any repository whose workflows ran those actions since 2026-05-18, and treat developer machines that opened an infected checkout in an AI editor as compromised ([if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)). Pinning actions to SHAs ([prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)) is the control that would have stopped every one of the six.

## Sources
- [TanStack — Postmortem: TanStack npm supply-chain compromise](https://tanstack.com/blog/npm-supply-chain-compromise-postmortem)
- [StepSecurity — TeamPCP's Mini Shai-Hulud Is Back: A Self-Spreading Supply Chain Attack Compromises TanStack npm Packages](https://www.stepsecurity.io/blog/mini-shai-hulud-is-back-a-self-spreading-supply-chain-attack-hits-the-npm-ecosystem)
- [Akamai — Mini Shai-Hulud: The Worm Returns and Goes Public](https://www.akamai.com/blog/security-research/mini-shai-hulud-worm-returns-goes-public)
- [Phoenix Security — Mini Shai-Hulud: TeamPCP's Self-Propagating npm Worm Hits TanStack, OpenSearch, and Mistral AI Across 170 Packages](https://phoenix.security/mini-shai-hulud-teampcp-tanstack/)
- [Orca Security — TanStack and 160+ npm/PyPI Packages Compromised in Supply Chain Worm Attack](https://orca.security/resources/blog/tanstack-npm-supply-chain-worm/)
- [Strobes — TanStack npm Supply Chain Attack: 170 Packages Compromised](https://strobes.co/blog/tanstack-npm-supply-chain-attack/)
- [SafeDep — Mass Supply Chain Attack Hits TanStack, Mistral AI npm and PyPI Packages](https://safedep.io/mass-npm-supply-chain-attack-tanstack-mistral/)
- [Aikido — Mini Shai-Hulud Is Back: npm Worm Hits over 160 Packages, including Mistral and Tanstack](https://www.aikido.dev/blog/mini-shai-hulud-is-back-tanstack-compromised)
- [Snyk — TanStack npm Packages Hit by Mini Shai-Hulud](https://snyk.io/blog/tanstack-npm-packages-compromised/)
- [Snyk — Zero-Day Advisory: TanStack npm Supply Chain Compromise May 2026](https://security.snyk.io/TanStack-npm-Supply-Chain-Compromise-May-2026)
- [Wiz — Mini Shai-Hulud Strikes Again: TanStack + more npm Packages Compromised](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
- [Mend — Mini Shai-Hulud Wave Hits 172 npm and PyPI Packages](https://www.mend.io/blog/mini-shai-hulud-is-back-172-npm-and-pypi-packages-compromised-in-latest-wave/)
- [The Hacker News — Mini Shai-Hulud Worm Compromises TanStack, Mistral AI, Guardrails AI & More Packages](https://thehackernews.com/2026/05/mini-shai-hulud-worm-compromises.html)
- [Picus Security — Mini Shai-Hulud: The npm Supply Chain Worm Explained](https://www.picussecurity.com/resource/blog/mini-shai-hulud-the-npm-supply-chain-worm-explained)
- [Expel — Mini Shai-Hulud: Cross-ecosystem supply chain worm targeting npm & PyPI](https://expel.com/blog/mini-shai-hulud-cross-ecosystem-supply-chain-worm-targeting-npm-pypi/)
- [The CyberSec Guru — Mini Shai-Hulud npm Attack: All Affected Packages](https://thecybersecguru.com/news/mini-shai-hulud-npm-worm-affected-packages-list/)
- [Qualysec — Mini Shai-Hulud Worm: 170+ npm & PyPI Packages Compromised](https://qualysec.com/cybersecurity-news/mini-shai-hulud-worm-compromises/)
- [Cybersecurity News — MistralAI PyPI Package Compromised](https://cybersecuritynews.com/mistralai-pypi-package-compromised/amp/)
- [OpenAI — Our response to the TanStack npm supply chain attack](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/) — official vendor IR: 2 employee devices, signing certs rotated, June 12 revocation
- [The Register — OpenAI caught in TanStack npm supply chain chaos after employee devices compromised (2026-05-15)](https://www.theregister.com/security/2026/05/15/openai-caught-in-tanstack-npm-supply-chain-chaos-after-employee-devices-compromised/5241019)
- [The Hacker News — TanStack Supply Chain Attack Hits Two OpenAI Employee Devices, Forces macOS Updates](https://thehackernews.com/2026/05/tanstack-supply-chain-attack-hits-two.html)
- [SecurityWeek — OpenAI Hit by TanStack Supply Chain Attack](https://www.securityweek.com/openai-hit-by-tanstack-supply-chain-attack/)
- [TechCrunch — OpenAI says hackers stole some data after latest code security issue](https://techcrunch.com/2026/05/14/openai-says-hackers-stole-some-data-after-latest-code-security-issue/)
- [CISA — Three Known Exploited Vulnerabilities Added to Catalog (2026-05-27)](https://www.cisa.gov/news-events/alerts/2026/05/27/cisa-adds-three-known-exploited-vulnerabilities-catalog) — CVE-2026-45321 KEV addition
- [SecurityAffairs — U.S. CISA adds Daemon Tools, TanStack, and Nx Console flaws to its KEV catalog](https://securityaffairs.com/192776/security/u-s-cisa-adds-daemon-tools-tanstack-and-nx-console-flaws-to-its-known-exploited-vulnerabilities-catalog.html)
- [CrowdSec — TanStack supply-chain attack analysis: how ~170 private repos were exposed](https://www.crowdsec.net/blog/tanstack-supply-chain-attack-analysis) — victim's own post-mortem, published 2026-09-18: the May 22 05:52–06:01 UTC clone window, the `gho_` OAuth token, the 05-25 revocation, the 08-17 SNS-token test, the 09-16 forum leak, the 83-user / 51-investor figures, EDR remediation. Fetched 2026-09-20.
- [The Hacker News — CrowdSec Says TanStack npm Attack Led to Copy of 170 Private GitHub Repositories](https://thehackernews.com/2026/09/crowdsec-says-tanstack-npm-attack-led.html) — 2026-09-19; independent write-up of the CrowdSec disclosure with the CVE-2026-45321 linkage and the "only usable credential… AWS SNS" detail. Fetched 2026-09-20.
- [CrowdSec — Statement on source code exposure](https://www.crowdsec.net/blog/crowdsec-statement-source-code-exposure) — 2026-09-17; the ~300-repository figure (130+ public), what the private code covers, the "backdoored to extract an API key" description of the vector, the 09-16 notification and rotation, the no-customer-data statement. Fetched 2026-09-21.
- [SecurityWeek — CrowdSec Confirms Source Code Stolen in Supply Chain Attack](https://www.securityweek.com/crowdsec-confirms-source-code-stolen-in-supply-chain-attack/) — 2026-09-21; mainstream confirmation citing the statement; the TeamPCP / 84-artifact / 42-package linkage. Fetched 2026-09-21.
- [VentureBeat — Four AI supply-chain attacks in 50 days exposed the release pipeline red teams aren't covering](https://venturebeat.com/security/supply-chain-incidents-openai-anthropic-meta-release-surface-vendor-questionnaire-matrix)
- **2026-09-24 update sources** — [SafeDep — Mini Shai-Hulud Is Still Infecting GitHub Repositories](https://safedep.io/mini-shai-hulud-reinfection-github-repositories/) (2026-09-24: the six new infections and their star counts, the 2026-05-18 tag moves on `actions-cool/issues-helper` and `maintain-one-comment`, the scheduled-workflow triggers, the `ghs_` token read from `Runner.Worker`, the five committed files, the `t.m-kosche[.]com` OTel-path exfil host, the wiper trigger, the commit markers, the remediation). Fetched 2026-09-24.
