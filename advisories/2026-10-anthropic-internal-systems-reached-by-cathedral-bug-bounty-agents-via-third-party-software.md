---
id: 2026-10-anthropic-internal-systems-reached-by-cathedral-bug-bounty-agents-via-third-party-software
title: "Anthropic: a bug-bounty firm's agents reached sales, HR and IT systems through third-party software; no Claude conversations, source or weights, Anthropic says"
date_disclosed: 2026-10-26
last_updated: 2026-10-29
severity: medium
status: contained
ecosystems: [ai-vendors, saas, third-party-software]
tools_affected: ["Anthropic customers and partners whose business contact information sat in the affected sales systems", "Anthropic staff (meeting transcripts, compensation, Slack messages, per the Washington Post's account of Cathedral's draft report)"]
tags: [vendor-incident, anthropic, bug-bounty, third-party-saas, ai-agents-offensive, business-contact-data, disputed-account, press-primary, washington-post-paywall]
---

## TL;DR
Cathedral, a security startup founded by former DOGE staff, told the Washington Post that its AI agents got into Anthropic's internal systems in under 12 hours through vulnerabilities in third-party business software and reached meeting transcripts, salary and offer data and Slack messages; Anthropic says the access, which it cut off the same day and had already flagged, covered a limited set of sales, HR and IT systems including customer and partner business contact information and some basic user account records, and did not touch Claude users' conversations, source code or model weights. The engagement ran under Anthropic's bug bounty, which Anthropic says Cathedral breached by not disclosing the full extent of its activity. For a reader the exposure is business contact data: expect targeted phishing that knows your vendor relationship.

## What happened

**The claim.** Gizmodo (2026-10-26, Ece Yildirim) reports the Washington Post's account of a draft Cathedral report: the firm's AI agents, after several days of failed direct attempts, found paths through vulnerabilities in third-party business software that Anthropic uses, and within 12 hours reached meeting transcripts, salaries and job offers, and Slack messages. Cathedral's founders are named as Gavin Kliger, Luke Farritor, Marko Elez and Jack Stein; the firm is described as focused on military applications. The third-party software is not named in any source opened this run.

**The vendor's account.** As reported by Gizmodo and WION (2026-10-28, Anamica Singh): Anthropic confirmed access to a "limited set" of its sales, HR and IT systems, including customer and partner business contact information and some basic user account records; it says Claude users' conversations, source code and model weights were not accessed; the probing was not as quick as Cathedral suggests; the activity ran under Anthropic's bug bounty program and Anthropic accused Cathedral of violating its rules by not disclosing the full extent of its activity; it learned of the activity before Cathedral contacted it and cut off access the same day. Anthropic's statement was read through the two outlets; the channel it was issued on is not stated by either. WION adds that others linked the access to a "hygiene failure" in third-party software, unattributed.

**What this file does not have.** The Washington Post article is paywalled and was not opened. Cathedral's draft report is not public. The engagement dates are not given. Whether the business contact data was copied, and whether affected customers were notified, is not stated. Fast Company's article returned 403.

**Why it matters here.** Three things. A third-party SaaS vendor was the door into an AI vendor's corporate estate, the shape of the Vercel incident earlier this year, and the data reached was the kind that makes a convincing "your Anthropic account representative" email. The intrusion was run by agents, which is the offensive-capability story the corpus otherwise declines to file; it is here because the target holds this audience's account records. And the two accounts disagree on speed and on rules, so the figure "12 hours" is one side's claim.

## Am I affected?

- You or your company have an Anthropic sales or partner relationship. Business contact information from those systems is in the set Anthropic describes.
- There is no indication from either account that API keys, conversation data or Claude Code sessions were reached; no key rotation is indicated by the sources.

## If you are affected

1. Treat unsolicited messages that reference your Anthropic contract, seat count, contact or renewal as suspect until verified through a channel you already had.
2. Confirm any Anthropic notice through the console or your account representative rather than a link in email.
3. No credential action is indicated by the vendor's statement; this file will carry an update if Anthropic publishes one that says otherwise.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): a vendor's business systems hold your contact data; the defence is verification discipline, not rotation.

## Sources
- [Gizmodo — Former DOGE Staffers' New Startup Claims It Hacked Anthropic](https://gizmodo.com/former-doge-staffers-new-startup-claims-it-hacked-anthropic-2000830560) — fetched 2026-10-29 (2026-10-26 11:00 ET, Ece Yildirim): the Washington Post's account of Cathedral's draft report, the data categories, the third-party-software entry point, Anthropic's "limited set" statement and what it says was not accessed, the bug-bounty rules accusation, the founders.
- [WION — Anthropic hacked by AI startup comprising former DOGE staff in just 12 hours](https://www.wionews.com/trending/anthropic-hacked-by-ai-startup-comprising-former-doge-staff-in-just-12-hours-1793167439392) — fetched 2026-10-29 (2026-10-28, Anamica Singh): Anthropic learned of the activity before Cathedral's contact and cut access the same day; source code and user conversations not reached; the unattributed third-party "hygiene failure" line.
- Not opened: the Washington Post article of 2026-10-26 (paywall), Cathedral's draft report (not public), Fast Company's article (403).
- Related in this corpus: [Vercel and Context.ai OAuth supply-chain breach](2026-04-vercel-context-ai-breach.md) for the third-party-SaaS entry shape.
