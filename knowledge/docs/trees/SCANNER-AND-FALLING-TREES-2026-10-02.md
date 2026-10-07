# SCANNER-AND-FALLING-TREES — what goes when trees come from our structures, what it saves, and how felling becomes exact

- Date: 2026-10-02 · Build read: `/home/claude/_build/bp02-205` (BP-02 v1.3.205, `@minecraft/server` 2.3.0). The scripts are `scripts/*.js`: `main.js` is 5,200 lines / 262,945 B, and all 13 files total 375,157 B.
- Origin of the questions: his D-C460 list (14:13), which asked about removing the scanner, the memory saved, falling trees with structures, and whether structure-tree leaves are final.
- Method: a read-only static analysis. No BDS run (the server is in use by another job) and no file changed except this report.
- **Evidence tags used below:**
  - **[CODE]** read directly from code (file:line).
  - **[CALC]** computed with Python from the code's own constants.
  - **[EST]** an estimate. The assumption is stated next to it.
- Per the witness rule and P1, nothing here is witnessed. Every claim about runtime behaviour is a hypothesis until a BDS probe or his hardware confirms it. §7 lists the probes.
- Journal context used:
  - D-C265 / census (line 1450): leaf state space and the permutation budget.
  - D-C321 / D-C322: v0 far cube; his long-term vision "ditch the leaf scanner entirely".
  - D-C328: his design intent — an engine far swap, and trees as structures with every variant pre-placed.
  - D-C329: "the scanner was SUPPOSED to stop rerolling with a permanent flag"; "structure phase will remove the scanner".
  - D-C333: his 15:59 felling request.
  - D-C335 / D-C339: J1/J2/J3 plan. Structure-known trunk/branch sets make felling exact.
  - D-C342: **L-FAR-1** SUPERSEDES L9. `alpha_test_to_opaque` switches far blocks to opaque by itself, and worldgen places default permutations only.
  - D-C343 / D-C345: leaf look, picked once by position plus distance to wood.
  - D-C350: v1.3.198.
  - D-C459: `world.structureManager` get/place/getBlockPermutation BDS-verified on 2.3.0. Rotate90 maps (x,z) → (sz−1−z, x). Rotation turns vanilla and trait states, NOT custom states.
  - D-C460: the questions themselves.

---

## 0 · Bottom line

1. **What we can remove (Q1):** with every tree placed from our structures with final leaves, the whole leaf scanner goes. That is Process A, phase-1, the verify script, the far reverter, the re-applicator, the cascade, the heartbeat, the diagnostics and the stats (≈ 55 KB of `main.js`).
   - **Leaf decay** stops being a periodic sweep and becomes event-driven.
   - **Already dead or no-op today**, even without structures:
     - the far reverter and re-applicator (their registry is never written);
     - the verify script (it only counts);
     - the classify pass's section/exposure flags (nothing renders them);
     - decay's exposure re-check (resets are switched off).
   - **Still needed in some form:**
     - **old chunks:** the leaves and logs already generated there;
     - **player-placed leaves:** the `onPlace` component stays;
     - **sapling growth:** TREEGROW stays and gets upgraded;
     - **leaf-litter lifecycle and ambient leaf drift:** both stay;
     - **vines and planks:** both stay, for other block sources.
   - **The far swap needs nothing:** it is engine-native per L-FAR-1. All 98 render permutations of a leaf are `alpha_test_to_opaque` [CODE `blocks/oak_leaves.json`].
2. **What we save (Q2):** the big win is CPU, not RAM.
   - **CPU:** the two always-on jobs ask for about 690,000 `getBlock` calls per second per player at their nominal cadence. That is more than any time slice can supply, so they consume the whole `runJob` slice continuously (Process A 710,781 cells per sweep every 30 t; phase-1 215,883 every 22 t) [CALC].
   - **Resident script heap:** about 1.0–1.6 MB [EST], plus 55–75 KB of source.
   - **Dynamic properties: 0 B.** The scanner stores none; its persistence is block states.
   - **Block permutations: −12,397 of BP-02's 30,104 (−41 %)**, if the four bookkeeping leaf states are dropped [CALC]. This needs a save-migration probe first.
   - **World writes:** 2 `setPermutation` per worldgen leaf on first contact, plus cascade rewrites. Every one of them dirties a chunk; all of them disappear.
3. **How felling improves (Q3):** a structure-placed tree can carry its own identity.
   - A **root block** at the trunk base holds the template index in a custom state. A rotation-carrying **trait** holds the rotation (traits ARE turned by structure rotation, D-C459).
   - At break time the script walks down the trunk to the root (≤ 32 reads) and reads the template straight from the `.mcstructure` via `world.structureManager.get(id).getBlockPermutation()`. It then knows the exact trunk, branch and leaf cells.
   - That replaces:
     - the 26-neighbour log BFS;
     - the leaf-adjacency heuristic;
     - the rooted-column "other tree" heuristic;
     - the canopy rays;
     - the vine grid;
     - the 40,000-cell orphan-leaf AABB scan.
   - Cost per fell drops from about 13.7K (mature oak) and about 47K (elder) world reads to about 0.5–3K [EST].
   - With 15 identity rules (§6.2), **a player-placed log can never fell anything:**
     - in survival every player log is vanilla, because logs drop vanilla items, and vanilla logs carry no root identity;
     - creative-placed pw logs are flagged on `playerPlaceBlock`;
     - and a log must be a trunk cell of a decoded template.

---

## 1 · Inventory — every periodic or bulk job in BP-02 (all 13 script files)

Abbreviations:
- **t** = game tick (20 t = 1 s).
- **gB** = `dim.getBlock` call.
- **sP** = `setPermutation`/`setType` write.

"Per pass" is per online player unless the row says otherwise.

### 1A · Leaf scanner family (`main.js`) — the "scanner"

