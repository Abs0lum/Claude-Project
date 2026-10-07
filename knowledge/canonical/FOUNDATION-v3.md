# AbsolutRealism Foundation — v2 (current as of v1.2.36)

> **Authoritative reference for project identity, locked invariants, and all confirmed lessons.** This document supersedes:
> - `ABSOLUTREALISM-FOUNDATION-v1_2_31.md`
> - `foundation-patch-v1_2_32.md`, `foundation-patch-v1_2_32-1.md`
> - All `FOUNDATION_PATCH_v*.md` (v1.0.1 → v1.2.32)
> - The lessons sections of all `ABSOLUTREALISM-HANDOFF-v*.md`
>
> Companion documents:
> - `OPERATING-MANUAL-v2.md` — How to work on this project (witness rule, failure modes, communication, ship protocol). Read FIRST.
> - `ARCHITECTURE-v2.md` — Technical schema, scanner, geometry, formats, scripts, pack stack
> - `HISTORY-v2.md` — Per-version chronicle v1.0.0 → v1.2.36
> - `CURRENT-STATE-v1_2_36.md` — Current ship status, candidate lessons, queued work, file index

---

## §1. PROJECT IDENTITY

### 1.1. Name and stylization

**Public/display name**: `AbsolutRealism`. Stylized in pack manifests and folder names as `Abs0lutRealism` — note the **digit zero "0"** in place of the second letter "o", matching the user's gamertag stylization. NOT a lowercase-O. Both forms refer to the same project; `AbsolutRealism` is preferred for prose and human-readable documents, `Abs0lutRealism` is preferred for filesystem paths and manifest fields.

**Historical name**: The project was named `PatrixWorld` from inception through v1.0.0. It was renamed `Abs0lutRealism` at the v1.0.1 ship. Historical artifacts (older handoffs, conflict notes) may still reference `PatrixWorld` — do not rename retrospectively.

**Internal namespace prefix**: `pw:` — preserved across the rename. Block IDs, biome IDs, sound events, atmospherics IDs, particle IDs, entity IDs, animation references all use the `pw:` prefix. This is a save-compatibility invariant and MUST NOT be changed (would orphan all existing player worlds).

### 1.2. Project description

AbsolutRealism is a Bedrock 26.x texture, behavior, and shader-data pack ecosystem derived from the Patrix Java resource pack. Target platforms: PS5 (primary), mobile (Android), and Windows/console. Render distance target: 18 chunks on PS5 with deferred rendering and Vibrant Visuals enabled.

**Pack identity (v1.0.1+)**: 128/256x blend. Most textures are at 128x with selective 256x integration on a per-item basis (first integrated item: furnace family). NOT marketed as 128x-vs-256x tiers; resolution is a quality detail, not a marketing differentiator.

**Subpacks**: NONE in v1.2.31. Subpack tiering (mobile/console-low/console-high/PC at differing resolutions) is BACKLOGGED until after marketplace publish.

### 1.3. License rule

All source assets must be **CC0**, **CC-BY**, or other commercially-permissive licenses. Never copy from RC (Render Comparison / RealismCraft) binary archives or other proprietary mod assets. When CC-BY is used, attribution must be recorded in a `credits.md` at the resource pack root.

**Confirmed CC0/CC-BY sources used in pack**:
- v1.2.9 water normals: OGA CC-BY 3.0 (Keith333 / Benkyou Studio) — RP-02 ships `credits.md`
- v1.2.9 sand: ambientCG `Ground033` (CC0)
- v1.2.9 ice: ambientCG `Ice002`, `Ice004` (CC0)

### 1.4. WITNESS RULE (governing principle)

When the user reports a visual observation, behavior, or factual claim about the pack, **defer to the user**. The user is closer to ground truth than the model. Do not defend the model's prior assertion against the user's witness. Specifically:

- **Visual observations**: user sees X in-game; model "thinks" Y from code reading. User wins. Investigate.
- **Factual claims about pack contents**: user says "we have X"; model believes "we don't." Verify by extraction (`unzip -l` or filesystem listing) before contradicting.
- **Runtime behavior**: user reports script crash, parse error, or visual breakage; model verifies JSON parses correctly. JSON parsing ≠ runtime correctness — the user's runtime observation IS the validation (Lesson #77).

**Origin**: established in v1.0.0 era, extended via Lesson #144 (v1.0.1) to cover factual claims, reaffirmed every release.

---

## §2. PACK STACK (16 packs)

### 2.1. Activation order (LOCKED INVARIANT)

Bedrock applies resource packs **bottom-to-top** in the active list. Pack later in the activation order overrides packs earlier. The required activation order is:

**Resource Packs (bottom → top)**:
```
RP-01 — AbsolutRealism Tectonic RP            (bottom — base)
RP-02 — AbsolutRealism Atmospheric Effects RP
RP-03 — AbsolutRealism PBR RP
RP-04 — AbsolutRealism Basic RP
RP-05 — AbsolutRealism Flora RP
RP-06 — AbsolutRealism Hostile Mobs RP
RP-07 — AbsolutRealism Neutral Mobs RP
RP-08 — AbsolutRealism Items RP
RP-09 — AbsolutRealism Trees RP   (folder name "RP-09-pw-Trees-RP" preserved)
RP-10 — AbsolutRealism Terrain RP
RP-11 — AbsolutRealism Ores RP                (top — overrides all)
```

**Behavior Packs (bottom → top)**:
```
BP-01 — AbsolutRealism Atmospheric Effects BP   (bottom)
BP-02 — AbsolutRealism Tectonic BP
BP-03 — AbsolutRealism Identification Diagnostics BP
BP-04 — AbsolutRealism Mob Spawn BP
BP-05 — AbsolutRealism Trees BP   (folder name "BP-05-pw-Trees-BP" preserved)
```

(Optional BP-06 Lens Flare BP from v1.2.0 was not bundled in v1.2.16+; deferred.)

**Why two folders retain `pw-` prefix**: `RP-09-pw-Trees-RP` and `BP-05-pw-Trees-BP` source-folder names retain the `pw-` prefix because their internal blockstate identifiers (`pw:oak_leaves` etc.) all reference the `pw:` namespace. The output filename uses `AbsolutRealism-Trees-{BP,RP}` per the rebrand convention; the source-folder rename was deemed not worth the rework cost.

### 2.2. Pack capabilities

Packs declaring `pbr` capability MUST be at `min_engine_version = [1, 21, 120]` minimum:
- RP-01, RP-02, RP-03, RP-08, RP-09, RP-11 ship `pbr`
- All packs (16/16) at `min_engine_version = [1, 21, 120]` since v1.2.14 (was inconsistent prior; v1.2.14 standardized)
- Manifest `metadata.product_type: "addon"` added v1.2.14 (per Bedrock 1.26.x convention; allows VV to enable regardless of capabilities and keeps achievements working)
- Manifest `metadata.authors: ["Abs0lum"]` standardized v1.2.14

### 2.3. UUID stability (LOCKED INVARIANT)

All 17 manifest UUIDs (16 visible packs + 1 historical, plus internal `modules[*].uuid`) are PERMANENTLY LOCKED. They MUST NOT change between versions. UUID stability is a save-compatibility invariant — changing them orphans the pack on existing worlds.

**Exception**: the v1.0.1 rename `PatrixWorld → Abs0lutRealism` preserved all UUIDs intentionally. ONLY `header.name`, `header.description`, and `header.version` were touched.

---

## §3. FORMAT VERSIONS — LOCKED TABLE

The following format versions are LOCKED at the values shown. Any drift causes silent parse rejection.

