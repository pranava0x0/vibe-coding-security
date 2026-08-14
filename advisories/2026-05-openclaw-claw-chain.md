---
id: 2026-05-openclaw-claw-chain
title: "OpenClaw 'Claw Chain' — 4 chainable sandbox-escape flaws (May 2026), plus a March 2026 device-pairing privilege-escalation CVE"
date_disclosed: 2026-05-13
last_updated: 2026-08-14
severity: critical
status: patched
ecosystems: [ai-agents]
tools_affected: [openclaw]
tags: [cve, sandbox-escape, race-condition, allowlist-bypass, ai-agent, claw-chain, cyera, privilege-escalation]
---

## TL;DR
Cyera Research disclosed **four chainable vulnerabilities** in **OpenClaw** — the autonomous AI agent that rocketed to 135K+ GitHub stars in early 2026 — collectively dubbed **"Claw Chain."** The chain (CVE-2026-44112, -44113, -44115, -44118) lets an attacker bypass the OpenShell managed sandbox, read & write outside the mount root, execute disallowed commands through here-doc shell-expansion bypass, and impersonate the agent owner to control gateway, cron, and execution environment. SecurityScorecard previously reported **~245,000 publicly accessible OpenClaw instances**, with 63% of them running with **no authentication at all** and ~35% flagged as vulnerable. Patched in **OpenClaw 2026.4.22**. If you exposed an instance to the internet, assume full compromise. **Update (2026-08-08):** a separate, earlier-fixed device-pairing bug — **CVE-2026-33579** (patched in **2026.3.28**, about a month before Claw Chain) — is folded in below; check both fix versions independently.

## What happened
OpenClaw ships an "OpenShell" managed sandbox that's supposed to confine agent-issued shell commands to a tmpfs mount and an allowlist. Cyera found four design flaws that, chained, neutralize the sandbox entirely:

1. **CVE-2026-44112 (CVSS 9.6 / 6.3)** — TOCTOU race in the OpenShell sandbox backend. The mount-root check and the write operation are non-atomic; an attacker who can race the agent can redirect writes outside the mount root.
2. **CVE-2026-44113 (CVSS 7.7 / 6.3)** — Symmetric TOCTOU on the read path: read files outside the mount root by winning the same race.
3. **CVE-2026-44115 (CVSS 8.8)** — Allowlist bypass via shell expansion tokens inside a here-doc. The disallowed-input list checked argv but not what the shell would expand inline, so `cat <<EOF\n$(...)\nEOF` evaded the filter and executed the inner command.
4. **CVE-2026-44118** — Improper access control on the OpenClaw control plane: non-owner clients could impersonate the owner and reconfigure the agent's gateway, cron jobs, and execution environment, gaining persistence.

Why this matters: each step looks like normal agent behaviour to traditional security controls — the agent is writing files, reading files, running shell commands, updating cron — but at each step the attacker is *the one* driving the agent. Detection is hard precisely because the actions originate from a trusted process.

## Exposure scale (pre-patch)

| Metric | Value |
|---|---|
| Public-facing OpenClaw instances | ~245,000 |
| Running with no authentication | ~63% (~154K hosts) |
| Flagged vulnerable | ~35.4% (~87K hosts) |
| Fixed in | `OpenClaw 2026.4.22` |

## Am I affected?

```bash
# Local install
openclaw --version 2>/dev/null
which openclaw && openclaw doctor 2>/dev/null

# Self-hosted server: check listening port + auth posture
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:7860/api/status
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:7860/api/agents

# If port 7860/8080/<custom> is reachable from the public internet without auth,
# treat the host as already-compromised.

# Audit cron / gateway / env for unexpected entries
crontab -l 2>/dev/null | grep -iE 'openclaw|claw'
ls -la ~/.openclaw/gateway.yaml ~/.openclaw/env 2>/dev/null
```

### IOCs / artifacts to look for
- Unexpected modifications to `~/.openclaw/gateway.yaml`, `~/.openclaw/cron.yaml`, or any env file the agent loads.
- New entries in OpenShell's task ledger from operators you don't recognize.
- here-doc shell command patterns in agent logs (`cat <<...$(...)...`).
- Files written outside the configured sandbox mount root.

