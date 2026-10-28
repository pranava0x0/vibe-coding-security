---
id: 2026-10-litellm-enterprise-unauthenticated-file-read-master-key-leak-ghsa-w4c7-34wj-hqm8
title: "LiteLLM Enterprise proxy: an unauthenticated request reads a local file and leaks the master key (GHSA-w4c7-34wj-hqm8, 10.0); fixed 1.106.5 and three backports"
date_disclosed: 2026-10-27
last_updated: 2026-10-28
severity: critical
status: patched
ecosystems: [pypi, ai-gateway, ai-agents, mcp]
tools_affected: ["litellm (PyPI) proxy below 1.103.10, below 1.104.8, below 1.105.6 and below 1.106.5, when an Enterprise license is loaded", "ghcr.io/berriai/litellm and Docker Hub images on those lines", "every provider key, master key and salt key an affected proxy's environment holds", "Claude Code, Codex and other agents routed through an affected gateway"]
tags: [litellm, ai-gateway, unauthenticated, file-read, ssrf, credential-theft, master-key, enterprise, rce, patched]
---

## TL;DR
A LiteLLM proxy running with an Enterprise license accepted an unauthenticated request to any LLM route that made the proxy read a local file and send its contents to a URL the request chose; reading `/proc/self/environ` returns the master key and every provider API key, which is full admin on the gateway, and the vendor says some configurations reach Python code execution as root (GHSA-w4c7-34wj-hqm8, Critical, CVSS 3.1 10.0, no CVE as of 2026-10-28). Fixed in 1.103.10, 1.104.8, 1.105.6 and 1.106.5, all on PyPI 2026-10-27 between 19:39 and 19:44 UTC. Open-source deployments without a license do not load the affected code paths. If an Enterprise proxy was reachable from the internet before the upgrade, rotate the master key, the salt key and every provider key it held.

## What happened

BerriAI published [GHSA-w4c7-34wj-hqm8](https://github.com/BerriAI/litellm/security/advisories/GHSA-w4c7-34wj-hqm8) on 2026-10-27 (publisher ojensen-berri): "Unauthenticated file read leaks master key on Enterprise proxy", Critical, CVSS 3.1 10.0 (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`), CWE-73, CWE-200, CWE-306 and CWE-918. The advisory's description: an unauthenticated request to any LLM route on a proxy with an Enterprise license can make the proxy read a local file and send its contents to an attacker-chosen URL; a file such as `/proc/self/environ` exposes `LITELLM_MASTER_KEY` and the provider API keys, which gives the attacker full admin access, and "in some configurations, this can lead to arbitrary Python code execution as root." The advisory says open-source deployments without a license are not affected because the relevant code paths load only with an active Enterprise license. Two finders are credited independently: Dylan Ong at Karmasec and Cyrill Bannwart at Compass Security (GitHub reporter bcyrill). Affected `litellm` below 1.103.10, below 1.104.8, below 1.105.6 and below 1.106.5; patched in those four versions, which PyPI dates to 2026-10-27 19:39 to 19:44 UTC (1.106.4, the prior stable, is 2026-10-25).

The vendor's edge mitigations, for anyone who cannot upgrade today: at the WAF, ingress or reverse proxy, reject or strip POST bodies containing the JSON keys `standard_callback_dynamic_params`, `gcs_path_service_account`, `callbacks`, `success_callback` or `failure_callback`; restrict outbound traffic to the configured LLM provider endpoints so the exfiltration leg fails even if the vulnerable code is reached; keep the proxy off the public internet (VPN, mTLS, authenticating ingress or IP allowlist). The advisory's hardening list adds: load the master key from a secret manager, set a separate salt key, and restrict outbound traffic to known provider endpoints. The key names in that mitigation are the request-level callback-configuration parameters LiteLLM accepts per request; this file states no more about the mechanism than the advisory does, and a third-party write-up read this sweep (HOL) says it inferred the link from a logging change and that the vendor has not published the chain.

This is the seventh LiteLLM file here in eight months and the second CVSS 10 class on the gateway in a month: [the 2026-10-21 release hijack](2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0.md) began with an exposed master key on an internal deployment, [CVE-2026-114612](2026-04-litellm-sql-injection.md) let an internal user forge a proxy-admin token through the salt key, and this one hands the master key to a request with no key at all. A gateway holds every provider key behind it, and three of the four ways in this autumn were the key store, not the model.

## Am I affected?

```bash
# Version; below 1.103.10 / 1.104.8 / 1.105.6 / 1.106.5 on a proxy with an Enterprise license is affected.
pip show litellm 2>/dev/null | grep -i ^version
docker ps --format '{{.Image}}' | grep -i litellm

# Enterprise license loaded? (the affected code paths load only with one)
env | grep -E '^LITELLM_LICENSE=' | sed 's/=.*/=<set>/'
grep -rn 'litellm_license\|LITELLM_LICENSE' /path/to/litellm/config.yaml 2>/dev/null

# Was the proxy reachable without a key from outside? (your ingress, not the proxy, answers this)
# Proxy access logs: POST bodies to /chat/completions, /completions, /embeddings etc. carrying
# "standard_callback_dynamic_params", "gcs_path_service_account", "success_callback", "failure_callback" or "callbacks"
```

If the proxy was internet-reachable on an affected version with a license loaded, assume `/proc/self/environ` was read. There is no exploitation report in the advisory and CISA's KEV JSON read on 2026-10-28 does not list it.

## If you are affected

Upgrade to the patched version on your line, then rotate in this order: `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY` (a leaked salt key is the [CVE-2026-114612](2026-04-litellm-sql-injection.md) admin-forgery key as well), every provider key in the proxy environment and config, and every virtual key the proxy issued, since an admin can list them. Then check provider consoles for usage from the window. [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) covers the provider side; [if your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md) covers a host where the advisory's root code execution case may apply.

## Prevention

- Never expose an LLM gateway to the internet without an authenticating layer in front of it; the advisory's own list starts there.
- Egress-restrict the gateway to its provider endpoints, which turns a file-read-and-send bug into a file read.
- Keep the master key and salt key in a secret manager, not the environment, and make them different values.
- [credential-hygiene](../prevention/credential-hygiene.md) and [agent-sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [BerriAI/litellm — GHSA-w4c7-34wj-hqm8: Unauthenticated file read leaks master key on Enterprise proxy](https://github.com/BerriAI/litellm/security/advisories/GHSA-w4c7-34wj-hqm8) — fetched 2026-10-28: published 2026-10-27, Critical 10.0 with vector, CWEs, affected and patched versions, the Enterprise-only statement, the root code execution sentence, the edge mitigations and key names, the hardening list, credits (Karmasec, Compass Security). Single source: the vendor; no CVE on the page.
- [BerriAI/litellm security advisories tab](https://github.com/BerriAI/litellm/security/advisories) — walked 2026-10-28: the 10-27 row beside the 09-30 salt-key advisory.
- [GitHub Advisory Database — claude listing, sorted by publication](https://github.com/advisories?query=claude+sort%3Apublished-desc) — fetched 2026-10-28: CVE-2026-114612 reviewed 10-27 (the salt-key record, in its own file); this advisory had no database row when read.
- PyPI `litellm` release JSON, queried 2026-10-28: 1.103.10 2026-10-27 19:41 UTC, 1.104.8 19:39, 1.105.6 19:42, 1.106.5 19:44; 1.106.4 2026-10-25; `pip index versions litellm` prints 1.106.5.
- CISA KEV JSON, read 2026-10-28: no LiteLLM entry.
