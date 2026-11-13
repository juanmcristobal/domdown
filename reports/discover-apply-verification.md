# Discover & Apply verification report

**Date:** 2026-11-12  
**Branch:** `feature/discover-apply-criteria`  
**Current result:** **PARTIAL**. The corrected contract checks pass on all 33 existing raws: complete public documents match, and Discover/Apply body Markdown matches exactly. E2E coverage remains incomplete for four registered adapters; GitHub Release uses an unfrozen external resource, and the Securelist raw is absent.

## A. Executive summary

- Inspected and processed **33/33** checked-in HTML raws from `tests/real/html/`; all parsed and ran locally without external network access. Total corpus size is 10,417,144 bytes.
- Compared current no-criteria conversion against the isolated base worktree at commit `d2bd5e072200a4c096841ad5e3de03bd0d2488ac`: **0 differences** across Markdown, cleaned HTML, metadata, frontmatter, structured document and warnings.
- Discover → JSON → Apply produced exact Markdown for **33/33** raws. **31/33** also had exact `cleaned_html`; two harmless-to-Markdown but unexplained cleaned DOM differences are recorded below.
- Five registered adapters were exercised with real raws: GitHub, arXiv, Wikipedia, CyberSecurityNews and DailySecu. Real manual overrides recovered content from GitHub, arXiv, Wikipedia and CyberSecurityNews; DailySecu was covered for Discover/replay but no meaningful extraction override was identified.
- The 40 existing real-raw editing/override checks remain in place and pass; 33 contract cases now compare full documents with full documents and Markdown bodies with Markdown bodies.
- Current full suite: **327 passed**. Flake8 and `git diff --check` pass.
- Recommendation: **PARTIAL VERIFICATION**. The corrected output contract passes across the available corpus. Coverage remains incomplete because Medium, BleepingComputer, GBHackers and TheHackerNews have no raw fixtures; GitHub Release external assets could not be frozen; Securelist raw is absent.

The corrected contract section below supersedes the earlier comparison that incorrectly compared a complete API document with the body-only `result.markdown` field.

## B. Raw inventory

All listed inputs are the original `tests/real/html/*.html` files. SHA-256 and byte sizes were computed from disk. The site column uses canonical/OG metadata when available; missing sites are not inferred from filenames. “generic” means no site adapter was matched in the actual run.

