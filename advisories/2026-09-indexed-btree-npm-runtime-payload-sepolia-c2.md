---
id: 2026-09-indexed-btree-npm-runtime-payload-sepolia-c2
title: "indexed-btree and nine sibling npm packages (a sorted-btree look-alike, ~2M registry downloads a week) carried no install script at all — the loader sat inside BTree.prototype.set and fired the first time an application called it with key 100, fingerprinted the host to Slack and Telegram, and pulled an encrypted second stage from an Ethereum Sepolia smart contract; removed from npm 2026-09-03, disclosed by Checkmarx 2026-09-17"
date_disclosed: 2026-09-17
last_updated: 2026-09-21
severity: high
status: contained
ecosystems: [npm]
tools_affected: ["indexed-btree ≤ 2.1.3", "btree-core ≤ 3.2.4", "ordered-kv-index", "btree-leaderboard", "priority-slot-queue", "btree-range-store", "btree-time-index", "btree-lru-cache", "neighbor-key-map", "sliding-score-window", "any project whose assistant picked one of these names instead of sorted-btree"]
tags: [supply-chain, npm, runtime-payload, install-script-evasion, npm-v12, blockchain-c2, ethereum, slack-exfil, telegram-exfil, look-alike, slopsquatting]
---

## TL;DR
Checkmarx Zero (Bruno Dias) published on **2026-09-17** an npm campaign built for the post-`npm v12` world: **`indexed-btree`**, a look-alike of the legitimate `sorted-btree` B+ tree library, has **no `preinstall`/`install`/`postinstall`** — nothing for a lifecycle-script block or `--ignore-scripts` to catch. Its loader lives inside the library's own **`BTree.prototype.set`** and runs the first time application code calls `set()` with **`key == 100`**, spawning a child process on an obfuscated `sharedLoad.min.js`. That stage fingerprints the host (OS, architecture, hostname, CPU, memory, uptime), posts it to **Slack and Telegram** bot channels, then generates an X25519 key pair, reads the attacker's public key from an **Ethereum Sepolia smart contract** (`0xE390863Dac96a7118C71227C2b099B50cF602D31`), derives an AES key by ECDH and decrypts two ciphertext blobs stored on-chain into the second-stage payload — C2 that no domain takedown reaches. Checkmarx found **nine sibling packages** on the same contract (`btree-core`, `ordered-kv-index`, `btree-leaderboard`, `priority-slot-queue`, `btree-range-store`, `btree-time-index`, `btree-lru-cache`, `neighbor-key-map`, `sliding-score-window`), a prior reuse in `mutex-forge`, a GitHub repo dressed with plausible commits and an AI-generated maintainer photo, and a wallet holding ~**109 ETH**. npm replaced all of them with security-holding packages on **2026-09-03**; the registry still reports ~2M "weekly downloads" for the holding package, which says the headline download counts were traffic, not adoption.

## What happened

**Trigger without an install script.** Checkmarx: "Rather than using install scripts, the malware hides within `BTree.prototype.set`. When users call this core function with `key == 100`, it spawns a child process executing `sharedLoad.min.js`." Every other method behaves like the real library, so tests pass and the package looks fine in a diff. This is the same evasion the corpus has seen at *import* time — [WeaselBiscuit](2026-09-weaselbiscuit-npm-chrome-extension-storage-stealer.md)'s `initialize()`, [PolinRider](2026-03-polinrider-multi-ecosystem-dprk-campaign.md)'s `index.js`, [Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md)'s `binding.gyp` — moved one step later, to *use* time, which also defeats sandboxes that load the module and watch for side effects.

**Exfiltration and C2.** Stage one collects OS architecture, hostname, CPU/memory specs and uptime and sends them through a Slack bot token and channel and a Telegram bot token and chat id (Checkmarx publishes both; they are omitted here as they are attacker credentials, not defender signals). Stage two is fetched from the blockchain: the malware generates an X25519 keypair, retrieves the attacker's public key from the Sepolia contract, derives an AES key via ECDH, and decrypts two ciphertext blobs the contract stores — the payload itself lives on-chain, read through public RPC providers. The hard-coded attacker X25519 public key is `bad013df6eec5d686f4cc8551e0a5c87a0135164bdd1dafb1c75141d1b526702`. Checkmarx puts the operator's wallet at ~109 ETH (€230,933.57 at writing). Blockchain dead-drops are the [ChainDrop / NullReceiver](2026-08-nullreceiver-npm-ethereum-c2.md) pattern; this campaign stores the *payload* on-chain, not only the pointer.

**The cluster and the timeline (npm registry, fetched 2026-09-21).** `indexed-btree` published 2.1.1 on 2026-06-18, 2.1.2 on 06-22, 2.1.3 on 07-27; `btree-core` 3.2.1 on 06-22 through 3.2.4 on 07-24; `ordered-kv-index` 1.0.1 on 07-24. All three now carry `0.0.1-security` as `latest`, published **2026-09-03 between 10:12 and 10:13 UTC** — the registry's takedown marker, two weeks before the write-up. Checkmarx's per-package download figures: `btree-core` 1,951,274, `btree-leaderboard` 493,685, `btree-range-store` 468,092, `ordered-kv-index` 448,184, `sliding-score-window` 448,024, `btree-time-index` 425,312, `priority-slot-queue` 402,860, `btree-lru-cache` 372,185, `neighbor-key-map` 366,019.

