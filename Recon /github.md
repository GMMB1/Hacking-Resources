# GitHub OSINT & Security Research — 

---

## What is Git?

**Git** is a **distributed version control system** created by Linus Torvalds in 2005. It tracks every change made to every file in a project over time.

```
Without Git:                    With Git:
project_final.zip               ┌─────────────────────────┐
project_final_v2.zip            │     Git Repository      │
project_final_REAL.zip          │                         │
project_final_USE_THIS.zip      │  commit 1 → initial     │
                                │  commit 2 → add login   │
😤 Chaos                        │  commit 3 → fix bug     │
                                │  commit 4 → add API key │ ← !
                                │  commit 5 → remove key  │ ← too late!
                                └─────────────────────────┘
                                ✅ Full history preserved
```

---

## Git Core Concepts

### Repository (Repo)
A folder that Git is tracking — contains all files and their complete history:
```bash
# Initialize a new repo
git init my-project

# Structure of a Git repo
my-project/
├── .git/                    ← Git's database (hidden folder)
│   ├── config               ← repo configuration
│   ├── HEAD                 ← current branch pointer
│   ├── objects/             ← all file versions stored here
│   ├── refs/                ← branch and tag references
│   └── logs/                ← history of all changes
├── src/
│   └── app.py
├── config/
│   └── settings.py
└── README.md
```

### Commits
A **snapshot** of the entire project at a point in time:
```bash
# Each commit has:
commit a3f8b2c1d4e5f6789...    ← unique SHA-1 hash
Author: John Dev <john@company.com>
Date:   Mon Jan 15 10:30:00 2024
Message: "Add database connection"    ← developer's note

# Changes in this commit:
+ DB_HOST = "db.internal.company.com"      ← added
+ DB_PASSWORD = "SuperSecret123!"          ← added (mistake!)
```

### Branches
Parallel lines of development:
```
main ────●────●────●────●────●
              \              ↑ merge
          dev  ●────●────●──/
                    \
              feature ●────●
```

```bash
# Common branch names (interesting for pentesters)
main / master      ← production code
dev / develop      ← development (often less secure)
staging            ← pre-production
feature/payment    ← new features in progress
hotfix/            ← emergency fixes
release/           ← release candidates
```

---

## GitHub vs Other Platforms

| Platform | URL | Notes |
|---|---|---|
| **GitHub** | github.com | Largest, owned by Microsoft |
| **GitLab** | gitlab.com | Often self-hosted by companies |
| **Bitbucket** | bitbucket.org | Popular with enterprise |
| **Gitea** | self-hosted | Open source, small teams |
| **Azure DevOps** | dev.azure.com | Microsoft enterprise |
| **SourceForge** | sourceforge.net | Older projects |

> ⚠️ Don't forget to check **all platforms** — a company may secure GitHub but leave GitLab exposed!

---

## Why GitHub is a Gold Mine for Pentesters

Developers accidentally commit sensitive data **every day**. Common mistakes:

```python
# config.py — accidentally committed
DATABASE_URL = "postgresql://admin:password123@db.company.com/prod"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLE"
SECRET_KEY = "super-secret-flask-key-12345"
STRIPE_API_KEY = "sk_live_abc123xyz789"
SENDGRID_API_KEY = "SG.xxxxxxxxxxxxxxxxxxxx"
TWILIO_AUTH_TOKEN = "abc123def456"
```

```bash
# .env file — should never be committed!
DB_PASSWORD=Admin@123
JWT_SECRET=mysecretkey
SMTP_PASSWORD=emailpass123
REDIS_PASSWORD=redispass
```

```yaml
# docker-compose.yml — accidentally public
services:
  db:
    environment:
      MYSQL_ROOT_PASSWORD: rootpass123
      MYSQL_PASSWORD: apppass456
```

---

## GitHub Search — Advanced Techniques

### Basic Search Operators
```
# Search for exact phrase
"company-name"

# Search in specific file
filename:.env

# Search in file path
path:config/

# Search by file extension
extension:sql

# Search by language
language:python

# Search by organization
org:company-name

# Search by user
user:developer-name

# Search by repo name
repo:company/project

# Combine operators
org:company-name filename:.env
```

### Powerful Search Queries for OSINT

**Finding Credentials:**
```
# AWS Keys
"AKIAIOSFODNN" OR "AKIA"
org:target-company "AWS_ACCESS_KEY"
org:target-company "aws_secret_access_key"

# Passwords
org:target-company "password" filename:.env
org:target-company "DB_PASSWORD"
org:target-company "db_password" extension:env
org:target-company "mysql_password"

# API Keys
org:target-company "api_key"
org:target-company "apikey"
org:target-company "secret_key"
org:target-company "private_key"
org:target-company "access_token"

# SSH Keys
org:target-company "BEGIN RSA PRIVATE KEY"
org:target-company "BEGIN OPENSSH PRIVATE KEY"
org:target-company "BEGIN EC PRIVATE KEY"

# JWT Secrets
org:target-company "JWT_SECRET"
org:target-company "jwt_secret"
```

