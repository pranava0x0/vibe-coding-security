---
id: 2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader
title: "MALFEX: one operator's npm packages since 2023 (40,767 downloads) deliver a Windows RAT and stealer; loader moved into a native addon, imgdecode 1.0.3 live 2026-10-13"
date_disclosed: 2026-10-05
last_updated: 2026-10-17
severity: high
status: active
ecosystems: [npm, windows, nodejs]
tools_affected: ["function-flag 1.7.3, 2.3.5 through 2.3.9, 3.0.0, 4.0.0 (npm security holding since 2026-10-08)", "function-color 1.0.0 and 1.7.3 (depends on function-flag; holding since 2026-10-07)", "cdn-img-fetch 1.0.0 through 1.0.3 (holding since 2026-10-08)", "img-to-native and native-runner 1.0.0 through 1.0.3 (seized by npm)", "tlxbnhd, tldriver 0.0.1 and mxdriver 0.0.1, 0.0.2 (unpublished)", "imgdecode 1.0.0 through 1.0.3 (live on npm 2026-10-13; native Windows addon loader)", "Windows developer machines that installed any of them; CI with redirected output is not triggered by the addon variant"]
tags: [npm, malware, supply-chain, windows, rat, infostealer, native-addon, n-api, no-install-script, discord, browser-credentials, telegram, crypto-wallet, long-running, single-operator, checkmarx, cloudsek, safedep, active]
---

## TL;DR
Checkmarx (2026-10-05) and CloudSEK, who named it, describe MALFEX as a single operator's npm campaign running since 2023-08-06: twelve packages, eight malicious, 40,767 downloads by 2026-10-01, all payloads Windows-only. Three delivery paths share one actor and no infrastructure: loaders for the open-source Go remote access trojan Overlord that run during `npm install`; a chain through `img-to-native` and `native-runner` that fetches a Go executable which installs movinlike, a Node.js stealer for Discord tokens, browser cookies and saved logins, Telegram Desktop sessions and cryptocurrency wallets; and a downloader inside every malicious `function-flag` version, the longest-running part, which accounts for 37,419 of the downloads and had no advisory when the report ran. On 2026-10-13 SafeDep reported the next step: after npm removed the JavaScript loaders, the operator published `imgdecode` (1.0.0 on 2026-09-30, 1.0.3 on 2026-10-11) whose nine-line JavaScript loads a compiled Windows DLL from a prebuilt N-API addon; the addon runs in module initialisation, needs no install script, and only when standard output is an interactive Windows console, so `--ignore-scripts` does nothing and CI never sees it. The registry on 2026-10-13: `function-flag`, `function-color` and `cdn-img-fetch` have been replaced by npm's `0.0.1-security` holding versions since 2026-10-07 and 10-08, `imgdecode` 1.0.3 is still `latest` under a publisher account carrying the MALFEX name, with 247 downloads in the week of 2026-10-05. No widely used package depends on any of these names; the risk is a direct or transitive install on a Windows machine. A Windows host that ran `npm install` on one of the eight install-hook packages with scripts enabled is compromised; for `imgdecode`, only a host that loaded the module in an interactive Windows console is, and a lockfile, cache or unused install is exposure to remove.

## What happened

### The campaign as Checkmarx and CloudSEK describe it

Checkmarx's post (Anurag Chevendra and Pavan Gudimalla, 2026-10-05) traces the operator to a first publish on 2023-08-06 and counts twelve packages, eight malicious and four benign cover packages, across five publisher accounts carrying the MALFEX name. CloudSEK coined the name and did the attribution: Portuguese-language content, commit time zones and a shared handle, with the caution that this does not make Brazil the target; second-stage targeting is opportunistic. SecurityWeek (2026-10-06) and The Hacker News (2026-10-07) carry both firms' findings; Checkmarx's "anyone who installs the stealer becomes a target" is the targeting statement.

