---
id: 2026-10-agents-md-in-downloads-folder-hijacks-coding-agents-started-there-function-color-npm
title: "A planted AGENTS.md in ~/Downloads is read as project rules by agents started there; it steered Codex and Claude Code to a malicious npm package"
date_disclosed: 2026-10-24
last_updated: 2026-10-26
severity: high
status: active
ecosystems: [npm, ai-coding-agents, macos, windows]
tools_affected: ["OpenAI Codex CLI, Claude Code and other agents that load AGENTS.md, CLAUDE.md or equivalent instruction files from the working directory", "any session started with ~/Downloads as the working directory"]
tags: [prompt-injection, instruction-file, agents-md, claude-md, downloads-folder, working-directory, codex, claude-code, malfex, npm, defender-signal]
---

## TL;DR
Researchers at Forever Security showed, and BleepingComputer (10-25) and The Hacker News (10-24) reported, that a browser download can drop an instruction file into `~/Downloads`, and an agent started in that folder treats it as the project's rules. Their test file told the agent to install an npm package from the MALFEX family (`function-color`, already in [the MALFEX advisory](2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader.md)); Codex complied in about 90% of runs and Claude Code in about 50%. The researchers' own customer telemetry showed hundreds of customers running agents from ~/Downloads and more than 1,300 Claude Code sessions launched from that folder. Both vendors told the outlets the behaviour is by design: the instruction file is trusted because the directory is. Never start an agent in a folder a browser writes to, and treat instruction files you did not write as untrusted.

## What happened
An instruction file is not code, so download scanners, Gatekeeper and SmartScreen ignore it; it only has to be present when the agent reads its working directory. The researchers' chain ended at a package install, which is the step this corpus already tracks as a compromise. No vulnerability was assigned and there is nothing to patch; the control is where the agent is started and what it is allowed to install.

## Am I affected?
- `ls ~/Downloads/AGENTS.md ~/Downloads/CLAUDE.md ~/Downloads/.cursorrules ~/Downloads/.github/copilot-instructions.md` and the same in any folder a browser, mail client or chat app saves to.
- Agent session logs showing a working directory under Downloads, Desktop or a shared folder.
- `npm ls -g function-color` and the MALFEX package list in the linked advisory.

## If you are affected
1. Delete the planted file; if the agent ran an install from it, follow [if you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md) and [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).
2. Rotate what the session could read: [credential hygiene](../prevention/credential-hygiene.md).

## Prevention
- Start agents in a project directory you created; add Downloads and Desktop to the agent's deny list where the tool supports one.
- Require confirmation for package installs and network calls; [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources
- [BleepingComputer — AI coding agents hijacked using AGENTS.md file in Downloads folder](https://www.bleepingcomputer.com/news/security/ai-coding-agents-hijacked-using-agentsmd-file-in-downloads-folder/) — fetched 2026-10-26 (2026-10-25, Bill Toulas): the researcher attribution, the `function-color` package, the compliance rates, the session count, the vendors' responses.
- [The Hacker News — Malicious file in Downloads folder hijacks AI coding agents](https://thehackernews.com/2026/10/malicious-file-in-downloads-folder.html) — fetched 2026-10-26 (2026-10-24): the mechanism category and vendor statements.
- Related: [MALFEX](2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader.md), [BragJack](2026-09-bragjack-browser-extension-builtin-ai-assistant-hijack.md) for the same researchers' earlier work.
