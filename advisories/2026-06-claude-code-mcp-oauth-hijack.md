---
id: 2026-06-claude-code-mcp-oauth-hijack
title: "Claude Code MCP OAuth token hijack via malicious npm postinstall hook — Anthropic won't fix"
date_disclosed: 2026-04-10
last_updated: 2026-06-15
severity: high
status: active
ecosystems: [npm, claude-code, mcp, oauth]
tools_affected: [claude-code]
tags: [supply-chain, credential-theft, mcp, oauth, postinstall, config-poisoning, claude-code, no-patch]
---

## TL;DR

Mitiga Labs disclosed a 5-step attack chain where a **malicious npm package's `postinstall` hook** modifies `~/.claude.json` to intercept **MCP OAuth bearer tokens** (Jira, Confluence, GitHub, and any other MCP-connected OAuth service) via a localhost proxy. The hook **re-asserts itself on every Claude Code session start**, surviving manual URL correction. Reported to Anthropic April 10, 2026; **Anthropic declined to fix on April 12, 2026** ("out of scope"). No CVE assigned. Status: active — no patch planned.

## What happened

Mitiga Labs researchers disclosed a supply-chain attack targeting Claude Code's MCP OAuth token storage.

**5-step attack chain:**

1. **Malicious npm package installed.** A supply-chain attacker delivers a package (or trojanizes an existing one) whose `postinstall` script modifies `~/.claude.json` — Claude Code's runtime configuration file.

2. **`~/.claude.json` poisoned.** The hook injects two changes:
   - A `sessionStart` lifecycle hook pointing to an attacker-controlled script, which runs on every Claude Code session start.
   - Replacement entries for legitimate MCP server URLs (e.g., the Jira MCP, Confluence MCP, GitHub MCP) pointing to an attacker-controlled localhost proxy process.

3. **Localhost proxy intercepts OAuth tokens.** The attacker's proxy listens on a localhost port, proxies all MCP traffic to the real MCP server, and reads every `Authorization: Bearer <token>` header in plaintext before forwarding.

4. **Hook self-reasserts on startup.** Because the `sessionStart` hook runs on every Claude Code launch, it re-injects the proxy URL and hook configuration each session — manual correction of the MCP server URL is not durable.

5. **OAuth tokens exfiltrated.** Bearer tokens for all MCP-connected OAuth services (Jira, Confluence, GitHub, etc.) are captured and transmitted to the attacker.

**Key properties of the attack:**
- Requires only a malicious package installed via `npm install` — no other user interaction.
- The attack surface is `~/.claude.json`, a user-writable file that Claude Code trusts completely.
- The `sessionStart` hook that enables persistence is a designed Claude Code feature; there is no privilege-separation boundary between Claude Code's config and the local filesystem.
- Attackers gain OAuth tokens for **every MCP-connected OAuth service simultaneously** — if a developer has connected Jira, Confluence, GitHub, and Slack, all four token families are exfiltrated.

**Disclosure timeline:**
- **2026-04-10**: Mitiga Labs reported the issue to Anthropic.
- **2026-04-12**: Anthropic declined to issue a fix, classifying the issue as "out of scope."
- **2026-06 (public)**: Mitiga Labs published their findings.

**Anthropic's position:** The attack requires a malicious npm package to be installed first, which Anthropic treats as a pre-compromise state outside their threat model. However, the npm supply-chain ecosystem in mid-2026 — active campaigns including IronWorm, Hades, Phantom Gyp, Solana FakeFix, and the Miasma worm lineage — makes malicious `postinstall` hooks a realistic and ongoing threat rather than a theoretical precondition.

## Am I affected?

Any Claude Code user who:
- Runs `npm install` in untrusted repositories
- Has installed packages from compromised accounts (supply-chain compromise waves are ongoing)
- Has MCP servers connected via OAuth

