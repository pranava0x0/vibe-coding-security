---
id: 2026-09-shai-hulud-111-day-dormant-payload-mcp-package
title: "Shai-Hulud payload republished after 111 days — four unrelated npm packages including the MCP server feishu-docx-mcp pushed with the byte-identical @AntV Wave-C preinstall stealer (2026-09-07), with .claude/settings.json and .vscode/tasks.json persistence; a known hash walked through npm's publish-time malware scan"
date_disclosed: 2026-09-07
last_updated: 2026-09-17
severity: high
status: contained
ecosystems: [npm, mcp, claude-code, vscode]
tools_affected: [feishu-docx-mcp, bmc-i18n-extract-cli, blueai-cli, bmc-translate-utils, "Claude Code (.claude/settings.json persistence)", "VS Code (.vscode/tasks.json persistence)", "npm publish-time malware scanning"]
tags: [supply-chain, shai-hulud, mini-shai-hulud, worm, preinstall, bun, credential-theft, mcp, claude-code-persistence, vscode-tasks-persistence, dormant-payload, registry-scanning-gap]
---

## TL;DR
On **2026-09-07** a single npm account published, within one hour, new versions of four unrelated packages — **`feishu-docx-mcp@0.3.2`** (an MCP server for Feishu/Lark documents), **`bmc-i18n-extract-cli@1.1.1`**, **`blueai-cli@0.7.0`** and **`bmc-translate-utils@1.1.1`** — each carrying a root-level `index.js` with a `preinstall` script of **`bun run index.js`** whose **SHA-256 (`e37e3dde…b1a6`) is byte-identical to the Shai-Hulud "Wave C" payload from the 2026-05-19 @AntV compromise**, a payload Aikido had seen in **319 package versions, all on that one May day, and never since**. The stealer validates stolen npm tokens, downloads and re-injects tarballs, republishes infected versions, creates Dune-themed GitHub repositories, and writes persistence into **`.vscode/tasks.json`** and **`.claude/settings.json`** — the [ChainDrop](2026-08-keyv-mini-shai-hulud-npm-worm.md) lineage's hooks into the developer's editor and coding agent. npm replaced all four with the `0.0.1-security` holding package the same afternoon (the registry shows `0.3.2` published 09:25 UTC and `0.0.1-security` at 13:50 UTC), and GitHub's malware advisories followed. The gap that matters: npm's **July 2026 publish-time malware scanning** (a 5–15 minute hold before a version goes live) let a **known, already-fingerprinted** artifact through. A 111-day dormancy is the longest observed for this family — stolen tokens from May were still valid in September.

## What happened

**Discovery.** Aikido's malware triage queue flagged the four publications on 2026-09-07 because the preinstall file hash-matched the original @AntV payload exactly. Aikido's write-up ("A Shai-Hulud npm payload came back 111 days later") lays out the identity: same file, same `bun run index.js` preinstall, same behaviours — validate stolen npm tokens, pull tarballs of packages the token can publish, inject the payload, republish, create GitHub repositories with Dune-lexicon names — and the same two persistence writes, `.vscode/tasks.json` (VS Code runs it on folder open) and `.claude/settings.json` (Claude Code hooks). The packages are unrelated to each other and to @AntV; what they share is a publisher whose credential the May wave presumably captured and that no one rotated.

**Why an MCP server matters here.** `feishu-docx-mcp` is an MCP server. MCP servers are installed *by AI coding agents on the developer's instruction*, typically with `npx -y <name>` — a flow that never shows a lockfile, never pins a version, and runs lifecycle scripts by default. A poisoned MCP package is thus both a supply-chain payload (it runs at install) and, by construction, a tool the agent will trust afterward. This repo's [MCP stdio](2026-05-mcp-stdio-systemic-rce.md) and [Deadbugz](2026-09-deadbugz-mcp-supply-chain-campaign.md) entries cover malicious *behaviour* in MCP servers; this is the first tracked case of a legitimate MCP server's *npm release* being hijacked by the Shai-Hulud family. The registry data: `feishu-docx-mcp` had three real releases in March 2026 (0.2.0–0.2.2), nothing for six months, then 0.3.2 on 09-07 and the security placeholder four and a half hours later.

**The scanning gap.** npm introduced publish-time malware scanning in July 2026 — new versions are held briefly while automated checks run. Aikido's point, echoed by the secondary coverage, is that the file that got through was not a novel obfuscation but a **known hash**: a signature match is the minimum a scanner can do, and this one did not. Whatever the scan checks, it evidently did not include "is this exact file the one from the largest npm compromise of May." The four versions were live for a few hours — long enough for anyone with an unpinned `npx feishu-docx-mcp` in an agent config, or a CI job that resolved `latest`, to install them.

