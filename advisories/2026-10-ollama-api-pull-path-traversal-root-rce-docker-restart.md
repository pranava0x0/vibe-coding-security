---
id: 2026-10-ollama-api-pull-path-traversal-root-rce-docker-restart
title: "Ollama: an unauthenticated /api/pull request writes a file outside the model store, and in the default Docker image that is root code execution on the next restart (CVE-2026-103663, CVSS 4.0 9.4, 0.34.2 to 0.34.x, fixed 0.35.0); the tensor-blob redirect SSRF (CVE-2026-85180, 8.7) and the agent-mode approval bypass round out the quarter"
date_disclosed: 2026-10-08
last_updated: 2026-10-09
severity: critical
status: patched
ecosystems: [go, local-llm, docker, ai-infrastructure, self-hosted]
tools_affected: [ollama, "Ollama Docker images", "any agent, IDE plugin or app pointed at an internet-reachable or LAN-reachable Ollama"]
tags: [cve, path-traversal, rce, root, docker, model-pull, ssrf, cloud-metadata, local-llm, exposed-llm-infrastructure]
---

## TL;DR
**Ollama**, the local model server behind most "run it on my own box" vibe-coding setups, shipped a path traversal in the `/api/pull` endpoint: the `digestToPath` function did not validate layer digests, so an unauthenticated remote caller can name a traversal sequence as a digest and have a file written outside the model store. CERT Polska, which coordinated the disclosure and acts as CNA, states that where the server process can write to `/usr/lib/ollama`, "the default in most Ollama Docker images", the written file is loaded and executed on the next restart as **root**. **CVE-2026-103663**, published 2026-10-08, two CVSS 4.0 scores on the record: **9.4** for the writable-library-directory case and 6.9 otherwise. Affected **0.34.2 up to but not including 0.35.0**; fixed **0.35.0**. Reporter Bartłomiej Dmitruk (striga.ai). Ollama's API has no authentication, and the [PoeLLM botnet](2026-10-poellm-canto-incognito-litellm-ollama-cryptomining-botnet.md) already scans for exposed instances. Upgrade, and keep port 11434 off anything but loopback.

## What happened
The pull endpoint downloads a model's layers from a registry and stores each blob under a path derived from its digest. On 0.34.2 through the last 0.34.x release the digest was not validated, so a crafted pull request, or a hostile registry answering a legitimate one, chooses where the blob lands. CERT Polska's advisory and the CNA record describe the rest: a binary written into the directory Ollama loads its runner libraries from runs as the server user on the next restart, and in the Docker image that user is root. No CVSS 3.1 vector is on the record; the two 4.0 vectors differ only in whether the subsequent-system impact is counted. The release page for v0.35.0 shows a 28 September release date with the year not displayed, and carries no security note, which is the silent-fix pattern this corpus keeps recording for runtime servers.

**The rest of the quarter on Ollama's record.** The corpus had no Ollama file before this one, so two earlier entries belong here:

- **CVE-2026-85180** (VulnCheck CNA, 2026-09-03, CVSS 4.0 **8.7**, CWE-918). Ollama did not validate redirect destinations when pulling tensor-layer models, so a registry an attacker controls can redirect blob downloads to arbitrary hosts, including cloud metadata endpoints, and the server fetches them. The database record lists no package and no fixed version; the VulnCheck advisory slug names 0.30.0 through 0.33.2 and the reference is issue #17041. Treat it as unresolved on the record until a fix version is published.
- **CVE-2026-102697** (VulnCheck, 2026-09-29, 8.5, fixed 0.31.2): the experimental agent mode's Bash approval matched a command prefix and ran whatever followed a semicolon. Already tracked in [the agent-framework MCP batch](2026-08-agent-framework-mcp-cve-batch.md); listed here for the product's timeline.

The common thread is the pull path: a model name is a network fetch, a registry is a server the attacker can run, and the process that fetches runs as root in the image most people copy from the README.

## Am I affected?
```bash
ollama --version                      # 0.34.2 through 0.34.x affected; 0.35.0 fixed
curl -s localhost:11434/api/version   # the running server, which may differ from the CLI
docker inspect ollama 2>/dev/null | grep -i '"User"'     # empty or root means the critical case
ss -ltnp | grep 11434                 # 0.0.0.0 or a LAN address means the pull endpoint is reachable
```
You are in the 9.4 case if an affected version ran in a container, or as a user that can write to the Ollama library directory, and the API was reachable from anything you do not trust. A page in a browser on the same machine can also reach a loopback-bound Ollama, so "localhost only" narrows the window but does not close it.

## If you are affected
1. Upgrade to **0.35.0 or later** and restart.
2. Before restarting an affected container that was exposed, list the library directory for files newer than the image build and remove anything unexpected; a planted file executes on restart.
3. Run Ollama as a non-root user with the library directory read-only, and bind the API to 127.0.0.1 behind whatever auth layer your agent gateway provides.
4. If the host was exposed, treat it as compromised: rotate any provider keys, SSH keys and cloud credentials reachable from it. See [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) and [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention
An unauthenticated model server is infrastructure, not a desktop app: put it behind a gateway, egress-filter it so a registry cannot redirect it to metadata, and never run it as root ([agent-sandboxing.md](../prevention/agent-sandboxing.md), [credential-hygiene.md](../prevention/credential-hygiene.md)). Pull models only from registries you control or trust, and pin the server on `latest`, because the fix shipped with no release note.

## Sources
- [CERT Polska — Vulnerability in Ollama software (CVE-2026-103663)](https://cert.pl/en/posts/2026/10/CVE-2026-103663/) (fetched 2026-10-09; published 2026-10-08, vulnerable "From 0.34.2 to 0.35.0", CWE-23, the `/usr/lib/ollama` Docker default and root-on-restart statement, fixed 0.35.0, credit Bartłomiej Dmitruk / striga.ai)
- [CVE Services — CVE-2026-103663](https://cveawg.mitre.org/api/cve/CVE-2026-103663) (CNA CERT-PL, published 2026-10-08; affected `0.34.2` lessThan `0.35.0`; CVSS 4.0 9.4 `AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H` and 6.9)
- [GitHub Advisory Database — GHSA-w8p2-phwr-px3r (CVE-2026-103663)](https://github.com/advisories/GHSA-w8p2-phwr-px3r) (unreviewed, published 2026-10-08, no package or version fields; description as above)
- [GitHub Advisory Database — GHSA-57p7-34ff-7w3w (CVE-2026-85180)](https://github.com/advisories/GHSA-57p7-34ff-7w3w) (VulnCheck, 2026-09-03, CVSS 4.0 8.7, CWE-918, no fixed version listed, references issue #17041 and `x/transfer/download.go` at v0.33.2)
- [GitHub Advisory Database — GHSA-44m8-pr79-3734 (CVE-2026-102697)](https://github.com/advisories/GHSA-44m8-pr79-3734) and [CVE Services — CVE-2026-102697](https://cveawg.mitre.org/api/cve/CVE-2026-102697) (VulnCheck, 2026-09-29, 8.5, 0.14.0 to <0.31.2, fixed 0.31.2)
- [ollama/ollama — Release v0.35.0](https://github.com/ollama/ollama/releases/tag/v0.35.0) (fetched 2026-10-09; shows "28 Sep" with no year rendered and no security note)
- [GitHub Advisory Database — `ollama` listing](https://github.com/advisories?query=ollama+sort%3Apublished-desc) (where the 2026-10-08 row surfaced)
