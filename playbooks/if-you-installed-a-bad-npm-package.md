# If you installed a bad npm package

> Scope: any npm package — direct or transitive — that turned out to be compromised.

## Authoritative reference playbooks

Before this one, read whichever applies:

- **[Snyk — NPM Security Best Practices After the Shai-Hulud Attack](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/)** — incident-response checklist tuned for 2025–2026 worms.
- **[Microsoft Security — Shai-Hulud 2.0 Guidance](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/)** — detect, investigate, defend.
- **[StepSecurity — Active Supply Chain Attack: Malicious node-ipc](https://www.stepsecurity.io/blog/node-ipc-npm-supply-chain-attack)** — recent example with IOCs.
- **[CISA — Defending Against Software Supply Chain Attacks](https://www.cisa.gov/resources-tools/resources/defending-against-software-supply-chain-attacks)** — framework-level.

## Do this first (60 seconds)

```bash
# 1. Disconnect from the internet if you can (Wi-Fi off / VPN kill switch).
#    This stops live exfiltration mid-flight.

# 2. Kill node processes that might still be exfiltrating.
pkill -9 node
pkill -9 npm
pkill -9 bun
pkill -9 yarn
pkill -9 pnpm
```

Now reconnect. The damage is mostly done at install-time; what matters next is rotation.

## Triage

### What got run?

The dangerous moment is `postinstall` execution. If you installed with `--ignore-scripts`, you're probably fine — just remove and reinstall clean.

```bash
# Confirm whether ignore-scripts was set
cat ~/.npmrc | grep ignore-scripts
cat .npmrc 2>/dev/null | grep ignore-scripts
```

### Identify the bad package + version

```bash
# All copies in your tree (direct + transitive)
npm ls <bad-package> --all

# Or dump the lockfile
grep -B1 -A3 '"<bad-package>"' package-lock.json
```

### Identify when it ran

```bash
ls -la node_modules/<bad-package>/package.json
# stat times tell you when the bad version landed
```

## Rotate (in priority order)

Assume **everything readable from your user account was exfiltrated**. Rotate in this order — top items have the shortest exploitation window.

1. **npm token.** → [if-your-npm-token-leaked.md](if-your-npm-token-leaked.md)
2. **GitHub PAT.** → [if-your-github-pat-leaked.md](if-your-github-pat-leaked.md)
3. **Cloud credentials** (AWS, GCP, Azure, Kubernetes). → [rotating-cloud-credentials.md](rotating-cloud-credentials.md)
4. **SSH keys.** Generate new `~/.ssh/id_ed25519`, replace public keys in GitHub/GitLab/servers, revoke old key everywhere it was authorized.
5. **AI API keys.** Anthropic, OpenAI, Google AI, OpenRouter, Replicate. Rotate via each vendor's console.
6. **Browser cookies / saved passwords.** If the malware ran as your user, it could have read Chrome/Firefox storage. Sign out of high-value services (banking, email, GitHub, AWS) and force-revoke active sessions.
7. **Crypto wallets.** If you have hot wallets (MetaMask, etc.) on this machine, move funds **from a different device** to a fresh wallet. Don't trust the compromised machine.

## Clean

```bash
# Nuke the dependency tree
rm -rf node_modules package-lock.json yarn.lock pnpm-lock.yaml

# Reinstall with scripts disabled, then verify the bad package is gone
npm install --ignore-scripts
npm ls <bad-package>
```

If the bad version is still pulled in transitively, pin a known-good in `overrides` (npm) / `resolutions` (yarn/pnpm):

```json
// package.json
"overrides": {
  "<bad-package>": "<known-good-version>"
}
```

## Verify — look for known worm signatures

```bash
# Shai-Hulud 2.0 bun-based execution
find ~ -name "setup_bun.js" -o -name "bun_environment.js" 2>/dev/null

# node-ipc forensic markers (May 2026)
find ~/.npm ~/.cache -name "node-ipc-*.tgz" -exec sh -c \
  'tar -tvf "$1" 2>/dev/null | grep "1985"' _ {} \;
ps eww | grep "__ntw=1"
ls -la "${TMPDIR:-/tmp}"/nt-* 2>/dev/null

# Check GitHub for planted public repos (Shai-Hulud signature)
gh api /user/repos --paginate --jq '.[] | select(.created_at > "DATE_OF_INSTALL" or (.name | test("Shai-Hulud"; "i"))) | .full_name'

# Check npm for packages you didn't publish
npm whoami
npm access list packages
```

If you find traces — **assume full machine compromise**. Reimage the dev machine, don't just rotate secrets.

## Detection signals to monitor for the next 7 days

Per [Microsoft's Shai-Hulud 2.0 guidance](https://www.microsoft.com/en-us/security/blog/2025/12/09/shai-hulud-2-0-guidance-for-detecting-investigating-and-defending-against-the-supply-chain-attack/):

- Outbound DNS to unusual domains (the [node-ipc payload uses DNS exfil](../advisories/2026-05-node-ipc-compromise.md)).
- New public repos in your GitHub account.
- New SSH keys / deploy keys in your account.
- Unexpected commits / pushes to your repos.
- Cloud billing anomalies (compute spikes from unfamiliar regions).
- npm 2FA challenge prompts you didn't initiate.

## Document

Add to your team's `issues.md`:

- date, package, version, install timestamp
- which secrets were on disk
- what you rotated (with timestamps)
- whether you reimaged

You'll want this when the auditor / your CTO / your customers ask.

## Prevention going forward

- [prevention/npm-hardening.md](../prevention/npm-hardening.md) — `--ignore-scripts`, exact pins, release cooldown, `npm ci`, trusted publishing.
- [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — install inside a devcontainer.
