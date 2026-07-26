# Google Dorking

Teknik menggunakan advanced search operators untuk menemukan informasi spesifik via Google dan search engine lain. Dipopulerkan oleh Johnny Long (2002) lewat Google Hacking Database.

## Halaman

- **[[google-dorking/overview]]** — Apa itu dorking, kenapa penting, konsep inti, legalitas, tools
- **[[google-dorking/operator-list]]** — Semua operator Google + Bing + Yandex + Perplexity AI (2026)
- **[[google-dorking/osint-examples]]** — Real-world dork patterns: file exposure, recon, credential leaks, cameras, GHDB categories
- **[[google-dorking/engine-comparison]]** — Cross-engine matrix: Google vs Bing vs Yandex vs DuckDuckGo vs Brave vs Yahoo
- **[[google-dorking/deprecated]]** — Operator yang dihapus Google (12+ sejak 2010) + timeline + replacement
- **[[google-dorking/defense]]** — Cara melindungi organisasi dari Google dorking exposure

## Quick Reference

| Operator | Fungsi |
|---|---|
| `site:example.com` | Batasi ke domain |
| `filetype:pdf` | Tipe file spesifik |
| `intitle:"index of"` | Keyword di title |
| `inurl:admin` | Keyword di URL |
| `intext:"password"` | Keyword di body |
| `before:2025-01-01` | Sebelum tanggal |
| `-term` | Exclude |
| `"exact phrase"` | Exact match |

## Sumber Utama

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [Exploit-DB Google Hacking Database](https://exploit-db.com/google-hacking-database)
