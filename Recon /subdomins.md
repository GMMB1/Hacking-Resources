# Subdomain Enumeration — 

---

## What is Subdomain Enumeration?

**Subdomain enumeration** is the process of finding all valid subdomains belonging to a target domain. It is a critical part of the **reconnaissance phase** in security testing and bug bounty hunting.

```
Target domain: example.com

Discovered subdomains:
├── www.example.com          ← main website
├── mail.example.com         ← email server
├── blog.example.com         ← blog (WordPress!)
├── dev.example.com          ← development server
├── staging.example.com      ← staging environment
├── api.example.com          ← API endpoint
├── admin.example.com        ← admin panel!
├── vpn.example.com          ← VPN gateway
├── jenkins.example.com      ← CI/CD server
└── db.example.com           ← database server!
```

---

## Why Subdomains Matter — The Attack Surface

Each subdomain is a **potential entry point**:

```
example.com (main site)     → well secured, patched
dev.example.com             → outdated software, no WAF
staging.example.com         → test credentials still active
old.example.com             → legacy code, many vulnerabilities
partner.example.com         → third-party code, less maintained
jenkins.example.com         → default credentials admin:admin
```

### The Panama Papers Case
```
1. Attacker enumerated subdomains of Mossack Fonseca
2. Found: blog.mossfon.com
3. Blog ran WordPress 4.1 (outdated)
4. WordPress plugin "Revolution Slider" had Remote Code Execution CVE
5. Attacker exploited it → gained server access
6. Pivoted to email server → 11.5 million documents leaked
7. Largest data leak in history at that time (2016)

Lesson: One forgotten subdomain = entire company compromised
```

---

## The Cyber Kill Chain — Where Subdomain Enumeration Fits

```
1. Reconnaissance     ← Subdomain enumeration happens HERE
   └── Find subdomains, technologies, vulnerabilities

2. Weaponization
   └── Prepare exploit for discovered vulnerability

3. Delivery
   └── Send exploit to target (web, email, etc.)

4. Exploitation
   └── Execute the exploit

5. Installation
   └── Install backdoor/persistence

6. Command & Control
   └── Establish communication channel

7. Actions on Objectives
   └── Steal data, pivot, cause damage
```

---

## Method 1 — Passive Reconnaissance

Passive methods gather information **without directly contacting the target**.

### Google Dorking
```bash
# Find all subdomains indexed by Google
site:example.com

# Exclude main site to find subdomains only
site:example.com -www

# Find specific file types on subdomains
site:example.com filetype:pdf
site:example.com filetype:sql
site:example.com filetype:env

# Find login pages
site:example.com inurl:login
site:example.com inurl:admin
site:example.com inurl:dashboard

# Find specific technologies
site:example.com inurl:wp-admin
site:example.com "Powered by WordPress"
site:example.com intext:"Index of /"

# Combine operators
site:example.com -www -mail -blog
```

### Bing Dorking
```bash
# Bing sometimes finds different subdomains than Google!
domain:example.com
site:example.com
```

### Certificate Transparency Logs
Every SSL certificate issued is logged publicly — great for finding subdomains:
```bash
# Search crt.sh
https://crt.sh/?q=%.example.com
https://crt.sh/?q=%.%.example.com    ← wildcard subdomain search

# Using curl
curl -s "https://crt.sh/?q=%.example.com&output=json" | \
  python3 -c "
import json,sys
data=json.load(sys.stdin)
for entry in data:
    print(entry['name_value'])
" | sort -u

# Using certspotter API
curl -s "https://api.certspotter.com/v1/issuances?domain=example.com&include_subdomains=true&expand=dns_names" | \
  python3 -c "
import json,sys
data=json.load(sys.stdin)
for cert in data:
    for name in cert['dns_names']:
        print(name)
" | sort -u
```

### DNS History & Passive DNS
```bash
# SecurityTrails (requires account)
https://securitytrails.com/domain/example.com/subdomains

# DNSdumpster (free)
https://dnsdumpster.com/

# VirusTotal
https://www.virustotal.com/gui/domain/example.com/relations

# Shodan
https://www.shodan.io/search?query=hostname:example.com

# RiskIQ / PassiveTotal
https://community.riskiq.com/
```

