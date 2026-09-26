---
id: 2026-09-deep-live-cam-requirements-git-source-dependency-hijack
title: "Deep-Live-Cam (96.6K-star face-swap app): a compromised maintainer account rewrote requirements.txt so `requests` installed from an impersonating GitHub repo whose setup.py ran a hidden loader at pip build time — a Windows/macOS cryptocurrency clipboard hijacker with login persistence; live on main for 9 h 39 min on 2026-09-08/09, reverted after a user's issue"
date_disclosed: 2026-09-09
last_updated: 2026-09-26
severity: high
status: patched
ecosystems: [pypi, python, github, windows, macos]
tools_affected: ["hacksider/Deep-Live-Cam (requirements.txt at commit 7895c547)", "anyone who ran pip install -r requirements.txt between 2026-09-08 15:58 and 2026-09-09 01:37 UTC"]
tags: [supply-chain, github, maintainer-account-compromise, requirements-txt, git-source-dependency, setup-py, pip-build-time-execution, clipboard-hijacker, cryptocurrency, persistence, ai-app]
---

## TL;DR
On **2026-09-08 at 15:58 UTC** a commit titled `chore: update requirements.txt` landed on the `main` branch of **Deep-Live-Cam**, the 96,600-star real-time face-swapping app. It rewrote **18 dependency lines to install from Git sources instead of PyPI**, and one of them pointed `requests` at a GitHub repository created three days earlier under an account named `pypls` whose `setup.py` hides 434 spaces of whitespace followed by obfuscated code that **runs during pip's build step, before the app is ever launched**. On Windows and macOS it fetches a loader from a public paste page, unpacks a **cryptocurrency clipboard hijacker** (Bitcoin, Ethereum, Tron, Solana address swapping) and registers it to run at login. A user spotted it in issue #1930 at 01:26 UTC on 09-09; the maintainer reverted at 01:37 and reported unusual account access despite 2FA. **Exposure window ~9 h 39 min.** Reverting the file does not remove the payload from machines that installed it.

## What happened

SafeDep's technical report (2026-09-09) and the reporter's issue give a consistent timeline:

| UTC | Event |
|---|---|
| 2026-09-05 | GitHub account `pypls` created with a repository named `requests` that keeps the real project's metadata |
| 2026-09-08 15:58:54 | Commit `7895c547a6788ee53e5c7c34e93454f86f6d2b53` on `main`: 18 dependency entries rewritten to Git sources; `requests @ git+https://github.com/pypls/requests.git` among them |
| 2026-09-09 01:26:18 | `fred-cardoso` opens issue #1930, "Supply chain attack – requirements.txt compromised," naming the commit and the `setup.py` |
| 2026-09-09 01:37:35 | Revert commit `55d306d5ae07a4e6494013422ab244306a5c0879` |
| 2026-09-09 01:39:12 | Maintainer reports unusual account access despite two-factor authentication; passwords and keys changed |

The rewrite to `git+https://…` sources is the trick: it looks like a routine "pin to source" change, it bypasses PyPI entirely (so no registry scanner ever saw the package), and pip builds a Git-sourced dependency from its `setup.py`, which is arbitrary Python. SafeDep: "The hidden code precedes both the Python version check and `setup()`," so it executes for every install, including ones where the build later fails. The loader targets Windows and macOS only (Linux exits). Payload drop paths are `%LOCALAPPDATA%\WindowsHelper\sys.pyw` (run via `pythonw.exe` from a `HKCU\…\Run` value named `SysHelper`) and `~/Library/Application Support/HowToFind/sys.py` (a LaunchAgent `com.user.syshelper.plist`, `RunAtLoad` + `KeepAlive`). The final stage watches the clipboard for 26–120-character alphanumeric strings, classifies them as BTC/ETH/TRX/SOL addresses and swaps in the operator's. An error string in Russian is the only language indicator. SafeDep "establishes malicious behavior in the code, but does not establish infection counts or financial losses."

