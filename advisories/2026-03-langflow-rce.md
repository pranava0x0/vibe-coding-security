---
id: 2026-03-langflow-rce
title: "Langflow unauthenticated RCE — CVE-2026-33017 (March 2026)"
date_disclosed: 2026-03-17
last_updated: 2026-05-20
severity: critical
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [langflow]
tags: [cve, rce, ai-agent-framework, unauthenticated, cisa-kev, rapid-exploitation, incomplete-fix]
---

## TL;DR
**CVE-2026-33017** — an **unauthenticated remote code execution** flaw in **Langflow**, the popular open-source visual builder for AI-agent / RAG pipelines. The public flow-build endpoint (`build_public_tmp`) executes user-controlled input inside a Python context with no authentication, so a **single crafted HTTP request runs arbitrary code** on any exposed instance. Rated **CVSS 9.8 (critical)** and added to **CISA's Known Exploited Vulnerabilities (KEV)** catalog; Sysdig honeypots saw exploitation **~20 hours after disclosure**, built straight from the advisory text with no public PoC. Beware the **incomplete fix**: JFrog confirmed **1.8.2 is still exploitable** — you must be on **1.9.0** (or `langflow-nightly` ≥ 1.9.0.dev18).

## What happened
Langflow disclosed CVE-2026-33017 on **2026-03-17**. The root cause is unsafe handling of user-controlled input in the public flow-build endpoint (`build_public_tmp`): the input is evaluated within a Python execution context without sufficient sanitization, giving an unauthenticated attacker arbitrary code execution with a single HTTP request and no credentials required.

Exploitation was nearly immediate. Per Sysdig's Threat Research Team, attackers began scanning for vulnerable instances roughly **20 hours** after the advisory published, ran Python-based exploitation within ~21 hours, and started harvesting `.env` and `.db` files within ~24 hours. Observed post-exploitation included **stealing AWS keys** and deploying a **NATS messaging worker as scalable C2** — a "SaaS-style" cybercrime pattern. CISA added the flaw to its KEV catalog (federal remediation deadline April 8, 2026).

**Incomplete-fix warning:** Langflow 1.8.2 was widely reported as the patched version, but **JFrog Security Research confirmed 1.8.2 remains exploitable**. Only **1.9.0** properly closes the hole. JFrog's testing showed `langflow-nightly` 1.9.0.dev18 effective as an interim mitigation; if you cannot upgrade cleanly, uninstalling Langflow until on 1.9.0+ is the safe move.

This is the same rapid-exploitation pattern as the [PraisonAI auth bypass](2026-05-praisonai-auth-bypass.md): AI-agent frameworks now get weaponized within hours-to-a-day of disclosure.

## Am I affected?

```bash
# Check installed Langflow version (must be >= 1.9.0)
pip show langflow 2>/dev/null | grep -E '^(Name|Version):'

# Is a Langflow instance exposed on the network?
ss -tlnp 2>/dev/null | grep -E ':7860|:7861'   # default Langflow ports
ps eww | grep -i '[l]angflow'
```

If you ran a Langflow version **before 1.9.0** reachable from anything other than localhost, assume compromise: check for unexpected outbound connections (NATS / unknown brokers), exfiltrated `.env`/`.db` files, and unfamiliar processes/workers.

### IOCs

| Type | Value |
|---|---|
| CVE | `CVE-2026-33017` |
| CVSS | 9.8 (critical); CISA KEV-listed |
| Vulnerable endpoint | public flow-build (`build_public_tmp`) |
| Affected versions | all before 1.9.0 — **1.8.2 is NOT a complete fix** |
| Fixed version | `langflow 1.9.0` (interim: `langflow-nightly` ≥ 1.9.0.dev18) |
| Post-exploit TTP | AWS key theft; NATS worker as C2; `.env`/`.db` harvesting |
| Disclosure-to-exploit | ~20 hours |

## If you are affected
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — AWS keys first.
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — generic host-compromise triage (rotation logic applies to any RCE).

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Never expose AI-agent / pipeline-builder dev servers to the public internet. Default-bind to `127.0.0.1`, front with authenticated reverse proxy or a tunnel. Treat **disclosure-to-exploit as < 24 hours** for AI-agent frameworks and prioritize their security updates. Verify that a "patched" release actually fixes the issue — read the researcher follow-up (cf. the 1.8.2 incomplete fix here).

## Sources
- [Sysdig — CVE-2026-33017: How attackers compromised Langflow AI pipelines in 20 hours](https://www.sysdig.com/blog/cve-2026-33017-how-attackers-compromised-langflow-ai-pipelines-in-20-hours)
- [JFrog Security Research — Langflow CVE-2026-33017: Latest 'fixed' version is still exploitable](https://research.jfrog.com/post/langflow-latest-version-was-not-fixed/)
- [BleepingComputer — CISA: New Langflow flaw actively exploited to hijack AI workflows](https://www.bleepingcomputer.com/news/security/cisa-new-langflow-flaw-actively-exploited-to-hijack-ai-workflows/)
- [Help Net Security — CISA sounds alarm on Langflow RCE, Trivy supply chain compromise after rapid exploitation](https://www.helpnetsecurity.com/2026/03/27/cve-2026-33017-cve-2026-33634-exploited/)
- [The Hacker News — Critical Langflow Flaw CVE-2026-33017 Triggers Attacks within 20 Hours of Disclosure](https://thehackernews.com/2026/03/critical-langflow-flaw-cve-2026-33017.html)
- [CSO Online — Attackers exploit critical Langflow RCE within hours as CISA sounds alarm](https://www.csoonline.com/article/4151203/attackers-exploit-critical-langflow-rce-within-hours-as-cisa-sounds-alarm.html)
- [GBHackers — Langflow CVE-2026-33017 Exploited to Steal AWS Keys, Deploy NATS Worker](https://gbhackers.com/langflow-cve-2026-33017-exploited/)
- [NVD — CVE-2026-33017](https://nvd.nist.gov/vuln/detail/CVE-2026-33017)
