---
id: 2026-06-gluestack-react-native-aria-rat
title: "Gluestack @react-native-aria RAT via compromised contributor token (June 2026)"
date_disclosed: 2026-06-06
last_updated: 2026-06-04
severity: critical
status: contained
ecosystems: [npm, react-native]
tools_affected: [React Native, Gluestack UI, Expo, any mobile/web project using @react-native-aria/*]
tags: [supply-chain, rat, credential-theft, compromised-token]
---

## TL;DR

A compromised npm contributor token let attackers publish 17 of the 20 **`@react-native-aria`** packages plus **`@gluestack-ui/utils`** (~960K weekly downloads) with a hidden **Remote Access Trojan (RAT)** starting June 6, 2026. Packages have been deprecated; roll back immediately and assume your dev machine is compromised if you `npm install`-ed any of these after June 6.

## What happened

On **2026-06-06 at ~21:33 UTC** a threat actor used a compromised npm access token belonging to a Gluestack-UI contributor to publish tampered versions of the `@react-native-aria` ecosystem (17 of 20 packages) and `@gluestack-ui/utils`.

The malicious payload is an obfuscated RAT that:
- Connects to an attacker-controlled C2
- Supports commands including `ss_info` (harvest full system information) and `ss_ip` (exfiltrate public IP address of the host)
- Persists on the developer's machine

Initial detection came from **Aikido Security** monitoring anomalous publish activity. Gluestack revoked the compromised token within hours and deprecated all malicious versions on npm.

The technique — compromised publisher credential → poisoned version → RAT payload — is the same playbook as [Bitwarden CLI (April 2026)](2026-04-bitwarden-cli-shai-hulud-third-coming.md) and [Nx Console (May 2026)](2026-05-nx-console-vscode-compromise.md). Note the specific targeting of React Native / Expo / mobile stacks (distinct from the web-framework targeting of prior waves).

## Am I affected?

Check whether any of the following packages are in your `node_modules`, `package-lock.json`, or `yarn.lock` at versions published on **2026-06-06 or later**:

```bash
# Quick lockfile grep for the affected scope
grep -E '"@react-native-aria/|@gluestack-ui/utils"' package-lock.json

# Check installed version dates via npm
npm view @react-native-aria/focus time --json | tail -5
npm view @gluestack-ui/utils time --json | tail -5
```

Affected packages include (but are not limited to):
- `@react-native-aria/focus`
- `@react-native-aria/overlays`
- `@react-native-aria/button`
- `@react-native-aria/checkbox`
- `@react-native-aria/radio`
- `@react-native-aria/slider`
- `@react-native-aria/switch`
- `@react-native-aria/tabs`
- `@react-native-aria/tooltip`
- `@react-native-aria/listbox`
- `@react-native-aria/combobox`
- `@react-native-aria/menu`
- `@react-native-aria/dialog`
- `@react-native-aria/selection`
- `@react-native-aria/interactions`
- `@react-native-aria/utils`
- `@react-native-aria/visually-hidden`
- `@gluestack-ui/utils`

Safe versions are those published **before 2026-06-06** or the most recent non-deprecated releases after Gluestack re-published clean versions.

## If you are affected

1. **Roll back** to the last clean version (before 2026-06-06) immediately.
2. **Rotate all credentials** accessible from the affected machine: cloud API keys (AWS/GCP/Azure), GitHub/npm tokens, SSH keys, browser-stored passwords, `.env` files.
3. **Assume full system compromise** — the RAT provides interactive C2 access.
4. See [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md).

## Prevention

- Pin dependency versions to exact SHAs in lockfiles and verify on CI.
- Enable npm audit / Snyk / Socket.dev in your CI pipeline to catch anomalous new versions.
- Use `npm install --ignore-scripts` for packages where lifecycle hooks are not needed.
- Monitor for abnormal outbound connections from your development machine during `npm install`.

## Sources

- [Aikido Security — "Active NPM Attack Escalates: 16 React Native Packages for GlueStack Backdoored Overnight"](https://www.aikido.dev/blog/supply-chain-attack-on-react-native-aria-ecosystem) — canonical detection report, timeline, payload analysis.
- [SecurityWeek — "React Native Aria Packages Backdoored in Supply Chain Attack"](https://www.securityweek.com/react-native-aria-packages-backdoored-in-supply-chain-attack/) — scope confirmation, attack mechanism.
- [BleepingComputer — "Malware found in NPM packages with 1 million weekly downloads"](https://www.bleepingcomputer.com/news/security/supply-chain-attack-hits-gluestack-npm-packages-with-960k-weekly-downloads/) — download counts, mitigation.
- [Snyk SNYK-JS-GLUESTACKUIUTILS-10336056](https://security.snyk.io/vuln/SNYK-JS-GLUESTACKUIUTILS-10336056) — per-package vulnerability data.
- [Snyk SNYK-JS-REACTNATIVEARIAOVERLAYS-10335834](https://security.snyk.io/vuln/SNYK-JS-REACTNATIVEARIAOVERLAYS-10335834) — per-package vulnerability data.
