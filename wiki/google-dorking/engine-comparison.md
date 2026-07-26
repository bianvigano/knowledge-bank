# Search Engine Comparison — Operator Support Matrix

Cross-engine compatibility untuk 6 search engine utama yang relevan untuk OSINT dan dorking.

## Operator Support Matrix

| Operator | Google | Bing | DuckDuckGo | Yandex | Brave | Yahoo |
|---|---|---|---|---|---|---|
| `site:` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `filetype:` | ✅ | ✅ | ⚠️ | ❌ (`mime:`) | ✅ | ✅ |
| `intitle:` | ✅ | ✅ | ⚠️ | ❌ (`title:`) | ✅ | ✅ |
| `inurl:` | ✅ | ❌ | ⚠️ | ✅ | ❌ | ❌ |
| `intext:` | ✅ | ✅ (`inbody:`) | ❌ | ❌ | ✅ (`inbody:`) | ✅ |
| Proximity | ✅ `AROUND(X)` | ✅ `near:N` | ❌ | ❌ | ❌ | ✅ |
| Date Filter | ✅ `before:`/`after:` | ❌ (UI only) | ❌ (UI only) | ✅ `date:` | ❌ | ❌ |
| `" "` exact | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| `OR` | ✅ | ✅ | ✅ | ✅ `()` | ✅ | ✅ |
| `-` exclude | ✅ | ✅ | ⚠️ | ✅ `~~` | ✅ | ✅ |
| `*` wildcard | ✅ | ✅ | ❌ | ✅ | ❌ | ✅ |
| `..` range | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ |
| Language | ❌ | ✅ `language:` | ❌ | ✅ `lang:` | ✅ `lang:` | ✅ |
| Location | ❌ | ✅ `loc:` | ❌ | ❌ | ✅ `loc:` | ✅ |

**Key**: ✅ = berfungsi, ❌ = tidak didukung, ⚠️ = tidak konsisten / terbatas

## Note Per Engine

### Google
- Index paling besar
- `site:` satu-satunya operator yang didukung semua 6 engine
- `inurl:` masih berfungsi
- `cache:` removed 2024, `related:` removed 2023
- SearchGuard (Jan 2025) — deteksi ~15-20 query/jam trigger CAPTCHA

### Bing
- **5+ operator exclusive** yang Google tidak punya: `ip:`, `linkfromdomain:`, `contains:`, `feed:`, `hasfeed:`
- `inurl:` **tidak didukung** sejak 2007 (Microsoft suspended untuk cegah data mining)
- `near:N` proximity lebih akurat dari `AROUND(X)` Google
- `intext:` pakai syntax `inbody:`
- Yahoo Search powered by Bing sejak 2010 — inherit semua Bing operator

### Yandex
- **Raja reverse image search** — facial recognition AI, deteksi foto modifikasi
- **Deep index** konten Rusia dan Cyrillic yang Google nyaris tidak sentuh
- Operator unique: `rhost:` (reverse host), `date:` (rich syntax), `mime:`
- Morphological control: `!` (cegah variasi), `[ ]` (preserve order)
- Market share 66-74% di Rusia
- Dijual $5.3B (Juli 2024), tetap akses internasional
- Diblokir di Latvia, Ukraina

### DuckDuckGo
- Disabled most operators April 2023, hanya restore sebagian
- Hasil tidak konsisten — jangan andalkan
- Gunakan untuk privacy, bukan untuk dorking presisi

### Brave
- Operator labeled "experimental"
- Bisa di-drop silently saat terlalu sedikit hasil
- Independent index, 1.6B query/bulan — powers Claude AI search

### Yahoo
- Powered by Bing sejak 2010
- Inherit semua Bing operator

## AI Search Engines

| Engine | Operator Support | Scale | Nilai OSINT |
|---|---|---|---|
| **Perplexity AI** | `site:`, `filetype:`, `inurl:`, `before:`, `after:` | 30M query/hari | Terbaik — operator + natural language |
| **ChatGPT Search** | `site:` (emergent, undocumented) | 700M user/minggu | Tidak konsisten |
| **Google AI Mode** | `site:` di retrieval layer | 2B+ user/bulan | AI summary mungkin tidak honor constraint |
| **Microsoft Copilot** | Bing operators influence retrieval | N/A | Grounded on Bing |

## Strategi Multi-Engine

Untuk investigasi komprehensif, gunakan kombinasi:

| Engine | Gunakan Untuk |
|---|---|
| **Google** | Index size + `before:`/`after:` date filtering |
| **Bing** | `ip:` infrastructure mapping + `linkfromdomain:` outbound analysis |
| **Yandex** | Reverse image search + konten Rusia/Cyrillic + `rhost:` |
| **Perplexity** | Natural language dorking + operator hybrid |
| **Brave** | Independent index — coverage yang Google/Bing tidak punya |

Engine yang meng-index konten berbeda, pakai filter berbeda, support operator berbeda. Dorking Google-only = meninggalkan intel signifikan di meja.

## Sumber

- [Google Dorking Reference 2026 — Max Intel](https://maxintel.org/google-dorking-reference-2026.html)
- [DorkPlus Cheat Sheet](https://dorkplus.com/blog/google-dork-operators-cheat-sheet-2026)
- [Perplexity AI Search Operators](https://www.perplexity.ai/)
