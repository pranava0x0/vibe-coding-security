---
id: 2026-11-litellm-proxy-azure-entra-request-parameters-leak-environment-and-master-key-ghsa-2rwg-2wh4-7c4f
title: "LiteLLM proxy: an authenticated caller can read server environment values, including the master key, through Azure Entra request parameters (GHSA-2rwg-2wh4-7c4f); fixed 1.109.1"
date_disclosed: 2026-11-12
last_updated: 2026-11-14
severity: high
status: patched
ecosystems: [pypi, python, litellm, llm-gateway, azure]
tools_affected: ["litellm (PyPI) before 1.106.9, 1.108.x before 1.108.6, 1.109.0", "LiteLLM proxy deployments with at least one `azure/` or `azure_ai/` model and no `AZURE_API_KEY` or `AZURE_OPENAI_API_KEY` set", "agents and applications that share a LiteLLM proxy across users or teams"]
tags: [litellm, llm-gateway, pypi, secret-exfiltration, master-key, azure, entra-id, authenticated, no-cve, patched]
---

## TL;DR
LiteLLM's proxy did not block six Azure Entra ID credential parameters in request bodies. A user with any key that can call one Azure model could send them and get server-side values back in the error, including provider API keys, the database URL and `LITELLM_MASTER_KEY`. The vendor advisory, published 2026-11-12, scores it 7.7 and lists no CVE. Fixed in 1.106.9, 1.108.6, 1.109.1 and 1.110.0-rc.2. All four are on PyPI.

## What happened

The vendor advisory GHSA-2rwg-2wh4-7c4f (High, CVSS 3.1 7.7, `AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N`) names the parameters: `tenant_id`, `client_id`, `client_secret`, `azure_username`, `azure_password` and `azure_scope`. A value supplied in a chat completion or image generation request to an Azure deployment overrides the deployment's default Azure credential. The resulting authentication error goes back to the caller and can include resolved server-side values. The advisory says this covers environment variables of the proxy process and the contents of files those variables point to, and that the master key gives full administrative control of the proxy.

The advisory limits the affected configurations to deployments with at least one Azure OpenAI or Azure AI model that do not set `AZURE_API_KEY` or `AZURE_OPENAI_API_KEY`.

The page prints "CVE ID: None known" when read on 2026-11-14 and lists no credit. `pip` listed 1.106.9, 1.108.6, 1.109.1 and 1.110.0rc2 on 2026-11-14.

This is a different bug from the unauthenticated file read in [2026-10-litellm-enterprise-unauthenticated-file-read-master-key-leak-ghsa-w4c7-34wj-hqm8.md](2026-10-litellm-enterprise-unauthenticated-file-read-master-key-leak-ghsa-w4c7-34wj-hqm8.md). This one needs a valid key.

## Am I affected?

```bash
pip show litellm | grep -i '^version'
```

- The version is below the fixed release for your line.
- The proxy config has an `azure/` or `azure_ai/` model.
- Neither `AZURE_API_KEY` nor `AZURE_OPENAI_API_KEY` is set in the proxy's environment.
- People or agents you do not fully trust hold proxy keys.

No CVE exists, so a scanner keyed on CVE ids will not flag this.

## If you are affected

1. Upgrade to 1.106.9, 1.108.6 or 1.109.1 for your line.
2. Until then, block the six parameters in request bodies at a reverse proxy in front of LiteLLM. This is the vendor's workaround.
3. If untrusted callers held keys while you ran an affected version, rotate `LITELLM_MASTER_KEY`, the provider keys in the proxy's environment and the database password. This step is this file's advice. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- Keep the proxy's environment small. A key the proxy does not hold cannot leak from it.
- See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

Single source: the vendor.

- [GHSA-2rwg-2wh4-7c4f](https://github.com/BerriAI/litellm/security/advisories/GHSA-2rwg-2wh4-7c4f), fetched 2026-11-14: published 2026-11-12, score and vector, affected and patched versions, the six parameters, affected configurations, the workaround, "None known".
- [BerriAI/litellm security advisories](https://github.com/BerriAI/litellm/security/advisories), fetched 2026-11-14: the row, first on page 1.
- `pip download litellm==99` version list, run 2026-11-14.
- Not covered: the fix commit and the release notes.
