# Google Search Operators — Complete List (2026)

Semua operator yang berfungsi di Google per 2026, plus syntax rules wajib.

## Core Operators (Reliable)

Operator-operator ini **stabil** — berfungsi konsisten dan menjadi backbone semua dork query.

### Filter Dasar

| Operator | Syntax | Fungsi | Contoh |
|---|---|---|---|
| `" "` | `"exact phrase"` | Exact phrase match. Cegah substitusi sinonim | `"nginx config"` |
| `OR` / `\|` | `term1 OR term2` | Either term (harus UPPERCASE) | `docker OR podman` |
| `-` | `-term` | Exclude term. Bisa dikombinasi dengan operator lain | `jaguar -car` |
| `*` | `"best * language"` | Wildcard — 1 kata di dalam quoted phrase | `"top * tools"` |
| `( )` | `(A OR B) C` | Grouping untuk Boolean logic kompleks | `(linux OR unix) security` |
| `..` | `$200..$500` | Numeric range. Paling akurat dengan `$` prefix | `laptop $500..$1000` |

### Domain & File

| Operator | Syntax | Fungsi | Contoh |
|---|---|---|---|
| `site:` | `site:example.com` | Batasi hasil ke domain/subdomain/path/TLD | `site:.gov security` |
| `filetype:` | `filetype:pdf` | Hanya tipe file spesifik (pdf, doc, xls, pptx, sql, log, env, dll.) | `filetype:sql "password"` |
| `ext:` | `ext:pdf` | Alias untuk `filetype:` — perilaku identik | `ext:xlsx budget` |

### Title, URL, Body

| Operator | Syntax | Fungsi | Contoh |
|---|---|---|---|
| `intitle:` | `intitle:keyword` | Keyword di HTML title tag | `intitle:"index of"` |
| `allintitle:` | `allintitle:word1 word2` | **Semua** kata di title. JANGAN gabung dengan operator lain | `allintitle:admin login` |
| `inurl:` | `inurl:keyword` | Keyword di URL | `inurl:admin` |
| `allinurl:` | `allinurl:word1 word2` | **Semua** kata di URL | `allinurl:wp-content plugins` |
| `intext:` | `intext:keyword` | Keyword di body halaman | `intext:"DB_PASSWORD"` |
| `allintext:` | `allintext:word1 word2` | **Semua** kata di body | `allintext:username password` |

### Date, News, Images

| Operator | Syntax | Fungsi | Status |
|---|---|---|---|
| `before:` | `before:2025-06-01` | Hasil sebelum tanggal (YYYY-MM-DD atau YYYY) | **BETA** (sejak April 2019) |
| `after:` | `after:2024-01-01` | Hasil setelah tanggal | **BETA** (sejak April 2019) |
| `define:` | `define:OSINT` | Definisi kamus | Stable |
| `source:` | `source:reuters` | Google News — batasi ke publikasi spesifik | Stable |
| `imagesize:` | `imagesize:1920x1080` | Halaman dengan gambar dimensi spesifik | Stable |
| `src:` | `src:URL` | Halaman yang merujuk URL gambar tertentu (Google Images) | Stable |

## "Unreliable" Operators

Secara teknis masih berfungsi, tapi **hasil tidak konsisten**:

| Operator | Fungsi | Masalah |
|---|---|---|
| `AROUND(X)` | Kata berjarak X kata. `term1 AROUND(5) term2` | Sering mengabaikan proximity constraint |
| `@` | Social media | Hasil mirip query normal — tidak bisa diandalkan |
| `#` | Hashtag | Sama — hasil tidak spesifik |
| `inanchor:` | Cari di anchor text link | Data tidak lengkap — deprecated di Google sejak 2017 |
| `allinanchor:` | Semua kata di anchor text | Sama |
| `daterange:` | Range tanggal (Julian format) | Digantikan `before:` / `after:` |

## Syntax Rules (Wajib)

1. **NO SPACE** antara operator dan parameter — `site:example.com` ✓, `site: example.com` ✗
2. **OR + AND HARUS UPPERCASE** — lowercase dianggap kata biasa
3. **`allin*` family** (`allintitle:`, `allinurl:`, `allintext:`) — JANGAN gabung dengan operator lain dalam satu query
4. **Query cap**: 32 keywords, 2,048 karakter per keyword
5. **Stack operators** — bisa gabung multiple operator: `site:.gov filetype:pdf intitle:"annual report"`

## Operator Non-Google

### Bing Exclusive

| Operator | Fungsi |
|---|---|
| `ip:` | Map semua konten di IP spesifik — infra mapping |
| `linkfromdomain:` | Outbound link analysis — semua situs yang di-link domain target |
| `contains:` | Halaman mengandung link ke tipe file spesifik (mp3, dll.) |
| `feed:` | Temukan RSS/Atom feeds |
| `hasfeed:` | Halaman yang punya RSS feed |
| `near:N` | Proximity — lebih akurat dari `AROUND(X)` Google |
| `norelax:` | Paksa inklusi kata yang biasanya di-drop Bing |
| `language:` | Filter bahasa |
| `loc:` | Filter lokasi |

### Yandex Exclusive

| Operator | Fungsi |
|---|---|
| `rhost:` | Reverse host search — temukan halaman hosted di domain (pakai Yandex crawl data) |
| `date:` | Date filtering kaya syntax (exact, range, comparison) |
| `mime:` | Eq. `filetype:` — lebih konsisten + support MIME types |
| `title:` | Eq. `intitle:` |
| `host:` | Hostname-specific search |
| `domain:` | Filter by TLD |
| `!` | Sebelum kata — cegah morphological variations |
| `[ ]` | Preserve word order |
| `~` | Single: exclude from sentence. `~~` Double: full NOT |

### Perplexity AI

AI search engine pertama yang support structured operators: `site:`, `filetype:`, `inurl:`, `before:`, `after:` — bisa digabung dengan natural language prompt.

### DuckDuckGo

Disabled most operators April 2023. Hanya restore sebagian. `site:` + `filetype:` + beberapa basic — hasil tidak konsisten.

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [Google Search Central Docs](https://developers.google.com/search/docs)
- [DorkPlus Cheat Sheet 2026](https://dorkplus.com/blog/google-dork-operators-cheat-sheet-2026)
