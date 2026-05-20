---
id: 2026-05-mini-shai-hulud-may19-wave
title: "Mini Shai-Hulud May 19 wave — @antv npm + Microsoft durabletask PyPI (May 2026)"
date_disclosed: 2026-05-19
last_updated: 2026-05-20
severity: critical
status: active
ecosystems: [npm, pypi]
tools_affected: [any-react-project, any-node-project, azure-durable-functions, cursor, claude-code, lovable, bolt, v0, llm-tooling, ci-cd]
tags: [supply-chain, worm, ci-cd, credential-theft, sigstore-provenance, teampcp, docker-escape, multi-cloud]
---

## TL;DR
On **2026-05-19**, threat actor **TeamPCP** (aka PCPcat / DeadCatx3 / UNC6780) ran two more arms of the Mini Shai-Hulud worm in the same window: a compromised npm maintainer account pushed **~637 malicious versions across ~317 npm packages** — the entire **`@antv`** data-viz ecosystem plus `echarts-for-react` (~1.1M weekly downloads), `timeago.js`, `size-sensor`, `canvas-nest.js` — in a ~22-minute automated burst, and three trojanized versions of **Microsoft's official `durabletask` PyPI SDK** (1.4.1/1.4.2/1.4.3) were published directly to PyPI. The payload steals 20+ credential classes (AWS/GCP/Azure/GitHub/npm/SSH/Kubernetes/Vault/Stripe/DB strings), attempts **Docker host-socket container escape**, plants VS Code + Claude Code backdoors, and self-propagates. New escalation: the worm now mints **cryptographically valid Sigstore provenance attestations** (ephemeral EC keypair + OIDC) so packages show a green "verified provenance" badge. This is the same campaign as the [May 11 TanStack wave](2026-05-tanstack-mini-shai-hulud.md) and the [GitHub internal breach disclosed May 20](2026-05-teampcp-github-breach.md).

## What happened

### npm — the @antv ecosystem (01:56–02:56 UTC, 2026-05-19)
A compromised npm maintainer account (`atool`) was used to publish **~637 malicious versions across ~317 packages** in a fully automated ~22-minute burst (Socket counted 639 affected package names). Affected packages include the whole Alibaba **`@antv`** scope (`@antv/g2`, `@antv/g6`, `@antv/x6`, `@antv/l7`, `@antv/s2`, `@antv/f2`, `@antv/g`, `@antv/g2plot`, `@antv/graphin`, `@antv/data-set`, `@antv/scale`) plus standalone packages: **`echarts-for-react`** (~1.1M weekly / ~3.8M monthly downloads), **`timeago.js`** (~1.15M), **`size-sensor`** (~4.2M monthly), and `canvas-nest.js`.

The injected payload is a **498 KB obfuscated Bun script** matching the Mini Shai-Hulud toolkit used in the [SAP compromise](2026-04-mini-shai-hulud-sap.md) three weeks earlier — same scanner architecture, same credential regex set, same obfuscation. It harvests **20+ credential types** (AWS, GCP, Azure, GitHub, npm, SSH, Kubernetes, Vault, Stripe, database connection strings), attempts a **Docker container escape via the host socket**, plants backdoors in VS Code and Claude Code config, then reuses stolen npm tokens to enumerate, inject, version-bump, and republish across every package the tokens can reach.

Socket's detection flagged most activity within **6–12 minutes** (median 6.7 min) of publication.

### PyPI — Microsoft `durabletask` (2026-05-19)
Three malicious versions (**1.4.1, 1.4.2, 1.4.3**) of Microsoft's official **`durabletask`** Python SDK — the client for Azure Durable Functions, ~400K downloads/month — were uploaded to PyPI within a ~35-minute window and later quarantined. The attacker did **not** breach PyPI: a compromised GitHub account already involved in earlier TeamPCP attacks had access to the `microsoft/durabletask-python` repo, cloned recent commit messages, and extracted a **PyPI token stored in GitHub Actions secrets**, then published directly. The 28 KB payload steals AWS/Azure/GCP/Kubernetes/password-manager creds + 90+ dev-tool configs, spreads laterally, and **skips systems with a Russian locale** (a hallmark of Eastern-European cybercrime). C2: `check.git-service.com`, `t.m-kosche.com`.

