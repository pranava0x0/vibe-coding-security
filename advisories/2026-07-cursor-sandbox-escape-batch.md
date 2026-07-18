---
id: 2026-07-cursor-sandbox-escape-batch
title: "Cursor's own GHSA page: 4 more sandbox-escape advisories (May–July 2026), one still unpatched"
date_disclosed: 2026-05-21
last_updated: 2026-07-18
severity: high
status: active
ecosystems: [cursor, ai-coding-agent]
tools_affected: [Cursor Desktop, Cursor Cloud Agent]
tags: [sandbox-escape, workspace-trust, cve, ghsa, python-venv, docker, privileged-container, cloud-agent, unauthenticated-endpoint]
---

## TL;DR

Cursor's own GitHub Security Advisories page (`github.com/cursor/cursor/security`) carries **four sandbox-escape advisories from the last two months** that this repo had not yet tracked, on top of the already-covered DuneSlide, open-folder-autorun, and GhostApproval clusters: **CVE-2026-48124** (Claude hook commands from `.claude/settings.local.json` executed without approval, fixed 3.0.0), **CVE-2026-61613** (Cursor Cloud Agent's browser-controllable local endpoint had no authentication, fixed back in March but only disclosed 2026-07-06), and two **July 14, 2026** advisories with **no CVE and no independent aggregator coverage as of this sweep**: a Python-virtual-environment-tampering sandbox escape (fixed 3.1.2) and a privileged-container escape via Docker/Dev Containers on macOS that **Cursor's own advisory page lists with no patched version**.

## What happened

Cursor discloses vulnerabilities through its own GitHub repository's Security Advisories tab rather than (or in addition to) third-party coordination, and this sweep found four entries there that hadn't surfaced in prior sweeps' aggregator-focused queries.

### CVE-2026-48124 (GHSA-pc9j-3qc2-95wv) — Claude hook auto-execution, CVSS 8.5

Published **2026-05-21**. Cursor Desktop < 3.0.0 executed hook commands defined in a workspace's `.claude/settings.local.json` file when an agent turn completed — **without requiring dedicated user approval**, and without applying the same execution-policy controls Cursor uses for other agent shell commands. A malicious or agent-generated `.claude/settings.local.json` inside a cloned repo, template, or shared workspace is enough: the developer opens the folder, interacts with the agent once, and at turn-completion the planted hook runs with the developer's full privileges — sandbox escape, persistence across turns, or follow-on host compromise. Fixed in **Cursor 3.0.0**, which now requires approval and applies standard execution-policy controls to workspace-sourced hooks. Independently corroborated via SentinelOne's vulnerability database entry (CVSS 8.5, CWE-94).

This is a second, independent instance of the "AI coding tool auto-executes workspace config on open" systemic class already tracked in this repo (alongside Claude Code CVE-2025-59536, the earlier Cursor open-folder-autorun cluster, Windsurf CVE-2026-30615, TrustFall, and Amazon Q CVE-2026-12957) — this time the trust failure is specifically in how Cursor treats a *Claude Code*-formatted hook file it discovers inside an untrusted workspace, not its own native config.

### CVE-2026-61613 (GHSA-whx2-4gvm-m3r3) — Cloud Agent browser sandbox escape, CVSS 7.7

Fixed **2026-03-31**, publicly disclosed **2026-07-06** — a three-month gap between silent fix and public advisory. Browser-enabled Cursor Cloud Agent sessions ran a local control-channel endpoint inside the agent container with **no authentication** (CWE-306). Any web content the agent's browser loaded — a malicious page, an injected ad, a compromised site the agent was asked to visit — could connect to that endpoint from inside the browser sandbox and execute arbitrary code within the Cloud Agent's session. Impact: full session files and repository contents, environment variables and stored secrets, the session's GitHub App access token, and any cloud/CI credentials configured for that agent. Fixed by requiring authentication on the control channel; no user action needed for Cursor-hosted Cloud Agents post-fix. Independently corroborated via a third-party CVE tracker (cve.threatint.eu) in addition to Cursor's own advisory.

### GHSA-p9g2-cr55-cw9c — Python virtual-environment tampering sandbox escape, macOS

