---
id: 2026-09-vscode-workspace-trust-bypass-single-link-extension-install
title: "VS Code Workspace Trust bypass with one click: a link inside an untrusted (Restricted Mode) file resolves to a `command:` URI that installs an arbitrary extension with no signature or publisher check — the extension then runs on every editor launch; Remedio reported it to MSRC, which rated it a Moderate 'Security Feature Bypass,' declined a CVE, and had shipped no fix as of 2026-09-17"
date_disclosed: 2026-09-17
last_updated: 2026-09-26
severity: high
status: unconfirmed
ecosystems: [vscode, cursor, windsurf, github-copilot]
tools_affected: ["Visual Studio Code (latest stable at 2026-09-17)", "VS Code forks that inherit Workspace Trust and the link handler (Cursor, Windsurf, Antigravity — not individually verified)"]
tags: [workspace-trust, vscode, one-click, command-uri, extension-install, persistence, wont-fix, no-cve, ai-ide, restricted-mode-bypass]
---

## TL;DR
Remedio's Omri Dar published (2026-09-17) a chain by which **a single click on an ordinary-looking link inside a file opened in Restricted Mode installs an attacker-chosen VS Code extension**, which then activates on every launch, survives closing the folder and rebooting, and is removed only by hand. Workspace Trust exists precisely so that code in an untrusted folder cannot run; here the folder never has to be trusted. Six checks sit between "a link in a file you do not trust" and "a command executes" — the link scanner accepts any URI scheme, validation looks only at length, the `command:` scheme is turned into an executable command with no trust gate, command execution is enabled unconditionally, the execution guard accepts a bare `true` instead of an allow-list, and `workbench.extensions.installExtension` performs no signature or publisher validation — and each one lets the request through. **MSRC classified it as a Security Feature Bypass of Moderate severity, said it duplicated an earlier report, declined a CVE and cited the required click and a tooltip as mitigations; no patch had shipped at publication.** Every AI editor built on VS Code inherits this code path unless its maintainers changed it. This entry is `unconfirmed`: one research source, no vendor advisory, fork exposure not individually tested.

## What happened

Workspace Trust (VS Code 1.57, 2021) is the editor's answer to "I cloned something and opened it": in Restricted Mode, tasks, debug configurations, workspace settings that execute things, and extension features that run code are all disabled until the user clicks *Trust*. It is also the boundary every VS Code-derived AI IDE points to when asked how an untrusted repository is kept from running code — and it is the same boundary this corpus has already seen bypassed from the *agent* side ([Cursor open-folder autorun](2026-05-cursor-open-folder-autorun.md), [Claude Code's repo-controlled settings file](2026-08-claude-code-desktop-ghsa-batch.md), [Kiro's global-config writes from an untrusted workspace](2026-09-kiro-ide-cli-aws-bulletin-cve-batch.md)).

Remedio's finding bypasses it from the *editor* side. A Markdown or similar file in the untrusted folder carries a link. VS Code's link detection accepts the `command:` URI scheme without checking trust, so the rendered link is a command invocation with attacker-supplied arguments; the command chosen is the built-in extension installer, which takes an extension identifier (or VSIX) and installs it without signature or publisher verification. From the researcher's write-up: "Click it once, and an attacker is running code on your machine, as you, with access to your files, your SSH keys, your cloud tokens, and your source code." Because the result is an installed extension rather than a one-shot process, "one click does not rent the attacker a few seconds of code execution; it grants a standing foothold that renews itself every time you open the editor."

Microsoft's position, as reported by Remedio: a Security Feature Bypass of Moderate severity; a duplicate of an earlier submission; the click requirement and the hover tooltip are mitigations; no CVE. The Hacker News' 09-25 roundup carried the item as "workspace trust bypass flaw allowing one-click code execution via single link with access to SSH keys and cloud tokens." No VS Code release note or advisory referencing the issue was found at sweep time, and the `vscode` advisory-database query returns nothing matching.

**Why this matters more for AI-tool users than for 2021's VS Code:** the attacker no longer needs the user to click. A coding agent operating in the same workspace can be prompt-injected into opening a file and following a link (agent browsers and "open this URL" tools exist in Cursor, Copilot and Claude Code), and the corpus already documents agents that install extensions and MCP servers on instruction. Remedio's post does not test the forks; this entry flags them as *likely inherited* rather than confirmed.

## Am I affected?

- You open untrusted repositories in VS Code or a VS Code fork and rely on Restricted Mode to keep them inert. That is the design, so: yes, potentially.
- Check for the signal after the fact: an extension you did not install, appearing in `code --list-extensions` (or the fork's equivalent) after opening an untrusted folder; an extension whose publisher you do not recognise activating at launch.
- Check whether your build disables `command:` links in rendered content — there is no user setting that does so in stock VS Code at the time of writing; treat the answer as "no" unless your fork's release notes say otherwise.

## If you are affected

1. List and remove extensions you did not install (`code --list-extensions`; uninstall from the Extensions view). Removal is manual; there is no automatic rollback.
2. If a foreign extension ran, treat it as code execution as your user: rotate SSH keys, cloud and Git tokens → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md); if an agent was in the loop, → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- **Open untrusted code in a disposable environment, not in Restricted Mode on your workstation** — a devcontainer, a VM, or a cloud workspace — so that the trust decision is made by isolation, not by a dialog. → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Do not click links inside files from repositories you have not trusted**; hover first and refuse anything that is not `http(s)`.
- **Allow-list extensions** where the editor supports it (VS Code's `extensions.allowed` policy for managed installs) so that an installer command cannot add an unlisted publisher.
- Agent operators: keep "open URL / open file" tools behind approval in untrusted workspaces; the click that MSRC counts as a mitigation is one an agent can supply.

## Sources
- [Remedio — Bypassing VS Code Workspace Trust with a Single Link](https://remedio.io/blog/bypassing-vs-code-workspace-trust-with-a-single-link/) — primary, 2026-09-17 (Omri Dar): the six checkpoints, the `command:`-URI to `workbench.extensions.installExtension` path, the persistence properties, the MSRC classification, duplicate finding and CVE refusal, "no patch has shipped." Fetched 2026-09-26.
- [The Hacker News — ThreatsDay: AI Search Poisoning, AI Coding Tool Leaking Repos, One-Click Code Execution and 13 More Stories](https://thehackernews.com/2026/09/threatsday-ai-search-poisoning-ai.html) — 2026-09-25 roundup item; restates Remedio, adds no independent verification. Fetched 2026-09-26.
- [GitHub Advisory Database — query `vscode`, newest first](https://github.com/advisories?query=vscode+sort%3Apublished-desc) — checked 2026-09-26: no entry for this issue.
- Single-source note: MSRC's classification and response are known only through the researcher's post; Microsoft has published nothing. Status stays `unconfirmed` until a vendor advisory, release note or second researcher confirms; severity is set to `high` on the corpus's own reading (persistent code execution from a workspace the editor labels untrusted, inherited by the AI IDEs this audience uses).
- Related in this corpus: [Cursor open-folder autorun](2026-05-cursor-open-folder-autorun.md), [Claude Code trust-dialog bypasses](2026-08-claude-code-desktop-ghsa-batch.md), [Kiro untrusted-workspace global writes](2026-09-kiro-ide-cli-aws-bulletin-cve-batch.md), [Codespaces devcontainer autoexec](2026-02-github-codespaces-devcontainer-autoexec.md).
