---
id: 2026-08-ghostjacking-firewall-log-injection
title: "GhostJacking — attackers plant prompt injections in Cloudflare/Datadog/Sentry logs; Claude Code hijacked 9 times out of 10 when asked to triage them"
date_disclosed: 2026-08-09
last_updated: 2026-08-09
severity: high
status: active
ecosystems: [mcp, claude-code, cursor]
tools_affected: [claude-code, "Claude Desktop", cursor, "any AI agent that reads Cloudflare/Datadog/Sentry logs or alerts"]
tags: [prompt-injection, indirect-prompt-injection, log-poisoning, cloudflare, datadog, sentry, ai-agents, agentjacking]
---

## TL;DR

Tenet Security disclosed **GhostJacking** at DEF CON on **2026-08-09**: attackers plant hidden prompt-injection payloads inside requests that get *blocked* by a firewall — Cloudflare WAF, in the flagship example — knowing the block itself gets faithfully logged word-for-word. When a developer later asks their AI coding agent (tested primarily against **Claude Code**) to "review the blocked requests" or triage an alert, the agent reads the poisoned log entry as data and executes the embedded instructions as commands — DNS rewrites, credential theft, arbitrary code execution — with **zero alerts from EDR, WAF, or IAM**, because every step in the chain is a legitimate, authorized action taken by a tool the developer trusts. Tenet reports a **90% success rate** against Claude Code, and identified **2,700+ organizations** exposed via Cloudflare alone, with an estimated **15,000+ organizations at risk** across Cloudflare, Datadog, and Sentry combined — including Fortune 500 firms and, per Tenet, "a leading AI research lab." Anthropic confirmed and patched a related Claude Desktop data-exfiltration issue before the talk (no CVE issued); Cloudflare, Datadog, and Sentry were notified June–July 2026 but the underlying pattern — "logs are trusted context, not user input" — has no vendor-side fix, since the poisoned content is attacker-controlled *by design* (it's the thing the firewall correctly blocked).

## What happened

GhostJacking is Tenet Security's second disclosed instance of this general shape, after **[Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md)** (Sentry error-data injection, June 2026). The new research generalizes the technique to any monitoring/logging platform a developer routinely asks their AI agent to review:

- **Cloudflare.** A firewall correctly blocks a malicious request — but records the full request, including headers and body, in its logs "word for word." An attacker crafts the blocked request specifically so its logged text reads as an instruction to an AI agent, not just as blocked traffic.
- **Datadog.** Attackers plant fake diagnostic alerts using publicly exposed API keys, so the poisoned alert appears in the developer's normal monitoring dashboard.
- **Sentry.** Crafted error reports carry the same payload shape as the original Agentjacking research, this time framed around log/alert triage rather than error-issue review.

The trigger is an entirely ordinary request: a security analyst or engineer asks their AI assistant (Claude Code was the primary test target; Claude Desktop and Cursor are referenced as related/defensive-guidance targets) to review blocked events or recent error logs — ordinary operational hygiene, not a suspicious action. The agent reads the attacker's planted text as legitimate findings and, following its normal tool-use permissions, executes the embedded instructions: rewriting DNS records, exfiltrating cloud credentials, or running code — all as actions the agent's own trust model considers authorized, since nothing in the chain looks like an attack to conventional defenses. Tenet measured a **90% success rate** against Claude Code specifically, with **zero detections** from EDR, WAF, and IAM tooling across their test runs.

Tenet also tested **Sentry's own AI agent ("Seer")** and found it similarly exploitable through the same log-poisoning shape, reinforcing that this is a property of "AI agent reads operational data and treats it as trusted context," not a bug specific to any one vendor's agent.

Anthropic separately confirmed and shipped a fix for a related Claude Desktop data-exfiltration vulnerability Tenet found during this research, ahead of the public talk — no CVE was assigned. Cloudflare, Datadog, and Sentry were all notified between June and July 2026; none has issued a CVE, and Tenet's own framing is that there is no clean platform-side fix, since the injected text is exactly the kind of attacker-controlled content these systems are supposed to log faithfully.

## Am I affected?

You're at risk if any of the following is true:
- You or your team routinely ask an AI coding agent (Claude Code, Cursor, or similar) to "look at the blocked requests," "check what tripped the WAF," "summarize recent Sentry/Datadog alerts," or similar log/alert-triage prompts.
- Your AI agent has any credential or tool access beyond read-only log viewing when it performs this kind of review (DNS management, cloud credentials, shell/code execution).
- You run Cloudflare, Datadog, or Sentry and haven't reviewed whether your team's AI-agent workflows treat log/alert content as trusted input.

```bash
# Search recent agent session transcripts for signs a log-review prompt
# was immediately followed by an unexpected privileged action (DNS change,
# credential read, shell command) with no explicit human instruction for it
grep -riE "(review|check|triage).*(blocked|firewall|waf|alert|error log)" ~/.claude/history* 2>/dev/null
```

## If you are affected

1. Treat any AI-agent session that reviewed Cloudflare/Datadog/Sentry logs or alerts as a potential prompt-injection event — audit what actions the agent took immediately afterward.
2. Rotate any credentials the agent had access to during or after a log-review session, per the standard credential-rotation playbook.
3. Check DNS records for unexpected changes if the agent had any DNS-management access during the affected window.

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
- **Never let data an agent reads become an instruction it runs.** Log/alert content is attacker-influenceable by definition (anyone can send a request that gets blocked and logged) — treat it the same as any other untrusted external input, not as trusted operational telemetry.
- **Block outbound network access by default** for agents performing log/alert triage, and require explicit human approval before the agent executes any privileged action (DNS change, credential access, code execution) that a log-review task triggered.
- **This is the same root cause as [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md)** — if you already hardened against that, extend the same controls to Cloudflare and Datadog log/alert review, not just Sentry.

## Sources

- [Tenet Security — "GhostJacking Attacks: Half of the Fortune 500 Run These Tools. Getting Blocked by the Firewall Was the Way to Take Over Their AI Agents"](https://tenetsecurity.ai/blog/ghostjacking-attacks-agentic-kill-chain/) — primary research, attack mechanism, 90% success rate against Claude Code, 2,700+/15,000+ exposure estimates, vendor disclosure timeline.
- [SecurityWeek — "'Ghostjacking' Attack Uses Poisoned Logs to Turn AI Agents Bad"](https://www.securityweek.com/ghostjacking-attack-uses-poisoned-logs-to-turn-ai-agents-bad/) — independent confirmation, DEF CON presentation date, mitigation recommendations.
- Cross-reference: [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md) — the earlier, Sentry-specific instance of the same log/alert-poisoning class from the same research firm.
