---
id: 2026-11-1984-hosting-infrastructure-attack-all-services-suspended-scope-under-investigation
title: "1984 Hosting: all services suspended on 2026-11-20 after an attack on its infrastructure; scope still under investigation, most VPS and sites back by 2026-11-27"
date_disclosed: 2026-11-20
last_updated: 2026-11-27
severity: medium
status: active
ecosystems: [hosting, vps, dns, email]
tools_affected: ["1984 Hosting (1984 ehf, Iceland) VPS instances", "1984 Hosting shared web hosting", "1984 Hosting email, webmail and DNS"]
tags: [hosting-provider, vps, incident, outage, infrastructure-breach, investigation-ongoing, no-cve]
---

## TL;DR

Icelandic host 1984 ehf suspended all services on 2026-11-20 after what it and CERT-IS called an extensive and serious attack on its infrastructure, per [their joint statement as printed by DV](https://dv.is/frettir/2026/11/20/stodva-thjonustu-timabundid-eftir-alvarlega-tolvuaras-a-innvidi-1984-ehf). The statement says the scope is under investigation and more systems may be affected than confirmed. No vendor text read for this file says whether customer data, virtual machine disks or account credentials were accessed. The [status page](https://status.1984.is/status/public) said on 2026-11-27 that about 90% of VPS instances and about 85% of hosted websites were back online. If you host there, rotate the secrets stored on your servers as a caution. The vendor has not asked for that.

## What happened

| Date | Event | Source |
|---|---|---|
| 2026-11-20 | 1984 ehf and CERT-IS issue a joint statement. All services are suspended. DNS and email are to return first, under monitoring. | DV, dated 11:08 |
| 2026-11-21 | The status page opens an entry titled "A November 2026 security incident". | status page API, created 17:20:09 |
| 2026-11-24 | Email and webmail are fully operational from early that morning. | status page, 2026-11-27 update |
| 2026-11-27 | "Approximately 90% of VPS instances are now online." "Approximately 85% of hosted websites are now back online." | status page update, 14:10 UTC |

The joint statement is in Icelandic. It says first findings point to a well-organised and technically advanced attack. It says the company cannot rule out that more systems were affected than had been confirmed. It says the other services return only after security measures and verification are complete. The company reported the incident to CERT-IS, which is assisting.

[Daily Northern](https://www.dailynorthern.com/39679/icelandic-web-host-suspends-services-after-cyberattack/) carried the same points in English on 2026-11-20, citing mbl.is.

The status page entry held only the 2026-11-27 restoration update when read. Earlier text of the entry was not available.

### What no source read states

- Whether the attacker read or copied customer data, VPS disks, backups, mailboxes or control-panel credentials.
- How the attacker got in, and when.
- Whether customers were told to change passwords or keys.

A commenter on [the Hacker News thread](https://news.ycombinator.com/item?id=50656686) says keys were taken from a virtual machine a customer had deleted at 1984. The commenter adds that it is unclear whether that is this incident. No other source read supports it.

## Am I affected?

- You are affected by the outage if you run a VPS, a shared-hosting site, email or DNS at 1984 Hosting.
- Whether your data was reached is not known. The vendor has not said.
- List what the server holds: `.env` files, database passwords, API keys for model providers, SSH private keys, deploy tokens and TLS private keys.

## If you are affected

The vendor's statements give no customer steps. These are this file's advice.

1. When your server returns, check it before putting it back into use. Compare the authorised SSH keys, user accounts, scheduled jobs and running services with what you expect.
2. Rotate the secrets the server stored, starting with cloud and model-provider API keys. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
3. Change your 1984 control-panel password and any password reused elsewhere.
4. If DNS for your domain is hosted there, compare the records with your own copy.
5. Watch the status page for a statement on data access.

## Prevention

- Keep secrets in a secret manager, not in files on a rented server. See [credential hygiene](../prevention/credential-hygiene.md).
- Keep off-provider backups and a copy of your DNS zone so you can move during a provider outage.

## Sources

- [DV, "Stöðva þjónustu tímabundið eftir alvarlega tölvuárás á innviði 1984 ehf."](https://dv.is/frettir/2026/11/20/stodva-thjonustu-timabundid-eftir-alvarlega-tolvuaras-a-innvidi-1984-ehf), 2026-11-20, read 2026-11-27: the joint statement of 1984 ehf and CERT-IS, printed in full in Icelandic. The paraphrase in English is this file's.
- [1984 Hosting status page](https://status.1984.is/status/public), read 2026-11-27 through its JSON API: entry title, creation and update times, the quoted restoration figures.
- [Daily Northern](https://www.dailynorthern.com/39679/icelandic-web-host-suspends-services-after-cyberattack/), 2026-11-20: English summary citing mbl.is.
- [Hacker News item 50656686](https://news.ycombinator.com/item?id=50656686), 2026-11-26, read through the Algolia items API: the commenter's claim.
- Not opened: an Iceland Monitor article of 2026-11-21 linked in the thread (HTTP 403), the mbl.is report, and `1984.is` (connection reset on 2026-11-27).
