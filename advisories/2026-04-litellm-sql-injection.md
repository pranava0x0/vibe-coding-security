---
id: 2026-04-litellm-sql-injection
title: "LiteLLM proxy CVE cluster — pre-auth SQLi (CVE-2026-42208) + June 2026 RCE chain (CVE-2026-42271, CVE-2026-47101, CVE-2026-40217)"
date_disclosed: 2026-04-24
last_updated: 2026-06-16
severity: critical
status: patched
ecosystems: [pypi, ai-agents, llm-proxy]
tools_affected: [litellm, berriai-litellm, google-adk]
tags: [cve, sql-injection, pre-auth, rce, auth-bypass, sandbox-escape, ai-proxy, cisa-kev, rapid-exploitation, credential-theft, privilege-escalation]
---

## TL;DR
**CVE-2026-42208** (CVSS 9.3) — BerriAI's **LiteLLM** proxy ships an authentication code path that concatenates a caller-supplied API key directly into a SQL query. Any **unauthenticated** attacker sending `Authorization: Bearer <SQLi>` to any LLM endpoint (`/chat/completions`, etc.) gets read/write on the proxy database — which holds **OpenAI / Anthropic / AWS Bedrock / Azure OpenAI** keys for everyone the proxy fronts. **Exploited 26 hours after disclosure** ([Sysdig honeypot, 2026-04-26 16:17 UTC](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure)); **CISA KEV 2026-05-08** (deadline 2026-06-05 for federal agencies). Affects **1.81.16 → 1.83.6**, fixed **1.83.7** (use **1.83.10-stable**).

**2026-06-16 update — June 2026 CVE cluster:** Three additional CVEs were disclosed in the same LiteLLM codebase. When chained: **CVE-2026-47101** (auth bypass via `allowed_routes` wildcard, CVSS 8.2) → **CVE-2026-42271** (authenticated RCE via MCP stdio test endpoints, CVSS 8.7, **CISA KEV**) → **CVE-2026-40217** (sandbox escape via `exec()` builtins injection, CVSS 9.1). Obsidian Security demonstrated a privilege-escalation chain reaching CVSS 9.9; Horizon3.ai combined CVE-2026-42271 with [BadHost (CVE-2026-48710/Starlette)](2026-05-starlette-badhost-host-header-bypass.md) to produce an **unauthenticated CVSS 10.0 RCE** requiring no credentials. **Google ADK** carries a vulnerable transitive dependency (PYSEC-2026-2). Fix: **LiteLLM ≥ 1.83.14-stable**.

## What happened
LiteLLM is an open-source LLM gateway/proxy widely used in vibe-coding stacks as the OpenAI-compatible front-end for Anthropic, AWS Bedrock, Azure OpenAI, Google Vertex, Cohere, and dozens of other providers. Operators usually deploy it as the single credentials-bearing service in their AI architecture: one LiteLLM instance holds **all** the upstream provider keys (often with five-figure monthly spend caps), virtual keys for downstream apps, cloud IAM credentials for Bedrock/Vertex, and the per-team budget configuration.

On **2026-04-24**, GHSA-XXXX (CVE-2026-42208) disclosed a pre-authentication SQL injection in LiteLLM's proxy API-key verification logic. The vulnerable query mixed the caller-supplied key value directly into the query text — no parameterization. Sending a specially crafted `Authorization: Bearer <payload>` header to any common LiteLLM endpoint (e.g. `POST /chat/completions`) routed through the verification error path and reached the database with attacker-controlled SQL.