| File | Bytes | SHA-256 | Site | Format | Adapter | Observed source features |
|---|---:|---|---|---|---|---|
| `tests/real/html/0xmaz.me_posts_HookChain-A-Deep-Dive-into-Advanced-EDR-Bypass-Techniques.html` | 41,100 | `67381db2b718d6b4c85839a6b6f5eef72e47e56ba1da8c146cef976c648c5992` | 0xmaz.me | HTML | genérico | code:39, images:11, links:80 |
| `tests/real/html/1password.com_blog_as-ai-supercharges-phishing-scams-1password-introduces-built-in-protection.html` | 214,216 | `9fea54e631494716d0d2ed1a9ace1a16e6dd388b398ab44f838ceebdade1898e` | no verificable | HTML | genérico | images:20, links:110 |
| `tests/real/html/404media.co_a-secure-chat-apps-encryption-is-so-bad-it-is-meaningless.html` | 51,670 | `6f0b031314ed1a28598c11f4f555ec0660f4757d297fd96fe91057e3b8518f83` | www.404media.co | HTML | genérico | images:13, links:80 |
| `tests/real/html/acronis_boto_cor_de_rosa_campaign_astaroth_whatsapp_brazil.html` | 416,844 | `4906936cf16751a94db6cde08890a575263351c18d474ee66ebbcdeca8a23445` | www.acronis.com | HTML | genérico | images:34, links:46 |
| `tests/real/html/adnanthekhan_clinejection.html` | 83,976 | `4fc8dc0127cb8e050d2cd5a931055aac8cdf85f39dfcf1e184b95b050324d8a4` | adnanthekhan.com | HTML | genérico | pre:9, code:40, images:10, links:59 |
| `tests/real/html/aikido.dev_blog_axios-npm-compromised-maintainer-hijacked-rat.html` | 350,753 | `f49095d2493d202b701308213e54e05f81c4a29748af27f8c21523d2ff8dd138` | www.aikido.dev | HTML | genérico | pre:9, code:55, images:39, links:217 |
| `tests/real/html/arstechnica.com_security_2026_02_new-airsnitch-attack-breaks-wi-fi-encryption-in-homes-offices-and-enterprises.html` | 193,340 | `f54711c1b1b17c1d51d62d91064a06207e2048d27f961dc19d990ab4a4095a84` | arstechnica.com | HTML | genérico | images:5, links:128 |
| `tests/real/html/arxiv.org_abs_2603.28627.html` | 43,738 | `f317a01d383bce6019746768836b0a2fac2b145220e7cce46346f2778180016e` | arxiv.org | HTML | arxiv | tables:1, textarea:1, images:6, links:73 |
| `tests/real/html/attack.mitre.org_techniques_T1102_001.html` | 90,915 | `6e93c781ee733abef101576a570703a3def05fe094295410c7ad24dce971f5ad` | no verificable | HTML | genérico | tables:4, images:3, links:230 |
| `tests/real/html/blog.alyac.co.kr_5035.html` | 197,430 | `f1e9a77c13cf485401515d7256b134008f53de92f50e698239444c604a8bf9a1` | blog.alyac.co.kr | HTML | genérico | tables:2, textarea:1, images:35, links:49 |
| `tests/real/html/blog.ethiack.com_blog_bypassing-wafs-for-fun-and-js-injection-with-parameter-pollution.html` | 153,240 | `c3c9980c05c132a25cef5b768aa1ba0a5adfb4a77a62c38cb2c95882ac40106f` | blog.ethiack.com | HTML | genérico | tables:3, images:37, links:83 |
| `tests/real/html/blog.gdatasoftware.com_2026_03_38385-acr-stealer-infrastructure.html` | 64,892 | `1e8581d19680cc00ed618df19845ad3c1afc20064a6e4ea1628b02969dce3bb9` | blog.gdatasoftware.com | HTML | genérico | images:20, links:59 |
| `tests/real/html/blog.gdatasoftware.com_2026_03_38399-analysis-kissloader.html` | 62,299 | `3888aebb9b9481941325d2fad8c5738df4e558b581ff2f2bf5ab406cfa013f2c` | blog.gdatasoftware.com | HTML | genérico | tables:1, images:15, links:60 |
| `tests/real/html/bushidotoken.net_2025_02_blackbasta-leaks-lessons-from-ascension.html` | 5,144,108 | `3a674fb6c3c17ff8deac9de395add6993755271099de7e11305a02fa0b70c30d` | blog.bushidotoken.net | HTML | genérico | images:36, links:681 |
| `tests/real/html/cisa.gov_news-events_alerts_2026_03_03_cisa-adds-two-known-exploited-vulnerabilities-catalog.html` | 53,881 | `07f2e8ce9ead47072c215d646f0d26e0b04f2e509b0396577da58c2a32d39967` | www.cisa.gov | HTML | genérico | images:8, links:115 |
| `tests/real/html/cybersecuritynews.com_microsofts-azure-password-spray-attack.html` | 348,623 | `6a700feee292fec438821a09ae84436175441921a1ed7cdc38ed9ae8a7eb6b35` | cybersecuritynews.com | HTML | cybersecuritynews | tables:1, code:1, images:8, links:104 |
| `tests/real/html/dailysecu.com_news_articleView.html_idxno_207575.html` | 78,074 | `14b4fdb4f30d8426c94e1c17e77915d9899cdfb331c2283cf170643b3b93fb1c` | www.dailysecu.com | HTML | dailysecu | images:15, links:76 |
| `tests/real/html/dragos_threat_voltzite.html` | 127,323 | `c6afe9b151d095a1d078ac0f65fa9eca988b7f2992a2b80c50f5e1346e907aa1` | www.dragos.com | HTML | genérico | images:17, links:192 |
| `tests/real/html/elastic.co_security-labs_phantom-in-the-vault.html` | 204,494 | `1bb21b97423db31017e59877c2c057036ececef04ecd7307f747b78111b7a041` | www.elastic.co | HTML | genérico | tables:5, pre:11, code:143, images:1, links:74 |
| `tests/real/html/en.wikipedia.org_wiki_Elliptic-curve_cryptography.html` | 289,346 | `c0efce0361418d41a93668a0c86d71eb46339c466a51ce4111380fa8f5536747` | en.wikipedia.org | HTML | wikipedia | tables:9, code:1, images:60, links:818 |
| `tests/real/html/encryptionconsulting.com_enterprise-guide-to-pqc-migration.html` | 391,121 | `78e33e96698cc05e0845023f3b8fc76ce02df81417256e4839e281ab8891738a` | www.encryptionconsulting.com | HTML | genérico | tables:1, images:13, links:208 |
| `tests/real/html/endorlabs.com_learn_how-ai-sast-traced-data-flows-to-uncover-six-openclaw-vulnerabilities.html` | 273,607 | `ff9f06a9600f5055b56e0ba19bea55b3ed806b88e3427c921be9d79c6f188491` | www.endorlabs.com | HTML | genérico | tables:1, pre:18, code:18, images:19, links:240 |
| `tests/real/html/fortinet.com_corporate_about-us_newsroom_press-releases_2025_fortinet-threat-report-reveals-record-surge-in-automated-cyberattacks.html` | 271,841 | `ffcd7595034aabf5c719cb1e1e4745b19917cecc3eb3f55a1068e399b958c36a` | www.fortinet.com | HTML | genérico | images:45, links:491 |
| `tests/real/html/github.com_BerriAI_litellm_issues_24518.html` | 313,131 | `9209c903f515a8e8af8a8ed139856cc7c089975fe6b69a48c3e0518e62af1261` | github.com | HTML | github | tables:1, code:15, textarea:1, images:2, links:120 |
| `tests/real/html/github.com_PaloAltoNetworks_Unit42-timely-threat-intel_blob_main_2025-12-03-recent-surge-in-ClickFix-activity.txt.html` | 312,022 | `9762ddfc900bf1d3bc5d6a75f9b9c3e29748d1edd5e38900fc1b59d3c02cc00e` | github.com | HTML | github | textarea:1, links:105 |
| `tests/real/html/github.com_nodejs_node_releases_tag_v25.3.0.html` | 232,974 | `2a33f0eb811894723a4e2346018e0a5d2fcd2345c9168c9489d9f9927659fe49` | no verificable | HTML | github | code:10, textarea:1, images:3, links:154 |
| `tests/real/html/nisos.com_blog_dprk-remote-worker-fraud-interview.html` | 147,039 | `ef1fd1b7d3acdfe2ed8d984e69de4d744375fad63450b65260aa4eefa2f3186a` | nisos.com | HTML | genérico | images:3, links:82 |
| `tests/real/html/okta.com_blog_threat-intelligence_vishing-actors-target-microsoft-entra-passkey-enrollment.html` | 2,509 | `b4f6fdbd3deea6bc80fbbf000ff9219cbccc7dedccddf4079e864ba39ff259b3` | www.okta.com | HTML | genérico | tables:1, code:3, links:5 |
| `tests/real/html/safedep.io_malicious-ixpresso-core-npm-rat.html` | 115,208 | `a18ed6b135a1b8b0425ab9d30212aead99d6c1016b0776ee0d1a1dee34164219` | safedep.io | HTML | genérico | tables:3, pre:5, code:103, images:56, links:102 |
| `tests/real/html/socket.dev_blog_jscrambler-supply-chain-attack.html` | 2,911 | `b761df199febb5eb57ecb40adbefefbd35522a1b194eb4930be73b3909d32622` | socket.dev | HTML | genérico | code:8, links:6 |
| `tests/real/html/techzone.bitdefender.com_en_tech-explainers_what-is-dll-sideloading.html` | 31,493 | `4d3f41c93743a4cc796e262a7bcc530d4af5ab987ce6f3abd9870df1298ec34a` | techzone.bitdefender.com | HTML | genérico | images:6, links:33 |
| `tests/real/html/vmray.com_the-redline-thread-that-led-to-a-maritime-bec-infrastructure-cluster.html` | 9,933 | `c87b691dfcf160cd875ae7ca720e2c21118ade378026f53f4925f70c054341bd` | www.vmray.com | HTML | genérico | pre:2, code:2, images:1 |
| `tests/real/html/zimperium.com_blog_over-3000-android-malware-samples-using-multiple-techniques-to-bypass-detection.html` | 103,093 | `c2c5751f245ea90a6346753b805c5564497990ae89227f5b9ba8fa10416985ef` | zimperium.com | HTML | genérico | images:14, links:134 |

