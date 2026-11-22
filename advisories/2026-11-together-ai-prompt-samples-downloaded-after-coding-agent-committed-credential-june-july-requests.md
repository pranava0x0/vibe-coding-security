---
id: 2026-11-together-ai-prompt-samples-downloaded-after-coding-agent-committed-credential-june-july-requests
title: "Together AI: stored prompt samples from June and July 2026 downloaded after a coding agent committed a credential to a public repository"
date_disclosed: 2026-11-21
last_updated: 2026-11-22
severity: high
status: contained
ecosystems: [inference-providers, llm-api, openrouter, huggingface, github]
tools_affected: ["Together AI serverless inference requests to MiniMax M3, GLM-5.2 and Kimi K2.6, primarily 2026-06-24, 2026-07-04, 2026-07-08 and 2026-07-14", "requests routed to Together AI by OpenRouter for those models", "coding agents and pipelines that send credentials in prompts"]
tags: [inference-provider, prompt-exposure, breach, credentials-in-prompts, coding-agent-committed-secret, secret-in-public-repo, zero-data-retention, vendor-incident]
---

## TL;DR

[Together AI](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026) says an unauthorized party downloaded stored prompt samples from its serverless inference service. The samples came from requests to MiniMax M3, GLM-5.2 and Kimi K2.6 in June and July 2026. The party searched them for credentials and tested those credentials. Rotate any secret you sent in a prompt to those models on Together in that period.

## What happened

Together published the notice on 2026-11-21, signed by its CEO. Single source: the vendor, for its own service.

- Together collected prompt samples for software testing and stored them in a private Hugging Face repository. It says the samples were "authorized for that use".
- The samples came from requests to MiniMax M3, GLM-5.2 and Kimi K2.6, "primarily on June 24, July 4, July 8, and July 14, 2026".
- "During development of our public GitHub repository, xorl, an AI coding agent committed a credential that provided access to the private Hugging Face repository."
- Together says its scanning detected the credential and it reverted the commit. An unauthorized party obtained the credential "during the exposure window" and downloaded the samples.
- The party "searched those samples for credentials to other services and tested whether those credentials were valid".
- "Five of the credentials tested were canary credentials associated with a Dragos security experiment."

Together says it has "not identified evidence of additional prompt leakage beyond this incident". Its review of the sample contents continues, and it will contact affected customers directly.

The notice does not give the date of the commit, the length of the exposure window, the number of samples, or the number of customers. It does not say whether requests with Zero Data Retention enabled were sampled.

[The Hacker News](https://thehackernews.com/2026/11/openrouter-drops-3-providers-after.html) reports on 2026-11-22 that the company "has no reason to believe the data went further" and "understands it has been deleted". Those two statements are not in the notice as read on 2026-11-22.

[OpenRouter](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/) lists the notice among provider security announcements and says it notified all potentially affected customers. The [Dragos study](2026-11-dragos-canary-study-three-ai-providers-breached-phala-minimax-prompts-read.md) names no provider. No source says Together is one of the three breached providers Dragos counts.

## Am I affected?

| Route | Window | Action |
|---|---|---|
| Together AI serverless inference, MiniMax M3, GLM-5.2 or Kimi K2.6 | June and July 2026, primarily 06-24, 07-04, 07-08, 07-14 | rotate every secret that appeared in those prompts |
| The same models reached through OpenRouter with Together as the provider | same | same |

- Check your Together usage logs or your router's request logs for those models and dates.
- Search agent transcripts from that period for API keys, tokens and passwords. A coding agent sends what it reads, including `.env` contents.
- Together says it will contact affected customers. The absence of a notice is not yet a clear result, because its review is not finished.

## If you are affected

1. Rotate every credential that appeared in a prompt or tool result sent on that route. Together states the downloaded samples were searched for credentials and that those credentials were tested.
2. Review the accounts behind those credentials for use you do not recognise since June 2026. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
3. Together advises customers handling sensitive prompts to enable Zero Data Retention in account settings. Together made it the default for new accounts.
4. Questions go to the address in the notice.

## Prevention

- Keep credentials out of model context. See [credential hygiene](../prevention/credential-hygiene.md).
- The exposed credential was committed by a coding agent to a public repository. Scan every commit and pull request for secrets before it reaches a public remote, and give agents scoped, short-lived tokens. Together lists both as changes it made. See [CI/CD hardening](../prevention/ci-cd-hardening.md).
- Ask a provider whether it samples prompts for testing and where it stores them. Retention settings differ per account and per provider.
- Related: [Fireworks AI](2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure.md) and [the Dragos canary study](2026-11-dragos-canary-study-three-ai-providers-breached-phala-minimax-prompts-read.md).

## Sources

- [Together AI: Security event: Prompt leakage for requests in June and July of 2026](https://www.together.ai/blog/security-event-prompt-leakage-for-requests-in-june-and-july-of-2026): Vipul Ved Prakash, published 2026-11-21, read 2026-11-22. Every quoted sentence, the models, the dates, the changes.
- [OpenRouter: Data Processing Incidents on Inference Providers](https://openrouter.ai/blog/announcements/data-processing-incidents-on-inference-providers/): 2026-11-22. Lists the Together notice and says affected customers were notified.
- [The Hacker News](https://thehackernews.com/2026/11/openrouter-drops-3-providers-after.html): 2026-11-22. The two statements attributed to the company that the notice does not carry.
- [Hacker News item 50595816](https://news.ycombinator.com/item?id=50595816): 2026-11-22, 37 points when read. Where the notice surfaced.
- Not opened: the `xorl` repository and its commit history.
