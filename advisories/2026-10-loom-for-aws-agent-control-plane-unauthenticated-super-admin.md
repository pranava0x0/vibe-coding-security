---
id: 2026-10-loom-for-aws-agent-control-plane-unauthenticated-super-admin
title: "Loom for AWS (awslabs/loom, the AWS Labs enterprise agent platform on Strands + Bedrock AgentCore): with no identity provider configured, every request to the control-plane API — no Authorization header needed — was treated as super-admin (CVE-2026-103956, CVSS 10.0): register tool servers, read stored integration credentials, rewrite the IAM policies on managed agent roles; plus two SSRFs that hand an authenticated user another user's OAuth2 access token (CVE-2026-103957) or the container role's credentials (CVE-2026-103958). Fixed 1.6.1 (2026-08-04) and 1.7.0; AWS bulletin 2026-124, published 2026-10-02"
date_disclosed: 2026-10-02
last_updated: 2026-10-04
severity: critical
status: patched
ecosystems: [aws, ai-agents, python, fastapi, mcp]
tools_affected: ["Loom for AWS < 1.6.1 (CVE-2026-103956)", "Loom for AWS < 1.7.0 (CVE-2026-103957, CVE-2026-103958)", "deployments without an IdP configured, or where IdP config became unreachable", "MCP tool servers and A2A remote agents registered in Loom"]
tags: [cve, aws, aws-bulletin, agent-platform, control-plane, missing-authentication, ssrf, oauth2, token-theft, iam, strands, agentcore, fastapi, mcp, a2a, cwe-306, cwe-918]
---

## TL;DR

**Loom for AWS** is the AWS Labs open-source "enterprise-grade platform for building, deploying and operating AI agents" on Strands Agents and Amazon Bedrock AgentCore Runtime, announced on the AWS Open Source Blog on 2026-07-09 and pitched on its security model (RBAC/ABAC, OAuth2 token exchange, human-in-the-loop MCP elicitations). On **2026-10-02** AWS published bulletin **2026-124-AWS** with three CVEs, all credited to Kenneth Cox via coordinated disclosure:

- **CVE-2026-103956 — Critical, CVSS 10.0 (3.1 and 4.0), CWE-306/CWE-1188.** Before **1.6.1**, "when no identity provider was configured, the backend's authentication dependency granted every incoming request — including those without an Authorization header — super-admin identity." Per the CVE record that meant "registering tool servers, reading stored integration credentials, and rewriting the IAM role policies attached to managed agent roles, via any request to the application API." The vendor advisory says it hit "freshly deployed instances before IdP setup completion or when IdP configuration became unreachable." Fixed in **1.6.1, released 2026-08-04** — two months before the bulletin.
- **CVE-2026-103957 — CVSS 4.0 8.2 / 3.1 6.2, CWE-918/CWE-201.** Before **1.7.0**, an authenticated user registering a tool server or remote agent for delegated auth could supply a crafted OAuth2 discovery-document address and "obtain the access token of another user of the deployment" or make the backend hit arbitrary internal addresses.
- **CVE-2026-103958 — CVSS 4.0 8.3 / 3.1 7.6, CWE-918.** Before **1.7.0**, the connection address given when "registering, updating or testing a tool server or remote agent" was fetched server-side with no destination check: "obtain the credentials of the application's own container role and read responses from arbitrary internal network locations."

Upgrade to **1.7.0**; AWS's remediation list is longer than "upgrade" — rotate the OAuth2 client secrets for MCP/A2A integrations, revoke and re-issue access tokens from the affected period, and if container credentials were exposed, rotate the IAM role session credentials and audit CloudTrail.

## What happened

**The product.** Loom's control plane is a FastAPI API that manages agent deployments, memory, tool servers (MCP) and remote agents (A2A), integrates with an IdP (Cognito or external) for RBAC/ABAC, stores integration credentials in Secrets Manager, and provisions the IAM roles agents run under on AgentCore. It is the kind of thing a platform team stands up once so everyone else can ship agents without touching IAM — which is exactly why "the API is the admin" is a 10.0.