Corpus coverage: 33 tables, 54 `<pre>`, 438 `<code>`, 5 `<textarea>`, 555 images and 5,014 links. The corpus contains documents with long bodies and the 5.14 MB BushidoToken HTML. A Securelist HTML raw is not present; Securelist appears only as references in a MITRE fixture.

## C. Compatibility against base

The pre-feature base commit is `d2bd5e072200a4c096841ad5e3de03bd0d2488ac` (`HEAD` and `master` at audit start). An isolated worktree at that commit and the current working tree ran the same 33 raws, same Python 3.12 environment/dependencies, manifest `base_url`, and no-criteria pipeline. GitHub Release `_fetch_release_assets` was disabled in both runs so no request was made.

Compared per raw: `markdown`, `cleaned_html`, `metadata`, `frontmatter`, `document` and `warnings`. **33/33 equal for every field; zero regressions.** Existing snapshots were not changed.

## D. Discover fidelity and replay

The added parametrized test serializes the discovered criteria through the public `to_json()` and `ExtractionCriteria.from_json()`, reruns the same raw, and checks exact Markdown, deterministic criteria/trace over two runs, versioned JSON, in-range node IDs, and trace size below the source document. It passed for all 33 raws.

Observed behavior: root selection and adapter activity are present in trace and the trace references parser-assigned IDs for actual source nodes. The public `criteria.include` records a root selector where available; for GitHub blob extraction the include list is empty and the adapter’s special Markdown route is represented by internal state rather than a portable CSS include. In particular, the trace’s `clean-stage-discard` gives node IDs but does not label individual reasons/selectors, so it is diagnostic but not a full semantic explanation of each heuristic.

