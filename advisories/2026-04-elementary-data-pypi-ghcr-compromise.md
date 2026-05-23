---
id: 2026-04-elementary-data-pypi-ghcr-compromise
title: "elementary-data PyPI + GHCR compromise — malicious .pth auto-exec (April 2026)"
date_disclosed: 2026-04-24
last_updated: 2026-05-23
severity: critical
status: contained
ecosystems: [pypi, docker]
tools_affected: [elementary-data, dbt, data-engineering, ci-cd, any-python-project]
tags: [supply-chain, credential-theft, github-actions, script-injection, pth-execution, docker-poisoning, forged-release]
---

## TL;DR
On **2026-04-24**, attackers published a malicious **`elementary-data==0.23.3`** to PyPI (uploaded 22:20:47 UTC) and **poisoned the matching Docker images on GHCR** (`ghcr.io/elementary-data/elementary`). The package — a popular **dbt data-observability** tool with **~1M+ monthly downloads** — shipped a single weaponized addition: a top-level **`elementary.pth`** file. Python auto-execs `.pth` lines that start with `import` **at every interpreter startup**, so the three-stage infostealer fired on *any* Python invocation in an environment where it was installed. The attacker got in via a **GitHub Actions script-injection** flaw in the project's own workflow, then used the workflow's `GITHUB_TOKEN` to **forge a signed release commit and dispatch the legitimate publishing pipeline against it**. Fixed in **0.23.4**; `:latest` GHCR tag now resolves clean.

## What happened
The root cause was a **script-injection vulnerability in one of Elementary's own GitHub Actions workflows**. The attacker injected commands that ran with the workflow's `GITHUB_TOKEN`, used it to **forge a signed release commit**, and then **dispatched the project's real publishing pipeline** against that commit — so the malicious `0.23.3` was shipped by the legitimate release automation (the same "hijack the real pipeline" shape behind the [TanStack/Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md) provenance abuse, here applied to PyPI + GHCR rather than npm).

Both the wheel and the sdist contained one malicious file: **`elementary.pth`**. `.pth` files in `site-packages` are a Python packaging mechanism — but Python **executes any line beginning with `import`** when the interpreter starts. That turns a "data file" into an **auto-run primitive**: the payload executes on every `python`, `dbt`, `pytest`, etc., run, with no import of the package required.

The payload is a **three-stage information stealer** that hunts developer secrets:
- **Cloud access tokens** (AWS / GCP / Azure), **SSH private keys**, **Kubernetes credentials**, and **cryptocurrency wallets**.

The **GHCR Docker images were poisoned in lockstep**: every unpinned `docker pull ghcr.io/elementary-data/elementary` and every `FROM ghcr.io/elementary-data/elementary` without a pinned digest/tag pulled the **trojaned image** from 2026-04-24 until cleanup. The Elementary team removed `0.23.3` from PyPI and the malicious GHCR image, then published a clean **0.23.4** (and re-pointed `:latest`).

## Am I affected?
You are affected if you installed `elementary-data==0.23.3` from PyPI **or** pulled an unpinned `ghcr.io/elementary-data/elementary` image after 2026-04-24.

```bash
# PyPI side: is the bad version present?
pip show elementary-data 2>/dev/null | grep -i version
pip freeze 2>/dev/null | grep -i '^elementary-data==0.23.3'

# The smoking gun: a .pth file that runs code at interpreter startup
find "$(python -c 'import site; print(site.getsitepackages()[0])')" -name 'elementary.pth' 2>/dev/null -exec cat {} \;

# Docker side: did you pull/build on an unpinned tag after 2026-04-24?
docker images 'ghcr.io/elementary-data/elementary' --format '{{.Repository}}:{{.Tag}} {{.CreatedAt}} {{.Digest}}'
grep -rn 'ghcr.io/elementary-data/elementary' Dockerfile* docker-compose*.yml 2>/dev/null
```

If `elementary.pth` exists (or you ran an unpinned image after the window): **assume cloud tokens, SSH keys, K8s creds, and any wallet material on that host/CI runner are compromised.** Rotate everything and rebuild from a clean, pinned image.

### IOCs

| Type | Value |
|---|---|
| Malicious PyPI version | `elementary-data==0.23.3` (uploaded 2026-04-24 22:20:47 UTC) |
| Malicious container | `ghcr.io/elementary-data/elementary` (unpinned tags, from 2026-04-24) |
| Execution primitive | top-level **`elementary.pth`** auto-exec at Python startup |
| Initial access | GitHub Actions **script injection** → `GITHUB_TOKEN` → forged signed release → real publish pipeline |
| Payload | 3-stage infostealer: cloud tokens, SSH keys, K8s creds, crypto wallets |
| Fixed version | **0.23.4** (PyPI); clean `:latest` re-published on GHCR |

## If you are affected
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — cloud tokens, SSH keys, K8s creds first.
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — especially for CI runners that built/ran the image.
→ Rebuild any image derived from `ghcr.io/elementary-data/elementary` from a **pinned, post-fix digest**; redeploy.

## Prevention
→ [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) — flag `.pth` files in dependencies; they're a known auto-exec vector.
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ **Pin container images by digest** (`@sha256:...`), not floating tags — a poisoned `:latest` reaches everyone who pulls.
→ Harden your own GitHub Actions against script injection: never interpolate untrusted `${{ }}` context into `run:` steps; scan workflows with [`zizmor`](https://github.com/woodruffw/zizmor); restrict `GITHUB_TOKEN` to least privilege.

## Sources
- [Elementary Data — Security Incident Report: Malicious release of Elementary OSS Python CLI v0.23.3](https://www.elementary-data.com/post/security-incident-report-malicious-release-of-elementary-oss-python-cli-v0-23-3) — vendor postmortem, timeline, fix.
- [StepSecurity — elementary-data Compromised on PyPI and GHCR: Forged Release Pushed via GitHub Actions Script Injection](https://www.stepsecurity.io/blog/elementary-data-compromised-on-pypi-and-ghcr-forged-release-pushed-via-github-actions-script-injection) — initial-access analysis.
- [Snyk — Malicious Release of elementary-data PyPI Package Steals Cloud Credentials from Data Engineers](https://snyk.io/blog/malicious-release-of-elementary-data-pypi-package-steals-cloud-credentials-from-data-engineers/) — `.pth` payload + infostealer detail.
- [Cybersecurity News — Popular PyPI Package With 1 Million Monthly Downloads Hacked to Inject Malicious Scripts](https://cybersecuritynews.com/pypi-package-hacked-with-malware/)
- [Chainguard — Chainguard customers safe from elementary-data compromise](https://www.chainguard.dev/unchained/chainguard-customers-safe-from-elementary-data-compromise) — GHCR image-poisoning context.
- [The CyberSec Guru — Elementary-Data PyPI Hack: 1.1M Users Targeted by Infostealer](https://thecybersecguru.com/news/elementary-data-pypi-hack-infostealer/)
