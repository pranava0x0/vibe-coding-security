---
id: 2026-07-cursor-git-exe-autoexec
title: "Cursor IDE — a git.exe planted in a repo root auto-executes on open; silently patched in Desktop, still unpatched in Cursor CLI, Gemini CLI, Codex"
date_disclosed: 2026-07-14
last_updated: 2026-07-29
severity: high
status: active
ecosystems: [cursor]
tools_affected: [cursor]
tags: [zero-click-rce, windows, git-hijacking, unpatched, ai-ide, disclosure-stonewalled, cve-2026-63093]
---

## TL;DR
Mindgard disclosed that **Cursor Desktop on Windows** searches multiple locations for a Git binary when it opens a project — including the **workspace root itself** — and will execute whatever it finds there **automatically, with no prompt, warning, or user interaction**. Placing a malicious binary renamed to `git.exe` in a repository's root directory is enough: simply opening that repo in Cursor runs it, repeatedly, during normal operation. Reported privately in December 2025, the flaw remained live through Mindgard's full public disclosure on **2026-07-14** — but Cursor **silently patched it on 2026-07-13**, one day earlier, with no CVE, no advisory, and no disclosed version number. Separately, independent research from Cymulate found the **same binary-planting class in Cursor CLI, Google Gemini CLI, and OpenAI's Codex Desktop App — all still unpatched** as of that research's publication.

