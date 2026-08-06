---
id: 2026-08-cursor-ghsa-november-batch
title: "Cursor's own GHSA page: 3 more patched advisories from November 2025 this repo hadn't tracked (CVE-2025-64106, -64107, -64108)"
date_disclosed: 2025-11-03
last_updated: 2026-08-06
severity: high
status: patched
ecosystems: [cursor]
tools_affected: [Cursor Desktop]
tags: [cve, ghsa, sensitive-file-protection, mcp-deeplink, ntfs, windows, prompt-injection]
---

## TL;DR
A direct page-walk of `github.com/cursor/cursor/security/advisories` — the same practice this repo has used to catch prior undertracked Cursor and Claude Code GHSA entries — found **three CVEs from a single November 2025 disclosure batch** that had never surfaced in this repo's aggregator-focused search rotation: a **Speedbump Modal Bypass** in Cursor's MCP deep-link install flow (CVE-2025-64106), and two variants of the same **sensitive-file-protection bypass on Windows** — one via backslash path obfuscation (CVE-2025-64107), one via NTFS path quirks (CVE-2025-64108). All three are CVSS **8.8 (high)**, all fixed in **Cursor 2.0**, and all predate this repo's other tracked Cursor CVE clusters (DuneSlide, open-folder-autorun, GhostApproval, git.exe-autoexec, the July sandbox-escape batch, DeepJack/CursorJack).

## What happened

### CVE-2025-64106 (GHSA-4575-fh42-7848) — Speedbump Modal Bypass in MCP deep-link install, CVSS 8.8
Cursor's `cursor://` MCP-install deeplink flow shows a "red alert" warning modal before installing an unfamiliar MCP server, intended to stop a user from unknowingly running an attacker-specified command. Insufficient input validation in the parsing logic that identifies "trusted" MCP servers (CWE-78, OS command injection class) let an attacker craft a deeplink that bypasses this warning entirely — a victim believing they're installing a well-known server (the advisory's own example: Playwright) instead silently runs the attacker's arbitrary command, with no visibility into what actually executed. Affected Cursor 1.7.28; fixed in **2.0**. Reported by researcher **yardenporat353**.

This is an earlier, structurally different bug from the same general attack surface as [DeepJack/CursorJack](2026-07-cursor-deepjack-cursorjack-deeplink-mcp.md) (which defeats a *later* fix, CVE-2025-54133, via dialog-truncation and nested-URI tricks rather than a trusted-server parsing bypass) — both show Cursor's MCP-install deeplink flow has needed multiple, independent rounds of fixing.

### CVE-2025-64107 (GHSA-2jr2-8wf5-v6pf) — sensitive-file bypass via Windows backslash paths, CVSS 8.8
Cursor's sensitive-file protection (the guardrail requiring explicit human approval before an agent overwrites certain editor/config files) correctly detected path-obfuscation attempts using forward slashes, but **not the equivalent technique using backslashes on Windows** — letting an attacker who already controls agent output (via prompt injection or a malicious model) overwrite protected files without triggering the approval prompt. Affected 1.7.52; fixed in **2.0**. Reported by researcher **Philts**. Must be chained with a prompt-injection or malicious-model foothold to reach exploitation — not independently exploitable from a clean session.

### CVE-2025-64108 (GHSA-6r98-6qcw-rxrw) — sensitive-file bypass via NTFS path quirks, CVSS 8.8
A related but distinct bypass of the same sensitive-file protection: NTFS-specific path syntax (short (8.3) path names and alternate data streams) let an attacker's already-injected agent overwrite protected files, because path normalization for these NTFS-specific forms happened **before** the security guardrail's own path check ran. Affected 1.7.44; fixed in **2.0**. Same reporter (**Philts**) as CVE-2025-64107, same chaining requirement (needs prompt injection or a malicious model as the entry point), same fix version.

All three were published on Cursor's own GitHub Security Advisories page on **2025-11-03** — nine months before this sweep found them via a direct index walk rather than search-engine queries, consistent with this repo's standing finding that vendor-only GHSA disclosures with no third-party aggregator pickup are systematically under-indexed by keyword search.

## Am I affected?
```bash
cursor --version   # or Cursor > About Cursor in the app
```
All three are fixed in **Cursor 2.0** and later — if you're on any version ≥ 2.0 (nearly certain if auto-update is on; Cursor is at 3.11+ as of this sweep), you are not exposed. If you're pinned to a pre-2.0 build for any reason, update immediately.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — never click an unfamiliar MCP-install deeplink regardless of what server name it claims to install; a warning modal's presence isn't proof it can't be bypassed.

## Why this matters for vibe coders
Two of these three bugs (CVE-2025-64107, CVE-2025-64108) are variations on the exact same theme — a security check that runs *before* platform-specific path normalization, so an attacker only needs to find one more OS-specific path quirk the check doesn't yet cover. Combined with this repo's other tracked Cursor sensitive-file and sandbox-escape clusters, the pattern holds: "sensitive file protection" and "sandbox" in Cursor are each a collection of individually-discovered, individually-patched edge cases rather than one structural guarantee — treat "patched" as "patched against the specific bypasses found so far."

## Sources
- [GitHub — Speedbump Modal Bypass in Cursor MCP Server Deep-Link (GHSA-4575-fh42-7848, CVE-2025-64106)](https://github.com/cursor/cursor/security/advisories/GHSA-4575-fh42-7848)
- [GitHub — Sensitive File Protection Bypass - Path Manipulation Using Backslashes on Windows (GHSA-2jr2-8wf5-v6pf, CVE-2025-64107)](https://github.com/cursor/cursor/security/advisories/GHSA-2jr2-8wf5-v6pf)
- [GitHub — Sensitive File Modification - NTFS Path Quirks (GHSA-6r98-6qcw-rxrw, CVE-2025-64108)](https://github.com/cursor/cursor/security/advisories/GHSA-6r98-6qcw-rxrw)
- [GitHub — cursor/cursor Security Advisories index](https://github.com/cursor/cursor/security/advisories)
