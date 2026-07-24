# Ncdu — Installation

## Package Manager (Rekomendasi)

Tersedia di repositori hampir semua distro. Pakai package manager masing-masing:

```bash
# Debian / Ubuntu / Mint
sudo apt install ncdu

# Arch / Manjaro / EndeavourOS
sudo pacman -S ncdu

# Fedora / RHEL / CentOS / AlmaLinux / Rocky
sudo dnf install ncdu
# Versi lama RHEL:
sudo yum install ncdu

# openSUSE
sudo zypper install ncdu

# Alpine Linux
sudo apk add ncdu

# Gentoo
sudo emerge -a sys-apps/ncdu

# Void Linux
sudo xbps-install ncdu

# NixOS
nix-env -i ncdu

# macOS (Homebrew)
brew install ncdu

# FreeBSD
sudo pkg install ncdu
```

## Static Binary (Tanpa Install)

Download binary static langsung dari website, extract, jalankan:

```bash
# x86_64
wget https://dev.yorhel.nl/download/ncdu-2.9.2-linux-x86_64.tar.gz
tar xzf ncdu-2.9.2-linux-x86_64.tar.gz
./ncdu

# ARM / AArch64 juga tersedia
```

Cocok untuk server minimal yang tidak punya package manager.

## Kompilasi dari Source

### Versi 2.x (Zig)

```bash
wget https://dev.yorhel.nl/download/ncdu-2.9.2.tar.gz
tar xzf ncdu-2.9.2.tar.gz
cd ncdu-2.9.2
zig build -Doptimize=ReleaseSafe
./zig-out/bin/ncdu --version
```

Requirement: Zig 0.14 atau 0.15.

### Versi 1.x (C)

```bash
git clone git://g.blicky.net/ncdu.git/
cd ncdu
git checkout master  # branch C version
autoreconf -i
./configure
make
sudo make install
```

Requirement: ncurses dev library (`libncurses5-dev` / `ncurses-devel`).

## Verifikasi

```bash
ncdu --version
# Ncdu 2.9.2
```

## Konfigurasi (Optional)

Buat file konfigurasi di `~/.config/ncdu/config` atau `/etc/ncdu.conf`:

```ini
# Enable extended mode (ownership, permissions, mtime)
-e

# Exclude .git directories
--exclude .git

# Enable colors (dark terminal)
--color=dark

# Only scan current filesystem
-x

# Disable delete (safety)
--disable-delete
```

Satu opsi per baris. Prefix `@` untuk suppress error (misal file exclude tidak ada):

```ini
@--exclude-from ~/.ncduexcludes
```

Pakai `--ignore-config` kalau ingin skip semua config file.

## Lihat Juga

- [[wiki/ncdu/overview]] — Overview
- [[wiki/ncdu/usage]] — Penggunaan
- [[wiki/ncdu/commands]] — Flags + keybindings
