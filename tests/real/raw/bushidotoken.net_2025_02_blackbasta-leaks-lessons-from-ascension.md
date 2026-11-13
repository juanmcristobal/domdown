---
title: "BlackBasta Leaks: Lessons from the Ascension Health attack"
source: "https://blog.bushidotoken.net/2025/02/blackbasta-leaks-lessons-from-ascension.html"
canonical_url: "https://blog.bushidotoken.net/2025/02/blackbasta-leaks-lessons-from-ascension.html"
language: en-GB
domdown_version: 0.3.8
image: "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh-qoL0E4JtCsVj8ok2ypVL4NMiNd8empJ3AiU6daFD2D3V2yxMZVoGgrWlwLlb4eC2HwbS5HRB-6k0nMEht3aEVc-f_Cgt4ei5exGzbq3v_uf_L9VTnMf2x3RATanSrAAnlrRKJJWzuFTD-as1pcQi1QmRFgHCBXqxk9smz41AUl-0JUL_bIuWleszY5Vu/w1200-h630-p-k-no-nu/blackbasta.png"
author:
  - "February 27, 2025"
  - "ambulances"
  - "Black Basta"
  - "CTI"
  - "Cyber Threat Intelligence"
  - "Cybercrime"
  - "healthcare"
  - "HIPAA"
  - "hospitals"
  - "leak"
  - "medical"
  - "patients"
  - "ransomware"
  - "threat intel"
  - "April 02, 2025"
  - "Visit profile"
published: "2025-02-27T14:43:00-08:00"
description: "CTI, threat intelligence, OSINT, malware, APT, threat hunting, threat analysis, CTF, cybersecurity, security"
tags:
  - ambulances
  - Black Basta
  - CTI
  - Cyber Threat Intelligence
  - Cybercrime
  - healthcare
  - HIPAA
  - hospitals
  - leak
  - medical
  - patients
  - ransomware
  - threat intel
---
# @BushidoToken Threat Intel

### BlackBasta Leaks: Lessons from the Ascension Health attack

[![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh-qoL0E4JtCsVj8ok2ypVL4NMiNd8empJ3AiU6daFD2D3V2yxMZVoGgrWlwLlb4eC2HwbS5HRB-6k0nMEht3aEVc-f_Cgt4ei5exGzbq3v_uf_L9VTnMf2x3RATanSrAAnlrRKJJWzuFTD-as1pcQi1QmRFgHCBXqxk9smz41AUl-0JUL_bIuWleszY5Vu/w640-h270/blackbasta.png)](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEh-qoL0E4JtCsVj8ok2ypVL4NMiNd8empJ3AiU6daFD2D3V2yxMZVoGgrWlwLlb4eC2HwbS5HRB-6k0nMEht3aEVc-f_Cgt4ei5exGzbq3v_uf_L9VTnMf2x3RATanSrAAnlrRKJJWzuFTD-as1pcQi1QmRFgHCBXqxk9smz41AUl-0JUL_bIuWleszY5Vu/s613/blackbasta.png)

