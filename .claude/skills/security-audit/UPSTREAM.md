# Upstream provenance

This directory is a vendored copy of Cloudflare's `security-audit` skill.

- Upstream: https://github.com/cloudflare/security-audit-skill (`skills/security-audit/`)
- Upstream commit: `c1c8a8c1471069fb0e188eeaff69b8e8db6564a8` (2026-09-14, "Clarify guidance and full audit modes")
- Fetched: 2026-11-06 from `raw.githubusercontent.com/cloudflare/security-audit-skill/main/`
- Licence: MIT, see [LICENSE](LICENSE). The upstream README is not copied; the file list and phases are described in [`prevention/agent-security-audit.md`](../../../prevention/agent-security-audit.md).
- Local changes: none. Every file other than this one and `LICENSE` is byte-identical to upstream at that commit.

## Why it is vendored

`/security-audit` runs inside Claude Code sessions opened on this repository without a network install step, and the version that produced each self-audit under [`security-audits/`](../../../security-audits/) is the one in the tree at that commit. The upstream install path is `npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit`.

## Refreshing

```bash
for f in SKILL.md RECONNAISSANCE.md HUNTING.md ATTACK-CLASSES.md VALIDATION-AND-REPORTING.md \
         MEMORY-SAFETY-AND-BINARY.md AI-AND-LLM.md WEB-PROTOCOL-AND-AUTH.md CLIENT-SIDE.md \
         SUPPLY-CHAIN-AND-RELEASE.md CLOUD-AND-DEPLOYMENT.md PROTOCOLS-RPC-AND-MESSAGING.md \
         RESOURCE-EXHAUSTION-AND-AVAILABILITY.md DATA-ISOLATION-AND-LIFECYCLE.md \
         DESKTOP-MOBILE-AND-LOCAL-IPC.md report-schema.json validate-findings.cjs \
         validate-findings.test.cjs validate-coverage-ledger.cjs validate-coverage-ledger.test.cjs; do
  curl -sSf -o ".claude/skills/security-audit/$f" \
    "https://raw.githubusercontent.com/cloudflare/security-audit-skill/<commit>/skills/security-audit/$f"
done
node --test .claude/skills/security-audit/validate-findings.test.cjs .claude/skills/security-audit/validate-coverage-ledger.test.cjs
```

Update the commit and date above after a refresh, and note any local change here.
