---
id: 2026-10-n8n-october-14-ten-advisory-batch-data-table-cross-project-webhook-xss
title: "n8n: fifteen advisories on 2026-10-14, cross-project Data Table access from a crafted workflow ID, webhook stored XSS; fixed 1.123.85, 2.43.5, 2.44.1"
date_disclosed: 2026-10-14
last_updated: 2026-10-15
severity: high
status: patched
ecosystems: [npm, n8n, ai-agents]
tools_affected: ["n8n (npm) before 1.123.85, before 2.43.5 and before 2.44.1", "n8n Data Tables", "n8n Chat Hub", "n8n webhook responses", "n8n Read/Write Files, Git, MongoDB Atlas Vector Store, Google Cloud Storage, SeaTable Trigger, Quick Base, Microsoft Outlook and SharePoint v1 nodes", "n8n error workflows (fixed 2.42.2 / 2.41.5 on 2026-10-01)"]
tags: [n8n, ghsa-batch, workflow-automation, credential-hub, cross-project, prototype-key, stored-xss, filter-injection, credential-leak, redos, chat-hub, patched]
---

## TL;DR
n8n's advisory tab carried fifteen new entries on 2026-10-14, none with a CVE: ten on page 1, written up below, and five on page 2 (a Local Gateway deep-link re-pair, a prototype-pollution DoS, an unauthenticated Slack token exfiltration and two credential-check gaps) added in the 2026-10-15 update. Eight are fixed in 1.123.85 (v1 line), 2.43.5 (stable) and 2.44.1 (next), which npm shows were published between 07:43 and 08:28 UTC the same morning; the Data Table bug lists 2.44.1 and 2.43.5 only, with no v1 line; and one was fixed on 2026-10-01 in 2.42.2 and 2.41.5. The three High ones: a member who can create workflows could choose the workflow's own ID, and the value `__proto__` made the in-memory owner cache return an invalid project so the Data Table check matched every project on the instance, giving read, write and delete on all Data Table rows (GHSA-wvjj-qg37-pv73, 7.2); webhook error responses and some header-less responses were served without the sandbox Content-Security-Policy, so a workflow owner could serve HTML that runs on the n8n origin with the session of whoever opens the URL (GHSA-mp7q-23hg-35cf, 8.4); and a Read/Write Files glob with many wildcards blocks the event loop until the process restarts (GHSA-m7gv-mpg5-7c9v, 7.1). The other seven leak credential secrets into execution data, skip a credential permission check in inline sub-workflows, let chat-only users register sandboxed tool types, and allow filter injection in three nodes. Upgrade; the per-advisory workarounds are labelled short-term by the vendor.

## What happened

This is the sixth n8n batch since July ([July](2026-07-n8n-july-security-advisory-batch.md), [September 30](2026-09-n8n-september-30-ten-advisory-batch.md)), all published by the same maintainer account with "No known CVE" and a workaround list that each advisory says does not fully remediate the risk. The fix versions: `2.44.1` published to npm 2026-10-14 07:43 UTC (dist-tag `next`), `2.43.5` at 08:15 (`latest` and `stable`), `1.123.85` at 08:28 (`rc`). One of the page-1 ten (the error-workflow advisory) was fixed earlier, in `2.42.2` and `2.41.5` (both 2026-10-01), and published today; one (the Data Table advisory) lists no v1 fix line. Ranked by CVSS 4.0, the vendor's scores:

