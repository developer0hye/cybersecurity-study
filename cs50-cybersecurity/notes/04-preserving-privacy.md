# Lecture 4: Preserving Privacy

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/4/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/4/)

## TL;DR

- The first four lectures were about keeping A↔B communication safe from people *in between*. This lecture asks a different question: what if you don't want **B itself** (or your ISP, or an advertiser) to learn things about you?
- Clearing your browser history doesn't clear **server logs**. Every request reveals your IP, the time, the URL, the referrer, and your user agent.
- You are tracked through **headers** (Referer, User-Agent), **cookies** (session, tracking, third-party, supercookies), **URL tracking parameters**, and **fingerprinting**.
- **Private browsing** is purely client-side. It stops your *own device* from keeping history and cookies after the session, but sites, your ISP, and your employer still see you.
- **DNS** queries are plaintext by default, so your ISP learns every domain you visit. **DoH/DoT** encrypts them.
- A **VPN** encrypts traffic to one point and changes your apparent IP. **Tor** wraps traffic in layers of encryption across several relays.
- Review app **permissions**, location especially.
- None of these tools give absolute protection. They only **raise the bar**.

## Core concepts

### Web browsing history: a feature and a risk

- **Why it's useful**: you can find a page you saw yesterday, and the browser uses history for **autocomplete** in the URL bar.
- **Why it's a risk**: anyone with physical access to the device can see where you've been. Think of a shared lab computer, an internet café, or a family laptop.
- **Clearing history** is heavy-handed. With all the boxes checked it also wipes cookies and saved passwords, so you're logged out of Google, Outlook, and everything else, even if you only wanted to remove one site.

### Server logs: what the other side remembers

Clearing your local history doesn't touch what the server recorded. Servers keep logs for **diagnostics** (reconstructing what went wrong), **auditing** (who accessed what), and **analytics and advertising** (mining the data to monetize it).

A very common web-server convention is nginx's "combined" log format:

```nginx
log_format combined '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';
```

| Field | What it reveals |
|---|---|
| `$remote_addr` | Your **IP address** |
| `$time_local` | Date and time of the request |
| `$request` | Exactly which file or path you asked for |
| `$http_referer` | The page you came **from** |
| `$http_user_agent` | Your browser, OS, and versions |

You have essentially no control over deleting this data. Unless a law or regulation forces the operator to delete it on a schedule, it can be kept forever.

### The Referer header

HTTP headers are key-value pairs inside the "virtual envelope" of each request or response. Suppose you search Google for cats (`https://www.google.com/search?q=cats`) and click a result:

```html
<a href="https://example.com">cats</a>
```

The browser requests `example.com` and, by default, tells it where you came from:

```http
Referer: https://www.google.com/search?q=cats
```

- **Why sites like it**: analytics. "Most of our visitors come from Google searches for *cats*, not *dogs*."
- **Why it's invasive**: example.com now knows which search engine you use and exactly what you searched for. Every link you click broadcasts where you were.
- **Fun fact**: the header name is misspelled. "Referrer" has four R's, but the author of the original HTTP specification wrote **"Referer"**, and browsers and servers have used the typo ever since. Newer mechanisms such as the HTML attribute and `Referrer-Policy` spell it correctly.

**Sending less.** A site can tell browsers to send only the **origin** (scheme + domain, e.g. `https://www.google.com/`) and not the path or query:

```html
<meta name="referrer" content="origin">
```

or to send nothing at all:

```html
<meta name="referrer" content="no-referrer">
```

A site that controls its web server can set the same policy as an HTTP response header instead:

```http
Referrer-Policy: origin
Referrer-Policy: no-referrer
```

The lecture noted that Google itself sends only the origin, so the destination learns "came from Google" but not the query.

> ⚠️ The lecture and official notes use `content="none"`. That isn't a valid Referrer-Policy value, and the correct token is **`no-referrer`**. 📌 Modern browsers already default to **`strict-origin-when-cross-origin`**, which sends only the origin to other sites, so full search URLs usually don't leak this way anymore.

> **Q: Can I, as a user, remove these traces myself?**
> A: Yes. Client-side privacy software (browser extensions and apps) can strip or reduce such headers, so you don't have to rely on each website to behave well.
>
> **Q: What if that privacy software is itself spying on me?**
> A: A real risk. Open-source code that others can inspect helps, and so does market pressure, since a privacy scandal is bad for business. In the end, installing any software requires trust.
>
> **Q: Do Tor or a live OS like Tails remove all traces?**
> A: No. Some evidence stays on both the client and the server side. Tor is covered below.

