---
id: 2026-10-graphify-code-knowledge-graph-skill-fortran-include-host-file-read-untrusted-repo-fixed-0-9-70
title: "Graphify, the 130k-star code-graph skill for Claude Code, Cursor and Codex: indexing an untrusted repo read host files into the graph; fixed graphifyy 0.9.70"
date_disclosed: 2026-09-27
last_updated: 2026-10-20
severity: medium
status: patched
ecosystems: [python, pypi, agent-skills, claude-code, cursor, codex, mcp]
tools_affected: ["graphifyy 0.7.2 through 0.9.69 (PyPI; CLI `graphify`) when it indexes a repository containing Fortran sources", "the graphify skill installed into Claude Code (.claude/skills/graphify/SKILL.md), Cursor, Codex, Gemini CLI, Copilot, OpenCode, Aider, OpenClaw, Kiro and the other assistants its installer targets", "the optional graphifyy[mcp] stdio server"]
tags: [ghsa, agent-skill, path-traversal, file-read, exfiltration, untrusted-repo, claude-code, cursor, codex, mcp, vendor-advisory, db-date-lag]
---

## TL;DR
Graphify (`Graphify-Labs/graphify`, PyPI `graphifyy`, about 130k stars) is the "turn any codebase into a queryable knowledge graph" tool that installs itself as a skill into Claude Code, Cursor, Codex and some twenty other assistants, so `/graphify .` runs over whatever repository the agent is in. Before 0.9.70 its Fortran extractor ran the C preprocessor over `#include` directives with incomplete restrictions, so a crafted Fortran file in an untrusted repository made the tool read arbitrary files from the host and write their contents into the generated graph and output files, where the agent then reads them (GHSA-pcc4-rvhr-2pr8, CVSS 4.0 6.8, no CVE). The vendor published the fix on 2026-09-27 (0.9.70 on PyPI the same day); the advisory reached the GitHub Advisory Database on 2026-10-19. Upgrade and re-run the install so the skill uses the new binary.

## What happened

Graphify parses code locally with tree-sitter and, for documents, with the assistant's own model, then writes a graph the assistant queries instead of grepping. Its README names Claude Code, Cursor, Codex, Gemini CLI and GitHub Copilot explicitly and lists "20+" supported assistants, with `graphify install` registering the skill and `graphify install --project` writing project-scoped files such as `.claude/skills/graphify/SKILL.md`. For Claude Code it adds a hook that fires before search-style tool calls. An optional extra, `graphifyy[mcp]`, exposes it as an MCP stdio server.

**GHSA-pcc4-rvhr-2pr8**, published by the vendor on 2026-09-27 and updated 2026-10-19 when it entered the database. Affected `graphifyy` >= 0.7.2, < 0.9.70; patched 0.9.70. CWE-22 and CWE-73. The Fortran extractor's preprocessor step applied incomplete `#include` restrictions, so a crafted Fortran source file in an untrusted repository could make the tool read arbitrary host files and include their contents in the graph and output files. CVSS 4.0 6.8 (`AV:L/AC:L/AT:N/PR:N/UI:P/VC:H/VI:N/VA:N`): local vector, user interaction, high confidentiality, no integrity or availability. Reporter aeonframework. The advisory's suggested fixes are to reject includes with absolute paths or paths outside the repository root, strip `#include` before preprocessing, or run the preprocessor in a filesystem sandbox; the title's word "incomplete" says an earlier hardening existed and this closed what it missed.

The reason this matters more than a 6.8 suggests is where the output goes. The graph is built so the agent reads it. A file read into the graph is a file read into the agent's context, and from there into whatever the agent writes next: a commit, a pull request, a tool call. That is the [SneakPeek](2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma.md) and [Miri](2026-09-rust-miri-github-actions-cache-secrets-leak.md) shape: a tool the pipeline trusts writes what it should not into an output that is read downstream.

PyPI, read 2026-10-20: 0.9.69 on 2026-09-26, 0.9.70 on 09-27, newest 0.9.92 (2026-10-16). The README warns that other `graphify*` packages on PyPI are not affiliated; the real one is `graphifyy` with two y's.

## Am I affected?

- `pip show graphifyy`, `uv tool list` or `pipx list` on the machine that runs the agent. Affected: 0.7.2 through 0.9.69.
- The skill is installed if `.claude/skills/graphify/` exists in a project, or the assistant's global skill directory holds a graphify entry, or the Claude Code hook graphify adds is present in settings.
- The condition is indexing a repository you did not write that contains Fortran sources, or any file the Fortran extractor picks up. Clones of untrusted repositories, dependency checkouts and pull-request branches all count.
- Check graph output files already generated from untrusted repositories for content that is not from that repository (keys, dotfiles, `/etc` paths).

## If you are affected

1. `pip install -U "graphifyy>=0.9.70"` (or the `uv tool` / `pipx` upgrade) and run `graphify install` again so the skill points at the upgraded tool.
2. Search generated graph and output files for host content; if any was produced from an untrusted repository and then read by the agent, treat the files it contained as disclosed and rotate accordingly, per [credential hygiene](../prevention/credential-hygiene.md).
3. Run skills that index untrusted repositories inside the agent's sandbox, not on the host, per [agent sandboxing](../prevention/agent-sandboxing.md).

## Prevention

- [Agent sandboxing](../prevention/agent-sandboxing.md): a skill that reads a repository is code the repository can steer.
- [Package vetting checklist](../prevention/package-vetting-checklist.md): a 130k-star skill is a dependency with a security tab; read it.
- [MCP hygiene](../prevention/mcp-hygiene.md) if you run the MCP extra.

## Sources
- [GitHub Advisory Database — GHSA-pcc4-rvhr-2pr8: Graphify Fortran extractor: incomplete cpp #include hardening allows arbitrary host-file read/exfiltration when indexing an untrusted repo](https://github.com/advisories/GHSA-pcc4-rvhr-2pr8) — fetched 2026-10-20: package, range, patched 0.9.70, CVSS 4.0 6.8 and vector, CWE-22/CWE-73, published 2026-09-27, updated 2026-10-19, no CVE, reporter, the suggested fixes.
- [Graphify-Labs/graphify — repository README](https://github.com/Graphify-Labs/graphify) — fetched 2026-10-20: the product description, `graphifyy` package name and the unaffiliated-package warning, `graphify install` and `--project` writing `.claude/skills/graphify/SKILL.md`, the per-platform install commands, the named assistants, the Claude Code hook, the MCP extra, about 129.8k stars.
- [GitHub Advisory Database — "mcp", sorted by published date](https://github.com/advisories?query=mcp+sort%3Apublished-desc) — fetched 2026-10-20: the row dated 2026-10-19 that surfaced this advisory.
- PyPI JSON for `graphifyy` — read 2026-10-20: 0.9.69 (2026-09-26), 0.9.70 (2026-09-27), newest 0.9.92 (2026-10-16); project URLs point at `Graphify-Labs/graphify`.
- Related in this corpus: [SneakPeek](2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma.md), [Miri writing CI environment variables into target/](2026-09-rust-miri-github-actions-cache-secrets-leak.md), [plugin4shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) for the skill-as-dependency class.
