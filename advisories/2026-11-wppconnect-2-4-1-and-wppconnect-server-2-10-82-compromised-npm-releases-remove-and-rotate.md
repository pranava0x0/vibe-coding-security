---
id: 2026-11-wppconnect-2-4-1-and-wppconnect-server-2-10-82-compromised-npm-releases-remove-and-rotate
title: "Compromised @wppconnect-team/wppconnect 2.4.1 and @wppconnect/server 2.10.82: pin 2.4.0 and 2.10.81, rotate secrets and WhatsApp sessions"
kind: malicious-artifact
date_disclosed: 2026-11-16
last_updated: 2026-11-16
severity: high
status: contained
ecosystems: [npm, whatsapp, nodejs]
tools_affected: ["@wppconnect-team/wppconnect 2.4.1 (npm)", "@wppconnect/server 2.10.82 (npm)", "WhatsApp bots and automations built on WPPConnect", "CI jobs and developer machines that installed either version on 2026-11-15 or 2026-11-16"]
tags: [supply-chain, malicious-package, compromised-release, npm, whatsapp, session-tokens, credential-rotation]
---

## TL;DR
Remove `@wppconnect-team/wppconnect` 2.4.1 and `@wppconnect/server` 2.10.82 and pin 2.4.0 and 2.10.81. If either version ran, rotate every secret in that environment and re-link the WhatsApp sessions it held.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (checked 2026-11-16) | Record |
|---|---|---|---|---|---|
| npm | `@wppconnect-team/wppconnect` | 2.4.1 (published 2026-11-15 23:31 UTC) | pin 2.4.0 (2026-11-13) | still resolvable by exact version, marked deprecated with a security-incident notice, `latest` is 2.4.0 | no OSV record returned for the package |
| npm | `@wppconnect/server` | 2.10.82 (published 2026-11-16 03:09 UTC) | pin 2.10.81 (2026-11-13) | still resolvable by exact version, marked deprecated with a security-incident notice, `latest` is 2.10.81 | OSV not queried for this name |

Publish times and dist-tags are from the npm registry. SafeDep gives weekly downloads for 2026-11-09 to 11-15 of 7,498 for the library and 1,527 for the server, and 155 downloads of 2.4.1. SafeDep says the deprecation was applied at about 08:00 on 2026-11-16 and that the tagged GitHub history does not match the published npm releases.

## Am I affected?

- `npm ls @wppconnect-team/wppconnect @wppconnect/server` shows 2.4.1 or 2.10.82, directly or through another package.
- Your lockfile names either version. Search `package-lock.json`, `yarn.lock` or `pnpm-lock.yaml` for `@wppconnect-team/wppconnect` and `@wppconnect/server` and read the resolved version.
- An install or a CI run resolved `latest` for either package between the publish times above and about 08:00 on 2026-11-16.
- The system temp directory holds a file named `.wpp-support-diag` or `.wpp-diag`. SafeDep lists these as signs that the release ran.
- The project directory holds a `tokens/` or `wppconnect_tokens/` directory. These hold the WhatsApp sessions to treat as exposed.

## If you are affected

1. Pin `@wppconnect-team/wppconnect` to 2.4.0 and `@wppconnect/server` to 2.10.81, reinstall from a clean lockfile, and rebuild any image that contains the bad version.
2. Rotate every environment variable the process could read: API keys, database connection strings and cloud credentials.
3. Rotate secrets held in `.env` files and configuration files in the project directory.
4. Treat every linked WhatsApp session as compromised. Log the devices out from the WhatsApp account and link again after the rotation.
5. Follow [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Pin exact versions and install with `npm ci`. Do not let CI resolve `latest`.
- Set a minimum release age in your package manager so a version a few hours old is not installed.
- See [prevention/npm-hardening.md](../prevention/npm-hardening.md) and [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).

## Sources

One research firm, plus the registry's own state.

- [SafeDep: Malicious wppconnect Release Steals Secrets and WhatsApp Sessions](https://safedep.io/blog/wppconnect-npm-whatsapp-session-stealer.md), 2026-11-16, fetched 2026-11-16 for versions, dates, file names, credential categories and remediation only.
- npm registry metadata for `@wppconnect-team/wppconnect` and `@wppconnect/server`, read 2026-11-16: publish times, dist-tags, the deprecation flag on 2.4.1 and 2.10.82.
- OSV query for `@wppconnect-team/wppconnect`, 2026-11-16: no records.
- Not found: a maintainer statement or repository issue. Not opened: SafeDep's indicator list.
