---
id: 2026-09-rust-miri-github-actions-cache-secrets-leak
title: "Miri wrote every environment variable of the CI job into target/ — and projects that cache target/ in GitHub Actions (actions/cache, Swatinem/rust-cache) with a cache readable by pull requests handed their secrets to any PR author; Rust Security Response WG disclosure 2026-09-21, fixed in the 2026-09-22 nightly"
date_disclosed: 2026-09-21
last_updated: 2026-09-24
severity: medium
status: patched
ecosystems: [rust, cargo, github-actions, ci-cd]
tools_affected: ["Miri (cargo miri) before the 2026-09-22 nightly", "GitHub Actions workflows that run cargo miri with secrets in the environment and cache target/ (actions/cache, Swatinem/rust-cache)"]
tags: [ci-cd, secrets-exposure, github-actions, cache-poisoning, rust, miri, registry-team-disclosure, supply-chain]
---

## TL;DR
On **2026-09-21** the Rust Security Response Working Group published "GitHub Actions leaking secrets when Miri output is cached." **Miri**, Rust's undefined-behaviour interpreter, "stores all environment variables to `target/`" — the whole job environment, secrets included — as part of its build output. If a workflow (a) runs `cargo miri`, (b) has secrets exposed as environment variables in that step, (c) caches `target/` with `actions/cache` or `Swatinem/rust-cache`, and (d) accepts pull requests from people who are not already trusted, then "it is possible for this to expose secrets to PRs": GitHub's cache is readable by PR jobs from the same base branch, so an attacker's PR can restore the cache and read the previous run's environment out of the Miri artifacts. The short-term fix, in the **2026-09-22 nightly**, makes Miri "only preserve `CARGO_*` environment variables (excepting `CARGO_*_TOKEN`) and `OUT_DIR`." If your CI matched the four conditions: disable caching for that job or move secrets out of the Miri step, **clear existing caches, and rotate every secret the job could see.** The WG's broader point applies to every ecosystem: "even if you do not run Miri, ensure jobs that can write to public caches do not have access to secrets."

## What happened

**The mechanism.** Miri interprets a crate's test binaries and, to make `env!`/`std::env` behave, serialises the host environment into its build artifacts under `target/`. Rust projects routinely cache `target/` between Actions runs because Rust builds are slow — `Swatinem/rust-cache` exists for exactly this. GitHub Actions caches are scoped by branch but a workflow run for a pull request can restore caches created on the base branch. So a job on `main` that ran `cargo miri test` with, say, a `CARGO_REGISTRY_TOKEN` or a cloud key in its environment wrote that value into `target/`, the cache action uploaded it, and the next contributor's PR job could restore the same cache and read it — a leak with no exploit beyond opening a pull request. The WG notes the exposure includes contributors "who already had a PR merged," i.e. the usual "first-time contributors need approval" gate does not close it.

**The fix.** The nightly of 2026-09-22 restricts what Miri preserves to `CARGO_*` (minus `CARGO_*_TOKEN`) and `OUT_DIR`. That is a short-term allow-list; the WG says so. Stable Miri users get it with the next release train.

