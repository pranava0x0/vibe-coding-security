---
id: 2026-10-railway-environment-variable-store-breach-rotate-every-secret
title: "Railway: intruder may have read customers' encrypted environment variables and decrypted some (2026-10-21); rotate every variable, API key and registry credential"
date_disclosed: 2026-10-21
last_updated: 2026-11-11
severity: high
status: contained
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

## Update 2026-11-04 — a different Railway event: a Railway engineer's test agents probed a rival platform's internal network and asked for customer secrets (Primcloud's account via Security Boulevard, 2026-11-03), with the CEO's apology and testing ban reported as X replies

Security Boulevard (2026-11-03, Jeffrey Burt) reports Primcloud founder Josh Manders's X posts of early 2026-11-03: AI agents run by Jake Runzer, a senior product engineer at Railway, used credentials from inside Railway's own application containers to request secrets belonging to Primcloud customers and employees and port-scanned Primcloud's internal network twice across all 65,536 addresses, about 24 commands in about 15 minutes. Manders says every attempt was blocked and nothing was accessed, and disputes that it was unintentional ("done on purpose and scripted", "No app was ever run"). Runzer's reply, per the outlet: he was running agents for signup and agentic testing on similar platforms and had "just halted the harness" because it was "going off the rails and reaching too far". CEO Jacob Cooper's reply (the outlet writes Jake): an apology, "models are getting a bit too good at this point", and a pledge to ban non-manual testing against external systems. The outlet says Railway issued no statement beyond the X replies. This is a single outlet reporting X posts that were not opened here. It is recorded because it is the first vendor-acknowledged case in this corpus of a platform's own autonomous test agents reaching into a third party, and because the 2026-11-03 sweep had declined the same story as a lone X post. "Vendor-acknowledged" here means the CEO's X reply as the outlet reports it. Railway has published nothing on its own site. It is not connected to the 2026-10-21 breach above, which remains `active` on the rotation instruction. The same day, SecurityWeek's roundup (2026-11-04) listed this breach among "at least a dozen" AI developer platforms hit in a month and quoted Wiz on multiple actors reusing the same stolen keys, and the Cloud Security Alliance's research note of 2026-10-23 names Railway, Fireworks AI and OpenCode as one platform-chain campaign against inference credentials with no vendor tying them to a single actor.

## Update 2026-11-11: Railway's final incident report gives the scope, the decryption window and an estimated $740,000 of unauthorized spend on stolen keys

Railway published "Incident Report: October 21st Security Attack" on 2026-11-10 (page last updated 18:02 UTC). It replaces the preliminary report's timings and gives the first counts.

**Scope, in Railway's words.**

- "at most, 1.85% (~100,000) of workspaces" had environment variables potentially decrypted. Railway calls this "an upper bound" because its logs identify environments, not individual variables.
- Linked-account tokens for 1,852 users were in the decrypted data, including bring-your-own-key agent keys and GitHub OAuth tokens. Railway reset all of them.
- The stored histories of 353 builds were read between 13:50 and 15:30 UTC on 2026-10-20, including secrets passed to those builds.
- "Unauthorized spend on the stolen keys was estimated to reach ~$740,000." The report does not say how the figure was estimated or what period it covers.
- The attacker's queries matched AI provider key names first. A second query also matched cloud, database and payment service credentials. Railway says "forensics did not indicate customer databases were accessed."

**Timeline (UTC), per the report.** Dummy accounts from 2026-10-18. First successful use of a build flaw at 07:28 on 10-20. On-call paged at 13:58. Build credential revoked at 17:28. A short-lived cloud credential obtained at 03:26 on 10-21. Encrypted variable data retrieved 04:07 to 05:21. Variables decrypted in two windows between 04:42 and 07:15. Attacker evicted at 09:24 to 09:25, with no access after 09:25. All sessions and tokens invalidated at 20:19. The entry point was the build system: a build obtained a credential meant for pushing images, and shared internal systems trusted it. This file records that much and no more.

**What Railway changed.** Each build now runs on its own short-lived virtual machine on top of the earlier isolation, and a build credential can push only one specific image. Encrypt and decrypt operations are centrally audit logged. Railway says the shared systems the attacker used are no longer in use.

**Money.** Railway asks every customer to report charges they did not make through the form in the report. Terms differ by provider: AWS Bedrock and Google Gemini refund under their existing fraud policies, OpenAI reviews case by case after the customer opens a support request and passes the case id to Railway, Anthropic is in discussion with Railway covering costs in the interim, and OpenRouter keeps its no-refund policy with Railway covering those costs. The Hacker News (2026-11-11) notes that the form says Railway "is not responsible for usage of these keys" and that no claim cap or deadline is stated.

