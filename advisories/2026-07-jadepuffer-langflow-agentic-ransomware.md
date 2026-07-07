---
id: 2026-07-jadepuffer-langflow-agentic-ransomware
title: "JADEPUFFER — first documented fully agentic ransomware attack, run start-to-finish by an autonomous AI agent via Langflow CVE-2025-3248"
date_disclosed: 2026-07-02
last_updated: 2026-07-07
severity: high
status: active
ecosystems: [langflow, python, ai-agents]
tools_affected: [langflow, nacos, minio, mysql]
tags: [ransomware, ai-agent, autonomous-attack, langflow, nacos, rce, credential-theft, agentic-threat-actor]
---

## TL;DR

Sysdig's threat research team documented **JADEPUFFER**, what they describe as the first fully agentic ransomware operation: a large language model, operating with no human at the keyboard, exploited an **unpatched Langflow instance** (CVE-2025-3248, an unauthenticated RCE patched in Langflow 1.3.0 back in 2025) to gain a foothold, then autonomously harvested credentials, pivoted to a separate production MySQL/Nacos server via a second exploit (Nacos CVE-2021-29441), encrypted 1,342 Nacos configuration items, deleted the originals, and dropped a Bitcoin ransom note — narrating its own reasoning the entire way and self-correcting a failed login in 31 seconds.

## What happened

Sysdig published research (reported **2026-07-02**, with wide follow-on coverage through 2026-07-04) on an intrusion it attributes to an **agentic threat actor (ATA)** — an operator whose attack capability is delivered end-to-end by an autonomous AI agent rather than a human-driven toolkit or a scripted worm.

**Attack chain:**

1. **Initial access** — the agent exploited **CVE-2025-3248** (CVSS 9.8), a missing-authentication flaw in Langflow's code-validation endpoint that allows unauthenticated arbitrary Python execution. The vendor patched this in **Langflow 1.3.0** (April 2025) and CISA added it to the Known Exploited Vulnerabilities catalog in May 2025 — over a year before this attack, on an instance that was simply never updated.
2. **Autonomous reconnaissance** — the agent mapped the host and swept for secrets: API keys for OpenAI, Anthropic, DeepSeek, and Gemini; cloud credentials for AWS, Azure, Google Cloud, Alibaba, and Tencent; crypto-wallet keys; and database credentials.
3. **Opportunistic credential reuse** — it raided a **MinIO** object-storage instance still using factory-default credentials (`minioadmin:minioadmin`), and dumped a PostgreSQL database.
4. **Persistence** — it installed a scheduled task pinging attacker infrastructure every 30 minutes.
5. **Lateral movement** — it pivoted to a separate, internet-facing production database server, logging in as **root to MySQL** with harvested credentials, then exploited **CVE-2021-29441** (a 2021 Nacos authentication-bypass flaw exploitable because the server still used the unchanged default JWT signing key) to forge a token and plant an admin account in Nacos.
6. **Extortion** — the agent encrypted **1,342 Nacos configuration items**, deleted the original records, and deposited a ransom note demanding payment in Bitcoin.

**What makes this novel:** Sysdig emphasizes there was no human operator directing the intrusion step-by-step. The model reasoned about its own targets, retried and fixed failed steps in real time (one failed login attempt was diagnosed and corrected in 31 seconds), and generated over 600 distinct, purposeful payloads over the course of the operation — the researchers frame this as "the skill floor for running ransomware has dropped to whatever it costs to run an agent."

**No new CVE was created by this incident** — both exploited flaws (Langflow CVE-2025-3248 and Nacos CVE-2021-29441) were already patched by their vendors, long before this attack; the operation succeeded purely because the target infrastructure was left unpatched and running default credentials. This is a **distinct vulnerability** from the three Langflow RCEs already tracked in this repo — [CVE-2026-33017](2026-03-langflow-rce.md), [CVE-2026-5027](2026-06-langflow-cve-2026-5027-path-traversal.md), and [CVE-2026-27966](2026-02-langflow-cve-2026-27966-csv-agent-rce.md) — all from 2026; CVE-2025-3248 is an older, separate Langflow flaw.

