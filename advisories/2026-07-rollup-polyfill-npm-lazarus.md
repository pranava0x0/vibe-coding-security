---
id: 2026-07-rollup-polyfill-npm-lazarus
title: "Rollup polyfill impersonation — 6 npm packages deliver full RAT, tentatively linked to Lazarus (July 2026)"
date_disclosed: 2026-07-04
last_updated: 2026-07-04
severity: high
status: contained
ecosystems: [npm]
tools_affected: [rollup, rollup-plugin-polyfill-node]
tags: [supply-chain, typosquat, credential-theft, rat, npm, dprk]
---

## TL;DR

JFrog disclosed six malicious npm packages — led by **`rollup-packages-polyfill-core`** and **`rollup-runtime-polyfill-core`** — that impersonate the popular `rollup-plugin-polyfill-node` (~295,000 downloads/week) and drop a full cross-platform remote-access trojan. JFrog tentatively links the campaign to North Korea's **Lazarus** group but stops short of firm attribution. All six packages have been removed from npm.

## What happened

JFrog Security Research disclosed on **2026-06-30** (public reporting followed 2026-07-01 through 2026-07-04) that two lead packages — `rollup-packages-polyfill-core` and `rollup-runtime-polyfill-core` — copied the name and description of the legitimate, widely used `rollup-plugin-polyfill-node` build-tool plugin ([TechTimes](https://www.techtimes.com/articles/319672/20260704/north-koreas-lazarus-group-hid-full-rat-six-rollup-polyfill-npm-packages.htm), [The Hacker News](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html)). Once installed, the first-stage packages quietly pulled in four more packages disguised as unrelated utilities — **`swift-parse-stream`**, **`quirky-token`**, **`react-icon-svgs`**, and **`rollup-plugin-polyfill-connect`** — for six malicious packages total ([Aardwolf Security](https://aardwolfsecurity.com/npm-supply-chain-attack-rollup/)).

Notably, **the payload fires at import time, not install time** — a JSON object is fetched from a remote hosting service at runtime and its embedded payload executed, meaning npm's newer install-time defenses (`--ignore-scripts`, and the forthcoming npm v12 `allowScripts: off`) do not stop this vector on their own ([The Hacker News](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html)).

The final-stage malware is a comprehensive credential harvester and remote-access trojan targeting: browser credentials (Chrome, Edge, Brave, Opera), cryptocurrency wallets (MetaMask and related extensions by extension ID), SSH keys, AWS/Azure credentials, npm tokens, Git logins, **VS Code, Cursor, and Windsurf editor history**, `.env` files, and clipboard contents (tokens, seed phrases) — plus interactive remote terminal access on Windows systems ([Aardwolf Security](https://aardwolfsecurity.com/npm-supply-chain-attack-rollup/)).

JFrog researchers noted similarities to a separate, larger 108-package campaign from earlier in the year attributed to the same broader threat cluster, but "stop short of claiming certainty" on the Lazarus attribution ([TechTimes](https://www.techtimes.com/articles/319672/20260704/north-koreas-lazarus-group-hid-full-rat-six-rollup-polyfill-npm-packages.htm)) — treat the specific actor attribution as `unconfirmed` even though the campaign itself is well documented across independent outlets.

All six packages have been removed from the npm registry.

## Am I affected?

```bash
# Check your lockfile / node_modules for any of the six malicious packages
npm ls rollup-packages-polyfill-core rollup-runtime-polyfill-core swift-parse-stream quirky-token react-icon-svgs rollup-plugin-polyfill-connect 2>/dev/null

grep -E "rollup-packages-polyfill-core|rollup-runtime-polyfill-core|swift-parse-stream|quirky-token|react-icon-svgs|rollup-plugin-polyfill-connect" package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
```

You're at risk if you (or a dependency) installed any of the six packages above — note the deliberate typosquat of the legitimate `rollup-plugin-polyfill-node`, so double-check the exact package name before trusting an existing install.

## If you are affected

1. Remove the packages immediately and purge lockfile entries.
2. Treat the machine as fully compromised — the payload targets browser credentials, crypto wallets, SSH keys, cloud credentials, npm tokens, and editor history (VS Code/Cursor/Windsurf). Follow [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).
3. Rotate all cloud, npm, Git, and SSH credentials from a clean machine; treat browser-saved passwords and crypto wallet seed phrases as compromised per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Check for unauthorized remote-terminal activity if on Windows.

## Prevention

- Verify exact package names before installing build-tool plugins — typosquats of high-download packages (`rollup-plugin-polyfill-node` here) are a recurring pattern; see [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- Note that this payload triggers at **import time**, not install time — `--ignore-scripts` and npm v12's `allowScripts: off` reduce install-time risk but do not address this vector. See [prevention/npm-hardening.md](../prevention/npm-hardening.md) and [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- Pin dependency versions and review new/transitive dependencies pulled in by a plugin install, especially ones with generic-sounding names (`swift-parse-stream`, `quirky-token`).

## Sources

- [TechTimes — "North Korea's Lazarus Group Hid a Full RAT in Six Rollup Polyfill npm Packages"](https://www.techtimes.com/articles/319672/20260704/north-koreas-lazarus-group-hid-full-rat-six-rollup-polyfill-npm-packages.htm) — attribution caveat, timeline, discovery.
- [The Hacker News — "North Korea-Linked npm Packages Mimic Rollup Polyfills to Steal Developer Secrets"](https://thehackernews.com/2026/07/north-korea-linked-npm-packages-mimic.html) — attack mechanism (import-time trigger), scope of credential targeting.
- [Aardwolf Security — "npm Supply Chain Attack Hits Rollup Build Tools"](https://aardwolfsecurity.com/npm-supply-chain-attack-rollup/) — full package list, payload capability breakdown.
