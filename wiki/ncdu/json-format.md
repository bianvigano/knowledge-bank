# Ncdu JSON Export — Format Specification & Parsing

## Overview

JSON format diperkenalkan di ncdu 1.9. Format ini backward-compatible — major version tetap `1` sejak awal.

Dokumen referensi resmi: https://dev.yorhel.nl/ncdu/jsonfmt

## Top-Level Structure

```json
[
  <majorver>,    // integer, selalu 1
  <minorver>,    // integer, 0-2
  <metadata>,    // object
  <directory>    // array (rekursif)
]
```

## Version History

| Minor Ver | ncdu Version | Additions |
|-----------|-------------|-----------|
| 0 | 1.9 - 1.12 | Base format |
| 1 | 1.13 - 1.15.2 | Extended mode (`-e`): uid, gid, mode, mtime |
| 2 | 1.16+ | `nlink` field untuk hard link tracking |

## Metadata Object

```json
{
  "progname": "ncdu",
  "progver": "2.9.2",
  "timestamp": 1690000000
}
```

Metadata diabaikan saat import oleh ncdu. Bisa ditambah custom fields untuk external tooling.

## Directory Structure (Rekursif)

```
<directory> = [
  <infoblock>,                          // info direktori ini
  <infoblock>,                          // file anak
  <directory>,                          // subdirektori (rekursif)
  <infoblock>,                          // file anak lain
  ...
]
```

Array dimulai dengan infoblock direktori. Sisanya = anak-anak: file (infoblock) atau subdirektori (array).

Direktori kosong = array dengan 1 elemen saja (infoblock-nya sendiri).

## The Info Block (Semua Fields)

### Required

| Field | Type | Range | Deskripsi |
|-------|------|-------|-----------|
| `name` | string | ≤32768 bytes | Nama file/dir. Top-level: full path. Lainnya: basename |

### Disk Usage

| Field | Type | Range | Deskripsi |
|-------|------|-------|-----------|
| `asize` | number | 0 ≤ x < 2⁶³ | Apparent size (st_size) |
| `dsize` | number | 0 ≤ x < 2⁶³ | Disk usage (st_blocks × S_BLKSIZE) |

### Device & Inode (Hard Link Tracking)

| Field | Type | Range | Deskripsi |
|-------|------|-------|-----------|
| `dev` | number | 0 ≤ x < 2⁶⁴ | Device ID (unique dalam dump) |
| `ino` | number | 0 ≤ x < 2⁶⁴ | Inode number (only if st_nlink > 1) |
| `hlnkc` | boolean | — | True jika st_nlink > 1 (redundant, backward compat) |
| `nlink` | number | 1 ≤ x < 2³² | st_nlink value (sejak v1.16) |

### Status Flags

| Field | Type | Deskripsi |
|-------|------|-----------|
| `read_error` | boolean | lstat() / readdir() gagal |
| `excluded` | string | Reason item excluded dari kalkulasi |
| `notreg` | boolean | Bukan file regular atau direktori (symlink, socket, dll) |

### Extended Mode (`-e`)

| Field | Type | Range | Deskripsi |
|-------|------|-------|-----------|
| `uid` | number | 0 ≤ x < 2³¹ | User ID |
| `gid` | number | 0 ≤ x < 2³¹ | Group ID |
| `mode` | number | 0 ≤ x < 2¹⁶ | File mode (st_mode), lihat inode(7) |
| `mtime` | number | 0 ≤ x < 2⁶⁴ | Modification time (UNIX timestamp, bisa fractional) |

## Excluded Status Values

| Value | Arti |
|-------|------|
| `"pattern"` | Matched exclude pattern |
| `"otherfs"` | Different filesystem (ncdu ≥1.21/2.5) |
| `"othfs"` | Different filesystem (ncdu <1.21/2.5, old spelling) |
| `"kernfs"` | Linux pseudo-filesystem exclude (v1.15+) |
| `"frmlink"` | macOS firmlink (v1.15+) |

## Contoh Export Real

```json
[1, 0,
  {"progname":"ncdu","progver":"1.9","timestamp":1354477149},
  [
    {"name":"/media/harddrive","dsize":4096,"asize":422,"dev":39123423,"ino":29342345},
    {"name":"SomeFile","dsize":32768,"asize":32414,"ino":91245479284},
    [
      {"name":"EmptyDir","dsize":4096,"asize":10,"ino":3924}
    ]
  ]
]
```

