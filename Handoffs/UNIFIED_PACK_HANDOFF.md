# Unified-Abs0lut-Claude — Project Handoff

**Started**: 2026-04-19  
**Current version**: v0.5.0 (Turn 1 infrastructure build)  
**File**: `/mnt/user-data/outputs/Unified-Abs0lut-Claude-v0.5.0.mcaddon`

## Architecture

Single `.mcaddon` bundles 8 component `.mcpack` files. Installing the `.mcaddon` installs all 8 packs into Minecraft with a single import. UUIDs across all packs are unique (verified 18 UUIDs, zero conflicts).

```
Unified-Abs0lut-Claude-v0.5.0.mcaddon
├── 01-PatrixWorld-Sampler-v0.4.0.mcpack          (existing, unchanged, 32 MB, RP)
├── 02-BIGCANOPY-BP-v2.8.1.mcpack                 (existing, unchanged, BP + script)
├── 03-BIGCANOPY-RP-v2.8.1.mcpack                 (existing, unchanged, RP)
├── 04-PatrixCanopyGen-BP-v0.1.2.mcpack           (existing, unchanged, BP only)
├── 05-PatrixWorld-Tectonic-BP-v0.7.2.mcpack      (existing, unchanged, BP)
├── 06-PatrixWorld-Tectonic-RP-v0.7.2.mcpack      (existing, unchanged, RP)
├── 07-pw-variants-BP-v0.1.0.mcpack               (NEW, scaffold, script stub)
└── 08-pw-variants-RP-v0.1.0.mcpack               (NEW, scaffold, empty)
```

## UUIDs (all locked)

Existing 6 packs carry the UUIDs from prior sessions — not listed here, they're in each pack's manifest.json.

**New UUIDs for pw_variants (locked from this session on):**

| Key | UUID |
|---|---|
| variants_bp_header | `3e884770-759a-4a80-81fc-9b7a6e22fec0` |
| variants_bp_data | `99da2689-d1f9-47fa-b8ba-ea9a3b4cd1d7` |
| variants_bp_script | `d7609a19-bf82-44d9-9b6f-3b68b70ad510` |
| variants_rp_header | `bccd3b03-ba64-4862-9879-9c7c7e2216e2` |
| variants_rp_res | `15d85bb0-8386-4c93-9c94-2daf763395c2` |

Also stored as JSON at `/home/claude/_reference_archive/pw_variants_uuids.json`.

## pw_variants BP scope (what it does, what it doesn't)

**At v0.1.0 (this session):**
- Script stub that logs `[pw_variants] scaffold v0.1.0 loaded` to chat and console on world load
- Empty `entities/` directory ready to receive vanilla entity overrides
- Declares `@minecraft/server` v2.0.0 dependency

**Planned v0.2.0 (Turn 2):**
- `entities/zombie.json` — override vanilla zombie entity JSON with custom property `pw:variant` (int 0–15, client_sync)
- `scripts/main.js` — subscribe to `entitySpawn` event, assign random 0–15 to `pw:variant` on zombie spawns (and other registered species)
- Zombie is the proof-of-concept; system generalizes from there

**Planned v0.3.0+ (future turns):**
- Expand the entity override table mob-by-mob
- Each addition = 1 BP entity JSON + 1 RP entity JSON + 1 RP render controller + N variant textures
- Architecture stays constant; the species table grows

## pw_variants RP scope

**At v0.1.0 (this session):** empty scaffolding, manifest only.

**Planned v0.2.0 (Turn 2):**
- `entity/zombie.entity.json` — client entity def referencing 16 texture slots
- `render_controllers/zombie.render.json` — molang switch on `query.property('pw:variant')`
- `textures/entity/zombie/zombie_v0.png` ... `_v15.png` — 4 authored textures padded to 16 slots per user directive (v0-v3 use source 1, v4-v7 use source 2, v8-v11 use source 3, v12-v15 use source 4)
- Proper `_mer.png` + `_normal.png` + `.texture_set.json` PBR sidecars for each

## Subpack tier system (Turn 3 plan)

Tier slider (32x/64x/128x/256x/512x) will be declared in the **Sampler**'s manifest.json (Option A decision from this session). Not in BIGCANOPY, Tectonic, or pw_variants — those stay at fixed single resolution. The Sampler has the bulk of visual content, and one slider in one place matches user's UX intent.

Subpack structure will be:
```
Sampler pack root contents = 128x textures (default baseline)
subpacks/32x/textures/...   (override when slider at low)
subpacks/64x/textures/...
subpacks/256x/textures/...
subpacks/512x/textures/...
```

## Testing expectations for Turn 1 build

Loading `Unified-Abs0lut-Claude-v0.5.0.mcaddon` in a fresh world with all 8 packs active should produce:

1. **Zero new visual changes** — all 4 original packs work as they did before the unification
2. **Zero console errors** related to the new pw_variants packs
3. **One chat message on world load**: "[pw_variants] scaffold v0.1.0 loaded"
4. **Behavior Packs list** shows: BIGCANOPY BP, PatrixCanopyGen BP, PatrixWorld-Tectonic BP, pw_variants BP (4 entries)
5. **Resource Packs list** shows: PatrixWorld Sampler, BIGCANOPY RP, PatrixWorld-Tectonic RP, pw_variants RP (4 entries)
6. Enable scripting experiment (should already be on from BIGCANOPY)

If any of these fail — that's information for Turn 2 diagnostics.

## Archive locations

- `/home/claude/_reference_archive/haiku_salvage/` — 1 file (zombie Patrix/Alacrity composite, reference only)
- `/home/claude/_reference_archive/haiku_labpbr_maps/` — 86 files (43 `_n` + 43 `_s` maps, LabPBR convention, not directly usable by VV but preserved per user directive)
- `/home/claude/_reference_archive/pw_variants_uuids.json` — UUID dictionary
- `/home/claude/_reference_archive/README.md` — what was discarded and why

## Things deferred, not forgotten

Everything from prior session handoffs still applies:
- Color normalization (savannah/canyon/badlands)
- Fluid physics (Track G)
- BIGCANOPY acacia geometry rework
- Lava animation boost
- Villager Patrix re-author (user doing manually)
- BIGCANOPY dynamic canopy sizing (#1, #2 from 14-item backlog)
- Slope-aware rest angle (#13)
- Giant mushroom felling (#9)

None of these are touched by the unification. They'll come back up as Turn 4+ priorities after in-game testing validates the unified pack.
