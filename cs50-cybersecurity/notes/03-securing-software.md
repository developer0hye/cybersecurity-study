# Lecture 3: Securing Software

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/3/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/3/)

## TL;DR

- **Never trust user input.** Almost every bug in this lecture happens because input was treated as *code* instead of *data*.
- **Phishing** works because a link's visible text and its real destination (`href`) are independent.
- **XSS**: escape output (`&lt;`, `&gt;`, `&amp;`, `&quot;`, `&#39;`) and add a **Content-Security-Policy** header as a second layer.
- **SQL injection**: use **prepared statements (parameterized queries)**, never string formatting. Also run the app with a least-privilege database account.
- **Command injection**: be very careful with `system` and `eval`. Use the language's escaping or argument-list APIs.
- **Client-side validation is only for UX.** If you can have only one, choose **server-side validation**.
- **CSRF**: GET requests must be "safe" (no state changes). Protect state-changing requests with a random **CSRF token** that only the real server knows.
- **Buffer overflows** let attackers overwrite a function's return address and run their own code (**arbitrary / remote code execution**).
- Trusting software: open vs. closed source, app stores and package managers that use **digital signatures**, **bug bounties**, and tracking vulnerabilities with **CVE / CVSS / EPSS / KEV**.

The lecture covers two areas: web software (the first two-thirds) and software on your own devices (the last third).

## Part 1: Web software

### A minimal HTML primer

HTML (HyperText Markup Language) is the language web pages are written in. Browsers read **tags**:

```html
<p>...</p>              <!-- "Hey browser, here comes a paragraph" ... "that's it for the paragraph" -->
<script>...</script>    <!-- "here's some code (JavaScript) to execute" ... "that's it for the code" -->
<a href="...">...</a>   <!-- an anchor, i.e. a link -->
```

- An **open (start) tag** like `<p>` tells the browser to start doing something. The matching **close (end) tag** `</p>`, with a *forward* slash, tells it to stop.
- An **attribute** adds detail to a tag. `href` ("hyper-reference") on an anchor tag is the URL the link leads to.
- Some tags have no close tag, e.g. `<input>`, and some attributes need no value, e.g. `disabled`, `required`.

### Phishing with HTML

A link has **two independent parts**: the text the human sees, and the `href` value where the browser actually goes.

```html
<a href="https://harvard.edu">Harvard</a>              <!-- honest -->
<a href="https://harvard.edu">harvard.edu</a>          <!-- honest, shows the domain -->
<a href="https://harvard.edu">https://harvard.edu</a>  <!-- honest, URL typed twice on purpose -->
<a href="https://yale.edu">https://harvard.edu</a>     <!-- misleading -->
```

The last link *looks* like it goes to Harvard but opens Yale. On a laptop or desktop, **hovering** over a link shows the real destination, usually in the browser's bottom-left corner, before you click.

Sending someone to Yale is just a prank. The real attack works like this:

1. The adversary registers a lookalike domain, with one character slightly off from `harvard.edu`.
2. They copy all of Harvard's HTML to build a convincing fake site.
3. They send you a link whose visible text says `https://harvard.edu`.
4. You don't notice the subtle URL difference, so you type your username and password into the fake site. The adversary now has your credentials.

The same method works for your bank, PayPal, or any site where you could lose money or other assets. This is the implementation side of the phishing (social engineering) covered in Lecture 0.

> **Q: Could an attacker use a raw IP address instead of a domain?**
> A: Yes, e.g. `http://1.2.3.4/`. It would usually be HTTP rather than HTTPS, which should make you suspicious, but many people wouldn't notice. The **lesson for website owners**: use one or very few consistent domains, and never send users to a bare IP. Every inconsistency teaches users to accept odd URLs.

### Code injection and cross-site scripting (XSS)

**Code injection** is a category of attacks where an adversary gets your software to run code that *you* didn't write. **Cross-site scripting (XSS)** is the web version: the adversary gets a website to run their JavaScript in visitors' browsers.

#### The Google search example (hypothetical)

Imagine Google didn't know about this attack. Actually, it defends against it. When you search for `cats`, the results page shows your input in two places: in the search box and in a sentence like:

```html
<p>About 6,420,000,000 cats</p>
```

The word `cats` was written by *you*, not by Google. What if you search for this instead?

