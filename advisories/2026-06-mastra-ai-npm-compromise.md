---
id: 2026-06-mastra-ai-npm-compromise
title: "Mastra AI npm namespace compromise — 144 @mastra/* packages carry easy-day-js typosquat RAT via hijacked contributor account (June 2026)"
date_disclosed: 2026-06-17
last_updated: 2026-06-17
severity: critical
status: active
ecosystems: [npm]
tools_affected: [mastra, "@mastra/*", easy-day-js]
tags: [supply-chain, credential-theft, typosquat, postinstall, ai-agents, crypto-stealer, miasma-lineage, dependency-injection]
---

## TL;DR
A hijacked npm contributor account was used to inject **`easy-day-js`** — a typosquat of the popular `dayjs` date library — as a dependency across **144 packages** in the `@mastra/*` namespace (Mastra AI agent framework). The malicious `easy-day-js` version ran an obfuscated `postinstall` hook that downloaded and executed a cryptocurrency-stealing RAT, then self-deleted to remove evidence. Combined weekly downloads across affected packages exceed **1.1 million**. Attribution: Shai-Hulud/Miasma lineage payload characteristics.

## What happened

**Mastra** is an open-source TypeScript AI agent framework (`@mastra/*` npm namespace) widely used to build AI-powered workflows, agents, tool integrations, and LLM orchestration pipelines. On **2026-06-17**, attackers used a hijacked Mastra contributor's npm access token to publish a malicious dependency across **144 packages** in the `@mastra/*` scope.

The attack technique — **dependency injection via a typosquat** — is more subtle than directly modifying the primary package:

1. The attacker added `easy-day-js` as a `dependencies` entry (not `devDependencies`) in the `package.json` of 144 `@mastra/*` packages.
2. `easy-day-js` is a typosquat of the legitimate `dayjs` date-utility library (60M+ weekly downloads). The `@mastra/*` packages are legitimate — their own code is unmodified — but anyone who installed them pulled in the malicious `easy-day-js` as a transitive dependency.
3. The malicious `easy-day-js` version's `postinstall` hook ran an obfuscated dropper that fetched and executed a **cryptocurrency-stealing RAT**, then self-deleted the dropper.

**Why this evades common defenses:**
- `npm audit` focuses on known CVEs in direct/transitive dependencies, not supply-chain-injected typosquats that haven't yet received a CVE.
- The primary `@mastra/*` package code itself is clean — only the dependency tree is poisoned.
- `--ignore-scripts` would block `postinstall`, but many CI systems and developer workflows do not set this flag.

**Why this matters for vibe coders:** Mastra is a primary AI-agent orchestration framework. Any Mastra-powered project running `npm install` during the exposure window installed the RAT with full developer-machine privileges. The RAT specifically targets AI-tool credentials (Anthropic/OpenAI API keys, MCP config files) alongside cloud credentials, SSH keys, and crypto wallets.

This is the sixth documented copycat wave in the Shai-Hulud/Miasma lineage (Shai-Hulud → Second Coming → Third Coming → Phantom Gyp → Hades → Mastra injection), and the first to use a **dependency-injection** (adding a typosquat as a dep, rather than compromising the primary package directly) as its install-time vector at this scale.

## Am I affected?

```bash
# Check if any @mastra/* packages are installed
npm ls --depth=0 2>/dev/null | grep "@mastra/"

# Check if easy-day-js is in your dependency tree
npm ls 2>/dev/null | grep "easy-day-js"

# Check package-lock.json for the typosquat
grep "easy-day-js" package-lock.json 2>/dev/null

# Check npm cache
ls ~/.npm/easy-day-js/ 2>/dev/null

# Check for any crypto-stealer persistence artifacts (common RAT IOCs)
# Look for unexpected cron/launchd/systemd entries added 2026-06-17
```

If you installed any `@mastra/*` package on **2026-06-17** (or if `easy-day-js` appears in your `package-lock.json`), treat the machine as compromised and rotate all credentials.

### IOCs

| Type | Value |
|---|---|
| Namespace | `@mastra/*` (144 packages) |
| Malicious dependency | `easy-day-js` (typosquat of `dayjs`) |
| Attack vector | `postinstall` hook in injected `easy-day-js` |
| Payload | Obfuscated two-stage dropper → crypto-stealing RAT (self-deletes) |
| Initial access | Hijacked npm contributor account |
| Attribution | Shai-Hulud/Miasma lineage (payload family) |
| Combined affected downloads | 1.1M+ weekly |

## If you are affected

1. **Assume full credential compromise.** The RAT targets:
   - LLM API keys (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GEMINI_API_KEY`, etc.)
   - AI-tool config files (`~/.claude/settings.json`, `~/.cursor/mcp.json`, MCP OAuth tokens)
   - Cloud credentials (AWS `~/.aws/credentials`, GCP service account keys, Azure credentials)
   - npm tokens (`~/.npmrc`), GitHub tokens, SSH keys (`~/.ssh/`)
   - Crypto wallet files (Exodus, MetaMask seed phrases)
2. **Immediately rotate** all credentials on any affected machine, in priority order: LLM API keys → cloud IAM credentials → npm/GitHub tokens → SSH keys.
3. **Remove from your lockfile:** grep `package-lock.json` or `yarn.lock` for `easy-day-js` and re-run `npm install` against patched `@mastra/*` versions.
4. **Run `npm audit`** after removing `easy-day-js` and upgrading `@mastra/*` packages.
5. **Check for persistence:** look for new cron entries, LaunchAgent plists, or systemd units created on 2026-06-17 — the RAT may have installed a persistence mechanism before self-deleting.
6. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) for the full credential-rotation and forensics procedure.

## Prevention

- **`npm install --ignore-scripts`** for all CI/CD and deployment installs. Note: `--ignore-scripts` does **not** block `binding.gyp` native-addon builds — see [Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md).
- **Add `allow-scripts=false` to `.npmrc`** to suppress lifecycle scripts globally; allow-list only specific trusted native addons. Available today in npm 11.16.0; default in npm v12 (expected July 2026).
- **Monitor the full dependency tree, not just direct deps.** Tools like [Socket.dev](https://socket.dev), Snyk, and Aikido can alert on newly-added transitive dependencies that are typosquats or have no prior publish history.
- **Pin `@mastra/*` to a known-good lockfile** (`package-lock.json` / `yarn.lock`) and review diffs on every `npm install` run in CI.
- **Scrutinize dependency additions.** A newly-added `easy-day-js` in a well-known framework's `package.json` is the IOC — require human review of any `package.json` change from a dependency update PR.
- → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## Sources

- [The Hacker News — 144 Mastra npm Packages Compromised via Hijacked Contributor Account](https://thehackernews.com/2026/06/mastra-npm-packages-compromised-hijacked.html) — primary disclosure; contributor-token compromise, 144 packages, easy-day-js typosquat, crypto-stealing RAT.
- [GitHub Advisory Database — GHSA advisory for @mastra/* easy-day-js dependency injection](https://github.com/advisories?query=mastra+easy-day-js) — official GHSA records.
- Cross-link: [IronWorm](2026-06-ironworm-npm-rust-ebpf.md), [Hades Campaign](2026-06-hades-campaign-pypi-mcp-attack.md), [Solana FakeFix](2026-06-solana-fakefix-campaign.md) — same Miasma-lineage payload family; [Phantom Gyp](2026-06-phantom-gyp-miasma-wave4.md) — prior wave using binding.gyp; [Shai-Hulud copycat wave](2026-05-shai-hulud-copycat-wave.md) — prior copycat cadence.
