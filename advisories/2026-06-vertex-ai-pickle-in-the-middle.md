---
id: 2026-06-vertex-ai-pickle-in-the-middle
title: "Pickle in the Middle — Google Cloud Vertex AI SDK bucket-squatting enables cross-tenant model hijack and RCE (patched), plus an unrelated stored-XSS CVE in the same SDK"
date_disclosed: 2026-06-15
last_updated: 2026-08-16
severity: critical
status: patched
ecosystems: [pypi, google-cloud, vertex-ai]
tools_affected: [google-cloud-aiplatform]
tags: [rce, bucket-squatting, pickle-deserialization, cross-tenant, google-cloud, vertex-ai, ml-supply-chain, xss]
---

## TL;DR
Palo Alto Networks Unit 42 disclosed **"Pickle in the Middle"**: the Python `google-cloud-aiplatform` SDK (Google Cloud Vertex AI) picked a **predictable, unowned-by-default staging bucket name** for model uploads (`{project}-vertex-staging-{region}`), so an attacker could pre-create that bucket in their own GCP project, wait for a victim to upload a model without specifying `staging_bucket` explicitly, silently swap in a **malicious pickled model**, and get arbitrary code execution inside Google's own model-serving infrastructure the moment Vertex AI deserializes it — no access to the victim's project and no social engineering required. Fixed across two releases: **v1.144.0** (2026-03-31, randomized bucket naming) and **v1.148.0** (2026-04-15, added bucket-ownership verification). **Update (2026-08-08):** a second, unrelated bug in the same SDK — **CVE-2026-2472**, an unauthenticated stored XSS in the evaluation-results visualizer — was folded in below; it affects a different version range and requires a separate upgrade.

## What happened
Unit 42 reported the flaw to Google's Vulnerability Reward Program on **2026-03-05**; Google assigned it top priority within days.

### The mechanism
1. **Predictable bucket naming.** When a caller doesn't explicitly set `staging_bucket`, the SDK derives a Cloud Storage bucket name deterministically: `{project}-vertex-staging-{region}`. An attacker who knows (or guesses) a target's GCP project ID and region can compute this name in advance.
2. **No ownership check.** The SDK calls `staging_bucket.exists()` before uploading — but a bucket name that exists in *any* GCP project satisfies that check, not just one owned by the caller. An attacker pre-creates a bucket with the predicted name in their **own** project; the victim's SDK then silently uploads the victim's model artifacts into the attacker's bucket.
3. **The race and the swap.** Unit 42 measured roughly 2.5 seconds between a victim's model upload completing and Vertex AI reading the file to deploy it. In their proof of concept, a Cloud Function triggered on the upload event replaced the legitimate model with a malicious one in **1.4 seconds** — comfortably inside that window.
4. **Pickle deserialization → RCE.** Vertex AI models are commonly serialized with `pickle`/`joblib`. Pickle's `__reduce__` mechanism lets a crafted payload execute arbitrary code the moment the file is deserialized — so the swapped-in "model" runs attacker code the instant Vertex AI's serving infrastructure loads it, inside Google's own execution environment, with **no interaction from the victim required beyond the original upload**.

This chains a classic bucket-squatting/name-guessing weakness (the same class of bug as any cloud service that derives resource names predictably from a project ID) with the well-known pickle-deserialization RCE primitive, applied to an ML model-serving pipeline specifically — a cross-tenant compromise vector unique to the shared-infrastructure nature of a managed AI platform.

### Affected versions and fix
- **Affected:** `google-cloud-aiplatform` SDK versions **1.139.0 and 1.140.0** were the versions Unit 42 tested against and confirmed vulnerable (earlier versions using the same bucket-naming scheme are likely affected too, though not explicitly enumerated in the primary source).
- **Fix, in two stages:**
  - **v1.144.0** (2026-03-31) — added a random UUID4 suffix to auto-generated staging bucket names, eliminating predictability.
  - **v1.148.0** (2026-04-15) — added explicit bucket-ownership verification in `Model.upload()`, closing the bucket-squatting primitive even if a name were somehow guessed.

No CVE identifier or CVSS score was published alongside the primary disclosure as of this writing. **Update (2026-08-16): a CVE has since been assigned — CVE-2026-2473** (GHSA-wh2j-26j7-9728), covering Vertex AI Experiments specifically, affecting `google-cloud-aiplatform` **1.21.0 up to (but not including) 1.133.0**, fixed in **1.133.0**. Confirmed directly against the GitHub Advisory Database record and cross-checked with Tenable's and SentinelOne's independent vulnerability-database entries — same predictable-bucket-naming root cause as the primary finding above, just formally tracked under this ID for the Experiments code path.

## Am I affected?

```bash
pip show google-cloud-aiplatform 2>/dev/null | grep -E '^(Name|Version):'
```

