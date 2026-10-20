---
id: 2026-10-apex-accelerator-malicious-npm-packages-ref8801
title: "Malicious `@apexacc` and `@apexfdn` npm packages (Apex Accelerator): remove and rotate AI-tool, wallet and browser credentials"
kind: malicious-artifact
date_disclosed: 2026-10-12
last_updated: 2026-10-20
severity: high
status: active
ecosystems: [npm, ai-coding-agents, mcp]
tools_affected: ["anyone who installed @apexacc/cli or @apexacc/audit (Windows x64, macOS arm64 builds)", "anyone who installed @apexfdn/apex or @copilot-mcp/apex before npm removed them", "Claude, Cursor and Windsurf users on the same machine (credential files named by Elastic)", "MCP configurations on the same machine"]
tags: [supply-chain, malicious-package, infostealer, npm, web3-lure, fake-accelerator, elastic, osv, ai-tool-credentials, mcp-config]
---

## TL;DR
Remove `@apexacc/cli`, `@apexacc/audit`, `@apexfdn/apex` and `@copilot-mcp/apex` from every machine and lockfile; `@apexacc/cli` is deprecated but still installs, and the `@apexfdn` scope still carries a live package no record covers. If any of them ran, treat the host as compromised and rotate AI coding-tool authentication, LLM and MCP tokens, wallet, browser, messenger, VPN and remote-access credentials, and the macOS administrator password if it was entered.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| npm | `@apexacc/cli` | every version: 1.1.8 (2026-08-09) through 1.6.2 (2026-09-27), 122 versions; Elastic says malicious from the first release | remove; no clean release | deprecated 2026-10-13 ("Package no longer supported"), still resolves and installs (2026-10-20) | MAL-2026-17924 (2026-10-16; credits Elastic Security Labs, Patrick Duggan) |
| npm | `@apexacc/audit` | every version; Elastic says all 18 of its tools return fabricated findings | remove | removed, registry returns "Not found" (2026-10-20) | MAL-2026-17923 (2026-10-16; same credits) |
| npm | `@apexfdn/apex` | 1.0.1 through 1.0.32 per OSV; the registry timeline shows 34 versions from 2026-07-05 | remove | replaced by the npm security holder `0.0.1-security` (2026-07-21) | MAL-2026-10979 (2026-07-21; credit Amazon Inspector) |
| npm | `@copilot-mcp/apex` | 1.0.0 through 1.0.22, thirteen versions listed by OSV | remove | removed, registry returns "Not found" (2026-10-20) | MAL-2026-12314 (2026-08-05; credit Amazon Inspector) |
| npm | `@apexfdn/copilot-mcp` | 0.1.0 (2026-04-30) through 0.11.6 (2026-07-20), 21 versions | remove; no record names it, listed here because it shares the scope of a package npm replaced with a security holder | live, not deprecated (2026-10-20) | none |

Elastic Security Labs (REF8801, 2026-10-12, Jia Yu Chan and Daniel Stepanic) describes the operation as a fake Web3 accelerator, "Apex Arena", offering crypto founders free AI coding credits, tools, security audits and an in-person event; `@apexacc/cli` is a repackaged copy of the open-source coding agent Oh My Pi (Elastic compared Apex Copilot v1.6.1 against Oh My Pi v16.3.6). Windows x64 and macOS arm64 builds exist for both `@apexacc` packages. Elastic's post does not state version ranges, publish dates or registry status; those columns come from the npm registry `time` field and the OSV records, read 2026-10-20.

## Am I affected?

- Lockfiles and manifests: `grep -rE '@apexacc/|@apexfdn/|@copilot-mcp/apex' package.json package-lock.json pnpm-lock.yaml yarn.lock` in every project and `npm ls -g --depth=0 | grep -E 'apexacc|apexfdn|copilot-mcp'` for global installs.
- Files Elastic names as left on disk: `%USERPROFILE%\.apex-audit`, `%USERPROFILE%\.apex\agent\mcp.json`, `%APPDATA%\.cobra`, `~/.config/cloudsync/`, `~/.local/share/cloudsync/` (with a log directory), and in `%TEMP%`: `_apex_run.ps1`, `_apex_run.vbs`, `_audit_run.ps1`, `_audit_run.vbs`, `exegis.exe`, `updater_loader.exe`, `visual.exe`; plus cached executables under the user's home directory written by the npm launchers.
- Agent MCP configuration files (`~/.claude.json`, `.cursor/mcp.json`, Windsurf and other clients' MCP settings) containing server entries you did not add.
- You received an "Apex Arena" or Apex accelerator invitation, audit offer or credit offer and installed what it pointed at.

## If you are affected

1. Uninstall the packages, delete the directories and files listed above, and treat the host as compromised: review for persistence before returning it to service, or reimage.
2. Rotate, from a clean machine, in this order per Elastic: the macOS administrator password if it was entered at a prompt; every LLM and API token used on the machine (Apex, OpenRouter, provider keys); MCP server bearer tokens; AI coding-tool authentication files for Claude, Cursor and Windsurf; browser-saved passwords and session cookies; cryptocurrency wallet credentials; messenger, remote-access, FTP and VPN credentials; game-client and Wi-Fi profile credentials.
3. Remove unfamiliar entries from every agent's MCP configuration and re-add only servers you installed.
4. Follow [if you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md) for the lockfile and CI sweep and [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) for the MCP-config step.

## Prevention

- [Package vetting checklist](../prevention/package-vetting-checklist.md): a scoped package from an organisation you met through an invitation is a new publisher with no history.
- [npm hardening](../prevention/npm-hardening.md): `--ignore-scripts` and install-time review.
- [MCP hygiene](../prevention/mcp-hygiene.md): review MCP configuration files after any install that touched the agent.
- [Credential hygiene](../prevention/credential-hygiene.md).

## Sources
- [Elastic Security Labs — Threat Command: Apex Accelerator malicious npm packages (REF8801)](https://www.elastic.co/security-labs/threat-command/apex-accelerator-malicious-npm-packages) — fetched 2026-10-20: publication date 2026-10-12, authors, the two `@apexacc` package names, the lure, the Oh My Pi repackaging and version comparison, affected platforms, the on-disk paths, credential categories and remediation steps quoted above. Read for artifacts and remediation only.
- [OSV — MAL-2026-17924 (@apexacc/cli)](https://osv.dev/vulnerability/MAL-2026-17924), [MAL-2026-17923 (@apexacc/audit)](https://osv.dev/vulnerability/MAL-2026-17923), [MAL-2026-10979 (@apexfdn/apex)](https://osv.dev/vulnerability/MAL-2026-10979), [MAL-2026-12314 (@copilot-mcp/apex)](https://osv.dev/vulnerability/MAL-2026-12314) — fetched 2026-10-20 through `api.osv.dev`: publication dates, credits and the version lists in the table.
- npm registry records for `@apexacc/cli`, `@apexacc/audit`, `@apexfdn/apex`, `@copilot-mcp/apex` and `@apexfdn/copilot-mcp` — read 2026-10-20 (`registry.npmjs.org/<name>`): version counts, first and last publish dates, the deprecation text, the security-holder version, and the two "Not found" responses.
- Related in this corpus: [the infostealer families with an AI-agent module](2026-09-infostealers-target-coding-agent-tokens-mcp-configs-prompt-histories.md) for the credential categories, [the third-party.com placeholder-domain skills](2026-09-third-party-com-placeholder-domain-clickfix-agent-skills.md) for the invitation-shaped lure.
