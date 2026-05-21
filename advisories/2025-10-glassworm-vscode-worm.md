---
id: 2025-10-glassworm-vscode-worm
title: "GlassWorm — self-propagating VS Code / Open VSX extension worm (Oct 2025 → 2026)"
date_disclosed: 2025-10-17
last_updated: 2026-05-21
severity: high
status: active
ecosystems: [vscode, openvsx, npm, github]
tags: [supply-chain, ide-extension, worm, self-propagating, credential-theft, crypto-theft, invisible-unicode, solana-c2]
---

## TL;DR
**GlassWorm** (first flagged by Koi Security in **October 2025**) is the first **self-propagating worm** to spread through **VS Code / Open VSX extensions**. It hides its payload using **invisible Unicode characters** that don't render in any editor — code that is literally invisible to a human reviewer — and takes commands from a **triple-redundant C2** (a **Solana** blockchain memo as an un-takedownable dead-drop, plus a direct IP and Google Calendar). It steals npm/GitHub/Git credentials, drains **49 crypto-wallet extensions**, drops **SOCKS proxies** and **hidden VNC** servers, and republishes itself into more extensions to keep spreading. It has returned in **multiple waves through 2026** (Dec 2025; 24 extensions, then 72+ Open VSX extensions since Jan 31; a v2 wave in Mar–Apr 2026 hitting 150+ GitHub repos).

## What happened
GlassWorm's signature trick is **steganographic source**: the malicious logic is encoded in **printable-but-non-rendering Unicode** (e.g., variation selectors / invisible code points), so a maintainer or reviewer eyeballing the extension's source sees nothing. This defeats human review and most diff-based checks.

Capabilities across waves: steals **npm/GitHub/Git credentials** (reused to publish the worm into more packages → self-propagation), drains **49 crypto-wallet browser extensions**, deploys **SOCKS proxies** and **hidden VNC** for remote control, and logs keystrokes / dumps cookies+session tokens / takes screenshots. C2 is resilient: a **Solana blockchain memo** acts as a censorship-resistant dead-drop, backed by **direct IP** and **Google Calendar** fallbacks.

Timeline:
- **2025-10** — Koi Security discovers GlassWorm in 3 Open VSX / VS Code extensions (thousands of installs); npm packages using the same invisible-Unicode tactic trace back to ~March 2025.
- **2025-12** — returns with **24** malicious extensions impersonating popular dev tools.
- **2026-01-31 →** — **72+** additional malicious Open VSX extensions discovered.
- **2026-03 (v2)** — fresh wave; **GitHub** compromises ~Mar 3–9, **150+** repos; ~433 components estimated across Open VSX, VS Code Marketplace, GitHub, and npm.
- **2026-04** — **73** fake VS Code extensions delivering **GlassWorm v2**.

The campaign keeps recurring because takedowns can't reach the Solana dead-drop and the worm re-seeds itself with every set of stolen publish credentials — the same **IDE-extension trust surface** abused by the [Nx Console compromise](2026-05-nx-console-vscode-compromise.md) and the [TeamPCP GitHub breach](2026-05-teampcp-github-breach.md).

## Am I affected?
You're at risk if you install extensions from **Open VSX** (the default marketplace for VS Code forks like Cursor, Windsurf, VSCodium) or sideload niche VS Code extensions.

```bash
# Enumerate installed extensions across editors
code     --list-extensions --show-versions 2>/dev/null
cursor   --list-extensions --show-versions 2>/dev/null
codium   --list-extensions --show-versions 2>/dev/null

# Heuristic: scan extension sources for invisible/zero-width Unicode (a GlassWorm tell)
grep -RIlP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{2064}\x{FE00}-\x{FE0F}\x{E0000}-\x{E007F}]' \
  ~/.vscode/extensions ~/.cursor/extensions ~/.vscode-oss/extensions 2>/dev/null
```

If a flagged extension turns up, treat the machine as compromised: npm/GitHub/Git creds, browser sessions, and any crypto-wallet extensions are all in scope.

### IOCs / tells

| Type | Value |
|---|---|
| Obfuscation | Invisible/zero-width Unicode in extension source |
| C2 | Solana blockchain memo (dead-drop) + direct IP + Google Calendar |
| Targets | npm/GitHub/Git creds, 49 crypto-wallet extensions |
| Persistence | SOCKS proxy + hidden VNC servers |
| Marketplaces | Open VSX (primary), VS Code Marketplace; also GitHub + npm |
| First flagged | Koi Security, 2025-10 |

## If you are affected
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ Prefer verified-publisher, first-party extensions; disable silent auto-update on credential-holding editors; be especially wary of typosquatted "popular dev tool" clones on Open VSX, which is GlassWorm's primary vector.

## Sources
- [The Hacker News — Self-Spreading 'GlassWorm' Infects VS Code Extensions in Widespread Supply Chain Attack](https://thehackernews.com/2025/10/self-spreading-glassworm-infects-vs.html)
- [Veracode — GlassWorm: The First Self-Propagating VS Code Extension Worm](https://www.veracode.com/blog/glassworm-vs-code-extension/)
- [The Hacker News — GlassWorm Supply-Chain Attack Abuses 72 Open VSX Extensions to Target Developers](https://thehackernews.com/2026/03/glassworm-supply-chain-attack-abuses-72.html)
- [The Hacker News — Researchers Uncover 73 Fake VS Code Extensions Delivering GlassWorm v2 Malware](https://thehackernews.com/2026/04/researchers-uncover-73-fake-vs-code.html)
- [Aikido — GlassWorm Returns: Invisible Unicode Malware Found in 150+ GitHub Repositories](https://www.aikido.dev/blog/glassworm-returns-unicode-attack-github-npm-vscode)
- [Dark Reading — GlassWorm Returns, Slices Back into VS Code Extensions](https://www.darkreading.com/cyberattacks-data-breaches/glassworm-returns-vs-code-extensions)
- [Truesec — GlassWorm: Self-Propagating VSCode Extension Worm](https://www.truesec.com/hub/blog/glassworm-self-propagating-vscode-extension)
