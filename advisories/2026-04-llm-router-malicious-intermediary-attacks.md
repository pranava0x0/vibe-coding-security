---
id: 2026-04-llm-router-malicious-intermediary-attacks
title: "Third-party LLM API routers caught injecting malicious tool calls and harvesting credentials (UC research, Apr 2026)"
date_disclosed: 2026-04-09
last_updated: 2026-09-08
severity: high
status: unconfirmed
ecosystems: [ai-agents, llm-routers, openrouter-class-services]
tools_affected: ["Third-party LLM API routers/aggregators (paid and free)", "Any AI coding agent configured to route model calls through one, incl. Claude Code"]
tags: [llm-router, man-in-the-middle, tool-call-injection, credential-theft, secret-exfiltration, research, arxiv, crypto-wallet]
---

## TL;DR
A University of California research team (paper: *"Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain,"* arXiv:2604.08407) tested 28 paid and 400 free third-party LLM API routers — services that sit between an AI agent and providers like OpenAI, Anthropic, and Google, terminating TLS and getting full plaintext access to every request and response. Of those, 9 routers (1 paid, 8 free) were caught actively injecting malicious tool calls into model responses, 2 used adaptive triggers to evade detection during testing, 17 accessed researcher-planted AWS canary credentials, and 1 drained a researcher-funded canary Ethereum wallet. **Status is `unconfirmed`**: this is a single research group's measurement study (no independent replication found), and this repo could not confirm the primary paper's own dollar figure for the wallet drain — several outlets reported it as a $500,000 theft, but a source that read the paper directly described the seeded funds as "nominal" and losses as under $50; see the discrepancy note below.

## What happened
AI coding agents and other LLM-based tools increasingly route model calls through third-party "router" or "aggregator" services rather than calling OpenAI/Anthropic/Google APIs directly — for cost arbitrage, unified billing, or access to models a developer's account doesn't otherwise have. Because these routers act as a TLS-terminating proxy, they see every prompt, every tool-call request, and every model response in plaintext, and no provider currently enforces end-to-end cryptographic integrity between the client and the upstream model that would let a client detect tampering in transit.

The researchers formalized two attack classes a malicious or compromised router can carry out: **payload injection (AC-1)** — altering or fabricating tool-call instructions in a model's response so the client executes commands the model never actually generated — and **secret exfiltration (AC-2)** — silently copying credentials, API keys, or other sensitive data that pass through the router. Two adaptive-evasion variants were also observed: dependency-targeted injection (only firing when a specific library/tool is in play) and conditional delivery (only firing under conditions designed to dodge test/audit traffic).

Testing 28 paid routers (sourced from Taobao, Xianyu, and Shopify storefronts) and 400 free routers (from public community lists), the team found: **1 paid and 8 free routers** actively injecting malicious tool calls; **2 routers** using adaptive evasion triggers; **17 routers** that accessed AWS credentials the researchers had planted as canaries; and **1 router** that drained funds from a canary Ethereum private key the researchers had seeded specifically to test for this behavior.

**Accuracy note — unresolved figure discrepancy.** Multiple outlets (Cointelegraph, CCN, ChainCatcher, PANews) headlined the wallet-drain finding as a "$500,000" theft. A separate outlet that read the paper directly (CoinDesk) instead described the seeded wallet as carrying a "nominal balance" with reported losses "below $50." The arXiv abstract page itself states only that one router drained the canary wallet, without a dollar figure. This repo could not resolve which figure is correct from primary-source text alone — treat the "$500,000" figure as unverified sensationalism pending a direct reading of the paper's full text, and treat the CoinDesk figure as the better-sourced (if still secondhand) number. This is the same "search-result summary blends multiple pages" failure mode this repo has flagged before; it is being logged explicitly rather than repeating the larger, more dramatic number.

**Why this matters for AI coding agents specifically:** a developer using an agent like Claude Code, Cursor, or any OpenAI-SDK-compatible client configured to point at a third-party router — commonly done to access additional models or reduce cost — routes every tool call (including shell commands, file writes, and any secrets referenced in agent context) through that intermediary. The researchers specifically name AI coding agents working on smart-contract or wallet code as a realistic target class, since a malicious router sitting in that path could inject a tool call that exfiltrates a private key or seed phrase the agent has in context.

## Am I affected?
You are potentially exposed if you (or a team member) configured an AI coding agent, IDE plugin, or SDK to use a third-party LLM router/aggregator rather than calling the model provider (OpenAI, Anthropic, Google) directly.

```bash
# Check for router/aggregator base URLs in common agent configs
grep -rEi 'openrouter|api\.together|api\..*proxy|base_url.*http' ~/.config ~/.claude ~/.cursor .env* 2>/dev/null

# Review any environment variables that redirect an SDK's base API URL
env | grep -Ei 'OPENAI_BASE_URL|ANTHROPIC_BASE_URL|API_BASE'
```
Pay particular attention if you have ever pasted a private key, seed phrase, or long-lived cloud credential into a session routed through a non-default (non-vendor) API endpoint.

## If you are affected
1. If an agent session touching sensitive credentials (cloud keys, private keys, seed phrases) was ever routed through a third-party LLM router, treat those credentials as potentially exposed and rotate them.
2. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
3. Prefer calling model providers directly, or a router from a vendor with a published security/privacy commitment (no-logging, no request modification) that you have reviewed — this research found the risk concentrated far more heavily in unvetted free routers (8 of 400) than paid ones (1 of 28), but neither category was risk-free.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — never place a long-lived private key or seed phrase directly in an agent's working context, routed or not; use ephemeral, scoped credentials for any agent session that touches funds.
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a router that can inject tool calls is functionally equivalent to a compromised MCP server in blast radius; apply the same least-privilege tool-access principle regardless of which layer is untrusted.

## Sources
- [arXiv 2604.08407 — Your Agent Is Mine: Measuring Malicious Intermediary Attacks on the LLM Supply Chain](https://arxiv.org/abs/2604.08407) — primary research paper (UC researchers incl. Hanzhi Liu, Chaofan Shou), submitted 2026-04-09; router counts, attack-class taxonomy.
- [CoinDesk — As AI agents scale in crypto, researchers warn of a critical security gap](https://www.coindesk.com/tech/2026/04/13/ai-agents-are-set-to-power-crypto-payments-but-a-hidden-flaw-could-expose-wallets) — independent secondary coverage; describes the canary wallet as carrying a nominal balance with losses reported under $50.
- [Cointelegraph — AI Routers Can Steal Credentials and Crypto](https://cointelegraph.com/news/researchers-discover-malicious-ai-agent-routers-that-can-steal-crypto) — independent secondary coverage; reports the disputed "$500,000" wallet-drain figure not corroborated by the primary source's own abstract text.
