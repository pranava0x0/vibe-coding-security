# Auditing your app with an agent security-audit skill

> Cloudflare's open-source `security-audit` skill turns Claude Code or Codex into a multi-agent source auditor. It is good at the bugs this corpus sees most in vibe-coded apps (missing authorization, SSRF, path traversal, unsafe rendering) and useless for the ones scanners already catch (known CVEs in dependencies). Run it on a scoped target with a budget, read every finding yourself, and pair it with a dependency scanner.

## What it is

[`cloudflare/security-audit-skill`](https://github.com/cloudflare/security-audit-skill) (MIT, created 2026-06-18, 63.5k stars when read on 2026-11-06) is a ~320 KB bundle of Markdown instructions and two Node validators that a coding agent loads as a skill. Cloudflare published it as the single-repository seed of the internal harness it describes in its post "Build your own vulnerability harness"; the fleet harness itself is not public. The skill runs six phases:

1. **Reconnaissance**: four parallel read-only agents map the stack, principals, entry surfaces and local build paths into `architecture.md` and a deterministic `coverage-ledger.json`.
2. **Coverage-led hunting**: isolated hunters each take ledger units (surface × trust boundary × attack class) and return structured candidates, never prose.
3. **Candidate validation**: a fresh agent that did not find the candidate tries to refute it from source.
4. **Structured output**: `findings.json`, checked against `report-schema.json` by `validate-findings.cjs`; the ledger by `validate-coverage-ledger.cjs`.
5. **Independent record verification**: another fresh agent re-checks every retained record.
6. **Target-neutral reports**: `REPORT.md`, `FINDINGS-DETAIL.md`, `NEEDS-VALIDATION.md`.

Three verdicts only. `confirmed` needs a complete source trace from a lower-trust entry point to a crossed boundary and a bounded observed result; only confirmed records get a severity. `needs_validation` is a source-grounded lead blocked by a fact outside the repository (a deployment header, a provider setting) and carries no severity. `rejected` is a disproved candidate, kept so the next run does not repeat it. A missing best practice with no affected principal is a hardening note, not a finding.

## What people report after running it

- **Token cost is the loudest complaint.** On the Hacker News thread (2026-09-17, 213 points) one user spent "at least 150k" tokens on "a relatively small FastAPI project" and hit a session limit; another "threw 1M tokens for nothing in a medium codebase". The repeated advice in that thread: "These work best on a targeted section of the code, like a PR."
- **A single run is half a run.** Cloudflare's own README says one run finds roughly half of what repeated runs find in total, so the skill carries prior ledgers forward and repeated runs are additive.
- **It does not find dependency CVEs, by design.** A blind test posted as upstream issue #20 (three runs per approach against a seeded target) reported median 90 percent precision and no hits on decoy findings, and 0 percent on a disclosed CVE in a pinned dependency. This repo has not reproduced that test; treat it as one contributor's experiment.
- **The sandbox requirement bites.** Target code (tests, builds, fixtures) runs only inside an OS-enforced sandbox with no network, an allowlisted empty environment and resource limits. Without one, the skill stays source-only and every lead that needs execution lands in `NEEDS-VALIDATION.md`. That is the correct outcome, not a bug.
- **Security framing can trip model refusals.** Practitioners on the same thread report that prompts framed as security research sometimes draw refusals from frontier models; Anthropic's cyber-verification programme removes most of them.
- **The validators check structure, not exploitability.** Every `confirmed` record still needs a human to read the trace.

## When to run it on a vibe-coded app

Run it when the agent that wrote your app also wrote your authorization logic, which is most of the time. The classes it is built for are the ones in [auditing a vibe-coded repo](../playbooks/auditing-a-vibe-coded-repo.md): BOLA and IDOR in API routes, Supabase RPCs that skip Row-Level Security, SSRF in server-side fetches, file uploads that trust a path, CORS that trusts any origin, and rendering of untrusted HTML. It will not replace `osv-scanner`, Socket, `npm audit` or `pip-audit` for known-vulnerable dependencies, and it will not tell you about a header your host sets.

Good scope: one subsystem, one pull request, or the `auth/`, `api/` and `server/` directories of a generated app. Bad scope: a whole monorepo on a weekend token budget.

## How to run it

```bash
# install into the agent you use (Claude Code, Codex, Cursor and Copilot are listed by the skills CLI)
npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit

# then, inside the project, with an explicit profile, scope and budget:
#   "security audit ./src/api with the quick profile and a budget of 12 agents, output to ~/audits/<app>"
```

Pick `quick` for a first pass or a pull request, `standard` for a release, `deep` once a quarter. Set a budget in agent invocations; the skill reserves critics and verifiers before it spends on hunters and reports an incomplete run instead of silently thinning evidence. Keep the output directory outside the repository, or in a directory your `.gitignore` covers, and never commit `agents/*/scratch/`.

Read the output in this order: `REPORT.md` for the posture summary and the confirmed table, `FINDINGS-DETAIL.md` for each confirmed record's trace and smallest fix, then `NEEDS-VALIDATION.md` as a to-do list of facts only you can observe (your hosting provider's headers, your branch protection, your database policies). Do not ship a fix you cannot connect to a line in the trace.

## What it found here

This repository runs the vendored copy at [`.claude/skills/security-audit/`](../.claude/skills/security-audit/UPSTREAM.md) on its own build pipeline and publishes every run, including the rejected candidates, under [`security-audits/`](../security-audits/). The first run (2026-11-06) is summarised there; the pattern it found, a Markdown renderer that passes raw HTML through to a public site whose content is written partly by an automated agent reading untrusted web pages, is the same shape this corpus documents in the [agent sandboxing](agent-sandboxing.md) guide: untrusted content plus a publishing path.

## Related

- [Auditing a vibe-coded repo](../playbooks/auditing-a-vibe-coded-repo.md): the 15-point manual list this skill automates part of.
- [Agent sandboxing](agent-sandboxing.md): the OS-enforced sandbox the skill requires for any execution.
- [Package vetting checklist](package-vetting-checklist.md): the dependency half that this skill does not cover.
