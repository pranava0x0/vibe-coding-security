---
id: 2026-11-mcp-server-cves-november-16-awslabs-timestream-influxdb-token-leak-pricing-file-write-kubeshark-code-review-mcp
title: "MCP server CVEs, 2026-11-16: awslabs Timestream for InfluxDB token leak, AWS Pricing file write, Kubeshark, code-review-mcp-server; all fixed"
date_disclosed: 2026-11-16
last_updated: 2026-11-17
severity: high
status: patched
ecosystems: [mcp, pypi, npm, go, aws, awslabs, kubernetes]
tools_affected: ["awslabs.timestream-for-influxdb-mcp-server (PyPI) 0.0.12 before 0.0.19", "awslabs.aws-pricing-mcp-server (PyPI) before 1.0.31", "awslabs.cost-analysis-mcp-server 1.0.5 and earlier, deprecated, no patch", "kubeshark CLI 53.1.0 before 53.4.0 running kubeshark mcp", "code-review-mcp-server (npm) before 1.5.3"]
tags: [cve, ghsa, mcp, mcp-server, prompt-injection, credential-exposure, path-traversal, arbitrary-file-write, argument-injection, command-injection, aws-security-bulletin, awslabs-mcp, kubernetes, late-cve]
---

## TL;DR
Five CVE records for four MCP servers were published on 2026-11-16, and every fix was already on its registry. `awslabs.timestream-for-influxdb-mcp-server` before 0.0.19 could send its InfluxDB API token to a URL placed in the agent's context ([AWS bulletin 2026-185](https://aws.amazon.com/security/security-bulletins/2026-185-aws/), CVE-2026-126681). Upgrade it and rotate the token. Upgrade `awslabs.aws-pricing-mcp-server` to 1.0.31, Kubeshark to 53.4.0 and `code-review-mcp-server` to 1.5.3. In each case the attacker is content that the agent reads.

## What happened

| Server | CVE | Score | Affected | Fixed | Fix on the registry |
|---|---|---|---|---|---|
| `awslabs.timestream-for-influxdb-mcp-server` (PyPI) | CVE-2026-126681 | AWS CNA: 5.5 (3.1), 6.8 (4.0) | 0.0.12 before 0.0.19 | 0.0.19 | 2026-07-28 |
| `awslabs.aws-pricing-mcp-server` (PyPI) | CVE-2026-126816 | AWS CNA: 5.5 (3.1), 6.8 (4.0) | before 1.0.31 | 1.0.31 | 2026-06-09 |
| Kubeshark `start_kubeshark` tool | CVE-2026-129236 | vendor: High 7.2 | 53.1.0 before 53.4.0 | 53.4.0 | fix commit 2026-08-12 |
| Kubeshark `download_file` tool | CVE-2026-129235 | database: Moderate | 53.1.0 before 53.4.0 | 53.4.0 | fix commit 2026-08-12 |
| `code-review-mcp-server` (npm) | CVE-2026-68934 | database: High (4.0) | before 1.5.3 | 1.5.3 | 2026-07-06 |