Why it is in this corpus: Deep-Live-Cam is an AI application that its audience installs by cloning and running `pip install -r requirements.txt` — the same motion as every AI-agent, RAG and model-demo repo — and the vector (a maintainer account compromise turning a *requirements file* into the payload carrier, with the code living in a look-alike GitHub repo rather than on PyPI) defeats every registry-side control this repo recommends. It is the Python sibling of the [Mini Shai-Hulud GitHub Actions re-tagging](2026-05-tanstack-mini-shai-hulud.md) lesson: a dependency line that names a mutable Git ref is a supply-chain trust decision, not a version pin.

## Am I affected?

- You ran `pip install -r requirements.txt` (or `pip install -e .`, or any installer that reads it) in a Deep-Live-Cam checkout **updated between 2026-09-08 15:58 and 2026-09-09 01:37 UTC**, on Windows or macOS. Check with `git log --all --oneline | grep -E '7895c547|55d306d5'` in your clone; if `7895c547` is in your history and you installed while it was `HEAD`, assume execution.
- Persistence check — **any of these present is a confirmed compromise signal**: the `SysHelper` Run value or `%LOCALAPPDATA%\WindowsHelper\sys.pyw` on Windows; `~/Library/LaunchAgents/com.user.syshelper.plist` or `~/Library/Application Support/HowToFind/` on macOS; a `pythonw`/`python` process with that script path.
- Any project whose requirements were rewritten to `git+https://github.com/pypls/…` sources.

## If you are affected

1. Remove the persistence entries and payload files above, then **verify every crypto transaction made from that machine since 09-08** — the hijacker's effect is a silently altered destination address. → [playbooks/if-you-ran-malicious-postinstall.md](../playbooks/if-you-ran-malicious-postinstall.md) applies (build-time execution is the pip equivalent).
2. The payload analysed does not steal credentials, but the maintainer's account was compromised by someone with unknown further access; if you also hold write access to the project or shared a machine with it, rotate → [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md).
3. Reinstall from a checkout at or after `55d306d5`, and diff `requirements.txt` against the previous release before every future install of any AI repo.

## Prevention

- **Treat a requirements-file change that swaps PyPI names for Git URLs as a security event**, and review it like a new dependency: who owns the repo, when was it created, does `setup.py` contain anything before `setup()`? → [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md).
- **Pin Git-sourced dependencies to a commit hash**, never a branch — and prefer the PyPI release with `--require-hashes`.
- **Install untrusted AI repos in a sandbox** (container or VM) rather than on the host that holds your wallets and keys → [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md).
- Maintainers: the account had 2FA and was still taken over — audit OAuth app grants and active sessions after a compromise, not only the password; → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md) for protected branches and required reviews on `main`.

## Sources
- [SafeDep — Deep-Live-Cam Supply Chain Attack: Technical Analysis](https://safedep.io/deep-live-cam-supply-chain-attack/) — primary, 2026-09-09: the UTC timeline, both commit hashes, the 18 rewritten entries, the `pypls/requests` impersonation, the four-stage loader and its platform gating, the persistence paths, the clipboard-classifier behaviour, the no-infection-count caveat. Fetched 2026-09-26.
- [hacksider/Deep-Live-Cam — issue #1930, "Supply chain attack – requirements.txt compromised"](https://github.com/hacksider/Deep-Live-Cam/issues/1930) — the reporter's record (fred-cardoso, 2026-09-09), naming commit `7895c54` and the malicious `setup.py`; the project's only public record of the incident (issue now closed). Fetched 2026-09-26.
- [The Hacker News — ThreatsDay: AI Search Poisoning, AI Coding Tool Leaking Repos, One-Click Code Execution and 13 More Stories](https://thehackernews.com/2026/09/threatsday-ai-search-poisoning-ai.html) — 2026-09-25 roundup item ("Deep-Live-Cam (96.6K GitHub stars): malicious dependency added Sept 8 with cryptocurrency clipboard hijacker"); restates SafeDep. Fetched 2026-09-26.
- The paste-page payload URL, hit-counter endpoint and attacker e-mail are in the SafeDep report and deliberately not reproduced here; the `pypls/requests` repository is named as an indicator and not linked.
- Related in this corpus: [Mini Shai-Hulud / TanStack](2026-05-tanstack-mini-shai-hulud.md) (mutable refs as the persistence mechanism), [MemTensor sckit](2026-09-memtensor-memos-openclaw-plugin-sckit-worm.md) (stolen maintainer credentials → poisoned AI-tool release).
