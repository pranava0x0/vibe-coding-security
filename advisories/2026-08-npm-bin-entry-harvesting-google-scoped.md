---
id: 2026-08-npm-bin-entry-harvesting-google-scoped
title: "npm 'bin entry harvesting' — 21 packages squat unscoped binary names exposed by Google-scoped npm packages (unconfirmed, single-source)"
date_disclosed: 2026-08-14
last_updated: 2026-09-15
severity: medium
status: unconfirmed
ecosystems: [npm]
tools_affected: ["any project depending on Google-scoped npm packages with bin entries (e.g. @angular/*, @google-cloud/*)"]
tags: [dependency-confusion, bin-script-confusion, reconnaissance, npm, unscoped-package-squatting]
---

## TL;DR
SafeDep's research team reported that on **2026-08-12**, an actor published **21 unscoped npm packages** (`bazelisk`, `gaarf`, `ngsw-config`, `upload-to-gcp`, and 17 others) that squat the **unscoped binary names** exposed by legitimate Google-scoped packages' `bin` entries — a structural gap that standard dependency-confusion defenses (scoped publishing, registry allowlists, lockfile pinning) don't cover, because a scoped package's `bin` entry cannot itself carry the scope prefix. Each package's postinstall hook sent a minimal system-fingerprint beacon (hostname, platform, CPU arch, Node version) to a per-package C2 subdomain; all 21 were unpublished within roughly 32 seconds of each other about 3.5 hours after the first wave went live. **This finding is currently single-sourced** (SafeDep only, no independent corroboration found as of this sweep) — treat as unconfirmed pending a second source, per this repo's accuracy bar.

## What happened
Per SafeDep's writeup, a scoped package like `@google-cloud/some-tool` can declare a `bin` entry (e.g. `bazelisk`) that generates an **unscoped** executable name on `$PATH` once installed — because npm's `bin` field cannot itself carry the `@scope/` prefix. An attacker who registers that same unscoped name as a standalone public package can get resolved instead of the intended scoped tool in certain dependency-resolution or global-install scenarios, since none of the usual dependency-confusion mitigations (which protect the *package* name, not the *binary* name it exposes) apply to this specific gap.

The campaign published 21 such packages in two waves on **2026-08-12** (13:23 UTC: `gaarf`, `upload-to-gcp` at v3.2.1; 16:57–16:59 UTC: the remaining 19 at v1.0.0), all squatting binary names associated with Google-affiliated tooling: `bazelisk`, `broadcast-graphics-mcp`, `chrome-enterprise-premium-mcp`, `chromecast-webdriver-cli`, `chromeos-webdriver-cli`, `code-assist-mcp`, `gaarf`, `gaarf-bq`, `gaarf-node`, `gaarf-node-bq`, `gemini-cli-a2a-server`, `github-policy-bot`, `karma-proxy`, `localize-extract`, `localize-translate`, `ngsw-config`, `tfjs-inference`, `tizen-webdriver-cli`, `upload-to-gcp`, `wct-st`, `xbox-one-webdriver-cli`. All 21 were unpublished by the same npm account within a 32-second window at 17:22 UTC the same day. The postinstall payload was reconnaissance-only — a system fingerprint POST to a package-specific subdomain — not a credential stealer, consistent with this repo's existing "reconnaissance-only payload as first-stage precursor" triage pattern (see the [npm dependency confusion recon campaign](2026-05-npm-dependency-confusion-recon-campaign.md)).

**IOCs (per SafeDep, unverified independently):** npm publisher `rootdaddy-msrc` (`ayyitscompton@gmail.com`, author field `r00tdaddy`); C2 pattern `*.instances.poc.jchunt[.]top`; apex domain `jchunt[.]top` (Cloudflare-hosted); C2 IP `152.53.138.110`.

## Am I affected?
```bash
npm ls bazelisk gaarf ngsw-config upload-to-gcp 2>/dev/null
grep -RE '"(bazelisk|gaarf|gaarf-bq|gaarf-node|gaarf-node-bq|ngsw-config|upload-to-gcp|localize-extract|localize-translate|karma-proxy|code-assist-mcp|gemini-cli-a2a-server)"' package.json package-lock.json 2>/dev/null
```
All 21 packages were removed from the registry within hours of publication, so a fresh `npm install` today should not resolve them — but check your lockfile history / CI cache for any install that happened during the ~4-hour window on 2026-08-12 (UTC 13:23–17:22).

## If you are affected
1. If any of the 21 names appear in your lockfile or `node_modules` history, treat the host as having sent a reconnaissance beacon; check outbound connections to `jchunt.top` or its subdomains in your logs.
2. This was reconnaissance-only (no credential theft observed) — no credential rotation is indicated on current evidence, but monitor for a follow-on wave from the same actor given this repo's established pattern of recon-only payloads preceding a larger campaign.
3. See [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) for general unscoped-package vetting practices.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ If you depend on a scoped package that exposes a `bin` entry, consider pinning or vendoring the resolved binary rather than relying on `$PATH` resolution of its unscoped name in CI.

## Update — 2026-09-15: a second, separately reported Google-namespace dependency-confusion cluster (Centriole) — four unscoped packages that sat on npm for 129 days

Centriole (2026-08-31) reported a different set of packages, worth logging beside the SafeDep finding because it targets the same namespace with the classic technique rather than the bin-entry variant: four **unscoped** names styled as Google Cloud internal tooling — `google-internal-cloud-audit-security-check` (versions `99.9.1777210552` and `99.9.1777210553`), `google-cloud-mono-repo-helper` (`1.0.1777211772`), `google-cloud-internal-build-helper` (`1.2.45`) and `google-cloud-internal-core-utils` (`1.2.50`) — all published within 29 minutes on **2026-04-26** (13:36–14:05 UTC). The three version strategies are textbook dependency confusion: a `99.9.x` "beat any internal version," an epoch-stamped patch field, and plausible `1.2.x` numbers for a specific target. Centriole states the payload is undisclosed and quotes npm's standard "should be considered fully compromised" notice; no IOCs are published. **npm replaced all four with `0.0.1-security` placeholders on 2026-09-03** — confirmed directly against the registry for this update (`npm view <pkg> time` shows the April publish times and the 2026-09-03T02:45Z placeholder) — **129 days after publication**. The GitHub Advisory Database had no malware advisory for any of the four names as of 2026-09-15. Different researcher, different packages and no shared IOCs with the SafeDep cluster above; it is recorded here as a second data point on the namespace, not as the same campaign. Still single-source on what the packages *did*; the registry action confirms only that npm judged them malicious.

## Sources
- [SafeDep — npm Bin Entry Harvesting: A Dependency Confusion Blind Spot](https://safedep.io/google-dep-confusion-bin-harvesting/) — sole source found this sweep: full package list, publish/unpublish timeline, IOCs, technical mechanism. No independent corroboration found — treat as unconfirmed.

**2026-09-15 update sources:**
- [Centriole — 129 Days on Public npm: google-cloud-internal Packages Built for Dependency Confusion](https://blog.centriole.io/google-cloud-internal-dependency-confusion) — fetched 2026-09-15; published 2026-08-31: package names, versions, publish timestamps, the three version strategies, the 2026-09-03 takedown.
- npm registry (`npm view google-cloud-internal-core-utils time` and the other three names, run 2026-09-15) — the 2026-04-26 publish times and the 2026-09-03T02:45Z `0.0.1-security` placeholders.
- [GitHub Advisory Database — search for the package names](https://github.com/advisories?query=google-internal-cloud-audit-security-check) — fetched 2026-09-15; no malware advisory for any of the four.
