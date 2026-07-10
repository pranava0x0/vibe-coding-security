---
id: 2026-07-ghostapproval-symlink-trust-boundary
title: "GhostApproval — symlinked config files trick 6 AI coding assistants into writing outside the workspace (July 2026)"
date_disclosed: 2026-07-08
last_updated: 2026-07-08
severity: high
status: active
ecosystems: [claude-code, cursor, amazon-q, windsurf, google-antigravity, agent-frameworks]
tools_affected: [Anthropic Claude Code, Cursor, Amazon Q Developer, Google Antigravity, Windsurf, Augment]
tags: [symlink, trust-boundary, ui-misrepresentation, approval-dialog, ssh-key-theft, no-single-patch]
---

## TL;DR

Wiz Research disclosed **GhostApproval**: a malicious repository containing a symlink disguised as an ordinary config file (`project_settings.json` → really `~/.ssh/authorized_keys`) can trick **six AI coding assistants** into writing attacker-controlled content through the link — while the tool's confirmation dialog shows the harmless symlink path, not the real target. A developer who approves "add a line to project_settings.json" is actually approving a write to their SSH `authorized_keys` file, handing an attacker passwordless remote access. **AWS, Cursor, and Google shipped fixes; Augment and Windsurf acknowledged but haven't patched; Anthropic rejected it as "outside our threat model."**

## What happened

Published **2026-07-08**, Wiz's proof of concept works like this: a cloned repo contains a symlink named to look like an innocuous project file. The repo's README instructs the agent to "add a line" to that file — a completely ordinary-sounding setup instruction. When the developer asks the agent to "set up the workspace" or "follow the README," the agent resolves the symlink and writes the attacker's payload (an SSH public key, a malicious shell alias, etc.) through it into the real target outside the workspace: `~/.ssh/authorized_keys`, `~/.zshrc`, or similar.

Two chained weaknesses make this work:

- **CWE-61 (symlink following)** — the agent follows the symlink without canonicalizing the path or checking whether the resolved target is inside the workspace boundary.
- **CWE-451 (UI misrepresentation)** — the approval/confirmation dialog shown to the developer displays the *original, unresolved symlink path* rather than where the write will actually land. In several cases Wiz found the agent's own internal reasoning correctly identified the dangerous real target — but the UI never surfaced that to the human approving the action. As Wiz put it: "the human is still in the loop, but the loop is showing them the wrong thing."

Six tools were confirmed affected, with divergent vendor responses:

| Tool | Affected version | CVE | Status |
|---|---|---|---|
| Amazon Q Developer | < 1.69.0 | CVE-2026-12958 | Fixed |
| Cursor | < 3.0 | CVE-2026-50549 | Fixed |
| Google Antigravity | < 1.19.6 | pending | Fixed |
| Augment | 0.754.3 | — | Acknowledged, in progress |
| Windsurf | v1.9566 | — | Acknowledged, in progress |
| Anthropic Claude Code | v2.1.42 | — | Disputed / rejected |

Note: Cursor's CVE-2026-50549 and Amazon Q's CVE-2026-12958 were **already disclosed under different names** — CVE-2026-50549 is one of the two [DuneSlide](2026-06-cursor-duneslide-zeroclick-rce.md) flaws (symlink-resolution fallback), and CVE-2026-12958 is the symlink-bypass half of the [Amazon Q Developer `.amazonq/mcp.json`](2026-06-amazon-q-mcp-workspace-rce.md) disclosure. GhostApproval is Wiz's finding that the *same symlink-trust-boundary root cause* recurs independently across Claude Code, Augment, Windsurf, and Google Antigravity — a systemic pattern, not a single bug, reported to Anthropic starting **2026-02-12**.

Timeline: discovered in testing 2026-02-10; reports submitted 2026-02-12 to 2026-02-15 (Anthropic rejected as "outside our threat model" within days); vendors acknowledged through early March; Google, AWS, and Cursor shipped fixes between 2026-05-22 and 2026-06-05; CVEs assigned 2026-06-23; publicly disclosed 2026-07-08. Wiz reports no evidence of in-the-wild exploitation — this is disclosed research, not an active campaign.

## Am I affected?

You're in scope if you use **Claude Code, Cursor (< 3.0), Amazon Q Developer (< 1.69.0), Google Antigravity (< 1.19.6), Augment, or Windsurf** and ever ask the agent to process instructions from an untrusted or unfamiliar repository (a fork, a coding-challenge repo, a dependency you're evaluating).

Quick self-test before opening an unfamiliar repo:
```bash
find . -type l -exec ls -la {} \;
```
Any symlink whose target resolves **outside** the repo directory (especially into `$HOME`, `~/.ssh`, or a dotfile) is a red flag — do not let an agent "set up" or "follow the README of" that repo until you've inspected it manually.

## If you are affected

- If you're on **Cursor < 3.0, Amazon Q Developer < 1.69.0, or Google Antigravity < 1.19.6**, update immediately — these are patched.
- If you use **Claude Code, Augment, or Windsurf**, there is no vendor fix to rely on. Treat any repo-processing session where the agent is asked to write to config files as a manual-review step: read the confirmation dialog's *canonicalized* target, not just the displayed path, or check `readlink -f <path>` yourself before approving.
- If you already approved a suspicious write in one of the unpatched tools, check `~/.ssh/authorized_keys`, shell rc files, and any credential files the session touched for unauthorized entries, and rotate any credentials in files the agent could have reached.

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- **Never approve an AI agent's file-write action based on the path shown in the dialog alone** — resolve symlinks yourself (`readlink -f`) before confirming, especially in unfamiliar repos.
- **Audit cloned repos for symlinks before letting an agent "set up" or process them**: `find . -type l` and check every target is inside the repo.
- **Run agents processing untrusted repos in an isolated environment** (container, VM, throwaway user account) where `~/.ssh` and other sensitive paths don't exist or are read-only.
- **This is a sibling of the "AI coding tool auto-executes workspace config on open" class** (Claude Code CVE-2025-59536, Cursor CVE-2025-54136, Windsurf CVE-2026-30615, Amazon Q CVE-2026-12957/-12958) — the common defensive pattern is the same: don't let agent-readable repo content (README instructions, symlinks, config files) cross into a privileged write without independently verifying the real target.

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources

- [Wiz Research — GhostApproval: A Trust Boundary Gap in AI Coding Assistants](https://www.wiz.io/blog/ghostapproval-a-trust-boundary-gap-in-ai-coding-assistants) — primary disclosure; full per-tool CVE/version table, disclosure timeline, attack chain detail.
- [The Hacker News — GhostApproval Symlink Flaws Could Let Malicious Repos Run Code in AI Coding Agents](https://thehackernews.com/2026/07/ghostapproval-symlink-flaws-could-let.html) — independent corroboration of affected-tool list, CVE numbers, and vendor status.
- [The Register — Bug in top AI coding agents shows that Unix-era security headaches never really die](https://www.theregister.com/security/2026/07/08/bug-in-top-ai-coding-agents-shows-that-unix-era-security-headaches-never-really-die/5268025) — additional corroboration and vendor-response framing.