### Fingerprinting

**Fingerprinting** combines many traits of your requests into a profile that identifies you with high probability. It doesn't learn your *name*, but it can tell that today's visitor is the same person as yesterday's and last week's, because no "internet twin" has exactly the same configuration.

The ingredients:

- **IP address**: the "return address" on every envelope. It narrows things down, but homes, campuses, and companies often share one IP.
- **User-Agent header**: a long string naming the browser, OS, and their versions:
  ```
  Mozilla/5.0 (Linux; {Android Version}; {Build Tag etc.})
  AppleWebKit/{WebKit Rev} (KHTML, like Gecko)
  Chrome/{Chrome Rev} Mobile Safari/{WebKit Rev}
  ```
  Millions of people run the same browser, so this alone isn't unique either.
- **Values queried with JavaScript** (the server sends code that asks your browser questions): **screen resolution** (especially if you always use a full-screen browser on the same monitor), **installed fonts**, **time zone**, and **installed extensions/plug-ins**.

Together these can identify you even when you're **not logged in** and even when you strip headers. **Retroactive identification** makes this worse: if a site has logged a fingerprint for months and you log in *once*, it can link your name to all that earlier history.

> **Q: Does a VPN prevent fingerprinting?**
> A: No. A VPN changes your IP, which is only one ingredient. Everything else still leaks.
>
> **Q: Could an attacker steal my fingerprint and impersonate me?**
> A: Yes, if they can see the same information. With HTTPS, everything inside the envelope (headers, HTML, JS, CSS) is encrypted, so an on-path attacker sees only your IP. If your device or the server is compromised, all bets are off.
>
> **Q: Can mobile browsers be fingerprinted more?**
> A: Possibly. Phones have extra hardware such as GPS, accelerometers, and gyroscopes that JavaScript can query, usually on an opt-in basis, and that adds identifying signals.
>
> **Q: For storing data on the front end, is local storage or a cookie more secure?**
> A (lecture): Generally **local storage**, because cookies are sent back and forth on every request and could leak through mistakes such as starting on HTTP before redirecting to HTTPS. Anyone with physical access to the device can read either one.
>
> ⚠️ **Caveat:** any JavaScript running on the page can read local storage, so an **XSS** bug (Lecture 3) can steal what's there. For session tokens, the usual recommendation is a cookie marked **`HttpOnly; Secure; SameSite`**, because JavaScript can't read an `HttpOnly` cookie.
>
> **Q: Why do I get calls from local-looking numbers that aren't real?**
> A: **Caller-ID spoofing**. Faking a phone number is trivial. Spammers often copy your own prefix so the call looks like a neighbor. It's another reason the phone network and **SMS** are poor choices for MFA: the system was never designed with cryptography.

### Cookies: session cookies

A **cookie** is a value a server stores in your browser so it can recognize you when you come back. It's usually a large random string, and it doesn't reveal *who* you are until you log in and the server links the cookie to your account.

HTTP is **stateless**: each request/response exchange is complete on its own. To remember you across page loads, the browser must remind the server on every request. Picture a club's **hand stamp**: "you've seen me before, don't make me log in again." This is how logins and **shopping carts** (Amazon remembering your cart as you browse) work.

The server sets it:

```http
HTTP/3 200
Set-Cookie: session=1234abcd
```

(`200` means OK, as opposed to `404` Not Found.) Every visitor gets a different random value, and the browser sends it back on later requests:

```http
GET / HTTP/3
Cookie: session=1234abcd
```

A **session cookie** is meant to be short-lived, gone when you close the browser or reboot. That's good for privacy, because tomorrow you look like a new visitor. In practice browsers restore tabs, so sessions last longer than they used to.

Recommended cookie attributes (not covered in the lecture, but relevant):

| Attribute | Effect |
|---|---|
| `Secure` | Sent only over HTTPS |
| `HttpOnly` | JavaScript can't read it (limits XSS theft) |
| `SameSite=Lax/Strict` | Not sent on cross-site requests (limits CSRF and tracking) |
| `Max-Age` / `Expires` | Lifetime. With neither set, it's deleted when the browser closes |

### Tracking cookies

The mechanism is the same, but the purpose is to **follow you** for analytics, debugging, and especially **targeted advertising**. Different users see different ads, chosen to maximize clicks.

Example: the **Google Analytics** cookie `_ga`. It's set when a site embeds Google's analytics JavaScript, and it's unique per site:

