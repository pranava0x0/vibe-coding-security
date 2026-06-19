---
id: 2026-03-sglang-unauth-rce
title: "SGLang unauth RCE cluster — CVE-2026-3059/3060 (pickle ZMQ, CVSS 9.8) + CVE-2026-5760 (GGUF model RCE)"
date_disclosed: 2026-03
last_updated: 2026-06-14
severity: critical
status: patched
ecosystems: [pypi, ai-agents]
tools_affected: [sglang, any LLM inference server using SGLang's multi-node ZMQ broker]
tags: [rce, unauth, deserialization, pickle, ai-infrastructure, llm-inference, gguf, supply-chain]
---

## TL;DR

Three critical unauthenticated RCE vulnerabilities in **SGLang** (the fast LLM inference and serving framework, ~1M monthly PyPI downloads) form a cluster: **CVE-2026-3059** and **CVE-2026-3060** (CVSS 9.8 each) exploit `pickle.loads()` in the multi-node ZMQ broker to execute arbitrary code without authentication; **CVE-2026-5760** allows RCE via a maliciously crafted GGUF model file. All three are patched in SGLang ≥ 0.4.6. Any self-hosted SGLang inference server exposed to the network — or reachable by an attacker with access to the local network — should be treated as fully compromised until patched.

## What happened

**CVE-2026-3059 & CVE-2026-3060 — pickle deserialization in ZMQ broker (CVSS 9.8)**

SGLang's multi-node/multi-GPU serving stack uses a ZeroMQ (ZMQ) broker to fan out requests to worker processes. The broker deserializes incoming task payloads with `pickle.loads()` — the Python equivalent of `eval()` on binary data. An attacker who can send a TCP packet to the ZMQ broker port (default: **30000/tcp** for inter-node communication, often bound to `0.0.0.0`) can include a crafted pickle payload that executes arbitrary Python code as the process user (commonly root in container deployments).

- **CVE-2026-3059**: ZMQ broker deserializes scheduler results without authentication or integrity checking
- **CVE-2026-3060**: ZMQ broker deserializes inference requests on the worker-facing port — a second independent deserialization path with the same root cause

No authentication, no TLS, no HMAC — the broker trusts any TCP connection on its port. SGLang clusters running on multi-GPU hosts (A100/H100) routinely expose this port on `0.0.0.0` for inter-node communication in training/serving environments.

**CVE-2026-5760 — GGUF model file RCE**

SGLang's GGUF model loader (used for llama.cpp-compatible quantized models) processes metadata tensors in a manner that allows a maliciously crafted `.gguf` file to trigger code execution when loaded. An attacker who can supply or substitute a GGUF model file — via a compromised model repository, a poisoned HuggingFace model, or a man-in-the-middle on model download — achieves RCE at model load time. This joins a broader class of **model-file RCE** vulnerabilities (PyTorch `torch.load()` pickle class; `numpy.load()` allow_pickle; Keras lambda layer deserialization).

**Blast radius:** SGLang inference servers typically hold:
- LLM provider API keys (OpenAI, Anthropic, AWS Bedrock, Google Vertex) in env vars
- Cloud IAM credentials (AWS, GCP, Azure) for model storage access
- SSH keys for multi-node communication
- In enterprise deployments: customer data processed through the LLM pipeline

## Am I affected?

```bash
# Check SGLang version
pip show sglang | grep Version
# Affected: < 0.4.6

# Check if ZMQ broker port is exposed
ss -tlnp | grep 30000
# Any result with 0.0.0.0:30000 means the broker is internet/LAN accessible

# Check for GGUF model files from untrusted sources
find . -name "*.gguf" | xargs -I{} python -c "
import struct, sys
with open('{}', 'rb') as f:
    magic = f.read(4)
    print('{}', 'OK' if magic == b'GGUF' else 'SUSPICIOUS: '+magic.hex())
"
```

## If you are affected

1. **Patch immediately**: `pip install "sglang>=0.4.6"`.
2. **Rotate all credentials** accessible from the inference server: cloud API keys, LLM provider tokens, SSH keys, any secrets in env vars or mounted volumes.
3. **Audit ZMQ broker access logs** for unexpected connections to port 30000 (or your configured broker port).
4. **Firewall the broker port**: restrict to known inference cluster IP ranges with `iptables` or security group rules. The broker should never be accessible from the public internet.
5. **Verify GGUF model integrity**: compare SHA-256 checksums of any GGUF files against the published HuggingFace model card hashes.
6. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) for the general credential rotation playbook.

## Prevention

- **Pin SGLang to ≥ 0.4.6** and verify the version in CI before deploying inference servers.
- **Bind the ZMQ broker to localhost or a private inter-node VLAN**, never to `0.0.0.0` in environments where untrusted hosts can reach the port.
- **Enable network-level authentication** for multi-node inference clusters: use mTLS or a VPN overlay (WireGuard, Tailscale) for inter-node communication rather than relying on network segmentation alone.
- **Treat model files as untrusted binary blobs**: verify SHA-256 against the upstream model card before loading; do not auto-update GGUF files in production without integrity checking.
- **Never expose LLM inference servers directly to the public internet**: place behind an authenticated reverse proxy (nginx + OAuth2 proxy / Caddy + forward-auth).
- More broadly, see the **"AI/data tools shipping unauthenticated network RCE" cluster** in [advisories/2026-04-flowise-rce-cluster.md](2026-04-flowise-rce-cluster.md) — SGLang joins Langflow, PraisonAI, Marimo, Flowise, and LiteLLM as named instances of the same operational mistake.

## Sources

- [The Hacker News — Critical SGLang Vulnerabilities Allow Attackers to Execute Arbitrary Code](https://thehackernews.com/2026/03/critical-sglang-vulnerabilities-allow.html)
- [Snyk — SGLang CVE-2026-3059: Pickle Deserialization Remote Code Execution](https://snyk.io/vuln/SNYK-PYTHON-SGLANG-CVE-2026-3059)
- [Snyk — SGLang CVE-2026-3060: ZMQ Broker Remote Code Execution](https://snyk.io/vuln/SNYK-PYTHON-SGLANG-CVE-2026-3060)
- [NVD — CVE-2026-3059](https://nvd.nist.gov/vuln/detail/CVE-2026-3059)
- [NVD — CVE-2026-5760](https://nvd.nist.gov/vuln/detail/CVE-2026-5760)
- [GitHub Advisory — SGLang unsafe pickle deserialization (GHSA)](https://github.com/advisories)