### Web Archive (Wayback Machine)
```bash
# Find historical subdomains
curl -s "http://web.archive.org/cdx/search/cdx?url=*.example.com/*&output=text&fl=original&collapse=urlkey" | \
  grep -oP "https?://[^/]+" | sort -u

# Also check:
https://web.archive.org/web/*/example.com
```

---

## Method 2 — Active Reconnaissance

Active methods **directly interact** with the target's DNS servers.

### DNS Brute Forcing
```bash
# Using a wordlist to guess subdomains:
# Try: mail.example.com, dev.example.com, etc.

# Common subdomain wordlist locations:
/usr/share/wordlists/SecLists/Discovery/DNS/
/usr/share/wordlists/dnsmap.txt
```

### Sublist3r — The Tool Mentioned
```bash
# Install
git clone https://github.com/aboul3la/Sublist3r.git
cd Sublist3r
pip install -r requirements.txt

# Basic usage
python3 sublist3r.py -d example.com

# With verbose output
python3 sublist3r.py -d example.com -v

# Save results to file
python3 sublist3r.py -d example.com -o results.txt

# Use specific engines only
python3 sublist3r.py -d example.com -e google,bing,virustotal

# Enable brute force
python3 sublist3r.py -d example.com -b

# Use with threads (faster)
python3 sublist3r.py -d example.com -t 50

# Full options:
# -d domain     → target domain
# -b            → enable brute force
# -p ports      → scan specific ports
# -v            → verbose mode
# -t threads    → number of threads
# -e engines    → specific search engines
# -o output     → save to file
# -n            → no color output
```

### Amass — Most Powerful Tool
```bash
# Install
go install -v github.com/owasp-amass/amass/v4/...@master
# or
sudo apt install amass

# Passive enumeration only
amass enum -passive -d example.com

# Active enumeration
amass enum -active -d example.com

# Full enumeration (passive + active + brute force)
amass enum -d example.com -brute -w /path/to/wordlist.txt

# Save to file
amass enum -d example.com -o subdomains.txt

# Multiple domains
amass enum -d example.com -d example.org -o results.txt

# With API keys configured (~/.config/amass/config.ini)
amass enum -d example.com -config config.ini

# Visualize results
amass viz -d3 -d example.com

# Track changes over time
amass track -d example.com
```

### Subfinder — Fast and Reliable
```bash
# Install
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Basic usage
subfinder -d example.com

# Verbose output
subfinder -d example.com -v

# Save output
subfinder -d example.com -o subdomains.txt

# Use all sources
subfinder -d example.com -all

# Multiple domains
subfinder -dL domains.txt -o results.txt

# JSON output
subfinder -d example.com -oJ -o results.json

# Silent mode (only subdomains, no banner)
subfinder -d example.com -silent
```

### DNSx — DNS Validation
```bash
# Install
go install -v github.com/projectdiscovery/dnsx/cmd/dnsx@latest

# Resolve subdomains from subfinder
subfinder -d example.com -silent | dnsx -silent

# Get IP addresses too
subfinder -d example.com -silent | dnsx -a -resp

# Check for wildcard DNS
dnsx -d example.com -wc

# Get all record types
echo "example.com" | dnsx -a -aaaa -cname -mx -txt -resp
```

### MassDNS — Ultra-Fast Brute Force
```bash
# Install
git clone https://github.com/blechschmidt/massdns.git
cd massdns
make

# Generate subdomain wordlist
cat wordlist.txt | \
  sed 's/$/.example.com/' > targets.txt

# Run massdns
./bin/massdns -r resolvers.txt -t A targets.txt > results.txt

# Parse results
grep "NOERROR" results.txt | cut -d' ' -f1 | sed 's/\.$//'
```

### Gobuster DNS Mode
```bash
# DNS subdomain brute forcing
gobuster dns \
  -d example.com \
  -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt \
  -t 50 \
  -v

# Show IP addresses
gobuster dns \
  -d example.com \
  -w wordlist.txt \
  -i    ← show IP addresses
```

### FFUF for DNS
```bash
# Subdomain fuzzing with FFUF
ffuf -u http://FUZZ.example.com \
  -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc 200,301,302,403 \
  -v
```

---

## Method 3 — Zone Transfer (AXFR)

```bash
# Step 1 — Find nameservers
dig NS example.com
nslookup -type=NS example.com

# Step 2 — Attempt zone transfer
dig axfr @ns1.example.com example.com
dig axfr @ns2.example.com example.com

# Using host command
host -t AXFR example.com ns1.example.com

# Automated with dnsrecon
dnsrecon -d example.com -t axfr
```

