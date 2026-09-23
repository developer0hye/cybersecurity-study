# Lecture 0: Securing Accounts

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/0/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/0/)

## TL;DR

- Security is always a **tradeoff with usability**. The goal is to raise the attacker's cost (time, money, effort, risk) until the attack is not worth it.
- Length adds more strength to a password than complexity does. What matters most is to **never reuse passwords**.
- **Rate limiting** (lockouts after failed attempts) slows attackers down by orders of magnitude.
- Add a second factor. From weakest to strongest: SMS OTP < authenticator-app OTP < hardware key / passkey.
- Most real account takeovers come from people (social engineering, phishing) and leaked passwords (credential stuffing), not from clever math.
- Use a **password manager** (with one excellent primary password), use **SSO** where it makes sense, and move to **passkeys** as sites support them.

---

## 1. What "security" means: a physical analogy

A house key lets you through a locked door and into the entire home. Anyone else who gets that key gets the same access. Digital accounts work the same way, and the building blocks are:

| Concept | Question | Physical analogy |
|---|---|---|
| **Authentication** (AuthN) | *Who are you?* Prove that you are David. | Having a key that fits the lock |
| **Authorization** (AuthZ) | *What are you allowed to access?* | Being David doesn't mean you may enter *my* home, or maybe only the entryway |

> ⚠️ The lecture video defines both terms correctly. The **written official notes** say "Authorization is the act of verifying that you are … the person who should have access." That describes **authentication**.

In the digital world, the "key" is usually a **username plus a password**:

- The **username** (often an email address) identifies you and **can be public**.
- The **password** is the secret. The assumption is that only you know *both*, so typing both proves it's you.
- Having a password isn't enough. You need a **good** one.

## 2. Attacks on passwords

- **Dictionary attack**: instead of typing randomly, the attacker tries actual words from a file of English (or other-language) words, one at a time. A real word as a password falls quickly.
- **Brute-force attack**: software tries **every possible** password, the digital version of a battering ram against a castle gate. Even random letters, digits, and symbols can be brute-forced if the password is **short**.

## 3. Measuring password strength: live demo

### 4-digit passcode

Many phones still default to a **4-digit passcode**. Asked how many there are, the audience guessed 1,000, 9,999, and 10,000. The answer is **10,000** (0000 through 9999, counting 0000):

```
10 × 10 × 10 × 10 = 10⁴ = 10,000
```

Guesses for how long cracking would take ranged from milliseconds to a day. To find out, Malan wrote `crack.py` in **VS Code** (Python). "Crack" is the term of art for figuring out a password.

```python
from string import digits

for i in digits:
    for j in digits:
        for k in digits:
            for l in digits:
                print(i, j, k, l)
```

He noted that the nested loops aren't elegant code, but they make the idea clear: try every first digit, every second digit, and so on. The scenario is that someone swipes your phone from a café table, plugs it into a laptop over USB/Lightning, and feeds it every code. Running `python crack.py` printed all 10,000 combinations in **milliseconds**. A 4-digit PIN protected only by math is basically no protection.

### 4 letters (upper + lower case)

```
52 × 52 × 52 × 52 = 52⁴ ≈ 7.3 million
```

(An audience member said 26⁴, but upper *and* lower case makes 52 per position.) The code switched to `ascii_letters`:

```python
from string import ascii_letters

for i in ascii_letters:
    for j in ascii_letters:
        for k in ascii_letters:
            for l in ascii_letters:
                print(i, j, k, l)
```

This time Malan had time to walk over to the screen and watch lowercase, then uppercase, scroll by. It finished at `ZZZZ` in **a few seconds**. It was slower, but not by much.

### 4 characters: letters + digits + punctuation

A US English keyboard has **94** printable characters: 26 lowercase + 26 uppercase + 10 digits + 32 punctuation.

```
94⁴ ≈ 78 million  (about 10× more than 52⁴)
```

