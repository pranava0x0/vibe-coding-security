---
id: 2026-10-unauthorized-codex-claude-code-relays-rewrite-cli-config-disable-sandbox-symantec
title: "Grey-market relays reinstall Codex and Claude Code with sandbox off and base URL pointed at third-party servers (Symantec, 2026-10-29)"
date_disclosed: 2026-10-29
last_updated: 2026-10-31
severity: high
status: ongoing
ecosystems: [codex, claude-code, npm, agent-config]
tools_affected: ["OpenAI Codex CLI installs whose ~/.codex config or OPENAI_BASE_URL points at a non-OpenAI endpoint", "Claude Code installs whose ~/.claude settings or ANTHROPIC_BASE_URL point at a non-Anthropic endpoint", "every secret, file and prompt an agent session sent through such an install"]
tags: [codex, claude-code, api-relay, grey-market, config-tampering, sandbox-disabled, environment-variables, credential-exposure, prompt-exposure, man-in-the-middle, symantec, no-cve, not-a-vulnerability]
---

## TL;DR
Symantec's Threat Hunter Team (2026-10-29) found a grey-market "relay" service that installs the genuine OpenAI Codex and Anthropic Claude Code CLIs from npm, then rewrites their configuration: Codex's sandbox set to full access with network enabled, Claude Code's base URL replaced, and user-scope `OPENAI_BASE_URL`, `CODEX_API_KEY`, `ANTHROPIC_BASE_URL` and `ANTHROPIC_AUTH_TOKEN` set to relay-issued values, so every prompt, file and secret the agent sends passes through the relay and every response the relay returns runs with the user's full privileges. About a dozen organisations since early 2026, mostly in mainland China with subsidiaries in South Korea, Taiwan and Malaysia; no abuse observed; not a vulnerability in either CLI. Check both tools' configuration and your user-scope environment for base URLs you did not set, and rotate anything that went through one.

## What happened

Symantec (Broadcom) published the report on 2026-10-29. Users in the affected organisations installed the real CLI through `npm`, then shortly afterwards ran a download-and-execute script from a lookalike domain. The script installs the genuine tool and applies the relay's changes, so the activity looks like an ordinary install. For Codex it edits the user config in `~/.codex`, setting the sandbox mode to full access and enabling network access for the write sandbox. For Claude Code it edits the user settings in `~/.claude`, replacing the base URL with a relay endpoint. It sets the four base-URL and key variables above at user scope so they persist across reboots, and it disables telemetry and error reporting. On at least one host the script logged the user out of their Anthropic session and cleared the existing authentication variables before installing relay-issued credentials.

What the relay can see and do, per Symantec: every prompt, file and secret sent to the agent; every response, which it could alter or fabricate; and, because the sandbox is off, a fabricated response could run commands with the user's full privileges. Persistent user-scope variables also expose the relay's credentials to other tools on the same machine. Symantec found no evidence that the operator has used this access, and states that Codex and Claude Code behave as designed once their configuration has been changed; there is no CVE and nothing for either vendor to patch. Delivery was manual (users ran the script); no exploit or automated delivery was observed. The affected sectors listed are industrial automation, electronics, semiconductors, pharmaceuticals, shipping, tyre manufacturing, petrochemicals and data centres.

SecurityWeek's 2026-10-30 roundup carries the report as a Symantec and Carbon Black warning about "a grey-market relay that reroutes genuine Codex and Claude Code CLIs through third-party servers". Dark Reading's coverage returns 403 to this sweep and was not read.

