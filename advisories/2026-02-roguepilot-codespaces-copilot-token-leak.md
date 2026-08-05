---
id: 2026-02-roguepilot-codespaces-copilot-token-leak
title: "RoguePilot: a hidden instruction in a GitHub Issue + a symlinked PR let GitHub Copilot leak your Codespaces GITHUB_TOKEN (patched)"
date_disclosed: 2026-02-16
last_updated: 2026-02-16
severity: high
status: patched
ecosystems: [github, vscode, github-codespaces]
tools_affected: [github-copilot, github-codespaces, vscode]
tags: [prompt-injection, symlink, token-leak, repository-takeover, github-issue, patched, backfill]
---

## TL;DR
Orca Research Pod found a chained attack — codenamed **RoguePilot** — against **GitHub Copilot running inside GitHub Codespaces**: a malicious instruction hidden in HTML comments inside a public **GitHub Issue** gets silently ingested by Copilot's agent mode when a developer launches a Codespace from that issue; the injected instruction directs Copilot to check out an attacker's pull request containing a symlink pointing at Codespaces' internal `user-secrets-envs.json`; Copilot's file-read tool follows the symlink; and a final step abuses VS Code's automatic JSON-schema download feature to exfiltrate the developer's live `GITHUB_TOKEN` to an attacker-controlled server — enough for full repository takeover. Reported to Microsoft/GitHub in mid-February 2026; Microsoft shipped a multi-layer patch **before 2026-02-24**. Backfilled into this repo this sweep — it predates this repo's coverage window and had gone untracked.

## What happened
[Orca Security's writeup](https://orca.security/resources/blog/roguepilot-github-copilot-vulnerability/) (Orca Research Pod, disclosed 2026-02-16) chains three separate weaknesses into one attack:

1. **Passive prompt injection via a GitHub Issue.** An attacker opens a public GitHub Issue containing an instruction hidden inside an HTML comment — invisible to a human skimming the issue, but read in full by an AI agent that ingests the issue body as context.
2. **Codespaces launch → Copilot agent mode.** When a developer opens a Codespace directly from that issue (a common "Code with agent mode" workflow), Copilot ingests the issue text as part of its working context and follows the hidden instruction.
3. **Symlink-based secret exfiltration.** The injected instruction directs Copilot to check out an attacker-supplied pull request. That PR contains a file that is actually a **symlink** pointing at `/workspaces/.codespaces/shared/user-secrets-envs.json` — a Codespaces-internal file holding the session's live secrets, including its `GITHUB_TOKEN`. Copilot's file-read tool follows the symlink rather than rejecting it.
4. **JSON-schema download as the exfil channel.** The attacker crafts the target file so it carries a `$schema` property pointing at an attacker-controlled URL. VS Code's `json.schemaDownload.enable` setting — on by default — automatically fetches that schema, and in doing so sends the file's contents (including the leaked `GITHUB_TOKEN`) to the attacker's server.

The combined chain gives the attacker the developer's live GitHub token and, with it, full access to whatever repositories that token can reach — no click beyond "open this Codespace from this issue," and no separate confirmation step for any of the intermediate actions.

**Patch status:** Orca reports Microsoft/GitHub "responded promptly," and independent coverage from [The Hacker News](https://thehackernews.com/2026/02/roguepilot-flaw-in-github-codespaces.html) states Microsoft developed and fully deployed a multi-layer patch before **2026-02-24** — roughly a week after private disclosure. No CVE was assigned.

## Relationship to this repo's other Codespaces/Copilot findings
This is a **distinct** vulnerability chain from the already-tracked [GitHub Codespaces devcontainer/tasks.json auto-execution class](2026-02-github-codespaces-devcontainer-autoexec.md) (also an Orca Research Pod finding, disclosed 12 days earlier on 2026-02-04, which Microsoft classified "by design" and left unpatched). Both target GitHub Codespaces and both start from "open an untrusted repository/issue," but RoguePilot's mechanism is prompt-injection-driven secret exfiltration through Copilot's agent tooling and VS Code's schema-download feature — not workspace-config auto-execution — and unlike the devcontainer class, **RoguePilot was patched**, not accepted as by-design behavior.

## Am I affected?
- If you use GitHub Copilot's agent mode inside GitHub Codespaces, update to a current Codespaces/Copilot build — the fix shipped before 2026-02-24, so any environment kept current since then already has it.
- As general hygiene going forward: be wary of launching a Codespace directly from an unfamiliar GitHub Issue, especially one prompting you to "code with agent mode," and consider disabling `json.schemaDownload.enable` in shared/ephemeral dev environments if you don't need it.

## If you are affected
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — rotate your GitHub token and audit repository access if you suspect this chain ran against you before the patch.
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — treat any AI-agent tool that ingests issue/PR text as reading untrusted input.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Why this matters for vibe coders
This is a clean instance of the "MCP/agent data-stream injection" pattern this repo tracks under Agentjacking, applied to GitHub's own first-party Copilot-in-Codespaces integration rather than a third-party MCP server: content an agent is designed to read (a GitHub Issue) turns out to be an instruction-delivery channel, and two unrelated platform features (symlink handling in a file-read tool, VS Code's automatic schema fetch) combine into a full token-exfiltration primitive that neither feature's owners had reason to threat-model in isolation. It's also a useful contrast with the sibling Codespaces devcontainer-autoexec finding: same researcher, same host platform, two weeks apart — one got a "by design, no fix" response, the other got a patch within about a week. Vendor response to structurally similar findings in the same product is not consistent, so "GitHub patched a related bug" is not a reason to assume every similar report gets fixed.

## Sources
- [Orca Security — RoguePilot: Critical GitHub Copilot Vulnerability Exploit](https://orca.security/resources/blog/roguepilot-github-copilot-vulnerability/) — primary disclosure: full attack chain, affected components, discovery/disclosure timeline.
- [The Hacker News — RoguePilot Flaw in GitHub Codespaces Enabled Copilot to Leak GITHUB_TOKEN](https://thehackernews.com/2026/02/roguepilot-flaw-in-github-codespaces.html) — independent corroboration, patch timeline (fixed before 2026-02-24).
- [SecurityWeek — GitHub Issues Abused in Copilot Attack Leading to Repository Takeover](https://www.securityweek.com/github-issues-abused-in-copilot-attack-leading-to-repository-takeover/) — independent corroboration.
