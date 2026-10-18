---
id: 2026-10-npm-dependency-confusion-native-addon-beacon-cluster-galicia-kmf-cloudflare-module-ci-token-theft
title: "Five npm dependency-confusion lures with prebuilt native-addon beacons, one escalating to CI token theft; uploaded 2026-10-09, all unpublished"
date_disclosed: 2026-10-09
last_updated: 2026-10-18
severity: medium
status: contained
ecosystems: [npm, ci-cd]
tools_affected: ["any npm project whose .npmrc lets an internal or plausible-internal name fall through to the public registry", "CI runners and build images that installed @galicia-toolkit-nestjs/paas 999.0.3 through 999.0.6, kmf-bootstrap 100.100.100 through 100.100.106, kmf-vendor-pack 99.0.0 through 100.100.106, ksp-app 100.100.100 or 100.100.101 (the second from the registry timeline only), or cloudflare_module 0.1.0 (registry only), 1.0.0, 1.0.1, 3.0.0 or 99.0.1", "bundlers that resolved an internal cloudflare_module name from the public registry (import-time beacon)"]
tags: [dependency-confusion, supply-chain, npm, native-addon, preinstall, postinstall, import-time, reconnaissance, credential-theft, ci-cd, osv-mal, contained]
---

## TL;DR

On 2026-10-09, between 15:48 and 22:59 UTC, five package names shaped like internal dependencies appeared on the public npm registry at versions chosen to win resolution over any private copy (999.0.x, 100.100.x, 99.0.x): `@galicia-toolkit-nestjs/paas`, `kmf-bootstrap`, `kmf-vendor-pack`, `ksp-app` and `cloudflare_module`. Four ran at install time through a `preinstall` or `postinstall` hook that loaded a prebuilt native addon shipped in the tarball (`prebuilds/linux-x64/*.node`, with a Windows build in the scoped package), so there was no JavaScript payload to read and no `binding.gyp` to build. The addon forked a detached process that collected the hostname, username, working directory, OS and Node versions, the package name and the configured npm registry URL, and sent them to attacker infrastructure over HTTP, a raw socket or DNS lookups. The later versions of `@galicia-toolkit-nestjs/paas` went further and read the full values of CI and cloud secrets from environment variables, among them `NPM_TOKEN`, `NODE_AUTH_TOKEN` and `GITHUB_TOKEN`. `cloudflare_module` fired its beacon at install time and again whenever anything `require()`d it. None of the five spreads on its own. The registry's `time` field shows the `kmf-*` and `ksp-app` names unpublished at 22:12 UTC on 2026-10-09, within seven hours of the first upload, and the scoped package is gone entirely. OSV holds a malicious-package record for each, published 2026-10-09 to 2026-10-11 (MAL-2026-17723, MAL-2026-17744, MAL-2026-17746, MAL-2026-17768, MAL-2026-17770), sourced from Amazon Inspector with SafeDep, OpenSSF Package Analysis and InvisiRisk corroborating some; Corgea's write-up of 2026-10-12 is the one narrative source.

The trigger condition for a compromised host is specific: a machine ran `npm install` (or `npm ci`) on a project where one of these names resolved from the public registry at one of the listed versions, the registry-only ones included, with lifecycle scripts enabled, or executed code that imported `cloudflare_module`. A lockfile entry is the evidence; a live-registry check that comes back empty proves nothing, because the packages are already gone.

## What happened

Dependency confusion is the technique this corpus wrote up in May: the attacker registers on the public registry the name your build expects to come from a private one, at a version higher than yours, and waits for a client whose configuration lets the name fall through. The May campaign (45 packages across nine corporate scopes, Microsoft Threat Intelligence) used a `postinstall` script that fetched an obfuscated payload. This cluster swaps the fetched script for a compiled N-API addon inside the tarball, the same loader shape SafeDep described for MALFEX on 2026-10-13, and the May campaign's `100.100.100` version number reappears on three of the five names. That is a resemblance, not an attribution; no source attributes this cluster to anyone.

What the registry recorded, from the `time` field read on 2026-10-18 (all UTC, 2026-10-09 unless stated):

