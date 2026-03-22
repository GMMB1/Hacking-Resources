
---

**XSS Explained**

XSS is a scripting language specific to web applications. It is a type of injection that can allow an attacker to execute malicious scripts on the victim's device. A web application is vulnerable to XSS if it uses unsanitized user input. It can be written in JavaScript, VBScript, Flash, and CSS.

There are three main types of Cross-Site Scripting:

---

**Stored XSS:**
This is the most dangerous type of this vulnerability. This is where a malicious string originates from the website's database. This usually happens when a website allows unsanitized user input (removing the "bad parts" from user input) when inserting it into the database.

---

**Reflected XSS:**
The malicious payload is part of the victim's request to the website. The website includes this payload in its response to the user. To exploit it, the attacker needs to trick the victim into clicking a URL to execute their payload.

---

**DOM-Based XSS:**
The DOM (Document Object Model) is an interface for HTML and XML documents. It represents the page so that programs can change the document's structure, style, and content.

---

**XSS Payloads**

Remember that Cross-Site Scripting is a vulnerability that can be exploited to execute malicious JavaScript on the victim's device.

Here are some common payload types used:

```html
<script>alert("Hello World")</script>
```
This command displays a popup message saying "Hello World".

```html
<h1>hello world</h1>
```
HTML code.

`http://www.xss-payloads.com/payloads/scripts/simplekeylogger.js.html`
You can log all of the user's keystrokes, capturing their password and other sensitive information they type on the webpage.

`http://www.xss-payloads.com/payloads/scripts/portscanapi.js.html`
A small local port scanner.

For more payloads, visit: `http://www.xss-payloads.com/`

---

**Some Important Injections:**

```html
<script>alert(window.location.hostname)</script>
```
Prints your IP address on the web page inside a popup window.

```html
<script>alert(document.cookie)</script>
```
This command displays your cookies in a popup window.

```html
<script>document.querySelector('#thm-title').textContent = 'I am a hacker'</script>
```
To change the content inside a `div`, we use this command, select the target `id`, and write between the quotes what we want to display.
