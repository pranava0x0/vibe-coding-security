---
id: 2026-04-canisterworm-namastex-npm
title: "CanisterWorm — self-propagating npm worm hits Namastex Labs' Automagik AI-agent packages, uses an Internet Computer canister as a dead drop"
date_disclosed: 2026-04-22
last_updated: 2026-04-22
severity: high
status: contained
ecosystems: [npm, pypi, ai-agents, namastex]
tools_affected: ["@automagik/genie", "pgserve", "@fairwords/websocket", "@fairwords/loopback-connector-es", "@openwebconcept/design-tokens", "@openwebconcept/theme-owc"]
tags: [supply-chain, npm-worm, credential-theft, blockchain-c2, self-propagation, teampcp, ai-agents]
---

## TL;DR
A self-propagating npm worm — dubbed **CanisterWorm** for its use of an **Internet Computer Protocol (ICP) canister** as exfiltration infrastructure — compromised packages belonging to **Namastex Labs** (an agentic-AI vendor whose `@automagik/genie` package is part of its "Automagik" autonomous-agent suite), plus several unrelated packages sharing the same embedded RSA key material. The payload steals a broad set of developer/cloud credentials and crypto-wallet data at install time, then self-propagates by hijacking the maintainer's own npm publish tokens to inject itself into further packages. Code references tie it to the **TeamPCP** threat actor, the same group behind the Trivy/LiteLLM GitHub Actions compromise and other 2026 campaigns already tracked in this repo.

## What happened
Socket.dev and other researchers identified a wave of trojanized npm releases starting **2026-04-22**, publicly reported as still developing (additional malicious versions were being published as the story broke). Confirmed compromised packages/versions:

- **`@automagik/genie`** 4.260421.33–4.260421.39 — part of Namastex Labs' Automagik autonomous-AI-agent product suite
- **`pgserve`** 1.1.11–1.1.13 — also tied to Namastex; researchers noted these versions **lack corresponding Git tags** despite the repository's history tracking tags through v1.1.10, suggesting a **release-path compromise** (the attacker published directly to npm without a matching, reviewable Git commit) rather than a stolen account posting from the legitimate source.
- **`@fairwords/websocket`** 1.0.38–1.0.39
- **`@fairwords/loopback-connector-es`** 1.4.3–1.4.4
- **`@openwebconcept/design-tokens`** and **`@openwebconcept/theme-owc`** 1.0.3

All carry the same embedded RSA key material used by the malicious payload, indicating one campaign across unrelated maintainer accounts.

**Payload mechanics:** a `postinstall` script triggers at install time (blockable via `--ignore-scripts` or npm v12's `allowScripts: off` default, unlike `binding.gyp`-triggered payloads tracked elsewhere in this repo). It harvests a broad credential set — environment variables matching common secret-naming patterns, `.npmrc`, SSH keys, `.git-credentials`, `.netrc`, AWS/Azure/GCP cloud credentials, Kubernetes/Docker/Terraform configuration, browser-stored logins, and crypto-wallet data (MetaMask, Phantom, Solana, Ethereum). Stolen data is encrypted with an **AES-256-CBC + RSA-OAEP-SHA256 hybrid scheme** and exfiltrated to two channels: a webhook at `telemetry.api-monitor[.]com/v1/telemetry` (styled to look like ordinary telemetry) and an **ICP (Internet Computer Protocol) canister** at `cjn37-uyaaa-aaaac-qgnva-cai.raw.icp0[.]io/drop` — a blockchain-hosted, decentralized-compute dead drop, extending this repo's already-tracked list of blockchain C2 channels (Solana memos, Ethereum smart contracts, Tron/Aptos/BNB Smart Chain transaction queries) to a new platform.

**Self-propagation:** the worm extracts any npm publish tokens it finds on the infected host, enumerates which packages those tokens can publish to, injects the same malicious `postinstall` hook, and republishes — the same worm shape as this repo's tracked Shai-Hulud lineage, but running over freshly-stolen tokens rather than a single compromised maintainer account. A PyPI propagation path via `.pth` file injection was also observed, extending the worm cross-ecosystem.

**TeamPCP attribution:** the malicious Python injection logic contains an explicit code-level reference to a "TeamPCP/LiteLLM method" — the same threat actor and technique lineage this repo already tracks in the [Trivy/LiteLLM GitHub Actions compromise](2026-03-trivy-litellm-supply-chain.md). Researchers also note the ICP-canister infrastructure pattern matches a **prior, smaller CanisterWorm wave** that compromised 29 packages using the same canister-backed C2 — this repo had not previously tracked either wave.

## Am I affected?
```bash
# Check your lockfile for any of the compromised package/version combinations
grep -E "@automagik/genie|pgserve|@fairwords/websocket|@fairwords/loopback-connector-es|@openwebconcept/design-tokens|@openwebconcept/theme-owc" package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null

# Look for the exfiltration endpoints in node_modules (if you suspect a run occurred)
grep -r "api-monitor\|icp0.io/drop\|cjn37-uyaaa" node_modules/ 2>/dev/null
```
If any match, treat every credential the malware targets (npm tokens, SSH keys, cloud creds, browser-stored logins, crypto wallets) as compromised — this campaign was still expanding as of disclosure, so also check for versions published after 2026-04-22 that may not be listed above.

## If you are affected
1. Remove the affected package versions and pin to a known-clean version or a patched release.
2. Rotate: npm publish tokens, SSH keys, cloud credentials (AWS/Azure/GCP), `.netrc`/`.git-credentials` contents, and any crypto wallet whose extension data lives on the affected machine.
3. → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
4. → [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
5. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts` / npm v12 `allowScripts: off` blocks this specific payload's install-time trigger (a `postinstall` hook, not a `binding.gyp` build step).
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources
- [Socket.dev — Namastex.ai npm Packages Hit with TeamPCP-Style CanisterWorm](https://socket.dev/blog/namastex-npm-packages-compromised-canisterworm) — primary technical writeup, fetched directly: package/version list, payload mechanics, TeamPCP attribution, ICP canister infrastructure.
- [SC World — Namastex npm packages compromised in 'CanisterWorm' supply-chain attack](https://www.scworld.com/news/namastex-npm-packages-compromised-in-canisterworm-supply-chain-attack)
- [The Register — Another npm supply chain worm hits dev environments](https://www.theregister.com/2026/04/22/another_npm_supply_chain_attack/) — independent corroboration, disclosure date.
- [GBHackers — NPM Worm Hits Namastex Packages, Steals Secrets Across Registries](https://gbhackers.com/npm-worm-hits-namastex/)
- [CyberSecurityNews — Compromised Namastex npm Packages Deliver TeamPCP-Style CanisterWorm Malware](https://cybersecuritynews.com/compromised-namastex-npm-packages/)
