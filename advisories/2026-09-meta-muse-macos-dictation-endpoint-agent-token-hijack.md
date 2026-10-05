---
id: 2026-09-meta-muse-macos-dictation-endpoint-agent-token-hijack
title: "Meta Muse for macOS (Meta's personal AI agent, launched 2026-09-17): an undocumented preference, endo_voyager_dictation_endpoint, let any unprivileged local process redirect the agent's dictation traffic to a server it chose — capturing spoken prompts, injecting prompts the agent trusts, and stealing the agent's session token, which carries every permission the user had granted Muse (linked-phone location, device actions); Patrick Wardle published the PoC 88 hours after launch (2026-09-21), Meta hot-fixed within a day by removing the setting"
date_disclosed: 2026-09-21
last_updated: 2026-10-05
severity: high
status: patched
ecosystems: [macos, ai-agents, meta]
tools_affected: ["Meta Muse macOS app (builds before the 2026-09-22 hotfix)", "Muse-linked devices and services reachable with the agent's token", "any personal AI agent that stores its backend endpoint in a user-writable preference"]
tags: [agent-token-hijack, local-privilege-escalation, prompt-injection, dictation, macos, personal-ai-agent, undocumented-setting, meta, zero-day, patched]
---

## TL;DR

Meta shipped **Muse**, its personal AI agent, as a macOS app on **2026-09-17**. On **2026-09-21** Patrick Wardle (Objective-See) published a proof of concept showing that the app read its dictation backend URL from an **undocumented preference, `endo_voyager_dictation_endpoint`, that any process running as the user could change** — no root, no TCC prompt, no entitlement. Point it at your own server and you receive the user's **dictated audio and prompts**, can **return prompts the agent executes as the user's own**, and capture the **authentication material Muse sends with the request** — a token that lets the attacker drive the agent and reach whatever the user had connected to it (VentureBeat cites linked-iPhone location and Bluetooth scans). The prerequisite is code execution as the local user, which is why Meta's David Singleton called it "a local privilege escalation attack, not a remote exploit" with "quite low" practical risk; Meta **hot-fixed within about a day** by removing the setting from production builds, and no exploitation has been reported. The reason this file exists anyway: a personal agent turns ordinary user-level malware — an infostealer, a trojanised extension, a malicious npm postinstall — into something that **holds the agent's identity and permissions**, and the fix was a configuration change, not a redesign of where an agent keeps its trust anchors.

## What happened

- **Launch and disclosure.** Meta announced the Muse macOS app on 2026-09-17; Wardle's thread and the `not-a-mused` proof-of-concept repository went public at 14:42 UTC on 09-21 — "about 88 hours" later (The Register). Muse is Meta's consumer agent (voice, dictation, device actions, linked phone); a sibling product, Muse Code, is a coding agent, and Meta's Muse *Spark* models are the ones in this repo's [eval-containment file](2026-08-meta-irregular-eval-containment-failure.md) — a different incident.
- **The bug.** The app's dictation path read its upstream endpoint from a preference key, `endo_voyager_dictation_endpoint`, that was not documented, not protected and writable by any unprivileged process in the user's session. An attacker-controlled endpoint receives what the app sends there: the dictated audio/prompt stream and the request's authentication material. Because the app treats the response as the transcribed prompt, the endpoint can also **inject prompts** that Muse acts on as if the user had spoken them.
- **What the token buys.** VentureBeat's summary: "the authentication token let attackers control the agent and access linked device information, including geographic locations and device functions"; The Register: "whatever permissions the user previously granted to Muse." That is the point of a personal agent — it is a credential with reach.
- **Meta's response.** Statement via David Singleton (Meta Superintelligence Labs), as quoted by The Register: "This was a local privilege escalation attack, not a remote exploit … the practical risk to users of the Muse Mac app was therefore quite low. Nonetheless, we have issued a hotfix to the app to address the issue." VentureBeat: Meta "hot-fixed the Mac app within a day by removing the setting from production builds." No CVE, no Meta advisory page, no version number for the fixed build in any source this sweep read; the app auto-updates.
- **Wardle's position.** Malwarebytes quotes his recommendation — "Please don't install" — and his framing that "AI agents need a higher security standard than ordinary apps."

**Why "local" is not reassuring here.** Every initial-access story in this repo's npm, PyPI and extension files ends with code running as the developer's user. That is exactly the prerequisite. An infostealer that would once have taken browser cookies and an SSH key now also takes **the agent** — and an agent, unlike a cookie, can act, dictate, and reach the user's linked devices. Enterprise visibility makes it worse: VentureBeat notes Meta's documentation has "no mention of SIEM audit exports, IT admin consoles, or DLP integration," so a hijacked agent's actions would not show up anywhere a security team looks.

## Am I affected?

