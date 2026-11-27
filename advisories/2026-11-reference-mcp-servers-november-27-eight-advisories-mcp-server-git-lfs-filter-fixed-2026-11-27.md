---
id: 2026-11-reference-mcp-servers-november-27-eight-advisories-mcp-server-git-lfs-filter-fixed-2026-11-27
title: "Reference MCP servers: eight advisories on 2026-11-27, one High in mcp-server-git through the Git LFS filter; fixed in 2026.11.27"
date_disclosed: 2026-11-27
last_updated: 2026-11-27
severity: high
status: patched
ecosystems: [pypi, npm, mcp, git]
tools_affected: ["mcp-server-git (PyPI) below 2026.11.27", "mcp-server-fetch (PyPI) 2026.10.10 to below 2026.11.27", "@modelcontextprotocol/server-memory (npm) 1.0.0 to below 2.2.2", "machines with Git LFS installed in the user or system Git configuration", "coding agents that open repositories received as archives, shared folders or vendored trees"]
tags: [mcp, mcp-server-git, git-lfs, git-config, command-execution, credential-leak, environment-variables, reference-servers, no-cve, patched]
---

## TL;DR

`mcp-server-git` below 2026.11.27 runs programs named in a repository's own `.git/config` through the Git LFS filter, per [GHSA-6663-fm5v-gqm5](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-6663-fm5v-gqm5) (High, 7.8, no CVE). The advisory requires Git LFS in the user's Git configuration and a repository whose `.git` directory someone else wrote. It says a plain `git clone` is not enough, and that the read-only `git_status` tool is one of six that trigger it. Seven Moderate and Low advisories were published the same day. Upgrade `mcp-server-git` and `mcp-server-fetch` to 2026.11.27 and `@modelcontextprotocol/server-memory` to 2.2.2.

## What happened