- **GHSA-mp7q-23hg-35cf — Webhook Responses Without the Sandbox Policy Allow Stored Cross-Site Scripting (8.4, High).** n8n adds a sandbox CSP to webhook responses so workflow HTML does not run on the n8n origin; error responses and some responses without headers skipped it. A user who can create and activate workflows serves HTML that runs as a page on the n8n origin, and a second user who opens the webhook URL lends it their session. All three lines. Reporter Masofgon. Workarounds: trusted users only, audit active webhook workflows in legacy response mode for HTML, restrict `/webhook/*` to trusted sources.
- **GHSA-wvjj-qg37-pv73 — Crafted Workflow ID Gives Access to Data Tables in Other Projects (7.2, High).** Workflow creation accepted a client-supplied ID, and the owner-project cache was keyed on it. A chosen ID returned an invalid owner, and the Data Table project check built from that value matched every project, so a member could list, read, modify and delete Data Table rows across the instance. Fixed 2.44.1 and 2.43.5 (no v1 line listed). Reporter momenashrafff. The advisory's own audit step is the detection: look for a stored workflow ID of `__proto__` and remove it.
- **GHSA-m7gv-mpg5-7c9v — Read/Write Files Node Glob Pattern Causes Unbounded Event-Loop Block (7.1, High).** The File(s) Selector glob compiled on the main event loop with no time limit; a pattern with many wildcards backtracks exponentially and the UI, API, webhooks and health checks stop until restart. All three lines. Reporter Masofgon. Workaround: `NODES_EXCLUDE=n8n-nodes-base.readWriteFile`.
- **GHSA-43v8-hjhm-chjp — Chat Hub: chat-only users can register tool types the product already tries to sandbox (5.3).** The `global:chatUser` role, which cannot create or edit workflows, could add Chat Hub tools that run code in the task runner sandbox, read and write files in allowed directories, or call the instance's workflows, Data Tables and agents, and then invoke them through chat. All three lines. Workarounds include `N8N_SSRF_PROTECTION_ENABLED=true` and not assigning the role to untrusted users.
- **GHSA-qmvv-q3c9-wpp7 — Credential Secrets Exposed in Execution Error Data of Several Nodes (5.3).** The Git, MongoDB Atlas Vector Store and Google Cloud Storage nodes stored an error that contained a credential secret (a Git password or token, a MongoDB password, a Google access token); a user with execution read access but no credential access recovers it. All three lines. Reporter sm1ee.
- **GHSA-crfj-5wv6-8v86 — SeaTable Trigger Node Stores the API Token in Failed Poll Execution Data (5.3).** The same shape for one trigger: the failed poll record kept the request headers, including the API token. All three lines. Reporter kemrec. The vendor's own step list includes rotating affected tokens.
- **GHSA-mgpr-56r4-5c67 — OData $filter Injection in Microsoft Outlook and SharePoint v1 Nodes (5.3).** Expression-bound parameters were concatenated into the `$filter` string unescaped; untrusted input could return the whole mailbox's contact list or redirect a SharePoint pre-write lookup to another item, within the stored credential's scope. All three lines. Reporter sm1ee.
- **GHSA-65mv-v8rp-54wc — Quick Base Node Allows Filter Injection Through the Where Parameter (5.3).** The Where filter went to the API as raw query text; a Get Many could return every record, a Delete could remove every record. The fix adds a Where Parameters option; a filter built with an expression stays unsafe. All three lines. Reporter Masofgon.
- **GHSA-8vrr-mgc5-jg55 — Credential Permission Check Skips Inline Sub-Workflow Nodes With a Non-Boolean Disabled Value (5.1).** The pre-run permission check and the execution engine disagreed on whether a node was disabled, so a node inside an inline sub-workflow passed as skipped and still ran; a member who knows the ID of a credential they cannot use can run such a node and send the decrypted value to a server they control. All three lines. Reporter Masofgon. This is the inline sub-workflow gap from the September batch (GHSA-r6g9-5cpp-ppwr) reached by a different route.
- **GHSA-pcr3-v5vr-qppf — Per-User Credential Theft via Error-Workflow Execution Context Inheritance (5.1).** The error workflow received the failed run's execution context including the identifier of the user who started it; a project editor who set a colleague's workflow to use an error workflow they own ran under the colleague's identity and resolved that user's per-user credential secrets. Fixed 2.42.2 and 2.41.5 (2026-10-01). Reporter sm1ee.

The pattern across the batch is the one this corpus has recorded for n8n since July: an instance is a credential hub, and most of the findings are a lower-privileged member reaching a higher-privileged member's credential or data through a path the role model did not cover. The new entry in the list is the client-chosen primary key: a prototype-named ID poisoning a cache is the same class as the September MCP-interpreter prototype mutation, one layer down.

