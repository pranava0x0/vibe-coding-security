---
id: 2026-05-npm-dependency-confusion-recon-campaign
title: "Dependency-confusion recon campaign — 33+12 malicious npm packages profile developer environments across 9 corporate scopes (May 2026)"
date_disclosed: 2026-05-29
last_updated: 2026-07-01
severity: medium
status: contained
ecosystems: [npm]
tools_affected: [any npm-based project resolving packages from public + internal scopes without registry pinning]
tags: [dependency-confusion, supply-chain, reconnaissance, postinstall, npm]
---

## TL;DR

Microsoft Threat Intelligence disclosed a **dependency-confusion campaign**: a single operator, publishing under three npm aliases (`mr.4nd3r50n`, `ce-rwb`, `t-in-one`), published **33 malicious packages in an initial pair of bursts on May 28, 2026, then a further 12 in a third burst on May 29, 2026 (45 total)** under **9 organizational scopes that mirror real internal corporate namespaces** (e.g. `@cloudplatform-single-spa`, `@data-science`, `@payments-widget`, `@travel-autotests`, `@sber-ecom-core`, `@wb-track`, and three matching the actor aliases). Each package's `postinstall` hook fetches and runs an obfuscated **reconnaissance-only** payload — no destructive or credential-exfiltration action confirmed yet, but the architecture supports escalation. npm has taken down the accounts and packages.

## What happened

Dependency confusion occurs when a build system is configured to resolve a package name from the public registry even though an identically-named package is meant to be private/internal — an attacker who registers the public name gets installed instead. Microsoft's Threat Intelligence team found this actor doing exactly that at scale: pre-staging some packages as early as **2026-05-04**, then publishing in three timed bursts:

- **`mr.4nd3r50n`** — 26 packages, version `100.100.100`, 2026-05-28 18:47–18:51 UTC
- **`ce-rwb`** — 7 packages, version `3.5.22`, 2026-05-28 19:02–19:03 UTC
- **`t-in-one`** — 12 packages across three scopes, 2026-05-29 09:01–09:02 UTC

Each malicious package's `postinstall` script fetches an obfuscated payload from an attacker C2 (`oob.moika.tech`) that harvests system information, environment variables, and developer/build context — Microsoft describes it as operating in **"reconnaissance-only mode" by default**, with the C2 architecture capable of pushing further payloads to specific targets later. Microsoft attributes the campaign to **a single operator** across all three aliases based on shared C2 infrastructure, identical endpoints, matching authentication tokens, and matching publishing-toolchain fingerprints — but does **not** name a known threat-actor group.

Per Microsoft: *"Based on our investigation and feedback to the npm team these repos and users were taken down."*

## Am I affected?

```bash
# Check whether any of the actor-linked scopes were ever installed
npm ls --all 2>/dev/null | grep -E '@cloudplatform-single-spa|@wb-track|@data-science|@ce-rwb|@payments-widget|@travel-autotests|@t-in-one|@capibar\.chat|@sber-ecom-core'

# Audit for any postinstall reaching oob.moika.tech
grep -r "oob.moika.tech" node_modules/*/package.json 2>/dev/null
```

You're at risk if your build pulls packages from any of the nine scopes above from the **public** npm registry rather than an internal/private registry, or if you (coincidentally) use one of these scope names for your own internal packages without registry-scoping enforcement.

## If you are affected

1. Remove any installed package from the listed scopes and purge lockfile entries.
2. Treat any host that ran `npm install` against these packages as having had system/environment information disclosed — rotate CI secrets and developer credentials as a precaution, per [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
3. Check outbound network logs for connections to `oob.moika.tech`.
4. Configure npm/Yarn/pnpm to always resolve your internal scope names from your private registry, never falling back to the public registry (`.npmrc` scope-to-registry mapping).

## Prevention

- **Register your internal package scope names on the public npm registry too** (even as empty placeholder packages), or configure explicit scope-to-registry mapping in `.npmrc` so internal scopes can never resolve publicly.
- Use `npm config set install-links true` equivalents / lockfile registry pinning to prevent silent registry substitution.
- See [prevention/npm-hardening.md](../prevention/npm-hardening.md) and [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) for dependency-confusion-specific hardening steps.

## Sources

- [Microsoft Security Blog — "Malicious npm packages abuse dependency confusion to profile developer environments"](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) — primary vendor disclosure: package counts, scopes, aliases, timeline, payload behavior, attribution assessment, takedown confirmation.
