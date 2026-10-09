---
id: 2026-10-lmcache-unauthenticated-pickle-rce-vllm-kv-cache
title: "LMCache (the KV-cache layer under vLLM) — unauthenticated remote code execution via pickle deserialization on the multiprocess ZeroMQ transport (CVE-2026-105192, CVSS 9.8); affected 0.3.9 through 0.5.5 and the 0.5.6 release candidates, no fixed version at disclosure, and the official container images run the process as root"
date_disclosed: 2026-10-07
last_updated: 2026-10-09
severity: critical
status: active
ecosystems: [pypi, llm-infrastructure, self-hosted]
tools_affected: [lmcache, "vLLM deployments using the LMCache multiprocess/distributed connector", "any multi-node or Kubernetes LLM-serving stack that sets a routable LMCache --host"]
tags: [cve, rce, pickle-deserialization, missing-authentication, zeromq, llm-infrastructure, vllm, unpatched, runs-as-root]
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

**Record check 2026-10-09.** The CVE record (CNA JFrog, updated 2026-10-07) lists the affected range as `0.3.9` with no upper bound and no fixed version. PyPI's latest stable is still 0.5.5 (2026-09-12); `0.5.6rc3` (2026-10-06) is the newest pre-release and falls inside that range, so do not treat a release candidate as a fix.

## Prevention
Treat every unauthenticated LLM-infrastructure port as internet-reachable until proven otherwise ([supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)); never expose an inference or cache control plane without authentication and network isolation ([ci-cd-hardening.md](../prevention/ci-cd-hardening.md)).

## Sources
- [JFrog Security Research — LMCache is vulnerable to Unauthenticated RCE via Pickle Deserialization on the Multiprocess ZMQ Transport (CVE-2026-105192)](https://research.jfrog.com/vulnerabilities/lmcache-is-vulnerable-to-unauthenticated-remote-code-execution-via-pickle-deserialization-on-the-multiprocess-zmq-transport-cve-2026-105192-jfsa-2026-001694382/) (2026-10-07: CVSS 9.8, affected 0.3.9+ incl. 0.5.5 and 0.5.6rc*, no fix, official images run as root, mitigations)
- [CVE Services — CVE-2026-105192](https://cveawg.mitre.org/api/cve/CVE-2026-105192) (CNA JFrog, published 2026-10-07, CVSS 3.1 9.8 `AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H`, references the LMCache repo and the two affected source files)
- [The Hacker News — Unpatched Critical LMCache Flaw Lets Unauthenticated Attackers Run Code Remotely](https://thehackernews.com/2026/10/unpatched-critical-lmcache-flaw-lets.html) (2026-10-07: discovery by Yuval Moravchick, six single-account follow-up reports from 2026-10-06, ShadowMQ and vLLM CVE-2026-105756 context)
- [PyPI — lmcache release history](https://pypi.org/project/lmcache/) (checked 2026-10-08: latest stable 0.5.5, confirming no fixed release)
