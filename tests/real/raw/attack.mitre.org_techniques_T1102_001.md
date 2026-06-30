---
title: "Web Service: Dead Drop Resolver, Sub-technique T1102.001 - Enterprise | MITRE ATT&CK®"
language: en
domdown_version: 0.3.0
image: /theme/images/mitre_attack_logo.png
---
# Web Service: Dead Drop Resolver

##### Other sub-techniques of Web Service (3)

- **T1102.002:** <a href="https://attack.mitre.org/techniques/T1102/002/">T1102.002</a>
- **Bidirectional Communication:** <a href="https://attack.mitre.org/techniques/T1102/002/">Bidirectional Communication</a>
- **T1102.003:** <a href="https://attack.mitre.org/techniques/T1102/003/">T1102.003</a>
- **One-Way Communication:** <a href="https://attack.mitre.org/techniques/T1102/003/">One-Way Communication</a>

Adversaries may use an existing, legitimate external Web service to host information that points to additional command and control (C2) infrastructure. Adversaries may post content, known as a dead drop resolver, on Web services with embedded (and often obfuscated/encoded) domains or IP addresses. Once infected, victims will reach out to and be redirected by these resolvers.

Popular websites and social media acting as a mechanism for C2 may give a significant amount of cover due to the likelihood that hosts within a network are already communicating with them prior to a compromise. Using common services, such as those offered by Google or Twitter, makes it easier for adversaries to hide in expected noise. Web service providers commonly use SSL/TLS encryption, giving adversaries an added level of protection.

Use of a dead drop resolver may also protect back-end C2 infrastructure from discovery through malware binary analysis while also enabling operational resiliency (since this infrastructure may be dynamically changed).

- **ID:** T1102.001
- **Platforms:** ESXi, Linux, Windows, macOS
- **Version:** 1.1
- **Created:** 14 March 2020
- **Last Modified:** 12 May 2026