```python
from string import ascii_letters, digits, punctuation

for i in ascii_letters + digits + punctuation:
    for j in ascii_letters + digits + punctuation:
        for k in ascii_letters + digits + punctuation:
            for l in ascii_letters + digits + punctuation:
                print(i, j, k, l)
```

This run was noticeably slower, and the scrolling output "looks like a Hollywood movie". Malan pointed out that movies show hackers getting the 3rd character, then the 1st, then the 4th, "just in time". **Real brute force isn't like that.** It works through the possibilities methodically, and it can't tell when a single character is right. He didn't wait for it to finish, but estimated about a minute.

### 8 characters from 94 symbols

```
94⁸ ≈ 6.1 × 10¹⁵ ≈ 6 quadrillion
```

Now an attacker would likely run out of time, energy, money, or lifetime before trying them all, provided your password is actually random within that space and not `00000000`.

### Takeaways

- Security is a **game of relativity and resources**. Adding length and character types doesn't change the approach. It raises the bar. By the time the attacker gets in, you may have changed the password or stopped using the account.
- The catch: longer, more complex passwords are **harder to remember and type**. Where to draw the **usability vs. security** line is partly personal and partly company policy.

Length beats character variety, because each extra character multiplies the work by the charset size. Try [`demos/01_keyspace.py`](../demos/01_keyspace.py), which also estimates crack times.

> **Q:** Why aren't USB fingerprint readers used more?
> **A:** Cost. An extra device per person is expensive for consumers and for companies with many employees. **Passkeys** (end of lecture) get the same benefit from a device you already own: a phone with a fingerprint or face sensor.

> **Q:** If 4-digit codes are so weak, why do programs still use them?
> **A:** The usability tradeoff: if logging in is too hard, users forget passwords and stop using the product. Some designers are also just unaware of the risk. Industry is slowly nudging toward better defaults.

## 4. NIST recommendations

**NIST** (National Institute of Standards and Technology, US) publishes password guidance in **SP 800-63B**. These points come from the version the lecture quotes. In NIST's terms, a **verifier** is the website or app that checks your password, and a **memorized secret** is your password.

1. **"Memorized secrets shall be at least eight characters in length."** This matches the demo: things only got really slow around 94⁸.
2. **Allow long passwords, at least 64 characters, with all printing ASCII characters, spaces, and Unicode (emoji, accented letters).** A long, memorable **passphrase** (a sentence or quote) can beat a short password full of symbols, and it survives dictionary and brute-force attacks as long as it's original. Malan complained about a site that had just made him jump through hoops of uppercase/lowercase/punctuation rules and allowed only certain symbols. That's a lot of friction for questionable security.
3. **Compare new passwords against a list of commonly used, expected, or compromised values**, including:
   - passwords from **previous breach corpuses** (leaked databases posted online, effectively a ready-made dictionary for attackers, who try it before brute force)
   - **dictionary words**
   - **repetitive or sequential characters** (`aaaaaa`, `1234abcd`, `0000`)
   - **context-specific words** such as the service name or username (`gmailpassword`, `amazonpassword`). *If you can think of a clever trick, so can an attacker.*
4. **No password hints** available to unauthenticated users, and **no prompts for specific personal information** ("What was the name of your first pet?"). Many sites still violate this. Hints leak information ("it's my first pet's name"), and social media and LinkedIn make such facts easy to find.
5. **Do not require arbitrary or periodic password changes.**
   > **Q (Malan to the audience):** Why not force changes every few months?
   > **A (audience + Malan):** People put in minimal effort: `password1` → `password2` → `password3`. If an old password leaks, the new one is easy to guess. People also forget frequently changed passwords.
6. **Rate-limit failed authentication attempts.** Enter the wrong phone passcode ~10 times and the phone locks you out. After 10 misses, it's more likely a thief than you. The lockout grows (1 minute, then 2, 5, 10…), and the phone may even **wipe itself** if that setting is on. An attacker who could try 10,000 codes in under a second now needs hours or days, which makes the attack **more expensive and riskier** (the owner may come back to the table). Ideally the attacker gives up and moves on.