Replay results by raw:

| Raw ID | Adapter | Declared replayable | Markdown exact | cleaned_html exact | Limitation / base comparison |
|---|---|---:|---:|---:|---|
| `0xmaz_hookchain_edr_bypass` | genérico | True | True | True | — / ninguna |
| `1password_ai_phishing_protection` | genérico | True | True | True | — / ninguna |
| `404media_secure_chat_encryption` | genérico | True | True | True | — / ninguna |
| `acronis_boto_cor_de_rosa_campaign_astaroth_whatsapp_brazil` | genérico | True | True | True | — / ninguna |
| `adnanthekhan_clinejection` | genérico | True | True | True | — / ninguna |
| `aikido_axios_npm_compromised_maintainer_hijacked_rat` | genérico | True | True | True | — / ninguna |
| `arstechnica_airsnitch_article_chrome` | genérico | True | True | True | — / ninguna |
| `arxiv_2603_28627` | arxiv | True | True | True | — / ninguna |
| `mitre_attack_t1102_001` | genérico | True | True | True | — / ninguna |
| `alyac_taket_shipping_smishing` | genérico | True | True | True | — / ninguna |
| `ethiack_waf_parameter_pollution` | genérico | True | True | False | — / ninguna |
| `gdatasoftware_acr_stealer_infrastructure` | genérico | True | True | True | — / ninguna |
| `gdatasoftware_kiss_loader_analysis` | genérico | True | True | True | — / ninguna |
| `bushidotoken_blackbasta_leaks_lessons_from_ascension` | genérico | True | True | True | — / ninguna |
| `cisa_alert_kev_catalog` | genérico | True | True | True | — / ninguna |
| `cybersecuritynews_azure_password_spray_attack` | cybersecuritynews | True | True | True | — / ninguna |
| `dailysecu_sparrow_enterprise_procurement` | dailysecu | True | True | True | — / ninguna |
| `dragos_threat_voltzite` | genérico | True | True | True | — / ninguna |
| `elastic_phantom_in_the_vault` | genérico | True | True | True | — / ninguna |
| `wikipedia_elliptic_curve_cryptography` | wikipedia | True | True | True | — / ninguna |
| `encryptionconsulting_enterprise_guide_to_pqc_migration` | genérico | True | True | True | — / ninguna |
| `endorlabs_openclaw_ai_sast_vulnerabilities` | genérico | True | True | True | — / ninguna |
| `fortinet_threat_report_automated_cyberattacks` | genérico | True | True | False | — / ninguna |
| `github_issue_security_timeline` | github | True | True | True | — / ninguna |
| `github_blob_release_notes` | github | True | True | True | — / ninguna |
| `node_release_tag_v2530` | github | False | True | True | Fetch remoto de assets requiere el mismo fragmento congelado / ninguna |
| `nisos_remote_worker_fraud` | genérico | True | True | True | — / ninguna |
| `okta_vishing_entra_passkey_enrollment` | genérico | True | True | True | — / ninguna |
| `safedep_malicious_ixpresso_core_npm_rat` | genérico | True | True | True | — / ninguna |
| `socket_jscrambler_supply_chain_attack` | genérico | True | True | True | — / ninguna |
| `bitdefender_dll_sideloading` | genérico | True | True | True | — / ninguna |
| `vmray_redline_maritime_bec_infrastructure_cluster` | genérico | True | True | True | — / ninguna |
| `zimperium_android_malware_bypass_detection` | genérico | True | True | True | — / ninguna |

The raw result records `cleaned_html` mismatch on exactly Ethiack and Fortinet. Both contain peripheral empty wrappers/footer changes after replay. The original Markdown and replay Markdown are exactly equal in both cases. This should be considered a limitation if exact DOM replay is expected.

