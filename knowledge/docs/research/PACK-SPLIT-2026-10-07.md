# Can a resource pack be "parted out" and stay under 250 MB per part? (2026-10-07)

**Status: research only. No pack was changed or built.** Data: `PACK-SPLIT-2026-10-07.json` (beside this file). Scripts:
`_docs/research/tvr_src/split_plan.py` (sizes every part and checks every reference stays inside its part) and
`split_rp07.py` (RP-07 by creature).

**His question (00:23 CT 10-07):** *"Can a resource pack be 'parted out' (part 1 / part 2, or multipart that recombines) keeping
each part under 250 MB?"*

---

## 1. The answer

**Yes — as two (or more) complete resource packs that the game stacks together.** There is no "multi-volume" pack format:
one `.mcpack` is exactly one pack, and the game never glues files back into one pack. The "recombining" happens at run time,
because the game loads every active pack in the stack and merges the registry files (terrain, flipbook, items, sounds,
languages) across all of them. RP-13 (Architecture) was already split out of RP-04 this way on 10-06.

Three things make the parts behave like one pack:
1. **Each part is complete and independent**: its own `manifest.json` (its own header uuid and module uuid), pack icon and
   version, and it carries every file its own entries point at.
2. **They sit next to each other in the stack** (same place the old pack was), so any file that overrides vanilla by path
   still wins in the same order.
