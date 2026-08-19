---
id: 2026-08-nullreceiver-npm-ethereum-c2
title: "NullReceiver: DPRK-linked npm malware hides C2 IPs inside blank Ethereum transactions, hits Tailwind/PostCSS-themed packages"
date_disclosed: 2026-08-10
last_updated: 2026-08-10
severity: high
status: contained
ecosystems: [npm, javascript, blockchain-c2]
tools_affected: ["@kolbo/mcp", "agentgui", "godot-kit", "envpack-conf", "postcss-initial-provider", "tailwindcss-motion-advanced"]
tags: [supply-chain, npm, c2, blockchain, dprk, contagious-interview, tailwind-css]
---

## TL;DR

Sonatype Research Labs found six npm packages — three hijacked legitimate packages and three newly published malicious ones — using a technique dubbed **"NullReceiver"**: the loader queries Ethereum for a specific outbound transaction from an attacker-controlled wallet, then reads the raw bytes of the transaction's **recipient address** and decodes them as two IPv4 addresses to use as primary/secondary C2 endpoints. The transaction itself carries **zero value and no data** — nothing but an ordinary-looking wallet-to-wallet transfer — so there's no smart-contract call, no memo field, and no fixed destination address for a defender to flag, evading the detection techniques already built for the earlier "EtherHiding" blockchain-C2 technique. Attribution points to **DPRK's Contagious Interview campaign** (Lazarus-linked). Two of the three newly-published malicious packages — `postcss-initial-provider` and `tailwindcss-motion-advanced` — are named to look like Tailwind CSS/PostCSS plugins, directly targeting the Tailwind ecosystem this repo tracks.

## What happened

Sonatype Research Labs identified the campaign on **2026-08-10** across two tracking IDs: `sonatype-2026-005899` (three hijacked legitimate packages: `@kolbo/mcp@1.57.1`, `agentgui@1.0.1127`, `godot-kit@1.0.1786316795`) and `sonatype-2026-005901` (three newly-published malicious packages designed from the start to carry the payload: `envpack-conf@1.0.1`, `postcss-initial-provider@3.0.4`, `tailwindcss-motion-advanced@1.0.1`) ([Sonatype](https://www.sonatype.com/blog/six-npm-packages-use-ethereum-transactions-to-retrieve-malicious-payloads)).

**Mechanism:** the loader queries an Ethereum RPC endpoint (implementation supports multiple providers with request racing and batched JSON-RPC calls, falling back to the Blockscout API if direct RPC access is blocked) for an outbound transaction sent from an attacker-controlled wallet. It reads the transaction's **recipient address bytes** and decodes them as two IPv4 addresses — the C2 servers. Because the transaction itself has a value of `0` and an empty input/data field, it is indistinguishable from a routine, meaningless wallet-to-wallet transfer to anyone inspecting the chain casually; the "message" is encoded entirely in *which address* the wallet paid, not in anything carried by the payment. Once C2 resolves, the malware retrieves further stages from `/0x/cls` and `/0x/ls` endpoints, either via a standard HTTP GET or via an `X-Payload-B64` response header, then Base64- and XOR-decodes the payload before executing it with `eval()` or as a detached Node.js child process.

**Why this matters beyond "another crypto stealer":** this is a distinct evolution of the blockchain dead-drop C2 techniques this repo already tracks (Solana memos, Ethereum smart-contract calls, ICP canisters, Tron/Aptos/BNB transaction queries). Prior "EtherHiding"-style techniques relied on smart-contract interactions, transaction payload data, or a fixed destination address — all of which give defenders a concrete artifact to signature or blocklist. NullReceiver removes all three: no contract call, no payload bytes, no fixed address, leaving only "a wallet sent an empty transaction to another wallet" as the observable event.

**Attribution:** Sonatype and independent researcher OpenSourceMalware both link the campaign to DPRK's **Contagious Interview** operation (attributed to the Lazarus Group), based on wallet-address overlap with prior Contagious Interview activity ([OpenSourceMalware](https://opensourcemalware.com/blog/nullreceiver-dprk-c2-technique)). Coverage corroborated independently by [The Hacker News](https://thehackernews.com/2026/08/trojanized-npm-packages-decode-c2-ip.html) and [Cyberpress](https://cyberpress.org/nullreceiver-hides-ethereum-c2/).

## Am I affected?

```bash
npm ls @kolbo/mcp agentgui godot-kit envpack-conf postcss-initial-provider tailwindcss-motion-advanced 2>/dev/null
```

You are affected if any of the six named packages/versions above are in your dependency tree. Pay particular attention if you use Tailwind/PostCSS plugin-sounding packages installed outside your normal, pinned toolchain — `postcss-initial-provider` and `tailwindcss-motion-advanced` are not real Tailwind Labs or PostCSS project packages.

## If you are affected

1. Remove the affected package(s) immediately and audit `node_modules` for the loader logic described above (searches for Ethereum RPC calls, `X-Payload-B64` header handling, or IP-address bit-shifting from a byte array are good greps).
2. Treat any host that installed one of these packages as potentially compromised — check for unexpected outbound connections to unfamiliar IPs following an `npm install`.
3. Rotate any credentials (npm tokens, cloud keys, SSH keys) that were present in the environment where the package was installed.
4. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- Egress-monitor build/CI environments for unexpected Ethereum JSON-RPC calls (or calls to Blockscout-style block-explorer APIs) from `node_modules` code that has no legitimate reason to touch a blockchain — this is the same detection principle already recommended for other blockchain-C2 npm campaigns this repo tracks.
- Pin dependencies and vet new/renamed packages before adopting them, especially ones that closely mimic a popular framework's plugin-naming convention (Tailwind, PostCSS, Vite, etc.).
- → [prevention/npm-hardening.md](../prevention/npm-hardening.md)
- → [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources

- [Sonatype — Six npm Packages Use Ethereum Transactions to Retrieve Malicious Payloads](https://www.sonatype.com/blog/six-npm-packages-use-ethereum-transactions-to-retrieve-malicious-payloads) — primary technical disclosure: package names/versions, mechanism, tracking IDs.
- [The Hacker News — Trojanized npm Packages Employ NullReceiver Tactic to Decode C2 IP from Blockchain](https://thehackernews.com/2026/08/trojanized-npm-packages-decode-c2-ip.html) — independent corroboration.
- [OpenSourceMalware — NullReceiver: hidden blockchain C2 in npm packages](https://opensourcemalware.com/blog/nullreceiver-dprk-c2-technique) — independent corroboration, DPRK/Contagious Interview attribution via wallet-address overlap.
