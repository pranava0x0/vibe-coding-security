---
id: 2026-04-litellm-sql-injection
title: "LiteLLM proxy pre-auth SQL injection — CVE-2026-42208 (April 2026, CISA KEV) + CVE-2026-42271 (June 2026, actively exploited)"
date_disclosed: 2026-04-24
last_updated: 2026-06-19
severity: critical
status: patched
ecosystems: [pypi, ai-agents, llm-proxy]
tools_affected: [litellm, berriai-litellm]
tags: [cve, sql-injection, pre-auth, ai-proxy, cisa-kev, rapid-exploitation, credential-theft]
---

## TL;DR
**CVE-2026-42208** (CVSS 9.3) — BerriAI's **LiteLLM** proxy ships an authentication code path that concatenates a caller-supplied API key directly into a SQL query. Any **unauthenticated** attacker sending `Authorization: Bearer <SQLi>` to any LLM endpoint (`/chat/completions`, etc.) gets read/write on the proxy database — which holds **OpenAI / Anthropic / AWS Bedrock / Azure OpenAI** keys for everyone the proxy fronts. **Exploited 26 hours after disclosure** ([Sysdig honeypot, 2026-04-26 16:17 UTC](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure)); **CISA KEV 2026-05-08** (deadline 2026-06-05 for federal agencies). Affects **1.81.16 → 1.83.6**, fixed **1.83.7** (use **1.83.10-stable**).

## What happened
LiteLLM is an open-source LLM gateway/proxy widely used in vibe-coding stacks as the OpenAI-compatible front-end for Anthropic, AWS Bedrock, Azure OpenAI, Google Vertex, Cohere, and dozens of other providers. Operators usually deploy it as the single credentials-bearing service in their AI architecture: one LiteLLM instance holds **all** the upstream provider keys (often with five-figure monthly spend caps), virtual keys for downstream apps, cloud IAM credentials for Bedrock/Vertex, and the per-team budget configuration.

