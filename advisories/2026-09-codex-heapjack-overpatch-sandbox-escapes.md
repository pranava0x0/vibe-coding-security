---
id: 2026-09-codex-heapjack-overpatch-sandbox-escapes
title: "Heapjack and Overpatch — two OpenAI Codex sandbox escapes: Codex Desktop's JavaScript sandbox kept its trust token in the same V8 heap as untrusted code (read-only mode → host commands), and Codex CLI's apply_patch granted write access to the parent directory of any path in a patch (workspace-write → ~/.zshrc); fixed 0.149.0 / build 26.818.21641, no CVE, no advisory"
date_disclosed: 2026-09-15
last_updated: 2026-09-20
severity: high
status: patched
ecosystems: [codex, openai, npm, macos, linux]
tools_affected: ["OpenAI Codex CLI < 0.149.0 (@openai/codex)", "OpenAI Codex Desktop builds before 26.818.21641", "any CI or automation that runs Codex against repositories it did not author"]
tags: [sandbox-escape, coding-agent, codex, symlink, apply-patch, heap-snapshot, silent-patch, no-cve, agent-sandboxing]
---

## TL;DR
Accomplish AI (Oren Yomtov — the researcher behind the Docker Sandboxes and Claude Cowork escapes) published on **2026-09-15** two ways out of the OpenAI Codex sandbox, both reported **2026-08-12** and both fixed by **2026-08-20**. **Overpatch** (Codex CLI): the `apply_patch` tool derived *write permission* from the paths named in the patch — including their parent directories — so a patch that mentioned `/tmp` unlocked the whole filesystem, and a second entry through a symlink appended a line to `$HOME/.zshrc` that ran on the next terminal open, from inside `workspace-write` mode. **Heapjack** (Codex Desktop): the `node_repl` JavaScript sandbox told trusted and untrusted code apart with a token that lived in the **same V8 heap** as the untrusted code; a heap snapshot recovered it, and forged requests to the native parent process ran unsandboxed commands — in the strictest `read-only` mode, triggered by having Codex analyse a malicious repository. Fixed in **Codex CLI 0.149.0** (npm 2026-08-20; release note: "Prevent `apply_patch` from widening write permissions") and **Codex Desktop build 26.818.21641**. No CVE, no entry on Codex's advisory tab (still 2025-09-19), no bounty stated; BleepingComputer covered it on 2026-09-20. Yomtov's one-line diagnosis: "The thing doing the enforcement was sitting inside the thing being enforced."

## What happened

**Overpatch — Codex CLI (`@openai/codex` < 0.149.0).** Codex's `apply_patch` tool is how the model edits files. Per Accomplish, the tool "granted write permissions to parent directories of any specified paths": name a path in a patch and its parent directory became writable for that operation. A patch that referenced a file under `/tmp` therefore obtained write access to `/`, and a second patch entry that went through a symlink wrote to `$HOME/.zshrc` — "executing arbitrary commands on the next terminal session, even in restricted `workspace-write` mode." The sandbox mode a user chose was being widened by the content of the patch the model (or whatever poisoned the model) produced.

**Heapjack — Codex Desktop (builds before 26.818.21641).** Codex Desktop's `node_repl` component runs trusted and untrusted JavaScript in separate contexts, but in one Node process sharing one heap. The sandbox "relied on a token stored in shared V8 heap memory to distinguish trusted from untrusted code contexts." As BleepingComputer summarises Yomtov: "Both contexts live in one Node process and share one memory heap, so the token is just a string sitting in memory the untrusted side can read." Untrusted code took a heap snapshot, extracted the token, and forged requests to the native parent process — "gaining unsandboxed command execution." This "worked in the strictest `read-only` mode where writes supposedly weren't permitted," and the trigger was ordinary: Codex analysing a repository that carried the payload.

**Disclosure and fix.** Both flaws were reported to OpenAI on **2026-08-12** and "resolved both issues within eight days" (Accomplish; BleepingComputer). The Codex CLI fix shipped as **0.149.0**, whose GitHub release (dated 20 Aug) lists "Prevent `apply_patch` from widening write permissions" among a run of hardening lines — "Reject symbolic links in memory workspaces," "Harden skill installation against unsafe symlinks," "Prevent Noise auth tokens from reaching child processes," "Drop capabilities from Linux sandbox processes," "Enforce filesystem permissions when loading AGENTS.md," "Harden Windows sandbox provisioning against reparse points," "Isolate IPC in Bubblewrap sandboxes." The npm registry's `time` field puts `0.149.0` at **2026-08-20T21:09 UTC**. The Desktop fix is build **26.818.21641**. Neither fix carries a CVE; the `openai/codex` security-advisories tab still shows a single 2025-09-19 entry, so — as with [Plugin4Shell](2026-09-plugin4shell-sha-pin-bypass-coding-agent-plugins.md) (fixed 0.146.0, release-note only) — the record of this fix is a release-note line and the researcher's blog. BleepingComputer (Ax Sharma, 2026-09-20) "reached out to OpenAI for comment prior to publishing"; no OpenAI statement is quoted, and no bounty is mentioned by either source.

