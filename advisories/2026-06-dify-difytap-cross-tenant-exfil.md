---
id: 2026-06-dify-difytap-cross-tenant-exfil
title: "Dify DifyTap — 4 CVEs allow cross-tenant AI conversation exfiltration (1M+ apps affected; patched 1.14.2)"
date_disclosed: 2026-06-22
last_updated: 2026-06-26
severity: high
status: patched
ecosystems: [mcp, python, api]
tools_affected: [dify, langchain, supabase, claude-code, cursor]
tags: [cve, cross-tenant, data-exposure, prompt-injection, plugin-daemon, authorization-bypass, ai-agent-platform]
---

## TL;DR

Zafran Security disclosed **4 CVEs in Dify** (the open-source LLM app builder powering **1M+ applications** across 50+ industries) that allow authenticated attackers to **read private AI conversations from other customers' tenants**, trigger cross-tenant internal API calls, and exfiltrate documents uploaded by other users. The most severe CVE (**CVE-2026-41948, CVSS 9.4**) reaches through the plugin daemon to internal network endpoints via SSRF. All flaws except CVE-2026-41948 are patched in **Dify 1.14.2** (released June 23 2026); CVE-2026-41948 requires a WAF rule as temporary mitigation until the plugin-daemon fix ships.

## What happened

Zafran Security researchers **Ido Shani** and **Gal Zaban** disclosed four authorization-bypass and SSRF vulnerabilities in the Dify platform, collectively named **"DifyTap"**, on June 22–23, 2026. Dify is used to build and deploy LLM-powered apps at scale — with 146,000 GitHub stars and 1M+ downstream applications across healthcare, finance, and enterprise tooling — making cross-tenant data access particularly high-impact.

### CVE-2026-41947 (CVSS 9.1) — Tracing endpoint tenant validation bypass

Dify's **application tracing configuration endpoints** did not validate that the requesting user's tenant matched the target application. An authenticated editor-level user could set or read trace configurations for **any application** on the same instance, regardless of tenant ownership. In a multi-tenant SaaS deployment this allows cross-customer application access.

### CVE-2026-41948 (CVSS 9.4) — Plugin daemon SSRF / internal API access

The **plugin daemon** exposes two primitives (GET and POST request relay) that allow **any authenticated user** to direct the daemon to make arbitrary HTTP requests to internal endpoints. Insufficient URL sanitization means the daemon can be directed to:

- Internal Kubernetes service-mesh endpoints
- Cloud metadata endpoints (`169.254.169.254`)
- Other Dify tenants' internal application endpoints
- Backend databases or auth services bound to internal interfaces

This is the highest-severity CVE in the set and is **not fully patched in 1.14.2** — a WAF rule blocking requests to the plugin daemon's relay endpoints is the current mitigation while the upstream plugin-daemon fix is developed.

### CVE-2026-41949 (CVSS 7.5) — File UUID cross-tenant document preview

Dify's **file preview endpoint** accepted a file UUID and returned up to 3,000 characters of the document content without validating tenant ownership. Any authenticated user could enumerate and read document excerpts from **any other tenant's uploaded files** by iterating or guessing UUIDs.

### CVE-2026-41950 (CVSS 6.5) — File contents cross-tenant read

A related authorization bypass in Dify's **file content access** allowed authenticated users to read **full file contents** uploaded by other users within the same shared tenant (relevant in multi-workspace deployments where multiple orgs share one Dify instance).

### Blast radius

Dify is often deployed as a multi-tenant AI backend with applications that ingest:
- Customer support conversations (PII)
- Internal knowledge base documents (confidential)
- Code review and developer logs (API keys, tokens)
- Healthcare and financial records

Cross-tenant exfiltration of AI agent conversation history means an attacker can passively harvest whatever sensitive data other tenants have fed to their applications — without needing access to those tenants' credentials.

## Am I affected?

If you run **Dify < 1.14.2** in a multi-tenant or multi-workspace configuration, all four CVEs apply.

```bash
# Check your Dify version
docker exec <dify-api-container> python -c "import importlib.metadata; print(importlib.metadata.version('dify'))" 2>/dev/null || \
  grep "dify" requirements.txt 2>/dev/null

# Or via the Dify web UI: Settings → About
```

**Single-tenant self-hosted deployments** have reduced exposure on CVE-2026-41947, CVE-2026-41949, and CVE-2026-41950 (no other tenants to exfiltrate from), but CVE-2026-41948's SSRF can still reach your internal network from the plugin daemon.

**Cloud-hosted Dify (dify.ai):** Zafran coordinated disclosure with the Dify team; the cloud platform received patches before the public disclosure.

### Was I exfiltrated?

CVE-2026-41947 and CVE-2026-41949 leave minimal log traces if an attacker used valid credentials. Check your Dify application logs for:

```bash
# Unusual tracing configuration requests from unexpected tenants
grep -E "POST /api/apps/[a-f0-9-]+/trace-config" dify-api.log | \
  awk '{print $1,$2,$3}' | sort | uniq -c | sort -rn | head -20

# File preview requests with UUIDs not matching your tenant's uploads
grep -E "GET /files/[a-f0-9-]+" dify-api.log
```

## If you are affected

- **PII or confidential documents may have been read cross-tenant.** File a breach assessment and notify affected tenants under your applicable data-protection obligations.
- For plugin-daemon SSRF (CVE-2026-41948): treat your internal network endpoints as potentially enumerated. See [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
- For general app-level exposure: [If your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md).

## Prevention

**Immediate:**

1. **Upgrade to Dify ≥ 1.14.2** immediately. The upgrade patches CVE-2026-41947, CVE-2026-41949, and CVE-2026-41950.
2. **Apply WAF rule** to block direct requests to the plugin daemon relay endpoints (path `/api/plugin-daemon/*`) from any client other than the Dify API backend, pending CVE-2026-41948 patch.
3. **Network-isolate the plugin daemon** at the network layer — it should not have direct internet egress; route all outbound through an allowlisted proxy.

**Ongoing:**

- **[Credential hygiene](../prevention/credential-hygiene.md)** — rotate secrets in any Dify app that processed sensitive data during the vulnerable window.
- Do not grant external or low-trust users "editor" access on shared Dify instances until CVE-2026-41947 is confirmed patched in your deployment.
- When deploying multi-tenant AI platforms, test for cross-tenant IDOR by attempting to access another account's resource UUIDs with valid credentials.

## Sources

- [Researchers Detail DifyTap Flaws in Dify That Could Expose AI Chats Across Tenants](https://thehackernews.com/2026/06/researchers-detail-difytap-flaws-in.html) — The Hacker News, June 23 2026. Full CVE summary, researcher attribution (Zafran Security), affected versions, and patched version.
- [Data Exposure Flaws Threaten Dify AI Platform Used by 1 Million Apps](https://www.securityweek.com/data-exposure-flaws-threaten-dify-ai-platform-powering-over-1-million-apps/) — SecurityWeek, June 23 2026. Independent coverage confirming severity ratings and WAF mitigation for CVE-2026-41948.