The BlackBasta ransomware group’s [leaked chat logs](https://www.bleepingcomputer.com/news/security/black-basta-ransomware-gang-s-internal-chat-logs-leak-online/) have proven to already be another unique and fascinating opportunity for researchers to better understand the internal operations of a Russia-based organised cybercrime enterprise. These leaks followed a major leak of Conti chat logs in 2022, which also proved to be a [treasure trove of intelligence](https://blog.bushidotoken.net/2022/04/lessons-from-conti-leaks.html) on the cybercrime enterprise. The BlackBasta gang consists of former Conti ransomware members and it should come as no surprise that their operations are similar in nature and structure.

Ransomware researchers have several valuable resources to conduct investigations with nowadays. This includes [ransomware.live](https://www.ransomware.live/), which contains several resources including [ransomch.at](https://ransomch.at/), a collection of negotiation chats between ransomware gangs and their victims, as well as the [ransomware

tool matrix](https://github.com/BushidoUK/Ransomware-Tool-Matrix) and [ransomware

vulnerability matrix](https://github.com/BushidoUK/Ransomware-Vulnerability-Matrix). These resources allow to deeply understand the capabilities and motivations of these ransomware gangs. However, leaked chat logs are the final missing piece of the puzzle and offer a deeper understanding from the cybercriminal’s very own perspective and organisational structure.

Active [since

April 2022](https://www.bleepingcomputer.com/news/security/new-black-basta-ransomware-springs-into-action-with-a-dozen-breaches/), BlackBasta is one of the top-tier ransomware gangs and one of the largest cybercrime enterprises in the world. According to the [US

Cybersecurity Infrastructure and Security Agency (CISA)](https://www.cisa.gov/news-events/cybersecurity-advisories/aa24-131a), BlackBasta impacted up to 500 different businesses and critical infrastructure in North America, Europe, and Australia as of May 2024.

## The importance of the Ascension Health incident

This blog shall dive deep into the Ascension Health attack by BlackBasta. It is a step-by-step extraction of the conversation between the BlackBasta members while they decide how to handle the attack.

The new insights around how BlackBasta and other ransomware gangs perceive being involved with incidents at healthcare sector victim should prove useful for incident responders, law enforcement, and governments that have to resolve these types of attacks on the healthcare sector on an alarmingly regularly basis.

## Background

On 9 May 2024, mainstream news organisations in the US reported about a cyberattack and significant disruption of services of Ascension Health, one of the largest healthcare providers in the country. On 11 May 2024, [BleepingComputer](https://www.bleepingcomputer.com/news/security/healthcare-giant-ascension-redirects-ambulances-after-suspected-Black-Basta-ransomware-attack/) reported that BlackBasta was to blame for the attack on Ascension Health and that ambulances had been disrupted and patients were being redirected to other hospitals.

## How the Incident Began

The BlackBasta attack on Ascension Health began many months before the ransomware was deployed on their network. Reconnaissance of Ascension Health by members of BlackBasta began around 3 November 2023. They shared 14 email addresses of Ascension Health employees, which we can only assume were used for phishing or password guessing. Ransomware gangs often used Zoominfo to profile their targets to determine whether it is worth it for them to attack and get a ransom from them.

A screenshot of a chat

AI-generated content may be incorrect.

The ransomware gang themselves wrote in their Matrix chat that [CBS

News](https://d.docs.live.net/62bce0f216f5575d/Documents/Blogs/%E2%80%A2%09https:/www.cbsnews.com/chicago/news/ascension-health-care-network-disrupted-cyberattack/) had written about a cyberattack on Ascension Health on 9 May 2024 and exclaimed that “it looks like one of the largest attacks of the year.”

A screenshot of a chat

AI-generated content may be incorrect.

Another BlackBasta member “gg” confirmed in the chat that it was them and appeared to be surprised that the news was writing about it.

Later, “gg” appeared to feel bad about the attack and concerned that cancer patients were suffering. However, at this stage it is hard to tell if they are serious or being sarcastic.

A close-up of a white rectangular object

AI-generated content may be incorrect.

One member of BlackBasta who used the moniker “tinker” then stated that he wanted to be the negotiator for the BlackBasta team and began to strategize how to extract a ransom payment.

A close-up of a white background

AI-generated content may be incorrect.

“gg” says they encrypted Ascension Health’s network using the Windows [Safe Mode Boot](https://attack.mitre.org/techniques/T1562/009/) technique, which is a function that [BlackBasta

is well-known](https://www.trendmicro.com/en_gb/research/22/e/examining-the-black-basta-ransomwares-infection-routine.html) to do.

A screenshot of a computer

AI-generated content may be incorrect.

The negotiator, “tinker” begins to weigh up their options. He states he believes the FBI and CISA will be involved, as well as Mandiant and begins to compare the incident to the [Change

Healthcare attack](https://www.wired.com/story/alphv-change-healthcare-ransomware-payment/) by ALPHV/BlackCat (and later RansomHub) who received a 22 million USD ransom payment.

A close-up of a sign

AI-generated content may be incorrect.

A screenshot of a message

AI-generated content may be incorrect.

“gg” shares that all the stolen data was put on a server named “ftp8” and tagged as “ALBIR_DS” and says to “tinker” that he should “look at the folder name, everything we downloaded from them is there."

The operator, “gg” also shared a summary of the target environment of Ascension Health. This includes number of servers being over 12,000, what security tools they use such as Cylance, Tanium, and McAfee. Plus, “gg” said they downloaded over 1.4TB of data to "ftp8" and used BlackBasta ransomware version 4.0 and attacked them on 8 May 2024.

A screenshot of a chat

AI-generated content may be incorrect.

## Negotiation Strategizing

After having established the details of the incident, Tinker (the negotiator) began to wonder about the likelihood of getting a ransom payment as well as estimate how much Ascension Health is likely losing per day.

A close-up of a message

AI-generated content may be incorrect.

Tinker (negotiator) then explains to the rest of the BlackBasta members involved in the attack what course of action they should take to get the ransom from Ascension Health. Tinker says they would normally set a 3% of the annual revenue and negotiate from there. They note that there are clear problems with the victim being a hospital and that this attack followed the Change Health attack by ALPHV/BlackCat. They also noted that they are worried as they believe the US National Security Agency (NSA) attacked TrickBot's servers four years ago and that the FBI took down Qakbot more recently. Tinker is also worried that one of Ascension Health’s patients will die and they will be blamed and labelled as a terrorist attack.

Tinker also noted that when BlackSuit attacked Octapharma that it was labelled by the news as "hostile actions by Russia" and they warned that Conti was already under sanctions and that because they are tied to Conti they may not get paid.

Tinker, ransomware negotiator for BlackBasta, ultimately recommended giving the decryptor for free to Ascension Health and resorting to data theft extortion. This is notable, as it is a similar situation to the Irish HSE ransomware attack by Conti, who also [provided the decryptor for free](https://www.bbc.co.uk/news/world-europe-57197688).

A close up of a text

AI-generated content may be incorrect.

## Healthcare Impact

The fact Ascension Health is a major medical organisation with many patients appeared to take its toll on the BlackBasta members. Tinker wrote in the BlackBasta chat they he found a post on Reddit by a doctor that works for Ascension Health who described the damage of the attack.

A screenshot of a chat

AI-generated content may be incorrect.

Another member of BlackBasta, “nn” also found out that Ascension Health is a group of hospitals. He immediately recommends giving them a decryptor for free.

A close-up of a white background

AI-generated content may be incorrect.

A screenshot of a chat

AI-generated content may be incorrect.

Interestingly, “gg” compares the attack on Change Health and also recognises Mandiant and warns that the FBI and CISA will be involved. Plus, “gg” noted that they did not encrypt via virtualization (such as vCenter, ESXi or Hyper-V) and reconfirmed they used Safe Mode Boot. Further, “gg” was also inclined to give Ascension the decryptor for free too.

A screenshot of a chat

AI-generated content may be incorrect.

Another BlackBasta member, “nickolas” comments about the situation. He warned and was particularly concerned about law enforcement retaliation, such as hacking back, sanctions, indictments. He recommended auditing the entire infrastructure and having a rebrand of the BlackBasta name, which means changing the ransomware, leak site, and other personas.

A screenshot of a chat

AI-generated content may be incorrect.

Tinker (negotiator) is aware however of the risk of someone dying and how it will impact their chances of getting the ransom.

A white background with black text

AI-generated content may be incorrect.

Tinker also discussed the politics of the scenario. He compared the situation to the colonial pipeline incident of 2021. He mentioned how Russia reacted and arrested ransomware operators. He also brought up the war in Ukraine and how ransomware attacks on the US impact the politics with Russia.

A screenshot of a message

AI-generated content may be incorrect.

Tinker highlighted that the ransomware was used to encrypt patient data and how it caused the hospital management system to crash. He was particularly concerned about the ambulances being unable to operate but also tries to minimize the severity of the incident. Nevertheless, he asked to see the stolen data himself to get a better understanding of what data BlackBasta operators have that they can leverage against Ascension Health.

A screenshot of a chat

AI-generated content may be incorrect.

By the end of deliberations, Tinker recommends giving a free decryptor and then demand a ransom for the stolen data.

A screenshot of a chat

AI-generated content may be incorrect.

tinker edited his message to then clarify that he reckons they should demand a ransom in the 10s of millions USD or over 100 million USD.

A white background with black text

AI-generated content may be incorrect.

## Ransomware Negotiations

The operator “gg” then shared the opening message to Ascension Health shared via the Black Basta negotiation portal:

A screenshot of a computer screen

AI-generated content may be incorrect.

The negotiator for Ascension Health (who BlackBasta believes is Mandiant) replied to the negotiation chat portal:

A screenshot of a computer

AI-generated content may be incorrect.

“gg” then clarified the terms of the ransom demand. A payment will be needed to delete and share the stolen data He maintains the offer to provide a free decryptor:

A screenshot of a computer

AI-generated content may be incorrect.

The negotiator for Ascension Health asked for the decryption tool:

A black and white rectangular object with white text

AI-generated content may be incorrect.

The decryptor was then provided to Ascension Health:

A screenshot of a computer program

AI-generated content may be incorrect.

Later, “gg” then shares a file tree for ""DS"" (which is equal to Ascension Health). The file is added to a ZIP and shared via a temp[.]sh link and is password protected:

A black and white screen with white text

AI-generated content may be incorrect.

The operator “gg” then uses Privat (a screenshot sharing site) to show the proof that they have deleted the data of Ascension Health:

From these messages, it appears no ransom was paid and BlackBasta returned the data and deleted it.

## Change of Heart

The most interesting part of this engagement with Ascension Health by BlackBasta was that the members deliberated back and forth about whether to provide a free decryption tool but all appeared to be fine with demanding a ransom for the victim data.

The operator “gg” appears to have a change of heart. He exclaims that they (the members of the BlackBasta ransomware gang) are "pentesters" and not "killers" and claims he “held a meeting in the office” which is interesting as it further proves they are a cybercrime enterprise, potentially with full-time employees.

A screenshot of a chat

AI-generated content may be incorrect.

The operator “gg” decided to help Ascension Health and requests not to work on hospitals anymore.

A screenshot of a phone

AI-generated content may be incorrect.

He also said “the software will fly to the trash” which likely means the group was thinking of ditching the brand of BlackBasta and rebrand to another name. Finally, “gg” warns other BlackBasta members not to target hospitals any more:

A screenshot of a chat

AI-generated content may be incorrect.

## The Impact of the BlackBasta Attack on Ascension Health

According to the [HIPAA Journal](https://www.hipaajournal.com/ascension-cyberattack-2024/), the personal data of up to 5.6 million patients was exposed and Ascension confirmed that some patient data was stolen during the attack. Ascension said that it found no evidence that the ransomware group gained access to electronic health records or other clinical systems, so full medical histories have not been stolen. During the attack, however, Ascension was forced to divert ambulances, close pharmacies, take critical IT systems offline and resort to pen and paper to record patient information. The attack affected a large percentage of its 136 hospitals across the US and took Ascension around 6 weeks to restore access to its electronic medical record system and resume normal operations. The ransomware attack reportedly caused delays in revenue cycle processes, claims submission, and payment processing, in addition to significant remediation costs.

## Lessons Learned

This chat log confirms that BlackBasta attacked Ascension Health using version 4.0 of their ransomware and used the Safe Mode Boot technique on 12,000 endpoints of the healthcare system.

If reconnaissance began on 3 November 2023 and the attack happened on the 8 May 2024, that would make the amount of time they took to gain access and deploy the ransomware was up to 187 days long or around six months. Due to this, cybercriminal campaign appears to be comparable to a more focused state-sponsored level intrusion where months of planning and numerous attempts are made to infiltrate a target.

The BlackBasta negotiator, Tinker, believed that they were going to get a very high ransom payment in the 10s of millions or up to 100 million USD and compared the attack to the Change Health incident by ALPHV/BlackCat who got 22 million USD.

The high ransom payment by Change Health has appeared to be like a dinner bell for ransomware gangs to go after other healthcare sector victims. Paying the ransom as a healthcare organisation clearly has significant downstream impact on the rest of the industry and it should be an absolute last resort and default to be to never pay the ransom.

There was an interesting change of heart and moment where the operator “gg” decided to give up on the Ascension Health attack, provide them a decryptor, provide the data back to them, and share proof that they deleted it. The members of BlackBasta were clearly concerned about hack-backs from law enforcement or intelligence services, as well as sanctions and deanonymization. The BlackBasta team also mentioned several times during this incident that they were going to have to rebrand because of the attack.

Overall, this incident goes to show that even Russia-based cybercrime enterprises with dozens of members remain paranoid about being attack by law enforcement and intelligence services. It is really interesting that they themselves admit that their actions warrant such a response.

One of the key lessons to learn from this engagement is that if a healthcare organisation is attacked by a ransomware gang, then it would be a valid strategy to tell the news about the incident. News about patients lives being at risk and dying will get the attention of these ruthless cybercriminals who will realise the mistakes they made and are potentially likely to at least provide a free decryptor and may give up entirely on their ransom payment pursuit and move on to the next target.

Lastly, these chat logs appear to prove that the West’s policies aimed at increasing pressure on Russia-based ransomware gangs is evidently working. These organised cybercrime enterprises are beginning to alter their targeting behaviour as a result to avoid the wrath of law enforcement retaliation.

### Popular posts from this blog

- **Read more:** <a href="https://blog.bushidotoken.net/2025/05/ransomware-tool-matrix-project-updates.html" title="Ransomware Tool Matrix Project Updates: May 2025">Read more</a>
- **Read more:** <a href="https://blog.bushidotoken.net/2023/05/raspberry-robin-global-usb-malware.html" title="Raspberry Robin: A global USB malware campaign providing access to ransomware operators">Read more</a>
- **Read more:** <a href="https://blog.bushidotoken.net/2025/04/tracking-adversaries-evilcorp-ransomhub.html" title="Tracking Adversaries: EvilCorp, the RansomHub affiliate">Read more</a>