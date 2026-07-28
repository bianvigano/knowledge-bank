#!/usr/bin/env python3
"""
vault_update.py v3 — Deep session extractor from request_dump JSON.
Reads USER_HOME/.hermes/sessions/request_dump_*.json
Groups by session_id, picks the richest dump per session,
generates rich markdown session files in vault/sessions/.

Flow:
  1. Scan request_dump JSON files (skip cron_, take user sessions only)
  2. Group by session_id, pick dump with most messages per session
  3. Extract full conversation: user questions, assistant answers, commands, decisions
  4. Write rich session .md to vault/sessions/<category>/
  5. Update index.md and .manifest.json

Usage:
  python vault_update.py [--vault-path <path>] [--sessions-path <path>] [--dry-run] [--force] [--verbose]
"""

import argparse
import json
import re
import sys
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


def sanitize_home_path(text):
    """Replace /home/the-meh/ with USER_HOME/ in text."""
    if isinstance(text, str):
        return text.replace("/home/the-meh/", "USER_HOME/")
    return text

# ─── Config ───────────────────────────────────────────────────────────────────

VAULT_PATH = Path.home() / "vault"
SESSIONS_RAW_PATH = Path.home() / ".hermes" / "sessions"
SESSIONS_OUT_PATH = VAULT_PATH / "sessions"
MANIFEST_PATH = VAULT_PATH / ".manifest.json"

MIN_MESSAGES = 6  # Minimum user+assistant msgs to keep
MAX_SUMMARY_LINES = 300  # Max lines in summary section
MAX_QA_PAIRS = 15  # Max Q&A pairs to extract

# Category detection
CATEGORIES = {
    "minecraft": ["minecraft", "bukkit", "spigot", "paper", "folia", "fabric",
                   "plugin", "luckperms", "spark", "worldedit", "chunky",
                   "server", "hungergames", "scoreboard", "purpur", "modrinth"],
    "webdev": ["nextjs", "react", "prisma", "typescript", "tailwind", "javascript",
               "nodejs", "html", "css", "api", "frontend", "backend", "senyawa",
               "database", "supabase", "redis", "mongodb", "scraper", "web-x"],
    "hermes": ["hermes", "vault", "skill", "cron", "memory", "session", "agent",
               "openrouter", "gateway", "workspace", "plugin", "config", "skill",
               "caveman", "profile"],
    "devops": ["server", "vps", "ssh", "docker", "deploy", "nginx", "coolify",
               "firewall", "ufw", "systemd", "ssl", "certbot", "backup", "zip",
               "linux", "ubuntu", "debian", "git", "github"],
    "discord": ["discord", "bot", "webhook", "embed", "discordjs", "guild"],
    "general": [],
}

LOCK_PATH = VAULT_PATH / ".vault_update.lock"
LOCK_TIMEOUT = 600  # 10 minutes


# ─── Lock ─────────────────────────────────────────────────────────────────────

def acquire_lock():
    if LOCK_PATH.exists():
        try:
            age = (datetime.now().timestamp() - LOCK_PATH.stat().st_mtime)
            if age > LOCK_TIMEOUT:
                LOCK_PATH.touch()
                return True
            return False
        except:
            return False
    LOCK_PATH.touch()
    return True


def release_lock():
    try:
        if LOCK_PATH.exists():
            LOCK_PATH.unlink()
    except:
        pass


# ─── Helpers ──────────────────────────────────────────────────────────────────

def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "version": "3.0",
        "counts": {"sessions": 0, "concepts": 0},
        "processed_sessions": [],
        "sessions": [],
    }


def save_manifest(manifest):
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def clean_text(text):
    """Clean and normalize text."""
    if not isinstance(text, str):
        return ""
    # Remove [Note: ...] prefixes
    text = re.sub(r'\[Note:.*?\]\s*', '', text)
    # Normalize whitespace
    text = ' '.join(text.split())
    return text.strip()


def slugify(text, max_len=50):
    """Generate clean slug."""
    text = re.sub(r'[^a-z0-9\s-]', '', text.lower())
    words = [w for w in text.split() if len(w) > 2][:5]
    if not words:
        return "session"
    slug = "-".join(words)
    return slug[:max_len].strip("-")


def detect_category(text):
    """Detect topic category by keyword scoring."""
    text_lower = text.lower()
    scores = {}
    for cat, keywords in CATEGORIES.items():
        if cat == "general":
            continue
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"


