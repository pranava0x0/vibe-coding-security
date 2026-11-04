---
id: 2026-11-plerdy-seo-tracker-click-script-compromised-august-27-to-september-3-check-embeds-and-visitors
title: "Plerdy SEO Tracker click script served modified code from 2026-08-27 to 2026-09-03 (Sekoia, APT29): check whether your site embedded it and tell visitors"
kind: malicious-artifact
date_disclosed: 2026-11-04
last_updated: 2026-11-04
severity: medium
status: contained
ecosystems: [web, third-party-script, web-analytics, seo]
tools_affected: ["any website that loads Plerdy's SEO Tracker or click-tracking script from the vendor's hosts", "visitors to those sites on iOS and Android between 2026-08-27 and 2026-09-03 who were not on current OS and browser versions", "web apps whose session cookies were readable to a page script during the window"]
tags: [malicious-artifact, third-party-script, web-analytics, supply-chain, website-compromise, watering-hole, apt29, sekoia, ukraine, n-day-exploits]
---

## TL;DR
If a site you run loaded Plerdy's SEO Tracker click script between 2026-08-27 and 2026-09-03, remove or re-verify the embed and tell visitors who used iOS or Android devices on older OS or browser versions during that window that their session cookies on your site may have been taken. Invalidate sessions issued during the window, and advise affected visitors to update their devices and rotate saved passwords, in particular Wi-Fi credentials.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Third-party website script | Plerdy SEO Tracker click-tracking file `public/js/click/main.js`, loaded from the vendor's `a.plerdy.com` host | the copy served from 2026-08-27 to 2026-09-03 (no version number; the file is fetched live) | re-verify the embed against the vendor's current file, or remove it; Sekoia reports no vendor statement | the vendor's script is served live, so a site that still embeds it loads whatever the vendor serves today (2026-11-04); no registry record applies | none; Sekoia report 2026-11-04 |

Sekoia says thousands of websites loaded the tracker, most of them Ukrainian, including army, special-forces and military-equipment sites, and that the campaign separately compromised or cloned other sites in the US, Ukraine, the Czech Republic and Bulgaria, which are a different vector from the Plerdy file. The Hacker News (2026-11-04) reports the same window and discovery, attributes the activity to APT29 as Sekoia does, and notes no vendor statement. Visitors were targeted with exploits for already-fixed iOS, Android and Chrome flaws (Sekoia lists CVE-2025-43529, CVE-2024-27834, CVE-2026-20700, CVE-2025-14174, CVE-2025-43510, CVE-2025-43520, CVE-2026-3910 and CVE-2025-27038) and the report says a user on an up-to-date operating system was not affected. The discovery date is mid-October 2026; the report is dated 2026-11-04, two months after the window closed, so the status is `contained` on Sekoia's account and no fresh serving is reported.

## Am I affected?

1. **Grep your templates, tag manager and built bundles** for `plerdy` and for the vendor's host name. A tag-manager container can load the script with no reference in the repository, so check Google Tag Manager, Segment and similar containers too.
2. **Check your deploy and CDN logs** for whether the embed was live between 2026-08-27 and 2026-09-03. A site that added Plerdy after 2026-09-03 is outside the window.
3. **Identify the exposed visitors:** iOS and Android sessions during the window on devices not on current OS and browser versions. Server logs with user agents give the population; the exploits were platform-specific.
4. **Session cookies set during the window** on those visitors' browsers are the data to treat as exposed, together with anything a page script on your site could read.

## If you are affected

- Remove the embed, or re-verify it against the vendor's current file and keep a hash of what you expect to load. See [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md) for the session-invalidation and notification steps.
- Invalidate sessions issued to the exposed visitor population during the window and force re-authentication.
- Tell visitors in the exposed population to update iOS, Android and Chrome, to rotate passwords saved on those devices, including Wi-Fi passwords, and to review accounts they were signed into on your site. Sekoia says site operators can contact their national CERT for the indicators, which it shares under TLP:AMBER.
- If your site is in the categories Sekoia names (defence, military recruitment, Ukrainian public sector), treat the embed window as a targeted intrusion attempt against your visitors, not a generic infection, and involve your CERT.

## Prevention

- Load third-party scripts with Subresource Integrity where the vendor supports a pinned file, and self-host analytics where you can. See the [supply-chain attack surface map](../prevention/supply-chain-attack-surface.md).
- Keep a list of every third-party host your pages load, with the date each was added, so a vendor compromise window can be matched to your deploy history in minutes. This is the second third-party-script compromise in this corpus in a week, after [DebugBear's RUM snippet](2026-10-debugbear-rum-snippet-compromise-polymarket-drain-remove-the-snippet.md).

## Sources
- [Sekoia — Poisoned Source: APT29 watering holes target mobile devices with n-day exploits](https://www.sekoia.com/blog/poisoned-source-apt29-watering-holes-targets-mobile-devices-with-n-day-exploits) — fetched 2026-11-04 (2026-11-04, Amaury Garçon, Félix Aimé, Robin Kwiatkowski, Sekoia TDR): the vendor and file, the window, the site categories, the discovery, the CVE list, the up-to-date-OS statement, the CERT coordination; fetched for artifact, dates and remediation only.
- [The Hacker News — APT29-Linked Hackers Hijack Web Analytics Script to Deliver iOS and Android Exploits](https://thehackernews.com/2026/11/apt29-linked-hackers-hijack-web.html) — fetched 2026-11-04 (2026-11-04): the same window and discovery, the Sekoia credit, no vendor statement.
- Not fetched: any Plerdy page. Sekoia reports no vendor statement and none was looked for beyond the two sources above.
- Related in this corpus: [DebugBear RUM snippet compromise](2026-10-debugbear-rum-snippet-compromise-polymarket-drain-remove-the-snippet.md).
