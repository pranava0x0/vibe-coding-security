---
id: 2026-09-infostealers-target-coding-agent-tokens-mcp-configs-prompt-histories
title: "Commodity infostealers now collect your coding agent's local state — Gen Digital telemetry shows Amatera, Remus, CallbackBeaver, Djinn and five other families grabbing access/refresh tokens, MCP configs, conversation databases and prompt histories from Claude, Cursor, Codex, Cline, Continue, OpenCode, Gemini and Kilo installs"
date_disclosed: 2026-09-08
last_updated: 2026-09-18
severity: high
status: ongoing
ecosystems: [claude-code, cursor, codex, cline, continue, opencode, gemini-cli, kilo, windows, macos, infostealer]
tools_affected: ["Claude (Claude Code / Claude Desktop local data)", "Cursor", "OpenAI Codex", "Cline", "Continue", "OpenCode", "Gemini", "Kilo", "any IDE agent that stores tokens or MCP configuration on disk"]
tags: [infostealer, credential-theft, mcp, session-hijacking, prompt-history, vendor-telemetry, windows, macos, ongoing]
---

## TL;DR
Gen Digital's threat research (2026-09-08, a three-month Windows telemetry window plus macOS samples) reports that mainstream infostealer families have added **AI coding agents to their collection lists** next to browsers and crypto wallets: **Amatera** targets **Cline and Continue**; **Remus** targets **Claude, Cursor and OpenCode**; **CallbackBeaver** added **Cursor and Claude** (5,000+ samples in 30 days); BeeStealer, STG Stealer, HydraStealer, APEX Stealer and Otter Stealer are adopting the same rules, with "new AI agent collection rules appearing almost every day"; on macOS, **Djinn Stealer** collects from **Claude, Codex, Gemini, Cline, OpenCode and Kilo**. What they take is the agent's local state: **access and refresh tokens, account and subscription identifiers, MCP configuration files** (endpoints, headers, env vars and API keys for every connected tool), **conversation databases and prompt histories**, recently accessed files and project names — "both the means to access an account and the context needed to understand what is valuable behind it." Gen counted over 3.3 million protected users hitting infostealers in H1 2026. This is the collection side of the market Okta and Anthropic described ([stolen Claude sessions](2026-09-anthropic-claude-session-infostealer-hijack.md)); the fix is the same — short-lived scoped tokens, OS credential stores instead of files, nothing secret pasted into a prompt.

## What happened

**The finding.** Gen Digital (Norton/Avast/AVG telemetry): "The findings concern locally installed development agents, not a direct compromise of an AI model or agent." Over three months of Windows detections the researchers watched stealer families add dedicated collection routines for AI development tools, each naming the directories and files that specific agents write. The families and targets, as Gen lists them:

| Family | Targets |
|---|---|
| Amatera | Cline, Continue |
| Remus | Claude, Cursor, OpenCode |
| CallbackBeaver | Cursor, Claude (5,000+ samples in a 30-day window) |
| BeeStealer, STG Stealer, HydraStealer, APEX Stealer, Otter Stealer | adopting AI-agent rules |
| Djinn Stealer (macOS) | Claude, Codex, Gemini, Cline, OpenCode, Kilo |

**What the local state contains.** Gen's inventory of what a stealer archive from a developer machine now holds: access and refresh tokens; account identifiers, organisation ids and subscription information; **MCP configuration files** ("endpoints, headers, environment variables, API keys, or other authentication details for external tools," meaning "reusable secrets could expose source control, ticketing, databases, cloud resources, or collaboration services connected to the agent"); **prompt histories and transcripts** (developers "examine code, analyze logs, and solve incidents" in chat, so histories "may reveal source code, internal hostnames, repository names, deployment details, or secrets pasted during troubleshooting"); recently accessed files and project names. Gen's line: "In one archive, an attacker may obtain both the means to access an account and the context needed to understand what is valuable behind it."

**Why this is different from the browser-cookie era.** A browser session gets you one SaaS account. An agent's token gets you the agent's paid usage (the [Anthropic warning](2026-09-anthropic-claude-session-infostealer-hijack.md) was about exactly that drain), its MCP config gets you every system the agent was wired to — the [GitLab MCP PAT theft](2026-07-gitlab-mcp-account-takeover-cve-cluster.md) and [Claude Code MCP OAuth hijack](2026-06-claude-code-mcp-oauth-hijack.md) entries show what one MCP credential is worth — and its history tells the buyer which repo, host and secret to try first. Okta's analysis of a 5,871-machine stealer dump ([logged 2026-09-12](2026-09-anthropic-claude-session-infostealer-hijack.md)) already found replayable Anthropic, Cursor and OpenAI tokens for sale; Gen's report shows the harvesters that fill those dumps being updated for the purpose.

