---
source: memory
archived_at: 2026-07-26T21:00:00+07:00
tags: memory-archive,oldest-entry,tabby-terminal
---

**Original Entry:**
Tabby terminal: built from source (github.com/Eugeny/tabby, v1.0.235, Electron 38.8.6). Installed as directory at /opt/Tabby/resources/app/ (NOT asar — ESM/CJS conflict). Source repo: ~/tabby-build. Config: ~/.config/tabby/. Binary: /opt/Tabby/tabby --no-sandbox. Rebuild: cd ~/tabby-build && git pull && yarn install && yarn build && sudo rm -rf /opt/Tabby/resources/app && sudo cp -a ~/tabby-build/app /opt/Tabby/resources/app. Also re-patch cliui ESM/CJS fix. Skill: tabby-build-fix.

**Content:**
duplicate entry — same info exists in earlier Tabby entry