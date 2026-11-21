---
id: 2026-11-dragos-canary-study-three-ai-providers-breached-phala-minimax-prompts-read
title: "Dragos canary study: prompts stolen at three AI inference providers, read by marketplace resellers and fetched despite Zero Data Retention; Phala and MiniMax notices"
date_disclosed: 2026-11-19
last_updated: 2026-11-21
severity: high
status: active
ecosystems: [inference-providers, llm-api, ai-gateways, openrouter, open-weight-models]
tools_affected: ["requests routed by OpenRouter to Phala's DeepSeek V4 Flash 0731 deployment, 2026-10-21 00:00 UTC to 2026-11-08 05:35 UTC", "requests to MiniMax models through MiniMax, Novita, AtlasCloud or StreamLake, July to October 2026", "coding agents and pipelines that send credentials in prompts through AI routers or reseller marketplaces", "Phala confidential VMs whose owner received a notice"]
tags: [inference-provider, prompt-exposure, breach, zero-data-retention, ai-router, canary-tokens, credentials-in-prompts, vendor-incident, researcher-disclosure]
---

## TL;DR

[Dragos](https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens) sent about two million prompts with unique test secrets to AI services from July to November 2026. It reports that attackers were stealing data from three hosting providers, and names none of them. [Phala](https://phala.com/posts/phala-november-preliminary-incident-report) has published its own incident, and OpenRouter has emailed users about MiniMax models. Rotate any secret that appeared in a prompt sent on the routes below. Stop putting credentials in prompts.

## What happened

Dragos published on 2026-11-19. Each test secret went into exactly one request to one provider. It reports three findings.

1. **Provider breaches.** "We found attackers actively stealing data from three different hosting providers." The earliest dates to mid-July. Dragos says none of the three knew before it told them. In the largest, "a couple hundred" of its AWS keys were taken in late October, including keys in requests the provider rejected. In the other two, some stolen requests were marked Zero Data Retention.
2. **Marketplace resellers.** Sellers on an inference marketplace read prompts through ordinary request logging. People then tried the planted passwords by hand.
3. **Privacy settings not honoured.** A Chinese AI lab's systems fetched the secret URLs from more than half of the prompts sent to its models. That includes about two-thirds of requests marked no data collection or Zero Data Retention. Prompts sent to US providers that resell the lab's models triggered the same fetches.

Dragos says the first provider "has still not publicly disclosed the incident". It says one of the late-October providers "has already published a preliminary security notice".

### Phala's report

Phala's preliminary report is dated 2026-11-10. It says an attacker took control of an inference VM serving DeepSeek V4 Flash 0731, "making in-flight request data visible during processing". Phala says the requests were routed to it by OpenRouter and that it served the model "only through the affected route". A "third-party security researcher" gave it the evidence on 2026-11-08, from canary credentials sent on 2026-10-21 and 10-22. Phala says it contained the incident on 2026-11-08 at 05:35 UTC and that the investigation continues.

The same attacker created unauthorized confidential VMs on two servers and obtained application credentials. Phala confirmed misuse of some stolen credentials belonging to one tenant and says it contacted that tenant.

No source names Phala as one of Dragos's three providers. The canary method, the dates and the notice match.

### OpenRouter's notice about MiniMax

A [Hacker News user](https://news.ycombinator.com/item?id=50585962) posted an email on 2026-11-21 that they say came from OpenRouter. A second user says they received it. OpenRouter has no public page for it. As relayed, it says:

- A researcher's test URLs in prompts sent to MiniMax models from July to October 2026 were accessed by a third party 40 to 130 hours later.
- AtlasCloud, Novita and StreamLake told OpenRouter they forwarded requests for MiniMax models to MiniMax.
- "none of the AWS test keys were used."
- OpenRouter removed the Zero Data Retention label from those endpoints. It asked MiniMax for an account and had not received one.

Dragos does not name the lab in its third finding. The notice's dates and method match it.

## Am I affected?

| Route | Window | Source | Action |
|---|---|---|---|
| OpenRouter to Phala, DeepSeek V4 Flash 0731 | 2026-10-21 00:00 UTC to 2026-11-08 05:35 UTC | Phala | rotate every secret in those requests |
| MiniMax models through MiniMax, Novita, AtlasCloud or StreamLake | July to October 2026 | OpenRouter email, relayed | treat prompts and outputs as read |
| Two more breached providers | mid-July onward, and late October | Dragos, providers unnamed | cannot be checked by name |
| Reseller marketplaces and routers with default provider pools | ongoing | Dragos | treat prompts as readable by each hop |

- Check your router's request logs for the model and provider of each request.
- Search your agent transcripts for secrets. A coding agent sends whatever it reads, including `.env` contents.

## If you are affected

1. Rotate every API key, token and password that appeared in a prompt or tool result on an affected route. Phala asks for this.
2. Review those accounts for use you do not recognise. Dragos saw stolen AWS keys tested within hours, then used to list S3 buckets and search Secrets Manager and Parameter Store. It saw attempts to enable Bedrock models and to add IAM users. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
3. Phala confidential VM owners who received a notice: rotate the KMS-derived secrets it lists.
4. In your router settings, pick the upstream providers yourself and check that a privacy setting changes where requests go.

## Prevention

- Keep credentials out of model context. Dragos: "AI agents will happily send whatever they can read, including credentials." See [credential hygiene](../prevention/credential-hygiene.md).
- A Zero Data Retention flag is a request to the first hop. Dragos's tests show later hops ignoring it.
- Dragos suggests adding a canary credential to the context your agents already send and treating any use of it as an incident.
- Earlier incidents of the same kind: [Fireworks AI](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md) and [router intermediaries](2026-04-llm-router-malicious-intermediary-attacks.md).

## Sources

- [Dragos: Three breaches, endless leaks: Your AI supply chain needs canaries](https://www.dragos.com/blog/ai-supply-chain-security-canary-tokens): HD Moore, 2026-11-19, read 2026-11-21. Method, three findings, quoted sentences.
- [Phala November Preliminary Incident Report](https://phala.com/posts/phala-november-preliminary-incident-report): 2026-11-10, read 2026-11-21. Window, timeline, tenant impact.
- [Hacker News item 50585962](https://news.ycombinator.com/item?id=50585962): 2026-11-21, 27 points when read. The OpenRouter email as posted by a recipient, read through the Algolia items API.
- [Ars Technica](https://arstechnica.com/security/2026/11/a-leaky-ai-supply-chain-is-exposing-secret-user-data-at-an-alarming-rate/): 2026-11-20. Coverage of the Dragos post. Names no breached provider.
- Not found: a public OpenRouter page, a MiniMax statement, or the names of the other two providers.
