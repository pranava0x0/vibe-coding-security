---
id: 2026-10-hugging-face-qwen2-tiny-trust-remote-code-model-repositories-remove-and-rotate
title: "Fake qwen2-tiny model repositories on Hugging Face run code through trust_remote_code: remove the models and the miner, rotate keys"
kind: malicious-artifact
date_disclosed: 2026-10-29
last_updated: 2026-10-30
severity: high
status: unconfirmed
ecosystems: [huggingface, pytorch, transformers, xinference]
tools_affected: ["anyone who loaded a model from the seven Hugging Face accounts below with trust_remote_code=True, directly or through Xinference, since 2026-09-21", "GPU hosts and inference servers holding Hugging Face tokens, cloud credentials and SSH keys"]
tags: [malicious-artifact, hugging-face, model-repository, trust-remote-code, cryptominer, xinference, persistence, credential-theft, pluto-security, single-firm, wave-2-live]
---

## TL;DR
Remove any model loaded from the Hugging Face accounts `hhzz667`, `dsxk4mr8tq`, `MENXIANGYU`, `wjsbg`, `soumikmahato`, `r1r13` or `htt0118` (31 repositories named `qwen2-tiny`, `qwen2-mini`, `qwen2-final`, `llama-tiny-x1019` and variants) from your Hugging Face cache and Xinference registrations, and remove the miner, watchdog, cron entry, startup-file lines and SSH key the loader leaves on the host. Rotate Hugging Face tokens, cloud credentials, passwords and SSH keys the process could reach; Pluto Security (2026-10-29) is the single firm reporting, Hugging Face removed the first two accounts, and five were still live on 2026-10-30.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Hugging Face model repositories (wave 1) | `hhzz667/qwen2-shell`, `qwen2-tiny`, `qwen2-mini`, `qwen2-nano`, `qwen2-legacy`, `qwen2-final`; `dsxk4mr8tq/qwen2-tiny`, `qwen2-tiny-gpt2`, `qwen2-tiny-lite`, `qwen2-tiny-pure`, `qwen2-tiny-real`, `qwen2-tiny-assets` | every revision (uploaded 2026-09-21 to 10-12, per Pluto) | remove; the genuine Qwen2 checkpoints are under the `Qwen` organisation | both accounts return 401 from the models API (removed) on 2026-10-30; Pluto says Hugging Face and ModelScope removed them after its report | none (no OSV or database record for model repositories) |
| Hugging Face model repositories (wave 2) | `MENXIANGYU` (13 repositories: `qwen2-tiny` and variants, `qwen2-mini-c4`, `qwen2-mini-c5`, `qwen2-ezv`, `llama-tiny-x1019`, `zz_ext`, `qa-whl-1021`); `wjsbg/eagle-tiny`, `qwen2-tiny-zh21`, `qwen2-final`; `soumikmahato/qwen2-tiny-chat`; `r1r13/qwen-lora-text-v1`; `htt0118/qwen2-tiny` | every revision (wave 2 appeared within days of the wave 1 takedown; `htt0118` created 2026-10-25) | remove; do not load with `trust_remote_code=True` | `MENXIANGYU/qwen2-tiny`, `wjsbg/qwen2-final`, `soumikmahato/qwen2-tiny-chat`, `r1r13/qwen-lora-text-v1` and `htt0118/qwen2-tiny` return 200 (live) on 2026-10-30; Pluto says some were still live eight days after reporting | none |

The repositories carry Python files named in `config.json`'s `auto_map` (Pluto lists `modeling_evil.py`, `modeling_evil2.py`, `modeling_evil6.py`, `modeling_qtz.py`, `modeling_parasit.py`, `configuration_parasit.py`, `modeling_hl.py`) and a binary `syscore.bin`; Transformers runs the named Python before any weights load when `trust_remote_code=True` is set, and no malicious weights are needed. Pluto counts over 32,000 downloads across the campaign and linked repositories, which is downloads, not infections. Pluto also lists linked accounts and repositories outside the 31; this file names only the 31. One firm, one post, no Hugging Face statement read, so `status: unconfirmed`; the wave 1 removals are the registry-side fact that corroborates the report.