On **2026-04-24**, CVE-2026-42208 disclosed a pre-authentication SQL injection in LiteLLM's proxy API-key verification logic. The vulnerable query mixed the caller-supplied key value directly into the query text — no parameterization. Sending a specially crafted `Authorization: Bearer <payload>` header to any common LiteLLM endpoint (e.g. `POST /chat/completions`) routed through the verification error path and reached the database with attacker-controlled SQL.

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

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-42208` |
| Affected versions | `litellm 1.81.16 … 1.83.6` |
| Fixed version | `litellm 1.83.7` (use `1.83.10-stable`) |
| CISA KEV date | 2026-05-08 (federal deadline 2026-06-05) |
| First seen exploit | 2026-04-26 16:17 UTC (Sysdig) |
| Exploit IP (Sysdig) | `65.111.27[.]132` |
| Targeted DB tables | `litellm_credentials.credential_values`, `litellm_config` |
| Exploit primitive | `Authorization: Bearer <SQLi>` header on any LLM endpoint |
| CWE | CWE-89 (Improper Neutralization of Special Elements used in an SQL Command) |

## If you are affected
1. **Upgrade immediately** to `1.83.10-stable` (or any `>= 1.83.7`).
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

## June 2026 update — CVE-2026-49468: Host header auth bypass + Obsidian Security privilege escalation chain

**CVE-2026-49468** — LiteLLM proxy **< 1.84.0** fails to properly validate the `Host` header on incoming requests. An attacker can forge the `Host` header to bypass authentication checks that rely on origin validation, effectively gaining access to the LiteLLM admin API as an unauthenticated caller. This is distinct from the pre-auth SQL injection (CVE-2026-42208) — it targets the HTTP-layer auth step rather than the SQL layer.

**Obsidian Security privilege escalation chain (mid-June 2026):** Obsidian Security published a compound attack chain that combines CVE-2026-49468 with two additional LiteLLM logic flaws to escalate from **low-privilege API access → full admin → RCE**:
1. Step 1 — Use CVE-2026-49468 (Host header bypass) to bypass authentication on a low-privilege virtual key.
2. Step 2 — Exploit a LiteLLM admin API logic flaw that allows any authenticated user to modify their own account's `user_role` field without admin approval — escalate to `proxy_admin`.
3. Step 3 — As `proxy_admin`, use the `/health/readiness` config endpoint to write attacker-controlled configuration to the LiteLLM host filesystem → code execution via a hot-reloaded config directive.

**Affected:** LiteLLM `< 1.84.0`. **Fixed:** 1.84.0+. Upgrade immediately.

## June 2026 update — Obsidian Security chain (CVE-2026-47101 → CVE-2026-47102 → CVE-2026-40217, CVSS 9.9) + CVE-2026-42271 callback injection (actively exploited)

In June 2026, **Obsidian Security** disclosed a chain that takes a **default low-privilege LiteLLM user to `proxy_admin` and then RCE** on the gateway — which holds every upstream provider key (OpenAI/Anthropic/Gemini/Bedrock/Azure…), the master key, salt key, and DB URL. Obsidian rates the full chain **CVSS 9.9**:

1. **CVE-2026-47101** — authorization bypass: unvalidated `allowed_routes` on the key-management endpoints (`/key/generate`, `/key/update`) lets a non-admin mint a key with access to arbitrary routes, including admin-only ones.
2. **CVE-2026-47102** — privilege escalation: missing field-level authorization on `/user/update` and `/user/bulk_update` lets a caller set their own `user_role`, escalating to `proxy_admin`.
3. **CVE-2026-40217** — RCE: the Custom Code Guardrail `exec()` path is turned into a reverse shell by injecting Python builtins.

**Full chain:** low-privilege request → authorization bypass (CVE-2026-47101) → `proxy_admin` (CVE-2026-47102) → arbitrary code execution (CVE-2026-40217). **No admin credentials required.**

Separately, **CVE-2026-42271** is a **callback-injection** flaw that lets an attacker rewrite Claude Code (and other client) responses in transit with no visible tampering indicator. It is **actively exploited in the wild** and listed in **CISA KEV**.

**Remediation:** Upgrade to the latest LiteLLM release (≥ 1.84.0 for all four known CVEs). Given active exploitation, treat any internet-facing LiteLLM instance as potentially compromised and rotate all upstream provider keys regardless of patch status.

## Sources
- [GitHub Advisory — GHSA / NVD CVE-2026-42208](https://nvd.nist.gov/vuln/detail/CVE-2026-42208) — canonical CVE record.
- [NVD — CVE-2026-42271](https://nvd.nist.gov/vuln/detail/CVE-2026-42271) — command injection, CVSS 8.7, actively exploited.
- [Obsidian Security — Breaking LiteLLM: From Low-Privilege User to Admin and RCE (CVE-2026-47101 / CVE-2026-47102 / CVE-2026-40217)](https://www.obsidiansecurity.com/blog/litellm-privilege-escalation-rce) — canonical CVSS 9.9 chain analysis.
- [Sysdig — CVE-2026-42208: Targeted SQL injection against LiteLLM's authentication path discovered 36 hours following vulnerability disclosure](https://www.sysdig.com/blog/cve-2026-42208-targeted-sql-injection-against-litellms-authentication-path-discovered-36-hours-following-vulnerability-disclosure) — honeypot telemetry, attacker IP, target tables.
- [Bishop Fox — CVE-2026-42208: Pre-Authentication SQL Injection in LiteLLM Proxy](https://bishopfox.com/blog/cve-2026-42208-pre-authentication-sql-injection-in-litellm-proxy) — technical walkthrough.
- [LiteLLM official security update — CVE-2026-42208 in LiteLLM Proxy](https://docs.litellm.ai/blog/cve-2026-42208-litellm-proxy-sql-injection) — vendor advisory + fix version.
- [The Hacker News — LiteLLM CVE-2026-42208 SQL Injection Exploited within 36 Hours of Disclosure](https://thehackernews.com/2026/04/litellm-cve-2026-42208-sql-injection.html) — aggregator framing.
- [CISA — Adds One Known Exploited Vulnerability to Catalog (2026-05-08)](https://www.cisa.gov/news-events/alerts/2026/05/08/cisa-adds-one-known-exploited-vulnerability-catalog) — KEV listing.
- [Security Affairs — U.S. CISA adds a flaw in BerriAI LiteLLM to its Known Exploited Vulnerabilities catalog](https://securityaffairs.com/191964/security/u-s-cisa-adds-a-flaw-in-berriai-litellm-to-its-known-exploited-vulnerabilities-catalog.html) — CISA reporting.
- [The Hacker News — LiteLLM Vulnerability Chain Lets Low-Privilege Users Take Over AI Gateway Servers](https://thehackernews.com/2026/06/litellm-vulnerability-chain-lets-low.html) — independent coverage of the CVE-2026-47101 / 47102 / 40217 chain.
- [Tenable — CVE-2026-42208](https://www.tenable.com/cve/CVE-2026-42208) — CVE catalog corroboration.
- [Sonatype — Compromised litellm PyPI Package Exposes AI Systems](https://www.sonatype.com/blog/compromised-litellm-pypi-package-delivers-multi-stage-credential-stealer) — broader LiteLLM/PyPI corroboration.
- [Trend Micro — Your AI Stack Just Handed Over Your Root Keys: Inside the litellm PyPI Breach](https://www.trendmicro.com/en_us/research/26/c/your-ai-stack-just-handed-over-your-root-keys-inside-the-litellm-pypi-breach.html) — impact framing.
- [GitLab Advisory Database — CVE-2026-49468: LiteLLM authentication bypass via Host header injection](https://advisories.gitlab.com/pypi/litellm/CVE-2026-49468/) — official advisory; affects < 1.84.0.
- [NVD — CVE-2026-49468](https://nvd.nist.gov/vuln/detail/CVE-2026-49468) — Host header auth bypass, affects LiteLLM < 1.84.0.
