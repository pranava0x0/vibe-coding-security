---
id: 2026-05-npm-dependency-confusion-recon-campaign
title: "Dependency-confusion recon campaign — 4 waves, 9+ corporate-scope impersonations, escalated to full credential theft (May–Jul 2026)"
date_disclosed: 2026-05-29
last_updated: 2026-07-04
severity: high
status: active
ecosystems: [npm]
tools_affected: [any npm-based project resolving packages from public + internal scopes without registry pinning]
tags: [dependency-confusion, supply-chain, reconnaissance, credential-theft, postinstall, npm]
---

## TL;DR

Microsoft Threat Intelligence disclosed a **dependency-confusion campaign**: a single operator, publishing under three npm aliases (`mr.4nd3r50n`, `ce-rwb`, `t-in-one`), published **33 malicious packages in an initial pair of bursts on May 28, 2026, then a further 12 in a third burst on May 29, 2026 (45 total)** under **9 organizational scopes that mirror real internal corporate namespaces** (e.g. `@cloudplatform-single-spa`, `@data-science`, `@payments-widget`, `@travel-autotests`, `@sber-ecom-core`, `@wb-track`, and three matching the actor aliases). Each package's `postinstall` hook fetches and runs an obfuscated **reconnaissance-only** payload — no destructive or credential-exfiltration action confirmed at the time. **Update (2026-07-04):** SafeDep's independent tracking shows this is one template reused across **at least four waves through July 1, 2026**, and the most recent wave has **escalated from reconnaissance to full credential exfiltration** (SSH keys, cloud credentials, Kubernetes/Docker config). npm has taken down the accounts and packages disclosed so far, but the template is still being reused by new actors/scopes.

## What happened

Dependency confusion occurs when a build system is configured to resolve a package name from the public registry even though an identically-named package is meant to be private/internal — an attacker who registers the public name gets installed instead. Microsoft's Threat Intelligence team found this actor doing exactly that at scale: pre-staging some packages as early as **2026-05-04**, then publishing in three timed bursts:

- **`mr.4nd3r50n`** — 26 packages, version `100.100.100`, 2026-05-28 18:47–18:51 UTC
- **`ce-rwb`** — 7 packages, version `3.5.22`, 2026-05-28 19:02–19:03 UTC
- **`t-in-one`** — 12 packages across three scopes, 2026-05-29 09:01–09:02 UTC

Each malicious package's `postinstall` script fetches an obfuscated payload from an attacker C2 (`oob.moika.tech`) that harvests system information, environment variables, and developer/build context — Microsoft describes it as operating in **"reconnaissance-only mode" by default**, with the C2 architecture capable of pushing further payloads to specific targets later. Microsoft attributes the campaign to **a single operator** across all three aliases based on shared C2 infrastructure, identical endpoints, matching authentication tokens, and matching publishing-toolchain fingerprints — but does **not** name a known threat-actor group.

Per Microsoft: *"Based on our investigation and feedback to the npm team these repos and users were taken down."*

### Update 2026-07-04 — same template, four waves, escalation to credential theft

SafeDep's independent tracking ([SafeDep](https://safedep.io/marketfront-dependency-confusion-campaign/)) found that the README lure text used by Microsoft's May 28–29 disclosure ("Internal package — Platform Engineering Team"-style marker) is a **reused template now confirmed across four separate waves**:

