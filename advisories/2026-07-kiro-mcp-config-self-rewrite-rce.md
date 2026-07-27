---
id: 2026-07-kiro-mcp-config-self-rewrite-rce
title: "AWS Kiro IDE — prompt injection lets the agent rewrite its own MCP config, achieving RCE (CVE-2026-10591, patched v0.11.130)"
date_disclosed: 2026-02-11
last_updated: 2026-07-27
severity: high
status: patched
ecosystems: [kiro, mcp, aws]
tools_affected: [kiro (aws agentic ide)]
tags: [cve, prompt-injection, mcp, self-rewrite, workspace-config-auto-execute, aws]
---

## TL;DR
Researchers **Nicole Fishbein and Eran Segal (Kodem Security)** found that AWS's agentic IDE **Kiro** let its own AI agent rewrite `~/.kiro/settings/mcp.json` — the file that decides which MCP servers Kiro will load and execute — with no user review. A web page with hidden (white-on-white) instructions was enough: a developer asks Kiro to fetch/summarize the page, Kiro reads the injected instructions, and writes a malicious MCP server entry into its own config, which reloads automatically and runs attacker code. Reported via HackerOne on **2026-02-11**; AWS confirmed a fix deployed by **2026-04-03** and assigned **CVE-2026-10591** with a formal security bulletin on **2026-07-22**, four-plus months after the fix shipped. Patched in **Kiro v0.11.130**.

## What happened
Kiro (AWS's agentic IDE, part of the same "AI coding tool auto-executes workspace config" cluster this repo has tracked across Claude Code, Cursor, Windsurf, Amazon Q Developer, and the multi-tool TrustFall disclosure) stores its Model Context Protocol server configuration in `~/.kiro/settings/mcp.json`. Kodem Security found that Kiro's own file-write tool could modify this file without any approval gate — meaning **the AI agent could edit the exact file that governs what code it is allowed to execute**, collapsing the config into something the agent could rewrite on its own initiative rather than only the user ([Intezer's technical summary of the finding](https://research.intezer.com/blog/2026/07/remote-code-execution-kiro/)).

The proof-of-concept chain:
1. An attacker hosts a page containing hidden instructions (rendered in white text on a white background, invisible to the human reader but present in the page's text content).
2. A developer asks Kiro to fetch and summarize the page — an entirely ordinary request.
3. The developer approves the fetch itself (the only approval step in the whole chain).
4. Kiro's model processes the hidden instructions embedded in the fetched content and, without any further approval, writes a new MCP server entry into `~/.kiro/settings/mcp.json`.
5. Kiro reloads its MCP configuration automatically, launching the attacker-specified server and executing its code.

Kodem's PoC demonstrated exfiltration of the victim's hostname, username, and platform information via callbacks to an external server — a conservative demonstration of a chain that could just as easily deliver a full payload.

AWS's own security bulletin describes the underlying flaw more broadly than just this one config file: "insufficient access control restrictions in the file write tool in Kiro IDE... might allow remote unauthenticated actors to execute arbitrary commands via crafted instructions that cause writes to execution-sensitive paths (such as `.vscode/tasks.json`)" ([AWS Security Bulletin 2026-037-AWS](https://aws.amazon.com/security/security-bulletins/2026-037-aws/)). That means the file-write tool's insufficient path restriction is the actual root cause, and `mcp.json` (Kodem's PoC) and `.vscode/tasks.json` (a separate PoC by Cymulate Research Labs, already covered in this repo's [Cursor git.exe advisory](2026-07-cursor-git-exe-autoexec.md)) are two independent, concrete instances of the same underlying bug reaching different execution-sensitive files.

**Correction to this repo's prior coverage:** the [Cursor git.exe advisory](2026-07-cursor-git-exe-autoexec.md) previously cited CVE-2026-10591 only in passing and attributed it solely to "Cymulate research." That attribution was incomplete — Kodem Security's HackerOne report (2026-02-11) predates and is independent of Cymulate's `.vscode/tasks.json` PoC, and targets a different file (`mcp.json`, not `tasks.json`). Both are real, both are folded into the same CVE and the same AWS fix.

**Disclosure timeline:**
- **2026-02-11** — Kodem Security reports the finding to AWS via HackerOne.
- **2026-04-03** — AWS confirms patches deployed (Kiro v0.11.130).
- **2026-07-22** — AWS formally assigns **CVE-2026-10591** and publishes Security Bulletin 2026-037-AWS, more than three months after the fix had already shipped.

## Am I affected?
Check your Kiro version:
```bash
kiro --version
```
Anything below **v0.11.130** is vulnerable. If you use Kiro and have ever asked it to fetch or summarize a web page, check `~/.kiro/settings/mcp.json` for any MCP server entry you don't recognize:
```bash
cat ~/.kiro/settings/mcp.json
```
An unfamiliar `command` or `args` entry pointing outside your normal toolchain is a sign the agent's config was rewritten without your knowledge.

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — treat any MCP config file as a privileged, security-relevant file; diff it after every AI-tool session, not just after `git pull`.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — don't let an agent fetch untrusted web content in the same session/profile that holds live cloud or SSH credentials.

## Why this matters for vibe coders
This is another entry in this repo's **"AI coding tool auto-executes workspace config"** class (siblings: [Claude Code `postStart` hooks](2025-08-claude-code-inverseprompt.md), [Amazon Q `.amazonq/mcp.json`](2026-06-amazon-q-mcp-workspace-rce.md), [TrustFall's five-CLI MCP auto-execute](2026-05-trustfall-mcp-auto-execute.md)) — except here the write path isn't a config file the developer edited, it's a file **the agent itself can write to**, which means the trust boundary depends entirely on whether the agent's own file-write tool is gated. A single "summarize this page" request, on an unpatched Kiro, was enough to have the agent quietly edit the one file that decides what it's allowed to run next. The four-plus-month gap between AWS confirming a fix (April) and actually publishing a CVE/bulletin (July) is also its own lesson: a vendor's silent "we already fixed it" is not the same as a public record a downstream auditor or SOC can search for — treat "no CVE yet" as "not yet triaged," not "not real," consistent with this repo's standing caution on silently-patched findings.

## Sources
- [Intezer — CVE-2026-10591: Kiro MCP Configuration Vulnerability](https://research.intezer.com/blog/2026/07/remote-code-execution-kiro/) — technical summary of Kodem Security's finding, PoC mechanics, disclosure timeline, researcher attribution.
- [AWS Security Bulletin 2026-037-AWS](https://aws.amazon.com/security/security-bulletins/2026-037-aws/) — official vendor advisory, CVE-2026-10591, affected/patched versions, root-cause description covering both `mcp.json` and `.vscode/tasks.json` instances.
