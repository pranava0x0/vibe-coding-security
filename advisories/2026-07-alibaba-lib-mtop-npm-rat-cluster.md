---
id: 2026-07-alibaba-lib-mtop-npm-rat-cluster
title: "18 npm packages impersonating internal Alibaba tooling deliver a cross-platform RAT (aone-cli) — single-source, unconfirmed"
date_disclosed: 2026-07-28
last_updated: 2026-07-28
severity: medium
status: unconfirmed
ecosystems: [npm]
tools_affected: ["lib-mtop", "aone-kit", "aone-kit-cli", "aone-sandbox", "local-config-parser", "smart-config-manager", "cloud-config-fetcher", "fast-transform-pipeline", "aone-cloud-cli", "colder-cli", "def-open-client", "feedback-ai-sdk", "flight-compare-analyzer", "lwp-web-client", "lzd-unified-station-sdk", "open-worker-cli", "test-skill-zip", "uniapi-bridge"]
tags: [supply-chain, rat, dependency-confusion-style, dingtalk-c2, single-source]
---

## TL;DR

Socket.dev reported (**2026-07-28**) an 18-package npm cluster that impersonates internal, `@ali`-scoped Alibaba tooling — top-level lure packages copy the names of private Alibaba packages, and a layered dependency chain assembles a downloader that installs a cross-platform RAT called **aone-cli**. The activity was reportedly staged on **2026-04-27/28** but was only publicly disclosed this week. **This is currently single-source** (Socket.dev only — no independent researcher confirmation was found by this sweep), so treat the details below as reported rather than confirmed, per this repo's own accuracy standard.

## What happened

Socket's research team identified the campaign after examining `lib-mtop`, an npm package that had received new versions after years of dormancy ([Socket](https://socket.dev/blog/npm-rat-targets-alibaba)). The same maintainer account published a cluster of packages that copy the names of private, `@ali`-scoped packages internal to Alibaba Group as their declared dependencies — a lure structure similar in spirit to dependency-confusion attacks, though these specific packages were published under public (not scoped) names rather than exploiting private-registry resolution directly. Socket lists 18 packages total: `lib-mtop`, `aone-kit`, `aone-kit-cli`, `aone-sandbox`, `local-config-parser`, `smart-config-manager`, `cloud-config-fetcher`, `fast-transform-pipeline`, `aone-cloud-cli`, `colder-cli`, `def-open-client`, `feedback-ai-sdk`, `flight-compare-analyzer`, `lwp-web-client`, `lzd-unified-station-sdk`, `open-worker-cli`, `test-skill-zip`, and `uniapi-bridge`.

**Payload:** the final-stage RAT, named **aone-cli**, supports command execution, arbitrary file upload/download, host reconnaissance, payload staging, an encrypted reverse TCP proxy, application-specific persistence via code injection, and lateral movement through **DingTalk** (a Chinese enterprise messaging platform popular at Alibaba and its ecosystem partners) — predefined commands include screenshot capture and Python/Node module installation. On Windows, the malware reportedly replaces components of Alibaba's own **Alilang** security application; on Linux/macOS it uses background execution and scheduled-task persistence.

**C2:** primary domain `xemzqli2vu.ai-app.pub`, with a reverse-proxy channel at `diamond-cli-znsxphqell.cn-shanghai.fcapp.run` and payload delivery staged via Alibaba Cloud OSS buckets.

**Attribution:** Socket notes later-stage payload code is heavily commented in Chinese and uses UTC+0800 commit timestamps — but explicitly cautions these signals "can be faked, and shouldn't be taken as a strong evidence of attribution." No threat-actor name is assigned.

**Scale and timeline:** Socket describes the campaign as staged across **2026-04-27/28** (initial test packages, then the full dependency chain) and says it went undetected for roughly three months before this week's disclosure. Download counts are reported as "not significant." Socket characterizes the operation as narrowly targeted rather than broadly distributed — consistent with the specific Alibaba-tooling impersonation angle rather than a mass-typosquat campaign.

**Why this is marked unconfirmed:** this sweep found only one directly-verifiable source (Socket.dev's own writeup). Search results referenced apparent pickup by CyberSecurityNews and GBHackers, but both articles returned empty content on direct fetch and could not be independently verified — per this repo's citation standard, an un-openable secondary mention doesn't count as independent confirmation. If a second source becomes verifiable in a future sweep, this advisory should be updated and promoted out of `unconfirmed`.

## Am I affected?

```bash
# Check whether any of the named packages are anywhere in your dependency tree
for pkg in lib-mtop aone-kit aone-kit-cli aone-sandbox local-config-parser smart-config-manager \
  cloud-config-fetcher fast-transform-pipeline aone-cloud-cli colder-cli def-open-client \
  feedback-ai-sdk flight-compare-analyzer lwp-web-client lzd-unified-station-sdk \
  open-worker-cli test-skill-zip uniapi-bridge; do
  grep -q "\"$pkg\"" package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null && echo "FOUND: $pkg"
done
```

You're at risk only if you or a tool in your organization installed one of the 18 named packages, particularly if searching for internal Alibaba (`@ali`-scoped) tooling by name.

## If you are affected

1. Follow [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) and [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md).
2. Rotate credentials per [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), with particular attention to DingTalk and Alibaba Cloud (OSS) credentials given the lateral-movement targeting.

## Prevention

→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — be wary of packages whose name mimics internal/private tooling at a specific employer, even when the package itself is public.
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)

## Sources

- [Socket — "Distributed npm Package Cluster Delivers Cross-Platform RAT"](https://socket.dev/blog/npm-rat-targets-alibaba) — sole directly-verified source, published 2026-07-28: full package list, payload capabilities, C2 infrastructure, attribution caveats, timeline.
