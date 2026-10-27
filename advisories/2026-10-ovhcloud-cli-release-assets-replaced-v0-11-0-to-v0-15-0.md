---
id: 2026-10-ovhcloud-cli-release-assets-replaced-v0-11-0-to-v0-15-0
title: "Compromised OVHcloud CLI release archives v0.11.0 to v0.15.0 (2026-10-19, 94 minutes): reinstall v0.16.0 and rotate cloud, SSH, npm and AI-tool credentials"
kind: malicious-artifact
date_disclosed: 2026-10-19
last_updated: 2026-10-26
severity: high
status: contained
ecosystems: [github-releases, go, cli, cloud-tooling]
tools_affected: ["ovhcloud-cli v0.11.0 through v0.15.0 downloaded or updated between 12:47 and 14:21 UTC on 2026-10-19 (macOS x86_64 and arm64, Linux x86_64 and arm64, Windows x86_64)", "the official install script and the CLI's own upgrade command on macOS and Linux (no hash pin)", "CI jobs that fetch release archives without a pinned hash", "every credential file on the host, including ~/.claude, ~/.hermes, OpenCode databases and the VS Code and Cursor extension stores the vendor lists"]
tags: [supply-chain, malicious-package, compromised-release, github-releases, release-immutability, credential-theft, cloud-cli, ai-tool-credentials, vendor-advisory]
---

## TL;DR
If you downloaded, installed or upgraded `ovhcloud-cli` v0.11.0 through v0.15.0 between 12:47 and 14:21 UTC on 2026-10-19 and ran it, delete the binary and reinstall v0.16.0, the immutable release the vendor published that evening. The vendor says secrets on that machine "should be considered compromised": rotate cloud, container, Kubernetes, Terraform, SSH, Git, npm and AI-tool credentials from a different machine.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub release assets (`ovh/ovhcloud-cli`) | `ovhcloud` archives for Darwin_arm64, Darwin_x86_64, Linux_arm64, Linux_x86_64 and `ovhcloud.exe` Windows_x86_64 | v0.11.0, v0.12.0, v0.13.0, v0.14.0, v0.15.0 as served 2026-10-19 12:47 to 14:21 UTC (the v0.15.0 Darwin archive from 12:47, all v0.15.0 archives from 12:57, all five releases from 13:30) | delete; install v0.16.0 (2026-10-19 17:16 UTC, signed tag, marked immutable) | replaced files deleted 14:21 UTC; v0.16.0 is the only release marked immutable (2026-10-20) | GHSA-862f-55f5-vmvw (vendor, 2026-10-20, High, no CVE) |
| GitHub release assets | the same releases, Linux i386, Windows i386, Windows arm64 and WebAssembly builds | none replaced, per the vendor and the reporter | no action | unchanged | same |
| Homebrew cask, `go install`, source builds, Docker image | `ovhcloud-cli` | none: the cask pinned the original hashes and refused the download, the v0.15.0 tag still points to its original commit, the image's latest tag was not rebuilt | no action | unchanged | same |

Per the vendor advisory: a compromised OVHcloud developer's GitHub account, registered to the organisation, was used to replace the archives and checksum file of already-published releases; the source code, tags, build chain and internal CI/CD were not affected; the root cause named is that "the GitHub repository was not appropriately configured to ensure release immutability," since corrected. The reporter (issue #300, opened 2026-10-19) was a customer whose CI job pins the archive's SHA-256 and failed; they noted the replacement assets were uploaded by a different account than the originals and carried build metadata of a later, uncommitted commit. Public announcement 16:52 UTC; private vulnerability reporting enabled afterwards. The Hacker News attributes a link between the uploading account and the GlassWorm campaign to researchers and calls it an inference, with nothing from the October binary tied to GlassWorm.

## Am I affected?

- Only if you fetched an affected archive inside the window and ran it. Downloads before 12:47 UTC on 2026-10-19, and installs of v0.10.0 or earlier or v0.16.0 or later, are not affected per the vendor.
- The exposure paths The Hacker News lists: the official install script, which downloads the latest archive without a hash check; manual downloads from the five release pages; CI steps fetching release archives without a pinned hash; the CLI's upgrade command on macOS or Linux for installs from v0.12.0 to v0.14.0 that were not made through Homebrew or `go install`.
- The vendor's checks: look in the temp directory for a directory named `envchecker-` followed by random digits, and compare the installed binary's checksum with the values in the advisory's appendix. Do not run the binary to check it.
- Verify a fresh download with `gh release verify-asset v0.16.0 <file>` (per The Hacker News) before trusting it.

## If you are affected

