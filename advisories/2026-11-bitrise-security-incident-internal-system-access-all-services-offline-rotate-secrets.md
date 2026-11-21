---
id: 2026-11-bitrise-security-incident-internal-system-access-all-services-offline-rotate-secrets
title: "Bitrise security incident: unauthorized access to an internal system, all services taken offline on 2026-11-13; rotate secrets, access tokens and certificates"
date_disclosed: 2026-11-13
last_updated: 2026-11-21
severity: high
status: contained
ecosystems: [bitrise, ci-cd, mobile, saas, github, code-signing]
tools_affected: ["Bitrise CI/CD (app.bitrise.io), all users", "Git provider credentials and access tokens connected to Bitrise", "secrets and environment variables stored in Bitrise apps and workspaces", "code-signing certificates and provisioning profiles uploaded to Bitrise", "mobile apps built by coding agents and shipped through Bitrise pipelines"]
tags: [breach, vendor-incident, bitrise, ci-cd, mobile, code-signing, secrets, credential-rotation, outage, investigation-ongoing]
---

## TL;DR
Bitrise, the mobile CI/CD service, detected an intruder on 2026-11-13 at 16:32 UTC and took every service offline at 20:34 UTC. Its [preliminary review](https://bitrise.io/blog/post/the-bitrise-security-incident-preliminary-review-and-recommended-steps) of 2026-11-18 says the attacker signed in to an internal test bot account that had no two-factor authentication. Files in 15 customer workspaces were accessed, and Bitrise says it contacted all 15. Bitrise says it has no indication that its customer secret store was accessed. It still suggests rotating the secrets, tokens and certificates stored in Bitrise.

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

## Update 2026-11-17: Bitrise closes the incident, says the platform is safe to use, and keeps the rotation advice; forensic investigation continues

Bitrise marked the [status incident](https://status.bitrise.io/incidents/7055z4g9nbck) resolved on 2026-11-17 at 09:53 UTC. The closing update says "The immediate security risks have been addressed, and we consider Bitrise safe to use." The page held 59 updates when read, counted in code from the page's JSON.

- Bitrise says it rotated all internal credentials, secrets and keys, and "revoked all potentially affected access tokens and sessions".
- It says it rebuilt its build infrastructure "from scratch across all data centers" and reviewed every service before bringing it back.
- It still recommends "rotating any secrets and credentials connected to Bitrise" and points to the Protected Secret Masked Review feature.
- It says "We are now in the state of forensic investigation" and that further updates will appear in a follow-up status entry.

The closing update does not say what the intruder accessed or how. `status` moves from `active` to `contained` on the vendor's "safe to use" sentence. The resolved state of the status page is not the end of the investigation.

## Update 2026-11-19: preliminary review names the entry point and says files in 15 customer workspaces were accessed

Bitrise published a [preliminary review](https://bitrise.io/blog/post/the-bitrise-security-incident-preliminary-review-and-recommended-steps) on 2026-11-18, signed by its VP of Engineering and Infrastructure.

- **Entry point.** An internal testing bot account in a workspace used to build and test build steps. The review says the attacker supplied "the valid username and password combination" and that the account "lacked two-factor authentication". How the credentials were obtained "remains under investigation".
- **Bitrise's own data.** The review says most of what was accessed was internal credentials, some of its repositories, and operational records such as infrastructure configuration and build machine logs.
- **Customer data.** "Files in 15 customer workspaces were accessed without authorization." The review lists one code-signing certificate file whose password was not accessed, one provisioning profile, and 13 diagnostic build logs from May 2026. One log held a credential and another an email address.
- **Secrets.** The review says "we have no indication of customer secret store access, nor attempts to access customer secret store". It suggests rotation "out of an abundance of caution".
- **GitHub.** On 2026-11-13 Bitrise replaced the private key of its GitHub App and revoked all user authorizations for it. It also revoked every token issued by its GitHub OAuth app. GitHub then removed the SSH deploy keys Bitrise had added to repositories.
- **Timeline.** Scanning on 2026-10-25 to 10-27. A new account ran builds that probed the build environment on 2026-11-12. Detection at 16:32 UTC on 2026-11-13, shutdown started at 19:26 UTC, platform off at 20:34 UTC.

The review says Bitrise is waiting for audit logs from GitHub before it closes the investigation and writes a final report. `status` stays `contained`.

What to do, from the review:

1. Rotate secrets, tokens and certificates stored in Bitrise, and the Git credentials connected to it.
2. Authorize the Bitrise GitHub App again, or reconnect the GitHub OAuth connection, whichever the project uses.
3. Re-add the SSH key if a build cannot clone the repository.

## Update 2026-11-21: full incident report counts the files accessed in the 15 workspaces

Bitrise published its [incident report](https://bitrise.io/artex-incident-report) on 2026-11-19. The page read on 2026-11-21 is version 1.4.

- Activity ran from 2026-10-25 to 2026-11-18. The sign-in to the dormant internal test bot account was on 2026-11-13 at 11:46:48 UTC.
- "Files in 15 customer workspaces were accessed without authorization." The files were 1 code-signing certificate file, 1 provisioning profile and 13 diagnostic build logs from May 2026.
- Bitrise says the attacker could not access the password for the certificate file. It says one log contained a credential and another an email address.
- "Our logs show no access, and no attempted access, to the store that holds customer secrets."
- The attacker downloaded 236 production Terraform state files. Bitrise says it treated every secret in them as exposed and rotated it.
- The attacker returned on 2026-11-18. Bitrise counts 19 cloud requests, all denied, and 9 sign-in attempts, all refused.
- Bitrise says some of its repositories were copied and that it found no change to its code or releases.
- The report says how several credentials were obtained, an infrastructure key among them, "is not established".

Bitrise's advice is unchanged: rotate the secrets, tokens and certificates stored in Bitrise and reconnect GitHub. The status stays `contained`.

## Sources

Single source: the vendor.

- [Bitrise: security incident report, October to November 2026](https://bitrise.io/artex-incident-report): published 2026-11-19, version 1.4 read 2026-11-21. File counts, dates, quoted sentences.
- [Bitrise status](https://status.bitrise.io), fetched 2026-11-14: the "Security Incident" entry (incident id 7055z4g9nbck), seventeen updates from 2026-11-13 20:44 UTC to 2026-11-14 14:34 UTC, SEV-1, All Users, unresolved.
- Hacker News item 50489750, seen 2026-11-14 through the Algolia search feed: the status page submitted on 2026-11-13, 4 points. The item page was not opened.
- Not covered: the incident's own URL, Bitrise's blog and trust centre, and any customer email.
- [Bitrise status](https://status.bitrise.io), re-read 2026-11-15: 18 further updates from 2026-11-14 16:05 UTC to 2026-11-15 14:23 UTC, the incident still unresolved. The count of 18 was made in code from the page's timestamps. Only the 20:35 sentence is quoted.
- [Bitrise status: Security Incident](https://status.bitrise.io/incidents/7055z4g9nbck), re-read 2026-11-16 with `curl`: the 13:23 UTC and 12:45 UTC updates quoted above.
- [Bitrise status: Security Incident](https://status.bitrise.io/incidents/7055z4g9nbck), re-read 2026-11-17 through the page's JSON: the resolved state, the 09:53 UTC closing update and the count of 59 updates.
- [Bitrise: The Bitrise security incident, preliminary review and recommended steps](https://bitrise.io/blog/post/the-bitrise-security-incident-preliminary-review-and-recommended-steps), 2026-11-18, read 2026-11-19 with `curl`: every quotation and count in the 2026-11-19 update. The technical advisory and indicator files it mentions were not opened.
