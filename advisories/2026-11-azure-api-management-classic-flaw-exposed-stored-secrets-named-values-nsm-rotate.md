---
id: 2026-11-azure-api-management-classic-flaw-exposed-stored-secrets-named-values-nsm-rotate
title: "Azure API Management classic tiers: flaw exposed stored secrets and named values, used in attacks before Microsoft's 2026-11-19 fix; NSM says rotate them"
date_disclosed: 2026-11-20
last_updated: 2026-11-28
severity: high
status: contained
ecosystems: [azure, cloud, api-gateway]
tools_affected: ["Azure API Management classic tiers (Basic, Standard and Premium, per Anders Kristiansen's reading)", "any backend, identity provider or API whose key, client secret or token was stored in an APIM instance"]
tags: [cloud-provider-incident, secrets-exposure, api-gateway, exploited, credential-rotation, no-cve]
---

## TL;DR

Norway's National Security Authority says an unknown actor went after access tokens, secrets and named values in Azure API Management. [NSM's notice](https://nsm.no/aktuelt/nsm-deler-tiltak-mot-sarbarhet-i-azure-api-management) of 2026-11-20 says the flaw should now be closed. It tells every APIM customer to assume those values are exposed and to rotate all tokens and secrets. V2 and Consumption tier instances are not vulnerable, per NSM. No CVE id appears in any source read.

## What happened

NSM says it learned of the flaw earlier in the week of 2026-11-20 and that several Norwegian organisations were hit, including Equinor and Skagerak Energi. It says the flaw affects several sectors in Norway and outside it. NSM also says it is still uncertain how widely the flaw was used.

[SecurityWeek](https://www.securityweek.com/azure-flaw-exploited-to-target-secrets-at-norwegian-energy-firms/) reported on 2026-11-23 that Microsoft is notifying customers. It cites a private notification that one customer posted on Reddit. Per that account, Microsoft found the issue on 2026-11-18 and closed the access path the next day. SecurityWeek quotes Microsoft:

> Our investigation found that customers were exposed and an unauthorized party could have used the issue to access secrets stored in Azure API Management Classic instances before Microsoft identified the security issue

SecurityWeek lists the data that can be exposed as secrets stored as named values, client secrets for identity providers, subscription keys, and tokens for APIM's direct management APIs. It says Equinor reported an attack on 2026-11-17 and found no evidence that data was stolen or altered.

No Microsoft page was opened for this file. The Reddit post was not opened. No source read describes the flaw itself.

## Am I affected?

NSM gives a version check for your own instance. Open `https://<your-gateway-hostname>/internal-status-0123456789abcdef` and read `RuntimeVersion`.

| RuntimeVersion | NSM's reading |
|---|---|
| `0.52.x` | patched if the last number is 31936 or higher |
| `0.53.x` | patched if the last number is 31938 or higher |
| other patterns, for example `0.53.4608.0` or `0.52.4150.0` | V2 or Consumption tier, not vulnerable |

A patched instance still held its secrets while the flaw was open. NSM's rotation advice applies to every APIM customer, whatever the version check shows.

[Anders Kristiansen](https://anderskristiansen.com/post/2026/apim-legacy-access/), whom SecurityWeek calls a security expert, names Basic, Standard and Premium as the affected classic tiers. The `sku.name` field of the `Microsoft.ApiManagement/service` resource shows the tier.

## If you are affected

NSM's steps:

1. Rotate every token and secret stored in APIM, and every named value that holds one.
2. Map what data and systems sit behind each APIM instance.
3. If the instance is not updated, contact Microsoft. Organisations in Norway that see signs of compromise are asked to contact NSM.

Kristiansen's post adds steps that NSM does not give:

- Rotate backend credentials, app registration secrets, subscription keys, the Key Vault secrets that APIM references, and the tenant access keys.
- Set "Enable Management REST API" to No on every instance. He says the direct Management API does not use Entra ID and its calls are not recorded in the Activity log.
- Unpublish a developer portal you do not use and disable sign-up.
- Check Entra service principal sign-in logs and Key Vault audit logs for use of the stored credentials.

See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Keep model provider keys and backend secrets in a vault, and give the gateway a managed identity where the backend supports one. Kristiansen notes that Key Vault references do not protect a value from someone who can edit policies or use tracing.
- See [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [NSM, "NSM deler tiltak mot sårbarhet i Azure API Management"](https://nsm.no/aktuelt/nsm-deler-tiltak-mot-sarbarhet-i-azure-api-management), in Norwegian, read 2026-11-28. The page says it was updated on 2026-11-23. The actor's targets, the rotation advice, the version check, the two named companies.
- [SecurityWeek, 2026-11-23](https://www.securityweek.com/azure-flaw-exploited-to-target-secrets-at-norwegian-energy-firms/), read 2026-11-28. The Microsoft quotation, the 2026-11-18 and 2026-11-19 dates from a customer's copy of the notification, the data list, the Equinor and Skagerak Energi dates.
- [Anders Kristiansen, "Azure API Management advisory: what to check and how to hunt after recent attacks"](https://anderskristiansen.com/post/2026/apim-legacy-access/), modified 2026-11-21, read 2026-11-28. The tiers, the extra rotation and hardening steps. The post says it is the author's understanding from public sources.
- Not opened: Microsoft's customer notification, the Reddit post that carries it, Equinor's and Skagerak Energi's statements.
