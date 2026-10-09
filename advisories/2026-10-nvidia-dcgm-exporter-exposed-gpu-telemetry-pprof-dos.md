---
id: 2026-10-nvidia-dcgm-exporter-exposed-gpu-telemetry-pprof-dos
title: "NVIDIA DCGM Exporter: about 2,100 GPU servers at some 300 organisations exposed unauthenticated GPU telemetry to the internet, and a quarter also exposed the Go profiling endpoints an unauthenticated caller can use to crash monitoring (CVE-2026-47483, 8.2, bulletin 2026-07-28, DCGM 4.5.3 / Exporter 4.8.2); Lava research 2026-10-08"
date_disclosed: 2026-10-08
last_updated: 2026-10-09
severity: medium
status: patched
ecosystems: [ai-infrastructure, gpu, kubernetes, monitoring, prometheus]
tools_affected: [nvidia-dcgm-exporter, nvidia-dcgm, "Prometheus scrape targets on GPU hosts", "GPU-cloud tenants who deployed the exporter themselves"]
tags: [cve, exposed-infrastructure, gpu, telemetry, information-disclosure, dos, internet-scan, ai-infrastructure]
---

## TL;DR
Lava published research on 2026-10-08 after four internet scans between March and May 2026 found "more than 2,000" hosts, about 2,100, serving **NVIDIA DCGM Exporter** GPU telemetry over plaintext HTTP with no authentication, reporting more than 12,000 unique GPUs at nearly 300 organisations. The metrics name the exact GPU model, utilisation, memory, power, NVLink traffic, driver version and error events, which is enough to map an AI deployment and its workload schedule from outside. About a quarter of those hosts also exposed Go's `/debug/pprof/` profiling endpoints, and Lava found that concurrent unauthenticated profiling requests exhaust the exporter's resources; NVIDIA assigned **CVE-2026-47483** (CVSS 8.2, CWE-770, "denial of service and information disclosure") and published bulletin 5857 on **2026-07-28** with fixed versions **DCGM 4.5.3** and **DCGM Exporter 4.8.2**. Much of the exposure sat on customer infrastructure at GPU clouds (Voltage Park, Lambda, Northern Data, DigitalOcean), which say customers deployed the exporters themselves. If you run GPUs, check port 9400.

## What happened
DCGM Exporter reads telemetry from every GPU on a host and publishes it at `:9400/metrics` for Prometheus. It has no authentication of its own because it is meant to sit on a private scrape network. Lava's researcher Michael Katchinskiy enabled it on the company's own cluster, saw how much a single response revealed, and asked how many were public. The answer, per Lava and the outlets that read the post: roughly 2,100 hosts, 12,000-plus GPUs including Blackwell Ultra B300, H200, H100, RTX 5090 and 4090, an estimated $100 million of hardware, 44 percent of the GPUs in the United States, then Romania and China. Help Net Security's summary of the post gives Voltage Park as the largest single group (71 public DCGM Exporter hosts and 672 public Node Exporter hosts), with the provider confirming the instances were customer-deployed and notifying them. Lava separately counted 12,096 public Prometheus Node Exporter hosts, a reconnaissance source rather than a vulnerability.

**The vulnerability.** The exporter also served Go's standard `/debug/pprof/` endpoints. Some keep a request open for a caller-chosen duration, so a burst of concurrent unauthenticated profiling requests drives memory up until the exporter crashes, blinding operators to GPU health and, per Lava, potentially slowing workloads on the same host. NVIDIA's bulletin: "an attacker could cause uncontrolled resource consumption by submitting concurrent unauthenticated profiling requests", CVSS 3.1 8.2 (`AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H`), CWE-770. The bulletin's fix table lists DCGM "0.0 to 4.5.2" updated to **4.5.3**, and DCGM Exporter "0.0 to 4.8.2" updated to **4.8.2**, which names the same number as last affected and fixed; Lava's post, as summarised by Unite.AI, says the fix is Exporter 4.8.2. Read the Exporter line as "upgrade to 4.8.2 or later" and the DCGM line as "4.5.3 or later". The CNA record was published 2026-07-28; no exploitation in the wild is reported and the CVE is not in KEV as of 2026-10-09.

