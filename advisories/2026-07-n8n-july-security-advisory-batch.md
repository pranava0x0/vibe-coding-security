---
id: 2026-07-n8n-july-security-advisory-batch
title: "n8n — 10-advisory security batch: host-level RCE via expression evaluator, SSO privilege escalation to instance owner, AI-agent sandbox bypass"
date_disclosed: 2026-07-08
last_updated: 2026-07-17
severity: high
status: patched
ecosystems: [npm, n8n, ai-agents]
tools_affected: [n8n]
tags: [n8n, workflow-automation, credential-hub, rce, privilege-escalation, sso, ssrf, xss, sandbox-bypass]
---

## TL;DR

n8n — the workflow-automation platform this repo already tracks as a "central credentials cache" (see [n8n Ni8mare, CVE-2026-21858](2025-11-n8n-ni8mare-rce.md)) — quietly published **10 security advisories in one day (2026-07-08)** on its own GitHub Security Advisories page, none yet carrying a CVE. The two most serious: a **sanitizer bypass in the legacy expression evaluator giving authenticated users host-level code execution** (CVSS 4.0: 8.9) and a **Token Exchange privilege-escalation bug that mints full-admin Public API tokens** (CVSS 4.0: 8.9). All are fixed in **n8n 1.123.64 / 2.29.8 / 2.30.1**. A separate, narrower **Token Exchange cross-issuer impersonation bug (CVE-2026-59208)** patched three weeks earlier (2026-06-24) only reached mainstream security-press coverage on 2026-07-16, well after this repo's last sweep — both belong in the same "n8n's Enterprise Token Exchange feature has had a rough July" story.

## What happened

n8n's own [GitHub Security Advisories page](https://github.com/n8n-io/n8n/security/advisories) published ten advisories on **2026-07-08**, all fixed in the same release train (**1.123.64**, **2.29.8**, **2.30.1**, or later). As of this sweep, none has an assigned CVE ("No known CVE" on each GHSA page), and no independent security-press outlet has covered this specific batch — sourcing here is n8n's own vendor advisory pages, fetched directly. Ranked by CVSS 4.0 score:

- **GHSA-pm35-fqvh-cq5g — Legacy Expression Evaluator Sanitizer Bypass Leads to Authenticated Code Execution (CVSS 8.9, High).** The default/legacy expression engine's computed-member sanitizer can be bypassed, letting an authenticated user with workflow create/modify permissions achieve **host-level code execution as the n8n process**. Affects < 1.123.64 / < 2.29.8 / < 2.30.1. Workaround: switch to the non-legacy engine (`N8N_EXPRESSION_ENGINE=vm`) or restrict instance access to trusted users.
- **GHSA-777w-rpr6-c52h — Privilege Escalation and Code Execution via Full Public API Key Scope Assignment to Token Exchange JWTs (CVSS 8.9, High).** JWTs minted through the Token Exchange feature receive **full Public API permissions regardless of the actual user's role**, letting a low-privileged attacker with a valid external JWT create/delete users and escalate roles. Requires Token Exchange + Public API enabled and a JWT accepted by a configured trusted key.
- **GHSA-9wcp-9r3j-383q — Stored DOM XSS via Resource Locator `cachedResultUrl` (CVSS 8.4, High).** A persisted `cachedResultUrl` field is passed to `window.open()` with no scheme validation; a malicious workflow can plant a JS payload that executes in a victim's browser when they interact with the workflow's external links.
- **GHSA-35q8-9mj6-wjmf — SSO Instance-Role Provisioning Allows Privilege Escalation to Instance Owner (CVSS 7.7, High).** With Enterprise SSO instance-role provisioning enabled (`N8N_SSO_SCOPES_PROVISION_INSTANCE_ROLE`, off by default), n8n didn't block assignment of the `global:owner` role during SSO login the way other identity paths do — an attacker who controls the instance-role claim at the IdP can log in as full admin.
- **GHSA-x5vx-c2c8-m3w9 — AI Agents Project Viewer Privilege Escalation via run_node_tool (CVSS 7.2, High).** Read-only Project Viewer users could invoke agent node-execution tools without the `agent:execute` scope being checked against their actual permissions, letting them run arbitrary tool nodes and read credential secrets they weren't authorized for — extending to arbitrary command execution where Execute Command/SSH nodes are enabled.
- **GHSA-9w78-79q7-r4fp — Authenticated SSRF via Dynamic Node Parameters Endpoints Allows Internal Network Access (CVSS 6.3, Moderate).** Dynamic node-parameter endpoints lacked authorization checks and accepted absolute URLs overriding declared base URLs, letting any authenticated user force the server to issue requests to arbitrary internal targets (SSRF protection is disabled by default).
- **GHSA-fpg6-x68q-5793 — computer-use Shell Sandbox Not Enforced on Linux and Windows (CVSS 5.5, Moderate).** The `@n8n/computer-use` package's shell tool enforced sandboxing on macOS only; on Linux/Windows, shell commands from the agent ran with **no filesystem or network restrictions**. Fix adds bubblewrap sandboxing on Linux and disables the shell tool where sandboxing can't be established.
- **GHSA-89gh-3pgc-v5h2 — Custom Header Credential Values Leaked in Plaintext into LLM Node Execution Data (CVSS 5.1, Moderate).** Custom HTTP headers on LLM sub-node credentials (OpenAI, Anthropic, Lemonade) appear masked in the UI but are written **in plaintext into execution data** — any authenticated user who can view execution records can read the underlying API keys/secrets, and that data persists in exports.
- **GHSA-q5xf-xhwf-cwqf — Member-Level Users Can Execute Other Users' MCP Server Trigger Workflows via Missing OAuth Authorization Check (CVSS 5.1, Moderate).** n8n's OAuth 2.1 implementation let a member-level user register an OAuth client, self-approve consent for another user's OAuth2-protected MCP Server Trigger workflow, and obtain a token — executing that workflow (and its stored credentials/connected integrations) under the real owner's identity, breaking project isolation.
- **GHSA-33q9-f52j-gc75 — Unauthenticated Endpoint Allows Cancellation of Any User's Active Test Webhook (CVSS 5.1, Moderate).** `DELETE /rest/test-webhook/:id` is processed before authentication middleware runs, letting an unauthenticated caller who knows a workflow ID cancel in-progress test webhook sessions. No impact on production webhooks or persisted data.