| Package | Versions seen by OSV | Published | Removed | Trigger | What it read and where it went |
|---|---|---|---|---|---|
| `kmf-vendor-pack` | 99.0.0, 100.100.100, 100.100.101, 100.100.106 | 15:48 to 21:25 | 22:12 | `postinstall: node postinstall.js`, which loads `prebuilds/linux-x64/addon.node` | the addon's module-init routine forks, opens a socket to a fixed address and posts hostname, package name, user and registry URL |
| `kmf-bootstrap` | 100.100.100 through 100.100.106 | 18:43 to 21:25 | 22:12 | `postinstall`, same addon shape | DNS lookups carrying the hostname and package name to an interaction-service domain, plus the addon's socket post |
| `ksp-app` | 100.100.100 (OSV); registry also shows 100.100.101 | 18:44 and 18:49 | 22:12 | `postinstall`, addon only; `index.js` exports an empty object, no C source, no `binding.gyp` | `HOSTNAME`, `npm_package_name`, `npm_config_registry`, posted |
| `cloudflare_module` | 1.0.0, 1.0.1, 3.0.0, 99.0.1 (OSV); registry also shows 0.1.0 | 22:57 to 22:59 | by 2026-10-10 00:24 | `postinstall: node beacon.cjs`, and `index.js` calls the beacon at load, so any `require()` fires it too | hostname, install path, working directory and Node version posted as JSON over plain HTTP; the default export is a Proxy that returns a no-op for every property, so a bundler that resolved the name keeps building |
| `@galicia-toolkit-nestjs/paas` | 999.0.3 through 999.0.6 | 2026-10-09 (OSV); the registry returns 404 | removed | early versions: DNS beacon of the hostname; later versions: `preinstall` runs `node index.js`, which loads `prebuilds/<platform>-<arch>/metrics.node` (Linux and Windows) | hostname, username, OS and architecture, working directory, and the full values of CI and cloud secrets from the environment: `NPM_TOKEN`, `NODE_AUTH_TOKEN`, `GITHUB_TOKEN`, the GitHub Actions runtime token variables and others listed in the OSV record |

OSV names the publishing account for the scoped package and the namespaces it targeted (`@galicia-toolkit-*`, `@brick-v2`). The `kmf-*`, `ksp-app` and `cloudflare_*` names have no public owner to impersonate; they are plausible-internal names that win if a client's registry configuration lets them.

Why the native addon matters for review: `npm audit`, lockfile diffs and a reviewer reading `index.js` all see a one-line `require()` of a `.node` file. The behaviour is in a compiled ELF or PE binary, which registry scanners that read JavaScript do not parse. Corgea's page and the OSV records both describe this as the reason the packages were worth cataloguing beyond their modest reach.

## Am I affected?

The condition is a resolved install of one of the five names at a listed version, or an import of `cloudflare_module`. Check what your lockfiles and caches say, not the live registry:

```bash
# lockfiles and manifests, every checkout and CI cache you have
grep -rE '(@galicia-toolkit-nestjs/paas|kmf-bootstrap|kmf-vendor-pack|ksp-app|cloudflare_module)' --include=package-lock.json --include=yarn.lock --include=pnpm-lock.yaml --include=package.json . 2>/dev/null

# the npm cache index on a workstation or runner image
grep -rlE 'galicia-toolkit-nestjs|kmf-bootstrap|kmf-vendor-pack|ksp-app|cloudflare_module' ~/.npm/_cacache/index-v5 2>/dev/null | head

# internal registry or proxy logs: any of the five names served from upstream between 2026-10-09 15:00 UTC and 2026-10-11
```

- A hit on `@galicia-toolkit-nestjs/paas` at any of 999.0.3 through 999.0.6 on a runner with CI secrets in the environment is token theft until shown otherwise. The OSV record splits the behaviour into early versions (DNS beacon) and later versions (the addon reading secrets) without naming the boundary version, so treat every token the runner held as taken.
- A hit on any other name is a beacon that told the attacker your hostname, user, working directory and internal registry URL, which is the information needed to choose the next name. Expect follow-up lures against the namespaces your registry URL implies.
- `npm` debug logs do not record which lifecycle scripts ran. A hit on a machine where scripts were enabled is an unprovable install, which this corpus classes as unknown and treats as compromised.
- `--ignore-scripts` blocks the `postinstall` and `preinstall` paths on all five names. It does not block the second path on `cloudflare_module`, the beacon that fires when the module is imported.

