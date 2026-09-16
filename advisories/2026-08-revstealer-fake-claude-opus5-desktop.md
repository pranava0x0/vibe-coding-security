---
id: 2026-08-revstealer-fake-claude-opus5-desktop
title: "RevStealer — a fake 'Claude Opus 5 Free Desktop' GitHub repo delivers a Windows infostealer that streams credentials, wallets and dev secrets, then deletes itself (Aug 2026)"
date_disclosed: 2026-08-31
last_updated: 2026-09-16
severity: high
status: active
ecosystems: [windows, github, ai-desktop-tool]
tools_affected: [developers-seeking-a-claude-desktop-app, windows-workstations-with-ai-and-crypto]
tags: [infostealer, credential-theft, fake-ai-tool, github-lure, electron, crypto-wallet, blockchain-c2, impersonation]
---

## TL;DR
**RevStealer** is a Windows infostealer distributed through a **GitHub repository impersonating Anthropic** — `claude5opus/Claude-Opus-5-Free-Desktop`, offering a `ClaudeOpus5-desktop.zip` (~101 MB) that claims to be a free desktop build of "Claude Opus 5" (a model that does not exist as a free desktop app). Running it launches an **invisible Electron loader** that decrypts and runs a native stealer targeting browser data, **50+ crypto wallets**, 12+ password managers, VPN/remote-access creds, and developer files, **streams the loot to a C2 in memory** (no on-disk archive), then **self-deletes with no persistence**. It was flagged by **1 of 66 antivirus engines** on first scan and keeps a **Polygon smart-contract C2 fallback**. Morphisec ([2026-08-31](https://www.morphisec.com/blog/revstealer-silence-is-its-greatest-weapon/)) and Help Net / SC Media (2026-09-01) covered it. **Do not install "free desktop" AI apps from GitHub release ZIPs**; the official Claude apps come from Anthropic's own domains.

## What happened
The lure trades on the demand for a local Claude desktop client. The fake repo ships screenshots and model-comparison charts alongside the download to look legitimate; the executable inside opens **no window**. The chain, per [Morphisec Threat Labs](https://www.morphisec.com/blog/revstealer-silence-is-its-greatest-weapon/) (Shmuel Uzan):

1. **Electron loader** runs environment checks first — minimum RAM/CPU, hostname/username blocklist, graphics-adapter and debugger-timing checks — and tries to add the user's `AppData` to **Microsoft Defender's exclusion list** before proceeding.
2. It decrypts an embedded **AES-256-CBC** native payload, which runs weighted anti-VM scoring, terminates on Russian/Ukrainian/Central-Asian locale settings, and gates behind a CAPTCHA to defeat sandboxes.
3. The stealer collects **browser databases and encryption keys, extension storage, Windows Credential Manager, 12+ password managers, 50+ cryptocurrency wallets, VPN and remote-access credentials, messaging apps, game launchers, OBS profiles, clipboard, screenshots, and selected documents**.
4. Loot is **streamed to the C2 as it is collected**, with no staged archive on disk; a **Polygon (MATIC) blockchain smart contract** holds a fallback C2 address so operators can rotate infrastructure without rebuilding the malware. After exfiltration it **self-deletes** — no scheduled task, Run key, or startup entry.

The evasion is the point: Morphisec frames it as built for silence, and it was seen by **only 1 of 66 AV engines** initially ([Help Net Security](https://www.helpnetsecurity.com/2026/09/01/revstealer-malware-claude-opus-5-github/)). RevStealer is also distributed via game-cheat sites, but the **fake-Claude GitHub repo is the developer-facing vector** and the reason it belongs here: it is the same "impersonate a wanted AI tool" play as the malicious IDE-extension and skill-marketplace waves this repo already tracks, aimed at exactly the people who want an AI coding/desktop tool.

## Am I affected?

You are at risk if anyone on a Windows machine downloaded and ran a "Claude Opus 5" desktop build from a GitHub repo or a cheat site. There is no official free "Claude Opus 5 Desktop" ZIP on GitHub — the official Claude desktop and mobile apps come from Anthropic's own properties.

```powershell
# Did a fake-Claude archive land or run?
Get-ChildItem -Recurse $env:USERPROFILE\Downloads -Filter "ClaudeOpus5*.zip" -ErrorAction SilentlyContinue
Get-MpPreference | Select-Object -ExpandProperty ExclusionPath   # look for an AppData path you did not add

# Electron app that opens no window, launched from an unusual AppData/Temp path,
# is the tell; RevStealer self-deletes, so absence of the binary is not absence of infection.
```

Because it **streams and self-deletes**, treat *having run it once* as full compromise of everything on that machine.

### IOCs

| Type | Value |
|---|---|
| Malware | RevStealer (aka REF2859) — Windows infostealer |
| Developer lure | GitHub repo `claude5opus/Claude-Opus-5-Free-Desktop`; download `ClaudeOpus5-desktop.zip` (~101 MB), 64-bit Electron |
| Behaviour | AES-256-CBC-decrypted native payload; anti-VM/CAPTCHA gating; Defender AppData exclusion attempt; in-memory streaming exfil; self-delete, no persistence |
| C2 resilience | **Polygon blockchain smart contract** holds fallback C2 address |
| Detection at disclosure | **1 / 66** AV engines |
| Targets | browsers, 12+ password managers, 50+ crypto wallets, VPN/remote-access creds, messaging, dev files, clipboard, screenshots |

## If you are affected
1. **Isolate the machine** and treat every credential entered or stored on it as compromised — browser-saved passwords, password-manager vaults, crypto wallets/seed phrases, VPN and cloud/dev credentials.
2. Rotate from a **known-clean device**: cloud and AI-provider keys ([playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)), GitHub PATs ([playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)), and move any crypto to a fresh wallet.
3. If the machine ran a local AI agent with live credentials: [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — a GitHub star count and a screenshot are not provenance; install AI desktop apps only from the vendor's own domain, never a release ZIP that impersonates them.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — an infostealer's whole yield is what a workstation holds in plaintext; keep long-lived keys and wallet seeds off developer laptops.

## Sources
- [Morphisec — RevStealer: Silence Is Its Greatest Weapon](https://www.morphisec.com/blog/revstealer-silence-is-its-greatest-weapon/) — fetched 2026-09-16; primary technical analysis (Shmuel Uzan, published 2026-08-31): the fake `Claude-Opus-5-Free-Desktop` GitHub repo and `ClaudeOpus5-desktop.zip`, the Electron loader chain, AES-256-CBC payload, target list, in-memory streaming exfil, self-delete, and Polygon smart-contract C2 fallback.
- [Help Net Security — Fake Claude Opus 5 app delivers malware and wipes its own tracks](https://www.helpnetsecurity.com/2026/09/01/revstealer-malware-claude-opus-5-github/) — fetched 2026-09-16; independent coverage, published 2026-09-01: 1/66 AV detection, 50+ wallet target count.
- [SC Media — RevStealer malware spread through fake Claude Opus 5 download](https://www.scworld.com/news/revstealer-malware-spread-through-fake-claude-opus-5-download) — fetched 2026-09-16; independent coverage of the GitHub distribution vector.