> 📌 **Update:** The final **SP 800-63B Revision 4** (August 2025) raised the minimum to **15 characters when a password is the only factor**, keeps **8** as the minimum when it is part of MFA, and says verifiers **shall not** impose composition rules such as "must include a symbol". Check the current revision when you write a policy.

## 5. Two-factor / multi-factor authentication (2FA / MFA)

On top of one factor (your password), you need a second factor or more. The factors must be **fundamentally different kinds**:

| Factor | Meaning | Examples |
|---|---|---|
| **Knowledge** | Something only you know | Password, PIN |
| **Possession** | Something only you physically have | Key fob, your phone (SMS or app code), hardware key |
| **Inherence** | Something you are (biometrics) | Fingerprint, face |

Why possession helps: **millions of people on the internet** could find or guess your password, but only people **physically near you** (the others in the coffee shop) could steal your phone or fob. That shrinks the threat enormously.

> Some sites say "**two-step** verification". That can mean just two passwords. Strictly, **two-factor** means two *different types* of factor.

## 6. One-time passwords (OTP)

The code from a possession factor is a **one-time password**. It is used once, not memorized and reused.

- **Key fobs**: a small device showing a code that changes every few seconds, **synchronized with a server**. If your typed code matches the server's current code, you're in. Some plug in over USB, so there's nothing to type.
- **Authenticator apps** (Google's and others') keep all your rotating OTPs in one place.
- **SMS codes** (usually 6 digits) are common but the **least secure** option because of **SIM swapping**:
  - Your carrier links your phone number to your SIM's unique identifier, whether it's a physical card or an eSIM.
  - An attacker calls your carrier, pretends to be you using personal details, and convinces them to move your number to the attacker's SIM.
  - Your text messages, including OTPs, now go to the attacker.
- **Prefer** a native app (push notification or app-generated code over your data connection) or a physical key over SMS.

> 📌 TOTP codes from any source can still be **phished in real time** (see §10). Phishing-resistant options are FIDO2/WebAuthn hardware keys and passkeys.

## 7. Keylogging

**Malware** (malicious software, from an untrusted install or a virus/worm infection) can include a **keylogger** that records everything you type or tap and often **uploads it** to the attacker's server.

- Your username isn't a big deal, since it's often public. Your **password** is.
- A fast, sophisticated attacker could even capture your **OTP** and use it on their own machine before you press Enter.
- **Defense:** be careful about which computers you use. Malan rarely if ever logs in on internet café machines, campus lab computers, or even friends' computers, because he can't know how well they're maintained. Log in only on **your own devices**.
- The real-time OTP relay is sophisticated and less likely, but it's a real threat if you're personally **targeted**.

> **Q:** Should I let Google or Apple remember my passwords?
> **A:** Short answer: yes. See password managers (§12).

## 8. Credential stuffing

A **credential** is a username + password. **Credential stuffing** means taking lists of known credentials, leaked from a breached site, and **stuffing them into other sites** (Amazon, Gmail…), betting that you reused them. It needs no dictionary and no brute force.

- If you use the same password on 2, 3, or 30 sites, **you are vulnerable right now**. One breach anywhere exposes all of them.
- **Defense:** a **different password on every site and app**. Reusing a username or email is fine. Reusing a password is not.

## 9. Social engineering

This is an attack on **people**, not technology.

**Live demo:** Malan asked everyone to write one of their real passwords on a piece of paper. Some objected in the chat, but some heads went down and people started writing. Anyone who wrote one down was **just socially engineered**: they trusted an authority figure (a cybersecurity teacher, no less) and followed the instruction at face value.

- If *any* teacher, caller, or emailer asks for a password, **don't do it**.
- Be skeptical of requests for personal details (your first pet…). Ask yourself *why they need it* before you share anything.
- Remember the feeling of being duped, because it will matter one day. (And go shred that piece of paper.)

## 10. Phishing

**Phishing** is social engineering done through technology, "hooking" a victim. It usually arrives as an email that looks like it's from PayPal, Google, a politician, or a Harvard teacher, asking you to *click to donate / change your password / verify your information*.

