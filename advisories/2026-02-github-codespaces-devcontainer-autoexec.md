---
id: 2026-02-github-codespaces-devcontainer-autoexec
title: "GitHub Codespaces auto-executes devcontainer.json / tasks.json / settings.json on repo open — Microsoft calls it 'by design' (no fix, no CVE)"
date_disclosed: 2026-02-04
last_updated: 2026-07-29
severity: high
status: active
ecosystems: [github, vscode, devcontainers]
tools_affected: [github-codespaces, vscode]
tags: [rce, workspace-trust, devcontainer, auto-execute, wont-fix, supply-chain]
---

## TL;DR
Orca Security researchers found that **GitHub Codespaces** auto-executes several workspace-defined configuration files the instant a repository or pull request is opened — no confirmation dialog, no workspace-trust gate — via three separate mechanisms: `.devcontainer/devcontainer.json`'s `postCreateCommand`, `.vscode/tasks.json`'s `folderOpen`-triggered tasks (enabled by VS Code's default `task.allowAutomaticTasks: "on"` setting), and shell-startup variable injection via `.vscode/settings.json`. Opening a malicious repository, or reviewing a malicious pull request in Codespaces, is enough to run arbitrary code with the developer's own GitHub token and cloud credentials. Microsoft/GitHub reviewed the finding and confirmed the behavior is **"by design,"** relying on Codespaces' existing "trusted repository" controls as the only mitigation — no patch, no CVE. This is a sixth documented instance of this repo's tracked "AI coding tool auto-executes workspace config on open" systemic class, backfilled into this sweep after going untracked here since its February 2026 disclosure.

## What happened
Orca Security's research (published 2026-02-04) documented that GitHub Codespaces — the cloud-hosted, VS Code-based development environment tightly integrated with GitHub, Copilot, and Copilot Chat — respects several VS Code configuration files automatically on container creation and folder open, without first establishing that the workspace is trusted:

1. **`.devcontainer/devcontainer.json`** — the `postCreateCommand` (and related lifecycle hooks) runs automatically the moment a Codespace is created from a repository, executing whatever shell command the file specifies.
2. **`.vscode/tasks.json`** — tasks marked to run `"folderOpen"` execute automatically because VS Code ships with `task.allowAutomaticTasks` defaulted to `"on"`.
3. **`.vscode/settings.json`** — shell-startup variables (e.g. `PROMPT_COMMAND` on Linux/bash shells) can be injected to run commands the first time a terminal opens in the Codespace.

Because Codespaces provisions each session with the developer's live GitHub token and often cloud credentials pre-wired for CI-style workflows, any of these three paths gives an attacker code execution with that same access the instant a developer opens an untrusted repository — or reviews a pull request from an untrusted contributor in Codespaces, a workflow many maintainers use routinely. Orca specifically calls out **maintainers reviewing PRs in Codespaces** as the highest-value target: opening a PR that only modifies `.devcontainer/` or `.vscode/` config is enough, no code-review red flag in the "real" source files required.

**Microsoft's response:** Orca reports Microsoft/GitHub reviewed the finding and classified the behavior as **"by design,"** pointing to Codespaces' existing trusted-repository/trusted-owner controls as the intended mitigation rather than committing to change the auto-execution behavior itself. No CVE was assigned, and no patch has shipped as of this writing.

This is the sixth entry in this repo's tracked systemic class of "AI coding tool reads a workspace config file and spawns processes before establishing workspace trust" — joining [Claude Code CVE-2025-59536](2025-08-claude-code-inverseprompt.md), Cursor's `.cursor/` auto-run (CVE-2025-54136), [Windsurf's zero-click MCP RCE](2026-05-windsurf-zero-click-mcp-rce.md), [TrustFall](2026-05-trustfall-mcp-auto-execute.md), and [Amazon Q Developer's CVE-2026-12957](2026-06-amazon-q-mcp-workspace-rce.md). GitHub Codespaces differs from the other five in that the attack surface is VS Code's own long-standing task/devcontainer automation rather than an AI-agent-specific MCP config — but the blast radius (a developer's live GitHub token and cloud credentials, triggered by opening a folder) and Microsoft's "won't fix, it's by design" response put it squarely in the same category.

## Am I affected?
- If you use GitHub Codespaces (or open untrusted repositories/PRs in local VS Code with Codespaces-style devcontainer support), any repository you haven't personally authored is a potential attack vector the moment you open it or create a Codespace from it.
```bash
# Before opening an unfamiliar repo's Codespace, inspect these files for anything unexpected:
cat .devcontainer/devcontainer.json 2>/dev/null | grep -A2 -i "postCreateCommand\|postStartCommand\|onCreateCommand"
cat .vscode/tasks.json 2>/dev/null | grep -B2 -A5 '"folderOpen"'
cat .vscode/settings.json 2>/dev/null | grep -i "prompt_command\|terminal.integrated"
```
- Check your local VS Code's automatic-task setting: `Preferences → Settings → search "allowAutomaticTasks"`. Setting it to `"off"` disables the `tasks.json`/`folderOpen` vector (but not `devcontainer.json`'s lifecycle hooks).

## If you are affected
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — if you opened an untrusted repo/PR in Codespaces and suspect your GitHub token was used maliciously.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — never open an unfamiliar repository's Codespace, or review an untrusted PR in Codespaces, on an account holding production-scoped credentials.
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

## Why this matters for vibe coders
This is the same "git clone → code execution" shape this repo tracks repeatedly across AI coding tools, except here the vendor is Microsoft/GitHub itself and the mechanism predates the current wave of AI-agent-specific MCP auto-execution bugs — VS Code's `tasks.json`/`devcontainer.json` automation has quietly been an auto-execute-on-open surface all along. A "won't fix, by design" response from a major vendor is itself a fact worth knowing before you assume opening any repository in Codespaces is safe by default.

## Sources
- [Orca Security — Hacking GitHub Codespaces: RCE & Supply Chain Risks](https://orca.security/resources/blog/hacking-github-codespaces-rce-supply-chain-attack/) — primary disclosure: technical root cause for all three auto-execution vectors, Microsoft's "by design" response, publish date 2026-02-04.
- [SecurityWeek — VS Code Configs Expose GitHub Codespaces to Attacks](https://www.securityweek.com/vs-code-configs-expose-github-codespaces-to-attacks/) — independent corroboration of the finding and vendor response.
