# If your web app was compromised

> Scope: a production web app (Next.js, React, FastAPI, Streamlit, or any framework) had an exploitable vulnerability that was or may have been actively exploited — RCE, auth bypass, SSRF, deserialization, etc.

## Do this first

1. **Take the app offline or restrict to known IPs** at the network layer.
2. **Preserve logs before you do anything else** — they overwrite quickly.
3. Note the CVE / affected version.

## Assume full credential exfiltration

The compromised process could read:

- **Cloud metadata** (`169.254.169.254`) → IAM role credentials → rotate immediately: [rotating-cloud-credentials.md](rotating-cloud-credentials.md)
- **Environment variables** → all secrets the process held
- **Database connection string** → treat DB as accessed; audit query logs
- **GitHub PAT / deploy keys** → [if-your-github-pat-leaked.md](if-your-github-pat-leaked.md)
- **Session secrets / JWT signing keys** → rotate and invalidate existing sessions

## Check for persistence

```bash
# New cron jobs
crontab -l -u www-data 2>/dev/null
# New files in web directories
find /var/www /app -newer /tmp -ls 2>/dev/null | head -10
# Unexpected outbound connections
ss -tnp | grep -v "127.0.0.1\|::1"
```

## Patch and redeploy

1. Identify the CVE; apply the vendor patch.
2. Deploy from a clean build — not the potentially-modified running binary.
3. Re-enable external traffic only after confirming the patch is live.

## Prevention
→ [prevention/credential-hygiene.md](../prevention/credential-hygiene.md)
→ [prevention/agent-sandboxing.md](../prevention/agent-sandboxing.md)
→ Block IMDS egress (IMDSv2 hop-limit 1; Kubernetes NetworkPolicy denying `169.254.169.254`).
