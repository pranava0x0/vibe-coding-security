---
id: 2026-10-claude-code-extension-2-1-313-cursor-marketplace-remove-and-rotate
title: "Harmful Claude Code extensions 2.1.312 and 2.1.313 from Cursor: check your installation and remove affected copies"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-10-30
severity: critical
status: contained
ecosystems: [vscode-extension, cursor-marketplace, npm, open-vsx]
tools_affected: ["Cursor users on macOS or Windows who installed or auto-updated anthropic.claude-code 2.1.312 or 2.1.313 from the Cursor Marketplace between about 02:27 and 13:35 PT on 2026-10-29", "machines holding SSH keys, cloud and provider keys, Git and registry tokens and environment-variable secrets that ran Cursor with that version"]
tags: [malicious-artifact, vscode-extension, cursor-marketplace, claude-code, ssh-backdoor, persistence, credential-theft, supply-chain, marketplace-compromise, auto-update, cursor-notice, no-vendor-statement]
---

## TL;DR
Remove the harmful copies of the Claude Code extension (`anthropic.claude-code` 2.1.312 or 2.1.313) supplied through Cursor's marketplace, and use 2.1.314 or later. If checks show the harmful code ran or added a way for someone else to log in, follow the cleanup steps below and replace passwords, keys and login tokens it could have accessed; a file or program name matching a search is not enough to show this happened.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Cursor Marketplace (VS Code extension) | `anthropic.claude-code` (listed under the Anthropic publisher name; Cursor says Anthropic did not develop it) | 2.1.312 and 2.1.313 (modified macOS/Windows copies) | remove; after any needed cleanup, install 2.1.314 or later | removed by Cursor on 2026-10-29 at about 13:35 PT; marketplace shut down, keys rotated, rebuilt and back online (Cursor notice, read 2026-10-30) | none read (no OSV or GHSA record for the extension) |
| npm | `@anthropic-ai/claude-code` | none | 2.1.314 (2026-10-30 00:12 UTC) is `latest` | `time` goes 2.1.312 (10-27) to 2.1.314 with no 2.1.313 entry and no unpublish marker (2026-10-30) | none |
| Open VSX | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:07 UTC) | the API returns "Extension not found" for 2.1.313 (2026-10-30) | none |
| Microsoft VS Marketplace | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:17 to 01:20 UTC, per platform) | 2,385 version rows, none 2.1.313 (2026-10-30) | none |

