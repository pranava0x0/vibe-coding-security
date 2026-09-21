---
id: 2026-09-rust-maintainers-fake-interview-video-call-campaign
title: "Rust's crates.io team warns of an ongoing campaign against rust-lang members and popular-crate owners — a fake job, project or contract pitch leads to a video call where the target is asked to install a 'missing audio codec' or run a clipboard command; a June attempt on a crates.io maintainer delivered a RAT hidden in a take-home TypeScript 'test' repo, and the August arrayref compromise fits the same shape"
date_disclosed: 2026-09-17
last_updated: 2026-09-21
severity: high
status: active
ecosystems: [crates-io, rust, linkedin, npm]
tools_affected: ["crates.io maintainer accounts", "rust-lang team members", "cargo (any project building a crate whose owner was compromised)", "any developer sent a 'take-home test' repository to build locally"]
tags: [social-engineering, dprk, contagious-interview, supply-chain, crates-io, maintainer-compromise, rat, take-home-test, video-call, clipboard-injection]
---

## TL;DR
On **2026-09-17** the Rust project's crates.io team and Security Response Working Group published ["Be alert: targeted attacks on prominent Rustaceans"](https://blog.rust-lang.org/2026/09/17/targeted-attacks/): an **ongoing** campaign is targeting "rust-lang members and owners of popular crates." The pattern: an approach "for something positive — maybe for a job, maybe for a project, maybe for a contract opportunity" from a "new but legitimate seeming" company with a plausible LinkedIn presence, then a video call used "to either get the target to install something on their computer (such as a purportedly missing audio codec) or execute another command" placed on the clipboard. The post ties two prior events to the pattern: a **June 2026** attempt on crates.io maintainer Matt Mastracci — a fake Singapore VC, a video call, then a "Ticket Harbor" TypeScript repo to build as a test, carrying a multi-stage loader for a RAT — and the **[August arrayref compromise](2026-08-arrayref-proc-macro1-crates-io.md)** (~245M lifetime downloads, malicious versions live under two hours). The style "is known to be used by the DPRK"; the Rust team says it does not know whether every incident is one campaign. The goal is a maintainer's machine or account, so that malware ships from a name nobody has reason to distrust. Recommendations: treat unsolicited approaches with suspicion however credible they look, hold calls on a platform *you* set up, enable MFA, check login history, and report to `help@crates.io` / `security@rust-lang.org`.

## What happened

**The warning (2026-09-17).** Adam Harvey, writing for the crates.io team and the security response working group, describes the lure and the two payload paths — a fake codec install, or a command the target is talked into pasting from the clipboard — and the infrastructure: freshly created company identities with LinkedIn profiles built to survive a quick check. The post links the June attempt and the August arrayref incident as examples, and points to existing documentation of the DPRK "Contagious Interview" tradecraft. It does not name a group.

**The June attempt, in the target's own words.** Matt Mastracci (a crates.io maintainer) published ["Anatomy of a Failed (Nation-State?) Attack"](https://grack.com/blog/2026/06/25/dissecting-a-failed-nation-state-attack/) on 2026-06-25. A persona claiming to represent **Lua Ventures** — a Singapore venture firm that turned out to be defunct — emailed about advisory work, name-dropped two portfolio companies, held an unremarkable video call, and then sent the "test": a TypeScript ferry-ticketing repository called **Ticket Harbor**, with instructions to run "typecheck, test suite, and relevant desktop/server build commands before submitting." Inside: patch files that injected code into the TypeScript compilation tooling, a self-executing stub obfuscated with Base64 and XOR, a payload hidden in `operators/3.png`, and a WASM stub that spawned a detached Node process carrying a 1.68 MB obfuscated second stage — a RAT Mastracci calls **PinpinRAT**, with system fingerprinting, file exfiltration, arbitrary command execution and DNS tunnelling. He caught it because he had Claude analyse the repository before running anything, and the patch files stood out; nothing executed. He reported it to Canadian authorities the week of 2026-06-25.

**The August compromise.** The [arrayref / proc-macro1 incident](2026-08-arrayref-proc-macro1-crates-io.md) (2026-08-20) — a compromised owner account publishing malicious versions of three crates that pulled a typosquatted build-time dropper — is, per the Rust blog, an example of what this campaign is for. The Register notes "evidence suggested compromised maintainer credentials."

**Context from the press (2026-09-21).** SecurityWeek: the techniques "matched previous North Korean attack patterns"; the Rust team "did not know whether all of these incidents are part of the same campaign." The Register: the tactics resemble the fake-recruiter campaigns described in an international advisory from Australia, Germany, Japan and the US; Help Net Security summarises that advisory as counting **30,000+ infected devices in 100+ countries** and **7,000+ cryptocurrency wallets** between December 2025 and July 2026, with infrastructure shared with the DPRK IT-worker operation.

