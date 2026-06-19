---
id: 2026-02-sandworm-mode-npm-worm
title: "SANDWORM_MODE — Shai-Hulud-style npm worm with MCP injection, CI implant, and 48-hour delayed activation (Feb 2026)"
date_disclosed: 2026-02-17
last_updated: 2026-06-06
severity: critical
status: active
ecosystems: [npm, mcp, github-actions, ai-agents]
tools_affected: [claude-code, openclaw, any npm package using the compromised accounts, CI pipelines using GitHub Actions]
tags: [supply-chain, credential-theft, worm, mcp-injection, ai-toolchain, ci-cd, github-actions, prompt-injection]
---

## TL;DR
**SANDWORM_MODE** is a self-propagating npm supply-chain worm discovered by Socket in February 2026. It typosquats high-traffic Node.js utilities and AI coding tools (including Claude Code and OpenClaw impersonators), runs a multi-stage credential harvest, and then **injects a malicious MCP server with embedded prompt injection** into the victim's AI coding environment. A built-in **48-hour (+ random jitter) delayed activation** lets the first stage establish itself before the deeper harvest begins, defeating most automated takedown windows.

## What happened

Socket's Threat Research Team identified at least **19 malicious npm packages** across two publisher aliases (confirmed; number may grow). The campaign name comes from `SANDWORM_*` environment-variable switches hard-coded in the malware's runtime control logic.

### Two-stage attack chain

**Stage 1 (immediate, on `npm install`):**
- Steals developer and CI/CD credentials: npm tokens, GitHub tokens, AWS/GCP/Azure keys, SSH keys, crypto wallet seeds.
- Exfiltrates to a GitHub API endpoint with DNS fallback.

**Stage 2 (after 48h + up to 48h random jitter):**
- Deep credential sweep from password managers.
- **MCP server injection**: writes a malicious `mcp.json` / MCP server registration that starts an attacker-controlled local server on the next IDE restart.
- The injected MCP server carries **embedded prompt injection** instructions that silently influence any Claude Code, Cursor, or similar agent using it.
- Installs Git hook persistence (`.git/hooks/pre-commit`, `.git/hooks/post-merge`).
- Launches self-propagating worm: uses stolen npm and GitHub tokens to publish trojanized versions of packages the victim maintains.
- **GitHub Actions CI implant**: patches `.github/workflows/*.yml` to harvest CI secrets (`$GITHUB_TOKEN`, masked secrets, OIDC tokens), inject new workflow triggers, and auto-merge malicious dependency updates.

### Targets

Four packages impersonate AI coding tools directly:
- Three target Claude Code (typosquats on `@anthropic-ai/claude-code` and related)
- One targets OpenClaw (typosquat)

Remaining packages are typosquats of popular Node.js crypto, AI, and dev-utility packages.

The GitHub repository `ci-quality/code-quality-check` was used as a disguised GitHub Action — presented as a "code quality and security scanning" Action for Node.js projects, but actually a CI exfiltration implant.

### Why the delayed activation matters

The 48-hour + jitter window is longer than the typical npm security-team triage window (~6–24 hours). First-stage credential theft and self-propagation have time to spread before the deeper MCP injection payload fires. This means **packages removed from the registry may already have propagated** to other maintainer accounts and seeded CI implants.

## Am I affected?

```bash
# Check for the known indicator environment variable pattern
grep -r "SANDWORM_MODE\|SANDWORM_ENABLED\|SANDWORM_SKIP" node_modules/ ~/.npm/ 2>/dev/null

# Check for suspicious MCP server registrations injected by the worm
# Claude Code
cat ~/.claude/mcp.json 2>/dev/null | jq '.mcpServers' 2>/dev/null
# Cursor
cat ~/.cursor/mcp.json 2>/dev/null | jq . 2>/dev/null

# Look for the ci-quality/code-quality-check Action in your workflows
grep -r "ci-quality/code-quality-check" .github/workflows/ 2>/dev/null

# Check Git hooks for injected code
for h in .git/hooks/pre-commit .git/hooks/post-merge .git/hooks/post-checkout; do
  [ -f "$h" ] && echo "=== $h ===" && head -20 "$h"
done
```

You are affected if:
- You installed any of the 19 flagged packages while they were malicious.
- You added the `ci-quality/code-quality-check` Action to a workflow.
- Your MCP config contains servers you don't recognise.
- Your npm or GitHub publish tokens were accessible from an infected environment.

## If you are affected

1. **Rotate all credentials immediately**: npm tokens, GitHub tokens, AWS/GCP/Azure IAM keys, SSH keys. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
2. **Audit MCP server registrations** — remove any entry you didn't manually configure.
3. **Remove the `ci-quality/code-quality-check` Action** from all workflows and review any workflow changes made in the past 30 days.
4. **Audit Git hooks** in all repos you recently worked on.
5. **Check npm publish history** for any versions you didn't release.
6. **Treat any npm package you maintain** as potentially containing a CI implant — re-examine recent `package.json` and workflow changes.

## Prevention

→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

- Use `npm audit` + Socket's `socket npm` CLI before installing new packages.
- Pin GitHub Actions to full commit SHAs, not tags.
- Never use `ci-quality/code-quality-check` or other unfamiliar "quality scan" Actions.
- Apply `allowedOrgs` lists in your npm token configuration to limit publish scope.
- Audit MCP config files (`~/.claude/mcp.json`, `~/.cursor/mcp.json`) on a schedule, especially after running `npm install`.

## Sources

- [Socket — SANDWORM_MODE: Shai-Hulud-Style npm Worm Hijacks CI Workflow and AI Toolchain](https://socket.dev/blog/sandworm-mode-npm-worm-ai-toolchain-poisoning) — Primary disclosure; full IOC list, technical breakdown, two-stage payload analysis.
- [SecurityWeek — New 'Sandworm_Mode' Supply Chain Attack Hits NPM](https://www.securityweek.com/new-sandworm_mode-supply-chain-attack-hits-npm/) — Independent confirmation; 19-package scope, CI implant details.
- [The Hacker News — Malicious npm Packages Harvest Crypto Keys, CI Secrets, and API Tokens](https://thehackernews.com/2026/02/malicious-npm-packages-harvest-crypto.html) — Campaign overview and developer impact.
- [The Hacker News Weekly Recap (2026-05-xx)](https://thehackernews.com/2026/05/weekly-recap-exchange-0-day-npm-worm.html) — SANDWORM_MODE cited in worm recap alongside later Shai-Hulud waves.
