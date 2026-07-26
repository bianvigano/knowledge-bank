# Google Dorking — OSINT Examples & Patterns

Dork patterns real-world untuk investigasi, pentest, dan bug bounty. Semua untuk **defensive security, authorized testing, dan edukasi**.

> **Disclaimer**: Akses sistem tanpa izin itu ilegal — walaupun ditemukan lewat Google.

## Directory Listings / File Exposure

### Open Directory Index

Menemukan direktori yang ter-indeks tanpa proteksi:

```
intitle:"index of" "parent directory"
```

Cari spesifik — backup:

```
intitle:"index of" "backup"
```

Cari direktori dengan file `wp-config`:

```
intitle:"index of" "wp-config.php"
```

### Environment Files (.env)

File `.env` sering mengandung database credentials + API keys:

```
filetype:env "DB_PASSWORD" | "API_KEY" | "SECRET"
```

`.env` di server production:

```
intitle:"index of" ".env"
```

### Database Backups / SQL Dumps

```
filetype:sql "password" | "pass"
filetype:sql intext:"wp_users"
filetype:sql "INSERT INTO" site:example.com
```

Backup files langsung:

```
filetype:bak inurl:backup
intitle:"index of" "database.sql"
```

### Config Files

```
filetype:conf "password" | "passwd"
filetype:config inurl:web.config
filetype:ini "password"
filetype:yaml "api_key" | "token"
```

### WordPress Specific

Database credentials:

```
inurl:wp-config.php intext:"DB_PASSWORD"
```

Backup wp-config:

```
filetype:txt inurl:wp-config
```

Plugin/theme exposure:

```
site:example.com inurl:wp-content/plugins
site:example.com inurl:wp-content/themes
```

### Cloud Storage

Amazon S3 public buckets:

```
site:s3.amazonaws.com "confidential"
site:s3.amazonaws.com "internal"
```

Trello boards with credentials:

```
site:trello.com "password" "admin" "production"
```

Google Drive shared links:

```
site:drive.google.com "confidential" filetype:pdf
```

## Reconnaissance / Profiling

### Subdomain Discovery

Subdomain enumeration iterative — hapus known subdomains bertahap:

```
site:*.example.com -www -mail -blog -dev
```

Setelah tambahan ditemukan:

```
site:*.example.com -www -mail -blog -dev -api -cdn
```

### Employee / Personnel

LinkedIn — role spesifik:

```
site:linkedin.com/in "CISO" "company name"
site:linkedin.com/in "engineer" "company name"
```

GitHub — developer profiles:

```
site:github.com "company.com" "engineer"
```

### Technology Stack

WordPress detection:

```
site:example.com inurl:wp-content
```

API documentation:

```
intitle:"Swagger UI" site:example.com
site:example.com inurl:api-docs
```

Server headers:

```
intitle:"Apache HTTP Server" site:example.com
intitle:"Welcome to nginx" site:example.com
```

Login panels:

```
intitle:"admin" inurl:login
intitle:"dashboard" inurl:admin
intitle:"phpMyAdmin" inurl:index.php
site:example.com inurl:login
```

Version disclosure:

```
intext:"Powered by WordPress" site:example.com
intext:"vBulletin" site:example.com
```

### Cross-Platform Identity Linking

Cari username di berbagai platform:

```
"username123" site:github.com | site:reddit.com | site:twitter.com
"username123" site:gitlab.com | site:stackoverflow.com
```

### Email Discovery

```
site:example.com "@gmail.com" | "@yahoo.com"
site:example.com intext:"@example.com" filetype:csv
```

## Government / Public Records

### Government Documents

```
filetype:pdf site:.gov "annual report" after:2024-01-01
site:.mil filetype:pdf "sensitive but unclassified"
filetype:pdf site:.gov "FOIA" "response"
```

### SEC Filings

```
site:sec.gov "company name" filetype:pdf
site:sec.gov intitle:"10-K" | intitle:"10-Q" "company name"
```

### Educational (.edu) Resources

```
site:.edu filetype:pdf "thesis" | "dissertation"
site:.edu "student" "phone number" filetype:xlsx
```

## Credential Exposure

### GitHub Leaks

```
site:github.com "example.com" ("API_KEY" | "SECRET_KEY" | "password")
site:github.com "BEGIN RSA PRIVATE KEY"
site:github.com "example.com" "DB_PASSWORD"
```

### Paste Sites

```
site:pastebin.com "password" "example.com"
site:justpaste.it "admin" "password"
```

### Generic Password Files

```
filetype:txt inurl:"password"
filetype:csv intext:"email" "password"
intitle:"index of" "passwd"
intitle:"index of" "htpasswd"
```

### FTP / Backup / Log

```
intitle:"index of" "ftp"
intitle:"index of" inurl:log
filetype:log "password" | "username"
```

## Cameras & IoT

### Unsecured Cameras

```
inurl:"view/index.shtml"
intitle:"Live View / - AXIS"
intitle:"Network Camera NetworkCamera"
inurl:guestimage.html
```

### Printer / Network Devices

```
intitle:"HP LaserJet" inurl:device
inurl:"/cgi-bin/status" intitle:"printer"
```

## Financial / Sensitive Data

### Invoices & Statements

```
filetype:pdf "invoice" | "statement" intext:"confidential"
filetype:xlsx "budget" "confidential"
```

### Credit Card Patterns (Partial Match)

```
filetype:txt intext:"4111"
filetype:log intext:"cvv" | intext:"ccv"
```

## Dork Pattern Structure

Setiap dork mengikuti formula:

```
[scope] + [type] + [keyword]

scope:   site:example.com, site:.gov, site:*.target.com
type:    filetype:pdf, intitle:"...", inurl:..., intext:"..."
keyword: "confidential", "password", "admin"
```

Contoh gabungan:

```
site:example.com filetype:pdf intext:"confidential"
```

## Query Syntax Best Practices

1. **Start specific** → sempitkan → jika tidak ada hasil, perluas
2. **Quote exact strings** — `"error message"`, `"DB_PASSWORD"`
3. **Kombinasi operator** — maks 3-4 per query, lebih dari itu hasil buruk
4. **Exclude noise** — `-site:github.com` untuk filter kode repositori
5. **Iterate** — ganti keyword, tambah/ubah scope, ganti filetype

## Google Hacking Database (GHDB)

GHDB di Exploit-DB mengorganisir ribuan dork ke 14 kategori:

| Kategori | Isi |
|---|---|
| Footholds | Entry point untuk akses |
| Files Containing Usernames | File dengan username |
| Sensitive Directories | Direktori sensitif |
| Web Server Detection | Deteksi versi server |
| Vulnerable Files | File vulnerable |
| Vulnerable Servers | Server vulnerable |
| Error Messages | Pesan error (info disclosure) |
| Files Containing Juicy Info | File dengan info berharga |
| Files Containing Passwords | File dengan password |
| Sensitive Online Shopping Info | Data e-commerce |
| Network or Vulnerability Data | Data jaringan / vuln |
| Pages Containing Login Portals | Halaman login |
| Various Online Devices | Perangkat online |
| Advisories and Vulnerabilities | Advisory keamanan |

Akses: [exploit-db.com/google-hacking-database](https://exploit-db.com/google-hacking-database)

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [StationX Google Dorks Cheat Sheet](https://www.stationx.net/google-dorks-cheat-sheet/)
- [Exploit-DB GHDB](https://exploit-db.com/google-hacking-database)
- [Splunk: Google Dorking for Cybersecurity](https://www.splunk.com/en_us/blog/learn/google-dorking.html)