**Why this file exists when the corpus already has Contagious Interview.** The [PolinRider](2026-03-polinrider-multi-ecosystem-dprk-campaign.md), [Joyfill](2026-07-joyfill-npm-devpopper-rat.md) and [WeaselBiscuit](2026-09-weaselbiscuit-npm-chrome-extension-storage-stealer.md) files document the same actor class hitting npm and Packagist. This is the first time a **registry's own security team** has warned that its maintainers are being worked as a class, and the first with a maintainer's first-person account of the take-home-repo variant. For this audience the take-home repo is the part that matters: **a repository you are asked to build is a payload delivery format**, whether you build it by hand or hand it to a coding agent — the same trust boundary as [GitSpawn](2026-09-gitspawn-git-config-agent-rce-cluster.md) (a repo's `.git/config` runs commands when an agent opens it) and the [Codex/Cursor git-hook bugs](2026-09-gitspawn-git-config-agent-rce-cluster.md).

## Am I affected?

You are a target if you own a crate, an npm package, a PyPI project or a GitHub Action with meaningful downloads, or hold a role on a language or registry team. The signals are on the human side, not in a lockfile:

- An unsolicited job, advisory, "project" or contract approach from a company you cannot find independent history for (recent LinkedIn page, no press, no product).
- A video call that ends with a request to install something (an "audio codec," a "meeting plugin") or to run a command from the clipboard.
- A "test" or "take-home" repository you are asked to **build or run locally** — especially one with patch files, `postinstall`/`prepare` scripts, binaries or images in unexpected places, or a WASM blob in a web app.

```bash
# Before building any repository someone sent you: look before you run.
git -C the-repo log --oneline | head            # one or two commits from a fresh account is a tell
find the-repo -name "*.patch" -o -name "patches" -o -name "*.wasm" -o -name "*.node" | head
grep -rn "postinstall\|preinstall\|prepare" the-repo/package.json
# Signals from the June sample (Mastracci): a process named PinpinWrappedJs, a hidden
# ~/.cache-<randomhex> directory, and outbound traffic to 89.124.107.161:80 from a dev box
pgrep -fl PinpinWrappedJs; ls -d ~/.cache-* 2>/dev/null
# crates.io / npm / GitHub: unrecognised sessions, tokens or publishes
# crates.io → Account Settings → API Tokens; GitHub → Settings → Sessions and → Applications
```

## If you are affected

If you ran a "test" repository or installed something on a recruiter's call and the machine holds publishing credentials: assume the machine and every token on it are gone. Follow [if-your-local-ai-agent-was-exploited.md](../playbooks/if-your-local-ai-agent-was-exploited.md) for the host (it is the same job: an untrusted repo executed as you), then [if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) and [rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) from a *different* machine. Revoke and re-issue crates.io and npm tokens, check what was published under your name in the window, and tell the registry (`help@crates.io`, `security@rust-lang.org`) — the Rust team asked to hear about attempts, not only successes.

## Prevention

- **Build unknown repositories only in a throwaway sandbox** — a container or microVM with no credentials mounted ([prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)). This applies doubly when a coding agent does the building: it will run the same `postinstall`, hook or patch step you would.
- **Read the repo before you run it.** Mastracci's save was a review pass (with an LLM) before executing anything; [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) is the checklist.
- **Hold calls on your own platform**, never install "codecs" or paste commands mid-call, and treat a recruiter's insistence on *their* meeting link as the signal.
- **Hardware-key MFA on registry and GitHub accounts, scoped short-lived publish tokens, and Trusted Publishing** where the registry offers it ([prevention/credential-hygiene.md](../prevention/credential-hygiene.md)). A compromised laptop still publishes, but it publishes once and visibly rather than quietly for months.
- Downstream: pin and audit dependencies, and watch registry security posts — the arrayref window was under two hours because someone reported it.

## Sources
- [Rust Blog — Be alert: targeted attacks on prominent Rustaceans](https://blog.rust-lang.org/2026/09/17/targeted-attacks/) — primary, 2026-09-17, Adam Harvey for the crates.io team and security response WG: the lure, the codec/clipboard payload paths, the fake-company/LinkedIn infrastructure, the June and August references, the DPRK attribution of the style, the recommendations and reporting addresses. Fetched 2026-09-21.
- [Matt Mastracci — Anatomy of a Failed (Nation-State?) Attack](https://grack.com/blog/2026/06/25/dissecting-a-failed-nation-state-attack/) — primary for the June attempt, 2026-06-25: Lua Ventures persona, the video call, the "Ticket Harbor" test repo, the patch-file/PNG/WASM loader chain, PinpinRAT capabilities, the Claude-assisted review that caught it, the process-name and cache-directory signals. Fetched 2026-09-21.
- [SecurityWeek — Rust Team Members and Popular Crate Owners Targeted via Video Calls](https://www.securityweek.com/rust-team-members-and-popular-crate-owners-targeted-via-video-calls/) — 2026-09-21; the DPRK-pattern match, the "did not know whether all of these incidents are part of the same campaign" statement, the June/August timeline. Fetched 2026-09-21.
- [The Register — Rustaceans warned of job interviews with a malicious payload](https://www.theregister.com/security/2026/09/21/rustaceans-warned-of-job-interviews-with-a-malicious-payload/5297690) — 2026-09-21; the international advisory framing, the defunct-VC detail, arrayref's ~245M downloads and sub-two-hour window, "compromised maintainer credentials." Fetched 2026-09-21.
- [Help Net Security — North Korea's job interview scam runs both ways](https://www.helpnetsecurity.com/2026/09/21/north-korean-hackers-contagious-interview-defenses/) — 2026-09-21; the Rust warning in the context of the Contagious Interview / WaterPlum campaign and the joint Japan–US–Australia–Germany advisory's 30,000-device / 7,000-wallet figures (the advisory PDF itself was not fetched). Fetched 2026-09-21.