---

## Method 4 — Virtual Host Discovery

Some subdomains only respond to specific **Host headers**:
```bash
# Using FFUF for virtual host discovery
ffuf -u http://10.10.10.10 \
  -H "Host: FUZZ.example.com" \
  -w /usr/share/wordlists/SecLists/Discovery/DNS/subdomains-top1million-5000.txt \
  -mc 200,301,302,403 \
  -fs 0    ← filter by response size

# Using gobuster vhost mode
gobuster vhost \
  -u http://example.com \
  -w subdomains.txt \
  -t 50
```

---

## Complete Automated Workflow

```bash
#!/bin/bash
TARGET=$1
OUTPUT_DIR="./recon_$TARGET"
mkdir -p $OUTPUT_DIR

echo "[+] Starting subdomain enumeration for: $TARGET"
echo "================================================"

# 1. Certificate Transparency
echo "[*] Checking certificate transparency..."
curl -s "https://crt.sh/?q=%.${TARGET}&output=json" | \
  python3 -c "
import json,sys
try:
    data=json.load(sys.stdin)
    [print(e['name_value']) for e in data]
except: pass
" | sort -u > $OUTPUT_DIR/crt_sh.txt
echo "[+] crt.sh: $(wc -l < $OUTPUT_DIR/crt_sh.txt) subdomains"

# 2. Subfinder
echo "[*] Running subfinder..."
subfinder -d $TARGET -silent -o $OUTPUT_DIR/subfinder.txt 2>/dev/null
echo "[+] Subfinder: $(wc -l < $OUTPUT_DIR/subfinder.txt) subdomains"

# 3. Sublist3r
echo "[*] Running Sublist3r..."
python3 ~/tools/Sublist3r/sublist3r.py \
  -d $TARGET -o $OUTPUT_DIR/sublist3r.txt -n 2>/dev/null
echo "[+] Sublist3r: $(wc -l < $OUTPUT_DIR/sublist3r.txt) subdomains"

# 4. Amass passive
echo "[*] Running Amass (passive)..."
amass enum -passive -d $TARGET \
  -o $OUTPUT_DIR/amass.txt 2>/dev/null
echo "[+] Amass: $(wc -l < $OUTPUT_DIR/amass.txt) subdomains"

# 5. Zone transfer attempt
echo "[*] Attempting zone transfer..."
for ns in $(dig +short NS $TARGET); do
  dig axfr @$ns $TARGET >> $OUTPUT_DIR/axfr.txt 2>/dev/null
done

# 6. Combine and deduplicate
echo "[*] Combining results..."
cat $OUTPUT_DIR/*.txt | \
  grep -v "^#\|^;\|^$" | \
  sed 's/\.$//g' | \
  grep -E "^[a-zA-Z0-9].*\.$TARGET$|^[a-zA-Z0-9].*\.${TARGET}" | \
  sort -u > $OUTPUT_DIR/all_subdomains.txt

echo "[+] Total unique subdomains: $(wc -l < $OUTPUT_DIR/all_subdomains.txt)"

# 7. DNS resolution and alive check
echo "[*] Checking which subdomains are alive..."
cat $OUTPUT_DIR/all_subdomains.txt | \
  dnsx -silent -a -resp > $OUTPUT_DIR/resolved.txt
echo "[+] Alive: $(wc -l < $OUTPUT_DIR/resolved.txt) subdomains"

# 8. HTTP probing
echo "[*] Probing for HTTP/HTTPS services..."
cat $OUTPUT_DIR/resolved.txt | \
  cut -d' ' -f1 | \
  httpx -silent -status-code -title \
  > $OUTPUT_DIR/http_alive.txt
echo "[+] HTTP services: $(wc -l < $OUTPUT_DIR/http_alive.txt)"

echo ""
echo "================================================"
echo "[+] Results saved to: $OUTPUT_DIR/"
echo "[+] Final alive HTTP services:"
cat $OUTPUT_DIR/http_alive.txt
```

---

## Best Wordlists for DNS Brute Forcing

