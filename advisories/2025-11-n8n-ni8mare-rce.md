---
id: 2025-11-n8n-ni8mare-rce
title: "n8n Ni8mare + RCE cluster — CVSS 10.0 unauth takeover of workflow automation (Nov 2025 → June 2026)"
date_disclosed: 2025-11-09
last_updated: 2026-08-17
severity: critical
status: patched
ecosystems: [npm, self-hosted]
tools_affected: [n8n (workflow automation), any AI agent pipeline using n8n as an orchestration layer]
tags: [rce, unauth, workflow-automation, credential-theft, ai-agents, oauth-pivot]
---

## TL;DR

**Ni8mare** (CVE-2026-21858, CVSS 10.0) is an unauthenticated remote code execution vulnerability in **n8n**, the popular self-hosted workflow automation platform, letting any network-reachable attacker take full control of an n8n instance — and everything it has OAuth access to (Google Drive, Slack, GitHub, HubSpot, etc.). ~26,500 exposed instances observed in the wild. Patched in **n8n 1.121.0** (November 18, 2025). A follow-on authenticated bypass (CVE-2026-25049) was found in February 2026 and **exploited in the wild**. June 2026 added **CVE-2026-27577** (CVSS 9.4, expression compiler sandbox escape) and **CVE-2026-27493** (pre-auth RCE via Form node double-evaluation on public endpoints). **Upgrade to the latest n8n release.**

## What happened

**Ni8mare (CVE-2026-21858)**

Security researcher Dor Attias reported CVE-2026-21858 on November 9, 2025. The vulnerability allowed a remote, unauthenticated attacker to execute arbitrary system commands on the host running n8n and achieve full host compromise — without any valid credentials. n8n patched it in **1.121.0** released November 18, 2025.

Estimated exposed instances at disclosure: **~26,512 to 100,000** (GreyNoise and SecurityWeek estimates vary). GreyNoise observed **potentially malicious scanning activity** targeting exposed n8n endpoints between January 27 and February 3, 2026, logging at least 33,000 requests.

**CVE-2026-25049 (February 2026)**

A second critical flaw (CVSS 9.4, some sources report 9.9) was disclosed on **2026-02-04**. It bypasses mitigations added for the prior December 2025 fix (CVE-2025-68613): that earlier fix added a `FunctionThisSanitizer` to block direct property-access patterns like `obj.constructor`, but the sanitizer only recognized regular-function AST nodes. **Arrow functions** (`const {constructor} = () => {}`) produce a different AST node type — an `ObjectPattern` via destructuring, rather than a `MemberExpression` — that the sanitizer never checked, and because arrow functions inherit `this` lexically from their enclosing scope, the payload reaches the unsanitized global context anyway. **Update (added 2026-08-10, no new CVE — additional technical depth on an already-tracked finding):** researchers note this is actually exploitable **unauthenticated**, not just by an authenticated workflow editor as originally summarized — an attacker configures a workflow with a public, no-auth webhook, embeds the destructuring-based payload in a connected node, and activates it; any subsequent HTTP request to the webhook URL executes attacker-chosen system commands as the n8n process, with no login required at all. Patched in **n8n 1.123.17 / 2.5.2**. Public PoCs are available; researchers describe the failure as "every layer said 'this looks safe,' and together they allowed something that was not safe at all" — n8n's expression sandbox has now had this same class of AST-node gap patched at least twice.

**March 2026 RCE + credential exposure cluster**

The Hacker News reported additional critical n8n flaws in March 2026 that allow RCE and exposure of stored credentials. These appear to be separate from the Nov/Feb cluster.

**April 2026 (backfilled this sweep) — CVE-2026-42232: XML node prototype pollution → RCE, the bug CVE-2026-44791 (below) later bypassed**

