# npm hardening

> Reduce the blast radius of `npm install` so that a compromised package can't trivially own you.

## The single highest-leverage setting

```bash
npm config set ignore-scripts true
```

This globally disables `preinstall` / `install` / `postinstall` scripts. **Shai-Hulud, Nx s1ngularity, and most npm worms execute via `postinstall`** — this neuters the most common attack vector with one line.

Trade-off: a few legitimate packages need their install scripts (esbuild, sharp, node-sass). For those, run with `--scripts-prepended-node-path` and only enable scripts after auditing what they do:

```bash
# Per-install override when you trust this specific install
npm install <pkg> --foreground-scripts --ignore-scripts=false
```

Or maintain a per-project `.npmrc` that re-enables for projects you've vetted.

## Use `npm ci`, not `npm install`, in CI

`npm install` resolves versions live and can pull a freshly-published malicious version. `npm ci` installs *exactly* what's in the lockfile — same SHAs, every time.

```bash
# In every CI job
npm ci --ignore-scripts
```

## Pin exactly, not loosely

In `package.json`, avoid `^` and `~` for dependencies that are credential-relevant or low-level (build tools, HTTP clients, IPC libs). Pin exact:

```json
{
  "dependencies": {
    "axios": "1.7.4",        // not "^1.7.4"
    "node-ipc": "9.2.1"      // not "~9.2.1"
  }
}
```

The lockfile already pins SHAs, but a fresh `npm install` (vs `ci`) will resolve to a new version inside the range and replace lockfile entries — including the malicious one if you're unlucky.

## Use `overrides` to block known-bad versions

When an advisory hits, you can block a bad version range across your entire transitive tree:

```json
{
  "overrides": {
    "axios": "1.7.4",
    "node-ipc": "9.2.1"
  }
}
```

For yarn use `resolutions`. For pnpm use `pnpm.overrides`.

## Run scans before merge

Wire these into pre-commit and CI:

- **[Socket](https://socket.dev/)** — supply-chain risk score per package. Free for open source.
- **[Snyk](https://snyk.io/) `snyk test`** — known CVEs in deps.
- **[npm audit](https://docs.npmjs.com/cli/v10/commands/npm-audit)** — built-in, runs against GitHub Advisory Database.
- **[npq](https://github.com/lirantal/npq)** — wraps `npm install` and prompts before installing low-reputation packages.

A reasonable pre-commit:

```bash
#!/bin/bash
npm audit --audit-level=high || exit 1
npx socket-security scan || exit 1
```

## Use a registry proxy for sensitive teams

Tools like [JFrog Xray](https://jfrog.com/xray/), [Sonatype Nexus Firewall](https://www.sonatype.com/products/nexus-firewall), or [Cloudsmith](https://cloudsmith.com/) can hold new package versions for 24–48 hours, blocking install of fresh malicious publishes during the typical detection-and-takedown window. The simplest version: cache packages in your own registry; only sync new versions after they've existed for 24+ hours.

## Audit the lockfile diff in every PR

In code review: when a PR touches `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml`, **look at the new packages**. A PR titled "fix typo" that adds 47 transitive deps is a flag.

## Disable telemetry / postinstall analytics

```bash
npm config set fund false
npm config set audit-level critical  # less noise, surface only critical
```

## What this stack stops

| Attack | Mitigation |
|---|---|
| Shai-Hulud, Nx s1ngularity (postinstall) | `ignore-scripts` |
| Axios, qix (auto-update to bad version) | `npm ci` + exact pins |
| TanStack mini Shai-Hulud (signed-but-bad in CI) | registry proxy hold-window + scan |
| Slopsquatting | `npq` / Socket pre-install check |
| Transitive bad versions | `overrides` / `resolutions` |

## What this stack doesn't stop

- A maintainer being legitimately compromised AND your scanner not having flagged the version yet. This is the irreducible risk; the only real mitigation is **distance from the dependency** (don't depend on it at all, or use a vendored copy).
- Build-pipeline compromises that result in *legitimately-signed* malicious artifacts (the TanStack pattern). Defense-in-depth helps: registry proxy hold-window + Socket alerts catch most of these within hours.
