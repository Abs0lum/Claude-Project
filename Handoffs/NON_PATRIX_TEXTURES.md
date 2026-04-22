# PatrixWorld v0.4.0 — Non-Patrix Texture Audit

Document of every sampler texture not sourced from Patrix directly. User directive: recreate these in Patrix style for full aesthetic consistency when time permits.

Generated: 2026-04-18 — after v0.4.0 "Patrix-everywhere swap" (sheep/zombie/phantom reverted to Patrix).

---

## Category 1 — Villager System (Alacrity-sourced)

**Reason**: Patrix ships no villager textures anywhere — 64x basic, 128x basic, and 128x mobs all lack villager textures. We use Alacrity (128×128 Bedrock-vanilla UV) for the full layered system.

**What to recreate in Patrix style:**

### Base villagers
- `textures/entity/villager2/villager.png` (128×128 base body)
- `textures/entity/villager2/villager2.png` (alt base)
- `textures/entity/villager2/villager3.png` (alt base)
- `textures/entity/villager2/villager_baby.png` (baby variant)
- `textures/entity/villager2/hair.png` (hair overlay)
- `textures/entity/villager.png` (top-level fallback, duplicate of villager2/villager.png)

### Profession overlays (14 overlays + base)
- `textures/entity/villager2/profession/armorer.png`
- `textures/entity/villager2/profession/butcher.png`
- `textures/entity/villager2/profession/cartographer.png`
- `textures/entity/villager2/profession/cleric.png`
- `textures/entity/villager2/profession/farmer.png`
- `textures/entity/villager2/profession/fisherman.png`
- `textures/entity/villager2/profession/fletcher.png`
- `textures/entity/villager2/profession/leatherworker.png`
- `textures/entity/villager2/profession/librarian.png`
- `textures/entity/villager2/profession/mason.png`
- `textures/entity/villager2/profession/nitwit.png`
- `textures/entity/villager2/profession/shepherd.png`
- `textures/entity/villager2/profession/toolsmith.png`
- `textures/entity/villager2/profession/weaponsmith.png`

### Profession level overlays (5 tiers, both naming conventions)
- `textures/entity/villager2/profession_level/stone.png`
- `textures/entity/villager2/profession_level/iron.png`
- `textures/entity/villager2/profession_level/gold.png`
- `textures/entity/villager2/profession_level/emerald.png`
- `textures/entity/villager2/profession_level/diamond.png`
- `textures/entity/villager2/levels/level_stone.png` (Faithful naming convention)
- `textures/entity/villager2/levels/level_iron.png`
- `textures/entity/villager2/levels/level_gold.png`
- `textures/entity/villager2/levels/level_emerald.png`
- `textures/entity/villager2/levels/level_diamond.png`

### Type/biome overlays (7 biomes, both naming conventions)
- `textures/entity/villager2/type/plains.png`
- `textures/entity/villager2/type/desert.png`
- `textures/entity/villager2/type/jungle.png`
- `textures/entity/villager2/type/savanna.png`
- `textures/entity/villager2/type/snow.png`
- `textures/entity/villager2/type/swamp.png`
- `textures/entity/villager2/type/taiga.png`
- `textures/entity/villager2/biomes/biome_plains.png` (Faithful naming)
- `textures/entity/villager2/biomes/biome_desert.png`
- `textures/entity/villager2/biomes/biome_jungle.png`
- `textures/entity/villager2/biomes/biome_savanna.png`
- `textures/entity/villager2/biomes/biome_snow.png`
- `textures/entity/villager2/biomes/biome_swamp.png`
- `textures/entity/villager2/biomes/biome_taiga.png`

### Zombie Villager — full layered system (Alacrity-sourced)
Everything under `textures/entity/zombie_villager2/` follows the same structure as villager2 above. Replace analogously.

**Total villager textures to recreate: 42 files × 2 (villager + zombie_villager) = 84 files**

---

## Category 2 — Squid + Glow Squid (Alacrity-sourced)

**Reason**: Patrix ships no squid or glow_squid textures in any pack.

- `textures/entity/squid.png` (128×64, Alacrity)
- `textures/entity/glow_squid.png` (128×64, Alacrity — if present)

**Total: 2 files**

---

## Category 3 — Environment Textures (Hyper Realistic Sky-sourced)

**Reason**: Patrix doesn't ship sky/weather textures. We used Hyper Realistic Sky v3.8 by UsernameGeri for the sun, moon, clouds, rain, snow. Not Patrix aesthetic but unavoidable — no Patrix sky alternative exists.

- `textures/environment/sun.png`
- `textures/environment/moon_phases.png`
- `textures/environment/clouds.png`
- `textures/environment/rain.png`
- `textures/environment/snow.png`
- `textures/environment/celestial/moon/new_moon.png`
- `textures/environment/celestial/moon/waxing_crescent.png`
- `textures/environment/celestial/moon/first_quarter.png`
- `textures/environment/celestial/moon/waxing_gibbous.png`
- `textures/environment/celestial/moon/full_moon.png`
- `textures/environment/celestial/moon/waning_gibbous.png`
- `textures/environment/celestial/moon/third_quarter.png`
- `textures/environment/celestial/moon/waning_crescent.png`
- `textures/environment/celestial/sun.png`
- `textures/environment/celestial/end_flash.png`
- `textures/environment/colormap/fog0.png`

