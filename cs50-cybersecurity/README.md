# CS50's Introduction to Cybersecurity

Study notes for **Harvard CS50's Introduction to Cybersecurity (2023)**, taught by David J. Malan. The full course is also posted as a single 7h 44m video on [freeCodeCamp's YouTube channel](https://www.youtube.com/watch?v=9HOpanT0GRs).

These notes follow the [official lecture notes](https://cs50.harvard.edu/cybersecurity/notes/) and add:

- **Corrections and updates** where the 2023 material is imprecise or out of date (marked ⚠️ and 📌), e.g. authentication vs. authorization, NIST SP 800-63B Rev. 4, post-quantum standards, `Referrer-Policy` values
- **Deeper explanations** of the mechanisms (Diffie-Hellman, TLS certificate validation, parameterized queries, CSRF defenses, Tor)
- **Runnable Python demos** you can run and change
- **Review questions** with hidden answers at the end of each lecture

## Where this fits

This is the first course in my [AI × Security study roadmap](../roadmap/). It covers most of the core concepts, cryptography, and web attacks in [Phase 1: Security foundations](../roadmap/01-security-foundations.md). Those classic attacks come back in the AI-era phases:

- SQL injection, XSS, and command injection (L3) → prompt injection and improper output handling in [Phase 3](../roadmap/03-attacks-on-ai-systems.md)
- Phishing, social engineering, and passkeys (L0, L1) → AI-written phishing and deepfake fraud in [Phase 4](../roadmap/04-attacks-powered-by-ai.md)

The [crosswalk table](../roadmap/README.md#crosswalk-classic-security--ai-era-equivalent) pairs each classic concept with its AI-era equivalent.

Networking fundamentals continue in [Professor Messer's Network+](../comptia-network-plus/).

## Contents

| # | Lecture | Topics |
|---|---|---|
| 0 | [Securing Accounts](notes/00-securing-accounts.md) | AuthN vs AuthZ, brute-force & dictionary attacks, NIST guidance, MFA, OTP, phishing, credential stuffing, SSO, password managers, passkeys |
| 1 | [Securing Data](notes/01-securing-data.md) | hashing, salting, symmetric vs. public-key crypto, Diffie-Hellman, digital signatures, passkeys, E2EE, secure deletion, full-disk encryption, quantum |
| 2 | [Securing Systems](notes/02-securing-systems.md) | Wi-Fi/WPA, HTTP threats, HTTPS/TLS & certificates, SSL stripping & HSTS, VPN, SSH, ports, firewalls, DPI, malware, zero-days |
| 3 | [Securing Software](notes/03-securing-software.md) | XSS (reflected/stored/DOM), escaping, CSP, SQL injection, prepared statements, command injection, server-side validation, CSRF, buffer overflows, supply chain, CVE/CVSS/EPSS/KEV |
| 4 | [Preserving Privacy](notes/04-preserving-privacy.md) | server logs, Referer, fingerprinting, session/tracking/third-party cookies, tracking parameters, private browsing, supercookies, DNS/DoH, VPN, Tor, permissions |
| – | [Glossary & cheat sheet](notes/glossary.md) | every term in one place, plus a "what defends against what" table |

## Demos

Requires Python 3.9+ and only the standard library.

```bash
cd demos
python3 01_keyspace.py          # L0: brute-force cost vs. length and charset
python3 02_hash_and_salt.py     # L1: plain SHA-256 vs. salted scrypt
python3 03_diffie_hellman.py    # L1: toy Diffie-Hellman key exchange
python3 04_sql_injection.py     # L3: ' OR '1'='1 vs. parameterized query
python3 05_xss_escaping.py      # L3: HTML escaping
python3 06_command_injection.py # L3: shell=True vs. argument list
```

The demos are for learning only. Use them on your own machine, and only test systems you are authorized to test.

## Suggested study path

1. Read a lecture note here (about 20–30 minutes).
2. Run that lecture's demos.
3. Answer the review questions without peeking.
4. Watch only the parts of the [official lecture video](https://cs50.harvard.edu/cybersecurity/) that are still unclear, at 1.5–2× speed.
5. Optionally do the [official problem sets](https://cs50.harvard.edu/cybersecurity/) and get the free certificate through edX.

## Source & license

- Original course: [CS50's Introduction to Cybersecurity](https://cs50.harvard.edu/cybersecurity/) by David J. Malan, Harvard University. The course materials are licensed under [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
- These notes are an unofficial derivative work with no affiliation with or endorsement by Harvard or CS50. They are released under the same **[CC BY-NC-SA 4.0](LICENSE)** license, which applies to everything in this folder.
