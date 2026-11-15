---
id: 2026-11-kong-ai-gateway-2-2-1-gateway-enterprise-nine-cves-llm-usage-counter-sql-injection-cache-cross-caller
title: "Kong AI Gateway 2.2.1 and Gateway Enterprise fix nine CVEs: SQL injection through a model name (CVE-2026-92544), cached responses served to other callers"
date_disclosed: 2026-11-10
last_updated: 2026-11-15
severity: high
status: patched
ecosystems: [kong, ai-gateway, api-gateway, llm-proxy, self-hosted]
tools_affected: ["Kong AI Gateway 2.2.0 (fixed 2.2.1)", "Kong Gateway Enterprise 3.10.0.0 before 3.10.0.20, 3.13.0.0 before 3.13.0.12, 3.14.0.0 before 3.14.0.17, 3.15.0.0 before 3.15.0.7, 3.16.0.0 before 3.16.0.2", "deployments that route LLM traffic through Kong and use proxy-cache, proxy-cache-advanced, graphql-proxy-cache-advanced, ai-semantic-cache, request-callout or the SAML plugin"]
tags: [cve, kong, ai-gateway, llm-gateway, sql-injection, cache-poisoning, cross-tenant, rbac, saml, vendor-cna, partial-fix]
---

## TL;DR
Kong released fixes on 2026-11-10 for nine CVEs in Kong AI Gateway and Kong Gateway Enterprise. CVE-2026-92544 (Kong CNA, 8.7) lets a client run SQL against the Kong database through a crafted model name, which the LLM usage counters wrote without escaping. Five ids are caching flaws that can serve one caller's response to another. Upgrade AI Gateway 2.2.0 to 2.2.1, and Gateway Enterprise to 3.16.0.2, 3.15.0.7, 3.14.0.17, 3.13.0.12 or 3.10.0.20. One id, CVE-2026-92442, is only partially fixed. Kong's record does not say whether AI Gateway 2.3.0 is affected.

## What happened

Kong is the CNA for all nine records. Each was published on 2026-11-10 and references only Kong's two changelogs. The changelog entries are the vendor advisory. Scores are Kong's CVSS 4.0 scores as read from CVE Services on 2026-11-15.

| CVE | Kong score | Component | What the record says |
|---|---|---|---|
| CVE-2026-92544 | 8.7 | LLM usage counters | SQL injection. A client may execute arbitrary SQL against the Kong database through a crafted model name. Needs low privileges (`PR:L`). |
| CVE-2026-92545 | 8.7 | `proxy-cache`, `proxy-cache-advanced` | The request hostname was left out of the cache key. A response cached for one hostname may be served for another. |
| CVE-2026-105986 | 8.7 | Admin API RBAC | A delegated administrator can elevate privileges through a percent-encoded role name or a self-assigned role. |
| CVE-2026-92442 | 8.3 | `graphql-proxy-cache-advanced` | The caller's identity was left out of the cache key. One caller's response may be served to another. |
| CVE-2026-92443 | 8.2 | caching plugins | A response cached for a request carrying `Authorization` or `Proxy-Authorization` may be served to different callers. |
| CVE-2026-123041 | 8.2 | `request-callout` | Callout headers not sent by the client were left out of the cache key. One caller's cached callout response may be served to another. |
| CVE-2026-92439 | 7.8 | SAML plugin | `AudienceRestriction` was not enforced. A valid assertion issued for another Service Provider can be replayed to authenticate to Kong. |
| CVE-2026-92441 | 7.8 | regex Routes | Decoded CR/LF characters from the request path reached `X-Forwarded-Prefix`, allowing header injection and request smuggling to the upstream. |
| CVE-2026-92558 | 6.3 | `proxy-cache`, `proxy-cache-advanced` | Separator characters were not escaped in the cache key. A response cached for one request may be served for a different request on the same Route. |

The count of nine was made in code: the set of Kong-assigned ids in the AI Gateway 2.2.1 changelog section equals the set in each of the Gateway Enterprise 3.16.0.2, 3.15.0.7, 3.14.0.17 and 3.10.0.20 sections. The 3.13.0.12 section carries one more, CVE-2026-96437 (Kong 8.2): the `ai-azure-content-safety` plugin skipped inspection of request bodies larger than the in-memory buffer, so a large prompt bypassed the input check. Its record gives fixed versions 3.13.0.12, 3.14.0.11, 3.15.0.4 and 3.16.0.1 and does not list AI Gateway.

### Why the model-name bug matters here

A gateway in front of model providers records usage per model. The changelog says the fix escapes every value "preventing SQL injection when a client-supplied model name is written to the `license_llm_data` table." The model name is a field any API client sets. The record's `AT:P` means an attack precondition exists, and neither the record nor the changelog says what it is.

### The cache bugs and LLM traffic

