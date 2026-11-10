---
id: 2026-11-fastapi-code-generator-openapi-spec-fields-unescaped-in-generated-code-three-rce-cves-fixed-0-8-1
title: "fastapi-code-generator before 0.8.1 writes OpenAPI spec fields into generated Python unescaped: three code-execution CVEs, fixed in 0.8.1"
date_disclosed: 2026-11-03
last_updated: 2026-11-10
severity: high
status: patched
ecosystems: [pypi, fastapi, openapi, code-generation, ci-cd]
tools_affected: ["fastapi-code-generator (PyPI) before 0.8.1", "any pipeline, scaffold step or coding agent that generates a FastAPI app from an OpenAPI document it did not write and then imports or serves the result", "FastAPI apps already generated with 0.8.0 or earlier from an untrusted spec (the generated main.py keeps the injected code after the generator is upgraded)"]
tags: [cve, ghsa, fastapi, openapi, code-generation, code-injection, untrusted-spec, ci-cd, agent-scaffolding, database-date-not-disclosure-date]
---

## TL;DR
`fastapi-code-generator`, the PyPI tool that turns an OpenAPI document into a FastAPI app, wrote three spec fields into the generated `main.py` without escaping them in every version before 0.8.1: the route path, a response status-code key and the operation summary. A crafted OpenAPI document therefore becomes Python that runs when the generated app is imported, which is at server start, or when the route is called. The fix is 0.8.1, on PyPI since 2026-07-01. The three CVE records were published on 2026-11-03 and the rows reached the GitHub Advisory Database's reviewed-critical list on 2026-11-09, four months after the fix. Upgrade the generator, and regenerate any app built from a spec you did not write.

## What happened

**The three records.** All three are GitHub CNA records published 2026-11-03, all `< 0.8.1`, all CVSS 4.0 9.3 (`AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N`), supplied by the CNA.

| CVE | Record title | Runs when |
|---|---|---|
| CVE-2026-63471 | "Import-time RCE via route path -> unescaped @app.get('...') decorator" | the generated `main.py` is imported |
| CVE-2026-63469 | "Import-time RCE via response status-code key -> unescaped @app.get(..., responses={...}) dict" | the generated `main.py` is imported |
| CVE-2026-63470 | "Call-time RCE via operation summary -> unescaped route-handler docstring" | the route handler is called |

The vendor advisory for the route-path bug (GHSA-p2mm-64f6-gmpp, opened this run) says the generator emits the OpenAPI path into the route decorator as a single-quoted string literal without escaping, so a quote in the path closes the string, and that it was verified on 0.8.0. Its impact section describes code execution at import or startup "in any application or CI pipeline that generates a FastAPI app from an attacker-controlled or attacker-influenced spec and then imports or serves it." Credits: Gal3m and mrostamipoor. The other two vendor advisory pages were not opened; their titles, ranges and scores above come from the CNA records, which reference the same two fix commits and the 0.8.1 release.

**Dates.** PyPI shows 0.8.0 uploaded 2026-06-26 and 0.8.1 uploaded 2026-07-01 09:39 UTC. The vendor advisory is dated 2026-07-01. The CVE records are dated 2026-11-03, NVD-published the same day, and the database published and reviewed the rows on 2026-11-09. This file is dated by the CVE records and is not a new disclosure: the fix has been installable since July.

**Severity here.** The CNA scores 9.3 with no privileges and no user interaction, which describes a spec arriving over the network into an automated generator. This file rates it `high`: the attacker needs the victim to run the generator on a document the attacker controls or can influence, and then to import the output. Where that is automatic, such as a CI job that regenerates a client or server from a partner's published spec, or an agent told to "scaffold an API from this OpenAPI URL", the CNA's reading applies in full.

**Why it is here.** FastAPI is in this corpus's named backend stack, and spec-to-code generation is a step coding agents take without being asked. The generated file is ordinary Python in the repository, so the injected line survives a later upgrade of the generator and passes review as boilerplate. This is the same trust inversion as [model output executed as code](2026-09-ro1me-open-source-agent-framework-llm-output-execution-cve-wave.md), with an API description as the untrusted input.

## Am I affected?

1. `pip show fastapi-code-generator` or `uv pip list | grep -i fastapi-code-generator`. Anything before 0.8.1 is affected. Check CI images, dev containers and agent sandboxes as well as laptops.
2. `grep -rn "fastapi-code-generator\|fastapi_code_generator\|fastapi-codegen" . --include="*.toml" --include="*.txt" --include="*.yml" --include="*.yaml" --include="*.lock" --include="Makefile"` to find pipelines that run it.
3. For each generated app, ask where the OpenAPI document came from. A spec written in the same repository by the same team is not an attack path. A spec fetched from a URL, received from a partner, taken from an issue or produced by a model from untrusted text is.
4. In an app generated before the upgrade from such a spec, read `main.py`: every `@app.<method>(...)` decorator line, every `responses={...}` dict and every handler docstring should contain only the literal path, status codes and summary text from the spec.

## If you are affected

- Upgrade to 0.8.1: `pip install -U "fastapi-code-generator>=0.8.1"`. Then regenerate the app from the spec and diff the output against what is committed.
- If a generated app from an untrusted spec was imported or served, treat the host or CI runner as having run someone else's code: rotate the secrets it could read and follow [if your web app was compromised](../playbooks/if-your-webapp-was-compromised.md). For a CI runner, [CI/CD hardening](../prevention/ci-cd-hardening.md) lists what a job token can reach.

## Prevention

- **Treat an OpenAPI document as input, not configuration.** Pin specs by commit or hash, review changes to them like code, and do not generate from a live URL in CI.
- **Generate in a sandbox and import somewhere else.** A generation step needs no network and no secrets. [Agent sandboxing](../prevention/agent-sandboxing.md) covers the pattern for agent-run scaffolding.
- **Review generated code before the first import.** "It is generated" is the reason nobody reads it.

## Sources

- [CVE Services: CVE-2026-63471](https://cveawg.mitre.org/api/cve/CVE-2026-63471), [CVE-2026-63469](https://cveawg.mitre.org/api/cve/CVE-2026-63469) and [CVE-2026-63470](https://cveawg.mitre.org/api/cve/CVE-2026-63470), fetched 2026-11-10: GitHub CNA, each published 2026-11-03, titles quoted above, `< 0.8.1`, CVSS 4.0 9.3, each referencing its vendor advisory, two fix commits and the 0.8.1 release.
- [GitHub Advisory Database: GHSA-p2mm-64f6-gmpp](https://github.com/advisories/GHSA-p2mm-64f6-gmpp), fetched 2026-11-10: vendor-published 2026-07-01, NVD-published 2026-11-03, database-published 2026-11-09; the summary and impact paraphrased above; CWE-94 and CWE-116; credits; EPSS 0.312 percent on the read date.
- [GitHub Advisory Database: reviewed critical pip listing](https://github.com/advisories?query=type%3Areviewed+ecosystem%3Apip+severity%3Acritical), fetched 2026-11-10: the three rows dated Nov 9, 2026.
- PyPI JSON API for `fastapi-code-generator`, read 2026-11-10: 0.8.0 uploaded 2026-06-26 16:24 UTC, 0.8.1 uploaded 2026-07-01 09:39 UTC; `pip index versions` lists 0.8.1 as newest.
- Single vendor source for the mechanism, with the CNA records as the id source. The vendor advisory pages for CVE-2026-63469 and CVE-2026-63470 were not opened this run.
