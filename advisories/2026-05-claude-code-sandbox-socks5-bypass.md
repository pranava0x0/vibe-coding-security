---
id: 2026-05-claude-code-sandbox-socks5-bypass
title: "Claude Code network-sandbox SOCKS5 null-byte allowlist bypass (May 2026)"
date_disclosed: 2026-05-20
last_updated: 2026-05-21
severity: high
status: patched
ecosystems: [claude-code, anthropic]
tools_affected: [claude-code]
tags: [claude-code, sandbox-escape, allowlist-bypass, credential-theft, data-exfiltration, silent-patch]
---

## TL;DR
Claude Code's **network sandbox** (the allowlist that's supposed to confine the agent to, say, `*.google.com`) could be bypassed with a **SOCKS5 hostname null-byte injection**: a host like `attacker-host.com\x00.google.com` passes the allowlist matcher (it sees the trailing `.google.com`) but the OS truncates at the `\x00` and dials `attacker-host.com`. Every release from **v2.0.24** (sandbox GA, 2025-10-20) through **v2.1.89** was affected — ~130 versions over ~5.5 months. Anthropic **silently fixed it in v2.1.90 (2026-04-01)** with no changelog note, no CVE, and no advisory. Researcher **Aonan Guan** went public on **2026-05-20**; it's the **second** such sandbox bypass he's reported.

## What happened
Claude Code's sandbox lets users restrict the agent's egress to an allowlist of domains. The allowlist check ran a string match on the requested hostname, then handed the hostname to a **SOCKS5** proxy for the actual connection. The matcher and the OS resolver disagreed on where the hostname ended:

- **Allowlist matcher:** sees `attacker-host.com\x00.google.com`, notes it ends in `.google.com`, **approves**.
- **OS / SOCKS5 dial:** the C string terminates at the **null byte**, so it connects to **`attacker-host.com`**.

Any code Claude Code could be induced to run (via prompt injection in a repo, MCP-delivered content, etc.) could use this to **exfiltrate data straight past a user-configured allowlist** — AWS creds from `~/.aws/`, GitHub tokens from `~/.config/gh/`, environment variables, model API keys, internal/intranet API responses — all over **raw SOCKS5**, which also sidesteps standard HTTP egress logging.

The fix in **sandbox-runtime 0.0.43** (shipped with Claude Code **v2.1.90**, 2026-04-01) adds an `isValidHost()` wrapper that rejects `\x00`, `%`, CRLF, and other non-DNS characters **before** the allowlist matcher runs.

**The disclosure friction is the story:** Anthropic shipped the fix with **no CVE, no advisory, and no changelog note**, and didn't notify users who ran a wildcard allowlist during the 5.5-month window (Anthropic said its team had independently found and fixed it before Guan's report). This is the **second silently-patched** Claude Code sandbox bypass in ~5 months (the earlier one is tracked as **CVE-2025-66479**), continuing the quietly-shipped-fix cadence of the [source-map leak](2026-03-claude-code-source-map-leak.md) era.

## Am I affected?
You were exposed if you relied on Claude Code's network allowlist as a security boundary on **any version from v2.0.24 through v2.1.89**, especially with a **wildcard / broad allowlist**.

```bash
# What version are you on? (≥ 2.1.90 is fixed)
claude --version 2>/dev/null

# Check the bundled sandbox-runtime (≥ 0.0.43 contains the isValidHost() fix)
grep -RIn '"version"' ~/.claude 2>/dev/null | grep -i sandbox

# If you keep them, scan agent/proxy logs for null-byte or odd hostnames around your usage window
grep -RIal $'\x00' ~/.claude/**/*.log 2>/dev/null
```

If you used the sandbox as a containment boundary on a vulnerable version while running untrusted repos or MCP content, **treat any credential that was reachable from those sessions as potentially exfiltrated** and rotate.

### IOCs / version data

| Type | Value |
|---|---|
| Mechanism | SOCKS5 hostname **null-byte (`\x00`) injection** past the allowlist matcher |
| Affected | Claude Code **v2.0.24 → v2.1.89** (~130 versions, sandbox GA 2025-10-20) |
| Fixed | Claude Code **v2.1.90** (2026-04-01), `sandbox-runtime` **0.0.43** (`isValidHost()`) |
| CVE | **None assigned** (silent fix; researcher tracks the prior bypass as CVE-2025-66479) |
| Researcher | Aonan Guan (oddguan.com) — public 2026-05-20 |
| Exfil surface | AWS/GitHub creds, env vars, API keys, intranet responses over raw SOCKS5 |

## If you are affected
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — and don't treat an in-tool allowlist as your *only* egress control. Enforce egress at the OS/network layer (firewall, proxy with its own validation) so a single in-app parsing bug isn't the whole boundary.
→ Upgrade Claude Code promptly and keep auto-update on; because Anthropic ships some security fixes silently, **assume "latest" carries undisclosed fixes** and don't pin old versions for long. See the [Claude Code InversePrompt / May-2026 cluster](2025-08-claude-code-inverseprompt.md) and [deeplink RCE](2026-05-claude-code-deeplink-rce.md).

## Sources
- [The Register — Even Claude agrees: hole in its sandbox was real and dangerous](https://www.theregister.com/security/2026/05/20/even-claude-agrees-hole-in-its-sandbox-was-real-and-dangerous/)
- [SecurityWeek — Anthropic Silently Patches Claude Code Sandbox Bypass](https://www.securityweek.com/anthropic-silently-patches-claude-code-sandbox-bypass/)
- [Aonan Guan — Second Time, Same Sandbox: Another Anthropic Claude Code Network Sandbox Bypass Enables Data Exfiltration](https://oddguan.com/blog/second-time-same-sandbox-anthropic-claude-code-network-allowlist-bypass-data-exfiltration/)
- [Aonan Guan — CVE-2025-66479: Anthropic's Silent Fix and the CVE That Claude Code Never Got](https://oddguan.com/blog/anthropic-sandbox-cve-2025-66479/)
- [Cybersecurity News — Claude Code's Network Sandbox Vulnerability Exposes User Credentials and Source Code](https://cybersecuritynews.com/claude-codes-network-sandbox-vulnerability/)
- [Cyberpress — Claude Code Sandbox Flaw Exposes Credentials and Source Code](https://cyberpress.org/claude-code-sandbox-flaw/)
