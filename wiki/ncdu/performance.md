# Ncdu — Performance, Benchmark & Optimization

## Filosofi Kinerja

Ncdu dirancang untuk **fast enough** — bukan fastest-at-all-costs. Fokus: keseimbangan antara kecepatan, memory usage, dan kenyamanan interaktif.

Penulis (Yoran Heling) sengaja tidak mengoptimalkan untuk benchmark wars. Ncdu 2.0 vs gdu benchmark dari komunitas: ncdu ~75% waktu gdu (ncdu 2.0 = 770% lebih cepat dari ncdu 1.16).

## Faktor yang Mempengaruhi Kinerja

### 1. Jumlah File

Semakin banyak file = semakin lama scan. Linear relationship.

| Jumlah File | Single Thread | 8 Thread | Memory |
|------------|--------------|----------|--------|
| 100K | ~1 detik | ~0.3 detik | ~12 MB |
| 1M | ~10 detik | ~2 detik | ~80 MB |
| 10M | ~100 detik | ~15 detik | ~600 MB |
| 50M | ~500 detik | ~75 detik | ~3 GB |

Estimasi kasar, bervariasi tergantung filesystem, disk speed, dan tree depth.

### 2. Filesystem Type

| Filesystem | Relative Speed | Notes |
|-----------|---------------|-------|
| ext4 | Baseline | Standard Linux |
| xfs | ~0.9x | Comparable |
| btrfs | ~1.2x | Slower, metadata overhead |
| zfs | ~1.3x | Slower, COW overhead |
| NFS | ~3-5x | Network latency dominates |
| tmpfs | ~0.5x | RAM = very fast |
| NTFS (ntfs3) | ~2x | Kernel driver overhead |

### 3. Disk Type

| Disk | IOPS | Scan 1M files |
|------|------|--------------|
| NVMe SSD | 500K-1M | ~2-3 detik |
| SATA SSD | 80K-100K | ~10-15 detik |
| HDD 7200rpm | 100-200 | ~60-100 detik |
| HDD 5400rpm | 50-100 | ~120-200 detik |

Scan bottleneck: random read IOPS (metadata + inode lookup), bukan sequential throughput.

### 4. Directory Depth

Tree yang sangat dalam (banyak nested directories) lebih lambat dari tree dangkal dengan jumlah file sama. Setiap directory boundary = seek + readdir().

```
BURUK: /a/b/c/d/e/f/g/h/i/j/file  (10 level depth, 10 readdir + 10 seek)
BAIK:   /flat/file1 ... /flat/file1M  (1 level, 1 readdir)
```

## Optimasi Scan

### Parallel Scanning (`-t`)

```bash
# 8 thread = roughly 6-8x speedup pada SSD
ncdu -t8 /

# Tune thread count: jangan > CPU cores
ncdu -t$(nproc) /
```

Parallel scanning efektif pada SSD (multi-queue) tapi kurang efektif pada HDD (single head, thrashing).

### Exclude Pattern (Kurangi Scope)

```bash
# Skip directories yang tidak perlu
ncdu --exclude .git --exclude node_modules --exclude .cache /

# Dari file
cat > ~/.ncduexcludes <<EOF
.git
node_modules
.cache
target
*.pyc
.snap
EOF
ncdu -X ~/.ncduexcludes /
```

### Single Filesystem (`-x`)

```bash
# Hanya scan /home, skip semua mount points
ncdu -x /home

# Tanpa -x: ncdu akan scan /home/user/gdrive (mount) juga
```

### Skip Kernfs (`--exclude-kernfs`)

Linux pseudo-filesystems: /proc, /sys, /dev, /run. Default: included. Explicit exclude:

```bash
sudo ncdu --exclude-kernfs /
```

### Combined: Maximum Speed

```bash
# Scan / dengan optimasi maksimal
sudo ncdu -t8 -x \
  --exclude-kernfs \
  --exclude .git \
  --exclude node_modules \
  --exclude .cache \
  -0 -O /tmp/root-scan.ncdu /
```

