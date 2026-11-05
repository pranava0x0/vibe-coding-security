---
id: 2026-10-solanacry-solana-starter-kit-github-repository-ranked-by-agent-search-remove-and-rotate
title: "Malicious SolanaUpdateTools/solana-starter-kit GitHub repository reached agents through search ranking (SolanaCry): remove the implant and rotate wallet keys"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-11-05
severity: high
status: unconfirmed
ecosystems: [github, windows, claude-code, agent-web-search, solana]
tools_affected: ["Windows developer machines whose coding agent (AIR Security's demonstration used Claude Code with its web search) selected the repository while building a Solana project", "any developer who followed the repository's README install step by hand"]
tags: [malicious-repository, agent-search-poisoning, readme-install-command, remote-access-tool, windows, crypto-wallets, air-security, single-firm, unconfirmed]
---

## TL;DR
If a coding agent or a developer on a Windows machine ran the install step from the `SolanaUpdateTools/solana-starter-kit` GitHub repository, remove the staging folder and the Run key it leaves, then rotate every wallet key, credential and token that was on the machine. The repository returned 404 on 2026-11-05; the operator has reused the same lure pattern against other audiences and new repositories are likely.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub | `SolanaUpdateTools/solana-starter-kit` | the repository as a whole (created 2025-11, 286 stars at analysis); its README's only install step downloads and runs remote content | do not clone or install; treat any copy as hostile | `github.com` returned 404 for the repository (2026-11-05) | none: not a registry package, no GHSA, no OSV record |

The status is `unconfirmed` because AIR Security is the only firm to have analysed the repository and its payload; The Hacker News lists the finding in its 2026-11-05 roundup from the same post. AIR Security says the payload URL was offline when it checked and the payload was recovered from a web archive.

## Am I affected?

Windows only. AIR Security lists what the installer leaves:

1. A hidden staging folder `%LOCALAPPDATA%\y2inwRnI6G` holding 13 NetSupport Manager components, among them `client32.exe` and several DLLs, plus an attacker-supplied `client32.ini`.
2. A `Run` value named `SecureModule` under `HKCU\Software\Microsoft\Windows\CurrentVersion\Run` that starts `client32.exe` at every login.
3. The installer clears the `RunMRU` history under `HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer` and deletes its own script, so an empty recent-commands list on a machine that ran a PowerShell install step is itself a signal.

```powershell
Get-ChildItem "$env:LOCALAPPDATA\y2inwRnI6G" -ErrorAction SilentlyContinue
Get-ItemProperty "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run" -Name SecureModule -ErrorAction SilentlyContinue
Get-Process client32 -ErrorAction SilentlyContinue | Select-Object Path
```

4. Check the agent's transcripts: a Claude Code (or other agent) session that was asked to build a Solana project and fetched or cloned `solana-starter-kit`, or ran a PowerShell command from its README, is the path AIR Security demonstrated. The developer never had to approve the command for the agent to follow the README.

## If you are affected

- Disconnect the machine from the network. Remove the staging folder and the `SecureModule` Run value, then reboot and confirm `client32.exe` is not running. NetSupport Manager is a legitimate remote-control product, so an endpoint scanner may not flag it; the folder name and the Run value are the indicators.
- Rotate every cryptocurrency wallet key, seed phrase, exchange API key, cloud credential, Git token and session cookie that was on the machine, in that order. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) and [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
- Move funds out of any wallet whose key was on the machine before rotating anything else.

## Prevention

- Treat everything an agent reads, including search results, READMEs and documentation, as untrusted input, and require review before an agent runs a command that downloads and executes remote content. See [agent sandboxing](../prevention/agent-sandboxing.md).
- A high search rank is not provenance. Vet a repository before an agent installs from it: [package vetting checklist](../prevention/package-vetting-checklist.md).
- Expect the pattern to recur under new names; AIR Security says the operator changes lures often and used the same install-command pattern against traders in a campaign documented in 2025-10.

## Sources
- [AIR Security — SolanaCry](https://www.air.security/blog-posts/solanacry) — fetched 2026-11-05 (2026-10-29, Eliad Mualem and Dor Granat, AIR Research Lab): the repository name and creation date, the 286 stars, the agent-search delivery path with Claude Code and Brave Search named, the README install step, the staging folder, file names, Run value and history clearing, the NetSupport Manager payload, the credential categories, the remediation list, the 2025-10 related campaign, the offline payload URL and web-archive recovery. Single firm.
- [The Hacker News — ThreatsDay: Apache OFBiz RCE, DreamHost Breach, DeFi Site Hijacks + 17 More Stories](https://thehackernews.com/2026/11/threatsday-apache-ofbiz-rce-dreamhost.html) — fetched 2026-11-05 (2026-11-05): item 19, "Malicious AI Search Results Steal Crypto", from the same post. Outlet pickup.
- GitHub, `github.com/SolanaUpdateTools/solana-starter-kit`, fetched 2026-11-05: HTTP 404. The repository URL is not linked here.
- Not opened: AIR Security's companion post "web-hole", linked by The Hacker News.
- Related in this corpus: [AGENTS.md in the Downloads folder](2026-10-agents-md-in-downloads-folder-hijacks-coding-agents-started-there-function-color-npm.md), [Binance initial findings: trojanized AI coding tool from a search result](2026-11-binance-october-29-heist-initial-findings-trojanized-ai-coding-tool-search-result-fake-interview-assignment-internal-ai-tool.md), [fake qwen2-tiny Hugging Face repositories](2026-10-hugging-face-qwen2-tiny-trust-remote-code-model-repositories-remove-and-rotate.md).
