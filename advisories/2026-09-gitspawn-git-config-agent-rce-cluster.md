---
id: 2026-09-gitspawn-git-config-agent-rce-cluster
title: "GitSpawn — repo-local git config (core.fsmonitor and others) runs code in 7 AI coding agents before any trust prompt"
date_disclosed: 2026-09-01
last_updated: 2026-09-04
severity: critical
status: active
ecosystems: [claude-code, cursor, openai-codex, goose, qwen-code, grok-build, hermes-agent]
tools_affected: ["Claude Code", "Cursor / Cursor CLI", "OpenAI Codex CLI/Desktop", "Block goose", "Alibaba Qwen Code", "xAI Grok Build", "Hermes Agent"]
tags: [git-config-abuse, core-fsmonitor, pre-trust-execution, sandbox-escape, workspace-trust-bypass, rce, cve, cluster]
---

## TL;DR
Manifold Security researcher Francisco Rosales disclosed **GitSpawn**, a vulnerability class in AI coding agents that run `git` commands (e.g. `git status`) to gather repository context the moment a folder or repo is opened — without stripping the repository's own `.git/config`. Git's `core.fsmonitor` setting (and at least one other, unnamed, still-exploitable key) lets a repo specify a helper program that git executes on any index-refresh operation. A repository shipped with a crafted `.git/config` therefore runs arbitrary attacker code with the developer's full privileges — **before any prompt, tool approval, model call, or workspace-trust dialog**, and outside the agent's sandbox. Eight findings were reported across seven agents between July 1 and August 8, 2026; **four remained unpatched** at publication on 2026-09-01, including a second, distinct Claude Code path (via `claude ultrareview`) still open as of build 2.1.252.

