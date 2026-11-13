---
title: "Incident report: what happened and what customers need to do"
source: "https://chainstack.com/security-incident-nov-2026/"
site_name: Chainstack
canonical_url: "https://chainstack.com/security-incident-nov-2026/"
language: en-US
domdown_version: 0.3.7
image: "https://chainstack.com/wp-content/uploads/2026/11/Chainstack-Incident-report.png"
author:
  - "Chainstack"
published: "2026-11-03T09:17:33+00:00"
description: "Incident report: what happened, what was exposed, and why we ask customers to change passwords and rotate node credentials"
---
# Incident report: what happened and what customers need to do

__Chainstack is committed to the security of our platform and the protection of our customers’ data. In keeping with that commitment to transparency, we are sharing the details of a recent security incident.__

### **What happened**

Our findings indicate that this incident was part of a [broader AI-powered attack campaign](https://thehackernews.com/2026/10/chinese-hackers-use-ai-powered-artex-to.html) reported in late October. That does not change our responsibility for what happened in our environment.

An external attacker gained unauthorized access to part of Chainstack’s infrastructure through a third-party component. We detected the intrusion, cut the access paths and are hardening our systems.

Customer-facing services continued to operate normally throughout the incident. Customer nodes, the console, and the API were not modified. We do not store payment method details, such as full card numbers or security codes, so they were not exposed.

### **What was exposed**

The attacker accessed a database containing customer account information. Information that may have been exposed includes organization names, account holder names, the email addresses of your organization’s members on Chainstack, and password hashes.

The attacker also had access to systems holding node credentials. We have no evidence they were read, but we are treating them as exposed and ask customers to rotate them.

- **October 26, 2026:** The attacker gained access to a development environment
- **October 29, 2026:** The attacker gained access to some parts of our production environment
- **October 31, 2026:** We detected the intrusion and cut the access paths the same day
- **November 2, 2026:** We finalized the investigation and closed the incident

### What we ask customers to do

We are notifying all customers by email and asking them to:

- **Change the passwords**, including on any other services where they reused the same password.
- **Rotate the node credentials.** Self-service rotation is now available in the console. Current endpoints keep working until customers complete the rotation, allowing them to rotate credentials without downtime. See the [documentation](https://docs.chainstack.com/docs/manage-your-node#rotate-node-credentials).

![Screenshot 2026 11 03 At 18.06.18 logo](https://chainstack.com/wp-content/uploads/2026/11/Screenshot-2026-11-03-at-18.06.18.png)

- **Regenerate the platform API keys** if they use the platform API.
- **Watch for phishing messages.** Chainstack will never ask for passwords, tokens or keys.

This page is the single source of truth for the incident. We will update it if new information becomes available.

If you have any further questions, [contact us](https://chainstack.com/cdn-cgi/l/email-protection#41323431312e333501222920282f323520222a6f222e2c).

SHARE THIS ARTICLE

[![Blog Twitter logo](https://chainstack.com/wp-content/themes/chainstack/img/blog-twitter.svg)](https://twitter.com/intent/tweet?text=Incident report: what happened and what customers need to do-&url=https%3A%2F%2Fchainstack.com%2Fsecurity-incident-nov-2026%2F&via=Chainstack)

[![Blog Linkedin logo](https://chainstack.com/wp-content/themes/chainstack/img/blog-linkedin.svg)](https://www.linkedin.com/sharing/share-offsite/?mini=true&url=https%3A%2F%2Fchainstack.com%2Fsecurity-incident-nov-2026%2F)

[![Blog Facebook logo](https://chainstack.com/wp-content/themes/chainstack/img/blog-facebook.svg)](https://www.facebook.com/sharer/sharer.php?u=https%3A%2F%2Fchainstack.com%2Fsecurity-incident-nov-2026%2F)