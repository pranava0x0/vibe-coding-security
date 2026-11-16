---
id: 2026-11-fragment-api-py-14-4-2-compromised-pypi-release-remove-and-move-ton-wallet-funds
title: "Compromised fragment-api-py 14.4.2 on PyPI: pin 14.4.1 and move TON funds to a wallet with a new seed phrase"
kind: malicious-artifact
date_disclosed: 2026-11-10
last_updated: 2026-11-16
severity: high
status: contained
ecosystems: [pypi, telegram, ton, crypto]
tools_affected: ["fragment-api-py 14.4.2 (PyPI)", "Telegram bots and scripts that use fragment-api-py with a TON wallet seed phrase"]
tags: [supply-chain, malicious-package, compromised-release, pypi, telegram-bot, crypto-wallet, seed-phrase]
---

## TL;DR
Remove `fragment-api-py` 14.4.2 and pin 14.4.1. If 14.4.2 ran with a TON wallet seed phrase, move all funds to a wallet created from a new seed phrase.

## Packages and versions

| Ecosystem | Name | Bad versions | Clean version or action | Registry state (checked 2026-11-16) | Record |
|---|---|---|---|---|---|
| PyPI | `fragment-api-py` | 14.4.2 (published 2026-11-08 per SafeDep) | pin 14.4.1 | 14.4.2 is not in the index's version list, newest is 14.4.1 | no OSV record returned for the package |

SafeDep describes 14.4.1 as the last release tagged on GitHub. It reports that two wallets lost funds. It gives no download count and no maintainer statement.

## Am I affected?

- `pip show fragment-api-py` prints version 14.4.2 in any environment, virtualenv or image.
- A requirements file or lockfile names `fragment-api-py==14.4.2`, or leaves the version open and was installed on or after 2026-11-08.
- The code that imported the package was given a TON wallet seed phrase.

## If you are affected

1. Move all funds to a wallet created from a new seed phrase. SafeDep says changing the wallet version or subwallet id on the same seed phrase does not help.
2. Uninstall the package, pin `fragment-api-py==14.4.1` with its published hash, and install with hash checking.
3. Rebuild any image or environment that held 14.4.2.
4. Rotate other secrets that process could read. SafeDep does not say whether other credentials were at risk, so this step is this file's advice.

## Prevention

- Pin versions with hashes for anything that handles wallet keys.
- Keep signing keys out of the process that runs third-party packages where the design allows it.
- See [prevention/package-vetting-checklist.md](../prevention/package-vetting-checklist.md) and [prevention/credential-hygiene.md](../prevention/credential-hygiene.md).

## Sources

One research firm, plus the registry's own state.

- [SafeDep: Backdoored PyPI Package fragment-api-py 14.4.2 Drains TON Wallets on Startup](https://safedep.io/blog/fragment-api-py-pypi-ton-wallet-drainer.md), 2026-11-10, fetched 2026-11-16 for versions, dates, credential categories and remediation only.
- `pip index versions fragment-api-py`, run 2026-11-16: 14.4.1 is the newest version listed and 14.4.2 is absent.
- OSV query for `fragment-api-py`, 2026-11-16: no records.
- Not opened: SafeDep's indicator list.