### Campaign rollup
Across the full Mini Shai-Hulud campaign tracked to date, researchers count **1,055 compromised versions across 502 unique packages** — npm (1,048), PyPI (6), Composer (1). The campaign began in early March (Aqua's **Trivy** scanner), then cascaded through **Checkmarx KICS**, **LiteLLM**, **Telnyx**, the [SAP scope](2026-04-mini-shai-hulud-sap.md) (April), [PyTorch Lightning + intercom-client](2026-04-pytorch-lightning-compromise.md) (Apr 30), [TanStack / Mistral / UiPath / OpenSearch](2026-05-tanstack-mini-shai-hulud.md) (May 11), [node-ipc](2026-05-node-ipc-compromise.md) (May 14), and now @antv + durabletask (May 19).

## Am I affected?

```bash
# npm side — @antv ecosystem + standalone packages
npm ls --all 2>/dev/null | grep -E '@antv/|echarts-for-react|timeago\.js|size-sensor|canvas-nest'

# Did any land in your lockfile after 2026-05-18?
grep -E '@antv/|echarts-for-react|timeago|size-sensor' package-lock.json 2>/dev/null

# PyPI side — Microsoft durabletask
pip show durabletask 2>/dev/null | grep -E '^(Name|Version):'
# Versions 1.4.1 / 1.4.2 / 1.4.3 are malicious. Pin to 1.4.0.
```

If any of these landed on a dev machine or CI runner on/after 2026-05-19, treat the host as compromised — cloud creds, GitHub/npm tokens, SSH keys, and any secret reachable from the Docker socket are all suspect.

```bash
# Worm artifacts to look for
ls -la .vscode/tasks.json 2>/dev/null          # check for runOn: folderOpen backdoor
ls -la .claude/settings.json .claude/setup.mjs 2>/dev/null
# Block C2 at DNS/proxy:
#   check.git-service.com, t.m-kosche.com
```

### IOCs

| Type | Value |
|---|---|
| Threat actor | TeamPCP (aka PCPcat, DeadCatx3, UNC6780) |
| npm maintainer account abused | `atool` |
| npm publish window | ~01:56–02:56 UTC, 2026-05-19 (~22-min burst) |
| npm payload | 498 KB obfuscated Bun script (Mini Shai-Hulud toolkit) |
| Malicious `durabletask` versions | `1.4.1`, `1.4.2`, `1.4.3` (safe: `1.4.0`) |
| `durabletask` payload | 28 KB multi-cloud credential stealer + worm; skips Russian locale |
| C2 (durabletask) | `check.git-service.com`, `t.m-kosche.com` |
| Provenance abuse | Self-minted **valid Sigstore attestations** (ephemeral EC keypair + OIDC) → green badge |
| Postinstall artifacts | `.vscode/tasks.json` (`runOn: folderOpen`), `.claude/settings.json`, `.claude/setup.mjs` |
| Campaign total | 1,055 versions / 502 packages (npm 1,048, PyPI 6, Composer 1) |

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — especially for CI runners with PyPI/npm publish tokens in Actions secrets
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Why the Sigstore-provenance angle matters
The [May 11 TanStack wave](2026-05-tanstack-mini-shai-hulud.md) was the first malicious npm package with *valid SLSA provenance* — but that came from hijacking a real release pipeline mid-build. The May 19 wave goes further: the worm itself **generates fresh, cryptographically valid Sigstore attestations** on the fly using an ephemeral EC keypair and OIDC identity tokens, so every republished package passes standard provenance verification with a green badge. **Provenance attestation proves *who* built an artifact, not that the artifact is *safe*.** Treat the badge as identity metadata, not a security verdict.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — never store long-lived PyPI/npm publish tokens in CI secrets; use OIDC trusted publishing with environment protection rules.
→ Pin dependencies and use `--ignore-scripts` by default; review postinstall scripts before enabling them.

## Sources
- [Socket — Mini Shai-Hulud Hits @antv Ecosystem, 639 Compromised npm Packages](https://socket.dev/blog/antv-packages-compromised) — npm count, payload, detection timing.
- [StepSecurity — Shai-Hulud: Here We Go Again. Mass npm Supply Chain Attack Hits the AntV Ecosystem](https://www.stepsecurity.io/blog/shai-hulud-here-we-go-again-mass-npm-supply-chain-attack-hits-the-antv-ecosystem) — maintainer account, burst window.
- [Aikido — Mini Shai-Hulud Strikes Again: npm Worm Compromises Hundreds of @antv Packages](https://www.aikido.dev/blog/mini-shai-hulud-antv-npm-supply-chain-attack) — IOCs, affected package list.
- [Aikido — Microsoft's durabletask package on PyPi Compromised. Mini Shai Hulud attacks again... again!](https://www.aikido.dev/blog/durabletask-package-compromised-mini-shai-hulud) — durabletask arm.
- [Wiz — durabletask: TeamPCP's Latest PyPi Compromise](https://www.wiz.io/blog/durabletask-teampcp-supply-chain-attack) — payload, GitHub-token pivot, attribution.
- [SafeDep — Malicious durabletask on PyPI: Multi-Cloud Credential Stealer with Worm Capabilities](https://safedep.io/malicious-durabletask-pypi-supply-chain-attack/) — versions, C2, Russian-locale skip.
- [SafeDep — Mini Shai-Hulud Strikes Again: 317 npm Packages Compromised](https://safedep.io/mini-shai-hulud-strikes-again-314-npm-packages-compromised/) — package/version counts.
- [InfoWorld — AntV data visualization tool the latest to be hit by ongoing npm supply chain attacks](https://www.infoworld.com/article/4173277/antv-data-visualization-tool-the-latest-to-be-hit-by-ongoing-npm-supply-chain-attacks.html)
- [BleepingComputer — New Shai-Hulud malware wave compromises 600 npm packages](https://www.bleepingcomputer.com/news/security/new-shai-hulud-malware-wave-compromises-600-npm-packages/)
- [CyberScoop — Mini Shai-Hulud returns, compromising hundreds of npm packages](https://cyberscoop.com/mini-shai-hulud-malware-npm-packages-compromised-again/)
- [Cybersecurity News — Microsoft Python Client DurableTask Compromised by TeamPCP Hackers](https://cybersecuritynews.com/microsoft-python-client-durabletask/)
- [SecurityWeek — Over 320 NPM Packages Hit by Fresh Mini Shai-Hulud Supply Chain Attack](https://www.securityweek.com/over-320-npm-packages-hit-by-fresh-mini-shai-hulud-supply-chain-attack/)
- [The Hacker News — Mini Shai-Hulud Pushes Malicious AntV npm Packages via Compromised Maintainer Account](https://thehackernews.com/2026/05/mini-shai-hulud-pushes-malicious-antv.html)
