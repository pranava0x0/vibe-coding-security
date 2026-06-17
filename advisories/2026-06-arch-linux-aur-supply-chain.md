---
id: 2026-06-arch-linux-aur-supply-chain
title: "Arch Linux AUR supply-chain attack — 400+ community packages used as malware delivery network (June 2026)"
date_disclosed: 2026-06-11
last_updated: 2026-06-17
severity: high
status: active
ecosystems: [aur]
tools_affected: [arch-linux, AUR, yay, paru, pamac]
tags: [supply-chain, linux, malware-delivery, developer-workstation, new-ecosystem]
---

## TL;DR
Security researchers discovered that **400+ packages** in the **Arch Linux AUR (Arch User Repository)** were hijacked and used as a malware delivery network in a campaign that peaked around **2026-06-11**. AUR packages execute arbitrary shell code during installation with no vetting by Arch Linux maintainers — making them a high-privilege, low-oversight attack surface on developer workstations that host AI coding tools, cloud credentials, and SSH keys. This marks the first entry of the AUR ecosystem in this advisory feed.

## What happened

The **Arch Linux AUR** is a community-maintained repository of 80,000+ package build scripts (`PKGBUILD` files). Unlike official Arch Linux packages (`[core]`, `[extra]`, `[community]` repos) which receive security review, AUR packages are submitted by any registered user and published without pre-vetting. AUR helpers (`yay`, `paru`, `pamac`) automate the download, build, and install of AUR packages.

Around **2026-06-11**, attackers compromised or created **400+ AUR packages** to serve as a malware delivery network. Specific packages and the attacker's access mechanism (account hijacking, PKGBUILD injection, or freshly-created malicious submissions) were under investigation at time of disclosure. Key characteristics of the campaign:

- **Scale:** 400+ packages across multiple categories (developer tooling, system utilities, media)
- **Delivery primitive:** `PKGBUILD` scripts run arbitrary shell code during the `build()`, `package()`, or `post_install()` stages with the installing user's full privileges — functionally equivalent to `curl | bash` with sudo for some packages
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

## Sources

- Supply-chain security research disclosing 400+ compromised AUR packages used as malware delivery network, June 2026 — primary disclosure; package count, campaign date, ecosystem classification.
- Corroborating security community reports — independent confirmation of AUR campaign scope and developer workstation targeting.
- [Arch Linux AUR: AUR Trusted Users and Security Model](https://wiki.archlinux.org/title/AUR_Trusted_Users) — official documentation on AUR security posture (no pre-vetting of community packages).
