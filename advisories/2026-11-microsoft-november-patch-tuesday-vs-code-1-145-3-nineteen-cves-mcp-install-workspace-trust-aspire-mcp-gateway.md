---
id: 2026-11-microsoft-november-patch-tuesday-vs-code-1-145-3-nineteen-cves-mcp-install-workspace-trust-aspire-mcp-gateway
title: "VS Code 1.145.3 fixes 19 CVEs (MCP server links, Workspace Trust bypasses); Aspire 13.6.5 and MCP Gateway also patched (2026-11-10)"
date_disclosed: 2026-11-10
last_updated: 2026-11-11
severity: critical
status: patched
ecosystems: [vscode, mcp, aspire, dotnet, npm, azure, copilot, jetbrains]
tools_affected: ["Visual Studio Code before 1.145.3 (19 CVEs)", "Aspire Dashboard, Aspire.Hosting and Aspire.Cli before 13.6.5 (npm `@microsoft/aspire-cli` before 13.6.5)", "Microsoft MCP Gateway (CVE-2026-109492; fixed build printed as 1.0.0)", "Microsoft 365 Agents SDK (CVE-2026-109485; product printed as Microsoft Agent Framework SDK for .NET, fixed build 1.8.77)", "GitHub Copilot plugin for JetBrains IDEs before 1.17.0-251 (CVE-2026-83953)", "Azure OpenAI (CVE-2026-119990, fixed by Microsoft, no customer action)"]
tags: [cve, msrc, patch-tuesday, vscode, mcp, mcp-install-link, workspace-trust, extension-marketplace, inline-chat, aspire, mcp-gateway, agents-sdk, azure-openai, copilot-jetbrains]
---

## TL;DR
Microsoft's November 2026 security updates (2026-11-10) carry 19 CVEs fixed in Visual Studio Code 1.145.3. Two name MCP servers: a remote MCP server that gets a click on a notification link can run code as the user (CVE-2026-120779, 9.6), and an MCP install link's preview can omit security-relevant details (CVE-2026-114171, 8.8). A third describes a malicious server whose response runs code on the client, without naming the protocol (CVE-2026-119983, 8.8). Four more let an untrusted workspace run code without the user granting trust. Update VS Code to 1.145.3 or later. If you use Aspire, update to 13.6.5: CVE-2026-118740 (9.1) is an unauthenticated bypass of dashboard authentication. Microsoft marks none of these as exploited or publicly disclosed.

## What happened

All facts below are from Microsoft's November security update document and its per-CVE entries, read 2026-11-11. Microsoft is the CNA and supplied every score. The scores are Microsoft's assessment and each entry is a short description plus an FAQ, with no researcher write-up read by this sweep. Forks of VS Code (Cursor, Windsurf and others) are not named in the document and this file does not say whether they are affected.

**Visual Studio Code, fixed build 1.145.3 for all 19.**

