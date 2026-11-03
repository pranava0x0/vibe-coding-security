---
id: 2026-11-trigger-dev-security-incident-environment-variables-exposed-subset-of-organizations-rotate
title: "Trigger.dev security incident 2026-11-01: an attacker read environment variables for a subset of organizations; no root cause published"
date_disclosed: 2026-11-01
last_updated: 2026-11-03
severity: high
status: ongoing
ecosystems: [trigger-dev, background-jobs, nextjs, supabase, environment-variables, hosted-platform]
tools_affected: ["Trigger.dev cloud (cloud.trigger.dev) organizations, a subset of which were emailed on 2026-11-01", "every secret stored as a Trigger.dev environment variable: database URLs, Stripe and Supabase keys, LLM provider keys, OAuth client secrets, secrets-manager credentials", "the apps and services those variables unlock"]
tags: [vendor-incident, credential-exposure, environment-variables, background-jobs, workflow-platform, ai-agents, rotate-credentials, no-root-cause, status-page, hacker-news]
---

## TL;DR
Trigger.dev, the TypeScript background-jobs and AI-workflow platform, said on 2026-11-01 that "the attacker gained unauthorized access to environment variables" for "a subset of organizations", that it "blocked the exploit used in this attack", and that it emailed every impacted account owner mitigation steps. It has not said how the attacker got in, how many organizations were affected, or when the access began. If your organization was emailed, rotate every secret that was ever a Trigger.dev environment variable from a clean machine and treat the services behind them as reachable by the attacker until you have checked their logs. If you were not emailed, you are outside the subset the vendor identified, but the vendor's investigation is not finished and the status page marked the incident "Resolved" the same evening it was opened.

## What happened

**The vendor's disclosure.** Trigger.dev CTO Eric Allam published "Security Disclosure: Sunday November 1st" on the vendor blog and the same text as status-page incident 1110434 (component: API), which reads in full: "There has been a security incident at Trigger.dev. We've blocked the exploit used in this attack but our investigation has identified exposure across a subset of organizations. The attacker gained unauthorized access to environment variables for these organizations. We have emailed all impacted account owners with steps to mitigate. We will follow up with more details." The status page shows the incident as Resolved at 22:50 UTC on 2026-11-01. The post gives no timeline, no detection time, no count and no root cause. The Register (2026-11-02, Brandon Vigliarolo) asked and a spokesperson "declined to provide more information", saying a full incident report would follow. The Register also names the webhooks Trigger.dev recently added for Stripe, Supabase and Slack as the reason environment variables on this platform are worth stealing; that is the reporter's reasoning, and the vendor has not said which integrations were involved.

**What the audience stores there.** Trigger.dev is where AI-generated Next.js and Supabase apps put queues, cron and long-running LLM calls, and a task's environment variables are the app's real secrets: database URLs, provider keys, Stripe keys, OAuth secrets. The platform's own July 2026 advisories ([the self-hosted coordinator file](2026-07-trigger-dev-self-hosted-coordinator-default-secret-env-exfiltration.md)) describe what an attacker gets from a run's environment: "decrypted environment variables from any run". Trigger.dev's own API keys and personal access tokens, and any secrets-manager credentials stored as variables, belong on the rotation list too; the vendor has not published one.

**What is not known.** Whether the exposure is limited to cloud.trigger.dev or involved self-hosted operators (the post does not say; self-hosters hold their own variables, and the status page files the incident under the API component). Whether the attacker used a vulnerability in the platform, a stolen credential, or a third party. Whether variables were read in bulk or per organization. When access began. Hacker News commenters (item 50331784, 166 points) asked the same questions; one compared the Linux kernel TCP CVE and Northflank's incident as candidates, and nothing in the thread answers them. Two commenters objected to the "Resolved" state on a disclosure with no root cause.