**Timeline (UTC, from the npm registry and Aikido):**
- 2026-05-19 — @AntV / `atool` compromise: 637 malicious versions across 317 packages in 22 minutes; the Wave-C payload hash first seen (319 versions carry it, all that day).
- 2026-09-07 09:25 — `feishu-docx-mcp@0.3.2` published; the other three within the hour.
- 2026-09-07 13:50 — npm replaces `feishu-docx-mcp` with `0.0.1-security` (dist-tag `latest` now points there); the other three are likewise replaced the same afternoon; GitHub malware advisories published.

**IOC (defender signal, from Aikido):** preinstall payload SHA-256 `e37e3ddeeaaa9e0c4fdbcb829b4895a6521031c80053fc436625b61e6ee5b1a6`; a root `index.js` invoked via `bun run index.js` in `preinstall`; new or modified `.vscode/tasks.json` / `.claude/settings.json` in any project after an install. No C2 infrastructure is reproduced here.

**Sourcing.** Aikido is the sole research source; the npm registry's own replacement of the versions with the security-holder package (and the resulting `latest` dist-tag) is the registry's independent record of the takedown, per this repo's rule that the registry's post-incident action counts as the second source. Secondary coverage (SourceTrail, CyberPress, daily.dev) restates Aikido. Status `contained`: the versions are gone; the token that published them, and any tokens the stealer took in its few hours live, are the residual risk.

## Am I affected?

```bash
# Did any of the four land in a lockfile, cache or agent config?
grep -rn 'feishu-docx-mcp\|bmc-i18n-extract-cli\|blueai-cli\|bmc-translate-utils' package-lock.json pnpm-lock.yaml yarn.lock \
  ~/.claude.json .mcp.json ~/.cursor/mcp.json ~/.kiro/settings/mcp.json 2>/dev/null
ls ~/.npm/_npx/*/node_modules 2>/dev/null | grep -E 'feishu-docx-mcp|bmc-i18n-extract-cli|blueai-cli|bmc-translate-utils'
# The payload hash, anywhere under node_modules or the npx cache
find . ~/.npm/_npx -name index.js -path '*node_modules*' 2>/dev/null | xargs -I{} sh -c 'sha256sum "{}"' 2>/dev/null \
  | grep -i e37e3ddeeaaa9e0c4fdbcb829b4895a6521031c80053fc436625b61e6ee5b1a6
# Persistence writes since 2026-09-07
find . -path '*/.vscode/tasks.json' -newermt 2026-09-07 2>/dev/null; find . -path '*/.claude/settings.json' -newermt 2026-09-07 2>/dev/null
```

You are affected if you installed `feishu-docx-mcp@0.3.2`, `bmc-i18n-extract-cli@1.1.1`, `blueai-cli@0.7.0` or `bmc-translate-utils@1.1.1` between roughly 09:25 and 14:00 UTC on 2026-09-07 with lifecycle scripts enabled (the npm default; `npx -y` counts), and Bun was present or installable on the host.

## If you are affected

1. Stop the agent/IDE session; remove the package and the npx cache entry; delete any `.vscode/tasks.json` / `.claude/settings.json` you did not write. → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md)
2. From a clean machine, **rotate npm tokens, GitHub tokens, cloud credentials and SSH keys** — the payload's first act is to validate and use npm tokens to republish. → [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
3. Check every package you can publish for versions you did not release, and your GitHub account for repositories with Dune-themed names. → [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
4. If the MCP server was configured in an agent, treat it as a malicious MCP server for the window. → [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md)

## Prevention

- → [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `ignore-scripts=true` by default; `--ignore-scripts` on `npx`; a minimum-release-age policy (the four packages were minutes old when they were installable).
- → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — pin MCP servers to exact versions in agent config (`npx -y feishu-docx-mcp@0.2.2`, not `npx -y feishu-docx-mcp`), and prefer servers you vendor or run from a reviewed checkout.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — if you were anywhere near the May wave, assume the token is still out there; granular, short-lived npm tokens with 2FA-required publishing end this family's replay loop.

## Sources

- [Aikido Security — A Shai-Hulud npm payload came back 111 days later](https://www.aikido.dev/blog/shai-hulud-npm-resurfaces) — fetched 2026-09-17; primary: published 2026-09-07, the four package@version pairs, the `bun run index.js` preinstall, the SHA-256 match to the @AntV Wave-C payload (319 versions, all 2026-05-19), the `.vscode/tasks.json` / `.claude/settings.json` persistence, the publish-time-scan observation.
- [npm registry — `feishu-docx-mcp` package document](https://registry.npmjs.org/feishu-docx-mcp) — fetched 2026-09-17; `time` field: 0.2.0–0.2.2 (2026-03-19/20), **0.3.2 at 2026-09-07T09:25:00Z**, **0.0.1-security at 2026-09-07T13:50:30Z**; `dist-tags.latest = 0.0.1-security` (npm security-holder placeholder).
- [Mini Shai-Hulud — the 2026-05-19 @AntV/atool wave](2026-05-mini-shai-hulud-may19-wave.md) and [ChainDrop / keyv](2026-08-keyv-mini-shai-hulud-npm-worm.md) — this repo's entries for the origin payload and the lineage's editor/agent persistence hooks.
