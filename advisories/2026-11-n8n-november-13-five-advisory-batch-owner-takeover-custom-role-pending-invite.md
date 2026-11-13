---
id: 2026-11-n8n-november-13-five-advisory-batch-owner-takeover-custom-role-pending-invite
title: "n8n: five advisories on 2026-11-13, two High (owner takeover through a custom role, pending-invite takeover); fixed 1.123.96, 2.47.6, 2.48.3"
date_disclosed: 2026-11-13
last_updated: 2026-11-13
severity: high
status: patched
ecosystems: [npm, n8n, ai-agents]
tools_affected: ["n8n (npm) before 2.47.6 and before 2.48.3 (four of the five)", "n8n before 1.123.96 on the v1 line (two of the five list a v1 range at this version)", "n8n before 1.123.90 and before 2.14.0 (the pending-invite takeover)", "n8n custom instance roles with user management permissions", "n8n AWS Bedrock Chat Model and Embeddings nodes", "n8n integration nodes that build API paths from record, table or resource ids", "n8n trigger nodes registered at workflow activation"]
tags: [n8n, ghsa-batch, workflow-automation, credential-hub, account-takeover, privilege-escalation, ssrf, path-traversal, authorization, patched, no-cve]
---

## TL;DR
n8n published five advisories on 2026-11-13, none with a CVE. Two are High. A user holding a custom instance role with user management permissions could get a password reset link for the owner or change the owner's role (GHSA-q8rc-7m84-mfvj, 7.5). A member who could list users could set the password of any account with a pending invitation (GHSA-m7qq-gm3x-v79g, 7.7). Upgrade to `2.47.6` or later on the stable line, `2.48.3` or later on beta, or `1.123.96` or later on v1. The advisories and the vendor bulletin also name a `3.2.2` that npm does not carry as of 2026-11-13.

## What happened

This is the next n8n batch after [October 28](2026-10-n8n-october-28-twelve-advisory-batch-deprecated-code-nodes-expression-isolation-graphicsmagick.md). The security team's community bulletin "Security update — 13 November 2026" (posted 11:55 UTC) lists five advisories, two High and three Medium, and four fixed lines: "v1 patched in v1.123.96", "v3 patched in v3.2.2", "beta patched in v2.48.3", "stable patched in v2.47.6". The vendor tab, pages 1 and 2, showed four rows dated 2026-11-13 when read. The fifth, the invitation advisory, is listed in the bulletin and its own page is dated 2026-11-13. Every page says "No known CVE".

Registry facts, read 2026-11-13 with `npm view n8n time` and `npm view n8n dist-tags`:

| Version | Published (UTC) | Note |
|---|---|---|
| 1.123.96 | 2026-11-13 08:24 | v1 fix |
| 2.48.3 | 2026-11-13 08:28 | beta fix |
| 2.47.6 | 2026-11-13 08:40 | stable fix |
| 2.47.7 | 2026-11-13 09:44 | `latest`, `stable`, `rc` when read |
| 2.48.4 | 2026-11-13 09:44 | `next`, `beta` when read |
| 3.2.2 | not on npm | `npm view n8n@3.2.2` returns 404; `npm view n8n versions` lists no 3.x release |

The five advisories, as the vendor pages print them:

- **GHSA-m7qq-gm3x-v79g: Invitation Acceptance Endpoint Lets a Member Take Over Pending User Accounts (7.7, High).** The invitation acceptance endpoint did not verify a signed invitation token and accepted any inviter and invitee user ids. A member who could list users could read a pending account's id and set its password, then sign in as that user, as an admin if the invitation carried the admin role. Affected `< 1.123.90` and `< 2.14.0`. Fixed `1.123.90` (npm 2026-10-29) and `2.14.0` (npm 2026-03-24), so the fix shipped before the advisory. Reporter odgrso.
- **GHSA-q8rc-7m84-mfvj: Custom Instance Role with User Management Permissions Gives Control of the Owner Account (7.5, High).** The owner account is protected from changes by other users, but the password reset link and role change operations did not apply that protection to users with a custom instance role. The advisory says this "gave the attacker full control of the instance". It requires the custom roles feature and a custom role with user management permissions assigned to the attacker. Affected `< 2.47.6`, `< 2.48.3`, `< 3.2.2`. No v1 range is listed.
- **GHSA-c772-hjfp-gfc2: Integration Nodes Send Authenticated Requests to Unintended API Endpoints (5.3).** Several nodes built the URL path of an API request from parameters such as record, table or resource ids without encoding them, so a value with relative path segments reached a different endpoint of the same service with the node's stored credential. The risk applies when a workflow passes untrusted input, such as a webhook body, into one of those parameters. Affected `< 1.123.96`, `< 2.47.6`, `< 2.48.3`, `< 3.2.2`.
- **GHSA-h59h-rf6m-7jp5: Workflow Activation Allows Trigger Nodes to Use Credentials the Publisher Cannot Access (5.3).** Activation registers trigger nodes with connected services using the credentials on those nodes and did not check that the publishing user had access to them. A member who knew the id of another user's credential could create or delete webhooks on the connected service with that credential. Same four ranges. Reporter assakafpix.
- **GHSA-g333-hr44-g82p: AWS Bedrock Nodes Skip SSRF Protection for Custom Runtime Endpoints (5.3).** An AWS credential can set a custom Bedrock runtime endpoint, and requests to it did not pass through n8n's SSRF protection. A member who could create an AWS credential could make n8n send requests to an internal address and see the start of the response in the node error. Affected `< 2.47.6`, `< 2.48.3`, `< 3.2.2`. No v1 range is listed.

