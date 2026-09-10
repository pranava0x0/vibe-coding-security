---
id: 2026-09-gtig-adversarial-ai-agentic-pipelines
title: "GTIG: attacker agentic pipelines — TeamPCP trojanized MCP servers, hidden .claude/.cursor malware, a 23,800-secret harvester dashboard"
date_disclosed: 2026-09-08
last_updated: 2026-09-10
severity: high
status: ongoing
ecosystems: [npm, pypi, docker-hub, mcp, github-actions, claude-code, cursor, cline, continue, gemini, openai-codex]
tools_affected: [cursor, cline, continue, claude-code, gemini-cli, codex, litellm, github-actions, mcp-servers, any-developer-workstation-holding-ai-platform-credentials]
tags: [agentic-threat-actor, threat-intelligence, teampcp, supply-chain, mcp, credential-theft, infostealer, model-distillation, ai-vendor-report, github-actions, oidc]
---

## TL;DR

Google Threat Intelligence Group (GTIG) published its adversarial-AI tracker on **2026-09-08**, and it is the first vendor-telemetry report to describe attackers running **agentic pipelines** rather than asking a chatbot for help. Three findings bear directly on this repo's readers: **(1)** the actor GTIG tracks as **UNC6780 — TeamPCP**, behind the Mini Shai-Hulud waves, is now shipping **trojanized MCP servers** (`tiktoken_mcp`, `azure-functions-mcp-extension`), extracting OIDC tokens from GitHub Actions runners to sign SLSA Build Level 3 attestations, hiding malware in `.claude/`, `.vscode/`, and `.cursor/` directories, and placing prompt-injection text in its JavaScript loaders aimed at **LLM-based security scanners**; **(2)** in Q2 2026 a financially motivated actor compromised a cloud resource, then used "an AI coding chatbot, a prompt, and a set of agent instructions" (markdown playbooks) to plan, build, and run a mass credential-harvesting campaign — **thousands of third-party credentials in under six hours**; **(3)** an exposed C2 dashboard for a framework GTIG calls **"Recon"** held **23,800+ harvested secrets** (API keys, cloud and AI-service credentials), configured through `AGENTS.md`/`KNOWLEDGE.md`-style agent files — the same instruction-file convention your own coding agent reads. GTIG's incident-response guidance now includes: **assume threat actors have your developer IDE configurations.**

## What happened

GTIG's report (single primary source — Google's own telemetry, with Mandiant incident-response cases; The Hacker News' same-day coverage restates it) lays out a five-stage progression it says attackers have moved through in 2026: basic prompting → multi-stage prompt chains → agentic workflows (autonomous scanning, error resolution, credential harvesting) → AI integrated across the whole attack lifecycle → fully autonomous pipelines with machine-speed vulnerability discovery, which it says it has observed "in limited cases." The specifics that matter here:

### UNC6780 / TeamPCP — the supply-chain actor this repo already tracks, now with an MCP and agent-config toolkit

GTIG attributes the [TeamPCP / Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md) campaign (March 2026 – ongoing, PyPI/npm/Docker Hub) to UNC6780 and names its credential stealer **DUSTMAKER**. New in this report, relative to what this repo had from vendor IR posts:

- **Trojanized MCP servers** as a distribution vector, with `tiktoken_mcp` and `azure-functions-mcp-extension` named — MCP packages impersonating real tooling, the [same lane as Deadbugz](2026-09-deadbugz-mcp-supply-chain-campaign.md) and the [malicious-MCP-registry findings](2026-08-agent-framework-mcp-cve-batch.md).
- **OIDC token extraction from GitHub Actions runners** to sign attestations — which is how compromised packages arrived with **valid SLSA Build 3 provenance**, the "provenance was real, the package was still malicious" problem first seen in the [`@7nohe/openapi-react-query-codegen` compromise](2026-08-openapi-react-query-codegen-comment-triggered-publish.md).
- **Prompt injection inside the JavaScript loaders, targeting LLM-based security scanners.** The payload carries text meant for the *analyst's AI*, not the victim's — the same anti-triage move as the [Hades campaign's "AI analyst misdirection"](2026-06-hades-campaign-pypi-mcp-attack.md).
- **Hidden-directory malware and config hijacking for persistence** in `.claude/`, `.vscode/`, and `.cursor/` — dropped where an AI coding tool will read them and where a human `ls` won't show them. Compare [TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md) and the [Claude Code MCP OAuth hijack](2026-06-claude-code-mcp-oauth-hijack.md).

### Mass credential harvesting, built by an agent, in under six hours

GTIG's headline case: in Q2 2026 an actor compromised a cloud resource, then leveraged "an AI coding chatbot, a prompt, and a set of agent instructions to plan, build, and execute a mass credential harvesting campaign in less than six hours." The tooling was a multi-agent architecture with markdown instruction sets as operational playbooks, autonomous vulnerability scanning, and IP-rotation logic — no manual intervention between steps. GTIG does not name the victim, the chatbot, or the exact credential count beyond "thousands of third-party credentials."

### "Recon" — a credential-harvesting dashboard with 23,800+ secrets

Google found an exposed command-and-control server running a production dashboard for an automated reconnaissance framework it calls "Recon," holding **23,800+ secrets** — API keys, cloud credentials, and AI-service credentials — with the framework configured through files named `AGENTS.md`, `KNOWLEDGE.md`, and `agentic_vuln_research.md`. GTIG frames it as the shift from passive endpoint infostealers to offensive agentic harvesting: the infostealer output becomes the seed list for an agent that goes and uses the keys.

### Everything else in the report

- **UNC6508** (PRC-nexus) targets North American academic, medical, and military AI research for model weights and source code — and deploys **local open-weight LLM infrastructure inside compromised cloud environments** to avoid commercial-API monitoring while using the victim's compute (Mandiant saw requests for 48-vCPU instances and NVIDIA RTX 6000 quota).
- **Model distillation** campaigns against Gemini exceeded **100 million prompts** in Q2, run through proxy infrastructure with thousands of compromised credentials and account rotation.
- Extortion cases where the stolen assets were **proprietary AI models, prompts, skills, and model scripts** at a healthcare company and an AI media-generation company.
- **Tools GTIG saw abused or built by actors:** Gemini, Claude, Codex, DeepSeek-Coder; Cursor, Cline, Continue, Gemini CLI; a LiteLLM proxy; the Manus agent framework; and actor-built tooling named CC Switch (LLM orchestration), Phalanx (autonomous pentest), and Recon.

## Am I affected?

This is a threat-landscape report, not a single incident with an IOC list, so "affected" means "in the target set." You are if you:

- Publish to npm/PyPI/Docker Hub from GitHub Actions with OIDC trusted publishing — GTIG documents runner-side OIDC token theft used to sign provenance.
- Run MCP servers you installed by name rather than by audited source. Check for the two named packages:

```bash
grep -ri 'tiktoken_mcp\|azure-functions-mcp-extension' ~/.claude/settings.json ~/.cursor/mcp.json ~/.codex/config.toml ~/.vscode/ 2>/dev/null
pip list 2>/dev/null | grep -i 'tiktoken.mcp\|azure.functions.mcp'
npm ls -g 2>/dev/null | grep -i 'tiktoken-mcp\|azure-functions-mcp'
```

- Keep AI-platform API keys on a workstation that has ever run an infostealer — GTIG names **LUMMAC.V2, STEALC.V2, VIDAR, and ACRSTEALER** as the feeders; the same families are behind the [Claude.ai session-hijack wave](2026-09-anthropic-claude-session-infostealer-hijack.md).
- Have a hidden `.claude/`, `.cursor/`, or `.vscode/` directory in a project you did not create:

```bash
find . -maxdepth 3 -type d \( -name .claude -o -name .cursor -o -name .vscode \) -newer package.json 2>/dev/null
git status --ignored --short | grep -E '\.(claude|cursor|vscode)/'
```

## If you are affected

- Trojanized MCP server or hidden agent config found: [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md), then [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).
- Any AI-platform key that lived on a machine with an infostealer detection: [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). GTIG's specific ask: **audit your cloud projects for unauthorized Generative Language API enablement** — the same silent-scope-expansion problem as the [Google API-key/Gemini finding](2026-02-google-api-key-gemini-scope-escalation.md) — and review BigQuery/Cloud Run/Artifact Registry IAM for exfiltration paths.

## Prevention

- [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) — OIDC trusted publishing is only as strong as the runner; a compromised job step can mint the same token your release job does. Pin actions, scope `id-token: write` to the one job that publishes, and treat provenance as "the build ran," not "the build was honest."
- [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — install MCP servers from audited source, not by searching a registry for a plausible name.
- [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — AI-service keys are now a first-class infostealer target and a first-class *agent* target. Short-lived tokens; no long-lived keys in `.env` files on laptops.
- **Assume your agent instruction files are read by attackers and written by them.** GTIG's actor configured its harvester with `AGENTS.md`; TeamPCP drops payloads into `.claude/`. The convention that makes your coding agent useful is the same one that makes it steerable.

## Sources

- [Google Cloud Threat Intelligence — From Prompting to Autonomy: The Evolution of Adversarial AI](https://cloud.google.com/blog/topics/threat-intelligence/from-prompting-to-autonomy-the-evolution-of-adversarial-ai) — fetched 2026-09-10; primary source, published 2026-09-08: UNC6780/TeamPCP toolkit (DUSTMAKER, trojanized MCP servers, OIDC/SLSA, hidden-directory persistence, scanner-targeted prompt injection), the <6-hour credential-harvesting case, the Recon dashboard (23,800+ secrets), UNC6508, distillation figures, named tools, and defender recommendations.
- [The Hacker News — Autonomous AI Agents Compromise Thousands of Credentials in Under Six Hours](https://thehackernews.com/2026/09/autonomous-ai-agents-compromise.html) — fetched 2026-09-10; same-day secondary coverage of the GTIG report (restates, does not independently verify).
