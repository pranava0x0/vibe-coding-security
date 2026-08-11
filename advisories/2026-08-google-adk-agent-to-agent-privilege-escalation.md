---
id: 2026-08-google-adk-agent-to-agent-privilege-escalation
title: "\"I'll Just Call You\" — a public PR comment tricks Google ADK's low-privilege triage bot into invoking its own maintainer-only agent, leaking API keys and a GCP service-account key"
date_disclosed: 2026-08-03
last_updated: 2026-08-03
severity: high
status: patched
ecosystems: [ai-agents, github-actions]
tools_affected: ["Google Agent Development Kit (ADK)", "google/adk-python"]
tags: [prompt-injection, agent-to-agent, privilege-escalation, ci-cd, github-actions, decorator-as-documentation]
---

## TL;DR

Pillar Security found what it calls the first practical, real-world case of **agent-to-agent exploitation in a multi-agent system**: on Google's own `google/adk-python` GitHub repository, a low-privileged, public-facing PR-triage bot (`adk-bot`) could be manipulated via a prompt injection hidden in an ordinary pull request to post a comment beginning `@gemini-cli` — which a separate CI workflow (`gemini-dispatch.yml`) automatically routed to a **maintainer-only, highly privileged agent** (`gemini-invoke.yml`), executing attacker-controlled instructions with elevated permissions. The proof-of-concept chain leaked a GitHub personal access token (`ADK_TRIAGE_AGENT` PAT), a `GOOGLE_API_KEY`, and a `GCP_SA_KEY` service-account key with Vertex AI access. Reported to Google **2026-06-02/05**; Google fixed it by **2026-07-21** by deleting the three vulnerable workflows outright rather than patching them, and gave Pillar an "Honorable Mention" (no monetary bounty).

## What happened

Google's Agent Development Kit repository ran an automated CI pipeline with two agents at different privilege tiers: a low-privilege, public-facing `adk-bot` that triages incoming pull requests, and a separate, maintainer-only agent invoked via `gemini-invoke.yml` that carries far broader repository permissions. The two were connected by a dispatch mechanism (`gemini-dispatch.yml`): any comment beginning with the string `@gemini-cli` was automatically routed from the low-privilege triage context into the high-privilege agent's workflow, with **no re-authentication or privilege check on the content being routed** — the classic "decorator/dispatch-string as documentation, not a security boundary" pattern this repo tracks across SDK annotations and tool-registration APIs, here applied to a GitHub Actions comment-dispatch trigger.

Pillar crafted a pull request whose body was written to satisfy Google's own contribution guidelines on its face — so `adk-bot`'s triage response, generated in reply, itself contained a comment that began with `@gemini-cli` and carried attacker-chosen instructions. That triggered the dispatch workflow to invoke the privileged `gemini-invoke.yml` agent with those instructions, which Pillar used to demonstrate exfiltration of:
- `ADK_TRIAGE_AGENT`, a scoped GitHub personal access token,
- `GOOGLE_API_KEY`,
- `ADK_GCP_SA_KEY`, a GCP service-account key with **Vertex AI** access.

A contributing structural flaw: the agents were classified in GitHub's permission model as **"collaborators" rather than "bots,"** which granted them access to maintainer-only workflow paths they should not have been eligible to trigger.

Pillar reported the finding **2026-06-02/05**; Google's fix, shipped by **2026-07-21**, was to **delete all three implicated workflows** (an issue-analysis workflow that ran automatically on every new issue, an issue-fix workflow listening for a `/adk-issue-fix` command, and the pull-request analysis workflow) rather than attempt to patch the dispatch logic in place. Pillar published its writeup **2026-08-03**; no CVE has been assigned.

## Am I affected?

This specific chain affected Google's own `adk-python` repository and has been fixed there. You're at risk of the same *class* of bug if your own CI/CD pipeline runs more than one AI agent at different privilege levels and:

```bash
# Look for any workflow that dispatches based on matching a string prefix
# in agent-generated or user-generated comment/PR text
grep -rn "startsWith\|contains(.*comment\|@[a-z-]*-cli\|@[a-z-]*-bot" .github/workflows/*.yml

# Check whether any bot/agent account in your repo is classified as a
# "collaborator" (broad permissions) rather than a scoped GitHub App/bot
```

You're affected if: (1) a low-privilege agent's *output* (a comment, a label, a reply) can trigger a separate, higher-privilege agent's workflow, and (2) the trigger condition is a simple string/prefix match rather than a signed, out-of-band authorization check.

## If you are affected

1. Remove or disable any workflow that dispatches to a higher-privilege agent based on matching text in agent-generated or user-generated content.
2. Re-classify bot/agent GitHub accounts as scoped GitHub Apps rather than repository collaborators, so their effective permissions match their intended role.
3. Rotate any credentials (PATs, API keys, service-account keys) available to either agent in the chain.

→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
- **An agent that reads untrusted text and holds a credential is a privilege-escalation primitive that speaks natural language.** Treat any dispatch mechanism between agents of different privilege levels as a security boundary requiring real authorization, not a string match.
- **Never let one agent's output be the sole trigger for a more-privileged agent's action.** Require a human-in-the-loop confirmation, or at minimum an out-of-band signed token, before crossing a privilege boundary between agents.
- This is the same **decorator-as-documentation** root cause this repo tracks in SDK tool-annotation frameworks (Semantic Kernel, Flowise) and agent-platform tool-registration APIs (Composio) — here it's a CI dispatch string instead of a code annotation, but the lesson is identical: a matching pattern is not an authorization check.

## Sources

- [Pillar Security — "I'll Just Call You: Agent-to-Agent Privilege Boundary Failures in CI/CD on Google's ADK Repository"](https://www.pillar.security/blog/ill-just-call-you-agent-to-agent-privilege-boundary-failures-in-ci-cd-on-googles-adk-repository) — primary research, full attack chain, credential exposure detail, disclosure timeline, Google's remediation.
- [GIGAZINE — "A hacking technique against Google ADK has been discovered that involves 'hacking low-privilege agents and executing code with higher privileges'"](https://gigazine.net/gsc_news/en/20260804-agent-development-kit-attack) — independent confirmation, attack-chain summary, "collaborator vs. bot" permission detail.
- Cross-reference: [CoreBreak](2026-08-corebreak-agent-harness-tool-call-forgery.md) — a different Google ADK vulnerability (forged tool-call authorization, CVE-2026-18236) in the same product, unrelated root cause.
