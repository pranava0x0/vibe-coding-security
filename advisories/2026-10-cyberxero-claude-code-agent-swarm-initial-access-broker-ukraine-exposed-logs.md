---
id: 2026-10-cyberxero-claude-code-agent-swarm-initial-access-broker-ukraine-exposed-logs
title: "CyberXero: an initial access broker ran 51 Claude Code agent definitions and PentAGI against WordPress sites and Ukrainian utilities; 628,000 records (SOCRadar, 2026-10-06)"
date_disclosed: 2026-10-06
last_updated: 2026-10-13
severity: high
status: active
ecosystems: [ai-agents, claude-code, wordpress, php, redis, critical-infrastructure]
tools_affected: ["Claude Code (abused as the actor's orchestration layer; not a product flaw)", "PentAGI (open-source AI pentesting framework, wired to a Cobalt Strike team server)", "WordPress, Magento and PrestaShop sites reachable from the internet", "internet-exposed Redis", "any operator's own AI agent session logs, memory files and working directories left on a reachable host"]
tags: [offensive-use, agentic-threat-actor, initial-access-broker, claude-code, pentagi, cobalt-strike, wordpress, ukraine, critical-infrastructure, exposed-logs, refusal-evasion, socradar]
---

## TL;DR
SOCRadar published on 2026-10-06 a report on CyberXero, a Russian-speaking, financially motivated initial access broker that has run since July 2026 with an AI orchestration layer: a Claude Code setup with 51 specialised agent definitions covering reconnaissance, exploitation and post-exploitation, plus PentAGI, an open-source AI pentesting framework, connected to a Cobalt Strike team server through an AI provider API. The researchers found it through the actor's own exposed working directory, more than 90,000 files including AI session logs, scripts with plaintext tokens and victim data exports, and mapped eight infrastructure nodes from it. Two pipelines ran at once: an opportunistic global campaign against WordPress, e-commerce and exposed Redis hosts, and a targeted one against Ukrainian energy and utilities, where four confirmed exfiltration victims account for more than 628,000 records tied to Ukrainian individuals, about 564,000 of them subscriber records of a Kharkiv district heating provider. One automated run scanned 4,708 targets, confirmed 429 reachable admin panels and deployed 32 web shells in 61 seconds. The session logs show the models refusing several requests (a backdoor, disabling a firewall, lateral movement, a web shell) and the actor resetting sessions with an "authorized testing on my own infrastructure" framing preloaded. The operation was active at publication. The Hacker News' 2026-10-12 pickup pairs it with SOCRadar's 2026-09-24 report on Operation Master, a Brazilian intrusion-and-invoice-fraud pipeline whose operator used a coding agent with 36 or more offensive sub-agents. This is the third file in this corpus where the coding agent is the attacker's workbench, after [ARTEX](2026-10-artex-claude-code-south-korea-bank-intrusions-exposed-logs.md) and [Aurora](2026-08-aurora-ransomware-cursor-agent-abuse.md); it is not a vulnerability in Claude Code.

## What happened

### How it was found

SOCRadar's investigation began with an open directory that served the actor's live working directory. The report counts more than 90,000 files: AI agent session logs, operational scripts with tokens in plaintext, and exports of victim data. That one failure let the researchers map eight linked infrastructure nodes and reconstruct the operation's timeline. The same shape produced the [ARTEX](2026-10-artex-claude-code-south-korea-bank-intrusions-exposed-logs.md) case a week earlier (CrowdStrike, Claude Code session histories and memory files recovered from the attacker's exposed directories) and is the practical lesson of the file: an agent's session logs are a complete record of an operation, and they sit in a directory.

### The AI layer

- **Claude Code with 51 agent definitions** on the primary workstation, covering offensive, reconnaissance and post-exploitation roles. SOCRadar describes it as an orchestration layer that let one operator run at the scale of a team.
- **PentAGI**, an open-source autonomous pentesting agent, connected to a **Cobalt Strike** team server through an AI provider API for payload generation and execution.
- Conventional tooling beside them: masscan, nuclei, wpscan, and an internally developed WordPress exploitation package SOCRadar calls wp2shell, which chains WordPress vulnerabilities (The Hacker News names CVE-2026-63030 and CVE-2026-60137, and the Support Board plugin SQL injection CVE-2026-4815) into shell deployment.

