# Ncdu Binary Export — Format Specification (v2.6+)

## Overview

Binary export format diperkenalkan di ncdu 2.6. Dirancang untuk mengatasi keterbatasan JSON export.

Dokumen referensi resmi: https://dev.yorhel.nl/ncdu/binfmt

## Keunggulan vs JSON

| Aspek | JSON (`-o`) | Binary (`-O`) |
|-------|-------------|---------------|
| Parallel scan support | Delay output, perlu seluruh tree di RAM | Thread-local buffering, minimal sync |
| Streaming browse | Tidak (harus load seluruh file) | Ya (depth-first, breadth-first, mixed) |
| Cumulative dir sizes | Tidak (harus walk tree) | Built-in dalam export |
| Kompresi | Optional (`-c`) | Built-in (Zstandard) |
| Parsing eksternal | Mudah (jq, Python) | Kompleks |

**Rule**: gunakan JSON untuk external tooling. Gunakan binary untuk internal ncdu flow.

## Konversi Format

```bash
# JSON → Binary
ncdu -f in.json -O out.ncdu

# Binary → JSON
ncdu -f in.ncdu -o out.json
```

## File Signature

Binary export dimulai dengan magic bytes:

```
bf 6e 63 64 75 45 58 31
```

Dibaca sebagai C string: `\xbfncduEX1`

Backward-incompatible changes = magic bytes berbeda (misal `EX2`).

## Block Format

Setelah signature, file terdiri dari satu atau lebih **block**:

```
┌──────────┬──────────┬──────────┐
│ TypeLen  │ Content  │ TypeLen  │
│ (4 byte) │ (n byte) │ (4 byte) │
└──────────┴──────────┴──────────┘
```

- **TypeLen** (4 byte, big-endian): high 4 bit = block type, low 28 bit = length
- **Content** (n byte): n = Length - 8
- **TypeLen** diulang di akhir → file bisa dibaca forward maupun backward (reverse seek untuk random access)

### Block Types

| Type | Arti |
|------|------|
| 0 | Data block |
| 1 | Index block |

Parser HARUS mengabaikan block dengan type unknown.

File valid minimal: 1 data block + 1 index block. Index block HARUS menjadi block TERAKHIR di file.

## Data Blocks

```
┌──────────────┬─────────────────────┐
│ Block Number │ Compressed Data     │
│ (4 byte)     │ (n byte, Zstandard) │
└──────────────┴─────────────────────┘
```

- **Block number** (4 byte, big-endian, unsigned): mulai dari 0, idealnya sequential tanpa gap
- **Compressed data**: Zstandard compressed dalam single frame

### Constraints

- Total block size ≤ 16 MiB - 1 byte (header + content + footer)
- Decompressed data ≤ 16 MiB - 1 byte
- ZSTD_getFrameContentSize() HARUS tersedia (pre-allocate buffer)

### Decompressed Data: Stream of Items

Data yang sudah di-decompress adalah stream dari satu atau lebih **Items**.

## Index Block

```
┌────────────────────┬──────────────┐
│ Block Pointers     │ Root ItemRef │
│ (n × 8 byte)       │ (8 byte)     │
└────────────────────┴──────────────┘
```

- **Block Pointers**: array offset ke setiap data block dalam file. Index i = block number i. Pointer = file offset (8 byte, big-endian).
- **Root ItemRef**: (block_number, item_index) ke root directory item.

## Item Format

Setiap item dalam decompressed data block:

```
┌──────┬──────┬──────────┬─────┐
│ Type │ Name │ Extras...│ End │
│(1 B) │(var) │ (var)    │(1 B)│
└──────┴──────┴──────────┬─────┘
```

### Item Types

| Type Byte | Arti |
|-----------|------|
| `0x00` | End marker (bukan item, penanda akhir stream) |
| `0x01` | Directory entry (node dalam tree) |
| `X ≥ 0x80` | Extended info (high bit set) |

### Directory Entry (0x01)

Berisi informasi file/direktori:

| Field | Encoding | Deskripsi |
|-------|----------|-----------|
| Name | Length-prefixed string | Nama file/dir |
| asize | Varint | Apparent size (unsigned) |
| dsize | Varint | Disk usage (unsigned) |
| cumulative_size | Varint | Total size dir + children (hanya untuk direktori) |
| dev | Varint | Device ID |
| ino | Varint | Inode number |
| nlink | Varint | Hard link count |
| Flags | Bitset | Status flags |

**Varint encoding**: variable-length integer, mirip Protobuf varint — 7 bit data per byte, high bit = continuation.

### Extended Info (≥0x80)

Extended info items:

| Type | Data |
|------|------|
| `0x81` | mtime (varint, UNIX timestamp) |
| `0x82` | uid (varint) |
| `0x83` | gid (varint) |
| `0x84` | mode (varint, st_mode) |

Extended info items opsional — hanya ada kalau scan dengan `-e`.

## Item References (ItemRef)

Item di-referensi oleh Index Block atau directory listing. ItemRef = 8 byte:

```
┌─────────────────┬──────────────────┐
│ Block Number    │ Item Index       │
│ (4 byte)        │ (4 byte)         │
└─────────────────┴──────────────────┘
```

- **Block number**: data block mana
- **Item index**: index item dalam decompressed data block (0-based)

## Cara Kerja Streaming Browse

### Depth-First Walk

1. Baca Index Block → dapatkan Root ItemRef
2. Seek ke data block root → decompress → temukan item root
3. Untuk setiap child: seek ke data block + index → decompress → baca child
4. Rekursif untuk subdirektori

Binary format mendukung **random access**: ncdu hanya mendekompresi data block yang sedang dibutuhkan. Tidak perlu load seluruh file.

### Cumulative Size Display

Tidak seperti JSON (harus walk seluruh tree untuk menghitung cumulative), binary export sudah menyimpan `cumulative_size` di setiap item direktori. UI bisa langsung menampilkan tanpa recursive walk.

## Block Size Tuning

`--export-block-size N` (4-16000, satuan KiB, default: start 64 lalu auto-grow):

- Block kecil: lebih banyak random access, cache-friendly
- Block besar: kompresi lebih baik, throughput lebih tinggi
- Auto-grow: ncdu memulai dengan 64 KiB block, lalu bertahap memperbesar untuk export besar

Kombinasikan dengan `--compress-level` (1-19, default 4):

```bash
# Kompresi maksimal untuk arsip
ncdu -O archive.ncdu --export-block-size 256 --compress-level 19 /

# Low latency untuk streaming
ncdu -O stream.ncdu --export-block-size 4 --compress-level 1 /
```

## Perbandingan Ukuran

Untuk 1 juta file (rough estimate):

| Format | Ukuran | Kompresi |
|--------|--------|----------|
| JSON (`-o`) | ~65 MiB | —
| JSON compressed (`-co`) | ~10 MiB | Zstandard |
| Binary (`-O`) | ~5 MiB | Built-in Zstandard |
| Binary (`-O`, level 19) | ~3 MiB | Max Zstandard |

Binary format ~2-3x lebih kecil dari compressed JSON, ~10-20x dari uncompressed JSON.

## Implementasi Referensi

Ncdu sendiri adalah reference implementation. Kode di cabang `zig` (Zig language):

```
src/
├── bin_export.zig   # Binary export writer
├── bin_reader.zig   # Binary import/reader
├── model.zig        # Data model
└── scan.zig         # Filesystem scanner
```

Third-party parsers untuk binary format belum banyak karena format baru dan kompleks. Untuk external tooling, JSON masih direkomendasikan.

## Lihat Juga

- [[wiki/ncdu/json-format]] — JSON export format (recommended untuk external tooling)
- [[wiki/ncdu/export]] — Export/import usage
- [[wiki/ncdu/ncdu2-rewrite]] — Arsitektur ncdu 2
- [[wiki/ncdu/performance]] — Benchmark & performance
