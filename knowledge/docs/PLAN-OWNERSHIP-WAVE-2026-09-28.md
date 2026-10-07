# PLAN — THE OWNERSHIP WAVE (2026-09-28, D-C264) — FOR ABS0LUM'S CONFIRMATION

> **Rev 5 note (20:0x CT 09-28, D-C270):** RP-06 1.4.11 (creeper render-controller schema fix) shipped too — the wave's RP-06 becomes **1.4.12**, built from rp06-1411 (new file `render_controllers/pw_creeper_armor.render.json`).
> **Rev 4 note (20:1x CT 09-28, D-C269):** round 4 shipped RP-06 1.4.10 and RP-07 1.4.15 (equine Converter B + eyes removed) before the wave, so the wave's numbers move up one more: RP-06 1.4.11, RP-07 1.4.16 (RP-04 stays .143). The wave's builder must start from rp06-1410 / rp07-1415 (new: `animations/pw_undead_equine_look.animation.json` in RP-06, `animations/pw_equine_look.animation.json` in RP-07) — the table below still shows the rev-3 numbers.
> **Rev 3 note (17:3x CT 09-28, D-C267):** round 3 shipped RP-04 1.3.142, RP-06 1.4.9, RP-07 1.4.14 and TestRunner BP 0.3.1 before the wave, so the wave's numbers move up one (RP-04 .143, RP-06 1.4.10, RP-07 1.4.15). The b09 witness decided the lookup question: texture paths resolve WHOLE-STACK and by extensionless STEM (a higher pack's .tga beats a lower pack's .png) — KEY-FOLLOWS-FILE stays as ownership hygiene, and the builder's censuses must key on the stem. The real danger it guards against is a key defined in two packs (the engine merges it into an un-weighted array).

**Status: CONFIRMED 01:58 (his rulings in §13) — BUILD IN PROGRESS.** TestRunner 0.3.0 (the recreated tests) is built and delivered; the wave itself follows in phases B–H. One test run after delivery (p0 → p1 → p2).
Inputs: his 23:28 rulings (ownership law for ALL inter-pack relationships; RP-02 owns ALL atmospherics; sizes as a real-life relationship;
leaves → 128; walk-around checks become runner steps) + his 00:25 rulings (RP-03/RP-04: **one pack iff the result is under 250 with reasonable
room, else two**; dependencies ON after the dedupe, dependent → owner — AGREED; StripMine RP "3.0.2" was MY MISLABEL — the Packs folder's
newest is **3.0.1**, which I hold byte-exact; "recreate the tests with the new information; plot the build; after I confirm, we build, then I test").
Census tool: `tools/ownership_map.py` (new) → `_logs/ownership_map.json` (every file in the stack: holders, referencing registries, class, owner).

## 0 · What I hold as his CURRENT LIST (the Packs folder, 09-27 16:12 CT upload) — the screenshots he mentioned did not arrive

| Pack | On the Drive (his list) | Newest delivered by me (gofile, awaiting his verdict) |
|---|---|---|
| RP-01 Tectonic RP | 1.3.104 | 1.3.104 |
| RP-02 Atmospheric Effects RP | 2.0.4 | 2.0.5 (hearth ember particle) |
| RP-03 PBR RP | 1.3.60 | 1.3.60 |
| RP-04 Basic RP | 1.3.138 | 1.3.141 (.139 embers → .141 strips-2 + sky trio removed) |
| RP-05 Flora RP | 1.3.49 | 1.3.51 |
| RP-06 Hostile Mobs RP | 1.4.6 | 1.4.8 |
| RP-07 Neutral Mobs RP | 1.4.11 | 1.4.13 |
| RP-08 Items RP | 1.4.6 | 1.4.7 |
| RP-10 Terrain RP | 1.3.40 | 1.3.42 |
| RP-11 Ores RP | 1.3.35 | 1.3.35 |
| BP-01 / BP-02 / BP-03 | 1.3.35 / 1.3.187 / 1.3.34 | — / 1.3.189 / — |
| PW-StripMine RP / BP (Realm) | **3.0.1** / 1.3.1 | — / 1.3.3 (size curve) |
| PW-TestRunner BP / RP | 0.1.0 / — | 0.2.2 / 0.2.2 |
| Markers RP/BP 0.2.1 · LeafProbe RP 0.3.1 / BP 0.4.1 · WitnessRig 0.1.0 · SlabForge 0.1.0 · StreetKit 0.1.4 · bridge_companion 0.1.6 | as listed | — |

