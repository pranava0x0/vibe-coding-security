---
id: 2026-11-chatgpt-apps-sdk-follow-up-tool-call-routed-through-different-connector-same-mcp-server-developer-report-no-openai-response
title: "ChatGPT Apps SDK: a follow-up tool call was routed through a different connector for the same MCP server, developer report; no OpenAI response"
date_disclosed: 2026-11-05
last_updated: 2026-11-07
severity: medium
status: unconfirmed
ecosystems: [chatgpt, openai-apps-sdk, mcp, oauth, connectors]
tools_affected: ["developers who publish a ChatGPT app and also keep a developer-mode connector pointing at the same MCP server, each with its own OAuth client", "any ChatGPT app whose MCP server treats the connector that started a flow as the one that will finish it (one-time codes, widget confirmations, pending operations keyed by connector)"]
tags: [chatgpt-apps, mcp, oauth, connector-routing, authorization-context, single-source, bug-bounty-process, hacker-news-front-page]
---

## TL;DR
A developer (AldiPower) reported on OpenAI's developer forum on 2026-11-05 that, in a ChatGPT conversation with two connectors enabled that both point at the same MCP server, a follow-up tool call carrying a one-time confirmation code issued through connector A was sent through connector B, with no indication to the user; the server rejected it, and the author's explanation is that ChatGPT matches a tool call to a connector by its OAuth client rather than by MCP server URL. No OpenAI staff member has replied in the thread as read on 2026-11-07, and the author says they did not submit it to the bug bounty because the program requires identity verification, including an ID document, before a report can be filed. This is one developer's observation with no vendor confirmation; if your MCP server assumes the connector that started a flow is the one that finishes it, treat connector identity as something the server must check per call.

## What happened

**The report.** The thread "Security: Follow-up tool call silently routed to a different connector" (ChatGPT Apps SDK category, 2026-11-05) describes two connectors in one conversation: connector A, a custom connector added in developer mode, and connector B, the published app from the app directory. Both point to the same MCP server and each has its own OAuth client. A flow started through an MCP Apps widget on connector A, whose `ui/message` carried a one-time confirmation code; the follow-up tool call that redeemed the code arrived through connector B. In the author's words, "the code was confirmed through connector A and redeemed through connector B." The server rejected every attempt in that conversation, so the author's own app was not compromised; the report is about the routing. The author proposes that "Tool calls are matched to a connector by its OAuth client, not by the MCP server URL." No ChatGPT, SDK or server versions are stated.

**The replies.** One community reply (techsoft.ye, 2026-11-06) suggests binding pending operations to the originating connector, preventing automatic connector switching, and recording routing decisions in traces, and asks whether the connector identity changed at confirmation or only when the model chose the follow-up call; it recommends OpenAI's coordinated disclosure process and does not identify its author as OpenAI staff. The author's follow-up (2026-11-06) says they tried the bug bounty route and declined because the program requires personal data, "biometric identification and ID card up front", before a report can be submitted. The page does not name the bounty platform.

**How it reached the public.** Hacker News item 50399569 ("ChatGPT silently passes data between connectors and the bounty wants an ID card", 2026-11-06 22:50 UTC, 90 points, 37 comments) links the thread. Simon Willison's comment links Bugcrowd's documentation stating that identity verification is now mandatory for all researchers before submitting reports, which is the program-side fact behind the author's refusal. No comment in the thread is from an identified OpenAI employee. One commenter reports their own vulnerability-report accounts being closed; that is the commenter's claim and nothing in this file rests on it.

**What is and is not established.** Established by the author's log, as relayed: one conversation, two connectors on one server, a follow-up call delivered to the other connector. Not established: whether this is deliberate routing (the model choosing among tools that look identical because both connectors expose the same server), a bug in connector matching, or specific to developer-mode plus published pairs; whether a user's data crossed an authorization boundary (both connectors here belonged to the same developer and server); and OpenAI's view. The only mechanism statement is the author's hypothesis. This file stays `unconfirmed` until OpenAI, a second developer with a separate reproduction, or a bounty record says more.

**Why it matters to app builders.** A ChatGPT app's MCP server sees requests through an OAuth client it issued per connector. If the server keys a pending operation, a confirmation code, a cart or a session to the connector that started it and trusts that the same connector will complete it, a call that arrives through a sibling connector either fails (as here) or, if the server keys only to the user, succeeds under a different client's grant than the one the user confirmed in the widget. The server-side control is the same in both cases: bind the operation to the client that started it and reject a completion from another, which is what this server did.

## Am I affected?

1. **Do you run two connectors on one MCP server?** The common case is exactly the one reported: a developer-mode connector for testing beside the published app. Check whether both are enabled in the ChatGPT account you test with.
2. **Does your server bind flows to the connector?** Look at how one-time codes, widget confirmations and pending operations are stored: if the key is the user alone, a call through another connector completes them; if the key includes the OAuth client, it fails closed, as the reporter's did.
3. **Can you see which client each call came through?** If your server does not log the OAuth client id per tool call, you cannot tell whether this has happened to you.

## If you are affected

- Nothing to rotate. Bind pending operations to the originating OAuth client and reject completions from another; log the client per call; disable the developer-mode connector in the accounts where the published app is installed until the behaviour is explained.
- If you observe the same routing with a server you can log, a second independent reproduction is what would move this file from `unconfirmed`; OpenAI's coordinated-disclosure page is the reporting route the thread's reply named, and the bounty's identity-verification requirement is the program's, not OpenAI's app platform's, per the Bugcrowd document the Hacker News thread links.

## Prevention

- Treat the connector as part of the authorization context: the MCP server, not the client, decides whether a call may complete something another client started. [MCP hygiene](../prevention/mcp-hygiene.md) covers server-side checks that do not rely on the client behaving.
- Keep test connectors out of production accounts.

## Sources

- [OpenAI Developer Community — Security: Follow-up tool call silently routed to a different connector](https://community.openai.com/t/security-follow-up-tool-call-silently-routed-to-a-different-connector/1413053) — fetched 2026-11-07: AldiPower's 2026-11-05 post, the two-connector setup, the quoted log sentence and hypothesis, techsoft.ye's 2026-11-06 reply, the author's 2026-11-06 follow-up on the bounty's identity requirement; no OpenAI reply on the page; no versions stated.
- [Hacker News — ChatGPT silently passes data between connectors and the bounty wants an ID card](https://news.ycombinator.com/item?id=50399569) — read 2026-11-07 through the Algolia items API: 2026-11-06 22:50 UTC, 90 points, 37 comments; simonw's comment linking Bugcrowd's identity-verification documentation; no identified OpenAI employee in the thread.
- Related in this corpus: [ChatGPT Lockdown Mode bypass](2026-11-chatgpt-lockdown-mode-bypass-html-preview-popup-sandbox-escape-zero-click-exfiltration-fixed-09-18-no-cve.md) (the other ChatGPT client-side report of the week, also without an OpenAI statement), [mcp-remote OAuth discovery batch](2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md) (OAuth client identity in MCP flows).
