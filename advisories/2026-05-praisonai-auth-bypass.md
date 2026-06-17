---
id: 2026-05-praisonai-auth-bypass
title: "PraisonAI authentication bypass — CVE-2026-44338 + platform CVEs (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-06-17
severity: high
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [praisonai, praisonai-platform]
tags: [cve, authentication-bypass, ai-agent-framework, rapid-exploitation, missing-auth, idor, privilege-escalation]
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

## June 2026 update — `praisonai-platform` package: four additional CVEs

A second cluster of vulnerabilities affecting the **`praisonai-platform`** PyPI package (the newer multi-tenant deployment surface, distinct from the legacy `api_server.py` covered by CVE-2026-44338) was disclosed in mid-2026:

| CVE | CVSS | Issue |
|---|---|---|
| **CVE-2026-47418** | high | Cross-workspace IDOR — a user in workspace A can enumerate and read resources belonging to workspace B by supplying the target workspace ID directly. No ownership check. |
| **CVE-2026-47416** | high | Privilege escalation to workspace owner — a regular member can elevate their own role to owner via a crafted API call; no server-side enforcement of role hierarchy. |
| **CVE-2026-47408** | critical | Unauthenticated A2A (agent-to-agent) tool execution — the inter-agent communication endpoint did not require authentication; any network-reachable caller could invoke registered tools as if they were a legitimate agent. |
| **CVE-2026-47409** | medium | Missing auth on member removal — the `DELETE /workspace/members/{id}` endpoint did not verify the caller had owner/admin privileges; any workspace member could remove other members. |

**Fix:** Upgrade `praisonai-platform` to the patched version per the GitHub advisory. If you run a multi-tenant PraisonAI Platform deployment, treat any workspace with untrusted members as potentially compromised for the IDOR and privilege-escalation bugs; treat any internet-exposed A2A endpoint as having been reachable without credentials.

## June 2026 update — MCP path-traversal RCE (CVE-2026-44336) and CWD tools.py injection (CVE-2026-40156)

Two additional high/critical vulnerabilities in PraisonAI's MCP surface and tool-loading logic were disclosed in June 2026:

**CVE-2026-44336** (CVSS 9.4, GHSA-9mqq-jqxf-grvw) — **MCP `tools/call` path-traversal → `.pth` injection → RCE**

PraisonAI's default MCP tool set includes file-manipulation tools (`praisonai.rules.create`, `praisonai.rules.update`, `praisonai.rules.read`, and related methods). These tools accept a filename parameter and write to the path without adequate traversal validation. A local attacker (or a prompt-injected agent) can supply a path like `../../../../site-packages/evil.pth` to write a Python `.pth` file into the active Python environment's `site-packages/` directory. A `.pth` file added to `site-packages/` is **executed automatically at every subsequent Python interpreter startup** — achieving persistent, arbitrary code execution on the PraisonAI host. No authentication is required on the MCP `tools/call` endpoint in default configurations. Fixed in PraisonAI ≥ 4.6.34 (same release that patched CVE-2026-44338).

**CVE-2026-40156** — **Arbitrary code injection via `tools.py` auto-loading from CWD**

PraisonAI uses `importlib.util.spec_from_file_location` to auto-load a file named `tools.py` from the current working directory at startup. If an attacker can place a malicious `tools.py` in a directory where `praisonai` is run (e.g., via a supply-chain-poisoned project, a compromised MCP server, or a shared development directory), the file is executed with the full privileges of the Python process on every PraisonAI startup — no additional user action needed.

**Remediation for CVE-2026-44336 and CVE-2026-40156:**
1. Upgrade to `praisonai >= 4.6.34` (already required for CVE-2026-44338).
2. Audit `site-packages/` directories in your Python environment for unexpected `.pth` files: `python -c "import site; print(site.getsitepackages())"` then `ls -la <site-packages>/` looking for recently modified `.pth` files.
3. Avoid running `praisonai` in directories that accept untrusted files (shared project roots, downloaded repos).
4. If you use PraisonAI in an MCP multi-agent context, audit the MCP `tools/call` history for path-traversal attempts.

## June 2026 update — CVE-2026-39891: template injection via unescaped agent.start() input (CVSS 8.8)

**CVE-2026-39891** (CVSS 8.8) — A **template injection** vulnerability in PraisonAI's `create_agent_centric_tools()` function allows an attacker with the ability to influence the input passed to `agent.start()` to inject malicious template syntax that the framework evaluates in the server context. The `agent.start()` call passes the user's task string directly into the tool-construction pipeline without escaping it, enabling injection of template directives that access the server's environment variables, file system, or execution context — depending on the template engine in use.

**Scope:** Any deployment where end-users or untrusted callers can influence the task string passed to `agent.start()` — including multi-tenant PraisonAI Platform deployments, API endpoints that expose agent execution, or any LLM-driven orchestration where the LLM's output is passed to `agent.start()` (a prompt-injection-to-template-injection chain).

**Remediation:** Upgrade to `praisonai >= 4.6.34` (the same release that addressed CVE-2026-44338 and CVE-2026-44336, with additional input sanitization).

## Sources
- [Sysdig — CVE-2026-44338: PraisonAI authentication bypass in under 4 hours and the growing trend of rapid exploitation](https://www.sysdig.com/blog/cve-2026-44338-praisonai-authentication-bypass-in-under-4-hours-and-the-growing-trend-of-rapid-exploitation)
- [The Hacker News — PraisonAI CVE-2026-44338 Auth Bypass Targeted Within Hours of Disclosure](https://thehackernews.com/2026/05/praisonai-cve-2026-44338-auth-bypass.html)
- [SecurityWeek — Hackers Targeted PraisonAI Vulnerability Hours After Disclosure](https://www.securityweek.com/hackers-targeted-praisonai-vulnerability-hours-after-disclosure/)
- [CSO Online — PraisonAI vulnerability gets scanned within 4 hours of disclosure](https://www.csoonline.com/article/4171215/praisonai-vulnerability-gets-scanned-within-4-hours-of-disclosure.html)
- [Cybersecurity News — PraisonAI Vulnerability Exploited Within Hours of Public Disclosure](https://cybersecuritynews.com/praisonai-vulnerability-exploited/)
- [GBHackers — PraisonAI Vulnerability Actively Exploited Within Hours of Being Made Public](https://gbhackers.com/praisonai-vulnerability-actively-exploited/)
- [GitHub Advisory — GHSA-6rmh-7xcm-cpxj (CVE-2026-44338)](https://github.com/advisories/GHSA-6rmh-7xcm-cpxj)
- [GitHub Advisory — GHSA-9mqq-jqxf-grvw (CVE-2026-44336 MCP path-traversal .pth injection)](https://github.com/advisories/GHSA-9mqq-jqxf-grvw)
- [NVD — CVE-2026-44336](https://nvd.nist.gov/vuln/detail/CVE-2026-44336)
- [Snyk — SNYK-PYTHON-PRAISONAI-CVE-2026-44336](https://snyk.io/vuln/SNYK-PYTHON-PRAISONAI-CVE-2026-44336)
- [GitHub Advisory — CVE-2026-47418 praisonai-platform cross-workspace IDOR](https://github.com/advisories?query=praisonai-platform)
- [GitHub Advisory — CVE-2026-47408 praisonai-platform unauthenticated A2A tool execution](https://github.com/advisories?query=praisonai-platform)