**Finding Configuration Files:**
```
# Environment files
org:target-company filename:.env
org:target-company filename:.env.local
org:target-company filename:.env.production

# Config files
org:target-company filename:config.php
org:target-company filename:wp-config.php
org:target-company filename:database.yml
org:target-company filename:settings.py
org:target-company filename:application.properties
org:target-company filename:appsettings.json

# Docker/K8s
org:target-company filename:docker-compose.yml
org:target-company filename:kubernetes.yml
org:target-company filename:.dockerenv
```

**Finding Internal Infrastructure:**
```
# Internal URLs/IPs
org:target-company "internal.company.com"
org:target-company "192.168."
org:target-company "10.0.0."

# Database connections
org:target-company "jdbc:mysql"
org:target-company "mongodb://"
org:target-company "postgresql://"

# Internal tools
org:target-company "jira.company.com"
org:target-company "confluence.company.com"
org:target-company "jenkins.company.com"
```

---

## GitHub Dorking Tools

### 1. GitDorker
```bash
# Automated GitHub dorking
python3 gitdorker.py -t YOUR_GITHUB_TOKEN -q company-name -d dorks.txt

# Dorks file example:
filename:.env
filename:config.php
"BEGIN RSA PRIVATE KEY"
"api_key"
"password"
```

### 2. TruffleHog — Secret Scanner
```bash
# Install
pip install trufflehog

# Scan a public repo for secrets
trufflehog github --repo https://github.com/target/repo

# Scan entire organization
trufflehog github --org target-company

# Scan with regex patterns
trufflehog github --repo https://github.com/target/repo --only-verified

# Scan local repo
trufflehog git file://./my-repo
```

### 3. GitLeaks
```bash
# Install
brew install gitleaks  # macOS
# or download from github.com/gitleaks/gitleaks

# Scan a repo
gitleaks detect --source https://github.com/target/repo

# Scan with report
gitleaks detect --source . --report-format json --report-path report.json

# Scan specific branch
gitleaks detect --source . --log-opts "main..dev"
```

### 4. GitAllSecrets
```bash
python3 gitallsecrets.py -t YOUR_TOKEN -org target-company
```

### 5. Gitrob
```bash
# Scan organization
gitrob analyze target-company --github-access-token YOUR_TOKEN
```

### 6. GitHub CLI
```bash
# Install GitHub CLI
# https://cli.github.com/

# Search code
gh search code "password" --owner target-company

# List repos of an org
gh repo list target-company --limit 100

# Clone all repos of an org
gh repo list target-company --json nameWithOwner \
  -q '.[].nameWithOwner' | \
  xargs -I {} gh repo clone {}
```

---

## Analyzing Git History — The Most Dangerous Part

Even if a secret was **deleted** in a later commit, it still exists in the **git history**!

```bash
# Clone the target repo
git clone https://github.com/target/repo
cd repo

# View full commit history
git log --oneline

# View all changes in every commit
git log -p

# Search through ALL commits for keywords
git log -p | grep -i "password\|secret\|key\|token\|credential"

# Search for specific string in all commits
git log -S "password" --all

# View a specific commit's changes
git show a3f8b2c1

# View what a file looked like at a specific commit
git show a3f8b2c1:config/settings.py

# See deleted files
git log --all --full-history -- "*.env"

# Restore a deleted file from history
git checkout a3f8b2c1 -- config/settings.py

# View all branches including remote
git branch -a

# Switch to a different branch and check for secrets
git checkout dev
cat config/settings.py
```

### Automated History Analysis
```bash
# Using git-secrets scanner on history
git log --all --oneline | while read hash msg; do
  git show $hash | grep -i "password\|secret\|api_key" && echo "Found in: $hash"
done

# Using TruffleHog on history
trufflehog git https://github.com/target/repo --since-commit HEAD~100
```

---

## Exposed .git Folders on Web Servers

Sometimes developers **deploy their .git folder** to web servers accidentally!

```bash
# Check if .git is exposed
curl https://target.com/.git/config
curl https://target.com/.git/HEAD

# If accessible, you can reconstruct the entire source code!

# Using GitDumper
git-dumper https://target.com/.git/ ./output

# Using wget
wget -r https://target.com/.git/

# What you can find:
# - Complete source code
# - Database credentials in config files
# - Internal API endpoints
# - Encryption keys
# - Business logic
```

---

## GitHub Actions & CI/CD Secrets Exposure

```yaml
# .github/workflows/deploy.yml — badly configured
name: Deploy
on: push
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Deploy
        env:
          # BAD — hardcoded secrets in workflow!
          AWS_KEY: AKIAIOSFODNN7EXAMPLE
          DB_PASS: SuperSecret123
        run: |
          echo "Deploying..."
          
      # GOOD — using GitHub Secrets
      - name: Deploy Safely
        env:
          AWS_KEY: ${{ secrets.AWS_ACCESS_KEY_ID }}
          DB_PASS: ${{ secrets.DATABASE_PASSWORD }}
```

