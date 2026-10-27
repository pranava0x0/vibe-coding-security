---
id: 2026-10-testmetest-miasma-npm-worm-packages-and-42-hijacked-github-repositories
title: "Malicious `*-testmetest` and `@iobandamwer` npm packages (Miasma-family worm, 2026-10-19 to 10-25) and 42 hijacked GitHub repositories: remove, isolate, then rotate"
kind: malicious-artifact
date_disclosed: 2026-10-22
last_updated: 2026-10-26
severity: critical
status: active
ecosystems: [npm, github, github-actions, ai-coding-agents]
tools_affected: ["anyone who installed any package in the table between 2026-10-19 and 10-25", "repositories of the 11 GitHub owners JFrog lists as hijacked", "Claude, Gemini, Cursor and VS Code configurations on the same machine (hooks planted)"]
tags: [supply-chain, malicious-package, worm, miasma, phantom-gyp, mini-shai-hulud, wiper, token-revocation-trigger, npm, github, native-addon, anti-analysis, ai-tool-hooks, safedep, jfrog]
---

## TL;DR
Remove every package below and treat the host as compromised. The worm is a Miasma-family variant that SafeDep first took for a test (the `-testmetest` suffix) and JFrog (10-26) showed was already live: 42 repositories across 11 GitHub owners were armed with a payload hidden in files too large for GitHub code search, and 18 npm packages were published between 10-19 and 10-25. It steals developer, cloud and CI credentials, plants execution hooks for Claude, Gemini, Cursor and VS Code, spreads through the victim's npm and GitHub access, and carries the Mini Shai-Hulud wiper: **revoking the stolen GitHub token from a still-infected machine deletes the home directory.** Isolate and remove persistence first, then revoke and rotate.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| npm | `event-emitter-testmetest` | 1.0.4 to 1.0.7, 3.0.0, 3.0.1, 4.1.0, 5.0.0 | remove | not re-checked this sweep | JFrog inventory 10-26 |
| npm | `data-pipeline-testmetest` | 2.0.1 | remove | not re-checked | JFrog |
| npm | `event-bus-lite-testmetest` | 0.0.1, 0.0.2, 0.0.6 | remove | not re-checked | JFrog |
| npm | `pixel-map-testmetest` | 0.0.1 to 0.0.3 | remove | not re-checked | JFrog |
| npm | `path-stream-utils-testmetest` | 0.0.1, 0.0.2 | remove | live per SafeDep (10-26) | SafeDep, JFrog |
| npm | `@iobandamwer/cache-helper` | 1.0.2 to 1.0.8 | remove | live per SafeDep (10-26) | SafeDep, JFrog |
| npm | `@iobandamwer/native-helper` | 0.0.1 | remove | live per SafeDep (10-26) | SafeDep, JFrog |
| npm | `net-codec-testmetest`, `log-rotate-testmetest`, `log-sink-testmetest`, `npm-publish-testmetest`, `retry-utils-testmetest` | 1.0.1 (retry-utils: 1.0.3) | remove | not re-checked | JFrog |
| npm | `test-brotli-testmetest`, `test-brotli2-testmetest` | 1.0.0 | remove | not re-checked | JFrog |
| npm | `sdk-utils-testmetest`, `kvarzo8f3atestmetest`, `canvas-draw-testmetest`, `string-helpers-testmetest`, `form-render-testmetest`, `task-runner-testmetest`, `byte-parser-testmetest` | all versions | remove | not re-checked | SafeDep list |

JFrog's inventory covers 25 package names and 82 version records; the table carries the names both reports print. JFrog links the operator's infrastructure to the campaign that exploited cPanel/WHM CVE-2026-41940 (KEV since 2026-04-30) and found no confirmed downstream cPanel compromise. The 42 repositories are listed in JFrog's post; the account hijacks began as early as July.

## Am I affected?
- `grep -rE 'testmetest|@iobandamwer/' package.json package-lock.json pnpm-lock.yaml yarn.lock` across every project; `npm ls -g --depth=0 | grep -E 'testmetest|iobandamwer'`.
- A `node-gyp` rebuild or `postinstall` you did not expect, a hidden `.napi_cache` file in a dependency, a dotfile under `/tmp` named after a process id, or an unexplained `%TEMP%\.nc*.js`.
- Hook or settings entries you did not add in Claude Code, Gemini CLI, Cursor or VS Code configuration; new workflow files or `ci-sync`-style branches in your repositories; commits from your account you did not make.
- Wrapper or data files of 12 to 14 MB committed to a repository without explanation.

## If you are affected
1. Disconnect the machine from the network **before** touching tokens; the wiper triggers on revocation.
2. Remove the packages, the planted hooks and any scheduled task or login item they added; reimage if unsure. Only then revoke and rotate: GitHub, npm, PyPI, SSH, cloud (AWS, GCP, Azure), Vault, Kubernetes, browser-saved logins, every `.env` the user could read. [If you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
3. Audit every repository and package the account can publish to for commits and releases made since July.

## Prevention
- [npm hardening](../prevention/npm-hardening.md): `ignore-scripts`, a cooldown on new versions, trusted publishing.
- [CI/CD hardening](../prevention/ci-cd-hardening.md): short-lived tokens, so a stolen one cannot publish.

## Sources
- [SafeDep — testmetest npm worm, a Miasma variant](https://safedep.io/testmetest-npm-worm-miasma-variant) — fetched 2026-10-26 (2026-10-22, updated 10-26): the package list, which were still live, the loader behaviour categories, the credential targets.
- [JFrog Security Research — Beyond testmetest: 42 hijacked GitHub repositories](https://research.jfrog.com/post/beyond-testmetest-42-hijacked-github-repos/) — fetched 2026-10-26 (2026-10-26, Guy Korolevski and Yair Benamou): the repository and owner counts, the version inventory, the hidden-payload size, the anti-analysis checks, the cPanel link.
- [The Register — Worm armed 42 GitHub repos by hiding a payload too big to fail](https://www.theregister.com/2026/10/26/worm-armed-42-github-repos-by-hiding-a-payload-too-big-to-fail/5305570) — fetched 2026-10-26: press account and the attribution quotes.
- Related: [Phantom Gyp / Miasma wave 4](2026-06-phantom-gyp-miasma-wave4.md), [TanStack Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md) for the wiper, [MALFEX](2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader.md) for the native-addon loader class.
