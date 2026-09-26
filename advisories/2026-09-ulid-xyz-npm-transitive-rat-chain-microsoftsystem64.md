---
id: 2026-09-ulid-xyz-npm-transitive-rat-chain-microsoftsystem64
title: "ulid-xyz: a cross-platform RAT hidden three dependencies deep — 28 attacker-authored GitHub 'starter' repos depend on ioredis-xyz → redis-type-xyz → ulid-xyz, whose postinstall detaches a 467 KB Node implant that persists as 'MicrosoftSystem64' on Windows, macOS and Linux; the same implant shipped in js-logger-pack and terminal-logger-utils since April, exfiltrating to Hugging Face datasets; DPRK-linked per SafeDep, npm removed ulid-xyz 2026-08-25"
date_disclosed: 2026-09-01
last_updated: 2026-09-26
severity: high
status: contained
ecosystems: [npm, github, windows, macos, linux]
tools_affected: ["ulid-xyz (npm)", "redis-type-xyz (npm)", "ioredis-xyz (npm)", "index-ulid (npm)", "js-logger-pack / terminal-logger-utils / ts-logger-pack / pretty-logger-utils / pinno-loggers (npm)", "developers who cloned the attacker's 28 starter repositories"]
tags: [supply-chain, npm, typosquat, transitive-dependency, postinstall, rat, persistence, dprk, famous-chollima, contagious-interview, huggingface-exfil, ssh-keys, browser-credentials, github-lure-repos]
---

## TL;DR
SafeDep's 2026-09-01 analysis (surfaced by The Hacker News' 09-25 roundup) documents an npm delivery chain built so that **nobody ever types the malicious package's name**: the lure is one of **28 GitHub repositories** whose `package.json` depends on `ioredis-xyz`, which depends on `redis-type-xyz`, which as of `1.10.6` (2026-06-17 07:56 UTC) depends on **`ulid-xyz`** — a typosquat of `ulid`/`ulidx` whose `postinstall` launches a detached Node process that drops a **467 KB remote-access implant** persisting as **`MicrosoftSystem64`** (scheduled task + Run key on Windows, LaunchAgent on macOS, systemd user unit on Linux). The implant is the same one SafeDep pulled apart on 2026-05-28 from `js-logger-pack` and `terminal-logger-utils`: browser credentials from 15 families, 80+ wallet extensions, Telegram sessions, **SSH keys**, keystrokes, clipboard and periodic screenshots, **uploaded to attacker-controlled Hugging Face datasets**. SafeDep attributes the cluster to **FAMOUS CHOLLIMA / Contagious Interview** (DPRK) on persistence design, C2 ports, hosting and overlapping personas. **npm replaced `ulid-xyz` with a security-holding package on 2026-08-25**; the two relay packages are still published but now install nothing harmful because their dependency is gone. If any of these packages ever appeared in a lockfile on your machine, treat the host as fully compromised.

## What happened

