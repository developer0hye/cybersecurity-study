# Lecture 2: Securing Systems

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/2/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/2/)

## TL;DR

- Plain **HTTP** can be read (**packet sniffing**) and changed (**MITM injection**) by anyone on the path. **HTTPS** (HTTP over TLS) fixes both.
- HTTPS trust comes from **certificates** signed by **Certificate Authorities**. **HSTS** stops downgrade attacks (**SSL stripping**).
- A **VPN** encrypts traffic to the VPN server and hides your IP from websites. It doesn't make you anonymous, and it doesn't protect you from malware.
- Every open **port** is attack surface. **Firewalls** limit who can reach which port.
- Malware comes in several forms: **virus**, **worm**, **botnet** (which powers DDoS). Update often, because **zero-days** are exploited before a patch exists.

## Core concepts

### Wi-Fi

- An **open** network sends frames unencrypted, so nearby devices can capture them.
- **WPA** (Wi-Fi Protected Access) encrypts traffic between your device and the access point. Use **WPA2** or, better, **WPA3**. WEP and the original WPA are broken.
- WPA protects only the **wireless hop**. Beyond the access point you still need HTTPS.

### HTTP and its threats

| Threat | What happens |
|---|---|
| **Packet sniffing** | Someone on the path reads your plaintext traffic: passwords, card numbers, session cookies |
| **MITM injection** | An on-path device changes responses: injects ads, malicious scripts, or fake downloads |
| **Session hijacking** | A stolen **session cookie** lets the attacker act as you without your password |

**Cookies** are small pieces of data a site stores in your browser. The browser sends them back on every request to that site, which is how you stay logged in and how the site keeps your shopping cart. Lecture 4 covers them in depth.

### HTTPS and TLS

HTTPS is HTTP carried inside **TLS** (formerly SSL). TLS provides:

- **Confidentiality**: traffic is encrypted.
- **Integrity**: tampering is detected.
- **Authentication**: you are talking to the real `example.com`.

**How the browser trusts a site**

1. The site presents an **X.509 certificate**. It contains the domain name and the site's **public key**, and it is **signed by a Certificate Authority (CA)**.
2. The browser/OS ships with a list of trusted **root CAs**.
3. The browser hashes the certificate contents and checks the CA's signature using the **CA's public key**. It also checks that the certificate matches the domain, hasn't expired, and hasn't been revoked.
4. If everything checks out, the browser runs a key exchange (Diffie-Hellman) with the server to get a shared **symmetric session key**, and the rest of the traffic uses fast symmetric encryption.

> ⚠️ The official notes say the browser verifies using "the public key of the website." The certificate signature is checked with the **issuing CA's public key**. The website's own public key is what the certificate vouches for, and the server proves it holds the matching private key during the handshake.

**What HTTPS does *not* hide:** the domain you visit, which leaks through DNS and TLS SNI, plus your IP address and traffic volume and timing.

### SSL stripping and HSTS

- **SSL stripping**: a MITM catches your first plain `http://` request and keeps you on HTTP, or sends you to a lookalike HTTPS site, so you never reach the real HTTPS site.
- **HSTS (HTTP Strict Transport Security)**: the server sends `Strict-Transport-Security: max-age=31536000; includeSubDomains`, and from then on the browser *refuses* plain HTTP for that domain.
- HSTS applies only after the first visit. The **HSTS preload list** built into browsers covers the very first visit too.

### VPN (Virtual Private Network)

- A VPN creates an **encrypted tunnel** from your device to a VPN server. Websites see the VPN server's IP instead of yours, which is why people use VPNs to appear to be in another country.
- It protects you from the local network (café Wi-Fi, your ISP).
- It moves trust from your ISP to the VPN provider, which can see your traffic metadata.
- Companies use VPNs to reach internal networks.

### SSH (Secure Shell)

- SSH is an encrypted protocol for running commands on a remote machine: `ssh user@host`.
- Prefer **key-based authentication** (`ssh-keygen`, `~/.ssh/authorized_keys`) over passwords. Disable password and root login on internet-facing servers.

### Ports, scanning, and firewalls

- A **port** number selects a service on a host. Common ones: **22** SSH, **80** HTTP, **443** HTTPS, 53 DNS, 25 SMTP.
- **Port scanning** (for example with `nmap`) finds which ports are open. Attackers use it for reconnaissance, and defenders use it to audit.
- **Penetration testing / ethical hacking** is *authorized* attacking to find weaknesses before real attackers do. Without permission, it's illegal.
- A **firewall** allows or blocks traffic by IP address, port, and protocol. Default-deny inbound traffic, and open only what you need.
- **Deep packet inspection (DPI)** looks inside packet payloads, not just headers. Organizations often run it on a **proxy** that all traffic passes through, to filter URLs, log activity, or catch data leaving the company (DLP). Inspecting HTTPS this way requires TLS interception with a company CA installed on your devices.

### Malware

| Type | Behavior |
|---|---|
| **Virus** | Attaches to a legitimate program or file and runs when the host runs, then spreads |
| **Worm** | Spreads **by itself** from machine to machine through vulnerabilities, with no user action |
| **Botnet** | A network of infected machines ("bots") that one attacker controls remotely |
| **Ransomware** | Encrypts your files and demands payment for the key |
| **Trojan** | Looks like legitimate software but carries a malicious payload |

**Denial-of-service (DoS)** attacks flood a server with requests until it slows down or goes offline. **DDoS** (distributed DoS) comes from thousands of botnet IPs, so blocking a single IP doesn't help. Mitigations are CDNs, rate limiting, and upstream scrubbing services.

### Antivirus, updates, and zero-days

- **Antivirus / EDR** detects known malware by signature and suspicious activity by behavior.
- **Automatic updates** are one of the most effective defenses, because most attacks use *known* vulnerabilities that already have patches.
- A **zero-day** is a vulnerability that attackers exploit before the vendor knows about it or ships a fix. The name means defenders have had "zero days" to patch it.

## Review questions

<details><summary>1. What three guarantees does TLS provide?</summary>

Confidentiality (encryption), integrity (tampering is detected), and server authentication (the certificate is signed by a trusted CA).
</details>

<details><summary>2. How does SSL stripping work, and what stops it?</summary>

A MITM keeps the victim on plain HTTP by catching the initial `http://` request. HSTS makes the browser insist on HTTPS, and the HSTS preload list covers the first visit.
</details>

<details><summary>3. Does a VPN make you anonymous?</summary>

No. It hides your IP from websites and your traffic from the local network, but the VPN provider can see your traffic metadata. Cookies and fingerprinting also still identify you (Lecture 4).
</details>

<details><summary>4. What is the key difference between a virus and a worm?</summary>

A virus needs a host program and usually a user action to spread. A worm spreads by itself across the network.
</details>

<details><summary>5. Why can't you stop a DDoS by blocking the attacker's IP?</summary>

The traffic comes from thousands of compromised machines (a botnet) with different IPs, and many of them look like legitimate users.
</details>
