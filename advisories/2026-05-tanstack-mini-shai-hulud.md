---
id: 2026-05-tanstack-mini-shai-hulud
title: "Mini Shai-Hulud wave — TanStack, Mistral, UiPath, OpenSearch (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-05-17
severity: critical
status: active
ecosystems: [npm, pypi]
tools_affected: [any-react-project, cursor, claude-code, lovable, bolt, v0, llm-tooling]
tags: [supply-chain, worm, ci-cd, github-actions, oidc, credential-theft, slsa-provenance, teampcp]
---

## TL;DR
Over a 48-hour window on **2026-05-11 → 2026-05-12**, the Mini Shai-Hulud worm — operated by threat actor group **TeamPCP** — compromised **172 unique packages across 403 malicious versions** on npm and PyPI. High-profile scopes hit: **`@tanstack`, `@mistralai`, `@uipath`, `@opensearch-project`**, plus Guardrails AI. The TanStack subset included `@tanstack/react-router` (~12.7M weekly downloads). This is the **first documented case of a malicious npm package carrying valid SLSA provenance** — published by the legitimate release pipeline after attacker-controlled code hijacked the runner mid-workflow.

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
