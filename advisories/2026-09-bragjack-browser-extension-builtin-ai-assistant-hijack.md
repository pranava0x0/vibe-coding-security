---
id: 2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack
title: "BragJack — an ordinary browser extension with page-modification and declarativeNetRequest permissions hijacks the built-in AI assistant in Chrome (Gemini), Edge (Copilot), Perplexity Comet, Opera Neon and Claude in Chrome by injecting into the vendor's own trusted domain; Chrome CVE-2026-0628 (8.8) and Edge CVE-2026-55945 patched, Anthropic patched with no CVE, Comet and Neon acknowledged"
date_disclosed: 2026-09-16
last_updated: 2026-09-17
severity: high
status: mitigated
ecosystems: [browser-extension, ai-agents, claude-code]
tools_affected: [claude-in-chrome, google-chrome (gemini), microsoft-edge (copilot), perplexity-comet, opera-neon, "any agentic browser or browser AI sidebar that trusts a vendor domain for prompt input"]
tags: [browser-extension, agentic-browser, prompt-forcing, trusted-domain-injection, declarativeNetRequest, cve, account-data-exfiltration, claude-in-chrome]
---

## TL;DR
**Forever Security** (researcher Gal Weizman) published **"BragJack"** on **2026-09-16**: a technique in which a browser extension holding only two commonplace permissions — a content script that modifies pages (what every ad blocker has) and **`declarativeNetRequest`** (rewrite network requests) — takes over the browser's *built-in* AI assistant. Each assistant listens for prompts from a **trusted vendor domain**; the extension injects into that page (or redirects the assistant's own script loads) and "speaks to the AI as if it were the vendor," a pattern the researchers call **prompt-forcing** — the attacker authors the entire prompt sequence, not a fragment smuggled into a page. Results per product: **Chrome/Gemini** (extension could redirect the assistant's JS components: local file access, camera/mic, screenshots, profile data — **CVE-2026-0628**, CVSS 8.8, fixed **143.0.7499.192**, January 2026, $7,000); **Perplexity Comet** (an abandoned `testing.perplexity.com` domain: OS file access, full history, screenshots, full agent control — no CVE, $7,000); **Microsoft Edge/Copilot** (marketing-page permissions plus a Think/Do mode race — **CVE-2026-55945**, CVSS 4.2, fixed **150.0.4078.48**, 2026-07-02, $5,000); **Opera Neon** (no extension blocking on opera.com — email/history leakage, agent hijack, $900); **Claude in Chrome** (Anthropic's marketing/demo page could send prompts to the extension with no granular permission check — email exfiltration and arbitrary data access through the agent; Anthropic acknowledged, patched, rated medium, **$600**, no CVE). No in-the-wild exploitation reported; every variant requires the malicious extension to be installed first. Third Claude-in-Chrome hijack class this repo tracks after [ClaudeBleed](2026-05-claudebleed-chrome-extension.md) and [PleaseFix](2026-08-pleasefix-agentic-browser-hijack.md).

## What happened

**The shared design flaw.** A built-in browser assistant needs a channel through which the vendor's own web pages (a marketing demo, a "try Gemini Live" page, a Copilot side panel origin) can hand it prompts and receive results. That channel trusts the *origin*. Extensions, by design, run inside origins: a content script executes in the page, and `declarativeNetRequest` rewrites requests before the page sees them. Forever Security's finding is that in five browsers the assistant's trust in its vendor origin did not account for an extension already living there — so an extension with two ordinary permissions could either inject script directly into the trusted page (Opera Neon, Claude in Chrome, Edge) or redirect the assistant's own component loads to attacker code (Chrome, Comet). The write-up's one-line diagnosis: "AI will have access to your endpoint in ways that are virtually impossible to predict or protect from." The Hacker News' summary of the mechanism: "Together they let the extension slip its own code into the trusted page and speak to the AI as if it were the vendor."

**Prompt-forcing vs prompt injection.** The researchers distinguish this from indirect prompt injection: the attacker is not hiding an instruction in content the model happens to read, but controls the *whole* prompt stream and its sequencing, adaptively, in real time — which also means there is no static payload for an endpoint agent to detect.

**Per product, from the Forever Security post and NVD:**

| Product | Abused element | What the extension got | Fix |
|---|---|---|---|
| Chrome (Gemini) | `declarativeNetRequest` redirect of Gemini's JavaScript components | local file read, microphone/camera, screenshots, profile data leak | **CVE-2026-0628** — NVD: "insufficient policy enforcement in WebView tag in Google Chrome prior to 143.0.7499.192 allowed an attacker who convinced a user to install a malicious extension to inject scripts or HTML into a privileged page," CVSS 3.1 **8.8**, published 2026-01-07 |
| Perplexity Comet | abandoned `testing.perplexity.com` origin still trusted; extension blocks redirects and injects | OS filesystem access, complete browsing history, screenshots, full agent control | acknowledged; no CVE; no fix date published |
| Microsoft Edge (Copilot) | marketing-page permissions + a race switching Think/Do modes mid-execution | browser-agent hijack, screenshots | **CVE-2026-55945** — NVD: race condition (CWE-362) "allows an authorized attacker to disclose information locally," CVSS **4.2**, fixed **150.0.4078.48**, published 2026-07-03 |
| Opera Neon | opera.com does not block extensions | email and history leakage, full browser-agent hijack | acknowledged; no CVE |
| **Claude in Chrome** | Anthropic marketing page with over-permissive prompt-sending to the extension; direct injection on Anthropic domains sent unrestricted messages to the assistant | **email exfiltration and arbitrary data access via the agent** | acknowledged, **patched** (per Forever Security), rated medium, $600 bounty, no CVE |

