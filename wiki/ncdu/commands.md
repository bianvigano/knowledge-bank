# Ncdu — Commands & Keybindings

## Semua Flag CLI

```
ncdu [-f file] [-o file] [-O file] [-e] [--ignore-config]
     [-x] [--exclude pattern] [-X file] [--include-caches]
     [-L] [-t num] [-c] [--compress-level num]
     [-0/-1/-2] [-q] [--enable-shell] [--enable-delete]
     [-r] [--si] [--disk-usage] [--show-hidden] [--show-itemcount]
     [--show-graph] [--sort column] [--color scheme]
     [path]
```

### Mode

| Flag | Fungsi |
|------|--------|
| `-h`, `--help` | Print help |
| `-v`, `-V`, `--version` | Print versi |
| `-f file` | Import dari file (hasil `-o`/`-O`) |
| `path` | Scan direktori |

### Scan Options

| Flag | Fungsi |
|------|--------|
| `-x`, `--one-file-system` | Tidak cross filesystem |
| `--cross-file-system` | Cross filesystem (default) |
| `--exclude pattern` | Exclude file/dir matching pattern (bisa multiple) |
| `-X file`, `--exclude-from file` | Exclude dari file (satu pattern per baris) |
| `--include-caches` / `--exclude-caches` | Scan direktori dengan CACHEDIR.TAG |
| `-L`, `--follow-symlinks` | Follow symlinks (hitung ukuran file target) |
| `--include-kernfs` / `--exclude-kernfs` | Include/exclude /proc, /sys (Linux) |
| `-t num`, `--threads num` | Thread count untuk parallel scan (default 1) |

### Export Options

| Flag | Fungsi |
|------|--------|
| `-o file` | Export JSON ke file (`-` = stdout) |
| `-O file` | Export binary ke file (`-` = stdout) |
| `-c`, `--compress` | Zstandard compress JSON export |
| `--compress-level num` | Level kompresi 1-19 (default 4) |
| `--export-block-size num` | Block size KiB untuk binary export (4-16000) |
| `-e`, `--extended` | Scan + export dengan ownership, permissions, mtime |

### Interface Options

| Flag | Fungsi |
|------|--------|
| `-0` | Tanpa feedback saat scan (Cron-friendly) |
| `-1` | Progress text tanpa ncurses UI |
| `-2` | Full-screen ncurses UI saat scan (default) |
| `-q`, `--slow-ui-updates` | UI update lambat (1x per 2 detik), hemat bandwidth |
| `--fast-ui-updates` | UI update cepat (10x per detik, default) |
| `--enable-shell` / `--disable-shell` | Enable/disable spawn shell |
| `--enable-delete` / `--disable-delete` | Enable/disable hapus file |
| `--enable-refresh` / `--disable-refresh` | Enable/disable refresh direktor |
| `-r` | Read-only (sekali: disable delete; dua kali: +disable shell) |
| `--si` | Base 10 prefixes (kB, MB) bukan KiB, MiB |
| `--disk-usage` / `--apparent-size` | Tampilkan disk usage / apparent size |

### Display Options

| Flag | Fungsi |
|------|--------|
| `--show-hidden` / `--hide-hidden` | Show/hide hidden & excluded files |
| `--show-itemcount` / `--hide-itemcount` | Show/hide item count column |
| `--show-mtime` / `--hide-mtime` | Show/hide mtime column (butuh `-e`) |
| `--show-graph` / `--hide-graph` | Show/hide bar graph column |
| `--show-percent` / `--hide-percent` | Show/hide percentage column |
| `--graph-style` | `hash` (default), `half-block`, `eighth-block` |
| `--shared-column` | `off`, `shared`, `unique` |
| `--sort column` | `disk-usage`, `name`, `apparent-size`, `itemcount`, `mtime` (+ `-asc`/`-desc`) |
| `--enable-natsort` / `--disable-natsort` | Natural sort untuk nama file |
| `--group-directories-first` | Sort folder sebelum file |
| `--confirm-quit` | Konfirmasi sebelum quit |
| `--confirm-delete` | Konfirmasi sebelum hapus (default: on) |
| `--delete-command command` | Pakai custom command untuk delete (misal `gio trash`) |
| `--color scheme` | `off` (default), `dark`, `dark-bg` |
| `--ignore-config` | Skip loading `/etc/ncdu.conf` dan `~/.config/ncdu/config` |

## Semua Keybinding (Interactive Mode)

### Navigasi

| Key | Aksi |
|-----|------|
| `↑`, `k` | Move cursor up |
| `↓`, `j` | Move cursor down |
| `→`, `Enter`, `l` | Open selected directory |
| `←`, `<`, `h` | Go to parent directory |
| `q` | Quit |

### Sorting

| Key | Sort By |
|-----|---------|
| `s` | Size (descending default) |
| `n` | Name |
| `C` | Item count |
| `M` | Modified time (need `-e`) |

### Toggle Display

| Key | Aksi |
|-----|------|
| `a` | Apparent size ↔ Disk usage |
| `c` | Item count column |
| `e` | Hidden/excluded files |
| `g` | Percentage/graph/both/none |
| `m` | Mtime column (need `-e`) |
| `t` | Dirs before files |
| `u` | Shared/unique hard link sizes |

### Actions

| Key | Aksi |
|-----|------|
| `d` | Delete selected file/directory |
| `i` | Show info (path, size, item count) |
| `r` | Refresh/recalculate current directory |
| `b` | Spawn shell in current directory |
| `?` | Help screen |

## Tips

```bash
# Scan /var dengan 8 thread, export binary, tampilkan mtime
sudo ncdu -e -t8 -O /tmp/var-scan.ncdu /var
ncdu -f /tmp/var-scan.ncdu

# Exclude .git + node_modules
ncdu --exclude .git --exclude node_modules /

# Read-only full system scan
sudo ncdu -r -x /

# Custom delete: trash bukan rm
ncdu --delete-command 'gio trash --'

# Dark mode + extended info + sort by name
ncdu -e --color=dark --sort=name ~/

# Cron: scan /home, export JSON compressed, ke /var/log
ncdu -0xco /var/log/home-scan-$(date +%Y%m%d).json.zst /home
```

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview
- [[wiki/ncdu/installation]] — Install
- [[wiki/ncdu/usage]] — Penggunaan dasar
- [[wiki/ncdu/export]] — Export/import + remote scanning
