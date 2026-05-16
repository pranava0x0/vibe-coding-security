---
id: 2026-04-mini-shai-hulud-sap
title: "Mini Shai-Hulud — SAP-related npm packages (April–May 2026)"
date_disclosed: 2026-04
last_updated: 2026-05-16
severity: high
status: active
ecosystems: [npm]
tools_affected: [enterprise-node, sap-cap, any-node-with-sap-deps]
tags: [supply-chain, credential-theft, npm, mini-shai-hulud, enterprise]
---

## TL;DR
A Mini Shai-Hulud variant targeting the SAP ecosystem compromised `mbt`, `@cap-js/db-service`, `@cap-js/postgres`, `@cap-js/sqlite`, and related packages starting in April 2026. The payload harvests local dev creds, GitHub/npm tokens, GitHub Actions secrets, and cloud credentials for AWS, Azure, GCP, and Kubernetes.

## What happened
A targeted credential-stealing payload was injected into SAP-related npm packages. Unlike the worm versions of Shai-Hulud, this campaign focused on enterprise developer machines and CI runners where SAP CAP (Cloud Application Programming) tooling is common.

The malware specifically enumerates:
- `~/.npmrc`, `~/.yarnrc`, `~/.config/configstore/`
- `~/.aws/credentials`, `~/.aws/config`
- `~/.azure/`, `~/.config/gcloud/`
- `~/.kube/config`
- GitHub Actions secrets via `$GITHUB_TOKEN` if running in CI
- Environment variables matching `*TOKEN*`, `*KEY*`, `*SECRET*`, `*PASSWORD*`

## Am I affected?

```bash
# Affected package families
npm ls --all 2>/dev/null | grep -E '(@cap-js/|^mbt|@sap/cds)'
```

If you've installed or upgraded any of these in April or May 2026, assume credential theft.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — all of AWS, Azure, GCP, Kubernetes
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — use short-lived creds, OIDC, 1Password CLI

## Sources
- [The Hacker News — SAP-Related npm Packages Compromised in Credential-Stealing Supply Chain Attack](https://thehackernews.com/2026/04/sap-npm-packages-compromised-by-mini.html)
- [NHS England Digital — Supply Chain Attack Affecting Numerous npm and PyPI Packages](https://digital.nhs.uk/cyber-alerts/2026/cc-4781)
