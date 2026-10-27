---
id: 2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0
title: "LiteLLM 1.107.0 root cause: a master key committed to a public repo in May became org-owner GitHub tokens, secret-stealing workflows and a hijacked release"
date_disclosed: 2026-10-21
last_updated: 2026-10-26
severity: critical
status: contained
ecosystems: [pypi, docker, github-actions, litellm, ai-gateway]
tools_affected: ["litellm 1.107.0 (PyPI, 2026-10-21 11:39 to 13:23 UTC)", "ghcr.io/berriai/litellm and docker.io/litellm tags v1.107.0, latest, main-latest, main-stable (11:46 to 14:20 UTC)", "any host that ran the LiteLLM proxy with a long-lived master key in a committed config", "any GitHub organisation whose CI secrets are readable by a workflow pushed from a stolen owner token"]
tags: [supply-chain, litellm, pypi, docker, github-actions, credential-theft, secret-exfiltration, master-key, force-push, branch-protection, release-hijack, lookalike-org, incident-response, second-compromise]
---

## TL;DR
LiteLLM's root-cause post (2026-10-23) says the 2026-10-21 PyPI and Docker compromise began with an `opencode.json` carrying the company's Agent Platform master key, committed to the public `LiteLLM-Labs/lite-harness` repository on 2026-05-27, force-pushed over and never revoked. On 2026-10-10 an attacker used that key to obtain an organisation owner's GitHub CLI OAuth token from the platform, pushed throwaway `ci-tmp-*` branches whose workflows posted six organisation secrets, including a maintainer `GH_TOKEN`, to a webhook-capture service, deleted the runs, and repeated it on 10-12 across private repositories for fourteen more. On 10-21 the attacker disabled branch protection, force-pushed a release workflow pointed at a lookalike `Berri-AI/litellm` organisation, approved the production gate with a second stolen maintainer token and published seven backdoored wheels and four Docker tags; PyPI quarantined the release within 1h44m, after about 49,000 downloads (Wiz, cited by The Register). The vendor has locked registries, removed organisation members, revoked every token and withdrawn its earlier "tokens taken from logs" explanation. Artifacts, hashes and host indicators are in [the companion blocklist](2026-10-litellm-1-107-0-pypi-docker-malicious-artifacts.md).

## What happened

**The key.** Per the vendor's attack-chain post, at 2026-05-27 18:53 UTC a developer committed `opencode.json` containing the Agent Platform master key to the public `LiteLLM-Labs/lite-harness` repository, then force-pushed the commit away. The key stayed valid. Socket's reconstruction and The Hacker News carry the same account.

**First use, 2026-10-10.** From 21:13 to 21:28 UTC the attacker called the Agent Platform API with the master key and at 21:27 obtained an organisation owner's GitHub CLI OAuth token, post-2FA and owner-scoped. At 22:11:45 a workflow on branch `ci-tmp-a351cc` in `BerriAI/litellm` (commit `b69bc36`, `.github/workflows/cache.yml`, per Socket) sent six organisation secrets to a webhook-capture service: `GH_TOKEN`, `PROVIDER_INFO_SYNC_APP_ID`, `PROVIDER_INFO_SYNC_PRIVATE_KEY`, `LINEAR_API_KEY`, `LITELLM_API_KEY`, `TOGETHER_API_KEY`. At 22:12:09 `ci-tmp-be33e9` in `BerriAI/litellm-auto` took `RELEASE_PLEASE_TOKEN`. The runs were deleted at 22:14. Socket attributes the pushes to the `ishaan-berri` account, meaning the credential, not the person.

**Second round, 2026-10-12.** Between 12:08 and 12:30 UTC a workflow on `ci-tmp-4d8517` (commit `1a6e3c1`) ran across private repositories and took fourteen more secrets, among them `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GITGUARDIAN_API_KEY`, `DATABASE_URL`, Redis credentials and a Linear browser-session blob (Socket). Socket's host indicators for these workflows are `/tmp/c.env` and `/tmp/c.b64`.

**Release hijack, 2026-10-21.** At 10:08 UTC a commit repointing the release workflow at a fork was rejected by branch protection; the attacker disabled the protections and force-pushed. At 10:46 the staging pipeline was dispatched from commit `20535d8f` in the lookalike organisation `Berri-AI/litellm`. At 11:11:18 the production gate was approved with a second maintainer's token. 11:39 to 11:40: seven wheels and the sdist to PyPI; 11:46: Docker Hub and GHCR tags; 11:53: run records deleted. At 12:06 a community member (LidorMachluf) opened issue #47826; 12:09 to 12:24 the changes were reverted and `main` force-pushed back to `d687b69`; incident response began 13:02; PyPI quarantine completed by 13:23; Docker tags removed 14:19 to 14:20 (GHCR by 13:51 per the first incident post).

**Correction and changes.** The first vendor post said the tokens had been read from CI logs; the 10-23 post withdraws that and names the master key. Credits: LidorMachluf, Karlo Zanki (Socket), Trail of Bits (Asritha Bodepudi, Evan Sultanik). Registries locked, organisation members removed, every token revoked, and the next release drops the eMudhra CA from the bundled trust store.

