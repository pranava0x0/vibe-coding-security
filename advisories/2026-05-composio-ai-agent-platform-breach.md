---
id: 2026-05-composio-ai-agent-platform-breach
title: "Composio AI-agent platform breach — LLM-augmented attacker registered malicious tool definitions in the execution sandbox (May 2026)"
date_disclosed: 2026-05-22
last_updated: 2026-05-27
severity: high
status: contained
ecosystems: [ai-agents, mcp, third-party-ai, github, oauth]
tools_affected: [composio, mcp-toolkits, github, gmail, jira, hubspot, linear, notion, slack, google-calendar, vercel, sentry, google-drive]
tags: [oauth, third-party-ai, ai-agent-platform, mcp, sandbox-escape, llm-augmented-attacker, magic-link, credential-theft, supply-chain]
---

## TL;DR
On **2026-05-21** (01:05 – 09:15 PT), an attacker compromised **Composio** — a popular AI-agent infrastructure platform that brokers ~100 MCP toolkits (GitHub, Gmail, Jira, Notion, Slack, Linear, HubSpot, Drive, Vercel, Sentry, etc.) for downstream agents — by **brute-forcing exploit chains with LLM-generated attack patterns** until they landed in an *internal agentic tool* used to monitor connector health, pivoted that into the **automated-remediation** system, and finally **registered malicious tool definitions inside Composio's own sandboxed execution environment** to get arbitrary code execution. The blast radius reached **5,001 user GitHub OAuth connections** plus **~5,241 API keys** held in an auxiliary cache (~0.3% of active connections). Composio mandated full API-key rotation by **2026-05-23 23:00 PT** and deleted all keys older than 2026-05-22 23:00 PT. Disclosed via Composio's blog + X on 2026-05-22. This is the **second** widely-documented **"AI tool → cloud platform" OAuth-pivot incident** (after [Vercel / Context.ai](2026-04-vercel-context-ai-breach.md)) and the **first** where the attacker openly used LLM-augmented exploitation and weaponized a *malicious-tool-definition-in-sandbox* primitive — the agent-platform analogue of [MCP tool poisoning](2025-07-supabase-mcp-lethal-trifecta.md) and [Windsurf zero-click MCP](2026-05-windsurf-zero-click-mcp-rce.md), but executed from *inside* the platform that brokers agent tools to every downstream customer.

## What happened

Composio (composio.dev) sits *above* MCP — its customers' AI agents call Composio's API, and Composio fans that call out to ~100 third-party services using OAuth grants and API keys the customer has connected. That makes Composio a high-trust **hub** in the agent ecosystem: a single foothold inside it touches every downstream app the platform brokers.

The attack chain Composio published in its **2026-05-22 incident report**:

1. **Initial recon (LLM-augmented brute-force).** The attacker probed Composio's API surface extensively, "brute-forcing many combinations of exploits using **LLM-generated attack patterns**." Composio assesses the actor as "consistent with a highly skilled actor, likely augmented by advanced AI systems" — exceptional speed, deep knowledge of internal architecture.
2. **Foothold in an internal agentic tool.** The attacker landed inside an **internal monitoring agent** used by Composio to watch connector health and report connector failures.
3. **Pivot to automated remediation.** From that monitoring agent, the attacker abused tool-calling privileges to reach the **automated remediation system** that fixes connector errors.
4. **Malicious-tool-definition registration.** Inside Composio's **sandboxed execution environment**, the attacker **registered new "tool definitions"** — fake tools that, when the remediation agent called them, executed attacker-controlled logic. Chained over multiple steps, this escalated to **arbitrary code execution inside the tool-execution sandbox**.
5. **Internal lateral movement via Gmail OAuth.** Separately, the attacker compromised the **Gmail OAuth tokens of certain Composio employees** and abused them via Composio's **magic-link sign-in** to reach staging systems. (Same shape as the [Vercel / Context.ai](2026-04-vercel-context-ai-breach.md) OAuth-pivot, but inside Composio's own employee surface.)
6. **Reach into customer connections.** From inside the platform, the attacker accessed an **auxiliary cache service** holding **~5,241 customer API keys**, plus user OAuth tokens for connected services — most prominently **5,001 GitHub connections** and a handful of Gmail, Jira, HubSpot, Linear, Notion, Slack, Google Calendar, Vercel, Sentry, and Google Drive connections. (~0.3% of active connections; many internal test accounts.)

