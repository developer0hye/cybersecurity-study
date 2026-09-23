# Glossary & Cheat Sheet

## What defends against what

| Threat | Primary defenses | Lecture |
|---|---|---|
| Brute-force / dictionary attack on login | Long unique passwords, rate limiting & lockout, MFA | 0 |
| Credential stuffing | Unique password per site (password manager), MFA, breached-password checks | 0 |
| Phishing | Password manager autofill, passkeys / FIDO2 keys, type URLs yourself | 0, 3 |
| SIM swapping | Authenticator app or hardware key instead of SMS | 0 |
| Stolen password database | Salted, slow hashing (Argon2id / scrypt / bcrypt) | 1 |
| Lost or stolen device | Full-disk encryption, screen lock | 1 |
| Eavesdropping / packet sniffing | TLS (HTTPS), WPA2/WPA3, VPN | 2 |
| MITM / SSL stripping | HTTPS + certificate validation, HSTS (+ preload) | 2 |
| Session hijacking | HTTPS everywhere, `Secure` + `HttpOnly` + `SameSite` cookies | 2, 4 |
| Port scanning / exposed services | Firewall (default-deny), close unused ports, keep services patched | 2 |
| Malware / known vulnerabilities | Automatic updates, antivirus/EDR, install from trusted, signed sources | 2, 3 |
| DDoS | CDN / scrubbing service, rate limiting | 2 |
| XSS | Context-aware output escaping, CSP, `HttpOnly` cookies | 3 |
| SQL injection | Parameterized queries, least-privilege DB user | 3 |
| Command injection | No shell (argument lists), no `eval`, input allowlists | 3 |
| Tampered client-side checks | Server-side validation & authorization | 3 |
| CSRF | Safe GET, CSRF tokens, `SameSite` cookies | 3 |
| Buffer overflow / ACE | Memory-safe languages, bounds checks, ASLR, DEP/NX, canaries | 3 |
| Malicious packages | Signed packages, lockfiles & version pinning, watch for typosquatting | 3 |
| Cross-site tracking | Block third-party cookies, strip tracking params, tracker blockers | 4 |
| Fingerprinting | Tor Browser, anti-fingerprinting browser settings | 4 |
| DNS snooping | DoH / DoT, VPN, Tor | 4 |

## Glossary