GitHub release raw `node_release_tag_v2530` is declared non-replayable because `_expand_release_assets()` can request an external expanded-assets fragment (`domdown/adapters/github.py:254-268, 271-296`). The test replaces fetch with an `OSError`; it does not claim end-to-end replay of the external fragment.

## E. Apply: real criterion edits

The test `tests/real/test_discover_apply_verification.py` includes real-raw cases for exclusion, restoration outside the automatic root, root change, unwrap and explicit empty exclusions, plus adapter-owned content recovery.

- **D1/D4 partial edit — PASS.** Raw: `socket_jscrambler_supply_chain_attack`. Discover returns `include=["article"]`; changing only `exclude` to `[".dek"]` invalidates the recorded replay key and the actual `.dek` teaser (“A compromised jscrambler npm release added a malicious preinstall hook…”) is absent from both `cleaned_html` and Markdown, while the independent full-text article paragraph (“A compromised release of the popular…”) remains. This confirms the partial edit is reinterpreted and the explicit exclusion applies to the DOM.
- **D2 recovery — PASS.** Socket `include=[".newsletter"]` emits “Subscribe to our newsletter” and its description, outside auto-selected `article`. GitHub issue `.js-repo-nav` restores the “Issues 1.3k” navigation; arXiv `div.extra-services` restores “Access Paper”; Wikipedia `.hatnote` restores “Further information”; CyberSecurityNews `.td-post-sharing` restores “Copy URL”. Each marker was absent in normal Markdown and present after Apply.
- **D3 root change — PASS.** Socket `.article-body` selects the requested body; title-only heading disappears, article prose remains.
- **D5 unwrap — PASS.** Socket `article` with `unwrap=[".article-body"]` removes that wrapper from cleaned HTML, preserves text and does not duplicate the stable phrase checked.
- **D6 explicit `exclude=[]` — PASS.** Selecting `body` returns the newsletter and related-post content, showing common default extraction filtering does not run on the manual path.
- The original real-raw editing/override checks have 40 collected cases and all pass, including D1/D4 partial exclusion.

No synthetic HTML was used for these functional edits.

## F. Adapter matrix

There are nine default registered adapters. Source: `domdown/_pipeline/runner.py:45-56` and `domdown/adapters/__init__.py`.

| Adapter | Real raw | Discover | Replay | Override | E2E status |
|---|---|---|---|---|---|
| GitHub | Issue, blob, release | Yes | Exact for the three local offline executions; release marked non-replayable due remote assets | Issue navigation recoverable; blob route included in raw replay; release assets unavailable with network disabled | Partial |
| arXiv | `arxiv_2603_28627` | Yes | Exact Markdown | `div.extra-services` “Access Paper” recoverable | Covered |
| Wikipedia | `wikipedia_elliptic_curve_cryptography` | Yes | Exact Markdown | `.hatnote` “Further information” recoverable | Covered |
| CyberSecurityNews | `cybersecuritynews_azure_password_spray_attack` | Yes | Exact Markdown | `.td-post-sharing` “Copy URL” recoverable | Covered |
| DailySecu | `dailysecu_sparrow_enterprise_procurement` | Yes | Exact Markdown | No meaningful conflicting extraction node exercised | Partial |
| Medium | None | Not verified on real raw | Not verified | Not verified | Pending raw |
| BleepingComputer | None | Not verified on real raw | Not verified | Not verified | Pending raw |
| GBHackers | None | Not verified on real raw | Not verified | Not verified | Pending raw |
| TheHackerNews | None | Not verified on real raw | Not verified | Not verified | Pending raw |

No HTTP requests were made. The existing GitHub Release route is intentionally tested with its external fetch stubbed to fail; exact replay needs the same frozen fragment, which is not checked in as a fixture.

## G. Markdown quality

Existing raw corpus feature counts cover tables, code, links, images and textareas. Discover/replay had exact Markdown for each. Four explicit edits recovered content from adapter-controlled regions without replacing the Markdown renderer.

The specifically named `securelist-cloud-infrastructure-isolation-bypass` raw does **not** exist. MITRE’s raw contains references to Securelist, but is not the requested article/widget fixture. Consequently the textarea-to-table issue for that page cannot be reproduced. Other real raws contain five `<textarea>` nodes (arXiv, Alyac, GitHub issue, GitHub blob, GitHub release). No evidence in this audit establishes the reported Securelist renderer regression, so it is not attributed to Criteria. `SKIP_TAGS` behavior and Markdown rendering remain outside the claims made by this report.

## H. Findings

### Medium — DA-01: Discover’s cleaned HTML is not exactly replayed for two raw documents

