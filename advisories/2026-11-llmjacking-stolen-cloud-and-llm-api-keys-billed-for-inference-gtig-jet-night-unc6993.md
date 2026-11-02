---
id: 2026-11-llmjacking-stolen-cloud-and-llm-api-keys-billed-for-inference-gtig-jet-night-unc6993
title: "LLMjacking: stolen cloud and LLM API keys billed for inference at $100,000 a day; GTIG names Jet Night and UNC6993 (2026-11-02)"
date_disclosed: 2026-11-02
last_updated: 2026-11-02
severity: high
status: ongoing
ecosystems: [aws, azure, google-cloud, llm-api-keys, litellm, ollama, github]
tools_affected: ["any organisation or developer holding Amazon Bedrock, Gemini API, Azure OpenAI or other model-provider credentials, cloud IAM keys, service account keys, GitHub personal access tokens or active session tokens", "self-hosted LiteLLM gateways and publicly exposed Ollama endpoints", "public code repositories that contain provider API keys"]
tags: [llmjacking, credential-theft, api-keys, cloud-credentials, billing-abuse, litellm, ollama, github-pat, session-hijack, gtig, mandiant, threat-intel, ongoing]
---

## TL;DR
Google Threat Intelligence Group and Mandiant report (2026-11-02) a 2026 run of incidents in which stolen cloud identity credentials, LLM API keys, GitHub personal access tokens and hijacked session tokens were used to run inference on the victim's account, with fraudulent charges above $100,000 in a single day and cumulative charges reaching $1 million before access was revoked. One actor, UNC6993, ran a fake application portal to capture active access tokens past password and MFA; another harvested provider keys from public repositories and validated them with `max_tokens=1` requests; one exploited LiteLLM CVE-2026-40217 to turn ordinary virtual keys into administrative credentials; and a resale service called Jet Night pushed over 500,000 API calls in under eight hours onto one victim. Scope every key, set budget caps and alerts, treat unexpected enablement of an LLM service as a critical event, and rotate anything that has touched a public repository.

## What happened

GTIG defines LLMjacking as hijacking enterprise access to large language models through compromised cloud or LLM credentials and running fraudulent inference workloads the victim pays for; unlike cryptojacking, the charges arrive in hours. Mandiant responded to incidents across North America, South America and Asia Pacific in financial services, retail, technology and transportation. The post describes a division of labour: one group obtains access, another ("LLM Mixers") pools stolen credentials behind open-source API gateways, meters usage and resells it through underground storefronts.

**How the keys were obtained, per GTIG.**
- Stolen cloud identity credentials were the dominant vector: IAM credentials, service account keys, GitHub personal access tokens and active session tokens, including a misconfigured service account key on a cloud instance.
- UNC6993 hosted a fake application portal that asked users to paste their active access token, which then bypassed password and MFA controls.
- One actor used cloud federation tokens to mint new access keys, around MFA.
- One actor harvested corporate LLM API keys from public code repositories and validated them with minimal requests (`max_tokens=1`) to stay under volume alerts.
- Actors scanned for publicly exposed model-serving endpoints (Ollama is named) and tested whether they could register their own models.

**Inside the account.** Actors enumerated regions, services, repositories and data stores for more credentials, pulled database passwords and third-party API keys from secret managers, created unauthorized IAM and service accounts, attached administrative policies to service roles, and injected SSH keys into compute instances. GTIG says one actor exploited "a user ID rebind vulnerability in the LiteLLM gateway (CVE-2026-40217) to turn standard virtual keys into full administrative credentials"; that id is the third link of the Obsidian Security chain recorded in [the LiteLLM file](2026-04-litellm-sql-injection.md), which describes it as the Custom Code Guardrail `exec()` path, so the two descriptions of the same id differ and both are printed here.

**The bill.** UNC6993 generated additional API keys and enabled services in victim projects, accumulating over $100,000 in charges. One actor created and deleted short-lived service accounts to dodge rate limits while watching the billing console. The Jet Night token-routing service made over 500,000 API calls in under eight hours, passing nearly $1 million in token costs to a victim; it sold unlimited plans at about $60 a month against typical market rates of $100 to $250, which GTIG reads as evidence it runs on stolen keys, and its advertised outages line up with key revocations. The Register (2026-11-02) carries the same figures and adds CrowdStrike's August 2026 report of about 200,000 API requests in two minutes in another case.

