---
id: 2026-09-n8n-september-30-ten-advisory-batch
title: "n8n — ten advisories on 2026-09-30 (eight High): an MCP workflow-validation interpreter that lets a read-only user become instance owner via prototype mutation, code execution through the Git node's log operation, an HMAC bypass that approves waiting executions without a signature, a cross-user hijack of pending agent tool approvals, unauthenticated OAuth-client disk exhaustion, SQL injection in the Microsoft SQL node, two stored XSS, credential checks that miss nested sub-workflows; fixed 1.123.83 / 2.42.1 / 2.41.4"
date_disclosed: 2026-09-30
last_updated: 2026-09-30
severity: high
status: patched
ecosystems: [npm, n8n, ai-agents, mcp]
tools_affected: [n8n, "n8n MCP server (instance-level)", "n8n AI Agents module", "n8n AI Workflow Builder", "n8n Git node", "n8n Microsoft SQL node", "n8n Send-and-Wait node", "n8n Chat Trigger"]
tags: [n8n, ghsa-batch, workflow-automation, credential-hub, privilege-escalation, prototype-pollution, mcp, rce, hmac-bypass, agent-approval-hijack, sql-injection, xss, dos]
---

## TL;DR

n8n published **ten security advisories on 2026-09-30** — its fifth batch since July — all fixed in **1.123.83** (v1 line), **2.42.1** (stable) and **2.41.4** (legacy 2.x), which npm shows were published between 06:03 and 06:18 UTC the same morning. None carries a CVE yet. The ones that matter most to this audience: a user with nothing but **`workflow:read` on the instance-level MCP server** could push untrusted code through the MCP workflow-validation interpreter, mutate a shared prototype, and **escalate to instance owner** (GHSA-5jr4-xmvf-frmj, 7.7; MFA on the owner account blocks it); the **Git node's log operation** executes an external program it did not neutralise, so a repository the node is pointed at can run code as the n8n process — "compounded" by the node's use as an **agent tool** (GHSA-x8wx-g24x-3549, 7.7); and a **Send-and-Wait HMAC bypass** lets anyone holding a resume token approve a waiting execution without the signature, triggering whatever the workflow does next under the owner's credentials (GHSA-728h-pmr2-7cgh, 7.0). Three of the ten are in the AI surface specifically: the MCP interpreter, a **cross-user hijack of another user's pending agent tool approval** (GHSA-p3pg-xw4f-m72c, 6.1), and prototype pollution in the **AI Workflow Builder** (GHSA-3p2g-2wpm-8h3g, 6.0). Upgrade, then enable MFA on every admin.

## What happened

n8n's advisory tab carried ten new entries on 2026-09-30, each published with "No known CVE" and a set of "incomplete protection, short-term only" workarounds. Ranked by CVSS 4.0:

