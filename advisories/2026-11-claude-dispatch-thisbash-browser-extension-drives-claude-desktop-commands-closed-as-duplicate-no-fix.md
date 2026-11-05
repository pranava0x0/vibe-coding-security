---
id: 2026-11-claude-dispatch-thisbash-browser-extension-drives-claude-desktop-commands-closed-as-duplicate-no-fix
title: "Claude Dispatch: a browser extension on claude.ai can drive Claude Desktop into running commands (ThisBash); Anthropic closed it as a duplicate, no fix"
date_disclosed: 2026-11-04
last_updated: 2026-11-05
severity: high
status: unconfirmed
ecosystems: [claude, claude-desktop, claude-cowork, browser-extension, anthropic]
tools_affected: ["Claude Desktop with Dispatch enabled (macOS, Windows, Linux) paired with the Claude mobile app", "claude.ai web sessions in a browser that has a third-party extension with access to claude.ai", "per the researcher, Claude Code Remote Control and Claude Cowork sessions (not demonstrated in the post)"]
tags: [prompt-injection, browser-extension, cross-device, claude-desktop, dispatch, cowork, remote-control, approval-bypass, no-cve, vendor-response-per-researcher, forever-security, single-researcher]
---

## TL;DR
Forever Security (Gal Weizman, 2026-11-04) reports that Claude Dispatch, the feature that lets a phone or browser hand tasks to Claude Desktop, accepted requests from any ordinary signed-in claude.ai session, so a browser extension with access to claude.ai could open the Dispatch page in a hidden window, address the user's desktop agent, send prompts until the agent ran a command, and click the approval buttons itself. The researcher's proof of concept installed an npm package and opened Calculator on the desktop; the same path runs anything. Per the researcher, Anthropic acknowledged the report on 2026-05-19, closed it as a duplicate of an internally known issue, paid no bounty, issued no CVE, and said on 2026-10-13 that Dispatch would be retired by the end of October. On 2026-11-05 the support page still lists Dispatch in limited beta. This file is `unconfirmed` because every statement about Anthropic's response is the researcher's account and no second firm has reproduced the chain.

## What happened

**The feature.** Dispatch is part of Claude Cowork. Anthropic's support page says you message Claude from your phone and it works on your desktop, using local files, connectors, plugins and apps, and that development work is routed to Claude Code. It requires the Claude Desktop app and the Claude mobile app, is in limited beta on some Pro, Max and Ultra plans, and is closed to new users. The same page warns that an instruction from the phone can read, move or delete files and control the browser, and that malicious content could cascade into actions that are hard to undo.

**The flaw as the researcher describes it.** Claude Desktop is an Electron app built on the same web interface and API as claude.ai, and the Dispatch page, though not linked from the web version, accepted requests from an authenticated web session. A content script running on claude.ai with the user's cookies could therefore open the Dispatch view in a small unfocused window, find the local Claude Desktop session, submit prompts through the composer, read the replies, and adjust the next prompt (the researcher calls this prompt forcing). A script clicked the approval buttons, so no human confirmed anything. The payload was an npm install whose postinstall opened Calculator. The researcher names the missing control as an authorization boundary between the web session and the desktop agent, and points at OpenAI's Codex, which does not share sessions between web and desktop, as the contrast. The Register adds that Weizman's firm found personal Claude accounts on corporate endpoints at 18% to 71% of known Claude accounts in six organizations it examined, which is the cross-device case: a personal browser's extension reaching a work laptop's agent.

**Prerequisites.** A browser extension that can act on claude.ai (the proof of concept used a Manifest V3 content script and a host permission for all URLs), a user signed in to claude.ai in that browser, and Dispatch enabled with a Claude Desktop reachable through the account, on the same or another machine. No browser exploit and no further user interaction are needed. The researcher says Claude Code Remote Control and Claude Cowork sessions allow the same attack and promises a follow-up; this file records that as a claim, not a demonstration.

**Timeline, per the researcher.** 2026-05-14 reported to Anthropic. 2026-05-19 Anthropic acknowledged the findings and closed the report as a duplicate of an issue it had already found internally. 2026-10-13 Anthropic said Dispatch would be retired, targeting the end of October 2026. 2026-11-04 publication; the post says the flaw remains exploitable until Dispatch is retired. The Register (2026-11-05) says Anthropic did not respond to its questions, including when Dispatch would be retired, and that the support page still listed Dispatch on 2026-10-30. Read on 2026-11-05, the support page lists it in limited beta and shows "Updated this week" with no date.

