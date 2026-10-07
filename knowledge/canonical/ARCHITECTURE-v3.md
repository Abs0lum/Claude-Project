# AbsolutRealism Architecture — v2 (current as of v1.2.36)

> **Authoritative technical reference for pack architecture, scanner systems, geometry, formats, and scripts.** This document supersedes:
> - `ABSOLUTREALISM-ARCHITECTURE-v1_2_31.md`
> - The architecture sections of all `ABSOLUTREALISM-HANDOFF-v*.md` (v1.2.32 → v1.2.36)
>
> Companion documents:
> - `OPERATING-MANUAL-v2.md` — How to work on this project. Read FIRST.
> - `FOUNDATION-v2.md` — Project identity, locked invariants, all lessons
> - `HISTORY-v2.md` — Per-version chronicle v1.0.0 → v1.2.36
> - `CURRENT-STATE-v1_2_36.md` — Current ship status, candidate lessons, queued work, file index

---

# AbsolutRealism Architecture — v1.2.31

> **Authoritative technical reference.** This document supersedes the architecture sections of:
> - `PATRIXWORLD_v1_0_0_FOUNDATION.md` (technical sections)
> - All `FOUNDATION_PATCH_v*.md` (technical sections)
> - All `RESEARCH-REPORT-v*.md`
>
> Companion documents: `ABSOLUTREALISM-FOUNDATION-v1_2_31.md`, `ABSOLUTREALISM-HISTORY-AND-BACKLOG-v1_2_31.md`, `ABSOLUTREALISM-DIAGNOSTICS-v1_2_31.md`.

This document is the **how it works** reference. The Foundation document is the **what's true** reference. When working on a system, read the foundation first for invariants and lessons, then read this document for the system's architecture.

---

## §1. SYSTEM ARCHITECTURE OVERVIEW

AbsolutRealism is a 16-pack Bedrock 26.x add-on. Major systems by domain:

```
┌────────────────────────────────────────────────────────────────┐
│  WORLDGEN                                                       │
│  ├─ Custom biomes (16 client_biome + matching server biomes)   │
│  ├─ Tree features (9 species × {young, mature, old, elder})    │
│  ├─ Branch features (8 species × 6 features each = 48 features)│
│  ├─ Sparse-tree variants (4 features: taiga + forest variants) │
│  └─ Bush features                                               │
├────────────────────────────────────────────────────────────────┤
│  CUSTOM BLOCKS                                                  │
│  ├─ Logs (17 trunk types × ~35 perms each = 595 perms)         │
│  ├─ Leaves (9 species × 7 variants × 2×3×2×2 implicit = 168)   │
│  ├─ Branches (8 species × 4 directions = 32 perms)             │
│  └─ pw:variant + pw:rseed + section/exposure storage states    │
├────────────────────────────────────────────────────────────────┤
│  LEAF VARIANT SYSTEM (4-tier cascade)                          │
│  ├─ Tier 1: section flag scanner (50-radius, 100-tick)         │
│  ├─ Tier 2: variant scanner (25-radius, 100-tick)              │
│  ├─ Tier 3: cascade event subscriptions                        │
│  │  ├─ playerBreakBlock cascade                                │
│  │  ├─ explosion cascade                                       │
│  │  ├─ BIGCANOPY-inline cascade                                │
│  │  └─ decay-scanner re-validation cascade                     │
│  └─ Tier 4: bidirectional re-validation                        │
├────────────────────────────────────────────────────────────────┤
│  BIGCANOPY (falling-tree mechanic)                             │
│  ├─ findConnectedTree BFS log discovery                        │
│  ├─ detectTrunkWidth (1×1 vs 2×2)                              │
│  ├─ hasAdjacentLeaves validation                               │
│  ├─ falling_tree entity (12 dodecagon + 11 box geometries)     │
│  ├─ FALL_KEYS animation + settling bounce                      │
│  ├─ Mid-fall leaf shedding                                     │
│  ├─ Tree-fall + impact sounds                                  │
│  └─ Leaf litter spawn after fall                               │
├────────────────────────────────────────────────────────────────┤
│  ATMOSPHERICS / VV (Vibrant Visuals)                            │
│  ├─ atmospherics (10 files, sky/sun/moon/mie keyframes)        │
│  ├─ lighting (10 files, orbital + sky + ambient)               │
│  ├─ color_grading (10 files, ACES tone + per-zone gain)        │
│  ├─ water (22 files per-biome)                                 │
│  ├─ fogs (51 files distance + volumetric)                      │
│  ├─ local_lighting (87 entries per-block emissive)             │
│  └─ client_biome (16 files for biome-specific routing)         │
├────────────────────────────────────────────────────────────────┤
│  PBR / TEXTURES                                                 │
│  ├─ texture_set.json (4-channel MERS at format_version 1.21.30)│
│  ├─ Cross-pack PBR layering rules (RP-03 self-contained)       │
│  ├─ Variations (sand v0..v15, stone v0..v7, etc.)              │
│  └─ Sun/moon textures + lens flare particles                   │
├────────────────────────────────────────────────────────────────┤
│  SCRIPTING (BP-02 main.js, ~2500+ lines)                        │
│  ├─ @minecraft/server v2.0.0                                   │
│  ├─ Custom block components (pw:randomize_variant)             │
│  ├─ system.runInterval scanners                                │
│  ├─ world.afterEvents subscriptions                            │
│  └─ Entity property reads/writes for falling-tree state        │
├────────────────────────────────────────────────────────────────┤
│  AUDIO + PARTICLES                                              │
│  ├─ Tree fall + impact sounds (8 events, 14 .ogg files)        │
│  ├─ pw:leaf_fall particle (5/spawn, 3-sec lifetime)            │
│  ├─ Lens flare particles (4 entity-billboard particles)        │
│  └─ pw:ambient.* (122 dormant; AmbientSounds port queued)      │
└────────────────────────────────────────────────────────────────┘
```

---

## §2. LEAF VARIANT SYSTEM (the centerpiece architecture)

The leaf variant system is the most complex and architecturally significant system in v1.2.31. It uses a **4-tier cascade** to keep custom-leaf geometry coherent across all possible block-state mutations.

### 2.1. State storage (block states)

Each `pw:*_leaves` block declares **5 storage states**:

| State | Type | Range | Purpose |
|---|---|---|---|
| `pw:variant` | int | [0, 6] | Final geometry choice (0..6) |
| `pw:rseed` | bool | [false, true] | Variant-randomizer "rolled" gate |
| `pw:section` | int | [0, 1, 2] | Canopy vertical section (bottom/middle/top) |
| `pw:exposure` | int | [0, 1] | Inner (depth ≥ 2) vs outer (depth 0 or 1) |
| `pw:section_rolled` | bool | [false, true] | Section-flagger's "rolled" gate |

Total implicit permutations per block: 7 × 2 × 3 × 2 × 2 = **168** (well under engine limit).

### 2.2. Geometry — 7 variants

`pw_leaves_variants.geo.json` defines 7 geometries. As of v1.2.31:

| Variant | Section | Exposure | Cubes | Composition |
|---|---|---|---|---|
| 0 | (worldgen default) | — | **8** | 1 core + 4 +X corner puffs + top + bottom + +X face slab |
| 1 | bottom | outer | 10 | 1 core + 4 bottom corners + 4 axis + bottom face |
| 2 | bottom | outer | 9 | 1 core + 4 bottom corners + 4 axis (alt) |
| 3 | (deep_inner) | inner | **8** | 8 corner puffs only (truly empty interior) |
| 4 | middle | outer | 5 | 1 core + 4 horizontal corners |
| 5 | top | outer | 9 | 1 core + 4 top corners + 3 axis + top face |
| 6 | top | outer | 7 | 1 core + 4 top corners + 2 axis (alt) |

**Cube count signature**: `[8, 10, 9, 8, 5, 9, 7]`. Verifier check V8 enforces this exact pattern.

**variant_0 directional design (v1.2.31)**: All leaves orient identically in world-space; +X corners on every block co-locate with adjacent block's missing -X side. Asymmetric per-block, symmetric in aggregate. Per Lesson F-08, the +X corners overlap with adjacent block's -X gap, creating the illusion of complete coverage.

**variant_3 (deep_inner)**: 8 corner puffs only, no core cube. Truly empty interior — players inside the canopy see swiss-cheese geometry. Hidden from outside view by the 2-block-deep outer mantle.

**Render method**: All 63 leaf permutations use `render_method: "alpha_test"` (LOCKED INVARIANT, Lesson F-04). NEVER use `alpha_test_to_opaque` — solid shadow casting through transparent pixels is a hidden cost.

