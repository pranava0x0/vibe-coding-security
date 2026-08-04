---
id: 2025-12-shadowprompt-claude-chrome-extension
title: "ShadowPrompt — zero-click prompt injection via Claude's Chrome extension, any website could hijack it (patched, backfill)"
date_disclosed: 2025-12-27
last_updated: 2026-03-01
severity: high
status: patched
ecosystems: [claude-chrome-extension]
tools_affected: [claude-in-chrome]
tags: [prompt-injection, zero-click, xss, chrome-extension, origin-validation, backfill]
---

## TL;DR
Koi Security researcher Oren Yomtov found that Anthropic's **Claude Chrome extension** trusted prompts from any subdomain matching `*.claude.ai` — and a DOM-based XSS bug in an Arkose Labs CAPTCHA component hosted on one of those subdomains (`a-cdn.claude[.]ai`) meant **any website** could embed that component in a hidden iframe and silently drive Claude's sidebar with attacker-chosen prompts, no click and no permission prompt required. Patched in the Chrome extension (v1.0.41) and by Arkose Labs; disclosed responsibly, so no confirmed in-the-wild exploitation.

## What happened
The Claude Chrome extension's message-passing layer allowed **any subdomain matching the pattern `*.claude.ai`** to send prompts directly to Claude for execution — an overly permissive origin allowlist rather than an exact-match check ([Koi Security](https://www.koi.ai/blog/shadowprompt-how-any-website-could-have-hijacked-anthropic-claude-chrome-extension)). Separately, an Arkose Labs CAPTCHA widget embedded on the subdomain `a-cdn.claude[.]ai` had its own **DOM-based cross-site scripting (XSS)** vulnerability. Chained together: an attacker's website could load the vulnerable Arkose component in a hidden iframe, trigger the XSS to run attacker-controlled JavaScript in the `a-cdn.claude.ai` origin, and use that origin's standing to send arbitrary prompts to the Claude extension — with **zero clicks, no permission dialog, and no visible sign to the victim**.

Because the injected prompts execute with the extension's own standing privileges, the reported impact included stealing Gmail access tokens, reading Google Drive contents, exporting chat history, and sending emails as the victim — anywhere Claude's Chrome extension had connector access. Disclosure was responsible: reported 2025-12-27, no evidence of pre-patch exploitation reported. **Fixed in Claude Chrome extension v1.0.41** (strict origin validation requiring an exact match to `claude.ai`); the underlying Arkose Labs XSS was independently fixed by Arkose Labs as of **2026-02-19**. No CVE assigned.

This is a **backfill** — found via a routine sweep several months after disclosure — and is a distinct vulnerability chain from this repo's already-tracked [ClaudeBleed](2026-05-claudebleed-chrome-extension.md) (a different Chrome-extension `externally_connectable` trust-boundary bug letting *any Chrome extension*, not any website, drive Claude), [Claudy Day](2026-03-claudy-day-claude-ai-exfiltration.md) (a `claude.ai` web-app URL-parameter injection chain), and [PromptFiction](2026-07-promptfiction-claude-desktop.md) (a `claude://` desktop deeplink auto-submit bug). Together the four confirm a recurring theme across Anthropic's client surfaces: origin/trust-boundary checks on what counts as "Claude's own" content have repeatedly been the weak point, across the Chrome extension, the web app, and the desktop app independently.

## Am I affected?
This was a client-side vulnerability in Anthropic's own Chrome extension and a third-party CAPTCHA vendor's component — not something detectable from your own repo or dependency tree.

- Check your installed Claude Chrome extension version is **≥ 1.0.41**; browser extensions typically auto-update, so most users were covered without action.
- If you were running an older, unpatched version between the December 2025 disclosure and the February 2026 fixes and used Claude's Chrome extension with connected services (Gmail, Google Drive, etc.) during that window, treat those connectors' access as a possible (low-confidence, since exploitation requires visiting a malicious page) exposure and review account activity for anything unexplained.

## If you are affected
No specific rotation is indicated absent evidence you visited a malicious site during the exposure window and observed unexplained activity in a connected account. If you did, treat it as a standard account-compromise response for the specific connector involved (Gmail, Drive, etc.).

→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
- Keep browser extensions on auto-update; this class of fix ships silently and there's no user-facing signal that you were ever exposed.
- Treat AI browser-extension origin allowlists the same as any other trust boundary: a wildcard subdomain match (`*.example.com`) is not equivalent to an exact-origin check, and any third-party component hosted on an in-scope subdomain becomes part of your attack surface.

## Sources
- [Koi Security — ShadowPrompt: How Any Website Could Have Hijacked Anthropic's Claude Chrome Extension](https://www.koi.ai/blog/shadowprompt-how-any-website-could-have-hijacked-anthropic-claude-chrome-extension) — primary research: origin-allowlist flaw, Arkose Labs XSS chain, impact, disclosure timeline, patched versions.
- [The Hacker News — Claude Extension Flaw Enabled Zero-Click XSS Prompt Injection via Any Website](https://thehackernews.com/2026/03/claude-extension-flaw-enabled-zero.html) — independent corroboration, disclosure date, patch confirmation.
- [SOCRadar — ShadowPrompt: Zero-Click Prompt Injection Chain in Anthropic's Claude Chrome Extension](https://socradar.io/blog/shadowprompt-zero-click-anthropics-claude/) — independent corroboration and technical summary.
