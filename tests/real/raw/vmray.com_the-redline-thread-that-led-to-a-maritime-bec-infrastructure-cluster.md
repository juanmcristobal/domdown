---
title: The RedLine Thread That Led to a Maritime BEC Infrastructure Cluster
source: "https://www.vmray.com/the-redline-thread-that-led-to-a-maritime-bec-infrastructure-cluster/"
site_name: VMRay
canonical_url: "https://www.vmray.com/the-redline-thread-that-led-to-a-maritime-bec-infrastructure-cluster/"
language: en
domdown_version: 0.3.5
image: "https://www.vmray.com/wp-content/uploads/2026/06/att_5_for_287998281.png"
published: "2026-06-30T10:26:49+00:00"
description: A pivot chain from a RedLine C2 to a maritime phishing campaign and attacker-owned infrastructure.
---
# The RedLine Thread That Led to a Maritime BEC Infrastructure Cluster

## Introduction

Most threat intelligence work begins with a feed. Platforms like VMRay UniqueSignal deliver a continuous stream of fresh and unique indicators, each timestamped and labeled with contextual information such as the malware family, runtime behavior and MITRE ATT&CK labels. In a typical workflow, an analyst takes one of these indicators, confirms it is still relevant and pushes it into a blocklist or SIEM rule.

Pivoting takes the same indicator further. Instead of stopping at the blocklist, you look at everything around it and the kind of context available depends on the indicator type. Since the starting point in this case is an IP address, the relevant pivots are things like the files that communicated with it, the certificates it served, the other domains hosted on it, its passive DNS history. Platforms like VirusTotal, FOFA, and Censys exist to map exactly these relationships. The goal is to turn one indicator into a cluster that is far more useful than a lone IP, both for detection coverage and for understanding what the attacker is actually doing.

### Background: RedLine Stealer

RedLine is a commodity infostealer first observed in early 2020 and sold under a Malware-as-a-Service model on underground forums and Telegram channels. It gave affiliates a point-and-click control panel that both generates payloads and acts as the C2 server. The malware harvests credentials, browser cookies, autofill data, and cryptocurrency wallets, which then get bundled into logs and sold on credential marketplaces.

However, RedLine still surfaces in new incidents through older builds and repackaged variants, which is exactly the kind of long-tail activity that fresh threat feeds continue to pick up. The indicator at the center of this investigation is one of those late sightings and as it turned out, the RedLine label was only the entry point into a much broader threat ecosystem.

## One Indicator, One Fingerprint

Every investigation needs a starting point. In this case it was a single RedLine indicator pulled from the VMRay UniqueSignal feed in our OpenCTI instance:

- 194[.]156.79.122:55615

UniqueSignal is VMRay’s threat intelligence feed that delivers fresh and unique IOCs in STIX format. Feeds like this are especially valuable for catching fresh C2 infrastructure early in a campaign lifecycle.

Then I turned to the VMRay Platform’s sandbox to pull a full analysis report on one of the communicating samples. My goal was to capture the C2’s HTTP response and build a fingerprint from it. The VMRay sandbox executed the sample in an isolated environment and captured its full runtime behavior, including the HTTP traffic.

That combination of the port 55615 and the Microsoft-HTTPAPI/2.0 server string is selective enough to be worth searching on. That combination is our first fingerprint.

## A Second RedLine C2 Surfaces

With a fingerprint in hand, the next step was to see how many other servers shared it. FOFA indexes internet-wide scan data, so it is well suited for this kind of lookup and querying it means we never touch the target infrastructure directly, which keeps the investigation quiet.

I translated the port and server-string combination into a FOFA query:

```
port="55615" && server="Microsoft-HTTPAPI/2.0"
```

The query returned two additional hosts beyond the original:

- 85[.]17.40.98:55615 (RedLine)
- 23[.]164.48.21:55615 (false positive)

That left one new confirmed RedLine C2: 85[.]17.40.98. Not a huge expansion on its own. But the value of this host turned out to have nothing to do with RedLine.