**Scale and confidence.** Gen reports monthly infostealer detections above 500,000 across its base and 3.3M+ affected users in H1 2026; the per-family AI-agent figures are Gen's own telemetry and are single-sourced by nature (vendor detection data). Cyber Security News (2026-09-09) and GBHackers republished the findings; The Hacker News' 2026-09-17 ThreatsDay roundup carried them as "Amatera and Remus malware now collecting access tokens, MCP configs, prompt histories from Cline, Continue, Claude, Cursor tools." Status **`ongoing`**: this is a standing capability in commodity malware, not an incident with an end.

## Am I affected?

If a machine that runs any of the listed agents had an infostealer infection (fake installer, cracked software, malicious npm/PyPI package, "free desktop app" ZIP), assume the agent's tokens and MCP configuration were taken. Know where your agents keep state:

```bash
# Where the agents' tokens / MCP configs / histories live (inspect permissions and contents; do not paste these into a chat)
ls -la ~/.claude/ ~/.claude.json ~/.cursor/ ~/.codex/ ~/.config/opencode/ ~/.gemini/ ~/.continue/ 2>/dev/null
ls -la ~/Library/Application\ Support/Claude/ ~/Library/Application\ Support/Cursor/User/globalStorage/ 2>/dev/null   # macOS
# MCP configs that hold secrets in plain text:
grep -l -iE 'token|api[_-]?key|secret|password' ~/.claude.json ~/.cursor/mcp.json ~/.codex/config.toml .mcp.json 2>/dev/null
# Cline / Continue (VS Code globalStorage) on macOS / Linux:
ls ~/.vscode/extensions/ 2>/dev/null | grep -iE 'cline|continue'
```

## If you are affected

- Revoke the agent's sessions from the vendor console (Anthropic, OpenAI, Cursor, Google) and sign back in; rotate **every** key referenced in MCP configuration files — that list is the blast radius. [`playbooks/if-an-mcp-server-was-malicious.md`](../playbooks/if-an-mcp-server-was-malicious.md) has the MCP credential inventory steps; [`playbooks/rotating-cloud-credentials.md`](../playbooks/rotating-cloud-credentials.md) and [`playbooks/if-your-github-pat-leaked.md`](../playbooks/if-your-github-pat-leaked.md) for what those configs usually point at.
- Read your own recent prompt history as an attacker would: any secret, hostname or customer data pasted there is now exposed and needs rotating or notifying.
- Clean or reimage the endpoint first; rotated credentials on an infected machine are stolen again.

## Prevention

- Prefer OS credential stores over file-based tokens where the agent supports it; use short-lived, scoped tokens for MCP servers and never long-lived personal tokens. [`prevention/credential-hygiene.md`](../prevention/credential-hygiene.md), [`prevention/mcp-hygiene.md`](../prevention/mcp-hygiene.md).
- Do not paste secrets into prompts; keep histories short or off for sensitive work; review agents' retention settings.
- Install AI tooling only from the vendor's own channel — the [fake "Claude Opus 5 Desktop"](2026-08-revstealer-fake-claude-opus5-desktop.md) and [fake Claude Code](2026-07-jscrambler-npm-preinstall-infostealer.md) lures are how these stealers arrive.

## Sources
- [Gen Digital — Infostealers Have Found a New Target: Your AI Agent](https://www.gendigital.com/blog/insights/research/infostealers-your-ai-agent) — primary; 2026-09-08; the family/target table, the data inventory, the 3.3M and 500K figures, the "means to access… and the context" quote, defensive guidance. Fetched 2026-09-18.
- [Cyber Security News — Hackers Target Claude, Cursor and Codex AI Agents to Steal Tokens and Prompt Histories](https://cybersecuritynews.com/ai-agents-2/) — 2026-09-09; independent republication with the "locally installed development agents, not a direct compromise" quote. Fetched 2026-09-18.
- [The Hacker News — ThreatsDay (2026-09-17)](https://thehackernews.com/2026/09/threatsday-self-rewriting-agents-800.html) — item "Infostealers Target AI Agents" naming Amatera/Remus and Cline/Continue/Claude/Cursor. Fetched 2026-09-18.
