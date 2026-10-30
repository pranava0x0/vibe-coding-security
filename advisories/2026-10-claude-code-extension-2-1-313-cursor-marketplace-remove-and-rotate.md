---
id: 2026-10-claude-code-extension-2-1-313-cursor-marketplace-remove-and-rotate
title: "Malicious anthropic.claude-code 2.1.312 and 2.1.313 on the Cursor Marketplace: remove affected copies; rotate credentials if executed"
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
Remove affected Cursor Marketplace copies of `anthropic.claude-code` 2.1.312 or 2.1.313 and replace them with 2.1.314 or later; check the version, source and installation history below. If there is evidence of payload execution or backdoor installation, follow the cleanup guidance and rotate accessible credentials and sessions from a trusted machine; an inventory or generic hunting match alone does not confirm execution.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Cursor Marketplace (VS Code extension) | `anthropic.claude-code` (listed under the Anthropic publisher name; Cursor says Anthropic did not develop it) | 2.1.312 and 2.1.313 (modified macOS/Windows copies) | remove; after the host is cleaned, install 2.1.314 or later | removed by Cursor on 2026-10-29 at about 13:35 PT; marketplace shut down, keys rotated, rebuilt and back online (Cursor notice, read 2026-10-30) | none read (no OSV or GHSA record for the extension) |
| npm | `@anthropic-ai/claude-code` | none | 2.1.314 (2026-10-30 00:12 UTC) is `latest` | `time` goes 2.1.312 (10-27) to 2.1.314 with no 2.1.313 entry and no unpublish marker (2026-10-30) | none |
| Open VSX | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:07 UTC) | the API returns "Extension not found" for 2.1.313 (2026-10-30) | none |
| Microsoft VS Marketplace | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:17 to 01:20 UTC, per platform) | 2,385 version rows, none 2.1.313 (2026-10-30) | none |

