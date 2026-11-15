---
id: 2026-11-cursor-security-incident-fireworks-issued-key-agent-traces-credentials-exposed-marketplace-cache
title: "Cursor incident update: a key issued to Fireworks exposed agent traces holding credentials, which led to the tampered Claude Code extension"
date_disclosed: 2026-11-13
last_updated: 2026-11-15
severity: high
status: contained
ecosystems: [cursor, ai-coding-tools, api-keys, vscode-extension, cursor-marketplace, fireworks-ai, saas]
tools_affected: ["Cursor accounts that ran coding agent sessions outside Privacy Mode, mostly in 2025", "customers whose API credentials appeared unredacted in those traces (Cursor: less than 0.01% of customers)", "users who sent credentials to Cursor support", "Cursor users who installed or updated anthropic.claude-code 2.1.312 or 2.1.313 from Cursor's extension marketplace on 2026-10-29"]
tags: [breach, vendor-incident, cursor, fireworks-ai, third-party-vendor, agent-traces, privacy-mode, credential-exposure, api-keys, extension-marketplace, support-data]
---

## TL;DR
Cursor says an attacker used an access key Cursor had issued to Fireworks AI, which Fireworks exposed, to copy coding agent traces from a storage bucket the two companies shared. Some traces held unredacted credentials. Cursor puts the exposure at less than 0.01% of customers for API credentials and fewer than 0.05% of users for traces, and says it notified those affected. Credentials from that data let the attacker reach some of Cursor's SaaS tools and, on 2026-10-29, place the tampered `anthropic.claude-code` 2.1.312 and 2.1.313 copies on Cursor's extension marketplace cache. Cursor says it believes the incident is contained. Rotate any key Cursor's notice lists for you, rotate anything you ever pasted into a Cursor support conversation, and follow the [extension advisory](2026-10-claude-code-extension-2-1-313-cursor-marketplace-remove-and-rotate.md) if you had either version.

## What happened

Cursor published "An update on our recent security incident" on 2026-11-13. The October notice had left the publication path of the tampered extension unexplained. This post gives it. Dates are the post's. It gives no date for the first three steps.

| When | What Cursor says |
|---|---|
| not dated | "An attacker obtained an access key we had issued to Fireworks." The post says the key was exposed by Fireworks. The attacker used it to copy data from "a read-only storage bucket we used to share data with them." |
| not dated | The bucket held coding agent traces from sessions not in Privacy Mode, mostly from 2025. "A small number of those traces contained credentials that had not been redacted." |
| not dated | With credentials found in that data the attacker reached select SaaS tools Cursor uses. Cursor's monitoring found the activity. Cursor deactivated the vendor's key and began rotating credentials. |
| 2026-10-29 | Using a stolen credential, the attacker "placed malicious, unauthorized copies of Anthropic's Claude Code extension directly on the cache" serving Cursor's extension marketplace. The copies were available for about 11 hours. |
| 2026-11-01 | "The last attacker activity we have seen was on November 1, and it was blocked." |
| 2026-11-13 | "We believe the incident is contained." Cursor says it continues to monitor. The post does not say the investigation is closed. |

### What Cursor says was accessed

- Coding agent traces from sessions not in Privacy Mode: "coding agent traces were exposed for fewer than 0.05% of users."
- API credentials inside those traces: "less than 0.01% of customers had API credentials exposed."
- Archived non-production Cursor source code repositories, some holding business contact information.
- Limited customer support data and email conversations, and some credentials users had sent to Cursor support.
- Product usage metrics and contact details.
- Summaries of some coding agent conversations.

### What Cursor says was not affected

Prompts and code of Privacy Mode users, customer code repositories, Cursor's production systems, the Cursor app, official updates and release signing keys, plugins from the Cursor Marketplace, and other marketplace extensions, which Cursor says it validated as authentic. Cursor says Open VSX, the marketplace's source, "never had the malware", and that "Anthropic did not publish this copy, and this was not a vulnerability in Anthropic's product."

### The extension count

