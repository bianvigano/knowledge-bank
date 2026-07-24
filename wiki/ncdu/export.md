# Ncdu — Export, Import & Remote Scanning

## Export Local → Browse Later

Scan sekarang, lihat nanti tanpa scan ulang.

### JSON Export (Text, Standard)

```bash
# Export ke file
ncdu -o scan.json /

# Browse hasil export
ncdu -f scan.json
```

Kelemahan JSON: seluruh tree harus dimuat di memory. Untuk direktori besar, pakai binary export.

### JSON Export dengan Kompresi Zstandard

```bash
# Export + kompresi Zstandard
ncdu -co scan.json.zst /

# Browse langsung dari compressed file
ncdu -f scan.json.zst
```

### Binary Export (v2.6+) — Rekomendasi

```bash
# Export binary dengan kompresi built-in, 8 thread
ncdu -t8 -O scan.ncdu /

# Browse (tidak perlu load seluruh tree ke memory)
ncdu -f scan.ncdu
```

Keunggulan binary (`-O`):
- Built-in Zstandard compression
- **Streaming**: tidak perlu seluruh tree di RAM, cocok untuk direktori jutaan file
- Paralel: bisa digabung dengan `-t` multi-thread
- Block size bisa di-tune: `--export-block-size 256` (KiB)

### Pipe ke stdout — "Scan + Browse" Sekaligus

```bash
# Scan sambil export ke pipe, langsung browse
ncdu -O- / | ncdu -f-
```

### Extended Mode Export

Export dengan metadata extra: ownership, permissions, last modification time.

```bash
# Export binary, extended mode, 8 thread
ncdu -e -t8 -O /tmp/root-scan.ncdu /

# Browse dengan extended info (mtime column muncul)
ncdu -e -f /tmp/root-scan.ncdu
```

**Penting**: flag `-e` harus dipakai saat export DAN import.

## Remote Scanning — Local Browsing

Scan di remote server, lihat hasilnya di lokal. Ini lebih baik daripada menjalankan ncdu langsung di remote karena:
1. Tidak ada network latency saat browsing
2. ncdu remote tidak menyimpan seluruh tree di memory (export mode)

### JSON Pipe via SSH

```bash
# Scan remote, export JSON compressed, pipe ke ncdu lokal
ssh -C user@server ncdu -co- / | ncdu -f-
```

`-C` = SSH compression (menghemat bandwidth).

### Binary Pipe via SSH

```bash
# Binary export lebih efisien
ssh user@server ncdu -O- / | ncdu -f-
```

### SSH + sudo

Kalau perlu akses root di remote:

```bash
ssh user@server 'sudo ncdu -xO- /' | ncdu -f-
```

Pastikan user remote bisa sudo tanpa password untuk `ncdu`, atau setup di `/etc/sudoers`:

```
user ALL=(ALL) NOPASSWD: /usr/bin/ncdu
```

## Export untuk Cron / Monitoring

### Cron: Scan harian + simpan

```bash
# crontab
0 2 * * * ncdu -0xO /var/log/disk-usage/$(date +\%Y\%m\%d).ncdu /
```

- `-0` = tanpa output UI (cron-friendly)
- `-x` = satu filesystem saja
- `-O` = binary export compressed

### Bandingkan ukuran antar scan

```bash
# Export JSON, parse dengan jq untuk monitor folder tertentu
ncdu -o- /var | jq '.[3] | select(.name == "log") | .asize'
```

### Alert kalau direktori > threshold

```python
import subprocess, json, sys

def check_dir_size(path, threshold_gb):
    result = subprocess.run(
        ['ncdu', '-0xo', '/dev/stdout', path],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    size = data[3].get('dsize', 0)  # disk size in bytes
    if size > threshold_gb * 1024**3:
        print(f"WARNING: {path} = {size/1024**3:.1f} GiB")
        sys.exit(1)

check_dir_size('/var/log', 10)
```

## Import dari File

### JSON

```bash
ncdu -f scan.json
ncdu -f scan.json.zst         # compressed
ncdu -f - < scan.json          # stdin
```

### Binary

```bash
ncdu -f scan.ncdu
```

### Catatan Import

- Refresh, delete, dan shell **disabled** saat import (kecuali scan ulang)
- File import bisa dari versi ncdu lain — binary format backward-compatible
- Extended info (`-e`) harus match antara export dan import

## Perbandingan Format Export

| Fitur | JSON (`-o`) | Binary (`-O`) |
|-------|-------------|---------------|
| Human-readable | Ya | Tidak (binary) |
| Kompresi | Optional (`-c`) | Built-in |
| Streaming | Tidak (harus muat RAM) | Ya (2.6+) |
| Parallel scan | Delay output + RAM besar | Efisien |
| Multithread export | Delay setelah scan | Tidak delay |
| Parsing eksternal | `jq`, Python, dll | Butuh decode binary |

**Rule of thumb**: pakai `-O` untuk direktori besar (>100K files), `-o` untuk skrip parsing.

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview
- [[wiki/ncdu/usage]] — Penggunaan
- [[wiki/ncdu/commands]] — Semua flag
- [[wiki/ncdu/alternatives]] — Tool alternatif