Published **2026-07-14**, reported by researcher **Danus365**. An agent running in Cursor's Auto-Run Sandbox mode on macOS could replace a Python virtual environment's interpreter executable with a malicious substitute — a write the sandbox is supposed to permit only inside the workspace. When the **Microsoft Python extension** later invoked that (now-tampered) interpreter from *outside* the sandbox, the substituted wrapper executed arbitrary host commands with the developer's privileges, including writes outside the workspace and launching arbitrary applications. Fixed in **Cursor 3.1.2**. No CVE assigned yet; no independent aggregator coverage found as of this sweep — sourced solely from Cursor's own advisory page.

### GHSA-v4xv-rqh3-w9mc — Privileged-container sandbox escape via Docker, macOS — **no patch listed**

Published **2026-07-14**, same reporter (Danus365). On macOS, with Docker Desktop and the Dev Containers CLI installed, an agent in Auto-Run Sandbox mode could launch a **privileged container** and mount Docker's `virtiofs0` share, which grants read/write access to the user's home directory outside the sandbox — enabling command execution with the developer's privileges with no additional prompt. Cursor's advisory page lists the affected range as "< 3.0.0" but shows **no patched version** in the "Patched versions" field, which is internally inconsistent (Cursor is at 3.11 as of this sweep) — we could not resolve this discrepancy from the advisory page alone and are flagging it rather than guessing. Treat as **unpatched status unconfirmed**: verify against your installed Cursor version and Docker Desktop configuration directly rather than relying on this advisory's version metadata.

## Am I affected?

```bash
# Check your Cursor version
cursor --version   # or Cursor > About Cursor in the app

# CVE-2026-48124 / venv-tampering / privileged-container fixes require >= 3.0.0 / 3.1.2 respectively — update to latest
# Check for a planted Claude-format hook file in any cloned/shared workspace before opening it in Cursor:
find . -maxdepth 2 -name "settings.local.json" -path "*/.claude/*" 2>/dev/null

# If you use Auto-Run Sandbox mode on macOS with the Microsoft Python extension or Docker/Dev Containers installed,
# treat any AI-agent-modified virtualenv interpreter or unexpected privileged container as a compromise signal:
docker ps --filter "label=com.docker.compose.project" --format '{{.Names}}: {{.Command}}' | grep -i privileged
```

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if a Cloud Agent session (CVE-2026-61613) may have exposed a GitHub App token or cloud/CI credential before the March fix

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — treat any workspace-sourced config file (`.claude/`, `.cursor/`, `.vscode/`) in a cloned repo as untrusted input, not documentation

## Why this matters for vibe coders

Cursor now has five independently-disclosed sandbox-escape advisory clusters tracked in this repo across 2026 (DuneSlide, open-folder-autorun, GhostApproval, git.exe-autoexec, and this batch) — each with a different root cause (working-directory allowlisting, symlink fallback, Git hooks, a foreign system binary trusted from the workspace, a foreign config-file format's hooks, an unauthenticated Cloud Agent endpoint, virtualenv tampering, privileged containers). The consistent pattern: **Auto-Run Sandbox mode is not a single security boundary** — it's a collection of ad hoc allow/deny checks around specific operations (writes, working directories, symlinks, subprocess launches), and each new integration surface (a Python extension, Docker, a competitor's hook-file format) has needed its own, separately-discovered fix. Read "sandboxed" as "sandboxed against the specific escapes fixed so far," not as a guarantee.

## Sources
- [GitHub — Cursor Desktop sandbox escape via Claude hook configuration (GHSA-pc9j-3qc2-95wv)](https://github.com/cursor/cursor/security/advisories/GHSA-pc9j-3qc2-95wv)
- [SentinelOne — CVE-2026-48124: Cursor Code Editor RCE Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-48124/)
- [GitHub — Cloud Agent Browser Sandbox Escape (GHSA-whx2-4gvm-m3r3, CVE-2026-61613)](https://github.com/cursor/cursor/security/advisories/GHSA-whx2-4gvm-m3r3)
- [THREATINT — CVE-2026-61613](https://cve.threatint.eu/CVE/CVE-2026-61613)
- [GitHub — Sandbox escape via tampered Python virtual environments (GHSA-p9g2-cr55-cw9c)](https://github.com/cursor/cursor/security/advisories/GHSA-p9g2-cr55-cw9c)
- [GitHub — Sandbox escape via launching privileged containers (GHSA-v4xv-rqh3-w9mc)](https://github.com/cursor/cursor/security/advisories/GHSA-v4xv-rqh3-w9mc)
- [GitHub — cursor/cursor Security Advisories index](https://github.com/cursor/cursor/security)