**Why this is a vibe-coding file.** The desktop agent Dispatch addresses is the one that routes development work to Claude Code, so the command runs with the developer's files, shell, cloud credentials and connectors. The delivery vehicle is a browser extension, which is the channel this corpus already tracks for [BragJack](2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack.md) and [ClaudeBleed](2026-05-claudebleed-chrome-extension.md). The difference is that the extension does not need Claude for Chrome installed: any extension with access to claude.ai will do, and the extension stores have shipped malicious ones every month this year.

## Am I affected?

1. **Is Dispatch on?** In Claude Desktop, open the Cowork side panel and look for Dispatch. If it is present and paired with your phone, you are in the described configuration until Anthropic retires it or ships a fix.
2. **Which extensions can act on claude.ai?** In Chrome, `chrome://extensions`, open each extension's details and read its site access: "On all sites" or an explicit `claude.ai` entry is the prerequisite. In Firefox, `about:addons`, Permissions tab.
3. **Is the desktop you pair a work machine?** If a personal Claude account on a personal browser is paired with a Claude Desktop on a corporate laptop, the extension population of the personal browser is now in the laptop's threat model.
4. **Look back.** Review Claude Desktop and Claude Code session history for tasks you did not dispatch, and the shell history of the desktop for `npm install`, `npx`, `curl | sh` or similar commands around sessions you do not recognise.

## If you are affected

- Turn Dispatch off, or unpair the mobile app, until Anthropic publishes a fix or confirms the retirement. The researcher's advice is to disable cross-device dispatch where there is no business need.
- Remove browser extensions you cannot vouch for from any browser signed in to claude.ai, and move claude.ai into a browser profile with no third-party extensions.
- If a session ran a command you did not dispatch, treat the desktop as compromised: follow [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md) and [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for every key the desktop held.
- Do not pair a personal Claude account with a corporate desktop. Bring agents under corporate SSO where the plan allows it.

## Prevention

- Approval prompts that the request initiator can click are not approvals. A control that stops a prompt-injected agent has to live where the page's scripts cannot reach it. See [agent sandboxing](../prevention/agent-sandboxing.md).
- Treat browser extensions as endpoint software: review permissions, control installation, and re-review when permissions change. See [credential hygiene](../prevention/credential-hygiene.md).
- Monitor agent activity on developer machines for unexpected package installs, configuration changes, credential reads and new outbound connections.

## Sources
- [Forever Security — ThisBash Escape: Claude Dispatch Flaw Enables Browser Extensions RCE on the OS](https://forever.security/blog/thisbash-claude-dispatch-browser-extension-rce) — fetched 2026-11-05 (dated 2026-11-04, Gal Weizman): the feature description, the six-step chain, the prerequisites, the Calculator proof of concept, the timeline, the "acknowledged the validity of our findings, but closed the report as a duplicate" and retirement statements (the researcher's account of Anthropic's communications, no direct quotes), the Remote Control and Cowork claim, the recommendations. Single researcher; no second firm.
- [The Register — Anthropic won't fix a Claude Dispatch flaw that could let attackers execute remote commands across corporate boundaries](https://www.theregister.com/research/2026/11/05/anthropic-wont-fix-a-claude-dispatch-flaw-that-could-let-attackers-execute-remote-commands-across-corporate-boundaries/5307684) — fetched 2026-11-05 (2026-11-05): the exclusive reporting of the same research, the 18% to 71% personal-account figure for six organizations, the 2026-10-30 support-page check, Anthropic's non-response to the outlet's questions, no CVE and no bounty. Outlet pickup of the same researcher, counted as one source.
- [Anthropic support — Assign tasks from anywhere in Claude Cowork](https://support.claude.com/en/articles/13947068-assign-tasks-from-anywhere-in-claude-cowork) — fetched 2026-11-05: Dispatch in limited beta on some Pro, Max and Ultra plans, closed to new users, requires Claude Desktop and the mobile app, the routing to Claude Code, the safety warnings, "Updated this week" with no date.
- Hacker News item 50379673 (the Register article, 2 points at 14:42 UTC on 2026-11-05), read through the Algolia API: no vendor comment in the thread.
- Not opened: the researcher's X post linked by the Register (X is not reachable from this environment). Anthropic has published no advisory, changelog entry or statement that this sweep could find on 2026-11-05.
- Related in this corpus: [BragJack](2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack.md), [ClaudeBleed](2026-05-claudebleed-chrome-extension.md), [Claude Cowork sandbox escape](2026-07-claude-cowork-sandbox-escape.md), [Embrace embedded browsers](2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma.md).
