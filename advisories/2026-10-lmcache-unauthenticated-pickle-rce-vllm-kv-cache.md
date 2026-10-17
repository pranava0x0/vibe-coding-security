---
id: 2026-10-lmcache-unauthenticated-pickle-rce-vllm-kv-cache
title: "LMCache (the KV-cache layer under vLLM) — unauthenticated remote code execution via pickle deserialization on the multiprocess ZeroMQ transport (CVE-2026-105192, CVSS 9.8); affected 0.3.9 through 0.5.5 and the 0.5.6 release candidates, no fixed version at disclosure, and the official container images run the process as root; fixed 0.5.6 on 2026-10-15, upgrade every worker and server together"
date_disclosed: 2026-10-07
last_updated: 2026-10-17
severity: critical
status: patched
ecosystems: [pypi, llm-infrastructure, self-hosted]
tools_affected: [lmcache, "vLLM deployments using the LMCache multiprocess/distributed connector", "any multi-node or Kubernetes LLM-serving stack that sets a routable LMCache --host"]
tags: [cve, rce, pickle-deserialization, missing-authentication, zeromq, llm-infrastructure, vllm, runs-as-root, vendor-ghsa, wire-format-change, patched]
---

## TL;DR
**LMCache**, the open-source KV-cache layer that speeds up LLM servers such as vLLM, has an **unauthenticated remote code execution** bug in its multiprocess (distributed) mode: the cache server opens an unauthenticated ZeroMQ socket, and one message type is handed to Python's `pickle` during argument decoding, before any handler runs. A single crafted message from any host that can reach the port runs code as the LMCache process — **root** in the project's official container images. JFrog disclosed it on **2026-10-07** as **CVE-2026-105192, CVSS 9.8**, with **no fixed version available**. The default bind is localhost and is not exposed; the risk is multi-node and Kubernetes deployments that set a routable `--host`, which LMCache's own example Kubernetes manifest does.

## What happened
LMCache's multiprocess/distributed mode opens a ZeroMQ `ROUTER` socket (default port 5555) so worker processes can register and share cache blocks, with no CURVE, ZAP, password or per-message authentication. Messages are msgpack; extension code 1 is passed to a deserializer that calls `pickle.loads` on attacker-supplied bytes while the server is still decoding a `REGISTER_KV_CACHE` request's arguments and before the handler runs. JFrog's Yuval Moravchick reported it, and JFrog disclosed it on **2026-10-07** as **CVE-2026-105192 (JFSA-2026-001694382)**, CVSS **9.8** (the score applies to the routable configuration), CWE-502 and CWE-306. The vendor had not published an advisory and **no fixed version exists**; JFrog notes the official container images run the process as **root**, so a single message means full host compromise. A separate JFrog note records that one GitHub account opened six more LMCache security reports on 2026-10-06 (unauthenticated cross-tenant cache reads and command-running network services), single-source proof-of-concept claims with no CVE, maintainer confirmation or fix — tracked here only as context. Public proof-of-concept code for CVE-2026-105192 has since appeared; this advisory links JFrog's analysis, not any exploit.

This is the same class as the two InternLM LMDeploy RCEs disclosed in September (CVE-2025-66455, CVE-2025-59953 — pickle over ZeroMQ) and the November 2025 ShadowMQ research that found the pattern across several AI inference frameworks: an unauthenticated network socket feeding `pickle`. The audience overlap for vibe coders is anyone self-hosting vLLM with LMCache for a RAG or agent backend.

## Am I affected?
```bash
pip show lmcache 2>/dev/null | grep -i version      # 0.3.9 through 0.5.5 (and 0.5.6rc*) are affected
# Is the multiprocess server reachable off-box? Default bind is localhost (safe).
# You are exposed only if LMCache runs in multiprocess/distributed mode with a routable --host,
# e.g. a multi-node or Kubernetes deployment binding on all interfaces.
ss -ltnp 2>/dev/null | grep 5555
```
An LMCache embedded inside a single vLLM process does not open the port and is not remotely exploitable. JFrog gives operators no way to tell whether a server has already been hit.

## If you are affected
No patch exists. Keep the LMCache ZMQ transport off routable networks — bind it to localhost or a trusted cluster-internal network only, and do not set `--host` to a routable address. A firewall reduces exposure but does not remove it, since any host that can open a connection can run code; segment the serving tier and do not run the container as root. See [agent-sandboxing.md](../prevention/agent-sandboxing.md) and [if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md). Watch for a fixed LMCache release and upgrade immediately when it ships.

**Update 2026-10-09: still no fix.** The CVE record (CNA JFrog, updated 2026-10-07) gives the affected versions as 0.3.9 and later, with no fixed version. PyPI's latest stable is still 0.5.5 (2026-09-12). The newest pre-release, `0.5.6rc3` (2026-10-06), falls inside that range. This advisory keeps the tested range in its title and treats every later version as affected until a fix ships. Do not treat a release candidate as a fix.