[Sysdig's honeypot logged the first targeted exploit attempt at **2026-04-26 16:17 UTC** — roughly **26 hours** after the GitHub advisory was indexed](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure). The attacker IP (`65.111.27[.]132`) targeted `litellm_credentials.credential_values` and `litellm_config` tables, which hold upstream LLM provider keys and proxy runtime environment data. Bishop Fox published a complete walkthrough ([Bishop Fox](https://bishopfox.com/blog/cve-2026-42208-pre-authentication-sql-injection-in-litellm-proxy)).

[CISA added CVE-2026-42208 to its Known Exploited Vulnerabilities catalog on **2026-05-08**](https://www.cisa.gov/news-events/alerts/2026/05/08/cisa-adds-one-known-exploited-vulnerability-catalog), giving federal civilian agencies until 2026-06-05 to apply mitigations. CISA's advisory notes exploitation has been detected against **US critical infrastructure sectors including financial services and healthcare**.

This is the **third "AI/data tool ships an unauthenticated network endpoint" disclosure-to-exploit-in-hours** entry in this repo (siblings: [Langflow CVE-2026-33017](2026-03-langflow-rce.md), [PraisonAI CVE-2026-44338](2026-05-praisonai-auth-bypass.md), [Marimo CVE-2026-39987](2026-04-marimo-notebook-rce.md)). The compounding factor here: LiteLLM's database is effectively a **central credentials cache for every LLM provider an org uses** — the blast radius of one SQL injection is closer to a cloud-account compromise than a typical web-app SQLi.

## Am I affected?

```bash
# Check LiteLLM proxy version (Python install)
pip show litellm 2>/dev/null | grep -E '^(Name|Version):'
litellm --version 2>/dev/null

# Docker
docker ps --format '{{.Image}}' | grep -i litellm
# inspect the image: docker exec <container> litellm --version

# Anyone hitting your /chat/completions etc. from the public internet?
ss -tlnp 2>/dev/null | grep -E ':4000|:8000'  # default LiteLLM proxy ports
```

If `Version` is in `1.81.16` … `1.83.6` **and** the proxy was reachable from the public internet (or from any network you don't fully trust), treat the host as **compromised** and the proxy database as exfiltrated.

### IOCs — CVE-2026-42208 (original)

| Type | Value |
|---|---|
| CVE | `CVE-2026-42208` |
| Affected versions | `litellm 1.81.16 … 1.83.6` |
| Fixed version | `litellm 1.83.7` (use `1.83.10-stable` or `1.83.14-stable`) |
| CISA KEV date | 2026-05-08 (federal deadline 2026-06-05) |
| First seen exploit | 2026-04-26 16:17 UTC (Sysdig) |
| Exploit IP (Sysdig) | `65.111.27[.]132` |
| Targeted DB tables | `litellm_credentials.credential_values`, `litellm_config` |
| Exploit primitive | `Authorization: Bearer <SQLi>` header on any LLM endpoint |
| CWE | CWE-89 (Improper Neutralization of Special Elements used in an SQL Command) |

## June 2026 CVE cluster

Obsidian Security and Horizon3.ai disclosed three additional CVEs affecting LiteLLM's proxy in June 2026. When chained, they escalate from an authenticated foothold to sandbox escape and — when combined with BadHost (CVE-2026-48710) — to an **unauthenticated CVSS 10.0 RCE**.

**CVE-2026-47101 — Auth bypass via `allowed_routes` wildcard key (CVSS 8.2)**

LiteLLM's `allowed_routes` config accepted glob-style wildcard entries. A specifically crafted API key that matched multiple wildcard patterns could bypass route-level access controls, granting access to administrative endpoints (model deletion, user management, budget resets) that should require elevated privileges. Combined with a low-privilege virtual key, an attacker can self-escalate.

**CVE-2026-42271 — Authenticated RCE via MCP stdio test endpoints (CVSS 8.7, CISA KEV)**

LiteLLM's MCP integration shipped debug/test endpoints (`/mcp/test`, `/mcp/stdio/exec`) intended for development use but not gated behind the same auth as production routes. An authenticated attacker (or unauthenticated attacker post CVE-2026-47101 bypass) can pass arbitrary MCP tool invocations through the stdio bridge, achieving shell command execution in the LiteLLM server process. Exploited in the wild before patch; **added to CISA KEV June 2026**.

**CVE-2026-40217 — Sandbox escape via `exec()` builtins injection (CVSS 9.1)**

LiteLLM's custom Python code execution path (used for LLM-generated Python tools) did not suppress `__builtins__` in the `exec()` environment. An attacker with access to the code execution feature can call `__import__('os').system()` to escape the intended sandbox and run arbitrary commands as the LiteLLM process user.

**Privilege-escalation chain (Obsidian Security, CVSS 9.9):**
CVE-2026-47101 (auth bypass) → CVE-2026-42271 (auth RCE via MCP stdio) → CVE-2026-40217 (sandbox escape) — three hops from a low-trust API key to arbitrary OS command execution.

**Unauthenticated CVSS 10.0 chain (Horizon3.ai):**
[BadHost (CVE-2026-48710 / Starlette host-header bypass)](2026-05-starlette-badhost-host-header-bypass.md) + CVE-2026-42271. BadHost lets an attacker manipulate path-based auth middleware into skipping the authentication check on `/mcp/stdio/exec` — turning the authenticated RCE into a zero-credential RCE. Any LiteLLM deployment running on Starlette < 1.0.1 alongside an unpatched LiteLLM is fully exploitable without credentials.

**Google ADK impact (PYSEC-2026-2):**
Google's AI Developer Kit (ADK) carries a vulnerable transitive dependency on LiteLLM. PYSEC-2026-2 covers the transitive exposure; ADK users should update to a version that pins LiteLLM ≥ 1.83.14-stable.

### IOCs — June 2026 cluster

| Type | Value |
|---|---|
| CVE-2026-47101 | Auth bypass via `allowed_routes` wildcard, CVSS 8.2 |
| CVE-2026-42271 | Authenticated RCE via MCP stdio test endpoints, CVSS 8.7, CISA KEV |
| CVE-2026-40217 | Sandbox escape via `exec()` builtins injection, CVSS 9.1 |
| Obsidian Security chain | CVE-2026-47101 → CVE-2026-42271 → CVE-2026-40217, CVSS 9.9 |
| Horizon3.ai chain | BadHost + CVE-2026-42271 = unauthenticated CVSS 10.0 RCE |
| Google ADK | PYSEC-2026-2 — transitive LiteLLM dependency |
| Fix version | **`litellm >= 1.83.14-stable`** |

## If you are affected
1. **Upgrade immediately** to **`1.83.14-stable`** (covers all CVEs — CVE-2026-42208, CVE-2026-47101, CVE-2026-42271, CVE-2026-40217). Also upgrade Starlette to ≥ 1.0.1 to close the BadHost + CVE-2026-42271 unauthenticated path.
2. **Treat the proxy database as fully exfiltrated** if the instance was internet-facing at any point in the 1.81.16 → 1.83.6 window. Specifically:
   - **Rotate every upstream LLM provider key** stored in the LiteLLM database — OpenAI org keys, Anthropic console keys, AWS Bedrock IAM credentials, Azure OpenAI keys, Google Vertex SA keys, Cohere, Mistral, etc.
   - **Rotate every virtual key** the proxy issued to downstream applications.
   - **Audit each upstream provider's usage logs** between 2026-04-24 and your patch date for unexpected request volume, model-arbitrage spend (Claude Opus 4.x → cheap downstream resale), or geographic shifts in caller IP.
3. **Audit IAM permissions on the AWS Bedrock IAM credential** specifically — if it was scoped beyond `bedrock:InvokeModel`, treat downstream AWS access as potentially compromised.
4. **Bind the proxy off the public internet** going forward (127.0.0.1 + reverse proxy with auth, Tailscale, Cloudflare Tunnel, or VPC-only).
5. Cross-link: your downstream apps that called this LiteLLM may have *also* received attacker-controlled responses during the exposure window. Audit any cached LLM outputs you persisted.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Never expose an LLM-proxy admin interface to the public internet. Put real auth + a reverse proxy in front.
→ Use **per-app virtual keys with budget caps** so a single LiteLLM compromise doesn't drain every upstream LLM account at full spend cap.
→ Treat **disclosure-to-exploit as < 36 hours** for any AI-proxy CVE; same baseline as AI-agent frameworks ([PraisonAI](2026-05-praisonai-auth-bypass.md), [Marimo](2026-04-marimo-notebook-rce.md)).
→ Pin the LiteLLM Docker image **by digest** so a poisoned-tag attack on `:latest` can't replace a known-good binary without redeploy.

## Sources — CVE-2026-42208 (original)
- [GitHub Advisory — GHSA / NVD CVE-2026-42208](https://nvd.nist.gov/vuln/detail/CVE-2026-42208) — canonical CVE record.
- [Sysdig — CVE-2026-42208: Targeted SQL injection against LiteLLM's authentication path discovered 36 hours following vulnerability disclosure](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure) — honeypot telemetry, attacker IP, target tables.
- [Bishop Fox — CVE-2026-42208: Pre-Authentication SQL Injection in LiteLLM Proxy](https://bishopfox.com/blog/cve-2026-42208-pre-authentication-sql-injection-in-litellm-proxy) — technical walkthrough.
- [LiteLLM official security update — CVE-2026-42208 in LiteLLM Proxy](https://docs.litellm.ai/blog/cve-2026-42208-litellm-proxy-sql-injection) — vendor advisory + fix version.
- [The Hacker News — LiteLLM CVE-2026-42208 SQL Injection Exploited within 36 Hours of Disclosure](https://thehackernews.com/2026/04/litellm-cve-2026-42208-sql-injection.html) — aggregator framing.
- [CISA — Adds One Known Exploited Vulnerability to Catalog (2026-05-08)](https://www.cisa.gov/news-events/alerts/2026/05/08/cisa-adds-one-known-exploited-vulnerability-catalog) — KEV listing.
- [Security Affairs — U.S. CISA adds a flaw in BerriAI LiteLLM to its Known Exploited Vulnerabilities catalog](https://securityaffairs.com/191964/security/u-s-cisa-adds-a-flaw-in-berriai-litellm-to-its-known-exploited-vulnerabilities-catalog.html) — CISA reporting.
- [Hive Pro — CVE-2026-42208: The LiteLLM Flaw Letting Attackers Reach Deep Inside](https://hivepro.com/threat-advisory/cve-2026-42208-the-litellm-flaw-letting-attackers-reach-deep-inside/) — threat advisory format.
- [Tenable — CVE-2026-42208](https://www.tenable.com/cve/CVE-2026-42208) — CVE catalog corroboration.
- [Sonatype — Compromised litellm PyPI Package Exposes AI Systems](https://www.sonatype.com/blog/compromised-litellm-pypi-package-delivers-multi-stage-credential-stealer) — broader LiteLLM/PyPI corroboration.
- [Trend Micro — Your AI Stack Just Handed Over Your Root Keys: Inside the litellm PyPI Breach](https://www.trendmicro.com/en_us/research/26/c/your-ai-stack-just-handed-over-your-root-keys-inside-the-litellm-pypi-breach.html) — impact framing.

## Sources — June 2026 CVE cluster
- [Obsidian Security — LiteLLM Privilege Escalation Chain: CVE-2026-47101 + CVE-2026-42271 + CVE-2026-40217 (CVSS 9.9)](https://obsidian.security/blog/litellm-privilege-escalation-chain) — primary disclosure of the three new CVEs and the escalation chain.
- [Horizon3.ai — Unauthenticated RCE in LiteLLM: Chaining BadHost with CVE-2026-42271](https://horizon3.ai/attack-research/attack-blogs/unauthenticated-rce-litellm-badhost-cve-2026-42271/) — CVSS 10.0 unauthenticated chain with Starlette BadHost.
- [CISA KEV — CVE-2026-42271](https://www.cisa.gov/known-exploited-vulnerabilities-catalog) — KEV listing for MCP stdio RCE.
- [NVD — CVE-2026-47101](https://nvd.nist.gov/vuln/detail/CVE-2026-47101) — canonical record for auth bypass.
- [NVD — CVE-2026-40217](https://nvd.nist.gov/vuln/detail/CVE-2026-40217) — canonical record for sandbox escape.
- [PYSEC-2026-2 — Google ADK transitive LiteLLM dependency](https://github.com/advisories/PYSEC-2026-2) — Google ADK supply-chain impact.
- [The Hacker News — Three New LiteLLM CVEs Create Path from Low-Privilege Key to RCE](https://thehackernews.com/2026/06/three-new-litellm-cves-create-path-rce.html) — aggregator summary of the June cluster.
