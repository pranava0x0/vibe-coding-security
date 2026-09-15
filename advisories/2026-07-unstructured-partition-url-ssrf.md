---
id: 2026-07-unstructured-partition-url-ssrf
title: "unstructured (the ingestion layer under LangChain's UnstructuredURLLoader, LlamaIndex's UnstructuredReader and Chainlit) — full-read SSRF via partition(url=) (CVE-2026-71428, CVSS 9.3), fixed 0.24.0"
date_disclosed: 2026-07-10
last_updated: 2026-09-15
severity: critical
status: patched
ecosystems: [pypi, python, rag, ai-agent-frameworks]
tools_affected: [unstructured, "langchain UnstructuredURLLoader", "llama-index UnstructuredReader", chainlit, "any RAG or agent pipeline that passes a user- or model-supplied URL to partition()"]
tags: [cve, ssrf, rag, document-ingestion, cloud-metadata, langchain, llamaindex, agent-tools]
---

## TL;DR
`unstructured` is the library most Python RAG stacks call to turn a URL or file into text chunks. Its `partition(url=…)`, `partition_html(url=…)` and `partition_md(url=…)` fetched the URL with `requests.get()` and **no host validation**, and returned the response body as element text — a **full-read SSRF** from wherever the ingestion service runs: loopback admin APIs, internal HTTP services, and cloud metadata endpoints. **CVE-2026-71428**, CVSS 3.1 **9.3** (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:L/A:N`), affects **≥ 0.4.7, < 0.24.0**, fixed in **0.24.0**. The vendor advisory itself names the downstream reach: "the de-facto URL ingestion layer for LangChain `UnstructuredURLLoader`, LlamaIndex `UnstructuredReader`, Chainlit, and many agent frameworks." If an agent tool or an "add a source by URL" form ends in `partition()`, the URL an attacker (or a prompt-injected model) supplies is fetched from inside your network.

## What happened

Unstructured-IO published GHSA-4mvj-m6j5-pmf7 on **2026-07-10** (reporter: hayato1121); NVD's record followed on 2026-08-20 with the same 9.3 score, CNA GitHub, CWE-918 and CWE-601. Three code paths took a caller-supplied URL straight to the network:

- `unstructured/partition/auto.py` — `file_and_type_from_url()` behind `partition(url=…)`
- `unstructured/partition/html/partition.py` — `partition_html(url=…)`
- `unstructured/partition/md.py` — `partition_md(url=…)`

None of them checked for private, loopback or link-local destinations, and the fetched body became the returned `Element` text, so the attacker reads the response rather than merely triggering a request. The advisory lists the three usual routes around naive filters — direct private-IP targets, an HTTP redirect from a public host, and DNS rebinding — and the usual targets: internal services and the metadata endpoints of GCP, Azure, Oracle, DigitalOcean and EC2 IMDSv1. The fix (PR #4388, release 0.24.0) adds destination validation; the advisory offers no workaround for older versions.

**Why this is an agent-framework issue and not a "library CVE."** The URL usually is not typed by an administrator. In a RAG product it comes from the end user's "import this page" box; in an agent it comes from a tool call the model decided to make after reading something. Both are attacker-reachable inputs, and the same ingestion path is wired in by name in LangChain's `UnstructuredURLLoader` and LlamaIndex's `UnstructuredReader`. This joins the read-SSRF entries already tracked here for [LangChain's SitemapLoader](2026-08-agent-framework-mcp-cve-batch.md) and for the MCP servers whose fetch tools trusted their input — the model's ability to *choose* a URL turns every unvalidated fetch into a network pivot.

No exploitation in the wild is reported by the vendor or NVD as of 2026-09-15.

## Am I affected?

```bash
pip show unstructured 2>/dev/null | grep -i '^version'      # < 0.24.0 is vulnerable
pip index versions unstructured 2>/dev/null | head -1
# Do you pass URLs into partition()?
grep -rn 'partition(\|partition_html(\|partition_md(\|UnstructuredURLLoader\|UnstructuredReader' --include='*.py' . 2>/dev/null | grep -i 'url' | head -20
```

You are affected if any code path — a web form, an API parameter, an agent tool — can put an attacker-influenced URL into `partition*(url=…)` on a version below 0.24.0, and the process runs somewhere with anything worth reaching on its network (a cloud VM with a metadata service, a VPC with internal services, a machine with local admin ports).

## If you are affected

1. Upgrade to **unstructured ≥ 0.24.0**. Pin it; transitive pins from `langchain-community` or `llama-index-readers-file` may not have moved.
2. Independently of the library fix, validate URLs at your own boundary (resolve, reject private/loopback/link-local, re-check after redirects) and run ingestion workers with **IMDSv2-only** or no metadata access and minimal network egress.
3. If the endpoint was internet-facing on a cloud host, review ingestion logs for requests to `169.254.169.254`, `localhost`, RFC 1918 ranges, or unexpected redirect chains; if found, rotate the instance's credentials. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — a tool that fetches URLs on the model's behalf needs an egress policy, not a hostname regex.
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — SSRF is only as bad as what the process can reach; keep long-lived credentials off ingestion workers.

## Sources

- [Unstructured-IO — GHSA-4mvj-m6j5-pmf7: Server-Side Request Forgery in the URL-based partitioning (CVE-2026-71428)](https://github.com/Unstructured-IO/unstructured/security/advisories/GHSA-4mvj-m6j5-pmf7) — fetched 2026-09-15; vendor advisory published 2026-07-10: CVSS 9.3 vector, affected ≥ 0.4.7 < 0.24.0, fixed 0.24.0, the three code paths, attack routes and metadata targets, the named downstream consumers, reporter credit.
- [GitHub Advisory Database — GHSA-4mvj-m6j5-pmf7](https://github.com/advisories/GHSA-4mvj-m6j5-pmf7) — fetched 2026-09-15; reviewed copy with the same ranges, plus links to PR #4388 and the 0.24.0 release.
- [NVD — CVE-2026-71428](https://nvd.nist.gov/vuln/detail/CVE-2026-71428) — fetched via the NVD API 2026-09-15; published 2026-08-20, CNA GitHub, CVSS 3.1 9.3, CWE-601/918, fix commit `445c957`.
