# HTTP Headers — 

---

## What are HTTP Headers?

HTTP Headers are **key-value pairs** sent between a client (browser) and a web server with every request and response. They carry metadata about the communication — things like what type of content is being sent, who is sending it, what software is running, and much more.

```
Client (Browser)                    Web Server
      │                                  │
      │  ──── HTTP Request ────────────▶ │
      │  GET /index.php HTTP/1.1         │
      │  Host: example.com               │
      │  User-Agent: Mozilla/5.0         │
      │                                  │
      │  ◀──── HTTP Response ─────────── │
      │  HTTP/1.1 200 OK                 │
      │  Server: nginx/1.18.0            │
      │  X-Powered-By: PHP/7.4.3         │
      │  Content-Type: text/html         │
```

---

## Types of HTTP Headers

### 1. Request Headers (Client → Server)
```http
GET /login HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
Accept: text/html,application/xhtml+xml
Accept-Language: en-US,en;q=0.9
Accept-Encoding: gzip, deflate
Cookie: session=abc123; user=admin
Referer: https://example.com/home
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/x-www-form-urlencoded
Content-Length: 27
X-Forwarded-For: 192.168.1.1
```

### 2. Response Headers (Server → Client)
```http
HTTP/1.1 200 OK
Server: nginx/1.18.0
X-Powered-By: PHP/7.4.3
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Set-Cookie: session=xyz789; Path=/; HttpOnly
Cache-Control: no-cache, no-store
Location: https://example.com/dashboard
WWW-Authenticate: Basic realm="Admin Area"
Access-Control-Allow-Origin: *
```

---

## Using curl for Header Analysis

**Basic Commands:**
```bash
# -v (verbose) — shows both request and response headers
curl http://10.10.251.54 -v

# -I (HEAD request) — only fetch headers, no body
curl http://10.10.251.54 -I

# -i — show response headers with body
curl http://10.10.251.54 -i

# Follow redirects and show headers
curl http://10.10.251.54 -vL

# Save response to file while showing headers
curl http://10.10.251.54 -v -o response.html

# Send custom headers
curl http://10.10.251.54 -v -H "X-Custom-Header: test"

# Send as different User-Agent
curl http://10.10.251.54 -v -A "Mozilla/5.0"

# POST request with data
curl http://10.10.251.54 -v -X POST -d "username=admin&password=test"

# Include cookies
curl http://10.10.251.54 -v -b "session=abc123"

# HTTPS with certificate check disabled
curl https://10.10.251.54 -vk
```

**Understanding curl -v Output:**
```bash
curl http://10.10.251.54 -v

# Output breakdown:
* Connected to 10.10.251.54 port 80       ← connection info
> GET / HTTP/1.1                           ← request line  (> = sent)
> Host: 10.10.251.54
> User-Agent: curl/7.68.0
> Accept: */*
>
< HTTP/1.1 200 OK                          ← response line (< = received)
< Server: nginx/1.18.0                     ← web server + version!
< X-Powered-By: PHP/7.4.3                  ← backend language + version!
< Content-Type: text/html
< Content-Length: 1234

```

---

## Information Disclosure Headers — Pentester's Gold Mine

These headers reveal **technology stack** information:

### Server Header
```http
Server: nginx/1.18.0
Server: Apache/2.4.41 (Ubuntu)
Server: Microsoft-IIS/10.0
Server: Apache-Coyote/1.1   ← reveals Tomcat
Server: lighttpd/1.4.55
```

**What to do with it:**
```bash
# Search for known vulnerabilities
searchsploit nginx 1.18.0
searchsploit apache 2.4.41

# Check CVE databases
# https://www.cvedetails.com/
# https://nvd.nist.gov/
```

### X-Powered-By Header
```http
X-Powered-By: PHP/7.4.3
X-Powered-By: ASP.NET
X-Powered-By: Express          ← reveals Node.js
X-Powered-By: Servlet/3.0      ← reveals Java
```

