---
id: 2026-09-weaselbiscuit-npm-chrome-extension-storage-stealer
title: "WeaselBiscuit — 13–14 npm packages published 2026-09-12 → 09-16 (`process-tailwind`, `engin1`, six `@biz44/id*-client` packages…) fire on import, pull a Base64 second stage from a JSON dead-drop into memory, and harvest Chrome extension storage (wallet state) on Windows, macOS and Linux; OpenSourceMalware assesses a stripped-down BeaverTail/OtterCookie descendant, DPRK attribution low-to-moderate"
date_disclosed: 2026-09-17
last_updated: 2026-09-18
severity: medium
status: contained
ecosystems: [npm, chrome, windows, macos, linux]
tools_affected: ["any project that installed process-tailwind, engin1, id79-client, process-lhpm, process-mite, swnwall, @biz44/id10-client, @biz44/id12-client, @biz44/id44-client, @biz44/id79-client, @biz44/id95-client, @biz44/id99-client, @biz44/process-runtime-utils or @biz44/runtime-utils", "Chrome/Chromium profiles with wallet or credential extensions on the same machine"]
tags: [supply-chain, npm, infostealer, import-time-execution, dead-drop, chrome-extensions, crypto-wallets, dprk-suspected, contained]
---

## TL;DR
OpenSourceMalware (Paul McCarty, Jenn Gile; 2026-09-17) found a small campaign of npm packages — The Hacker News lists **13**, the primary report **14** (it includes `swnwall`) — published between **2026-09-12 and 2026-09-16** under names like **`process-tailwind`** (v1.1.99), **`engin1`** (v1.3.99), `process-lhpm`, `process-mite`, `id79-client` and six scoped **`@biz44/id<NN>-client`** packages. Each **runs on `import`**, not on install: an `initialize()` call spawns a detached Node process that fetches a Base64 payload from an **Npoint.io JSON dead-drop**, decodes it and executes it via dynamic function instantiation, "ensuring the malicious code never touches disk." The stealer profiles the host and copies **Chrome extension storage directories** — where wallet extensions keep signing state — across Windows, macOS and Linux, with operator-gated clipboard logging and Windows keystroke capture; campaign ids 10/12/44/79/95/99 are baked into the package names. Gile: "a stripped down stealer that borrows several functions from DPRK's BeaverTail and OtterCookie, but is much smaller." OSM calls the DPRK link "a working investigative hypothesis, not a conclusion." All checked packages now return **404 from the npm registry** (2026-09-18). Small blast radius, but two details matter for this audience: `process-tailwind` is a name an assistant could plausibly suggest, and an **import-time** payload defeats `ignore-scripts`.

## What happened