### 2.3. Variant pool keying

```js
const PW_LEAF_VARIANT_POOLS = {
  // Section-Exposure → array of valid variant indices (with weights via repetition)
  "0_1": [1, 1, 2, 2],          // bottom outer → variants 1, 2 (bias toward 1)
  "0_0": [3, 3, 3],             // bottom inner (rare) → variant 3
  "1_1": [4, 4, 4, 4],          // middle outer → variant 4 (most common)
  "1_0": [3, 3, 3, 3, 3, 3],    // middle inner (most common) → variant 3
  "2_1": [5, 5, 6, 6],          // top outer → variants 5, 6 (bias toward 5)
  "2_0": [3, 3, 3],             // top inner (rare) → variant 3
};
// Default fallback: variant 0 (worldgen, before any flagging)
function pickVariantForBlock(section, exposure) {
  const pool = PW_LEAF_VARIANT_POOLS[`${section}_${exposure}`];
  if (!pool) return 0;
  return pool[Math.floor(Math.random() * pool.length)];
}
```

### 2.4. Leaf Scanner v1.2.36 — Layered runJob Architecture (CURRENT)

> **Supersedes**: §2.4 Section flag scanner (v1.2.27-v1.2.34), §2.5 Variant scanner (v1.2.27-v1.2.34), §2.6 Cascade event subscriptions (v1.2.28-v1.2.34).
>
> **Reason for supersession**: The v1.2.34-v1.2.35 scanner used synchronous nested-loop block scanning that caused ~900ms tick spikes in dense forests, exceeding the 100ms script-watchdog spike-threshold by 9× and triggering chunk render-pipeline stalls (the "graphics reset" symptom user reported in v1.2.35).

#### 2.4.1. Architecture overview (v1.2.36 — Tier C full)

Six coordinated systems replace the old multi-tier scanner:

1. **`system.runJob` generator pacing** — engine spreads scanner work across ticks automatically
2. **`dimension.getBlocks(volume, filter, allowUnloadedChunks=true)`** — native C++ batch filter
3. **In-memory `_pwProcessedFlags` Map** — no `pw:section_rolled` state writes (eliminates GC pressure)
4. **5-layer downward sweep** — covers player.y+35 down to player.y-15 in 5 layers of 51×10×51
5. **Movement-triggered cadence** — next sweep starts when player has moved >8 blocks since last sweep
6. **Teleport detection** — movement >16 blocks/tick clears flag map and triggers immediate fresh sweep

See Lessons #170–#175 in FOUNDATION-v2.md §6.5 for the supporting evidence and mechanism details.

#### 2.4.2. Scan parameters (locked)

```
PW_LAYER_RADIUS_XZ   = 25       (51-wide horizontal scan box)
PW_LAYER_HEIGHT      = 10       (10 vertical blocks per layer)
PW_LAYER_COUNT       = 5        (5 layers = 50 vertical coverage)
PW_TOP_OFFSET        = 35       (top edge of top layer at player.y+35)
PW_LAYER_SPACING_TICKS = 10     (10t between layer starts → 2.5s full sweep)
PW_MOVE_TRIGGER_DIST_SQ = 64    (>8 blocks moved triggers next sweep)
PW_TELEPORT_THRESHOLD_SQ = 256  (>16 blocks/tick = teleport)
PW_POST_TELEPORT_DELAY_TICKS = 10  (chunk-settle delay before first sweep)
PW_DIAG_WINDOW_TICKS = 100      (5-second diagnostic aggregation)
```

Layer centers (top to bottom):
- Layer 0: `player.y + 30` (covers y=[25, 35])
- Layer 1: `player.y + 20` (covers y=[15, 25])
- Layer 2: `player.y + 10` (covers y=[5, 15])
- Layer 3: `player.y` (covers y=[-5, 5])
- Layer 4: `player.y - 10` (covers y=[-15, -5])

Per layer: 51 × 10 × 51 = 26,010 cells. Native filter returns only the matching leaves (~50-400 in dense forest).

#### 2.4.3. Section detection (replaces section/exposure)

Old approach: walk-up 32 + walk-down 32 + 6 face-neighbor reads = 70+ reads per leaf.

v1.2.36 approach: 2 reads per leaf (above + below):
```javascript
function _pwDetectSection(dim, x, y, z) {
  let hasLeafAbove = false, hasLeafBelow = false;
  try {
    const above = dim.getBlock({ x, y: y + 1, z });
    if (above && PW_LEAF_TYPES_SET.has(above.typeId)) hasLeafAbove = true;
  } catch {}
  try {
    const below = dim.getBlock({ x, y: y - 1, z });
    if (below && PW_LEAF_TYPES_SET.has(below.typeId)) hasLeafBelow = true;
  } catch {}
  if (!hasLeafAbove && !hasLeafBelow) return 2;  // isolated → top
  if (!hasLeafAbove) return 2;                    // canopy top
  if (!hasLeafBelow) return 0;                    // canopy bottom
  return 1;                                       // middle
}
```

Returns section value matching the legacy `pw:section` state (0=bottom, 1=middle, 2=top) for diagnostic compat. Block JSON still defines `pw:section`, `pw:exposure`, `pw:section_rolled` states for save compatibility but they are no longer written by the scanner.

#### 2.4.4. Variant selection within section

7 variants total: v0 (worldgen safety net) + 6 contextual variants in 3 asymmetric mirror pairs.

```javascript
function _pwPickVariantForSection(section, x, y, z) {
  const parity = ((x + y + z) % 2 + 2) % 2;  // 0 or 1
  if (section === 0) return parity === 0 ? 1 : 2;  // bottom pair
  if (section === 1) return parity === 0 ? 3 : 4;  // middle pair
  return parity === 0 ? 5 : 6;                      // top pair
}
```

Within-pair selection by `(x+y+z) % 2` parity is fully deterministic — no detection needed. Adjacent leaves alternate between pair members, filling each other's asymmetric gaps. See Lesson #173 for the rationale.

#### 2.4.5. Diagnostic event API

Toggle scanner diagnostics via scriptevents (default OFF):
- `/scriptevent pw:diag_on` — enable 5-second aggregated chat reports
- `/scriptevent pw:diag_off` — silence
- `/scriptevent pw:scanner_force_sweep` — clear flags + force immediate sweep for executing player
- `/scriptevent pw:scanner_clear_flags` — clear flag map only (testing aid)

When enabled, scanner emits aggregated messages every 100 ticks via `world.sendMessage`:
```
[pw:scanner] sweeps: 4→4 | layers: 20 | leaves: scanned=130050 found=412 skipped=890 |
  flagged: T=84 M=210 B=118 | rand: T=84 M=210 B=118 | teleports=2
```

Counters in `_pwDiagState`: `scanned`, `leavesFound`, `skippedAlreadyProcessed`, `flaggedTop/Middle/Bottom`, `randomizedTop/Middle/Bottom`, `sweepsStarted/Completed`, `layersCompleted`, `teleportsDetected`, `flagMapResets`.

### 2.5. (RESERVED) — formerly Variant scanner pre-v1.2.36

> **Section deprecated**. Folded into §2.4 (unified scanner architecture).

### 2.6. (RESERVED) — formerly Cascade event subscriptions pre-v1.2.36

> **Section deprecated** — folded into §3.8 (Leaf clearing + cascade integration) and §2.4's `_pwProcessedFlags.delete()` pattern.

### 2.6a. BIGCANOPY cascade integration with new scanner

When BIGCANOPY's falling-tree mechanic clears a leaf via `setblock destroy` (which is actually `setPermutation(air)` per Lesson #160), the 6 face neighbors' sections may have changed (the leaf just above now has no leaf above → became "top"). The OLD scanner used a `_pendingCascades` queue. The NEW scanner uses direct flag map invalidation:

```javascript
const dimId = dim.id;
const offsets = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]];
for (const [dx, dy, dz] of offsets) {
  const k = `${p.x+dx},${p.y+dy},${p.z+dz},${dimId}`;
  _pwProcessedFlags.delete(k);
}
_pwProcessedFlags.delete(`${p.x},${p.y},${p.z},${dimId}`);
```

Next scanner sweep re-processes these positions and picks the correct variant for the new section.

### 2.7. Migration (cross-version state transition)

When a user installs v1.2.27+ on an existing world with leaves placed by older versions, those leaves have `pw:rseed=true` (set by old randomizer with old 4-variant pool). The migration trigger is **section-scanner reset of rseed**:

```js
// Section flag scanner writes BOTH:
block.setPermutation(block.permutation
  .withState("pw:section", section)
  .withState("pw:exposure", exposure)
  .withState("pw:section_rolled", true)
  .withState("pw:rseed", false));    // ← migration gate
```

