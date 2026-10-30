---
id: 2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma
title: "Claude Code Desktop preview pane rendered large HTML files without CSP, letting a cloned repository read and send local credentials (SneakPeek); fixed 2026-08-17"
date_disclosed: 2026-10-15
last_updated: 2026-10-30
severity: high
status: mitigated
ecosystems: [claude-code, claude-desktop, electron]
tools_affected: ["Claude Code Desktop (Claude Desktop app) before 1.30096.1, per the researcher", "developers who clone untrusted repositories and ask Claude to review HTML files in them"]
tags: [claude-code, claude-desktop, electron, preview-pane, csp, file-url, data-exfiltration, credential-theft, untrusted-repository, two-researchers, no-cve-yet]
---

## TL;DR
Noma Labs published "SneakPeek" on 2026-10-15: Claude Code Desktop's preview pane renders an HTML file the agent reads or edits, and files over 256 KB were loaded from a `file://` URL without the Content Security Policy that smaller files get, so a script in an oversized HTML file in a cloned repository ran, read local files the request filter did not cover, and sent them out with a one-way HTTP request. The victim only has to clone the repository and ask Claude to review the file; no permission prompt fires. The researcher's timeline says Anthropic triaged it at CVSS 4.0 8.7 on 2026-07-09, shipped a first patch on 2026-07-24 that a Web Worker created from a `blob:` URL bypassed the same day, and fixed it in Claude Desktop 1.30096.1 on 2026-08-17 via auto-update. This file is `unconfirmed` because the only source is the researcher's post; no vendor advisory, GHSA or CVE exists as of 2026-10-15.

## What happened

Noma's post describes two gaps that chained. Claude Code Desktop is an Electron app with a preview pane that automatically renders HTML files Claude reads or edits. Files under 256 KB are loaded as `data:` URLs with a CSP. Files over that size are loaded by `file://` URL with no CSP, and the request filter that blocks local file reads does not engage for static files rendered directly from disk. Together those allowed arbitrary JavaScript to execute in the renderer, read local files and send them to a server the attacker controls. The targets the post lists are SSH keys, cloud and registry credentials, Git and package-registry tokens, Kubernetes credentials and Claude's own OAuth tokens, plus the victim's IP address.

The delivery is a public repository containing an HTML file over 256 KB that looks like a routine coverage report and carries a script. A developer clones it and asks Claude to review that file; the pane renders it and the script runs. The post says no additional prompt is required.

Timeline, as the researcher states it: reported 2026-07-04; triaged as CVSS 4.0 8.7 (High) on 2026-07-09; a patch blocking direct `file://` reads from the main page context shipped 2026-07-24 and Noma reported a bypass the same day using a Web Worker created from a `blob:` URL; Anthropic confirmed the bypass 2026-08-03; the fix shipped in Claude Desktop 1.30096.1 and later on 2026-08-17, delivered by auto-update; the post says a GitHub advisory and CVE are pending. Claude Code's own advisory tab on 2026-10-15 carries no entry for this bug; its newest Desktop advisory there is the 2026-09-25 Cowork folder entry ([tracked here](2026-08-claude-code-desktop-ghsa-batch.md)). A web search on the day returned no second source, and the Hacker News thread (15 points) links only the post.

Why it matters to this audience: it is the third Claude Desktop path this year where a file in a cloned repository, not an instruction to the model, is the attack, after the Cowork folder entry and the Windows `git.exe` search-path bug ([CVE-2026-88066 file](2026-10-claude-desktop-windows-git-exe-search-path-rce-cve-2026-88066.md)). The preview pane is a browser with the developer's filesystem behind it, and the size threshold decided which security policy applied.

## Am I affected?

- You run Claude Code Desktop and it is older than 1.30096.1 (the researcher's fixed version; the app auto-updates, so check the About dialog).
- Before 2026-08-17 (the researcher's fix date; the bug predates the 2026-07-04 report and nothing bounds its start) you cloned a repository you did not author and asked Claude to open or review an HTML file in it.

```bash
# oversized HTML files in recently cloned repositories
find . -name '*.html' -size +256k 2>/dev/null | head
```

## If you are affected

Update Claude Desktop. If an untrusted repository's large HTML file was opened in the pane on a build older than 1.30096.1, treat the workstation's credentials as exposed: rotate SSH keys, cloud and registry tokens, Git and package tokens, Kubernetes credentials and Claude sessions. Follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md), [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) and [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Review a cloned repository before asking an agent to open files in it; a large HTML report is content, and the agent's viewer is a browser.
- Keep fewer long-lived credentials on the workstation the agent runs on. See [credential-hygiene.md](../prevention/credential-hygiene.md) and [agent-sandboxing.md](../prevention/agent-sandboxing.md).


## Update 2026-10-30 — a second firm reported the same web-worker read a day before Noma; status moves to `mitigated`

Forever Security's "Embrace" post (2026-10-29) says it reported to Anthropic on 2026-07-23 that a `file://` page's read restrictions in Claude Desktop were not applied inside a web worker, and that Anthropic declined the report as a workspace-trust issue; Noma's report of 2026-07-24 for the same path was accepted. The Register (10-29) carries the same account. Two researchers reaching the same gap independently is the second source this file lacked, so `status` moves from `unconfirmed` to `mitigated`: the fix date and version (2026-08-17, 1.30096.1) remain the researcher's statement, no vendor advisory names the bug on the Claude Code tab as of 2026-10-30, and Forever's post does not say whether its variant is closed. The other four tools in that post are in [the Embrace file](2026-10-embrace-embedded-browser-flaws-cursor-copilot-claude-desktop-codex-vscode-forever-security.md).

Sources for this update: [Forever Security — Embrace](https://forever.security/blog/embrace-hacking-5-ai-assistants-embedded-browsers-technical) — fetched 2026-10-30: the 07-23 report, "declined", Noma's 07-24 acceptance; [The Register, 2026-10-29](https://www.theregister.com/security/2026/10/29/researchers-find-bugs-in-5-ai-developer-tools-with-openai-and-microsoft-flaws-still-unpatched/5306508) — fetched 2026-10-30: the same timeline and Anthropic's non-response to its questions.

## Sources
- [Noma Labs, "SneakPeek", 2026-10-15](https://noma.security/noma-labs/sneakpeek-how-the-preview-pane-in-claude-code-desktop-can-exfiltrate-your-data) — the two gaps, the delivery, the timeline and the fixed version; single source.
- [Claude Code security advisories tab](https://github.com/anthropics/claude-code/security/advisories) — no entry for this bug as of 2026-10-15.
