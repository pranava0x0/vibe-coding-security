---
id: 2026-06-miasma-leoplatform-go-wave
title: "Miasma LeoPlatform + Go ecosystem wave — 20 npm packages + Go module + GitHub Actions compromise (June 24 2026)"
date_disclosed: 2026-06-24
last_updated: 2026-06-26
severity: critical
status: active
ecosystems: [npm, go, github-actions]
tools_affected: [leo-sdk, leo-aws, leo-cli, leo-auth, rstreams-metrics, serverless-leo, claude-code, cursor, codfish-semantic-release-action]
tags: [supply-chain, credential-theft, phantom-gyp, binding-gyp, miasma, shai-hulud-lineage, ci-cd, github-actions, go, npm-worm]
---

## TL;DR

On **2026-06-24 at 23:04:55 UTC**, a compromised npm maintainer account (`czirker`) published **20 malicious versions** of LeoPlatform / RStreams npm packages in a **3-second burst**, using the Phantom Gyp (`binding.gyp`) install-time execution primitive that bypasses `--ignore-scripts`. The same campaign simultaneously force-pushed a poisoned commit to **codfish/semantic-release-action** on GitHub (affecting **1,442 dependent repositories**) and compromised a **Go module** (`github.com/verana-labs/verana-blockchain`). This is the most recent documented wave of the Miasma / Mini Shai-Hulud supply-chain worm lineage.

## What happened

At **23:04:55 – 23:04:58 UTC on June 24, 2026**, an attacker using a stolen npm token for the `czirker` account published malicious versions of 20 LeoPlatform and RStreams npm packages within a **3-second burst** — a pattern consistent with automated release tooling.

**Affected npm packages (20 total):**

`leo-logger`, `leo-sdk`, `leo-aws`, `leo-config`, `leo-streams`, `serverless-leo`, `leo-connector-mongo`, `serverless-convention`, `rstreams-metrics`, `leo-connector-elasticsearch`, `leo-auth`, `leo-cache`, `leo-cli`, `leo-cron`, `leo-connector-redshift`, `leo-connector-oracle`, `rstreams-shard-util`, `leo-connector-mysql`, `leo-cdk-lib`, `solo-nav`

In addition, `hexo-deployer-wrangler`, `hexo-shoka-swiper`, and `prism-silq` were also compromised in the same wave.

### Attack mechanism: Phantom Gyp (binding.gyp)

The malicious packages add a `binding.gyp` file that triggers `node-gyp build` during `npm install`, executing attacker-controlled C/JS code **even when `--ignore-scripts` is set**. The payload uses three-layer obfuscation:

1. **ROT-N cipher** (letter-shift obfuscation)
2. **AES-128-GCM decryption** (key embedded in the payload)
3. **obfuscator.io** runtime obfuscation

The inner payload is a Bun-staged credential harvester that:
- Downloads **Bun v1.3.13** from GitHub releases to `/tmp/p*.js`
- Reads Runner process memory via `/proc/{pid}/mem` to steal in-memory CI/CD secrets
- Harvests: GitHub tokens, npm tokens, AWS/GCP/Azure credentials, SSH keys, HashiCorp Vault tokens, 1Password vault data, Docker configs
- Exfiltrates credentials using the victim's **own GitHub token** (to avoid external egress detection)
- Injects persistence hooks into AI coding assistant config (`.claude/`, `.vscode/`)

### GitHub Actions compromise

At **15:39:06 UTC on June 24**, the attacker force-pushed malicious commits to **`codfish/semantic-release-action`**, injecting a "Run Copilot" workflow that captures CI/CD environment secrets from runner memory. This GitHub Action is used by **1,442 repositories** — any workflow using this action during the compromise window ran the malicious payload with access to that repo's `GITHUB_TOKEN` and stored secrets.

### Go module compromise

**`github.com/verana-labs/verana-blockchain@v0.10.1-dev.20`** was poisoned in the same campaign. The Go security team was notified and acted quickly after disclosure.

### Campaign markers (IOCs)

| Marker | Location |
|---|---|
| `"Alright Lets See If This Works"` | GitHub dead-drop description |
| `"RevokeAndItGoesKaboom"` | Token relay function name |
| `"TheBeautifulSandsOfTime"` | Internal campaign string |
| `"firedalazer"` | GitHub polling commit marker |

The malware polls GitHub hourly for commits matching the string `"firedalazer"`. **559 repositories** were found containing the dead-drop marker at time of disclosure.

**Killswitch:** Russian locale (`LANG=ru_RU`) causes the payload to exit early without executing. Endpoint security software checks are also present.

### Lineage

