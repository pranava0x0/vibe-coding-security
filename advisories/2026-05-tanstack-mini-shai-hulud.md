---
id: 2026-05-tanstack-mini-shai-hulud
title: "Mini Shai-Hulud wave — TanStack, Mistral, UiPath, OpenSearch (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-05-20
severity: critical
status: active
ecosystems: [npm, pypi]
tools_affected: [any-react-project, cursor, claude-code, lovable, bolt, v0, llm-tooling]
tags: [supply-chain, worm, ci-cd, github-actions, oidc, credential-theft, slsa-provenance, teampcp, cve]
---

## TL;DR
Over a 48-hour window on **2026-05-11 → 2026-05-12**, the Mini Shai-Hulud worm — operated by threat actor group **TeamPCP** — compromised **172 unique packages across 403 malicious versions** on npm and PyPI. High-profile scopes hit: **`@tanstack`, `@mistralai`, `@uipath`, `@opensearch-project`**, plus Guardrails AI. Cumulative downloads of affected packages exceed **518 million**. The TanStack subset (~84 versions across 42 `@tanstack/*` packages, including `@tanstack/react-router` ~12.7M weekly downloads) was assigned **CVE-2026-45321 (CVSS 9.6)**. This is the **first documented case of a malicious npm package carrying valid SLSA provenance** — published by the legitimate release pipeline after attacker-controlled code hijacked the runner mid-workflow. Same threat actor is now confirmed to have launched the [PyTorch Lightning compromise](2026-04-pytorch-lightning-compromise.md) on April 30, 2026, and went on to hit the [@antv ecosystem + Microsoft `durabletask` on May 19](2026-05-mini-shai-hulud-may19-wave.md) and to breach [GitHub's own internal repos on May 20](2026-05-teampcp-github-breach.md).

> **Campaign context (updated 2026-05-20):** TeamPCP (aka PCPcat / DeadCatx3 / UNC6780) has been the most active supply-chain actor of 2026. The Mini Shai-Hulud campaign began in early March with **Aqua's Trivy** scanner, then cascaded through **Checkmarx KICS**, **LiteLLM**, **Telnyx**, the [SAP scope](2026-04-mini-shai-hulud-sap.md) (April), [PyTorch Lightning](2026-04-pytorch-lightning-compromise.md) (Apr 30), this TanStack/Mistral/UiPath/OpenSearch wave (May 11), [node-ipc](2026-05-node-ipc-compromise.md) (May 14), and the [@antv + durabletask wave](2026-05-mini-shai-hulud-may19-wave.md) (May 19). **Campaign total to date: ~1,055 malicious versions across ~502 unique packages** (npm 1,048, PyPI 6, Composer 1).

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
| CVE (TanStack subset) | `CVE-2026-45321` (CVSS 9.6) |
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
