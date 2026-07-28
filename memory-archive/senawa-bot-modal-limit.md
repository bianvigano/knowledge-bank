---
source: memory
archived_at: 2026-07-26T07:00:00+07:00
tags: discord, bots, senawa
---

**Original Entry:**
Senawa bot: TextInput.setPlaceholder() max ~100 chars (strict @sapphire/shapeshift). Error: "Invalid string length". Event handler precedence — creator_admin.js defensive deferUpdate() makan interaction milik creator_apply.js (open_apply_modal). Fix: PASS_THROUGH array skip button. Creator apply modal rekrutmen: Nama Akun, Platform (YT/IG/TT), Link Akun, Konten Unggulan (4 fields, max 5 limit).

**Content:**
Pitfall: modalState.get() reads fresh — must update() after every mutation. Label/Checkbox rejected (UNION_TYPE_CHOICES) — only TextInput in modals. Modal max 5 components. TextInput.setPlaceholder() max ~100 chars.