Published to n8n's own GitHub Security Advisories page on **2026-04-22** as **GHSA-hqr4-h3xv-9m3r** (CVSS 9.4): an authenticated user with workflow create/modify permissions could achieve **global prototype pollution via the XML node** — the parser fails to sanitize keys such as `__proto__`, `constructor`, and `prototype` when converting XML structures into JavaScript objects, and chaining the polluted prototype with other nodes yields arbitrary code execution. Fixed in **n8n 1.123.32 / 2.17.4 / 2.18.1**. Confirmed independently via [SentinelOne's vulnerability database](https://www.sentinelone.com/vulnerability-database/cve-2026-42232/) and Singapore's CSA advisory AL-2026-057. This predates and is distinct from the June 2026 cluster below — CVE-2026-44791 (below) is n8n's own follow-up fix for a **bypass** of this same patch.

**June 2026 — n8n node-level RCE cluster (CVE-2026-44789, CVE-2026-44790, CVE-2026-44791)**

Three additional critical flaws were disclosed in June 2026, all fixed in n8n **1.123.43 / 2.20.7 / 2.22.1**:
- **CVE-2026-44789** (HTTP Request node prototype pollution): user-controlled pagination parameters in the HTTP Request node pollute the JavaScript prototype, bypassing sandbox restrictions and enabling arbitrary code execution.
- **CVE-2026-44790** (Git node argument injection): the Git node passes user-supplied branch and tag names directly into shell arguments without sanitization, allowing a workflow editor to inject shell commands that read arbitrary files or execute code on the n8n host.
- **CVE-2026-44791** (XML node patch bypass): despite the April 2026 fix for CVE-2026-42232 above, attackers could still reach prototype pollution through the XML node via an alternate code path.

Affected: n8n **< 1.123.43** (v1 release line) **/ < 2.20.7 / < 2.22.1** (v2 release lines). Upgrade immediately.

**June 2026 additional — CVE-2026-21877 (CVSS 10.0): authenticated arbitrary file write → RCE**

A second CVSS 10.0 vulnerability (**CVE-2026-21877**, GHSA-v364-rw7m-3263) was disclosed in June 2026 and affects n8n in the same era as Ni8mare. An **authenticated** n8n user with workflow-creation privileges can craft a workflow that causes the n8n process to write arbitrary content to arbitrary paths on the host filesystem. Because n8n typically runs as a system-level service with broad filesystem access, writing a malicious file to `/etc/cron.d/`, a startup script directory, or any path that gets auto-executed yields persistent remote code execution. Fixed in **n8n 1.121.3**; upgrade to ≥ 1.121.3 (or the latest release) immediately.

**CISA KEV — CVE-2025-68613 added March 2026**

**CVE-2025-68613** (the December 2025 authentication-bypass patch that preceded Ni8mare) was added to the **CISA Known Exploited Vulnerabilities (KEV) catalog** in March 2026 after CISA observed active exploitation targeting approximately **24,700 exposed n8n instances**. If you are a US federal agency or contractor, this CVE carried a mandatory remediation deadline; consult your compliance team.

**June 2026 — CVE-2026-27577 (CVSS 9.4): expression compiler sandbox escape**

A sandbox escape vulnerability in n8n's **expression compiler** allows a workflow editor with access to create or modify workflows to break out of the sandboxed JavaScript execution context and achieve arbitrary code execution on the n8n host. The expression compiler evaluates user-supplied JavaScript expressions in n8n workflow nodes; insufficient sandboxing of the compiler's internals allows a crafted expression to escape the intended execution environment. Fixed in the latest n8n release; check the GitHub advisory for the minimum fixed version.

**June 2026 — CVE-2026-27493: Form node double-evaluation → pre-auth RCE via public endpoints**

n8n's **Form node** (used to create public-facing HTML forms that trigger workflows) passes user-submitted form field values into the workflow execution context without adequate sanitization. A double-evaluation bug allows an attacker who submits a crafted form response to a public n8n Form endpoint to inject expressions that the n8n engine evaluates with the workflow's full privileges — achieving **pre-authenticated remote code execution** via any publicly accessible Form node. Because n8n Form endpoints can be exposed to the internet intentionally (they're the whole point of the Form node), this affects any n8n instance with a public Form trigger, not just misconfigured ones. Fixed in the latest n8n release.

**June 2026 — CVE-2026-27495 (CVSS 9.4): JS Task Runner sandbox escape**

n8n's **JavaScript Task Runner** node executes arbitrary user-supplied JavaScript in a sandboxed environment intended to prevent access to the host filesystem and network. **CVE-2026-27495** (CVSS 9.4) breaks out of this sandbox: a crafted JavaScript payload bypasses the isolation primitive and achieves arbitrary code execution on the n8n host. Any authenticated workflow editor can exploit this by adding a JS Task Runner node with a malicious script. Fixed in the latest n8n release.

**June 2026 — CVE-2026-27497 (CVSS 9.4): Merge node SQL mode → arbitrary code / file write**

n8n's **Merge node** in SQL aggregation mode processes user-controlled SQL expressions that are insufficiently sanitized. **CVE-2026-27497** (CVSS 9.4) allows an authenticated workflow editor to inject SQL that causes n8n to write arbitrary content to arbitrary host filesystem paths — yielding persistent code execution via the same arbitrary-file-write → cron / startup-path chain as CVE-2026-21877. Fixed in the latest n8n release.

**June 2026 — CVE-2026-27494**: Details pending coordinated disclosure as of 2026-06-18. Severity reported as critical; associated with the same June 2026 n8n vulnerability batch as CVE-2026-27493 / CVE-2026-27495 / CVE-2026-27497. Upgrade to the latest n8n release to cover all concurrent fixes.

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

# Vulnerable: any n8n < 1.121.0 (Ni8mare), < 1.127.x (CVE-2026-25049),
#             < 1.123.43/2.20.7/2.22.1 (June 2026 node-level cluster CVE-2026-44789 / CVE-2026-44790 / CVE-2026-44791),
#             and additional versions affected by CVE-2026-27577 + CVE-2026-27493 (June 2026) —
#             upgrade to the latest available release.
# Check if your instance is network-exposed
curl -s -o /dev/null -w "%{http_code}" http://localhost:5678/healthz

# Check for anomalous workflow executions (n8n admin panel)
# Admin → Executions → sort by date, look for unfamiliar triggered workflows
```

**If you're running n8n < 1.121.0 and it's network-reachable:** treat the instance as fully compromised and rotate all credentials it had access to.

**Exposure check:** Run your n8n host/port through Shodan or Censys to confirm whether it's publicly exposed.

## If you are affected

1. **Upgrade to the latest n8n release** (addresses Ni8mare CVE-2026-21858, CVE-2026-25049, the March 2026 RCE cluster, the authenticated file-write CVE-2026-21877, and the June 2026 node-level cluster; minimum: ≥ 1.123.43 / 2.20.7 / 2.22.1 for the node-level cluster, but upgrade to the latest available version).
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

- [GitHub Security Advisories — n8n has XML Node Prototype Pollution that leads to RCE (GHSA-hqr4-h3xv-9m3r / CVE-2026-42232)](https://github.com/n8n-io/n8n/security/advisories/GHSA-hqr4-h3xv-9m3r) — primary source for the April 2026 backfill: CVE↔GHSA pairing, CVSS score, affected/patched versions confirmed directly on n8n's own advisory page.
- [SentinelOne Vulnerability Database — CVE-2026-42232](https://www.sentinelone.com/vulnerability-database/cve-2026-42232/) — independent corroboration.
- [BleepingComputer — "Max severity Ni8mare flaw lets hackers hijack n8n servers"](https://www.bleepingcomputer.com/news/security/max-severity-ni8mare-flaw-lets-hackers-hijack-n8n-servers/) — Ni8mare CVE-2026-21858 detail, 26,512 instances, GreyNoise exploitation data.
- [The Hacker News — "Critical n8n Vulnerability (CVSS 10.0) Allows Unauthenticated Attackers to Take Full Control"](https://thehackernews.com/2026/01/critical-n8n-vulnerability-cvss-100.html) — broad coverage.
- [CyberSecurityNews — "Ni8mare Vulnerability Let Attackers Hijack n8n Servers"](https://cybersecuritynews.com/ni8mare-hijack-n8n-servers/) — 26,512 hosts exposed figure.
- [The Hacker News — "Critical n8n Flaw CVE-2026-25049 Enables System Command Execution"](https://thehackernews.com/2026/02/critical-n8n-flaw-cve-2026-25049.html) — authenticated bypass, February 2026.
- [BleepingComputer — "Critical n8n flaws disclosed along with public exploits"](https://www.bleepingcomputer.com/news/security/critical-n8n-flaws-disclosed-along-with-public-exploits/) — public exploit availability.
- [NVD — CVE-2026-21858](https://nvd.nist.gov/vuln/detail/CVE-2026-21858) — official CVE record.
- [The Hacker News — "Critical n8n Flaws Allow Remote Code Execution and Exposure of Stored Credentials"](https://thehackernews.com/2026/03/critical-n8n-flaws-allow-remote-code.html) — March 2026 follow-on cluster.
- [SecurityWeek — "Critical Vulnerability Exposes n8n Instances to Takeover Attacks"](https://www.securityweek.com/critical-vulnerability-exposes-n8n-instances-to-takeover-attacks/) — instance count and exploitation risk.
- Cross-reference: [2026-05-mcp-stdio-systemic-rce.md](2026-05-mcp-stdio-systemic-rce.md) (n8n-mcp SSRF), [2026-05-composio-ai-agent-platform-breach.md](2026-05-composio-ai-agent-platform-breach.md) (same "workflow broker as credential hub" pattern).
- [GitLab Advisory Database — CVE-2026-44789: n8n HTTP Request Node pagination prototype pollution → RCE](https://advisories.gitlab.com/npm/n8n/CVE-2026-44789/) — June 2026 cluster (CVE-2026-44789 / CVE-2026-44790 / CVE-2026-44791); prototype pollution, Git-node argument injection, XML node RCE; fixed in 1.123.43 / 2.20.7 / 2.22.1.
- [CyberSecurityNews — Critical n8n Vulnerabilities Expose Automation Nodes to Full RCE](https://cybersecuritynews.com/n8n-rce-vulnerabilities/) — CVE-2026-44789 / CVE-2026-44790 / CVE-2026-44791 prototype-pollution + node-RCE detail.
- [NVD — CVE-2026-44789](https://nvd.nist.gov/vuln/detail/CVE-2026-44789), [CVE-2026-44790](https://nvd.nist.gov/vuln/detail/CVE-2026-44790), [CVE-2026-44791](https://nvd.nist.gov/vuln/detail/CVE-2026-44791) — official CVE records.
- [GitHub Advisory — GHSA-v364-rw7m-3263 (CVE-2026-21877, authenticated file-write → RCE, fixed 1.121.3)](https://github.com/advisories/GHSA-v364-rw7m-3263)
- [NVD — CVE-2026-21877](https://nvd.nist.gov/vuln/detail/CVE-2026-21877) — CVSS 10.0 authenticated arbitrary file write.
- [SecureLayer7 — A Deep Dive into CVE-2026-25049: n8n Remote Code Execution](https://blog.securelayer7.net/cve-2026-25049/) — added 2026-08-10: AST-node root cause, arrow-function/destructuring bypass mechanics, unauthenticated-via-public-webhook exploitation path, relationship to CVE-2025-68613.
- [Endor Labs — CVE-2026-25049 Expression Escape Vulnerability Leading to RCE in n8n](https://www.endorlabs.com/learn/cve-2026-25049-n8n-rce) — added 2026-08-10: independent confirmation, patched-version detail.
- [CISA KEV — CVE-2025-68613](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) — added March 2026; ~24,700 exposed instances observed.
- [The Hacker News — n8n CVE-2026-27577 Expression Compiler Sandbox Escape](https://thehackernews.com/2026/06/n8n-cve-2026-27577.html) — June 2026 sandbox escape in expression compiler (CVSS 9.4).
- [GitHub Advisory — CVE-2026-27493 n8n Form node double-evaluation pre-auth RCE](https://github.com/advisories?query=n8n+CVE-2026-27493) — June 2026 pre-auth RCE via public Form node endpoints.
- [NVD — CVE-2026-27495](https://nvd.nist.gov/vuln/detail/CVE-2026-27495) — CVSS 9.4, JS Task Runner sandbox escape.
- [NVD — CVE-2026-27497](https://nvd.nist.gov/vuln/detail/CVE-2026-27497) — CVSS 9.4, Merge node SQL mode arbitrary code/file write.
- [NVD — CVE-2026-27494](https://nvd.nist.gov/vuln/detail/CVE-2026-27494) — additional June 2026 n8n CVE; details pending coordinated disclosure.
