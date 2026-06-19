---
id: 2026-06-ironworm-npm-rust-ebpf
title: "IronWorm — Rust-based npm worm with eBPF rootkit + Tor C2 (June 2026)"
date_disclosed: 2026-06-04
last_updated: 2026-06-05
severity: critical
status: active
ecosystems: [npm]
tools_affected: [any Node.js project; specifically targets OpenAI Codex, Anthropic, AWS, GitHub, npm, Exodus wallet credentials]
tags: [supply-chain, worm, credential-theft, self-propagating, rust, ebpf, tor]
---

## TL;DR

A new self-propagating npm supply-chain worm called **IronWorm** hit 36 packages in June 2026, deploying a **Rust ELF binary** that hides behind an **eBPF kernel rootkit** and exfiltrates credentials over **Tor** — making it invisible to many eBPF-based security monitoring tools and nearly untraceable at the network layer.

## What happened

JFrog Security Research identified a new npm supply-chain worm starting from a compromised account named **`asteroiddao`**. The attacker published package versions containing a **Rust ELF binary** executed via a `preinstall` lifecycle hook. The worm then pushed malicious commits into the victim's GitHub repositories — with commit timestamps backdated up to 13 years to evade chronological anomaly detection — and self-propagated by using stolen npm credentials (including Trusted Publishing workflow secrets) to publish trojanized versions of the victim's own packages.

**What makes IronWorm distinct from the Miasma/Shai-Hulud family:**

| Dimension | Miasma / Mini Shai-Hulud | IronWorm |
|---|---|---|
| Language | JavaScript | **Rust ELF binary** |
| Install primitive | `binding.gyp` (wave 4), `preinstall` | `preinstall` |
| C2 channel | GitHub Gists / attacker-controlled hosts | **Tor network** |
| Anti-forensics | AI-vendor-host camouflage URLs | **eBPF kernel rootkit** hides from eBPF-based monitors |
| Propagation | npm publish via stolen token | npm publish via stolen token + Trusted Publishing |

**Payload capabilities:**
- Harvests **86 environment variables** and **20 credential files** — specifically targets OpenAI, Anthropic, and AWS credentials alongside npm tokens, SSH keys, and Exodus cryptocurrency wallet files
- **eBPF kernel rootkit** conceals the malware's own operations from EDR and observability tools that also use eBPF for detection (eBPF gives deep kernel visibility and can intercept and filter events)
- Exfiltrates via **Tor** — prevents network-based IOC detection; IP blocklists and DNS monitoring are ineffective
- Backdates git commits (timestamps up to 13 years old) to evade timeline analysis
- Commit author masquerades as **"claude"** to blend into AI-assisted development workflows

**Attribution:** JFrog named this "Shai-Hulud's rustier cousin," acknowledging TTP overlap with the Shai-Hulud family but treating it as a distinct actor. The upgrade from JS to Rust, the eBPF rootkit, and the Tor C2 represent a significant capability escalation beyond the open-sourced Mini Shai-Hulud tooling.

## Am I affected?

```bash
# Check for packages from the compromised account
npm ls 2>/dev/null | grep asteroiddao

# Check installed packages for unexpected Rust/ELF binaries in postinstall output
find node_modules -name "*.node" -newer /tmp/last_week 2>/dev/null

# Look for backdated git commits added recently (timestamp mismatch)
git log --all --format="%H %ai %ci %s" | awk '$2 != $3' | head -20

# Check if unexpected workflows were added
git log --all --oneline -- .github/workflows/ | head -20

# Audit what was published from your npm account recently
npm profile get  # confirm your account wasn't used
```

If you installed any unfamiliar package via `preinstall` between **2026-06-01 and 2026-06-05**, audit your npm token activity at npmjs.com → Account → Access Tokens → Activity.

## If you are affected

1. **Rotate immediately:** npm token, GitHub token, AWS credentials, Anthropic API keys, OpenAI API keys, SSH keys.
2. **Check npm publish history** for unexpected releases from your packages.
3. **Audit GitHub Actions workflows** added or modified after 2026-06-01.
4. **Assume eBPF-based monitoring was blind** during the infection window — check kernel audit logs and process accounting instead.
5. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- **`npm install --ignore-scripts`** blocks the `preinstall` hook (but NOT `binding.gyp` / node-gyp — see [Phantom Gyp advisory](2026-06-phantom-gyp-miasma-wave4.md) for that primitive).
- **Enable npm Trusted Publishing with scoped OIDC** — but note that IronWorm explicitly targets the Trusted Publishing workflow secrets. Rotate these separately.
- **Run npm installs inside an ephemeral sandbox** (Docker, rootless container, VM) so even if eBPF manipulates the kernel, it can't reach host-level secrets.
- **Prefer kernel audit (auditd) over eBPF-only monitoring** for npm CI pipelines — eBPF rootkits can interfere with eBPF-based sensors; auditd syscall logs are harder to suppress without elevated kernel access.
- **Pin packages to exact SHAs** and use `npm ci` with lockfile integrity in CI.

## Sources

- [JFrog Security Research — "IronWorm: Shai-Hulud's rustier cousin"](https://research.jfrog.com/post/iron-worm-shai-hulud-rustier-cousin/) — canonical analysis, eBPF rootkit detail, Tor C2, Rust binary, 36 package list, `asteroiddao` attribution.
- [BleepingComputer — "New IronWorm malware hits 36 packages in npm supply-chain attack"](https://www.bleepingcomputer.com/news/security/new-ironworm-malware-hits-36-packages-in-npm-supply-chain-attack/) — attack overview, propagation mechanism.
- [The Hacker News — Miasma Supply Chain](https://thehackernews.com/2026/06/miasma-supply-chain-attack-compromises.html) — family context.
- Cross-reference: [2026-06-phantom-gyp-miasma-wave4.md](2026-06-phantom-gyp-miasma-wave4.md) (binding.gyp variant, same week), [2026-06-miasma-redhat-cloud-services-compromise.md](2026-06-miasma-redhat-cloud-services-compromise.md).
