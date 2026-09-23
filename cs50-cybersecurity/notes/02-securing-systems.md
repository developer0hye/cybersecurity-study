# Lecture 2: Securing Systems

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/2/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/2/)

## TL;DR

- Encryption from Lecture 1 is the building block for securing networked systems.
- **Wi-Fi encryption (WPA)** protects only the hop between your device and the access point.
- Plain **HTTP** can be read (**packet sniffing**) and changed (**machine-in-the-middle injection**) by anyone on the path, and stolen **session cookies** allow **session hijacking**. **HTTPS** (HTTP over **TLS**) fixes all three.
- HTTPS trust comes from **X.509 certificates** signed by **Certificate Authorities** that your browser trusts. **SSL stripping** attacks the first unencrypted request. **HSTS** (plus **preload**) closes that window.
- A **VPN** encrypts *all* your traffic to one VPN server and gives you that server's IP. **SSH** encrypts remote command sessions.
- **Port numbers** tell a server which service a packet is for. **Port scanning** finds open services, so hiding a service on an odd port is only **security through obscurity**. **Pen testers / ethical hackers** attack with permission.
- **Firewalls** filter by IP, port, or packet contents (**deep packet inspection**). **Proxies** do this by design, and an employer-installed **CA certificate** can let a proxy read your HTTPS traffic.
- **Malware**: a **virus** needs you to run it, a **worm** spreads by itself, and a **botnet** of infected machines powers **DDoS** attacks.
- Defenses are **antivirus** plus **automatic updates**. **Zero-day** attacks still get through, so use **defense in depth**.

## Wi-Fi

- Networks are either **unsecured** or **secured**. The padlock icon next to a network name means the wireless link is encrypted.
- On a secured network, your packets are encrypted between your device and the **access point**, the box with antennas on the wall or ceiling that you talk to wirelessly.
- The standard is **Wi-Fi Protected Access (WPA)**, which has gone through several versions. Use the latest your devices support. 📌 Today that means **WPA3**, or WPA2 at minimum. WEP and the original WPA are broken.
- The access point connects to **routers**, which forward packets from router to router until they reach the destination. **WPA encrypts only the wireless hop.** Beyond the access point, your traffic is only as protected as the protocol you use (HTTP vs. HTTPS).

## HTTP and its threats

**HTTP (Hypertext Transfer Protocol)** is the set of conventions browsers and web servers use to talk to each other. It is **not encrypted**: requests and responses are English-like text anyone on the path can read.

The lecture's cast of characters: **Alice** is the user, **Bob** is the web server, and **Eve** is an eavesdropper or machine in the middle.

### Threat 1: machine-in-the-middle (MITM) injection

When you visit a site, the server sends back **HTML (Hypertext Markup Language)**. Over HTTP that HTML travels unscrambled, so any device in the middle can **change it on the way**, for example by adding a `<script>` tag:

- **Ad injection**: ISPs, coffee shops, and hotels have inserted ads into pages that were never designed to have them, often at the very top of the page.
- **Malicious code**: a script that steals your data.

> **Q:** How do you detect a machine in the middle and get rid of it?
> **A:** You often *can't* detect it, because it can work without your knowledge. The cure is encryption, the subject of the rest of this lecture.

### Threat 2: packet sniffing

A **packet** is a virtual envelope carrying data from point A to point B. Large messages are split across many packets. **Packet sniffing** means looking inside these envelopes. Without encryption, any machine in the middle can read, and even change, their contents before passing them on.

A search request inside an unencrypted envelope:

```http
GET /search?q=cats HTTP/3
Host: www.example.com
```

`GET` means "get me a page", `/search` is the search endpoint, and `q=cats` reveals your **query**. That might not matter for cats, but consider a checkout:

```http
POST /checkout HTTP/3
Host: www.example.com

number=4111111111111111&...
```

`POST` means "send (upload) information". Anyone sniffing this packet gets your **credit card number**, and possibly your name, address, and security code.

