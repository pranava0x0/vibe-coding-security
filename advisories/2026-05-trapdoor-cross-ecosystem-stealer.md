---
id: 2026-05-trapdoor-cross-ecosystem-stealer
title: "TrapDoor — cross-ecosystem stealer poisons .cursorrules / CLAUDE.md (May 2026)"
date_disclosed: 2026-05-22
last_updated: 2026-05-25
severity: critical
status: active
ecosystems: [npm, pypi, crates, cursor, claude-code]
tools_affected: [any-node-project, any-python-project, any-rust-project, cursor, claude-code, codex]
tags: [supply-chain, credential-theft, prompt-injection, crypto-stealer, zero-width-unicode, cursorrules, npm, pypi, crates]
---

## TL;DR
**TrapDoor** is an active, coordinated supply-chain campaign that pushed **34+ malicious packages across 384+ versions** to **npm, PyPI, and Crates.io** at once (first activity 2026-05-22 20:20 UTC), impersonating crypto/DeFi/AI/security developer tooling. Beyond the usual wallet- and credential-stealing payload, its defining trick is **vibe-coding-specific**: it rewrites your repo's **`.cursorrules` and `CLAUDE.md`** with **zero-width Unicode** to hide a prompt-injection instruction, so your *own* AI coding agent exfiltrates secrets on its next run under the guise of "running an automated project security scan."

## What happened
Socket flagged TrapDoor on 2026-05-24/25 as a single actor publishing in **timed waves from a cluster of accounts** across three registries simultaneously. The packages use deceptive, community-adjacent names to feign legitimacy — observed examples include **`prompt-engineering-toolkit`**, **`solidity-deploy-guard`**, and **`defi-threat-scanner`** — and target developers in the **crypto, DeFi, Solana/Sui/Aptos, and AI** communities.

Each ecosystem gets a tailored execution path:
- **npm** — a `postinstall` hook runs a shared payload **`trap-core.js`** (a ~1,149-line credential harvester). It scans for secrets and **validates stolen AWS and GitHub tokens with live API calls** to confirm they're still active before exfiltrating, then attempts lateral movement + persistence.
- **PyPI** — the payload **auto-executes on import** (no build step needed).
- **Crates.io (Rust)** — a **`build.rs`** build script searches for local keystores, **XOR-encrypts the loot with a hardcoded key**, and exfiltrates it to **GitHub Gists**.

**The vibe-coding angle (the reason this is in scope):** TrapDoor deliberately targets AI coding assistants by modifying **`.cursorrules`** and **`CLAUDE.md`** project files, using **zero-width Unicode characters** to obscure a malicious prompt inside otherwise-normal-looking instructions. The hidden prompt tricks the agent into performing credential exfiltration framed as a benign "automated project security scan." This combines the steganographic-Unicode technique seen in [GlassWorm](2025-10-glassworm-vscode-worm.md) with **AI-agent-config files as a persistence + re-infection surface** — the package poisons the repo once, and the developer's own agent re-runs the attack thereafter. It's the inverse of prior incidents that merely *read* AI-tool config (cf. [Bitwarden CLI](2026-04-bitwarden-cli-shai-hulud-third-coming.md) and the [Nx Console](2026-05-nx-console-vscode-compromise.md) `~/.claude/settings.json` theft): here the attacker *writes* instructions into the files your agent trusts.

**Attribution / markers:** Socket ties the operation to the GitHub account **`ddjidd564`**, the domain **`ddjidd564.github.io`**, and the campaign marker string **`P-2024-001`**. No link to TeamPCP/Shai-Hulud has been established — treat it as a distinct actor.

**Stolen data:** wallet seeds / keystores (Solana, Sui, Aptos), SSH keys, AWS credentials, GitHub tokens, browser profile/login databases, crypto-wallet extension data, environment variables, API keys, and local dev configuration files.

## Am I affected?

