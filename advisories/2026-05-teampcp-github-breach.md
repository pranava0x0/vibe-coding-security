---
id: 2026-05-teampcp-github-breach
title: "TeamPCP breaches GitHub's internal repos via poisoned VS Code extension (May 2026)"
date_disclosed: 2026-05-20
last_updated: 2026-05-20
severity: high
status: contained
ecosystems: [vscode, github, npm, pypi]
tools_affected: [vscode, cursor, windsurf, github, any-ide-extension-user]
tags: [supply-chain, ide-extension, credential-theft, source-code-theft, teampcp, dev-tool]
---

## TL;DR
On **2026-05-20**, GitHub confirmed that attackers exfiltrated **~3,800 of its own internal repositories** after a GitHub employee installed a **poisoned VS Code extension** on their device. The actor is **TeamPCP** (aka PCPcat / DeadCatx3 / UNC6780) — the same group behind the [Mini Shai-Hulud npm/PyPI worm](2026-05-mini-shai-hulud-may19-wave.md) — who listed the stolen source for sale at **$50,000** and threatened to leak it free if no buyer appeared. GitHub says it removed the malicious extension version, isolated the endpoint, and found **no evidence** that customer data stored outside its internal repos was affected (investigation ongoing). The takeaway for vibe coders: your **IDE extension marketplace is an unaudited supply-chain surface** sitting directly on top of every credential your editor can reach.

## What happened
GitHub launched an investigation after TeamPCP publicly claimed it had breached GitHub's private codebase. GitHub's findings: the attacker compromised a GitHub employee's device through a **malicious version of a Visual Studio Code extension**, then used that foothold to access and exfiltrate GitHub-internal repositories. The attacker's claim of **~3,800 repositories** is, per GitHub, "directionally consistent" with the investigation so far.

This is the latest escalation in the TeamPCP campaign that has run all year — the group has previously trojanized Aqua's **Trivy** scanner, **Checkmarx KICS**, **LiteLLM**, the **Telnyx** SDK, **TanStack**, **MistralAI**, and most recently Microsoft's [`durabletask` PyPI SDK and the @antv npm ecosystem](2026-05-mini-shai-hulud-may19-wave.md). The through-line: TeamPCP keeps weaponizing **developer trust surfaces** — package registries, CI tokens, and now IDE extensions — to reach source code and credentials.

GitHub's response so far: removed the malicious extension version, isolated the compromised endpoint, and began incident response. The company stated it has no evidence customer information outside GitHub-internal repos was impacted, with the caveat that the investigation is ongoing.

> **Note:** at the time of writing the specific malicious extension and its publisher/IOCs have not been publicly named. This advisory will be updated as GitHub and researchers publish concrete indicators. Do not infer a package name that isn't confirmed.

## Am I affected?
This is a breach of GitHub's *own* internal repos, not a directly distributed payload — so most readers are not directly compromised. The actionable risk is the **attack pattern**: a poisoned IDE extension on a developer machine.

```bash
# List installed VS Code / Cursor / Windsurf extensions and their versions
code --list-extensions --show-versions 2>/dev/null
cursor --list-extensions --show-versions 2>/dev/null

# Review what auto-updated recently (extensions auto-update silently by default)
ls -lat ~/.vscode/extensions/ 2>/dev/null | head
ls -lat ~/.cursor/extensions/ 2>/dev/null | head
```

Things to check:
- Disable **automatic extension updates** for high-privilege editors (`extensions.autoUpdate: false`) so a compromised maintainer can't silently push a trojanized version to you.
- Audit extensions that request broad capabilities (terminal, file-system, network, secret access).
- Treat any extension that runs on `folderOpen` / startup as you would a postinstall script.

### IOCs

| Type | Value |
|---|---|
| Threat actor | TeamPCP (aka PCPcat, DeadCatx3, UNC6780) |
| Initial access vector | Poisoned VS Code extension on employee device |
| Impact | ~3,800 GitHub-internal repositories exfiltrated |
| Extortion | Source listed for sale at $50,000; leak threat if unsold |
| Malicious extension name | Not yet publicly disclosed (this advisory will be updated) |

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — closest analogue for "a tool inside my editor was hostile"; same rotation logic applies.
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Pin and review IDE extensions like any other dependency. Disable silent auto-update for editors that hold cloud/GitHub credentials. Prefer first-party / verified-publisher extensions, and watch for sudden ownership or maintainer changes — the same trust-transfer pattern that drove the [Amazon Q wiper](2025-07-amazon-q-wiper.md) and the [postmark-mcp backdoor](2025-09-postmark-mcp-backdoor.md).

## Sources
- [Help Net Security — TeamPCP breached GitHub's internal codebase via poisoned VS Code extension](https://www.helpnetsecurity.com/2026/05/20/github-breached-teampcp/)
- [The Record — GitHub confirms being hacked by TeamPCP, says customer data unaffected](https://therecord.media/github-confirms-teampcp-hack-customers-unaffected)
- [The Hacker News — GitHub Breached — Employee Device Hack Led to Exfiltration of 3,800+ Internal Repos](https://thehackernews.com/2026/05/github-investigating-teampcp-claimed.html)
- [Hackread — GitHub Breach: TeamPCP Steals 3,800 Repositories via VS Code Extension](https://hackread.com/github-breach-teampcp-repositories-vs-code-extension/)
- [SecurityAffairs — A Malicious VS Code Extension Just Breached GitHub's Internal Repositories](https://securityaffairs.com/192440/cyber-crime/a-malicious-vs-code-extension-just-breached-github-s-internal-repositories.html)
- [Phoenix Security — GitHub Internal Repository Breach via Poisoned VS Code Extension (May 2026)](https://phoenix.security/vs-code-extension-malware-github-breach-teampcp-2026/)
- [Cybernews — GitHub hacked after poisoned VS Code extension infects employee device](https://cybernews.com/security/github-vscode-extension-breach-sourcecode/)
