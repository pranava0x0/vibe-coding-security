---
id: 2026-02-clawhavoc-clawhub-skills
title: "ClawHavoc — mass malicious-skill poisoning of OpenClaw's ClawHub marketplace (February 2026)"
date_disclosed: 2026-02-01
last_updated: 2026-07-08
severity: high
status: active
ecosystems: [ai-agents, openclaw, clawhub]
tools_affected: [openclaw, clawdbot, moltbot, clawhub-skills, skills.sh]
tags: [supply-chain, credential-theft, ai-agent, skill-marketplace, atomic-stealer, amos, malware, koi-security, snyk, toxicskills, prompt-injection]
---

## TL;DR
Koi Security found that **ClawHub** — the open-by-default skill marketplace for the self-hosted **OpenClaw** AI agent (formerly Clawdbot / Moltbot) — was flooded with malicious "skills" that install the **Atomic Stealer (AMOS)** infostealer through fake prerequisites. The first audit (early Feb 2026) flagged **341 malicious skills out of 2,857**; as the marketplace ballooned to 10,700+ skills the count more than doubled. Installing an AI-agent skill is functionally `curl | bash` — and ClawHub only requires a GitHub account a week old to publish.

## What happened
ClawHub is "npm for OpenClaw skills" — a community marketplace where anyone can publish plugin-style packages (scripts, configs, resources) that extend the agent's capabilities. It is **open by default**: the only gate to publishing is a GitHub account at least one week old.

Koi Security audited **all 2,857 skills** then on ClawHub and found **341 malicious** ones, of which **335 traced to a single coordinated operation** they named **ClawHavoc** (named 2026-02-01). The first malicious skill was uploaded **2026-01-27** and the campaign surged on **2026-01-31**.

- **Payload:** 335 skills use **fake prerequisites** ("install this dependency first") to drop **Atomic macOS Stealer (AMOS)** — a malware-as-a-service infostealer (~$500–1,000/month) that harvests browser credentials, keychain passwords, crypto-wallet data, SSH keys, and files from user directories. Reporting also notes Windows-targeting variants in the wave.
- **Camouflage:** the malicious skills span ~25 attack categories built to look useful to developers — browser-automation agents, **coding agents**, LinkedIn/WhatsApp integrations, PDF tools, and even **fake security-scanning skills**.
- **Growth:** since the initial blog the marketplace grew from 2,857 to **10,700+** skills and Koi's malicious count **more than doubled to 824**; some trackers tally **~1,184** as removals lagged. Because the marketplace is open-by-default, the surface is **ongoing**, not a one-time event.

### Update (May 2026) — Snyk "ToxicSkills": the problem is the whole ecosystem, not one campaign
Snyk Labs published the first comprehensive security audit of the AI-agent-skill ecosystem, scanning **3,984 skills across ClawHub *and* skills.sh** (snapshot 2026-02-05). The results generalize ClawHavoc from "one bad campaign" to a structural problem:

- **Prompt injection in 36%** of skills tested; **1,467 malicious payloads** across the ecosystem; **534 of 3,984 (13.4%)** carried critical-level issues; 76 confirmed credential-theft / backdoor / exfil payloads. **8 malicious skills were still live on clawhub.ai at publication.**
- **"ToxicSkills" threat class:** a skill that looks harmless under static review but behaves maliciously *when executed by a capable agent* — the agent itself is the gadget that turns benign-looking instructions into actions.
- **Runtime-fetch evasion:** **2.9% of ClawHub skills (21% of malicious samples) dynamically fetch and execute remote content at runtime.** The published skill passes review; the attacker swaps the payload later on their own infrastructure. This breaks naive "scan-on-publish" defenses — Snyk's companion piece argues a **skill scanner is often false security** (and can itself be malware).
- **Second marketplace:** **skills.sh** joins ClawHub as an affected surface; this is a class issue across agent-skill registries, not a single site.

### Update (2026-07-06) — SkillCloak/SkillDetonate: academic research shows scanner-evasion for skill malware is trivial, and proposes a runtime fix
Researchers at Hong Kong University of Science and Technology published **SkillCloak**, a proof-of-concept tool that rewrites a malicious Agent Skill to preserve its payload while evading static scanners — via structural obfuscation (character substitution) and **self-extracting packing** that hides payloads in directories scanners typically skip. Tested against 8 static scanners, the packing technique evaded detection **>90% of the time (>99% against most individual scanners)**; even lighter rewriting cleared most scanners **>80%** of the time. The paper targets Agent Skills for **Claude Code, OpenAI Codex, and OpenClaw** specifically, and cites this repo's already-tracked ClawHavoc campaign's malicious-skill counts as real-world grounding.