1. **2026-05-27** — `@cloudplatform-single-spa`, `@mlspace`, `@car-loans` (version `99.99.99`)
2. **2026-05-29** — `@t-in-one`, `@capibar.chat`, `@sber-ecore-core` (the wave Microsoft's disclosure covers)
3. **2026-06-01** — `@emcd-vue` scope
4. **2026-07-01** — **`@marketfront`** (25 packages, all version `7.0.0`, published in a single burst at ~22:59:33 UTC) and **`@tqm-mfe`** scopes

The `@marketfront` wave impersonates an e-commerce internal registry with package names like `@marketfront/header`, `@marketfront/footer`, `@marketfront/navbar`, `@marketfront/bannerpopup`, and `@marketfront/designsystemdevtool`, plus the same fictional-internal-registry lure (`npm.marketfront.io`, `jira.marketfront.io`, `docs.marketfront.io`) referencing "telemetry collection."

**This wave is a material escalation, not a repeat.** Where Microsoft characterized the May wave as reconnaissance-only, the `@marketfront` wave's `postinstall` runs a ~160KB obfuscated script that **actively harvests and exfiltrates** roughly 20 credential file types — SSH keys, AWS credentials, Kubernetes config, Docker config, npm/git credentials, `.env` files, and shell history — compresses the haul with gzip, and exfiltrates it via HTTPS POST with a custom `X-Secret` header to a `/api/v1/events` endpoint, with the C2 host itself obscured via RC4+XOR encryption. This confirms the prior sweep's triage note that a reconnaissance-only first-stage payload is often a precursor to a larger campaign — here, the same actor/template graduated to full credential theft within about five weeks.

## Am I affected?

```bash
# Check whether any of the actor-linked scopes were ever installed
npm ls --all 2>/dev/null | grep -E '@cloudplatform-single-spa|@wb-track|@data-science|@ce-rwb|@payments-widget|@travel-autotests|@t-in-one|@capibar\.chat|@sber-ecom-core|@mlspace|@car-loans|@sber-ecore-core|@emcd-vue|@marketfront|@tqm-mfe'

# Audit for any postinstall reaching oob.moika.tech (May wave) or making requests
# with an X-Secret header to a /api/v1/events path (July @marketfront wave)
grep -r "oob.moika.tech" node_modules/*/package.json 2>/dev/null
grep -rl "X-Secret" node_modules/*/package.json node_modules/*/*.js 2>/dev/null
```

You're at risk if your build pulls packages from any of the scopes above from the **public** npm registry rather than an internal/private registry, or if you (coincidentally) use one of these scope names for your own internal packages without registry-scoping enforcement. Given the template is being reused with new scope names roughly every 3–5 weeks, treat *any* npm scope with a README claiming "Internal package — Platform Engineering Team"-style ownership as suspect, not just the specific scopes listed here.

## If you are affected

1. Remove any installed package from the listed scopes and purge lockfile entries.
2. For the May wave (recon-only): treat any host that ran `npm install` against these packages as having had system/environment information disclosed — rotate CI secrets and developer credentials as a precaution, per [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
3. For the July `@marketfront`/`@tqm-mfe` wave (active credential exfiltration): treat the host as fully compromised — rotate SSH keys, AWS/cloud credentials, Kubernetes/Docker config, npm/git tokens, and anything in `.env` files immediately, per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Check outbound network logs for connections to `oob.moika.tech`, and for POST requests carrying an `X-Secret` header to any `/api/v1/events` path.
5. Configure npm/Yarn/pnpm to always resolve your internal scope names from your private registry, never falling back to the public registry (`.npmrc` scope-to-registry mapping).

## Prevention

- **Register your internal package scope names on the public npm registry too** (even as empty placeholder packages), or configure explicit scope-to-registry mapping in `.npmrc` so internal scopes can never resolve publicly.
- Use `npm config set install-links true` equivalents / lockfile registry pinning to prevent silent registry substitution.
- See [prevention/npm-hardening.md](../prevention/npm-hardening.md) and [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) for dependency-confusion-specific hardening steps.

## Sources

- [Microsoft Security Blog — "Malicious npm packages abuse dependency confusion to profile developer environments"](https://www.microsoft.com/en-us/security/blog/2026/05/29/33-malicious-npm-packages-abuse-dependency-confusion-profile-developer-environments/) — primary vendor disclosure: package counts, scopes, aliases, timeline, payload behavior, attribution assessment, takedown confirmation.
- [SafeDep — "@marketfront: 25 npm Packages Reuse a Known Lure"](https://safedep.io/marketfront-dependency-confusion-campaign/) — fourth-wave discovery, cross-wave timeline (May 27 → Jul 1), escalation from recon-only to full credential exfiltration, IOC detail (`X-Secret` header, RC4+XOR C2 obfuscation).
