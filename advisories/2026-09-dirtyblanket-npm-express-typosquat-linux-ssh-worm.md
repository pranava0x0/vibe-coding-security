---
id: 2026-09-dirtyblanket-npm-express-typosquat-linux-ssh-worm
title: "DirtyBlanket — nine npm packages impersonating Express and React (xeprews, express-nodejs, express-javascript, react-nodejs, exprdd…) published in 33 minutes on 2026-09-29 carried an install hook that, on Linux, installs a Tor-controlled remote-access backdoor disguised as a systemd font service and spreads itself over the victim's SSH keys, npm publish tokens and Arch AUR packages (SafeDep); all nine unpublished the same day"
date_disclosed: 2026-09-29
last_updated: 2026-09-30
severity: high
status: contained
ecosystems: [npm, linux, arch-aur, ssh]
tools_affected: ["Linux hosts that ran npm install on any of the nine packages", "SSH keys and known_hosts on those machines", "npm publish tokens on those machines", "Arch User Repository packages maintained from those machines", "CI runners and dev containers with an SSH agent"]
tags: [supply-chain, typosquat, express, react, preinstall, worm, ssh-lateral-movement, npm-token, aur, tor, contained]
---

## TL;DR

On **2026-09-29 between 06:05 and 06:38 UTC** an npm account named `dirtyblanket` published **nine packages** — eight look-alikes of **Express** (`xeprews`, `express-javascript`, `express-nodejs`, `exprdd`, `exprrdd`, `exptrdd`, `exptred`, `exptredd`, all at Express's real current version 5.2.1 with Express's author, repository and homepage metadata copied in) and one of **React** (`react-nodejs` 19.3.0). Each declares a `preinstall` lifecycle hook. On Linux the hook ends in a self-propagating worm: it installs a **Tor-tunnelled remote-access backdoor** registered as a fake systemd "Font Rendering Service", **uses every SSH private key and `known_hosts` entry on the machine to log into other hosts and run itself there**, **republishes the victim's own npm packages with the same hook using any npm token it finds**, and **injects itself into Arch AUR `.install` files** the victim maintains. SafeDep published the analysis the same day; the registry shows all nine unpublished and `xeprews` recorded **0 downloads** for the week ending 09-28. Status `contained` for the registry side — but a worm that spreads over SSH does not need npm any more once it is on a host. macOS and Windows installs are not affected by the payload, but a developer whose laptop is fine may still have seeded every Linux host their key reaches.

## What happened

SafeDep's write-up (2026-09-29) describes a three-stage install chain that is Linux-only past the first step, and a worm with six behaviours. The defender-relevant facts:

- **Delivery** is a plain npm `preinstall` hook that fetches a loader from a public archive front — an egress destination most allowlists permit — so `--ignore-scripts` stops it at the door and a network policy that trusts archive hosts does not.
- **Persistence** is a modified open-source remote-access client installed as `systemd-fontd`, presented as a "Font Rendering Service" / "Font Caching Service", talking to its operator over the local Tor SOCKS port. It gives the operator a shell, file upload/download/deletion, screenshots and reboot — as root if the install ran as root. Root installs set the **immutable attribute** on the binary and unit files.
- **Propagation** is the reason this file exists: (1) every SSH private key and every `known_hosts` on the box is used to log into each known host and run the worm there; (2) npm tokens on the box are used to publish new versions of the victim's own packages with the hook injected; (3) `.install` files of AUR packages the victim maintains are rewritten so the worm ships to every Arch user who installs them next. Any CI runner, jump box or dev container reachable by an agent-forwarded key is a hop.

Two facts settle the registry side. `registry.npmjs.org` returned **`unpublished`** for `xeprews`, `express-javascript`, `express-nodejs`, `react-nodejs` and `exprdd` when queried 2026-09-30 — no versions, no dist-tags — and **OSV MAL-2026-17248** ("Malicious code in xeprews (npm)", published 2026-09-29T14:40Z) is the OpenSSF record of the takedown. `api.npmjs.org` shows **0 downloads** for `xeprews` in the week ending 09-28; the packages existed for hours, and SafeDep does not report a download count. A CachyOS forum post the same evening is the Arch community relaying SafeDep, not independent telemetry. **Nobody has reported an infected host**; the severity here is the blast radius of the design — SSH plus npm-token plus AUR is three propagation channels, only one of which the registry can close — not confirmed victims.

Two technique-neutral lessons: the impersonation copied Express's `package.json` metadata verbatim, so `npm view <pkg> repository` shows `expressjs/express` for a package that is not Express — check the **name**, not the metadata; and a fetch-anything archive proxy in an egress allowlist is a code-delivery channel.

## Am I affected?

