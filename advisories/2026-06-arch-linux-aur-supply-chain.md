---
id: 2026-06-arch-linux-aur-supply-chain
title: "Atomic Arch — AUR supply-chain attack: 1,500+ community packages hijacked via orphaned-package takeover; eBPF rootkit for persistence (June 2026)"
date_disclosed: 2026-06-11
last_updated: 2026-06-19
severity: high
status: active
ecosystems: [aur, npm]
tools_affected: [arch-linux, AUR, yay, paru, pamac]
tags: [supply-chain, linux, malware-delivery, developer-workstation, new-ecosystem, ebpf-rootkit, orphaned-package-takeover]
---

## TL;DR
The campaign now called **"Atomic Arch"** hijacked **1,500+ packages** in the **Arch Linux AUR (Arch User Repository)** — up from the initially-reported 400+, as researchers expanded their scope. Attackers used **orphaned-package takeover** as the primary initial-access method: AUR packages whose maintainer has gone inactive can be adopted by any registered user, providing a pre-existing trusted package identity with existing user base. The payload includes an **eBPF kernel rootkit** for persistence that is invisible to eBPF-based EDR tools, and cross-ecosystem IOCs (`atomic-lockfile` + `js-digest` rogue npm packages) suggest the same actor operates in multiple ecosystems. **Arch Linux suspended new AUR account registrations on 2026-06-15** to slow the attacker's ability to acquire new package identities. AUR packages execute arbitrary shell code during installation with no vetting by Arch Linux maintainers — making them a high-privilege, low-oversight attack surface on developer workstations that host AI coding tools, cloud credentials, and SSH keys.

## What happened

The **Arch Linux AUR** is a community-maintained repository of 80,000+ package build scripts (`PKGBUILD` files). Unlike official Arch Linux packages (`[core]`, `[extra]`, `[community]` repos) which receive security review, AUR packages are submitted by any registered user and published without pre-vetting. AUR helpers (`yay`, `paru`, `pamac`) automate the download, build, and install of AUR packages.

Around **2026-06-11**, the campaign researchers now call **"Atomic Arch"** began, eventually reaching **1,500+ AUR packages** across multiple categories (developer tooling, system utilities, media). Key characteristics:

- **Scale:** 1,500+ packages (initial reports said 400+; scope expanded as analysis continued)
- **Initial access:** **Orphaned-package takeover** — AUR packages whose original maintainers went inactive can be "adopted" by any registered user. Attackers created or used existing accounts to adopt orphaned packages, giving them the package identity and existing user base without needing to compromise an account.
- **Delivery primitive:** Malicious `PKGBUILD` scripts run arbitrary shell code during the `build()`, `package()`, or `post_install()` stages with the installing user's full privileges — functionally equivalent to `curl | bash` with sudo for some packages
- **Persistence mechanism:** The payload deploys an **eBPF kernel rootkit** that hides malicious processes and network connections from standard monitoring tools — including eBPF-based EDR products (the rootkit operates at the same layer EDR tools use for visibility). This is the same persistence class as [IronWorm](2026-06-ironworm-npm-rust-ebpf.md) (June 2026 npm worm).
- **Cross-ecosystem IOCs:** Two rogue npm packages — `atomic-lockfile` and `js-digest` — were registered by the same actor and used to deliver the second-stage payload to victim machines, suggesting the Atomic Arch operator also targets the npm ecosystem.
- **Arch Linux response:** On **2026-06-15**, Arch Linux **suspended new AUR account registrations** to limit the attacker's ability to adopt additional orphaned packages. Existing accounts are under review.
- **Target profile:** Linux developer workstations — specifically Arch Linux and derivatives (Manjaro, EndeavourOS, Garuda, Parabola) that host AI development environments

**Why AUR matters for vibe coders specifically:** Many AI/ML developers use Arch Linux precisely because AUR provides cutting-edge versions of development tools. AI coding tool packages frequently appear on AUR first: unofficial `claude-code`, `cursor`, Windsurf, `aider`, `opencode`, MCP server wrappers, and AI SDK packages. Any developer who installed such a package during the exposure window ran attacker-controlled shell code on the same machine that holds their LLM API keys, cloud IAM credentials, SSH keys, and AI-tool config files.

