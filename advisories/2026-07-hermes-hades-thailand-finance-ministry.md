---
id: 2026-07-hermes-hades-thailand-finance-ministry
title: "Hermes AI agent in \"YOLO mode\" runs unattended post-exploitation against Thailand's Ministry of Finance (agentic threat actor, July 2026)"
date_disclosed: 2026-07-23
last_updated: 2026-07-23
severity: high
status: unconfirmed
ecosystems: [ai-agents, hermes]
tools_affected: [hermes-ai-agent]
tags: [agentic-threat-actor, autonomous-attack, government-target, credential-theft, web-shell, exposed-infrastructure]
---

## TL;DR
Between **2026-07-09 and 07-13**, researchers at Hunt.io and Bob Diachenko found an exposed Hong Kong staging server (585 files, ~470 MB) documenting an intrusion into systems belonging to **Thailand's Ministry of Finance**, run substantially by **Hermes** — an open-source, persistent AI agent — with human approval prompts disabled via its **"YOLO mode."** Recovered agent logs show the AI autonomously ran privilege-escalation scanning, kernel-vulnerability checks, and directory enumeration against ministry infrastructure with no operator directing each step. This is the second **agentic-threat-actor**-class incident this repo tracks after [JADEPUFFER](2026-07-jadepuffer-langflow-agentic-ransomware.md) — a different tool, a different target, and (unlike JADEPUFFER's honeypot-style disclosure) evidence recovered directly from the attacker's own staging infrastructure. The Ministry has not confirmed the breach.

## What happened
Hunt.io, working with researcher Bob Diachenko, discovered three open directories exposed on a Hong Kong server (`43.246.208[.]207`) — 145 files on 2026-07-09, 62 files on 2026-07-10, and 378 files on 2026-07-13, 585 total (~470 MB) — that functioned as the operator's own staging and evidence area for an intrusion against Thailand's Ministry of Finance (MOF). ThaiCERT and Thailand's National Cyber Security Agency were notified on **2026-07-15** and acknowledged receipt the same day; public disclosure followed a standard 7-day embargo on **2026-07-23** ([Hunt.io](https://hunt.io/blog/thailand-ministry-finance-targeted-with-hermes-ai-agent); [BleepingComputer](https://www.bleepingcomputer.com/news/security/hermes-ai-agent-used-to-automate-attack-on-thai-finance-ministry/)).

**Hermes** is an open-source AI agent released in February 2026 that runs as a persistent daemon with cross-session memory and tool/command execution. Its **"YOLO mode"** removes the prompts that would normally require a human operator to approve a dangerous command — the same "remove the human-in-the-loop" pattern this repo has flagged in other local-agent CVEs, but here deliberately enabled by the attacker rather than exploited as a bug.

Recovered Hermes activity logs (five call-log files) show the agent **autonomously**:
- running LinPEAS-based privilege-escalation and kernel-vulnerability assessments across MOF hosts, using a version customized to target three named 2026 CVE classes ("DirtyClone," "Copy Fail," "Dirty Frag"),
- enumerating SUID/SGID binaries, containers, and the filesystem,
- recursively searching web roots belonging to the **Office of Permanent Secretary for Finance**, cataloguing personnel records, performance evaluations, and Office documents dating back to 2012.

Hunt.io found no evidence that this cataloged data was exfiltrated at the time of discovery, consistent with a reconnaissance phase rather than a completed theft.

Alongside the Hermes logs, the staging server held a substantial toolkit: exploit code for **CVE-2021-3156** (sudo heap overflow), **CVE-2021-4034** (PwnKit), and **CVE-2017-7269** (IIS 6.0 WebDAV overflow, hardcoded with ministry-specific paths); a Python HiveServer2 exploitation script (`hive_rce_py2.py`) abusing default `NONE` authentication to register malicious Java UDFs against the ministry's Hadoop/HiveServer2 cluster; PHP and JSP web shells disguised as systemd journal caches and legitimate application files; and 62 Go-compiled binaries staging a custom cross-platform implant, **Hades**, in both Windows PE and Linux ELF form. Hades communicates over HTTPS using URI paths designed to mimic static web assets (`/assets/app.min.js`, `/assets/vendor.js`), encrypts traffic with AES-256-GCM using hardcoded per-build keys, and includes kill-dates and working-hour scheduling to blend in with normal activity — Windows Hades beaconed back to the staging server itself; the Linux variant used a separate C2 at `202.181.27[.]115:12443`.

Session cookies and credentials recovered from the server show the attacker reached the ministry's ICT-committee admin panel, tested SMTP credentials against mail infrastructure, and accessed a GlassFish admin console via headless-browser automation and an Alfresco document-management system.

**Attribution:** Hunt.io assesses **low-to-medium confidence** that the operator is Chinese-speaking or closely familiar with the language, based on the staging server's prior history as a ShadowPad controller, an active VShell C2 on related infrastructure, a Hermes panel password referencing "Leishen" (Thunder God), and a recovered API key for FOFA (a Chinese reconnaissance/OSINT platform). TLS-certificate (JA4X) pivoting tied the staging server to two further hosts in Malaysia and Hong Kong.

## Am I affected?
This is a targeted government intrusion, not a package or tool compromise — there is no lockfile check. If you operate or advise on infrastructure similar to what was targeted here, the concrete takeaways are:
- **Any AI agent with an "unattended"/"auto-approve"/"YOLO" mode should be treated as a privileged automation tool, not a chatbot** — audit what commands it can run, and never run one with broad network/credential access on a host that also holds sensitive infrastructure access.
- **Default or weak authentication on internal admin surfaces (Hive/HiveServer2, GlassFish admin consoles, Ambari) remains a primary escalation path** once initial access is gained — this incident's lateral movement leaned entirely on default-credential and unauthenticated internal services, not further zero-days.
- **Government/critical-infrastructure operators using Hadoop/Hive, GlassFish, or Alfresco should confirm HiveServer2 is not running with `NONE` authentication and that admin consoles are not reachable without strong auth.**

## If you are affected
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — relevant to the "unattended agent" angle even though this incident is attacker-operated rather than a hijack of a victim's own agent.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — the general lesson for defenders: any AI agent capable of running arbitrary commands without approval is an attacker force-multiplier once an attacker has any foothold, not just a productivity tool for legitimate operators.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Why this matters for vibe coders
This is a second, independently-sourced confirmation that autonomous AI agents are being used by real intruders to run entire post-exploitation phases with minimal human direction — not just in a researcher's honeypot ([JADEPUFFER](2026-07-jadepuffer-langflow-agentic-ransomware.md)) but recovered directly from an attacker's own staging server. It reinforces the agentic-threat-actor pattern this repo has been tracking since JADEPUFFER: the defender-side implication is that "an agent needs a human to approve dangerous steps" is a safety assumption that only holds when the operator chooses to keep it on — and attackers, unsurprisingly, don't. Note the `status: unconfirmed` — Thailand's Ministry of Finance has not confirmed the breach as of this writing, and this advisory relies on the researchers' own recovered evidence rather than a victim statement.

## Sources
- [Hunt.io — Thailand Ministry of Finance Targeted with Hermes AI Agent](https://hunt.io/blog/thailand-ministry-finance-targeted-with-hermes-ai-agent) — primary technical disclosure: exposed-server contents, Hermes/YOLO-mode detail, Hades implant analysis, attribution assessment, disclosure timeline.
- [BleepingComputer — Hermes AI agent used to automate attack on Thai finance ministry](https://www.bleepingcomputer.com/news/security/hermes-ai-agent-used-to-automate-attack-on-thai-finance-ministry/) — independent corroboration.
