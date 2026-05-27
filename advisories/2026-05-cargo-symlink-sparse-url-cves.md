---
id: 2026-05-cargo-symlink-sparse-url-cves
title: "Cargo May 2026 security release — symlink-override + sparse-URL credential leak (CVE-2026-5223, CVE-2026-5222)"
date_disclosed: 2026-05-25
last_updated: 2026-05-27
severity: medium
status: patched
ecosystems: [crates, rust, registry, supply-chain]
tools_affected: [cargo, rust, third-party-cargo-registries]
tags: [supply-chain, registry-hygiene, symlink, sparse-registry, cargo, rust]
---

## TL;DR
On **2026-05-25** the Rust Security Response Team disclosed two Cargo CVEs, both fixed in **Rust 1.96.0 (released 2026-05-28)**:

- **CVE-2026-5223 (medium):** Cargo did not reject **symlinks inside crate tarballs** from third-party registries — a malicious crate could ship a tarball whose extraction wrote files **one directory up** from its own cache and **overwrote the cached source of another crate from the same registry**. crates.io itself is **not affected** because it server-side-rejects symlink uploads; corporate / mirror Cargo registries that don't are.
- **CVE-2026-5222 (low):** Cargo's **sparse-registry** URL normalization unintentionally stripped the `.git` suffix, so credentials saved for `https://example.com/index.git` could be **replayed against `https://example.com/index`**. Niche but enables credential leakage to a different registry hosted on the same domain.

Both bugs affect **every Cargo shipped before Rust 1.96.0**. **crates.io users are NOT affected by 5223; users of self-hosted / corporate Rust registries are.** Treat the disclosure as an additional reason to put **registry-side symlink rejection** in place (mirror operators) and to **upgrade to Rust 1.96.0** (every Rust developer).

## Why this is in scope for a vibe-coding feed

We added Crates.io / Rust to the cross-ecosystem rotation last week after [TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md) showed an actor running npm + PyPI + Crates.io in a single coordinated wave. CVE-2026-5223 is the **first Cargo-itself bug in this repo**, and it's the kind of primitive future TrapDoor-style attackers will compose with: drop a malicious crate that overwrites another crate's source in the *same* enterprise registry, then wait for a CI build to pick up the substituted code. It's a generalizable lesson: **build systems treat archive-extraction as plumbing, but every archive primitive — symlinks, ZIP slip, path traversal — is a supply-chain primitive in disguise.**

## What happened

### CVE-2026-5223 — symlink-override in third-party Cargo registries

When Cargo downloads a crate tarball from a registry, it extracts it under `~/.cargo/registry/src/<registry>/<crate>-<version>/`. The Rust Security Response Team found that **Cargo did not block symlinks inside the tarball**, so a malicious crate could ship a tarball whose extraction included a symlink pointing *one directory up* into `~/.cargo/registry/src/<registry>/<other-crate>-<version>/`. Writes through that symlink would **overwrite the cached source of another crate from the same registry** — meaning a `cargo build` that depends on the victim crate would compile attacker-controlled code under the victim crate's name.

- **Severity:** medium for users of third-party registries.
- **crates.io users are NOT affected** — crates.io has always forbidden symlinks in uploaded crates and rejects them server-side.
- **Affected:** every Cargo shipped before Rust 1.96.0.
- **Fix:** Rust 1.96.0 — Cargo now refuses to extract any symlink within crate tarballs, **regardless of registry**.
- **Mitigation if you can't upgrade immediately:** audit any third-party Cargo registry you depend on for the presence of symlinks in published crates and, if the registry supports it, configure it to reject symlink uploads server-side.

### CVE-2026-5222 — sparse-registry URL normalization leaks credentials

When Cargo introduced sparse index protocol (`registry+https://...`), it inherited an older git-protocol normalization that **stripped a trailing `.git`** from registry URLs. The two URLs `https://example.com/index` and `https://example.com/index.git` were treated as the same registry — including for **credential lookup**. If a single domain hosts two registries that differ only by a `.git` suffix and a user has saved credentials for one, an attacker who can publish crates in the *other* could **harvest the user's credentials** by serving a normal sparse-index response and watching the inbound `Authorization` header.

- **Severity:** low — extremely niche prerequisites (multiple registries on one domain, sparse protocol).
- **Affected:** every Cargo shipped between Rust 1.68 (sparse-index stabilization) and Rust 1.96.
- **Fix:** Rust 1.96.0 — the `.git` strip is now scoped to git-protocol URLs only.