- Attackers exploit your **trust** in familiar brands and your **comfort with familiar interfaces**. Copying a real site's look is often simple copy-paste.
- **Social media "phishing"**: posts like "comment your favorite childhood song!" can collect answers to **security questions** from thousands of people at once.
- **Fake login pages**: a page that looks exactly like Gmail's login.
  - Check the **URL bar** (gmail.com, google.com, or google.*country code*).
  - **Hover over links** and check the real destination, shown in a corner of the browser. The link text can differ from where it goes.
  - For anything sensitive (banking, medical, personal), **don't click the email link**. Open a new tab and type `paypal.com` yourself. It's less convenient (the usability/security tradeoff again) but safer.
- **2FA phishing**: a sophisticated fake Gmail page can also **ask for your 2FA code** and relay your username, password, and code to the real Gmail right away, then change your password. It's less common, but it shows why you shouldn't blindly trust screens that ask for credentials.

## 11. Machine-in-the-middle (MITM) attacks

It feels like it's just you and amazon.com, but your data passes through **many machines in between**: routers and servers owned by ISPs, universities, companies, or your own home network. If one of them is malicious, it could **store or read** your data unless you use proper defenses (cryptography, covered in Lecture 1). It's sophisticated and less common, but worth knowing about.

## 12. The root problem is us, and the defenses

People are bad at choosing passwords. Strict policies push us to do the minimum, and hundreds or thousands of accounts pile up over the years. The result: **sticky notes** on monitors, printouts in desk drawers, or a `passwords.txt` / Excel / CSV file on the desktop.

### Single sign-on (SSO)

"Log in with Google / Facebook / …" alongside the usual email + password form.

- **Benefits:** no new account and no new password to remember, which means less friction. The new site also **inherits** the good password and 2FA you (hopefully) already use on your important Google/Facebook account.
- **How it works:** you're **redirected to the real google.com/facebook.com** (check this!), you log in *there*, and your password is **never given to the third-party site**. Using cryptography, Google/Facebook sends back only a confirmation that you logged in successfully and your identity (e.g. your email address).
- It helps both users, who get convenience and security, and sites, which get easier sign-up and login.

### Password managers

Software that **stores** your passwords and **generates** new random ones at the click of a button, of any length and matching any site's rules. You don't memorize them and you don't write them down.

- **Autofill** logs you in with a keystroke, **only on the real domain**. It remembers the URL where each password was saved, so on a phishing lookalike it **refuses to fill**. That's built-in phishing protection.
- **The catch:** "all your eggs in one basket". Protect the manager with **one excellent primary password** (long, complex, even a little annoying to type). If you lose or forget it, you may lose access to everything.
- **Browser password saving** (the dots in the form) has existed for years, but the lecture points out it has often been tied to one browser, doesn't sync to other devices, and is hard to share with family. Dedicated managers add syncing, sharing, and generation.
  > 📌 **Update:** today the built-in managers in Chrome, Safari, Edge, and Firefox do sync across devices signed in to the same account, so the gap is smaller than the 2023 lecture suggests.
- **Built-in options** are recommended for less technical users: **Apple iCloud Keychain** (now also the Apple **Passwords** app), **Google Password Manager**, **Microsoft Credential Manager**. Third-party managers can add features useful for families and companies.
- **Advice:** if you aren't using one, start with your **most important accounts** (financial, medical, personal), turn on 2FA with an app or key instead of SMS, and migrate the rest **one account at a time** as you log in. Don't try to change 1,000 passwords in one night.

> **Q:** If password managers are so helpful, why do we still need antivirus?
> **A:** Malware does many bad things (encrypts or deletes data, sends spam) and could still keylog your password or 2FA code. You don't want any bad software on your machine, so keep raising the bar.

> **Q:** AI can clone voices. Could someone impersonate my boss, or me when calling my bank?
> **A:** Yes, with **deepfakes**. If an account (especially a bank) uses **voice recognition** ("my voice is my password", as in the movie *Sneakers*), **turn it off** and use app-based 2FA instead. Anyone with recordings of your voice could generate that phrase.