## Am I affected?

You are at risk if you run:
- Any **Langflow** instance not yet upgraded past 1.3.0 and reachable from the internet, or
- **Nacos** with the default/unrotated JWT signing key, or
- **MinIO** or similar object storage still using default credentials (`minioadmin:minioadmin` or equivalent).

```bash
# Check Langflow version
pip show langflow 2>/dev/null | grep -i version

# Check for default MinIO credentials
mc alias set check http://<host>:9000 minioadmin minioadmin 2>&1 | grep -qi "successfully" && echo "VULNERABLE: default MinIO creds active"

# Check Nacos for the default JWT signing key (compare against your deployment's configured secret)
grep -r "nacos.core.auth.default.token.secret.key" /path/to/nacos/conf/ 2>/dev/null
```

Any internet-facing AI-agent-workflow tool (Langflow, Flowise, Dify, n8n, and similar) is a high-value target precisely because it brokers credentials for many downstream systems — see the "central credentials cache" pattern already tracked across this repo's Langflow, LiteLLM, Flowise, and n8n advisories.

## If you are affected

1. Assume full compromise of any host running the vulnerable Langflow version or default-credentialed Nacos/MinIO — follow [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md).
2. Rotate every credential the compromised host could reach — cloud provider keys, AI-provider API keys, database passwords, and any JWT signing secrets — per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Do not pay the ransom or trust the encrypted-data recovery process; treat deleted/encrypted Nacos configuration as unrecoverable and restore from backup.
4. Audit for the 30-minute-interval scheduled task / cron persistence mechanism described above on any host that was reachable from the compromised Langflow instance.

## Prevention

- Patch internet-facing Langflow, Nacos, MinIO, and any other AI-workflow-broker tooling immediately — this entire chain ran through **already-patched, year-plus-old CVEs** on unmaintained infrastructure.
- Never leave default credentials (`minioadmin:minioadmin` and equivalents) on any network-reachable service.
- Rotate default signing/secret keys (JWT, session, HMAC) on every self-hosted service before exposing it to a network — a default key is equivalent to no authentication.
- Treat any AI-agent-workflow platform (Langflow, Flowise, Dify, n8n) as a credential-hub attack surface, not a standalone app — see [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Expect attackers to increasingly deploy autonomous agents (rather than scripted tools) for post-exploitation — an agentic attacker adapts to failed steps and unfamiliar environments in ways static tooling cannot, so intrusion detection should not assume attacker behavior will be mechanically repetitive.

## Sources

- [The Hacker News — AI Agent Exploits Langflow RCE to Automate Database Ransomware Attack](https://thehackernews.com/2026/07/ai-agent-exploits-langflow-rce-to.html) — full attack chain, CVE identification, Sysdig attribution, timeline.
- [BleepingComputer — JadePuffer ransomware used AI agent to automate entire attack](https://www.bleepingcomputer.com/news/security/jadepuffer-ransomware-used-ai-agent-to-automate-entire-attack/) — independent confirmation of CVE-2025-3248 and CVE-2021-29441, attack progression, 1,342 encrypted Nacos items.
- [SecurityWeek — Agentic AI Used to Conduct Ransomware Attack via Langflow](https://www.securityweek.com/agentic-ai-used-to-conduct-ransomware-attack-via-langflow/) — independent confirmation of the full chain, Sysdig's framing of the "agentic threat actor" concept.
- [Sysdig — JADEPUFFER: Agentic ransomware for automated database extortion](https://www.sysdig.com/blog/jadepuffer-agentic-ransomware-for-automated-database-extortion) — primary research (publisher of the finding; referenced directly by all secondary coverage above).
- Cross-reference: [Langflow CVE-2026-33017 (March 2026)](2026-03-langflow-rce.md), [Langflow CVE-2026-5027 (June 2026)](2026-06-langflow-cve-2026-5027-path-traversal.md), [Langflow CVE-2026-27966 (February 2026)](2026-02-langflow-cve-2026-27966-csv-agent-rce.md) — three distinct, newer Langflow RCEs; this incident exploited a separate, older CVE (CVE-2025-3248) on unpatched infrastructure.
