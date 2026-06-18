---
id: 2026-06-jetbrains-ide-plugins-ai-key-theft
title: "15 malicious JetBrains Marketplace plugins steal AI provider API keys on entry (70K+ installs)"
date_disclosed: 2026-06-17
last_updated: 2026-06-18
severity: high
status: active
ecosystems: [jetbrains-marketplace, ide-extensions]
tools_affected: [IntelliJ IDEA, PyCharm, WebStorm, GoLand, Rider, CLion, DataGrip, RubyMine, PhpStorm, and other JetBrains IDEs]
tags: [credential-theft, ide-extension, ai-api-keys, supply-chain, jetbrains-marketplace]
---

## TL;DR
**15 malicious plugins** on the **JetBrains Marketplace** (combined **70,000+ installs**) silently exfiltrate AI provider API keys — OpenAI, Anthropic, Google AI, and others — **the moment the user enters them** in the plugin's settings panel and clicks "Apply." No lockfile to audit; the key is captured before it reaches your env. Remove any unfamiliar AI-assistant JetBrains plugin immediately, rotate all AI provider API keys, and audit `~/.config/JetBrains/` for unexpected outbound configs.

## What happened

Security researchers reported **15 malicious plugins on the JetBrains Marketplace** targeting developers who configure AI provider credentials inside their IDE. The plugins mimic legitimate AI coding assistants or productivity tools.

**Attack mechanics:** When a developer installs one of these plugins and enters their API key (OpenAI, Anthropic, Google AI Studio SDK, AWS Bedrock, etc.) in the plugin's settings dialog and clicks "Apply," the plugin's settings handler fires immediately — before the IDE stores the key locally — and POSTs the entered value to an attacker-controlled server. The key is captured at the point of entry, making this a **settings-UI credential interception** rather than a file-system or env-var read.

This is distinct from the more common postinstall-hook credential sweepers (Miasma, Hades, IronWorm) that read already-stored credential files. Instead, the plugin is **positioned as the settings UI itself** — so the developer never sees an anomaly; the key appears to work normally.

**What's targeted:** The harvested keys are AI provider API keys — OpenAI organization keys, Anthropic Console API keys, Google AI Studio SDK keys, AWS Bedrock IAM credentials, and similar. These are typically high-value, with monthly spend caps in the thousands of dollars and access to model APIs used in production pipelines.

**Scope:** 15 plugins, **70,000+ combined installs** across the JetBrains Marketplace. JetBrains was notified; removal status of individual plugins varies.

## Am I affected?

```bash
# List all installed JetBrains plugins across recent IDE versions
# (adjust the path to match your JetBrains product and version)
ls ~/.config/JetBrains/*/plugins/ 2>/dev/null
ls ~/Library/Application\ Support/JetBrains/*/plugins/ 2>/dev/null   # macOS

# Check for outbound network connections from IDE processes
# (while IDE is running with a plugin active)
lsof -i -n -P 2>/dev/null | grep -i idea
ss -tnp 2>/dev/null | grep idea
```

**Ask yourself:**
- Did you install any AI-assistant, AI-chat, or productivity plugin from the JetBrains Marketplace in the past 6 months?
- Did that plugin have a settings panel where you entered an API key?
- Is the plugin from a well-known, verified publisher?

If any unfamiliar AI-adjacent plugin has a settings panel that accepted an API key, rotate that key immediately and treat it as compromised.

### IOCs

| Type | Value |
|---|---|
| Plugin count | 15 malicious plugins |
| Combined installs | 70,000+ |
| Target credentials | OpenAI org keys, Anthropic console keys, Google AI Studio SDK keys, AWS Bedrock IAM, other AI provider keys |
| Exfil trigger | Settings dialog "Apply" / "OK" click |
| Affected marketplaces | JetBrains Marketplace (Marketplace ID varies) |
| Ecosystem | JetBrains IDEs (IntelliJ IDEA, PyCharm, WebStorm, GoLand, etc.) |

## If you are affected

1. **Rotate every AI provider API key** you have entered in any JetBrains plugin settings. Treat it as exfiltrated even if the plugin appeared functional.
2. **Remove all unfamiliar AI-assistant plugins** from your JetBrains IDE(s).
3. **Audit spend and usage logs** on OpenAI (platform.openai.com/usage), Anthropic (console.anthropic.com), and other providers for unexpected requests.
4. **Revoke AWS Bedrock IAM credentials** if entered in any plugin, and audit CloudTrail for unexpected `InvokeModel` or credential use.
5. **Review `~/.config/JetBrains/` / `~/Library/Application Support/JetBrains/`** for plugins from publishers you don't recognize.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- **Only install plugins from verified JetBrains publishers** — look for the blue checkmark in the Marketplace.
- **Prefer entering AI provider keys via environment variables** (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`) rather than plugin settings UI — env vars can't be intercepted by a settings handler.
- **Use scoped, budget-capped API keys** for IDE plugins. Never give a plugin an organization master key.
- **Audit plugin permissions** before install — a syntax-highlighter plugin has no reason to make network connections.
- **Keep IDE auto-update off for plugins** (File → Settings → Plugins → uncheck "Update plugins automatically") so you have time to review changelogs before updates apply.

→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources

- [CyberSecurityNews — Malicious JetBrains Marketplace Plugins Steal AI API Keys](https://cybersecuritynews.com/malicious-jetbrains-plugins-steal-ai-api-keys/) — primary disclosure, 15 plugins, 70K+ installs, settings-UI interception mechanism.
- [JetBrains Security Advisories](https://www.jetbrains.com/legal/docs/privacy/security/) — JetBrains notification and removal tracking.