## Am I affected?

```bash
# Installed version; below 1.123.85 (v1), 2.43.5 (stable) or 2.44.1 (next) is affected.
# The Data Table advisory lists no v1 fix: a v1 instance with Data Tables enabled has no patched version on record.
npm ls -g n8n 2>/dev/null | grep n8n
docker ps --format '{{.Image}}' | grep n8n

# The Data Table advisory's own audit: a stored workflow ID of __proto__
# (n8n CLI, or query the workflow_entity table)
n8n export:workflow --all --output=/tmp/wf.json && grep -n '"id": *"__proto__"' /tmp/wf.json

# Error workflows pointing at another user's workflow (GHSA-pcr3-v5vr-qppf)
grep -o '"errorWorkflow": *"[^"]*"' /tmp/wf.json | sort | uniq -c
```

For the credential-in-execution-data advisories, a user who could view executions of Git, MongoDB Atlas Vector Store, Google Cloud Storage or SeaTable Trigger nodes that failed had the secret; execution read access is the audience.

## If you are affected

Upgrade to 1.123.85, 2.43.5 or 2.44.1; on the v1 line, disable the Data Tables module as well, since that advisory names no v1 fix. Rotate the credentials named above where a failed execution of those nodes was visible to users who could not read the credential, and the SeaTable token regardless. If a `__proto__` workflow exists on the instance, treat every Data Table as read and modified. [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) covers the provider side; [if your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md) covers an instance whose origin served attacker HTML.

## Prevention

- An n8n instance holds every credential its workflows use; keep membership to people you would hand those credentials to directly, which is the vendor's first workaround in all fifteen advisories.
- Restrict `/webhook/*` at the proxy to the sources that need it, and set `N8N_CONTENT_SECURITY_POLICY` yourself rather than relying on per-response headers.
- `NODES_EXCLUDE` the nodes you do not use; the file node, the Git node and Chat Hub each appear in a workaround this month.
- [credential-hygiene](../prevention/credential-hygiene.md) and [ci-cd-hardening](../prevention/ci-cd-hardening.md).

## Update 2026-10-15: five more 2026-10-14 advisories sit on page 2 of the tab

The tab's first page holds ten rows and the batch was written from that page. Page 2, read 2026-10-15, carries five more entries dated 2026-10-14, so the day's batch is fifteen. The five:

- **Local Gateway deep link re-pairs to an attacker's instance, GHSA-cwm2-vhf5-27q9, 5.9.** A crafted `n8n-computer-use://` link made the Local Gateway desktop app connect to an attacker's n8n instance without confirmation, and permissions the user had already granted carried over, so the attacker could act on the user's computer through the gateway. Affected below 2.42.1 and 2.41.4, fixed 2.42.1 and 2.41.4. Workarounds: set `allowedOrigins` to the paired instance URL instead of the default wildcard, quit the app when idle, disable Computer Use if unused. Reporter nlgbao1340.
- **Prototype pollution in workflow-history compaction, GHSA-fvv4-gmv9-xqf5, 7.1 (High).** A low-privileged user saves a workflow whose connections object carries a reserved key; the periodic compaction task's diff routine pollutes built-in objects for the whole process and the instance then fails logins and writes. Affected below 2.41.4; the Patches section names 2.41.4 and 2.42.1. Workaround `N8N_WORKFLOW_HISTORY_ENABLED=false`. Reporter Masofgon.
- **Slack Trigger webhook sends the workspace token to any host, GHSA-3c3p-5959-3ghr, 6.3.** The signing secret is optional and the check returned success when it was absent, so an unauthenticated caller who knows the webhook URL could make the node send the Slack access token to a host of their choice and read the response back. Affected below 1.123.83, 2.42.1 and 2.41.4, fixed in those. Set a Signature Secret on every Slack credential, turn off Download Files, enable `N8N_SSRF_PROTECTION_ENABLED`, rotate Slack tokens on trigger workflows.
- **Execute Sub-workflow `source: url` / `source: localFile` bypasses the shared-workflow credential guard, GHSA-8crx-5h96-q72q, 5.1.** The save-time check cannot see sub-workflows loaded at run time, so an editor gets the project's credentials resolved and decrypted through one. Fixed 1.123.85, 2.44.1, 2.43.5. Reporter kemrec.
- **Credential permission check skips nodes whose default parameters are omitted, GHSA-v9cx-v88r-42vw, 5.1.** Stored parameters omit defaults, defaults are restored at execution, so a member runs a workflow that uses a credential they cannot access and sends the decrypted value out. Fixed 1.123.85, 2.44.1, 2.43.5. Reporter Masofgon.

