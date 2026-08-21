---
id: 2026-08-knaithe-hermes-autonomous-ai-scanning
title: "knaithe/KnYuan — an autonomous DeepSeek+Hermes agent mass-scanned 460+ targets for Langflow, n8n and Marimo RCEs; the AI-tool exploits failed only where auth was on (July–August 2026)"
date_disclosed: 2026-07-30
last_updated: 2026-08-21
severity: high
status: active
ecosystems: [self-hosted, ai-infrastructure]
tools_affected: [Langflow, n8n, Marimo, Citrix NetScaler, Hermes Agent, DeepSeek, OpenClaw]
tags: [agentic-threat-actor, autonomous-agent, mass-scanning, rce, credential-theft, ai-infrastructure, exposure]
---

## TL;DR

Palo Alto Networks **Unit 42** recovered a live session showing a Chinese-speaking operator (**knaithe** / **KnYuan**) running an **autonomous** attack pipeline — **DeepSeek** as the reasoning engine inside the open-source **Hermes Agent** framework — against **460+ targets**, hunting exactly the self-hosted AI infrastructure this repo already tracks: **Langflow (CVE-2026-33017)**, **n8n (CVE-2026-21858 / CVE-2025-68613)**, and **Marimo (CVE-2026-39987)**, plus Citrix NetScaler (CVE-2026-3055). The agent enumerated **84 Langflow instances** and sampled from **25,209 Chinese n8n systems** via FOFA, then exploited on its own. The finding worth your attention: **the Langflow and n8n attempts failed, and they failed for exactly the reasons this repo tells you to configure** — `auto_login` was off, no public flow ID was exposed, and the n8n form endpoints required authentication. Marimo and NetScaler, which had no such gate, were compromised: **command execution on 11 Marimo notebooks** and data exfiltration from three NetScaler organizations. Tenable subsequently clustered this with six other incidents as a named **"Agentic AI Threat Cluster."**

## What happened

