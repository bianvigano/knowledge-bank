# Ncdu — Usage Guide

## Basic Scanning

```bash
# Scan current directory
ncdu

# Scan specific directory
ncdu ~/Downloads

# Scan entire root filesystem (dengan sudo, -x = same filesystem only)
sudo ncdu -x /

# Scan without crossing filesystem boundaries
ncdu -x /home
```

## Interface

Setelah scan selesai, ncdu menampilkan TUI dengan:

```
┌─────────────────────────────────────────────────────────────┐
│  Dirs / files listed                                         │
│  ───────────────────────────────────────────────────────── │
│  12.4 GiB [/home/user]                                       │
│    8.2 GiB [##########]  .local                              │
│    2.1 GiB [###       ]  .cache                              │
│    1.5 GiB [##        ]  Documents                           │
│  624.3 MiB [#         ]  Downloads                           │
│  124.8 MiB [          ]  .config                             │
│    ...                                                       │
│  Total disk usage: 12.4 GiB  Apparent size: 13.1 GiB        │
└─────────────────────────────────────────────────────────────┘
```

Kolom: ukuran + grafis bar + nama item. Terbesar di atas.

## Navigasi

| Tombol | Aksi |
|--------|------|
| `↑` / `↓` / `j` / `k` | Pindah cursor atas-bawah |
| `→` / `Enter` / `l` | Masuk folder yang dipilih |
| `←` / `<` / `h` | Kembali ke parent folder |
| `q` | Keluar ncdu |

## Melihat Detail

Tekan `i` pada item yang dipilih — menampilkan popup:

- Full path
- Disk usage (ukuran di disk)
- Apparent size (ukuran sebenarnya)
- Item count (jumlah file di dalamnya)

Tekan `i` lagi untuk tutup.

## Menghapus File/Folder

Tekan `d` pada item → konfirmasi "Yes" / "No". Item langsung dihapus dan tampilan tree di-refresh.

**Safety tip**: Pakai `-r` (read-only) atau `--disable-delete` kalau tidak ingin accident delete.

## Sorting

| Tombol | Sort By |
|--------|---------|
| `s` | Size (default, descending) |
| `n` | Nama (ascending/descending) |
| `C` | Item count (ascending/descending) |
| `M` | Modified time (butuh mode `-e`) |

Tombol yang sama ditekan dua kali: toggle ascending ↔ descending.

## Toggling Display

| Tombol | Fungsi |
|--------|--------|
| `a` | Apparent size ↔ Disk usage |
| `c` | Show/hide item count column |
| `e` | Show/hide hidden & excluded files |
| `g` | Percentage / graph / both / none |
| `m` | Show/hide mtime column (butuh `-e`) |
| `t` | Directories before files (sort order) |
| `u` | Shared/unique size column (hard links) |

## Refresh Directory

Tekan `r` untuk rescan direktori yang sedang dibuka. Berguna kalau ada perubahan di luar ncdu.

## Spawn Shell

Tekan `b` — buka shell di direktori yang sedang dipilih. Variabel environment:

- `NCDU_SHELL` — shell yang dipakai (fallback: `$SHELL` → `/bin/sh`)
- `NCDU_LEVEL` — nesting depth (berguna untuk cegah recursive ncdu)

Contoh: buka vifm (file manager) dari ncdu:

```bash
NCDU_SHELL=vifm ncdu
```

## Mode Read-Only

```bash
# -r sekali = disable delete
ncdu -r /

# -r dua kali = disable delete + disable shell
ncdu -r -r /
```

## Scan dengan Progress Bar

```bash
# -0: tanpa output (cocok untuk cron)
# -1: progress text saja
# -2: full ncurses UI selama scan (default)
ncdu -2 /
```

Untuk remote connection lambat, pakai `-q` (slow UI updates, 1x per 2 detik):

```bash
ncdu -q /
```

## File Flags

Di tampilan TUI, beberapa item punya prefix flag:

| Flag | Arti |
|------|------|
| `!` | Error membaca direktori ini |
| `.` | Error membaca subdirektori (ukuran mungkin tidak akurat) |
| `<` | Item di-exclude oleh pattern |
| `>` | Direktori di filesystem lain |
| `^` | Linux pseudo-filesystem (excluded) |
| `@` | Bukan file/folder (symlink, socket, dll) |
| `H` | Hard link (sudah dihitung sebelumnya) |
| `e` | Direktori kosong |

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview
- [[wiki/ncdu/installation]] — Install
- [[wiki/ncdu/commands]] — Semua flag + keybindings
- [[wiki/ncdu/export]] — Export/import + remote scanning
