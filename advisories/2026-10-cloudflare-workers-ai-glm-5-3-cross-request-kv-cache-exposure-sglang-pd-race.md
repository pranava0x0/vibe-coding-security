---
id: 2026-10-cloudflare-workers-ai-glm-5-3-cross-request-kv-cache-exposure-sglang-pd-race
title: "Cloudflare Workers AI GLM-5.3 returned other customers' prompt data in 155 responses (Aug 27 to Sep 9); SGLang PD race fixed 0.5.21 to 0.5.23"
date_disclosed: 2026-10-26
last_updated: 2026-10-27
severity: high
status: patched
ecosystems: [cloudflare, workers-ai, inference-hosting, sglang, llm-serving]
tools_affected: ["Cloudflare Workers AI @cf/zai-org/glm-5.3 (requests above 681,280 tokens, 2026-08-27 to 09-09)", "self-hosted SGLang in prefill/decode disaggregation with Mooncake, NIXL, MORI or a custom KV transfer backend, v0.4.x up to but not including v0.5.21 (v0.5.22 for MORI)"]
tags: [cross-tenant, data-exposure, kv-cache, inference-platform, sglang, cloudflare, hosted-inference, disclosure-delay, no-cve]
---

## TL;DR
Between 2026-08-27 and 09-09, Cloudflare's hosted GLM-5.3 model on Workers AI served 155 responses that contained data from other customers' requests made shortly before, because the prefill KV-cache pool was smaller than the context window and an SGLang race let over-length requests decode over stale cache pages (Cloudflare, 2026-10-26). Cloudflare says no other Workers AI model was affected and customers need take no action; anyone running SGLang's prefill/decode disaggregation themselves is exposed to the same race until v0.5.21, v0.5.22 for MORI, with no error or log line to show it happened.

## What happened

**The hosted side (Cloudflare).** A researcher reported through HackerOne on 2026-09-08 that responses from `@cf/zai-org/glm-5.3` could carry another request's content. Cloudflare took the model private on 09-09, restored it that evening, and published the write-up on 10-26, seven weeks later. Its status page for 09-09 records the event only as "Cloudflare Workers AI increased errors when using GLM 5.3", investigating 14:25 UTC, identified 15:02, resolved 20:09. The post states the window as 2026-08-27 to 09-09, 155 affected responses, "a small number of customers", all affected requests longer than 681,280 tokens, no evidence of deliberate exploitation, and no other model affected. Root cause as Cloudflare states it: the GLM-5.3 prefill KV cache pool was smaller than the model's context window, and an SGLang bug caused over-length requests to be handled as if they had valid KV cache data, so decode attended over stale pages from earlier requests. Remediation: the pool was raised to about 2.04 million tokens, roughly twice the context length; SGLang was patched so rejected requests return an error before any KV transfer; deployment checks were added across production. The post does not say what kinds of data the 155 responses carried.

**The self-hosted side (SGLang).** The SGLang team's coordinated post the same day describes the general bug: in prefill/decode (PD) disaggregation with an asynchronous KV transfer backend, a request that aborts mid-transfer (client disconnect, timeout, transport fault) has its decode-side slots freed while prefill's already-launched RDMA writes can still land, so those writes overwrite another request's cache and corrupt its output silently. Three conditions must all hold: PD disaggregation with a transfer backend (Mooncake, NIXL, MORI or custom); a request terminating mid-transfer; and the allocator reusing the freed slots before the writes land, which the team says can happen within milliseconds under memory pressure. Single-instance deployments without cross-engine transfer are not affected. A second variant needs decode-side hierarchical cache offload, which is off by default. Affected: default PD configurations from the v0.4.x line (early 2025) up to but not including v0.5.21, up to but not including v0.5.22 for MORI; the post phrases it as "until v0.5.21" and names those as the fix versions. Fixes: v0.5.21 protects Mooncake and NIXL by default; MORI support and generation-tagged acknowledgments in v0.5.22; failed Mooncake sends stop acknowledging as drained in v0.5.22, failed NIXL and MORI sends in v0.5.23. The fix line is not backported to earlier release branches. The team notes long-context workloads widen the race window, that a client can raise the odds by disconnecting mid-transfer, and that the client cannot choose the victim or the landing slots.

**Why it is here.** A hosted inference API is the component a vibe-coded app trusts with its prompts, and the prompts carry the user's data. The corpus already tracks hosted gateways that leak keys; this is the model host leaking request content between tenants, disclosed with the vendor's statement that affected customers were few and need not act, and with no CVE on either side.

## Am I affected?

- **Workers AI customer.** Only if your app called `@cf/zai-org/glm-5.3` between 2026-08-27 and 2026-09-09 with prompts above 681,280 tokens. Cloudflare says it confirmed no other model was affected and states no customer action. The post does not say whether affected customers were notified individually; ask Cloudflare support if your logs show requests in that range.
- **Self-hosted SGLang.** Affected if you run PD disaggregation with Mooncake, NIXL, MORI or a custom KV transfer backend on any version below 0.5.21 (0.5.22 for MORI). Corruption leaves no error or log entry, so the SGLang team says operators cannot reliably tell whether exposure already occurred.

```bash
python -c "import sglang; print(sglang.__version__)"
# PD mode is the exposure; a single-instance server is not affected by this race
```

## If you are affected

1. SGLang operators: upgrade to v0.5.21 or later, v0.5.22 or later for MORI. On v0.5.19 or v0.5.20, set `SGLANG_DISAGGREGATION_DEFERRED_DECODE_KV_RELEASE=1` on both prefill and decode servers as the interim. Run a router that cancels both halves of a PD pair on abort (`sgl-router` in PD mode). Check that pool capacity matches the configured context length. After rollout, watch `sglang:decode_deferred_kv_release_total{outcome}`; a high share of timeout outcomes means the acknowledgment path needs attention. `--disaggregation-enable-kv-checksum` on both engines detects some late writes at a GPU cost and is off by default.
2. Workers AI customers in the window: treat the prompt and response content of those requests as possibly seen by another tenant, and decide on notification by what the prompts held. [If your webapp was compromised](../playbooks/if-your-webapp-was-compromised.md) covers the user-data side.

## Prevention

- Keep per-request secrets out of prompts sent to any shared inference endpoint; a cross-request leak at the host is outside your controls. [Credential hygiene](../prevention/credential-hygiene.md).
- For self-hosted serving, treat the KV-cache allocator as a tenant boundary and test abort paths under load before enabling disaggregation.

## Sources
- [Cloudflare — Cross-request KV cache exposure in the GLM-5.3 Workers AI model, and our remediation with SGLang](https://blog.cloudflare.com/kv-cache-exposure-remediation/) — fetched 2026-10-27: published 2026-10-26, report 09-08, model private and restored 09-09, window 08-27 to 09-09, 155 responses, the 681,280-token threshold, no other model affected, the root cause and the three remediation steps, no customer action.
- [Cloudflare Status — Cloudflare Workers AI increased errors](https://www.cloudflarestatus.com/incidents/jsvvrtk5hvym) — fetched 2026-10-27: 2026-09-09 investigating 14:25 UTC, identified 15:02, resolved 20:09; the page names only increased errors.
- [SGLang — SGLang security update: improving request isolation](https://www.lmsys.org/blog/2026-10-26-cf-security) — fetched 2026-10-27: 2026-10-26, the PD-disaggregation race, the three conditions, affected v0.4.x through v0.5.21 (v0.5.22 MORI), the fix versions 0.5.21 to 0.5.23, the environment-variable interim, the router, checksum and metric guidance, no backport, the "cannot reliably tell" statement.
