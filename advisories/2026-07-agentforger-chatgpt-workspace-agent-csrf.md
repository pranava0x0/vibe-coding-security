---
id: 2026-07-agentforger-chatgpt-workspace-agent-csrf
title: "AgentForger — a single ChatGPT link CSRF'd a fully autonomous, attacker-controlled Workspace Agent (patched)"
date_disclosed: 2026-06-04
last_updated: 2026-07-24
severity: high
status: patched
ecosystems: [openai, chatgpt, ai-agents]
tools_affected: [chatgpt-workspace-agents, chatgpt-agent-builder]
tags: [csrf, prompt-injection, oauth-pivot, connector-chaining, agent-builder, insider-threat, business-email-compromise]
---

## TL;DR

Zenity Labs disclosed **AgentForger**, a Cross-Site Request Forgery flaw in OpenAI's **ChatGPT Workspace Agents / Agent Builder**: a single crafted link — no click-through confirmation, no separate authorization step — could create a fully autonomous, attacker-controlled agent running as the victim employee, with approval gates switched off and a recurring 5-minute polling schedule to an attacker-controlled inbox for new instructions. The forged agent inherited the victim's **already-authorized enterprise connectors** (Outlook, Gmail, Slack, Google Drive, SharePoint, Teams, Google Calendar) without triggering any new consent screen. OpenAI confirmed the report within 24 hours and shipped a fix in **4 days** (reported 2026-06-04, fixed 2026-06-08); no evidence of in-the-wild exploitation before the patch. The finding got a second wave of mainstream coverage on **2026-07-23** (The Register, CSO Online, BusinessWire), six weeks after the original fix — a backfill-style resurgence this repo has seen before with single-incident case studies that don't reliably surface in campaign-focused sweep queries.

## What happened

ChatGPT's Agent Builder (`chatgpt.com/agents/studio/new`) accepted two query-string parameters that controlled agent creation directly from a URL, with no additional confirmation step:

- **`template_name`** — preselected a starting template, including `chief-of-staff`, described as the most privileged/capable template available.
- **`initial_assistant_prompt`** — supplied a numbered instruction list that the Agent Builder treated as **executable instructions to carry out immediately**, not as text merely displayed for the user to review and approve.

An attacker only needed a target employee who was (a) logged into ChatGPT with Workspace Agents access and (b) had previously authorized at least one enterprise connector (Outlook, Gmail, Slack, Google Drive, SharePoint, Teams, or Google Calendar) — a baseline condition true for most enterprise ChatGPT users. A single link, delivered by any normal phishing channel (email, chat, a shared doc), was sufficient: no separate OAuth consent screen appeared, because the forged agent operated under connector authorizations the victim had already granted in an earlier, legitimate session.

Once loaded, the injected prompt drove the Agent Builder through its own legitimate workflow to:
1. Activate all of the victim's previously-connected integrations.
2. Flip approval gates for write actions from "ask first" to **"never ask."**
3. Set up a recurring schedule — polling roughly every 5 minutes.
4. Publish the agent live and start it running immediately in Preview Mode.

The resulting agent then quietly checked an attacker-controlled inbox for new instructions (emails prefixed `TASK`), executed them autonomously using the victim's own connector access, and emailed results back — enabling reconnaissance, sensitive-data discovery, credential harvesting, impersonation of the victim, internal phishing, and business email compromise, all without the victim taking any action beyond the initial link click. Zenity Labs' own framing: **"This isn't a forged request, it's a forged insider."**

**Disclosure timeline:** reported to OpenAI via Bugcrowd 2026-06-04, triaged and accepted 2026-06-05, fixed 2026-06-08 by removing/restricting the vulnerable URL parameters. No CVE was assigned. No evidence of pre-patch exploitation has surfaced.

## Why this belongs in this repo

