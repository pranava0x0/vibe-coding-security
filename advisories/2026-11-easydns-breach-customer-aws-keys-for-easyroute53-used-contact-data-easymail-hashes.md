---
id: 2026-11-easydns-breach-customer-aws-keys-for-easyroute53-used-contact-data-easymail-hashes
title: "easyDNS breach: customers' AWS keys stored for easyRoute53 were used, and contact data and unsalted easyMail password hashes were exposed"
date_disclosed: 2026-11-27
last_updated: 2026-11-28
severity: high
status: active
ecosystems: [dns, hosting, aws, email]
tools_affected: ["easyDNS accounts", "easyRoute53 integrations that stored a customer AWS key", "easyMail mailboxes"]
tags: [vendor-breach, dns-provider, aws-keys, stored-credentials, password-hashes, credential-rotation]
---

## TL;DR

[easyDNS says](https://easydns.com/blog/2026/11/27/easydns-data-breach/) someone logged in to its AWS account without authorisation on 2026-11-26 and used AWS keys that some customers had stored for the easyRoute53 integration. Contact data, limited billing data and unsalted SHA256 easyMail password hashes were also exposed. easyDNS says control panel passwords and REST API keys were not exposed. Change your easyMail password. As a caution, replace any AWS key you gave easyRoute53.

## What happened

The CEO's post of 2026-11-27 gives this account. On the morning of 2026-11-26 the company learned of an unauthorised login to its AWS account. It also received reports of unauthorised use of some customers' keys stored for easyRoute53, which it calls BYOK. It says it alerted affected easyRoute53 users immediately. By about 17:00 ET it had confirmed the entry point and found that "the breach went beyond the AWS keys".

The post says the investigation continues and that a fuller post-mortem will follow. It does not name the entry point. It says the incident is not related to CVE-2026-109618 or CVE-2026-109619.

| Data | Status per easyDNS |
|---|---|
| Customer AWS keys stored for easyRoute53 | some were used without authorisation |
| Name, email, address, phone and fax numbers | may be exposed, varies by customer |
| Card last four digits, expiry, postal code, billing name and address | may be exposed for customers with recurring billing |
| easyMail address and password hash | exposed. The hashes are SHA256 with no salt. |
| Control panel passwords and their hashes | not exposed |
| REST API keys and their Argon2id hashes | not exposed |
| Dynamic DNS tokens and their salted hashes | not exposed |
| Secret question answers and recovery codes | not exposed |
| Full card numbers | never stored |

easyDNS says no domains, DNS, email, certificates or web forwarding were operationally affected. The easyRoute53 integration is offline, with a stated aim to resume by the end of the weekend. The company is forcing a control panel password reset at next login.

The post does not say how many customers or keys were affected.

## Am I affected?

- You have an easyDNS account. Your contact data may be exposed.
- You enabled easyRoute53 with your own AWS key. easyDNS says it alerted the users whose keys were used. The post does not say whether unused stored keys were also read.
- You use easyMail. Your mailbox password hash was exposed.

To find AWS activity from a key you gave easyRoute53, look up the access key id in CloudTrail:

```bash
aws cloudtrail lookup-events \
  --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=<your-access-key-id> \
  --start-time 2026-11-01
```

The start date is a wide starting point. easyDNS has not published when the access began.

## If you are affected

easyDNS asks for two things:

1. Change your easyMail password.
2. Watch for phishing that uses your contact details.

These steps go beyond the vendor's post:

- Deactivate and replace any AWS access key stored in easyRoute53, whether or not you were alerted. Review Route 53 hosted zones and records for changes you did not make.
- Change the easyMail password anywhere else it was used. An unsalted SHA256 hash of a weak password can be cracked, as the post says.
- See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Give a DNS integration an IAM user limited to the Route 53 actions and hosted zones it needs. A key with wider rights exposes everything those rights reach when the vendor is breached.
- See [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [easyDNS, "easyDNS Data Breach", Mark E. Jeftovic, 2026-11-27](https://easydns.com/blog/2026/11/27/easydns-data-breach/), read 2026-11-28. Single source: the vendor. Every fact above except the steps marked as going beyond the post.
- [Hacker News item 50671965](https://news.ycombinator.com/item?id=50671965), 7 points when read on 2026-11-28. Where the sweep found the post.
