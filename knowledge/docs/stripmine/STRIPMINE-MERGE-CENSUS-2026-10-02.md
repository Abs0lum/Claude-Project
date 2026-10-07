# STRIPMINE MERGE CENSUS — 2026-10-02

Read-only study. Nothing was built, moved or deleted. Machine-readable twin: `STRIPMINE-MERGE-CENSUS-2026-10-02.json` (same folder).
Scratch tools that produced every number: `/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad/smcensus/{census,analyse,report}.py`.

His ruling (D-C465, journal line 2579, verbatim): *"Put everything from stripmine into appropriate packs we already have; but keep them labeled based on the pack they came from. We may need to start separating packs (like basic) into 2 parts, labeled by which is loaded first."*

---

## 0. PLAIN-LANGUAGE SUMMARY (for a beginner)

**What StripMine is today**

- StripMine is two packs: **StripMine RP 3.0.1** (the "looks and sounds" half, 4,932 files, 37.0 MB unzipped / 27.7 MB as a .mcpack) and **StripMine BP 1.3.13** (the "behaviour" half, 2,660 files, 9.8 MB unzipped / 2.4 MB as a .mcpack).
- The **behaviour half** holds 608 creatures, 550 spawn rules, 617 items, 523 loot tables, 149 recipes, 29 blocks and 111 script files. They come from 8 sources:
  - **Naturalist 26.1** (namespace `sf_nba`): 138 creatures, 488 items, 29 blocks, 149 recipes, all 111 scripts.
  - **Animals and Fauna** (`_anf`): 319 creatures. (The add-on file is `Animals-and-Fauna.mcaddon`, not "Animals & Friends".)
  - **World Animals** (`_wa`): 46. **yCreatures Savanna** (`_ysav`): 46. **yCreatures Trial** (`_ytri`): 29. **WWA** (`_wwa`): 17. **Wildlife Sanctuary** (`_ws`): 12. **Immersive Fauna Savanna** (`_ifs`): 1.
- The **looks half is mostly copies.** All 1,559 Naturalist pictures in StripMine RP are byte-for-byte identical to pictures that RP-06, RP-07 and RP-08 *each* already hold.
  - StripMine RP's own unique content is small: Naturalist **sounds** (1,304 files, 10.8 MB), the Naturalist **lists** (sound list, item-icon list, block-texture list, `blocks.json`), 7 "worn item" models (crab hats, butterfly wings, peacloak), and a handful of global Vibrant-Visuals files from RealSource.
  - It also holds two things that do nothing: 817 "Oreville" sound files (7.1 MB) that no sound list points to, and a misplaced copy of the Naturalist *behaviour* pack (1,217 files) inside the looks pack. The game ignores that copy.
- **The creatures' bodies already live in our packs.** Their models, animations, client files and textures are in RP-07 (561 of 608 creatures), RP-08 (29: eggs, cage, plushies, projectiles) and RP-06 (12 hostile ones: sharks, snakes, scorpions, eels, piranha, ravenous hyena).
  - All 470 menagerie creatures already sit in RP-07 under `…/pw_menagerie/<source>/` folders.
  - So the "move" is mostly about the behaviour half, the sounds and the lists.

**Where each part would go (recommended)**

| StripMine part | Goes to | Why |
|---|---|---|
| All behaviour (creatures, spawn rules, items, blocks, loot, recipes, functions, structures) | **BP-02 Tectonic** | It is the only content behaviour pack we have. BP-01 is scripts for weather and sky, BP-03 is diagnostics, and his ruling D-C249 keeps TestRunner separate. |
| Naturalist scripts (111 files) | **BP-02**, stored but **not switched on** at first | They have never run (StripMine BP has no script module, D-C231). Switching them on is a separate decision. |
| Naturalist sounds + sound lists | **RP-07 Neutral Mobs** | RP-07 already holds these creatures' bodies and the menagerie sounds. |
| Naturalist item-icon list (441 icons) | **RP-08 Items** | RP-08 is the items pack and already holds all 446 icon pictures. |
| Naturalist block textures (28 keys) + `blocks.json` (14) + 7 worn-item models | **RP-07** | RP-07 holds their pictures and the chrysalis/starfish/crab/wing models. |
| Global VV files (`pbr/global.json`, `local_lighting.json`, `cubemap.json`, `biomes_client.json`, `flame_atlas.png`) | **RP-02 Atmospheric** | RP-02 owns atmosphere and lighting. Today StripMine is the only pack that ships these. |
| 1,559 Naturalist pictures, 11 environment pictures, entity.material, enderman file, nested BP copy, PROVENANCE.md | **Not copied** (archived, never deleted) | Each is either already in our packs byte-for-byte, a known duplicate (the D-C284 backlog says to remove the enderman), or inert. |

**Labelling.** Every moved file keeps a folder segment naming its source: `…/sf_nba/…` for Naturalist and `…/pw_menagerie/<source>/…` for the others, which is already how RP-07 and the menagerie files are laid out. Each receiving pack also gets one `PROVENANCE-STRIPMINE.json` that lists every moved file and every merged list entry with its source add-on and its original StripMine path. **No identifier is renamed**: renaming would delete existing creatures in a world.

**Conflicts that need his decision** (full list in section 1)