Struktur direktori:
```
/media/harddrive
├── SomeFile (32 KiB)
└── EmptyDir (kosong)
```

## Parsing dengan jq

### Top 5 largest directories

```bash
ncdu -o- /home | jq '.[3][1:] | map(select(type=="array")) | sort_by(.[0].dsize) | reverse | .[:5] | .[][0].name'
```

### Find all files > 1 GB

```bash
ncdu -o- / | jq '.. | select(type=="object" and .dsize > 1073741824 and .notreg != true) | {name, size_gb: (.dsize/1073741824)}'
```

### Total disk usage

```bash
ncdu -o- /home | jq '.[3][0].dsize'
# Output: bytes (dsize top-level directory)
```

### Count total files

```bash
ncdu -o- /home | jq '[.. | select(type=="object" and has("name"))] | length'
```

## Parsing dengan Python

### Streaming parser (untuk large export)

```python
import ijson  # pip install ijson
import sys

def find_large_files(filepath, min_size_mb=100):
    """Stream ncdu JSON export, yield files > min_size_mb."""
    with open(filepath, 'rb') as f:
        # Stream melalui array top-level: [major, minor, meta, tree]
        parser = ijson.parse(f)
        for prefix, event, value in parser:
            if event == 'number' and prefix.endswith('.dsize'):
                if value > min_size_mb * 1024 * 1024:
                    # Backtrack name (dari infoblock yang sama)
                    # Ini sederhana — real code perlu state tracking
                    yield value / (1024**3)

# Untuk parsing full (bukan streaming), cukup json.load()
import json
with open('scan.json') as f:
    major, minor, meta, tree = json.load(f)
print(f"Root size: {tree[0]['dsize'] / 1024**3:.2f} GiB")
```

### Walk tree rekursif

```python
import json

def walk_tree(node, path='/', depth=0):
    """Rekursif walk ncdu tree."""
    info = node[0]
    name = info['name']
    full_path = path + '/' + name if depth > 0 else name
    dsize = info.get('dsize', 0)
    
    # Filter: only directories
    children = [n for n in node[1:] if isinstance(n, list)]
    
    yield {
        'path': full_path,
        'size_bytes': dsize,
        'size_gib': dsize / 1024**3,
        'children': len(children)
    }
    
    for child in children:
        yield from walk_tree(child, full_path, depth + 1)

with open('scan.json') as f:
    _, _, _, tree = json.load(f)

for d in sorted(walk_tree(tree), key=lambda x: -x['size_bytes'])[:10]:
    print(f"{d['size_gib']:8.2f} GiB  {d['path']}")
```

## Catatan Penting

### Encoding

Filenames diekspor dalam encoding yang sama dengan filesystem (biasanya UTF-8). Kalau filesystem punya filename bukan UTF-8, JSON tidak akan valid UTF-8. Gunakan iconv untuk konversi:

```bash
ncdu -o- / | iconv -f latin1 -t utf-8 > scan-utf8.json
```

### Bug UTF-16 Escaping (BUG#245)

Versi ncdu <1.21 atau <2.7 tidak membaca escaped UTF-16 surrogate pairs dengan benar. Untuk portabilitas, unicode di atas U+FFFF sebaiknya di-encode sebagai UTF-8 (bukan escape). Ncdu sendiri tidak pernah output UTF-16 surrogate pairs.

### Large Exports

Export JSON bisa SANGAT besar:
- 10.000 files → ~600-700 KiB uncompressed / ~100 KiB compressed
- 1.000.000 files → ~60-70 MiB uncompressed / ~10 MiB compressed

Gunakan:
- `-c` (Zstandard compression): `ncdu -co scan.json.zst /`
- `-O` (binary format, 2.6+): jauh lebih efisien
- Stream parser untuk processing (ijson, bukan json.load)

## Lihat Juga

- [[wiki/ncdu/binary-format]] — Binary export format (2.6+)
- [[wiki/ncdu/export]] — Export/import usage
- [[wiki/ncdu/commands]] — CLI flags
