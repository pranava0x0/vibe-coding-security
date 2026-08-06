---
id: 2026-08-claude-code-desktop-ghsa-batch
title: "Claude Code / Claude Desktop's own GHSA index: 8 more advisories (Feb–Jun 2026) this repo hadn't tracked"
date_disclosed: 2026-02-06
last_updated: 2026-08-06
severity: high
status: patched
ecosystems: [claude-code, claude-desktop, anthropic]
tools_affected: ["Claude Code CLI / Agent SDK", "Claude Desktop for Windows", "Claude Cowork / CoworkVMService"]
tags: [sandbox-escape, privilege-escalation, mitm, data-exfiltration, symlink, directory-junction, command-injection, cve, ghsa, claude-code, claude-desktop]
---

## TL;DR

A direct audit of `github.com/anthropics/claude-code/security/advisories` — the same "walk the vendor's own GHSA index" discipline this repo applied to Cursor on 2026-07-18 — turned up **8 patched CVEs from February–June 2026** that had not surfaced in this repo's prior aggregator-focused sweeps, on top of the already-tracked InversePrompt cluster. All are fixed and most ship automatically via Claude Code's auto-update, but two (**CVE-2026-44470**, **CVE-2026-44467**) affect Claude Desktop for Windows specifically and require a manual update if auto-update is disabled.

## What happened

Anthropic discloses Claude Code and Claude Desktop vulnerabilities primarily through its own GitHub Security Advisories, and — as with Cursor's advisory page in a prior sweep — several entries here had not been picked up by search-engine-driven queries, likely because they lack independent aggregator coverage. All seven CVE↔GHSA pairings below were confirmed by fetching the advisory page directly; the two highest-severity were cross-confirmed against NVD.

### CVE-2026-55607 (GHSA-7835-87q9-rgvv) — Sandbox escape via git worktree path confusion, CVSS 8.8/7.7, published 2026-06-25

Claude Code's worktree handling allowed creating a worktree literally named `.git`, enabling git-directory confusion. Combined with path traversal in worktree navigation, symlink manipulation, and abuse of git's `fsmonitor` hook execution during worktree operations, a malicious repository containing prompt-injection content could get Claude Code to overwrite files in the user's home directory (e.g., `.zshenv`) and execute code **outside the seatbelt sandbox**. Affected: `>= 2.1.38, < 2.1.163`. Patched: **2.1.163**.

### CVE-2026-54316 (GHSA-fg94-h982-f3mm) — Out-of-band exfiltration via pre-approved HuggingFace domain in WebFetch, CVSS 6.0, published 2026-06-13

`huggingface.co` was pre-approved as a bare hostname for the WebFetch tool, so **any path** on that domain was auto-fetched with no permission prompt and no `--allowedTools` gating. An attacker able to inject untrusted content into Claude's context could direct WebFetch at attacker-controlled HuggingFace repository files (e.g., a `resolve/main/config.json` path) and use HuggingFace's own download-counting mechanism as a covert side channel to exfiltrate file contents, environment variables, or command output — no outbound connection to an unfamiliar domain required, the same "allowlisted host as camouflage" shape this repo has tracked for AI-vendor-host exfil, just applied to an allowlisted *third-party* domain instead. Affected: `>= 0.2.54, < 2.1.163`. Patched: **2.1.163**. Reported via HackerOne (novee).

### CVE-2026-44470 (GHSA-5p5x-5294-qhp3) — CoworkVMService directory-junction LPE, CVSS 8.5/7.8, published 2026-05-06

On Windows, `CoworkVMService` runs as **SYSTEM** and creates files inside the Cowork VM bundle directory without checking whether that path is a real directory or an NTFS directory junction. A local, non-elevated user can replace the user-writable bundle directory with a junction pointing anywhere on disk; the SYSTEM-privileged service then creates SYSTEM-owned files at the attacker's chosen location — full local privilege escalation. Affected: **Claude Desktop for Windows < 1.3834.0**. Patched: **1.3834.0**. Independently confirmed via NVD. Note: this is a distinct, already-patched CoworkVMService bug, separate from the unresolved Armadin DLL-sideloading/RPC-abuse chain already tracked in [Claude Cowork for Windows sandbox escape](2026-07-claude-cowork-sandbox-escape.md) — same component, two unrelated root causes.

### CVE-2026-44467 (GHSA-3rwf-2g6p-c2f9) — SSH host key verification bypass enables MITM, CVSS 7.8/7.4, published 2026-05-06