The [advisory tab](https://github.com/modelcontextprotocol/servers/security/advisories) of the Model Context Protocol reference servers showed eight rows dated 2026-11-27 on page 1 when read that day. Page 2 held none. Six name `mcp-server-git`, one names `mcp-server-fetch` and one names `@modelcontextprotocol/server-memory`. All eight print "No known CVE". Earlier advisories for these servers are in [the 2026-11-18 file](2026-11-mcp-server-git-repository-config-runs-commands-six-high-advisories-fixed-2026-11-18.md).

| Advisory | Package | Severity label and score | Affected as printed | Patched | What the advisory says |
|---|---|---|---|---|---|
| [GHSA-6663-fm5v-gqm5](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-6663-fm5v-gqm5) | `mcp-server-git` | High, 7.8 | below 2026.11.27 | 2026.11.27 | Repository config names programs that run through the Git LFS filter, as the user who runs the server. |
| [GHSA-wvv2-676g-r57j](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-wvv2-676g-r57j) | `mcp-server-git` | Moderate, 5.3 | 2026.11.4 to below 2026.11.27 | 2026.11.27 | `git_remote` output can show a Git credential from the user's own global or system config. |
| [GHSA-f33v-89w7-f9vc](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-f33v-89w7-f9vc) | `mcp-server-git` | Moderate, no score | below 2026.11.27 | 2026.11.27 | `repo_path` expands environment variables and the error message shows their values. |
| [GHSA-5pwg-5xfw-x322](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-5pwg-5xfw-x322) | `mcp-server-git` | Moderate, 6.5 in the body | below 2026.11.27 | 2026.11.27 | `git_show` can read objects from a second repository outside `--repository`, through a race. Needs a file-write tool on the same repository and a known object id. |
| [GHSA-3whj-m8jj-x97q](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-3whj-m8jj-x97q) | `mcp-server-git` | Moderate, 5.9 in the body | below 2026.11.27 | 2026.11.27 | A `.git` pointer file in the configured root makes `git_show` read a second repository. |
| [GHSA-qf89-h82f-h5r5](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-qf89-h82f-h5r5) | `mcp-server-git` | Low, 6.5 in the body | 2026.11.4 to below 2026.11.27 | 2026.11.27 | `git_merge` with `fast_forward_only=false` can replace an ignored local file such as `.env`. |
| [GHSA-48j5-hj63-c82c](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-48j5-hj63-c82c) | `@modelcontextprotocol/server-memory` | Moderate, 4.2 | 1.0.0 to below 2.2.2 | 2.2.2 | A local user who can write to a shared graph directory can change permissions on a file outside it, through a race. |
| [GHSA-g7v6-hfx3-8rv6](https://github.com/modelcontextprotocol/servers/security/advisories/GHSA-g7v6-hfx3-8rv6) | `mcp-server-fetch` | Low, 3.7 | 2026.10.10 to below 2026.11.27 | 2026.11.27 | The robots.txt check misses backslash and path-parameter spellings. Titled as an incomplete fix for GHSA-3rxj-6jhw-qfv7. |

### The High advisory

GHSA-6663-fm5v-gqm5 prints CVSS 3.1 7.8, `AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H`. Its conditions:

- Git LFS is installed in the user's system or global Git configuration.
- The attacker controls the repository's `.git` directory. The advisory's examples are an unpacked archive, a shared folder and a vendored tree.
- An MCP client calls `git_status`, `git_diff_unstaged`, `git_diff`, `git_add`, `git_checkout` or `git_merge` on that repository.

The advisory says a plain `git clone` of a hostile repository is not sufficient, and that the `--repository` option does not prevent the attack.

### The credential and environment advisories

- GHSA-wvv2-676g-r57j applies when the user has a credential-bearing `url.<cred>.insteadOf` rewrite in a global or system Git config and inspects an untrusted repository. The advisory says `git_remote` is annotated read-only, so clients often run it without an approval prompt. Its Summary states the range as 2026.11.18 and earlier, which differs from the range field.
- GHSA-f33v-89w7-f9vc needs only influence over a tool argument, and names prompt injection as one way. The advisory says the attacker can read any environment variable of the server process. With `--repository`, it applies when the server's working directory is inside the allowed repository.

### What the pages do not agree on

- The bodies of GHSA-5pwg-5xfw-x322 and GHSA-3whj-m8jj-x97q say no patched version is identified. Their patched field says 2026.11.27.
- GHSA-qf89-h82f-h5r5 is labelled Low. Its body prints a 6.5 base score. "In the body" in the table marks a score that the reporter's text gives.
- GHSA-5pwg-5xfw-x322, GHSA-3whj-m8jj-x97q, GHSA-qf89-h82f-h5r5 and GHSA-48j5-hj63-c82c each print a higher score that the reporter requested for one described deployment. The table shows the base scores.
- GHSA-5pwg-5xfw-x322 and GHSA-3whj-m8jj-x97q say only loss of confidentiality was demonstrated. GHSA-qf89-h82f-h5r5 says only replacement of an ignored file was demonstrated.

## Am I affected?

The commands are this file's. They do not see a server that a launcher downloads at start.

```bash
pip show mcp-server-git mcp-server-fetch 2>/dev/null | grep -iE '^(name|version)'
npm ls -g @modelcontextprotocol/server-memory
git lfs version                                   # present = one condition of the High advisory
git config --global --get-regexp '^filter\.lfs\.'  # LFS in the global Git configuration
git config --system --get-regexp '^filter\.lfs\.'  # LFS in the system Git configuration
git config --global --get-regexp 'insteadof'       # a credential here = GHSA-wvv2-676g-r57j applies
git config --system --get-regexp 'insteadof'
```

- `mcp-server-git` below 2026.11.27 is affected by at least four of the six. Version 2026.11.18, the fix for the earlier batch, is inside all six ranges.
- Check the version your MCP client configuration pins or resolves.
- The High advisory needs Git LFS and a repository whose `.git` directory someone else wrote.
- `@modelcontextprotocol/server-memory` is affected only with the opt-in HTTP transport and a graph directory another local user can write to. The advisory says default stdio installs and private graph directories are not affected.
- No CVE exists for any of the eight, so a scanner keyed on CVE ids will not flag them. OSV had no record for any of the eight ids on 2026-11-27.

## If you are affected

1. Upgrade `mcp-server-git` and `mcp-server-fetch` to 2026.11.27 and `@modelcontextprotocol/server-memory` to 2.2.2. PyPI and npm show all three published on 2026-11-27.
2. Restart the MCP client so it starts the new server. This step is this file's advice.
3. If an agent used an affected `mcp-server-git` on a repository received as an archive, shared folder or vendored tree, on a machine with Git LFS, treat the account that ran the server as exposed. Rotate the credentials it could read. See [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md). This step is this file's advice.
4. If your global Git config holds a token in an `insteadOf` rewrite and an agent ran `git_remote` on a repository you did not create, rotate that token. See [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md). This step is this file's advice.

## Prevention

- Make a fresh clone before pointing an agent at a repository someone sent you.
- Keep tokens out of Git config rewrites and out of the MCP server's environment. See [credential hygiene](../prevention/credential-hygiene.md).
- Run MCP servers under an account or sandbox that holds no cloud tokens or SSH keys. See [agent sandboxing](../prevention/agent-sandboxing.md) and [MCP hygiene](../prevention/mcp-hygiene.md).
- Do not auto-approve tools, including read-only ones, on repositories you did not create.

## Sources

Single source: the vendor repository's advisories.

- [modelcontextprotocol/servers security advisories](https://github.com/modelcontextprotocol/servers/security/advisories), pages 1 and 2, fetched 2026-11-27: id, severity and date for every row.
- The eight advisory pages linked in the table, fetched 2026-11-27 through a summarizing fetch. Paraphrased, not quoted.
- PyPI simple API for `mcp-server-git` and `mcp-server-fetch`, and `registry.npmjs.org` for `@modelcontextprotocol/server-memory`, read 2026-11-27: versions and publish times.
- OSV returned no record for any of the eight ids on 2026-11-27.
- Not opened: the fix pull requests, the release notes and page 3 of the tab. npm also shows `@modelcontextprotocol/server-filesystem` 2.4.1 published on 2026-11-27. No advisory read names it.
