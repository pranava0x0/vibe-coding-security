---
id: 2026-07-joyfill-npm-devpopper-rat
title: "Compromised Joyfill npm beta packages ship an import-time DEV#POPPER RAT with blockchain-resolved C2"
date_disclosed: 2026-07-28
last_updated: 2026-07-28
severity: high
status: active
ecosystems: [npm]
tools_affected: ["@joyfill/layouts", "@joyfill/components"]
tags: [supply-chain, rat, blockchain-c2, import-time-execution, devpopper, credential-theft, clipboard-theft]
---

## TL;DR

Two beta releases of the **Joyfill** npm packages — `@joyfill/layouts@0.1.2-2773.beta.0` and `@joyfill/components@4.0.0-rc24-2773-beta.4`, published minutes apart on **2026-07-28** — contained a **DEV#POPPER**-family remote access trojan that fires on **import** (not `npm install`), so `--ignore-scripts` gives no protection. The implant resolves its second-stage payload through **Tron, Aptos, and BNB Smart Chain transactions** and, once live, gives an operator shell execution, clipboard theft, and file access, plus a companion infostealer variant that harvests Windows Credential Manager, browser data, crypto-wallet extensions, Git credentials, and VS Code storage.

## What happened

On **2026-07-28**, a malicious actor published beta versions of two legitimate Joyfill packages — `@joyfill/layouts` (versions `0.1.2-2773.beta.0/1/2`) and `@joyfill/components` (versions `4.0.0-rc24-2773-beta.4/5/6`) — each carrying roughly **16,000 weekly downloads** on their stable release lines. Both malicious beta versions were published by the same npm publisher identity within about nine minutes of each other, using Node.js 18.20.0 and npm 10.5.0 ([Socket](https://socket.dev/blog/joyfill-npm-beta-releases-compromised)).

**Execution trigger:** unlike most npm supply-chain payloads, this implant does **not** rely on a `preinstall`/`postinstall` lifecycle script. It triggers when the package is **imported** — when Node.js loads the CommonJS entry point — which means dependency-scanning tools and `npm install --ignore-scripts` policies that only guard install-time hooks do not stop it ([The Hacker News](https://thehackernews.com/2026/07/two-compromised-joyfill-npm-packages.html)).

**C2 mechanism:** the implant resolves its encrypted second-stage payload through live blockchain transactions — querying **Tron and Aptos** addresses, then retrieving and XOR-decrypting the payload from a **BNB Smart Chain (BSC)** transaction — with a direct-IP fallback (`166.88.134.62`, `23.27.13.43`) for secondary payload delivery. Blockchain-resolved C2 is resilient to conventional domain/IP takedowns, the same rationale seen in other 2026 campaigns this repo tracks (Solana-memo and Ethereum-smart-contract C2).

**Capabilities:** the recovered RAT supports interactive remote-control sessions over Socket.IO, arbitrary JavaScript/shell execution, file upload and modification, clipboard exfiltration (via PowerShell on Windows, `pbpaste` on macOS, `xclip`/`xsel` on Linux), and persistence via injection into developer tooling — VS Code, Discord Desktop, GitHub Desktop, and the npm CLI itself. A companion Python infostealer variant additionally targets environment/host data, Windows Credential Manager, Linux Secret Service, Chromium/Firefox browser data, crypto-wallet browser extensions, Git credentials, GitHub CLI config, and VS Code storage.

**Attribution:** both Socket and The Hacker News identify the malware family as **DEV#POPPER**, with loader infrastructure overlapping the **PolinRider** cluster this repo already tracks ([2026-03-polinrider-multi-ecosystem-dprk-campaign.md](2026-03-polinrider-multi-ecosystem-dprk-campaign.md)) and a possible link to the North Korea-linked **Contagious Interview** operation. Socket is explicit that this is a **family/infrastructure assessment based on code overlap, not a confirmed attribution of the Joyfill compromise to a specific group** — treat the PolinRider/DPRK link as probable but unconfirmed rather than established fact.

**Status:** as of publication, no patched/clean version had been released for the affected beta lines, and package-removal status was not explicitly confirmed by either source.

## Am I affected?

```bash
# Check for the exact malicious beta versions in your lockfile
grep -E '"@joyfill/(layouts|components)"' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
npm ls @joyfill/layouts @joyfill/components 2>/dev/null
```

You're affected if you installed:
- `@joyfill/layouts` version `0.1.2-2773.beta.0`, `.beta.1`, or `.beta.2`
- `@joyfill/components` version `4.0.0-rc24-2773-beta.4`, `.beta.5`, or `.beta.6`

Because the payload triggers on import rather than install, simply having the package in `node_modules` without ever importing it is lower-risk — but any build, test, or dev-server run that imports either package should be treated as a potential compromise.

## If you are affected

1. Treat the machine as compromised — this implant has clipboard, file, and shell access. Follow [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) and [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).
2. Rotate all credentials reachable from that machine, especially Git/GitHub CLI tokens, VS Code stored secrets, and any crypto wallet browser extensions — per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) and [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).
3. Remove the affected beta versions and pin to a known-clean stable release.

## Prevention

- `--ignore-scripts` does not stop import-time payloads — this is now a recurring evasion technique (see also the [Rollup polyfill impersonation](2026-07-rollup-polyfill-npm-lazarus.md) and [jscrambler compromise](2026-07-jscrambler-npm-preinstall-infostealer.md) advisories). Vet beta/prerelease versions with the same scrutiny as stable ones — beta channels are a common place for a compromised publish to hide in plain sight.
- Watch for blockchain-resolved C2 (Tron/Aptos/BSC transaction queries) as an emerging IOC pattern distinct from disposable-tunnel or AI-vendor-host camouflage C2.
- See [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) and [prevention/npm-hardening.md](../prevention/npm-hardening.md).

## Sources

- [Socket — "Distributed npm Package Cluster Delivers Cross-Platform RAT"](https://socket.dev/blog/joyfill-npm-beta-releases-compromised) — primary technical writeup, published 2026-07-28: exact package/version list, publish timestamps, download counts, capability breakdown, C2 mechanism, explicit attribution caveat.
- [The Hacker News — "Two Compromised Joyfill npm Packages"](https://thehackernews.com/2026/07/two-compromised-joyfill-npm-packages.html) — independent corroboration, published 2026-07-29: import-time trigger detail, DEV#POPPER/PolinRider/Contagious Interview attribution framing.