```html
<script>alert('attack')</script>
```

`alert(...)` is a built-in JavaScript function that pops up a message. If Google pastes your input into the page without changes, the browser receives:

```html
<p>About 6,420,000,000 <script>alert('attack')</script></p>
```

The browser can't tell that the `<script>` tag came from the user and not from Google. It reads: start a paragraph, write "About 6,420,000,000", then **run this script**, which shows a pop-up saying "attack". The word "cats" disappears from the sentence because the input became code instead of text.

Here, you're only "hacking yourself", so it's harmless. But it shows the site will run code it didn't write. The **correct** behavior is for the page to display the characters `<script>alert('attack')</script>` as text, without a pop-up.

#### Reflected attack

A **reflected** XSS attack sends the attacker's code to the server in the victim's own request and has the server **reflect** it back to the victim's browser.

Searching Google creates a URL. The shortest one that works is:

```
https://www.google.com/search?q=cats
```

Change `q=cats` to `q=dogs` and you've searched for dogs. The search box is just a convenient way to build this URL. So an attacker can build a link like this:

```html
<a href="https://www.google.com/search?q=%3Cscript%3Ealert%28%27attack%27%29%3C%2Fscript%3E">cats</a>
```

- The strange `%3C` / `%3E` sequences are **URL encoding** (percent-encoding) for characters such as `<` and `>`, which aren't safe to put in URLs as-is.
- After decoding, the server receives the script tag in `q`. If it echoes `q` into the page without escaping, the victim's browser runs the script.
- The victim thinks they're searching for "cats" on the real google.com, but they're running the attacker's code *on google.com*.

Instead of `alert('attack')`, the attacker could use `alert(document.cookie)`. JavaScript can read the site's cookies, at least those not hidden from JavaScript. A real attack wouldn't show them. It would **send `document.cookie` to the attacker's server**, along with the username or other personal information from the page. A stolen session cookie lets the attacker log in as the victim (session hijacking, Lecture 2).

> **Q: Can't I just block JavaScript in my browser?**
> A: Not realistically. Most websites depend on JavaScript to work at all. A better approach is to disable *some* JavaScript, meaning inline scripts, using a CSP header (below).

#### Stored attack

In a **stored** XSS attack, the server **saves** the malicious input and later shows it to other users.

Example (hypothetical): you send someone a Gmail message containing `<script>alert('attack')</script>`. Email is stored on the server until it's deleted. If Gmail saved the HTML and JavaScript without changes and displayed it when the recipient opened the message, the **recipient** would run the attacker's code. They'd be attacked just by opening their inbox. The correct behavior is for the recipient to *see* the code as text without running it.

A reflected attack needs the victim to click a crafted link. A stored attack affects everyone who views the stored content.

#### Defense 1: character escapes

The general solution is **escaping**: replace characters that could be misinterpreted, or that are dangerous, with harmless equivalents. In HTML, `<` could start a tag and `>` could end one, so they must not appear raw.

HTML defines standard **character entities** (escape sequences). The browser sees `&lt;` and *displays* `<` without treating it as the start of a tag.

```html
<p>About 6,420,000,000 &lt;script&gt;alert('attack')&lt;/script&gt;</p>
```

You don't escape everything, only a specific list. The slash and the letters of the tag name stay as they are. The five you should generally escape, depending on context:

| Character | Escape | Why |
|---|---|---|
| `<` less-than | `&lt;` | could start a tag |
| `>` greater-than | `&gt;` | could end a tag |
| `&` ampersand | `&amp;` | escapes themselves start with `&`, so a literal `&` must be escaped to avoid confusion |
| `"` double quote | `&quot;` | could end an attribute value |
| `'` single quote | `&#39;` / `&apos;` | could end an attribute value |

If Google escaped all user input before putting it into search results or inboxes, none of the attacks above would work. Try [`demos/05_xss_escaping.py`](../demos/05_xss_escaping.py).

> 📌 Escaping depends on **context**. HTML body, HTML attributes, JavaScript strings, and URLs each need different encoding. In practice, rely on your framework's auto-escaping templates instead of hand-written replacements.

#### Defense 2: HTTP headers (Content-Security-Policy)

Recall that **HTTP headers** are key–value lines sent in the "virtual envelope" along with requests and responses. A server (say example.com) can send:

