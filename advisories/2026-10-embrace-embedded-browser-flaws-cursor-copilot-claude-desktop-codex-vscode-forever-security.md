---
id: 2026-10-embrace-embedded-browser-flaws-cursor-copilot-claude-desktop-codex-vscode-forever-security
title: "Embedded browsers in Cursor, Copilot, Claude Desktop, Codex and VS Code read local files or drive the agent (Embrace); Codex and VS Code unfixed"
date_disclosed: 2026-10-29
last_updated: 2026-10-30
severity: high
status: active
ecosystems: [cursor, github-copilot, claude-desktop, codex, vscode, electron]
tools_affected: ["Cursor before the silent fix of 2026-10-01 (integrated browser)", "GitHub Copilot 1.1.27, as the post names it (browser preview); fixed 1.1.29, a line that matches the github/app releases", "Claude Desktop (file:// page read through a web worker); reported 2026-07-23 and 2026-07-24, fix status per the SneakPeek file", "Codex (file:// pages read any file); unfixed as of 2026-10-29", "VS Code (same web-worker read as Claude Desktop); unfixed as of 2026-10-29"]
tags: [embedded-browser, electron, file-url, local-file-read, prompt-injection, address-bar-spoofing, cursor, github-copilot, claude-desktop, codex, vscode, silent-fix, no-cve, unpatched, forever-security, workspace-trust]
---

## TL;DR
Forever Security (Gal Weizman, 2026-10-29) reports that the browsers embedded in five AI coding tools carry capabilities a normal browser does not: in Cursor a web page could write into the agent's composer and reach code execution (fixed silently on 2026-10-01), in the GitHub Copilot app 1.1.27 a page could set the address bar to a URL of its choosing (fixed 1.1.29 on 2026-10-13), and in Claude Desktop, Codex and VS Code a local `file://` page, or a web worker spawned from one, could read any file the user can read. The researcher says Codex and VS Code were still open at publication, OpenAI told The Register it is working on the Codex issue, and Microsoft and Anthropic classed the reports as workspace-trust issues. No CVE has been assigned to any of the five.

## What happened

Forever Security's post names the class "EMBRACE" (embedded browser) and gives one finding per tool. Dates and statuses below are the researcher's unless marked otherwise; The Register (Jessica Lyons, 2026-10-29) carries the same table and the vendor responses.

| Tool | Component, as the post names it | What a page could do | Status as the researcher states it |
|---|---|---|---|
| Cursor | "Cursor's integrated browser" | call a bridge that injects instructions into the agent's composer; the demonstration ran the macOS Calculator | reported 2026-09-10; "silently patched" 2026-10-01; no advisory, no reply to the researcher or to The Register |
| GitHub Copilot | "Copilot's browser preview", version 1.1.27 | report its own address to the app, which checked only the format, so the bar showed `github.com/login` over another page | confirmed 2026-09-26 on 1.1.27; fixed in 1.1.29 (2026-10-13) before a report was sent |
| Claude Desktop | "Claude Desktop" | a `file://` page's read restrictions were not applied inside a web worker; any file on disk | reported 2026-07-23, declined as a workspace-trust issue; Noma Security reported the same path 2026-07-24 and it was accepted |
| Codex | "Codex" | no file-read restriction on `file://` pages | reported 2026-07-27; no response; open at publication |
| VS Code | "VS Code" | the same worker escape as Claude Desktop | reported 2026-09-10; declined as a workspace-trust issue; open at publication |

The post does not give platform or version numbers for Cursor, Claude Desktop, Codex or VS Code, and it gives no user guidance beyond "Anyone using either tool is still exposed." The Register adds the vendor responses: OpenAI "is aware of the Codex issue and is working to address it"; Cursor, GitHub, Anthropic and Microsoft did not answer its questions.

**Claude Desktop is the SneakPeek bug.** The dates match the Noma Labs timeline in [the SneakPeek file](2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma.md): Anthropic's first mitigation on 2026-07-24 blocked `file://` reads from the main page and Noma bypassed it the same day with a worker created from a `blob:` URL; the fix Noma reports shipped 2026-08-17 in Claude Desktop 1.30096.1. Forever's report of 2026-07-23 is the day before Noma's and describes the worker read, so the two firms found the same gap independently. Forever's post does not say whether Anthropic's August fix closes its variant, and this file does not claim it does.

