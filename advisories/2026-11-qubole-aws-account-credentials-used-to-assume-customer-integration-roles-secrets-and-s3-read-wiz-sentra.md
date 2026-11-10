---
id: 2026-11-qubole-aws-account-credentials-used-to-assume-customer-integration-roles-secrets-and-s3-read-wiz-sentra
title: "Qubole's AWS account credentials used to assume customers' integration roles, 2026-10-14 to 10-26: secrets and S3 data read; no vendor statement"
date_disclosed: 2026-11-09
last_updated: 2026-11-10
severity: high
status: active
ecosystems: [aws, iam, saas-integration, cloud-credentials, secrets, data-platform]
tools_affected: ["any AWS account holding an IAM role whose trust policy names Qubole's AWS account, including accounts that stopped using Qubole", "AWS access keys created for a Qubole integration (a separate 2026-10-08 to 10-11 key-testing activity)", "Lambda environment variables, Secrets Manager secrets and SSM parameters readable by such a role", "S3 buckets readable by such a role", "AWS keys, Microsoft Entra ID client secrets and Okta client credentials stored in those secrets"]
tags: [vendor-incident, supply-chain, cross-account-role, iam, external-id, dormant-integration, secrets-manager, ssm-parameter-store, lambda-environment-variables, s3, rotate-credentials, no-vendor-statement, wiz, sentra]
---

## TL;DR
Wiz and Sentra reported on 2026-11-09 that someone holding IAM user credentials from the AWS account Qubole's platform uses assumed the cross-account roles that Qubole customers had created for it, between 2026-10-14 and 2026-10-26. Inside each customer account the actor listed resources, read Lambda environment variables, Secrets Manager secrets and SSM parameters, tested the AWS keys, Entra ID client secrets and Okta client credentials found there, and read S3 buckets, in some sessions whole buckets. Most of the roles belonged to integrations the customer no longer used but had never removed. Qubole and its owner had published no statement when the reports were read on 2026-11-10, and neither Qubole nor AWS answered The Register. If any AWS account you control has a role that trusts Qubole, check CloudTrail from 2026-10-01, remove the trust, rotate everything the role could read and revoke its sessions.

## What happened

**Who reported it.** Sentra says it spotted the same activity across its customers' environments, identified it as one campaign in under 24 hours and brought it to Wiz. Wiz's incident response team investigated with Sentra and Mandiant and published "Qubole Cross-Account Access Abused in the Wild" on 2026-11-09 (Zack Morrow, Sean Johnstone, Benjamin Read). Those are two firms with their own observations. The Hacker News and The Register (both 2026-11-09) report the Wiz post.

**What the actor had.** Per Wiz, IAM user credentials in an AWS account that Qubole's platform uses to assume roles in customer accounts. How the credentials were obtained is not stated by anyone. Qubole runs in a customer's AWS account through a role whose trust policy names Qubole's account and requires an External ID. Every role assumption Wiz observed carried the External ID and every one succeeded. Wiz notes the External ID appears in clear text in CloudTrail and in vendor and infrastructure-as-code files, and is not a secret. On 2026-10-18 the actor began using a second IAM user from the same account. Sentra says all of the activity came from outside Qubole's network, through a rented server and a VPN service.

**What was read.** Wiz lists three categories. Configuration and metadata for storage, compute, database, identity and key resources, including Lambda function configuration with its environment variables. Secrets: Secrets Manager values and SSM Parameter Store values, after which the actor validated the AWS keys, Entra ID client secrets and Okta client credentials it found. Data: S3 buckets the role could reach were listed and read, and "in some sessions, entire buckets were downloaded". Sentra adds that about 100 passwords and keys were read in seven minutes in one environment, that a final pass took production database backups, and that the actor made no write actions.

**Dormant trust.** Wiz, by email to The Register: "Because many organizations left trust policies active even after deprecating the platform, the attacker was able to successfully assume integration roles." In most affected environments the actor's requests were the only role assumptions from the vendor account in October. Sentra says the roles it saw had been dormant since spring.

**How many.** Wiz gives no count and declined to give one to The Register. Its post says "multiple victim AWS environments". Sentra's post says "more than a dozen organizations" in one place and "dozens of Qubole customers" in another. This file repeats those as each firm's words and derives no number.

**A second, unlinked activity.** From 2026-10-08 to 2026-10-11 someone tested customer-owned AWS access keys that Wiz believes were created for Qubole integrations, in a small number of environments. Wiz has not linked it to the role assumptions.

**What the vendor has said.** Nothing public as of 2026-11-10. Wiz's post does not say whether Qubole responded. The Hacker News says neither Qubole nor Idera, which it names as Qubole's owner, had posted a statement. The Register says neither Qubole nor AWS responded to it. Sentra says it warned its own affected customers directly and does not say Qubole notified anyone. Status is `active` for that reason: the credentials' origin is unknown, no rotation by the vendor is confirmed, and the customer-side trust stays in place until each customer removes it.

**Attribution.** Wiz has not tied the activity to a known group and calls it opportunistic. Wiz also found a bootable Linux image on infrastructure the actor controlled and has not seen it deployed. Neither fact changes what a customer does.

