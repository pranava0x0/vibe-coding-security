---
id: 2026-09-unsloth-studio-model-inspection-trust-remote-code-ace
title: "Unsloth Studio — selecting a Hugging Face model in the fine-tuning UI ran Python shipped inside the model repository, because the backend's config probe defaulted to trust_remote_code=True and ignored the user's own setting; the vulnerable Studio shipped inside the GA `unsloth` PyPI package; fixed 2026.6.9 (June 2026), no CVE and no vendor advisory by maintainer choice (Pillar Security, 2026-09-29)"
date_disclosed: 2026-09-29
last_updated: 2026-10-01
severity: high
status: patched
ecosystems: [pypi, huggingface, ai-ml-tooling]
tools_affected: ["unsloth (PyPI) < 2026.6.9, Studio backend", "Unsloth Studio (browser UI, beta)", "any tool that calls transformers AutoConfig.from_pretrained with trust_remote_code=True on a user-selected model"]
tags: [arbitrary-code-execution, trust-remote-code, huggingface, model-supply-chain, fine-tuning, no-cve, silent-fix, auto-map, config-json, credential-theft]
---

## TL;DR

Pillar Security published on **2026-09-29** that **Unsloth Studio** — the browser UI bundled in the `unsloth` fine-tuning package — executed Python shipped inside a Hugging Face model repository the moment a user **selected** the model in the picker. The backend's capability probe called `transformers` with `trust_remote_code=True` by default, before any weights were loaded and before the user's own `trust_remote_code` toggle (default off) was consulted; a model's `config.json` `auto_map` pointing at a sibling `.py` file was enough to run code as the Studio user on a GPU host that typically holds Hugging Face tokens, SSH keys and cloud credentials. Unsloth fixed it in **2026.6.9** (Pillar says the fix shipped 2026-06-18; PyPI shows 2026.6.8 on 06-18 and 2026.6.9 on 06-22) but **declined to publish an advisory or request a CVE** because Studio is labelled beta — even though the vulnerable code arrived through an ordinary `pip install unsloth`. Upgrade, and audit every place your pipeline sets `trust_remote_code=True` on your behalf.

## What happened

**The mechanism (Pillar).** Hugging Face `transformers` lets a model repository declare, in `config.json`, an `auto_map` that points `AutoConfig`, `AutoModel` or the tokenizer at custom Python files shipped next to the weights. That code runs only when the caller passes `trust_remote_code=True` — a deliberate, documented feature that legitimate models (IBM Granite Speech/Vision, DeepSeek-OCR, ChatGLM, early Qwen) depend on. Unsloth Studio's backend, in `studio/backend/utils/models/model_config.py` (Pillar pins line numbers to commit `d91183d`, the 2026.5.10 release), declared `load_model_config(..., trust_remote_code: bool = True)`; the vision/capability probe called it without overriding that default; and a second code path for transformers 5 hardcoded `{"trust_remote_code": True}`. The probe is also reachable directly over HTTP via `GET /api/models/config/{model_name}` and `GET /api/models/check-vision/{model_name}`. So when the operator picked a model, Studio fetched its `config.json` and any `auto_map` targets and **imported them during capability inspection** — "the act of inspecting a model was enough to run its code" — before load, train or export, and before the user's own trust setting was read.

**Impact.** Code ran with the Studio user's permissions in the backend process. Pillar's point is about where that process lives: fine-tuning hosts are GPU boxes that hold Hugging Face tokens, SSH keys, cloud credentials, proprietary training data and model artefacts. Its proof-of-concept opened the OS calculator and wrote a marker file; a real payload need not look malicious at rest, because an `auto_map` module can pass Hugging Face's scanners and fetch a second stage at run time. Pillar explicitly ties the bug to a growing CVE family with the same sink — **CVE-2026-46432 (LMDeploy)**, **CVE-2026-4944 (vLLM)** and **CVE-2026-6859 (InstructLab)**, all hardcoded `trust_remote_code=True` on model load — and notes Unsloth Studio combined the LMDeploy sink with the vLLM "override the user's False" aggravator and moved the trigger earlier, to selection.

