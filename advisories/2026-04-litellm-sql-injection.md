---
id: 2026-04-litellm-sql-injection
title: "LiteLLM proxy pre-auth SQL injection — CVE-2026-42208 (April 2026, CISA KEV) + CVE-2026-42271 (June 2026, actively exploited)"
date_disclosed: 2026-04-24
last_updated: 2026-09-15
severity: critical
status: patched
ecosystems: [pypi, ai-agents, llm-proxy, mcp]
tools_affected: [litellm, berriai-litellm]
tags: [cve, sql-injection, pre-auth, ai-proxy, cisa-kev, rapid-exploitation, credential-theft, cryptomining, mcp]
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

Separately, **CVE-2026-42271** (CVSS 3.1: 8.8 / CVSS 4.0: 8.7; **CISA KEV added 2026-06-08**) is a **command injection** flaw in LiteLLM's MCP server preview endpoints. `POST /mcp-rest/test/connection` and `POST /mcp-rest/test/tools/list` accepted a full MCP server configuration in the request body — including `command`, `args`, and `env` fields — without validating the caller's role. Any authenticated user (including low-privilege virtual-key holders) could supply a malicious `stdio`-transport config causing LiteLLM to spawn arbitrary OS commands as a subprocess with the privileges of the proxy process. **Actively exploited in the wild** per CISA KEV. Affected range: `1.74.2` → `1.83.6`; fixed in **1.83.7**. GHSA: `GHSA-v4p8-mg3p-g94g`.

**Remediation:** Upgrade to the latest LiteLLM release (≥ 1.84.0 for all four known CVEs). Given active exploitation, treat any internet-facing LiteLLM instance as potentially compromised and rotate all upstream provider keys regardless of patch status.

## September 2026 update — CVE-2026-59822: MCP auth-bypass chained with CVE-2026-42271 to deploy XMRig, CISA KEV

**CVE-2026-59822** (CVSS 3.1: 8.2 / CVSS 4.0: 8.8; CWE-287 Improper Authentication) — LiteLLM's **MCP Streamable HTTP endpoint** supports OAuth2 passthrough for upstream MCP servers, but the fallback path on a failed LiteLLM key check replaces it with an **empty `UserAPIKeyAuth()` object** instead of rejecting the request. An unauthenticated attacker who sends a fabricated `Authorization` header reaches MCP tooling — listing and calling configured MCP tools and any services they're wired to — without a valid LiteLLM key. Affects **all versions before 1.84.0**; fixed in **1.84.0** (GHSA-7488-6r32-c95q).

**CISA added CVE-2026-59822 to its Known Exploited Vulnerabilities catalog on 2026-09-02**, one of seven CVEs added that day. Per The Hacker News' coverage of the KEV batch, attackers chain CVE-2026-59822 with the **already-tracked CVE-2026-42271** (MCP command-injection, above) to breach LiteLLM gateways and deploy **XMRig cryptocurrency miners** — fingerprinting the host and killing competing miner processes before deploying their own. Wiz reportedly links this activity to the **Qilin ransomware group**, and has observed honeypot probing against LiteLLM's model-enumeration endpoints. Treat any internet-facing LiteLLM instance below 1.84.0 as a live cryptomining target, not just a theoretical risk.

**Remediation:** upgrade to LiteLLM ≥ 1.84.0 (supersedes all prior version guidance in this advisory). If the instance was internet-facing and unpatched, check for unexpected CPU load, unfamiliar processes, and outbound connections to mining pools in addition to the credential-rotation steps above.

## September 2026 update — CVE-2026-37004 (SSTI RCE) + Wiz "Off Guard": ~1 in 10 exposed gateways still accept the example master key

Two additions this window, both raising LiteLLM's already-high exposure:

