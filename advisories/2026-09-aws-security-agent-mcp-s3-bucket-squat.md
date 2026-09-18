---
id: 2026-09-aws-security-agent-mcp-s3-bucket-squat
title: "AWS Security Agent MCP server and the aws-agents-for-devsecops plugin — the scan-input S3 bucket name is derived from your account id and was never ownership-checked, so a pre-registered bucket receives your private source archive, credentials and infrastructure state (CVE-2026-87912 / CVE-2026-87913); upgrading does not free a bucket someone already took"
date_disclosed: 2026-09-10
last_updated: 2026-09-17
severity: medium
status: patched
ecosystems: [pypi, mcp, aws, ai-agents]
tools_affected: ["awslabs.security-agent-mcp-server", "aws-agents-for-devsecops (AWS Security Agent plugin)", "agent-toolkit-for-aws", "any coding agent with the AWS Security Agent MCP server configured"]
tags: [cve, mcp, aws, bucket-squatting, predictable-resource-name, missing-ownership-verification, source-code-exfiltration, credential-exfiltration, cna-vendor]
---

## TL;DR
AWS's **Security Agent** — an AI code-scanning service that agents reach through **`awslabs.security-agent-mcp-server`** (PyPI) or the **AWS Security Agent plugin in `aws-agents-for-devsecops`** — uploads a **private archive of the scanned workspace** to an S3 bucket named **`security-agent-scans-<account-id>-<region>`**. Neither client verified that the bucket belonged to the caller's account. Because account ids are widely public and the naming scheme is documented, a third party could **pre-create that bucket in their own account**, and the agent would upload the victim's source tree — "including credentials and infrastructure state contained in that archive" — into it. **CVE-2026-87913** (MCP server **0.1.0–0.1.5**, fixed **0.2.0**) and **CVE-2026-87912** (`aws-agents-for-devsecops` ≤ 1.0.0, fixed by commit `1c0dfd4f…` in `agent-toolkit-for-aws`), AWS Security Bulletin **2026-105-AWS**, published **2026-09-10**; NVD (CNA AWS) CVSS 3.1 **5.9** / 4.0 5.1, CWE-283 + CWE-341. Reported by Nadav Claude Cohen (glow.io). AWS's guidance has a sentence every reader should act on: **upgrading does not release a bucket name a third party has already registered** — verify the bucket in your account is yours, or pre-create it.

## What happened

**The mechanism.** The Security Agent workflow is: the MCP server (or plugin) packages the workspace into an archive, puts it in a per-account scan-input bucket, and calls the service to scan it. The bucket name is deterministic — `security-agent-scans-<account-id>-<region>` — and the client created it if missing and used it if present. S3 bucket names are global; if the name already existed in *another* account, the client's "use it if present" path uploaded to that bucket. AWS's bulletin: the flaws "might allow remote attackers to obtain the private source archive of a scanned workspace, including credentials and infrastructure state contained in that archive, via pre-registered storage buckets with predictable names derived from account identifiers." NVD phrases the MCP-server CVE the same way: "via a pre-registered storage bucket derived from a publicly known account identifier." The attacker's precondition is knowing a target's 12-digit account id (exposed in ARNs, error messages, public AMIs, IAM policies pasted into forums) and the region — a listable, enumerable space.

**Why this is the "Pickle in the Middle" pattern, for source code.** This repo's [Vertex AI bucket-squatting advisory](2026-06-vertex-ai-pickle-in-the-middle.md) documented the same primitive in Google's SDK: a predictable, account-derived bucket name that the SDK trusts if it exists. Here the payload flows the other way — not a malicious object the SDK downloads, but the victim's own repository the agent uploads. What a "scanned workspace" contains is exactly what a security scanner needs: the full source tree, and in a vibe-coded project that routinely means `.env` files, Terraform state, Kubernetes manifests with embedded secrets, and provider keys committed "temporarily." The tool built to find leaked credentials became the channel that leaked them.

**Affected and fixed (AWS bulletin, 2026-09-10).**
- **CVE-2026-87913** — `awslabs.security-agent-mcp-server` **≥ 0.1.0, ≤ 0.1.5**; fixed **0.2.0** (PyPI).
- **CVE-2026-87912** — AWS Security Agent plugin in `aws-agents-for-devsecops` **≤ 1.0.0**; fixed in `agent-toolkit-for-aws` at commit `1c0dfd4f677237ee9769769209969ca80b112140` (aggregators cite 1.1.0 as the carrying release; the bulletin names the commit).
- **Mitigation beyond the upgrade (AWS):** "verify the scan-input bucket named `security-agent-scans-<account-id>-<region>` belongs to their own account, or pre-create it to prevent third-party registration." The fixed clients add ownership verification (the `ExpectedBucketOwner` check), which makes the upload fail closed against a foreign bucket — but if an attacker already holds the name, your scans will fail until you pick a region or configuration whose bucket you own, and every archive uploaded *before* the fix may already be in their hands.

