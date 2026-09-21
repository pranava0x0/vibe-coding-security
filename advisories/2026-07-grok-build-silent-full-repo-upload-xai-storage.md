---
id: 2026-07-grok-build-silent-full-repo-upload-xai-storage
title: "xAI's Grok Build CLI uploaded every repository it was opened in — as a git bundle with full history, including tracked .env files and files the agent was told not to read — to a Google Cloud Storage bucket; the 'Improve the model' toggle did not stop it (5.10 GiB out for a task that needed 192 KB); xAI switched uploads off server-side on 2026-07-13 and Musk promised deletion, but the upload code stayed in the client"
date_disclosed: 2026-07-12
last_updated: 2026-09-21
severity: high
status: mitigated
ecosystems: [grok-build, xai, ai-coding-cli, macos, linux]
tools_affected: ["xAI Grok Build CLI 0.2.93 (and, per the wire analysis, earlier builds with the same storage channel)", "any repository opened in Grok Build before 2026-07-13", "every secret in those repositories' tracked files and git history"]
tags: [data-exposure, ai-vendor-hygiene, coding-agent, secrets-exposure, git-history, telemetry, opt-out-ineffective, repo-upload, grok-build]
---

## TL;DR
On **2026-07-12** a researcher publishing as **cereblab** put xAI's **Grok Build** CLI (version 0.2.93) behind `mitmproxy` and found two channels out of the developer's machine: `POST /v1/responses`, carrying what the agent actually read, and **`POST /v1/storage`**, carrying the **whole repository as a git bundle** — every tracked file, whether or not the model opened it, plus full commit history — into a Google Cloud Storage bucket named `grok-code-session-traces`. On a 12 GB repository the model channel used **196,705 bytes in five requests**; the storage channel sent **5,476,228,005 bytes (5.10 GiB) in 82 POSTs** before capture was stopped, every one answered `HTTP 200`. A tracked `.env` with canary `API_KEY` and `DB_PASSWORD` values went out unredacted in both channels; a file the agent was told "do not read any files" about was recovered verbatim by cloning the captured bundle. Turning off the **"Improve the model"** toggle changed nothing — the server still answered `trace_upload_enabled: true`, because that setting governs *training consent*, not *transmission*. By **2026-07-13** the same binary made zero storage requests: xAI had flipped a server-side flag (`disable_codebase_upload: true`), and Elon Musk said previously uploaded data would be "completely and utterly deleted." The Hacker News reports the upload code was **still present in build 0.2.99**, held off only by that server flag. Filed here in September as the precedent for [Zhipu ZCode](2026-09-zhipu-zcode-silent-workspace-git-history-upload.md), which repeated all three failures ten weeks later.

## What happened

**The wire analysis (cereblab, 2026-07-12).** Routing `grok` 0.2.93 (SHA-256 `2a97ba67…d767c`) through a local proxy showed a `GET /v1/settings` on start-up returning `upload_enabled: true`, `trace_upload_enabled: true`, `session_registry_enabled: true` and `max_upload_file_bytes: 1073741824`, then repository snapshots leaving as git bundles in ~75 MB chunks to `POST /v1/storage`. The binary carried the literal strings `grok-code-session-traces` and `storage.googleapis.com`, and the manifests showed destination paths of the form `gs://grok-code-session-traces/repo_changes_dedup/v2/supplemental/sha256_…`. Two independent repositories produced the same behaviour.

