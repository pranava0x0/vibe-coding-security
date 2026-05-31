---
id: 2026-05-megalodon-github-actions-mass-campaign
title: "Megalodon — mass GitHub-Actions workflow poisoning of 5,561 repos (May 2026)"
date_disclosed: 2026-05-22
last_updated: 2026-05-31
severity: critical
status: contained
ecosystems: [github, github-actions, npm]
tools_affected: [any-github-repo, ci-cd, claude-code, cursor, openhands, any-ai-agent-with-gh-tokens]
tags: [supply-chain, github-actions, credential-theft, infostealer-cascade, mass-campaign, ci-cd, workflow-injection]
---

## TL;DR
On **2026-05-18**, an automated campaign codenamed **"Megalodon"** pushed **5,718 malicious commits to 5,561 GitHub repositories in a six-hour window**, injecting GitHub Actions workflows that exfiltrate **CI secrets, cloud credentials, SSH keys, OIDC tokens, and source-code secrets** to **`216.126.225.129:8443`**. The attacker never touched npm — they used **stolen GitHub credentials harvested from infostealer infections** (Hudson Rock: **331 of 978 affected accounts (~33%) matched known infostealer victims**) to push poisoned workflows, and then the *legitimate maintainers* republished from the poisoned source. **`@tiledesk/tiledesk-server` npm versions 2.18.6 → 2.18.12** carried the targeted variant downstream. Distinct actor from TeamPCP; clearest example yet of the **"compromise the source repo, not the npm token"** class. CISA added the campaign to its [supply-chain alert](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories) on **2026-05-28** alongside the [Nx Console / GitHub-breach chain](2026-05-nx-console-vscode-compromise.md).

## What happened
SafeDep's analysis (first disclosed **2026-05-22**) found an automated push pattern across thousands of unrelated GitHub repositories: throwaway accounts with forged author identities (`build-bot`, `auto-ci`, `ci-bot`, `pipeline-bot`) committing single-file changes to `.github/workflows/*.yml` to disguise the malicious commits as routine CI maintenance. Each poisoned workflow ran a base64-encoded bash payload that scoped out the runner's environment and exfiltrated everything attacker-reachable to a single C2:

```yaml
# Pattern (simplified, from SafeDep / StepSecurity / CyberLeveling reverse-engineering)
- run: |
    set +e
    echo "<base64 blob>" | base64 -d | bash
```

Decoded, the payload harvests **CI secrets (`$GITHUB_TOKEN`, OIDC tokens, masked `secrets.*`), `~/.aws/credentials`, `~/.npmrc`, `~/.ssh/id_*`, `~/.docker/config.json`, env files matching `**/.env*`, and any source files matching common secret patterns**, packages them, and POSTs them to **`216.126.225.129:8443`**.

The campaign deployed **two variants**:

