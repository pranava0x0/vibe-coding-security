---
id: 2026-10-litellm-1-107-0-pypi-docker-malicious-artifacts
title: "Compromised LiteLLM 1.107.0 wheels on PyPI and four Docker tags (2026-10-21, two hours): pin a clean version, remove dropped files, rotate every key"
kind: malicious-artifact
date_disclosed: 2026-10-21
last_updated: 2026-10-26
severity: critical
status: contained
ecosystems: [pypi, docker, ghcr, ai-gateway]
tools_affected: ["litellm 1.107.0 from PyPI between 11:39 and 13:23 UTC on 2026-10-21 (about 49,000 downloads per Wiz)", "ghcr.io/berriai/litellm and docker.io/litellm tags v1.107.0, latest, main-latest, main-stable pulled between 11:46 and 14:20 UTC", "every Python process on a host where the wheel was installed, because the payload loads from site-packages"]
tags: [supply-chain, malicious-package, pypi, docker, litellm, infostealer, pth-loader, sitecustomize, ai-gateway, provider-keys, wiz, safedep]
---

## TL;DR
If `litellm==1.107.0` was installed, or one of the four image tags was pulled, in the window on 2026-10-21, the host ran a credential stealer in every Python process and the proxy's provider-key table was taken. Pin a clean version, remove the dropped files, and rotate from a clean machine. The root cause and timeline are in [the companion advisory](2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0.md).

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| PyPI | `litellm` | 1.107.0 (uploaded 11:39 UTC 2026-10-21, removed 13:23 UTC) | pin `1.106.2` or `1.107.0rc2`; later releases are vendor-stated clean | 1.107.0 removed; `pip index versions litellm` returned nothing in this session (2026-10-26) | vendor incident post; Wiz; SafeDep |
| Docker (GHCR) | `ghcr.io/berriai/litellm` | `v1.107.0`, `latest`, `main-latest`, `main-stable` as pushed 11:46 UTC, replaced 14:20 UTC | re-pull by digest from a current tag | tags replaced (vendor, 2026-10-21) | vendor incident post |
| Docker Hub | `litellm/litellm` | same four tags, same window | re-pull by digest | tags replaced (vendor, 2026-10-21) | vendor incident post |

Markers on an affected host (Wiz, SafeDep): `cook.pth`, `cook.py` and `sitecustomize.py` in the environment's `site-packages`, and an hourly detached process that was not there before. The wheel and image hashes are on the SafeDep and Wiz posts.

## Am I affected?
- `pip show litellm | grep -i version`, lockfiles and `requirements.txt` for `1.107.0`; `docker images --digests | grep litellm` for an image created on 2026-10-21 before 14:20 UTC.
- `ls "$(python -c 'import site;print(site.getsitepackages()[0])')" | grep -E 'cook\.(pth|py)|sitecustomize'` in each virtualenv and container that had the package.
- Cloud audit logs for the instance role of any host that ran the proxy, from 11:39 UTC 10-21 onward.

## If you are affected
1. Stop the proxy, snapshot for evidence, then rebuild the environment from a clean base rather than deleting the three files in place.
2. Rotate from a clean machine: every model-provider key in the proxy's table and in its `.env`, the proxy master key, database credentials, cloud and instance-role credentials, SSH, GitHub, npm and PyPI tokens, browser-saved logins. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md), [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
3. Review provider dashboards for spend and new keys created after the window.

## Prevention
- [Package vetting checklist](../prevention/package-vetting-checklist.md): pin by hash, delay upgrades of gateway software by a day, mirror images by digest.
- [Credential hygiene](../prevention/credential-hygiene.md): the proxy's key table is the highest-value file on the host; keep it in a secrets manager with short-lived access.

## Sources
- [LiteLLM — Security incident, October 21 2026](https://docs.litellm.ai/blog/security-incident-oct-21-2026) — fetched 2026-10-26: the PyPI and Docker windows, the tags, the clean pin.
- [Wiz — LiteLLM compromised: credential stealer in 1.107.0](https://www.wiz.io/blog/litellm-compromised-steals-credentials) — fetched 2026-10-26: the dropped files, hashes, the download figure.
- [SafeDep — Compromised LiteLLM 1.107.0 on PyPI](https://safedep.io/litellm-pypi-compromise-credential-stealer-backdoor) — fetched 2026-10-26: wheel hashes, the hourly process, clean versions.
- Related: [root cause and timeline](2026-10-litellm-agent-platform-master-key-leak-github-token-theft-release-hijack-1-107-0.md), [March 2026 LiteLLM compromise](2026-03-trivy-litellm-supply-chain.md).
