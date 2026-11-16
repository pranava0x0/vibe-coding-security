---
id: 2026-11-bitrise-security-incident-internal-system-access-all-services-offline-rotate-secrets
title: "Bitrise security incident: unauthorized access to an internal system, all services taken offline on 2026-11-13; rotate secrets, access tokens and certificates"
date_disclosed: 2026-11-13
last_updated: 2026-11-16
severity: high
status: active
ecosystems: [bitrise, ci-cd, mobile, saas, github, code-signing]
tools_affected: ["Bitrise CI/CD (app.bitrise.io), all users", "Git provider credentials and access tokens connected to Bitrise", "secrets and environment variables stored in Bitrise apps and workspaces", "code-signing certificates and provisioning profiles uploaded to Bitrise", "mobile apps built by coding agents and shipped through Bitrise pipelines"]
tags: [breach, vendor-incident, bitrise, ci-cd, mobile, code-signing, secrets, credential-rotation, outage, investigation-ongoing]
---

## TL;DR
Bitrise, the mobile CI/CD service, detected suspicious activity in an internal cloud environment on 2026-11-13 at 16:32 UTC, confirmed unauthorized access to an internal system, and took every service offline. Bitrise says the system does not store customer data and that it has found no evidence that customer data, secrets or source code were exposed. It still tells users to rotate secrets, access tokens and certificates once they can sign in. Services were still being restored when the status page was read on 2026-11-14 at about 15:00 UTC. On 2026-11-15 at 14:23 UTC the page said api.bitrise.io and app.bitrise.io were back in a limited safety mode with most features unavailable, and the incident was still unresolved.

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

## Update 2026-11-15: sign-in and the API return in a limited safety mode; a 2026-11-14 update refers to signs of a live attack; still unresolved

The status page was re-read on 2026-11-15 at about 15:20 UTC. It carried 18 more updates after the 2026-11-14 14:34 UTC one. The incident is listed as unresolved, SEV-1, All Users. Updates are paraphrased except where quoted.

| Posted (UTC) | What Bitrise said |
|---|---|
| 2026-11-14 16:05 to 19:31 | app.bitrise.io is back online in a limited safety mode. |
| 2026-11-14 20:35 | Work continues on restoring logins and build infrastructure. Bitrise wrote that it shut down and rotated all the secrets its platform uses "minutes after we saw an indication of live a attack on our internal system" (wording as printed). |
| 2026-11-14 21:45 to 2026-11-15 07:32 | Only app.bitrise.io is back, in limited safety mode. Full restoration is not expected before 2026-11-15. |
| 2026-11-15 08:32 to 14:23 | api.bitrise.io and app.bitrise.io are back online in limited safety mode. Most features remain unavailable. |

Every update repeats the recommendation to rotate all secrets, access tokens and certificates stored in Bitrise once you can sign in. Sign-in is now possible, so step 2 and step 3 above can be done today. The page still gives no cause, no actor, no count and no post-mortem date. No other incident was opened on or after 2026-11-14. `status` stays `active`.

## Update 2026-11-16: builds are being restored for paid workspaces; Bitrise contacts customers with identified impact directly; still unresolved

The incident page was re-read on 2026-11-16 at about 15:30 UTC. Its newest update is dated 2026-11-16 13:23 UTC. The incident is still unresolved, SEV-1, All Users.

- Builds (CI) and BuildHub are "gradually getting restored", and "workspaces with a paid subscription can start builds". The 12:45 UTC update adds Release Management and CodePush.
- "The investigation is ongoing. Customers with identified impact are contacted directly." The sentence first appears in the 2026-11-16 08:14 UTC update, found by searching the page text in code. It is the first statement on the page that some customers have identified impact. The page gives no count and does not say what the impact is.
- Bitrise says it enabled a "Protected Secret Masked Review" feature, first mentioned in the 2026-11-15 17:35 UTC update, to help users find the secrets to rotate, under Workflow Editor, Secrets and under Workspace settings, Shared resources.
- The recommendation is unchanged: rotate all secrets, access tokens and certificates stored in Bitrise.

The page still gives no cause and no post-mortem date. `status` stays `active`. If Bitrise has not contacted you, that is not a statement that you are unaffected. Rotate anyway.

## Sources

Single source: the vendor.

- [Bitrise status](https://status.bitrise.io), fetched 2026-11-14: the "Security Incident" entry (incident id 7055z4g9nbck), seventeen updates from 2026-11-13 20:44 UTC to 2026-11-14 14:34 UTC, SEV-1, All Users, unresolved.
- Hacker News item 50489750, seen 2026-11-14 through the Algolia search feed: the status page submitted on 2026-11-13, 4 points. The item page was not opened.
- Not covered: the incident's own URL, Bitrise's blog and trust centre, and any customer email.
- [Bitrise status](https://status.bitrise.io), re-read 2026-11-15: 18 further updates from 2026-11-14 16:05 UTC to 2026-11-15 14:23 UTC, the incident still unresolved. The count of 18 was made in code from the page's timestamps. Only the 20:35 sentence is quoted.
- [Bitrise status: Security Incident](https://status.bitrise.io/incidents/7055z4g9nbck), re-read 2026-11-16 with `curl`: the 13:23 UTC and 12:45 UTC updates quoted above.
