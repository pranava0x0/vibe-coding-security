---
id: 2026-05-cursor-open-folder-autorun
title: "Cursor 'Open-Folder' autorun + Git-hook RCE (CVE-2026-26268, CVE-2026-22708, CVE-2026-32202, May 2026)"
date_disclosed: 2026-05-08
last_updated: 2026-05-18
severity: high
status: patched
ecosystems: [cursor, vscode]
tools_affected: [cursor]
tags: [cve, rce, workspace-trust, git-hooks, autorun, cursor, vscode-task]
---

## TL;DR
A cluster of Cursor IDE vulnerabilities disclosed in May 2026 turn the act of opening — or just cloning — a repo into silent RCE on the developer's machine. **CVE-2026-26268 (Novee, high severity)** — a malicious `.git/hooks/pre-commit` inside a *bare* repo embedded in a parent repo triggers when the agent autonomously runs Git commands. **CVE-2026-22708** — shell built-ins bypass the Cursor Auto-Run allowlist. **CVE-2026-32202 (Oasis Security)** — Workspace Trust is disabled by default, so a malicious `.vscode/tasks.json` with `runOptions.runOn: folderOpen` runs the moment a developer browses a project. All patched in **Cursor 2.5**. Together they mean: do not open or `git clone` an untrusted repo on a vulnerable Cursor install.

## What happened

### CVE-2026-26268 — Git-hook RCE in nested bare repos (Novee)
Git supports "bare repositories" — folders containing only the `.git` directory metadata with no working tree. Git also runs hook scripts in `.git/hooks/*` for events like commit and checkout. Cursor's AI agent, by design, autonomously runs `git commit` / `git checkout` / `git status` inside repos it doesn't control.

The exploit: a malicious repo embeds a *bare* repo inside a normal-looking directory. When the agent (or even a user) issues a git operation that traverses into that directory, Git resolves the inner bare repo first and runs its `pre-commit` / `post-checkout` / `post-merge` hook. The hook executes outside the agent's reasoning chain and outside the user's field of view — there is no prompt, no permission dialog, no agent log entry.

### CVE-2026-22708 — Auto-Run Mode allowlist bypass
Cursor's Auto-Run mode lets the agent execute commands matching an allowlist without prompting. Researchers found that **shell built-ins** (`eval`, `exec`, `source`, `.`) were not properly accounted for, letting the agent run arbitrary code by wrapping it in a built-in even when the underlying command wasn't on the allowlist.

### CVE-2026-32202 — Workspace Trust off by default (Oasis Security)
VS Code added Workspace Trust to mitigate the long-known `.vscode/tasks.json` `runOn: folderOpen` autorun problem. Cursor inherited the task-runner code but shipped with **Workspace Trust disabled by default**. Result: opening any folder containing a malicious `.vscode/tasks.json` runs the task immediately, in the user's context, with their cloud keys / PATs / SaaS sessions.

## Am I affected?

```bash
# Cursor version
cursor --version 2>/dev/null
# Vulnerable: any version < 2.5

# Audit: does Workspace Trust default off?
# In Cursor: Settings → search "Workspace Trust" → confirm "Enabled" after upgrade.

# Inbound exposure check on any repo you've touched recently:
find ~/code -type f -name 'tasks.json' -path '*.vscode/*' \
  -exec grep -l 'runOn.*folderOpen' {} \; 2>/dev/null

# Look for nested bare repos in cloned repos
find . -type d -name 'HEAD' -path '*/objects/../HEAD' 2>/dev/null
# or simpler: find . -type f -name 'HEAD' -exec grep -l '^ref: refs/heads' {} \;
```

### IOCs / artifacts

