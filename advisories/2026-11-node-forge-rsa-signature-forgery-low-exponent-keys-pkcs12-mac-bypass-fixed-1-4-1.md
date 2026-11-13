---
id: 2026-11-node-forge-rsa-signature-forgery-low-exponent-keys-pkcs12-mac-bypass-fixed-1-4-1
title: "node-forge before 1.4.1: RSA signature forgery for e=3 keys (CVE-2026-85393) and PKCS#12 integrity bypass (CVE-2026-118782); upgrade to 1.4.1 or later"
date_disclosed: 2026-10-27
last_updated: 2026-11-13
severity: high
status: patched
ecosystems: [npm, javascript, cryptography]
tools_affected: ["node-forge (npm) 1.4.0 and earlier", "applications that verify RSA PKCS#1 v1.5 signatures, X.509 certificates or PKCS#7 signatures with node-forge", "applications that open PKCS#12 files or PKCS#8 encrypted private keys from untrusted sources with node-forge", "lockfiles that pin node-forge 1.4.0 or earlier as a transitive dependency"]
tags: [cve, node-forge, npm, cryptography, signature-forgery, rsa, pkcs12, x509, transitive-dependency, incomplete-fix, patched]
---

## TL;DR
node-forge 1.4.0 and earlier accept forged RSA PKCS#1 v1.5 signatures for keys with public exponent 3, and accept PKCS#12 files whose password check an attacker can bypass. Three vendor advisories cover this, all fixed in 1.4.1, published to npm on 2026-10-27. The package had 53,233,919 downloads in the week 2026-11-06 to 2026-11-12. Run `npm ls node-forge` and upgrade to 1.4.1 or later. The newest release is 1.4.3.

## What happened

The maintainers (the `digitalbazaar/forge` repository) published the two signature advisories on 2026-10-27, the day 1.4.1 reached npm. The vendor page for the PKCS#12 advisory was not opened; its CNA record is dated 2026-10-29. The GitHub Advisory Database listed the PKCS#12 one on 2026-10-30 and one of the signature ones on 2026-11-10, which is how it reached this sweep. The database dates are not the disclosure dates.

| Advisory | CVE | Score | What it is |
|---|---|---|---|
| GHSA-2g46-22mc-6gwp | CVE-2026-85393 (VulnCheck, record published 2026-09-03) | vendor CVSS 3.1 7.5; VulnCheck CVSS 4.0 8.7 and 3.1 7.5 | Verification ignored extra elements in the nested DigestAlgorithm sequence of the DigestInfo |
| GHSA-6qrw-m8cv-hcxf | the page prints CVE-2026-119192; CVE Services had no record on 2026-11-13 | vendor CVSS 3.1 7.5 | Verification accepted non-canonical BER encodings of the DigestInfo |
| GHSA-jc66-7q78-782g | CVE-2026-118782 (GitHub CNA, 2026-10-29) | CNA CVSS 3.1 7.5 | A PKCS#12 MAC or PBE iteration count of zero or less produced a constant key |

**Signature forgery.** Both signature advisories affect `publicKey.verify()` with the default RSASSA-PKCS1-v1_5 scheme, and the X.509 certificate and PKCS#7 signature verification that use it. The advisories say an attacker can forge a signature "for an arbitrary message that verifies as valid, without the private key" for RSA keys with a low public exponent, and that "Only keys with a small public exponent such as e=3 are practically affected." GHSA-2g46-22mc-6gwp describes itself as an incomplete fix of CVE-2026-33894. The 1.4.1 fix re-encodes the expected DigestInfo and requires a byte-for-byte match.

The 7.5 score does not carry that condition. For an application that never verifies against a low-exponent key, the advisories describe no practical forgery.

**PKCS#12.** The CNA record says `pki.pbe.generatePkcs12Key()` "returned a constant key independent of the password and salt, allowing crafted PKCS#12 input processed by `forge.pkcs12.pkcs12FromAsn1()` to bypass password-based integrity checks." Predictable keys also affected two legacy PBE schemes and PKCS#8 encrypted private key input passed to `forge.pki.decryptPrivateKeyInfo()`. PBES2 and PBKDF2 content is unaffected. This matters for code that opens a `.p12` or `.pfx` file from an untrusted source and treats a successful password check as proof of origin.