```http
Content-Security-Policy: script-src https://example.com/
```

- The key is `Content-Security-Policy`, and the value is `script-src <allowed URL>`.
- The browser will then run JavaScript only from **separate files** (usually `.js`) loaded from that origin:
  ```html
  <script src="..."></script>
  ```
- **Inline scripts are blocked.** A `<script>...</script>` block inside the HTML won't run, even if the developer forgot to escape user input somewhere. The assumption is that someone who put a `.js` file on your own server meant for it to be there.

The same mechanism works for **CSS** (Cascading Style Sheets, the language used to style pages):

```http
Content-Security-Policy: style-src https://example.com/
```

This allows only stylesheets loaded like the example below and blocks inline `<style>` tags:

```html
<link href="..." rel="stylesheet">
```

This is **defense in depth**. It works in newer browsers and adds a second layer in case escaping fails.

> **Q: Doesn't React (JSX) mix JavaScript and HTML? Isn't that a risk?**
> A: With JSX, the browser runs JavaScript from the React library, loaded from `.js` files, which reads the JSX and turns it into the page. As long as all the code comes from external files, everything works under CSP. Inlined code would be blocked, so the same rules apply.

> 📌 Also mark session cookies `HttpOnly` so `document.cookie` can't read them even if XSS gets through. (Not covered in the lecture.)

### SQL injection

**SQL** (Structured Query Language) is used to query databases on a server. It's usually combined with another language (Python, PHP, Java, ...), which **builds queries dynamically** from what the user typed. The lecture uses pseudocode that mixes SQL with a Python placeholder:

```sql
SELECT * FROM users WHERE username = '{username}'
```

`{username}` means "insert whatever the human typed here". For a normal user named `malan`, this selects everything known about that user.

**Theme: always mistrust user input.** Sanitize it by escaping dangerous characters, just like with XSS.

#### Attack 1: running a second, destructive command

The adversary guesses the site uses SQL and types this as their username, usually found by **trial and error** rather than on the first try:

```
malan'; DELETE FROM users; --
```

After the input is inserted:

```sql
SELECT * FROM users WHERE username = 'malan'; DELETE FROM users; --'
```

Each symbol has a purpose:

| Piece | Effect |
|---|---|
| `'` after `malan` | Closes the developer's opening quote early |
| `;` | Ends the first SQL command, like a period in English. Anything after it is a new command |
| `DELETE FROM users;` | A second command written entirely by the adversary: **delete every user** |
| `--` | A SQL **comment**: ignore the rest of the line, including the developer's leftover closing `'`, which would otherwise be a syntax error |

Rewritten for readability:

```sql
SELECT * FROM users WHERE username = 'malan';
DELETE FROM users;
```

The first query works as intended. The second deletes *every account in the system*. It doesn't help the adversary log in, but it's destructive.

#### Attack 2: bypassing a login

Now the site asks for both a username and a password:

```sql
SELECT * FROM users WHERE username = '{username}' AND password = '{password}'
```

The adversary types a normal username, `malan`, and this as the password:

```
' OR '1'='1
```

Result:

```sql
SELECT * FROM users WHERE username = 'malan' AND password = '' OR '1'='1'
```

The adversary's quotes line up exactly with the developer's quotes, so everything is balanced. `AND` binds more tightly than `OR`, just as multiplication comes before addition, so it's equivalent to:

```sql
SELECT * FROM users
WHERE (username = 'malan' AND password = '')
OR '1'='1'
```

- The first part is probably false, since the password isn't empty. That doesn't matter.
- `'1'='1'` is **always true**, so the query returns **every user**.
- Login code often assumes the first row returned is the user logging in. The first account in a database is often the **site's creator with admin privileges**, so the adversary might log in as the admin.
- Nothing is special about `1`. `'cat'='cat'` works too, because anything equals itself.

#### Defense: prepared statements

Don't write your own escaping code, the same advice as for cryptography. Millions of developers have hit this problem before, so use the database's built-in solution: **prepared statements**. You write the query with **placeholders**, and the **database** fills in the user's values and handles escaping:

```sql
SELECT * FROM users WHERE username = ?
```

- `?` is a common placeholder convention. You don't add quotes around it, because the prepared statement adds them.
- In SQL, a single quote is conventionally escaped by **doubling it** (`''`), not with `&apos;` or a backslash.

Attack 1 then becomes harmless:

```sql
SELECT * FROM users WHERE username = 'malan''; DELETE FROM users; --'
```

The database treats `''` as one literal apostrophe, so the whole input is just a strange username that matches nobody. Attack 2 becomes:

```sql
SELECT * FROM users WHERE username = 'malan' AND password = ''' OR ''1''=''1'
```

Every quote the adversary typed is doubled. The only quotes that pair up are the ones around the whole username and the whole password.

> 📌 The lecture explains prepared statements as automatic quote-doubling. In most real database drivers, the query **structure is sent and parsed separately from the values**, so the input is never parsed as SQL. The practical advice is the same: always use placeholders, never string formatting. See [`demos/04_sql_injection.py`](../demos/04_sql_injection.py).

> **Q: Couldn't we just run queries as a database user without admin or delete rights?**
> A: Yes, that's a good **additional** defense (least privilege), but it doesn't replace prepared statements. The login bypass only needs `SELECT` permission, so it would still work.

### Command injection

A **command-line interface** (a terminal) runs text commands instead of using menus and buttons. Many languages offer a function called **`system`** that runs a command on the underlying operating system to copy, move, or delete files, or run other programs. Some languages also have **`eval`**, which runs whatever code you pass it.

If a program passes user input to `system` or `eval` without escaping, characters such as `;` can end *your* command and start the *adversary's*. The adversary can then do anything you could do at a command line: delete files, send spam, and more. This puts the whole system at risk.

**Defense:** these languages almost always provide a way to escape user input, built in or as a companion function. **Read the documentation**, and every time you handle user input, ask yourself: "How do I escape this so it can't become a command, SQL, or HTML/JavaScript?"

See [`demos/06_command_injection.py`](../demos/06_command_injection.py). In Python, the safe pattern is passing an argument list without a shell: `subprocess.run(["cmd", user_value])`.

### Developer tools and client-side validation

A lot of software is web-based, including many "native" desktop and phone apps built with HTML, CSS, and JavaScript. Browsers have **developer tools** (usually opened from a menu or by right-clicking the page) that let anyone inspect and **edit** the HTML, CSS, and JavaScript of a page *on their own copy*.

**Example 1: a disabled checkbox**

```html
<input disabled type="checkbox">
```

- `<input>` has no close tag, and `disabled` needs no value.
- The site shows the checkbox grayed out, perhaps because this user shouldn't have access to a feature.
- The user opens developer tools, deletes `disabled`, checks the box, and submits the form.
- A server that assumes "a checked box means they were allowed to check it" has been fooled.

**Example 2: a required field**

```html
<input required type="text">
```

The user deletes `required` and submits without the value. A server that assumes every submission includes a name, email, or password can break.

Editing their own copy is only "hacking themselves" until the server trusts what they send. They can also **disable JavaScript**, which turns off every JavaScript-based check.

- **Client-side validation** runs in the browser: a disabled button, "email format is wrong" messages. It gives immediate, helpful feedback, but it works on the **honor system**.
- **Server-side validation** runs on the server and has the final say over what gets accepted and stored. How to implement it depends on your server language and framework.
- **Rule:** always pair client-side validation with server-side validation. If you have to pick one, **pick server-side**. Client-side validation is "icing on the cake".

### Cross-site request forgery (CSRF)

Browsers send data to servers using HTTP **methods**.

**GET** puts all the information **in the URL**. Imagine Amazon's US "Buy Now" feature, which ships a product with one click if your account is set up, implemented as a plain link:

```html
<a href="https://www.amazon.com/dp/B07XLQ2FSK">Buy Now</a>
```

The URL alone contains enough to buy product `B07XLQ2FSK`. That's convenient, but the link could just as easily be on an adversary's website or in an email.

It gets worse: the adversary doesn't even need you to click. Images load automatically, so:

```html
<img src="https://www.amazon.com/dp/B07XLQ2FSK">
```

The browser requests that URL as soon as you **visit** the page. It isn't an image, but the browser doesn't know that in advance. If you're logged in to Amazon in another tab, or even earlier that day, the request carries your session and **the product is bought**.

GET is supposed to be **"safe"**: it should never change state on the server. A real Buy Now built as a plain GET link would be bad practice.

**POST** puts data deeper inside the "envelope" instead of the URL. It's used for passwords, credit card numbers, and uploads, and it's the method meant for **changing state**. A form-based Buy Now (the `dp` field is the lecture's made-up example):

```html
<form action="https://www.amazon.com/" method="post">
  <input name="dp" type="hidden" value="B07XLQ2FSK">
  <button type="submit">Buy Now</button>
</form>
```

- `method="post"` has to be explicit, because forms default to GET.
- `type="hidden"` sends a key–value pair (`dp=B07XLQ2FSK`) that the user doesn't see.
- It *seems* safer: it isn't a URL you can put in an `<img>`, and a human has to click the button.

That's naive. JavaScript can submit forms by itself:

```html
<script>
  document.forms[0].submit();  // get the first form on the page and submit it
</script>
```

Put this on the adversary's site and anyone logged in to Amazon who visits it buys the product without clicking anything. That's a **cross-site request forgery**:

- **Cross-site**: the request to amazon.com starts from a different site.
- **Request forgery**: the request contains all the right information, but the adversary forged it. It didn't come from Amazon's own pages.

**Defense: a CSRF token.** The server adds another hidden field with a **random, secret** value and **remembers** it, for example in its database:

```html
<form action="https://www.amazon.com/" method="post">
  <input name="csrf_token" type="hidden" value="1234abcd">  <!-- really long and random -->
  <input name="dp" type="hidden" value="B07XLQ2FSK">
  <button type="submit">Buy Now</button>
</form>
```

- Only the real server knows *your* token. Unless the adversary has hacked Amazon or your computer, they can't know it, and guessing a truly random value is practically impossible.
- The forged form has no token or a wrong one, so the server rejects it and shows an error.
- Most web frameworks and libraries (Python has several) include this protection. You have to know the threat exists in order to turn it on.
- Sites that talk to the server directly from JavaScript can send the token in an **HTTP header** instead of a form field.

For more on web attacks, the lecture recommends **OWASP** (the Open Worldwide Application Security Project), which documents these attacks and how to defend against them.

> 📌 Modern browsers also default cookies to `SameSite=Lax`, which blocks cookies on most cross-site POSTs. It's a useful extra layer, but CSRF tokens remain the standard defense. (Not covered in the lecture.)

> **Q: How will AI and quantum computing change cybersecurity?**
> A: Out of scope for today, but "quantum computing is bad if the bad guys have it and you and I don't." (See Lecture 1.)

## Part 2: Software on your own devices

### Arbitrary code execution and buffer overflows

**Arbitrary code execution (ACE)** means an adversary tricks your computer into running code *they* wrote, which isn't part of the software. When the adversary does this from elsewhere over a network, it's called **remote code execution (RCE)**. A very common way to do it is a **buffer overflow**.

**Mental model of memory.** Picture a program's memory as a big rectangle:

- **Top**: the program's **machine code**, the zeros and ones that are its instructions, loaded when you open the program.
- **Bottom**: the **stack**, memory the program uses and releases as it runs (reading input, loading a game level, and so on). In this picture the stack **grows upward** from the bottom, like trays in a cafeteria. Each function call gets its own **frame**.

**Return addresses.** When a program calls a function (you click Print, or start a search), it first writes a **"note to self"** on the stack: the **return address**, meaning where in the machine code to go back to afterward. Then the function's data goes *above* it. Normally:

1. You click Search. The return address ("go back here in the machine code") is pushed.
2. You type `cats`, which is stored in a buffer just above it.
3. The search finishes, that frame is removed, the program follows the return address back, and it waits for your next action.

**The attack.**

- Programmers guess how much input to expect and allocate a **buffer** of that size. If the input is longer than expected and the program doesn't check, it **overflows** the buffer into nearby memory.
- An adversary provides two long things instead of `cats`:
  1. **Attack code**: bytes that are machine instructions (delete files, send spam, skip the software's registration check).
  2. Enough extra bytes to **overwrite the return address** with the **address of their attack code**, usually found by lots of trial and error.
- When the function finishes, the program "returns" into the attacker's code instead of its own.
- The attack code runs with **your** privileges. Whatever you can do on your computer, the adversary can now do.
- In practice, the input wouldn't be typed as literal zeros and ones on a keyboard. It would be delivered some other way, such as a file or network data.

The name of the programmer Q&A site **stackoverflow.com** refers to this kind of bug.

> 📌 In real CPUs (e.g. x86), the stack usually grows toward *lower* addresses. The lecture's "grows upward" matches its diagram, where the stack sits at the bottom. The attack works the same way either way: overflowing a local buffer reaches the saved return address. Strictly, this is a **stack-based buffer overflow**. "Stack overflow" also names a different bug, running out of stack space from deep recursion. Modern mitigations include stack canaries, ASLR, non-executable memory (DEP/NX), and memory-safe languages such as Rust, Go, Java, and Python.

**Cracking and reverse engineering.**

- **Cracking** means breaking into software, for example removing the need for a serial number or activation code by injecting code that skips those instructions. (It also refers to guessing passwords.)
- **Reverse engineering** means figuring out how something was built. Installed software is mostly zeros and ones, but with the right techniques and trial and error, people can work out what it does. Depending on the language it was written in, they can learn even more.
- There's a good side: **malware analysis** uses the same techniques to understand malware and build antivirus defenses.

### Open-source vs. closed-source software

**Open source**: anyone can read the source code (Python, PHP, Java, C#, C++, ...) and see exactly what it will do.

- 👍 Anyone can **audit** it for **backdoors** or malicious instructions, and many people looking might find bugs sooner.
- 👎 The version *you're* running might not match the published code. You could be tricked by phishing into installing a malicious fake build.
- 👎 Bugs still exist, and you're handing adversaries the blueprint. The lecture compares it to the **Death Star plans** in Star Wars.
- 👎 If an adversary finds a bug and tells no one, you have a **zero-day** (Lecture 2).

**Closed source** (the default for most commercial software): only the company's employees can see the code.

- 👍 Adversaries can't read the code, so bugs may be less likely to be found and exploited.
- 👎 Users can't verify what it does.

The lecture leaves this as a debate for you to form your own opinion on.

### App stores and code signing

Getting software only from **official app stores** (Apple, Google, Microsoft; iPhone, Android, macOS, Windows) means a large company, or its automated tools, analyzes apps before distributing them.

- It isn't perfect, and malicious apps have gotten through, but it raises the adversary's cost and risk.
- Don't install software from random websites or email links.
- Developers sometimes need to install "unauthorized" software, which requires changing settings. People criticize this **walled garden**, where you need a corporation's permission to distribute software, but it does serve a security purpose.

**How the store enforces this with the Lecture 1 building blocks:**

1. **Developer → store.** The developer hashes the software, getting a fixed-length, almost certainly unique fingerprint, and **signs the hash with their private key**. They registered their **public key** with the store in advance, so the store can verify the software really came from that developer and not from an impersonator.
2. **Store → your device.** The store hashes the software and **signs the hash with the store's private key**. Your phone or computer checks this signature before installing.
3. Unsigned software from the internet triggers warnings like "this app is from an unidentified developer".

### Package managers

Linux systems and programming-language ecosystems use **package managers** to install libraries and tools, often open source: **pip** (Python), **gem** (Ruby), **npm** (Node.js), **apt** (Linux). They use the same idea: packages are **digitally signed**, and your computer verifies the signatures before installing. Modern operating systems increasingly build in these checks. That makes installing third-party software more annoying, but if you trust the store or package manager, you can more safely trust what it distributes.

**Still not fail-safe.** Version 1 and 2 of a package might be fine and version 3 malicious, because:

- The developer finally did what they intended all along.
- The developer **sold** the project to someone who added ads or malware.
- Someone hacked the developer's account or computer and stole their **private key**, so they can sign as that developer.

The goal is the course's recurring idea: **raise the bar**. Increase the adversary's cost and risk, and lower the chance that any given piece of software is malicious.

### Bug bounties

Some companies pay people to find security bugs, as a **bounty** (a reward, not a ransom):

- You report the bug **only to the vendor** and give them time to fix it before telling anyone else. The vendor pays you, with more money for more severe bugs.
- Everyone wins: you get paid, the company fixes the bug, and hopefully no adversary found it first.
- It channels skills that might otherwise go into ransomware toward defense. This is mainly a practice for software *developers* to consider.

### Tracking vulnerabilities

| Acronym | Meaning |
|---|---|
| **CVE** (Common Vulnerabilities and Exposures) | A unique ID for each publicly known flaw in a specific product and version, e.g. `CVE-2021-44228` (Log4Shell). Admins, companies, and users use CVEs to stay current |
| **CVSS** (Common Vulnerability Scoring System) | A standardized **severity** score (0–10). It helps you prioritize what to fix or update with limited time, or what to stop using |
| **EPSS** (Exploit Prediction Scoring System) | The estimated **probability** that a vulnerability will actually be exploited. It separates hypothetical threats from real ones |
| **KEV** (Known Exploited Vulnerabilities catalog, from CISA) | Vulnerabilities **known to have been exploited** in the wild |

Together they show how large the field is: there are thousands of real vulnerabilities to track.

📌 How to prioritize: KEV first, then high EPSS, then high CVSS. A severe bug nobody exploits can be less urgent than a medium bug under active attack.

## Review questions

<details><summary>1. In the phishing example, which part of the link does the browser follow, and how can you check it before clicking?</summary>

The browser follows the `href` attribute, not the visible text between `<a>` and `</a>`. Hovering over the link shows the real destination, usually in the bottom-left corner of the browser.
</details>

<details><summary>2. What root cause do XSS, SQL injection, and command injection share?</summary>

Untrusted input is inserted into something that gets interpreted (HTML/JavaScript, SQL, a shell), so data becomes code. The fix is to escape the input for that context or keep code and data separate (prepared statements, argument lists).
</details>

<details><summary>3. Reflected vs. stored XSS: how does each reach the victim?</summary>

Reflected: the payload is in a crafted URL (e.g. `?q=%3Cscript%3E...`), and the server echoes it back to whoever opens the link. Stored: the payload is saved on the server (e.g. in an email or comment) and served to everyone who views it.
</details>

<details><summary>4. Why must `&` itself be escaped as `&amp;`?</summary>

HTML escapes start with `&`. A literal ampersand in user input could be mistaken for the start of an escape sequence, so it gets its own escape.
</details>

<details><summary>5. What does `Content-Security-Policy: script-src https://example.com/` do, and why is it "defense in depth"?</summary>

It tells the browser to run only JavaScript loaded from `.js` files on example.com and to block inline `<script>` blocks. If the developer forgets to escape user input somewhere, an injected inline script still won't run.
</details>

<details><summary>6. Walk through why `' OR '1'='1` logs you in.</summary>

It turns the query into `WHERE (username='malan' AND password='') OR '1'='1'`. `AND` binds first. The `OR '1'='1'` part is always true, so the query returns every user, and login code that takes the first row may log the attacker in, possibly as the admin.
</details>

<details><summary>7. Why isn't a least-privilege database account enough to stop SQL injection?</summary>

It stops destructive commands like `DELETE`, but the login-bypass attack only needs `SELECT`. It's an additional defense, not a replacement for prepared statements.
</details>

<details><summary>8. Why is a `required` or `disabled` attribute not a security control?</summary>

The HTML runs on the user's machine. They can remove attributes with developer tools, disable JavaScript, or send requests directly. Only server-side validation is enforceable.
</details>

<details><summary>9. Why doesn't switching Buy Now from GET to POST stop CSRF, and what does?</summary>

JavaScript on the attacker's page can auto-submit a POST form (`document.forms[0].submit()`), and the victim's cookies go along with it. A random per-user CSRF token that only the real server knows, checked on the server, stops it. The attacker can't include a token they don't know.
</details>

<details><summary>10. How does a buffer overflow lead to arbitrary code execution?</summary>

Input longer than the buffer overwrites nearby stack memory, including the saved return address. The attacker supplies machine code plus an address pointing to it. When the function returns, the program jumps into the attacker's code and runs it with the user's privileges.
</details>

<details><summary>11. How do app stores use hashing and signatures?</summary>

The developer signs a hash of the app with their private key, and the store verifies it with the developer's registered public key. The store then signs the app with its own private key, and devices verify the store's signature before installing.
</details>

<details><summary>12. You have 200 open CVEs. What do you patch first?</summary>

Anything in CISA's KEV catalog, since it's known to be exploited, then CVEs with a high EPSS, then by CVSS severity and how exposed the affected system is.
</details>
