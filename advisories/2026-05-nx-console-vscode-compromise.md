---
id: 2026-05-nx-console-vscode-compromise
title: "Nx Console VS Code extension compromised — nrwl.angular-console 18.95.0 (May 2026)"
date_disclosed: 2026-05-18
last_updated: 2026-05-31
severity: critical
status: contained
ecosystems: [vscode, npm, github]
tools_affected: [vscode, cursor, windsurf, nx-console, claude-code, any-ide-extension-user]
tags: [supply-chain, ide-extension, credential-theft, teampcp, mini-shai-hulud, dev-tool, provenance-abuse, cisa-kev, cve]
---

## TL;DR
On **2026-05-18**, a trojanized build of the **Nx Console** VS Code extension (`nrwl.angular-console` **v18.95.0**, ~**2.2M installs**) was published to the Visual Studio Marketplace and was live for only **~18 minutes** (12:30–12:48 UTC). Within seconds of *any* workspace opening, it pulled a **498 KB credential-stealer** hidden in a **dangling orphan commit inside the official `nrwl/nx` GitHub repo** and exfiltrated GitHub/npm/AWS/Vault/Kubernetes/1Password secrets — and notably **`~/.claude/settings.json`** — over HTTPS, the GitHub API, and DNS tunneling. The maintainer was compromised because their GitHub token leaked in the [TanStack / Mini Shai-Hulud wave](2026-05-tanstack-mini-shai-hulud.md) a week earlier. This is the **same poisoned extension** a GitHub employee installed, leading to the [TeamPCP exfiltration of ~3,800 GitHub-internal repos](2026-05-teampcp-github-breach.md). **Now tracked as CVE-2026-48027**; **CISA added it to the Known Exploited Vulnerabilities catalog on 2026-05-27** (federal-agency remediation deadline **2026-06-10**). **Patch: upgrade Nx Console to ≥ 18.100.0** (clean release).

## What happened
The May 11 [Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md) wave (TeamPCP / UNC6780) harvested credentials across the ecosystem; one stolen set belonged to an **Nx contributor**. On **2026-05-18** the attacker used that contributor's **GitHub token** to push `nrwl.angular-console@18.95.0` to the VS Code Marketplace — pivoting the campaign from package registries into the **IDE-extension channel**.

The extension activated on `folderOpen` (immediately, on any project) and fetched a **498 KB obfuscated payload** stored as a **dangling orphan commit hidden in the legitimate `nrwl/nx` repo** — a blind spot, since the bytes live in a trusted GitHub repo but aren't reachable from any branch. The payload is a multi-stage **credential stealer / supply-chain poisoning tool** that harvests:

- **GitHub** tokens, **npm** tokens, **AWS** keys, **HashiCorp Vault** secrets, **Kubernetes** configs, **1Password** data, and
- **AI coding assistant config** — specifically `~/.claude/settings.json` — one of the first supply-chain payloads explicitly written to scoop up AI-tool credentials/config.

Exfil ran over **three channels**: HTTPS, the GitHub API, and **DNS tunneling**. Per StepSecurity the payload also carries **Sigstore/SLSA provenance-minting** capability, so harvested npm tokens can republish packages with a green "verified provenance" badge (cf. the [May 19 self-mint wave](2026-05-mini-shai-hulud-may19-wave.md)).

The Nx team pulled the rogue publish within minutes (reports say **~11–18 min** of exposure). Because VS Code extensions **auto-update silently by default**, even a short window reaches many machines — Nx analytics suggest **6,000+** installs got it. On **2026-05-21** Nx confirmed a developer was compromised via the **TanStack supply-chain attack**, leaking the GitHub credential that enabled this pivot; **OpenAI, Mistral AI, and Grafana Labs** were also caught in the same fallout.

**This is the upstream of the [GitHub internal-repo breach](2026-05-teampcp-github-breach.md):** a GitHub employee who installed this extension version became the foothold TeamPCP used to exfiltrate ~3,800 internal repositories.

> Not to be confused with the **2025** [Nx `s1ngularity`](2025-08-nx-s1ngularity.md) attack, which poisoned the `nx` **npm package** (not the VS Code extension). Same project, different distribution channel, ~9 months apart.

## Am I affected?
You are at risk if you had Nx Console installed with auto-update on between **2026-05-18 12:30 and 12:48 UTC**, or if you manually installed `18.95.0`.

```bash
# Is the bad version present? (VS Code / Cursor / Windsurf)
code --list-extensions --show-versions 2>/dev/null    | grep -i 'nrwl.angular-console'
cursor --list-extensions --show-versions 2>/dev/null  | grep -i 'nrwl.angular-console'

# Inspect the on-disk extension folder for 18.95.0
ls -d ~/.vscode/extensions/nrwl.angular-console-18.95.0* 2>/dev/null
ls -d ~/.cursor/extensions/nrwl.angular-console-18.95.0* 2>/dev/null

# Look for DNS-tunneling / outbound bursts and Claude config reads around the window
grep -RIl 'settings.json' ~/.claude 2>/dev/null   # confirm what config existed to be stolen
```