def extract_code_blocks(text):
    """Extract code/command blocks from text."""
    blocks = []
    for m in re.finditer(r'```(\w*)\n(.*?)```', text, re.DOTALL):
        lang = m.group(1) or "bash"
        code = m.group(2).strip()
        if len(code) > 10:
            blocks.append({"lang": lang, "code": code[:800]})
    return blocks[:5]


def extract_inline_commands(text):
    """Extract standalone commands from text."""
    cmds = set()
    prefixes = [
        "sudo", "apt", "apt-get", "npm", "npx", "pnpm", "yarn", "git",
        "docker", "python", "python3", "pip", "pip3", "curl", "wget",
        "ssh", "scp", "chmod", "chown", "systemctl", "journalctl",
        "ufw", "zip", "tar", "gzip", "bzip2", "find", "grep", "rg",
        "psql", "mysql", "redis-cli", "mongosh", "node", "java", "javac",
        "code", "windsurf", "hermes", "rtk", "pm2", "cargo", "rustc",
        "prisma", "next", "vite", "tsc", "eslint", "prettier",
        "ls", "cd", "mkdir", "cp", "mv", "rm", "cat",
        "nano", "vim", "vi", "htop", "top", "df", "du", "free",
    ]
    for line in text.split("\n"):
        stripped = line.strip().lstrip("- 123456789.").strip("`")
        if 5 < len(stripped) < 200:
            for prefix in prefixes:
                if stripped.startswith(prefix + " ") or stripped.startswith(prefix + "\n"):
                    cmds.add(stripped)
                    break
    return sorted(cmd[:120] for cmd in cmds)[:15]


def group_sessions(sessions_path):
    """Group request_dump files by session_id, pick richest per session."""
    groups = defaultdict(list)
    
    for f in sorted(sessions_path.glob("request_dump_*.json")):
        # Skip cron sessions
        if "cron_" in f.stem:
            continue
        
        try:
            with open(f, "r", encoding="utf-8") as fp:
                data = json.load(fp)
        except:
            continue
        
        session_id = data.get("session_id", f.stem)
        msg_count = len(data.get("request", {}).get("body", {}).get("messages", []))
        groups[session_id].append((msg_count, f, data))
    
    # Pick richest dump per session
    best = {}
    for sid, candidates in groups.items():
        candidates.sort(key=lambda x: x[0], reverse=True)
        best[sid] = candidates[0]
    
    return best


def extract_session_data(msg_count, dump_file, data):
    """Extract all useful data from a request_dump."""
    body = data.get("request", {}).get("body", {})
    messages = body.get("messages", [])
    model = body.get("model", "?")
    timestamp = data.get("timestamp", datetime.now().isoformat())
    
    # Skip system messages
    user_msgs = [m for m in messages if m.get("role") == "user"]
    assistant_msgs = [m for m in messages if m.get("role") == "assistant"]
    tool_msgs = [m for m in messages if m.get("role") == "tool"]
    
    # Extract Q&A pairs
    qa_pairs = []
    for um in user_msgs:
        content = um.get("content", "")
        if isinstance(content, str):
            content = clean_text(content)
            if len(content) > 10:
                qa_pairs.append({"q": content[:300], "a": ""})
    
    # Find answers (last assistant before next user, or final)
    for i, am in enumerate(assistant_msgs):
        content = am.get("content", "")
        if isinstance(content, str) and len(content) > 10:
            answer = clean_text(content)[:500]
            # Attach to nearest question before this answer
            if i < len(qa_pairs):
                qa_pairs[i]["a"] = answer
            # Also check tool calls
            if "tool_calls" in am:
                for tc in am["tool_calls"]:
                    func_name = tc.get("function", {}).get("name", "")
                    if func_name and i < len(qa_pairs):
                        qa_pairs[i]["a"] += f" [tool: {func_name}]"
    
    # Extract commands from all text
    all_text = " ".join(
        m.get("content", "") if isinstance(m.get("content"), str) 
        else " ".join(p.get("text", "") for p in m.get("content", []) if isinstance(p, dict))
        for m in messages
    )
    all_text = sanitize_home_path(all_text)
    commands = extract_inline_commands(all_text)
    
    # Extract code blocks
    code_blocks = extract_code_blocks(all_text)
    
    # Extract decisions (lines with key decision words)
    decisions = []
    decision_keywords = ["fix", "solved", "done", "set", "config", "use", "run", "install", "create", "deploy"]
    for line in all_text.split("\n")[:200]:
        stripped = line.strip().lstrip("- ").strip("`")
        if len(stripped) > 20 and len(stripped) < 200:
            if any(stripped.lower().startswith(kw) for kw in decision_keywords):
                decisions.append(stripped[:150])
    
    # First meaningful user message (title)
    title = "Session"
    for um in user_msgs:
        content = um.get("content", "")
        if isinstance(content, str):
            content = clean_text(content)
            if len(content) > 10:
                title = content[:100]
                break
    
    # Detect category
    category = detect_category(all_text[:5000])
    
    return {
        "session_id": dump_file.stem.replace("request_dump_", ""),
        "timestamp": timestamp[:19],
        "message_count": msg_count,
        "title": title,
        "category": category,
        "model": model,
        "qa_pairs": qa_pairs[:MAX_QA_PAIRS],
        "commands": commands,
        "code_blocks": code_blocks,
        "decisions": decisions[:10],
        "source_dump": dump_file.name,
    }


