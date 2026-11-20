---
id: 2026-11-prime-intellect-deepseek-v4-1-flash-endpoint-served-modified-weights-november-8-to-10
title: "Prime Intellect: an unauthorised party swapped a DeepSeek v4.1 Flash deployment to weights modified to reduce or remove refusals, 2026-11-08 to 2026-11-10 (PI-SA-2026-001)"
date_disclosed: 2026-11-19
last_updated: 2026-11-20
severity: medium
status: contained
ecosystems: [inference-providers, llm-api, open-weight-models]
tools_affected: ["Prime Inference endpoint deepseek/deepseek-v4.1-flash, 2026-11-08 01:24 UTC to 2026-11-10 06:35 UTC", "applications and agents that relied on that model's refusals during the window"]
tags: [inference-provider, model-substitution, incident, vendor-bulletin, open-weight, guardrails]
---

## TL;DR

[Prime Intellect's notice PI-SA-2026-001](https://primeintellect.one/security/advisories/deepseek-v4-1-flash-model-substitution) says an unauthorised party replaced a deployment behind its `deepseek/deepseek-v4.1-flash` endpoint with a copy "modified to reduce or remove refusal behavior". The swap lasted from 2026-11-08 01:24 UTC to 2026-11-10 06:35 UTC. The vendor says no keys, customer credentials or other models were affected, and that it found no evidence prompts or completions left the cluster. If your application relied on the model refusing, review its outputs from that window.

## What happened

The notice was published on 2026-11-19, nine days after the window closed. It states:

- The replacement was a publicly available abliterated copy of the same model. The chat template, tokenizer and serving configuration were not changed.
- Capability benchmarks were unaffected in the vendor's tests.
- Refusals fell from 98 of 100 prompts to 1 on JailbreakBench, from 304 of 313 to 2 on StrongREJECT, and from 198 of 240 to none on HarmBench.
- All affected customers have been contacted.
- The vendor found "no evidence that prompts or completions were recorded or left our deepseek/deepseek-v4.1-flash serving cluster, and no evidence of access beyond it".
- "No keys or customer credentials were affected."
- "Our investigation is ongoing."

The notice does not say how the party got access to the serving cluster. It mentions an "attacker's proxy" on the nodes and says none of its versions reads or transfers request content.

This file rates it `medium` because the vendor reports no data or credential exposure. The status is `contained` because the investigation is open.

## Am I affected?

- You called `deepseek/deepseek-v4.1-flash` through Prime Inference between 2026-11-08 01:24 UTC and 2026-11-10 06:35 UTC.
- The notice says no other models on the platform were modified. It says nothing about other providers of the same model.
- Only requests served by the replaced deployment were answered by the modified model. The notice does not say what share of requests that was.
- Check your request logs for that model and window. The vendor says it keeps no request logs.

## If you are affected

1. Review outputs from the window wherever your application depended on the model declining a request. Moderation, user-facing chat and agent tool gating are the cases to check first.
2. Re-run any safety evaluation that used the endpoint during the window.
3. No key rotation is requested by the vendor. Rotating the Prime Intellect API key is this file's suggestion while the investigation is open.

## Prevention

- Do not use a model's refusals as the only control. Put input and output checks in your own code.
- A hosted open-weight model can change without the model name changing. Run a small fixed set of refusal and behaviour probes against each provider on a schedule and alert on a shift.
- See [credential hygiene](../prevention/credential-hygiene.md) for provider key scoping.

## Sources

- [Prime Intellect: Notice regarding deepseek/deepseek-v4.1-flash, 8 to 10 November 2026 (PI-SA-2026-001)](https://primeintellect.one/security/advisories/deepseek-v4-1-flash-model-substitution): published 2026-11-19, read 2026-11-20. Window, benchmark counts, quoted statements.
- Single source: the vendor. Found through [Hacker News item 50573737](https://news.ycombinator.com/item?id=50573737), 3 points when read.
