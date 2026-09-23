# Lecture 1: Securing Data

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/1/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/1/)

## TL;DR

- Servers should never store passwords. They store a **salted, slow hash** of each one. If a site can email you your current password, it isn't hashing, so stop using it.
- **Hashing** is one-way and throws information away. **Encryption** is two-way with a key. **Codes** and **encoding** are not modern security.
- **Symmetric** crypto (AES, 3DES) uses one shared secret and is fast. But how do strangers like you and Amazon agree on that secret? **Asymmetric** crypto (RSA, Diffie-Hellman) solves that with a public/private key pair.
- The public/private key pair can be used in two directions. *Encrypt with someone's public key* → confidentiality. *Sign with your private key* → **digital signatures**. Passkeys and HTTPS are built on this.
- Keep the **algorithm public and the key secret** (Kerckhoffs's principle). Don't invent your own crypto.
- Protect data **in transit** (TLS, and better, **end-to-end encryption**) and **at rest** (full-disk encryption). Deleting a file doesn't erase it.
- Quantum computers could break today's public-key crypto, so the math must be hardened ahead of time.

---

## 1. Why password storage matters

Last week was about *your* job: pick good passwords. But there's a second party involved. The **server** stores something that lets it check your password every time you log in.

The naive approach is a text file of `username:password` lines:

```
alice:apple
bob:banana
```

Unix-like systems really do store credentials in a file like this, though with extra fields and, today, hashes instead of plaintext. The problem: if an attacker steals this file, they have **everyone's password**, and they can go **credential stuffing** on other sites (Lecture 0). The goal is to **minimize the damage when the database leaks**. Assume "when", not "if".

## 2. Hashing

A **hash function** takes an input (a password) and produces a **hash value**, usually a fixed-length string of letters and digits. Think of it as a black box, a program, or a mathematical function `f(x)`.

### Building intuition: a bad hash function

Malan's toy hash maps a word to the position of its first letter: `apple → 1`, `banana → 2`, `cherry → 3`, …

Two problems:

1. **Collisions**: `avocado` also hashes to `1`. Different inputs, same output.
2. **It leaks information**: seeing `1` tells you the password starts with "A", so you only have 1/26 of the search left.

A good hash looks **random and patternless**. An older real-world hash function turns `apple` into something like `..ekWXa83dhiA`, which reveals nothing about the input, and `banana` and `cherry` give completely different-looking strings.

### How login works with hashes

- **Registration**: Alice sends `alice` / `apple`. The server computes `hash("apple")`, stores `alice:<hash>`, and **throws away** `apple`.
- **Login** (a day or a year later): Alice types `apple` again. The server hashes what she typed with the **same function** and compares the result to the stored hash. Match → authenticated.

The extra work is trivial: a few lines of code, usually from a well-tested **library** rather than your own.

**Benefit:** a stolen file now contains only usernames and hashes, not passwords.

> **Q:** If developers all use the same public libraries, can't an attacker just try those 10–40 functions and reverse the hashes?
> **A:** Attackers can use the same library to *compute* hashes and *compare* them. But hashes can't be *reversed*. We haven't made the system absolutely secure, only **relatively more secure**: attacks now cost more time, money, and risk.

> **Q:** What if the password is intercepted *before* it's hashed?
> **A:** Then hashing doesn't help at all. That's a separate problem, solved by encryption in transit (below).

### Attacks that still work on hashes

- **Dictionary attack**: hash each word in a list (or every fruit!) and compare it against the stolen hashes. This is more work than before, and a lot of work when there are millions of rows.
- **Brute-force attack**: hash `00000000`, `00000001`, …, `aaaaaaaa`, … Eventually `apple` comes up, but it takes time.
- **Rainbow table**: the attacker **precomputes** hashes of dictionary words or all short passwords and stores the `password → hash` table. Cracking then becomes a lookup, with no hashing at attack time. For strong hash functions, the table would need terabytes to petabytes, which limits this attack. It is very effective for short or common passwords.

### The identical-password problem

Carol and Charlie both chose `cherry`. With plain hashing, their stored hashes are **identical**, because a function without randomness always gives the same output. An attacker who sees the file learns that the two have the same password. Maybe they're related or share interests, and that narrows the guessing. With many users, lots of people will share `1234` or `12345678`.

## 3. Salting

**Salting** "sprinkles" extra input into the hash so that identical passwords produce different hashes.

- The hash function now takes **two inputs**: `hash(password, salt)`.
- The salt is chosen **randomly by the server**, not by the user. It's different for each user.
- In Malan's example (an old scheme), the salt is **2 characters**, and the output **begins with the salt**:
  - `cherry` + salt `50` → `50…` (one hash)
  - `cherry` + salt `49` → `49…` (a completely different hash)
- The salt is **not secret**. Its job is to make hashes unique, not to hide anything.

> **Q:** Where is the salt stored?
> **A:** Right in the stored hash string. In this scheme it's the first 2 characters. At login, the server looks up Carol's hash, reads the salt from its first two characters, computes `hash("cherry", "50")`, and compares the result with the full stored value.

Corner case: if two users get the **same salt** by bad luck, their identical passwords show up again. With only 2-character salts and millions of users, salts must repeat. Salting lowers the probability of an attack working. It doesn't make attacks impossible.

> 📌 Modern schemes use long random salts (16 bytes or more), so repeats are effectively impossible.

> **Q:** Is there a point in hashing a password twice?
> **A:** You can, but a well-designed modern hash shouldn't need it, because one pass already gives a random-looking result.
> 📌 Nuance: *password* hashing functions deliberately repeat work internally ("key stretching", e.g. PBKDF2 runs thousands of iterations, and bcrypt has a cost factor) to **slow down** attackers. The point is cost per guess, not extra randomness.

**Soapbox:** don't invent your own hashing or crypto unless it's your full-time job. There are too many corner cases, and researchers have spent years testing the standard algorithms.

### What modern stored hashes look like

Modern hashes are **much longer** strings, with more bits. Carol's and Charlie's look completely different even though both are `cherry`. They start with a marker between dollar signs, like `$y$…`, which tells the system **which algorithm** produced the rest. The documentation for each algorithm lists these codes.

> 📌 `$y$` is **yescrypt**, the default on many current Linux distributions (`/etc/shadow`). Other common prefixes: `$2b$` bcrypt, `$argon2id$` Argon2id, `$6$` SHA-512-crypt.

### Size of the search space

- The early, short hash from the example: about **18 quintillion** (~1.8 × 10¹⁹) possible values. That sounds large, but with enough time, money, and cloud computing, those early hashes **can be broken**.
- Modern long hashes have a number of possible values so large that Malan wasn't sure how to pronounce it, likely more than the atoms in the universe. Brute force won't finish before the end of time, *unless there are other weaknesses*, such as a password of `00000000` that the attacker tries first.

### Red flag: "Forgot password" emails you your password

If a site's password reset emails your **actual current password**, the site can **see** your password. That means it stores it in plaintext or reversibly, and a breach would expose it. Hashes are one-way, so a well-built site *can't* recover your password. It can only let you **reset** it.

What to do: at minimum, stop using the service and make sure that password isn't reused anywhere. At most, tell them why it's a problem.

> **Q:** If my company leaks customer passwords because of bad practices, am I obligated to report it?
> **A:** Ethically, yes. Legally, it depends on your industry, country, and regulations. In practice, companies rarely publish details of breaches. They're embarrassed, may face legal or financial trouble, and don't want to give future attackers information. Society loses the lessons as a result. How much to disclose, and to whom (privately to the vendor or to the public), is a recurring ethical question in security.

### NIST on password storage

NIST requires that verifiers store passwords in a form **resistant to offline attacks**: passwords **SHALL be salted and hashed using a suitable one-way key derivation function**, so that each guess by an attacker who has stolen the hash file is expensive.

The lecture lists **SHA-2** and **SHA-3** families as recommended hash functions. Related algorithms can also check the **authenticity and integrity** of messages, meaning they weren't changed in transit.

> ⚠️ SHA-2 and SHA-3 are great general-purpose cryptographic hashes, but they are **fast**, which is exactly wrong for passwords. For password storage, use a slow, salted **password hashing function / KDF**: **Argon2id** (preferred), **scrypt**, **bcrypt**, or PBKDF2. See [`demos/02_hash_and_salt.py`](../demos/02_hash_and_salt.py).

### One-way hash functions: why they can't be reversed

- They take input of **arbitrary length** and produce output of **fixed length**.
- The domain (all possible inputs) is effectively infinite, and the range (all possible hashes) is **finite**. Mapping infinitely many inputs onto finitely many outputs guarantees **collisions**. Think of 100 passwords in 10 buckets.
- So even the system owner can't tell from a hash whether the password was `apple` or `avocado`. Hashing **throws information away**.
- Side effect: on some systems, a *different* password with the same hash would also let you in. With long modern hashes, the chance of finding one is negligible.
- These are called **cryptographic hash functions** because they are building blocks of **cryptography**, the practice and study of securing data in transit and at rest.

---

## 4. Codes

**Codes** (unrelated to programming code) map **code words** to real messages using a **code book**. Malan showed a page (page 187) from a code book more than 100 years old: code words in the left column, their meanings ("true readings") on the right.

- **Encode**: plaintext → codetext. **Decode**: codetext → plaintext, using the same book.
- Downsides:
  - It's **slow**, because the recipient flips through the book.
  - It's **bulky**, with hundreds of pages.
  - If the book is **stolen**, every past message can be decoded, and every future one too if nobody notices the theft.

## 5. Ciphers

**Ciphers** are **algorithmic**. They work on individual letters, or bits in computers, instead of whole words, and repeat the same steps across the message.

- Pop-culture example: Ralphie's **Little Orphan Annie secret decoder pin** in *A Christmas Story*, which maps letters to numbers and twists to change the mapping.
- WWII: the German **Enigma machine**, a mechanical cipher with rotors and lights, configurable by its settings.

Vocabulary:

| Term | Meaning |
|---|---|
| **Encipher / encrypt** | plaintext → ciphertext (synonyms, and "encrypt" is more common today) |
| **Decipher / decrypt** | ciphertext → plaintext |

## 6. Keys

Everyone can use the **same public, well-tested algorithm**. What makes your use of it unique is a secret **key**. Like a house key, it unlocks the cipher, and typically both sender and receiver need it.

- Keys are just **very large numbers**, ultimately bits. They're often displayed as letters and symbols.
- Without keys, everyone sending the same message with the same algorithm would produce the same ciphertext, and that **leaks information**, just like identical password hashes.

## 7. Secret-key (symmetric) cryptography

The security depends on a key that A and B keep **secret**, and both use the **same key**. That's why it's called **symmetric**.

`encrypt(plaintext, key) → ciphertext` and `decrypt(ciphertext, key) → plaintext`

### The Caesar cipher (a rotational cipher)

- Plaintext `A`, key `1` → `B`. `B` + 1 → `C`. `Z` wraps around to `A`. Julius Caesar reportedly used this.
- Key `13`: `A → N`. This is **ROT13**, long used online to hide **movie spoilers**. It scrambles text but isn't meant to be secure.
- Key `26` gives back the plaintext unchanged. The internet joke: "ROT26 is twice as secure as ROT13."
- **Decryption** reverses the process: subtract the key (`B` with key `1` → `A`).
- **Why it's insecure:** there are only 25 useful keys. Pen and paper can brute-force them, and Python can do it instantly.

In the lecture, Malan put an all-caps ciphertext on screen, encrypted with an unknown rotation, as a puzzle. The plaintext is the famous decoder-pin message from *A Christmas Story*. Try decoding it yourself from the slides. People who break ciphers like this practice **cryptanalysis**, which is a real job, particularly in government.

### Real symmetric algorithms

**AES** and **Triple DES (3DES)** are widely vetted and commonly used. Their math is much more complex, and their keys are huge, so trying every key is hopeless.

> 📌 3DES has been deprecated by NIST (disallowed for new encryption after 2023). Use **AES** (or ChaCha20).

> **Q:** If an attacker learns which hash function a company uses, can they find a reverse function?
> **A:** Not for modern, vetted functions. Mathematicians have scrutinized them. What *is* possible is guessing easy passwords and finding an input that matches a hash. Companies **shouldn't** hide which algorithm they use. Using public standards is reassuring. The **key** is what must stay secret.

> **Q:** Wouldn't it be easier to break into the server and study its hashing code?
> **A:** Possible, but you shouldn't rely on hiding the algorithm. Trust the math. The search space for modern hashes and keys is so large that we'd all be long dead before brute force succeeded. Security comes down to **probabilities**, and a weak password like `00000000` still defeats it.

> **Q:** How does a cipher work with words instead of numbers?
> **A:** Keys usually aren't words. They're random numbers generated by the computer. Text can always be converted to numbers anyway (ASCII/Unicode: `A` = 65, `B` = 66, …) and then to bits.

### The chicken-and-egg problem

Symmetric crypto assumes the two sides **already share a secret**. You don't know anyone at amazon.com or gmail.com, yet you want an encrypted connection (the S in HTTPS). The only way to share a key securely is over a secure channel, and you need the key to create one. That's a deadlock.

## 8. Public-key (asymmetric) cryptography

The algorithms named here are **Diffie-Hellman, MQV, and RSA**, with RSA the best known.

- Everyone has **two keys**, both very large numbers that are **mathematically related**. Your device generates them for you. Unlike passwords, you don't choose them.
- **Public key**: publish it anywhere (email signature, website, social media).
- **Private key**: never share it. Keep it on your device.
- **The key property:** a message encrypted with your **public key** can be decrypted **only with your private key**.

`encrypt(plaintext, recipient_public_key) → ciphertext` and `decrypt(ciphertext, recipient_private_key) → plaintext`

The asymmetry: one key encrypts and a *different* key decrypts.

### RSA in a nutshell

1. Pick a very large prime `p` and another very large prime `q`.
2. Compute `n = p × q`. Security rests on the fact that recovering `p` and `q` from `n` (**factoring**) is extremely hard.
3. Further math derives a public exponent `e` and a private exponent `d`.
4. **Encrypt**: `c = mᵉ mod n`. **Decrypt**: `m = cᵈ mod n`.

`mod` means "take the remainder after division", so this is called **modular arithmetic**. Malan stresses this is a big oversimplification, and it was the scariest formula of the course.

> 📌 The lecture says browsers "probably use some variant of RSA underneath the hood." Today's TLS 1.3 uses **(EC)Diffie-Hellman** for key exchange, and RSA appears mainly in **certificate signatures**. Elliptic-curve algorithms (ECDSA, Ed25519, X25519) are increasingly common.

## 9. Key exchange: Diffie-Hellman

Goal: A and B end up with the **same shared secret**, and anyone watching their messages can't work it out.

1. Agree publicly on a **generator** `g` (it can be as small as 2) and a large **prime** `p`.
2. Alice picks a private `a` and sends `A = gᵃ mod p`.
3. Bob picks a private `b` and sends `B = gᵇ mod p`.
4. Alice computes `Bᵃ mod p`, and Bob computes `Aᵇ mod p`. Both get `s = g^(ab) mod p`.

The full secret never crosses the network. Each side sent only "part" of it and kept `a` or `b` private. They can then use `s` as the key for a **symmetric** cipher like AES. Try [`demos/03_diffie_hellman.py`](../demos/03_diffie_hellman.py).

This level of sophistication is exactly why you should use vetted standards instead of inventing your own "cryptosystem".

## 10. Digital signatures

The same key pair can prove **who** signed a document and that it **wasn't changed**. Algorithms: **DSA, ECDSA, RSA**.

**Signing**

1. Hash the message (a letter, a contract, anything of any length) to get a short, fixed-size value. Hashing keeps the math fast.
2. Feed your **private key** and the hash into the signature algorithm → **signature** (a big number or string).
3. Send the message **and** the signature. The message itself is public, and what matters is who signed it.

This is the **reverse** of public-key encryption. There, others use *your public key* and you use *your private key* to decrypt. Here, *you* use your private key and *others* use your public key.

**Verifying**

1. The recipient hashes the received message with the same public hash function.
2. The recipient uses the signer's **public key** on the signature, which "decrypts" it back to a hash.
3. If the two hashes match, only the holder of that private key could have signed it, and the message is unchanged. Often a trusted third party vouches that "this is David Malan's public key".

Unlike an ink signature, which can be photographed, copied, or traced, a digital signature is only as forgeable as your private key is exposed. In that sense it is "objectively better".

> 📌 The lecture describes verification as "decrypting" the signature. That picture fits textbook RSA. Algorithms such as ECDSA and Ed25519 have a separate *verify* operation, so "verify with the public key" is the more general way to say it.

> **Q:** Are key pairs tied to your IP address?
> **A:** No. They're stored in a **registry**: a trusted third party that says "this is Vlad's key, this is David's key", with trust passed along from there. Or trust can be **distributed**: you post your public key in your email footer, on your website or LinkedIn, and people trust it as much as they trust those channels.

> **Q:** So hashing is a function, and encryption is a function plus a key, like Caesar?
> **A:** Yes. Think of hashing as **one-way**: it discards information, so even with unlimited effort you can't tell `apple` from `avocado`. Encryption is **two-way**, "reversible hashing" so to speak. It would be useless if it lost information. The key lets you reverse it while others can't.

> **Q:** Can signatures be spoofed?
> **A:** Not if the algorithm is sound and your private key hasn't been stolen. The probability is negligible.

## 11. Passkeys (WebAuthn)

Passkeys are the practical version of **WebAuthn** (web authentication) and move us toward **passwordless** accounts: nothing to invent, memorize, or store in a password manager. There are only two ways to use a key pair (encrypt with one, decrypt with the other, in either direction), and passkeys use the signature direction.

**Registration**

1. The site offers "create a passkey". Your device asks for a factor (**fingerprint, face, or PIN**) to confirm you're allowed to use the device.
2. Your device generates a **new key pair just for this site**.
3. It sends the site your **public key** and user ID, **no password**. The private key stays in your browser, device, or software.

**Login**

1. The site sends a **challenge**: random data it wants you to sign.
2. Your device signs it with the **private key** and sends back the **signature**.
3. The site verifies it with the stored **public key**. If it gets back the same challenge, it's really you.

Implications:

- There are no passwords to remember.
- You need to keep the registering device(s), or use a cloud service (Apple, Google, Microsoft) that **syncs passkeys** across devices. Syncing can be done without the provider learning your keys, if they use end-to-end encryption (next section).
- Passkeys can even be shared with other people.
- Adoption is still spreading. If a site offers sign-up with your fingerprint, face, or PIN and never asks for a password, it's probably using passkeys.

## 12. Encryption in transit

**Encryption in transit** means no machine in the middle can read your data on its way from A to B.

The classic picture: Alice talks to Bob, and **Eve** (the eavesdropper) sits in between. That could be someone on the wire or wireless link, **or the service itself**, such as Gmail, Outlook, or Zoom.

- Alice has an encrypted connection *to Gmail*, and Bob has one *to Gmail*. That **doesn't** mean Alice has a secure connection *to Bob*. Security isn't transitive.
- Gmail, as "Eve", could technically read the email. Policies and restricted access hopefully prevent that, but nothing technical does.
- Same with **Zoom**: encrypted to Zoom doesn't mean hidden from Zoom.
- Encryption in transit still keeps random outsiders out. It doesn't keep out the company in the middle.

**End-to-end encryption (E2EE)**: data is encrypted all the way from Alice to Bob. Any number of servers or companies in between see only **ciphertext**.

- It isn't always in a company's interest, since some mine your data (for example, for ads).
- **iMessage** and **WhatsApp** are known for E2EE. If implemented correctly, WhatsApp employees can't read messages even though they pass through WhatsApp's servers.
- The service has to offer E2EE, so choose services that do.

## 13. Deleting files

Storage (hard drives, **SSDs** with no moving parts, USB sticks) is just a lot of 0s and 1s.

- Dragging a file to the **Recycle Bin / Trash** doesn't delete it.
- **Emptying** the bin doesn't really delete it either. The OS keeps a table (file name/location → which bits hold it), and deleting just **forgets** the entry and marks the space as **free**.
- Later files **gradually overwrite** some of those bits, but pieces of your sensitive document or photo can remain for a long time.

**Secure deletion** overwrites the file's bits with **all 0s, all 1s, or random bits**. Physically removing the bits would also work in theory, but it shrinks your storage, so overwriting is the practical method.

## 14. Full-disk encryption (encryption at rest)

- **Encryption at rest**: data sitting on your device is encrypted. **Full-disk encryption** is one form of it.
- It's decrypted automatically, and quickly on modern hardware, only when you log in with your password, fingerprint, or face. When the lid is closed, the power is off, or you're logged out, the disk looks like **random bits**.
- **Stolen laptop** (say, from a café table): the thief can wipe or sell it but **can't read your data** without your password or biometrics.
- **Selling or donating** a device: with FDE and a strong password, your data is effectively **already securely deleted**.
- **Why start using it on day one:** flash storage wears out, and the drive's **firmware** may retire failing bits and **refuse to overwrite them**. Secure deletion can then silently fail. If the data was always encrypted, those leftovers are unreadable anyway.
- **Tradeoff:** forget your password, or have your biometrics change enough, and you're locked out of your own data.

### The dark side: ransomware

Attackers who get into a laptop, a corporate network, a **hospital**, or a **city** government increasingly don't just send spam or mine cryptocurrency. They **encrypt all the data** and demand a ransom (often in bitcoin) for the key. There's no guarantee you'll get a working key even if you pay. This is a growing concern for cities, companies, and universities.

## 15. Quantum computing

- A classical **bit** is either 0 or 1. A **qubit** can represent 0 **and** 1 at the same time. 2 qubits → 4 states, 3 → 8, 32 → about 4 billion.
- Much of security relies on attacks taking enormous time and resources. If adversaries get exponentially more computing power **before we do**, today's cryptography could become insecure, so the math needs to be hardened.

> 📌 "Tries all possibilities at once" is a popular simplification. The real threats come from specific algorithms. **Shor's algorithm** would break **RSA, Diffie-Hellman, and ECC**. **Grover's algorithm** only halves symmetric key strength, so AES-256 stays safe. "Harvest now, decrypt later" makes this urgent. NIST finalized **post-quantum** standards in 2024: **ML-KEM** (FIPS 203) for key exchange, and **ML-DSA** (FIPS 204) and **SLH-DSA** (FIPS 205) for signatures. Browsers and messengers already deploy hybrid post-quantum key exchange.

---

## Summary table

| Building block | Keys | Reversible? | Used for |
|---|---|---|---|
| Hash (SHA-2/3) | none | no | integrity, fingerprints, signatures |
| Password hash (Argon2id, bcrypt, scrypt) | none (+ salt) | no | storing passwords |
| Symmetric cipher (AES) | 1 shared secret | yes | bulk encryption |
| Asymmetric encryption (RSA) | public + private | yes | encrypting to someone you've never met |
| Key exchange (Diffie-Hellman) | private values + public g, p | n/a | agreeing on a shared symmetric key |
| Digital signature (RSA, ECDSA, DSA) | sign: private, verify: public | n/a | authenticity + integrity, passkeys |

## Review questions

<details><summary>1. Walk through what a server stores at registration and what it does at login when passwords are hashed.</summary>

At registration it stores `username : hash(salt, password)`, with the salt kept alongside, and discards the password. At login it reads the stored salt, hashes the typed password with the same salt and function, and compares the result to the stored hash.
</details>

<details><summary>2. Why is a toy hash like "first letter → number" bad, in two ways?</summary>

It collides constantly (apple and avocado → 1), and it leaks information (a hash of 1 means the password starts with A).
</details>

<details><summary>3. What's a rainbow table, and what defeats it?</summary>

A precomputed `password → hash` table that turns cracking into a lookup. Unique random salts defeat it, because the attacker would need a separate table for every salt.
</details>

<details><summary>4. Why do we salt passwords, and does the salt need to be secret?</summary>

So identical passwords produce different hashes, which hides password reuse between users and breaks precomputation. The salt isn't secret. It's stored with the hash (in the lecture's scheme, as its first two characters).
</details>

<details><summary>5. A site emails you your current password after "Forgot password?". What does that tell you?</summary>

It stores passwords in plaintext or reversibly, not as one-way hashes. A breach would expose your password. Stop using the site and make sure that password isn't used anywhere else.
</details>

<details><summary>6. Why are hash functions necessarily non-reversible, and what's a side effect?</summary>

Infinitely many possible inputs map to finitely many fixed-length outputs, so information is lost and collisions must exist. Side effect: in theory, another password with the same hash would also work, but with long hashes that's practically impossible to find.
</details>

<details><summary>7. What's the "chicken-and-egg" problem with symmetric encryption, and how is it solved?</summary>

Both parties need a shared key, but sharing it securely requires an already-secure channel. It's solved by asymmetric crypto: encrypt to someone's public key, or run Diffie-Hellman key exchange to derive a shared key, then switch to fast symmetric encryption.
</details>

<details><summary>8. Encrypting vs. signing: which key does what?</summary>

To encrypt for Bob, use Bob's public key, and Bob decrypts with his private key. To sign as Alice, use Alice's private key, and anyone verifies with Alice's public key.
</details>

<details><summary>9. How does a passkey login work, and why is there nothing useful for an attacker to steal from the server?</summary>

The site sends a random challenge, your device signs it with the site-specific private key, and the site verifies with the stored public key. The server holds only public keys, which can't be used to log in.
</details>

<details><summary>10. You and a friend both use Gmail over HTTPS. Is your email end-to-end encrypted?</summary>

No. It's encrypted in transit between each of you and Gmail, but Gmail itself can read it. Security isn't transitive. E2EE (like iMessage or WhatsApp) means only the endpoints hold the keys.
</details>

<details><summary>11. Why enable full-disk encryption when you first get a device instead of relying on secure deletion later?</summary>

Worn-out flash cells may be retired by firmware and never overwritten, so secure deletion can silently miss data. If everything was encrypted from the start, those leftovers are unreadable. FDE also protects a stolen device and makes resale safe.
</details>
