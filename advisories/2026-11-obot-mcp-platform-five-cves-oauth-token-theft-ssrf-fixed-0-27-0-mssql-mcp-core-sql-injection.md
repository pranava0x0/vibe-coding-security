---
id: 2026-11-obot-mcp-platform-five-cves-oauth-token-theft-ssrf-fixed-0-27-0-mssql-mcp-core-sql-injection
title: "Obot before 0.27.0: five CVEs, including access token theft by a remote MCP server (CVE-2026-130766). Also mssql-mcp-core SQL injection"
date_disclosed: 2026-10-31
last_updated: 2026-11-19
severity: high
status: patched
ecosystems: [mcp, self-hosted, docker, go, npm]
tools_affected: ["Obot before 0.27.0", "@connorbritain/mssql-mcp-core and mssql-mcp-server before 0.6.0", "@connorbritain/mssql-mcp-reader and mssql-mcp-writer before 0.5.0"]
tags: [cve, mcp, obot, oauth, token-theft, ssrf, command-injection, sql-injection, vulncheck]
---

## TL;DR
[CVE-2026-130766](https://cveawg.mitre.org/api/cve/CVE-2026-130766) says Obot 0.26.0 lets a malicious remote MCP server obtain a user's access token for a different service. Four more records cover SSRF, command injection and an open redirect in older versions. All are fixed in 0.27.0. The [vendor advisories](https://github.com/obot-platform/obot/security/advisories) are dated 2026-10-31 and the CVE ids arrived on 2026-11-18. A separate record covers SQL injection in the `mssql-mcp` packages.

## Obot

Obot is a platform for running and connecting to MCP servers. VulnCheck published five records on 2026-11-18. Each references a vendor advisory that the vendor's tab dates 2026-10-31. Scores are VulnCheck's.

| CVE | Vendor advisory | What the record says | Affected | CVSS 4.0 / 3.1 |
|---|---|---|---|---|
| [CVE-2026-130766](https://cveawg.mitre.org/api/cve/CVE-2026-130766) | GHSA-x3hf-v55x-jcp6 | a remote MCP server names a different service in its resource metadata, and Obot fetches the victim's token for that service and forwards it | 0.26.0 before 0.27.0 | 8.8 / 8.0 |
| [CVE-2026-130764](https://cveawg.mitre.org/api/cve/CVE-2026-130764) | GHSA-57qx-69p6-3w3g | a Power User points the OAuth token endpoint at internal hosts or cloud metadata services and reads error bodies | 0.8.0 before 0.27.0 | 8.3 / 7.6 |
| [CVE-2026-130767](https://cveawg.mitre.org/api/cve/CVE-2026-130767) | GHSA-2mfp-9vv3-q737 | an authenticated user runs shell commands through file-type MCP server configuration values | 0.9.0 before 0.27.0 | 5.3 / 6.4 |
| [CVE-2026-130768](https://cveawg.mitre.org/api/cve/CVE-2026-130768) | GHSA-r3m3-5rmh-h3fm | a Power User bypasses outbound address checks to probe internal services | 0.14.0 before 0.27.0 | 5.1 / 4.1 |
| [CVE-2026-130765](https://cveawg.mitre.org/api/cve/CVE-2026-130765) | GHSA-cv8w-jqg2-jg55 | an unauthenticated open redirect on sign-in and sign-out links | before 0.27.0 | 5.3 / 4.7 |

Notes on the table:

- The vendor tab rates the first two High and the other three Moderate.
- The token theft record has `UI:P` in its vector. A user has to connect to the attacker's MCP server.
- The 0.27.0 release notes, as read through a truncated page, include "fix: reject protected resource metadata for a different origin".
- The [releases page](https://github.com/obot-platform/obot/releases) showed v0.28.1 as latest on 2026-11-19. The 0.27.0 release date was not read.

The tab's first page holds five more advisories from 2026-09-17 to 2026-10-07 that have no file here and no CVE in the sources read:

- GHSA-6fwv-3h4c-37j9, High, an authorization bypass on `/mcp-connect-composite/`.
- GHSA-2qcm-3gv6-2mfc, High, "CLI login flow could be used to steal another user's API key".
- GHSA-929v-v9hq-5xhr, GHSA-xhpw-65qw-wj6m and GHSA-q5wf-87f5-cxgq, Moderate.

Their fixed versions were not read. Page 2 of the tab was not opened.

## mssql-mcp-core

[CVE-2026-63129](https://cveawg.mitre.org/api/cve/CVE-2026-63129) was published by GitHub's CNA on 2026-11-18 and scores 8.8 (CVSS 3.1, `PR:L`). The record says several write tools build T-SQL from caller-supplied table names, columns and a free-form `whereClause`. It also says row-count and preview queries run before `confirmUpdate` or `confirmDelete` is checked.

| Package | Fixed in, per the record | On npm | Newest on npm, read 2026-11-19 |
|---|---|---|---|
| `@connorbritain/mssql-mcp-core` | 0.6.0 | 2026-06-29 | 0.7.0 |
| `@connorbritain/mssql-mcp-server` | 0.6.0 | 2026-06-29 | 0.7.0 |
| `@connorbritain/mssql-mcp-reader` | 0.5.0 | 2026-06-29 | 0.6.1 |
| `@connorbritain/mssql-mcp-writer` | 0.5.0 | 2026-06-29 | 0.6.0 |

The fixed versions were on npm on 2026-06-29, before the record's 2026-11-18 date. The record says malicious arguments bypass the confirmation step.

## Am I affected?

```bash
npm ls @connorbritain/mssql-mcp-core @connorbritain/mssql-mcp-server @connorbritain/mssql-mcp-reader @connorbritain/mssql-mcp-writer 2>/dev/null
```

- **Obot.** Check the version of the running deployment. Anything before 0.27.0 is affected by at least one id. Only 0.26.x is affected by the token theft bug.
- **mssql-mcp.** Core or server below 0.6.0, reader or writer below 0.5.0.

## If you are affected

- **Obot.** Upgrade to the current release. Review the remote MCP servers users have added, and revoke OAuth grants made through any server you do not recognise.
- **mssql-mcp.** Upgrade to the newest versions. Give the server a database login that can only do what the tools should do.
- See [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md).

## Prevention

- Limit who can add remote MCP servers to a shared platform. Three of the five Obot records need a Power User or an authenticated user.
- A database MCP server's safety comes from the database login's permissions, not from tool-level confirmation. See [MCP hygiene](../prevention/mcp-hygiene.md).

## Sources

- [CVE-2026-130764](https://cveawg.mitre.org/api/cve/CVE-2026-130764), [CVE-2026-130765](https://cveawg.mitre.org/api/cve/CVE-2026-130765), [CVE-2026-130766](https://cveawg.mitre.org/api/cve/CVE-2026-130766), [CVE-2026-130767](https://cveawg.mitre.org/api/cve/CVE-2026-130767), [CVE-2026-130768](https://cveawg.mitre.org/api/cve/CVE-2026-130768): VulnCheck CNA records, read 2026-11-19.
- [obot-platform/obot security advisories](https://github.com/obot-platform/obot/security/advisories), page 1, read 2026-11-19: titles, ratings, dates.
- [obot-platform/obot releases](https://github.com/obot-platform/obot/releases), read 2026-11-19: v0.28.1 latest, the quoted 0.27.0 line.
- [CVE-2026-63129](https://cveawg.mitre.org/api/cve/CVE-2026-63129): GitHub CNA record, read 2026-11-19. npm `time` for the four packages, read 2026-11-19.
- [GitHub Advisory Database, `mcp` listing](https://github.com/advisories?query=mcp+sort%3Apublished-desc), read 2026-11-19.
- Not opened: the five Obot advisory pages, the mssql-mcp-core advisory page and its fix commits.