**Who is exposed.** Not every Rust project: you need Miri in CI (common for unsafe-heavy crates and the ecosystem's core libraries), secrets in that step's environment, `target/` caching, and external PRs. Where all four hold, the secrets are typically the ones that matter most — publish tokens and deployment credentials — because they were set at the workflow level rather than scoped to the publish job.

**Why it matters for vibe coders.** The four conditions are the default output of "add CI for my Rust crate" from an assistant: a single workflow with `secrets:` at the top, `Swatinem/rust-cache@v2`, and a Miri step copied from a template. More generally this is the same lesson as the corpus's [Cargo CVE-2026-5223 cluster](2026-05-cargo-symlink-sparse-url-cves.md) and the [`arrayref` compromise](2026-08-arrayref-proc-macro1-crates-io.md): the build tooling and the CI cache are part of the supply chain, and a cache that PRs can read is a public artifact. The Rust WG's disclosure is also the second registry/ecosystem-team security post in a week (after the [maintainer-targeting warning](2026-09-rust-maintainers-fake-interview-video-call-campaign.md)) that no outlet had covered when it was published.

## Am I affected?

- **Affected if:** a workflow runs `cargo miri` **and** secrets are available to that step (workflow- or job-level `env:` with `${{ secrets.* }}`) **and** `target/` is cached **and** pull requests from outside collaborators run that workflow (or a variant that restores the same cache key).
- **Not affected if:** no Miri in CI; or secrets are only exposed in a separate publish job that does not run Miri; or `target/` is not cached; or the repo takes no external PRs.

```bash
# Miri in CI?
grep -rn "cargo miri\|miri" .github/workflows/ 2>/dev/null
# Secrets exposed at workflow/job level (not step-scoped) in the same workflow
grep -rn -B2 -A2 'secrets\.' .github/workflows/*.yml | grep -n "env:" | head
# target/ caching
grep -rn "Swatinem/rust-cache\|actions/cache" .github/workflows/ 2>/dev/null
# Existing caches to purge (needs gh with repo scope)
gh cache list --limit 50
```

## If you are affected

1. **Clear the caches now** (`gh cache delete --all`, or the repository's Actions → Caches page) — a cache written by a pre-fix Miri run holds the secret until it expires.
2. **Rotate every secret the Miri job could read** — registry tokens (`cargo owner`/`CARGO_REGISTRY_TOKEN`), cloud credentials, signing keys → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md); for a crates.io token, revoke it on crates.io and re-issue.
3. Update Miri (`rustup update nightly` / the toolchain file) to ≥ the 2026-09-22 nightly, **and** restructure the workflow so secrets are step-scoped to the jobs that need them — the fix narrows what Miri preserves, it does not make caching secrets-bearing output safe.
4. Check whether any unfamiliar PR restored the cache during the window (the Actions log for a PR run shows `Cache restored from key: …`); if one did and the actor is not a known contributor, treat the secret as used.

## Prevention

- **Jobs that write to caches must not hold secrets.** Split CI into an untrusted job (build, test, Miri, cache) with no secrets and a trusted job (publish, deploy) with no cache restore from PR-reachable keys. [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).
- **Scope secrets to steps, never to the workflow.** A workflow-level `env:` with a token makes every tool in every step a potential leak; Miri happened to be the one that wrote the environment to disk.
- **Treat build output as untrusted for secrets.** Any tool that snapshots its environment (Miri, some coverage and reproducibility tools, debug bundles) will do this again; scan caches and artifacts for secret patterns before uploading them. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources
- [Rust Blog — GitHub Actions leaking secrets when Miri output is cached](https://blog.rust-lang.org/2026/09/21/github-actions-leaking-secrets-when-miri-output-is-cached/) — primary, Rust Security Response Working Group, 2026-09-21: "Miri stores all environment variables to `target/`," the four conditions, the PR-readable cache behaviour, the `CARGO_*` / `OUT_DIR` allow-list fix in the 2026-09-22 nightly, the remediation list, "even if you do not run Miri, ensure jobs that can write to public caches do not have access to secrets." Fetched 2026-09-24.
- [Rust Blog — index](https://blog.rust-lang.org/) — fetched 2026-09-24 to confirm the post's date and that it sits between the 09-17 maintainer-targeting warning and a 09-22 Cargo post; no other vendor or outlet coverage was found (Lobsters and link aggregators only).
- Single-source note: the disclosure is the ecosystem security team's own; per this corpus's practice a registry/ecosystem-team post is the authoritative record for its own tooling, and no independent researcher write-up exists yet.
- Related in this corpus: [Rust maintainers targeted through fake interviews](2026-09-rust-maintainers-fake-interview-video-call-campaign.md), [arrayref / crates.io compromise](2026-08-arrayref-proc-macro1-crates-io.md), [Cargo symlink / sparse-URL CVEs](2026-05-cargo-symlink-sparse-url-cves.md).