This is the **connector-chaining lethal trifecta** pattern this repo already tracks (Claude Desktop Extensions, Claude Desktop personalization sync, Windsurf zero-click MCP, Supabase MCP) — a low-trust *reader* input (a URL parameter, clicked without a second thought) reaching a high-trust *executor* context (an agent inheriting live OAuth grants into Outlook/Gmail/Slack/Drive/SharePoint/Teams) — applied here to **OpenAI's own first-party agent-builder product**, not a third-party MCP server or desktop app. It's also a fresh instance of "AI coding/agent tool auto-executes attacker-supplied config on open," just delivered via URL parameters instead of a workspace file (`.cursorrules`/`CLAUDE.md`/`mcp.json`) — the same root failure (treating attacker-reachable input as a trusted instruction) shows up whether the vibe-coding-relevant surface is a repo folder or an agent-builder URL.

## Am I affected?

You were exposed if your organization used **ChatGPT Workspace Agents / Agent Builder** with one or more enterprise connectors authorized, at any point before **2026-06-08**. There is no local artifact to check — this was a server-side flaw in OpenAI's hosted product, fully closed by OpenAI's fix.

- Review your ChatGPT Workspace admin console for any agents you don't recognize, especially ones using the "Chief of Staff" template, with approval gates set to "never ask," or with unexplained 5-minute recurring schedules.
- Audit connector activity logs (Outlook, Gmail, Slack, Drive, SharePoint, Teams) for unexpected automated access in the window before 2026-06-08.

## If you are affected

- Delete any unrecognized or unexplained Workspace Agents, and revoke and re-authorize the connectors they had access to.
- Treat any connector (email, chat, drive, calendar) an unrecognized agent had access to as a potential credential/data-exposure event — rotate any secrets that were reachable through that connector (shared drive links, service-account tokens, stored credentials in email/chat history).
- → [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) for general incident-response steps if you find evidence of an unauthorized agent having run.

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — treat any URL-driven or link-triggered agent-creation flow as untrusted input, not a convenience feature; a "one link, no confirmation" agent-provisioning flow is a CSRF surface by construction.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — periodically review which enterprise connectors are authorized against which AI tools, since a stale, forgotten OAuth grant is exactly what a forged agent inherits with no new consent prompt.

## Why this matters for vibe coders

Vibe-coding teams increasingly wire ChatGPT/Copilot/Claude agents into the same connectors they use for day-to-day engineering work (GitHub, Slack, Drive, calendars) — the same "AI agent holding real OAuth grants" trust model already flagged for Claude Desktop and GitHub Agentic Workflows. A vendor's own first-party agent-builder product is not exempt from this class: any flow that lets an agent be created or reconfigured from a single link, with pre-existing OAuth grants silently inherited, is a forged-insider risk regardless of which AI vendor built it.

## Sources

- [Zenity Labs — AgentForger, Part 1: ChatGPT Cross-Site Agent Forgery](https://labs.zenity.io/p/agentforger-part-1-chatgpt-cross-site-agent-forgery) — primary technical disclosure: vulnerable URL parameters, attack chain, disclosure timeline.
- [Zenity Labs — AgentForger, Part 2: The Autonomous Insider](https://labs.zenity.io/p/agentforger-part-2-the-autonomous-insider) — follow-up on persistence and autonomous-insider framing.
- [SecurityWeek — OpenAI Fixes ChatGPT Agent Flaw That Could Let Attackers Forge an AI Insider](https://www.securityweek.com/openai-fixes-chatgpt-agent-flaw-that-could-let-attackers-forge-an-ai-insider/) — independent corroboration of mechanism, timeline, and impact.
- [The Hacker News — ChatGPT AgentForger Flaw Could Deploy Rogue Workspace Agents via a Phishing Link](https://thehackernews.com/2026/07/chatgpt-agentforger-flaw-could-deploy.html) — independent corroboration.
- [The Register — One ChatGPT link could smuggle a rogue AI agent into your company](https://www.theregister.com/security/2026/07/23/one-chatgpt-link-could-smuggle-a-rogue-ai-agent-into-your-company/5275116) — the 2026-07-23 resurgence coverage that surfaced this finding in this sweep.
