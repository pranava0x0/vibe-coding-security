---
id: 2026-11-ethersphere-bee-js-13-3-0-and-swarm-desktop-0-56-2-compromised-releases-remove-and-rotate
title: "Compromised @ethersphere/bee-js 13.3.0 and Swarm Desktop 0.56.2: remove, use 13.2.0 and 0.56.3, rotate keys"
kind: malicious-artifact
date_disclosed: 2026-11-09
last_updated: 2026-11-10
severity: high
status: contained
ecosystems: [npm, github-releases, desktop-app, ci-cd]
tools_affected: ["@ethersphere/bee-js 13.3.0 (npm)", "Swarm Desktop 0.56.2 (GitHub release; Windows x64 and Apple Silicon auto-update)", "projects that resolved bee-js through @ethersphere/swarm-cli, @ethersphere/bee-dashboard, @snaha/swarm-id, @solarpunkltd/file-manager-lib, bee-wasm-js or create-swarm-app between 00:09 and 01:25 UTC on 2026-11-09", "CI jobs and developer machines that installed 13.3.0 with install scripts enabled"]
tags: [supply-chain, malicious-package, compromised-release, npm, stolen-ci-credentials, postinstall, desktop-app, auto-update]
---

## TL;DR
Remove `@ethersphere/bee-js` 13.3.0 and Swarm Desktop 0.56.2, and use bee-js 13.2.0 and Swarm Desktop 0.56.3. If either ran, rotate every credential that user or CI job could read, and move Swarm node funds to a new key from a clean machine.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| npm | `@ethersphere/bee-js` | 13.3.0 (published 2026-11-09 00:09:50 UTC, removed about 01:25 UTC) | pin 13.2.0 | 13.3.0 not in the version list, `latest` is 13.2.0 (2026-11-10) | GHSA-hh7j-5m3j-23pf, MAL-2026-18773 |
| GitHub release | Swarm Desktop | 0.56.2 (appeared about 00:36 UTC on 2026-11-09, tag deleted 09:04 UTC) | install 0.56.3 | 0.56.3 marked Latest, dated 09 Nov 12:52 (2026-11-10) | maintainer pull request #582 |
| npm (dependents) | `@ethersphere/swarm-cli` 3.6.0 and 3.7.0, `@ethersphere/bee-dashboard` 0.37.0 and 0.37.1, `@snaha/swarm-id` 0.5.0 to 0.8.0, `@solarpunkltd/file-manager-lib` 1.1.0 and 1.1.1, `bee-wasm-js` 0.1.0 and 0.1.1 | not malicious themselves; their ranges accepted 13.3.0 during the window | reinstall with bee-js pinned to 13.2.0 | per Socket (2026-11-09); not checked on the registry by this sweep | none |

Notes on the table. The npm `time` field still lists 13.3.0 at 2026-11-09 00:09:50 UTC, which is the publish time of a version the registry no longer serves. The `upcoming` dist-tag points at `13.3.0-upcoming.g4568f7a`, a pre-release published 2026-10-27 that no source names as affected. Socket counts 3,741 downloads of bee-js between 2026-11-01 and 2026-11-08. The Hacker News puts downloads of 13.3.0 itself at about ten. Socket says the 0.56.2 installer counters reached 65 by 08:27 UTC and that the figure is an upper bound that includes researchers. The maintainer's pull request says 0.56.2 "was published by an attacker using stolen CI credentials and has been withdrawn". How the credentials were obtained is not stated.

## Am I affected?

