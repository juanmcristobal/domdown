---
title: "Endgame Harvesting: Inside ACRStealer’s Modern Infrastructure"
source: "https://blog.gdatasoftware.com/2026/03/38385-acr-stealer-infrastructure"
site_name: "G DATA | Trust in German Sicherheit"
canonical_url: "https://blog.gdatasoftware.com/2026/03/38385-acr-stealer-infrastructure"
language: en
image: "https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/G_DATA_Blog_ACR_Stealer_OGTag.jpg"
author:
  - "G DATA Security Center"
published: "2026-03-12T08:44:48"
description: "ACRStealer is one of the many payloads that is used by HijackLoader. It seems to specifically target gamers, stealing data like Steam logins."
---
# Endgame Harvesting: Inside ACRStealer’s Modern Infrastructure

![Endgame Harvesting: Inside ACRStealer’s Modern Infrastructure](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/G_DATA_Blog_ACR_Stealer_Title.jpg)

[Malware](https://blog.gdatasoftware.com/malware)

_Written by John Dador_

From our previous article of [HijackLoader](https://blog.gdatasoftware.com/2026/02/38373-pivigames-spreads-hijackloader), the observed payload is a rebranded ACRStealer initially reported by [Proofpoint](https://www.proofpoint.com/us/blog/threat-insight/amatera-stealer-rebranded-acr-stealer-improved-evasion-sophistication) in the early half of last year. This updated variant follows similar evasion techniques and C2 initialization strategy to make it even stealthier. Since ACRStealer is known as a Malware as a Service (MaaS), it makes sense that it is now being used as one of the many payloads used by HijackLoader. This signifies that ACRStealer is not just a repurpose malware, but a continuously refined and rebranded module actively deployed through intricate loaders. This integration with HijackLoader highlights ACRStealer’s versality and modularity, which will likely attract more malicious actors to use it as a final payload.

For this part, we will highlight ACRStealer’s evasion techniques, C2 communication and notably its stealing capabilities, where our focus on the latter provides new insights.

## NTCalls and WoW64 SysCalls

Interestingly, this version of ACRStealer uses dynamic API resolution through NTDLL and WoW64 syscalls, as initially reported by Proofpoint. Most malware families typically rely on higher-level Win32 APIs to directly perform evasion or execution, which are easily detected and monitored by security products such as EDRs. By using low-level syscalls, this ACRStealer variant can bypass user-mode hooks and reduce its detectability.

The new variant ‘s behavior starts by accessing the Process Environment Block (PEB) to locate the ntdll.dll. It then manually parses the Export Address Table (EAT) to resolve the function names which are done via a modified version of djb2 also used in HijackLoader but with a different seed. After lookup, it saves the corresponding address and System Service Number (SSN) of the function and stores it to a global variable. Lastly, in order to execute the system call, it makes use of the Wow64 transition gate, bypassing the Win32 API layer and user-mode hooks.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_1_-_Dynamic_API_Resolution_.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_1_-_Dynamic_API_Resolution_.png)

Figure 1: Dynamic API Resolution

## AFD and NTSockets

Early versions of ACRStealer leveraged the use of Dead Drop Resolver (DDR) to obfuscate C2 communication. This version however uses NTSockets and Ancillary Function Driver (AFD) to establish a C2 connection without using the Winsock or any high-level APIs.

The code starts by manually constructing the string \\Device\\Afd\\Endpoint\\, which represents the AFD’s native path object. Then it builds an OBJECT_ATTRIBUTE structure along with a UNICODE_STRING structure. Together, these structures describe the target object to the Windows Object Manager. With this setup, the code invokes NtCreateFile allowing it to resolve and open the AFD Endpoint from user mode and instead of going through the Win32 API layer, again evading detection.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_2_Building_AFD_Endpoint_with_Object_Attribute_Struct.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_2_Building_AFD_Endpoint_with_Object_Attribute_Struct.png)

Figure 2: Building AFD Endpoint with Object_Attribute Struct

