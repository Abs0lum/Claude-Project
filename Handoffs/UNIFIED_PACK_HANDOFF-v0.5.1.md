# Unified-Abs0lut-Claude v0.5.1-ZOMBIE-PROOF — Project Handoff

**Built**: 2026-04-19  
**Iteration tag**: ZOMBIE-PROOF (first working mob variant)  
**File**: `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon` (32.55 MB)  
**Supersedes**: v0.5.0 (infrastructure-only scaffold)

---

## What changed from v0.5.0

**New in v0.5.1:**
- `pw_variants BP` bumped **0.1.0 → 0.1.1**
  - Added `entities/zombie.json` (overrides vanilla zombie with `pw:variant` int property, range 0–15, client_sync)
  - Script now subscribes to `entitySpawn` and assigns random variant to zombies
- `pw_variants RP` bumped **0.1.0 → 0.1.1**
  - Added `entity/zombie.entity.json` (full vanilla zombie client entity + 16 texture slots)
  - Added `render_controllers/pw_zombie.render.json` (molang-based variant selection)
  - Added 5 texture files: `zombie_v0.png`, `zombie_v1.png`, `zombie_v2.png`, `zombie_v3.png`, `zombie_baby.png`

**Unchanged from v0.5.0:**
- All 6 original packs (Sampler, BIGCANOPY BP+RP, PatrixCanopyGen BP, Tectonic BP+RP) — byte-for-byte identical
- All 18 UUIDs across all 8 packs

---

## Current pack architecture (same as v0.5.0 layout)

```
Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon
├── 01-PatrixWorld-Sampler-v0.4.0.mcpack          (unchanged)
├── 02-BIGCANOPY-BP-v2.8.1.mcpack                 (unchanged)
├── 03-BIGCANOPY-RP-v2.8.1.mcpack                 (unchanged)
├── 04-PatrixCanopyGen-BP-v0.1.2.mcpack           (unchanged)
├── 05-PatrixWorld-Tectonic-BP-v0.7.2.mcpack      (unchanged)
├── 06-PatrixWorld-Tectonic-RP-v0.7.2.mcpack      (unchanged)
├── 07-pw-variants-BP-v0.1.1.mcpack               (v0.1.0 → v0.1.1: zombie support)
└── 08-pw-variants-RP-v0.1.1.mcpack               (v0.1.0 → v0.1.1: zombie assets)
```

---

## Locked UUIDs (unchanged from v0.5.0)

| Pack | Component | UUID |
|---|---|---|
| pw_variants BP | header | `3e884770-759a-4a80-81fc-9b7a6e22fec0` |
| pw_variants BP | data module | `99da2689-d1f9-47fa-b8ba-ea9a3b4cd1d7` |
| pw_variants BP | script module | `d7609a19-bf82-44d9-9b6f-3b68b70ad510` |
| pw_variants RP | header | `bccd3b03-ba64-4862-9879-9c7c7e2216e2` |
| pw_variants RP | resources module | `15d85bb0-8386-4c93-9c94-2daf763395c2` |

Backup: `/home/claude/_reference_archive/pw_variants_uuids.json`.

---

## Variant system — how it works end-to-end

1. **Zombie spawns** → Bedrock reads the BP `entities/zombie.json` (now ours, replacing vanilla). The `pw:variant` property is declared on the entity with `client_sync: true`.
2. **BP script fires** on `world.afterEvents.entitySpawn`. For identifier `minecraft:zombie`, calls `entity.setProperty("pw:variant", Math.floor(Math.random()*16))`.
3. **Property syncs to client** because of `client_sync: true`.
4. **Client reads** `pw_variants RP /entity/zombie.entity.json` which defines 16 texture short-names (`variant_0` .. `variant_15`) pointing to 4 physical PNG files.
5. **Render controller** `controller.render.pw_zombie` runs this molang:
   ```
   query.is_baby ? Texture.baby : Array.variants[math.clamp(query.property('pw:variant'), 0, 15)]
   ```
6. **Result**: baby zombie uses baby texture; adult zombie uses one of 4 visual variants based on random spawn index.

**Slot mapping (4-into-16 per user directive):**
| Property value | Short-name | PNG file |
|---|---|---|
| 0, 1, 2, 3 | variant_0..3 | `zombie_v0.png` (Patrix zombie baseline) |
| 4, 5, 6, 7 | variant_4..7 | `zombie_v1.png` (Patrix drowned — reused as zombie variant) |
| 8, 9, 10, 11 | variant_8..11 | `zombie_v2.png` (Patrix husk — reused as zombie variant) |
| 12, 13, 14, 15 | variant_12..15 | `zombie_v3.png` (programmatic dark/weathered) |

Expected per-variant distribution: ~25% each (uniform 0–15 → 4 equal bands).

---

## What to test in a fresh Realms world

Load `Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon`, enable all 8 packs.

### Must-pass checks

1. **Chat message on world load**: `[pw_variants] v0.1.1 ZOMBIE-PROOF loaded. Zombies now have 16 variant slots (4 distinct textures).`
2. **No script errors** in the in-game content log (check via pause menu → Settings → debug info or the chat)
3. **All 4 original subsystems still work** — no regression in blocks, trees, worldgen
4. **Zombies spawn with visible variants** — spawn 16+ zombies near each other (naturally at night, or use `/summon minecraft:zombie` 16 times) and verify at least 3 of the 4 distinct looks appear
5. **Baby zombies still look like babies** (small, zombie proportions, aggro-ride chickens)
6. **Zombie armor still works** — give a zombie a helmet via `/replaceitem`, confirm it renders

### Useful test commands

