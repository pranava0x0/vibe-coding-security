---
id: 2026-05-claude-code-mcp-traffic-hijacking
title: "Claude Code MCP OAuth token interception via npm postinstall config rewrite (Mitiga Labs)"
date_disclosed: 2026-05
last_updated: 2026-06-10
severity: high
status: active
ecosystems: [npm, mcp, ai-agents]
tools_affected: [Claude Code (any version with dynamic MCP authorization), any MCP server using OAuth token grant flow]
tags: [mcp, oauth, credential-theft, npm, postinstall, persistence, anthropic-out-of-scope, claude-code]
---

## TL;DR

**Mitiga Labs** found that a malicious npm package's `postinstall` hook can silently rewrite MCP server URLs in **`~/.claude.json`** — Claude Code's local config — replacing legitimate MCP server endpoints with attacker-controlled proxies. When Claude Code subsequently runs an OAuth authorization flow, the attacker intercepts the OAuth token before it reaches the legitimate MCP server. Tokens are stored **in plaintext** in `~/.claude.json` and can be harvested directly or intercepted mid-flow. A **persistence mechanism** restores the malicious URL if the user edits it or rotates the token. Reported to Anthropic April 10, 2026; Anthropic responded April 12 that this was **"out of scope"** — citing user consent to install the malicious package as a prerequisite. No patch planned; no CVE assigned.

## What happened

Mitiga Security Labs researchers identified that Claude Code stores MCP server configurations and OAuth tokens in plaintext in `~/.claude.json`. This file is readable and writable by any process running as the same user — including npm `postinstall` hooks from newly installed packages.

### Attack mechanism

1. The victim installs a malicious npm package (typosquat, compromised legitimate package, or social-engineered install).
2. The package's `postinstall` script reads `~/.claude.json`, locates configured MCP server URLs (Jira, Confluence, GitHub, etc.), and replaces them with attacker-controlled proxy URLs.
3. The next time Claude Code performs an OAuth authorization flow against the impersonated server, the attacker's proxy intercepts the authorization code or access token before forwarding to the real server — the user may see no error.
4. **Persistence**: the hook also registers a file-watcher or periodic restore task that reverts the config to the malicious URL if the user manually edits it or rotates the token.

The attack requires only that the victim run `npm install` on the same machine where Claude Code is installed with OAuth-capable MCP servers configured. No root access is needed, and no vulnerability in Claude Code itself is exploited — the attack operates entirely within normal filesystem permissions.

### Anthropic's "out of scope" determination

Anthropic's April 12 response categorized the attack as requiring the user's prior consent to install the malicious package, placing it outside Anthropic's threat model. The determination means:
- No in-product warning when `~/.claude.json` is modified by a third-party process
- No integrity check on MCP server URLs at authorization time
- No detection of unexpected file-watchers targeting the config file
- Full detection and response burden falls on enterprise security teams and individual developers

### Affected tokens and services

OAuth tokens stored in `~/.claude.json` that can be intercepted include any MCP server configured with **OAuth 2.0 Dynamic Client Registration** per the MCP spec. Commonly configured services:
- Jira, Confluence (Atlassian OAuth)
- GitHub (GitHub OAuth App or Fine-Grained PAT flows)
- Slack, Linear, Notion, HubSpot, and any other OAuth-capable MCP server

The attack surface is growing as more MCP servers adopt OAuth authorization flows per the MCP specification (introduced late 2025).

## Am I affected?

```bash
# Check if ~/.claude.json has MCP server configurations
ls -la ~/.claude.json 2>/dev/null

# Print all configured MCP server names and URLs
cat ~/.claude.json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    servers = data.get('mcpServers', {})
    for name, cfg in servers.items():
        url = cfg.get('url', cfg.get('serverUrl', '(no url)'))
        print(f'{name}: {url}')
except: pass
" 2>/dev/null

# Check when ~/.claude.json was last modified
stat ~/.claude.json 2>/dev/null | grep -i modify

# Audit recently installed npm packages for postinstall scripts
# (run this in the directory where you last ran npm install)
cat package-lock.json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    pkgs = data.get('packages', {})
    for name, info in pkgs.items():
        scripts = info.get('scripts', {})
        if 'postinstall' in scripts or 'install' in scripts:
            print(name, scripts.get('postinstall', scripts.get('install', '')))
except: pass
" 2>/dev/null
```

**You are at risk if:**
- You have Claude Code installed with any MCP server configured with OAuth authorization on the same machine.
- You installed any npm package on that machine in the past 30–60 days, particularly anything adjacent to AI tooling, developer utilities, or security tooling.
- The modification timestamp on `~/.claude.json` does not match when you last changed it.

## If you are affected

1. **Inspect `~/.claude.json`** for MCP server URLs that you did not configure or that point to unexpected domains.
2. **Revoke all OAuth tokens** for every connected MCP service (Jira, Confluence, GitHub, Slack, etc.) and re-authorize only after verifying server URLs are correct.
3. **Kill any file-watcher processes** that may be monitoring `~/.claude.json`: check `ps aux | grep claude.json` and any unusual `inotifywait` or `fswatch` processes.
4. **Audit recently installed npm packages** for suspicious `postinstall` scripts — especially anything installed in the 30 days before you noticed the issue.
5. Set `chmod 600 ~/.claude.json` to restrict future writes.
6. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- **Treat `~/.claude.json` as a credential file**, not a config file — it contains OAuth tokens and should be protected the same way you protect `~/.npmrc`, `~/.pypirc`, or `~/.aws/credentials`.
- **Audit npm packages before installing**: use Socket (`socket scan`) or `npm audit` and inspect `postinstall` scripts in unfamiliar packages.
- **Run `npm install` in isolated environments** (containers, VMs, sandboxed Claude Code sessions) when evaluating unfamiliar packages — keep AI-tool config directories out of scope.
- **Hash-pin or version-pin dependencies** and diff lockfile changes before installing.
- **Monitor `~/.claude.json` for unexpected modification**: add a `DIGEST=$(sha256sum ~/.claude.json)` check to your shell's `precmd` hook or a simple cron job.
- See [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Sources

- [SecurityWeek — "Claude Code MCP Traffic Can Be Hijacked Via Malicious npm Package"](https://www.securityweek.com/claude-code-mcp-traffic-can-be-hijacked-via-malicious-npm-package/) — Primary disclosure; Mitiga Labs research, attack mechanism, OAuth interception chain, Anthropic "out of scope" response.
- [CyberSecurityNews — "Malicious npm Package Hijacks Claude Code MCP Traffic to Steal OAuth Tokens"](https://cybersecuritynews.com/malicious-npm-package-hijacks-claude-code-mcp-traffic/) — Independent confirmation; persistence mechanism, affected services, enterprise detection recommendations.
- Cross-reference: [2026-02-sandworm-mode-npm-worm.md](2026-02-sandworm-mode-npm-worm.md) — SANDWORM_MODE injects a malicious MCP server entry via npm Stage-2 payload; independent discovery of the same `~/.claude.json` MCP-URL rewrite primitive.
- Cross-reference: [2026-04-bitwarden-cli-shai-hulud-third-coming.md](2026-04-bitwarden-cli-shai-hulud-third-coming.md) — First supply-chain malware specifically hunting MCP files and Claude Code config as a credential target; the read-target precursor to this write-target attack.
- Cross-reference: [2026-05-trapdoor-cross-ecosystem-stealer.md](2026-05-trapdoor-cross-ecosystem-stealer.md) — TrapDoor npm `postinstall` rewrites `.cursorrules`/`CLAUDE.md` for AI-config persistence; same delivery mechanism against a different config file.
