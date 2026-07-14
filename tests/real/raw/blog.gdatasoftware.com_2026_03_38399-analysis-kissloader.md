---
title: "KissLoader: An Analysis and an Unexpected Encounter"
source: "https://blog.gdatasoftware.com/2026/03/38399-analysis-kissloader"
site_name: "G DATA | Trust in German Sicherheit"
canonical_url: "https://blog.gdatasoftware.com/2026/03/38399-analysis-kissloader"
language: en
domdown_version: 0.3.4
image: "https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/G_DATA_Blog_KissLoader_OGTag.jpg"
author:
  - "G DATA Security Center"
published: "2026-03-24T08:55:38"
description: "Analysis of Kiss Loader, a newly observed malware loader using WebDAV and Early Bird APC injection - ending in a rare live exchange with its developer."
---
# When Malware Talks Back: Real-Time Interaction with a Threat Actor During the Analysis of Kiss Loader

![Real-Time Interaction with a Threat Actor During the Analysis of Kiss Loader](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/G_DATA_Blog_KissLoader_Title.jpg)

[Kurios](https://blog.gdatasoftware.com/kuerios)

The author was actively developing a loader referred to as “Kiss Loader,” which, at the time of analysis, had not been previously observed and appears to be a newly developed tool representing a potential emerging threat. It employs techniques such as Early Bird APC injection, among others. The experience was both thrilling and remarkable, as the line between analyst and adversary briefly blurred. Before delving into this unusual encounter, it is important to first examine the sample that led us there.

## Technical Analysis Overview

To simplify the behavior of the sample, I mapped the execution into a multi-stage flow, as illustrated in Figure 1. The diagram highlights the key phases of execution.

[![Diagram showing a multi-stage cyberattack chain labeled “WebDAV Delivery,” starting with files “DKM_DE000922.pdf.url” and “DKM_DE80KS0095283.pdf.url” leading through “oa.wsh,” “ccv.js,” and “gg.bat” to “pol.bat” with steps like “Initial Access,” “Execution Trigger,” “Script Execution,” “Payload Retrieval,” and “Persistence Setup.” Further stages include “Payload Delivery” with “vwo.zip,” “Loader Deployment” via “so.py,” “Shellcode Decryption” using files “ov.bin,” “a.json,” “tv.bin,” “t.json,” and “Decrypted Payload” producing “VenomRAT” and “kryptik,” ending in “Payload Execution” and “Process Injection” into “explorer.exe,” alongside labels like “Decoy PDF Execution” and “rechnung-kleinunternehmer-data.pdf.”](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_1.png)](https://blog.gdatasoftware.com/fileadmin/_processed_/b/6/KissLoader_Figure_1_b241aa6be1.png)

(Figure 1: Kiss Loader Execution Chain Overview)

### Initial Access and WebDAV Delivery

The infection begins with a Windows Internet Shortcut file (DKM_DE000922.pdf.url) that triggers execution and connects to a remote WebDAV resource hosted through a TryCloudflare tunnel. TryCloudflare is a Cloudflare service that creates temporary public tunnels to locally hosted services without requiring domain registration or dedicated infrastructure. This enables the attacker to dynamically host and modify payloads.

### Execution Trigger and Script Execution

Among the files in the WebDAV directory is a secondary shortcut (DKM_DE80KS0095283.pdf.url), disguised as a PDF document, which requires user interaction to execute. One triggered, this shortcut launches a WSH script that chains into a JScript component. This layered execution flow enables controlled staging of the payload while minimizing direct exposure of later stages.

### Payload Retrieval and Staging

The JScript component retrieves and executes a batch script responsible for orchestrating the next steps. This includes displaying a decoy PDF to the user, establishing persistence by placing a batch script in the user’s Startup folder, and downloading additional payload components.

### Loader Deployment, Shellcode Decryption and Execution

The retrieved archive contains a Python-based loader, identified by the threat actor as “Kiss Loader,” which is deployed to decrypt payloads. Decryption keys are sourced from JSON configuration files, allowing the payload to remain concealed until runtime. The shellcode was generated using [Donut, an open-source tool that produces position-independent shellcode](https://github.com/TheWover/donut) for in-memory execution of .NET assemblies. To expedite analysis, I utilized a [dedicated Donut decryptor and extractor](https://github.com/volexity/donut-decryptor), enabling me to recover the embedded payloads from the BIN files. One of the payload was identified by our system as VenomRAT, which also resembles an AsyncRAT variant (See [here](https://www.welivesecurity.com/en/eset-research/unmasking-asyncrat-navigating-labyrinth-forks/), as well as [one of our earlier articles on AsyncRAT](https://blog.gdatasoftware.com/2025/05/38207-asyncrat-rust)), while the other was a .NET Reactor–protected utility. These components are subsequently prepared for execution, and this stage represents the transition from staging to active compromise.

### Process Injection

The final execution is achieved through injection into a legitimate process (explorer.exe) using an Early Bird APC technique, as shown in Figure 2. The loader creates the target process in a suspended state, preventing its main thread from executing immediately. It then allocates memory within the target process with executable permissions and writes the decrypted shellcode into the allocated region.

Instead of creating a new thread, the loader queues an Asynchronous Procedure Call (APC) to the primary thread of the suspended process.

Upon resuming the thread, the queued APC is executed before the process begins normal execution, allowing the injected shellcode to run under the context of a trusted process, thereby enhancing stealth and evading detection.

[![Python code for a method named inject(self, shellcode: bytes, target: str = "explorer.exe") -> bool with the comment Inject shellcode using Early Bird APC technique. It creates a suspended explorer.exe process, allocates and writes shellcode, queues QueueUserAPC, and resumes the thread.](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_2.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_2.png)

(Figure 2: Early Bird APC Injection Implementation in Kiss Loader)

## Key Observation

Both the supporting infrastructure and associated scripts of Kiss Loader were still under development at the time of analysis. The exposed WebDAV directory lacked access restrictions, which allowed me to directly enumerate and retrieve its contents. I also observed that the files were recently deployed, as I first identified them on March 10 (see Figure 3).

[![Web page titled “Index of /” listing files and folders with columns “Name,” “Type,” “Size,” and “Last modified.” Entries include “DOKUMENTE” (Directory), “ccv.js,” “desktop.ini,” “gg.bat,” “oa.wsh,” “pol.bat,” and “vwo.zip,” with a footer link “WsgiDAV/4.3.3 - Thu, 12 Mar 2026 00:34:17 GMT.”](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_3.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_3.png)

(Figure 3: Open WebDAV Repository Used for Payload Delivery)

Additionally, the scripts, particularly the “Kiss Loader,” exhibit clear signs of ongoing development. This is evident from the inclusion of testing utilities and helper functions intended for validating payloads and simulating execution scenarios (see Figure 4).

[![Python code section titled “LAB TESTING UTILITIES” defining a class LabTester with methods for shellcode validation and payload creation. It includes printed messages like “[-] Shellcode too small,” “[] Detected Meterpreter-like shellcode,” “[] Detected x64 shellcode,” and “[*] Detected x86 shellcode,” and a method create_test_payload() returning a byte sequence for a “calc.exe” payload.](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_4.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_4.png)

(Figure 4: Presence of Testing Utilities within Kiss Loader Code)

The code also contains extensive inline comments that describe key routines such as decryption and process injection, providing step-by-step context for logic. The level of detail in these comments may suggest the use of automated assisted code generation during development (see Figure 5).

[![Python script header with shebang “#!/usr/bin/env python3” and text “KISS Loader - Early Bird APC Injection for Lab Testing” plus usage line “python loader.py -p payload.bin [-k keys.json] [-t target.exe]”. It shows sections “DECRYPTION” and “INJECTION,” comments like “Simple XOR decryption” and “Load XOR key from JSON file,” and a class EarlyBirdInjector with notes about creating a suspended process and allocating memory, followed by a banner “KISS Loader - Lab Testing Edition Early Bird APC Injection.”](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_5.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_5.png)

(Figure 5: Embedded Comments Describing Decryption and Injection Logic)

Moreover, the loader produces verbose execution output, displaying detailed runtime information such as payload loading, decryption status, process creation, and injection steps. This level of output is typically associated with testing or debugging phases (see Figure 6).

[![Command prompt showing execution python.exe so.py -p tv.bin -k t.json in a Windows directory and a banner “KISS Loader - Lab Testing Edition Early Bird APC Injection.” Console output lists steps like “Loading payload: tv.bin,” “Loading key: t.json,” “Decrypting payload,” “Target process: explorer.exe,” “Creating suspended process,” “Writing shellcode,” “APC queued successfully,” and ends with “INJECTION SUCCESSFUL,” “Time: 0.01 seconds,” and “Check for target process behavior.”](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_6.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_6.png)

(Figure 6: Verbose Execution Output of Kiss Loader During Injection Process)

## My encounter with the Threat Actor

Since the resources hosted on WebDAV were still live and accessible, I executed the shortcut file within a controlled analysis environment to simulate its intended behavior and observe the overall execution flow. Using the parameters specified in the batch script, I proceeded with decrypting the embedded shellcode. While attempting to dump the decrypted payload, something immediately felt off. The command prompt suddenly terminated, followed by the abrupt shutdown of the analysis tools I had open: Notepad++, Process Explorer, and System Informer.

Then the cursor started moving on its own. I attempted to reopen the command prompt, but each attempt was instantly shut down. At that moment, I paused, took my hands off the keyboard, and even raised them to confirm that I was not interacting with the system. The cursor continued to move, clearly indicating that the behavior was not user-initiated. That realization was both notable and unexpected. Since this was my first time encountering “Kiss Loader,” I was driven to learn more about it and validate whether the observed activity was merely incidental or the result of deliberate remote access.

To test this, I re-executed the sample within the same controlled environment and left a Notepad window open containing a simple message: “Hello! Are you the author of this malware?”

I let the system run.

After roughly an hour, a response appeared, as shown in Figure 7.

[![Screenshot of a Notepad window titled “Untitled - Notepad” showing a chat between “Analyst:” and “Threat Actor:” about malware, including lines like “Hello! Are you the author of this malware?” and “early bird injection.” The conversation mentions locations such as “malawi and you” and “I am from [redacted],” and includes questions about payloads, malware development, and how the injection technique works.](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_7.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/KissLoader_Figure_7.png)

(Figure 7: Direct Interaction with Threat Actor via Notepad During Analysis)

The message was brief and informal, but it confirmed what I had suspected. The system was being actively accessed. What followed was an unexpected exchange. The individual on the other end appeared curious, even conversational, asking about my tools and whether I was an analyst. At one point, he acknowledged the nature of his own work, referring to it simply as “the malware,” and admitted to developing it in different forms while experimenting with various techniques.

As the conversation progressed, I steered it toward technical details. When asked about the injection method, the threat actor identified it as “early bird injection,” aligning with my prior analysis of the loader’s behavior. The discussion also revealed that the malware was still under development, reinforcing earlier observations from both the infrastructure and the code itself.

It is rare to engage directly with a threat actor during active development, and even rarer to receive confirmation of specific techniques in real time. The exchange was short. After a few responses, the threat actor stopped replying and did not reconnect in subsequent attempts. Still, the encounter left a lasting impression.

## Conclusion

We often study malware as artifacts, reduced to data points for detection and correlation. But behind every command and connection is a human who observes, adapts, and sometimes reveals more than intended. This case shows that analysis is not always one-sided. The boundary between analyst and adversary can become unexpectedly thin, turning observation into interaction.

Beyond the technical findings, this reinforces a key principle: analysis must remain within a controlled and isolated environment, as demonstrated in our handling of this case. We are not only analyzing code; at times, we are confronting the individuals behind it.

## IoC List

| 6abd118a0e6f5d67bfe1a79dacc1fd198059d8d66381563678f4e27ecb413fa7 | DKM_DE000922.pdf.url |
| --- | --- |
| e8f83d67a6b894399fad774ac196c71683de9ddca3cf0441bb95318f5136b553 | oa.wsh |
| 549c1f1998f22e06dde086f70f031dbf5a3481bd3c5370d7605006b6a20b5b0b | ccv.js |
| 6d62b39805529aefe0ac0270a0b805de6686d169348a90866bf47a07acde2284 | gg.bat |
| b4525711eafbd70288a9869825e5bb3045af072b5821cf8fbc89245aba57270a | pol.bat |
| e8dbdab0afac4decce1e4f8e74cc1c1649807f791c29df20ff72701a9086c2a0 | vwo.zip |
| 5cab6bf65f7836371d5c27fbfc20fe10c0c4a11784990ed1a3d2585fa5431ba6 | so.py |
| 20a585c4d153f5f551aaa509c8c1fa289fa6f964fe53f241ef9431a9390b3175 | tv.bin |
| 6a7c3029cd4f7ffe9a24ea5d696e1f612ada91b5a5ca5b28d4972d9c772051fd | t.json |
| 665f44b5a46947ad4fdac34a2dca4cf52b3e7e21cfa3bd0fc3ef10bd901ad651 | ov.bin |
| b3737f621eb2ee6d784a6b9d695b890a5f22ee69e96058c99d9048b479451fbd | a.json |
| 130ca411a3ef6c37dbd0b1746667b1386c3ac3be089c8177bc8bee5896ad2a02 | decrypted ov.bin (VenomRAT) |
| 2b40a8a79b6cf90160450caaad12f9c178707bead32bcc187deb02f71c25c354 | decrypted tv.bin (Kryptik) |

##### Share Article

##### Content

##### Topics

- [Kurios](https://blog.gdatasoftware.com/kuerios)
- [Malware](https://blog.gdatasoftware.com/malware)