## If you are affected
1. **Upgrade to OpenClaw 2026.4.22** or newer immediately.
2. Take any internet-exposed instance behind authentication (tunnel + SSO, or at minimum reverse proxy with strong basic auth + IP allowlist).
3. Treat any host that ran a vulnerable version with public exposure as fully compromised:
   - Rotate every credential the agent had reachable (API keys for tools, SSH keys, cloud creds).
   - Reimage the host or restore from a known-clean backup; the persistence (CVE-2026-44118) means cleanup is unreliable.
   - Audit any data the agent had access to for unauthorized reads/writes.
4. Audit cron / scheduled tasks / gateway config for backdoor entries.

## Update — 2026-08-08: CVE-2026-33579, device-pairing privilege escalation (fixed 2026.3.28, predates Claw Chain)
A distinct, unrelated bug — **CVE-2026-33579** (CVSS 3.1: 8.1 High / CVSS 4.0: 8.6 High) — sits in OpenClaw's device-pairing approval flow rather than the OpenShell sandbox. The `/pair approve` command path fails to forward the *approving caller's own* security scopes into the core authorization check, so a low-privilege account holding only pairing rights (not admin) can approve a *pending device request that asks for broader scopes*, including full `operator.admin`. The exploit sequence: register a new device, submit a pairing request that asks for `operator.admin` in its desired scopes, then approve it with a low-privilege caller — the missing scope-forwarding check lets the approval succeed anyway, handing the new device admin-level control. Root cause: improper authorization validation (CWE-863) in `extensions/device-pair/index.ts` and `src/infra/device-pairing.ts`. **Fixed in OpenClaw 2026.3.28** — note this predates the Claw Chain fix (2026.4.22) by about a month, so an instance patched only against Claw Chain (i.e., already on ≥ 2026.4.22) is *also* covered here, but one patched only against this bug (≥ 2026.3.28 but < 2026.4.22) is **not** covered against Claw Chain.

```bash
openclaw --version 2>/dev/null   # confirm >= 2026.3.28 for this CVE, >= 2026.4.22 for Claw Chain
```

## Update — 2026-08-14: two more, earlier OpenClaw CVEs found via a direct vendor/NVD check, unrelated to Claw Chain or CVE-2026-33579
A routine cross-check against NVD and ArmoSec's vulnerability writeups turned up **two further, distinct OpenClaw CVEs** predating both the Claw Chain cluster (fixed 2026.4.22) and CVE-2026-33579 (fixed 2026.3.28) — neither previously tracked in this repo:

- **CVE-2026-32922** (CVSS 3.1: 9.9 / CVSS 4.0: 9.4) — a privilege-escalation bug in the device-pairing subsystem's **`device.token.rotate`** function: a caller holding only the limited `operator.pairing` scope could invoke this function and receive back a fully-privileged `operator.admin` token, with no scope check on the returned token's privilege level. Reported 2026-02-19, fixed and a GitHub Security Advisory published 2026-03-13, CVE published 2026-03-29. **Fixed in OpenClaw 2026.3.11** — the earliest fix among all five OpenClaw CVEs this repo now tracks. Same general class as CVE-2026-33579 (device-pairing scope-forwarding failure) but a different function, different CVE, and fixed roughly six weeks earlier.
- **CVE-2026-24763** (CVSS 3.1: 8.8) — a command-injection flaw in OpenClaw's **Docker sandbox execution mechanism**, caused by unsafe handling of the `PATH` environment variable when constructing shell commands; an authenticated user able to control environment variables could manipulate command execution inside the container. Published 2026-02-02, **fixed in OpenClaw 2026.1.29**.

Both confirmed via NVD directly (CVE-2026-32922, CVE-2026-24763) and cross-referenced against ArmoSec's writeup — satisfying this repo's independent-source bar. Any OpenClaw instance running a version older than **2026.1.29** is now confirmed exposed to at least five independently-patched CVEs in this repo's tracking (this one, CVE-2026-24763's fix; plus CVE-2026-32922 at 2026.3.11; CVE-2026-33579 at 2026.3.28; and the Claw Chain cluster at 2026.4.22) — the practical guidance is unchanged: run the latest OpenClaw release, don't assume "patched for Claw Chain" covers earlier bugs.