| CVE | Microsoft's title | CVSS 3.1 | What the FAQ says |
|---|---|---|---|
| CVE-2026-120779 | Remote Code Execution | 9.6 | An attacker who controls a remote MCP server convinces a user to connect VS Code to it and click a link in a notification, and can then run code with the user's permissions. |
| CVE-2026-114171 | Security Feature Bypass | 8.8 | A user installs an MCP server through a crafted link. "The installation preview could omit security-relevant details", and the installed server runs code as the user. |
| CVE-2026-119983 | Security Feature Bypass | 8.8 | A user connects an affected client to a malicious server, and the server's response leads to code execution on the client. |
| CVE-2026-121663 | Security Feature Bypass | 8.8 | Opening a crafted workspace bypasses Workspace Trust and runs code. "The user does not need to grant trust." Exploitation More Likely. |
| CVE-2026-121662 | Remote Code Execution | 8.6 | Same FAQ text as CVE-2026-121663. Exploitation More Likely. |
| CVE-2026-102236 | Security Feature Bypass | 8.6 | Content from an untrusted workspace runs commands or code without the user first granting trust. |
| CVE-2026-121665 | Security Feature Bypass | 8.8 | A crafted workspace plus a click on an attacker-controlled notification runs commands without trust being granted. |
| CVE-2026-121661 | Security Feature Bypass | 7.8 | An untrusted workspace applies settings that Workspace Trust should block. |
| CVE-2026-119975 | Remote Code Execution | 8.8 | An extension with crafted display information. A click on a link in the publisher trust dialog runs code before the extension is installed or the publisher trusted. |
| CVE-2026-121664 | Remote Code Execution | 8.3 | A link on a crafted extension's details page runs code without installing the extension. Needs an already-open integrated terminal. |
| CVE-2026-121660 | Security Feature Bypass | 7.5 | An extension installs and runs despite an administrator's extension allowlist policy. |
| CVE-2026-119985 | Remote Code Execution | 8.3 | A crafted link or web page opened in VS Code leads to code execution in the user's connected development environment. |
| CVE-2026-120780 | Remote Code Execution | 8.3 | A crafted link opened by a user with an authenticated VS Code web-server session can cause a vulnerable older server version to run, if one remains available. |
| CVE-2026-70094 | Remote Code Execution | 8.8 | The user opens a crafted file. |
| CVE-2026-119982 | Security Feature Bypass | 6.5 | Crafted content processed with inline chat modifies other workspace files, "bypassing the restriction that limits edits to the active document". |
| CVE-2026-102230 | Information Disclosure | 7.4 | File content. |
| CVE-2026-119976 | Information Disclosure (GitHub Pull Requests and Issues extension) | 6.5 | NetNTLMv2 hashes. |
| CVE-2026-119981 | Elevation of Privilege | 7.0 | Code execution in the context of another VS Code user on the same system. |
| CVE-2026-120782 | Security Feature Bypass | 7.8 | No FAQ. |

**Aspire, fixed build 13.6.5.**

| CVE | Component | CVSS 3.1 | What Microsoft says |
|---|---|---|---|
| CVE-2026-118740 | Aspire Dashboard | 9.1 | An unauthenticated attacker with network access to the dashboard bypasses authentication, reads sensitive information and can modify or delete telemetry. |
| CVE-2026-120778 | Aspire.Cli on Linux and macOS | 7.3 | Code execution with another local user's permissions. |
| CVE-2026-120792 | Aspire.Cli on Linux and macOS | 7.3 | Another user's configuration, "including credentials stored in that configuration", is exposed through diagnostic logs on a shared computer. |
| CVE-2026-120006 | Aspire.Hosting, Aspire.Hosting.AppHost | none printed | Elevation of privilege. No FAQ. |

`npm view @microsoft/aspire-cli time` on 2026-11-11 shows 13.6.5 published 2026-11-10 17:47 UTC, after 13.6.4 on 2026-10-24. The GitHub Advisory Database lists CVE-2026-120792 against that npm package as GHSA-q6jf-24jf-m3cg.

**Agent and gateway products.**

- **Microsoft MCP Gateway, CVE-2026-109492.** An authenticated attacker sends crafted requests to reach another user's resources in the gateway, and can "read another user's workload logs or disrupt that user's workloads". The CNA record scores it 8.8 (`AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H`). The record's affected entry reads version `1.0.0.0`, less than `1.0.0`, which is not a usable range. This file gives no "upgrade to" version for it. Use the newest release and read Microsoft's entry.
- **Microsoft 365 Agents SDK, CVE-2026-109485, 6.3.** Server-side request forgery that discloses information to an authorized attacker. The title says Microsoft 365 Agents SDK. The affected product is printed as "Microsoft Agent Framework SDK" for .NET with version `1.21.0` and less-than `1.8.77`. The title and the product name differ and the two version numbers do not form a range. This file prints them as read and derives no fixed version.
- **GitHub Copilot plugin for JetBrains IDEs, CVE-2026-83953, 5.5.** Local information disclosure, described as reading from the file system. Fixed build 1.17.0-251.
- **Azure OpenAI, CVE-2026-119990, 9.8.** Elevation of privilege in the service. Microsoft says it "has already been fully mitigated by Microsoft" and customers have no action to take.

