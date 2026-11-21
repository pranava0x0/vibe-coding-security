---
id: 2026-11-portkey-ai-gateway-customer-notice-api-key-compromised-logs-credentials-taken
title: "Portkey AI Gateway: a customer notice relayed on Hacker News says logs and credentials were taken 2026-11-05 to 11-10; no public vendor page"
date_disclosed: 2026-11-20
last_updated: 2026-11-21
severity: high
status: unconfirmed
ecosystems: [ai-gateways, llm-api, saas, provider-keys]
tools_affected: ["Portkey AI Gateway hosted accounts", "provider API keys and tokens stored in Portkey", "prompts and responses held in Portkey gateway logs"]
tags: [ai-gateway, breach, vendor-incident, relayed-notice, single-source, credentials, logs, provider-keys]
---

## TL;DR

A [Hacker News user](https://news.ycombinator.com/item?id=50585039) posted an email dated 2026-11-20 that says an unauthorized party took customer data from Portkey AI Gateway between 2026-11-05 and 2026-11-10. The email lists account emails, gateway logs and "Credentials (including API keys and tokens)". Portkey has no public page for it, and nothing else confirms it. Sign in to Portkey by typing the address yourself and look for the incident banner. Do not follow links in the email.

## What happened

The post is the only source. It reproduces an email with the subject "IMPORTANT NOTICE: Security Incident Affecting Portkey AI Gateway". The poster shows the sender as "Portkey Product Security" at a `paloaltonetworks.com` address.

As relayed, the email says:

- "an unauthorized third party compromised a Portkey AI Gateway API key and gained access to customer data in our environment."
- Data was taken "from backend storage providers used in the Portkey AI Gateway infrastructure" between 2026-11-05 and 2026-11-10.
- The data may include account usernames and email addresses, Portkey AI Gateway logs, and credentials including API keys and tokens.
- The vendor engaged Unit 42 to investigate.
- A customer can download a file of metadata for the affected records from a banner in the Portkey portal.

What was checked on 2026-11-21:

- `status.portkey.ai` listed no security incident.
- The Portkey blog index showed no post about it.
- A web search returned no outlet coverage.
- The Hacker News item had 3 points and no comments.

The email asks the reader to click a link and sign in. A real notice and a phishing message both look like that. This file is `unconfirmed` for that reason.

## Am I affected?

- You have a hosted Portkey account. The email gives no count of affected accounts.
- You received this email. Check its headers before trusting it.
- Sign in at the address you normally use and look for a banner titled "Portkey Security Incident". The banner's presence is the confirmation.
- Self-hosted deployments of the open-source gateway are not mentioned in the email.

## If you are affected

1. If the banner is there, download the file it offers. It identifies your affected records.
2. Rotate every provider key stored in Portkey: OpenAI, Anthropic, cloud and any other. Rotate Portkey API keys too. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
3. Treat prompts and responses in the gateway logs as read. Rotate any secret that appeared in them.
4. Check provider billing and usage from 2026-11-05 for calls you did not make.

If the banner is not there, report the email to Portkey support and change nothing because of it.

## Prevention

- A gateway holds every provider key. Give it keys scoped to the gateway, with spend limits. See [credential hygiene](../prevention/credential-hygiene.md).
- Turn off prompt and response logging where you do not need it, or set short retention.

## Sources

- [Hacker News item 50585039, "Portkey Security Incident"](https://news.ycombinator.com/item?id=50585039): posted 2026-11-21 01:52 UTC, 3 points when read through the Algolia items API. The email as a recipient posted it.
- [Portkey status page](https://status.portkey.ai/): read 2026-11-21. No security incident listed.
- Single source: one recipient's post. No vendor page, outlet or second recipient was found.
