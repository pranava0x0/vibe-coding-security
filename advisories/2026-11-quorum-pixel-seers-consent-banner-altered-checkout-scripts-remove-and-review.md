---
id: 2026-11-quorum-pixel-seers-consent-banner-altered-checkout-scripts-remove-and-review
title: "Altered Quorum marketing pixel and Seers consent banner settings on store checkouts: review your embeds and tell affected shoppers"
kind: malicious-artifact
date_disclosed: 2026-11-27
last_updated: 2026-11-28
severity: medium
status: unconfirmed
ecosystems: [web, third-party-script, e-commerce]
tools_affected: ["sites that load the Quorum marketing pixel", "sites that use a Seers consent banner", "any checkout page that loads third-party scripts"]
tags: [malicious-artifact, third-party-script, supply-chain, website-compromise, payment-page, single-source]
---

## TL;DR

[InfoHawk reports](https://www.infohawk.com/news/2026-11-27-black-friday-webrtc-skimmer) that an altered Quorum marketing pixel, edited Seers consent banner settings and an altered file on one retailer's own CDN loaded unwanted code on five store checkouts, all removed by 2026-11-25. If your site loads either vendor's script, check it for the files below, and treat card and contact details entered at an affected mobile checkout as exposed.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| third-party script | Quorum marketing pixel, `pscript.js` | the copy served before 2026-11-24 21:09 UTC, start not stated | Quorum restored a clean pixel, per InfoHawk | not checked by this sweep | none |
| third-party script | Seers consent banner config, `cb.js` | configs whose privacy-policy link field holds more than a URL | review and re-save the banner settings | removed on two stores on 2026-11-24 14:25 UTC, per InfoHawk | none |
| first-party CDN file | a file on Revolve's own CDN, serving revolve.com and fwrd.com | start not stated | Revolve confirmed removal on 2026-11-25, per InfoHawk | not checked by this sweep | none |

InfoHawk names five stores: Lascana, Samsonite, American Tourister, Revolve and FWRD. It says it saw test card details leave the page on one of them, Lascana. It says it does not know how many shoppers' details were captured, if any. InfoHawk's page is the only source. It quotes Revolve and says Quorum confirmed the removal. Samsonite, American Tourister and Seers did not reply to it.

## Am I affected?

Site owners, from InfoHawk's checklist:

- Search page source, tag manager containers, consent banner settings and CDN files for scripts named `Insds.js` or `gtage.js`.
- If you load the Quorum pixel, read the last line of the `pscript.js` your site serves and look for a storage bucket you do not recognise.
- If you use Seers, open your banner config and check that every URL field holds only a URL.
- Test the payment step on a phone-sized touch screen. InfoHawk says desktop checks and homepage scans miss it.
- Search your pages for the strings `KghRtc`, `rtc-signal-v1` and `quickfetch`.

Shoppers: you are in scope if you entered payment details on a phone or tablet at one of the five stores before the removals on 2026-11-24 and 2026-11-25. InfoHawk says the code was planted in the week before Black Friday and gives no start date.

## If you are affected

- Site owners: remove the altered script or setting, then follow [if your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md). Work out the dates the script was live from your CDN and tag manager history, and notify shoppers who paid in that period.
- Rotate the credentials for the tag manager, consent banner and CDN accounts that could edit the altered file.
- Shoppers: check card statements, report charges you do not recognise to the issuer and ask for a new card number.

## Prevention

- InfoHawk's first step for site owners is a `connect-src` rule on every payment page that lists only the hosts you use.
- Load as few third-party scripts as possible on payment pages, and review who can edit tag manager and consent banner settings. See [supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources

- [InfoHawk, "Credit card skimming scripts using WebRTC found on popular shopping sites", 2026-11-27](https://www.infohawk.com/news/2026-11-27-black-friday-webrtc-skimmer), read 2026-11-28. Single source. The stores, vendors, removal times, file names, strings and site-owner steps.
- [Hacker News item 50668145](https://news.ycombinator.com/item?id=50668145), 567 points on 2026-11-28. Where the sweep found the report.
- Not opened: any Quorum, Seers, Revolve, Lascana or Samsonite statement.