```bash
# Check for unexpected hooks in ~/.claude.json
cat ~/.claude.json | python3 -m json.tool 2>/dev/null | grep -A10 '"hooks"'

# Look for localhost proxy MCP server URLs (unusual localhost port numbers)
cat ~/.claude.json | python3 -m json.tool 2>/dev/null | grep -E '"url".*localhost:[0-9]{4,5}'

# Check modification time of ~/.claude.json — was it changed around an npm install?
ls -la ~/.claude.json

# Full view of MCP server config
cat ~/.claude.json | python3 -m json.tool 2>/dev/null | grep -B2 -A10 '"mcpServers"'
```

**Indicators of compromise:**
- `~/.claude.json` modified at a time coinciding with an `npm install` run
- MCP server URLs pointing to `localhost` on unexpected port numbers
- Unexpected `hooks.sessionStart` entries in `~/.claude.json`
- Unfamiliar scripts running on Claude Code session start

## If you are affected

1. **Stop using Claude Code** until cleanup is complete.
2. **Revoke all MCP OAuth grants** — log in to each connected service (Jira, Confluence, GitHub, Slack, etc.) and revoke the OAuth authorization for Claude Code and each MCP server. Treat every bearer token the proxy could have seen as compromised.
3. **Remove and rebuild `~/.claude.json`:**
   ```bash
   mv ~/.claude.json ~/.claude.json.compromised.$(date +%s)
   # Reinstall each MCP server fresh via: claude mcp add <server>
   ```
4. **Identify the malicious package** — check `~/.npm/_logs/` and shell history for recent `npm install` runs that coincided with the `~/.claude.json` modification time.
5. **Review the exposure window** — determine how long the proxy ran and which MCP-authenticated actions Claude Code performed during that time (Jira issues read/written, GitHub repos accessed, etc.).
6. **Rotate credentials for every downstream service** the compromised MCP servers could have accessed.

## Prevention

- **Vet npm packages before installing.** Use `npm audit` and tools like [Socket.dev](https://socket.dev), [Snyk](https://snyk.io), or [Aikido](https://aikido.dev) to inspect packages for malicious `postinstall` hooks before running `npm install`.
- **Use `--ignore-scripts` for npm installs** in repos you don't fully trust: `npm install --ignore-scripts`. Note this does NOT block `binding.gyp` (see [Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md)).
- **Monitor `~/.claude.json` for unexpected changes.** Add it to file-integrity monitoring, or check its mtime after every `npm install`.
- **Audit MCP server URLs regularly.** Legitimate MCP server URLs should point to known addresses — not `localhost` on unusual ports.
- **Limit MCP OAuth scope.** Use read-only OAuth scopes where possible; don't grant full write access if the agent only needs to read.
- **No vendor fix is coming.** Since Anthropic has declined to fix the underlying trust model, defensive hygiene at the npm-install and config-monitoring layer is the only mitigation. This attack surface exists in all current Claude Code versions.

## Sources

- [SecurityWeek — Researchers Detail Claude Code MCP OAuth Token Hijacking Attack via Malicious npm Packages](https://www.securityweek.com/researchers-detail-claude-code-mcp-oauth-token-hijacking-attack-via-malicious-npm-packages/)
- [Cybersecurity News — Malicious npm Postinstall Hook Hijacks Claude Code MCP OAuth Tokens](https://cybersecuritynews.com/malicious-npm-postinstall-hook-hijacks-claude-code-mcp-oauth-tokens/)
- Cross-reference: [2026-06-solana-fakefix-campaign.md](2026-06-solana-fakefix-campaign.md) — current npm supply-chain wave that delivers `postinstall` hooks targeting AI-tool config
- Cross-reference: [2026-02-claude-desktop-extensions-rce.md](2026-02-claude-desktop-extensions-rce.md) — Anthropic's parallel "out of scope" response to DXT zero-click RCE; same pattern
- Cross-reference: [2025-08-claude-code-inverseprompt.md](2025-08-claude-code-inverseprompt.md) — broader Claude Code config-as-attack-surface history
- Cross-reference: [2026-04-bitwarden-cli-shai-hulud-third-coming.md](2026-04-bitwarden-cli-shai-hulud-third-coming.md) — first supply-chain malware to specifically hunt Claude Code/MCP credential files
