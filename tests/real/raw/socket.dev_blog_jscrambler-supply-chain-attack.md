---
title: jscrambler npm Package Compromised in Supply Chain Attack
source: "https://socket.dev/blog/jscrambler-supply-chain-attack"
site_name: Socket
canonical_url: "https://socket.dev/blog/jscrambler-supply-chain-attack"
domdown_version: 0.3.4
published: 2026-07-11
description: "A compromised jscrambler npm release added a malicious preinstall hook that runs hidden native binaries on Linux, macOS, and Windows."
---
# jscrambler npm Package Compromised in Supply Chain Attack

A compromised jscrambler npm release added a malicious preinstall hook that runs hidden native binaries on Linux, macOS, and Windows.

A compromised release of the popular [jscrambler npm package](https://www.npmjs.com/package/jscrambler) introduced hidden native binaries that execute automatically during `npm install`.

The malicious 8.14.0 release adds an undocumented `preinstall` hook that invokes `dist/setup.js`. It also introduces platform-specific binaries embedded in an obfuscated CSI container.

## Impact

Simply installing `jscrambler@8.14.0` is enough to trigger the bundled platform-specific binary. Users do not need to import the package or run the CLI.

## Technical Analysis

The compromised version ships two malicious files under `dist/`.

1. Reads the container.
2. Selects the blob matching `process.platform`.
3. Launches the native executable in the background.

## Indicators of Compromise

- `jscrambler@8.14.0`
- `jscrambler@8.16.0`