# Lecture 3: Securing Software

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/3/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/3/)

## TL;DR

- **Never trust user input.** Almost every bug in this lecture happens because input was treated as *code* instead of *data*.
- **XSS**: escape output for its context and add a **Content-Security-Policy**.
- **SQL injection**: use **parameterized queries (prepared statements)**, never string formatting.
- **Command injection**: avoid the shell. Pass arguments as a list and never `eval` user input.
- **Client-side validation is for UX only.** Always validate on the **server**.
- **CSRF**: GET requests must not change state. Use CSRF tokens and `SameSite` cookies.
- The supply chain matters too: signed code, app stores, package managers, and tracking vulnerabilities with **CVE / CVSS / EPSS / KEV**.

## Core concepts

### Phishing with HTML

The text a user sees in a link can differ from where it goes:

```html
<a href="https://yale.edu">https://harvard.edu</a>
```

This shows `https://harvard.edu` but opens `yale.edu`. Hover to check the real target, or better, type important URLs yourself. Attackers also clone login pages on lookalike domains such as `harvard-login.co` or `hаrvard.edu` (with a Cyrillic "а").

### Cross-site scripting (XSS)

**XSS** happens when a site includes attacker input in a page without neutralizing it, so the victim's browser **runs the attacker's script** with the site's privileges. The script can read cookies, act as the user, or rewrite the page.

```html
<script>alert('attack')</script>
```

| Variant | Where the payload lives |
|---|---|
| **Reflected** | In the request (usually a URL parameter), echoed back right away. The victim is tricked into clicking a crafted link such as `https://site/search?q=%3Cscript%3E...` |
| **Stored** | Saved on the server (a comment, profile, or email) and served to *every* viewer, so it spreads further |
| **DOM-based** | Client-side JavaScript writes untrusted data into the page (`innerHTML = location.hash`). The server never sees the payload |

#### Defense 1: escape output (character escapes)

Convert characters that have meaning in HTML into entities so they display as text:

| Char | Entity |
|---|---|
| `<` | `&lt;` |
| `>` | `&gt;` |
| `&` | `&amp;` |
| `"` | `&quot;` |
| `'` | `&#39;` / `&apos;` |

```html
<p>About 6,420,000,000 &lt;script&gt;alert('attack')&lt;/script&gt;</p>
```

Escaping depends on **context**. HTML body, HTML attributes, JavaScript strings, and URLs each need different encoding. Use your framework's auto-escaping templates (React, Jinja2, and similar) instead of doing it by hand. Try [`demos/05_xss_escaping.py`](../demos/05_xss_escaping.py).

#### Defense 2: Content-Security-Policy (CSP) header

An HTTP response header that tells the browser which sources it may load and run content from:

```http
Content-Security-Policy: script-src https://example.com/
Content-Security-Policy: style-src https://example.com/
```

With `script-src` set this way, the browser runs only scripts loaded from that origin. **Inline `<script>` blocks are blocked** unless the policy explicitly allows them with nonces, hashes, or `'unsafe-inline'`. CSP is **defense in depth**: it limits the damage if escaping fails somewhere.

Related: mark session cookies **`HttpOnly`** so JavaScript can't read them, even through XSS.

### SQL injection

When user input is pasted into a SQL string, it can change the query's structure.

```sql
SELECT * FROM users WHERE username = '{username}'
```

**Input:** `malan'; DELETE FROM users; --`

```sql
SELECT * FROM users WHERE username = 'malan'; DELETE FROM users; --'
```

That deletes every user. `--` comments out the rest of the line.

**Authentication bypass**, input into the password field: `' OR '1'='1`

```sql
SELECT * FROM users
WHERE (username = 'malan' AND password = '') OR '1'='1'
```

`'1'='1'` is always true, so the query returns every row and the login succeeds.

#### Defense: prepared statements / parameterized queries

```sql
SELECT * FROM users WHERE username = ?
```

```python
db.execute("SELECT * FROM users WHERE username = ?", (username,))
```

> 📌 The lecture explains prepared statements as "replacing `'` with `''`" (escaping). In real database drivers, the query **structure is sent and parsed separately from the values**, so input is always data and never becomes SQL. Parameterization is the fix. Don't rely on hand-escaping. Also run the app with a **least-privilege** database account. See [`demos/04_sql_injection.py`](../demos/04_sql_injection.py).

### Command injection

User input reaches a system shell, and the attacker adds their own commands with `;`, `&&`, `|`, or `$( )`.

- Dangerous functions: `system()`, `os.system`, `subprocess(..., shell=True)`, `eval`, `exec`, backticks.
- Defense: don't use a shell. Pass arguments as a **list** (`subprocess.run(["ls", filename])`), use library APIs instead of shelling out, allowlist expected values, and **never `eval` user input**.
- The lecture's advice: **read the documentation** on how to escape input for each function you use.

See [`demos/06_command_injection.py`](../demos/06_command_injection.py).

### Client-side vs. server-side validation

The user fully controls anything that runs in their browser. With **developer tools** they can remove attributes like `disabled`, `required`, `maxlength`, or `type="email"`, or skip the page entirely and send requests with `curl`.