Claude Desktop's SSH remote-development feature checked only whether a hostname existed in `~/.ssh/known_hosts`, **without comparing the presented host key against the stored one**. A network-positioned attacker (rogue Wi-Fi, ARP/DNS spoofing) who intercepts a connection to an already-known host can present any host key and have it silently accepted, letting them read and modify traffic in a full MITM. Affected: `>= 1.2581.0, < 1.4304.0`. Patched: **1.4304.0**.

### CVE-2026-46406 (GHSA-4vp2-6q8c-pvq2) — Insecure temp file in `/copy` command, CVSS 6.1, published 2026-06-25

The `/copy` command wrote responses to a hardcoded, predictable path (`/tmp/claude/response.md`) with no UID isolation, randomness, or symlink protection — world-readable (0644) in a world-traversable directory (0755), letting any local user read a privileged user's Claude output (which may contain secrets), and letting a local attacker pre-plant a symlink at that path to redirect the privileged write to an arbitrary file. Affected: `>= 2.1.59, < 2.1.128`. Patched: **2.1.128**.

### CVE-2026-40068 (GHSA-q5hj-mxqh-vv77) — Trust dialog bypass via git worktree spoofing, CVSS 7.7, published 2026-04-24

Folder-trust determination read the git worktree `commondir` file without validating its contents. A crafted repository's `commondir` pointing at a path the victim had previously trusted let Claude Code skip the trust-confirmation dialog entirely and immediately execute hooks defined in `.claude/settings.json` — arbitrary command execution with no prompt shown, provided the attacker can guess or learn a path the victim already trusts. Affected: `>= 2.1.63, < 2.1.84`. Patched: **2.1.84**.

### CVE-2026-35020 (GHSA-jgg3-qqhf-7rx7) — OS command injection via `TERMINAL` environment variable, published 2026 (Claude Code CLI and Claude Agent SDK)

Claude Code CLI and the Claude Agent SDK for Python built a shell command incorporating the `TERMINAL` environment variable without sanitizing shell metacharacters, executable via normal CLI usage or the deep-link handler, running arbitrary commands under the invoking user's privileges. Affected: Claude Code `<= 2.1.91`, Claude Agent SDK for Python `<= 0.1.55`. Patched: Claude Code **2.1.92**, Claude Agent SDK **0.1.56**.

### CVE-2026-25722 (GHSA-66q4-vfjg-2qhh) — Command injection via directory change bypasses write protection, CVSS 7.7, published 2026-02-06

Claude Code's write-protection guardrail (which blocks unapproved writes to sensitive directories like `.claude/`) didn't properly re-validate the working directory after a `cd` command changed it — an attacker able to get untrusted content into the context window could have the agent `cd` into a protected directory and then write/modify files there without triggering the approval check. Combines **CWE-20** (improper input validation) and **CWE-78** (OS command injection). Affected: `< 2.0.57`. Patched: **2.0.57**. Reported via HackerOne (nil221) — one of this repo's earliest-dated finds in this batch, predating even the April 2026 CVEs above by two months, and found via this sweep's index walk rather than any prior aggregator query.

**Update (2026-08-06):** added this eighth entry, found on a follow-up pass of Cursor's *and* Claude Code's own GHSA indexes in the same sweep — two other candidate GHSA IDs found in that pass (GHSA-5cwg-9f6j-9jvx / CVE-2026-35603, GHSA-mmgp-wc2j-qcv7 / CVE-2026-33068) turned out to already be listed (without full write-ups) in the InversePrompt cluster advisory's CVE roster — confirmed via direct grep before treating them as new, per this repo's standing "verify the actual IOC/CVE list, don't trust a prior summary" discipline.

All eight are distinct from the CVEs already listed in this repo's [Claude Code InversePrompt cluster](2025-08-claude-code-inverseprompt.md) (CVE-2025-54794, CVE-2025-54795, CVE-2025-52882, CVE-2025-59536, CVE-2026-21852, CVE-2026-33068, CVE-2026-24887, CVE-2026-35021, CVE-2026-39861, CVE-2026-35603, CVE-2026-25723) and the [git.exe / DuneSlide-class](2026-07-cursor-git-exe-autoexec.md) findings tracked elsewhere in this repo.

## Am I affected?

