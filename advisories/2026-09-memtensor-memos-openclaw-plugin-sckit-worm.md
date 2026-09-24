---
id: 2026-09-memtensor-memos-openclaw-plugin-sckit-worm
title: "MemTensor's official OpenClaw memory plugin (@memtensor/memos-cloud-openclaw-plugin 0.1.21 / 0.1.23 / 0.1.25) and MemoryOS 2.0.34 on PyPI were published from stolen release tokens with a credential-stealing Go implant ('sckit') that runs when the agent gateway starts and on memory-recall events; four researchers confirmed it within hours on 2026-09-23 — clean baselines are 0.1.20 and 2.0.33"
date_disclosed: 2026-09-23
last_updated: 2026-09-24
severity: high
status: active
ecosystems: [npm, pypi, ai-agents, github-actions]
tools_affected: ["@memtensor/memos-cloud-openclaw-plugin 0.1.21, 0.1.23, 0.1.25", "MemoryOS 2.0.34 (PyPI, quarantined)", "OpenClaw gateways running the MemOS Cloud plugin", "MemOS (memos) Python users"]
tags: [supply-chain, npm, pypi, credential-theft, ci-token-theft, openclaw, agent-memory, go-implant, active]
---

## TL;DR
On **2026-09-23**, between 02:23 and 05:25 UTC, someone holding MemTensor's registry publish tokens released three malicious versions of **`@memtensor/memos-cloud-openclaw-plugin`** — the official long-term-memory plugin for OpenClaw agents — and one malicious version of **`MemoryOS`** on PyPI (the `memos` module of the ~11.5K-star MemOS framework). None of the four releases corresponds to a commit or tag in either repository. Each bundles a launcher plus platform-specific Go binaries that StepSecurity, SafeDep, Socket and Aikido independently identified as a **credential stealer** aimed at developer and cloud secrets in the user's home directory; the npm plugin starts it when the OpenClaw gateway boots and on memory-recall events, and the PyPI package starts it on import. SafeDep and Aikido classify it as a worm because the package carries templates for re-publishing itself from CI with credentials it finds. **Clean baselines: 0.1.20 (npm, 2026-08-03) and 2.0.33 (PyPI).** As of this sweep npm's `latest` tag points at the clean 0.1.24, but the malicious versions are neither deprecated nor removed; PyPI has quarantined `MemoryOS` (its file index is empty). The only maintainer-side record is the reporter's GitHub issue; there is no vendor advisory yet.

## What happened

**Timeline (UTC, 2026-09-23; SafeDep's write-up and the npm registry's `time` field agree).** Malicious commits were pushed to and deleted from a branch of the plugin repository between 00:48 and 02:03. npm **0.1.21** was published at 02:23:04, a clean **0.1.22** at 03:45:44, malicious **0.1.23** at 03:49:20, clean **0.1.24** at 04:33:30, malicious **0.1.25** at 04:36:58 — StepSecurity notes each malicious release landed within about three and a half minutes of the clean one before it, i.e. someone was re-publishing the payload as fast as it was being reverted. PyPI **MemoryOS 2.0.34** was uploaded at 05:24–05:25. The previous legitimate plugin release, 0.1.20, dates from 2026-08-03; the last tag in the repository is v0.1.20.

**How the releases were made.** The reporter's issue (`MemTensor/MemOS-Cloud-OpenClaw-Plugin#173`, opened 2026-09-23) shows the published tarballs contain ~7.4 MB of files that exist nowhere in git history and concludes the npm publish token was compromised. SafeDep traced both publishes to the project's **GitHub Actions release pipelines**: the attacker altered the release workflow so that the registry token available to the publish step was exposed to the implant before the job ended. Socket's write-up (as quoted by The Hacker News) lists the credential targets as npm, PyPI, GitHub, GitLab, AWS, HashiCorp Vault and SSH material; StepSecurity adds Hugging Face, Slack, Stripe and SendGrid keys and generic token-shaped strings. StepSecurity's most important observation for agent operators: on the npm side the launcher **passes the host process environment and, during recall, the user's prompt text** to the binary — so an OpenClaw gateway with this plugin loaded leaked its environment and whatever users typed to the agent during the window.

**Why the package matters to this audience.** This is the vendor-official memory integration for OpenClaw, a project this repo already tracks for [Claw Chain](2026-05-openclaw-claw-chain.md) and the [75-advisory batch](2026-09-openclaw-2026-8-1-advisory-batch.md); a memory plugin runs inside the gateway process with the gateway's credentials and sees every recall. MemOS itself is a general agent-memory framework used well outside OpenClaw. The registry counts are small (the plugin pulled 29 downloads in the week to 2026-09-21, before the incident), so this is a targeted compromise of an agent-ecosystem package rather than a mass event — but an agent plugin is the highest-value place to sit for this kind of payload, and the CI-token theft means the maintainers' other packages should be treated as at risk until they rotate.

