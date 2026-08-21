---
id: 2026-08-arrayref-proc-macro1-crates-io
title: "arrayref (244M downloads) and append-only-vec hijacked on crates.io to pull a build-time infostealer via a typosquatted proc-macro1 dependency (August 2026)"
date_disclosed: 2026-08-20
last_updated: 2026-08-21
severity: critical
status: contained
ecosystems: [crates-io, rust]
tools_affected: [arrayref, append-only-vec, internment, proc-macro1, cargo]
tags: [supply-chain, crates-io, rust, build-rs, typosquatting, credential-theft, infostealer, maintainer-compromise]
---

## TL;DR

On **2026-08-20**, a compromised crates.io maintainer account published malicious versions of **`arrayref` (~244–245M all-time downloads), `append-only-vec` (~4M), and `internment`**, each adding a single dependency line on **`proc-macro1`** — a typosquat of the legitimate `proc-macro2`, published under an account impersonating its real author. `proc-macro1`'s **`build.rs` downloads and executes a platform-specific binary at compile time**, so merely *building* a project that resolves the dependency is enough to get infected — no function of the crate needs to be called. The malicious versions were live for **86–107 minutes** before the Rust Security Response Team removed them and locked the account.

## What happened

The [Rust Security Response Team](https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/) received a report at **07:15 UTC on 2026-08-20** that the `proc-macro1` crate was malicious, and confirmed that the crate carried a build script downloading a remote payload. Investigation showed a **compromised maintainer account** had published malicious versions of three legitimate crates that depended on the fake one.