## What happened
Mindgard researcher **Aaron Portnoy** found that when Cursor loads a project on Windows, it resolves the Git executable by searching several candidate locations rather than trusting only the system `PATH` or a pinned binary — and one of those candidate locations is inside the opened workspace itself. As proof of concept, the researchers renamed the Windows Calculator (`calc.exe`) to `git.exe` and placed it at the root of a test repository; opening that repository in Cursor caused the "calculator" to launch repeatedly and automatically as Cursor performed its normal Git-status operations, with **zero clicks, prompts, or confirmation dialogs** ([Mindgard](https://mindgard.ai/blog/cursor-0day-when-full-disclosure-becomes-the-only-protection-left)). In a real attack, the planted binary would be an actual payload rather than a calculator, giving the attacker code execution under the current user's privileges the instant a developer opens the repository — no different from cloning any other untrusted repo.

**Disclosure timeline** (per Mindgard, corroborated by [Cryptobriefing](https://cryptobriefing.com/cursor-vulnerability-code-execution-risk/) and [Developers Digest](https://www.developersdigest.tech/blog/cursor-0day-git-exe-vulnerability)):
- **2025-12-15** — reported to `security-reports@cursor.com`.
- **2026-01-15** — after no response, Mindgard filed via HackerOne; Cursor's CISO subsequently acknowledged the delay as an "automation failure" and manually added the researchers to the bug-bounty program.
- **2026-01-16** — the report was briefly closed as out-of-scope, then reopened after Mindgard reproduced it.
- **2026-02 → 2026-06** — multiple follow-up requests for a patch timeline went unanswered.
- **2026-07-14** — Mindgard published full public disclosure. Sources differ on exactly how many Cursor releases shipped in that window without a fix — Mindgard's own post cites **"197+ new versions,"** while Developers Digest's independent summary states **"70+ releases"**; both agree the number is large and that the flaw remained present in every one of them. Confirmed still present as of the **latest version tested (2026-07-14)**; Mindgard separately notes it verified the bug was still live as late as **2026-04-30** against Cursor 3.2.16.

**Scope**: Windows only — Mac and Linux were not reported as affected. **No CVE has been assigned.** This is a distinct bug from the two other 2026 Cursor Git-related flaws already tracked in this repo: [DuneSlide](2026-06-cursor-duneslide-zeroclick-rce.md) (CVE-2026-50548/CVE-2026-50549, sandbox-escape via `working_directory`/symlink handling, patched in Cursor 3.0) and the nested-bare-repo Git-hook RCE (CVE-2026-26268, patched February 2026) — this is a third, separate mechanism: trusting a Git binary found *inside the untrusted workspace* rather than the system's own Git installation.

## Update — 2026-07-18: silently patched one day before public disclosure — and the same binary-planting class is unpatched in three other AI coding CLIs

**Cursor silently fixed the Cursor Desktop git.exe issue on 2026-07-13** — one day before Mindgard's public disclosure went live on 2026-07-14. As of 2026-07-17, Cursor has issued **no public security advisory, no CVE, and has not disclosed which version number contains the fix** — the fix was confirmed only by researchers re-testing and observing the exploit no longer working, not by any vendor statement. Per this repo's standing "silent patch ≠ no incident" caution: treat this as `status: patched`, but keep the "no disclosure" fact itself as part of the record, and update to Cursor's latest build rather than trying to pin a specific "safe" version number, since none has been published.

Separately, and distinct from the above: **Cymulate Research Labs** disclosed (reported to vendors starting ~2026-01-04, published 2026-06-04) that the **same class of vulnerability — an AI coding tool auto-executing a `git.exe` (or similar) binary planted in the working directory, with no approval, warning, or integrity check — also affects Cursor *CLI*** (a separate product from Cursor Desktop covered above), **Google Gemini CLI**, and **OpenAI's Codex Desktop App**. In Cymulate's Gemini CLI proof-of-concept, the technique escalated to an elevated PowerShell process via a UAC bypass. Vendor responses documented by Cymulate as of its June 4 write-up: **Google acknowledged the Gemini CLI finding as valid but had not shipped a patch**; **OpenAI closed the Codex report as "Not Applicable"**; **Cursor closed the CLI report as "Informative"** (i.e., not treated as a vulnerability) just eight days after the report. Note this is **not** the same bug as AWS Kiro's CVE-2026-10591 — that finding is a related but distinct config-auto-execute flaw in Kiro's file-write tool, already patched in Kiro v0.11.130, and structurally closer to this repo's "AI coding tool auto-executes workspace config" class than to the binary-planting class documented here. **Correction (2026-07-27):** CVE-2026-10591 was independently reported by **Kodem Security** (Nicole Fishbein and Eran Segal, via HackerOne on 2026-02-11, targeting `~/.kiro/settings/mcp.json`) as well as by Cymulate (targeting `.vscode/tasks.json`) — both are real instances of the same root cause (AWS's own bulletin describes it as an unrestricted file-write tool reaching "execution-sensitive paths"), not a single Cymulate-only finding. See the dedicated writeup: [AWS Kiro — MCP config self-rewrite RCE](2026-07-kiro-mcp-config-self-rewrite-rce.md).

**Net effect:** the git.exe/binary-planting root cause that Mindgard found in Cursor Desktop is now known to recur, unpatched as of this sweep, in at least three more widely-used AI coding CLIs (Cursor CLI, Gemini CLI, Codex Desktop). If you use any of these tools on Windows, the "check for a planted binary before opening an untrusted repo" mitigation below applies regardless of which specific tool you're running.

## Update — 2026-07-29: a CVE was assigned (CVE-2026-63093) — and sources now disagree on whether Cursor Desktop is actually patched

**CVE-2026-63093** (CWE-426, Untrusted Search Path) was published to NVD on **2026-07-17**, formally assigning a CVE number to the same Cursor-for-Windows git.exe binary-planting bug this advisory has tracked since Mindgard's initial disclosure — CVSS **8.8** (v3.1) / **8.7** (v4.0), affecting **Cursor for Windows 3.2.16**. This is a genuine accuracy-bar discrepancy worth stating explicitly rather than resolving one way: **NVD's own CVE record, as of publication, lists no patched version** and marks the entry "Awaiting Enrichment" — directly contradicting this advisory's prior note (from the 2026-07-18 update, above) that Cursor silently fixed Cursor Desktop on 2026-07-13. TechRepublic's 2026-07-24 writeup on the new CVE also states the flaw "was quietly fixed on July 13," matching this advisory's original claim — but The Hacker News (2026-07-15/26) and several other outlets (GBHackers, Latest Hacking News, Security Online) independently report the bug as **still unpatched** as of **2026-07-26**, with Mindgard's own re-tests confirming it live against the **current Cursor release (3.11, shipped 2026-07-10)**, not just the older 3.2.16 build named in the CVE record. No vendor advisory, changelog entry, or confirmed patched version number has been published by Cursor itself to resolve this discrepancy. **Status changed from `patched` to `active`** to reflect that the weight of independent, directly-fetched evidence (NVD + The Hacker News + Mindgard's own re-test) says unpatched, against a single secondary source (TechRepublic) claiming otherwise — treat the mitigation below as still necessary until Cursor publishes an unambiguous fixed-version statement.

## Am I affected?
**Patch status is disputed as of 2026-07-29 — see the update above.** Do not assume Cursor Desktop is safe merely by being on a recent build; NVD's CVE-2026-63093 record lists no fixed version, and independent researchers report the bug still reproduces against Cursor 3.11 (the latest release as of 2026-07-10). **Cursor CLI, Google Gemini CLI, and OpenAI Codex Desktop remain unpatched as of this sweep** for the same binary-planting class; if you run any of these tools on Windows and open repositories from untrusted sources, the mitigation below is still necessary regardless of which tool or version you're on.

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
- [Security Online — Cursor Zero-Day Vulnerability Remains Unpatched After Seven Months](https://securityonline.info/cursor-zero-day-vulnerability/) — independent corroboration of the disclosure timeline; noted the exploit stopped working on 2026-07-13 during re-testing, ahead of the public writeup.
- [Cymulate — When AI Tools Become the Backdoor: Zero-Click RCE via Prompt Injection](https://cymulate.com/blog/zero-click-rce-prompt-injection-ai-tools/) — primary source for the Cursor CLI / Gemini CLI / Codex Desktop binary-planting findings and vendor-response details (Google acknowledged/no patch, OpenAI closed as Not Applicable, Cursor CLI closed as Informative).
- [AWS Security Bulletin 2026-037-AWS — CVE-2026-10591](https://aws.amazon.com/security/security-bulletins/2026-037-aws/) — the related-but-distinct Kiro IDE config-auto-execute finding, patched in Kiro v0.11.130; see [dedicated advisory](2026-07-kiro-mcp-config-self-rewrite-rce.md) for the full writeup and correct researcher attribution.
- [NVD — CVE-2026-63093](https://nvd.nist.gov/vuln/detail/CVE-2026-63093) — canonical CVE record confirming CVSS 8.8/8.7, CWE-426, affected version Cursor for Windows 3.2.16, and no patched version listed as of the "Awaiting Enrichment" record.
- [TechRepublic — Cursor Quietly Patches High-Severity Git Vulnerability After Seven-Month Delay](https://www.techrepublic.com/article/news-cursor-git-code-execution-vulnerability-cve-2026-63093/) — states the flaw was fixed 2026-07-13, contradicting NVD and the sources below.
- [The Hacker News — Cursor Flaw Lets Malicious Cloned Repositories Trigger Windows Code Execution](https://thehackernews.com/2026/07/cursor-flaw-lets-malicious-cloned.html) — reports the flaw as still unpatched as of 2026-07-15/26, with Mindgard's re-test against the current Cursor 3.11 release.