| Package | Malicious versions | Path | Registry state (Checkmarx, 2026-10-01) | Registry state (this sweep, 2026-10-13) |
|---|---|---|---|---|
| function-flag | 1.7.3, 2.3.5 to 2.3.9, 3.0.0, 4.0.0 | downloader; 1.7.3 triggers on an ASCII-art font and runs a hidden Node executable | live, 37,419 downloads, no advisory | `0.0.1-security` holding since 2026-10-08; malicious versions were published 2024-07-01 to 2025-08-04 |
| function-color | 1.0.0, 1.7.3 | no payload; depends on function-flag | live, 300 downloads, no advisory | holding since 2026-10-07 |
| cdn-img-fetch | 1.0.0 to 1.0.3 | fetches and runs a Go executable | live, 643 downloads; advisory covered 1.0.0 and 1.0.1 only | holding since 2026-10-08; 1.0.4 published 2026-09-30 before the hold |
| img-to-native, native-runner | 1.0.0 to 1.0.3 | Go executable, then the movinlike stealer | seized by npm | seized |
| tlxbnhd, tldriver, mxdriver | 0.0.1; 0.0.1, 0.0.2 | Overlord RAT loaders, run at `npm install` | unpublished | unpublished |
| imgdecode | 1.0.0 to 1.0.3 | native N-API addon loader (SafeDep, 2026-10-13) | not in the Checkmarx report | live; 1.0.0 on 2026-09-30, 1.0.3 on 2026-10-11, `latest` |

Download counts are npm's public statistics as Checkmarx quoted them on 2026-10-01 and measure registry reach, not infections; some `function-flag` downloads came through `function-color` as a dependency. The holding packages' own download counts (991 for `function-flag` in the week of 2026-10-05) are installs of the empty security stub.

### The payloads, as credential categories

- **Overlord**: an open-source Go RAT with screen capture, keylogging, clipboard capture, active-window monitoring, file search, a remote shell and a hidden desktop; Checkmarx calls it monitoring and control rather than bulk theft, but keylogging and clipboard capture reach every credential typed. The Hacker News notes it resolves its command server from blockchain transactions, the pattern of [indexed-btree](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md) and [Reactime](2026-10-reactime-repository-compromise-vscode-folder-open-task-polinrider.md).
- **movinlike**: a Node.js stealer for Discord authentication tokens and account details across eight Discord clients, cookies and saved logins from seven browsers, Telegram Desktop session data and cryptocurrency wallet data.
- **The function-flag downloader**: fetches and runs an executable Checkmarx has not recovered for 1.7.3; the install completes even when the download fails and fails silently on macOS and Linux.

### The October change: a loader with no script and no JavaScript to read

SafeDep's 2026-10-13 post: `imgdecode` ships a prebuilt Windows x64 `.node` addon; its JavaScript is nine lines that load the addon, and the addon's N-API initialisation function runs the loader, which downloads encrypted shellcode, decrypts it and injects it into a new process. The operator published 1.0.3 on 2026-10-11, six days after Checkmarx's report, having replaced each removed JavaScript loader with a new package first. Two properties matter for defenders: no install script is involved, so install-time script blocking and `--ignore-scripts` do not apply, the addon runs when the package is loaded; and it runs only when standard output is an interactive Windows console, so a CI job, a sandbox with redirected output or an automated scanner does not trigger it. SafeDep did not recover the final payload and says the link from the native loader to the MALFEX stealer is an inference from the shared operator and infrastructure. The package was still on npm on 2026-10-13, and the registry agreed when this sweep checked.

### Why the advisory gaps are the story

Checkmarx's point is not the download count. `function-flag` was malicious from July 2025, had 37,000 downloads and no advisory until October 2026; `cdn-img-fetch`'s advisory covered half its malicious versions; three packages were installable on 2026-10-01, a week after the report went to the registry. A dependency scanner that keys on advisories would have said nothing for fourteen months. The holding versions arrived on 2026-10-07 and 10-08, after the press cycle.