> **Q:** Doesn't one password manager defeat the purpose of having different passwords?
> **A:** It's a real tradeoff. If you currently use easy or reused passwords, a manager is a **net positive**. If you already use strong, unique passwords that aren't written down anywhere, it could be a net negative. Most people are in the first group. Decide for yourself, and "don't just believe something some guy on the internet told you."

### Passkeys

This is where things are heading, and it avoids the "forgot the primary password" problem:

- When you register on a site, **your device** (Mac, PC, or phone) generates the passkey. You don't remember anything.
- A passkey is **a pair of mathematically related values**: a **private** one that stays on your device and a **public** one that the site stores.
- On later visits, your device uses them to **authenticate you automatically**, usually after a fingerprint or face check.
- Passkeys are **synced across your devices**.
- Understanding them needs cryptography, which comes in [Lecture 1](01-securing-data.md#passkeys-webauthn--fido2).

## Summary

- Tradeoffs between security and usability/convenience are everywhere.
- Your **behavior and awareness** are what really protect you.
- NIST: long passwords allowed, breached and common passwords blocked, no hints or security questions, no forced rotation, rate limiting.
- 2FA/MFA with OTPs (app or key rather than SMS) greatly reduces risk.
- Common attacks: dictionary, brute force, keylogging, credential stuffing, social engineering, phishing, MITM.
- Defenses: unique passwords, password managers, SSO, and passkeys going forward.

## Review questions

<details><summary>1. What's the difference between authentication and authorization?</summary>

Authentication proves *who you are* (password, passkey). Authorization decides *what you may access* once you're known (the whole house vs. only the entryway).
</details>

<details><summary>2. How many 4-character passwords can you make from letters, digits, and punctuation on a US keyboard, and why?</summary>

94⁴ ≈ 78 million: 26 lowercase + 26 uppercase + 10 digits + 32 punctuation = 94 choices for each of 4 positions.
</details>

<details><summary>3. Why is a 16-character lowercase passphrase often stronger than an 8-character "complex" password?</summary>

26¹⁶ ≈ 4.4 × 10²² vs. 94⁸ ≈ 6.1 × 10¹⁵. Length grows the exponent, while complexity only grows the base. A passphrase is also easier to remember. It still must not be a well-known phrase, or it falls to a dictionary attack.
</details>

<details><summary>4. A phone uses a 4-digit PIN. What actually protects it, since 10,000 guesses take milliseconds?</summary>

Rate limiting: lockouts after ~10 wrong attempts, with growing delays and possibly a wipe. That turns milliseconds into hours or days and raises the thief's risk of getting caught.
</details>

<details><summary>5. Name the four kinds of passwords NIST says to reject.</summary>

Passwords from breach corpuses, dictionary words, repetitive/sequential characters (`aaaaaa`, `1234abcd`), and context-specific words (service name, username, and variations).
</details>

<details><summary>6. Why does NIST advise against forced periodic password changes and security questions?</summary>

Forced changes lead to predictable patterns (`password1` → `password2`) and forgotten passwords. Security question answers (first pet, favorite song) are often public or can be collected through social media "phishing" posts.
</details>

<details><summary>7. Why is SMS the weakest second factor?</summary>

SIM swapping: an attacker talks your carrier into moving your number to their SIM and then receives your codes. Like other OTPs, SMS codes can also be phished or keylogged in real time.
</details>

<details><summary>8. What single habit defeats credential stuffing?</summary>

Using a unique password for every site, which in practice means a password manager. A leak from one site then can't be replayed anywhere else.
</details>

<details><summary>9. How does a password manager protect you from phishing?</summary>

It remembers the domain where each password was saved and autofills only there. On a lookalike domain it won't fill, and that's a red flag.
</details>

<details><summary>10. With SSO ("Log in with Google"), does the third-party site see your Google password?</summary>

No. You're redirected to Google, you authenticate there, and Google sends the site only a cryptographically protected confirmation of who you are.
</details>
