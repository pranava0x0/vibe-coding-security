---
id: 2026-08-corebreak-agent-harness-tool-call-forgery
title: "CoreBreak — forged tool-call events bypass the model entirely across AWS Bedrock AgentCore, Google ADK, and Vercel AI SDK harnesses"
date_disclosed: 2026-07-10
last_updated: 2026-08-06
severity: critical
status: patched
ecosystems: [aws-bedrock-agentcore, google-adk, vercel-ai-sdk]
tools_affected: ["Amazon Bedrock AgentCore InvokeHarness API", "Google Agent Development Kit (ADK) for Python", "@ai-sdk/harness-codex", "@ai-sdk/harness-opencode"]
tags: [agent-framework, tool-call-forgery, authorization-bypass, confused-deputy, cve, black-hat]
---

## TL;DR
Researchers **Hedi Ingber and Aviyam Ivgi (Stealth)** presented **CoreBreak** at Black Hat USA 2026: a cross-vendor pattern where an agent runtime accepts a tool-call event that *looks* model-generated and executes the named tool **without the model ever actually deciding to call it** — no prompt injection, no guardrail to bypass, because the model is skipped entirely. The pattern recurred independently across three vendors' agent-harness products: **AWS Bedrock AgentCore's InvokeHarness API** (CVE-2026-18830, CVSS 8.6), **Google's Agent Development Kit for Python** (CVE-2026-18236, CVSS 9.3), and **Vercel AI SDK's `@ai-sdk/harness-codex` / `@ai-sdk/harness-opencode`** (CVE-2026-64650 / CVE-2026-64651, CVSS 6.3). All three are patched.

## What happened
Agent harnesses sit between a model's output and the tools it's allowed to invoke, translating a model-generated "call this tool with these arguments" event into an actual function call. CoreBreak's common finding: several of these harnesses did not verify **provenance** between "a message that looks like a tool-call event" and "a tool-call event the model actually produced" — if the runtime received data shaped like a model tool-call, it treated it as authoritative regardless of source. Because the bypass happens *before* the model is invoked (or by forging session history the model never actually saw), system prompts, content filters, and any model-level guardrail never get a chance to intervene.

**AWS Bedrock AgentCore — CVE-2026-18830 (CVSS 4.0: 8.6).** An authenticated remote caller could place a tool-use content block directly into the final message of an `InvokeHarness` request. The event loop dispatched the named tool immediately, without routing the decision through the model first. Affected the managed InvokeHarness API prior to **2026-07-31**; AWS shipped server-side validation that rejects caller-supplied tool-use blocks, applied automatically to the managed service with no customer action required.

**Google ADK for Python — CVE-2026-18236 (CVSS 4.0: 9.3, critical).** Two related paths, both in the tool-confirmation flow:
1. **Continuation forgery.** An attacker able to manipulate or inject events into an agent's session history could forge a tool-confirmation response — the framework did not verify that the target tool was actually registered to the executing agent, that the tool genuinely required confirmation, or that the confirmation's arguments matched the original tool-call event.
2. **Resumable-mode bypass.** User-authored events containing `function_call` parts could trigger registered-tool execution directly, again bypassing the model.

Affected ADK for Python **before 2.5.0**. Fixed in **2.5.0** (released 2026-07-16), which adds verification checks and rejects function calls appearing in user-authored messages; Google's own release notes confirm "prevent continuation forgery in tool confirmation" and "prevent model bypass in resumable mode by rejecting user-authored function calls" as shipped fixes, alongside unrelated hardening (artifact-service path validation, blocking dangerous stdlib modules in agent config).

**Vercel AI SDK — CVE-2026-64650 (`@ai-sdk/harness-codex`) / CVE-2026-64651 (`@ai-sdk/harness-opencode`), both CVSS 4.0: 6.3.** A different variant: the harness relay authorized a request if the calling process's command line contained the path of an approved helper script — a **process-identity check based on an inspectable string, not a cryptographic guarantee**. Malicious code already running inside the sandbox (a compromised dependency, a malicious build script, a poisoned lifecycle hook) could satisfy that check and invoke host-exposed tools — secret lookups, deployment operations, cloud API calls — without any corresponding model-authorized event. Exploitation required Linux, an active harness session with at least one host-provided tool, and untrusted code already executing inside the sandbox. Affected `@ai-sdk/harness-codex` through **1.0.28** and `@ai-sdk/harness-opencode` through **1.0.27**; fixed in **1.0.29** / **1.0.28** respectively, which removes the process-path fallback entirely and requires exact, short-lived, one-time authorization tied to an observed model event.

