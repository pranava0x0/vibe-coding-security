---
id: 2025-08-salesloft-drift-oauth-breach
title: "Salesloft Drift OAuth Breach — UNC6395 steals Salesforce CRM data from Cloudflare, Palo Alto, Zscaler and hundreds of orgs (August 2025)"
date_disclosed: 2025-08-26
last_updated: 2026-06-24
severity: high
status: contained
ecosystems: [saas, oauth, salesforce]
tools_affected: [salesloft, drift, salesforce-crm]
tags: [oauth-pivot, ai-tool-oauth-pivot, saas-supply-chain, credential-theft, unc6395, github-account-compromise]
---

## TL;DR

Threat actor **UNC6395** compromised a Salesloft GitHub account, stole OAuth tokens from the **Drift AI chat agent**'s Salesforce integration, and used them to exfiltrate CRM data — including AWS keys, Snowflake tokens, and support case credentials — from **hundreds of organizations** including Cloudflare, Palo Alto Networks, and Zscaler. This is the **first documented large-scale AI-tool OAuth pivot breach**, and the direct template for the [Vercel/Context.ai breach](2026-04-vercel-context-ai-breach.md) (April 2026) and the [Klue/Icarus breach](2026-06-klue-icarus-oauth-breach.md) (June 2026).

## What happened

**Drift** is an AI-powered chat and marketing automation tool, owned by Salesloft, that integrates with Salesforce CRM via OAuth. Thousands of organizations authorized Drift to read and write their Salesforce data — contact records, account information, and support case logs — as part of normal sales and customer-success workflows.

**Attack timeline:**

- **March – June 2025:** UNC6395 (Mandiant/Google classification; tracked as GRUB1 by Cloudflare) compromised a Salesloft employee GitHub account and conducted extended reconnaissance of the Salesloft and Drift application environments.

- **August 8–18, 2025:** Using credentials obtained from the GitHub compromise, UNC6395 extracted **OAuth tokens and refresh tokens** from the Drift-Salesforce integration. With these tokens, they connected directly to hundreds of downstream Salesforce instances — bypassing any authentication at Salesloft itself — and ran automated SOQL queries to bulk-export data.

- **August 26, 2025:** Salesloft publicly disclosed the breach. Cloudflare confirmed it was notified the same day. Salesforce disabled all Salesloft integrations in response.

**What was stolen from downstream Salesforce instances:**
- Customer contact information (names, emails, phone numbers, job titles, location)
- Support case data — often containing **API tokens, access keys, Snowflake credentials, and configuration details** shared during support interactions
- Sales account records and licensing information
- At Cloudflare specifically: **104 API tokens** contained in support case data

**The GitHub-to-OAuth-to-CRM pivot chain:** The entry point was not the npm or PyPI registry, not an AI coding tool — it was a Salesloft employee's GitHub account used during internal development. That single account compromise gave the attacker enough access to extract the OAuth tokens Drift held on behalf of every integrated Salesforce customer.

**Why AI tool → OAuth → downstream service is the attack template:** Drift is classified as an AI chat bot/AI marketing assistant. Its Salesforce OAuth grant was a **high-trust, persistent, scope-broad token** — a "Allow All" integration connecting Salesloft's AI product to the most sensitive sales and support data in the customer's cloud. The same structural pattern (AI productivity tool holds OAuth with read/write on an enterprise cloud platform) is what made the [Vercel/Context.ai](2026-04-vercel-context-ai-breach.md) and [Klue/Icarus](2026-06-klue-icarus-oauth-breach.md) breaches possible.

**Confirmed affected organizations:**
- Cloudflare (104 API tokens in support case data)
- Palo Alto Networks (contact + account data)
- Zscaler (contact + support case data)
- Google, Cisco, Farmers Insurance, Workday, Adidas, Qantas, Allianz Life, Louis Vuitton, Dior, Tiffany & Co. (per BleepingComputer)
- Proofpoint, SpyCloud, Tanium, Tenable (confirmed in later SecurityWeek reporting)
- Total estimated: hundreds of organizations

## Am I affected?

If your organization used **Salesloft + Drift** with a Salesforce integration between 2025-01 and 2025-08:

```bash
# Check Salesforce Connected App audit trail (run as Salesforce admin)
# Go to: Setup → Security → Session Management → View All Active Sessions
# Filter for "Connected App: Drift" sessions between 2025-08-08 and 2025-08-19

# Check Salesforce API usage logs for anomalous bulk SOQL queries during Aug 8-18
# Look for: large SELECT volume against Contact, Account, Case objects in that window
```

**Rotation priority:**

1. Any API tokens, Snowflake credentials, or database passwords ever shared in Salesforce support cases
2. AWS access keys mentioned in any CRM record or case
3. Any credential contained in case attachments or case comments

Even if Salesloft has revoked the Drift OAuth tokens, data already copied to attacker-controlled infrastructure during August 8–18 **remains in their possession**.

## If you are affected

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — for AWS keys, Snowflake tokens, and any infrastructure credentials found in support case data.

→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — if GitHub tokens were exposed through the breach (GitHub tokens are a common support-case artifact).

## Prevention

The structural lesson: **every AI productivity tool you authorize with an "Allow All" or broad OAuth scope becomes a pivot point.** When that tool is breached, the attacker inherits your cloud permissions without touching your infrastructure directly.

- **Audit connected OAuth apps quarterly.** Go to Salesforce Setup → App Manager → Connected Apps → review every active integration and its granted scopes. Revoke integrations you no longer use.
- **Prefer read-only OAuth scopes** for AI chat and marketing tools. If Drift only needs contact data, it doesn't need write access to support cases.
- **Separate support credentials from CRM data.** Never paste API keys, AWS credentials, or database passwords into Salesforce case comments or attachments. Use a secret manager for sensitive handoffs.
- **Monitor for bulk SOQL queries.** In Salesforce, set up Event Monitoring or a security tool that alerts on anomalously large API query volumes from Connected Apps — a bulk SOQL SELECT on 50,000+ records from an AI chat tool is a red flag.

See also: [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources

- [BleepingComputer — Salesloft breached to steal OAuth tokens for Salesforce data-theft attacks](https://www.bleepingcomputer.com/news/security/salesloft-breached-to-steal-oauth-tokens-for-salesforce-data-theft-attacks/) — primary disclosure; OAuth token theft mechanism; confirmed victim list; AWS/Snowflake credential exposure.
- [SecurityWeek — Security Firms Hit by Salesforce–Salesloft Drift Breach](https://www.securityweek.com/security-firms-hit-by-salesforce-salesloft-drift-breach/) — independent corroboration; Cloudflare, Palo Alto, Zscaler named; Salesforce disabling all Salesloft integrations.
- Cross-link: [Vercel/Context.ai breach](2026-04-vercel-context-ai-breach.md) — April 2026 instance of the same AI-tool OAuth pivot class.
- Cross-link: [Klue/Icarus breach](2026-06-klue-icarus-oauth-breach.md) — June 2026 instance; Icarus actor used the Salesloft/Drift template.
- Cross-link: [Composio AI-agent platform breach](2026-05-composio-ai-agent-platform-breach.md) — agent-platform-as-MCP-broker variant of the same class.