Next, the function constructs deliberately crafted strings. The first resulting string is AfdOpenPacketXX. Alongside this crafted string, it also defines protocol-related values (2, 1, 6) which corresponds to AF_INET, SOCKSTREAM and IPPROTO_TCP indicating that it is preparing a TCP IPv4 socket without importing ws2_32.socket. It then dynamically builds another string NTCreateFile, by concatenating string values. The function passes this string to the custom function resolver mentioned earlier and uses the Wow64 transition gate to invoke the native system call directly.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_3_Building_AFDOpenPacketXX_with_TCP_Ipv4_socket.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_3_Building_AFDOpenPacketXX_with_TCP_Ipv4_socket.png)

Figure 3: Building AFDOpenPacketXX with TCP Ipv4 socket

## Layered Communication

Another key aspect of this version is how it implemented a layered communication design: it first establishes a raw TCP connection, then performs SSL/TLS over that connection through SSPI.

After preparing the AFD endpoint handle, it manually parses the target IP address in this case is **157[.]180[.]40[.]106** and converts it to a network byte order together with **port 443**. It then configures the remote C2 endpoint via native AFD IOCTLS using NtDeviceIoControlFile which is an equivalent of connect() in WinSock. This suggests that it wants to blend in with the normal HTTPS traffic while using AFD. At this stage, it already established a plain TCP connection. During analysis, the IP address **157[.]180[.]40[.]106** was no longer responsive and might already be down thus it immediately terminates the endpoint.

However, if the IP address was still up, the sample would start to do a TLS Handshake over the established TCP connection. This TLS handshake happens with the use of SSPI through **AcquireCredentialsHandleA**which uses Microsoft Unified Security Protocol Provider and is followed by a call to **InitializeSecurityContextA** with a hardcoded **pszTargetName** in playtogga[.]com. This is looped in a statement where it checks a code **0x90312** which translates to the SSPI status code of **SEC_I_CONTINUE_NEEDED**. That indicates that additional handshake tokens must be exchanged before TLS session is fully established.

### Post-Handshake Transmission: Plaintext vs TLS

Once the handshake is completed, the code exits and frees the temporary buffers. It prepares the HTTP request before evaluating the transmission mode. One of eight HTTP methods (GET, HEAD, POST, PUT, DELETE, CONNECT, OPTIONS, TRACE, PATCH) is used in this function where the POST method is the default. The resulting header is exactly as follows **“POST / HTTP/1.1\r\nHost: playtogga[.]com\r\nConnection: close\r\nContent-Length: 48\r\nContent-Type: application/octet-stream\r\n\r\n”**.

After building the HTTP request header, it checks a configuration flag to determine whether the data will be sent in a plaintext or TLS wrapped data. If the flag is configured as 0, it will send the constructed HTTP request over the established TCP connection via AFD. It's like a single shot HTTP request commonly used for beaconing. Otherwise, it will start to encrypt the HTTP request header using the **EncryptMessage**API before sending. Based on the status code (200), it either decrypts the data from the server using AES-256 with a hardcoded 32-byte key or executes a Sleep command for two seconds before entering a recovery routine where it tries to initiate a re-connection.

## Loot, Sleep and Repeat

This section reveals ACRStealer’s range of data stealing functions. Apart from the unique methods used to steal sensitive browser information, the analysis also confirms that this variant deliberately targets gamers shown through exfiltration of Steam account data, something that has not been encountered and studied before.

The stealing features of ACRStealer are all based on eight short string config keys each associated with a type value (integer, array, bolean, string). These config keys are passed as an argument which will define what task the code will execute. The function that we labeled as **GetArrayField** (Figure 4) returns the array values stored under a given config key which will be used later on by task handling functions starting from **0x4126D0** to determine which files and directories to target.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_4_The_8_short_string_config_keys_and_the_series_of_stealing_functions.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_4_The_8_short_string_config_keys_and_the_series_of_stealing_functions.png)

Figure 4: The 8 short string config keys and the series of stealing functions

The very start of each stealing function is presented like this [Figure 5]. It checks if the config key value is indeed an array (type 4). It then iterates over each element of the array to confirm that each is an object (type 5) holding dictionary-like keys such as (p, tp, n, f, r). These dictionary keys are then used to retrieve the task’s parameters on what we assume to be name (n), target path (tp), argument (a), files (f) and recursive flag (r).

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_5_The_config_key_checker_and_task_parameter_assignment_observed_at_the_start_of_most_stealing_functions..png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_5_The_config_key_checker_and_task_parameter_assignment_observed_at_the_start_of_most_stealing_functions..png)