This is part of the **Miasma / Mini Shai-Hulud** worm family: the `binding.gyp` Phantom Gyp vector was established by [Wave 4 (June 3)](2026-06-phantom-gyp-miasma-wave4.md) which hit @vapi-ai/server-sdk and 56 other packages. The LeoPlatform wave adds cross-ecosystem spread (npm → Go → GitHub Actions) and use of a compromised legitimate maintainer token rather than a newly registered attacker account. Cross-link: [Miasma Wave 5 (June 5)](2026-06-miasma-wave5-microsoft-azure-github.md) for the prior source-repo poisoning pattern.

## Am I affected?

**Check your npm lockfile and installed packages:**

```bash
# Check if any LeoPlatform/RStreams packages are installed
npm ls | grep -E "leo-sdk|leo-aws|leo-cli|leo-auth|leo-cron|leo-config|leo-logger|leo-cache|leo-streams|leo-connector|rstreams|serverless-leo|leo-cdk-lib|solo-nav|hexo-deployer-wrangler|hexo-shoka-swiper|prism-silq"

# Or in package-lock.json
grep -E '"leo-sdk"|"leo-aws"|"leo-cli"|"leo-auth"|"rstreams-metrics"|"serverless-leo"' package-lock.json

# Check for Phantom Gyp IOC in node_modules
find node_modules -name "binding.gyp" 2>/dev/null | while read f; do
  dir=$(dirname $f)
  echo "FOUND: $f (pkg: $(node -e "try{let p=require('$dir/package.json');console.log(p.name+'@'+p.version)}catch(e){console.log('unknown')}"))"
done
```

**Check for the campaign dead-drop marker:**

```bash
# If you have GitHub API access, search your org's repos
gh api search/repositories -f q="firedalazer in:description" --jq '.items[].full_name'

# Check for AI coding tool config hooks (Miasma persistence)
grep -rE "firedalazer|RevokeAndItGoesKaboom|TheBeautifulSandsOfTime|Alright Lets See If This Works" .claude/ .vscode/ .cursor/ CLAUDE.md GEMINI.md 2>/dev/null
```

**GitHub Actions exposure:**

If your CI uses `codfish/semantic-release-action`, check whether any workflow ran between **2026-06-24 15:39:06 UTC** and the time the compromised version was removed. The `GITHUB_TOKEN` and any secrets in scope of that workflow should be treated as compromised.

```bash
# Check your repo's workflow files
grep -r "codfish/semantic-release-action" .github/workflows/
```

**Go module check:**

```bash
grep "verana-labs/verana-blockchain" go.sum go.mod
```

## If you are affected

- **npm packages:** [If you installed a bad npm package](../playbooks/if-you-installed-a-bad-npm-package.md)
- **npm token stolen:** [If your npm token leaked](../playbooks/if-your-npm-token-leaked.md)
- **GitHub token stolen:** [If your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md)
- **Cloud credentials exposed:** [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md)

If the `binding.gyp` payload ran during `npm install`, treat all credentials in scope of that environment as compromised — the payload specifically targets CI/CD runner memory for in-flight secrets.

## Prevention

- **[npm hardening](../prevention/npm-hardening.md)** — including `allow-scripts=false` in `.npmrc` (npm ≥ 11.16.0) which blocks BOTH lifecycle scripts AND `binding.gyp`-triggered builds (unlike `--ignore-scripts` which only blocks the former).
- **[CI/CD hardening](../prevention/ci-cd-hardening.md)** — pin GitHub Actions to a specific commit SHA rather than a floating tag (`uses: codfish/semantic-release-action@v3` → `uses: codfish/semantic-release-action@<SHA>`).
- **[Supply-chain attack surface](../prevention/supply-chain-attack-surface.md)** — audit for `binding.gyp` files in unfamiliar npm packages.

## Sources

- [Miasma Mini Shai-Hulud Hits LeoPlatform npm Packages and Go Ecosystem](https://socket.dev/blog/miasma-mini-shai-hulud-hits-leoplatform-npm-packages-go-ecosystem) — Socket Threat Research, June 25 2026. Primary technical analysis, IOCs, package list, timeline.
- [Mass npm Supply Chain Attack: 20 Leo Platform Packages Compromised](https://www.stepsecurity.io/blog/mass-npm-supply-chain-attack-20-leo-platform-packages-compromised) — StepSecurity, June 24 2026. First disclosure, package list, attack timeline.
- [Miasma Malware Targets npm Packages and GitHub Actions in Supply Chain Attack](https://thehackernews.com/2026/06/miasma-malware-targets-npm-packages-and.html) — The Hacker News, June 25 2026. Summary coverage including GitHub Actions and Go module impact.
