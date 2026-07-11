---
id: 2026-07-injective-labs-npm-wallet-stealer
title: "Injective Labs SDK npm compromise — compromised contributor account plants wallet-key stealer in @injectivelabs/sdk-ts"
date_disclosed: 2026-07-08
last_updated: 2026-07-08
severity: high
status: contained
ecosystems: [npm]
tools_affected: ["@injectivelabs/sdk-ts", "@injectivelabs/wallet-core", "@injectivelabs/wallet-evm", "@injectivelabs/wallet-cosmos", "@injectivelabs/wallet-private-key", "any project depending on @injectivelabs scoped packages pinned to 1.20.21"]
tags: [supply-chain, npm, crypto-wallet-theft, account-compromise, credential-theft, key-derivation]
---

## TL;DR

On **2026-06-08 (~22:59 CEST)**, an attacker who compromised a **legitimate contributor's GitHub account** on the Injective Labs SDK repository published `@injectivelabs/sdk-ts@1.20.21` (plus 17 dependent `@injectivelabs`-scoped packages pinned to it) with malicious code that hooks the SDK's wallet key-derivation functions and exfiltrates mnemonic seed phrases and private keys. Injective's maintainers reverted the malicious commits and published a clean release within roughly an hour, and the malicious version was downloaded only **310 times** against the package's ~50,000 weekly download base — but the incident was not publicly reported until **~July 8-10, 2026**, a full month later. Multiple outlets (Socket, BleepingComputer, The Hacker News, SC Media) independently confirmed the technical details.

## What happened

`@injectivelabs/sdk-ts` is the official TypeScript SDK for the Injective Protocol blockchain, used by developers building wallets, trading bots, DEXs, and DeFi/payment tooling on Injective — roughly 50,000 weekly npm downloads and 87 direct dependent packages (~112,000 cumulative downloads across the dependency tree).

According to Socket's timeline (all times GMT+2 on 2026-06-08):
- **20:06** — Suspicious commits begin, including a branch named `test-backdoor-check`, apparently testing the compromised account's access and rights.
- **22:59** — Malicious `@injectivelabs/sdk-ts@1.20.21` published to npm, along with 17 other `@injectivelabs`-scoped packages that pinned to the malicious version.
- **23:18** — Malicious commits reverted on GitHub.
- **23:48** — A clean release published to npm.

The malicious code was injected via commits from a **compromised GitHub account belonging to a developer with an established history of legitimate contributions** to the repository — not a stolen npm token. The attacker used the project's own trusted publishing pipeline to ship the poisoned package, similar in shape (trusted-identity abuse rather than credential-only theft) to the source-repo-compromise pattern seen in [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md), though here the vector was a compromised personal account rather than a bot-authored workflow file.

### Malware mechanism

The payload does **not** run at install time — it activates only when a consuming application calls the SDK's wallet key-derivation functions, `fromMnemonic` and `fromHex` (located in `dist/esm/accounts-jQ1GSgaW.js` and `dist/cjs/accounts-Cy0p4lLW.cjs`). A hooked `trackKeyDerivation` function, disguised as telemetry, captures the full mnemonic seed phrase and/or private key material, base64-encodes it, and exfiltrates it via an HTTPS POST to a subdomain crafted to resemble Injective's own public testnet infrastructure — blending the exfil traffic into what looks like normal SDK-to-chain communication rather than an obviously foreign C2 host.

### Impact

- Only **310 downloads** of the malicious version were recorded before it was deprecated, against the package's ~50,000/week baseline — the live window was short.
- Socket, OX Security, and StepSecurity all independently flagged the compromise; Injective's response was fast enough that the incident had limited real-world blast radius, and reporting indicates no confirmed financial loss ("nobody lost a dime").
- Anyone who installed `1.20.21` directly, or transitively through any of the 17 co-published `@injectivelabs` packages, and then generated or imported a wallet key while running that version, should treat the affected key material as compromised.

## Am I affected?

```bash
# Check whether the malicious version is anywhere in your dependency tree
npm ls --all 2>/dev/null | grep -E "@injectivelabs/(sdk-ts|wallet-core|wallet-evm|wallet-cosmos|wallet-private-key)@1\.20\.21"

# Check your lockfile directly
grep -A2 '"@injectivelabs/sdk-ts"' package-lock.json | grep '1.20.21'
```

You're affected only if you had `1.20.21` installed **and** your application (or a script/test you ran) actually called wallet key-generation or key-import functions during the roughly one-hour window on 2026-06-08. Merely having the package in `node_modules` without invoking those code paths does not trigger exfiltration.

## If you are affected

1. Update to `@injectivelabs/sdk-ts@1.20.23` (or later) immediately.
2. **Treat any mnemonic or private key generated or imported through the SDK while `1.20.21` was installed as compromised** — move funds to a newly generated wallet and never reuse the old key material.
3. Rotate any other secrets present in the same environment as a precaution, per [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).
4. Audit outbound network logs for connections resembling `injective.network`-style hostnames originating from your build/runtime environment that don't match your normal RPC endpoints.

## Prevention

- Pin dependencies with lockfiles and review diffs on version bumps for security-sensitive SDKs (wallet/crypto libraries especially), not just major-version changes.
- Treat a compromised **maintainer/contributor GitHub account** as an equally viable attack path to a stolen npm token — 2FA and hardware security keys on contributor accounts matter as much as on publishing accounts.
- See [prevention/npm-hardening.md](../prevention/npm-hardening.md) and [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Sources

- [The Hacker News — Injective Labs GitHub Compromise Pushes Wallet-Key-Stealing npm Packages](https://thehackernews.com/2026/07/injective-labs-github-compromise-pushes.html) — overview, package/version details, exfiltration mechanism.
- [BleepingComputer — Injective SDK on npm infected with cryptocurrency wallet stealer](https://www.bleepingcomputer.com/news/security/injective-sdk-on-npm-infected-with-cryptocurrency-wallet-stealer/) — attack vector (compromised contributor account), remediation guidance.
- [Socket — Compromised Injective SDK npm Package Exfiltrates Wallet Keys](https://socket.dev/blog/compromised-injective-sdk-npm-package) — detailed timeline, function-level technical analysis, download-impact numbers.
- [SC Media — Injective Labs SDK npm package compromised to steal cryptocurrency keys](https://www.scworld.com/brief/injective-labs-sdk-npm-package-compromised-to-steal-cryptocurrency-keys) — independent corroboration of scope and response.
