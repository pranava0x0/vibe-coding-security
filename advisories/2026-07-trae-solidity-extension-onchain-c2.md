---
id: 2026-07-trae-solidity-extension-onchain-c2
title: "On-chain backdoor in a malicious TRAE IDE extension — Ethereum smart contract as dynamically updatable C2 (juannegro.solidity)"
date_disclosed: 2026-07-17
last_updated: 2026-07-20
severity: high
status: unconfirmed
ecosystems: [openvsx, trae, vscode-fork, solidity, ethereum]
tools_affected: [trae-ide, open-vsx, vscode-forks]
tags: [malicious-extension, open-vsx, ide-marketplace, blockchain-c2, ethereum, smart-contract, solidity, crypto-developer-targeting, rat, persistence]
---

## TL;DR
A malicious extension impersonating a Solidity language-support plugin (`juannegro.solidity`) was published to Open VSX on 2026-05-01 and pulled within hours — but **ByteDance's TRAE IDE marketplace kept serving it through at least 2026-07-18** because TRAE never synchronized Open VSX's takedown. The extension drops a cross-platform (Windows/macOS/Linux) backdoor whose command-and-control configuration lives **on an Ethereum smart contract**, letting the attacker redirect every infected host to a new C2 server by sending a blockchain transaction — no extension update, no new package, nothing for a registry to take down.

## What happened
X user **@Will42W** publicly flagged the extension on 2026-07-17; **SlowMist**'s MistEye threat-intelligence team confirmed and analyzed it, publishing a technical writeup the next day.

