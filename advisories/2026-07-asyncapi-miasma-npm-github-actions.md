---
id: 2026-07-asyncapi-miasma-npm-github-actions
title: "AsyncAPI npm compromise — GitHub Actions 'pwn request' steals CI token, publishes Miasma RAT through the project's own OIDC pipeline (July 2026)"
date_disclosed: 2026-07-14
last_updated: 2026-07-14
severity: critical
status: active
ecosystems: [npm, github-actions]
tools_affected: [asyncapi-generator, claude-code, vscode]
tags: [supply-chain, npm, github-actions, pwn-request, oidc-provenance-abuse, miasma, credential-theft, ai-config-poisoning, ipfs-c2, crypto-wallet]
---

## TL;DR
An attacker abused a **`pull_request_target` "pwn request"** misconfiguration in the AsyncAPI generator repo's CI to steal the `asyncapi-bot` GitHub token, then used it to get a malicious commit onto the `next` branch and trigger the project's **own legitimate, OIDC-signed release pipeline** — publishing five trojanized packages (**`@asyncapi/generator`, `generator-helpers`, `generator-components`, `@asyncapi/specs`**) with a combined **~3M weekly downloads** on **2026-07-14**. The payload fires at import/require time, pulls a second stage from IPFS, and drops a 744-module RAT ("Miasma") with six C2 channels — including an Ethereum smart contract and BitTorrent DHT — that steals browser/SSH/cloud/npm/GitHub credentials and crypto wallets, and is reported to write persistence into AI-coding-tool config. No patched version has been announced as of this writing — **treat any host that ran the affected versions as compromised.**

## What happened
`@asyncapi/generator` and its sibling packages are official code-generation tooling from the AsyncAPI Initiative (a CNCF-adjacent spec used to describe event-driven/async APIs), together pulling roughly **3 million downloads a week**.

