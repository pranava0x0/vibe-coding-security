---
id: 2026-11-apify-internal-systems-breach-account-credentials-accessed-oauth-connections-revoked
title: "Apify breach: an intruder used a compromised credential to obtain account credentials on 2026-11-09 and 11-10; rotate API tokens and reconnect GitHub"
date_disclosed: 2026-11-11
last_updated: 2026-11-14
severity: high
status: active
ecosystems: [apify, saas, web-scraping, ai-agents, oauth, github]
tools_affected: ["Apify platform accounts (api.apify.com, Actors)", "Apify Actors built from private GitHub repositories", "third-party integrations connected to Apify through OAuth", "agents, workflows and CI jobs that hold an Apify API token", "accounts that sign in to Apify with Google or GitHub"]
tags: [breach, vendor-incident, apify, account-takeover, credential-theft, oauth, github-integration, api-tokens, web-scraping, investigation-ongoing]
---

## TL;DR
Apify, the web scraping and automation platform, says an unauthorized third party accessed parts of its internal systems on 2026-11-09 and 2026-11-10, used a compromised credential to obtain account credentials, and accessed related Apify accounts. Apify has emailed the customers whose personal information or stored data was accessed, and revoked some OAuth connections including GitHub. The investigation is ongoing. If you got the email, follow it. Either way, rotate Apify API tokens used by agents and pipelines, and reconnect GitHub if you build Actors from private repositories.

## What happened

Apify's status page carries one incident, "Security incident", with three updates when read on 2026-11-13. Times are as the page prints them (CET).

| Posted | What Apify said |
|---|---|
| 2026-11-11 20:46 | "On 9 and 10 November 2026, an unauthorized third party gained access to parts of Apify's internal systems. We detected the activity on 11th November at 12:13 UTC, cut off access, and started an investigation that is still ongoing." Some OAuth connections to external integrations, including GitHub, were revoked as a precaution. "If our investigation shows that your tokens were affected, we will rotate them on your behalf and notify you." |
| 2026-11-12 12:08 | "On 9 and 10 November, an unauthorized third party used a compromised credential to obtain a number of account credentials and accessed related Apify accounts. This access path is closed, and we have detected no further activity from the attacker since 11 November." Apify rotated "various critical internal secrets" and notified authorities. Of the revoked OAuth connections: "Our investigation has not found that these connections could be used as an attack vector." |
| 2026-11-12 17:16 | "We have notified customers whose personal information or stored data was accessed in this incident." And: "If you haven't received an email from us, we have not identified your account as affected so far." |

The page promises a post-mortem after remediation. It lists the affected components as the API, Actors and General. It gives no count of affected accounts and does not say how the first credential was compromised.

SecurityWeek (2026-11-13) reports the incident from the status page and adds a list of exposed data, which it takes from a breach notification a customer shared on Reddit: names, email addresses, billing details, account activity, IP addresses, salted password hashes, two-factor recovery codes, phone numbers, authentication tokens tied to Google and GitHub sign-ins, and partial payment card data (cardholder name, expiry, last four digits). This list is SecurityWeek's account of a relayed notification. Apify's status page does not print it, and this sweep could not open the Reddit thread. SecurityWeek also says Apify has 91,000 customers and "has not disclosed the number of compromised customer accounts."

`status` is `active` because the vendor says its investigation is ongoing and scope may change. The vendor's own sentence is that the access path is closed.

## Am I affected?

- You have an Apify account. Search your mailbox for a notification from Apify dated 2026-11-11 or later. Apify says accounts with no email have not been identified as affected so far, and that this may change.
- You build Actors from private GitHub repositories. Apify says it revoked some OAuth connections "including GitHub" and tells these users to reconnect it.
- An agent, an MCP client, a workflow tool or a CI job holds an Apify API token. Find where tokens live:

```bash
env | grep -i apify                                  # e.g. APIFY_TOKEN
grep -rIl -i 'apify' .env* .github/workflows 2>/dev/null | head
grep -rn -i 'apify' ~/.claude.json .mcp.json .cursor/mcp.json 2>/dev/null | head
```

- You sign in to Apify with Google or GitHub.

## If you are affected

Apify's instructions, from the status page:

1. "If you got an email from us, follow its instructions."
2. "If you build Actors from private GitHub repos, reconnect GitHub: open an Actor built from GitHub → 'Change provider' → GitHub → authorize (once per account and per organization)."
3. "If prompted, reconnect your integrations."

This file's advice, which Apify has not stated:

4. Create new Apify API tokens, update the agents and pipelines that use them, and delete the old ones. Prefer scoped tokens.
5. Change the Apify password, and regenerate two-factor recovery codes. If the old password was used elsewhere, change it there too.
6. In GitHub and Google, review the authorized applications and sessions for Apify and remove any you do not recognise. [If your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) lists the GitHub audit steps.
7. Rotate any third-party secret you stored in Apify, such as Actor environment variables, proxy credentials or API keys in Actor input. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) covers the order.
8. Review recent Actor runs, schedules and webhooks in the account for anything you did not create.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): give each agent or pipeline its own scoped token so one can be revoked without stopping the rest.
- Do not keep long-lived third-party secrets in a scraping platform's inputs or environment when a short-lived one works.
- Grant a platform's GitHub App access to the repositories it builds from, not to the whole organisation.

## Update 2026-11-14

Apify posted a fourth update on 2026-11-13 at 17:36 CET, read on 2026-11-14. The investigation and response are ongoing, so the status stays `active`.

- Apify says it now stores API tokens only as hashes, has added network restrictions between internal services and has strengthened internal authentication. A security review of its stack and log analysis continue.
- Apify recommends restricting storage access in Console under Settings, General resource access. It says that while a storage is open, anyone who knows a storage ID can read that storage.
- Apify warns about phishing and says it will never ask for passwords, 2FA codes or payment details.
- The next update is due within 72 hours. A post-mortem with root cause and remediation is promised within a week.

SecurityWeek's article, re-read on 2026-11-14, cites Apify's figure of 91,000 customers worldwide. That is Apify's customer count, not a count of affected accounts. Apify has given none.

## Sources

- [Apify status: Security incident](https://status.apify.com/incidents/sxd1dj5j6749), fetched 2026-11-13: the three updates quoted above, the affected components.
- [SecurityWeek: Apify Confirms Customer Data Accessed in Cyberattack](https://www.securityweek.com/apify-confirms-customer-data-accessed-in-cyberattack/), fetched 2026-11-13 (dated 2026-11-13): the data list attributed to a customer-shared notification, the customer count, the statement that no account count is disclosed.
- [Apify status: Security incident](https://status.apify.com/incidents/sxd1dj5j6749), re-read 2026-11-14: the fourth update, dated 2026-11-13 17:36 CET. Hacker News item 50486258 (2026-11-13, 96 points) links the page and was seen through the Algolia feed only.
- Hacker News item 50472323, seen 2026-11-13 through the Algolia search feed: the status page submitted on 2026-11-12, 11 points. The item page and its comments were not opened.
- Not opened: the Reddit thread SecurityWeek cites (`reddit.com` is not fetchable from this sweep) and Apify's notification email.
