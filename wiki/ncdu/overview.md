# Ncdu — NCurses Disk Usage

## Apa Itu?

**ncdu** = **NC**urses **D**isk **U**sage. Tool CLI interaktif untuk analisis pemakaian disk. Dibangun di atas ncurses (TUI), ditulis dalam C (versi 1.x LTS) dan Zig (versi 2.x stable).

Ncdu adalah versi interaktif dari perintah `du`. Bedanya: ncdu memberi tampilan tree-view dengan navigasi panah, grafis bar, dan kemampuan menghapus file langsung dari interface.

## Kenapa ncdu?

| Masalah | Solusi ncdu |
|---------|-------------|
| `du -sh *` cuma output teks, harus sort manual | ncdu sort otomatis descending, largest di atas |
| Harus `cd` + `ls` berulang kali cari folder besar | Navigasi panah — enter masuk folder, left keluar |
| Hapus file = buka terminal terpisah + `rm` | Tekan `d` di ncdu, konfirmasi, beres |
| Remote server tanpa GUI — tools grafik berat | ncdu jalan di terminal SSH, ncurses ringan |

## Use Case Utama

1. **Remote server cleanup** — SSH ke VPS, jalanin `ncdu /`, temukan space hog, hapus
2. **Local audit** — Laptop penuh, cari folder `/var`, `~/.cache`, `node_modules` mana yang gendut
3. **Export & review later** — Scan dulu, export ke file, browse nanti tanpa scan ulang
4. **Cron monitoring** — Export JSON tiap jam, alert kalau direktori tertentu > threshold

## Arsitektur

```
ncdu (TUI frontend)
  ├── Filesystem scanner (single-thread / multi-thread)
  ├── In-memory directory tree
  ├── Export engine (JSON / binary)
  └── Import engine (JSON / binary)
```

- **Scanner**: Traverse filesystem, hitung disk usage per item. Default single-thread, bisa `-t 8` untuk 8 thread parallel (v2.5+).
- **Tree**: Struktur data di memory. Untuk export binary (`-O`), tree tidak harus muat di RAM — streaming.
- **Export/Import**: JSON (`-o`) atau binary (`-O`). Binary bisa dikompresi Zstandard, ukuran lebih kecil, bisa streaming.

## Dua Versi

### Versi 2.x (Zig) — Stable
- Versi terbaru: 2.9.2 (Oct 2025)
- Ditulis dalam Zig
- Fitur: parallel scanning (`-t`), binary export (`-O`), Zstandard compression
- Butuh Zig 0.14+ untuk kompilasi

### Versi 1.x (C) — LTS
- Versi terbaru: 1.22 (Mar 2025)
- Ditulis dalam C
- Lebih stabil, masih di-maintain
- Fitur lebih sedikit, lebih portable

**Rekomendasi**: Pakai versi dari package manager distro (biasanya versi 2.x terbaru).

## Lisensi

MIT — bebas pakai, modifikasi, distribusi.

## Analogi

> ncdu adalah **"File Explorer versi terminal untuk ukuran disk"** — seperti WinDirStat tapi di CLI.

## Sumber

- Website resmi: https://dev.yorhel.nl/ncdu
- Manual: https://dev.yorhel.nl/ncdu/man
- Git: `git clone git://g.blicky.net/ncdu.git/`

## Lihat Juga

- [[wiki/ncdu/installation]] — Cara install
- [[wiki/ncdu/usage]] — Penggunaan dasar
- [[wiki/ncdu/commands]] — Semua flag + keybindings
- [[wiki/ncdu/export]] — Export/import + remote scanning
- [[wiki/ncdu/alternatives]] — Tool serupa (gdu, dua, duc, dll)
