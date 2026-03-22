# DNS Zone Transfer (AXFR) 

---

## What is DNS?

Before diving into zone transfers, let's understand DNS fundamentals.

**DNS (Domain Name System)** is the internet's phone book — it translates human-readable domain names into IP addresses:
```
google.com  →  142.250.185.46
facebook.com  →  157.240.241.35
```

**DNS Record Types:**

| Record | Purpose | Example |
|---|---|---|
| `A` | Maps domain to IPv4 address | `example.com → 93.184.216.34` |
| `AAAA` | Maps domain to IPv6 address | `example.com → 2606:2800::1` |
| `MX` | Mail server for domain | `mail.example.com` |
| `CNAME` | Alias for another domain | `www → example.com` |
| `NS` | Name servers for domain | `ns1.example.com` |
| `TXT` | Text records (SPF, verification) | `"v=spf1 include:..."` |
| `PTR` | Reverse DNS (IP → domain) | `34.216.184.93 → example.com` |
| `SOA` | Start of Authority (zone info) | Admin email, serial number |
| `SRV` | Service location records | VoIP, messaging services |

---

## What is a DNS Zone?

A **DNS Zone** is a portion of the DNS namespace managed by a specific organization or administrator. For example:

```
Zone: example.com
Contains:
  example.com          A      93.184.216.34
  www.example.com      CNAME  example.com
  mail.example.com     A      93.184.216.50
  ftp.example.com      A      93.184.216.51
  dev.example.com      A      10.0.0.5        ← internal!
  admin.example.com    A      10.0.0.1        ← sensitive!
  vpn.example.com      A      10.0.0.2        ← sensitive!
```

The **zone file** is a text file containing all these DNS records.

---

## What is a Zone Transfer (AXFR)?

A **Zone Transfer** is the process of copying the entire DNS zone file from one DNS server to another. It uses the **AXFR** (Asynchronous Full Transfer Zone) protocol.

**Why it exists:**
- Organizations run **multiple DNS servers** for redundancy
- The **Primary (Master)** server holds the original zone file
- **Secondary (Slave)** servers need copies to answer queries
- Zone transfers keep all servers **synchronized**

```
Primary DNS Server          Secondary DNS Server
┌─────────────────┐         ┌─────────────────┐
│  Full Zone File │──AXFR──▶│  Copy of Zone   │
│  (all records)  │         │  File           │
└─────────────────┘         └─────────────────┘
```

---

## Why is it a Security Risk?

When zone transfers are **misconfigured** to allow requests from anyone (not just authorized secondary DNS servers), an attacker can:

1. Get a **complete map** of the entire domain
2. Discover **hidden subdomains** not publicly advertised
3. Find **internal IP addresses**
4. Identify **sensitive services** (admin panels, VPNs, dev servers)
5. Map the **attack surface** before launching further attacks

**Example of what an attacker could discover:**
```
dev.example.com       A  10.0.0.5    ← development server
staging.example.com   A  10.0.0.6    ← staging environment
admin.example.com     A  10.0.0.1    ← admin panel
vpn.example.com       A  10.0.0.2    ← VPN server
db.example.com        A  10.0.0.10   ← database server!
backup.example.com    A  10.0.0.11   ← backup server!
internal.example.com  A  192.168.1.1 ← internal network!
```

This is essentially a **free recon gift** — the entire infrastructure handed to an attacker on a silver platter! 🎁

---

## How to Perform a Zone Transfer

**Step 1 — Find the Name Servers:**
```bash
# Find NS records for target
nslookup -type=NS example.com

# OR using dig
dig NS example.com

# Result:
# example.com nameserver = ns1.example.com
# example.com nameserver = ns2.example.com
```

**Step 2 — Attempt Zone Transfer:**
```bash
# Using dig (most common method)
dig axfr @ns1.example.com example.com

# Using nslookup
nslookup
> server ns1.example.com
> set type=AXFR
> example.com

# Using host command
host -t AXFR example.com ns1.example.com

# Using fierce (automated)
fierce --domain example.com

# Using dnsrecon
dnsrecon -d example.com -t axfr
```

**Successful Zone Transfer Output:**
```
; <<>> DiG 9.16.1 <<>> axfr @ns1.example.com example.com
;; ANSWER SECTION:
example.com.        3600  IN  SOA   ns1.example.com. admin.example.com. ...
example.com.        3600  IN  NS    ns1.example.com.
example.com.        3600  IN  NS    ns2.example.com.
example.com.        3600  IN  A     93.184.216.34
www.example.com.    3600  IN  A     93.184.216.34
mail.example.com.   3600  IN  MX    10 mail.example.com.
admin.example.com.  3600  IN  A     10.0.0.1      ← found!
dev.example.com.    3600  IN  A     10.0.0.5      ← found!
vpn.example.com.    3600  IN  A     10.0.0.2      ← found!
```

**Failed (Properly Secured) Response:**
```
; Transfer failed.
;; AXFR query to ns1.example.com for example.com failed: REFUSED
```

---

