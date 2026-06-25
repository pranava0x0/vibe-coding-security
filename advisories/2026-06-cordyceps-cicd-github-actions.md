---
id: 2026-06-cordyceps-cicd-github-actions
title: "Cordyceps — CI/CD misconfiguration class in GitHub Actions enables PR-based code execution and credential theft at 300+ major repos"
date_disclosed: 2026-06-24
last_updated: 2026-06-25
severity: high
status: active
ecosystems: [github-actions, ci-cd, npm, pypi]
tools_affected: [GitHub Actions, CI/CD pipelines, any repo with pull_request-triggered workflows using excessive permissions]
tags: [ci-cd, supply-chain, credential-theft, github-actions, pull-request, code-execution, class]
---

## TL;DR
**Cordyceps** (Novee Security, disclosed June 24, 2026): a class of GitHub Actions CI/CD misconfiguration that lets **any unauthenticated user with a free GitHub account** forge approvals, push code, or steal credentials by submitting a malicious pull request. 300+ of ~30,000 scanned high-impact repositories are fully exploitable — including **Microsoft Azure Sentinel, Google AI Agent Development Kit, Apache Doris, Cloudflare Workers SDK,** and **Python Software Foundation's Black formatter**. Exploitation can trigger npm/PyPI/Crates.io/Docker package publishes, push commits to protected branches, and compromise AWS/GCP/Netlify credentials. No CVE assigned; patches being applied individually.

## What happened

**Novee Security** published the Cordyceps class on **2026-06-24** after scanning ~30,000 high-impact GitHub repositories. The core issue is a well-known but widely-misconfigured GitHub Actions pattern: **workflows triggered by `pull_request_target` or `push` events that run with excessive permissions while checking out untrusted content**.

The Cordyceps class has three forms:

### Form 1 — `pull_request_target` + checkout of PR head
```yaml
on:
  pull_request_target:
    types: [opened, synchronize]

jobs:
  ci:
    runs-on: ubuntu-latest
    permissions:
      contents: write          # ← excessive
      packages: write          # ← lets attacker publish packages
      id-token: write          # ← grants cloud OIDC credentials
    steps:
      - uses: actions/checkout@v4
        with:
          ref: ${{ github.event.pull_request.head.sha }}   # ← attacker's code
      - run: npm publish                                     # ← runs attacker's code
```
A PR from any external contributor triggers the workflow with **write permissions to the repository**, cloud OIDC tokens, and npm/PyPI publishing credentials. The attacker's code runs with the full capability of the workflow.

### Form 2 — Weak `CODEOWNERS` + auto-approve bots
Some repos configure a bot to automatically approve PRs when tests pass. If the bot has `contents: write` permission and doesn't distinguish external from internal contributors, a malicious PR that passes tests gets auto-approved and auto-merged.

### Form 3 — Mutable `workflow_dispatch` inputs with no permission gates
A workflow with `workflow_dispatch` and a `cmd` input runs it as a shell command:
```yaml
on:
  workflow_dispatch:
    inputs:
      cmd:
        required: true
run:
  - run: ${{ inputs.cmd }}
```
If the workflow is triggerable by any contributor (fork or otherwise), this is an arbitrary command execution interface.

**Confirmed exploitable at:**
| Organization | Repository | Impact |
|---|---|---|
| Microsoft | Azure Sentinel | Cloud credential exfiltration; potential Sentinel data access |
| Google | AI Agent Development Kit | npm publish credentials; OIDC to Google Cloud |
| Apache | Doris | Release pipeline credentials |
| Cloudflare | Workers SDK | npm publish to `@cloudflare/*` namespace |
| Python Software Foundation | Black formatter | PyPI publish credentials for `black` |
| 295+ others | Various | npm/PyPI/Crates.io/Docker publish, cloud OIDC, protected branch pushes |

Novee Security conducted responsible disclosure; Microsoft and Google confirmed impact. Cloudflare, Python, and Apache applied patches before public disclosure. **Microsoft and Google are still in the process of remediating** as of June 24, 2026.

