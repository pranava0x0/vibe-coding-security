---
id: 2026-06-klue-icarus-oauth-breach
title: "Klue AI integration breach — Icarus extortion group steals Salesforce/HubSpot/Slack OAuth tokens from CRM data via AI productivity tool (June 2026)"
date_disclosed: 2026-06-12
last_updated: 2026-06-27
severity: high
status: contained
ecosystems: [oauth, saas-integrations, ai-productivity-tools]
tools_affected: [Klue, Salesforce, HubSpot, SharePoint, Zoom, Gong, Chorus, Clari, Google Drive, Slack]
tags: [oauth-pivot, credential-theft, ai-tool-breach, crm-data, extortion, third-party-breach, salesforce, hubspot]
---

## TL;DR

The **Icarus** extortion group breached **Klue**, an AI-powered competitive intelligence platform, on **2026-06-11 to 2026-06-12** by exploiting OAuth tokens Klue held on behalf of customers. Attackers used automated Salesforce REST API queries to exfiltrate CRM records — including pipeline data, account details, and contact lists — from at least two confirmed victims: **Huntress** and **Recorded Future**. This is the AI-tool OAuth pivot class (template: [Vercel/Context.ai](2026-04-vercel-context-ai-breach.md), [Composio](2026-05-composio-ai-agent-platform-breach.md)) applied to a CRM-connected sales-intelligence tool. A single breach at an AI productivity tool yielded upstream access to every OAuth-connected enterprise service.

## What happened

**Klue** is an AI-powered competitive intelligence platform used by sales and marketing teams. To function, Klue receives and stores OAuth grants from customers' Salesforce, HubSpot, SharePoint, Zoom, Gong, Chorus, Clari, Google Drive, and Slack accounts — standard for any B2B AI productivity tool that aggregates enterprise data.

