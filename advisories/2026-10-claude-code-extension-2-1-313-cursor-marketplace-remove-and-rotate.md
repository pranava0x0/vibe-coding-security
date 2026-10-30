---
id: 2026-10-claude-code-extension-2-1-313-cursor-marketplace-remove-and-rotate
title: "Malicious anthropic.claude-code 2.1.313 on the Cursor Marketplace: remove it, remove the added SSH key and persistence, rotate credentials"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-10-30
severity: critical
status: contained
ecosystems: [vscode-extension, cursor-marketplace, npm, open-vsx]
tools_affected: ["Cursor users who installed or auto-updated the Claude Code extension (anthropic.claude-code) from the Cursor Marketplace between about 02:27 and 13:35 PT on 2026-10-29 (at most 5,000 users, per Cursor)", "machines holding SSH keys, cloud and provider keys, Git and registry tokens and environment-variable secrets that ran Cursor with that version"]
tags: [malicious-artifact, vscode-extension, cursor-marketplace, claude-code, ssh-backdoor, persistence, credential-theft, supply-chain, marketplace-compromise, auto-update, cursor-notice, no-vendor-statement]
---

## TL;DR
Remove `anthropic.claude-code` 2.1.313 if Cursor installed it from the Cursor Marketplace on 2026-10-29, then remove the SSH key it added to `authorized_keys` and the LaunchAgent, scheduled task, cron entry and helper files it left, because uninstalling the extension alone leaves them in place. From a clean machine, rotate SSH keys, cloud and provider API keys, Git and registry tokens and every secret that was in the environment, and update to 2.1.314 or later.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Cursor Marketplace (VS Code extension) | `anthropic.claude-code` (listed under the Anthropic publisher name; Cursor says Anthropic did not develop it) | 2.1.313 | remove; after the host is cleaned, install 2.1.314 or later | removed by Cursor on 2026-10-29 at about 13:35 PT; marketplace shut down, keys rotated, rebuilt and back online (Cursor notice, read 2026-10-30) | none read (no OSV or GHSA record for the extension) |
| npm | `@anthropic-ai/claude-code` | none | 2.1.314 (2026-10-30 00:12 UTC) is `latest` | `time` goes 2.1.312 (10-27) to 2.1.314 with no 2.1.313 entry and no unpublish marker (2026-10-30) | none |
| Open VSX | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:07 UTC) | the API returns "Extension not found" for 2.1.313 (2026-10-30) | none |
| Microsoft VS Marketplace | `anthropic.claude-code` | none | 2.1.314 (2026-10-30 01:17 to 01:20 UTC, per platform) | 2,385 version rows, none 2.1.313 (2026-10-30) | none |

Cursor's notice is the only vendor statement: at most 5,000 users, a window of about 02:27 to 13:35 PT on 2026-10-29, "This malicious version of the extension was not developed by Anthropic", no evidence that other versions or the official distribution are affected, and no account of how the version was published. Anthropic had published nothing on its news page, its status page or the Claude Code advisories tab when read on 2026-10-30; the most-voted Hacker News item on the story carried a title saying Anthropic itself was hacked, and nothing read this run supports or refutes that beyond the registry facts above. OpenSourceMalware (Jenn Gile, Paul McCarty; credit to Dean Hardcastle) and Phorion (Calum Hall) published the independent analyses; Phorion wrote that 2.1.313 was pulled from the npm and VS Code registries too, which the registry timelines above do not show.

## Am I affected?

- You use Cursor, the Claude Code extension was installed or updated through Cursor's marketplace, and its version was 2.1.313 at any point on 2026-10-29. Open VSX and Microsoft VS Marketplace installs are not known to be affected.

```bash
# installed extension versions (Cursor's extension directory; the path varies by editor)
ls -d ~/.cursor/extensions/anthropic.claude-code-* 2>/dev/null
# the added key is labelled svc-telemetry in every published analysis
grep -n 'svc-telemetry' ~/.ssh/authorized_keys 2>/dev/null
# persistence and helper files named by Phorion and Cursor
ls -la ~/Library/LaunchAgents/com.apple.sysmond.plist ~/.config/.smt ~/.config/.smtk "${TMPDIR:-/tmp}"/.stk_* 2>/dev/null   # macOS
crontab -l 2>/dev/null | grep -n '@reboot'; ls -la ~/.config/.smt ~/.config/.smtk 2>/dev/null                              # Linux
pgrep -af 'autossh|ssh .* -R' 2>/dev/null                                                                                  # a long-running reverse tunnel
```

```powershell
Get-ScheduledTask -TaskName SysMon -ErrorAction SilentlyContinue
Get-ChildItem "$env:USERPROFILE\.config\smt.cmd","$env:USERPROFILE\.config\smtk","$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup\sysmon.cmd" -ErrorAction SilentlyContinue
```

- Any hit means the version ran. Cursor's notice says the persistence step needs no administrator rights on macOS and may fail without them on some systems; the absence of persistence does not prove the collection step did not run.

## If you are affected

1. Disconnect the machine and preserve what you can (process list, `authorized_keys`, the files above, shell and SSH logs) before deleting anything.
2. Run Cursor's platform-specific remediation (its notice carries check and clean-up scripts for macOS and Windows): remove the key from `authorized_keys`, the LaunchAgent or scheduled task and Startup script or cron entry, the helper files and any running tunnel. Then uninstall 2.1.313. Both OpenSourceMalware and Cursor say rebuilding the host is the safer outcome.
3. From a machine that did not run the version, rotate: SSH keys whose private halves were on the host, cloud provider keys, OpenAI, Anthropic and other provider API keys, GitHub and npm tokens, anything that was in environment variables, and active sessions. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md).
4. Reinstall 2.1.314 or later. Cursor says it will contact affected users and takes questions at `security@cursor.com`.

## Prevention

- Extension auto-update is the delivery path: an eleven-hour window reached up to 5,000 users with no action on their part. VS Code 1.123 (2026-06-03) delays automatic extension updates by two hours, but "This delay does not apply to extensions from trusted publishers such as Microsoft, GitHub, and OpenAI"; whether Cursor's marketplace applies any delay is not stated in its notice. Consider turning automatic extension updates off on machines that hold production credentials and updating on a schedule you control.
- Prefer the extension vendor's own channel (Open VSX or the Microsoft marketplace for this extension) where the editor allows it, and know which marketplace your editor resolves against.
- Keep fewer long-lived credentials on the workstation that runs the agent, and treat `authorized_keys` as a file to monitor: [credential hygiene](../prevention/credential-hygiene.md), [supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources
- [Cursor — Security notice: malicious version of Anthropic.claude-code (2.1.313) identified in the Cursor Extension Marketplace](https://cursor.com/blog/claude-code-extension-security-notice) — fetched 2026-10-30: 2026-10-29, the window, "at most 5,000 users", "not developed by Anthropic", removal, marketplace shutdown and rebuild, key rotation, "uninstalling the extension may not be sufficient", the check and remediation scripts, the indicator sections, `security@cursor.com`. Vendor primary for the marketplace; it does not say how the version was published.
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
