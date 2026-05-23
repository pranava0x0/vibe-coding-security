---
id: 2026-04-bitwarden-cli-shai-hulud-third-coming
title: "Bitwarden CLI backdoored — first supply-chain attack to hunt AI-coding-tool creds (April 2026)"
date_disclosed: 2026-04-22
last_updated: 2026-05-23
severity: critical
status: contained
ecosystems: [npm]
tools_affected: [bitwarden-cli, claude-code, cursor, codex-cli, any-mcp-user, any-node-project, ci-cd]
tags: [supply-chain, worm, credential-theft, ai-tool-targeting, mcp, teampcp, shai-hulud, dead-drop-c2]
---

## TL;DR
On **2026-04-22**, a malicious **`@bitwarden/cli` v2026.4.0** (the package has **~70K weekly / ~250K monthly downloads**) was published to npm and stayed live for **~90 minutes** (≈17:57–19:30 ET) before takedown — ~**334** downloads of the bad version. Beyond the usual multi-cloud credential harvesting + self-propagating npm worm, this payload shipped a **dedicated module that hunts authenticated AI coding assistants** — it specifically scrapes **AI-tool configuration and MCP-related files** (Claude Code, Cursor, Codex CLI). Researchers call it the **first documented supply-chain attack that explicitly targets AI coding assistant credentials.** Part of the **"Shai-Hulud: The Third Coming"** campaign attributed to **TeamPCP (UNC6780)** — the same actor behind the [Mini Shai-Hulud wave](2026-05-tanstack-mini-shai-hulud.md).

## What happened
TeamPCP backdoored `@bitwarden/cli` as one arm of an ongoing supply-chain campaign that also weaponized **Checkmarx** distribution channels (the "Shai-Hulud: The Third Coming" wave). The malicious `2026.4.0` was published via a compromised release path and self-described in commit strings as *"Shai-Hulud: The Third Coming."* Bitwarden confirmed the npm package compromise and stated its **investigation found no evidence that end-user vault data, production data, or production systems were accessed** — the blast radius is anyone who *installed the poisoned CLI*, not Bitwarden vault holders.

The payload is a multi-stage stealer-worm with several modules:

- **Multi-cloud credential harvester** across **six secret surfaces** — Azure, AWS, GCP, GitHub, npm tokens — plus **SSH material and shell history**.
- **AI-tooling collector (novel).** A module that specifically targets **authenticated AI coding assistants**: AI-tool configuration files and **MCP-related files** (e.g. Claude Code / Cursor / Codex CLI config and credentials). This is the headline first — malware that treats your logged-in AI dev tools as a credential store.
- **Self-propagating npm worm.** Re-infects **every npm package the victim's token can publish**, backdooring them in turn (the Shai-Hulud propagation model).
- **GitHub commit dead-drop C2** with **RSA-signed command delivery** — commands are fetched from attacker commits and verified by signature, so a takedown of one repo doesn't break control.
- **Authenticated-encryption exfiltration** designed to **survive repository seizure** (stolen data stays confidential even if the staging repo is recovered).
- **Shell RC persistence** (writes to `.bashrc` / `.zshrc`-style startup files).

This is a sibling of the [Nx Console compromise](2026-05-nx-console-vscode-compromise.md) (which scooped `~/.claude/settings.json`) and an escalation of the [AI-agent → AI-agent supply-chain](2026-02-cline-clinejection.md) pattern: the AI dev-tool credential surface is now a *first-class objective*, not incidental loot.

## Am I affected?
You are at risk if `@bitwarden/cli@2026.4.0` was installed (directly, via CI, or transitively) during the ~90-minute window on **2026-04-22**.

```bash
# Lockfile / install check (npm, pnpm, yarn)
grep -rn '"@bitwarden/cli"' package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null | grep '2026.4.0'
npm ls @bitwarden/cli 2>/dev/null | grep '2026.4.0'

# Globally installed?
npm ls -g @bitwarden/cli 2>/dev/null

# Did the worm read your AI-tool config? Review for unexpected access / modification.
ls -la ~/.claude/ ~/.codex/ ~/.cursor/ 2>/dev/null
grep -RIl . ~/.claude/settings.json ~/.config/claude 2>/dev/null

# Look for shell-RC persistence and dead-drop indicators
tail -n 20 ~/.bashrc ~/.zshrc 2>/dev/null
```