| # | Job | Lines | What it does | Cadence | Volume / pass | Caps | State it keeps | After structure trees with final leaves |
|---|---|---|---|---|---|---|---|---|
| S1 | **Process A — trunk association** (`_treeAssociationJob`, runJob) | 2953–3011 (walk 2894–2943) | Walks every cell near-first. At each **log cell** (not each tree) it walks up to the top log (≤ 32 gB), finds an adjacent leaf (6 gB; if none, a tolerant ring search of ≤ 400 gB, v1.3.147 oak fix). If that leaf is unrolled, it marks it and BFS-floods the canopy (`_treeCompletionBFS`) | `runInterval` 30 t; guarded single job, re-kicked as soon as one ends | **710,781 cells** (±35 xz × ±70 y) [CALC], + per-log walks | 400 cells or 8 ms per yield; walk deadline 40 ms; **trees per cycle 3, ×3 = 9 while the SlabForge key is out** (2976, the default state); BFS 300 marks / 1,500 visited | `_taStats` counters; per-job typed shell buffers 612 KiB (§2) | **REMOVE.** Its only purpose is classifying leaves fast. Final leaves need no classification. Felling does not read it. |
| S2 | **Phase-1 classify + look** (`_phase1ScanJob`) | 3024–3119 | Near-first walk over leaf cells. If `pw:section_rolled` is false: `_markLeaf` → `detectSectionAndExposure` (≤ 64 vertical gB + 6) + 1 sP. Then if `pw:rseed` is false: `pwLeafLook` (≤ 62 gB at band 3, ≤ 128 at band 4) + 1 sP | 22 t, guarded | **215,883 gB** (±25 xz, y −40..+42) [CALC] | 400 cells or 8 ms per yield; no per-cycle mark cap | `_scanStats`; typed buffers 275 KiB | **REMOVE.** Final leaves already carry `pw:variant` and `pw:off`. Old chunks: see §3 row "legacy leaves". |
| S3 | Far reverter | 3167–3197 | Walks `_appliedRegistry` and sets far leaves to v0 | 39 t | registry size | 300 per cycle | `_appliedRegistry` (cap 30,000) | **REMOVE — already dead.** `_appliedRegistry` has **no `.set()` anywhere** (only `.delete`/`.size`, lines 3186–3224) [CODE], so it returns at line 3168 every time. The far swap is engine-native (L-FAR-1). |
| S4 | Re-applicator (HOTFIX-2) | 3202–3233 | Restores variants on dormant registry entries | 17 t | registry size | 300 | same registry | **REMOVE — already dead** (same reason). |
| S5 | Cascade flush | 3312–3342 | For each queued broken position: 6 gB, and resets neighbour leaves to `section_rolled=false, rseed=false` (≤ 6 sP). S2 then re-marks and re-looks them (≤ 12 more sP) | 4 t, only while queued | 6 per key | 50 keys / 4 t | `_pendingCascades` Set (strings) | **REMOVE** the periodic part. Keep one event-driven "re-look the leaves within band of a broken log once" (v1.3.197 intent: cards touching vanished wood should become full shapes) — §3. The fell's `removeOne` calls `_enqueueCascade` (774), so drop that call. |
| S6 | Break trigger | 3260–3272 | Any broken pw leaf or wood → enqueue cascade + `_forceKickScanner` (only clears the guard, 3246–3258) | event `playerBreakBlock` | 1 | — | — | REMOVE (folded into the event re-look above) |
| S7 | Explosion trigger | 3275–3283 | Enqueue a cascade for every impacted block | event `explosion` | n blocks | — | — | REMOVE (or event re-look; see S5) |
| S8 | Spawn / join / dimension-change kicks | 3286–3307 | Kick Process A | events | — | — | — | REMOVE |
| S9 | Heartbeat | 3348–3363 | If S2 is stale for > 300 t, force-kick (guard clear) | 600 t | — | — | — | REMOVE |
| S10 | Diagnostics chat ping | 3366–3385 | Disabled (`PW_DIAGNOSTICS_ENABLED=false`, 2563) | 400 t | 0 | — | — | REMOVE |
| S11 | **Verification script** (runJob) | 3408–3483 | Re-reads 6 overlapping layers ±30 and **only counts** "stranded" leaves. Re-enqueue was removed in v1.3.36 (3442–3444) | 200 t, guarded | **178,608 gB** (6 layers × 8 rows × 61²) [CALC] | 250 cells or 8 ms per yield; 500 cap (never reached: nothing increments `reEnqueued`) | `_verifyStats` | **REMOVE — a no-op today**: it does 179K reads to update a counter. |
| S12 | Stats logger + `pw:stats` | 3497–3529 | `[BIGCANOPY-STATS]` line | 1,200 t (idle heartbeat 6,000 t) | string build | — | counters | REMOVE (scanner-only content) |
| S13 | Diagnostic scriptevents `pw:variant_audit`, `pw:diag_status`, `pw:variant_dump` | 3939–4074 | On-demand ±32 cube dumps (274,625 gB each) | on demand | 274,625 | — | — | OPTIONAL remove (7.0 KB). **Keep the `pw:forge_beat` handler, which lives inside the `variant_audit` subscriber at line 3940** (move it out first). TestRunner phases p1/p2/p3/p15 reference these ids/states (grep hit) and need edits. |

### 1B · Tree lifecycle jobs (`main.js`)

| # | Job | Lines | What | Cadence | Volume | Caps | State | After structure trees |
|---|---|---|---|---|---|---|---|---|
| T1 | **Leaf decay sweep** (runJob) | 3762–3850 (helpers 3630–3755) | Box ±10 xz × ±8 y. For each pw leaf: `reValidateExposure` (6 gB; **its write is disabled**, `PW_EXPOSURE_RESETS=false`, 3629/3676 → pure reads). If not verified within 600 t: BFS to a log (≤ 50 iterations × 6 = ≤ 300 gB, distance ≤ 6). Orphans → `pw:leaf_litter` + air | 200 t, guarded | **7,497 cells** [CALC] + 6/leaf + ≤ 300 per unverified leaf | 8 decays per cycle; early exit after 1,000 cells with no leaf | `_decayLastVerified` Map, cleanup only when > 5,000 (drops entries > 1,200 t old) | **REPLACE with event-driven decay** (on a log break that does not fell, and on explosions). Structure trees know which leaves hang from which branch, so that is exact. A periodic sweep is only justified if he wants decay after fire burns logs (no event exists for that). |
| T2 | Leaf-litter lifecycle | 3867–3922 | `getEntities(pw:leaf_litter)` in 3 dimensions: landing check, then despawn at 200 t on the ground / 600 t max | 20 t | n litter | — | entity properties | KEEP (litter still comes from fells and decay). Could early-return when no litter exists (tiny). |
| T3 | Boot orphan sweep | 229–237 | Removes leftover `ft:falling_tree` / `pw:leaf_litter` | once at 40 t | — | — | — | KEEP |
| T4 | **Fell handler** (event) | 1212–1899 | See §5. Per fell: `system.run` + 1 t clear + `cleanOrphanLeavesJob` (633–807, runJob, AABB ≤ 40,000 gB) + 1 t pin interval (1642–1733, ≤ trunkH gB per tick for ~95 t) + 1 t sweep interval (791–802) + ~11 timeouts | per log break | §5 | MAX_LOGS 200, MAX_LEAVES 260, sweep 40/t | transient | **UPGRADE** (§6). Note: `log("broke …")` runs `console.log` on **every** block any player breaks (1219, 45), even with DEBUG=false. |
| T5 | **TREEGROW** sapling → structure | 4915–4943, 5048–5110 | `playerPlaceBlock` on a sapling → `_growRegistry`. Every 40 t, due entries (2,400 + ≤ 1,200 t) are checked for ground and a 5×5×6 clearance (150 gB), then `structure load "pw:test_<sp>_young"` | 40 t; cap reset 12,000 t | pending saplings only | 6 per chunk | `_growRegistry`, `_growChunkCount` (memory only, lost on reload) | **KEEP + UPGRADE** (§6.6). P11 audit: the 9 pool ids `pw:test_<sp>_young` exist in NONE of the censused spaces (BP-02 205 `structures/pw/` CENSUSED: 9 files, all CIVITAS/roof; all 255 `_build/*` folders CENSUSED by `find`: none). His **world-DB saved templates are NOT CENSUSED** (unreadable from here). So unless he saved those names in-world, every growth logs `pool_miss`. Static finding; needs his witness. |
| T6 | Ambient leaf drift | 5170–5200 | 26 random columns × ≤ 15 gB → ≤ 4 `pw:leaf_drift` particles per player | 40 t | ≤ 390 gB | 4 emits | — | KEEP (ambient; tree origin is irrelevant) |

