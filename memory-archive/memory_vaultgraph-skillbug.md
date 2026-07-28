---
source: memory
archived_at: 2026-07-26T21:00:00+07:00
tags: memory-archive,oldest-entry,vault-graph,skill-bug
---

**Original Entry:**
vault-graph skill_manage BUG: skill listed in skills_list() but skill_manage actions (edit, patch, write_file) fail with "Skill 'vault-graph' not found in active profile 'default'". Skill exists at ~/.hermes/skills/vault/vault-graph/SKILL.md and is visible in vault-graph skill_view. Path: ~/.hermes/skills/vault/vault-graph/ — likely profile mismatch between skills_list (all-skills) and skill_manage (profile-scoped). Workaround: direct filesystem write to ~/.hermes/skills/vault/vault-graph/SKILL.md then sync to ~/.hermes/skills-all/vault/vault-graph/SKILL.md.

**Content:**
Profile-scoped skill management bug workaround documented in Vault skill