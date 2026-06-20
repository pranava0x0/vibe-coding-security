# If you ran a malicious npm postinstall script

> Scope: `npm install` ran an attacker-controlled `install`/`preinstall`/`postinstall` lifecycle script or `binding.gyp` node-gyp build step.

## Do this first

1. **Disconnect from the internet** (stops active exfiltration).
2. Kill node processes: `pkill -f node`.
3. Note the exact package name + version.

## Assume full credential exposure

Postinstall scripts run as your user and can read all files in `~/` (`.aws/credentials`, `.ssh/`, `.npmrc`, `.claude/`, `.cursor/`, etc.) and all environment variables. Rotate immediately:

1. Cloud IAM credentials → [rotating-cloud-credentials.md](rotating-cloud-credentials.md)
2. GitHub PAT / SSH keys → [if-your-github-pat-leaked.md](if-your-github-pat-leaked.md)
3. npm token → [if-your-npm-token-leaked.md](if-your-npm-token-leaked.md)
4. LLM API keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, etc.)

## Check for persistence

```bash
crontab -l 2>/dev/null
ls ~/Library/LaunchAgents/ 2>/dev/null     # macOS
ls ~/.config/systemd/user/ 2>/dev/null     # Linux
ls -lt ~/.bashrc ~/.zshrc ~/.profile 2>/dev/null
```

## Check AI config for poisoning (TrapDoor class)

```bash
python3 -c "
import os
for f in ['.cursorrules','CLAUDE.md','.windsurfrules','AGENTS.md']:
    if os.path.exists(f):
        t = open(f).read()
        bad = [hex(ord(c)) for c in t if 0x200b <= ord(c) <= 0x200f or ord(c) == 0xfeff]
        if bad: print(f'{f}: SUSPICIOUS', bad)
"
```

## References

- [Snyk — NPM Security Best Practices After the Shai-Hulud Attack](https://snyk.io/articles/npm-security-best-practices-shai-hulud-attack/)
- [CISA — Defending Against Software Supply Chain Attacks](https://www.cisa.gov/resources-tools/resources/defending-against-software-supply-chain-attacks)

## Prevention
→ [prevention/npm-hardening.md](../prevention/npm-hardening.md)
→ [prevention/supply-chain-attack-surface.md](../prevention/supply-chain-attack-surface.md)