Figure 5: The config key checker and task parameter assignment observed at the start of most stealing functions.

Leveraging the use of NT syscalls, ACRStealer starts with the USERPROFILE and recursively searches for sensitive files using NtOpenFile and NtQueryDirectoryFile which loops until there are no more entries. Also, most of the stealing functions immediately submit the stolen data to its C2 server and are then followed by a call to NtDelayExecution before going to the next stealing function.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_6_File_traversal_through_the_used_of_NT_Syscalls.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_6_File_traversal_through_the_used_of_NT_Syscalls.png)

Figure 6: File traversal through the use of NT Syscalls

The stealing functions below are executed as follows.

It first extracts the browser master encryption key by locating Local State file to retrieve the values of encrypted_key and decrypting it via Base64, stripping the DPAPI prefix and calling the API **CryptUnprotectData** which returns the raw AES master key. After obtaining the master key, it proceeds to enumerate user directories and browser profiles. This is a classic DPAPI abused to decrypt browser artifacts. The stolen data is then extracted into a txt file with the hardcoded name “d5e48e78-2951-4117-b806-e4f8e626f28c.txt“ before sending it to the C2 server.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_7_DPAPI_abuse_to_acquire_browser_s_master_key.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_7_DPAPI_abuse_to_acquire_browser_s_master_key.png)

Figure 7: DPAPI abuse to acquire browser’s master key

The next stealing function performs a more advanced technique. It first enumerates browser profiles and extracts the raw AES master keys for each profile. But then it employs an App Bound Encryption bypass which is done via shellcode process injection into the target browser. This makes it clear that ACRStealer also targets Chrome versions lower than v127 before app bound encryption was introduced. The goal of the latter was to prevent stealers from using DPAPI to decrypt sensitive data. The shellcode also plays an important role here since it has no import table, it only dynamically resolves and calls CopyFileA from kernel32.dll. I also noticed a string “Elevator.exe “which strongly suggests that it copies Elevator.exe or elevation_service.exe which performs privilege operations for Chrome. Successful execution of this results in bypassing the App-Bound encryption and eventually decrypting sensitive browser information.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_8_Application_Bound_Encryption_Key_Bypass.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_8_Application_Bound_Encryption_Key_Bypass.png)

Figure 8: Application Bound Encryption Key Bypass

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_9_The_shellcode_used_to_copy_Elevator.exe_and_perform_privilege_operation_of_the_injected_process.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_9_The_shellcode_used_to_copy_Elevator.exe_and_perform_privilege_operation_of_the_injected_process.png)

Figure 9: The shellcode used to copy Elevator.exe and perform privilege operation of the injected process

The next sets of stealing functions are exfiltration of Login Data, Cookies and WebData. It also does full victim fingerprinting (Machine GUID, architecture, username, locale, build time etc.) where it again writes to the same hardcoded txt file before sending it to the C2 server.

The next stealing function exfiltrates Steam credential and tokens. It retrieves information via the install path registry where it extracts the account/login token data from the configuration files (loginuser.vdf, local.vdf). It again writes into the same hardcoded txt file before sending it to the C2 server.

The next function shows the stealer‘s capability to execute multiple secondary payloads based on the assigned field configuration. In this function, the additional payloads(exe, cmd, dll and ps1) are placed into four cases. This determines what type of execution the code will perform. There are three execution methods present: two Powershell commands via **CreateProcessA** and one **process hollowing** via rundll32.exe as a host process.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_10_Switch_case_function_for_secondary_payloads.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_10_Switch_case_function_for_secondary_payloads.png)

Figure 10: Switch case function for secondary payloads

Rather than invoking rundll32.exe through its legitimate DLL export interface (rundll32.exe <dll>, <export>), the malware employs process hollowing. It first spawns rundll32.exe in a suspended state using the **CREATE_SUSPENDED** flag, injects the malicious payload, overwrites its primary thread’s instruction pointer and resumes the thread to effectively bypass the process’s original entry point.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_11_Process_Hollowing_function.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_11_Process_Hollowing_function.png)

Figure 11: Process Hollowing function

