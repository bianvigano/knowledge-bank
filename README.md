# Hermes Vault

Wiki pribadi untuk menyimpan knowledge, session history, dan konsep dari percakapan dengan Hermes Agent.

## Struktur

- `sessions/` — Ringkasan session dari request_dump JSON
- `concepts/` — Konsep reusable yang diekstrak dari session
- `index.md` — Daftar isi utama
- `index.html` — Redirect ke `index.md`

## Cara Akses

### Via GitHub Pages
```
https://bianvigano.github.io/hermes-vault/
```

### Via Cache Local
```bash
python3 ~/.hermes/vault/scripts/vault_cache.py get index.md
python3 ~/.hermes/vault/scripts/vault_cache.py get sessions/hermes/nama-file.md
```

## Pipeline Otomatis

Cron `vault-session-ingest` tiap 2 jam:
1. `vault_update.py` — baca request_dump JSON → buat session .md
2. `vault_concepts.py` — ekstrak concept dari session .md
3. Push ke GitHub
4. `cleanup_old_sessions.py` — bersihin session lama

## Keamanan

- Semua path home diganti jadi `USER_HOME/`
- Tidak ada password atau credential di vault
- Repo public, jangan simpan data sensitif

## Setup Multi-Token

Di `~/.hermes/config.yaml`:
```yaml
github:
  vault_repo: bianvigano/hermes-vault
  tokens:
    - ghp_xxxxxxxx
    - ghp_yyyyyyyy
```

## Catatan

Vault ini adalah knowledge base pribadi. Gunakan skill `vault-smart-query` untuk query sebelum menjawab pertanyaan teknis.

## Vault Knowledge Graph
Query: `vault-graph search <term>`, `vault-graph explain <node>`
Graph: vault-out/graph.json (274 nodes, 206 edges)
CLI from anywhere. Build: `vault-graph build`