- **CVE-2026-37004** (CVSS 3.1 **9.8**, CWE-1336) — a **server-side template injection** in the **`/prompts/test`** endpoint: the `dotprompt_content` parameter is rendered through an **unsandboxed `jinja2.Environment`**, so an unauthenticated attacker can execute arbitrary OS commands. Affects **< 1.83.7**; fixed in **1.83.7** (commit `d910a95`). This is a distinct root cause from every prior LiteLLM CVE tracked here (SQLi, header auth-bypass, the MCP OAuth2 fallback) — a fresh RCE surface, not a variant. GHSA-6wvf-77m9-58rm, published 2026-08-27.
- **Wiz "Off Guard" (2026-09-09)** — Wiz scanned ~3,000 internet-facing LiteLLM gateways and found **9.6% still accept the default master key `sk-1234`** (the value shipped in LiteLLM's own Docker Compose and pip quick-starts) and **6.2% require no authentication at all**. From an authenticated position, attackers abuse pass-through endpoints to reach the **cloud metadata service and retrieve IAM credentials**, defeating IMDSv2 via header manipulation — turning a default-credential gateway into cloud compromise. This is the practical exploitation path behind the CISA-KEV CVE-2026-59822 activity already documented above.

**Remediation:** upgrade to the latest LiteLLM (≥ 1.84.0 already required by the MCP/auth CVEs above; ≥ 1.83.7 closes CVE-2026-37004 — take the higher), **replace `sk-1234` and any example master key with a strong unique value**, scope the proxy's IAM role to least privilege, and audit guardrail and pass-through routes. Treat any gateway that ever ran with the default key as compromised.

## September 2026 update — two more SSRF / credential-exfiltration advisories on the vendor's index (published 2026-08-26), one of them fixed back in April

Both from `BerriAI/litellm`'s own advisory tab; neither had press coverage and neither is part of the KEV-driven coverage above.

- **CVE-2026-84377 / GHSA-3cv6-jpf6-8222** (Moderate, CVSS 6.5; published 2026-08-26). An **authenticated** proxy user could redirect outbound provider calls and **exfiltrate the configured provider credentials**: request-body validation was a denylist that missed nested routing and credential parameters, so `api_base` / `base_url` / `model_list` / `fallbacks`-class fields and credential values smuggled in the body were honoured. Affects **< 1.94.0** per the advisory, with backported fixes listed for 1.96.2, 1.95.1, 1.94.3, 1.93.2, 1.92.2, 1.91.5, 1.90.7, 1.89.7 and 1.88.6. Vendor guidance: disable `allow_client_side_credentials`, restrict the proxy to trusted users, and strip those parameters at a reverse proxy. Reporter: stuxf. Read alongside the Wiz "Off Guard" finding above — on a gateway where one in ten callers is effectively anonymous, "authenticated" is a low bar.
- **CVE-2026-59823 / GHSA-hx8v-g79f-8w5f** (Moderate, CVSS 5.3, CWE-918; published 2026-08-26). `is_request_body_safe` blocked `api_base` / `base_url` at the top level but not when nested inside `user_config`, so a caller with a valid virtual key pointed the proxy's outbound request at arbitrary hosts. Affects **≤ 1.83.8**; fixed **1.83.9 — released 2026-04-17**, four months before the advisory was published. Reporter: brettgus. Another instance of this repo's "advisory date is not the fix date" caution: anyone on ≥ 1.83.9 was already covered; anyone pinned below it had no signal until August.

Neither changes the version guidance above (≥ 1.84.0 for the KEV items; take the latest release, which covers all of these).

## Sources
- [GitHub Advisory — GHSA / NVD CVE-2026-42208](https://nvd.nist.gov/vuln/detail/CVE-2026-42208) — canonical CVE record.
- [GitHub Advisory Database — GHSA-6wvf-77m9-58rm (CVE-2026-37004)](https://github.com/advisories/GHSA-6wvf-77m9-58rm) — fetched 2026-09-12: `/prompts/test` unsandboxed-jinja2 SSTI, CVSS 9.8, affected < 1.83.7, fixed 1.83.7, commit `d910a95`, published 2026-08-27.
- [Wiz — Off Guard: Breaking LiteLLM From Authentication Bypass to Cloud Compromise](https://www.wiz.io/blog/off-guard-breaking-litellm-from-authentication-bypass-to-cloud-compromise) — fetched 2026-09-12; 2026-09-09: 9.6% default-key / 6.2% no-auth measurement across ~3,000 gateways, metadata-service IAM-credential path, IMDSv2 header bypass.
- [The Hacker News — Nearly 1 in 10 Exposed LiteLLM Gateways Accept the Default Master Key](https://thehackernews.com/2026/09/nearly-1-in-10-exposed-litellm-gateways.html) — fetched 2026-09-12; 2026-09-09: corroboration of the Wiz figures and CVE-2026-59822 exploitation context.
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
- [GitLab Advisory Database — CVE-2026-59822: LiteLLM MCP Authentication Bypass via OAuth2 Passthrough Fallback](https://advisories.gitlab.com/pypi/litellm/CVE-2026-59822/) — official advisory; description, affected/fixed versions, GHSA-7488-6r32-c95q.
- [CISA — Adds Seven Known Exploited Vulnerabilities to Catalog (2026-09-02)](https://www.cisa.gov/news-events/alerts/2026/09/02/cisa-adds-seven-known-exploited-vulnerabilities-catalog) — KEV listing for CVE-2026-59822.
- [The Hacker News — CISA Adds Seven Exploited Flaws as Attackers Deploy Reverse Shells and Crypto Miners](https://thehackernews.com/2026/09/cisa-adds-seven-exploited-flaws-as.html) — CVE-2026-59822 + CVE-2026-42271 chaining, XMRig deployment, Wiz/Qilin attribution.

**2026-09-15 update sources** — all fetched 2026-09-15:
- [LiteLLM — GHSA-3cv6-jpf6-8222: Authenticated SSRF and provider-credential exfiltration via unvalidated request-body routing parameters (CVE-2026-84377)](https://github.com/BerriAI/litellm/security/advisories/GHSA-3cv6-jpf6-8222) — CVSS 6.5, < 1.94.0, the backport list, the `allow_client_side_credentials` guidance.
- [LiteLLM — GHSA-hx8v-g79f-8w5f: Server-side request forgery via the `user_config` request parameter (CVE-2026-59823)](https://github.com/BerriAI/litellm/security/advisories/GHSA-hx8v-g79f-8w5f) — CVSS 5.3, ≤ 1.83.8 → 1.83.9 (released 2026-04-17), the `user_config` nesting bypass.
- [LiteLLM security advisories index](https://github.com/BerriAI/litellm/security/advisories) — newest entries 2026-08-26.