```http
Set-Cookie: _ga=GA1.2.0123456789.0; max-age=63072000
```

`63072000` seconds = **2 years**. A session cookie lasts roughly a day or less. Look through your own browser's cookie settings and you'll likely find `_ga` values.

### Tracking parameters

Clearing cookies hurts trackers, so they also put IDs in **URLs**. Everything after `?` is a query parameter, and `&` separates multiple parameters:

```
https://example.com/ad_engagement?click_id=YmVhODI1MmZmNGU4&campaign_id=23
```

| Parameter | Purpose |
|---|---|
| `campaign_id=23` | Which ad campaign. A small number shared by many users, so it doesn't identify you |
| `click_id=YmVhODI1…` | Unique **per user/click**. A tracking cookie in disguise |

Because the ID is part of the requested URL, it lands in **server logs** and databases, so the site learns which ads you saw and clicked.

- Unlike cookies, which are hidden in headers, tracking parameters are **visible** in the URL bar.
- Browsers and privacy tools increasingly **strip known tracking parameters** automatically, even rewriting links in a page before you click. The lecture's example URL came from Apple's announcement of this feature in Safari. It only works for known parameter names, and sites can rename them.

> **Q: Do cookies track, or are they what gets tracked?**
> A: Cookies are the **values used to track you**, like ink stamped on your hand that your browser shows to every site. The technology itself is neutral and necessary for logins and carts. Because much of the web is free, advertisers have used, or abused, cookies to monetize browsing.

### Third-party cookies

When `example.com` embeds Google Analytics, `example.com` is the **first party** (the site you chose to visit) and `google.com` is a **third party**. Your browser can end up with cookies from both. Browsers offer settings to **block third-party cookies**, but sites can still track you through URL parameters.

**Why third parties are so powerful.** Harvard, Yale, and Stanford each run a page that is just one ad from the same ad network:

```html
<!DOCTYPE html>
<html>
  <head><title>Harvard</title></head>
  <body>
    <img src="https://example.com/ad.gif">
  </body>
</html>
```

The Yale and Stanford pages are identical except for the `<title>`.

1. **You visit harvard.edu.** Your browser sees the `<img>` tag and automatically sends a second request to the ad server:
   ```http
   GET /ad.gif HTTP/3
   Host: example.com
   Referer: https://harvard.edu/
   ```
   The response includes the image and a **one-year** cookie (31,536,000 s = 365 days):
   ```http
   HTTP/3 200
   Set-Cookie: id=1234abcd; max-age=31536000
   ```
2. **You visit yale.edu.** Your browser shows the same stamp to example.com:
   ```http
   GET /ad.gif HTTP/3
   Host: example.com
   Cookie: id=1234abcd
   Referer: https://yale.edu/
   ```
3. **You visit stanford.edu.** The same cookie is sent, this time with `Referer: https://stanford.edu/`.

Now `example.com` knows user `1234abcd` visited Harvard, then Yale, then Stanford, while none of the universities knows about the others. A popular third party (Google in the real world) is embedded in so many sites that it sees far more than any single first party. That is why disabling third-party cookies, or using a browser that blocks them, is worth doing.

📌 Safari and Firefox block or partition third-party cookies by default. Chrome's plans to phase them out have changed several times, so check current browser defaults.

> **Q: Which browsers are best for privacy?**
> A: The lecturer asked to frame it as *privacy-preserving*, not "more secure", since all major browsers are about equally secure at HTTPS. His rough ranking: **Safari** is strong (e.g. stripping tracking parameters). **DuckDuckGo** and **Brave** are privacy-focused third-party browsers. **Firefox** and **Edge** are more privacy-conscious than Chrome. **Chrome** sits at the bottom, because Google's business is monetizing behavior (he admitted he uses it himself).
>
> ⚠️ The lecture groups Firefox with Edge under "the Microsoft ecosystem." Firefox is made by **Mozilla**. Only Edge is Microsoft's.

### Private / incognito browsing

- It gives you what is effectively a **fresh chunk of memory**: no past history, no past cookies, no saved usernames or passwords.
- **The web still works the same inside it.** Tracking parameters, new tracking cookies, and server logs all still apply during the session.
- When you close the window, that session's data is **discarded from your computer**. Tomorrow's private window starts fresh, though **fingerprinting and your IP** can still link the sessions.
- It is **entirely client-side**. It keeps your normal history uncontaminated and lowers, but doesn't eliminate, the chance a server recognizes you.
- **Developer tip**: private windows are handy for web development, because you can test a site as a brand-new visitor without old cookies or cached state.