- You installed Muse for macOS between **2026-09-17 and the 09-22 hotfix** and did not restart the app since. Current builds no longer honour the preference.
- The same shape applies to any agent app that keeps its backend URL, model endpoint or MCP server list in a user-writable config (`defaults`, a JSON in `~/Library/Application Support`, `~/.config`, `~/.claude`, `~/.cursor`) — which is most of them; see the [Claude Code `ANTHROPIC_BASE_URL` exfiltration](2025-08-claude-code-inverseprompt.md) for the coding-agent twin.

```bash
# Muse: confirm the app is current and the preference is absent / inert
defaults domains | tr "," "\n" | grep -i muse | xargs -I{} sh -c 'defaults read {} 2>/dev/null | grep -i dictation_endpoint'
# Generalise: which agent configs on this machine point at a non-vendor host?
grep -rhoE 'https?://[^"'"'"' ]+' ~/.claude ~/.codex ~/.cursor ~/.config/*mcp* 2>/dev/null | sort -u
```

## If you are affected

1. Update Muse (or let it auto-update), quit and relaunch, and **sign out and back in** so any session token captured during the window is invalidated — the sources do not say whether Meta rotated tokens server-side.
2. If you have any reason to think user-level malware ran on the Mac in that window (the actual prerequisite), treat the agent's grants as compromised: review and revoke Muse's connected devices and services, then follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for the machine itself.
3. For teams: there is no audit export to check; ask users directly whether Muse performed actions they did not request.

## Prevention

- Treat agent trust anchors — backend URLs, model endpoints, MCP server lists, API keys — as secrets, not preferences: keychain-backed, integrity-checked, or at minimum not writable by every process in the session. [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md), [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Pin the agent's upstream: an app that will talk to whatever host a config says is an app whose config is the attack surface.
- Before installing a personal agent on a work machine, ask what its token can reach and whether any of it is logged anywhere you can see; the answer here was "linked devices" and "no."
- Keep the developer-machine baseline that makes the prerequisite expensive: no agent installs on the same account that runs untrusted `npm install`s and unvetted extensions — [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Why this matters for vibe coders

Muse itself is a consumer product, but the mechanism is the one every agent on your laptop shares: a config file decides where the agent sends your prompts and its credentials, and that file is writable by the same user that runs your package installs. This repo already has the coding-agent version of this bug (Claude Code's `ANTHROPIC_BASE_URL` in a repo-local `.env`); Muse is the personal-agent version, with a session token that reaches your phone. When the next stealer's harvest list includes "AI-agent config files" — as the one in [this week's npm compromise](2026-10-subql-common-npm-postinstall-stealer-ci-workflow-injection.md) does — this is what it is looking for.

## Sources

- [The Register — Meta Muse AI app flaw lets local malware redirect dictation traffic](https://www.theregister.com/ai-and-ml/2026/09/21/meta-muse-ai-app-flaw-lets-local-malware-redirect-dictation-traffic/5297980) — 2026-09-21 (updated 09-22), Thomas Claburn: the preference key, the unprivileged-process prerequisite, what is captured, the 88-hour gap, Wardle's `not-a-mused` PoC, Meta's statement via David Singleton quoted above. Fetched 2026-10-05.
- [Malwarebytes — Meta's Muse AI assistant has a zero-day that can turn it into a Mac backdoor](https://www.malwarebytes.com/blog/bugs/2026/09/metas-muse-ai-assistant-has-a-zero-day-that-can-turn-it-into-a-mac-backdoor) — 2026-09-22, Pieter Arntz: the attack capabilities, the local-code-execution prerequisite, Wardle's "Please don't install" and "higher security standard" quotes. Fetched 2026-10-05.
- [VentureBeat — Meta patched Muse's zero-day, but security teams still lack visibility into what the agent can access](https://venturebeat.com/security/meta-patched-muses-zero-day-but-security-teams-still-lack-visibility-into-what-the-agent-can-access) — 2026-09-22, Louis Columbus: the "within a day … removing the setting from production builds" fix, the linked-iPhone location and Bluetooth-scan reach, the absence of SIEM/DLP/admin-console documentation. Fetched 2026-10-05.
- [Noma Security — Personal AI Agent Security: Discovering and Governing dots, Grok Bot, Instinct, Muse, & Muse Code](https://noma.security/blog/personal-ai-agent-security-discovering-and-governing-dots-grok-bot-muse-muse-code) — 2026-10-02, vendor blog; the pointer that surfaced this incident for the sweep, plus the Muse / Muse Code product distinction. Fetched 2026-10-05; incident facts above are taken from the three outlets, not from this post.
- Not fetched: Patrick Wardle's X thread and the `not-a-mused` repository (X is not reachable from this environment; the repository is cited by The Register and was not opened — the PoC is out of scope for this repo).
- Related in this repo: [Claude Code `ANTHROPIC_BASE_URL` key exfiltration](2025-08-claude-code-inverseprompt.md), [Meta / Irregular eval containment failure](2026-08-meta-irregular-eval-containment-failure.md) (a different Muse incident), [Claude Desktop Cowork host-boundary advisories](2026-08-claude-code-desktop-ghsa-batch.md).
