---
id: 2026-11-antd-img-crop-github-repository-forged-commit-do-not-install-from-git-npm-clean
title: "Forged commit in the antd-img-crop GitHub repository: do not install from git; the npm package is clean"
kind: malicious-artifact
date_disclosed: 2026-11-03
last_updated: 2026-11-03
severity: high
status: unconfirmed
ecosystems: [github, npm, git-dependencies, react, hugo]
tools_affected: ["anyone who cloned, forked, built or installed github.com/nanxiaobei/antd-img-crop from git after 2026-10-31 15:12 UTC (a `github:` specifier, a git URL in package.json, a lockfile `resolved` git URL, or a developer checkout)", "anyone who installed the Hugo theme github.com/nanxiaobei/hugo-paper from git between 2026-08-21 and 2026-10-21", "Ant Design React apps that pin antd-img-crop through npm are not affected by the registry copy"]
tags: [malicious-artifact, forged-commit, force-push, github-repository, maintainer-account-compromise, stealer, credential-theft, supply-chain, npm-clean, git-dependency, single-source, safedep]
---

## TL;DR
Do not clone, build or install `antd-img-crop` from its GitHub repository until the maintainer or a second firm confirms it is restored; the npm package `antd-img-crop` (newest 4.30.0, published 2026-03-12) is not affected and a registry install is fine. If a machine ran a git checkout taken after 2026-10-31 15:12 UTC, or the `hugo-paper` theme from git between 2026-08-21 and 2026-10-21, rotate browser-saved passwords, SSH keys, `.env` and `.npmrc` secrets, keychain and keyring entries, and wallet material from a clean machine.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (date checked) | Record |
|---|---|---|---|---|---|
| GitHub repository | `nanxiaobei/antd-img-crop` (`main`) | one forged commit force-pushed 2026-10-31 15:12 UTC from the maintainer's account, rebuilding the 4.30.0 release commit with the original author line, date (displayed as Mar 12) and message | do not install from git; use the npm package; wait for a maintainer or second-firm statement before trusting `main` | commits page read 2026-11-03 shows a top commit titled "4.30.0" dated Mar 12, 2026, which is the shape SafeDep describes; the activity page needs a sign-in and was not read | none (OSV query returns zero records for the npm package; no GHSA) |
| npm | `antd-img-crop` | none | 4.30.0 (2026-03-12 16:53 UTC) is `latest`; about 97,000 downloads in the week to 2026-11-02 | `time` ends at 4.30.0 on 2026-03-12 with no later publish (2026-11-03); SafeDep: "The npm package is not affected" | none |
| GitHub repository | `nanxiaobei/hugo-paper` (Hugo theme) | a dropper added 2026-08-21, removed 2026-10-21 (per SafeDep) | clean as of 2026-11-03 per SafeDep; the commits page shows "remove preinstall" on Oct 21 and later commits on Oct 26 | no registry | none |

SafeDep (2026-11-03, Kunal Singh) is the only source, so `status` is `unconfirmed`. The post says the maintainer account should be treated as still compromised, which is why the repository stays on this list even though the forged commit may be reverted by the time you read this. The npm tarball predates the forged commit by seven months, so a registry-keyed scanner, `npm audit` and `npm view` all read clean, and that is correct for the registry copy and says nothing about a git install.

## Am I affected?

```bash
# Any git-sourced install of either repository in a project
grep -rn 'nanxiaobei/antd-img-crop\|nanxiaobei/hugo-paper\|github:nanxiaobei' package.json package-lock.json pnpm-lock.yaml yarn.lock go.mod hugo.toml config.toml 2>/dev/null
# A lockfile that resolved antd-img-crop from the registry is fine; one that resolved it from git is not
grep -n '"resolved": "git' package-lock.json 2>/dev/null | grep -i antd-img-crop
# Local checkouts and their checkout time
find ~ -maxdepth 4 -type d -name 'antd-img-crop' -o -maxdepth 4 -type d -name 'hugo-paper' 2>/dev/null
```

- A clone or fork taken after 2026-10-31 15:12 UTC, or a `hugo-paper` checkout between 2026-08-21 and 2026-10-21, is the exposure. The displayed commit date is not the checkout date; check your clone's reflog or the directory's creation time.
- SafeDep's post names a macOS temporary path (`/var/tmp/check`) and persistence entries on macOS, Linux and Windows, including short-lived SYSTEM scheduled tasks on Windows; its linked indicator list has the exact names and is not reproduced here.

## If you are affected

- Delete the checkout. Reinstall `antd-img-crop` from npm only.
- From a clean machine, rotate the credential categories SafeDep lists as targeted: browser passwords and cookies, macOS Keychain and Linux keyring entries, SSH keys, `.env`, `.npmrc` and `.gitconfig` secrets, KeePass databases, and cryptocurrency wallet and key material. Follow [if you ran a malicious postinstall](../playbooks/if-you-ran-malicious-postinstall.md), [if your npm token leaked](../playbooks/if-your-npm-token-leaked.md) and [if your GitHub PAT leaked](../playbooks/if-your-github-pat-leaked.md).
- Check the persistence locations SafeDep lists for your operating system and remove what you confirm, then decide with help whether to rebuild the machine.

## Prevention

- Install libraries from the registry, not from `github:` specifiers or git URLs, unless you pin a commit you have read; a registry publish is a second event an attacker with a repository account has to perform.
- Treat a force push on a default branch, or a head commit that loses its Verified badge, as an alert on any repository you build from; SafeDep's post describes both signals. See [package vetting](../prevention/package-vetting-checklist.md) and [npm hardening](../prevention/npm-hardening.md).

## Sources
- [SafeDep — antd-img-crop GitHub Repository Hijacked to Deliver OverLord Stealer](https://safedep.io/blog/antd-img-crop-forged-commit-overlord-stealer.md) — fetched 2026-11-03: 2026-11-03, Kunal Singh; the force push at 2026-10-31 15:12 UTC from the maintainer's account, the reused author line, date and message, "The npm package is not affected", the `hugo-paper` dates, the credential categories, the Contagious Interview technique match stated as not attribution. Behaviour, addresses and the indicator list are in the post and not here.
- npm registry `antd-img-crop` `time` and `dist-tags`, queried 2026-11-03: 4.30.0 at 2026-03-12 16:53 UTC is `latest`, no later entry; `api.npmjs.org` weekly downloads 97,138 for 2026-10-27 to 2026-11-02.
- OSV API query for npm `antd-img-crop`, 2026-11-03: zero records.
- [nanxiaobei/antd-img-crop — commits on main](https://github.com/nanxiaobei/antd-img-crop/commits/main) — fetched 2026-11-03: top commit titled "4.30.0" dated Mar 12, 2026, author nanxiaobei; the page does not show whether it is the forged commit, and the activity page returned only navigation without a sign-in.
- [nanxiaobei/hugo-paper — commits on main](https://github.com/nanxiaobei/hugo-paper/commits/main) — fetched 2026-11-03: "remove preinstall" on Oct 21, 2026, three commits on Oct 26, 2026.
