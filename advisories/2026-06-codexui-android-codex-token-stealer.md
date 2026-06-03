---
id: 2026-06-codexui-android-codex-token-stealer
title: "codexui-android npm — OpenAI Codex auth-token stealer (June 2026)"
date_disclosed: 2026-06-01
last_updated: 2026-06-03
severity: high
status: active
ecosystems: [npm, android]
tools_affected: [openai-codex, codex-cli]
tags: [supply-chain, credential-theft, npm, android, ai-coding-tool, token-theft, openai]
---

## TL;DR
**`codexui-android`** (~29K weekly npm downloads) silently exfiltrates the OpenAI Codex OAuth auth blob (`~/.codex/auth.json`) to **`sentry.anyclaw.store/startlog`** on every `postinstall`. The same actor ("BrutalStrike") also delivered the payload via two Android apps (50K+ and 10K+ installs). First documented supply-chain attack targeting **OpenAI Codex authentication tokens specifically**.

## What happened
On or around 2026-06-01, Aikido Security flagged **`codexui-android`** as a malicious npm package. The package presents a clean GitHub source repository — the attack lives entirely in the pre-built `dist/` directory published to the npm registry, a pattern designed to defeat source-diff review.

The `postinstall` hook reads `~/.codex/auth.json` (the OAuth authentication blob written by `@openai/codex` / `codex-cli` after login) and POSTs the full blob to `https://sentry.anyclaw.store/startlog`. The exfil endpoint domain `anyclaw.store` was registered on **April 12, 2026**, roughly 7 weeks before disclosure, suggesting a brief but deliberate campaign window.

The actor, self-identified as **"BrutalStrike"**, simultaneously distributed the payload through at least two Android applications with a combined 60K+ installs on third-party Android markets. The npm vector targets developers; the Android vector appears to target end users of a fake "Codex UI" wrapper app.

### Scope
- **npm package:** `codexui-android` (~29K weekly downloads at disclosure)
- **Android apps:** Two undisclosed-name apps; 50K+ installs and 10K+ installs respectively
- **Credential targeted:** `~/.codex/auth.json` — the OAuth access token used by `@openai/codex` / `codex-cli` against the OpenAI Codex API
- **Exfil endpoint:** `https://sentry.anyclaw.store/startlog` (fake Sentry host chosen to blend into error-monitoring egress logs)
- **Domain registered:** 2026-04-12

## Am I affected?

```bash
# Was the package installed?
npm ls codexui-android 2>/dev/null
cat ~/.npm/_logs/*.log 2>/dev/null | grep codexui-android

# Check for the auth token
ls -la ~/.codex/auth.json 2>/dev/null

# Check npm install history
npm ls --global codexui-android 2>/dev/null
```

If `codexui-android` ever ran its `postinstall` on a machine with `~/.codex/auth.json` present, treat the token as stolen.

### IOCs

| Type | Value |
|---|---|
| npm package | `codexui-android` |
| Exfil endpoint | `https://sentry.anyclaw.store/startlog` |
| Exfil domain | `anyclaw.store` (registered 2026-04-12) |
| Actor handle | `BrutalStrike` |
| Credential targeted | `~/.codex/auth.json` |
| Attack surface | npm `postinstall`, Android apps |

## If you are affected
1. **Revoke the Codex OAuth token immediately.** Go to [platform.openai.com/account/api-keys](https://platform.openai.com/account/api-keys) (or the Codex-specific OAuth management page) and revoke any tokens associated with the compromised machine.
2. **Re-authenticate** on a clean machine after removing the package: `npm uninstall -g codexui-android`.
3. **Check your OpenAI usage logs** for unexpected API calls in the Codex API (code generation, editing) from unusual IPs — stolen tokens can be used for API cost abuse or to enumerate your codebase context.
4. **Audit other AI-tool auth files** on the same machine: `~/.claude/settings.json`, `~/.cursor/mcp.json`, `~/.config/github-copilot/`, `~/.gemini/` — this class of attacker commonly pivots to sibling tools once on a dev machine.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never install packages that use a clean GitHub source + an opaque pre-built `dist/` without independently verifying the build is reproducible.
→ Alert on any outbound HTTPS to domains containing `sentry.` that aren't `sentry.io` — fake Sentry hosts are a recurring camouflage pattern (cf. [Miasma's `api.anthropic.com:443/v1/api`](2026-06-miasma-redhat-cloud-services-compromise.md) fake-AI-vendor host). Add `sentry.anyclaw.store` to your egress deny list.

## Sources
- [Aikido Security — Malicious npm Package Steals OpenAI Codex Auth Tokens](https://www.aikido.dev/blog/malicious-npm-package-codexui-android-steals-openai-codex-auth-tokens) — canonical discovery and technical analysis
- [The Hacker News — codexui-android npm Package Found Stealing OpenAI Codex API Keys](https://thehackernews.com/2026/06/codexui-android-npm-package-found.html)
- [Cybersecurity News — Malicious npm Package Targets OpenAI Codex Users](https://cybersecuritynews.com/malicious-npm-package-targets-openai-codex-users/)
- [SecurityWeek — Supply Chain Attack Targets OpenAI Codex Users via npm](https://www.securityweek.com/supply-chain-attack-targets-openai-codex-users-via-npm/)