You're exposed if you're running `google-cloud-aiplatform` **< 1.148.0** and any of your team's code calls `Model.upload()` (or equivalent SDK model-upload paths) **without** explicitly setting the `staging_bucket` parameter to a Cloud Storage location you control.

## If you are affected
1. **Upgrade to `google-cloud-aiplatform` ≥ 1.148.0.**
2. **Always pass an explicit `staging_bucket`** pointing at a bucket you own, rather than relying on the SDK's auto-generated default — this is Google's own stated best practice going forward, independent of the patch.
3. If you uploaded models on an affected SDK version before April 2026, audit those model artifacts for signs of tampering (unexpected file sizes, unfamiliar pickle opcodes, deploy logs showing unexpected serving-container behavior) and consider re-uploading from a clean, patched environment.
4. → [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — if you suspect exploitation, treat the Vertex AI serving environment's own service-account credentials as potentially exposed, since attacker code would have run with that environment's privileges.

## Update — 2026-08-08: CVE-2026-2472, unrelated stored XSS in the same SDK
A separate, unrelated bug in `google-cloud-aiplatform` — **CVE-2026-2472** (GCP advisory GCP-2026-011) — is an **unauthenticated stored cross-site scripting** flaw in the SDK's `_genai/_evals_visualization.py` module, which renders model-evaluation results and dataset JSON inside Jupyter and Google Colab notebooks. The renderer embeds evaluation-result JSON directly into an HTML `<script>` block without escaping `</script>` sequences, so a crafted evaluation result or dataset field (e.g. a prompt string containing `</script><script>alert('XSS')</script>`) breaks out of the script context and executes arbitrary JavaScript in the notebook's browser session the moment results are displayed — no authentication needed beyond whatever produced the evaluation data in the first place. **Affected: 1.98.0 up to (but not including) 1.131.0. Fixed in 1.131.0.** A public proof-of-concept is available. This is a distinct root cause (XSS via unescaped JSON-in-HTML) from the pickle-deserialization RCE above, and a distinct affected-version range — check both independently.

```bash
pip show google-cloud-aiplatform 2>/dev/null | grep -E '^Version:'
```
You're exposed to CVE-2026-2472 if your version is `>= 1.98.0` and `< 1.131.0` and you view model-evaluation results in a Jupyter/Colab notebook using this SDK's visualization helpers, especially against evaluation data or datasets you didn't author yourself. Upgrade to **≥ 1.131.0**.

## Prevention
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
- Never let a cloud SDK derive a resource name it will subsequently trust from data an attacker could also predict (project ID + region, in this case) without also verifying ownership of that resource.
- Avoid `pickle`/`joblib` for any model-serialization path that crosses a trust boundary (upload, download, or transfer between environments) — prefer formats that don't support arbitrary code execution on load (e.g., ONNX, SafeTensors) where the serving framework supports them.
- Treat any managed AI platform's shared-infrastructure staging/upload path as a cross-tenant attack surface, not just a private pipe to your own project — the same caution this repo already applies to shared-execution-environment platforms like Dialogflow CX ([Rogue Agent](2026-07-rogue-agent-dialogflow-cx-shared-execution.md)).

## Sources
- [Unit 42 (Palo Alto Networks) — Pickle in the Middle: Hijacking Vertex AI Model Uploads for Cross-Tenant RCE](https://unit42.paloaltonetworks.com/hijacking-vertex-ai-model/) — primary technical disclosure, PoC timing data, fix commits.
- [The Hacker News — Google Vertex AI SDK Flaw Let Attackers Hijack Model Uploads via Bucket Squatting](https://thehackernews.com/2026/06/google-vertex-ai-sdk-flaw-let-attackers.html) — independent corroboration, disclosure timeline.
- [GitLab Advisory Database — CVE-2026-2472: Google Cloud Vertex AI SDK affected by Stored Cross-Site Scripting (XSS)](https://advisories.gitlab.com/pkg/pypi/google-cloud-aiplatform/CVE-2026-2472/) — canonical affected/patched version range for the XSS finding.
- [SentinelOne Vulnerability Database — CVE-2026-2472](https://www.sentinelone.com/vulnerability-database/cve-2026-2472/) — independent corroboration of the finding and GCP-2026-011 advisory reference.
- [GitHub Advisory Database — GHSA-wh2j-26j7-9728 (CVE-2026-2473)](https://github.com/advisories/GHSA-wh2j-26j7-9728) — added 2026-08-16: canonical CVE↔GHSA pairing for the Vertex AI Experiments bucket-squatting finding, confirmed affected/patched version range.
- [Tenable — CVE-2026-2473](https://www.tenable.com/cve/CVE-2026-2473) — added 2026-08-16: independent corroboration.