[Version Permalink](https://attack.mitre.org/versions/v19/techniques/T1102/001/)

[Live Version](https://attack.mitre.org/versions/v19/techniques/T1102/001/)

## Procedure Examples

- **C0057:** <a href="https://attack.mitre.org/campaigns/C0057">C0057</a>
- **3CX Supply Chain Attack:** <a href="https://attack.mitre.org/campaigns/C0057">3CX Supply Chain Attack</a>
- **G0096:** <a href="https://attack.mitre.org/groups/G0096">G0096</a>
- **APT41:** <a href="https://attack.mitre.org/groups/G0096">APT41</a>
- **S0373:** <a href="https://attack.mitre.org/software/S0373">S0373</a>
- **Astaroth:** <a href="https://attack.mitre.org/software/S0373">Astaroth</a>
- **S0128:** <a href="https://attack.mitre.org/software/S0128">S0128</a>
- **BADNEWS:** <a href="https://attack.mitre.org/software/S0128">BADNEWS</a>
- **S0069:** <a href="https://attack.mitre.org/software/S0069">S0069</a>
- **BLACKCOFFEE:** <a href="https://attack.mitre.org/software/S0069">BLACKCOFFEE</a>
- **G0060:** <a href="https://attack.mitre.org/groups/G0060">G0060</a>
- **BRONZE BUTLER:** <a href="https://attack.mitre.org/groups/G0060">BRONZE BUTLER</a>
- **C0017:** <a href="https://attack.mitre.org/campaigns/C0017">C0017</a>
- **C0017:** <a href="https://attack.mitre.org/campaigns/C0017">C0017</a>
- **S0674:** <a href="https://attack.mitre.org/software/S0674">S0674</a>
- **CharmPower:** <a href="https://attack.mitre.org/software/S0674">CharmPower</a>
- **S9010:** <a href="https://attack.mitre.org/software/S9010">S9010</a>
- **GlassWorm:** <a href="https://attack.mitre.org/software/S9010">GlassWorm</a>
- **S0531:** <a href="https://attack.mitre.org/software/S0531">S0531</a>
- **Grandoreiro:** <a href="https://attack.mitre.org/software/S0531">Grandoreiro</a>
- **S0528:** <a href="https://attack.mitre.org/software/S0528">S0528</a>
- **Javali:** <a href="https://attack.mitre.org/software/S0528">Javali</a>
- **S1051:** <a href="https://attack.mitre.org/software/S1051">S1051</a>
- **KEYPLUG:** <a href="https://attack.mitre.org/software/S1051">KEYPLUG</a>
- **G0094:** <a href="https://attack.mitre.org/groups/G0094">G0094</a>
- **Kimsuky:** <a href="https://attack.mitre.org/groups/G0094">Kimsuky</a>
- **S0455:** <a href="https://attack.mitre.org/software/S0455">S0455</a>
- **Metamorfo:** <a href="https://attack.mitre.org/software/S0455">Metamorfo</a>
- **S0051:** <a href="https://attack.mitre.org/software/S0051">S0051</a>
- **MiniDuke:** <a href="https://attack.mitre.org/software/S0051">MiniDuke</a>
- **S1221:** <a href="https://attack.mitre.org/software/S1221">S1221</a>
- **MOPSLED:** <a href="https://attack.mitre.org/software/S1221">MOPSLED</a>
- **G0040:** <a href="https://attack.mitre.org/groups/G0040">G0040</a>
- **Patchwork:** <a href="https://attack.mitre.org/groups/G0040">Patchwork</a>
- **S0013:** <a href="https://attack.mitre.org/software/S0013">S0013</a>
- **PlugX:** <a href="https://attack.mitre.org/software/S0013">PlugX</a>
- **S0518:** <a href="https://attack.mitre.org/software/S0518">S0518</a>
- **PolyglotDuke:** <a href="https://attack.mitre.org/software/S0518">PolyglotDuke</a>
- **G0106:** <a href="https://attack.mitre.org/groups/G0106">G0106</a>
- **Rocke:** <a href="https://attack.mitre.org/groups/G0106">Rocke</a>
- **S0148:** <a href="https://attack.mitre.org/software/S0148">S0148</a>
- **RTM:** <a href="https://attack.mitre.org/software/S0148">RTM</a>
- **G0048:** <a href="https://attack.mitre.org/groups/G0048">G0048</a>
- **RTM:** <a href="https://attack.mitre.org/groups/G0048">RTM</a>
- **S1201:** <a href="https://attack.mitre.org/software/S1201">S1201</a>
- **TRANSLATEXT:** <a href="https://attack.mitre.org/software/S1201">TRANSLATEXT</a>
- **S9034:** <a href="https://attack.mitre.org/software/S9034">S9034</a>
- **Tsundere Botnet:** <a href="https://attack.mitre.org/software/S9034">Tsundere Botnet</a>
- **S0341:** <a href="https://attack.mitre.org/software/S0341">S0341</a>
- **Xbash:** <a href="https://attack.mitre.org/software/S0341">Xbash</a>

## Mitigations

- **M1031:** <a href="https://attack.mitre.org/mitigations/M1031">M1031</a>
- **Network Intrusion Prevention:** <a href="https://attack.mitre.org/mitigations/M1031">Network Intrusion Prevention</a>
- **M1021:** <a href="https://attack.mitre.org/mitigations/M1021">M1021</a>
- **Restrict Web-Based Content:** <a href="https://attack.mitre.org/mitigations/M1021">Restrict Web-Based Content</a>

## Detection Strategy

- **DET0058:** <a href="https://attack.mitre.org/detectionstrategies/DET0058">DET0058</a>
- **Detection Strategy for Web Service: Dead Drop Resolver:** <a href="https://attack.mitre.org/detectionstrategies/DET0058">Detection Strategy for Web Service: Dead Drop Resolver</a>
- **AN0158:** AN0158
- **AN0159:** AN0159
- **AN0160:** AN0160
- **AN0161:** AN0161

## References

- **Robert Falcone, Josh Grunzweig. (2023, March 30). Threat Brief: 3CXDesktopApp Supply Chain Attack. Retrieved September 15, 2025.:** <a href="https://unit42.paloaltonetworks.com/3cxdesktopapp-supply-chain-attack/">Robert Falcone, Josh Grunzweig. (2023, March 30). Threat Brief: 3CXDesktopApp Supply Chain Attack. Retrieved September 15, 2025.</a>
- **Jeff Johnson, Fred Plan, Adrian Sanchez, Renato Fontana, Jake Nicastro, Dimiter Andonov, Marius Fodoreanu, Daniel Scott. (2023, April 20). 3CX Software Supply Chain Compromise Initiated by a Prior Software Supply Chain Compromise; Suspected North Korean Actor Responsible. Retrieved August 25, 2025.:** <a href="https://cloud.google.com/blog/topics/threat-intelligence/3cx-software-supply-chain-compromise/">Jeff Johnson, Fred Plan, Adrian Sanchez, Renato Fontana, Jake Nicastro, Dimiter Andonov, Marius Fodoreanu, Daniel Scott. (2023, April 20). 3CX Software Supply Chain Compromise Initiated by a Prior Software Supply Chain Compromise; Suspected North Korean Actor Responsible. Retrieved August 25, 2025.</a>
- **Fraser, N., et al. (2019, August 7). Double DragonAPT41, a dual espionage and cyber crime operation APT41. Retrieved September 23, 2019.:** <a href="https://www.mandiant.com/sites/default/files/2022-02/rt-apt41-dual-operation.pdf">Fraser, N., et al. (2019, August 7). Double DragonAPT41, a dual espionage and cyber crime operation APT41. Retrieved September 23, 2019.</a>
- **GReAT. (2020, July 14). The Tetrade: Brazilian banking malware goes global. Retrieved November 9, 2020.:** <a href="https://securelist.com/the-tetrade-brazilian-banking-malware/97779/">GReAT. (2020, July 14). The Tetrade: Brazilian banking malware goes global. Retrieved November 9, 2020.</a>
- **Settle, A., et al. (2016, August 8). MONSOON - Analysis Of An APT Campaign. Retrieved September 22, 2016.:** <a href="https://www.forcepoint.com/sites/default/files/resources/files/forcepoint-security-labs-monsoon-analysis-report.pdf">Settle, A., et al. (2016, August 8). MONSOON - Analysis Of An APT Campaign. Retrieved September 22, 2016.</a>
- **Levene, B. et al.. (2018, March 7). Patchwork Continues to Deliver BADNEWS to the Indian Subcontinent. Retrieved March 31, 2018.:** <a href="https://researchcenter.paloaltonetworks.com/2018/03/unit42-patchwork-continues-deliver-badnews-indian-subcontinent/">Levene, B. et al.. (2018, March 7). Patchwork Continues to Deliver BADNEWS to the Indian Subcontinent. Retrieved March 31, 2018.</a>
- **Lunghi, D., et al. (2017, December). Untangling the Patchwork Cyberespionage Group. Retrieved July 10, 2018.:** <a href="https://documents.trendmicro.com/assets/tech-brief-untangling-the-patchwork-cyberespionage-group.pdf">Lunghi, D., et al. (2017, December). Untangling the Patchwork Cyberespionage Group. Retrieved July 10, 2018.</a>
- **FireEye Labs/FireEye Threat Intelligence. (2015, May 14). Hiding in Plain Sight: FireEye and Microsoft Expose Obfuscation Tactic. Retrieved November 17, 2024.:** <a href="https://web.archive.org/web/20240119213200/https://www2.fireeye.com/rs/fireye/images/APT17_Report.pdf">FireEye Labs/FireEye Threat Intelligence. (2015, May 14). Hiding in Plain Sight: FireEye and Microsoft Expose Obfuscation Tactic. Retrieved November 17, 2024.</a>
- **FireEye. (2018, March 16). Suspected Chinese Cyber Espionage Group (TEMP.Periscope) Targeting U.S. Engineering and Maritime Industries. Retrieved April 11, 2018.:** <a href="https://www.fireeye.com/blog/threat-research/2018/03/suspected-chinese-espionage-group-targeting-maritime-and-engineering-industries.html">FireEye. (2018, March 16). Suspected Chinese Cyber Espionage Group (TEMP.Periscope) Targeting U.S. Engineering and Maritime Industries. Retrieved April 11, 2018.</a>
- **Counter Threat Unit Research Team. (2017, October 12). BRONZE BUTLER Targets Japanese Enterprises. Retrieved January 4, 2018.:** <a href="https://www.secureworks.com/research/bronze-butler-targets-japanese-businesses">Counter Threat Unit Research Team. (2017, October 12). BRONZE BUTLER Targets Japanese Enterprises. Retrieved January 4, 2018.</a>
- **Rufus Brown, Van Ta, Douglas Bienstock, Geoff Ackerman, John Wolfram. (2022, March 8). Does This Look Infected? A Summary of APT41 Targeting U.S. State Governments. Retrieved July 8, 2022.:** <a href="https://www.mandiant.com/resources/apt41-us-state-governments">Rufus Brown, Van Ta, Douglas Bienstock, Geoff Ackerman, John Wolfram. (2022, March 8). Does This Look Infected? A Summary of APT41 Targeting U.S. State Governments. Retrieved July 8, 2022.</a>
- **Check Point. (2022, January 11). APT35 exploits Log4j vulnerability to distribute new modular PowerShell toolkit. Retrieved January 24, 2022.:** <a href="https://research.checkpoint.com/2022/apt35-exploits-log4j-vulnerability-to-distribute-new-modular-powershell-toolkit/">Check Point. (2022, January 11). APT35 exploits Log4j vulnerability to distribute new modular PowerShell toolkit. Retrieved January 24, 2022.</a>
- **Gal Hachamov. (2025, December 29). GlassWorm Goes Mac: Fresh Infrastructure, New Tricks. Retrieved April 10, 2026.:** <a href="https://www.koi.ai/blog/glassworm-goes-mac-fresh-infrastructure-new-tricks">Gal Hachamov. (2025, December 29). GlassWorm Goes Mac: Fresh Infrastructure, New Tricks. Retrieved April 10, 2026.</a>
- **Idan Dardikman, Yuval Ronen, Lotan Sery. (2025, November 6). GlassWorm Returns: New Wave Strikes as We Expose Attacker Infrastructure. Retrieved April 10, 2026.:** <a href="https://www.koi.ai/blog/glassworm-returns-new-wave-openvsx-malware-expose-attacker-infrastructure">Idan Dardikman, Yuval Ronen, Lotan Sery. (2025, November 6). GlassWorm Returns: New Wave Strikes as We Expose Attacker Infrastructure. Retrieved April 10, 2026.</a>
- **Idan Dardikman. (2025, October 18). GlassWorm: First Self-Propagating Worm Using Invisible Code Hits OpenVSX Marketplace. Retrieved April 10, 2026.:** <a href="https://www.koi.ai/blog/glassworm-first-self-propagating-worm-using-invisible-code-hits-openvsx-marketplace">Idan Dardikman. (2025, October 18). GlassWorm: First Self-Propagating Worm Using Invisible Code Hits OpenVSX Marketplace. Retrieved April 10, 2026.</a>
- **Ilyas Makari. (2025, October 31). The Return of the Invisible Threat: Hidden PUA Unicode Hits GitHub repositorties. Retrieved April 10, 2026.:** <a href="https://www.aikido.dev/blog/the-return-of-the-invisible-threat-hidden-pua-unicode-hits-github-repositorties">Ilyas Makari. (2025, October 31). The Return of the Invisible Threat: Hidden PUA Unicode Hits GitHub repositorties. Retrieved April 10, 2026.</a>
- **Kirill Boychenko. (2026, January 31). GlassWorm Loader Hits Open VSX via Developer Account Compromise. Retrieved April 10, 2026.:** <a href="https://socket.dev/blog/glassworm-loader-hits-open-vsx-via-suspected-developer-account-compromise">Kirill Boychenko. (2026, January 31). GlassWorm Loader Hits Open VSX via Developer Account Compromise. Retrieved April 10, 2026.</a>
- **Lotan Sery. (2025, December 10). GlassWorm Goes Native: Same Infrastructure, Hardened Delivery. Retrieved April 10, 2026.:** <a href="https://www.koi.ai/blog/glassworm-goes-native-same-infrastructure-hardened-delivery">Lotan Sery. (2025, December 10). GlassWorm Goes Native: Same Infrastructure, Hardened Delivery. Retrieved April 10, 2026.</a>
- **Park, S. (2024, June 27). Kimsuky deploys TRANSLATEXT to target South Korean academia. Retrieved October 14, 2024.:** Park, S. (2024, June 27). Kimsuky deploys TRANSLATEXT to target South Korean academia. Retrieved October 14, 2024.
- **ESET Research. (2019, October 3). Casbaneiro: peculiarities of this banking Trojan that affects Brazil and Mexico. Retrieved September 23, 2021.:** <a href="https://www.welivesecurity.com/2019/10/03/casbaneiro-trojan-dangerous-cooking/">ESET Research. (2019, October 3). Casbaneiro: peculiarities of this banking Trojan that affects Brazil and Mexico. Retrieved September 23, 2021.</a>
- **F-Secure Labs. (2015, September 17). The Dukes: 7 years of Russian cyberespionage. Retrieved December 10, 2015.:** <a href="https://www.f-secure.com/documents/996508/1030745/dukes_whitepaper.pdf">F-Secure Labs. (2015, September 17). The Dukes: 7 years of Russian cyberespionage. Retrieved December 10, 2015.</a>
- **Kaspersky Lab's Global Research & Analysis Team. (2013, February 27). The MiniDuke Mystery: PDF 0-day Government Spy Assembler 0x29A Micro Backdoor. Retrieved November 17, 2024.:** <a href="https://web.archive.org/web/20170630181406/https://cdn.securelist.com/files/2014/07/themysteryofthepdf0-dayassemblermicrobackdoor.pdf">Kaspersky Lab&#x27;s Global Research &amp; Analysis Team. (2013, February 27). The MiniDuke Mystery: PDF 0-day Government Spy Assembler 0x29A Micro Backdoor. Retrieved November 17, 2024.</a>
- **Faou, M., Tartare, M., Dupuy, T. (2019, October). OPERATION GHOST. Retrieved September 23, 2020.:** <a href="https://www.welivesecurity.com/wp-content/uploads/2019/10/ESET_Operation_Ghost_Dukes.pdf">Faou, M., Tartare, M., Dupuy, T. (2019, October). OPERATION GHOST. Retrieved September 23, 2020.</a>
- **Punsaen Boonyakarn, Shawn Chew, Logeswaran Nadarajan, Mathew Potaczek, Jakub Jozwiak, and Alex Marvi. (2024, June 18). Cloaked and Covert: Uncovering UNC3886 Espionage Operations. Retrieved September 24, 2024.:** <a href="https://cloud.google.com/blog/topics/threat-intelligence/uncovering-unc3886-espionage-operations">Punsaen Boonyakarn, Shawn Chew, Logeswaran Nadarajan, Mathew Potaczek, Jakub Jozwiak, and Alex Marvi. (2024, June 18). Cloaked and Covert: Uncovering UNC3886 Espionage Operations. Retrieved September 24, 2024.</a>
- **Kaspersky Lab's Global Research & Analysis Team. (2016, July 8). The Dropping Elephant – aggressive cyber-espionage in the Asian region. Retrieved August 3, 2016.:** <a href="https://securelist.com/the-dropping-elephant-actor/75328/">Kaspersky Lab&#x27;s Global Research &amp; Analysis Team. (2016, July 8). The Dropping Elephant – aggressive cyber-espionage in the Asian region. Retrieved August 3, 2016.</a>
- **Lancaster, T. and Idrizovic, E.. (2017, June 27). Paranoid PlugX. Retrieved July 13, 2017.:** <a href="https://researchcenter.paloaltonetworks.com/2017/06/unit42-paranoid-plugx/">Lancaster, T. and Idrizovic, E.. (2017, June 27). Paranoid PlugX. Retrieved July 13, 2017.</a>
- **Anomali Labs. (2019, March 15). Rocke Evolves Its Arsenal With a New Malware Family Written in Golang. Retrieved April 24, 2019.:** <a href="https://www.anomali.com/blog/rocke-evolves-its-arsenal-with-a-new-malware-family-written-in-golang">Anomali Labs. (2019, March 15). Rocke Evolves Its Arsenal With a New Malware Family Written in Golang. Retrieved April 24, 2019.</a>
- **Faou, M. and Boutin, J. (2017, February). Read The Manual: A Guide to the RTM Banking Trojan. Retrieved March 9, 2017.:** <a href="https://www.welivesecurity.com/wp-content/uploads/2017/02/Read-The-Manual.pdf">Faou, M. and Boutin, J. (2017, February). Read The Manual: A Guide to the RTM Banking Trojan. Retrieved March 9, 2017.</a>
- **Eisenkraft, K., Olshtein, A. (2019, October 17). Pony’s C&C servers hidden inside the Bitcoin blockchain. Retrieved June 15, 2020.:** <a href="https://research.checkpoint.com/2019/ponys-cc-servers-hidden-inside-the-bitcoin-blockchain/">Eisenkraft, K., Olshtein, A. (2019, October 17). Pony’s C&amp;C servers hidden inside the Bitcoin blockchain. Retrieved June 15, 2020.</a>
- **Duncan, B., Harbison, M. (2019, January 23). Russian Language Malspam Pushing Redaman Banking Malware. Retrieved June 16, 2020.:** <a href="https://unit42.paloaltonetworks.com/russian-language-malspam-pushing-redaman-banking-malware/">Duncan, B., Harbison, M. (2019, January 23). Russian Language Malspam Pushing Redaman Banking Malware. Retrieved June 16, 2020.</a>
- **Ubiedo, L. (2025, November 20). Blockchain and Node.js abused by Tsundere: an emerging botnet. Retrieved April 6, 2026.:** <a href="https://securelist.com/tsundere-node-js-botnet-uses-ethereum-blockchain/117979/">Ubiedo, L. (2025, November 20). Blockchain and Node.js abused by Tsundere: an emerging botnet. Retrieved April 6, 2026.</a>
- **Ctrl-Alt-Intel. (2026, March 4). MuddyWater Exposed: Inside an Iranian APT operation . Retrieved April 6, 2026.:** <a href="https://ctrlaltintel.com/research/MuddyWater/">Ctrl-Alt-Intel. (2026, March 4). MuddyWater Exposed: Inside an Iranian APT operation . Retrieved April 6, 2026.</a>
- **Xiao, C. (2018, September 17). Xbash Combines Botnet, Ransomware, Coinmining in Worm that Targets Linux and Windows. Retrieved November 14, 2018.:** <a href="https://researchcenter.paloaltonetworks.com/2018/09/unit42-xbash-combines-botnet-ransomware-coinmining-worm-targets-linux-windows/">Xiao, C. (2018, September 17). Xbash Combines Botnet, Ransomware, Coinmining in Worm that Targets Linux and Windows. Retrieved November 14, 2018.</a>