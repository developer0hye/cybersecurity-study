# Lecture 4: Preserving Privacy

[Official notes](https://cs50.harvard.edu/cybersecurity/notes/4/) · [Week page (video, slides, transcript)](https://cs50.harvard.edu/cybersecurity/weeks/4/)

## TL;DR

- Clearing your browser history doesn't clear **server logs**. Every request reveals your IP, time, URL, referrer, and user agent.
- You are tracked through **headers** (Referer, User-Agent), **cookies** (session, tracking, third-party, supercookies), **URL parameters**, and **fingerprinting**.
- **Private browsing** only stops your *own device* from keeping history and cookies after the session. Sites, your ISP, and your employer can still see you.
- **DNS** queries are plaintext by default. **DoH/DoT** encrypts them.
- A **VPN** moves trust to the VPN provider. **Tor** spreads trust across relays so no single one knows both who you are and where you go.
- Review app **permissions**, location especially.
- No technology gives absolute protection.

## Core concepts

### Browsing history and server logs

A typical web server (nginx "combined" format) logs every request:

```nginx
log_format combined '$remote_addr - $remote_user [$time_local] '
                    '"$request" $status $body_bytes_sent '
                    '"$http_referer" "$http_user_agent"';
```

That is your **IP address**, the time, the requested URL, where you came from, and your browser/OS. Clearing local history (which also logs you out) does nothing to these logs.

### Referer header

When you click a link, the browser can tell the destination site where you came from:

```http
Referer: https://www.google.com/search?q=cats
```

That reveals your search query. (The header name really is misspelled "Referer" in the HTTP spec.) A site can limit what it sends:

```html
<meta name="referrer" content="origin">       <!-- sends only https://www.google.com/ -->
<meta name="referrer" content="no-referrer">  <!-- sends nothing -->
```

or with the HTTP header `Referrer-Policy: no-referrer`.

> ⚠️ The official notes use `content="none"`. That isn't a valid Referrer-Policy value, and the correct token is **`no-referrer`**. 📌 Modern browsers already default to **`strict-origin-when-cross-origin`**, which sends only the origin to other sites, so full search URLs usually don't leak this way anymore.

### Fingerprinting

Even without cookies, a site can combine many small signals into a near-unique ID:

- **User-Agent**: browser, version, OS, device model
  ```
  Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/... Mobile Safari/537.36
  ```
- IP address, screen resolution, timezone, language, installed fonts and extensions, canvas/WebGL rendering quirks

You can't delete a fingerprint the way you delete a cookie. Defenses make users *look alike*: Tor Browser and Brave/Firefox fingerprinting protections standardize or randomize these signals.

### Cookies

A server sets a cookie with a `Set-Cookie` response header, and the browser sends it back in a `Cookie` request header.

**Session cookie**: identifies your logged-in session. It is the "hand stamp" from a club.

```http
HTTP/3 200
Set-Cookie: session=1234abcd
```

Anyone who steals it can take over your session (see Lecture 2). Harden it with attributes:

| Attribute | Effect |
|---|---|
| `Secure` | Sent only over HTTPS |
| `HttpOnly` | JavaScript can't read it (limits XSS theft) |
| `SameSite=Lax/Strict` | Not sent on cross-site requests (limits CSRF and tracking) |
| `Max-Age` / `Expires` | Lifetime. With neither set, it's a *session cookie* deleted when the browser closes |

**Tracking cookie**: a long-lived ID used for analytics and ads. The Google Analytics cookie below lasts 2 years (`63072000` seconds):

```http
Set-Cookie: _ga=GA1.2.0123456789.0; max-age=63072000
```

### Tracking parameters

Tracking IDs placed in the URL itself are visible, but they survive even when cookies are blocked:

```
https://example.com/ad_engagement?click_id=YmVhODI1MmZmNGU4&campaign_id=23
```

`click_id` identifies *you*, while `campaign_id` only identifies the ad campaign. Some browsers now strip known tracking parameters (`fbclid`, `gclid`, etc.), and you can remove them yourself before sharing a link.

### Third-party cookies

A page on `harvard.edu` includes an ad image from `example.com`. That request goes to `example.com`, which sets its own cookie:

```http
GET /ad.gif HTTP/3
Host: example.com
Referer: https://harvard.edu/

HTTP/3 200
Set-Cookie: id=1234abcd; max-age=31536000
```

Later, `yale.edu` shows the same ad network's image:

```http
GET /ad.gif HTTP/3
Host: example.com
Cookie: id=1234abcd
Referer: https://yale.edu/
```

Now `example.com` knows user `1234abcd` visited both harvard.edu and yale.edu. Put this on millions of sites and you have **cross-site tracking**.

📌 Safari and Firefox block or partition third-party cookies by default. Chrome's plans to phase them out have changed several times, so check current browser defaults.

### Private / incognito browsing

- It starts with **no existing cookies** and **discards** history and cookies when the window closes.
- During the session, new cookies still work, sites still log you, and fingerprinting still works.
- Your ISP, employer network, and DNS resolver still see your traffic.
- It protects you from *other people using your device*, not from the network or the websites.

### Supercookies

- Your **ISP** can inject a tracking header into your *unencrypted HTTP* traffic. Verizon's "UIDH" header was a well-known case.
- You can't clear it in the browser, because it's added on the network. Some ISPs allow opting out, and HTTPS blocks the injection.
- "Supercookie" also names browser tricks that store IDs outside the normal cookie jar (HSTS flags, caches, ETags). Browsers now partition these storage areas.

### DNS

- **DNS** translates `harvard.edu` into an IP address. Traditional DNS is **unencrypted**, so your ISP, your network operator, or the DNS resolver sees every domain you look up, even when the site itself uses HTTPS.
- **DNS over HTTPS (DoH)** and **DNS over TLS (DoT)** encrypt the query between you and the resolver. The resolver itself (Cloudflare, Google, your ISP) still sees your queries, so choose one you trust.

### VPN, revisited

- It creates an encrypted tunnel from your computer (A) to a VPN server (B), and websites see B's IP.
- It hides your traffic from the local network and ISP, but the **VPN provider** can see it.
- It **doesn't protect you from malware** on your device, and it doesn't stop cookies or fingerprinting.

### Tor

- **Tor** routes your traffic through **three volunteer relays** (guard → middle → exit), with a separate layer of encryption for each ("onion routing").
- The guard knows your IP but not your destination. The exit knows the destination but not your IP. No single relay knows both.
- Tor Browser also resists fingerprinting by making all users look alike, and it keeps no history.
- Limits: it's slower, the exit relay sees traffic that isn't HTTPS, and **standing out can identify you**. If you're the only Tor user on a campus network, the traffic pattern alone may point to you. Logging into personal accounts over Tor also cancels out the anonymity.

### Permissions

- Operating systems increasingly ask before apps can use location, camera, microphone, contacts, or Bluetooth.
- **Location services** can build a precise history of where you go. Grant permission "while using the app" or "approximate location" when possible, and review permissions regularly.

## Review questions

<details><summary>1. What does private browsing protect against, and what doesn't it?</summary>

It protects against other users of the same device seeing your history and cookies afterward. It doesn't hide you from websites (logs, new cookies, fingerprinting), your ISP, your employer, or DNS.
</details>

<details><summary>2. How do third-party cookies track you across sites?</summary>

Many sites embed content from the same third party (ads, analytics, social buttons). The third party's cookie is sent with each embedded request, and the Referer shows which site you're on. One ID then ties your visits together.
</details>

<details><summary>3. Why does fingerprinting survive clearing cookies?</summary>

It's built from properties of your device and browser (UA, screen, fonts, GPU rendering, timezone). Nothing is stored on your side, so there's nothing to delete.
</details>

<details><summary>4. VPN vs. Tor: whom are you trusting?</summary>

With a VPN you trust a single provider, which sees your IP and your destinations. With Tor you trust that the three relays aren't all controlled by the same party. No single relay sees both ends.
</details>

<details><summary>5. Your site uses HTTPS. Can your ISP still tell which sites you visit?</summary>

Usually yes. Plain DNS queries and the TLS SNI field reveal the domain, and the destination IP does too. DoH/DoT and Encrypted Client Hello (ECH) reduce this. A VPN or Tor hides it from the ISP.
</details>
