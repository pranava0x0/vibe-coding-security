---
id: 2026-09-gitspawn-git-config-agent-rce-cluster
title: "GitSpawn — repo-local git config (core.fsmonitor and others) runs code in 7 AI coding agents before any trust prompt"
date_disclosed: 2026-09-01
last_updated: 2026-09-20
severity: critical
status: active
ecosystems: [claude-code, cursor, openai-codex, goose, qwen-code, grok-build, hermes-agent, github-copilot-cli]
tools_affected: ["Claude Code", "Cursor / Cursor CLI", "OpenAI Codex CLI/Desktop", "Block goose", "Alibaba Qwen Code", "xAI Grok Build", "Hermes Agent", "GitHub Copilot CLI (CVE-2026-45033, May 2026 precedent)"]
tags: [git-config-abuse, core-fsmonitor, pre-trust-execution, sandbox-escape, workspace-trust-bypass, rce, cve, cluster]
---

## TL;DR
Manifold Security researcher Francisco Rosales disclosed **GitSpawn**, a vulnerability class in AI coding agents that run `git` commands (e.g. `git status`) to gather repository context the moment a folder or repo is opened — without stripping the repository's own `.git/config`. Git's `core.fsmonitor` setting (and at least one other, unnamed, still-exploitable key) lets a repo specify a helper program that git executes on any index-refresh operation. A repository shipped with a crafted `.git/config` therefore runs arbitrary attacker code with the developer's full privileges — **before any prompt, tool approval, model call, or workspace-trust dialog**, and outside the agent's sandbox. Eight findings were reported across seven agents between July 1 and August 8, 2026; **four remained unpatched** at publication on 2026-09-01, including a second, distinct Claude Code path (via `claude ultrareview`) still open as of build 2.1.252.