**Related, earlier disclosure — Token Exchange cross-issuer impersonation (CVE-2026-59208, GHSA-mq3m-f8x3-579w, CVSS 4.0: 7.6):** published to n8n's own advisories on **2026-06-24** (fixed same day in 2.27.4/2.28.1), this is a *different* Token Exchange bug: when multiple trusted external issuers are configured, identity resolution used only the JWT `sub` claim and ignored `iss`, letting an attacker with a valid token from one trusted issuer authenticate as any victim `sub` under a *different* issuer. It only reached mainstream coverage via [The Hacker News on 2026-07-16](https://thehackernews.com/2026/07/n8n-token-exchange-flaw-could-let.html) — nine days after n8n's own fix shipped, and after this repo's 2026-07-16 sweep. Included here for context since it's part of the same "Token Exchange had a rough July" pattern as GHSA-777w-rpr6-c52h above, but it predates and is independent of the 2026-07-08 batch.

## Am I affected?

```bash
n8n --version
```

You're exposed if you self-host n8n **< 1.123.64 / < 2.29.8 / < 2.30.1** (check your branch) and any of:
- You allow non-admin users to create/modify workflows (legacy expression evaluator RCE — the highest-severity item here, and the legacy engine is the *default*).
- You use Token Exchange + Public API together, or Token Exchange with multiple trusted issuers.
- You use Enterprise SSO with `N8N_SSO_SCOPES_PROVISION_INSTANCE_ROLE` enabled.
- You share team projects with agent nodes to lower-privileged Project Viewer members.
- You use `@n8n/computer-use` on Linux or Windows.
- You store LLM sub-node credentials (OpenAI, Anthropic, Lemonade) with custom HTTP headers.
- You use OAuth2-authenticated MCP Server Trigger workflows shared across users.

## If you are affected

1. **Upgrade to n8n ≥ 1.123.64 / ≥ 2.29.8 / ≥ 2.30.1** (whichever matches your branch) — this closes all 10 items in the July 8 batch.
2. **If on an older Token Exchange-enabled build, also confirm you're ≥ 2.27.4 / ≥ 2.28.1** for CVE-2026-59208.
3. Until you can upgrade: switch off the legacy expression engine (`N8N_EXPRESSION_ENGINE=vm`), disable SSO instance-role provisioning, and restrict instance access to trusted users only.
4. **Rotate any LLM-provider API keys stored as custom HTTP headers** on OpenAI/Anthropic/Lemonade credentials — they were written in plaintext into execution data readable by any authenticated user (GHSA-89gh-3pgc-v5h2). Treat this the same as any other credential-hub exposure.
5. Audit execution history and Token Exchange logs for anomalous access before you patched.
6. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- **Treat n8n (and any workflow-automation/iPaaS broker) as a central credentials cache** — the union of every downstream OAuth token and API key it holds is reachable through a single privilege-escalation or RCE bug in the platform itself, not just through the workflows it runs.
- Don't grant workflow create/modify permissions more broadly than necessary; the legacy expression evaluator's RCE requires only that permission level, not admin.
- Don't share agent-enabled projects with viewer-level teammates unless you've confirmed your version has GHSA-x5vx-c2c8-m3w9 fixed.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)