**Packages (OSM's list, versions where given):** `process-tailwind` 1.1.99, `engin1` 1.3.99, `swnwall` 1.2.10, `id79-client`, `process-lhpm`, `process-mite`, `@biz44/id10-client`, `@biz44/id12-client`, `@biz44/id44-client`, `@biz44/id79-client`, `@biz44/id95-client`, `@biz44/id99-client`, `@biz44/process-runtime-utils`, `@biz44/runtime-utils`. Neither source gives download counts. This sweep queried the registry for eight of them; every one returned `{"error":"Not found"}` — removed rather than replaced with the usual `0.0.1-security` holder, so no takedown timestamps are available.

**Two-stage loader.** THN's description: importing the package triggers `loader.js`, which "retrieves the primary payload from an Npoint dead drop for in-memory execution," and resolves its command server through a second Npoint URL. OSM: on import the package "automatically call[s] `initialize()`," launching a detached Node.js process that fetches Base64 from the dead-drop URLs, decodes it, and runs it through dynamic function instantiation. Six distinct Npoint resolver URLs and one C2 endpoint were recovered (an IP with a non-standard port; not reproduced here). The payload's SHA-256 is `7b15605f23b131b3eeea57e031ae7cb32fc4b78c7bbb2025aa7a561ea5ae5159`.

**What it takes.** Chrome extension storage on all three desktop OSes ("wallet extension data and signing state"); host reconnaissance (hostname, OS, CPU, RAM, IPs, geolocation via public IP-lookup services); clipboard contents and Windows keystrokes when the operator enables them. OSM notes what is *absent*: "No wallet-draining code, no hardcoded wallet extension ID list" — it copies the storage wholesale and lets the operator sort it out, which also means credential-manager and session-holding extensions are in scope, not only wallets.

**Lineage and attribution.** Overlaps with BeaverTail/OtterCookie (the Contagious Interview toolset tracked in [PolinRider](2026-03-polinrider-multi-ecosystem-dprk-campaign.md)): Node.js delivery, extension-storage theft, native clipboard and keylogging, and "use of lightweight external configuration to decouple the loader from C2 infrastructure." Divergences: no Socket.IO/WebSocket, no screenshots, no explicit wallet ids, no Python second stage. OSM rates the overlap "behavioral, not dispositive" and its DPRK attribution "low to moderate," resting on the Npoint.io dead-drop habit seen in prior DPRK samples, nested IP/geolocation lookups, and numeric campaign markers resembling the PolinRider cluster — "no exclusive infrastructure or shared code recovered."

**Why it is here despite the size.** Import-time execution is the [rollup-polyfill](2026-07-rollup-polyfill-npm-lazarus.md) lesson again: `--ignore-scripts` does nothing, the first `require()` does. And the names — `process-tailwind`, `runtime-utils`, `process-runtime-utils` — sit in the space where slopsquatting lives; a developer asking an assistant "what package handles Tailwind process config" could be handed one.

## Am I affected?

```bash
grep -E 'process-tailwind|engin1|swnwall|id79-client|process-lhpm|process-mite|@biz44/' package-lock.json yarn.lock pnpm-lock.yaml package.json 2>/dev/null
ls node_modules/@biz44 node_modules/process-tailwind node_modules/engin1 2>/dev/null
# The second-stage hash, if you capture Node's in-memory payloads or have EDR file/script telemetry:
# 7b15605f23b131b3eeea57e031ae7cb32fc4b78c7bbb2025aa7a561ea5ae5159
# Outbound connections from node to npoint.io JSON endpoints from a build or dev host are the network signal.
```

## If you are affected

- Assume every Chrome profile's extension storage on that machine was copied: move wallet funds to fresh keys, revoke sessions held by password-manager and SSO extensions, and rotate anything the clipboard or keystrokes could have carried. [`playbooks/if-you-installed-a-bad-npm-package.md`](../playbooks/if-you-installed-a-bad-npm-package.md), [`playbooks/if-you-ran-malicious-postinstall.md`](../playbooks/if-you-ran-malicious-postinstall.md) (the triage applies even though the trigger was import, not install).

## Prevention

- Vet names before installing, especially ones an assistant supplied: [`prevention/package-vetting-checklist.md`](../prevention/package-vetting-checklist.md), [`ongoing-slopsquatting.md`](ongoing-slopsquatting.md).
- Keep wallets and developer browsers on different profiles or machines; import-time stealers need only one `require` to run. [`prevention/npm-hardening.md`](../prevention/npm-hardening.md), [`prevention/credential-hygiene.md`](../prevention/credential-hygiene.md).

## Sources
- [OpenSourceMalware — WeaselBiscuit Strips BeaverTail and OtterCookie Down to Essentials](https://opensourcemalware.com/blog/introducing-weaselbiscuit) — primary; 2026-09-17; the 14-package list with versions and the 09-12 → 09-16 window, the `initialize()` loader, targets, the overlap/divergence analysis, the attribution caveats, the payload hash. Fetched 2026-09-18.
- [The Hacker News — WeaselBiscuit Stealer Spreads via 13 npm Packages to Harvest Chrome Extension Storage](https://thehackernews.com/2026/09/weaselbiscuit-stealer-spreads-via-13.html) — 2026-09-18; the 13-package list, `loader.js` / Npoint dead-drop description, Jenn Gile's quote. Fetched 2026-09-18.
- npm registry lookups for `engin1`, `id79-client`, `process-lhpm`, `process-mite`, `process-tailwind`, `@biz44/runtime-utils`, `@biz44/id10-client`, `@biz44/id44-client`, `@biz44/process-runtime-utils` — all "Not found" on 2026-09-18.
