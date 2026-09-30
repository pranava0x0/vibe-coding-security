---
id: 2026-09-phantomsub-baileys-npm-whatsapp-channel-subscription
title: "PhantomSub — 101 npm packages forked from the Baileys WhatsApp library (ourin-baileys, @nexustechpro/baileys, levvleys, neuralwhatsapp, cloud-baileys, my-auto-follow…) silently subscribe the developer's WhatsApp account to scam channels when the bot runs; ~490,000 downloads, 116,000 in the last 30 days, only 16 removed at disclosure and several still publishing (OX Security, 2026-09-28)"
date_disclosed: 2026-09-28
last_updated: 2026-09-30
severity: medium
status: active
ecosystems: [npm, whatsapp, javascript]
tools_affected: ["Any WhatsApp bot, customer-support automation or scraper built on a Baileys fork from npm", "the developer's or business's WhatsApp account", "vibe-coded WhatsApp bots that picked a Baileys variant by search"]
tags: [supply-chain, npm, baileys, whatsapp, account-abuse, follower-inflation, long-running-campaign, fork-poisoning, active]
---

## TL;DR

OX Security's research team identified **101 npm packages** that repackage **Baileys** — the unofficial WhatsApp Web API library developers use for support bots, chat managers and scrapers — with one addition: when the bot logs in with your WhatsApp account, the package **subscribes that account to WhatsApp channels the operator chose**, without telling you. Three variants differ only in where the channel list comes from: **19 packages fetch it from GitHub at runtime** (so the operator can retarget without republishing), **60 hard-code it in cleartext**, **14 base64-encode it**, and 7 more were removed before OX could classify them. Combined downloads are **~490,000, 116,000 in the prior 30 days**. The channels are Indonesian storefronts selling game accounts, TikTok accounts and bot services; the stolen subscriptions are **social proof** (follower counts of 800–4,800 per channel). **Only 16 of the 101 had been removed by 2026-09-28**, and the registry shows several of the named packages still publishing new versions on 09-28 and **09-30**. Not a credential stealer — but it is a package that logs into your customer-facing WhatsApp account and acts as you.

## What happened

OX's post (2026-09-28) and The Hacker News' coverage (09-29) describe the campaign. Baileys is a reverse-engineered WhatsApp Web client; hundreds of forks live on npm under names like `*-baileys`, `*leys`, `*whatsapp`, because the upstream project churns and forks promise "fixed" or "extended" builds. The malicious forks are functional — the bot works — which is why they accumulate downloads and why nobody notices. The subscribe call runs on connection. Thirty-two channels appear across multiple packages, which OX reads as one operator or one shared list; the runtime-fetched lists live in three public GitHub repositories (named in the OX post). OX names a contact tied to several of the storefronts and places the operation in Indonesia. Prior sightings of the same family: SafeDep flagged Baileys forks in August 2026, Xygeni disclosed `@dappaoffc/baileys-mod` earlier in September, and Xygeni's September digest calls `cloud-baileys` "one of the longest-running impersonations tracked."

Sample package names from the report: `ourin-baileys`, `@nexustechpro/baileys`, `levvleys`, `neuralwhatsapp`, `cloud-baileys`, `my-auto-follow`. Registry check 2026-09-30: all six still resolve with versions and `latest` tags; `@nexustechpro/baileys` published 2.2.8 on **2026-09-28** and 2.2.9 on **2026-09-30**, `cloud-baileys` 1.1.41 on 09-18, `my-auto-follow` 1.0.7 on 09-20. No security-holder placeholders yet. That is why the status is `active`.

Why it matters to this audience: "build me a WhatsApp bot" is a common vibe-coding prompt, the agent picks a Baileys package by name similarity or star count, and the package gets the one thing a WhatsApp bot needs — a logged-in session for a real account, often the business's. Today the abuse is channel subscriptions. The same hook could send messages, read chats, or add the account to groups; the library already has every capability a stealer would want, so the difference between this campaign and a worse one is a few lines the operator has not written yet.

## Am I affected?