- **Extension:** `juannegro.solidity` v0.0.189 (VSIX SHA-256 `ff943371750ecd2ce6caa50c12d673e82743bdbc9569552eebfa98ccb2f4ac69`), impersonating Solidity language-support tooling to bait blockchain/smart-contract developers — a recurring target demographic for this style of campaign (Datadog's unrelated **MUT-9332** cluster targeted Solidity developers via different fake VS Code extensions in 2025; no confirmed link between the two actors beyond the shared victim profile).
- **Delivery:** published to Open VSX 2026-05-01, removed by Open VSX within hours the same day. **TRAE's own IDE marketplace did not propagate that removal** and continued distributing v0.0.189 as of the 2026-07-18 confirmation — over ten weeks after Open VSX pulled it.
- **Activation:** fires automatically on IDE startup via the `onStartupFinished` VS Code extension-activation event — no user action beyond having the extension installed.
- **Payload:** a cross-platform dropper (hash-obfuscated `child_process.exec` calls) that establishes OS-specific persistence — `~/Library/LaunchAgents/` on macOS, a systemd user service on Linux, Windows Registry Run keys plus attempted Windows Defender exclusions — then opens a remote shell and fetches second-stage payloads.
- **The novel part — on-chain C2:** the dropper reads its C2 configuration from a deployed Ethereum smart contract (`0xf8a900db50b3331be6b768ba460bb59f3e40c344`, owner wallet `0xFd3fc58bcbd8ccc77b6000201438eDfc636E7cA7`) via two contract functions — `param1()` returns the current remote-shell address for macOS/Linux, `param2()` returns the current Windows payload-download URL. Infected hosts query **public Ethereum RPC endpoints** to read these values, so the attacker updates every infected host's C2 destination by sending a normal on-chain transaction, with no need to touch the extension package again. On-chain transactions confirm the attacker exercised this: the contract was deployed 2026-03-14, and C2 parameters were updated 2026-05-03 and again 2026-05-16 — weeks after the initial publish, while the extension sat live and undetected.

This generalizes the Solana-memo and Solana-mainnet-JSON-RPC dead-drop C2 techniques this repo already tracks (GlassWorm, GlassWASM) to a **different chain (Ethereum) and a different mechanism (a queryable smart-contract getter rather than a transaction-memo field)** — and, unlike a registry takedown, removing the malicious extension from one marketplace does nothing to the C2 channel or to hosts already infected via a marketplace (TRAE) that didn't sync the removal.

## Am I affected?

```bash
# Check for the malicious extension across VS Code-family editors and TRAE
find ~/.vscode* ~/.trae* ~/.cursor* ~/.windsurf* -iname "*juannegro*solidity*" 2>/dev/null

# Verify VSIX hash if you find a matching extension directory
shasum -a 256 <path-to-extension>/*.vsix 2>/dev/null
# Compare against: ff943371750ecd2ce6caa50c12d673e82743bdbc9569552eebfa98ccb2f4ac69

# Persistence check (macOS)
ls -la ~/Library/LaunchAgents/ 2>/dev/null

# Persistence check (Linux)
systemctl --user list-unit-files 2>/dev/null | grep -iv '^UNIT'

# Persistence check (Windows, run in PowerShell)
Get-ItemProperty HKCU:\Software\Microsoft\Windows\CurrentVersion\Run

# Network IOCs to check against firewall/proxy logs
# 107.189.27.46:4912, 107.189.27.46:3000, 91.108.240.156:4912, 107.189.16.215:4912
```

**If you use TRAE IDE and have Solidity tooling installed**, check specifically — this is the only confirmed still-live distribution channel as of this sweep. Open VSX itself already removed the package.

### IOCs

| Type | Value |
|---|---|
| Malicious extension | `juannegro.solidity` v0.0.189 |
| VSIX SHA-256 | `ff943371750ecd2ce6caa50c12d673e82743bdbc9569552eebfa98ccb2f4ac69` |
| Ethereum C2 contract | `0xf8a900db50b3331be6b768ba460bb59f3e40c344` |
| Contract owner wallet | `0xFd3fc58bcbd8ccc77b6000201438eDfc636E7cA7` |
| C2 IPs | `107.189.27.46:4912`, `107.189.27.46:3000`, `91.108.240.156:4912`, `107.189.16.215:4912` |
| macOS binary hash | `80d2672e2599732d3c0ae2a4cd0d1e3fe4d555a60273ce33feb99db3f34d250f` |
| Linux amd64 binary hash | `9b73e7cd4e1425e770392549d8df46c706139ef476f4f7b9ac405165dc8d9696` |

## If you are affected
→ [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) — same "untrusted code ran with your privileges" blast-radius logic applies to a malicious extension.
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — treat any host that ran this extension as fully compromised (arbitrary shell access) and rotate everything reachable from it, including crypto wallet keys given the Solidity-developer targeting.
1. Uninstall the extension and kill any established remote-shell session.
2. Remove the OS-specific persistence artifacts listed above.
3. Because C2 is a live smart contract the attacker can still update, don't assume "the extension is gone" means the threat is inert — check for outbound connections to the C2 IPs above and to any new addresses the contract's `param1()`/`param2()` might now return.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — treat any IDE extension marketplace, including ones bundled into a VS Code fork, as an untrusted package source.
- **If your IDE is a VS Code fork with its own bundled extension marketplace (TRAE, Cursor, Windsurf, and others), don't assume a takedown on Open VSX propagates to it.** Confirm with the fork vendor whether removals sync automatically; this incident shows at least one major fork does not.
- Blockchain-based C2 (Solana memos, Ethereum contract storage) cannot be taken down by a registry, domain seizure, or IP block — the only durable defense is not running the malicious code in the first place. Vet extension publishers and be suspicious of niche-language tooling (Solidity, Rust, etc.) from unfamiliar or newly created publisher accounts.

## Sources
- [SlowMist — Threat Intelligence: On-Chain Backdoor in a Malicious TRAE Extension](https://slowmist.medium.com/threat-intelligence-on-chain-backdoor-in-a-malicious-trae-extension-0d913cbf1f56) — primary technical analysis, IOCs, timeline, confirms TRAE's continued distribution as of 2026-07-18.

**Sourcing note:** this incident is corroborated only by SlowMist's own writeup as of this sweep (the original report came from X user @Will42W, whose post SlowMist's analysis references but which was not independently fetched here). No independent security-research or aggregator coverage of this specific `juannegro.solidity`/TRAE incident was found — distinct from the unrelated, earlier **MUT-9332** Solidity-developer-targeting campaign (Datadog Security Labs, 2025) which used different extensions and a different actor. Marked `unconfirmed` per this repo's two-independent-source standard for full advisories.