> 📌 The slides label these plaintext examples `HTTP/3`. Real HTTP/3 runs over QUIC, which always uses TLS encryption, so it can't be sniffed like this. The point holds for plain HTTP/1.1, which is what unencrypted `http://` traffic uses.

> **Q:** Does an attacker have to be on the same Wi-Fi network as you?
> **A:** Usually they are, but they don't have to be. Anyone close enough, with an antenna that picks up nearby wireless packets, can capture them, especially on unencrypted networks. Software exists that listens to every network in range.

> **Q:** Does the attacker need to know your IP address first?
> **A:** No. An **IP address** is a computer's unique address on the internet, like a postal address. The sender and receiver IPs are visible in the packets flying through the air, so the attacker learns them just by listening.

### Threat 3: cookies and session hijacking

When you log in, the server needs to remember you as you click around (open emails, add to your cart). It does this with a **cookie**:

```http
HTTP/3 200
Set-Cookie: session=1234abcd
```

- `200` is the **status code** for OK (like the familiar `404` Not Found).
- `Set-Cookie` stores a key-value pair in your browser. Real values are long random strings. `1234abcd` just keeps the example readable.
- **Analogy:** it's like having your **hand stamped** at an amusement park, bar, or club. You show your ticket or ID once, and after that you just show the stamp.

On every later request, the browser shows its "stamp":

```http
GET / HTTP/3
Host: www.example.com
Cookie: session=1234abcd
```

A **session** is the server's ability to remember who you are across requests (your shopping session, your inbox). Your cookie value differs from everyone else's, which is how the server tells users apart. A cookie may live only in memory or be stored for a day, a week, or a year, depending on the server.

**Session hijacking:** over HTTP, the `Set-Cookie` and `Cookie` lines travel in the clear. An eavesdropper who sees `session=1234abcd` can send requests with that same cookie, and the server treats them as **you**. You're both "logged in as David." The fix is HTTPS, which encrypts these low-level headers along with everything else.

## HTTPS and TLS

**HTTPS** makes the connection between Alice and Bob fully encrypted, so none of the machines in between can read the envelope's contents. Some information stays visible on the *outside* of the envelope, such as the sender and receiver IP addresses.

The protocol that does the encryption is **TLS (Transport Layer Security)**. Its predecessor was **SSL**, and TLS is the new and improved version modern browsers use. TLS relies on **public-key cryptography** (Lecture 1), which solves the chicken-and-egg problem of talking securely to a site you've never visited, without a shared secret agreed in advance.

### Certificates and Certificate Authorities

- The web server has a public/private key pair. The private key stays private.
- It also has a **certificate**: essentially its **public key, digitally signed by a trusted third party**.
- The format is **X.509**. Think of a certificate as a printed page listing the **website's name**, **how long it's valid**, and its **public key**.
- The signers are **Certificate Authorities (CAs)**: companies and organizations whose job is to sign certificates.
- Browser makers (Apple, Microsoft, Google, Mozilla) ship a list of CAs they trust in Safari, Edge, Chrome, and Firefox. If you trust the browser maker, then by **transitivity** you trust the CAs it trusts.

### How the browser checks a certificate

1. It **downloads the site's certificate** over HTTPS.
2. It **hashes** certain fields of the certificate with a hash function, producing a fixed-size value.
3. It takes the **signature** on the certificate and uses the **issuing CA's public key** to check it. In the lecture's words, it effectively "decrypts" the signature back into a hash.
4. If that hash **matches** the one from step 2, the CA really signed this certificate, so the browser trusts the connection.

> ⚠️ The official notes say the browser verifies using "the public key of the website." The lecture itself gets it right: the certificate signature is checked with the **issuing CA's public key**. The website's own public key is what the certificate vouches for, and the server proves it holds the matching private key during the handshake. 📌 In practice a CA signs through **intermediate certificates**, so the browser checks a *chain* up to a trusted root. It also checks that the domain name matches and that the certificate hasn't expired or been revoked.

**What HTTPS does *not* hide:** the domain you visit (visible through DNS and TLS SNI), your IP address, and traffic volume and timing.