## A Maritime Phishing Campaign Behind the C2

The natural next step with a confirmed C2 is to look at what else VirusTotal knows about it. Pulling the relations for 85[.]17.40.98 returned a string of email files (.eml and .msg) submitted since January.

All of the email samples had been exclusively submitted from South Korea. These appear to be business exchanges written as part of ongoing conversations about shipment procedures, addressed to Kangrim Heavy Industries, a South Korean manufacturer of marine and industrial boilers that holds over 60% of the world market. The emails carried attached ZIP files which delivered Formbook, a long-running form-grabber and infostealer also sold as MaaS.

![Maritime phishing campaign example](https://www.vmray.com/wp-content/uploads/2026/06/att_5_for_287998281.png)

Image source: TheHackerNews

Several characteristics distinguished this from generic malspam: The senders impersonated real companies in the maritime supply chain, the pretexts mimicked routine shipping correspondence specific to that industry vertical and the targeting was narrow. This was a tailored spear-phishing campaign rather than a spray-and-pray operation.

### What is Business Email Compromise?

Business Email Compromise (BEC) is a category of fraud that relies on social engineering. The attacker impersonates someone the target trusts and uses that trust to insert themselves into a routine business transaction to redirect a payment. There is often no malware involved at all. The leverage comes from a convincing email arriving at the right moment in an expected conversation.

That is the reasoning behind chasing the distribution infrastructure rather than the payload. The domains and mail servers used to send these emails have a longer shelf life and blocking them at the email gateway prevents the next wave from ever landing.

## Identifying the Attacker-Owned Infrastructure

The campaign gave us five sender addresses to work with. The first task is to figure out which ones actually belonged to the attacker versus which were legitimate accounts that had been compromised or spoofed.

- infos@krysegroupllc[.]online
- P.POLITIS@BSCL[.]GLOBAL
- ALFRED.KOH@BOURBON-ONLINE[.]COM
- 8139@shengan-light[.]com.tw
- SYLVIA.XIAO@MACGREGOR[.]COM

Three of these domains have been active since a long time ago and seem to belong to real companies. These are likely legitimate accounts being spoofed or compromised to send phishing from a trusted source. Either way, the domain itself is not attacker infrastructure and pivoting on it would only lead back to a legitimate company.

The remaining two stand out for the opposite reason. krysegroupllc[.]online was registered in mid-2025 and impersonated a real company. On the other hand, bscl[.]global was harder to classify from registration data alone, but its passive DNS records were recent enough to be suspicious.

## A Pivot Turns Into A Cluster

The first pivot point was the domain itself. Running krysegroupllc[.]online through FOFA pointed at Cloudflare and showed a default landing page, which is not useful on its own since Cloudflare sits in front of countless unrelated sites.

Scrolling further, though, a more interesting record appeared: one host served the domain from a provider called TheHost LLC with a fairly specific HTTP server banner:

> Apache/2.4.62 (Unix) OpenSSL/1.0.2k-fips

Neither attribute is remarkable in isolation. But the combination of that specific hosting provider and the Apache/OpenSSL build string is selective enough to be worth pivoting on. I built a query around both:

```
org="TheHost LLC" && server="Apache/2.4.62 (Unix) OpenSSL/1.0.2k-fips"
```

This narrowed the results down to a manageable set. From there, I went through the resulting hosts and examined their TLS certificates looking for the same kind of domain-naming pattern we had already seen.

- 185[.]252.24.78 acasiallc[.]shop
- 185[.]252.24.52 ansysllc[.]shop
- 185[.]252.24.74 softinsallc[.]online
- 176[.]114.8.101 amdocsllc[.]shop
- 91[.]108.82.73 taicom[.]top
- 91[.]108.82.101 cimentosservices[.]online
- 176[.]114.8.90 epsilongroup[.]online

The naming pattern is consistent with the original lead: short strings, several ending in llc, impersonating real businesses.