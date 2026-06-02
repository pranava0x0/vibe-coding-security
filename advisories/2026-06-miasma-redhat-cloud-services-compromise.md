---
id: 2026-06-miasma-redhat-cloud-services-compromise
title: "Miasma — @redhat-cloud-services npm scope compromised by Mini-Shai-Hulud-derived worm (June 2026)"
date_disclosed: 2026-06-01
last_updated: 2026-06-02
severity: critical
status: contained
ecosystems: [npm, github-actions]
tools_affected: [any-redhat-cloud-services-consumer, openshift-frontend-apps, any-react-frontend-using-redhat-ui, ci-cd, claude-code, cursor, openhands]
tags: [supply-chain, worm, credential-theft, mini-shai-hulud, teampcp-derivative, oidc, github-actions, cloud-credential-theft, anthropic-camouflage]
---

## TL;DR
On **2026-06-01**, Wiz Research and others identified a supply-chain compromise of the **`@redhat-cloud-services` npm scope** — Red Hat's official client libraries used by the Hybrid Cloud Console, Insights, and OpenShift frontends. **32 packages / 96 malicious versions** were published in a roughly **72-second automated burst** ([Aikido](https://www.aikido.dev/blog/red-hat-npm-packages-compromised-credential-stealing-worm), [Wiz](https://www.wiz.io/blog/miasma-supply-chain-attack-targeting-redhat-npm-packages)), each carrying a **preinstall hook** that drops a **~4.2 MB obfuscated payload** stealing **AWS / GCP / Azure / Kubernetes / HashiCorp Vault / GitHub / npm / CircleCI** credentials. Cumulative weekly downloads of the affected scope: **~80,000**. The campaign — dubbed **"Miasma: The Spreading Blight"** — is a **lightly reskinned descendant of the (Mini) Shai-Hulud worm** that [TeamPCP open-sourced on 2026-05-12](2026-05-shai-hulud-copycat-wave.md), with **Greek-mythology theming (`spartan`) replacing Dune references** but the same self-propagation core, and **new GCP/Azure identity collectors** added. Notable IOC: the payload exfiltrates over HTTPS to a **camouflage URL `https://api.anthropic.com:443/v1/api`** — *not* Anthropic infrastructure, but a fake path on a real-vendor host chosen to blend into network logs at organizations using Anthropic. Initial access was a **compromised Red Hat employee GitHub account → GitHub Actions OIDC token → npm publish** ([JFrog](https://research.jfrog.com/post/shai-hulud-miasma-redhat-cloud-services/), [Aikido](https://www.aikido.dev/blog/red-hat-npm-packages-compromised-credential-stealing-worm)). Red Hat published [RHSB-2026-006](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006); npm has removed the malicious versions.

## What happened