CVE-2026-85393 was published by VulnCheck on 2026-09-03 with the range "through 1.4.0", 54 days before the fix reached npm.

Registry facts, `npm view node-forge time` on 2026-11-13: 1.4.0 on 2026-03-24, 1.4.1 on 2026-10-27 04:44 UTC, 1.4.2 on 2026-10-27 14:09 UTC, 1.4.3 on 2026-11-04. `latest` is 1.4.3.

## Am I affected?

```bash
npm ls node-forge                 # every copy in the tree, with the package that pulls it in
grep -n '"node-forge"' package-lock.json
grep -n 'node-forge@' yarn.lock pnpm-lock.yaml 2>/dev/null
```

- Any copy at 1.4.0 or earlier is in the affected range.
- Exposure to forgery needs both: your code, or a dependency, verifies RSA PKCS#1 v1.5 signatures or certificates with node-forge, and a verifying key has public exponent 3. To read a key's exponent: `openssl rsa -pubin -in key.pem -noout -text | grep Exponent`.
- Exposure to the PKCS#12 flaw needs your code to parse PKCS#12 or encrypted PKCS#8 input that an untrusted party supplies.
- A copy used only to generate a development certificate is in range but does not verify attacker input.

## If you are affected

1. Upgrade to node-forge 1.4.1 or later. For a transitive copy, update the parent package, or add an `overrides` (npm) or `resolutions` (yarn) entry for `node-forge` at `^1.4.1`, then reinstall and rerun `npm ls node-forge`.
2. If you verify against an e=3 key and cannot upgrade today, the vendor's workaround is: "Do not use RSA keys with a low public exponent (e=3) for signature verification."
3. If an application accepted signatures or certificates under an e=3 key on an affected version and the result gated access or code loading, review what was accepted during that period.

## Prevention

- [npm hardening](../prevention/npm-hardening.md) and the [package vetting checklist](../prevention/package-vetting-checklist.md): keep lockfiles reviewed and run `npm audit` in CI so a transitive cryptography library does not sit a major fix behind.
- Prefer the platform's `crypto` module or WebCrypto for signature verification in new code. Generated code often reaches for a pure-JavaScript library where the runtime already has one.
- Do not treat a PKCS#12 password check as authentication of the file's source.

## Sources

Single source for the mechanism: the vendor, for its own package. The CNA records are VulnCheck and GitHub.

- [GHSA-6qrw-m8cv-hcxf](https://github.com/digitalbazaar/forge/security/advisories/GHSA-6qrw-m8cv-hcxf), fetched 2026-11-13: published 2026-10-27, affected and patched versions, affected APIs, the quoted sentences, the workaround, the CVE id the page prints.
- [GHSA-2g46-22mc-6gwp](https://github.com/digitalbazaar/forge/security/advisories/GHSA-2g46-22mc-6gwp), fetched 2026-11-13: published 2026-10-27, the incomplete-fix statement, the quoted sentence, the fix.
- [CVE Services: CVE-2026-118782](https://cveawg.mitre.org/api/cve/CVE-2026-118782), fetched 2026-11-13: GitHub CNA, 2026-10-29, the description quoted above, CVSS 3.1 7.5, the reference to GHSA-jc66-7q78-782g.
- [CVE Services: CVE-2026-85393](https://cveawg.mitre.org/api/cve/CVE-2026-85393), fetched 2026-11-13: VulnCheck, 2026-09-03, range through 1.4.0, both scores.
- CVE Services, queried for CVE-2026-119192 on 2026-11-13: `CVE_RECORD_DNE`. The query URL is not linked because it returns 404 while no record exists.
- [GitHub Advisory Database listing, `claude` query](https://github.com/advisories?query=claude+sort%3Apublished-desc), fetched 2026-11-13: the database publication dates of the two rows.
- [npm download counts for node-forge](https://api.npmjs.org/downloads/point/last-week/node-forge), read 2026-11-13: 53,233,919 for 2026-11-06 to 2026-11-12.
- npm registry, `npm view node-forge time` and `dist-tags`, read 2026-11-13: publish times and `latest`.
- Not opened: the GHSA-jc66-7q78-782g vendor page, the 1.4.1 release notes and the fix commit. The PKCS#12 facts come from the CNA record.
