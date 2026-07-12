---
id: 2026-07-jscrambler-npm-preinstall-infostealer
title: "jscrambler npm package compromised — Rust infostealer that survives --ignore-scripts (July 2026)"
date_disclosed: 2026-07-11
last_updated: 2026-07-12
severity: high
status: contained
ecosystems: [npm]
tools_affected: [any-node-project, claude-desktop, cursor, windsurf, zed, vscode]
tags: [supply-chain, credential-theft, npm, preinstall-hook, import-time-exec, ignore-scripts-bypass, infostealer, crypto-wallet]
---

## TL;DR
An attacker who obtained jscrambler's npm publishing credential pushed **five malicious releases** of the `jscrambler` package (**8.14.0, 8.16.0, 8.17.0, 8.18.0, 8.20.0**) between **15:12–17:53 UTC on 2026-07-11**, dropping a Rust-compiled infostealer that harvests crypto wallets, browser credentials, and — notably for this audience — **API keys and MCP credentials from Claude Desktop, Cursor, Windsurf, Zed, and VS Code config files**. The first three releases used a `preinstall` hook; the last two moved the loader into `dist/index.js`/`dist/bin/jscrambler.js` so it fires on `require()`/import instead — a technique that **survives `npm install --ignore-scripts`**. Socket detected the first bad version within 6 minutes. Jscrambler revoked and rotated its publishing credentials; **8.22.0 is the confirmed-clean release**.

## What happened
`jscrambler` is a JavaScript/webpack obfuscation tool (~15,800 weekly downloads) used in build pipelines. On **2026-07-11**, an attacker who had obtained a valid npm publishing credential for the package published a run of malicious versions interleaved with what appear to be the maintainers' own remediation releases — Socket's advisory notes "compromised and clean releases are interleaved, not a single contiguous bad range":

- **8.14.0, 8.16.0, 8.17.0** — added an undocumented `"preinstall": "node dist/setup.js"` hook.
- **8.18.0, 8.20.0** — the attacker **moved the trigger off the install hook** and inlined the loader as self-executing code directly into `dist/index.js` and `dist/bin/jscrambler.js`. This version of the payload only fires when the package is imported or its CLI is run — not at `npm install` time — which means it is **not blocked by `npm install --ignore-scripts`**, the standard mitigation for lifecycle-hook malware (see the Phantom Gyp and Rollup-polyfill cautions already tracked in this repo for the other two primitives — `binding.gyp` native builds and import-time remote fetch — that also evade `--ignore-scripts`).
- **8.13.0** (2026-06-30) was the last known-clean release before the compromise; **8.22.0** is confirmed clean.

### Delivery mechanism
The `setup.js` loader unpacks a 7.8 MB file, `dist/intro.js`, disguised as an ordinary JS asset but actually an obfuscated container (custom 5-byte magic header `1B 43 53 49 01`) holding three platform-specific Rust-compiled binaries — a Linux x86-64 ELF, a Windows PE32+, and an Apple Silicon Mach-O. The loader drops the platform-matched binary into a randomly named, hidden file in the OS temp directory and executes it detached from the parent process.

### What the stealer targets
- **Crypto wallets:** MetaMask, Trust Wallet, Coinbase, and Phantom browser-extension data; Exodus wallet vault extraction with an attempted seed-phrase decryption using embedded scrypt parameters.
- **AI/dev-tool credentials:** Claude Desktop, Cursor, Windsurf, Zed, and VS Code configuration files — the API keys and MCP credentials stored there.
- **Cloud credentials:** GCP metadata-service tokens and Secret Manager access, AWS ECS task metadata / Secrets Manager / SSM Parameter Store, Azure IMDS and management endpoints.
- **Everything else:** browser login data (Chrome/Firefox `Login Data`, cookies, Local Storage/IndexedDB), Discord, Slack, Telegram, Steam, KDE KWallet, systemd units, crontab, macOS LaunchAgents, plus persistence via Windows Task Scheduler and macOS LaunchAgents, anti-analysis (Tor detection, `/etc/machine-id` fingerprinting), and TLS-encrypted exfiltration over HTTP multipart uploads.
- Sensitive strings inside the binary are individually encrypted with **ChaCha20-Poly1305** (embedded 32-byte keys, 12-byte nonces) — Socket recovered roughly 2,400 decrypted strings with independent AEAD implementations and zero tag mismatches.

