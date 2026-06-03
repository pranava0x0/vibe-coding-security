---
id: 2026-03-trivy-litellm-supply-chain
title: "TeamPCP breaches Trivy GitHub Actions → LiteLLM 1.82.7–1.82.8 backdoored (March 2026)"
date_disclosed: 2026-03-12
last_updated: 2026-06-03
severity: critical
status: contained
ecosystems: [pypi, ci-cd, github-actions]
tools_affected: [litellm, trivy, aquasecurity-trivy-action]
tags: [supply-chain, ci-cd, github-actions, credential-theft, pypi, security-scanner-as-vector, teamPCP, litellm]
---

## TL;DR
TeamPCP force-pushed malicious tags across **75 of 76 `aquasecurity/trivy-action` release tags**, injecting a malicious `entrypoint.sh`. Any CI pipeline running an unpinned `uses: aquasecurity/trivy-action@*` leaked its `GITHUB_TOKEN`, CI secrets, and cloud credentials. LiteLLM's pipeline was hit: **versions 1.82.7 and 1.82.8** (~3.4M daily downloads) were backdoored for roughly 3 hours before removal. Cisco's source code was stolen in a related breach. First documented case of a **security scanning tool itself weaponized as a supply-chain attack vector**.

## What happened
On **2026-03-11 to 2026-03-12**, TeamPCP (PCPcat/DeadCatx3/UNC6780) compromised the **`aquasecurity/trivy-action`** GitHub repository — the official GitHub Actions wrapper for the Trivy vulnerability scanner — and **force-pushed malicious replacements onto 75 of 76 existing version tags**. The injected `entrypoint.sh` exfiltrated `$GITHUB_TOKEN`, masked CI secrets, AWS/GCP/Azure credentials, `.env*` files, and SSH keys.

Because the attack targeted **existing tags** (not a new version), any CI workflow pinned to a tag like `v0.20.0` rather than a full commit SHA received the malicious entrypoint automatically — the tag pointer was silently re-aimed.

### LiteLLM downstream impact
BerriAI's **LiteLLM** used `trivy-action` in its release pipeline. When the poisoned tag fired, it exfiltrated LiteLLM's **PyPI publish token**. TeamPCP used that token to push **LiteLLM 1.82.7 and 1.82.8** (both backdoored) to PyPI. The malicious versions were live for approximately **3 hours** before detection and removal.

LiteLLM is a unified proxy that aggregates API keys for **OpenAI / Anthropic / AWS Bedrock / Azure / Vertex / Cohere / Mistral** for every organization that deploys it — the downstream credential blast radius is disproportionate to the 3-hour window.

### Cisco downstream impact
A separate CI pipeline at Cisco was also caught by the compromised Trivy action; Cisco confirmed internal source-code repository access was lost. Full extent was not publicly disclosed.

### Scale
- **Affected Trivy action tags:** 75 of 76 (essentially all historical versions)
- **Dependent CI workflows:** 1,705 PyPI packages traced their release pipelines to `trivy-action`; additional npm / Docker / internal projects not fully enumerated
- **LiteLLM exposure window:** ~3 hours (1.82.7 + 1.82.8)
- **LiteLLM daily downloads:** ~3.4M

## Am I affected?

```bash
# Do any of your workflow files use trivy-action by tag (not pinned SHA)?
grep -r "aquasecurity/trivy-action@" .github/workflows/ 2>/dev/null | grep -v '@[a-f0-9]\{40\}'

# Is a vulnerable LiteLLM version pinned in any lockfile?
grep -r "litellm==" requirements*.txt poetry.lock Pipfile.lock 2>/dev/null | grep '1\.82\.[78]'
pip list 2>/dev/null | grep -i litellm | grep '1\.82\.[78]'
```

If any CI workflow ran `aquasecurity/trivy-action` by tag (not SHA) between **2026-03-11 and 2026-03-13**, treat every secret the runner had access to as compromised.

### IOCs

| Type | Value |
|---|---|
| Compromised action | `aquasecurity/trivy-action` (75/76 tags force-pushed) |
| Backdoored PyPI versions | `litellm==1.82.7`, `litellm==1.82.8` |
| Actor | TeamPCP (PCPcat / DeadCatx3 / UNC6780) |
| Exposure window | 2026-03-11 → 2026-03-13 (CI); ~3h (PyPI) |
| Novel attack pattern | Security-scanner-as-supply-chain-vector |

## If you are affected
1. **Rotate all CI secrets** that ran in a pipeline using `trivy-action` by tag in the affected window: `GITHUB_TOKEN` (scoped to repo — check if it had write access), npm tokens, PyPI tokens, AWS/GCP/Azure OIDC tokens and access keys, Docker Hub tokens.
2. **Check if your PyPI or npm token was used to publish packages** outside your normal cadence in March 2026. Review your package release history for unexpected versions.
3. **Upgrade LiteLLM** past 1.82.8: `pip install 'litellm>=1.83.0'` (run `1.83.10-stable` per LiteLLM docs).
4. **Pin Trivy action to a SHA, not a tag**: `uses: aquasecurity/trivy-action@<full-40-char-sha>`. Re-verify the SHA against the official release.
5. **Audit dependent packages.** If you maintain a PyPI package whose release pipeline used `trivy-action`, check whether your own token was exposed and whether any unexpected versions were pushed.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)
→ **Always pin GitHub Actions to full commit SHAs**, not tags or branches. Tags are mutable references; a force-push to a tag is indistinguishable from a normal push unless you pin the SHA. Use tools like StepSecurity's Harden-Runner or GitHub's `pin-github-action` script.
→ **Security tools are not immune to supply-chain attacks.** `trivy-action`, `snyk-action`, `semgrep-action` etc. run with the same CI permissions as any other action. Pin them with the same rigor you'd apply to a code dependency.
→ **Scope CI secrets minimally.** The `GITHUB_TOKEN` used in a scanning step should have read-only scope if the action only needs to read code. A `PYPI_TOKEN` should never be present in the same job as a security-scanner step.

## Sources
- [The Hacker News — TeamPCP Poisons Trivy Security Scanner GitHub Action, Backdoors LiteLLM PyPI Packages](https://thehackernews.com/2026/03/teampcp-poisons-trivy-security-scanner.html)
- [BleepingComputer — Trivy GitHub Action compromised, LiteLLM 1.82.7/1.82.8 backdoored](https://www.bleepingcomputer.com/news/security/trivy-github-action-compromised-litellm-backdoored-march-2026/)
- [StepSecurity — Compromised GitHub Actions: aquasecurity/trivy-action tag-force-push attack](https://www.stepsecurity.io/blog/compromised-github-actions-trivy-action-tag-force-push)
- [Snyk Security — Supply chain attack on trivy-action: how pinning to SHA protects you](https://snyk.io/blog/supply-chain-attack-trivy-action-sha-pinning/)
- [The Register — Security scanner becomes supply chain attack vector in TeamPCP campaign](https://www.theregister.com/2026/03/13/teampcp_trivy_litellm_supply_chain/)
- [SecurityWeek — TeamPCP Turns Security Scanner Into Supply Chain Attack Vector](https://www.securityweek.com/teampcp-turns-security-scanner-into-supply-chain-attack-vector/)