The fix lines are unchanged: 1.123.85, 2.43.5 and 2.44.1 close the whole day, and the two fixed in 2.42.1 and 2.41.4 were already closed on 2026-09-30. Still no CVE on any of the fifteen. The six CVE ids VulnCheck assigned on 2026-10-14 belong to the [September 30 batch](2026-09-n8n-september-30-ten-advisory-batch.md), not to these.

## Sources
- [n8n — GHSA-wvjj-qg37-pv73](https://github.com/n8n-io/n8n/security/advisories/GHSA-wvjj-qg37-pv73), [GHSA-mp7q-23hg-35cf](https://github.com/n8n-io/n8n/security/advisories/GHSA-mp7q-23hg-35cf), [GHSA-m7gv-mpg5-7c9v](https://github.com/n8n-io/n8n/security/advisories/GHSA-m7gv-mpg5-7c9v), [GHSA-43v8-hjhm-chjp](https://github.com/n8n-io/n8n/security/advisories/GHSA-43v8-hjhm-chjp), [GHSA-qmvv-q3c9-wpp7](https://github.com/n8n-io/n8n/security/advisories/GHSA-qmvv-q3c9-wpp7), [GHSA-8vrr-mgc5-jg55](https://github.com/n8n-io/n8n/security/advisories/GHSA-8vrr-mgc5-jg55), [GHSA-pcr3-v5vr-qppf](https://github.com/n8n-io/n8n/security/advisories/GHSA-pcr3-v5vr-qppf), [GHSA-mgpr-56r4-5c67](https://github.com/n8n-io/n8n/security/advisories/GHSA-mgpr-56r4-5c67), [GHSA-65mv-v8rp-54wc](https://github.com/n8n-io/n8n/security/advisories/GHSA-65mv-v8rp-54wc), [GHSA-crfj-5wv6-8v86](https://github.com/n8n-io/n8n/security/advisories/GHSA-crfj-5wv6-8v86) (all published 2026-10-14; descriptions, CVSS 4.0 vectors, affected and patched versions, workarounds, reporters)
- [n8n security advisories tab](https://github.com/n8n-io/n8n/security/advisories) (the ten rows, read 2026-10-14) and [page 2](https://github.com/n8n-io/n8n/security/advisories?page=2) (five more 2026-10-14 rows, read 2026-10-15)
- [GHSA-cwm2-vhf5-27q9](https://github.com/n8n-io/n8n/security/advisories/GHSA-cwm2-vhf5-27q9), [GHSA-fvv4-gmv9-xqf5](https://github.com/n8n-io/n8n/security/advisories/GHSA-fvv4-gmv9-xqf5), [GHSA-3c3p-5959-3ghr](https://github.com/n8n-io/n8n/security/advisories/GHSA-3c3p-5959-3ghr), [GHSA-8crx-5h96-q72q](https://github.com/n8n-io/n8n/security/advisories/GHSA-8crx-5h96-q72q), [GHSA-v9cx-v88r-42vw](https://github.com/n8n-io/n8n/security/advisories/GHSA-v9cx-v88r-42vw) (the page-2 five, fetched 2026-10-15)
- [npm registry — n8n](https://registry.npmjs.org/n8n) (`time` field: 2.44.1 2026-10-14T07:43Z, 2.43.5 08:15Z, 1.123.85 08:28Z, 2.42.2 and 2.41.5 2026-10-01; dist-tags latest 2.43.5, next 2.44.1, rc 1.123.85, read 2026-10-14)
