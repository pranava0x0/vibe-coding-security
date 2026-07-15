---
id: 2026-07-hallusquatting-ai-agent-hallucination
title: "HalluSquatting — pre-registering AI-hallucinated package/skill/repo names weaponizes coding-agent trust (research, July 2026)"
date_disclosed: 2026-07-08
last_updated: 2026-07-08
severity: high
status: active
ecosystems: [cursor, windsurf, github-copilot, cline, gemini-cli, openclaw]
tools_affected: [cursor, windsurf, github-copilot, cline, gemini-cli, openclaw]
tags: [prompt-injection, hallucination, slopsquatting, botnet, research, agent-trust]
---

## TL;DR
Researchers from Tel Aviv University, the Technion, and Intuit disclosed **HalluSquatting**: a fake package, repository, or agent "skill" pre-registered under a name that AI coding models **consistently hallucinate** when asked to do something ordinary ("clone the repo for X," "install the skill for Y"). When the agent later hallucinates the same fake name and the developer approves the fetch, the attacker's poisoned artifact runs with the developer's own privileges. Tested against **Cursor, Windsurf, GitHub Copilot, Cline, Gemini CLI, and the OpenClaw assistant family**, the technique reached **85% success on hallucinated repository names and 100% success on hallucinated skill installs**. This is a research disclosure — no confirmed in-the-wild campaign yet — but the underlying weakness (agents trusting a name because *they themselves* generated it) is structural, not a single patchable bug, and the researchers say they notified affected vendors/marketplace operators before publishing.

## What happened
This repo already tracks **slopsquatting** as an ongoing pattern (see [ongoing-slopsquatting.md](ongoing-slopsquatting.md)): an attacker registers a package name that LLMs are known to hallucinate when asked to solve a coding problem, and waits for a developer's AI assistant to `pip install`/`npm install` it. HalluSquatting, published **2026-07-08** by Aya Spira and colleagues in Ben Nassi's group at Tel Aviv University, together with Stav Cohen (Technion) and Ron Bitton (Intuit), generalizes the same core idea from "packages a model invents" to **any resource an agent fetches and executes on the developer's behalf**:

1. The researchers first characterized which fake repository names, package names, and agent "skill" names different models **consistently** generate for common prompts ("clone the official X SDK," "install the skill that does Y") — the hallucination has to be reproducible across phrasings and, ideally, across vendor models to be worth squatting.
2. They then registered those exact names on the relevant host (a GitHub repo, an npm/PyPI package, or an agent skill marketplace) with adversarial instructions embedded in the artifact.
3. When a developer's coding agent later hallucinated the same name in response to an ordinary request, and the agent auto-cloned/installed/executed the fetched artifact, the embedded instructions ran with the developer's terminal privileges.

The researchers report this worked against **Cursor, Windsurf, GitHub Copilot, Cline, Google Gemini CLI, and the OpenClaw family of assistants**, with **85% of hallucinated-repository-clone attempts** and **100% of hallucinated-skill-install attempts** succeeding across the tested prompts and models. No CVE has been assigned — the researchers frame this explicitly as a systemic weakness in how agents establish trust in a resource name (the name came from the model's own output, so the agent treats it as more trustworthy than an externally-supplied name), not a bug in any one product. No specific vendor mitigation has been publicly confirmed as of this writing.

This is distinct from — but published in the same window as — this repo's already-tracked [Friendly Fire](2026-07-friendly-fire-defensive-agent-rce.md) (defensive-agent misuse) and [GhostApproval](2026-07-ghostapproval-symlink-trust-boundary.md) (symlinked-config trust bypass) disclosures; HalluSquatting's distinguishing mechanic is that the attacker doesn't need to inject anything into content the agent reads — they only need to **win the race to register a name the model was always going to invent.**

## Am I affected?
There's no version check here — this is a technique against a class of agent behavior, not a single product bug. You're exposed if you regularly let a coding agent (any of the six tools above, or any similar tool) **auto-clone a repository, auto-install a package, or auto-install a "skill"/plugin** based on a name the agent itself generated, without you independently verifying that name against the resource's actual official source first.

```bash
# Quick self-audit: check your shell/agent history for install commands
# where you can't recall independently verifying the package/repo name yourself
history | grep -E 'git clone|npm install|pip install' | tail -50
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — if an agent auto-installed a package you can't verify, treat it as potentially malicious and follow the standard bad-package response.
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — independently verify any package/repo/skill name an agent proposes against the project's own documented source before letting the agent install or clone it; never trust a name just because the model generated it.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — require explicit human confirmation (with the actual URL visible, not just a name) before any agent-initiated clone or install.

## Why this matters for vibe coders
Slopsquatting has mostly been discussed as a package-registry problem (`pip install <hallucinated-name>`). HalluSquatting shows the same mechanic reaches further: repository clones and, notably, **agent "skill"/plugin installs** — a marketplace surface this repo already tracks as poorly gated (see [ClawHavoc](2026-02-clawhavoc-clawhub-skills.md)). A 100% success rate on hallucinated skill installs specifically is a strong signal that skill marketplaces need the same name-verification discipline as package registries, not less.

## Sources
- [The Hacker News — New "HalluSquatting" Attack Could Trick AI Coding Agents Into Installing Malware](https://thehackernews.com/2026/07/new-hallusquatting-attack-could-trick.html)
- [SecurityWeek — HalluSquatting Turns AI Hallucinations Into a Botnet Delivery Mechanism](https://www.securityweek.com/hallusquatting-turns-ai-hallucinations-into-botnet-delivery-mechanism/)
- [Cybersecurity News — HalluSquatting Attack Can Poison AI Coding Assistants](https://cybersecuritynews.com/hallusquatting-attack-poison-ai-coding-assistants/amp/)
- [Cyberpress — Agentic Botnets: HalluSquatting Turns AI Coding Assistants Into Malware Delivery Vectors](https://cyberpress.org/agentic-botnets-hallusquatting-ai-coding/)
