---
title: What is DLL Sideloading – Bitdefender TechZone
source: "https://techzone.bitdefender.com/en/tech-explainers/what-is-dll-sideloading.html"
canonical_url: "https://techzone.bitdefender.com/en/tech-explainers/what-is-dll-sideloading.html"
language: en
domdown_version: 0.3.3
image: ../../css/image/corporate-logo.svg
description: "DLL sideloading exploits the Windows DLL search order to force legitimate, signed binaries to execute malicious code. Analyze passive and active exploitation methods used by threat actors to bypass application control and evade signature-based detection."
---
# What is DLL Sideloading– Bitdefender TechZone

Abstract

DLL sideloading exploits the Windows DLL search order to force legitimate, signed binaries to execute malicious code. Analyze passive and active exploitation methods used by threat actors to bypass application control and evade signature-based detection.

Welcome to the Bitdefender Tech Explainers about DLL sideloading attacks! In this article, we will focus on the type of attacks that frequently raise concerns, as they often involve libraries from well-known and trusted vendors.

## Welcome to the world of Dynamic Link Libraries

In the world of Microsoft Windows, much of the functionality of both operating system (OS) and third-party applications are provided by Dynamic Link Library (DLL) binaries. DLL files are Microsoft’s interpretation of the shared library concept. Instead of shipping all libraries (and libraries they are dependent on – and their dependencies – and so on) for each application, libraries are stored in a shared location, dynamically located, and loaded as needed.

When an executable needs to call a function from a library, it asks the OS to load that library into memory, typically by specifying the library name (without a full path). The loader locates the dynamic library and loads it into the calling process’s address space. There are a few different locations where these libraries can be located, and the OS will loop through all of them in a specific order until it can find the requested file.

![Dynamic Link Libraries3](../image/uuid-c485ba8e-0964-855f-e532-f52843cd2a71.jpg)