1. Putting creature behaviour into BP-02 means the creatures can no longer be removed by unticking one pack. This conflicts with his 09-30 15:11 ruling (journal line 1586): "other animals → RP-07 if under 250 MB, else a new 'Wildlife' pack", and with the D-C328 note "keep them in the removable creature pack".
2. Naturalist scripts: keep them stored and dormant, or switch them on? Switching them on is blocked until the API version is settled. Naturalist was written against `@minecraft/server` **2.4.0**, and BP-02 pins **2.3.0**.
3. StripMine's `sounds.json` changes **61 vanilla mobs' sounds and 17 vanilla sound events**. 29 of those entries (230 references, including **thunder, flint-and-steel "ignite", the player, zombie, creeper and spears**) point to `oreville_ans:*` sound names that no pack and no vanilla file defines. That may make those sounds silent in his world today. This is static evidence only and needs his ears.
4. The 817 Oreville sound files: archive them, carry them along dormant, or restore their missing sound list from the original Naturalist add-on on Drive.
5. Expect a visible change. StripMine's plain copies of 761 Naturalist creature pictures sit *above* RP-06/07/08's texture sets for the same pictures. By the D-C421 "separated" reading, those sets may be switched off today. Dropping StripMine would likely switch on depth and shine (MERS/normal) for Naturalist creatures. Accept the change, or freeze today's look?
6. Smaller placement choices: block textures in RP-07 or RP-01 (his 09-27 ruling put BP-02's custom-block client files in RP-01); item icons in RP-08 or RP-07; worn items in RP-07 or RP-08.

**Sizes against the 250 MB cap**

- Nothing goes over the cap, and nothing comes within 10% of it (225 MB).
- **RP-07** grows from 191.8 MB to **203.6 MB** unzipped, or **210.7 MB** if the Oreville sounds are carried along. That is 81–84% of the cap. As a .mcpack it goes from 149.7 MB to at most 168.6 MB.
- **BP-02** grows from 11.5 MB to about 21.7 MB. **RP-08** and **RP-02** each grow by less than 0.2 MB.

**The split idea (RP-04 Basic in two parts)**

- **Not needed for StripMine.** RP-04 receives nothing and sits at 189.7 MB unzipped (75.9%).
- **It is clean if he wants headroom.** RP-04 divides into "Blocks" (140.9 MB) and "Objects" (entity and sky pictures, 48.8 MB). No block texture entry points into the objects half (checked: 0 references), so the two halves never overlap and their order does not matter.
- **Label the order anyway.** In Bedrock's list the pack at the **top wins**, which means the bottom pack is applied **first**. So "RP-04A (load 1st)" is placed *below* "RP-04B (load 2nd)".
- **RP-07 is the pack that will actually need a split.** It doubled in one round (74.9 → 149.7 MB as a .mcpack between 1.4.37 and 1.4.40), and his menagerie ruling is "add EVERY mob". The natural split is "vanilla/Patrix mobs" (137 MB) and "wildlife by source" (Naturalist + menagerie, about 55 MB today, about 66 MB after StripMine's sounds).

**Verification gate for every phase:** a file census and an identifier census, then the dedicated-server load test `/home/claude/tools/bds_load.py` (or `bds_civtest.py`), then his device for looks and sounds. A dedicated server draws nothing, so it cannot check looks or sounds.

---

## 1. DECISIONS HE MUST MAKE

| # | Decision | Options | Recommendation | Evidence |
|---|---|---|---|---|
| D1 | Home of creature **behaviour** | (a) BP-02; (b) keep a separate creature BP (= a new or renamed pack, against the new ruling) | (a), per the new ruling | BP list §2.1; ruling conflict C2/C3 |
| D2 | Naturalist **scripts** | (a) move dormant (not imported) = exactly today's behaviour; (b) activate from BP-02 `main.js` | (a) now, (b) later as its own round | StripMine BP manifest has no script module (`_build/stripmine-bp-1313/manifest.json`); nested original pins `@minecraft/server` 2.4.0 vs BP-02 2.3.0 |
| D3 | **Oreville** 817 ogg (7,087,591 B) | (a) archive (not in any pack); (b) carry dormant into RP-07; (c) restore the `oreville_ans` sound list from the Drive Naturalist original | (a), plus open (c) as an investigation | 0 sound definitions reference `sounds/oreville/` (analysis.json `sound_events`) |
| D4 | StripMine **sounds.json vanilla overrides** (61 entities + 17 events; 29 keys → 230 undefined `oreville_ans:*` refs) | (a) carry as-is (no change); (b) carry only the `sf_nba` entries (vanilla sounds return); (c) witness first | (c), then (a) or (b) | §3.4 |
| D5 | Naturalist **block** client side (28 terrain keys, 14 `blocks.json` entries) | (a) RP-07 (images + chrysalis geometry already there); (b) RP-01 (his 09-27 ruling: BP-02's custom-block client files live in RP-01) | (a) | `rp07-1443/models/blocks/chrysalis_stage0.geo.json`; journal line 787 |
| D6 | Naturalist **item icons** (441 keys) | (a) RP-08; (b) RP-07 | (a) | RP-08 holds `textures/item_texture.json` + all `textures/sf/nba/items` images |
| D7 | 7 **attachables** | (a) RP-07 (their geometry `geometry.sf_nba.crab/butterfly_wings/peacloak` is there); (b) RP-08 | (a) | `rp07-1443/models/entity/sf/nba/attachable/` |
| D8 | **Global VV files** from StripMine (RealSource-1.9.1) | (a) all to RP-02 (keeps today's look); (b) retire the legacy `biomes_client.json` (D-C263 flagged it as a possible fog override on the Realm) | (a), then judge (b) in a VV round | StripMine is the only pack in our stack shipping these 5 paths (`merge_files_presence`) |
| D9 | **Separated texture sets** (761 Naturalist pictures) | (a) accept that sets switch on when StripMine's plain copies leave; (b) freeze today's look | (a) + witness | §3.5 |
| D10 | **Labelling convention** | confirm §5 | confirm | — |
| D11 | Nested `Naturalist Add-On 26.1 BP/` inside StripMine RP | (a) archive only; (b) also keep it inside a pack | (a) | inert; 159 of its 1,217 files differ from BP 1.3.13 |
| D12 | **Split** | (a) no split now; (b) split RP-04 now (A Blocks / B Objects); (c) plan an RP-07 split for the next menagerie wave | (a) + (c) | §6 |
| D13 | **What "250 MB" measures** | the .mcpack archive (what `package_round_1002d.py` asserts) or unzipped | ask; this report gives both | `tools/package_round_1002d.py` line 13 `CAP = 250 * 1000 * 1000` on the archive |
| D14 | **Wilds / Wildlife exceptions** | does the new "packs we already have" ruling cancel the planned "AbsolutRealism Wilds" pair (Jurassic + capture orbs) and the fallback "Wildlife" pack? | ask | journal line 1586 |

### Conflicts with older rulings (for his decision)

- **C1, 09-22 (line 507):** "the best parts go into StripMine to avoid licensing complications".
  - Superseded by D-C320 / custom-instructions §9 (personal use only; any asset may go in any pack).
  - No conflict in substance; StripMine's reason to exist is gone.
- **C2, 09-30 15:11 (line 1586):** "Pokemon (capture orbs) + Jurassic → their own removable pack pair ('AbsolutRealism Wilds'); other animals → RP-07 Neutral if it fits under 250 MB, else a new 'Wildlife' pack".
  - StripMine holds **no** Jurassic or Pokemon content. CENSUSED: source folders are only nba/anf/wa/wwa/ysav/ytri/ws/ifs, identifier namespaces are only `sf_nba:` and `pw:`, and a grep for jurassic/pokemon/kingdom_of_the_giants found nothing.
  - So Wilds is untouched by this merge. The RP side fits RP-07 under 250 MB, which matches the old ruling.
  - The new ruling may cancel the future Wilds pair and Wildlife pack (D14).
- **C3, D-C328 retro-sweep (line 1584):** "keep them in the removable creature pack".
  - Merging behaviour into BP-02 removes that removability (D1).
- **C4, D-C249 (line 553):** TestRunner stays a separate pack that loads last.
  - So StripMine must **not** go into TestRunner. No conflict with the proposal.
- **C5, 09-27 (line 787):** RP-01 Tectonic takes the custom-block client files (BP-02's matched set).
  - Conflicts with D5(a) if Naturalist blocks count as "custom blocks".
- **C6, D-C284 backlog (line 1117):** "remove the duplicate enderman from StripMine RP at its next build".
  - Consistent: the enderman file is not moved.
- **C7, D-C263 KEY-FOLLOWS-FILE / ownership law (line 779):** a key, its image and its texture set in one pack.
  - D5(a), D6(a) and D7(a) satisfy it, because the images are already in the destination.
  - The ×3 duplication of the Naturalist textures (RP-06/07/08) is an existing breach. It is not created by this move.
- **C8, D-C240 L-HOME-1 (line 518):** "every change goes into its existing relevant pack; new packs only when necessary".
  - Agrees with the new ruling.
- **C9, his 10-01 14:41 rule (`tools/bds_load.py` `discard`):** "never delete — move into _garbage".
  - Every "not copied" item is archived, never deleted.

---

## 2. INVENTORY BY SOURCE

### 2.1 StripMine BP 1.3.13 (`/home/claude/_build/stripmine-bp-1313`) — 2,660 files, 9,800,898 B

Manifest: `PW StripMine BP v1.3.13`, uuid `0caba18b-cb39-4c06-9057-d6587197d0ed`.

- min_engine `[1,21,30]`, one `data` module.
- **No script module and no dependencies.** The 111 script files have never run (D-C231, line 448).

| Source (folder / suffix) | Files | Bytes | Entities | Spawn rules | Items | Loot | Other |
|---|---:|---:|---:|---:|---:|---:|---|
| Naturalist 26.1 (`sf_nba:`; root folders + `sf/nba`, `sf_nba`) | 1,215 | 4,576,809 | 138 (131 root + 5 `utility/` + 2 `projectiles/`) | 102 | 488 | 134 (`loot_tables/sf/nba`) | 29 blocks, 149 recipes, 8 BP animations (6 files), 59 controllers (38 files), 10 functions (`functions/sf/nba`), 2 features + 2 feature rules (ant hills), 2 structures (`structures/sf_nba`), `item_catalog/crafting_item_catalog.json`, 111 script files (109 .js + `info_book_page_names.json` + `deno.json`), `texts/` (pack name only), stray `update_recipe_enum.js` at the root |
| Animals and Fauna (`pw:*_anf`, `pw_menagerie/anf`) | 996 | 3,827,006 | 319 | 318 | 38 | 319 | 8 animations (1 file), 2 controllers (1 file) |
| World Animals (`pw:*_wa`) | 207 | 566,849 | 46 | 44 | 64 | 51 | 2 animations |
| yCreatures Savanna (`pw:*_ysav`) | 110 | 417,433 | 46 | 29 | 21 | 12 | 2 controllers |
| yCreatures Trial (`pw:*_ytri`) | 57 | 165,411 | 29 | 28 | — | — | — |
| WWA (`pw:*_wwa`) | 46 | 133,910 | 17 | 16 | 6 | 7 | — |
| Wildlife Sanctuary (`pw:*_ws`) | 24 | 99,419 | 12 | 12 | — | — | — |
| Immersive Fauna Savanna (`pw:*_ifs`) | 2 | 10,037 | 1 | 1 | — | — | — |
| StripMine meta (manifest, icon, PW-DEPENDENCIES.md) | 3 | 4,024 | | | | | |
| **Total** | **2,660** | **9,800,898** | **608** | **550** | **617** | **523** | |

- Full identifier lists per source: JSON `stripmine_bp_groups.<src>.ids`.
- Naturalist per-folder bytes: entities 3,237,054 · scripts 423,914 · spawn_rules 299,238 · items 255,731 · loot 133,327 · recipes 71,489 · blocks 68,328 · controllers 49,940 · item_catalog 23,821 · functions 5,106 · animations 1,931 · feature_rules 1,866 · structures 1,273 · features 1,086 · texts 172 · root 2,533.
- File format versions (JSON `format_versions`): entities range 1.12.0–1.21.90 (387 at 1.16.0, 135 at 1.21.50); spawn rules 1.8.0 (448) / 1.17.0 (101) / 1.11.0 (1); blocks 1.20.20–1.21.60; items 1.21.30 (485) / 1.21.40 (132); recipes 1.21.50.

**Script modules.** Entry would be `scripts/main.js` (76 lines; there is no manifest script module today).

- 109 .js files. 101 are reachable from `main.js`. 8 are unreached because their imports are commented out: block/Egg, HamsterBed, HamsterHut, SnailEgg, entity/RandomVariantSpawner, fix_info_book_entity_order, item/EelBuckets, item/Plushies.
- `main.js` imports 53 modules by **root-relative** names (`import "entity/Scorpion.js"`, `"block/Chrysalis.old.js"`, `"item/Whistle.js"`, `"compatability.js"` …). It is the only file that does this. Every other import is `./` or `../` relative (113) or `@minecraft/server` (77).
- APIs used: `system.beforeEvents.startup` (2.x style, 3 files), `blockComponentRegistry` / `itemComponentRegistry`. `worldInitialize` appears only inside a comment (`entity/Hamster.js` line 223).
- Custom components registered: `sf_nba:whistle`, `sf_nba:skunk_flamethrower`, `sf_nba:hamster_placer` (+ block ones). The chrysalis and egg registrations are commented out.
  - 15 block/item files declare `minecraft:custom_components`.
  - No name collides with BP-02's `pw:*` components (pw:flue, pw:ground_behaviour, pw:hatch, pw:hearth, pw:randomize_variant, pw:seat, pw:wall_dual).
- Full import graph: JSON `script_import_graph`.

### 2.2 StripMine RP 3.0.1 (`/home/claude/_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack`) — 4,932 files, 36,984,811 B

Manifest: `PW StripMine v3.0.1`, uuid `4208a758-1111-4073-a3d0-9e1db762bdf7`, min_engine `[1,21,120]`, capabilities `["pbr"]`.

| Group (source) | Files | Bytes | Contents | Already elsewhere? |
|---|---:|---:|---|---|
| Naturalist pictures `textures/sf/nba/**` | 1,559 png | 13,182,963 | entity 1,088 · items 446 · blocks 13 · particle 10 | **Yes, byte-identical** in RP-06, RP-07 and RP-08 (1,559/1,559 each; each of those packs holds 3,081 `textures/sf` files = these 1,559 + 761 MERS/normal pngs + 761 texture sets) |
| Naturalist sounds `sounds/sf/nba/**` | 1,304 ogg | 10,792,704 | mob 1,228 · step 36 · item 36 · book 4 | **No** (only here) |
| Naturalist lists | 6 | 682,316 | `sounds/sound_definitions.json` 427,812 (595 events, all `sf_nba.*`) · `sounds.json` 135,979 (171 entity entries: 110 `sf_nba:` + **61 vanilla**; 20 events, **17 vanilla**; interactive: zebra, donkey, mule, skeleton/zombie horse + ladder) · `textures/item_texture.json` 45,286 (441 keys) · `textures/terrain_texture.json` 2,967 (28 keys) · `blocks.json` 1,130 (14 entries) · `textures/textures_list.json` 69,142 | Keys collide with **none** of our 12 RPs (0 terrain, 0 item, 0 blocks.json, 0 sound-event and 0 sounds.json entity collisions with RP-07) |
| Naturalist attachables | 7 | 5,826 | `sf_nba:butterfly_wings`, `crab_{orange,brown,red,blue,yellow}`, `peacloak` | No (geometry + textures in RP-07) |
| Naturalist material `materials/entity.material` | 1 | 700 | — | Identical in RP-02 |
| Oreville sounds `sounds/oreville/ans/**` | 817 ogg | 7,087,591 | obfuscated names | **Referenced by no sound definition anywhere.** Donor not in `PROVENANCE.md`. Inferred to be part of the Naturalist family: `sf_nba` items carry the tag `oreville:is_throwable` and `sounds.json` uses `oreville_ans:*` event names (inference) |
| RealSource-1.9.1 VV "experience layer" | 16 | 224,924 | `biomes_client.json` 12,632 · `cubemaps/cubemap.json` 530 · `local_lighting/local_lighting.json` 5,355 · `pbr/global.json` 507 · `textures/flame_atlas.png` 154,080 · `textures/environment/destroy_stage_0..9.png` + `pixel.png` 51,820 | The 11 environment pngs are identical in RP-02; the other 5 paths exist in **no** other pack of ours |
| Vanilla override `entity/enderman.v1.8.animation.json` | 1 | 2,291 | client entity `minecraft:enderman` (min_engine 1.8.0) | RP-07 beats it since 1.4.22 (L-ENT-PREC); D-C284 backlog: remove |
| Misplaced `Naturalist Add-On 26.1 BP/` | 1,217 | 4,609,826 | a full Naturalist BP (manifest pins `@minecraft/server` 2.4.0, script entry `scripts/main.js`) | Older copy of BP content: 1,058 identical paths, **159 differ** from BP 1.3.13. Inert inside an RP (his world BP list, journal line 486, shows no such pack) |
| StripMine meta | 4 | 395,670 | manifest 734 · icon 2,288 · `PROVENANCE.md` 390,100 (5,326 lines; 1,209 entries name paths that no longer exist; 822 zip paths are not in it) · `PW-DEPENDENCIES.md` 2,548 | — |
| **Total** | **4,932** | **36,984,811** | | |

### 2.3 Where the creatures' client files live today (answer to his question)

Checked against every StripMine BP entity identifier (CENSUSED: StripMine RP, RP-06, RP-07, RP-08, TestRunner RP, Markers RP):

| StripMine BP source | Client entity home |
|---|---|
| Naturalist (138) | RP-07 94 · RP-08 29 (eggs, cage, plushies, projectiles, info book, hamster wheel …) · RP-06 12 (cave/coral snake, rattlesnake, desert/jungle scorpion, electric eel, great white + hammerhead shark, moray ×2, piranha, ravenous hyena) · none 3 (invisible helpers `bear_harvest_pathfinder`, `custom_hit_test`, `load`) |
| anf 319 · wa 46 · ysav 43 (+3 lay-egg helpers with no client) · ytri 29 · wwa 17 · ws 12 · ifs 1 | **all RP-07** (`entity|models/entity|animations|animation_controllers|render_controllers|particles|sounds|textures/…/pw_menagerie/<src>/`) |

- **RP-07 menagerie client files by source:** anf 1,601 / 9,136,620 B · wa 650 / 6,749,635 · wwa 208 / 5,467,313 · ysav 339 / 3,250,282 · ytri 205 / 1,263,438 · ws 88 / 388,624 · ifs 15 / 263,846. Total 3,106 files / 26.5 MB.
- **Naturalist client side by pack:**
  - RP-07: 94 client entities, 245 model files (299 geometries), 94 animation files (1,922 animation ids), 48 render-controller files (140 ids), 38 particles, 3,081 `textures/sf`.
  - RP-06: 12 client entities, 12 models, 12 animation files, 3,081 `textures/sf`.
  - RP-08: 29 client entities, 3,081 `textures/sf`.
  - RP-02: 38 particles (byte-identical to RP-07's 38).
  - StripMine RP: textures (copies), sounds, lists, attachables.

---

## 3. DEPENDENCIES AND CONFLICTS IF MOVED

### 3.1 Identical file paths in destinations (would overwrite)

- **BP side (StripMine BP vs our BPs):**
  - `scripts/main.js` exists in all five of our BPs. It must never be copied over; move the Naturalist file to `scripts/stripmine/sf_nba/main.js` instead.
  - `texts/en_US.lang` + `texts/languages.json` collide with BP-03 and TestRunner BP only (BP-02 has no texts). They contain only Naturalist's pack name and description plus a Marketplace `contentKey` line, so they are not moved.
  - No other path collisions. No StripMine BP path is a vanilla behaviour-pack path (0 hits against `_intake/bedrock-samples/behavior_pack` 1.26.50).
- **RP side (StripMine RP vs each of our RPs; JSON `rp_path_overlaps`):**
  - The only collisions are the 1,559 identical Naturalist pngs (RP-06/07/08) and the 12 identical RP-02 files (environment pngs + `entity.material`).
  - Everything else is a merge file, which must be **merged, never copied** over: `textures/terrain_texture.json`, `textures/item_texture.json`, `blocks.json`, `sounds/sound_definitions.json`, `sounds.json`, `textures/textures_list.json`.
  - Nothing new would overwrite a different file.

### 3.2 Duplicate identifiers

Entity, item, block, recipe, spawn-rule, feature, feature-rule, BP animation, BP controller, function and loot-table identifiers in StripMine BP vs BP-01, BP-02, BP-03, Markers BP and TestRunner BP: **0 collisions** (JSON `id_collisions_vs_our_bps`).

- 0 duplicates inside StripMine BP.
- 0 `minecraft:` identifiers in StripMine BP, so it overrides no vanilla behaviour file.
- Client side: the only shared client-entity id is `minecraft:enderman` (handled by D-C284).

### 3.3 Merge files (merged by key, never copied)

| Merge file | StripMine has | Destination has | Collisions |
|---|---|---|---|
| `sounds/sound_definitions.json` | 595 `sf_nba.*` events, 427,812 B | RP-07 (42,946 B); also RP-01, RP-02 | 0 with RP-07/06/08/02/01/04 |
| `sounds.json` | 171 entity + 20 event + interactive | RP-07 (114,916 B) | 0 keys shared with RP-07 (but 61 entity + 17 event keys override **vanilla**, §3.4) |
| `textures/item_texture.json` | 441 keys | RP-08 (44,138 B) / RP-07 (13,494 B) / Markers | 0. Icon keys used by StripMine BP items: 438 resolve only in StripMine RP, 129 in RP-07, 0 missing |
| `textures/terrain_texture.json` | 28 `sf_nba.*` keys | RP-07 has none (new file); RP-01/03/04/05/10/11/Markers/TestRunner have their own | 0 |
| `blocks.json` | 14 `sf_nba:*` | RP-07 none (new); RP-01, RP-04, RP-10, TestRunner have their own | 0 |
| `textures/textures_list.json` | 69,142 B | RP-07 18,603 B | union adds 1,559 lines (~74 KB) |
| `item_catalog/crafting_item_catalog.json` (BP) | 23,821 B | BP-02 has none | none (copy as-is; merge if BP-02 ever gets one) |
| `texts/*.lang` | RP: none. BP: pack name only | — | not moved |
| `biomes_client.json`, `pbr/global.json`, `local_lighting/local_lighting.json`, `cubemaps/cubemap.json` | RealSource copies | **no other pack of ours ships these paths** (RP-02 uses `biomes/`, `lighting/`, `atmospherics/`) | none; they move to RP-02 unchanged |

### 3.4 Things in StripMine that override vanilla or our own files

1. **`sounds.json` overrides 61 vanilla entities** (armadillo … zombie_pigman, including `player`, `zombie`, `skeleton`, `creeper`, `chicken`, `lightning_bolt`) **and 17 vanilla individual events** (`ignite`, `break`, `item.{iron,copper,golden,diamond,netherite}_spear.{attack_hit,attack_miss,use}`).
   - 29 of these keys reference `oreville_ans:*` events, 230 references in all.
   - Those events are **defined nowhere**: not in StripMine's `sound_definitions.json` (all 595 keys are `sf_nba.*`), not in any of our 12 RPs, and not in vanilla 1.26.50's 1,851 definitions.
   - Examples: `ignite → oreville_ans:pciaaz`; `lightning_bolt` thunder and explode; `player` 76 refs (weapon-variant maps); `zombie` per-sword variants.
   - **Static only (P1):** these sounds *may* be silent in his world today. Witness question: does thunder sound? Does flint-and-steel make its ignite sound? Do weapon swings make sounds?
2. **`biomes_client.json`** (legacy RealSource) sits above RP-02. D-C263 (line 778) flagged it as possibly the fog map the engine honours on the Realm.
3. **`pbr/global.json`, `local_lighting.json`, `cubemap.json`** (RealSource): StripMine is today the *only* source of these global VV settings in our stack. Moving them to RP-02 keeps them in effect.
4. **`textures/flame_atlas.png`** (RealSource; a vanilla path).
5. **`entity/enderman.v1.8.animation.json`** (`minecraft:enderman`): neutralised by RP-07's min_engine 1.21.0 (L-ENT-PREC, D-C284).
6. **Our own files:** none differ. The 1,559 + 12 shared paths are byte-identical, and the decision journal (line 2557) recorded "0 terrain keys shared with ours or vanilla".

### 3.5 Texture-set shadowing (expected visible change)

- 761 of StripMine's 1,559 plain pngs have a `.texture_set.json` at the same stem in RP-06, RP-07 **and** RP-08 (counted: 761 in each).
- StripMine is above all three in his order.
- By the D-C421 reading (journal line 2340: "per-path, top pack with ANY file wins; a set wins only inside its own pack"), the Naturalist creatures may be drawn **without** their MERS/normal maps today. That reading was witnessed for blocks ("no depth"); applying it to entity textures is an inference.
- After StripMine leaves, the top holder becomes RP-08, which has the sets. Expect Naturalist creatures to gain depth and shine.
- Witness required. This also overlaps D-C421 report (3), "some mobs too shiny".

### 3.6 Script integration (BP has one script entry per pack)

| Pack | Script entry | `@minecraft/server` | `@minecraft/server-ui` | min_engine |
|---|---|---|---|---|
| BP-01 Atmospheric Effects 1.3.35 | scripts/main.js | 2.3.0 | — | 1.21.120 |
| **BP-02 Tectonic 1.3.205** | scripts/main.js (13 js) | **2.3.0** | 2.0.0 | 1.21.120 |
| BP-03 Diagnostics 1.3.34 | scripts/main.js | 2.0.0 | — | 1.21.120 |
| Markers BP 0.2.1 | scripts/main.js | 2.0.0 | — | 1.21.80 |
| TestRunner BP 0.5.12 | scripts/main.js (30 js) | 2.3.0 | 2.0.0 | 1.21.120 |
| **StripMine BP 1.3.13** | **none** (manifest has no script module) | **none declared** | — | **1.21.30** |
| Naturalist original (nested copy) | scripts/main.js | **2.4.0** | — | 1.21.60 |
| Naturalist `scripts/deno.json` (dev typings, stale) | — | 1.17.0 | 1.3.0 | — |

- **Blocker (activation only):** Naturalist code targets 2.4.0 and BP-02 pins 2.3.0. Activating needs one of these:
  - `tools/api_audit.py` (L-API-STABLE gate) showing every member the 101 reachable files use exists in 2.3.0, or
  - BP-02 moving to ≥ 2.4.0, with the same audit run on BP-02's own 13 files.
- A dormant move (D2a) has no blocker. Activation would also need:
  - one line in BP-02 `main.js` (`import "./stripmine/sf_nba/main.js";`), and
  - rewriting the 53 root-relative imports in the Naturalist `main.js` to `./…`. Moving the tree under `scripts/stripmine/sf_nba/` breaks root-relative names; the other 108 files use relative imports and move unchanged.
- min_engine 1.21.30 → 1.21.120: files parse by their own `format_version`.
  - Evidence: BDS loaded BP-02 1.3.200 + StripMine 1.3.12 with 0 errors (journal line 2086).
  - The merged result still needs its own BDS load.
- Capabilities / experimental toggles:
  - No BP declares capabilities.
  - StripMine content needs no experimental toggle; it loads on BDS today.
  - The word "experimental" in StripMine BP JSON (558 files) is the harmless `"is_experimental": false` in entity descriptions.
  - All RPs except Markers declare `["pbr"]` (StripMine RP too), so nothing changes there.
  - **No manifest dependency** is added (L-VV-2: a BP dependency on an RP disables VV).

---

## 4. DESTINATION PROPOSAL (by pack role)

| Group | Destination | Reasoning |
|---|---|---|
| All StripMine BP behaviour (all 8 sources) | **BP-02** | Only existing content BP (holds entities, spawn_rules, items, blocks, loot, recipes, features, structures already). BP-01/BP-03 are script-only. TestRunner is separate by ruling D-C249. New folders in BP-02: `animations/`, `animation_controllers/`, `functions/`, `item_catalog/`. |
| Naturalist scripts | **BP-02** `scripts/stripmine/sf_nba/**`, not imported (D2) | Today's behaviour unchanged |
| Hostile vs neutral | **No reshuffle** | Client files already follow role: hostile Naturalist mobs are in RP-06, neutral ones and all menagerie mobs in RP-07, object-like entities in RP-08. StripMine RP holds no client entities to sort (only the enderman, which is dropped). |
| Naturalist sounds + `sound_definitions` + `sounds.json` + `textures_list` | **RP-07** | Creature sounds belong with the creatures. RP-07 already ships sounds, `sound_definitions.json` and `sounds.json` (menagerie). 0 key collisions. |
| `terrain_texture.json` + `blocks.json` (Naturalist blocks) | **RP-07** (D5) | Images (`textures/sf/nba/blocks`) and chrysalis/starfish geometry are in RP-07 (KEY-FOLLOWS-FILE). Alternative: RP-01 by the 09-27 ruling, which would need 13 images + 4 sets + 3 geometries copied there. |
| `item_texture.json` (441 icons) | **RP-08** (D6) | Items pack; holds every icon image + set |
| Attachables (7) | **RP-07** (D7) | Their geometry is in RP-07 |
| VV globals (5 paths) | **RP-02** (D8) | Atmosphere and lighting owner |
| Oreville (817) | **archive** (D3) | Unreferenced |
| `textures/sf/**` copies, environment pngs, `entity.material`, enderman, nested BP, `PROVENANCE.md`, StripMine manifests | **archive** | Duplicates / inert / replaced |

**Blocks: which BP?** BP-02, because it already holds our custom blocks. The 29 Naturalist blocks use format 1.20.20–1.21.60 and `minecraft:custom_components`. BDS accepted them inside StripMine 1.3.12 and 1.3.13.

---

## 5. LABELLING CONVENTION

1. **Folder segment = source add-on**, inside each engine folder.
   - Menagerie: `<folder>/pw_menagerie/<src>/…`, already in place in BP and RP-07 (`src` ∈ anf, wa, wwa, ysav, ytri, ws, ifs).
   - Naturalist: `<folder>/sf_nba/…` for path-free files: BP `entities/ spawn_rules/ items/ blocks/ animations/ animation_controllers/ features/ feature_rules/`, and `scripts/stripmine/sf_nba/`.
   - **Keep path-referenced files at their current, already-labelled paths:** `loot_tables/sf/nba/**` (entity files name these paths), `functions/sf/nba/**` (the path *is* the function name), `structures/sf_nba/**` (the path *is* the structure id), `recipes/sf/nba/**`, RP `textures/sf/nba/**`, `sounds/sf/nba/**`, `models/entity/sf/nba/**`.
   - Hygiene note: YSav BP files sit under folder names with spaces (`entities/pw_menagerie/ysav/Savanna Animals/{Antelopes,Fixed}/…`, `…/ysav/No-Mobs/`). They load today (BDS), but they break naive shell tooling. Either keep them byte-identical or normalise them to `savanna_animals/`, `no_mobs/` during the move (path-free files, so this is safe).
2. **Identifiers are never renamed.** `sf_nba:` and `pw:*_<src>` already carry the source label. Renaming would orphan creatures and items already in a world.
3. **Merge-file entries** (terrain/item keys, sound events, `sounds.json` entries, `blocks.json`) carry their label in the key prefix (`sf_nba.` / `sf_nba:` / `pw:*_<src>`). JSON has no safe comment slot in every file type, so the per-entry record lives in the provenance file.
4. **One `PROVENANCE-STRIPMINE.json` per destination pack** (root; not read by the engine). Contents:
   - one record per moved file: `{dest_path, source_pack: "PW StripMine BP 1.3.13" | "PW StripMine RP 3.0.1", origin_addon, original_path, bytes, sha1}`;
   - per merge file, the list of merged keys with their origin;
   - estimated sizes ~0.43 MB (RP-07), ~0.05 MB (RP-08), ~0.45 MB (BP-02).
5. **Description stamp** (description-stamp law): e.g. "… Includes StripMine BP 1.3.13 (Naturalist, AnF, WA, YSav, YTri, WWA, WS, IFS)". RESTRICTED-ASSETS lines get their "pack + file" column updated (custom instructions §9) in both copies.
6. **Engine-fixed paths** (cannot carry a source folder):
   - `manifest.json`, `pack_icon.png`, `texts/*.lang`, `texts/languages.json`
   - `textures/terrain_texture.json`, `item_texture.json`, `flipbook_textures.json`, `textures_list.json`
   - `blocks.json`, `sounds.json`, `sounds/sound_definitions.json`
   - `biomes_client.json`, `pbr/global.json`, `local_lighting/local_lighting.json`, `cubemaps/cubemap.json`, `materials/*.material`
   - vanilla override paths (`textures/flame_atlas.png`, `textures/environment/*`)
   - BP `item_catalog/crafting_item_catalog.json`
   - models only load from `models/entity/**` or `models/blocks/**` (L-MODELS-ENTITY candidate, D-C355).
   - Subfolder loading: entity files in subfolders are witnessed (p18/p19 menagerie). Spawn rules in subfolders are common practice but unwitnessed here; the existing menagerie rules already rely on it (journal line 1691).

---

## 6. SIZE (cap = 250,000,000 B; the 90% line is 225,000,000 B)

| Pack | Before unzipped | Before .mcpack | Added | After unzipped | % cap | After .mcpack (upper bound) |
|---|---:|---:|---:|---:|---:|---:|
| RP-07 (Oreville archived) | 191,759,618 | 149,655,760 | 11,872,236 | **203,631,854** | 81.5 | 161,527,996 |
| RP-07 (Oreville carried) | 191,759,618 | 149,655,760 | 18,959,827 | **210,719,445** | 84.3 | 168,615,587 |
| RP-08 | 86,163,124 | 81,955,822 | 99,286 | 86,262,410 | 34.5 | 82,055,108 |
| RP-02 | 93,953,756 | 92,582,445 | 174,104 | 94,127,860 | 37.7 | 92,756,549 |
| BP-02 | 11,494,726 | 896,256 | 10,248,902 | 21,743,628 | 8.7 | ~3.3 MB expected (StripMine BP zips to 2.4 MB) |

- "Added" includes the estimated provenance files.
- The .mcpack upper bound treats added bytes as incompressible. .ogg files barely compress; JSON compresses a lot.
- **Result:** no pack exceeds the cap or reaches the 90% line under either measure.
- **Other packs today, unzipped / .mcpack:**

  | Pack | Unzipped | .mcpack |
  |---|---:|---:|
  | RP-01 | 163.9 | 134.2 |
  | RP-02 | 94.0 | 92.6 |
  | RP-03 | 119.9 | 120.3 |
  | RP-04 | **189.7** | **187.6** |
  | RP-05 | 46.2 | 46.1 |
  | RP-06 | 75.9 | 71.0 |
  | RP-07 | 191.8 | 149.7 |
  | RP-08 | 86.2 | 82.0 |
  | RP-10 | 22.5 | 22.0 |
  | RP-11 | 4.1 | 4.1 |
  | TestRunner RP | 35.1 | 35.1 |

- **Bonus space (not part of this move):** the Naturalist `textures/sf` set (3,081 files, 20.2 MB) is held three times, in RP-06 (20.5 MB incl. 12 models/anims), RP-07 and RP-08. One owner (RP-07) would free about 40 MB from RP-06 and RP-08. That belongs in the ownership-dedupe wave and must respect KEY-FOLLOWS-FILE: the RP-08 icons stay with RP-08's item keys.

### 6.1 Splitting a pack in two — what is safe

**Engine behaviour across packs, with confidence:**

- **Same file path in two RPs:** the pack higher in the list replaces the file wholesale.
  - High confidence. Witnessed repeatedly; `stack_census.py`, b09 (D-C266/267).
- **Texture path lookup:** whole-stack, highest holder first, vanilla last.
  - High. Witnessed by b09.
- **`terrain_texture.json` / `item_texture.json`:** the engine merges entries from every pack. A key defined in **two** packs is merged into an un-weighted array, and only the first element draws.
  - Merge across packs: high. Array behaviour: medium-high (the engine's own content-log line, D-C265).
  - Rule: **a key must be defined in exactly one half.**
- **Texture set:** applies only from the pack that holds the winning image ("separated" pattern, D-C421).
  - Medium. Witnessed for blocks only.
  - Rule: **image + `.texture_set.json` + MERS/normal layers in the same half.**
- **`blocks.json`, `flipbook_textures.json`, `sound_definitions.json`, `sounds.json`, `texts/*.lang`, `textures_list.json`:** merged per entry across packs.
  - High for `blocks.json` and lang, because RP-01/04/10 each ship `blocks.json` and they work together. Medium-high for the others.
  - Rule: each entry lives in one half.
- **Geometry / animation / render-controller / particle identifiers:** global across packs.
  - High. RP-08 entities already use RP-07 geometry.
  - These may cross halves, but per the ownership law keep them with their owner.

**RP-04 split test** (`_build/rp04-155`: 5,706 files, 189,688,904 B; 1,832 terrain keys, 29 flipbooks, 268 `blocks.json` entries):

- **RP-04A Basic — Blocks:** 140,871,125 B (74%).
  - `textures/terrain_texture.json`, `flipbook_textures.json`, `blocks.json`, `textures/blocks/**` (5,281 files, 139.3 MB), `models/blocks/**` (42), `texts/**`, its share of `textures_list.json`.
- **RP-04B Basic — Objects & Sky:** 48,817,779 B (26%).
  - `textures/entity/**`: boat 22.0 MB, shulker 9.8, bed 5.8, chest 4.7, endercrystal 1.2, banner 1.1, misc 1.6, bell.
  - `textures/environment/**` (incl. celestial 2.3 MB), `entity/pw_seat.entity.json`, `models/entity/pw_seat.geo.json`.
- **Independence checked:** 0 terrain keys and 0 flipbooks point at `textures/entity` or `textures/environment`. The halves share no path and no key, so the order between them does not matter.
- Still labelled:
  - **"RP-04A AbsolutRealism Basic — Blocks (load 1st: place BELOW 04B)"**
  - **"RP-04B AbsolutRealism Basic — Objects (load 2nd: place ABOVE 04A)"**
- Rule for the labels: **top of the list wins**, so "loaded first" means lower in the list.
- New uuids for 04B; 04A keeps RP-04's uuid so worlds keep it active.
- If blocks alone ever outgrow one pack, split `textures/blocks` by family. pw_* is 28.5 MB, grass 9.5, lava 7.0, dirt 5.7, log 4.1 … Each family's keys, images, sets and flipbook entries move together.
- **Not needed now.** RP-04 is at 75.9%.

**RP-07 is the real split candidate** (needs a reference census before building):

- **RP-07A "Neutral Mobs — vanilla & Patrix":** 137.0 MB (109.6 MB entity textures + 27.4 MB client JSON, models, animations).
- **RP-07B "Neutral Mobs — Wildlife (labelled by source)":** Naturalist 28.2 MB + menagerie 26.5 MB, plus StripMine sounds 10.8 MB, about 66 MB.
- **Shared merge files** (`sounds.json`, `sound_definitions.json`, `item_texture.json`, lang): split by key.
- **Cross references** (RP-06 → RP-07 animation ids, RP-08 → RP-07 geometry) are global ids and keep working (high).
- This revives his old "Wildlife pack" idea as a *part of an existing pack*, which may satisfy both rulings (D12/D14).

---

## 7. PHASED MOVE PLAN (no building in this study)

| Phase | Work | Verify after | Effort |
|---|---|---|---|
| 0 Baseline | Freeze the inputs. Run `stack_census.py`, `ownership_map.py`, `entity_precedence.py` with StripMine in → baseline JSON. BDS baseline: `bds_load.py` with BP-02 1.3.205 + StripMine BP 1.3.13 (+ BP-01/03/Markers/TestRunner) → error list. | baseline saved | S (part of 1 turn) |
| 1 BP merge → BP-02 | Copy StripMine BP into BP-02 with the §5 paths (Naturalist root files → `…/sf_nba/`; menagerie paths unchanged; loot/functions/structures/recipes paths unchanged). Scripts → `scripts/stripmine/sf_nba/` dormant (D2a). `item_catalog` copied. Provenance file. Manifest description stamp. No BP-02 code change. | (a) **file census equality**: every StripMine BP file is moved (sha1 equal) or listed as not moved with a reason. (b) **identifier census**: BP-02 ids = old ∪ StripMine, 0 duplicates. (c) every `loot_table` / `function` / `structure` path named in an entity or feature resolves. (d) `main.js` unchanged (no new import). (e) **BDS gate `tools/bds_load.py`**: new BP-02 alone ⊇ baseline (0 new errors). (f) TestRunner static gates. | M (1–2 turns) |
| 2 RP merges | RP-07: `sounds/sf/**`, `sound_definitions` merge, `sounds.json` merge (D4 choice), `textures_list` union, `terrain_texture.json` + `blocks.json` (D5), attachables (D7). RP-08: `item_texture` merge (D6). RP-02: 5 VV paths (D8). Provenance files; stamps. | (a) **JSON merge checks**: merged key set = A ∪ B exactly, values byte-equal to their source, 0 collisions, valid JSON. (b) every `sounds/…` path in a definition exists in the stack. Pre-existing defects, carried as-is and listed: 18 `sounds/sf` ogg that no definition uses; 16 referenced paths StripMine lacks, of which 8 are vanilla-named (block/azalea/break1-4, block/beehive/exit, mob/fox/spit1-3) and 8 are missing Naturalist files (finch idle1-3, snail idle, snake rattleshort, sparrow idle1-3). (c) every item icon / terrain key resolves, with image + set in the same pack (KEY-FOLLOWS-FILE). (d) **stack resolution diff vs baseline**: the only expected changes are winners moving from StripMine to RP-08 for `textures/sf` (identical bytes) and texture sets now applying (§3.5). (e) `entity_precedence.py` unchanged. (f) size gate ≤ 250,000,000 B (`package_round_1002d.py` pattern). | M (1–2 turns) |
| 3 Retire StripMine | StripMine RP + BP retired (archived, never deleted). RESTRICTED-ASSETS both copies updated. `PW-DEPENDENCIES.md` regenerated (depscan). TestRunner text that names "StripMine BP 1.3.x" (p2, p9–p11, p18–p21, bump, runner) updated in its next build. Handoff. | BDS load of the full final BP set (`bds_load.py` / `bds_civtest.py` if the Civitas pilot rides along). Packaging asserts the cap. | S (1 turn) |
| 4 His witness | One world edit, all together: remove StripMine RP + BP, install BP-02 / RP-07 / RP-08 / RP-02 new versions. Laptop worlds copy packs at creation (engine law), so either re-activate or use his new world. Run p18/p19 (all creatures render, Naturalist sounds, item icons, chrysalis/egg/ant-hill blocks, crab hats / wings). Check thunder and flint-and-steel sound (D4). Check Naturalist creature shine (§3.5). | his reports (witness rule) | his time |
| 5 Later, separate rounds | Ownership dedupe of `textures/sf` ×3 (~40 MB), Oreville restore (D3c), script activation (D2b; API audit), RP-07 split when a wave pushes it toward 225 MB. | each its own gates | M–L each |

Total for phases 1–3: about 4–6 turns, so a phased plan is required (P3). Shippable after phase 3. Phases 1 and 2 must ship **together**. If BP-02 lost the Naturalist definitions while StripMine RP stayed, or the other way round, creatures would lose behaviour or sound.

---

## 8. PREMISE AUDIT (P11) and limits

- **Searched for menagerie and Naturalist client files** (CENSUSED): StripMine RP 3.0.1 zip, RP-01 116, RP-02 206, RP-03 66, RP-04 155, RP-05 58, RP-06 1428, RP-07 1443, RP-08 1412, RP-10 151, RP-11 139, Markers RP 0.2.1, TestRunner RP 0.7.1.
  - EXCLUSION-VERIFIED: LeafProbe RP 0.3.1 (11 files per journal line 492; not a creature pack).
  - NOT CENSUSED: his device's installed copies. Builds and deliveries are assumed byte-equal to what he installed. Note that `stack_now.py` ORDER still names older installed builds (RP-10 1.3.42, RP-08 1.4.9 …); this study used the newest builds named in the brief.
- **Identifier collision scan:** BP-01 135, BP-02 205, BP-03 134, Markers BP 0.2.1, TestRunner BP 0.5.12 (CENSUSED). Vanilla 1.26.50 bedrock-samples was used for vanilla paths and sound definitions.
  - The sample has no `textures/environment/` folder, so the "vanilla path" check for those pngs could not be made from it. They are known vanilla paths.
- **Static only (P1):** every behavioural statement here (silent sounds, texture sets switching on, subfolder spawn-rule loading) is unwitnessed until he confirms on device.
- **Guesses, marked:** the Oreville add-on identity; the RP-07 split sizes (no reference census yet); the BP-02 .mcpack size after the merge (~3.3 MB); provenance file sizes.
