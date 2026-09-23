# Lecture 1: Securing Data

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/1/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/1/)

## TL;DR

- Servers should never store passwords. They store a **salted, slow hash** of each one.
- **Hashing** is one-way. **Encryption** is two-way with a key. **Encoding** is not security at all.
- **Symmetric** crypto uses one shared secret and is fast. **Asymmetric** (public-key) crypto uses a key pair and solves "how do strangers agree on a secret?"
- Public-key crypto gives us **key exchange** (Diffie-Hellman), **digital signatures**, **passkeys**, and HTTPS.
- Protect data **in transit** (TLS, end-to-end encryption) and **at rest** (full-disk encryption).

## Core concepts

### Storing passwords: hashing

A **hash function** maps input of any length to a fixed-length output. For password storage it must be:

- **One-way (preimage-resistant)**: you can't recover the input from the hash.
- **Deterministic**: the same input always gives the same hash, so the server can compare.
- **Collision-resistant**: it's infeasible to find two inputs with the same hash.

Login flow: `hash(typed_password) == stored_hash` → allow.

> ⚠️ The official notes say "without access to the precise hash function, an adversary cannot output the correct password." Real systems don't depend on the algorithm being secret. Assume the attacker knows it (**Kerckhoffs's principle**). Security comes from one-wayness, from salting, and from making each guess expensive.

### Attacks on stolen hashes

- **Dictionary / brute-force**: hash every candidate and compare. Fast hashes (MD5, SHA-256) allow billions of guesses per second on GPUs.
- **Rainbow tables**: a precomputed table from hash back to password. It trades storage for time, but works only when the hashes are **unsalted**.
- **Identical hashes** show that users share a password. Crack one, and you've cracked them all.

### Salting

A **salt** is a random value, unique per user, that is combined with the password before hashing and stored next to the hash.

- Same password → different hashes, so shared passwords are no longer visible.
- Precomputed rainbow tables stop working, because the attacker would need one table per salt.
- A salt is **not secret**. It exists to make every hash unique.

**Modern practice:** use a deliberately **slow, memory-hard** password hashing function: **Argon2id** (preferred), **scrypt**, **bcrypt**, or PBKDF2. Plain SHA-256 is the wrong tool even with a salt, because it is fast. See [`demos/02_hash_and_salt.py`](../demos/02_hash_and_salt.py).

A **pepper** is an optional extra secret added to every hash and stored outside the database, for example in an HSM or a config secret.

### Codes, ciphers, and keys

| Term | Meaning |
|---|---|
| **Encoding / decoding** | Maps words to other words or symbols. No key is involved, so it is **not security**. Base64 is encoding. |
| **Cipher** | An algorithm that turns **plaintext** into **ciphertext** (encryption) and back (decryption) using a **key** |
| **Key** | A large secret number/string. Security rests on the key, not on hiding the algorithm |
| **Cryptography** | Designing systems for secure communication |
| **Cryptanalysis** | Studying how to **break** those systems |

### Secret-key (symmetric) cryptography

- One **shared key** encrypts and decrypts. AES is the standard.
- It is fast and used for bulk data.
- Problem: **key distribution**. How do two parties who have never met agree on the key without an eavesdropper learning it?

### Public-key (asymmetric) cryptography

- Each party has a **key pair**: a **public key** anyone can know and a **private key** only the owner holds.
- **Encryption**: anyone encrypts with the recipient's *public* key, and only the recipient's *private* key decrypts.
- **RSA** is the classic algorithm. It relies on the difficulty of factoring the product of two large primes. Elliptic-curve crypto (ECC) is the modern alternative with smaller keys.
- It is slow, so real protocols use it to set up a symmetric key and then switch to AES. This design is called **hybrid encryption**.

### Key exchange: Diffie-Hellman

This lets two parties create a shared secret over a public channel:

1. They publicly agree on a prime `p` and a generator `g`.
2. Alice picks a private `a` and sends `A = gᵃ mod p`. Bob picks a private `b` and sends `B = gᵇ mod p`.
3. Alice computes `Bᵃ mod p`, and Bob computes `Aᵇ mod p`. Both equal `gᵃᵇ mod p`, which is the shared secret `s`.
4. An eavesdropper sees `p, g, A, B`, but recovering `a` or `b` means solving the **discrete logarithm problem**, which is infeasible for large numbers.