## What happened
`core.fsmonitor` is a legitimate Git performance feature: its value is a command Git runs to ask a filesystem-watcher helper which files changed, instead of walking the whole tree. Git reads this setting from the repository's own `.git/config` — not a global, trusted location — and **any operation that refreshes the index** (`git status`, `git diff`, `git add`, and the repo-context calls agents run on startup) triggers it. An ordinary `git clone` does not carry a source repo's local `.git/config` forward, so exploitation requires the poisoned repository to arrive with its `.git` directory intact — a zip download, a shared drive, a synced folder, a CI artifact, or a "clone this exact tarball" onboarding step all qualify ([Manifold Security](https://www.manifold.security/blog/ai-coding-agents-git-hijack); [paddo.dev](https://paddo.dev/blog/gitspawn-opening-the-folder)).

AI coding agents made this exploitable at scale because they run `git status`-class commands eagerly, on open, to build context for the model — before the user has clicked through any workspace-trust or sandbox-approval dialog. Manifold's own summary: *"no submitted prompt, no model call, no tool approval, no trust prompt. The command executes before [the agent] ever contacts the model."* The researcher notes this reintroduces a class of bug VS Code itself patched in 2021 (CVE-2021-43891, fixed 1.63.1, which blocked git operations in untrusted workspaces) — AI coding agents re-added eager git execution on open and reopened the same hole ([paddo.dev](https://paddo.dev/blog/gitspawn-opening-the-folder)).

**Disclosure timeline** (per Manifold): Grok Build reported 2026-07-01 (closed "informative"), Qwen Code reported 2026-07-07 (accepted by Alibaba), Goose reported 2026-07-13, Grok Build re-reported 2026-07-14, Claude Code `ultrareview` path reported 2026-07-15, Hermes Agent and OpenAI Codex reported 2026-07-20, Cursor reported 2026-08-08, published 2026-09-01.

**Per-agent status at publication:**

| Agent | Affected version(s) | Status | CVE / GHSA |
|---|---|---|---|
| **Block goose** | < 1.44.0 | Patched (1.44.0) | [CVE-2026-72718](https://github.com/aaif-goose/goose/security/advisories/GHSA-r5pp-p5r8-466r) / GHSA-r5pp-p5r8-466r (CVSS 4.0: 7.0) |
| **OpenAI Codex CLI/Desktop** | 0.102.0–0.130.0 (CLI); pre-fix Desktop builds | Patched — three CVEs assigned 2026-09-01 | CVE-2026-19592 (`core.fsmonitor`), CVE-2026-19590 (`core.hooksPath`), CVE-2026-19593 (`attr.tree` + clean filter) |
| **Claude Code** — `core.fsmonitor` path | ≤ 2.1.193 | Patched (2.1.196, 2026-06-29); **no Anthropic advisory published for either Claude Code finding** | none published |
| **Claude Code** — `claude ultrareview` path (separate, unnamed git-config key) | 2.1.210 → **2.1.252 confirmed still vulnerable 2026-09-01** | **Unpatched.** Reported 2026-07-15; closed by Anthropic as a duplicate of an internal ticket. Runs before the workspace-trust prompt is shown. | none published |
| **Hermes Agent** | 0.18.2, 0.21.0 | **Unpatched.** Vendor did not respond across six contact attempts; CVE assigned independently. | [CVE-2026-71963](https://cve.threatint.com/CVE/CVE-2026-71963) (assigned by VulnCheck, an independent CNA) |
| **Alibaba Qwen Code** | 0.19.6, 0.22.3 | **Unpatched** (report accepted 2026-07-07, no fix shipped by publication) | none published |
| **xAI Grok Build** | 0.2.93, 1.0.13 | **Unpatched** (first report closed "informative"; re-report also unresolved) | none published |
| **Cursor / Cursor CLI** | — | Disputed — see note below | none published |

**Note on Cursor's status:** Manifold's own summary table and The Hacker News' writeup list Cursor as patched following the 2026-08-08 report. Separate secondary coverage (CyberSecurityNews, a hacklido.com repost) instead lists "Cursor CLI" as unpatched. Manifold is the primary discloser and is the source this repo defers to, but the discrepancy is unresolved as of this writing — treat Cursor's status as **unconfirmed** rather than fully patched until Cursor publishes its own advisory or Manifold's tracker is checked directly.

This is a distinct, newer disclosure from the already-tracked [Claude Code / Claude Desktop GHSA batch](2026-08-claude-code-desktop-ghsa-batch.md), whose `CVE-2026-55607` (git-worktree path confusion, affecting Claude Code 2.1.38–2.1.163, fixed in 2.1.163) is a different mechanism and an earlier, already-closed window — do not conflate the two when triaging.

## Am I affected?
```bash
# Claude Code
claude --version   # unpatched core.fsmonitor path if <= 2.1.196 predecessor builds;
                    # the `claude ultrareview` path is unpatched through 2.1.252 as of 2026-09-01 — check for a newer fix before trusting any version number here

# goose
goose --version    # affected if < 1.44.0

# OpenAI Codex
codex --version    # affected if in 0.102.0-0.130.0 range; confirm against latest release notes

# Any agent: look for a repo-local fsmonitor hook before opening an unfamiliar repo/archive
git config --get core.fsmonitor
git config --get core.hooksPath
```
You are at risk if you routinely open repositories, extracted archives, or synced folders you did not create yourself in any of the agents above — especially ones delivered as a zip/tarball or copied from a shared location rather than a fresh `git clone` from a URL you control (a plain clone from a remote does not carry the source's local `.git/config`).

## If you are affected
1. Update the affected agent to the patched build listed above; for Claude Code, be aware that **no version is confirmed to close the `ultrareview` path** as of this advisory — avoid `claude ultrareview` against any repository you have not fully reviewed until Anthropic confirms a fix.
2. Treat any machine that opened an untrusted repo/archive in an affected agent before patching as potentially compromised: audit `~/.ssh/authorized_keys`, shell history, and cron/launchd persistence, and rotate any cloud or CI credentials that were present in the environment.
3. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
4. Before opening any repository or extracted archive of unknown provenance, inspect `.git/config` for a `core.fsmonitor`, `core.hooksPath`, or `attr.tree` entry pointing at an executable.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a sandbox flag is not a guarantee when the executing process is git itself, invoked outside the agent's own command sandbox.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — treat "download and open" workflows (zips, shared drives, CI artifacts) as carrying more risk than a plain `git clone`, since only the former preserves a poisoned local `.git/config`.
→ Never run an AI coding agent against a repository whose `.git` directory you did not create via a fresh clone from a URL you chose.

## Sources
- [Manifold Security — GitSpawn: A Single Flaw Lets Untrusted Repos Run Code in Claude Code, Codex, Cursor, and Grok](https://www.manifold.security/blog/ai-coding-agents-git-hijack) — primary disclosure: mechanism, full disclosure timeline, per-agent status table.
- [GitHub Security Advisory GHSA-r5pp-p5r8-466r — Arbitrary command execution in goose CLI via `goose review` via git core.fsmonitor](https://github.com/aaif-goose/goose/security/advisories/GHSA-r5pp-p5r8-466r) — vendor advisory confirming CVE-2026-72718, CVSS 4.0 7.0, credited to Francisco Rosales.
- [The Hacker News — Malicious .git Configs Can Make Claude, Codex, Cursor, and Other AI Agents Run Attacker Code](https://thehackernews.com/2026/09/malicious-git-configs-can-make-claude.html) — independent secondary coverage; per-agent version/CVE table including the three OpenAI Codex CVEs.
- [paddo.dev — Opening the Folder Was the Exploit: GitSpawn, Seven Coding Agents, and a Bug VS Code Fixed in 2021](https://paddo.dev/blog/gitspawn-opening-the-folder) — independent technical follow-up; VS Code CVE-2021-43891 historical context; author's own retest of Claude Code 2.1.259 confirming the `ultrareview` path remained unpatched.
- [OffSeq Threat Radar — CVE-2026-19592: OpenAI Codex CLI](https://radar.offseq.com/threat/cve-2026-19592-cwe-15-external-control-of-system-or-configuration-setting-in-openai-codex-cli-6bb433ae2527fe34) — CVE record detail for the Codex `core.fsmonitor` finding.
