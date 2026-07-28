---
source: memory
archived_at: 2026-07-26T07:00:00+07:00
tags: bug, modrinth, javascript
---

**Original Entry:**
BUG: modrinth-lookup script crashes on 0-result search — NameError: 'TIDAK' not defined at line 287 in print_search().

**Content:**
Fix: replace `print(f"\n{TIDAK} ada hasil untuk '{query}'{RESET}")` with `print(f"\nTidak ada hasil untuk '{query}'{RESET}")` (hardcode string, not undefined var). Path: ~/.hermes/skills/modrinth-lookup/scripts/modrinth.py