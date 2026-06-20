---
id: 2025-06-vsxploit-openvsx-build-token-theft
title: "VSXPloit — Open VSX nightly build pipeline could be exploited to steal marketplace admin token (June 2025)"
date_disclosed: 2025-06-25
last_updated: 2026-06-20
severity: high
status: patched
ecosystems: [vscode, openvsx, cursor, windsurf]
tools_affected: [Open VSX Registry, Cursor, Windsurf, VSCodium, Google Cloud Shell Editor, Gitpod, StackBlitz, Coder]
tags: [supply-chain, ide-extension, openvsx, token-theft, build-pipeline, marketplace-takeover, historical]
---

## TL;DR

Koi Security researcher **Oren Yomtov** discovered that Open VSX's **nightly build pipeline** executed arbitrary code from community-submitted extension repositories, allowing any extension author to silently capture the **`@open-vsx` account's publish token** — the master key to the entire marketplace. An attacker with that token could push malicious updates to **all** installed extensions or publish new ones under any namespace, affecting **8M+ developers** using Cursor, Windsurf, VSCodium, Gitpod, and other VS Code forks. Patched **June 25, 2025** after responsible disclosure on **May 4, 2025**. No exploitation observed prior to disclosure.

## What happened

Open VSX (operated by the Eclipse Foundation) is the extension marketplace used by VS Code forks that cannot access Microsoft's proprietary VS Code Marketplace — including **Cursor, Windsurf, VSCodium, Google Cloud Shell Editor, Gitpod, StackBlitz, and Coder**.

Every night, Open VSX ran an automated process that:
1. Fetched the latest versions of community-submitted extensions from their source repositories.
2. Ran `npm install` on those repositories to build the extensions.
3. Published the resulting `.vsix` artifacts to the marketplace using a **high-privilege `@open-vsx` account token** stored as a secret in the build environment.

The critical flaw: step 2 ran `npm install` on **arbitrary, attacker-controlled code**. Any extension author could plant a malicious npm `postinstall` script (or a malicious transitive dependency) in their extension repository. When the nightly build process ran `npm install`, it would execute that code with access to the build environment's secrets — including the `@open-vsx` publish token.

**The impact of stealing the `@open-vsx` token:**
- **Push malicious updates** to any existing extension in the marketplace — updates that get silently auto-installed by all users with auto-update enabled (the default in Cursor, Windsurf, etc.).
- **Publish new extensions** under any namespace, including ones that match legitimate extension names.
- **Overwrite existing publishers' namespaces** — effective supply-chain takeover of the entire marketplace.

With the token, an attacker would have had **super-admin access** to every extension used by the 8M+ developers across all Open VSX-integrated tools.

**No CVE was assigned** (the flaw is in Open VSX's build infrastructure, not a packaged dependency). **No exploitation was observed** before or after disclosure — Oren Yomtov followed responsible disclosure, giving the Eclipse Foundation time to patch before publishing.

### Relationship to other Open VSX vulnerabilities

VSXPloit is distinct from two other Open VSX security issues tracked in this repo:

- **[Open Sesame](2026-05-whitecobra-vscode-extensions.md#open-sesame)** (Feb 2026, patched in Open VSX 0.32.0): a scanner boolean-ambiguity bug where `false` (scan failed/errored) was interpreted as "not malicious" — letting malicious extensions slip through pre-publish checks. VSXPloit targets the **build step** (pre-publish execution), Open Sesame targets the **scan step** (post-publish gate).
- **[AI IDEs recommend non-existent extensions](2026-01-vscode-fork-recommended-extension-hijack.md)** (Jan 2026): VS Code-fork IDEs point at unclaimed OpenVSX namespaces in their recommended-extensions config — a supply-chain gap from marketplace divergence, not from the build pipeline.

VSXPloit is the most severe of the three: a single compromised build run would have given an attacker the ability to **push to any extension**, not just claim an unclaimed namespace or slip through a scan gate.

## Am I affected?

The vulnerability was **patched on June 25, 2025** before any exploitation was observed. If you are running a recent version of Cursor, Windsurf, VSCodium, or any other Open VSX-integrated tool, your installed extensions came from the marketplace **after** the fix was deployed.

However, this advisory documents a **class of supply-chain risk** that remains relevant:

```bash
# Audit extensions installed in VS Code forks
cursor --list-extensions --show-versions 2>/dev/null
windsurf --list-extensions --show-versions 2>/dev/null
# Or in-app: Extensions sidebar → installed → inspect publisher, version, last updated

# Check that all installed extensions are from legitimate, known publishers
# Any extension from an unknown publisher updated around May–June 2025 should be scrutinized
```

The structural lesson: **Open VSX's build pipeline executing npm install against community-submitted code was the root cause**. Any equivalent build/CI system that fetches and runs code from external contributors without sandboxing carries the same risk.

## If you are affected

If you suspect an extension installed from Open VSX between **2025-05-04 and 2025-06-25** may have been compromised:

→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md) — audit installed extensions and verify publisher legitimacy.
→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) — if you believe an extension executed malicious code.

## Prevention

→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — treat IDE extension marketplaces as package registries with the same vetting rigor.
→ **For extension marketplace operators:** sandbox the build environment — never give a build step access to a publish token for the marketplace being built. Use OIDC tokens scoped to the specific extension being published, not a global admin token.
→ **For developers:** pin installed extensions to specific versions and audit changelog + publisher identity before updating. Enable automatic updates only for extensions from publishers you've verified.
→ **For Open VSX specifically:** the post-patch architecture requires explicit trust grants before an extension can be auto-published. The nightly build pipeline no longer has unscoped access to the marketplace publish token.

## Sources

- [The Hacker News — Critical Open VSX Registry Flaw Exposes Millions of Developers to Supply Chain Attacks](https://thehackernews.com/2025/06/critical-open-vsx-registry-flaw-exposes.html) — primary writeup, 8M+ developers figure, nightly build mechanism, disclosure timeline.
- [Security Affairs — Taking over millions of developers exploiting an Open VSX Registry flaw](https://securityaffairs.com/179398/hacking/taking-over-millions-of-developers-exploiting-an-open-vsx-registry-flaw.html) — Oren Yomtov / Koi Security attribution, `@open-vsx` super-admin token impact.
- [BleepingComputer — The zero-day that could've compromised every Cursor and Windsurf user](https://www.bleepingcomputer.com/news/security/the-zero-day-that-couldve-compromised-every-cursor-and-windsurf-user/) — Cursor/Windsurf framing, patch timeline, exploit-free disclosure confirmation.
- Cross-reference: [2026-05-whitecobra-vscode-extensions.md](2026-05-whitecobra-vscode-extensions.md) — WhiteCobra's repeated abuse of Open VSX after the VSXPloit patch.
- Cross-reference: [2026-01-vscode-fork-recommended-extension-hijack.md](2026-01-vscode-fork-recommended-extension-hijack.md) — separate Open VSX risk class (unclaimed-namespace hijack via IDE-hardcoded recommended-extension lists).