def generate_session_md(session_data):
    """Generate rich session markdown."""
    d = session_data
    slug = slugify(d["title"])
    
    md = f"""---
title: "{d['title']}"
date: {d['timestamp']}
session_id: {d['session_id']}
category: {d['category']}
model: {d['model']}
messages: {d['message_count']}
source_dump: {d['source_dump']}
---

# {d['title']}

## Ringkasan
Model: {d['model']} | Pesan: {d['message_count']} | Kategori: {d['category']}

"""
    
    # Q&A pairs
    if d["qa_pairs"]:
        md += "## Percakapan\n"
        for i, qa in enumerate(d["qa_pairs"][:10]):
            if qa["q"]:
                md += f"### Q{i+1}: {qa['q'][:120]}\n"
            if qa["a"]:
                md += f"**A:** {qa['a'][:300]}\n\n"
    
    # Commands
    if d["commands"]:
        md += "## Commands\n"
        for cmd in d["commands"][:12]:
            md += f"- `{cmd}`\n"
        md += "\n"
    
    # Code blocks
    if d["code_blocks"]:
        md += "## Code\n"
        for i, block in enumerate(d["code_blocks"][:3]):
            md += f"```{block['lang']}\n{block['code']}\n```\n\n"
    
    # Decisions / actions
    if d["decisions"]:
        md += "## Keputusan / Tindakan\n"
        for dec in d["decisions"][:8]:
            md += f"- {dec}\n"
        md += "\n"
    
    md += f"## Sumber\n- Request dump: `{d['source_dump']}`\n"
    md += f"- Session ID: `{d['session_id']}`\n\n"
    md += "## Related\n"
    
    return md, slug


def update_folder_index(session_dir, filename, session_data):
    """Update folder index.md."""
    index_path = session_dir / "index.md"
    entry = f"- [[{filename.replace('.md', '')}]] — {session_data['title'][:60]}"
    
    if index_path.exists():
        content = index_path.read_text(encoding="utf-8")
        if filename.replace('.md', '') not in content:
            content += f"\n{entry}"
            index_path.write_text(content)
    else:
        header = f"# {session_dir.name.capitalize()} — Sessions\n\n"
        index_path.write_text(header + entry + "\n")


