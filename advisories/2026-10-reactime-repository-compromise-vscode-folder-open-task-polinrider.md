---
id: 2026-10-reactime-repository-compromise-vscode-folder-open-task-polinrider
title: "Reactime: 20 of 22 repository branches carried a folder-open VS Code task that ran a stealer, 2026-06-01 to 10-07; npm package clean"
date_disclosed: 2026-10-06
last_updated: 2026-10-12
severity: high
status: contained
ecosystems: [github, vscode, react, chrome-extension, npm]
tools_affected: ["clones of open-source-labs/reactime on any branch other than master or dev, made between 2026-06-01 and 2026-10-07 and opened in VS Code or built", "VS Code and Discord installations on those machines (modified to re-run the implant)", "credentials reachable from those machines: GitHub, npm, cloud, browser sessions, SSH"]
tags: [repository-compromise, vscode-tasks, folder-open, backdated-commits, forged-commits, credential-theft, persistence, blockchain-c2, dprk-consistent, polinrider, react, devtools, contained]
---

## TL;DR
Reactime, the open-source React debugging extension maintained under Open Source Labs, had its GitHub repository compromised through a contributor account. From 2026-06-01, with further pushes on 2026-08-20 and 2026-09-27, 20 of the repository's 22 branches carried an implant; `master` and `dev` stayed clean, and the published npm package `reactime` 3.1.1 (2020) was reported clean. The commits were forged to look like one-file changes with 2020 dates while replacing 387 files. A `.vscode/tasks.json` task set to run on folder open launched an obfuscated JavaScript file named like a font, so cloning a non-default branch and opening it in VS Code was enough; 15 branches also had the code appended to the Babel configuration, so building ran it too. The implant profiles the host, resolves its command server from a public Ethereum transaction, sends machine data out encrypted, and edits the installed VS Code and Discord so it re-runs on each launch. Deep Woods Security, who analysed it, say the tradecraft is consistent with public reporting on the PolinRider campaign and do not claim an independent attribution. Maintainers reset all twenty branches on 2026-10-07. Local clones made before that still contain it.

## What happened

**Timeline, from the Deep Woods write-up and the public issue.**

| Date | Event |
|---|---|
| 2026-06-01 | First push of the implant through a compromised contributor account (added to the issue in its 2026-10-11 edit; the original issue text started the window at 08-20). |
| 2026-08-20, 2026-09-27 | Committer dates on the rewrites of branch tips; twelve other branches were backdated so the dates do not show. Each rewrite presented as a one-file change and replaced hundreds of files. The `staging` tip is a forged commit; a fork preserves the original with the same author, date, message and parent. |
| 2026-09-30 | Michael Novati, co-founder of Formation, posts a public warning before technical details exist (per Deep Woods and the issue; the post itself was not fetched this sweep). |
| 2026-10-06 | t3lesph0re files issue #368, "Security: 20 branches contain malware. Do not open in VS Code or build," and in parallel a private GitHub security advisory to the maintainers and a report to GitHub Support. Deep Woods report the findings to GitHub, CISA and the FBI. |
| 2026-10-07 | Maintainers reset all twenty affected branches to their pre-compromise tips; all 22 branches clean. |
| 2026-10-11 | Deep Woods publish the analysis; the issue is edited to widen the window to 06-01 and link it. |
| 2026-10-12 | The reporter closes the issue as completed. No maintainer comment appears on the issue page. |

**What the implant does, in the analysts' terms.** Two triggers: a VS Code task configured to run automatically when the folder opens, enabled by a workspace setting that allows automatic tasks, and obfuscated JavaScript appended to a Babel configuration file on 15 branches. The payload is a file disguised as a font that is actually obfuscated JavaScript. It profiles the host and withholds the payload from machines that look like analysis systems. It resolves its command server from a public Ethereum transaction rather than a hard-coded address, the same dead-drop design as [NullReceiver](2026-08-nullreceiver-npm-ethereum-c2.md) and [indexed-btree](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md). It exfiltrates harvested machine data as encrypted uploads tagged with the machine's identity. It modifies the installed VS Code and Discord applications so that it re-runs and re-resolves its server on each launch. Five submitted samples had zero detections across antivirus engines. The write-up does not enumerate the credential categories taken; given the host profiling and the persistence targets, treat everything the user account could read as taken.

**Attribution.** Deep Woods state the activity is consistent with public reporting on a North Korea-linked campaign and that this is not their own determination; the issue reporter says the same of PolinRider. This corpus tracks that campaign in [the PolinRider file](2026-03-polinrider-multi-ecosystem-dprk-campaign.md), whose npm-side victims this year include [ulid-xyz](2026-09-ulid-xyz-npm-transitive-rat-chain-microsoftsystem64.md), [WeaselBiscuit](2026-09-weaselbiscuit-npm-chrome-extension-storage-stealer.md) and [mathmain](2026-09-mathmain-encrypted-loader-npm-lusolve-trigger.md). What is new here is the delivery: not a registry publication but a repository's non-default branches, aimed at people who clone to contribute or to try a branch, with the editor itself as the execution step.

**Why the npm package being clean does not end it.** Reactime is distributed as a Chrome extension and the `reactime` npm name has not been published since 2020-03-05 (3.1.1), so a dependency audit sees nothing. The exposure is a `git clone` plus an editor open. That is the shape [tensorlake](2026-10-tensorlake-npm-shai-hulud-hostage-token-wipe.md) used for persistence a week earlier (`.vscode/tasks.json` and `.claude/settings.json` written into reachable repositories) and the shape [the MoAI-ADK record](2026-10-vulncheck-single-researcher-agent-mcp-gateway-cve-wave-mini-swe-agent-env-leak.md) describes as a bug; here it is the initial access.

