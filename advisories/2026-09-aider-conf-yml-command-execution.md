---
id: 2026-09-aider-conf-yml-command-execution
title: "aider auto-loads a repo's .aider.conf.yml and runs its test-cmd/lint-cmd with no confirmation (CVE-2026-85674, unpatched)"
date_disclosed: 2026-09-04
last_updated: 2026-09-04
severity: high
status: unconfirmed
ecosystems: [pypi, aider]
tools_affected: ["aider (aider-chat)"]
tags: [command-injection, config-auto-load, untrusted-repo, no-confirmation, cve, unpatched]
---

## TL;DR
Aider automatically loads a `.aider.conf.yml` file from the root of whatever git repository it's launched in. If that file sets `test: true` with a `test-cmd`, or a `lint-cmd`, aider runs the command through a shell (`subprocess.Popen(..., shell=True)`) — at startup for `test-cmd`, on first file edit for `lint-cmd` — with **no confirmation prompt, no LLM interaction, and no API key required**, and reportedly regardless of `--yes`. Cloning and running aider inside an attacker-supplied repository is enough to get arbitrary command execution on the developer's machine. Reported to the maintainers on GitHub 2026-06-12; two competing fix pull requests have sat open and unmerged since June; CVE-2026-85674 was published 2026-09-04 with no fixed version available.

## What happened
GitHub user `geo-chen` opened [Aider-AI/aider#5254](https://github.com/Aider-AI/aider/issues/5254) on 2026-06-12, titled "Opening an untrusted repository with aider executes arbitrary commands at startup via .aider.conf.yml test-cmd / lint-cmd (no confirmation)." Per the issue, aider's config loader (`aider/main.py`'s `default_config_files` list) picks up `.aider.conf.yml` from the repository root the same way it would a user's own home-directory config, and a `test-cmd`/`lint-cmd` key in that file reaches `coder.commands.cmd_test()` → `cmd_run()` → `run_cmd()`, which executes the string through a shell. The reporter confirmed the command runs "with and without `--yes`." A companion vector: aider also auto-loads a repo-root `.env` file with `override=True`, which can override environment variables the same way.

Two independent fix attempts have been proposed and remain unmerged as of this advisory: [#5280](https://github.com/Aider-AI/aider/pull/5280) (opened 2026-06-18 by `Sarthak816`) and [#5365](https://github.com/Aider-AI/aider/pull/5365) (opened ~2026-06-30), both of which add a confirmation gate for `test-cmd`/`lint-cmd`/`test`/`lint`/`auto-test`/`auto-lint` keys sourced from a repo-local config, with #5280 explicitly designed so the check cannot be bypassed by `--yes`. As of this advisory neither PR has been merged and `Aider-AI/aider/security/advisories` lists no published GitHub Security Advisory.

CVE-2026-85674 was published 2026-09-04, describing the same mechanism and confirming it reproduces on `0.86.3.dev` (current `main` at assignment time), with a CVSS 4.0 base score reported as 8.5 by the CVE record aggregator OffSeq (the GitHub issue itself states CVSS 7.8 in its own text) — **treat the exact score as unsettled**; the important fact both agree on is High severity and an unauthenticated, no-interaction exploitation path. No GHSA has been published for this CVE at the time of writing, so this advisory is marked `unconfirmed`: the GitHub issue is the primary technical source and the CVE record is a second, independent confirmation that the finding was validated for numbering, but neither is a vendor-published security advisory.

## Am I affected?
```bash
pip show aider-chat   # any version through 0.86.3.dev (current main) is confirmed vulnerable; no fixed release exists yet

# Before running aider in a repo you didn't create yourself, check for the trigger keys:
cat .aider.conf.yml 2>/dev/null | grep -E 'test-cmd|lint-cmd|^test:|^lint:|auto-test|auto-lint'
cat .env 2>/dev/null
```
You are at risk if you clone and run `aider` inside any repository whose contents you have not reviewed — a coding challenge, a fork, a PR checkout, or a "try my project" link.

## If you are affected
1. Do not run `aider` inside an unreviewed repository until a fix ships; if you must, inspect `.aider.conf.yml` and `.env` at the repo root first, or run aider outside the repo directory (e.g. via `--file`) so the repo-root config is not auto-discovered.
2. If you already ran aider inside an untrusted repository, treat the machine as potentially compromised: review shell history, check for unexpected cron/launchd persistence, and rotate any credentials that were present in the environment at the time.
3. → [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)
4. Watch [Aider-AI/aider#5254](https://github.com/Aider-AI/aider/issues/5254) and PRs [#5280](https://github.com/Aider-AI/aider/pull/5280)/[#5365](https://github.com/Aider-AI/aider/pull/5365) for a merged fix.

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a coding agent that auto-loads and executes repo-supplied configuration is exactly the "workspace config runs before trust is established" pattern this repo tracks across multiple tools; treat any such auto-loaded config as a code-execution primitive.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources
- [GitHub — Aider-AI/aider issue #5254: Opening an untrusted repository with aider executes arbitrary commands at startup via .aider.conf.yml test-cmd / lint-cmd (no confirmation)](https://github.com/Aider-AI/aider/issues/5254) — primary report: mechanism, code path, reporter's confirmation, opened 2026-06-12.
- [GitHub — Aider-AI/aider pull request #5280](https://github.com/Aider-AI/aider/pull/5280) — proposed fix (unmerged), opened 2026-06-18.
- [GitHub — Aider-AI/aider pull request #5365](https://github.com/Aider-AI/aider/pull/5365) — second proposed fix (unmerged).
- [OffSeq Threat Radar — CVE-2026-85674: Improper Control of Generation of Code ('Code Injection') in Aider-AI aider](https://radar.offseq.com/threat/cve-2026-85674-improper-control-of-generation-of-code-code-injection-in-aider-ai-aider-9e9c2323d21cf688) — CVE record detail, confirms reproduction on 0.86.3.dev.