The first PowerShell command function is responsible for executing only .ps1 and .exe files. The ps1 file is executed with the arguments **“-NoProfile -ExecutionPolicy Bypass -File**. For exe files, it simply prepares the executable’s path as the command line. In both cases, the ps1 and exe file are executed via **CreateProcessA**.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_12_The_first_PowerShell_command_.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_12_The_first_PowerShell_command_.png)

Figure 12: The first PowerShell command

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_13_The_second_PowerShell_command.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_13_The_second_PowerShell_command.png)

Figure 13: The second PowerShell command

The second PowerShell command, aside from the bypass execution method, also use DownloadString which is executed via Invoke-Expression(IEX). This function only executes a type ‘4‘ which maps to a .ps1 file.

This version of ACRStealer might still be incomplete. We do not see a function that executes a .cmd file and the process hollowing is mapped to type ‘5‘ which does not properly correspond to the declared type ‘3‘ or .dll files. This might also suggest a coding error or oversight as both cmd and dll files are declared but never executed.

[![](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_14_Supposedly_function_invoking_CMD_and_DLL_payloads.png)](https://blog.gdatasoftware.com/fileadmin/web/general/images/blog/2026/03/Figure_14_Supposedly_function_invoking_CMD_and_DLL_payloads.png)

Figure 14: Supposedly function invoking CMD and DLL payloads

The last function involves recursively traversing files while skipping executable file types (exe, dll, msi, sys) likely to avoid collecting system files. It captures screenshots by dynamically resolving libraries (user32.dll & gdi32.dll) and APIs such as **GetDC, CreateCompatibleBitmap, BitBlt**via **GetProcAddress**. The captured image is then stored as “g/screen/screen.bmp“. Each stolen data is inserted into an in-memory ZIP archive where it is enforced to only have a maximum size of 40MB (0x2800000). Once complete, it will be sent to the C2 server over TCP port 443.

## Patterns in Action

ACRStealer’s activity showed a very interesting operational pattern. VirusTotal telemetry indicates an active infection in countries such as USA, Mongolia and Germany. All identified samples are communicating with the same IP address **(157[.]180[.]40[.]106)** and five of the seven samples collected also establish connections to **playtogga[.]com**. Playtogga is a popular fantasy soccer platform currently headquartered at Austin, Texas. In contrast, PiviGames is the domain from which HijackLoader was downloaded, eventually dropping ACRStealer generally sees higher traffic in Spanish-speaking countries. This interaction suggests ACRStealer’s broad and diverse digital footprint possibly to mask and blend with legitimate traffic.

Within the first few days of this year 2026, the malicious URL _(hxxps://pivigames[.]blog/adbuho)_ is still active but there seems to be some changes. It still follows the same script and redirection chain, but it now leads to a new cloud storage and hosting service, in this case Mega. The downloaded zip file now only contains a single executable file with no resource file or folders unlike the previously downloaded zip file. Analysis showed that the executable file, which is also named “Setup.exe”, is a variant of **LummaStealer**.

This only indicates that the threat actors in control of the PiviGames infrastructure are still continuously infecting systems. Just like in this case, they might still actively approach unsuspecting users in popular gaming platforms like Steam, Discord, Twitch, and even social media like Reddit to compromise and steal data.

## IOCs

[1] FuII Verslon Setup 6419 σρєи Download.zip (sic!), archive with all files 418A1A6B08456C06F2F4CC9AD49EE7C63E642CCE1FA7984AD70FC214602B3B1

[2] ACRStealer, payload - 59202cb766c3034c308728c2e5770a0d074faa110ea981aa88f570eb402540d2 - Win32.Trojan-Stealer.ACRStealer.%M

[3] LummaStealer -f88c6e267363bf88be69e91899a35d6f054ca030e96b5d7f86915aa723fb268b - Win32.Trojan-Stealer.LummaStealer.%M

[4] 157[.]180[.]40[.]106 – ACRStealers’ C2 URL - Malware

[5] playtogga[.]com – ACRStealers’ C2 URL - Malware

## Previous Research on ACRStealer

[www.proofpoint.com/us/blog/threat-insight/amatera-stealer-rebranded-acr-stealer-improved-evasion-sophistication](https://www.proofpoint.com/us/blog/threat-insight/amatera-stealer-rebranded-acr-stealer-improved-evasion-sophistication)