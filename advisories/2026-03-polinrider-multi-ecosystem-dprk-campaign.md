---
id: 2026-03-polinrider-multi-ecosystem-dprk-campaign
title: "PolinRider — ongoing DPRK-linked campaign backdoors npm, Packagist, Go, and a Chrome extension via maintainer-account takeover (Mar 2026–ongoing)"
date_disclosed: 2026-03-01
last_updated: 2026-10-01
severity: high
status: active
ecosystems: [npm, packagist, go, chrome-extension]
tools_affected: [multiple compromised maintainer accounts/repos across npm, Packagist, Go, Chrome Web Store]
tags: [supply-chain, dprk, account-takeover, git-history-rewrite, credential-theft, wallet-theft, cross-ecosystem]
---

## TL;DR

**PolinRider** is an ongoing, DPRK-linked ("Contagious Interview"/Famous Chollima) supply-chain campaign that takes over maintainer accounts across **npm, Packagist (PHP/Composer), Go modules, and at least one Chrome extension**, then plants obfuscated JavaScript loaders — hidden in fake `.woff2` font files, config files, or VS Code `folderOpen` tasks — that fetch and `eval()` second-stage payloads from blockchain/RPC infrastructure. As of this sweep, **over 100 packages/extensions and 1,900+ GitHub repositories** have been implicated, and the campaign is **still active**.

## What happened