- **Code:** `domdown/stages/clean.py:115-123` and later renderer/postprocess path; records indicate `clean_root(... apply_extraction_heuristics=recorded_replay)` is responsible for the replay differences.
- **Raw:** `blog.ethiack.com...parameter-pollution.html` and Fortinet threat report.
- **Reproduction:** Discover, replay `criteria.to_json()`, compare `cleaned_html` byte-for-byte.
- **Expected:** exact DOM if claimed; Markdown-only guarantee otherwise.
- **Observed:** cleaned HTML differs; Markdown is exact in both.
- **Impact:** consumers persisting cleaned HTML cannot treat replay as identical DOM output even when criteria is marked replayable.
- **Recommendation:** clarify the replay contract as Markdown-only, or capture the remaining decisions if cleaned DOM equality is intended.

### Low — DA-02: Trace size can be large relative to the criteria

- **Code:** `domdown/_pipeline/runner.py:161-173` and `_trace_node_references()` records a descriptor for every referenced removed node.
- **Raw:** Wikipedia, 289,346 bytes.
- **Reproduction:** serialize `result.trace.to_dict()`.
- **Expected:** a compact diagnostic adequate to explain/replay decisions.
- **Observed:** largest trace is 186,241 bytes, about 64% of raw size; it does not duplicate full HTML but may be costly to persist.
- **Impact:** storage/logging overhead for pages with many removals.
- **Recommendation:** consider opt-in detail or compact ranges/selector summaries in a later change; ensure replay-critical IDs remain separately available.

### Low — DA-03: declared console script points to missing module

- **Code:** `setup.py:41-43` declares `domdown=domdown.cli:main`; current `domdown/cli.py` does not exist.
- **Raw:** not applicable.
- **Reproduction:** inspect package files / attempt CLI entry point.
- **Expected:** CLI should resolve if advertised.
- **Observed:** no CLI implementation file exists; Criteria CLI behavior is therefore not testable. This appears pre-existing and is not a Discover/Apply regression.
- **Recommendation:** track separately; no new CLI contract should be claimed until resolved.

## I. Contract robustness and public API

- Versioned JSON roundtrip is exercised across all 33 raws; invalid selector and schema tests exist in `tests/pipeline/test_pipeline.py` and passed in the full suite.
- `html_to_markdown()` remains a string API; `HtmlToMarkdownPipeline.run()` returns result fields. Public package exports `ExtractionCriteria` and diagnostics from `domdown/__init__.py`.
- New real-raw checks do not cover every requested malformed/reference edge case (e.g. changed HTML with an edited criteria that no longer has its replay key, complex nested unwrap, malformed large documents). Existing unit tests cover some invalid selectors/schema and no-match cases, not the full requested matrix.
- Criteria carry both user-editable CSS and generated replay IDs. `has_recorded_replay` uses a key over include/exclude/unwrap plus internal IDs and metadata. An edit invalidates the key and changes interpretation to the selector path; the Socket partial-exclusion case passed on the real raw.
- CLI is not available because the declared module is missing, as DA-03 records.

## J. Test and lint results

- Baseline/current corpus script: 33 executed per side; all compared fields identical.
- Initial real-raw verification module before the triple-equivalence cases: **40 passed in 113.65s**.
- Initial full suite before the corrected contract cases: **294 passed in 158.76s** on Python 3.12. The latest full suite including the corrected contract cases is reported in section L: 327 passed.
- Flake8: **passed** (`.venv/bin/python -m flake8 domdown tests`).
- `git diff --check`: passed.
- No raw files, snapshots, production files, dependencies or commits were changed for the verification. The implementation files listed as modified in Git status predated this audit; the only files added by the audit are `tests/real/test_discover_apply_verification.py` and this report.

## K. Recommended actions

### Recommended

1. Decide whether “replayable” promises Markdown equality only or exact `cleaned_html`; current evidence supports Markdown equality for all 33 but not cleaned HTML for two.
2. Add checked-in offline fixture coverage for GitHub Release assets if exact replay of expanded assets is required.
3. Add real raws for the four unrepresented adapters if adapter-wide E2E control is an acceptance requirement.
4. Add the Securelist widget raw only if available from the project’s existing licensed/test corpus; this audit did not fetch it.

### Known coverage limitations for this audit

- No HTTP testing was permitted; release fragment route is explicitly non-replayable without frozen resource data.
- Adapter E2E coverage is incomplete despite the full unit suite passing.
- Securelist page-specific issue remains unverified because the raw is absent.


## L. Equivalencia contractual de las salidas

