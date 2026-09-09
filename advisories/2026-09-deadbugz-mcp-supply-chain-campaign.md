---
id: 2026-09-deadbugz-mcp-supply-chain-campaign
title: "Deadbugz — malicious MCP server waits until the third tool call before rewriting its own metadata into credential-theft instructions"
date_disclosed: 2026-08-12
last_updated: 2026-09-09
severity: high
status: unconfirmed
ecosystems: [mcp, claude-code, cursor, codex-cli]
tools_affected: [claude-code, cursor, codex-cli, mcp-clients, github-pull-requests]
tags: [prompt-injection, mcp, malicious-mcp-server, agentjacking, data-exfiltration, no-cve, call-count-trigger]
---

## TL;DR

Pillar Security disclosed an active MCP supply-chain campaign it calls **Deadbugz**: a malicious MCP server named `productivity-suite` looks and behaves like an ordinary text-formatting/summarization tool for its first three tool calls, then silently rewrites the tool descriptions it returns to the connected AI coding agent into instructions to hunt for and exfiltrate SSH keys, AWS credentials, shell history, and Kubernetes configs — while hiding the activity from the user. The threat actor pushed the server into **23 unsolicited GitHub pull requests across unrelated AI/developer-tool projects in a 74-minute window** on 2026-08-10. No CVE has been assigned; this is a single-researcher disclosure (Pillar Security), with secondary outlets (Adversa, nhimg.org) summarizing rather than independently verifying it — marked `unconfirmed` per this repo's two-independent-source bar, the same status given to the related [GhostSplice](2026-08-ghostsplice-mcp-instruction-splitting.md) finding.

## What happened

The server calls itself `productivity-suite` and, on first connection, offers exactly the kind of small, plausible utility a developer would add to a coding agent's toolset: text formatting and summarization. For the first three tool calls made against it, that's exactly what it does. On the fourth interaction, the server changes the tool metadata (the `description` text an MCP client shows to the connected model as if it were a static, already-reviewed capability) into instructions directing the agent to search for and exfiltrate SSH private keys, AWS credentials, shell history, and Kubernetes config files, without surfacing that change to the human operator.

The trigger is a **call count, not a code change or version bump** — the same package/server artifact a reviewer approved on day one is the one that turns malicious later, once ordinary usage crosses a threshold. That defeats the control most teams actually rely on for MCP servers: a one-time install/code review at connection time. Static inspection of the server at approval time sees only the benign first-three-calls behavior; the credential-hunting instructions do not exist anywhere to be reviewed until the fourth call constructs them at runtime.

Distribution was via GitHub: the threat actor (GitHub account `zellkernel`, source repo `github.com/zellkernel/productivity-suite-mcp`) opened 23 pull requests recommending or adding the MCP server to unrelated AI, MCP, and developer-tool projects between 21:52 and 23:07 UTC on 2026-08-10 — a 74-minute window. Of those, 19 were closed by maintainers and 4 remained open as of Pillar's disclosure (2026-08-12).

This is the same "tool definition treated as static, pre-reviewed metadata" root cause this repo already tracks for [GhostSplice](2026-08-ghostsplice-mcp-instruction-splitting.md) (instruction fragmented across `description` and `result` fields) — Deadbugz's novel contribution is spreading the same class of attack across *time* (a call-count gate) rather than across *structured fields*, and packaging distribution as a mass, automated pull-request campaign rather than requiring a developer to seek the server out.

## Am I affected?

You're exposed if you (or a repository you maintain) connected the `productivity-suite` MCP server, or accepted a pull request recommending it, at any point since 2026-08-10.

```bash
# Check MCP client configs for the malicious server's endpoint or package name
grep -ri 'productivity-suite' ~/.claude/settings.json ~/.cursor/mcp.json ~/.codex/config.toml 2>/dev/null
grep -ri 'productivity-suite-mcp.onrender.com' ~/.claude/settings.json ~/.cursor/mcp.json ~/.codex/config.toml 2>/dev/null

# Check for the disguised local artifact IOC published in the disclosure
ls -la ~/.config/.cache/.sys/.deadbug-mcp.py 2>/dev/null

# Review any open or recently-merged PR from GitHub user zellkernel across your repos
```

There's no static signature in your own repo's source — the malicious behavior lives in the server's runtime response after three calls, not in code you'd diff. Any outbound connection to `productivity-suite-mcp.onrender.com` from a developer machine or CI runner is a confirmed compromise signal.

## If you are affected

- [If an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md)
- [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) — SSH keys, AWS credentials, and Kubernetes configs are the stated targets
- [If your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention

- [MCP hygiene](../prevention/mcp-hygiene.md)
- [Agent sandboxing](../prevention/agent-sandboxing.md)
- Treat a change in an MCP tool's `description`/metadata between calls as a security event requiring re-approval, not a benign update — a one-time install review is not sufficient when the malicious behavior is gated on usage count rather than on the artifact itself.
- Be skeptical of MCP-server pull requests, especially ones arriving as part of a burst of similar PRs across unrelated repositories in a short window — that pattern is itself a detection signal, independent of what the server does.
- Never execute a script an MCP server or its documentation asks you to run locally; the disclosure also names a disguised local artifact path (`~/.config/.cache/.sys/.deadbug-mcp.py`) as part of the campaign's persistence mechanism.

## Sources

- [Pillar Security — Deadbugz: Currently Active MCP Supply-Chain Campaign](https://www.pillar.security/blog/deadbugz-currently-active-mcp-supply-chain-campaign) — primary disclosure: mechanism, timeline, IOCs (endpoint, local artifact path, GitHub account/repo, campaign Bitcoin address), PR count and window, open/closed PR status.
- [Adversa AI — MCP security September 2026: Deadbugz + 3 server CVEs](https://adversa.ai/blog/top-mcp-security-resources-september-2026/) — secondary summary confirming the three-call trigger and targeted-credential list.
- [nhimg.org — Deadbugz shows how MCP metadata poisoning evades AI agent trust](https://nhimg.org/articles/deadbugz-shows-how-mcp-metadata-poisoning-evades-ai-agent-trust/) — secondary summary; frames the finding as a tool-identity/runtime-integrity problem for agent governance.