**Evidence and status.** One analyst firm's write-up and one reporter's issue carry the technical detail; the two may overlap. The maintainers' reset of twenty branches on 2026-10-07, recorded in the issue, is the project's confirmation that the branches were compromised, and the forged-commit evidence (a fork holding the unforged original) is checkable by anyone with the repository. `contained` because the upstream is clean; the clones are not, which is why this is not `historical`.

## Am I affected?

```bash
# Did you clone Reactime on a non-default branch in the window?
cd path/to/reactime && git branch --show-current && git log -1 --format='%ci %H' 2>/dev/null
# A folder-open task in any clone (the trigger)
grep -rn '"runOn"\s*:\s*"folderOpen"' --include=tasks.json . ~/projects 2>/dev/null
grep -rn 'task.allowAutomaticTasks' --include=settings.json . ~/projects 2>/dev/null
# Font-named files that are not fonts
find . -path ./node_modules -prune -o \( -name '*.woff' -o -name '*.woff2' -o -name '*.ttf' \) -print 2>/dev/null | xargs -r file | grep -iv 'font'
# Babel config with appended code (15 branches)
wc -c babel.config.* .babelrc* 2>/dev/null
# Editor and chat clients modified for persistence: compare the installed entry points against a fresh install
ls -la --time-style=full-iso "$HOME/.vscode" "$HOME/.config/Code" "$HOME/.config/discord" 2>/dev/null | head
```

- Affected if a clone of any branch other than `master` or `dev`, made between 2026-06-01 and 2026-10-07, was opened in VS Code with automatic tasks allowed, or was built. The issue's original window started 2026-08-20; the 10-11 edit moved it to 06-01. Use 06-01.
- Not affected by this incident if you only installed the Chrome extension from the store or the 2020 npm package, per the analysts; both were reported clean.
- A clone reset by `git pull` after 2026-10-07 removes the files from the working tree but does not undo what ran when the folder was first opened.

## If you are affected

1. **Treat the machine as compromised.** Delete the clone, reinstall VS Code and Discord from fresh downloads rather than trusting the installed copies, and rebuild if you can. [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) covers the host triage; the trigger was an editor task rather than an install script, but the aftermath is the same.
2. **Rotate every credential the machine could reach:** GitHub ([playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)), npm ([playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)), cloud ([playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)), SSH keys, browser sessions, and AI-provider and MCP tokens in `~/.claude.json`, `~/.cursor/` and similar, which the current worms read first.
3. **Match the analysts' indicators.** Deep Woods publish a hash set and detection rules for the modified VS Code and Discord entry points; use those rather than anything reproduced here.
4. **Audit your other clones for folder-open tasks** before opening them again; the grep above is the check.

## Prevention

- **Set VS Code's automatic-tasks setting to off** (`task.allowAutomaticTasks: "off"`) in user settings, and keep Workspace Trust on; a repository you are evaluating should not get to run anything when a window opens. The same applies to the hooks and settings files of AI editors: [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- **Clone into a disposable environment** (container, VM, Codespace) when trying a branch of a project you do not maintain: [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- **Forged dates and single-file diffs are the disguise.** A commit whose stat line says one file while the tree changed hundreds, or a 2020 date on a tip pushed this year, is checkable with `git show --stat` and `git log --format='%ad %cd'`; maintainers should require signed commits and branch protection on every branch that people clone, not only the default.
- **Keep a project's contributor accounts under 2FA and review them.** The entry here was a contributor account, and the fix was a credential revocation plus a reset, which is the [tensorlake](2026-10-tensorlake-npm-shai-hulud-hostage-token-wipe.md) template again.

## Sources
- [Deep Woods Security — Reactime repository compromise](https://www.deepwoodssec.com/research/reactime) — fetched 2026-10-12, published 2026-10-11: the exposure window, the 20-of-22 branch count, the 387-file and 160,000-line rewrite, the forged and backdated commits, the folder-open task and font-named payload, the Ethereum-transaction resolution, host profiling, encrypted exfiltration, the VS Code and Discord persistence, the zero-detection samples, the "consistent with public reporting" attribution wording, the reports to GitHub, CISA and the FBI, and the remediation list. The indicator set and detection rules are on that page and are not reproduced here.
- [open-source-labs/reactime — issue #368](https://github.com/open-source-labs/reactime/issues/368) — fetched 2026-10-12: opened 2026-10-06 by t3lesph0re, the branch list, the rewrite dates, the `staging` forged-commit evidence and the preserving fork, the private-advisory and GitHub Support reports, the 10-07 reset, the 10-11 edit widening the window to 06-01, the 10-12 closure, the mention of Michael Novati's 09-30 warning, no maintainer comment. The warning post itself was not located this sweep.
- Registry, checked 2026-10-12: `npm view reactime` shows latest 3.1.1, published 2020-03-05, repository `oslabs-beta/reactime`; no publication since.
- Related in this corpus: [PolinRider campaign](2026-03-polinrider-multi-ecosystem-dprk-campaign.md), [NullReceiver](2026-08-nullreceiver-npm-ethereum-c2.md) and [indexed-btree](2026-09-indexed-btree-npm-runtime-payload-sepolia-c2.md) (blockchain-resolved command servers), [tensorlake](2026-10-tensorlake-npm-shai-hulud-hostage-token-wipe.md) (editor and agent config files as re-run hooks), [GlassWorm](2025-10-glassworm-vscode-worm.md) (the VS Code ecosystem as the delivery path).
