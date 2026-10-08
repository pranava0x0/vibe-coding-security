---
id: 2026-10-vtcode-find-approval-bypass-ansi-c-quote
title: "VTCode (open-source Rust coding agent): once a user approves three ordinary `find` commands, the agent auto-approves later `find` commands in that family, and an ANSI-C quote spliced into a destructive flag (`-exe$''c`) evades the block on `-exec`/`-delete` — so a prompt-injected agent runs an unapproved destructive command (CVE-2026-104247, CVSS 6.3, fixed 0.171.5)"
date_disclosed: 2026-10-05
last_updated: 2026-10-08
severity: medium
status: patched
ecosystems: [cargo, ai-agents, coding-agent]
tools_affected: ["vtcode (Rust coding agent)"]
tags: [cve, coding-agent, approval-bypass, prompt-injection, shell-parsing, find-command, jfrog]
---

## TL;DR
**VTCode**, an open-source Rust coding agent, learns to auto-approve commands: after a user approves three ordinary `find` commands in the same workspace subdirectory, it treats later `find` commands in that family as safe. Its guard against destructive flags (`-exec`, `-delete`) compares exact tokens, so splicing an empty ANSI-C quote into a flag — `-exe$''c` — slips a destructive command past the check and runs it **without a prompt**. With indirect prompt injection steering the agent, that is an unapproved destructive command on the user's machine. JFrog disclosed it as **CVE-2026-104247, CVSS 6.3**, fixed in **0.171.5** (2026-10-05).

## What happened
JFrog's Natan Nehorai found that VTCode's shell-approval logic has two reinforcing weaknesses: a **family-learning** rule that auto-approves `find` commands after three manual approvals under the same subdirectory, and a **denylist** for destructive `find` flags that matches exact tokens and so misses `-exec`/`-delete` written with an empty ANSI-C quote spliced in. Combined, a `find` command carrying a destructive predicate is classified as safe and executed without approval. Exploitation needs a local session with those prior approvals plus a way to steer the agent, such as indirect prompt injection in the content it reads. An earlier change (0.141.12) blocked the bypass only for bare `find`; the fix in **0.171.5** (PR #778) also stops family-learning for path-qualified `find`, quote-spliced and mixed-case flags, wrapper/environment prefixes and compound commands. JFrog rates it **CVSS 6.3 (medium)**, advisory JFSA-2026-001694179 / GHSA-r249-hpfx-x2w7. The crates.io release line is at 0.174.0.

This is the same approval-bypass class as the Mistral Vibe, Cursor and Claude Code `find`/allowlist bypasses: a coding agent's auto-approve heuristic is a parser, and the shell parses more than the heuristic does. VTCode is niche, but the pattern is the point.

## Am I affected?
```bash
cargo install --list 2>/dev/null | grep -i vtcode     # < 0.171.5 is affected
vtcode --version 2>/dev/null
```
You are exposed if you ran VTCode below 0.171.5 and relied on learned `find` approvals in a workspace where untrusted input can steer the agent.

## If you are affected
Upgrade to **0.171.5 or later**. Until then do not rely on learned `find` approvals, and treat any workspace where untrusted content drives the agent as able to run shell commands after a few approved finds. See [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) and [agent-sandboxing.md](../prevention/agent-sandboxing.md).

## Prevention
Prefer agents that sandbox rather than learn-to-approve, and never let an auto-approve heuristic stand in for an OS sandbox ([agent-sandboxing.md](../prevention/agent-sandboxing.md)); keep untrusted repos and content from steering an agent with command approvals banked ([mcp-hygiene.md](../prevention/mcp-hygiene.md)).

## Sources
- [JFrog Security Research — VTCode is vulnerable to arbitrary command execution via an ANSI-C quote bypass of the find approval check (CVE-2026-104247)](https://research.jfrog.com/vulnerabilities/vtcode-is-vulnerable-to-arbitrary-command-execution-via-an-ansi-c-quote-bypass-of-the-find-approval-check-cve-2026-104247-jfsa-2026-001694179/) (2026-10-05, Natan Nehorai: family-learning + denylist bypass, `-exe$''c` example, fix 0.171.5 / PR #778, mitigations)
- [GitHub — vinhnx/vtcode GHSA-r249-hpfx-x2w7: 'Destructive find' Security Filter Bypass](https://github.com/vinhnx/vtcode/security/advisories/GHSA-r249-hpfx-x2w7) (CVE-2026-104247, CVSS 6.3 `AV:L/AC:H/PR:H/UI:R/S:U/C:H/I:H/A:H`, affected < 0.171.5, fixed 0.171.5, credit nnfrog / JFrog)
- [GitHub — vinhnx/VTCode releases](https://github.com/vinhnx/vtcode/releases) (fix release 0.171.5; the crates.io line was at 0.174.0 at this sweep, confirming the fix is published)
