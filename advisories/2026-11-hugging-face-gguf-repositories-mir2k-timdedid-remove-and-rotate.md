---
id: 2026-11-hugging-face-gguf-repositories-mir2k-timdedid-remove-and-rotate
title: "Five malicious GGUF model repositories on Hugging Face (Mir2k, timdedid): delete the files and rotate browser-stored passwords"
kind: malicious-artifact
date_disclosed: 2026-11-27
last_updated: 2026-11-28
severity: medium
status: contained
ecosystems: [huggingface, gguf, llama-cpp, ollama, lm-studio]
tools_affected: ["llama.cpp", "LM Studio", "Ollama", "any agent that runs a local GGUF model with tool access"]
tags: [malicious-artifact, malicious-model, supply-chain, huggingface, gguf, chat-template]
---

## TL;DR

[Malspark reports](https://malspark.com/blog/malicious-gguf-models-hugging-face/) five malicious GGUF model repositories on Hugging Face under the accounts `Mir2k` and `timdedid`, and the Hugging Face API showed all five as disabled on 2026-11-28. If you ran one, delete the file and rotate passwords saved in your browser, wallet extension credentials and anything else stored or typed on that machine.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| Hugging Face | `Mir2k/Huihui-Qwen3.5-9B-abliterated-GGUF` | all, created 2026-11-22 | delete; no clean release | disabled (2026-11-28 15:23 UTC) | none |
| Hugging Face | `Mir2k/Inkling-2-Mini-Uncensored-GGUF` | all, created 2026-11-24 | delete; no clean release | disabled (2026-11-28 15:23 UTC) | none |
| Hugging Face | `timdedid/qwen3.8-cyber-uncensored` | all, created 2026-11-21 | delete; no clean release | disabled (2026-11-28 15:23 UTC) | none |
| Hugging Face | `timdedid/qwen3-cyber-UNCENSORED-2` | all, created 2026-11-22 | delete; no clean release | disabled (2026-11-28 15:23 UTC) | none |
| Hugging Face | `timdedid/qwen3-cyber-UNCENSORED` | all, created 2026-11-21 | delete; no clean release | disabled (2026-11-28 15:23 UTC) | none |
| Ollama | `timdedid/qwen3-1.7b-cyber`, named by Malspark | all | delete | not checked | none |

Malspark scanned 3,273,389 public model repositories on 2026-11-26 and counted 2,428 downloads of the five on 2026-11-27. It notes that Hugging Face counts downloads, not users. Its post said all five were online on 2026-11-27. The Hugging Face API listed 2,807 downloads across the five when read on 2026-11-28. Malspark's post is the only narrative source.

## Am I affected?

```bash
find ~ -name '*.gguf' 2>/dev/null | grep -iE 'Huihui-Qwen3.5-9B-abliterated|Inkling-2-Mini-Uncensored|qwen3.8-cyber-uncensored|qwen3-cyber'
ls ~/.cache/huggingface/hub 2>/dev/null | grep -iE 'Mir2k|timdedid'
ollama list 2>/dev/null | grep -i timdedid
```

The GGUF file names the API listed are `Huihui-Qwen3.5-9B-abliterated-Q5_K_M.gguf`, `Inkling-2-Mini-Uncensored-Q4_K_M.gguf`, `qwen3.8-cyber-uncensored.gguf` and `qwen3-cyber-1.7b-Q4_K_M.gguf`. Malspark publishes an open-source scanner, gguf-radar, that checks a file without running the model.

## If you are affected

- Delete the model files and remove them from LM Studio, Ollama and any internal model registry.
- Rotate passwords saved in Chrome, Edge or Brave, and wallet extension credentials. Malspark also lists any other credential stored on or typed into the machine.
- If the model ran inside an agent with tool access, follow [if your local AI agent was exploited](../playbooks/if-your-local-ai-agent-was-exploited.md).

## Prevention

- Do not run a command that a model suggests without reading it.
- Malspark's advice for agents with tool access is to pass a reviewed chat template with `--chat-template-file` in llama.cpp or `TEMPLATE` in an Ollama Modelfile.
- Download models from publishers you can identify, and scan new files before they reach a developer machine. See the [package vetting checklist](../prevention/package-vetting-checklist.md).

## Sources

- [Malspark, "Malicious GGUF models on Hugging Face", Düzgün, 2026-11-27](https://malspark.com/blog/malicious-gguf-models-hugging-face/), read 2026-11-28 through a summarizing fetch. The repositories, dates, download counts, runtimes, credential categories and remediation.
- Hugging Face API, `huggingface.co/api/models/<owner>/<name>` for each of the five, read 2026-11-28 15:23 UTC. Creation dates, `disabled: true`, download counts, file names.
- [Hacker News item 50676752](https://news.ycombinator.com/item?id=50676752), 71 points on 2026-11-28. Where the sweep found the post.
