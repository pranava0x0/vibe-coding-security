---
id: 2026-05-tanstack-mini-shai-hulud
title: "TanStack Mini Shai-Hulud (May 2026)"
date_disclosed: 2026-05-11
last_updated: 2026-05-16
severity: critical
status: active
ecosystems: [npm]
tools_affected: [any-react-project, cursor, claude-code, lovable, bolt, v0]
tags: [supply-chain, worm, ci-cd, github-actions, oidc, credential-theft]
---

## TL;DR
On 2026-05-11 the Mini Shai-Hulud worm compromised 84 npm package artifacts across 42 `@tanstack/*` packages — including `@tanstack/react-router` (12.7M weekly downloads) — via a chained GitHub Actions "Pwn Request" + cache poisoning + OIDC token abuse attack. If you `npm install`ed a TanStack package on or after May 11, assume credential exfiltration.

## What happened
Attackers exploited a vulnerable `pull_request_target` GitHub Actions workflow in the TanStack monorepo (a classic "Pwn Request") to inject code into a cached build artifact. That cache was then consumed by a trusted publishing workflow holding npm OIDC tokens, which republished the trojanized artifacts with valid signatures.

This is a refinement of the original Shai-Hulud playbook: instead of phishing a maintainer, the attacker compromised the *build pipeline* and let trusted CI sign the malware.

Affected packages (partial): `@tanstack/react-router`, `@tanstack/router`, `@tanstack/query`, `@tanstack/table`, `@tanstack/virtual`, plus framework-specific siblings. Full list in the Wiz/Snyk writeups below.

## Am I affected?

```bash
# List every @tanstack/* package in your tree
npm ls --all 2>/dev/null | grep -E '@tanstack/'

# Check install dates
ls -la node_modules/@tanstack/*/package.json | head
```

If any TanStack package was installed or upgraded between 2026-05-11 and the takedown, treat the dev machine and any CI runner that ran `npm install` as compromised.

```bash
# CI / cloud blast radius — check for outbound connections from build runners
# Look for unexpected GH repos, public gists, suspicious commits to your own repos
gh repo list YOUR_USER --limit 100 --json name,createdAt --jq '.[] | select(.createdAt > "2026-05-10")'
```

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — especially for CI runners
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)

## Sources
- [Snyk — TanStack npm Packages Hit by Mini Shai-Hulud](https://snyk.io/blog/tanstack-npm-packages-compromised/)
- [Wiz — Mini Shai-Hulud Strikes Again: TanStack + more npm Packages Compromised](https://www.wiz.io/blog/mini-shai-hulud-strikes-again-tanstack-more-npm-packages-compromised)
