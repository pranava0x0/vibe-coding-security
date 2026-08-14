---
id: 2026-08-metabase-sqli-n8n-breach
title: "Metabase CVE-2026-72898 — unauthenticated SQLi (CVSS 10.0), CISA KEV, breached n8n customer data"
date_disclosed: 2026-08-06
last_updated: 2026-08-14
severity: critical
status: active
ecosystems: [metabase, n8n, workflow-automation]
tools_affected: [metabase, n8n]
tags: [sql-injection, rce, credential-hub, cisa-kev, data-breach, self-hosted]
---

## TL;DR
An unauthenticated, CVSS 10.0 SQL-injection bug in self-hosted Metabase (a popular open-source BI/analytics tool many dev teams run alongside their app stack) let attackers take over admin accounts with no credentials at all. CISA added it to the Known Exploited Vulnerabilities catalog on 2026-08-11 with a remediation deadline of today, 2026-08-14. Confirmed victims include **n8n** — the workflow-automation "credential hub" this repo already tracks heavily — whose customer emails, usernames, and bcrypt-hashed passwords were accessed.

## What happened
Metabase's `/api/session/reset_password` endpoint combines Clojure map-merging, JSON keywordization, and HoneySQL's `:raw` escape hatch in a way that lets an unauthenticated request inject unparameterized SQL — full admin account takeover with zero credentials ([Wiz](https://www.wiz.io/blog/inside-the-metabase-sqli-exploited-in-the-wild)). CVE-2026-72898 / GHSA-vwf4-m7j8-wcjf, CWE-89, CVSS scored as high as 10.0.

Affected: self-hosted Metabase **1.58.x through 1.63.3**; fixed in **1.58.24, 1.59.21, 1.60.17, 1.61.11, 1.62.9, 1.63.5**. CISA added the CVE to the **Known Exploited Vulnerabilities catalog on 2026-08-11**, with a federal remediation deadline of **2026-08-14** ([CISA KEV](https://www.cisa.gov/news-events/alerts/2026/08/11/cisa-adds-three-known-exploited-vulnerabilities-catalog)).

Confirmed breached organizations include **n8n**, Framework, Kilo Code (an Anaconda-acquired AI coding platform), Tally, and ChecklyHQ ([The Hacker News](https://thehackernews.com/2026/08/metabase-zero-day-exploited-in-wild.html)).

**n8n's own disclosure** ([blog.n8n.io](https://blog.n8n.io/metabase-security-incident-update/)): unauthorized access to its self-hosted Metabase instance occurred **2026-08-03**; n8n was notified **2026-08-06**; n8n published an updated disclosure **2026-08-11**. 136 records were accessed in total: 5 records exposed name/username/email plus a **bcrypt-hashed n8n Cloud password**, 7 exposed username+email only, and 62 remain unconfirmed which fields were accessed. A separate group of 25 accounts was additionally affected by an unrelated, historical plaintext-password-storage bug uncovered during the investigation. n8n rotated affected credentials and notified Berlin's data protection authority.

This is the same "workflow-broker / credential-hub" blast-radius pattern this repo tracks for n8n's own product CVEs (Ni8mare, the July security batches) — except here the root cause is a *third-party dependency* (Metabase), not n8n's own code, which is exactly why it's worth tracking separately: even a fully-patched credential-hub tool is only as safe as the analytics/BI software sitting next to it in the same infrastructure.

## Am I affected?
```bash
# Check your self-hosted Metabase version
curl -s "https://${METABASE_HOST}/api/health"
# Compare against the affected range: 1.58.x – 1.63.3
```
- If you self-host Metabase anywhere in your infrastructure (including alongside n8n, internal dashboards, or a vibe-coded analytics layer), check your version against the ranges above.
- If you use **n8n Cloud** and haven't rotated your password since 2026-08-11, do so now — n8n's disclosure states passwords were bcrypt-hashed (not plaintext) but recommends rotation regardless.
- Metabase Cloud (the hosted SaaS offering) was not reported as affected — this is a self-hosted-deployment issue.

## If you are affected
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources
- [Wiz — Inside the Metabase SQLi exploited in the wild](https://www.wiz.io/blog/inside-the-metabase-sqli-exploited-in-the-wild) — root-cause technical analysis, CVE/GHSA identification.
- [The Hacker News — Metabase zero-day exploited in the wild](https://thehackernews.com/2026/08/metabase-zero-day-exploited-in-wild.html) — confirmed victim list, patch versions.
- [n8n — Metabase security incident update](https://blog.n8n.io/metabase-security-incident-update/) — n8n's own primary disclosure of the breach timeline, records accessed, and remediation.
- [CISA — CISA Adds Three Known Exploited Vulnerabilities to Catalog](https://www.cisa.gov/news-events/alerts/2026/08/11/cisa-adds-three-known-exploited-vulnerabilities-catalog) — KEV listing date, federal remediation deadline.