First flagged by the OpenSourceMalware team around **2026-03**, PolinRider involves DPRK-linked threat actors — tied to the broader **Contagious Interview / Famous Chollima** developer-targeting cluster — compromising open-source maintainer accounts (via credential theft, not registry-side bugs) and using that access to plant obfuscated JavaScript payloads directly into legitimate repositories ([The Hacker News](https://thehackernews.com/2026/07/north-korean-hackers-publish-108.html), [Socket](https://socket.dev/blog/polinrider-north-korea-linked-supply-chain-campaign-expands)).

**Concealment technique:** payloads are hidden via whitespace-padding (pushing code beyond the visible editor width), embedding in config files (`vite.config.js` and similar), or disguised as **fake `.woff2` font files**, then wired to auto-execute via a **VS Code task file** configured with `"runOn": "folderOpen"` — meaning simply opening the poisoned repo folder in VS Code triggers the payload, no `npm install` required. The threat actors also **rewrite Git history and force-push** to backdate malicious commits, making the compromise harder to spot in a normal `git log` review — one Packagist compromise reportedly used antedated January 8 commits with a May 16 cleanup attempt to cover tracks ([Socket](https://socket.dev/blog/polinrider-north-korea-linked-supply-chain-campaign-expands)).

**Execution chain:** the loader reaches out to **blockchain and public RPC infrastructure (TRON, Aptos, BNB Smart Chain)** to retrieve an encrypted second-stage payload, decrypts it with an embedded XOR key, and executes the result with `eval()`. Observed follow-on payloads include **DEV#POPPER** (command execution + `socket.io-client`-based C2) and **OmniStealer** (credential theft, browser-data theft, wallet exfiltration) ([Socket](https://socket.dev/blog/polinrider-north-korea-linked-supply-chain-campaign-expands)). A related, merged activity cluster called **TaskJacker** specifically drops malicious VS Code task files into victims' existing repositories ([The Hacker News](https://thehackernews.com/2026/07/north-korean-hackers-publish-108.html)).

**Scale (as of 2026-07-01, per The Hacker News):** 108 unique packages/extensions across 162 release artifacts — 19 npm packages, 10 Composer/Packagist packages, 61 Go modules, and 1 Chrome extension. Socket's independent tracking (as of the same period) counted 80 Go modules, 10 Packagist packages, 1 Chrome extension, plus additional npm packages — the exact per-ecosystem counts vary slightly by tracker as the campaign is still growing; both sources agree the campaign spans all four ecosystems and remains active. As of **2026-04-11**, the broader activity (including the pre-PolinRider BeaverTail-loader phase) had touched **1,951 public GitHub repositories across 1,047 unique maintainer accounts** ([The Hacker News](https://thehackernews.com/2026/07/north-korean-hackers-publish-108.html)). A confirmed recent wave hit GitHub user **`Xpos587`**'s repositories (`git2md`, `markfetch`) and organization **`7span`**/Packagist namespace **`sevenspan`** (`react-list`) with synchronized modifications around **2026-06-23 10:00 UTC** ([Socket](https://socket.dev/blog/polinrider-north-korea-linked-supply-chain-campaign-expands)).

**Status: ongoing.** Socket explicitly tracks this as a live, growing campaign at a dedicated tracking page, with new compromises surfacing regularly.

### Update 2026-07-25 — disputed link to ChainVeil/ViteVenom npm typosquat waves
Researcher outlet **OpenSourceMalware** published an analysis ([ChainVeil and ViteVenom are DPRK's PolinRider Campaign](https://opensourcemalware.com/blog/chainveil-and-vitevenom-dprk-polinrider-campaign), 2026-07-17) arguing that the **ChainVeil** (May–June 2026, Tailwind CSS/Sass typosquats) and **ViteVenom** (June–July 2026, Vite typosquats) npm campaigns — see the new standalone writeup at [2026-07-chainveil-vitevenom-npm-blockchain-c2.md](2026-07-chainveil-vitevenom-npm-blockchain-c2.md) — share blockchain-wallet infrastructure with PolinRider, based on wallet addresses OpenSourceMalware says it had independently tracked before either campaign's public report. **This is a contested claim, not a confirmed one:** Checkmarx Zero, the primary researcher who discovered and named both ChainVeil and ViteVenom, attributes them to a distinct operator it calls "SuccessKey" and makes no DPRK or PolinRider attribution in either of its own writeups. Noting the dispute here rather than merging the campaigns — a single party's claimed infrastructure overlap is not sufficient to override the original discoverer's own attribution.

## Am I affected?

```bash
# Audit for VS Code auto-run tasks that trigger on folder open — a key PolinRider persistence primitive
grep -r '"runOn"\s*:\s*"folderOpen"' .vscode/tasks.json 2>/dev/null

# Look for unexpected .woff2 files outside font/asset directories, and check recently
# force-pushed history on dependencies you maintain or heavily rely on
git log --all --source --diff-filter=A -- '*.woff2' 2>/dev/null

# Review GitHub Activity logs (not just `git log`) for force-pushes to any repo you
# maintain or depend on — history rewriting is a core part of this campaign's cover-up
```

You're at risk if you cloned or opened (in VS Code) a repository maintained by an account named in ongoing PolinRider disclosures, or if a dependency you use was published from a compromised maintainer account during the exposure window. Check Socket's live tracking page for currently-known affected packages before assuming you're clear, since the list changes frequently.

## If you are affected

1. Do not open a suspected-poisoned repository folder in VS Code until you've inspected `.vscode/tasks.json` and any `.woff2`/config files for obfuscated content.
2. If you already opened an affected repo or installed an affected package, treat the machine as compromised — DEV#POPPER and OmniStealer target credentials, browser data, and crypto wallets. Follow [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) and [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).
3. Rotate credentials and treat any crypto wallets accessed from that machine as compromised, per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. If you maintain a package/repo, audit your account's recent push history via the GitHub **Activity** log (not just `git log`, since history can be rewritten) for force-pushes you didn't make, and rotate your GitHub credentials/tokens and enable MFA.

## Prevention

- Disable or review VS Code `"runOn": "folderOpen"` tasks by default in untrusted repositories — this is now a documented auto-execution primitive across multiple campaigns (see also the Miasma Wave 5 hook-auto-execution class). See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- Enforce MFA and hardware security keys on maintainer accounts across every registry you publish to (npm, Packagist, Go module proxies, Chrome Web Store) — account takeover, not a registry vulnerability, is the entry point here.
- Prefer reviewing GitHub's **Activity/audit log** over `git log` alone when auditing a dependency's recent history, since this campaign relies on rewritten/force-pushed commits.
- See [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) and [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) for routine cross-ecosystem dependency hygiene.


### Update 2026-10-01 — the loader now reads its C2 from Ethereum mainnet transactions, and SafeDep finds it live at HEAD in 35 GitHub repositories (7,578 stars) — surfaced by a rejected pull request against oxc that a formatting bot un-minified

SafeDep (2026-09-30) reports a new PolinRider loader variant whose C2 discovery works like [NullReceiver](2026-08-nullreceiver-npm-ethereum-c2.md): it reads **Ethereum mainnet** for small transactions from an operator wallet and decodes **each transaction's recipient address as a C2 IP**. Two operator wallets use the scheme — one sending a transaction roughly every **51 minutes since 2026-06-23**, the other every ~3.3 hours since 07-25 — and their public histories show **11 C2 servers**, eight on one hosting provider (AS149440 Evoxt); two of the servers also appear in SafeDep's earlier `astro.config.mjs` and `@joyfill` investigations, which is the link back to this campaign. One infection writes **two loaders** into a project: the Ethereum one and a second keyed to a Tron address pair SafeDep had not seen in public reports; the OpenSSF malicious-packages database holds 70 npm/PyPI records containing the second wallet and none for the first.

**Where it was found.** A pull request against **oxc-project/oxc** (opened 09-14, branch rewritten 09-25) added the loader to **20 build, test, benchmark and code-generation scripts**, each edit placed after 2,000 spaces on the last line (TypeScript files carried it as base64 inside `eval(atob(…))`), with the commit's *author* field forged to a real oxc maintainer and an author date ten weeks older than the commit. **The maintainers did not merge it** — the payload became visible only because the repository's `autofix.ci` formatting bot reformatted the one-line payload into 106 lines in the diff, and maintainer Boshen posted the screenshot on 09-30. GitHub has removed the contributor account; the commits remain reachable by SHA in the fork network. From that diff SafeDep decoded every stage statically and found **35 repositories carrying the loader at the tip of their default branch on 2026-09-30** (7,578 stars, 2,884 forks combined); the loader runs when a developer builds or starts the project.

**What is new for defenders.** (1) The "poison the repo, not the registry" branch of PolinRider has a **pull-request** delivery variant — a forged-author commit in a PR that touches scripts CI runs, aimed at a maintainer merging or a CI job building the branch; a bot that reformats code exposed it where human review of a 2,000-space line would not. (2) **Blockchain dead-drop C2 now reaches repository-level DPRK tooling**, so "block the known C2 IPs" is a losing control — the wallet is the durable indicator, and the on-chain history is a public log of every C2 the operator has ever used. (3) The 35 repositories are **currently infected** — a `git clone && npm run build` of any of them runs the loader. SafeDep's post lists them; this advisory does not reproduce the list or the wallet/IP indicators (see the repo's IOC policy) — read the post before building an unfamiliar JavaScript project with a large star count, and check CI for `autofix`-style diff expansion as a review aid.

```bash
# In any repository you are about to build: scripts with a very long trailing line, or eval(atob(...)) in TypeScript
grep -rlE '^.{2000,}$' --include='*.js' --include='*.mjs' --include='*.cjs' . 2>/dev/null | head
grep -rnE 'eval\(.*atob\(' --include='*.ts' --include='*.js' . 2>/dev/null | head
# PRs against your project that touch build/test/bench scripts with single-quoted imports where your code uses double quotes
git log --format='%h %an <%ae> %ad | %cn %cd' --date=short -- '*.js' '*.mjs' | awk '$0 ~ /\|/' | head   # author ≠ committer, author date far older than commit date
```

## Sources

- [The Hacker News — "North Korean Hackers Publish 108 Malicious Packages and Extensions in PolinRider Campaign"](https://thehackernews.com/2026/07/north-korean-hackers-publish-108.html) — scale, ecosystem breakdown, TaskJacker cross-link, historical repository-count figures.
- [Socket — "PolinRider: North Korea-Linked Supply Chain Campaign Expands"](https://socket.dev/blog/polinrider-north-korea-linked-supply-chain-campaign-expands) — attack mechanism detail (Git history rewriting, `.woff2` concealment, blockchain RPC C2), specific IOCs, timeline, live-tracking status.
- **2026-10-01 update sources** — [SafeDep — PolinRider Switches to Ethereum C2 in 30+ Repositories (2026-09-30)](https://safedep.io/polinrider-ethereum-c2-github-repositories) (primary, fetched 2026-10-01 with indicators filtered: the recipient-address C2 encoding, two operator wallets and their cadence since 06-23 / 07-25, 11 C2 servers / AS149440, the two-loader infection, the oxc pull request anatomy — 20 scripts, 2,000-space padding, forged author, `autofix.ci` reformat, Boshen's 09-30 post — the 35-repository / 7,578-star count at HEAD on 09-30, the OpenSSF malicious-packages cross-reference, and the overlap with SafeDep's astro.config.mjs and @joyfill cases); [SafeDep blog index](https://safedep.io/blog/) (fetched 2026-10-01; the 09-30 post sits beside the 09-29 DirtyBlanket post).
