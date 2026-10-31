---
id: 2026-10-debugbear-rum-snippet-compromise-polymarket-drain-remove-the-snippet
title: "DebugBear RUM snippet compromised: remove it from your sites and invalidate sessions (Polymarket drained 2026-10-29)"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-10-31
severity: high
status: active
ecosystems: [web, third-party-script, real-user-monitoring, polymarket]
tools_affected: ["any website that embeds DebugBear's real user monitoring (RUM) snippet", "polymarket.com (international site) users who were signed in on 2026-10-29", "web apps whose signed-in session can authorise transactions from the browser"]
tags: [malicious-artifact, third-party-script, rum-snippet, supply-chain, website-compromise, session-abuse, debugbear, polymarket, hudson-rock, goplus, vendor-site-down]
---

## TL;DR
Remove DebugBear's real user monitoring (RUM) snippet from every site that embeds it until DebugBear publishes a post-mortem and a clean release, because the script it served on 2026-10-29 was modified and drained signed-in Polymarket users' positions. If your site carried the snippet during the window, invalidate active sessions and review anything a signed-in browser session on your site could authorise.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Third-party website script | DebugBear real user monitoring (RUM) snippet, loaded from DebugBear's hosts | the copy served on 2026-10-29 (no version number; the snippet is fetched live) | remove the snippet; DebugBear told RUM customers to pull it (SecurityWeek, 2026-10-30) | `debugbear.com` returned HTTP 530 on every path read on 2026-10-31 (front page, blog, guessed incident paths); its status host did not connect; DebugBear's statement is an X post of 2026-10-29 | none (not a package; no OSV or GHSA record) |
| Website | `polymarket.com` (international site) | pages served while the snippet was embedded, 2026-10-29 | Polymarket's production build of 17:59 UTC on 2026-10-29 removed the DebugBear script (Hudson Rock, via SecurityWeek); the US platform was reportedly unaffected | trading halted for about an hour and resumed at 15:00 ET on 2026-10-29 (NBC News) | none |

Figures differ by analyst and are printed with their sources: Hudson Rock about $2.19 million; GoPlus about $2.71 million across 710 deposit wallets and 731 addresses, with the note that the address count is not a victim count; Arkham, as reported by The Block and NBC News, about $2.65 million. Polymarket says every affected trader will be reimbursed and has referred the matter to law enforcement. Hudson Rock said it had not determined how the script was tampered with, and DebugBear described its incident as ongoing on 2026-10-29; no post-mortem had appeared when this file was written.

## Am I affected?

Search your site's templates, tag manager and bundles for the snippet:

```bash
# Repository and build output
grep -rniE 'debugbear' --include='*.html' --include='*.js' --include='*.ts' --include='*.tsx' --include='*.vue' --include='*.svelte' --include='*.astro' . 2>/dev/null | grep -v node_modules | head
```

Also check your tag manager (Google Tag Manager, Segment and similar) for a DebugBear tag, since snippets often arrive that way and never appear in the repository. In server or CDN logs and CSP reports, look for your pages loading scripts from DebugBear hosts on 2026-10-29. If your site handles money, signing or other actions a signed-in browser can take, review the transactions and account changes made during the time the snippet was present.

A site that embeds the snippet was served whatever DebugBear's hosts returned; this file does not establish that any customer other than Polymarket received the modified copy, and Hudson Rock's findings, as reported, do not indicate other customers were targeted. Treat embedding during the window as exposure to review, not as a confirmed compromise.

## If you are affected

1. Remove the snippet from templates and tag managers and redeploy; do not re-add it until DebugBear publishes what happened and how its hosts were secured.
2. Invalidate active user sessions on the site and force re-authentication, so a token a page-level script could have used no longer works.
3. Rotate any key or token that was present in page source or reachable from the browser (public API keys that gate anything, signing endpoints, embedded service tokens). Follow [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md) and, for cloud keys exposed through the site, [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
4. Review transactions and account changes during the window and notify affected users; Polymarket's own response was to halt, remove, resume and reimburse.

## Prevention

- Every third-party script on a page runs with the page's full session; load only what you need, and prefer self-hosting a pinned copy of monitoring scripts over a live snippet from the vendor's host.
- Put a Content Security Policy on signed-in pages with explicit `script-src` and `connect-src` allow-lists, and send reports somewhere you read; a modified script's new connections are then visible, and often blocked.
- Where a vendor serves a versioned static file, add Subresource Integrity hashes; a snippet that changes on the vendor's side cannot carry one, which is the reason to self-host it.
- Keep high-value actions behind re-authentication or a hardware prompt rather than a session cookie alone. See [supply-chain attack surface](../prevention/supply-chain-attack-surface.md) and [credential hygiene](../prevention/credential-hygiene.md).

## Sources
- [SecurityWeek — $2 Million+ Drained From Polymarket Traders in New Supply Chain Attack](https://www.securityweek.com/2-million-drained-from-polymarket-traders-in-new-supply-chain-attack/) — fetched 2026-10-31: 2026-10-30; the DebugBear RUM snippet as the vector, Hudson Rock's analysis and $2.19 million figure, GoPlus's $2.71 million and 710/731 counts, Arkham's $2.65 million, Polymarket's 17:59 UTC build removing the script, the US platform reportedly unaffected, DebugBear confirming it was affected and urging RUM customers to remove its snippet, Hudson Rock not having determined how the script was tampered with, reimbursement and law-enforcement referral.
- [NBC News — Polymarket halts trading after compromise, impacted users will be 'made whole'](https://www.nbcnews.com/business/consumer/polymarket-trading-halt-hack-wallets-rcna606405) — fetched 2026-10-31: 2026-10-29, Rob Wile; Polymarket's statements ("One of our 3rd party providers was compromised", "fully reimbursing all affected traders"), DebugBear's X statement of an "ongoing security incident" at about 14:00 ET, the hour-long halt ending at 15:00 ET, Arkham's figure via The Block.
- [KuCoin News — GoPlus: Polymarket Hack Linked to DebugBear Script Supply Chain Compromise](https://www.kucoin.com/news/flash/goplus-polymarket-hack-linked-to-debugbear-script-supply-chain-pollution) — fetched 2026-10-31: 2026-10-30; GoPlus's attribution to a compromised DebugBear RUM script, the on-chain figures and the address-count caveat.
- Hacker News items 50296185 ("DebugBear Security Incident", linking DebugBear's X post, 2026-10-29 21:20 UTC), 50295883 (Polymarket's X post) and 50305225 (NBC News, 114 points), read through the Algolia search API 2026-10-31 for titles, times and links; the X posts were not opened.
- `debugbear.com` front page, `/blog` and two guessed incident paths — requested 2026-10-31: HTTP 530 (origin error) on each; `status.debugbear.com` did not connect. Not read: Wired's and SC World's coverage (403), Hudson Rock's and GoPlus's own posts (not located outside X).