- **GHSA-3qcw-p65v-c7vq — Unauthenticated Unbounded OAuth Client Persistence via the Authorize Endpoint (8.2, High).** The unauthenticated authorize endpoint resolved OAuth clients by URL path but keyed rows on the caller's raw identifier, so varying a query string created a new first-party record every time — exempt from the registration cap, with no size limit, expiry or deletion path. Unauthenticated disk exhaustion. Fixed 2.42.1 / 2.41.4. Workaround: deactivate Form/Chat Trigger nodes using `n8nUserAuth`, alert on database growth.
- **GHSA-5jr4-xmvf-frmj — Shared Prototype Mutation Through the MCP Workflow-Validation Interpreter Allows Owner Account Takeover (7.7, High).** The MCP workflow-validation tool ran untrusted code through an interpreter that allowed shared prototype mutation; a caller with only read permission could override built-in methods, bypass server-side permission checks and become instance owner. **MFA-protected owners are not affected.** Fixed 2.42.1 / 2.41.4. Workarounds: deactivate the instance-level MCP server, drop unneeded `workflow:read` MCP OAuth permissions, enable MFA on admins.
- **GHSA-x8wx-g24x-3549 — Code Execution in the Git Node Log Operation via Unneutralized Repository Configuration (7.7, High).** One Git-node operation "invokes an external program" and did not strip dangerous repository configuration, so an attacker controlling a repository the node touches executes code as the n8n process user; the advisory notes the node's usability as an agent tool compounds the risk. Fixed 1.123.83 / 2.42.1 / 2.41.4. Workaround: `NODES_EXCLUDE` the Git node, audit local git configs for program-execution keys. This is the [GitSpawn class](2026-09-gitspawn-git-config-agent-rce-cluster.md) landing in a workflow engine.
- **GHSA-r6g9-5cpp-ppwr — Shared-Workflow Credential Check Misses Nested and Tool Inline Sub-Workflows (7.2, High; v1 only).** Save-time validation "inspected only one node type, one level deep," so an editor could embed credentials they may not use inside inline workflow definitions in Workflow Tool / Workflow Retriever nodes and run them with the owner's values. Fixed 1.123.83.
- **GHSA-29xw-66fq-4xc3 — Stored XSS via Same-Origin Blob URL in the Binary-Data File Preview (7.2, High).** The file-preview modal republished binary data as a same-origin URL in an unsandboxed iframe, stripping protective headers; a member uploading a crafted file runs script as whoever previews it, "typically the instance owner reviewing execution output." Fixed all three lines. Workaround: a restrictive `N8N_CONTENT_SECURITY_POLICY`.
- **GHSA-728h-pmr2-7cgh — Send-and-Wait HMAC Bypass Allows Unauthenticated Approval of Waiting Executions (7.0, High).** The waiting-webhook endpoint accepted two reference formats and validated before normalising the second, so a resume-token holder approves "without the signature approvals require" — and the downstream actions run under the workflow owner's credentials, "including possible command execution." Fixed 2.42.1 / 2.41.4. Workaround: no Send-and-Wait gates on high-consequence actions behind public triggers.
- **GHSA-5qpp-pqww-h7fp — SQL Injection in the Microsoft SQL Node via Expression Interpolation into the Query Field (7.0, High).** Node typeVersion 1 substituted resolved expressions straight into SQL text. Fixed 2.42.1 / 2.41.4; or move to typeVersion ≥ 1.1 with Query Parameters.
- **GHSA-x5cw-hm7v-q7mj — Chat Trigger Stored XSS via `customCss` on the Hosted-Chat Page (7.0, High).** A workflow author's custom CSS was interpolated into the page as markup; on chats published without n8n authentication on the instance's own origin it executes for every visitor. Fixed all three lines.
- **GHSA-p3pg-xw4f-m72c — Cross-User Agent Chat Resume Allows Hijacking Another User's Pending Tool Approval (6.1, Moderate).** The endpoint that resumes a suspended agent tool call "accepted a run identifier from the request body without checking that the checkpoint belonged to the caller": a project member could read another user's private agent conversation and **approve pending tools on their behalf**, with results written into the victim's chat. Fixed 2.42.0 / 2.41.4. Workaround: `N8N_ENABLED_MODULES` without the Agents module.
- **GHSA-3p2g-2wpm-8h3g — Prototype Pollution in the AI Workflow Builder Connection Merge (6.0, Moderate).** Connections were merged using node names as object members with no reserved-key check, so a node named `__proto__` / `constructor` / `prototype` reached the global prototype, process-wide until restart. Fixed all three lines.