On **2026-06-11 to 2026-06-12**, the **Icarus** extortion group (a financially-motivated threat actor distinct from North Korea's Icarus/APT38 — same name, different group) gained access to Klue's internal systems. The access path has not been fully disclosed; Klue confirmed unauthorized access to its OAuth credential store.

**What the attackers did:**

1. Retrieved OAuth tokens for connected customer services from Klue's internal credential store.
2. Used the stolen Salesforce OAuth tokens to execute automated Salesforce REST API queries — extracting CRM account records, pipeline stages, deal values, and contact details over approximately **24 hours** of automated exfiltration before detection.
3. Contacted at least two victim organizations (**Huntress** and **Recorded Future**) with ransom demands and proof-of-exfiltration samples.

**Scope confirmed:**

- **Huntress** — endpoint security firm; CRM data exfiltrated
- **Recorded Future** — threat intelligence firm; CRM data exfiltrated
- **Tanium**, **Jamf**, **Sprout Social**, **Gong**, **Insurity** — confirmed affected (Klue/SecurityWeek disclosure, 2026-06-12)
- **HackerOne**, **Kudelski Security**, **Snyk** — confirmed affected (The Register, 2026-06-22)
- **LastPass** — confirmed breach 2026-06-23: Salesforce CRM data exposed (names, email addresses, phone numbers, physical addresses, support case info); LastPass notified 2026-06-12; "customer vaults remained secure." (BleepingComputer, 2026-06-23)
- **BeyondTrust**, **OneTrust**, **8×8**, **Pendo**, **Gms-net** (Swiss AI communications provider) — confirmed affected (SecurityWeek, 2026-06-24); brings known confirmed victims to ~15 organizations
- **~4 additional undisclosed victims** listed on Icarus's dark-web leak site as of 2026-06-24
- **"Hundreds" of Klue customers** affected total (Huntress statement)

**Extortion / data leak status (updated 2026-06-27):** Icarus began posting victim data on its dark-web leak site and sent extortion emails with a 48-hour deadline. **Salesforce and Gong both disabled** the Klue app integration for affected customers to block further OAuth access. Icarus's Tor-based leak site subsequently went offline; additional victims are expected to come forward. Klue itself had not publicly disclosed the total victim count as of 2026-06-24.

**Services with stolen OAuth tokens:** Salesforce, HubSpot, SharePoint, Zoom, Gong, Chorus, Clari, Google Drive, Slack. All of these are typical AI productivity tool integrations that a platform like Klue would request.

**Why this matters for vibe coders:** This is the AI-tool OAuth pivot class at scale. Every AI productivity tool that connects to your enterprise services holds a set of OAuth tokens that is *upstream* of every downstream service it can reach. A breach at the AI tool means a breach at all connected services — without any vulnerability in the downstream services themselves. The attacker never touched Salesforce's own infrastructure; they walked in through Klue's OAuth tokens.

**Status:** Klue confirmed the breach on 2026-06-12 and initiated credential rotation for all affected OAuth connections. The Klue infrastructure breach was contained by 2026-06-13; however, Icarus continues to release stolen CRM data on its leak site as of 2026-06-23.

## Am I affected?

You may be affected if:

1. Your organization uses Klue as a competitive intelligence or sales-intelligence platform.
2. You granted Klue OAuth access to any of: Salesforce, HubSpot, SharePoint, Zoom, Gong, Chorus, Clari, Google Drive, Slack.
3. Your Salesforce or HubSpot instance contains CRM records, pipeline data, or contact lists.

More broadly, this incident is a signal to audit **all** AI productivity tools that hold OAuth grants to your enterprise services.

```bash
# Audit connected apps in Salesforce (admin only)
# Setup → Connected Apps → OAuth Usage

# Audit connected apps in Google Workspace
# admin.google.com → Security → API controls → App access control

# Audit GitHub OAuth apps
# github.com/settings/applications → Authorized OAuth Apps

# Audit Slack OAuth apps
# slack.com/apps → apps with data access to your workspace
```

### IOCs

| Type | Value |
|---|---|
| Threat actor | Icarus extortion group (financially motivated; not APT38) |
| Breach window | 2026-06-11 to 2026-06-12 |
| Access method | Klue OAuth credential store compromise |
| Exfil mechanism | Automated Salesforce REST API queries (~24h duration) |
| Confirmed victims | Huntress, Recorded Future, Tanium, Jamf, Sprout Social, Gong, Insurity, HackerOne, Kudelski Security, Snyk, LastPass, BeyondTrust, OneTrust, 8×8, Pendo, Gms-net (~15 known) |
| Services exposed | Salesforce, HubSpot, SharePoint, Zoom, Gong, Chorus, Clari, Google Drive, Slack |
| Attacker goal | CRM data exfiltration + ransom |

## If you are affected

1. **Immediately revoke and rotate all OAuth grants** Klue holds to your enterprise services. Do this at the service level (Salesforce, HubSpot, etc.) — don't wait for Klue to initiate.
2. **Audit Salesforce audit logs** for API calls made by the Klue integration between 2026-06-11 and 2026-06-13. Look for bulk record reads, unusual query patterns, or access from unexpected IP addresses.
3. **Audit all other connected services** (HubSpot, Google Drive, Slack, Zoom) for unauthorized access during the same window.
4. **Notify your security team and legal counsel** — CRM data typically includes customer PII (contact details), financial pipeline data, and potentially material non-public information (MNPI). This may trigger breach-notification obligations.
5. **Re-evaluate your AI tool OAuth exposure:** list every AI/SaaS tool with OAuth access to Salesforce or other enterprise systems, and confirm each has a valid business purpose and minimal-scope grant.

## Prevention

- **Grant minimal OAuth scopes.** AI productivity tools rarely need write access; prefer read-only OAuth grants where the tool's function permits it.
- **Audit connected apps quarterly.** Most enterprise services expose this in their admin panels. Remove any integration that is no longer actively used.
- **Prefer API keys with IP-allowlisting** over OAuth grants where possible — they're easier to scope and revoke selectively.
- **Monitor for anomalous API usage patterns** on your Salesforce/HubSpot integration accounts — bulk record reads from an AI tool at 2 AM are suspicious.
- **Treat every AI productivity tool as a potential upstream supply-chain exposure.** The question is not just "do we trust this vendor?" but "if this vendor's systems were breached, what could attackers do with our OAuth tokens?"
- See the AI-tool OAuth pivot pattern: [Vercel/Context.ai](2026-04-vercel-context-ai-breach.md), [Composio](2026-05-composio-ai-agent-platform-breach.md)

## Sources

- [SecurityWeek — Klue Breach: Icarus Group Stole CRM Data from Cybersecurity Firms via OAuth Token Abuse](https://www.securityweek.com/cybersecurity-firms-impacted-by-klue-supply-chain-attack/) — primary disclosure; Huntress and Recorded Future named; Salesforce REST API exfil; Icarus group attribution.
- [SecurityWeek — More Cybersecurity Firms Disclose Impact From Klue Hack](https://www.securityweek.com/more-cybersecurity-firms-disclose-impact-from-klue-hack/amp/) — Tanium, Jamf, Sprout Social, Gong, Insurity confirmed; Icarus extortion.
- [BleepingComputer — LastPass confirms data breach in Klue supply chain attack](https://www.bleepingcomputer.com/news/security/lastpass-confirms-data-breach-in-klue-supply-chain-attack/) — LastPass Salesforce data exposed (June 23 confirmation); names, addresses, support case info; vaults unaffected.
- [The Register — Security shops among the 'hundreds' of Klue hack victims](https://www.theregister.com/cyber-crime/2026/06/22/security-shops-among-the-hundreds-of-klue-hack-victims/5259743) — HackerOne, Kudelski Security, Snyk named; "hundreds" victim count (Huntress); Icarus leak-site activity; Salesforce disables Klue integration; attacker infrastructure IPs (Netherlands, France, Ukraine — likely VPN/Tor).
- [The Hacker News — Salesforce Disables Klue App Integration After OAuth Token Abuse Exposes Customer Data](https://thehackernews.com/2026/06/salesforce-disables-klue-app.html) — Salesforce's direct response; OAuth token lifecycle; extortion timeline.
- [SecurityWeek — BeyondTrust, LastPass Impacted by Klue-Salesforce Incident](https://www.securityweek.com/beyondtrust-lastpass-impacted-by-klue-salesforce-incident/) — adds BeyondTrust, OneTrust, 8×8, Pendo, Gms-net as confirmed victims (2026-06-24); Gong disables Klue integration; Icarus leak-site goes offline.
- Cross-link: [Vercel/Context.ai OAuth pivot (April 2026)](2026-04-vercel-context-ai-breach.md) — template for this attack class.
- Cross-link: [Composio AI-agent platform breach (May 2026)](2026-05-composio-ai-agent-platform-breach.md) — second documented "AI tool → downstream cloud access" breach.
