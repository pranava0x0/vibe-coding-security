---
id: 2026-03-claude-code-source-map-leak
title: "Claude Code source-map leak — 512K lines of internal TypeScript shipped in npm package (March 2026)"
date_disclosed: 2026-03-31
last_updated: 2026-05-18
severity: medium
status: contained
ecosystems: [claude-code, npm]
tools_affected: [claude-code]
tags: [information-disclosure, source-disclosure, npmignore, source-map, supply-chain-hygiene]
---

## TL;DR
On **2026-03-31**, Anthropic published a release of the `@anthropic-ai/claude-code` npm package that included a **59.8 MB source-map file** exposing ~**512,000 lines of unobfuscated TypeScript** across roughly 1,900 internal files. Root cause: a missing `*.map` entry in `.npmignore` (and no `files` allowlist in `package.json`) — Bun, which Anthropic uses for the build, generates source maps by default. No model weights, training data, or user information were exposed. The code was mirrored, ported to Python and Rust, and a clean-room rewrite hit 50K GitHub stars in two hours. Anthropic shipped a follow-up patch removing the map. **No security vulnerability for end users directly** — but the leaked internals seeded subsequent prompt-injection and tool-use research (see the [Claude Code CVE cluster](2025-08-claude-code-inverseprompt.md) that arrived in the following weeks).

## What happened
The Claude Code npm package is built with Bun (acquired by Anthropic in late 2025). Bun emits `.map` source maps by default, mapping the published bundle back to its original TypeScript. Nothing in the package metadata excluded these maps:

- No `*.map` entry in `.npmignore`.
- No `files` allowlist in `package.json` (the safer pattern — explicit allow over `.npmignore`'s implicit deny).

The 59.8 MB map shipped to the npm registry as part of a normal release. Within hours:
- The code was downloaded, decoded, and mirrored.
- It was rewritten in Python and Rust.
- A clean-room rewrite hit ~50K stars within ~2 hours — possibly the fastest-growing repo in GitHub history.
- Researchers extracted **44 hidden feature flags**, internal model codenames, the always-on background agent codenamed **KAIROS**, and a stealth mode designed to hide Anthropic employee contributions to open-source projects.

Anthropic confirmed within a day. They shipped a follow-up release of the npm package that excluded the source maps and added the missing `.npmignore` entries.

## Am I affected?
This was a **supply-chain hygiene incident**, not a vulnerability you could be "infected" by:

- No malicious code was inserted.
- No user data, no API keys, no model weights were leaked.
- No prompt injection or RCE primitive was added.

But there are second-order effects to be aware of:

1. **Anyone has the internal architecture now.** Subsequent prompt-injection research against Claude Code (the CVE-2026-21852 / -33068 / -35021 / -24887 cluster) benefited from the leak. If you run Claude Code, **keep it updated** — the disclosure window for new CVEs is shorter now.
2. **The "KAIROS background agent" pattern is in the wild.** Reverse engineers know about always-on agent components that previously weren't documented.
3. **Anyone who downloaded a vulnerable Claude Code version during the window has the leaked map locally** in their `~/.npm` cache. It's not dangerous, just present. You can clear it:
   ```bash
   npm cache clean --force
   # Or surgically:
   find ~/.npm -name '*.map' -path '*claude-code*' -delete
   ```

## If you are affected
1. Keep Claude Code updated. The CVE patch cadence accelerated post-leak.
2. There's no host-side compromise to remediate.

## Why this matters for vibe coders
This is a textbook example of a vibe-coding-class operational mistake hitting a vendor that should know better. The whole product is **vibe-coded** (per the layer5 / Kilo Blog timelines, the team uses Claude Code to build Claude Code). A missing `.npmignore` entry is exactly the kind of bug an AI agent will let through if no one is explicitly checking the published package contents.

**Two takeaways:**
1. Always check what your package actually publishes (`npm pack --dry-run`, then inspect the tarball) — agents won't reliably catch what shouldn't be shipped.
2. Use the `files` allowlist in `package.json` rather than relying on `.npmignore`'s deny-list semantics. Explicit allow > implicit deny.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ Add `"files": ["dist/", "README.md", "LICENSE"]` (or equivalent) to every published package's `package.json`.
→ Disable source map emission in production builds, or post-process to strip maps before publish.
→ Add `npm pack --dry-run | grep -E '\.map$|\.env|secret'` to CI as a pre-publish gate.

## Sources
- [VentureBeat — Claude Code's source code appears to have leaked: here's what we know](https://venturebeat.com/technology/claude-codes-source-code-appears-to-have-leaked-heres-what-we-know)
- [InfoQ — Anthropic Accidentally Exposes Claude Code Source via npm Source Map File](https://www.infoq.com/news/2026/04/claude-code-source-leak/)
- [Layer5 — The Claude Code Source Leak: 512,000 Lines, a Missing .npmignore](https://layer5.io/blog/engineering/the-claude-code-source-leak-512000-lines-a-missing-npmignore-and-the-fastest-growing-repo-in-github-history/)
- [Kilo Blog — Claude Code Source Leak: A Timeline](https://blog.kilo.ai/p/claude-code-source-leak-a-timeline)
- [DEV.to — Claude Code's Entire Source Code Just Leaked — 512,000 Lines Exposed](https://dev.to/evan-dong/claude-codes-entire-source-code-just-leaked-512000-lines-exposed-3139)
- [Tony Lixu (Medium) — The Claude Code Source Leak: How a Single Source Map File Exposed 510,000 Lines of Code](https://tonylixu.medium.com/the-claude-code-source-leak-how-a-single-source-map-file-exposed-510-000-lines-of-code-0ac25df26fd2)
- [claudefa.st — Claude Code Source Leak: Everything Found (2026)](https://claudefa.st/blog/guide/mechanics/claude-code-source-leak)
