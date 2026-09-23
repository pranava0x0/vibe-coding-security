---
id: 2026-09-mathmain-encrypted-loader-npm-lusolve-trigger
title: "mathmain, mathsbase and math-universe — three npm clones of mathjs (part of a 23-package, six-month campaign) carried an encrypted loader that stays dormant until application code calls math.lusolve() with a specific 3×3 Pascal matrix, at which point the LU factor becomes the AES key that decrypts a remote-access payload from a second file; a GitHub Actions farm inflated all three past 2M weekly 'downloads', npm removed them, JFrog + SafeDep disclosed 2026-09-17/21"
date_disclosed: 2026-09-17
last_updated: 2026-09-23
severity: high
status: contained
ecosystems: [npm]
tags: [supply-chain, npm, encrypted-loader, runtime-payload, install-script-evasion, trigger-condition, blockchain-c2, ethereum, slack-exfil, telegram-exfil, download-inflation, look-alike, slopsquatting]
---

## TL;DR
JFrog Security Research ("Equation of Compromise," 2026-09-21) and SafeDep (2026-09-17/18) documented an npm campaign of **23 weaponised packages over March–September 2026** that clone `mathjs` almost exactly and add an **encrypted, dormant loader**. The three headline packages — **`mathmain` (1.0.0, published 2026-08-27), `mathsbase` (1.0.1), `math-universe` (1.0.0–1.0.2)** — behave like the real library for every ordinary call. There is **no install script**: the payload only decrypts when application code calls **`math.lusolve(A, b)` with a particular 3×3 symmetric Pascal matrix**, at which point the JSON form of the matrix's LU lower factor is used as the password, `scryptSync` derives a 32-byte AES key, and `AES-256-GCM` decrypts a remote-access payload stored in a second file (`graph.js`). The activated stage fingerprints the host and talks to **Ethereum Sepolia smart contracts (13 on Sepolia, 1 on Base Sepolia, five operator wallets, 2026-03-05 → 09-16)** and **Slack/Telegram** channels. A three-operator **GitHub Actions farm** (30 repos, one-second tarball downloads through a shared WASM decoder) manufactured the headline numbers: as of 2026-09-21 all three were `0.0.1-security` stubs on npm yet still recorded **~2 million "weekly downloads" each** — inflation, not adoption. npm removed the malicious versions. This is the **same operator infrastructure** as [`indexed-btree`](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md) (Slack + Sepolia + X25519, an identical download-inflation farm — JFrog names `events-sync` at 40.7M fake downloads); the two campaigns are one actor's parallel efforts, `math*` cloning `mathjs` and `*btree` cloning `sorted-btree`. JFrog also notes the recovered second stage is "completely broken," so the intended post-compromise action could not be fully recovered.

## What happened

**Trigger without an install script.** SafeDep: the package is `mathjs` with one addition, an encrypted loader that never runs during install or import. The activation is a specific input to a legitimate-looking API — `lusolve()` with a Pascal-matrix argument — so a lifecycle-script block, `--ignore-scripts`, or a sandbox that installs and imports the module all see nothing. This is the same "loader lives inside a normal library method, fires at use time in the deployed app" evasion as [indexed-btree](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md)'s `BTree.prototype.set`, moved one step later than install-time or import-time triggers.

