---
id: 2026-07-chainveil-vitevenom-npm-blockchain-c2
title: "ChainVeil / ViteVenom — two sequential npm typosquat waves impersonating Tailwind CSS and Vite tooling, four-tier blockchain C2 (May–July 2026)"
date_disclosed: 2026-07-14
last_updated: 2026-07-14
severity: medium
status: contained
ecosystems: [npm]
tools_affected: [tailwindcss, vite, any-node-project]
tags: [supply-chain, typosquat, npm, blockchain-c2, rat, credential-theft, import-time-exec]
---

## TL;DR
Checkmarx Zero disclosed two sequential npm typosquat campaigns from the same operator: **ChainVeil** (May–June 2026, 9 packages impersonating Tailwind CSS/Sass/TypeORM tooling, ~3,300 downloads) and its sequel **ViteVenom** (June–July 2026, 7 packages impersonating **Vite** tooling under names like `@vite-pro/vite-ui` and `@vite-mcp/vite-type`, ~2,400 downloads). Both deliver an identical 77 KB remote-access trojan via a novel **four-tier blockchain command channel** spanning Tron, Aptos, and Binance Smart Chain, executed at **import time** (not install time), evading `--ignore-scripts`. Checkmarx attributes both waves to a single operator it calls **SuccessKey** with no nation-state claim; a second research group, OpenSourceMalware, separately argues the same infrastructure overlaps with the DPRK-linked [PolinRider](2026-03-polinrider-multi-ecosystem-dprk-campaign.md) campaign — a claim Checkmarx's own writeup does not make. Both attributions are noted below; treat the PolinRider link as **unconfirmed**, sourced from one party only.