**Initial access — a "pwn request."** Wiz Research traced the entry point to a `pull_request_target`-triggered workflow (the repo's docs-preview/Netlify build) that ran with access to repository secrets but checked out the **pull request's own code** rather than the base branch — the classic "pwn request" GitHub Actions misconfiguration (the same root-cause class already tracked in this repo's [Cordyceps](2026-06-cordyceps-cicd-github-actions.md) advisory). The attacker buried a malicious PR (#2155) among 36 low-signal spam PRs on **2026-07-14 05:08 UTC**; the vulnerable workflow ran at 05:16 UTC and exfiltrated the `asyncapi-bot` personal access token.

**Publish — through the project's own trusted pipeline, not a stolen npm token.** Socket's independent analysis of the published artifacts traces the actual publish to the repo's `release-with-changesets.yml` workflow, run under **`GitHub Actions <npm-oidc-no-reply@github.com>`** — i.e. the attacker never touched an npm publishing credential at all. A malicious commit landed on the `next` branch (authored as `"Your Name <you@example.com>"`, GitHub user `invalid-email-address`) at **06:58 UTC**, and the existing release automation did the rest, publishing with **valid npm OIDC provenance**. (Wiz and Socket describe the compromised-CI-token entry point and the publish-time mechanism from two different angles; both are consistent with a single chain — stolen PAT → malicious commit → the project's own trusted publish workflow fires — but neither source individually confirms every link, so treat the middle step as reported rather than independently re-verified by this advisory.)

**Packages and versions:**

| Package | Malicious version(s) | Published (UTC) |
|---|---|---|
| `@asyncapi/generator-helpers` | 1.1.1 | 07:10:42 |
| `@asyncapi/generator-components` | 0.7.1 | 07:10:44 |
| `@asyncapi/generator` | 3.3.1 | 07:10:48 |
| `@asyncapi/specs` | 6.11.2-alpha.1 | 08:06:20 |
| `@asyncapi/specs` | 6.11.2 | 08:30:09 |

**Payload.** The malicious code is a small, obfuscated statement injected at module load — it runs on `import`/`require()`, **not** on `npm install`, so it doesn't need a lifecycle hook at all. It spawns a detached, output-suppressed `node -e` child process that:

1. **Stage 1** fetches an encrypted blob from IPFS (`ipfs.io/ipfs/QmQobZSp1wRPrpSEQ56qnyq7ecZh5Bg5k1fnjt4SUwwHb9`, ~8.25 MB) and writes it to a path disguised as Node.js runtime state (`~/.local/share/NodeJS/sync.js` on Linux, `~/Library/Application Support/NodeJS/sync.js` on macOS, `%LOCALAPPDATA%\NodeJS\sync.js` on Windows).
2. **Stage 2** decrypts that blob (HKDF-SHA256 → AES-256-GCM, with an extra ROT94 transform layer) into a ~3 MB payload that self-identifies internally as **"miasma-train-p1"** — a 744-module RAT framework.
3. The framework installs persistence via a **`miasma-monitor` systemd user service** on Linux and opens **six separate C2 channels**: direct HTTP to `85.137.53.71` (ports 8080/8081/8091), Nostr relays, a second IPFS hash, an Ethereum smart contract (`0x12c37A86a0Ed0beBe5d1d6a43E42f07860eAc710`), BitTorrent DHT, and mDNS.
4. Target data: browser passwords/cookies (Chrome, Brave, Firefox, Edge), SSH keys, npm/GitHub tokens, AWS credentials, macOS Keychain, and cryptocurrency wallets, plus a remote command channel for arbitrary file operations and exfiltration.

This is the same **Miasma/Shai-Hulud lineage** already tracked in this repo across several 2026 waves (LeoPlatform+Go, `@immobiliarelabs` Backstage, Wave 5 Microsoft Azure/mantine-datatable, `@redhat-cloud-services`) — but a **new entry point**: prior waves compromised an npm publishing token or a maintainer's GitHub account directly, whereas this wave got there via CI-token theft through a `pull_request_target` misconfiguration and rode the project's own OIDC-signed publish pipeline, defeating the "check for valid provenance" mitigation this repo has flagged before (see the caution on provenance-as-identity-not-integrity). Wiz's report additionally states the payload writes malicious entries into AI-coding-assistant configuration (`.vscode/tasks.json`, `.claude/settings.json`) as an auto-execution/persistence mechanism, consistent with the pattern documented in the Miasma Wave 5 and `@immobiliarelabs` advisories — flag this specifically for readers of this repo.

## Am I affected?

```bash
# Check whether any of the compromised versions are in your dependency tree
npm ls @asyncapi/generator @asyncapi/generator-helpers @asyncapi/generator-components @asyncapi/specs --all 2>/dev/null
grep -E '"@asyncapi/(generator|generator-helpers|generator-components|specs)".*"(3\.3\.1|1\.1\.1|0\.7\.1|6\.11\.2(-alpha\.1)?)"' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Hunt for the dropped Stage 2 file
find ~/.local/share/NodeJS ~/Library/Application\ Support/NodeJS "$LOCALAPPDATA/NodeJS" -name 'sync.js' 2>/dev/null

# Hunt for the persistence service
systemctl --user list-units | grep -i miasma
ls -la ~/.config/.miasma 2>/dev/null

# Look for outbound connections to the C2 IP
sudo lsof -i | grep 85.137.53.71
```

### IOCs

| Type | Value |
|---|---|
| Malicious versions | `@asyncapi/generator@3.3.1`, `@asyncapi/generator-helpers@1.1.1`, `@asyncapi/generator-components@0.7.1`, `@asyncapi/specs@6.11.2`, `@asyncapi/specs@6.11.2-alpha.1` |
| Primary C2 | `85.137.53.71` (ports 8080, 8081, 8091) |
| IPFS payload hashes | `QmQobZSp1wRPrpSEQ56qnyq7ecZh5Bg5k1fnjt4SUwwHb9`, `Qmet4fhsAaWMBUxNDfREHwgiyDeSWy4YSYs9wiKUW5jGyf` (react-sdk variant) |
| Ethereum C2 contracts | `0x12c37A86a0Ed0beBe5d1d6a43E42f07860eAc710` |
| Persistence | `miasma-monitor.service` (systemd, Linux); `.config/.miasma` lock files |
| Compromise window | 2026-07-14, 05:08–08:30 UTC |

If any affected version ran on a dev machine or CI runner, treat the host as fully compromised: rotate browser-stored credentials, move crypto wallet funds to a fresh wallet on a clean device, and rotate every cloud/npm/GitHub credential resident in that environment — including any AI-coding-tool API keys or MCP tokens stored in `.claude/`, `.cursor/`, or similar config directories.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — this campaign's entry point was a stolen CI PAT, not a developer's own token, but the rotation steps are the same if your org's CI also uses `pull_request_target` with secrets.

## Prevention
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — audit every `pull_request_target` workflow in your org for the "pwn request" pattern: it must **never** check out and execute PR-head code while holding access to secrets.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — a green OIDC/provenance badge proves *who* published a package, not that the build inputs were trustworthy; it does not substitute for pinning and auditing.
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — this payload fires on import, not install, so `--ignore-scripts` provides no protection here; pin dependency versions and diff `node_modules` on upgrade.

## Why this matters for vibe coders
This is the first Miasma-lineage wave documented in this repo where the entry point is **CI-token theft via a `pull_request_target` misconfiguration** rather than a compromised npm account or maintainer GitHub credential — meaning the malicious release carried fully valid OIDC provenance from the project's own trusted pipeline. If your team relies on "verified provenance" as a supply-chain signal, this is a concrete example of why that's necessary but not sufficient. It's also the first entry in this Miasma lineage reported to specifically target AI-coding-tool config files as a persistence surface, alongside the already-documented crypto/cloud/browser credential harvesting.

## Sources
- [Wiz — M-RED-TEAM: AsyncAPI Supply Chain Compromise via GitHub Actions](https://www.wiz.io/blog/m-red-team-asyncapi-supply-chain-compromise-via-github-actions)
- [Socket — Compromised AsyncAPI npm Packages Distribute the Miasma RAT](https://socket.dev/blog/asyncapi-supply-chain-attack)
- [The Hacker News — Compromised AsyncAPI npm Packages](https://thehackernews.com/2026/07/compromised-asyncapi-npm-packages.html)
- [StepSecurity — Compromised `next` branch pushes malicious AsyncAPI generator, generator-helpers, and generator-components to npm](https://www.stepsecurity.io/blog/compromised-next-branch-pushes-malicious-asyncapi-generator-generator-helpers-and-generator-components-to-npm)
- [OX Security — AsyncAPI npm organization compromised, 2M+ weekly downloads affected](https://www.ox.security/blog/asyncapi-npm-organization-compromised-2m-weekly-downloads-affected/)
- [SafeDep — AsyncAPI generator supply chain attack: Miasma RAT](https://safedep.io/asyncapi-generator-supply-chain-attack-miasma-rat/)
