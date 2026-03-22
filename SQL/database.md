

---

**SQL Injection (SQLi) — Introduction**

SQL (Structured Query Language) Injection, commonly referred to as SQLi, is an attack on a web application's database server that causes malicious queries to be executed. When a web application connects to a database using user input that has not been properly validated, there is a potential for an attacker to steal, delete, or modify private and customer data — and also attack web application authentication methods to access private or customer areas. This is why SQLi, in addition to being one of the oldest web application vulnerabilities, can also be the most damaging.

---

**Database Basics**

A database is a way of storing collections of data electronically in an organized manner. A database is controlled by a **DBMS** (Database Management System). DBMS falls into two camps — **relational** or **non-relational**. The focus here is on relational databases. Common ones you will encounter include **MySQL**, **Microsoft SQL Server**, **Access**, **PostgreSQL**, and **SQLite**.

---

**Structure of a Database:**

Within a DBMS, you can have multiple databases, each containing its own set of related data. For example, you might have a database called `shop`. Inside this database, you want to store information about products available for purchase, users who have registered on your online store, and information about orders received. You can store this information separately using **tables** — each table is identified by a unique name.

**Tables** consist of **columns** and **rows:**
- **Columns (Fields)** — run across the top from left to right. Each column has a unique name and a defined data type such as:
  - `INT` — integers (numbers)
  - `VARCHAR` / `TEXT` — strings (text)
  - `DATE` — dates
  - `FLOAT` — decimal numbers
  - `BOOLEAN` — true/false
- **Rows (Records)** — run from top to bottom and contain the actual data. When data is added, a new row is created; when deleted, a row is removed.

A column can also have **auto-increment** enabled, giving each row a unique growing number — this creates what is called a **Primary Key** field, which must be unique for every row.

---

**Relational vs Non-Relational Databases:**

| | Relational | Non-Relational (NoSQL) |
|---|---|---|
| Structure | Tables, columns, rows | Documents, key-value, graphs |
| Schema | Fixed, predefined | Flexible, dynamic |
| Examples | MySQL, PostgreSQL, SQLite | MongoDB, Cassandra, ElasticSearch |
| Relationships | Uses foreign keys | No formal relationships |
| Best for | Structured data | Unstructured/flexible data |

**Relational databases** store information in tables and often share information between them using a **Primary Key** in one table referenced as a **Foreign Key** in another — this creates a relationship between tables, hence the name.

**Non-relational databases** (NoSQL) don't use tables, columns, or rows. No specific database layout needs to be created, so each row of data can contain different information, providing more flexibility.

---

**Essential SQL Commands for Pentesters:**

**Retrieving Data:**
```sql
-- Select all data from a table
SELECT * FROM users;

-- Select specific columns
SELECT username, password FROM users;

-- Filter results
SELECT * FROM users WHERE username='admin';

-- Limit results
SELECT * FROM users LIMIT 1;
```

**Exploring the Database Structure:**
```sql
-- List all databases
SHOW DATABASES;

-- List all tables in current database
SHOW TABLES;

-- Show table structure
DESCRIBE users;

-- Using information_schema (crucial for SQLi)
SELECT schema_name FROM information_schema.schemata;
SELECT table_name FROM information_schema.tables WHERE table_schema='sqli';
SELECT column_name FROM information_schema.columns WHERE table_name='users';
```

**Manipulating Data:**
```sql
-- Insert data
INSERT INTO users (username, password) VALUES ('admin', 'password123');

-- Update data
UPDATE users SET password='newpass' WHERE username='admin';

-- Delete data
DELETE FROM users WHERE username='admin';
```

---

**How SQLi Works — The Core Concept:**

A normal login query looks like:
```sql
SELECT * FROM users WHERE username='admin' AND password='password123';
```

If the application doesn't sanitize input, an attacker can inject:
```sql
-- In username field: admin'--
SELECT * FROM users WHERE username='admin'--' AND password='anything';
-- The -- comments out the rest, bypassing password check
```

---

**Types of SQL Injection:**

| Type | Description | Example |
|---|---|---|
| **In-Band (Classic)** | Results shown directly on page | Error-based, Union-based |
| **Blind Boolean** | True/false responses | Page changes based on condition |
| **Blind Time-Based** | Uses delays to confirm | `SLEEP(5)` |
| **Out-of-Band** | Uses DNS/HTTP requests | `LOAD_FILE()` |
| **Error-Based** | Extracts data via error messages | Forces DB errors |

---

**Important SQL Injection Characters:**

```sql
'           → Single quote (breaks out of string context)
"           → Double quote
--          → Comment (MySQL, MSSQL)
#           → Comment (MySQL)
/**/        → Comment block
;           → Statement terminator
OR 1=1      → Always true condition
AND 1=2     → Always false condition
UNION       → Combine results from multiple queries
```

---

**Common Databases & Their Differences:**

| Feature | MySQL | MSSQL | PostgreSQL | SQLite |
|---|---|---|---|---|
| Comment | `--` or `#` | `--` | `--` | `--` |
| String concat | `CONCAT()` | `+` | `\|\|` | `\|\|` |
| Version | `VERSION()` | `@@VERSION` | `version()` | `sqlite_version()` |
| Current DB | `DATABASE()` | `DB_NAME()` | `current_database()` | — |
| Sleep | `SLEEP(5)` | `WAITFOR DELAY '0:0:5'` | `pg_sleep(5)` | — |

---

**Prevention:**

- Always use **prepared statements / parameterized queries** — the gold standard:
```php
// Vulnerable
$query = "SELECT * FROM users WHERE username='$username'";

// Safe (prepared statement)
$stmt = $pdo->prepare("SELECT * FROM users WHERE username=?");
$stmt->execute([$username]);
```
- Use an **ORM** (Object Relational Mapper) like SQLAlchemy or Hibernate
- Apply **input validation** and whitelisting
- Use **least privilege** — the DB user should only have permissions it needs
- Enable a **WAF** (Web Application Firewall)
- Regularly **audit** and **test** your application with tools like SQLMap

---

**Bug Bounty Severity:**
- SQLi with data extraction → **Critical** 🔴
- SQLi leading to authentication bypass → **Critical** 🔴
- SQLi on a read-only endpoint → **High** 🟠

SQLi is consistently ranked **#1 or #3** in the OWASP Top 10 and remains one of the **highest-paid vulnerabilities** in bug bounty programs! 💰
