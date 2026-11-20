---
id: 2026-11-mcp-server-advisories-november-19-20-jupyter-todoist-k8s-sqlite-obsidian-codewhale-fixed-earlier
title: "Twelve MCP server and coding-agent advisories published 2026-11-19 and 11-20: Jupyter MCP Server, Todoist MCP, k8s-mcp-server and seven more; fixes shipped June to October"
date_disclosed: 2026-11-19
last_updated: 2026-11-20
severity: high
status: patched
ecosystems: [mcp, npm, pypi, go, jupyter, kubernetes, coding-agents]
tools_affected: ["jupyter-mcp-server before 1.0.3", "@doist/todoist-mcp before 10.3.3", "k8s-mcp-server before 1.1.0", "StacklokLabs sqlite-mcp before 0.1.2", "obsidian-sync-mcp before 0.5.7", "Gortex before 0.55.0", "axon-mcp 0.1.0 (no fixed release)", "@apireno/domshell before 2.0.8", "safari-mcp before 2.22.15", "codewhale 0.8.67 and earlier"]
tags: [mcp, dns-rebinding, missing-authentication, sql-injection, path-traversal, backfill, ghsa, coding-agents]
---

## TL;DR

The [GitHub Advisory Database](https://github.com/advisories?query=mcp+sort%3Apublished-desc) published twelve advisories for ten MCP servers and coding agents on 2026-11-19 and 2026-11-20. Nine of the ten products shipped the fix between 2026-06-24 and 2026-10-19, so a current install is already fixed. `axon-mcp` has no fixed release on PyPI. Two are rated critical: a website can drive a local Jupyter MCP Server or Todoist MCP server in HTTP mode. Check installed versions against the table.

## What happened

The database rows are dated 2026-11-19 and 2026-11-20. The vendor advisory pages were not opened, so the vendor publication dates are not known. Fix dates come from the registries, read 2026-11-20.

| Product (package) | Id | Rating | Affected | Fixed, registry date | Condition in the record |
|---|---|---|---|---|---|
| Jupyter MCP Server (PyPI `jupyter-mcp-server`) | [CVE-2026-77359](https://cveawg.mitre.org/api/cve/CVE-2026-77359) | 9.3, GitHub CNA, CVSS 4.0 | before 1.0.3 | 1.0.3, 2026-07-11 | standalone `streamable-http` mode. A website the user visits can repoint the server's Jupyter backend through DNS rebinding |
| Jupyter MCP Server | [CVE-2026-77318](https://api.osv.dev/v1/vulns/GHSA-24pw-rf5p-mgp7) | High | before 1.0.3 | 1.0.3, 2026-07-11 | same mode. The management routes do not check `MCP_TOKEN` |
| Todoist MCP (npm `@doist/todoist-mcp`) | [CVE-2026-76807](https://cveawg.mitre.org/api/cve/CVE-2026-76807) | 9.3, GitHub CNA, CVSS 3.1 | before 10.3.3 | 10.3.3, 2026-06-24 | the optional `todoist-mcp-http` server. A website can call tools with the server's Todoist API key |
| k8s-mcp-server (Go `github.com/reza-gholizade/k8s-mcp-server`) | [CVE-2026-130007](https://api.osv.dev/v1/vulns/GHSA-m932-63jc-4jqq) | High | before 1.1.0 | 1.1.0, 2026-08-31 | default SSE transport has no authentication. Anyone who reaches the port runs Kubernetes tools |
| sqlite-mcp (Go `github.com/StacklokLabs/sqlite-mcp`) | [CVE-2026-130008](https://api.osv.dev/v1/vulns/GHSA-q433-mp6c-8v4f) | High | before 0.1.2 | 0.1.2, 2026-10-19 | read-only mode, the default, can be bypassed to write |
| obsidian-sync-mcp (npm) | [CVE-2026-77283](https://api.osv.dev/v1/vulns/GHSA-mx6p-3fg7-v6pj) | High | before 0.5.7 | 0.5.7, 2026-07-10 | no-auth mode, run without `MCP_AUTH_TOKEN`. A website can reach the vault |
| Gortex (Go `github.com/zzet/gortex`) | [CVE-2026-62964](https://api.osv.dev/v1/vulns/GHSA-w42c-h7hr-f67p) | High | before 0.55.0 | 0.55.0, 2026-06-27 | write tools accept paths outside the indexed repository |
| Axon (PyPI `axon-mcp`) | [CVE-2026-76818](https://api.osv.dev/v1/vulns/GHSA-r7wg-f7r2-8wf7) | High | 0.1.0 | none on PyPI | downloads and runs a helper binary with no integrity check |
| DOMShell (npm `@apireno/domshell`) | [CVE-2026-75518](https://api.osv.dev/v1/vulns/GHSA-vg83-hcp4-5qcc) | Moderate | before 2.0.8 | 2.0.8, 2026-07-08 | a read-tier tool can change page state without `--allow-write` |
| Safari MCP (npm `safari-mcp`) | [GHSA-4rj4-rcrq-gr92](https://api.osv.dev/v1/vulns/GHSA-4rj4-rcrq-gr92), no CVE | Moderate | before 2.22.15 | 2.22.15, 2026-10-10 | a tool argument can run JavaScript in the page |
| CodeWhale (npm `codewhale`, crates.io `codewhale-tui`) | [CVE-2026-83816](https://api.osv.dev/v1/vulns/GHSA-3mgh-93r5-r7jf) | High | 0.8.67 and earlier | 0.9.0, npm 2026-07-16 | the shell tool auto-approves some search commands that can run programs |
| CodeWhale | [CVE-2026-83817](https://api.osv.dev/v1/vulns/GHSA-8hp3-xxrg-v9c8) | High | 0.8.67 and earlier | 0.9.0, npm 2026-07-16 | automations default to `auto_approve` true |

Notes on single rows:

- **Axon.** PyPI lists one version, 0.1.0, uploaded 2026-06-16. The record marks it last affected and references three repository commits. No release carries them as of 2026-11-20.
- **Jupyter MCP Server.** PyPI's newest version is 2.2.6.
- **Newest versions when read:** `@doist/todoist-mcp` 14.0.5, `obsidian-sync-mcp` 0.12.1, `@apireno/domshell` 2.0.11, `safari-mcp` 2.24.1, `codewhale` 0.10.2, Gortex v0.64.11, k8s-mcp-server v1.1.0, sqlite-mcp v0.1.2.
- The crates.io version of `codewhale-tui` was not checked.

This file rates the batch `high`. Both critical scores apply to an optional HTTP mode, and both fixes shipped more than four months before the database rows.

Earlier CodeWhale advisories are in [the August agent-framework batch](2026-08-agent-framework-mcp-cve-batch.md).

## Am I affected?

```bash
pip show jupyter-mcp-server axon-mcp 2>/dev/null | grep -E '^(Name|Version)'
npm ls -g @doist/todoist-mcp obsidian-sync-mcp @apireno/domshell safari-mcp codewhale
```

- Compare each version with the table.
- Go servers: check the version of the binary or the image tag you deployed.
- Check your MCP client configuration for these servers started over HTTP or SSE instead of stdio.

## If you are affected

1. Upgrade to the fixed version or newer and restart the server.
2. Remove `axon-mcp` until a fixed release exists.
3. If k8s-mcp-server ran on a reachable port without authentication, review cluster audit logs and rotate the credentials it used. See [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
4. If a Jupyter, Todoist or Obsidian server ran in HTTP mode on an old version, review recent changes to notebooks, tasks or notes.

## Prevention

- Run local MCP servers over stdio. Use HTTP only with a token and Host and Origin checks.
- Pin MCP servers and update them on a schedule. See [MCP hygiene](../prevention/mcp-hygiene.md).

## Sources

- [GitHub Advisory Database, `mcp` listing by publication](https://github.com/advisories?query=mcp+sort%3Apublished-desc) and [`agent` listing](https://github.com/advisories?query=agent+sort%3Apublished-desc), read 2026-11-20: the rows and their dates.
- OSV copies of the twelve advisories, linked per row, read 2026-11-20: ranges, fixed versions, descriptions.
- [CVE-2026-77359](https://cveawg.mitre.org/api/cve/CVE-2026-77359) and [CVE-2026-76807](https://cveawg.mitre.org/api/cve/CVE-2026-76807), CVE Services records: the two 9.3 scores and their conditions.
- Registry reads on 2026-11-20: `npm view <package> time`, `pypi.org/pypi/<package>/<version>/json`, `proxy.golang.org/<module>/@latest`.
- Not opened: the ten vendor advisory pages, crates.io.