1. **`SysDiag` (mass variant)** — adds a *new* workflow file triggered on every `push` and `pull_request`, maximizing automated execution on every subsequent maintainer interaction. This is the variant behind the **5,561-repo number**.
2. **`Optimize-Build` (targeted variant)** — *replaces* an existing trusted workflow (commonly the project's Docker build) with a `workflow_dispatch`-triggered backdoor that lies dormant until the attacker fires it via the GitHub API. This is the variant that reached **`@tiledesk/tiledesk-server` 2.18.6 (2026-05-19) → 2.18.12 (2026-05-21)** when the legitimate maintainer published from the poisoned repo without spotting the workflow swap. **No npm credential was stolen** for the tiledesk arm — the attack flowed through source-repo commit → legit `npm publish`.

### Attribution and the infostealer cascade
**Hudson Rock** correlated the affected accounts against its infostealer-victim database and found **331 of 978 unique usernames (~33%) were direct matches to machines previously infected by infostealers**. Combined with **CrowdStrike's 2026-05-26 takedown of the GlassWorm botnet** (which has been mass-harvesting developer credentials from poisoned [Open VSX extensions](2025-10-glassworm-vscode-worm.md) since 2025), this almost certainly explains where the credentials came from. **There is currently no direct evidence tying Megalodon to TeamPCP** — surface similarities, no shared infrastructure, no overlapping markers. Treat it as a **distinct opportunist actor monetizing the broader stolen-credential-as-a-service market**.

### Why this matters for vibe coders
- Your **GitHub PAT was the only credential needed** — no npm token, no 2FA bypass, no provenance abuse. If you use Claude Code / Cursor / OpenHands with a long-lived GitHub PAT in your shell or in `~/.claude/settings.json`, that PAT is in the same risk class as the ones stolen in this wave.
- The *source repo* — not the npm account — is the publish-time trust boundary you need to defend. A maintainer republishing from a poisoned `main` will ship clean-looking releases that pass every provenance check.
- **Auto-bot commits are now a phishing surface.** Names like `build-bot` and `pipeline-bot` look ignorable in a long PR list. They're not.

## Am I affected?

### Check if your GitHub account is in the leaked-credential pool
If you've ever installed an Open VSX extension, run unverified VS Code Marketplace extensions, or your machine has been on the receiving end of a Lumma / RedLine / Atomic Stealer infection in the last year — assume your GitHub PAT is in scope.

### Check your repos for Megalodon's IOCs

```bash
# Recent commits authored by the throwaway bot identities, since 2026-05-17
gh api graphql -f query='
  query($owner:String!, $repo:String!) {
    repository(owner:$owner, name:$repo) {
      defaultBranchRef { target { ... on Commit {
        history(since:"2026-05-17T00:00:00Z", first:100) {
          nodes { oid messageHeadline committedDate author { name email } }
        }
      }}}
    }
  }' -f owner=YOUR_ORG -f repo=YOUR_REPO \
  | jq '.data.repository.defaultBranchRef.target.history.nodes[]
        | select(.author.name | test("^(build-bot|auto-ci|ci-bot|pipeline-bot)$"))'

# Workflow files added or modified since 2026-05-17
git log --since=2026-05-17 --name-status --diff-filter=AM -- '.github/workflows/*.yml' '.github/workflows/*.yaml'

# Grep for the base64-bash pipe pattern (the literal Megalodon shape)
grep -RIE 'base64 -d[[:space:]]*\|[[:space:]]*bash' .github/workflows/ 2>/dev/null

# Look for the SysDiag / Optimize-Build workflow names
grep -RIlE '(SysDiag|Optimize-Build)' .github/workflows/ 2>/dev/null

# Outbound connections to the C2 (if you have CI egress logs)
grep -F '216.126.225.129' /var/log/*  2>/dev/null
```

### If you depend on `@tiledesk/tiledesk-server`

```bash
# Are you on a poisoned version?
npm ls @tiledesk/tiledesk-server 2>/dev/null
# Affected: 2.18.6, 2.18.7, 2.18.8, 2.18.9, 2.18.10, 2.18.11, 2.18.12
# Downgrade to 2.18.5 or wait for a clean release ≥ 2.18.13
```

If any of these turn up positive, treat every credential reachable from the runner *and* from a developer machine that ran the workflow locally as compromised.

### IOCs

| Type | Value |
|---|---|
| Campaign | **Megalodon** (SafeDep naming) |
| First commit wave | **2026-05-18**, ~6-hour burst |
| Scope | **5,718 malicious commits across 5,561 GitHub repositories** |
| Variants | `SysDiag` (mass, new workflow on every push/PR) + `Optimize-Build` (targeted, replaces existing workflow with `workflow_dispatch` backdoor) |
| C2 | **`216.126.225.129:8443`** |
| Author masquerade | `build-bot`, `auto-ci`, `ci-bot`, `pipeline-bot` |
| Payload | base64-encoded bash; harvests `$GITHUB_TOKEN`, OIDC, masked CI secrets, AWS / npmrc / SSH / Docker creds, `.env*` files, source secrets |
| Confirmed npm impact | **`@tiledesk/tiledesk-server`** versions **2.18.6 → 2.18.12** (published 2026-05-19 → 2026-05-21) |
| Attribution | Unknown actor; **distinct from TeamPCP**; credentials harvested from infostealer ecosystem (Hudson Rock: 331/978 accounts = ~33% known infostealer victims) |
| Likely upstream | [GlassWorm](2025-10-glassworm-vscode-worm.md) and adjacent infostealer waves (Lumma, RedLine, AMOS) |
| Official advisory | [CISA — Supply Chain Compromises Impact Nx Console and GitHub Repositories (2026-05-28)](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories) |

## If you are affected
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md) — for the `@tiledesk/tiledesk-server` arm
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if a poisoned workflow ran in CI