### 1C · Other periodic jobs (not tree-related — listed for completeness, all KEEP)

| Job | File:lines | Cadence | Work per pass |
|---|---|---|---|
| Held-torch light | main.js 2001–2009 | 20 t | movement-gated, 1 gB + ≤ 2 sP per moved player |
| Firefly ambient | main.js 4147–4153 | 30 t | night/biome check, 2 particles |
| Milky Way band | main.js 4227–4246 | 900 t (+ once at 100 t) | ≤ 80 particles at night |
| Golden-crown aura | main.js 4269–4307 | 4 t | equipment read, effect, ≤ 1 light block |
| SLABSMOOTH (+ lip job, audit) | main.js 4872–4911 | 20 t; **dormant unless the SlabForge key-pack heartbeats** (4876) | spiral r20, ±3 y, 350 cells per yield, 160 places per cycle |
| Snow accumulation | main.js 4969–5021 | 100 t | 4 × 24 columns × ≤ 13 gB per player |
| Vine swap (`getBlocks` includeTypes) | pw_vine.js 42–72 | 100 t | 48 engine-filtered `getBlocks` calls (49×49×33 = 79,233 cells) [CALC], 64 swaps per yield |
| Vine rustle / climb | pw_vine.js 98–105 / 119–134 | 10 t / 2 t | rustle map; 2 gB per player (+ 36 when inside a vine) |
| Plank grid swap | pw_planks.js 118–168 | 100 t | same 48 engine-filtered calls |
| Homestead hearth / puff / chute / rafter | pw_homestead.js 610–613 | 40 t / 4 t / **1 t** / 10 t | ledger walk; particles; 1–2 gB per player |
| Mob light | pw_mob_light.js 112 | 4 t | `getEntities` r48 per player, ≤ 256 lights |
| Fowl flutter | pw_flutter.js 23–46 | 2 t | `getEntities` × 6 types × 3 dimensions |
| Seat cleanup | pw_furniture.js 50–60 | 20 t | `getEntities(pw:seat)` × 3 dimensions |
| Place hooks (ramp lattice, seated stairs, furniture, companion, vine, plank, sapling) | main.js 4946, 5035, 5048; pw_*.js | events | O(1) each |

---

## 2 · Persistent and in-memory state of the scanner

**Dynamic properties.** The tree scanner, decay and felling write **none** [CODE: every `DynamicProperty` call in BP-02 is listed below]. **Saving from them = 0 B.**

| Key | Owner | Size bound | Tree-related? |
|---|---|---|---|
| `pw:slab_deny`, `pw:slab_done`, `pw:slab_editcols` | SLABSMOOTH (main.js 4428–4485) | ≤ 20,000 chars each (`PW_SLAB_PROP_CAP`) | no |
| `pw:mob_lights` | pw_mob_light.js 20/62 | JSON of ≤ 256 records | no |
| hearth ledger index + entries | pw_homestead.js 74–90 | per hearth | no |
| weather cache | pw_weather.js 37/53 | per dimension | no |
| riser-convert flag | pw_ground.js 79/255 | bool | no |

**Block states — where the scanner's persistence really lives.** Leaf blocks carry `pw:variant`(7) × `pw:rseed`(2) × `pw:section`(3) × `pw:exposure`(2) × `pw:section_rolled`(2) × `pw:off`(7) = **1,176 permutations each × 11 leaf blocks = 12,936** [CALC from `blocks/*_leaves.json`].
- **Only `pw:variant` and `pw:off` drive geometry:** 539 conditions, all `q.block_state('pw:variant')` / `'pw:off'` [CODE grep].
- The other four states are script bookkeeping and multiply the permutation count ×24.
- BP-02's total is **30,104** permutations [CALC, same method as `tools/block_state_census.py`], so leaves are 43 % of it.
- The 65,536-permutation warning history is in D-C265 / census.

**In-memory structures (QuickJS heap):**

| Structure | Lines | Bound | Bytes |
|---|---|---|---|
| Process A typed shell buffers (`Int16Array`×3 + `Uint32Array`) | 2362–2370 | 62,658 entries × 10 B | **612 KiB** [CALC], allocated at every job start; the job is near-continuous, so effectively resident |
| Phase-1 typed shell buffers | same | 28,178 × 10 B | **275 KiB** [CALC] |
| Shell index arrays (`new Array(n)`, sorted per shell) | 2426–2428 | largest shell 29,402 (A) / 15,002 (P1) | ≤ 459 KiB + 234 KiB transient [EST 16 B per JSValue]; **garbage per sweep 11.4 MB (A) + 3.5 MB (P1)** [EST, 710,781 / 221,085 entries] |
| Block wrapper objects from `getBlock` | everywhere | ~927K per A+P1 sweep pair, + verify 179K per 10 s | churn, not resident; bytes per wrapper unknown |
| `_treeCompletionBFS` visited Set | 2733 | ≤ 1,500 string keys | ~100–150 KiB transient [EST] |
| `_decayLastVerified` Map | 3611 | soft cap ~5,000 (cleanup at > 5,000, 3843) | ~0.5 MB [EST ~100 B per string-keyed entry] |
| `_appliedRegistry` Map | 2870 | cap 30,000, **never written** | 0 today |
| `_pendingCascades` Set | 3238 | bursts ≤ 260 per fell (one per removed leaf) | transient |
| `_leafScanLastPos/_Cooldown` | 2488–2489 | per player | trivial |

