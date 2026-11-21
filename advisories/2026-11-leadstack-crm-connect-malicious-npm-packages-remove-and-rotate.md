---
id: 2026-11-leadstack-crm-connect-malicious-npm-packages-remove-and-rotate
title: "Malicious `@leadstack/crm-connect` npm package and three related packages: remove, rebuild hosts that installed as root, rotate credentials"
kind: malicious-artifact
date_disclosed: 2026-11-19
last_updated: 2026-11-21
severity: high
status: unconfirmed
ecosystems: [npm]
tools_affected: ["Linux servers that ran npm install of @leadstack/crm-connect 1.0.15 to 1.1.1", "projects depending on @zmatdspcrm/trading-connector, @zmatdspcrm/brandnet-connect or brandnet-connect", "CRM integration services and their stored credentials"]
tags: [supply-chain, malicious-package, npm, single-source, agent-misuse]
---

## TL;DR

Remove `@leadstack/crm-connect` and the three related packages below, which [SafeDep](https://safedep.io/blog/malicious-npm-leadstack-crm-connect-hermes-agent-backdoor) reported as malicious on 2026-11-19. Rebuild any host where an affected version was installed as root, and rotate every credential that host or its application could reach.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| npm | `@leadstack/crm-connect` | 1.0.15 through 1.1.1, nine releases per SafeDep | remove; no clean release | 404 (2026-11-21) | none on OSV (2026-11-21) |
| npm | `@zmatdspcrm/trading-connector` | 1.0.0, 1.0.1 | remove | live, published 2026-11-18 (2026-11-21) | none on OSV |
| npm | `@zmatdspcrm/brandnet-connect` | 0.0.0-stage, 1.0.0 | remove | live, published 2026-11-18 (2026-11-21) | none on OSV |
| npm | `brandnet-connect` | 0.0.0-stage, 1.0.0, 1.0.1 | remove | live, published 2026-11-18 (2026-11-21) | none on OSV |

SafeDep names the publisher account `zmaticoo` and gives 2026-11-16 as the first publish date. The registry lists `zmaticoo` as maintainer of the three live packages. The version lists for those three come from the registry `time` field. SafeDep is the only source, so the status is `unconfirmed`.

## Am I affected?

- Search `package.json`, `package-lock.json`, `yarn.lock` and `pnpm-lock.yaml` for the four names: `grep -rnE "leadstack/crm-connect|zmatdspcrm|brandnet-connect" .`
- On Linux hosts, look for the systemd units SafeDep lists: `leadstack-routing.service` and `leadstack-ingest-worker.service`, system-wide and per user.
- Look for the directories SafeDep lists: `~/.leadstack/`, `~/.config/leadstack/` and `~/.local/share/leadstack/bin/`.
- Check whether linger is enabled for any user. SafeDep lists this check.

## If you are affected

1. Where an affected version was installed as root, rebuild the host. SafeDep advises a rebuild over cleaning.
2. Where the install ran as a normal user, treat everything that user could read as exposed, including the application's secrets.
3. Rotate every credential the host or the application environment could reach: CRM API keys, database passwords, cloud keys and tokens in environment files.
4. Remove the packages from manifests and lockfiles and reinstall from a clean lockfile.
5. Follow [if you ran a malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md) and [if you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- Do not run `npm install` as root on a server. Install with scripts disabled where the build allows it. See [npm hardening](../prevention/npm-hardening.md).
- Check a new scoped package's publisher and age before adding it. See the [package vetting checklist](../prevention/package-vetting-checklist.md).

## Sources

- [SafeDep: report on `@leadstack/crm-connect`](https://safedep.io/blog/malicious-npm-leadstack-crm-connect-hermes-agent-backdoor): 2026-11-19, read 2026-11-21. Package names, versions, publisher, unit and directory names, remediation.
- npm registry `time` and `maintainers` fields for the four packages, read 2026-11-21.
- OSV package queries for the four names returned no record on 2026-11-21.
- Found through [Hacker News item 50585975](https://news.ycombinator.com/item?id=50585975), 7 points when read.
- Single source: SafeDep.
