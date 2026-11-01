---
id: 2026-10-northflank-security-incident-assume-all-environment-variables-decrypted-ai-keys-abused
title: "Northflank security incident: assume every environment variable was decrypted; customers report AI API keys abused (2026-10-30)"
date_disclosed: 2026-10-30
last_updated: 2026-11-01
severity: critical
status: active
ecosystems: [paas, kubernetes, docker, vibe-platform]
tools_affected: ["Northflank (all customers: workload secrets, secret groups, global secrets; add-on credentials for Postgres, MongoDB, MySQL, Redis, MinIO and RabbitMQ; AI provider keys stored on the platform)"]
tags: [vibe-platform, data-breach, env-vars, secrets-exposure, paas, ai-api-keys, rotate-everything, black-october, wiz]
---

## TL;DR

Northflank, a deploy-from-Git platform for containers, databases and jobs, told customers on 2026-10-30 to "Assume all environment variables have been decrypted. Disable/rotate all keys." The same day its status page said "Multiple users are confirming that their AI keys have been used." As of 2026-11-01 the incident is still "Identified" with seven platform components in major outage, no root cause has been published, and the instruction has not changed: rotate every secret you ever stored on Northflank, at the issuer, and check your AI provider usage and billing.

## What happened

All times are UTC and come from Northflank's status page, which lists the incident as "Security incident" affecting seven components.

- **2026-10-30, 11:43.** Wiz sends Northflank a threat alert. Engineers review it at 11:44. An "initial network policy patch" goes out at 12:02, with "additional patching deployed" at 12:50 and 13:05, and Wiz's incident response team is asked for support at 13:00.
- **13:40 (Investigating).** First public update: "Rotate environment variables immediately."
- **13:58 (Identified).** "Assume all environment variables have been decrypted. Disable/rotate all keys."
- **15:12.** Secret rotation for Postgres and MongoDB add-ons is enabled for all users; users who enabled public exposure on add-ons are told to turn it off; the rotation instruction now names secrets on workloads, secret groups and global secrets. The update says multiple users confirm their AI keys have been used.
- **19:28.** "Our investigation is ongoing. We have no further confirmed findings to share at this time." Guidance unchanged.
- **23:38.** Users report unauthorized use of AI API keys stored on the platform. Northflank tells customers who have not rotated user-provided secrets to revoke them with the issuing provider, generate replacements, update the affected workloads, and review AI provider usage and billing logs. The update links the activity to Wiz's "Black October" research on attacks against AI credentials.
- **2026-10-31, 01:04.** Audit logs are enabled for all customers, including free accounts.
- **2026-10-31, 13:34, 22:32 and 23:31.** Secret rotation becomes available for MySQL and Redis, then MinIO, then RabbitMQ add-ons, each update repeating "Please rotate all secrets if you have not already."

What the page does not say, as of 2026-11-01: how the attacker got in, what the network policy patches closed, how many customers or which regions are affected, whether bring-your-own-cloud deployments are in scope, or whether a decryption of the variable store was confirmed rather than assumed. The "assume decrypted" wording is Northflank's own and is the strongest statement a customer can act on.

Wiz's post of 2026-10-30, "Black October for AI developer platforms" (Benjamin Read and Rami McCarthy), lists Northflank as the ninth AI developer platform with an incident in October 2026, after Fireworks AI (10-06), Andromeda (10-09), Zeabur (10-14), Lightning AI (10-15), OpenCode (10-16 to 17), Railway (10-20), Warp (10-23) and CommandCode (10-28). Across the public reports Wiz sees one pattern: "All public reports highlight targeted exploitation, explicitly hunting stored environment variables, with a focus on those granting AI access." Wiz was also the detector here, which makes its post a second account of the same event rather than outlet pickup. The Hacker News thread "Northflank Breached" (item 50305025, 2026-10-30 15:10 UTC) reached 475 points and links only the status page.

Why it is here: a vibe-coded app's whole secret set, the database URL, the Stripe key, the OpenAI or Anthropic key, the OAuth client secret, lives in the hosting platform's environment-variable store. When the operator says to assume that store was decrypted, every third-party account behind the app is exposed, and the first abuse customers reported was of AI provider keys. This is the pattern already filed for [Railway](2026-10-railway-environment-variable-store-breach-rotate-every-secret.md), [Zeabur](2026-10-zeabur-october-security-incident-env-var-store-breach-shutdown-december-31.md) and [Fireworks AI](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md), and the month's list is kept in [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md).

## Am I affected?

- Any Northflank project, team or add-on that held a secret on 2026-10-30. Treat every environment variable, secret group entry, global secret and add-on credential as read by the attacker.
- Check each AI provider's usage and billing page (OpenAI, Anthropic, Google, OpenRouter and any other key you stored) for requests you did not make from 2026-10-30 onward. Northflank's own update says this is where abuse showed up first.
- Open Northflank's audit log, available to all accounts since 2026-10-31 01:04 UTC, and review access to secrets and add-ons.
- If an add-on had public exposure enabled, assume the database itself was reachable with the leaked credential, not just the credential.

## If you are affected

1. Rotate at the issuer, not in Northflank: AI provider keys, database passwords (use the platform's new rotation for Postgres, MongoDB, MySQL, Redis, MinIO and RabbitMQ, then update consumers), OAuth client secrets, Stripe and payment keys, GitHub and registry tokens, cloud credentials, webhook signing secrets, JWT and session secrets.
2. Revoke the old values at the provider so a copy the attacker holds stops working; replacing the value in Northflank alone does not do that.
3. Invalidate user sessions for apps whose session secret lived on the platform, and review database access logs for the window.
4. Disable public exposure on add-ons unless the app needs it.
5. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and, for the app itself, [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

- Keep provider keys short-lived and scoped, and give each deployment its own key, so one platform incident is one revocation. See [credential hygiene](../prevention/credential-hygiene.md).
- Set spend limits and usage alerts on every AI provider account; the abuse here was noticed by customers reading their bills.
- Treat the hosting platform's secret store as a copy of your secrets, not the only place they are controlled, and keep the issuer-side inventory that lets you rotate in one pass.

## Sources

- [Northflank status — Security incident](https://status.northflank.com/cmvv0rn5a092f14rutwccodpp) — fetched 2026-11-01: the 11:43 to 13:05 UTC internal timeline, every public update from 2026-10-30 13:40 to 2026-10-31 23:31 with the quoted instructions, the AI-key abuse reports, the audit-log and add-on rotation announcements, the "Identified" status and the seven components in major outage.
- [Northflank status page](https://status.northflank.com) — fetched 2026-11-01: the same incident on the front page, component status (app and API operational, the rest in major outage).
- [Wiz — Black October for AI developer platforms](https://www.wiz.io/blog/black-october-for-ai-developer-platforms) — fetched 2026-11-01: dated 2026-10-30, authors Benjamin Read and Rami McCarthy; the nine-platform list with dates and the environment-variable pattern quoted above; Northflank's entry links the status page.
- [Hacker News — Northflank Breached (item 50305025)](https://hn.algolia.com/api/v1/items/50305025) — read 2026-11-01 through the Algolia items API: posted 2026-10-30 15:10 UTC, 475 points, 31 top-level comments, link target the status page.
- [Qovery — Northflank Security Incident (October 30, 2026): What Happened and How to Protect Your Secrets](https://www.qovery.com/blog/northflank-security-incident-secrets-own-cloud) — fetched 2026-11-01: a competitor's write-up (Romaric Philogene, 2026-10-30) that reproduces the status-page timeline and notes the absent root cause and the unaddressed bring-your-own-cloud question; used only for what it attributes to the status page and to Wiz.
