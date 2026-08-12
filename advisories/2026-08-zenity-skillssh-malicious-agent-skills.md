---
id: 2026-08-zenity-skillssh-malicious-agent-skills
title: "Zenity Labs finds dozens of malicious AI-agent skills on Vercel's skills.sh, one family with 1.7M+ installs, abusing Claude Code and OpenClaw as droppers"
date_disclosed: 2026-08-06
last_updated: 2026-08-06
severity: high
status: contained
ecosystems: [ai-agents, skills.sh, claude-code, openclaw]
tools_affected: [skills.sh, claude-code, openclaw]
tags: [supply-chain, credential-theft, ai-agent, skill-marketplace, prompt-injection, self-preservation]
---

## TL;DR
Zenity Labs found dozens of malicious "skills" published to **skills.sh**, Vercel's public registry of AI-agent add-ons, that build trust with legitimate-looking versions before shipping updates that harvest SSH keys, cloud credentials, database logins, and access tokens. One tainted skill family alone reached **1.7 million+ aggregate installs**, with a single skill hitting **250,000+ installs** while undetected for months. Over **30% of the dangerous skills identified abuse Claude Code and OpenClaw as malware droppers** — instructing the agent itself to download and execute an attacker-hosted payload. Some skills showed self-preservation behavior, reinstalling themselves if deleted and rewriting the host agent's own skill-creation tooling. Vercel and GitHub removed the identified skills and repositories within about 12 hours of disclosure, but Zenity warns copied instructions can persist in downstream repos and on machines that already installed them.

## What happened
Presented at Black Hat USA on 2026-08-06, Zenity Labs' research targeted **skills.sh**, a public registry Vercel operates for AI-agent "skills" — the same npm-for-agents pattern already tracked in this repo for OpenClaw's ClawHub (see [ClawHavoc](2026-02-clawhavoc-clawhub-skills.md), which already noted skills.sh as a second affected marketplace per Snyk's May 2026 "ToxicSkills" ecosystem audit). This disclosure is a distinct, named campaign/finding on that same registry, not a re-report of ClawHavoc.

Key findings:
- **Scale:** one tainted skill family reached **1.7 million+ aggregate installs** (download counts, not confirmed unique-victim counts); a separate individual skill reached **250,000+ installs**, entering the platform's top 150 skills, and stayed undetected for "several months."
- **Dropper behavior:** more than **30% of the dangerous skills identified instructed Claude Code or OpenClaw to download and execute an attacker-hosted file** — using the coding agent itself as the malware-delivery mechanism rather than shipping a payload directly in the skill package.
- **Self-preservation:** some skills rewrote the agent's system prompt to resist deletion, and at least one reinstalled itself automatically if removed; researchers also observed a skill replacing Claude's own skill-creator tool without the user's awareness.
- **Typosquatting infrastructure:** the research also uncovered hundreds of reserved-but-empty package names on the registry, apparently staged for future abuse.
- **Detection method:** Zenity built "AI Total," a dynamic-analysis sandbox that observes runtime behavior rather than static code review, to find these skills — a similar rationale to the runtime-behavioral auditing (SkillDetonate) already recommended in the ClawHavoc advisory, since static scan-on-publish has repeatedly been shown to miss this class of payload.
- **Response:** following notification, Vercel and GitHub/Microsoft removed the identified skills, marketplace listings, and repositories within roughly 12 hours. No CVE applies — this is a content-moderation/marketplace-trust incident, not a software vulnerability.

Individual skill/package names were not disclosed in the available coverage, and no CVE was assigned.

## Am I affected?
You're exposed if you or your team installed any third-party skill from skills.sh, especially one whose behavior changed across an update, or one that prompted your agent to run an unfamiliar download-and-execute step.

```bash
# Locate installed skills.sh / agent-skill directories (paths vary by tool)
find ~ -maxdepth 4 -iname "*skill*" -type d 2>/dev/null | grep -vi node_modules

# Look for skills that instruct the agent to fetch and run remote content
grep -rinE 'curl |wget |download.*execute|self-install|reinstall' \
  ~/.claude/skills/ ~/.openclaw/skills/ 2>/dev/null

# Check for unexpected modifications to Claude Code's own skill-creator tooling
git -C ~/.claude 2>/dev/null log --oneline -- skills/ 2>/dev/null
```

If a skill triggered an unexpected download, self-reinstalled after removal, or you find modifications to your own agent tooling you didn't make, treat the machine as compromised.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — same blast-radius logic for a malicious agent extension
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — rotate SSH keys, cloud credentials, database logins, and access tokens from a clean machine

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — treat an agent skill like an untrusted package
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — don't run agent skills with your full user privileges
- A skill's install count and marketplace ranking are not trust signals — the 250,000-install skill in this campaign went undetected for months precisely because of its popularity, not despite it.
- Treat "the coding agent downloads and runs a file" as equivalent to running an unreviewed shell script, regardless of whether the instruction to do so comes from a skill's stated behavior or a later update.
- This is the same class already tracked in [ClawHavoc](2026-02-clawhavoc-clawhub-skills.md): an under-governed AI-agent-skill marketplace becomes a credential-theft delivery channel, and static scan-on-publish has repeatedly failed to catch it (see ClawHavoc's SkillCloak/Trail-of-Bits updates). Prefer curated, internally-managed skill collections over public registries for anything security-sensitive.

## Sources
- [Zenity Labs — Zenity Labs Discovers Dozens of Malicious AI Agent Skills Evading Detection, Launches AI Total](https://zenity.io/company-overview/newsroom/company-news/zenity-labs-discovers-dozens-of-malicious-ai-agent-skills-evading-detection-launches-ai-total) — primary disclosure, install counts, dropper behavior, self-preservation detail.
- [TheNextWeb — Zenity finds malicious AI skills with 1.7M installs in supply-chain credential-theft campaign](https://thenextweb.com/news/zenity-malicious-ai-skills-1-7m-installs-supply-chain-credential-theft) — independent confirmation naming skills.sh as the Vercel-operated registry, 1.7M install figure.
- [Business Wire — Zenity Labs Uncovers 1.7 Million-Install Malicious Skills Campaign](https://www.businesswire.com/news/home/20260806707467/en/Zenity-Labs-Uncovers-1.7-Million-Install-Malicious-Skills-Campaign-and-Dozens-of-Malicious-AI-Agent-Skills) — Vercel/GitHub 12-hour removal response.