**About the download numbers.** `api.npmjs.org` reports **1,977,204** downloads of `indexed-btree` and **2,225,915** of `btree-core` for 2026-09-14 → 09-20 — a week in which both had been security-holding stubs for eleven days — against **802,346** for the genuine `sorted-btree`. A holding package that out-pulls the library it impersonates is registry traffic (mirrors, scanners, or the operator's own inflation to make the package look established), not two million projects. The real blast radius is unknown; the "millions of downloads" in coverage should be read as the campaign's marketing, and the risk as: **if an assistant or a search put one of these names in your `package.json`, you have the loader.** BleepingComputer covered the campaign on 2026-09-20 (not fetched: the site returns 403 to this sweep).

## Am I affected?

```bash
# Any of the ten names in any lockfile, anywhere
grep -rE '"(indexed-btree|btree-core|ordered-kv-index|btree-leaderboard|priority-slot-queue|btree-range-store|btree-time-index|btree-lru-cache|neighbor-key-map|sliding-score-window|mutex-forge)"' \
  package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
ls node_modules | grep -E '^(indexed-btree|btree-core|ordered-kv-index|btree-leaderboard|priority-slot-queue|btree-range-store|btree-time-index|btree-lru-cache|neighbor-key-map|sliding-score-window|mutex-forge)$'
# The loader file and the on-chain C2 in installed code
grep -rl "sharedLoad.min.js" node_modules 2>/dev/null
grep -rl "0xE390863Dac96a7118C71227C2b099B50cF602D31\|bad013df6eec5d686f4cc8551e0a5c87a0135164bdd1dafb1c75141d1b526702" node_modules 2>/dev/null
# Runtime signal: an app process spawning node on sharedLoad.min.js, or outbound to
# hooks.slack.com / api.telegram.org / a Sepolia RPC endpoint from a service that has no business there
```

- **Affected if:** any of the packages resolved into a project and application code called `.set()` on the tree (a `key` of 100 is an ordinary value in leaderboard/queue/range code — the trigger is not exotic).
- **Not affected if:** you depend on `sorted-btree` itself, or the name never entered a lockfile. The registry now serves only the `0.0.1-security` stub for every name.

## If you are affected

Follow [if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md): remove the package, rebuild `node_modules` from a clean lockfile, and treat the host's fingerprint as sent and its second stage as unknown — rotate what a process running as the app could read ([rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)). Because the trigger is at run time, a *deployed* service that used the library is the affected system, not only the developer laptop that installed it.

## Prevention

- **Blocking install scripts is necessary, not sufficient.** `npm v12`'s default and `ignore-scripts=true` ([prevention/npm-hardening.md](../prevention/npm-hardening.md)) stop the install-time class; this campaign, WeaselBiscuit and PolinRider were designed around it. Add a dependency scanner that looks at *code* (Socket, Aikido, StepSecurity, npm audit signatures) and watches for prototype-method overrides, child-process spawns in data-structure libraries, and blockchain RPC clients in packages that have no reason to have them.
- **Verify the package an assistant names exists and is the one you meant** — [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md). `indexed-btree` next to `sorted-btree` is the slopsquatting shape: a plausible name, a real-looking repo, download counts bought or botted.
- Egress control on build and runtime hosts: a B-tree library talking to Slack, Telegram or an Ethereum RPC is the detection.

## Sources
- [Checkmarx Zero — npm 'btree' Malware Campaign Affects Millions of Downloads, No Need for Install Script](https://checkmarx.com/zero-post/npm-btree-malware-campaign-affects-millions-of-downloads-no-need-for-install-script/) — primary, 2026-09-17 (Bruno Dias): the `BTree.prototype.set` / `key == 100` trigger, `sharedLoad.min.js`, the Slack/Telegram exfiltration, the Sepolia contract and X25519/ECDH/AES second-stage mechanism, the nine sibling packages with download counts, `mutex-forge`, the ~109 ETH wallet, the decoy GitHub repo. Fetched 2026-09-21.
- npm registry records (`registry.npmjs.org/<pkg>`, fetched 2026-09-21): `indexed-btree` 2.1.1 2026-06-18, 2.1.2 06-22, 2.1.3 07-27, `0.0.1-security` 2026-09-03T10:13Z; `btree-core` 3.2.1 06-22 → 3.2.4 07-24, `0.0.1-security` 09-03T10:12Z; `ordered-kv-index` 1.0.1 07-24, `0.0.1-security` 09-03. Weekly downloads via `api.npmjs.org` for 2026-09-14 → 09-20: `indexed-btree` 1,977,204; `btree-core` 2,225,915; `sorted-btree` 802,346.
- BleepingComputer's 2026-09-20 story "Malicious npm packages evade install-script defenses at runtime" surfaced through the Hacker News feed and is the second-outlet coverage of Checkmarx's finding; it was not fetched (the site returns 403 to this sweep) and is not relied on for any figure above.
