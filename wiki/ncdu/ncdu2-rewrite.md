# Ncdu 2: Rewrite Zig — Arsitektur & Perubahan Internal

## Sejarah

- **ncdu 1.x (C)**: Sejak 2007, ditulis Yoran Heling untuk belajar C. Tujuan awal: disk usage analyzer untuk remote server via SSH.
- **ncdu 2.0**: Di-release 25 Desember 2021. Full rewrite dalam Zig. Prototipe untuk solusi 3 masalah fundamental versi 1.x.

## 3 Masalah Ncdu 1.x yang Mendorong Rewrite

### 1. Memory Hog

Setiap node dalam directory tree disimpan penuh di RAM. Untuk direktori jutaan file, memory usage signifikan. Struktur data C versi 1.x tidak optimal — room for improvement setelah low-hanging fruit.

### 2. Hard Link O(n²) Loop

Ncdu 1.x tidak efisien menghitung hard link. Pada kasus tertentu (jarang), bisa terjebak di loop O(n²) — performa collapse pada direktori dengan banyak hard link.

### 3. Hard Link Misleading Sizes

Masalah UX: hard link dihitung sekali dalam ukuran kumulatif direktori. Ini berguna (data tidak duplikat di disk), tapi misleading — menghapus direktori tidak serta-merta re-claim space jika ada hard link di luar direktori. Versi 1.x tidak punya cara menampilkan "shared vs unique" sizes.

Solusi: shared/unique column (`--shared-column`, toggle `u`) — hanya mungkin dengan data model baru.

## Perubahan Arsitektur di Versi 2

### Data Model

| Aspek | Ncdu 1.x (C) | Ncdu 2.x (Zig) |
|-------|-------------|----------------|
| Struktur | Linked tree in memory | Optimized flat arrays + indexes |
| Hard link tracking | O(n²) naif | Efficient hash-based lookup |
| Memory per node | ~120 bytes | ~60-80 bytes (roughly half) |
| Shared size calc | Tidak ada | Built-in (`u` toggle) |
| Parallel scan | Tidak mungkin | Supported (`-t`) |

### Memory Improvement

Rewrite Zig memangkas memory usage ~30-50% dibanding versi C. Dicapai dengan:
- Struct packing lebih tight (Zig punya kontrol memory layout eksplisit)
- String interning untuk nama file yang sama
- Eliminasi pointer overhead dengan array-based storage

### Hard Link Handling Baru

- Hash table `(dev, ino)` → node lookup
- Saat scan menemukan hard link, lookup hash table untuk node existing
- Track link count + shared size secara incremental
- Tampilkan "shared" vs "unique" column di UI

### Parallel Scanning (v2.5+)

`-t N` = N thread scanning filesystem secara paralel:

```
Thread 1: scan /usr/bin
Thread 2: scan /usr/lib
Thread 3: scan /var/log
...
```

- Setiap thread punya local buffer
- Shared hash table untuk hard link tracking (dengan synchronization minimal)
- Binary export (`-O`) bisa streaming multi-threaded output
- JSON export (`-o`) tetap single-threaded di output (delay sampai scan selesai)

## Kenapa Zig?

Alasan Yoran Heling (author):

1. **Cocok untuk systems programming**: kontrol memory + layout eksplisit
2. **Compile-time code execution** (`comptime`): generate optimized code untuk data structures
3. **No hidden allocations**: semua alokasi eksplisit, mudah audit memory behavior
4. **Cross-compilation built-in**: `zig build -Dtarget=x86_64-linux-musl` dari satu codebase
5. **C ABI compatibility**: bisa pakai libc tanpa overhead

## Masalah dengan Zig

### Instabilitas

Zig belum stable. Setiap rilis baru membawa breaking changes:

- Ncdu 2.0: Zig 0.8
- Ncdu 2.5: Zig 0.11
- Ncdu 2.9: Zig 0.14/0.15

Distro Linux kesulitan: versi ncdu terikat versi Zig. Kalau distro upgrade Zig, ncdu mungkin tidak kompilasi. Kalau distro mau upgrade ncdu, mungkin butuh versi Zig yang tidak dipaketkan.

### Workaround

- **Static binary** dari website — tidak perlu kompilasi
- **C version (1.x)** — tetap di-maintain untuk stabilitas
- **Package manager distro** — biasanya maintain patch untuk kompatibilitas

## Dua Versi — Dual Maintenance

Yoran Heling commit untuk maintain KEDUA versi:

| Aspek | C version (1.x) | Zig version (2.x) |
|-------|----------------|-------------------|
| Branch | `master` | `zig` |
| Status | LTS, maintained | Active development |
| Versi terbaru | 1.22 (Mar 2025) | 2.9.2 (Oct 2025) |
| Fitur baru | Backport selected features | All new features |
| Stabilitas | Very stable | Stable enough |
| Kompilasi | `./configure && make` | `zig build` |
| Dependensi | ncurses, C compiler | Zig compiler only |

### Fitur Backport ke 1.x

Fitur UI/UX di-backport dari 2.x ke 1.x agar user experience konsisten:
- CLI flags baru
- Keybindings baru
- Display improvements

Fitur yang tidak di-backport (terlalu sulit di C codebase):
- Parallel scanning
- Binary export format
- Shared/unique hard link column

## Timeline Versi

| Versi | Tanggal | Changes |
|-------|---------|---------|
| 1.0 | 2007 | Initial release (C) |
| 1.9 | 2012 | JSON export (`-o`, `-f`) |
| 1.13 | 2015 | Extended mode (`-e`), colors |
| 1.16 | 2018 | Improved hard link export (`nlink`) |
| 2.0 | Dec 2021 | Full Zig rewrite |
| 2.5 | Aug 2024 | Parallel scanning (`-t`) |
| 2.6 | Nov 2024 | Binary export (`-O`) |
| 2.9.2 | Oct 2025 | Current stable (Zig 0.14+) |

## Upgrade Path

### Dari 1.x ke 2.x

Drop-in replacement — semua flag, keybinding, dan UI identik. Tidak ada konfigurasi ulang atau workflow change.

### Antara Versi 2.x

Backward compatible. File export binary (2.6+) backward-compatible antar versi. JSON export selalu backward-compatible (major version tetap 1).

## Pitfalls & Edge Cases

### Hard Link + Refresh

Kalau hard link dihapus di luar ncdu sementara ncdu masih berjalan, angka shared/unique jadi salah. Harus restart ncdu (`q` lalu `ncdu` lagi) untuk koreksi.

### Symlink ke Direktori

Ncdu tidak follow symlink ke direktori (hanya symlink ke file dengan `-L`). Direktori symlink dihitung sebagai item `notreg` — ukuran symlink itu sendiri (bukan target).

### Filesystem Boundaries

`-x` mencegah cross filesystem. Tapi ncdu tidak otomatis exclude `/proc`, `/sys`, `/dev`, `/run` — gunakan `--exclude-kernfs`.

### 8 EiB Limit

Semua ukuran = signed 64-bit integer. Direktori > 8 EiB akan di-clip. Item count = 32-bit integer (max 4 miliar item per direktori).

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview
- [[wiki/ncdu/commands]] — Semua flag
- [[wiki/ncdu/json-format]] — JSON export format spec
- [[wiki/ncdu/binary-format]] — Binary export format spec
- [[wiki/ncdu/performance]] — Benchmark & optimization
