---
id: 2026-05-claudebleed-chrome-extension
title: "ClaudeBleed — Claude in Chrome extension hijack (May 2026, reopened July 2026)"
date_disclosed: 2026-05-06
last_updated: 2026-07-14
severity: high
status: mitigated
ecosystems: [claude-code, browser-extension]
tools_affected: [claude-in-chrome]
tags: [trust-boundary, prompt-injection, extension-to-extension, gmail, google-drive, github, calendar]
---

## TL;DR
Anthropic's **"Claude in Chrome"** extension exposes an `externally_connectable` message handler that lets **any other Chrome extension** — even a zero-permission one — issue commands to the Claude agent in the user's browser. LayerX named the flaw **ClaudeBleed** and used it to drive Claude into reading Gmail, exfiltrating Google Drive files, and acting on private GitHub repos *on the victim's behalf*. Anthropic shipped **v1.0.70** on **2026-05-06** with extra approval prompts for privileged actions, but the underlying trust boundary remained breakable through the side-panel initialization path. **Update (2026-07-14):** Manifold Security showed the same trust boundary is still exploitable via a forged-click bypass and an undocumented `skipPermissions` URL parameter, confirmed unchanged through **v1.0.80** (released 2026-07-07) — Anthropic closed the new report as a duplicate of the still-open original issue. Treat as **mitigated, not patched**: assume an attacker-controlled extension can still drive Claude until a structural fix lands.

## What happened
On **2026-04-27**, LayerX disclosed to Anthropic a trust-boundary failure in the Claude in Chrome extension. The extension's content script accepts messages via Chrome's `externally_connectable` API but does not verify the *origin extension's identity* before dispatching commands. Any other extension installed in the same browser — including one that holds **no host permissions and no special API access** — can therefore:

1. Open a port to the Claude extension.
2. Send a structured message that the content script forwards into Claude's LLM context as if it came from the user.
3. Drive Claude to perform actions on whatever sites the user has authenticated (Gmail, Google Drive, GitHub, internal SaaS).

Because the malicious extension is just talking to Claude — not the target site — the cross-origin protections that normally stop one extension from reading another's pages do not apply. The victim sees Claude "doing its thing" with no visible attacker.