1. Delete the binary and reinstall v0.16.0 or later. Updating does not revoke anything already copied, so rotation comes first and happens from a different machine.
2. Rotate or deactivate, per the vendor's list: AWS (`~/.aws/credentials`, `~/.aws/config`, `~/.aws/cli/cache`); Google Cloud (`~/.config/gcloud/credentials.db`, `access_tokens.db`, `configurations/config_default`); Azure (`~/.azure/azureProfile.json`, `clouds.config`, `config`, `msal_token_cache.json`); Docker and Kubernetes (`~/.docker/config.json`, `~/.dockercfg`, `~/.kube/config`); DigitalOcean, Terraform, `~/.netrc` and `~/.npmrc`; SSH keys and `~/.gitconfig`; AI tools (`~/.claude`, `~/.hermes/sessions`, `~/.hermes/.hermes_history`, the OpenCode databases under `~/.local/share/opencode/` and `~/.config/opencode/`); the VS Code and Cursor `globalStorage/state.vscdb` stores and the Continue and Sourcegraph Cody databases beside them; and OVHcloud API credentials in `~/.ovh.conf` or environment variables. The vendor says any other secret readable from disk should be treated the same way.
3. Follow [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) and [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md) for the order of operations, and [if you ran malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md) for the host.
4. Pin hashes in every CI and build step that fetches release archives, and prefer the Homebrew cask or `go install` paths that already do.

## Prevention

- [CI/CD hardening](../prevention/ci-cd-hardening.md): pin the hash of every downloaded release asset; a pinned job is what caught this one.
- [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md): a release page is mutable unless the repository enables release immutability, and a tag pointing at the right commit says nothing about the archive next to it.
- [Credential hygiene](../prevention/credential-hygiene.md): the vendor's rotation list is the inventory of what a CLI on a developer laptop can read.

## Update 2026-10-26 — StepSecurity's write-up (10-19) adds the account, the window, the on-disk markers and the GlassWorm link

StepSecurity names the GitHub account used (`HassenBF`), confirms the 12:47 to 14:21 UTC window and that v0.16.0 was published clean at 17:16 UTC, and notes that release immutability was not enabled on the repository, which is why assets could be replaced in place. Defender signals it lists: a `/tmp/envchecker-*` file, a `~/init.json` file, a binary whose `ovhcloud version` prints `undefined`, and a build stamped with a commit (`5ead8ef…`) that does not exist in the repository; file hashes for the replaced archives are on the post. The loader fetched its second stage through a blockchain dead-drop in the GlassWorm style, which is the basis for the campaign link. Credits: alink-tothepast, Ivan Kwiatkowski, OpenSourceMalware.

## Sources
- [ovh/ovhcloud-cli — GHSA-862f-55f5-vmvw: ovhcloud-cli security incident - October 19th, 2026](https://github.com/ovh/ovhcloud-cli/security/advisories/GHSA-862f-55f5-vmvw) — fetched 2026-10-20: published 2026-10-20, High, no CVE, the affected assets and versions, patched 0.16.0, the UTC timeline, the affected and not-affected statements, the root-cause and immutability statements, the detection checks and the credential-file list quoted above. Read for artifacts and remediation only.
- [ovh/ovhcloud-cli — issue #300: Release assets of v0.13.0–v0.15.0 replaced on 2026-10-19 with a dirty build of a later commit](https://github.com/ovh/ovhcloud-cli/issues/300) — fetched 2026-10-20: the reporter's observations (checksum mismatch, different uploading account, build metadata), the maintainers' replies ("All binaries involved have been deleted at 16:21 GMT+2", the immutable v0.16.0, the promised post-mortem), closed 2026-10-20.
- [ovh/ovhcloud-cli — releases](https://github.com/ovh/ovhcloud-cli/releases) — fetched 2026-10-20: v0.16.0 marked "Immutable release", the only release so marked; v0.11.0 (2026-04-14) through v0.15.0 (2026-09-16) dates.
- [The Hacker News — Hackers Hijack Five OVHcloud CLI Releases to Distribute Secret-Stealing Malware](https://thehackernews.com/2026/10/hackers-hijack-five-ovhcloud-cli.html) — 2026-10-20: the exposure paths, the Homebrew, `go install` and Docker statements, the OpenSourceMalware timeline attribution, the GlassWorm inference, `gh release verify-asset`, and `~/.ovh.conf`. Read for artifacts and remediation only.
- Not fetched: OpenSourceMalware's write-up (the site index rendered without posts this sweep) and OVHcloud's X announcement (not openable); both are cited through The Hacker News and the vendor advisory.
- Related in this corpus: [GlassWorm](2025-10-glassworm-vscode-worm.md) for the campaign the account was linked to by inference, [Coder registry](2026-09-coder-registry-cloudflare-terraform-supply-chain.md) for a release channel swapped under an unchanged tag.
- **2026-10-26 update source** — [StepSecurity — OVHcloud CLI GitHub release swap (GlassWorm)](https://www.stepsecurity.io/blog/ovhcloud-cli-github-release-swap-glassworm) — fetched 2026-10-26 (2026-10-19): the account, the timeline, immutability status, the markers, hashes, credits.
