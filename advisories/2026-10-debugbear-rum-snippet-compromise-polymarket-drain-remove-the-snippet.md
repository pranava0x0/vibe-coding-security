---
id: 2026-10-debugbear-rum-snippet-compromise-polymarket-drain-remove-the-snippet
title: "DebugBear RUM snippet compromised: remove it from your sites and invalidate sessions (Polymarket drained 2026-10-29)"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-11-02
severity: high
status: contained
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

## Update 2026-11-02 — DebugBear says its DNS records were compromised at its domain registrar; Polymarket returns $3.9 million to 726 drained wallets and about 5,500 affected by the halt; status to contained

DebugBear's preliminary findings, posted on X and quoted by The Hacker News (2026-11-01) and SecurityWeek (2026-11-02): "Our DNS server records were compromised through our domain registrar." It says it is not yet clear how the registrar-level access was obtained, that it has found no sign its internal systems were compromised, that early findings suggest the attack targeted one customer's website, that the DNS problems also stopped it receiving email at its domain, and that the investigation is ongoing; it has told RUM customers to remove its embed code. Neither outlet names the registrar or gives a timeline for the DNS change. The Hacker News adds that the host serving the modified file had no DNS record when it checked on 2026-11-01, and that Ohey observed a different server answering for DebugBear's addresses at 18:13 UTC on 2026-10-29 while the modified file was still online. This is a DNS-level substitution of what DebugBear's hostnames resolved to, which is why DebugBear's own servers show no intrusion and why every site loading the snippet live from those hostnames was exposed during the window.

Polymarket's figures, per both outlets: about $2.7 million stolen directly from 726 wallets, 689 of them refunded in full by 2026-10-30 and the remaining 37 paid after verification; a further $1.19 million to about 5,500 wallets affected by the trading halt or by positions sold or transferred by the script; $3.9 million returned in total. Its first status update was at 17:38 UTC, cancel-only mode at 18:05 UTC, and its statement reads: "The attack came through a compromised 3rd party provider which we removed within the hour." It has not named the provider, is working with law enforcement, and has promised a post-mortem that had not appeared on 2026-11-02. Hudson Rock, which reviewed the file without running it, found no code sending API keys, passwords, seed phrases or private keys to the reporting server; the script used the open session's trading permissions, and a signing request alone does not prove a trader signed knowingly. Ohey traced 28.6 million POL and positions from 33 wallets to the attacker's wallet between 17:10 and 18:02 UTC; DefiPrime values the POL at about $2.64 million at the 18:19 UTC price, excluding positions. These sit beside the earlier figures in the table above, each with its source.

`www.debugbear.com` failed the TLS handshake on `/` and `/blog` and returned HTTP 530 on `/status` at 16:13 UTC on 2026-11-02, so DebugBear's site is still down four days on. `status` moves to `contained`: the DNS substitution is identified and no longer resolving, the modified file's host has no DNS record, Polymarket has removed the snippet and reimbursed traders, and DebugBear reports no compromise of its own systems. The advice above stands until DebugBear publishes its post-mortem and a clean release: sites that still embed the snippet should keep it out, because the registrar-level weakness that let the hostnames be redirected has not been explained.

Sources for this update: [The Hacker News — Hackers Steal About $2.7 Million From Polymarket Traders via Hijacked DebugBear Script](https://thehackernews.com/2026/11/hackers-steal-about-27-million-from.html) (fetched 2026-11-02: 2026-11-01; DebugBear's X statements as quoted, the 726/689/37 wallet counts, the $1.19 million and 5,500 figures, the 17:38 and 18:05 UTC times, Hudson Rock's, Ohey's and DefiPrime's findings, the no-DNS-record check); [SecurityWeek — Polymarket Returns $3.9 Million to Traders as DebugBear Cites DNS Hijack](https://www.securityweek.com/polymarket-returns-3-9-million-to-traders-as-debugbear-cites-dns-hijack/) (fetched 2026-11-02: 2026-11-02; the registrar statement, the $3.9 million total, Polymarket's "compromised 3rd party provider" statement, the promised post-mortem, Hudson Rock's no-key-theft finding); `www.debugbear.com` `/`, `/blog`, `/status` — requested 2026-11-02 16:13 UTC: TLS handshake failure, TLS handshake failure, HTTP 530.
