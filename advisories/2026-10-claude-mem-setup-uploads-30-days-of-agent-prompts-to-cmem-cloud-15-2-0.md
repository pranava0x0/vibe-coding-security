---
id: 2026-10-claude-mem-setup-uploads-30-days-of-agent-prompts-to-cmem-cloud-15-2-0
title: "claude-mem 15.2.0 to 15.5.0 setup uploads 30 days of Claude Code, Codex, Gemini CLI and OpenCode prompts to the vendor's cloud"
date_disclosed: 2026-10-29
last_updated: 2026-10-29
severity: high
status: ongoing
ecosystems: [npm, claude-code, codex, gemini-cli, opencode, plugins]
tools_affected: ["claude-mem (npm) 15.2.0 through 15.5.0 (current) when the interactive installer runs on a machine that has not completed setup", "the local transcript directories of Claude Code, Codex, Gemini CLI, Antigravity CLI and OpenCode on that machine"]
tags: [telemetry, prompt-upload, privacy, claude-code-plugin, memory-plugin, default-on, consent, third-party-inference, changelog-disclosure, open-source-code-verified]
---

## TL;DR
Since 15.2.0 (npm 2026-10-25), running `npx claude-mem install` on a machine without a completed setup opens a browser flow that reads the last 30 days of prompts from Claude Code, Codex, Gemini CLI, Antigravity CLI and OpenCode transcripts and uploads them, gzip-compressed, to the vendor's hosted service for "intent extraction"; the only checkbox on the screen is pre-ticked and, by the code's own comment, does not stop the upload. The project's changelog states this; its privacy wording, as quoted in the issue, says nothing leaves the device without cloud sync turned on. 15.5.0 (2026-10-29) still ships it. If you ran the installer, assume thirty days of everything you typed to those agents, including any pasted secrets, left the machine; rotate what you pasted and ask the vendor for deletion.

## What happened

**The report.** Issue #5176 on `thedotmack/claude-mem`, opened 2026-10-29 by saltenasl, says the installer's setup page scans local chat histories from five agents regardless of which tools the user selected, collects prompts from the last 30 days, and uploads prompt text with session ids, project names, folder paths and timestamps to the vendor's cloud. The upload starts when the page loads; the status text reads "Checking your AI usage" and does not mention upload; the one checkbox ("Help make claude-mem smarter for everyone with my anonymized setup results") is ticked by default and disabled during the upload. The author says the vendor confirmed by email that unticking it does not stop the upload, that the prompts were processed by a DeepSeek model through OpenRouter routed to the cheapest provider, and that the vendor's deletion covers its own records and not copies held by the routing provider or the model host. Those three statements are the author's account of the vendor's email and were not independently confirmed this run. No maintainer comment was on the issue when read. The related issue #4605 (2026-10-09, "Privacy statements contradict the shipped defaults", PostHog telemetry on by default) also had no maintainer reply; a contributor said on 10-24 that PR #4972 fixed the `SECURITY.md` part and that the marketplace consent gap remains.

**What the code says.** Read this run at commit d7c2da3 (v15.5.0):

- `src/services/prompt-import/setup-scan.ts`: the Scan step reads each supported agent's transcripts for the last 30 days (`AGENT_LABELS`: Claude Code, Codex, Gemini CLI, Antigravity CLI, OpenCode), stores the owner's typed prompts in the local database, and in the `uploading` phase passes them to the hosted extractor whenever one is configured. The `improveProduct` flag defaults to `true` in `idleState()`, and its comment reads "Optional improvement use only; false still runs the complete hosted extraction." The upload is not gated on the flag.
- `src/services/work-view/hosted-intent.ts`: posts a gzip JSON body with `ownerPrompts`, `improveProduct` and `timezoneOffsetMinutes` to `<origin>/api/pro/intent`, with install-credential headers and, when signed in, a bearer token and user id; it obtains an install credential from the same origin first; the body is capped at 2 MiB; no consent check is in the file. The origin is supplied by the caller, so the hostname is not in this file.

**What the changelog says.** 15.2.0 (2026-10-25): "Fresh installs now open a browser setup flow that finds your recent work"; the Reveal step "uploads the filtered owner prompts (gzip) to CMEM Cloud for hosted intent extraction"; "The pre-checked product-improvement box only changes `improveProduct`." 15.3.0 (10-26) adds install help saying which providers need a cmem.ai sign-in. 15.4.0 (10-28) and 15.5.0 (10-29) extend the My Work feature; neither changes the upload. The disclosure is therefore in the changelog, and not on the screen that performs it.

