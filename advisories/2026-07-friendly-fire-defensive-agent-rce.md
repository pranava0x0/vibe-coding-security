---
id: 2026-07-friendly-fire-defensive-agent-rce
title: "Friendly Fire — hijacking Claude Code auto-mode and Codex auto-review into running the malware they were sent to catch (July 2026)"
date_disclosed: 2026-07-08
last_updated: 2026-07-08
severity: high
status: active
ecosystems: [claude-code, codex-cli, agent-frameworks]
tools_affected: [Anthropic Claude Code CLI, OpenAI Codex CLI]
tags: [prompt-injection, rce, defensive-ai, readme-injection, no-cve, no-patch]
---

## TL;DR

The AI Now Institute disclosed **Friendly Fire**: a proof-of-concept where a coding agent asked to *defensively review* a third-party codebase for vulnerabilities is instead tricked into executing the malicious payload it was supposed to catch. The injection lives entirely in a `README.md` and a disguised binary — no MCP server, hook, skill, or config file needed. It works unchanged against **Claude Code (Sonnet 4.6, Sonnet 5, Opus 4.8) in auto-mode** and **OpenAI Codex CLI (GPT-5.5) in auto-review mode**. Both vendors were notified but say the report falls outside their formal disclosure programs; there is **no CVE and no patch** — the authors frame it as a workflow-design flaw, not a version bug.

## What happened

Published **2026-07-08**, the researchers built a two-layer payload inside a forked copy of the popular `geopy` Python library:

1. **Legitimacy layer** — three files (`security.sh`, a compiled binary named `code_policies`, and a matching `code_policies.go` source file) made the binary look like ordinary, already-reviewed security tooling. Matching source/binary filenames and strings were chosen specifically to defeat an agent's "does this binary match its claimed source" sanity check — in some test runs, a model correctly *noticed* the binary didn't match its supposed source and **ran it anyway**.
2. **Activation layer** — `README.md` was edited to reference `security.sh` as a normal setup/verification step. No exploit code appears in application logic; the entire attack surface is a text file every repository already has.

When a developer points Claude Code (in **auto-mode**, i.e., configured to act without per-step confirmation) or Codex CLI (in **auto-review**) at the repo with an instruction like "review this library for security issues," the agent reads the README, treats running `security.sh` as a routine verification step, and executes the attacker's binary on the host — achieving RCE with the developer's privileges.

Tested configurations: Claude Code CLI versions 2.1.116, 2.1.196, 2.1.198, and 2.1.199 across Claude Sonnet 4.6, Sonnet 5, and Opus 4.8; and OpenAI Codex CLI 0.142.4 on GPT-5.5. The same unmodified payload worked across every model tested. The authors' framing: "the access needed to employ AI agents toward automating vulnerability discovery or patching... coupled with inadequate AI-enabled safeguards, is sufficient to pave unmitigable pathways to arbitrary code execution."

Both Anthropic and OpenAI were contacted; the researchers state the finding sits outside the scope of either company's formal security-disclosure program. No CVE has been assigned and no patch exists as of publication — this is disclosed research with **no reported in-the-wild exploitation**, but the technique requires no special access and generalizes to any agent run in an unattended/auto-approve defensive-review workflow.

## Am I affected?

You're in scope if you run **Claude Code in auto-mode** or **Codex CLI in auto-review** (or any agent configured to act without per-command confirmation) against **third-party or unfamiliar codebases** — including the common "have the agent security-review this dependency before I adopt it" workflow, which is exactly the scenario this PoC targets.

Quick self-test: before pointing an auto-mode/auto-review agent at an unfamiliar repo, check whether its `README.md` instructs running any script, and whether that script's referenced binary has a plausible but unverifiable source match — that pattern (script + companion "source" file + compiled binary, invoked from README as a routine step) is the Friendly Fire shape.

## If you are affected

- **Never run Claude Code auto-mode or Codex CLI auto-review against an untrusted or unfamiliar repository.** Use per-step confirmation for any agent session reviewing code you didn't write and don't already trust.
- If an auto-mode/auto-review session already processed an unfamiliar repo, treat the host as potentially compromised: check shell history and running processes for anything spawned during that session, and rotate credentials reachable from that machine.
- Don't rely on an agent's own "this binary doesn't match its source" observation as a safety gate — the PoC shows models can flag the mismatch and still execute the file.

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- **Treat "have an AI agent security-review this dependency" as itself an untrusted-content workflow** — the agent doing the reviewing is exposed to the same prompt-injection risk as any other agent reading attacker-controlled text.
- **Disable auto-mode/auto-approve for any session where the codebase under review isn't already trusted**, regardless of whether the task is offensive or defensive in nature.
- **Run defensive code-review agent sessions in an isolated, disposable environment** (container/VM with no credentials or network access) so a successful injection can't reach real secrets or systems.
- **Don't treat "this is a security review, not a build" as lower risk** — Friendly Fire shows the defensive-use case carries the same RCE exposure as any other agent-reads-untrusted-content pathway; the same connector-chaining and workspace-trust cautions this repo tracks for coding agents apply equally here.

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources

- [AI Now Institute — Friendly Fire: Hijacking Defensive Cyber AI Agents for Remote Code Execution](https://ainowinstitute.org/publications/friendly-fire-exploit-brief) — primary disclosure; full technical breakdown, tested versions/models, vendor contact status.
- [The Hacker News — Top AI Agents Built to Catch Malicious Code Can Be Tricked Into Running It](https://thehackernews.com/2026/07/friendly-fire-ai-agents-built-to-catch.html) — independent corroboration of attack mechanism, tested tools, and disclosure status.