**Vendor response.** None published as of 2026-09-23. The npm `dist-tags` show the maintainers (or npm) have re-pointed `latest` to 0.1.24 and added tags named `clean-inverse-0-1-23` → 0.1.22 and `clean-inverse-0-1-25` → 0.1.24, which is a manual revert, not a takedown: `npm install` of an explicit `0.1.21`, `0.1.23` or `0.1.25`, or a lockfile that resolved one, still gets the payload. PyPI's simple index for `memoryos` returns no files (project quarantined, per The Hacker News). No issue mentioning 2.0.34 exists on the MemOS repository.

## Am I affected?

```bash
# npm — the plugin, any lockfile, any OpenClaw install
grep -rE '"@memtensor/memos-cloud-openclaw-plugin".*"0\.1\.2[135]"' package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
npm ls @memtensor/memos-cloud-openclaw-plugin 2>/dev/null
ls -la node_modules/@memtensor/memos-cloud-openclaw-plugin/.sckit 2>/dev/null   # present only in the malicious versions
# PyPI
pip show MemoryOS 2>/dev/null | grep -i '^version'    # 2.0.34 is the bad one; 2.0.33 is clean
# Runtime and on-disk signals (from the StepSecurity / SafeDep IOC lists)
pgrep -af sckit
ls -d "$HOME/.openclaw/.cache/runtime" "$HOME/.memos/.cache/runtime" 2>/dev/null
# CI: a workflow you did not write
git log --all --oneline -- .github/workflows/runtime-update.yml
```

- **Affected if:** any host or gateway installed one of the three npm versions or `MemoryOS 2.0.34`, or an OpenClaw gateway auto-updated the plugin during 2026-09-23. StepSecurity's IOC list gives SHA-256 hashes for all twelve binaries; any outbound connection to a `skyleen[.]fr` subdomain from a developer machine, agent host or CI runner is a compromise signal.
- **Not affected if:** you are pinned at `0.1.20` / `2.0.33` or earlier and no lockfile or gateway resolved a later version.

## If you are affected

1. Stop the gateway or process, kill any `sckit` process, remove the package and the state directories above, and reinstall from the clean baseline.
2. **Rotate everything a process running as that user could read**: registry publish tokens first (npm, PyPI), then GitHub/GitLab tokens and SSH keys, cloud credentials, Vault tokens, AI-provider keys, and any secret in the gateway's environment — follow [if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md), [if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md) and [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Treat **prompt text sent to the agent during the window as disclosed** (StepSecurity): review what users pasted into OpenClaw sessions on affected gateways.
4. Audit repositories the affected identity can push to for workflows or `.sckit/` directories you did not add, and check your own packages' recent publishes — the campaign's stated goal is to re-publish from stolen tokens.
5. Maintainers of packages published from GitHub Actions: this is a reason to move to **trusted publishing / OIDC** with no long-lived registry token in the job, and to require provenance ([prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)).

## Prevention

- **Agent plugins are dependencies with the gateway's privileges** — pin them, review upgrades, and do not let a gateway auto-update plugins from `latest` ([prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) applies to memory and channel plugins as much as MCP servers).
- **Install-time script blocking does not help here**: the npm payload runs from the plugin's normal entry points at gateway start, and the PyPI payload runs on import ([prevention/npm-hardening.md](../prevention/npm-hardening.md) explains why `ignore-scripts` is necessary but not sufficient). A scanner that looks at package *contents* — a 7.4 MB stripped binary in a JavaScript plugin is the tell — and egress control on agent hosts are the controls that fire.
- A package whose releases stop matching its git tags is the earliest public signal; the reporter found this by diffing the tarball against the repository. [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).

## Update 2026-09-24 — Socket and SafeDep add the repository-side timeline and frame `sckit` as a reusable implant framework

