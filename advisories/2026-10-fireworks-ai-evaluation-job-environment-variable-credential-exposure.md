---
id: 2026-10-fireworks-ai-evaluation-job-environment-variable-credential-exposure
title: "Fireworks AI incident: internal credentials misused to read evaluation-job environment variables, including customer API keys and third-party tokens (detected 2026-10-06)"
date_disclosed: 2026-10-09
last_updated: 2026-11-11
severity: high
status: active
ecosystems: [ai-inference-platform, api-keys, fireworks-ai, secrets]
tools_affected: ["Fireworks AI accounts that ran evaluation jobs with secrets exposed as environment variables", "Fireworks API keys issued before 2026-10-10", "third-party credentials (model-provider, cloud, database) stored as Fireworks secrets and used in evaluation jobs", "applications that call Fireworks with a key the vendor has since revoked"]
tags: [vendor-incident, credential-exposure, api-keys, inference-platform, secrets-rotation, evaluation-jobs, single-source, active-monitoring]
---

## TL;DR
Fireworks AI, the hosted inference platform many agent and app builders use for open-weight models, says an unauthorized third party used internal Fireworks credentials to read the environment variables of evaluation jobs in "a limited number of customer accounts." Those variables included API keys and tokens customers had stored as secrets. Fireworks detected it on 2026-10-06, notified affected customers on 10-07 and 10-09, rotated employee keys on 10-09, revoked further user keys and service-account tokens on 10-10, and published a bulletin that is still marked "active monitoring." If you got a notice, your Fireworks key is already dead and every third-party credential your evaluation jobs could see needs rotating at its issuer.

