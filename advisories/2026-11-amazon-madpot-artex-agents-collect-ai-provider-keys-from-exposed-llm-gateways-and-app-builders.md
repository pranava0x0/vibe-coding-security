---
id: 2026-11-amazon-madpot-artex-agents-collect-ai-provider-keys-from-exposed-llm-gateways-and-app-builders
title: "Amazon: automated campaigns collect AI provider keys from internet-exposed LiteLLM, One API, Dify, Langflow and RAGFlow instances"
date_disclosed: 2026-11-13
last_updated: 2026-11-16
severity: high
status: active
ecosystems: [llm-gateway, self-hosted, pypi, docker, cloud]
tools_affected: ["LiteLLM proxy with the default master key", "Langflow before 1.3.0 (CVE-2025-3248)", "RAGFlow 0.24.0 and earlier (CVE-2026-28797)", "One API, New API, Veloera, Sub2API", "Dify, FastGPT, Open WebUI, LobeChat, Ollama reachable from the internet", "any gateway or app builder that stores model provider keys"]
tags: [threat-report, llm-gateway, provider-keys, default-credentials, exposed-instance, litellm, langflow, ragflow, dify, amazon, key-rotation]
---

## TL;DR
Amazon Threat Intelligence reports that, from 2026-10-03 to 2026-11-05, its decoy sensors recorded automated campaigns that looked for internet-exposed LLM gateways and AI app builders and collected the model provider keys stored in them. The named weaknesses are the LiteLLM default master key, CVE-2025-3248 in Langflow, CVE-2026-28797 in RAGFlow and an authentication bypass in One API family systems. If you self-host any product in the list below and it is reachable from the internet, change default credentials, patch, and rotate the provider keys it holds.

## What happened

Amazon's post is dated 2026-11-13 and signed by CJ Moses. It says the records come from MadPot, its network of decoy sensors, and that the campaigns were run with agents built on ARTEX, an open-source penetration-testing tool. Amazon "assesses with moderate confidence that ARTEX was used for these campaigns" and attributes the activity, also with moderate confidence, to "disparate Chinese-nexus threat groups". It adds that it "did not observe that activity as it happened and cannot verify the outcomes the agents reported". The decoys recorded what the agents did and claimed. They do not show how many real deployments lost keys.

**Products Amazon names as targets.**

| Category | Products, in Amazon's words | Weakness Amazon names |
|---|---|---|
| "LLM gateways and proxy platforms" | One API, New API, Veloera, Sub2API, LiteLLM | "the LiteLLM default master key"; an authentication bypass "in One API family systems", no CVE given |
| "AI application builders" | Dify, FastGPT, Langflow, RAGFlow, Open WebUI, LobeChat, Ollama | CVE-2025-3248 (Langflow); CVE-2026-28797 (RAGFlow) |

Amazon gives no versions. The version facts below come from other records.

| Id | Record | Affected | Fix |
|---|---|---|---|
| CVE-2025-3248 | tracked here in [2026-09-langflow-cve-2026-0768-validate-code-rce-exploited.md](2026-09-langflow-cve-2026-0768-validate-code-rce-exploited.md) | The Hacker News: Langflow before 1.3.0 | The Hacker News: 1.3.0. In CISA KEV since 2025-05-05 per the same article. |
| CVE-2026-28797 | GitHub CNA, published 2026-04-03. CVSS 4.0 8.7. CISA-ADP 8.8 under CVSS 3.1. | "versions 0.24.0 and prior". An authenticated user can run operating-system commands. | The record says "At time of publication, there are no publicly available patches." The Hacker News writes that 0.25.0 contains the fix. That release was not opened in this run. |

Being named as a target is not a vulnerability in the product. For Dify, FastGPT, Open WebUI, LobeChat, Ollama, New API, Veloera and Sub2API, Amazon names no flaw. The exposure is an instance on the internet that holds keys.

