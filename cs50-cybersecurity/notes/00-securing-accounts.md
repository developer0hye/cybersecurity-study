# Lecture 0: Securing Accounts

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/0/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/0/)

## TL;DR

- Security is always a **tradeoff with usability**. The goal is to raise the attacker's cost (time, money, effort) until the attack is not worth it.
- Length adds more strength to a password than complexity does. What matters most is to **never reuse passwords**.
- Add a second factor. From weakest to strongest: SMS OTP < authenticator-app OTP < hardware key / passkey.
- Most real account takeovers come from people (phishing, social engineering) and leaked passwords (credential stuffing), not from clever math.

## Core concepts

### Authentication vs. authorization

| | Question it answers | Example |
|---|---|---|
| **Authentication** (AuthN) | *Who are you?* | username + password, passkey |
| **Authorization** (AuthZ) | *What are you allowed to do?* | you can read this doc but not delete it |

> ⚠️ The official notes say "Authorization is the act of verifying that you are … the person who should have access." That describes **authentication**. The two terms get mixed up all the time, so keep them apart.

### Brute-force and dictionary attacks

- **Brute-force attack**: try every possible combination.
- **Dictionary attack**: try likely passwords first (common words, leaked password lists, `password123`). In practice this is much faster than brute force.
- The number of combinations is `charset_size ^ length`:

| Password | Keyspace |
|---|---|
| 4 digits | 10⁴ = 10,000 |
| 4 letters (a–z, A–Z) | 52⁴ ≈ 7.3 million |
| 4 chars (letters + digits + punctuation, 94 symbols) | 94⁴ ≈ 78 million |
| 12 chars from the same 94 symbols | 94¹² ≈ 4.7 × 10²³ |

Each extra character multiplies the work by the size of the charset. Adding more kinds of characters only raises the base of the exponent, so **length wins**. Try [`demos/01_keyspace.py`](../demos/01_keyspace.py).

A phone's 4-digit PIN survives only because the device **rate-limits and locks out** attempts. The math doesn't protect it.

### NIST guidance (SP 800-63B)

NIST (National Institute of Standards and Technology) publishes the password guidance that most modern policies follow. The points the lecture highlights:

- Require a minimum length and allow long passwords (at least 64 characters), with all printable ASCII and Unicode characters allowed.
- Check new passwords against **breached password lists**, dictionary words, repeated sequences, and context-specific words such as the service name.
- **Do not** force periodic password changes. Rotate only when there is evidence of compromise.
- Do not show password hints to unauthenticated users.
- **Rate-limit** failed login attempts.

> 📌 The lecture (2023) quotes an 8-character minimum. The final **SP 800-63B Revision 4** (2025) raised it to **15 characters when the password is the only factor**, keeps 8 as the minimum when it is part of MFA, and says verifiers **shall not** impose composition rules such as "must include a symbol". Check the current revision when you write a policy.

### Multi-factor authentication (MFA / 2FA)

The three factor types:

1. **Knowledge**: something you know (password, PIN)
2. **Possession**: something you have (phone, hardware security key)
3. **Inherence**: something you are (fingerprint, face)

Two passwords still count as one factor. MFA means factors of *different* types.

### One-time passwords (OTP)

- **SMS OTP** is weak because of **SIM swapping**: the attacker convinces your carrier to move your number to their SIM, and your codes go to them.
- **Authenticator apps** (TOTP: a code derived from a shared secret plus the current time) are better.
- A TOTP code can still be **phished in real time**: a fake site forwards your code to the real site right away. Phishing-resistant options are FIDO2/WebAuthn hardware keys and passkeys (see Lecture 1).

### Attacks on accounts

| Attack | How it works | Defense |
|---|---|---|
| **Keylogging** | Malware or a hardware device records your keystrokes | Don't log in on untrusted or shared machines; keep devices clean |
| **Credential stuffing** | Username/password pairs leaked from site A are tried on site B | Unique password per site; MFA; sites check logins against breach lists |
| **Social engineering** | Manipulates people through trust, pressure, or urgency (fake IT support calls) | Verify through a separate channel; keep security answers non-guessable |
| **Phishing** | Social engineering over technology: a fake login page, a lookalike domain | Type the URL yourself; use password managers and passkeys, which won't fill on the wrong domain |
| **Machine-in-the-middle** (MITM) | A compromised device on the network path reads or changes traffic | Encryption (HTTPS/TLS), certificate validation |

### Reducing the password burden

- **SSO (Single Sign-On)**: log in to many services with one identity provider ("Sign in with Google"). There are fewer passwords to leak, but that one account is now a **single point of failure**, so protect it with strong MFA.
- **Password managers** generate and store a unique random password per site. They also resist phishing, because autofill matches the real domain. The tradeoff is "all eggs in one basket", so use a strong master password plus MFA.
- **Passkeys** replace passwords with a public/private key pair. The site stores only the public key, so a database leak reveals nothing usable, and the key is bound to the real domain. Lecture 1 covers the cryptography behind them.

## Review questions

<details><summary>1. Why is a 16-character lowercase passphrase often stronger than an 8-character "complex" password?</summary>

26¹⁶ ≈ 4.4 × 10²² vs. 94⁸ ≈ 6.1 × 10¹⁵. Length grows the exponent, while complexity only grows the base. A passphrase is also easier to remember. It still must not be a well-known phrase, or it falls to a dictionary attack.
</details>

<details><summary>2. Why is SMS the weakest second factor?</summary>

SIM swapping and SS7 interception let an attacker receive your texts without touching your phone. Like other OTPs, SMS codes can also be phished in real time.
</details>

<details><summary>3. Why does NIST advise against forced periodic password changes?</summary>

Users respond with predictable patterns (`Spring2024!` → `Summer2024!`). This weakens passwords without stopping attackers who already have the current one. Change a password when there is evidence of compromise.
</details>

<details><summary>4. What single habit defeats credential stuffing?</summary>

Using a unique password for every site, which in practice means a password manager. A leak from one site then can't be replayed anywhere else.
</details>