Se confirmaron las interfaces antes de escribir las aserciones:

- `html_to_markdown()` devuelve `result.document or result.markdown` (`domdown/api.py:20`), es decir, el documento completo cuando hay frontmatter.
- `HtmlToMarkdownResult.markdown` es el cuerpo Markdown (`domdown/_core/result.py:14`).
- `HtmlToMarkdownResult.document` es el documento final completo (`result.py:19`), asignado desde `context.rendered_document` al construir el resultado (`domdown/_pipeline/runner.py:200-207`). La etapa de frontmatter compone ese documento a partir del cuerpo y del frontmatter.

La parametrización utiliza los 33 raws de `tests/real/html/` (ningún raw nuevo desde la auditoría anterior) y cuatro ejecuciones independientes con iguales `html`, opciones, `base_url` y entorno:

1. API pública automática.
2. Pipeline Discover.
3. Pipeline Apply con `ExtractionCriteria` deserializado desde el JSON de Discover.
4. API pública Apply con el mismo criterio.

Las instancias de pipeline son independientes. En el raw GitHub Release, la obtención de assets se deshabilitó para todas las rutas; no se realizó ninguna petición de red.

### Resultados

| Comparación | Resultado observado |
|---|---:|
| Automatic == Discover.document | **33/33 exactas** |
| Automatic == Apply.document | **33/33 exactas**; **32/32** de las declaradas reproducibles |
| Automatic == Apply público | **33/33 exactas**; **32/32** de las declaradas reproducibles |
| Discover.markdown == Apply.markdown | **33/33 exactas**; **32/32** de las declaradas reproducibles |
| JSON → Criteria → JSON | **33/33** serializaciones canónicas exactas y estructuralmente iguales |
| Repetición de Automatic y Discover | **33/33** deterministas para salidas, criterio y traza |
| `cleaned_html` idéntico | **31/33**; Ethiack y Fortinet difieren solo en wrappers periféricos, detallados abajo |

El criterio de GitHub Release `node_release_tag_v2530` es el único marcado como no reproducible: GitHub puede cargar assets desde un fragmento externo y no hay un raw local congelado de ese fragmento. Al ejecutar el replay sin red, las salidas coincidieron, pero esa coincidencia observada no se considera garantía. Los otros **32 criterios reproducibles** cumplieron todas las igualdades exactas.

### Resultados por raw

Los SHA-256 del HTML raw están en el inventario de la sección B. Los tests parametrizados tienen ID estable igual al ID de caso indicado aquí.

| Raw | Adaptador | Automatic = Discover.document | Automatic = Apply.document | Automatic = Apply público | Discover.markdown = Apply.markdown | Replayable |
|---|---|---|---|---|---|---|
| `okta_vishing_entra_passkey_enrollment` | genérico | PASS | PASS | PASS | PASS | Sí |
| `socket_jscrambler_supply_chain_attack` | genérico | PASS | PASS | PASS | PASS | Sí |
| `dailysecu_sparrow_enterprise_procurement` | dailysecu | PASS | PASS | PASS | PASS | Sí |
| `zimperium_android_malware_bypass_detection` | genérico | PASS | PASS | PASS | PASS | Sí |
| `404media_secure_chat_encryption` | genérico | PASS | PASS | PASS | PASS | Sí |
| `cybersecuritynews_azure_password_spray_attack` | cybersecuritynews | PASS | PASS | PASS | PASS | Sí |
| `arstechnica_airsnitch_article_chrome` | genérico | PASS | PASS | PASS | PASS | Sí |
| `bitdefender_dll_sideloading` | genérico | PASS | PASS | PASS | PASS | Sí |
| `cisa_alert_kev_catalog` | genérico | PASS | PASS | PASS | PASS | Sí |
| `node_release_tag_v2530` | github | PASS | PASS | PASS | PASS | No |
| `github_issue_security_timeline` | github | PASS | PASS | PASS | PASS | Sí |
| `github_blob_release_notes` | github | PASS | PASS | PASS | PASS | Sí |
| `arxiv_2603_28627` | arxiv | PASS | PASS | PASS | PASS | Sí |
| `wikipedia_elliptic_curve_cryptography` | wikipedia | PASS | PASS | PASS | PASS | Sí |
| `nisos_remote_worker_fraud` | genérico | PASS | PASS | PASS | PASS | Sí |
| `0xmaz_hookchain_edr_bypass` | genérico | PASS | PASS | PASS | PASS | Sí |
| `mitre_attack_t1102_001` | genérico | PASS | PASS | PASS | PASS | Sí |
| `gdatasoftware_acr_stealer_infrastructure` | genérico | PASS | PASS | PASS | PASS | Sí |
| `alyac_taket_shipping_smishing` | genérico | PASS | PASS | PASS | PASS | Sí |
| `bushidotoken_blackbasta_leaks_lessons_from_ascension` | genérico | PASS | PASS | PASS | PASS | Sí |
| `ethiack_waf_parameter_pollution` | genérico | PASS | PASS | PASS | PASS | Sí |
| `gdatasoftware_kiss_loader_analysis` | genérico | PASS | PASS | PASS | PASS | Sí |
| `elastic_phantom_in_the_vault` | genérico | PASS | PASS | PASS | PASS | Sí |
| `fortinet_threat_report_automated_cyberattacks` | genérico | PASS | PASS | PASS | PASS | Sí |
| `endorlabs_openclaw_ai_sast_vulnerabilities` | genérico | PASS | PASS | PASS | PASS | Sí |
| `1password_ai_phishing_protection` | genérico | PASS | PASS | PASS | PASS | Sí |
| `acronis_boto_cor_de_rosa_campaign_astaroth_whatsapp_brazil` | genérico | PASS | PASS | PASS | PASS | Sí |
| `safedep_malicious_ixpresso_core_npm_rat` | genérico | PASS | PASS | PASS | PASS | Sí |
| `aikido_axios_npm_compromised_maintainer_hijacked_rat` | genérico | PASS | PASS | PASS | PASS | Sí |
| `encryptionconsulting_enterprise_guide_to_pqc_migration` | genérico | PASS | PASS | PASS | PASS | Sí |
| `vmray_redline_maritime_bec_infrastructure_cluster` | genérico | PASS | PASS | PASS | PASS | Sí |
| `adnanthekhan_clinejection` | genérico | PASS | PASS | PASS | PASS | Sí |
| `dragos_threat_voltzite` | genérico | PASS | PASS | PASS | PASS | Sí |