## If you are affected

1. Isolate the workstation, runner or build image. Rebuild from a known-good image rather than cleaning, because the addon ran as a detached process and the OSV records describe no persistence to look for.
2. Rotate everything the host's environment held: npm tokens, `NODE_AUTH_TOKEN`, GitHub tokens, cloud and Azure DevOps credentials, internal-registry credentials. [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md), [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Search internal registry and proxy logs for other names that resolved from the public registry in the same window; the beacon's registry-URL field exists to find them.
4. Pin every internal scope to the private registry in `.npmrc`, and configure the proxy so an unknown name under an internal prefix fails rather than falls through. [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) for the install-side steps.

## Prevention

→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — scope pinning in `.npmrc` is the whole defence against dependency confusion; `--ignore-scripts` is a second layer that one of the five bypassed.
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — a runner that exposes `GITHUB_TOKEN` and cloud credentials to `npm install` loses them to any package that runs at install time; install in a step with no secrets.
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — a prebuilt `.node` file in a package that is not a known native addon, with no C source and no `binding.gyp`, is a loader; the three-line JavaScript around it is not the package.

## Sources

- [Corgea Research — October 2026 npm dependency-confusion native-addon cluster](https://corgea.com/research/october-2026-npm-dependency-confusion-native-addon-cluster) — fetched 2026-10-18; dated 2026-10-12, no author named: the five names and versions, the two-stage read-out, the native-addon loader, the removal note, the response list. The one narrative source.
- [OSV — MAL-2026-17723 (@galicia-toolkit-nestjs/paas)](https://osv.dev/vulnerability/MAL-2026-17723) — fetched 2026-10-18; published 2026-10-09, modified 2026-10-12; credits Amazon Inspector and SafeDep: the publishing account, the targeted namespaces, the DNS beacon in early versions, the `preinstall` and `metrics.node` loader in later ones, the environment-variable list.
- [OSV — MAL-2026-17744 (kmf-vendor-pack)](https://osv.dev/vulnerability/MAL-2026-17744) — fetched 2026-10-18; published 2026-10-09; credits Amazon Inspector, InvisiRisk and OpenSSF Package Analysis: the addon's module-init fork and socket post.
- [OSV — MAL-2026-17746 (kmf-bootstrap)](https://osv.dev/vulnerability/MAL-2026-17746) — fetched 2026-10-18; published 2026-10-09, modified 2026-10-11; credits Amazon Inspector and OpenSSF Package Analysis: the DNS beacon and the addon.
- [OSV — MAL-2026-17768 (cloudflare_module)](https://osv.dev/vulnerability/MAL-2026-17768) — fetched 2026-10-18; published 2026-10-11; credit Amazon Inspector: the `postinstall` beacon, the import-time call, the no-op Proxy export.
- [OSV — MAL-2026-17770 (ksp-app)](https://osv.dev/vulnerability/MAL-2026-17770) — fetched 2026-10-18; published 2026-10-11; credit Amazon Inspector: addon-only payload, empty `index.js`, no build tooling.
- npm registry `time` fields for `kmf-bootstrap`, `kmf-vendor-pack`, `ksp-app` and `cloudflare_module` (`registry.npmjs.org/<name>`), read 2026-10-18: upload times 2026-10-09 15:48 to 22:59 UTC, `unpublished` at 22:12 for the three `kmf`/`ksp` names, `cloudflare_module` last modified 2026-10-10 00:24; `registry.npmjs.org/@galicia-toolkit-nestjs%2Fpaas` returns "Not found".
- Related here: [advisories/2026-05-npm-dependency-confusion-recon-campaign.md](2026-05-npm-dependency-confusion-recon-campaign.md) for the May campaign this cluster resembles, and [advisories/2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader.md](2026-10-malfex-npm-windows-rat-stealer-campaign-native-addon-loader.md) for the native-addon loader described five days earlier.