But unfortunately, the execution of this idea was not perfect, especially before the .NET framework was popularized. Working as an enterprise architect specializing in application delivery, I was dealing with hundreds of (often legacy) applications. Nothing triggered my stress more than remembering the “DLL hell” and endless hours spent troubleshooting COM registrations. In case you are not familiar with the term “DLL hell” (lucky you), the [definition from Wikipedia](https://en.wikipedia.org/wiki/DLL_Hell) nails it: _“…a term for the complications that arise when one works with dynamic-link libraries (DLLs) used with Microsoft Windows operating systems.”_

One of the challenges I’ve seen many times stems from installing a new application that includes a set of shared libraries. These libraries are stored in a location that overrides the search order for another application – and suddenly, this other application (that was stable for months) starts crashing because it is served an incompatible library version.

This [search order of the libraries](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order#standard-search-order-for-desktop-applications) is hardcoded in Windows OS. There are methods to modify the location from which libraries are loaded – using [DLL redirection](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-redirection), [manifest files](https://learn.microsoft.com/en-us/windows/win32/sbscs/manifests), or more commonly with isolation tools like MSIX app attach or the older App-V. The search order also changed in Windows 10 (and Windows Server 2012 R2) with the introduction of [SafeDllSearchMode](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order#standard-search-order-for-desktop-applications). Safe DLL mode is enabled by default on the newer operating systems.

![Dynamic Link Libraries](../image/uuid-baa45a1a-6914-66d8-e58d-1fac9683b3e6.jpg)

## What is DLL sideloading?

When dealing with library (in)compatibilities, one of the simplest (and most effective) methods was to take advantage of this search order loading. If an original developer wrote a code that depended on an outdated version of the library and deployed it to a shared location (C:\Windows\System32 for example), a simple fix is to copy this outdated library into the same folder as the executable. With this fix, the legacy application loads an older version of the binary, while all the other applications use the latest version from a shared location.

But this “hack” was not only used to solve compatibility issues – it could also be used for malicious purposes. There are two different approaches (and their variations) to how DLL search order hijacking can be weaponized by threat actors:

- **Passive Exploitation** –a standalone binary (highly trusted) is uploaded to a target system and used to sideload a malicious library.
- **Active Exploitation** – this approach is relying on the pre-installed applications or components vulnerable to loading a malicious library from an unsafe location.

Passive exploitation is less severe, but it is a recurring topic in media because it involves the use of libraries from well-known (and trusted) vendors. Bitdefender Labs previously documented how this technique is used in a research paper [Loading DLLs for illicit profit. A story about a Metamorfo distribution campaign](https://www.bitdefender.com/files/News/CaseStudies/study/333/Bitdefender-PR-Whitepaper-Metamorfo-creat4500-en-EN-GenericUse.pdf). To quote this research paper: “_During the time we monitored the Metamorfo campaign, we’ve seen 5 different software components, manufactured by respected software vendors, abused in the attack. Are any of these software companies at fault? Well, they only have the misfortune of developing popular software, as they become more prominent targets than less-known applications_.”

### Passive exploitation

This method of DLL sideloading exploitation is the most common. Threat actors usually prefer one of the older signed libraries, often from legacy operating systems or other highly trusted sources. The copy of this binary is then placed into a folder where threat actors have “write” access, together with a malicious library. This malicious library uses the filename that the binary is known to be looking for. After the initial binary is launched, it locates and sideloads the malicious library located in the same folder. This attack vector is based on a design flaw in the way that Windows OS locates libraries and vendors whose software is abused can’t do anything to prevent these attacks.

![Dynamic Link Libraries3](../image/uuid-66a7ef35-1899-b1cc-46e5-260588584589.jpg)

The loaded library inherits the same access rights as the binary – which must be executed by the threat actor. It is important to remember – this method is used only on systems that were already compromised, and it is useful only for **defense evasion**. The initial binary and malicious library are both standalone and deployed by a threat actor to an arbitrary folder; locally installed software is not part of this attack. The primary purpose is to avoid application control policies or more basic security solutions since the launching binary is digitally signed. In most cases, outdated versions of binaries are used, and there are a wide array of binaries for threat actors to choose from. It is a common practice that threat actors will try a variety of different executables to sideload their malicious library. With passive exploitation, the software that triggers the DLL sideloading does not need to be installed, only a standalone binary is typically used.

This method is used only on systems that were already compromised, and it is useful only for **defense evasion**. The goal for threat actors is to fool the installed security solution, not the executable that is sideloading the malicious library.

#### Real-World Example

A real-world example of this technique in action is documented in Bitdefender Labs' research on[Unfading Sea Haze](https://www.bitdefender.com/en-us/blog/businessinsights/deep-dive-into-unfading-sea-haze-a-new-threat-actor-in-the-south-china-sea), a likely nation-state threat actor targeting government and military organizations in South China Sea countries. The attackers copied legitimate Windows executables into attacker-controlled directories and placed malicious DLL files alongside them. When the executable ran, it loaded the malicious library instead of the intended system DLL — using a trusted, signed binary as cover to evade detection.

### Active exploitation

In the case of active exploitation, threat actors need to identify a pre-installed application (or OS component) that is vulnerable to DLL search order hijacking. A malicious library is loaded automatically by the calling process by placing a library with the right name in a location that is included in the search order. You can also think of this attack as a man-in-the-middle attack when the operating system is trying to locate the requested library. In some cases, the requested library might not even exist on the targeted system at all (for example debugging libraries). This is known as a Phantom DLL Hijacking.

The most serious result of using this technique can lead to privilege escalation – the malicious library is executed with the same access permissions as the calling process, which can be administrator or a SYSTEM in many cases. If the calling application is loading a library regularly (for example daily scheduled check for updates), search order hijacking can also help to establish persistence. Finally, this technique again helps with defense evasion. The malicious library can act as a proxy to the legitimate DLL that was replaced, so the vulnerable application behaves normally, and the presence of malicious code stays hidden.

![Dynamic Link Libraries3](../image/uuid-ab9e54af-1555-aed2-97bb-8481d28d88e6.jpg)

While this masquerading technique does not prevent detection by modern endpoint security solutions, it can be used to bypass software restriction policies or more simplistic security solutions. Threat actors need to identify software component that is vulnerable to search order hijacking and be able to save a malicious library in one of the folders that are searched.

## DLL Sideloading Mitigations

The best protection against modern cyber-attacks is a defense-in-depth architecture. After reducing your attack surface and implementing leading-edge prevention controls, lean on security operations to catch any incidents that may get through. Implement detection and response capabilities, either as a service ([Bitdefender MDR](https://www.youtube.com/watch?v=TRp7uLYLGiQ&ab_channel=BitdefenderEnterprise)) or by providing strong detection and response tools to your in-house security teams ([Bitdefender XDR](https://www.youtube.com/watch?v=ReBDrsyyiSY&ab_channel=BitdefenderEnterprise)).

Software developers are the first layer of defense against DLL sideloading attacks. Microsoft [provides a list of best practices](https://support.microsoft.com/en-us/topic/secure-loading-of-libraries-to-prevent-dll-preloading-attacks-d41303ec-0748-9211-f317-2edc819682e1) for the secure loading of libraries, all binaries from Bitdefender are following these best practices. To prevent active exploitation, make sure you are patching not only operating system files but also various third-party applications (learn more about the GravityZone [Patch Management](../security-layers/prevention/patch-management.html)solution). Applications vulnerable to privilege escalation through DLL sideloading are promptly patched, but those patches need to be applied effectively. As an additional layer of protection, Bitdefender employs Self-Protect technology to guard our product data (files, folders, registries etc.) against unauthorized access. Even if an attacker discovers an unknown vulnerability, access to external non-Bitdefender processes is detected and blocked.

For prevention, the most effective digital artifact that can lead to the detection of a DLL sideloading attack is the malicious library itself. Alert can be triggered by downloading a suspicious file (IP/domain/URL reputation capabilities are included with all Bitdefender GravityZone agents), when it is saved to a disk (on-access detection), or when it’s loaded into memory (one of the algorithms for monitoring process behavior).

For **active exploitation**, the most important question to ask is how could threat actors gain access to write to a location where the malicious binary is searched for. The typical search order includes only locations that require elevated rights. One of the prerequisites for active exploitation is that currently installed software must be vulnerable, and threat actors need write access to the system.

For **passive exploitation**, the system was already compromised when this detection evasion technique is used. The launching binary is not recognized as malicious, and behaves as intended, trying to locate and load a library without knowing it was compromised. Why would a threat actor put so much effort into finding these legitimate vulnerable executables when rundll32.exe or regsvr32.exe can be used to load any DLL? Both rundll32.exe and regsvr32.exe are common utilities used by threat actors, and detection and response tools like Bitdefender XDR are looking for these red flags. A valid digital signature and known publisher can further confuse some security tools. DLL sideloading allows threat actors to keep a low profile. This method can be effective only if a security solution doesn’t implement more advanced algorithms for monitoring process behavior. With modern endpoint security solutions, the malicious library should be detected and blocked.

For **active exploitation**, the most important question to ask is how could threat actors gain access to write to a location where the malicious binary is searched for. The typical search order includes only locations that require elevated rights.