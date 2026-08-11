---
id: 2026-08-checkpoint-agent-framework-post-injection-cluster
title: "\"No Tools Required\" — Check Point finds a dozen framework-internals RCE/deserialization bugs across LangChain, CrewAI, Microsoft Agent Framework, and Google ADK; two detailed, most CVE numbers not yet public"
date_disclosed: 2026-08-05
last_updated: 2026-08-05
severity: high
status: unconfirmed
ecosystems: [pypi, npm, ai-agents]
tools_affected: [langchain, crewai, "Microsoft Agent Framework", "Google Agent Development Kit (ADK)", langgraph, autogen]
tags: [prompt-injection, deserialization, decorator-as-documentation, rce, ai-agent-framework, black-hat]
---

## TL;DR

At Black Hat USA 2026 (**2026-08-05**), Check Point researchers **Yarden Porat and Shahar Tal** presented **"No Tools Required: Post-Injection Exploitation Across AI Agent Frameworks,"** arguing that framework *internals* — memory stores, planning loops, serialization/deserialization layers, and orchestration logic — are the real attack surface once a prompt injection lands, not just the model's tool-calling permissions. Reported vulnerability counts and affected-framework lists **disagree between sources**: The Register reported **11 vulnerabilities across six frameworks** (LangChain, LangGraph, CrewAI, AutoGen, Microsoft Agent Framework, Google ADK); Check Point's own blog post says **12 CVEs across four frameworks** (LangChain, CrewAI, Microsoft Agent Framework, Google ADK). Neither source lists individual CVE numbers for the newly-disclosed bugs, and Check Point states the full technical write-up is still forthcoming on `research.checkpoint.com`. Two specific bugs have concrete detail: a **critical insecure-deserialization RCE in Microsoft Agent Framework** ($10,000 bounty, no CVE assigned because the framework wasn't yet generally available at discovery) and an **unauthenticated, HTTP-reachable Google ADK development assistant** allowing arbitrary file writes and code execution ($3,133.70 bounty; Google initially called it "not a bug," then shipped a partial fix). This repo already tracks three of the specific CVEs referenced in this cluster — the LangGraph checkpointer chain (CVE-2025-67644, CVE-2026-28277, CVE-2026-27022) — from the same researcher's earlier work; those are covered in [2026-06-langgraph-rce-chain.md](2026-06-langgraph-rce-chain.md), not repeated here.

## What happened

The talk's framing: prompt injection is a **delivery mechanism**, not the underlying bug — the actual security failure is that attacker-controlled content, once injected, is allowed to cross from the "data plane" (things the model reasons about) into a framework's own **trusted logic, memory, routing, and state-handling code**. Researcher Shahar Tal's own characterization: "Almost none of it was a completely new bug class... These are bugs that we learned to fix 20 years ago" — insecure deserialization, SSRF, path traversal, use-after-free, all showing up fresh inside AI-agent-framework internals because those code paths were never threat-modeled against hostile input the way a public API would be.

**Two bugs with concrete public detail:**

- **Microsoft Agent Framework — critical insecure-deserialization RCE.** Reported to carry a $10,000 bounty; Microsoft "released hardened protections." No CVE was issued for this specific finding because, per The Register's reporting, the framework was not yet generally available at the time of discovery — meaning there is no public advisory or version-range detail to check your own deployment against yet.
- **Google ADK — unauthenticated development assistant reachable over HTTP.** Google ADK ships a built-in development assistant that, per this research, was reachable over HTTP **without authentication** and allowed **arbitrary file writes and code execution**. Bounty: $3,133.70. Google's initial response reportedly classified this as **"not a bug"**; a partial fix has since shipped, and no CVE has been issued.

**Nine to ten additional findings are referenced only in aggregate** ("11 vulnerabilities," "12 CVEs") across LangChain, LangGraph, CrewAI, AutoGen, and (per The Register's list only) Microsoft Agent Framework and Google ADK again — with no individual CVE numbers, affected-version ranges, or per-bug technical detail published in either source reviewed for this advisory. Per this repo's accuracy standard, those remaining findings are **not itemized here** — doing so would mean inventing CVE numbers or version ranges that no source has actually stated. This advisory will be updated once Check Point's promised full technical write-up is published.

**Relationship to already-tracked LangGraph findings.** The same researcher, Yarden Porat, previously disclosed the LangGraph checkpointer RCE chain this repo already tracks in [2026-06-langgraph-rce-chain.md](2026-06-langgraph-rce-chain.md) (CVE-2025-67644 SQL injection in the SQLite checkpointer, chained with CVE-2026-28277 unsafe msgpack deserialization; CVE-2026-27022 covers a parallel Redis-checkpointer variant). It is likely — but not confirmed by either source reviewed here — that this Black Hat talk folds those already-disclosed CVEs into its "11/12 vulnerabilities" count alongside the newly-disclosed Microsoft Agent Framework and Google ADK bugs. Treat the LangGraph CVEs as already covered; do not double-count them against this advisory.

## Am I affected?

There is not yet enough public detail to give a concrete affected-version check for the Microsoft Agent Framework or Google ADK bugs specifically. General guidance:

```bash
# If you use Microsoft Agent Framework, confirm you're on a build that
# post-dates the "hardened protections" release referenced in this research
# (no version number has been published as of this writing — check Microsoft's
# own release notes directly)

# If you self-host Google ADK, check whether its built-in development
# assistant is reachable over the network without authentication
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:<adk-dev-assistant-port>/
```

## If you are affected

Given the lack of published version ranges or CVE numbers for the two newly-detailed bugs, the safest posture is:
1. Never expose an AI-agent framework's development/debug assistant to any network beyond localhost.
2. Treat framework-internal serialization/deserialization, memory stores, and checkpoint/state-persistence layers as untrusted-input boundaries — the same discipline already recommended for the LangGraph checkpointer chain.
3. Watch this advisory (and this repo's LangGraph entry) for updates once Check Point's full technical write-up publishes actual CVE numbers and version ranges.

→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- **Framework internals are a security boundary, not just a data pipeline.** Memory stores, planning-loop state, checkpoint/serialization layers, and orchestration routing all need the same hostile-input threat modeling as a public-facing API — this is the core lesson of this cluster.
- **Never bind a framework's debug/development assistant to a non-localhost interface**, and never assume "we didn't document this as a public API" is the same as "it's not reachable" — the Google ADK dev assistant was reachable over HTTP by default with no authentication.

## Sources

- [The Hacker News-adjacent / The Register — "Prompt injection isn't the bug, AI agent frameworks are"](https://www.theregister.com/security/2026/08/05/prompt-injection-isnt-the-bug-ai-agent-frameworks-are/5283585) — Black Hat talk summary, 11-vulnerability/six-framework count, Microsoft Agent Framework and Google ADK bounty/fix detail.
- [Check Point Research Blog — "Black Hat 2026: Check Point Research Takes the Stage"](https://blog.checkpoint.com/research/black-hat-2026-check-point-research-takes-the-stage) — Check Point's own summary, 12-CVE/four-framework count (discrepancy noted above), confirms full technical write-up is forthcoming on research.checkpoint.com.
- Cross-reference: [2026-06-langgraph-rce-chain.md](2026-06-langgraph-rce-chain.md) — the same researcher's earlier, already-tracked LangGraph checkpointer CVEs (CVE-2025-67644, CVE-2026-28277, CVE-2026-27022), likely folded into this talk's aggregate vulnerability count.
