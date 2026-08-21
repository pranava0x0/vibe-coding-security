---
id: 2025-11-n8n-ni8mare-rce
title: "n8n Ni8mare + RCE cluster — CVSS 10.0 unauth takeover of workflow automation (Nov 2025 → August 2026)"
date_disclosed: 2025-11-09
last_updated: 2026-08-21
severity: critical
status: patched
ecosystems: [npm, self-hosted]
tools_affected: [n8n (workflow automation), any AI agent pipeline using n8n as an orchestration layer]
tags: [rce, unauth, workflow-automation, credential-theft, ai-agents, oauth-pivot]
---

## TL;DR

**Ni8mare** (CVE-2026-21858, CVSS 10.0) is an unauthenticated remote code execution vulnerability in **n8n**, the popular self-hosted workflow automation platform, letting any network-reachable attacker take full control of an n8n instance — and everything it has OAuth access to (Google Drive, Slack, GitHub, HubSpot, etc.). ~26,500 exposed instances observed in the wild. Patched in **n8n 1.121.0** (November 18, 2025). A follow-on authenticated bypass (CVE-2026-25049) was found in February 2026 and **exploited in the wild**. A separate five-CVE sandbox-escape batch (CVE-2026-27493 / -27494 / -27495 / -27497 / -27577) was published **2026-02-25**, headlined by an **unauthenticated** expression-evaluation bug in the Form node (CVE-2026-27493, CVSS 9.5) — all five fixed in **1.123.22 / 2.9.3 / 2.10.1**. *(Corrected 2026-08-21: this advisory previously dated that batch to June 2026 and gave no fixed versions.)* A further **nine-advisory batch landed 2026-08-19**, none carrying a CVE, including two more sandbox escapes to host RCE — fixed in **1.123.73 / 2.35.4 / 2.36.2**. **Upgrade to the latest n8n release**, and bump the `isolated-vm` sandbox underneath it at the same time (see [the August 2026 sandbox-escape advisory](2026-08-vm2-isolated-vm-sandbox-escapes.md)).

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

**February 2026 (five-CVE sandbox-escape batch — dating and patched versions corrected 2026-08-21)**

Earlier revisions of this advisory dated the five-CVE February sandbox-escape cluster to June 2026 and said only "fixed in the latest n8n release." Both were wrong. Fetching each advisory directly (GHSA and NVD, links below) shows all five were **published 2026-02-25** as one coordinated batch, and all five share the same affected range and the same fix:

- **Affected:** n8n `< 1.123.22`, `>= 2.0.0 < 2.9.3`, `>= 2.10.0 < 2.10.1`
- **Patched:** **1.123.22 / 2.9.3 / 2.10.1**

The five:

- **CVE-2026-27493** (GHSA-75g8-rv7v-32f7, **CVSS 9.5**) — *Unauthenticated Expression Evaluation via Form Node.* A **double-evaluation** bug: user input is interpolated into an HTML template on the first evaluation pass, and the second pass scans that rendered output for expression syntax and evaluates it as code. An unauthenticated attacker submitting crafted form data to a public Form node gets arbitrary expression evaluation — and, chained with any of the sandbox escapes below, RCE. Note the precondition the earlier write-up omitted: it requires a workflow where **a form field value begins with `=` and interpolates user-provided input**, so not every public Form node is exploitable.
- **CVE-2026-27577** (GHSA-vpcf-gvg4-6qwr, **CVSS 9.4**) — *Expression Sandbox Escape Leads to RCE.* An authenticated workflow editor escapes the expression sandbox and runs system commands on the host. Root cause: the AST rewriter's `switch` statement was missing the `SpreadElement` node type, so the `process` identifier survived rewriting unmodified and reached the runtime as a bare global.
- **CVE-2026-27494** (**CVSS 3.1: 9.9** / CVSS 4.0: 7.1) — *Python Code node sandbox escape.* Not "pending coordinated disclosure" as this advisory previously stated; NVD published full details 2026-02-25 with NIST's own CVSS 3.1 assessment added 2026-03-05. File exfiltration or RCE; full host compromise on instances using internal Task Runners.
- **CVE-2026-27495** (**CVSS 3.1: 9.9** / CVSS 4.0: 9.4, CWE-94) — *JavaScript Task Runner sandbox escape.* Same shape as CVE-2026-27494 but via the JS runner rather than the Python one.
- **CVE-2026-27497** (**CVSS 3.1: 8.8**, not 9.4 as previously stated here; CWE-89 + CWE-94) — *Merge node SQL query mode.* An authenticated workflow editor executes arbitrary code and writes arbitrary files on the n8n host.

