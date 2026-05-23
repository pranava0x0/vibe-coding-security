---
id: 2026-04-marimo-notebook-rce
title: "Marimo notebook pre-auth RCE (CVE-2026-39987) — exploited in under 10 hours (April 2026)"
date_disclosed: 2026-04-08
last_updated: 2026-05-23
severity: critical
status: patched
ecosystems: [pypi, ai-data-tools]
tools_affected: [marimo, python-notebooks, data-apps, ml-tooling]
tags: [rce, missing-auth, websocket, cisa-kev, fast-exploit, credential-theft]
---

## TL;DR
**CVE-2026-39987 (CVSS 9.3)** is an **unauthenticated, pre-auth RCE** in **Marimo**, the reactive Python notebook used to build data/ML apps and dashboards. The `/terminal/ws` WebSocket endpoint **skips authentication entirely** (every other WS endpoint calls `validate_auth()`; this one only checks run-mode + platform), so any network-reachable attacker gets a **full PTY shell** and runs arbitrary commands. Sysdig's honeypot saw exploitation **9h 41m after disclosure** — built straight from the advisory text, with no public PoC — and credential theft completed **in under 3 minutes**. **CISA added it to KEV** (2026-04-23). Affects **≤ 0.20.4**; fixed in **0.23.0**.

## What happened
Marimo exposes several WebSocket endpoints. The general `/ws` endpoint correctly calls `validate_auth()` before accepting a connection. The **`/terminal/ws`** endpoint does **not** — it only checks whether the server is in a mode/platform that supports a terminal, then hands the client a **PTY shell**. Any attacker who can reach a running Marimo server (the notebook server, often started for "just local" work but frequently bound to a reachable interface or exposed behind a tunnel/0.0.0.0) connects to that endpoint and **executes shell commands as the notebook process**, unauthenticated.

This is the same shape as the [Langflow unauthenticated RCE](2026-03-langflow-rce.md) and [PraisonAI auth bypass](2026-05-praisonai-auth-bypass.md): an **AI/data-dev tool that ships a powerful network endpoint without an auth gate**, where the disclosure-to-exploit window is now **measured in hours**. Per Sysdig, the attacker's objectives were **reconnaissance and credential theft** — reading `.env` files (DB credentials, API keys, secret tokens) and hunting **SSH private keys** for lateral movement.

Timeline:
- **2026-04-08** — disclosed (CVSS 9.3, fix in 0.23.0).
- **+9h 41m** — first in-the-wild exploitation observed (Sysdig TRT honeypot); credential theft in **< 3 min**.
- **2026-04-23** — added to **CISA KEV**; FCEB remediation deadline 2026-05-07.

## Am I affected?
You are affected if you run **Marimo ≤ 0.20.4** reachable from anything but loopback (a shared dev box, a container with a published port, a `--host 0.0.0.0` launch, a notebook behind an ngrok/Cloudflare tunnel, a cloud workspace).

```bash
# Installed version
pip show marimo 2>/dev/null | grep -i version
python -c "import marimo, sys; print(marimo.__version__)" 2>/dev/null

# Is a marimo server listening on a non-loopback interface?
lsof -iTCP -sTCP:LISTEN -P -n 2>/dev/null | grep -i marimo

# The vulnerable endpoint (do NOT run against systems you don't own)
# A reachable 0.20.4-or-older server answers on /terminal/ws without auth.
```

If you ran an exposed `≤ 0.20.4` server: **assume `.env` secrets and SSH keys on that host are compromised.** Rotate DB credentials, API keys, and SSH keys; check shell history and outbound connections for the exploitation window.

### IOCs / facts

| Type | Value |
|---|---|
| CVE | `CVE-2026-39987` (CVSS 9.3, pre-auth RCE) |
| Vulnerable endpoint | `/terminal/ws` WebSocket — missing `validate_auth()` |
| Affected versions | **≤ 0.20.4** |
| Fixed version | **0.23.0** |
| Disclosure → exploit | **9h 41m** (Sysdig honeypot); cred theft < 3 min |
| KEV | added **2026-04-23**; FCEB deadline 2026-05-07 |
| Attacker goals | recon, `.env` exfil, SSH-key theft for lateral movement |

## If you are affected
→ Upgrade to **Marimo 0.23.0+** immediately; never expose a notebook server to untrusted networks even when patched.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — for `.env` cloud keys and SSH material.
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) — sweep the host and the repo for what the shell could reach.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run notebook/agent servers as an unprivileged user, in a container, with egress allowlists; bind to loopback by default.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — keep secrets out of `.env` on shared/exposed hosts.
→ **Treat AI/data-tool dependencies as time-critical to patch.** When a tool like Marimo / Langflow / PraisonAI ships an unauthenticated network endpoint, assume exploitation within hours of disclosure — don't pin to vulnerable versions waiting for a maintenance window.

## Sources
- [Sysdig — Marimo OSS Python Notebook RCE: From Disclosure to Exploitation in Under 10 Hours](https://www.sysdig.com/blog/marimo-oss-python-notebook-rce-from-disclosure-to-exploitation-in-under-10-hours) — canonical research, honeypot timeline, attacker behavior.
- [The Hacker News — Marimo RCE Flaw CVE-2026-39987 Exploited Within 10 Hours of Disclosure](https://thehackernews.com/2026/04/marimo-rce-flaw-cve-2026-39987.html)
- [SecurityAffairs — CVE-2026-39987: Marimo RCE exploited in hours after disclosure](https://securityaffairs.com/190623/hacking/cve-2026-39987-marimo-rce-exploited-in-hours-after-disclosure.html)
- [Rescana — Critical Marimo Python Notebook RCE Vulnerability (CVE-2026-39987) Exploited Within 10 Hours](https://www.rescana.com/post/critical-marimo-python-notebook-rce-vulnerability-cve-2026-39987-exploited-within-10-hours-of-disc/)
- [GitHub — keraattin/CVE-2026-39987 (technical writeup + detection scripts)](https://github.com/keraattin/CVE-2026-39987) — root cause: unauthenticated `/terminal/ws`, fixed in 0.23.0.
- [CyberPress — Marimo RCE Vulnerability Exploited Within 10 Hours of Public Disclosure](https://cyberpress.org/marimo-rce-vulnerability-exploited-within-10-hours-of-public-disclosure/)