---

## 3 · Q1 verdict — what can go, and what still needs covering

| Part | Verdict | Why / what still covers it |
|---|---|---|
| S1 Process A, S2 phase-1, S9 heartbeat, S10 diag, S11 verify, S12 stats, S6–S8 triggers, the offset iterator (2316–2473), the section/BFS/layered helpers (2626–2835) | **Remove** | Structure leaves are placed final (`pw:variant` + `pw:off` baked; the look is never recomputed). Felling never reads scanner state; its only links are the `_enqueueCascade` call (774) and the constant sets `PW_LEAF_TYPES` (1439) and `PW_LEAF_TO_WOOD_TYPE` (1586), which stay. |
| S3 far reverter, S4 re-applicator | **Remove (dead today)** | The registry is never written. The far swap is engine `alpha_test_to_opaque` (L-FAR-1, D-C342). |
| S5 cascade | **Shrink to an event** | On a non-fell log break or an explosion: re-run `pwLeafLook` once on the pw leaves within Manhattan ≤ band (≤ 62 cells at band 3, ≤ 128 at band 4 [CALC]) of each removed log. No periodic job. |
| T1 decay sweep | **Shrink to an event** | Same trigger. Structure trees: the orphaned leaves are the template leaf cells whose supporting branch was removed. Legacy trees: a bounded BFS from the break. |
| `onPlace` component `pw:randomize_variant` (2165–2217) | **Keep + guard** | Player-placed leaves and logs still need a look. **Guard:** return when the placed permutation already has its look baked (e.g. `pw:rseed===true`, or the new nat bit), in case `onPlace` fires on structure placement (probe P-2). Otherwise a rotated structure's baked looks could be overwritten. The look itself is deterministic (`pwLeafLook`), so the risk is the wood-distance input on half-built structures, not randomness. |
| **Legacy leaves in old chunks** (already generated by `tree_feature`) | **His choice (Q2 below)** | Without a scanner they stay at worldgen v0. Since D-C343, v0 is a full shape with `alpha_test_to_opaque`, so they look complete but uniform. Options: (a) accept; (b) a one-shot `/scriptevent pw:legacyleaves <r>` finisher (TestRunner step, his witness-via-runner rule); (c) a slim periodic finisher using `dim.getBlocks(volume, {includeTypes: pw leaf ids})` like pw_vine (48 engine calls per 100 t instead of 927K `getBlock`s), assigning the look only where `rseed !== true`. |
| Legacy pw **log tiers** (bark variants) | **Gains** | Static finding F4 below: the scanner never gave worldgen bark tiers a variant. Structures can bake `pw:variant`/`pw:top_variant` for logs, so bark variety arrives for the first time. |
| Sapling growth T5 | **Keep + upgrade** | It is THE path by which player-planted trees become structure trees (§6.6). |
| Far swap | **Nothing needed** | Engine-native. |
| Vanilla leaves (`minecraft:*_leaves`) | unchanged | The scanner never processed them (`PW_LEAF_TYPES` is pw: only). |
| Vine scanner, plank scanner | **Keep** | Other sources remain: vanilla vines in old chunks and vanilla features; vanilla planks everywhere. If tree structures bake `pw:vine` and the vine-bearing tree features (`*_with_vines_*`) are replaced by structures, the vine scanner is left covering only old chunks and non-tree vines. |
| Litter lifecycle T2, leaf drift T6, boot sweep T3 | **Keep** | Independent of tree origin. |

### Static findings that are true today (pre-structure) — hypotheses until witnessed (P1)

- **F1** — S3 and S4 are dead code: `_appliedRegistry` is never filled (no `.set`, grep 2870–3233).
- **F2** — S11 verify does 178,608 reads per 10 s and only increments a counter; no write path remains (3442–3444).
- **F3** — The classify pass is legacy: `pwLeafLook` (2141–2149) reads position and wood distance only. `pw:section`/`pw:exposure` are read by nothing that renders. `_markLeaf` (2703–2723) survives only as a gate and costs up to 70 reads + 1 write per leaf. This confirms D-C342's retro-sweep ("forward scanner shrinks to 'assign pv once by position'"). It is removable even before J2.
- **F4** — `PW_LEAF_TYPES` is an alias of `PW_RANDOMIZE_TYPES` (2259), which **includes the 17 pw log-tier blocks**. Those blocks have only `pw:variant`/`pw:rseed`/`pw:top_variant` (no `pw:section_rolled`) [CODE `blocks/oak_young.json`, `spruce_elder.json`]. So:
  - In S2, every pw log in range reaches `_markLeaf` every sweep.
  - `detectSectionAndExposure` walks the trunk column (≤ 64 reads), then `withState("pw:section")` throws and is caught. The log never gets a variant from the scanner.
  - Depending on whether `getState` of an absent state returns `undefined` or throws (probe P-6), the per-log cost is ~h+8 reads or ~1 read.
  - Side effect in felling: the canopy-ray scan at 1439 counts pw log tiers as "leaves", which can inflate `ft:canopy_size` on pw-log trees.
- **F5** — Process A visits **every log cell**, and each one walks to the trunk top: Σ ≈ h²/2 reads per tree per sweep. h=10 gives ~55; an elder h=25 2×2 gives ~1,300 for the trunk alone [EST]. Then 6–400 adjacency reads.
  - Trees whose crown is vanilla leaves (any `_leaves` id passes 2888/2922) never become "rolled".
  - `_markLeaf` on a vanilla leaf throws, so `_walkTreeFromLog` returns 0 and those trees are retried on **every** sweep forever.
