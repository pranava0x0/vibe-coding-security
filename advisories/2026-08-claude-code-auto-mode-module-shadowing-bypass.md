---
id: 2026-08-claude-code-auto-mode-module-shadowing-bypass
title: "Claude Code Auto Mode (Opus 5) — module-shadowing chain turns 'summarize this page' into RCE; Anthropic: working as designed"
date_disclosed: 2026-08-26
last_updated: 2026-09-10
severity: high
status: active
ecosystems: [claude-code, anthropic, python]
tools_affected: [claude-code, claude-code-auto-mode, opus-5, any-agent-that-writes-and-runs-its-own-helper-scripts]
tags: [prompt-injection, auto-mode, classifier-bypass, module-shadowing, python, steganography, no-cve, vendor-declined, working-as-designed]
---

## TL;DR

Two independent researchers showed within the same fortnight that **Claude Code's Auto Mode** — the default since mid-August 2026, in which Claude decides for itself which tools to run without asking — can be walked into executing attacker code from nothing more than a "summarize this website" request. Johann Rehberger's chain (published 2026-08-26) succeeded in **60–80%** of trials; a second researcher's steganographic variant succeeded in **6 of 10**. Neither needed a jailbreak: every individual step looked benign to the safety classifier, and in Rehberger's chain the step that fired the payload was Claude *refusing* to run a suspicious binary and writing its own Python decoder instead — which imported a poisoned `struct.py` sitting in the directory it had just unpacked. Anthropic closed the report as **"Informative"**: Auto Mode is "a convenience feature backed by a best-effort classifier, not a security guarantee." No fix is planned. **Treat Auto Mode approval as no evidence that a command is safe, and run the agent inside a sandbox with egress control.**

## What happened

### The chain (Rehberger, embracethered.com, 2026-08-26)

1. The user asks Claude Code to summarize a URL. Claude's `WebFetch` tool tries it.
2. The attacker's server answers **HTTP 415** (Unsupported Media Type). Claude falls back to `curl` in bash.
3. The redirect lands on a ZIP archive. Claude downloads and unpacks it: encoded "records," a binary decoder, and some Python files.
4. Claude **declines to run the supplied binary** — the safety behaviour working as intended.
5. Claude writes its own small Python decoder to finish the task, and runs it from the extracted directory.
6. That decoder does `import base64`. Python's import resolution searches the script's own directory first, so the attacker's **`struct.py`** in the unpacked folder shadows the standard library module that `base64` depends on. The poisoned module runs.
7. The payload launches a remote stager, which fetches native malware with a command-and-control callback.

No single step is a "run this malware" instruction. The classifier that backs Auto Mode scores actions, and each action — fetch, fall back to curl, unpack, refuse the binary, write a helper, run the helper — is individually reasonable. Rehberger's line: *"Ironically, that safety decision is the exploit path."*

Three variants were tested five times each: a `python3 -I -c` chain to a C2 stager (**3/5**), a `claude -p` subprocess doing reconnaissance and launching Calculator (**3/5**), and a `claude -p` subprocess writing files (**4/5**). Small samples, but consistent with the second researcher's numbers.

### The second, independent chain (IT Meets OT, itmeetsot.eu)

A separate researcher tested **Claude Code 2.1.228, Opus 5 in auto mode, with Sonnet 5 as the safety classifier**. Here the instructions were hidden **steganographically in the repository's only image** — split the luminance plane into 8×8 blocks, DCT each, read the signs of low-frequency coefficients as ASCII — and the write-up describes "adversarial trajectory guidance": soft nudges spread across the chain that steer the model toward the unsafe action rather than one blunt instruction. Execution was achieved by having the agent wrap untrusted code in `sys.addaudithook()`, a Python mechanism documented as not being a security boundary. Success in **6 of 10** trials; the classifier blocked the other four. (The post's URL carries a 2026-08-12 date; the fetched page references an update on 2026-08-29 acknowledging Rehberger's parallel findings.)

Two researchers, two delivery mechanisms (HTTP content-negotiation fallback vs. image steganography), two execution primitives (module shadowing vs. an audit hook), one root cause: **Auto Mode's classifier evaluates steps, and a chain of individually-benign steps is not a benign chain.**

### Anthropic's response

Rehberger first sent the report to Anthropic's model bug-bounty address and received no response, then re-filed through the security reporting channel. Anthropic closed it as **"Informative," "working as designed."** Its stated position, quoted by the researcher and by The Next Web: Auto Mode is *"a convenience feature backed by a best-effort classifier, not a security guarantee,"* determined prompt-injection chains built from benign steps fall outside the classifier's scope, and **OS isolation and network controls are the actual security boundary.** Anthropic did not respond to The Register's request for comment.