**Total: 16 files**

---

## Category 4 — Synthesized variants (derived from Patrix)

These are algorithmically derived from Patrix sources via rotation / hue-shift / brightness / vertical-shift / horizontal-shift. They preserve the Patrix aesthetic but aren't direct copies — you may want to re-author some by hand for natural variation rather than mathematical.

### Log top variants (112 files)
- `oak_log_top_v0` through `_v7` through legacy alias `log_top_oak_v0` through `_v7`
- Same for birch, spruce, jungle, acacia, dark_oak (big_oak legacy), cherry, mangrove
- 8 woods × 8 variants × 2 naming (modern+legacy) = 112 files (some overlap)

### Log side variants beyond v0-v7 (80 files)
- `oak_log_v8` through `_v11` — 8 existing woods × 4 = 32 synthesized
- `bamboo_block_v0-v11`, `pale_oak_log_v0-v11`, `crimson_log_v0-v11`, `warped_log_v0-v11` — 4 new woods × 12 = 48 from scratch

### Stripped log variants (220 files)
- All 11 woods (oak, spruce, birch, jungle, acacia, dark_oak, cherry, mangrove, pale_oak, crimson, warped)
- Each: 12 side variants + 8 top variants = 20 per wood × 11 = 220

### Plank variants (72 files)
- 12 woods × 6 joint-offset variants each

### Smooth/polished material synthetic variants
- `smooth_stone_v0-v7`, `smooth_sandstone_v0-v7`, `smooth_red_sandstone_v0-v7`, `smooth_quartz_v0-v7`
- `basalt_top_v0-v5`, `polished_basalt_top_v0-v5`
- `polished_andesite_v0-v7`, `polished_diorite_v0-v7`, `polished_granite_v0-v7`, `polished_deepslate_v0-v7`, `polished_tuff_v0-v7`, `tuff_bricks_v0-v7`
- `end_bricks_v0-v7`, `chiseled_stone_bricks_v0-v5`
- `polished_blackstone_v0-v7`, `polished_blackstone_bricks_v0-v7`, `cracked_polished_blackstone_bricks_v0-v7`, `chiseled_polished_blackstone_v0-v5`
- `chiseled_nether_bricks_v0-v5`, `cracked_nether_bricks_v0-v7`
- `red_nether_brick_v0-v7`

**Total synthetic variants: approximately 485 files**

These hold up algorithmically but if you want them to look hand-authored-varied (each tree has unique authored grain rather than color-shifted duplicates), they'd need manual re-creation.

---

## Category 5 — 100% Patrix-Sourced (NO action needed)

Everything else in the sampler — which is the vast majority:
- All block textures (2,000+ PNGs)
- All log side v0-v7 for existing woods (direct Patrix CTM-derived)
- All vegetation variants (leaves, flowers, bushes, vines, grass, cactus, kelp, seagrass, lily_pad, saplings, etc.)
- All mob textures except those listed in Categories 1-2
  - Including sheep/sheep_wool/sheep_wool_undercoat (Patrix 64 basic, swapped back this turn)
  - phantom.png (Patrix 64 basic, swapped back this turn)
  - zombie/zombie.png, zombie/drowned.png, zombie/husk.png (Patrix 64, swapped back this turn)
  - cat breeds, chicken biome variants, cow biome variants (Patrix 128 mobs scaled 50% to 64x)
  - copper_golem, creaking, breeze (Patrix 128 mobs scaled)

---

## Summary Counts

| Category | Files to recreate |
|----------|-------------------|
| Villager system (both villager + zombie_villager) | ~84 |
| Squid + glow_squid | 2 |
| Environment (Hyper Sky) | 16 |
| Synthesized variants (Patrix-derived, optional re-authoring) | ~485 |
| **Hard requirements (Categories 1-3)** | **~102 files** |
| **Optional re-authoring (Category 4)** | **~485 files** |

---

## How to prioritize

If recreating in priority order for v1.0:
1. **Villager base + main professions** (farmer, librarian, cleric) — highest visibility NPCs
2. **Environment sun/moon/clouds** — constantly visible sky
3. **Squid** — low priority, underwater and minimal
4. **Villager biome types + levels** — subtle variation, lower impact
5. **Zombie villager parallel** — even lower impact
6. **Synthesized block variants** — optional polish; the math-generated ones already look reasonable

## Source Locations (for reference)

Current non-Patrix sources:
- Alacrity: `/refpacks/alacrity/assets/minecraft/textures/entity/`
- Hyper Realistic Sky v3.8: `/mods_round3/hyper_sky/assets/minecraft/textures/environment/`
- Faithful R13 naming (for villager2/levels alias paths): `/uploads_all/faithful_64_r13/textures/entity/villager2/`