The bulletin says n8n Cloud instances are patched automatically.

## Am I affected?

```bash
# Installed version. Stable below 2.47.6 or beta below 2.48.3 is affected by four of the five.
# v1 below 1.123.96 is affected by the two that list a v1 range at that version.
# v1 below 1.123.90, or 2.x below 2.14.0, is affected by the pending-invite takeover.
npm ls -g n8n 2>/dev/null | grep n8n
docker ps --format '{{.Image}}' | grep n8n
npm view n8n dist-tags   # latest/stable 2.47.7, next/beta 2.48.4 on 2026-11-13
```

- Custom-role takeover: you use custom instance roles, and a role with user management permissions is assigned to someone you would not hand the owner account.
- Pending-invite takeover: invitations sat unaccepted while the instance ran a version below 1.123.90 or 2.14.0.
- Bedrock SSRF: members can create AWS credentials. Check AWS credentials for a custom Bedrock Runtime Endpoint you did not set.
- Trigger credentials: the advisory's workaround is to review connected services such as GitLab and GitHub for unexpected webhooks.
- Path parameters: a workflow passes webhook or other external input into a node's record, table or resource id.

## If you are affected

1. Upgrade to `2.47.6` or later, `2.48.3` or later, or `1.123.96` or later. Do not wait for a 3.x package. None is on npm.
2. If you cannot upgrade today, the vendor's interim steps are: remove user management permissions from custom roles held by users who are not fully trusted, enable two-factor authentication on the owner account, delete unaccepted invitations and resend them after upgrading, and remove unexpected custom Bedrock endpoints. The vendor says these "do not fully remediate the risk".
3. If the owner's password or role changed without your action, or a pending account signed in before its invitee accepted, treat the instance as taken over. Rotate every credential stored in n8n and review workflow changes. [If your web app was compromised](../playbooks/if-your-webapp-was-compromised.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) cover the steps.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): scope each n8n credential to the resources its workflows need, so a node that reaches the wrong endpoint reaches little.
- Keep n8n membership to people you would trust with every stored credential. Earlier batches in this corpus also include paths from a member to another user's credential or to the instance.
- Restrict outbound connections from the n8n host to internal addresses at the network.

## Sources

Single source: the vendor, for its own product.

- [n8n community: Security update — 13 November 2026](https://community.n8n.io/t/security-update-13-november-2026/328485), fetched 2026-11-13: the list of five, the four fixed lines, the Cloud sentence.
- [GHSA-m7qq-gm3x-v79g](https://github.com/n8n-io/n8n/security/advisories/GHSA-m7qq-gm3x-v79g), fetched 2026-11-13: score, ranges, mechanism, conditions, workarounds.
- [GHSA-q8rc-7m84-mfvj](https://github.com/n8n-io/n8n/security/advisories/GHSA-q8rc-7m84-mfvj), fetched 2026-11-13: score, ranges, the quoted impact sentence, workarounds.
- [GHSA-c772-hjfp-gfc2](https://github.com/n8n-io/n8n/security/advisories/GHSA-c772-hjfp-gfc2), fetched 2026-11-13: score, ranges, mechanism.
- [GHSA-h59h-rf6m-7jp5](https://github.com/n8n-io/n8n/security/advisories/GHSA-h59h-rf6m-7jp5), fetched 2026-11-13: score, ranges, mechanism.
- [GHSA-g333-hr44-g82p](https://github.com/n8n-io/n8n/security/advisories/GHSA-g333-hr44-g82p), fetched 2026-11-13: score, ranges, mechanism.
- [n8n security advisories tab](https://github.com/n8n-io/n8n/security/advisories), fetched 2026-11-13: pages 1 and 2, four rows dated 2026-11-13.
- npm registry, `npm view n8n time`, `dist-tags` and `versions`, read 2026-11-13: the publish times and the absence of any 3.x release.
