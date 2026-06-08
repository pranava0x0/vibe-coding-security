---
id: 2026-06-miasma-wave5-microsoft-azure-github
title: "Miasma Wave 5 — 73 Microsoft Azure GitHub repos + mantine-datatable compromised; payload auto-fires via Claude Code / Cursor / Gemini CLI (June 2026)"
date_disclosed: 2026-06-05
last_updated: 2026-06-07
severity: critical
status: active
ecosystems: [npm, github]
tools_affected: [Claude Code, Cursor, Gemini CLI, VS Code, any project repo open in an AI coding assistant; npm packages in icflorescu/mantine-datatable family; Azure, Azure-Samples, Microsoft, MicrosoftDocs GitHub orgs]
tags: [supply-chain, worm, credential-theft, miasma-lineage, github-repo-poisoning, ai-tool-config, self-propagating]
---

## TL;DR

**Wave 5 of the Miasma/Shai-Hulud worm family** hit **73 Microsoft GitHub repositories** (across the Azure, Azure-Samples, Microsoft, and MicrosoftDocs GitHub organizations) on **2026-06-05**, plus **5 mantine-datatable repositories**, via a compromised contributor's GitHub account. Unlike prior waves that spread through the npm registry, Wave 5 **skips the registry entirely** and plants a 4.3 MB payload runner directly into source repositories, wired to auto-execute via **5 developer tools: Claude Code, Gemini CLI, Cursor, VS Code, and the npm test hook**. Opening a poisoned repository in any of these tools triggers a full credential harvest — no `npm install` required.

## What happened

On **2026-06-05**, attackers leveraged a previously compromised contributor account (a credential stolen during the Phantom Gyp / binding.gyp wave 4 campaign from June 3–4) to push malicious commits to Microsoft's Azure/durabletask repository. GitHub subsequently **disabled 73 repositories** across four Microsoft GitHub organizations:

- `Azure`
- `Azure-Samples`
- `Microsoft`
- `MicrosoftDocs`

Concurrently, the same actor pushed malicious commits to five repositories in the **`icflorescu`** namespace (author of mantine-datatable):

- `mantine-datatable`
- `mantine-contextmenu`
- `next-server-actions-parallel`
- `mantine-datatable-v6`
- `mantine-contextmenu-v6`

### Attack technique: "registry bypass" via GitHub source-repo poisoning

Miasma Wave 5 introduces a significant escalation over prior waves:

- **No npm registry involvement.** Prior waves (Red Hat @redhat-cloud-services, Phantom Gyp/binding.gyp) published malicious npm packages. Wave 5 **commits directly to the GitHub source repository** — bypassing npm entirely and any registry-side protections (provenance checks, malware scanning).
- **Multi-tool auto-execution hooks.** The malicious commit plants a **4.3 MB payload runner** and wires it as an automatic execution hook for five developer tools:
  1. **Claude Code** (`.claude/` config / hooks)
  2. **Gemini CLI**
  3. **Cursor** (`.cursor/` hooks)
  4. **VS Code** (`.vscode/tasks.json`)
  5. **npm test script** (`package.json` test hook)

Any developer who **opens the compromised repository in any of these tools** — without running `npm install` — will trigger the payload.

### What the payload does

The payload is a lightly reskinned Miasma/Shai-Hulud descendant (Greek-mythology theming; same credential-targeting scope as prior waves):

1. **Credential harvesting:** AWS/GCP/Azure IAM creds, Kubernetes configs (`~/.kube/config`), Docker credentials, GitHub tokens, npm tokens, SSH keys, RubyGems/PyPI publish tokens, password manager secrets, AI tool API keys.
2. **AI tool config targeting:** specifically targets Claude Code settings, Cursor config, Gemini CLI config — the attacker-controlled repository files register themselves as trusted tool configurations.
3. **Self-propagation:** uses stolen npm/GitHub tokens to publish poisoned versions of packages the victim maintains and to push to other repos the victim has write access to.
4. **GitHub Actions injection:** plants `.github/workflows/*.yml` files for persistence — same `base64 -d | bash` pattern as [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md).

### Vibe-coding-specific risk: AI-tool auto-execution

The most novel and dangerous capability of Wave 5 for vibe coders is the **AI coding assistant trigger**. When a developer with Claude Code, Cursor, or Gemini CLI opens a compromised repository:

- The tool's session-start or project-open hook fires the payload runner
- The developer never runs `npm install` — standard supply-chain hygiene (`--ignore-scripts`, lockfile integrity) is **irrelevant**
- The attack requires only that the developer **clone and open the repo**

This is a direct extension of the technique first seen in [TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md) (zero-width Unicode in `.cursorrules`/`CLAUDE.md`) and the binding.gyp wave's GitHub Actions injection, but now lands via a **legitimate maintainer's own commit history** (stolen GitHub account), making the commit appear trusted in `git log`.

### Attribution / lineage

Wave 5 is confirmed Miasma-lineage (same payload, same Greek-mythology markers, same C2 patterns as [Wave 3 — Red Hat](2026-06-miasma-redhat-cloud-services-compromise.md) and [Wave 4 — Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md)). The credential chain is traceable: the compromised contributor account used for the Microsoft Azure commit was almost certainly a token stolen during Wave 4 or the earlier [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md) / [GlassWorm](2025-10-glassworm-vscode-worm.md) harvest.

