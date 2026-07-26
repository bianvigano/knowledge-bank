# Deprecated Google Search Operators

Google removes operators that serve power users or could expose sensitive data. Timeline removal, detail, dan replacement.

## Deprecation Timeline

| Operator | Function | Year Removed | Keterangan |
|---|---|---|---|
| `cache:` | Tampilkan versi tersimpan Google | **2024** | Cache links hilang dari snippets Dec 2023–Jan 2024. Danny Sullivan konfirmasi removal Mar 2024. Documentation removed Sep 17, 2024. **Replacement**: Wayback Machine |
| `related:` | Cari situs mirip | **2023** | Removed from Search Central docs Jul 18, 2023. Sullivan: "hasn't really worked that well for some time" |
| `info:` / `id:` | Tampilkan metadata halaman | **2017** | Sekarang redirect ke normal search result untuk URL |
| `link:` | Cari halaman yang link ke URL | **2017** | Officially killed. Mungkin return sampled/inaccurate results |
| `~` | Include sinonim | **2013** | Removed karena Google sekarang auto-include sinonim |
| `+` | Force exact match | **2011** | Deprecated saat Google+ launch. Tidak direstore setelah Google+ mati 2019 |
| `phonebook:` | Cari nomor telepon | **2010** | Removed untuk privacy |
| `blogurl:` | Cari blog untuk domain | **2011** | Deprecated with Google Blog Search |
| `inpostauthor:` | Cari penulis post blog | **2011** | Deprecated with Google Blog Search |
| `inposttitle:` | Cari judul post blog | **2011** | Deprecated with Google Blog Search |

## Total: 12+ operator dihapus sejak 2010

Google tidak menambahkan operator baru sejak 2019. Polanya jelas: operator yang melayani power user atau mengekspos data sensitif dihapus, diganti pengalaman AI-driven yang lebih simpel.

## `cache:` — Kerugian Terbesar untuk OSINT

`cache:` adalah cornerstone technique untuk OSINT — melihat halaman yang dihapus atau dimodifikasi.

**Replacement**: [Wayback Machine](https://web.archive.org/) — coverage tidak konsisten, tapi satu-satunya alternatif gratis. Google sekarang menampilkan link Wayback Machine di search results sebagai ganti cache.

## Operator Berstatus "BETA" Sejak 2019

`before:` dan `after:` tetap **BETA** sejak April 2019 — lebih dari 6 tahun tanpa graduate ke stable.

Format yang harus: `YYYY-MM-DD` atau `YYYY`. Hasil tidak konsisten karena website handle date metadata secara berbeda. Built-in filter Google (Tools → Custom Date Range) sering lebih reliable.

## `daterange:`

Technical masih berfungsi, tapi perlu **Julian date format** (tidak praktis). Digantikan `before:`/`after:`.

## Operator "Zombie" — Masuk Guide 2024-2025 Tapi Nyatanya Mati

Banyak guide populer terbit 2024-2025 **masih list `cache:` dan `related:` sebagai berfungsi** — ini salah.

| Operator | Status di Guide Populer | Status Sesungguhnya |
|---|---|---|
| `cache:` | "Working" | Dead (2024) |
| `related:` | "Working" | Dead (2023) |
| `link:` | "Working" | Dead (2017), sampled results |
| `info:` | "Working" | Redirect ke normal search |
| `+` | "Force exact" | Dead (2011) |

Saat baca guide dorking, cek tanggal publikasi. Jika sebelum 2024, verifikasi operator yang di-listing.

## Masa Depan

Trend penurunan operator akan terus berlanjut. Google berinvestasi di AI-driven search (AI Overviews, AI Mode) dengan target 2B+ user — bukan di operator untuk power user. SearchGuard (Jan 2025) dan lawsuit Google vs SerpApi (Dec 2025) menandakan Google makin agresif memblokir automated queries.

Untuk investasi jangka panjang: kuasai multi-engine proficiency — Google untuk index size, Bing untuk `ip:` + `linkfromdomain:`, Yandex untuk facial recognition + konten Rusia.

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [Danny Sullivan (Google Search Liaison) on Twitter](https://twitter.com/searchliaison)
- [Google Search Central Documentation](https://developers.google.com/search/docs)
- [Wayback Machine](https://web.archive.org/)