The reset of `pw:rseed=false` forces the variant scanner to re-pick using the new section/exposure-aware pool. Without this, existing trees would render with new geometries against their stale random distribution = visible regression. This is **Lesson #144 (CONFIRMED)** — cross-version state migration via flag reset.

### 2.8. Worldgen weighting (BIGCANOPY layer variants)

Worldgen places leaves at variant_0 (the default). Once the section scanner runs, leaves migrate to section-appropriate variants. The legacy `PW_LEAF_LAYER_VARIANTS` weighting is now informational — actual variant selection is via the variant scanner pool.

For trees placed by `BIGCANOPY` script (not used in current worldgen — vanilla worldgen places leaves at variant_0):
```
STANDALONE: [0, 1, 1, 2, 2, 3, 3]   // all variants
BOTTOM:     [0, 1, 1, 3, 3]          // exclude v2 (no bottom puffs in alt)
MIDDLE:     [0, 1, 1, 2, 2, 3, 3]    // full set
TOP:        [0, 2, 2, 3, 3]          // exclude v1 (no top puffs in alt)
```

---

### 2.9. Variant scheme v1.2.36 — 7 uniform variants with asymmetric mirror pairs

> **Supersedes**: §2.2 Geometry — 7 variants (v1.2.27-v1.2.35 variable cube counts).

All 7 variants are uniformly 9 cubes each (8 leaves + 1 inner_core), sharing the same `inner_core` (14×14×14 at [-7,1,-7]) for consistent material binding.

#### 2.9.1. Variant roles

| Variant | Role | Geometry summary |
|---|---|---|
| v0 | Worldgen safety net | 4 bottom corner puffs + 4 top corner puffs + inner_core (symmetric, neutral) |
| v1 | Bottom pair A | 4 bottom corners + bottom slab + N+E face puffs + NW mid-corner |
| v2 | Bottom pair B | 4 bottom corners + bottom slab + S+W face puffs + SE mid-corner |
| v3 | Middle pair A | NW+SE diagonal corners (top+bottom) + N+E face puffs + NW+SE mid-corners |
| v4 | Middle pair B | NE+SW diagonal corners (top+bottom) + S+W face puffs + NE+SW mid-corners |
| v5 | Top pair A | 4 top corners + top slab + N+E face puffs + NW mid-corner |
| v6 | Top pair B | 4 top corners + top slab + S+W face puffs + SE mid-corner |

**Mirror axis**: y-axis point rotation. Position (x,y,z) in pair A ↔ (-x,y,-z) in pair B. y coordinate preserved (so section emphasis stays correct).

#### 2.9.2. Cube coordinates per variant (for reproducibility)

Common to all variants:
- `inner_core`: `[14, 14, 14] at [-7, 1, -7]` → occupies x∈[-7,7], y∈[1,15], z∈[-7,7]

8 corner positions (4 bottom + 4 top, all 4×4×4):
```
BOTTOM_CORNERS = [
  [-11, -4, -11],  // NW bottom
  [ 7, -4, -11],   // NE bottom
  [-11, -4,  7],   // SW bottom
  [ 7, -4,  7],    // SE bottom
]
TOP_CORNERS = [
  [-11, 16, -11],  // NW top
  [ 7, 16, -11],   // NE top
  [-11, 16,  7],   // SW top
  [ 7, 16,  7],    // SE top
]
```

Face puffs at mid-height y∈[5,11]:
```
FACE_PUFF_N: origin=[-3, 5,-10] size=[6, 6, 4]
FACE_PUFF_S: origin=[-3, 5,  6] size=[6, 6, 4]
FACE_PUFF_E: origin=[ 6, 5, -3] size=[4, 6, 6]
FACE_PUFF_W: origin=[-10,5, -3] size=[4, 6, 6]
```

Slabs (8×4×8):
```
SLAB_BOTTOM: origin=[-4, -4, -4] size=[8, 4, 8]
SLAB_TOP:    origin=[-4, 16, -4] size=[8, 4, 8]
```

Mid-corner accents at y∈[6,10] (small 4×4×4):
```
MID_CORNER_NW: [-11, 6, -11]
MID_CORNER_NE: [ 7,  6, -11]
MID_CORNER_SW: [-11, 6,  7]
MID_CORNER_SE: [ 7,  6,  7]
```

Per-variant cube lists:
```
v0: BOTTOM_CORNERS + TOP_CORNERS + inner_core
v1: BOTTOM_CORNERS + SLAB_BOTTOM + FACE_PUFF_N + FACE_PUFF_E + MID_CORNER_NW + inner_core
v2: BOTTOM_CORNERS + SLAB_BOTTOM + FACE_PUFF_S + FACE_PUFF_W + MID_CORNER_SE + inner_core
v3: [BOTTOM_CORNERS[0], BOTTOM_CORNERS[3], TOP_CORNERS[0], TOP_CORNERS[3]] + FACE_PUFF_N + FACE_PUFF_E + MID_CORNER_NW + MID_CORNER_SE + inner_core
v4: [BOTTOM_CORNERS[1], BOTTOM_CORNERS[2], TOP_CORNERS[1], TOP_CORNERS[2]] + FACE_PUFF_S + FACE_PUFF_W + MID_CORNER_NE + MID_CORNER_SW + inner_core
v5: TOP_CORNERS + SLAB_TOP + FACE_PUFF_N + FACE_PUFF_E + MID_CORNER_NW + inner_core
v6: TOP_CORNERS + SLAB_TOP + FACE_PUFF_S + FACE_PUFF_W + MID_CORNER_SE + inner_core
```