## What happened
`core.fsmonitor` is a legitimate Git performance feature: its value is a command Git runs to ask a filesystem-watcher helper which files changed, instead of walking the whole tree. Git reads this setting from the repository's own `.git/config` — not a global, trusted location — and **any operation that refreshes the index** (`git status`, `git diff`, `git add`, and the repo-context calls agents run on startup) triggers it. An ordinary `git clone` does not carry a source repo's local `.git/config` forward, so exploitation requires the poisoned repository to arrive with its `.git` directory intact — a zip download, a shared drive, a synced folder, a CI artifact, or a "clone this exact tarball" onboarding step all qualify ([Manifold Security](https://www.manifold.security/blog/ai-coding-agents-git-hijack); [paddo.dev](https://paddo.dev/blog/gitspawn-opening-the-folder)).

AI coding agents made this exploitable at scale because they run `git status`-class commands eagerly, on open, to build context for the model — before the user has clicked through any workspace-trust or sandbox-approval dialog. Manifold's own summary: *"no submitted prompt, no model call, no tool approval, no trust prompt. The command executes before [the agent] ever contacts the model."* The researcher notes this reintroduces a class of bug VS Code itself patched in 2021 (CVE-2021-43891, fixed 1.63.1, which blocked git operations in untrusted workspaces) — AI coding agents re-added eager git execution on open and reopened the same hole ([paddo.dev](https://paddo.dev/blog/gitspawn-opening-the-folder)).

**Disclosure timeline** (per Manifold): Grok Build reported 2026-07-01 (closed "informative"), Qwen Code reported 2026-07-07 (accepted by Alibaba), Goose reported 2026-07-13, Grok Build re-reported 2026-07-14, Claude Code `ultrareview` path reported 2026-07-15, Hermes Agent and OpenAI Codex reported 2026-07-20, Cursor reported 2026-08-08, published 2026-09-01.

**Per-agent status at publication:**

| Agent | Affected version(s) | Status | CVE / GHSA |
|---|---|---|---|
| **Block goose** | < 1.44.0 | Patched (1.44.0) | [CVE-2026-72718](https://github.com/aaif-goose/goose/security/advisories/GHSA-r5pp-p5r8-466r) / GHSA-r5pp-p5r8-466r (CVSS 4.0: 7.0) |
| **OpenAI Codex CLI/Desktop** | 0.102.0–0.130.0 (CLI); pre-fix Desktop builds | Patched — three CVEs assigned 2026-09-01 (a fourth, CVE-2026-19591, from the same batch — see note below) | CVE-2026-19592 (`core.fsmonitor`), CVE-2026-19590 (`core.hooksPath`), CVE-2026-19593 (`attr.tree` + clean filter) |
| **Claude Code** — `core.fsmonitor` path | ≤ 2.1.193 | Patched (2.1.196, 2026-06-29); **no Anthropic advisory published for either Claude Code finding** | none published |
| **Claude Code** — `claude ultrareview` path (separate, unnamed git-config key) | 2.1.210 → **2.1.252 confirmed still vulnerable 2026-09-01** | **Unpatched.** Reported 2026-07-15; closed by Anthropic as a duplicate of an internal ticket. Runs before the workspace-trust prompt is shown. | none published |
| **Hermes Agent** | 0.18.2, 0.21.0 | **Unpatched.** Vendor did not respond across six contact attempts; CVE assigned independently. | [CVE-2026-71963](https://cve.threatint.com/CVE/CVE-2026-71963) (assigned by VulnCheck, an independent CNA) |
| **Alibaba Qwen Code** | 0.19.6, 0.22.3 | **Unpatched** (report accepted 2026-07-07, no fix shipped by publication) | none published |
| **xAI Grok Build** | 0.2.93, 1.0.13 | **Unpatched** (first report closed "informative"; re-report also unresolved) | none published |
| **Cursor / Cursor CLI** | — | Disputed — see note below | none published |

**Note on Cursor's status:** Manifold's own summary table and The Hacker News' writeup list Cursor as patched following the 2026-08-08 report. Separate secondary coverage (CyberSecurityNews, a hacklido.com repost) instead lists "Cursor CLI" as unpatched. Manifold is the primary discloser and is the source this repo defers to, but the discrepancy is unresolved as of this writing — treat Cursor's status as **unconfirmed** rather than fully patched until Cursor publishes its own advisory or Manifold's tracker is checked directly.

This is a distinct, newer disclosure from the already-tracked [Claude Code / Claude Desktop GHSA batch](2026-08-claude-code-desktop-ghsa-batch.md), whose `CVE-2026-55607` (git-worktree path confusion, affecting Claude Code 2.1.38–2.1.163, fixed in 2.1.163) is a different mechanism and an earlier, already-closed window — do not conflate the two when triaging.

### Update 2026-09-12 — the library layer: GitPython CVE-2026-78676 turns a dormant `.git/config` value into a live `core.hooksPath` directive (RCE), and aider ships a vulnerable pin

GitSpawn is about agents that *shell out* to `git`. The same "repo-local git config becomes code execution" class also lives one layer down, in the Python libraries agents use to read and write git config. **GitPython CVE-2026-78676 / GHSA-284h-m62q-gf8w** (CVSS 4.0 **9.3**, published 2026-08-25; fix released 2026-08-10 in **3.1.59**, affects **≤ 3.1.58**) is a read-then-rewrite injection: GitPython correctly parses a multi-line quoted value from a poisoned `.git/config`, but `write_section()` re-serializes it by replacing embedded newlines with bare newline-tab sequences — so the second half of a crafted value becomes an **independent config line** the next time the file is parsed. An attacker plants a dormant value; any routine GitPython config write (setting `user.name`, say) activates it into a live directive such as `core.hooksPath`, and the next hook-triggering git operation runs attacker code. Earlier hardening (commits `c417af46`, `1ed1b924`) guarded programmatic arguments but not the read-then-rewrite path.

Why it belongs with GitSpawn: it is the same trust-boundary failure (a repository's own `.git/config` is attacker-controlled input, not configuration you can trust) reached through a library rather than a shelled-out command, and it lands in the same tools. **aider** pins `gitpython==3.1.46` (confirmed in aider-chat 0.86.2's dependency metadata, 2026-09-12) — below 3.1.59, so an aider install that has not upgraded its transitive GitPython is exposed when opening a repository carrying a poisoned config. Any agent, script, or CI job that uses GitPython against untrusted repositories is in scope.

```bash
# Is a vulnerable GitPython present (directly or transitively, e.g. via aider)?
pip show GitPython 2>/dev/null | grep -E '^(Name|Version):'   # vulnerable if <= 3.1.58
pip install -U 'GitPython>=3.1.59'
```

Fix is GitPython **3.1.59+** (current release 3.1.62). This does not change the GitSpawn per-agent status table above; it is a related library CVE affecting the same "opening a repo runs its config" surface.

## Am I affected?
```bash
# Claude Code
claude --version   # unpatched core.fsmonitor path if <= 2.1.196 predecessor builds;
                    # the `claude ultrareview` path is unpatched through 2.1.252 as of 2026-09-01 — check for a newer fix before trusting any version number here

# goose
goose --version    # affected if < 1.44.0

# OpenAI Codex
codex --version    # affected if in 0.102.0-0.130.0 range; confirm against latest release notes

# Any agent: look for a repo-local fsmonitor hook before opening an unfamiliar repo/archive
git config --get core.fsmonitor
git config --get core.hooksPath
```
You are at risk if you routinely open repositories, extracted archives, or synced folders you did not create yourself in any of the agents above — especially ones delivered as a zip/tarball or copied from a shared location rather than a fresh `git clone` from a URL you control (a plain clone from a remote does not carry the source's local `.git/config`).

### Update 2026-09-14 — the precedent GitSpawn's write-up did not cite: GitHub Copilot CLI had the same `core.fsmonitor` bug, via a *nested bare repository*, patched in May (CVE-2026-45033)

GitHub's own advisory [GHSA-9ccr-r5hg-74gf](https://github.com/advisories/GHSA-9ccr-r5hg-74gf) (published 2026-05-06; NVD 2026-05-13; CVSS 4.0 **8.5**; reporter syvb) describes a variant that **does not need the top-level `.git/config` at all**: a **bare git repository nested inside a project directory** (a `vendor/` folder, a deeply nested path) is auto-discovered by git as it walks up the directory tree, and its config — including `core.fsmonitor` — is applied when Copilot CLI runs a routine `git status`/`git diff`. That closes the "a plain clone is safe" loophole for this one vector: a nested bare repo *survives* a normal clone, a pull request, or a dependency, because it is committed content, not local metadata. Affects `@github/copilot` **≤ 1.0.42**; fixed **1.0.43**, which sets **`safe.bareRepository=explicit`** via environment variable so git stops discovering bare repositories implicitly.

Two things follow. First, the fix is generic and cheap — any agent that shells out to git can set `GIT_CONFIG_PARAMETERS='safe.bareRepository=explicit'` (or `git config --global safe.bareRepository explicit` on the developer's machine) and remove the nested-bare-repo path regardless of vendor patch status; do that today for every agent in the table above, patched or not. Second, this advisory's May precedent means the class was publicly documented four months before Manifold's cluster disclosure, in GitHub's own advisory database, under a product name none of the GitSpawn queries used — the same sourcing gap this repo keeps hitting with vendor-only GHSA disclosures.

```bash
# Global mitigation for the nested-bare-repo variant, independent of any agent's patch:
git config --global safe.bareRepository explicit
# Find nested bare repos (a HEAD file next to objects/ and refs/, outside the top-level .git) before opening a checkout in an agent:
find . -type f -name HEAD -not -path './.git/*' -execdir test -d objects \; -execdir test -d refs \; -print 2>/dev/null
```

## If you are affected
1. Update the affected agent to the patched build listed above; for Claude Code, be aware that **no version is confirmed to close the `ultrareview` path** as of this advisory — avoid `claude ultrareview` against any repository you have not fully reviewed until Anthropic confirms a fix.
2. Treat any machine that opened an untrusted repo/archive in an affected agent before patching as potentially compromised: audit `~/.ssh/authorized_keys`, shell history, and cron/launchd persistence, and rotate any cloud or CI credentials that were present in the environment.
3. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
4. Before opening any repository or extracted archive of unknown provenance, inspect `.git/config` for a `core.fsmonitor`, `core.hooksPath`, or `attr.tree` entry pointing at an executable.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a sandbox flag is not a guarantee when the executing process is git itself, invoked outside the agent's own command sandbox.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — treat "download and open" workflows (zips, shared drives, CI artifacts) as carrying more risk than a plain `git clone`, since only the former preserves a poisoned local `.git/config`.
→ Never run an AI coding agent against a repository whose `.git` directory you did not create via a fresh clone from a URL you chose.

**Note 2026-09-20 — the same 2026-09-01 Codex batch carries a fourth CVE that is not a git-config sink.** [GHSA-2frj-4qr5-m2rf / CVE-2026-19591](https://github.com/advisories/GHSA-2frj-4qr5-m2rf) (CVSS 8.8, Codex CLI on Windows/macOS/Linux and Codex Desktop): Codex's command-safety parser read PowerShell's stop-parsing token (`--%`) differently from PowerShell itself, so an attacker-prepared repository could make Codex run **file-writing git commands without approval**, modify configuration, and end up executing an attacker-controlled MCP server with the user's privileges (fix: openai/codex PR #22643). Different root cause, same outcome class — a repository steering the agent into an unapproved write — and the same fix window; it is recorded here so a reader reconciling the Codex CVE list against this table is not left with one unexplained id. Affected/patched versions are "unknown" on the database record; run current Codex (see also the separate [Heapjack/Overpatch sandbox escapes](2026-09-codex-heapjack-overpatch-sandbox-escapes.md), fixed 0.149.0).

## Sources
- [Manifold Security — GitSpawn: A Single Flaw Lets Untrusted Repos Run Code in Claude Code, Codex, Cursor, and Grok](https://www.manifold.security/blog/ai-coding-agents-git-hijack) — primary disclosure: mechanism, full disclosure timeline, per-agent status table.
- [GitHub Security Advisory GHSA-r5pp-p5r8-466r — Arbitrary command execution in goose CLI via `goose review` via git core.fsmonitor](https://github.com/aaif-goose/goose/security/advisories/GHSA-r5pp-p5r8-466r) — vendor advisory confirming CVE-2026-72718, CVSS 4.0 7.0, credited to Francisco Rosales.
- [The Hacker News — Malicious .git Configs Can Make Claude, Codex, Cursor, and Other AI Agents Run Attacker Code](https://thehackernews.com/2026/09/malicious-git-configs-can-make-claude.html) — independent secondary coverage; per-agent version/CVE table including the three OpenAI Codex CVEs.
- [paddo.dev — Opening the Folder Was the Exploit: GitSpawn, Seven Coding Agents, and a Bug VS Code Fixed in 2021](https://paddo.dev/blog/gitspawn-opening-the-folder) — independent technical follow-up; VS Code CVE-2021-43891 historical context; author's own retest of Claude Code 2.1.259 confirming the `ultrareview` path remained unpatched.
- [OffSeq Threat Radar — CVE-2026-19592: OpenAI Codex CLI](https://radar.offseq.com/threat/cve-2026-19592-cwe-15-external-control-of-system-or-configuration-setting-in-openai-codex-cli-6bb433ae2527fe34) — CVE record detail for the Codex `core.fsmonitor` finding.
- [GitHub Advisory Database — GHSA-284h-m62q-gf8w (CVE-2026-78676, GitPython)](https://github.com/advisories/GHSA-284h-m62q-gf8w) — fetched 2026-09-12 for the 2026-09-12 update: the read-then-rewrite `write_section()` injection, `core.hooksPath` activation, CVSS 9.3, affected ≤ 3.1.58 / fixed 3.1.59, prior-fix commit references.
- [NVD — CVE-2026-78676](https://nvd.nist.gov/vuln/detail/CVE-2026-78676) — fetched via the NVD API 2026-09-12: CVSS 4.0 9.3, "before 3.1.59," published 2026-08-25.
- [PyPI — aider-chat 0.86.2 dependency metadata](https://pypi.org/pypi/aider-chat/json) — queried 2026-09-12: confirms the `gitpython==3.1.46` pin (< 3.1.59).
- [GitHub Advisory Database — GHSA-9ccr-r5hg-74gf (CVE-2026-45033, GitHub Copilot CLI: nested bare repository can execute arbitrary commands via core.fsmonitor)](https://github.com/advisories/GHSA-9ccr-r5hg-74gf) — fetched 2026-09-14 for the 2026-09-14 update: mechanism, delivery vectors (PRs, dependencies, nested clones), `safe.bareRepository=explicit` fix, affected ≤ 1.0.42 / fixed 1.0.43, published 2026-05-06, reporter syvb.
- [NVD — CVE-2026-45033](https://nvd.nist.gov/vuln/detail/CVE-2026-45033) — fetched via the NVD API 2026-09-14: CVSS 4.0 8.5 HIGH, published 2026-05-13, "prior to 1.0.43."