"At most 5,000 users who requested specific cached versions of the extension" may have received the tampered build. This is the same upper bound earlier coverage carried. It is an upper bound on users who requested those cached versions, not a count of compromised machines.

### What Fireworks has said

Fireworks' bulletin index was read on 2026-11-15. It lists two bulletins about its October incident, last updated 2026-10-10 and 2026-11-09, both marked "Active monitoring". Neither names Cursor. The statement that Fireworks exposed the key is Cursor's. See the [Fireworks advisory](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md).

### What Cursor changed

Cursor says it moved all inference off Fireworks, deactivated the key and cut Fireworks' access to shared datasets. It rotated the exposed credentials and then every credential in internal use, rebuilt the extension marketplace, redeployed production infrastructure, added secret scanning over repositories and other internal data, tightened network restrictions with service providers, and engaged outside forensics.

## Am I affected?

- Cursor says it contacted affected customers directly and sent team admins lists of affected keys. Check the inbox of the account owner and each team admin for a notice from Cursor.
- Cursor says that if you received no notification about coding agent traces, your data was not in those traces.
- You are in the population the traces came from if you used Cursor's agent outside Privacy Mode, mostly in 2025. Check whether Privacy Mode is on for your account or team now. This step is this file's advice.
- You have separate exposure if you ever sent a key, token or password to Cursor support.
- You have separate exposure if Cursor installed or updated `anthropic.claude-code` to 2.1.312 or 2.1.313 on 2026-10-29. The checks are in the [extension advisory](2026-10-claude-code-extension-2-1-313-cursor-marketplace-remove-and-rotate.md).

## If you are affected

1. Rotate every key named in Cursor's notice at its issuer. Cursor says it asked the issuing services to revoke them. Do not rely on that alone.
2. Rotate any credential you sent to Cursor support, whether or not you were notified. This step is this file's advice.
3. If you ran agent sessions outside Privacy Mode and those sessions printed or read secrets, such as `.env` contents or a cloud key in terminal output, treat a notice about traces as a notice about those secrets. Review the issuer's audit log for use since October 2026. This step is this file's advice.
4. For the extension, Cursor says "Uninstalling the extension alone may not be enough." Follow the steps in the extension advisory.
5. Questions go to security@cursor.com, the address the post gives.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- An agent trace is a copy of whatever the agent read and printed. Keep secrets out of the agent's view: use a secrets manager or short-lived tokens, and do not `cat` environment files in an agent session. See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Turn on the privacy setting of any coding tool that offers one if your sessions touch secrets or customer data, and check what each tool shares with its inference and training vendors.
- Never send a live credential to a vendor's support channel. If support needs one, issue a temporary key and revoke it afterwards.
- Pin or review extension updates on machines that hold production credentials. See [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources

The vendor's own incident post is the primary. The Hacker News article restates it and adds no independent finding.

- [Cursor: An update on our recent security incident](https://cursor.com/blog/security-incident-update), dated 2026-11-13, fetched 2026-11-15: the key issued to Fireworks, the shared bucket, the traces and percentages, the SaaS access, the marketplace cache, the 5,000 upper bound, the 2026-11-01 last activity, the containment statement, the not-affected list, the remediation list.
- [The Hacker News: Cursor Says Stolen Fireworks AI Key Led to Trojanized Claude Code Extension Incident](https://thehackernews.com/2026/11/stolen-fireworks-ai-key-led-to-cursor.html), dated 2026-11-15, fetched 2026-11-15: a restatement of Cursor's post. It carries no statement from Fireworks or Anthropic.
- [Fireworks AI security bulletins](https://fireworks.ai/security/bulletins), fetched 2026-11-15: two bulletins, last updated 2026-10-10 and 2026-11-09, neither naming Cursor.
- Hacker News item 50496937, seen 2026-11-15 through the Algolia search feed: Cursor's post submitted on 2026-11-14, 6 points. The item page was not opened.
- Not opened this run: Cursor's October notice (`cursor.com/blog/claude-code-extension-security-notice`), which the post links for extension cleanup. The extension advisory cites it from earlier runs.