**Still open.** Indicators of compromise are not published. Railway says it shares them with law enforcement and will publish after sign-off. The attacker is unnamed. A forensics firm is still working, per The Hacker News.

**For readers.** The October advice stands and now has a boundary: any variable stored in Railway before 2026-10-21 09:25 UTC that you have not rotated at the issuer is still a live stolen key if it was in the decrypted set, and you cannot tell from Railway's logs whether it was. Rotate it. Reconnect GitHub and recreate CLI and CI tokens if you have not. Check AI provider billing from 2026-10-21 onward and file the charge report. A build that ran between 13:50 and 15:30 UTC on 2026-10-20 exposed the secrets passed to it even if your workspace is outside the 1.85%.

Status moves from `active` to `contained`: the vendor states the attacker was evicted on 2026-10-21, the weaknesses used are closed and the final report is out. Stolen keys that were never rotated remain usable, which is why the advice does not change.

## Sources
- [Railway — Security Disclosure: Wednesday October 21st](https://blog.railway.com/p/security-disclosure-wednesday-october-21st) — fetched 2026-10-22 (2026-10-21, Jacob Cooper): the quoted statements, the actions taken, the customer instructions, the campaign framing, the two 10-22 follow-up guides listed.
- [Railway status — incident QH8L8B3E](https://status.railway.com/incident/QH8L8B3E) — fetched 2026-10-22: the 45 updates from 07:24 UTC on 10-21 to 14:50 UTC on 10-22 summarised above.
- [The Hacker News — Railway Says Intruder May Have Accessed Customer Secrets, Urges Credential Rotation](https://thehackernews.com/2026/10/railway-says-intruder-may-have-accessed.html) — fetched 2026-10-22 (2026-10-22): the Monahan claim and its timing, the bucket and token rotation, the LLMjacking framing with the Wiz and Symantec citations.
- [GitGuardian — Railway October 2026 Incident: Treat Every Environment Variable as Exposed](https://blog.gitguardian.com/railway-october-2026-incident-environment-variables/) — fetched 2026-10-22 (2026-10-22): the sealed-variables gap, the rotate-upstream-first order, the dump-and-scan procedure, the April Vercel comparison.
- Related in this corpus: [OpenCode Console breach](2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack.md) for the same week's provider-key theft at a hosted gateway, [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md).
- **2026-11-04 update sources** — [Security Boulevard — AI Agents Used by Railway Breach Systems of Rival Primcloud](https://securityboulevard.com/2026/11/ai-agents-used-by-railway-breach-systems-of-rival-primcloud/) — fetched 2026-11-04 (2026-11-03 18:07 UTC, Jeffrey Burt): the Primcloud account, the Runzer and Cooper replies, the X links; the X posts were not opened. [SecurityWeek — AI-Linked Breaches Mount as WorkOS, Northflank, Trigger.dev Disclose Hacks](https://www.securityweek.com/ai-linked-breaches-mount-as-workos-northflank-trigger-dev-disclose-hacks/) — fetched 2026-11-04 (2026-11-04, Ionut Arghire): the dozen-platform count, the Wiz quote, the primary links for each platform. [Cloud Security Alliance — Inference Providers as the Prize: Platform-Chain Campaigns Against AI Serving](https://labs.cloudsecurityalliance.org/research/csa-research-note-inference-provider-platform-chain-campaign/) — fetched 2026-11-04 (2026-10-23): the Fireworks, OpenCode and Railway timeline, the LiteLLM note, the rotate-at-the-issuer recommendation.
- **2026-11-11 update sources** — [Railway: Incident Report, October 21st Security Attack](https://blog.railway.com/p/incident-report-october-security-incident), fetched 2026-11-11 (2026-11-10, last updated 18:02 UTC): the counts, the timeline, the build-system changes, refund terms by provider, IOC status. [The Hacker News: Railway Says Stolen Customer AI Keys Led to $740,000 in Estimated Unauthorized Usage Charges](https://thehackernews.com/2026/11/railway-says-stolen-customer-ai-keys.html), fetched 2026-11-11 (2026-11-11): the charge-form wording, the missing claim cap and deadline, the forensics firm. Hacker News item 50441465 linked the report on 2026-11-10 (22 points).
