---
id: 2026-11-grok-build-apps-anyone-with-the-link-default-35578-open-apps-claroc
title: "Grok-built apps on grok.me: 35,578 of 37,571 open without sign-in, some holding internal data (Claroc); vendor disputes the default"
date_disclosed: 2026-11-10
last_updated: 2026-11-11
severity: high
status: unconfirmed
ecosystems: [vibe-coding-platforms, grok, ai-app-builders, generated-apps]
tools_affected: ["apps published from Grok's chat-based app builder (Build mode) at `<name>.grok.me` with access set to \"Anyone with the link\"", "organisations whose staff publish internal tools from personal or unmanaged Grok accounts", "Grok-generated team sign-in code (one researcher test app: the membership check always passed)"]
tags: [vibe-platform-exposure, grok, share-default, public-by-default, pii, plaintext-passwords, generated-auth, single-researcher, vendor-disputes]
---

## TL;DR
Claroc (2026-11-10) reports that 35,578 of 37,571 live apps built with Grok's app builder opened for anyone with no sign-in, and that about 1 in 10 of the open apps held internal business or personal data. The researchers say the publish step preselects "Anyone with the link". The vendor told a reporter that apps are private until shared and that employee accounts default to "Only you"; it removed 24 apps built by its own staff and left the rest. If you or your team published a Grok app, open its address in a private browser window now. If it loads, set access to "Invited users" or "Only you". Every count here is Claroc's alone.

## What happened

**The product.** Grok's Build mode creates an app from a chat description and publishes it at its own hostname, `<name>.grok.me`. Claroc says Grok proposes four random words as the name and about half of the names it saw were exactly that. The Hacker News notes the builder shares the "Grok Build" name with the terminal coding tool this corpus covers in [a separate file](2026-07-grok-build-silent-full-repo-upload-xai-storage.md). They are different products.

**Claroc's counts, as its post prints them.**

| Step | Figure |
|---|---|
| App addresses tried | 43,551 (the methods section says 43,601 names; the post does not reconcile the two) |
| Still online | 37,571 |
| Opened with no sign-in | 35,578 (94.7%) |
| Returned HTTP 401 | 1,993 (5.3%) |
| Open apps with sensitive, internal or personal data | "about 1 in 10" |
| Estimated to hold material rated high or critical | "roughly 2%" |
| Sample-based estimate of apps with private data | "roughly 650 to 800" |
| Apps built by the vendor's own staff | 24 |
| Other organisations identified | 30, of which 26 have more than 1,000 employees and 6 are in the Fortune 500 |

"About 1 in 10" of 35,578 and "roughly 650 to 800" are both in the post and do not obviously agree. This file prints both and derives nothing. Examples the post gives: a hospital staff roster of more than 3,500 employees, a timesheet app with 18 accounts and plain-text passwords in its code, and a sales territory map covering 594 accounts.

**Why the apps were open, per Claroc.** In the paid account the researchers used, the publish panel offered "Anyone with the link", "Invited users" and "Only you", with "Anyone with the link" preselected. Each app is its own DNS name, so opening one leaves a record that DNS-history services index. A random-word name therefore does not keep an app private.

**Two test apps.** Claroc built two apps with invented data. One with no sign-in, published at the default, was readable and writable by anonymous visitors. In the other, Grok-generated team sign-in code added the signed-in user to the team before checking membership, so an outside account could view, edit and delete records. Both findings are from the researchers' own apps. Claroc says it did not sign in to, write to or submit forms on anyone else's app, and used no password or key it found.

**The vendor's position.** The Hacker News reports the company's reply: apps stay private until the creator shares them, publishing takes several steps that include choosing an access setting and accepting a disclaimer, and employee accounts default to "Only you". Claroc's post says the company answered a reporter on 2026-11-10 and had not replied to its report of 2026-11-08, and that it took down the 24 staff apps and not other users' apps. Claroc's answer to the vendor is that the access step already had "Anyone with the link" selected.

**Why `unconfirmed`.** One research firm, which sells tools for finding AI-built apps, produced every number. The outlet reports the same post plus the vendor's reply. The vendor confirms the three access settings exist and disputes that apps become public by default. No second researcher has repeated the count. The reader's check below does not depend on who is right.

## Am I affected?

1. **List your Grok apps.** In Grok, open each app you published and read its access setting.
2. **Test from outside.** Open the app's `grok.me` address in a private browser window with no Grok session. Claroc reports that "Only you" returned 401 to a stranger for both the page and its data.
3. **Test sign-in from outside.** If the app has team sign-in, try an account that should not have access. If it gets in, the generated check is not checking.
4. **Ask your organisation.** Internal tools built by colleagues on personal accounts do not show up in any company inventory.

## If you are affected

- Set the app to "Invited users" or "Only you", or unpublish it. Claroc reports unpublishing took effect within seconds.
- If the app held personal data and was open, treat the data as read. The address was discoverable while the app was live. Your notification duties depend on the data and your jurisdiction.
- Change any password that was stored in the app or its code, anywhere it was reused. Rotate API keys the app's scripts contained. [Credential hygiene](../prevention/credential-hygiene.md) covers where keys should live instead.
- Recheck access after later prompts. Claroc notes that an app can start harmless and gain sensitive data as it is edited.

## Prevention

- **Treat a share setting as a deployment decision.** Read it before every publish. A preselected option is still a choice you made.
- **A hostname is not a secret.** Anything served at its own subdomain should be assumed findable.
- **Test generated auth with an account that should fail.** [Auditing a vibe-coded repo](../playbooks/auditing-a-vibe-coded-repo.md) has the checks. The pattern across builders is tracked in [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md).

## Sources

- [Claroc: GhostShares 2, Grok Apps Exposed xAI's Business Secrets and People's Private Data](https://blog.claroc.io/ghostshares-grok-build-apps/), fetched 2026-11-11: dated 2026-11-10, Asaf Aprozper; every count above; the default setting; the two test apps; what was and was not tested; the disclosure timeline of 2026-11-08 to 2026-11-10; the vendor's reply as Claroc paraphrases it.
- [The Hacker News: Over 35,000 Grok-Built Apps Exposed Online, Some Leaking Confidential Data and Passwords](https://thehackernews.com/2026/11/over-35000-grok-built-apps-exposed.html), fetched 2026-11-11: dated 2026-11-11; the vendor's reply as the outlet reports it; the naming overlap with the terminal tool. Outlet coverage of the same post, not a second finding.
