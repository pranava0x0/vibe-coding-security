---
id: 2026-10-tensorlake-npm-shai-hulud-hostage-token-wipe
title: "tensorlake@0.5.144 (npm SDK for Tensorlake agent sandboxes/cloud, ~12–19K weekly downloads) shipped a Shai-Hulud/ChainDrop worm from the project's own release workflow with valid provenance (published 2026-10-08 01:12 UTC, pulled within ~2 hours): preinstall hook steals npm/GitHub/cloud/SSH/Vault/Kubernetes secrets and the config/MCP files of Claude, Cursor, Kiro, Windsurf and Zed, republishes the victim's packages, plants Claude Code and VS Code re-run files, and installs a `gh-token-monitor` that deletes the home directory if the stolen GitHub token is revoked — remove the monitor before rotating"
date_disclosed: 2026-10-08
last_updated: 2026-10-09
severity: critical
status: active
ecosystems: [npm, github-actions, claude-code, vscode, mcp]
tools_affected: [tensorlake, "tensorlake-native-* (six platform binary packages at 0.5.144)", "Claude Code (re-run persistence + ~/.claude.json read)", "VS Code (.vscode/tasks.json persistence)", "Cursor, Kiro, Windsurf, Zed (config/MCP files read)", "any npm or GitHub account whose token sat on an infected host"]
tags: [supply-chain, npm, shai-hulud, chaindrop, worm, credential-theft, ai-agent-config-theft, hostage-token, dead-man-switch, provenance, preinstall, claude-code-persistence]
---

## TL;DR
On **2026-10-08 at 01:12 UTC** npm recorded `tensorlake@0.5.144`, the TypeScript SDK for Tensorlake's agent sandboxes and cloud, built and published by the project's **own GitHub Actions release workflow** from a `main` branch that a repository-admin account had been committing a worm payload to since **2026-10-07 01:20 UTC** — so the tarball carried a **valid npm provenance attestation**. The payload is a Shai-Hulud/ChainDrop variant: it harvests developer and cloud secrets plus the config and MCP files of Claude, Cursor, Kiro, Windsurf and Zed; republishes packages the stolen npm token can publish; plants Claude Code and VS Code re-run files in reachable repositories; and installs a **`gh-token-monitor`** service whose dead-man switch deletes the user's home directory if the stolen GitHub token is revoked. Socket flagged it eleven minutes after publication, npm removed the version within about two hours, and the maintainers merged a revert-and-harden PR the same morning. If 0.5.144 ever installed with scripts enabled: **disable `gh-token-monitor` first, then rotate every credential.**

## What happened

**The package.** `tensorlake` is the npm SDK for Tensorlake, a platform for running agent applications and code sandboxes in the cloud — the kind of dependency an agent harness or vibe-coded backend adds to run model-written code. npm's download API reported **18,826 downloads in the week ending 2026-10-04**; Socket and Endor Labs cite "~12K weekly", SafeDep "about 106,000 monthly", Aikido "over 100,000" lifetime — all overall usage, not installs of the bad version. The repo has roughly 1,000 stars.

**How the bad version shipped.** The maintainers' post-incident PR #1016 (merged 2026-10-08) states the payload "was committed directly to `main` by a repo-admin account through the GitHub web UI" and "released by manually dispatching `publish_npm.yaml`, which signed it with Sigstore provenance." StepSecurity dates the first rogue commit to **2026-10-07 01:20 UTC** under a maintainer's name, with seven more commits over the following hours (one adding the `preinstall` hook), none through a pull request. SafeDep adds the commits were signed and the release workflow was manually started at **2026-10-08 00:08 UTC**; npm's `time` field puts the publish at **01:12:07 UTC**. Because the project's legitimate pipeline built it from its own branch, the package carried a **valid npm provenance attestation** — StepSecurity's point is that provenance shows where a build came from, not that the source is clean, so a provenance-based allow policy would not have blocked it. Six companion packages `tensorlake-native-*@0.5.144` were published in the same run; the PR and Endor Labs say no payload was found in them but they should be treated as part of the affected release. No source has published how the admin account was taken over.