**Why it is in this corpus.** This is the third exposed-AI-infrastructure entry in a week, after [LMCache's unauthenticated ZeroMQ transport](2026-10-lmcache-unauthenticated-pickle-rce-vllm-kv-cache.md) and [the PoeLLM botnet scanning for LiteLLM and Ollama](2026-10-poellm-canto-incognito-litellm-ollama-cryptomining-botnet.md). A GPU box rented for fine-tuning or self-hosted inference arrives with monitoring the tenant turns on and forgets to firewall, and the metrics page tells the next scanner exactly what the box is worth. Filed medium: the CVE is a denial of service, and the exposure finding is a configuration problem rather than a product flaw.

## Am I affected?
```bash
ss -ltnp | grep -E ':9400|:9100'                     # dcgm-exporter and node-exporter bound beyond loopback
curl -s "$GPU_HOST:9400/debug/pprof/" | head -3        # from outside the scrape network: any response is exposure
helm list -A 2>/dev/null | grep -i dcgm; kubectl get svc -A 2>/dev/null | grep -i dcgm   # LoadBalancer or NodePort services
```
Compare the running exporter image or binary version against 4.8.2.

## If you are affected
1. Upgrade DCGM Exporter to **4.8.2 or later** and DCGM to **4.5.3 or later**.
2. Take ports 9400 and 9100 off public and tenant-shared interfaces; scrape through a private network, a mesh, or an authenticating reverse proxy, and disable or firewall `/debug/pprof/`.
3. Assume the hardware inventory, driver versions and utilisation pattern are known to anyone who scanned during the exposure window; that is reconnaissance, so review the rest of the host's exposed services with the same care. See [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) if the host also exposed anything that carries secrets.

## Prevention
Treat metrics endpoints as internal services from the first deploy, and include them in the egress and ingress review for every GPU host ([ci-cd-hardening.md](../prevention/ci-cd-hardening.md), [supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)). On rented GPU capacity, the provider's firewall defaults are not your security policy.

## Sources
- [Lava — CVE-2026-47483: NVIDIA DCGM Exporter Vulnerability Exposes GPU Servers](https://lava.security/research/cve-2026-47483-nvidia-dcgm-exporter-vulnerability) (fetched 2026-10-09; primary research: "more than 2,000" servers, "more than 12,000 unique GPUs", $100 million estimate, the GPU models, the named providers and their response, what the metrics reveal, the `/debug/pprof/` finding)
- [NVIDIA Product Security — Security Bulletin: NVIDIA DCGM Exporter, July 2026 (bulletin 5857)](https://github.com/NVIDIA/product-security/tree/main/2026/5857) (raw markdown fetched 2026-10-09; updated 2026-07-28; CVE-2026-47483, CVSS 8.2 vector, CWE-770, affected DCGM 0.0 to 4.5.2 → 4.5.3 and DCGM Exporter 0.0 to 4.8.2 → 4.8.2, credit Michael Katchinskiy)
- [CVE Services — CVE-2026-47483](https://cveawg.mitre.org/api/cve/CVE-2026-47483) (CNA nvidia, published 2026-07-28; affected DCGM "0.0 to 4.5.2" and DCGM Exporter "0.0 to 4.8.2"; 8.2)
- [Help Net Security — High-severity NVIDIA vulnerability lets unauthenticated attackers crash GPU monitoring](https://www.helpnetsecurity.com/2026/10/09/nvidia-dcgm-exporter-vulnerability-cve-2026-47483/) (2026-10-09; the country split, the Voltage Park counts, the bulletin date)
- [Unite.AI — Lava Finds Thousands of Exposed GPU Servers and a High-Severity NVIDIA Monitoring Flaw](https://www.unite.ai/lava-nvidia-dcgm-exporter-gpu-security/) (2026-10-08; "roughly 2,100" hosts, the scan window caveat, the fix version as 4.8.2)
- [The Register — High-severity Nvidia bug could crash GPU monitoring on exposed servers](https://www.theregister.com/security/2026/10/08/high-severity-nvidia-bug-could-crash-gpu-monitoring-on-exposed-servers/5302077) (2026-10-08; about 2,100 servers, 12,000 UUIDs, about 300 organisations, 5,274 GPUs in the US)
