# AI Assistant Setup

Multi-assistant workflow with shared knowledge graph.

## Assistants
| Assistant | Role | Context |
|---|---|---|
| Hermes | Primary CLI agent | `~/.hermes/` — skills, memory, cron |
| Trae IDE | Coding agent | `~/.trae/builtin_skills/` — MCP native |
| Claude Code | Terminal agent | `~/.claude/CLAUDE.md` |
| Codex | CLI agent | `~/.codex/AGENTS.md` |
| Continue | IDE agent | `~/.continue/rules/` |
| Codeium | IDE agent | `~/.codeium/memories/` |

## Shared Knowledge
All assistants connected via vault-graph to `~/vault/` (github.com/bianvigano/knowledge-bank).

## Environment
- OS: Linux Ubuntu (6.8.0-134-generic)
- Python: 3.10.12 (no pip), uv installed
- Package manager: pip → python3.10
- Git: SSH key auth to GitHub (bianvigano)

## Related
- [[hermes/hermes-setup]]
- [[vault/vault-system]]
