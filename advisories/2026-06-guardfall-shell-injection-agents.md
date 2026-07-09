---
id: 2026-06-guardfall-shell-injection-agents
title: "GuardFall — shell-injection design flaw breaks command guards in 10 of 11 open-source AI coding agents (June 2026)"
date_disclosed: 2026-06-30
last_updated: 2026-06-30
severity: high
status: active
ecosystems: [aider, opencode, cline, agent-frameworks]
tools_affected: [aider, OpenHands, SWE-agent, cline, opencode, block/goose, RooCodeInc/Roo-Code, plandex-ai/plandex, Open-Interpreter, NousResearch/hermes-agent]
tags: [shell-injection, command-guard-bypass, sandbox-escape, agent-orchestration, design-flaw, no-cve]
---

## TL;DR

Adversa AI researcher Omer Ben Simon disclosed **GuardFall**: a class of shell-injection bypasses that defeats the pattern-matching "safety filters" most open-source AI coding agents use to block dangerous shell commands. **10 of 11 surveyed agents — including Aider, OpenHands, and SWE-agent, three frameworks this repo tracks by name — are bypassable**; only **Continue** correctly closes the gap with a tokenize-and-canonicalize evaluator. No CVE applies: the researchers frame it as a structural design convention ("agent → shell, gated by string matching") rather than a single patchable bug, so there is **no vendor patch to wait for**.

## What happened

Published **2026-06-30**, GuardFall's root cause is a mismatch between how a guard inspects a command and how bash actually executes it: **the guard reads raw text; bash expands, unquotes, and rewrites that text before running it.** A filter that blocks the literal string `rm` does nothing against `r''m` (bash strips the empty quote pair) or `rm$IFS-rf$IFS/` (word-splitting via `$IFS` reconstructs the flags after the filter has already passed the string).

Five documented bypass classes:

| Class | Technique | Example |
|---|---|---|
| A — Quote removal | Bash strips quote pairs before matching | `r''m file` |
| B — `$IFS` expansion | Word-splitting rebuilds blocked flags | `rm$IFS-rf$IFS/` |
| C — Command substitution | Binary name hidden in `$(...)` | `$(echo rm) -rf /` |
| D — Base64 piping | Benign-looking commands compose into a destructive pipeline | `echo <b64> \| base64 -d \| sh` |
| E — Alternative destructive flags | Flag-focused blocklists miss non-`rm` destruction | `find /x -delete`, `dd of=/dev/sda` |

Adversa AI tested 11 popular open-source agents and grouped the failures into four modes:

1. **Regex over raw string** (Hermes, opencode, Goose) — no defense against any bash expansion.
2. **Tokenized but raw-text matching** (Cline, Roo-Code) — closes Classes A–B, still fails C and E.
3. **No static guard, relies on human approval** (Aider, Plandex, Open Interpreter) — protection disappears the moment an auto-execute/auto-approve flag is set.
4. **Sandbox-only with a documented local opt-out** (OpenHands, SWE-agent) — container isolation works until the tool's own documented local/no-sandbox mode is enabled.

**Continue** was the sole tool that held up, using a five-stage evaluator: tokenize with shell-quote semantics, detect variable expansion, recursively evaluate substitutions, check pipe destinations for interpreters, and match an explicit disabled-command list — closing all five bypass classes in combination.

**Why this matters for vibe coders:** any of the 10 affected agents running in an unattended/CI context — auto-merge bots, autonomous coding loops, agents processing fork pull requests or third-party dependency files — is exposed to prompt-injected or otherwise attacker-controlled input that looks harmless to the guard but is destructive once bash gets hold of it. The affected agents collectively represent roughly **548,000 combined GitHub stars**.

## Am I affected?

You're in scope if you run any of: **Aider, OpenHands, SWE-agent, Cline, opencode, Goose, Roo-Code, Plandex, Open Interpreter, or Hermes** — especially with auto-execution/auto-approve enabled, or in a CI/CD pipeline that lets the agent process untrusted content (fork PRs, fetched web content, third-party files).

Quick self-test — try feeding the agent a prompt that asks it to run:
```
r''m -rf /tmp/guardfall-test-marker
```
and confirm your command guard (if any) actually blocks it. If your setup only pattern-matches the literal string `rm`, you're exposed.

## If you are affected

- **Disable all auto-execution/auto-approve flags** for these agents until you've applied mitigations — require human review of every shell command.
- **Disable agent execution on fork pull requests** in CI; never let an agent process untrusted PR content with shell access enabled.
- **Redirect `$HOME`** for agent sessions to a scoped directory (`HOME=$HOME/.agent-sandbox-$RANDOM agent …`) to limit blast radius if a bypass succeeds.
- **Audit agent config files** (`.aider.conf.yml` and equivalents) for auto-run settings.

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- **Don't trust regex/string-matching command guards as a security boundary.** If your agent's guard doesn't tokenize with shell-quote semantics, evaluate `$IFS`/variable expansion, and recursively resolve command substitution, it is not a security control — treat it as an operational nicety only.
- **Prefer a tokenize-and-canonicalize evaluator** (Continue's reference design) or real OS-level sandboxing (containers/VMs with no documented opt-out) over pattern matching.
- **Build a bypass-class regression test** (Classes A–E above) into CI for any custom command-guard code you maintain.
- **Treat "sandbox with a local opt-out flag" as no sandbox** — if the isolation can be disabled by config, assume attacker-controlled input can eventually reach that config.

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources

- [Adversa AI — AI coding agents vulnerability: GuardFall shell injection](https://adversa.ai/blog/opensource-ai-coding-agents-shell-injection-vulnerability/) — primary disclosure; full bypass-class breakdown, per-agent failure-mode classification, Continue's defense design.
- [The Hacker News — GuardFall Exposes Open-Source AI Coding Agents to Decades-Old Shell Injection Risks](https://thehackernews.com/2026/06/guardfall-exposes-open-source-ai-coding.html) — independent corroboration of affected/unaffected agent list, disclosure date, and technical detail.
- [SecurityAffairs — GuardFall Flaw Hits 10 of 11 Popular Open-Source AI Agents](https://securityaffairs.com/194546/ai/guardfall-flaw-hits-10-of-11-popular-open-source-ai-agents.html) — additional corroboration.
