# robots.txt & sitemap.xml — 

---

## robots.txt — Deep Dive

### What is robots.txt?

The `robots.txt` file is a plain text file placed at the **root of a website** that follows the **Robots Exclusion Protocol (REP)**. It gives instructions to web crawlers about which parts of the site they should or should not visit.

```
https://example.com/robots.txt    ← always at root level
```

### robots.txt Syntax
```
# Basic structure:
User-agent: [crawler name]
Disallow: [path to block]
Allow: [path to allow]
Crawl-delay: [seconds between requests]
Sitemap: [URL to sitemap]

# Wildcard (*) means ALL crawlers
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /public/
```

---

## Reading robots.txt — Real Examples

### Example 1 — Simple Website
```
User-agent: *
Disallow: /admin/
Disallow: /login/
Disallow: /wp-admin/
Disallow: /backup/
Sitemap: https://example.com/sitemap.xml
```
**What this reveals:**
- `/admin/` → admin panel exists
- `/wp-admin/` → site uses **WordPress**
- `/backup/` → backup directory exists!

---

### Example 2 — Detailed Corporate Site
```
User-agent: *
Disallow: /internal/
Disallow: /staff/
Disallow: /api/v1/
Disallow: /api/v2/
Disallow: /staging/
Disallow: /dev/
Disallow: /test/
Disallow: /old-site/
Disallow: /config/
Disallow: /uploads/private/
Disallow: /customer-data/
Disallow: /financial-reports/
Disallow: /.env
Disallow: /phpinfo.php
```
**What this reveals to a pentester:**
```
/internal/          → internal portal
/staff/             → staff-only area
/api/v1/ and /v2/   → API versions (try both!)
/staging/           → staging environment
/dev/               → development server
/test/              → test environment
/old-site/          → legacy site still running!
/config/            → configuration files
/.env               → environment file (critical!)
/phpinfo.php        → PHP info page (info disclosure)
```

---

### Example 3 — E-commerce Site
```
User-agent: *
Disallow: /checkout/
Disallow: /cart/
Disallow: /account/
Disallow: /order-history/
Disallow: /admin/
Disallow: /vendor/
Disallow: /cron.php
Disallow: /install/
Disallow: /setup/
```
**Security insights:**
```
/vendor/      → third-party libraries (check for outdated versions)
/cron.php     → scheduled task file (may be accessible!)
/install/     → installation directory (critical if accessible)
/setup/       → setup scripts (never leave these online!)
```

---

### Example 4 — Technology Fingerprinting via robots.txt
```
# This robots.txt reveals the entire tech stack!

# WordPress indicators:
Disallow: /wp-admin/
Disallow: /wp-includes/
Disallow: /wp-content/

# Drupal indicators:
Disallow: /core/
Disallow: /profiles/
Disallow: /modules/

# Joomla indicators:
Disallow: /administrator/
Disallow: /components/
Disallow: /modules/

# Laravel indicators:
Disallow: /storage/
Disallow: /artisan

# Django indicators:
Disallow: /django-admin/
Disallow: /static/admin/
```

---

## sitemap.xml — Deep Dive

### What is sitemap.xml?

A **sitemap** is an XML file that lists all pages a website wants search engines to index. Unlike robots.txt (which hides pages), sitemap.xml **advertises** pages.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://example.com/</loc>
    <lastmod>2024-01-15</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://example.com/about</loc>
    <lastmod>2024-01-10</lastmod>
    <changefreq>monthly</changefreq>
    <priority>0.8</priority>
  </url>
</urlset>
```

### Sitemap Index Files
Large sites use a **sitemap index** that points to multiple sitemaps:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <sitemap>
    <loc>https://example.com/sitemap-pages.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-posts.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-products.xml</loc>
  </sitemap>
  <sitemap>
    <loc>https://example.com/sitemap-old-content.xml</loc>  ← old pages!
  </sitemap>
</sitemapindex>
```

---

## Common File Locations to Check

### Standard Locations
```
/robots.txt
/sitemap.xml
/sitemap_index.xml
/sitemap-index.xml
/sitemaps.xml
/sitemap/sitemap.xml
/wp-sitemap.xml          ← WordPress
/page-sitemap.xml        ← WordPress Yoast
/post-sitemap.xml        ← WordPress Yoast
/category-sitemap.xml    ← WordPress Yoast
```

### Additional Discovery Files
```
# Also check these while you're at it:
/security.txt            ← security contact info
/.well-known/security.txt
/crossdomain.xml         ← Flash cross-domain policy
/clientaccesspolicy.xml  ← Silverlight policy
/browserconfig.xml       ← Windows tile config
/manifest.json           ← Web app manifest
/humans.txt              ← team info (OSINT!)
/ads.txt                 ← advertising info
/app-ads.txt             ← mobile advertising
/favicon.ico             ← can fingerprint framework
```

