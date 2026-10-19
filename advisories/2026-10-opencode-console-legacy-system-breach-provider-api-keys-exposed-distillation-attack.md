---
id: 2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack
title: "OpenCode Console: intruder reached a legacy system and may have taken users' OpenAI, Anthropic and Google provider keys; 1.4% of Console users, charges reported"
date_disclosed: 2026-10-17
last_updated: 2026-10-19
severity: high
status: active
ecosystems: [opencode, ai-coding-agents, hosted-gateway, ai-provider-keys, anthropic, openai, google]
tools_affected: ["OpenCode Console workspaces with an OpenAI, Anthropic or Google provider key saved before 2026-10-17", "every application, script and CI job that shares a provider key with such a workspace"]
tags: [data-breach, api-key-exposure, hosted-gateway, bearer-credential, anthropic-key, openai-key, google-key, opencode, distillation, vendor-incident, active]
---

## TL;DR
OpenCode, the open-source coding agent built by Anomaly, says an intruder reached "a legacy system that we were in the process of decommissioning" on the night of 2026-10-16 and that third-party provider API keys saved in OpenCode Console workspaces "may have been exposed." Console is the optional hosted gateway that stores a workspace's OpenAI, Anthropic or Google key so members can use the models without seeing it. OpenCode puts the affected share at 1.4% of Console users, all of whom had an outside provider linked, says everyone affected was emailed on 2026-10-17 and that anyone without the email is not affected, calls the incident ongoing, and ties it to "a large scale distillation attack" without saying how. Keys added to the OpenCode CLI or desktop app are stored locally and are not part of this incident, per co-founder Dax Raad. Several users reported unauthorized OpenAI, Anthropic and Google usage charges, from about $170 to about $1,700, beginning before the vendor's notice. A provider key is a bearer credential: deleting it from Console does not revoke it, and a Console budget cannot cap usage made outside Console's gateway. If a Console workspace held a provider key, revoke it at the provider, replace it everywhere it was reused, and read the provider's usage log back to 2026-10-16.

## What happened

**The product.** OpenCode is an open-source coding agent that runs in a terminal, editor or desktop app and connects to more than 75 model providers; its repository has about 215,000 GitHub stars and the company claims 16 million monthly developers (figures as reported by The Latent and Dealroom, both 2026-10-17 to 10-18). Console is an optional hosted service. Per OpenCode's own documentation, Console "stores the provider credential and serves each provider through its gateway," so workspace members use the models without seeing the key; owners and admins manage keys from the Providers tab. That design puts the provider key on OpenCode's servers, which is what was reached.

**The vendor's account, in its own words as quoted by outlets.** OpenCode's post on X (2026-10-17, quoted by The Latent, The Hacker News, Dealroom and Notebookcheck): "We had a security breach last night related to a large scale distillation attack" affecting 1.4% of Console users; the incident is "ongoing so we cannot share more details at this point"; the company is "working with Anthropic, OpenAI, and Google to remediate." The email to affected users, subject "Action Required: Potential provider key breach" (quoted by The Latent and Dealroom): someone gained "unauthorized access to a legacy system that we were in the process of decommissioning," and keys "saved in your workspace may have been exposed"; users were told to revoke and replace the keys and watch for unexpected usage. Raad on X, 10-17 and 10-18 (per The Hacker News): the breach involves "the OpenCode Console, not OpenCode itself"; keys in the CLI and desktop apps sit in a local database and "never come to us"; attackers had been "non stop trying to attack our systems for the past 48 hours," and "a side effect is everything is getting hardened." The X posts could not be opened this sweep; every quotation above is as the named outlet printed it.

**What the vendor has not said, as of 2026-10-19.** How the legacy system was reached, what it was, how many users 1.4% is, how long the access lasted, whether any key was copied or used, and how the key exposure connects to a distillation campaign (a distillation attack harvests a model's outputs at scale to train another model, and the obvious link is that stolen provider keys fund the harvesting on victims' accounts, but OpenCode has not drawn that line). No status page, blog post or GitHub security advisory carries the incident; the repository's security tab lists three unrelated advisories (two from January, one from September, both tracked here). Dealroom reports that Anthropic revoked affected Claude API keys; that statement is Dealroom's, not a provider page.

