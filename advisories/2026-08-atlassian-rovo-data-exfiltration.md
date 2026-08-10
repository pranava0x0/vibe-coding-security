---
id: 2026-08-atlassian-rovo-data-exfiltration
title: "Atlassian Rovo — indirect prompt injection exfiltrates Jira/Confluence data; the admin 'disable web search' toggle doesn't stop it (unpatched, 2.5+ months unacknowledged)"
date_disclosed: 2026-08-05
last_updated: 2026-08-05
severity: high
status: active
ecosystems: [ai-agents, atlassian, jira, confluence]
tools_affected: [atlassian-rovo]
tags: [prompt-injection, indirect-prompt-injection, data-exfiltration, agentjacking, admin-bypass]
---

## TL;DR
PromptArmor found that **Atlassian Rovo** — the AI assistant built into Jira and Confluence — can be tricked by hidden instructions in ordinary content (a PDF, a Confluence page) into fetching internal Jira/Confluence data an authenticated user can see and sending it to an attacker-controlled server, with **zero clicks** beyond the user asking Rovo a normal question. Worse: the admin console's "disable web search" toggle, which org admins would reasonably assume blocks this class of exfiltration, **does not work** — it disables Rovo's search UI without revoking the underlying capability to resolve and fetch outbound links. Reported to Atlassian on **2026-05-23**; after repeated follow-ups over more than two months with no further communication, PromptArmor published publicly on **2026-08-05**. As of this writing, Rovo remains vulnerable and there is no confirmed fix.

## What happened
PromptArmor disclosed two distinct attack paths that both end with Rovo — the generative-AI assistant embedded across Atlassian's Jira and Confluence products — retrieving data the logged-in user has access to and transmitting it off-platform:

1. **Indirect prompt injection via hidden document content.** An attacker plants invisible instructions inside content Rovo will eventually read as part of normal use — for example, white-on-white or tiny-font text inside a PDF attached to a Jira ticket or embedded in a Confluence page. The text is invisible to a human reviewer but fully legible to Rovo's model when it processes the document. When a user later asks Rovo a question that causes it to read that content (e.g., "summarize this ticket," "search Confluence for X"), the hidden instructions redirect Rovo to gather sensitive Jira/Confluence data the user can access and pass it to an attacker-controlled URL, disguised as a normal-looking outbound link resolution.

2. **Admin "disable web search" control does not close the channel.** Enterprise administrators can toggle off Rovo's web-search feature in the Atlassian admin console, which would reasonably be assumed to prevent Rovo from reaching out to arbitrary external URLs. PromptArmor found this toggle **only disables the search UI/feature surface** — it does not revoke Rovo's underlying capability to resolve and fetch outbound web links triggered indirectly through injected instructions, so the exfiltration path in (1) works identically whether or not an org has "turned off" web search.

**Disclosure timeline.** PromptArmor reported both issues to Atlassian on **2026-05-23**; Atlassian assigned a case number and acknowledged receipt. Despite multiple follow-ups from PromptArmor over the following **2.5+ months**, Atlassian provided no further substantive communication or fix confirmation. PromptArmor published its research publicly on **2026-08-05**.

## Am I affected?
There's no local dependency to check — this is a live prompt-injection surface in Atlassian's hosted product, not something in your dependency tree. You're in scope if:
- Your organization uses Atlassian Rovo (Jira or Confluence AI assistant), AND
- Users can upload/attach documents (PDFs, images) or edit Confluence pages that other users' Rovo sessions might later read, AND
- You have not received a confirmed fix notice from Atlassian as of this writing.

## If you are affected
1. Do not rely on the admin console's "disable web search" toggle as a mitigation — it does not close this exfiltration path.
2. Audit recent Rovo usage logs (if available) for unusual outbound-link resolution patterns or requests to unfamiliar domains.
3. Restrict who can attach documents or edit pages that feed into Rovo's context, where feasible, until Atlassian confirms a structural fix.
4. Treat any Jira/Confluence content from external or low-trust contributors (support tickets, external collaborators, public-facing forms that create tickets) as untrusted input to Rovo.

→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — treat any AI assistant with read access to your ticketing/wiki system as having the union of every document a user can see; an "off" toggle in an admin UI is not guaranteed to revoke underlying tool capability.
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — the same "don't let low-trust content reach a high-trust executor" discipline this repo tracks for MCP servers applies to any first-party AI assistant wired into a collaboration platform (Jira, Confluence, Slack, Notion).
- Cross-reference with [Agentjacking](2026-06-agentjacking-sentry-mcp-injection.md) and [GitLost](2026-07-gitlost-github-agentic-workflows-injection.md) — the same class: an AI feature reads user-controlled content from a collaboration platform and treats it as instructions, not data.

## Sources
- [PromptArmor — Atlassian Rovo Exfiltrates Data, Bypassing Controls](https://www.promptarmor.com/resources/atlassian-rovo-exfiltrates-data) — primary disclosure: both attack paths, admin-toggle bypass detail, disclosure timeline.
- [The Hacker News — Atlassian Rovo Can Be Tricked Into Sending Jira and Confluence Data to Attackers](https://thehackernews.com/2026/08/atlassian-rovo-can-be-tricked-into.html) — independent confirmation and summary.
- [GIGAZINE — A vulnerability has been discovered in Atlassian's AI 'Rovo' that allows internal company data to be transmitted externally simply by having it read documents](https://gigazine.net/gsc_news/en/20260806-atlassian-rovo/) — independent confirmation.