**Payload, briefly.** Wiz and SafeDep: the wheels place `cook.pth`, `cook.py` and `sitecustomize.py` in `site-packages`, so every Python process on the host runs the stealer whether or not it imports `litellm`; it collects SSH, cloud, CI, browser and AI-provider credentials plus the proxy's credential table, and a detached hourly loader fetched a second-stage address from a GitHub account deleted about two hours after release. Wiz observed stolen AWS instance-role credentials validated and used for Bedrock and IAM enumeration from two IPs. Hashes are in the blocklist file.

Why it is here: the second LiteLLM compromise in seven months ([March, via Trivy](2026-03-trivy-litellm-supply-chain.md)); the proxy fronts every provider key a team owns; and the chain is one vibe-coding stacks reproduce daily: an agent-platform config with a master key, committed, "removed" by force-push, never rotated.

## Am I affected?

- `pip show litellm` and lockfiles for `1.107.0`; images for the four tags or the digest in the blocklist. Clean pins: `1.106.2`, `1.107.0rc1`, `1.107.0rc2` (SafeDep).
- Hosts: the three files in `site-packages`, `/tmp/.pc_once_72129118c59f5636c0bb`, `/tmp/remote_code_loader.lock`, `PRIVCOLLECT_ACTIVE=1` in a process environment, a detached Python process with parent PID 1 and working directory `/` (SafeDep, Wiz).
- Your own organisation: audit log for `ci-tmp-` branches with workflow runs deleted within minutes, disabled branch protection, force-pushes to `main`, release approvals from accounts that did not act. [Gheist](2026-10-gheist-stolen-github-tokens-ci-sync-branches-actions-log-secret-exfiltration.md) uses the same shape under `ci-sync-`.

## If you are affected

1. Remove the package, delete the three files, kill the detached process, rebuild the host where you can; assume second-stage code may have run (SafeDep).
2. Rotate from a clean machine: every provider key the proxy held, cloud and instance-role credentials, SSH, GitHub and npm/PyPI tokens, browser-saved passwords. [If you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md) covers the credential set; [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) for the role credentials Wiz saw used.
3. Review cloud logs for `sts:GetCallerIdentity`, `bedrock:ListFoundationModels` and IAM `List*` calls from unfamiliar sources after 2026-10-21 11:39 UTC (Wiz).
4. If your organisation has a master key or admin token in any committed file, force-pushed or not, rotate it today; history rewriting is not revocation.

## Prevention

- [Credential hygiene](../prevention/credential-hygiene.md): a force-push does not revoke; secrets in config files need the same rotation as a leak.
- [CI/CD hardening](../prevention/ci-cd-hardening.md): environment-scoped secrets with required reviewers, no owner-level OAuth tokens in automation, alerts on branch-protection changes and deleted runs.
- [npm hardening](../prevention/npm-hardening.md) and [package vetting](../prevention/package-vetting-checklist.md): cooldown on fresh releases of packages that hold provider keys.

## Sources
- [LiteLLM — Security incident, October 21 2026: the attack chain](https://docs.litellm.ai/blog/security-incident-oct-21-2026-attack-chain) — fetched 2026-10-26: the 2026-05-27 `opencode.json` commit, the 10-10 and 10-12 timelines, the 10-21 release hijack, the correction of the log hypothesis, credits, remediation.
- [LiteLLM — Security incident, October 21 2026](https://docs.litellm.ai/blog/security-incident-oct-21-2026) — fetched 2026-10-26: PyPI window 11:39 to 13:23 UTC, Docker tags and removal times, clean pin.
- [Socket — New evidence shows LiteLLM secret-stealing workflows ran 11 days before supply chain attack](https://socket.dev/blog/litellm-attack-timeline) — fetched 2026-10-26: commits `b69bc36` and `1a6e3c1`, the two secret lists, the `ishaan-berri` attribution, host indicators.
- [The Hacker News — Leaked LiteLLM master key let attackers steal GitHub tokens and hijack release pipeline](https://thehackernews.com/2026/10/leaked-litellm-master-key-let-attackers.html) — fetched 2026-10-26: independent account of the chain.
- [The Register — LiteLLM compromise traced to a master key left in a public repo](https://www.theregister.com/2026/10/26/litellm_master_key/5305544) — fetched 2026-10-26: the ~49,000-download figure attributed to Wiz.
- [Wiz — LiteLLM compromised: credential stealer in 1.107.0](https://www.wiz.io/blog/litellm-compromised-steals-credentials) — fetched 2026-10-26: payload behaviour, file hashes, the AWS post-exploitation calls.
- [SafeDep — Compromised LiteLLM 1.107.0 on PyPI](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor) — fetched 2026-10-26: wheel hashes, the hourly loader, host and network indicators, clean versions.
- Related in this corpus: [March 2026 Trivy-sourced LiteLLM compromise](2026-03-trivy-litellm-supply-chain.md), [the 1.107.0 blocklist](2026-10-litellm-1-107-0-pypi-docker-malicious-artifacts.md), [Gheist](2026-10-gheist-stolen-github-tokens-ci-sync-branches-actions-log-secret-exfiltration.md).