Revert any auto-bot-authored workflow change made after **2026-05-17 23:00 UTC**, rotate every CI secret the affected workflow could have read, and audit `pull_request_target` / `workflow_dispatch` permissions on any repo that even briefly carried the payload.

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — the source-repo-is-publish-trust angle
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — long-lived PAT minimization
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — Claude Code / Cursor / OpenHands shouldn't hold a GitHub PAT broader than the task they're running
→ **Require signed commits on protected branches** (Megalodon's `build-bot`-authored commits would have failed verification).
→ **Audit `.github/workflows/` on every merge** — even a one-file change to a workflow is a privileged change.
→ Run [`zizmor`](https://github.com/woodruffw/zizmor) and pin third-party Actions by commit hash, not by tag (the same root cause as the [Axios → OpenAI macOS cert rotation](2026-03-axios-compromise.md): a floating tag let the malicious action version slip into a privileged workflow).

## Sources
- [SafeDep — Megalodon: Mass GitHub Repo Backdooring via CI Workflows](https://safedep.io/megalodon-mass-github-repo-backdooring-ci-workflows/) — canonical reverse-engineering, named the campaign
- [StepSecurity — Megalodon: Mass GitHub Actions Secret Exfiltration Across 5,500+ Public Repositories](https://www.stepsecurity.io/blog/megalodon-mass-github-actions-secret-exfiltration-across-5-500-public-repositories) — IOC list, two-variant breakdown
- [SecurityWeek — Over 5,500 GitHub Repositories Infected in 'Megalodon' Supply Chain Attack](https://www.securityweek.com/over-5500-github-repositories-infected-in-megalodon-supply-chain-attack/) — scope confirmation, Hudson Rock infostealer-cascade attribution
- [The Hacker News — Megalodon GitHub Attack Targets 5,561 Repos with Malicious CI/CD Workflows](https://thehackernews.com/2026/05/megalodon-github-attack-targets-5561.html)
- [Cybersecurity News — Megalodon Malware Compromised 5,500+ GitHub Repos Within 6 Hours](https://cybersecuritynews.com/megalodon-malware-github-repos/) — `@tiledesk/tiledesk-server` version range
- [The Register — Megalodon chums the waters in 5.5K+ GitHub repo poisonings](https://www.theregister.com/security/2026/05/22/megalodon-chums-the-waters-in-55k-github-repo-poisonings/5245342)
- [Dark Reading — 'Megalodon' Malware Infects Thousands of GitHub Repos](https://www.darkreading.com/application-security/megalodon-malware-infects-thousands-github-repos)
- [Hackread — 5,561 GitHub Repositories Hit by Megalodon Supply Chain Attack in Six Hours](https://hackread.com/github-repositories-megalodon-supply-chain-attack/)
- [CyberLeveling — Megalodon: The GitHub Actions Attack That Turned CI/CD Into a Secret-Stealing Machine](https://cyberleveling.com/blog/megalodon-github-actions-cicd-attack-2026)
- [CISA — Supply Chain Compromises Impact Nx Console and GitHub Repositories (2026-05-28)](https://www.cisa.gov/news-events/alerts/2026/05/28/supply-chain-compromises-impact-nx-console-and-github-repositories) — official US-government bundled alert (Megalodon + Nx Console)
- [Cybersecurity Dive — CISA urges security teams to check for software development compromises](https://www.cybersecuritydive.com/news/cisa-security-software-supply-chain-compromises-GitHub/821487/)
