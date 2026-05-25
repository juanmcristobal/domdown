---
title: "axios compromised on npm: maintainer account hijacked, RAT deployed"
source: "https://www.aikido.dev/blog/axios-npm-compromised-maintainer-hijacked-rat"
canonical_url: "https://www.aikido.dev/blog/axios-npm-compromised-maintainer-hijacked-rat"
language: en
image: "https://cdn.prod.website-files.com/642adcaf364024654c71df23/69cb517f68773d10396bd924_Group%202147256681.png"
description: Malicious axios versions 1.14.1 and 0.30.4 were published via a hijacked maintainer account. A hidden dependency deploys a cross-platform RAT. Check if you are affected and remediate now.
---
# axios compromised on npm: maintainer account hijacked, RAT deployed

## Key takeaways

- The npm account of the lead axios maintainer was hijacked. Two malicious versions were published: `axios@1.14.1` and `axios@0.30.4`. npm has since removed both.
- Anyone who installed either version before the takedown should assume their system is compromised. The malicious versions inject a dependency (`plain-crypto-js`) that deploys a cross-platform remote access trojan targeting macOS, Windows, and Linux.
- axios has ~100 million weekly downloads. This is one of the most impactful npm supply chain attacks on record.
- The malware self-destructs after execution, so post-infection inspection of `node_modules` will not reveal it. You need to check your logfiles.

Credit to the great coverage of this incident by:

