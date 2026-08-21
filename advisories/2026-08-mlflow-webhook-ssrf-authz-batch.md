---
id: 2026-08-mlflow-webhook-ssrf-authz-batch
title: "MLflow — critical unauthenticated SSRF (CVSS 9.3) plus two authorization-bypass CVEs, all fixed in 3.15.0"
date_disclosed: 2026-08-02
last_updated: 2026-08-21
severity: critical
status: active
ecosystems: [pypi, mlflow]
tools_affected: [mlflow]
tags: [cve, ssrf, authorization-bypass, credential-hub, ml-tooling, dns-rebinding]
---

## TL;DR
MLflow — the de facto standard open-source ML experiment-tracking and model-registry server that AI/vibe-coding teams stand up to log runs, artifacts, and model versions — shipped three CVEs in one coordinated batch (2026-08-02, -04, and -17). The headline: **CVE-2026-64849** (CVSS 9.3, critical) lets an unauthenticated attacker abuse the model-registry webhook-test endpoint as a full-read SSRF into your internal network and cloud metadata service (`169.254.169.254`), by redirecting past MLflow's own SSRF guard. Two more CVEs (CVSS 8.6 and unrated-high) let authenticated users read another user's private artifacts and inject fake data into another user's experiment runs by exploiting authorization gaps in newer FastAPI-based endpoints that the older Flask-based auth middleware never learned to protect. All three are fixed in **MLflow 3.15.0** — upgrade immediately if you run a self-hosted tracking server.

## What happened
MLflow's default Tracking Server exposes a model-registry webhooks API. Its `POST /api/2.0/mlflow/webhooks/{id}/test` endpoint is unauthenticated by default and synchronously fetches the webhook URL, returning the upstream response status and body straight back to the caller — a textbook full-read SSRF primitive if the target-URL validation can be bypassed.

**CVE-2026-64849 (GHSA-7gwp-5pfp-969j, CVSS 9.3, critical, published 2026-08-02).** MLflow added an SSRF guard (`_validate_webhook_url`, shipped in PR #20747 / MLflow 3.10.0) that resolves the webhook hostname and rejects anything that resolves to a non-public IP. The guard has two gaps: it doesn't set `allow_redirects=False` on the outbound request, and it never re-validates or pins the IP after the initial DNS resolution. An attacker hosts a public HTTPS endpoint that passes the initial hostname check, then responds with `302 Location: http://169.254.169.254/latest/meta-data/iam/security-credentials/...` (or `http://127.0.0.1:<port>/...`) — MLflow follows the redirect without re-checking it, and because `/test` reflects the full response body back to the (unauthenticated) caller, this is a complete, unauthenticated cloud-metadata and internal-service read primitive against any default-configured MLflow Tracking Server. A DNS-rebinding variant achieves the same bypass without needing a redirect. Fixed in **3.15.0**.

**CVE-2026-69148 (GHSA-gqch-g4w5-7qcw, high, published 2026-08-04).** The `_validate_source_run`/`_validate_source_model` checks in `mlflow/server/handlers.py` verify that a model version's source path stays *within* the referenced run's or logged model's artifact directory — but never check whether the calling user has **READ** permission on that run or model in the first place. An authenticated user can pass another user's `run_id` to `CreateModelVersion`, creating a model version whose artifact URI points into the victim's private artifact directory, then read the victim's files via `GET /model-versions/get-artifact` without ever holding permission on the source run. A broken-object-level-authorization (BOLA) bug in the model registry. Fixed in **3.15.0**.

**CVE-2026-69146 (GHSA-3p64-6gvh-82v5, moderate, published 2026-08-04).** When MLflow runs with the built-in `basic-auth` plugin, its before-request authorization hook checks a fixed map of proto handlers that require per-run permission checks. The `LogInputs` handler (`POST /api/2.0/mlflow/runs/log-inputs`) is missing from that map entirely, so the hook skips authorization on it — any authenticated user can inject arbitrary dataset-lineage records into another user's run with no permission check at all. Fixed in **3.15.0**.

All three advisories were reported by the same researcher (GitHub handle `PattaraS`) and disclosed via MLflow's own GitHub Security Advisories, confirmed independently on the GitLab Advisory Database and Rapid7's vulnerability database with matching CVE IDs, CVSS scores, and affected-version ranges. As of this writing none of the three appear in CISA's Known Exploited Vulnerabilities catalog. The two authorization-bypass CVEs share a root cause worth generalizing: MLflow's server has grown a mix of legacy Flask-routed endpoints and newer FastAPI-routed endpoints (jobs, tracing, some registry actions), and its authorization middleware — built for the Flask routing table — doesn't automatically cover new FastAPI routes added later. This is the same "two systems, one app, inconsistent enforcement" shape this repo has flagged before for FastAPI/Starlette apps generally (see the BadHost advisory) — any team adding new API surface to an MLflow-adjacent or similarly mixed-framework server should check that the authorization layer was updated in step.

## Am I affected?
```bash
# Check your installed MLflow version
python -c "import mlflow; print(mlflow.__version__)"
pip show mlflow 2>/dev/null | grep Version

# You are affected if you run a self-hosted MLflow Tracking Server < 3.15.0
# Especially high risk if:
#  - the server is reachable from outside your trusted network (CVE-2026-64849 needs no auth at all)
#  - you run it with --app-name basic-auth and multiple users/teams share one server
#    (CVE-2026-69148 / CVE-2026-69146 need only an authenticated but low-privileged account)

# Check whether your MLflow server is internet- or LAN-reachable
curl -s -o /dev/null -w "%{http_code}\n" http://<your-mlflow-host>:5000/api/2.0/mlflow/webhooks/1/test
```
If your MLflow server runs on cloud infrastructure (AWS/GCP/Azure), a pre-3.15.0 instance with any network reachability to the webhook-test endpoint should be treated as a live cloud-credential-theft risk, not a theoretical one — the same class of unauthenticated-SSRF-to-IMDS bug has been used for full account/cluster takeover in other tools this repo tracks (e.g. Starlette BadHost-derived apps).

## If you are affected
1. Upgrade to **MLflow ≥ 3.15.0** immediately — all three CVEs are fixed in this single release.
2. If you can't upgrade immediately, put the Tracking Server behind a network boundary that blocks unauthenticated inbound access, and block outbound requests from the MLflow process to link-local/metadata addresses (`169.254.169.254`, `127.0.0.1`, RFC1918 ranges) at the network layer as a stopgap — don't rely on the application-layer guard alone, since that's exactly what these CVEs bypass.
3. If you run `basic-auth` mode, audit model-registry and run history for artifacts or dataset records you don't recognize — CVE-2026-69148/-69146 leave no obvious crash or error, just quiet cross-user data access.
4. Treat any cloud IAM role attached to the host running MLflow as compromised if you can't rule out pre-patch exploitation of CVE-2026-64849, and rotate accordingly.

→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)
→ [playbooks/if-your-webapp-was-compromised.md](../playbooks/if-your-webapp-was-compromised.md)

