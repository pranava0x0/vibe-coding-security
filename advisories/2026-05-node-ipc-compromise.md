---
id: 2026-05-node-ipc-compromise
title: "node-ipc compromise (3 malicious versions, May 2026)"
date_disclosed: 2026-05-14
last_updated: 2026-05-18
severity: critical
status: active
ecosystems: [npm]
tools_affected: [any-node-project, cursor, claude-code, replit, lovable, bolt]
tags: [supply-chain, credential-theft, npm, transitive-dependency, dns-exfiltration]
---

## TL;DR
Three malicious versions of `node-ipc` (~822K weekly downloads) were published to npm on 2026-05-14: **`9.1.6`, `9.2.3`, and `12.0.1`**, each carrying an identical ~80 KB obfuscated payload that exfiltrates 90+ categories of credentials. `node-ipc` is a transitive dependency in countless build toolchains — you can be affected without ever installing it directly.

## What happened
Three malicious versions were published within minutes of each other. The malware lives only in `node-ipc.cjs`, appended as an IIFE after the legitimate `module.exports` — making it easy to miss in a casual diff.

Payload behavior:
- Harvests **AWS, Azure, GCP credentials, SSH keys, Kubernetes tokens, GitHub CLI configs, Claude AI / Kiro IDE settings, Terraform state, DB passwords, shell history** (90+ categories).
- Exfiltrates over **DNS (UDP/53)** to an attacker-controlled server — a covert channel that bypasses many egress-allowlist setups.
- Uses temporary directories matching `$TMPDIR/nt-*`.
- Child processes set env flag `__ntw=1`.

## Am I affected?

```bash
# Show every node-ipc version anywhere in your tree
npm ls node-ipc --all

# Specifically check for the three bad versions
npm ls node-ipc --all | grep -E '9\.1\.6|9\.2\.3|12\.0\.1'
```

### IOCs

| Type | Value |
|---|---|
| Malicious versions | `node-ipc@9.1.6`, `node-ipc@9.2.3`, `node-ipc@12.0.1` |
| npm shasum (12.0.1) | `fe5d107b9d285327af579259a32977c4f475fa26` |
| C2 domain | `sh.azurestaticprovider[.]net` |
| C2 IP | `37.16.75[.]69` |
| Exfil channel | DNS UDP/53 |
| Temp dir pattern | `$TMPDIR/nt-*` |
| Process env flag | `__ntw=1` |
| Forensic marker | Every file in malicious tarball timestamped `1985-10-26` |
| Publisher account | `atiertant` (a.tiertant@atlantis-software[.]net) — not a prior maintainer |

```bash
# Lockfile spot-check
grep -E '"node-ipc".*"(9\.1\.6|9\.2\.3|12\.0\.1)"' package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Tarball forensic marker
find ~/.npm ~/.cache -name "node-ipc-*.tgz" -exec sh -c 'tar -tvf "$1" 2>/dev/null | grep "1985"' _ {} \;

# Egress / process artifacts
ps eww | grep "__ntw=1"
ls -la "${TMPDIR:-/tmp}"/nt-* 2>/dev/null
```

If any malicious version was on a dev machine or CI runner, treat the host as compromised.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts`, lockfile pinning, Socket
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — run `npm install` inside a container

## Sources
- [Socket — Popular node-ipc npm Package Infected with Credential Stealer](https://socket.dev/blog/node-ipc-package-compromised)
- [StepSecurity — Malicious node-ipc Versions Published to npm](https://www.stepsecurity.io/blog/node-ipc-npm-supply-chain-attack)
- [Snyk — Malicious node-ipc Versions Published to npm](https://snyk.io/blog/malicious-node-ipc-versions-published-npm/)
- [The Hacker News — Stealer Backdoor Found in 3 Node-IPC Versions](https://thehackernews.com/2026/05/stealer-backdoor-found-in-3-node-ipc.html)
- [SafeDep — Compromised node-ipc on npm: Credential Stealer via DNS Exfiltration](https://safedep.io/malicious-node-ipc-npm-compromise/)
- [Cybersecurity News — node-ipc npm Package with 822K Weekly Downloads Compromised](https://cybersecuritynews.com/node-ipc-npm-package-compromised/)
- [Upwind — Malicious node-ipc npm Package Targets Developer Credentials](https://www.upwind.io/feed/malicious-node-ipc-npm-package-credential-theft)
- [The Register — Another npm supply chain worm hits dev environments](https://www.theregister.com/2026/04/22/another_npm_supply_chain_attack/)
- [Datadog Security Labs — Backdoored node-ipc npm releases steal developer credentials through DNS queries](https://securitylabs.datadoghq.com/articles/node-ipc-npm-malware-analysis/)
- [StepSecurity X post — BREAKING: node-ipc compromised. Again.](https://x.com/step_security/status/2054965387041874223)