The npm registry's own `time` field gives the sequence: `index-ulid` first (2026-06-15, later replaced with a security holder), `ioredis-xyz` created 2026-06-16, `redis-type-xyz@1.10.5` 2026-06-17 06:07 UTC (clean), `ulid-xyz` versions 2.12.1 → 3.2.2 published between 07:02 and 07:29 the same morning, `ioredis-xyz@5.11.2` adding the `redis-type-xyz` dependency at 07:37, and `redis-type-xyz@1.10.6` adding `ulid-xyz@^2.12.2` at 07:56 — the chain was armed in under two hours. Three more `ulid-xyz` versions followed on 2026-06-29. The `ulid-xyz` README even instructs users to `npm install index-ulid` and import from it, a second confusable name by the same author, so a developer checking "does this package look legitimate?" is steered to another attacker package. OSV's malicious-package entry ([MAL-2026-6672](https://osv.dev/vulnerability/MAL-2026-6672), published 2026-06-29, sourced from Amazon Inspector and SafeDep) lists all nine `ulid-xyz` versions as malicious.

The lure layer is what makes this a developer-targeting campaign rather than a typosquat waiting for typos: SafeDep found **28 attacker-created GitHub repositories** — "starter" and "boilerplate" projects — whose `package.json` pulls `ioredis-xyz`, so cloning the repo and running `npm install` is the whole infection path. That is the Contagious Interview playbook (a "take-home assignment" repository) with the payload moved from the repo into a third-level dependency, which also defeats the reviewer who reads the repo's own code and its direct dependencies.

Stage one is reconnaissance and remote access ("fingerprints the host, lets an operator read the file system, and then takes whatever the operator sends" — SafeDep); stage two is the credential stealer documented in May. That earlier analysis dates the implant's npm history to `js-logger-pack` (2026-04-01 → 04-20, first a WebSocket stealer, then a binary dropper), `terminal-logger-utils` (05-20/21), and `ts-logger-pack`, `pretty-logger-utils`, `pinno-loggers` (May), with earlier related packages `polymarket-validator` and `changelog-logger-utilities` (Feb–Mar). The Hugging Face accounts used as the drop (`jpeek998`, created 2026-05-15; `Lordplay`, disabled by Hugging Face) are named in that report; the npm publisher accounts SafeDep names are `jpeek*` and `toskypi`.

**Containment, from the registry:** `ulid-xyz`'s `latest` tag now points at `0.0.1-security` (published 2026-08-25 16:36 UTC) and all nine malicious versions are gone; `index-ulid` was replaced the same way. `ioredis-xyz@5.11.2` and `redis-type-xyz@2.1.1` remain on npm as of 2026-09-26, but an install of the armed `redis-type-xyz@1.10.6` now fails to resolve `ulid-xyz`. Weekly downloads for the three are 5 / 24 / 68 — small, and consistent with a lure-driven campaign rather than a typosquat harvesting traffic.

## Am I affected?

- Search every lockfile and `node_modules` on developer machines and CI for any of: `ulid-xyz`, `index-ulid`, `redis-type-xyz`, `ioredis-xyz`, `js-logger-pack`, `terminal-logger-utils`, `ts-logger-pack`, `pretty-logger-utils`, `pinno-loggers`, `polymarket-validator`, `changelog-logger-utilities`.

  ```bash
  grep -rlE '"(ulid-xyz|index-ulid|redis-type-xyz|ioredis-xyz|js-logger-pack|terminal-logger-utils|ts-logger-pack|pretty-logger-utils|pinno-loggers)"' \
    --include=package-lock.json --include=yarn.lock --include=pnpm-lock.yaml --include=package.json .
  ```
- Look for the persistence artefacts by name — **any of these present is a confirmed compromise signal**: a scheduled task or `HKCU\…\Run` value named `MicrosoftSystem64` (Windows); `~/Library/LaunchAgents/com.launchkeeper.MicrosoftSystem64.plist` (macOS); `~/.config/systemd/user/MicrosoftSystem64.service` or an XDG autostart `MicrosoftSystem64.desktop` (Linux); a running process named `MicrosoftSystem64`.
- Ask whether anyone on the team cloned a "starter" repository from a recruiter, a "client," or an unfamiliar GitHub account since June and ran `npm install` in it.

## If you are affected

1. **Treat the machine as fully compromised** (SafeDep's words) — the implant took SSH keys, browser sessions and keystrokes, and gave an operator a shell. Reimage rather than clean. → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
2. **Rotate from a clean device:** SSH keys, npm and GitHub tokens, cloud keys, browser-saved passwords, Telegram sessions; move any crypto held in a browser wallet. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md), [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).
3. Audit packages you published and repositories you pushed to while the implant was resident — the operator had your credentials.

## Prevention

- **Install with scripts disabled** (`npm config set ignore-scripts true`, or `--ignore-scripts` in CI) so a `postinstall` cannot detach a process; → [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- **Review the transitive tree, not the repo.** A recruiter's take-home repo is untrusted code: run it only in a disposable VM or container, and diff `npm ls --all` against what the README claims. → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md), [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Watch for `-xyz` / `-utils` / `-pack` suffixed clones of core libraries**; the same operator has cycled through logger, redis and ULID names. → [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- Egress control that flags uploads to Hugging Face dataset endpoints from developer hosts that have no ML workflow.

## Sources
- [SafeDep — A malicious npm package hidden three dependencies deep: the ulid-xyz delivery chain](https://safedep.io/ulid-xyz-transitive-dependency-delivery-chain/) — primary, 2026-09-01: the 28-repository lure layer, the `ioredis-xyz → redis-type-xyz → ulid-xyz` chain with UTC timestamps, the detached `postinstall`, the 467 KB implant, the `MicrosoftSystem64` persistence on three platforms, the FAMOUS CHOLLIMA attribution, npm's 2026-08-25 removal. Fetched 2026-09-26.
- [SafeDep — Inside MicrosoftSystem64: A Supply Chain RAT Exfiltrating to HuggingFace](https://safedep.io/microsoftsystem64-binary-payload-analysis/) — primary, 2026-05-28: the April–May package lineage (`js-logger-pack`, `terminal-logger-utils`, …), the stolen-data categories, the Hugging Face dataset drop and account names, the persistence paths and process name, the "treat it as a full compromise" guidance. Fetched 2026-09-26.
- [OSV — MAL-2026-6672 (npm/ulid-xyz)](https://osv.dev/vulnerability/MAL-2026-6672) — the OpenSSF malicious-packages record, published 2026-06-29, modified 2026-08-26, sourced from Amazon Inspector and SafeDep; lists the nine affected versions. Independent registry-side confirmation. Fetched 2026-09-26.
- [npm registry — `ulid-xyz`](https://registry.npmjs.org/ulid-xyz), [`index-ulid`](https://registry.npmjs.org/index-ulid), [`redis-type-xyz`](https://registry.npmjs.org/redis-type-xyz), [`ioredis-xyz`](https://registry.npmjs.org/ioredis-xyz) — `time` fields and `dist-tags` queried 2026-09-26: the 2026-06-15/16/17 publish sequence, the 2026-08-25 `0.0.1-security` replacement, the relays still published. [api.npmjs.org last-week downloads](https://api.npmjs.org/downloads/point/last-week/ulid-xyz): 5 / 24 / 68 for the three packages (2026-09-18 → 09-24).
- [The Hacker News — ThreatsDay: AI Search Poisoning, AI Coding Tool Leaking Repos, One-Click Code Execution and 13 More Stories](https://thehackernews.com/2026/09/threatsday-ai-search-poisoning-ai.html) — 2026-09-25 roundup item that surfaced the SafeDep chain report; restates it, no independent research. Fetched 2026-09-26.
- Command-server addresses and the attacker's Hugging Face URLs are in the SafeDep reports and deliberately not reproduced here.
- Related in this corpus: [Joyfill / DevPopper npm RAT](2026-07-joyfill-npm-devpopper-rat.md) and [PolinRider](2026-03-polinrider-multi-ecosystem-dprk-campaign.md) — the same DPRK developer-targeting family; [Rust maintainers' fake-interview campaign](2026-09-rust-maintainers-fake-interview-video-call-campaign.md) — the same lure against crate owners.
