# Playbooks

Step-by-step recovery and audit procedures. Optimized for someone who just realized they're in trouble.

| Scenario | Playbook |
|---|---|
| You ran `npm install` on a package that turned out to be malicious | [if-you-installed-a-bad-npm-package.md](if-you-installed-a-bad-npm-package.md) |
| Your `~/.npmrc` token was on disk when malware ran | [if-your-npm-token-leaked.md](if-your-npm-token-leaked.md) |
| Your GitHub PAT was on disk when malware ran | [if-your-github-pat-leaked.md](if-your-github-pat-leaked.md) |
| An MCP server you installed turned out to be malicious | [if-an-mcp-server-was-malicious.md](if-an-mcp-server-was-malicious.md) |
| You need to rotate AWS / GCP / Azure / Kubernetes creds | [rotating-cloud-credentials.md](rotating-cloud-credentials.md) |
| You inherited a vibe-coded repo and need to audit it | [auditing-a-vibe-coded-repo.md](auditing-a-vibe-coded-repo.md) |

## How to use a playbook

1. Identify the matching scenario above.
2. Open the playbook. Each starts with **"Do this first (60 seconds)"** — execute it without reading further.
3. Then work through **"Triage,"** **"Rotate,"** and **"Verify."**
4. If multiple playbooks apply, do **"Do this first"** for all of them, then work each in parallel.

Time is the enemy. Stolen npm tokens publish malicious packages within minutes. Stolen GitHub PATs flip private repos public in seconds. Stolen cloud creds spin up crypto miners on your bill within hours.