## Am I affected?

Only Windows machines run any of it, but a lockfile pin survives the removal. A hit below means the package was present; whether its code ran depends on the package (see the first step under "If you are affected").

```bash
# Direct or transitive presence in a project
npm ls function-flag function-color cdn-img-fetch img-to-native native-runner tlxbnhd tldriver mxdriver imgdecode 2>/dev/null
grep -nE '"(function-flag|function-color|cdn-img-fetch|img-to-native|native-runner|tlxbnhd|tldriver|mxdriver|imgdecode)"' package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
# Caches and private registry mirrors keep removed tarballs
ls ~/.npm/_cacache 2>/dev/null | head -1 && grep -rl 'imgdecode\|function-flag' ~/.npm/_cacache/index-v5 2>/dev/null | head
```

```powershell
# On a Windows machine that installed one: the native addon ships under prebuilds
Get-ChildItem -Path . -Recurse -Filter imgdecode.node -ErrorAction SilentlyContinue | Select-Object FullName
# Persistence Checkmarx describes: a backdated scheduled task and copied loader directories
Get-ScheduledTask | Where-Object { $_.Date -lt (Get-Date).AddYears(-1) -and $_.TaskPath -notlike '\Microsoft\*' } | Select-Object TaskName, Date, TaskPath
```

## If you are affected