**Credential categories.** The Hacker News's account of the post lists model provider API keys stored in gateways and app builders, default or hard-coded administrator credentials, cloud credentials with a preference for managed model services and secret stores, keys left in code, public files, client-side JavaScript, container images and package repositories, and Cloudflare account-level API tokens.

**A second report the same week.** StepSecurity's 2026-11-12 post on the same tool cites Microsoft, CrowdStrike, CERT-In, Unit 42 and WorkOS reports, and does not cite Amazon. Its entry points are leaked secrets in public code, development credentials that work in production and long-lived tokens. It adds one item for teams that run the tool themselves: it says a backdoored Docker image of ARTEX circulated, citing a 2026-11-04 analysis by BadByte that was not opened in this run. Related files here: [the WorkOS incident](2026-11-workos-october-30-internal-sales-tool-incident-crm-support-slack-excerpts-phishing-risk.md) and [stolen keys billed for inference](2026-11-llmjacking-stolen-cloud-and-llm-api-keys-billed-for-inference-gtig-jet-night-unc6993.md).

`status` is `active`: the observation window ended eleven days before this file and nothing says the activity stopped. `severity` is `high` because a gateway holds every provider key behind it.

## Am I affected?

- You run LiteLLM, One API, New API, Veloera, Sub2API, Dify, FastGPT, Langflow, RAGFlow, Open WebUI, LobeChat or Ollama, and the instance answers on a public address.
- Your LiteLLM proxy still uses the master key from an example configuration, or a key you never changed after setup.
- Your Langflow is older than 1.3.0, or your RAGFlow is 0.24.0 or older.
- An install was started and never finished, and its setup page is still reachable.
- A provider's usage page shows spend or request volume you cannot explain.

## If you are affected

1. Take the instance off the public internet or put authentication in front of it.
2. Change every default or shared administrator credential. Finish or remove unfinished installs.
3. Upgrade Langflow and RAGFlow to their current releases.
4. Rotate every model provider key and cloud credential the instance stored, at the provider. Deleting the key from the instance does not revoke it.
5. Review provider usage and billing for the period since 2026-10-03. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
6. Search configuration files, environment variables, CI settings and databases for embedded secrets, as Amazon recommends.

## Prevention

- Amazon's summary: default or hard-coded credentials, exposed keys, unauthenticated endpoints and unpatched software. "Getting those fundamentals right remains the most effective defense."
- Run gateways and app builders under the same controls as other production systems. Set spend limits and alerts on every provider key.
- See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) and [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md).

## Sources

- [Amazon Threat Intelligence observes threat actors running cybercrime campaigns with ARTEX AI agents](https://aws.amazon.com/blogs/security/amazon-threat-intelligence-observes-threat-actors-running-cybercrime-campaigns-with-artex-ai-agents/), 2026-11-13, fetched 2026-11-16: the window, the product lists, the named weaknesses, the confidence and verification statements, the recommendations.
- [The Hacker News: Amazon Uncovers AI Agent Campaign Targeting LiteLLM, Dify, and Other Apps for API Keys](https://thehackernews.com/2026/11/amazon-uncovers-ai-agent-campaign.html), 2026-11-16, fetched 2026-11-16: the version lines for both CVEs, the KEV date, the credential categories.
- [StepSecurity: ARTEX: Attackers Adopted This AI Pentesting Tool in Three Months](https://www.stepsecurity.io/blog/artex-ai-pentesting-tool-attackers-leaked-secrets), 2026-11-12, fetched 2026-11-16: the entry points, the reports it cites, the Docker image note.
- [CVE-2026-28797 (GitHub CNA)](https://cveawg.mitre.org/api/cve/CVE-2026-28797), published 2026-04-03, fetched 2026-11-16: the range, both scores, the no-patch sentence.
- Hacker News item 50512675, seen 2026-11-16 through the Algolia feed, 5 points. The item page was not opened.
- Not opened: the indicator lists Amazon and others published, the BadByte analysis, the RAGFlow releases page, any vendor statement from the named products.
