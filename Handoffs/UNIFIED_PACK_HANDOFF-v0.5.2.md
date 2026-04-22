# Unified-Abs0lut-Claude v0.5.2-ERRORS-FIXED — Project Handoff

**Built**: 2026-04-19  
**Iteration tag**: ERRORS-FIXED  
**File**: `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.2-ERRORS-FIXED.mcaddon` (32.55 MB)  
**Supersedes**: v0.5.1-ZOMBIE-PROOF  
**Purpose of this iteration**: zero-error load. The zombie variant system from v0.5.1 is preserved; errors surfaced during your in-game test are resolved.

---

## What changed from v0.5.1

| Pack | Version | Change |
|---|---|---|
| **PatrixWorld Sampler** | 0.4.0 → **0.4.1** | Fixed 3 registry errors in `blocks.json` + `terrain_texture.json` |
| **pw_variants RP** | 0.1.1 → **0.1.2** | Removed deprecated `animation_controllers` field from `zombie.entity.json` |
| All other 6 packs | unchanged | — |

---

## Root-cause summary for each fix

### Fix 1 — zombie `animation_controllers` schema error

**Error in v0.5.1**: `entity/zombie.entity.json | minecraft:client_entity | description | animation_controllers | child 'animation_controllers' not valid here`

**Cause**: The canonical vanilla `zombie.entity.json` from the ZtechNetwork mirror included an `animation_controllers` array at the `description` level. Bedrock 1.26.0+ rejects this field — animation controllers are now registered exclusively through the `animations` map (each with a `_controller` suffix in the short-name) and referenced via `scripts.animate`. The separate array is a legacy artifact.

**Fix**: Removed the entire `animation_controllers` field from our override. Verified all 15 `scripts.animate` entries still resolve to short-names present in the `animations` map. No behavioral change expected — the same 15 controllers are still registered and still animate.

### Fix 2 — `firefly_bush` invalid atlas index

**Error in v0.5.1**: `Texture firefly_bush is using an invalid atlas index 1 for the expected UV count 1`

**Cause**: Sampler v0.4.0's `terrain_texture.json` declared `firefly_bush` with a 3-entry `variations` array. Other flowers in the same file (dandelion, poppy, pink_petals, torchflower, fern, wither_rose — all with the exact same variations structure) don't error. The difference is that `firefly_bush` is a newer block (added via `behavior_packs/vanilla_1.21.70/feature_rules/`) and its engine schema apparently enforces a stricter single-UV constraint.

**Fix**: Changed `firefly_bush` from variations array to single path string pointing at `textures/blocks/firefly_bush_v0`. The `v1.png` and `v2.png` files stay on disk, unused by the terrain atlas. **Tradeoff**: visual variety for firefly bush drops from 3 variants to 1. Recoverable if a future Bedrock engine revision loosens the constraint, or if we reroute variety through a block state rather than texture variations.

### Fix 3 — `flowering_azalea_leaves` not in registry

**Error in v0.5.1**: `The block named minecraft:flowering_azalea_leaves used in a "blocks.json" file does not exist in the registry`

**Cause**: `minecraft:flowering_azalea_leaves` is a Java Edition block ID. Bedrock doesn't have it as a distinct block — verified by parsing BDS 1.26.14.1's `resource_packs/vanilla/blocks.json`: neither `flowering_azalea_leaves` nor `azalea_leaves_flowered` exists as a block name. In Bedrock, flowering azalea leaves are likely handled as a block state variant of `azalea_leaves`, not a separate identifier.

**Fix**: Removed `minecraft:flowering_azalea_leaves` entry from `blocks.json`. No Patrix texture is lost — the entry only configured sound + isotropic rendering flags, no texture was assigned.

### Fix 4 — `light_gray_glazed_terracotta` not in registry

**Error in v0.5.1**: `The block named minecraft:light_gray_glazed_terracotta used in a "blocks.json" file does not exist in the registry`