**Containment.** Composio revoked all user GitHub OAuth tokens platform-wide as a precaution, revoked OAuth + API-key connections across ~100 toolkits, deleted **every developer API key created before 2026-05-22 23:00 PT** starting **2026-05-23 23:00 PT**, mandated all customers rotate their Composio API keys, paused new releases pending investigation, and engaged external IR. Composio says supply-chain integrity is "verified safe" — no malicious code shipped to customer SDKs.

The most-quoted reaction line on X (Ryan Carson): *"Agentic hackers are now hacking your agents."*

### Why this is its own class

- **Hub trust.** Composio brokers agent tool calls for thousands of customers. A foothold inside its platform is upstream of *every* MCP/OAuth-connected service those agents touch — GitHub, Gmail, Slack, Drive, etc. This is the agent-platform analogue of [Vercel / Context.ai](2026-04-vercel-context-ai-breach.md) but with **much higher fan-out**: Context.ai was a single AI productivity tool; Composio is the connector layer for a whole class of agents.
- **Malicious tool-definitions inside the sandbox.** Until now, "tool poisoning" in this repo has been an *external* attack — a malicious MCP server convincing a user's agent to do something ([Supabase MCP lethal trifecta](2025-07-supabase-mcp-lethal-trifecta.md), [Windsurf zero-click MCP](2026-05-windsurf-zero-click-mcp-rce.md), [Claude Desktop DXT](2026-02-claude-desktop-extensions-rce.md)). Here the attacker registered fake tool definitions *inside the platform's own execution sandbox*, against the platform's *own* agents. This is the **sandbox-as-policy** failure pattern (same family as [Microsoft Semantic Kernel](2026-05-semantic-kernel-rce.md), [Google Antigravity](2026-02-google-antigravity-sandbox-escape.md), [OpenClaw Claw Chain](2026-05-openclaw-claw-chain.md)) — an annotation/registration system was treated as documentation, not a security boundary.
- **LLM-augmented attacker is now documented in the wild.** Earlier incidents inferred AI augmentation; here Composio explicitly says the actor used "LLM-generated attack patterns" to brute-force exploit combinations. This formalizes a category we will see repeatedly: **defenders' rate-limits and waf signatures were calibrated against humans, not against an agent that can produce 10,000 well-formed candidate exploits per minute**.
- **Magic-link + employee OAuth = lateral primitive.** Magic-link sign-in built on top of Gmail OAuth tokens means an infostealer-grade compromise of an employee's Gmail becomes a *passwordless* keys-to-the-platform. Same shape as [Vercel / Context.ai](2026-04-vercel-context-ai-breach.md).

## Am I affected?

Yes if **either** of these is true:

- You are a **Composio customer** (developer using their API/SDK or their hosted toolkits), **or**
- You are an **end-user of an app that connected to Composio on your behalf** (e.g. you authorized a third-party agent's GitHub/Gmail/etc. via Composio's OAuth flow).

```bash
# 1. Customer / developer check
#    Did you have a Composio API key issued before 2026-05-22 23:00 PT?
#    If yes, it was deleted on 2026-05-23 — generate a new one + redeploy.

# 2. End-user check
#    GitHub:  https://github.com/settings/applications  → look for any Composio / connected-app
#             authorization. Revoke any you don't recognize.
#    Google:  https://myaccount.google.com/permissions  → revoke Composio-connected apps.
#    Other:   audit OAuth-app/integration lists on Jira, Linear, Notion, Slack, HubSpot,
#             Google Calendar, Vercel, Sentry, Google Drive.

# 3. If your GitHub token may have been in the 5,001:
#    a. Composio revoked it server-side, but rotate the underlying PAT/fine-grained token
#       you used to authorize the Composio app, in case the token itself was exfiltrated
#       and is reusable through other apps.
#    b. Audit private-repo access logs and Actions secrets for unfamiliar reads/writes
#       between 2026-05-21 01:05 PT and 2026-05-23 23:00 PT.

# 4. If you stored secrets in env vars or vaults reachable from a Composio-connected agent,
#    treat them as potentially read and rotate.
```

### IOCs