## What happened
Fireworks published a security bulletin on the evening of **2026-10-09** (Pacific time) and updated it on **2026-10-10 at 11:16 PDT**. The bulletin's own words: "An unauthorized third party accessed environment variables used in evaluation jobs in a limited number of customer accounts." The access was made with **internal Fireworks credentials**, not with a customer's key, so it is a vendor-side incident rather than a customer misconfiguration ([Fireworks bulletin](https://fireworks.ai/security/bulletins/october-2026-security-incident), fetched 2026-10-11).

Timeline, as the bulletin gives it (all times PDT):

| When | What |
|---|---|
| 2026-10-06 09:00 | Fireworks identified the unauthorized activity and began containment. |
| 2026-10-07 07:00 | Started notifying affected customers. |
| 2026-10-09 16:00 | Rotated Fireworks employee API keys. |
| 2026-10-09 18:00 | Notified the customers identified as affected. |
| 2026-10-09 22:00 | Published the bulletin. |
| 2026-10-10 | Revoked additional Fireworks user API keys and rotated service-account tokens found in a completed credential review. Review and rotation continue. |

What the vendor says was and was not reached:

- **Reached:** environment variables of evaluation jobs in the affected accounts. Fireworks says API keys and tokens stored as secrets "were likely captured in some affected accounts."
- **Not reached, so far:** customer models, datasets and training data inside the Fireworks security perimeter; inference traffic; personal information. Fireworks notes it does not store prompts or outputs by default. Its review of calls made with the exposed credentials is still in progress, so these are interim statements.
- **Attribution:** none. The bulletin says only "an unauthorized third party."
- **Scope:** "a limited number of customer accounts." No count. Customers who received no notice "were not identified as affected so far."

Two details matter for anyone who wires a hosted inference platform into an agent stack. First, the stolen material is **secrets you handed the platform so a job could use them**: model-provider keys, cloud credentials, database URLs, webhook tokens. Revoking the Fireworks key does nothing for those. The bulletin says this directly: removing a stored secret does not invalidate the credential itself. Second, the compromise ran through the vendor's own internal credentials, which is the same shape as the [Coder registry compromise](2026-09-coder-registry-cloudflare-terraform-supply-chain.md) and the [Vercel/Context.ai OAuth breach](2026-04-vercel-context-ai-breach.md): the customer's hygiene was not the control that failed.

**Source note.** This advisory rests on one source, the vendor's own bulletin. On the sweep date no security outlet had covered it, the Hacker News Algolia feed had no story, and web search returned nothing. A vendor's own incident bulletin is the primary record of a vendor incident, so the file is written as confirmed rather than `unconfirmed`, but every number and claim above is Fireworks's and the review was still open when the bulletin was last updated.

## Am I affected?

You are in scope if your Fireworks account ran **evaluation jobs** and those jobs had secrets exposed as environment variables. Checks:

1. **Look for the notice.** Fireworks emailed affected accounts on 2026-10-07 and 2026-10-09. No notice means not identified "so far," not cleared.
2. **Find keys that stopped working on 2026-10-09 or 10-10.** The vendor revoked keys in bulk; an application that began failing Fireworks authentication on those dates was holding a revoked key.

```bash
# Any Fireworks key in your repos, CI or agent configs?
grep -rIn --exclude-dir=node_modules --exclude-dir=.git -E 'fw_[A-Za-z0-9]{20,}|FIREWORKS_API_KEY' . 2>/dev/null
# Claude Code / Cursor / OpenClaw / LiteLLM-style provider configs often carry it too
grep -rIn -i fireworks ~/.claude.json ~/.cursor ~/.openclaw ~/.config/litellm 2>/dev/null
```

3. **List what your evaluation jobs could see.** In the Fireworks console, review every evaluator, evaluation job and dataset for secrets referenced by name. Each one is a credential to rotate at its issuer, regardless of whether Fireworks says it was captured.
4. **Audit for things you did not create.** The bulletin asks customers to check API keys, users, evaluators, training jobs and datasets for unrecognized entries and report them to the vendor.

## If you are affected

1. **Create new Fireworks API keys** and update every application and agent config that used the old ones. Applications holding a revoked key fail authentication until updated.
2. **Rotate every third-party credential your evaluation jobs could read, at the issuer.** Cloud keys: [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). GitHub tokens: [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md). npm tokens: [playbooks/if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md). Model-provider keys (Anthropic, OpenAI, Google, OpenRouter) at each provider's console. Rotate even if you see no suspicious use; the vendor's review of calls made with exposed credentials was still running.
3. **Review access logs at each issuer** for the window from 2026-10-06 back to whenever the secret was first set on a job. Fireworks offers secret names and credential fingerprints through a secure channel to help scope this.
4. **Report unrecognized keys, users, evaluators or jobs** to security@fireworks.ai.

## Prevention

- **Treat secrets handed to a hosted job runner as shared with the vendor.** Use short-lived, narrowly scoped credentials for evaluation and training jobs, never a provider key that also runs production. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- **Give an inference platform its own provider keys.** A Fireworks job should not hold the same Anthropic or OpenAI key your agents use; one revocation should not take down everything.
- **Inventory where provider keys live.** Agent configs, MCP configs and CI are the usual places a Fireworks key ends up beside everything else: [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md).
- **Watch the vendor's bulletin page.** Fireworks publishes incidents at `fireworks.ai/security/bulletins/`; the status was "active monitoring" when this was written, and the review of credential use was open.

## Update 2026-11-09: a second bulletin widens the data scope and reports further access on 2026-10-24 through a third-party cloud provider

Fireworks published "Update on October 2026 security incident" as a second page on its bulletins index, last updated 2026-11-09, status still "Active monitoring". The first bulletin's page is unchanged since 2026-10-10, so a reader who re-opens only that URL sees nothing new.

**Scope, then and now.** The update says that at the time of the October bulletin "only Fireworks stored secrets (e.g. used in evaluation jobs) were known to have been accessed." It now lists account and billing information as affected, and for a limited set of accounts, secrets, datasets and incomplete models. Resource metadata: identifiers, display names, descriptions and creation times. Billing: addresses, invoice and payment history, account balance and credit usage. "Payment card numbers are not stored by Fireworks and were not impacted." For certain customers, a subset of incomplete model weights and datasets was accessed. Fireworks says it detected no impact to Inference, Training SDK or Nexus, which it describes as zero data retention by default. No count of affected accounts is given.

**Further activity.** On 2026-10-23 a third-party cloud provider that hosted Fireworks research and development machines "experienced a security incident". On 2026-10-24 an unauthorized third party "used it to reach Fireworks development machines" and ran an unauthorized workload that caused additional customer data impact; Fireworks says it detected this the same day, and that as of 2026-10-25 "we have not detected further evidence of successful unauthorized access" to the platform customers use. The bulletin does not name the provider and does not say whether this was the same actor as the October access. This file does not guess the provider.

**Actor and root cause.** The update links the incident to a financially motivated group that sells LLM tokens obtained through unauthorized access, the pattern this corpus tracks as [LLMjacking](2026-11-llmjacking-stolen-cloud-and-llm-api-keys-billed-for-inference-gtig-jet-night-unc6993.md). It still does not say how the internal credentials were first obtained.

**What changed for customers.** Fireworks says it is notifying impacted customers with recommended actions. The page lists none beyond replying to the notification or writing to the security address in the bulletin. Self-serve dataset uploads and downloads for Batch Inference and dataset-based training are disabled during the investigation. Hardening listed: credentials and service accounts revoked and replaced, elevated privileges removed, network pathways restricted, storage and analytics access tightened, logging secured.

**Headlines.** A Hacker News item on 2026-11-09 carries the title "Fireworks AI Hacked" and links a Bloomberg article whose URL slug reads "notifies customers of its second hack in weeks"; a commenter cites The Information on exposed model weights and datasets. Neither article was opened (paywalls). The vendor's page describes one incident with further activity, in one update, and this file follows the vendor's framing while recording the outlets' as theirs.

**For readers.** The first bulletin's rotation advice stands. Add: if you uploaded datasets or ran fine-tuning on Fireworks before 2026-10-25, treat those datasets and any partial model weights as possibly disclosed until your notification says otherwise, and review what the datasets contain (customer records, prompts, internal documents). Billing addresses and invoice history are phishing material. Expect invoices and "account suspended" mail that looks right. Status stays `active`: the investigation is open and the vendor's status line is unchanged.

## Update 2026-11-11: Notion names Fireworks as the vendor behind exposed Notion AI chat transcripts, fewer than 1% of workspaces

Notion published a help-centre notice, "Security incident involving a third-party AI vendor". The page carries no publication date. A Hacker News item linked it on 2026-11-10 (164 points). The page does not date the Fireworks incident or link a Fireworks bulletin. This file reads it as the incident tracked here because the vendor, the data type and the 2026-11-03 disconnection fit, and that link is this file's inference.

**What Notion says.** "One of our vendors, Fireworks AI, notified us of a security incident impacting fewer than 1% of Notion workspaces." The exposed data is chat transcripts: any input to or output from the model written to the chat. Three uses are named: Notion AI chat content, the Insights feature, which used Fireworks for classification, and the Learning and Early Access Program, where volunteered data was used to experiment with training task-specific models. AI Meeting Notes data was not affected unless it was used as input in a Notion AI chat. The page gives no time window and no row count.

**What Notion did.** "As of November 3rd" it disconnected its systems from Fireworks and stopped sending data. It deleted the data in the Fireworks system, halted all training runs, disabled Insights and stopped serving open-weight models through Fireworks. It says it is auditing critical vendors for data minimization and zero data retention.

**What this adds to the Fireworks bulletins.** Fireworks' 2026-11-09 update said datasets and incomplete model weights were accessed for certain customers and named none. If it is the same incident, Notion's notice shows what such a dataset can be: end users' chat text, held by the inference vendor for training experiments. An end user of a product built on Fireworks had no way to know their text was there.

**For readers.**

- Notion workspace owners: check sidebar, then `?`, then `Security incident review`, on a desktop browser. Owners can download the affected-member files. Notion's advice is "We recommend that you treat this data as if it were exposed."
- Anyone who pasted a password, API key or other credential into Notion AI: rotate it. Notion says the same.
- If you build on an inference vendor: list what you send it beyond live requests. Fine-tuning sets, evaluation sets and logged prompts are stored data, and zero-retention terms for inference do not cover them. If your users' text was in a dataset on Fireworks before 2026-10-25, your users are in the same position as Notion's.

Status stays `active`: Fireworks' bulletin still reads "Active monitoring" as last read on 2026-11-10, and this sweep did not re-read it.

## Sources
- [Fireworks AI — October 2026 security incident (security bulletin)](https://fireworks.ai/security/bulletins/october-2026-security-incident) — fetched 2026-10-11; last updated 2026-10-10 11:16 PDT: the quoted scope statement, the full timeline, the "likely captured" wording on API keys and tokens, the list of what was not accessed, the customer actions, the secret-name and fingerprint offer, and the contact address. The only source on the sweep date; no outlet, HN story or search result covered it.
- Related in this corpus: [Coder registry compromise](2026-09-coder-registry-cloudflare-terraform-supply-chain.md) and [Vercel / Context.ai OAuth breach](2026-04-vercel-context-ai-breach.md), the two other tracked cases where a vendor's own internal credential was the entry point and customer secrets were the loot.
- **2026-11-09 update sources:** [Fireworks: Update on October 2026 security incident](https://fireworks.ai/security/bulletins/october-2026-security-incident-update), fetched 2026-11-10: last updated 2026-11-09, "Active monitoring"; the widened data categories, the 2026-10-23 and 2026-10-24 events, the 2026-10-25 statement, the LLM-token-resale attribution, the disabled dataset features; no account count, no provider name, no initial access vector. [Fireworks security bulletins index](https://fireworks.ai/security/bulletins), fetched 2026-11-10: two bulletins, the October page last updated 2026-10-10. Hacker News item 50432415 ("Fireworks AI Hacked", 2026-11-09 21:26 UTC, 11 points), read through the Algolia items API on 2026-11-10 for the title, the Bloomberg link and the commenter's citation; the Bloomberg and The Information articles were not opened.
- **2026-11-11 update sources** — [Notion: Security incident involving a third-party AI vendor](https://www.notion.com/help/security-incident-involving-a-third-party-ai-vendor), fetched 2026-11-11: undated page; the quoted sentences, the three features, the 2026-11-03 disconnection, the owner review path. Hacker News item 50437106 (2026-11-10, 164 points) links it. Seen on front pages and not opened: The Hacker News "Fireworks AI Confirms Wider Breach Affecting Customer Datasets, Model Weights and Notion AI Chats" and The Register "Fireworks AI gets burned twice as customer data exposure widens", both 2026-11-10.
