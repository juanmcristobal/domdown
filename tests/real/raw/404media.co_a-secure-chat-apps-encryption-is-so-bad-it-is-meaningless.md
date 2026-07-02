---
title: A Secure Chat App’s Encryption Is So Bad It Is ‘Meaningless’
source: "https://www.404media.co/a-secure-chat-apps-encryption-is-so-bad-it-is-meaningless/"
site_name: 404 Media
canonical_url: "https://www.404media.co/a-secure-chat-apps-encryption-is-so-bad-it-is-meaningless/"
language: en
domdown_version: 0.3.3
image: "https://storage.ghost.io/c/0f/76/0f76b548-bc58-4f25-abc3-3f5ebca07da4/content/images/size/w1200/2026/04/teleguard.png"
author:
  - "Joseph Cox"
  - "Janus Rose"
  - "Becky Ferreira"
  - "Jason Koebler"
published: "2026-04-02T13:47:24.000Z"
description: "TeleGuard is an app downloaded more a million times that markets itself as a secure way to chat. The app uploads users’ private keys to the company’s server, and makes decryption of messages trivial."
tags:
  - Privacy
---
TeleGuard, an app that markets itself as a secure, end-to-end encrypted messaging platform which has been downloaded more than a million times, implements its encryption so poorly that an attacker can trivially access a user’s private key and decrypt their messages, multiple security researchers told 404 Media. TeleGuard also uploads users’ private keys to a company server, meaning TeleGuard itself could decrypt its users’ messages, and the key can also at least partially be derived from simply intercepting a user’s traffic, the researchers found.

The news highlights something of the wild west of encrypted messaging apps, where not all are created equal.

💡

Do you know anything else about this app or other security issues? I would love to hear from you. Using a non-work device, you can message me securely on Signal at joseph.404 or send me an email at joseph@404media.co.

“No storage of data. Highly encrypted. Swiss made,” the [website for TeleGuard reads](https://teleguard.com/en?ref=404media.co). The site also says, “The chats as well as voice and video calls are end-to-end encrypted.”