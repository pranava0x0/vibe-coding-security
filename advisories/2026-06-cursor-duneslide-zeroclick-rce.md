---
id: 2026-06-cursor-duneslide-zeroclick-rce
title: "Cursor DuneSlide — two CVSS 9.8 zero-click prompt-injection-to-RCE flaws (CVE-2026-50548, CVE-2026-50549)"
date_disclosed: 2026-06-25
last_updated: 2026-07-02
severity: critical
status: patched
ecosystems: [cursor]
tools_affected: [cursor]
tags: [prompt-injection, sandbox-escape, rce, zero-click, mcp, ai-ide]
---

## TL;DR
Cato AI Labs disclosed **DuneSlide**: two CVSS 9.8 zero-click flaws in Cursor IDE (**CVE-2026-50548**, **CVE-2026-50549**) that let attacker-controlled content read by the agent — an MCP tool response or a poisoned web-search result — escape Cursor's sandbox and write files anywhere on disk, with **no user click or approval beyond the original benign prompt**. Both were fixed in **Cursor 3.0** (released 2026-04-02); the CVEs were assigned 2026-06-05 and publicly disclosed 2026-07-01.

## What happened
Cursor runs agent-issued terminal commands inside a sandbox that's supposed to confine writes to the current project. DuneSlide is two independent ways prompt-injected content defeats that boundary:

- **CVE-2026-50548** — Cursor's `run_terminal_cmd` tool accepts an optional `working_directory` parameter. When the agent sets it to a non-default path, Cursor adds that path to the sandbox's allowed-write list **without validating that it's actually inside the workspace**. Injected instructions (from an MCP response or a fetched web page) can point `working_directory` at a system path and have the agent overwrite the **sandbox helper binary itself** (on macOS: `/Applications/Cursor.app/Contents/Resources/app/resources/helpers/cursorsandbox`) — disabling the sandbox for every subsequent command in the session.
- **CVE-2026-50549** — before any file write, Cursor resolves symlinks/shortcuts on the target path to confirm the real destination is inside the project. When that resolution **fails** (target doesn't exist yet, or a folder in the path has had read access stripped), Cursor's fallback is to **trust the shortcut's unresolved in-project-looking path** instead of refusing the write — letting the resolved write land anywhere on disk.

Both are variants of the "two parsers, one string" class already tracked in this repo (a security check runs on one representation of a path while the actual write uses another) and both require **zero user interaction** beyond the developer's original, innocuous prompt — the attacker's payload rides in on content the agent reads on the developer's behalf (an MCP server's tool result, or a web-search hit the agent fetches).

Cato AI Labs (formerly Aim Security, credited for the related CVE-2025-54135) reported the issues 2026-02-19; Cursor shipped fixes in **version 3.0** on 2026-04-02, roughly six weeks before the CVEs were formally assigned (2026-06-05) and over four months before public disclosure (2026-07-01) — a long but ultimately coordinated disclosure timeline.

## Am I affected?
```bash
# Check your Cursor version — anything before 3.0 is vulnerable
cursor --version
```
If you're on Cursor < 3.0 and use MCP servers or let the agent browse/fetch web content, treat any session where the agent read untrusted MCP output or search results as a potential sandbox-escape window. Update to **Cursor ≥ 3.0** — both flaws are fixed there, so if you're current you're not exposed.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — don't treat an in-app sandbox as a hard boundary; a single path-validation gap anywhere in the chain (parameter handling, symlink resolution) can void it entirely.
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — MCP tool output and agent-fetched web content are both attacker-reachable surfaces; review which MCP servers your agent trusts.
→ Keep Cursor on auto-update; this is another case (see [Cursor open-folder autorun](2026-05-cursor-open-folder-autorun.md), [IDEsaster](2026-06-idessaster-ai-ide-cve-cluster.md)) where the fixed version shipped months before public disclosure.

## Sources
- [The Hacker News — Critical Cursor Flaws Could Let Prompt Injection Escape Sandbox and Run Commands](https://thehackernews.com/2026/07/critical-cursor-flaws-could-let-prompt.html)
- [NVD — CVE-2026-50548](https://nvd.nist.gov/vuln/detail/CVE-2026-50548)
- [NVD — CVE-2026-50549](https://nvd.nist.gov/vuln/detail/CVE-2026-50549)
- [Cybersecurity News — Critical Cursor IDE RCE Vulnerabilities Enable Prompt Injection in Zero-Click](https://cybersecuritynews.com/cursor-ide-rce-vulnerabilities/)
- [CSO Online — Sandbox bypass flaws in Cursor IDE highlight prompt injection as an RCE vector](https://www.csoonline.com/article/4191923/sandbox-bypass-flaws-in-cursor-ide-highlight-prompt-injection-as-an-rce-vector.html)