```bash
# 1. Did any TrapDoor-named package land in your tree? (names seen so far)
npm ls prompt-engineering-toolkit solidity-deploy-guard defi-threat-scanner --all 2>/dev/null
pip show prompt-engineering-toolkit solidity-deploy-guard defi-threat-scanner 2>/dev/null
grep -REn "prompt-engineering-toolkit|solidity-deploy-guard|defi-threat-scanner|trap-core" \
  package-lock.json yarn.lock pnpm-lock.yaml requirements*.txt poetry.lock Cargo.lock 2>/dev/null

# 2. Campaign infrastructure / markers
grep -REn "ddjidd564|P-2024-001|trap-core\.js" . 2>/dev/null

# 3. THE IMPORTANT ONE — was your AI-agent config silently rewritten?
# Flag zero-width / invisible Unicode in agent instruction files (the persistence vector):
for f in .cursorrules CLAUDE.md AGENTS.md .github/copilot-instructions.md .windsurfrules; do
  [ -f "$f" ] && grep -nP '[\x{200B}-\x{200F}\x{202A}-\x{202E}\x{2060}-\x{206F}\x{FEFF}\x{E0000}-\x{E007F}]' "$f" \
    && echo "  ^ invisible Unicode in $f — INSPECT"
done

# 4. Rust crates: build.rs that reaches for keystores / gists
grep -REn "build\.rs" Cargo.toml 2>/dev/null && grep -REn "gist|keystore|XOR" build.rs 2>/dev/null
```

If `.cursorrules`/`CLAUDE.md` contains hidden Unicode you didn't write, **assume any credential your agent could reach was exfiltrated** — including tokens validated live by `trap-core.js`.

## If you are affected
1. Remove the package, delete `node_modules` / venv / `target`, and reinstall from a clean lockfile.
2. **Restore your AI-agent config files from a known-good commit** and re-scan them for invisible Unicode before letting any agent run again.
3. Rotate everything: crypto wallets/seeds, SSH keys, AWS + GitHub tokens (the npm payload live-validates AWS/GitHub creds, so assume they're known-good to the attacker), browser-stored logins, API keys.

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — disable install scripts, pin versions, watch typosquats of crypto/AI tooling names
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
- **Treat `.cursorrules` / `CLAUDE.md` / `AGENTS.md` as security-sensitive code.** Diff them on every dependency change, keep them in version control, and grep for zero-width/bidi code points — your agent obeys whatever they contain.

## Sources
- [Socket — TrapDoor Crypto Stealer Supply Chain Attack Hits 34 Packages Across npm, PyPI, and Crates](https://socket.dev/blog/trapdoor-crypto-stealer-npm-pypi-crates) — canonical research, package names, `trap-core.js`, ddjidd564 / P-2024-001 markers, `.cursorrules`/`CLAUDE.md` abuse.
- [The Hacker News — TrapDoor Supply Chain Attack Spreads Credential-Stealing Malware via npm, PyPI, and CratesIO](https://thehackernews.com/2026/05/trapdoor-supply-chain-attack-spreads.html) — timeline, ecosystem-specific execution paths.
- [CyberSecurityNews — Hackers Compromised 34 Packages in npm, PyPI, and Crates in New Supply Chain Attack](https://cybersecuritynews.com/supply-chain-trapdoor-malware/) — IOCs, data-theft list.
- [GBHackers — Hackers Compromise 34 npm, PyPI, and Crates Packages in Major Supply Chain Attack](https://gbhackers.com/hackers-compromise-34-npm-pypi-and-crates-packages/) — corroborating details.
- [The Block — Researchers flag TrapDoor malware campaign targeting crypto developer environments (Aptos, Sui, Solana)](https://www.theblock.co/post/402458/researchers-flag-trapdoor-malware-campaign-targeting-crypto-developer-environments-including-aptos-sui-and-solana) — crypto-ecosystem targeting.
- [The Crypto Times — TrapDoor Malware Hits npm, PyPI & Crates.io, Steals Crypto Wallets & SSH Keys](https://www.cryptotimes.io/2026/05/25/trapdoor-malware-hits-npm-pypi-crates-io-steals-crypto-wallets-ssh-keys/) — Rust `build.rs` XOR→Gist exfil.
- [Cyber Kendra — Malicious Packages on npm, PyPI, and Crates.io Steal Crypto Wallets, SSH Keys, and Cloud Credentials](https://www.cyberkendra.com/2026/05/malicious-packages-on-npm-pypi-and.html) — corroborating IOCs.
