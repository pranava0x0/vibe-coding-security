---
id: 2026-10-railway-environment-variable-store-breach-rotate-every-secret
title: "Railway: intruder may have read customers' encrypted environment variables and decrypted some (2026-10-21); rotate every variable, API key and registry credential"
date_disclosed: 2026-10-21
last_updated: 2026-10-22
severity: high
status: active
ecosystems: [paas, railway, deployment-platforms, ai-inference, crypto]
tools_affected: ["every Railway project: environment variables, sealed variables (scope unconfirmed), Railway API tokens (all invalidated), bucket credentials (all rotated by Railway)", "upstream providers whose keys were stored as Railway variables: OpenAI, Anthropic, Google, AWS, GCP, GitHub, databases, private registries", "wallets whose private keys were stored as Railway variables (researcher claim via The Hacker News)"]
tags: [breach, platform, environment-variables, secrets-exposure, credential-rotation, railway, llmjacking, ai-inference-keys, deployment-pause, vendor-disclosure, crypto-drain]
---

## TL;DR
Railway, the platform-as-a-service that a large share of generated backends deploy to, disclosed on 2026-10-21 that it detected "anomalous activity involving systems that store customer environment variables" and that an unauthorized third party "may have accessed encrypted environment variables and, in some cases, obtained the decrypted contents." Railway paused all deployments, notified upstream providers so they could revoke keys proactively, rotated every bucket credential, invalidated every Railway API token, and told all customers to roll every environment variable, every API key and every private-registry credential now and to review service logs. It says the impact is likely limited to a subset of users, who will be emailed, and that the intrusion is "part of a series of attacks recently targeting platform companies" whose aim is to compromise AI inference providers. The Hacker News reports researcher Taylor Monahan's claim that wallet private keys held as Railway variables were drained from 19:36 on the day of disclosure, at least two hours before Railway's post; Railway has not confirmed that. Builds returned for Enterprise at 03:32 UTC on 10-22 and Pro at 06:29, with Hobby, Free and Trial still paused at 14:50 UTC. If your app runs on Railway, treat every secret it held as exposed.

## What happened

**Railway's account.** The disclosure (Jacob Cooper, 2026-10-21) says the activity was detected "earlier this morning," gives no times, and limits the known scope to the environment-variable systems. Environment variables "may contain secrets such as API keys, database credentials, and registry credentials." Railway's actions: upstream providers notified for proactive revocation, deployments paused, affected customers to be contacted by email, status page for the build timeline. Two follow-up guides dated 2026-10-22 cover checking for anomalous GCP and AWS access. GitGuardian (2026-10-22) notes the disclosure does not say whether sealed variables, which cannot be read back through the UI, API or CLI, were in scope, and recommends rotating them too.

**The status page.** The incident opened at 07:24 UTC on 10-21 as an investigation; by 09:28 the dashboard, API and CLI were down and builds paused in all regions. The security notice went up at 21:59 UTC. Bucket credential rotation began at 22:10 and surfaced in customers' audit logs as revocations by a Railway employee (22:45). At 01:22 on 10-22 Railway published guides for checking unexpected usage, rotating database credentials, redeploying buckets, reconnecting GitHub and checking anomalous access. Enterprise builds returned at 03:32, all Railway API tokens were invalidated at 04:17 (new tokens required), Pro builds at 06:29; through the morning deployments queued and failed at elevated rates, and at 14:50 UTC Pro and Enterprise were running "a little slower than usual" with Hobby, Free and Trial still to come.

**The wallet claim.** The Hacker News (2026-10-22) attributes to Taylor Monahan a first known theft transaction at 7:36 p.m., "at least two hours before the official disclosure," and the draining of wallets whose private keys were stored on Railway; the post is on X and did not open this sweep, so the claim is carried as the outlet's report of the researcher's statement. An extended search returned secondary sites citing Monahan for a figure of about $371,000 across 19 chains; none is a primary, and Railway's disclosure does not mention transfers, so no figure is stated here as fact.

**The campaign framing.** Railway's "series of attacks targeting platform companies" to reach "AI inference providers" matches the shape of the OpenCode Console breach five days earlier, where a gateway's stored provider keys were the target, and The Hacker News places both under LLMjacking, citing Wiz's 2026-10-20 post on cloud-billing theft for LLM usage. Railway did not name the other platforms.

Why it is here: Railway is where a generated Next.js, FastAPI or Express app and its Postgres go when the builder does not want to run servers, and the environment-variable panel is where the OpenAI, Anthropic, Supabase, Stripe and database secrets live. A read of that store is a read of every third party the app talks to.

## Am I affected?

- Any project on Railway on or before 2026-10-21. Railway says "a subset of users" and will email confirmed accounts; its guidance is for everyone to rotate regardless.
- Dump what was there: `railway variables` per service and environment (GitGuardian's suggestion is to scan the dump with a secret scanner to prioritise, then delete the dump).
- Check the providers, not only Railway: OpenAI, Anthropic and Google usage dashboards for unexpected spend; AWS CloudTrail and GCP audit logs per Railway's two guides; GitHub for app and token activity; database logs for new connections.
- Railway API tokens: all are dead; any automation using one has stopped.

## If you are affected

1. Rotate at the provider first, then update the value in Railway, so the old secret is dead before the new one is stored. Order: cloud and database credentials, AI provider keys (check spend caps), payment and email keys, registry credentials, GitHub app connections.
2. Redeploy each service after rotation; on 10-22 this needs builds to be enabled for your tier.
3. Treat sealed variables as exposed until Railway says otherwise.
4. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and, for any key that shows use you did not make, [if your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md).
5. Wallet keys in environment variables are a different problem: move funds from any address whose key was stored on Railway.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): provider keys with spend caps, scoped to one project; no wallet keys in a hosting panel; short-lived cloud credentials over long-lived ones.
- [CI/CD hardening](../prevention/ci-cd-hardening.md): one platform's secret store is one breach from every secret; prefer workload identity to stored keys where the provider offers it.

## Sources
- [Railway — Security Disclosure: Wednesday October 21st](https://blog.railway.com/p/security-disclosure-wednesday-october-21st) — fetched 2026-10-22 (2026-10-21, Jacob Cooper): the quoted statements, the actions taken, the customer instructions, the campaign framing, the two 10-22 follow-up guides listed.
- [Railway status — incident QH8L8B3E](https://status.railway.com/incident/QH8L8B3E) — fetched 2026-10-22: the 45 updates from 07:24 UTC on 10-21 to 14:50 UTC on 10-22 summarised above.
- [The Hacker News — Railway Says Intruder May Have Accessed Customer Secrets, Urges Credential Rotation](https://thehackernews.com/2026/10/railway-says-intruder-may-have-accessed.html) — fetched 2026-10-22 (2026-10-22): the Monahan claim and its timing, the bucket and token rotation, the LLMjacking framing with the Wiz and Symantec citations.
- [GitGuardian — Railway October 2026 Incident: Treat Every Environment Variable as Exposed](https://blog.gitguardian.com/railway-october-2026-incident-environment-variables/) — fetched 2026-10-22 (2026-10-22): the sealed-variables gap, the rotate-upstream-first order, the dump-and-scan procedure, the April Vercel comparison.
- Related in this corpus: [OpenCode Console breach](2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack.md) for the same week's provider-key theft at a hosted gateway, [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md).
