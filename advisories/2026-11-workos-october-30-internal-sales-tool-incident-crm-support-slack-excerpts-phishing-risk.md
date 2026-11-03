---
id: 2026-11-workos-october-30-internal-sales-tool-incident-crm-support-slack-excerpts-phishing-risk
title: "WorkOS incident 2026-10-30: an internal sales API exposed CRM contacts, support summaries and customer Slack excerpts; production untouched, expect targeted phishing"
date_disclosed: 2026-11-02
last_updated: 2026-11-03
severity: medium
status: ongoing
ecosystems: [workos, auth-sdk, saas-vendor, crm, slack, salesforce, snowflake]
tools_affected: ["WorkOS customers (AuthKit, SSO, Directory Sync, Vault, Airlock) whose contact details, account history, support tickets and shared-Slack conversations sat in the vendor's sales and marketing tools", "anyone at those companies who could receive a convincing email that quotes a past WorkOS support conversation"]
tags: [vendor-incident, auth-vendor, crm-data, support-data, slack-excerpts, phishing, social-engineering, ai-assisted-attack, recipient-relayed-notice, hacker-news, no-production-impact]
---

## TL;DR
WorkOS, the authentication and SSO vendor behind many generated apps' login flows, says an unauthorized actor reached "an internal API used by our sales and marketing tools" on 2026-10-30, with access to its Salesforce and Snowflake data: business contact details, account histories, "summaries and excerpts from sales calls, support discussions, and customer Slack conversations", and operational metadata such as "product usage and connection or directory health". WorkOS says "There is no evidence that WorkOS application data was accessed" and no evidence production services were touched, so no key, user or session needs rotating because of this incident. The exposure is what an attacker can write with your support history: WorkOS tells customers to "verify unexpected requests before sharing sensitive information or taking action", and that is the action for this file.

## What happened

**The vendor's bulletin.** WorkOS published "October 30th, 2026 Data Security Incident" on 2026-11-02. It identified "unauthorized access to an internal application used by its sales team" on 2026-10-30, disabled external access to the application, "retained an independent digital forensics and incident response firm", and began "a broader review of access controls on internal tools". The data categories it lists: business contact details (names, emails, phone numbers, job titles, company affiliations) from CRM systems; business account and relationship information including account histories; customer communications, "including summaries and excerpts from sales calls, support discussions, and customer Slack conversations"; and operational metadata, "such as product usage and connection or directory health". It says "Our current analysis indicates this incident affected only CRM and customer support data", that it is "reviewing the affected records to determine the impact for individual organizations", and that it "will contact affected customers directly". No count is given.

**The notification, read through a recipient.** The bulletin was preceded by a customer email, which a recipient reproduced on Hacker News (item 50345712, 75 points) with the remark that it was "not on their website or Trust center yet". The email, as reproduced, adds timing and scope the bulletin omits: "On October 30, 2026, at 16:39 UTC, WorkOS detected anomalous traffic to an internal business system"; "The unauthorized actor gained access to an internal API used by our sales and marketing tools"; the API "had access to" Salesforce and Snowflake data; and "We have no evidence that your application data was accessed." The recipient paraphrases the email as attributing the activity to the ARTEX framework and to addresses in Hong Kong and China. Those two claims are the recipient's reading of the email and are not in the bulletin. WorkOS CEO Michael Grinich replied in the thread with the bulletin link, wrote that "No customer platform data was accessed" and that the incident was "isolated to internal GTM systems", and offered calls through `security@workos.com`. Commenters asked for the initial access vector and whether lateral movement was ruled out; neither was answered in the thread.

**The attack tool.** The bulletin says the actor used "an AI-assisted offensive security framework" to automate reconnaissance and exploitation attempts and links Wiz, Google and CrowdStrike reports on agentic attacks whose URLs name ARTEX, without naming it in the body. Runtimewire (2026-11-02) and Cryptika (2026-11-03, crediting Cyber Security News) both print ARTEX in their headlines; Runtimewire cites Grinich's X post as its primary and that post was not opened this run. Which tool an intruder ran changes nothing for a WorkOS customer, and this file records it only because every outlet leads with it. Offensive-use detail is outside this corpus.

