---
title: "[Security]: litellm PyPI package (v1.82.7 + v1.82.8) compromised — full timeline and status · Issue #24518"
source: "https://github.com/BerriAI/litellm/issues/24518"
author:
  - "isfinne"
description: The Trivy supply-chain compromise has been contained 🎉 . All affected packages have been deleted and current releases are free of the compromised code/component. Please refer to our Security Townhall for a deeper understanding of the pro...
---
## The Trivy supply-chain compromise has been contained 🎉 . All affected packages have been deleted and current releases are free of the compromised code/component. Please refer to our [Security Townhall](https://docs.litellm.ai/blog/security-townhall-updates) for a deeper understanding of the problem, and [CI/CD v2](https://docs.litellm.ai/blog/ci-cd-v2-improvements) for how we're improving moving forward.

[LITELLM TEAM UPDATES]

- Compromised packages have been deleted (v1.82.7, v1.82.8)
- Compromise came from trivvy security scan dependency
- All maintainer accounts have been rotated (new maintainer accounts: [@krrish-berri-2](https://github.com/krrish-berri-2) , [@ishaan-berri](https://github.com/ishaan-berri))
- Proxy Docker image users were **not impacted**, all dependencies are pinned on requirements.txt
- No litellm releases will be out until we have scanned our chain and make sure it's safe

Next Steps

- Review all berriai repo's for impact
- Scan circle ci builds to understand blast radius, and mitigate it
- We've engaged Google's [mandiant.security](https://cloud.google.com/security/mandiant) team, and are actively working on this with them

We are actively investigating this issue. Please reach out to us on [support@berri.ai](mailto:support@berri.ai), if you have any questions / concerns.

## Summary

The litellm PyPI package was compromised by an attacker who gained access to the maintainer's PyPI account. Malicious versions were published that steal credentials and exfiltrate them to an attacker-controlled server.

Original detailed analysis: [#24512](https://github.com/BerriAI/litellm/issues/24512)

Hacker News discussion: [https://news.ycombinator.com/item?id=47501729](https://news.ycombinator.com/item?id=47501729)

## What happened

- The maintainer's PyPI account (`krrishdholakia`) appears to have been hijacked by an attacker (`teampcp`)
- The attacker published malicious versions to PyPI that were never released through the official GitHub CI/CD
- GitHub releases only go up to `v1.82.6.dev1` — versions 1.82.7 and 1.82.8 on PyPI were uploaded directly by the attacker

## Affected versions

| Version | Method | Trigger |
| --- | --- | --- |
| 1.82.7 | Payload embedded in `litellm/proxy/proxy_server.py` | Triggered on `import litellm.proxy` |
| 1.82.8 | Added `litellm_init.pth` (34,628 bytes) + payload in `proxy_server.py` | **Any Python startup** — no import needed |

Other versions may also be affected and should be audited.

## What the malicious code does

1. **Collects**: SSH keys, environment variables (API keys, secrets), AWS/GCP/Azure/K8s credentials, crypto wallets, database passwords, SSL private keys, shell history, CI/CD configs
2. **Encrypts**: AES-256-CBC + RSA-4096 (hardcoded public key)
3. **Exfiltrates**: `curl POST` to `https://models.litellm.cloud/`

The exfiltration domain `litellm.cloud` (NOT the official `litellm.ai`) was registered on **2026-03-23** via Spaceship, Inc. — just hours before the malicious packages appeared.

## Current status

- **PyPI**: The entire litellm package has been suspended/removed. All versions currently return "No matching distribution found." We reported the malware to PyPI via the official "Report malware" form.
- **GitHub Issue [[Security]: CRITICAL: Malicious litellm_init.pth in litellm 1.82.8 — credential stealer #24512](https://github.com/BerriAI/litellm/issues/24512)**: Contains the original detailed technical analysis (currently closed by the attacker's spam — see below).
- **Attacker behavior**: The attacker appears to be publishing hundreds of spam comments to suppress discussion. If this continues, we recommend moderating via the Hacker News thread linked above.

## Recommendations for affected users

1. Check if `litellm_init.pth` exists in your `site-packages/` directory
2. **Rotate ALL credentials** that were present as environment variables or config files on any system where litellm 1.82.7+ was installed
3. Pin dependencies to exact versions and verify against GitHub releases
4. Monitor for unauthorized access using any potentially leaked credentials

## References

- Original analysis: [[Security]: CRITICAL: Malicious litellm_init.pth in litellm 1.82.8 — credential stealer #24512](https://github.com/BerriAI/litellm/issues/24512)
- Hacker News: [https://news.ycombinator.com/item?id=47501729](https://news.ycombinator.com/item?id=47501729)
- Attacker's exfil domain WHOIS: registered 2026-03-23, Spaceship Inc., privacy-protected
- `litellm_init.pth` SHA256: `ceNa7wMJnNHy1kRnNCcwJaFjWX3pORLfMh7xGL8TUjg`