1. **Decide which package you had, because the trigger differs.** For the install-hook packages (`tlxbnhd`, `tldriver`, `mxdriver`, `img-to-native`, `native-runner`, `function-flag`, `function-color`, `cdn-img-fetch`), an `npm install` on a Windows host with lifecycle scripts enabled ran the loader, so treat the host as compromised even if the package is gone. For `imgdecode`, installation alone did nothing: the addon runs only when the module is loaded (`require`/`import`) and stdout is an interactive Windows console. A lockfile or cache hit on `imgdecode` with no code that loads it, or loads it only under redirected output in CI, is exposure to remove, not a compromise. Where it was loaded in a terminal session, or you cannot tell, treat the host as compromised. Then isolate it, preserve logs, and rebuild rather than clean: [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md), [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
2. **Rotate from a clean machine**: Discord tokens and passwords, every browser-saved login, Telegram sessions (end them all), wallets (move funds to new keys), and because Overlord keylogs, everything typed on the host since the install, including npm, GitHub, cloud and AI-provider keys: [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
3. **Purge the names** from private registries, proxies and caches, and block all nine at the proxy, pairs included; blocking one half of `function-color` and `function-flag` leaves the other.

## Prevention

- **Install-script blocking is not a control against module-load payloads.** The 2025 AsyncAPI and indexed-btree cases ran at load time; `imgdecode` runs at load time from native code. Vet what you add, not only how it installs: [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md), [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- **A prebuilt native addon in a tiny package is a tell.** Nine lines of JavaScript plus a compiled `.node` for one platform, from a publisher with no history, is the shape; treat `prebuilds/` directories in new dependencies as binaries you are executing.
- **Advisory feeds lag the registry by months.** Fourteen months for `function-flag`. Pair `npm audit` with a reputation or behaviour signal, and treat a `0.0.1-security` holding version in your lockfile's history as a notice that you installed malware earlier: [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- **Interactive-console-only triggers defeat sandboxes that redirect output.** When you detonate a package, give it a TTY or you will see nothing.

**Update 2026-10-17.** The Hacker News covered the `imgdecode` step on 2026-10-17, crediting SafeDep for the analysis and Checkmarx and CloudSEK for the campaign; it adds a consolidated takedown-and-replace timeline (`cdn-img-fetch` removed 10-08, `img-to-native` and `native-runner` removed 09-28 and replaced by `imgbundle` and `runhelper` on 09-30, themselves removed 10-07 and the same day) and puts `imgdecode` at about 979 downloads with every other package in the chain gone; it adds no independent analysis of the loader. The registry on 2026-10-17: `imgdecode` 1.0.3 is still `latest`, no version has been published since 2026-10-11, and no security holding version exists.

## Sources
- [Checkmarx Zero — MALFEX npm malware campaign: three payloads and an adversary that signs their work](https://checkmarx.com/zero-post/malfex-npm-malware-campaign-three-payloads-and-an-adversary-that-signs-their-work/) — fetched 2026-10-13 (summary only, indicators omitted): 2026-10-05, Anurag Chevendra and Pavan Gudimalla; the 2023-08-06 start, twelve packages and eight malicious, the five publisher accounts, the version table, the download table as of 2026-10-01, the three payload families and their credential categories, the live-package and advisory-gap statements, the remediation list.
- [SafeDep — MALFEX Moves Its npm Loader into a Native Windows DLL](https://safedep.io/malfex-imgdecode-npm-native-addon-loader) — fetched 2026-10-13 with indicators stripped: `imgdecode` 1.0.0 to 1.0.3, the nine-line JavaScript and the prebuilt N-API addon, initialisation-time execution with no install script, the interactive-console condition, the 2026-10-11 publish six days after the Checkmarx report, the replacement-package timeline, the "still available on npm on 2026-10-13" statement, and the inference caveat on the final payload.
- [SecurityWeek — Long-Running npm Malware Campaign Accumulates 40,000 Downloads](https://www.securityweek.com/long-running-npm-malware-campaign-accumulates-40000-downloads/) — fetched 2026-10-13: 2026-10-06, Ionut Arghire; the three independent delivery paths, the macOS and Linux silent failure, the OSV coverage of six packages and the two-of-four cdn-img-fetch gap, the three packages still installable on 2026-10-01, the no-targeting quote.
- [The Hacker News — Eight Malicious npm Packages Downloaded 40,767 Times Deliver Overlord RAT and Stealer](https://thehackernews.com/2026/10/eight-malicious-npm-packages-downloaded.html) — fetched 2026-10-13: 2026-10-07; CloudSEK's naming and attribution with its Brazil caveat, Checkmarx's payload analysis, the eight Discord clients and seven browsers, the blockchain command-server resolution for Overlord, function-flag's July 2024 first publish and 2025-08-04 last version.
- Registries, checked 2026-10-13: `npm view <pkg> time` for `function-flag` (malicious versions 2024-07-01 to 2025-08-04; `0.0.0-stage` and `0.0.1-security` on 2026-10-08), `function-color` (holding 2026-10-07), `cdn-img-fetch` (1.0.0 to 1.0.4 between 2026-09-26 and 09-30; holding 2026-10-08), `imgdecode` (1.0.0 to 1.0.2 on 2026-09-30 and 10-01, 1.0.3 on 2026-10-11, `latest`, maintainer account carrying the MALFEX name); `api.npmjs.org` last-week downloads for the week of 2026-10-05 (`imgdecode` 247; the holding stubs 991, 602 and 730).
- Related in this corpus: [indexed-btree](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md) (runtime payload, no install hook), [AsyncAPI](2026-07-asyncapi-miasma-npm-github-actions.md) (module-load execution), [Reactime](2026-10-reactime-repository-compromise-vscode-folder-open-task-polinrider.md) (blockchain-resolved server), [Operation Navy Ghost](2026-06-operation-navy-ghost-pyrogram.md) (a long-running single-operator registry campaign on PyPI).
- [The Hacker News — MALFEX npm Package 'imgdecode' Hides Shellcode Loader in Windows Native Addon](https://thehackernews.com/2026/10/malfex-npm-package-imgdecode-hides.html) — fetched 2026-10-17 at defender altitude: SafeDep credited, the eight-package timeline with the `imgbundle` and `runhelper` replacements, the 979-download figure, the on-`require` note for the stealer chain. `npm view imgdecode time` re-run 2026-10-17: 1.0.3 on 2026-10-11 is the newest version and `latest`.