**The canary proof.** In a repo containing `src/_probe/never_read_canary.txt` with a unique marker, the prompt was "Reply exactly OK, do not read any files." The agent replied OK; the storage channel uploaded a bundle; `git clone` of the captured bundle recovered the never-read file with its marker, plus the full history. The [reproduction harness](https://github.com/cereblab/grok-build-exfil-repro) makes the point that matters for permission systems: **`--deny` rules and settings-file denials stop the agent *reading* a file into the conversation; they do not keep that tracked file out of the bundle. Only `.gitignore` does.**

**The toggle.** With "Improve the model" off, `/v1/settings` still returned `trace_upload_enabled: true` and bundles kept landing with `HTTP 200`. One commenter's summary that cereblab adopted: the opt-out is "a data-*retention* setting, not a block on what's *sent*." The Next Web notes xAI had marketed Grok Build with the claim that "nothing from your codebase [is] transmitted to xAI servers during a session."

**The response.** The Hacker News (published 2026-07-14) reports that by **2026-07-13** the same binary had stopped making storage requests — six retests, zero `/v1/storage` calls — with the server now returning `disable_codebase_upload: true`; that xAI's account stated enterprise zero-data-retention customers never had code stored and individual subscribers should run `/privacy` in the CLI; and that Musk promised previously uploaded data would be "completely and utterly deleted." The same article's key concern: the upload code remained in build **0.2.99**, "held only by a server flag — meaning xAI could reactivate uploads without requiring a client update." The Next Web: "No independent audit has verified the claimed data deletion."

**Local veto.** cereblab's gist records community-verified controls with precedence env > config > remote: `[harness] disable_codebase_upload = true` in `~/.grok/config.toml` blocks whole-repo uploads even against remote overrides; `GROK_TELEMETRY_TRACE_UPLOAD=false` / `GROK_TELEMETRY_ENABLED=false` in the environment (or `[features] telemetry = false`, `[telemetry] trace_upload = false` in config) cover the session-trace channel. These came from commenters on the analysis, not from xAI documentation; verify them with a canary before relying on them.

**Why it is in this corpus.** Grok Build already appears here as an *affected* product in [SymJack](2026-06-symjack-ai-coding-agent-mcp-symlink.md) and [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md). This file is about the vendor side: a coding CLI's own storage channel is an exfiltration path that no prompt, deny rule or sandbox around the *model* constrains, and it moved 27,800× more bytes than the model needed. Ten weeks later [ZCode](2026-09-zhipu-zcode-silent-workspace-git-history-upload.md) did the same with `.git` history and a vendor-held encryption key — two independent vendors, one design: "the toggle controls training, the upload is separate."

## Am I affected?

- **Affected if:** you ran Grok Build (any build up to and including 0.2.93, and by the same channel any earlier build) on a repository before 2026-07-13 while the server default was upload-on. Everything tracked in that repo, and its history, was eligible for upload up to the 1 GiB per-file cap; a tracked `.env` went in plaintext.
- **Not affected if:** you first ran it after 2026-07-13 with the server flag off, or you had set `disable_codebase_upload = true` locally (only possible once the analysis surfaced the key), or the repository was on an enterprise zero-data-retention plan per xAI's statement.

```bash
# Version
grok --version 2>/dev/null
# Local veto (community-verified; confirm with a canary run behind a proxy)
cat ~/.grok/config.toml 2>/dev/null | grep -n "disable_codebase_upload\|trace_upload\|telemetry"
# Watch the wire yourself: run once behind mitmproxy on a throwaway repo with a canary .env
HTTPS_PROXY=http://127.0.0.1:8080 SSL_CERT_FILE=~/.mitmproxy/mitmproxy-ca-cert.pem grok
# In mitmproxy: any POST /v1/storage is a whole-repo upload; the model channel is /v1/responses

# What went with it: every secret in tracked files and history
gitleaks detect --source . --log-opts="--all" 2>/dev/null | head
```

## If you are affected

1. **Rotate every secret that was tracked in any repository you opened in Grok Build** — `.env` files were confirmed unredacted in both channels — and everything in those repos' history: [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md), [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md), [if-your-npm-token-leaked.md](../playbooks/if-your-npm-token-leaked.md).
2. Set the local veto (`disable_codebase_upload = true`) and the telemetry environment variables before the next run; the server flag is the vendor's decision, the config key is yours.
3. If the code was under NDA or regulation, the exposure window is first use → 2026-07-13, and the deletion promise is unaudited.

## Prevention

- **Keep secrets out of tracked files and history entirely** ([prevention/credential-hygiene.md](../prevention/credential-hygiene.md)); a coding tool's side channel does not respect a deny rule.
- **Proxy a new AI coding tool once before trusting it** with real code — a throwaway repo, canary secrets, `mitmproxy`, and a look at every endpoint it talks to. Both incidents in this class were found that way, not by reading settings pages ([prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md)).
- **Run the agent in a sandbox that contains only the working repository** ([prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)); it bounds what a whole-workspace upload can take.
- Treat a "privacy" or "improve the model" toggle as a training-consent setting until the vendor documents, per channel, what stops being *sent*.

## Sources
- [cereblab — What xAI Grok Build CLI actually sends to xAI: a wire-level analysis (grok 0.2.93)](https://gist.github.com/cereblab/dc9a40bc26120f4540e4e09b75ffb547) — primary, 2026-07-12: the two channels, the byte counts (196,705 B vs 5,476,228,005 B, 82 POSTs, ~75 MB chunks), the `grok-code-session-traces` bucket and `gs://` paths, the `/v1/settings` flags, the unredacted `.env` canary, the never-read canary, the toggle result, the 07-13 server-side flag, the config/env vetoes. Fetched 2026-09-21.
- [cereblab/grok-build-exfil-repro](https://github.com/cereblab/grok-build-exfil-repro) — reproduction harness: the canary-repo method, "reply OK, do not open any files," bundle recovery, and the deny-rules-vs-`.gitignore` finding. Fetched 2026-09-21.
- [The Hacker News — Grok Build Uploaded Entire Git Repositories to xAI Storage, Not Just Files It Read](https://thehackernews.com/2026/07/grok-build-uploads-entire-git.html) — 2026-07-14: the 5.10 GB / 73-chunk / 27,800× figures, the 07-13 cessation and `disable_codebase_upload: true`, xAI's statement on zero-data-retention customers and `/privacy`, Musk's deletion promise, and the upload code still present in 0.2.99. Fetched 2026-09-21.
- [The Next Web — Grok Build was uploading entire Git repositories to xAI's cloud, including committed secrets](https://thenextweb.com/news/grok-build-uploaded-entire-git-repositories-secrets) — 2026-07-14: xAI's prior "nothing from your codebase transmitted" marketing claim, the response summary, and the note that no independent audit has verified deletion. Fetched 2026-09-21.
