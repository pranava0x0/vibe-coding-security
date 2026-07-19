---
id: 2026-07-rogue-agent-dialogflow-cx-shared-execution
title: "Rogue Agent — shared Cloud Run execution environment let one Dialogflow CX agent hijack every agent in a GCP project (patched, disclosed July 2026)"
date_disclosed: 2026-07-07
last_updated: 2026-07-07
severity: high
status: patched
ecosystems: [google-cloud, dialogflow-cx]
tools_affected: [Google Dialogflow CX, Playbook Code Blocks]
tags: [ai-agent-platform, shared-execution-environment, cross-tenant, agent-hijack, prompt-injection-adjacent, vpc-sc-bypass, imds]
---

## TL;DR
Varonis Threat Labs disclosed **Rogue Agent**: any Dialogflow CX agent with a "Code Blocks" Playbook feature enabled shares a single Google-managed Cloud Run execution environment with **every other agent in the same GCP project**. A user holding only the `dialogflow.playbooks.update` permission on **one** agent could overwrite the shared `code_execution_env.py` file and inject code that ran for **every subsequent Code Block execution across every agent in the project** — reading live conversations, exfiltrating data, and injecting phishing prompts, with **Cloud Logging blind to the filesystem overwrite**. Google fixed it in two stages (April 2026 partial, June 2026 full) after Varonis reported it via VRP in November 2025; no CVE was assigned, and Google says it has no evidence of in-the-wild exploitation.

## What happened
**Dialogflow CX** is Google Cloud's conversational-AI platform for building production chatbots/voice agents; its **Playbooks** feature lets developers embed custom Python ("Code Blocks") directly into a conversation flow to call external APIs or manipulate state.

Varonis found that Code Block execution for **every Dialogflow CX agent in a given GCP project runs inside one shared, Google-managed Cloud Run service** — not an environment isolated per agent. That environment had:
- **Public network egress** (unrestricted outbound internet)
- A **write-enabled filesystem**
- Sufficient privileges to modify the interpreter's own runtime files
- **Access to the Cloud Run instance's Instance Metadata Service (IMDS)**, from which an attacker could retrieve the environment's Google-managed service-account access tokens

An attacker who could edit Code Blocks on **just one agent** (i.e., held `dialogflow.playbooks.update` — grantable per-agent or project-wide) could have a Code Block overwrite the shared `code_execution_env.py` file that Cloud Run uses to execute all Code Blocks. From that point, the attacker's injected logic ran for **every Code Block invocation on every agent in the project**, with access to each conversation's `history` and `state` objects and the ability to call the agent's own `respond()` function — reading live customer conversations and pushing attacker-authored messages (e.g., fake re-authentication prompts for credential phishing) back to real users. Because the compromise lives in the shared runtime file rather than in any individual agent's visible configuration, **Cloud Logging captured none of it** — Varonis describes the persistence as "virtually undetectable" from the customer side.

Two additional issues compounded the blast radius: the shared Cloud Run environment's public egress meant Code Blocks could **exfiltrate data even from projects protected by a VPC Service Controls (VPC-SC) perimeter**, and the exposed IMDS endpoint let an attacker harvest the environment's own Google-managed service-account tokens.

**Attacker prerequisite:** `dialogflow.playbooks.update` on at least one agent — realistically a malicious insider or an attacker who has already compromised a developer/service account with that scope, not an anonymous internet attacker.

**Timeline:** Varonis reported via Google's Vulnerability Reward Program in **November 2025**; Google shipped an initial fix in **April 2026** and fully resolved the shared-environment design flaw in **June 2026**; Varonis published its writeup on **2026-07-07**. No CVE was assigned. Google states it has no evidence of exploitation before the fix.

**Why this matters for vibe coders:** this is the same **agent-platform-as-shared-execution-hub** shape this repo already tracks for MCP-broker platforms like Composio (one compromised tenant/agent reaches every other tenant/agent sharing the same backend) — except here the platform is Google's own first-party product, the "tenants" are Playbook agents inside a single project, and a project-scoped write permission on one agent turned into a project-wide code-execution primitive because the runtime underneath was shared, not isolated. If you build multi-agent systems on any managed platform, ask whether "your agent's" code actually runs in "your agent's" sandbox — or in one shared with every other agent your team or org owns.

## Am I affected?
You were exposed if your GCP project used **Dialogflow CX Playbooks with Code Blocks** before Google's June 2026 fix, and any user/service account other than ones you fully trusted held `dialogflow.playbooks.update` on any agent in that project.

```bash
# Review who currently holds playbook-update permission on your Dialogflow CX agents
gcloud projects get-iam-policy YOUR_PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/dialogflow.admin OR bindings.role:roles/dialogflow.editor" \
  --format="table(bindings.role, bindings.members)"
```

Since this was a platform-side shared-infrastructure flaw (not something you could detect via your own Cloud Logging, per Varonis), there is no reliable customer-side forensic check for past exploitation — Google's fix is what closes the exposure. Audit your Playbook Code Block source for anything you didn't author, and review past Playbook edit history for changes you can't attribute.

## If you are affected
- No customer action was required to receive the fix — Google's June 2026 patch already applies to all Dialogflow CX projects.
- Audit `dialogflow.playbooks.update` grants going forward and scope them to the smallest set of agents/users that actually need edit access, since the permission model (not just the shared runtime) was part of the exposure.
- Review Code Block source across your agents for logic you didn't write, and review conversation logs from before the June 2026 fix for signs of unexpected agent responses (e.g., unsolicited re-authentication requests).

→ [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md)

## Prevention
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — when evaluating any multi-agent platform (managed or self-hosted), explicitly ask whether each agent's code execution is isolated per-agent or shared across a project/org, and whether a scoped write permission on one agent can reach that shared surface.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — treat any exposed IMDS/metadata endpoint inside a managed execution environment as a credential-theft surface; this is the same root class already tracked for MCP servers and agent-orchestration platforms in this repo.

## Sources
- [Varonis — Rogue Agent: How a Single Code Block Could Hijack Your AI Conversations in Google's DialogFlow](https://www.varonis.com/blog/rogue-agent-dialogflow-attack) — primary disclosure; full technical mechanism, timeline, VPC-SC bypass, and IMDS exposure detail.
- [The Hacker News — Rogue Agent Flaw Could Have Let Attackers Hijack Google Dialogflow CX Chatbots](https://thehackernews.com/2026/07/rogue-agent-flaw-could-have-let.html) — independent corroboration of timeline, permission requirement, and lack of a CVE assignment.