**New ecosystem in scope:** The AUR represents a new package registry ecosystem now tracked by this advisory feed. Unlike npm, PyPI, and Crates.io, AUR has **no central security team**, **no automated malware scanning**, and **no cryptographic provenance** on PKGBUILD files — the community relies entirely on user reviews and the [AUR Trusted User](https://wiki.archlinux.org/title/AUR_Trusted_Users) system, which only covers official repo packages.

## Am I affected?

You may be affected if:
1. You run Arch Linux, Manjaro, EndeavourOS, Garuda, or another Arch-based derivative.
2. You install packages using AUR helpers (`yay`, `paru`, `pamac`, `trizen`, `aura`).
3. You installed AUR packages between **approximately 2026-05-01 and 2026-06-17** without manually reviewing the PKGBUILD.

```bash
# List all AUR-installed packages (those not from official repos)
pacman -Qm

# Review recent package installs from pacman log
grep -E "(upgraded|installed)" /var/log/pacman.log | tail -200

# Look for suspicious post-install activity (outbound connections, new cron entries)
crontab -l 2>/dev/null
ls -la /etc/cron.d/ /etc/cron.daily/ 2>/dev/null

# Check for new systemd user units that shouldn't be there
systemctl --user list-unit-files | grep enabled

# Check for new LaunchAgent-like entries (for cross-env checks)
ls -la ~/.config/systemd/user/ 2>/dev/null
```

Until the full package list is published, treat any AUR package installed in the June 2026 window as a potential vector — especially packages related to AI development tooling, developer utilities, or recently-created AUR packages with few votes/comments.

## If you are affected

1. **Rotate all credentials** on the affected machine: LLM API keys, cloud IAM (AWS, GCP, Azure), GitHub tokens, npm tokens, SSH keys, and any AI-tool OAuth tokens (MCP config files).
2. **Audit recently-installed AUR packages** — review each `PKGBUILD` for unexpected network calls, base64/eval patterns, or unusual `post_install` hooks. Compare against the [AUR package history](https://aur.archlinux.org) for recent changes.
3. **Remove and reinstall** any suspect AUR packages after confirming the current PKGBUILD is clean.
4. **Check for persistence** — new cron entries, systemd user units, or shell RC modifications added on or after 2026-06-11.
5. **Report** any suspicious PKGBUILD to the [AUR security team](https://aur.archlinux.org/account/) and the [Arch Linux security mailing list](https://lists.archlinux.org/).

## Prevention

- **Always review the PKGBUILD before installing any AUR package.** Most AUR helpers support a pre-build review: `yay --editmenu`, `paru --fm=vim`, or simply download and inspect manually.
- **Use a sandboxed build environment.** [`aurutils`](https://github.com/AladW/aurutils) can build AUR packages in an isolated clean chroot (`aur chroot`), limiting the blast radius of a malicious PKGBUILD to the sandbox.
- **Check votes and comments on the AUR package page.** Zero-vote, recently-created packages are higher risk. Look for comments flagging anomalous behavior.
- **Prefer official repositories** where equivalent packages exist. Check `pacman -Ss <package>` before reaching for AUR.
- **Subscribe to the [Arch Linux security advisories mailing list](https://lists.archlinux.org/mailman3/lists/arch-security.lists.archlinux.org/)** for official vulnerability disclosures.
- → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)

## 2026-06-19 update — 1,500+ packages, eBPF rootkit, orphaned-package takeover, npm cross-ecosystem IOCs

Security researchers expanded analysis to confirm **1,500+ packages** affected (up from initially reported 400+). Key new findings:
- **Orphaned-package takeover** confirmed as primary initial access — attackers registered accounts and adopted abandoned AUR packages to gain their install base without credential theft.
- **eBPF kernel rootkit** deployed as persistence mechanism — invisible to standard process listing and eBPF-based EDR monitoring.
- **`atomic-lockfile` and `js-digest`** rogue npm packages registered by the same actor — cross-ecosystem signal; a machine running Node.js alongside an Arch Linux system is doubly at risk.
- **Arch Linux suspended new AUR account registrations on 2026-06-15** to limit orphaned-package adoption.
- Campaign name "Atomic Arch" applied by researchers; likely distinct actor from IronWorm (npm eBPF worm, same month) but same eBPF rootkit class.

## Sources

- [SecurityWeek — "Atomic Arch": Arch Linux AUR Attack Grows to 1,500+ Packages with eBPF Rootkit](https://securityweek.com) — updated scale; orphaned-package takeover; eBPF rootkit; npm cross-ecosystem IOCs.
- [BleepingComputer — Arch Linux AUR Supply-Chain Attack Expands: 1,500 Packages, eBPF Rootkit, atomic-lockfile npm IOC](https://bleepingcomputer.com) — independent corroboration; Arch Linux account suspension 2026-06-15.
- [The Hacker News — "Atomic Arch" AUR Campaign Now Counts 1,500+ Malicious Packages; eBPF Rootkit Evades EDR Detection](https://thehackernews.com) — eBPF rootkit mechanism; campaign scale; orphaned-package adoption vector.
- [CybersecurityNews — Arch Linux AUR Supplier Attack Expands to 1,500 Packages with Cross-Ecosystem npm IOCs](https://cybersecuritynews.com) — npm package IOCs (atomic-lockfile, js-digest); account suspension.
- [TheRegister — Arch Linux Freezes New AUR Accounts After 1,500-Package Supply-Chain Attack](https://theregister.com) — account-suspension announcement; AUR security model detail.
- [Arch Linux AUR: AUR Trusted Users and Security Model](https://wiki.archlinux.org/title/AUR_Trusted_Users) — official documentation on AUR security posture (no pre-vetting of community packages).
- Cross-link: [IronWorm](2026-06-ironworm-npm-rust-ebpf.md) — distinct eBPF rootkit npm worm, same month; similar persistence mechanism but different actor and ecosystem.
