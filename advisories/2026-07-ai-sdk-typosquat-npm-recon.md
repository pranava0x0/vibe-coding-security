---
id: 2026-07-ai-sdk-typosquat-npm-recon
title: "AI-SDK-name typosquats on npm harvest git/SSH/cloud identity — anthropic-toolkit, ai-sdk-helpers, @langgraphjs/toolkit and more (~20K downloads, removed)"
date_disclosed: 2026-07-09
last_updated: 2026-07-16
severity: high
status: contained
ecosystems: [npm]
tools_affected: [anthropic-sdk, vercel-ai-sdk, langgraph, ollama, openai-agents-sdk]
tags: [typosquatting, npm, reconnaissance, ai-sdk-impersonation, supply-chain, credential-recon]
---

## TL;DR
A single npm publisher account ran a months-long typosquatting campaign impersonating **AI SDK tooling by name** — `anthropic-toolkit` (mimics Anthropic's Claude SDK), `ai-sdk-helpers` (mimics Vercel's `ai` SDK), `@langgraphjs/toolkit` (mimics LangChain's LangGraph.js), `ollama-helpers`, and `openai-agents-helpers` — plus two unrelated fake Argon2 password-hashing packages from the same actor. Install hooks silently profiled the developer's machine (hostname, git/GitHub identity, SSH key comments, cloud account IDs, CI platform) and exfiltrated it to a Google Cloud Run endpoint. Combined downloads across all packages were roughly **20,000**; packages and the publishing account were taken down after disclosure.

## What happened
[OpenSourceMalware](https://opensourcemalware.com/blog/cybersecurity-startup-publishes-infostealers-to-npm) identified five npm packages, all first published between **April and June 2026**, that specifically typosquat the names developers reach for when integrating popular AI agent/SDK tooling rather than generic utility-package names:

| Package | Impersonates | Version at disclosure |
|---|---|---|
| `anthropic-toolkit` | Anthropic Claude SDK | 1.3.0 |
| `ai-sdk-helpers` | Vercel's `ai` SDK | 1.4.4 |
| `@langgraphjs/toolkit` | LangChain's LangGraph.js | 1.2.12 |
| `ollama-helpers` | Ollama | 1.2.2 |
| `openai-agents-helpers` | OpenAI Agents SDK | 1.3.2 |

The same publisher also shipped two unrelated fake Argon2 password-hashing packages from April 2026 (`@aspect-security/argon2` 1.0.1, `argon2-napi` 1.0.0). Combined weekly/monthly downloads across the full set were on the order of **20,000** at disclosure time.

**Data harvested** — OpenSourceMalware documents 11 distinct categories collected via a preinstall/postinstall hook: machine hostname and OS username; git identity (from `~/.gitconfig` and project-local config); GitHub CLI identity (`~/.config/gh/hosts.yml`); up to 15 unique committer emails pulled from the last 50 `git reflog` entries; the `origin` remote URL; SSH **public**-key comments from `~/.ssh/*.pub` (not private key material); cloud identity — GCP project/account from `~/.config/gcloud/properties` and AWS profile names/SSO URLs/account IDs from `~/.aws/config` (the report notes credential *values* were explicitly skipped, only identity metadata was taken); the host's corporate DNS domain via `/etc/resolv.conf`; the parent project's `package.json` name/author/repository; CI-platform detection (GitHub Actions, GitLab CI, Jenkins, CircleCI, Travis, Buildkite); and basic runtime metadata (Node version, OS, CPU arch, timestamp). Exfiltration went to Google Cloud Run URLs (`npm-package-logger-228835561205.{region}.run.app`), sharing a single embedded GCP project number (`228835561205`) across every artifact — a strong signal all packages are one operator. A fake "telemetry opt-out" environment variable was offered as cover.

OpenSourceMalware attributes the publishing account to **the founder of a still-in-stealth-mode, Israel-based cybersecurity startup**, but deliberately declined to name the company or individual. [Xygeni's weekly malicious-code digest](https://xygeni.io/blog/xygeni-malicious-code-digest-78/), published independently, corroborates the same five package names and confirms the campaign was still active on **2026-07-07** — all five received incremented versions that day (`anthropic-toolkit` 1.3.1, `ai-sdk-helpers` 1.4.5, `openai-agents-helpers` 1.3.3, `@langgraphjs/toolkit` 1.2.13, `ollama-helpers` 1.2.3) as part of what Xygeni calls a continuing "AI-tooling impersonation pattern" — meaning the campaign continued for weeks after OpenSourceMalware's private disclosure (made in late June 2026) until the public writeup and takedown on **2026-07-09**. Both packages and the publishing account have since been removed from npm.

**No CVE has been assigned** — this is npm-registry malware, not a bug in a specific package version of a legitimate project.

## Am I affected?
```bash
# Check any Node project for these package names, at any version
npm ls anthropic-toolkit ai-sdk-helpers ollama-helpers openai-agents-helpers "@langgraphjs/toolkit" "@aspect-security/argon2" argon2-napi --all 2>/dev/null

grep -E '"(anthropic-toolkit|ai-sdk-helpers|ollama-helpers|openai-agents-helpers|@langgraphjs/toolkit|@aspect-security/argon2|argon2-napi)"' \
  package-lock.json yarn.lock pnpm-lock.yaml 2>/dev/null

# Look for outbound traffic to the exfil endpoint in shell/proxy history
grep -r 'npm-package-logger-228835561205' ~/.bash_history ~/.zsh_history 2>/dev/null
```
None of these are real Anthropic, Vercel, LangChain, Ollama, or OpenAI packages — the legitimate SDKs are `@anthropic-ai/sdk`, `ai` (Vercel), `@langchain/langgraph`, `ollama`, and `openai`/`@openai/agents` respectively.

## If you are affected
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — this campaign is reconnaissance-only (no credential *values*, private keys, or wallet material were exfiltrated per the source), but the harvested git/GitHub/CI identity and cloud account IDs are enough to build a targeted follow-on attack; treat any host that ran an affected version as having disclosed its developer and CI identity to an unknown third party.
→ [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — verify you're installing the vendor's actual published package name before adding an AI-SDK dependency.
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)

## Why this matters for vibe coders
This is a purpose-built variant of typosquatting that targets **the exact package names a vibe coder reaches for when wiring up an AI SDK** — Claude, Vercel AI SDK, LangGraph, Ollama, OpenAI Agents — rather than generic high-traffic utility names. The recon-only payload (profiling git/CI/cloud identity without stealing secret values) matches the pattern this repo has previously flagged in the npm dependency-confusion campaign: a reconnaissance-first stage is often a precursor to a larger, more damaging follow-on wave, so a package match here is worth investigating even though nothing was directly stolen.

## Sources
- [OpenSourceMalware — Cybersecurity Startup Publishes Infostealers to npm](https://opensourcemalware.com/blog/cybersecurity-startup-publishes-infostealers-to-npm) — primary technical writeup, full IOC list, package/version table, exfil endpoint.
- [Xygeni — Malicious Code Digest #78](https://xygeni.io/blog/xygeni-malicious-code-digest-78/) — independent corroboration, confirms campaign was still active with new versions as of 2026-07-07.