**Why an auth vendor's CRM matters to this audience.** WorkOS customers are companies whose login, SSO and directory-sync integrations WorkOS supports, often through shared Slack channels. A message that quotes last month's support thread about your SAML connection, from a sender who knows your account manager's name and your directory's health status, is the phishing email the bulletin warns about. Nothing in the vendor's statements says API keys, client secrets, user records or session data left WorkOS, so the risk is social, not cryptographic.

## Am I affected?

- If your company is a WorkOS customer, assume your business contacts, account history and any support or shared-Slack conversation with WorkOS staff may have been read. WorkOS says it will contact affected organizations directly; absence of an email on 2026-11-03 means the per-organization review is not finished, not that you were excluded.
- Check whether your WorkOS support channel was a shared Slack Connect channel. The bulletin names "customer Slack conversations" as a category.
- No WorkOS-issued credential is reported exposed. Rotating API keys is not required by this incident; do it if your own policy rotates after any vendor incident.

## If you are affected

- Brief the people who talk to WorkOS (engineering leads, IT, procurement) that a message referencing a real past conversation is now the expected attack. Verify any request to change an SSO connection, a redirect URI, a directory sync, a billing detail or a contact through a channel you initiate.
- Treat emails from WorkOS domains the same way; the attacker holds enough context to impersonate the vendor convincingly.
- If a request has already been acted on, follow [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md) for the auth-configuration audit and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for any key shared in a conversation.

## Prevention

- Do not paste secrets, tokens or connection strings into vendor support channels or shared Slack; a vendor's CRM and support tooling keeps them for as long as the vendor does.
- Keep vendor contacts and change procedures written down so a request that skips them stands out. See [credential hygiene](../prevention/credential-hygiene.md).

## Sources
- [WorkOS — October 30th, 2026 Data Security Incident](https://workos.com/security/bulletins/october-30th-2026-data-security-incident) — fetched 2026-11-03: 2026-11-02; the data categories, the "no evidence" statements, the actions taken, the "AI-assisted offensive security framework" sentence, the customer guidance; no count, no timeline beyond the two dates. Vendor primary.
- Hacker News item 50345712 ("WorkOS reports security breach", 75 points, 10 comments), read through the Algolia items API 2026-11-03: the notification email reproduced by the submitter (16:39 UTC detection, the internal API, Salesforce and Snowflake), the submitter's ARTEX and Hong Kong/China paraphrase, Michael Grinich's reply with the bulletin link and the "isolated to internal GTM systems" statement, the unanswered questions on initial access and lateral movement.
- [Runtimewire — WorkOS says ARTEX attack accessed internal sales tool](https://runtimewire.com/article/workos-sales-tool-breach-artex-ai-agent) — fetched 2026-11-03: 2026-11-02 18:57 CT, Ryan Merket; the CRM contacts, call summaries and Slack excerpts; Grinich's X post cited as primary and not opened here; the list of unknowns.
- [Cryptika — Hackers Use ARTEX AI to Breach WorkOS and Access Customer Slack Conversations](https://www.cryptika.com/hackers-use-artex-ai-to-breach-workos-and-access-customer-slack-conversations/) — fetched 2026-11-03: 2026-11-03, credited to Cyber Security News; confirms the bulletin does not name the framework and that the ARTEX description comes from GTIG, Mandiant and Wiz research, not from WorkOS.
- [WorkOS — blog index](https://workos.com/blog) — fetched 2026-11-03: no post about the incident as of the read; the newest posts are 2026-11-03.
- [Mallory — WorkOS Breach Exposes Sales and Support Data Through Internal Application](https://mallory.ai/stories/01a19eb9-b051-73cc-ba2e-fa100274adf1) — fetched 2026-11-03: an aggregator timeline that links only Cryptika, Cyber Security News and the HN item; it adds the statement that "traffic from Hong Kong and China does not establish attribution", which is its own.
