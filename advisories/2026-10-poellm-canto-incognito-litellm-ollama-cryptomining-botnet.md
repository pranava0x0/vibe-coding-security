---
id: 2026-10-poellm-canto-incognito-litellm-ollama-cryptomining-botnet
title: "PoeLLM (Canto Incognito): a cryptomining botnet that scans for and exploits internet-exposed LLM infrastructure — mostly vulnerable LiteLLM and Ollama, plus Gotenberg and Gitea — 3,400+ servers since April 2026, with its command-and-control address hidden in an AI-written poem on GitHub (Lumen Black Lotus Labs)"
date_disclosed: 2026-10-07
last_updated: 2026-10-08
severity: high
status: active
ecosystems: [llm-infrastructure, self-hosted]
tools_affected: ["LiteLLM (exposed instances)", "Ollama (exposed instances)", "Gotenberg", "Gitea", "Ivanti Sentry (investigation entry point, CVE-2026-10520)", "any internet-facing self-hosted AI/LLM service"]
tags: [cryptomining, botnet, llm-infrastructure, litellm, ollama, exposed-services, adversarial-poetry, etherhiding-style-c2, active-exploitation]
---

## TL;DR
**PoeLLM** is a financially-motivated cryptomining botnet, tracked by Lumen's Black Lotus Labs as **Canto Incognito**, that scans the internet for exposed AI/LLM infrastructure — most victims ran vulnerable, internet-facing **LiteLLM** and **Ollama**, with hundreds also running **Gotenberg** and **Gitea** — compromises it, and uses the victims' GPUs to mine cryptocurrency while turning them into scanners and exploit servers. It has hit **more than 3,400 servers since April 2026**, peaking above 800 active per day. Its distinguishing trick is hiding its command-and-control address inside an **AI-written poem on GitHub**: the malware parses keywords from the poem to derive the current C2, and the operator rotates C2 by editing the poem (done 11 times through September). The lesson for vibe coders is blunt: an exposed LLM gateway or local model server is a mining target the same day it goes public.

## What happened
Black Lotus Labs' report (shared with The Register, **2026-10-07**) attributes PoeLLM to an Italian-speaking operator (Italian-language comments and netflow) and names the campaign **Canto Incognito**. Active since at least **April 2026** (first malicious GitHub commit **2026-04-13**), it has compromised **3,400+ servers**, mostly in the US and Western Europe, and continues to spread. The threat hunters found it while investigating an **Ivanti Sentry** vulnerability (**CVE-2026-10520**): in early June a compromised Sentry host began scanning for other vulnerable devices after contacting a dedicated C2. Most victims, though, were running exposed **LiteLLM** and **Ollama**; The Hacker News and the Lumen writeup name **LiteLLM's `/mcp-rest/test/connection` endpoint (CVE-2026-42271)** as the likely LiteLLM exploitation path — a command-execution bug already tracked in this corpus and added to CISA KEV earlier for separate reasons. Compromised hosts scan the internet and POST to exposed ports instructing targets to pull the malware, which deploys **XMRig** and **Iron** miners and connects victims to the Kryptex mining service.

The novelty Lumen highlights is the C2 channel. The operator (GitHub user committing to a fork of the nodejs.org site source) stores a poem titled "On the Nature of Connection" in a file; the malware extracts specific words and converts them to an address through a hard-coded dictionary, so editing the poem silently repoints every infected host. Lumen calls it the first real-world case of "adversarial poetry" they have seen. There is no CVE for PoeLLM itself; it exploits known flaws in exposed services. (Live C2 and wallet addresses are in Lumen's report and omitted here.)

**Why it matters to vibe coders.** The victim profile is exactly the self-hosted AI stack vibe coders stand up — LiteLLM as a gateway, Ollama for local models — exposed to the internet without authentication or network isolation. A gateway holds every provider key; a mined GPU box is only the visible symptom.

## Am I affected?
```bash
# Is an LLM gateway / model server internet-reachable?
ss -ltnp 2>/dev/null | grep -E ':4000|:11434|:3000'   # LiteLLM 4000, Ollama 11434, Gotenberg 3000
# LiteLLM: confirm you are past the MCP test-endpoint fix (CVE-2026-42271, fixed 1.83.7)
pip show litellm 2>/dev/null | grep -i version
# Ivanti Sentry: patch CVE-2026-10520.
```
Unexpected high GPU/CPU use, outbound mining-pool traffic, or your host originating internet-wide scans are compromise signals. Lumen notes a shift toward SSH and login-portal brute-forcing as well.

## If you are affected
Isolate the host and treat it as fully compromised: see [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md) and [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) (an exposed LiteLLM gateway means every provider key it held is burned). Patch LiteLLM to 1.83.7+ and Ivanti Sentry, and take the LLM control plane off the public internet.

## Prevention
Never expose a LiteLLM gateway, Ollama, or any model/inference control plane to the internet without authentication and network isolation ([supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md), [ci-cd-hardening.md](../prevention/ci-cd-hardening.md)); audit external exposure after standing up any new self-hosted AI tool, and keep it patched ([credential-hygiene.md](../prevention/credential-hygiene.md)).

## Sources
- [The Register — Poetry is the new AI security threat as PoeLLM malware infects 3K+ servers](https://www.theregister.com/security/2026/10/07/poetry-is-the-new-ai-security-threat-as-poellm-malware-infects-3k-servers/5301672) (2026-10-07, Jessica Lyons: Lumen quotes, LiteLLM/Ollama/Gotenberg/Gitea victims, Ivanti Sentry CVE-2026-10520 entry point, the poem-as-C2 mechanism, 3,400+ servers, Italian-speaking attribution)
- [Lumen Black Lotus Labs — Canto Incognito: Tracking the PoeLLM Malware](https://www.lumen.com/blog/en-us/canto-incognito-tracking-the-poellm-malware) (2026-10-07: target list, LiteLLM `/mcp-rest/test/connection` path, XMRig/Iron/Kryptex, 11 poem rotations through September, victim counts, defender recommendations)
- [The Hacker News — PoeLLM Malware Infects 3,400+ Servers to Expand Crypto Mining Botnet](https://thehackernews.com/2026/10/poellm-malware-infects-3400-servers-to.html) (2026-10-07: relays Lumen, names LiteLLM CVE-2026-42271 as the likely LiteLLM path)
