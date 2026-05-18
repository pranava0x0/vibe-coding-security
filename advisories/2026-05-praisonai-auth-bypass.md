---
id: 2026-05-praisonai-auth-bypass
title: "PraisonAI authentication bypass — CVE-2026-44338 (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-05-18
severity: high
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [praisonai]
tags: [cve, authentication-bypass, ai-agent-framework, rapid-exploitation, missing-auth]
---

## TL;DR
**CVE-2026-44338** (CVSS 7.3) — PraisonAI's legacy Flask API server (`api_server.py`, versions **2.5.6 → 4.6.33**) shipped with **`AUTH_ENABLED = False`** hard-coded, exposing `GET /agents` and `POST /chat` to anyone on the network. **Sysdig honeypots saw the first targeted exploit attempt 3 hours, 44 minutes after the advisory was published** — among the fastest public-disclosure-to-scan times yet observed for an AI-agent framework CVE. Fixed in **PraisonAI 4.6.34**; upgrade or switch to the new `serve agents` command (binds 127.0.0.1, requires `--api-key`).

## What happened
On 2026-05-11 at **13:56 UTC**, GitHub published advisory **GHSA-6rmh-7xcm-cpxj** for PraisonAI, an open-source multi-agent orchestration framework. The legacy Flask entrypoint shipped with two "protected" routes:

- `GET /agents` — returns the configured agent metadata, including the agent definition filename and the list of agents.
- `POST /chat` — accepts any JSON body containing a `message` key and dispatches it to the configured agent.

The `check_auth()` helper returned `True` whenever `AUTH_ENABLED` was `False`, which it always was by default. Both routes failed open.

At **17:40 UTC** the same day — **3h44m39s after publication** — a Sysdig-monitored honeypot saw the first targeted probe from a scanner identifying itself as `CVE-Detector/1.0`. The traffic only enumerated agent metadata (no exploit POSTs observed), consistent with a validation/reconnaissance run before later weaponization.

This compresses the same "disclosure-to-exploit" gap that hit Langflow in 2025 (also a Python AI-agent framework) but is even tighter. The pattern is now well-established: **any AI-agent framework that gets a CVE will be scanned for it inside one workday.**

## Am I affected?

```bash
# Check version
pip show praisonai 2>/dev/null | grep -E '^(Name|Version):'

# Did you expose the legacy api_server?
ps eww | grep -E 'praisonai.*api_server|python.*api_server\.py'
ss -tlnp 2>/dev/null | grep -E ':5000|:8000' # default Flask ports
```

If you ran `python api_server.py` (or the `praisonai api` subcommand on a vulnerable version) on a publicly reachable interface, treat the host as compromised: attackers could enumerate agents, send arbitrary chat messages, and depending on agent tool wiring, get RCE or LLM-cost drain.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-44338` |
| GHSA | `GHSA-6rmh-7xcm-cpxj` |
| Affected versions | `praisonai >= 2.5.6, <= 4.6.33` |
| Fixed version | `praisonai 4.6.34` |
| Exploit-validation UA | `CVE-Detector/1.0` |
| Vulnerable paths | `GET /agents`, `POST /chat` (on legacy `api_server.py`) |

## If you are affected
1. Upgrade immediately: `pip install --upgrade 'praisonai>=4.6.34'`.
2. **Stop running `api_server.py` directly.** Use `praisonai serve agents` (the new entrypoint) which binds to `127.0.0.1` and requires `--api-key`.
3. If the legacy server was exposed: rotate any LLM API keys the agent had access to (token theft via cost abuse is the obvious post-exploit move), rotate any tool-use credentials (DB, GitHub, cloud) the agent's tools could call, and review LLM provider logs for unexpected request volume between 2026-05-11 and your patch date.
4. Audit any agent definition files exposed via `/agents` — they may have leaked tool descriptions an attacker can now target.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never expose agent-framework dev servers to the public internet. Default-bind to `127.0.0.1`, put a real reverse proxy with auth in front, or route through a tunnel (Tailscale, Cloudflare Tunnel, Ngrok with basic auth).
→ Treat **disclosure-to-exploit as <4 hours** for any AI-agent framework. Subscribe to vendor security advisories; consider Dependabot security updates with auto-merge for these packages.

## Sources
- [Sysdig — CVE-2026-44338: PraisonAI authentication bypass in under 4 hours and the growing trend of rapid exploitation](https://www.sysdig.com/blog/cve-2026-44338-praisonai-authentication-bypass-in-under-4-hours-and-the-growing-trend-of-rapid-exploitation)
- [The Hacker News — PraisonAI CVE-2026-44338 Auth Bypass Targeted Within Hours of Disclosure](https://thehackernews.com/2026/05/praisonai-cve-2026-44338-auth-bypass.html)
- [SecurityWeek — Hackers Targeted PraisonAI Vulnerability Hours After Disclosure](https://www.securityweek.com/hackers-targeted-praisonai-vulnerability-hours-after-disclosure/)
- [CSO Online — PraisonAI vulnerability gets scanned within 4 hours of disclosure](https://www.csoonline.com/article/4171215/praisonai-vulnerability-gets-scanned-within-4-hours-of-disclosure.html)
- [Cybersecurity News — PraisonAI Vulnerability Exploited Within Hours of Public Disclosure](https://cybersecuritynews.com/praisonai-vulnerability-exploited/)
- [GBHackers — PraisonAI Vulnerability Actively Exploited Within Hours of Being Made Public](https://gbhackers.com/praisonai-vulnerability-actively-exploited/)
- [GitHub Advisory — GHSA-6rmh-7xcm-cpxj](https://github.com/advisories/GHSA-6rmh-7xcm-cpxj)
