---
id: 2026-05-semantic-kernel-rce
title: "Microsoft Semantic Kernel — prompt injection to RCE (CVE-2026-25592, CVE-2026-26030, May 2026)"
date_disclosed: 2026-05-07
last_updated: 2026-05-18
severity: critical
status: patched
ecosystems: [pypi, dotnet, ai-agents]
tools_affected: [semantic-kernel-dotnet, semantic-kernel-python]
tags: [cve, prompt-injection, rce, sandbox-escape, microsoft, ai-agent-framework, kernelfunction]
---

## TL;DR
On **2026-05-07**, Microsoft disclosed two RCE flaws in **Semantic Kernel**, its open-source agent framework. **CVE-2026-25592** (.NET SDK, **CVSS 10.0**) — an internal `DownloadFileAsync` helper was accidentally tagged `[KernelFunction]`, exposing it to the LLM with an attacker-controlled `localFilePath`. A prompt-injected agent can stage arbitrary files on the host and **escape the Azure Container Apps Python sandbox**. **CVE-2026-26030** (Python SDK, **CVSS 9.9**) — the `InMemoryVectorStore` default filter built a Python lambda from user input and executed it with `eval()`; one crafted filter string → arbitrary code execution. Both came out of Microsoft's own "When prompts become shells" research. Patch to **.NET SDK 1.71.0** and **Python SDK 1.39.4**.

## What happened

### CVE-2026-25592 — `[KernelFunction]` exposure of `DownloadFileAsync` (.NET)
Microsoft's Semantic Kernel .NET SDK uses the `[KernelFunction]` attribute to mark methods the LLM is allowed to call as tools. Internal helper `DownloadFileAsync` was annotated with `[KernelFunction]` during development and **shipped with the attribute intact** — the LLM could invoke it. Its `localFilePath` parameter accepted any path with no validation. A prompt-injected agent could:

1. Call `DownloadFileAsync` with `localFilePath = /tmp/x.so` (or `C:\Windows\Temp\x.dll`) to drop a payload on the host.
2. Trigger that payload via any other tool the agent had (Python interpreter, shell function, file watcher).
3. Escape the **Azure Container Apps Python sandbox** that's the default for Semantic Kernel's auto-spun execution environment.

Microsoft's PoC: a single prompt launches `calc.exe` on the host running the agent. CVSS **10.0**.

### CVE-2026-26030 — `eval()` in `InMemoryVectorStore` filter (Python)
The Python SDK's `InMemoryVectorStore.search()` filter takes a string like `"city == 'Paris'"` and historically converted it to a Python lambda via `eval()`. Anywhere the filter string can be influenced by upstream data (RAG over user-controlled documents, vector search over agent-fetched content, etc.), `eval()` runs attacker code. CVSS **9.9**. Fixed by replacing `eval()` with a safe parser in 1.39.4.

Both vulnerabilities stem from the same architectural pattern Microsoft itself flagged: **treating an SDK annotation (`[KernelFunction]`, the filter parameter) as documentation rather than a security boundary**.

## Am I affected?

```bash
# Python
pip show semantic-kernel 2>/dev/null | grep -E '^(Name|Version):'
# Vulnerable: < 1.39.4

# .NET
dotnet list package | grep -i 'Microsoft.SemanticKernel'
# Vulnerable: < 1.71.0
```

Quick filter audit (Python):
```bash
# Any place you build an InMemoryVectorStore filter from user/RAG content
grep -rn 'InMemoryVectorStore\|\.search(.*filter' --include='*.py'
```

### IOCs

| Type | Value |
|---|---|
| CVE (.NET) | `CVE-2026-25592` (CVSS 10.0) |
| CVE (Python) | `CVE-2026-26030` (CVSS 9.9) |
| Vulnerable .NET versions | `Microsoft.SemanticKernel < 1.71.0` |
| Vulnerable Python versions | `semantic-kernel < 1.39.4` |
| Root cause (.NET) | `DownloadFileAsync` exposed via `[KernelFunction]`, unvalidated `localFilePath` |
| Root cause (Python) | `eval()`-based filter in `InMemoryVectorStore` |

## If you are affected
1. Upgrade now: `pip install --upgrade 'semantic-kernel>=1.39.4'` / `dotnet add package Microsoft.SemanticKernel --version 1.71.0`.
2. **Turn off `AutoInvokeKernelFunctions`** on any agent with disk, shell, or network reach until you've audited every exposed function for path validation and side-effect scope.
3. Audit your own `[KernelFunction]` annotations — any internal helper that wasn't supposed to be callable by the LLM is now one prompt injection away from RCE.
4. If you ran Semantic Kernel on Azure Container Apps and an agent was reachable from untrusted input (RAG over the web, chatbot, MCP-fed content) between Semantic Kernel's first vulnerable release and your patch date, treat container memory and any mounted secrets as compromised.
5. For Python: stop building filter strings from any data you don't fully trust. Use the new safe parser exclusively.

## Why this matters for vibe coders
Semantic Kernel is one of the three big agent SDKs (alongside LangChain and the Anthropic Agent SDK) sitting underneath many vibe-coded chatbots and back-end agent services. The class issue — **decorators-as-documentation** — repeats across every framework that lets the LLM choose which method to call. If you've written `@tool` / `@function_tool` / `[KernelFunction]` annotations and the function does anything irreversible, you're one prompt injection away from a bad day.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — same principles for tool exposure
→ Treat `[KernelFunction]` / `@tool` decorators as **security policy**. Audit before each release.
→ Default-deny untrusted input as an argument source for any function the LLM can call.
→ Never `eval()` LLM- or RAG-derived strings. Use parsers (ast, pydantic) with allowlists.

## Sources
- [Microsoft Security Blog — When prompts become shells: RCE vulnerabilities in AI agent frameworks](https://www.microsoft.com/en-us/security/blog/2026/05/07/prompts-become-shells-rce-vulnerabilities-ai-agent-frameworks/)
- [NVD — CVE-2026-25592](https://nvd.nist.gov/vuln/detail/CVE-2026-25592)
- [NVD — CVE-2026-26030](https://nvd.nist.gov/vuln/detail/cve-2026-26030)
- [Particula — Semantic Kernel CVE-2026-25592: How Prompt Injection Became RCE](https://particula.tech/blog/semantic-kernel-cve-2026-25592-prompt-injection-rce)
- [Nuka-AI — The Cracked Kernel: Semantic Kernel disclosure](https://nuka-ai.github.io/posts/2026-07-28-Semantic-Kernel-disclosure/)
- [Miggo — CVE-2026-25592: Semantic Kernel PythonPlugin RCE](https://www.miggo.io/vulnerability-database/cve/CVE-2026-25592)
- [GitLab Advisories — CVE-2026-26030: Semantic Kernel InMemoryVectorStore filter RCE](https://advisories.gitlab.com/pkg/pypi/semantic-kernel/CVE-2026-26030/)
- [Windows Forum — Semantic Kernel Prompt Injection Bugs Let Attackers Run Code or Write Files](https://windowsforum.com/threads/semantic-kernel-prompt-injection-bugs-let-attackers-run-code-or-write-files.416873/)
- [Vibe Graveyard — Semantic Kernel bugs turned prompt injection into remote code execution](https://vibegraveyard.ai/story/semantic-kernel-prompt-injection-rce/)