**The pattern.** By disclosure date this is the seventh hosted developer platform since 2026-10-09 to report theft of stored customer secrets, after Fireworks AI (2026-10-09), Lightning AI (2026-10-15), OpenCode Console (2026-10-17), Zeabur (2026-10-19), Railway (2026-10-21) and Northflank (2026-10-30), each tracked here; Wiz's "Black October" roundup counts nine platforms breached in October by a wider definition. A platform that stores customer secrets decrypted for its runtime is a single breach away from every service those secrets unlock. An October 6 Trigger.dev incident (1083239, "Some sensitive environment variables synced from Vercel were cleared") was an availability bug, not a breach, and is recorded here only so the two are not confused.

## Am I affected?

1. **Check the account owner's inbox for the 2026-11-01 notification.** The vendor emailed "all impacted account owners". If an organization has several owners or a shared owner mailbox, check every one.
2. **List every environment variable in every Trigger.dev environment** (dev, staging, prod) from the dashboard, under the project's Environment Variables page. The names are the inventory; the values are the secrets to rotate.
3. **Inventory what each variable unlocks.** A `DATABASE_URL` is the database; a `STRIPE_SECRET_KEY` is the payment account; an `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` is a bill; a `SUPABASE_SERVICE_ROLE_KEY` bypasses row-level security on every table.
4. **Check the logs of those services for use you did not make** since at least 2026-10-25 (the vendor has given no start date, so widen the window): provider usage dashboards, Stripe event logs, database connection logs, cloud audit logs.

## If you are affected

- Rotate every secret that was a Trigger.dev environment variable, from a clean machine, starting with database credentials and provider keys. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for cloud keys and [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) for Git tokens stored as variables.
- Rotate Trigger.dev's own credentials too: project API keys (`TRIGGER_SECRET_KEY`) and personal access tokens, since an attacker who read the variables may have read those.
- Where a variable was a provider key, check the provider's usage for the LLMjacking pattern ([the GTIG file](2026-11-llmjacking-stolen-cloud-and-llm-api-keys-billed-for-inference-gtig-jet-night-unc6993.md)): high-volume inference billed to your account within hours.
- If the app behind the variables holds user data, treat it as a [compromised web app](../playbooks/if-your-webapp-was-compromised.md) until the service logs say otherwise.

## Prevention

- Give background-job platforms scoped, short-lived credentials: a database role limited to the job's tables, a restricted Stripe key, a provider key with a spend cap. See [credential hygiene](../prevention/credential-hygiene.md).
- Prefer a secrets manager the job fetches from at run time over variables stored decrypted in the platform, so a platform breach yields a reference and not the secret.
- Keep an inventory of which third-party platforms hold which secrets. This is the seventh such disclosure since 2026-10-09 and the rotation has to start within hours.

## Sources
- [Trigger.dev — Security Disclosure: Sunday November 1st](https://trigger.dev/blog/security-incident-nov-2026) — fetched 2026-11-03: 2026-11-01, Eric Allam (CTO); the full disclosure text, "a subset of organizations", "blocked the exploit", email to impacted owners, no root cause, no count, no timeline.
- [Trigger.dev status — incident 1110434](https://status.trigger.dev/incident/1110434) — fetched 2026-11-03: same text, component API, Resolved 2026-11-01 22:50 UTC, one update only.
- [Trigger.dev status page](https://status.trigger.dev/) — fetched 2026-11-03: the incident list, including 1083239 (2026-10-06, Vercel-synced sensitive variables cleared, availability only).
- [The Register — Thieves pilfer environment variables from Trigger AI workflow tool](https://www.theregister.com/security/2026/11/02/thieves-pilfer-environment-variables-from-trigger-ai-workflow-tool/5306998) — fetched 2026-11-03: 2026-11-02 16:44 UTC, Brandon Vigliarolo; the spokesperson's "wait for a full incident report", the Stripe, Supabase and Slack webhooks, customers named from the vendor's site without any claim they were affected.
- Hacker News item 50331784 ("Trigger.dev customer environment variables exposed", 166 points, about 86 comments), read through the Algolia items API 2026-11-03: the "Resolved" objections, the root-cause speculation, no commenter claiming to be affected or staff.
- [triggerdotdev/trigger.dev — security advisories](https://github.com/triggerdotdev/trigger.dev/security/advisories) — fetched 2026-11-03: newest advisory 2026-10-20 (GHSA-65rr-73jq-6qhf); no advisory for this incident.