## Am I affected?

```bash
# Check if you have any of the compromised repos in your local clone list
git remote -v | grep -E "azure/durabletask|mantine-datatable|mantine-contextmenu|next-server-actions-parallel"

# Check for malicious .claude/ or .cursor/ config added since 2026-06-04
git log --since="2026-06-04" --all --oneline -- .claude/ .cursor/ .vscode/tasks.json package.json

# Check for the 4.3MB payload runner file (look for large unexpected JS files committed)
git log --since="2026-06-04" --all --diff-filter=A --name-only | grep -E "\.(js|mjs|cjs)$"

# Check for unexpected GitHub Actions workflows added
git log --since="2026-06-04" --all --oneline -- .github/workflows/

# Check AI tool config files for zero-width Unicode (TrapDoor technique)
grep -rP "[\x{200B}-\x{200D}\x{FEFF}\x{00AD}]" .claude/ .cursor/ .cursorrules CLAUDE.md 2>/dev/null
```

**High risk if you:**
- Recently cloned or `git pull`'d from any Microsoft Azure, Azure-Samples, Microsoft, or MicrosoftDocs GitHub repo
- Cloned or opened any mantine-datatable family repo after 2026-06-04
- Have an AI coding assistant (Claude Code, Cursor, Gemini CLI, VS Code) configured to auto-run hooks on project open
- Maintain npm packages and had your GitHub token exposed in any prior Shai-Hulud/Miasma/Megalodon/GlassWorm wave

## If you are affected

1. **Rotate all credentials** reachable from the machine where you opened the compromised repo: GitHub tokens, npm tokens, cloud IAM keys, SSH keys, AI tool API keys.
2. **Audit `.claude/`**, `.cursor/`, `.vscode/tasks.json`, `CLAUDE.md`, `.cursorrules` for unauthorized entries.
3. **Check GitHub Actions workflows** for bot-authored single-file changes: `git log --all --author="build-bot\|auto-ci\|pipeline-bot" --since="2026-06-01"`.
4. **Audit npm packages** you maintain for unexpected versions published since 2026-06-04.
5. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — steps apply even without a postinstall hook, since the payload executes at project-open.

## Prevention

- **Keep AI coding assistant hooks locked down.** Never grant auto-execute permissions to session-start hooks for untrusted repositories. Review `.claude/`, `.cursor/`, `.vscode/tasks.json`, `CLAUDE.md` whenever you clone or pull from a new source.
- **Diff agent-config files on every `git pull`** — `git diff HEAD~1 .claude/ .cursor/ CLAUDE.md .cursorrules` before opening the project in your AI tool.
- **Require signed commits** on protected branches of your own repos. An unsigned commit from a contributor account on a security-sensitive file is a red flag.
- **Review workflow changes carefully.** Any `.github/workflows/*.yml` change authored by a bot-named account or containing `base64 -d | bash` should be rejected immediately.
- **Pin GitHub Actions to commit SHA** — see [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Assume stolen credentials cascade.** If your token appeared in any prior Miasma/GlassWorm/Megalodon wave, assume Wave 5 may already have used it.

## Sources

- [The Hacker News — "Miasma Worm Hits 73 Microsoft GitHub Repositories in Major Supply Chain Attack"](https://thehackernews.com/2026/06/miasma-worm-hits-73-microsoft-github.html) — primary disclosure; 73-repo count, 4-org breakdown, AI-tool trigger detail.
- [The Hacker News — "IronWorm and New Miasma Worm Variant Hit npm in Supply Chain Attacks"](https://thehackernews.com/2026/06/ironworm-and-new-miasma-worm-variant.html) — registry-bypass technique, mantine-datatable repos.
- [StepSecurity — "Miasma npm Supply Chain Attack: Self-Spreading Worm via Phantom Gyp"](https://www.stepsecurity.io/blog/binding-gyp-npm-supply-chain-attack-spreads-like-worm) — payload runner mechanics, 5-tool auto-exec hooks, IOC list.
- [Snyk — "Node-gyp Supply Chain Compromise"](https://snyk.io/blog/node-gyp-supply-chain-compromise-self-propagating-npm-worm-binding-gyp/) — Wave 4/5 scope, Miasma lineage, affected package tracking.
- [Snyk Vulnerability DB — Embedded Malicious Code in weavedb-sdk (SNYK-JS-WEAVEDBSDK-17146541)](https://security.snyk.io/vuln/SNYK-JS-WEAVEDBSDK-17146541) — specific malicious version IOC.
- Cross-reference: [2026-06-phantom-gyp-miasma-wave4.md](2026-06-phantom-gyp-miasma-wave4.md) — Wave 4 (binding.gyp) from which the compromised contributor credentials originated.
- Cross-reference: [2026-06-miasma-redhat-cloud-services-compromise.md](2026-06-miasma-redhat-cloud-services-compromise.md) — Wave 3 (Red Hat @redhat-cloud-services).
- Cross-reference: [2026-05-megalodon-github-actions-mass-campaign.md](2026-05-megalodon-github-actions-mass-campaign.md) — Megalodon GitHub Actions injection; same `.github/workflows/*.yml` base64-bash payload shape.
- Cross-reference: [2025-10-glassworm-vscode-worm.md](2025-10-glassworm-vscode-worm.md) — GlassWorm credential harvest that almost certainly fed the contributor-token pool exploited here.