**Look for leaked secrets in:**
```
.github/workflows/*.yml    ← CI/CD pipelines
.travis.yml                ← Travis CI
.circleci/config.yml       ← CircleCI
Jenkinsfile                ← Jenkins
.gitlab-ci.yml             ← GitLab CI
azure-pipelines.yml        ← Azure DevOps
```

---

## OSINT from GitHub Profiles

```bash
# From a developer's profile you can find:
# 1. Their email address
git log --format="%ae" | sort -u

# 2. Internal project names
# 3. Technologies used
# 4. Other employees (contributors)
# 5. Internal domain names
# 6. Architecture details
# 7. Third-party services used

# Find all contributors to an org's repos
# → gives you employee names and emails!

# Check a developer's personal repos
# → they may have copied work code there

# Check forks of private repos
# → forks remain public even if original is deleted!
```

---

## Google Dorking for GitHub

```
# Find GitHub repos for a company
site:github.com "company-name"
site:github.com "company.com"

# Find specific file types
site:github.com "company-name" filename:.env
site:github.com "company-name" "password"
site:github.com "company-name" "api_key"

# Find internal tools
site:github.com "company-name" "internal"
site:github.com "company-name" "confidential"
```

---

## Automated OSINT Workflow

```bash
#!/bin/bash
TARGET="company-name"
TOKEN="your_github_token"

echo "[+] Starting GitHub OSINT for: $TARGET"

# 1. Find all repos
echo "[*] Finding repositories..."
curl -s "https://api.github.com/orgs/$TARGET/repos?per_page=100" \
  -H "Authorization: token $TOKEN" | \
  jq -r '.[].clone_url' > repos.txt

echo "[+] Found $(wc -l < repos.txt) repositories"

# 2. Clone all repos
echo "[*] Cloning repositories..."
while read url; do
  git clone $url 2>/dev/null
done < repos.txt

# 3. Scan with TruffleHog
echo "[*] Scanning for secrets..."
for dir in */; do
  trufflehog git file://./$dir --json >> secrets.json
done

# 4. Search history
echo "[*] Searching git history..."
for dir in */; do
  cd $dir
  git log -p | grep -i \
    "password\|secret\|api_key\|token\|credential\|private_key" \
    >> ../history_findings.txt
  cd ..
done

echo "[+] Done! Check secrets.json and history_findings.txt"
```

---

## Prevention — For Developers

### 1. Use .gitignore
```bash
# .gitignore — add these to EVERY project
.env
.env.local
.env.production
*.pem
*.key
config/secrets.yml
config/database.yml
wp-config.php
settings_local.py
secrets.json
credentials.json
.aws/credentials
```

### 2. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.16.1
    hooks:
      - id: gitleaks

# Now gitleaks runs before every commit!
pre-commit install
```

### 3. GitHub Secret Scanning
```
GitHub → Repository → Settings → Security
→ Enable Secret Scanning
→ Enable Push Protection
```

### 4. Remove Secrets from History
```bash
# If you accidentally committed a secret:

# Option 1 — BFG Repo Cleaner (easier)
java -jar bfg.jar --replace-text passwords.txt my-repo.git
git push --force

# Option 2 — git filter-branch
git filter-branch --force --index-filter \
  'git rm --cached --ignore-unmatch config/secrets.py' \
  --prune-empty --tag-name-filter cat -- --all

# Option 3 — git-filter-repo (recommended)
pip install git-filter-repo
git filter-repo --path config/secrets.py --invert-paths

# IMPORTANT: After removing from history:
# 1. Rotate ALL exposed credentials immediately!
# 2. Assume they were already found and used
# 3. Force push to all branches
# 4. Contact affected service providers
```

---

## Bug Bounty Severity Guide

| Finding | Severity | Payout Range |
|---|---|---|
| Public repo with internal docs | Low 🟡 | $50–$300 |
| Exposed .git folder on web server | Medium–High 🟠 | $500–$3,000 |
| Hardcoded API key (low privilege) | Medium 🟠 | $300–$1,000 |
| Hardcoded database credentials | High 🟠 | $1,000–$10,000 |
| AWS/Cloud credentials exposed | Critical 🔴 | $5,000–$50,000 |
| Private key / SSH key exposed | Critical 🔴 | $5,000–$30,000 |
| Cloud credentials → account takeover | Critical 🔴 | $10,000–$100,000+ |

---

## Key Takeaway

> GitHub is often the **weakest link** in an organization's security. Developers are human — they make mistakes, commit secrets, and forget to check what they're pushing. As a pentester, GitHub reconnaissance can give you **complete access** to a company's infrastructure in minutes. As a developer, treat your repository like a **public billboard** — never put anything there you wouldn't want the world to see, and always rotate credentials the moment you suspect exposure! 🛡️