**Copilot's fix is in the `github/app` release of 2026-10-13.** The repository `github/app` carries a v1.1.29 release dated 13 Oct whose notes list session, diff, Files-panel, MCP sign-in and Windows fixes and do not mention the browser preview or the address bar; the researcher's statement that 1.1.29 fixed the spoof is the only account of the fix. The post does not say which Copilot client "GitHub Copilot 1.1.27" is; the version line matches the `github/app` releases.

**Why it matters.** Each of these tools gives its browser pane to the agent and, in Cursor's case, gives the page a way back into the agent. A repository the user clones can carry an HTML file, and the agent will open it. The Claude Desktop, Codex and VS Code findings make that file a reader of SSH keys, cloud credentials and tokens on the workstation; the Cursor finding made it an instruction source for the agent. "Workspace trust", the boundary two vendors cited, is a prompt the user answered once when opening the folder.

**Severity.** `high`, not `critical`: every path needs the user to open attacker content inside the tool, and the two unfixed ones read files rather than run code. `status: active` because the researcher says Codex and VS Code are open and OpenAI says it is working on a fix.

## Am I affected?

- You open repositories or HTML files you did not author in Codex or VS Code and the tool renders them in its own browser pane. Until a fix ships, that pane can read any file your account can.
- You run Cursor and did not update after 2026-10-01: the composer path is fixed only in builds after that date, and Cursor has published no version number for it.
- You run a GitHub Copilot client on the 1.1.x line below 1.1.29 (the post names only "GitHub Copilot").
- You run Claude Desktop below 1.30096.1 (Noma's fixed version); see the SneakPeek file for the check.

```bash
# the HTML a cloned repository ships, which the agent will render if asked
git ls-files '*.html' | head
git log --diff-filter=A --name-only --format= -- '*.html' | head   # when each was added
```

## If you are affected

1. Do not render untrusted HTML in Codex or VS Code's embedded browser until a fix is published; open it in a browser that has no `file://` access to your home directory, or not at all.
2. Update Cursor, the Copilot app and Claude Desktop to current builds.
3. If an untrusted repository's HTML was rendered in one of the three file-reading tools, rotate the credentials on that workstation: [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md), [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Keep fewer long-lived credentials on the machine the agent runs on: [credential hygiene](../prevention/credential-hygiene.md).
- Run agents in a sandbox whose filesystem view is the project, not the home directory: [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources
- [Forever Security — Embrace: hacking 5 AI assistants through their embedded browsers](https://forever.security/blog/embrace-hacking-5-ai-assistants-embedded-browsers-technical) — fetched 2026-10-30: dated 2026-10-29, Gal Weizman, the five findings, the timeline (07-23, 07-24, 07-27, 09-10, 09-26, 10-01, 10-13, 10-29), the component names as quoted above, "At the time of publishing, the Codex and VS Code issues are still open", no CVE, no user guidance.
- [The Register — Researchers find bugs in 5 AI developer tools, with OpenAI and Microsoft flaws still unpatched](https://www.theregister.com/security/2026/10/29/researchers-find-bugs-in-5-ai-developer-tools-with-openai-and-microsoft-flaws-still-unpatched/5306508) — fetched 2026-10-30: 2026-10-29, Jessica Lyons, the same table, Noma's independent Claude Desktop report, OpenAI's statement, the non-responses from Cursor, GitHub, Anthropic and Microsoft.
- [github/app — release v1.1.29](https://github.com/github/app/releases/tag/v1.1.29) — fetched 2026-10-30: dated 13 Oct, notes list fixes without naming the browser preview or address bar.
- [cursor/cursor — security advisories](https://github.com/cursor/cursor/security/advisories) — fetched 2026-10-30: newest row 2026-07-14, no advisory for the composer bridge.
- [anthropics/claude-code — security advisories](https://github.com/anthropics/claude-code/security/advisories) — fetched 2026-10-30: no advisory naming the preview pane or web workers.
- Related in this corpus: [Claude Code Desktop preview pane (SneakPeek, Noma)](2026-10-claude-code-desktop-sneakpeek-preview-pane-html-file-url-exfiltration-noma.md).