- **F6** — The cascade resets plus re-classify cost 3 writes per neighbour leaf per broken leaf/log. The only visible effect is the wood-distance re-look (the v1.3.197 intent).
- **F7** — The decay sweep's `reValidateExposure` reads 6 blocks per leaf per pass and never writes (`PW_EXPOSURE_RESETS=false`).
- **F8 (hazard, untested)** — The decay sweep has no "player-placed" exemption. A pw leaf that a player places more than 6 leaf-steps from any log (a hedge, a decoration) would turn to litter within ~10 s. This only matters if players can obtain pw leaf items (creative / pick-block / loot). Vanilla leaves are not in `PW_LEAF_TYPES_DECAY`, so they are safe.
- **F9** — TREEGROW's pool ids exist in no censused space (T5 row, P11 audit).
- **F10** — TREEGROW's `structure load name x y z` puts the structure's **min corner** at the sapling, so the trunk lands at the template's local trunk offset from the sapling, not on it (5090). The rotated offset needs `rotXZ` (civ_verify.js 16–21).

---

## 4 · Q2 — how much we save (numbers)

### 4.1 Script source (measured: byte counts of line ranges [CALC])

| Range | Bytes |
|---|---|
| Offset iterator 2316–2473 | 6,309 |
| Process A constants 2294–2314 | 1,235 |
| `_taStats` + teleport cooldown 2475–2510 | 1,253 |
| Scanner header / tunables / state 2512–2624 | 6,441 |
| Section / mark / BFS / layered 2626–2835 | 8,396 |
| Process A + phase-1 jobs 2837–3122 | 13,248 |
| Reverse / far-revert / re-apply 3123–3233 | 4,996 |
| Triggers / cascade / heartbeat / diag 3235–3388 | 7,082 |
| Verify + stats 3390–3531 | 7,433 |
| **Core scanner total** | **56,393 B (55.1 KiB) = 21.4 % of main.js** |
| + decay sweep 3536–3850 (keep ~2 KB of shared sets: `PW_LEAF_TYPES_DECAY`, `PW_LEAF_TO_WOOD_TYPE`) | 69,999 B (68.4 KiB) |
| + diagnostic scriptevents 3926–4074 (keep the `pw:forge_beat` line) | 77,122 B (75.3 KiB) = 29.3 % |

QuickJS keeps the compiled bytecode resident. Bytecode is roughly the same order as the source, so about **55–75 KiB of source plus a similar order of bytecode** [EST].

### 4.2 Resident heap

| Item | Freed |
|---|---|
| Typed shell buffers (A + P1) | 887 KiB [CALC] |
| `_decayLastVerified` (if decay becomes event-driven) | ~0.5 MB [EST] |
| BFS sets, shell index arrays (transient peaks) | ~0.8 MB peak [EST] |
| Source + bytecode | ~0.1–0.15 MB [EST] |
| **Total** | **≈ 1.0–1.6 MB resident/peak** [EST] |

This is modest: the D-C-era OOM threshold note (2319–2321) was 130 MB. Memory is **not** the main win.

### 4.3 CPU / tick budget — the real win

| Job | Reads per pass [CALC] | Nominal cadence | Demand if each pass finished instantly | Steady-state writes |
|---|---|---|---|---|
| S1 Process A | 710,781 + per-log walks (F5) | 30 t | **473,854 reads/s/player** | 0 once rolled |
| S2 phase-1 | 215,883 (+ F4 log walks) | 22 t | **196,257 reads/s/player** | 0 once looked |
| S11 verify | 178,608 | 200 t | 17,861 reads/s/player | 0 |
| T1 decay | 7,497 + 6 per leaf + ≤ 300 per unverified leaf (TTL 600 t) | 200 t | ~750–5,000 reads/s/player [EST at 0–1,500 leaves in the box] | ≤ 8 litter per pass |
| S5 cascade | 6 per key | 4 t | event-bound | ≤ 6 + 12 per key |
| S3/S4 | 0 (empty registry) | 39 / 17 t | ~0 | 0 |
| **Sum** | | | **≈ 690,000 reads/s per player** | |

- **Demand vs supply.** Script `getBlock` cost has not been measured here. Probe P-7 will replace this assumed range, which reads as follows:
  - at 1 µs per read, 690K reads/s is 0.69 s of script time per second;
  - at 3 µs it is 2.1 s;
  - at 5 µs it is 3.5 s.
- At any plausible cost, S1 and S2 **cannot finish at their cadence**. Each restarts at the next 30 t / 22 t boundary after it ends (single-job guards at 3003 and 3111), so together they **occupy the full `runJob` time slice every tick, permanently, and serially for each online player**. The verify job then competes on top.
- Everything else that uses `runJob` queues behind them:
  - the fell's `cleanOrphanLeavesJob` (the canopy "lingers");
  - the vine and plank swaps;
  - SLABSMOOTH;
  - CIVITAS jobs.
- **Removing the scanner returns that whole slice.** This is the honest headline. A precise "% of tick" figure needs P-7.

### 4.4 World writes avoided

- **Worldgen leaf on first contact:** 2 writes (mark + look).
  - Canopy sizes from code comments: "typical 1×1 canopy ~50–200 leaves" (2233–2234); elders up to ~1,500 (2591).
  - So **~100–400 writes per ordinary tree and up to ~3,000 per elder** [EST].
  - Every write dirties its chunk, so every forest chunk the player walks through is re-saved (disk / Realm upload).
  - **Structure trees: 0.**
- **Cascade:** ≤ 18 writes per broken leaf or log next to leaves. Event re-look: ≤ 1 write per leaf whose look really changes.

### 4.5 Block permutations (engine block registry)

| Leaf state set | Per block | × 11 | Δ vs today |
|---|---|---|---|
| Today (variant, rseed, section, exposure, section_rolled, off) | 1,176 | 12,936 | — |
| Drop the 4 bookkeeping states (variant × off) | 49 | **539** | **−12,397** (BP-02 30,104 → 17,707, −41 %) |
| Keep one bool (`pw:nat`, natural/structure-placed; §6.1) | 98 | 1,078 | −11,858 |
| + root blocks for §6.1 (48 templates × 4 rotations × 11 species) | +2,112 | | net −9,746 |

Dropping states changes the save format of existing leaves. D-C343 kept the states on purpose ("no save migration"). So **probe P-4 comes before any state removal**; until then the states can stay as dead weight with zero script cost.

---

## 5 · Today's BIGCANOPY felling, as read (for the upgrade)

