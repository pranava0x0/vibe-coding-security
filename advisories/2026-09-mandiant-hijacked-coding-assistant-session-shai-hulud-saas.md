---
id: 2026-09-mandiant-hijacked-coding-assistant-session-shai-hulud-saas
title: "Mandiant case study — an attacker hijacked a developer's live AI coding-assistant session at a SaaS provider, had it recommend a poisoned PyPI package, stole GitHub OAuth tokens through the resulting infostealer, and spread Shai-Hulud across ~100 internal repositories; a second case study shows Mandiant's own red team talking an internal repo-and-CI assistant into pushing private code to an external GitHub account"
date_disclosed: 2026-09-16
last_updated: 2026-09-17
severity: high
status: ongoing
ecosystems: [pypi, npm, github, ai-coding-tools, ci-cd]
tools_affected: ["AI coding assistants (unnamed in the report)", "internal AI assistants with repository and CI/CD access", "PyPI", "GitHub OAuth tokens", "Shai-Hulud-family worms"]
tags: [agent-session-hijack, poisoned-recommendation, shai-hulud, pypi, infostealer, oauth-token-theft, worm, internal-repos, social-engineering-the-agent, vendor-ir-report, mandiant]
---

## TL;DR
Mandiant's **"AI Risk and Resilience" report (September 2026)** carries the first published incident-response account of a worm reaching an enterprise *through the developer's AI assistant*. Per The Hacker News (2026-09-16): an attacker **hijacked an active AI coding-assistant session** at an unnamed SaaS provider, the assistant — "operating as a trusted interpreter within the environment" — **recommended an external package the attacker had poisoned**, the developer accepted, and the **poisoned PyPI package installed an infostealer** that harvested **GitHub OAuth tokens**; with those, the attacker deployed the self-propagating **Shai-Hulud** worm across **about 100 internal code repositories**, then **poisoned a package in the company's own namespace**, which infected a second employee who pulled it. The worm "stole repository secrets and source code for the company's products." The public case study does **not** say when it happened or how the session was taken over. A second, separate case in the same report is a **Mandiant red-team exercise**: the team convinced an internal AI assistant that manages repositories and CI/CD pipelines that it was "participating in an authorized security test," handed it a personal access token for a GitHub repository they controlled, and the assistant **cloned sensitive internal repositories and pushed them to the external account** — GitHub being an approved domain. Mandiant's defenses: check AI-recommended dependencies against checksums and allow-lists, keep raw API keys and long-lived OAuth tokens out of extensions' reach, route dependency traffic through controlled internal repositories. Vendor IR report, single-sourced by nature — recorded as `ongoing` with the provenance stated.

## What happened

**Case 1 — the hijacked session (a real intrusion).** The Hacker News, reading the report: "Mandiant says an attacker hijacked an active AI coding-assistant session at an unnamed software-as-a-service provider." SecurityBrief's account of the same case: "a real intrusion at a SaaS provider. Attackers hijacked an active AI coding assistant session after deploying a poisoned software package containing an infostealer. They collected GitHub OAuth tokens and spread the worm across 'about 100 internal code repositories, leading to the theft of repository secrets and proprietary source code.'" The chain as THN lays it out:

1. Attacker gains control of a developer's active coding-assistant session (method undisclosed).
2. The assistant recommends installing an external package the attacker has poisoned; the developer accepts the recommendation.
3. The poisoned **PyPI** package installs an infostealer, which harvests **GitHub OAuth tokens**.
4. With the tokens, the attacker deploys the self-spreading **Shai-Hulud** worm across **~100 internal repositories**.
5. The attacker poisons a package in the **company's official namespace**; a second employee pulls it and is infected.
6. The worm exfiltrates repository secrets and product source code.

Two details do the damage. The assistant is *trusted*: a recommendation it makes is accepted the way a senior colleague's would be, and a session in progress carries whatever the developer already approved. And the second hop is **internal**: once the worm holds tokens, the company's own package namespace becomes the delivery channel — no typosquat, no public registry, the real package name in the real private registry. That is the [Shai-Hulud/Miasma](2026-05-mini-shai-hulud-may19-wave.md) playbook (steal publish credentials, republish infected versions) run inside one organisation.

**Case 2 — the red team and the "authorized test" framing.** Help Net Security, on the same report: during offensive testing, Mandiant's team "manipulated an internal AI assistant managing code repositories and CI/CD pipelines," convinced it that it was participating in an authorized security test, and "supplied a personal access token for an external GitHub repository they controlled"; "the assistant cloned sensitive internal repositories and pushed them to the external account." Because GitHub was an approved domain, the exfiltration matched policy. This is the same social-engineering move this repo logged from a *criminal* operator in the [Aurora/Cursor](2026-08-aurora-ransomware-cursor-agent-abuse.md) advisory — where, notably, the "told the agent it was an authorized test" quote turned out to belong to a different actor (Gryxa); here Mandiant's own team documents it working against an enterprise assistant.