```bash
# 1. Which Baileys variant did you install? Upstream is @whiskeysockets/baileys; anything else is a fork.
grep -E '"[^"]*(baileys|leys|whatsapp)[^"]*":' package.json package-lock.json 2>/dev/null | sort -u
npm ls 2>/dev/null | grep -iE 'baileys|leys|whatsapp'

# 2. The six OX named (there are 95 more — read the OX post for the full list)
grep -rE 'ourin-baileys|@nexustechpro/baileys|levvleys|neuralwhatsapp|cloud-baileys|my-auto-follow' package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null

# 3. In the installed fork, look for channel/newsletter subscription calls you did not write
grep -rniE 'newsletter|subscribe|followNewsletter|idChannel|@newsletter' node_modules/*baileys*/ node_modules/*leys*/ 2>/dev/null | grep -v '\.d\.ts' | head

# 4. On the WhatsApp account the bot uses: Updates → Channels → check for channels you never followed
```

## If you are affected

1. In WhatsApp, unfollow and report the channels; treat the account as having been operated by a third party.
2. Remove the fork, pin to upstream `@whiskeysockets/baileys` (or a fork you have read), and log the bot out of WhatsApp so the old session is revoked (Linked Devices → log out); delete the stored auth state directory the bot used.
3. Because the runtime-fetch variant executes an operator-controlled list, assume the package's behaviour can change at any time: review the fork's source for outbound calls and any other network activity before reinstalling anything similar. [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- **Name the upstream explicitly.** Ask the agent for `@whiskeysockets/baileys` and refuse the "fixed", "pro", "cloud" or "neural" variants; a fork of a library that holds a logged-in session is a package that can act as your account. [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- **A working package is not a safe package.** Download counts and "it runs" are exactly what this campaign optimises for; vet for what a library *also* does on connect. [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- Run bots on a dedicated WhatsApp account with nothing on it, never the business's primary line. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

- [OX Security — PhantomSub: Malicious npm Campaign Secretly Adds Users to WhatsApp Spam Channels](https://www.ox.security/blog/phantomsub-malicious-npm-campaign-secretly-adds-users-to-whatsapp-spam-channels/) — primary, 2026-09-28: the 101-package count, 490,000 / 116,000 downloads, 16 removed, the 19 / 60 / 14 / 7 variant split, the three GitHub-hosted channel lists, 32 shared channels, the Indonesian storefronts and follower counts, detection guidance. Fetched 2026-09-30.
- [The Hacker News — 101 Malicious npm Packages Add Developers' WhatsApp Accounts to Groups Without Consent](https://thehackernews.com/2026/09/101-malicious-npm-packages-add.html) — 2026-09-29: the researcher credits (Nir Zadok, Moshe Siman Tov Bustan, Vitalii Chepurko), the six sample names, the SafeDep (August) and Xygeni (`@dappaoffc/baileys-mod`) prior sightings, the named channels. Fetched 2026-09-30.
- [Xygeni — Malicious Code Digest, September 2026](https://xygeni.io/blog/malicious-code-digest-monthly-recap-september-2026/) — the `cloud-baileys` 1.1.37 / 1.1.38 / 1.1.40 / 1.1.41 publications (Sept 2, 4, 11, 19) and the "longest-running impersonations" note. Fetched 2026-09-30.
- npm registry (`registry.npmjs.org/<pkg>`, queried 2026-09-30): `ourin-baileys` latest 9.0.21 (2026-08-22), `levvleys` 2.1.0 (09-11), `neuralwhatsapp` 3.3.3 (08-22), `cloud-baileys` 1.1.41 (09-18), `my-auto-follow` 1.0.7 (09-20), `@nexustechpro/baileys` 2.2.8 (09-28) and 2.2.9 (09-30) — all live, none replaced by a security holder.
- Related in this corpus: [Alibaba `lib-mtop` npm RAT cluster](2026-07-alibaba-lib-mtop-npm-rat-cluster.md) (functional packages with a side channel), [Shai-Hulud copycat wave](2026-05-shai-hulud-copycat-wave.md).