## Am I affected?

- You called `from_pretrained` with `trust_remote_code=True` on any repository above, or registered one in Xinference, since 2026-09-21.

```bash
# cached copies of the named repositories
ls -d ~/.cache/huggingface/hub/models--{hhzz667,dsxk4mr8tq,MENXIANGYU,wjsbg,soumikmahato,r1r13,htt0118}--* 2>/dev/null
# remote-code files Pluto names
find ~/.cache/huggingface /root/.xinference 2>/dev/null \( -name 'modeling_evil*.py' -o -name 'modeling_qtz.py' -o -name 'modeling_parasit.py' -o -name 'modeling_hl.py' -o -name 'syscore.bin' \)
# host artifacts Pluto names
ls -la /tmp/.cch /tmp/.cchx /tmp/.kitsd /tmp/.c /tmp/.cache-hf /root/.hl /etc/cron.d/.sync-helper /tmp/.qa_pwned ~/qa_pwned 2>/dev/null
grep -n 'svc.py\|\.cch' /root/.bashrc /root/.profile ~/.bashrc 2>/dev/null
ps -eo pid,user,args | grep -E '\[kworker/u20:1\]' | grep -v grep     # a kernel-thread name with userspace arguments
xinference list 2>/dev/null | grep -E 'qwen2-tiny-|ezv-'              # registrations named qwen2-tiny-<base32> or ezv-<base32>
```

- Any of these, or an unrecognised key in `authorized_keys` on a GPU host, means the loader ran. Pluto notes that no single missing indicator rules out compromise.

## If you are affected

1. Isolate the host and restrict outbound traffic; preserve processes, connections, logs, the model cache and startup files before deleting.
2. Remove the loader files, the miner and watchdog, the cron entry, the startup-file lines, the Xinference registrations and any added SSH key; Pluto also says to review miners the loader deleted as competitors. Rebuild from a trusted image if host integrity cannot be established: [if you ran a malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md) covers the same clean-up order.
3. Rotate Hugging Face tokens, cloud credentials, passwords and SSH keys the process could reach, and review their recent use: [rotating cloud credentials](../playbooks/rotating-cloud-credentials.md).
4. Require authentication on the Xinference API and limit who can reach it; Pluto describes registrations arriving through it.

## Prevention

- Do not set `trust_remote_code=True` for a repository you have not read; review every `.py` file `auto_map` points at, and pin the reviewed revision. The official checkpoints live under the `Qwen` organisation, not under a personal account with a `-tiny` or `-final` suffix.
- Run model loading with limited privileges, no production secrets and restricted egress: [agent sandboxing](../prevention/agent-sandboxing.md).
- A model repository is a package: [package vetting checklist](../prevention/package-vetting-checklist.md), [supply-chain attack surface](../prevention/supply-chain-attack-surface.md).

## Sources
- [Pluto Security — Load/Mine: a Hugging Face malware campaign](https://pluto.security/blog/hugging-face-malware-campaign-load-mine/) — fetched 2026-10-30: 2026-10-29, Shaked Chen, Eitan Chassid and Yotam Perkal; the seven accounts and 31 repositories, the upload dates, the `trust_remote_code` loading condition, the file names, the host paths and process names, the Xinference registrations, the remediation list, the wave 1 takedown and wave 2 reappearance, the 32,000-download figure. Single firm.
- Hugging Face models API (`huggingface.co/api/models/<owner>/<name>`), queried 2026-10-30: `hhzz667/qwen2-tiny` and `dsxk4mr8tq/qwen2-tiny` return 401; `MENXIANGYU/qwen2-tiny`, `htt0118/qwen2-tiny`, `wjsbg/qwen2-final`, `soumikmahato/qwen2-tiny-chat` and `r1r13/qwen-lora-text-v1` return 200.
- Hacker News item 50303651 ("Fake Qwen2 checkpoints on Hugging Face mine crypto via trust_remote_code"), read through the Algolia items API 2026-10-30: 2026-10-30 13:33 UTC, linking the Pluto post. No Hugging Face statement was found this run.