```
/locate biome minecraft:forest
/tp <x> <y> <z>
/time set night
/summon minecraft:zombie
/give @s minecraft:zombie_spawn_egg 64
/replaceitem entity @e[type=zombie,c=1] slot.armor.head 0 diamond_helmet
/clear @e[type=zombie]
```

### Nice-to-have observations

- Visual distinctness of the 4 variants — v0 greenish, v1 blueish (drowned-reused), v2 tan (husk-reused), v3 dark
- Any texture stretching or UV issues (this is the whole point of Turn 2 — proving the system works on real UV)
- Chunk-based consistency: same zombie should keep its variant after despawn/respawn

---

## Known limitations / deferred items for this iteration

1. **PBR sidecars not yet authored.** The 4 zombie textures have no `_mer.png` / `_normal.png` / `.texture_set.json` files. Bedrock VV falls back to diffuse-only rendering for these textures. This is intentional for placeholder-phase; real PBR comes when real variants are hand-authored.
2. **`zombie_baby.png` falls back to `zombie_v0.png`.** No zombie_baby source exists in any of the uploaded packs (Patrix, Alacrity, v0.4.0 Sampler). Vanilla Bedrock has one; ours doesn't. Baby zombies will look like miniaturized adult v0 zombies, not the vanilla stylized baby. Acceptable placeholder; fix requires sourcing or authoring a zombie_baby.png.
3. **Variants 1 & 2 are reused drowned/husk textures.** Visually this means some zombies in-game will look wet/blue or dry/tan — which is fine for variety but a player familiar with Minecraft might mistake them for actual drowned/husk entities from a distance. Unambiguous zombie variants will come when real textures are hand-authored.
4. **Subpack tier system not yet enabled.** Zombie textures ship at whatever resolution the sampler baseline is (256×256 based on file inspection). The 32x/64x/128x/256x/512x slider comes in Turn 3, applied to the Sampler pack.
5. **Only zombie has variants.** Drowned, husk, and all other mobs still use vanilla rendering. `VARIANT_SPECIES` dict in `main.js` has zombie only; expansion is mob-by-mob in future turns.

---

## Critical / catastrophic failure recovery

**If the pack won't load at all:**
- Check: does v0.5.0 (the scaffold-only) still load? If yes, v0.5.1's entity override is the culprit — the `entities/zombie.json` file in pw_variants BP.
- Emergency fallback: disable `pw_variants BP` and `pw_variants RP` in-game. The other 6 packs work standalone; zombies revert to vanilla behavior.

**If zombies spawn invisible or as "missing texture" magenta:**
- Most likely cause: `render_controllers/pw_zombie.render.json` molang is rejecting. Check in-game content log.
- Recovery: disable `pw_variants RP` only (keep BP). Zombies will use vanilla RP textures since BP entity override still has the property but client entity override is gone — the vanilla render controller runs.

**If zombies spawn but all look identical:**
- Most likely cause: script not setting property (check content log for script errors), or property not syncing (check `client_sync: true` in entities/zombie.json).

**If other mobs break:**
- `pw_variants BP` only overrides `entities/zombie.json` — no other entities touched. If any other mob breaks, it's NOT from this iteration. Disable other packs one at a time to isolate.

**Full restore to v0.5.0 state:**
- Use `Unified-Abs0lut-Claude-v0.5.0.mcaddon` from `/mnt/user-data/outputs/` (if you kept it).
- Otherwise rebuild from `/home/claude/work/unified_v0_5_0/` — has all 8 mcpack sources.

---

## Canonical source of truth for vanilla zombie JSON

Our `entities/zombie.json` override is based on **BDS 1.26.14.1** → `behavior_packs/vanilla_1.26.0/entities/zombie.json` (the version-snapshotted entity definition matching our `min_engine_version: [1,26,0]`). Only modification: added `pw:variant` to the `description.properties` block. All components, component_groups, events remain vanilla-identical.

Our `entity/zombie.entity.json` override is based on the **ZtechNetwork MCB Vanilla Resource Pack mirror** (master branch, format_version 1.26.0). Modifications: added 16 variant texture slots, replaced render_controllers array with our custom `controller.render.pw_zombie`. All scripts, animations, animation_controllers, enable_attachables preserved verbatim.

If Mojang updates vanilla zombie behavior in a future Bedrock release, our overrides will pin us to the 1.26.0 version of that behavior. This is a standard tradeoff for vanilla overrides.

---

## Archive & reference locations

- `/home/claude/_reference_archive/haiku_salvage/` — 1 file (zombie Patrix/Alacrity composite)
- `/home/claude/_reference_archive/haiku_labpbr_maps/` — 86 files (LabPBR _n/_s maps)
- `/home/claude/_reference_archive/pw_variants_uuids.json` — UUID registry
- `/home/claude/_reference_archive/README.md` — archive documentation
- `/home/claude/bds_extract/` — extracted BDS content (vanilla entity JSONs)
- `/home/claude/work/unified_v0_5_0/` — source build tree for v0.5.1 (persists between iterations; reused for future builds)

---

## Turn 3 preview

Next session introduces the **subpack tier system** (32x / 64x / 128x / 256x / 512x slider on the Sampler pack). Zombie textures will be populated across all 5 tiers to validate end-to-end. After that, v0.5.2 expands pw_variants to a second mob (drowned or husk as logical next candidate — they already have matching Patrix textures).

---

## Deferred items (still not forgotten)

- Real PBR (MER + normal + texture_set sidecars) for variant textures
- Real hand-authored variant textures (replacing the 4 placeholders)
- Color normalization (savannah/canyon/badlands)
- Fluid physics (Track G)
- BIGCANOPY acacia geometry rework
- Lava animation boost
- Villager Patrix re-author (user doing manually)
- BIGCANOPY backlog items #1, #2, #8, #9, #11, #13
- Giant mushroom felling