**Why this matters to vibe-coding developers:**
1. Vibe-coded projects that depend on packages published via exploitable workflows may receive malicious updates. A Cordyceps exploitation against Cloudflare's Workers SDK or PSF's Black would affect a significant fraction of the vibe-coding stack.
2. Vibe-coded projects frequently copy CI/CD configurations from popular templates or starter kits — many of which use `pull_request_target` without understanding the security implications.
3. Google's AI Agent Development Kit repo being affected means OIDC credentials for Google Cloud are in scope — for vibe-coders using Gemini or Google AI Studio SDK, this is a direct upstream credential risk.

## Am I affected?

**Check your own repo:**
```bash
# Find workflows using pull_request_target
grep -r 'pull_request_target' .github/workflows/ 2>/dev/null

# Check for write permissions combined with checkout of PR head
grep -A20 'pull_request_target' .github/workflows/*.yml | grep -E 'contents: write|packages: write|id-token: write'

# Find workflow_dispatch with unvalidated shell inputs
grep -B5 -A10 'workflow_dispatch' .github/workflows/*.yml | grep -E 'inputs\.|run:.*inputs\.'
```

**Check if your dependencies come from affected repos:**
- If you use `@cloudflare/*` npm packages, `black` (Python formatter), any Azure Sentinel SDK, or Google AI Agent development tooling — verify your lockfiles resolve versions published *before* June 24, 2026 from known-clean commits.
- Monitor release changelogs of affected packages for unexpected versions in the next 1-4 weeks.

## If you are affected

→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

**If your own repo is vulnerable:**
1. Change `pull_request_target` to `pull_request` for workflows that check out PR code.
2. Add an explicit permissions block with the **minimum** required — use `read-all` as default, promote only what's needed.
3. For npm publish workflows, add a manual-approval gate (`environment: production` with required reviewers) before any publish step.
4. Gate `workflow_dispatch` inputs through an allowlist rather than passing them directly to `run:`.
5. Enable GitHub's "Require a pull request before merging" and disable auto-merge for external contributors.

## Prevention

→ [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

**Key principles:**
- **Never combine `pull_request_target` + `checkout: ref: ${{ github.event.pull_request.head.sha }}` + write permissions.** This triple is the Cordyceps pattern. Use `pull_request` (which runs on the base branch, not the PR head) if you need read-only access to PR metadata.
- **Scope OIDC token permissions tightly.** Do not issue `id-token: write` to workflows that process external contributor input.
- **Require signed commits from maintainers.** The [Megalodon campaign](2026-05-megalodon-github-actions-mass-campaign.md)'s `build-bot` commits would have failed signed-commit verification; Cordyceps would require a reviewer to approve a malicious PR.
- **Pin GitHub Actions to full commit SHAs.** Floating `@v4` tags can be silently redirected; pinning to a SHA prevents tag-hijack supply-chain attacks that compound Cordyceps-style misconfigurations.
- Use StepSecurity's [Harden Runner](https://stepsecurity.io) GitHub Action to audit outbound network egress from CI runners — a Cordyceps exploit that exfiltrates credentials will appear as unexpected egress.

## Sources
- [The Hacker News — Cordyceps CI/CD Flaws Expose 300+ GitHub Repositories to Supply-Chain Attacks](https://thehackernews.com/2026/06/cordyceps-cicd-flaws-expose-300-github.html) — primary coverage, June 24, 2026.
- [Dark Reading — 'Cordyceps': Malicious Pull Requests Threaten CI/CD Workflows](https://www.darkreading.com/application-security/cordyceps-malicious-pull-requests-developer-workflows) — independent analysis, June 24, 2026.
- [SecurityWeek — Exploitable CI/CD Vulnerabilities Expose Millions of Repositories to Hijacking](https://www.securityweek.com/exploitable-ci-cd-vulnerabilities-expose-millions-of-repositories-to-hijacking/) — broader context on the CI/CD vulnerability class, June 24, 2026.
