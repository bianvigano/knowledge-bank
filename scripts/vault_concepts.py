#!/usr/bin/env python3
"""
vault_concepts.py v2 — Deep knowledge extractor
Baca session .md files + generate concept dengan synthesis.
Output: problem → solution → commands → decisions → pitfalls.

Usage:
  python vault_concepts.py [--vault-path <path>] [--dry-run] [--force] [--verbose]
  --force : regenerate semua concept (default: skip existing)
"""

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

# ─── Config ───────────────────────────────────────────────────────────────────

VAULT_PATH = Path.home() / "vault"
SESSIONS_PATH = VAULT_PATH / "sessions"
CONCEPTS_PATH = VAULT_PATH / "concepts"
MANIFEST_PATH = VAULT_PATH / ".manifest.json"

# Minimal content quality
MIN_SECTION_SIZE = 40  # chars minimum per section
MIN_COMMANDS = 3  # min lines in code block to keep

# Category keywords (weighted)
CATEGORIES = {
    "minecraft": {
        "keywords": [
            "minecraft", "bukkit", "spigot", "paper", "folia", "fabric", "purpur",
            "plugin", "luckperms", "spark", "worldedit", "chunky", "denizen",
            "server", "hungergames", "scoreboard", "gamerule", "health"
        ],
        "weight": 5
    },
    "devops": {
        "keywords": [
            "server", "vps", "ssh", "docker", "deploy", "nginx", "coolify",
            "firewall", "ufw", "systemd", "ssl", "certbot", "backup", "zip",
            "linux", "ubuntu", "debian"
        ],
        "weight": 3
    },
    "webdev": {
        "keywords": [
            "nextjs", "react", "prisma", "typescript", "tailwind", "javascript",
            "postgresql", "nodejs", "express", "api", "frontend", "backend",
            "database", "redis", "mongodb", "supabase", "scraper", "html", "css"
        ],
        "weight": 3
    },
    "hermes": {
        "keywords": [
            "hermes", "vault", "skill", "cron", "memory", "session", "agent",
            "openrouter", "gateway", "workspace", "plugin", "config", "tool"
        ],
        "weight": 4
    },
    "discord": {
        "keywords": ["discord", "bot", "webhook", "embed", "discordjs", "guild"],
        "weight": 3
    },
    "general": {"keywords": [], "weight": 0},
}

# Noise words buat filtering title/slug
# ALL words < 4 chars auto-skip; these are 4+ char noise
NOISE = {
    "note", "model", "just", "switched", "from", "halo", "ini",
    "yang", "saya", "adalah", "bisa", "kamu", "untuk", "dengan",
    "pada", "tidak", "sudah", "belum", "akan", "juga",
    "saja", "kode", "code", "bikin", "ganti", "cara", "apakah",
    "dari", "atau", "baru", "lagi", "punya", "cek", "link",
    "clone", "github", "http", "https", "www", "com", "net", "org",
    "have", "this", "that", "with", "from", "will", "been", "were",
    "they", "their", "what", "when", "where", "which", "there",
    "about", "would", "could", "should", "does", "make", "like",
    "just", "more", "some", "than", "them", "then", "into", "only",
    "also", "very", "much", "even", "back", "well", "know", "take",
    "come", "good", "give", "most", "over", "such", "think", "help",
    "through", "before", "between", "after", "still", "find", "here",
    "thing", "many", "long", "part", "great", "right", "look", "want",
    "tell", "work", "first", "need", "keep", "call", "made", "down",
    "being", "each", "done", "open", "show", "seems", "ask",
    "used", "try", "start", "might", "must", "mean", "hand",
    "high", "last", "move", "next", "once", "other", "same",
    "seem", "turn", "went", "while", "read", "said",
    "false", "true", "null", "none", "value", "string", "class",
    "local", "static", "option", "default", "return", "event",
    "player", "world", "server", "method", "package", "import",
    "public", "private", "void", "object", "array", "index",
    "total", "count", "size", "data", "type", "name", "description",
    "category", "session", "message", "messages", "topic", "topics",
    "depth", "text", "file", "files", "content", "title", "source",
    "document", "classname", "const"
}


