---
id: 2026-11-n8n-security-update-november-26-expression-sandbox-escape-chroma-redaction-websocket
title: "n8n 2026-11-26: four advisories, one High expression sandbox escape to code execution; fixed in 1.123.102, 2.49.7, 2.50.2 and Docker 3.4.1"
date_disclosed: 2026-11-26
last_updated: 2026-11-26
severity: high
status: patched
ecosystems: [npm, docker, n8n, workflow-automation]
tools_affected: ["n8n self-hosted below 1.123.102, 2.49.7 or 2.50.2", "n8nio/n8n Docker images below 3.4.1", "n8n instances with CHROMA_API_KEY set in the process environment"]
tags: [vendor-batch, sandbox-escape, code-execution, expression-sandbox, credential-exposure, redaction-bypass, denial-of-service, no-cve, patched]
---

## TL;DR

[n8n's bulletin of 2026-11-26](https://community.n8n.io/t/security-update-26-november-2026/331111) lists four advisories. The High one lets a user who can create and run workflows escape the expression sandbox and run code in the main n8n process. One Moderate flaw needs no login and can stop the server from responding. Upgrade self-hosted n8n to 1.123.102, 2.49.7 or 2.50.2, or to Docker image 3.4.1. n8n says its cloud instances are patched. No advisory carried a CVE when read on 2026-11-26.

## What happened

The bulletin lists four advisories and four fixed lines: "v1 patched in v1.123.102", "v3 patched in v3.4.1", "beta patched in v2.50.2" and "stable patched in v2.49.7". The vendor tab showed the same four rows dated 2026-11-26.

| Advisory | Severity, CVSS 4.0 | Who can do it | Affected, as printed | Patched, as printed |
|---|---|---|---|---|
| [GHSA-w6f8-8qh4-h3j4](https://github.com/n8n-io/n8n/security/advisories/GHSA-w6f8-8qh4-h3j4) Expression sandbox escape allows code execution in the main process | High, 7.7 | a user who can create and run workflows | npm `< 2.49.2`, Docker `< 3.4.0` | npm `>= 2.49.2`, Docker `>= 3.4.0` |
| [GHSA-g45f-rmpv-24vc](https://github.com/n8n-io/n8n/security/advisories/GHSA-g45f-rmpv-24vc) Chroma Vector Store node gives members access to the host's Chroma Cloud account | Moderate, 5.8 | a member who can create credentials and run workflows, when `CHROMA_API_KEY` is set on the host | npm `< 2.49.0`, Docker `< 3.3.0` | npm `>= 2.49.0`, Docker `>= 3.3.0` |
| [GHSA-rqx8-m8xf-23ff](https://github.com/n8n-io/n8n/security/advisories/GHSA-rqx8-m8xf-23ff) Execution data redaction sends unredacted node errors to the editor | Moderate, 5.3 | a user who can run workflows from the editor, when execution data redaction is enabled | npm `< 2.50.2` and `< 2.49.7`, Docker `< 3.4.1` | npm 2.50.2 and 2.49.7, Docker 3.4.1 |
| [GHSA-p3cc-p7wp-f2x7](https://github.com/n8n-io/n8n/security/advisories/GHSA-p3cc-p7wp-f2x7) Unclaimed WebSocket upgrade requests exhaust file descriptors | Moderate, 6.9 | anyone who can reach the n8n HTTP port, no login | npm `< 1.123.102`, `< 2.50.2`, `< 2.49.7`, Docker `< 3.4.1` | npm 1.123.102, 2.50.2, 2.49.7, Docker 3.4.1 |

The bulletin rates the three Moderate advisories "Medium".

The sandbox escape advisory says n8n ran expressions in a V8 isolate, and a flaw in the bundled V8 engine let a crafted expression corrupt memory and leave the isolate. Code then runs with the privileges of the n8n service user. The advisory also names pointer-compression images 2.47.6-pc, 2.48.3-pc and 3.2.2-pc as fixed.

The Chroma advisory says the node accepted a Chroma Cloud credential with an empty API key, and the client then used the key in the n8n process environment. A member could read, overwrite or delete the host's collections.

The redaction advisory says the node status message sent to the editor held the full error object, which can include request URLs, response bodies or values taken from credentials.

Registry facts, read 2026-11-26:

| Version | Channel | Published |
|---|---|---|
| 2.49.0 | npm | 2026-11-17 |
| 2.49.2 | npm | 2026-11-19 |
| 1.123.102, 2.50.2, 2.49.7 | npm | 2026-11-26 |
| 3.3.0 | Docker Hub `n8nio/n8n` | 2026-11-17 |
| 3.4.0 | Docker Hub `n8nio/n8n` | 2026-11-24 |
| 3.4.1 | Docker Hub `n8nio/n8n` | 2026-11-26 |

npm has no `n8n` 3.x version. The 3.x line the bulletin and the advisories name exists as Docker image tags. npm dist-tags were `latest` and `stable` 2.49.7, `beta` and `next` 2.50.2, and `rc` 1.123.102.

The sandbox escape advisory lists npm `< 2.49.2` as affected and names no 1.x fixed version. The bulletin says the batch is fixed on the 1.x line in 1.123.102.

## Am I affected?

- Run `n8n --version`, or read the image tag of your container. Below 1.123.102 on 1.x, below 2.49.7 on 2.49.x, below 2.50.2 on 2.50.x, or a Docker 3.x tag below 3.4.1 is inside at least one range.
- The sandbox escape matters most where people you do not fully trust can create or edit workflows.
- The Chroma flaw applies only when `CHROMA_API_KEY` is set in the n8n process environment.
- The WebSocket flaw applies to any instance whose HTTP port an untrusted client can reach.

## If you are affected

1. Upgrade to 1.123.102, 2.49.7, 2.50.2 or Docker 3.4.1, or later on the same line.
2. Until then, remove workflow creation and editing access from users who are not fully trusted. n8n says this does not fully remove the risk.
3. If `CHROMA_API_KEY` was set on the host, rotate the Chroma Cloud API key and check its collections for unexpected changes, as the advisory says. Remove the variable if it is not needed, or add `@n8n/n8n-nodes-langchain.vectorStoreChromaDB` to `NODES_EXCLUDE`.
4. If untrusted users could run workflows on a version inside the sandbox escape range, treat credentials stored in n8n as readable by them and rotate. See [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
5. For the WebSocket flaw, n8n's workaround is to have the reverse proxy forward WebSocket upgrades only for the editor and chat paths.

## Prevention

- Keep self-hosted n8n on the newest patch of its line. n8n publishes a bulletin every two weeks.
- Do not expose the n8n HTTP port beyond the clients that need it. See [CI/CD hardening](../prevention/ci-cd-hardening.md).
- Keep provider keys out of the process environment of a multi-user instance. See [credential hygiene](../prevention/credential-hygiene.md).

## Sources

Single source: the vendor.

- [n8n community: Security update, 26 November 2026](https://community.n8n.io/t/security-update-26-november-2026/331111), posted 2026-11-26 09:40 UTC, read through the topic's JSON. The four advisories and the fixed lines.
- [n8n advisories tab](https://github.com/n8n-io/n8n/security/advisories), page 1 read 2026-11-26: four rows dated 2026-11-26.
- The four advisory pages linked in the table, each read 2026-11-26. Each printed "No known CVE".
- `registry.npmjs.org/n8n` `time` and `dist-tags`, and the Docker Hub tag API for `n8nio/n8n`, read 2026-11-26.
- Not available: OSV had no record for any of the four ids on 2026-11-26.
