---
id: 2026-09-coder-registry-cloudflare-terraform-supply-chain
title: "Coder registry compromise — a stolen Cloudflare API key rerouted registry.coder.com for 14 hours, serving credential-stealing Terraform modules to AI-workspace provisioners (GHSA-vx42-ghc9-gw65)"
date_disclosed: 2026-09-01
last_updated: 2026-09-20
severity: critical
status: patched
ecosystems: [terraform, coder, cloud-dev-environment, ai-agents]
tools_affected: [coder, registry.coder.com, any-coder-workspace-provisioning-ai-agents]
tags: [supply-chain, credential-theft, cloudflare, terraform, dev-environment, ai-agents, oidc, cdn-hijack]
---

## TL;DR
Between **07:35 and 21:45 UTC on 2026-08-31**, an attacker used a **stolen Cloudflare API key** to add malicious origin IPs to the pool behind **`registry.coder.com`**, so a fraction of legitimate module pulls were served **tampered Terraform modules** that stole every credential in the provisioning environment and shipped them to a lookalike domain. Coder — a self-hosted cloud development environment used to provision workspaces for **Claude Code, Codex, and other AI coding agents** — is the CDN-hijack sibling of the [Coder AI-Bridge OIDC release](2026-07-coder-ai-bridge-oidc-security-release.md): this time the bug was not in Coder's code but in the delivery path in front of it. Fixed by upgrading to **2.37.0 / 2.36.4 / 2.35.7 / 2.34.9**, which purge the poisoned modules from cache. If your Coder pulled a module during the window, treat every credential the provisioner could reach as exfiltrated.