## Sources

- [n8n GitHub Security Advisories — overview page](https://github.com/n8n-io/n8n/security/advisories) — listing of all 10 advisories with dates, fetched directly.
- [GHSA-pm35-fqvh-cq5g — Legacy Expression Evaluator Sanitizer Bypass Leads to Authenticated Code Execution](https://github.com/n8n-io/n8n/security/advisories/GHSA-pm35-fqvh-cq5g)
- [GHSA-777w-rpr6-c52h — Privilege Escalation and Code Execution via Full Public API Key Scope Assignment to Token Exchange JWTs](https://github.com/n8n-io/n8n/security/advisories/GHSA-777w-rpr6-c52h)
- [GHSA-9wcp-9r3j-383q — Stored DOM XSS via Resource Locator cachedResultUrl](https://github.com/n8n-io/n8n/security/advisories/GHSA-9wcp-9r3j-383q)
- [GHSA-35q8-9mj6-wjmf — SSO Instance-Role Provisioning Allows Privilege Escalation to Instance Owner](https://github.com/n8n-io/n8n/security/advisories/GHSA-35q8-9mj6-wjmf)
- [GHSA-x5vx-c2c8-m3w9 — AI Agents Project Viewer Privilege Escalation via run_node_tool](https://github.com/n8n-io/n8n/security/advisories/GHSA-x5vx-c2c8-m3w9)
- [GHSA-9w78-79q7-r4fp — Authenticated SSRF via Dynamic Node Parameters Endpoints Allows Internal Network Access](https://github.com/n8n-io/n8n/security/advisories/GHSA-9w78-79q7-r4fp)
- [GHSA-fpg6-x68q-5793 — computer-use Shell Sandbox Not Enforced on Linux and Windows](https://github.com/n8n-io/n8n/security/advisories/GHSA-fpg6-x68q-5793)
- [GHSA-89gh-3pgc-v5h2 — Custom Header Credential Values Leaked in Plaintext into LLM Node Execution Data](https://github.com/n8n-io/n8n/security/advisories/GHSA-89gh-3pgc-v5h2)
- [GHSA-q5xf-xhwf-cwqf — Member-Level Users Can Execute Other Users' MCP Server Trigger Workflows via Missing OAuth Authorization Check](https://github.com/n8n-io/n8n/security/advisories/GHSA-q5xf-xhwf-cwqf)
- [GHSA-33q9-f52j-gc75 — Unauthenticated Endpoint Allows Cancellation of Any User's Active Test Webhook](https://github.com/n8n-io/n8n/security/advisories/GHSA-33q9-f52j-gc75)
- [GHSA-mq3m-f8x3-579w — Cross-Issuer Token Exchange Account Binding via Subject-Only Identity Resolution (CVE-2026-59208)](https://github.com/n8n-io/n8n/security/advisories/GHSA-mq3m-f8x3-579w) — published 2026-06-24, fixed same day; CVE↔GHSA pairing verified directly on this page.
- [The Hacker News — n8n Token Exchange Flaw Could Let Attackers Log In as Users From Another Issuer](https://thehackernews.com/2026/07/n8n-token-exchange-flaw-could-let.html) — independent corroboration of CVE-2026-59208 only (published 2026-07-16); no independent coverage found for the 2026-07-08 batch of 10 as of this sweep — sourced solely from n8n's own vendor advisory pages.

**Sourcing note:** the ten 2026-07-08 advisories are corroborated only by n8n's own GitHub Security Advisories (a single vendor domain, ten separate first-party pages, no assigned CVEs yet). No independent aggregator or research-firm coverage of this specific batch was found as of 2026-07-17. Treated here as a verified vendor disclosure (not a disputed incident claim) given the precision of the CVSS vectors and fixed-version data on each page, but flagged per this repo's two-independent-source standard for full advisories.
