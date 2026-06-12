---
id: 2025-10-glassworm-vscode-worm
title: "GlassWorm — self-propagating VS Code / Open VSX extension worm (Oct 2025 → 2026)"
date_disclosed: 2025-10-17
last_updated: 2026-06-12
severity: high
status: active
ecosystems: [vscode, openvsx, npm, github]
tags: [supply-chain, ide-extension, worm, self-propagating, credential-theft, crypto-theft, invisible-unicode, solana-c2, botnet-takedown]
---

## TL;DR
**GlassWorm** (first flagged by Koi Security in **October 2025**) is the first **self-propagating worm** to spread through **VS Code / Open VSX extensions**. It hides its payload using **invisible Unicode characters** that don't render in any editor — code that is literally invisible to a human reviewer — and takes commands from a **quad-redundant C2** (a **Solana** blockchain memo as an un-takedownable dead-drop, plus **BitTorrent DHT**, Google Calendar dead-drops, and direct VPS IPs). It steals npm/GitHub/Git credentials, drains **49 crypto-wallet extensions**, drops **SOCKS proxies** and **hidden VNC** servers, and republishes itself into more extensions to keep spreading. It has returned in **multiple waves through 2026** (Dec 2025; 24 extensions, then 72+ Open VSX extensions since Jan 31; a v2 wave in Mar–Apr 2026 hitting 150+ GitHub repos).

> **Update 2026-05-31 — disrupted.** On **2026-05-26 14:00 UTC**, **CrowdStrike Counter Adversary Operations + Google + the Shadowserver Foundation** executed a coordinated takedown, **simultaneously disabling all four C2 channels** (Solana blockchain memos, BitTorrent DHT, Google Calendar dead-drops, direct VPS IPs). The takedown stopped new payload delivery but did not uninstall the malware, rotate stolen credentials, or undo downstream credential resale.
>
> **Update 2026-06-12 — back: new Mac wave with reconstituted fresh infrastructure.** Koi Security and BleepingComputer report a **new GlassWorm wave targeting macOS exclusively** with **fresh C2 infrastructure** — the first wave to survive the May 26 takedown and reconstitute. The operator rebuilt on new infrastructure, pivoted from Windows-only to macOS-first, and added a **hardware-wallet trojanization capability** (Ledger Live and Trezor Suite replaced with backdoored versions). Status reverted to **`active`**. Defensive cue: eBPF/EDR tools that detected the Windows variant may not detect the macOS AppleScript/LaunchAgent-based variant — check koi.ai IOC list for the macOS wave specifically.

## What happened
GlassWorm's signature trick is **steganographic source**: the malicious logic is encoded in **printable-but-non-rendering Unicode** (e.g., variation selectors / invisible code points), so a maintainer or reviewer eyeballing the extension's source sees nothing. This defeats human review and most diff-based checks.

Capabilities across waves: steals **npm/GitHub/Git credentials** (reused to publish the worm into more packages → self-propagation), drains **49 crypto-wallet browser extensions**, deploys **SOCKS proxies** and **hidden VNC** for remote control, and logs keystrokes / dumps cookies+session tokens / takes screenshots. C2 is resilient: a **Solana blockchain memo** acts as a censorship-resistant dead-drop, backed by **direct IP** and **Google Calendar** fallbacks.

Timeline:
- **2025-10** — Koi Security discovers GlassWorm in 3 Open VSX / VS Code extensions (thousands of installs); npm packages using the same invisible-Unicode tactic trace back to ~March 2025.
- **2025-12** — returns with **24** malicious extensions impersonating popular dev tools.
- **2026-01-31 →** — **72+** additional malicious Open VSX extensions discovered.
- **2026-03 (v2)** — fresh wave; **GitHub** compromises ~Mar 3–9, **150+** repos; ~433 components estimated across Open VSX, VS Code Marketplace, GitHub, and npm.
- **2026-04** — **73** fake VS Code extensions delivering **GlassWorm v2**.
- **2026-05-26 14:00 UTC** — **CrowdStrike + Google + Shadowserver coordinated takedown** disables all four C2 channels simultaneously; attribution narrows to a **likely Russia-based operator** (malware exits on CIS-country locale checks; Russian-language source comments). The takedown caps a campaign that had poisoned **300+ GitHub repos** via stolen credentials alone.
- **2026-06 (post-takedown)** — **New macOS-targeting wave with fresh infrastructure** (Koi Security / BleepingComputer). Operator reconstituted on new C2. Targeting macOS exclusively for the first time. New payload: AES-256-CBC encryption, **AppleScript** persistence (vs. PowerShell), **LaunchAgent** persistence (vs. Registry), and a **hardware-wallet trojanization module** targeting **Ledger Live** and **Trezor Suite** app bundles. Also sweeps 50+ browser crypto extensions, GitHub/npm tokens, Safari/Chrome browser data, and macOS Keychain. Hardware-wallet trojans appear incomplete at time of disclosure ("returning empty files") — attacker likely still finalizing macOS wallet payloads. Status reverted to `active`.

