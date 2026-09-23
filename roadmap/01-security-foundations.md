# Phase 1: Security Foundations

**Main source:** 🛡️ [roadmap.sh/cyber-security](https://roadmap.sh/cyber-security)

**Goal:** understand how systems, networks, and identities are attacked and defended. Every AI-era threat in Phases 3–4 builds on these ideas.

**AI-era angle:** When an LLM agent can browse, run code, and call APIs, it becomes one more *user* and one more *process* on your network. Networking, identity, least privilege, and logging are what keep it contained.

## Checklist

### Core concepts
- [x] CIA triad, risk, threat vs. vulnerability, defense in depth → [CS50 L0–L4](../cs50-cybersecurity/)
- [x] Authentication vs. authorization, MFA, SSO, passkeys → [CS50 L0](../cs50-cybersecurity/notes/00-securing-accounts.md)
- [ ] Zero trust principles
- [ ] Threat modeling basics (STRIDE, attack trees)
- [ ] Security frameworks: NIST CSF, CIS Controls, ISO 27001 (what they are, not memorizing them)

### Cryptography
- [x] Hashing, salting, symmetric vs. asymmetric, key exchange, signatures → [CS50 L1](../cs50-cybersecurity/notes/01-securing-data.md)
- [x] TLS and certificates, PKI basics → [CS50 L2](../cs50-cybersecurity/notes/02-securing-systems.md)
- [ ] Hands-on: inspect a real certificate chain with `openssl s_client`

### Networking

> Main resource for this section: [Professor Messer's Network+ N10-009](../comptia-network-plus/)

- [ ] OSI / TCP-IP models, IP addressing, subnetting, NAT
- [ ] Core protocols: DNS, DHCP, HTTP(S), SSH, ARP
- [x] Ports, firewalls, VPN, proxies, DPI → [CS50 L2](../cs50-cybersecurity/notes/02-securing-systems.md)
- [ ] Network segmentation, DMZ, VLANs
- [ ] Tools: `nmap`, `tcpdump`, Wireshark, `dig`, `curl`

### Operating systems
- [ ] Linux command line, permissions, processes, logs
- [ ] Windows basics: users/groups, event logs, PowerShell
- [ ] OS hardening, patching, least privilege
- [ ] Virtualization and sandboxing (important for running untrusted AI-generated code later)

### Attacks & web security
- [x] Phishing, social engineering, credential stuffing → [CS50 L0](../cs50-cybersecurity/notes/00-securing-accounts.md)
- [x] XSS, SQL injection, command injection, CSRF, buffer overflow → [CS50 L3](../cs50-cybersecurity/notes/03-securing-software.md)
- [ ] OWASP Top 10 (web) → [owasp.org](https://owasp.org/www-project-top-ten/)
- [ ] Malware types, MITM, DoS/DDoS, privilege escalation, lateral movement
- [ ] Attack models: Cyber Kill Chain, MITRE ATT&CK

### Defense & operations
- [ ] Logging, SIEM, EDR, IDS/IPS
- [ ] Vulnerability management: CVE / CVSS / EPSS / KEV → [CS50 L3](../cs50-cybersecurity/notes/03-securing-software.md#tracking-vulnerabilities)
- [ ] Incident response lifecycle (preparation → identification → containment → eradication → recovery → lessons learned)
- [ ] Cloud security basics: shared responsibility, IAM, storage misconfigurations
- [x] Privacy: tracking, cookies, fingerprinting, DNS, Tor → [CS50 L4](../cs50-cybersecurity/notes/04-preserving-privacy.md)

### Practice
- [ ] A beginner path on TryHackMe or Hack The Box
- [ ] picoCTF or another beginner CTF

## Notes & resources I used

- ✅ [CS50's Introduction to Cybersecurity](../cs50-cybersecurity/)
- 🟡 [Professor Messer's CompTIA Network+ N10-009](../comptia-network-plus/): networking fundamentals