| Domain | format_version | File | Notes |
|---|---|---|---|
| Manifests | `2` | `manifest.json` | Stable across all packs |
| `min_engine_version` (manifest) | `[1, 21, 120]` | `manifest.json` | Floor for VV registration; any pack below silently fails to register VV files (Lesson #20) |
| Atmospherics | `1.21.40` | `atmospherics/*.json` | (Lesson #21) — `1.21.90` is silently rejected |
| Lighting | `1.26.0` | `lighting/*.json` | Required for time-keyframed ambient color/illuminance feature (Lesson G2) |
| Color grading | `1.21.90` | `color_grading/*.json` | Valid (this one passes 1.21.90 parser) |
| Water | `1.26.0` | `water/*.json` | `sampleWidth` deprecated; do not include (Lesson #23) |
| Client biome | `1.21.120` | `client_biome/*.json` | (Lesson #28 — 1.21.90 rejected) |
| Local lighting | `1.21.120` | `local_lighting.json` | Block-level light source registry |
| Custom blocks (BP) | `1.21.80` | `BP-*/blocks/*.json` | Permutation/state schema (lesson #93) |
| MERS texture sets | `1.21.30` | `**/texture_set.json` | Color + Normal + MERS triplet schema |
| Animations | `1.8.0` | `**/animations/*.json` | Stable, no recent change |
| Entity render controllers | `1.10.0` | `**/render_controllers/*.json` | Stable |
| Particles | `1.10.0` | `**/particles/*.json` | Stable |
| Geometry | `1.21.0` (typical) | `**/models/**/*.geo.json` | Some legacy models still at `1.16.0` |

### 3.1. Reserved filenames (Microsoft Learn-mandated)

These VV directories have RESERVED default filenames. Custom-named files in those directories are loaded as additional profiles, but the default profile MUST use the reserved filename:

| Directory | Reserved default filename |
|---|---|
| `atmospherics/` | `atmospherics.json` (NOT `global.json`) |
| `lighting/` | `global.json` (yes — only one with `global`) |
| `color_grading/` | `color_grading.json` |
| `water/` | `water.json` |

Custom files use `<name>_atmospherics.json`, `<biome_id>_lighting.json`, etc. — pattern is `<name>_<directory>.json` with the name acting as biome ID or profile ID.

### 3.2. Format version rules — exceptions and notes

**EXCEPTION (lighting 1.26.0 keyframed ambient)**: The time-keyframed `ambient.color` and `ambient.illuminance` features ONLY activate when `lighting/*.json` is at `format_version: "1.26.0"` AND Bedrock client is at 1.21.120/preview-26.x or higher. On older clients, the ambient falls back to first keyframe value (still works, just less mood transition).

**EXCEPTION (water `sampleWidth`)**: Pre-v1.21.120 water schemas required `waves[*].sampleWidth`. v1.21.120+ deprecated this field. v1.0.0 stripped it from all 22 water files. Including it in 1.26.0 water JSONs causes parse failure.

**EXCEPTION (custom block 1.21.40 vs 1.21.80)**: Pre-permutation custom blocks could use `1.21.40`. v1.0.0+ leaves use the permutation/state schema added in 1.21.60-1.21.80, requiring `1.21.80`. Don't drop to 1.21.40 for new blocks.

---

## §4. NAMING CONVENTIONS

### 4.1. Internal block/biome/sound IDs

All custom content uses the `pw:` namespace prefix:
- Blocks: `pw:oak_leaves`, `pw:oak_young_log`, `pw:oak_branch`, `pw:leaf_litter`, etc.
- Biomes: `pw:forest_lighting`, `pw:cherry_lighting`, `pw:coastal_lighting`, etc.
- Sound events: `pw.tree_fall.small`, `pw.tree_impact.medium`, `pw.ambient.forest_dawn`, etc. (note: sound event IDs use `.` not `:` per Bedrock convention)
- Atmospherics IDs: `pw:forest`, `pw:cherry`, `pw:coastal`, `pw:desert_dunes`, `pw:alpine`, `pw:pale`, `pw:river_canyon`
- Particles: `pw:leaf_fall`, `pw:falling_dust_mud`

The `pw:` prefix is preserved despite the `PatrixWorld → Abs0lutRealism` rename (lesson #148). It refers to the project legacy name and is part of save-state compatibility.

### 4.2. File naming (resource pack assets)

- Color textures: `pw_<species>_<part>_v<N>.png` (e.g., `pw_oak_leaves_v0.png`)
- Normal maps: `pw_<species>_<part>_v<N>_n.png` (suffix `_n`, standardized v1.2.15-v1.2.16; Bedrock-only convention)
- MERS maps: `pw_<species>_<part>_v<N>_mer.png` (suffix `_mer`)
- Texture set sidecars: `pw_<species>_<part>_v<N>.texture_set.json`

**EXCEPTION (`_s.png` LabPBR specular)**: Some Patrix-source files include `_s.png` (LabPBR specular). Bedrock does NOT read these — the MER + normal + texture_set convention is what works. `_s.png` files are inert; deleting them is safe but not required.

### 4.3. Manifest dependency type rules (LOCKED — Lesson H-53/H-54)

Pack manifest `dependencies[]` array contains entries of TWO distinct types with DIFFERENT version-format rules:

| Dep type | Identified by | Version format | Stamping rule |
|---|---|---|---|
| **API module** | `module_name: "@minecraft/*"` (string) | Semantic version STRING (`"2.0.0"`, `"1.16.0"`) | **NEVER bump on pack stamping** — represents API version requested |
| **Pack-UUID** | `uuid: "<UUID>"` (no module_name) | Array `[N, N, N]` matching pack version | Bump to match new pack version |

**Stamping rule (mandatory in build pipeline)**:
- ✅ Bump `header.version`
- ✅ Bump `modules[].version`
- ✅ Bump `dependencies[].version` ONLY if entry has `uuid` (pack-UUID dep)
- ❌ NEVER touch `dependencies[].version` if `module_name` starts with `@minecraft/`

**Origin**: v1.2.15 shipped a manifest-stamping bug that blindly bumped EVERY `version` field including `@minecraft/server` API deps from `"2.0.0"` to `[1, 2, 15]`. Bedrock couldn't find a v1.2.15 of the API module, returned `undefined` from import, all scripts crashed at first `system.beforeEvents.startup.subscribe` call. All 23 `pw:*_leaves` blocks failed to parse because `pw:randomize_variant` never registered. v1.2.16 fixed the bug + added a manifest-diff gate (Lesson H-54) to catch any future regression.

**Manifest diff gate (Lesson H-54)**: After any manifest-stamping pass, the build script must diff each pack's manifest against the previous version's manifest. The acceptable diff between version N and N+1 is:
1. `header.version` bumped (consistent across packs)
2. `modules[].version` bumped (matches header)
3. `dependencies[].version` for pack-UUID deps ONLY (matches header)
4. (Optional) `header.description` text edits if intentional

ANY diff that touches `module_name`, `uuid`, `dependencies[].module_name`, `dependencies[].uuid`, `capabilities`, `min_engine_version`, `metadata`, or `@minecraft/*` dep versions MUST FAIL the build until human-confirmed.

### 4.4. Current API dependency versions (preserve as strings)

| Pack | API dep | Version string |
|---|---|---|
| BP-01 Atmospheric Effects | `@minecraft/server` | `"1.16.0"` |
| BP-02 Tectonic | `@minecraft/server` | `"2.0.0"` |
| BP-03 Identification Diagnostics | `@minecraft/server` | `"2.0.0"` |

Total of **3 string deps** across the BP stack. The build script's verification pass checks "3 string deps preserved" (`preserved_string_deps == 3`) on every release.

---

## §5. RENDER CONSTRAINTS — LOCKED INVARIANTS

### 5.1. Leaf rendering — alpha_test ONLY

All 9 custom leaf species (oak, spruce, birch, jungle, acacia, dark_oak, mangrove, cherry, pale_oak) MUST use `render_method: "alpha_test"` for all permutations. v1.2.31 has 63 permutations across 9 species (7 variants × 9 species), all `alpha_test`.

**Why**: `alpha_test_to_opaque` was a VV stability optimization that had a hidden cost — solid disc shadow casting through transparent pixels (sun blocked behind solid leaf cube even though pixels are transparent). `alpha_test` matches vanilla and produces dappled god-ray scatter through gaps. `alpha_test_blend` does NOT cast shadows in Render Dragon's deferred shader (engine optimization), so loses dappled shadows entirely.

**Exception**: NONE. User has confirmed `alpha_test` is the working state (v1.1.3 finalized this; v1.2.31 reaffirmed).

**Tradeoff**: Leaves no longer cast crisp self-shadow. Possible distant edge fizz at >24 chunks (not visible at 18-chunk PS5 target).

### 5.2. Blocks shadowing through transparent pixels

Render Dragon's deferred shadow path treats `alpha_test_to_opaque` blocks as solid for shadow rays — pixel transparency only matters at the rasterization stage, not at shadow-cast stage. To get dappled light through alpha-test transparent pixels, MUST use plain `alpha_test`.

### 5.3. light_dampening for custom multi-cube blocks

For multi-cube custom blocks like leaves (variants with up to 11 cubes), `light_dampening: 1` (matches vanilla) is REQUIRED. v1.1.2 fixed an issue where `light_dampening: 7` stacked across 3-7 cubes, 3-5 deep, totaled past 15/15 = pitch-black canopies. All 9 custom leaf species use `light_dampening: 1` since v1.1.2.

**Logs and trunks** use `light_dampening: 15` (solid wood blocks).

### 5.4. tint_method for custom leaves

Currently set to `"none"` for all 9 custom leaf species. Patrix templates are pre-tinted in the texture itself; engine-side tinting would double-tint.

**EXCEPTION (open path)**: User has indicated openness to experimenting with engine-tinted approaches in future iterations (e.g., `default_foliage` or per-biome tinting). NOT locked — if user wants to test biome tinting, the path is open. v1.2.31 still uses `"none"`.

### 5.5. Partial-block geometry — variations array forbidden

Bedrock's partial-block rendering path (`snow_layer`, `candle`, `sea_pickle`, `vines`, `top_snow`, etc.) does NOT honor `variations` arrays. Engine renders only first entry and emits warning about wasted variations.

**Fix pattern**: For any block with non-uniform geometry (snow_layer, candle, sea_pickle, top_snow, attached-state vines), define a single-texture shortname in `terrain_texture.json` and override the block's texture binding in `blocks.json`:

```json
// terrain_texture.json
"snow_layer_single": { "textures": "textures/blocks/snow_layer_v2" },

// blocks.json
"minecraft:snow_layer": {
  "textures": "snow_layer_single",
  "sound": "snow",
  "isotropic": {"up": true}
}
```

**Conformance**: RP-04-Basic/blocks.json overrides `minecraft:snow_layer` to use `snow_layer_single` since v1.1.1.

### 5.6. packed_ice texture binding (Lesson #126)

`minecraft:packed_ice` in `RP-04-Basic/blocks.json` requires an explicit `textures` field. Without it, the block renders as missing-texture purple/black. Affects RP-04-Basic ONLY (RP-03 has full PBR chain). Don't remove the textures field on packed_ice.

```json
"minecraft:packed_ice": {
  "textures": "packed_ice",
  "sound": "glass"
}
```

---

## §6. LESSONS LIBRARY

> **Organization**: Lessons are grouped by topic family. Within each family, exceptions are kept WITH the rule they modify (per user direction). Status notation:
> - **CONFIRMED** — Validated by multiple corroborations or in-game testing.
> - **PROMOTED** — Promoted to confirmed via cost (a release cycle was lost reproving it).
> - **CANDIDATE** — Awaiting first confirmation.
> - **SUPERSEDED** — Replaced by a later lesson; preserved for historical context.
> - **FALSIFIED** — Disproved by later evidence.
>
> **Numbering**: Original PatrixWorld foundation used #1-#125 (v1.0.0). v1.0.1 added #126-#131 (intent) and #132-#152 (implementation). v1.1.x onward used the Lesson Family scheme (G-01 through G-07, H-01 through H-55). v1.2.x reverted to numeric (#149-#155). The numbering is non-contiguous and historical; the topic-grouped organization below is more useful than chronological.

### 6.1. Family A — Project process and discipline

**Lesson #18 (CONFIRMED)** — Plan-first → investigate → build → verify → ship sequence. Every release follows this. Investigations may invalidate plans; that's normal. Document the reframe (Lesson #146).

**Lesson #53 (CONFIRMED, mandatory) — NEVER touch @minecraft/* string deps when stamping manifests.**
- Rule: detailed in §4.3.
- Cost of violation: full release cycle (v1.2.15 → v1.2.16).
- Build verification gate must check this on every release.

**Lesson #77 (CONFIRMED) — parse-OK ≠ runtime-OK.**
JSON parsing cleanly does NOT validate runtime correctness. `node --check main.js` confirms syntax only. Runtime behavior (does the script actually run? do events fire? does the user observe the intended behavior?) requires user in-game testing. Always note this caveat in handoffs: "JS syntax check passed (parse only — Lesson #77 reminder: runtime requires user in-game testing)".

**Lesson #126 (CONFIRMED) — packed_ice needs explicit textures field in RP-04-Basic.**
- Detailed in §5.6.

**Lesson #143 (CONFIRMED) — ALWAYS ship docs alongside binaries.**
Every release ships:
- 4 deliverables (`MAIN.mcaddon`, `ATMOSPHERIC.mcaddon`, `RP-04-Basic.mcpack`, `RP-07-Neutral-Mobs.mcpack`)
- `MD5SUMS.txt` manifest
- `README-AbsolutRealism-v<X_Y_Z>-INSTALL.md`
- `FOUNDATION_PATCH_v<X_Y_Z>.md`
- `ABSOLUTREALISM-HANDOFF-v<X_Y_Z>.md`

If docs are missed, user can't install correctly or recover state for next session.

**Lesson #144 (CONFIRMED) — WITNESS RULE extended to factual claims about pack contents.**
- Detailed in §1.4.

**Lesson #146 (CONFIRMED) — Mid-investigation reframing is normal and valuable.**
Document the reframe so future sessions understand the lineage. Don't pretend the original framing was always right.

**Lesson #147 (CONFIRMED) — Foundation lesson numbers must reconcile with cumulative patches.**
v1.0.0 had #1-#125. v1.0.1 added #126-#131 (intent) + #132-#152 (implementation). If patches merge out of order, numbers must be reconciled at merge time.

**Lesson #155 (NEW CANDIDATE v1.2.31) — Decision journals are required complement to phase logs.**
Phase log = "what shipped, when." Decision journal = "what we thought, when." Both needed for amnesia recovery, especially when intermediate workspaces get cleaned up. Adopted in v1.2.31; first build to maintain `_logs/decision_journal.md` alongside `_logs/phase_log.md`. Cleanup operations must archive journals to `/home/claude/_logs/archive/v<old>_journal.md` before deleting build dirs.

**Lesson H-04 (CANDIDATE) — Patch ship efficiency.**
Small patches that fix one specific issue and ship same-session beat large multi-issue patches that risk regressions.

**Lesson H-07 (CONFIRMED, INSTITUTIONALIZED) — Ask which side stays before two-system mismatch fix.**
When two systems disagree (e.g., color in atlas vs color in PBR), ASK USER which side is authoritative. Don't assume.

**Lesson H-17 (CONFIRMED) — Aggressive-first testing methodology.**
For ambiguous parameter ranges, push aggressive first to confirm the channel works at all, then dial back. Faster than incremental probing.

**Lesson #18 process rule (procedure) — Witness loop**:
1. User reports observation
2. Verify by extraction (filesystem listing, schema inspection, runtime log)
3. If confirmed, document with reproducible evidence
4. If unconfirmed, ask for screenshots/logs before further action

### 6.2. Family B — Manifest authoring and version stamping

**Lesson #20 (CONFIRMED) — min_engine_version 1.21.120 is the floor for VV registration.**
Below 1.21.120, VV files (atmospherics/lighting/color_grading) silently fail to register. v0.18.4 root-cause-fixed this in v1.0.0 prep. Any "let's go back to 1.21.90 for inclusion" is settled — answer is no.
- **Exception**: NONE. 1.21.120 is the floor.

**Lesson #21 (CONFIRMED) — atmospherics/lighting at 1.21.90 silently rejected.**
v26.x parser silently rejects 1.21.90 for atmospherics and lighting (despite pre-1.21.90 docs sometimes mentioning it). Use the locked table in §3.

**Lesson #28 (CONFIRMED) — client_biome 1.21.90 was a wrong move; restore to 1.21.120.**
v0.18.2 dropped client_biome from 1.21.120 to 1.21.90 attempting to fix atmospheric cascade. Did not fix the issue (root cause was manifest gating). v0.18.4 restored to 1.21.120.

**Lesson #53 (CONFIRMED) — see Family A above.**

**Lesson H-50 (CONFIRMED) — Pack stack: TOP wins, processes BOTTOM-up.**
Bedrock's pack stack: top-of-list-wins. Higher-priority packs override lower-priority. Reaffirmed v1.2.16 — when v1.2.15 had broken texture_sets in RP-04/RP-05, RP-03's complete chains at higher priority still won (the visual breakage came from script crash + render pipeline chaos, not from RP-04 displacing RP-03).

**Lesson H-53 (PROMOTED) — Manifest version stamping must NEVER touch @minecraft/* dependency versions.**
- Detailed in §4.3.

**Lesson H-54 (PROMOTED) — Manifest diff gate after stamping.**
- Detailed in §4.3.

**Lesson #148 (CONFIRMED) — Pack rename without UUID change is the safe path.**
When renaming a pack family, change ONLY display name + description + version + dependency versions. NEVER change UUIDs (save compatibility) or internal namespace prefix (saved worlds reference these by string). Validated by v1.0.1 PatrixWorld→Abs0lutRealism rename.

### 6.3. Family C — Atmospherics, lighting, color grading (Visual Volume / Vibrant Visuals)

**Lesson #24 + #78 (CONFIRMED) — VV directory reserved filename conventions.**
- Detailed in §3.1.

**Lesson G-01 (SUPERSEDED v1.2.1) — Keyframe density 25-40+ for buttery transitions.**
*Original*: dense keyframes (25-40+) needed for smooth transitions between sun illuminance / sun color stops.
*Supersession*: 13 keyframes is sufficient for the practical "cinematic-romantic" mood. v1.2.0 used 27; v1.2.1 dialed back to 13.

**Lesson G-02 (CONFIRMED) — Time-keyframed ambient color is supported as of VV 1.26.0.**
Microsoft Learn confirms: "As of version 1.26.0, both 'color' and 'illuminance' can be specified using keyframes" for the ambient property. Strong authoring tool. `format_version: "1.26.0"` in `lighting/global.json` activates this.

**Lesson G-03 (SUPERSEDED v1.2.1) — highlightsMin and midtonesMax universally used by polished VV packs.**
*Original*: `highlightsMin: 20`, `midtonesMax: 55` for clean tonal zones.
*Supersession v1.2.1*: `highlightsMin: 5`, `midtonesMax: 35` better fits cinematic-realism mood (less aggressive isolation).

**Lesson G-04 (SUPERSEDED v1.2.1+v1.2.2) — sun_mie_strength sweet spot.**
*Original*: 7-15 = golden-hour cinematic haze.
*v1.2.1*: dialed to 2.5-3.5.
*v1.2.2*: added system-coordination requirement — sun_mie must coordinate with sun_glare (combined visual, not independent knobs).
*v1.2.7*: settled at RC pattern — 0 at noon, peak at sunrise/sunset. Eliminates midday sun-square artifacts (Lesson H-25).
*v1.2.8*: bumped peak slightly for golden-hour cinematic haze (modest).

**Lesson G-05 (CONFIRMED) — moon_mie + visible moon illuminance create romantic nights.**
- Default moon illuminance 0.27 with mie 0.0-1.0: barely visible moon.
- v1.2.0 settled: illuminance 0.85, color `[200, 225, 255]` (silvery), `moon_mie_strength: 2.0`.
- *Don't go extreme*: Vibrant BSL's illum 11.5 + mie 26 brightens night so much it stops feeling like night.
- *v1.0.0 diagnostic finding #1*: peak `moon_mie_strength: 0.5` was washing out the moon disc; reduced to 0.15 in v1.0.1.

**Lesson G-06 (CONFIRMED) — Per-biome lighting variation IS supported and routed via biomes_client.json.**
Existing biome routing (`pw:forest_lighting`, `pw:cherry_lighting`, etc.) auto-loads biome-specific lighting JSON. Each biome can have its own ambient color profile, ambient illuminance level, sky intensity, and moon brightness.

**Per-biome lighting reference (v1.2.0 baseline, may have drifted in patches)**:
```
forest      → green-warm cream daytime, golden canopy sunset, indigo night, sky 0.65, ambient ×0.95
cherry      → pink-warm all-day, pink-coral sunset, slightly warmer moon [210,215,245], sky 0.7
coastal     → cool cream day, warm sunset over water, deeper indigo, brighter moon ×1.15, sky 0.72
desert_dunes→ warm tan, deep gold-amber sunset, brighter sky 0.75, ambient ×1.1
alpine      → cool blue-white, cold indigo night, brightest sky 0.85, brighter moon ×1.1, ambient ×1.15
pale        → neutral gray, eerie cold dim night, dimmer sky 0.6, ambient ×0.85
river_canyon→ warm afternoon, deep canyon-gold sunset, sky 0.7, default ambient
```

**Lesson G-07 (CONFIRMED) — Sky intensity tradeoffs.**
- 1.0 = sky contributes maximally to indirect lighting (softer shadows, brighter ambient feel)
- 0.1 = sky contributes minimally (darker shadows, sun stands out)
- v1.2.0 used 0.7 cinematic baseline; per-biome variation: alpine 0.85 (snow reflects), pale 0.6 (foggy), forest 0.65 (canopy shade).
- v1.2.7 dialed to RC range 0.6-0.7.

**Lesson H-01 (CANDIDATE) — Bloom-vs-disc tradeoff.**
`sun_mie × sun_glare < 5` to keep disc visible while allowing bloom haze.

**Lesson H-02 (CANDIDATE) — Proportional keyframe scaling.**
When tuning a keyframe set proportionally, scale all values together rather than tuning individuals.

**Lesson H-03 (CONFIRMED) — Nether/End exception class.**
Nether and End atmospherics are EXCEPTIONS to all overworld tuning. They preserve their distinct character (red-warm Nether, purple-violet End) even when overworld lighting/color grading is overhauled. Don't blanket-apply atmospheric changes; carve out Nether/End.

**Lesson H-08 (CANDIDATE) — Fog-vs-sky harmonization needs floor coordination.**
Fog `fog_color` must coordinate with sky color at horizon, or visible "fog edge" appears.

**Lesson H-09 (CANDIDATE) — Color delta < 100 between consecutive keyframes.**
Larger color deltas produce visible "stair-step" tonal shifts during transitions.

**Lesson H-10 (CANDIDATE) — Rate-of-change is a misleading metric for keyframe density.**
Don't tune by "change per keyframe rate"; tune by "perceptible visual transition smoothness."

**Lesson H-11 (CONFIRMED → SUPERSEDED v1.2.7) — horizon=zenith at noon = uniform dome.**
*v1.2.3 confirmed*: Setting sky_horizon_color = sky_zenith_color at noon produced a uniform sky dome (no gradient).
*v1.2.7 superseded*: Uniform dome too dark per user; replaced with Interpretation C (gradient horizon→zenith at noon, RC tonal feel).

**Lesson H-12 (CONFIRMED) — Two-system fog architecture (distance + volumetric coexist).**
- Distance fog: `fog_start`, `fog_end`, `fog_color` — affects all rendering, masks chunk-loading edge.
- Volumetric fog: `volumetric.density.*` — godray/scattering visible only when sun overhead.
- Both can coexist; tune independently.

**Lesson H-13 (CONFIRMED) — Distance fog `fog_end` = render distance to mask chunk-loading edge.**
Set `fog_end` close to render distance (e.g., 0.95-1.0 in render-mode). Fog covers the chunk-loading horizon line.

**Lesson H-14 (PROMOTED) — `volumetric.density.air.max_density: 0.150` crashes Android Bedrock.**
Cap at `0.05` for Android safety. v1.1.0 ceiling: 0.05 (was 0.06 in v1.0.1; imperceptible difference).

**Lesson H-15 (CONFIRMED) — Per-biome density character is dramatic and worth authoring.**
Different biomes benefit from different fog densities (mesa needs layered, jungle needs uniform-thick, alpine needs cool-thin).

**Lesson H-16 (CANDIDATE) — Volumetric fog cost peaks under dense overhead foliage.**
Forest biomes with dense canopy cause more samples through the fog volume.

**Lesson H-22 (PROMOTED) — caustics.power must be INT 1-6.**
Bedrock VV 1.26.0 schema requires INT, not float. v1.2.6 used floats (2.6, 3.9, 3.25); silently clamped/rejected. v1.2.7 fixed.

**Lesson H-23 (PROMOTED) — Bedrock VV 1.26.0 water_settings schema does NOT include `surface`, `foam`, or `subsurface` blocks.**
Schema is exactly: `particle_concentrations`, `waves`, `caustics`, `biome_water_color_contribution`. Foam emerges from `waves.depth` and engine procedural shoreline rendering; surface reflectivity from PBR water material; subsurface scattering from texture_set MERS — not separate water_settings blocks.

**Lesson H-24 (CANDIDATE) — RC-style godray recipe.**
`volumetric.density.air.uniform: true` + `max_density: 0.04-0.05` + `henyey_greenstein_g: 0.5-0.7` + `render_distance_type: "render"` produces clean godray scattering.

**Lesson H-25 (CONFIRMED v1.2.7) — RC pattern: sun_mie_strength and sun_glare_shape are 0 at noon.**
Only fire at sunrise/sunset. Eliminates midday sun-square artifacts.

**Lesson H-31 (PROMOTED-CANDIDATE) — License-clean source rule.**
- Detailed in §1.3.

**Volumetric fog ceilings (LOCKED v1.1.0)**:
- `max_density` ceiling: **0.05** (was 0.06 in v1.0.1).
- `zero_density_height` ceiling: **250** (was 320 in v1.0.1).
- These are the two volumetric knobs with measurable PS5 GPU cost. All other fog parameters (`fog_start`, `fog_end`, `fog_color`, `media_coefficients`, `henyey_greenstein_g`, `max_density_height`) are artistic-only with negligible perf cost.

### 6.4. Family D — PBR / MERS authoring (RP-03 + RP-04 + RP-05 + others)

**Lesson H-18 (CONFIRMED) — Bedrock PBR requires color PNG in same pack as texture_set.json.**
A `texture_set.json` references a `color` field; the engine resolves to a PNG in the SAME pack. Cross-pack basename resolution is also supported but dangerous (broken refs cascade silently as `CONTENT_ERROR` log entries). Per Microsoft Learn: "If a Texture Set is invalid, CONTENT_ERROR will be logged and the Texture Set will not be used."

**Lesson H-19 (CONFIRMED) — Block variations need own PBR companions.**
Each variation in a `terrain_texture.json` `variations` array needs its own `_n.png`, `_mer.png`, and `texture_set.json`. Engine doesn't automatically share companions across variants.

**Lesson H-20 (CONFIRMED) — `pw:` namespace blocks need vanilla textures co-located.**
Custom pw:* blocks reference vanilla textures via `terrain_texture.json` shortnames. The vanilla textures must exist in the same pack hierarchy.

**Lesson H-55 (PROMOTED) — H-18 violations must be cleaned, not deferred.**
When an H-18 violation is discovered in any audit pass, EITHER:
- (A) Fix it in the same release (delete broken texture_set + companions OR add the missing color PNG), OR
- (B) Document it in the release's foundation patch with a specific block list of affected vanilla blocks, AND warn user that those blocks will render incorrectly.

Don't silently defer. v1.2.16 cleaned 81 known H-18 violations (24 in RP-04, 57 in RP-05) when defer-strategy proved costly during v1.2.15 testing.

**Lesson #127 (CONFIRMED) — Cross-pack PBR layering: RP-03 ships only normal+MER+texture_set sidecars; color PNGs ship in OTHER packs.**
Verifiers must do cross-pack basename resolution.

**Lesson #128 (CONFIRMED) — Patrix 256x source basic archive ships color textures in palette mode (P).**
Convert to RGBA before saving for Bedrock (Bedrock expects RGBA, not palette).

**Lesson #129 (CONFIRMED) — Idle MER from active MER: zero G channel; same-material copy works for missing faces.**
For animated blocks with idle/active states, idle MER = active MER with G channel zeroed.

**Lesson #130 (CONFIRMED) — Sand and red_sand PBR sidecars in RP-03 referenced nonexistent color files (cleaned up in v1.0.1).**

**Naming convention — `_n` suffix standardized v1.2.15-v1.2.16**: All RP-03 normal map files use `_n` suffix (1838 texture_sets updated, 967 files renamed in v1.2.15-v1.2.16). RP-03 has 1862 complete texture_set chains, 0 broken refs as of v1.2.16.

**Texture file content requirements**:
- Color: RGBA 8-bit PNG, pack-resolution (typically 128×128 or 256×256)
- Normal: RGB-encoded normal map (Bedrock convention), `_n.png` suffix
- MERS: 4-channel where R=metalness, G=emissive, B=roughness, A=subsurface scattering
- Texture set: JSON sidecar `<base>.texture_set.json` referencing `color`, `normal`, `metalness_emissive_roughness`, optional `subsurface`

### 6.5. Family E — Sand sun-glint MERS authoring (specific)

**Lesson #62 (CONFIRMED) — 4-variant lock for sand.**
Only 4 sand variants registered (base + sand_v5 + sand_v6 + sand_v9 with weights 18/10/10/10). Other 12 variants on disk but unused. Over-variance produced "checkered" appearance.

**Lesson H-32 (PROMOTED-CANDIDATE) — Sand transition harshness root cause.**
When randomly-selected variant block tiles show visible boundaries during gameplay, the cause is **macro-feature variation in the variant color tiles themselves**, NOT normal-map discontinuity NOR color-mean shift. Diagnostic threshold: `macro_std < 8` (compute by downsampling tile to 16×16 luminance via Lanczos and taking `arr.std()`). Real-world photographic textures cluster at 4-6.
- **Repair**: Replace variant color tiles with random crops from a uniform photographic source.
- **Evidence**: Old `pw_sand_v*` tiles macro_std 9.8-19.0 (worst v22, v26, v27 at 18-19); ambientCG Ground033 random crops macro_std 4.4-6.6.

**Sand sun-glint MERS specification (v1.1.1 LOCKED, supersedes v1.1.0 §6.8)**:

| Channel | Sparkle pixel | Non-sparkle pixel | Meaning |
|---|---|---|---|
| **R (metalness)** | **128** | **0** | Sparkle = semi-metallic (mirror facet); rest is dielectric sand |
| **G (emissive)** | **0** | **0** | NO active emissive — sand should not glow at any time |
| **B (roughness)** | **12** | **240** | Sparkle = very smooth (sharp specular flash); rest = max rough |
| **A (subsurface)** | **12** | **12** | Minimal subsurface (sand grains opaque) |

**The critical pairing**: sparkle pixels combine HIGH metalness (R=128) with LOW roughness (B=12) so that ONLY when sun direction + surface normal + view direction align does the pixel reflect a bright specular highlight.

**Sparkle density**: ~1.2% of total pixels (785 of 65,536 in 256×256). Higher density = artificial; lower = disappears at viewing distance.

**Files conforming**: `RP-04-Basic/textures/blocks/pw_sand_mer.png`, `RP-04-Basic/textures/blocks/pw_red_sand_mer.png`.

**EXCEPTION (v1.1.0 §6.8 SUPERSEDED)**: v1.1.0 spec used **G=200-240** (paired with B=30 mirror-low). That produced a glow-and-mirror hybrid visible regardless of viewing angle. v1.1.1 reverted G to 0 — sparkle is purely specular (angle-dependent) now.

### 6.6. Family F — Leaves authoring

**Lesson #29 (SUPERSEDED) — "Custom blocks don't support per-instance variation".**
*Old claim*: Custom blocks (`pw:*`) DO NOT support per-instance variation; variations on terrain_texture.json ignored.
*Reality (v1.0.0+)*: Custom blocks WITH PERMUTATIONS support per-instance variation via `pw:variant` block state + `minecraft:custom_components: ["pw:randomize_variant"]` placement-time randomizer. v1.0.0 leaves used 6 variants per species this way.
*Replaced by*: Lessons #94, #95.

**Lesson #34 (UPDATED 2026-05) — Leaves use `render_method: "alpha_test"`.**
*Old claim* (v0.10.5/v0.16.x): Leaves use `render_method: "blend"` with alpha 217.
*Reality*: Leaves use `alpha_test`. v1.1.3 finalized; v1.2.31 reaffirmed. Backlog "test blend mode for leaves" REMOVED — no longer wanted.

**Lesson #62 (CONFIRMED) — see Family E above (sand).**

**Lesson #69 (CONFIRMED) — Tree feature canopy STRICT spec.**
Elder MAX 5 blocks tall, spruce elder MAX 6, never additive to vanilla, total leaf volume across 17 features ~1,111 to prevent Android crashes.

**Lesson #70 (SUPERSEDED) — see Lesson #29.**

**Lesson #72 (UPDATED 2026-05) — Z-fighting concerns moot under alpha_test.**
*Old claim*: Multi-cube leaves z-fight at edges due to coplanar surfaces.
*Reality (alpha_test)*: alpha_test rendering eliminates this concern by per-pixel discard.

**Lesson #94 + #95 (CONFIRMED) — Permutation + custom-component pattern for leaves.**
- Permutation states: `pw:variant`, `pw:rseed` (initial v1.0.0 set; v1.2.27 added `pw:section`, `pw:exposure`, `pw:section_rolled`).
- `minecraft:custom_components: ["pw:randomize_variant"]` declares the placement-time randomizer.
- Component handler must be registered in `scripts/main.js` startup AND declared on each block JSON's `components` (or in a permutation's components). Registering the handler alone doesn't activate randomization (Lesson #150).

**Lesson #150 (v1.0.1) (CONFIRMED) — Custom block state declaration alone doesn't activate randomization.**
The `pw:randomize_variant` component must be declared explicitly on each block JSON's `components` (or in a permutation's `components`) to make `onPlace` fire for that block type. Registering the component handler in `scripts/main.js` only adds it to the registry — blocks must opt-in by declaring it.

**Lesson #151 (v1.0.1) (CONFIRMED) — Randomize component handlers must be type-aware about variant count, not hardcoded.**
v1.0.0 randomizer used hardcoded `Math.floor(Math.random() * 4)` (4 variants). When leaves bumped to 6 variants in v1.0.1, the randomizer was missing variants 4 and 5. Fix: read variant count from `PW_VARIANT_COUNT` constant or per-block-type registry.

**Lesson #152 (v1.0.1) (CONFIRMED) — Custom block loot tables shipped at v1.0.0 across 9 leaf species dropped block items at 100% with NO conditions.**
This is non-vanilla. Vanilla drops sticks + saplings + apples conditionally. v1.0.1 audit established the audit pattern.

**Lesson #144 (CONFIRMED v1.2.27/v1.2.28) — Cross-version state migration via flag reset.**
When a downstream gate persists across state transitions, the upstream re-trigger must also reset it. Pattern: when adding a new state (e.g., `pw:section_rolled`), the section scanner must also reset existing `pw:rseed=false` to force re-rolls of leaves placed under prior state schemas.

**Lesson #146 (CONFIRMED v1.2.28) — Multi-stage cascade architecture.**
Three-stage architecture: cascade event → scanner re-flag → variant re-roll. Each stage idempotent; events propagate via state resets. Generalizes to any state-driven block system (snow accumulation, biome blooms, damage propagation).

**Lesson #147 (CONFIRMED v1.2.29) — Event-queue dedup via Set with composite key.**
When event triggers fire faster than processing, queueing into an unsorted list creates duplicates. Using a Set keyed on `${x},${y},${z},${dimensionId}` auto-dedupes. Cost: O(1) amortized membership check on enqueue. Benefit: no wasted re-processing.

**Lesson #148 (CONFIRMED v1.2.29) — Cascade coverage gaps from event-API limits — four-tier solution.**
Bedrock script API doesn't expose unified "block changed" event. Different change sources fire different events:
- `playerBreakBlock` — tool break only
- `explosion` — TNT, creeper (not playerBreakBlock)
- `setPermutation` — silent (no event); used by BIGCANOPY, /setblock, structure load
- vanilla leaf decay — silent

A cascade subscribing to one event misses the others. Full coverage = four tiers:
1. `playerBreakBlock` event hook
2. `explosion` event hook (added v1.2.29)
3. BIGCANOPY-inline cascade call from `cleanOrphanLeaves` (added v1.2.29)
4. Periodic sanity-check (`reValidateExposure` on every leaf scanned by decay scanner, added v1.2.29)

**Lesson #149 (CONFIRMED v1.2.30) — Flag-based depth detection with multi-cycle convergence.**
Reading neighbors' flags rather than walking 36 second-order neighbors directly is cheaper but converges over 2-3 cycles (~10-15 sec). First-cycle over-classifies one direction; subsequent cycles correct. Practical for migration/rollout latency.

**Lesson #150 (CONFIRMED v1.2.30) — Asymmetric scan volume for vertically-skewed content.**
When search space is naturally weighted in one direction (leaves above ground), asymmetric extents preserve total cell budget while improving coverage where it matters. UP=35, DOWN=4 has same cost as symmetric ±19.5 but covers up to 35 blocks above.
- **Caveat (v1.2.31 — Lesson #154)**: iteration order matters. Top-down sweep with bail-on-empty fails when scan extent reaches into typically-empty regions. Bottom-up + "found anything yet" check is more robust.

**Lesson #154 (NEW CANDIDATE v1.2.31) — Iteration order matters with bounded early-exit.**
When a scan loop has an "early exit on no work" optimization, the iteration ORDER determines whether the optimization fires legitimately (finished work) or spuriously (haven't reached work yet). Top-down sweep with bail-on-empty fails when scan extent reaches into typically-empty regions. Bottom-up + "found anything yet" check is more robust. Validated by v1.2.31 scanner fix.

### 6.7. Family G — Worldgen / feature_rules

**Lesson H-05 (CANDIDATE) — Vanilla saplings grow vanilla blocks not pw: blocks.**
Player-placed sapling growth uses vanilla tree generation logic. To get pw:* trees from saplings, would require either:
- (A) Override vanilla sapling block (risky, affects worldgen)
- (B) Custom sapling block (`pw:oak_sapling`) with bone_meal trigger script

**Lesson H-06 (CANDIDATE) — Foliage wind sway is engine-level.**
Bedrock's wind-sway animation for vanilla foliage is engine-side; not exposed via JSON. Custom blocks don't sway. To get sway: (a) custom geometry animation (not flipbook), or (b) wait for Bedrock to expose the parameter.

**Lesson #6.6 (LOCKED v1.1.1) — Bedrock feature_rules placement_pass enum is closed.**
Valid values: `surface_pass`, `before_surface_pass`, `after_surface_pass`, `underground_pass`, `pregeneration_pass`. NO custom passes (`tree_pass`, `forest_pass`, `decoration_pass` all silently fail).

**Lesson #6.6 sub (LOCKED v1.1.1) — Bedrock Molang `query.heightmap` takes no arguments.**
Java mods often use `heightmap(x, z)`. Bedrock's `query.heightmap` is implicitly evaluated at the iteration's (x, z) when used WITHOUT arguments. Passing arguments produces parse failure and the rule never fires. Use `y: {distribution: "uniform", extent: [low, high]}` if explicit Y control is needed.

**Lesson #6.11 (LOCKED v1.1.1) — local_lighting entry validity rules.**
The `minecraft:local_light_settings` schema (format_version 1.21.120) accepts entries keyed by **block identifier**, not entity identifier and not Java identifier. Valid keys must satisfy ALL three:
1. Identifier must reference an actual Bedrock block. `minecraft:end_crystal` is an entity. `minecraft:portal` is a vanilla rendering effect. `minecraft:end_gateway` is a special rendering effect, not a block.
2. Identifier must use Bedrock namespace, not Java:
   - `minecraft:jack_o_lantern` (Java) → `minecraft:lit_pumpkin` (Bedrock)
   - `minecraft:redstone_lamp` lit state is `minecraft:lit_redstone_lamp`
   - `minecraft:redstone_ore` lit state is `minecraft:lit_redstone_ore`
3. Custom-namespace identifiers (e.g., `pw:held_light`) are valid IF the block is registered in a behavior pack.

**Cascade hazard**: invalid identifier produces misleading `light_type out of range [1, 6]` error pointing at the enum schema rather than identifying the offending key. Audit for non-block keys FIRST when this error appears.

**v1.1.1 conformance**: removed `minecraft:end_crystal`, `minecraft:jack_o_lantern`, `minecraft:portal`, `minecraft:end_gateway` from RP-02 local_lighting. Total entries: 91 → 87.

**Lesson #149 (v1.0.1) (CONFIRMED) — Server-side biome with `replace_biomes` configuration but no matching `pw_*.client_biome.json` will render with the REPLACED vanilla biome's colors/atmospherics, not custom values.**
Easily-overlooked authoring gap. v1.0.1 fixed 6 affected biomes via TD-C1.

**Lesson #131 (CONFIRMED) — Foundation backlog can drift from pack reality.**
"7 dormant branch geometries" claim was inaccurate at v1.0.0. Always extract before claiming pack contents (Lesson #144 corollary).

### 6.8. Family H — Mobs and entities

**Lesson #3 (CONFIRMED) — Bedrock doesn't read LabPBR `_s.png`.**
The MER + normal + texture_set.json convention is what works. `_s.png` files are inert; can be deleted (not required for cleanup).

**Bird wing_flap pre_animation init (LOCKED v1.1.2)** — chicken and parrot entities require:
```json
"pre_animation": {
  "wing_flap": "math.sin(query.anim_time * 360 * 3);"
}
```
Without initialization, vanilla animation files reference `variable.wing_flap` and cause Molang errors.

**Mob spawn rules** — BP-04 ships rules for: zombie, spider, skeleton, creeper. NOT Warden (Warden uses sculk_shrieker `summoned_by_warning_level_4` mechanic, not standard spawn rules).

**Bed rendering (Bedrock 1.21+)**: beds render as ENTITY-style geometry, not block atlas. Engine reads from `textures/entity/bed/<color>.png`, not from `terrain_texture.json`. v1.0.0 ships beds at this path; if rendering breaks, check Bedrock version's expected path (may have moved like armor did v1.21.70).

**Armor path (Bedrock 1.21.70+)** — armor moved to NEW humanoid path:
- Old: `textures/models/armor/<material>_layer_1.png` and `_layer_2.png`
- New: `textures/entity/equipment/humanoid/<material>.png` and `humanoid_leggings/<material>.png`
- v1.0.0 ships BOTH paths for compatibility.
- **Diagnostic finding #7**: equipped armor renders vanilla, in-hand renders Patrix → likely missing `attachables/` directory (Bedrock 1.21+ system for 3rd-person equipped armor). Author 24+ attachables JSON files (4 slots × 6 materials). Deferred.

**Lesson #137 (CONFIRMED) — Audio mod jars mixed-license.**
Test-by-test: never assume an audio source is fully reusable just because some files are CC0.

**Lesson #138 (CONFIRMED) — Atmosfera schema optimal generalization.**
For ambient audio, the Atmosfera mod's schema (per-event biome conditions + time-of-day modifiers + activation gates) is the highest-ROI Bedrock-portable design. Worth porting for v1.3.0+ ambient audio activation.

**Lesson #139 (CONFIRMED) — Verify pack inventory by extraction.**
Don't trust prior handoffs about "we have X." Extract and verify.

**Lesson #140 (CONFIRMED) — DEFINED vs WIRED sound events distinction.**
v1.0.0 had 122 dormant `pw:ambient.*` sound events DEFINED in `sound_definitions.json` but never WIRED via subscription/event triggers. Counting events ≠ counting playing audio.

**Lesson #141 (CONFIRMED) — Some Java features categorically impossible in Bedrock.**
Fullscreen UI, chunk pixel rendering, minimap overlay, arbitrary file write, custom render hooks. Honest unportability verdict respects user time better than half-built approximation.

**Lesson #142 (CONFIRMED) — All-Rights-Reserved license = independent reimplementation only.**
No asset/code reuse. Schema isn't usable, assets aren't usable; only the user-visible concept is.

**Lesson #143 (CONFIRMED) — For an existing player base in a curated visual-realism pack, ambient audio is higher-impact than waypoints.**
ROI prioritization context.

**Lesson #145 (CONFIRMED) — Naming similarity ≠ functional similarity.**
"Atmosfera" (audio by Haven King) vs "AtmosphericA" (visuals by Beash) vs "Atmospherics" (visuals by CelloPudding/UsernameGeri) are three distinct mods despite similar names. Verify SAME DOMAIN before comparing.

### 6.9. Family I — Custom worldgen JSON misc

**Lesson #132 (CONFIRMED) — ONNX worldgen unportable.**
Java mods using ONNX models for terrain generation cannot be ported to Bedrock — runtime is Java-specific.

**Lesson #133 (CONFIRMED) — Java BiomeClassifier translation deltas.**
Java BiomeClassifier's biome decision tree doesn't map 1:1 to Bedrock's biome JSON; translation requires hand-curating equivalent biome configurations.

**Lesson #134 (CONFIRMED) — Sparse-tree variants high-ROI.**
For a curated worldgen pack, adding "sparse" variants (low tree density) of standard biomes provides high visual diversity at low authoring cost.

**Lesson #135 (CONFIRMED) — replace_biomes collision audit mandatory.**
When a custom biome uses `replace_biomes` to override a vanilla biome, audit for COLLISIONS with other replace_biomes targeting the same vanilla. Last-loaded wins; you may silently displace another biome.

**Lesson #136 (CONFIRMED) — Identity reuse for visual coherence.**
Re-using identity blocks/colors across related custom biomes maintains visual coherence (e.g., all mountain variants share a color palette).

**Locatebiome returns surface column, not biome Y position (LOCKED v1.1.1)**:
`/locatebiome <id>` and `/locate biome <id>` return X, Y, Z where Y is surface elevation of the column above the biome — not the biome's actual extent. For underground biomes (lush_caves, dripstone_caves, deep_dark), the biome exists at Y -50 to ~60 but the command returns surface Y (~64-100). User must dig down or fly down from returned coords.

### 6.10. Family J — Lens flare / scripted entity-billboard

**Lesson F6 / Path B (LOCKED v1.2.0)** — Bedrock VV atmospherics schema has NO `lens_flare`, `sun_disc`, or bloom-control field. The 7 atmospherics fields are: `horizon_blend_stops`, `rayleigh_strength`, `sun_mie_strength`, `moon_mie_strength`, `sun_glare_shape`, `sky_zenith_color`, `sky_horizon_color`.

Real lens flare in Bedrock requires the **scripted entity-billboard particle pattern**: per-tick player view tracking + sun-direction math + screen-aligned billboard particles spawned along the sun→camera ray. BP-06 (v1.2.0) implemented this using stable `@minecraft/server 2.0.0`.

Particles use `minecraft:particle_appearance_billboard` with `facing_camera_mode: "rotate_xyz"` for screen-aligned rendering.

### 6.11. Family K — Sun and Moon rendering (texture-side)

**Sun.png authoring (LOCKED v1.2.0)**:
- 1024×1024 RGBA
- Solid white disc at 150px radius (~6.7% texture area), hard 2-pixel alpha edge
- Pure white center (255,255,255,255) for engine HDR bloom auto-trigger
- 8-point starburst rays at 45° intervals
- NO painted-in halo — that compounds with engine bloom; pure white hard-edge disc lets engine HDR auto-bloom drive the halo cleanly

**Sun atmospherics arc (resolved v1.2.0)**:
- v1.0: `sun_mie_strength` peak 5.0 (overwhelming halo)
- v1.1.x: dropped progressively (peak 1.0, then 0.3)
- v1.2.0: settled at peak 7.0 with cinematic mood
- v1.2.7+: RC pattern (0 at noon, peak at sunrise/sunset)

**Sun three-knob problem (Lesson v1.1.3)** — sun visibility is a three-knob interaction: `sun_mie_strength` × `sun_glare_shape` × `rayleigh_strength`. Auditing one alone is insufficient. Sun textures with painted-in glare stack with engine mie — pick one approach, not both.

**Moon — celestial directory** (Bedrock 1.21+):
- Old/legacy path: `textures/environment/moon_phases.png` (1024×512 RGBA, 8-tile horizontal strip for 8 lunar phases)
- New path: `textures/environment/celestial/moon/<phase>.png` (per-phase 2048×2048)
- v1.0.0 ships both. Diagnostic finding #1 (moon-as-white-ball) hypothesizes engine may render only legacy path.

### 6.12. Family L — Dodecagon trunks / falling-tree mechanic

**Standing-tree dodecagon trunks (LOCKED v1.2.19+)**:
- 17 trunk blocks total (9 species × 3 tiers + extras = 17)
- 595 permutations (V4 invariant)
- Geometry: 12-panel cylinder approximation, chord-flush (each panel touches its neighbor with 1-pixel overlap)
- Standing chord widths (LOCKED): young = 3.2, mature = 3.75, old = 4.0
- 7 Patrix end-grain log-top variants per species (9 species × 7 variants = 63 unique end grains)
- Variants 2, 4, 6, 7, 8 inpainted to remove cracks; variants 3, 5 retain cracks for variety
- Heartwood enlarged to fill dodecagon interior (no visible gaps through panel edges)
- Independent randomization: bark variant + log-top variant pick separately per tree
- Vines on dodecagon mature/old worldgen: 15% in oak forests, 30% in jungles

**Falling-tree dodecagon (LOCKED v1.2.20+)**:
- 12 dodecagon falling-tree geometries: oak/spruce/jungle/birch × young/mature/old
- 11 square trunks: elder species + dark_oak + pale_oak + acacia + cherry + mangrove (preserve 2×2 square)
- 23 falling-tree geometries total
- Per-tier chord widths (V6 invariant): young = 1.6 (z=2), mature = 2.7 (z=4), old = 3.2 (z=5)
- 25 cubes per log_panel bone × all dodecagon geometries (V6: "0 broken segments")
- Multi-cube puff canopies for all 23 falling-tree geometries (1 LOD anchor + 4 corner puffs + 1 top crown each)

**Falling-tree branches (LOCKED v1.2.20+)**:
- 8 branch species: oak_elder, spruce_elder, jungle_elder, dark_oak_elder, pale_oak_elder, acacia, cherry, mangrove
- Geometry: shared `geometry.pw_branch` (16×4×4 horizontal cube)
- 4 permutations per species for cardinal directions (`pw:direction` state values 0/1/2/3)
- Permutations use `minecraft:transformation` rotation [0, 0/90/180/270, 0]
- Material instance bound to species-specific bark texture
- Render method: `alpha_test`
- Loot: empty (branches break to nothing)
- Tags: `wood`, `branch`

**Worldgen branch placement** — for 5 elder species, aggregate features `pw:{species}_elder_with_branches_tree_feature` combine existing `pw:{species}_elder_tree_feature_v2` + `pw:{species}_elder_branch_scatter`. Acacia, cherry, mangrove branches exist but biome integration deferred (vanilla biome features harder to override).

**Tree-fall sounds** (LOCKED v1.2.21):
- 14 .ogg files in `RP-01/sounds/tree/`: small (3 fall + 3 impact), medium (2 fall + 1 impact), big (2 fall + 1 impact), generic (1 fall + 1 impact)
- 8 sound events in `sound_definitions.json`: `pw.tree_fall.{small,medium,big,generic}`, `pw.tree_impact.{small,medium,big,generic}`
- Sound size matches species tier: young → small, mature → medium, old/elder → big; nether species → generic
- Triggered on fall start (after `playAnimation`) + on impact (collision-stop OR 1.8s natural completion)

**Leaf particles during fall** (LOCKED v1.2.21):
- New `pw:leaf_fall` particle (5 leaves per spawn, 3-second lifetime, downward acceleration with drag, billboard rendering)
- Triggered alongside existing `falling_dust_mud_particle` at 5 timed phases (15%, 30%, 50%, 70%, 85%)
- Skipped for nether/mushroom species (no leaves)

**Mid-fall leaf shedding** (LOCKED v1.2.30, Lesson C-10):
- `SHED_FRACTIONS = [0.3, 0.55, 0.8]` (3 bursts at 30%, 55%, 80% of fall arc)
- Each burst spawns 2-4 `pw:leaf_litter` entities at randomized positions around stump (mid-air)
- Cost: 3 timeouts + 6-12 spawnEntity calls per fall — negligible

**Settling bounce animation** (LOCKED v1.2.30, Lesson C-14):
- `animation.ft_falling_tree.rest` is 5-keyframe damped oscillation over 600ms:
  - 0.00s: at fall_angle (Molang `q.property('ft:fall_angle')`)
  - 0.15s: angle - 4° (overshoot inward)
  - 0.30s: angle + 1° (rebound)
  - 0.45s: angle - 0.5° (small overshoot)
  - 0.60s: settle at fall_angle
- `animation_length: 0.6`, `loop: hold_on_last_frame`
- Subtle 4° amplitude — heavy/realistic, not cartoonish

### 6.13. Family M — Asset processing pipeline

**Lesson #151 (CANDIDATE) — Asset-side bulk processing via PIL+numpy.**
Pattern: `Image.open → np.array → channel manipulation → Image.fromarray.save`. Works for any per-pixel transformation across many similar textures. ~28 sec for 54 textures at 128×1024. Used for v1.2.30 MERS S channel ×2 scaling and v1.2.31 asymmetric MERS bump.

```python
from PIL import Image
import numpy as np
img = Image.open(path).convert('RGBA')
arr = np.array(img)
# Channel 3 of RGBA = alpha = MERS S
arr[..., 3] = np.minimum(255, arr[..., 3].astype(np.uint16) * 2).astype(np.uint8)
Image.fromarray(arr, 'RGBA').save(path, 'PNG')
```

**Lesson #152 (CANDIDATE) — Phase-offset flipbook for "alive canopy" effect.**
Vary `ticks_per_frame` per variant in `flipbook_textures.json`; adjacent variants animate at slightly different speeds → natural ripple effect. Cost: zero. Apply to any animated tile-set with multiple variants where lockstep sync looks artificial.

**v1.2.30 flipbook variance pattern**: `{v0: 4, v1: 5, v2: 6, v3: 5, v4: 4, v5: 6}` ticks_per_frame across variants.

**Lesson #153 (CANDIDATE) — Molang keyframes with per-entity dynamic base.**
When animation needs to oscillate around a per-entity property value, use Molang in keyframes: `"q.property('ft:fall_angle') - 4.0"` etc. Allows reusable damped-oscillation animation that respects per-entity state.

### 6.14. Family N — Build pipeline / verification

**Verification suite (mandatory regression prevention, runs every release)**:
1. **Schema parse**: every JSON file in every pack parses cleanly
2. **UUID uniqueness**: all 17 manifest UUIDs distinct
3. **Manifest version uniformity**: all 16 manifests at the same version triple
4. **Inter-pack dependency versions**: each `dependencies.version` matches its target pack's `header.version`
5. **API string deps preserved**: 3 string deps (`@minecraft/server` × 3) preserved as strings (Lesson #53)
6. **Texture-set companion existence**: every `texture_set.json` references real PNG files OR uses inline uniform arrays
7. **Backup file exclusion**: no `.bak*` files in shipped mcpacks
8. **Macro-feature audit (NEW for H-32)**: any new variant tile authoring compared to `macro_std < 8` baseline
9. **License audit (NEW for H-31)**: any new external assets verified CC0 or CC-BY with `credits.md` updated
10. **Manifest diff gate (Lesson H-54)**: diff each pack's manifest against prior version's; fail on unexpected field changes

**Verification check naming**: V1, V2, ... incrementally added per release. v1.2.31 has 49 checks (V1-V49). Numbering is non-strict; checks are added when needed. Pattern:
- V1-V12: structural invariants from v1.0.0 era (manifests, packed_ice, trunks, leaves, branches, sounds)
- V20-V21: v1.2.29 architecture
- V30-V32: v1.2.30 polish
- V41-V49: v1.2.31 scanner fix + variant_0 redesign + MERS bump

**Build pipeline (LOCKED, standard since v1.0.0)**:
1. Bootstrap working dir from prior version (`cp -r`)
2. Apply targeted modifications
3. Stamp manifests to new version (preserving @minecraft/* string deps)
4. Build per-pack `.mcpack` files (zip with deflate compression level 6)
5. Bundle MAIN + ATMOSPHERIC `.mcaddon` (zip-of-zips of nested mcpacks)
6. Compute MD5SUMS.txt
7. Run verification suite (must pass 100% before ship)
8. Write README, FOUNDATION_PATCH, HANDOFF docs
9. `present_files` to user

---

---

## §6.5. LESSONS ADDED SINCE v1.2.31

These lessons were added during the v1.2.32 → v1.2.36 cycle. They use globally-unique numbering (#154–#175). For lessons #154–#159 inherited from the v1.2.32 foundation patches, the LATEST authoritative numbering (per `foundation-patch-v1_2_32-1.md`) is used.

> **Note**: Lessons #150–#155 also appear in §6 above with family-local meanings (a numbering inconsistency from earlier releases). Where numbers collide, both lessons are preserved — the §6 family-local entry is older, the §6.5 entry below is the latest globally-numbered version. v2.0.0 will normalize this.

### Family V — MERS sampling, LabPBR conversion, and PBR pipeline (v1.2.32 cycle)

#### Lesson #154 (CONFIRMED v1.2.32) — MERS roughness baseline sampling

For alpha_test foliage textures, computing MER channel means over `color_alpha > 0` is misleading because anti-aliased edge pixels (alpha 1-127) have their MER set to all-zeros (background). Those pixels don't render under alpha_test (threshold = 128) but they DO drag the overall mean down.

**Correct sampling**: filter pixels by `color_alpha >= 128` (the alpha_test threshold) before computing MER channel means. Reflects what's actually rendered.

For oak v0:
- Mean over `alpha > 0`: R=47.8, S=63.4 (misleading)
- Mean over `alpha >= 128`: R=192, S=255 (correct — what's rendered)

#### Lesson #155 (CONFIRMED v1.2.32) — `preserved_string_deps == 3` IS CORRECT

The 3 string deps that must be preserved across the 16-pack ship:
- BP-01 (atmospheric-effects): `@minecraft/server @ 1.16.0` (older API surface)
- BP-02 (tectonic): `@minecraft/server @ 2.0.0`
- BP-03 (identification-diagnostics): `@minecraft/server @ 2.0.0`

A prior mid-build count of 2 was due to operating with only 12 of 16 packs available. When auditing string deps, do it across all 16 packs not just the ones being modified.

#### Lesson #156 (CONFIRMED v1.2.32) — Patrix LabPBR-to-MERS conversion

LabPBR `_s` files (Java spec) → Bedrock MERS:
- M (metalness) = 255 if G ≥ 230, else 0
- E (emissive) = A_lab if A_lab < 255, else 0
- R (roughness) = 255 − R_lab (perceptual smoothness → roughness)
- S (subsurface) = (B_lab − 64) × 255 / 191 if B_lab ≥ 65, else 0

All 9 species in Patrix Java source (`assets/minecraft/optifine/ctm/patrix/leaves/{species}/2_s.png`) have valid LabPBR data. Each species gets one canonical `_s` file applied to all 7 variants (variant differences are color-only).

Patrix-authentic MERS for oak: R=210, S=205. Compare to v1.2.31's R=192, S=255 (saturated). Subsurface saturated at 255 was the dominant issue, not roughness.

#### Lesson #157 (CONFIRMED v1.2.32) — Block material_instance binding is per-face, not per-bone

For Bedrock CUSTOM BLOCKS, the `minecraft:material_instances` map is keyed by face name OR custom-named instance name. The binding from geometry to material instance is via the `material_instance` STRING field on each face of each cube — **NOT** via the bone name.

```json
"cubes": [
  {
    "origin": [-6, 0, -6],
    "size": [12, 16, 12],
    "uv": {
      "north": {"uv": [0, 0], "uv_size": [16, 16], "material_instance": "inner_core"},
      "south": {"uv": [0, 0], "uv_size": [16, 16], "material_instance": "inner_core"},
      ...
    }
  }
]
```

**EXCEPTION (entity vs block contexts)**: Bone-name binding IS the entity render-controller pattern — Molang queries pick textures per bone for entities. For blocks, only per-face binding works. Different systems. Don't confuse them.

**Origin**: Caught mid-build in v1.2.32 by web research. Initial Phase 1 split cubes into `inner_core` and `leaves` bones and tried to bind via bone name — verified at static check level (bone exists, material instance exists in block JSON) but would have failed at runtime. Web research confirmed face-level binding; fixed by adding face-level `material_instance` to all 6 faces of each inner_core cube.

#### Lesson #158 (CONFIRMED v1.2.32) — Godray-aware geometry: only cubes inside the block footprint matter

For overhead-godray penetration through alpha_test foliage, only cubes whose XZ footprint intersects the block's `[-8, 8) × [-8, 8)` footprint matter. Cubes that extend OUTSIDE the block boundary (e.g., corner puffs at x=[-12, -8) and face puffs at x=[8, 12)) DO NOT BLOCK overhead rays through the block — they only block oblique side rays.

For the central area, what matters is the COUNT of stacked alpha-test surfaces a vertical ray passes through. Per cube, `survival_per_cube = 1 − alpha_opaque_fraction` ≈ 0.751 for typical leaf textures. Through 4-deep canopy: `survival^(4 × cubes_per_block)`.

Vanilla baseline: 75.1% per block, 31.85% through 4-deep.

To beat vanilla while preserving puffy aesthetic, the lever is **slab thickness/footprint** (slabs triple-stack with the core in the central area). Shrinking face puffs gives zero overhead-ray benefit (they're outside the block).

A-Sweet-Spot composition (core 12×16×12 + slabs 8×4×8) yields 36.7% through 4-deep — beats vanilla by +15% with minimal silhouette loss.

#### Lesson #159 (CONFIRMED v1.2.32) — U4 atmospherics: surgical golden-hour edits

For warm-tint at golden hour without affecting mid-day or night:
1. Sun illuminance: bump only the 4 keyframes in [0.225, 0.250, 0.750, 0.775]; leave 0.0/0.150/0.500/0.850/1.0 alone
2. Ambient color: amber-bias only the 4 keyframes in [0.220, 0.250, 0.750, 0.780] by R+8, B−8
3. Color grading: highlights.gain warm bias = [1.15, 1.10, 1.05] (R+5% relative, B−5% relative). Don't touch midtones/shadows

The lighting/global.json convention used here:
- 0.0 / 1.0 = noon (full daylight)
- 0.225 = sunset golden hour
- 0.250 = sunset orange
- 0.500 = midnight
- 0.750 = sunrise dim
- 0.775 = sunrise golden hour

### Family W — Worldgen, custom-block onPlace, alpha-test rendering edge cases (v1.2.34 cycle)

#### Lesson #160 (CONFIRMED v1.2.34) — Bedrock `setblock destroy` drops the block AS ITEM, bypassing `match_tool` loot table conditions

**MCPE-50331**. When script calls `dimension.runCommand("setblock x y z air destroy")`, the resulting drops use the WRONG loot context — the block drops AS IF the player broke it bare-handed, ignoring `match_tool` conditions in the loot table. This was the bug in the v1.2.33 leaf-loot system where shears were giving stick drops instead of sapling drops.

**Correct pattern**: use `block.setPermutation(airPerm)` to clear the block, then perform manual loot rolls in script that account for the player's tool:

```js
// Clear the block silently
block.setPermutation(airPerm);
// Manually roll loot with tool awareness
if (player.getComponent('equippable').getEquipment(EquipmentSlot.Mainhand)?.typeId === 'minecraft:shears') {
  if (Math.random() < 0.05) dropItem('minecraft:sapling');
} else {
  if (Math.random() < 0.02) dropItem('minecraft:stick');
  // ... etc
}
```

#### Lesson #161 (CONFIRMED v1.2.34) — Alpha-test rendering tolerates volume overlap but NOT coplanar shared faces

For Bedrock custom-block geometry with alpha-test materials (leaves, glass-like blocks): two cubes can occupy the SAME volume (one inside the other, partial overlap, etc.) without visible z-fighting because each cube's alpha-test discards transparent pixels independently.

But two cubes that share a COPLANAR FACE (e.g., both have a face at y=8 with overlapping XZ ranges) WILL z-fight even with alpha-test material, because both faces render at the same depth and the GPU can't decide which to draw on top.

**Verification rule**: for each pair of cubes in a variant, check whether any pair of their bounding-box faces is coplanar AND overlapping in the perpendicular axes. If yes → z-fight risk. Volume overlap alone is safe.

This is why v1.2.36's `face puffs penetrate 1px into inner_core` is fine (volume overlap with `inner_core` boundary at z=±7, puff boundary at z=±6 and z=±10 — no coplanar shared faces).

#### Lesson #162 (CONFIRMED v1.2.34) — Worldgen-placed blocks NEVER fire `onPlace`

Bedrock's worldgen path places blocks directly via internal C++ calls that DO NOT trigger the script-block `onPlace` component event. Only blocks placed by player action or by `dimension.setBlockType` from script trigger `onPlace`.

**Consequence**: any randomization or initialization logic in `onPlace` will NEVER run for naturally-generated trees, ore veins, or any other worldgen content. To randomize worldgen-placed blocks, you need a periodic scanner that detects them post-placement (this is what BP-02's leaf scanner does, and what v1.2.36's runJob/getBlocks architecture optimizes).

**Implication for the variant system**: the `pickVariantForBlock` function in v1.2.36 only runs when a player breaks/places a leaf. Worldgen leaves stay at variant 0 until the scanner reaches them (which takes ~2.5s after entering chunk render range).

#### Lesson #163 (CONFIRMED v1.2.34) — Dodecagon panel chord width formula: `w = 2 × r × tan(15°)`

For a regular 12-sided polygon (dodecagon) inscribed in a circle of radius `r`, each panel's chord width is `w = 2 × r × tan(π/12) = 2 × r × tan(15°) ≈ 0.5359 × r`.

Used in v1.2.34 to fix the birch vine geometry, where 3 different panel widths were needed for different inscribed radii. The corrected widths are:
- r = 3 → w = 3.2154
- r = 3.5 → w = 3.7513
- r = 3.75 → w = 4.0192

Bad geometry (using `w = r` or `w = 2 × r × sin(15°)`) produces visible gaps or overlaps between panels. The tangent formula gives exact face-to-face contact at sub-pixel precision.

### Family X — Scanner architecture and Bedrock script performance (v1.2.36 candidate lessons)

These lessons are CANDIDATE pending corroboration by user verification of v1.2.36. They will be promoted to CONFIRMED after sprint-through-dense-forest testing confirms graphics resets are eliminated.

#### Lesson #170 (CANDIDATE v1.2.36) — `system.runJob` is the official pattern for spreading block operations across ticks

**Evidence**: Microsoft Learn ([Game Loops and Timed Callbacks](https://learn.microsoft.com/en-us/minecraft/creator/documents/scripting/system-run-guide)) explicitly recommends generator-based work spreading via `system.runJob` for any per-tick block iteration that could exceed frame budget. Synchronous loops in the scanner caused ~900ms spikes, far exceeding the 100ms script-watchdog spike threshold and triggering chunk render-mesh rebuild stalls (the "graphics reset" user observation).

**Pattern**:
```js
function* myWorkGenerator() {
  for (const item of bigList) {
    processItem(item);
    yield;  // give engine control back between each item
  }
}
system.runJob(myWorkGenerator());
```

#### Lesson #171 (CANDIDATE v1.2.36) — `dimension.getBlocks(volume, filter, allowUnloadedChunks)` is ~100× faster than nested JS getBlock loop

**Evidence**: A 51×51×14 = 36,414-cell volume scan via nested JS loop in QuickJS = ~36K native bridge calls + try/catch on unloaded chunks. Same volume via `dimension.getBlocks` with `includeTypes` filter = single native call returning a `ListBlockVolume` of only matching leaves (typically 100-400 in dense forest). Plus `allowUnloadedChunks=true` skips exception-throwing entirely for unloaded cells. Combined: from 36,414 JS iterations to ~100-400.

#### Lesson #172 (CANDIDATE v1.2.36) — `setPermutation` triggers chunk mesh rebuild even when geometry unchanged

Pre-v1.2.36 scanner wrote 4 states per leaf (`pw:section`, `pw:exposure`, `pw:section_rolled`, `pw:variant`) via chained `withState()` calls. Only `pw:variant` triggers actual geometry change (per the leaf block JSON's permutation conditions). But every `setPermutation` invalidates the chunk's render mesh regardless of whether geometry changes — the engine has to re-evaluate permutation conditions. With 120 leaves processed per scan cycle in dense forest, that's 120 unnecessary chunk mesh invalidations queued per cycle.

**v1.2.36 mitigation**: only call `setPermutation` when `pw:variant` actually changes (no-op skip if current variant matches the picked variant).

#### Lesson #173 (CANDIDATE v1.2.36) — Position parity `(x+y+z) % 2` is sufficient for asymmetric mirror pair selection

Pair members in v1.2.36 are point-mirrored around y-axis. Adjacent leaves in a canopy differ by ±1 in some coordinate, flipping the parity. This guarantees adjacent leaves get different pair members, which fills the asymmetric gaps maximally. No detection needed at scan time — geometry is encoded in coordinates.

#### Lesson #174 (CANDIDATE v1.2.36) — BlockVolume has no documented hard size limit

The BlockVolume / getBlocks docs (Microsoft Learn) document no explicit maximum dimensions. Empirically, 51×10×51 = 26,010 cells per call works fine. The bedrock-wiki performance guide warns against "hundreds of thousands of iterations per chunk of multi-block features" but that's worldgen, not scripting.

#### Lesson #175 (CANDIDATE v1.2.36) — "Graphics reset" symptom = render-pipeline stall (spike threshold), NOT watchdog kick

User reported "everything goes dark and slowly loads back up" without being kicked from the world. Matches MCPE-173706 pattern ("block faces failing to render i.e. x-ray view as you move around a build"). Caused by chunk render mesh queue overflow when many `setPermutation` calls concentrate in small region during chunk streaming activity. Distinct from watchdog `hang` termination (3000ms threshold) which would kick the player.

**Foundation note**: future ambiguous "crash" reports should ask user whether they're kicked or whether it's visual-only. The two have different root causes.

**Bedrock script watchdog thresholds (immutable for world/realm play)**:
- `spike-threshold`: 100ms (single-tick warning, not a kick; triggers engine corrective action)
- `hang-threshold`: 3000ms (kicks the script, terminates execution)
- `slow-threshold`: 2ms (warning over multiple ticks)
- Memory threshold: 250MB combined (saves and shuts down world via watchdog termination)

CRITICAL: spike events do NOT kick the player but DO cause render-pipeline stalls (chunk meshes go dark briefly while engine catches up). User report of "graphics reset" without world disconnect = spike-class symptom, not hang-class.

---

## §7. STANDING PROTOCOL — every "please continue" turn

(Established v1.1.3, extended v1.2.31 to include decision journal.)

Every turn that's not a fresh authorization starts with:
1. Read `phase_log.md` tail (last 50 lines)
2. Check `/mnt/user-data/outputs/` state for what's already shipped
3. List recently modified working files (`find /home/claude/build -mmin -60 ...`)
4. Search for `_logs/v1_X_Y*` evidence of in-progress work
5. **NEW v1.2.31**: Read `decision_journal.md` tail (entries from current build) to recover RATIONALE context, not just state

This catches amnesia before any new work is started. Critical for multi-turn builds that may span session boundaries.

---

## §8. TERMINOLOGY GLOSSARY

| Term | Meaning |
|---|---|
| **AbsolutRealism / Abs0lutRealism** | Project name (post-v1.0.1). "0" is intentional, matches user gamertag. |
| **PatrixWorld** | Project name pre-v1.0.1. Now historical. |
| **`pw:`** | Internal namespace prefix. Preserved across rename. |
| **Cascade** | Multi-tier event-driven system that propagates state changes across blocks. v1.2.28+ uses 4-tier cascade. |
| **Section scanner** | The pre-pass scanner that flags leaves with `pw:section` (0/1/2 = bottom/middle/top) and `pw:exposure` (0/1 = inner/outer). 50-radius, 100-tick interval. |
| **Variant scanner** | The downstream scanner that gates on `pw:section_rolled === true` and picks a leaf variant from the section-aware pool. 25-radius, 100-tick interval. |
| **BIGCANOPY** | The custom falling-tree mechanic. When player chops a log, the tree's logs convert to a falling-tree entity that animates falling, then the entity is destroyed and logs re-spawn at the base. Defined in `BP-02-Abs0lutRealism-Tectonic-BP/scripts/main.js`. |
| **Fancy_canopy** | Tree feature canopy spec from lesson #69. Strict size limits to prevent Android crashes. |
| **Foundation patch** | Per-version delta document amending the cumulative foundation. Now superseded by this document. |
| **Handoff** | Per-version state document for next-session amnesia recovery. Contains: where everything lives, what user authorized, what's done, what's pending. |
| **Process error log** | `/home/claude/.claude_session/error_log.md` — running log of process mistakes (selecting tier without explicit confirmation, file-state assumptions, etc.). |
| **Phase log** | `/home/claude/build/v<NNN>/_logs/phase_log.md` — per-build narrative log of what shipped when. |
| **Decision journal** | `/home/claude/build/v<NNN>/_logs/decision_journal.md` — per-build log of WHY decisions were made. NEW v1.2.31. |
| **Witness rule** | When user reports observation, defer to user. See §1.4. |
| **VV** | Vibrant Visuals — Bedrock's deferred renderer with PBR support, atmospherics, lighting/color grading, water/fog systems. Required for AbsolutRealism. Activated by `pbr` capability + `min_engine_version` ≥ `[1, 21, 120]`. |
| **MERS** | Metalness/Emissive/Roughness/Subsurface — 4-channel texture format. R=metalness, G=emissive, B=roughness, A=subsurface scattering. Stored as `_mer.png` per file convention. |
| **PBR** | Physically-Based Rendering — the rendering pipeline that uses MERS + normal maps for realistic light interaction. Bedrock VV implements PBR. |
| **Section_rolled** | Block state on leaves indicating section scanner has flagged this leaf. Gates the variant scanner. Reset to `false` by cascade events. |
| **rseed** | Block state on leaves indicating randomizer has picked a variant. Reset to `false` when section_rolled is reset, forcing re-roll. |
| **Mega-jungle** | Tall jungle tree formation; canopies extend up to 35 blocks above ground. Trigger for asymmetric scanner extent. |
| **Inner / Outer / Edge / Shell / Deep_inner** | Leaf classification depths:<br>• Edge (depth 0) = at canopy boundary, ≥1 non-leaf neighbor<br>• Shell (depth 1) = all 6 neighbors leaves, ≥1 neighbor is edge<br>• Deep_inner (depth 2+) = all 6 neighbors leaves AND no neighbor is edge<br>v1.2.29 redefined `pw:exposure`: 0 = deep_inner, 1 = outer (edge OR shell). |

---

## §9. CHANGE DIRECTIVES

These directives govern how this foundation document evolves:

1. **Authority**: This document is authoritative for everything in §1-§8. If a handoff or patch contradicts it, the foundation wins. Update the foundation in the same release if needed.

2. **Numbering**: Lesson numbers do NOT need to be contiguous. Use whichever number was assigned at first capture. New lessons get the next available number; the topic-grouped organization in §6 is what matters.

3. **Exception placement**: When a lesson has an exception, the exception MUST be grouped with the rule (per user direction). Don't separate them into different sections of the document.

4. **Falsification rule**: When a lesson is falsified, mark it `FALSIFIED` with a date and reason. Don't delete it (preserve historical lineage). The replacement lesson should reference the falsified one.

5. **Supersession rule**: When a lesson is superseded (improved upon, but old version still has historical value), mark it `SUPERSEDED v<release>` with reason. Don't delete it (preserve learning history).

6. **Promotion rule**: A `CANDIDATE` lesson promotes to `CONFIRMED` after first independent corroboration. A `CONFIRMED` lesson promotes to `PROMOTED` if reproving it cost a release cycle (i.e., the lesson is "expensively learned" — never forget it).

7. **WITNESS RULE supremacy**: When a lesson conflicts with user observation, the user wins by default. Investigate before defending the lesson.

8. **Documentation loop**: Every release ships:
   - 4 binaries (MAIN.mcaddon + ATMOSPHERIC.mcaddon + RP-04-Basic.mcpack + RP-07-Neutral-Mobs.mcpack)
   - MD5SUMS.txt
   - README-AbsolutRealism-v<X_Y_Z>-INSTALL.md
   - FOUNDATION_PATCH_v<X_Y_Z>.md (now historical; v2.0.0 will fold these into this doc)
   - ABSOLUTREALISM-HANDOFF-v<X_Y_Z>.md

9. **No retroactive renaming**: Historical artifacts retain `PatrixWorld`, `pw-`, `pw:` references where they were originally written. Don't rewrite history.

---

---

## §10. END OF FOUNDATION v2

For current ship status, queued work, and the 10 post-ship diagnostic priorities, see `CURRENT-STATE-v1_2_36.md`. For technical architecture details, see `ARCHITECTURE-v2.md`. For per-version history, see `HISTORY-v2.md`. For how to work with Abs0lum, see `OPERATING-MANUAL-v2.md`.

---

## Update for v1.3.35 patches 1-8 (May 2026) — Mob Conversion Phase

### New format versions used in mob conversion

| Asset | format_version | Notes |
|---|---|---|
| `.geo.json` (custom entity geometry) | 1.12.0 | Standard for Patrix-derived geos in v1.3.35 |
| `.entity.json` (client entity) | 1.10.0 | Standard for entity definitions |
| `.animation.json` (entity animations) | 1.8.0 | Standard for procedural Molang animations |
| `.render.json` (render controllers) | 1.10.0 | Standard for entity render controllers |

### New lessons added during patches 1-8

These extend the existing lessons #1 through #195.

#### Lesson #196: Vanilla animations silently fail on custom bone names

**Problem**: vanilla animations like `animation.quadruped.walk` reference vanilla bone names (`leg0..leg3`). When a custom geometry uses non-vanilla bone names (e.g., `front_left_leg`), the vanilla animation has nothing to target. Result: the mob appears to slide without leg motion.

**Solution**: either rename bones to match vanilla, or replace the vanilla animation reference in `entity.animations` with a custom animation that targets the actual bone names.

Found during patches 1-2 when cats and ocelots (with `front_left_leg` etc.) appeared to glide while moving.

#### Lesson #197: Diagonal leg pairing for natural quadruped walk

For a natural-looking walk, legs are diagonally paired (in-phase) and the opposite diagonal pair is antiphase:
- `leg0` (front-right) + `leg3` (back-left) in phase
- `leg1` (front-left) + `leg2` (back-right) in opposite phase

Same-side pairing (front pair and back pair separately phased) produces a bunny-hop look, not a walk.

Discovered during pig/cow walk authoring in Tier 1 animations.

#### Lesson #198: Body-rotation inverse-math for child pivot computation

When a parent bone has rotation `R`, and you want a child to render at world position `(X', Z')` (Y unchanged for Y-axis rotation), declare the child's pivot at the body-local position computed by the INVERSE rotation:

For a `[0, 45, 0]` parent rotation:
- World → body-local: `X = 0.707(X' - Z')`, `Z = 0.707(X' + Z')`
- Body-local → world: `X' = 0.707(X + Z)`, `Z' = 0.707(Z - X)`

Discovered during frog limb repositioning (Patch 7) when the body bone got `[0, 45, 0]` rotation to make the cube appear diamond from above.

#### Lesson #199: Child bone rotations compound with parent

If a parent bone has rotation `R_p` and a child has rotation `R_c`, the child's effective world-frame rotation is `R_p ∘ R_c` (composition). To achieve a desired world rotation `R_w` on a child:
- `R_c = R_p⁻¹ ∘ R_w`

For 90° single-axis rotations this is simple negation. For complex rotations it's full matrix math.

Practical rule: when you add rotation to a parent, audit ALL children's rotations and adjust as needed.

#### Lesson #200: Per-cube rotation for Y-axis flips

When a witness reports a creature appearing "upside down" across iterations of UV manipulation attempts, the issue is geometric not textural. Apply per-cube `rotation: [0, 0, 180]` with `pivot: [cube_centroid]` to flip each cube in place.

Cube-level rotation in Bedrock is set on the cube itself (not the parent bone) using:
```json
{
  "origin": [...],
  "size": [...],
  "rotation": [0, 0, 180],
  "pivot": [cube_X_center, cube_Y_center, cube_Z_center]
}
```

This rotation does NOT cascade to child bones (it's local to the cube). Useful for flipping individual cubes without affecting hierarchies.

Discovered during dolphin/turtle conversion (Patches 6-8). Patch 6 used sub-bone rotation, which had cascade issues. Patch 7 used UV manipulation, which only affected textures (not geometry). Patch 8 used per-cube rotation, which was the correct approach.

#### Lesson #201: Re-parenting decorative cubes to limb bones

For mobs where decorative cubes are attached to a static body bone but visually should move with a limb (e.g., parrot wing decoration cubes), re-parent the decorative cubes to the limb bone. Then animation of the limb moves the decoration with it.

Done in Patch 7 for parrot: 4 wing-decoration cubes moved from `body_main` to `left_wing`/`right_wing` bones. In Patch 8, the original "extending wing" cubes were removed entirely, leaving only the decoration cubes in the wing bones.

#### Lesson #202: Vanilla MC ocelot scale is smaller than cat

Vanilla MC applies a smaller `minecraft:scale` to ocelot entities than to cat entities (in the behavior pack). Resource pack geometries that are identically-sized between cat and ocelot will appear smaller for ocelots due to this BP-side scaling.

Compensate by scaling the ocelot's geometry in the resource pack: multiply all cube origins, sizes, and pivots by a compensating factor (1.4x worked for Patch 7).

#### Lesson #203: Animation amplitude threshold for natural locomotion

Walk animations scaling amplitude linearly by `* query.modified_move_speed` produce invisible legs at slow movement speeds. The amplitude at `speed=0.1` is only 10% of full, which is barely visible.

**Standard pattern**: replace `* query.modified_move_speed` with `* math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)`. This produces a smooth ramp:
- At `speed=0.0`: amplitude factor = 0
- At `speed=0.05`: amplitude factor = 1.0 (clamped)
- At `speed=1.0` (sprint): amplitude factor = 1.0

Any movement above 0.05 produces full-amplitude legs.

Standard for all walk animations in Patch 8 forward.

#### Lesson #204: Geometric vs textural causes of upside-down appearance

When a witness reports a creature appearing upside down, and UV-only manipulation does not fix it, the issue is geometric. Apply rotation (per-cube or per-bone). Lesson #200 is the per-cube version.

Diagnostic test: does the issue persist when no UV manipulation is applied AND the cube has no rotation? If yes, the geometry was authored with an inverted Y axis somewhere upstream (often in the JEM source with `invertAxis` flags).

#### Lesson #205: Bone pivots at joints, not centroids

For look-at animations and limb rotations, the bone's pivot must be at the JOINT (where the limb meets the body), not at the cube's geometric centroid. A pivot at the centroid causes the limb to rotate around its center, producing a "swinging through space" effect instead of a natural hinge motion.

Symptom: head "disconnects" from the body when looking around. Caught during Patch 8 fox investigation.

**Rule**: when you reposition a cube, ALSO reposition its bone's pivot to match the new joint location. Don't just move the cube and leave the pivot behind.

#### Lesson #206: Mob-anatomical-frame direction language

The witness uses anatomical direction terms (back, forward, left, right) relative to the mob's body orientation, NOT world coordinates. Always confirm orientation frame when receiving directional instructions.

For mobs with body rotations (frog's `[0, 45, 0]`), the mob-anatomical frame differs from both world and body-local frames. Use the mob's visual front (where the eyes point) as the "forward" reference.

---

### Lessons in the 200s — quick reference

| # | Lesson |
|---|---|
| 196 | Vanilla anims silently fail on custom bone names |
| 197 | Diagonal leg pairing for natural quadruped walk |
| 198 | Body-rotation inverse math for child pivots |
| 199 | Child rotations compound with parent — subtract when authoring |
| 200 | Per-cube rotation [0,0,180] with centroid pivot for Y-flips |
| 201 | Re-parent decorative cubes to limb bones for unified animation |
| 202 | Vanilla MC ocelot is smaller than cat — compensate via geo scaling |
| 203 | Use `math.clamp(speed * 20, 0, 1)` for animation activation threshold |
| 204 | Geometric vs textural upside-down — use rotation not UVs |
| 205 | Bone pivots at joints, not cube centroids |
| 206 | Mob-anatomical-frame direction language |

---

### Project-state-at-foundation-v3

As of end of Patch 8 (v1.3.35):
- 33 mobs in conversion scope
- ~30 mobs through at least one witness-test iteration
- All Tier 1-4 animations authored (31 original animation files)
- Patches 1-8 shipped; awaiting Patch 8 witness test
- Conversion methodology documented in JEM-TO-BEDROCK-CONVERSION-STANDARD.md
- Creator permission settled (FreshLX granted, wants final review)

Pending after Patch 8 witness test:
- Iteration on whatever Patch 8 surfaces
- Frog directional language development (after color-coded inspection)
- Final mob polish
- Methodology document hand-off to FreshLX