## Am I affected?

1. **VS Code.** `code --version`. Anything before 1.145.3 is affected by all nineteen. Check remote hosts and containers too: the VS Code server on a remote machine has its own version, and CVE-2026-120780 turns on an older server version remaining available.
2. **MCP servers in VS Code.** List the servers you have added, in user settings and in each workspace's `.vscode/mcp.json`. Ask where each one came from. A server installed from a link on a web page or in a chat message is the case CVE-2026-114171 describes.
3. **Aspire.** `aspire --version`, and the `Aspire.*` package versions in your projects. Then check whether an Aspire dashboard is reachable from any network you do not control.
4. **Copilot for JetBrains.** The plugin version in the IDE's plugin list, against 1.17.0-251.

## If you are affected

- Update VS Code to 1.145.3 or later and restart it. Update remote servers and dev container images, and remove old server versions left on remote hosts.
- Review MCP servers added before the update and remove any you cannot trace to a source you trust. [If an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) covers what to rotate.
- Update Aspire to 13.6.5. If a dashboard before 13.6.5 was reachable from an untrusted network, treat the telemetry it showed as read, including any secrets in logged environment or connection strings, and rotate them.
- On shared Linux or macOS machines that ran Aspire.Cli before 13.6.5, rotate credentials stored in Aspire configuration.

## Prevention

- **Do not install an MCP server from a link.** Add servers by hand from a source you chose, and read the command and arguments it will run. [MCP hygiene](../prevention/mcp-hygiene.md) has the checklist.
- **Workspace Trust is one control, not a sandbox.** Five of these CVEs bypass it. Open unfamiliar repositories in a container or VM with no credentials. See [agent sandboxing](../prevention/agent-sandboxing.md).
- **Keep developer dashboards off public interfaces.** Bind them to loopback and reach them through a tunnel.

## Sources

- [MSRC CVRF document 2026-Nov](https://api.msrc.microsoft.com/cvrf/v3.0/cvrf/2026-Nov), fetched 2026-11-11: "November 2026 Security Updates", initial release 2026-11-10, current release 2026-11-11 01:07 UTC, 1,362 vulnerability records. Titles, CVSS vectors, FAQ text, fixed builds, exploitability assessments and acknowledgments for every id above. Single source: the vendor, which is also the CNA.
- [MSRC: CVE-2026-109492](https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability/CVE-2026-109492), [CVE-2026-109485](https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability/CVE-2026-109485) and [CVE-2026-120792](https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability/CVE-2026-120792), fetched 2026-11-11: released 2026-11-10, customer action required, not exploited, not publicly disclosed.
- [CVE Services: CVE-2026-109492](https://cveawg.mitre.org/api/cve/CVE-2026-109492), [CVE-2026-109485](https://cveawg.mitre.org/api/cve/CVE-2026-109485) and [CVE-2026-120792](https://cveawg.mitre.org/api/cve/CVE-2026-120792), fetched 2026-11-11: Microsoft CNA, published 2026-11-10; the affected entries and scores quoted above.
- [GitHub Advisory Database, `mcp` listing](https://github.com/advisories?query=mcp+sort%3Apublished-desc), fetched 2026-11-11: rows for CVE-2026-120792 (GHSA-q6jf-24jf-m3cg, `@microsoft/aspire-cli`) and CVE-2026-109492 (GHSA-xgj3-w2cc-qgrq, unreviewed).
- `npm view @microsoft/aspire-cli time`, run 2026-11-11: 13.6.5 at 2026-11-10 17:47 UTC.
- Count note: this sweep selected records by product name in the title and then by fixed product. Both returned the same 19 ids, one of which is the GitHub Pull Requests and Issues extension. The Hacker News and SecurityWeek front pages print different totals for the whole release (1,259 and 1,094). The document held 1,362 records when read. Neither article was opened.
