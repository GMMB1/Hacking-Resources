
---

**Broken Access Control — Deep Dive**

**What is IDOR?**
IDOR (Insecure Direct Object Reference) is a type of Broken Access Control where an application uses user-controllable input to access objects directly without proper authorization checks.

---

**Types of Broken Access Control:**

**1. Horizontal Privilege Escalation**
Accessing another user's data at the **same privilege level**:
```
# Your profile
https://example.com/profile?id=1001

# Another user's profile (just change the ID)
https://example.com/profile?id=1002
```

**2. Vertical Privilege Escalation**
Accessing resources at a **higher privilege level** (user → admin):
```
# Normal user page
https://example.com/user/dashboard

# Try forcing access to admin page
https://example.com/admin/dashboard
https://example.com/admin/panel
https://example.com/administrator
```

**3. Parameter Tampering**
Changing hidden parameters to gain elevated access:
```
# Original request (intercepted with Burp Suite)
POST /update_profile
role=user  →  change to →  role=admin
isAdmin=false  →  change to →  isAdmin=true
account_id=1001  →  change to →  account_id=1
```

**4. Path Traversal as Access Control Bypass**
```
https://example.com/user/../admin/settings
https://example.com/api/v1/users/me/../../../admin
```

---

**Common IDOR Testing Locations:**

| Location | Example |
|---|---|
| URL parameters | `?id=123`, `?user=john` |
| API endpoints | `/api/users/123/data` |
| Hidden form fields | `<input type="hidden" name="role" value="user">` |
| Cookies | `role=user` → change to `role=admin` |
| JSON request body | `{"userid": 123}` → change to `{"userid": 1}` |
| File names | `/files/user123_invoice.pdf` → `/files/user1_invoice.pdf` |

---

**Security Misconfiguration — Deep Dive**

**Common Examples:**

**1. Default Credentials**
Many systems ship with default credentials that are never changed:
```
admin:admin
admin:password
admin:123456
root:root
```
Always check: https://cirt.net/passwords — a database of default credentials for hundreds of systems.

**2. Exposed Sensitive Files**
```
/robots.txt        → may reveal hidden paths
/.git/             → exposed Git repository (source code leak!)
/.env              → environment file with API keys and passwords
/config.php        → database credentials
/backup.zip        → full website backup
/phpinfo.php       → detailed server configuration
/web.config        → IIS server configuration
```

**3. Verbose Error Messages**
Errors that reveal too much information:
```
SQL Error: You have an error near 'SELECT * FROM users WHERE id=1'
File not found: /var/www/html/admin/config.php
```
These reveal database structure, file paths, and technology stack.

**4. Directory Listing Enabled**
When a web server shows all files in a directory:
```
https://example.com/uploads/   → lists all uploaded files
https://example.com/backup/    → lists all backup files
```

**5. Unnecessary Services & Ports Open**
Use tools like Shodan or Nmap to find:
```
Port 21  → FTP (often with anonymous login)
Port 22  → SSH (with default credentials)
Port 3306 → MySQL exposed to the internet
Port 27017 → MongoDB with no authentication
```

---

**Tools Used to Find These Vulnerabilities:**

| Tool | Purpose |
|---|---|
| **Burp Suite** | Intercept and modify requests, test IDOR |
| **FFUF / Gobuster** | Brute force hidden directories and files |
| **Nikto** | Scan for security misconfigurations automatically |
| **Nmap** | Discover open ports and services |
| **Shodan** | Find exposed services on the internet |

---

**How to Prevent Broken Access Control:**
- Enforce **server-side** authorization checks on every request
- Use **indirect references** (random tokens/UUIDs instead of sequential IDs)
- Implement **role-based access control (RBAC)**
- Log and monitor all access control failures
- Deny access by default — only allow what is explicitly permitted

**How to Prevent Security Misconfiguration:**
- Always change **default credentials** immediately
- Disable **directory listing** on web servers
- Hide **error messages** from end users
- Regularly audit exposed files and services
- Use automated scanners like **Nikto** to detect misconfigurations

---

**Bug Bounty Severity:**
- IDOR exposing other users' private data → **High to Critical** 🔴
- IDOR leading to admin access → **Critical** 🔴
- Security Misconfiguration (exposed .env or .git) → **High to Critical** 🔴
- Default credentials → **Critical** 🔴

These are some of the **most commonly found and rewarded** vulnerabilities in bug bounty programs! 💰
