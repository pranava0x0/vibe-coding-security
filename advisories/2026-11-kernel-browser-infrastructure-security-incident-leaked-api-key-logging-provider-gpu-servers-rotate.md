---
id: 2026-11-kernel-browser-infrastructure-security-incident-leaked-api-key-logging-provider-gpu-servers-rotate
title: "Kernel browser-infrastructure incident (notice 2026-11-04): leaked API key, logging-provider download, four GPU servers; 0.28% of customers told to rotate"
date_disclosed: 2026-11-04
last_updated: 2026-11-05
severity: medium
status: contained
ecosystems: [kernel, browser-infrastructure, web-agents, mcp, saas, api-keys]
tools_affected: ["Kernel (kernel.sh) customers: Kernel API keys and the third-party secrets of app deployments that appeared in the logging provider's data", "browser sessions on the three affected GPU servers between 2026-11-03 05:41 and 07:46 UTC", "agents using Kernel through its SDKs, CLI or hosted MCP server with a key issued before 2026-11-03"]
tags: [vendor-incident, credential-exposure, api-keys, browser-agents, logging-provider, cryptominer, artex, ai-developer-platform-wave, rotate-credentials, hacker-news]
---

## TL;DR
Kernel, which sells cloud Chromium sessions for web agents with SDKs, a CLI and a hosted MCP server, says that from 2026-10-24 an attacker used a compromised Kernel API key to probe internal data, on 2026-10-27 used it to reach a staff login at Kernel's logging provider and download data containing "a small number of kernel API keys and app deployments' third-party secrets", and on 2026-11-03 used a compromised hosting-provider credential to reach four GPU servers, three of which ran customer browser sessions, and start cryptominers. Kernel says the breach "impacted 0.28% of Kernel's customers", that it revoked and rotated the credentials involved, took the servers offline, notified affected organizations, and believes the actor used the ARTEX framework as a command center. If you hold a Kernel key issued before 2026-11-03 or stored third-party secrets in a Kernel app deployment, rotate them.

## What happened

**The vendor's account.** Kernel's public notice (2026-11-04) gives a UTC timeline. 2026-10-24 21:18: the attacker uses a leaked API key to read data across internal profiles. 2026-10-27 18:01: the attacker verifies access to the logging provider. 2026-11-02 19:28: a customer escalation arrives; 22:20 incident declared at high severity; 22:30 the compromised API key is found and revoked; 23:50 severity raised to critical. 2026-11-03 05:41: a development server is accessed and a cryptominer started; 06:09 to 07:17: servers 2, 3 and 4 accessed and a cryptominer start attempted; 07:11 second incident declared, critical; 07:37 hosting-provider API keys rotated; 07:46 servers 2 to 4 taken offline; 09:00 the second incident is confirmed as the same actor; 09:29 the development server taken offline; 11:12 and 11:27 root cause analysis completed and the development server cloned for forensics; 14:00 to 22:50 containment and customer communications. The notice says the fourth server was a development server holding no customer data, that the logging-provider data contained a small number of Kernel API keys and app deployments' third-party secrets, and that the actor appears financially motivated and part of a larger cryptomining campaign. It does not say how the first API key leaked or how the hosting-provider credential was obtained, and the root cause analysis it says was completed is not published.

**What Kernel is.** Its site describes "browser infrastructure for web agents and automations": cloud Chromium sessions controlled through an API, TypeScript, Python and Go SDKs and a CLI, persistent profiles, proxies, a captcha solver, live view and replays, vaults and payments, and a hosted MCP server over streamable HTTP. An agent that browses the web through Kernel authenticates with a Kernel API key; an app deployed to Kernel carries whatever third-party secrets the developer gave it. Those are the two credential categories the notice names.

**The wave it joins.** This is the tenth hosted AI developer platform since 2026-10-09 to report theft of stored customer credentials, after Fireworks AI, Andromeda, Zeabur, Lightning AI, OpenCode Console, Railway, Northflank, Trigger.dev and GitBook, each tracked here, and the fourth vendor in a week (WorkOS, Chainstack, GitBook, Kernel) to name ARTEX or AI agents in its account. Kernel's "0.28% of customers" is the only count any of them has published. SecurityWeek's 2026-11-04 roundup, written before Kernel's notice, counts "at least a dozen" platforms and quotes Wiz on two cases that "shared an identical first unauthorized activity" within 30 minutes of credential access. Kernel is not in that article.

