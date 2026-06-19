---
id: 2026-06-promptsnatcher-chrome-ai-chat-stealer
title: "PromptSnatcher — malicious Chrome ad-blocker extensions intercept AI chatbot conversations from 900K users across 8 platforms"
date_disclosed: 2026-06-14
last_updated: 2026-06-19
severity: high
status: active
ecosystems: [browser-extensions, chrome, ai-tools]
tools_affected: [ChatGPT, Claude, Gemini, Microsoft Copilot, Perplexity, DeepSeek, Grok, Meta AI]
tags: [credential-theft, browser-extension, prompt-injection, ai-chatbot, chrome, conversation-exfil, supply-chain]
---

## TL;DR

Security researchers named **PromptSnatcher**: at least **two malicious Chrome browser extensions** masquerading as ad-blockers have been silently intercepting **full AI chatbot conversations** — including system prompts, user messages, and model responses — from **~900,000 users** across **8 AI platforms**: ChatGPT, Claude (claude.ai), Gemini, Microsoft Copilot, Perplexity, DeepSeek, Grok, and Meta AI. Extensions with broad `tabs` and `webRequest` manifest permissions can inject content scripts into any matching URL — no exploit required. Exfiltrated conversations include code, credentials, business logic, and proprietary prompts shared with AI tools. **Extensions remain active on the Chrome Web Store as of initial disclosure; removal status is ongoing.**

## What happened

Two Chrome extensions advertised as ad-blockers — with names resembling legitimate privacy tools — requested the `tabs`, `webRequest`, `webRequestBlocking`, `storage`, and `activeTab` Chrome manifest permissions alongside access to a broad URL pattern that matched all major AI chat domains.

**What the extensions did:**

1. On page load for any matching AI chat domain, a **content script** was injected into the page's DOM.
2. The content script hooked into the page's network request/response cycle using `webRequest` APIs and the DOM — specifically, it intercepted XHR/fetch responses from the AI platform APIs (e.g., `api.openai.com`, `api.anthropic.com` streaming endpoints).
3. Every message — user prompts, system prompts, and model responses — was captured and POST-ed to an attacker-controlled endpoint.
4. The ad-blocking functionality worked as advertised, reducing user suspicion.

**Scope:** Researchers estimated **~900,000 users** across the two extensions based on Chrome Web Store install counts. The eight targeted AI platforms cover the vast majority of consumer and enterprise AI chat usage:

| Platform | Domain targeted |
|---|---|
| ChatGPT | chat.openai.com |
| Claude | claude.ai |
| Google Gemini | gemini.google.com |
| Microsoft Copilot | copilot.microsoft.com |
| Perplexity | perplexity.ai |
| DeepSeek | chat.deepseek.com |
| Grok | grok.x.ai |
| Meta AI | meta.ai |

**What's being exfiltrated:** Full conversation content — every prompt you've typed into these platforms and every response you've received — including:
- Source code shared for debugging or review
- Business logic, API keys, and environment variables pasted for AI analysis
- Proprietary prompts and system instructions
- Personal information shared in conversation context
- Any secrets accidentally included in prompts (a common occurrence)

**Monetization:** Captured conversations likely sold to competitive intelligence firms, used to train competing models, or mined for API keys/credentials present in shared code.

## Am I affected?

Any user who had one of the two malicious ad-blocker extensions installed while using AI chat platforms is affected. Because extension names are not published at time of writing (pending Chrome Web Store coordination), check your extension list:

```bash
# In Chrome: chrome://extensions/
# Look for any recently installed ad-blocker you don't remember installing
# Check permissions: extensions with "Read your browsing history" + "Read and change data on all websites"
# are the highest risk class
```

**Red flags in Chrome extension permissions:**
- "Read your browsing history" (tabs permission)
- "Intercept, block, or modify web requests" (webRequestBlocking)
- Broad host permissions matching `*://*.openai.com/*`, `*://*.anthropic.com/*`, or `*://*.google.com/*`

**Questions to ask yourself:**
1. Do you have any ad-blocker or privacy extension installed that you didn't install deliberately?
2. Do your existing extensions have permissions broader than expected for their advertised function?
3. Did you recently install an extension after a recommendation from a browser search or ad?

### IOCs

| Type | Value |
|---|---|
| Extension type | Chrome extension (ad-blocker disguise) |
| Estimated user count | ~900,000 |
| Targeted platforms | ChatGPT, Claude, Gemini, Copilot, Perplexity, DeepSeek, Grok, Meta AI |
| Exfil target | All AI chat conversation content (prompts + responses) |
| Permissions abused | `tabs`, `webRequest`, `webRequestBlocking`, `activeTab`, broad host match |
| Extension names | Not published at time of writing (pending coordination) |

## If you are affected

1. **Remove any suspicious Chrome extension immediately.** If you're not certain an extension is legitimate, remove it; you can always reinstall known-good extensions.
2. **Assume all AI conversations conducted while the extension was installed have been exfiltrated.** This includes any code, credentials, business information, or personal data you've shared with any of the 8 platforms.
3. **Rotate any API keys, secrets, or credentials you've pasted into an AI chat session.** This is a general best practice, but is now urgent if you had a PromptSnatcher-class extension installed.
4. **Audit other Chrome extensions** for broad permissions — any extension with `webRequest` and broad URL match patterns has the same capability.
5. **Notify your security team** if you used AI tools for work purposes and may have shared proprietary code or business information.

## Prevention

- **Audit installed extensions regularly.** The Chrome extension model grants broad capabilities; treat extensions with the same scrutiny as installed applications.
- **Prefer purpose-built extensions from verified publishers.** For ad-blocking, use [uBlock Origin](https://ublockorigin.com/) (open source, verified), not browser-search results for "ad blocker."
- **Check extension permissions before installing.** An ad-blocker does not need access to `api.anthropic.com` or `api.openai.com`.
- **Use AI tools in a separate browser profile or sandboxed browser** if you're handling sensitive work. This limits the blast radius of a malicious extension.
- **Never paste credentials, API keys, or sensitive secrets into AI chat sessions.** Assume any pasted content may be logged, stored, or exfiltrated.
- **Use enterprise AI deployments with DLP controls** rather than consumer chat interfaces for work containing PII or intellectual property.

## Sources

- [The Hacker News — PromptSnatcher: Malicious Chrome Ad-Blocker Extensions Steal AI Chatbot Conversations from 900K Users](https://thehackernews.com) — primary disclosure; 900K users; 8 platforms targeted; conversation exfil mechanism.
- [SecurityWeek — Two Malicious Chrome Extensions Captured AI Chatbot Conversations from Hundreds of Thousands of Users](https://securityweek.com) — independent corroboration; extension permissions detail; platform list.
- [CybersecurityNews — PromptSnatcher: Chrome Extensions Intercept ChatGPT, Claude, and Gemini Conversations at Scale](https://cybersecuritynews.com) — content script injection mechanism; exfil endpoint detail.
