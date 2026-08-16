---
id: 2026-07-cursor-cli-worktree-pretrust-execution
title: "Cursor CLI ran untrusted repository code before the Workspace Trust prompt — and even with --sandbox enabled (patched)"
date_disclosed: 2026-08-10
last_updated: 2026-08-10
severity: high
status: patched
ecosystems: [cursor]
tools_affected: ["Cursor CLI (cursor-agent)"]
tags: [workspace-trust-bypass, sandbox-bypass, pre-trust-execution, rce, git-clone]
---

## TL;DR
Manifold Security found that starting Cursor's CLI agent (`cursor-agent`) with the `-w` (worktree) flag inside a cloned repository let the repo run an arbitrary shell command **before** Cursor's Workspace Trust prompt ever appeared — and the command still ran even when the user had explicitly passed `--sandbox enabled`. A single `git clone` plus `cursor-agent -w` was enough to execute attacker-controlled commands with the full privileges of the logged-in user: reading `~/.ssh`, stealing cloud credentials from the environment, opening a reverse shell, or writing persistence. Reported to Cursor 2026-07-20; patched in `cursor-agent` build **2026.07.23-e383d2b**, three days later. Publicly disclosed 2026-08-10.

## What happened
The attack vector was a normal, version-controlled config file: `.cursor/worktrees.json`. Per Manifold Security's own writeup: *"The command sat in a normal tracked file, .cursor/worktrees.json, so it arrived with an ordinary git clone."* When a developer ran Cursor's CLI agent with `-w` inside a repository containing a crafted `worktrees.json`, Cursor executed a setup command specified in that file **as part of worktree initialization — before the Workspace Trust dialog was shown**, and regardless of whether the sandbox flag was set. This is the same general class this repo already tracks as "AI coding tool auto-executes workspace config on open" (see [TrustFall](2026-05-trustfall-mcp-auto-execute.md) and the [git.exe binary-planting](2026-07-cursor-git-exe-autoexec.md) advisory) — a workspace-scoped file gets treated as executable configuration before trust is ever established — but here the specific bypass also defeats the explicit `--sandbox enabled` opt-in, which is a stronger claim than most entries in that cluster: a developer who took the extra step of requesting a sandbox was still exposed.

Cursor fixed the ordering in `cursor-agent` build **2026.07.23-e383d2b** (2026-07-23), so the Workspace Trust prompt now appears before any worktree setup command is permitted to run.

## Am I affected?
```bash
cursor-agent --version
```
- Any `cursor-agent` build **before 2026.07.23-e383d2b** is affected if you (or anyone on your team) use the `-w` / worktree flag against repositories you don't fully control, including forks, cloned PRs, or "run this coding challenge" repos.
- If you cloned and ran `cursor-agent -w` against an untrusted repository before 2026-07-23, treat your machine as potentially compromised: check `~/.ssh/authorized_keys` for unexpected entries, review shell history and cron/launch-agent persistence, and audit any cloud credentials present in your environment at the time.

## If you are affected
1. Upgrade `cursor-agent` to **≥ 2026.07.23-e383d2b** (or the latest release) immediately.
2. See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for triage and credential-rotation steps if you ran an untrusted repo with `-w` before patching.
3. Cross-reference with [GhostApproval](2026-07-ghostapproval-symlink-trust-boundary.md) and [TrustFall](2026-05-trustfall-mcp-auto-execute.md) — this is the same "workspace config auto-executes before trust is established" root cause recurring in Cursor specifically for the third time this repo tracks (after git.exe binary planting and the DuneSlide/hook-config cluster).

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Treat any AI-CLI flag that references "worktree," "workspace init," or similar as a code-execution primitive, not a convenience flag — never run it against a repository you haven't reviewed.

## Sources
- [Manifold Security — Cursor CLI Ran Untrusted Repository Code With the Sandbox Switched Off](https://www.manifold.security/blog/cursor-cli-worktree-pre-trust-execution) — primary technical disclosure: `.cursor/worktrees.json` mechanism, disclosure/patch timeline, exact patched build number.
- [Infosecurity Magazine — Cursor Security Bug Allowed Repositories to Execute Commands Pre Trust](https://www.infosecurity-magazine.com/news/cursor-security-bug-command/) — independent corroboration.
- [The Hacker News — ThreatsDay: GhostJacking AI Attacks, EtherHiding ClickFix, Cursor CLI Flaw + 17 More Stories](https://thehackernews.com/2026/08/threatsday-ghostjacking-ai-attacks.html) — roundup coverage confirming disclosure and patch timeline.