**Z-fight verification (per Lesson #161)**: all 7 variants checked, 0 coplanar shared faces. Face puffs penetrate 1px into inner_core (volume overlap, safe). Corner puffs at y=[-4,0] or y=[16,20] don't share planes with inner_core at y=[1,15].

#### 2.9.3. Material instance binding (per Lesson #157)

Per-face `material_instance` field binds each cube face to a named material instance defined in the block JSON's `minecraft:material_instances`. The `inner_core` cube has all 6 faces bound to the `"inner_core"` material instance, which uses a saturation-boosted texture for the U2 rim-glow effect.

NOT bone-name binding (that's the entity render-controller pattern).

## §3. BIGCANOPY (FALLING-TREE MECHANIC)

Located in `BP-02-Abs0lutRealism-Tectonic-BP/scripts/main.js`. ~1500+ lines of code dedicated to falling-tree behavior.

### 3.1. Activation conditions

A tree falls when:
1. Player breaks a log block via tool (playerBreakBlock event fires)
2. Block is one of 17 trunk types in `PW_LOG_TYPES`
3. `findConnectedTree()` returns ≥ 1 connected log
4. `hasAdjacentLeaves()` validation passes (rejects player-built log walls)
5. Total log count ≤ MAX_LOGS = 200 (budget cap)

### 3.2. findConnectedTree (BFS)

Standard BFS from broken log. Walks 26 connectivity (face + edge + diagonal) in a bounding box up to 12 blocks high × 6 wide. Returns the set of all connected log positions.

```js
const QUEUE = [start];
const VISITED = new Set();
while (QUEUE.length > 0 && VISITED.size < MAX_LOGS) {
  const pos = QUEUE.shift();
  const key = `${pos.x},${pos.y},${pos.z}`;
  if (VISITED.has(key)) continue;
  VISITED.add(key);
  for (const [dx, dy, dz] of OFFSETS_26) {
    const npos = { x: pos.x + dx, ... };
    const nb = dim.getBlock(npos);
    if (nb && PW_LOG_TYPES.has(nb.typeId)) QUEUE.push(npos);
  }
}
return Array.from(VISITED);
```

### 3.3. detectTrunkWidth

Determines if tree is 1×1 (oak/birch/jungle/spruce young/mature/old) or 2×2 (any elder species + dark_oak + acacia + cherry + mangrove + pale_oak). Used to select the correct falling-tree geometry.

```js
function detectTrunkWidth(stump) {
  // Check 4 quadrants around stump for additional log presence
  const checks = [[1,0,0], [0,0,1], [1,0,1]];  // +X, +Z, +X+Z
  let width = 1;
  for (const [dx, dy, dz] of checks) {
    const nb = dim.getBlock({ x: stump.x + dx, y: stump.y, z: stump.z + dz });
    if (nb && PW_LOG_TYPES.has(nb.typeId)) width = 2;
  }
  return width;
}
```

### 3.4. hasAdjacentLeaves

Concern #3 from v1.0.0 — rejects player-built log walls. A real tree always has ≥ 1 leaf block adjacent to its top log. A log wall has zero leaves nearby.

```js
function hasAdjacentLeaves(logs) {
  const top = logs.reduce((max, p) => p.y > max.y ? p : max, logs[0]);
  for (const [dx, dy, dz] of OFFSETS_26) {
    const nb = dim.getBlock({ x: top.x + dx, y: top.y + dy, z: top.z + dz });
    if (nb && (nb.typeId.endsWith("_leaves") || nb.typeId.endsWith("_wart_block"))) {
      return true;
    }
  }
  return false;
}
```

### 3.5. Falling-tree entity

Defined in `BP-02-.../entities/falling_tree.entity.json`. Properties:
- `ft:wood_type` (int 0-12, species index in SPECIES roster)
- `ft:trunk_width` (int 1 or 2)
- `ft:fall_angle` (float, set per-fall)

Geometry: `geometry.ft_falling_tree.<species>_<tier>` — multiple geometries handle dodecagon trunks (oak/spruce/jungle/birch × young/mature/old = 12 dodecagon geometries) and 2×2 box trunks (elder species + dark_oak + acacia + cherry + mangrove + pale_oak = 11 box geometries).

### 3.6. FALL_KEYS animation

Controlled by `falling_tree.animation.json`. Two animations:
- `animation.ft_falling_tree.fall` — main fall arc, ~1.5 sec, hand-tuned keyframes
- `animation.ft_falling_tree.rest` — settling bounce (v1.2.30 enhancement, 5 keyframes over 600ms)

```json
"animation.ft_falling_tree.rest": {
  "loop": "hold_on_last_frame",
  "animation_length": 0.6,
  "bones": {
    "root": {
      "rotation": {
        "0.0":  ["q.property('ft:fall_angle')",     0, 0],
        "0.15": ["q.property('ft:fall_angle') - 4", 0, 0],
        "0.3":  ["q.property('ft:fall_angle') + 1", 0, 0],
        "0.45": ["q.property('ft:fall_angle') - 0.5", 0, 0],
        "0.6":  ["q.property('ft:fall_angle')",     0, 0]
      }
    }
  }
}
```

Per Lesson #153 (candidate v1.2.30): Molang keyframes with per-entity dynamic base allow reusable damped-oscillation animations.

### 3.7. Mid-fall leaf shedding (v1.2.30)

After spawning the falling-tree entity, schedule 3 bursts of leaf_litter spawns at 30%, 55%, 80% of fall arc:
```js
const SHED_FRACTIONS = [0.3, 0.55, 0.8];
const fallDurationTicks = 25;
for (const frac of SHED_FRACTIONS) {
  system.runTimeout(() => {
    const sheddingCount = 2 + Math.floor(Math.random() * 3);
    for (let i = 0; i < sheddingCount; i++) {
      const offsetX = (Math.random() - 0.5) * 8;
      const offsetZ = (Math.random() - 0.5) * 8;
      const offsetY = 4 + Math.random() * 8;
      const ent = dimension.spawnEntity("pw:leaf_litter", {
        x: stump.x + offsetX, y: stump.y + offsetY, z: stump.z + offsetZ
      });
    }
  }, Math.floor(fallDurationTicks * frac));
}
```

### 3.8. Leaf clearing + cascade integration

After fall animation, BIGCANOPY clears the canopy via `setblock ... air destroy`. Each cleared leaf triggers an inline cascade for its neighbors:
```js
for (const leafLoc of foundLeaves) {
  dim.runCommand(`setblock ${leafLoc.x} ${leafLoc.y} ${leafLoc.z} air destroy`);
  for (const [dx, dy, dz] of OFFSETS_6) {
    const nb = dim.getBlock({ x: leafLoc.x + dx, y: leafLoc.y + dy, z: leafLoc.z + dz });
    if (nb && PW_LEAF_TYPES.has(nb.typeId)) {
      _enqueueCascade({ x: nb.location.x, y: nb.location.y, z: nb.location.z, dim });
    }
  }
}
```

### 3.9. Sounds (v1.2.21)

8 sound events registered in RP-01 sound_definitions.json:
- `pw.tree_fall.{small, medium, big, generic}` (4 events)
- `pw.tree_impact.{small, medium, big, generic}` (4 events)

14 .ogg files mapped per tier:
- Small: 3 fall + 3 impact (young trees: oak/birch/jungle/spruce young)
- Medium: 2 fall + 1 impact (mature trees)
- Big: 2 fall + 1 impact (old/elder trees)
- Generic: 1 fall + 1 impact (crimson, warped, mushroom)

Triggered on fall start (after `playAnimation`) + impact (collision-stop OR 1.8s natural completion).

### 3.10. Particles (v1.2.21)

`pw:leaf_fall` particle defined in RP-01 particles/. 5 leaves per spawn, 3-second lifetime, downward acceleration with drag, billboard rendering. Triggered alongside `falling_dust_mud_particle` at 5 timed phases through fall arc (15%, 30%, 50%, 70%, 85%).

Skipped for nether/mushroom species (no leaves).

---

## §4. ATMOSPHERICS / VV ARCHITECTURE

The Vibrant Visuals system is configured via 6 file types in RP-02 (Atmospheric Effects RP). Each has a strict format_version (see Foundation §3).

### 4.1. atmospherics/*.json (format_version 1.21.40)

Per-biome sky/sun/moon parameters. 10 files: default + 9 biome-specific.

**Reserved default**: `atmospherics/atmospherics.json` (NOT `global.json`).

Key sub-objects:
- **`sky_horizon_color`** / **`sky_zenith_color`** — keyframed RGB at time-of-day stops (0.0 / 0.23 / 0.30 / 0.50 / 0.70 / 0.77 / 1.00 typical). v1.2.31 values approximate cinematic-realism (not Vibrant BSL extreme).
- **`sun_mie_strength`** / **`sun_glare_shape`** / **`sun.illuminance`** keyframed. Sun-disc visibility depends on these three knobs interacting (Lesson #195 from v1.1.3: "sun visibility is a three-knob problem").
- **`moon_mie_strength`** / **`moon.illuminance`** / **`moon.color`** — similar shape. v1.0.1 reduced moon_mie peak from 0.5 → 0.15 to fix Diagnostic #1 (moon disc washed out).
- **`rayleigh_strength`** — atmospheric scattering bias.
- **`horizon_blend_stops`** — gradient transition between horizon and zenith.

### 4.2. lighting/*.json (format_version 1.26.0)

Per-biome lighting. 10 files: default (`global.json` — note this one IS "global", different from atmospherics).

Key sub-objects:
- **`directional_lights.orbital.sun`** — illuminance keyframes, color keyframes. v1.2.0 cinematic baseline: 27 illuminance keyframes, 22 color stops painterly progression.
- **`directional_lights.orbital.moon`** — same shape. v1.2.0: illuminance peak 0.85, color [200, 225, 255], moon_mie 2.0.
- **`sky.intensity`** — 0..1 multiplier. v1.2.0 cinematic: 0.7 default, alpine 0.85, pale 0.6.
- **`ambient.illuminance`** + **`ambient.color`** — keyframed, v1.2.0 added time-of-day color tints.
- **`emissive_desaturation`** — 0 = full saturation on emissive blocks; >0 desaturates.
- **`flash`** (End only) — purple flash spec.

### 4.3. color_grading/*.json (format_version 1.21.90)

Per-biome ACES tone mapping. 10 files: default + 9 biome.

**Reserved default**: `color_grading/color_grading.json`.

Key sub-objects:
- **`saturation`** (1.0 = neutral; v1.2.0 used 1.55 for cinematic)
- **`contrast`** / **`gamma`** / **`gain`** — global
- **`highlights.gain`** + **`highlightsMin`** (v1.2.0 added: highlightsMin=20 isolates highlights to brightest pixels)
- **`shadows.gain`**
- **`midtones.gain`** + **`midtonesMax`** (v1.2.0 added: midtonesMax=55 upper bound for midtones)

### 4.4. water/*.json (format_version 1.26.0)

Per-biome water. 22 files (10 biomes × 2 contexts).

**Reserved default**: `water/water.json`.

Schema notes:
- `sampleWidth` is DEPRECATED in 1.21.120. v1.0.0 strips it from all 22 files.
- 1.26.0 has NO `surface`, `foam`, or `subsurface` blocks (Lesson H-23) — they're flat objects, not nested.
- `caustics.power` is INT (1-6), NOT float (Lesson H-22).
- `biome_water_color_contribution` (1.26.0 feature) — 0..1 weight for biome tint.
- `particle_concentrations` per-biome (clearer/murkier water character).
- `waves` sub-object: depth/octaves with calibrated values per biome.

### 4.5. fogs/*.json (format_version 1.21.90)

Per-biome fog. 51 files (most biomes need both atmospheric + cave fogs).

Schema:
- `render_distance_type`: `"fixed"` (legacy) or `"render"` (auto-scaling — v1.2.7+ pattern).
- `fog_start` / `fog_end`: float (0..1 percentage when type=render; absolute distance when type=fixed).
- `volumetric.density.air.uniform` (1.26.0): true = single uniform density layer; false = layered.
- `volumetric.density.air.max_density`: ≤ 0.05 (v1.1.0 ceiling; was 0.06 in v1.0.1). 0.150 crashes Android Bedrock (Lesson H-14 PROMOTED).
- `volumetric.density.air.zero_density_height`: ≤ 250 (v1.1.0 ceiling; was 320).
- `henyey_greenstein_g`: 0.5..0.7 (RC range — v1.2.7 retune from 0.85..0.92).
- `media_coefficients.scattering`: cool grey-blue baseline (`#10181f` — RC pattern from v1.2.7).

### 4.6. local_lighting (format_version 1.21.120)

`RP-02/local_lighting/local_lighting.json` — 87 entries (was 91 pre-v1.1.1, then 4 removed for invalid keys).

Schema:
```json
{
  "minecraft:local_light_settings": {
    "<bedrock-block-identifier>": {
      "light_color": [r, g, b],  // 0-1 floats
      "light_type": <int 1-6>     // light_intensity tier
    },
    ...
  }
}
```

**Validity rules** (Lesson #N from v1.1.1):
1. Identifier must reference an actual Bedrock block (NOT entity, NOT rendering effect).
2. Identifier must use Bedrock namespace (not Java).
3. Identifier must exist (`minecraft:end_crystal` is entity, `minecraft:portal` is rendering effect, `minecraft:end_gateway` is rendering effect — all caused `light_type out of range [1, 6]` cascade errors).

### 4.7. client_biome/*.json (format_version 1.21.120)

Per-biome client-side rendering routing. 16 files map biome ID → atmospherics + lighting + color_grading + water identifiers.

```json
{
  "format_version": "1.21.120",
  "minecraft:client_biome": {
    "description": { "identifier": "pw:forest" },
    "components": {
      "minecraft:atmospherics_identifier": { "atmospherics_identifier": "pw:forest" },
      "minecraft:lighting_identifier": { "lighting_identifier": "pw:forest_lighting" },
      "minecraft:color_grading_identifier": { "color_grading_identifier": "pw:forest_color_grading" },
      "minecraft:water_identifier": { "water_identifier": "pw:forest_water" }
    }
  }
}
```

**Lesson #149**: Server biome with `replace_biomes` configuration but no matching `pw_*.client_biome.json` will render with REPLACED vanilla biome's colors/atmospherics, not custom values. v1.0.1 fixed this for 6 affected biomes.

### 4.8. Per-biome lighting variation (v1.2.0)

Each biome inherits cinematic structure and tints ambient color keyframes:

```
forest      → green-warm cream daytime, golden canopy sunset, indigo night, sky 0.65, ambient ×0.95
cherry      → pink-warm all-day, pink-coral sunset, slightly warmer moon [210,215,245], sky 0.7
coastal     → cool cream day, warm sunset over water, deeper indigo, brighter moon ×1.15, sky 0.72
desert_dunes→ warm tan, deep gold-amber sunset, brighter sky 0.75, ambient ×1.1
alpine      → cool blue-white, cold indigo night, brightest sky 0.85, brighter moon ×1.1, ambient ×1.15
pale        → neutral gray, eerie cold dim night, dimmer sky 0.6, ambient ×0.85
river_canyon→ warm afternoon, deep canyon-gold sunset, sky 0.7, default ambient
```

---

## §5. PBR / MERS AUTHORING

### 5.1. texture_set.json (format_version 1.21.30)

The MERS pattern is 4-channel (R=Metalness, E=Emissive, R=Roughness, S=Subsurface):

```json
{
  "format_version": "1.21.30",
  "minecraft:texture_set": {
    "color": "<basename>",                    // sibling color PNG
    "metalness_emissive_roughness_subsurface": "<basename>_mer"  // sibling RGBA PNG
  }
}
```

Or with inline uniform values:
```json
"metalness_emissive_roughness_subsurface": [0, 0, 200, 12]
```

`format_version 1.21.30` is for MERS. `format_version 1.16.100` is MER-only (no subsurface) — DO NOT USE for new authoring.

### 5.2. Per-category subsurface (S) values

| Category | S value | Notes |
|---|---|---|
| Wood | 12 | Logs, planks |
| Plants | 90 | Grass, ferns |
| Leaves | 100 | Foliage (NOT 35-59 baseline — those were v1.0.0 source samples) |
| Coral | 80 | Coral blocks |
| Snow | 200 | Snow, packed ice |

**v1.2.30 change**: S values for leaves were too low in source (35-65 range). v1.2.30 scaled all 54 leaf MER textures ×2 → S avg 96-123. v1.2.31 added asymmetric bump (×1.15 uniform + ×1.5 oak catch-up). Current state: leaf-pixel S 250-255 (effectively maxed).

### 5.3. Cross-pack PBR layering (Lesson H-18 PROMOTED)

**LOCKED RULE**: A texture_set.json MUST find its color PNG in the SAME PACK (or same directory). Bedrock doesn't do cross-pack atlas lookup for PBR companions.

This was discovered v1.2.6 — RP-03 (PBR pack) shipped 991 texture_set.json files but 676 referenced color PNGs that didn't exist in RP-03. Magenta rendering. Fix: copy 595 color PNGs from RP-04 / RP-09 into RP-03 to make it self-contained. RP-03 grew from ~50MB to ~117MB.

### 5.4. Sand sun-glint MERS (Lesson H-09 / §6.8)

**LOCKED PATTERN** (for sand-family textures with sun-glint):

| Channel | Sparkle pixel | Non-sparkle pixel | Meaning |
|---|---|---|---|
| R (metalness) | 128 | 0 | Sand is slightly metallic at sparkles, matte elsewhere |
| G (emissive) | 0 | 0 | NO emissive — would glow at all angles |
| B (roughness) | 12 | 240 | Sparkle = mirror-low; rest = max rough |
| A (subsurface) | 12 | 12 | Sand has minimal subsurface |

**Critical pairing**: sparkle pixel must be sun-aligned specular (R=128 + B=12), not emissive glow. v1.0.1 → v1.1.0 → v1.1.1 evolution:
- v1.0.1: G=240 + B=30 (emissive — wrong)
- v1.1.0: same pattern but tuned
- v1.1.1: switched to R=128 + B=12 (true specular — correct)

Sparkle density: ~1.2% of total pixels (785 of 65,536 in 256×256).

### 5.5. snow_layer rendering constraint (Lesson §6.13)

`minecraft:snow_layer` is a partial/thin block — geometry varies 1-8 layers. Render Dragon's partial-block path does NOT honor `variations` arrays even though schema allows them.

**Symptom**: terrain_texture.json defines `snow_layer` with `variations: [...]`. Engine renders only first entry, warns about rest unreachable.

**Fix**: define a separate single-texture shortname, override in blocks.json:
```json
// terrain_texture.json
"snow_layer_single": { "textures": "textures/blocks/snow_layer_v2" }

// blocks.json
"minecraft:snow_layer": { "textures": "snow_layer_single", "sound": "snow", "isotropic": {"up": true} }
```

**General rule**: any block with non-uniform geometry (snow_layer, candle, sea_pickle, vines, top_snow) cannot use `variations` arrays.

### 5.6. packed_ice texture binding (Lesson #126)

In RP-04-Basic blocks.json, `packed_ice` requires explicit `textures` field — won't auto-resolve from terrain_texture entries:
```json
"minecraft:packed_ice": {
  "textures": "packed_ice",
  "sound": "ice"
}
```

### 5.7. Variants need own PBR companions (Lesson H-19 CONFIRMED)

When a block has variations (`stone_v0..v7`, `dirt_v0..v15`, `sand_v0..v15`, etc.), each variation needs its own texture_set.json + normal + MER. v1.2.6 created 871 PBR companion files for variations (most pointing to base block's normal/MER).

### 5.8. Asset processing pipeline (Lesson #151 candidate)

PIL + numpy bulk pixel manipulation:
```python
from PIL import Image
import numpy as np
arr = np.array(Image.open(path).convert('RGBA'))
new_a = np.minimum(255, (arr[..., 3].astype(np.uint16) * 115 + 50) // 100).astype(np.uint8)
arr[..., 3] = new_a
Image.fromarray(arr, 'RGBA').save(path, 'PNG')
```

~28 sec for 54 textures. Pattern works for any per-pixel transformation across many similar textures.

---

## §6. CUSTOM WORLDGEN

### 6.1. Tree features (`minecraft:tree_feature`)

9 species × 4 tiers (young, mature, old, elder) = 36 base tree features. Plus `tree_feature_v2` variants and `with_branches` aggregates for elder species.

**LOCKED canopy rule** (Lesson §6.14): All `pw:*_tree_feature*` MUST use `fancy_canopy`. NEVER use `random_spread_canopy` (caused scattered ground-level leaves and missing canopy in v1.0.0/v1.1.1).

**Canopy size spec** (Lesson #69 — Android crash prevention):
- Elder MAX 5 blocks tall
- Spruce elder MAX 6 blocks tall
- Total leaf volume across 17 features ~1,111 blocks
- Never additive to vanilla

**Branches min_altitude_factor** (Lesson §6.15):

| Tree tier | branches.density | branches.min_altitude_factor |
|---|---|---|
| young | 0.0 | **1.0** |
| mature | 0.0 | **1.0** |
| old | 0.0 | **1.0** |
| elder | 0.4 | **0.3** |

Anti-pattern: density 0.0 paired with min_altitude_factor 0.4 — branches still appeared.

### 6.2. Branch features (v1.2.21)

8 branch species × 6 features each = 48 features:
- 4 single_block_features (cardinal directions)
- 1 weighted_random_feature picking random direction (25/25/25/25)
- 1 scatter_feature (3 iterations, 70% chance, X/Z extent ±1, Y extent 3-8)

5 elder species also have `pw_{sp}_with_branches_tree_feature.json` aggregate combining tree_feature_v2 + branch_scatter.

10 biome container files updated to reference with_branches variants.

### 6.3. feature_rules schema constraints (Lesson §6.6)

Valid `placement_pass` values (CLOSED enum):
- `surface_pass`
- `before_surface_pass`
- `after_surface_pass`
- `underground_pass`
- `pregeneration_pass`

INVALID: `tree_pass`, `forest_pass`, `decoration_pass`, or any custom name. Causes silent worldgen failure.

Valid `y` distribution forms:
```json
"y": 64
"y": {"distribution": "uniform", "extent": [60, 100]}
"y": {"distribution": "fixed_grid", "extent": [60, 100], "step_size": 4}
"y": {"distribution": "gaussian", "extent": [60, 100], "deviation": 5}
"y": {"distribution": "triangle", "extent": [60, 100]}
```

INVALID: `"y": "query.heightmap(x, z)"` — Bedrock's Molang heightmap takes NO arguments.

### 6.4. Sparse-tree variants (v1.1.1)

4 sparse-tree feature rules: `taiga_sparse_spruce`, `forest_sparse_oak`, `forest_sparse_birch`, `snowy_taiga_sparse_spruce`. Lower density than vanilla forests, gives a "natural clearing" feel.

### 6.5. weighted_random_feature schema

```json
{
  "format_version": "1.13.0",
  "minecraft:weighted_random_feature": {
    "description": { "identifier": "pw:my_random" },
    "features": [
      ["pw:option_a", 50],
      ["pw:option_b", 30],
      ["pw:option_c", 20]
    ]
  }
}
```

Schema is `[[id, weight], ...]` — array of pairs, NOT object with weight key.

### 6.6. Custom biomes (16 files)

Server biomes in BP-04. Client biomes in RP-02 (`client_biome/*.json`). Key custom biomes:
- pw:forest, pw:cherry, pw:coastal, pw:desert_dunes, pw:alpine, pw:pale, pw:river_canyon
- Plus auxiliary: pw:taiga, pw:jungle, pw:dark_forest, pw:swamp, etc.

`replace_biomes` configuration replaces vanilla biome with custom one. Without matching client_biome, falls back to vanilla colors (Lesson #149).

---

## §7. CUSTOM BLOCK AUTHORING

### 7.1. Block JSON structure (format_version 1.21.80)

```json
{
  "format_version": "1.21.80",
  "minecraft:block": {
    "description": {
      "identifier": "pw:oak_leaves",
      "states": {
        "pw:variant": {"values": {"min": 0, "max": 6}},
        "pw:rseed": [false, true],
        "pw:section": {"values": {"min": 0, "max": 2}},
        "pw:exposure": {"values": {"min": 0, "max": 1}},
        "pw:section_rolled": [false, true]
      }
    },
    "components": {
      "minecraft:custom_components": ["pw:randomize_variant"],
      "minecraft:material_instances": {
        "*": {
          "texture": "pw_oak_leaves_v0",
          "render_method": "alpha_test"  // LOCKED — never alpha_test_to_opaque
        }
      },
      "minecraft:light_dampening": 1,
      "tags": ["pw:foliage"]
    },
    "permutations": [
      // 7 permutations for variant 0..6, each with material instance for textures
      ...
    ]
  }
}
```

### 7.2. Permutation pattern (v1.0.1+)

`Permutations` array maps `pw:variant` value → texture override + geometry override. With 7 variants × 9 species = 63 leaf permutations.

### 7.3. Custom components (Lesson #150)

```js
// In BP-02 main.js startup hook:
world.beforeEvents.worldInitialize.subscribe((ev) => {
  ev.blockComponentRegistry.registerCustomComponent(
    "pw:randomize_variant",
    {
      onPlace(event) {
        const block = event.block;
        const rseed = block.permutation.getState("pw:rseed");
        if (rseed === true) return;  // already rolled
        // Pick variant from pool, write back
        ...
        block.setPermutation(block.permutation
          .withState("pw:variant", N)
          .withState("pw:rseed", true));
      }
    }
  );
});
```

**Lesson #150**: Block state declaration alone doesn't activate randomization. The `pw:randomize_variant` component must be declared explicitly on each block JSON's `components` (or in a permutation's `components`). Registering the handler in scripts only adds it to the registry — blocks must opt-in.

### 7.4. light_dampening (Lesson §6.17)

| Block type | light_dampening |
|---|---|
| Custom leaves | **1** (matches vanilla *_leaves) |
| Custom logs | 0 |
| Custom saplings/flowers | 0 |

Anti-pattern: light_dampening 7 on leaves → with multi-cube leaves stacked 3-5 deep, total dampening hit ≥ 15 = pitch-black canopies (Diagnostic from v1.1.1, fixed v1.1.2).

### 7.5. blocks.json (format_version 1.1.0 LOCKED)

In RP-04-Basic, blocks.json maps block IDs to terrain_texture shortnames. Special cases:
- `packed_ice` needs explicit `textures` field (Lesson #126)
- `snow_layer` needs single-texture binding (Lesson §6.13)

---

## §8. SCRIPT API DEPENDENCIES

### 8.1. @minecraft/server

| Pack | API version | Purpose |
|---|---|---|
| BP-01 (Atmospheric) | `"1.16.0"` | Lens flare entity-billboard |
| BP-02 (Tectonic) | `"2.0.0"` | BIGCANOPY + leaf cascade + scanners |
| BP-03 (Diagnostics) | `"2.0.0"` | Identification overlay |

**LOCKED RULE (Lesson H-53 / H-54 PROMOTED)**: When stamping manifests for a new version, NEVER touch `dependencies[].version` if `module_name` starts with `@minecraft/`. Those are API module versions (semantic strings like `"2.0.0"`), NOT pack versions. Distinguish by:
- If dep has `uuid` field → local pack reference, bump version (array)
- If dep has `module_name` field starting with `@minecraft/` → API module, leave version as-is (string)

This was learned the hard way in v1.2.15 (broke `@minecraft/server` from `"2.0.0"` → `[1, 2, 15]`, cascading to script crash + 14 BlockDescriptor errors). Fixed v1.2.16. Promoted to PROMOTED status because reproving cost a release cycle.

### 8.2. Scripting patterns used

- `world.beforeEvents.worldInitialize.subscribe` — register custom block components
- `world.afterEvents.playerBreakBlock.subscribe` — cascade trigger
- `world.afterEvents.explosion.subscribe` — cascade trigger
- `system.runInterval(fn, ticks)` — periodic scanners (60 / 100 / 200-tick intervals)
- `system.runTimeout(fn, ticks)` — delayed callbacks (mid-fall shedding, settling)
- `block.permutation.getState(name)` / `withState(name, value).setPermutation(...)` — state read/write
- `dimension.spawnEntity(typeId, location)` — entity spawning
- `dimension.runCommand(cmd)` — fallback for setblock destroy

### 8.3. Performance budgeting

Per-tick caps for scanners:
| Scanner | Cap | Interval | Effective rate |
|---|---|---|---|
| Section flag scanner | 120 flags/tick | 100 ticks (5s) | 1200 flags / 5s per player |
| Variant scanner | 50 rolls/tick | 100 ticks (5s) | 500 rolls / 5s per player |
| Cascade flush | 50 cascades/tick | 4 ticks (200ms) | 12,500 cascades / 5s |
| BIGCANOPY leaf scan | 40 leaves/tick | 60 ticks (3s) | 2400 leaves / 3s per player |
| Decay scanner | ~50-100 leaves/scan | 200 ticks (10s) | bounded by foundation |

---

## §9. AUDIO + PARTICLES (PRESENT STATE + DORMANT)

### 9.1. Active sound events (v1.2.21)

`RP-01-.../sounds/sound_definitions.json` registers 8 active events:
- `pw.tree_fall.{small, medium, big, generic}` — 4 events, 8 .ogg files
- `pw.tree_impact.{small, medium, big, generic}` — 4 events, 6 .ogg files

Total 14 .ogg files in RP-01/sounds/tree/.

### 9.2. Dormant ambient events (122 — backlogged)

122 `pw:ambient.*` sound events declared but NOT wired (no triggering logic). Queued for AmbientSounds 6.3.5 port.

### 9.3. Active particles

- `pw:leaf_fall` — used in BIGCANOPY mid-fall shedding + falling-tree arc
- `pw:leaf_litter` (entity, not particle) — spawned during/after tree fall
- 4 lens flare particles (anamorphic, ghost ring, sun ray, sun corona) — spawned by BP-01 lens flare

---

## §10. BUILD PIPELINE + VERIFICATION

### 10.1. Standard build sequence

```
1. cp -r /home/claude/build/v<prev>/ /home/claude/build/v<new>/
2. Apply changes (str_replace, file edits)
3. Stamp manifests via stamp_v<X_Y_Z>.py:
   - header.version → [X, Y, Z]
   - modules[].version → [X, Y, Z]
   - dependencies[].version → [X, Y, Z] ONLY IF dep has uuid (not module_name)
   - Preserve all @minecraft/* string deps (Lesson #53 / H-53)
4. Build deliverables via build_deliverables.py:
   - Per-pack mcpack (zip with DEFLATED)
   - MAIN.mcaddon (12 nested mcpacks)
   - ATMOSPHERIC.mcaddon (2 nested mcpacks)
   - RP-04-Basic.mcpack (standalone)
   - RP-07-Neutral-Mobs.mcpack (standalone)
   - MD5SUMS.txt
5. Run verification suite (V1...V49+ checks)
6. Write README + FOUNDATION_PATCH + HANDOFF
7. Present files
```

### 10.2. Verification checklist (~49 checks as of v1.2.31)

| Check | Description |
|---|---|
| V1 | 16 manifests at correct version |
| V2 | @minecraft/* string deps preserved |
| V3 | 17 trunk types × 595 perms |
| V4 | packed_ice has textures field |
| V5 | Standing dodecagon chord-flush |
| V6 | Falling chord-flush 792/792 panels |
| V7 | 9/9 leaves with 5 storage states + 7 variants + 7 perms |
| V8 | Cube count signature [8,10,9,8,5,9,7] |
| V9 | All 63 leaf perms alpha_test |
| V10 | Cascade tokens present (queue, flush, budget, event subs, init log) |
| V11 | Scanner architecture preserved |
| V12 | 8 branches + 14 .ogg + 8 sound events |
| V13-V14 | log_top material instances + falling end-grain UVs |
| V15 | 168 implicit perms per leaf |
| V20-V21 | v1.2.29 architecture preserved (UP=35, DOWN=4, variant_3 8-corner-puff) |
| V30-V32 | v1.2.30 polish preserved (flipbook variance, mid-fall shed, settling bounce) |
| V41-V47 | v1.2.31 NEW (bottom-up sweep, smart early-exit, threshold raise, v0 directional, MERS bump) |
| V48 | Deliverable zip integrity (mcpack contents) |
| V49 | MD5 manifest match + zip-of-zips + JS parse + shipped-matches-build |

### 10.3. Failure modes / regression prevention

**Lesson #77** is the canonical reminder: **JSON parse OK ≠ runtime registration OK**. The verification suite checks parse + cross-references, but doesn't actually run the engine. User in-game testing is the runtime validation.

Particularly for VV: the engine silently rejects invalid format_versions. A pack can ship with format_version 1.21.90 atmospherics, parse cleanly, and produce ZERO `[ContentLog]` errors at world load — yet not register the atmospherics at all. Always cross-reference Microsoft Learn for the locked schema.

### 10.4. Manifest diff gate (Lesson H-54 PROMOTED)

After any manifest-stamping pass, build script must diff each pack's manifest against the previous version's:
- Acceptable diff: header.version, modules[].version, dependencies[].version (UUID-deps only)
- FAIL the build if diff touches: module_name, uuid, dependencies[].module_name, dependencies[].uuid, capabilities, min_engine_version, metadata, @minecraft/* dep versions

This rule is the structural fix for the v1.2.15 disaster. Until implemented as automation, manual review of stamped manifests is the safety net.

---

## §11. END OF ARCHITECTURE DOCUMENT

For locked invariants and lessons library, see `ABSOLUTREALISM-FOUNDATION-v1_2_31.md`.

For per-version changelog and queued work, see `ABSOLUTREALISM-HISTORY-AND-BACKLOG-v1_2_31.md`.

For known unresolved diagnostic issues, see `ABSOLUTREALISM-DIAGNOSTICS-v1_2_31.md`.

*Document authored 2026-05-10 as part of the master-doc consolidation. Supersedes all prior architecture/research/research-report documents through v1.2.31.*

---

## §V. Mob conversion architecture (v1.3.35 patches 1-8)

This section documents the architecture specific to the mob conversion phase.

### V.1. RP-07 pack structure

```
RP-07-AbsolutRealism-Neutral-Mobs-RP/
├── manifest.json                        # Pack manifest (linked to BP)
├── pack_icon.png
├── animations/
│   ├── ar_pig.animation.json            # AR-authored procedural animations
│   ├── ar_cow.animation.json
│   ├── ... (31 ar_*.animation.json files for 33 mobs)
│   ├── pw_animation_shims.animation.json # Patrix wrapper shims (preserved)
│   └── pw_wolf.animation.json            # Patrix wolf-specific (preserved)
├── entity/
│   ├── pig.entity.json                  # 33 client_entity files
│   ├── cow.entity.json
│   └── ... (all neutral mobs)
├── models/
│   └── entity/
│       ├── pig.geo.json                 # Custom geometries from JEM conversion
│       ├── cow.geo.json
│       └── ... (33 geo files)
├── render_controllers/
│   ├── pw_pig.render.json               # Render controllers (Patrix-derived)
│   └── ... (all mobs)
└── textures/
    └── entity/
        ├── pig/                          # Texture sets per mob
        │   ├── pig.png                   # Main color/diffuse
        │   ├── pig_n.png                 # Normal map
        │   └── pig_s.png                 # Specular (LabPBR convention) — converted to MERS in production builds
        └── ...
```

### V.2. Animation registration flow

Each entity has:
1. `animations` map: alias → animation ID
   ```json
   "animations": {
     "setup": "animation.quadruped.setup",
     "look_at_target": "animation.common.look_at_target",
     "ar_walk": "animation.ar_pig.walk",
     "ar_idle": "animation.ar_pig.idle"
   }
   ```
2. `scripts.animate` list: triggers with conditional weights
   ```json
   "animate": [
     "setup",
     "look_at_target",
     {"ar_walk": "math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"},
     {"ar_idle": "1.0 - math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"}
   ]
   ```

The animation files (in `animations/`) define the actual bone transforms using Molang expressions.

### V.3. Animation file structure (procedural pattern)

```json
{
  "format_version": "1.8.0",
  "animations": {
    "animation.ar_<mob>.walk": {
      "loop": true,
      "animation_length": <seconds>,
      "bones": {
        "leg0": {
          "rotation": ["math.cos(query.modified_distance_moved * FREQ) * AMP * THRESHOLD", 0, 0]
        },
        "leg1": {
          "rotation": ["math.cos(query.modified_distance_moved * FREQ + 180.0) * AMP * THRESHOLD", 0, 0]
        },
        ...
      }
    },
    "animation.ar_<mob>.idle": {
      "loop": true,
      "animation_length": <seconds>,
      "bones": {
        "body": {"position": [0, "math.cos(query.life_time * BFREQ) * BAMP", 0]},
        "head2": {"rotation": [
          "math.sin(query.life_time * HFREQ_X) * HAMP_X",
          "math.sin(query.life_time * HFREQ_Y) * HAMP_Y",
          0
        ]}
      }
    }
  }
}
```

THRESHOLD is the activation threshold: `math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)` (Lesson #203).

### V.4. Geometry file structure (custom mob geo)

```json
{
  "format_version": "1.12.0",
  "minecraft:geometry": [
    {
      "description": {
        "identifier": "geometry.<mob>.patrix",
        "texture_width": 64,
        "texture_height": 64,
        "visible_bounds_width": 2,
        "visible_bounds_height": 2,
        "visible_bounds_offset": [0, 1, 0]
      },
      "bones": [
        {
          "name": "body",
          "pivot": [0, 12, 0],
          "rotation": [0, 0, 0]
        },
        {
          "name": "body_cube",
          "parent": "body",
          "pivot": [0, 12, 0],
          "cubes": [
            {
              "origin": [-3, 11, -5],
              "size": [6, 8, 14],
              "uv": {
                "north": {"uv": [10, 20], "uv_size": [6, 8]},
                "south": {"uv": [30, 20], "uv_size": [6, 8]},
                "east":  {"uv": [0, 20],  "uv_size": [10, 8]},
                "west":  {"uv": [16, 20], "uv_size": [10, 8]},
                "up":    {"uv": [10, 12], "uv_size": [-6, -10]},
                "down":  {"uv": [16, 12], "uv_size": [-6, 10]}
              }
            }
          ]
        },
        ...
      ]
    }
  ]
}
```

### V.5. Mob taxonomy and bone hierarchies

#### Tier 1: simple quadrupeds + biped chicken

| Mob | Bones | Special features |
|---|---|---|
| pig | head/body/head2/snout/ears/leg0..3 | Snout sub-bone for nose detail |
| cow | head/body/head2/snout/horns/ears/neck/udder/leg0..3 | Horns, neck, udder |
| mooshroom | (same as cow) | Cow skeleton; mushroom decoration in body_cube |
| sheep | head/body/body_cube/head2/snout/ears/leg0..3 | body_cube has `rotation: [90, 0, 0]` (lays cube flat) |
| chicken | head/body/head2/comb/wattle/body_cube/neck/wings/tail/leg0..1 | Biped, comb/wattle/tail decorations |
| cold_chicken | (same as chicken) | Variant texture |
| warm_chicken | (same as chicken) | Variant texture |
| rabbit | root/body/head/head_main/nose/ears/leg0..3/leg2_foot/leg3_foot | Has explicit root bone, segmented hind feet |

#### Tier 2: multi-state mobs

| Mob | Bones | Special features |
|---|---|---|
| cat | head/body/tail/tail2/body_cube/head2/ears/tail3/tail4/front_left_leg/front_right_leg/back_left_leg/back_right_leg | NON-standard leg naming; segmented tail |
| ocelot | (same as cat) | Identical skeleton to cat; geo 1.4x scaled in Patch 7 (Lesson #202) |
| wolf | head/body/body_cube/mane/head2/ears/snout/tail/leg0..3 | Mane bone, segmented tail |
| fox | head/body/body_cube/head2/snout/ears/tail/leg0..3 | Standard skeleton |
| panda | body/body_cube/head/ears/leg0..3 | Simplified hierarchy; head as direct body child |
| polar_bear | head/body/body_cube/head2/bone/leg0..3 | Standard quadruped |

#### Tier 3: large quadrupeds

| Mob | Bones | Special features |
|---|---|---|
| horse | head/body/body_cube/neck/head2/snout/ears/mane_top/mane/tail/leg0..3 | Tilted neck (30° forward), mane re-parented to head2 in Patch 7 |
| donkey | (horse + right_chest/left_chest) | Same as horse + saddle chests |
| mule | (donkey skeleton) | Same as donkey |
| llama | head/body/body_cube/head2/snout/ears/leg0..3 | Standard quadruped |
| trader_llama | (same as llama) | Variant; uses trader_llama_decor for decoration |
| camel | head/body/head2/ears/body_cube/hump/tail/leg0..3 | Hump bone |
| goat | body/coat/head/head2/nose2/horns/ears/leg0..3/leg0_lower..leg3_lower/beard_right/beard_under/beard_left | Coat sub-bone, segmented legs, horns, beard chain |

#### Tier 4: aquatic + flying

| Mob | Bones | Special features |
|---|---|---|
| dolphin | body/body2/head/top_fin/right_fin/left_fin/tail/tail3/tail_fin | Per-cube `[0,0,180]` rotation applied in Patch 8 |
| turtle | body/head/right_front_leg/left_front_leg/right_back_leg/left_back_leg/egg_belly/tail | Same per-cube rotation as dolphin |
| cod | body/body2/head/left_fin/right_fin/fin_back2/body3/tail/right_fin_b/left_fin_b | Segmented body, multiple fin pairs |
| salmon | body_front/body/head/left_fin/right_fin/left_fin_b/right_fin_b/fin_top/body3/tail | Similar to cod with front-body extension |
| tropical_fish_a | body/body2/bone/left_fin/right_fin/left_bottom_fin/right_bottom_fin/fin_top2/fin_bottom/tail | A variant |
| tropical_fish_b | body/body2/bone/right_fin0/left_fin0/fin_top2/fin_bottom2/tail/right_fin/left_fin/left_bottom_fin/right_bottom_fin | B variant; more fin bones |
| tropical_fish_pattern_a | (same as tropical_fish_a) | Different texture |
| tropical_fish_pattern_b | (same as tropical_fish_b) | Different texture |
| pufferfish_large | body/body2/spike sets (8)/left_fin/right_fin/bone/bone2/tail | Multiple spike bones |
| pufferfish_medium | body/body2/spike sets (8)/tail/left_fin/right_fin/bone/bone2 | Smaller spikes |
| pufferfish_small | body/body2/tail/tail3/left_fin/right_fin/bone/bone2 | Deflated, no spikes |
| axolotl | body/head/bone/top_fern/left_fern/left_fern2/right_fern/right_fern2/body2/legs (4)/tail2/back_fin/leg5..leg13 | Ferns/gills; many leg bones for variants |
| parrot | head/body/body_main/head_main/beak/feathers/wings (left/right)/tail/leg stubs+feet | Decorative cubes consolidated to wings in Patches 7-8 |
| frog | body/body_main/head/head_main/eyes/right_arm/right_hand/left_arm/left_hand/right_leg/right_foot/left_leg/left_foot | Body has `[0, 45, 0]` rotation (diamond from above); limbs in body-local diamond coords |

### V.6. Patch script architecture

Each iteration is a Python script `patch{N}_apply.py` that:
1. Loads each mob's `.geo.json` file
2. Applies specific edits (cube origin changes, UV updates, rotation adds)
3. Saves the file
4. Validates JSON integrity

Scripts include helper functions:
- `load(p)` / `save(p, data)` — JSON I/O
- `find_bone(geo, name)` — locate bone by name in geometry
- `flip_y_uvs(uv_dict)` — self-inverse Y-axis UV transform (used in Patch 7 and undone in Patch 8)

Scripts are versioned by patch number and stored in `/home/claude/_research/v1_3_35_jem_methodology/`.

### V.7. Build pipeline

```bash
# 1. Apply patch
python3 patch{N}_apply.py

# 2. Validate
# (script-internal JSON validation)

# 3. Package
cd _build/v1_3_35_rp07/ && \
zip -r -q -X /_deliverables/RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_3_35.mcpack . -x "*.bak"

# 4. MD5 documentation
md5sum *.mcpack > MD5SUMS.txt

# 5. README
# (manual: write PATCH{N}-README.md describing changes)

# 6. Stage to output
cp *.mcpack *.md /mnt/user-data/outputs/

# 7. Present
# (Python: call present_files tool)
```

### V.8. Animation activation pattern (post-Lesson #203)

All walk animations use the threshold pattern:
```
* math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)
```

This replaces the older `* query.modified_move_speed` pattern that produced invisible animations at slow speeds.

Standard idle trigger:
```json
{"ar_idle": "1.0 - math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"}
```

Walk and idle are mutually exclusive (sum to 1.0 always).

Special cases:
- **Parrot fly**: `1.0 - query.is_on_ground` (triggers when airborne)
- **Cod/salmon flop**: `1.0 - query.is_in_water` (triggers when out of water)
- **Turtle walk**: `(1.0 - query.is_in_water) * math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)` (combination)

---

*End of v3 mob conversion architecture appendix.*