**Timeline and removal.** Socket's scan flagged 0.5.144 at **01:23:10 UTC**, eleven minutes after publication; SafeDep flagged it within minutes too, and StepSecurity opened repo issue #1014 the same day. At this sweep the registry `/tensorlake/0.5.144` endpoint returned 404, `dist-tags.latest` was back at **0.5.143**, and the `time` field carried a `modified` stamp of 02:54 UTC — consistent with removal about an hour and forty minutes after publish. PR #1016 reverts `main` to the last clean commit, runs `npm ci --ignore-scripts` in every workflow, adds a tripwire that fails the build if a published manifest declares install scripts, bumps everything to **0.5.145**, and records that `main` now forbids admin bypass and requires signed commits and a second reviewer on the `npm` environment. 0.5.145 was not yet on the registry at this sweep; interim guidance is to pin **0.5.143**.

**Registry check 2026-10-09.** `tensorlake@0.5.145` was published 2026-10-08 20:24 UTC and is `latest`; `0.5.144` is gone from the package's versions map. The six `tensorlake-native-*` packages (linux-x64-gnu, linux-x64-musl, linux-arm64-gnu, linux-arm64-musl, darwin-arm64, win32-x64) are at `0.5.145` as `latest` but **still list `0.5.144`** in their version maps, as the maintainers' PR said they would until unpublished. Upgrade to 0.5.145 and keep the sibling check above until those versions are removed.

**What the payload targets (Socket, StepSecurity, SafeDep, Aikido).** A `preinstall` hook runs an obfuscated loader under the Bun runtime (the loader exits on CI runners, so developer workstations are the main target). It collects npm and GitHub tokens, AWS credentials (IMDS/ECS/Secrets Manager/SSM), HashiCorp Vault, Kubernetes service-account tokens and kubeconfigs, SSH keys, `.env` files, browser logins and wallets, and the configuration and MCP files of **Claude (`~/.claude.json`), Cursor, Kiro (`~/.kiro/settings/mcp.json`), Windsurf and Zed**. It has no hardcoded C2, resolving its endpoint through an Ethereum contract with a GitHub fallback (the same EtherHiding technique Unit 42 described for ChainDrop the same week). As a worm it republishes packages the stolen npm token can publish and commits to reachable repositories as a spoofed "claude" author, planting `.claude/settings.json` and `.vscode/tasks.json` so it re-runs when the project is opened in Claude Code or VS Code, plus a workflow that dumps repository secrets. Persistence is the **`gh-token-monitor`** service (a Linux systemd user service and `~/.config/gh-token-monitor/`, a macOS LaunchAgent, or a Windows logon scheduled task running `monitor.ps1`) that polls the stolen GitHub token; if the token is revoked, its handler deletes the user's home directory. New GitHub repositories carry the description "Shai-Hulud: Here We Go Again."

**Why it matters to vibe coders.** This is the first tracked Shai-Hulud wave whose harvest list and persistence are built *around* the AI coding agent: it reads Claude/Cursor/Kiro/Windsurf/Zed configs and MCP settings, and it writes Claude Code and VS Code auto-run files so opening the repo re-executes it. The provenance attestation is the second lesson — a signed, attested package from the real pipeline is still only as trustworthy as the branch it was built from.

## Am I affected?

```bash
# Did 0.5.144 (or a native sibling) resolve anywhere?
npm ls tensorlake 2>/dev/null | grep 0.5.144
grep -rn '"tensorlake"' package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null | grep 0.5.144
grep -rn 'tensorlake-native-.*0\.5\.144' . 2>/dev/null

# Persistence service (CHECK BEFORE you revoke any GitHub token)
ls ~/.config/gh-token-monitor/ 2>/dev/null                 # Linux
systemctl --user list-units 2>/dev/null | grep gh-token-monitor
launchctl list 2>/dev/null | grep -i gh-token-monitor      # macOS
schtasks /query 2>NUL | findstr /i gh-token-monitor        # Windows (cmd)

# Persistence / spread artefacts
find . -path '*/.claude/settings.json' -o -path '*/.vscode/tasks.json' 2>/dev/null
git log --all --format='%an %s' | grep -i '^claude '        # spoofed "claude" commits
```
Any match on 0.5.144 means secrets on that host should be treated as exposed. A `preinstall` ran during `npm install` unless `ignore-scripts` was set; CI-only installs were spared execution by the loader's CI check but any secret that job could read is still at risk.

