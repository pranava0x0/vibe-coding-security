---
id: 2025-11-n8n-ni8mare-rce
title: "n8n Ni8mare + RCE cluster — CVSS 10.0 unauth takeover of workflow automation (Nov 2025 → Feb 2026)"
date_disclosed: 2025-11-09
last_updated: 2026-06-05
severity: critical
status: patched
ecosystems: [npm, self-hosted]
tools_affected: [n8n (workflow automation), any AI agent pipeline using n8n as an orchestration layer]
tags: [rce, unauth, workflow-automation, credential-theft, ai-agents, oauth-pivot]
---

## TL;DR

**Ni8mare** (CVE-2026-21858, CVSS 10.0) is an unauthenticated remote code execution vulnerability in **n8n**, the popular self-hosted workflow automation platform, letting any network-reachable attacker take full control of an n8n instance — and everything it has OAuth access to (Google Drive, Slack, GitHub, HubSpot, etc.). ~26,500 exposed instances observed in the wild. Patched in **n8n 1.121.0** (November 18, 2025). A follow-on authenticated bypass (CVE-2026-25049) was found in February 2026 and **exploited in the wild**.

## What happened

**Ni8mare (CVE-2026-21858)**

Security researcher Dor Attias reported CVE-2026-21858 on November 9, 2025. The vulnerability allowed a remote, unauthenticated attacker to execute arbitrary system commands on the host running n8n and achieve full host compromise — without any valid credentials. n8n patched it in **1.121.0** released November 18, 2025.

Estimated exposed instances at disclosure: **~26,512 to 100,000** (GreyNoise and SecurityWeek estimates vary). GreyNoise observed **potentially malicious scanning activity** targeting exposed n8n endpoints between January 27 and February 3, 2026, logging at least 33,000 requests.

**CVE-2026-25049 (February 2026)**

A second critical flaw (CVSS 9.4) was disclosed in February 2026. It bypasses mitigations added for the prior December 2025 fix (CVE-2025-68613). An **authenticated** attacker with permissions to create or modify workflows could use crafted expressions in workflow parameters to trigger system command execution. Public exploits published.

**March 2026 RCE + credential exposure cluster**

The Hacker News reported additional critical n8n flaws in March 2026 that allow RCE and exposure of stored credentials. These appear to be separate from the Nov/Feb cluster.

**Why this matters for vibe coders and AI agent builders:**

n8n is widely used as an AI workflow orchestration layer — it brokers connections between AI models and dozens of downstream services (Google Drive, Gmail, Slack, GitHub, HubSpot, Notion, Jira, Airtable, Telegram, and more) via OAuth grants and API keys stored in its credential store. A full host compromise via Ni8mare gives an attacker:
- **All stored OAuth tokens** for every connected service
- **All API keys** in the n8n credential store
- **Full workflow execution** — attacker can trigger any configured workflow as if they were the operator
- **LLM API keys** if n8n is orchestrating Claude / GPT-4 / Gemini calls

This is structurally equivalent to the [Composio breach](2026-05-composio-ai-agent-platform-breach.md) pattern: a single foothold in a workflow-broker platform is upstream of every service it touches.

## Am I affected?

```bash
# Check n8n version
npx n8n --version 2>/dev/null
docker exec <n8n-container> n8n --version 2>/dev/null

# Vulnerable: any n8n < 1.121.0 (Ni8mare), < 1.127.x (CVE-2026-25049)
# Check if your instance is network-exposed
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz

# Check for anomalous workflow executions (n8n admin panel)
# Admin → Executions → sort by date, look for unfamiliar triggered workflows
```

**If you're running n8n < 1.121.0 and it's network-reachable:** treat the instance as fully compromised and rotate all credentials it had access to.

**Exposure check:** Run your n8n host/port through Shodan or Censys to confirm whether it's publicly exposed.

## If you are affected

1. **Upgrade to n8n ≥ 1.127.0** (addresses both Ni8mare and CVE-2026-25049; check current latest).
2. **Rotate all OAuth tokens and API keys** stored in n8n's credential store — attacker had full access.
3. **Revoke and re-authorize** every service connection under Settings → Credentials.
4. **Review execution logs** for unusual workflow triggers, especially to external webhooks.
5. **Place n8n behind a VPN or reverse proxy with authentication** — it should never be directly internet-exposed.

## Prevention

- **Never expose n8n directly to the internet.** Use a reverse proxy (nginx, Caddy, Traefik) that requires authentication, or put it behind a VPN/tailnet.
- **Enable n8n's built-in user management and two-factor auth** if you must have it web-accessible.
- **Keep n8n on the latest release.** Like other AI/data tools (Langflow, Marimo, LiteLLM), n8n has a pattern of security patches without always prominent release-note callouts.
- **Apply least-privilege OAuth grants.** Don't grant n8n `service_role` or full write access to services where read-only would suffice for your workflows.
- **Audit stored credentials regularly** — run `Settings → Credentials → list` and remove any you no longer use.

## Sources

- [BleepingComputer — "Max severity Ni8mare flaw lets hackers hijack n8n servers"](https://www.bleepingcomputer.com/news/security/max-severity-ni8mare-flaw-lets-hackers-hijack-n8n-servers/) — Ni8mare CVE-2026-21858 detail, 26,512 instances, GreyNoise exploitation data.
- [The Hacker News — "Critical n8n Vulnerability (CVSS 10.0) Allows Unauthenticated Attackers to Take Full Control"](https://thehackernews.com/2026/01/critical-n8n-vulnerability-cvss-100.html) — broad coverage.
- [CyberSecurityNews — "Ni8mare Vulnerability Let Attackers Hijack n8n Servers"](https://cybersecuritynews.com/ni8mare-hijack-n8n-servers/) — 26,512 hosts exposed figure.
- [The Hacker News — "Critical n8n Flaw CVE-2026-25049 Enables System Command Execution"](https://thehackernews.com/2026/02/critical-n8n-flaw-cve-2026-25049.html) — authenticated bypass, February 2026.
- [BleepingComputer — "Critical n8n flaws disclosed along with public exploits"](https://www.bleepingcomputer.com/news/security/critical-n8n-flaws-disclosed-along-with-public-exploits/) — public exploit availability.
- [NVD — CVE-2026-21858](https://nvd.nist.gov/vuln/detail/CVE-2026-21858) — official CVE record.
- [The Hacker News — "Critical n8n Flaws Allow Remote Code Execution and Exposure of Stored Credentials"](https://thehackernews.com/2026/03/critical-n8n-flaws-allow-remote-code.html) — March 2026 follow-on cluster.
- [SecurityWeek — "Critical Vulnerability Exposes n8n Instances to Takeover Attacks"](https://www.securityweek.com/critical-vulnerability-exposes-n8n-instances-to-takeover-attacks/) — instance count and exploitation risk.
- Cross-reference: [2026-05-mcp-stdio-systemic-rce.md](2026-05-mcp-stdio-systemic-rce.md) (n8n-mcp SSRF), [2026-05-composio-ai-agent-platform-breach.md](2026-05-composio-ai-agent-platform-breach.md) (same "workflow broker as credential hub" pattern).
