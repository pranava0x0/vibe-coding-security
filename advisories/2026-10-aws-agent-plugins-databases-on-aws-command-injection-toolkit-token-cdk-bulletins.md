---
id: 2026-10-aws-agent-plugins-databases-on-aws-command-injection-toolkit-token-cdk-bulletins
title: "AWS bulletins 2026-10-08: the databases-on-aws plugin for AI coding agents let ingested content reach a local psql helper as an OS command (CVE-2026-107322, fixed 1.7.1), AWS Toolkit for VS Code cached a CodeCatalyst bearer token world-readable (CVE-2026-107332, fixed 4.10.0), and CDK Docker bundling could emit symlinked files (CVE-2026-107608, fixed aws-cdk-lib 2.267.0)"
date_disclosed: 2026-10-08
last_updated: 2026-10-09
severity: high
status: patched
ecosystems: [aws, ai-agents, vscode, npm, iac]
tools_affected: ["Amazon Agent Plugins for AWS (databases-on-aws)", "Claude Code, Kiro, Cursor and other agents with the plugin installed", "AWS Toolkit for Visual Studio Code", "aws-cdk-lib"]
tags: [cve, aws-bulletin, agent-plugin, prompt-injection, command-injection, credential-exposure, vscode-extension, cdk, symlink]
---

## TL;DR
AWS published three security bulletins on 2026-10-08. The one for this audience is **CVE-2026-107322** (CVSS 4.0 8.5 / 3.1 7.8): **Amazon Agent Plugins for AWS**, the open-source plugin collection that "extends supported AI coding agents with AWS-focused workflows", shipped a `databases-on-aws` plugin whose Aurora DSQL helper had an incomplete list of disallowed inputs. "A remote unauthenticated actor" can "supply crafted content that an agent ingests", and if the agent then invokes the local helper with that value, an OS command runs with the helper's permissions. That is prompt injection to shell through an agent plugin, with AWS's own wording. Affected 1.0.0 through 1.7.0; the fix in **1.7.1** reached the marketplace from the repository's main branch on **2026-08-26**, six weeks before the bulletin, and pinned checkouts need commit `8b13a503…` or later. The other two: **CVE-2026-107332** (6.8 / 5.5), AWS Toolkit for VS Code below **4.10.0** wrote the CodeCatalyst bearer token to a world-readable cache file and never deleted it (fixed 2026-07-09); **CVE-2026-107608** (6.8 / 5.5), `aws-cdk-lib` below **2.267.0** let a Dockerfile insert symlinked files into asset-bundling output.

## What happened
All three bulletins carry a 10/08 publication date and a fix that shipped earlier, which is AWS's usual pattern: the bulletin is the disclosure, the release was the fix.

**2026-130 — CVE-2026-107322, databases-on-aws plugin.** The plugin "provides database design, development, migration, and operational guidance, including Aurora DSQL helper scripts". The affected code "is not a listening network service"; the chain is content the agent reads, a database command value built from it, and the optional `psql` connection helper executing it. AWS is explicit that the command "runs with the permissions of the process running the helper" and that the DSQL service and database privileges are not bypassed. Workarounds while upgrading: avoid the helper's connection command path and use reviewed SQL or the plugin's DSQL MCP server instead; run the agent and helper as an unprivileged OS user with an IAM role limited to `dsql:DbConnect` and a scoped, preferably read-only, database role; never `dsql:DbConnectAdmin` for routine agent work. If the helper host "was inappropriately accessed", rotate the AWS credentials available to that process and review the IAM-to-database role mappings. Credit Shay Sakazi. The bulletin cites GHSA-x7f2-wxc8-qpxq; that advisory page returned 404 at both the database and repository URLs on 2026-10-09, so the bulletin and the CNA record are the sources here.

**2026-129 — CVE-2026-107332, AWS Toolkit for Visual Studio Code.** When a user connected to a CodeCatalyst Dev Environment, "the extension cached the user's CodeCatalyst bearer token to a file with world-readable permissions and did not remove the file after the session ended". Any local user or process could read it. Fixed in 4.10.0 on 2026-07-09, which writes the file owner-only and deletes it when the environment stops. Workaround for older versions: delete files named `codecatalyst..token` in the extension's global storage after each session. This is the [Kiro and AWS Toolkit credential-file class](2026-09-kiro-ide-cli-aws-bulletin-cve-batch.md) again: a developer tool leaves a bearer token on disk where the next malicious npm postinstall finds it.