```bash
# Check your Claude Code CLI version
claude --version

# Fixes for all eight land at or before 2.1.163 — anything below that on a manual-update install is exposed to at least one
# Claude Agent SDK for Python — check for TERMINAL-injection fix
pip show claude-agent-sdk 2>/dev/null | grep -i version   # need >= 0.1.56

# Claude Desktop for Windows — CoworkVMService LPE and SSH MITM require >= 1.3834.0 and >= 1.4304.0 respectively
# Help > About Claude in the desktop app
```

Users on Claude Code's standard auto-update have already received all eight fixes; this advisory matters mainly for pinned/manual-update installs, CI images that bake in a specific Claude Code version, and Claude Desktop for Windows users who've disabled auto-update.

## If you are affected

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if you ran an affected version against an untrusted repo or over an untrusted network path

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — treat cloned repos as untrusted input; don't assume "sandboxed" covers every escape route

- **Pin CI/CD images to the latest Claude Code release**, not a version frozen at build time — as this repo has noted before, "latest" carries undisclosed and disclosed security fixes alike.
- **Don't disable auto-update on Claude Desktop** unless you have a process for checking `github.com/anthropics/claude-code/security/advisories` directly — this sweep's own finding is that these advisories under-surface in general security news coverage.

## Why this matters for vibe coders

This is the same lesson the Cursor GHSA index audit produced: **a vendor's own GitHub Security Advisories index is a primary source that general security-news queries routinely miss**, especially for CVEs that never get an independent researcher writeup or aggregator pickup. Seven fixed, unremarkable-looking advisories accumulate into a real gap in any tracker (including this one) that leans on search-engine discovery. If you maintain your own AI-tool inventory, add a periodic direct check of each tool's own advisory page — `github.com/<org>/<repo>/security/advisories` — to your process rather than relying solely on news aggregators or CVE feeds, which lag or skip vendor-only disclosures.

## Sources

- [GitHub — anthropics/claude-code Security Advisories index](https://github.com/anthropics/claude-code/security/advisories)
- [GitHub — Sandbox Escape via Git Worktree Path Confusion (GHSA-7835-87q9-rgvv, CVE-2026-55607)](https://github.com/anthropics/claude-code/security/advisories/GHSA-7835-87q9-rgvv)
- [NVD — CVE-2026-55607](https://nvd.nist.gov/vuln/detail/CVE-2026-55607)
- [GitHub — Out-of-Band Data Exfiltration via Pre-Approved HuggingFace Domain in WebFetch (GHSA-fg94-h982-f3mm, CVE-2026-54316)](https://github.com/anthropics/claude-code/security/advisories/GHSA-fg94-h982-f3mm)
- [GitHub — Local Privilege Escalation via Directory Junction in CoworkVMService (GHSA-5p5x-5294-qhp3, CVE-2026-44470)](https://github.com/anthropics/claude-code/security/advisories/GHSA-5p5x-5294-qhp3)
- [NVD — CVE-2026-44470](https://nvd.nist.gov/vuln/detail/CVE-2026-44470)
- [GitHub — SSH Host Key Verification Bypass Allows Man-in-the-Middle Attack on Remote Sessions (GHSA-3rwf-2g6p-c2f9, CVE-2026-44467)](https://github.com/anthropics/claude-code/security/advisories/GHSA-3rwf-2g6p-c2f9)
- [GitHub — Insecure Temporary File in /copy Command Enables Response Disclosure and Symlink-Based File Write (GHSA-4vp2-6q8c-pvq2, CVE-2026-46406)](https://github.com/anthropics/claude-code/security/advisories/GHSA-4vp2-6q8c-pvq2)
- [GitLab Advisory Database — CVE-2026-46406](https://advisories.gitlab.com/npm/@anthropic-ai/claude-code/CVE-2026-46406/)
- [GitHub — Trust Dialog Bypass via Git Worktree Spoofing Allows Arbitrary Code Execution (GHSA-q5hj-mxqh-vv77, CVE-2026-40068)](https://github.com/anthropics/claude-code/security/advisories/GHSA-q5hj-mxqh-vv77)
- [GitHub Advisory Database — CVE-2026-35020 (GHSA-jgg3-qqhf-7rx7)](https://github.com/advisories/GHSA-jgg3-qqhf-7rx7)
- [SentinelOne — CVE-2026-35020: Claude CLI OS Command Injection Vulnerability](https://www.sentinelone.com/vulnerability-database/cve-2026-35020/)
- [GitHub — Command Injection via Directory Change Bypasses Write Protection (GHSA-66q4-vfjg-2qhh, CVE-2026-25722)](https://github.com/anthropics/claude-code/security/advisories/GHSA-66q4-vfjg-2qhh)