## Prevention
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- Never expose an ML experiment-tracking or model-registry server directly to the internet; MLflow's own auth options are opt-in, not default-on.
- When mixing web frameworks in one server process (Flask + FastAPI, as MLflow does), treat every new route addition as a checklist item to confirm it's covered by the authorization middleware — don't assume coverage is automatic just because older routes are protected.
- Block outbound requests to `169.254.169.254` and other metadata/loopback addresses from any process that fetches user- or webhook-supplied URLs, as defense in depth against SSRF-guard bypasses like this one.


## Update — 2026-08-19: CISA adds CVE-2026-64849 to the Known Exploited Vulnerabilities catalog

Confirmed directly in [CISA's KEV feed](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) (catalogVersion 2026.08.21): **CVE-2026-64849**, listed as "MLflow Server-Side Request Forgery Vulnerability", **`dateAdded` 2026-08-19**, **`dueDate` 2026-09-02**.

This moves the unauthenticated webhook-test SSRF from "critical but no public exploitation reported" to **confirmed exploited in the wild**, seventeen days after the fix shipped in MLflow 3.15.0. Federal civilian agencies have a 2026-09-02 remediation deadline under BOD 26-04; everyone else should read the KEV listing as evidence that the window for an unhurried upgrade has closed.

**This advisory's `status` is therefore changed from `patched` to `active`** — the vendor fix exists and is complete, but attackers are using this against unpatched instances now. If your MLflow Tracking Server has any network reachability beyond a fully trusted host and is not on **3.15.0+**, treat it as a live incident rather than a scheduled upgrade: the exploit is a single unauthenticated request that reflects cloud-metadata responses straight back to the caller, so assume credential theft rather than merely probing.

## Sources
- [GitHub Security Advisory — GHSA-7gwp-5pfp-969j: Unauthenticated full-read SSRF in MLflow webhook delivery](https://github.com/mlflow/mlflow/security/advisories/GHSA-7gwp-5pfp-969j) — primary source for CVE-2026-64849: mechanism, CVSS 9.3, affected/patched versions.
- [GitHub Security Advisory — GHSA-gqch-g4w5-7qcw: CreateModelVersion source validation does not check READ permission on referenced run_id](https://github.com/mlflow/mlflow/security/advisories/GHSA-gqch-g4w5-7qcw) — primary source for CVE-2026-69148.
- [GitHub Security Advisory — GHSA-3p64-6gvh-82v5: LogInputs endpoint bypasses per-run UPDATE authorization in MLflow basic-auth](https://github.com/mlflow/mlflow/security/advisories/GHSA-3p64-6gvh-82v5) — primary source for CVE-2026-69146.
- [GitLab Advisory Database — CVE-2026-64849](https://advisories.gitlab.com/pypi/mlflow/CVE-2026-64849/) — independent corroboration of CVSS score, mechanism, and patched version.
- [Rapid7 Vulnerability & Exploit Database — CVE-2026-64849](https://www.rapid7.com/db/vulnerabilities/cve-2026-64849/) — independent corroboration.
- [CISA — Known Exploited Vulnerabilities catalog (JSON feed, catalogVersion 2026.08.21)](https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json) — added 2026-08-21, fetched directly: confirms CVE-2026-64849 KEV entry, dateAdded 2026-08-19, dueDate 2026-09-02.