## What happened
**ChainVeil** (Checkmarx Zero, published 2026-06-16): nine npm packages published by the npm account `successkeyteck` — `tailwindcss-merge`, `tailwindcss-animatics`, `tailwindcss-animates-kit`, `sass-format`, `sass-formats`, `clsx-tailwind`, `typeorm-encrypt`, `rate-limit-flexible`, `rate-limits-flexible` — all impersonating popular Tailwind CSS/Sass/ORM tooling names. Published May 18 – June 10, 2026, 14 malicious versions, 3,293 combined downloads. The payload sits in `lib/lib.min.js`, obfuscated with seven layers of a custom seeded string-shuffling algorithm, and contains "zero suspicious install scripts" — it fires only when imported. Malicious versions are tagged internally with an "A6-" campaign-tracking prefix (e.g. `A6-519-81`) that funnels every infection to the same primary C2, `166.88.54.158:443` ([Checkmarx Zero — ChainVeil](https://checkmarx.com/zero-post/chainveil-a-malicious-npm-supply-chain-attack-by-successkey/)).

**ViteVenom** (Checkmarx Zero, published 2026-07-14): a sequel targeting the **Vite** ecosystem specifically — seven packages (`@uw010010/vite-tree`, `@vite-tab/tab`, `@vite-ln/build-ts`, `@vite-mcp/vite-type`, `@vite-pro/vite-ui`, `@vitets/vite-ts`, `@vite-ts/vite-ui`), published 2026-06-29 – 07-03, malicious code identically placed in `bin/vite.js`, 2,420 combined downloads across 9 versions. Checkmarx attributes ViteVenom to the same operator as ChainVeil with "high confidence," citing identical Tier-2 wallet addresses, identical XOR decryption keys, and the same 77 KB RAT payload — while explicitly noting "a shared-infrastructure-as-a-service model cannot be ruled out on technical grounds alone" ([Checkmarx Zero — ViteVenom](https://checkmarx.com/zero-post/sequel-to-chainveil-npm-malware-targets-vite-ecosystem/)).

### Payload and blockchain C2
Both waves deliver a full-featured RAT (reverse shell, SSH-key/npm-token/environment-variable credential harvesting, file exfiltration, shell-config persistence via 200+ spaces of whitespace padding). The C2 resolution chain — designed so that seizing a domain doesn't disable the campaign — works in four tiers:
1. Query a hardcoded **Tron** wallet address for its most recent outbound transaction.
2. Hex-decode and reverse the transaction's data field to derive a **Binance Smart Chain (BSC)** transaction hash.
3. Query that BSC transaction; the encrypted next-stage payload is embedded in the transaction's input field.
4. **XOR-decrypt** the payload with a hardcoded key and execute it via `eval()`. **Aptos** serves as a fallback broadcast layer, synchronized with the Tron post within roughly 0.3 seconds.

ViteVenom adds a persistence variant: a detached, invisible child process (`stdio: 'ignore'`, `windowsHide: true`) that survives the parent process exiting and fetches its payload directly from an HTTP C2 (`198.105.127[.]210:443`, `/$/boot` endpoint) rather than the blockchain, as a backup channel.

### Competing attribution
Checkmarx's own primary research names the operator **SuccessKey** (from the npm account `successkeyteck`) and makes **no nation-state or PolinRider attribution**. A separate outlet, **OpenSourceMalware**, published its own analysis ([ChainVeil and ViteVenom are DPRK's PolinRider Campaign](https://opensourcemalware.com/blog/chainveil-and-vitevenom-dprk-polinrider-campaign), 2026-07-17) arguing the two Tron wallets anchoring ChainVeil's command channel were ones it had itself been tracking roughly 100 days before Checkmarx's ChainVeil report existed, and ties both waves to the DPRK-linked, Lazarus-associated PolinRider campaign already tracked in this repo. **This repo cites both claims but does not merge them**: the primary discoverer (Checkmarx) explicitly declines the nation-state/PolinRider attribution its own evidence would support, while a second party asserts it based on independently-tracked wallet history not corroborated in Checkmarx's writeup. Readers should treat the PolinRider link as an open question, not a settled fact — a useful reminder that "shared blockchain C2 infrastructure" (Tron/Aptos/BSC XOR-key channels) is now common enough across unrelated npm-malware campaigns that infrastructure overlap alone is suggestive, not dispositive, evidence of common operatorship.

## Am I affected?
```bash
# Check whether any ChainVeil or ViteVenom package is anywhere in your dependency tree
for pkg in tailwindcss-merge tailwindcss-animatics tailwindcss-animates-kit sass-format sass-formats \
           clsx-tailwind typeorm-encrypt rate-limit-flexible rate-limits-flexible \
           @uw010010/vite-tree @vite-tab/tab @vite-ln/build-ts @vite-mcp/vite-type \
           @vite-pro/vite-ui @vitets/vite-ts @vite-ts/vite-ui; do
  npm ls "$pkg" --all 2>/dev/null | grep -q "$pkg" && echo "FOUND: $pkg"
done

# None of these are real Tailwind/Vite/TypeORM packages — the presence of ANY of them
# in package.json or a lockfile is itself the indicator of compromise.
grep -E '"(tailwindcss-merge|tailwindcss-animatics|tailwindcss-animates-kit|sass-formats?|clsx-tailwind|typeorm-encrypt|rate-limits?-flexible|@uw010010/vite-tree|@vite-(tab|ln|mcp|pro|ts)/|@vitets/vite-ts)"' package.json package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null
```
None of these package names correspond to real Tailwind CSS, Sass, TypeORM, or Vite projects — they are purely typosquat/impersonation names invented for this campaign, so simply *not recognizing the name* is itself a strong signal to remove it.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md) — the RAT specifically harvests npm tokens and SSH keys.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — verify a package's actual npm-account maintainer and GitHub repo before installing anything with a name that only *resembles* a well-known framework (`tailwindcss-*`, `@vite-*`, `vite-*`) rather than being published under the framework's own official scope.
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — note again that this payload triggers at **import time**, not install time, so `--ignore-scripts` does not protect against it.

## Why this matters for vibe coders
This campaign directly typosquats two of the most commonly used vibe-coding frontend tools — **Tailwind CSS** and **Vite** — with package names plausible enough to be pulled in by autocomplete or a quick `npm install` when a developer (or an AI coding agent) is reaching for a Tailwind merge/format helper or Vite plugin. Download counts are modest (a few thousand combined) and well under this repo's usual >100k-download bar for a standalone advisory, but the direct framework impersonation plus the genuinely novel four-tier blockchain C2 architecture — and the live disagreement between two research groups over whether this is DPRK state activity — make it worth tracking on its own rather than folding into an unrelated campaign's writeup.

## Sources
- [Checkmarx Zero — ChainVeil: A Malicious npm Supply Chain Attack by SuccessKey](https://checkmarx.com/zero-post/chainveil-a-malicious-npm-supply-chain-attack-by-successkey/) — primary technical disclosure of the ChainVeil wave; package list, blockchain C2 mechanics, "SuccessKey" attribution.
- [Checkmarx Zero — Sequel to ChainVeil: npm Malware Targets Vite Ecosystem](https://checkmarx.com/zero-post/sequel-to-chainveil-npm-malware-targets-vite-ecosystem/) — primary technical disclosure of the ViteVenom wave; Vite-specific package list, persistence variant, same-operator attribution.
- [OpenSourceMalware — ChainVeil and ViteVenom are DPRK's PolinRider Campaign](https://opensourcemalware.com/blog/chainveil-and-vitevenom-dprk-polinrider-campaign) — competing attribution claim tying both waves to PolinRider/DPRK via independently-tracked wallet history.