On **2026-07-30**, [Unit 42 published](https://unit42.paloaltonetworks.com/autonomous-ai-cyber-attack-campaign/) an analysis of a threat actor it tracks under the aliases **knaithe** and **KnYuan**, assessed as an individual operator **based in Zhuhai, China**, whose activity Unit 42 characterizes as opportunistic rather than state-directed.

**The stack.** Unit 42 is explicit about the division of labor: *"Hermes Agent provided orchestration (terminal access, Telegram-based command and control, and the skills system) while DeepSeek served as the reasoning engine."* The actor also used Qwen, GLM, Kimi, and MiniMax, and did limited testing of **Claude Code and Codex** — Western platforms — alongside the Chinese models. This repo already tracks the **Hermes** framework from the [Thailand Ministry of Finance intrusion](2026-07-hermes-hades-thailand-finance-ministry.md) and the [Taiwan government/nuclear-safety campaign](2026-08-taiwan-dream-autonomous-ai-agent-attack.md); this is its third appearance and the first where the recovered artifact is the agent's own session transcript.

**The recovered session (2026-05-07).** The agent ran a coordinated vulnerability assessment that Unit 42 says executed *"hundreds of hours of equivalent manual work in minutes"*:

- **Langflow phase** — enumerated **84 Langflow instances via FOFA**, then ran a proof-of-concept scanner with **10 parallel threads**.
- **n8n phase** — DeepSeek sampled roughly **100 IP addresses** out of **25,209 Chinese systems** FOFA identified, then probed about **40 unique IPs**, checking each one's version via `curl`. Unit 42 notes the actor *"allowed DeepSeek to narrow the targeting scope, likely to conserve AI compute"* — the model was making the targeting decisions, not just executing a list.

Across the wider campaign the actor hit **over 460 targets** using a mix of autonomous and manual techniques, exploiting seven vulnerabilities in total.

### What failed, and why it matters more than what succeeded

This is the part of the report that changes what a reader should actually do.

| Target | CVE | Outcome | Why |
|---|---|---|---|
| **Langflow** | CVE-2026-33017 | **Failed** | The exploit *"requires either `auto_login` enabled or a public flow ID and the target had neither."* The agent's own reasoning, quoted by Unit 42: *"All three Langflow need public flow ID but no auto_login — stuck."* |
| **n8n** | CVE-2026-21858 / CVE-2025-68613 | **Failed** | Three instances *were* running vulnerable versions, but *"all required authentication"* on the form endpoints. The agent: *"these forms have auth enabled. Let me check other targets."* |
| **Marimo** | CVE-2026-39987 | **Succeeded** | Command execution achieved on **11 Marimo notebook instances**. |
| **Citrix NetScaler** | CVE-2026-3055 | **Succeeded** | Data exfiltrated from **three organizations**; the actor searched for NetScaler authentication cookies (`NSC_AAAC=`), indicating session-hijacking intent. |

An autonomous attacker with a working exploit and a list of confirmed-vulnerable hosts was stopped by ordinary authentication being switched on. Both of the failures land on tools this repo has repeatedly flagged as "central credentials cache" targets — see [Langflow CVE-2026-33017](2026-03-langflow-rce.md) and the [n8n RCE cluster](2025-11-n8n-ni8mare-rce.md) — and in both cases the specific control that held is the one those advisories tell you to set. Meanwhile [Marimo CVE-2026-39987](2026-04-marimo-notebook-rce.md), an unauthenticated pre-auth RCE with no equivalent gate, fell.

**The intelligence pipeline.** The actor maintains a GitHub-hosted automated vulnerability-intelligence tool called **1DayNews**, which aggregates RCE disclosures from **17 sources** (primarily network-perimeter vendors), uses **DeepSeek to filter for exploitability**, and pushes actionable alerts over **Telegram**. This is the reconnaissance half of the same automation: disclosure-to-exploit compression is not just faster exploitation, it is faster *triage of which disclosures are worth exploiting at all*.

### Tenable clusters this with six other incidents (2026-08-14)

On **2026-08-14**, [Tenable published](https://www.tenable.com/blog/the-agentic-ai-threat-cluster-seven-incidents-three-actors-and-what-they-mean) an "Agentic AI Threat Cluster" analysis grouping **seven incidents and three named actors** spanning roughly November 2025 → August 2026. The three actors: the **Taiwan operator** (suspected China-linked, unattributed to a specific entity), **JADEPUFFER**, and **knaithe/KnYuan**. Tenable's contribution is the clustering, not new primary research — it cites Unit 42 (2026-07-30), Dream Security (2026-08-12), and Sysdig TRT's JADEPUFFER report (2026-07-01), all three of which this repo already tracks separately ([JADEPUFFER](2026-07-jadepuffer-langflow-agentic-ransomware.md), [Taiwan/Dream](2026-08-taiwan-dream-autonomous-ai-agent-attack.md)). It characterizes agentic capability as autonomous or semi-autonomous systems operating *"beyond step-by-step human direction,"* with self-directed reconnaissance, technique selection, and lateral-expansion decisions.

The CVE list Tenable attributes across the cluster is a near-exact overlay of this repo's own coverage: CVE-2025-3248 and CVE-2026-33017 (Langflow), CVE-2026-39987 (Marimo), CVE-2026-21858 and CVE-2025-68613 (n8n), plus CVE-2026-3055 (Citrix NetScaler), CVE-2026-34486 (Apache Tomcat), CVE-2026-0300 (PAN-OS), and CVE-2026-33824 (Windows IKE VPN). **Self-hosted AI orchestration tooling is now a standing target category for autonomous attackers**, not an incidental one.

## Am I affected?

You are in the target set if you run any of these reachable from a network you don't fully control. Check exposure and configuration, in this order:

```bash
# 1. Is anything listening on the usual AI-tool ports on a non-loopback interface?
ss -tlnp 2>/dev/null | grep -E ':(7860|5678|2718|8080|3000)\b' | grep -v '127\.0\.0\.1'

# 2. Langflow — the two conditions the agent needed and did not get.
#    Confirm auto_login is OFF and no flow is publicly reachable without a token.
env | grep -i 'LANGFLOW_AUTO_LOGIN\|LANGFLOW_SUPERUSER'
LANGFLOW_HOST="your-langflow-host:7860"   # set this, then:
curl -s -o /dev/null -w '%{http_code}\n' "http://$LANGFLOW_HOST/api/v1/auto_login"   # want 401/403/404, not 200

# 3. n8n — form/webhook endpoints must require auth, and the version must be current.
docker exec "$N8N_CONTAINER" n8n --version 2>/dev/null || npm ls n8n 2>/dev/null

# 4. Marimo — no equivalent gate exists; the only safe posture is "not reachable".
#    Confirm your version is patched for CVE-2026-39987 and that it is not bound to 0.0.0.0.
```

Then check for the outcomes the agent actually achieved:

- **Marimo** — review notebook process history and any child processes spawned by the Marimo server; command execution was confirmed on 11 instances in this campaign.
- **NetScaler** — audit for `NSC_AAAC=` cookie theft and unexpected authenticated sessions.
- **Any exposed instance** — treat every credential the tool held as in scope, not just the tool's own login. That is the standing rule for this class in this repo, and it is exactly what an agentic attacker is optimizing for.

Note the campaign's observed targeting was Chinese infrastructure (FOFA enumeration of Chinese systems), so **geographic absence from that set is not a reason to relax** — the technique, the tooling, and the CVE list are all portable, and the same Hermes framework has already been used against Thai and Taiwanese targets.

## If you are affected

- [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)
- [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) — an exposed Langflow/n8n/Marimo instance is a credential hub; rotate every upstream provider key it held, not just the tool's own.
- [If your web app was compromised](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md)
- [Credential hygiene](../prevention/credential-hygiene.md)
- [CI/CD hardening](../prevention/ci-cd-hardening.md)

The single highest-value action this incident supports: **turn authentication on and keep convenience defaults off.** `auto_login`, anonymous form endpoints, and `0.0.0.0` binds are the difference between the two rows of the table above.

## Sources

- [Unit 42 — Chinese-Speaking Threat Actor Harnesses AI Models for Autonomous Cyberattacks](https://unit42.paloaltonetworks.com/autonomous-ai-cyber-attack-campaign/) (published 2026-07-30) — primary source, fetched directly: actor aliases and Zhuhai assessment, the Hermes+DeepSeek division of labor, the 2026-05-07 recovered session (84 Langflow instances, 25,209 FOFA-identified n8n systems, ~100 sampled IPs, ~40 probed), per-CVE success/failure outcomes and the agent's own quoted reasoning, the 11 compromised Marimo instances, the three NetScaler victims and `NSC_AAAC=` cookie hunting, and the 1DayNews pipeline (17 sources, DeepSeek filtering, Telegram distribution).
- [Tenable — The Agentic AI Threat Cluster: Seven Incidents, Three Actors, and What They Mean for Your Exposure](https://www.tenable.com/blog/the-agentic-ai-threat-cluster-seven-incidents-three-actors-and-what-they-mean) (published 2026-08-14) — independent corroboration and clustering, fetched directly: the seven-incident/three-actor framing, the cross-campaign CVE list, and the characterization of agentic capability as operating beyond step-by-step human direction. Explicitly a synthesis of already-disclosed reporting (Unit 42, Dream Security, Sysdig TRT) rather than new primary research.
