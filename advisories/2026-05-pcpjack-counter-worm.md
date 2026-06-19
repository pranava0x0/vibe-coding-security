---
id: 2026-05-pcpjack-counter-worm
title: "PCPJack — credential-stealing counter-worm that removes TeamPCP infections (May 2026)"
date_disclosed: 2026-05
last_updated: 2026-06-07
severity: high
status: active
ecosystems: [npm, cloud, kubernetes, docker]
tools_affected: [kubernetes clusters, Docker hosts, Redis instances, MongoDB deployments, RayML environments, Next.js apps (CVE-2025-29927), React RSC apps (CVE-2025-55182)]
tags: [worm, credential-theft, cloud, kubernetes, supply-chain, teampcp, lateral-movement, cve-chaining]
---

## TL;DR
**PCPJack** is a credential-stealing worm that poses as a cleanup tool for TeamPCP infections — it genuinely removes TeamPCP malware from compromised hosts, but simultaneously steals all credentials and spreads itself. Disclosed May 2026 by SentinelLabs. Chains **5 CVEs** to spread worm-like across Kubernetes, Docker, Redis, and MongoDB infrastructure. Critically, it also spreads by **exploiting React2Shell (CVE-2025-55182) and Next.js (CVE-2025-29927)** — meaning web apps using affected frameworks are lateral-movement entry points for cloud infrastructure compromise.

## What happened

SentinelLabs identified **PCPJack** as a new malware framework distinct from TeamPCP, possibly developed by a former TeamPCP affiliate or member who started an independent operation. The "counter-worm" framing is deliberate deception: PCPJack genuinely removes TeamPCP's malicious processes and configurations, giving the victim false confidence that their system is clean, while PCPJack's own credential harvest runs in the background.

### Attack capabilities

1. **System reconnaissance**: identifies cloud provider, Kubernetes credentials (`~/.kube/config`), Docker socket, Redis/MongoDB connection strings, SSH keys.
2. **Credential theft**: exfiltrates cloud IAM credentials (AWS, GCP, Azure), Kubernetes service account tokens, Docker registry creds, database connection strings, npm/GitHub tokens, and SSH private keys.
3. **Lateral movement**: uses extracted credentials to propagate across:
   - **Kubernetes** clusters (via stolen `kubeconfig` / service-account tokens)
   - **Docker** hosts (via exposed Docker socket or stolen Docker credentials)
   - **Redis** and **MongoDB** deployments (via connection strings)
   - **RayML** environments (via stolen API credentials)
   - SSH key propagation to known hosts
4. **CVE-based spreading**: downloads Parquet files from Common Crawl to identify internet-accessible targets, then exploits:
   - **CVE-2025-29927** (Next.js)
   - **CVE-2025-55182** (React2Shell CVSS 10.0 — React Server Components RCE)
   - **CVE-2026-1357** (WPVivid Backup plugin)
   - **CVE-2025-9501** (W3 Total Cache)
   - **CVE-2025-48703** (CentOS Web Panel)
5. **TeamPCP cleanup**: actively kills TeamPCP processes, deletes TeamPCP files, and revokes TeamPCP persistence — to reduce "noise" and avoid drawing attention to the host.

### Vibe-coding relevance: React2Shell chain

PCPJack actively exploits **CVE-2025-55182 (React2Shell, CVSS 10.0)** to gain initial footholds. Any vibe-coded app running a vulnerable React Server Components setup (Next.js, Waku, React Router RSC, RedwoodSDK, Parcel RSC, Vite RSC plugin) that is **not yet patched** is a potential entry point into the developer's cloud infrastructure. The worm pivots from the web app into the cloud credentials it finds on the same host.

The 766+ hosts confirmed compromised by React2Shell through April 2026 are all potential PCPJack lateral-movement targets.

## Am I affected?

```bash
# Is your React/Next.js app patched against React2Shell?
# Vulnerable: React <19.0.4/19.1.5/19.2.4, Next.js <15.5.18/<16.2.6
npm list react react-dom next 2>/dev/null | grep -E 'react|next'

# Check for PCPJack indicators on your host
# PCPJack commonly drops a "cleanup" script that writes to /tmp
ls -la /tmp/pcp* /tmp/.pcpjack* 2>/dev/null

# Check for unexpected Kubernetes context changes
kubectl config get-contexts 2>/dev/null

# Audit for unexpected Docker image pulls
docker events --since 24h 2>/dev/null | grep -i pull
```