---

## Manual Discovery Workflow

### Step 1 — Fetch and Analyze robots.txt
```bash
# Fetch robots.txt
curl https://target.com/robots.txt

# Save and analyze
curl -s https://target.com/robots.txt | grep -i "Disallow" | sort -u

# Extract all paths
curl -s https://target.com/robots.txt | \
  grep -E "^(Allow|Disallow)" | \
  awk '{print $2}' | sort -u

# Check each disallowed path
curl -s https://target.com/robots.txt | \
  grep "Disallow:" | awk '{print $2}' | \
  while read path; do
    status=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
    echo "$status → https://target.com$path"
  done
```

### Step 2 — Fetch and Parse sitemap.xml
```bash
# Fetch sitemap
curl https://target.com/sitemap.xml

# Extract all URLs
curl -s https://target.com/sitemap.xml | \
  grep -oP '(?<=<loc>)[^<]+'

# Count total pages
curl -s https://target.com/sitemap.xml | \
  grep -c "<loc>"

# Find old/interesting pages
curl -s https://target.com/sitemap.xml | \
  grep -oP '(?<=<loc>)[^<]+' | \
  grep -i "admin\|login\|old\|backup\|test\|dev\|api"

# Get last modified dates
curl -s https://target.com/sitemap.xml | \
  grep -E "<loc>|<lastmod>" | \
  paste - -
```

### Step 3 — Check for Sitemap Index
```bash
# Fetch sitemap index
curl -s https://target.com/sitemap_index.xml | \
  grep -oP '(?<=<loc>)[^<]+'

# Recursively fetch all sitemaps
#!/bin/bash
fetch_sitemap() {
  local url=$1
  curl -s "$url" | grep -oP '(?<=<loc>)[^<]+' | while read loc; do
    if echo "$loc" | grep -q "sitemap"; then
      fetch_sitemap "$loc"
    else
      echo "$loc"
    fi
  done
}
fetch_sitemap "https://target.com/sitemap_index.xml" > all_urls.txt
echo "Total URLs: $(wc -l < all_urls.txt)"
```

---

## Automated Tools

### 1. wget / curl
```bash
# Simple fetch
wget https://target.com/robots.txt
wget https://target.com/sitemap.xml

# Recursive sitemap fetch
wget -r -l 2 https://target.com/sitemap.xml
```

### 2. Nikto
```bash
# Automatically checks robots.txt and sitemap
nikto -h https://target.com

# Output includes:
# + /robots.txt: contains 5 entries which should be manually viewed
# + /sitemap.xml: found sitemap with X pages
```

### 3. Burp Suite
```
# Spider feature automatically:
# 1. Fetches robots.txt
# 2. Parses sitemap.xml
# 3. Adds all discovered URLs to the target scope
# 4. Identifies interesting paths

Target → Site Map → Right click → Spider this host
```

### 4. FFUF (for path discovery after robots.txt hints)
```bash
# Use robots.txt findings as wordlist seeds
ffuf -u https://target.com/FUZZ \
  -w robots_paths.txt \
  -mc 200,301,302,403 \
  -v

# Fuzz with common wordlist
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/dirb/common.txt \
  -mc 200,301,302,403
```

### 5. Gobuster
```bash
# Directory brute forcing informed by robots.txt
gobuster dir \
  -u https://target.com \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -s 200,301,302,403 \
  -v
```

### 6. Python Script — Complete Analyzer
```python
import requests
from xml.etree import ElementTree
import re

def analyze_robots(url):
    print(f"\n[+] Analyzing robots.txt for {url}")
    try:
        r = requests.get(f"{url}/robots.txt", timeout=5)
        if r.status_code == 200:
            print("[*] robots.txt found!")
            lines = r.text.split('\n')
            
            disallowed = []
            allowed = []
            sitemaps = []
            user_agents = []
            
            for line in lines:
                line = line.strip()
                if line.startswith('Disallow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        disallowed.append(path)
                elif line.startswith('Allow:'):
                    path = line.split(':', 1)[1].strip()
                    if path:
                        allowed.append(path)
                elif line.startswith('Sitemap:'):
                    sitemap = line.split(':', 1)[1].strip()
                    sitemaps.append(sitemap)
                elif line.startswith('User-agent:'):
                    ua = line.split(':', 1)[1].strip()
                    user_agents.append(ua)
            
            print(f"\n[*] Disallowed paths ({len(disallowed)}):")
            for path in disallowed:
                # Check if path is accessible
                status = requests.get(
                    f"{url}{path}", 
                    timeout=3,
                    allow_redirects=False
                ).status_code
                print(f"  [{status}] {path}")
            
            print(f"\n[*] Sitemaps found:")
            for s in sitemaps:
                print(f"  {s}")
                
    except Exception as e:
        print(f"[-] Error: {e}")

def analyze_sitemap(url):
    print(f"\n[+] Analyzing sitemap.xml for {url}")
    try:
        r = requests.get(f"{url}/sitemap.xml", timeout=5)
        if r.status_code == 200:
            root = ElementTree.fromstring(r.content)
            ns = {'sm': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
            
            urls = []
            for url_elem in root.findall('.//sm:loc', ns):
                urls.append(url_elem.text)
            
            print(f"[*] Found {len(urls)} URLs in sitemap")
            
            # Find interesting ones
            keywords = ['admin', 'login', 'old', 'backup', 
                       'test', 'dev', 'api', 'private', 'internal']
            
            print("\n[*] Interesting URLs:")
            for u in urls:
                if any(kw in u.lower() for kw in keywords):
                    print(f"  → {u}")
                    
    except Exception as e:
        print(f"[-] Error: {e}")

# Run analysis
target = "https://example.com"
analyze_robots(target)
analyze_sitemap(target)
```