**Cryptographic gating.** JFrog cracked the trigger: the caller activates the loader with a 3×3 symmetric Pascal matrix; the LU decomposition's lower factor, serialized to JSON, is the decryption password; `scryptSync(password, salt, 32)` yields the AES-256-GCM key that decrypts the payload from `graph.js`. Because the key is derived from the trigger input, the payload cannot be decrypted by an analyst who does not already know the matrix — malware that only reveals itself to its intended targets. JFrog "did the work of cracking the password," which is what enabled SafeDep's follow-on analysis (per the researchers' own Hacker News thread).

**Exfiltration and C2.** The activated stage reports host data (platform, hostname, CPU, memory) to Slack and Telegram bot channels (both are attacker credentials and are omitted here as they are not defender signals), then polls **Ethereum Sepolia smart contracts** for tasks — a blockchain dead-drop no domain takedown reaches. JFrog counts 14 C2 contracts across five operator wallets deployed 2026-03-05 → 09-16, and a GitHub Actions farm of 30 repositories (`worker1`–`10`, `job_worker1`–`10`) that used a shared WASM decoder (MD5 `91e020c13cb97a6365135b53b0d0fe5f`) and one-second-interval downloads to inflate counts.

**The download numbers are the story.** `api.npmjs.org` (fetched 2026-09-21) reports **1,981,038** downloads of `mathmain`, **2,591,653** of `mathsbase` and **2,482,574** of `math-universe` for 2026-09-15 → 09-21 — a week in which the npm registry served only the `0.0.1-security` stub for all three (`latest` → `0.0.1-security`, published 2026-09-21 ~19:48–20:05 UTC). A holding stub pulling millions is manufactured traffic, and JFrog's own tell is exactly this: ">1 million downloads with zero dependent packages or repositories." The real blast radius is unknown; the "3.1 million installs of malware" figure in coverage is the campaign's inflation, and the actual risk is narrower and use-triggered: **if an assistant or a fuzzy search put `mathmain`/`mathsbase`/`math-universe` in your `package.json` where you meant `mathjs`, and your code calls `lusolve`, you have the loader.**

## Am I affected?

```bash
# The look-alike names in any lockfile (you almost certainly meant mathjs)
grep -rE '"(mathmain|mathsbase|math-universe|matrixflow-js|modern-events|graphcore-js|mutex-forge)"' \
  package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
ls node_modules 2>/dev/null | grep -E '^(mathmain|mathsbase|math-universe|matrixflow-js|mutex-forge)$'
# The loader files and on-chain C2 in installed code (JFrog IOCs)
grep -rl "lib/cjs/utils/event.js\|lib/cjs/utils/graph.js" node_modules 2>/dev/null
grep -rl "REDISTRIBUTION REQUIRES INCLUSION OF THIS LICENSE" node_modules 2>/dev/null
# Runtime signal: a math library making JSON-RPC calls to an Ethereum Sepolia RPC, or posting to
# hooks.slack.com / api.telegram.org, from a service that has no reason to
```

- **Affected if:** any of the names resolved into a project and code path called `math.lusolve()` on attacker-shaped input (JFrog's matrix is a plausible value in numerical/DeFi code). A *deployed* service that used the library is the affected host, not only the laptop that installed it.
- **Not affected if:** you depend on `mathjs` itself and none of the clone names entered a lockfile. npm serves only the `0.0.1-security` stub for all three now.

## If you are affected

Follow [if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md): remove the package, rebuild `node_modules` from a clean lockfile, and — because the trigger is at run time — treat any host that *ran* the library as the affected system and rotate what a process there could read ([rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)).

## Prevention

- **Blocking install scripts is necessary but not sufficient.** This campaign, indexed-btree, WeaselBiscuit and PolinRider were all built around `npm v12`'s script-blocking default. Add a scanner that inspects package *code* for prototype/method-level payloads, and specifically for an encrypted blob decrypted by a runtime trigger. [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- **Verify the package an assistant names is the one you meant.** `mathmain`/`mathsbase`/`math-universe` next to `mathjs` is the slopsquatting shape — a plausible name, a real-looking repo, and download counts that were bought. [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- **Egress control on build and runtime hosts**: a math library that talks to an Ethereum RPC, Slack or Telegram is the detection. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Don't trust a download count as a trust signal** — a `0.0.1-security` stub out-pulling the library it impersonates proves the number was traffic. Check `api.npmjs.org/downloads/point/last-week/<pkg>` against dependent counts.

## Sources
- [JFrog Security Research — Equation of Compromise: Anatomy of a Live npm Supply-Chain Campaign](https://research.jfrog.com/post/equation-of-compromise/) — primary, 2026-09-21: 23 weaponised packages March–September 2026, the `lusolve` Pascal-matrix trigger and `scryptSync`/AES-256-GCM key derivation, the 14 Ethereum Sepolia/Base Sepolia C2 contracts and five operator wallets, the 30-repo GitHub Actions download-inflation farm and its WASM decoder MD5, the `event.js`/`graph.js` loader files and the license-string IOC, the "second stage is broken" note. Fetched 2026-09-23.
- [SafeDep — Why Does an npm Math Library Need an Encrypted Loader?](https://safedep.io/mathmain-encrypted-loader) — primary, 2026-09-17/18: the mathjs clone behaviour, the three headline packages and versions, the trigger mechanism, download figures 2026-09-12 → 09-18 (`mathmain` 605,157; `mathsbase` 1,923,059; `math-universe` 569,730), the publisher-email collision joining the cluster. Fetched 2026-09-23.
- [Hacker News discussion — "Why does mathmain need an encrypted loader?"](https://news.ycombinator.com/item?id=49791378) — 2026-09-22, 136 points: confirms JFrog cracked the password enabling the analysis and that npm removed the packages. Fetched 2026-09-23.
- npm registry / `api.npmjs.org`, fetched 2026-09-21 and 2026-09-23: `mathmain` `latest` → `0.0.1-security` (2026-09-21T19:48Z), last real version 1.0.0 (2026-09-17); `mathsbase` `0.0.1-security` (2026-09-21T20:05Z), last real 1.0.2 (2026-09-15); weekly downloads 2026-09-15 → 09-21 — `mathmain` 1,981,038; `mathsbase` 2,591,653; `math-universe` 2,482,574; the security stubs out-pull these because the count is inflated traffic, not installs.