| Term | Definition |
|---|---|
| **2FA / MFA** | Authentication with 2+ factors of different types: knowledge, possession, inherence |
| **ACE** | Arbitrary code execution: an attacker makes a program run code of their choosing |
| **AES** | Advanced Encryption Standard, the standard symmetric cipher |
| **Antivirus / EDR** | Software that detects malware by signature and behavior |
| **Argon2id / scrypt / bcrypt** | Deliberately slow, memory-hard password hashing functions |
| **Authentication (AuthN)** | Verifying *who* someone is |
| **Authorization (AuthZ)** | Deciding *what* an authenticated user may do |
| **Botnet** | A network of compromised machines under an attacker's remote control |
| **Brute-force attack** | Trying every possible combination |
| **Buffer overflow** | Writing past the end of a fixed-size buffer and corrupting nearby memory |
| **CA (Certificate Authority)** | A trusted third party that signs X.509 certificates |
| **Ciphertext / plaintext** | Encrypted / unencrypted data |
| **Code signing** | A developer's digital signature on software, so its origin and integrity can be verified |
| **Cookie** | A small piece of data a site stores in the browser and receives back on each request |
| **Credential stuffing** | Replaying leaked username/password pairs on other sites |
| **Cryptanalysis** | The study of breaking cryptographic systems |
| **CSP** | Content-Security-Policy: a header that limits where scripts and styles may load from |
| **CSRF** | Cross-site request forgery: tricking a browser into sending an authenticated request to another site |
| **CVE / CVSS / EPSS / KEV** | Vulnerability ID / severity score / exploitation probability / CISA's catalog of known-exploited CVEs |
| **DDoS** | Distributed denial of service: overwhelming a service with traffic from many sources |
| **Deep packet inspection (DPI)** | Inspecting packet payloads, not just headers, usually on a proxy |
| **Dictionary attack** | Trying likely passwords (words, leaked lists) first |
| **Diffie-Hellman** | A key-exchange protocol that creates a shared secret over a public channel |
| **Digital signature** | Proof of authenticity and integrity: made with a private key, checked with the public key |
| **DNS / DoH / DoT** | Domain-name lookup / DNS over HTTPS / DNS over TLS |
| **E2EE** | End-to-end encryption: only the endpoints can decrypt, not the service in the middle |
| **Encoding** | Changing the format of data (e.g. Base64). Uses no key and provides no security |
| **Ethical hacking / pentesting** | Authorized attacking to find vulnerabilities |
| **Fingerprinting** | Identifying a user from device and browser traits without cookies |
| **Firewall** | Filters traffic by IP, port, and protocol |
| **Full-disk encryption** | Encrypting an entire drive (encryption at rest) |
| **Hash function** | A one-way function mapping any input to a fixed-length output |
| **HSTS** | HTTP Strict Transport Security: the browser must use HTTPS for a domain |
| **HTTPS / TLS** | HTTP carried inside Transport Layer Security: encryption, integrity, server authentication |
| **Keylogger** | Malware or hardware that records keystrokes |
| **MITM** | Machine-in-the-middle: an attacker on the path who reads or changes traffic |
| **OTP / TOTP** | One-time password / time-based OTP (authenticator apps) |
| **Package manager** | A tool that installs third-party libraries (npm, pip, apt), a supply-chain risk |
| **Passkey (WebAuthn / FIDO2)** | Passwordless login using a per-site key pair on your device |
| **Password manager** | Software that generates and stores unique passwords |
| **Pepper** | A secret value added to all password hashes and stored outside the database |
| **Phishing** | Tricking users into giving up credentials through fake sites or messages |
| **Port / port scanning** | A number selecting a service on a host / probing which ports are open |
| **Post-quantum cryptography** | Algorithms believed secure against quantum computers (ML-KEM, ML-DSA, SLH-DSA) |
| **Prepared statement** | A SQL query with placeholders. Values are sent separately and can't change the query |
| **Private browsing** | A browser mode that discards local history and cookies at the end of the session |
| **Public-key (asymmetric) crypto** | Crypto with a public/private key pair (RSA, ECC) |
| **Rainbow table** | A precomputed hash-to-password lookup. Salting defeats it |
| **Ransomware** | Malware that encrypts your data and demands payment |
| **Referer / Referrer-Policy** | A header revealing the previous page / a policy limiting what it contains |
| **Salt** | A random, non-secret value added to each password before hashing |
| **Secret-key (symmetric) crypto** | Crypto where one shared key encrypts and decrypts (AES) |
| **Secure deletion** | Overwriting data so it can't be recovered |
| **Server-side validation** | Checking input on the server, the only enforceable validation |
| **Session hijacking** | Stealing a session cookie to impersonate a user |
| **SIM swapping** | Moving a victim's phone number to an attacker's SIM |
| **Social engineering** | Manipulating people instead of breaking technology |
| **SSH** | Secure Shell: encrypted remote command execution |
| **SSL stripping** | Downgrading a victim from HTTPS to HTTP |
| **SSO** | Single sign-on: one identity provider for many services |
| **Supercookie** | A tracking ID the user can't easily clear (ISP-injected headers, abused browser storage) |
| **Third-party cookie** | A cookie set by a domain other than the one in the address bar, used for cross-site tracking |
| **Tor** | Onion routing through three relays for anonymity |
| **Tracking parameter** | An identifier in a URL (e.g. `click_id`, `gclid`) |
| **User-Agent** | A header that describes the browser, OS, and device |
| **Virus / worm / trojan** | Malware that needs a host / spreads by itself / disguises itself as legitimate software |
| **VPN** | An encrypted tunnel to a server that becomes your apparent IP |
| **WPA2 / WPA3** | Wi-Fi encryption standards |
| **X.509 certificate** | A document binding a domain to a public key, signed by a CA |
| **XSS** | Cross-site scripting: injecting script that runs in other users' browsers |
| **Zero-day** | A vulnerability exploited before a patch exists |
