---
id: 2026-06-symjack-ai-coding-agent-mcp-symlink
title: "SymJack — symlink hijacking tricks AI coding agents into registering attacker-controlled MCP servers (June 2026)"
date_disclosed: 2026-06-10
last_updated: 2026-06-16
severity: high
status: mitigated
ecosystems: [mcp, claude-code, cursor, copilot, ai-agents]
tools_affected: [claude-code, cursor, github-copilot, google-antigravity, grok-build, windsurf]
tags: [symlink, mcp, agent-config-poisoning, filesystem-attack, supply-chain, one-click-rce]
---

## TL;DR

**SymJack** (Adversa AI, disclosed 2026-06-10) is a new attack class against AI coding agents: a malicious repository embeds a **symlink** that makes an innocent-looking project path (e.g., `tools/config-backup.json`) resolve at the filesystem level to the developer's MCP configuration file (e.g., `~/.claude/mcp.json`). When the developer approves what looks like a routine `cp` command from their AI agent, the symlink redirects the write into the MCP config, registering an **attacker-controlled MCP server**. On next agent restart, that server runs **unsandboxed with full user privileges**. Anthropic silently hardened Claude Code; Cursor, GitHub Copilot, Google Antigravity, and Grok Build have shipped patches. **No CVE assigned.**

## What happened

On **2026-06-10**, Adversa AI published research on **SymJack** — a symlink-based attack that exploits a fundamental gap between what AI coding agents *display* to developers for approval and what the filesystem *actually does* when the approved command runs.

**Attack anatomy:**

1. **Attacker plant:** A malicious repository (or a pull-request to an existing repo) includes a symlink at a benign-sounding path — e.g., `tools/config-backup.json → ../../../.claude/mcp.json`. The symlink target resolves to the victim's global MCP configuration file.

2. **Agent trigger:** The developer opens the repo and asks their AI coding agent to "set up the project" or "copy the default config." The agent proposes a `cp` command to write a template file to `tools/config-backup.json`. It displays both source and destination — both look innocuous.

3. **Developer approval:** The developer approves the `cp`. Because Unix `cp` follows symlinks by default, the write goes to `~/.claude/mcp.json` (or its equivalent), appending or overwriting MCP server definitions with attacker-controlled entries.

4. **MCP server registration:** On next agent restart (or within the same session if the agent reads its MCP config dynamically), the attacker-defined MCP server is loaded and runs arbitrary code with full user account privileges.

**Target MCP configuration paths by agent:**

| Agent | MCP config path |
|---|---|
| Claude Code | `~/.claude/mcp.json` |
| Cursor | `~/.cursor/mcp.json` |
| Windsurf | `~/.codeium/windsurf/mcp_config.json` |
| GitHub Copilot (VS Code) | workspace `.vscode/mcp.json` or user-level MCP settings |
| Google Antigravity | `~/.antigravity/mcp.json` |

**Why existing defenses miss it:**

- The developer explicitly approves the operation — there is no silent background write
- The permission display shows the symlink path (`tools/config-backup.json`), not the resolved target (`~/.claude/mcp.json`)
- Agent sandboxing typically enforces write ACLs against the *displayed* path, not the *resolved* path
- `--ignore-scripts` and similar flags are irrelevant — this is a filesystem symlink, not a script
- Static linters do not flag symlinks inside repo archives unless explicitly configured to do so

**Scope of affected agents:** Adversa AI's PoC reproduced successful MCP server registration against Claude Code, Cursor, GitHub Copilot (VS Code workspace MCP), Google Antigravity, and Grok Build. All agents relied on the apparent file path for the approval dialog rather than the resolved symlink target.

**Vendor responses:**
- **Anthropic:** Silently hardened Claude Code (agent now resolves symlinks before displaying paths in approval dialogs). No CVE, no public advisory.
- **Cursor, GitHub Copilot, Google Antigravity, Grok Build:** Patches shipped; see respective changelogs.
- **Windsurf (Codeium):** Patch pending at time of disclosure.

## Am I affected?

Check for unexpected symlinks in repositories you've recently cloned or worked in:

```bash
# Find symlinks in any cloned repo that resolve outside the repo root
find . -type l | while read link; do
  target=$(readlink -f "$link" 2>/dev/null)
  echo "$link -> $target"
done | grep -v "^$(pwd)"   # flag anything resolving outside repo root

# Check your MCP configs for unexpected server entries
cat ~/.claude/mcp.json 2>/dev/null
cat ~/.cursor/mcp.json 2>/dev/null
cat ~/.codeium/windsurf/mcp_config.json 2>/dev/null

# Check when MCP config files were last written
ls -la ~/.claude/mcp.json ~/.cursor/mcp.json 2>/dev/null
```

If any symlink in a recently cloned repository resolves to a path outside the repository root — especially inside `~/.claude/`, `~/.cursor/`, `~/.config/`, or any agent-config directory — **treat the repository as malicious and audit your MCP configuration immediately.**

## If you are affected

1. **Audit MCP config files** (`~/.claude/mcp.json`, `~/.cursor/mcp.json`, etc.) for unexpected server entries — unknown names, localhost ports you did not configure, or remote URLs.
2. **Remove unexpected MCP server entries** and restart your agent.
3. **Rotate all credentials** accessible via your MCP setup if unexpected entries were present — the attacker's MCP server ran with your full user privileges and may have read tokens, SSH keys, cloud credentials, or other secrets.
4. **Audit shell history and cloud audit logs** for commands or API calls you didn't initiate.
5. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md).

## Prevention

- **Never clone and immediately act on an untrusted repository.** Run `find . -type l` (list all symlinks) before any agent-assisted project setup or file-copy operation.
- **Verify symlink targets before approving file operations:** `readlink -f <path>` to confirm the resolved target is where you think it is.
- **Restrict MCP config write access:** set `chmod 600 ~/.claude/mcp.json` and monitor for unexpected modifications (`inotifywait -m ~/.claude/mcp.json` on Linux).
- **Isolate agent sessions for untrusted repositories:** run the agent in a container or ephemeral VM where `~/.claude/mcp.json` is either absent or scoped to a throwaway configuration.
- **Keep MCP config files in version control** and diff them after any agent-assisted operation in a new repository.
- See [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).

## Sources

- [SecurityWeek — 'SymJack' Attack Turns AI Coding Agents Into Supply Chain Attack Delivery Systems](https://www.securityweek.com/symjack-attack-turns-ai-coding-agents-into-supply-chain-attack-delivery-systems/) — incident coverage, six affected agents, vendor responses.
- [Adversa AI — Top Agentic AI Security Resources (June 2026)](https://adversa.ai/blog/top-agentic-ai-security-resources-june-2026/) — vendor disclosure context (Rony Utevsky / Adversa AI, primary researcher).
- [OffSeq Threat Radar — SymJack Attack Turns AI Coding Agents Into Supply Chain Attack Delivery Systems](https://radar.offseq.com/threat/symjack-attack-turns-ai-coding-agents-into-supply--f70aaebc) — threat-intel summary.