```bash
# 1. Did any of the nine names enter a lockfile, a cache or a build log?
grep -rE '"(xeprews|express-javascript|express-nodejs|react-nodejs|exprdd|exprrdd|exptrdd|exptred|exptredd)"' \
  package.json package-lock.json pnpm-lock.yaml yarn.lock 2>/dev/null
grep -rlE 'xeprews|express-nodejs|express-javascript|react-nodejs' ~/.npm/_cacache/index-v5 2>/dev/null | head

# 2. Host indicators (Linux) — any hit means treat the machine as fully compromised
ls -la /usr/lib/systemd/systemd-fontrenderd /etc/systemd/system/systemd-fontrenderd.service \
       ~/.config/systemd/systemd-fontcached ~/.config/systemd/user/systemd-font*.service 2>/dev/null
lsattr /usr/lib/systemd/systemd-fontrenderd /etc/systemd/system/systemd-fontrenderd.service 2>/dev/null   # 'i' = immutable
systemctl list-units --all | grep -i 'font rendering\|font caching\|fontrenderd\|fontcached'
pgrep -a tor; ss -tlnp | grep ':9050'           # a Tor daemon you did not install
ls -la /tmp/log 2>/dev/null                     # written by SSH-propagated infections

# 3. Did the worm arrive over SSH from another host you own?
grep -h 'Accepted publickey' /var/log/auth.log /var/log/secure 2>/dev/null | grep 'Sep 29\|Sep 30' | head

# 4. npm packages you maintain: any version published on/after 2026-09-29 that you did not cut, with a preinstall hook?
npm view <your-package> time --json | tail -5; npm view <your-package>@latest scripts
```

Also diff any **AUR package you maintain** for a changed `.install` file since 09-29. The exact file names, service names and the backdoor's SHA-256 are in SafeDep's post.

## If you are affected

- **Treat the host as fully compromised**: the implant is a remote shell with a Tor transport; reimage rather than clean. [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
- **Revoke and regenerate every SSH key** that was on the machine and review `authorized_keys` on every host in its `known_hosts` — those hosts may already be infected; check them with the indicators above. [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).
- **Revoke npm tokens** and audit your packages' `time` fields for versions you did not publish; unpublish or deprecate them and warn dependents. [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
- **Revoke AUR credentials** and diff every `.install` file you maintain; notify the AUR team if anything shipped.
- Inspect Git history from that machine for commits you did not make.

## Prevention

- `npm config set ignore-scripts true`, and `pnpm` with an explicit `onlyBuiltDependencies` allowlist — a `preinstall` hook is the entire delivery mechanism. [prevention/npm-hardening.md](../prevention/npm-hardening.md).
- Vet by **name**, not metadata: Express is `express`; anything else carrying Express's README is not. [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- Keep SSH keys off build hosts (agent forwarding with confirmation, or short-lived certificates) and keep npm publish tokens out of developer shells (trusted publishing / OIDC) — both propagation channels are "a long-lived secret was sitting on disk." [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- Treat archive proxies like paste sites in build-environment egress policy. [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).

## Sources

- [SafeDep — DirtyBlanket: Fake Express Packages on npm Spread a Linux Worm](https://safedep.io/dirtyblanket-express-impersonation-npm/) — primary, 2026-09-29: the nine packages and publish window, the `dirtyblanket` account, the install chain, the worm's behaviours, the file/service/process indicators and the implant hash, remediation. Fetched 2026-09-30. Its live download and command-and-control addresses are deliberately not reproduced here.
- [OSV — MAL-2026-17248: Malicious code in xeprews (npm)](https://osv.dev/vulnerability/MAL-2026-17248) — OpenSSF malicious-package record, published 2026-09-29; the registry-side second source for the takedown. Fetched 2026-09-30.
- npm registry (`registry.npmjs.org/<pkg>`, queried 2026-09-30): `xeprews`, `express-javascript`, `express-nodejs`, `react-nodejs`, `exprdd` all return `unpublished` with no versions or dist-tags. `api.npmjs.org/downloads/point/last-week/xeprews` (2026-09-22 → 09-28): 0.
- [CachyOS forum — AUR: NPM supply chain attack targeting AUR packages](https://discuss.cachyos.org/t/aur-npm-supply-chain-attack-targeting-aur-packages/36428) — 2026-09-29 community relay of the SafeDep report; no additional victims or package names. Fetched 2026-09-30.
- Related in this corpus: [Arch Linux AUR supply-chain incident (June 2026)](2026-06-arch-linux-aur-supply-chain.md), [Shai-Hulud (self-propagating npm worm, 2025)](2025-09-shai-hulud-original.md), [MemTensor sckit worm](2026-09-memtensor-memos-openclaw-plugin-sckit-worm.md).
