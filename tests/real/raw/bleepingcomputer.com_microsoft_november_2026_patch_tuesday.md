---
title: "Microsoft November 2026 Patch Tuesday fixes 1,235 flaws, Outlook zero-day"
source: "https://www.bleepingcomputer.com/news/microsoft/microsoft-november-2026-patch-tuesday-fixes-1-235-flaws-outlook-zero-day/"
site_name: BleepingComputer
canonical_url: "https://www.bleepingcomputer.com/news/microsoft/microsoft-november-2026-patch-tuesday-fixes-1-235-flaws-outlook-zero-day/"
language: en-us
domdown_version: 0.3.8
image: "https://www.bleepstatic.com/content/hl-images/2024/10/08/patch_tuesday_microsoft.jpg"
author:
  - "Lawrence Abrams"
description: "Today is Microsoft's November 2026 Patch Tuesday, with security updates addressing a record-breaking 1,235 flaws, including one actively exploited Microsoft Outlook zero-day vulnerability."
tags:
  - Microsoft
  - Patch Tuesday
  - Security Update
  - Vulnerability
  - Windows
  - Zero-Day
---
# Microsoft November 2026 Patch Tuesday fixes 1,235 flaws, Outlook zero-day

By

- [2](https://www.bleepingcomputer.com/news/microsoft/microsoft-november-2026-patch-tuesday-fixes-1-235-flaws-outlook-zero-day/#comments)

![Patch Tuesday](https://www.bleepstatic.com/content/hl-images/2024/10/08/patch_tuesday_microsoft.jpg)

Today is Microsoft's November 2026 Patch Tuesday, with security updates addressing a record-breaking 1,235 flaws, including one actively exploited Microsoft Outlook zero-day vulnerability.

This Patch Tuesday addresses 66 "Critical" vulnerabilities, 48 of which are Remote Code Execution (RCE), 15 are Elevation of Privilege (EoP), and three are Use-After-Free in Microsoft Edge.

The approximate number of bugs in each vulnerability category is listed below:

- 536 Elevation of Privilege Vulnerabilities
- 27 Security Feature Bypass Vulnerabilities
- 296 Remote Code Execution Vulnerabilities
- 157 Information Disclosure Vulnerabilities
- 46 Denial of Service Vulnerabilities
- 22 Spoofing Vulnerabilities
- 142 Microsoft Edge (Chromium-based) Vulnerabilities

Of the 1,235 vulnerabilities, approximately 639 are categorized under Windows or Microsoft Windows products/components.

When BleepingComputer reports on Patch Tuesday security updates, we only count vulnerabilities released by Microsoft on Patch Tuesday itself.

Therefore, today's total excludes 108 flaws fixed earlier this month, including one Entra Device Registration, 82 Mariner, and 25 Microsoft Edge flaws.

November's Patch Tuesday comes after a record-breaking [1,411 flaws in the October updates](https://www.bleepingcomputer.com/news/microsoft/microsoft-october-2026-patch-tuesday-fixes-1-411-flaws-3-zero-days/) as Microsoft continues to use AI to find and patch vulnerabilities.

## Microsoft patches 1 zero-days

This month's Patch Tuesday fixes one zero-day vulnerability in Microsoft Outlook that was exploited in attacks.

Microsoft [classifies a zero-day flaw](https://learn.microsoft.com/en-us/defender-vulnerability-management/tvm-zero-day-vulnerabilities) as publicly disclosed or actively exploited when no official fix is available.

The actively exploited zero-day vulnerability addressed in the November 2026 Patch Tuesday updates is:

**[CVE-2026-124194 - Microsoft Outlook Spoofing Vulnerability](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124194)**

Microsoft patched a Microsoft Outlook Spoofing zero-day vulnerability that was actively exploited in attacks to steal NTLM account hashes.

"An unauthenticated attacker could send a specially crafted message file and convince a user to open it in an affected version of Microsoft Outlook," warns Microsoft.

"Opening the file could cause Outlook to connect to an attacker-controlled network location without displaying the usual external-content warning, potentially disclosing authentication information that could be used to impersonate the user. Exploitation requires network connectivity and user interaction."

This type of vulnerability is known as an NTLM credential disclosure flaw, where a malicious attachment, when opened, causes Windows to connect to an attacker-controlled network share.

When connecting, Windows may automatically attempt to authenticate to the remote server, exposing the user's NTLMv2 authentication hash, which can then be captured by the attacker and potentially cracked offline.

The recovered credentials could then be used to gain unauthorized access to corporate accounts.

Similar vulnerability have been [exploited in the past](https://www.bleepingcomputer.com/news/security/windows-ntlm-hash-leak-flaw-exploited-in-phishing-attacks-on-governments/), typically through [malicious attachments](https://www.bleepingcomputer.com/news/security/hackers-steal-windows-ntlm-authentication-hashes-in-phishing-attacks/) sent in [phishing campaigns](https://www.bleepingcomputer.com/news/security/microsoft-patches-windows-zero-day-exploited-in-attacks-on-ukraine/).

## Recent updates from other companies

Other vendors who released updates or advisories in November 2026 include:

- **Barracuda Networks** [released security updates](https://www.bleepingcomputer.com/news/security/barracuda-warns-of-critical-flaws-allowing-root-access-to-devices/) for two vulnerabilities that can let attackers run commands with root privileges. A week later, these flaws were [exploited in attacks](https://www.bleepingcomputer.com/news/security/hackers-exploit-barracuda-email-security-gateway-flaws-to-get-root-access/).
- **Cisco** [released security updates](https://sec.cloudapps.cisco.com/security/center/publicationListing.x) for numerous products, including critical vulnerabilities Catalyst SD-WAN Controller, Secure Email Gateway, and Meraki.
- **Google** [released emergency security updates](https://www.bleepingcomputer.com/news/security/google-patches-eighth-chrome-zero-day-exploited-in-attacks-this-year/) to patch a new Chrome vulnerability exploited in zero-day attacks.
- **Ivanti** [released security updates](https://www.bleepingcomputer.com/news/security/ivanti-patches-two-more-connect-secure-zero-days-chained-in-attacks/) to patch two Connect Secure (ICS) remote access gateway flaws that have been chained in zero-day attacks since at least October 1.
- **N-able** is [working on a hotfix](https://www.bleepingcomputer.com/news/security/n-able-takes-cloud-platform-offline-after-30-plus-zero-days-published/) for an alleged 30+ zero-days that were publicly disclosed yesterday, causing the company to take its hosted N-central environments offline.
- **Linux** distributions [released security updates](https://www.bleepingcomputer.com/news/security/openssh-flaw-lets-attackers-log-into-password-disabled-linux-accounts/) to fix an authentication bypass flaw involving OpenSSH and musl, dubbed "*sshole".
- **SAP** [released the November security updates](https://www.bleepingcomputer.com/news/security/sap-patches-four-maximum-severity-security-vulnerabilities/), which include fixes for four maximum-severity vulnerabilities.
- **SonicWall** [released security updates](https://www.bleepingcomputer.com/news/security/sonicwall-warns-of-new-ssl-vpn-mfa-bypass-flaw-exploited-in-attacks/) for seven vulnerabilities in SonicOS firewalls, including an SSL-VPN authentication bypass flaw exploited in attacks.
- **Vates** [released security updates](https://www.bleepingcomputer.com/news/security/critical-xen-orchestra-auth-bypass-flaw-exploited-to-hijack-vm-servers/) for a critical authentication bypass vulnerability in Xen Orchestra is being actively exploited in attacks.
- **Zyxel**[patched a zero-day vulnerability](https://www.bleepingcomputer.com/news/security/zyxel-fixes-zero-day-exploited-to-hack-nearly-1-000-network-switches/) in its GS1900 series network switches that was exploited to compromise nearly 1,000 devices worldwide.

## The November 2026 Patch Tuesday Security Updates

Below is the complete list of resolved vulnerabilities in the November 2026 updates. Note, this report does include the flaws fixed earlier this month.

To access the full description of each vulnerability and the systems it affects, you can view the [full report here](https://www.bleepingcomputer.com/microsoft-patch-tuesday-reports/Microsoft-Patch-Tuesday-November-2026.html).

| Tag | CVE ID | CVE Title | Severity |
| --- | --- | --- | --- |
| .NET | [CVE-2026-118747](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118747) | .NET Denial of Service Vulnerability | Important |
| .NET | [CVE-2026-118746](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118746) | .NET Security Feature Bypass Vulnerability | Important |
| .NET | [CVE-2026-120796](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120796) | .NET Denial of Service Vulnerability | Important |
| .NET | [CVE-2026-114155](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114155) | .NET Elevation of Privilege Vulnerability | Important |
| .NET | [CVE-2026-105544](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105544) | .NET Elevation of Privilege Vulnerability | Important |
| .NET | [CVE-2026-109475](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109475) | .NET Denial of Service Vulnerability | Important |
| Active Directory Domain Services | [CVE-2026-105568](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105568) | Windows Active Directory Domain Services Denial of Service Vulnerability | Important |
| Active Directory Domain Services | [CVE-2026-118146](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118146) | Windows Active Directory Domain Services Remote Code Execution Vulnerability | Critical |
| Active Directory Domain Services | [CVE-2026-118735](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118735) | Active Directory Domain Services Elevation of Privilege Vulnerability | Important |
| Active Directory Domain Services | [CVE-2026-118148](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118148) | Active Directory Domain Services Elevation of Privilege Vulnerability | Critical |
| ActiveSyncProvider | [CVE-2026-119889](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119889) | ActiveSyncProvider Information Disclosure Vulnerability | Important |
| AMD Zen | [CVE-2026-84004](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-84004) | AMD Zen Information Disclosure Vulnerability | Important |
| AMD Zen | [CVE-2026-84005](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-84005) | AMD Zen Information Disclosure Vulnerability | Important |
| ASP.NET Core | [CVE-2026-109476](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109476) | ASP.NET Core Information Disclosure Vulnerability | Important |
| ASP.NET Core | [CVE-2026-109478](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109478) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-118741](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118741) | ASP.NET Core Elevation of Privilege Vulnerability | Important |
| ASP.NET Core | [CVE-2026-118750](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118750) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-118749](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118749) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-118748](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118748) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-109481](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109481) | ASP.NET Core Elevation of Privilege Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114156](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114156) | ASP.NET Core Security Feature Bypass Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114150](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114150) | ASP.NET Core Information Disclosure Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114154](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114154) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114149](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114149) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114146](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114146) | ASP.NET Core Elevation of Privilege Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114147](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114147) | ASP.NET Core Denial of Service Vulnerability | Important |
| ASP.NET Core | [CVE-2026-114157](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114157) | ASP.NET Core Security Feature Bypass Vulnerability | Important |
| Aspire | [CVE-2026-118740](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118740) | Aspire Security Feature Bypass Vulnerability | Important |
| Aspire | [CVE-2026-120006](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120006) | Aspire Elevation of Privilege Vulnerability | Important |
| Aspire | [CVE-2026-120792](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120792) | Aspire Information Disclosure Vulnerability | Important |
| Aspire | [CVE-2026-120778](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120778) | Aspire Elevation of Privilege Vulnerability | Important |
| Azure CLI | [CVE-2026-109457](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109457) | Azure CLI Remote Code Execution Vulnerability | Important |
| Azure Confidential Clean Rooms | [CVE-2026-121668](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121668) | Azure Confidential Clean Rooms Tampering Vulnerability | Important |
| Azure CycleCloud | [CVE-2026-114161](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114161) | Azure CycleCloud Elevation of Privilege Vulnerability | Important |
| Azure CycleCloud | [CVE-2026-113822](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113822) | Azure CycleCloud Elevation of Privilege Vulnerability | Important |
| Azure CycleCloud | [CVE-2026-102224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102224) | Azure CycleCloud Elevation of Privilege Vulnerability | Important |
| Azure CycleCloud | [CVE-2026-113823](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113823) | Azure CycleCloud Information Disclosure Vulnerability | Important |
| Azure DevOps | [CVE-2026-109467](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109467) | Azure DevOps Server Remote Code Execution Vulnerability | Important |
| Azure DevOps Server | [CVE-2026-85923](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85923) | Azure DevOps Server Elevation of Privilege Vulnerability | Important |
| Azure DevOps Server | [CVE-2026-112745](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112745) | Azure DevOps Server Information Disclosure Vulnerability | Important |
| Azure DevOps Server | [CVE-2026-120783](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120783) | Azure DevOps Server Elevation of Privilege Vulnerability | Important |
| Azure File Sync | [CVE-2026-118288](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118288) | Microsoft Azure File Sync Elevation of Privilege Vulnerability | Important |
| Azure Firmware | [CVE-2026-109462](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109462) | Azure Firmware Security Feature Bypass Vulnerability | Important |
| Azure Front Door (AFD) | [CVE-2026-118742](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118742) | Azure Front Door Elevation of Privilege Vulnerability | Important |
| Azure Local | [CVE-2026-105734](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105734) | Azure Local Elevation of Privilege Vulnerability | Important |
| Azure Managed Grafana | [CVE-2026-114160](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114160) | Azure Managed Grafana Elevation of Privilege Vulnerability | Critical |
| Azure NFS mount helper (aznfs) | [CVE-2026-105494](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105494) | Azure NFS mount helper (aznfs) Elevation of Privilege Vulnerability | Important |
| Azure OpenAI | [CVE-2026-119990](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119990) | Azure OpenAI Elevation of Privilege Vulnerability | Critical |
| Azure Pipelines | [CVE-2026-119989](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119989) | Azure Pipelines Remote Code Execution Vulnerability | Important |
| Connected Devices Platform Service (Cdpsvc) | [CVE-2026-96007](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96007) | Connected Devices Platform Service (Cdpsvc) Elevation of Privilege Vulnerability | Important |
| Data Deduplication | [CVE-2026-119883](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119883) | Data Deduplication Security Feature Bypass Vulnerability | Important |
| Data Sharing Service Client | [CVE-2026-95963](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95963) | Data Sharing Service Client Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-96103](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96103) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-105581](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105581) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-96175](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96175) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-96174](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96174) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-113819](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113819) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-96172](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96172) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-113758](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113758) | Windows Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-105528](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105528) | Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Desktop Window Manager | [CVE-2026-112988](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112988) | Windows Desktop Window Manager Elevation of Privilege Vulnerability | Important |
| Entra Device Registration | [CVE-2026-109469](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109469) | Entra Device Registration Elevation of Privilege Vulnerability | Critical |
| Github Copilot | [CVE-2026-83953](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-83953) | GitHub Copilot for Jetbrains Information Disclosure Vulnerability | Important |
| Graphic Fonts | [CVE-2026-96084](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96084) | Graphic Fonts Elevation of Privilege Vulnerability | Important |
| Graphic Fonts | [CVE-2026-88211](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88211) | Graphic Fonts Information Disclosure Vulnerability | Important |
| Graphic Fonts | [CVE-2026-119969](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119969) | Graphic Fonts Remote Code Execution Vulnerability | Critical |
| HEIF Image Extensions | [CVE-2026-100204](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100204) | HEIF Image Extensions Remote Code Execution Vulnerability | Important |
| HID class driver | [CVE-2026-96059](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96059) | HID class driver Information Disclosure Vulnerability | Important |
| HID Parser Library | [CVE-2026-96974](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96974) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| HID Parser Library | [CVE-2026-125135](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-125135) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| HID Parser Library | [CVE-2026-96982](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96982) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| HID Parser Library | [CVE-2026-96979](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96979) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| HID Parser Library | [CVE-2026-122173](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122173) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| HID Parser Library | [CVE-2026-96010](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96010) | HID Parser Library Elevation of Privilege Vulnerability | Important |
| JDBC Driver for SQL Server | [CVE-2026-70003](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70003) | JDBC Driver for SQL Server Security Feature Bypass Vulnerability | Important |
| Kernel Transaction Manager | [CVE-2026-94517](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94517) | Windows Kernel Transaction Manager Information Disclosure Vulnerability | Important |
| Kernel Transaction Manager | [CVE-2026-122297](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122297) | Windows Kernel Transaction Manager Information Disclosure Vulnerability | Important |
| Kernel Transaction Manager | [CVE-2026-94522](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94522) | Windows Kernel Transaction Manager Elevation of Privilege Vulnerability | Important |
| Kernel Transaction Manager | [CVE-2026-119397](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119397) | Windows Kernel Transaction Manager Elevation of Privilege Vulnerability | Important |
| Mailslot File System | [CVE-2026-105537](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105537) | Mailslot File System Information Disclosure Vulnerability | Important |
| Mariner | [CVE-2026-120756](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120756) | Heap Buffer Over-read via Malformed Message Size in HDF5's H5O__chunk_deserialize | Low |
| Mariner | [CVE-2026-120755](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120755) | Integer Underflow Leads to Out-of-Bounds Read via Truncated Chunk in HDF5 Szip Filter | Moderate |
| Mariner | [CVE-2026-120754](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120754) | Uninitialized Heap Memory Disclosure via Truncated Chunk in HDF5 Scale-Offset Filter | Low |
| Mariner | [CVE-2026-120830](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120830) | Libslirp: libslirp: out-of-bounds heap read in icmp_forward_error() leading to information disclosure | Moderate |
| Mariner | [CVE-2026-120758](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120758) | NULL Pointer Dereference in H5HL_unprotect via Corrupted File | Moderate |
| Mariner | [CVE-2026-99281](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99281) | tun: Require CAP_NET_ADMIN to attach to an ownerless device | Important |
| Mariner | [CVE-2026-120689](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120689) | Uncontrolled Recursion in HDF5 H5B__iterate_helper() via Crafted File | Low |
| Mariner | [CVE-2026-120647](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120647) | CGI versions before 5.00 for Perl allow Content-Disposition parameter injection via unescaped double quotes in the header attachment filename | Moderate |
| Mariner | [CVE-2026-120645](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120645) | CGI versions before 5.00 for Perl allow denial of service via submitted values used as a regex for optgroup selection in scrolling_list | Moderate |
| Mariner | [CVE-2026-120644](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120644) | CGI::Cookie versions before 5.00 for Perl allow cookie attribute injection via unvalidated path, domain and expires values | Moderate |
| Mariner | [CVE-2026-120651](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120651) | CGI versions before 5.00 for Perl allow an infinite loop on a short request body when $DISABLE_UPLOADS is set | Moderate |
| Mariner | [CVE-2026-120650](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120650) | CGI versions before 5.00 for Perl allow memory, CPU and disk exhaustion via missing or unenforced request size, parameter and upload limits | Moderate |
| Mariner | [CVE-2026-120648](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120648) | CGI versions before 5.00 for Perl allow HTML injection via text containing --> in comment | Moderate |
| Mariner | [CVE-2026-99220](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99220) | asymmetric_keys: reject trust keys without IDs | Moderate |
| Mariner | [CVE-2026-99219](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99219) | ftrace: Initialize modname and offset in print_rec() | Moderate |
| Mariner | [CVE-2026-99218](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99218) | coredump: hold RCU while releasing parked threads | Moderate |
| Mariner | [CVE-2026-99223](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99223) | keys: make keyring indexes independent of kernel addresses | Low |
| Mariner | [CVE-2026-99222](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99222) | keys: Protect the read method check against type removal | Moderate |
| Mariner | [CVE-2026-99221](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99221) | keys/trusted_keys: return immediately after TPM unseal failure | Low |
| Mariner | [CVE-2026-97371](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97371) | ntopng: Stack buffer overflow (write) in nDPI custom category detection allows remote code execution via crafted network packets | Moderate |
| Mariner | [CVE-2026-123158](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123158) | sshd in OpenSSH before 10.6p2 on Linux, when musl libc is used without PAM, lacks a workaround for a password authentication bypass (related to misinterpretation of whether a string is intended to be a password hash). For some configurations of accounts, any password between 256 and 1024 characters succeeds. An example of a platform using musl libc without PAM is Alpine Linux. | Important |
| Mariner | [CVE-2026-121520](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121520) | Malicious client could set xattr value outside of BuildKit state directory | Moderate |
| Mariner | [CVE-2026-120831](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120831) | Libslirp: libslirp: queue pointer corruption in if_output() leading to denial of service | Moderate |
| Mariner | [CVE-2026-82413](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-82413) | ntopng: authenticated (non-admin) OS command injection via the vulnerability-scan `scan_ports` parameter (`nmap` argument reaches `popen`) | Important |
| Mariner | [CVE-2026-124586](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124586) | Tencent RapidJSON diyfp.h GetCachedPowerByIndex out-of-bounds | Moderate |
| Mariner | [CVE-2026-124317](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124317) | libexpat through 2.10.0 Out-of-Bounds Read via unknown_toUtf8 and unknown_toUtf16 | Moderate |
| Mariner | [CVE-2026-120642](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120642) | CGI versions before 5.00 for Perl return request-derived values untainted under taint mode | Moderate |
| Mariner | [CVE-2026-112910](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112910) | filelock: WindowsFileLock ignores mode: a 0o600 lock file and the ReadWriteLock database inherit the directory ACL | Moderate |
| Mariner | [CVE-2026-100408](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100408) | Git for Windows: git-credential-wincred Erase Path Heap Overflow | Moderate |
| Mariner | [CVE-2026-100407](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100407) | Git for Windows: git-credential-wincred OAuth Store Heap Overflow | Moderate |
| Mariner | [CVE-2026-115710](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-115710) | Use of Cache Containing Sensitive Information in Elasticsearch Leading to Information Disclosure | Moderate |
| Mariner | [CVE-2026-115298](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-115298) | Incorrect Authorization in Elasticsearch Leading to Information Disclosure | Moderate |
| Mariner | [CVE-2026-114456](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114456) | Missing origin validation for the externalbrowser authenticator callback in multiple Snowflake client drivers | Moderate |
| Mariner | [CVE-2026-100082](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100082) | xen-blkback: Avoid UAF when reading I/O statistics | Moderate |
| Mariner | [CVE-2026-99283](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99283) | netfilter: conntrack: tcp: use UNACK timeout for non-closing RST packets | Low |
| Mariner | [CVE-2026-99284](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99284) | net: skbuff: propagate shared-frag marker in skb_zerocopy() | Moderate |
| Mariner | [CVE-2026-120757](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120757) | Heap Buffer Over-read via Non-Terminated Link Data in H5L__extern_traverse | Moderate |
| Mariner | [CVE-2026-100081](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100081) | xen-netback: defer xenvif_mcast_addr_list_free() | Moderate |
| Mariner | [CVE-2026-100080](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100080) | xen-netback: Fix UAF when reading statistics data | Moderate |
| Mariner | [CVE-2026-99282](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99282) | net/sched: sch_teql: fix use-after-free on lower qdisc drop | Moderate |
| Mariner | [CVE-2026-115715](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-115715) | Allocation of Resources Without Limits or Throttling in Elasticsearch Leading to Denial of Service | Moderate |
| Mariner | [CVE-2026-120638](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120638) | CGI versions before 5.00 for Perl allow open redirects via HTML entity decoding of the URL after application validation in redirect | Moderate |
| Mariner | [CVE-2026-120636](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120636) | CGI versions before 5.00 for Perl allow open redirects and script injection via URLs built from REQUEST_URI in url and start_form | Moderate |
| Mariner | [CVE-2026-120635](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120635) | CGI versions before 5.00 for Perl allow form fields to be smuggled past proxies and WAFs via multipart parsing that differs from the RFCs | Moderate |
| Mariner | [CVE-2026-120641](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120641) | CGI versions before 5.00 for Perl return upload filenames with any client-supplied path, including ../ and Windows paths | Important |
| Mariner | [CVE-2026-120640](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120640) | CGI versions before 5.00 for Perl allow the POSTDATA, PUTDATA, PATCHDATA and XForms:Model parameters to be set from the query string or form fields | Important |
| Mariner | [CVE-2026-120639](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120639) | CGI versions before 5.00 for Perl allow HTTP header injection via entity decoding after the newline check in header and unchecked values in multipart_start and do_push | Moderate |
| Mariner | [CVE-2026-120633](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120633) | CGI versions before 5.00 for Perl trust the client X-Forwarded-Host header in url, self_url, virtual_host and virtual_port | Moderate |
| Mariner | [CVE-2026-120453](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120453) | The Sleuth Kit through 4.15.0 Heap Out-of-Bounds Read via HFS+ decmpfs Header | Moderate |
| Mariner | [CVE-2026-119776](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119776) | frr: ospf6d fails to enforce all OSPFv3 packets use IPv6 link-local addresses | Moderate |
| Mariner | [CVE-2026-119741](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119741) | rsync < 3.5.2 Denial of Service via hash_search() Checksum Collisions | Important |
| Mariner | [CVE-2026-120632](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120632) | CGI versions before 5.00 for Perl allow CPU exhaustion via a backtracking regex on the XForms multipart/related Content-Type | Moderate |
| Mariner | [CVE-2026-120457](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120457) | libaec through 1.1.7 Out-of-Bounds Read via m_se_decode() Second Extension Decoder | Moderate |
| Mariner | [CVE-2026-120454](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120454) | The Sleuth Kit through 4.15.0 NULL Pointer Dereference via decmpfs LZVN Decompression | Moderate |
| Mariner | [CVE-2026-99246](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99246) | tipc: protect node reset trace dump with node lock | Important |
| Mariner | [CVE-2026-99245](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99245) | KEYS: Fix key_reject_and_link() race with keyring restriction | Moderate |
| Mariner | [CVE-2026-99243](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99243) | io-wq: order the exit bit against worker creation task work | Moderate |
| Mariner | [CVE-2026-99251](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99251) | Drivers: hv: Avoid infinite retry loop in init_vp_index() | Moderate |
| Mariner | [CVE-2026-99249](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99249) | pid_namespace: make zap_pid_ns_processes() freezable | Low |
| Mariner | [CVE-2026-99247](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99247) | tracing: Do not initialize tracefs work if tracing is disabled | Moderate |
| Mariner | [CVE-2026-99236](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99236) | tracing: Reject incomplete event filter expressions | Moderate |
| Mariner | [CVE-2026-99229](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99229) | io_uring/wait: don't spin on a stuck overflow list | Moderate |
| Mariner | [CVE-2026-99226](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99226) | keys: Avoid the owner account dereference in named keyring lookup | Moderate |
| Mariner | [CVE-2026-99225](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99225) | keys: Check the authorization payload in process keyring searches | Moderate |
| Mariner | [CVE-2026-99235](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99235) | tracing: Save the event file instead of the compatible histogram | Moderate |
| Mariner | [CVE-2026-99234](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99234) | tracing: Unregister field variable histograms when the command fails | Low |
| Mariner | [CVE-2026-99233](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99233) | tracing/histograms: Verify event_call identity when updating synth_event refcount | Moderate |
| Mariner | [CVE-2026-99254](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99254) | io_uring: don't flood a cancelling task with task_work | Moderate |
| Mariner | [CVE-2026-99272](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99272) | smb: client: validate the data area in SMB2_read() | Moderate |
| Mariner | [CVE-2026-99271](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99271) | ALSA: line6: Clear prev_fbuf on capture buffer release | Moderate |
| Mariner | [CVE-2026-99270](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99270) | tcp: Fix potential UAF in reqsk_timer_handler(). | Important |
| Mariner | [CVE-2026-99275](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99275) | smb: client: reject short SESSION_SETUP responses | Moderate |
| Mariner | [CVE-2026-99274](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99274) | smb: client: fix fiemap wild read on empty truncated response | Moderate |
| Mariner | [CVE-2026-99273](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99273) | ksmbd: reserve space for the UTF-16 terminator in stream info | Moderate |
| Mariner | [CVE-2026-99268](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99268) | io_uring: wake ring pollers for local task_work | Low |
| Mariner | [CVE-2026-99260](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99260) | ntfs: fix resident conversion in ntfs_new_attr_flags | Low |
| Mariner | [CVE-2026-99256](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99256) | dm cache: fix issue with background work locking | Low |
| Mariner | [CVE-2026-99255](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99255) | io_uring/io-wq: don't hide a link from cancellations | Moderate |
| Mariner | [CVE-2026-99263](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99263) | io_uring/poll: avoid retry wakeup loss when dropping ownership | Low |
| Mariner | [CVE-2026-99262](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99262) | io_uring/timeout: don't lose a cancel as io-wq arms a timeout | Moderate |
| Mariner | [CVE-2026-99261](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99261) | drm/amdgpu: correct reservation fence slots for userq per-vm BOs eviction | Low |
| Mariner | [CVE-2026-99224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-99224) | keys: Protect the type name while describing a key | Moderate |
| Microsoft 365 Agents SDK | [CVE-2026-109485](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109485) | Microsoft 365 Agents SDK Information Disclosure Vulnerability | Important |
| Microsoft Account | [CVE-2026-112982](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112982) | Microsoft Account Tampering Vulnerability | Important |
| Microsoft Account | [CVE-2026-112974](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112974) | Microsoft Account Tampering Vulnerability | Important |
| Microsoft ActiveX Installer Service | [CVE-2026-96158](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96158) | Microsoft ActiveX Installer Service Elevation of Privilege Vulnerability | Important |
| Microsoft Authentication Library (MSAL) for Node.js | [CVE-2026-108470](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108470) | Microsoft Authentication Library (MSAL) for Node.js Information Disclosure Vulnerability | Important |
| Microsoft Authentication Library for JavaScript | [CVE-2026-108469](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108469) | Microsoft Authentication Library for JavaScript Spoofing Vulnerability | Important |
| Microsoft Azure Kubernetes Service | [CVE-2026-122986](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122986) | Microsoft Azure Kubernetes Service Elevation of Privilege Vulnerability | Important |
| Microsoft Bluetooth Driver | [CVE-2026-70120](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70120) | Microsoft Bluetooth Driver Elevation of Privilege Vulnerability | Important |
| Microsoft Color Management | [CVE-2026-96067](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96067) | Microsoft Color Management Remote Code Execution Vulnerability | Important |
| Microsoft Color Management | [CVE-2026-96054](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96054) | Microsoft Color Management Remote Code Execution Vulnerability | Important |
| Microsoft Color Management | [CVE-2026-96078](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96078) | Microsoft Color Management Remote Code Execution Vulnerability | Important |
| Microsoft Configuration Manager | [CVE-2026-119991](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119991) | Microsoft Configuration Manager Information Disclosure Vulnerability | Important |
| Microsoft Defender | [CVE-2026-122194](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122194) | Microsoft Defender Remote Code Execution Vulnerability | Critical |
| Microsoft Dynamics 365 (on-premises) | [CVE-2026-122196](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122196) | Microsoft Dynamics 365 (on-premises) Information Disclosure Vulnerability | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121252](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121252) | Chromium CVE-2026-121252: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121251](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121251) | Chromium CVE-2026-121251: Missing authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121224) | Chromium CVE-2026-121224: Security issue | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121087](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121087) | Chromium CVE-2026-121087: Improper input validation | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121227](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121227) | Chromium CVE-2026-121227: Uninitialized resource | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121084](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121084) | Chromium CVE-2026-121084: Out of bounds read | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121255](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121255) | Chromium CVE-2026-121255: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121083](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121083) | Chromium CVE-2026-121083: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121081](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121081) | Chromium CVE-2026-121081: UI misrepresentation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121082](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121082) | Chromium CVE-2026-121082: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121085](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121085) | Chromium CVE-2026-121085: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121228](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121228) | Chromium CVE-2026-121228: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121226](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121226) | Chromium CVE-2026-121226: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121253](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121253) | Chromium CVE-2026-121253: Missing authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121254](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121254) | Chromium CVE-2026-121254: Information leak | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121086](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121086) | Chromium CVE-2026-121086: Buffer overflow | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121248](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121248) | Chromium CVE-2026-121248: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121245](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121245) | Chromium CVE-2026-121245: Race condition | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121214](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121214) | Chromium CVE-2026-121214: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121089](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121089) | Chromium CVE-2026-121089: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121091](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121091) | Chromium CVE-2026-121091: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121092](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121092) | Chromium CVE-2026-121092: Uncontrolled recursion | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121095](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121095) | Chromium CVE-2026-121095: Uninitialized resource | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121243](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121243) | Chromium CVE-2026-121243: Information leak | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121094](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121094) | Chromium CVE-2026-121094: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121093](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121093) | Chromium CVE-2026-121093: Out of bounds read | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121244](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121244) | Chromium CVE-2026-121244: UI misrepresentation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121215](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121215) | Chromium CVE-2026-121215: UI misrepresentation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121249](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121249) | Chromium CVE-2026-121249: Buffer overflow | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121221](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121221) | Chromium CVE-2026-121221: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121250](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121250) | Chromium CVE-2026-121250: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121223](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121223) | Chromium CVE-2026-121223: Observable discrepancy | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121222](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121222) | Chromium CVE-2026-121222: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121088](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121088) | Chromium CVE-2026-121088: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121217](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121217) | Chromium CVE-2026-121217: Use after free | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121216](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121216) | Chromium CVE-2026-121216: UI misrepresentation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121218](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121218) | Chromium CVE-2026-121218: Type confusion | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121220](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121220) | Chromium CVE-2026-121220: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121219](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121219) | Chromium CVE-2026-121219: Integer overflow | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-119270](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119270) | Chromium CVE-2026-119270: Improper input validation | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119271](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119271) | Chromium CVE-2026-119271: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119269](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119269) | Chromium CVE-2026-119269: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119267](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119267) | Chromium CVE-2026-119267: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119268](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119268) | Chromium CVE-2026-119268: Integer overflow | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119272](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119272) | Chromium CVE-2026-119272: Out of bounds read | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-76029](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76029) | Chromium CVE-2026-76029: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-76028](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76028) | Chromium CVE-2026-76028: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-76030](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76030) | Chromium CVE-2026-76030: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-122518](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122518) | Microsoft Edge (Chromium-based) Information Disclosure Vulnerability | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-76031](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76031) | Chromium CVE-2026-76031: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-118321](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118321) | Chromium CVE-2026-118321: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119260](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119260) | Chromium CVE-2026-119260: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-118314](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118314) | Chromium CVE-2026-118314: Incorrect reference resolution | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121206](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121206) | Chromium CVE-2026-121206: UI misrepresentation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-118309](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118309) | Chromium CVE-2026-118309: Incorrect reference resolution | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119261](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119261) | Chromium CVE-2026-119261: Improper input validation | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119265](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119265) | Chromium CVE-2026-119265: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119266](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119266) | Chromium CVE-2026-119266: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119264](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119264) | Chromium CVE-2026-119264: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119262](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119262) | Chromium CVE-2026-119262: Improper input validation | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-119263](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119263) | Chromium CVE-2026-119263: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121037](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121037) | Chromium CVE-2026-121037: Out of bounds write | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121256](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121256) | Chromium CVE-2026-121256: Use of released resource | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121036](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121036) | Chromium CVE-2026-121036: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121034](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121034) | Chromium CVE-2026-121034: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121035](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121035) | Chromium CVE-2026-121035: Use after free | Critical |
| Microsoft Edge (Chromium-based) | [CVE-2026-121038](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121038) | Chromium CVE-2026-121038: Information leak | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121079](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121079) | Chromium CVE-2026-121079: Race condition | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121080](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121080) | Chromium CVE-2026-121080: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121078](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121078) | Chromium CVE-2026-121078: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121039](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121039) | Chromium CVE-2026-121039: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121050](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121050) | Chromium CVE-2026-121050: Race condition | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-76024](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76024) | Chromium CVE-2026-76024: Memory corruption | Critical |
| Microsoft Edge (Chromium-based) | [CVE-2026-121230](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121230) | Chromium CVE-2026-121230: Race condition | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-76025](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76025) | Chromium CVE-2026-76025: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-76027](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76027) | Chromium CVE-2026-76027: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-76026](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-76026) | Chromium CVE-2026-76026: Memory corruption | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121257](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121257) | Chromium CVE-2026-121257: Use after free | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121031](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121031) | Chromium CVE-2026-121031: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121032](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121032) | Chromium CVE-2026-121032: Out of bounds read | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121030](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121030) | Chromium CVE-2026-121030: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-120930](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120930) | Chromium CVE-2026-120930: Incorrect authorization | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121029](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121029) | Chromium CVE-2026-121029: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121135](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121135) | Chromium CVE-2026-121135: Security issue | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121136](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121136) | Chromium CVE-2026-121136: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121134](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121134) | Chromium CVE-2026-121134: Information loss | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121132](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121132) | Chromium CVE-2026-121132: Information leak | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121133](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121133) | Chromium CVE-2026-121133: Incorrect reference resolution | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121137](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121137) | Chromium CVE-2026-121137: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121176](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121176) | Chromium CVE-2026-121176: Uninitialized resource | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121178](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121178) | Chromium CVE-2026-121178: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121175](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121175) | Chromium CVE-2026-121175: Improper resource exposure | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121138](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121138) | Chromium CVE-2026-121138: Observable discrepancy | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121174](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121174) | Chromium CVE-2026-121174: Missing authorization | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121124](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121124) | Chromium CVE-2026-121124: Improper adherence to coding standards | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121125](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121125) | Chromium CVE-2026-121125: Information leak | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121123](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121123) | Chromium CVE-2026-121123: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121121](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121121) | Chromium CVE-2026-121121: UI misrepresentation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121122](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121122) | Chromium CVE-2026-121122: UI misrepresentation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121126](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121126) | Chromium CVE-2026-121126: Use after free | Critical |
| Microsoft Edge (Chromium-based) | [CVE-2026-121130](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121130) | Chromium CVE-2026-121130: Observable discrepancy | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121131](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121131) | Chromium CVE-2026-121131: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121129](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121129) | Chromium CVE-2026-121129: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121127](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121127) | Chromium CVE-2026-121127: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121128](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121128) | Chromium CVE-2026-121128: Use after free | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121179](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121179) | Chromium CVE-2026-121179: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121198](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121198) | Chromium CVE-2026-121198: Confused deputy | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121199](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121199) | Chromium CVE-2026-121199: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121197](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121197) | Chromium CVE-2026-121197: Out of bounds read | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121194](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121194) | Chromium CVE-2026-121194: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121195](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121195) | Chromium CVE-2026-121195: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121200](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121200) | Chromium CVE-2026-121200: Incorrect reference resolution | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121204](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121204) | Chromium CVE-2026-121204: Incomplete cleanup | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121205](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121205) | Chromium CVE-2026-121205: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121203](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121203) | Chromium CVE-2026-121203: Use after free | Critical |
| Microsoft Edge (Chromium-based) | [CVE-2026-121201](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121201) | Chromium CVE-2026-121201: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121202](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121202) | Chromium CVE-2026-121202: Use after free | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121183](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121183) | Chromium CVE-2026-121183: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121184](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121184) | Chromium CVE-2026-121184: Out of bounds read | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121182](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121182) | Chromium CVE-2026-121182: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121180](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121180) | Chromium CVE-2026-121180: Buffer overflow | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121181](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121181) | Chromium CVE-2026-121181: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121185](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121185) | Chromium CVE-2026-121185: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121190](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121190) | Chromium CVE-2026-121190: UI misrepresentation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121193](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121193) | Chromium CVE-2026-121193: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121189](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121189) | Chromium CVE-2026-121189: Use after free | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121187](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121187) | Chromium CVE-2026-121187: Observable discrepancy | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121188](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121188) | Chromium CVE-2026-121188: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121120](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121120) | Chromium CVE-2026-121120: Improper input validation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121101](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121101) | Chromium CVE-2026-121101: Missing authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121209](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121209) | Chromium CVE-2026-121209: UI misrepresentation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121235](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121235) | Chromium CVE-2026-121235: Information leak | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121211](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121211) | Chromium CVE-2026-121211: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121100](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121100) | Chromium CVE-2026-121100: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121210](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121210) | Chromium CVE-2026-121210: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121208](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121208) | Chromium CVE-2026-121208: Out of bounds read | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121231](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121231) | Chromium CVE-2026-121231: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121207](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121207) | Chromium CVE-2026-121207: Uninitialized resource | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121233](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121233) | Chromium CVE-2026-121233: Type confusion | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121102](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121102) | Chromium CVE-2026-121102: Missing authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121232](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121232) | Chromium CVE-2026-121232: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121213](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121213) | Chromium CVE-2026-121213: Uninitialized resource | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121212](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121212) | Chromium CVE-2026-121212: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121097](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121097) | Chromium CVE-2026-121097: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121242](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121242) | Chromium CVE-2026-121242: Improper input validation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121240](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121240) | Chromium CVE-2026-121240: Improper input validation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121096](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121096) | Chromium CVE-2026-121096: Incomplete cleanup | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121237](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121237) | Chromium CVE-2026-121237: Improper state validation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121236](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121236) | Chromium CVE-2026-121236: Improper input validation | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121099](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121099) | Chromium CVE-2026-121099: Information leak | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121239](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121239) | Chromium CVE-2026-121239: Information leak | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121238](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121238) | Chromium CVE-2026-121238: Use after free | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121098](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121098) | Chromium CVE-2026-121098: Improper state validation | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121113](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121113) | Chromium CVE-2026-121113: Buffer overflow | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121111](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121111) | Chromium CVE-2026-121111: Incorrect authorization | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121104](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121104) | Chromium CVE-2026-121104: Incorrect authorization | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121115](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121115) | Chromium CVE-2026-121115: Improper input validation | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121114](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121114) | Chromium CVE-2026-121114: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121103](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121103) | Chromium CVE-2026-121103: Incorrect authorization | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121105](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121105) | Chromium CVE-2026-121105: Information leak | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121107](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121107) | Chromium CVE-2026-121107: Incorrect authorization | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121109](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121109) | Chromium CVE-2026-121109: Inadequate encryption strength | Low |
| Microsoft Edge (Chromium-based) | [CVE-2026-121108](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121108) | Chromium CVE-2026-121108: Confused deputy | Moderate |
| Microsoft Edge (Chromium-based) | [CVE-2026-121118](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121118) | Chromium CVE-2026-121118: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121119](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121119) | Chromium CVE-2026-121119: Use after free | Important |
| Microsoft Edge (Chromium-based) | [CVE-2026-121117](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121117) | Chromium CVE-2026-121117: Use after free | Important |
| Microsoft Entra Private Network Connector | [CVE-2026-109460](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109460) | Microsoft Entra Private Network Connector Information Disclosure Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118149](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118149) | Microsoft Exchange Server Remote Code Execution Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118150](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118150) | Microsoft Exchange Server Elevation of Privilege Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118151](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118151) | Microsoft Exchange Server Elevation of Privilege Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118152](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118152) | Microsoft Exchange Server Spoofing Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118208](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118208) | Microsoft Exchange Server Spoofing Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118207](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118207) | Microsoft Exchange Server Remote Code Execution Vulnerability | Critical |
| Microsoft Exchange Server | [CVE-2026-118157](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118157) | Microsoft Exchange Server Elevation of Privilege Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118153](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118153) | Microsoft Exchange Server Denial of Service Vulnerability | Important |
| Microsoft Exchange Server | [CVE-2026-118154](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118154) | Microsoft Exchange Server Elevation of Privilege Vulnerability | Important |
| Microsoft Graph | [CVE-2026-114162](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114162) | Microsoft Graph Elevation of Privilege Vulnerability | Important |
| Microsoft Graphics Component | [CVE-2026-112754](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112754) | Microsoft Graphics Component Information Disclosure Vulnerability | Important |
| Microsoft High Performance Computing (HPC) Pack | [CVE-2026-122987](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122987) | Microsoft High Performance Computing (HPC) Pack Elevation of Privilege Vulnerability | Important |
| Microsoft Input Method Editor (IME) | [CVE-2026-105505](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105505) | Microsoft Input Method Editor (IME) Elevation of Privilege Vulnerability | Important |
| Microsoft JScript | [CVE-2026-112985](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112985) | Windows JScript Remote Code Execution Vulnerability | Important |
| Microsoft JScript | [CVE-2026-105578](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105578) | Microsoft JScript Remote Code Execution Vulnerability | Important |
| Microsoft Local Security Authority Server (lsasrv) | [CVE-2026-112807](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112807) | Windows Local Security Authority Subsystem Service (LSASS) Denial of Service Vulnerability | Important |
| Microsoft MCP Gateway | [CVE-2026-109492](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109492) | Microsoft MCP Gateway Elevation of Privilege Vulnerability | Important |
| Microsoft Office | [CVE-2026-112731](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112731) | Microsoft Office Information Disclosure Vulnerability | Important |
| Microsoft Office | [CVE-2026-120003](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120003) | Microsoft Office Remote Code Execution Vulnerability | Critical |
| Microsoft Office | [CVE-2026-116717](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116717) | Microsoft Office Remote Code Execution Vulnerability | Important |
| Microsoft Office | [CVE-2026-122198](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122198) | Microsoft Office Remote Code Execution Vulnerability | Important |
| Microsoft Office | [CVE-2026-111293](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111293) | Microsoft Office Information Disclosure Vulnerability | Important |
| Microsoft Office | [CVE-2026-119998](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119998) | Microsoft Office Security Feature Bypass Vulnerability | Important |
| Microsoft Office | [CVE-2026-111291](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111291) | Microsoft Office Information Disclosure Vulnerability | Important |
| Microsoft Office | [CVE-2026-111286](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111286) | Microsoft Office Remote Code Execution Vulnerability | Important |
| Microsoft Office | [CVE-2026-111289](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111289) | Microsoft Office Remote Code Execution Vulnerability | Critical |
| Microsoft Office Access | [CVE-2026-110059](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110059) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-110058](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110058) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-111301](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111301) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-109493](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109493) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-109498](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109498) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-111305](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111305) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Access | [CVE-2026-110060](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110060) | Microsoft Office Access Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124183](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124183) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118301](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118301) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118302](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118302) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118297](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118297) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118298](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118298) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118300](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118300) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118299](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118299) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124187](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124187) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118703](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118703) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118704](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118704) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118705](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118705) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118702](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118702) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-124229](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124229) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118700](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118700) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118701](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118701) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-123395](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123395) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124170](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124170) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-124174](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124174) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-119986](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119986) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118728](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118728) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-119999](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119999) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-123385](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123385) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124176](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124176) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118294](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118294) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118295](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118295) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118296](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118296) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118293](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118293) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124178](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124178) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-124179](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124179) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118292](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118292) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118727](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118727) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118726](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118726) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118729](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118729) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-120785](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120785) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118723](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118723) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118722](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118722) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118725](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118725) | Microsoft Office Excel Elevation of Privilege Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118724](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118724) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-120789](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120789) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-120788](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120788) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-120791](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120791) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-120790](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120790) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-120786](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120786) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118730](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118730) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118732](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118732) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118731](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118731) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118711](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118711) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118710](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118710) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118713](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118713) | Microsoft Office Excel Remote Code Execution Vulnerability | Critical |
| Microsoft Office Excel | [CVE-2026-118712](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118712) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118707](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118707) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118706](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118706) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118709](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118709) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118708](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118708) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118719](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118719) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118718](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118718) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118721](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118721) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118720](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118720) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118715](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118715) | Microsoft Office Excel Elevation of Privilege Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118714](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118714) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118717](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118717) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-118716](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118716) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-116927](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116927) | Microsoft Office Excel Remote Code Execution Vulnerability | Important |
| Microsoft Office Excel | [CVE-2026-111292](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111292) | Microsoft Office Excel Information Disclosure Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-119997](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119997) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123382](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123382) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123381](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123381) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123378](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123378) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123379](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123379) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123380](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123380) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-124227](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124227) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-124228](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124228) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-110043](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110043) | Microsoft Office Outlook Remote Code Execution Vulnerability | Critical |
| Microsoft Office Outlook | [CVE-2026-124194](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124194) | Microsoft Outlook Spoofing Vulnerability | Moderate |
| Microsoft Office Outlook | [CVE-2026-111309](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111309) | Microsoft Office Outlook Remote Code Execution Vulnerability | Critical |
| Microsoft Office Outlook | [CVE-2026-123383](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123383) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123384](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123384) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123377](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123377) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123375](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123375) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-123376](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123376) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-110068](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110068) | Microsoft Office Outlook Remote Code Execution Vulnerability | Critical |
| Microsoft Office Outlook | [CVE-2026-119993](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119993) | Microsoft Office Outlook Information Disclosure Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-119995](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119995) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office Outlook | [CVE-2026-119996](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119996) | Microsoft Office Outlook Remote Code Execution Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-120001](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120001) | Microsoft Office PowerPoint Remote Code Execution Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-120005](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120005) | Microsoft PowerPoint Remote Code Execution Vulnerability | Critical |
| Microsoft Office PowerPoint | [CVE-2026-112734](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112734) | Microsoft Office PowerPoint Remote Code Execution Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-112738](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112738) | Microsoft Office PowerPoint Information Disclosure Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-112737](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112737) | Microsoft Office PowerPoint Remote Code Execution Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-109487](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109487) | Microsoft PowerPoint Remote Code Execution Vulnerability | Important |
| Microsoft Office PowerPoint | [CVE-2026-116922](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116922) | Microsoft Office PowerPoint Information Disclosure Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-111300](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111300) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-88176](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88176) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109504](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109504) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109456](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109456) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-111303](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111303) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109497](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109497) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-110044](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110044) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-110045](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110045) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109455](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109455) | Microsoft Office SharePoint Information Disclosure Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109499](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109499) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109495](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109495) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-111297](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111297) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109472](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109472) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109466](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109466) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-111296](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111296) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109502](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109502) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-80095](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-80095) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109454](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109454) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-112736](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112736) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-120002](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120002) | Microsoft SharePoint Server Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-123391](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123391) | Microsoft Office SharePoint Elevation of Privilege Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-124210](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124210) | Microsoft Office SharePoint Information Disclosure Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-123390](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123390) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-120000](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120000) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-109464](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109464) | Microsoft Office SharePoint Remote Code Execution Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-110057](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110057) | Microsoft Office SharePoint Information Disclosure Vulnerability | Important |
| Microsoft Office SharePoint | [CVE-2026-110065](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110065) | Microsoft Office SharePoint Spoofing Vulnerability | Important |
| Microsoft Office Visio | [CVE-2026-109496](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109496) | Microsoft Office Visio Remote Code Execution Vulnerability | Important |
| Microsoft Office Visio | [CVE-2026-109494](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109494) | Microsoft Office Visio Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111287](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111287) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111302](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111302) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110047](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110047) | Microsoft Office Word Remote Code Execution Vulnerability | Critical |
| Microsoft Office Word | [CVE-2026-109491](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109491) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110066](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110066) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111306](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111306) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110067](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110067) | Microsoft Office Word Remote Code Execution Vulnerability | Critical |
| Microsoft Office Word | [CVE-2026-111285](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111285) | Microsoft Office Word Remote Code Execution Vulnerability | Critical |
| Microsoft Office Word | [CVE-2026-110062](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110062) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110061](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110061) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110064](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110064) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111304](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111304) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110056](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110056) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110052](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110052) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-109505](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109505) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111294](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111294) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-109503](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109503) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110051](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110051) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110048](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110048) | Microsoft Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110046](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110046) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110050](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110050) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110049](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110049) | Microsoft Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111298](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111298) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110054](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110054) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111299](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111299) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111288](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111288) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-109500](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109500) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111295](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111295) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111290](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111290) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-109501](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109501) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110053](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110053) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112722](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112722) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112721](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112721) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112723](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112723) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112726](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112726) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112724](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112724) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112717](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112717) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112716](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112716) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112718](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112718) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112720](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112720) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112719](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112719) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112728](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112728) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-124233](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124233) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112741](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112741) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-113759](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113759) | Microsoft Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-123394](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123394) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-124185](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124185) | Microsoft Office Word Remote Code Execution Vulnerability | Critical |
| Microsoft Office Word | [CVE-2026-112730](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112730) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112729](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112729) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112733](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112733) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112739](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112739) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112735](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112735) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116925](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116925) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116923](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116923) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-110055](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-110055) | Microsoft Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111307](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111307) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116722](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116722) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116718](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116718) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116719](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116719) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111308](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111308) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116721](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116721) | Microsoft Office Word Information Disclosure Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-111310](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-111310) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112715](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112715) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-116720](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116720) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft Office Word | [CVE-2026-112714](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112714) | Microsoft Office Word Remote Code Execution Vulnerability | Important |
| Microsoft PowerShell | [CVE-2026-122985](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122985) | Microsoft PowerShell Information Disclosure Vulnerability | Important |
| Microsoft PowerShell Core | [CVE-2026-121675](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121675) | PowerShell Information Disclosure Vulnerability | Important |
| Microsoft PowerShell Core | [CVE-2026-121669](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121669) | PowerShell Information Disclosure Vulnerability | Important |
| Microsoft PowerShell Core | [CVE-2026-121674](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121674) | PowerShell Information Disclosure Vulnerability | Important |
| Microsoft QUIC | [CVE-2026-88236](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88236) | Microsoft QUIC Denial of Service Vulnerability | Important |
| Microsoft QUIC | [CVE-2026-105512](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105512) | Microsoft QUIC Denial of Service Vulnerability | Important |
| Microsoft Remote Registry Service | [CVE-2026-105492](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105492) | Microsoft Remote Registry Service Denial of Service Vulnerability | Important |
| Microsoft Streaming Service | [CVE-2026-119937](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119937) | Kernel Streaming Service Driver Elevation of Privilege Vulnerability | Important |
| Microsoft Teams | [CVE-2026-116926](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116926) | Microsoft Teams Spoofing Vulnerability | Important |
| Microsoft Teams for Android | [CVE-2026-69901](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-69901) | Microsoft Teams for Android Spoofing Vulnerability | Important |
| Microsoft Teams for Android | [CVE-2026-122979](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122979) | Microsoft Teams for Android Spoofing Vulnerability | Important |
| Microsoft Trace Data Helper | [CVE-2026-121681](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121681) | Microsoft Trace Data Helper Elevation of Privilege Vulnerability | Important |
| Microsoft Trace Data Helper | [CVE-2026-122172](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122172) | Microsoft Trace Data Helper Elevation of Privilege Vulnerability | Important |
| Microsoft WDAC OLE DB provider for SQL | [CVE-2026-85839](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85839) | Microsoft WDAC OLE DB provider for SQL Remote Code Execution Vulnerability | Important |
| Microsoft WDAC OLE DB provider for SQL | [CVE-2026-85838](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85838) | Microsoft WDAC OLE DB provider for SQL Remote Code Execution Vulnerability | Important |
| Microsoft WDAC OLE DB provider for SQL | [CVE-2026-88222](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88222) | Microsoft WDAC OLE DB provider for SQL Remote Code Execution Vulnerability | Important |
| Microsoft WDAC OLE DB provider for SQL | [CVE-2026-116698](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116698) | Microsoft WDAC OLE DB provider for SQL Remote Code Execution Vulnerability | Important |
| Microsoft WDAC OLE DB provider for SQL | [CVE-2026-116699](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116699) | Microsoft WDAC OLE DB provider for SQL Remote Code Execution Vulnerability | Important |
| Microsoft Windows App Store | [CVE-2026-119987](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119987) | Microsoft Windows App Store Elevation of Privilege Vulnerability | Important |
| Microsoft Windows Codecs Library | [CVE-2026-113749](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113749) | Microsoft Windows Codecs Library Remote Code Execution Vulnerability | Critical |
| Microsoft Windows Codecs Library | [CVE-2026-114167](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114167) | HEVC Video Extensions Remote Code Execution Vulnerability | Important |
| Microsoft Windows Codecs Library | [CVE-2026-114164](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114164) | HEVC Video Extensions Remote Code Execution Vulnerability | Important |
| Microsoft Windows Codecs Library | [CVE-2026-96150](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96150) | Microsoft Windows Codecs Library Information Disclosure Vulnerability | Important |
| Microsoft Windows Codecs Library | [CVE-2026-114165](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114165) | HEVC Video Extensions Remote Code Execution Vulnerability | Important |
| Microsoft Windows Media Foundation | [CVE-2026-96157](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96157) | Microsoft Windows Media Foundation Remote Code Execution Vulnerability | Important |
| Microsoft Windows Media Foundation | [CVE-2026-122168](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122168) | Microsoft Windows Media Foundation Elevation of Privilege Vulnerability | Important |
| Microsoft Windows SCSI Class System File | [CVE-2026-113821](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113821) | Microsoft Windows SCSI Class System File Information Disclosure Vulnerability | Important |
| Microsoft Windows SCSI Class System File | [CVE-2026-105586](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105586) | Microsoft Windows SCSI Class System File Elevation of Privilege Vulnerability | Important |
| Microsoft Windows Search Component | [CVE-2026-119954](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119954) | Microsoft Windows Search Component Elevation of Privilege Vulnerability | Important |
| Microsoft Windows Search Component | [CVE-2026-119943](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119943) | Microsoft Windows Search Component Elevation of Privilege Vulnerability | Important |
| Microsoft Windows Search Component | [CVE-2026-116928](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116928) | Windows Search Remote Code Execution Vulnerability | Critical |
| Microsoft Windows Speech | [CVE-2026-119904](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119904) | Microsoft Windows Speech Elevation of Privilege Vulnerability | Important |
| Microsoft XPS Document Converter | [CVE-2026-122171](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122171) | Microsoft XPS Document Converter Remote Code Execution Vulnerability | Important |
| Microsoft XPS Document Converter | [CVE-2026-119880](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119880) | Microsoft XPS Document Converter Remote Code Execution Vulnerability | Important |
| Microsoft XPS Document Converter | [CVE-2026-119881](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119881) | Microsoft XPS Document Converter Elevation of Privilege Vulnerability | Important |
| Quality Windows Audio/Video Experience (QWAVE) service | [CVE-2026-119387](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119387) | Quality Windows Audio/Video Experience (QWAVE) service Elevation of Privilege Vulnerability | Important |
| Quality Windows Audio/Video Experience (QWAVE) service | [CVE-2026-119388](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119388) | Quality Windows Audio/Video Experience (QWAVE) service Elevation of Privilege Vulnerability | Important |
| Quality Windows Audio/Video Experience (QWAVE) service | [CVE-2026-123389](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123389) | Quality Windows Audio/Video Experience (QWAVE) service Elevation of Privilege Vulnerability | Important |
| Reliable Multicast Transport Driver (RMCAST) | [CVE-2026-116697](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116697) | Reliable Multicast Transport Driver (RMCAST) Denial of Service Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-119858](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119858) | Remote Desktop Client Remote Code Execution Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-121677](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121677) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-108419](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108419) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-108418](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108418) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-108417](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108417) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-119934](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119934) | Remote Desktop Client Remote Code Execution Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-95908](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95908) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-95964](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95964) | Remote Desktop Client Remote Code Execution Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-119390](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119390) | Remote Desktop Client Remote Code Execution Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-119839](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119839) | Windows Remote Desktop Client Elevation of Privilege Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-119824](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119824) | Remote Desktop Client Tampering Vulnerability | Important |
| Remote Desktop Client | [CVE-2026-121678](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121678) | Windows Remote Desktop Client Information Disclosure Vulnerability | Important |
| Remote Desktop Gateway Service | [CVE-2026-69327](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-69327) | Windows Remote Desktop Services Remote Code Execution Vulnerability | Important |
| Remote Desktop Gateway Service | [CVE-2026-80094](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-80094) | Remote Desktop Gateway Service Elevation of Privilege Vulnerability | Important |
| Remote Desktop Gateway Service | [CVE-2026-69565](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-69565) | Windows Remote Desktop Services Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96020](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96020) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-112727](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112727) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96177](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96177) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96064](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96064) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-81384](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-81384) | Windows DNS Server Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96179](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96179) | Windows DNS Elevation of Privilege Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96975](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96975) | Role: DNS Server Denial of Service Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96112](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96112) | Windows DNS Server Information Disclosure Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96017](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96017) | Role: DNS Server Denial of Service Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96002](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96002) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| Role: DNS Server | [CVE-2026-96092](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96092) | Windows Domain Name Service Remote Code Execution Vulnerability | Important |
| RPC Runtime | [CVE-2026-83894](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-83894) | RPC Runtime Elevation of Privilege Vulnerability | Important |
| Secondary Logon | [CVE-2026-96989](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96989) | Secondary Logon Information Disclosure Vulnerability | Important |
| Servicing Stack Updates | [CVE-2026-88235](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88235) | Servicing Stack Updates Elevation of Privilege Vulnerability | Important |
| Servicing Stack Updates | [CVE-2026-112989](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112989) | Windows Servicing Stack Updates Elevation of Privilege Vulnerability | Important |
| Software Protection Platform (SPP) | [CVE-2026-113748](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113748) | Software Protection Platform (SPP) Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118111](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118111) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118112](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118112) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-67391](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67391) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-68783](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-68783) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-67387](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67387) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118113](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118113) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-67646](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67646) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-67637](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67637) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-67632](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67632) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-118117](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118117) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118115](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118115) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118118](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118118) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-62903](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-62903) | Microsoft.Data.SqlClient Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-118116](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118116) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118120](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118120) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118119](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118119) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118114](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118114) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-67375](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67375) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-67382](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67382) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-66813](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-66813) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-67372](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67372) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-67374](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-67374) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116936](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116936) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116937](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116937) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-84010](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-84010) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-116935](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116935) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-116940](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116940) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-116941](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116941) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116938](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116938) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116939](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116939) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-116934](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116934) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-88111](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88111) | SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116929](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116929) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-94511](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94511) | SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-94513](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94513) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-116932](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116932) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-116933](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116933) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116930](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116930) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116931](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116931) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-118104](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118104) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-118105](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118105) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118102](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118102) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-118103](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118103) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-118109](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118109) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118110](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118110) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-118106](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118106) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-118108](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118108) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-116944](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116944) | Microsoft SQL Server Elevation of Privilege Vulnerability | Important |
| SQL Server | [CVE-2026-116945](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116945) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116942](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116942) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116943](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116943) | Microsoft SQL Server Information Disclosure Vulnerability | Important |
| SQL Server | [CVE-2026-116947](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116947) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| SQL Server | [CVE-2026-116946](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116946) | Microsoft SQL Server Remote Code Execution Vulnerability | Important |
| Storport.sys Driver | [CVE-2026-119395](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119395) | Storport.sys Driver Information Disclosure Vulnerability | Important |
| vhdmp.sys | [CVE-2026-95989](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95989) | vhdmp.sys Elevation of Privilege Vulnerability | Important |
| Virtual Hard Disk (VHD) Miniport Driver | [CVE-2026-119849](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119849) | Virtual Hard Disk (VHD) Miniport Driver Remote Code Execution Vulnerability | Important |
| Visual Studio | [CVE-2026-114158](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114158) | Visual Studio Remote Code Execution Vulnerability | Important |
| Visual Studio | [CVE-2026-118745](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118745) | Visual Studio Remote Code Execution Vulnerability | Important |
| Visual Studio | [CVE-2026-114152](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114152) | Visual Studio Remote Code Execution Vulnerability | Important |
| Visual Studio | [CVE-2026-114151](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114151) | Visual Studio Remote Code Execution Vulnerability | Important |
| Visual Studio | [CVE-2026-114159](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114159) | Visual Studio Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-119975](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119975) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-70094](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70094) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-119983](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119983) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-119985](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119985) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-119981](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119981) | Visual Studio Code Elevation of Privilege Vulnerability | Important |
| Visual Studio Code | [CVE-2026-119982](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119982) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-102230](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102230) | Visual Studio Code Information Disclosure Vulnerability | Important |
| Visual Studio Code | [CVE-2026-120782](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120782) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-120780](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120780) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-120779](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-120779) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-102236](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102236) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121660](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121660) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121661](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121661) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121664](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121664) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121665](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121665) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-114171](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114171) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121663](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121663) | Visual Studio Code Security Feature Bypass Vulnerability | Important |
| Visual Studio Code | [CVE-2026-121662](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121662) | Visual Studio Code Remote Code Execution Vulnerability | Important |
| Visual Studio Code - GitHub Pull Requests and Issues Extension | [CVE-2026-119976](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119976) | Visual Studio Code GitHub Pull Requests and Issues Extension Information Disclosure Vulnerability | Important |
| Windows Active Directory | [CVE-2026-105559](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105559) | Windows Active Directory Denial of Service Vulnerability | Important |
| Windows Active Directory | [CVE-2026-123387](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123387) | Active Directory Domain Services Elevation of Privilege Vulnerability | Important |
| Windows Active Directory | [CVE-2026-119948](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119948) | Windows Active Directory Remote Code Execution Vulnerability | Important |
| Windows Active Directory Certificate Services | [CVE-2026-95884](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95884) | Windows Active Directory Certificate Services Information Disclosure Vulnerability | Important |
| Windows Active Directory Certificate Services | [CVE-2026-105590](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105590) | Windows Active Directory Certificate Services Security Feature Bypass | Important |
| Windows Admin Center | [CVE-2026-122988](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122988) | Windows Admin Center Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118280](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118280) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118283](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118283) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105498](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105498) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105499](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105499) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118278](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118278) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118277](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118277) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118279](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118279) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105025](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105025) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105022](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105022) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105497](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105497) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105495](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105495) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105496](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105496) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105021](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105021) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105491](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105491) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-95960](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95960) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105020](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105020) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-94515](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94515) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118232](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118232) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118219](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118219) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105493](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105493) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118222](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118222) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118221](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118221) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118218](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118218) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118215](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118215) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118214](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118214) | Windows Advanced Rasterization Platform Information Disclosure Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118217](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118217) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118216](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118216) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118223](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118223) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105026](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105026) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118226](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118226) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118227](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118227) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118229](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118229) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118228](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118228) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105490](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105490) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118224) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-105023](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105023) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Advanced Rasterization Platform | [CVE-2026-118225](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118225) | Windows Advanced Rasterization Platform Elevation of Privilege Vulnerability | Important |
| Windows Ancillary Function Driver for WinSock | [CVE-2026-88242](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88242) | Windows Ancillary Function Driver for WinSock Elevation of Privilege Vulnerability | Important |
| Windows App Readiness Service | [CVE-2026-95944](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95944) | Windows App Readiness Service Tampering Vulnerability | Important |
| Windows AppContainer | [CVE-2026-96018](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96018) | Windows AppContainer Information Disclosure Vulnerability | Important |
| Windows AppX Deployment Service | [CVE-2026-88224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88224) | Windows AppX Deployment Service Elevation of Privilege Vulnerability | Important |
| Windows AppX Deployment Service | [CVE-2026-116714](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116714) | Windows AppX Deployment Service Elevation of Privilege Vulnerability | Important |
| Windows AppX Package Manager | [CVE-2026-96074](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96074) | Windows AppX Package Manager Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-119895](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119895) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-96155](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96155) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-96038](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96038) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-119894](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119894) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-105541](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105541) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-119888](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119888) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-119893](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119893) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Audio Service | [CVE-2026-121671](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121671) | Windows Audio Service Elevation of Privilege Vulnerability | Important |
| Windows Autopilot | [CVE-2026-122175](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122175) | Windows Autopilot Elevation of Privilege Vulnerability | Important |
| Windows Background Intelligent Transfer Service (BITS) | [CVE-2026-105554](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105554) | Windows Background Intelligent Transfer Service (BITS) Elevation of Privilege Vulnerability | Important |
| Windows Backup Engine | [CVE-2026-119405](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119405) | Windows Backup Engine Elevation of Privilege Vulnerability | Important |
| Windows Bind Filter Driver | [CVE-2026-70182](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70182) | Windows Bind Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Biometric Service | [CVE-2026-96127](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96127) | Windows Biometric Service Elevation of Privilege Vulnerability | Important |
| Windows Biometric Service | [CVE-2026-95877](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95877) | Windows Biometric Service Elevation of Privilege Vulnerability | Important |
| Windows Biometric Service | [CVE-2026-88239](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88239) | Windows Biometric Service Elevation of Privilege Vulnerability | Important |
| Windows BitLocker | [CVE-2026-119832](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119832) | Windows BitLocker Security Feature Bypass Vulnerability | Important |
| Windows BitLocker | [CVE-2026-97015](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97015) | Windows BitLocker Security Feature Bypass Vulnerability | Important |
| Windows Bluetooth A2DP driver | [CVE-2026-88187](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88187) | Windows Bluetooth A2DP driver Elevation of Privilege Vulnerability | Important |
| Windows Bluetooth Port Driver | [CVE-2026-95996](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95996) | Windows Bluetooth Port Driver Elevation of Privilege Vulnerability | Important |
| Windows Bluetooth Service | [CVE-2026-88213](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88213) | Windows Bluetooth Service Elevation of Privilege Vulnerability | Important |
| Windows Bluetooth Service | [CVE-2026-96001](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96001) | Windows Bluetooth Service Information Disclosure Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-112761](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112761) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-119401](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119401) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-88221](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88221) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-119402](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119402) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-119403](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119403) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-94529](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94529) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-113762](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113762) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broadcast DVR User Service | [CVE-2026-95871](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95871) | Windows Broadcast DVR User Service Elevation of Privilege Vulnerability | Important |
| Windows Broker Infrastructure Service | [CVE-2026-96156](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96156) | Windows Broker Infrastructure Service Information Disclosure Vulnerability | Important |
| Windows Brokering File System | [CVE-2026-95979](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95979) | Windows Brokering File System Elevation of Privilege Vulnerability | Important |
| Windows Brokering File System | [CVE-2026-88245](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88245) | Windows Brokering File System Elevation of Privilege Vulnerability | Important |
| Windows Brokering File System | [CVE-2026-85929](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85929) | Microsoft Brokering File System Elevation of Privilege Vulnerability | Important |
| Windows Brokering File System | [CVE-2026-96097](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96097) | Windows Brokering File System Elevation of Privilege Vulnerability | Important |
| Windows Camera Frame Server Monitor | [CVE-2026-88238](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88238) | Windows Camera Frame Server Monitor Elevation of Privilege Vulnerability | Important |
| Windows Camera Frame Server Monitor | [CVE-2026-85942](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85942) | Windows Camera Frame Server Monitor Elevation of Privilege Vulnerability | Important |
| Windows Camera Frame Server Monitor | [CVE-2026-88232](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88232) | Windows Camera Frame Server Monitor Elevation of Privilege Vulnerability | Important |
| Windows CD-ROM Driver | [CVE-2026-108404](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108404) | Windows CD-ROM Driver Remote Code Execution Vulnerability | Important |
| Windows CD-ROM Driver | [CVE-2026-108405](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108405) | Windows CD-ROM Driver Elevation of Privilege Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-122165](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122165) | Windows Client for NFS Elevation of Privilege Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-95885](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95885) | Windows Client for NFS Elevation of Privilege Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-118141](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118141) | Windows Client for NFS Remote Code Execution Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-88249](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88249) | Windows Client for NFS Remote Code Execution Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-119404](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119404) | Windows Client for NFS Security Feature Bypass Vulnerability | Important |
| Windows Client for NFS | [CVE-2026-118138](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118138) | Windows Client for NFS Elevation of Privilege Vulnerability | Important |
| Windows Clipboard Virtual Channel Extension | [CVE-2026-96162](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96162) | Windows Clipboard Virtual Channel Extension Elevation of Privilege Vulnerability | Important |
| Windows Cloud Files Mini Filter Driver | [CVE-2026-112810](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112810) | Windows Cloud Files Mini Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Cloud Files Mini Filter Driver | [CVE-2026-112803](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112803) | Windows Cloud Files Mini Filter Driver Information Disclosure Vulnerability | Important |
| Windows Cloud Files Mini Filter Driver | [CVE-2026-105569](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105569) | Windows Cloud Files Mini Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Cloud Files Mini Filter Driver | [CVE-2026-119974](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119974) | Windows Cloud Files Mini Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Cloud Files Mini Filter Driver | [CVE-2026-112763](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112763) | Windows Cloud Files Mini Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows CNG Key Isolation Service | [CVE-2026-103571](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-103571) | Windows CNG Key Isolation Service Elevation of Privilege Vulnerability | Important |
| Windows COM | [CVE-2026-112968](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112968) | Windows COM Elevation of Privilege Vulnerability | Important |
| Windows COM | [CVE-2026-105533](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105533) | Windows COM Elevation of Privilege Vulnerability | Important |
| Windows COM | [CVE-2026-94531](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94531) | Windows COM Elevation of Privilege Vulnerability | Important |
| Windows COM+ Event System Service | [CVE-2026-113767](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113767) | Windows COM+ Event System Service Elevation of Privilege Vulnerability | Important |
| Windows COM+ Event System Service | [CVE-2026-113769](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113769) | Windows COM+ Event System Service Elevation of Privilege Vulnerability | Important |
| Windows COM+ Event System Service | [CVE-2026-119855](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119855) | Windows COM+ Event System Service Information Disclosure Vulnerability | Important |
| Windows Composite Image File System | [CVE-2026-112809](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112809) | Windows Composite Image File System Information Disclosure Vulnerability | Important |
| Windows Connected User Experiences and Telemetry | [CVE-2026-96072](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96072) | Windows Connected User Experiences and Telemetry Elevation of Privilege Vulnerability | Important |
| Windows Connected User Experiences and Telemetry | [CVE-2026-96101](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96101) | Windows Connected User Experiences and Telemetry Information Disclosure Vulnerability | Important |
| Windows Connected User Experiences and Telemetry | [CVE-2026-96088](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96088) | Windows Connected User Experiences and Telemetry Elevation of Privilege Vulnerability | Important |
| Windows Connection Manager Service | [CVE-2026-96043](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96043) | Windows Connection Manager Service Elevation of Privilege Vulnerability | Important |
| Windows Connection Manager Service | [CVE-2026-96042](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96042) | Windows Connection Manager Service Elevation of Privilege Vulnerability | Important |
| Windows Container Isolation FS Filter Driver (unionfs.sys) | [CVE-2026-112753](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112753) | Windows Container Isolation FS Filter Driver (unionfs.sys) Elevation of Privilege Vulnerability | Important |
| Windows Container Isolation FS Filter Driver (unionfs.sys) | [CVE-2026-113761](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113761) | Windows Container Isolation FS Filter Driver (unionfs.sys) Elevation of Privilege Vulnerability | Important |
| Windows Container Isolation FS Filter Driver (unionfs.sys) | [CVE-2026-113771](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113771) | Windows Container Isolation FS Filter Driver (unionfs.sys) Elevation of Privilege Vulnerability | Important |
| Windows Container Manager Service | [CVE-2026-105562](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105562) | Windows Container Manager Service Information Disclosure Vulnerability | Important |
| Windows Cred SSProvider Protocol | [CVE-2026-119962](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119962) | Windows CredSSP Remote Code Execution Vulnerability | Critical |
| Windows Credential Manager | [CVE-2026-119393](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119393) | Windows Credential Manager Elevation of Privilege Vulnerability | Important |
| Windows Credential User Interface | [CVE-2026-96978](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96978) | Windows Credential User Interface Elevation of Privilege Vulnerability | Important |
| Windows Defender Firewall Service | [CVE-2026-112758](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112758) | Windows Defender Firewall Service Elevation of Privilege Vulnerability | Important |
| Windows Deployment Services | [CVE-2026-105558](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105558) | Windows Deployment Services Remote Code Execution Vulnerability | Important |
| Windows Deployment Services | [CVE-2026-112977](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112977) | Windows Deployment Services Information Disclosure Vulnerability | Important |
| Windows Deployment Services | [CVE-2026-119951](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119951) | Windows Deployment Services Remote Code Execution Vulnerability | Critical |
| Windows Deployment Services | [CVE-2026-118213](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118213) | Windows Deployment Services Information Disclosure Vulnerability | Important |
| Windows Deployment Services | [CVE-2026-113818](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113818) | Windows Deployment Services Information Disclosure Vulnerability | Important |
| Windows Device Association Service | [CVE-2026-119874](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119874) | Windows Device Association Service Elevation of Privilege Vulnerability | Important |
| Windows Device Association Service | [CVE-2026-112743](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112743) | Windows Device Association Service Elevation of Privilege Vulnerability | Important |
| Windows Device Association Service | [CVE-2026-119866](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119866) | Windows Device Association Service Elevation of Privilege Vulnerability | Important |
| Windows Device Association Service | [CVE-2026-119844](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119844) | Windows Device Association Service Elevation of Privilege Vulnerability | Important |
| Windows Device Inventory | [CVE-2026-113750](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113750) | Windows Device Inventory Elevation of Privilege Vulnerability | Important |
| Windows Devices Human Interface | [CVE-2026-113817](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113817) | Windows Devices Human Interface Elevation of Privilege Vulnerability | Important |
| Windows DHCP Client | [CVE-2026-96115](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96115) | Windows DHCP Client Elevation of Privilege Vulnerability | Important |
| Windows DHCP Client | [CVE-2026-88240](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88240) | Windows DHCP Client Elevation of Privilege Vulnerability | Important |
| Windows DHCP Client | [CVE-2026-113863](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113863) | Windows DHCP Client Elevation of Privilege Vulnerability | Important |
| Windows DHCP Client | [CVE-2026-118739](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118739) | Windows DHCP Client Denial of Service Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-105560](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105560) | Windows DHCP Server Remote Code Execution Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-72998](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-72998) | Windows DHCP Server Remote Code Execution Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-119890](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119890) | Windows DHCP Server Denial of Service Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-96134](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96134) | Windows DHCP Server Denial of Service Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-105588](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105588) | Windows DHCP Server Elevation of Privilege Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-105557](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105557) | Windows DHCP Server Information Disclosure Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-88216](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88216) | Windows DHCP Server Remote Code Execution Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-88243](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88243) | Windows DHCP Server Remote Code Execution Vulnerability | Important |
| Windows DHCP Server | [CVE-2026-113773](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113773) | Windows DHCP Server Spoofing Vulnerability | Important |
| Windows Diagnostic Policy Service | [CVE-2026-112800](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112800) | Windows Diagnostic Policy Service Elevation of Privilege Vulnerability | Important |
| Windows Diagnostic Policy Service | [CVE-2026-95934](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95934) | Windows Diagnostic Policy Service Elevation of Privilege Vulnerability | Important |
| Windows Diagnostic Policy Service | [CVE-2026-95976](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95976) | Windows Diagnostic Policy Service Elevation of Privilege Vulnerability | Important |
| Windows DIAL Client | [CVE-2026-96076](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96076) | Windows DIAL Client Elevation of Privilege Vulnerability | Important |
| Windows DirectX | [CVE-2026-94507](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94507) | DirectX Elevation of Privilege Vulnerability | Important |
| Windows Distributed File System (DFS) | [CVE-2026-118142](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118142) | Windows Distributed File System (DFS) Elevation of Privilege Vulnerability | Important |
| Windows Distributed Transaction Coordinator | [CVE-2026-119919](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119919) | Windows Distributed Transaction Coordinator Elevation of Privilege Vulnerability | Important |
| Windows Distributed Transaction Coordinator | [CVE-2026-119917](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119917) | Windows Distributed Transaction Coordinator Elevation of Privilege Vulnerability | Important |
| Windows DNS | [CVE-2026-113855](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113855) | Windows DNS Remote Code Execution Vulnerability | Important |
| Windows DNS | [CVE-2026-96972](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96972) | Windows DNS Server Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-105520](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105520) | Windows DNS Elevation of Privilege Vulnerability | Important |
| Windows DNS | [CVE-2026-96987](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96987) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96986](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96986) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96985](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96985) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-88218](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88218) | Windows DNS Remote Code Execution Vulnerability | Important |
| Windows DNS | [CVE-2026-119905](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119905) | Windows DNS Spoofing Vulnerability | Important |
| Windows DNS | [CVE-2026-119971](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119971) | Windows DNS Server Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96176](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96176) | Windows DNS Denial of Service Vulnerability | Important |
| Windows DNS | [CVE-2026-96980](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96980) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96976](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96976) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96984](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96984) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-119970](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119970) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-96983](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96983) | Windows DNS Denial of Service Vulnerability | Important |
| Windows DNS | [CVE-2026-119953](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119953) | Windows DNS Elevation of Privilege Vulnerability | Important |
| Windows DNS | [CVE-2026-96970](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96970) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-108425](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108425) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-109463](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109463) | Windows DNS Remote Code Execution Vulnerability | Important |
| Windows DNS | [CVE-2026-96988](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96988) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-105579](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105579) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DNS | [CVE-2026-97006](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97006) | Windows DNS Information Disclosure Vulnerability | Important |
| Windows DPAPI (Data Protection Application Programming Interface) | [CVE-2026-113763](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113763) | Windows DPAPI (Data Protection Application Programming Interface) Elevation of Privilege Vulnerability | Important |
| Windows DWM Core Library | [CVE-2026-105575](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105575) | Windows DWM Core Library Elevation of Privilege Vulnerability | Important |
| Windows DWM Core Library | [CVE-2026-112986](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112986) | Windows DWM Core Library Elevation of Privilege Vulnerability | Important |
| Windows DWM Core Library | [CVE-2026-105583](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105583) | Windows DWM Core Library Elevation of Privilege Vulnerability | Important |
| Windows DWM Core Library | [CVE-2026-105582](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105582) | Windows DWM Core Library Elevation of Privilege Vulnerability | Important |
| Windows Encrypting File System (EFS) | [CVE-2026-105527](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105527) | Windows Encrypting File System (EFS) Denial of Service Vulnerability | Important |
| Windows Encrypting File System (EFS) | [CVE-2026-96973](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96973) | Windows Encrypting File System (EFS) Elevation of Privilege Vulnerability | Important |
| Windows Enhanced Storage | [CVE-2026-119394](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119394) | Windows Enhanced Storage Remote Code Execution Vulnerability | Important |
| Windows Error Reporting | [CVE-2026-96153](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96153) | Windows Error Reporting Elevation of Privilege Vulnerability | Important |
| Windows Error Reporting | [CVE-2026-105540](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105540) | Windows Error Reporting Elevation of Privilege Vulnerability | Important |
| Windows Error Reporting | [CVE-2026-85862](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85862) | Windows Error Reporting Elevation of Privilege Vulnerability | Important |
| Windows Error Reporting | [CVE-2026-94525](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94525) | Windows Error Reporting Elevation of Privilege Vulnerability | Important |
| Windows Error Reporting | [CVE-2026-95947](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95947) | Windows Error Reporting Elevation of Privilege Vulnerability | Important |
| Windows eSCL Scanner | [CVE-2026-112801](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112801) | Windows eSCL Scanner Elevation of Privilege Vulnerability | Important |
| Windows eSCL Scanner | [CVE-2026-95956](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95956) | Windows eSCL Scanner Remote Code Execution Vulnerability | Important |
| Windows Event Collector Service | [CVE-2026-112793](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112793) | Windows Event Collector Service Elevation of Privilege Vulnerability | Important |
| Windows Event Collector Service | [CVE-2026-112796](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112796) | Windows Event Collector Service Elevation of Privilege Vulnerability | Important |
| Windows Event Logging Service | [CVE-2026-95997](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95997) | Windows Event Logging Service Elevation of Privilege Vulnerability | Important |
| Windows Event Viewer | [CVE-2026-95977](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95977) | Windows Event Viewer Information Disclosure Vulnerability | Important |
| Windows exFAT File System | [CVE-2026-112766](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112766) | Windows exFAT File System Elevation of Privilege Vulnerability | Important |
| Windows exFAT File System | [CVE-2026-112804](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112804) | Windows exFAT File System Elevation of Privilege Vulnerability | Important |
| Windows Failover Cluster | [CVE-2026-119869](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119869) | Windows Failover Cluster Elevation of Privilege Vulnerability | Important |
| Windows Fast FAT Driver | [CVE-2026-113751](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113751) | Windows Fast FAT Driver Elevation of Privilege Vulnerability | Important |
| Windows Feedback Hub | [CVE-2026-96075](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96075) | Windows Feedback Hub Elevation of Privilege Vulnerability | Important |
| Windows File Server Resource Management Service | [CVE-2026-108415](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108415) | Windows File Server Resource Management Service Elevation of Privilege Vulnerability | Important |
| Windows File Server Resource Management Service | [CVE-2026-108416](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108416) | Windows File Server Resource Management Service Elevation of Privilege Vulnerability | Important |
| Windows File Server Resource Management Service | [CVE-2026-108421](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108421) | Windows File Server Resource Management Service Elevation of Privilege Vulnerability | Important |
| Windows File Server Resource Management Service | [CVE-2026-113765](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113765) | Windows File Server Resource Management Service Elevation of Privilege Vulnerability | Important |
| Windows FileCrypt Driver | [CVE-2026-113754](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113754) | Windows FileCrypt Driver Information Disclosure Vulnerability | Important |
| Windows FileCrypt Driver | [CVE-2026-113757](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113757) | Windows FileCrypt Driver Information Disclosure Vulnerability | Important |
| Windows FileCrypt Driver | [CVE-2026-113756](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113756) | Windows FileCrypt Driver Security Feature Bypass Vulnerability | Important |
| Windows Filter Manager | [CVE-2026-113755](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113755) | Windows Filter Manager Elevation of Privilege Vulnerability | Important |
| Windows Filter Manager | [CVE-2026-121673](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121673) | Windows Filter Manager Elevation of Privilege Vulnerability | Important |
| Windows Filtering Platform (WFP) | [CVE-2026-88215](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88215) | Windows Filtering Platform (WFP) Elevation of Privilege Vulnerability | Important |
| Windows Filtering Platform (WFP) | [CVE-2026-112756](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112756) | Windows Filtering Platform (WFP) Elevation of Privilege Vulnerability | Important |
| Windows Filtering Platform (WFP) | [CVE-2026-105553](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105553) | Windows Filtering Platform (WFP) Elevation of Privilege Vulnerability | Important |
| Windows FTP Service | [CVE-2026-118137](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118137) | Windows FTP Service Elevation of Privilege Vulnerability | Important |
| Windows Function Discovery Resource Publication | [CVE-2026-125134](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-125134) | Windows Function Discovery Resource Publication Remote Code Execution Vulnerability | Critical |
| Windows Function Discovery Resource Publication | [CVE-2026-119907](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119907) | Windows Function Discovery Resource Publication Elevation of Privilege Vulnerability | Important |
| Windows Function Discovery SSDP Provider | [CVE-2026-118145](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118145) | Windows Function Discovery SSDP Provider Remote Code Execution Vulnerability | Critical |
| Windows GDI | [CVE-2026-108407](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108407) | Windows GDI Elevation of Privilege Vulnerability | Important |
| Windows GDI | [CVE-2026-108424](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108424) | Windows GDI Information Disclosure Vulnerability | Important |
| Windows GDI | [CVE-2026-94527](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94527) | Windows GDI Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-125137](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-125137) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Critical |
| Windows Graphics Kernel | [CVE-2026-96133](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96133) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95922](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95922) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95932](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95932) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95942](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95942) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96137](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96137) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95938](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95938) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95935](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95935) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96144](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96144) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96126](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96126) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95879](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95879) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95888](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95888) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-94519](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94519) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-119841](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119841) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96048](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96048) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95895](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95895) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96122](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96122) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96124](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96124) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95909](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95909) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95906](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95906) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-88217](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88217) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95946](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95946) | Windows Graphics Kernel Information Disclosure Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95971](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95971) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96160](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96160) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95950](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95950) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-119966](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119966) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Critical |
| Windows Graphics Kernel | [CVE-2026-96171](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96171) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-96168](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96168) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95966](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95966) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95953](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95953) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95948](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95948) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95974](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95974) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95991](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95991) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95983](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95983) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows Graphics Kernel | [CVE-2026-95973](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95973) | Windows Graphics Kernel Elevation of Privilege Vulnerability | Important |
| Windows HTTP.sys | [CVE-2026-95923](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95923) | Windows HTTP.sys Elevation of Privilege Vulnerability | Important |
| Windows HTTP.sys | [CVE-2026-119942](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119942) | HTTP.sys Information Disclosure Vulnerability | Important |
| Windows HTTP.sys | [CVE-2026-119992](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119992) | Windows HTTP.sys Elevation of Privilege Vulnerability | Important |
| Windows HTTP.sys | [CVE-2026-119946](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119946) | HTTP.sys Information Disclosure Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-119391](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119391) | Windows Hyper-V Elevation of Privilege Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-96965](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96965) | Windows Hyper-V Denial of Service Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-113861](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113861) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-119960](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119960) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-119826](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119826) | Windows Hyper-V Elevation of Privilege Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-113753](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113753) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-119385](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119385) | Windows Hyper-V Denial of Service Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-113860](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113860) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-113856](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113856) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-113864](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113864) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-119947](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119947) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-119955](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119955) | Windows Hyper-V Denial of Service Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-113865](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113865) | Windows Hyper-V Elevation of Privilege Vulnerability | Critical |
| Windows Hyper-V | [CVE-2026-95913](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95913) | Windows Hyper-V Denial of Service Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-119959](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119959) | Windows Hyper-V Spoofing Vulnerability | Important |
| Windows Hyper-V | [CVE-2026-95910](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95910) | Windows Hyper-V Security Feature Bypass Vulnerability | Important |
| Windows IKE Extension | [CVE-2026-122169](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122169) | Windows IKE Extension Spoofing Vulnerability | Important |
| Windows Image Acquisition | [CVE-2026-122163](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122163) | Windows Image Acquisition Remote Code Execution Vulnerability | Important |
| Windows Imaging Component | [CVE-2026-96164](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96164) | Windows Imaging Component Remote Code Execution Vulnerability | Important |
| Windows Input System | [CVE-2026-119862](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119862) | Windows Input System Elevation of Privilege Vulnerability | Important |
| Windows Input System | [CVE-2026-119916](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119916) | Windows Input System Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-105532](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105532) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96028](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96028) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119838](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119838) | Windows Installer Information Disclosure Vulnerability | Important |
| Windows Installer | [CVE-2026-112789](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112789) | Windows Installer Information Disclosure Vulnerability | Important |
| Windows Installer | [CVE-2026-105545](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105545) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96062](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96062) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119831](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119831) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119865](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119865) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119867](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119867) | Windows Installer Security Feature Bypass Vulnerability | Important |
| Windows Installer | [CVE-2026-119852](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119852) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96073](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96073) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96061](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96061) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-105543](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105543) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119398](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119398) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96060](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96060) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-105501](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105501) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96047](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96047) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-105507](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105507) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96027](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96027) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96029](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96029) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-95951](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95951) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-113847](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113847) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96004](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96004) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119929](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119929) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119399](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119399) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96026](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96026) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96019](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96019) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119887](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119887) | Windows Installer Information Disclosure Vulnerability | Important |
| Windows Installer | [CVE-2026-119892](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119892) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96046](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96046) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96152](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96152) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96008](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96008) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-119903](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119903) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96035](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96035) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96036](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96036) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Installer | [CVE-2026-96085](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96085) | Windows Installer Elevation of Privilege Vulnerability | Important |
| Windows Internet (wininet.dll) | [CVE-2026-96093](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96093) | Windows Internet (wininet.dll) Information Disclosure Vulnerability | Important |
| Windows Internet Connection Sharing (ICS) | [CVE-2026-119861](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119861) | Windows Internet Connection Sharing (ICS) Elevation of Privilege Vulnerability | Important |
| Windows Internet Connection Sharing (ICS) | [CVE-2026-118124](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118124) | Windows Internet Connection Sharing (ICS) Elevation of Privilege Vulnerability | Important |
| Windows Internet Connection Sharing (ICS) | [CVE-2026-119860](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119860) | Windows Internet Connection Sharing (ICS) Elevation of Privilege Vulnerability | Important |
| Windows Internet Connection Sharing (ICS) | [CVE-2026-122179](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122179) | Windows Internet Connection Sharing (ICS) Elevation of Privilege Vulnerability | Important |
| Windows Internet Connection Sharing (ICS) | [CVE-2026-119859](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119859) | Windows Internet Connection Sharing (ICS) Elevation of Privilege Vulnerability | Important |
| Windows Internet Information Services | [CVE-2026-119961](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119961) | Windows Internet Information Services Remote Code Execution Vulnerability | Critical |
| Windows Internet Information Services | [CVE-2026-119936](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119936) | Windows Internet Information Services Denial of Service Vulnerability | Important |
| Windows Internet Information Services | [CVE-2026-119909](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119909) | Windows Internet Information Services Denial of Service Vulnerability | Important |
| Windows Inventory Backup | [CVE-2026-105584](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105584) | Windows Inventory Backup Information Disclosure Vulnerability | Important |
| Windows IP Translation Configuration Service | [CVE-2026-119871](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119871) | Windows IP Translation Configuration Service Elevation of Privilege Vulnerability | Important |
| Windows iSCSI | [CVE-2026-88234](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88234) | Windows iSCSI Remote Code Execution Vulnerability | Important |
| Windows iSCSI | [CVE-2026-95898](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95898) | Windows iSCSI Elevation of Privilege Vulnerability | Important |
| Windows iSCSI | [CVE-2026-105518](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105518) | Windows iSCSI Remote Code Execution Vulnerability | Important |
| Windows iSCSI | [CVE-2026-88231](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88231) | Windows iSCSI Information Disclosure Vulnerability | Important |
| Windows iSCSI | [CVE-2026-122177](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122177) | Windows iSCSI Elevation of Privilege Vulnerability | Important |
| Windows iSCSI Target Service | [CVE-2026-83684](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-83684) | Windows iSCSI Target Service Information Disclosure Vulnerability | Important |
| Windows Kerberos | [CVE-2026-85844](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85844) | Windows Kerberos Elevation of Privilege Vulnerability | Important |
| Windows Kerberos | [CVE-2026-96082](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96082) | Windows Kerberos Denial of Service Vulnerability | Important |
| Windows Kerberos | [CVE-2026-119940](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119940) | Windows Kerberos Denial of Service Vulnerability | Important |
| Windows Kerberos | [CVE-2026-70240](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70240) | Windows Kerberos Denial of Service Vulnerability | Important |
| Windows Kerberos | [CVE-2026-122164](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122164) | Windows Kerberos Elevation of Privilege Vulnerability | Important |
| Windows Kerberos | [CVE-2026-119847](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119847) | Windows Kerberos Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-119918](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119918) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-105513](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105513) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-119868](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119868) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-105504](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105504) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-96031](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96031) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-112802](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112802) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-112805](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112805) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-95988](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95988) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-95905](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95905) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-105552](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105552) | Windows Kernel Information Disclosure Vulnerability | Important |
| Windows Kernel | [CVE-2026-119965](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119965) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-112973](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112973) | Windows Kernel Security Feature Bypass Vulnerability | Important |
| Windows Kernel | [CVE-2026-112969](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112969) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-105566](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105566) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-119935](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119935) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-119857](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119857) | Windows Kernel Information Disclosure Vulnerability | Important |
| Windows Kernel | [CVE-2026-96129](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96129) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-108403](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108403) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-114170](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114170) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-112790](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112790) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-119884](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119884) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-109473](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109473) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-94514](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-94514) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-96052](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96052) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-96058](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96058) | Windows Kernel Information Disclosure Vulnerability | Important |
| Windows Kernel | [CVE-2026-119912](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119912) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-122183](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122183) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel | [CVE-2026-118143](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118143) | Windows Kernel Elevation of Privilege Vulnerability | Important |
| Windows Kernel-Mode Drivers | [CVE-2026-96139](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96139) | Windows Kernel-Mode Drivers Elevation of Privilege Vulnerability | Important |
| Windows Language Experience Service | [CVE-2026-113766](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113766) | Windows Language Experience Service Tampering Vulnerability | Important |
| Windows Layer-2 Bridge Network Driver | [CVE-2026-108402](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108402) | Windows Layer-2 Bridge Network Driver Denial of Service Vulnerability | Important |
| Windows LDAP - Lightweight Directory Access Protocol | [CVE-2026-119958](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119958) | Windows LDAP - Lightweight Directory Access Protocol Remote Code Execution Vulnerability | Critical |
| Windows Link Layer Topology Discovery Protocol | [CVE-2026-116706](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116706) | Windows Link Layer Topology Discovery Protocol Remote Code Execution Vulnerability | Important |
| Windows Link Layer Topology Discovery Protocol | [CVE-2026-116707](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116707) | Windows Link Layer Topology Discovery Protocol Elevation of Privilege Vulnerability | Important |
| Windows Link Layer Topology Discovery Protocol | [CVE-2026-88244](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88244) | Windows Link Layer Topology Discovery Protocol Remote Code Execution Vulnerability | Important |
| Windows Link-Layer Discovery Protocol (LLDP) | [CVE-2026-112975](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112975) | Windows Link-Layer Discovery Protocol (LLDP) Denial of Service Vulnerability | Important |
| Windows Link-Layer Discovery Protocol (LLDP) | [CVE-2026-113816](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113816) | Windows Link-Layer Discovery Protocol (LLDP) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-88227](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88227) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-96016](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96016) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-96066](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96066) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-70231](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-70231) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-88228](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88228) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Security Authority Subsystem Service (LSASS) | [CVE-2026-85801](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85801) | Windows Local Security Authority Subsystem Service (LSASS) Elevation of Privilege Vulnerability | Important |
| Windows Local Session Manager (LSM) | [CVE-2026-95876](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95876) | Windows Local Session Manager (LSM) Elevation of Privilege Vulnerability | Important |
| Windows LUAFV | [CVE-2026-88230](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88230) | Windows LUA File Virtualization Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows LUAFV | [CVE-2026-96117](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96117) | Windows LUA File Virtualization Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-105580](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105580) | Windows Management Instrumentation Remote Code Execution Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-105546](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105546) | Windows Management Instrumentation Elevation of Privilege Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-112965](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112965) | Windows Management Instrumentation Information Disclosure Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-105503](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105503) | Windows Management Instrumentation Elevation of Privilege Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-108410](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108410) | Windows Management Instrumentation Information Disclosure Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-105524](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105524) | Windows Management Instrumentation Elevation of Privilege Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-95920](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95920) | Windows Management Instrumentation Elevation of Privilege Vulnerability | Important |
| Windows Management Instrumentation | [CVE-2026-112814](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112814) | Windows Management Instrumentation Elevation of Privilege Vulnerability | Important |
| Windows Management Services | [CVE-2026-119836](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119836) | Windows Management Services Information Disclosure Vulnerability | Important |
| Windows Maps | [CVE-2026-122182](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122182) | Windows Maps Elevation of Privilege Vulnerability | Important |
| Windows Media Player | [CVE-2026-88229](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88229) | Windows Media Player Remote Code Execution Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-118126](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118126) | Windows Message Queuing Elevation of Privilege Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-119848](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119848) | Windows Message Queuing Denial of Service Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-118125](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118125) | Windows Message Queuing Elevation of Privilege Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-119833](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119833) | Windows Message Queuing Elevation of Privilege Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-119963](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119963) | Windows Message Queuing Remote Code Execution Vulnerability | Critical |
| Windows Message Queuing | [CVE-2026-116710](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116710) | Windows Message Queuing Remote Code Execution Vulnerability | Critical |
| Windows Message Queuing | [CVE-2026-105515](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105515) | Windows Message Queuing Denial of Service Vulnerability | Important |
| Windows Message Queuing | [CVE-2026-119964](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119964) | Windows Message Queuing Remote Code Execution Vulnerability | Critical |
| Windows Message Queuing Queue Manager | [CVE-2026-109459](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-109459) | Windows Message Queuing Queue Manager Remote Code Execution Vulnerability | Critical |
| Windows Message Queuing Queue Manager | [CVE-2026-119967](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119967) | Windows Message Queuing Queue Manager Remote Code Execution Vulnerability | Critical |
| Windows Microsoft Account Sign-in Assistant | [CVE-2026-119921](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119921) | Windows Microsoft Account Sign-in Assistant Elevation of Privilege Vulnerability | Important |
| Windows Microsoft Account Sign-in Assistant | [CVE-2026-119816](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119816) | Windows Microsoft Account Sign-in Assistant Elevation of Privilege Vulnerability | Important |
| Windows Microsoft DirectMusic | [CVE-2026-95901](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95901) | Microsoft DirectMusic Remote Code Execution Vulnerability | Important |
| Windows Microsoft DirectMusic | [CVE-2026-95896](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95896) | Microsoft DirectMusic Remote Code Execution Vulnerability | Important |
| Windows Microsoft DirectMusic | [CVE-2026-95891](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95891) | Microsoft DirectMusic Remote Code Execution Vulnerability | Important |
| Windows Microsoft DirectMusic | [CVE-2026-95882](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95882) | Microsoft DirectMusic Remote Code Execution Vulnerability | Important |
| Windows MIDI Service Module | [CVE-2026-105574](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105574) | Windows MIDI Service Module Elevation of Privileges Vulnerability | Important |
| Windows MIDI Service Module | [CVE-2026-105565](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105565) | Windows MIDI Service Module Elevation of Privileges Vulnerability | Important |
| Windows MIDI Service Module | [CVE-2026-119901](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119901) | Windows MIDI Service Module Elevation of Privileges Vulnerability | Important |
| Windows Mobile Device Management | [CVE-2026-119944](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119944) | Windows Mobile Device Management Elevation of Privilege Vulnerability | Important |
| Windows Modern Device Management (MDM) | [CVE-2026-113820](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113820) | Windows Modern Device Management (MDM) Elevation of Privilege Vulnerability | Important |
| Windows Modern Device Management (MDM) | [CVE-2026-102219](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102219) | Windows Modern Device Management (MDM) Remote Code Execution Vulnerability | Important |
| Windows Modern Device Management (MDM) | [CVE-2026-112987](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112987) | Windows Modern Device Management (MDM) Elevation of Privilege Vulnerability | Important |
| Windows Modern Device Management (MDM) | [CVE-2026-96184](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96184) | Windows Modern Device Management (MDM) Elevation of Privilege Vulnerability | Important |
| Windows Modern Device Management (MDM) | [CVE-2026-119945](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119945) | Windows Modern Device Management (MDM) Remote Code Execution Vulnerability | Important |
| Windows Multiple Provider Router | [CVE-2026-118220](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118220) | Windows Multiple Provider Router Elevation of Privilege Vulnerability | Important |
| Windows NetBIOS | [CVE-2026-105551](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105551) | Windows NetBIOS Elevation of Privilege Vulnerability | Important |
| Windows NetBIOS | [CVE-2026-96971](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96971) | Windows NetBIOS Elevation of Privilege Vulnerability | Important |
| Windows NetBIOS | [CVE-2026-112798](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112798) | Windows NetBIOS Elevation of Privilege Vulnerability | Important |
| Windows NetBIOS | [CVE-2026-119873](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119873) | Windows NetBIOS Elevation of Privilege Vulnerability | Important |
| Windows Network Address Translation (NAT) | [CVE-2026-113862](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113862) | Windows Network Address Translation (NAT) Remote Code Execution Vulnerability | Critical |
| Windows Network Address Translation (NAT) | [CVE-2026-88212](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88212) | Windows Network Address Translation (NAT) Remote Code Execution Vulnerability | Important |
| Windows Network Connected Devices Auto-Setup Service | [CVE-2026-125136](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-125136) | Windows Network Connected Devices Auto-Setup Service Remote Code Execution Vulnerability | Critical |
| Windows Network Connection Broker | [CVE-2026-119821](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119821) | Windows Network Connection Broker Elevation of Privilege Vulnerability | Important |
| Windows Network Connection Broker | [CVE-2026-105525](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105525) | Windows Network Connection Broker Elevation of Privilege Vulnerability | Important |
| Windows Network Connection Broker | [CVE-2026-108406](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108406) | Windows Network Connection Broker Elevation of Privilege Vulnerability | Important |
| Windows Network File System | [CVE-2026-118736](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118736) | Windows Network File System Information Disclosure Vulnerability | Important |
| Windows NTFS | [CVE-2026-102200](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102200) | Windows NTFS Tampering Vulnerability | Important |
| Windows NTFS | [CVE-2026-105542](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105542) | Windows NTFS Remote Code Execution Vulnerability | Important |
| Windows NTFS | [CVE-2026-100223](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-100223) | Windows NTFS Elevation of Privilege Vulnerability | Important |
| Windows NTFS | [CVE-2026-113848](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113848) | Windows NTFS Remote Code Execution Vulnerability | Important |
| Windows NTFS | [CVE-2026-119933](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119933) | Windows NTFS Elevation of Privilege Vulnerability | Important |
| Windows NTFS | [CVE-2026-119900](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119900) | Windows NTFS Elevation of Privilege Vulnerability | Important |
| Windows NTFS | [CVE-2026-113844](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113844) | Windows NTFS Tampering Vulnerability | Important |
| Windows NTLM | [CVE-2026-121680](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121680) | Windows NTLM Spoofing Vulnerability | Important |
| Windows ODBC Driver | [CVE-2026-108411](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108411) | Microsoft ODBC Driver Remote Code Execution Vulnerability | Important |
| Windows OLE | [CVE-2026-95933](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95933) | Windows OLE Elevation of Privilege Vulnerability | Important |
| Windows OLE | [CVE-2026-96110](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96110) | Windows OLE Information Disclosure Vulnerability | Important |
| Windows OLE DB | [CVE-2026-105587](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105587) | Windows OLE DB Elevation of Privilege Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-121670](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-121670) | Windows Overlay Filter Elevation of Privilege Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-112750](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112750) | Windows Overlay Filter Information Disclosure Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-112813](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112813) | Windows Overlay Filter Elevation of Privilege Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-112760](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112760) | Windows Overlay Filter Elevation of Privilege Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-119822](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119822) | Windows Overlay Filter Elevation of Privilege Vulnerability | Important |
| Windows Overlay Filter | [CVE-2026-108409](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108409) | Windows Overlay Filter Information Disclosure Vulnerability | Important |
| Windows Partition Management Driver | [CVE-2026-105018](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105018) | Windows Partition Management Driver Elevation of Privilege Vulnerability | Important |
| Windows PCI Bus Driver | [CVE-2026-96981](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96981) | Windows PCI Bus Driver Elevation of Privilege Vulnerability | Important |
| Windows PCI Bus Driver | [CVE-2026-96992](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96992) | Windows PCI Bus Driver Elevation of Privilege Vulnerability | Important |
| Windows Performance Counters | [CVE-2026-88220](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88220) | Windows Performance Counters Information Disclosure Vulnerability | Important |
| Windows Performance Counters | [CVE-2026-95975](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95975) | Windows Performance Counters Remote Code Execution Vulnerability | Important |
| Windows Performance Counters | [CVE-2026-113768](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113768) | Windows Performance Counters Remote Code Execution Vulnerability | Important |
| Windows Performance Monitor | [CVE-2026-96993](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96993) | Windows Performance Monitor Remote Code Execution Vulnerability | Important |
| Windows Phone Service | [CVE-2026-96107](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96107) | Windows Phone Service Elevation of Privilege Vulnerability | Important |
| Windows Point-to-Point Protocol over Ethernet (PPPoE) | [CVE-2026-118123](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118123) | Windows Point-to-Point Protocol over Ethernet (PPPoE) Elevation of Privilege Vulnerability | Important |
| Windows Point-to-Point Protocol over Ethernet (PPPoE) | [CVE-2026-105511](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105511) | Windows Point-to-Point Protocol over Ethernet (PPPoE) Elevation of Privilege Vulnerability | Important |
| Windows PowerShell | [CVE-2026-124224](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124224) | PowerShell Elevation of Privilege Vulnerability | Important |
| Windows PowerShell | [CVE-2026-113815](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113815) | Microsoft PowerShell Security Feature Bypass Vulnerability | Important |
| Windows PowerShell | [CVE-2026-124226](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124226) | Microsoft PowerShell Security Feature Bypass Vulnerability | Important |
| Windows PowerShell | [CVE-2026-124225](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-124225) | Windows PowerShell Remote Code Execution Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112806](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112806) | Windows Print Spooler Components Information Disclosure Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-119939](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119939) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-105567](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105567) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-119950](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119950) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-105531](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105531) | Windows Print Spooler Components Information Disclosure Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-119913](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119913) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-113770](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113770) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112792](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112792) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112980](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112980) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112762](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112762) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112765](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112765) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112791](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112791) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112976](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112976) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-113752](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113752) | Windows Print Spooler Components Remote Code Execution Vulnerability | Critical |
| Windows Print Spooler Components | [CVE-2026-112978](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112978) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112797](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112797) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112808](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112808) | Windows Print Spooler Components Information Disclosure Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112811](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112811) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112981](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112981) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows Print Spooler Components | [CVE-2026-112752](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112752) | Windows Print Spooler Components Elevation of Privilege Vulnerability | Important |
| Windows PrintWorkflowUserSvc | [CVE-2026-119928](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119928) | Windows PrintWorkflowUserSvc Elevation of Privilege Vulnerability | Important |
| Windows PrintWorkflowUserSvc | [CVE-2026-119898](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119898) | Windows PrintWorkflowUserSvc Elevation of Privilege Vulnerability | Important |
| Windows Program Compatibility Assistant Service | [CVE-2026-88247](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88247) | Windows Program Compatibility Assistant Service Information Disclosure Vulnerability | Important |
| Windows Program Compatibility Assistant Service | [CVE-2026-123388](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-123388) | Windows Program Compatibility Assistant Service Elevation of Privilege Vulnerability | Important |
| Windows Projected File System | [CVE-2026-112799](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112799) | Windows Projected File System Elevation of Privilege Vulnerability | Important |
| Windows Projected File System | [CVE-2026-113764](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113764) | Windows Projected File System Information Disclosure Vulnerability | Important |
| Windows Projected File System Filter Driver | [CVE-2026-108414](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108414) | Windows Projected File System Filter Driver Elevation of Privilege Vulnerability | Important |
| Windows Push Notification Core | [CVE-2026-96023](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96023) | Windows Push Notification Core Elevation of Privilege Vulnerability | Important |
| Windows Push Notifications | [CVE-2026-95881](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95881) | Windows Push Notifications Elevation of Privilege Vulnerability | Important |
| Windows Raw Image Extension | [CVE-2026-114169](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114169) | Windows Raw Image Extension Remote Code Execution Vulnerability | Critical |
| Windows Raw Image Extension | [CVE-2026-114166](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-114166) | Microsoft Raw Image Extension Information Disclosure Vulnerability | Important |
| Windows Redirected Drive Buffering | [CVE-2026-108412](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108412) | Windows Redirected Drive Buffering System Elevation of Privilege Vulnerability | Important |
| Windows Redirected Drive Buffering | [CVE-2026-113772](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113772) | Windows Redirected Drive Buffering Information Disclosure Vulnerability | Important |
| Windows Remote Access API | [CVE-2026-119853](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119853) | Remote Access API Elevation of Privilege Vulnerability | Important |
| Windows Remote Access API | [CVE-2026-119396](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119396) | Windows Remote Access API Tampering Vulnerability | Important |
| Windows Remote Access Connection Manager | [CVE-2026-113843](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113843) | Windows Remote Access Connection Manager Elevation of Privilege Vulnerability | Important |
| Windows Remote Assistance | [CVE-2026-112751](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112751) | Windows Remote Assistance Elevation of Privilege Vulnerability | Important |
| Windows Remote Desktop | [CVE-2026-119932](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119932) | Windows Remote Desktop Denial of Service Vulnerability | Important |
| Windows Remote Desktop Services | [CVE-2026-119957](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119957) | Windows Remote Desktop Services Elevation of Privilege Vulnerability | Critical |
| Windows Remote Desktop Services | [CVE-2026-122166](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122166) | Windows Remote Desktop Services Elevation of Privilege Vulnerability | Important |
| Windows Remote Desktop Services | [CVE-2026-108401](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108401) | Remote Desktop Services Remote Code Execution Vulnerability | Important |
| Windows Remote Desktop Services | [CVE-2026-119882](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119882) | Windows Remote Desktop Services Information Disclosure Vulnerability | Important |
| Windows Remote Procedure Call | [CVE-2026-119972](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119972) | Remote Procedure Call Denial of Service Vulnerability | Important |
| Windows Remote Procedure Call Runtime | [CVE-2026-118737](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118737) | Remote Procedure Call Runtime Remote Code Execution Vulnerability | Critical |
| Windows Resilient File System (ReFS) | [CVE-2026-105509](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105509) | Windows Resilient File System (ReFS) Elevation of Privilege Vulnerability | Important |
| Windows Resilient File System (ReFS) | [CVE-2026-119386](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119386) | Windows Resilient File System (ReFS) Elevation of Privilege Vulnerability | Important |
| Windows Rich Text Edit Control | [CVE-2026-96081](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96081) | Windows Rich Text Edit Control Remote Code Execution Vulnerability | Important |
| Windows RNDIS | [CVE-2026-112755](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112755) | Windows RNDIS Elevation of Privilege Vulnerability | Important |
| Windows Sandbox | [CVE-2026-119906](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119906) | Windows Sandbox Elevation of Privilege Vulnerability | Important |
| Windows Schannel | [CVE-2026-119952](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119952) | Windows Schannel Remote Code Execution Vulnerability | Critical |
| Windows Secure Kernel Mode | [CVE-2026-112757](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112757) | Windows Secure Kernel Mode Information Disclosure Vulnerability | Important |
| Windows Secure Socket Tunneling Protocol (SSTP) | [CVE-2026-105561](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105561) | Windows Secure Socket Tunneling Protocol (SSTP) Denial of Service Vulnerability | Important |
| Windows Secure Socket Tunneling Protocol (SSTP) | [CVE-2026-105510](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105510) | Windows Secure Socket Tunneling Protocol (SSTP) Elevation of Privilege Vulnerability | Important |
| Windows Security Account Manager | [CVE-2026-112966](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112966) | Windows Security Account Manager Denial of Service Vulnerability | Important |
| Windows Security Account Manager | [CVE-2026-112795](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112795) | Windows Security Account Manager Denial of Service Vulnerability | Important |
| Windows Security Account Manager | [CVE-2026-122474](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122474) | Windows Security Account Manager Remote Protocol Security Feature Bypass Vulnerability | Important |
| Windows Security Center | [CVE-2026-113842](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113842) | Windows Security Center Elevation of Privilege Vulnerability | Important |
| Windows Sensor Data Service | [CVE-2026-88241](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88241) | Windows Sensor Data Service Elevation of Privilege Vulnerability | Important |
| Windows Server for NFS | [CVE-2026-118140](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118140) | Server for NFS Information Disclosure Vulnerability | Important |
| Windows Setup and Deployment | [CVE-2026-105547](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105547) | Windows Setup and Deployment Elevation of Privilege Vulnerability | Important |
| Windows Setup and Deployment | [CVE-2026-119914](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119914) | Windows Setup and Deployment Elevation of Privilege Vulnerability | Important |
| Windows Shell | [CVE-2026-105506](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105506) | Windows Shell Information Disclosure Vulnerability | Important |
| Windows Shell | [CVE-2026-97013](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97013) | Windows Shell Elevation of Privilege Vulnerability | Important |
| Windows Shell | [CVE-2026-102868](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-102868) | Windows Shell Information Disclosure Vulnerability | Important |
| Windows Shell | [CVE-2026-119817](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119817) | Windows Shell Elevation of Privilege Vulnerability | Important |
| Windows Shell | [CVE-2026-119938](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119938) | Windows Shell Remote Code Execution Vulnerability | Important |
| Windows Smart Card | [CVE-2026-95968](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95968) | Windows Smart Card Elevation of Privilege Vulnerability | Important |
| Windows Smart Card | [CVE-2026-118144](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-118144) | Windows Smart Card Elevation of Privilege Vulnerability | Important |
| Windows Smart Card | [CVE-2026-119383](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119383) | Windows Smart Card Elevation of Privilege Vulnerability | Important |
| Windows Smart Card | [CVE-2026-112794](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112794) | Windows Smart Card Elevation of Privilege Vulnerability | Important |
| Windows Smart Card | [CVE-2026-119835](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119835) | Windows Smart Card Elevation of Privilege Vulnerability | Important |
| Windows Smart Card | [CVE-2026-105549](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105549) | Windows Smart Card Information Disclosure Vulnerability | Important |
| Windows SMB | [CVE-2026-122176](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122176) | Windows SMB Remote Code Execution Vulnerability | Important |
| Windows SMB | [CVE-2026-119988](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119988) | Windows SMB Remote Code Execution Vulnerability | Important |
| Windows SMB Client | [CVE-2026-112971](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112971) | Windows SMB Client Elevation of Privilege Vulnerability | Important |
| Windows SMB Client | [CVE-2026-112812](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112812) | Windows SMB Client Elevation of Privilege Vulnerability | Important |
| Windows SMB Client | [CVE-2026-119870](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119870) | Windows SMB Client Elevation of Privilege Vulnerability | Important |
| Windows SMB Client | [CVE-2026-112970](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112970) | Windows SMB Client Elevation of Privilege Vulnerability | Important |
| Windows SMB Server | [CVE-2026-112972](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112972) | Windows SMBv3 Server Remote Code Execution Vulnerability | Important |
| Windows SMB Server Network Transport Driver (srvnet.sys) | [CVE-2026-113825](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113825) | Windows SMB Server Network Transport Driver (srvnet.sys) Remote Code Execution Vulnerability | Critical |
| Windows SSDP Service | [CVE-2026-85907](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-85907) | Windows Simple Search and Discovery Protocol (SSDP) Service Elevation of Privilege Vulnerability | Important |
| Windows State Repository Service | [CVE-2026-112979](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112979) | Windows State Repository Service Tampering Vulnerability | Important |
| Windows StateRepository API | [CVE-2026-95998](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95998) | Windows StateRepository API Tampering Vulnerability | Important |
| Windows Storage | [CVE-2026-105534](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105534) | Windows Storage Remote Code Execution Vulnerability | Important |
| Windows Storage | [CVE-2026-105529](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105529) | Windows Storage Elevation of Privilege Vulnerability | Important |
| Windows Storage | [CVE-2026-95889](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95889) | Windows Storage Elevation of Privilege Vulnerability | Important |
| Windows Storage | [CVE-2026-119389](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119389) | Windows Storage Elevation of Privilege Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-119851](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119851) | Windows Storage Spaces Controller Elevation of Privilege Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-119392](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119392) | Windows Storage Spaces Controller Elevation of Privilege Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-113814](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113814) | Windows Storage Spaces Controller Remote Code Execution Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-105024](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105024) | Windows Storage Spaces Controller Elevation of Privilege Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-122475](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122475) | Windows Storage Spaces Controller Remote Code Execution Vulnerability | Important |
| Windows Storage Spaces Controller | [CVE-2026-119908](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119908) | Windows Storage Spaces Controller Remote Code Execution Vulnerability | Important |
| Windows Storport Miniport Driver | [CVE-2026-119885](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119885) | Windows Storport Miniport Driver Elevation of Privilege Vulnerability | Important |
| Windows Storport Miniport Driver | [CVE-2026-119830](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119830) | Windows Storport Miniport Driver Elevation of Privilege Vulnerability | Important |
| Windows Storport Miniport Driver | [CVE-2026-119875](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119875) | Windows Storport Miniport Driver Information Disclosure Vulnerability | Important |
| Windows Storport Miniport Driver | [CVE-2026-119823](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119823) | Windows Storport Miniport Driver Remote Code Execution Vulnerability | Important |
| Windows Subsystem for Linux | [CVE-2026-119834](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119834) | Windows Subsystem for Linux Elevation of Privilege Vulnerability | Important |
| Windows Subsystem for Linux | [CVE-2026-119846](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119846) | Windows Subsystem for Linux Elevation of Privilege Vulnerability | Important |
| Windows Subsystem for Linux | [CVE-2026-88237](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88237) | Windows Subsystem for Linux Elevation of Privilege Vulnerability | Important |
| Windows System Events Broker | [CVE-2026-105530](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105530) | Windows System Events Broker Information Disclosure Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-95894](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95894) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-96845](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96845) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-122174](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122174) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-112759](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112759) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-88233](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-88233) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows Task Scheduler | [CVE-2026-96053](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96053) | Windows Task Scheduler Elevation of Privilege Vulnerability | Important |
| Windows TCP/IP | [CVE-2026-113859](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113859) | Windows TCP/IP Remote Code Execution Vulnerability | Critical |
| Windows TCP/IP | [CVE-2026-96077](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96077) | Windows TCP/IP Denial of Service Vulnerability | Important |
| Windows TCP/IP | [CVE-2026-96969](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96969) | Windows TCP/IP Elevation of Privilege Vulnerability | Important |
| Windows TCP/IP | [CVE-2026-96102](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96102) | Windows TCP/IP Elevation of Privilege Vulnerability | Important |
| Windows Telephony Service | [CVE-2026-116700](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-116700) | Windows Telephony Service Elevation of Privilege Vulnerability | Important |
| Windows Telephony Service | [CVE-2026-108413](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108413) | Windows Telephony Service Elevation of Privilege Vulnerability | Important |
| Windows Telephony Service | [CVE-2026-108408](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108408) | Windows Telephony Service Information Disclosure Vulnerability | Important |
| Windows Telephony Service | [CVE-2026-119886](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119886) | Windows Telephony Service Elevation of Privilege Vulnerability | Important |
| Windows Text Services Framework | [CVE-2026-96022](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96022) | Windows Text Services Framework Information Disclosure Vulnerability | Important |
| Windows Text Services Framework | [CVE-2026-119925](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119925) | Windows Text Services Framework Elevation of Privilege Vulnerability | Important |
| Windows Text Services Framework | [CVE-2026-119818](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119818) | Windows Text Services Framework Elevation of Privilege Vulnerability | Important |
| Windows Text Services Framework | [CVE-2026-119931](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119931) | Windows Text Services Framework Elevation of Privilege Vulnerability | Important |
| Windows TPM | [CVE-2026-119382](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119382) | Windows TPM Elevation of Privilege Vulnerability | Critical |
| Windows Universal Disk Format File System Driver (UDFS) | [CVE-2026-119837](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119837) | Windows Universal Disk Format File System Driver (UDFS) Elevation of Privilege Vulnerability | Important |
| Windows Universal Disk Format File System Driver (UDFS) | [CVE-2026-122984](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122984) | Windows Universal Disk Format File System Driver (UDFS) Elevation of Privilege Vulnerability | Important |
| Windows Universal Disk Format File System Driver (UDFS) | [CVE-2026-119840](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119840) | Windows Universal Disk Format File System Driver (UDFS) Elevation of Privilege Vulnerability | Important |
| Windows Update Stack | [CVE-2026-122162](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122162) | Windows Update Stack Information Disclosure Vulnerability | Important |
| Windows USB Audio Class driver (usbaudio.sys) | [CVE-2026-119829](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119829) | Windows USB Audio Class driver (usbaudio.sys) Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-95872](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95872) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-96055](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96055) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-119872](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119872) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-96005](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96005) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-96057](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96057) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-112764](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112764) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-96051](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96051) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-122167](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122167) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Driver | [CVE-2026-96056](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96056) | Windows USB Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Hub Driver | [CVE-2026-95999](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95999) | Windows USB Hub Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Hub Driver | [CVE-2026-95902](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95902) | Windows USB Hub Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Hub Driver | [CVE-2026-96041](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96041) | Windows USB Hub Driver Information Disclosure Vulnerability | Important |
| Windows USB Scanner Driver | [CVE-2026-119876](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119876) | Windows USB Scanner Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Video Driver | [CVE-2026-112990](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112990) | Windows USB Video Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Video Driver | [CVE-2026-95961](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95961) | Windows USB Video Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Video Driver | [CVE-2026-112984](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112984) | Windows USB Video Driver Elevation of Privilege Vulnerability | Important |
| Windows USB Video Driver | [CVE-2026-95965](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95965) | Windows USB Video Driver Elevation of Privilege Vulnerability | Important |
| Windows User Manager Service | [CVE-2026-95987](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95987) | Windows User Manager Service Elevation of Privilege Vulnerability | Important |
| Windows User Manager Service | [CVE-2026-96037](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96037) | Windows User Manager Service Elevation of Privilege Vulnerability | Important |
| Windows USM Communication Manager | [CVE-2026-97000](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97000) | Windows USM Communication Manager Elevation of Privilege Vulnerability | Important |
| Windows Virtual Filtering Platform (VFP) | [CVE-2026-95962](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95962) | Windows Virtual Filtering Platform (VFP) Remote Code Execution Vulnerability | Important |
| Windows VMSwitch | [CVE-2026-97002](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-97002) | Microsoft Windows VMSwitch Elevation of Privilege Vulnerability | Important |
| Windows Volume Shadow Copy | [CVE-2026-105017](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105017) | Volume Shadow Copy Elevation of Privilege Vulnerability | Important |
| Windows Volume Shadow Copy | [CVE-2026-119941](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119941) | Volume Shadow Copy Elevation of Privilege Vulnerability | Important |
| Windows Win32K | [CVE-2026-119827](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119827) | Windows Win32k Elevation of Privilege Vulnerability | Important |
| Windows Win32K | [CVE-2026-95893](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95893) | Win32k Information Disclosure Vulnerability | Important |
| Windows Win32K | [CVE-2026-119825](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119825) | Win32k Information Disclosure Vulnerability | Important |
| Windows Win32K | [CVE-2026-122170](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-122170) | Windows Win32k Elevation of Privilege Vulnerability | Important |
| Windows Win32K | [CVE-2026-105028](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105028) | Windows Win32k Elevation of Privilege Vulnerability | Important |
| Windows Win32K | [CVE-2026-119856](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119856) | Win32k Information Disclosure Vulnerability | Important |
| Windows Win32K | [CVE-2026-119910](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119910) | Win32k Information Disclosure Vulnerability | Important |
| Windows Win32K | [CVE-2026-119899](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-119899) | Windows Win32k Elevation of Privilege Vulnerability | Important |
| Windows WinHTTP | [CVE-2026-108423](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-108423) | Windows WinHTTP Information Disclosure Vulnerability | Important |
| Windows Wireless Networking | [CVE-2026-105589](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105589) | Windows Wireless Networking Elevation of Privilege Vulnerability | Important |
| Windows WLAN Service | [CVE-2026-96086](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96086) | Windows WLAN Service Denial of Service Vulnerability | Important |
| Windows Xbox Live Networking Service | [CVE-2026-112967](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-112967) | Windows Xbox Live Networking Service Remote Code Execution Vulnerability | Critical |
| Windows XWizard Framework | [CVE-2026-113760](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-113760) | Windows XWizard Framework Elevation of Privilege Vulnerability | Important |
| Winlogon | [CVE-2026-83563](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-83563) | Winlogon Elevation of Privilege Vulnerability | Important |
| Winlogon | [CVE-2026-105522](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105522) | Winlogon Elevation of Privilege Vulnerability | Important |
| Winsock | [CVE-2026-96994](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-96994) | Winsock Elevation of Privilege Vulnerability | Important |
| Winsock | [CVE-2026-105526](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-105526) | Winsock Elevation of Privilege Vulnerability | Important |
| Xbox | [CVE-2026-66801](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-66801) | Microsoft Xbox Remote Code Execution Vulnerability | Important |
| Xbox | [CVE-2026-95874](https://msrc.microsoft.com/update-guide/en-US/advisory/CVE-2026-95874) | Xbox Gaming Services Elevation of Privilege Vulnerability | Important |