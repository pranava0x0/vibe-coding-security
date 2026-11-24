---
id: 2026-11-litellm-proxy-client-api-base-poisons-shared-deployments-ghsa-m8fp-3f3g-j5p7-fixed-1-103-0
title: "LiteLLM proxy: a request's own api_base or key joined the shared deployment list for every user (GHSA-m8fp-3f3g-j5p7); fixed 1.103.0"
date_disclosed: 2026-11-23
last_updated: 2026-11-24
severity: high
status: patched
ecosystems: [pypi, python, litellm, llm-gateway]
tools_affected: ["litellm (PyPI) 1.63.2 to below 1.103.0", "LiteLLM proxy deployments with `allow_client_side_credentials`, a deployment that allows `api_base`, or `forward_llm_provider_auth_headers`", "litellm (PyPI) 1.40.4 to 1.108.0 as printed, for the two Moderate advisories", "litellm (PyPI) 1.83.0 to below 1.104.0, for the plaintext password advisory", "agents and applications that share a LiteLLM proxy across users or teams"]
tags: [litellm, llm-gateway, pypi, traffic-redirect, prompt-exposure, provider-key, authenticated, no-cve, patched]
---

## TL;DR
[GHSA-m8fp-3f3g-j5p7](https://github.com/BerriAI/litellm/security/advisories/GHSA-m8fp-3f3g-j5p7) says a LiteLLM proxy request that carried its own `api_key`, `api_base` or `base_url` was added to the router's shared deployments for that model until restart. Where client-side `api_base` is allowed, an authenticated user could route part of other users' traffic to their own server and receive prompts and the operator's provider key. Affected 1.63.2 to below 1.103.0. Fixed in 1.103.0, on PyPI since 2026-09-27. The advisory was published 2026-11-23 with no CVE.

## What happened

The vendor rates it High, CVSS 3.1 8.4, `AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L`. The advisory describes three outcomes by configuration:

| Configuration | Outcome the advisory describes |
|---|---|
| Default | A caller's `api_key` could be used for other users' requests to that model. Those requests fail if the key is invalid. |
| `forward_llm_provider_auth_headers` on | One user's provider key, sent in `x-api-key`, could serve other users' requests and be billed for them. |
| `allow_client_side_credentials` on, or `api_base` allowed on a deployment | An authenticated user could redirect part of other users' traffic for that model to a server they control. That exposes prompts and the operator's provider API key, and lets the server return any response. |

The added deployments stayed until the proxy restarted.

The fixed release predates the advisory. PyPI shows 1.103.0 uploaded 2026-09-27 and 1.110.2, the newest, uploaded 2026-11-20.

### Two Moderate advisories the same day

Both are 4.3, need a logged-in low-privilege user, and expose no keys, prompts or responses according to the vendor.

| Advisory | Endpoint | What a low-privilege user could read | Affected as printed | Patched as printed |
|---|---|---|---|---|
| [GHSA-2364-6whj-g7vx](https://github.com/BerriAI/litellm/security/advisories/GHSA-2364-6whj-g7vx) | `GET /global/activity/cache_hits` | proxy-wide request, cache-hit and failure counts, key aliases and models | `>= 1.83.6, <= 1.108.0` | 1.108.0 |
| [GHSA-fjxr-j47c-4x2x](https://github.com/BerriAI/litellm/security/advisories/GHSA-fjxr-j47c-4x2x) | `GET /spend/tags` | every request tag with its request count and spend | `>= 1.40.4, <= 1.108.0` | 1.108.0 |

Each page prints 1.108.0 as both the last affected and the patched version. The affected range and the patched version overlap, so this file does not say whether 1.108.0 is fixed. PyPI shows 1.108.0 uploaded 2026-11-04 and 1.108.1 on 2026-11-05.

## Am I affected?

```bash
pip show litellm | grep -i '^version'
grep -rn 'allow_client_side_credentials\|forward_llm_provider_auth_headers\|configurable_clientside_auth_params' .
```

- Below 1.103.0, and people or agents you do not fully trust hold proxy keys.
- The redirect outcome needs one of the settings in the table. The `grep` covers the three setting names the advisory gives. Run it in the directory that holds the proxy config.
- No CVE exists, so a scanner keyed on CVE ids will not flag this.

## If you are affected

1. Upgrade to 1.103.0 or later. For the two Moderate advisories, run a version above 1.108.0.
2. Restart the proxy. The advisory says added deployments last until restart.
3. If client-side `api_base` was allowed while untrusted users held keys, rotate the provider keys for the affected models. This step is this file's advice. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).
4. If you cannot upgrade, the vendor's workaround for the Moderate advisories is to block the two endpoints at a reverse proxy. That also blocks them for admins.

## Prevention

- Leave client-supplied endpoints and credentials off on a proxy that more than one team uses.
- See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Update 2026-11-24

[GHSA-p377-4hwj-f3fh](https://github.com/BerriAI/litellm/security/advisories/GHSA-p377-4hwj-f3fh), published 2026-11-24, Moderate, CVSS 3.1 4.9, no CVE. A `POST /user/bulk_update` with `all_users: true` and a `password` field stored that password unhashed for every user. Affected 1.83.0 to below 1.104.0. Fixed in 1.104.0, on PyPI since 2026-10-03.

- It applies only where an admin used that call to give every user one password. The advisory says this pattern is not expected in deployments.
- Anyone who can read the database or its backups can read the password and sign in as any affected user.
- Upgrading does not rehash stored passwords. The advisory gives a query on `LiteLLM_UserTable` for rows whose `password` is set and does not start with `scrypt:` or `pbkdf2:`.
- Upgrade to 1.104.0 or later for this advisory, then reset the password of every user the query returns.
- Treat backups that hold those rows as exposed. This step is this file's advice.

## Sources

- [GHSA-p377-4hwj-f3fh](https://github.com/BerriAI/litellm/security/advisories/GHSA-p377-4hwj-f3fh), fetched 2026-11-24 through a summarizing fetch. Paraphrased, not quoted. PyPI simple API for the 1.83.0 and 1.104.0 upload times.

Single source: the vendor.

- [GHSA-m8fp-3f3g-j5p7](https://github.com/BerriAI/litellm/security/advisories/GHSA-m8fp-3f3g-j5p7), [GHSA-2364-6whj-g7vx](https://github.com/BerriAI/litellm/security/advisories/GHSA-2364-6whj-g7vx), [GHSA-fjxr-j47c-4x2x](https://github.com/BerriAI/litellm/security/advisories/GHSA-fjxr-j47c-4x2x), fetched 2026-11-23 through a summarizing fetch: dates, scores, vectors, ranges, patched versions, impact by configuration, workarounds, "No known CVE". Paraphrased, not quoted.
- [BerriAI/litellm security advisories](https://github.com/BerriAI/litellm/security/advisories), fetched 2026-11-23: three rows dated 2026-11-23.
- PyPI JSON for `litellm`, read 2026-11-23: upload dates for 1.63.2, 1.103.0, 1.108.0, 1.108.1 and 1.110.2.
- OSV returned no record for any of the three ids on 2026-11-23.
- Not covered: the fix commits and the release notes.
