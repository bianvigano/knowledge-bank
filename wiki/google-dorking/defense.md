# Defense Against Google Dorking

Cara melindungi organisasi dari exposure via search engine dorking. Fokus: mencegah data sensitif terindeks Google.

## Prinsip Dasar

Google hanya bisa menampilkan data yang **bisa di-crawl dan tidak dilindungi**. Defense = pastikan data sensitif tidak bisa diakses Googlebot.

## Checklist Defense

### 1. robots.txt — First Line of Defense

Block direktori sensitif:

```
User-agent: *
Disallow: /admin/
Disallow: /backup/
Disallow: /private/
Disallow: /config/
Disallow: /.env
Disallow: /wp-config.php
Disallow: /phpmyadmin/
Disallow: /db/
```

**Peringatan**: `robots.txt` adalah "suggestion", bukan enforcement. Crawler malicious bisa mengabaikan. JANGAN cantumkan path sensitif terlalu spesifik — itu seperti memberi peta ke penyerang.

```
# BURUK — memberi tahu penyerang path sensitif:
Disallow: /secret-admin-panel/
Disallow: /database-backup-2025/

# BAIK — pattern-based:
Disallow: /admin/
Disallow: /backup/
```

### 2. Authentication Everywhere

Setiap halaman admin, dashboard, internal tool, dan direktori sensitif **WAJIB** di balik autentikasi. Googlebot tidak bisa login — sehingga tidak bisa index konten di balik login.

### 3. `.htaccess` / Nginx Access Control

Apache:

```apache
<FilesMatch "\.(env|sql|bak|zip|tar|gz)$">
    Require all denied
</FilesMatch>
```

Nginx:

```nginx
location ~* \.(env|sql|bak|zip)$ {
    deny all;
    return 404;
}
```

### 4. Directory Listing OFF

Pastikan directory listing (indexes) **disabled**:

Apache:

```apache
Options -Indexes
```

Nginx (default `/etc/nginx/nginx.conf`):

```nginx
autoindex off;
```

### 5. No Sensitive Files in Web Root

- File `.env`, `database.sql`, `backup.zip`, `config.yml` **JANGAN PERNAH** berada di document root
- Database backup di luar `/var/www/` — simpan di `/var/backups/` atau remote storage
- File konfigurasi di luar web root, di-include via `require` atau `import`

### 6. Use `.gitignore`-style Blocking

Nginx block common sensitive patterns:

```nginx
location ~ /\. {
    deny all;
    return 404;
}

location ~* (wp-config\.php|\.env|composer\.json|package\.json|Dockerfile) {
    deny all;
    return 404;
}
```

### 7. Google Search Console — Remove URLs

Jika sudah terindeks: **Google Search Console → Removals → New Request** — hapus URL dari index sementara (6 bulan). Gunakan waktu ini untuk fix proteksi.

### 8. Meta Tags — No Index

Untuk halaman yang tidak boleh di-index:

```html
<meta name="robots" content="noindex, nofollow">
```

Atau HTTP header:

```
X-Robots-Tag: noindex, nofollow
```

### 9. Regular Self-Audit

Jalankan dork di domain sendiri secara berkala:

```
site:yourdomain.com filetype:env
site:yourdomain.com filetype:sql
site:yourdomain.com "index of"
site:yourdomain.com intitle:"index of"
site:yourdomain.com intext:"DB_PASSWORD"
site:yourdomain.com inurl:admin
site:yourdomain.com filetype:bak
site:yourdomain.com filetype:zip | filetype:tar
```

Ini **bukan ilegal** — audit domain sendiri. Gunakan hasil untuk memperbaiki exposure sebelum penyerang menemukannya.

### 10. Automated Monitoring

Tools untuk monitoring exposure:

- **Google Search Console** — notifikasi security issues
- **Shodan Monitor** — deteksi service yang terekspos
- **Splunk + custom alerts** — monitoring log untuk akses mencurigakan
- **Burp Suite / OWASP ZAP** — scanning rutin
- **Custom dork scripts** — cron job untuk cek domain sendiri (perhatikan rate limit)

## Incident Response — Jika Data Sudah Bocor

1. **Hapus file** dari server **segera**
2. **Google Search Console → Removals** — request penghapusan dari index (berlaku 6 bulan)
3. **Rotate semua credential** yang terekspos (password, API keys, tokens)
4. **Audit log** — cek siapa yang mengakses file tersebut
5. **Perbaiki root cause** — kenapa file bisa diakses tanpa autentikasi
6. **Google tidak bisa dihubungi untuk penghapusan manual** — hanya bisa via Search Console atau menunggu re-crawl alami

## Rate Limiting & SearchGuard

Google SearchGuard (Jan 2025) mendeteksi automated dorking:

- **~15-20 query/jam** per IP sebelum trigger CAPTCHA
- Detection signals: request frequency, IP reputation, browser fingerprinting, behavioral patterns
- Escalation: CAPTCHA → temporary block → IP ban

Jika penyerang bisa trigger SearchGuard, mereka harus switch ke manual query atau gunakan multi-engine. Ini memperlambat — tapi bukan menghentikan — mereka yang persistent.

## Yang Tidak Bisa Dilindungi Hanya dengan Technical Controls

Beberapa exposure tidak bisa dicegah secara teknis:

- **Postingan forum/Reddit** yang menyebutkan internal info
- **Paste sites** (Pastebin, JustPasteIt) — karyawan tidak sengaja paste kode/konfigurasi
- **GitHub public repos** — developer upload kredensial
- **LinkedIn profiles** — info karyawan untuk social engineering

Perlu **security awareness training** + **DLP (Data Loss Prevention)** + **monitoring paste sites**.

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [Google Search Console Help](https://support.google.com/webmasters/)
- [OWASP: Testing for Google Dorking](https://owasp.org/)
- [Splunk: Defending Against Google Dorking](https://www.splunk.com/en_us/blog/learn/google-dorking.html)