- `-t8`: 8 thread parallel
- `-x`: satu filesystem
- `--exclude-kernfs`: skip /proc, /sys
- `--exclude ...`: skip common noise
- `-0`: tanpa UI saat scan (output minimal)
- `-O`: binary export (lebih efisien)

## Memory Optimization

### Ncdu 1.x vs 2.x Memory

Ncdu 2.x (Zig) menggunakan ~50% memory dari 1.x (C) untuk tree size yang sama. Perbaikan dari: struct layout, string interning, array-based storage.

### Memory per Sejuta File

| Versi | Memory | Keterangan |
|-------|--------|-----------|
| ncdu 1.x | ~180 MB / 1M files | Full tree di RAM |
| ncdu 2.x | ~80 MB / 1M files | Optimized data model |
| ncdu 2.x + `-O` | ~10 MB buffer | Streaming, tidak simpan full tree |

### Mode Low-Memory

```bash
# Scan + export binary = memory konstan (streaming)
ncdu -t4 -O scan.ncdu /

# Buka hasil — ncdu pakai lazy loading (hanya load block yang dibuka)
ncdu -f scan.ncdu
```

Binary export + lazy loading: tree tidak harus muat di RAM. Ncdu hanya mendekompresi data block yang sedang dilihat.

## Remote Scanning Optimization

### Bandwidth Saving

```bash
# SSH compression (-C) + ncdu slow UI updates (-q)
ssh -C user@host ncdu -q -O- / | ncdu -f-

# Best: binary export + SSH compression = minimal bandwidth
ssh -C user@host 'ncdu -0O- /' > remote.ncdu
ncdu -f remote.ncdu
```

### Latency Hiding

Scan remote → export → browse lokal. Tidak ada network latency saat navigasi.

```bash
# Scan remote (sekali), browse lokal (berulang)
ssh user@host 'ncdu -0O- /' > /tmp/server-$(date +%Y%m%d).ncdu
ncdu -f /tmp/server-*.ncdu
```

## Benchmark Commands

### Quick: Single Directory

```bash
time ncdu -0o /dev/null /usr
```

### Proper: Cold Cache

```bash
# Drop filesystem cache (butuh root)
sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
time ncdu -0o /dev/null /
```

### Compare Tools

```bash
# ncdu
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
time ncdu -0o /dev/null /home

# gdu (kalau terinstall)
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
time gdu -n /home

# du (baseline)
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
time du -sh /home

# dua
sync && sudo sh -c 'echo 3 > /proc/sys/vm/drop_caches'
time dua /home
```

## Known Performance Issues

### HDD Thrashing dengan `-t`

Jangan pakai `-t` di HDD — multi-threaded random read akan menyebabkan head thrashing, justru lebih lambat.

**Rule**: `-t` untuk SSD, single-thread untuk HDD.

### Symlink Resolution

`-L` (follow symlinks) menyebabkan extra `stat()` call per symlink + potensi loop detection. Lambat jika banyak symlink.

### Extended Mode

`-e` menambah ~30% memory + sedikit overhead scan (extra `stat()` fields). Hanya aktifkan jika butuh mtime/ownership.

### Deep Directory Trees

Jutaan subdirektori dengan sedikit file = lambat karena overhead `readdir()` per direktori. Mitigasi: tidak ada (filesystem limitation).

## Scaling Guide

| Direktori Size | Rekomendasi |
|---------------|------------|
| <100K files | `ncdu` langsung, no flags needed |
| 100K - 1M | `ncdu -t4 --exclude .git --exclude node_modules` |
| 1M - 10M | `ncdu -t8 -x -O scan.ncdu / && ncdu -f scan.ncdu` |
| 10M - 100M | Export binary streaming, browse lazy-loading |
| >100M | Pertimbangkan `duc` (index-then-query) atau `du -sh *` |

## Lihat Juga

- [[wiki/ncdu/ncdu2-rewrite]] — Arsitektur ncdu 2
- [[wiki/ncdu/binary-format]] — Binary export (streaming + lazy loading)
- [[wiki/ncdu/json-format]] — JSON export
- [[wiki/ncdu/alternatives]] — Perbandingan tool
- [[wiki/ncdu/commands]] — Semua flag optimasi