1. **Lockfiles.** `grep -rn "bee-js" package-lock.json pnpm-lock.yaml yarn.lock | grep "13.3.0"`. Check transitive copies, internal registry mirrors and CI caches as well.
2. **Installed tree.** `npm ls @ethersphere/bee-js`. Any 13.3.0 is the bad version.
3. **CI logs.** Search for installs between 00:09 and 01:25 UTC on 2026-11-09 that resolved bee-js. The package used an install-time script, so an install with scripts enabled counts as a run even if the build failed later.
4. **Swarm Desktop.** Look for the version string 0.56.2 in `bee-desktop.log`: `~/Library/Logs/Swarm Desktop/` on macOS, `%LOCALAPPDATA%\Swarm Desktop\Log\` on Windows, `~/.local/state/Swarm Desktop/` on Linux. Windows x64 and Apple Silicon installs could have received it through auto-update. Intel Macs were not offered it. Linux packages do not auto-update.
5. **Files left behind.** A `~/.solidity/` folder; a user systemd unit named `solidity-langsupport-runner.service` on Linux; a LaunchAgent named `com.solidity.langsupport.runner` on macOS; on Windows, a service whose name begins `ScreenConnect Client` that you did not install, and `.stuffed-*` files in the temp directory. Any of these on a machine that never ran Solidity tooling from you is a confirmed sign the artifact ran.

## If you are affected

- Pin bee-js to 13.2.0, clear npm caches and mirrors, and reinstall. Install Swarm Desktop 0.56.3 and confirm the version afterwards. On Linux replace the package by hand.
- Removing the package or the app does not remove the files in step 5. The GitHub advisory says any computer that had the package installed or running "should be considered fully compromised". Rebuild from a trusted image where you can. [If you ran a malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md) has the order of work.
- Rotate, from a different machine: npm and GitHub tokens, cloud credentials (including ones a CI job could obtain through OIDC trust), SSH keys, and anything else readable by the user or job. [Rotating cloud credentials](../playbooks/rotating-cloud-credentials.md) covers providers.
- For Swarm Desktop 0.56.2: treat the node wallet key and its stored password as taken. From a clean machine, move funds, chequebook balance and stake to a new key.

## Prevention

- Install with lifecycle scripts off by default and allow them per package: [npm hardening](../prevention/npm-hardening.md).
- Do not let CI resolve `latest` or a caret range for a dependency at release time. Commit the lockfile and use `npm ci`: [CI/CD hardening](../prevention/ci-cd-hardening.md).
- For maintainers, the changes Ethersphere made are the lesson: signing jobs restricted to the main branch and gated on reviewer approval, so a stolen CI credential cannot publish from an arbitrary branch.
- A desktop app's auto-updater is a second install channel. Delay automatic updates on machines that hold keys, the same way a registry cooldown delays packages.

## Sources

- [Socket: bee-js compromise](https://socket.dev/blog/bee-js-compromise), fetched 2026-11-10: published 2026-11-09; versions, publish and removal times, the auto-update platforms, the dependent packages and ranges, download figures, files left on disk, remediation. Written before 0.56.3 existed.
- [SafeDep: Compromised bee-js and Swarm Desktop](https://safedep.io/blog/ethersphere-bee-js-npm-compromise), fetched 2026-11-10: published 2026-11-09; the same versions and times, the install-time script, files left on disk, the wallet-key advice. A second firm's own analysis.
- [StepSecurity: @ethersphere/bee-js 13.3.0 Compromised](https://www.stepsecurity.io/blog/ethersphere-bee-js-13-3-0-compromise), fetched 2026-11-10: publish time, 13.2.0 examined as clean, the file locations per platform, remediation. A third firm.
- [GitHub Advisory Database: GHSA-hh7j-5m3j-23pf](https://github.com/advisories/GHSA-hh7j-5m3j-23pf), fetched 2026-11-10: "Malware in @ethersphere/bee-js", affected `= 13.3.0`, no patched version, the "fully compromised" sentence.
- OSV `MAL-2026-18773`, read through `api.osv.dev/v1/query` on 2026-11-10: published 2026-11-09 01:25 UTC, modified 02:30 UTC, version 13.3.0, alias GHSA-hh7j-5m3j-23pf.
- [ethersphere/swarm-desktop pull request #582](https://github.com/ethersphere/swarm-desktop/pull/582), fetched 2026-11-10: "fix: replace compromised 0.56.2 release", merged 2026-11-09; the stolen-CI-credentials statement; 0.56.3 is the 0.56.1 code re-released with a new signing certificate.
- [ethersphere/swarm-desktop release v0.56.3](https://github.com/ethersphere/swarm-desktop/releases/tag/v0.56.3), fetched 2026-11-10: marked Latest, dated 09 Nov 12:52, notes "replace compromised 0.56.2 release".
- npm registry document for `@ethersphere/bee-js`, read 2026-11-10: dist-tags `latest` 13.2.0, `upcoming` 13.3.0-upcoming.g4568f7a, `next` 6.4.1-pre.1; 13.3.0 absent from `versions`; 3,496 downloads in the week 2026-11-02 to 2026-11-08 per the npm downloads API.
- [The Hacker News: Hackers Compromise Ethersphere's bee-js and Swarm Desktop](https://thehackernews.com/2026/11/hackers-compromise-etherspheres-bee-js.html), fetched 2026-11-10: 2026-11-09; outlet summary linking the primaries above and the maintainers' new signing-job approval rule.