Every build in this plan starts from the **newest delivered** tree (they are supersets of his list), so nothing he has is lost whichever he installed.
**If his screenshots show anything else, that row wins** — he confirms this table or marks the differences.

## 1 · The census (whole stack, 14 resource packs, 27,600 files; vanilla 1.26.50 registries + engine-implicit dirs included)

| Class | Files | Meaning |
|---|---|---|
| OWNED | 7,597 | exactly one pack references it from its own live registry — that pack owns it |
| MULTI-REF | 1,406 | two packs hold it AND both reference it (RP-03+RP-04 1,112 · RP-03+RP-05 138 · RP-01+RP-04 59 · RP-08+StripMine 15 · …) |
| VANILLA/ENGINE-REF | 3,849 | referenced only by vanilla's registries or loaded by fixed name (sky, ui, colormap, fogs, materials…) |
| X-PACK | 50 | referenced by a pack that does NOT hold it (RP-06→RP-07 23 zombie-villager skins · RP-05→RP-01 15 flowers · RP-04→RP-01 8 flowers · Markers→RP-04 2 planks · 2 singles) |
| DEAD-KEY-ONLY | 67 | referenced only through a key a higher pack out-ranks — draws nothing today |
| ORPHAN | **2,309 files / 112.7 MB** | referenced by nothing (ours, vanilla, engine) — see §7 |
| MISSING | 29 refs | referenced, held by nobody: RP-04's 18 `pw_side_*` keys · StripMine's 9 finch sounds + `enchanted_actor_glint` (also RP-08) |

**Shadows** (a copy in a pack that is not the owner): ~6,000 byte-identical (safe deletes) + 267 differing (decisions — §2 rule).
Global-id cross-references (geometry / animation / controller / render-controller / particle / fog / sound ids — these merge across packs by id, so they are
DEPENDENCIES, not duplicates): the hard edges today are RP-06→RP-07 (220 animations, 68 controllers, 7 geometries, 3 RCs: the HOSTILE animation files live
in RP-07), RP-07→StripMine (197 sf_nba sounds), StripMine RP→RP-02 (71 fogs: StripMine ships a legacy `biomes_client.json` mapping RP-02's `realsource:fog_*`
ids), RP-08→RP-07 (21 geometries + 21 animations + 11 RCs: the sf_nba egg/cage entities), BP-02→RP-04 (121 geometries) + RP-01 (24) + RP-02 (2 particles),
StripMine BP→RP-07 (10 geometries, 8 particles) + RP-02 (8 particles: the 38 sf_nba particles RP-02 carries), Markers BP→Markers RP (648).

Stack size today: **607 MB** of mcpacks. Projected after this wave: **≈ 400 MB** (−205 MB, −34 %).

## 2 · THE OWNERSHIP RULE (proposed law, v1) — how the law and L-DEDUP-4 stop conflicting

1. **Key-follows-file.** For every asset path exactly ONE pack ships the file AND every registry entry that names it (terrain/item key, flipbook entry,
   texture-set layer, entity/particle texture line). Cross-pack references remain only for global-namespace ids, and each of those becomes a manifest
   dependency (dependent → owner). Consequence: no registry ever references a file outside its pack → **L-DEDUP-4 is satisfied by construction**, and his
   law is satisfied (no duplicates) — the two only conflicted while a registry in pack A named a file that should live in pack B.
