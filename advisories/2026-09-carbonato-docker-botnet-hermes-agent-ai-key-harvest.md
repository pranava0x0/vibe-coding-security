---
id: 2026-09-carbonato-docker-botnet-hermes-agent-ai-key-harvest
title: "CARBONATO — a worm for Docker daemons exposed on port 2375 that installs Nous Research's open-source Hermes Agent on each victim with a replaced SOUL.md persona ('GH0ST'), takes tasks over Telegram, and is instructed to prioritise harvesting API keys for fourteen AI providers (OpenAI, Anthropic, Google, OpenRouter, Groq, Mistral, LiteLLM, Ollama…); rescans /24s every five minutes; ThreatDown, 2026-09-22"
date_disclosed: 2026-09-22
last_updated: 2026-09-30
severity: high
status: active
ecosystems: [docker, linux, ai-agents, hermes-agent]
tools_affected: ["Any Docker daemon reachable on TCP 2375 without TLS/auth (dev boxes, cloud VMs, CI hosts)", "Hermes Agent (Nous Research) as an attacker-installed runtime", "AI provider API keys stored on or reachable from the host: OpenAI, Anthropic, Google/Gemini, OpenRouter, Together, Groq, Mistral, Cohere, LocalAI, Ollama, vLLM, LiteLLM, One API", "neighbouring hosts on attached networks and Docker bridges"]
tags: [agentic-threat-actor, botnet, docker, exposed-daemon, worm, hermes-agent, soul-md, telegram-c2, api-key-theft, cryptominer, persistence, active]
---

## TL;DR