Anthropic released **v1.0.70 on 2026-05-06**. The patch added approval flows for several privileged actions, but per follow-up reporting (Business Standard, LayerX, CyberInsider), the `externally_connectable` handler itself was **not removed**, and switching Claude into "privileged" mode (used by the side panel's initialization path) bypasses the new approval prompts. The class of attack is still reachable.

## Update — 2026-07-14: reopened by Manifold Security
Manifold Security reported two additional bypasses to Anthropic on **2026-05-21** (against v1.0.72); The Hacker News independently confirmed on **2026-07-14** that both remain present, byte-for-byte unchanged, in **v1.0.80** (released 2026-07-07) — eight releases after the original May patch, with no public advisory issued.

1. **Forged-click bypass.** The extension's content script listens for clicks on `#claude-onboarding-button` but never checks `event.isTrusted`. Any other extension whose content script can reach the claude.ai DOM can construct the element, set a task ID, and dispatch a synthetic click — bypassing the May mitigation that restricted external callers to nine allowlisted task IDs (including `usecase-gmail`, `usecase-gdocs`, and `usecase-calendar`).
2. **`skipPermissions` URL parameter.** Loading the side panel with `?skipPermissions=true` puts it into a `skip_all_permission_checks` mode that executes actions with no user approval at all. Currently only the extension itself is documented to set this parameter, but Manifold flags it as a latent risk if any future bug lets an external page or extension set it remotely.

Severity is **CVSS 7.7 (High)** in the default approval-required mode, escalating to **CVSS 9.6 (Critical)** if the user has enabled Claude's "Act without asking" mode. Anthropic acknowledged both reports on **2026-05-22** and closed the forged-click issue as a duplicate of the original ClaudeBleed report, which "remains open pending a complete fix" — i.e. Anthropic itself confirms the underlying trust-boundary problem, not just this specific bypass technique, is still unresolved. **No patch has shipped as of 2026-07-14.**

## Am I affected?

```bash
# Chrome / Brave / Chromium — list installed extensions
ls -la ~/Library/Application\ Support/Google/Chrome/Default/Extensions/ 2>/dev/null    # macOS
ls -la ~/.config/google-chrome/Default/Extensions/ 2>/dev/null                          # Linux

# Look for Claude in Chrome (extension ID varies by channel)
# Open chrome://extensions/ and confirm version is >= 1.0.70
```

You are affected if:
- "Claude in Chrome" is installed at any version **before 1.0.70** — directly exploitable.
- "Claude in Chrome" ≥ 1.0.70 *and* you have other untrusted Chrome extensions installed (including ones from minor developers, free SEO tools, "color picker"-style utilities, etc.) — the trust-boundary issue is mitigated but not eliminated; assume residual risk.

## If you are affected
1. Update Claude in Chrome to **≥ 1.0.70** immediately. Visit `chrome://extensions/`, enable Developer mode, click "Update."
2. **Audit your other Chrome extensions.** Remove any you don't actively use, and any whose developer you can't identify. ClaudeBleed weaponizes neighbor extensions, so reducing your extension surface is the highest-leverage defense.
3. Until a structural fix lands, **don't run Claude in Chrome in the same browser profile as authenticated Gmail / Drive / GitHub sessions** for sensitive accounts. Use a dedicated profile or browser for AI-agent extensions.
4. Review Gmail, Drive, and GitHub audit logs from late April → mid-May for unexpected reads, sends, downloads, or repo accesses you can't account for.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Treat browser AI assistants as having the union of *every site you're authenticated to*. Run them in a profile that only has the data they need.
→ Disable AI-agent browser extensions on machines that hold privileged enterprise SSO sessions until each vendor publishes a clear `externally_connectable` policy.

## Sources
- [LayerX — ClaudeBleed: A Flaw In Claude's Browser Extension Allows Any Extension to Hijack It](https://layerxsecurity.com/blog/a-flaw-in-claudes-browser-extension-allows-any-extension-to-hijack-it/) — Original disclosure, timeline (disclosed 2026-04-27, partial patch 2026-05-06), and PoC.
- [SecurityWeek — Vulnerability in Claude Extension for Chrome Exposes AI Agent to Takeover](https://www.securityweek.com/vulnerability-in-claude-extension-for-chrome-exposes-ai-agent-to-takeover/) — Independent confirmation.
- [Hackread — ClaudeBleed Vulnerability Lets Hackers Hijack Claude Chrome Extension to Steal Data](https://hackread.com/claudebleed-vulnerability-hackers-claude-chrome-extension/) — Impact summary (Gmail/Drive/GitHub).
- [Business Standard — Claude's Chrome extension vulnerable to exploitation despite a fix](https://www.business-standard.com/technology/tech-news/claude-in-chrome-extension-vulnerable-exploitation-despite-update-126051100441_1.html) — Reports that v1.0.70 is incomplete; side-panel/privileged mode still bypasses checks.
- [CyberInsider — "ClaudeBleed" allows any Chrome extension to control Anthropic's AI assistant](https://cyberinsider.com/claudebleed-allows-any-chrome-extension-to-control-anthropics-ai-assistant/) — Independent confirmation.
- [GBHackers — Claude Chrome Extension Flaw Lets Malicious Add-Ons Steal Gmail and Drive Data](https://gbhackers.com/claude-chrome-extension-flaw/) — Confirmed attack scenario.
- [Cybersecurity News — Claude's Chrome Extension Vulnerability Allows Malicious Extensions to Steal Gmail and Drive Data](https://cybersecuritynews.com/claudes-chrome-extension-vulnerability/) — Confirmed attack scenario.
- [The Hacker News — Claude for Chrome Flaw Lets Other Extensions Hijack the AI Agent (2026-07-14 update)](https://thehackernews.com/2026/07/claude-for-chrome-flaw-lets-other.html) — Manifold Security's forged-click and `skipPermissions` bypasses, confirmed unpatched through v1.0.80, Anthropic's duplicate-closure response.
