---
id: 2026-05-node-ipc-compromise
title: "node-ipc compromise (3 malicious versions, May 2026)"
date_disclosed: 2026-05-14
last_updated: 2026-05-16
severity: critical
status: active
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code, replit, lovable, bolt]
tags: [supply-chain, credential-theft, npm, transitive-dependency]
---

## TL;DR
Three malicious versions of `node-ipc` (10M+ weekly downloads) were published to npm simultaneously on 2026-05-14, each carrying an identical 80 KB obfuscated credential-stealing payload. `node-ipc` is a transitive dependency in a huge number of build toolchains — you can be affected without ever installing it directly.

## What happened
On 2026-05-14, an attacker published three malicious versions of `node-ipc` within minutes of each other. The payload is an obfuscated ~80 KB JS file that scans the host for credentials and exfiltrates them. The package was previously known for the 2022 "protestware" incident, but the maintainer's account was reportedly compromised this time, not a deliberate act.

Because `node-ipc` is a foundational IPC library, it appears as a transitive dependency in many CLIs, dev tools, and bundlers. A clean `npm install` in a fresh project can pull it in.

## Am I affected?

```bash
# Show every node-ipc version anywhere in your tree (including transitive)
npm ls node-ipc --all
```

If any version published on or after 2026-05-14 appears, treat the machine as compromised until you've verified the version against the official advisory list. As of 2026-05-16 the malicious versions are removed from npm but lockfiles pinning the bad SHAs will still resolve to cached tarballs.

```bash
# Check your lockfile directly
grep -A2 '"node-ipc"' package-lock.json | head -30
grep -B1 -A3 'node-ipc' yarn.lock | head -30
grep -B1 -A3 'node-ipc' pnpm-lock.yaml | head -30
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts`, lockfile pinning, Socket
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run `npm install` inside a container

## Sources
- [The Register — Another npm supply chain worm hits dev environments (2026-04-22)](https://www.theregister.com/2026/04/22/another_npm_supply_chain_attack/)
- [Palo Alto Unit 42 — Monitoring npm Supply Chain Attacks (updated May 1)](https://unit42.paloaltonetworks.com/monitoring-npm-supply-chain-attacks/)
- [StepSecurity — Malicious node-ipc Versions Published to npm](https://www.stepsecurity.io/blog/node-ipc-npm-supply-chain-attack)
