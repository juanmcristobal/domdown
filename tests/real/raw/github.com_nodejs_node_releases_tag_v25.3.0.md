---
title: "Release 2026-01-13, Version 25.3.0 (Current), @RafaelGSS"
source: "https://github.com/nodejs/node/releases/tag/v25.3.0"
site_name: GitHub
canonical_url: "https://github.com/nodejs/node/releases/tag/v25.3.0"
language: en
domdown_version: 0.3.4
image: "https://opengraph.githubassets.com/efa7f03b81513177fe5d385f4de109fc9211c7055f248ab871081ae941f8eb73/nodejs/node/releases/tag/v25.3.0"
author:
  - "nodejs"
description: Node.js JavaScript runtime ✨🐢🚀✨. Contribute to nodejs/node development by creating an account on GitHub.
---
/

[node](https://github.com/nodejs/node)

Public

- [Notifications](https://github.com/login?return_to=%2Fnodejs%2Fnode) You must be signed in to change notification settings
- [Fork 35.5k](https://github.com/login?return_to=%2Fnodejs%2Fnode)
- [Star](https://github.com/login?return_to=%2Fnodejs%2Fnode)

# 2026-01-13, Version 25.3.0 (Current), @RafaelGSS

![@marco-ippolito](https://avatars.githubusercontent.com/u/36735501?s=40&v=4)

[marco-ippolito](https://github.com/marco-ippolito)

released this

13 Jan 13:58

·

[1580 commits](https://github.com/nodejs/node/compare/v25.3.0...main)

to main since this release

[v25.3.0](https://github.com/nodejs/node/tree/v25.3.0)

[00d6cd8](https://github.com/nodejs/node/commit/00d6cd83927d6d5c8fe9d0cdd101daa6df4b1a15)

This is a security release.

### Notable Changes

lib:

- ([CVE-2025-59465](https://github.com/advisories/GHSA-w2pg-hw7v-f7m9)) add TLSSocket default error handler (RafaelGSS) [nodejs-private/node-private#750](https://github.com/nodejs-private/node-private/pull/750) permission:
- ([CVE-2026-21636](https://github.com/advisories/GHSA-7xhv-hcmf-4rfv)) add network check on pipe_wrap connect (RafaelGSS) [nodejs-private/node-private#784](https://github.com/nodejs-private/node-private/pull/784)
- ([CVE-2025-55130](https://github.com/advisories/GHSA-62wc-jj78-f4f6)) require full read and write to symlink APIs (RafaelGSS) [nodejs-private/node-private#760](https://github.com/nodejs-private/node-private/pull/760)
- ([CVE-2025-55132](https://github.com/advisories/GHSA-pm9v-wcw9-xgpv)) disable futimes when permission model is enabled (RafaelGSS) [nodejs-private/node-private#748](https://github.com/nodejs-private/node-private/pull/748) src:
- ([CVE-2025-59466](https://github.com/advisories/GHSA-52xj-vx8w-46qj)) rethrow stack overflow exceptions in async_hooks (Matteo Collina) [nodejs-private/node-private#773](https://github.com/nodejs-private/node-private/pull/773) src,lib:
- ([CVE-2025-55131](https://github.com/advisories/GHSA-9jwr-p39p-hwg2)) refactor unsafe buffer creation to remove zero-fill toggle (Сковорода Никита Андреевич) [nodejs-private/node-private#759](https://github.com/nodejs-private/node-private/pull/759) tls:
- ([CVE-2026-21637](https://github.com/advisories/GHSA-ggxc-26fx-987r)) route callback exceptions through error handlers (Matteo Collina) [nodejs-private/node-private#790](https://github.com/nodejs-private/node-private/pull/790)

### Commits

### Assets

- [Source code (zip)](https://github.com/nodejs/node/archive/refs/tags/v25.3.0.zip) 2026-01-13T12:49:52Z
- [Source code (tar.gz)](https://github.com/nodejs/node/archive/refs/tags/v25.3.0.tar.gz) 2026-01-13T12:49:52Z