The logs record refusals that held, including requests to install a backdoor, disable a firewall, move laterally and deploy a web shell, and the actor's response: reset the session and retry with the "authorized test on my own infrastructure" framing already in place. SOCRadar's recommendation follows from that: refusal is a model behaviour, and evasion by session reset is a thing to log and audit at the infrastructure layer, not something model behaviour can be relied on to stop.

### Targets and scale

| Pipeline | Targets | Scale (SOCRadar's figures) |
|---|---|---|
| Opportunistic, global | WordPress sites, e-commerce platforms (Magento and PrestaShop named in the advice), telecom, government, internet-exposed Redis | one automated run: 4,708 targets scanned, 429 accessible admin panels, 32 shells deployed, 61 seconds; more than 40 affected organisations worldwide; confirmed compromises in Poland, China (two Redis-exposed entities), Pakistan and, per The Hacker News, the Netherlands |
| Targeted, Ukraine | energy and utilities under curated reconnaissance | four confirmed exfiltration victims, more than 628,000 records tied to Ukrainian individuals; one Kharkiv district heating provider, about 564,000 subscriber records and 213,000 access-log entries; SOCRadar flags physical risk to civilians given the city's position on an active front |

Timeline: first infrastructure observed July 2026; AI account created late July, marking a second phase with a measurable rise in WordPress and SQL injection activity; active through publication on 2026-10-06.

### Operation Master, the second SOCRadar report

The Hacker News' 2026-10-12 article pairs CyberXero with SOCRadar's 2026-09-24 report on Operation Master, run by the forum persona "masterblack" from 2026-04-23 to mid-September 2026. SOCRadar's claims there: an AI coding agent with 36 or more offensive sub-agents, about 48 auto-approved tools and about 45 persistent memory files wrote much of the intrusion code (exploit drivers, an automated exploit loop, exfiltration scripts), while the operator wrote the fraud platform and the custom command-and-control; refusal transcripts with the same "authorized bug bounty" framing were part of the attribution; a second open-source agent appeared in later snapshots along with AI-API key harvesting. Initial access was a PAN-OS GlobalProtect authentication bypass (CVE-2026-0257), SQL injection and OAuth device-code phishing; the monetisation was 2.4 million emails, SMS and WhatsApp messages carrying 622,666 personalised invoice links for Brazilian brands, about R$38.9 million in exposed invoices. The infrastructure went offline in mid-September after operational security failures. SOCRadar does not say which agent product it was; this file records the claim as SOCRadar's.

## Am I affected?

Two different readers.

**If you run WordPress, Magento, PrestaShop or Redis on the internet**, CyberXero's opportunistic pipeline may have reached you, and the signs are ordinary:

```bash
# WordPress: unexpected administrators and plugins
wp user list --role=administrator --fields=user_login,user_registered 2>/dev/null
wp plugin list --fields=name,status,version,update 2>/dev/null
# web shells: PHP changed since the campaign's first infrastructure (July 2026) under each installation's wp-content
find /var/www -name wp-config.php 2>/dev/null | while read -r cfg; do
  find "$(dirname "$cfg")/wp-content" -name '*.php' -newermt 2026-07-01 2>/dev/null
done | head
# Redis: is it reachable, and whose keys are in authorized_keys on the host?
redis-cli -h 127.0.0.1 CONFIG GET protected-mode 2>/dev/null; ss -ltnp | grep ':6379'
grep -c . ~/.ssh/authorized_keys /root/.ssh/authorized_keys 2>/dev/null
```

SOCRadar's detection rules cover the wp2shell artefacts and an obfuscated web shell variant; they are in the full report, not reproduced here.

**If you run AI coding agents yourself**, the question is whether your own session logs, memory files, MCP configurations and working directories are on a reachable path:

```bash
# Where agent state lives on a host, and whether any of it is under a served directory
ls -la ~/.claude ~/.claude.json ~/.codex ~/.cursor 2>/dev/null | head
for d in /var/www /srv /opt/*/public /home/*/public_html; do find "$d" -maxdepth 4 \( -name '.claude*' -o -name 'CLAUDE.md' -o -name '*.jsonl' -o -name 'mcp.json' \) 2>/dev/null; done
```

## If you are affected

1. **Web application operators:** remove rogue administrators, delete unknown plugins and shells, rotate every secret in the application's configuration and the database credential, and patch the named WordPress components: [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md). Take Redis off the internet and audit SSH authorised keys on the host.
2. **If credentials from a compromised host reached a cloud account**, rotate at the issuer: [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. **Agent operators whose logs were reachable:** treat every token in them as public, rotate the AI provider keys first, then the MCP server credentials, then whatever the sessions touched: [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- **Treat AI agent session logs and memory as credential-grade data.** SOCRadar's first recommendation is retention limits, encryption and access controls for agent session logs comparable to those on credential stores. The actor's logs held plaintext tokens and the victims' data; yours hold yours: [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- **Log at the infrastructure layer what a model may refuse.** A session reset with a preloaded framing is visible in API usage and in the agent's own history; a refusal is not. Where you operate agents for others, audit by request pattern, not by outcome: [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Exposure beats patch cadence against an automated attacker.** 32 shells in 61 seconds is the pace a single operator reaches with 51 agent definitions; admin panels reachable from the internet, Redis without authentication and unpatched CMS plugins are what that pace consumes. Put admin surfaces behind authentication you control and scan your own estate the way the actor did.
- **This is an offensive-use record, not a product advisory.** There is nothing to upgrade in Claude Code; the vendor's usage policy and refusals held on several requests and did not stop the campaign. Account-level controls on the provider side, not model behaviour, are the vendor-side lever.

## Sources
- [SOCRadar — CyberXero: AI-augmented initial access broker targeting Ukraine's critical infrastructure](https://socradar.io/blog/cyberxero-ai-iab-ukraine-critical-infrastructure/) — fetched 2026-10-13 (summary only, indicators omitted): publication 2026-10-06, the actor description, the Claude Code setup with 51 agent definitions, PentAGI and Cobalt Strike, the open-directory discovery and the 90,000-file count, the eight-node infrastructure, the two pipelines, the 628,000 and 564,000 figures, the 4,708 / 429 / 32 / 61-second run, the July and late-July timeline, the refusal and session-reset observations, the recommendations.
- [The Hacker News — CyberXero Uses Claude Code in Campaign That Stole Over 628,000 Ukrainian Records](https://thehackernews.com/2026/10/cyberxero-uses-claude-code-in-campaign.html) — fetched 2026-10-13: 2026-10-12, Ravie Lakshmanan; the CyberXero summary with the Netherlands added to the confirmed-compromise countries, the wp2shell CVE ids, and the pairing with Operation Master.
- [SOCRadar — Operation Master: inside an AI-assisted intrusion and invoice-fraud pipeline](https://socradar.io/blog/operation-master-intrusion-monetization-pipeline/) — fetched 2026-10-13 (summary only): 2026-09-24, the masterblack persona, the 36-plus sub-agent coding-agent claim, the 48 auto-approved tools and 45 memory files, the refusal transcripts used for attribution, the targets, the 2.4 million messages and 622,666 links, the R$150.4 million and R$38.9 million figures, the 2026-04-23 to mid-September timeline.
- Related in this corpus: [ARTEX and Claude Code at five South Korean banks](2026-10-artex-claude-code-south-korea-bank-intrusions-exposed-logs.md) (CrowdStrike, 2026-10-07; the same exposed-directory discovery), [Aurora ransomware crew's use of Cursor](2026-08-aurora-ransomware-cursor-agent-abuse.md) (Gambit, the same session-restart evasion), [Wiz red agent and the Snowflake Copilot review](2026-08-wiz-red-agent-snowflake-copilot-review.md).