---

## HTTP Status Codes — What They Mean

When checking discovered paths:

| Code | Meaning | Pentester Notes |
|---|---|---|
| `200 OK` | Page exists and accessible | ✅ Investigate further |
| `301/302` | Redirect | Follow the redirect |
| `403 Forbidden` | Exists but blocked | 🟠 Try bypass techniques |
| `401 Unauthorized` | Requires authentication | Try default credentials |
| `404 Not Found` | Doesn't exist | Move on |
| `500 Server Error` | Application error | May reveal info |

### 403 Bypass Techniques
```bash
# When robots.txt reveals a path but it returns 403:

# Method 1 — URL variations
/admin/          → /Admin/
/admin/          → /ADMIN/
/admin/          → /admin/.
/admin/          → //admin/
/admin/          → /admin//

# Method 2 — HTTP method change
curl -X POST https://target.com/admin/
curl -X PUT https://target.com/admin/

# Method 3 — Headers
curl -H "X-Forwarded-For: 127.0.0.1" https://target.com/admin/
curl -H "X-Real-IP: 127.0.0.1" https://target.com/admin/
curl -H "X-Custom-IP-Authorization: 127.0.0.1" https://target.com/admin/
curl -H "Referer: https://target.com/admin/" https://target.com/admin/

# Method 4 — Path traversal
/admin/../admin/
/%2fadmin/
/admin%20/
```

---

## Security.txt — Bonus Discovery

While checking for robots.txt, also check:
```bash
curl https://target.com/security.txt
curl https://target.com/.well-known/security.txt
```

Example response:
```
Contact: security@example.com      ← report vulnerabilities here
Encryption: https://example.com/pgp-key.txt
Bug-Bounty: https://hackerone.com/example
Acknowledgments: https://example.com/hall-of-fame
Policy: https://example.com/security-policy
```

This tells you:
- Where to report bugs (bug bounty!)
- Contact email for security team
- Whether they have a bug bounty program

---

## Complete Discovery Checklist

```
ROBOTS.TXT:
☐ Fetch /robots.txt
☐ List all Disallow paths
☐ List all Allow paths
☐ Note all Sitemap references
☐ Identify technology from path patterns
☐ Check HTTP status of each disallowed path
☐ Try 403 bypass on blocked paths

SITEMAP.XML:
☐ Fetch /sitemap.xml
☐ Check for sitemap index
☐ Extract all URLs
☐ Find URLs with interesting keywords
☐ Note pages with old lastmod dates
☐ Check for unlisted subsections

ADDITIONAL FILES:
☐ /security.txt
☐ /.well-known/security.txt
☐ /crossdomain.xml
☐ /humans.txt
☐ /browserconfig.xml
☐ /manifest.json

FOLLOW-UP:
☐ Run directory brute forcing on interesting paths
☐ Spider all discovered URLs with Burp Suite
☐ Check source code of discovered pages
☐ Note all technologies identified
```

---

## Bug Bounty Value

| Finding | Severity | Notes |
|---|---|---|
| robots.txt reveals admin panel → accessible | High 🟠 | Depends on what's inside |
| robots.txt reveals backup files → downloadable | Critical 🔴 | Data exposure |
| Old sitemap URLs with active vulnerabilities | Varies | Depends on vulnerability |
| robots.txt reveals dev/staging environment | Medium 🟠 | Often less secure |
| security.txt → confirms bug bounty scope | Informational | Guides your testing |

---

## Key Takeaway

> `robots.txt` and `sitemap.xml` are essentially a website's **self-written treasure map**. The site owner tells you exactly what they want to hide (`robots.txt`) and everything they want found (`sitemap.xml`). Always check these files first — they are the **fastest way** to discover the full structure of a target website and often reveal sensitive areas that shouldn't be public. A thorough pentester treats these files as their **first recon step** before any active scanning! 🛡️
