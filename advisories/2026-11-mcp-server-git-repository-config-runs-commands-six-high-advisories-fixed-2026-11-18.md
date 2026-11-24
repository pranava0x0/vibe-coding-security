---
id: 2026-11-mcp-server-git-repository-config-runs-commands-six-high-advisories-fixed-2026-11-18
title: "mcp-server-git: a repository's own Git config runs commands as the server user, six High advisories; fixed in 2026.11.18"
date_disclosed: 2026-11-18
last_updated: 2026-11-24
severity: high
status: patched
ecosystems: [pypi, npm, mcp, git]
tools_affected: ["mcp-server-git (PyPI) below 2026.11.18", "@modelcontextprotocol/server-filesystem (npm) below 2.4.0 and date-style versions 2025.1.14 to 2026.8.31", "@modelcontextprotocol/server-everything (npm) below 2.3.1 and date-style versions 2026.1.14 to 2026.8.31", "mcp-server-fetch (PyPI) 2026.10.10 to below 2026.11.11", "coding agents that open repositories received as archives, CI artifacts, shared folders or copied workspaces"]
tags: [mcp, mcp-server-git, git-config, command-execution, reference-servers, no-cve, patched, path-traversal]
---

## TL;DR

`mcp-server-git` below 2026.11.18 runs programs named in a repository's own Git configuration, per [six High advisories](https://github.com/modelcontextprotocol/servers/security/advisories), none with a CVE, on the Model Context Protocol reference servers repository. The advisories that name a delivery path describe a repository received with its `.git` directory, such as an archive or shared folder. Two say a plain `git clone` does not carry the config. Several paths start from read-only tools such as `git_status` and `git_diff`. Upgrade to 2026.11.18, on PyPI since 2026-11-18.

## What happened

The repository's advisory tab listed 23 advisories published between 2026-10-25 and 2026-11-18 when read on 2026-11-24. Nine name `mcp-server-git`. Six of those are High.

| Advisory | Published | Affected as printed | Patched | What the advisory says |
|---|---|---|---|---|
| [GHSA-6hqx-gqrx-c5r2](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-6hqx-gqrx-c5r2) | 2026-11-11 | below 2026.11.11 | 2026.11.11 | Repository config runs a command during `git_status`, the diff tools, `git_add`, `git_merge` and `git_log`. |
| [GHSA-pm7p-vphh-2cg7](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-pm7p-vphh-2cg7) | 2026-11-18 | below 2026.11.18 | 2026.11.18 | The 2026.11.11 hardening missed a driver with an empty name. The reporter's test ran it through `git_status` and through write tools. |
| [GHSA-87qg-cmw8-jc5m](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-87qg-cmw8-jc5m) | 2026-11-18 | below 2026.11.18 | 2026.11.18 | Repository config names a program that Git runs when a tool needs an object missing from the local store. Observed with `git_show` and the diff tools. |
| [GHSA-8wv7-r664-7594](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-8wv7-r664-7594) | 2026-11-18 | below 2026.11.18 | 2026.11.18 | A submodule's own config runs programs on the diff tools when the parent sets one option, and on `git_checkout` and `git_add`. |
| [GHSA-h2g3-rwxm-xfm3](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-h2g3-rwxm-xfm3) | 2026-11-18 | 2026.11.4 to below 2026.11.18 | 2026.11.18 | A successful `git_merge` with default settings starts Git maintenance, which runs a command from the repository's config. Needs Git 2.42 or later. |
| [GHSA-9vjp-x34c-xg6v](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-9vjp-x34c-xg6v) | 2026-11-18 | 2026.11.4 to below 2026.11.18 | 2026.11.18 | A `git_merge` with `fast_forward_only=false`, which is not the default, runs a command while a conflicting merge is being aborted. |

Five of the pages print CVSS 3.1 7.8, `AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`. GHSA-h2g3-rwxm-xfm3 prints High with no score. All six said "No known CVE" on 2026-11-24.

Five of the six pages name a delivery path for a repository with an attacker-written `.git` directory. GHSA-pm7p-vphh-2cg7 lists an archive, a CI artifact, a shared folder, a vendored tree or a copied workspace. GHSA-h2g3-rwxm-xfm3 names archives only. GHSA-8wv7-r664-7594 names no delivery path. GHSA-6hqx-gqrx-c5r2 and GHSA-pm7p-vphh-2cg7 say a plain `git clone` does not carry `.git/config`. Four pages say the `--repository` option does not prevent the attack. GHSA-pm7p-vphh-2cg7 gives the reason: the repository sits inside the allowed path.

GHSA-pm7p-vphh-2cg7 says the command runs with the server process's privileges and environment, and that `git_status` is usually auto-approved.

### The other advisories