See [`demos/03_diffie_hellman.py`](../demos/03_diffie_hellman.py). Plain DH doesn't prove *who* you're talking to, so it is combined with signatures and certificates to stop MITM attacks.

### Digital signatures

These prove **who** signed (authenticity) and that the content **hasn't changed** (integrity).

- **Sign**: `hash(message)` → sign the hash with the signer's **private key** → signature.
- **Verify**: the recipient computes `hash(message)` again and uses the signer's **public key** to check the signature against that hash.
- Encryption and signing use the keys in opposite directions: *encrypt with their public key* vs. *sign with your private key*.

> 📌 The lecture describes verification as "decrypting" the signature. That picture fits textbook RSA. Algorithms such as ECDSA and Ed25519 have a separate *verify* operation, so "verify with the public key" is the more general way to say it.

### Passkeys (WebAuthn / FIDO2)

1. **Registration**: your device creates a key pair for *that specific website*. The site stores only the **public key**.
2. **Login**: the site sends a random **challenge**. Your device signs it with the **private key** after you unlock it with a fingerprint, face, or PIN. The site verifies the signature with the public key.

Why this beats passwords:

- There is no shared secret on the server, so a breach leaks nothing usable.
- The key is bound to the site's domain, so it is **phishing-resistant**.
- Nothing needs to be remembered or reused.

Passkeys can be device-bound (like a hardware key) or synced across devices by a platform or password manager.

### Encryption in transit

- **TLS** encrypts the traffic between you and a server, for example HTTPS.
- The server itself, and any intermediary that terminates TLS (an email provider, a chat server), can still read your data.
- **End-to-end encryption (E2EE)**: only the endpoints (sender and recipient devices) hold the keys, so the service in the middle sees only ciphertext. Signal and WhatsApp are examples.

### Deletion and encryption at rest

- **Deleting** a file usually just removes the pointer to it, and the data stays until it is overwritten. This is how forensic recovery works.
- **Secure deletion** overwrites the data with zeros, ones, or random bits.
  > 📌 On **SSDs** and flash storage, wear-leveling means overwriting a file doesn't reliably reach every physical copy. Full-disk encryption plus a key wipe (crypto-erase) is the dependable approach.
- **Full-disk encryption (FDE) / encryption at rest** encrypts the whole drive (BitLocker, FileVault, LUKS). A lost or stolen device reveals nothing.
  - Downsides: lose the key or password and your data is gone, and **ransomware** uses the same technology against you.

### Quantum computing

- **Shor's algorithm**, run on a large enough quantum computer, would break **RSA, Diffie-Hellman, and ECC**.
- **Grover's algorithm** only halves the effective strength of symmetric keys, so AES-256 stays fine.
- "**Harvest now, decrypt later**": attackers can record encrypted traffic today and decrypt it once quantum machines exist.
- 📌 NIST finalized its first **post-quantum cryptography** standards in 2024: **ML-KEM** (FIPS 203) for key exchange, and **ML-DSA** (FIPS 204) and **SLH-DSA** (FIPS 205) for signatures. Browsers and messengers already deploy hybrid post-quantum key exchange.

## Review questions

<details><summary>1. What's the difference between hashing, encryption, and encoding?</summary>

Hashing is one-way with no key, used to verify (passwords, integrity). Encryption is two-way with a key, used to keep data confidential. Encoding is two-way with no key, used to change format (Base64) and provides no security.
</details>

<details><summary>2. Why do we salt passwords, and does the salt need to be secret?</summary>

Salting makes identical passwords produce different hashes and makes precomputed rainbow tables useless. The salt does not need to be secret. It is stored next to the hash.
</details>

<details><summary>3. Why is SHA-256 a bad choice for password storage even with a salt?</summary>

It's designed to be fast, so GPUs can test billions of guesses per second. Password hashing functions like Argon2id, scrypt, and bcrypt are intentionally slow and memory-hard.
</details>

<details><summary>4. Encrypting vs. signing: which key does what?</summary>

To encrypt for Bob, use Bob's public key, and Bob decrypts with his private key. To sign as Alice, use Alice's private key, and anyone verifies with Alice's public key.
</details>

<details><summary>5. Why are passkeys phishing-resistant but TOTP codes are not?</summary>

A passkey is bound to the real site's domain, and the browser won't use it on a lookalike domain. The signed challenge is also useless anywhere else. A person can type a TOTP code into a fake site, which forwards it to the real site right away.
</details>
