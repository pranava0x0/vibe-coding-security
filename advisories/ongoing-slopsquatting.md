---
id: ongoing-slopsquatting
title: "Slopsquatting — attackers register AI-hallucinated package names"
date_disclosed: 2025-04
last_updated: 2026-05-16
severity: medium
status: ongoing
ecosystems: [npm, pypi]
tools_affected: [any-llm-coding-tool, cursor, claude-code, copilot, codex, v0, lovable, bolt]
tags: [hallucination, supply-chain, typosquatting, ai-generated-code, npm, pypi]
---

## TL;DR
LLMs frequently hallucinate package names that don't exist. Attackers register those exact names on npm and PyPI as malware. The next person who pastes the same hallucinated `import` gets owned. Check Point detected 500+ malicious PyPI packages in two waves of this pattern alone (200 + 300+). The term, coined by Seth Larson / Andrew Nesbitt, is now a recognized class of supply-chain attack.

## What happens
1. You ask Cursor / Claude / Copilot / v0 for a library to do X.
2. The model confidently suggests `pip install fast-image-resize` or `npm install react-vibrant-table` — packages that **don't actually exist**.
3. You run the install. It works. Because an attacker, watching LLM outputs, **registered the hallucinated name** with a payload.
4. The payload steals creds, drops a RAT, or just hijacks future builds.

Variants:
- **Name confusion.** Real package is `colorama`, malicious package is `colorizr` — a plausible name an LLM might suggest.
- **Scope confusion.** Real package is `@stripe/stripe-js`, malicious is `stripe-js` (no scope).
- **Ecosystem confusion.** Python package exists, but the LLM suggests a Node equivalent that doesn't — attacker registers it.

## Am I affected?

```bash
# Audit your package.json / requirements.txt against the registry
# For every dep, manually verify:
# - The publisher matches the project you think you're installing
# - The README links to the official repo
# - The download count and version history look organic (not "1.0.0 published yesterday, 0 weekly downloads")

# A quick smell test:
npm view <package-name> repository.url homepage time
pip show <package-name>  # shows author, homepage, requires
```

Use [Socket](https://socket.dev/), [Snyk](https://snyk.io/), or [npq](https://github.com/lirantal/npq) to flag low-reputation packages before install.

## If you are affected
If you installed a slopsquatted package: same playbook as any other malicious npm/PyPI package.
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — verify before install
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts`, lockfile pinning

**The single highest-leverage habit:** before running an AI-suggested install command, copy the package name and:
1. Open the registry page directly (`npmjs.com/package/X` or `pypi.org/project/X`).
2. Check the publisher, homepage, GitHub link.
3. If the package was published in the last 30 days with no repo, **don't install it**.

This takes 15 seconds. It would have stopped almost every slopsquatting attack.

## Sources
- [Rescana — AI-Hallucinated Dependencies in PyPI and npm: The 2025 Slopsquatting Supply Chain Risk](https://www.rescana.com/post/ai-hallucinated-dependencies-in-pypi-and-npm-the-2025-slopsquatting-supply-chain-risk-explained)
- [TechTarget — Typosquatting campaign, malicious packages slam PyPI](https://www.techtarget.com/searchsecurity/news/366577455/Typosquatting-campaign-malicious-packages-slam-PyPi)
- [Checkmarx — PyPI Supply Chain Attack Uncovered: Colorama and Colorizr Name Confusion](https://checkmarx.com/zero-post/python-pypi-supply-chain-attack-colorama/)
- [The Hacker News — Malicious PyPI, npm, and Ruby Packages Exposed](https://thehackernews.com/2025/06/malicious-pypi-npm-and-ruby-packages.html)
