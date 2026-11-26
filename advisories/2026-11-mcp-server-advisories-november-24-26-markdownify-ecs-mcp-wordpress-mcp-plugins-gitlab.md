---
id: 2026-11-mcp-server-advisories-november-24-26-markdownify-ecs-mcp-wordpress-mcp-plugins-gitlab
title: "MCP advisories 2026-11-24 to 11-26: markdownify-mcp SSRF with no npm release of the fix, Amazon ECS MCP Server, two WordPress plugins, GitLab"
date_disclosed: 2026-11-24
last_updated: 2026-11-26
severity: high
status: active
ecosystems: [mcp, npm, pypi, wordpress, gitlab, aws]
tools_affected: ["mcp-markdownify-server 1.1.0 and earlier", "awslabs.ecs-mcp-server below 0.1.36", "miniOrange Secure MCP Server WordPress plugin 1.5.8 and earlier", "AI Engine WordPress plugin 3.9.4 and earlier", "GitLab EE 18.10 to below 19.4.11, 19.5.9 and 19.6.2"]
tags: [cve-batch, mcp, ssrf, prompt-injection, redaction-bypass, privilege-escalation, wordpress-plugin, fix-not-on-registry, active]
---

## TL;DR

Five CVE records for MCP servers and products that ship one were published between 2026-11-24 and 2026-11-26. [CVE-2026-137308](https://cveawg.mitre.org/api/cve/CVE-2026-137308) says an injected prompt can make markdownify-mcp fetch internal hosts and cloud metadata endpoints. The vendor advisory says 1.2.0 fixes it. npm's newest `mcp-markdownify-server` was 1.1.0 on 2026-11-26. Amazon's ECS MCP Server returned task-definition secrets its redaction setting should hide, fixed in 0.1.36. Update the two WordPress plugins and GitLab.

## What happened

| Product | Id | Score, provider | Affected | Fix |
|---|---|---|---|---|
| markdownify-mcp, npm `mcp-markdownify-server` | CVE-2026-137308 | 8.3 CVSS 4.0 and 7.4 CVSS 3.1, VulnCheck | before 1.2.0 | 1.2.0 per the vendor advisory. Not on npm when read. |
| Amazon ECS MCP Server, PyPI `awslabs.ecs-mcp-server` | CVE-2026-135614 | 5.5 CVSS 3.1 and 6.8 CVSS 4.0, Amazon | below 0.1.36 | 0.1.36 |
| Secure MCP Server for Claude, ChatGPT, Gemini, Cursor and other AI Agents, WordPress slug `miniorange-secure-mcp-server` | CVE-2026-131688 | 8.1 CVSS 3.1, Wordfence | 1.5.8 and earlier | none stated in the record |
| AI Engine, WordPress slug `ai-engine` | CVE-2026-131589 | 7.2 CVSS 3.1, Wordfence | 3.9.4 and earlier | none stated in the record |
| GitLab EE, MCP server OAuth handling | CVE-2026-135221 | 6.3 CVSS 3.1, GitLab | 18.10 to below 19.4.11, 19.5 to below 19.5.9, 19.6 to below 19.6.2 | 19.4.11, 19.5.9, 19.6.2 |

### markdownify-mcp

The vendor advisory, published 2026-11-25, says the SSRF protections in `webpage-to-markdown`, `youtube-to-markdown`, `bing-search-to-markdown` and `git-repo-to-markdown` could be bypassed. Its title names DNS hostnames, IPv6 and IPv4-mapped IPv6 literals, and scp-style SSH shorthand. [VulnCheck's record](https://cveawg.mitre.org/api/cve/CVE-2026-137308), published 2026-11-26, says attackers can reach the tools "through prompt injection to fetch loopback services, internal hosts, and cloud metadata endpoints". The vendor page printed "No known CVE" when read on 2026-11-26.

The advisory names the npm package `mcp-markdownify-server`, affected `<= 1.1.0`, patched 1.2.0. The npm registry listed four versions on 2026-11-26, the newest 1.1.0 from 2026-05-01. npm has no package named `markdownify-mcp`. The record references a `v1.2.0` release tag in the repository, which was not opened for this file.

### Amazon ECS MCP Server

[AWS bulletin 2026-200-AWS](https://aws.amazon.com/security/security-bulletins/2026-200-aws/), published 2026-11-24, says that with the sensitive data setting at its default, the troubleshooting tool returned container environment variable values and secret references from ECS task definitions without redaction. It says a remote actor who can influence the agent's input, "for example through prompt injection", might obtain those values. The vendor advisory is [GHSA-ppc7-5jf2-gcfc](https://github.com/awslabs/mcp/security/advisories/GHSA-ppc7-5jf2-gcfc).

PyPI shows 0.1.36 uploaded on 2026-09-22 and 0.1.39 as the newest on 2026-11-17. The fixed release predates the bulletin.

### WordPress plugins

[Wordfence's record for CVE-2026-131688](https://cveawg.mitre.org/api/cve/CVE-2026-131688) says any valid MCP bearer token for the miniOrange plugin, including a scope-restricted connection-test token, can be sent to other WordPress endpoints and gives the sender's account the Administrator role. It scores attack complexity high. WordPress.org listed version 1.5.10, updated 2026-11-25, with 10,000+ active installs. The record names no fixed version and references a plugin changeset.

[Wordfence's record for CVE-2026-131589](https://cveawg.mitre.org/api/cve/CVE-2026-131589) says an authenticated user with Editor access or above can upload HTML, SVG or JavaScript files through AI Engine's `/mwai/v1/helpers/create_image` endpoint. The record does not involve the plugin's MCP feature. Its references compare the 3.9.4 and 3.9.5 tags. WordPress.org listed version 3.9.7, updated 2026-11-26, with 90,000+ active installs.

### GitLab

[GitLab's record](https://cveawg.mitre.org/api/cve/CVE-2026-135221) says that "under certain conditions" an authenticated user could make server-side requests to internal network resources "due to insufficient URL validation in MCP server OAuth handling". The [patch release of 2026-11-25](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-6-2-released/) names 15 CVE ids, this one included.

## Am I affected?

- `npm ls mcp-markdownify-server`, or check the version in your MCP client's server configuration. Every npm release is inside the range.
- `pip show awslabs.ecs-mcp-server`. Below 0.1.36 is affected.
- In WordPress, check the plugin versions under Plugins. miniOrange Secure MCP Server 1.5.8 or earlier and AI Engine 3.9.4 or earlier are affected.
- Self-managed GitLab EE from 18.10 on a version below the three fixed releases is affected.

## If you are affected

The vendor sources give upgrade steps only. The removal and review steps below are cautions beyond them.

1. markdownify-mcp: no npm release carries the fix as of 2026-11-26. Remove the server from agents that read untrusted content, or run it where it cannot reach internal hosts or a cloud metadata endpoint. Check npm again before reinstalling.
2. ECS MCP Server: upgrade to 0.1.36 or later. AWS says to "rotate any credentials stored as plaintext task definition environment variables".
3. miniOrange Secure MCP Server: update to the newest version on WordPress.org, then revoke and reissue every MCP bearer token and review the Administrator list.
4. AI Engine: update to the newest version and review the uploads directory for files Editors added through the plugin.
5. GitLab: upgrade to 19.4.11, 19.5.9 or 19.6.2.

See [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) for the review steps after an MCP server misbehaves.

## Prevention

- Run URL-fetching MCP servers with no route to internal networks or metadata endpoints. See [MCP hygiene](../prevention/mcp-hygiene.md).
- Keep secrets out of plaintext task-definition environment variables. See [credential hygiene](../prevention/credential-hygiene.md).

## Sources

- [markdownify-mcp GHSA-pxwh-pcrm-vrm3](https://github.com/zcaceres/markdownify-mcp/security/advisories/GHSA-pxwh-pcrm-vrm3), published 2026-11-25, read 2026-11-26. Package name, range, tools.
- [CVE-2026-137308](https://cveawg.mitre.org/api/cve/CVE-2026-137308), VulnCheck, 2026-11-26. `registry.npmjs.org/mcp-markdownify-server` read 2026-11-26.
- [AWS bulletin 2026-200-AWS](https://aws.amazon.com/security/security-bulletins/2026-200-aws/), 2026-11-24, and [GHSA-ppc7-5jf2-gcfc](https://github.com/awslabs/mcp/security/advisories/GHSA-ppc7-5jf2-gcfc). [CVE-2026-135614](https://cveawg.mitre.org/api/cve/CVE-2026-135614), Amazon. PyPI simple API read 2026-11-26.
- [CVE-2026-131688](https://cveawg.mitre.org/api/cve/CVE-2026-131688) and [CVE-2026-131589](https://cveawg.mitre.org/api/cve/CVE-2026-131589), Wordfence, 2026-11-26. `api.wordpress.org` plugin information for both slugs, read 2026-11-26.
- [CVE-2026-135221](https://cveawg.mitre.org/api/cve/CVE-2026-135221), GitLab, 2026-11-25, and the [GitLab patch release 19.6.2, 19.5.9, 19.4.11](https://docs.gitlab.com/releases/patches/patch-release-gitlab-19-6-2-released/), read through the patch-release feed.
- Not readable: both Wordfence pages returned an empty body. Not opened: the markdownify-mcp releases page.