Teams cache LLM responses to cut cost. The Gateway Enterprise changelog lists the CVE-2026-92443 fix under `ai-semantic-cache` in the 3.16.0.2 and 3.15.0.7 sections: "Fixed CVE-2026-92443 by not caching authenticated responses". The AI Gateway 2.2.1 section carries the same fix line four times. A cached completion served to a different caller is another user's prompt output.

### Three things the records do not settle

- **CVE-2026-92442 is partially fixed.** The changelog says: "Partially fixed CVE-2026-92442" by including the authenticated consumer's id in the cache key. It adds that responses marked `Cache-Control: private` or `no-store` "can still be cached; this is not addressed in this release."
- **AI Gateway 2.3.0 is not covered either way.** The records list AI Gateway as 2.2.0, fixed in 2.2.1. The changelog dates 2.3.0 on 2026-11-04, six days before the fix, and 2.3.1 on 2026-11-10. The 2.3.1 section lists six upstream nginx patches and none of the nine ids. No Kong document read says 2.3.0 carried the fixes. Run 2.3.1 and ask Kong if you ran 2.3.0.
- **Gateway Enterprise 3.11 and 3.12 are not in the records.** The ranges name the 3.10, 3.13, 3.14, 3.15 and 3.16 lines only. The records do not say the other lines are unaffected.

The AI Gateway 2.2.1 section also bumps the bundled Brotli from 1.1.0 to 1.2.1 for CVE-2026-111497 and applies upstream nginx patches for six nginx CVEs. Those are upstream ids, not Kong's.

## Am I affected?

- You run Kong AI Gateway 2.2.0, or Kong Gateway Enterprise on a line and build inside the ranges above. `kong version` prints the build.
- You route LLM traffic through Kong. The usage counters are the component in CVE-2026-92544.
- You enabled `proxy-cache`, `proxy-cache-advanced`, `graphql-proxy-cache-advanced`, `ai-semantic-cache` or `request-callout` on a Route that more than one caller can reach.
- You use the SAML plugin with an identity provider that shares a signing key across Service Providers.

The records name Kong Gateway Enterprise and Kong AI Gateway. They do not name the open-source Kong Gateway, and this file makes no claim about it.

## If you are affected

1. Upgrade to AI Gateway 2.2.1 or 2.3.1, or to the fixed Gateway Enterprise build on your line.
2. Purge the caches of the plugins above after upgrading. Entries stored under the old keys are the ones at risk. This step is this file's advice.
3. For GraphQL caching, do not rely on `Cache-Control: private` or `no-store` to keep a response out of the cache. Kong says that part is not fixed.
4. If untrusted clients could set the model name before the upgrade, review the Kong database for unexpected changes and rotate the credentials it stores. This step is this file's advice. No source reports exploitation.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention

- Treat every client-set field on an LLM request, including the model name, as untrusted input wherever it is logged, counted or stored.
- Key any shared cache on the caller's identity and the host. Do not cache authenticated LLM responses across callers.
- A gateway holds every provider key. Restrict who can reach its admin API and its database. See [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

Single source: the vendor, which is also the CNA.

- [Kong AI Gateway changelog](https://developer.konghq.com/ai-gateway/changelog/), fetched 2026-11-15: the 2.2.1 section (2026/11/10) with every quoted fix line, the 2.3.0 (2026/11/04) and 2.3.1 (2026/11/10) sections.
- [Kong Gateway changelog](https://developer.konghq.com/gateway/changelog/), fetched 2026-11-15: the 3.16.0.2, 3.15.0.7, 3.14.0.17, 3.13.0.12 and 3.10.0.20 sections, each dated 2026/11/10, and the ids in each.
- CVE Services records, fetched 2026-11-15, for [CVE-2026-92544](https://cveawg.mitre.org/api/cve/CVE-2026-92544), [CVE-2026-92545](https://cveawg.mitre.org/api/cve/CVE-2026-92545), [CVE-2026-105986](https://cveawg.mitre.org/api/cve/CVE-2026-105986), [CVE-2026-92442](https://cveawg.mitre.org/api/cve/CVE-2026-92442), [CVE-2026-92443](https://cveawg.mitre.org/api/cve/CVE-2026-92443), [CVE-2026-123041](https://cveawg.mitre.org/api/cve/CVE-2026-123041), [CVE-2026-92439](https://cveawg.mitre.org/api/cve/CVE-2026-92439), [CVE-2026-92441](https://cveawg.mitre.org/api/cve/CVE-2026-92441), [CVE-2026-92558](https://cveawg.mitre.org/api/cve/CVE-2026-92558) and [CVE-2026-96437](https://cveawg.mitre.org/api/cve/CVE-2026-96437): assigner Kong, published 2026-11-10, descriptions, ranges and scores.
- [GitHub Advisory Database, `llm` listing](https://github.com/advisories?query=llm+sort%3Apublished-desc), fetched 2026-11-15: the unreviewed row GHSA-jvch-w6fx-vccj for CVE-2026-92544, dated 2026-11-10, where the item was first seen.
- Not opened: any Kong security bulletin outside the changelogs, and the Kong Gateway open-source changelog.