| Type | Value |
|---|---|
| CVE — Git-hook RCE | `CVE-2026-26268` (Novee) |
| CVE — Auto-Run bypass | `CVE-2026-22708` |
| CVE — Workspace Trust default | `CVE-2026-32202` (Oasis Security) |
| Fixed in | **Cursor 2.5** |
| Malicious-pattern files | `.git/` inside a non-root directory; `.vscode/tasks.json` with `runOptions.runOn: folderOpen` |

## If you are affected
1. **Upgrade Cursor to 2.5** or later.
2. After upgrade, **enable Workspace Trust** explicitly (`"security.workspace.trust.enabled": true`) and set `"task.allowAutomaticTasks": "off"`.
3. Before opening any unknown repo, open it in a disposable container or VM. The same applies to `git clone` followed by `code` / `cursor`.
4. If you opened or cloned an untrusted repo on a pre-2.5 Cursor: assume any credential reachable from your home directory is compromised. Rotate cloud creds, GitHub PATs, npm tokens, SSH keys. Review shell history and recent processes for unexpected activity.

## Why this matters for vibe coders
Cursor is the most-used agentic IDE among vibe coders. These bugs let a maliciously crafted repo (e.g., from a GitHub trending project, a "starter template" link in a tutorial, an MCP-returned URL, or a worm-planted `.claude/` setup) execute code on your machine **without a single prompt or permission dialog**. The "open this repo and let the agent figure it out" workflow is exactly the attack surface.

This also chains with the [PyTorch Lightning Mini Shai-Hulud advisory](2026-04-pytorch-lightning-compromise.md): that worm specifically plants `.vscode/tasks.json` with `runOn: folderOpen` in victim repos. Pre-Cursor-2.5, that re-fires on every collaborator who opens the repo.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Settings to harden Cursor:
  - `"security.workspace.trust.enabled": true`
  - `"task.allowAutomaticTasks": "off"`
  - `"git.autorepositoryDetection": false` (prevents auto-discovery of nested repos)
  - Disable autorun of git hooks for unknown repos (configure `core.hooksPath` to a curated dir).
→ Treat `git clone` of an unknown repo as untrusted-data ingestion. Clone first inside a container / VM and inspect before opening in your real editor.

## Sources
- [Oasis Security — Cursor "Open-Folder" Autorun Vulnerability Exposes Developers to Silent Code Execution](https://www.oasis.security/blog/cursor-security-flaw)
- [Novee — CVE-2026-26268: How an AI Coding Agent Can Run Exploits in Cursor IDE](https://novee.security/blog/cursor-ide-cve-2026-26268-git-hook-arbitrary-code-execution/)
- [Hackread — Cursor AI IDE vulnerability allows code execution via hidden Git hooks](https://hackread.com/cursor-ai-ide-vulnerability-code-execution-git-hooks/)
- [BleepingComputer — Cursor AI editor lets repos "autorun" malicious code on devices](https://www.bleepingcomputer.com/news/security/cursor-ai-editor-lets-repos-autorun-malicious-code-on-devices/)
- [Infosecurity Magazine — Cursor Autorun Flaw Lets Repositories Execute Code Without Consent](https://www.infosecurity-magazine.com/news/cursor-autorun-flaw-repos-execute/)
- [Cybersecurity News — Cursor AI Coding Agent Vulnerability Allow Attackers to Execute Code on Developer's Machine](https://cybersecuritynews.com/cursor-ai-coding-agent-vulnerability/)
- [SentinelOne — CVE-2026-22708: Cursor AI Code Editor RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-22708/)
- [NVD — CVE-2026-32202](https://nvd.nist.gov/vuln/detail/CVE-2026-32202)
- [Pillar Security — The Agent Security Paradox: When Trusted Commands in Cursor Become Attack Vectors](https://www.pillar.security/blog/the-agent-security-paradox-when-trusted-commands-in-cursor-become-attack-vectors)
- [Help Net Security — Default Cursor setting can be exploited to run malicious code on developers' machines](https://www.helpnetsecurity.com/2025/09/11/cursor-ai-editor-vulnerability/)