Practical consequence of the correction: if you read the earlier version of this page and concluded you were covered because you upgraded at some point in June, **check your actual version against 1.123.22 / 2.9.3 / 2.10.1** — the fix landed months earlier than this advisory claimed, but so did the disclosure, meaning the exposure window for anyone on an older line has been open considerably longer than stated.

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


## Update — 2026-08-19: a nine-advisory batch, none with a CVE, including two more sandbox escapes to host RCE

n8n published **nine security advisories on its own GHSA index on 2026-08-19**, **none of which carry a CVE** — so CVE-driven scanning will not surface any of them. All nine share the same affected range and fix:

- **Affected:** n8n `< 1.123.73`, `< 2.35.4`, `< 2.36.2`
- **Patched:** **1.123.73 / 2.35.4 / 2.36.2**

The four most serious, each verified on its own advisory page:

- **GHSA-9x83-43r8-5hwc** (CVSS 8.7) — **`$fromAI` prototype leak → RCE in the n8n main process.** The AI-tool-argument helper resolved placeholder names without ownership validation and permitted reserved keys, leaking live host-prototype references on primitive inputs. A low-privileged workflow builder walks the prototype chain to the `Function` constructor and executes arbitrary code **in the main process**. Note what this one is: the helper that exists specifically to let an *LLM* supply tool arguments.
- **GHSA-fg85-4wv2-p98j** (CVSS 7.2) — **expression-sandbox bypass with process-wide persistence.** Free identifiers in spread, computed-key, switch-case, and class-extension positions resolved to process globals instead of being rewritten, exposing 30+ host globals. Mutations **persist process-wide across all later expression evaluations until restart** — so one hostile expression contaminates every subsequent workflow run in that process. (Structurally the same missing-AST-case family as CVE-2026-27577 above, which suggests the rewriter's node coverage is worth auditing rather than patching case-by-case.)
- **GHSA-mwp5-2m32-r54h** (CVSS 7.7) — **Git node command execution from a malicious repository.** The node reset only a fixed list of command-bearing git config keys, omitting the content-filter and merge-driver families, so a malicious repo executes commands during ordinary Add/Commit/Checkout/Pull as the n8n process user. Third distinct Git-node finding in this advisory.
- **GHSA-4r56-g65c-fm83** (CVSS 7.2) — **credential exfiltration via inline workflow JSON.** Credential validation didn't inspect inline workflow JSON across all sub-workflow-executing node types, so a shared-workflow editor — **or any user creating workflows via the REST API, Public API, or MCP** — embeds a node referencing a credential they don't hold; when a user who *does* hold it runs the workflow, the secret resolves and can be shipped to an attacker destination. The MCP path is the one to notice: an agent with workflow-creation access is enough.

Also in the batch (titles and severities from n8n's advisory index): **GHSA-wxwj-8wv6-vpw2** (Elasticsearch/Firestore query injection, Moderate), **GHSA-95ph-833c-4wrp** (Gmail/Brevo local file read + SSRF, High), **GHSA-vrv8-j27g-g7cr** (Strapi/SeaTable/Mailcheck leak decrypted credentials, High), **GHSA-jp9j-jr97-w9pj** (SSRF check validates `uri` while axios dispatches `url` — a textbook instance of this repo's ["two parsers, one string"](2026-05-starlette-badhost-host-header-bypass.md) class, Moderate), and **GHSA-jmmj-93rg-6j39** (Insights API authorization, Moderate).

**Separately — a CVE was assigned to the August 5 MCP node-schema path traversal.** n8n disclosed it on **2026-08-05** as **GHSA-6h4x-896x-fw5m** (CVSS 8.7, affected `< 2.33.4` and `< 2.34.1`, fixed **2.33.4 / 2.34.1**) with no CVE at the time. On **2026-08-20** the GitHub Advisory Database published **GHSA-h5rm-9fhh-5phj** carrying **CVE-2026-77068** (CVSS 8.7, CWE-22) for the same underlying issue: `@n8n/workflow-sdk`'s node-schema loader derives a schema module path from an attacker-supplied node-type string with no traversal check, giving a basic member RCE in the n8n main process. **Two GHSA ids, one vulnerability** — flagged here so a reader tracking both doesn't double-count or assume the second is a new bug.

**Do not patch this in isolation.** n8n runs untrusted JavaScript in **`isolated-vm`**, which shipped its own critical sandbox escape in the same window — see [the vm2 / isolated-vm sandbox-escape advisory](2026-08-vm2-isolated-vm-sandbox-escapes.md). Treat the n8n upgrade and the sandbox dependency bump as one event.

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
Sources for the 2026-08-21 correction of the February sandbox-escape batch (each fetched directly this sweep; the earlier "June 2026 / fixed in latest release" text was not supported by any of them):

- [GitHub Advisory Database — GHSA-75g8-rv7v-32f7 (CVE-2026-27493)](https://github.com/advisories/GHSA-75g8-rv7v-32f7) — CVE↔GHSA pairing, CVSS 9.5, published 2026-02-25, affected ranges and patched versions, and the "form field value begins with `=`" precondition.
- [GitHub Advisory Database — GHSA-vpcf-gvg4-6qwr (CVE-2026-27577)](https://github.com/advisories/GHSA-vpcf-gvg4-6qwr) — CVSS 9.4, published 2026-02-25, same affected/patched ranges.
- [Pillar Security — Zero Click Unauthenticated RCE in n8n: A Contact Form That Executes Shell Commands](https://www.pillar.security/blog/zero-click-unauthenticated-rce-in-n8n-a-contact-form-that-executes-shell-commands) — primary researcher write-up; double-evaluation root cause for CVE-2026-27493 and the missing `SpreadElement` AST-rewriter case for CVE-2026-27577.
- [NVD — CVE-2026-27494](https://nvd.nist.gov/vuln/detail/CVE-2026-27494) — Python Code node sandbox escape; fully analyzed (not "pending disclosure"), CVSS 3.1 9.9, NIST assessment added 2026-03-05.
- [NVD — CVE-2026-27495](https://nvd.nist.gov/vuln/detail/CVE-2026-27495) — JS Task Runner sandbox escape, CVSS 3.1 9.9 / CVSS 4.0 9.4, CWE-94.
- [NVD — CVE-2026-27497](https://nvd.nist.gov/vuln/detail/CVE-2026-27497) — Merge node SQL query mode, CVSS 3.1 **8.8** (this advisory previously said 9.4), CWE-89 + CWE-94.
Sources for the 2026-08-19 batch (added 2026-08-21):

- [n8n GitHub Security Advisories index](https://github.com/n8n-io/n8n/security/advisories) — the nine same-day advisories, their severities, and the shared 1.123.73 / 2.35.4 / 2.36.2 fix line.
- [GHSA-9x83-43r8-5hwc](https://github.com/n8n-io/n8n/security/advisories/GHSA-9x83-43r8-5hwc) — `$fromAI` prototype leak to `Function` constructor, CVSS 8.7.
- [GHSA-fg85-4wv2-p98j](https://github.com/n8n-io/n8n/security/advisories/GHSA-fg85-4wv2-p98j) — expression-sandbox bypass, 30+ host globals, process-wide persistence until restart, CVSS 7.2.
- [GHSA-mwp5-2m32-r54h](https://github.com/n8n-io/n8n/security/advisories/GHSA-mwp5-2m32-r54h) — Git node content-filter / merge-driver config keys not reset, CVSS 7.7.
- [GHSA-4r56-g65c-fm83](https://github.com/n8n-io/n8n/security/advisories/GHSA-4r56-g65c-fm83) — inline-workflow-JSON credential validation gap reachable via REST/Public API/MCP, CVSS 7.2.
- [GitHub Advisory Database — GHSA-h5rm-9fhh-5phj (CVE-2026-77068)](https://github.com/advisories/GHSA-h5rm-9fhh-5phj) and [n8n GHSA-6h4x-896x-fw5m](https://github.com/n8n-io/n8n/security/advisories/GHSA-6h4x-896x-fw5m) — the two advisory ids covering the single `@n8n/workflow-sdk` node-schema path-traversal issue.