**Why it is here.** This is the third-party-role version of the platform breaches this corpus tracks for [Trigger.dev](2026-11-trigger-dev-security-incident-environment-variables-exposed-subset-of-organizations-rotate.md), [Railway](2026-10-railway-environment-variable-store-breach-rotate-every-secret.md) and [Fireworks AI](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md): the customer's secrets were reached through a vendor's access, and the customer learns it from researchers. Generated infrastructure code and agent-run setup scripts create exactly these roles, an account-wide trust plus an External ID plus broad read permissions, and nothing removes them when the trial ends.

## Am I affected?

1. **Find roles that trust Qubole.** In every account and region: `aws iam list-roles --query 'Roles[].[RoleName,AssumeRolePolicyDocument]' --output json` and search the trust policies for an external account principal you recognise as Qubole's from your own setup records. Include accounts that stopped using Qubole. Wiz's general advice is to inventory every role whose trust policy allows any external account.
2. **Read CloudTrail from 2026-10-01.** Look for `AssumeRole` on those roles where `userIdentity.accountId` is the Qubole account and `sourceIPAddress` is not an AWS address. Wiz's detection guidance lists the role session name, with a `quiam-` prefix, among the fields to review. Follow each session through `GetCallerIdentity`, `ListBuckets`, `ListObjects`, `GetObject`, `GetFunctionConfiguration`, `ListSecrets`, `GetSecretValue`, `DescribeParameters` and `GetParameter`.
3. **Check what the role could read.** Lambda configuration, Secrets Manager, SSM parameters and S3. If S3 data events or server access logs were off, you cannot tell which objects were read; Wiz says several victims were in that position.
4. **Check the separate key activity.** If you ever created an IAM user and access key for Qubole, look for its use between 2026-10-08 and 2026-10-11.
5. **Check identity providers.** Wiz says the actor tested Entra ID and Okta client credentials found in secrets. Review sign-in logs for those applications in the same window.

## If you are affected

- Remove Qubole's account from the role's trust policy, or delete the role if the integration is unused.
- Wiz: "If the threat actor assumed an integration role, rotate every secret, parameter and Lambda environment variable the role could read." Rotate at the issuer, including the AWS keys, Entra ID client secrets and Okta client credentials stored in those values. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) has the order.
- Revoke the role's active sessions. Rotating a credential does not end a session already issued.
- Preserve CloudTrail and S3 logs before they expire, and tell the vendor.
- Treat data in readable buckets as disclosed where logs cannot show otherwise.

## Prevention

- **Remove an integration's role when you stop using the integration.** A trust policy has no expiry. Put third-party roles in the same offboarding list as API keys.
- **Narrow the trust.** Replace the account-wide principal with the vendor's specific principal where the vendor supports it, and add a source IP or VPC endpoint condition for the vendor's published ranges. Wiz: "a source IP condition alone would have blocked every role assumption we observed."
- **Do not treat the External ID as a secret.** It protects against the confused-deputy problem, not against someone who holds the vendor's own credentials. Use a distinct value per role and change it after an incident.
- **Give the role less.** A data-platform role rarely needs `GetSecretValue`, `GetParameter` or Lambda configuration reads. [Credential hygiene](../prevention/credential-hygiene.md) and [the supply-chain attack surface](../prevention/supply-chain-attack-surface.md) cover vendor access.
- **Log enough to answer the question later.** An organization-wide CloudTrail trail, and S3 data events for buckets that hold sensitive data.

## Sources

- [Wiz: Qubole Cross-Account Access Abused in the Wild](https://www.wiz.io/blog/qubole-cross-account-access-abused-in-the-wild), fetched 2026-11-10: published 2026-11-09; the dates, the IAM user credentials, the External ID statement, the three access categories, the 2026-10-08 to 10-11 key activity, the recommendations, the CloudTrail event names and the `quiam-` session prefix, the stated limits; no customer count; no vendor response stated.
- [Sentra: Inside the Qubole Supply Chain Attack](https://sentra.io/blog/breaches/inside-the-qubole-supply-chain-attack), fetched 2026-11-10: published 2026-11-09 (Ron Reiter with three co-authors); Sentra's own detection across customer environments, the dormant roles, "more than a dozen organizations" and "dozens of Qubole customers", about 100 secrets in seven minutes, the database backups, no write actions; no Qubole statement. The post is also a product pitch.
- [The Register: Attackers backdoor trusted AWS integrations to steal secrets](https://www.theregister.com/security/2026/11/09/attackers-backdoor-trusted-aws-integrations-to-steal-secrets/5308553), fetched 2026-11-10: 2026-11-09 19:59 UTC; Wiz's emailed sentence on trust policies left active; Wiz declined to give a count; neither AWS nor Qubole responded.
- [The Hacker News: Hackers Exploit Qubole's Trusted AWS Access to Breach Customer Accounts and Steal Data](https://thehackernews.com/2026/11/hackers-exploit-quboles-trusted-aws.html), fetched 2026-11-10: 2026-11-09; names Idera as Qubole's owner and says neither had posted a statement; the source-IP quote from Wiz. Outlet coverage of the Wiz post, not a third source.
- Hacker News item 50432147 ("Supply chain attack on Qubole customers", 16 points on 2026-11-09), seen in the Algolia feed on 2026-11-10; it links the Sentra post.
- Not found: any statement from Qubole or its owner. Not opened: Qubole's own status or security pages, which no source links.
