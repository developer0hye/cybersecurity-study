# CompTIA Network+ (N10-009): Professor Messer

Study notes for **Professor Messer's free CompTIA Network+ N10-009 training course** (87 videos, about 13 hours).

- 🎬 [YouTube playlist](https://www.youtube.com/watch?v=k7IOn3TiUc8&list=PLG49S3nxzAnl_tQe3kvnmeMid0mjF8Le8)
- 📚 [Course index on professormesser.com](https://www.professormesser.com/network-plus/n10-009/n10-009-video/n10-009-training-course/) (videos grouped by exam objective)
- 📄 [Official N10-009 exam objectives (CompTIA)](https://www.comptia.org/certifications/network): the checklist the course follows

## Why this course

[CS50 Cybersecurity](../cs50-cybersecurity/) explains *why* things are secure or not, but touches networking only lightly (ports, firewalls, VPN, TLS). The **Networking** part of [Phase 1 of my roadmap](../roadmap/01-security-foundations.md#networking) still has open items: OSI/TCP-IP, subnetting, NAT, DNS/DHCP/ARP, VLANs, segmentation, and tools. Network+ covers exactly these, in a vendor-neutral way.

**AI-era angle:** an AI agent that can browse, call APIs, or run code is one more host on the network. Egress filtering, segmentation, DNS, proxies, and network monitoring are how you contain it and see what it does.

## Structure

Messer's videos follow the exam objectives one-to-one, so the notes do too: **one file per exam domain**, with one section per objective (1.1, 1.2, ...). I don't keep one file per video.

| Domain | Weight | Objectives | Notes | Status |
|---|---|---|---|---|
| 0. The exam | – | 0.1 Introduction | – | ⬜ |
| 1. Networking Concepts | 23% | 1.1 OSI model · 1.2 Appliances & applications · 1.3 Cloud · 1.4 Ports & protocols · 1.5 Transmission media · 1.6 Topologies · 1.7 IPv4 addressing · 1.8 Network environments | `notes/1-networking-concepts.md` | ⬜ |
| 2. Network Implementation | 20% | 2.1 Routing · 2.2 Switching · 2.3 Wireless · 2.4 Physical installations | `notes/2-network-implementation.md` | ⬜ |
| 3. Network Operations | 19% | 3.1 Processes & procedures · 3.2 Monitoring · 3.3 Disaster recovery · 3.4 IP services · 3.5 Network access | `notes/3-network-operations.md` | ⬜ |
| 4. Network Security | 14% | 4.1 Security concepts · 4.2 Attack types · 4.3 Security features | `notes/4-network-security.md` | ⬜ |
| 5. Network Troubleshooting | 24% | 5.1 Methodology · 5.2 Physical issues · 5.3 Network services · 5.4 Performance · 5.5 Tools & protocols | `notes/5-network-troubleshooting.md` | ⬜ |

Planned extras, added as I go:

- `labs/`: small hands-on exercises on my own machine (`ip`, `dig`, `tcpdump`, Wireshark, `nmap` against localhost or my own lab VMs), plus a subnetting calculator in Python
- `notes/ports-cheatsheet.md`: the port/protocol table from 1.4, which is worth memorizing

Where a topic is already covered in CS50 (TLS, VPN, SSH, firewalls, Wi-Fi/WPA), I link to that note instead of repeating it, and add only what Network+ adds.

## Suggested study path

1. Watch the videos for one objective (usually 2–5 videos, 1.5× speed is fine).
2. Write that objective's section in my own words, checked against the exam objectives list.
3. Try it on the command line when there is something to try (`labs/`).
4. After each domain, write a few review questions without looking at the notes.

## Source & copyright

- The course is by **Professor Messer** (Messer Studios, LLC) and is free to watch, but it is **not** openly licensed. "Professor Messer" is a registered trademark of Messer Studios, LLC. CompTIA and Network+ are trademarks of CompTIA, Inc.
- So, unlike the CS50 folder, **nothing here is copied or adapted from the course**: no transcripts, slides, or course-note PDFs. The notes are my own summaries of the topics, organized by the public exam objectives, with links back to the videos.
- These notes are unofficial and not affiliated with or endorsed by Professor Messer or CompTIA.