**Why it matters for this audience.** Claude in Chrome, Comet and the Edge/Chrome agents are the browsers developers use *while logged in* to GitHub, npm, Vercel, Supabase, AWS and their AI-provider consoles. An agent that can be driven by an extension inherits every session in the profile. The Hacker News notes the two prior public Claude-in-Chrome findings this year (LayerX's [ClaudeBleed](2026-05-claudebleed-chrome-extension.md) in April, Manifold Security's July report), and the [PleaseFix/Intent Collision](2026-08-pleasefix-agentic-browser-hijack.md) zero-click class from Black Hat. BragJack is the extension-side sibling: the attacker does not need the victim to visit a page, only to have installed something — and the [PromptSnatcher](2025-12-shadowprompt-claude-chrome-extension.md) campaign already showed malicious "ad blocker" extensions reaching ~900K users.

**Status.** Chrome and Edge fixes are shipped and CVE'd; Anthropic's fix is reported by the researchers as implemented but has no public advisory or version; Perplexity and Opera acknowledged with no dates. `mitigated` rather than `patched`: the structural issue (extensions run inside trusted origins) is addressed per-vendor by hardening each trusted page, and two vendors have not stated a fix.

## Am I affected?

- Chrome below **143.0.7499.192** (check `chrome://version`) or Edge below **150.0.4078.48** (`edge://version`) with any third-party extension installed.
- Perplexity Comet or Opera Neon with any third-party extension installed — no fixed version is published.
- Claude in Chrome: keep the extension current from the Chrome Web Store (Anthropic did not publish a version number); review `chrome://extensions` for anything you did not deliberately install.

```bash
# macOS: list installed Chrome extensions with their requested permissions
for m in ~/Library/Application\ Support/Google/Chrome/Default/Extensions/*/*/manifest.json; do
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(d.get('name'), d.get('permissions'))" "$m" 2>/dev/null
done | grep -i 'declarativeNetRequest\|scripting\|<all_urls>'
```

## If you are affected

1. Update Chrome/Edge; remove extensions you cannot account for, especially any requesting `declarativeNetRequest` plus a broad content-script match.
2. If a suspicious extension was present while an agentic browser or Claude in Chrome was in use, treat every web session in that profile as exposed: sign out everywhere, rotate tokens for GitHub/npm/cloud consoles reachable from that profile. → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
3. Review the agent's action history (Claude in Chrome, Comet) for tasks you did not start.

## Prevention

- → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run agentic browsers in a **separate browser profile with no extensions** and no logged-in developer sessions; a browser agent is only as trustworthy as the least trustworthy extension beside it.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — short-lived sessions and hardware-bound MFA limit what a hijacked agent can do with a profile.
- Enterprise: use extension allow-lists (`ExtensionInstallAllowlist`) on any machine that runs an agentic browser.

## Sources

- [Forever Security — BragJack: Hijacking 5 Browsers via Built-in AI Assistants](https://forever.security/blog/bragjack-hijacking-5-browsers-via-built-in-ai-assistants) — fetched 2026-09-17; primary: the content-script + `declarativeNetRequest` technique, per-product findings and bounties, the `testing.perplexity.com` abandoned origin, the Claude in Chrome marketing-page prompt channel, the "prompt-forcing" framing.
- [The Hacker News — One Extension Could Hijack AI Assistants Across Chrome, Comet, Edge, Opera Neon and Claude](https://thehackernews.com/2026/09/one-extension-could-hijack-ai.html) — fetched 2026-09-17; published 2026-09-16: the capability matrix, CVE numbers and fix versions, bounty amounts, vendor responses, the note that no in-the-wild exploitation is known.
- [NVD — CVE-2026-0628](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-0628) — fetched via the NVD API 2026-09-17; Chrome < 143.0.7499.192, CVSS 3.1 8.8, published 2026-01-07, WebView-tag policy enforcement.
- [NVD — CVE-2026-55945](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-55945) — fetched via the NVD API 2026-09-17; Edge < 150.0.4078.48, CVSS 3.1 4.2, CWE-362, published 2026-07-03.
- [ClaudeBleed](2026-05-claudebleed-chrome-extension.md), [PleaseFix / Intent Collision](2026-08-pleasefix-agentic-browser-hijack.md), [PromptSnatcher / ShadowPrompt](2025-12-shadowprompt-claude-chrome-extension.md) — this repo's prior Claude-in-Chrome and browser-extension entries.
