---
id: 2026-11-bitrise-security-incident-internal-system-access-all-services-offline-rotate-secrets
title: "Bitrise security incident: unauthorized access to an internal system, all services taken offline on 2026-11-13; rotate secrets, access tokens and certificates"
date_disclosed: 2026-11-13
last_updated: 2026-11-14
severity: high
status: active
ecosystems: [bitrise, ci-cd, mobile, saas, github, code-signing]
tools_affected: ["Bitrise CI/CD (app.bitrise.io), all users", "Git provider credentials and access tokens connected to Bitrise", "secrets and environment variables stored in Bitrise apps and workspaces", "code-signing certificates and provisioning profiles uploaded to Bitrise", "mobile apps built by coding agents and shipped through Bitrise pipelines"]
tags: [breach, vendor-incident, bitrise, ci-cd, mobile, code-signing, secrets, credential-rotation, outage, investigation-ongoing]
---

## TL;DR
Bitrise, the mobile CI/CD service, detected suspicious activity in an internal cloud environment on 2026-11-13 at 16:32 UTC, confirmed unauthorized access to an internal system, and took every service offline. Bitrise says the system does not store customer data and that it has found no evidence that customer data, secrets or source code were exposed. It still tells users to rotate secrets, access tokens and certificates once they can sign in. Services were still being restored when the status page was read on 2026-11-14 at about 15:00 UTC.

## What happened

Bitrise's status page carries one incident, "Security Incident", marked SEV-1, scope All Users. Times are UTC as the page prints them. The updates are paraphrased.

| Posted | What Bitrise said |
|---|---|
| 2026-11-13 20:44 | A security incident affecting some internal secrets was detected within the last hour. Bitrise was taken offline as a precaution. No confirmation that customer data or source code was accessed. Rotate Git and source-code access credentials connected to Bitrise. |
| 2026-11-13 21:45 to 2026-11-14 00:03 | Investigation continuing. Contact is support@bitrise.io. |
| 2026-11-14 01:26 | Suspicious activity was detected on 2026-11-13 at 16:32 UTC in an internal cloud environment. Unauthorized access to an internal system that does not store customer data is confirmed. All services were taken offline as a precaution. No evidence so far that customer data, secrets or source code were exposed. |
| 2026-11-14 02:29 | No evidence of exposure found. Services are being restored in phases, with no estimate for full restoration. Rotating secrets is recommended once services are back. |
| 2026-11-14 03:36 to 14:34 | Restoration progressing. Sign-in to app.bitrise.io is expected soon. Rotate secrets, access tokens and certificates once you can sign in. |

Two statements on the page pull in different directions. The first update says the incident affected "some internal secrets" and tells users to rotate Git credentials. Later updates say no evidence of customer exposure was found. Both are printed. The times also differ: the 20:44 update says detection was within the last hour, and the 01:26 update gives 16:32 UTC. The page gives no cause, no actor and no count.

No outlet coverage was found on 2026-11-14. A Hacker News item (50489750, 4 points) links the status page. This file has one source, the vendor.

## Am I affected?

- You have a Bitrise account or workspace.
- A Bitrise app holds a Git provider connection, a personal access token, an SSH key, cloud keys, an App Store Connect or Google Play credential, or a model provider key.
- Signing certificates, provisioning profiles or keystores are uploaded to Bitrise.

## If you are affected

1. Rotate the Git and source-code access credentials connected to Bitrise now. This does not need Bitrise to be online, and it is the first thing Bitrise asked for.
2. When sign-in is back, rotate every secret and access token stored in Bitrise, as Bitrise recommends.
3. Rotate signing certificates and keystores, as Bitrise recommends. Revoke the old certificates with the issuer. The revocation step is this file's advice.
4. Review your Git provider's audit log and your cloud audit logs for use of the old credentials since 2026-11-13. This step is this file's advice.
5. Expect builds and deployments to fail until restoration is complete. Do not move secrets into a hurried replacement pipeline without scoping them.

## Prevention

- Give CI short-lived, scoped credentials through OIDC federation where the provider supports it, so a platform incident leaves little to rotate.
- Keep an inventory of what each CI app can reach. See [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) and [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).

## Sources

Single source: the vendor.

- [Bitrise status](https://status.bitrise.io), fetched 2026-11-14: the "Security Incident" entry (incident id 7055z4g9nbck), seventeen updates from 2026-11-13 20:44 UTC to 2026-11-14 14:34 UTC, SEV-1, All Users, unresolved.
- Hacker News item 50489750, seen 2026-11-14 through the Algolia search feed: the status page submitted on 2026-11-13, 4 points. The item page was not opened.
- Not covered: the incident's own URL, Bitrise's blog and trust centre, and any customer email.