| Type | Value |
|---|---|
| Compromised platform | `composio.dev` (AI-agent infrastructure / toolkit broker) |
| Attack window | 2026-05-21, **01:05 – 09:15 PT** |
| Disclosure | 2026-05-22 (Composio blog + `@composio` X post) |
| GitHub connections revoked | ~5,001 |
| Auxiliary-cache API keys at risk | ~5,241 |
| Share of active connections | ~0.3% |
| Initial-access pattern | LLM-generated brute-force of exploit combinations |
| Foothold | Internal monitoring agent (connector-failure reporter) |
| Privilege-escalation primitive | Malicious tool definitions registered inside the sandboxed execution environment |
| Internal lateral primitive | Compromised Gmail OAuth tokens of Composio employees + magic-link sign-in |
| Affected toolkits | ~100, headlined by GitHub, Gmail, Jira, HubSpot, Linear, Notion, Slack, Google Calendar, Vercel, Sentry, Google Drive |
| Composio key cutoff | All keys created before **2026-05-22 23:00 PT** deleted starting **2026-05-23 23:00 PT** |
| Customer mandate | Rotate Composio API keys by **2026-05-23 23:00 PT** |

## If you are affected

- [If your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) — rotate GitHub PATs and audit recent activity.
- [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) — for any cloud-key OAuth you connected through Composio (AWS, GCP, Vercel, Sentry).
- [If an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md) — the closest playbook to "the platform brokering my MCP tools was compromised."

## Prevention

- [MCP hygiene](../prevention/mcp-hygiene.md) — assume any agent-platform / MCP broker that holds OAuth grants is *upstream* of every service it touches.
- [Credential hygiene](../prevention/credential-hygiene.md) — short-lived, scoped tokens; OAuth-grant audits; treat magic-link sign-in built on employee email OAuth as a passwordless equivalent of the email account.
- [Agent sandboxing](../prevention/agent-sandboxing.md) — "registered a tool" must be a security event, not a docs annotation.

Specific hardening lessons from this incident:

1. **Treat third-party AI-agent platforms like privileged identity providers.** When you OAuth your GitHub/Gmail/Slack into one, you are granting durable access to whatever the platform holds in its session/cache services — not just to the immediate task.
2. **Pin agent-platform OAuth grants to specific scopes** wherever the IdP supports it (GitHub fine-grained tokens, Google's per-scope consent, scope-bounded HubSpot keys). Avoid `repo`/`org` blanket scopes for app connections.
3. **Diff your connected-apps list quarterly.** Forgotten trial connections are the foothold (Vercel/Context.ai pattern, recurring here).
4. **Inside the platform: tool-definition registration is a *privileged write*.** Audit who can register tools; require code-review or signed registration for additions to the execution sandbox; rate-limit and alert on unexpected new tool definitions inside automated remediation systems.
5. **Calibrate exploit-attempt rate limits for LLM-driven adversaries**, not humans. The "exceptional speed" Composio describes was almost certainly thousands of well-formed requests per minute that an LLM helps an attacker generate cheaply.

## Sources

- [Composio May 2026 Security Incident — Composio blog](https://composio.dev/blog/composio-may-2026-security-incident) — primary incident report (attack chain, scope, mandate dates). (HTTP 403 on direct fetch; cited via multi-source quotation.)
- [Composio May 2026 Security Incident (mirror)](https://composio.ghost.io/composio-may-2026-security-incident/) — Ghost mirror of the same report.
- [@composio on X: security bulletin](https://x.com/composio/status/2057583584719020371) — short public disclosure (initial X post).
- [Ryan Carson on X — "Agentic hackers are now hacking your agents"](https://x.com/ryancarson/status/2057788752227922308) — independent corroboration of the agentic-attack framing.
- [Metorial — Composio Security Incident & MCP Security](https://metorial.com/blog/composio-security-incident-mcp-security) — independent agent-infra-vendor analysis.
- [Oren Rubin — Composio May 2026 Security Incident (LinkedIn)](https://www.linkedin.com/posts/orenrubin_composio-may-2026-security-incident-composio-activity-7463841687505817600-lPdy) — practitioner summary.
- [Axipro — GitHub Breach May 2026: All You Need to Know](https://axipro.co/github-breach-may-2026/) — third-party narrative + token-revocation guidance.
- [ArmorCode — The GitHub Breach: How it happened and actions you can take](https://www.armorcode.com/blog/the-github-breach-how-it-happened-and-actions-you-can-take) — defensive-actions guide.
- [Cyber Unit — GitHub breach, May 2026: What it means for SMBs](https://cyberunit.com/insights/github-breach-teampcp-vs-code-extension-2026/) — context within the broader May 2026 GitHub-credential wave.
- [eSecurity Planet — AI-driven threats, critical vulnerabilities, and supply chain breaches define the week in May 2026](https://www.esecurityplanet.com/weekly-roundup/ai-driven-threats-critical-vulnerabilities-and-supply-chain-breaches-define-the-week-in-may-2026/) — corroborating roundup.