**Registry.** npm `claude-mem`: 15.2.0 published 2026-10-25 11:57 UTC, 15.2.1 the same day, 15.3.0 10-27, 15.4.0 10-28, 15.5.0 2026-10-29 00:55 UTC (newest when read); 23,869 downloads in the week 2026-10-21 to 10-27; 271 versions in total.

**Why it matters here.** Agent transcripts are where developers paste tokens, connection strings, customer data and the contents of files they are debugging. A plugin that reads five agents' histories and ships thirty days of them to a third party's inference pipeline on first run, under a checkbox that does not control it, is the upload-and-telemetry pattern this corpus tracks for coding tools, now inside a Claude Code memory plugin. The number of installs that completed the flow is not published.

## Am I affected?

```bash
npm ls -g claude-mem 2>/dev/null; npm ls claude-mem 2>/dev/null          # 15.2.0 or later; do not use npx here, it would fetch and run the package
ls -d ~/.claude/projects ~/.codex ~/.gemini ~/.config/opencode 2>/dev/null      # four of the five history locations the scan reads; the Antigravity CLI path was not read this run
```

- You are affected if you ran `npx claude-mem install` on 15.2.0 or later on a machine where setup had not been completed before, and the browser setup page opened. The issue says the upload begins on page load.
- A marketplace install that never opened the browser flow is a different path; the issue's claim is specific to the interactive installer.

## If you are affected

1. Treat the last 30 days of prompts to those five agents as disclosed. Rotate any key, token or password you typed or pasted into an agent session in that window: [credential hygiene](../prevention/credential-hygiene.md), [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
2. Request deletion from the vendor and ask which downstream providers received the data; the issue says the vendor could not identify the receiving provider.
3. Do not run the installer on a machine with agent histories until a release changes the default; the issue author's workaround is to block the vendor host before running it. This file does not print the host.
4. Review what the plugin's hooks record on every turn, since 15.x stores prompts locally and offers cloud sync.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): a prompt is a log; keep secrets out of it.
- [Package vetting checklist](../prevention/package-vetting-checklist.md): read a plugin's changelog and network code before an install that opens a browser.

## Sources
- [thedotmack/claude-mem — issue #5176: Installing claude-mem uploads your last 30 days of prompts to cmem.ai, no opt-in](https://github.com/thedotmack/claude-mem/issues/5176) — fetched 2026-10-29: opened 2026-10-29 by saltenasl, the claim, the agents scanned, the checkbox behaviour, the author's account of the vendor's email, the cited code paths, no maintainer response.
- [thedotmack/claude-mem — `src/services/prompt-import/setup-scan.ts` at d7c2da3](https://github.com/thedotmack/claude-mem/blob/d7c2da3/src/services/prompt-import/setup-scan.ts) — fetched 2026-10-29: the five agents, the 30-day window, `improveProduct` default `true`, the comment that `false` still runs the hosted extraction, the ungated upload.
- [thedotmack/claude-mem — `src/services/work-view/hosted-intent.ts` at d7c2da3](https://github.com/thedotmack/claude-mem/blob/d7c2da3/src/services/work-view/hosted-intent.ts) — fetched 2026-10-29: the `/api/pro/intent` endpoint, the gzip JSON fields, the credential headers, the 2 MiB cap, no consent check.
- [thedotmack/claude-mem — CHANGELOG.md](https://raw.githubusercontent.com/thedotmack/claude-mem/refs/heads/main/CHANGELOG.md) — fetched 2026-10-29: the 15.2.0 entry quoted above, the 15.3.0 cmem.ai sign-in line, the 15.4.0 and 15.5.0 entries.
- [thedotmack/claude-mem — issue #4605: Privacy statements contradict the shipped defaults](https://github.com/thedotmack/claude-mem/issues/4605) — fetched 2026-10-29: opened 2026-10-09, PostHog telemetry on by default, no maintainer reply, the 10-24 contributor comment.
- npm registry `time` for `claude-mem`, read 2026-10-29: 15.2.0 2026-10-25, 15.5.0 2026-10-29; 23,869 downloads 2026-10-21 to 10-27.
- Related in this corpus: [ZCode silent workspace and git-history upload](2026-09-zhipu-zcode-silent-workspace-git-history-upload.md) for the coding-tool upload pattern, and [infostealers targeting prompt histories](2026-09-infostealers-target-coding-agent-tokens-mcp-configs-prompt-histories.md) for why those files are a target.