**2026-131 — CVE-2026-107608, aws-cdk-lib.** "Prior to 2.267.0, it was possible for a docker file to insert a symlinked file or directory into the output of asset bundling without the symlink having been provided as input". The exposure is a bundling container that runs untrusted code; the workaround is to audit every Docker bundling container and its dependencies. Relevant to anyone whose agent generates CDK stacks and pulls base images it was told to.

The fourth bulletin of the week, 2026-128 (CVE-2026-107352, Athena engine v3 query metadata readable across accounts), was fixed service-side on 2026-09-01 with no customer action, and is out of scope here.

## Am I affected?
```bash
# Agent plugin: look for the plugin in any agent's plugin/marketplace directory and check its version or commit
grep -rn "databases-on-aws" ~/.claude ~/.kiro ~/.cursor ~/.config 2>/dev/null | head
# AWS Toolkit for VS Code
code --list-extensions --show-versions 2>/dev/null | grep -i amazonwebservices.aws-toolkit-vscode    # < 4.10.0
# CDK
npm ls aws-cdk-lib 2>/dev/null; pip show aws-cdk-lib 2>/dev/null | grep Version                  # < 2.267.0
```
For the plugin, the exposed shape is an agent that reads untrusted content (issues, docs, web pages, repository files) and has the DSQL helper available with credentials in its environment.

## If you are affected
1. Update the plugin to **1.7.1 or later** in every environment, or move a pinned checkout past commit `8b13a503746a4ebb0402b936645163224058bde3`; confirm the updated plugin is the one the agent actually loads.
2. Update AWS Toolkit for VS Code to **4.10.0 or later** and delete any leftover `codecatalyst..token` files; treat the old token as exposed to every process on that machine.
3. Update `aws-cdk-lib` to **2.267.0 or later** and audit bundling containers.
4. Rotate the AWS credentials the helper process could reach if you have any reason to think it ran an unexpected command. See [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) and [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention
An agent plugin is code that runs with the agent's credentials on content the agent did not write; give it the narrowest IAM role and database role that still works, and keep admin roles out of its environment ([agent-sandboxing.md](../prevention/agent-sandboxing.md), [credential-hygiene.md](../prevention/credential-hygiene.md)). Inventory the plugins and skills installed in every agent, and treat a marketplace served from a `main` branch as unpinned ([mcp-hygiene.md](../prevention/mcp-hygiene.md)).

## Sources
- [AWS Security Bulletin 2026-130 — CVE-2026-107322: OS command injection in Amazon Agent Plugins for AWS databases-on-aws](https://aws.amazon.com/security/security-bulletins/2026-130-aws/) (fetched 2026-10-09; published 10/08/2026; affected 1.0.0 through 1.7.0, fix 1.7.1 available 2026-08-26, pinned-commit guidance, workarounds, credit Shay Sakazi)
- [AWS Security Bulletin 2026-129 — CVE-2026-107332: Insecure default file permissions on cached credentials in AWS Toolkit for Visual Studio Code](https://aws.amazon.com/security/security-bulletins/2026-129-aws/) (published 10/08/2026; < 4.10.0, fixed 4.10.0 on 2026-07-09, workaround)
- [AWS Security Bulletin 2026-131 — CVE-2026-107608: Improper link resolution in asset bundling output handling in aws-cdk-lib](https://aws.amazon.com/security/security-bulletins/2026-131-aws/) (published 10/08/2026; < 2.267.0)
- [AWS Security Bulletin 2026-128 — CVE-2026-107352: Missing authorization checks in Amazon Athena engine version 3](https://aws.amazon.com/security/security-bulletins/2026-128-aws/) (service-side fix 2026-09-01; noted for completeness)
- [CVE Services — CVE-2026-107322](https://cveawg.mitre.org/api/cve/CVE-2026-107322) (CNA AMZN, 2026-10-08, CVSS 4.0 8.5 / 3.1 7.8, `databases-on-aws` < 1.7.1), [CVE-2026-107332](https://cveawg.mitre.org/api/cve/CVE-2026-107332) (6.8 / 5.5, `aws-toolkit-vscode` < 4.10.0), [CVE-2026-107608](https://cveawg.mitre.org/api/cve/CVE-2026-107608) (6.8 / 5.5, `aws-cdk-lib` < 2.267.0)
- [AWS Security Bulletins index](https://aws.amazon.com/security/security-bulletins/) (walked 2026-10-09; 2026-128 through 2026-131 new since the 2026-10-07 sweep)