**Vulnerable PHP versions to watch for:**
```
PHP 5.x  → End of life, many critical CVEs
PHP 7.0-7.2 → End of life
PHP 7.3  → Multiple known vulnerabilities
PHP 7.4.3 → Check specific CVEs for this version
```

### Other Revealing Headers
```http
X-AspNet-Version: 4.0.30319      ← .NET version
X-AspNetMvc-Version: 5.2         ← MVC version
X-Generator: WordPress 5.8       ← CMS!
X-Drupal-Cache: HIT              ← reveals Drupal
X-Joomla-Version: 3.9.28         ← reveals Joomla
Via: 1.1 varnish                 ← reveals Varnish cache
X-Varnish: 12345
X-Cache: HIT from cdn.example.com ← reveals CDN
```

---

## Security Headers — What Should Be Present

These headers **protect** users. Their absence is a vulnerability:

### 1. Strict-Transport-Security (HSTS)
```http
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```
- Forces HTTPS — prevents downgrade attacks
- **Missing** = vulnerable to SSL stripping attacks

### 2. Content-Security-Policy (CSP)
```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.com
```
- Controls which resources can be loaded
- **Missing** = XSS attacks are easier to execute

### 3. X-Frame-Options
```http
X-Frame-Options: DENY
X-Frame-Options: SAMEORIGIN
```
- Prevents clickjacking attacks
- **Missing** = site can be embedded in malicious iframes

### 4. X-Content-Type-Options
```http
X-Content-Type-Options: nosniff
```
- Prevents MIME type sniffing
- **Missing** = browser may execute files with wrong content type

### 5. Referrer-Policy
```http
Referrer-Policy: strict-origin-when-cross-origin
Referrer-Policy: no-referrer
```
- Controls what URL info is sent to other sites
- **Missing** = sensitive URL data may leak to third parties

### 6. Permissions-Policy
```http
Permissions-Policy: camera=(), microphone=(), geolocation=()
```
- Controls browser features (camera, mic, GPS)
- **Missing** = malicious scripts may access device features

### 7. X-XSS-Protection (Legacy)
```http
X-XSS-Protection: 1; mode=block
```
- Old browser XSS filter (replaced by CSP)
- Still worth checking for older browsers

---

## Cookie Security Flags

Cookies are set via the `Set-Cookie` header:
```http
Set-Cookie: session=abc123; Path=/; HttpOnly; Secure; SameSite=Strict
```

| Flag | Purpose | Missing = Vulnerability |
|---|---|---|
| `HttpOnly` | Prevents JS access to cookie | XSS can steal cookies |
| `Secure` | Only send over HTTPS | Cookie sent over HTTP |
| `SameSite=Strict` | Prevents CSRF | CSRF attacks possible |
| `SameSite=Lax` | Partial CSRF protection | Some CSRF risk |
| `Expires` | Controls cookie lifetime | Session management issues |

**Dangerous cookie examples:**
```http
# Missing HttpOnly — XSS can steal with document.cookie
Set-Cookie: session=abc123; Path=/

# Missing Secure — sent over HTTP
Set-Cookie: session=abc123; HttpOnly

# Missing SameSite — CSRF possible
Set-Cookie: session=abc123; HttpOnly; Secure
```

---

## Authentication Headers

```http
# Basic Auth — base64 encoded (NOT encrypted!)
Authorization: Basic YWRtaW46cGFzc3dvcmQ=

# Decode it:
echo "YWRtaW46cGFzc3dvcmQ=" | base64 -d
# Output: admin:password

# Bearer Token (JWT)
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# API Key
X-API-Key: sk_live_abc123xyz
Authorization: ApiKey abc123xyz
```

**Pentesting Basic Auth:**
```bash
# Brute force basic auth with curl
curl -v --user admin:password http://target.com/admin

# Using hydra
hydra -l admin -P /usr/share/wordlists/rockyou.txt target.com http-get /admin
```