**Attack-condition differences across vendors, as characterized by the researchers:** AWS's path required only an authenticated remote request; Google's required either attacker-controlled session events or user-authored function calls; Vercel's required untrusted code already running inside the sandbox — a narrower bar, but one routinely met by a malicious dependency in the same supply-chain sense this repo tracks elsewhere.

This repo's existing coverage of AWS Bedrock AgentCore ([2026-07-aws-bedrock-agentcore-cve-cluster.md](2026-07-aws-bedrock-agentcore-cve-cluster.md)) tracks four *earlier* CVEs against the CLI, Python SDK, and Starter Toolkit — all argument-injection-class bugs in developer tooling. CVE-2026-18830 is a **fifth, distinct** CVE against the same product family, but a different component (the managed InvokeHarness API) and a different root-cause class (tool-call provenance, not argument injection) — see that advisory for the full AWS-specific CVE history.

## Am I affected?
```bash
# Google ADK for Python
pip show google-adk 2>/dev/null | grep -i version   # must be >= 2.5.0

# Vercel AI SDK harness packages
npm ls @ai-sdk/harness-codex @ai-sdk/harness-opencode 2>/dev/null
# harness-codex must be >= 1.0.29, harness-opencode must be >= 1.0.28

# Bedrock AgentCore InvokeHarness — managed service, already patched server-side
# as of 2026-07-31; no customer action required, but confirm you're not pinning
# an SDK version that predates the fix if you call InvokeHarness directly.
```

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — any tool a forged event could reach (secret lookups, deployment operations, cloud API calls) should be treated as potentially invoked outside the developer's intent until you've confirmed the patched version was in place throughout.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a sandbox boundary and a tool-authorization boundary are not the same thing; CoreBreak's Vercel variant shows code *already inside* a sandbox can still forge authorization to reach host tools if the authorization check itself is weak.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- Treat "the model decided to call this tool" as a claim that needs cryptographic or session-bound verification, not an assumption the runtime can infer from message shape or process command-line text.
- Keep agent-harness SDKs current — all three fixes here are opt-in only in the sense of "upgrade your pinned version"; the AWS fix was server-side and automatic, but Google's and Vercel's require a client-side version bump.

## Why this matters for vibe coders
CoreBreak is a distinct root-cause class from prompt injection, even though both land on "the agent did something the developer didn't intend." Prompt injection manipulates *what the model decides*; CoreBreak (and its siblings) manipulate *whether the model's decision is checked at all* before a tool runs — the same "the runtime received data shaped like an authoritative event and treated it as one" failure this repo already tracks under the "two parsers, one string" and "check-vs-effect scope disagreement" classes, here applied specifically to tool-call authorization in managed agent-harness products from three different major cloud/platform vendors. That it recurred independently at AWS, Google, and Vercel in the same disclosure round says the underlying assumption — "if it looks like a tool call, it came from the model" — was widespread across the current generation of agent-harness SDKs, not a one-vendor mistake.

## Sources
- [The Hacker News — AWS, Google, and Vercel Agent Flaws Let Attackers Trigger Tools Without Running the Model](https://thehackernews.com/2026/08/aws-google-and-vercel-patch-agent-flaws.html) — cross-vendor summary, CVE IDs, CVSS scores, patched versions, Black Hat USA 2026 presentation and researcher attribution (Hedi Ingber, Aviyam Ivgi, Stealth).
- [GitHub — google/adk-python v2.5.0 release notes](https://github.com/google/adk-python/releases/tag/v2.5.0) — primary vendor confirmation of the continuation-forgery and resumable-mode fixes shipped in this release.
- [THREATINT — CVE-2026-18830](https://cve.threatint.com/CVE/CVE-2026-18830) — CVE record confirming AWS Bedrock AgentCore InvokeHarness details, CVSS 8.6, affected-before-2026-07-31 scope.
- [THREATINT — CVE-2026-18236](https://cve.threatint.com/CVE/CVE-2026-18236) — CVE record confirming Google ADK continuation-forgery details, CVSS 9.3.
- [THREATINT — CVE-2026-64650](https://cve.threatint.com/CVE/CVE-2026-64650) — CVE record for `@ai-sdk/harness-codex`.
- [THREATINT — CVE-2026-64651](https://cve.threatint.com/CVE/CVE-2026-64651) — CVE record for `@ai-sdk/harness-opencode`.