The campaign kept recurring because takedowns couldn't reach the Solana dead-drop and the worm re-seeded itself with every set of stolen publish credentials — the same **IDE-extension trust surface** abused by the [Nx Console compromise](2026-05-nx-console-vscode-compromise.md) and the [TeamPCP GitHub breach](2026-05-teampcp-github-breach.md). The 2026-05-26 takedown finally hit all four redundancy channels at once, which is *why* it worked — a less coordinated strike would have let the Solana dead-drop carry survivors. The downstream lesson: **infostealer-harvested credentials don't expire when the C2 dies** — [Megalodon's 5,561-repo wave](2026-05-megalodon-github-actions-mass-campaign.md) (May 18) is what credential resale of this corpus looks like.

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
| C2 (all four disrupted 2026-05-26) | (1) Solana blockchain memo (dead-drop), (2) **BitTorrent DHT** (configuration data), (3) Google Calendar event titles, (4) direct VPS IPs |
| Targets | npm/GitHub/Git creds, 49 crypto-wallet extensions |
| Persistence | SOCKS proxy + hidden VNC servers |
| Marketplaces | Open VSX (primary), VS Code Marketplace; also GitHub + npm |
| First flagged | Koi Security, 2025-10 |
| Attribution | Likely Russia-based (CIS-locale exit checks, Russian-language source comments) |
| Takedown | **CrowdStrike Counter Adversary Operations + Google + Shadowserver Foundation**, 2026-05-26 14:00 UTC, all 4 C2 channels simultaneously |

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
- [CrowdStrike — Inside CrowdStrike's Takedown of a Developer-Targeting Botnet (2026-05-27)](https://www.crowdstrike.com/en-us/blog/inside-crowdstrike-takedown-of-a-developer-targeting-botnet/) — canonical takedown writeup
- [The Register — CrowdStrike, Google shatter Glassworm botnet (2026-05-27)](https://www.theregister.com/cyber-crime/2026/05/27/crowdstrike-google-shatter-glassworm-botnet/5247337)
- [BleepingComputer — New GlassWorm malware wave targets Macs with trojanized crypto wallets](https://www.bleepingcomputer.com/news/security/new-glassworm-malware-wave-targets-macs-with-trojanized-crypto-wallets/) — post-takedown macOS wave, hardware wallet trojanization.
- [Koi Security — GlassWorm Goes Mac: Fresh Infrastructure, New Tricks](https://www.koi.ai/blog/glassworm-goes-mac-fresh-infrastructure-new-tricks) — technical detail, AES-256-CBC payload, AppleScript/LaunchAgent persistence, IOCs.
- [TechCrunch — CrowdStrike and Google take down botnet used by hackers to target open source software developers](https://techcrunch.com/2026/05/27/crowdstrike-and-google-take-down-botnet-used-by-hackers-to-target-software-developers-in-supply-chain-attacks/)
- [Cybersecurity Dive — Coordinated operation takes down Glassworm botnet](https://www.cybersecuritydive.com/news/takedown-glassworm-botnet-crowdstrike-Google-Shadowserver/821227/)
- [CyberScoop — CrowdStrike disrupts Glassworm botnet that preyed on open-source supply chain](https://cyberscoop.com/crowdstrike-glassworm-botnet-takedown/)
- [Infosecurity Magazine — CrowdStrike, Google Take Down Glassworm Botnet](https://www.infosecurity-magazine.com/news/crowdstrike-google-takedown/)
- [Socket — GlassWorm Sleeper Extensions Activate on Open VSX](https://socket.dev/blog/glassworm-sleeper-extensions-activated-on-open-vsx) — late-April 2026 73-extension "sleeper" wave (clones of legit extensions, malicious only after update)