## What happened
Coder disclosed the incident on **2026-09-04** ([Coder blog](https://coder.com/blog/coder-registry-security-incident-what-happened-and-what-to-do)) alongside **[GHSA-vx42-ghc9-gw65](https://github.com/coder/coder/security/advisories/GHSA-vx42-ghc9-gw65)** (published 2026-09-01, Critical, CVSS 9.0, no CVE). The chain, per the advisory:

1. An unauthorized actor obtained a **Cloudflare API key** belonging to Coder and used it to **add attacker-controlled origin IPs to the server pool** for `registry.coder.com`, so Cloudflare load-balanced a share of real requests to the attacker's server.
2. The attacker's server returned **tampered copies of legitimate Coder registry modules**. The tamper was a single injected Terraform `data "external" "telemetry"` block that runs `${path.module}/dlp-docker.sh` — a legitimate Terraform construct that executes a script during provisioning **with the privileges of the provisioning process**.
3. The script harvested and exfiltrated **provisioner environment variables, cloud and AI-tooling API keys, CI/CD credentials, config-file secrets, terminal history, user OIDC tokens, SSH keys, external-auth tokens, and (where the provisioner ran inside `coderd`) Coder database passwords**.
4. Stolen data went out over `POST http://www.coder-infra[.]com/cli/check` with the loot in an `X-CLI-Token` header. The lookalike domain was **registered 2026-08-28**, three days before the window.

The window was **~14 hours**; the lookalike was pre-staged; only a *fraction* of pulls were poisoned because the malicious origins shared the pool with the real ones. Coder states its **own codebase and Google Cloud infrastructure were not compromised** and it found no evidence customer data it maintains was affected — but it cannot conclusively identify every affected deployment, and notes its **lock file does not track remote modules**, so version-pinning would not have caught this. Independent coverage: [BleepingComputer](https://www.bleepingcomputer.com/news/security/coders-registry-infrastructure-compromised-to-push-malicious-modules/), [eSecurity Planet](https://www.esecurityplanet.com/cybersecurity/news-coder-registry-malicious-terraform-modules/), [CSA Lab Space](https://labs.cloudsecurityalliance.org/research/csa-research-note-coder-registry-terraform-supply-chain-2026/).

**Why this repo cares:** Coder is where a lot of teams run their AI coding agents, so a poisoned provisioning module inherits **AI provider keys and MCP credentials** alongside the usual cloud/CI secrets. This is the same shape as the [Coder AI-Bridge coordinated release](2026-07-coder-ai-bridge-oidc-security-release.md) (dev-environment platform as a credential hub) and the same delivery-layer lesson as any CDN/registry hijack: **a trusted download endpoint is part of your supply chain even when the vendor's source is clean.**

## Am I affected?

You are potentially affected if a Coder deployment **pulled a registry module during 2026-08-31 07:35–21:45 UTC**.

```bash
# Coder version
coder version

# Provisioner logs: the tampered module leaves this sentinel string
grep -r 'data.external.telemetry' /var/log/coder* 2>/dev/null
# ...and the injected script name
grep -rn 'dlp-docker.sh\|dlp.sh' /var/log/coder* 2>/dev/null

# DNS / firewall / VPC flow logs: any lookup or connection to the exfil domain
#   is a confirmed-compromise signal (defanged; do not resolve or visit)
#   coder-infra[.]com  (and subdomains)  ->  199.91.220[.]205
```

Coder's advisory ships **SQL queries** to list templates, template versions, and workspaces that fetched cached modules during the window, plus a deletion query to purge them.

### IOCs

| Type | Value |
|---|---|
| GHSA | `GHSA-vx42-ghc9-gw65` (Critical, CVSS 9.0, no CVE) |
| Incident window | 2026-08-31 **07:35–21:45 UTC** |
| Exfil domain | `coder-infra[.]com` (registered 2026-08-28), endpoint `/cli/check`, `X-CLI-Token` header |
| Malicious origin IP | `199.91.220[.]205` |
| Provisioner-log sentinel | `data.external.telemetry`; scripts `dlp-docker.sh`, `dlp.sh` |
| Affected | Coder `< 2.37.0` (deployments that pulled a module in the window) |
| Fixed | `2.37.0`, `2.36.4`, `2.35.7`, `2.34.9` (purge cached poisoned modules) |
| Data stolen | cloud + AI-provider API keys, CI/CD creds, OIDC tokens, SSH keys, external-auth tokens, terminal history, `coderd` DB passwords |

## If you are affected
1. **Upgrade** to `2.37.0` / `2.36.4` / `2.35.7` / `2.34.9` (or later) and run Coder's cache-purge SQL so poisoned modules cannot be re-served from cache.
2. If you cannot rule out a pull during the window, **rotate every credential the provisioning process could reach**: cloud provider keys, CI/CD credentials, SSH keys, OIDC tokens, external-auth tokens, and — because Coder provisions AI workspaces — **every AI provider / MCP credential wired into a template**. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
3. Search firewall / DNS / VPC flow logs for `coder-infra[.]com` and `199.91.220[.]205`; a hit is confirmation, not suspicion.
4. If a workspace agent or its live credentials may have been used: [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Update 2026-09-20 — an earlier, unrelated Coder bug worth knowing: a workspace-proxy hostname *prefix* match let an attacker's domain collect app-scoped API keys (GHSA-h58h-qvv5-xvwg, CVSS 7.7, 2026-08-10; reported by Anthropic's security team)

Three weeks before the registry compromise, Coder published a batch of five advisories on 2026-08-10 that no sweep here had logged. The one that matters for workspaces exposed through proxies: `GetWorkspaceProxyByHostname` matched proxy hostnames with a **prefix pattern** rather than an exact host, so a domain that was merely a string prefix of a real proxy URL — the advisory's example: `syd.co` matching `syd.coder-proxy.example.com` — was treated as a trusted proxy. An attacker who got an authenticated user to click a crafted auth-redirect link could intercept an **application-scoped API key** and replay it against the genuine proxy to reach the victim's workspace apps. Affected **v2.35.0–2.35.3, v2.34.0–2.34.7, v2.33.0–2.33.11 and everything before v2.29.20**; fixed **v2.35.4 / v2.34.8 / v2.33.12 / v2.29.20** (the pattern now requires a string end, port delimiter or path separator after the host). Deployments that do not use workspace proxies are not affected. No CVE. Credited to the **Anthropic Security Team (ANT-2026-FXER0JGJ)** and Adam Korczynski (Ada Logics) — a data point that AI-vendor security teams are auditing the cloud-dev-environment layer their own agents run in. The same day's batch also covered an unauthenticated agent debug manifest exposing environment variables across workspace users (Low), user-level ACL grants bypassing org membership (Moderate), cross-org Terraform module file disclosure via the provisioner `DownloadFile` RPC (Moderate) and a workspace ACL endpoint exposing group-member PII (Moderate). If you are on a fix line below the registry-incident versions above (2.37.0 / 2.36.4 / 2.35.7 / 2.34.9), you are past this one too; if you pinned lower, the proxy bug is a second reason to move.

## Prevention
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md) — a vendor's download/registry endpoint is part of *your* supply chain; a clean source repo does not make the delivery path clean.
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — scope provisioning credentials as narrowly as possible; an AI-agent workspace needs its model-provider/MCP keys, not the full provisioning credential set.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — short-lived tokens over long-lived keys so a 14-hour exposure window is a rotation, not a standing breach.

## Sources
- [Coder — GHSA-h58h-qvv5-xvwg: Workspace proxy hostname prefix match lets an attacker-controlled domain steal a victim's workspace app credential](https://github.com/coder/coder/security/advisories/GHSA-h58h-qvv5-xvwg) — vendor advisory, published 2026-08-10: CVSS 7.7, affected/fixed ranges, the `syd.co` example, reporter credits. Fetched 2026-09-20.
- [coder/coder — security advisories tab](https://github.com/coder/coder/security/advisories) — fetched 2026-09-20: the five 2026-08-10 advisories and the 2026-09-01 registry advisory.
- [Coder — Coder Registry Security Incident: What Happened and What to Do](https://coder.com/blog/coder-registry-security-incident-what-happened-and-what-to-do) — fetched 2026-09-16; vendor primary, published 2026-09-04: Cloudflare-key mechanism, 07:35–21:45 UTC window, `coder-infra.com` exfil domain, "own codebase and Google Cloud infrastructure were not compromised," lock file does not track remote modules.
- [GitHub Security Advisory GHSA-vx42-ghc9-gw65 — Malicious Packages Served from Unauthorized Registry Server](https://github.com/coder/coder/security/advisories/GHSA-vx42-ghc9-gw65) — fetched 2026-09-16; CVSS 9.0, published 2026-09-01, affected `< 2.37.0`, fixes `2.37.0/2.36.4/2.35.7/2.34.9`, full IOC set (SHA-256 hashes, `data.external.telemetry` sentinel, `X-CLI-Token`/`/cli/check` exfil), detection SQL.
- [BleepingComputer — Coder's registry infrastructure compromised to push malicious modules](https://www.bleepingcomputer.com/news/security/coders-registry-infrastructure-compromised-to-push-malicious-modules/) — fetched 2026-09-16; independent coverage, published 2026-09-04.
- [eSecurity Planet — Coder Registry Compromise: Malicious Terraform Modules Explained](https://www.esecurityplanet.com/cybersecurity/news-coder-registry-malicious-terraform-modules/) — fetched 2026-09-16; published 2026-09-04, "no evidence that customer data it maintains was affected," lock file quote.
- [Cloud Security Alliance Lab Space — Coder Registry Compromise Spreads Credential-Stealing Terraform Modules](https://labs.cloudsecurityalliance.org/research/csa-research-note-coder-registry-terraform-supply-chain-2026/) — fetched 2026-09-16; research-note framing, AI-workspace provisioning impact.
