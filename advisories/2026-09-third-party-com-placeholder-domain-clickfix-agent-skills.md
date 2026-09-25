---
id: 2026-09-third-party-com-placeholder-domain-clickfix-agent-skills
title: "third-party.com — the documentation placeholder that is not IANA-reserved — has served a ClickFix clipboard-poisoning lure to Windows browsers since at least June 2026; it appears in 1,500+ files across 1,700+ public repositories including AI agent skills, MCP-server docs and test fixtures, so every skill or example config that hard-coded it is now a live pointer at attacker infrastructure (Manifold Security, 2026-09-23)"
date_disclosed: 2026-09-23
last_updated: 2026-09-25
severity: medium
status: ongoing
ecosystems: [agent-skills, mcp, documentation, github, windows]
tools_affected: ["any agent skill, MCP-server README, test fixture or sample config that references third-party.com", "coding agents that fetch URLs found in skills or docs", "developers who click example URLs"]
tags: [placeholder-domain, clickfix, clipboard-hijack, agent-skills, mcp, prompt-injection-surface, squatting, documentation, curl-pipe-bash-class, windows]
---

## TL;DR
On **2026-09-23** Manifold Security's Ax Sharma reported that **`third-party.com`** — used for years in docs, tests and examples as a stand-in for "some external service," the way `example.com` is — "serves a ClickFix lure to Windows browsers and a harmless decoy to everything else." Unlike `example.com`/`.net`/`.org`, which IANA reserves, `third-party.com` is an ordinary registration (Network Solutions, 1996) whose owner controls the content, and "since at least June 2026 it's been serving the ClickFix lure": Windows visitors get a fake Cloudflare verification page that poisons the clipboard with a PowerShell command and tells them to paste it into the Run dialog; macOS visitors get "this website requires a Windows PC." GitHub code search finds the domain in **over 1,500 files across 1,700+ repositories**, including projects from Chromium, Sanity and Vercel — and, the part that matters here, **AI agent skills, MCP-server documentation and test fixtures** that cite it as an example endpoint. As Sharma puts it, "In every one of those places it is exactly what it looks like: a placeholder … It is also, now, a live pointer to a ClickFix server." VirusTotal and Google Safe Browsing flag the domain. No code was compromised; the risk is a human or an agent following the URL. Audit what you have shipped, and use only reserved placeholders.

## What happened

**The domain.** `third-party.com` has "been a generic documentation placeholder for years, the same role example.com plays" (Sharma, via THN). It is not reserved: "Anyone could register it, and someone did. Every doc, test, and skill that hard-coded it now points readers at attacker infrastructure." Manifold's post gives the registration as 1996 through Network Solutions; when it changed hands or purpose is not stated.

**What it serves.** Per Manifold and THN: Windows browsers receive a Cloudflare-styled "verify you are human" page that copies a command to the clipboard and instructs the user to run it via the Windows Run dialog; the command "is designed to extract and run a remote PowerShell payload." Non-Windows browsers get a decoy error ("macOS is not supported. This website requires a Windows PC to access"). This is the standard ClickFix / pastejacking pattern documented across 2026's campaigns; what is new is the delivery vector — not a compromised site, not a malvertisement, but **a URL that trusted projects already published**.

**Where it is referenced.** Manifold counts "over 1,500 files across 1,700+ repositories," with "references [that] appear in AI agent skills, MCP-server documentation, and test fixtures," and names Chromium, Sanity and Vercel among the projects. THN: "including those related to AI agent skills and MCP-server docs that cite 'third-party[.]com' as an example endpoint." Manifold's framing of the risk is the `curl | bash` problem transposed: "static URLs in skills represent promises that servers can break later," and an agent that harvests URLs from documentation "may unknowingly fetch from compromised endpoints." THN adds that the weaponised placeholder "can open up avenues for prompt injection and other unintended behaviors" — a coding agent with a fetch tool that follows an example URL from a skill file receives whatever the attacker serves.

**What it is not.** No repository was modified; no package is malicious; the ClickFix page needs a human to paste and run. The agent-side exposure is a fetch of attacker content into context (an injection surface), not code execution. Manifold and THN report the domain as serving the lure "as of writing"; whether it is still doing so on the day you read this is unknown.