**Distribution.** Studio is described as beta, but the vulnerable code shipped inside the standard `unsloth` package: "Users could receive it through an ordinary `pip install unsloth` installation without selecting a beta release or enabling prerelease installation." Exploitation required running Studio and selecting an attacker-controlled model (or, per CSO's account of the fix, a local model directory carrying remote code).

**Vendor response.** Pillar reports that the maintainers disputed the assessment — citing Hugging Face's malware scanning and the beta label — but were responsive and shipped a fix; Pillar re-tested **2026.6.9** and confirmed both the Hugging-Face and local-directory paths are closed (Studio no longer enables arbitrary model loading directly from Hugging Face and no longer trusts remote code from local model files). The maintainers **declined to publish an advisory, and no CVE has been assigned.** CSO Online's 2026-09-30 report carries the same account and quotes researcher Ariel Fogel; The Hacker News listed the finding in its 2026-10-01 ThreatsDay roundup. This sweep found no statement from Unsloth and no entry on the project's GitHub security tab; the PyPI release history is the only vendor-side record of the fix.

**Why it is in this corpus.** Three reasons. (1) **A model repository is a code package.** The corpus already tracks the `transformers` `trust_remote_code=False` bypass (CVE-2026-4372) and the Hugging Face intrusion; this is the consumer-side version — a tool that turned the safe default back on for you. Anyone fine-tuning open models for an agent or app is in the audience. (2) **The fix is silent.** Readers who track CVE feeds, `pip-audit` or Dependabot will never see it; "keep `unsloth` current" is the only control that works. (3) **The same default is one `grep` away in any wrapper you build**: Gradio demos, Streamlit model pickers, FastAPI inference services and agent "load this model" tools that forward a user-chosen repo id into `from_pretrained(..., trust_remote_code=True)` have the identical bug.

## Am I affected?

You were exposed if, on `unsloth` **< 2026.6.9**, anyone launched Unsloth Studio and selected a model repository they did not author — including models suggested by an agent, a tutorial or a search result.

```bash
# 1. Installed version — anything below 2026.6.9 carried the vulnerable Studio backend
pip show unsloth 2>/dev/null | grep -E '^Version:'
pip install -U unsloth          # latest on PyPI at sweep time: 2026.9.14

# 2. Did Studio run on this host? (process history, shell history, the Studio backend's config probe in logs)
grep -rE 'api/models/(config|check-vision)/' ~/.unsloth 2>/dev/null; grep -E 'unsloth.*studio' ~/.bash_history ~/.zsh_history 2>/dev/null

# 3. Which model repos were pulled, and do any carry executable code?
ls ~/.cache/huggingface/hub/ | grep '^models--'
for d in ~/.cache/huggingface/hub/models--*/snapshots/*/; do
  [ -f "$d/config.json" ] && grep -l '"auto_map"' "$d/config.json" && ls "$d"/*.py 2>/dev/null
done

# 4. Your own code: every place a user- or agent-chosen repo id reaches a trusting loader
grep -rnE 'trust_remote_code\s*=\s*True' --include='*.py' . | grep -v site-packages
```

A `config.json` with `auto_map` **and** sibling `.py` files is not proof of compromise — legitimate models ship that way — but if such a repo was selected in Studio on a vulnerable version and you did not expect custom code, treat the host as having run untrusted code.

## If you are affected

1. Upgrade `unsloth` to **2026.6.9 or later** on every machine, including ones that "only use Unsloth core" — the vulnerable backend was in the same package.
2. If an unexpected `auto_map` model was selected on a vulnerable version: rotate the **Hugging Face token**, any **SSH keys** and **cloud credentials** reachable from that host, and review the training-data and artefact stores it could write to — [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) and [playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) cover the order.
3. Treat the model repository as an IOC: record the repo id and revision and report it to Hugging Face.

## Prevention

- **Never let a tool set `trust_remote_code=True` on your behalf.** In your own loaders default it to `False`, pass it explicitly only for the named models that need it, and pin those models by **commit revision** (`revision=`), not by tag, so a later push to the repo cannot add code.
- Run fine-tuning and model-inspection UIs under the same isolation you give a coding agent — a container or VM without ambient cloud credentials, with the Hugging Face token scoped to read-only — see [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).
- Treat a model repository like a package: [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) applies (who published it, what changed in the last revision, does it contain `.py` files it did not have before). Hugging Face's scanners are blocklists and best-effort by their own documentation; they are a layer, not the boundary.
- For AI/ML tooling specifically, "keep it on latest" is a security control, not hygiene: this fix, like several tracked here, has no CVE and will never appear in an audit tool.

## Sources

- [Pillar Security — Look, Don't Load: Model Inspection in Unsloth Studio Leads to Critical Arbitrary Code Execution (Ariel Fogel, 2026-09-29)](https://www.pillar.security/blog/look-dont-load-model-inspection-in-unsloth-studio-leads-to-critical-arbitrary-code-execution) — primary: the `load_model_config` default, the capability-probe and transformers-5 paths, the two HTTP endpoints, commit `d91183d` / release 2026.5.10, the GA-package distribution point, the maintainers' objections and Pillar's replies, fix shipped 2026-06-18 and re-tested in 2026.6.9, "no CVE has been assigned," and the LMDeploy / vLLM / InstructLab CVE comparison. Fetched 2026-10-01.
- [CSO Online — Unsloth's model picker had a code-execution problem (2026-09-30)](https://www.csoonline.com/article/4228910/unsloths-model-picker-had-a-code-execution-problem-2.html) — independent report: confirms the beta-status rationale for declining an advisory/CVE, the GA PyPI distribution, that 2026.6.9 disabled arbitrary loading from Hugging Face and stopped trusting remote code from local model files, and Pillar's advice to upgrade even if Studio is never launched. Fetched 2026-10-01.
- [The Hacker News — ThreatsDay: AI-Powered Zero-Day Chain, 543K Live Secrets, Model Inspection RCE and 13 More Stories (2026-10-01)](https://thehackernews.com/2026/10/threatsday-ai-powered-zero-day-chain.html) — roundup item "Model Inspection in Unsloth Studio Leads to Critical Arbitrary Code Execution," quoting Pillar. Fetched 2026-10-01.
- [PyPI — unsloth release history (JSON)](https://pypi.org/pypi/unsloth/json) — queried 2026-10-01: 2026.5.10 uploaded 2026-06-01, 2026.6.8 on 2026-06-18, 2026.6.9 on 2026-06-22; latest 2026.9.14. The registry is the only vendor-side record of the fix.
- Related in this corpus: [Hugging Face transformers `trust_remote_code=False` bypass and the agentic intrusion](2026-07-huggingface-agentic-intrusion.md) — the model-repository-as-code class this finding extends to a consumer tool.
