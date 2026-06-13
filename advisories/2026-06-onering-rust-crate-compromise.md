---
id: 2026-06-onering-rust-crate-compromise
title: "onering Rust crate compromised — build.rs exfiltrates your source code as fake Sentry telemetry (June 2026)"
date_disclosed: 2026-06-10
last_updated: 2026-06-13
severity: high
status: unconfirmed
ecosystems: [crates]
tools_affected: [onering, any project with onering in its Cargo.toml]
tags: [supply-chain, credential-theft, crates-io, rust, build-rs, code-exfiltration, account-compromise]
---

## TL;DR

On **2026-06-10**, Aikido Security detected malicious behavior in **`onering` v1.4.1** — a Rust synchronous queue/channels library (~18K Crates.io downloads). The malicious version injected a **`build.rs`** script that silently exfiltrates your **git diff / source code changes** to a remote server on every Cargo build, disguising the stolen data as a **Sentry telemetry event**. Both the Crates.io release and the maintainer's GitHub repository appear to be compromised — building from git does NOT make you safe.

> ⚠️ **Status: unconfirmed** — single primary source (Aikido) at time of publication. Treating as real given Aikido's weight-20 track record on supply-chain detection.

## What happened

On June 10, 2026, Aikido Security detected that **`onering` version 1.4.1** (a high-throughput synchronous queue and channels library for Rust) introduced a malicious `build.rs` file that was absent in prior versions.

### What the malicious build.rs does

The injected build script performs three operations on every `cargo build`:

1. **Locates the consuming project's root** via Cargo environment variables.
2. **Runs `git diff HEAD^ HEAD`** to capture the full diff of the consuming project's latest commit — your actual source code changes, not just onering's own code.
3. **Exfiltrates the diff to a remote server** via `curl`, disguised as a Sentry crash-report telemetry POST. The commit metadata becomes event tags; the code diff is stuffed into the `extra.patch` field.

This means that over many builds, the attacker receives a **rolling stream of your real source code changes** rather than a single snapshot. Any project that depends on `onering` and is actively developed will leak every committed change.

### Why "Sentry disguise" matters

Sentry ingest endpoints (`sentry.io/api/...`) are on most organizations' egress allowlists as normal error-telemetry traffic. Disguising the exfiltration as a Sentry event blends the outbound request into normal developer tooling egress — the same technique as the `codexui-android` actor who disguised exfil as a Sentry POST to a fake Sentry host (`sentry.anyclaw.store`).

### Scope of compromise

- The **Crates.io published package** (`onering` v1.4.1) is confirmed malicious.
- The **maintainer's GitHub repository** also appears compromised — pulling from git does not provide a clean build.
- Only `v1.4.1` is confirmed; prior versions are unaffected.

## Am I affected?

```bash
# Check if onering is in your dependency tree
cargo tree | grep onering

# Check which version is pinned in Cargo.lock
grep -A2 'name = "onering"' Cargo.lock

# If you have onering 1.4.1 installed, check for recent curl invocations in build output
# (may be suppressed by Cargo; check with verbose build)
cargo build -v 2>&1 | grep -i 'sentry\|curl'

# Grep build.rs of onering for signs of the malicious code
find ~/.cargo/registry/src -path '*/onering-1.4.1/build.rs' -exec cat {} \;
```

If your `Cargo.lock` pins `onering = "1.4.1"`, treat your source code repository as potentially compromised.

## If you are affected

1. **Pin to a known-safe version** of onering in `Cargo.toml` (e.g., `onering = "=1.4.0"`) or remove the dependency.
2. **Assume source code exfiltration** for any code changes built while v1.4.1 was active — rotate secrets embedded in or adjacent to the leaked diffs (API keys in config files, hardcoded tokens).
3. **Check git history** for any unexpected commits or pushes around the time v1.4.1 was installed.
4. **Audit outbound network traffic** from your CI runners for unexpected POSTs to Sentry-looking endpoints from build processes.

## Context: supply-chain compromise in the Rust ecosystem

This is consistent with the now-established `build.rs`-as-execution-primitive pattern in Rust supply-chain attacks. Unlike npm's `postinstall`, `build.rs` runs during `cargo build` and is not suppressed by any equivalent of `--ignore-scripts`. All `build.rs` scripts in your dependency tree run with full file-system access and can make outbound network connections.

Notable Rust supply-chain incidents this year:
- [TrapDoor (May 2026)](2026-05-trapdoor-cross-ecosystem-stealer.md) — cross-ecosystem npm+PyPI+Crates.io; `build.rs` XOR-encrypts keystores → GitHub Gists.
- [Cargo CVE-2026-5223 / CVE-2026-5222 (May 2026)](2026-05-cargo-symlink-sparse-url-cves.md) — Cargo-level archive-extraction vulnerabilities.
- Five malicious Rust crates posing as time utilities (March 2026) — `.env` file exfiltration.

## Sources

- [Aikido Security — Compromised Rust crate onering performs code exfiltration](https://www.aikido.dev/blog/compromised-rust-crate-onering-performs-code-exfiltration) — primary detection and technical analysis.
