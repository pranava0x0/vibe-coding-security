---
id: 2026-07-cursor-git-exe-autoexec
title: "Cursor IDE — unpatched Windows zero-day: a git.exe planted in a repo root auto-executes on open (no CVE, no patch)"
date_disclosed: 2026-07-14
last_updated: 2026-07-16
severity: high
status: active
ecosystems: [cursor]
tools_affected: [cursor]
tags: [zero-click-rce, windows, git-hijacking, unpatched, ai-ide, disclosure-stonewalled]
---

## TL;DR
Mindgard disclosed that **Cursor on Windows** searches multiple locations for a Git binary when it opens a project — including the **workspace root itself** — and will execute whatever it finds there **automatically, with no prompt, warning, or user interaction**. Placing a malicious binary renamed to `git.exe` in a repository's root directory is enough: simply opening that repo in Cursor runs it, repeatedly, during normal operation. Reported privately in December 2025, the flaw was still unpatched at full public disclosure on **2026-07-14** — over 190 days and, per Mindgard, well over 70 subsequent Cursor releases later.

## What happened
Mindgard researcher **Aaron Portnoy** found that when Cursor loads a project on Windows, it resolves the Git executable by searching several candidate locations rather than trusting only the system `PATH` or a pinned binary — and one of those candidate locations is inside the opened workspace itself. As proof of concept, the researchers renamed the Windows Calculator (`calc.exe`) to `git.exe` and placed it at the root of a test repository; opening that repository in Cursor caused the "calculator" to launch repeatedly and automatically as Cursor performed its normal Git-status operations, with **zero clicks, prompts, or confirmation dialogs** ([Mindgard](https://mindgard.ai/blog/cursor-0day-when-full-disclosure-becomes-the-only-protection-left)). In a real attack, the planted binary would be an actual payload rather than a calculator, giving the attacker code execution under the current user's privileges the instant a developer opens the repository — no different from cloning any other untrusted repo.

**Disclosure timeline** (per Mindgard, corroborated by [Cryptobriefing](https://cryptobriefing.com/cursor-vulnerability-code-execution-risk/) and [Developers Digest](https://www.developersdigest.tech/blog/cursor-0day-git-exe-vulnerability)):
- **2025-12-15** — reported to `security-reports@cursor.com`.
- **2026-01-15** — after no response, Mindgard filed via HackerOne; Cursor's CISO subsequently acknowledged the delay as an "automation failure" and manually added the researchers to the bug-bounty program.
- **2026-01-16** — the report was briefly closed as out-of-scope, then reopened after Mindgard reproduced it.
- **2026-02 → 2026-06** — multiple follow-up requests for a patch timeline went unanswered.
- **2026-07-14** — Mindgard published full public disclosure. Sources differ on exactly how many Cursor releases shipped in that window without a fix — Mindgard's own post cites **"197+ new versions,"** while Developers Digest's independent summary states **"70+ releases"**; both agree the number is large and that the flaw remained present in every one of them. Confirmed still present as of the **latest version tested (2026-07-14)**; Mindgard separately notes it verified the bug was still live as late as **2026-04-30** against Cursor 3.2.16.

**Scope**: Windows only — Mac and Linux were not reported as affected. **No CVE has been assigned.** This is a distinct bug from the two other 2026 Cursor Git-related flaws already tracked in this repo: [DuneSlide](2026-06-cursor-duneslide-zeroclick-rce.md) (CVE-2026-50548/CVE-2026-50549, sandbox-escape via `working_directory`/symlink handling, patched in Cursor 3.0) and the nested-bare-repo Git-hook RCE (CVE-2026-26268, patched February 2026) — this is a third, separate mechanism: trusting a Git binary found *inside the untrusted workspace* rather than the system's own Git installation.

## Am I affected?
You are affected if you run **Cursor on Windows** and ever open a repository from an untrusted source (a public GitHub repo, a fork, a coding-challenge template, a contributor's PR branch checked out locally, etc.) — no patched version exists as of this writing.

```powershell
# Before opening any unfamiliar repo in Cursor on Windows — check for a planted git.exe
Get-ChildItem -Path . -Recurse -Filter git.exe -File | Where-Object { $_.FullName -notmatch '\\Git\\' }

# Compare against your real Git install path
where.exe git
```
Any `git.exe` (or similarly named executable) sitting inside a cloned repository — anywhere other than your actual Git installation directory — should be treated as a live payload, not a coincidence.

## If you are affected
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) — audit any repo you've already opened in Cursor for a planted binary before assuming you're clean.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — never open an untrusted repository in Cursor on a host with production credentials until this is patched; use a disposable VM/container for first-look review.
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Why this matters for vibe coders
This is the same "git clone → code execution" shape already tracked across this repo's [AI-coding-tool-auto-executes-workspace-config class](2026-06-amazon-q-mcp-workspace-rce.md), except here the trust failure isn't a config file at all — it's the IDE resolving a *system binary* from inside the untrusted workspace. The seven-month stonewalled-disclosure timeline is itself a data point: treat "no CVE yet" as "not yet triaged," not "not real," and don't wait for a patch before changing how you open unfamiliar repos on Windows.

## Sources
- [Mindgard — Cursor 0day: When Full Disclosure Becomes the Only Protection Left](https://mindgard.ai/blog/cursor-0day-when-full-disclosure-becomes-the-only-protection-left) — primary disclosure, PoC details, full timeline.
- [Developers Digest — Cursor 0-Day: git.exe Vulnerability](https://www.developersdigest.tech/blog/cursor-0day-git-exe-vulnerability) — independent summary, affected-version detail, CVE cross-references.
- [Cryptobriefing — Cursor Vulnerability Poses Code Execution Risk](https://cryptobriefing.com/cursor-vulnerability-code-execution-risk/) — independent corroboration.
