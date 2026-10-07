# CIVITAS test harness (Claude Code on GitHub)

The cloud workspace runs the BP-02 script suites with `@minecraft/server` stand-ins installed in `node_modules`; the knowledge
mirror carries neither the stand-ins nor two generated files. This folder restores that so any repo session can run them.

- `node_modules_template/@minecraft/server` — load-only stand-in: every event signal accepts `subscribe`, scheduling returns ids
  and never runs, enums/classes the modules import (Direction, EquipmentSlot, BlockVolume, ItemStack, BlockPermutation…).
- `node_modules_template/@minecraft/server-ui` — form classes whose `show()` resolves as cancelled.
- `run_civ_tests.sh [SRC] [GALLERY_DIR]` — copies the source to a temp dir, installs the stand-ins, runs `node --check` on every
  script and every `tests/test_*.mjs`. GALLERY_DIR = an unpacked BP-02 pack's `scripts/` (for `pw_gallery_data.js`,
  `pw_gallery_text.js`).

Result on the 07c mirror (round-231 source) with BP-02 1.3.230's gallery files: 30/31 suites pass; `test_survey` needs
`tests/fixtures/civheight-20261005-190214.txt.gz`, which the mirror omits (large fixture).
These are unit tests of pure logic: static checks rule things OUT, only an in-game test rules them IN (CLAUDE-AR P1).
