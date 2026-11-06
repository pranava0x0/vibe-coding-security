---
id: 2026-11-chatgpt-lockdown-mode-bypass-html-preview-popup-sandbox-escape-zero-click-exfiltration-fixed-09-18-no-cve
title: "ChatGPT Lockdown Mode bypass: HTML preview popup escaped the sandbox, zero-click chat exfiltration in the desktop app; fixed 2026-09-18, no CVE (Check Point)"
date_disclosed: 2026-11-05
last_updated: 2026-11-06
severity: high
status: patched
ecosystems: [chatgpt, openai, electron, web]
tools_affected: ["ChatGPT Classic desktop app (Electron) before OpenAI's 2026-09-18 server-side fix, with or without Lockdown Mode", "ChatGPT web client before the same fix, with one click on the popup", "any product that renders untrusted HTML in a sandboxed frame with allow-popups-to-escape-sandbox and blocks window.open only on the outer frame"]
tags: [chatgpt, openai, lockdown-mode, prompt-injection, sandbox-escape, html-preview, iframe-sandbox, popup, exfiltration, phishing, malware-delivery, desktop-app, electron, patched, no-cve, check-point, single-researcher]
---

## TL;DR
Check Point Research (Alexey Bukhteyev, 2026-11-05) reports that ChatGPT's HTML page preview, the feature that renders HTML from a code block inside two nested sandboxed frames, granted the outer frame `allow-popups` and `allow-popups-to-escape-sandbox`, and ChatGPT's block on `window.open` covered only that outer frame, so a popup opened from the inner frame ran attacker HTML outside the sandbox. Lockdown Mode, OpenAI's June 2026 setting that cuts the outbound channels a prompt injection could use, did not cover that path; in the ChatGPT Classic desktop app the popup opened with no click, which per the researcher allowed silent exfiltration of the chat history and uploaded files, a spoofed ChatGPT window that kept the app icon for malware delivery, and forced sign-out onto an attacker page for phishing. OpenAI removed the two popup permissions on 2026-09-18 per Check Point, who retested and say the technique no longer works; there is no CVE and nothing to install.

## What happened

**The feature.** ChatGPT added HTML page previews for code blocks in February 2026 (Check Point's date). The preview runs in a sandbox built from two nested iframes. Lockdown Mode, introduced in June 2026 as an optional setting, restricts live web access to cached content, blocks internet images, disables network requests from Canvas code and turns off Deep Research, Agent Mode, live connectors and file downloads, the channels a prompt injection would use to move data out.

**The bypass, as Check Point describes it.** The outer sandboxed iframe carried `allow-popups` and `allow-popups-to-escape-sandbox`. ChatGPT overrode `window.open` so that popups were blocked until the user approved them, but the override applied to the outer frame only. A popup opened through the inner frame's `contentWindow` was not blocked, and because of the escape permission it ran arbitrary HTML outside the sandbox. The content could arrive through a crafted prompt, a malicious custom GPT or a shared chat, and the attacker controlled what the popup showed.

**What it gave an attacker, per the researcher.** Three results, each demonstrated by Check Point and reported by The Hacker News the same day:

- Silent exfiltration of the whole chat history and uploaded files. In ChatGPT Classic, the Electron desktop app, `window.open` worked without a user gesture, so the chain needed no click. In the web client it needed one.
- Malware delivery through a spoofed ChatGPT window that kept the application's icon, including from a shared chat, where the victim needs no account.
- Phishing and credential theft, including forcing a sign-out and re-authentication on an attacker-controlled page.

Check Point says the underlying issue was not limited to the desktop app. The Hacker News (2026-11-05) adds the context that OpenAI's own Lockdown Mode documentation does not guarantee that exfiltration cannot happen.

**The fix.** Per Check Point, OpenAI deployed a fix on 2026-09-18 by removing the two popup permissions from the outer iframe, and Check Point confirmed the described technique no longer works. The report date, the acknowledgement date and the retest date are not stated. No OpenAI post or advisory about this report was found this run; every statement about the fix is the researcher's account, and `patched` rests on that account and the retest, as it did for the [October share-link takeover](2026-10-chatgpt-public-share-link-mathlive-postmessage-javascript-session-takeover-parameter-fixed-10-26.md). There is no CVE and no bounty is mentioned.

**Why it matters here.** This corpus's readers paste logs, `.env` contents and connection strings into ChatGPT and upload files to it; a zero-click read of the conversation list is a credential exposure for them. It is also the second ChatGPT report in two weeks in which's sandboxed-frame design was undone by a permission on the frame's parent rather than by the sandbox itself (the MathLive listener in October, the popup permission here), which is the lesson for anyone shipping a generated app that previews untrusted HTML: the sandbox attribute is only as strong as the least careful permission or listener beside it.

## Am I affected?

The fix is server-side and shipped on 2026-09-18 per the researcher; there is nothing to update. If you opened a shared chat, used a third-party custom GPT, or pasted untrusted content into ChatGPT Classic before that date and saw a window open on its own, the conservative steps are the ones below. Exploitation outside the researcher's own tests is not reported.

For your own products, check any page that previews untrusted HTML:

```bash
grep -rn 'allow-popups-to-escape-sandbox' src/ app/ components/ 2>/dev/null   # a popup from this frame leaves the sandbox
grep -rn 'allow-popups' src/ app/ components/ 2>/dev/null                     # pair with an origin check on the opener, not a window.open override
```

A `window.open` override on the parent does not reach a popup opened through a nested frame's `contentWindow`.

## If you are affected

Sign out of other ChatGPT sessions (Settings, Security, log out of all devices) and review recent conversations and connected apps for anything you did not create. If a conversation or an uploaded file held keys, tokens or connection strings, rotate them: [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md). If a spoofed update window installed anything, treat the machine as compromised: [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- Treat Lockdown Mode as one control, not a guarantee; OpenAI's own documentation says so, and this report shows a rendering feature outside its list.
- Keep secrets out of chat transcripts and uploads; a conversation is a document that outlives the session.
- For builders: drop `allow-popups-to-escape-sandbox` from frames that render untrusted HTML, and enforce popup policy at the frame that opens the window, not at its parent. See [credential hygiene](../prevention/credential-hygiene.md).

## Sources
- [Check Point Research — ChatGPT Lockdown Mode Bypass: Phishing, Malware Delivery and Silent Data Exfiltration](https://research.checkpoint.com/2026/chatgpt-lockdown-mode-bypass-phishing-malware-delivery-and-silent-data-exfiltration/) — fetched 2026-11-06: 2026-11-05, Alexey Bukhteyev; the nested-iframe design, the two popup permissions and the outer-frame-only `window.open` override, the three outcomes, the no-gesture behaviour in ChatGPT Classic, OpenAI's 2026-09-18 fix and the retest; report, acknowledgement and retest dates not stated.
- [The Hacker News — Researchers Bypass ChatGPT Lockdown Mode to Exfiltrate Chats Without User Interaction](https://thehackernews.com/2026/11/researchers-bypass-chatgpt-lockdown.html) — fetched 2026-11-06: 2026-11-05; Eli Smadja credited as head of research, the June 2026 Lockdown Mode launch, the fix date, "the underlying issue is not limited to the desktop app"; pickup of the same research, not a second finder.
- [OpenAI Help — Lockdown Mode](https://help.openai.com/en/articles/20001061-lockdown-mode) — linked by both; not opened this run.
- Not found this run: any OpenAI post, advisory or CVE for this report; the fix date and the retest are Check Point's account.