## Update — 2026-10-17: fixed in 0.5.6 (PyPI 2026-10-15); the vendor advisory and post-mortem (2026-10-13) change the wire format, so every worker and server upgrades together; status → `patched`

The maintainers published [GHSA-w5f2-9q9c-ff4h](https://github.com/LMCache/LMCache/security/advisories/GHSA-w5f2-9q9c-ff4h) on **2026-10-13** (account nijaba; CVSS 3.1 9.8, CWE-306; affected `>= 0.3.9, < 0.5.6`, patched **0.5.6**) and [a post the same day](https://blog.lmcache.ai/en/2026/10/13/an-update-on-cve-2026-105192): JFrog's public disclosure on 2026-10-07 was the first the project heard of it, the fix (PR #5644) merged to the dev branch on 2026-10-12, and 0.5.6 reached PyPI on **2026-10-15**. The GitHub Advisory Database published the review on 2026-10-16, which is where this sweep saw it.

What the fix does, from the advisory: the device IPC descriptors that went through `pickle` are now versioned, typed MessagePack structures, validated first, with the wrapper type chosen from a fixed local allowlist and **no pickle fallback**. The wire format changed, so **old and new processes cannot talk**; the maintainers say to upgrade all workers and servers together, and that mixing versions is unsupported. The example Kubernetes deployment, which bound all interfaces, now binds localhost, and official images run as a non-root user from 0.5.6. Still planned, not shipped: RPC authentication between server, coordinator and frontend in 0.5.7, and removal of the remaining pickle use on the engine-driven path, which they describe as disabled by default and not network-reachable, before 0.5.8.

Compromise assessment, in the maintainers' words: if the port was reachable from untrusted networks, treat the host as potentially compromised, review connections from unexpected sources and unexpected child processes, shells or outbound connections, rotate reachable secrets and redeploy from clean images; a rejected request in the logs does not show the attack failed, because exploitation happens before message processing.

Status moves from `active` to `patched` on the vendor's explicit fixed version, which is on PyPI. Severity stays `critical` for the routable configuration. The 2026-10-09 note above ("do not treat a release candidate as a fix") stands for the 0.5.6 release candidates; the 0.5.6 release itself carries the fix.

```bash
pip show lmcache 2>/dev/null | grep -i '^version'   # 0.5.6 or later on every server and worker; a mixed cluster will not connect
```

## Prevention
Treat every unauthenticated LLM-infrastructure port as internet-reachable until proven otherwise ([supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)); never expose an inference or cache control plane without authentication and network isolation ([ci-cd-hardening.md](../prevention/ci-cd-hardening.md)).

## Sources
- [JFrog Security Research — LMCache is vulnerable to Unauthenticated RCE via Pickle Deserialization on the Multiprocess ZMQ Transport (CVE-2026-105192)](https://research.jfrog.com/vulnerabilities/lmcache-is-vulnerable-to-unauthenticated-remote-code-execution-via-pickle-deserialization-on-the-multiprocess-zmq-transport-cve-2026-105192-jfsa-2026-001694382/) (2026-10-07: CVSS 9.8, affected 0.3.9+ incl. 0.5.5 and 0.5.6rc*, no fix, official images run as root, mitigations)
- [CVE Services — CVE-2026-105192](https://cveawg.mitre.org/api/cve/CVE-2026-105192) (CNA JFrog, published 2026-10-07, CVSS 3.1 9.8 `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`, references the LMCache repo and the two affected source files)
- [The Hacker News — Unpatched Critical LMCache Flaw Lets Unauthenticated Attackers Run Code Remotely](https://thehackernews.com/2026/10/unpatched-critical-lmcache-flaw-lets.html) (2026-10-07: discovery by Yuval Moravchick, six single-account follow-up reports from 2026-10-06, ShadowMQ and vLLM CVE-2026-105756 context)
- [PyPI — lmcache release history](https://pypi.org/project/lmcache/) (checked 2026-10-08: latest stable 0.5.5, confirming no fixed release)
- **2026-10-17 update sources** — [LMCache/LMCache — GHSA-w5f2-9q9c-ff4h](https://github.com/LMCache/LMCache/security/advisories/GHSA-w5f2-9q9c-ff4h) (vendor advisory, published 2026-10-13; affected >= 0.3.9 < 0.5.6, patched 0.5.6, the MessagePack fix, the wire-format change, mitigations; fetched 2026-10-17 through the [database row](https://github.com/advisories/GHSA-w5f2-9q9c-ff4h) reviewed 2026-10-16); [LMCache blog — An update on CVE-2026-105192](https://blog.lmcache.ai/en/2026/10/13/an-update-on-cve-2026-105192) (2026-10-13; the 10-07 / 10-12 / 10-13 timeline, PR #5644, the compromise-assessment guidance, 0.5.7 and 0.5.8 plans); PyPI `lmcache` metadata, queried 2026-10-17: 0.5.5 on 2026-09-12, 0.5.6 on 2026-10-15, latest.
