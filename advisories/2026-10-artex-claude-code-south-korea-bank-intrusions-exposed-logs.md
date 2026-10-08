---
id: 2026-10-artex-claude-code-south-korea-bank-intrusions-exposed-logs
title: "A financially-motivated operator drove intrusions at five South Korean banks with Claude Code plus the Chinese open-source agentic-pentest tool ARTEX; CrowdStrike recovered the whole operation — Claude Code session histories, memory files, ARTEX configs and a résumé-writing prompt — from the attacker's own exposed directories (CrowdStrike, 2026-10-07)"
date_disclosed: 2026-10-07
last_updated: 2026-10-08
severity: high
status: active
ecosystems: [claude-code, ai-agents]
tools_affected: ["Claude Code (abused as attacker tooling)", "ARTEX (open-source LLM-driven agentic pentest tool)", "DeepSeek v4.1-flash, GLM-5.3, Grok 4.6 (model backends the operator used)", "financial-sector defenders"]
tags: [offensive-ai, agentic-attack, claude-code-abuse, threat-intel, exposed-directory, financial-sector, no-cve, crowdstrike]
---

## TL;DR
CrowdStrike, investigating data-theft at South Korean banks, found an **exposed attacker directory** that laid the whole operation bare: **Claude Code session histories and memory files**, a Chinese-language pentest prompt, **ARTEX** configuration files, and even a **résumé-writing prompt** that may identify the operator. The actor paired **Claude Code** with **ARTEX** — a recently released open-source LLM-driven agentic penetration-testing tool built in China — to run intrusions against at least five lenders, late September into early October 2026. This is not a vulnerability in Claude Code; it is a documented case of an AI coding agent used as offensive tooling, and a reminder that an attacker's own agent logs and config files are as exposable as any other server data.

## What happened
CrowdStrike analyst Ashley Campion's report (**2026-10-07**) describes two attacker-controlled servers found through an exposed open directory: a Chinese-language instruction file pointed to a second server in Hong Kong holding **Claude Code session histories, configuration files and AI memory files** documenting the targeting, alongside **ARTEX** config. The operator used **Claude Code** to draft materials, to ask where Korean breach data is sold and for help finding Korean Telegram data-sale groups, and ran **ARTEX** — described as a multi-agent autonomous pentest tool developed by a Chinese GitHub developer — against the banks, with **DeepSeek v4.1-flash** as the main model and **GLM-5.3** and **Grok 4.6** as supplements (DeepSeek likely reached through an API reseller). A **résumé-writing prompt** in the logs named "YY," a Chinese university and a Guangdong location with conflicting ages, and a Telegram handle that also appeared targeting a Chinese payment platform and an NFT gift marketplace; CrowdStrike considers the details likely the attacker's but cannot definitively confirm.

Per The Register's reporting on the same case, the attacks hit at least five lenders — Shinhan, KB Kookmin, Hana, Yegaram Savings and BNK Busan — breaching a loan-progress inquiry service in one case and a mobile work-support system in another; Shinhan reported ~25,000 customers affected, KB Kookmin 119 and Hana 89. The ARTEX developer said the attacks went against the tool's stated learning-and-research purpose and that the project will go closed-source. CrowdStrike assesses that adversaries will keep experimenting with AI tooling to raise their operational tempo. No CVE; this is a threat-intelligence incident, not a product flaw.

**Why it matters to vibe coders.** It is the clearest tracked case to date of **Claude Code as the attacker's workbench** rather than the victim's — session histories, memory files and MCP/agent configs all recoverable from a server the operator left open. The defensive read is twofold: the same agent logs and config files your team generates are high-value if a box is exposed, and financial-sector defenders should treat AI-accelerated, multi-intrusion tempo as the baseline. It sits beside the earlier Aurora/Cursor and "crook used three open-source agents" cases already in this corpus.

## Am I affected?
This is not a flaw to patch. For defenders: the useful artifacts are ARTEX's own fingerprint and the tempo of agent-driven intrusions. CrowdStrike notes ARTEX instances have been spotted by the string `ARTEX, an autonomous penetration testing console` in server HTTP headers (Genians), and the campaign used nine proxy IPs plus a dedicated ARTEX host (addresses omitted here — see CrowdStrike's IOC table). Financial-sector teams named by the Korean regulator received a suspicious-address list and were ordered to run emergency checks.

## If you are affected
If you run AI coding agents, keep their session logs, memory files and MCP/agent configs off internet-reachable paths and treat them as credential-bearing — see [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) and [credential-hygiene.md](../prevention/credential-hygiene.md). If you are a targeted-sector defender, hunt for the ARTEX header fingerprint and unexplained bursts of credential-stuffing / API-probing consistent with an autonomous agent.

## Prevention
Treat agent session and memory files as sensitive artifacts, not scratch data ([mcp-hygiene.md](../prevention/mcp-hygiene.md), [credential-hygiene.md](../prevention/credential-hygiene.md)); assume AI tooling compresses an intrusion campaign into hours, and prioritise exposure, privilege and segmentation over patch cadence ([ci-cd-hardening.md](../prevention/ci-cd-hardening.md)).

## Sources
- [CrowdStrike — Unknown Threat Actor Uses ARTEX to Target South Korean Finance](https://www.crowdstrike.com/en-us/blog/unknown-threat-actor-uses-artex-to-target-south-korean-finance/) (2026-10-07, Ashley Campion: exposed directory, Claude Code session/memory files, ARTEX configs, DeepSeek/GLM/Grok backends, the "YY" résumé prompt and Telegram handle, MITRE ATT&CK mapping, IOC categories)
- [The Register — CrowdStrike finds possible bank hacker's CV among exposed AI logs](https://www.theregister.com/cyber-crime/2026/10/08/crowdstrike-finds-possible-bank-hackers-cv-among-exposed-ai-logs/5301908) (2026-10-08, Connor Jones: five named lenders, affected-customer counts, the résumé detail, closed-sourcing of ARTEX, Oct 19 parliamentary audit)
- [The Hacker News — ARTEX AI Pentesting Tool Used in Data Theft Attacks on South Korean Financial Firms](https://thehackernews.com/2026/10/artex-ai-pentesting-tool-used-in-data.html) (2026-10-08: relays CrowdStrike, two-server setup, model backends)