```bash
openclaw --version 2>/dev/null
# Confirmed-vulnerable-below thresholds, oldest to newest fix:
#   < 2026.1.29  — CVE-2026-24763 (Docker sandbox PATH command injection)
#   < 2026.3.11  — CVE-2026-32922 (device.token.rotate privilege escalation)
#   < 2026.3.28  — CVE-2026-33579 (device-pairing /pair approve scope-forwarding)
#   < 2026.4.22  — Claw Chain (CVE-2026-44112/-44113/-44115/-44118)
```

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ Default-deny on the network: bind agent servers to `127.0.0.1`, expose via authenticated tunnels only.
→ Don't trust agent-supplied sandboxes as a security boundary. Use OS-level isolation (devcontainer, microVM, Firecracker) for any agent that can shell out.
→ Treat AI-agent frameworks like web frameworks: assume disclosure-to-exploit < 24 hours.

## Sources
- [The Hacker News — Four OpenClaw Flaws Enable Data Theft, Privilege Escalation, and Persistence](https://thehackernews.com/2026/05/four-openclaw-flaws-enable-data-theft.html)
- [Cyera Research — Claw Chain: Four Chainable Vulnerabilities in OpenClaw](https://www.cyera.com/blog/claw-chain-cyera-research-unveil-four-chainable-vulnerabilities-in-openclaw)
- [SecurityWeek — 'Claw Chain' OpenClaw Flaws Allow Sandbox Escape, Backdoor Delivery](https://www.securityweek.com/claw-chain-openclaw-flaws-allow-sandbox-escape-backdoor-delivery/)
- [Cybersecurity News — OpenClaw Chain Vulnerabilities Expose 245,000 Public AI Agent Servers to Attack](https://cybersecuritynews.com/openclaw-chain-vulnerabilities/)
- [Kaspersky — New OpenClaw AI agent found unsafe for use](https://www.kaspersky.com/blog/openclaw-vulnerabilities-exposed/55263/)
- [Dark Reading — Critical OpenClaw Vulnerability Exposes AI Agent Risks](https://www.darkreading.com/application-security/critical-openclaw-vulnerability-ai-agent-risks)
- [Reco — OpenClaw: The AI Agent Security Crisis Unfolding Right Now](https://www.reco.ai/blog/openclaw-the-ai-agent-security-crisis-unfolding-right-now)
- [Oasis Security — ClawJacked: OpenClaw Vulnerability Enables Full Agent Takeover](https://www.oasis.security/blog/openclaw-vulnerability)
- [Sangfor — OpenClaw Security Risks: From Vulnerabilities to Supply Chain Abuse](https://www.sangfor.com/blog/cybersecurity/openclaw-ai-agent-security-risks-2026)
- [SentinelOne — CVE-2026-33579: OpenClaw Privilege Escalation Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-33579/) — CVSS scoring, CWE classification, affected/fixed version.
- [DEV Community — OpenClaw CVE-2026-33579: Unauthorized Privilege Escalation via `/pair approve` Command Fixed](https://dev.to/olgabyte/openclaw-cve-2026-33579-unauthorized-privilege-escalation-via-pair-approve-command-fixed-l48) — exploit sequence and affected source files.
- [ArmoSec — CVE-2026-32922: Critical Privilege Escalation in OpenClaw](https://www.armosec.io/blog/cve-2026-32922-openclaw-privilege-escalation-cloud-security/) — fetched directly for the 2026-08-14 update: `device.token.rotate` scope-check bypass, disclosure timeline, fixed version.
- [NVD — CVE-2026-32922](https://nvd.nist.gov/vuln/detail/CVE-2026-32922), [NVD — CVE-2026-24763](https://nvd.nist.gov/vuln/detail/CVE-2026-24763) — fetched directly to confirm both CVEs independently for the 2026-08-14 update.
