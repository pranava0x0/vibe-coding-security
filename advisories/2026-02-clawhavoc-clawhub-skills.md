---
id: 2026-02-clawhavoc-clawhub-skills
title: "ClawHavoc — mass malicious-skill poisoning of OpenClaw's ClawHub marketplace (February 2026)"
date_disclosed: 2026-02-01
last_updated: 2026-05-22
severity: high
status: active
ecosystems: [ai-agents, openclaw, clawhub]
tools_affected: [openclaw, clawdbot, moltbot, clawhub-skills]
tags: [supply-chain, credential-theft, ai-agent, skill-marketplace, atomic-stealer, amos, malware, koi-security]
---

## TL;DR
Koi Security found that **ClawHub** — the open-by-default skill marketplace for the self-hosted **OpenClaw** AI agent (formerly Clawdbot / Moltbot) — was flooded with malicious "skills" that install the **Atomic Stealer (AMOS)** infostealer through fake prerequisites. The first audit (early Feb 2026) flagged **341 malicious skills out of 2,857**; as the marketplace ballooned to 10,700+ skills the count more than doubled. Installing an AI-agent skill is functionally `curl | bash` — and ClawHub only requires a GitHub account a week old to publish.

## What happened
ClawHub is "npm for OpenClaw skills" — a community marketplace where anyone can publish plugin-style packages (scripts, configs, resources) that extend the agent's capabilities. It is **open by default**: the only gate to publishing is a GitHub account at least one week old.

Koi Security audited **all 2,857 skills** then on ClawHub and found **341 malicious** ones, of which **335 traced to a single coordinated operation** they named **ClawHavoc** (named 2026-02-01). The first malicious skill was uploaded **2026-01-27** and the campaign surged on **2026-01-31**.

- **Payload:** 335 skills use **fake prerequisites** ("install this dependency first") to drop **Atomic macOS Stealer (AMOS)** — a malware-as-a-service infostealer (~$500–1,000/month) that harvests browser credentials, keychain passwords, crypto-wallet data, SSH keys, and files from user directories. Reporting also notes Windows-targeting variants in the wave.
- **Camouflage:** the malicious skills span ~25 attack categories built to look useful to developers — browser-automation agents, **coding agents**, LinkedIn/WhatsApp integrations, PDF tools, and even **fake security-scanning skills**.
- **Growth:** since the initial blog the marketplace grew from 2,857 to **10,700+** skills and Koi's malicious count **more than doubled to 824**; some trackers tally **~1,184** as removals lagged. Because the marketplace is open-by-default, the surface is **ongoing**, not a one-time event.

This is the AI-agent-skill analogue of the [GlassWorm Open VSX worm](2025-10-glassworm-vscode-worm.md) and the [Nx Console extension compromise](2026-05-nx-console-vscode-compromise.md): an under-governed plugin/extension marketplace becomes a credential-theft delivery channel. It is distinct from the [OpenClaw "Claw Chain" CVEs](2026-05-openclaw-claw-chain.md) (flaws *in* the agent) and the Moltbook token leak (see [vibe platform exposure](ongoing-vibe-platform-exposure.md)) — here the **content in the marketplace** is the threat.

## Am I affected?
You are exposed if you run OpenClaw (or its predecessors Clawdbot/Moltbot) and have installed any third-party skill from ClawHub, especially one that asked you to install a "prerequisite."

```bash
# List installed OpenClaw skills (paths vary by install)
ls -la ~/.openclaw/skills/ ~/.clawdbot/skills/ ~/.moltbot/skills/ 2>/dev/null

# Look for skills that shell out to an installer / fetch a "prerequisite"
grep -rinE 'curl |wget |osascript|installer|prerequisite|brew install|chmod \+x' \
  ~/.openclaw/skills/ 2>/dev/null

# macOS: AMOS commonly stages in /tmp and abuses osascript for a fake password prompt
ls -la /tmp/*.app 2>/dev/null
log show --last 7d --predicate 'process == "osascript"' 2>/dev/null | head
```

If a skill triggered an unexpected install step or a macOS password prompt, treat the machine as compromised.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — same blast-radius logic for a malicious agent extension
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — AMOS exfiltrates everything reachable; rotate from a clean machine

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — treat an agent skill like an untrusted package
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — don't run agent skills with your full user privileges
- Install skills only from publishers you can verify; a one-week-old GitHub account is not a trust signal.
- Be maximally suspicious of any skill that asks you to install a "prerequisite," run a script, or approve an OS password prompt.

## Sources
- [Koi Security — ClawHavoc: 341 Malicious ClawedBot Skills Found by the Bot They Were Targeting](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting) — canonical research, audit method, counts.
- [The Hacker News — Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) — timeline, AMOS, GitHub-account-age gate.
- [Trend Micro — Malicious OpenClaw Skills Used to Distribute Atomic macOS Stealer](https://www.trendmicro.com/en_us/research/26/b/openclaw-skills-used-to-distribute-atomic-macos-stealer.html) — AMOS analysis, delivery via fake prerequisites.
- [eSecurity Planet — Hundreds of Malicious Skills Found in OpenClaw's ClawHub](https://www.esecurityplanet.com/threats/hundreds-of-malicious-skills-found-in-openclaws-clawhub/) — macOS/Windows targeting.
- [The Register — It's easy to backdoor OpenClaw, and its skills leak API keys](https://www.theregister.com/2026/02/05/openclaw_skills_marketplace_leaky_security/) — open-by-default marketplace critique.
- [CyberPress — ClawHavoc Poisons OpenClaw's ClawHub With 1,184 Malicious Skills](https://cyberpress.org/clawhavoc-poisons-openclaws-clawhub-with-1184-malicious-skills/) — updated tally.
- [PointGuard AI — OpenClaw ClawHub Malicious Skills Supply Chain Attack](https://www.pointguardai.com/ai-security-incidents/openclaw-clawhub-malicious-skills-supply-chain-attack) — incident summary.