1. **Gate** (1212–1233): broken id ∈ `LOG_TO_SPECIES` (vanilla + pw logs, 12 species); creative skip via `testfor`. No axe gate (v1.3.37 "disconnection principle").
2. **2×2 cross-section rule** (1238–1282): a 2×2 trunk only fells when all 4 columns at the cut layer are gone; the forced yaw then points toward the missing columns.
3. **Seed + BFS** (1286–1301, `findConnectedTree` 268–387): a 26-neighbour BFS over same-species logs at or above the cut, MAX_LOGS 200.
   - "Other-tree boundary": a candidate more than 3 blocks away whose column is independently rooted (≤ 24 reads down) is pruned.
   - Acacia gets a bridge pass through ≤ 2 air/leaf cells.
4. **"Is it a tree?"** — the only rule: `hasAdjacentLeaves` (411–437), any `_leaves`/wart/mushroom block in the 27-neighbourhood of any found log, and `logs.length ≥ 2`. **There is no player-placed protection at all.** A player log pillar touching any leaf block fells (D-C333 request still backlogged).
5. **Shape guesses:**
   - `detectTrunkWidth` (474–502);
   - `measureColumnHeight` (979–992, contiguous column from the cut x/z);
   - canopy rays (1418–1461, 8 rays r≤7, ≤ 280 reads, height clamp v1.3.65);
   - dominant `pw:variant` → `ft:leaf_variant`;
   - `hasVines` coarse grid (510–545);
   - tier from the broken id.
6. **Direction** (`pickFallYaw` 817–971):
   - 8 directions sampled at R=10;
   - slope primary (8·drop − 3·obstacles), the v1.3.37 law "trees ALWAYS fall downhill";
   - flat ground: away from the player (5.0) + downhill (1.5) − obstacles;
   - obstacle corridor fixed at ±2 wide × 3 high × trunkLen ≤ 8;
   - terminal angle `computeFallAngle` by first contact (125–146).
7. **Animation:**
   - `ft:falling_tree` spawned at stump+1 with `initialRotation`; logs cleared 1 t later (1399–1413);
   - 5.05 s heavy-impact curve (176–199, mirrors the RP);
   - per-tick pin + collision sweep (1642–1733) that freezes `ft:rest_angle` on a hard collider;
   - two-cue audio (fall at t0, impact at 82 t);
   - mid-fall litter at 30/55/80 % (1583–1620);
   - particle trail (1777–1815).
8. **Debris / impact** (1821–1881): damage + shake + knockback in a ±1.5 corridor; small vegetation smashed in a ±1 × 3 corridor; dust and leaf particles along the trunk line.
9. **Canopy removal** (`cleanOrphanLeavesJob` 633–807):
   - AABB of the felled logs ± 9 (cap 40,000 reads);
   - own-canopy BFS from the felled logs (range 8);
   - neighbour-protection BFS from standing logs;
   - the unprotected leaves (≤ 260) removed trailing-edge-first along the fall vector, paced by the fall curve (v1.3.62), with exact loot rolls.
10. **Cleanup** at 101 + 70 + 3 t: entity removed, `logs.length` vanilla logs dropped as items, axe damage.

**Reads per fell [EST from the bounds above]:**
- **Mature 1×1 oak, h=10:** 2×2 probe 32 + BFS ~390 + adjacency ~27 + yaw ~1,100 + angle ≤ 500 + rays ≤ 280 + vines ~324 + orphan AABB 19×19×28 = 10,108 + pin ~1,000 ≈ **13.7K**.
- **2×2 elder, h≈25 with ±8 branches:** BFS ~5,200 + AABB capped 40,000 + the rest ≈ **47K**.

---

## 6 · Q3 — felling with structure-known trees

### 6.1 Giving each placed tree an identity (no worldgen event exists)

Worldgen `structure_template_feature` placement fires no script event, so a ledger written "at placement" is impossible for worldgen trees. The tree has to carry its identity in its own blocks.

- **Option A (recommended): root block.** The lowest trunk cell of every template is `pw:<species>_root`.
  - It looks identical to the trunk block (same geometry and textures).
  - State `pw:tpl` (0..47: 16 templates × 3 ages, D-C460 T2).
  - The **`minecraft:cardinal_direction` trait** holds the rotation. D-C459: structure rotation turns trait states of custom blocks (BDS-verified for `/structure load` / `structureManager.place`; worldgen path = probe P-3).
  - Decode at fell time: walk down from the cut through same-species natural trunk cells to the root (≤ 32 reads). Read `tpl` + direction, then `id = "pw:tree/<sp>_<age>_<nn>"` and rotation.
  - Then read the **template directly from the shipped file**: `world.structureManager.get(id)`, `.size`, `.getBlockPermutation({x,y,z})`. This is already used and BDS-verified on 2.3.0 in `tools/civ_src/civ_verify.js` 44–53. Map local → world with `rotXZ` (civ_verify.js 16–21) plus the root's local offset.
  - The result is one source of truth: the same `.mcstructure` feeds placement and felling. **No cell table in script source** (a table would cost ~0.2–1 MB [EST] and undo the memory saving).
  - Cache the decoded cell lists per (template, rotation) in a small LRU (e.g. 16 entries).
- **Option B (script-placed trees only): ledger.** For saplings grown by TREEGROW the script knows template, rotation and origin at placement. A per-chunk dynamic property `pw:trees:<cx>,<cz>` could hold packed entries (≈ 8 chars per tree [EST]: local root 3 + template 2 + rotation/age/flags 2). It is only needed for data that changes over time (e.g. a future age progression). Option A already covers identity, so B is optional.
- **Natural vs player-placed flag on the blocks themselves.** Use `world.afterEvents.playerPlaceBlock` (fires only for players) to set `pw:placed=true` on any pw log or leaf a player places.
  - Structure and worldgen blocks keep the default `false`.
  - This avoids depending on whether `onPlace` fires for structures (probe P-2).
  - It also lets decay exempt player-placed leaves (fixes F8).
  - Cost: ×2 on the affected blocks' permutations. For leaves, take the bit from the dropped bookkeeping states (`pw:rseed` can be repurposed and renamed only after P-4).

### 6.2 Rules — "a real TREE is being cut" (his D-C333 requirement), structure regime

Each rule is cheap and evaluated in order. The first failure means **no fall** (the block simply breaks).

