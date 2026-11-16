---
id: 2026-11-lovable-apps-supabase-records-readable-without-login-crissy-field-common-crawl-study
title: "Crissy Field study: 24,664 Lovable-built sites returned Supabase records without login; 7,403 held tables with email addresses"
date_disclosed: 2026-11-02
last_updated: 2026-11-16
severity: high
status: unconfirmed
ecosystems: [lovable, supabase, postgres, web, saas]
tools_affected: ["apps built with Lovable that store data in Supabase", "Supabase projects queried from the browser with the project's public key", "apps built with other generators on the same browser-to-database pattern"]
tags: [vibe-platform, data-exposure, supabase, row-level-security, lovable, pii, misconfiguration, researcher-study, single-research-firm]
---

## TL;DR
Crissy Field GmbH, a German security firm, reports that 24,664 websites built with Lovable sent Supabase database records to any visitor on page load, with no login. Read-only requests with the same public key found email addresses in 10,560 tables on 7,403 of those sites. Examples include more than 80,000 profiles and more than 200,000 chat messages from one forum, and more than 1,000 records with identity document details. There is no CVE and no platform fix. If you built an app with Lovable and Supabase, check every table's access rules today. `status` is `unconfirmed` because every count comes from one firm.

## What happened

Crissy Field used Common Crawl data to identify 159,041 Lovable projects published between December 2025 and September 2026. Of those, 34,545 used Supabase. The firm did not examine Lovable's own database feature, introduced in late 2025.

| Step in the firm's count | Number | What it means |
|---|---|---|
| Lovable projects found in Common Crawl | 159,041 | the sample, which the firm says is not representative of all Lovable apps |
| Projects using Supabase | 34,545 | the subset examined |
| Sites that returned database records on load, without login | 24,664 | records of any kind, not only personal data |
| Sites where further read-only requests found email addresses | 7,403 (in 10,560 tables) | 30% of the 24,664, not of all Lovable apps |

The firm states the limits itself. The 30% figure is not a confirmed leak rate. Email addresses can be public contact addresses or test data. The method misses personal records that carry no email address. Only parts of each dataset were retrieved. The firm could not establish whether any data had been misused, and it withholds access details.

The report names examples without naming the operators: a German lifestyle forum with more than 80,000 profiles and more than 200,000 chat messages, a service provider with more than 1,000 records holding identity document details including passport numbers, and a provider with 280,000 email addresses. It also lists tickets, payment information, contracts, invoices, photo albums and internal WhatsApp communications.

The report is undated. It says Handelsblatt reported the findings on 2026-11-02 and that its own figures are more recent than that article. Techzine covered it on 2026-11-04. It reached the Hacker News front page on 2026-11-14 with 995 points.

**Cause.** The report does not name a mechanism. It says the database integrations "follow recurring patterns". Techzine writes "poorly configured Supabase databases". On Hacker News, a commenter under the handle `igorandri`, who says they are Head of Security at Lovable, wrote that "the root cause in these apps was insufficent Row-Level Security" (spelling as posted). That is a forum comment under an unverified handle. No statement on Lovable's own site was opened.

**What the commenter says Lovable offers and plans.** A scan of every app before publish and a deeper scan, both free. A "Fix" action on findings. An auto-fix option. An option to block publishing when critical findings exist, which the commenter says will come to all tiers. The commenter also wrote that many of the projects came from earlier builds and older models, and that Lovable is considering a path to block apps that do not fix findings after notice. None of this is a shipped default the report confirms.

**Relation to earlier records.** Trending Topics writes that Lovable added its security scan after a similar flaw became public in 2025 as CVE-2025-48757. This corpus tracks the class in [ongoing-vibe-platform-exposure.md](ongoing-vibe-platform-exposure.md). This file is the first large count for 2026 projects.

## Am I affected?

- You published an app built with Lovable between December 2025 and September 2026, or earlier, and it stores data in Supabase.
- Your app's browser code talks to Supabase directly. This is the default pattern for these apps, and the project's public key is in the page by design.
- Any table holds personal data, messages, documents, payments or identity records.

Checks, in order:

1. Open the app in a private browser window without signing in. Open the browser's network panel and reload. If responses from your Supabase project contain rows a stranger should not see, the table is exposed.
2. In the Supabase dashboard, review each table. Confirm that Row Level Security is enabled and that every policy limits rows to the signed-in user or to the role that needs them.
3. In Lovable, run the security scan and read every finding, including the ones not marked critical.

## If you are affected

1. Fix the access rules first. Use the scan's "Fix" action or write the policies yourself, then repeat check 1.
2. Assume the data was read. The firm could not establish misuse, and public tables are reachable by anyone.
3. Rotate any secret stored in an exposed table.
4. If personal data was readable, treat it as a possible notifiable breach. Check your obligations under GDPR or your local law and get advice. This step is this file's advice.
5. Repeat the checks after every significant change, as the report recommends. The report says automated checks "are no substitute for a professional security assessment".

## Prevention

- Enable the access rules before the first real record is stored. The Hacker News commenter says adding them later to a complex app breaks things, which is why owners defer the fix.
- Do not store identity documents, payment data or private messages in a table the browser queries directly unless a tested policy protects it.
- See [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md), [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

One research firm. The outlets below report the same study.

- [Crissy Field: Lovable: Many Apps Built on the Platform Expose Sensitive Data](https://www.crissyfield.de/research/lovable-en/), undated, fetched 2026-11-16: the method, every count, the examples, the stated limits, the reference to Handelsblatt's 2026-11-02 article.
- [Techzine: Thousands of Lovable apps are leaking personal data](https://www.techzine.eu/news/security/145550/thousands-of-lovable-apps-are-leaking-personal-data/), 2026-11-04, fetched 2026-11-16: the same counts, the phrase "poorly configured Supabase databases", no vendor statement.
- [Trending Topics: Apps Built With Lovable Left Sensitive Data Exposed](https://www.trendingtopics.eu/lovable-apps-sensitive-data-exposed/), 2026-11-14, fetched 2026-11-16: the reference to CVE-2025-48757 and a summary of Lovable's position that it attributes to Cybernews.
- Hacker News item 50499017, 2026-11-14, 995 points, read 2026-11-16 through the Algolia items API: the comments by `igorandri` dated 2026-11-14 and 2026-11-15.
- Not opened: the Handelsblatt article, the Cybernews article, any page on lovable.dev, any Supabase statement.