Two more primaries were fetched on 2026-09-24. **Socket** (Kush Pandya / Socket Threat Research, 2026-09-23) dates the malicious commits to **00:48 UTC on 09-23**, ahead of the first registry artifact at 02:23, and reads that ordering as "repository compromise preceded package publication"; the npm releases came from the legitimate `leason1974` account **"without a `gitHead`"**, i.e. published outside the CI workflow. Socket's IOC set matches StepSecurity's and Aikido's — `skyleen[.]fr` subdomains with per-package campaign identifiers (`cloud-openclaw-semi-nuclear`, `memos-semi-nuclear`) and a `sckit.runtime.v1` configuration schema — and its remediation is the same: pin 0.1.20 / 2.0.33, rotate everything a gateway could read, delete `~/.openclaw/.cache/runtime/` and `~/.memos/.cache/runtime/`, block the domain, audit publish activity. **SafeDep**'s companion post, "sckit: A New Go Implant Framework for Supply Chain Worms" (2026-09-23), treats the binary as a framework rather than a one-off: cross-platform, receives **signed tasks** from its C2, profiles the host and filters victims by geography, runs remotely delivered modules over encrypted channels, and carries propagation logic for npm, PyPI and GitHub Actions workflows; it shares "no code or infrastructure in common with … other publicly reported npm worms" (contrast the [Mini Shai-Hulud lineage](2026-05-tanstack-mini-shai-hulud.md)), and the operator built a **separate binary per target**. `skyleen[.]fr` was registered on **2026-09-15** — eight days before the publish — and re-registered after an earlier expiry. Nothing in either post changes the affected-version list or the status; the practical addition is that a framework built for reuse will reappear under other package names, so the detection to keep is the behaviour (a multi-megabyte stripped Go binary inside a JavaScript or Python package, launched from a normal code path, talking to a fresh domain), not the MemTensor names.

## Sources
- [StepSecurity — Sckit Supply Chain Worm Hits MemTensor npm & PyPI scopes](https://www.stepsecurity.io/blog/sckit-supply-chain-worm-hits-memtensor-npm-pypi-scopes) — primary, 2026-09-23: publish timestamps, the launcher and binary layout, the environment/prompt-text pass-through, credential targets, per-campaign exfil hosts, SHA-256 hashes for all twelve binaries, state directories, remediation. Fetched 2026-09-23.
- [SafeDep — MemTensor npm and PyPI Packages Hit by a Go Worm](https://safedep.io/memtensor-sckit-worm-npm-pypi) — primary, 2026-09-23: the 00:48–05:25 UTC timeline, the release-pipeline token theft on both registries, the clean/malicious version table, the `runtime-update.yml` persistence marker. Fetched 2026-09-23.
- [Aikido — Novel supplychain.local Go worm appears](https://www.aikido.dev/blog/supplychain-local-memtensor-npm-pypi) — primary, 2026-09-23 (Oliver Smith): why it is classed as a worm, the campaign name from the binary's own module path, the six exfil subdomains and their shared IP. Fetched 2026-09-23.
- [The Hacker News — Compromised MemTensor Packages Deliver sckit Credential Stealer via npm and PyPI](https://thehackernews.com/2026/09/compromised-memtensor-packages-deliver.html) — 2026-09-23: synthesises all four researcher reports (Socket's is quoted here; its post was not fetched directly), notes the PyPI quarantine and that 0.1.22 / 0.1.24 are clean. Fetched 2026-09-23.
- [MemTensor/MemOS-Cloud-OpenClaw-Plugin issue #173 — Malicious versions 0.1.21 and 0.1.23 published to npm; publish token appears compromised](https://github.com/MemTensor/MemOS-Cloud-OpenClaw-Plugin/issues/173) — the reporter's diff of tarball vs. repository (no matching commits or tags; last tag v0.1.20 of 2026-08-03) and recommended maintainer actions; no maintainer reply as of fetch. Fetched 2026-09-23.
- npm registry record for [`@memtensor/memos-cloud-openclaw-plugin`](https://registry.npmjs.org/@memtensor%2Fmemos-cloud-openclaw-plugin), fetched 2026-09-23: version timestamps quoted above; `dist-tags` `latest` → 0.1.24, `clean-inverse-0-1-23` → 0.1.22, `clean-inverse-0-1-25` → 0.1.24; no version marked deprecated. `api.npmjs.org`: 29 downloads for 2026-09-15 → 09-21. PyPI simple index for `memoryos`, fetched 2026-09-23: zero files served.
- **2026-09-24 update sources** — [Socket — MemTensor NPM and PyPI packages compromised with credential stealer](https://socket.dev/blog/memtensor-compromise) (2026-09-23: the 00:48 UTC commit time, the four releases 02:23–05:25 UTC, `leason1974` publishes without `gitHead`, campaign identifiers, `sckit.runtime.v1`, remediation). Fetched 2026-09-24. [SafeDep — sckit: A New Go Implant Framework for Supply Chain Worms](https://safedep.io/sckit-go-implant-framework/) (2026-09-23: framework capabilities, signed tasking, per-target binaries, no shared code with prior npm worms, domain registration 2026-09-15). Fetched 2026-09-24.