## IXFR — Incremental Zone Transfer

Besides AXFR (full transfer), there is also **IXFR (Incremental Zone Transfer)**:

| | AXFR | IXFR |
|---|---|---|
| Transfer type | Full zone | Only changes since last update |
| Bandwidth | High | Low |
| Use case | Initial sync | Regular updates |
| Attack value | Very high | Medium |

```bash
# Attempt incremental zone transfer
dig ixfr @ns1.example.com example.com
```

---

## Tools for Zone Transfer & DNS Enumeration

**1. dig — Most Powerful:**
```bash
# Zone transfer
dig axfr @ns1.example.com example.com

# Get all record types
dig ANY example.com

# Get specific record type
dig MX example.com
dig TXT example.com
dig NS example.com

# Trace DNS resolution path
dig +trace example.com
```

**2. dnsrecon — Automated:**
```bash
# Full DNS recon including zone transfer attempt
dnsrecon -d example.com

# Zone transfer only
dnsrecon -d example.com -t axfr

# Brute force subdomains
dnsrecon -d example.com -t brt -D /usr/share/wordlists/subdomains.txt
```

**3. dnsenum — Comprehensive:**
```bash
dnsenum example.com
dnsenum --enum example.com
```

**4. fierce — Reconnaissance:**
```bash
fierce --domain example.com
fierce --domain example.com --subdomains-file wordlist.txt
```

**5. nmap DNS scripts:**
```bash
# Attempt zone transfer using nmap
nmap --script dns-zone-transfer --script-args dns-zone-transfer.domain=example.com -p 53 ns1.example.com

# DNS brute force
nmap --script dns-brute example.com
```

**6. Online Tools:**
- https://hackertarget.com/zone-transfer/ — online zone transfer test
- https://dnsdumpster.com/ — DNS recon and mapping
- https://viewdns.info/ — multiple DNS tools

---

## Real-World Attack Scenario

```
1. Attacker targets: megacorp.com

2. Find name servers:
   dig NS megacorp.com
   → ns1.megacorp.com
   → ns2.megacorp.com

3. Attempt zone transfer:
   dig axfr @ns1.megacorp.com megacorp.com

4. SUCCESS! Attacker discovers:
   dev.megacorp.com      → 10.5.0.10  (dev server)
   staging.megacorp.com  → 10.5.0.11  (staging)
   jenkins.megacorp.com  → 10.5.0.20  (CI/CD!)
   jira.megacorp.com     → 10.5.0.21  (project mgmt)
   vpn.megacorp.com      → 203.0.113.5 (VPN gateway)
   db-backup.megacorp.com → 10.5.0.50 (database backup!)

5. Attacker now targets:
   → jenkins (often has RCE vulnerabilities)
   → db-backup (contains sensitive data)
   → vpn (attempt credential stuffing)
```

---

## How to Prevent Zone Transfer Attacks

**1. Restrict AXFR to Authorized Servers Only:**

In **BIND (named.conf):**
```bash
zone "example.com" {
    type master;
    file "/etc/bind/db.example.com";
    
    # Only allow transfers to specific secondary servers
    allow-transfer { 
        192.168.1.2;    # ns2 IP only
        192.168.1.3;    # ns3 IP only
    };
};
```

**2. Use TSIG (Transaction Signature) Keys:**
```bash
# Generate TSIG key
tsig-keygen -a hmac-sha256 transfer-key

# Add to named.conf
key "transfer-key" {
    algorithm hmac-sha256;
    secret "base64encodedkey==";
};

zone "example.com" {
    allow-transfer { key "transfer-key"; };
};
```

**3. Use DNS over TLS / DNSSEC:**
- Encrypts DNS traffic
- Authenticates DNS responses
- Prevents tampering and eavesdropping

**4. Split-Horizon DNS:**
```
External DNS → only public records (www, mail)
Internal DNS → full zone with internal records
```
External users never see internal subdomains even if AXFR succeeds.

**5. Regular Auditing:**
```bash
# Test your own zone transfer security
dig axfr @your-nameserver yourdomain.com

# If it returns records → YOU ARE VULNERABLE! Fix immediately.
# If it returns REFUSED → you are properly secured ✅
```

---

## Bug Bounty & Pentesting Value

| Finding | Severity | Notes |
|---|---|---|
| Zone transfer allowed publicly | **High** 🟠 | Exposes full infrastructure |
| Zone transfer reveals internal IPs | **High** 🟠 | Major recon advantage |
| Zone transfer reveals sensitive subdomains | **Critical** 🔴 | If leads to further compromise |

**In a pentest report, finding an open zone transfer means:**
- Complete subdomain enumeration without brute forcing
- Internal network topology exposed
- Potential pivot points identified
- Significantly reduces time to compromise

---

## Key Takeaway

> DNS Zone Transfer is like asking someone for their **entire house blueprint** — every room, every door, every hidden passage. When misconfigured, it hands attackers a complete map of an organization's infrastructure in a single query. Always restrict AXFR to authorized servers only, and regularly test your own DNS configuration! 🛡️