That position is defensible engineering — and it is also the reason this entry is `active` rather than `mitigated`: the default configuration of the most widely used AI coding CLI now ships a mode whose approval signal the vendor itself says should not be relied on, and the mitigation is entirely on the user.

### Why this matters for vibe coders

- **Auto Mode is the default now.** If you installed or updated Claude Code after mid-August 2026 and didn't change anything, you're in the mode both researchers tested. Rehberger's post notes Auto Mode became the default in mid-August.
- **The entry point is ordinary.** "Summarize this page" and "look at this repo" are the two most common things people ask a coding agent to do with untrusted input.
- **This is the [0DIN DNS Setup Trap](2026-06-0din-dns-setup-trap.md) pattern generalised.** That advisory documented Claude Code's error-recovery automation being steered through a failing package init; this one steers it through a failing content type. Error recovery is a decision the agent makes on its own, and every such decision is a step an attacker can choose for it.
- **It composes with everything else in this repo.** A repo that already carries a [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md) config, a [TrapDoor-style `CLAUDE.md`](2026-05-trapdoor-cross-ecosystem-stealer.md), or an [aider `.aider.conf.yml`](2026-09-aider-conf-yml-command-execution.md) now also gets to include an image.

## Am I affected?

You are exposed if you run Claude Code in Auto Mode (the default since mid-August 2026) against content you did not author, **outside** an OS-level sandbox with restricted egress.

```bash
claude --version           # 2.1.228 was the build in the steganography test; the chain is behaviour, not a version bug
# Look for Python files named after stdlib modules sitting in project or download directories —
# the module-shadowing primitive needs one of these next to a script the agent will run:
find ~ -maxdepth 4 \( -name 'struct.py' -o -name 'base64.py' -o -name 'json.py' -o -name 'os.py' \) \
     -not -path '*/site-packages/*' -not -path '*/lib/python*' 2>/dev/null
# Review recent agent sessions for a WebFetch → curl fallback followed by an archive unpack:
grep -rl 'curl' ~/.claude/projects/ 2>/dev/null | head
```

If a session matches that shape and you weren't running in a container, assume the payload ran with your user's credentials.

## If you are affected

[playbooks/if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md), then [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md). The stager fetched native malware — a compromised host, not just a leaked token.

## Prevention

- [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — the vendor's own answer. Container, VM, or OS sandbox; **egress allow-list** (both chains phone home); no SSH keys or cloud credentials mounted into the agent's environment.
- Do not treat Auto Mode approval as review. If you want a human gate on network fetches and archive extraction, leave Auto Mode off for untrusted input.
- Don't assume interpreter flags close the shadowing path — Rehberger's 60% variant ran under `python3 -I -c` and still succeeded. The durable fix is procedural: never execute anything, including a helper the agent just wrote, from inside an unpacked untrusted archive; copy the script to a clean directory first, or don't run it.
- Both researchers' mitigation advice reduces to Rehberger's closing line: *"Do not trust the model output."*

## Sources

- [Embrace The Red (Johann Rehberger) — Breaking Claude Code Opus 5 and Auto Mode](https://embracethered.com/blog/posts/2026/breaking-claude-code-opus-5-and-automode/) — fetched 2026-09-10; primary research, published 2026-08-26: the full chain, three variants with 3/5, 3/5, 4/5 success, the disclosure timeline (bug-bounty address unanswered → security channel → closed "Informative"), Anthropic's quoted position, mitigations.
- [IT Meets OT — Prompt injection against Claude Code Opus 5 auto-mode via steganography](https://itmeetsot.eu/posts/2026-08-12-opus5_automode/) — fetched 2026-09-10; independent second researcher: Claude Code 2.1.228 / Opus 5 / Sonnet 5 classifier, DCT-coefficient image payload, `sys.addaudithook()` execution primitive, 6/10 success, update acknowledging Rehberger's parallel work.
- [The Register — Researcher shows how Claude Code can be tricked simply by asking it to summarize a website](https://www.theregister.com/research/2026/08/28/researcher-shows-how-claude-code-can-be-tricked-simply-by-asking-it-to-summarize-a-website/5293372) — fetched 2026-09-10; published 2026-08-28: independent coverage confirming the chain, the 60–80% figure, Auto Mode as default since mid-August, and that Anthropic did not respond to a request for comment.
- [The Next Web — A researcher hijacked Claude Code by asking it to summarise a web page](https://thenextweb.com/news/claude-code-prompt-injection-summarise-website-auto-mode) — fetched 2026-09-10; published 2026-09-01: Anthropic's "convenience feature backed by a best-effort classifier" statement, context on the mid-August Auto Mode default.
- [Adversa AI — Top AI coding agent security resources, September 2026](https://adversa.ai/blog/top-ai-coding-agent-security-resources-september-2026/) — fetched 2026-09-10; roundup that surfaced both primary posts for this sweep (aggregator, not an independent source).