2. **Owner by theme** (his rulings), then by registry: atmospherics (particles, environment, fogs, biomes, lighting, water, colour grading, shadows) → RP-02 ·
   everything `sf_nba` (Naturalist) → PW-StripMine RP · terrain family RP-10 holds → RP-10 · ores → RP-11 · flora (flowers, grass, fern, saplings, crops) → RP-05 ·
   pw_ tectonic + leaf variants + falling-tree → RP-01 (BP-02's matched set) · hostile mob client side → RP-06 · neutral mob client side → RP-07 · items → RP-08 ·
   every other block texture + its PBR layers → the block owner (§3).
3. **Visual continuity.** Where two copies DIFFER, the bytes that draw today (the highest holder in his 09-22 order) win and are placed in the owner pack —
   except copies already ruled defective (L-CAP256 slivers, Java-layout leftovers). Every such choice is logged and shown on a before/after sheet.
4. Nothing referenced is deleted without its owner copy existing first (migration precedes deletion, in the same build).

## 3 · RP-03 ↔ RP-04 under his rule (01:58: "250 MB is an absolute maximum. Separate based on NEEDS and future foreseeable CONFLICTS") → TWO PACKS, split by NEED

Merged owner-copies-only would be 164 MB — under the ceiling, but that is not the test he set. The census splits RP-03 + RP-04's content into two
populations with different needs and different growth:

| Population | Files | mcpack | Need | Growth |
|---|---|---|---|---|
| **The vanilla-block port** — every vanilla-named block texture (Patrix colour) + its PBR layers + texture sets | 5,769 | **137.5 MB** | stands alone (no behaviour pack) | bounded by Minecraft's own block list |
| **The pw: custom-block families** — sand/red-sand/terracotta/deck/fill/warped/crimson/ramp/hearth/roof/wedge/furniture/thatch… textures, their texture sets, `models/blocks/*` geometries, the `pw:seat` entity, block names | 649 | **26.7 MB** | REQUIRES BP-02 (the blocks are its) | the growth area (every new family) |

Foreseeable conflict if they share one pack: the families keep growing on top of a 137 MB port; one pack drifts toward the ceiling and every family
release re-ships the whole port. Split by need:
- **RP-04 Basic RP = the vanilla-block port only** (colour + PBR, RP-03's layers absorbed): ≈ 137 MB, ≈ 113 MB of room, and it grows only when Minecraft
  adds blocks or we complete PBR.
- **RP-01 Tectonic RP = every pw: custom-block client file** (it is already BP-02's matched set: tectonic blocks, the leaf variants, falling-tree), gaining
  RP-04's 649 custom files: ≈ 25 + 27 MB, plus the 128 leaves (§9) ≈ 40–60 MB on disk → **≈ 90–110 MB**, all growth lands here, room to spare.
- **RP-03 retired** (its content lives in RP-04). BP-02's 121 geometry references to RP-04 become references to RP-01 (already 24 there) → BP-02 depends on
  RP-01 + RP-02 only.
Alternative if he prefers RP-01 untouched: the 649 custom files go to a repurposed RP-03 ("AbsolutRealism Custom Blocks RP", same UUID, renamed). Same
sizes; one more pack. Recommendation: RP-01 (fewer packs, matched set, one home for everything BP-02 draws).

"250" = the .mcpack size in MB (what he uploads); raw is within 2 % because PNG barely compresses.

## 4 · The build — pack by pack (projected; exact counts come from the build log)

| Pack | From → To | OUT | IN | Projected size |
|---|---|---|---|---|
| **RP-04 Basic** | 1.3.142 → **1.3.143** | 1,497 identical shadows of RP-03 already inside it, 128 orphans (43 Java-name banners, 26 chest leftovers, 24 stray `_n` layers, 17 unreferenced blocks), the 18 dead `pw_side_*` keys (no block references them — verified), terrain copies RP-10 owns, **the 649 pw: custom-block files + their keys, geometries, `pw:seat`, block names → RP-01** | ALL of RP-03's owned files + texture sets (the port's PBR); flower keys → RP-05 (8) | 137.6 → **≈ 137 MB** |
| **RP-03 PBR** | 1.3.60 → **retired** | — | — | 108.9 → 0 |
| **RP-01 Tectonic** | 1.3.104 → 1.3.105 | flowers/grass/fern copies RP-05 owns (116), block copies RP-04/RP-03 own (108), 88 orphans (unreferenced sapling/deadbush/cactus/pitcher variants + 16 stray `_n`) | **RP-04's 649 pw: custom-block files (textures, texture sets, `models/blocks`, `pw:seat`, lang names) + their registry keys**; the 128 leaves (§9) | 31.9 → ≈ 52 MB (+ leaves → ≈ 90–110 MB) |
| **RP-05 Flora** | 1.3.51 → 1.3.52 | the 9 leaf strips + 187 copies RP-03 owns (its 32-px leaves = shadows of RP-03's 128s), 12 orphans | the 15 flowers it references but RP-01 holds + RP-04's 8 flower keys (files + keys) | 12.9 → ≈ 9 MB |
| **RP-10 Terrain** | 1.3.42 → 1.3.43 | 2 orphans, 4 copies RP-04 owns | texture sets for the terrain files it wins from RP-03 | 19.4 → ≈ 14 MB |
| **RP-11 Ores** | 1.3.35 → 1.3.36 | 19 identical shadows of RP-03/RP-04, 4 orphans | — | 4.8 → ≈ 2.7 MB |
| **RP-02 Atmospherics** | 2.0.5 → 2.0.6 | the 38 `sf_nba` particles (→ StripMine RP), 6 orphans | RP-04's `end_flash.png` if it differs from vanilla (else dropped); RP-04's dead `rain.png` + 2.3 MB `environment/celestial/*` (read by nothing) dropped | 92.5 → ≈ 92 MB |
| **RP-06 Hostile** | 1.4.9 → 1.4.10 | 12 sf_nba entities + 1,560 sf_nba textures (all shadows), 407 orphans (312 unreferenced sf_nba, 48 Patrix `_n/_s` LabPBR layers — no engine use yet, kept in the source zip for the mob-MERS wave; 33 Java-path skins: `witch/witch.png`, `wither/`, `illager/vex`, `ghast/happy_ghast*`, `phantom_eyes`, `bogged_overlay`…; 14 `zombie_villager2/profession/` Java-layout) | the HOSTILE animation + controller files from RP-07 (zombie/husk/drowned/skeleton/stray/creeper/spider/vindicator/pillager/witch/ravager + `pw_animation_shims`: 201 ids); RP-07's Bedrock-layout `zombie_villager2/professions|biomes/*` skins (23) it already references | 39.0 → ≈ 12 MB |
| **RP-07 Neutral** | 1.4.14 → 1.4.15 | 94 sf_nba entities, 159 sf_nba models, 136 animations, 94 controllers, 85 RCs, 38 particles + all sf_nba textures; the hostile animation files above; 186 identical shadows of RP-02 (particles/environment); 456 orphans (312 sf_nba, 101 Java-layout: `equipment/*` saddles, `villager2/hair|villager2|villager3`, wolf `striped_a/chestnut_b/dyed_armur`…; 43 root-level Java names `sheep.png pig.png villager.png bat.png spider_eyes.png witch.v2.png cow_warm…`) | — | 59.0 → ≈ 28 MB |
| **RP-08 Items** | 1.4.7 → 1.4.8 | 29 sf_nba entity files + attachables + all sf_nba textures; 761 orphans (429 item `_n/_s` layers with no engine support, 312 sf_nba, 17 Java `equipment/*` at 18 MB, 3 items) | — | 73.1 → ≈ 38 MB |
| **PW-StripMine RP** (Realm) | 3.0.1 → **3.1.0** | the nested `Naturalist Add-On 26.1 BP/` folder (1,217 files of behaviour-pack junk inside a resource pack), the legacy `biomes_client.json` (RP-02's fog map — RP-02 owns it), `PROVENANCE.md` | THE WHOLE sf_nba CLIENT SIDE: 106 entities (94 RP-07 + 12 RP-06) + RP-08's 29 egg/cage/projectile entities and 7 attachables, 159 models, 136 animations, 94 controllers, 85 RCs, 38 particles, its textures (already in it) and sounds | 26.9 → ≈ 24 MB, self-contained |
| **Markers RP** | 0.2.1 → 0.2.2 | — | its own copies of `planks_oak` / `planks_spruce` (2 files it references from RP-04) | +0.1 MB |
| **PW-StripMine BP** (Realm) | 1.3.3 → 1.3.4 | — | manifest dependency → StripMine RP 3.1.0 | — |
| BP-02 / BP-01 / BP-03, Markers BP, LeafProbe BP, TestRunner BP | version bump | — | manifest dependencies (§8) | — |

**Not touched:** LeafProbe RP, RP-02's atmospherics content, BP scripts, any mob geometry/animation CONTENT (only their pack home changes).

## 5 · sf_nba (Naturalist) → PW-StripMine RP 3.1.0 — the Matched-Set Law, now unblocked

Today the animal client side is split four ways: entities in RP-06/07/08, models/animations/controllers/RCs in RP-07, particles in RP-02 (38) and RP-07 (38),
textures in all four packs (1,560 files × 4 = 13.3 MB × 4), sounds in StripMine RP. After the wave: StripMine RP is the complete Naturalist client pack, next
to its BP; production worlds (no Naturalist BP) carry NONE of it (−40 MB across RP-06/07/08, and no dead sf_nba definitions). The 197 + 23 + 8 sound edges
and every sf_nba id edge become internal. RP-06's `hammer_head_shark` etc. move with the rest.

## 6 · Atmospherics (RP-02 owns ALL of it)

Done in .141: RP-04's sun/moon/clouds removed. This wave: RP-07's 186 identical particle/environment shadows deleted; RP-04's `end_flash.png` migrates to
RP-02 if it differs from vanilla's, its `rain.png` (dead) and `environment/celestial/*` (2.3 MB, read by nothing) go; the sf_nba particles leave RP-02 for
StripMine RP (they are creature effects, not atmospherics). **Realm note:** StripMine RP 3.0.1 sits ABOVE RP-02 and ships a legacy `biomes_client.json`
that maps 71 biomes to RP-02's `realsource:fog_*` ids — on the Realm that file may be what the engine honours for fog. It goes (RP-02 owns fog); the build
diffs its mapping against RP-02's `biomes/*.client_biome.json` and reports any biome whose fog would change.

## 7 · The orphan purge (asks for a YES — 2,309 files, 112.7 MB, nothing references them)

| Category | Files | MB | Where |
|---|---|---|---|
| sf_nba textures no registry names (alternate skins, 45 unused items) | 312 × 4 | 8.5 × 4 | StripMine, RP-06, RP-07, RP-08 |
| Patrix `_n` / `_s` / `_mer` layers with no texture set (entity + item PBR — no engine support in our format) | 48 + 429 + 24 + 16 + 4 + 3 + 3 + 1 | 13.9 + 12.1 + 1.2 + 0.3 + 0.5 + 0.3 + 0.1 | RP-06, RP-08, RP-04, RP-01, RP-03, RP-11, RP-05, RP-02 |
| Java-layout leftovers (paths Bedrock never reads: `equipment/`, `villager2/hair`, wolf variants, `profession/`, root-level `pig.png`…) | 101 + 43 + 33 + 14 + 17 | 13.6 + 6.6 + 3.7 + 0.1 + 18.0 | RP-07, RP-06, RP-08 |
| Nested `Naturalist Add-On 26.1 BP/` folder inside StripMine RP | 123 (+1,094 more once counted as junk) | 4.6 | StripMine RP |
| Unreferenced block variants (banner/chest leftovers in RP-04; sapling/deadbush/cactus/pitcher `_vN` in RP-01) | 128 + 88 + 21 | 6.9 + 1.6 + 0.5 | RP-04, RP-01, others |

Every purged file is archived on my side (`_archive/orphans-2026-09-28/`) and, for the Patrix layers, exists in the Patrix source zip — nothing is lost, only
un-shipped. P11 audit performed: our registries (terrain/item/flipbook/texture-set/entity/attachable/particle/sound), the BPs' material keys, vanilla 1.26.50's
registries and entity files, and the engine's fixed-name directories were all censused before a file was called an orphan.

## 8 · Dependencies — ON after the dedupe, dependent → owner only (agreed)

Edges that REMAIN after the wave (everything else becomes internal): BP-02 → RP-04 + RP-01 + RP-02 · RP-06 → RP-07 (the 19 shared ids: villager nose/blink
+ `humanoid_articulated`, used by witch and villagers — a real shared owner) · StripMine BP → StripMine RP · Markers BP → Markers RP · LeafProbe BP →
LeafProbe RP · TestRunner BP → TestRunner RP · RP-07 → RP-02 only if any RP-07 entity still names an RP-02 particle after the sf_nba move (the build
reports). **Cost, stated plainly:** a manifest dependency pins the owner's exact version, so every future bump of an owner (RP-02, RP-04, RP-07…) forces a
version bump + re-upload of each dependent. Benefit: the game orders the owner below the dependent and refuses activation without it — the 09-22
"forgot a pack" failure becomes impossible. No cycles remain (verified by the edge census before stamping).

## 9 · Leaves → 128 (his pick still open; recommendation 128 × 8)

Tier: 221 files at 32×256 (210 `pw_<wood>_leaves_v0..5` + `_inner` + `_mer`/`_n`, 10 grass, fern), 8-frame wind flipbooks (5 ticks/frame, blended). RP-03's
128×1024 strips + 28 static 128s are the source art. Build steps: (1) recover the variant recipe by comparing v0..v5 at 32 px against the source (rotation /
mirror / hue offset / crop) and prove it by regenerating the 32s and diffing them against the shipped files; (2) regenerate all 221 at 128 with that recipe;
(3) place them in their owners (pw_ → RP-01, grass/fern → RP-05) with texture sets. Corrected cost (RGBA before mipmaps): 128 × 8 ≈ 116 MB, 128 × 4 ≈ 58 MB,
128 static ≈ 14.5 MB, today ≈ 7 MB. Waste found: 30 of the 48 `_mer` strips repeat one frame ×8 (the normals do animate) — unavoidable if the engine wants
layer sizes to match the colour strip; I verify that constraint before the rebuild.

## 10 · The tests, recreated (PW-TestRunner 0.3.0)

**p0 v3 — neutral mobs:** the existing 35-step lineup, re-run on the new stack (RP-07 1.4.15). No change in content.

**p1 v2 — hostile rig + block stations (test world, Creative, Easy):**
- h01–h11 — as 0.2.2 (zombie, skeleton, drowned, husk, pillager, stray, vindicator, witch, creeper, evoker, ravager; roofed pen, fire resistance, adults).
- b01–b08 — as 0.2.2 (torches, lanterns, lit furnaces, lava, portal, fires, kelp, campfire).
- **b09 XPACK PROBE (replaces the log experiment — the logs stay as a regression row):** three probe blocks defined by the TestRunner BP, their texture keys
  registered ONLY in the TestRunner RP: **A** → `textures/blocks/stone` (a path the TestRunner RP does not hold; RP-04 holds the Patrix 128, vanilla the 16-px);
  **B** → an RP-01-only 128 texture with a name vanilla does not have (`textures/blocks/mushroom_stem_v3`); **C** → a path that exists nowhere (the control: what "missing" looks like). Readings:
  A = Patrix stone → the engine searches the whole stack (highest holder wins) → L-DEDUP-4 SUPERSEDED by a synthesis ("own pack first, then the stack");
  A = 16-px vanilla stone → own pack then vanilla only → L-DEDUP-4 HOLDS for our packs; A looks like C → strictly pack-local → L-DEDUP-4 HOLDS absolutely.
  B confirms the same from the other side. Either way the wave is already safe (§2 rule 1); the probe only decides the LESSON.
- **b10 SUN** — `time set 12500`, look WEST: PASS = RP-02's warm-halo sun; FAIL = a white disc with rays (the old RP-04 sun). **b11 MOON** — `time set 18000`,
  look EAST: PASS = textured moon with craters; FAIL = a flat grey disc. **b12 CLOUDS** — clear weather, look up: PASS = soft detailed cloud shapes.
- **b13 LEAVES** — a 2-high wall of oak / birch / spruce / dark oak leaves + two `pw:` variant leaves 5 blocks north: PASS = fine 128 detail with a gentle
  shimmer; FAIL = soft 32-px blur / no shimmer. (Only meaningful after §9 ships in the same wave.)
- **b14 DEDUPE REGRESSION** — a row of eight blocks whose files changed home: quartz block, a candle, oxidized copper, dirt + grass block (RP-10 wins),
  a flower row (allium, blue orchid, rose bush — now RP-05), bricks, glass: PASS = Patrix + PBR look, nothing vanilla or checkered.
- s01–s04 — sizes (Realm; NO MOB in the test world → Skip). q9 clear.

**p2 — Realm lineup (`start p2`):** s01–s04 sizes (beetle, ant, sparrow, rat with the 1-m post + hit test) · **r01 deer, r02 alligator, r03 hammer-head shark
(water pen)** — the Naturalist client side now lives in StripMine RP 3.1.0: PASS = textured, animated; FAIL = magenta / invisible / vanilla-shaped.

## 11 · Static gates before anything ships (per pack)

A manifest + uuids · B every JSON parses (Bedrock-tolerant) · C **diff accounting**: every removed file is a classified shadow or orphan, every added file a
logged migration, nothing else changed · D **pack-local registry**: no terrain/item/flipbook/texture-set/entity/particle reference leaves its pack (0 misses,
down from RP-04 89 / RP-05 15 / RP-10 2) · E no MISSING references except the 18 `pw_side_*` (or 0 if he supplies the art / rules them dead) · F size vs 250 ·
G every global id referenced resolves in the stack ∪ vanilla, every remaining edge is in the manifest dependencies, no cycles · H renders: the b14 row, the
h01–h11 mobs, 6 sf_nba mobs from StripMine RP alone (StripMine RP 3.1.0 + BP 1.3.4 in an otherwise vanilla stack) · P package + delivery law (md5, byte-exact
download, smallest first).

## 12 · Phases and turn budget (P3)

| Phase | Work | Turns |
|---|---|---|
| A | census tool (DONE: `ownership_map.py`) + the decisions file from §2–§4 | done |
| B | `build_ownership_wave.py`: applies the map to all 11 packs (migrate → re-key → delete), writes the accounting log | 2 |
| C | gates A–G on every pack; before/after contact sheets for the 267 differing decisions + the b14 row | 1 |
| D | StripMine RP 3.1.0 assembly + the vanilla-stack render (gate H) + StripMine BP 1.3.4 | 1 |
| E | dependency stamping (all manifests) + cycle check | ½ |
| F | leaves 128: recipe recovery → regeneration → texture sets → RP-01 1.3.105 / RP-05 1.3.52 | 1–2 |
| G | TestRunner 0.3.0 (probe blocks, p1 v2, p2) + mock tests | 1 |
| H | journal D-C264, handoff rev 23, FOUNDATION lesson candidates, delivery (smallest first) + the install/run sheet | 1 |

Delivery order: TestRunner BP/RP → Markers RP → RP-11 → RP-05 → RP-10 → RP-01 → RP-06 → StripMine RP/BP → RP-07 → RP-08 → RP-02 → RP-04 → BPs.

## 13 · Decisions — RESOLVED 01:58 (his rulings) + what remains

1. RP-03/RP-04: **"250 MB is an absolute maximum; separate based on needs AND future foreseeable conflicts"** → applied in §3 (two packs by need: port in RP-04,
   custom families in RP-01, RP-03 retired). He vetoes the RP-01 choice if he wants the repurposed-RP-03 alternative.
2. Orphans: **"Archive all until we're certain we don't need them for research"** → every purged file goes to `_archive/orphans-2026-09-28/<pack>/<path>` (kept
   in the workspace + a zip delivered alongside the packs so he holds the archive too); the shipped packs drop them.
3. Leaves: **128 × 8** (locked).
4. `pw_side_*`: he has no art → verified none of the 18 base keys is referenced by any block (the slabs use the `_n/_e/_s/_d` face keys, which resolve) →
   the 18 are dead keys, deleted; `hardened_clay_stained_light_gray` re-pointed to the Bedrock name if any block uses it, else deleted.
5. His version screenshots: still not received — §0 stands on the Packs folder until they arrive.
6. **Tests: DELIVERED** — PW-TestRunner BP + RP **0.3.0** (gate 41/41, mock 146/146): lineup p1 v2 (27 steps: h01–h11, b01–b08, **b09 XPACK probe**, b10 sun,
   b11 moon, b12 clouds, b13 leaves, b14 dedupe-regression row, q9) and lineup **p2** (Realm: s01–s04 sizes, r01 deer, r02 alligator, r03 hammer-head shark in a
   pool). Delivered to the NEW gofile folder (his 02:00 request) — https://gofile.io/d/Szv3tbtz.
7. Build order from here: phase B (the wave builder) → C (gates + sheets) → D (StripMine RP 3.1.0) → E (dependencies) → F (leaves 128×8) → H (docs + delivery to
   the new folder, smallest first). One test run after delivery: p0 → p1 → p2.


**Rev 6 note (22:xx 09-28, D-C273):** RP-07 1.4.16 has SHIPPED (Converter B round 2). The ownership wave's RP-07 build therefore moves to **RP-07 1.4.17** (never reuse a version number); RP-06 stays at 1.4.12 for the wave. The wave must start from `_build/rp07-1416`.

**Rev 7 note (23:xx 09-28, D-C274):** RP-07 1.4.17 has SHIPPED (Converter B round 3). The ownership wave's RP-07 build moves to **RP-07 1.4.18** and must start from `_build/rp07-1417`. If the ravager (RP-06) ships before the wave, the wave's RP-06 moves on accordingly.

**Rev 8 note (23:3x 09-28, D-C276):** RP-07 1.4.18 has SHIPPED (ravager + trader llama blanket layer + axolotl/frog). The ownership wave's RP-07 build moves to **RP-07 1.4.19** and must start from `_build/rp07-1418`. NOTE for the wave: `geometry.ravager` lives in RP-07 while its entity is in RP-06 — an ownership item.

**Rev 9 note (01:0x 09-29, D-C277):** RP-07 1.4.19 and RP-06 1.4.12 have SHIPPED (sizes, guardians + animations, spider/bee/tadpole/piglins/bogged, zombified piglin head). The ownership wave's builds move to **RP-07 1.4.20** (from `_build/rp07-1419`) and **RP-06 1.4.13** (from `_build/rp06-1412`). New ownership items from the sweep: `geometry.spider` lives in RP-07 while its entity is in RP-06 (as the ravager); RP-06's humanoid entities animate from RP-07's `animations/humanoid_articulated.animation.json`; RP-07's `pw_animation_shims.animation.json` redefines 55 VANILLA animation ids stack-wide (the shims that cost motion — enderman, squid/glow squid, dolphin, tadpole, parrot dance, silverfish, giant, parched — are to be dropped, the equine/llama `setup` shims kept; `MOB-SWEEP-2026-09-29.md` §3b).