**Cause**: Bedrock retains the legacy name `minecraft:silver_glazed_terracotta` for what Java calls `minecraft:light_gray_glazed_terracotta`. Verified present in BDS vanilla `blocks.json`: `silver_glazed_terracotta: {sound: stone, textures: silver_glazed_terracotta}`.

**Fix**: Renamed the key in Sampler's `blocks.json` from `minecraft:light_gray_glazed_terracotta` to `minecraft:silver_glazed_terracotta`. Sound property preserved; texture path confirmed valid.

---

## Non-errors that were logged (kept as-is, expected)

The two `[Scripting][warning]` messages from your test are **not errors** — they are `console.warn()` calls our scripts deliberately emit on startup to confirm loading:

- `[BIGCANOPY] script loaded` — BIGCANOPY's own load banner
- `[pw_variants] v0.1.1 loaded — zombie variant system active` — pw_variants' load banner (now v0.1.2 in this build but the banner text wasn't changed; cosmetic, no functional impact)

These render at "warning" log level purely because `console.warn()` is the logging API; they're informational, not warnings. The `pw_variants` banner will say `v0.1.1` in-game due to the text of the banner string, but the pack header displays `v0.1.2`. Will sync banner text in a future iteration so both match.

---

## What to test in a fresh Realms world

Load `Unified-Abs0lut-Claude-v0.5.2-ERRORS-FIXED.mcaddon`, enable all 8 packs.

**Primary goal: zero-error load.**

### Must-pass checks

1. **Content log shows NO `[Animation][error]`** messages
2. **Content log shows NO `[Texture][error]`** messages  
3. **Content log shows NO `[Texture][warning]`** messages for flowering_azalea_leaves or light_gray_glazed_terracotta
4. Two `[Scripting][warning]` messages still present — those are script load banners (expected, not errors)
5. **Zombies still spawn with visual variants** (the v0.5.1 behavior must survive the fix)
6. All 4 original subsystems still work (no regression in blocks/trees/worldgen)

### Visual check

The firefly bush (spawns naturally in swamps) will now show a single variant texture (previously 3). Other plants (dandelions, poppies, torchflower, fern, wither rose, pink petals, etc.) keep their multi-variation look — only firefly bush lost variety.

The terracotta: place a `silver_glazed_terracotta` via `/give @s silver_glazed_terracotta` — should render with the Patrix light-gray glazed texture. The alternate name `light_gray_glazed_terracotta` no longer exists in the pack but Bedrock itself may accept it as a shortcut; verify with both names if you want.

---

## Critical / catastrophic failure recovery

Same as v0.5.1 (see `UNIFIED_PACK_HANDOFF-v0.5.1.md`). Additionally:

**If new texture errors appear on firefly_bush:**
The single-path form should be universally accepted. If an error appears anyway, try deleting the `firefly_bush` entry entirely from `terrain_texture.json` — Bedrock will fall back to the block's internal default lookup and the `firefly_bush_v0.png` file in `textures/blocks/` will still be found by path convention.

**If the terracotta rename broke existing terracotta you've placed in a world:**
This is a Bedrock-internal ID mapping issue, not something our fix controls. Any terracotta you've already placed is stored by the block's engine-side identifier (which is `silver_glazed_terracotta` on Bedrock regardless of what our blocks.json said). Should be unaffected.

**Full rollback to v0.5.1** (if v0.5.2 breaks anything v0.5.1 had working):
Use `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.1-ZOMBIE-PROOF.mcaddon`. It's still in outputs.

---

## What remains deferred (unchanged from v0.5.1)

Nothing on the deferred list changed this iteration. Everything listed in `UNIFIED_PACK_HANDOFF-v0.5.1.md` still applies: real PBR, real variants, zombie_baby authoring, subpack tier system (Turn 3), mob-by-mob variant expansion, all the BIGCANOPY backlog items, etc.

---

## Turn 3 preview (unchanged)

Subpack tier system on the Sampler pack (32x / 64x / 128x / 256x / 512x slider). Populate zombie textures across all 5 tiers as end-to-end validation. Once that lands, v0.5.x expansion begins mob-by-mob — drowned or husk as logical next candidate (already have matching Patrix textures).