**Why it matters for vibe coders.** Skills, `SKILL.md` files, MCP-server READMEs and sample `mcp.json` configs are exactly the artefacts this audience copies verbatim and hands to an agent that can browse. A placeholder that becomes live is a supply-chain change nobody committed — the same lesson as the [abandoned-CDN-domain reuse](2026-09-shai-hulud-111-day-dormant-payload-mcp-package.md) and expired-maintainer-domain takeovers elsewhere in this corpus, but reaching further because a placeholder is *meant* to be copied. It is also a second data point for the "the URL in the skill is the attack surface" class alongside [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) and the [Deadbugz](2026-09-deadbugz-mcp-supply-chain-campaign.md) MCP campaign.

## Am I affected?

```bash
# In every repo, skill directory and MCP config you ship or run:
grep -rniE 'third-party\.com' . --include='*.md' --include='*.json' --include='*.yaml' --include='*.yml' --include='*.ts' --include='*.js' --include='*.py' 2>/dev/null
# Agent-specific locations
grep -rni 'third-party\.com' ~/.claude ~/.cursor ~/.codex ~/.config/opencode 2>/dev/null
# Broader: any non-reserved placeholder your docs use
grep -rniE '(yourcompany|mycompany|your-api|yourdomain|acme-corp)\.(com|net|io)' . 2>/dev/null | head
```

Reserved-for-documentation names that are safe to keep: `example.com`, `example.net`, `example.org`, `*.example`, `*.test`, `*.invalid`, `*.localhost`.

## If you are affected

1. Replace `third-party.com` with `example.com` (or another IANA-reserved name) in every file the grep finds; for hostnames that must resolve in tests, use `*.test` or `*.invalid`.
2. If you or a teammate visited the page on Windows and pasted anything into Run, treat the machine as compromised: → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) (the same triage and rotation order applies to a ClickFix payload), → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).
3. If an agent with a fetch tool followed the URL, review that session's subsequent actions for injected instructions: → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- **Only reserved placeholders in docs, skills, fixtures and sample configs.** Add a lint (a grep in CI) for non-reserved stand-ins — `third-party.com`, `yourcompany.com`, `mycompany.com`, `your-api.com` and lookalikes — as Manifold recommends.
- **Do not allowlist a live domain because a skill or README mentions it**; a skill's URL list is input to be reviewed, not a trust list: [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md), [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- **Give browsing agents a domain allowlist and no clipboard/exec path from fetched content**: [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources
- [Manifold Security — third-party.com now serves ClickFix](https://manifold.security/blog/third-party-com-placeholder-clickfix) — primary, 2026-09-23 (Ax Sharma): what the domain serves and to whom, "since at least June 2026," the 1,500+ files / 1,700+ repositories figure and the Chromium/Sanity/Vercel examples, the agent-skill and MCP-doc references, the `curl | bash` analogy, the 1996 Network Solutions registration, and the reserved-placeholder / audit recommendations. Fetched 2026-09-25.
- [The Hacker News — Placeholder third-party[.]com Referenced Across 1,700+ Repositories Now Serves Malicious Content](https://thehackernews.com/2026/09/placeholder-third-partycom-referenced.html) — 2026-09-24 (Ravie Lakshmanan): the Sharma quotes, the ClickFix mechanics for Windows and the macOS decoy, the VirusTotal / Safe Browsing status, and the prompt-injection framing. Fetched 2026-09-25. (Reports Manifold's research; THN's contribution is the reputation-list status and the ClickFix background.)
- [Manifold Security — blog index](https://manifold.security/blog) — fetched 2026-09-25 for the post date and the companion post "Placeholder domains serving scams" (2026-09-24, Cody Nash), not opened.
- Not fetched: BleepingComputer's coverage ("Placeholder domain used in dev docs now serves ClickFix attacks") — site returns 403 to this sweep.
- Related in this corpus: [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) (a pinned reference that resolves to something else later), [Deadbugz](2026-09-deadbugz-mcp-supply-chain-campaign.md) (MCP metadata that turns hostile after trust is earned), [ongoing slopsquatting](ongoing-slopsquatting.md) (names an LLM will emit that someone then registers).
