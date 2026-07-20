---
id: 2026-07-memghost-ai-agent-memory-poisoning
title: "MemGhost — a single malicious email plants persistent false memories in AI agents (research, OpenClaw + Claude Code SDK agents)"
date_disclosed: 2026-07-13
last_updated: 2026-07-20
severity: high
status: active
ecosystems: [ai-agents, openclaw, claude-code-sdk, mem0]
tools_affected: [openclaw, claude-code-sdk-agents, mem0, vector-memory-stores]
tags: [prompt-injection, memory-poisoning, persistence, ai-agent, research, email, indirect-prompt-injection]
---

## TL;DR
Researchers disclosed **MemGhost**: a single crafted email, read by an AI agent with email access and memory-write tools, silently plants a **false, persistent fact** into the agent's long-term memory — with no mention of the write in the agent's visible reply. Once planted, the false memory loads on every future session and quietly steers the agent's behavior (the paper's worked example: convincing the agent the user's Zelle daily transfer limit had been raised to $10,000). Tested against **OpenClaw** (87.5% success rate) and a **Claude Code SDK-based agent** (71.4% success rate) in background/autonomous mode, plus two other unnamed frameworks — both structured-file memory (`AGENTS.md`/`MEMORY.md`-style) and vector-database memory (e.g., Mem0) are vulnerable. No CVE; OpenClaw's security team says the behavior doesn't cross an existing tool-policy/sandbox boundary, so it doesn't qualify as in-scope under their current disclosure policy.

## What happened
A paper titled **"When Claws Remember but Do Not Tell: Stealthy Memory Injection in Persistent Personal Agents"** (arXiv:2607.05189), led by researcher Yechao Zhang, was published 2026-07-06 and picked up widely starting 2026-07-13.

### Attack mechanism
Any AI agent that (a) can read untrusted incoming email and (b) has a tool that writes to its own persistent memory is vulnerable. The attack:
1. An attacker sends an email containing text addressed to the *agent*, not the human recipient — instructing it to record a specific "fact" about the user into memory.
2. If the agent's email-processing step engages with the payload, it uses its **own memory-write tool** to record the false fact — no external write, no privilege escalation, just the agent doing what it was (indirectly) told.
3. The agent's **visible reply says nothing about the memory write** — the action happens silently, off-screen from anything a user would normally review.
4. On every subsequent session, the poisoned memory file or vector-store entry loads automatically and biases the agent's future answers and decisions, including — per the paper's test cases — auto-approving requests that a correctly-informed agent would flag (raised transfer limits, a re-classified "trusted" contact, medical misinformation).

### Scope
Researchers built **MemGhost**, an automated payload generator (trained offline via reinforcement learning) that crafts emails maximizing both injection success and reply-silence, and **WhisperBench**, a 108-case benchmark spanning financial-fraud, medical-misinformation, and security-sabotage scenarios. The vulnerability is **architecture-agnostic**: it doesn't matter whether an agent stores memory as plain files (`AGENTS.md`/`MEMORY.md` in OpenClaw) or in a vector database like Mem0 — any agent that writes what it "learns" to persistent storage without provenance tracking or a confirmation step is exposed.

Success rates in background/autonomous mode: **OpenClaw on GPT-5.4 — 87.5%**; **Claude Code SDK agent on Sonnet 4.6 — 71.4%**; two further (unnamed) frameworks tested above 80%.

### Vendor response
OpenClaw's security team was notified 2026-07-14. Their position: prompt injection is treated as out-of-scope for their disclosure program **unless it crosses an authorization, tool-policy, approval, or sandbox boundary** — and MemGhost doesn't, since it only uses the agent's own already-granted memory-write tool. OpenClaw's suggested mitigation is architectural: route untrusted email through a **separate reader agent stripped of memory, file, and shell tools**, so nothing that reads attacker-controlled content can also write to persistent state. They say they're evaluating memory-write controls (provenance tracking, audit logs, confirmation prompts) but have not committed to a fix. OpenClaw also questioned the paper's model choice (GPT-5.4 rather than Anthropic's Opus 4.6).

### Real-world confirmation (2026-07-16)
Lead author Zhang reported follow-up tests using **real Gmail accounts connected to OpenClaw via OAuth and the Gmail API** (rather than a synthetic test harness): "more than half the cases still ended with the payload written into persistent memory, with no explicit notice or confirmation to the user," though some payload variants were filtered to spam as expected.

## Am I affected?
You're exposed if you run any AI agent — OpenClaw, a Claude Code SDK-based custom agent, or similar — that:
- Has read access to an email inbox (directly or via an MCP/connector integration), **and**
- Has a tool that writes to a persistent memory file or vector store the agent reloads on future sessions.

```bash
# OpenClaw: inspect memory files for content you don't recognize authoring
cat ~/.openclaw/AGENTS.md ~/.openclaw/MEMORY.md 2>/dev/null

# Check memory-file modification times against your own session history —
# an edit timestamp with no corresponding chat session is a red flag
ls -la ~/.openclaw/*.md 2>/dev/null

# For vector-store memory (e.g. Mem0), audit recent inserts for anomalous
# "facts" you never told the agent yourself, especially anything touching
# trust relationships, spending/transfer limits, or approval policies
```

There is no automated signature for this — the only reliable check today is manually reading your agent's memory contents and asking "did I actually say this, or did the agent infer it from something it read?"

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
1. Review all persistent memory content for facts you didn't explicitly state to the agent yourself.
2. Purge or reset agent memory if you find content you can't attribute to a real conversation, especially anything about trust levels, spending limits, or approval rules.
3. Check whether any agent actions (approvals, transfers, tool calls) were taken on the basis of a memory entry you didn't create.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
- **Don't let one agent both read untrusted content (email, web pages, MCP tool output) and write to persistent memory.** OpenClaw's own recommended mitigation — a separate reader agent with memory/file/shell tools stripped out — is the general pattern: split trust domains the same way you would for the "connector-chaining lethal trifecta" (reader connector piped into an executor connector).
- If your agent framework supports it, require an explicit confirmation step before any memory write that wasn't directly dictated by the user in the current session.
- Periodically audit persistent memory content the same way you'd audit a `.cursorrules`/`CLAUDE.md`/`AGENTS.md` file for planted instructions — memory files are a write-target, not just a read-target, and this is the same class of risk this repo already tracks for AI-agent config files (TrapDoor, Miasma Wave 5), just applied to the agent's own memory store instead of a repo file.

## Sources
- [arXiv 2607.05189 — When Claws Remember but Do Not Tell: Stealthy Memory Injection in Persistent Personal Agents](https://arxiv.org/html/2607.05189) — primary research paper, MemGhost generator, WhisperBench benchmark, success-rate data.
- [The Hacker News — New MemGhost Attack Plants Persistent False Memories in AI Agents Through One Email](https://thehackernews.com/2026/07/new-memghost-attack-plants-persistent.html) — independent coverage, OpenClaw vendor-response details, real-Gmail follow-up test results.