On **2026-06-01**, Wiz Research detected malicious code in **at least 32 package releases** published under the [`@redhat-cloud-services`](https://github.com/RedHatInsights/javascript-clients/issues/492) npm scope — Red Hat's official frontend client libraries used by the OpenShift / Hybrid Cloud Console / Insights / Edge dashboards. The malicious releases included `@redhat-cloud-services/chrome`, `@redhat-cloud-services/compliance-client`, `@redhat-cloud-services/frontend-components`, and ~29 sibling client libraries. Across those 32 packages, **96 unique malicious versions** were published in a **~72-second window**, indicating fully automated publishing — the actor's tooling, not a sleepy human.

### Attack flow

1. **Initial access — compromised Red Hat employee GitHub account.** JFrog and Aikido converged on the conclusion that an employee's GitHub account was the foothold; the malicious npm publishes ran via the existing **GitHub Actions OIDC token** that the legitimate release workflow uses to talk to npm. **The npm account itself was not separately phished** — the source-repo trust boundary failed first. (Same shape as [Megalodon's `@tiledesk/tiledesk-server` arm](2026-05-megalodon-github-actions-mass-campaign.md).)
2. **Mass automated publishing.** 96 versions / 32 packages / 72 seconds → strong signal of a scripted republish that walked the org's package list.
3. **Preinstall hook.** Each malicious version's `package.json` adds a `preinstall` script that runs *before* dependency resolution completes. Anyone who ran `npm install` against an unpinned `^x.y.z` range or a `latest` tag on **2026-06-01** executed the payload on their workstation or CI runner.
4. **Stage-2 payload — ~4.2 MB obfuscated JavaScript.** Once decoded, the payload is a multi-stage credential harvester. It enumerates AWS / GCP / Azure / Kubernetes / HashiCorp Vault / GitHub / npm / CircleCI credentials reachable from the host, **explicitly attempts to bypass StepSecurity Harden-Runner**, then exfiltrates harvested data over HTTPS to a **camouflage URL `https://api.anthropic.com:443/v1/api`** — *not* Anthropic infrastructure, but the real host with a non-existent path, chosen because outbound HTTPS to `api.anthropic.com` is a *baseline-normal* destination at most organizations that use Anthropic models and will not flag in egress logs ([CyberSecurity News](https://cybersecuritynews.com/red-hat-cloud-services-npm-packages/), [StepSecurity](https://www.stepsecurity.io/blog/multiple-redhat-cloud-services-npm-packages-compromised)). Because the path is non-existent, every exfil POST returns 4xx — but the request *itself* carries the exfiltrated payload in body/headers, and many security stacks log only response codes.
5. **Worm component.** The payload also attempts to use the stolen npm token to **republish trojanized versions of every other package the victim can publish to**, the same self-propagation primitive as the original [Shai-Hulud](2025-09-shai-hulud-original.md), [Mini Shai-Hulud](2026-05-tanstack-mini-shai-hulud.md), and TrapDoor waves.

### What's new vs. plain Mini Shai-Hulud

Miasma is largely the **open-sourced Mini Shai-Hulud worm with cosmetic and operational changes** ([JFrog research](https://research.jfrog.com/post/shai-hulud-miasma-redhat-cloud-services/), [Wiz](https://www.wiz.io/blog/miasma-supply-chain-attack-targeting-redhat-npm-packages)), but two changes matter:

- **Greek-mythology theming replaces Dune.** Internal markers / function names now use `spartan`/`miasma` instead of `kralizec`/`phibian`/`shai-hulud`. This breaks blue-team yara rules and SIEM queries that grep for the original Dune string set.
- **New cloud-identity collectors.** Where the original Mini Shai-Hulud focused on AWS + GitHub + npm, Miasma added explicit **GCP and Azure identity collectors** that enumerate every cloud identity the infected machine has access to. This squarely targets *cloud-frontend* dev environments — which is exactly the audience of `@redhat-cloud-services` (OpenShift / RHEL / Insights dashboards run with broad multi-cloud IAM grants).
- **`api.anthropic.com` camouflage exfil.** The first observed wave to disguise exfil traffic as **AI-vendor API calls** rather than the usual GitHub Gist / direct VPS / disposable-tunnel C2. Expect this technique to spread to other waves — `api.openai.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, `bedrock-runtime.us-east-1.amazonaws.com` are all "AI-coding-tool baseline-normal" destinations now.

### Attribution

This is **almost certainly not TeamPCP themselves**. TeamPCP open-sourced the Mini Shai-Hulud worm on **2026-05-12** with the message *"Shai-Hulud: Open Sourcing The Carnage"*, and Miasma is what one would expect a competent second actor to ship two weeks later: original payload, new theming, expanded cloud-identity collection, fresh C2 disguise. This is the **third worm-source-public copycat wave** sweep-tracked so far:

1. [TrapDoor (2026-05-22)](2026-05-trapdoor-cross-ecosystem-stealer.md) — different actor, cross-ecosystem (npm + PyPI + Crates.io), `.cursorrules`/`CLAUDE.md` poisoning.
2. [Shai-Hulud copycat wave (2026-05-18)](2026-05-shai-hulud-copycat-wave.md) — `deadcode09284814` typosquats, near-verbatim worm clones with `*.lhr.life` C2.
3. **Miasma (2026-06-01)** — first to land on a major *legitimate* npm scope at TeamPCP scale rather than typosquats, with cloud-identity expansion and AI-vendor camouflage exfil.

The blast radius is smaller than the TanStack/Mistral wave (~80K weekly downloads vs. 518M+), but the **target scope alignment is sharper** — every consumer of `@redhat-cloud-services` is, by definition, a multi-cloud IAM holder.

## Am I affected?

### Check whether any compromised version reached your lockfile

```bash
# Any version of the scope installed in the install window
npm ls --all 2>/dev/null | grep '@redhat-cloud-services/'

# Specific packages confirmed compromised (sample; see Red Hat RHSB-2026-006 for the full list)
for p in chrome compliance-client frontend-components rbac-client host-inventory-client \
         notifications-client patches-client sources-client subscriptions-client \
         types config-utils-frontend frontend-components-config-utilities; do
  npm ls "@redhat-cloud-services/$p" 2>/dev/null
done

# Any install activity on 2026-06-01 (the window of malicious-version availability)
grep '@redhat-cloud-services' ~/.npm/_logs/*.log 2>/dev/null | grep '2026-06-01'
```

### Check your CI / Docker images

```bash
# Re-build any image whose lockfile or layer was created on 2026-06-01 against the
# scope's malicious versions. Pull the affected versions out of any registry cache:
docker images --digests | grep -i redhat-cloud-services
```

### Egress check — the camouflage IOC

If you have CI / endpoint egress logs, search for **outbound HTTPS to `api.anthropic.com` from non-AI workloads** on or after **2026-06-01**, especially with response codes that are not 200 (Anthropic's API does not have a `/v1/api` path, so every exfil request will be 4xx):

```bash
# Pseudo-pattern; adapt to your egress logs (CloudFlare/Cloudflare Logpush/AWS VPC flow logs/etc.)
grep -E 'api\.anthropic\.com[^ ]*/v1/api' /var/log/egress/* 2>/dev/null
```

Hits from a build/CI runner that doesn't talk to Claude are high-confidence Miasma exfil. Hits from a developer workstation that *does* normally talk to Claude need to be cross-correlated with the timestamp window.

### IOCs

| Type | Value |
|---|---|
| Campaign | **Miasma** (Wiz naming; "Miasma: The Spreading Blight") |
| Malware family | (Mini) **Shai-Hulud** — open-sourced by TeamPCP 2026-05-12; Miasma is a derivative with Greek-mythology theming |
| Disclosure | **2026-06-01** (Wiz Research) |
| Affected scope | **`@redhat-cloud-services`** (npm) |
| Versions | **32 packages / 96 malicious versions**, published in a ~72-second automated burst on **2026-06-01** |
| Cumulative downloads | ~**80,000 weekly** across the affected scope |
| Initial access | Compromised **Red Hat employee GitHub account** → existing GitHub Actions OIDC → `npm publish` |
| Trigger | **`preinstall`** lifecycle hook in `package.json` |
| Payload | ~**4.2 MB obfuscated JavaScript**; harvests AWS / GCP / Azure / K8s / Vault / GitHub / npm / CircleCI creds; explicit **Harden-Runner evasion** |
| Exfil destination (camouflage) | **`https://api.anthropic.com:443/v1/api`** — fake path on real-vendor host; not Anthropic infrastructure |
| Internal markers | `spartan`, `miasma` (Greek-mythology replacement for original Dune markers) |
| Worm primitive | Steals npm token + republishes trojanized versions of every other package the victim can publish |
| Red Hat advisory | **RHSB-2026-006** ([Red Hat Customer Portal](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006)) |
| Upstream tracking issue | [RedHatInsights/javascript-clients#492](https://github.com/RedHatInsights/javascript-clients/issues/492) |
| Status | **Contained** — malicious versions removed from npm; investigation ongoing |
| Attribution | **Unknown actor, distinct from TeamPCP** — third documented copycat of the open-sourced Mini Shai-Hulud worm after [TrapDoor](2026-05-trapdoor-cross-ecosystem-stealer.md) and the [`deadcode09284814` typosquat wave](2026-05-shai-hulud-copycat-wave.md) |

## If you are affected

If `@redhat-cloud-services/*` was resolved or installed against a malicious 2026-06-01 version on any developer machine or CI runner:

→ [playbooks/if-you-installed-a-bad-npm-package.md](../playbooks/if-you-installed-a-bad-npm-package.md)
→ [playbooks/rotating-cloud-credentials.md](../playbooks/rotating-cloud-credentials.md) — **multi-cloud**: rotate AWS, GCP, Azure access keys and any K8s / Vault tokens reachable from the affected host
→ [playbooks/if-your-github-pat-leaked.md](../playbooks/if-your-github-pat-leaked.md) — every reachable GitHub PAT, npm token, and CircleCI token is in scope
→ Pin to a **pre-2026-06-01 known-good version** for every affected package and clear your npm/yarn/pnpm caches:

```bash
rm -rf ~/.npm/_cacache ~/.npm/_logs
rm -rf node_modules package-lock.json
npm install
# Verify your lockfile resolves to versions published before 2026-06-01
```

→ If you run a corporate npm mirror (Artifactory / Verdaccio / Sonatype): purge the malicious versions from your mirror's cache before letting developers re-install.

## Prevention

→ [prevention/npm-hardening.md](../prevention/npm-hardening.md) — **`minimumReleaseAge`** would have blocked these versions for the 72-hour shake-out window during which they were detected and removed; **`ignore-scripts`** would have blocked the `preinstall` hook entirely
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md) — short-lived, narrowly-scoped cloud creds; no long-lived multi-cloud admin tokens in dev environments
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md) — your AI coding agent shouldn't be able to reach `api.anthropic.com` *from a CI runner that doesn't host the agent*; an explicit egress allowlist on CI runners would have caught the camouflage exfil
→ **Detect the camouflage primitive in your egress logs.** Add an alert for any outbound HTTPS to `api.anthropic.com` from workloads that are not the AI tool itself — this catches Miasma and any future variant that picks a different AI-vendor host (`api.openai.com`, `generativelanguage.googleapis.com`, etc.)
→ **Require signed commits + protected-branch review on `.github/workflows/`** — same defense as [Megalodon](2026-05-megalodon-github-actions-mass-campaign.md); the GitHub Actions OIDC publish path is only as trustworthy as the source repo behind it
→ Subscribe to [SafeDep](https://safedep.io/) / [StepSecurity](https://www.stepsecurity.io/blog) / [Aikido](https://www.aikido.dev/blog) / [Socket](https://socket.dev/blog) supply-chain feeds — Miasma was named within 12 hours of first publish, but only because all four had agents watching the npm publish firehose

## Sources

- [Wiz Research — Miasma: Supply Chain Attack Targeting RedHat npm Packages](https://www.wiz.io/blog/miasma-supply-chain-attack-targeting-redhat-npm-packages) — canonical first disclosure, named the campaign, 32 packages / 96 versions / 72-second burst
- [JFrog Security Research — Shai-Hulud — Miasma: The Spreading Blight Hits Red Hat npm Packages](https://research.jfrog.com/post/shai-hulud-miasma-redhat-cloud-services/) — payload reverse-engineering, Greek-mythology marker, GCP/Azure collector additions, employee-account attribution
- [Aikido — Red Hat npm Packages Compromised to Spread a Credential-Stealing Worm](https://www.aikido.dev/blog/red-hat-npm-packages-compromised-credential-stealing-worm) — automation evidence (72-second window), GitHub Actions OIDC publish path
- [StepSecurity — Multiple redhat-cloud-services npm Packages compromised](https://www.stepsecurity.io/blog/multiple-redhat-cloud-services-npm-packages-compromised) — package list, Harden-Runner-evasion call-out, `api.anthropic.com` camouflage IOC
- [Snyk — Miasma Attack Hits Red Hat npm Packages](https://snyk.io/blog/miasma-supply-chain-attack-malicious-code-redhat-cloud-services-npm-packages/) — payload taxonomy, AI-supply-chain framing
- [The Hacker News — Miasma Supply Chain Attack Compromises Red Hat npm Packages with Credential-Stealing Worm](https://thehackernews.com/2026/06/miasma-supply-chain-attack-compromises.html) — mainstream coverage, payload summary
- [Cybersecurity News — Multiple Red Hat Cloud Services npm Packages Compromised to Deploy Credential-Stealing Malware](https://cybersecuritynews.com/red-hat-cloud-services-npm-packages/) — `api.anthropic.com/v1/api` exfil endpoint, Mini-Shai-Hulud-family attribution
- [The Register — Shai-Hulud malware worms Red Hat npm package versions downloaded 80K times a week](https://www.theregister.com/security/2026/06/01/shai-hulud-malware-infects-red-hat-npm-packages-downloaded-80k-times-weekly/5249803) — ~80K weekly download figure, worm-propagation framing
- [BleepingComputer — Red Hat npm packages compromised to steal developer credentials](https://www.bleepingcomputer.com/news/security/red-hat-npm-packages-compromised-to-steal-developer-credentials/) — confirmed credential-theft scope
- [Mend — Miasma: Red Hat Cloud Services npm Packages Hit by a Mini Shai-Hulud-Style Campaign](https://www.mend.io/blog/redhat-cloud-services-packages-drop-multi-cloud-credential-stealer/) — multi-cloud-stealer framing
- [Orca Security — Red Hat npm Packages Compromised in Supply-Chain Attack Spreading Credential-Stealing Worm](https://orca.security/resources/blog/red-hat-npm-supply-chain-attack/) — preinstall-hook flow
- [Sonatype — Red Hat Cloud Services npm Packages Hijacked](https://www.sonatype.com/blog/red-hat-cloud-services-npm-packages-hijacked) — Sonatype Firewall detection
- [OX Security — New Shai-Hulud hits npm: @redhat-cloud-services Compromised](https://www.ox.security/blog/new-npm-supply-chain-attack-redhat-cloud-services-compromised/) — Shai-Hulud-family lineage
- [Security Boulevard — Miasma: Red Hat Cloud Services npm Packages Hit by a Mini Shai-Hulud-Style Campaign](https://securityboulevard.com/2026/06/miasma-red-hat-cloud-services-npm-packages-hit-by-a-mini-shai-hulud-style-campaign/) — aggregator summary
- [Red Hat — RHSB-2026-006: Supply chain compromise of @redhat-cloud-services npm packages](https://access.redhat.com/security/vulnerabilities/RHSB-2026-006) — official vendor advisory ID
- [RedHatInsights/javascript-clients#492 — Malicious npm releases detected across `@redhat-cloud-services/` scope](https://github.com/RedHatInsights/javascript-clients/issues/492) — upstream tracking issue with confirmed package-version list