- [GHSA-r2q8-f657-4r56](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-r2q8-f657-4r56), Moderate, 2026-11-18: a crafted index makes `git_diff_unstaged`, `git_diff` and `git_status` return files outside the `--repository` boundary. Fixed in 2026.11.18. The reporter tested on macOS only. The report says a separate root cause was not yet fixed when it was written.
- [CVE-2026-134465](https://cveawg.mitre.org/api/cve/CVE-2026-134465), 5.8 from the Anthropic CNA on 2026-11-23: a nested `.git` file bypasses `--repository`. Affected below 2026.10.28. The record references GHSA-w766-5x43-whvw. The advisory database row uses the id GHSA-7f33-9hc8-6cr8.
- [CVE-2026-134492](https://cveawg.mitre.org/api/cve/CVE-2026-134492), 2.3 from the Anthropic CNA on 2026-11-23: `mcp-server-fetch` 2026.10.10 to below 2026.11.11 treats one IPv6 range as public. The record says practical impact is limited.
- [GHSA-rq2p-q7c4-6g27](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-rq2p-q7c4-6g27), Low: `@modelcontextprotocol/server-filesystem` below 2.4.0, and 2025.1.14 through 2026.8.31, can list entry names outside the allowed directories through a race.
- [GHSA-38j4-j742-j7r3](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-38j4-j742-j7r3), Low: `@modelcontextprotocol/server-everything` below 2.3.1, and 2026.1.14 through 2026.8.31. The reporter did not demonstrate a completed connection.

The remaining rows are Moderate or Low and were read as tab rows only. One of them, GHSA-q74p-4wrc-q7w6 of 2026-11-11, is titled as an incomplete fix for GHSA-w766-5x43-whvw in `mcp-server-git`.

Both npm packages also have date-style versions on the registry, 2025.1.14 through 2026.8.31. They sort above 2.4.0, so a "below 2.4.0" comparison passes them.

## Am I affected?

The commands are this file's. They do not see a server that a launcher downloads at start.

```bash
pip show mcp-server-git mcp-server-fetch 2>/dev/null | grep -iE '^(name|version)'
npm ls -g @modelcontextprotocol/server-filesystem @modelcontextprotocol/server-everything
```

- `mcp-server-git` below 2026.11.18 is affected. Version 2026.11.4 is inside all six ranges and 2026.11.11 is inside five.
- Check the version your MCP client configuration pins or resolves.
- Exposure needs a repository whose `.git` directory someone else wrote. Two advisories say a plain clone does not carry the config. GHSA-8wv7-r664-7594, the submodule advisory, does not say.
- No CVE exists for the six High advisories, so a scanner keyed on CVE ids will not flag them.

## If you are affected

1. Upgrade `mcp-server-git` and `mcp-server-fetch` to 2026.11.18, `@modelcontextprotocol/server-filesystem` to 2.4.0 and `@modelcontextprotocol/server-everything` to 2.3.1. PyPI and npm show all four published on 2026-11-18.
2. Restart the MCP client so it starts the new server.
3. If an agent used an affected version on a repository received as an archive, artifact or shared folder, treat the account that ran the server as exposed. Rotate the credentials it could read. See [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md). This step is this file's advice.
4. If you cannot upgrade, GHSA-87qg-cmw8-jc5m gives workarounds for its path. Set `GIT_NO_LAZY_FETCH=1` in the server's environment. Do not open repositories received as archives or shared folders. Run the server as a user with no credentials that matter. GHSA-9vjp-x34c-xg6v adds one: require approval for `git_merge`.

## Prevention

- Make a fresh clone before pointing an agent at a repository someone sent you. GHSA-9vjp-x34c-xg6v recommends a clone where Git wrote the config.
- Run MCP servers under an account or sandbox that holds no cloud tokens or SSH keys. See [agent sandboxing](../prevention/agent-sandboxing.md) and [MCP hygiene](../prevention/mcp-hygiene.md).
- Do not auto-approve tools on repositories you did not create.

## Sources

Single source: the vendor repository's advisories and its CNA records.

- [modelcontextprotocol/servers security advisories](https://github.com/modelcontextprotocol/servers/security/advisories), pages 1 to 3, fetched 2026-11-24: id, severity and date for every row. Counts were made in code from the saved rows.
- The nine advisory pages linked above, fetched 2026-11-24 through a summarizing fetch. Paraphrased, not quoted.
- [CVE-2026-134465](https://cveawg.mitre.org/api/cve/CVE-2026-134465) and [CVE-2026-134492](https://cveawg.mitre.org/api/cve/CVE-2026-134492): CNA Anthropic, published 2026-11-23. Titles, ranges, scores, references.
- [GitHub Advisory Database listing for `mcp`](https://github.com/advisories?query=mcp+sort%3Apublished-desc), fetched 2026-11-24: the two CVE rows and their database ids.
- PyPI simple API for `mcp-server-git` and `mcp-server-fetch`, and `registry.npmjs.org` for the two npm packages, read 2026-11-24: versions and publish times.
- OSV returned no record for any of the vendor-tab ids on 2026-11-24.
- Not opened: the 14 other tab rows, the fix pull requests and the release notes.