def load_manifest():
    if MANIFEST_PATH.exists():
        with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"version": "3.0", "counts": {"sessions": 0, "concepts": 0}}


def save_manifest(manifest):
    manifest["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)


def scan_session_files():
    """Scan session .md files in vault/sessions/."""
    files = []
    if not SESSIONS_PATH.exists():
        return files
    for f in SESSIONS_PATH.rglob("*.md"):
        if f.name in ("index.md", "README.md"):
            continue
        files.append(f)
    return files


def clean_title(raw_title):
    """Strip model-switch noise and truncate."""
    # Remove [Note: ...] prefixes
    cleaned = re.sub(r'\[Note:.*?\]', '', raw_title or "")
    cleaned = re.sub(r'^\s*,\s*', '', cleaned)
    cleaned = ' '.join(cleaned.split())  # normalize whitespace
    if len(cleaned) < 5:
        cleaned = "Session concept"
    return cleaned[:80]


def filter_noise_tags(tags):
    """Remove noise words from tags."""
    if not tags:
        return []
    noise_tags = {"false", "true", "null", "none", "default", "error", "data",
                  "depth", "text", "file", "files", "type", "name", "value",
                  "session", "total", "count", "size", "server", "player",
                  "world", "event", "return", "static", "local", "class"}
    if isinstance(tags, str):
        tags = [t.strip().strip("[]'\"") for t in tags.replace("[", "").replace("]", "").split(",")]
    return [t for t in tags if t.lower() not in noise_tags and len(t) > 2][:5]


def parse_session(content):
    """Deep parse session .md into structured knowledge."""
    meta = {}
    body = content
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, _, val = line.partition(":")
                    key = key.strip()
                    val = val.strip().strip('"')
                    if key == "tags":
                        val = filter_noise_tags(val)
                    meta[key] = val
            body = parts[2].strip()

    # Extract sections
    sections = {}
    current_section = "_preamble"
    current_lines = []
    
    for line in body.split("\n"):
        if line.startswith("## "):
            if current_lines:
                sections[current_section] = "\n".join(current_lines).strip()
            current_section = line.replace("## ", "").strip().lower()
            current_lines = []
        else:
            current_lines.append(line)
    if current_lines:
        sections[current_section] = "\n".join(current_lines).strip()

    return meta, sections


def extract_code_blocks(text):
    """Extract code blocks with language detection."""
    blocks = []
    pattern = r'```(\w*)\n(.*?)```'
    for match in re.finditer(pattern, text, re.DOTALL):
        lang = match.group(1) or "bash"
        code = match.group(2).strip()
        if len(code.split("\n")) >= MIN_COMMANDS:
            blocks.append({"lang": lang, "code": code})
    return blocks


def extract_commands(text):
    """Extract shell commands from text."""
    cmds = []
    cmd_prefixes = ["sudo", "apt", "npm", "git", "docker", "python", "pip", 
                    "curl", "wget", "ssh", "scp", "chmod", "chown", "systemctl", 
                    "journalctl", "ufw", "zip", "tar", "npx", "pm2", "node", 
                    "java", "javac", "pnpm", "yarn", "cargo", "rustc", "gcc", 
                    "make", "cmake", "ls", "cd", "mkdir", "cp", "mv", "rm",
                    "psql", "mysql", "redis-cli", "mongosh", "nano", "vim",
                    "code", "windsurf", "hermes", "rtk", "find", "grep",
                    "prisma", "next", "vite", "tsc", "eslint"]
    for line in text.split("\n"):
        stripped = line.strip().lstrip("- ").strip("`")
        if len(stripped) < 5 or len(stripped) > 200:
            continue
        if any(stripped.startswith(p) for p in cmd_prefixes):
            cmds.append(stripped)
    return cmds[:15]


def extract_problem_solution(meta, sections):
    """Detect problem → solution flow."""
    title = meta.get("title", "")
    summary = sections.get("summary", "")
    topics = sections.get("topics", "")
    source = sections.get("source", "")
    full_text = " ".join(sections.values())
    
    problems = []
    solutions = []
    
    # Problem signals
    problem_keywords = ["error", "gagal", "fail", "issue", "bug", "problem", "tidak bisa", "kenapa", "kok", "crash", "stuck"]
    solution_keywords = ["fix", "solved", "berhasil", "done", "sudah", "solution", "working", "jalan"]
    
    for line in [title, summary, full_text[:2000]]:
        for kw in problem_keywords:
            if kw in line.lower():
                # Extract sentence around keyword
                idx = line.lower().find(kw)
                start = max(0, idx - 50)
                end = min(len(line), idx + 150)
                snippet = line[start:end].strip()
                problems.append(snippet)
                break
    
    for line in [summary, full_text[-1000:]]:
        for kw in solution_keywords:
            if kw in line.lower():
                idx = line.lower().find(kw)
                start = max(0, idx - 30)
                end = min(len(line), idx + 150)
                snippet = line[start:end].strip()
                solutions.append(snippet)
                break
    
    return problems[:3], solutions[:3]


def generate_smart_slug(meta, category):
    """Generate clean slug from content analysis."""
    title = meta.get("title", "").lower()
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = [t.strip() for t in tags.split(",")]
    
    words = []
    
    # From tags first
    for tag in tags[:3]:
        clean = re.sub(r'[^a-z0-9]', '', tag.lower())
        if len(clean) > 3 and clean not in NOISE:
            words.append(clean)
    
    # From title
    title_words = re.findall(r'[a-z]{3,}', title)
    for w in title_words[:5]:
        if w not in NOISE and w not in words:
            words.append(w)
    
    seen = set()
    unique = []
    for w in words:
        if w not in seen and len(w) > 3:
            seen.add(w)
            unique.append(w)
    
    # Category prefix if too short
    if len(unique) < 2:
        unique.insert(0, category)
    
    slug = "-".join(unique[:5])
    slug = re.sub(r'-+', '-', slug).strip('-')[:60]
    return slug


def classify_category(meta, sections):
    """Classify by keyword scoring."""
    full_text = (meta.get("title", "") + " " + 
                 " ".join(meta.get("tags", []) if isinstance(meta.get("tags"), list) else [meta.get("tags", "")]) + " " +
                 " ".join(sections.values())).lower()
    
    scores = {}
    for cat, data in CATEGORIES.items():
        if cat == "general":
            continue
        score = sum(data["weight"] for kw in data["keywords"] if kw in full_text)
        if score > 0:
            scores[cat] = score
    
    if scores:
        return max(scores, key=scores.get)
    return "general"


def generate_concept_md(meta, sections, category, slug, source_rel_path):
    """Generate rich concept markdown."""
    title = clean_title(meta.get("title", slug))
    tags = meta.get("tags", [])
    if isinstance(tags, str):
        tags = filter_noise_tags(tags)
    
    # Extract knowledge
    problems, solutions = extract_problem_solution(meta, sections)
    code_blocks = extract_code_blocks(" ".join(sections.values()))
    commands = extract_commands(" ".join(sections.values()))
    
    # Build sections
    md = f"""---
title: "{title[:80]}"
date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
category: {category}
tags: [{', '.join(tags[:5])}]
source: "{source_rel_path}"
---

# {title[:80]}

"""
    
    # Problem/Solution
    if problems or solutions:
        md += "## Masalah\n"
        for p in problems:
            md += f"- {p}\n"
        md += "\n"
        if solutions:
            md += "## Solusi\n"
            for s in solutions:
                md += f"- {s}\n"
            md += "\n"
    
    # Summary
    summary = sections.get("summary", "")
    if summary and len(summary) > MIN_SECTION_SIZE:
        md += "## Ringkasan\n"
        md += summary[:500] + "\n\n"
    
    # Commands
    if commands:
        md += "## Commands\n"
        seen_cmds = set()
        for cmd in commands[:8]:
            key = cmd.lower()
            if key not in seen_cmds and len(cmd) > 5:
                seen_cmds.add(key)
                md += f"- `{cmd}`\n"
        md += "\n"
    
    # Code snippets
    if code_blocks:
        md += "## Code\n"
        for i, block in enumerate(code_blocks[:3]):
            lang = block["lang"] or "bash"
            md += f"```{lang}\n{block['code'][:500]}\n```\n\n"
    
    # Topics
    topics = sections.get("topics", "")
    if topics:
        topic_list = [t.strip().lstrip("- ") for t in topics.split("\n") if t.strip()]
        topic_list = [t for t in topic_list if len(t) > 3 and t.lower() not in NOISE]
        if topic_list:
            md += "## Topik\n"
            for t in topic_list[:6]:
                md += f"- {t}\n"
            md += "\n"
    
    md += f'## Sumber\n- [{source_rel_path}]({source_rel_path})\n\n## Related\n'
    
    return md


def concept_exists(slug, category, manifest):
    """Check if concept already generated."""
    concepts = manifest.get("concepts", [])
    for c in concepts:
        if isinstance(c, dict) and c.get("slug") == slug and c.get("category") == category:
            return True
    return False


def update_concept_index():
    """Update all concept category indexes."""
    if not CONCEPTS_PATH.exists():
        return
    
    for cat_dir in sorted(CONCEPTS_PATH.iterdir()):
        if not cat_dir.is_dir():
            continue
        if cat_dir.name.startswith("."):
            continue
        
        index_path = cat_dir / "index.md"
        md_files = sorted([f for f in cat_dir.glob("*.md") 
                           if f.name not in ("index.md", "README.md")])
        
        lines = [f"# {cat_dir.name.capitalize()} — Concepts\n"]
        
        if md_files:
            for f in md_files:
                content = f.read_text(encoding="utf-8", errors="ignore")
                inner_meta, _ = parse_session(content)
                title = inner_meta.get("title", f.stem)
                lines.append(f"- [[{cat_dir.name}/{f.stem}]] — {title}")
        else:
            lines.append("Belum ada concepts.\n")
        
        index_path.write_text("\n".join(lines))


def build_cross_links():
    """Build cross-references between concepts by tag overlap."""
    if not CONCEPTS_PATH.exists():
        return
    
    all_meta = {}
    for f in CONCEPTS_PATH.rglob("*.md"):
        if f.name in ("index.md", "README.md"):
            continue
        content = f.read_text(encoding="utf-8", errors="ignore")
        meta, _ = parse_session(content)
        tags = meta.get("tags", [])
        if isinstance(tags, str):
            tags = filter_noise_tags(tags)
        rel_path = str(f.relative_to(CONCEPTS_PATH))
        all_meta[rel_path] = {"file": f, "meta": meta, "tags": set(tags)}
    
    for rel_path, data in all_meta.items():
        f = data["file"]
        content = f.read_text(encoding="utf-8", errors="ignore")
        
        related = []
        for other_path, other_data in all_meta.items():
            if other_path == rel_path:
                continue
            overlap = data["tags"] & other_data["tags"]
            if overlap:
                other_slug = Path(other_path).stem
                other_cat = Path(other_path).parent
                other_title = clean_title(other_data["meta"].get("title", other_slug))
                related.append(f"- [[{other_cat}/{other_slug}]] — {other_title}")
        
        if "## Related" in content and related:
            lines = content.split("\n")
            related_idx = None
            for i, line in enumerate(lines):
                if line.strip() == "## Related":
                    related_idx = i
                    break
            if related_idx is not None:
                # Keep lines before Related, replace everything after
                new_lines = lines[:related_idx + 1] + related[:8]
                new_content = "\n".join(new_lines)
                if new_content != content:
                    f.write_text(new_content)


def process_all(vault_path, manifest, force=False, dry_run=False, verbose=False):
    """Main processing loop."""
    global VAULT_PATH, SESSIONS_PATH, CONCEPTS_PATH, MANIFEST_PATH
    VAULT_PATH = vault_path
    SESSIONS_PATH = vault_path / "sessions"
    CONCEPTS_PATH = vault_path / "concepts"
    MANIFEST_PATH = vault_path / ".manifest.json"
    
    session_files = scan_session_files()
    
    if not session_files:
        print("No session files found in vault/sessions/")
        return
    
    print(f"Scanning {len(session_files)} session files...\n")
    
    created = 0
    updated = 0
    skipped = 0
    seen_slugs = set()  # track dedup within this run
    
    for sf in sorted(session_files):
        content = sf.read_text(encoding="utf-8", errors="ignore")
        meta, sections = parse_session(content)
        
        if len(sections) < 2:
            if verbose:
                print(f"  SKIP (no sections): {sf.name}")
            skipped += 1
            continue
        
        category = classify_category(meta, sections)
        slug = generate_smart_slug(meta, category)
        
        # Deduplicate within this run
        if slug in seen_slugs:
            if verbose:
                print(f"  SKIP (duplicate slug): {slug}")
            skipped += 1
            continue
        seen_slugs.add(slug)
        
        source_rel = str(sf.relative_to(VAULT_PATH))
        
        concept_dir = CONCEPTS_PATH / category
        concept_path = concept_dir / f"{slug}.md"
        
        # Check existing
        if not force and concept_exists(slug, category, manifest):
            if verbose:
                print(f"  SKIP (exists): {slug}")
            skipped += 1
            continue
        
        # Generate
        concept_md = generate_concept_md(meta, sections, category, slug, source_rel)
        
        if len(concept_md) < 400:
            if verbose:
                print(f"  SKIP (too thin): {slug}")
            skipped += 1
            continue
        
        if dry_run:
            print(f"  WOULD {'UPDATE' if concept_path.exists() else 'CREATE'}: concepts/{category}/{slug}.md")
            created += 1
            continue
        
        is_update = concept_path.exists()
        concept_dir.mkdir(parents=True, exist_ok=True)
        concept_path.write_text(concept_md)
        
        tag = "UPDATE" if is_update else "CREATE"
        print(f"  {tag}: concepts/{category}/{slug}.md")
        
        if is_update:
            updated += 1
        else:
            created += 1
        
        # Track in manifest
        if "concepts" not in manifest:
            manifest["concepts"] = []
        
        # Remove old entry if update
        manifest["concepts"] = [c for c in manifest.get("concepts", []) 
                                if not (isinstance(c, dict) and c.get("slug") == slug)]
        
        manifest["concepts"].append({
            "slug": slug,
            "category": category,
            "source": source_rel,
            "updated": datetime.now(timezone.utc).isoformat()
        })
        manifest["counts"]["concepts"] = len(manifest["concepts"])
    
    # Update indexes and cross-links
    print("\nUpdating concept indexes...")
    update_concept_index()
    
    print("Building cross-references...")
    build_cross_links()
    
    print(f"\n{'=' * 60}")
    print(f"Created: {created}  |  Updated: {updated}  |  Skipped: {skipped}")
    print(f"Total concepts: {manifest['counts'].get('concepts', 0)}")
    print(f"{'=' * 60}")


def main():
    parser = argparse.ArgumentParser(description="Vault Concepts v2 — Deep knowledge extractor")
    parser.add_argument("--vault-path", default=str(VAULT_PATH))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--force", action="store_true", help="Regenerate ALL concepts")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    
    vault_path = Path(args.vault_path)
    manifest = load_manifest()
    
    if args.force:
        # Clear all existing concepts
        if CONCEPTS_PATH.exists():
            import shutil
            for d in CONCEPTS_PATH.iterdir():
                if d.is_dir():
                    for f in d.glob("*.md"):
                        if f.name not in ("index.md", "README.md"):
                            f.unlink()
        manifest["concepts"] = []
        manifest["counts"]["concepts"] = 0
        print("Cleared all existing concepts.\n")
    
    process_all(vault_path, manifest, force=args.force, dry_run=args.dry_run, verbose=args.verbose)
    
    if not args.dry_run:
        save_manifest(manifest)
    else:
        print("\nDRY RUN — no changes saved.")


if __name__ == "__main__":
    main()
