---
id: 2026-10-subql-common-npm-postinstall-stealer-ci-workflow-injection
title: "@subql/common@5.8.3 (SubQuery, the web3 indexing framework; 18k-star monorepo) shipped a postinstall + on-import credential stealer and remote shell on 2026-10-05 — harvests .npmrc, .env, SSH, cloud, Kubernetes, Vault and AI-agent config files, reads the GitHub Actions runner process for tokens, and pushes a disguised CodeQL workflow to dump repository secrets; 19 of 77 @subql packages resolve to it; removed from the registry within hours"
date_disclosed: 2026-10-05
last_updated: 2026-10-05
severity: high
status: unconfirmed
ecosystems: [npm, github-actions, ci-cd]
tools_affected: ["@subql/common 5.8.3 (and the 5.8.3-onf-rt1 pre-release published 32 minutes earlier)", "@subql/cli 6.6.3, @subql/node-core 19.3.1, @subql/query 2.25.0 and 16 other @subql packages whose latest version resolves to it", "any project or CI pipeline that ran `npm install` with a floating @subql range on 2026-10-05", "GitHub Actions runners that installed it"]
tags: [supply-chain, npm, postinstall, on-import-payload, credential-theft, github-actions, runner-memory, workflow-injection, remote-shell, ai-agent-config-theft, web3, unconfirmed]
---

## TL;DR

On **2026-10-05 at 11:56 UTC** a new version of **`@subql/common`** — the shared library under SubQuery's indexing CLI, node and query packages — was published to npm as **5.8.3**, 32 minutes after a pre-release **`5.8.3-onf-rt1`** under a dist-tag named `redteam`. StepSecurity's analysis of 5.8.3, published the same day, says the version adds a `postinstall` hook and a 62 KB `dist/project/readers/manifest-cache.js` that is also exported from `index.js`, so the payload runs **on install and again on every import**, in a detached child process. Decoded, it collects `.npmrc`, `.env`, AWS/GCP/Azure credentials, SSH keys, kubeconfig, Vault tokens, cryptocurrency wallet paths **and AI-agent configuration files**; on Linux CI it reads the GitHub Actions runner process for the job token, uses stolen GitHub tokens to push a branch carrying a `.github/workflows/codeql_analysis.yml` that dumps repository secrets to an artifact, and opens a remote shell. By the time this sweep queried the registry the version was **gone** (`version not found: 5.8.3`), `latest` pointed back at 5.8.2, and the `redteam` pre-release was still listed. **If you installed any @subql package between roughly 11:56 UTC and the removal, treat the machine or runner as compromised, rotate everything it could read, and check your repositories for a CodeQL workflow you did not write.** Status is `unconfirmed` because the only analysis is StepSecurity's and SubQuery had not responded on the issue when this sweep read it; the registry removal is the one independent signal.

## What happened