**Severity note.** NVD's 5.9 reflects `AC:H` and `UI:R` (the attacker must pre-register and the victim must run a scan). The impact column is `C:H`: a complete private source archive with whatever secrets it holds. For a solo developer whose repo holds the production `.env`, that is the whole application. This advisory keeps the vendor/NVD `medium` in the frontmatter per this repo's practice of not out-scoring the CNA, and flags the impact here.

**Second source.** The vendor bulletin is the primary and AWS is the CNA; NVD mirrors it, and the GitHub Advisory Database carries a CVE-sourced copy (NVD's references cite GHSA-3jxw-vj8m-8x77, which returned 404 at fetch time — the database's own search lists the CVE under the `security-agent-mcp-server` query). No independent researcher write-up was located as of 2026-09-17; the reporter's credit is in the bulletin. Status `patched` on the vendor's word, with the bucket-ownership caveat above.

## Am I affected?

```bash
# Installed client versions
pip show awslabs.security-agent-mcp-server 2>/dev/null | grep Version
grep -rn 'security-agent' ~/.kiro/settings/mcp.json ~/.claude.json ~/.cursor/mcp.json .mcp.json 2>/dev/null
# Does the scan-input bucket in each region you used belong to YOUR account?
ACCT=$(aws sts get-caller-identity --query Account --output text)
for r in us-east-1 us-west-2 eu-west-1; do
  aws s3api get-bucket-location --bucket "security-agent-scans-$ACCT-$r" --expected-bucket-owner "$ACCT" >/dev/null 2>&1 \
    && echo "$r: owned by you" || echo "$r: NOT owned by you (or does not exist)"
done
```

You are affected if you ran the MCP server at 0.1.0–0.1.5 or the plugin at ≤ 1.0.0 and scanned a workspace while a third party held the bucket name for your account id and region. You cannot tell from the client side whether that happened; you can tell whether the bucket is yours *now*.

## If you are affected

1. Upgrade to **`awslabs.security-agent-mcp-server` ≥ 0.2.0** / the fixed `agent-toolkit-for-aws`.
2. Run the ownership check above for every region you scanned in. If the bucket exists and is **not** yours, treat every workspace you scanned from that region as disclosed: rotate every credential the source tree or its infrastructure state contained. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [playbooks/auditing-a-vibe-coded-repo.md](../playbooks/auditing-a-vibe-coded-repo.md)
3. **Pre-create** `security-agent-scans-<account-id>-<region>` in your own account for each region you use, so the name cannot be taken.
4. Check CloudTrail for `PutObject` calls from the agent's role to a bucket ARN outside your account. → [playbooks/if-an-mcp-server-was-malicious.md](../playbooks/if-an-mcp-server-was-malicious.md) (the MCP server was not malicious, but the triage steps for "what did the agent's credentials touch" apply)

## Prevention

- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — the archive that leaked contained secrets because they were in the working tree; a scanner cannot exfiltrate what is not there.
- → [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md) — any MCP server that uploads your workspace somewhere is a data-egress path; know the destination and who owns it.
- For any tool that derives a cloud resource name from your account id, pre-create the resource yourself and require `ExpectedBucketOwner`-style checks; predictable names are claimable names.

## Sources

- [AWS Security Bulletin 2026-105-AWS — CVE-2026-87912 and CVE-2026-87913: Missing S3 bucket ownership verification in the AWS Security Agent plugin for aws-agents-for-devsecops and MCP Server](https://aws.amazon.com/security/security-bulletins/2026-105-aws/) — fetched 2026-09-17; primary: published 2026-09-10, affected/fixed versions, the `security-agent-scans-<account-id>-<region>` name, the "upgrading does not release a bucket name" mitigation, credit to Nadav Claude Cohen (glow.io).
- [NVD — CVE-2026-87913](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-87913) — fetched via the NVD API 2026-09-17; CNA AWS, CVSS 3.1 5.9 / 4.0 5.1, CWE-283/341, affected 0.1.0–0.1.5, fixed 0.2.0, references to the bulletin, the GHSA copy and PyPI.
- [GitHub Advisory Database — search "security-agent-mcp-server"](https://github.com/advisories?query=security-agent-mcp-server) — fetched 2026-09-17; the listing that surfaced the CVE alongside the rmcp and atomic-agents-stack entries.
- [Vertex AI "Pickle in the Middle" bucket squatting](2026-06-vertex-ai-pickle-in-the-middle.md) — this repo's prior instance of the predictable-bucket-name class, in Google's SDK.
