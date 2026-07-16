---
title: "New AirSnitch attack bypasses Wi-Fi encryption in homes, offices, and enterprises"
source: "https://arstechnica.com/security/2026/02/new-airsnitch-attack-breaks-wi-fi-encryption-in-homes-offices-and-enterprises/"
site_name: Ars Technica
canonical_url: "https://arstechnica.com/security/2026/02/new-airsnitch-attack-breaks-wi-fi-encryption-in-homes-offices-and-enterprises/"
language: en
domdown_version: 0.3.6
image: "https://cdn.arstechnica.net/wp-content/uploads/2025/06/wi-fi-1152x648-1751309982.jpg"
published: "2026-02-26T15:45:18+00:00"
description: That guest network you set up for your neighbors may not be as secure as you think.
---
# New AirSnitch attack bypasses Wi-Fi encryption in homes, offices, and enterprises

That guest network you set up for your neighbors may not be as secure as you think.

[Dan Goodin](https://arstechnica.com/author/dan-goodin/)

–

Feb 26, 2026 10:45 am

|

[167](https://arstechnica.com/security/2026/02/new-airsnitch-attack-breaks-wi-fi-encryption-in-homes-offices-and-enterprises/#comments)

https://cdn.arstechnica.net/wp-content/uploads/2025/06/wi-fi.jpg

Credit: Getty Image | BlackJack3D

Credit: Getty Image | BlackJack3D

It’s hard to overstate the role that Wi-Fi plays in virtually every facet of life. The organization that shepherds the wireless protocol [says](https://www.wi-fi.org/beacon/the-beacon/powering-connected-world-wi-fi-momentum-2025) that more than 48 billion Wi-Fi-enabled devices have shipped since it debuted in the late 1990s. One [estimate](https://thenetworkinstallers.com/blog/wifi-statistics/) pegs the number of individual users at 6 billion, roughly 70 percent of the world’s population.

Despite the dependence and the immeasurable amount of sensitive data flowing through Wi-Fi transmissions, the history of the protocol has been [littered](https://arstechnica.com/gadgets/2019/03/802-eleventy-who-goes-there-wpa3-wi-fi-security-and-what-came-before-it/) with security landmines stemming both from the inherited confidentiality weaknesses of its networking predecessor, Ethernet (it was once possible for anyone on a network to [read and modify](https://blackhat.com/html/bh-usa-03/bh-usa-03-speakers.html) the traffic sent to anyone else), and the ability for anyone nearby to receive the radio signals Wi-Fi relies on.

## Ghost in the machine

In the early days, public Wi-Fi networks often resembled the Wild West, where [ARP spoofing](https://en.wikipedia.org/wiki/ARP_spoofing) attacks that allowed renegade users to read other users’ traffic were common. The solution was to build cryptographic protections that prevented nearby parties—whether an authorized user on the network or someone near the AP (access point)—from reading or tampering with the traffic of any other user.

New research shows that behaviors that occur at the very lowest levels of the network stack make encryption—in any form, not just those that have been broken in the past—incapable of providing client isolation, an encryption-enabled protection promised by all router makers, that is intended to block direct communication between two or more connected clients.

The isolation can effectively be nullified through AirSnitch, the name the researchers gave to a series of attacks that capitalize on the newly discovered weaknesses. Various forms of AirSnitch work across a broad range of routers, including those from Netgear, D-Link, Ubiquiti, Cisco, and those running DD-WRT and OpenWrt.

AirSnitch “breaks worldwide Wi-Fi encryption, and it might have the potential to enable advanced cyberattacks,” Xin’an Zhou, the lead author of the research paper, said in an interview. “Advanced attacks can build on our primitives to [perform] cookie stealing, DNS and cache poisoning. Our research physically wiretaps the wire altogether so these sophisticated attacks will work. It’s really a threat to worldwide network security.” Zhou presented his research on Wednesday at the 2026 [Network and Distributed System Security Symposium](https://www.ndss-symposium.org/ndss2026/).

Paper co-author Mathy Vanhoef, [said](https://infosec.exchange/deck/@vanhoefm/116138411163131123) a few hours after this post went live that the attack may be better described as a Wi-Fi encryption “bypass,” “in the sense that we can bypass client isolation. We don’t break Wi-Fi authentication or encryption. Crypto is often bypassed instead of broken. And we bypass it ;)” People who don’t rely on client or network isolation, he added, are safe.

Previous Wi-Fi attacks that overnight broke existing protections such as [WEP](https://dev.to/rijultp/wep-encryption-explained-how-it-worked-and-why-it-failed-23pf) and [WPA](https://dl.aircrack-ng.org/breakingwepandwpa.pdf) worked by exploiting vulnerabilities in the underlying encryption they used. AirSnitch, by contrast, targets a previously overlooked attack surface—the lowest levels of the networking stack, a hierarchy of architecture and protocols based on their functions and behaviors.

The lowest level, Layer-1, encompasses physical devices such as cabling, connected nodes, and all the things that allow them to communicate. The highest level, Layer-7, is where applications such as browsers, email clients, and other Internet software run. Levels 2 through 6 are known as the Data Link, Network, Transport, Session, and Presentation layers, respectively.

## Identity crisis

Unlike previous Wi-Fi attacks, AirSnitch exploits core features in Layers 1 and 2 and the failure to bind and synchronize a client across these and higher layers, other nodes, and other network names such as SSIDs (Service Set Identifiers). This cross-layer identity desynchronization is the key driver of AirSnitch attacks.

The most powerful such attack is a full, bidirectional [machine-in-the-middle (MitM) attack](https://en.wikipedia.org/wiki/Man-in-the-middle_attack), meaning the attacker can view and modify data before it makes its way to the intended recipient. The attacker can be on the same SSID, a separate one, or even a separate network segment tied to the same AP. It works against small Wi-Fi networks in both homes and offices and large networks in enterprises.

With the ability to intercept all link-layer traffic (that is, the traffic as it passes between Layers 1 and 2), an attacker can perform other attacks on higher layers. The most dire consequence occurs when an Internet connection isn’t encrypted—something that Google [recently estimated](https://transparencyreport.google.com/https/overview) occurred when as much as 6 percent and 20 percent of pages loaded on Windows and Linux, respectively. In these cases, the attacker can view and modify all traffic in the clear and steal authentication cookies, passwords, payment card details, and any other sensitive data. Since many company intranets are sent in plaintext, traffic from them can also be intercepted.

Even when HTTPS is in place, an attacker can still intercept domain look-up traffic and use DNS cache poisoning to corrupt tables stored by the target’s operating system. The AirSnitch MitM also puts the attacker in the position to wage attacks against vulnerabilities that may not be patched. Attackers can also see the external IP addresses hosting webpages being visited and often correlate them with the precise URL.

Given the range of possibilities it affords, AirSnitch gives attackers capabilities that haven’t been possible with other Wi-Fi attacks, including KRACK from [2017](https://arstechnica.com/information-technology/2017/10/severe-flaw-in-wpa2-protocol-leaves-wi-fi-traffic-open-to-eavesdropping/) and [2019](https://arstechnica.com/information-technology/2019/04/serious-flaws-leave-wpa3-vulnerable-to-hacks-that-steal-wi-fi-passwords/) and more recent Wi-Fi attacks that, like AirSnitch, inject data (known as frames) into remote [GRE tunnels](https://i.blackhat.com/BH-USA-25/Presentations/USA-25-Tung-From-Spoofing-To-Tunneling-New-wp.pdf) and [bypass network access control lists](https://www.usenix.org/legacy/event/woot11/tech/final_files/Goodspeed.pdf).

“This work is impressive because unlike other frame injection methods, the attacker controls a bidirectional flow,” said HD Moore, a security expert and the founder and CEO of [runZero](https://www.runzero.com/authors/hd-moore/).

He continued:

> This research shows that a wireless-connected attacker can subvert client isolation and implement full relay attacks against other clients, similar to old-school ARP spoofing. In a lot of ways, this restores the attack surface that was present before client isolation became common. For folks who lived through the chaos of early wireless guest networking rollouts (planes, hotels, coffee shops) this stuff should be familiar, but client isolation has become so common, these kinds of attacks may have fallen off people’s radar.

## Stuck in the middle with you

The MitM targets Layers 1 and 2 and the interaction between them. It starts with [port stealing](https://www.geeksforgeeks.org/ethical-hacking/what-is-port-stealing/), one of the earliest attack classes of Ethernet that’s adapted to work against Wi-Fi. An attacker carries it out by modifying the Layer-1 mapping that associates a network port with a victim’s [MAC](https://en.wikipedia.org/wiki/MAC_address)—a unique address that identifies each connected device. By connecting to the [BSSID](https://www.differencebetween.net/technology/difference-between-bssid-and-ssid/) that bridges the AP to a radio frequency the target isn’t using (usually a 2.4GHz or 5GHz) and completing a Wi-Fi [four-way handshake](https://networklessons.com/wireless/wpa-and-wpa2-4-way-handshake), the attacker replaces the target’s MAC with one of their own.

[![](https://cdn.arstechnica.net/wp-content/uploads/2026/02/airsnitch-mitm-downlink.png)](https://cdn.arstechnica.net/wp-content/uploads/2026/02/airsnitch-mitm-downlink.png)

The attacker spoofs the victim’s MAC address on a different NIC,

causing the internal switch to mistakenly associate the victim’s address with the attacker’s port/BSSID. As a result, frames intended for the victim are

forwarded to the attacker and encrypted using the attacker’s PTK.

Credit: Zhou et al.

The attacker spoofs the victim’s MAC address on a different NIC,

causing the internal switch to mistakenly associate the victim’s address with the attacker’s port/BSSID. As a result, frames intended for the victim are

forwarded to the attacker and encrypted using the attacker’s PTK.

Credit: Zhou et al.

In other words, the attacker connects to the Wi-Fi network using the target’s MAC and then receives the target’s traffic. With this, an attacker obtains all downlink traffic (data sent from the router) intended for the target. Once the switch at Layer-2 sees the response, it updates its MAC address table to preserve the new mapping for as long as the attacker needs.

This completes the first half of the MitM, allowing all data to flow to the attacker. That alone would result in little more than a denial of service for the target. To prevent the target from noticing—and more importantly, to gain the bidirectional MitM capability needed to perform more advanced attacks—the attacker needs a way to restore the original mapping (the one assigning the victim’s MAC to the Layer-1 port). An attacker performs this restoration by sending an [ICMP ping](https://en.wikipedia.org/wiki/Internet_Control_Message_Protocol) from a random MAC. The ping, which must be wrapped in a Group Temporal key shared among all clients, triggers replies that cause the Layer-1 mapping (i.e., port states) to revert back to the original one.

“In a normal Layer-2 switch, the switch learns the MAC of the client by seeing it respond with its source address,” Moore explained. “This attack confuses the AP into thinking that the client reconnected elsewhere, allowing an attacker to redirect Layer-2 traffic. Unlike Ethernet switches, wireless APs can’t tie a physical port on the device to a single client; clients are mobile by design.”

The back-and-forth flipping of the MAC from the attacker to the target, and vice versa, can continue for as long as the attacker wants. With that, the bidirectional MitM has been achieved. Attackers can then perform a host of other attacks, both related to AirSnitch or ones such as the cache poisoning discussed earlier. Depending on the router the target is using, the attack can be performed even when the attacker and target are connected to separate SSIDs connected by the same AP. In some cases, Zhou said, the attacker can even be connected from the Internet.

“Even when the guest SSID has a different name and password, it may still share parts of the same internal network infrastructure as your main Wi-Fi,” the researcher explained. “In some setups, that shared infrastructure can allow unexpected connectivity between guest devices and trusted devices.”

## No, enterprise defenses won’t protect you

Variations of the attack defeat the client isolation promised by makers of enterprise routers, which typically use credentials and a master encryption key that are unique to each client. One such attack works across multiple APs when they share a wired distribution system, as is common in enterprise and campus networks.

In their paper, [AirSnitch: Demystifying and Breaking Client Isolation in Wi-Fi Networks](https://www.ndss-symposium.org/ndss-paper/airsnitch-demystifying-and-breaking-client-isolation-in-wi-fi-networks/), the researchers wrote:

> Although port stealing was originally devised for hosts on the same switch, we show that attackers can hijack MAC-to-port mappings at a higher layer, i.e., at the level of the distribution switch—to intercept traffic to victims associated with different APs. This escalates the attack beyond its traditional limits, breaking the assumption that separate APs provide effective isolation.
>
> This discovery exposes a blind spot in client isolation: even physically separated APs, broadcasting different SSIDs, offer ineffective isolation if connected to a common distribution system. By redirecting traffic at the distribution switch, attackers can intercept and manipulate victim traffic across AP boundaries, expanding the threat model for modern Wi-Fi networks.

The researchers demonstrated that their attacks can enable the breakage of [RADIUS](https://en.wikipedia.org/wiki/RADIUS), a centralized authentication protocol for [enhanced security](https://www.fortinet.com/resources/cyberglossary/radius-protocol) in enterprise networks. “By spoofing a gateway MAC and connecting to an AP,” the researchers wrote, “an attacker can steal uplink RADIUS packets.” The attacker can go on to crack a message authenticator that’s used for integrity protection and, from there, learn a shared passphrase. “This allows the attacker to set up a rogue RADIUS server and associated rogue WPA2/3 access point, which allows any legitimate client to connect, thereby intercepting their traffic and credentials.”

The researchers tested the following 11 devices:

- Netgear Nighthawk x6 R8000
- Tenda RX2 Pro
- D-LINK DIR-3040
- TP-LINK Archer AXE75
- ASUS RT-AX57
- DD-WRT v3.0-r44715
- OpenWrt 24.10
- Ubiquiti AmpliFi Alien Router
- Ubiquiti AmpliFi Router HD
- LANCOM LX-6500
- Cisco Catalyst 9130

As noted earlier, every tested router was vulnerable to at least one attack. Zhou said that some router makers have already released updates that mitigate some of the attacks, and more updates are expected in the future. But he also said some manufacturers have told him that some of the systemic weaknesses can only be addressed through changes in the underlying chips they buy from silicon makers.

The hardware manufacturers face yet another challenge: The client isolation mechanisms vary from maker to maker. With no industry-wide standard, these one-off solutions are splintered and may not receive the concerted security attention that formal protocols are given.

## So how bad is AirSnitch, really?

With a basic understanding of AirSnitch, the next step is to put it into historical context and assess how big a threat it poses in the real world. In some respects, it resembles the 2007 [PTW attack](https://eprint.iacr.org/2007/120.pdf) (named for its creators Andrei Pyshkin, Erik Tews, and Ralf-Philipp Weinmann) that completely and immediately broke WEP, leaving Wi-Fi users everywhere with no means to protect themselves against nearby adversaries. For now, client isolation is similarly defeated—almost completely and overnight—with no immediate remedy available.

At the same time, the bar for waging WEP attacks was significantly lower, since it was available to anyone within range of an AP. AirSnitch, by contrast, requires that the attacker already have some sort of access to the Wi-Fi network. For many people, that may mean steering clear of public Wi-Fi networks altogether.

If the network is properly secured—meaning it’s protected by a strong password that’s known only to authorized users—AirSnitch may not be of much value to an attacker. The nuance here is that even if an attacker doesn’t have access to a specific SSID, they may still use AirSnitch if they have access to other SSIDs or BSSIDs that use the same AP or other connecting infrastructure.

Yet another difference to the PTW attack—and others that have followed breaking WPA, WPA2, and WPA3 protections—is that they were limited to hacks using terrestrial radio signals, a much more limited theater than the one AirSnitch uses. Ultimately, the AirSnitch attacks are broader but less severe.

Also unlike those previous attacks, firewall mitigations may be more problematic.

“We expand the threat model showing an attacker can be on another channel or port, or can be from the Internet,” Zhou said. “Firewalls are also networking devices. We often say a firewall is a Layer-3 device because it works at the IP layer. But fundamentally, it’s connected by wire to different network elements. That wire is not secure.”

Some of the threat can be mitigated by using VPNs, but this remedy has all the usual drawbacks that come with them. For one, VPNs are notorious for leaking metadata, DNS queries, and other traffic that can be useful to attackers, making the protection limited. And for another, finding a reputable and trustworthy VPN provider has historically proven to be [vexingly difficult](https://arstechnica.com/information-technology/2016/06/aiming-for-anonymity-ars-assesses-the-state-of-vpns-in-2016/), though things have [improved](https://www.nytimes.com/wirecutter/reviews/best-vpn-service/) more recently. Ultimately, a VPN shouldn’t be regarded as much more than a bandage.

Another potential mitigation is using wireless [VLANs](https://en.wikipedia.org/wiki/VLAN) to isolate one SSID from another. Zhou said such options aren’t universally available and are also “super easy to be configured wrong.” Specifically, he said VLANs can often be implemented in ways that allow “hopping vulnerabilities.” Further, Moore [has argued](https://arstechnica.com/civis/posts/44274656/) why “VLANs are not a practical barrier” against all AirSnitch attacks

The most effective remedy may be to adopt a security stance known as [zero trust](https://www.wired.com/story/what-is-zero-trust/), which treats each node inside a network as a potential adversary until it provides proof it can be trusted. This model is challenging for even well-funded enterprise organizations to adopt, although it’s becoming easier. It’s not clear if it will ever be feasible for more casual Wi-Fi users in homes and smaller businesses.

Probably the most reasonable response is to exercise measured caution for all Wi-Fi networks managed by people you don’t know. When feasible, use a trustworthy VPN on public APs or, better yet, tether a connection from a cell phone.

Wi-Fi has always been a risky proposition, and AirSnitch only expands the potential for malice. Then again, the new capabilities may mean little in the real world, where [evil twin](https://en.wikipedia.org/wiki/Evil_twin_(wireless_networks)) attacks accomplish many of the same objectives with much less hassle.

Moore said the attacks possible before client isolation were often as simple as running [ettercap](https://www.ettercap-project.org/) or similar tools as soon as a normal Wi-Fi connection was completed. AirSnitch attacks require considerably more work, at least until someone writes an easy-to-use script that automates it.

“It will be interesting to see if the wireless vendors care enough to resolve these issues completely and if attackers care enough to put all of this together when there might be easier things to do (like run a fake AP instead),” Moore said. “At the least it should make pentesters’ lives more interesting since it re-opens a lot of exposure that many folks may not have any experience with.”

_Headline updated to change “breaks” with “bypasses.”_