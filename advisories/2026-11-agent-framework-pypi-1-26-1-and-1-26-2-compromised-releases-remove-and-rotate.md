---
id: 2026-11-agent-framework-pypi-1-26-1-and-1-26-2-compromised-releases-remove-and-rotate
title: "Compromised agent-framework 1.26.1 and 1.26.2 on PyPI: pin 1.26.0, rotate Azure, GitHub and registry credentials"
kind: malicious-artifact
date_disclosed: 2026-11-17
last_updated: 2026-11-18
severity: high
status: contained
ecosystems: [pypi, github-actions, azure]
tools_affected: ["agent-framework (Microsoft Agent Framework, PyPI) 1.26.1 and 1.26.2", "CI pipelines and containers that installed agent-framework on 2026-11-17 without a pin"]
tags: [supply-chain, malicious-package, pypi, compromised-release, microsoft, agent-framework, credential-rotation]
---

## TL;DR
Remove `agent-framework` 1.26.1 and 1.26.2 from every environment and pin 1.26.0. [PyPI's advisory](https://osv.dev/vulnerability/PYSEC-2026-4388) says both were uploaded without authorization on 2026-11-17. If either was installed, rotate every credential that environment could reach, starting with Azure, Azure DevOps, GitHub and package registry credentials.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| PyPI | `agent-framework` | 1.26.1, 1.26.2 | pin 1.26.0 (published 2026-11-12) | both removed, newest is 1.26.0 (2026-11-18) | PYSEC-2026-4388, MAL-2026-20101 |

- [Wiz](https://www.wiz.io/blog/malicious-version-of-microsofts-agent-framework-published-to-pypi) and [Aikido](https://www.aikido.dev/blog/two-malicious-agent-framework-releases-hit-pypi-in-33-minutes) give 20:35 UTC on 2026-11-17 for 1.26.1 and about 21:08 UTC for 1.26.2.
- Aikido says both were removed by 21:20 UTC. Wiz says both were gone by about 21:30 UTC.
- A loose requirement such as `agent-framework>=1.26` resolved to a bad version during that window.
- PYSEC-2026-4388 credits Wiz, Mike Fiedler and Microsoft. MAL-2026-20101 credits Amazon Inspector, Kamil Mańkowski and OX Security.
- None of the four write-ups read quotes a Microsoft statement. No source read says other Microsoft packages were affected.
- Aikido puts the package at about 190,000 downloads a month.

## Am I affected?

Check without starting Python in the environment you are checking. [SafeDep](https://safedep.io/blog/microsoft-agent-framework-pypi-compromise) gives that advice because the bad releases add startup files.

```bash
# lockfiles and requirements
grep -rnE 'agent[-_]framework.*1\.26\.(1|2)' requirements*.txt pyproject.toml uv.lock poetry.lock Pipfile.lock 2>/dev/null

# installed metadata and the files the two releases leave in site-packages
find / -type d -name 'agent_framework-1.26.[12].dist-info' 2>/dev/null
find / \( -name 'agent_framework_meta.pth' -o -name 'agent_framework_meta' -o -name 'af_runtime_diag.pth' -o -name 'af_runtime_diag.py' \) 2>/dev/null
```

Any hit means the environment is affected. Run the same search inside container images and CI caches built on or after 2026-11-17. Check CI logs for installs of `agent-framework` between 20:35 and 21:30 UTC that day.

## If you are affected

- Rebuild the environment from a clean base with `agent-framework==1.26.0`. Removing the package does not undo what already ran.
- Rotate from a clean machine. The write-ups list these categories:
  - Azure CLI sessions, service principal secrets, and managed identity and federated credentials reachable from the host
  - Azure DevOps personal access tokens and service connections
  - GitHub tokens, and GitHub Actions OIDC trust for workflows with `id-token: write` that installed 1.26.2
  - PyPI, npm and NuGet tokens, Docker registry credentials, Hugging Face tokens and git credentials
  - secrets in environment variables and `.env` files, and secrets of other jobs on shared or self-hosted runners
- Review Entra ID sign-in and activity logs for those identities from the install time onward. Wiz says stolen Azure tokens may remain valid for up to 24 hours.
- Review federated credentials that trust the affected workflows.
- See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md) and [if you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md), whose steps also fit a PyPI package.

## Prevention

- Pin exact versions with hashes, for example with `uv lock` or pip-compile with hash generation. A hash-pinned 1.26.0 could not have resolved to either bad release.
- Delay new releases in CI by a day or more where the resolver supports a cooldown.
- SafeDep advises holding off on new `agent-framework` releases until Microsoft confirms they are clean.
- See [package vetting checklist](../prevention/package-vetting-checklist.md) and [CI/CD hardening](../prevention/ci-cd-hardening.md).

## Sources

- [PYSEC-2026-4388](https://osv.dev/vulnerability/PYSEC-2026-4388): PyPI's advisory, published 2026-11-17, modified 2026-11-18. Read through the OSV API on 2026-11-18.
- [Wiz](https://www.wiz.io/blog/malicious-version-of-microsofts-agent-framework-published-to-pypi): 2026-11-17, times and remediation.
- [Aikido](https://www.aikido.dev/blog/two-malicious-agent-framework-releases-hit-pypi-in-33-minutes): 2026-11-17, times, file names, download figure.
- [SafeDep](https://safedep.io/blog/microsoft-agent-framework-pypi-compromise): 2026-11-18, detection times and file names.
- [Socket](https://socket.dev/blog/agent-framework-pypi-package-compromised-with-credential-stealer): 2026-11-17, file names.
- [The Hacker News](https://thehackernews.com/2026/11/attackers-compromise-microsofts-agent.html): 2026-11-18, lists eight firms that reported it.
- [agent-framework on PyPI](https://pypi.org/project/agent-framework/): version list, read 2026-11-18.
- Not found: a Microsoft post or repository issue. A search of the repository's issues returned 404 when read.
