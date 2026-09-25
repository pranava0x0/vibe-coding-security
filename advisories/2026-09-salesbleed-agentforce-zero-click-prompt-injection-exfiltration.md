---
id: 2026-09-salesbleed-agentforce-zero-click-prompt-injection-exfiltration
title: "SalesBleed — Zenity Labs chained three Salesforce Agentforce flaws into a zero-click, unauthenticated CRM data-exfiltration and Slack-phishing attack: a prompt injection planted in a public Web-to-Lead form hijacks the agent when it later processes the record, a Trusted URLs redaction bypass (unrecognized TLDs + parser/renderer disagreement) lets attacker URLs through, and DNS-based exfiltration via image tags / Slack unfurling leaks data with no user click; reported to Salesforce 2026-06-01, all three fixed by 2026-09-21, disclosed 2026-09-24"
date_disclosed: 2026-09-24
last_updated: 2026-09-25
severity: high
status: patched
ecosystems: [ai-agents, salesforce, crm, saas]
tools_affected: ["Salesforce Agentforce", "Agentforce agents processing Web-to-Lead records", "Agentforce Slack integration (URL unfurling, Reply to a Slack Thread action)"]
tags: [indirect-prompt-injection, zero-click, data-exfiltration, dns-exfiltration, trusted-urls-bypass, web-to-lead, slack, agentforce, salesforce, agent-security]
---

## TL;DR
On **2026-09-24** Zenity Labs disclosed **SalesBleed**, a chain of three flaws in **Salesforce Agentforce** that let an external attacker exfiltrate CRM data **with no click and no authentication into the target org**. Step one is **indirect prompt injection through a public Web-to-Lead form** — a standard Salesforce feature that pipes external submissions straight into CRM records; the malicious instructions sit dormant until an Agentforce agent later processes that lead as part of normal business and treats the record content as instructions, then queries sensitive tables (e.g. Accounts). Step two defeats Salesforce's **Trusted URLs** redaction, which is supposed to strip links/images pointing at untrusted destinations: Zenity found it "didn't register hostnames ending in an unrecognized top-level domain" (e.g. `.fun`) and that certain characters (curly/square brackets) made the redactor and the browser disagree on where the URL ends. Step three exfiltrates: an HTML image tag or **Slack URL unfurling** fires an automatic DNS lookup whose subdomain carries the stolen data — so it works **0-click and survives HTTP egress controls**. A related third flaw abuses the **"Reply to a Slack Thread" action**, which lacked confirmation and attribution, to send phishing messages under the agent's own identity. Zenity reported all three on **2026-06-01**; Salesforce fixed the Trusted URLs bypass **2026-08-19** and Zenity confirmed all three patched **2026-09-21**. No CVE was assigned. No customer action is required for the platform fix, but the pattern — an agent reading untrusted records while holding backend data access and rendering rich content — generalizes to any AI agent, which is Zenity's point.

## What happened