**How it reached the public.** Hacker News item 50371427 ("Kernel.sh Hacked", 13 points, 2026-11-04 20:58 UTC) links the notice; commenters asked how the API key leaked, which the notice does not answer. No outlet had covered it on 2026-11-05.

## Am I affected?

1. **Did Kernel notify you?** The notice says affected organizations were notified and given remediation guidance on 2026-11-03. Check the account owner's inbox for a message from Kernel dated 2026-11-03 or 2026-11-04.
2. **Keys and secrets.** List Kernel API keys issued before 2026-11-03 in your Kernel dashboard and the third-party secrets configured on any Kernel app deployment (provider keys, site credentials in vaults, payment details).
3. **Browser sessions.** If your agents ran browser sessions on 2026-11-03 between 05:41 and 07:46 UTC, the notice says three of the four accessed servers ran browser sessions; it does not say whether session content was read.
4. **Billing.** Check Kernel and the providers whose keys lived in a deployment for usage you did not generate between 2026-10-24 and 2026-11-03.

## If you are affected

- Rotate Kernel API keys and every third-party secret stored in a Kernel app deployment at the issuer, in that order. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
- Re-issue the key your agents or MCP configuration use for Kernel, and remove the old one from `.mcp.json`, environment files and CI secrets. See [MCP hygiene](../prevention/mcp-hygiene.md).
- Adopt Kernel's scoped API keys where the notice recommends them, so a leaked key reads less.
- Ask Kernel for the "technical fingerprint of the attacker" the notice offers if your own logs need matching; request it at the security address the notice gives.

## Prevention

- A platform that executes your agents holds your keys; keep an inventory of which platform holds which secret so a vendor notice turns into a rotation list the same day. See [credential hygiene](../prevention/credential-hygiene.md).
- Scope every platform key to the project and permission it needs. Kernel's own remediation list leads with scoped keys.
- Treat a vendor's logging or observability provider as part of the vendor's blast radius; the first data taken here came from a third party the vendor logs to.

## Sources
- [Kernel — Public notice of security incident, 2026-11-04](https://www.kernel.sh/blog/public-notice-of-security-incident-nov-4-2026) — fetched 2026-11-05: the three-stage account, the UTC timeline, "a small number of kernel API keys and app deployments' third-party secrets", "The breach impacted 0.28% of Kernel's customers", the ARTEX sentence, the actions taken, the scoped-key recommendation, the offer to share the attacker's fingerprint. Single source: the vendor.
- [Kernel — product site](https://www.kernel.sh/) — fetched 2026-11-05: "browser infrastructure for web agents and automations", the SDKs, CLI, hosted MCP server, vaults and payments, computer use.
- Hacker News item 50371427 ("Kernel.sh Hacked", 13 points, 2026-11-04 20:58 UTC), read through the Algolia API 2026-11-05: the link and the unanswered how-did-the-key-leak question.
- [SecurityWeek — AI-Linked Breaches Mount as WorkOS, Northflank, Trigger.dev Disclose Hacks](https://www.securityweek.com/ai-linked-breaches-mount-as-workos-northflank-trigger-dev-disclose-hacks/) — fetched 2026-11-05 (2026-11-04, Ionut Arghire): the dozen-platform count, the Wiz quotes, the Chainstack details; Kernel not mentioned.
- Related in this corpus: [GitBook incident](2026-11-gitbook-november-2-security-incident-ai-agents-rotate-api-tokens-git-sync-secrets-reauth-mcp-server.md), [Trigger.dev incident](2026-11-trigger-dev-security-incident-environment-variables-exposed-subset-of-organizations-rotate.md), [Northflank incident](2026-10-northflank-security-incident-assume-all-environment-variables-decrypted-ai-keys-abused.md), [the platform-exposure pattern file](ongoing-vibe-platform-exposure.md).
