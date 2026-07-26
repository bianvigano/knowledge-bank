# Google Dorking — Overview

**Google Dorking** (alias Google Hacking) adalah teknik menggunakan **advanced search operators** untuk menemukan informasi spesifik yang terindeks Google — termasuk file sensitif, direktori terbuka, kredensial bocor, dan miskonfigurasi server.

Nama "dork" bukan hinaan — berasal dari slang hacker untuk seseorang yang tidak sadar mengekspos data sensitif. Istilah ini dipopulerkan oleh **Johnny Long** melalui Google Hacking Database (GHDB) tahun 2002.

## Kenapa Penting?

| Use Case | Contoh |
|---|---|
| **OSINT** (Open Source Intelligence) | Investigasi target, profiling perusahaan/orang |
| **Bug Bounty / Pentest** | Temukan file ekspos, admin panel, kredensial |
| **Defensive Security** | Audit domain sendiri — apa yang bocor ke Google? |
| **Research** | Cari dokumen spesifik (PDF laporan, Excel data, dll.) |
| **Reconnaissance** | Subdomain, karyawan, teknologi stack target |

## Konsep Inti

- **Search Operator** — prefix/filter spesial di query Google (contoh: `site:`, `filetype:`, `intitle:`)
- **Dork** — kombinasi operator + keyword untuk target spesifik (contoh: `site:.gov filetype:pdf "annual report"`)
- **GHDB (Google Hacking Database)** — database ribuan dork curated, di-maintain Exploit-DB
- **Automated Dorking** — tools seperti Pagodo menjalankan dork otomatis (hati-hati: Google memblokir automated queries)
- **SearchGuard** — sistem anti-bot Google, deployed Januari 2025

## Status 2026

- **~25 operator** masih berfungsi di Google
- **12+ operator** dihapus sejak 2010 — termasuk `cache:` (2024) dan `related:` (2023)
- **0 operator baru** ditambahkan sejak 2019
- **43% organisasi** masih mengekspos data sensitif yang bisa ditemukan lewat dorking
- **74% temuan** dari automated dorking rated high severity

## Legalitas

Dorking manual (ketik query di Google) **bukan aktivitas ilegal**. Semua data yang ditemukan adalah data publik yang sengaja/tidak sengaja terindeks Google.

**Yang ilegal**: mengakses sistem tanpa izin, mengeksploitasi kredensial yang ditemukan, mencuri data — walaupun diakses via Google.

Setiap kasus kriminal yang diketahui **menuntut aksi setelah dorking**, bukan query pencariannya sendiri.

## Tools Terkait

- **Google Hacking Database** — exploit-db.com/google-hacking-database
- **Pagodo** — automated GHDB query executor (pasif, rate-limited)
- **Maltego** — OSINT platform dengan transform dorking
- **Shodan / Censys** — search engine untuk device/server (separate dari Google)
- **Perplexity AI** — AI search engine pertama yang support `site:`, `filetype:`, `before:`, `after:`

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [Google Dorks Cheat Sheet — StationX](https://www.stationx.net/google-dorks-cheat-sheet/)
- [Exploit-DB Google Hacking Database](https://exploit-db.com/google-hacking-database)
- [Imperva: What is Google Dorking](https://www.imperva.com/learn/application-security/google-dorking-hacking/)
