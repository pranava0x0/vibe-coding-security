---
id: 2026-10-yoba-fake-gpt-claude-desktop-apps-github-releases-remove-and-rotate
title: "Fake GPT-5.6 Sol, GPT-6 Astra and Claude Opus Windows apps on GitHub: remove the WMProcess folder and scheduled task, rotate keys"
kind: malicious-artifact
date_disclosed: 2026-10-27
last_updated: 2026-10-29
severity: high
status: unconfirmed
ecosystems: [github-releases, windows, desktop-apps]
tools_affected: ["Windows developers who downloaded a ChatGPT or Claude desktop app from a GitHub project or GitHub Pages site rather than from OpenAI's or Anthropic's own download pages", "machines holding OpenAI, Anthropic or other provider keys, cloud credentials and browser sessions that ran such an archive"]
tags: [malicious-artifact, fake-installer, seo-poisoning, github-releases, dll-sideloading-class, cryptominer, chatgpt-lure, claude-lure, check-point, single-firm]
---

## TL;DR
Remove any "GPT-5.6 Sol", "GPT-6 Astra" or "Claude Opus" desktop app that came from a GitHub project, a GitHub Pages site or a search result rather than from `openai.com` or `claude.com`, delete the `WMProcess` folder under `ProgramData` and the scheduled task that launches it, and reinstall the real client from the vendor. Rotate every API key, cloud credential and browser-held session the machine had while the archive was present, and run an endpoint scan; Check Point's write-up is the behaviour reference.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub releases (Windows ZIP) | `GPT-5.6 Sol` fake desktop app | every release (first repository created around 2026-07, releases from late 2026-08, per THN citing Check Point) | remove; the only clean client is OpenAI's own download page | GitHub projects and Pages sites; takedown status not stated by either source (2026-10-29) | none (GitHub-hosted, no registry record) |
| GitHub releases (Windows ZIP) | `GPT-6 Astra` fake desktop app | every release | remove; install from OpenAI's download page | as above (2026-10-29) | none |
| GitHub releases (Windows ZIP) | `Claude Opus` fake desktop app | every release | remove; the only clean client is Anthropic's download page at `claude.com/download` | as above (2026-10-29) | none |

The archives pair a genuine signed OpenAI or Anthropic executable, renamed `Setup.exe`, with a malicious `winmm.dll` beside it, so a valid signature on `Setup.exe` does not mean the download is clean. The campaign is Windows-only. Check Point Research (2026-10-27) is the single firm reporting it; The Hacker News (2026-10-29) is coverage of that report, so the status is `unconfirmed` until a second firm, GitHub or a vendor speaks.

## Am I affected?

- You installed a "ChatGPT" or "Claude" desktop app from a GitHub repository, a `github.io` page or a search ad, on Windows, since about August 2026. The official clients come only from `openai.com` and `claude.com`.
- Check for the artifacts Check Point and THN name:

```powershell
Get-ChildItem "$env:ProgramData\WMProcess" -ErrorAction SilentlyContinue
Get-ScheduledTask | Where-Object { $_.Actions.Execute -like "*WMProcess*" -or $_.Actions.Execute -like "*wmpdmc*" }
Get-ChildItem -Path $env:USERPROFILE\Downloads -Recurse -Include Setup.exe,winmm.dll -ErrorAction SilentlyContinue | Where-Object { $_.Directory.Name -match "GPT|Claude|Sol|Astra|Opus" }
```

- A `WMProcess` folder under `ProgramData` holding a copy of a Windows Media component next to DLLs, or a scheduled task that launches from it, is the installed state. A folder with `Setup.exe` beside `winmm.dll` in a download is the archive.

## If you are affected

1. Delete the scheduled task and the `ProgramData\WMProcess` folder, remove the downloaded archive and its extracted folder, and run a full endpoint scan; Check Point says to treat the infection as a broader compromise, not only a miner.
2. Rotate from a clean machine: OpenAI, Anthropic and other provider API keys, cloud credentials, GitHub and npm tokens, and sign out every browser session that was open on the machine: [credential hygiene](../prevention/credential-hygiene.md), [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
3. Reinstall the client from the vendor's download page and check the publisher name in the installer's signature dialog against the site you downloaded from, not only that a signature exists.
4. Watch for sustained CPU use after the clean-up; the observed payload was a miner, and a loader can deliver anything else.

## Prevention

- [Package vetting checklist](../prevention/package-vetting-checklist.md): a vendor's product on a stranger's GitHub repository is not the vendor's product; a signed binary beside an unsigned DLL is the archive to refuse.
- [Credential hygiene](../prevention/credential-hygiene.md): keys on a developer machine are what a fake installer collects.

## Sources
- [Check Point Research — Yoba Malware Abuses Signed ChatGPT and Claude Binaries to Target AI Users](https://blog.checkpoint.com/research/yoba-malware-abuses-signed-chatgpt-and-claude-binaries-to-target-ai-users) — fetched 2026-10-29 (2026-10-27): the three fake project names, GitHub projects and Pages sites with ZIP releases, Windows, the signed `Setup.exe` beside `winmm.dll`, a scheduled task for persistence, the recommendations; the write-up carries the behaviour this file leaves out.
- [The Hacker News — Fake ChatGPT and Claude Apps Abuse Signed Executables to Deploy Crypto Miners](https://thehackernews.com/2026/10/fake-chatgpt-and-claude-apps-abuse.html) — fetched 2026-10-29 (Ravie Lakshmanan): the campaign dates (first repository around July 2026, releases late August), the `WMProcess` folder under `ProgramData` and the scheduled task, the SEO-poisoning distribution, the renamed OpenAI Codex or Anthropic Claude executable, the Windows Media component abused for the second stage.
- Related in this corpus: [an earlier fake AI desktop-app lure](2026-10-yoba-fake-gpt-claude-desktop-apps-github-releases-remove-and-rotate.md).
