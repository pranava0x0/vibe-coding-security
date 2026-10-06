---
id: 2026-10-databricks-genie-code-malicious-skills-exfil-phishing
title: "Databricks Genie Code: PromptArmor shows a malicious Skill loaded from a personal workspace — bypassing organisation-level skill governance — can render HTML in the chat that exfiltrates the user's query results through their own browser and shows a credential-phishing modal; four documented Databricks controls (including the auto-approve guardrail agent) did not stop the chain; Databricks' position is that 'it is ultimately the user's responsibility to ensure that uploaded skills do not contain malicious content'; disclosed to the vendor 2026-08-16, published by 2026-10-05 — single-source"
date_disclosed: 2026-10-05
last_updated: 2026-10-06
severity: medium
status: unconfirmed
ecosystems: [ai-agents, databricks, skills, data-platform]
tools_affected: ["Databricks Genie Code (agentic data assistant) with Skills loaded from a personal workspace", "any Genie Code user who installs a Skill from a marketplace or a colleague's share", "any agent platform whose org-level skill allow-list can be bypassed by a per-user workspace"]
tags: [malicious-skill, skills-marketplace, prompt-injection, html-rendering, data-exfiltration, phishing, governance-bypass, vendor-declined, single-source, unconfirmed, databricks]
---

## TL;DR

**PromptArmor** published (the post reached Hacker News on **2026-10-05**) a chain against **Databricks Genie Code**, the natural-language data assistant, through its **Skills** feature: a Skill uploaded to a **personal workspace** runs code that builds an HTML display containing the user's query results; when Genie renders it, JavaScript in the display **sends that data to an attacker's server from the user's browser** and shows a **phishing modal** asking for credentials. The post's title is the finding: **"Four Databricks Genie Controls That Don't Stop Malicious Skills."** PromptArmor's governance point is that Skills "are commonly distributed via online marketplaces, an ecosystem known to be polluted with malicious Skills," and that the organisation-level controls an admin would rely on are bypassed when the Skill is loaded from the user's own workspace.

**Vendor response, as quoted by PromptArmor:** Databricks determined "it is ultimately the user's responsibility to ensure that uploaded skills do not contain malicious content," and that the auto-approve guardrail agent is "not intended as a security boundary, but rather as a control measure to prevent untrusted input from running automatically." Timeline per the post: disclosed **2026-08-16**, coordination through **09-15**, publication intent announced **09-16**. **No CVE.**

**`status: unconfirmed`** — one researcher firm, no independent reproduction and no vendor statement outside the researcher's quotation this sweep could read. Databricks' own blog and security pages were searched and returned nothing on it. The pattern is well established elsewhere in this corpus ([ClawHavoc](2026-02-clawhavoc-clawhub-skills.md), the [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) family), which is why it is recorded rather than deferred.

## What happened

The mechanism has two halves that are each ordinary on their own. First, a Skill is code the agent runs; if the agent renders rich output, the Skill decides what that output contains. Second, rendered HTML in a chat surface is a browser context with the user's cookies and network position; a `<script>` or an `<img src>` in it is a request the user's browser makes. Put together, "show me a chart of Q3 revenue by customer" becomes a Skill that draws the chart and also posts the rows behind it somewhere else, then asks the user to re-authenticate. The governance half is the part specific to Databricks: PromptArmor describes org-level skill allow-listing that a user can route around by loading the same Skill into their personal workspace, so the control an admin configured is not the control that applies.

What this sweep could not verify: which Genie Code release was tested, whether Databricks changed any default after 09-15, and whether the four named controls are the complete set available to an admin. The vendor statement is quoted from the researcher's post, which is a single chain of custody; the exact text of the controls' documentation was not opened.

## Am I affected?

- You use **Genie Code with Skills**, and users can upload Skills to personal workspaces, or install them from a marketplace or a shared link.
- Genie renders **HTML/rich displays** from Skill output in your deployment (the default per the post).
- Your users have query access to data that would matter if it left — which, for a data-platform assistant, is the point of the product.

## If you are affected

1. **Inventory Skills in personal workspaces**, not only the org allow-list; the post's claim is that the latter is not the effective control. Remove anything not from a source you can read.
2. **Restrict or disable HTML rendering of Skill output** if the platform allows it, or confine it to a sandboxed origin without the user's session — the exfiltration and the phishing both need the browser context.
3. **Egress-filter the browser side where you can** (CSP on the Genie surface, if configurable; corporate proxy allow-lists otherwise) so a rendered display cannot reach arbitrary hosts.
4. If a user installed a third-party Skill before you did the above, review the query history for that user and treat displayed datasets as potentially exfiltrated — [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) covers the triage shape; credentials typed into an in-chat modal should be rotated — [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Treat a Skill as a dependency: read it, pin it, and install it through one governed path — [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) applies to agent skills verbatim, and [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) covers the "code the agent runs" half.
- Ask the platform where the trust boundary is in writing. Databricks' answer here — the guardrail agent is not one — is the same answer this repo has recorded from other vendors about auto-approve features; it tells you what you must enforce yourself.
- Rendered output from a tool is untrusted web content; the same CSP and sandboxing you would put on user-generated HTML belongs on agent-generated HTML.

## Why this matters for vibe coders

"Install this Skill to make the data assistant do X" is the data-team version of "add this MCP server," and the trust decision is the same: whoever wrote it runs code with your access and, through the chat panel, in your browser. The governance bypass is the detail to carry into any agent platform you build or buy — an allow-list that a user can sidestep by uploading to their own space is a suggestion, not a control.

## Sources

- [PromptArmor — Four Databricks Genie Controls That Don't Stop Malicious Skills](https://www.promptarmor.com/resources/four-databricks-genie-controls-that-dont-stop-malicious-skills) — the single primary source: the Skill → HTML display → browser exfiltration and phishing-modal chain, the personal-workspace governance bypass, the four controls, Databricks' quoted statements, the 2026-08-16 / 09-15 / 09-16 timeline. Fetched 2026-10-06.
- [Hacker News (Algolia) — "Four Databricks Genie Controls That Don't Stop Malicious Skills"](https://hn.algolia.com/api/v1/search_by_date?query=databricks&tags=story) — 2026-10-05 submission; the date this file uses as disclosure.
- Related in this repo: [ClawHavoc — 1,184 malicious ClawHub skills](2026-02-clawhavoc-clawhub-skills.md), [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md), [Atlassian Rovo data exfiltration (PromptArmor)](2026-08-atlassian-rovo-data-exfiltration.md), [Claude Code InversePrompt (PromptArmor)](2025-08-claude-code-inverseprompt.md).