**Why this is the same story as the last three.** This is the third sandbox this researcher has walked out of in three months, and the third with the same shape: [Claude Cowork's SharedRoot](2026-07-sharedroot-claude-cowork-macos-vm-escape.md) (VM shares a root the guest can reach), [Docker Sandboxes](2026-09-docker-sandboxes-virtiofs-symlink-host-escape.md) (host follows a guest's symlink), and now Codex — where the *enforcement state* (a permission set, a trust token) lived inside the thing being sandboxed. Combine it with the September Codex CVE batch tracked in [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md) (a repo's `.git/config` runs code before any prompt; a PowerShell `--%` parser bug lets a repo trigger file-writing git commands without approval) and the practical reading for Codex users is: **a repository you open is input to the sandbox, and until 0.149.0 the sandbox's own boundary was one of the things that input could edit.** `@openai/codex` pulled ~15.6 million downloads in the week to 2026-09-19, so the pre-fix population was large; the exposure window for anyone who did not update is 2026-08-12 → whenever they upgraded.

## Am I affected?

```bash
# Codex CLI: anything below 0.149.0 is affected (Overpatch)
codex --version
npm ls -g @openai/codex 2>/dev/null | grep codex
# Registry's current release, for comparison
npm view @openai/codex version

# Codex Desktop: About / settings → build number. Anything before 26.818.21641 is affected (Heapjack).

# Did a session before the fix touch your shell startup? Unexpected trailing lines are the Overpatch signal.
tail -n 5 ~/.zshrc ~/.bashrc ~/.profile ~/.zprofile 2>/dev/null
ls -la ~/.zshrc ~/.bashrc 2>/dev/null   # modification time vs your last Codex run on an untrusted repo
# Symlinks inside a workspace that point at $HOME are the Overpatch ingredient
find . -maxdepth 3 -type l -lname "$HOME*" 2>/dev/null
```

- **Affected if:** you ran Codex CLI < 0.149.0 or Codex Desktop < 26.818.21641 against a repository, PR, or package you did not author between the flaw's existence and your upgrade. Heapjack needed no writable mode at all — `read-only` was enough — so "I only used read-only mode on that repo" is not an exclusion.
- **Not affected if:** you were on ≥ 0.149.0 / ≥ 26.818.21641 before opening untrusted content, or you only ever run Codex inside an outer boundary (a container or microVM with no host credentials) and treat that as the real sandbox.
- **No exploitation in the wild is reported** by either source; there is no vendor advisory to check for IOCs.

## If you are affected

1. Update: `npm i -g @openai/codex@latest` (or the Desktop updater) — nothing below 0.149.0 / 26.818.21641 is safe against these two.
2. If a pre-fix Codex session opened an untrusted repo, follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md): diff your shell startup files and `~/.config`, look for new launch agents / cron entries, and rotate whatever a shell running as you could read — GitHub tokens, cloud keys, SSH keys, the OpenAI/Codex session itself ([rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)).
3. If Codex runs in CI or on shared hosts, treat those runners' secrets the same way; a `.zshrc` write is an interactive-host primitive, but the heap-token path gave direct command execution wherever Desktop ran.

## Prevention

- **The agent's sandbox is a mitigation; put a boundary it cannot edit beneath it** — a container or microVM with no host credentials mounted, per [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md). Every escape in this file worked because the enforcement state lived inside the enforced process.
- **Keep AI coding tools on `latest`.** This fix, Plugin4Shell's (0.146.0) and the GitSpawn CVEs were all shipped as release-note lines with no advisory; pinning an old Codex pins undisclosed holes.
- **Treat a repository you open as input**, and run first contact in clone mode / read-only with the outer boundary on — [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- Watch the researcher's channel, not only the vendor's: Accomplish's three escapes (Claude Cowork, Docker Sandboxes, Codex) each appeared on its blog before any advisory or outlet.

## Sources
- [Accomplish AI — Escaping the OpenAI Codex sandbox, twice](https://www.accomplish.ai/blog/escaping-the-openai-codex-sandbox-twice/) — primary, published 2026-09-15; the Overpatch and Heapjack mechanisms, the 2026-08-12 report and ~eight-day fix, the affected/fixed versions, the "thing doing the enforcement" line. Fetched 2026-09-20.
- [BleepingComputer — Researchers escape OpenAI Codex sandbox to run commands on host](https://www.bleepingcomputer.com/news/security/researchers-escape-openai-codex-sandbox-to-run-commands-on-host/) — 2026-09-20 (Ax Sharma); the "one Node process… one memory heap" quote, the read-only-mode and malicious-repository detail, OpenAI contacted for comment. Fetched 2026-09-20.
- [openai/codex — release rust-v0.149.0](https://github.com/openai/codex/releases/tag/rust-v0.149.0) — vendor record of the CLI fix: "Prevent `apply_patch` from widening write permissions" and the surrounding sandbox-hardening lines; release dated 20 Aug. Fetched 2026-09-20.
- npm registry `time` field for `@openai/codex` (`npm view @openai/codex time`, 2026-09-20): 0.148.0 2026-08-18, **0.149.0 2026-08-20T21:09Z**, 0.150.0 2026-08-26; weekly downloads 15,573,038 for 2026-09-13 → 09-19 (`api.npmjs.org`).
- [openai/codex — security advisories tab](https://github.com/openai/codex/security/advisories) — fetched 2026-09-20: one advisory, dated 2025-09-19; nothing for these fixes.