```html
<input disabled type="checkbox">  <!-- the user can delete "disabled" -->
<input required type="text">      <!-- the user can delete "required" -->
```

- **Client-side validation** gives users quick feedback. It is a UX feature, not a security control.
- **Server-side validation** is the only real enforcement. Check type, length, range, format, and **authorization** ("is this user allowed to do this?") on every request.

### Cross-site request forgery (CSRF)

Your browser **automatically attaches your cookies** to requests for a site, even when another site starts the request. An attacker's page can make your browser send a request you never meant to send.

**GET-based.** Loading an "image" fires a state-changing request:

```html
<img src="https://www.amazon.com/dp/B07XLQ2FSK">
```

**POST-based.** A hidden form on the attacker's site submits itself automatically:

```html
<form action="https://www.amazon.com/" method="post">
  <input name="dp" type="hidden" value="B07XLQ2FSK">
  <button type="submit">Buy Now</button>
</form>
<script>document.forms[0].submit();</script>
```

**Defenses**

1. **GET must be safe.** It should never change state (purchases, deletes, transfers).
2. **CSRF token**: an unpredictable per-session value sent in a hidden form field or custom header. The server rejects requests without the correct token, and the attacker's site can't read it.
3. **`SameSite` cookies** (`Lax` or `Strict`) stop the browser from sending cookies on cross-site requests. Modern browsers default to `Lax`.

XSS vs. CSRF: XSS runs the attacker's code *on* the target site. CSRF makes the victim's browser send a request *to* the target site from somewhere else.

### Arbitrary code execution (ACE)

**ACE** means an attacker can make a program run code it was never meant to run. It is usually the worst outcome a bug can have.

- **Buffer overflow**: a program writes more input than a fixed-size buffer holds, so it overwrites nearby memory. This is common in C/C++.
- **Stack-based overflow**: the overflow overwrites the function's **return address** on the stack, so the program jumps to attacker-chosen code. (The lecture calls this "stack overflow". That term usually means running out of stack from deep recursion, which is a different bug.)
- Mitigations: memory-safe languages (Rust, Go, Java, Python), bounds checking, stack canaries, ASLR, and non-executable memory (DEP/NX).
- The same techniques are used for **cracking** (bypassing license checks) and **reverse engineering**.

### Trusting the software you install

| Model | Security story |
|---|---|
| **Open source** | Anyone can audit the code ("many eyes"), but popular projects can still go years without review (Heartbleed, xz-utils backdoor) |
| **Closed source** | Hidden code is harder to study, but that's security through obscurity. Bugs still get found by reverse engineering |
| **App stores** | Google and Apple review submissions and require **developer code signing**. The store signs the app too, and the OS installs only signed software |
| **Package managers** (npm, pip, apt) | Signed packages and checksums, but open publishing allows **typosquatting**, maintainer account takeover, and malicious updates. Pin versions and use lockfiles |

**Bug bounties** pay researchers to *report* vulnerabilities instead of selling or exploiting them. Examples are HackerOne, Bugcrowd, and vendor programs.

### Tracking vulnerabilities

| Acronym | Meaning |
|---|---|
| **CVE** (Common Vulnerabilities and Exposures) | A unique ID for each publicly known vulnerability, e.g. `CVE-2021-44228` (Log4Shell) |
| **CVSS** (Common Vulnerability Scoring System) | A **severity** score from 0 to 10 based on impact and exploitability |
| **EPSS** (Exploit Prediction Scoring System) | The **probability** that a CVE will be exploited in the wild in the next 30 days |
| **KEV** (CISA Known Exploited Vulnerabilities catalog) | CVEs **confirmed exploited** in the wild. Patch these first |

How to prioritize: KEV first, then high EPSS, then high CVSS. A high-severity bug nobody exploits can be less urgent than a medium bug under active attack.

## Review questions

<details><summary>1. What root cause do XSS, SQL injection, and command injection share?</summary>

Untrusted input is mixed into something that gets interpreted (HTML/JS, SQL, a shell), so data becomes code. The fix is to keep code and data separate: context-aware escaping, parameterized queries, and argument lists.
</details>

<details><summary>2. Reflected vs. stored XSS?</summary>

Reflected XSS is echoed back from the current request, so the victim must open a crafted link. Stored XSS is saved on the server and hits everyone who views that content.
</details>

<details><summary>3. Why isn't a `required` attribute or a JavaScript check enough?</summary>

The user controls the client. They can edit the HTML in dev tools or skip the browser and send raw HTTP requests. Only server-side checks are enforceable.
</details>

<details><summary>4. How does a CSRF token stop the auto-submitting form?</summary>

The attacker's page can make the browser send cookies, but the same-origin policy stops it from reading the token embedded in the real site's pages. Its forged request has no valid token, so the server rejects it.
</details>

<details><summary>5. You have 200 open CVEs. What do you patch first?</summary>

Anything in CISA's KEV catalog, since it is known to be exploited, then CVEs with high EPSS, then by CVSS severity and how exposed the asset is.
</details>
