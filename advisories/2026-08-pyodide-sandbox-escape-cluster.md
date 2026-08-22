---
id: 2026-08-pyodide-sandbox-escape-cluster
title: "One Pyodide flaw, seven products — n8n, Grist, Cohere Terrarium and Hugging Face smolagents all trusted the same broken sandbox (DEF CON 34 backfill)"
date_disclosed: 2026-08-10
last_updated: 2026-08-22
severity: critical
status: patched
ecosystems: [pypi, npm, ai-agent-frameworks]
tools_affected: [n8n, grist, cohere-terrarium, huggingface-smolagents, langchain-sandbox, stlite, cibuildwheel]
tags: [sandbox-escape, pyodide, ai-agent-frameworks, rce, wasm, python]
---

## TL;DR

Cyera researchers Vladimir Tokarev and Saar Pearl showed at **DEF CON 34** (2026-08-10) that **the same root-cause flaw in Pyodide** (CPython compiled to WebAssembly, used to "safely" run untrusted Python inside Node.js/browser processes) broke the sandbox in **seven independent products at once**: n8n, Grist, Cohere's Terrarium, Hugging Face's smolagents, `langchain-sandbox`, `stlite`, and `cibuildwheel`. Four CVEs were assigned, CVSS 8.3–9.9. This repo tracked the individual n8n and Grist findings in isolation months ago but missed the unifying DEF CON research — this advisory backfills that gap and the products it adds (Cohere Terrarium, smolagents).

## What happened

Pyodide runs a full CPython interpreter compiled to WebAssembly inside a JavaScript host (Node.js, Deno, or a browser tab). A growing list of AI-adjacent products use it as their answer to "how do we let an LLM or an end-user run Python code without giving it real system access": n8n's Code node, Grist's spreadsheet formula sandbox, Cohere's Terrarium code-execution service, Hugging Face's smolagents code-executing agent framework, LangChain's `langchain-sandbox`, Streamlit-in-the-browser's `stlite`, and the wheel-building tool `cibuildwheel`.

Cyera's research found that restrictions layered on top of Pyodide across all seven products **did not account for Python's `ctypes` module and functions exported by Emscripten** (the WASM toolchain Pyodide is built with). `ctypes` gives Python code a path to call arbitrary native functions by address; combined with Emscripten's exported runtime functions, untrusted Python running "inside the sandbox" can reach into the host JavaScript/Node.js process directly — the sandbox boundary was Python-level, not WASM-level, and `ctypes` walks straight around it.

Per-product findings, publish date, CVSS, and fix status:

- **n8n — CVE-2025-68668 ("N8Scape"), CVSS 9.9 critical.** Any authenticated user with permission to create or edit a workflow could use the Python Code node to execute arbitrary commands on the host running n8n, with the n8n process's own privileges — including reaching credentials for every connected integration in that instance. Affected n8n 1.0.0–2.0.0-rc, fixed in **2.0.0** by moving Python execution to an external task-runner process, isolated from the core n8n service. GHSA-62r4-hw23-cc8v.
- **Grist — CVE-2026-24002 ("Cellbreak"), CVSS 9.1 critical.** When `GRIST_SANDBOX_FLAVOR=pyodide` (a supported configuration), a malicious spreadsheet formula could run arbitrary processes on the server hosting Grist. Affected grist-core < 1.7.9, fixed in **1.7.9** by switching the default Pyodide sandbox to run under Deno, adding a permission-based isolation layer on top. Operators can also switch to the gVisor-based sandbox flavor. GHSA-7xvx-8pf2-pv5g.
- **Cohere Terrarium — CVE-2026-5752, CVSS 9.3 critical.** Terrarium is Cohere's open-source, Docker-deployed sandbox for running untrusted or LLM-generated Python. The flaw is a JavaScript prototype-chain traversal in the Pyodide layer that lets sandboxed code execute with root privileges on the host Node.js process — full container-level code execution, no user interaction required (`AV:L/AC:L/PR:N/UI:N`). CERT/CC (VU#414811) notified Cohere 2026-02-19 and published 2026-04-21 after the coordination window lapsed; Cohere shipped **v1.0.1** the next day, 2026-04-22. GHSA-cmpr-pw8g-6q6c. **Correction note:** at least one secondary aggregator (eSecurityPlanet, in its DEF CON 34 recap) cites this finding as "CVE-2026-61522" — that ID does not resolve on NVD or GitHub's own advisory for Terrarium; the advisory GitHub itself publishes (GHSA-cmpr-pw8g-6q6c) states the CVE is **CVE-2026-5752**, which is the ID used throughout this advisory.
- **Hugging Face smolagents — reported as CVE-2026-10613, CVSS 8.3.** smolagents is Hugging Face's framework for agents that "think in code," and its `local_python_executor.py` module is a best-effort restricted-Python executor, not the Pyodide-specific escape itself, but Cyera's DEF CON talk and its secondary coverage (eSecurityPlanet) list smolagents among the seven Pyodide-based products broken by the same `ctypes`/Emscripten class. **Unlike the other three CVEs above, CVE-2026-10613 could not be independently confirmed by this sweep**: NVD shows it as `RESERVED` (no populated record as of this writing) and `github.com/huggingface/smolagents/security/advisories` lists no published advisories at all. Treat the CVE number itself as unconfirmed while the underlying finding (smolagents named in the DEF CON research) is corroborated by multiple secondary sources. This is a distinct, newer issue from the older, already-patched **CVE-2025-5120** (`local_python_executor.py` returning unwrapped builtins like `getattr`, fixed in smolagents 1.17.0) — don't conflate the two.
- **`langchain-sandbox`, `stlite`, `cibuildwheel`** — named by Cyera as also affected by the same underlying `ctypes`/Emscripten sandbox-escape class, but no CVE numbers or fixed-version details surfaced in this sweep's sources; flagged here so readers using these tools know to check for vendor advisories directly rather than assuming they're out of scope.