**Why this corpus files a threat report.** The victim here is whoever holds the key, which is every reader of this repository, and the exposure path is the one these advisories keep recording: a provider key in a repository, a `.env` or a hosted platform's secret store ([Railway](2026-10-railway-environment-variable-store-breach-rotate-every-secret.md), [Northflank](2026-10-northflank-security-incident-assume-all-environment-variables-decrypted-ai-keys-abused.md), [OpenCode Console](2026-10-opencode-console-legacy-system-breach-provider-api-keys-exposed-distillation-attack.md)), and a self-hosted gateway that holds every provider key at once. `status: ongoing` because GTIG expects the practice to displace cryptojacking and the resale market is operating; `severity: high` because the loss is money and access, not code execution on the reader's machine. Single primary (the vendor's threat-intelligence post) with one outlet; the IOC collection GTIG publishes is behind a login and is not reproduced here.

## Am I affected?

- **Billing.** Look for a step change in model-provider or cloud AI spend, for LLM services enabled in projects where you never enabled them, and for new API keys you did not create. GTIG: treat any unauthorized enablement of an LLM service as a critical security event.
- **Audit logs.** AWS CloudTrail for `bedrock.amazonaws.com`: `InvokeModel`, `InvokeModelWithResponseStream`, `Converse`, `ListFoundationModels`, `PutUseCaseForModelAccess`, `CreateFoundationModelAgreement`, and any change to model invocation logging. Azure Activity and Diagnostic Logs for `Microsoft.CognitiveServices`: `accounts/deployments/write` and high volumes of completion requests. Google Cloud Audit Logs: `ServiceUsage.EnableService` for `aiplatform.googleapis.com`, `GenerateContent` and `StreamGenerateContent` (Data Access logs, off by default), and `ListPublisherModels` reconnaissance.
- **Validation sweeps.** Low-volume requests with `max_tokens=1` from unfamiliar clients are the key-validation signature GTIG describes.
- **Your repositories.** Run a secret scanner over every repository you have pushed, public forks included: a key that was ever public is in someone's list.
- **Gateways and endpoints.** A LiteLLM proxy below the fixes in [the LiteLLM file](2026-04-litellm-sql-injection.md), or an Ollama endpoint reachable from the internet, is an entry point GTIG saw used.

## If you are affected

1. Rotate at the provider first: every model-provider key, cloud access key and GitHub token the compromised account or repository could have exposed, then revoke active sessions and federation tokens. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
2. Remove the persistence GTIG describes: unauthorized IAM users and service accounts, administrative policies attached to service roles, SSH keys added to instances or instance metadata, and any LLM service or deployment you did not create.
3. Set spending caps and budget alerts on every provider and project, and open a billing dispute with the provider for the fraudulent inference.
4. Patch the gateway: upgrade LiteLLM past CVE-2026-40217 and the later advisories in its file, and take Ollama and other model servers off the public internet.

## Prevention

- Scope keys by model, environment and spend limit so a leaked utility key cannot invoke frontier models; set budget alerts and quotas before the key exists: [credential hygiene](../prevention/credential-hygiene.md).
- Phishing-resistant MFA on every console and developer platform, so a pasted session token is worth less; no long-lived keys in repositories, `.env` files or hosted secret stores without an issuer-side inventory that lets you rotate in one pass.
- Enable Data Access logging for model invocation on Google Cloud and Diagnostic Logs on Azure, and alert on LLM service enablement and logging changes.
- Treat the gateway that holds your provider keys as production infrastructure: patch it, authenticate it, meter it. [Supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources
- [Google Cloud Threat Intelligence — The Rise of LLMJacking: How Threat Actors Monetize Compromised Cloud and Model Resources](https://cloud.google.com/blog/topics/threat-intelligence/llmjacking-monetizing-compromised-cloud-models) — fetched 2026-11-02: 2026-11-02, GTIG and Mandiant (nine named authors); the definition, the access vectors, UNC6993's token-capture portal, the `max_tokens=1` validation, CVE-2026-40217, the $100,000-a-day and $1 million figures, Jet Night's 500,000 calls and $60 plans, the AWS, Azure and Google Cloud detection events, the mitigation list; IOCs behind a GTI login and not reproduced.
- [The Register — Token thieves costing companies $100K+ per day in illicit LLM charges](https://www.theregister.com/security/2026/11/02/token-thieves-costing-companies-100k-per-day-in-illicit-llm-charges/5306967) — fetched 2026-11-02: 2026-11-02, Jessica Lyons; the Mandiant and GTIG figures, UNC6993, Jet Night, the fake application portal, the burn-and-rotate service accounts, CrowdStrike's August 2026 report of about 200,000 requests in two minutes.
- [Google Cloud Threat Intelligence — blog index](https://cloud.google.com/blog/topics/threat-intelligence) — fetched 2026-11-02: the post listed second, undated on the index.
- Related in this corpus: [LiteLLM proxy pre-auth SQL injection and the Obsidian Security chain (CVE-2026-40217)](2026-04-litellm-sql-injection.md), [Railway environment-variable store breach](2026-10-railway-environment-variable-store-breach-rotate-every-secret.md), [infostealers target coding-agent tokens, MCP configs and prompt histories](2026-09-infostealers-target-coding-agent-tokens-mcp-configs-prompt-histories.md).