- StepSecurity ([https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan](https://www.stepsecurity.io/blog/axios-compromised-on-npm-malicious-versions-drop-remote-access-trojan))
- Socket ([https://socket.dev/blog/axios-npm-package-compromised](https://socket.dev/blog/axios-npm-package-compromised))

## How to check if you are affected by the axios attack

### Option 1) Check manually

#### 1. Check for malicious axios versions

Scans your installed packages and lock file for `1.14.1` or `0.30.4`.

```bash
npm list axios 2>/dev/null | grep -E "1\.14\.1|0\.30\.4"
grep -A1 '"axios"' package-lock.json | grep -E "1\.14\.1|0\.30\.4"
```

#### 2. Check for the hidden dropper package

Even if `setup.js` self-deleted, the directory still exists. Its presence alone confirms the dropper ran.

```bash
ls node_modules/plain-crypto-js 2>/dev/null && echo "POTENTIALLY AFFECTED"
```

#### 3. Check for RAT artifacts on disk

**macOS**

```bash
ls -la /Library/Caches/com.apple.act.mond 2>/dev/null && echo "COMPROMISED"
```

**Windows**

```javascript
dir "%PROGRAMDATA%\wt.exe" 2>nul && echo COMPROMISED
```

**Linux**

```javascript
ls -la /tmp/ld.py 2>/dev/null && echo "COMPROMISED"
```

### Option 2) Use Aikido (free)

Connect your repositories to Aikido ([https://app.aikido.dev](https://app.aikido.dev)). Aikido's Malware Monitor compares your dependencies against Aikido Intel's live malware feed. If`axios@1.14.1`, `axios@0.30.4`, or `plain-crypto-js@4.2.1` is present in any of your projects, Aikido flags it immediately. This works on the free tier.

[Check if your code is affected by the Axios supply chain attack - scan it free with Aikido](https://app.aikido.dev)

### Remediation steps

1. Pin to safe versions:

```bash
npm install axios@1.14.0   # 1.x users
npm install axios@0.30.3   # 0.x users
```

1. Add overrides to prevent transitive resolution:

```json
{
  "dependencies": { "axios": "1.14.0" },
  "overrides":    { "axios": "1.14.0" },
  "resolutions":  { "axios": "1.14.0" }
}
```

1. Remove `plain-crypto-js` from node_modules:

```bash
rm -rf node_modules/plain-crypto-js
npm install --ignore-scripts
```

1. If any RAT artifact is found (`com.apple.act.mond`, `wt.exe`, `ld.py`), do not attempt to clean in place. Rebuild from a known-good state.
2. Rotate all credentials accessible on the affected system: npm tokens, AWS access keys, SSH private keys, CI/CD secrets, `.env` values.
3. Audit CI/CD pipeline logs for any runs that installed the affected versions. Rotate all injected secrets.
4. Run `npm ci --ignore-scripts` as a standing policy in CI/CD.

## What happened in the axios supply chain attack

The attacker compromised the `jasonsaayman` npm account, the primary maintainer of axios. The account email was changed to `ifstap@proton.me`. The attacker then published `axios@1.14.1` at 00:21 UTC on March 31 and `axios@0.30.4` at 01:00 UTC. Both the 1.x and legacy 0.x branches were hit within 39 minutes.

Neither version had a corresponding commit, tag, or release in the axios GitHub repository. Legitimate axios releases are published via GitHub Actions with OIDC Trusted Publisher binding. These were published manually with a stolen npm access token.

The only change in both versions was the addition of `plain-crypto-js@^4.2.1` as a dependency. This package is never imported anywhere in the axios source. It exists solely to run a postinstall hook that deploys a RAT.

The dependency was pre-staged ~18 hours earlier by a separate attacker account (`nrwise`, `nrwise@proton.me`). A clean decoy version (`4.2.0`) was published first to build registry history, followed by the malicious `4.2.1` at 23:59 UTC on March 30.

The RAT dropper (setup.js) contacts `sfrclak[.]com:8000` and delivers platform-specific payloads: a macOS binary disguised as an Apple cache daemon at `/Library/Caches/com.apple.act.mond`, a PowerShell script on Windows run via hidden VBScript with the interpreter copied to `%PROGRAMDATA%\wt.exe`, and a Python script on Linux at `/tmp/ld.py`. After execution, the dropper deletes itself and replaces its own `package.json` with a clean stub to hide evidence.

## Indicators of compromise (IOCs)

Malicious axios versions and dependencies:

- `axios@1.14.1` (shasum: `2553649f2322049666871cea80a5d0d6adc700ca`)
- `axios@0.30.4` (shasum: `d6f3f62fd3b9f5432f5782b62d8cfd5247d5ee71`)
- `plain-crypto-js@4.2.1` (shasum: `07d889e2dadce6f3910dcbc253317d28ca61c766`)

Network:

- C2: `sfrclak[.]com` / `142.11.206[.]73` / `http://sfrclak[.]com:8000/6202033`

File system:

- macOS: `/Library/Caches/com.apple.act.mond`‍
  - sha256: `92ff08773995ebc8d55ec4b8e1a225d0d1e51efa4ef88b8849d0071230c9645a`
- Windows: `%PROGRAMDATA%\wt.exe, %TEMP%\6202033.vbs, %TEMP%\6202033.ps1`
  - sha256: `617b67a8e1210e4fc87c92d1d1da45a2f311c08d26e89b12307cf583c900d101` (powershell)
- Linux: `/tmp/ld.py`‍
  - sha256: `fcb81618bb15edfdedfb638b4c08a2af9cac9ecfa551af135a8402bf980375cf`

Attacker accounts:

- jasonsaayman: compromised axios maintainer, email changed to [ifstap@proton.me](mailto:ifstap@proton.me)
- nrwise: attacker-created, [nrwise@proton.me](mailto:nrwise@proton.me)

## How to protect against installing malware

Aikido Safe Chain ([https://github.com/AikidoSec/safe-chain](https://github.com/AikidoSec/safe-chain)) is an open-source tool that wraps around npm, yarn, and pnpm. It checks every package against Aikido Intel's malware feed before it reaches your machine and enforces a configurable minimum package age (48 hours by default), suppressing newly published versions until they have been validated. In this axios attack, `plain-crypto-js@4.2.1`existed for less than 24 hours before the compromised axios versions pulled it in. Safe Chain's age check alone would have blocked it.

Free, no tokens required:

```javascript
curl -fsSL https://github.com/AikidoSec/safe-chain/releases/latest/download/install-safe-chain.sh | sh
```