Vendor responses varied: n8n and Grist made architectural changes (external runner / Deno-based re-sandboxing); Cohere shipped a point release; the status of `langchain-sandbox`, `stlite`, and `cibuildwheel` fixes is not confirmed by this sweep.

## Am I affected?

- **n8n:** check your version — `n8n --version` or the footer of the web UI. Affected: 1.0.0 through pre-2.0.0. Upgrade to **≥ 2.0.0**, or disable the Code node / Python support via environment variable as an interim mitigation.
- **Grist (self-hosted grist-core):** check whether `GRIST_SANDBOX_FLAVOR=pyodide` is set in your environment. Affected: grist-core < 1.7.9. Upgrade to **≥ 1.7.9**, or switch `GRIST_SANDBOX_FLAVOR` to `gvisor` if you can't upgrade immediately.
- **Cohere Terrarium (self-hosted):** check your deployed image tag. Affected: < v1.0.1. Upgrade to **≥ v1.0.1**.
- **Hugging Face smolagents:** if you use the Pyodide+Deno sandbox mode (as opposed to Blaxel/E2B/Modal/Docker), treat it as unproven until Hugging Face publishes a fix confirmation — `LocalPythonExecutor` and the Pyodide sandbox are explicitly documented by Hugging Face as "best-effort mitigations only, not a security boundary." Separately, confirm you're past 1.17.0 for the older CVE-2025-5120.
- **Any of `langchain-sandbox`, `stlite`, `cibuildwheel`:** check each project's own security advisories page directly; this sweep found no fixed-version data to report.

## If you are affected

See [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for triage steps if you believe sandboxed code reached your host, and [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) if the affected service had live cloud or integration credentials in its environment.

## Prevention

See [agent-sandboxing.md](../prevention/agent-sandboxing.md). The structural lesson, also drawn in this repo's [vm2/isolated-vm advisory](2026-08-vm2-isolated-vm-sandbox-escapes.md): **a JS/WASM sandbox around untrusted Python or JavaScript is a mitigation, not a security boundary.** If your product's answer to "what if the model or the user writes something malicious?" is "it runs in Pyodide/vm2/isolated-vm," treat that as reducing risk, not eliminating it — pair it with OS-level isolation (a real container or VM) for anything that touches credentials or a multi-tenant host.

## Sources

- [eSecurity Planet — DEF CON 34: One Pyodide Flaw Exposed Seven Products](https://www.esecurityplanet.com/threats/def-con-34-one-pyodide-flaw-exposed-seven-products/) — DEF CON 34 talk summary, researcher names, all seven affected products, CVE list (2026-08-10).
- [Cyera Research — N8Scape: 9.9 Critical Post-Auth RCE in n8n (CVE-2025-68668)](https://www.cyera.com/research/n8scape-pyodide-sandbox-escape-9-9-critical-post-auth-rce-in-n8n-cve-2025-68668) — primary researcher writeup for the n8n finding.
- [Cyera Research Labs — Cellbreak: Grist's Pyodide Sandbox Escape and the Data-at-Risk Blast Radius](https://www.cyera.com/research-labs/cellbreak-grists-pyodide-sandbox-escape-and-the-data-at-risk-blast-radius) — primary researcher writeup for the Grist finding.
- [NVD — CVE-2025-68668](https://nvd.nist.gov/vuln/detail/CVE-2025-68668) — CVSS 9.9, affected/patched n8n versions, GHSA reference.
- [NVD — CVE-2026-24002](https://nvd.nist.gov/vuln/detail/CVE-2026-24002) — CVSS 9.1, affected/patched Grist versions, GHSA reference.
- [GitHub Security Advisory — GHSA-cmpr-pw8g-6q6c (Cohere Terrarium sandbox escape)](https://github.com/advisories/GHSA-cmpr-pw8g-6q6c) — canonical source confirming the real CVE ID is CVE-2026-5752, CVSS 9.3, patched v1.0.1.
- [Miggo Vulnerability Database — CVE-2025-5120: smolagents Sandbox Escape RCE](https://www.miggo.io/vulnerability-database/cve/CVE-2025-5120) — the earlier, distinct smolagents `local_python_executor.py` bug, fixed 1.17.0.