## If you are affected
**Disable `gh-token-monitor` and delete its files before revoking any GitHub token** — revoking first can trigger the home-directory wipe. Then follow [if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md), [if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md), [if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md) and [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md). Rotate npm, GitHub, cloud, SSH, Vault, Kubernetes and wallet credentials and any AI-tool/MCP tokens in the harvested configs, hunt for new public repos described "Shai-Hulud: Here We Go Again" and unexpected `.claude`/`.vscode` files, and rebuild hosts you cannot confirm clean.

## Prevention
Set `ignore-scripts=true` in `.npmrc` and vet install hooks ([npm-hardening.md](../prevention/npm-hardening.md)); keep long-lived cloud/npm/GitHub tokens off developer and build hosts ([credential-hygiene.md](../prevention/credential-hygiene.md), [ci-cd-hardening.md](../prevention/ci-cd-hardening.md)); treat provenance as proof of origin, not safety ([supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)).

## Sources
- [StepSecurity — Tensorlake npm Package Compromised: A Worm With a Hostage Token That Wipes Your Machine If You Revoke It](https://www.stepsecurity.io/blog/tensorlake-npm-compromised-hostage-token-worm) (2026-10-08: rogue-commit timeline from 2026-10-07 01:20 UTC, provenance point, `gh-token-monitor` wipe, persistence paths, remediation order)
- [Socket — TensorLake npm SDK Compromised in ChainDrop Shai-Hulud Credential-Stealing Attack](https://socket.dev/blog/tensorlake-compromise) (2026-10-08: publish 01:12:07 UTC, flagged 01:23:10 UTC, ~12K weekly, harvest list incl. AI-tool configs, Ethereum C2 resolution, persistence)
- [SafeDep — tensorlake 0.5.144 npm Compromise Ships Mini Shai-Hulud](https://safedep.io/tensorlake-npm-compromise-mini-shai-hulud) (2026-10-08: ~106K monthly, `~/.claude.json` and `~/.kiro/settings/mcp.json` reads, 0.5.145 release, revert PR #1016, remediation order)
- [Aikido — tensorlake NPM package compromised with Shai Hulud worm](https://www.aikido.dev/blog/tensorlake-npm-package-compromised) (2026-10-08: ~20-hour repo-compromise window, crypto-extension targeting, dead-man switch)
- [Endor Labs — Tensorlake npm package compromised by Shai-Hulud](https://www.endorlabs.com/learn/tensorlake-npm-package-compromised-by-shai-hulud-in-latest-software-supply-chain-attack) (2026-10-08: six `tensorlake-native-*@0.5.144` siblings, ~12K weekly / ~1K stars, remediation)
- [The Hacker News — Tensorlake npm Package Compromised to Deliver Shai-Hulud Credential-Stealing Worm](https://thehackernews.com/2026/10/tensorlake-npm-package-compromised-to.html) (2026-10-08: synthesis of Socket + StepSecurity)
- [tensorlakeai/tensorlake PR #1016 — Revert the 0.5.144 supply-chain compromise and harden the npm release path](https://github.com/tensorlakeai/tensorlake/pull/1016) (maintainer statement: web-UI admin commit, manual workflow dispatch, Sigstore provenance, 0.5.145, ruleset hardening; merged 2026-10-08)
- [npm registry — tensorlake](https://registry.npmjs.org/tensorlake) (checked 2026-10-08: 0.5.144 endpoint 404, `latest` = 0.5.143, publish time 01:12:07Z); [npm downloads API — tensorlake](https://api.npmjs.org/downloads/point/last-week/tensorlake) (18,826 for week ending 2026-10-04)
- [Unit 42 — Evolution of Web3 in Cloud Supply Chain Attacks](https://unit42.paloaltonetworks.com/web3-cloud-supply-chain-attacks/) (2026-10-07: ChainDrop/Shai-Hulud EtherHiding C2 resolution, the technique this payload reuses)