### Supercookies

These are cookies **injected by a third party on the network path**: your ISP, mobile carrier, company, or university. If the provider can see inside the envelope (plain HTTP), nothing stops it from adding a header of its own, such as `id=1234abcd`. US mobile carriers have done this in the past.

- The value **doesn't come from your browser**, so clearing cookies, clearing history, or using incognito mode has no effect. You'll never see it on your device.
- It is essentially a **machine-in-the-middle attack** carried out by your own provider, for tracking or to serve advertising partners even after you've opted out.
- **Defense: always use HTTPS.** If the envelope is encrypted, the provider can't read it *or add anything to it*, because it doesn't have the key.
- After public backlash, carriers added **opt-out** settings, usually buried deep in account menus.

> **Q: If a cookie stores my password or email, can someone copy it to their computer and impersonate me?**
> A: In transit over HTTPS it's protected. With **physical access** to your computer, it's easy to browse your cookies and read the values. Better designs encrypt or digitally sign cookie values. **Best**: the server stores only a big random value (the hand stamp) in the cookie and keeps your username, email, and password on the server. Your credentials should be sent once, not with every request.
>
> **Q: Can someone intercept and alter my text messages?**
> A: **SMS** is insecure. Numbers are easy to forge, and SIM swapping or porting lets attackers receive your texts, so avoid SMS for anything important. Messengers with **end-to-end encryption** (iMessage, WhatsApp, Signal, some Telegram modes) protect messages even from the company relaying them, assuming it is implemented honestly. That protection comes from **cryptography and digital signatures**, not cookies.

### DNS

The **Domain Name System** translates names like `harvard.edu` into IP addresses, so people don't have to memorize numbers. It's like an old phone book or mnemonic numbers such as **1-800-COLLECT**.

- **Where DNS servers live**: your home router, your ISP, and a **hierarchy** of servers beyond them that can eventually answer any lookup. Answers are **cached** at the ISP, the router, the OS, and the browser for efficiency.
- DNS uses **port 53**, alongside the ports from Lecture 2 (80 HTTP, 443 HTTPS, 22 SSH).
- **The privacy problem**: traditional DNS is **unencrypted**. Every lookup announces the site you're about to visit to the network, and your **ISP** sees and can log every new domain you visit, unless laws restrict it.
- DNS reveals **only the domain**: the ISP knows you went somewhere on `harvard.edu`, but not which department or course page.
- On café or airport Wi-Fi, that hotspot is effectively your ISP. Do you want every hotspot to know everywhere you go?

**Encrypted alternatives**

- **DNS over HTTPS (DoH)** sends DNS queries inside HTTPS, encrypted with TLS, so your ISP or local network can't read them.
- **DNS over TLS (DoT)** is the same idea without the HTTP layer, just TLS.
- The resolver you send queries to (Google, Cloudflare, or another provider) still sees them. The point is to pick **one party you trust** instead of every network you join. These options are increasingly available but often not on by default.

> **Q: Can DNS itself be abused to deceive users?**
> A: Yes. Whoever controls a DNS server can return a **false IP**, pointing `harvard.edu` at a malicious server. **HTTPS** mitigates this: the fake server can't present a valid certificate for harvard.edu, so the connection fails or the browser shows a warning. Users can click through the warning, so don't. ISPs and hotspots do a mild version all the time: mistype a domain and their DNS returns their own server, which shows search results or ads.

### VPN (Virtual Private Network)

- It creates an **encrypted tunnel** from point A (you) to point B, so machines in the middle can't read the traffic.
- **Remote access**: reach campus or corporate services that are only available "on the network", securely, from home, a café, or an airport.
- **It doesn't protect against malware.** If your computer is infected, you now have an *infected* encrypted connection into the company.
- **Appearing to be in another country**: all your traffic exits at B, so services see B's foreign IP address.
- Encryption covers **only A↔B**. After leaving B, traffic is as protected as the protocol you use (plain HTTP is still plaintext).
- A new IP can help cover your tracks, but **fingerprinting** may still link "different IP, same person."

### Tor (The Onion Router)

1. The Tor software finds other computers (**nodes**) running Tor.
2. It picks a path through several of them, say three, and can choose a different path for each request or each day.
3. It **encrypts your request once per node**, using each node's **public key**, in layers like an **onion**.
4. Each node peels off **only its own layer** with its private key and forwards the rest. The last node sends the request to its destination.

Why it helps:

- The path keeps changing, and **by design Tor keeps very little information**, so there are few logs to hand over.
- A government *could* subpoena the relays to reconstruct a path, but this is laborious, and by then the interior nodes usually no longer have the data.

Limits:

- IP addresses and port numbers still show that **someone is using Tor**. If you're the only Tor user on your home, company, or campus network when something malicious happens, suspicion falls on you.
- Like every tool here, it **raises the bar**. It doesn't guarantee privacy.

### Permissions

- iOS, Android, and desktop OSes increasingly ask: allow this app to use the **camera**? The **microphone**? Your **contacts**?
- **Upside**: fine-grained control. **Downside**: the decision is pushed onto you, and many apps refuse to work unless you say yes. That's the usability-vs-privacy tension again.
- Finer choices help: **Always / Only while using the app / Never**. You want the camera and microphone off once the app is closed and the phone is in your pocket.
- **Location services** are the big one. GPS and Wi-Fi positioning are needed for Maps, but many apps ask for location **always** by default, so they can record everywhere you walk. Apple, Google, and others can know nearly everywhere you go if you leave location on everywhere. Think about what it means to carry these radios with you 24/7.

### Course wrap-up

Across the course: securing **accounts** → **data** → **systems** → **software** → preserving **privacy**. The lasting takeaway is the set of *first principles* and building blocks, so you can figure out how new technologies work, which new threats may affect you, and what questions to ask about the software you use or build.

## Review questions

<details><summary>1. You clear your browser history. Which records of your visits still exist?</summary>

Server logs (IP, time, URL, referrer, user agent), your ISP's DNS logs, and any tracking data held by third parties (ad networks, analytics). Clearing history only affects your own device.
</details>

<details><summary>2. What does the Referer header leak, and how can a site reduce it?</summary>

The full URL of the previous page, possibly including a search query. A site can send `Referrer-Policy: origin` (domain only) or `no-referrer` (nothing), as an HTTP header or with `<meta name="referrer" content="...">`.
</details>

<details><summary>3. Name four ingredients of a browser fingerprint. Why does logging in once make it worse?</summary>

IP address, User-Agent, screen resolution, installed fonts, time zone, extensions (any four). If a site has been logging your fingerprint anonymously, one login ties your identity to all the earlier activity.
</details>

<details><summary>4. Session cookie vs. tracking cookie?</summary>

It's the same mechanism with a different purpose and lifetime. A session cookie keeps state (login, cart) and should expire when the browser closes. A tracking cookie (e.g. `_ga`, 2 years) follows you over long periods for analytics and ads.
</details>

<details><summary>5. How do third-party cookies track you across sites?</summary>

Many sites embed content from the same third party. On the first embed, the third party sets a cookie with a unique ID. On every later site, your browser sends that cookie back, and the Referer shows which site you're on. The third party can link all your visits, while each first party sees only its own.
</details>

<details><summary>6. How is a tracking parameter different from a tracking cookie, and how do browsers fight it?</summary>

It lives in the URL (e.g. `click_id=...`), not in a header, so it's visible and survives clearing cookies. It ends up in server logs. Browsers such as Safari strip known tracking parameters automatically. This fails if sites rename them.
</details>

<details><summary>7. What does private browsing protect against, and what doesn't it?</summary>

It protects against other users of the same device seeing your history and cookies afterward. It doesn't hide you from websites (logs, new cookies, fingerprinting), your ISP, your employer, or DNS. It's entirely client-side.
</details>

<details><summary>8. Why can't you delete a supercookie, and what stops it?</summary>

Your ISP or carrier injects it into your traffic on the network path. It never lives in your browser, so there's nothing to clear. HTTPS stops it, because the provider can neither read nor modify encrypted traffic. Some carriers also offer an opt-out.
</details>

<details><summary>9. Your ISP can't read your HTTPS traffic. How does it still know which sites you visit? How do you fix that?</summary>

Plain DNS queries on port 53 reveal every domain you look up. DoH or DoT encrypts them, so only the resolver you choose sees them. A VPN or Tor hides them from the ISP too. The TLS SNI field and destination IP can also reveal the domain, and Encrypted Client Hello (ECH) addresses SNI.
</details>

<details><summary>10. VPN vs. Tor: what does each protect, and what are their limits?</summary>

A VPN encrypts traffic from you to one server and gives you that server's IP. You must trust the provider, and it does nothing against malware or fingerprinting. Tor encrypts in layers across several relays, so no single relay knows both who you are and where you're going, and it keeps little data. It's slow, and being the only Tor user on a network can single you out. Neither gives absolute protection.
</details>