**High risk if:**
- You run React/Next.js apps with Server Components that are not patched to React ≥ 19.0.4 / Next.js ≥ 15.5.18.
- Your web app server has cloud credentials (`~/.aws`, `~/.gcp`, `KUBECONFIG`, etc.) accessible to the web process.
- You run Kubernetes, Docker, Redis, or MongoDB in the same network segment as a web server.

## If you are affected

1. **Patch React2Shell immediately**: upgrade React to ≥ 19.0.4 and Next.js to ≥ 15.5.18 / ≥ 16.2.6.
2. **Rotate all cloud credentials** the compromised host could access.
3. **Audit Kubernetes RBAC** — check for unexpected service accounts or cluster-admin bindings.
4. **Check Redis / MongoDB** access logs for unauthorized queries.
5. **Do not trust the absence of TeamPCP infections** as a sign of a clean host — PCPJack cleans TeamPCP but persists itself.

## Prevention

→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

- **Patch React/Next.js** against CVE-2025-55182 now. This is CISA KEV.
- **Never run web app processes with access to cloud IAM credentials**, Kubernetes configs, or Docker sockets. Use separate service accounts with minimal permissions.
- **Network-segment your databases** — Redis and MongoDB should not be reachable from web app hosts.
- **Treat a "cleaned" host as still compromised** until full incident response confirms otherwise.

## June 2026 escalation — 230-node SMTP relay

**PCPJack has weaponized its credential harvest into a covert SMTP relay network.** As of June 2026, SentinelLabs researchers found that PCPJack hijacked **230 AWS, Google Cloud, and Azure servers** — all compromised via stolen cloud IAM credentials from prior waves — and quietly converted them into SMTP mail proxies. The relay network syncs verified outbound-mail-capable proxies to a downstream consumer every **five minutes**, providing a scalable, constantly-refreshing spam/phishing infrastructure sourced entirely from legitimate enterprise cloud accounts.

Key implications for defenders:
- PCPJack is not just a credential harvester — it is now monetizing stolen cloud access as **SMTP-as-a-Service** for downstream threat actors.
- If your AWS/GCP/Azure accounts were exposed in any prior Miasma/GlassWorm/Megalodon/Shai-Hulud wave, assume they may be enrolled in this relay network.
- Detection: unusual SMTP traffic (port 25/587) from EC2/Compute Engine/Azure VM instances that do not run mail servers; unexpected IAM role usage for network egress.

Source: [The Hacker News — "PCPJack Hijacks 230 AWS, Google Cloud, and Azure Servers for Covert SMTP Relay Network"](https://thehackernews.com/2026/06/pcpjack-hijacks-230-aws-google-cloud.html)

## Sources

- [SecurityWeek — 'PCPJack' Worm Removes TeamPCP Infections, Steals Credentials](https://www.securityweek.com/pcpjack-worm-removes-teampcp-infections-steals-credentials/) — Primary disclosure; counter-worm mechanics, CVE list.
- [BleepingComputer — New PCPJack worm steals credentials, cleans TeamPCP infections](https://www.bleepingcomputer.com/news/security/new-pcpjack-worm-steals-credentials-cleans-teampcp-infections/) — Technical detail, lateral-movement targets.
- [CyberSecurityNews — New PCPJack Worm Targets Docker, Kubernetes, Redis, and MongoDB for Credential Theft](https://cybersecuritynews.com/new-pcpjack-worm-targets-docker/) — Infrastructure targeting and reconnaissance mechanics.
- [The Hacker News — PCPJack Credential Stealer Exploits 5 CVEs to Spread Worm-Like Across Cloud Systems](https://thehackernews.com/2026/05/pcpjack-credential-stealer-exploits-5.html) — 5-CVE list, Common Crawl scanning, React2Shell chain.
- [The Hacker News — "PCPJack Hijacks 230 AWS, Google Cloud, and Azure Servers for Covert SMTP Relay Network"](https://thehackernews.com/2026/06/pcpjack-hijacks-230-aws-google-cloud.html) — June 2026 SMTP relay escalation; 230-node network, five-minute refresh, enterprise cloud accounts.
- Cross-reference: [2025-12-react2shell-rce.md](2025-12-react2shell-rce.md) — CVE-2025-55182 React Server Components RCE, which PCPJack uses as its primary web-entry vector.
- Cross-reference: [2026-05-tanstack-mini-shai-hulud.md](2026-05-tanstack-mini-shai-hulud.md) — TeamPCP campaign whose infections PCPJack claims to remove.