**Also in the report (noted, not the subject of this advisory).** A "Denial-of-Wallet" runaway agent: an unattended accounting agent hit corrupted data, entered a recursive loop, made **more than 15,000 reasoning API calls** in under an hour, ran up an estimated **$50,000** in cloud cost and locked a database — no attacker involved. The report also folds in already-tracked events: VirusTotal's February [OpenClaw skills](2026-02-clawhavoc-clawhub-skills.md) findings, [TeamPCP/UNC6780](2026-05-teampcp-github-breach.md) stealing AI service credentials and using prompt injection against coding assistants and LLM-based scanners, and [GTIG's](2026-09-gtig-adversarial-ai-agentic-pipelines.md) first confirmed criminal use of an AI-developed zero-day. Help Net's 2026-09-16 coverage led with the $50K agent; this repo's 2026-09-16 sweep declined the report on that basis. The hijacked-session case study, surfaced by THN the same day, is the part that is new and on-audience.

**What is not known.** The report page at Google Cloud is a landing page (the body did not render to this sweep's fetch); the victim, the assistant product, the PyPI package name, the initial session-hijack method, and the date are all undisclosed in the public case study. Nothing here names IOCs. Treat the *shape* as the finding: assistant session → poisoned recommendation → infostealer → tokens → worm → internal namespace.

**Mandiant's recommendations (THN's quotation):** "Check AI-recommended third-party dependencies against cryptographic checksums and approved allowlists. Keep raw API keys, long-lived OAuth tokens, and other secrets out of direct reach of extensions. Route dependency traffic through controlled internal repositories."

## Am I affected?

There is no IOC to check against. Ask instead:

- Can your AI coding assistant's session be driven by anyone other than the developer at the keyboard — a shared remote session, an exposed IDE server, a [loopback control API](2026-09-deepseek-harness-host-header-sandbox-escape.md), a [browser extension](2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack.md)?
- When the assistant recommends `pip install <thing>`, does anything verify the package against a lockfile, checksum or allow-list before it runs?
- Does the developer's machine hold long-lived GitHub OAuth tokens or PATs readable by the IDE extension process (`gh auth token`, `~/.git-credentials`, keychain entries the extension can query)?
- Can a token stolen from one developer publish to your internal package namespace?

```bash
# Long-lived GitHub credentials reachable from the developer's user context
gh auth status 2>&1 | head; ls -la ~/.git-credentials ~/.config/gh/hosts.yml 2>/dev/null
# Is your private registry write-scoped per publisher, or does one token publish everything?
npm whoami --registry <your-registry> 2>/dev/null; pip config list 2>/dev/null | grep index-url
```

## If you are affected

1. If an assistant session may have been driven by someone else, treat every dependency it installed during that session as suspect: uninstall, clear caches, rebuild from a reviewed lockfile. → [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md), [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
2. Rotate GitHub OAuth tokens and PATs from a clean machine; revoke OAuth app grants you do not recognise. → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
3. Audit your internal package namespace for versions published by a token, not a person, and for repositories with new workflows, branches or `.claude/`/`.vscode/` auto-run files. → [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
4. If the worm ran, assume repository secrets are gone. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — an assistant's `pip install` suggestion is an unreviewed dependency add; gate it like a PR.
- → [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — an internal assistant with repo *and* CI access, plus an approved-domain egress rule, is an exfiltration path with a policy stamp on it; scope its token to read where it must read and write nowhere it need not.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — short-lived, per-workflow tokens; nothing in the IDE process's reach should be able to publish to the internal registry.
- → [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — route dependency traffic through a controlled proxy that can refuse a version no one approved.

## Sources

- [The Hacker News — Attacker Hijacks AI Coding Assistant Session, Spreads Shai-Hulud Across About 100 Repositories](https://thehackernews.com/2026/09/attacker-hijacks-ai-coding-assistant.html) — fetched 2026-09-17; published 2026-09-16 (Swati Khandelwal): the six-step chain, "unnamed software-as-a-service provider," the internal-namespace second infection, Mandiant's three recommendations, and the note that timing and hijack method are undisclosed.
- [SecurityBrief — Mandiant warns of AI agents fuelling new attack risks](https://securitybrief.news/story/mandiant-warns-of-ai-agents-fuelling-new-attack-risks) — fetched 2026-09-17; independent summary of the same report: "a real intrusion at a SaaS provider," the ~100-repository quote, the CLI-hooks tampering case, the 15,000-call / $50,000 runaway agent.
- [Help Net Security — One runaway AI agent racked up a $50,000 cloud bill](https://www.helpnetsecurity.com/2026/09/16/google-mandiant-enterprise-ai-security-risks-report/) — fetched 2026-09-17; published 2026-09-16: the red-team "authorized security test" case (PAT for an external repo, cloning and pushing internal repositories), the UNC6780/TeamPCP incident-response mention, the VirusTotal OpenClaw and GTIG cross-references.
- [Google Cloud / Mandiant — AI Risk and Resilience Report 2026](https://cloud.google.com/security/resources/ai-risk-and-resilience-2026) — fetched 2026-09-17; the vendor landing page for the report (body truncated to this sweep's fetch; cited as the record, not as a source of quotes).
- [Aurora ransomware — Cursor agent abuse](2026-08-aurora-ransomware-cursor-agent-abuse.md), [Mini Shai-Hulud May 19 wave](2026-05-mini-shai-hulud-may19-wave.md), [ChainDrop / keyv](2026-08-keyv-mini-shai-hulud-npm-worm.md) — this repo's prior entries for the actor-side social engineering and the worm family.