---

## Header Injection Attacks

Headers can be vulnerable to injection just like SQL:

### HTTP Header Injection
```
# Inject newlines to add fake headers
User-Agent: Mozilla\r\nX-Injected: malicious-value

# CRLF Injection — inject new response headers
?redirect=https://example.com%0d%0aSet-Cookie:session=hijacked
```

### Host Header Injection
```bash
# Send request with modified Host header
curl -v http://target.com -H "Host: evil.com"

# Can lead to:
# - Password reset poisoning
# - Cache poisoning
# - SSRF (Server-Side Request Forgery)
```

**Password Reset Poisoning Example:**
```http
POST /forgot-password HTTP/1.1
Host: evil.com          ← injected!
Content-Type: application/x-www-form-urlencoded

email=victim@example.com

# Server sends reset link to victim containing evil.com:
# Click here to reset: http://evil.com/reset?token=abc123
# Attacker captures the token!
```

---

## Tools for Header Analysis

**1. curl (command line):**
```bash
curl -v https://target.com 2>&1 | grep -i "server\|powered\|version"
```

**2. Nikto (automated scanner):**
```bash
# Scans for missing security headers and info disclosure
nikto -h http://target.com
```

**3. whatweb:**
```bash
# Identifies technologies from headers
whatweb http://target.com
whatweb -v http://target.com    # verbose
```

**4. Wappalyzer (browser extension):**
- Automatically detects tech stack from headers
- Available for Chrome and Firefox

**5. securityheaders.com:**
```
https://securityheaders.com/?q=target.com
```
Grades security headers from A+ to F

**6. Burp Suite:**
- Intercepts all headers in real time
- Allows modifying and replaying requests
- Passive scanner flags missing security headers

---

## Complete Pentesting Checklist for HTTP Headers

```
INFORMATION DISCLOSURE:
☐ Server header reveals software/version
☐ X-Powered-By reveals backend language/version
☐ X-Generator reveals CMS
☐ Any custom headers leaking internal info

MISSING SECURITY HEADERS:
☐ Strict-Transport-Security missing
☐ Content-Security-Policy missing
☐ X-Frame-Options missing
☐ X-Content-Type-Options missing
☐ Referrer-Policy missing
☐ Permissions-Policy missing

COOKIE FLAGS:
☐ Session cookie missing HttpOnly
☐ Session cookie missing Secure flag
☐ Session cookie missing SameSite
☐ Cookies with sensitive data not encrypted

AUTHENTICATION:
☐ Basic Auth credentials (base64 decodable)
☐ API keys exposed in headers
☐ JWT tokens — check for weak signing (alg:none)

INJECTION:
☐ Host header injection
☐ CRLF injection in redirects
☐ X-Forwarded-For manipulation
```

---

## Bug Bounty Severity Guide

| Finding | Severity | Payout |
|---|---|---|
| Server version disclosure → known critical CVE | High 🟠 | $500–$5,000 |
| Missing HSTS | Low 🟡 | $50–$200 |
| Missing CSP | Low–Medium 🟡 | $100–$500 |
| Missing X-Frame-Options (+ PoC) | Low 🟡 | $100–$300 |
| Session cookie missing HttpOnly | Medium 🟠 | $200–$1,000 |
| CRLF Injection | Medium–High 🟠 | $500–$3,000 |
| Host Header Injection (reset poisoning) | High 🟠 | $1,000–$5,000 |
| JWT Algorithm Confusion | Critical 🔴 | $5,000–$30,000 |

---

## Key Takeaway

> HTTP Headers are like a building's **directory board** — they tell you exactly what's running inside, what version it is, and sometimes even where sensitive areas are. As a pentester, always read headers carefully — they are often the **first clue** to finding a critical vulnerability. As a developer, strip information-disclosing headers and always implement all security headers! 🛡️
