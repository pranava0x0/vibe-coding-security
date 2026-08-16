---
id: 2026-01-programdata-cross-user-config-trust
title: "CVE-2026-35603 — Claude Code, Cursor, Codex CLI, and Gemini CLI all load Windows system config from a folder any local user can write to"
date_disclosed: 2026-01-05
last_updated: 2026-08-11
severity: high
status: active
ecosystems: [claude-code, cursor, codex-cli, gemini-cli]
tools_affected: ["Anthropic Claude Code", "Cursor", "OpenAI Codex CLI", "Google Gemini CLI"]
tags: [privilege-escalation, windows, programdata, config-trust, hooks, cross-user, cve]
---

## TL;DR
Cymulate found that four major AI coding CLIs — Claude Code, Cursor, OpenAI Codex CLI, and Google Gemini CLI — all load machine-wide configuration on Windows from `C:\ProgramData\...`, a directory writable by any standard (non-administrative) local user by default. None of the four tools created their config subdirectory with restricted permissions or validated file ownership before loading it, so a low-privileged local attacker can drop a config file that runs commands in **any other user's session on the same machine — including an administrator's** — the next time that user launches the tool. **CVE-2026-35603** covers this class; only Anthropic has shipped a real fix (Claude Code ≥2.1.75). Cursor, OpenAI, and Google remain unresolved as of this sweep, with Google characterizing it as a documentation issue rather than a bug.

## What happened
Windows' `C:\ProgramData` is, by long-standing default, writable by any locally authenticated standard user — a well-known Windows administration gotcha, not something specific to these tools. Each of the four AI coding CLIs uses a subdirectory under `ProgramData` to store machine-wide (all-users) configuration that takes effect for every account on the machine:

| Tool | Config path | Execution primitive |
|---|---|---|
| Claude Code | `C:\ProgramData\ClaudeCode\managed-settings.json` | Hooks (session start) |
| Cursor | `C:\ProgramData\Cursor\hooks.json` | Hooks (prompt send) |
| OpenAI Codex CLI | `C:\ProgramData\openai\codex\config.toml` | `notify` command |
| Google Gemini CLI | `C:\ProgramData\gemini-cli\system-defaults.json` | Hooks (session start) |

None of the four pre-created their subdirectory with restricted ACLs at install time, and none validated the owner of the file before loading and executing it. The result: a low-privileged local user (or a process running as one, e.g. via a separate compromise) creates the tool's `ProgramData` subdirectory if it doesn't already exist, drops a config file wiring a hook or notify command to an attacker payload, and the payload executes with the privileges of **whoever next launches that tool on the machine** — no prompt, no warning, no elevation of the attacker's own privileges required. On a shared or multi-user Windows machine (common in enterprise VDI/terminal-server deployments), this is a straight path from any local account to an administrator's session.

**Disclosure and patch status per vendor:**
- **Anthropic** — disclosed 2026-01-05. **Fixed**: fully deprecated the vulnerable `C:\ProgramData\ClaudeCode\` path, relocated managed settings to a write-protected `Program Files` location in **Claude Code ≥2.1.75**, and proactively emailed affected enterprise customers ahead of the (breaking) migration.
- **Cursor** — disclosed 2026-01-12. Unresolved as of this sweep; no formal vendor response reported.
- **OpenAI** — disclosed 2026-02-16. Triaged but no fix committed as of this sweep.
- **Google** — disclosed via VRP. Google stated the issue would be "addressed as a documentation update," not a code fix.

This is a distinct root cause from this repo's existing "AI coding tool auto-executes workspace config on open" cluster (Claude Code CVE-2025-59536, Cursor CVE-2025-54136, Windsurf CVE-2026-30615, TrustFall, Amazon Q CVE-2026-12957, [GhostApproval](2026-07-ghostapproval-symlink-trust-boundary.md)) — those all involve a *per-repository* workspace config file executed without a trust gate when a folder is opened; this one is a *machine-wide, cross-user* config file loaded from an OS directory with permissive default ACLs, independent of any specific repository or workspace. Same broader lesson (a config file an AI CLI reads is treated as trusted without verifying who could have written it), different attack surface and blast radius (any user on the box, not just the one who opened a malicious repo).

## Am I affected?
```powershell
# Run as the account you normally use these tools with, on Windows
icacls "C:\ProgramData\ClaudeCode" 2>$null
icacls "C:\ProgramData\Cursor" 2>$null
icacls "C:\ProgramData\openai\codex" 2>$null
icacls "C:\ProgramData\gemini-cli" 2>$null
```
- If any of these directories exist and grant write access to `BUILTIN\Users` or `Everyone` (rather than only `Administrators`/`SYSTEM`), any local standard user on that machine can plant a persistence/privilege-escalation payload for the corresponding tool.
- **Claude Code**: check your version — `claude --version`. If `<2.1.75`, you're exposed; upgrade.
- **Cursor, Codex CLI, Gemini CLI**: currently exposed regardless of version on Windows, per this sweep's research — no vendor fix has shipped for these three.
- Primarily relevant on shared/multi-user Windows machines: VDI pools, terminal servers, shared build machines, or any box where more than one account can log in locally.

## If you are affected
1. Upgrade Claude Code to **≥2.1.75** immediately if you haven't already.
2. For Cursor, Codex CLI, and Gemini CLI on shared Windows machines, manually tighten the ACLs on the tool's `ProgramData` subdirectory to remove write access for standard users until a vendor fix ships (`icacls <path> /inheritance:r /grant:r "Administrators:(OI)(CI)F" "SYSTEM:(OI)(CI)F"`).
3. If you administer shared Windows machines running any of these tools, audit for unexpected files in the paths above — an existing malicious config is evidence of prior exploitation, not just exposure.
4. See [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for triage if you find evidence of exploitation.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ On any shared/multi-tenant Windows host, review ACLs on `C:\ProgramData` subdirectories for every AI CLI tool you deploy, not just the ones named here — this is a general Windows deployment pattern, and other tools may share the same default-permissive-ACL mistake.

## Sources
- [Cymulate — CVE-2026-35603: AI Coding Tools Privilege Escalation](https://cymulate.com/blog/cve-2026-35603-ai-coding-tools-privilege-escalation/) — primary research: all four affected tools, config paths, execution primitives, per-vendor disclosure/patch timeline.
- [SentinelOne Vulnerability Database — CVE-2026-35603](https://www.sentinelone.com/vulnerability-database/cve-2026-35603/) — independent corroboration: confirms Claude Code fixed version (≥2.1.75), affected-version detail.
