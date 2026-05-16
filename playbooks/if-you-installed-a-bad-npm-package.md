# If you installed a bad npm package

> Scope: any npm package — direct or transitive — that turned out to be compromised.

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
The dangerous moment is `postinstall` execution. If you installed the package with `--ignore-scripts`, you're probably fine — just remove and reinstall clean.

```bash
# Confirm whether ignore-scripts was set
cat ~/.npmrc | grep ignore-scripts
cat .npmrc 2>/dev/null | grep ignore-scripts
```

### Identify the bad package + version

```bash
# All copies in your tree (direct + transitive)
npm ls <bad-package> --all

# Or for the whole tree, dump the lockfile
cat package-lock.json | grep -B1 -A3 '"resolved"' | grep <bad-package>
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

If the bad version is still being pulled in transitively, pin a known-good version in `overrides` (npm) / `resolutions` (yarn/pnpm):

```json
// package.json
"overrides": {
  "<bad-package>": "<known-good-version>"
}
```

## Verify

```bash
# Search the home dir for new unexpected files / signatures of known worms
find ~ -name "setup_bun.js" -o -name "bun_environment.js" 2>/dev/null
find ~/.npm -newer /tmp/timestamp_pre_install -type f 2>/dev/null

# Check GitHub for planted public repos
gh api /user/repos --paginate --jq '.[] | select(.created_at > "DATE_OF_INSTALL") | .full_name'

# Check npm for packages you didn't publish
npm whoami
npm access list packages
```

If you find traces — assume full machine compromise. Consider reimaging the dev machine, not just rotating secrets.

## Document

Add an entry to your team's `issues.md`:
- date, package, version, install timestamp
- which secrets were on disk
- what you rotated (with timestamps)
- whether you reimaged

You'll want this when the auditor / your CTO / your customers ask.
