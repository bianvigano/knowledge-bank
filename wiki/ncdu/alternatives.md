# Ncdu — Alternatives & Comparisons

## Kenapa Bandingkan?

Ncdu bagus, tapi tidak selalu tool terbaik untuk setiap skenario. Pilih tool sesuai kebutuhan:

- **ncdu** — terminal interactive, remote-friendly, battle-tested
- **gdu** — Go, lebih cepat, support ncdu JSON import/export
- **dua** — Rust, CLI non-interaktif, sangat cepat
- **duc** — C, multiple UI (CLI, GUI, OpenGL), scalable > RAM
- **disk usage tools GUI** — Baobab (GNOME), Filelight (KDE)

## Tabel Perbandingan

| Tool | Bahasa | Interface | Paralel | Export | Speed Tier |
|------|--------|-----------|---------|--------|------------|
| **ncdu** | Zig/C | TUI (ncurses) | Ya (v2.5+) | JSON + Binary | Fast |
| **gdu** | Go | TUI | Ya | JSON (ncdu compat) | Very Fast |
| **dua** | Rust | CLI | Ya | N/A | Very Fast |
| **duc** | C | CLI + GUI + OpenGL | Tidak | Database | Fast |
| **pdu** | Rust | CLI | Ya | N/A | Very Fast |
| **diskonaut** | Rust | TUI (treemap) | Tidak | N/A | Medium |
| **godu** | Go | TUI (slightly different UI) | Tidak | N/A | Medium |
| **tdu** | Go | CLI | Tidak | JSON (ncdu compat) | Fast |
| **dut** | C | CLI | Tidak | N/A | Fast |

## ncdu vs du (GNU)

| Aspek | du | ncdu |
|-------|-----|------|
| Output | Teks one-shot | Interaktif tree-view |
| Navigasi | `cd` + `ls` manual | Panah + Enter |
| Hapus file | `rm` terpisah | Tekan `d` |
| Remote scanning | Pipe via SSH manual | `ssh host ncdu -O-` |
| Sort | `sort -h` eksternal | Built-in, toggle ascending |

`du` tetap berguna untuk: script pipeline, one-liner, CI/CD.

## ncdu vs gdu

**gdu** = Go Disk Usage. Alternatif paling mirip ncdu.

| Aspek | ncdu | gdu |
|-------|------|-----|
| Kecepatan scan | Cepat | ~2x lebih cepat (Go concurrency) |
| Parallel default | Tidak (opt-in `-t`) | Ya (otomatis) |
| Memory | Rendah (v1.x) | Sedang |
| Export | JSON + Binary | JSON (ncdu-compatible) |
| Delete file | Ya | Ya |
| Package size | ~100 KB C / ~500 KB Zig | ~5 MB Go binary |
| Maturity | Sangat mature (2007) | Lebih baru (2020) |

**Pilih gdu** kalau: scan direktori sangat besar (>1M files), butuh hasil cepat.
**Pilih ncdu** kalau: remote server minimal, stability priority, atau sudah familiar.

## ncdu vs dua

**dua** = Disk Usage Analyzer (Rust). CLI non-interaktif, fokus kecepatan.

```bash
# dua: output langsung, sort desc
dua /

# ncdu: interactive browse
ncdu /
```

| Aspek | ncdu | dua |
|-------|------|-----|
| Interactive | Ya (TUI) | Tidak (CLI one-shot) |
| Kecepatan | Cepat | Sangat cepat (parallel default) |
| UI | ncurses tree | Teks tree + bar |
| Delete file | Ya | Tidak |

**Pilih dua** kalau: cuma ingin tahu "folder mana yang gendut, output teks aja".

## ncdu vs duc

**duc** = Disk Usage Collector. Arsitektur berbeda: index dulu, query kemudian.

```bash
# duc: indexing
duc index /home
duc ui          # ncurses UI
duc graph /home | display  # sunburst graph
```

| Aspek | ncdu | duc |
|-------|------|-----|
| Arsitektur | Scan langsung | Index → cache → query |
| Scale > RAM | Terbatas (kecuali binary export) | Index database, scalable |
| Real-time | Selalu fresh | Hasil dari index terakhir |
| UI types | ncurses TUI | CLI, ncurses TUI, OpenGL, X11 |

**Pilih duc** kalau: butuh multiple queries di dataset yang sama, atau direktori > RAM capacity.

## GUI Alternatives

### Baobab (GNOME Disk Usage Analyzer)

- GTK, bundled dengan GNOME
- Pie chart + treeview + treemap
- Hanya untuk desktop

### Filelight (KDE)

- Qt, KDE native
- Pie chart interaktif
- Desktop only

### QDirStat / K4DirStat

- Qt, treemap + treeview
- Fitur cleanup: hapus, pindah, compress
- Alternatif WinDirStat di Linux

## Kapan Pakai ncdu?

```
┌─────────────┬───────────────────────────┐
│ Situasi     │ Tool                      │
├─────────────┼───────────────────────────┤
│ SSH ke VPS,│ ncdu / gdu                 │
│ cari space  │                           │
│ hog, hapus  │                           │
├─────────────┼───────────────────────────┤
│ Pipeline CI,│ du + sort                  │
│ scripting   │                           │
├─────────────┼───────────────────────────┤
│ Scan 10M    │ gdu / dua / duc            │
│ files       │                           │
├─────────────┼───────────────────────────┤
│ Desktop     │ ncdu (terminal) / Baobab   │
│ visual      │                            │
├─────────────┼───────────────────────────┤
│ Recurring   │ duc (index once, query xN) │
│ monitoring  │                            │
├─────────────┼───────────────────────────┤
│ Export for  │ ncdu (JSON/binary)         │
│ later       │                            │
└─────────────┴───────────────────────────┘
```

## Sumber

- gdu: https://github.com/dundee/gdu
- dua: https://github.com/Byron/dua-cli
- duc: https://duc.zevv.nl/
- disconaut: https://github.com/imsnif/diskonaut
- Baobab: https://wiki.gnome.org/Apps/DiskUsageAnalyzer

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview ncdu
- [[wiki/ncdu/usage]] — Penggunaan dasar
- [[wiki/ncdu/export]] — Export/import
