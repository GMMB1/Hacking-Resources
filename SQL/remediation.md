

---

**SQL Injection Remediation**

As impactful as SQL Injection vulnerabilities are, developers have ways to protect their web applications by following these tips:

---

**1. Prepared Statements (Parameterized Queries)**

In a prepared query, the first thing the developer writes is the SQL query, and then any user input is added as a parameter afterward. Writing prepared statements ensures that the structure of the SQL code cannot be changed, and the database can distinguish between the query and the data. As a bonus, it makes your code look cleaner and easier to read.

**2. Input Validation**

Input validation can go a long way in protecting what gets placed into an SQL query. Using an allowlist can restrict input to specific strings only, or the string replacement method in the programming language can filter characters you want to allow or disallow.

**3. Escaping User Input**

Allowing user input that contains characters like `'`, `"`, `$`, `\` can break SQL queries or, worse, as we have learned, open them up to injection attacks. Escaping user input is a method of adding a backslash (`\`) before these characters, causing them to be parsed as a regular string rather than a special character.

---

**Additional Details & Full Developer Guide**

---

**1. Prepared Statements — Deep Dive**

This is the **#1 most effective defense** against SQL Injection. The query structure is sent to the database first, and user data is sent separately — they are never combined into a raw string.

**PHP (PDO):**
```php
// ❌ Vulnerable
$query = "SELECT * FROM users WHERE username='$username' AND password='$password'";

// ✅ Safe — Positional Parameters
$stmt = $pdo->prepare("SELECT * FROM users WHERE username=? AND password=?");
$stmt->execute([$username, $password]);

// ✅ Safe — Named Parameters
$stmt = $pdo->prepare("SELECT * FROM users WHERE username=:user AND password=:pass");
$stmt->execute([':user' => $username, ':pass' => $password]);
```

**Python (with MySQL):**
```python
# ❌ Vulnerable
query = f"SELECT * FROM users WHERE username='{username}'"

# ✅ Safe
cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
```

**Node.js (MySQL2):**
```javascript
// ❌ Vulnerable
db.query(`SELECT * FROM users WHERE username='${username}'`);

// ✅ Safe
db.query("SELECT * FROM users WHERE username=? AND password=?", [username, password]);
```

**Java (JDBC):**
```java
// ❌ Vulnerable
String query = "SELECT * FROM users WHERE username='" + username + "'";

// ✅ Safe
PreparedStatement stmt = conn.prepareStatement(
    "SELECT * FROM users WHERE username=? AND password=?"
);
stmt.setString(1, username);
stmt.setString(2, password);
```

---

**2. Input Validation — Deep Dive**

Never trust user input. Validate everything before it touches the database.

**Allowlist Approach (Whitelist):**
```python
import re

# Only allow alphanumeric usernames
def validate_username(username):
    if not re.match("^[a-zA-Z0-9_]{3,20}$", username):
        raise ValueError("Invalid username format")
    return username

# Only allow integers for ID parameters
def validate_id(id):
    if not str(id).isdigit():
        raise ValueError("ID must be a number")
    return int(id)
```

**Type Casting:**
```php
// If you expect a number, force it to be one
$id = (int)$_GET['id'];  // "1 OR 1=1" becomes just 1
$query = "SELECT * FROM blog WHERE id=$id";  // Now safe
```

**Validation Rules by Input Type:**

| Input Type | Validation Rule |
|---|---|
| ID / Number | Must be integer only |
| Username | Alphanumeric + underscore only |
| Email | Must match email regex pattern |
| Date | Must match date format |
| Search | Strip SQL special characters |
| File name | No path traversal characters |

---

**3. Escaping User Input — Deep Dive**

Escaping converts dangerous characters into safe equivalents:

| Character | Escaped Version | Meaning |
|---|---|---|
| `'` | `\'` | Single quote |
| `"` | `\"` | Double quote |
| `\` | `\\` | Backslash |
| `%` | `\%` | Wildcard (LIKE queries) |
| `_` | `\_` | Single char wildcard |
| `;` | `\;` | Statement terminator |

**PHP Example:**
```php
// MySQL real escape (less preferred than prepared statements)
$username = mysqli_real_escape_string($conn, $_POST['username']);
$query = "SELECT * FROM users WHERE username='$username'";
```

> ⚠️ **Important:** Escaping alone is **not enough** — always combine it with prepared statements. Escaping can be bypassed in certain character encodings.

---

**4. Additional Layers of Defense**

**Least Privilege Database Accounts:**
```sql
-- Create a restricted DB user for the web app
CREATE USER 'webapp'@'localhost' IDENTIFIED BY 'strongpassword';

-- Only grant what's needed
GRANT SELECT, INSERT ON shopdb.products TO 'webapp'@'localhost';

-- Never use root for web applications!
```

**Disable Dangerous MySQL Features:**
```sql
-- Disable LOAD_FILE and INTO OUTFILE
SET GLOBAL secure_file_priv = NULL;

-- Disable multiple statements
-- Use PDO::MYSQL_ATTR_MULTI_STATEMENTS = false
```

**Error Handling — Never expose DB errors:**
```php
// ❌ Dangerous — shows DB structure to attacker
echo $e->getMessage();  

// ✅ Safe — log internally, show generic message
error_log($e->getMessage());
echo "An error occurred. Please try again.";
```

**Web Application Firewall (WAF) Rules:**
Common WAFs that block SQLi:
- **ModSecurity** (open source)
- **Cloudflare WAF**
- **AWS WAF**
- **Imperva**

Example ModSecurity rule that blocks common SQLi:
```
SecRule ARGS "@detectSQLi" "id:1001,phase:2,deny,status:403,msg:'SQL Injection Detected'"
```

**5. Using an ORM (Object Relational Mapper)**

ORMs automatically handle parameterization — you never write raw SQL:

**Python (SQLAlchemy):**
```python
# ✅ Automatically safe — no raw SQL
user = db.session.query(User).filter_by(username=username).first()
```

**PHP (Laravel Eloquent):**
```php
// ✅ Automatically safe
$user = User::where('username', $username)->first();
```

**Node.js (Sequelize):**
```javascript
// ✅ Automatically safe
const user = await User.findOne({ where: { username } });
```

---

**Defense-in-Depth Checklist:**

| Layer | Defense | Priority |
|---|---|---|
| Code | Prepared statements | 🔴 Critical |
| Code | Input validation | 🔴 Critical |
| Code | Escaping | 🟠 High |
| Code | ORM usage | 🟠 High |
| Database | Least privilege accounts | 🔴 Critical |
| Database | Disable dangerous functions | 🟠 High |
| Application | Generic error messages | 🟠 High |
| Network | WAF deployment | 🟡 Medium |
| Process | Regular security audits | 🟡 Medium |
| Process | Penetration testing | 🟡 Medium |

---

**Quick Reference — Safe vs Unsafe:**

```php
// ❌ NEVER DO THESE:
"SELECT * FROM users WHERE id=" . $_GET['id']
"SELECT * FROM users WHERE name='" . $name . "'"
sprintf("SELECT * FROM users WHERE id=%s", $id)

// ✅ ALWAYS DO THIS:
$stmt = $pdo->prepare("SELECT * FROM users WHERE id=?");
$stmt->execute([$_GET['id']]);
```

---

**Key Takeaway:**

> The golden rule is: **never concatenate user input directly into a SQL query.** Treat all user input as untrusted, always use prepared statements as your first line of defense, and layer additional protections on top. A single parameterized query can prevent the most critical vulnerability in web security! 🛡️
