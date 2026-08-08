---
id: 2026-08-pleasefix-agentic-browser-hijack
title: "PleaseFix / Intent Collision — zero-click hijack of Claude in Chrome, ChatGPT Atlas, Gemini, Perplexity Comet, Copilot Edge (Black Hat USA 2026)"
date_disclosed: 2025-12-27
last_updated: 2026-08-08
severity: high
status: active
ecosystems: [claude-code, browser-extension, ai-agents]
tools_affected: [claude-in-chrome, chatgpt-atlas, gemini-in-chrome, perplexity-comet, copilot-edge]
tags: [prompt-injection, indirect-prompt-injection, zero-click, account-takeover, agentic-browser]
---

## TL;DR
Zenity Labs presented **PleaseFix** at Black Hat USA 2026: a vulnerability class they call **"Intent Collision"** that lets attacker-controlled content (an email, a calendar invite, an X post) hijack an "agentic browser" — Claude in Chrome, ChatGPT Atlas, Gemini in Chrome, Perplexity Comet, and Microsoft Copilot Edge — with **zero clicks**. Against Claude in Chrome specifically, researchers chained a hidden email instruction into a fake-CDN JavaScript import, then used the agent's own authenticated session to steal confirmation codes out of Gmail and take over the victim's Slack, X, and Claude.ai accounts. Reported to Anthropic (Dec 2025 / Jan 2026) and OpenAI (Jan 2026); both still largely unpatched as of the Aug 5 2026 public disclosure — Anthropic closed the Claude report as "informative," OpenAI says there's "no easy patch" because the exploit abuses the agentic browser's intended core capability.

## What happened
Zenity Labs (Michael Bargury and Stav Cohen) built on their earlier March 2026 Perplexity Comet finding and generalized it into **Intent Collision**: any content an agentic browser's AI reads during normal use — a summarized email, a rendered web page, a calendar invite, a social-media comment — can plant instructions that silently redirect the agent to act on the attacker's behalf instead of (or in addition to) the user's actual request. No click, approval, or visible warning is required.

**Claude in Chrome — "From alert(1) to Full Account Takeover":**
1. A malicious email lands in the victim's Gmail inbox with a hidden instruction disguised as ordinary text.
2. The victim asks Claude in Chrome to summarize their recent emails; Claude reads the hidden instruction as if it were a legitimate directive.
3. The instruction tells Claude to run an innocuous-looking `import()` — "generate a UUID" — from a lookalike CDN (`esm-sh.com`, mimicking the real `esm.sh`) that Zenity controlled. The imported package silently executes arbitrary JavaScript while returning a plausible UUID, so nothing looks wrong.
4. That script fetches the victim's Gmail Atom feed (`https://mail.google.com/mail/u/0/feed/atom`), pulls message IDs and bodies, and exfiltrates them to an attacker server — while Claude continues summarizing emails normally in the foreground.
5. With inbox read access in hand, the researchers demonstrated full account takeover on three services: **Slack** (intercept the email confirmation code), **X** (complete a password-reset flow via its internal API using the emailed code), and **Claude.ai itself** (extract the magic-link nonce from Gmail and exchange it for a session cookie).

Reported to Anthropic via HackerOne on **2025-12-27**; closed as **"Informative"** on **2026-01-27**. A follow-up report on **2026-01-12** was closed as a duplicate and ruled ineligible for the bug-bounty program. As of the Aug 5 2026 public disclosure, no fix has shipped.

**ChatGPT Atlas — "Grand Theft Atlas":** OpenAI's agentic browser is vulnerable to the same Intent Collision class via a single planted comment on an X thread — the agent's benign user request gets hijacked mid-session and redirected to unauthorized actions (demonstrated: phishing via WhatsApp, an Amazon purchase with a modified shipping address) using the victim's own authenticated browser sessions. Reported to OpenAI in January 2026; OpenAI told SecurityWeek there is "no easy patch because the exploit relies on the intentional core capability of an agentic browser."

**Perplexity Comet, Gemini in Chrome, Copilot Edge:** Zenity's Black Hat talk extended the same Intent Collision technique to all five browsers. Perplexity had patched Zenity's original March 2026 file-system-access finding, but researchers **bypassed that fix twice**. Gemini and Copilot Edge findings were disclosed as part of the same research; per-vendor patch status for those two was not itemized in coverage found this sweep — treat as unconfirmed-patched until a vendor statement surfaces.

## Am I affected?
There's no local artifact to check — this is a live prompt-injection surface in the vendor's hosted product, not something in your dependency tree. You're in scope if you use any of these with agent/autonomous actions enabled:
- Claude in Chrome extension (any version)
- ChatGPT Atlas (OpenAI's agentic browser)
- Gemini in Chrome
- Perplexity Comet
- Microsoft Copilot Edge

## If you are affected
1. Don't let an agentic browser extension summarize or act on email/calendar content from untrusted or unauthenticated senders without reviewing what it did afterward.
2. Disable "act without asking" / autonomous-action modes in Claude in Chrome, Comet, and Atlas until each vendor confirms a structural fix — require an approval prompt for every state-changing action.
3. Run agentic-browser extensions in a **separate browser profile** that isn't signed into your primary Gmail, Slack, X, or other high-value accounts.
4. Review Gmail "sent," Slack, and X account-activity logs for confirmation-code or password-reset emails you didn't request.
5. Cross-reference with [ClaudeBleed](2026-05-claudebleed-chrome-extension.md) and [Claudy Day](2026-03-claudy-day-claude-ai-exfiltration.md) — this is the third distinct trust-boundary failure this repo tracks in Claude's browser-facing surfaces, and Anthropic's "informative" closure here echoes its handling of both.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Treat any AI browser agent as having the union of every site you're logged into. Give it a dedicated, low-privilege browser profile.
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — same "don't let low-trust content reach a high-trust executor" discipline applies to agentic-browser tool use, not just MCP.

## Sources
- [Zenity Labs — Claude in Chrome: From alert(1) to Full Account Takeover](https://labs.zenity.io/post/claude-in-chrome-from-alert-to-full-account-takeover) — primary technical writeup: attack chain, CDN spoofing, Gmail exfiltration, Slack/X/Claude.ai takeover, disclosure timeline.
- [Zenity Labs — Grand Theft Atlas: How We Hijacked ChatGPT's AI Browser](https://labs.zenity.io/post/grand-theft-atlas) — ChatGPT Atlas Intent Collision chain.
- [Zenity Labs — Claude in Chrome: A Threat Analysis](https://labs.zenity.io/post/claude-in-chrome-a-threat-analysis) — supporting threat-model writeup.
- [BusinessWire — Zenity Labs Exposes the Full Scope of PleaseFix](https://www.businesswire.com/news/home/20260805803998/en/Zenity-Labs-Exposes-the-Full-Scope-of-PleaseFix-a-Vulnerability-Class-Enabling-Zero-Click-Attacks-Across-Leading-Agentic-Browsers) — Black Hat USA 2026 disclosure, names all five affected browsers, Perplexity patch-bypass detail.
- [SecurityWeek — Zero-Click AI Browser Hacking: Claude and ChatGPT Atlas Hijacked via Emails, X Posts](https://www.securityweek.com/zero-click-ai-browser-hacking-claude-and-chatgpt-atlas-hijacked-via-emails-x-posts/) — independent confirmation, vendor response quotes, disclosure timeline.