ThreatDown (Malwarebytes) published on **2026-09-22** its analysis of **CARBONATO**, a botnet whose implant is not custom malware but **Hermes Agent** — the MIT-licensed open-source agent framework from Nous Research — with its `SOUL.md` persona file overwritten by a **39-line prompt** that names the agent "GH0ST" and tells it to take tasks over **Telegram**, keep access, and **collect credentials, AI API keys first**. Initial access is the oldest trick in the container book: a **Docker daemon listening on port 2375 with no authentication**, which the worm uses to start a privileged container with the host filesystem mounted. Every five minutes the implant enumerates attached networks and Docker bridges and scans each /24 for more open daemons. Persistence is layered (cron, systemd timers, `rc.local`, OpenRC, immutable bits, a watchdog that re-pulls the implant from the operators' registry, a container masquerading as `systemd-resolved`, a process masquerading as `[kworker/u2:0]`), and a cryptominer rides along as `/usr/sbin/systemd-logind`. The registry ThreatDown found had been public since May; six of seven known registries were still up on 2026-09-03. This is the fourth corpus entry where the attacker's tooling is an off-the-shelf agent harness ([Hermes/Strix/Cairn skimmers](2026-09-gambit-hermes-strix-cairn-autonomous-agent-retail-skimmer-campaign.md), [knaithe](2026-08-knaithe-hermes-autonomous-ai-scanning.md), [JADEPUFFER](2026-07-jadepuffer-langflow-agentic-ransomware.md)) — and the first where the harness is the persistent implant and your AI keys are its stated priority.

## What happened

In August 2026 ThreatDown researchers found an unauthenticated Docker registry that had been publicly exposed since May and recovered 59 repositories, 234 image tags, 605 blobs and 4.3 GB of images — two product lines, a factory for trojanised cryptocurrency-wallet apps and the Docker botnet. The botnet's mechanics, per ThreatDown and The Hacker News (09-28):

- **Entry:** connect to a Docker API exposed on TCP 2375 without auth, ask the daemon to run a **privileged container with the host mounted**, and use that to write to the host. No exploit, no CVE — an open daemon *is* root on the host.
- **Implant:** Hermes Agent, installed on the host, with the operators' own LLM gateway behind it (advertising 12 models and serving 27 through its API). The `SOUL.md` persona instructs the agent to "execute tasks received through Telegram, maintain persistence, and collect credentials," and lists **fourteen AI providers** whose keys it should prioritise: OpenAI, Anthropic, Google, Gemini, OpenRouter, Together, Groq, Mistral, Cohere, LocalAI, Ollama, vLLM, LiteLLM, One API. A developer's `.env`, shell history, `~/.config` and any gateway config on the box are the target.
- **Control:** a reverse SSH tunnel to a relay in Costa Rica on a port derived from the victim's IP, an SSH server with the operators' key, and deployment reports posted to a Telegram chat.
- **Spread:** every five minutes the worm lists attached networks and Docker bridges and scans each /24 for port 2375, skipping hosts already infected.
- **Attribution:** voseo Spanish in the deployment reports, UTC−06:00 timestamps, a Telegram handle ending in Costa Rica's +506, relay infrastructure in a Costa Rican AS; no link to a known group.

Why this audience: exposed Docker daemons are overwhelmingly developer machines and cloud VMs where someone enabled the TCP socket "for Docker Desktop / a remote IDE / a CI runner" and never put TLS on it — the same hosts that hold `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, an OpenRouter key and a LiteLLM master key. The persona's provider list is a shopping list for exactly that key ring, and a stolen provider key funds the operators' own agent gateway. Note also that the implant is a **legitimate, actively maintained agent framework**: signature-based detection of "known malware" will not flag it, and an EDR that allows Hermes Agent because your developers use it allows this.

## Am I affected?

```bash
# 1. Is a Docker daemon listening on TCP? (2375 = plaintext, 2376 = TLS; either without client-cert auth is exposure)
ss -tlnp | grep -E ':2375|:2376'
grep -rn '"hosts"' /etc/docker/daemon.json 2>/dev/null; systemctl cat docker 2>/dev/null | grep -n 'tcp://'
# From outside: curl -s http://<host>:2375/version — a JSON answer means anyone can run privileged containers on it

# 2. Host indicators from the ThreatDown report
ls -la /root/.hermes/SOUL.md 2>/dev/null && grep -l 'GH0ST' /root/.hermes/SOUL.md
ls -la /usr/local/bin/.docker-network-monitor /usr/sbin/systemd-logind /opt/gh0st 2>/dev/null   # /usr/sbin/systemd-logind should not exist; real logind is /usr/lib/systemd/systemd-logind
docker ps -a --format '{{.Names}} {{.Image}}' | grep -iE 'gh0st|fsociety|netd-svc|system/resolved|scrub-empty'
ps -eo pid,comm,args | grep -E '\[kworker/u2:0\]' | grep -v '^ *[0-9]* kworker'   # a kworker with a path is a masquerade
env | grep -E 'GH0ST_C2|FSOCIETY_DISABLE_TUNNEL|GATEWAY_ALLOW_ALL_USERS|CARBONATO_API_KEY'
lsattr /etc/cron.d/* /etc/rc.local 2>/dev/null | grep '^....i'                                     # immutable persistence
crontab -l 2>/dev/null; ls /etc/cron.d /etc/systemd/system/*.timer 2>/dev/null

# 3. Egress: outbound SSH you did not configure, Telegram API traffic from a server
ss -tnp | grep -E ':22 ' | grep -v '127.0.0.1'; ss -tnp | grep -i telegram
```

Any hit in step 2 or 3 is a confirmed compromise. Hosts on the same subnet as a confirmed victim should be checked for step 1 first — the worm has already scanned them.

## If you are affected

- **Rotate every AI provider key** that was on or reachable from the host — OpenAI, Anthropic, Google, OpenRouter, Groq, Mistral, and the master key of any LiteLLM / One API gateway — and check the providers' usage dashboards for spend you did not generate. [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
- Reimage the host; persistence is layered and immutable-flagged, and the watchdog re-installs from a remote registry. [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).
- Revoke SSH keys and cloud credentials present on the box, and any Docker registry credentials. Check neighbouring hosts.

## Prevention

- **Never bind the Docker daemon to TCP without mutual TLS**; prefer the Unix socket plus SSH (`DOCKER_HOST=ssh://…`) for remote use. A cloud firewall rule that opens 2375 "temporarily" is the whole incident. [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- Keep provider keys out of long-lived files on servers: short-lived, scoped keys from a gateway, spend limits per key, alerts on new-IP usage. The persona's provider list is what "AI keys are the loot" looks like from the attacker's side. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Treat agent frameworks as dual-use binaries in detection engineering: alert on a Hermes/OpenClaw/Strix install you did not do, on a `SOUL.md` or persona file change, and on Telegram egress from a server. [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Sources

- [ThreatDown — CARBONATO: a botnet built around an AI agent](https://www.threatdown.com/blog/carbonato/) — primary, 2026-09-22: the exposed registry and its contents, the port-2375 entry, Hermes Agent and the 39-line `SOUL.md`, the fourteen-provider key list, the gateway's model counts, the five-minute /24 scanning, the persistence set and detection indicators quoted above, the Costa Rica attribution, the six-of-seven registries figure. Fetched 2026-09-30. Its command-and-control identifiers (relay AS, Telegram chat id, tunnel-port derivation) are omitted here.
- [The Hacker News — Carbonato Botnet Compromises Docker Hosts to Deploy Telegram-Controlled Hermes AI Agent](https://thehackernews.com/2026/09/carbonato-botnet-compromises-docker.html) — 2026-09-28: independent summary of the ThreatDown findings, the "GH0ST" persona, the reverse-SSH relay, the broader AI-orchestrated-attack context. Fetched 2026-09-30.
- [Hermes Agent (Nous Research)](https://hermes-agent.nousresearch.com/) — the framework's home page, cited by The Hacker News; not opened this sweep.
- Not opened: BleepingComputer ("New Carbonato malware uses AI agents to hijack exposed Docker hosts") and Dark Reading coverage — both exist per search results; those outlets return 403 to this environment.
- Related in this corpus: [Gambit — Hermes/Strix/Cairn skimmer campaign](2026-09-gambit-hermes-strix-cairn-autonomous-agent-retail-skimmer-campaign.md), [knaithe — Hermes autonomous scanning](2026-08-knaithe-hermes-autonomous-ai-scanning.md), [JADEPUFFER agentic ransomware](2026-07-jadepuffer-langflow-agentic-ransomware.md), [MCP scanning campaign (SANS)](2026-07-mcp-scanning-campaign-sans.md).
