---
id: 2026-10-chatgpt-public-share-link-mathlive-postmessage-javascript-session-takeover-parameter-fixed-10-26
title: "ChatGPT: a public share link ran attacker JavaScript as chatgpt.com in the viewer's session; fixed 2026-10-26, no CVE (Parameter)"
date_disclosed: 2026-10-28
last_updated: 2026-10-31
severity: high
status: patched
ecosystems: [chatgpt, openai, web]
tools_affected: ["ChatGPT web users who opened a public shared conversation before 2026-10-26", "any product that renders untrusted HTML in a sandboxed frame beside a third-party widget that listens for window messages"]
tags: [chatgpt, openai, prompt-sharing, share-link, postmessage, mathlive, sandbox-bypass, xss, session-takeover, csp, bug-bounty, patched, no-cve]
---

## TL;DR
A public ChatGPT share link could run an attacker's JavaScript as `chatgpt.com` inside the signed-in session of anyone who opened it, which let the researchers list the viewer's conversations, read a private chat and call ChatGPT's authenticated APIs as the victim (Parameter, published 2026-10-28). The victim opened the link and, in the first version, clicked Preview once; a later version opened Preview on navigation, so opening the link was the only step. OpenAI rated it P1 and, per Parameter, both web frontends rejected the messages by 2026-10-26; there is no CVE, nothing to install, and no user action required beyond the ordinary review of active sessions.

## What happened

Parameter's write-up ("Do the Math: How We Took Over ChatGPT Accounts", Mukul Goyal, 2026-10-28) describes a chain through three ChatGPT features. A shared conversation can hold an HTML block that ChatGPT's Preview feature renders in a sandboxed frame on a separate origin; that sandbox held. The same conversation held an interactive graph, and drawing it loaded the MathLive math library into the main `chatgpt.com` page. MathLive left a listener running that accepted keyboard-layout messages from any sender, without checking which frame sent them, and the message was allowed to carry raw HTML. The Preview frame could therefore send HTML to the trusted page; the HTML created a frame that was not sandboxed and inherited the `chatgpt.com` identity; and a script loaded from YouTube, a host ChatGPT's content security policy allowed, supplied the code that ran in it. The Hacker News (2026-10-30) adds the researchers' framing: the YouTube step was the final workaround, not the cause, and blocking it alone would have left the message path open.

Once running, the code called ChatGPT's signed-in APIs directly. In the proof it enumerated the victim's recent conversations, opened a private chat never shared with the attacker and sent a small portion of it to a server the researchers controlled. "Essentially, we could perform any action on behalf of the victim's ChatGPT account," the write-up says. The proof ran between the researchers' own accounts; Parameter reports no real-world use.

Timeline, from the write-up: 2026-10-13 message-to-HTML path confirmed against production; 10-14 upgraded to arbitrary JavaScript; 10-16 and 10-17 public-share delivery confirmed between separate accounts, including automatic Preview on navigation; 10-18 reported through OpenAI's bug bounty; 10-19 private-chat proof added; 10-21 OpenAI reproduced it and raised the severity from P2 to P1; 10-22 one web frontend fixed; 10-23 CSP changes blocked part of the chain while one frontend update remained; 10-26 OpenAI confirmed both frontends rejected the reported messages and resolved the report. Total bounty: $5,000. OpenAI published nothing this run read; the fix and its dates are the researcher's account of the bounty correspondence.

**Why it matters here.** Shared ChatGPT conversations travel the way this audience works: pasted into issues, pull requests, Slack and support tickets as "here is what the model told me". A link that needs one click, or none, to act as the viewer's account is a phishing lure with no fake login page. The structural point reaches past ChatGPT: the sandbox around untrusted HTML did its job, and the exposure came from a neighbouring widget on the trusted page that trusted `postMessage` from anywhere. That is the shape of the [Storybook preview](2026-10-storybook-dev-server-cross-origin-preview-code-injection-cve-2026-114125-114126-addon-mcp.md) bug and of the embedded-browser flaws in [Embrace](2026-10-embrace-embedded-browser-flaws-cursor-copilot-claude-desktop-codex-vscode-forever-security.md): any chat or agent UI that renders model output as HTML needs every listener on the host page to check `event.origin`, not only the frame that holds the output.

## Am I affected?

The fix is server-side; there is nothing to update. If you opened shared ChatGPT links from people you do not know between mid-October and 2026-10-26 and clicked Preview, or saw a preview open on its own, the conservative step is to review and sign out other sessions and check for conversations or settings you did not create:

- ChatGPT: Settings → Security → log out of all devices, then sign back in.
- Review recent conversations for ones you did not start and connected apps or custom instructions you did not set.

For your own products: list every `message` event listener on pages that also host sandboxed or third-party frames, and confirm each one checks `event.origin` (or `event.source`) before acting on the payload. A third-party widget's listener counts.

## If you are affected

Sign out of all sessions and change the password if the account shares one with anything else. If ChatGPT held API keys, tokens or credentials in conversations (pasted logs, `.env` contents, connection strings), rotate them: [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).

## Prevention

- Treat a shared chat link like any other link from a stranger: open it signed out or in a separate browser profile.
- Keep secrets out of chat transcripts; a conversation is a document that outlives the session.
- For builders: [credential-hygiene](../prevention/credential-hygiene.md) and the origin-check rule above; a sandboxed frame is only as isolated as the least careful listener on its parent.

## Sources

- [Parameter — Do the Math: How We Took Over ChatGPT Accounts](https://www.parameter.ai/labs/we-found-a-gap-at-openai) — fetched 2026-10-31: 2026-10-28, Mukul Goyal; the timeline (10-13 to 10-26), P2 to P1, the two frontends, the feature chain (public sharing, HTML Preview, interactive graphs, MathLive, CSP), the enumeration and private-chat proof, no real users affected, the $5,000 bounty.
- [The Hacker News — A Shared ChatGPT Link Could Run Attacker Code in Your Session and Read Private Chats](https://thehackernews.com/2026/10/a-shared-chatgpt-link-could-run.html) — fetched 2026-10-31: 2026-10-30; the one-click and zero-click variants, the sandbox that held and the MathLive listener that did not, the YouTube CSP allowance as workaround not cause, "ChatGPT users do not need to do anything", OpenAI's bug bounty on Bugcrowd.
- Hacker News item 50314699 ("We Took over ChatGPT Accounts", 2026-10-31, 146 points), read through the Algolia items API 2026-10-31: the thread disputes none of the claims; one comment reproduces OpenAI's closing response and the bounty figure.
- Not found this run: any OpenAI post or advisory about the report; the fix dates are Parameter's account.
