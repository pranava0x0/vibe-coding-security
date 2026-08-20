---
id: 2026-08-viper-mcp-mass-audit-106-zerodays
title: "VIPER-MCP: automated audit of 39,884 MCP server repos finds 106 confirmed zero-days, 67 CVEs assigned"
date_disclosed: 2026-05-20
last_updated: 2026-08-20
severity: high
status: ongoing
ecosystems: [mcp]
tools_affected: [mcp-servers, model-context-protocol]
tags: [mcp, command-injection, taint-analysis, research, rce, systemic, academic]
---

## TL;DR

Academic researchers built **VIPER-MCP**, an automated auditing framework that scans MCP servers for taint-style vulnerabilities *and* proves exploitability by generating working natural-language attack prompts. Pointed at **39,884 real-world open-source MCP server repositories**, it found **106 zero-day vulnerabilities**, every one confirmed with an end-to-end exploit trace, with **67 CVE IDs assigned** so far. The takeaway for anyone wiring up MCP servers: the "just pass the model's argument to the shell" bug is not rare, and it is now being found at industrial scale by automation.

## What happened

The [VIPER-MCP paper](https://arxiv.org/abs/2605.21392) (arXiv:2605.21392, v1 2026-05-20, revised v2 **2026-08-12**) is described by its authors as the first end-to-end automated vulnerability-auditing framework for MCP servers that both detects taint-style flaws and **dynamically confirms exploitability** by producing concrete proof-of-concept prompts, rather than emitting unvalidated static alerts.

**The vulnerability class.** MCP servers expose privileged operations — shell execution, network access, file-system manipulation — to invocation by an agent acting on natural-language input. When a tool handler takes a model-supplied argument and passes it unsanitized into a shell, an HTTP request, or a file path, there is a direct path **from natural language to a security-sensitive sink**, yielding RCE or full system compromise. This is the same root cause behind the named MCP CVEs this repo already tracks in [advisories/2026-05-mcp-stdio-systemic-rce.md](2026-05-mcp-stdio-systemic-rce.md); VIPER-MCP's contribution is showing how *widespread* it is.

**How it works.** Two techniques: (1) a **two-pass static analysis** using CodeQL with an "anchor-query" pass that resolves file-level taint alerts to the specific MCP tool handler they belong to, producing vulnerability-anchored call chains rather than un-actionable file-level findings; and (2) a **feedback-driven prompt-evolution** loop with dual-mutator scheduling that corrects tool-selection drift and iteratively refines natural-language prompts toward the vulnerable sink, so the framework can demonstrate the exploit through the agent interface rather than by calling the handler directly.

**Results.** Against 39,884 repositories: **106 zero-days**, all confirmed by exploit trace, **67 CVEs assigned to date**, disclosed responsibly to affected developers with coordinated CVE assignment. Measured against two existing MCP security baselines, VIPER-MCP reports a **4.6% false-positive rate and 7.7% false-negative rate**. The paper's evaluation dataset comprises 130 vulnerable servers (the 67 CVE-assigned zero-days pinned at their exact vulnerable commits, plus 63 servers matching publicly disclosed 2025–2026 CVEs) against a manually audited benign set of 130.

**Context.** This lands alongside other measurements of the same surface: Censys counted **12,520 internet-exposed MCP services**, roughly 40% with no authentication at all, and Bitsight's TRACE team separately found ~1,000 exposed MCP servers with no authorization — figures already noted in this repo's [systemic MCP advisory](2026-05-mcp-stdio-systemic-rce.md). Independent secondary coverage of VIPER-MCP appears in [Adversa AI's MCP security roundup](https://adversa.ai/blog/top-mcp-security-resources-june-2026/).

**Why this is `ongoing` and not `patched`.** The 67 assigned CVEs are spread across dozens of small, independently maintained MCP server projects — there is no single vendor to ship a fix, and the paper does not claim the affected servers have all patched. A further 39 confirmed zero-days had no CVE assigned at publication. Assume the long tail of small MCP servers in your stack contains unfixed instances of this class.

## Am I affected?

There is no single package to check. Assess each MCP server you have configured:

```bash
# Enumerate configured MCP servers across the common agent config locations
cat ~/.claude/settings.json 2>/dev/null | grep -A5 -i mcp
cat ~/.cursor/mcp.json .cursor/mcp.json 2>/dev/null
cat ~/.codeium/windsurf/mcp_config.json 2>/dev/null
find . -maxdepth 3 -name 'mcp.json' -o -maxdepth 3 -name '.mcp.json' 2>/dev/null
```

For each server you run, particularly ones you installed from a small or unfamiliar repo, check the tool handlers for the pattern this research targets:

```bash
# Python MCP servers — model-supplied args reaching a shell
grep -rn -E 'subprocess\.(run|Popen|call).*shell=True|os\.system|os\.popen' <server-src>
# Node/TypeScript MCP servers
grep -rn -E 'child_process|exec\(|execSync\(|spawn\(.*shell' <server-src>
# Path handling — traversal into arbitrary file read/write
grep -rn -E 'open\(|readFile|writeFile|path\.join' <server-src>
```

A handler that takes a tool argument and reaches any of those without validation is the exact shape VIPER-MCP flags.

## If you are affected

1. **Remove or disable MCP servers you don't actively need** — every configured server is reachable by anything that can inject into your agent's context.
2. For servers you keep, prefer ones with a named maintainer, recent commits, and an issue tracker; the 106 findings skew toward quickly-written, functionality-focused implementations.
3. If a server you run has a CVE assigned, update it; if it is unmaintained, replace or fork-and-patch it.
4. See [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md).

## Prevention

- **Treat every MCP tool argument as attacker-controlled**, because it is — anything that can prompt-inject your agent controls those arguments. Validate against an allowlist; never interpolate into a shell.
- **Don't bind MCP HTTP transports to `0.0.0.0`, and require auth** — the Censys/Bitsight exposure counts above are what happens when the default is otherwise.
- **Prefer servers that propose rather than execute** (draft PRs, unsent emails, uncommitted changes) so a successful injection is reversible.
- See [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) and [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Sources

- [VIPER-MCP: Detecting and Exploiting Taint-Style Vulnerabilities in Model Context Protocol Servers — arXiv:2605.21392](https://arxiv.org/abs/2605.21392) — primary source: authors, methodology (two-pass anchor-query static analysis, feedback-driven prompt evolution), 39,884 repos scanned, 106 confirmed zero-days, 67 CVEs assigned, 4.6% FP / 7.7% FN rates, v2 revised 2026-08-12.
- [Top MCP security resources & CVEs — Adversa AI](https://adversa.ai/blog/top-mcp-security-resources-june-2026/) — independent secondary coverage placing the work alongside the Censys exposure counts and NSA/OWASP MCP guidance.