[Cursor's notice](https://cursor.com/blog/claude-code-extension-security-notice), updated 2026-10-30 at 11:30 PT, now lists modified **2.1.312 and 2.1.313** packages for macOS and Windows, expanding the initial 2.1.313-only scope. The distribution window remains about 02:27–13:35 PT on 2026-10-29. Cursor reports no evidence that other versions or the official distribution are affected. The registry observations above concern those separate channels; a version number shared with a compromised marketplace copy does not make the official package malicious. The earlier notice reported at most 5,000 users; the updated notice no longer gives that count. OpenSourceMalware and Phorion published independent analyses. Phorion's claim that 2.1.313 was also pulled from npm and the Microsoft marketplace was not supported by the registry timelines read earlier on 2026-10-30.

## Am I affected?

**1. Inventory — identify the version and distribution channel.** Check whether Cursor installed or updated to a modified 2.1.312 or 2.1.313 copy from its marketplace during the window above. Current directories are only an inventory; use extension-installation/update logs or retained package records to check earlier versions and their source.

```bash
# macOS/Linux: inventory only; this also lists clean versions such as 2.1.314
ls -d ~/.cursor/extensions/anthropic.claude-code-* 2>/dev/null
```

```powershell
# Windows: inventory only
Get-ChildItem "$env:USERPROFILE\.cursor\extensions" -Directory -Filter 'anthropic.claude-code-*' -ErrorAction SilentlyContinue
```

A machine that only ever had clean 2.1.314 is not affected by this incident solely because that directory matches. Conversely, 2.1.314 installed now does not rule out an earlier affected version. A directory name alone does not establish package provenance or execution. Compare a retained VSIX with the platform-specific SHA-256 values in Cursor's **Package version 2.1.312 / 2.1.313** indicator sections: a matching hash identifies the malicious package, not whether it ran. Do not install or launch a suspect copy to check it.

**2. Hunting leads — investigate matches before drawing conclusions.** These read-only checks find candidate files, key comments, tasks and processes. Legitimate software can use the same names; unrelated reboot jobs and SSH tunnels are not evidence of this incident.

```bash
# macOS/Linux: key comment and candidate helper files; corroborate below
grep -n 'svc-telemetry' ~/.ssh/authorized_keys 2>/dev/null
ls -la ~/.config/.smt ~/.config/.smtk "${TMPDIR:-/tmp}"/.stk_* 2>/dev/null
# macOS: candidate LaunchAgent
ls -la ~/Library/LaunchAgents/com.apple.sysmond.plist 2>/dev/null
# Linux: broad reboot-job discovery, including legitimate jobs
crontab -l 2>/dev/null | grep -n '@reboot'
# macOS/Linux: broad process discovery, including legitimate tunnels
pgrep -fl 'autossh|ssh .* -R' 2>/dev/null
```

```powershell
Select-String -Path "$env:USERPROFILE\.ssh\authorized_keys","C:\ProgramData\ssh\administrators_authorized_keys" -Pattern 'svc-telemetry' -ErrorAction SilentlyContinue
Get-ScheduledTask -TaskName SysMon -ErrorAction SilentlyContinue
Get-ChildItem "$env:USERPROFILE\.config\smt.cmd","$env:USERPROFILE\.config\smtk","$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\sysmon.cmd" -ErrorAction SilentlyContinue
```

Cursor currently scopes the compromised marketplace packages to macOS and Windows; the Linux paths remain research leads from the published analyses, not confirmation of a distributed Linux package.

**3. Corroborate — distinguish a package match from execution or backdoor evidence.** Use [Cursor's indicators](https://cursor.com/blog/claude-code-extension-security-notice) to compare the actual SSH public key or its fingerprint, not just the editable `svc-telemetry` comment. An unauthorized key matching the vendor's key in an authorization file supports backdoor installation; a matching key stored only inside an unexecuted package does not. Inspect candidate persistence files and task actions without running them, and correlate their contents and timestamps with extension-installation records, endpoint process history and network logs. Payload execution can be supported by endpoint records showing the identified payload running or process-linked connections matching the vendor's network indicators. A generic cron job, process name, filename or connection to a public-IP lookup service alone is insufficient.

No matches do **not** rule out earlier execution: persistence may fail, be removed or leave no retained logs. A failed SSH-service setup also does not prove nothing ran. If you establish an affected installation but cannot determine execution, remove the affected copy and seek help assessing exposure; precautionary credential rotation is an option, not proof of compromise.

## If you are affected

- **Affected package present, execution unconfirmed:** preserve installation/version details and any retained package hash, remove the affected marketplace copy, and investigate the leads above. Do not disconnect, delete unrelated jobs or rebuild solely because an inventory or generic hunting check matched. If evidence remains inconclusive, contact Cursor at `security@cursor.com`.
- **Evidence of payload execution or backdoor installation:** follow these steps, even if persistence failed or the extension has already been upgraded:

1. Isolate the host and preserve relevant process, SSH, installation and network records before cleanup.
2. Follow Cursor's platform-specific remediation guidance to remove confirmed unauthorized keys, persistence and running tunnels, then uninstall the affected extension. Uninstalling alone may leave artifacts behind; assess whether the host needs rebuilding.
3. From a trusted machine, rotate credentials and sessions accessible from that host: SSH keys, cloud and provider API keys, GitHub and npm tokens, and environment secrets. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md).
4. After cleanup, install 2.1.314 or later from a verified distribution channel.

## Prevention

- Extension auto-update can deliver a compromised copy without a manual install; record the version and marketplace used. VS Code 1.123 (2026-06-03) delays automatic extension updates by two hours, but "This delay does not apply to extensions from trusted publishers such as Microsoft, GitHub, and OpenAI"; whether Cursor's marketplace applies any delay is not stated in its notice. Consider turning automatic extension updates off on machines that hold production credentials and updating on a schedule you control.
- Prefer the extension vendor's own channel (Open VSX or the Microsoft marketplace for this extension) where the editor allows it, and know which marketplace your editor resolves against.
- Keep fewer long-lived credentials on the workstation that runs the agent, and treat `authorized_keys` as a file to monitor: [credential hygiene](../prevention/credential-hygiene.md), [supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

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