If `18.95.0` is/was present: **assume every credential reachable from that machine is compromised** — GitHub, npm, AWS, Vault, Kubernetes, 1Password, and your `~/.claude` config and any tokens it referenced.

### IOCs

| Type | Value |
|---|---|
| **CVE** | **CVE-2026-48027** (assigned 2026-05-27) |
| **CISA KEV** | **Added 2026-05-27** — federal-agency remediation deadline **2026-06-10** |
| Threat actor | TeamPCP (PCPcat / DeadCatx3 / UNC6780) |
| Malicious package | `nrwl.angular-console` (Nx Console) **v18.95.0** |
| Clean version | **≥ 18.100.0** |
| Channel | VS Code Marketplace (auto-update, silent) + Open VSX |
| Window | 2026-05-18, ~12:30–12:48 UTC on VS Code Marketplace (~11–18 min); ~36 min on Open VSX |
| Payload | ~498 KB obfuscated stealer in a **dangling orphan commit in `nrwl/nx`** |
| Trigger | `folderOpen` (runs on any workspace open) |
| Targets | GitHub, npm, AWS, Vault, Kubernetes, 1Password, **`~/.claude/settings.json`** |
| Exfil | HTTPS + GitHub API + DNS tunneling |
| Initial access | Nx contributor GitHub token leaked in [Mini Shai-Hulud / TanStack wave](2026-05-tanstack-mini-shai-hulud.md) |
| Downstream impact | [GitHub internal-repo breach (~3,800 repos)](2026-05-teampcp-github-breach.md); OpenAI / Mistral AI / Grafana Labs in fallout |

## If you are affected
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — closest analogue for "a tool inside my editor was hostile."
→ Rotate anything referenced by `~/.claude/settings.json` (model API keys, MCP server tokens, hook commands), and re-review that file for attacker-planted hooks.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ **Disable silent extension auto-update** on any editor that holds cloud/GitHub credentials (`"extensions.autoUpdate": false`), pin extension versions, and treat an extension that runs on `folderOpen`/startup like a `postinstall` script. A green provenance/SLSA badge is **identity, not integrity** — see the [May 19 self-minted-provenance wave](2026-05-mini-shai-hulud-may19-wave.md).

## Sources
- [The Hacker News — Compromised Nx Console 18.95.0 Targeted VS Code Developers with Credential Stealer](https://thehackernews.com/2026/05/compromised-nx-console-18950-targeted.html)
- [The Hacker News — GitHub Internal Repositories Breached via Malicious Nx Console VS Code Extension](https://thehackernews.com/2026/05/github-internal-repositories-breached.html)
- [StepSecurity — Nx Console VS Code Extension Compromised](https://www.stepsecurity.io/blog/nx-console-vs-code-extension-compromised)
- [BleepingComputer — GitHub links repo breach to TanStack npm supply-chain attack](https://www.bleepingcomputer.com/news/security/github-links-repo-breach-to-tanstack-npm-supply-chain-attack/)
- [Aikido — GitHub Breached via VS Code Extension](https://www.aikido.dev/blog/github-breached-vs-code-extension)
- [OpenAI — Our response to the TanStack npm supply chain attack](https://openai.com/index/our-response-to-the-tanstack-npm-supply-chain-attack/)
- [CISA — Supply Chain Compromises Impact Nx Console and GitHub Repositories (2026-05-28)](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories) — bundled the Nx Console and Megalodon alerts
- [CISA — Three Known Exploited Vulnerabilities Added to Catalog (2026-05-27)](https://www.cisa.gov/news-events/alerts/2026/05/27/cisa-adds-three-known-exploited-vulnerabilities-catalog) — CVE-2026-48027 KEV-listed alongside CVE-2026-45321 (TanStack) and CVE-2026-8398 (DAEMON Tools)
- [SecurityAffairs — U.S. CISA adds Daemon Tools, TanStack, and Nx Console flaws to its Known Exploited Vulnerabilities catalog](https://securityaffairs.com/192776/security/u-s-cisa-adds-daemon-tools-tanstack-and-nx-console-flaws-to-its-known-exploited-vulnerabilities-catalog.html)
- [SC Media — CISA adds Daemon Tools, TanStack, and Nx Console compromised versions to KEV catalog](https://www.scworld.com/brief/cisa-adds-daemon-tools-tanstack-and-nx-console-flaws-to-known-exploited-vulnerabilities-catalog)
- [Infosecurity Magazine — GitHub Breach Traced to Malicious 'Nx Console' VS Code Extension](https://www.infosecurity-magazine.com/news/github-breach-nx-console-vs-code/)
