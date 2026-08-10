---
id: 2026-08-flooding-dropper-wel1dropper-npm
title: "Flooding Dropper — ~850 npm packages deliver a cross-platform RAT/infostealer via require()-time execution, targets Russian fintech developers"
date_disclosed: 2026-08-05
last_updated: 2026-08-05
severity: high
status: contained
ecosystems: [npm]
tools_affected: []
tags: [supply-chain, dependency-confusion, cross-platform-rat, dns-exfiltration, cloudflare-workers, require-time-execution]
---

## TL;DR
Sonatype tracked (as **sonatype-2026-005660**) a campaign it calls **"Flooding Dropper"** — roughly **846 malicious npm packages**, published across many disposable throwaway accounts (a handful of packages per account, to slow takedown), using AI-generated typosquat-style names built around fintech/"buy-now-pay-later" terms (`bigops`, `bnpl`) that appear to target **Russian financial-services developers**. Unlike most campaigns this repo tracks, the payload doesn't run at install time via a lifecycle hook or `binding.gyp` — the package's README instructs the developer to load it via `require()`, and that `require()` call itself triggers a downloader (**WEL1DROPPER**) that fetches a platform-specific binary RAT/infostealer for Windows, Linux, or macOS. Discovered and published **2026-08-05**; may be an evolution of the April 2026 "Moika" dependency-confusion campaign.

## What happened
Rather than a single publisher account or a coordinated few-minute burst, Flooding Dropper's operators automated npm account and package creation at scale: **846 packages** distributed thinly across many accounts, combining terms like `bigops` and `bnpl` (buy-now-pay-later, a fintech term) with other words — e.g. `bigops-api`, `dolyame-boxy-desktop-bnpl-card-gallery` — many sharing version numbers in the `35.x.y` range. This pattern, and the fintech-adjacent naming, points toward developers integrating with Russian payment/BNPL platforms as the intended targets, and researchers note it may be a continuation or evolution of the **April 2026 "Moika" dependency-confusion campaign**.

**Delivery mechanism — require()-time execution, not install-time.** Most supply-chain campaigns this repo tracks fire at `npm install` time via a `preinstall`/`postinstall` lifecycle hook or a `binding.gyp` native-build step (both of which some mitigations, like `--ignore-scripts`, can block or reduce). Flooding Dropper instead ships a README that instructs the developer to load the package via `require()` in their own code — and it's that `require()` call, at normal runtime, that triggers **WEL1DROPPER**, a downloader that:
1. Identifies the host OS and processor architecture.
2. Fetches a platform-specific binary payload from one of three **Cloudflare Workers** hosts: `oob-worker.cf103-070.workers.dev`, `oob-worker.cf102-baf.workers.dev`, `oob-worker.cf99-9b3.workers.dev`.
3. If the HTTPS download fails, falls back to **DNS TXT record** exfiltration/staging from `wel1[.]ru`, using platform-specific subdomains (`sdk.dl`, `ext.dl`, `pkg.dl`, `net.dl`).
4. Executes the fetched payload as a detached background process.

The **Windows binary** includes anti-analysis evasion (Event Tracing for Windows patching, VM/debugger detection) and persistence via Registry Run keys and scheduled tasks — a materially more sophisticated payload than the typical single-stage JavaScript credential grabber this repo tracks in npm typosquat campaigns.

## Am I affected?
```bash
# Search your lockfiles for the naming pattern this campaign uses
grep -riE '"(bigops|bnpl|dolyame)[-a-z0-9]*":' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Check for outbound DNS activity to the campaign's exfil/staging domain
# (run against your DNS logs, not locally)
# wel1[.]ru and its subdomains: sdk.dl, ext.dl, pkg.dl, net.dl

# Look for the Cloudflare Workers staging hosts in outbound HTTP logs
# oob-worker.cf103-070.workers.dev
# oob-worker.cf102-baf.workers.dev
# oob-worker.cf99-9b3.workers.dev
```
You're at risk if you installed any package matching the naming pattern above from npm around or after **2026-08-05**, or if any of your dependencies' READMEs instructed you to `require()` a specific unfamiliar sub-package by name.

## If you are affected
1. Remove any matching package immediately and check whether it was actually `require()`'d/imported in your codebase (not just present in `node_modules`) — the payload only fires on that call, unlike install-time hooks.
2. If it was imported: treat the host as compromised. Check for the Windows persistence indicators (Registry Run keys, scheduled tasks) if on Windows; rebuild rather than clean in place.
3. Rotate credentials accessible from the affected machine.
4. Block the Cloudflare Workers hosts and `wel1[.]ru` (and subdomains) at your network egress.

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
- `--ignore-scripts` and npm v12's `allowScripts: off` don't help here — this campaign's payload fires on ordinary `require()`/`import`, the same "import-time execution, no install-time footprint" primitive this repo already tracks for the Rollup polyfill impersonation and Joyfill npm compromises. Vet a package's actual source before importing it, not just its `package.json` scripts.
- Be suspicious of any package README that specifically instructs you to `require()` a named sub-module rather than just documenting the package's normal public API.

## Sources
- [Sonatype — Flooding Dropper Hits npm With 850 Malicious Packages](https://www.sonatype.com/blog/flooding-dropper-hits-npm-with-850-malicious-packages) — primary technical writeup: package count, naming pattern, delivery mechanism, IOC domains.
- [The Hacker News — Nearly 800 Malicious npm Packages Deliver Cross-Platform RAT and Infostealer](https://thehackernews.com/2026/08/nearly-800-malicious-npm-packages.html) — independent confirmation, Windows binary evasion/persistence detail, researcher attribution (Paul McCarty / OpenSourceMalware), Moika-campaign lineage note.