- **The package.** `@subql/common` is the shared types-and-readers library that `@subql/cli`, `@subql/node-core`, `@subql/query` and the chain-specific node packages depend on. The `subquery/subql` monorepo has ~18k GitHub stars (per the Hacker News submission); the package itself had **4,380 downloads in the week ending 10-04**, with `@subql/cli` at 2,374 and `@subql/node-core` at 2,011 — a web3 developer audience, not a general one, but one that runs the CLI in CI and holds chain RPC keys, deployer keys and cloud credentials.
- **The publication.** The registry's `time` field shows **`5.8.3-onf-rt1` at 11:24 UTC** and **`5.8.3` at 11:56 UTC** on 2026-10-05; the previous release, 5.8.2, was 2025-11-20. The pre-release carries a `redteam` dist-tag. No source this sweep read explains the pre-release, the tag name or who published either version; StepSecurity's issue asks the maintainers to "investigate commit 506863d and the release workflow for unauthorized modifications" and to "rotate npm trusted-publisher settings and all CI secrets," which is the shape of a publish-pipeline compromise, but that is the reporter's request, not a finding.
- **The payload (StepSecurity's analysis).** 5.8.3 adds a `postinstall` script, a new `dist/project/readers/manifest-cache.js` (62,124 bytes) and a one-line export of it from `index.js`. The file unwraps three layers (base64/XOR, PBKDF2-HMAC-SHA256, AES-256-GCM) into an ~83 KB bundle that: harvests environment variables and `gh auth token` output; reads `.npmrc`, `.env`, SSH keys, AWS/GCP/Azure credential files, kubeconfig and Kubernetes service-account tokens, HashiCorp Vault tokens, wallet directories and **AI-agent configuration files**; on Linux runners **reads the `Runner.Worker` process memory for the GitHub Actions job token**; uses any GitHub token it finds to **push a branch containing `.github/workflows/codeql_analysis.yml`** that writes the repository's secrets to a workflow artifact; encrypts the collection (RSA-OAEP + AES-256-GCM) and posts it to a command-and-control host; and keeps a channel open for shell command execution and interactive PTY sessions. Because it runs from `index.js` as well as from `postinstall`, **`--ignore-scripts` does not prevent execution** — the first `require('@subql/common')` does.
- **Blast radius.** StepSecurity reviewed 77 `@subql` packages and found **19 whose latest version had a dependency path to `@subql/common@5.8.3`** — 16 directly (including `@subql/cli@6.6.3`, `@subql/node-core@19.3.1`, `@subql/query@2.25.0`) and three through an intermediate package. A floating `^5.8.2` range resolved to the malicious version for the window it was live.
- **Takedown.** As of this sweep's registry query (2026-10-05, afternoon UTC) `registry.npmjs.org/@subql/common/5.8.3` returns `version not found`, `dist-tags.latest` is `5.8.2`, and `5.8.3-onf-rt1` is still listed under `redteam` with its own tarball. Who removed 5.8.3 — npm, or the maintainers — is not stated anywhere this sweep could read. The GitHub issue (subquery/subql #3047, opened by a StepSecurity engineer) had **no maintainer reply** at fetch time.

**The pattern.** This is the Shai-Hulud/ChainDrop family's tradecraft on a smaller package: runner-memory token theft, a workflow pushed under a plausible security-tool name to exfiltrate secrets through artifacts, and the AI-agent config directories added to the harvest list — SafeDep's 2026-10-02 reading of Google Cloud's AI Risk and Resilience Report says the Shai-Hulud family now searches 469 credential locations, up from 189, with AI tool settings files among the additions (see the [Mandiant case study](2026-09-mandiant-hijacked-coding-assistant-session-shai-hulud-saas.md) for the report itself). The on-import execution path is the part a defender most often misses: a lockfile that pinned 5.8.3 during the window keeps re-running the payload on every process start until it is changed.

## Am I affected?

```bash
# Did the malicious version land in any lockfile or node_modules?
grep -rn '"@subql/common"' package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null | grep -n '5\.8\.3'
find . -path '*/node_modules/@subql/common/package.json' -exec grep -H '"version"' {} \;
# The payload file is the tell (absent in 5.8.2)
find . -path '*/node_modules/@subql/common/dist/project/readers/manifest-cache.js'
# CI: any run of a @subql install on 2026-10-05 after 11:24 UTC on a runner with a GITHUB_TOKEN
# Repos: a workflow you did not write
git log --all --diff-filter=A -- .github/workflows/codeql_analysis.yml
```

Any hit on `5.8.3` or `5.8.3-onf-rt1`, or the `manifest-cache.js` file, means the payload executed on that machine or runner.

## If you are affected

1. Remove `node_modules`, pin `@subql/common` to `5.8.2` (or whatever the maintainers publish as the clean successor) and reinstall from a clean checkout. Rebuild CI runners and any container image that installed during the window from trusted bases.
2. Rotate everything the payload lists: npm tokens (`.npmrc`), `.env` secrets, SSH keys, AWS/GCP/Azure credentials, kubeconfig and service-account tokens, Vault tokens, GitHub PATs and `gh` CLI tokens, and any API keys stored in AI-agent configuration directories (`~/.claude`, `~/.codex`, `~/.cursor`, MCP configs) — [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
3. In every repository a compromised token could push to: delete unexpected branches and any `codeql_analysis.yml` you did not author, delete workflow artifacts from those runs, rotate repository and organisation secrets, and audit the Actions log for runs you did not trigger — [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
4. Treat the host as having had an interactive shell: review outbound connections from the install window, and follow [if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).

## Prevention

- Pin exact versions and commit lockfiles; a floating `^` range is what resolved to 5.8.3. A cooldown rule (do not adopt a version published in the last N days) would have skipped a 32-minute-old release.
- `--ignore-scripts` is necessary but **not sufficient** against on-import payloads; combine it with install-time scanning (StepSecurity's, Socket's or Aikido's) and run installs in CI on runners with no ambient cloud credentials — [prevention/npm-hardening.md](../prevention/npm-hardening.md), [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- Keep AI-agent configuration out of the credential blast radius: API keys in the OS keychain or a secrets manager, not in `~/.claude/settings.json`-style files, since those directories are now on the harvest list of every major stealer family — [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Alert on new workflow files pushed by a token rather than a person, and on artifacts larger than your builds produce.

## Why this matters for vibe coders

A web3 indexer is not a vibe-coding tool, but the payload's harvest list is a snapshot of what attackers now expect to find on a developer machine in 2026: cloud and registry credentials, **and the agent config files that hold model-provider keys and MCP server secrets**. Whatever package you install next, assume its postinstall and its first import run with everything in your home directory. If you let an agent run `npm install` for you, that agent's own credentials are in scope.

## Sources

- [StepSecurity — SubQuery Ecosystem Compromise: Hidden Credential Theft and Backdoors](https://www.stepsecurity.io/blog/subql-ecosystem-compromised) — 2026-10-05, the primary analysis: files added in 5.8.3, the three-layer unpacking, the harvest list including AI-agent configs, runner-memory extraction, the CodeQL-named workflow injection, the 77-package / 19-affected dependency review, the on-import execution path. Fetched 2026-10-05.
- [subquery/subql issue #3047 — "[security]: Malicious release @subql/common@5.8.3 (postinstall credential stealer)"](https://github.com/subquery/subql/issues/3047) — opened 2026-10-05 by a StepSecurity engineer; the publish timestamp, the 62,124-byte file, the `index.js` export, the requested remediation (unpublish, investigate commit 506863d and the release workflow, rotate trusted-publisher settings). No maintainer reply at fetch time (2026-10-05).
- [npm registry — `@subql/common` `time` and `dist-tags`](https://registry.npmjs.org/@subql/common) — queried 2026-10-05: `5.8.3-onf-rt1` 11:24 UTC, `5.8.3` 11:56 UTC, `latest` → 5.8.2, dist-tag `redteam` → 5.8.3-onf-rt1; `/@subql/common/5.8.3` returns `version not found`.
- [npm downloads API — `@subql/common`, `@subql/cli`, `@subql/node-core` (week ending 2026-10-04)](https://api.npmjs.org/downloads/point/last-week/@subql/common) — 4,380 / 2,374 / 2,011.
- [Hacker News — "Subql/common 5.8.3 compromised: postinstall stealer in 18k-star SubQuery repo"](https://hn.algolia.com/api/v1/search_by_date?query=subquery&tags=story) — 2026-10-05 submission linking the issue; the star count.
- [SafeDep — An Attacker Hijacked an AI Coding Assistant to Spread a Worm](https://safedep.io/ai-coding-assistant-hijack-shai-hulud/) — 2026-10-02, secondary; the 189 → 469 credential-location figure attributed to Google Cloud's AI Risk and Resilience Report 2026. Fetched 2026-10-05.
- Related in this repo: [Mandiant hijacked coding-assistant session → Shai-Hulud](2026-09-mandiant-hijacked-coding-assistant-session-shai-hulud-saas.md), [ChainDrop / keyv](2026-08-keyv-mini-shai-hulud-npm-worm.md), [Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md).