### Detection and response
Socket flagged `8.14.0` **6 minutes after publication**. Jscrambler confirmed in its own advisory that "the attacker was able to publish the package using an npm publishing credential," and has since revoked and rotated its publishing credentials and added further controls around its publishing process.

## Am I affected?

```bash
# Check installed jscrambler version anywhere in your tree
npm ls jscrambler --all
grep -E '"jscrambler".*"(8\.14\.0|8\.16\.0|8\.17\.0|8\.18\.0|8\.20\.0)"' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Hunt for the loader/payload files
find . -path '*/node_modules/jscrambler/dist/setup.js' -o -path '*/node_modules/jscrambler/dist/intro.js' 2>/dev/null

# Hunt for hidden randomly-named binaries dropped in temp dirs
find "${TMPDIR:-/tmp}" -maxdepth 1 -type f -name '.*' -newermt '2026-07-11' 2>/dev/null
```

### IOCs

| Type | Value |
|---|---|
| Malicious versions | `jscrambler@8.14.0`, `8.16.0`, `8.17.0`, `8.18.0`, `8.20.0` |
| Clean versions | `8.13.0` (last known clean before compromise), `8.22.0` (confirmed clean) |
| Compromise window | 2026-07-11, 15:12–17:53 UTC |
| `dist/setup.js` SHA-256 | `a742de963f14a92d24ebcbc7b44ac867e23a20d31d1b0094a13a4f83287f4e60` |
| `dist/intro.js` SHA-256 | `a41a523ef9517aab37ed6eea0ec881821bdcb7aefcb5c5f603adc7907f868c86` |
| Linux ELF SHA-256 | `fbbcf4d8f98168f78f5c0c47a9ae56d59ec8ac84a7c9ca6b797fedfb8d62d2bd` |
| Windows PE SHA-256 | `b7ca95d1b23c8e67416a25cedf741de0917c2096bbc9d24649eea7853d054903` |
| macOS Mach-O SHA-256 | `c8fd47d36bdf7c825378593ab82ed8c24d1dc52e26b507812393e24e1d5201fd` |
| `dist/intro.js` magic header | `1B 43 53 49 01` |

No C2 domain has been disclosed by either primary source as of this writing.

If any affected version was installed on a dev machine or CI runner, treat the host as compromised: rotate browser-stored credentials and any crypto wallet secrets (move funds to a fresh wallet on a clean device), and rotate cloud/CI credentials that were resident in the environment.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) — if this ran on a CI/build host with deploy credentials

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — note that `--ignore-scripts` alone does **not** stop this payload once a package moves its trigger from a lifecycle hook into `dist/index.js`; pin to audited versions and diff `node_modules` on upgrade.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — don't leave long-lived AI-tool API keys/MCP credentials in plaintext config files on developer machines.

## Why this matters for vibe coders
This is one of the first widely disclosed npm infostealers to **explicitly enumerate Claude Desktop, Cursor, Windsurf, Zed, and VS Code** config paths as harvest targets, alongside crypto wallets and cloud credentials — confirming that AI-coding-tool API keys and MCP credentials are now a first-class target category for commodity npm supply-chain malware, not an afterthought. The evolution from a `preinstall` hook (generations 1–3) to an import-time trigger (generations 4–5) inside the *same* campaign is also a reminder that `--ignore-scripts` is necessary but not sufficient — it blocks the easy version of this attack, not the determined one.

## Sources
- [Socket — jscrambler npm Package Compromised in Supply Chain Attack](https://socket.dev/blog/jscrambler-supply-chain-attack)
- [StepSecurity — jscrambler npm package publishes malicious preinstall binary](https://www.stepsecurity.io/blog/jscrambler-npm-package-publishes-malicious-preinstall-binary)