def process_all(vault_path, sessions_path, manifest, force=False, dry_run=False, verbose=False):
    """Main processing loop."""
    global VAULT_PATH, SESSIONS_RAW_PATH, SESSIONS_OUT_PATH, MANIFEST_PATH
    VAULT_PATH = vault_path
    SESSIONS_RAW_PATH = sessions_path
    SESSIONS_OUT_PATH = vault_path / "sessions"
    MANIFEST_PATH = vault_path / ".manifest.json"
    
    print(f"Scanning request dumps from: {sessions_path}")
    best_dumps = group_sessions(sessions_path)
    print(f"Found {len(best_dumps)} unique user sessions\n")
    
    created = 0
    updated = 0
    skipped = 0
    processed = set(manifest.get("processed_sessions", []))
    
    for sid, (msg_count, dump_file, data) in sorted(best_dumps.items()):
        if sid in processed and not force:
            if verbose:
                print(f"  SKIP (processed): {sid[:40]}")
            skipped += 1
            continue
        
        if msg_count < MIN_MESSAGES:
            if verbose:
                print(f"  SKIP (too few msgs: {msg_count}): {sid[:40]}")
            skipped += 1
            continue
        
        session_data = extract_session_data(msg_count, dump_file, data)
        category = session_data["category"]
        
        md_content, slug = generate_session_md(session_data)
        
        if len(md_content) < 300:
            if verbose:
                print(f"  SKIP (too thin): {slug}")
            skipped += 1
            continue
        
        out_dir = SESSIONS_OUT_PATH / category
        out_file = out_dir / f"{slug}.md"
        
        if dry_run:
            tag = "UPDATE" if out_file.exists() else "CREATE"
            print(f"  {tag}: sessions/{category}/{slug}.md ({msg_count} msgs)")
            created += 1
            continue
        
        out_dir.mkdir(parents=True, exist_ok=True)
        out_file.write_text(md_content)
        
        tag = "UPDATE" if out_file.exists() else "CREATE"
        print(f"  {tag}: sessions/{category}/{slug}.md ({msg_count} msgs)")
        
        if out_file.exists() and not force:
            updated += 1
        else:
            created += 1
        
        # Update folder index
        update_folder_index(out_dir, out_file.name, session_data)
        
        # Track
        if sid not in processed:
            processed.add(sid)
            manifest["sessions"].append({
                "session_id": sid,
                "file": f"sessions/{category}/{slug}.md",
                "date": session_data["timestamp"],
                "messages": msg_count,
            })
    
    # Update counts
    manifest["processed_sessions"] = list(processed)
    manifest["counts"]["sessions"] = len([s for s in manifest.get("sessions", []) if isinstance(s, dict)])
    
    # Update root index
    update_root_index(manifest)
    
    print(f"\n{'=' * 60}")
    print(f"Created: {created}  |  Updated: {updated}  |  Skipped: {skipped}")
    print(f"Total sessions: {manifest['counts']['sessions']}")
    print(f"{'=' * 60}")


def update_root_index(manifest):
    """Regenerate vault/sessions index from manifest."""
    index_path = VAULT_PATH / "index.md"
    
    # Group by category
    by_cat = defaultdict(list)
    for s in manifest.get("sessions", []):
        if isinstance(s, dict):
            file_path = s.get("file", "")
            if "/" in file_path:
                cat = file_path.split("/")[1]
                by_cat[cat].append(s)
    
    lines = ["# Vault — Knowledge Base Index\n"]
    lines.append("Semua referensi dikelompokkan per topik.\n")
    
    lines.append("## Sessions by Category\n")
    for cat in sorted(by_cat):
        lines.append(f"### {cat.capitalize()}")
        for s in by_cat[cat][:10]:
            file_name = Path(s.get("file", "")).stem
            title = s.get("date", "")
            lines.append(f"- [[{cat}/{file_name}]] — {title}")
        lines.append("")
    
    lines.append(f"\n_Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}_")
    
    index_path.write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser(description="Vault Update v3 — Deep session extractor from request_dump JSON")
    parser.add_argument("--vault-path", default=str(VAULT_PATH))
    parser.add_argument("--sessions-path", default=str(SESSIONS_RAW_PATH))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Reprocess all sessions")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    sessions_path = Path(args.sessions_path)
    
    if not args.dry_run:
        if not acquire_lock():
            print("Another vault update is running. Skipping.")
            sys.exit(0)
    
    try:
        if args.force:
            # Clear existing sessions
            sessions_dir = vault_path / "sessions"
            for d in sessions_dir.iterdir():
                if d.is_dir() and not d.name.startswith("."):
                    for f in d.glob("*.md"):
                        if f.name not in ("index.md", "README.md"):
                            f.unlink()
        
        manifest = load_manifest()
        if args.force:
            manifest["processed_sessions"] = []
            manifest["sessions"] = []
            manifest["counts"]["sessions"] = 0
        
        process_all(vault_path, sessions_path, manifest, 
                    force=args.force, dry_run=args.dry_run, verbose=args.verbose)
        
        if not args.dry_run:
            save_manifest(manifest)
        else:
            print("\nDRY RUN — no changes saved.")
    finally:
        release_lock()


if __name__ == "__main__":
    main()