**Why it matters here.** This corpus already has the two halves of this story: [third-party LLM API routers caught injecting tool calls and harvesting credentials](2026-04-llm-router-malicious-intermediary-attacks.md) and [Claude Code's China proxy fingerprint](2026-07-claude-code-china-proxy-fingerprint.md), which is about the market this relay serves. The new fact is that the intermediary now ships as an installer that also turns the sandbox off, and that the artefact it leaves is configuration, not code: a scanner looking for a malicious package finds a clean `@openai/codex` and a clean `@anthropic-ai/claude-code`. The same shape applies to any "cheaper API" or "unblocked access" installer a developer runs on a work machine, whatever country it targets.

## Am I affected?

The relay's footprint is a base URL and a key you did not set. Read-only checks:

```bash
# Claude Code: settings and environment
grep -nE 'BASE_URL|AUTH_TOKEN|apiBaseUrl|baseUrl' ~/.claude/settings.json ~/.claude/settings.local.json 2>/dev/null
env | grep -E '^(ANTHROPIC_BASE_URL|ANTHROPIC_AUTH_TOKEN|OPENAI_BASE_URL|CODEX_API_KEY)='
# Codex: config and sandbox settings
grep -nE 'base_url|sandbox|network_access|api_key' ~/.codex/config.toml 2>/dev/null
# Where the variables persist (macOS/Linux shells; check the ones you use)
grep -nE 'ANTHROPIC_BASE_URL|OPENAI_BASE_URL|CODEX_API_KEY|ANTHROPIC_AUTH_TOKEN' ~/.zshrc ~/.zprofile ~/.bashrc ~/.bash_profile ~/.profile 2>/dev/null
```

```powershell
# Windows: user-scope environment variables
Get-ItemProperty HKCU:\Environment | Select-Object ANTHROPIC_BASE_URL, ANTHROPIC_AUTH_TOKEN, OPENAI_BASE_URL, CODEX_API_KEY
```

A base URL that is not the vendor's own endpoint, a Codex sandbox set to full access that you did not choose, or an API key you did not create means an agent session on this machine ran through a third party. An enterprise gateway your organisation deployed on purpose will match too; confirm against your approved configuration before treating it as a finding. Also look back: a `curl | bash` or `iwr | iex` run right after an `npm install` of either CLI in your shell history is the delivery pattern Symantec describes.

## If you are affected

1. Remove the relay's base URL and keys from the config files and the user environment, and reset Codex's sandbox and network settings to the defaults. Sign out of both CLIs and sign back in with your own account.
2. Treat everything the agent touched as seen by the relay: rotate provider keys, cloud credentials, tokens in `.env` files the agent read, and anything pasted into a prompt. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
3. Because the sandbox was off and responses could be fabricated, review what the agent executed while the relay was configured, not only what it read.

## Prevention

- Install AI CLIs only through the official package names and never run a post-install script a third party supplies; an "accelerator" that asks for `curl | bash` after `npm install` is the whole attack.
- Pin egress: an allow-list of approved AI endpoints for developer machines turns a silent relay into a connection failure.
- Audit `~/.claude`, `~/.codex` and user-scope variables in fleet checks; configuration drift is the only indicator this leaves.
- [credential-hygiene](../prevention/credential-hygiene.md), [agent-sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [Symantec Threat Hunter Team — Sandbox Flipped to 'Danger-Full-Access': Unauthorized AI Relays Create Risk for Organizations](https://www.security.com/threat-intelligence/openai-claude-unauthorized-relays) — fetched 2026-10-31: 2026-10-29; the dozen organisations, countries and sectors, "at least early 2026"; the `~/.codex` and `~/.claude` edits, the four user-scope variables, telemetry disabled, the logout-and-reissue case; what the relay sees; no abuse observed; not a vulnerability; the npm-then-script delivery; detection and mitigation list.
- [SecurityWeek — In Other News: Anthropic Breach Dispute, UEFI Flaw Hits Most Servers, Cloudflare AI Data Leak](https://www.securityweek.com/in-other-news-anthropic-breach-dispute-uefi-flaw-hits-most-servers-cloudflare-ai-data-leak/) — fetched 2026-10-31: 2026-10-30; the roundup item attributing the grey-market relay warning to Symantec and Carbon Black.
- Not read: Dark Reading's article (403 to this sweep).
