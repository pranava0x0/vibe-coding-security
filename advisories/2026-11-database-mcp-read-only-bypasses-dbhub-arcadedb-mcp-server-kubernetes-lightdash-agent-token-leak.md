---
id: 2026-11-database-mcp-read-only-bypasses-dbhub-arcadedb-mcp-server-kubernetes-lightdash-agent-token-leak
title: "DBHub, ArcadeDB and mcp-server-kubernetes MCP restrictions bypassed, and Lightdash's AI agent sends a GitLab token to an unverified host; all fixed"
date_disclosed: 2026-11-21
last_updated: 2026-11-23
severity: high
status: patched
ecosystems: [npm, mcp, docker, maven, dbhub, arcadedb, kubernetes, lightdash]
tools_affected: ["`@bytebase/dbhub` (npm) below 1.7.0", "`mcp-server-kubernetes` (npm) below 4.2.0", "ArcadeDB below 26.11.1", "Lightdash below 3.212.0 with AI writeback and a GitLab installation"]
tags: [mcp, read-only-bypass, sql-injection, argument-injection, authorization-bypass, credential-exposure, ai-agent, gitlab-token, vulncheck, patched]
---

## TL;DR
VulnCheck published seven CVE records on 2026-11-21 and 2026-11-22 for four products. A client limited to read-only SQL in DBHub below 1.7.0 can write and drop data ([CVE-2026-134803](https://cveawg.mitre.org/api/cve/CVE-2026-134803)). ArcadeDB 26.3.1 to below 26.11.1 has two read-only bypasses in its MCP mode, one limited to native-image builds and one to server administrators. The `mcp-server-kubernetes` package below 4.2.0 lets a remote MCP client read files on the server host. Lightdash below 3.212.0 sends the organization's GitLab token to a host a project developer chooses.

## What happened

| Product | CVE | CNA score (4.0 / 3.1) | What the record says | Fixed | Fix on the registry |
|---|---|---|---|---|---|
| DBHub | [CVE-2026-134803](https://cveawg.mitre.org/api/cve/CVE-2026-134803) | 7.2 / 8.1 | An MCP client restricted to read-only `execute_sql` hides stacked statements inside strings with backslash-escaped quotes and runs write and DDL statements on MySQL, MariaDB or PostgreSQL. | 1.7.0 | `@bytebase/dbhub` 1.7.0, npm, 2026-11-16 |
| mcp-server-kubernetes | [CVE-2026-134817](https://cveawg.mitre.org/api/cve/CVE-2026-134817) | 7.1 / 7.1 | A client on the SSE or Streamable HTTP transport passes dash-prefixed values as positional arguments to tools such as `exec_in_pod`, `kubectl_patch` and `kubectl_logs`. `kubectl` then reads files from the server host. | 4.2.0 | npm, 2026-10-26 |
| ArcadeDB | [CVE-2026-134337](https://cveawg.mitre.org/api/cve/CVE-2026-134337) | 8.7 / 8.8 | Native-image builds 26.8.1 and later: an authenticated client nests a write inside `SELECT` and it persists through the query endpoint, MCP read-only mode and follower routing. | 26.11.1 | Maven Central and Docker Hub, 2026-11-04 |
| ArcadeDB | [CVE-2026-134324](https://cveawg.mitre.org/api/cve/CVE-2026-134324) | 6.9 / 4.9 | 26.3.1 and later: a server administrator commits writes through the MCP read-only query tool with a Gremlin script. | 26.11.1 | same |
| ArcadeDB | [CVE-2026-134327](https://cveawg.mitre.org/api/cve/CVE-2026-134327) | 7.1 / 6.5 | An authenticated user reads schema definitions of types an ACL denies, through the PostgreSQL wire catalog, GraphQL introspection or MCP `get_schema`. | 26.11.1 | same |
| ArcadeDB | [CVE-2026-134329](https://cveawg.mitre.org/api/cve/CVE-2026-134329) | 7.1 / 4.3 | 26.2.1 and later: MCP tools return different errors for "not authorized" and "does not exist", so a caller can confirm by probing which database names exist. | 26.11.1 | same |
| Lightdash | [CVE-2026-134827](https://cveawg.mitre.org/api/cve/CVE-2026-134827) | 8.3 / 7.7 | A project developer sets the dbt connection `host_domain` to their own server. When the AI agent reads the repository, Lightdash sends the organization GitLab app token there. | 3.212.0 | Docker Hub tag `3.212.0`, 2026-11-11 |

VulnCheck is the CNA for all seven. The ArcadeDB records reference eight vendor advisories on the `ArcadeData/arcadedb` repository. The DBHub, mcp-server-kubernetes and Lightdash records reference a pull request, a commit and a release tag, and no vendor advisory. None of those pages was opened for this file.

Every fix was on its registry before the records appeared. Newer versions exist for three of the four. On 2026-11-23 npm listed `@bytebase/dbhub` 2.1.0 and `mcp-server-kubernetes` 4.2.3, Maven Central listed ArcadeDB 26.11.1 as its release, and Docker Hub listed Lightdash 3.371.2.

DBHub had an earlier read-only bypass, tracked in [2026-08-agent-framework-mcp-cve-batch.md](2026-08-agent-framework-mcp-cve-batch.md). CVE-2026-134803 is a different record with a different fix version.

## Am I affected?

```bash
npm ls -g @bytebase/dbhub mcp-server-kubernetes 2>/dev/null
grep -rn '"@bytebase/dbhub\|"mcp-server-kubernetes' ~/.cursor/mcp.json ~/.claude.json .mcp.json 2>/dev/null
```

- DBHub: below 1.7.0, and you rely on read-only mode to stop an agent changing data. An `npx` entry with no version pin runs the newest release.
- mcp-server-kubernetes: below 4.2.0, and it listens on SSE or Streamable HTTP. The record does not name the stdio transport.
- ArcadeDB: the server version is below 26.11.1.
- Lightdash: self-hosted below 3.212.0 with a GitLab installation and AI writeback in use.

## If you are affected

1. Upgrade: DBHub 1.7.0 or later, mcp-server-kubernetes 4.2.0 or later, ArcadeDB 26.11.1, Lightdash 3.212.0 or later.
2. DBHub and ArcadeDB: give the agent a database account that has only `SELECT`. The server's read-only mode is then a second control, not the only one.
3. Lightdash: if a project's `host_domain` pointed anywhere other than your GitLab host, rotate the GitLab app token. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. mcp-server-kubernetes: if untrusted clients could reach the HTTP transport, rotate the kubeconfig credentials on that host.

Steps 2 to 4 are this file's advice. The records give no workaround.

## Prevention

- Enforce read-only access in the database's own grants. See [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).
- Bind MCP servers to localhost or put authentication in front of them.

## Sources

Single source for each product: the CNA record.

- CNA records fetched from `cveawg.mitre.org` on 2026-11-23: [CVE-2026-134803](https://cveawg.mitre.org/api/cve/CVE-2026-134803), [CVE-2026-134817](https://cveawg.mitre.org/api/cve/CVE-2026-134817), [CVE-2026-134827](https://cveawg.mitre.org/api/cve/CVE-2026-134827), [CVE-2026-134324](https://cveawg.mitre.org/api/cve/CVE-2026-134324), [CVE-2026-134327](https://cveawg.mitre.org/api/cve/CVE-2026-134327), [CVE-2026-134329](https://cveawg.mitre.org/api/cve/CVE-2026-134329), [CVE-2026-134337](https://cveawg.mitre.org/api/cve/CVE-2026-134337): descriptions, ranges, both scores, references, publication dates.
- [GitHub Advisory Database, `mcp` listing](https://github.com/advisories?query=mcp+sort%3Apublished-desc), fetched 2026-11-23: the rows.
- `npm view @bytebase/dbhub time repository.url` and `npm view mcp-server-kubernetes time repository.url`, run 2026-11-23.
- Maven Central metadata for `com.arcadedb:arcadedb-server` and the Docker Hub tag API for `arcadedata/arcadedb` and `lightdash/lightdash`, read 2026-11-23.
- Not covered: the vendor advisories, pull requests and release notes the records reference, and VulnCheck's own pages.