**The auth bypass (CVE-2026-103956).** The vendor advisory is specific: `get_current_user` in `backend/app/dependencies/auth.py` "returned a fixed admin identity unconditionally for any request" when no IdP was configured. The two windows are (a) a fresh deployment before the operator finishes IdP setup — the period in which the API is typically reachable from a bastion or, in a demo, from the internet — and (b) any moment the IdP configuration becomes unreachable, which turns an outage into an auth-off state. Workarounds in the advisory: configure Cognito or an external IdP **before** exposing the backend beyond loopback, make sure `LOOM_ALLOW_UNAUTHENTICATED_LOCAL_DEV` is unset in production, and restrict security-group access during IdP setup. Fix version 1.6.1 shipped 2026-08-04; the bulletin, GHSA pages and CVEs landed 2026-10-02.

**The two SSRFs (CVE-2026-103957 / -103958).** Both sit in the integration-registration path: Loom fetches the OAuth2 discovery document and the connection endpoint of a tool server or remote agent that a user registers. Supplying an internal address — the AWS CVE text names the container credential endpoint as the target of the second — returns responses to the caller. The first is worse than a generic SSRF because it diverts the OAuth2 flow: the discovery address controls where the backend sends the deployment's client secret and where it exchanges codes, so one user obtains "the access token of another user of the deployment." PR:H in both vectors — the attacker must be allowed to register integrations — but that is a standard builder permission in a platform whose purpose is letting teams register their own MCP servers. Fixed in 1.7.0.

**Why it belongs here.** Three of this corpus's standing patterns in one product: the [auth-off-by-default control plane](2026-08-agent-framework-mcp-cve-batch.md) (Obot's quickstart, Casdoor, Bifrost's unauthenticated client registration); the [MCP/OAuth discovery-document SSRF](2026-09-mcp-remote-oauth-discovery-ssrf-cve-batch.md) that the official SDKs and `mcp-remote` have all had; and the "agent platform holds every integration credential" blast radius of n8n and LiteLLM. The twist is the IAM dimension: Loom provisions the roles its agents assume, so super-admin on the control plane means rewriting what every managed agent is allowed to do in the AWS account.

## Am I affected?

```bash
# Loom is deployed from the awslabs/loom repo (CDK/containers). Find the version:
git -C /path/to/loom describe --tags                    # < v1.6.1 → CVE-2026-103956; < v1.7.0 → the two SSRFs
grep -rn "LOOM_ALLOW_UNAUTHENTICATED_LOCAL_DEV" /path/to/loom/.env* 2>/dev/null   # must be unset in prod

# Was the backend ever reachable without an IdP configured? Check the IdP settings history and the
# security groups / ALB listeners for the backend during initial setup.
# CloudTrail: look for iam:PutRolePolicy / AttachRolePolicy on managed agent roles from the Loom backend role
# at times no operator was changing agents.
```

## If you are affected

1. **Upgrade to Loom 1.7.0** (1.6.1 is the minimum for the auth bypass; the SSRFs need 1.7.0).
2. **Rotate OAuth2 client secrets** for every MCP and A2A integration registered in Loom; **revoke and re-issue** access tokens issued during the exposure window.
3. If the backend's container role could have been reached (CVE-2026-103958): **rotate IAM role session credentials**, and **audit CloudTrail** for calls made with the backend role — especially IAM policy changes on agent roles and Secrets Manager reads. [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. Review every tool server and remote agent registered in the deployment for addresses you do not recognise (internal IPs, metadata hosts, attacker domains).
5. If the API was internet-reachable before IdP setup, treat the deployment as compromised: redeploy from clean config, re-register integrations.

## Prevention