```bash
# SecLists (most comprehensive)
git clone https://github.com/danielmiessler/SecLists

# Best DNS wordlists from SecLists:
SecLists/Discovery/DNS/subdomains-top1million-5000.txt      ← fast
SecLists/Discovery/DNS/subdomains-top1million-20000.txt     ← medium
SecLists/Discovery/DNS/subdomains-top1million-110000.txt    ← thorough
SecLists/Discovery/DNS/dns-Jhaddix.txt                      ← comprehensive
SecLists/Discovery/DNS/fierce-hostlist.txt                  ← classic

# Build custom wordlist from target
# Look for naming patterns in found subdomains:
# api-v1, api-v2, api-v3 → try api-v4, api-v5
# us-east, us-west → try eu-west, ap-east
# app1, app2 → try app3, app4
```

---

## Post-Discovery — What To Do With Subdomains

### 1. HTTP Probing with HTTPx
```bash
# Find which subdomains serve web content
cat subdomains.txt | httpx -silent \
  -status-code \
  -title \
  -tech-detect \
  -follow-redirects \
  -o web_alive.txt

# Output:
# https://admin.example.com [200] [Admin Panel] [WordPress]
# https://dev.example.com [200] [Dev Server] [PHP/7.4]
# https://api.example.com [401] [API Gateway] [nginx]
```

### 2. Screenshot with Aquatone / Gowitness
```bash
# Take screenshots of all discovered web services
cat subdomains.txt | aquatone -out screenshots/

# Using gowitness
gowitness file -f subdomains.txt -P screenshots/
```

### 3. Technology Detection
```bash
# Identify technologies on each subdomain
whatweb --input-file=subdomains.txt --log-brief=tech.txt

# Using webanalyze
webanalyze -hosts subdomains.txt -output json
```

### 4. Subdomain Takeover Check
```bash
# Check for subdomain takeover vulnerabilities
# Happens when CNAME points to unclaimed service

# Using subjack
subjack -w subdomains.txt -t 100 -o takeover.txt

# Using nuclei
nuclei -l subdomains.txt -t takeovers/

# Manual check:
dig CNAME dev.example.com
# If points to: something.github.io or something.s3.amazonaws.com
# And that resource doesn't exist → TAKEOVER POSSIBLE!
```

---

## Subdomain Takeover — Special Topic

```bash
# Common services vulnerable to takeover:
GitHub Pages      → *.github.io
Amazon S3         → *.s3.amazonaws.com
Azure             → *.azurewebsites.net
Heroku            → *.herokuapp.com
Shopify           → *.myshopify.com
Fastly            → *.fastly.net
Sendgrid          → em.example.com → u1234.wl.sendgrid.net

# Detection:
dig CNAME sub.example.com
# → sub.example.com CNAME something.github.io

# Verify:
curl -s https://sub.example.com
# → "There isn't a GitHub Pages site here"
# This means → VULNERABLE TO TAKEOVER!

# Severity: High → can serve malicious content
#           on trusted domain
```

---

## Online Tools & Resources

```
Passive DNS / Discovery:
├── https://dnsdumpster.com           ← free, visual maps
├── https://securitytrails.com        ← DNS history
├── https://crt.sh                    ← certificate transparency
├── https://virustotal.com            ← passive DNS
├── https://shodan.io                 ← internet scanning
├── https://censys.io                 ← similar to Shodan
├── https://buckets.grayhatwarfare.com ← S3 + subdomains
└── https://spyse.com                 ← OSINT platform

Subdomain Takeover:
├── https://github.com/EdOverflow/can-i-take-over-xyz
└── https://github.com/indianajson/can-i-take-over-dns
```

---

## Bug Bounty Value Guide

| Finding | Severity | Payout |
|---|---|---|
| Subdomain with outdated software → RCE | Critical 🔴 | $5,000–$50,000 |
| Subdomain takeover | High 🟠 | $500–$5,000 |
| Dev/staging subdomain with data | High 🟠 | $1,000–$10,000 |
| Admin panel exposed on subdomain | High 🟠 | $1,000–$10,000 |
| API subdomain with broken auth | High–Critical 🔴 | $2,000–$30,000 |
| Jenkins/CI-CD subdomain exposed | Critical 🔴 | $5,000–$50,000 |

---

## Key Takeaway

> Subdomain enumeration is like finding **all the doors and windows** of a building before deciding which one to enter. The main entrance (www) is always well-guarded, but a forgotten **side door** (dev.example.com, old.example.com) may be left wide open. Always enumerate subdomains thoroughly — the Panama Papers proved that one overlooked subdomain can bring down an **entire organization**. Use **multiple methods** in combination — no single tool finds everything! 🛡️
