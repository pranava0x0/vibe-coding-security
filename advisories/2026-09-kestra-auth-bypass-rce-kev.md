---
id: 2026-09-kestra-auth-bypass-rce-kev
title: "Kestra OSS — unauthenticated RCE via '/configs' auth-filter bypass (CVE-2026-49869, CISA KEV)"
date_disclosed: 2026-09-02
last_updated: 2026-09-03
severity: critical
status: active
ecosystems: [workflow-automation, java, docker]
tools_affected: [kestra, kestra-io/kestra]
tags: [cve, authentication-bypass, command-injection, rce, unauthenticated, cisa-kev, cryptomining, workflow-orchestration]
---

## TL;DR
**CVE-2026-49869** (CVSS 3.1: 10.0 CRITICAL) — Kestra OSS's `AuthenticationFilter` whitelists its public config endpoint with a **suffix match** (`request.getPath().endsWith("/configs")`) instead of an exact-path match, so any API path that merely *ends* in `configs` skips Basic Auth entirely. Because Kestra ships script-execution plugins by default, an unauthenticated attacker can walk straight through that gap to create and run arbitrary workflows — **remote code execution as root** inside the Kestra worker container, no credentials required. **CISA added it to the Known Exploited Vulnerabilities catalog on 2026-09-02**; Microsoft has documented in-the-wild exploitation reaching back to **late June 2026** (reverse shells, container-environment discovery, cryptocurrency miners, data harvesting). Fixed in **1.0.45** and **1.3.21**.

## What happened
Kestra is an open-source, self-hosted workflow-orchestration platform (YAML-defined pipelines, a large plugin ecosystem, and native script/shell-execution tasks) increasingly used for data and AI-pipeline automation — the same automation-tooling niche this repo already tracks for n8n and similar iPaaS platforms.

Kestra's `AuthenticationFilter` is supposed to gate every API endpoint behind Basic Auth except the public configuration endpoint (`/api/v1/configs`), which intentionally serves non-sensitive instance metadata to unauthenticated clients. The whitelist check does this with a **suffix comparison** — `request.getPath().endsWith("/configs")` — rather than comparing the full path exactly. Any request whose path merely *ends* with the string `configs` (for example a crafted path with an extra segment prepended) satisfies that check and skips authentication, even though it routes to a completely different, privileged handler.

Because Kestra ships with **script-execution plugins enabled by default** (used legitimately to run shell/Python/etc. steps inside workflows), an attacker who reaches an authenticated-in-name-only endpoint this way can create and execute a workflow containing an arbitrary OS command — **unauthenticated remote code execution as root** inside the Kestra worker container.

Microsoft's telemetry places exploitation in the wild as early as **late June 2026**: attackers used `curl`-pipe-shell one-liners to establish reverse shells, performed Docker container-environment discovery, deployed cryptocurrency-mining payloads, and — notably — **encoded and exfiltrated collected reconnaissance data through Kestra's own key-value store interface**, using the compromised tool's own feature set as a covert channel. CISA added CVE-2026-49869 to its KEV catalog on **2026-09-02**, alongside six other actively-exploited flaws including [CVE-2026-59822 (LiteLLM MCP auth bypass)](2026-04-litellm-sql-injection.md) and the already-tracked [CVE-2026-48710 (Starlette BadHost)](2026-05-starlette-badhost-host-header-bypass.md) — all three disclosed the same day by The Hacker News as part of one KEV batch tied to reverse-shell and cryptominer campaigns against exposed developer/AI infrastructure.

**Affected:** Kestra OSS versions prior to 1.0.45, and 1.1.0 through 1.3.20. **Fixed:** 1.0.45 and 1.3.21.

## Am I affected?

```bash
# Check installed Kestra version (Docker)
docker ps --format '{{.Image}}' | grep -i kestra
docker exec <kestra-container> kestra --version 2>/dev/null

# Check version via the (now-patched) API
curl -sk https://your-kestra-host/api/v1/configs | grep -i version

# Is the instance internet-reachable at all? (it should not be, unauthenticated)
curl -sk -o /dev/null -w '%{http_code}\n' https://your-kestra-host/api/v1/flows

# Look for the suffix-match bypass pattern in access logs (any path ending in
# "configs" that isn't exactly /api/v1/configs)
grep -E '/[^ ]*configs(\?| |$)' /var/log/nginx/access.log 2>/dev/null | grep -vE '/api/v1/configs'
```
If the version predates the fixed releases **and** the instance was reachable from an untrusted network at any point, treat the worker container — and anything it had filesystem/network/credential access to — as compromised.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-49869` |
| CVSS 3.1 | 10.0 CRITICAL (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`) |
| Affected | Kestra OSS `< 1.0.45`, and `1.1.0 – 1.3.20` |
| Fixed | `1.0.45`, `1.3.21` |
| CISA KEV added | 2026-09-02 |
| Exploitation observed (Microsoft) | Since late June 2026 |
| Attacker TTPs | `curl`-pipe-shell reverse shells; Docker environment discovery; XMRig-class cryptominer deployment; exfiltration via Kestra's own key-value store API |
| Vulnerable check | `AuthenticationFilter`: `request.getPath().endsWith("/configs")` (suffix match, not exact match) |
| CWE | CWE-287 (Improper Authentication) / CWE-863 (Incorrect Authorization) |

## If you are affected
1. **Upgrade immediately** to Kestra `1.0.45`/`1.3.21` or later.
2. **Treat the worker container as compromised** if it was internet-facing and unpatched at any point since late June 2026 — do not just patch in place.
3. **Rotate every credential the Kestra instance held**: plugin secrets, connected-service API keys/tokens (cloud, database, LLM provider), and any credentials referenced by workflows the instance was configured to run.
4. **Hunt for the documented TTPs**: unexpected outbound connections, unfamiliar cron-like workflows or flow definitions you didn't author, anomalous CPU load consistent with cryptomining, and unexpected entries in Kestra's key-value store (used here as an exfiltration channel).
5. **Rebuild from a clean image** rather than remediating in place, and audit any downstream systems the compromised instance had network reach to.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Never expose a workflow-automation control plane (Kestra, n8n, and similar) to the public internet without a real auth layer in front of it — a self-hosted orchestrator with script-execution plugins is equivalent to giving the network shell access.
→ Don't trust a framework's own path-whitelist logic for what counts as "public" — verify with an exact-match test, not a suffix/prefix check, and confirm with a live probe against a path crafted to abuse the difference.

## Sources
- [CISA — Adds Seven Known Exploited Vulnerabilities to Catalog (2026-09-02)](https://www.cisa.gov/news-events/alerts/2026/09/02/cisa-adds-seven-known-exploited-vulnerabilities-catalog) — official KEV listing, CVE-2026-49869 among seven.
- [The Hacker News — CISA Adds Seven Exploited Flaws as Attackers Deploy Reverse Shells and Crypto Miners](https://thehackernews.com/2026/09/cisa-adds-seven-exploited-flaws-as.html) — exploitation chain (reverse shells, Docker discovery, cryptominer, key-value-store exfiltration), Microsoft attribution of June 2026 in-the-wild activity.
- [NVD — CVE-2026-49869](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-49869) — canonical CVE record, CVSS 10.0, affected/fixed version ranges.
