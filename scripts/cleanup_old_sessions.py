#!/usr/bin/env python3
"""
cleanup_old_sessions.py — Hapus session JSON yang sudah di-extract ke vault.
Jalan tiap 24h via cron. Hapus session JSON yang sudah punya .md di vault.

Usage:
  python cleanup_old_sessions.py [--dry-run] [--verbose]
"""

import argparse
import json
import sys
from pathlib import Path

SESSIONS_PATH = Path.home() / ".hermes" / "sessions"
VAULT_PATH = Path.home() / "vault"
MANIFEST_PATH = VAULT_PATH / ".manifest.json"


def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None


def is_session_processed(session_stem, manifest):
    """Check if session already has a corresponding .md in vault."""
    if not manifest:
        return False
    
    # Check by session_stem in processed_sessions
    if session_stem in manifest.get("processed_sessions", []):
        return True
    
    # Check by session_id in sessions array
    for s in manifest.get("sessions", []):
        if isinstance(s, dict) and s.get("session_id") == session_stem:
            return True
        if isinstance(s, str) and s == session_stem:
            return True
    
    # Fallback: check if any vault file references this session
    sessions_dir = VAULT_PATH / "sessions"
    if sessions_dir.exists():
        for f in sessions_dir.rglob("*.md"):
            if f.name in ("index.md", "README.md"):
                continue
            content = f.read_text(encoding="utf-8", errors="ignore")
            if session_stem in content:
                return True
    
    return False


def main():
    parser = argparse.ArgumentParser(description="Cleanup sessions already in vault")
    parser.add_argument("--dry-run", action="store_true", help="Preview without deleting")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    args = parser.parse_args()

    print("=" * 60)
    print("Session Cleanup — Remove sessions already in vault")
    print("=" * 60)
    print(f"Sessions: {SESSIONS_PATH}")
    print(f"Vault:    {VAULT_PATH}")
    print(f"Mode:     {'DRY RUN' if args.dry_run else 'LIVE'}")
    print()

    manifest = load_manifest()
    if not manifest:
        print("WARNING: No vault manifest found. Nothing to clean.")
        sys.exit(0)

    session_files = sorted(SESSIONS_PATH.glob("session_*.json*"), key=lambda f: f.stat().st_mtime)

    if not session_files:
        print("No session files found.")
        sys.exit(0)

    delete_count = 0
    keep_count = 0
    freed_bytes = 0

    for sf in session_files:
        processed = is_session_processed(sf.stem, manifest)
        size = sf.stat().st_size

        if not processed:
            if args.verbose:
                print(f"  KEEP (not in vault): {sf.name}")
            keep_count += 1
            continue

        print(f"  DELETE: {sf.name} ({size // 1024}KB)")
        delete_count += 1
        freed_bytes += size

        if not args.dry_run:
            try:
                sf.unlink()
            except Exception as e:
                print(f"    ERROR: {e}")
                delete_count -= 1
                freed_bytes -= size

    print()
    print("=" * 60)
    print(f"Deleted: {delete_count}")
    print(f"Kept:    {keep_count}")
    print(f"Freed:   {freed_bytes // 1024}KB ({freed_bytes // (1024 * 1024)}MB)")
    print("=" * 60)


if __name__ == "__main__":
    main()