- An agent control plane must **fail closed when the IdP is absent or unreachable**; "no IdP configured" is a deployment-time state that should refuse requests, not a mode that grants admin. Verify this for any platform you adopt before the first `cdk deploy`.
- Any URL a user supplies for an integration — discovery document, tool-server endpoint, webhook — is an SSRF primitive; resolve, pin and block internal ranges, and never send client secrets to a discovery-derived endpoint without issuer pinning. See the [MCP SDK issuer-validation advisory](2026-09-mcp-python-sdk-oauth-issuer-validation-credential-redirect.md) for the client-side version of the same bug.
- Give the control plane's own role **no IAM-write permission** it does not need at runtime; provisioning agent roles can be a separate, audited path. [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/mcp-hygiene.md](../prevention/mcp-hygiene.md).

## Sources

- [AWS Security Bulletin 2026-124-AWS — CVE-2026-103956, CVE-2026-103957, and CVE-2026-103958: Issues in Loom for AWS](https://aws.amazon.com/security/security-bulletins/2026-124-aws/) — published 2026-10-02: the three CVEs with CWEs, affected/fixed versions (1.6.1 "released August 4, 2026"; 1.7.0), the four-step remediation (upgrade, rotate OAuth2 client secrets, revoke/re-issue tokens, rotate IAM role session credentials and audit CloudTrail), credit Kenneth Cox. Fetched 2026-10-04. [AWS Security Bulletins index](https://aws.amazon.com/security/security-bulletins/) — 2026-124 among seven bulletins dated 09-29 → 10-02 (2026-121 security-agent-mcp-server and 2026-125 SageMaker Distribution are the AI-adjacent siblings). Fetched 2026-10-04.
- CVE records, CNA AMZN, published 2026-10-02: [CVE-2026-103956](https://cveawg.mitre.org/api/cve/CVE-2026-103956) (affected < 1.6.1; references the v1.6.1 tag and GHSA-vgmj-998f-r8mp), [CVE-2026-103957](https://cveawg.mitre.org/api/cve/CVE-2026-103957) (< 1.7.0, CVSS 4.0 8.2 / 3.1 6.2, GHSA-jcxf-gpf4-58hm), [CVE-2026-103958](https://cveawg.mitre.org/api/cve/CVE-2026-103958) (< 1.7.0, CVSS 4.0 8.3 / 3.1 7.6, GHSA-w6g6-h8pv-6mc7) — descriptions quoted above. [NVD API — CVE-2026-103956](https://services.nvd.nist.gov/rest/json/cves/2.0?cveId=CVE-2026-103956) — CVSS 4.0 10.0 and 3.1 10.0 (`AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H`). Queried 2026-10-04.
- [awslabs/loom — GHSA-vgmj-998f-r8mp: Missing authentication for critical function in Loom for AWS](https://github.com/awslabs/loom/security/advisories/GHSA-vgmj-998f-r8mp) — vendor advisory, published 2026-10-02: the `get_current_user` / `backend/app/dependencies/auth.py` detail, the "freshly deployed … or when IdP configuration became unreachable" windows, the `LOOM_ALLOW_UNAUTHENTICATED_LOCAL_DEV` and security-group workarounds. [awslabs/loom advisory tab](https://github.com/awslabs/loom/security/advisories?state=published) — three entries dated 2026-10-02 (Critical / High / Moderate), repository at 188 stars. Fetched 2026-10-04.
- [AWS Open Source Blog — Building secure AI agents at scale: Introducing Loom for AWS](https://aws.amazon.com/blogs/opensource/building-secure-ai-agents-at-scale-introducing-loom-for-aws/) — 2026-07-09: the product description, FastAPI control plane, Strands/AgentCore, IdP + RBAC/ABAC, Secrets Manager, OAuth2 token exchange and MCP-elicitation approval model quoted above. Fetched 2026-10-04.
- Related in this corpus: [AWS security-agent-mcp-server bucket squat + diff-scan argument injection](2026-09-aws-security-agent-mcp-s3-bucket-squat.md), [Kiro IDE/CLI AWS bulletin batch](2026-09-kiro-ide-cli-aws-bulletin-cve-batch.md), [Bedrock AgentCore CVE cluster](2026-07-aws-bedrock-agentcore-cve-cluster.md).