The same researchers built **SkillDetonate**, a sandboxed runtime auditor that inspects a skill's actual OS-level behavior and data flow rather than its static appearance — catching **97%** of attacks in controlled testing (2% false-positive rate) and **87%** of real-world malicious skills, versus roughly 10% for static scanners alone.

**Why this matters beyond the original ClawHavoc campaign:** this is independent academic confirmation of the "skill scanner is often false security" finding Snyk's ToxicSkills audit already surfaced (see above) — and it demonstrates the evasion is not merely theoretical or specific to one marketplace's scanner, but generalizes across at least 8 tested tools with a simple, repeatable packing technique. No CVE applies (this is a research/tooling disclosure, not a specific incident), but the practical takeaway is the same: **static scan-on-publish is not a sufficient control for AI-agent skill marketplaces**, and runtime behavioral monitoring (SkillDetonate's approach, or equivalent sandboxed execution auditing) is the direction defenders should move toward.

### Why this keeps happening
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
- A clean static scan is not a clean bill of health: skills that fetch-and-execute remote content at runtime can flip malicious after review (Snyk ToxicSkills), and academic research (SkillCloak) shows trivial repackaging evades static scanners >90% of the time. Don't trust a "skill scanner" badge as proof of safety — prefer marketplaces or tooling that do runtime/sandboxed behavioral analysis.

## Sources
- [Koi Security — ClawHavoc: 341 Malicious ClawedBot Skills Found by the Bot They Were Targeting](https://www.koi.ai/blog/clawhavoc-341-malicious-clawedbot-skills-found-by-the-bot-they-were-targeting) — canonical research, audit method, counts.
- [The Hacker News — Researchers Find 341 Malicious ClawHub Skills Stealing Data from OpenClaw Users](https://thehackernews.com/2026/02/researchers-find-341-malicious-clawhub.html) — timeline, AMOS, GitHub-account-age gate.
- [Trend Micro — Malicious OpenClaw Skills Used to Distribute Atomic macOS Stealer](https://www.trendmicro.com/en_us/research/26/b/openclaw-skills-used-to-distribute-atomic-macos-stealer.html) — AMOS analysis, delivery via fake prerequisites.
- [eSecurity Planet — Hundreds of Malicious Skills Found in OpenClaw's ClawHub](https://www.esecurityplanet.com/threats/hundreds-of-malicious-skills-found-in-openclaws-clawhub/) — macOS/Windows targeting.
- [The Register — It's easy to backdoor OpenClaw, and its skills leak API keys](https://www.theregister.com/2026/02/05/openclaw_skills_marketplace_leaky_security/) — open-by-default marketplace critique.
- [CyberPress — ClawHavoc Poisons OpenClaw's ClawHub With 1,184 Malicious Skills](https://cyberpress.org/clawhavoc-poisons-openclaws-clawhub-with-1184-malicious-skills/) — updated tally.
- [PointGuard AI — OpenClaw ClawHub Malicious Skills Supply Chain Attack](https://www.pointguardai.com/ai-security-incidents/openclaw-clawhub-malicious-skills-supply-chain-attack) — incident summary.
- [Snyk — ToxicSkills: Prompt Injection in 36%, 1,467 Malicious Payloads across the Agent-Skills Supply Chain](https://snyk.io/blog/toxicskills-malicious-ai-agent-skills-clawhub/) — ecosystem-wide audit (ClawHub + skills.sh), runtime-fetch evasion, ToxicSkills class.
- [Snyk — Why Your "Skill Scanner" Is Just False Security (and Maybe Malware)](https://snyk.io/blog/skill-scanner-false-security/) — why scan-on-publish defenses fail.
- [Snyk — How a Malicious Google Skill on ClawHub Tricks Users Into Installing Malware](https://snyk.io/blog/clawhub-malicious-google-skill-openclaw-malware/) — worked example of a high-ranking malicious skill.
- [The Hacker News — New SkillCloak Technique Lets Malicious AI Agent Skills Evade Static Scanners](https://thehackernews.com/2026/07/new-skillcloak-technique-lets-malicious.html) — HKUST research; SkillCloak evasion rates, SkillDetonate runtime-auditor results, affected tools (Claude Code, OpenAI Codex, OpenClaw).