## SSL stripping

TLS is mathematically sound, but **humans are the weak link**. **SSL stripping** (the name is historical, and it applies to TLS too) tricks you into thinking you have a secure connection when you don't, or when you have a secure connection to the **attacker's** site.

**How it works**

1. Most people type `example.com` or `www.example.com`, not `https://…`. The browser helpfully fills in a full URL and may try **HTTP first**.
2. That first plain-HTTP request is the attacker's opening:
   ```http
   GET / HTTP/3
   Host: www.example.com
   ```
3. A MITM (Eve) answers instead of Bob, who never sees the request:
   ```http
   HTTP/3 307
   Location: https://www.examp1e.com/
   ```
   `307` is a **redirect** status code: "detour, go to this other URL instead."
4. The new URL is HTTPS and the browser shows it as secure, so you relax. But look closely: **`examp1e.com`**, with the digit **1** instead of the letter **l**. In many fonts you can't tell them apart.
5. You now have a **perfectly encrypted connection to Eve's server**, which opens you up to phishing (Lecture 0).

A simpler version just keeps you on plain HTTP the whole time, removing the upgrade to HTTPS.

**Defenses**

- **As a user:** always type `https://` yourself. It's tedious, but it's the most paranoid option, and nearly every site supports HTTPS now.
- **As a server admin:** use **HSTS (HTTP Strict Transport Security)**. The server sends one extra header:

  ```http
  Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
  ```

  - `max-age=31536000` is the number of seconds in a 365-day year. For the next year, the browser **automatically switches to HTTPS** for this domain and **won't allow HTTP at all**, even if you type `http://`.
  - `includeSubDomains` extends the rule to subdomains such as `www.example.com`.
  - HSTS leaves only the **very first request** unprotected. After that, the browser has learned the rule.
  - `preload` tells browser makers they may **build your domain into the browser itself** (for example into Chrome's source code), so even the first visit uses HTTPS.

> 📌 The lecture expands HSTS as "Hypertext Strict Transport Security." The standard name (RFC 6797) is **HTTP Strict Transport Security**. Adding `preload` doesn't enroll you by itself. You submit the domain to the preload list (hstspreload.org), which requires `includeSubDomains` and a `max-age` of at least one year.

> **Q:** Registrars try to block lookalike domains like `exam1e.com`. Why do they still exist?
> **A:** There are many registrars (the companies that sell or rent domain names), and not all are equally good at detecting lookalikes. There are also hundreds of top-level domains, so an attacker can pick `example.<something-else>`. Such domains may get shut down eventually, but maybe only after they've fooled 1, 10, or 100 people.

> **Q:** Is HTTPS the best defense against cookies and supercookies, or should I clear cookies often?
> **A:** **Supercookies** are injected by your ISP, company, or university into your traffic, so you can't stop them in the browser. You have to opt out with whoever injects them. AT&T and Verizon did this to mobile customers' HTTP requests, and customers had to opt out through their account settings. HTTPS makes it much harder, because injecters can't insert anything into encrypted traffic. The exception is when you've let your company or school install software on your device (see proxies below). Advice: always use HTTPS, and check whether your mobile carrier does this.

> **Q:** Could every router hop "stamp" packets, like a passport, to verify integrity?
> **A:** In theory, but nobody controls or coordinates all the routers in between. That's why **end-to-end encryption** (Lecture 1) is the better model: the sender and receiver do the encryption, so you don't need to trust anyone in the middle.

## VPN (Virtual Private Network)

- HTTPS protects only web traffic between browser and server. A **VPN** encrypts **all** your internet traffic between you and the VPN server.
- Alice and Bob (Bob being the VPN server) set up an **encrypted tunnel**, so routers and other machines in between see only ciphertext.
- **Corporate use:** you run VPN software on your laptop or phone and authenticate with a username and password, often plus a 2FA code or a USB key. After that, all traffic to company services (email, files, video conferencing) is encrypted between you (point A) and the company (point B).
- **Side effect: you get the VPN server's IP.** Sites you visit (Gmail, Amazon) see Bob's IP, not Alice's. That's why VPNs are used to **appear to be in another country**, for work resources or, as the lecture jokes, for streaming services only available elsewhere.

## SSH (Secure Shell)

- **SSH** is a protocol for connecting to a **remote server and running commands on it**, mainly used by programmers and system administrators. It can also carry other traffic, VPN-style.
- The lecture's demo, where `$` is the conventional prompt meaning "type your command here":

  ```console
  $ date
  Thu Jan  1 00:00:00 EST 1970
  $ ssh stanford.edu
  $ date
  Wed Dec 31 21:00:00 PST 1969
  ```

  The first `date` runs on the local machine (Eastern time). After `ssh stanford.edu`, the same command runs on **Stanford's server** (Pacific time), three hours "in the past." The dates are a joke about the Unix epoch.
- Everything typed after `ssh`, even a harmless `date`, is **encrypted**, so nobody between the two points can see what you're running. You still need credentials and permission on the remote server.

## Ports and port scanning

Besides the destination IP address, the outside of each envelope carries a **port number**: an agreed-upon number that says **which service** the packet is for (web server vs. email vs. chat).

| Port | Service |
|---|---|
| 22 | SSH |
| 80 | HTTP |
| 443 | HTTPS |

Visiting `http://www.example.com` sends packets to port **80**. If the server redirects you to HTTPS, the browser sends a new request to port **443**. There are hundreds or thousands of other standard numbers, but you don't need to memorize them.

A computer can listen on no ports at all, which means no inbound connections. Servers usually listen on several.

**Security through obscurity doesn't work.** You might think: "Everyone knows port 22 and port 80, so I'll run my service on a random port between 0 and ~65,000." But **port scanning**, a loop that tries every port, like the brute-force password loop from Lecture 0, is easy. It "knocks on every door" and finds whichever services answer. A non-standard port is fine as long as the service is also properly encrypted, authenticated, and patched. On its own it doesn't protect anything.

### Penetration testing and ethical hacking

- **Penetration testing (pen testing)** is a job: you're hired to **try to break into** an organization's systems before real adversaries do. That can mean scanning for ports that shouldn't be open ("no sense opening a door if no one's meant to go through it"), brute-forcing passwords, or socially engineering employees.
- **Ethical hacking** is the same skill used **legally**. You get paid to find flaws as long as you report them to the owner first, so they can fix them.
- **Red team vs. blue team**: some companies turn this into a game. The red team attacks and the blue team defends, and weaknesses surface before outsiders find them.

## Firewalls

The name comes from buildings: a physical **firewall** between two stores stops a fire in one from spreading to the other.

A digital firewall is software between your network and the outside world (or another network) that:

- **keeps in** data that shouldn't leave, such as an internal chat or intercom system that should never reach the public internet, and
- **keeps out** traffic that shouldn't come in. A home network with no servers can block all inbound connections.

Firewalls can **poke holes** for services that need outside connections, such as video calls.

**Ways to filter**

1. **By IP address.** For example, a parent blocks the IPs of social-media sites at home. The limit is **out-of-band paths**: a kid's phone on the mobile network skips the home firewall entirely. Know exactly which network you're filtering.
2. **By port.** For example, block every port except **22** so you can still manage a server over SSH, or open whatever port your VPN uses.
3. **By content, with deep packet inspection (DPI).** The firewall opens the envelope and looks inside. It can block sites by domain name instead of just IP, watch **who emails whom** (companies use this to stop employees emailing the press or competitors about unreleased products), and scan attachments for **malware**.

### Proxies

- A **proxy** is a server or piece of software **between** two points. It is essentially a machine in the middle by design: Alice inside the network, Bob outside, and Eve as the proxy.
- It can pass traffic along or **drop** it. Networks with a single path out (a company or university) often require your devices to use the proxy, so **all traffic goes through it**.

**Employer- or school-issued devices:** your company or school may have installed software with root/admin rights that can **monitor everything** you do. It may also have added **its own certificate authority** to the device's trusted list. Then:

- You think you're on `https://gmail.com` with a padlock.
- You're actually talking to the **company's proxy**, which shows a certificate signed by the company CA. Your device trusts that CA, so no warning appears.
- The proxy decrypts your traffic, inspects it, and may forward it on. It's a MITM set up with the device owner's permission.

If a device has ever been out of your control, you don't know what's installed on it.

### URL rewriting

Links in company or school email often don't go where they say. Hover over one and you may see something like:

```
https://example.com?url=https://gmail.com
```

- An email proxy **rewrote every link** to go through the organization's server (here `example.com`), with the real destination added as `url=`.
- When you click, the organization can **check the URL** against lists of known malware and phishing sites and block it.
- It can also **log** it ("David is visiting Gmail again"). The machine in the middle is right there in the URL, and it sees every link you click.

> **Q:** What's the difference between a VPN and Tor? And can my company or school see what I do if I'm on a VPN?
> **A:** A **VPN** is an encrypted connection between two points. Observers can't see *what* you're doing, but it's obvious where your traffic comes out, and a VPN provider could be subpoenaed. It **secures your data but doesn't preserve privacy** in the same way. **Tor** is privacy-focused: your traffic bounces through many servers so it's hard to trace back (covered in Lecture 4). If someone installed software with admin rights on your device, such as their own CA, **all bets are off**. You're open to MITM or proxy inspection, and they may be monitoring everything anyway.

## Malware

**Malware** (malicious software) is software written to do harm. Software can do *anything* the operating system allows: delete all your files, send spam, mine bitcoin, email your files to an adversary. Whether a program is malicious depends on the person who wrote it or runs it.

What separates a virus from Microsoft Word or Spotify? Mostly **ethics**, plus business pressure (getting caught would be bad for business). Well-meaning software can also do harm by accident, through bugs. Modern operating systems increasingly **sandbox** apps. iOS is especially strict: apps must ask **permission** to use the network, camera, or microphone. Those prompts are only useful if you read them instead of tapping OK every time.

| Type | How it spreads / what it does |
|---|---|
| **Virus** | Attaches to a host, as in biology. It usually needs **human action**: opening an infected file or clicking an email attachment. Once running, it can do anything |
| **Worm** | Spreads **from computer to computer without human action**. An infected machine **port-scans** the network for other machines and breaks into any that listen on a port and are unencrypted, unauthenticated, or otherwise vulnerable. Worms spread through software bugs and holes in firewalls |
| **Botnet** | Wrecking your machine doesn't help an attacker long term. Better to install quiet software that **waits for commands**. Infect thousands of computers and you control a network that can attack, send spam, or mine bitcoin **all at once** |

**Your computer's value to an attacker isn't just its own data.** It's a **node** in a network the attacker can use against others.

### Denial of service (DoS) and DDoS

- **DoS**: overwhelm a server so real users can't get service, for political, financial, or other reasons. A server has limited memory and can do only so much work per second, so bogus requests crowd out real ones.
- One attacker hitting reload on google.com doesn't work, because Google has far more resources than you. DoS only works if you out-muscle the target.
- **DDoS (distributed DoS)**: command a botnet to hit the target **simultaneously**, whether a giant like Google or a small business someone dislikes.
- **Why DDoS is hard to block:** the target can firewall one attacking IP, but not thousands. Many innocent users also **share one public IP** behind a campus or company network. Blocking those IPs would deny service to legitimate people on the same network as an infected machine.

## Antivirus, automatic updates, and zero-days

- **Antivirus software** runs constantly or on a schedule, detects **known** viruses and worms, and removes them, sometimes with a reboot. It may be too late for damage already done (spam sent, files deleted), but it stops further harm.
- Its weakness: it only knows threats it's been **updated** for.
- **Automatic updates** (for antivirus and the whole OS) are, on balance, **good for society**:
  - Everyone runs the latest versions, so you're not vulnerable to **yesterday's mistakes**. You're still exposed to today's and tomorrow's bugs.
  - Vendors can focus on current versions instead of supporting old ones forever.
  - Downside: vendors sometimes ship updates that **break** computers. To limit the damage, they roll updates out gradually to a few users, then more.
  - The worst feeling: getting attacked and learning that a fix had already been released.
- **Zero-day attack**: a new virus, worm, or exploit released before the world knows about it. Humans still have to notice it, write a fix, and ship it, which can take a day or a week, and you're exposed until then.

**Defense in depth.** No single measure is enough: not antivirus alone, not a good password alone. Build a **gauntlet** of layers so an attacker has to get through several. Security is never absolute. The goal is to **raise the cost and risk** to the adversary until they lose interest in you.

## Review questions

<details><summary>1. Your café Wi-Fi uses WPA2. Is your HTTP traffic safe?</summary>

No. WPA2 encrypts only the hop between your device and the access point. From there to the web server, plain HTTP is readable and changeable by any router or machine in the middle. You still need HTTPS.
</details>

<details><summary>2. Name three things an on-path attacker can do to plain HTTP traffic.</summary>

Read it (packet sniffing: search queries, card numbers), change it (inject ads or malicious scripts into the HTML), and steal session cookies to hijack your logged-in session.
</details>

<details><summary>3. Explain session hijacking with the hand-stamp analogy.</summary>

After you log in, the server stamps your hand (`Set-Cookie: session=…`), and you show the stamp on every request (`Cookie: session=…`). Over HTTP, anyone watching can copy the stamp and show it themselves, and the server treats them as you. HTTPS hides the stamp.
</details>

<details><summary>4. What three guarantees does TLS provide, and how does the browser trust a certificate?</summary>

Confidentiality, integrity, and server authentication. The browser hashes the certificate and checks the CA's signature with the issuing CA's public key. The CA must be one the browser maker trusts, and the hashes must match.
</details>

<details><summary>5. Walk through an SSL-stripping attack that ends on an HTTPS page.</summary>

The victim types `example.com`, and the browser sends a plain HTTP request. A MITM answers with a `307` redirect to `https://www.examp1e.com` (digit 1). The victim sees HTTPS and a padlock, but the encrypted connection goes to the attacker's server, which can then phish them.
</details>

<details><summary>6. What does `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload` do?</summary>

It tells the browser to use only HTTPS for this domain and all its subdomains for one year, and to refuse HTTP. `preload` asks browser makers to build the rule into the browser, so even the first visit is protected.
</details>

<details><summary>7. VPN vs. HTTPS vs. SSH: what does each encrypt?</summary>

HTTPS encrypts web traffic between your browser and one website. A VPN encrypts all your traffic between your device and the VPN server, and you appear to have the server's IP. SSH encrypts a remote command session (and can tunnel other traffic).
</details>

<details><summary>8. Why doesn't moving SSH from port 22 to port 48213 secure it?</summary>

A port scan tries every port (about 65,000) and quickly finds whatever is listening. That's security through obscurity. The service itself still needs strong authentication, encryption, and patches.
</details>

<details><summary>9. How can your employer read your HTTPS Gmail traffic on a company laptop?</summary>

They install their own certificate authority on the laptop and route traffic through a proxy. The proxy shows a certificate for gmail.com signed by the company CA, which the laptop trusts, so there's no warning. It decrypts, inspects, and forwards your traffic. Admin-installed monitoring software could see everything anyway.
</details>

<details><summary>10. Virus vs. worm vs. botnet, and why is a DDoS hard to block?</summary>

A virus needs a human to run it. A worm spreads by itself, scanning for vulnerable machines. A botnet is many infected machines taking orders from one attacker. A DDoS comes from thousands of IPs, many of them shared with innocent users behind the same campus or company address, so blocking them all would also block legitimate users.
</details>

<details><summary>11. You have antivirus and automatic updates. Why can you still be compromised?</summary>

Zero-day attacks exploit flaws before vendors know about them or ship a fix. Antivirus only knows threats it has been updated for. That's why you layer defenses (defense in depth) instead of relying on one.
</details>