**What users reported.** The Latent collected four accounts from X on 2026-10-17: Colin Parsons said $281 was charged to his OpenAI key and $168 to his Anthropic key starting around 2 a.m. ET, and posted before OpenCode's statement; Preston Zeller reported about $1,700; Francisco Giancarelli reported more than $700 of OpenAI usage before disabling the key; Alejandro García Iglesias reported stolen OpenAI and Anthropic credits and a suspended OpenAI account. Notebookcheck relayed two Reddit reports: about $400 of unauthorized Anthropic usage, and about €200 of Google usage with the project suspended for abuse. Several developers said they received provider usage alerts before OpenCode's email. These are the users' own claims; OpenCode has not confirmed any key was used.

**Side effects on the OpenCode repository.** Issues opened 2026-10-17 and 10-18 report Console workspaces "restricted since Oct 17" without a breach email (#56703), OpenCode-issued keys revoked with no expiry and no compensation policy (#56833), keys disappearing from accounts and then reporting as expired (#56556), and social sign-in failing. None of these is a vendor statement, but together they show Console revoking or restricting credentials around the disclosure.

**Why this is a vibe-coding incident.** A hosted gateway that holds the team's provider keys is the shape every "add your API key once" product takes, from Console to the LLM routers and agent platforms in this corpus. The key is a bearer token with a billing account behind it, the gateway's own budget controls do not apply to requests the thief makes directly to the provider, and the user learns of the theft from a usage alert. The same tier of product was the attack surface in the [Fireworks AI job-runner incident](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md) and the reason the [infostealer families](2026-09-infostealers-target-coding-agent-tokens-mcp-configs-prompt-histories.md) now carry a coding-agent module.

**Two-source note.** The vendor's statement and email are the primary and were quoted consistently by four outlets (The Latent, Dealroom, Notebookcheck, The Hacker News) and StepSecurity; the loss reports come from named users and are independent of the vendor; the repository issues are the victim-side record. The vendor's X posts were not opened directly, so this file cites the outlets that quote them.

## Am I affected?

You are in scope if a Console workspace you own or belong to had an OpenAI, Anthropic or Google provider key saved before 2026-10-17. OpenCode says the affected set is the 1.4% of Console users who were emailed; treat the email's absence as the vendor's statement, not as proof, if the workspace held a key.

```bash
# Did this machine use OpenCode, and which providers were linked locally?
which opencode; ls -la ~/.opencode/bin/opencode 2>/dev/null
ls ~/.config/opencode 2>/dev/null
cat ~/.local/share/opencode/auth.json 2>/dev/null | python3 -c 'import json,sys; print(list(json.load(sys.stdin).keys()))'
```

Per the vendor, the local `auth.json` keys never leave the machine, so a provider listed there is not itself evidence of exposure; StepSecurity treats it as the inventory of providers whose keys the developer may also have pasted into Console. The authoritative check is the Console Providers tab for each workspace, and the provider's own usage dashboard from 2026-10-16 onward.

- Unexpected usage, a usage-limit alert, a suspended project or a "free tier" or quota error on a provider account that a Console workspace shared a key with is the signal users reported.
- Deleting a key in Console is not revocation; only the provider dashboard revokes it.

## If you are affected

1. Revoke the key at the provider (OpenAI, Anthropic or Google Cloud console) and create a new one. Do it from the provider, not from Console.
2. Update every application, script and CI secret that used the old key; a key pasted into Console was usually pasted elsewhere too.
3. Read the provider's usage and billing logs back to at least 2026-10-16 for requests you did not make, and dispute charges with the provider.
4. Set spend limits or alerts on every provider account, and use one key per tool so a gateway's breach costs you one key.
5. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for any other secret the same workspace stored.

## Prevention

- Treat a hosted gateway's key store as a shared secret with the gateway's blast radius; prefer a key scoped to the gateway, with its own spend limit, over a reused team key. See [credential hygiene](../prevention/credential-hygiene.md).
- Keep provider keys in the local agent when a single developer is the only user; the hosted layer adds a server-side copy of the key for every workspace member's convenience.
- Watch the provider's usage alerts, not the gateway's budget page: the gateway's budget only sees requests that pass through it.

## Sources
- [The Hacker News, OpenCode Console Breach May Have Exposed OpenAI, Anthropic, and Google API Keys](https://thehackernews.com/2026/10/opencode-console-breach-may-have.html) — 2026-10-19; the Console design, the 10-16 night timing, the 1.4% figure, Raad's "not OpenCode itself" and "never come to us" quotations, the 48-hour statement, the Reddit and Dealroom loss reports, the revoke-replace-review guidance, "deleting a key from Console does not revoke it."
- [The Latent, OpenCode says breach tied to distillation attack exposed users' AI provider keys](https://thelatent.co/models/opencode-says-breach-tied-to-distillation-attack-exposed-users-ai-provider-keys) — 2026-10-17 21:07 UTC; the X statement and the affected-user email quoted verbatim, the four named user reports with amounts and times, the open questions, the 215,000-star and 16-million figures.
- [Dealroom, OpenCode breach drains users' AI keys as platforms holding customer credentials ...](https://dealroom.co/news/163473-opencode-breach-drains-users-ai-keys-as-platforms-holding-customer-crede/) — 2026-10-18; the "legacy system ... decommissioning" email sentence, Anomaly (formerly SST) as the builder, the Parsons, Zeller and Giancarelli amounts, the statement that Anthropic revoked affected Claude keys, the 48-hour statement.
- [Notebookcheck, OpenCode hacked, users urged to revoke their API keys](https://www.notebookcheck.net/OpenCode-hacked-users-urged-to-revoke-their-API-keys.1426957.0.html) — 2026-10-17, updated 10-18; the Reddit loss reports (about $400 Anthropic, about €200 Google with a suspended project), expired OpenCode keys and social-login failures.
- [StepSecurity, OpenCode Security Breach: Distillation Attack Hit Console Users With Linked AI Providers](https://www.stepsecurity.io/blog/opencode-security-breach) — 2026-10-18; the local file paths (`~/.opencode/bin/opencode`, `~/.config/opencode`, `~/.local/share/opencode/auth.json`) and the rotate-then-review steps; StepSecurity dates the disclosure 10-18, a day later than The Latent's time-stamped report of the same statement.
- [OpenCode docs, Console providers](https://opencode.ai/v2/docs/console/providers) — read 2026-10-19; Console "stores the provider credential and serves each provider through its gateway"; no incident notice on the page.
- [anomalyco/opencode issues, "breach" and "api key" since 2026-10-17](https://github.com/anomalyco/opencode/issues?q=breach+OR+%22api+key%22+console+sort%3Acreated-desc) — read 2026-10-19; #56703 (workspaces restricted since 10-17, no email), #56833 (key revoked, no compensation policy), #56556 (keys disappear), #56782 and #56586 (expired-key errors with no recovery path).
- [anomalyco/opencode, security advisories tab](https://github.com/anomalyco/opencode/security/advisories) — read 2026-10-19; three advisories, none about this incident.
- OpenCode's and Dax Raad's X posts of 2026-10-17 and 10-18 are the primary statements; they could not be opened this sweep and are cited above through the outlets that quote them.
- Related in this corpus: [OpenCode localhost RCE, January 2026](2026-01-opencode-localhost-rce.md), [OpenCode cross-site upgrade install, September 2026](2026-09-opencode-global-upgrade-cross-site-npm-install-rce.md), [Fireworks AI internal-credential incident](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md).
