---
title: "Release 2026-01-13, Version 25.3.0 (Current), @RafaelGSS"
source: "https://github.com/nodejs/node/releases/tag/v25.3.0"
author:
  - "nodejs"
description: Node.js JavaScript runtime ✨🐢🚀✨. Contribute to nodejs/node development by creating an account on GitHub.
---
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

- [[a6a74b89a7](https://github.com/nodejs/node/commit/a6a74b89a7)] - **deps**: update c-ares to v1.34.6 (Node.js GitHub Bot) [#60997](https://github.com/nodejs/node/pull/60997)
- [[5100614e26](https://github.com/nodejs/node/commit/5100614e26)] - **deps**: update undici to 7.18.2 (Node.js GitHub Bot) [#61283](https://github.com/nodejs/node/pull/61283)
- [[f0a8916887](https://github.com/nodejs/node/commit/f0a8916887)] - **([CVE-2025-59465](https://github.com/advisories/GHSA-w2pg-hw7v-f7m9))** **lib**: add TLSSocket default error handler (RafaelGSS) [nodejs-private/node-private#750](https://github.com/nodejs-private/node-private/pull/750)
- [[b4b887c5f7](https://github.com/nodejs/node/commit/b4b887c5f7)] - **([CVE-2025-55132](https://github.com/advisories/GHSA-pm9v-wcw9-xgpv))** **lib**: disable futimes when permission model is enabled (RafaelGSS) [nodejs-private/node-private#748](https://github.com/nodejs-private/node-private/pull/748)
- [[26be208039](https://github.com/nodejs/node/commit/26be208039)] - **([CVE-2025-55130](https://github.com/advisories/GHSA-62wc-jj78-f4f6))** **lib,permission**: require full read and write to symlink APIs (RafaelGSS) [nodejs-private/node-private#760](https://github.com/nodejs-private/node-private/pull/760)
- [[bdf5873d44](https://github.com/nodejs/node/commit/bdf5873d44)] - **([CVE-2026-21636](https://github.com/advisories/GHSA-7xhv-hcmf-4rfv))** **permission**: add network check on pipe_wrap connect (RafaelGSS) [nodejs-private/node-private#784](https://github.com/nodejs-private/node-private/pull/784)
- [[0578e3e921](https://github.com/nodejs/node/commit/0578e3e921)] - **([CVE-2025-59466](https://github.com/advisories/GHSA-52xj-vx8w-46qj))** **src**: rethrow stack overflow exceptions in async_hooks (Matteo Collina) [nodejs-private/node-private#773](https://github.com/nodejs-private/node-private/pull/773)
- [[4d6b55a6d1](https://github.com/nodejs/node/commit/4d6b55a6d1)] - **([CVE-2025-55131](https://github.com/advisories/GHSA-9jwr-p39p-hwg2))** **src,lib**: refactor unsafe buffer creation to remove zero-fill toggle (Сковорода Никита Андреевич) [nodejs-private/node-private#759](https://github.com/nodejs-private/node-private/pull/759)
- [[c357a39e14](https://github.com/nodejs/node/commit/c357a39e14)] - **([CVE-2026-21637](https://github.com/advisories/GHSA-ggxc-26fx-987r))** **tls**: route callback exceptions through error handlers (Matteo Collina) [nodejs-private/node-private#790](https://github.com/nodejs-private/node-private/pull/790)