**The malicious versions and their exposure windows** (per the Rust team's own post):

| Crate | Malicious version | Minutes live |
|---|---|---|
| `arrayref` | `0.3.10` | 86 |
| `append-only-vec` | `0.1.9` | 107 |
| `internment` | `0.8.7` | 90 |

The following attacker-published crates were **deleted entirely** from crates.io: `proc-macro1`, `proc-macro-en`, `aovine`, `arone`, `aronenao`, `tinymember`.

**The typosquat.** The attacker registered a GitHub account and a matching crates.io account impersonating **David Tolnay (`dtolnay`)**, the real author of the extremely widely used `proc-macro2`, and published a clean copy of `proc-macro2` under the near-identical name **`proc-macro1`** as staging, later adding the malicious build dependency and forged author metadata ([Aikido](https://www.aikido.dev/blog/two-popular-rust-crates-arrayref-and-append-only-vec-compromised-in-supply-chain-attack)). The hijack of the legitimate crates was then a **one-line manifest change** — adding `proc-macro1 = "1.0.107"` — which is easy to miss in a diff and does not itself look like malware.

**The payload.** Per [SafeDep's analysis](https://safedep.io/arrayref-proc-macro1-rust-build-time-malware/), `proc-macro1`'s `build.rs`:

- Reassembles the attacker's server address from **base64 fragments** so the raw IP never appears literally in the source.
- Connects over HTTPS to **`23.254.165.112:9089`** using a **custom TLS verifier that accepts any certificate without validation**, so a self-signed cert on the attacker's host works fine.
- Selects a platform-specific stage-2 binary — `rust-crate_0.1.0` (Linux x86_64), `_0.2.0` (Windows x86_64), `_0.3.0` (macOS x86_64), `_0.4.0` (macOS ARM64).
- On Unix, writes it to `/tmp/rust-setup`, marks it executable, and spawns it **detached**, passing the C2 address (`23.254.165.112:443`) as an argument. On Windows it **routes execution through WScript to escape Cargo's job object**, so the payload survives after the build finishes, writing a PowerShell script and a VBScript launcher to `%TEMP%`.

Stage 2 is a credential stealer with remote-control capability: it extracts saved passwords from **Chromium-based browsers (Chrome, Brave, Edge)**, reads **browser-extension storage where cryptocurrency wallets keep data**, installs a **macOS LaunchAgent for persistence**, and accepts `Shell`, `runscript`, and `ShellX` commands from its C2 ([Aikido](https://www.aikido.dev/blog/two-popular-rust-crates-arrayref-and-append-only-vec-compromised-in-supply-chain-attack)).

**On attribution:** the Rust team stated it does **not** believe the `arrayref` author acted maliciously — the account (in good standing since 2009) or its credentials were most likely compromised. The account was locked as a precaution and the legitimate yanked versions were restored.

**Update (2026-08-21) — Wiz reports substantial infrastructure overlap with DPRK campaigns.** Wiz published its own analysis on 2026-08-20 claiming three concrete overlaps with North Korean supply-chain activity, none of which contradicts the Rust team's account-compromise assessment (Wiz likewise frames the entry point as stolen maintainer credentials):

1. **Shared C2 URI path.** The `arrayref` payloads beacon to the path `/49890878`, which Wiz says was also used in the [Mastra npm compromise](2026-06-mastra-ai-npm-compromise.md) — attributed by Microsoft to **DPRK / Sapphire Sleet**. Wiz reports the IP also shares an SSL issuer with infrastructure from that campaign.
2. **Overlap with the axios compromise.** A victim-reported C2 IP appears in Google Cloud Threat Intelligence's analysis of **UNC1069**'s [axios npm attack](2026-03-axios-compromise.md), which Mandiant links to North Korea.
3. **Shared hosting preference.** Both campaigns used the same **23.254.164.0/23 Hostwinds LLC** range — consistent with this incident's C2 at `23.254.165.112`.

Treat this as **overlap, not formal attribution**: no vendor has formally attributed this incident to a named threat actor, and infrastructure reuse is a weaker signal than payload identity. It is, however, a reason to check whether your org appears in the victim sets of the two cross-linked npm incidents — this repo's standing "trace the leaked token forward" discipline applies across ecosystems, not just within npm.

Also refined this sweep: The Hacker News reports the exact `arrayref` download figures as **245,385,500 all-time** and **53,905,601 in the preceding 90 days** — the 90-day number is the one that matters for "how many builds could plausibly have resolved this," and it is the first precise recent-activity figure published for this incident.

**Why this matters for this repo's audience.** `build.rs` is the Rust analogue of an npm `postinstall` hook or a PyPI import-time exec — and it is the *fourth* install/build-time execution primitive this repo tracks (see [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)). Critically, **`cargo` has no `--ignore-scripts` equivalent**: build scripts are a core part of how Cargo compiles native code, so there is no flag a developer can pass to opt out. Any CI runner, container build, or developer laptop that ran `cargo build` against a tree resolving these versions during the ~2-hour window executed attacker code. This is the same shape as the [TrapDoor cross-ecosystem campaign](2026-05-trapdoor-cross-ecosystem-stealer.md) and the [onering crate compromise](2026-06-onering-rust-crate-compromise.md), but at a far larger download scale — by download count this is the largest crates.io compromise reported to date.

## Am I affected?

The exposure window was roughly **07:15–09:25 UTC on 2026-08-20**. If nothing in your org ran `cargo build`, `cargo fetch`, or a CI job resolving these crates in that window, you are almost certainly fine.

Check your local Cargo registry cache for the malicious versions:

```bash
find ~/.cargo/registry -maxdepth 3 \( \
  -name 'arrayref-0.3.10*' -o \
  -name 'append-only-vec-0.1.9*' -o \
  -name 'internment-0.8.7*' -o \
  -name 'proc-macro1-*' -o \
  -name 'proc-macro-en-*' -o \
  -name 'aovine-*' -o -name 'arone-*' -o -name 'aronenao-*' -o -name 'tinymember-*' \
\) -print
```

Check your lockfiles across every repo (the malicious versions may have been pinned into a `Cargo.lock` by a CI run):

```bash
grep -rn -E 'name = "(proc-macro1|proc-macro-en|aovine|arone|aronenao|tinymember)"' --include=Cargo.lock .
grep -rn -A1 -E 'name = "(arrayref|append-only-vec|internment)"' --include=Cargo.lock . | grep -E '0\.3\.10|0\.1\.9|0\.8\.7'
```

Look for the dropped payload and its persistence:

```bash
# Unix
ls -la /tmp/rust-setup 2>/dev/null
# macOS persistence
ls -la ~/Library/LaunchAgents/ /Library/LaunchAgents/ 2>/dev/null
# Windows: check %TEMP% for unexpected .ps1 / .vbs launchers
```

Network IOC — any outbound connection to **`23.254.165.112`** (ports **9089** and **443**) from a build host is a confirmed compromise signal.

**File hashes (SHA-256), per SafeDep:**
- `arrayref` 0.3.10 — `25ad700976873c76af785cb99b33c48db7df8b81f21d1e9e06b3676b9a9373ae`
- `proc-macro1` 1.0.107 — `61198155da51b838772eecf5bfaac6cbc4dcc388dccc56658fc28a8e831b34d4`

## If you are affected

1. **Treat the build host as fully compromised.** The payload runs with your user's privileges and has arbitrary shell command execution via C2.
2. **Rotate browser-stored credentials first** — the stealer specifically targets saved Chromium passwords. Then rotate everything else that was reachable from that host.
3. **If you hold cryptocurrency in a browser-extension wallet, move funds now** from a different, known-clean device — extension storage was an explicit target.
4. Remove persistence: check macOS LaunchAgents and Windows `%TEMP%` launchers as above; delete `/tmp/rust-setup`.
5. Purge and re-resolve dependencies: `cargo clean`, delete the affected entries from `~/.cargo/registry`, then rebuild against restored-clean versions.
6. See [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) — the build-time-execution remediation path is the same — and [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) for CI runners.

## Prevention

- **You cannot disable Cargo build scripts.** There is no `--ignore-scripts`; treat every `cargo build` against unvetted or newly-updated dependencies as code execution. Build in a container or disposable CI runner rather than on a laptop holding browser profiles and wallets.
- **Commit and review `Cargo.lock`.** A one-line new dependency in a patch-version bump of a crate you already trust is exactly what this attack looks like in a diff.
- **Delay adoption of fresh releases.** The malicious versions were live under two hours; any policy that waits even a day on new versions would have avoided this entirely — the Rust equivalent of npm's `minimumReleaseAge`.
- **Egress-filter build hosts.** A build machine reaching an unfamiliar bare IP on a non-standard port (`:9089`) is the anomaly that would have caught this instantly.
- See [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) and [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).

## Sources

- [Supply chain attack on arrayref — Rust Blog (Rust Security Response WG)](https://blog.rust-lang.org/2026/08/20/supply-chain-attack-on-arrayref/) — primary vendor disclosure: timeline, exact affected versions and exposure windows, deleted crates, account-compromise assessment, recommended user check.
- [Malicious Rust Crate arrayref Runs a Build-Time Payload — SafeDep](https://safedep.io/arrayref-proc-macro1-rust-build-time-malware/) — technical analysis of `build.rs`: base64-fragmented C2 address, TLS-verification bypass, per-platform binaries, Unix/Windows execution paths, SHA-256 hashes.
- [Two popular Rust crates arrayref and append-only-vec compromised in Supply Chain Attack — Aikido](https://www.aikido.dev/blog/two-popular-rust-crates-arrayref-and-append-only-vec-compromised-in-supply-chain-attack) — download counts, the `dtolnay`-impersonating typosquat account, stage-2 stealer capabilities (Chromium passwords, wallet extension storage, macOS LaunchAgent persistence, C2 command set).
- [Rust Supply Chain Attack on arrayref: Significant Overlap with DPRK Campaigns — Wiz](https://www.wiz.io/blog/rust-supply-chain-attack-on-arrayref-significant-overlap-with-dprk-campaigns) — added 2026-08-21: the three claimed DPRK infrastructure overlaps (shared `/49890878` C2 path with the Mastra campaign, shared SSL issuer, UNC1069/axios IP overlap, Hostwinds 23.254.164.0/23 range).
- [Rust Supply Chain Attack Puts Build-Time Malware in Crates with 245 Million Downloads — The Hacker News](https://thehackernews.com/2026/08/rust-supply-chain-attack-puts-build.html) — added 2026-08-21: exact download figures (245,385,500 all-time / 53,905,601 in 90 days), per-crate publish/deletion timestamps, and confirmation that no vendor has formally attributed the incident to a named actor.
