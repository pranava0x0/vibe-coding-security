---
id: 2026-10-zeabur-october-security-incident-env-var-store-breach-shutdown-december-31
title: "Zeabur breach: plaintext AWS keys and non-expiring cluster-admin token exposed 3.2 million environment-variable records across 321,810 accounts; platform shuts down December 31"
date_disclosed: 2026-10-19
last_updated: 2026-10-26
severity: critical
status: active
ecosystems: [paas, docker, kubernetes, vibe-platform]
tools_affected: ["Zeabur (all accounts; every service environment variable, zSend keys, API tokens, managed databases, backups in tpe1 and hkg1)"]
tags: [vibe-platform, data-breach, env-vars, secrets-exposure, cluster-admin, plaintext-credentials, config-repo, github-app, paas, shutdown, rotate-everything, n8n, hetzner, digitalocean, gcp]
---

## TL;DR
Zeabur, a deploy-from-GitHub PaaS popular with Next.js and n8n users, said on 2026-10-19 that an attacker used plaintext AWS keys, a non-expiring Kubernetes cluster-admin token and plaintext root passwords found in a private configuration repository to read its production stores between October 14 and 15, undetected for more than sixteen hours. The preliminary report counts 3,218,965 environment-variable records across 321,810 accounts, 566 zSend keys, 11,536 API tokens (all revoked), 865 database services and unknown exposure on 359 Hetzner and 48 DigitalOcean servers; backups in `tpe1` and `hkg1` were taken. Zeabur links the access to the GitHub App private key it leaked in August. On 10-17 it announced it will stop renewals on December 1 and shut down December 31. Every secret ever set in a Zeabur project is compromised; rotate all of it and migrate before December.

## What happened

- **2026-10-14 to 15.** Access to the private config repo, then to the GCP control plane (101 servers with plaintext root passwords) and the environment-variable store; Zeabur's audit-log window for customer review is October 15, 15:05 to 18:54 UTC.
- **2026-10-17.** "Zeabur is shutting down": renewals off December 1, service ends December 31, export tooling promised.
- **2026-10-19.** Preliminary incident post with the counts above, the credential root cause, the list of revoked tokens and the instruction to look for SSH keys named `@zeabur-pentest` on customer servers.
- **Earlier.** The August GitHub App private-key leak is already in [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md); this incident is the consequence it warned about.

**Same week, same pattern.** PingCAP (TiDB Cloud) disclosed on 10-19 that stolen service-account credentials gave an attacker access from September 9 to October 7 to source code, TiDB Cloud account records including SQL-editor text, an encrypted API-key table and billing data, with four vulnerabilities fixed 10-14 and no evidence of TiDB data access. Andromeda disclosed on 10-20 that credentials were accessed from about October 9 in what it called an industry-wide attack, disabled 10-13, keys rotated. Both are logged in the ongoing-exposure file; Zeabur gets its own entry because its exposure is every customer secret and its end-of-life forces a migration.

Why it is here: a vibe-coded app's whole secret set (database URL, Stripe key, OpenAI key, OAuth client secret) lives in the platform's environment-variable store; when the store is read, the app and every third-party account behind it are exposed, and the platform's own post says so.

## Am I affected?

- Any Zeabur account that existed on 2026-10-15. Assume every environment variable, zSend key and API token is in the attacker's hands.
- Managed databases: assume dumped; backups in the two named regions were taken.
- Servers attached through Zeabur's Hetzner or DigitalOcean integrations: check `~/.ssh/authorized_keys` for `@zeabur-pentest` and any key you did not add.

## If you are affected

1. Rotate every secret ever stored as a Zeabur variable, at the issuer: database passwords, cloud keys, Stripe, OpenAI/Anthropic, OAuth client secrets, n8n encryption key, webhook signing secrets. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and [credential hygiene](../prevention/credential-hygiene.md).
2. Pull Zeabur's audit log for the 15:05 to 18:54 UTC window on October 15 and treat any entry you did not make as attacker activity.
3. Remove unknown SSH keys on attached servers; reinstall if root passwords were among the plaintext set.
4. Export data and move before December 1; a platform in wind-down will not patch further.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): short-lived cloud credentials, no plaintext secrets in any repo, scoped tokens per service.
- Keep an inventory of which secrets each platform holds so a breach notice turns into a rotation list the same day.

## Sources
- [Zeabur — October 2026 security incident (preliminary)](https://zeabur.com/blogs/october-2026-security-incident) — fetched 2026-10-26: dates, root cause, every count above, revocations, the audit-log window, the `@zeabur-pentest` key name, the link to the August key leak.
- [Zeabur — Zeabur is shutting down](https://zeabur.com/blogs/zeabur-is-shutting-down) — fetched 2026-10-26: December 1 renewals stop, December 31 shutdown.
- [PingCAP — Security update, October 2026](https://www.pingcap.com/trust-hub/security/security-update-october-2026/) — fetched 2026-10-26: September 9 to October 7 window, what was accessed, fixes 10-14.
- [Andromeda — October 2026 security incident](https://andromeda.ai/security-updates/october-2026-security-incident) — fetched 2026-10-26: start about October 9, disabled 10-13, rotation.
- Related: [ongoing vibe-platform exposure](ongoing-vibe-platform-exposure.md).