**Timestream for InfluxDB MCP Server.** [AWS bulletin 2026-185](https://aws.amazon.com/security/security-bulletins/2026-185-aws/) is dated 2026-11-16. The [CNA record](https://cveawg.mitre.org/api/cve/CVE-2026-126681) says a remote unauthenticated actor could, "via prompt injection", obtain the InfluxDB API token configured on the server. The token is "sent to a crafted endpoint controlled through an InfluxDB URL introduced in the MCP client context". The record tells users to upgrade and "rotate any InfluxDB API tokens configured for the server". The bulletin's interim advice is a token with the fewest permissions and no untrusted content in the client.

**AWS Pricing MCP Server.** [AWS bulletin 2026-184](https://aws.amazon.com/security/security-bulletins/2026-184-aws/) is dated 2026-11-16. The [CNA record](https://cveawg.mitre.org/api/cve/CVE-2026-126816) says "an actor who can influence the MCP agent" can make the cost report tool write content outside the output directory through absolute paths or traversal sequences. The bulletin says the tool is annotated as read-only, so MCP clients may approve it without asking. The deprecated `awslabs.cost-analysis-mcp-server` 1.0.5 and earlier is affected and gets no patch.

**Kubeshark.** The vendor advisory [GHSA-8vf2-hxg5-crqh](https://github.com/kubeshark/kubeshark/security/advisories/GHSA-8vf2-hxg5-crqh) is dated 2026-08-13. The database published both Kubeshark records on 2026-11-16. The `start_kubeshark` tool passed a caller-supplied `pod_regex` to the `kubeshark tap` command without an end-of-options separator. The record says an attacker who can influence the tool arguments can point the deployed images at another registry, which yields node and cluster-admin compromise. The tool is registered only with `kubeshark mcp --allow-destructive`. The `download_file` tool wrote fetched bytes to a caller-supplied local path with no validation, and the record says it is available without that flag.

**code-review-mcp-server.** The database record GHSA-jq3q-62jc-fqq9 says the `getLocalGitDiff`, `codeReview`, `createPR` and `getPRTemplate` tools put the `folderPath` and `baseBranch` parameters into shell command strings. A crafted value runs commands on the host. The record lists no workaround. npm shows 1.5.3 published on 2026-07-06 and 1,391 downloads in the week to 2026-11-16.

## Am I affected?

```bash
pip show awslabs.timestream-for-influxdb-mcp-server awslabs.aws-pricing-mcp-server awslabs.cost-analysis-mcp-server 2>/dev/null | grep -E '^(Name|Version)'
npm ls -g code-review-mcp-server 2>/dev/null; npm ls code-review-mcp-server 2>/dev/null
command -v kubeshark                      # then compare the installed release with 53.4.0
grep -rn -E 'timestream-for-influxdb|aws-pricing-mcp|cost-analysis-mcp|code-review-mcp-server|kubeshark' ~/.cursor/mcp.json ~/.claude.json .mcp.json 2>/dev/null
grep -rn 'allow-destructive' ~/.cursor/mcp.json ~/.claude.json .mcp.json 2>/dev/null
```

- A configuration that starts the server at its latest version on each run picked up the fix on the registry date in the table. A pinned version or a cached environment did not.
- `awslabs.cost-analysis-mcp-server` at any version is affected.

## If you are affected

- Upgrade each server to the fixed version and restart the MCP clients that start it.
- Rotate the InfluxDB API token if the Timestream server ran at 0.0.12 through 0.0.18.
- Replace `awslabs.cost-analysis-mcp-server` with `awslabs.aws-pricing-mcp-server` 1.0.31 or later. Remove `generate_cost_report` from auto-approve lists until then.
- For Kubeshark, check the images of the worker, hub and front workloads against the registry you expect. Check `~/.ssh/authorized_keys`, `~/.kube/config` and shell startup files for changes made while the MCP server ran, as the advisory names those paths.
- For code-review-mcp-server, review agent transcripts for `baseBranch` or `folderPath` values that contain shell characters.
- See [if an MCP server was malicious](../playbooks/if-an-mcp-server-was-malicious.md). The transcript and configuration audit applies to a vulnerable server too.

## Prevention

- Give each MCP server a credential scoped to its task. See [MCP hygiene](../prevention/mcp-hygiene.md).
- Do not auto-approve a tool because its annotation says read-only.
- Do not run an MCP server with cluster or cloud write access in a client that reads untrusted content. See [agent sandboxing](../prevention/agent-sandboxing.md).

## Sources

- [AWS bulletin 2026-185-AWS](https://aws.amazon.com/security/security-bulletins/2026-185-aws/): Timestream for InfluxDB MCP Server, 2026-11-16.
- [AWS bulletin 2026-184-AWS](https://aws.amazon.com/security/security-bulletins/2026-184-aws/): AWS Pricing MCP Server, 2026-11-16.
- [CVE-2026-126681](https://cveawg.mitre.org/api/cve/CVE-2026-126681) and [CVE-2026-126816](https://cveawg.mitre.org/api/cve/CVE-2026-126816): AWS CNA records, ranges, scores and remediation text.
- [GHSA-8vf2-hxg5-crqh](https://github.com/kubeshark/kubeshark/security/advisories/GHSA-8vf2-hxg5-crqh): Kubeshark vendor advisory, 2026-08-13, range, score and workarounds.
- [GitHub Advisory Database, `mcp` listing](https://github.com/advisories?query=mcp+sort%3Apublished-desc): the Kubeshark and code-review-mcp-server rows dated 2026-11-16.
- OSV records GHSA-gj7r-p794-hhq5, GHSA-8vf2-hxg5-crqh and GHSA-jq3q-62jc-fqq9 (`api.osv.dev/v1/vulns/<id>`): descriptions and ranges. The vendor pages for GHSA-gj7r-p794-hhq5 and GHSA-jq3q-62jc-fqq9 were not opened.
- PyPI and npm publish times, read 2026-11-17: 0.0.19 on 2026-07-28, 1.0.31 on 2026-06-09, 1.5.3 on 2026-07-06. The Go module proxy dates the Kubeshark fix commit to 2026-08-12.