**The chain (Zenity's "SalesBleed").** Three distinct weaknesses, exploited together:

1. **Indirect prompt injection via Web-to-Lead.** Web-to-Lead lets any external user submit data that flows directly into CRM records. Zenity planted instructions in those form fields; when an Agentforce agent later processed the lead "as part of normal business operations, the embedded instructions would hijack the agent's behavior," steering it to read data it was not asked about. Preconditions: an unauthenticated Web-to-Lead endpoint (common) and an agent with query access across tables.

2. **Trusted URLs redaction bypass.** Salesforce's Trusted URLs control is meant to redact links and images pointing at untrusted destinations before the agent's output reaches the user. Zenity found two edge cases: hostnames ending in an **unrecognized TLD** were not recognized as URLs and slipped past redaction, and **termination-character disagreement** (curly braces, square brackets) meant the redactor and the browser parsed the URL boundary differently, so a string the redactor thought safe rendered as a live link. Combining them, "the researchers … successfully bypassed the URL redaction mechanism."

3. **0-click DNS exfiltration.** With a malicious URL reaching the UI, an HTML image source or **Slack link unfurling** triggers an automatic DNS query; the exfiltrated data rides in the query's subdomain. No user interaction, and because it is DNS, it "survives HTTP egress controls." The **Slack "Reply to a Slack Thread" action** provided a second sink: missing "user confirmation before sending a message" and missing visible attribution let an internal or external actor deliver phishing links "using the agent's own identity."

**Impact, per Zenity and Infosecurity.** Attackers could extract "company names, deal sizes and other CRM fields, using DNS-based exfiltration techniques that evaded Salesforce's Trusted URLs redaction controls," with "no click or credential theft" and "no direct access to the target organization."

**Timeline.** Reported to Salesforce **2026-06-01**; Salesforce confirmed it was working on fixes **2026-06-02**; the Trusted URLs bypass was fixed **2026-08-18/19**; Zenity tested and confirmed **all three** fixed **2026-09-21**; public disclosure **2026-09-24**. Salesforce "hardened the Trusted URLs mechanism to prevent similar attacks." No CVE was published; no customer-side action is documented for the platform fixes.

**Why it matters for vibe coders.** Agentforce is the enterprise face of the same pattern this corpus tracks in coding agents: an agent that (a) ingests untrusted external input, (b) treats record/document content as if it were instructions, (c) holds backend data access, and (d) renders rich content (images, link previews) whose fetch is itself an exfiltration channel. Zenity's closing line — "The idea of secure-by-design remains essential but for agents it may no longer be enough" — and Infosecurity's note that "the underlying risk pattern extends beyond Agentforce to any AI agent processing untrusted external records while rendering rich content and holding backend data access" are the transferable lessons. Anyone building an agent on Web-to-Lead-style intake, a support-ticket queue, or a shared inbox is building the SalesBleed shape. It sits with the [Sentry Seer PhantomFix](2026-09-sentry-seer-phantomfix-telemetry-to-coding-agent-rce.md) telemetry-to-agent class and the DNS/image-tag exfiltration seen in the [Claude Chrome extension "ShadowPrompt"](2025-12-shadowprompt-claude-chrome-extension.md) chain.

## Am I affected?

This is a patched Salesforce platform issue; the actionable question is whether you build agents with the same shape.

- **If you run Agentforce:** the three flaws are fixed platform-side (confirmed 2026-09-21) — no customer patch. Still review any custom agent that reads Web-to-Lead or other externally-submitted records and holds cross-object query access.
- **If you build any AI agent:** you have the SalesBleed pattern if an agent (1) processes records or documents submitted by untrusted parties, (2) can be steered by content in those records, (3) can reach sensitive backend data, and (4) emits output that a client renders with automatic fetches (images, link unfurling).

```text
Checklist for your own agents:
[ ] Untrusted-submitted content (forms, tickets, emails) is treated as data, never instructions
[ ] Agent output is sanitized for links/images before any client renders it
[ ] Outbound fetches from agent output cannot reach arbitrary hosts (allowlist; block DNS-only exfil)
[ ] Any "send message / reply" action requires confirmation and carries visible attribution
[ ] The agent's data access is scoped to the task, not the union of everything it can query
```

## If you are affected

1. **Agentforce users:** confirm your org is on the patched platform (Salesforce fixed this centrally); audit custom agents that read externally-submitted records for over-broad table access, and review Slack integrations for unattributed agent-sent messages.
2. **Agent builders:** treat this as a design finding — separate untrusted-content ingestion from privileged data access, and add egress/DNS controls, per the checklist above.

## Prevention

- **Untrusted records are untrusted input.** An agent that reads a form submission, a ticket, or an email must treat that content as data, not as instructions — the same rule as prompt-injection defense for coding agents. [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Sanitize agent output before rendering, and control egress.** Redaction that a browser can out-parse is not redaction; block automatic fetches to non-allowlisted hosts and watch for DNS-only exfiltration (data in subdomains). [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- **Gate agent-initiated messaging** with confirmation and visible attribution so an agent cannot phish under its own identity.

## Sources
- [Zenity Labs — SalesBleed: 0-Click Data Exfiltration on Agentforce](https://labs.zenity.io/post/salesbleed-0-click-data-exfiltration-on-agentforce) — primary, 2026-09-24 (Alex Apostolov, João Donato, Avishai Efrat, Ayush RoyChowdhury): the three findings with mechanisms, preconditions and impact; Web-to-Lead injection; the Trusted URLs bypass via unrecognized TLDs and bracket termination-character disagreement; DNS/image-tag and Slack-unfurl 0-click exfiltration; the disclosure timeline (report 06-01, fixes confirmed by 08-19/09-21); no CVE. Fetched 2026-09-25.
- [The Register — Salesforce Agentforce vulns allowed 0-click CRM data theft, anonymous phishing](https://www.theregister.com/security/2026/09/24/salesforce-agentforce-vulns-allowed-0-click-crm-data-theft-anonymous-phishing/5298958) — 2026-09-24: independent write-up of Zenity's research; the attack-chain summary, the Web-to-Lead vector, the Slack phishing flaw, and the June-to-September timeline. Fetched 2026-09-25.
- [Infosecurity Magazine — Zero-Click Vulnerabilities in Salesforce Agentforce Expose Wider AI Agent Risk](https://www.infosecurity-magazine.com/news/vulnerabilities-salesforce-ai/) — 2026-09-25 (Kevin Poireault): the "no click or credential theft / no direct access" framing, the extracted-fields detail, the DNS-exfiltration-evades-Trusted-URLs point, the 06-01 report / 08-18 fix dates, and the "extends beyond Agentforce to any AI agent" generalization. Fetched 2026-09-25.
- Related in this corpus: [Sentry Seer PhantomFix (platform telemetry → coding agent)](2026-09-sentry-seer-phantomfix-telemetry-to-coding-agent-rce.md), [Claude Chrome extension zero-click prompt-injection/exfiltration](2025-12-shadowprompt-claude-chrome-extension.md), [GTIG adversarial-AI agentic pipelines](2026-09-gtig-adversarial-ai-agentic-pipelines.md).