[Cursor's notice](https://cursor.com/blog/claude-code-extension-security-notice), updated 2026-10-30 at 11:30 PT, now lists modified **2.1.312 and 2.1.313** packages for macOS and Windows, adding 2.1.312 to its earlier warning. These copies were available from about 02:27–13:35 PT on 2026-10-29. Cursor has not found evidence that other versions or copies from the official sources were affected. The table records each download source separately: an official copy is not harmful just because it shares a version number with a modified copy from Cursor. The earlier notice reported at most 5,000 users; the updated notice no longer gives that count. OpenSourceMalware and Phorion published independent analyses. Phorion's claim that 2.1.313 was also pulled from npm and the Microsoft marketplace was not supported by the registry timelines read earlier on 2026-10-30.

## Am I affected?

**1. Check what you installed and where it came from.** Check whether Cursor downloaded an affected 2.1.312 or 2.1.313 copy during the times listed above. These commands list extension folders on your computer; installation and update records can help you or your agent check what was there before.

```bash
# macOS/Linux: list installed folders, including clean versions such as 2.1.314
ls -d ~/.cursor/extensions/anthropic.claude-code-* 2>/dev/null
```

```powershell
# Windows: list installed folders
Get-ChildItem "$env:USERPROFILE\.cursor\extensions" -Directory -Filter 'anthropic.claude-code-*' -ErrorAction SilentlyContinue
```

If you only ever had clean 2.1.314, seeing its folder in this list does **not** mean this incident affected you. If you updated to 2.1.314 after using an affected version, the update alone does not tell you whether cleanup is needed.

A folder name does not prove where a copy came from or whether it ran. If you saved the downloaded extension file (a `.vsix` file), compare its SHA-256 checksum—a value used to identify the exact file—with Cursor's published values for your version and operating system. A match identifies a harmful copy, but still does not prove it ran. Do not install or open a suspect copy just to check it.

**2. Look for warning signs, then check what they mean.** The commands below only read information. They look for files, saved remote-login keys, startup jobs and running programs mentioned in the reports. Other legitimate software can have the same names, so a search result alone does not mean your computer was affected.

```bash
# macOS/Linux: look for a key label and files mentioned in the reports
grep -n 'svc-telemetry' ~/.ssh/authorized_keys 2>/dev/null
ls -la ~/.config/.smt ~/.config/.smtk "${TMPDIR:-/tmp}"/.stk_* 2>/dev/null
# macOS: look for a startup job mentioned in the reports
ls -la ~/Library/LaunchAgents/com.apple.sysmond.plist 2>/dev/null
# Linux: list jobs set to run after a restart; these may be legitimate
crontab -l 2>/dev/null | grep -n '@reboot'
# macOS/Linux: find SSH programs; these may be legitimate remote connections
pgrep -fl 'autossh|ssh .* -R' 2>/dev/null
```

```powershell
Select-String -Path "$env:USERPROFILE\.ssh\authorized_keys","C:\ProgramData\ssh\administrators_authorized_keys" -Pattern 'svc-telemetry' -ErrorAction SilentlyContinue
Get-ScheduledTask -TaskName SysMon -ErrorAction SilentlyContinue
Get-ChildItem "$env:USERPROFILE\.config\smt.cmd","$env:USERPROFILE\.config\smtk","$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\sysmon.cmd" -ErrorAction SilentlyContinue
```

Cursor's current warning covers macOS and Windows copies. Researchers also listed Linux paths; finding those paths does not establish that Cursor distributed a harmful Linux copy.

**3. Check whether the harmful code ran or added remote access.** [Cursor's notice](https://cursor.com/blog/claude-code-extension-security-notice) lists the exact files, keys and connections to compare. You or someone helping you can check:

- **Remote-login keys:** compare the actual SSH key, or its identifying fingerprint, with Cursor's published key. The `svc-telemetry` label alone is not enough because labels can be changed. A matching, unauthorized key added to `authorized_keys`—the list of keys allowed to log in—supports a finding that unwanted remote access was set up. The same key merely stored inside a downloaded extension does not.
- **Startup jobs and files:** inspect what they contain and when they appeared without running them. Compare that information with the extension's installation history. A matching filename or an unrelated `@reboot` job is not enough.
- **Records of running programs and connections:** look for records showing the harmful code ran, or that it made connections matching Cursor's report. An ordinary SSH connection, or a visit to a service that tells you your public IP address, does not establish that.

Finding nothing does **not** prove the harmful code never ran. Changes meant to survive a restart may have failed or been removed, and older records may be missing. If you know an affected copy was installed but cannot tell whether it ran, remove it and ask for help; you can choose to replace exposed keys as a precaution without claiming that a break-in was confirmed.

## If you are affected

**You found an affected copy, but do not know whether it ran:** save its version, download source and any file checksum, then remove it. Follow the checks above or contact Cursor at `security@cursor.com`. A broad search result alone is not a reason to disconnect your computer, delete unrelated startup jobs or reinstall its operating system.

**Checks show the harmful code ran or added unwanted remote access:** follow these steps even if you have already updated the extension:

1. Disconnect the computer from the network. Save relevant installation, running-program and connection records before cleanup, if possible.
2. Follow Cursor's cleanup instructions for your operating system. Remove the unwanted login keys, startup jobs and connections it identifies, then uninstall the affected extension. Removing the extension alone may leave those changes behind; get help deciding whether the operating system should be reinstalled.
3. From another computer you trust, replace passwords, API keys and login tokens accessible from the affected computer, and sign out existing sessions. This is what security guides call **rotating credentials**. Include SSH keys, cloud and AI-provider API keys, GitHub and npm tokens, and secrets stored in environment variables (settings available to programs). See [cloud credential steps](../playbooks/rotating-cloud-credentials.md), [GitHub token steps](../playbooks/if-your-github-pat-leaked.md) and [npm token steps](../playbooks/if-your-npm-token-leaked.md).
4. After cleanup, install 2.1.314 or later from a source you have verified.

## Prevention

- Record the extension name, version and marketplace so you can check future warnings. Automatic updates can install a harmful copy without you choosing it that day. Consider reviewing extension updates before installing them on a computer with important account access; do not leave updates off indefinitely.
- Use the publisher's official download sources where your editor allows it. For this extension, the Open VSX and Microsoft marketplace copies are not known to be affected by this incident.
- Give coding agents access only to the account keys they need. See [how to store and limit account keys](../prevention/credential-hygiene.md) and [where risky downloads can enter a project](../prevention/supply-chain-attack-surface.md).

## Sources
- [Cursor — Claude Code extension security notice](https://cursor.com/blog/claude-code-extension-security-notice) — re-read 2026-10-30 after the 11:30 PT update: affected macOS/Windows marketplace copies now include 2.1.312 and 2.1.313; package hashes, SSH-key indicators, evidence-based isolation and remediation guidance. This supersedes the earlier 2.1.313-only scope and user count.
- [The Hacker News — Official Claude Code Extension on Cursor Marketplace Trojanized with Persistent SSH Backdoor](https://thehackernews.com/2026/10/official-claude-code-vs-code-extension.html) — fetched 2026-10-30: 2026-10-30, Ravie Lakshmanan, 2.1.314 published to Open VSX and the Microsoft marketplace, Open VSX and Microsoft installs not known to be affected, the `svc-telemetry` label, the OpenSourceMalware statement.
- [OpenSourceMalware — Trojanized Claude Code Extension Plants Persistent SSH Backdoor](https://opensourcemalware.com/blog/trojanized-claude-code-extension-plants-persistent-ssh-backdoor) — fetched 2026-10-30: 2026-10-30 09:42 UTC, the npm package, Open VSX and Microsoft extension stated as not malicious, "The provenance of the analyzed directory is not established", the later update naming the Cursor Marketplace as the origin, the file and process checks, "Rebuilding the host is safer", credit Dean Hardcastle.
- [Phorion — Compromised Claude Code for VS Code Extension](https://phorion.io/blog/offical-claude-code-vsx-compromise/) — fetched 2026-10-30: 2026-10-30, Calum Hall, the macOS, Linux and Windows persistence paths quoted above, the remediation list, the statement that Cursor pulled 2.1.313 from the npm and VS Code registries (not borne out by the registry timelines read this run).
- [Unite.AI — Cursor Discloses SSH Backdoor Attempt in Malicious Claude Code Extension](https://www.unite.ai/cursor-discloses-ssh-backdoor-attempt-in-malicious-claude-code-extension/) — fetched 2026-10-30: 2026-10-30, Cursor's statements quoted verbatim; no statement attributed to Anthropic.
- npm registry `@anthropic-ai/claude-code` `time` and `dist-tags`, queried 2026-10-30: 2.1.312 at 2026-10-27 18:36 UTC, 2.1.314 at 2026-10-30 00:12 UTC, no 2.1.313, `latest` 2.1.314.
- Open VSX API `open-vsx.org/api/anthropic/claude-code` and `/2.1.313`, queried 2026-10-30: newest 2.1.314 at 01:07 UTC; "Extension not found: anthropic.claude-code 2.1.313".
- Microsoft VS Marketplace `extensionquery` API, queried 2026-10-30: 2,385 version rows for `anthropic.claude-code`, newest 2.1.314 at 01:17 to 01:20 UTC, none 2.1.313.
- [Visual Studio Code 1.123 release notes](https://code.visualstudio.com/updates/v1_123) — fetched 2026-10-30: 2026-06-03, the two-hour delay and the trusted-publisher exemption quoted above.
- [Anthropic — News](https://www.anthropic.com/news) and [anthropics/claude-code — security advisories](https://github.com/anthropics/claude-code/security/advisories) — fetched 2026-10-30: no post or advisory about 2.1.313 or the Cursor Marketplace.
- Hacker News items 50301983 (title "Claude Code VS Code extension with backdoor released on Cursor marketplace", linking a Medium post whose URL says Anthropic was hacked; 393 points), 50300683 (Phorion, 163 points), 50301004 (Cursor notice) and 50300112 (OpenSourceMalware), read through the Algolia items API 2026-10-30 for titles, times and links; the Medium post was not opened.