| # | Rule | How it is checked | Cost |
|---|---|---|---|
| G1 | Survival or adventure only | existing `isCreative` (994–1000) | 1 cmd |
| G2 | Broken block is a log of a tree species | `LOG_TO_SPECIES` | 0 |
| G3 | **Vanilla log ids never fell** in the structure regime | Every structure tree uses pw logs (trunk and branches; acacia/cherry/mangrove too). Logs drop **vanilla** items (`SPECIES[].drop`), so **every log a survival player places is vanilla** and can never start a fall | 0 |
| G4 | **Not player-placed** | `ev.brokenBlockPermutation.getState("pw:placed") !== true` (catches creative / pick-block pw logs) | 0 |
| G5 | Root found | walk down same-species, non-placed trunk cells without a gap to a `pw:<sp>_root` within 32 | ≤ 32 |
| G6 | Root stands on natural ground | the block under the root is in `PW_GROW_GROUND` (+ sand / gravel / mud for acacia / mangrove) | 1 |
| G7 | Template decodes | `structureManager.get(id)` exists; species of root = broken log = template | 1 call |
| G8 | **The cut cell is a TRUNK cell** of that template (not a branch, not a root flare) | un-rotate (cut − root) and look it up in the template's trunk set. Branch cuts follow G16 | 0 (cached) |
| G9 | Integrity | ≥ 70 % of the template's trunk cells above the root still hold natural logs, and ≥ 25 % of its leaf cells still hold natural leaves (thresholds = his call, Q5) | one `getBlocks(volume, includeTypes)` call |
| G10 | Severed | no natural trunk cell of the template remains at the cut layer (generalises the 2×2 quad probe to any cross-section; keeps the forced yaw toward the missing cells) | ≤ 4 |
| G11 | Something to fall | ≥ 2 natural trunk cells above the cut (today's `logs.length < 2` rule) | 0 |
| G12 | **No player build attached** | no `pw:placed` block and no non-template solid block (planks, glass, doors…) inside a template cell or face-attached to a falling log (the treehouse rule — refuse vs keep is Q4) | ≤ 6 × falling logs |
| G13 | One tree only | the falling set = this template's cells only, so neighbour trees are never consumed (replaces the rooted-column heuristic 288–314) | 0 |
| G14 | Not already falling | a per-root lock `Set` (two players or rapid breaks) | 0 |
| G15 | Stump is not a tree | breaking a remaining stump cell after a fall: nothing above the cut, so G11 fails | 0 |
| G16 | Branch cut (optional, Q6) | the cut cell is a branch cell: drop only that branch's sub-tree (the template knows the parent chain offline) as a small limb event, or nothing | 0 |

**Legacy regime** (trees in old chunks: no root, vanilla or untagged logs). His choice, Q1:
- **(a) No felling for legacy trees.** Exact and simplest; it satisfies "player-placed never".
- **(b) Keep today's heuristic for legacy trees.** In that case the D-C333 candidate rules must be added, including a **placed-log ledger**:
  - `playerPlaceBlock` on any log → per-chunk dynamic property of packed local positions (~3 chars per log [EST]; 1,000 placed logs ≈ 3 KB + keys, chunk-bucketed under the per-property string limit). A fell candidate touching a ledger position is refused.
  - Root on soil; non-persistent leaves attached (vanilla `persistent_bit=false`); no player blocks touching the trunk; the broken block in the vertical trunk column; contiguous log runs with no leaves within N = a structure, never a tree.

### 6.3 What replaces the BFS

1. Decode the template (G5–G7): ≤ 32 world reads + 1 cached structure read.
2. **Template cells × world state:** one `dim.getBlocks(new BlockVolume(aabb), {includeTypes:[species pw logs, species leaves, vines]})` call returns the present cells (the engine-filtered call pw_vine/pw_planks already use). Intersect it with the rotated template sets, then drop any cell whose permutation is `pw:placed`.
3. The falling set is:
   - template trunk cells **above the cut**,
   - all branch cells,
   - all leaf cells (and baked vines) still present.
4. The stump is the template trunk cells below the cut.
5. This replaces `findConnectedTree` (BFS + acacia bridge), `hasAdjacentLeaves`, `cleanOrphanLeavesJob` steps 1–2 (the 40K AABB + own-canopy BFS + neighbour protection), the canopy rays and `hasVines`.
6. **Cost per fell drops from ~13.7K / ~47K reads to ~0.5–3K [EST]**, with no heuristics.

### 6.4 Using the known shape for the fall itself

| Aspect | Today (heuristic) | With the template |
|---|---|---|
| Height / width | contiguous column at the cut x/z; quad probe | exact: trunk cells above the cut; cross-section per layer |
| Direction | slope-primary 8-direction sampler (v1.3.37 law), fixed ±2 corridor, trunkLen ≤ 8 | Same law kept. The obstacle corridor uses the template's **real crown half-width per side** and the **real length** (trunk + crown reach). The template's **crown centroid offset (lean)** becomes an extra term only as the flat-ground tie-break; making lean stronger would amend the v1.3.37 law, which goes through §7 supersession (Q7). |
| Terminal angle | first contact along the trunk line | first contact over the **swept crown footprint**: rotate the template's leaf/branch cells about the cut pivot and sample the ground under the canopy disc, not just the trunk line |
| Falling entity look | generic per species/tier + `canopy_size` 1–3 guessed from rays + dominant leaf variant | **Exact per-template geometry** (Q10): generated offline from the same `.mcstructure` (greedy-merged leaf boxes + log boxes; leaf textures = the baked look), selected by `ft:tpl` (int), with a canopy bone yawed by (structure rotation − fall yaw). Middle option: keep generic geometry but feed exact height, width, canopy radius and vines from the template. |
| Which blocks vanish | logs from the BFS (≤ 200) at +1 t; leaves = AABB orphans | exactly the falling set. Logs at +1 t as now. **Leaves use the v1.3.62 directional sweep unchanged**, fed the exact leaf list (sorted trailing-edge-first along the fall vector) |
| Collision pin | samples r=2..trunkH+1 on the trunk line every tick | same loop, plus the crown tip at the template's real reach (catches a canopy landing on a wall) |
| Debris / impact | ±1.5 damage corridor, ±1 × 3 vegetation corridor along the trunk | damage and smash over the **real landing footprint** (trunk line + rotated canopy disc); litter spawned on the landing leaf cells weighted by density; dust along the real trunk length |
| Drops | `logs.length` vanilla logs as items at the stump | same count from the exact falling log set; or (Q8) place a lying log run along the landing line (the BP-02 `fallen_*_tree_feature` look) and drop leaves as litter |
| Stump | whatever logs remained below the cut | trunk cells below the cut stay. Optional (Q9): the top stump cell becomes `pw:<sp>_stump` (cut face, ring count from the template's age); the root block stays, so the stump can never fell (G15) |
| Audio tier | from the broken id suffix | from the template's age (young / mature / old / elder) |

### 6.5 Decay and re-look with structure trees (event-driven, replaces T1 + S5)

On a non-fell log removal (branch cut, explosion, a legacy break):
- **Structure tree:** the leaves hanging from the removed branch's sub-tree (template parent chain) decay to litter over a few ticks.
- **Any tree:** the pw leaves within band of the removed log are re-looked once.

No periodic cost.

### 6.6 Sapling growth (T5) upgrade

- Pools: `pw:tree/<sp>_young_00..15` (the real templates), picked by position hash.
- Place with `world.structureManager.place(id, dim, origin, {rotation})`, where `origin = sapling − rotXZ(rootLocal)`, so the trunk lands on the sapling (fixes F10). Pass the rotation explicitly instead of the command string.
- The root block arrives baked, so the tree is fellable the instant it exists.
- Keep: the clearance check, the 6-per-chunk cap and the delay jitter.
- Make `_growRegistry` survive a reload with a small dynamic property (pending saplings only) if he wants growth to continue across sessions. Today it is lost on reload.

---

## 7 · Probes required before building (BDS, after the other job releases it; then his witness via TestRunner)

| # | Probe | Why it gates |
|---|---|---|
| P-1 | A `structure_template_feature` placement keeps **custom states** (`pw:variant`, `pw:off`, `pw:tpl`) | The whole "final leaves" premise. D-C459 verified `/structure load` and `structureManager.place`, not the worldgen feature path. |
| P-2 | Does `onPlace` (`pw:randomize_variant`) fire for `structureManager.place`, `/structure load` and the worldgen structure feature? | If yes, the guard in §3 is mandatory. |
| P-3 | Does the worldgen structure feature rotate **trait** states like `/structure load` does (L-ROT-TRAITS)? | The root-block rotation encoding. Fallback: one root block per rotation (4 ids) or template matching. |
| P-4 | Load a world saved with today's 6 leaf states after removing 4 of them: do `pw:variant`/`pw:off` survive? | Unlocks the −12,397 permutations. |
| P-5 | `BlockFilter.includePermutations`: does a partial-state match work? | Only needed for the slim legacy finisher (§3 option c). |
| P-6 | `BlockPermutation.getState` of an absent state: `undefined` or a throw? | Sizes finding F4. |
| P-7 | Measure µs per `getBlock` (and per `getBlocks` box) on BDS | Replaces the [EST] range in §4.3 with a measured % of tick. |
| — | Already proven (D-C459, BDS): `structureManager.get/getBlockPermutation/place` on 2.3.0; the Rotate90 mapping; entities inside structure files survive load | — |

Also the `pw:off` nudge under rotation: off = (x+2y+4z) mod 7 baked from **local** coordinates stays unique for every face- and edge-neighbour pair under all 4 rotations [CALC: Python check of all 18 neighbour offsets × 4 rotations, no collision]. Baked nudges therefore stay z-fight-free in rotated structures.

---

## 8 · Questions for him (copy-paste block; answer on each line)

```
Q1 Old-chunk trees (made before structures) — felling:  (a) never fell, break like vanilla  (b) keep today's heuristic + a placed-log ledger  -> answer:
Q2 Old-chunk leaves stay at worldgen v0 once the scanner is gone:  (a) accept  (b) one-shot /scriptevent finisher via TestRunner  (c) slim periodic finisher (getBlocks, 100 t)  -> answer:
Q3 Drop the 4 bookkeeping leaf states (-12,397 permutations) after a save-migration probe:  yes / no  -> answer:
Q4 Player blocks attached to a tree (treehouse):  (a) tree refuses to fall  (b) tree falls, player blocks stay put  (c) player blocks drop as items  -> answer:
Q5 Integrity thresholds for a fall (70 % trunk cells, 25 % leaf cells still present):  ok / your numbers  -> answer:
Q6 Cutting a BRANCH log:  (a) nothing (just breaks)  (b) that limb falls (small event)  (c) limb + its leaves drop as items/litter  -> answer:
Q7 Crown lean (heavy side) as the FLAT-ground tie-break only (slope stays primary, v1.3.37 law):  yes / stronger (= amend the law)  -> answer:
Q8 After the fall:  (a) items at the stump (today)  (b) a lying log run on the ground + leaf litter  -> answer:
Q9 Cut stump block with growth rings by age:  yes / no  -> answer:
Q10 Falling-entity look:  (a) exact per-template geometry (528 geos)  (b) generic geometry fed exact sizes from the template  -> answer:
```

---

## 9 · RETRO-SWEEP (proposed journal entry — qualifying: failed assumptions found (F1–F10), new pipeline design, external-API capability reused)

**HITS:**
- **scripts (BP-02)**
  - remove S3/S4/S11 now — dead/no-op, no visual change → S → HIGH;
  - drop the classify pass (F3) before J2: phase-1 assigns the look directly where `rseed !== true` → S → HIGH;
  - stop phase-1 touching pw logs (F4): a separate leaf-only set → S → HIGH;
  - fix the Process A vanilla-leaf retry loop (F5) or retire Process A → S → MED;
  - move the `pw:forge_beat` handler out of the `variant_audit` subscriber before deleting diagnostics → S → HIGH;
  - make the `log()` per-break `console.log` conditional (1219) → S → LOW.
- **trees/canopy/falling-tree**
  - root-block identity + template-read felling (§6) → L → HIGH (his D-C333 requirement);
  - the canopy-ray scan counts log tiers as leaves (F4 side effect) → S → MED.
- **custom blocks/permutations**
  - −12,397 leaf permutations after P-4 → M → HIGH;
  - `pw:placed` bit on pw logs/leaves (G4, F8) → S → HIGH.
- **worldgen/features/mcstructures**
  - P-1/P-3 probes gate J3;
  - the root block lives in every tree template → M → HIGH.
- **TREEGROW**
  - pool ids missing (F9);
  - corner-offset placement (F10);
  - switch to `structureManager.place` → S → HIGH.
- **build/verification tooling**
  - a BDS timing probe P-7;
  - a structure-tree gate: root present, tpl decodes, rotation round-trip → S → MED.
- **documentation/lessons**
  - L-FAR-1 consequences recorded: far reverter/reapplier formally retired → S → LOW.

**NO-HIT:** terrain caps · redwood biome · mobs (RP-07) · atmospherics/sky/fog · PBR/MERS textures · audio (dormant).