### `cleaned_html`

Se mantuvo la comparación de `discovered.cleaned_html` y `applied.cleaned_html`. No forma parte de la igualdad del documento Markdown/API; se reportan las diferencias sin exigir identidad byte a byte.

- **Ethiack** (`tests/real/html/blog.ethiack.com_blog_bypassing-wafs-for-fun-and-js-injection-with-parameter-pollution.html`): Discover conserva un `<footer class="footer">` con sus contenedores vacíos y un control scroll-to-top dentro del wrapper footer. Apply conserva el wrapper exterior `data-global-resource-path`, pero deja su interior vacío. Conteo DOM: 636 tags en Discover, 629 en Apply.
- **Fortinet** (`tests/real/html/fortinet.com_corporate_about-us_newsroom_press-releases_2025_fortinet-threat-report-reveals-record-surge-in-automated-cyberattacks.html`): Discover conserva un `<header class="ftnt-navigation">` vacío con `div.disable-background`, además de wrappers CTA vacíos (`cta--item` / `C32-Text`). Apply elimina esos hijos y conserva algunos padres vacíos. Conteo DOM: 124 tags en Discover, 120 en Apply.
- En ambos raws, el contenido textual extraído y su secuencia/orden son idénticos al comparar los nodos de texto de los HTML limpios. Los diffs solo muestran wrappers de footer/navegación/CTA sin contenido editorial. No se detectó pérdida ni reordenamiento de nodos editoriales; el Markdown también coincide exactamente.

### Adaptadores y límites de cobertura

Los raws que activan adaptadores pasan las cuatro comparaciones contractuales: GitHub (issue, blob y release), arXiv, Wikipedia, CyberSecurityNews y DailySecu. La ruta Release conserva su limitación externa descrita arriba. No hay raw E2E para Medium, BleepingComputer, GBHackers ni TheHackerNews. El fixture Securelist solicitado no existe en el repositorio; solo hay referencias a Securelist dentro del raw MITRE, que no representa la página widget.

### Tests y lint

- Equivalencia contractual parametrizada: **33 passed in 205.84s** (40 casos de edición excluidos de esta selección enfocada).
- Suite completa: **327 passed, 0 failed, 0 skipped** (`368.12s`). Las 40 pruebas de edición real de criterios siguen incluidas y pasan.
- Flake8: **passed** (`.venv/bin/python -m flake8 domdown tests`).
- `git diff --check`: **passed**.

**Clasificación:** **PARTIAL**. Todas las igualdades contractuales requeridas pasan para los 32 criterios reproducibles y también se observó igualdad en el caso externo no reproducible. La verificación E2E de los cuatro adaptadores sin fixture sigue pendiente.