3. **Optional delivery and activation helpers:**
   - a `.mcaddon` = one zip that holds several `.mcpack` files, so one tap imports all the parts (Microsoft: ".mcaddon — a zip
     file that contains .mcpack or .mcworld files");
   - a manifest `dependencies` entry (uuid + exact version) from part A to part B, so activating A also asks for B.
     **Our packs use no manifest dependencies today** (checked: RP-01, RP-04, RP-13 have none). Adding one is optional; it
     needs B's exact version, which our "versions are never reused" law already guarantees changes in lockstep.

**What splitting does NOT fix:** the terrain atlas (one 8192² sheet for ALL packs together — see the TEXTURE-VARIANT doc's
atlas alarm), block permutations (those live in the behavior packs), and memory. Splitting only fixes the per-pack file size.

---

## 2. Bedrock's stacking rules that matter (with sources)

| Kind of file | Across packs | What it means for a split | Source |
|---|---|---|---|
| Textures, sounds, models referenced by **path** (e.g. `textures/entity/bed/red.png`) | **Overwritten**: the higher pack's file wins | a path-override part must keep the same stack position | bedrock.dev "Overwriting assets"; MS resource-pack intro ("each object that has the same name … overwritten by the latest applied pack") |
| `terrain_texture.json`, `item_texture.json`, `flipbook_textures.json` | **Merged** (each pack adds its keys) | each part ships ONLY its own keys — start from an empty file | bedrock.dev "Overwriting assets" |
| `sounds.json`, `sound_definitions.json`, `music_definitions.json` | **Merged** | each part ships only its own events + the sound files they name | bedrock.dev |
| Language files (`texts/*.lang`), UI files | **Merged** | each part ships the lines for its own items/blocks; `languages.json` in each part | bedrock.dev |
| Files with identifiers: client entities, geometry, animations, animation / render controllers, particles | **Replaced by identifier** (the higher pack's definition wins) | keep each identifier in exactly one part | bedrock.dev |
| `*.texture_set.json` (PBR) | **Not merged**; the higher pack's set for the same texture wins, and **a set can only use images in its own pack** | the set, its colour, its `_n` and `_mer` must all be in the same part | Microsoft Texture Sets intro (quoted below) |
| `blocks.json` | **Not documented** in the sources found | our own evidence: RP-04 overrides `minecraft:orange_terracotta` with only `{sound, isotropic}` and terracotta is not reported broken → entries appear to merge per block, field by field (**UNVERIFIED**) | — |
| `textures/textures_list.json` | not documented; it is a per-pack list of the pack's own texture paths | each part lists only its own paths | — |

Microsoft (Texture Sets): *"Texture Set definitions can only reference images that exist in the same resource pack as the
definition."* · *"Texture images in higher priority resource packs do not override a Texture Set's reference to a texture in
its own pack."* · *"In the resource pack stack, Texture Set definitions for the same texture resource don't get merged. The
higher priority pack's Texture Set definition will override the lower priority one."*

**Our own laws on top (the split must obey them):**
- **L-DEDUP-4 / KEY-FOLLOWS-FILE:** registry entries, flipbook sources and texture-set layers resolve pack-locally — one part
  holds a key AND every file it names. (History: the 09-28 b09 probe showed terrain texture *paths* do resolve across the whole
  stack — candidate L-TEX-RESOLVE — but pack-local stays our rule by his ownership ruling, and texture sets are pack-local by
  Microsoft's own text.)
- **L-KEY-MERGE (witnessed, D-C265):** a terrain key defined in two packs merges into one un-weighted array and only the first
  texture is drawn (the `snow_layer` warning). **Never define the same key in two parts.**
- Complete packs only (no overlays); every part ≤ 250 MB unzipped; versions never reused.

---

## 3. How to split so that nothing breaks (procedure)

1. **Choose a seam where nothing crosses it** — whole systems, never half a family: blocks vs entities; falling-tree copies vs
   the rest; one creature group vs another.
2. **Assign every file to one part.** For each key, set, flipbook entry, client entity, geometry, animation, controller and
   sound event, its whole closure goes into the same part.
3. **Split the merged registries**: each part gets its own `terrain_texture.json`, `flipbook_textures.json`,
   `item_texture.json`, `textures_list.json`, `sounds.json` / `sound_definitions.json`, `texts/` with only its own entries.
4. **New manifest for the new part** (new header + module uuid, a new name, version 1.0.0); the old pack keeps its uuid and
   bumps its version.
5. **Gate** (the checks `split_plan.py` already runs, plus the usual ones):
   - no key, identifier or sound event defined in two parts;
   - every key / set layer / flipbook source / entity texture / geometry resolves inside its own part;
   - `geo_ref_check.py` across all parts; each part ≤ 250 MB.
6. **Install**: both parts active, adjacent, in the old pack's place. Deliver as two `.mcpack` files or one `.mcaddon`.
   On laptop worlds remember the copy-at-creation law (remove and re-add packs to an existing world).

---

## 4. Concrete split plans for our biggest packs (sizes unzipped, from the current builds; 0 cross-part references unless stated)

| Pack today | Size | Part | Size | Files | Contents |
|---|---:|---|---:|---:|---|
| **RP-07** Neutral Mobs 1.4.45 | **195.3 MB** (biggest) | RP-07A | ~137.1 MB | — | half the creatures (331 client-entity files, balanced by size) + everything no entity file names directly (vanilla path overrides: `textures/entity/equipment` 13.4 MB, `sounds/sf/nba` 10.8 MB, menagerie items, particles) |
| | | RP-07B | ~60.7 MB | — | the other creatures (332 entity files) with their textures, sets, geometry, animations, controllers and sounds; 1.2 MB of shared files copied into both |
| **RP-04** Basic 1.3.159 | 194.7 MB | **RP-04A Basic Blocks** | **143.3 MB** | 5,340 | `textures/blocks` + terrain / flipbook / blocks.json + block models + texts |
| | | **RP-04B Basic Entities** | **51.4 MB** | 402 | `textures/entity` (beds, chests, signs, banners… 48.8 MB) + `textures/environment` + items + `item_texture.json` + `entity/` (pw_seat, pw_lead) + entity models — **checked: 0 cross-part references** |
| **RP-01** Tectonic 1.3.125 | 188.3 MB | RP-01A Tectonic core | 130.9 MB | 2,694 | biomes, blocks, sounds, leaves, bark, planks, vines, leaf litter |
| | | **RP-01B Falling Trees** | **57.4 MB** | 714 | `models/entity/ft_tpl` + `falling_tree*` geometry, entity, render controllers, animations, `textures/entity/fallingtree`, and the 11 `pw_leaves2/*_fall` atlases (the falling-tree entity names them) — **0 cross-part references** |
| RP-01, 3-way | | 01A core 61.5 · 01B Falling Trees 57.4 · **01C Vines 69.4** | | 2,586 / 714 / 111 | 01C = `textures/blocks/pw_vine/` + its 28 vine keys (`pw_vine_v0–v11`, `_r0–r11`, `_extra`, `_extra_r`, `vine`, `vine_single`) and 26 flipbook entries; **0 cross-part references** |
| RP-12 Gallery 1.0.1 | 175.3 MB | (by painting range) | — | — | 172.6 MB is `textures/gallery`; split by painting numbers with each painting's entity / texture together (not sized here) |
| RP-13 Architecture 1.0.1 | 92.1 MB | — | — | — | already split from RP-04 on 10-06 |

**Recommendation (if he wants headroom now):**
- **RP-04 → RP-04A Blocks + RP-04B Entities** is the cleanest seam in the suite: zero shared keys, and entity textures are
  path overrides that do not touch the terrain atlas.
- **RP-01 → split out the Falling Trees** (57.4 MB of geometry the client loads at boot). That also isolates the
  L-GEO-BUDGET risk (total cube count) into one pack he can remove to test.
- **RP-07** is the biggest, but splitting creatures needs a per-creature closure list; the first cut above is a starting
  point, not a gate-checked plan (the checker flagged 834 entity→texture references in the by-folder trial; the by-creature
  split has no checker run yet). **Investigation incomplete for RP-07.**
- Before splitting anything for SIZE: the 128 px list in the TEXTURE-VARIANT doc removes 104.7 MB (RP-01 −36.1 MB from the
  vines alone, RP-13 −48.1 MB) without any new pack.

---

## 5. Open questions for Abs0lum

1. Do you want headroom now (split RP-04 and RP-01 into Blocks/Entities and Core/Falling Trees), or only when a pack nears
   250 MB? (Today the biggest is RP-07 at 195.3 MB.)
2. Should the parts declare a manifest dependency on each other (activating one asks for the other), or stay independent
   like RP-13 (you add both by hand)?
3. Would one `.mcaddon` per delivery (all parts in one file, one tap) be easier for you than separate `.mcpack` files?

## 6. Sources
- Microsoft Learn — Texture Sets introduction: https://learn.microsoft.com/en-us/minecraft/creator/reference/content/texturesetsreference/texturesetsconcepts/texturesetsintroduction
- Microsoft Learn — Pack manifest (dependencies): https://learn.microsoft.com/en-us/minecraft/creator/reference/content/addonsreference/packmanifest
- Microsoft Learn — Resource pack introduction (pack stacking): https://learn.microsoft.com/minecraft/creator/documents/resourcepack
- Microsoft Learn — Minecraft file extensions (.mcpack / .mcaddon): https://learn.microsoft.com/en-us/minecraft/creator/documents/minecraftfileextensions
- Microsoft Learn — Comprehensive pack contents (lists blocks.json etc.; no merge rules stated): https://learn.microsoft.com/minecraft/creator/documents/comprehensivepackcontents
- Bedrock Wiki — Overwriting assets (merged vs overwritten files): https://wiki.bedrock.dev/concepts/overwriting-assets.html
- Our evidence: decision journal D-C263 / D-C265 (L-DEDUP-4, L-KEY-MERGE, b09 probe), line 787 (250 MB rule), 2470 (RP-04 split
  for size); HANDOFF-2026-10-06 (RP-13 split).