Context: this is the fifth n8n batch in three months — the [July 8 and July 22 batches](2026-07-n8n-july-security-advisory-batch.md), the August 19 nine-advisory batch and the [September 16 sixteen-advisory batch](2025-11-n8n-ni8mare-rce.md) (fixed 1.123.80 / 2.40.1 / 2.39.6) — and the second in a row where the AI surface (MCP server, agent approvals, workflow builder) supplies the privilege-escalation path. Community-published n8n nodes are also being impersonated on npm this month (`n8n-nodes-sysdiag2`, `n8n-nodes-buildcheck`, `n8n-nodes-data-transformer-utils`, per Xygeni's September digest), which is the other half of the same story: the platform that holds every integration credential is the platform worth both a CVE and a typosquat. No community-forum "Security update — 30 September" post existed at sweep time; the GHSA pages and the npm publish timestamps are the record.

## Am I affected?

```bash
n8n --version            # or: docker exec <n8n> n8n --version
npm view n8n time --json | grep -E '"(1\.123\.83|2\.42\.1|2\.41\.4)"'   # all three published 2026-09-30

# Exposed if < 1.123.83 (v1) / < 2.42.1 (stable) / < 2.41.4 (legacy 2.x), and especially if any of:
# - the instance-level MCP server is enabled and any OAuth client holds workflow:read
# - the Agents module is on and projects have more than one member
# - a Git node runs against repositories other people can push to
# - Send-and-Wait approvals sit behind public webhook / chat triggers
# - Chat Triggers are published without authentication
# - the instance owner has no MFA
grep -rE 'N8N_ENABLED_MODULES|NODES_EXCLUDE|N8N_CONTENT_SECURITY_POLICY' /path/to/n8n/.env docker-compose.yml 2>/dev/null
```

## If you are affected

1. Upgrade to **1.123.83 / 2.42.1 / 2.41.4** (all three lines shipped 2026-09-30).
2. **Turn on MFA for the instance owner and every admin** — it is the only workaround the vendor calls a real mitigation for the owner-takeover bug.
3. If the instance-level MCP server was enabled with read-scoped OAuth clients, or projects had multiple members with the Agents module on: review the audit log for owner-role changes and approved tool calls you did not make, and **rotate every credential the instance stores** — n8n is a credential hub, and owner is everything. [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).
4. Audit workflows with Git nodes for repositories you do not control; audit the git configs on the n8n host.

## Prevention

- Keep n8n on the current patch within days, not weeks: five batches in twelve weeks means a two-week-old install is behind two of them. [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- The AI features are the new privilege boundary: treat the MCP server, agent tool approvals and the AI builder as admin-grade surfaces — scope MCP OAuth clients minimally, keep shared agents out of multi-member projects, and never let an approval gate be the only control on a command-execution step. [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md), [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- Run n8n behind an identity-aware proxy; unauthenticated endpoints (authorize, waiting-webhook, hosted chat) keep appearing in these batches. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

All vendor advisory pages fetched directly 2026-09-30; each shows "No known CVE" at fetch time.
- [n8n — security advisories index](https://github.com/n8n-io/n8n/security/advisories) — ten entries dated 2026-09-30.
- [GHSA-5jr4-xmvf-frmj — Shared Prototype Mutation Through the MCP Workflow-Validation Interpreter Allows Owner Account Takeover](https://github.com/n8n-io/n8n/security/advisories/GHSA-5jr4-xmvf-frmj) — 7.7, < 2.42.1 / < 2.41.4, the MFA note, credit @sm1ee.
- [GHSA-x8wx-g24x-3549 — Code Execution in the Git Node Log Operation via Unneutralized Repository Configuration](https://github.com/n8n-io/n8n/security/advisories/GHSA-x8wx-g24x-3549) — 7.7, all three lines, the "invokes an external program" and agent-tool wording, credit tr4ce-ju.
- [GHSA-728h-pmr2-7cgh — Send-and-Wait HMAC Bypass Allows Unauthenticated Approval of Waiting Executions](https://github.com/n8n-io/n8n/security/advisories/GHSA-728h-pmr2-7cgh) — 7.0, credit @n0paew.
- [GHSA-3qcw-p65v-c7vq — Unauthenticated Unbounded OAuth Client Persistence via the Authorize Endpoint](https://github.com/n8n-io/n8n/security/advisories/GHSA-3qcw-p65v-c7vq) — 8.2, credit Matsuuu.
- [GHSA-5qpp-pqww-h7fp — SQL Injection in the Microsoft SQL Node](https://github.com/n8n-io/n8n/security/advisories/GHSA-5qpp-pqww-h7fp) — 7.0, credit Matsuuu.
- [GHSA-p3pg-xw4f-m72c — Cross-User Agent Chat Resume Allows Hijacking Another User's Pending Tool Approval](https://github.com/n8n-io/n8n/security/advisories/GHSA-p3pg-xw4f-m72c) — 6.1, fixed 2.42.0 / 2.41.4, credit nlgbao1340.
- [GHSA-r6g9-5cpp-ppwr — Shared-Workflow Credential Check Misses Nested and Tool Inline Sub-Workflows](https://github.com/n8n-io/n8n/security/advisories/GHSA-r6g9-5cpp-ppwr) — 7.2, v1 only, credit SunKimsroul.
- [GHSA-x5cw-hm7v-q7mj — Chat Trigger Stored XSS via customCss](https://github.com/n8n-io/n8n/security/advisories/GHSA-x5cw-hm7v-q7mj) — 7.0, credit Antoine Di Stasi.
- [GHSA-3p2g-2wpm-8h3g — Prototype Pollution in the AI Workflow Builder Connection Merge](https://github.com/n8n-io/n8n/security/advisories/GHSA-3p2g-2wpm-8h3g) — 6.0, credit Matsuuu.
- [GHSA-29xw-66fq-4xc3 — Stored XSS via Same-Origin Blob URL in the Binary-Data File Preview](https://github.com/n8n-io/n8n/security/advisories/GHSA-29xw-66fq-4xc3) — 7.2, credit AdamKorcz.
- npm registry (`npm view n8n time`, 2026-09-30): 2.42.0 published 2026-09-29 07:28 UTC; **1.123.83 06:03, 2.41.4 06:10, 2.42.1 06:18 UTC on 2026-09-30**.
- [NVD API — keyword `n8n`, published 2026-09-25 → 09-30](https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch=n8n&pubStartDate=2026-09-25T00:00:00.000&pubEndDate=2026-09-30T23:59:59.000) — 0 results at sweep time; no CVEs assigned yet.
- [n8n community — Security update — 16 September 2026](https://community.n8n.io/t/security-update-16-september-2026/314102) — the previous batch (sixteen advisories, fixed 1.123.80 / 2.40.1 / 2.39.6), fetched 2026-09-30 to confirm no later forum post existed.
- [Xygeni — Malicious Code Digest, September 2026](https://xygeni.io/blog/malicious-code-digest-monthly-recap-september-2026/) — the three `n8n-nodes-*` impersonation packages (Sept 15 and 23). Fetched 2026-09-30.
- Related in this corpus: [n8n July batches](2026-07-n8n-july-security-advisory-batch.md), [n8n Ni8mare and the August/September batches](2025-11-n8n-ni8mare-rce.md), [Metabase SQLi → n8n breach](2026-08-metabase-sqli-n8n-breach.md), [GitSpawn git-config agent RCE cluster](2026-09-gitspawn-git-config-agent-rce-cluster.md).