## Am I affected?

```bash
# Are you on the vulnerable Cargo range?
rustc --version    # affected if < 1.96.0 (released 2026-05-28)

# Do you use any third-party (non-crates.io) Cargo registry? (5223 is most relevant here.)
grep -RE '^\[registries\.|^registry *=' ~/.cargo/config.toml .cargo/config.toml 2>/dev/null

# If you operate a corporate/mirror Cargo registry: does it reject symlinks in uploads?
#   - Test by uploading a crate with a symlinked file and confirming it is rejected at publish time.
```

You are affected by 5223 if you depend on any third-party Cargo registry that did not previously enforce server-side symlink rejection. You are affected by 5222 if you ever used the sparse protocol against a host that runs multiple registries on the same domain.

You are **not** affected by 5223 if **all** your Cargo dependencies resolve through crates.io exclusively.

### IOCs

There are no public IOCs — these are pre-disclosure Cargo CVEs, not in-the-wild attacks. Detection is **build-system** hygiene, not malware-hunting:

| Check | What to look for |
|---|---|
| Symlinks in published crates on a private/mirror registry | `find <registry-storage> -type l` |
| Cargo version pinned in CI images | `rustc --version` < 1.96.0 |
| Sparse-registry config on multi-registry domains | `cat ~/.cargo/config.toml` — registries hosted on the same domain differing only by path |

## If you are affected

- Upgrade to **Rust 1.96.0** (rustup `update stable`) as soon as it's released on **2026-05-28**.
- Operators of self-hosted / corporate Cargo registries: enable **server-side symlink rejection** if your registry product supports it. Audit existing storage for any symlinks (`find ... -type l`).
- Audit CI build images that pin a specific older Rust toolchain — pinning is fine but it now means you carry these two CVEs until you bump the pin.

## Prevention

- [Package vetting checklist](../prevention/package-vetting-checklist.md) — generalizes to Rust: pin by version, audit build scripts (`build.rs`), and review your registry trust list.
- [Credential hygiene](../prevention/credential-hygiene.md) — for sparse-registry creds: prefer short-lived tokens scoped to a single registry URL rather than a domain.

Pattern lesson: **registry-side hygiene matters as much as client-side.** crates.io's blanket symlink rejection is *why* its users aren't affected by CVE-2026-5223. The same rule generalizes:

- npm registries: reject `postinstall` from anonymous publishers / first-week accounts.
- PyPI / private mirrors: reject `*.pth` top-level files in uploaded wheels (the [elementary-data](2026-04-elementary-data-pypi-ghcr-compromise.md) primitive).
- Cargo registries: reject symlinks in uploaded crates (the CVE-2026-5223 primitive).

Every archive-extraction primitive a client doesn't guard is one a registry can guard server-side, and vice-versa. Defense in depth.

## Sources

- [Security Advisory for Cargo (CVE-2026-5223) — Rust Blog, 2026-05-25](https://blog.rust-lang.org/2026/05/25/cve-2026-5223/) — canonical disclosure (symlink override). (HTTP 403 on direct fetch; cited via multi-source quotation.)
- [Security Advisory for Cargo (CVE-2026-5222) — Rust Blog, 2026-05-25](https://blog.rust-lang.org/2026/05/25/cve-2026-5222/) — canonical disclosure (sparse-registry URL normalization).
- [CVE-2026-5223 — Vulnerability-Lookup (CIRCL)](https://vulnerability.circl.lu/vuln/cve-2026-5223) — independent reference entry.
- [RustSec — Advisory Database](https://rustsec.org/) — index of Rust ecosystem CVEs.
- [Rust Bytes — JUST IN: Security Advisory for Cargo (Mastodon)](https://mastodon.social/@rustaceans/116636057366962625) — independent corroboration on Mastodon.
- [freedit.eu — Security Advisory for Cargo (CVE-2026-5223)](https://freedit.eu/post/2/274) — mirror of the Rust Blog post.
- [freedit.eu — Security Advisory for Cargo (CVE-2026-5222)](https://freedit.eu/post/2/273) — mirror of the Rust Blog post.
- [WTFpkg — Cargo extraction attacks](https://0xv1n.github.io/WTFpkg/techniques/cargo-extraction-attacks/) — third-party technical analysis of Cargo extraction primitives.