If `2026.4.0` is/was present: **assume every credential reachable from that host is compromised** — cloud keys (Azure/AWS/GCP), GitHub + npm tokens, SSH keys — **and** any API keys / MCP server tokens referenced by your AI-tool configs (Claude Code, Cursor, Codex). Rotate, then check whether your own npm packages were republished by the worm.

### IOCs

| Type | Value |
|---|---|
| Threat actor | TeamPCP (UNC6780) — "Shai-Hulud: The Third Coming" |
| Malicious package | `@bitwarden/cli` **v2026.4.0** (npm) |
| Live window | 2026-04-22, ≈17:57–19:30 ET (~90 min) |
| Downloads of bad version | ~334 |
| Targets | Azure/AWS/GCP, GitHub + npm tokens, SSH, shell history, **AI-tool config + MCP files** |
| C2 | GitHub commit **dead-drop**, RSA-signed command delivery |
| Persistence | shell RC files; npm worm republish of victim-publishable packages |
| Campaign siblings | Trivy (Mar), Checkmarx KICS / Jenkins AST Plugin, [Mini Shai-Hulud / TanStack](2026-05-tanstack-mini-shai-hulud.md) |

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md) — especially: check whether the worm republished your packages.
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — closest analogue for "my AI tool's credentials were harvested." Rotate every model API key and MCP server token referenced by `~/.claude`, `~/.codex`, `~/.cursor`, and re-review those files for attacker-planted hooks/servers.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — pin versions; use `--ignore-scripts`; cooldown before adopting fresh releases of credential-adjacent CLIs.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — don't leave long-lived cloud/GitHub/npm tokens on dev machines; treat logged-in AI tools as credential stores worth protecting.
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ Treat `npm install -g` of any security/credential tool as high-risk; prefer official signed binaries over the npm distribution where one exists.

## Sources
- [The Hacker News — Bitwarden CLI Compromised in Ongoing Checkmarx Supply Chain Campaign](https://thehackernews.com/2026/04/bitwarden-cli-compromised-in-ongoing.html)
- [Endor Labs — Shai-Hulud: The Third Coming — Inside the Bitwarden CLI 2026.4.0 Supply Chain Attack](https://www.endorlabs.com/learn/shai-hulud-the-third-coming----inside-the-bitwarden-cli-2026-4-0-supply-chain-attack) — module-by-module payload breakdown, AI-tool collector.
- [OX Security — Bitwarden CLI Compromised: Inside the Shai-Hulud Supply Chain Attack](https://www.ox.security/blog/shai-hulud-bitwarden-cli-supply-chain-attack/)
- [Socket — Bitwarden CLI Compromised in Ongoing Checkmarx Supply Chain Campaign](https://socket.dev/blog/bitwarden-cli-compromised)
- [Palo Alto Networks (Unit 42) — Bitwarden CLI Impersonation Attack Steals Cloud Credentials and Spreads Across npm Supply Chains](https://www.paloaltonetworks.com/blog/cloud-security/bitwardencli-supply-chain-attack/)
- [SecurityWeek — Bitwarden npm Package Hit in Supply Chain Attack](https://www.securityweek.com/bitwarden-npm-package-hit-in-supply-chain-attack/)
- [Cremit — Bitwarden CLI Hack (April 2026): How a 90-Minute npm Window Stole AWS, GCP, GitHub Tokens](https://www.cremit.io/blog/bitwarden-cli-supply-chain-attack-april-2026)
- [Bitwarden Community — Statement on Checkmarx Supply Chain Incident](https://community.bitwarden.com/t/bitwarden-statement-on-checkmarx-supply-chain-incident/96127) — vendor confirmation; no vault data accessed.
- [CSO Online — Supply-chain attacks take aim at your AI coding agents](https://www.csoonline.com/article/4167465/supply-chain-attacks-take-aim-at-your-ai-coding-agents.html) — the AI-coding-tool-targeting trend.
