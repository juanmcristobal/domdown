---
title: Vishing actors target Entra passkey enrollment
source: "https://www.okta.com/blog/threat-intelligence/vishing-actors-target-microsoft-entra-passkey-enrollment-/"
site_name: Okta
canonical_url: "https://www.okta.com/blog/threat-intelligence/vishing-actors-target-microsoft-entra-passkey-enrollment-/"
domdown_version: 0.3.4
published: 2026-07-05
description: Okta Threat Intelligence analysis of a phishing kit targeting Microsoft Entra passkey enrollment.
---
# Vishing actors target Entra passkey enrollment

## Executive Summary

Since April 2026, a threat actor tracked as O-UNC-066 has deployed a panel-controlled phishing kit targeting the passkey enrollment process for Microsoft 365 customers.

The threat actor calls targeted users and persuades them that they need to register a new passkey. Users are directed to a phishing kit that closely mimics the Microsoft passkey enrollment process.

## Infrastructure

Threat actors were observed creating subdomains for targeted entities under the following domains:

- `assignpasskey[.]com`
- `deploypasskey[.]com`
- `passkeydeploy[.]com`

Enroll users in strong authenticators such as Okta FastPass, passkeys or smart cards and enforce phishing resistance in policy.

| Tactic | Control |
| --- | --- |
| Phishing | Use phishing-resistant authentication |
| Valid Accounts | Restrict access by network and device context |