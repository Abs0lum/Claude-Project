# TEXTURES notes (slice 2, written ~04:12 CT 10-07)

## Read so far
- Brief _logs/agent_brief_1007.md; ruling D-C1007-R231 (decision_journal.md line ~3969).
- Research: _docs/research/TEXTURE-VARIANT-REDUCTION-2026-10-07.{md,json}; json keys meta/families(268 list)/per_pack/permutations/res128.
  Each family: family, class, now, proposed, res, packs, bytes_*, atlas_px_*, used_by (block ids), n_keys.
  Atlas meta: cap 67.109 Mpx; used 70.01 (atlas_budget method) / 74.75 (field-merged blocks.json); RP-13 used 21.71.
  Scripts that made the numbers: _docs/research/tvr_src/ (bpstates.py, tvr_census.py, tvr_group2.py, tvr_plan.py, tvr_tables.py) -> REUSE for before/after Mpx.
- NOT yet read: CLAUDE-AR.md §4/5/7/9, PACK-SPLIT-2026-10-07.md, memory texture-budget.md (leaves 256 / sand 256 / grass 192 rulings), engine-laws.md.

## Approved cut: 60 families change, 191 images dropped (list: python filter families where proposed<now).
Owners: mostly RP-04 1.3.159; also RP-05 1.3.59, RP-01 1.3.125, RP-10 1.3.51 (logs/bark/mushroom_stem split RP-01+RP-04/RP-05).

## Consumer census (started)
- BP-02 1.3.230 (_build/bp02-230, read-only) block state names found in blocks/: pw:gvar (45 files), pw:gvarx (2), pw:variant (28), pw:randomize_variant custom component (28), pw:top_variant (17). 73 block files reference gvar/var.
- scripts/main.js: pw:gvar written at ~4928 (slab smoother 4873-4929); pw:randomize_variant registered (pw_variants, onPlace) — src copy tools/bp02_src_227/main.js:2364. Need: read the randomizer to see how it picks the range (hard-coded max vs from state values).
- TODO census: (a) terrain_texture.json arrays in RP-01/04/05/10 for the 60 families (array length = variant count; vanilla-key random arrays need no BP change); (b) for each pw:variant block: state value range vs texture count, material_instances per permutation -> which permutations point at dropped indices; (c) structures (.mcstructure in BP-02 structures/ storing block states pw:variant=N > new max) — decode NBT block palettes; (d) RP-13 ramp fills + _staging/ramps231/option-fill-repoint (266 ramp JSONs) for task 2.
- Do NOT touch _build dirs. Stage to _staging/textures231/<pack>/.

## Next steps
1. Finish census (a)-(d) with a script in scratchpad -> save results as _staging/textures231/census_consumers.json.
2. Read texture-budget.md memory + engine-laws for prior rulings; draft tier table (family -> view class -> colour/normal/MERS res + reason); flag conflicts (leaves 256, sand 256, grass 192) without changing.
3. Compute atlas Mpx before/after with tvr_src methods; MB per pack.

## Census findings added ~04:14 CT
- Randomizer = BP-02 scripts/main.js (1.3.230 build) pickVariantForBlock ~2300: leaves -> pwLeafLook (geometry looks, 7, NOT texture variants -> untouched);
  others -> N = PW_VARIANT_COUNT[typeId] (table at main.js:2205; log tiers oak/spruce/birch/jungle young..elder + dark_oak/pale_oak elder = 5) else default 5.
  pw:top_variant hard-coded Math.floor(Math.random()*7) (~line 2345) for ids containing _young/_mature/_old/_elder.
- Log tier blocks (e.g. blocks/oak_mature.json): states pw:variant[0..4] x pw:top_variant[0..6]; material_instances per permutation:
  '*' -> pw_oak_mature_log_v{variant}, 'log_top' -> pw_oak_log_top_v{top}. These are BP-owned single terrain keys (one key = one image).
  => KEY RISK: families oak_log/spruce_log/jungle_log/birch_log (11/15 -> 8) and bark/*_log (9-10 -> 8) — must map which image paths pw_*_log_top_v0..v6 and pw_*_<tier>_log_v0..v4 point at
  in RP-01/RP-04 terrain_texture.json; if a dropped image is the target of one of these keys, REPOINT the key (keep 7 top keys -> fewer images) rather than change BP states (no BP state change = no permutation change, no structure risk).
- Preferred approach for every family: cut images, keep terrain KEYS, repoint keys modulo new count (e.g. key v7 -> image v(7 mod 8)); random-array keys just get shorter arrays. Then no BP/script/structure consumer changes at all. Verify by: every terrain key in every pack resolves to an existing image after staging.
- Still TODO: map research family 'used_by' + terrain keys -> image paths (tvr_src/tvr_census.py already does key->image resolution; reuse it); structures check only needed if any BP state range shrinks (plan above avoids that).

## Key->image census DONE (draft) ~04:13 CT
- Ran _docs/research/tvr_src/tvr_census.py -> scratchpad census_raw.json (3650 keys, 3525 images; 3.6 s). NOTE it reads _build/bp02-229 (BC.BPS) — next slice: rerun with bp02-230 (set BC.BPS) for the final numbers.
- My mapper: _staging/textures231/census_consumers_draft.py (args: census_raw.json, research json, out json) -> _staging/textures231/census_consumers_draft.json.
  All 60 families matched (image counts == research 'now'). Drop rule in the draft = highest indices (ps[proposed:]) — PLACEHOLDER; better: pick keepers by visual distinctness (view them) — decide next slice.
- Result: 84 single-image terrain keys point at to-be-dropped images (gvar lattice keys like snow_g2, gravel_g11, mycelium_top_g15, podzol *_single / pw_side_gravel_* etc., used by pw:slab_* + pw:podzol/pw:mycelium); 753 array-key memberships touch dropped images.
  => Fix = rewrite terrain_texture.json: single keys repoint to a kept image (lattice slot g mod proposed — research says 12 keeps the (x+2z) lattice no-repeat guarantee; for 8/6 families check no-repeat), arrays drop the path. No BP-02 state/permutation/script/structure change needed -> structures safe by construction (verify: zero BP edits).
- Log tiers (pw_*_log_top_v0..6, pw_*_<tier>_log_v0..4) not in the 84 single list printout head — check full list in the json.

## ~04:15 CT additions
- tvr_group2.py run -> scratchpad g2.json (args: census_raw.json out.json 0). Draft tier table written: _staging/textures231/TIER-TABLE-DRAFT.md (class x res table + draft tiers + 6 FLAGs/questions).
- Prior rulings (memory texture-budget.md, 10-02): leaves 256; sand 256 all maps; dirt 128; planks grids, nylium, mud family, logs/bark, workstations, mycelium, copper chains+lanterns -> 128; others 256->192. Atlas law: keep referenced < ~60 Mpx.
- LAW CHECK open: layers smaller than colour unprecedented (only 30 sets differ, colour192/layers256). WebFetch Microsoft Learn texture sets page next slice.
- Bark keeper choice: BP log tiers use single keys pw_<sp>_<tier>_log_v0..4 -> bark/<sp>_log_vN; keep images so each tier's 5 keys stay DISTINCT (dropping highest index makes old/elder lose images: e.g. pw_spruce_old_log_v2/v3, elder v1/v2 hit). Repoint by tier, not mod.
- Census counting note: group2 'used' total = 76.44 Mpx (differs from doc 70.01/74.75) — reproduce the doc's two methods via tvr_plan.py/tvr_tables.py or tools/atlas_budget.py.
## NEXT (exact)
1. Rerun census with BC.BPS=[_build/bp02-230, markers-0.2.4-bp] and RP-13 from _staging/ramps231/rp13 (+ option-fill-repoint 266 JSONs) to get post-ramp-v9 numbers.
2. Microsoft Learn texture-set dimension check.
3. Choose keepers per family (view contact sheets of each family; keep visually distinct), finalise repoint map (84 single keys + bark tiers).
4. Compute Mpx before/after both methods + MB per pack for the tier table; must be < 67.1 with margin.
5. Then builder tools/texture_tier_231.py (deterministic), staging, README, 12-block before/after sheet (VIEW it).
- ~04:17 LAYER-SIZE LAW CHECK (partial): Microsoft Learn "Texture Set Documentation - Introduction" and bedrock.dev stable "Texture Sets" say NOTHING about layers needing to match colour dimensions. No documented rule either way -> mixed sizes are UNVERIFIED (P1). Only in-suite precedent: 30 sets colour192/layers256 (glowstone etc.) — check whether he ever witnessed those as fine (HISTORY/journal grep 'glowstone'). Safe default for the builder: keep layers == colour size; offer "layers at half res" only as a witness-test option (one test block family) — put that as a question to him.
- Side note: MCPE-110361 (old, WAI) — PBR layers not loading for variation arrays in terrain_texture.json; suite has used variation arrays + sets since; not relevant unless he reports flat PBR.

## ~04:20 CT 10-07 (fresh slice after R231c)
- R231c: ramps -> v9 solid stepped sides; RP-13's 248 pw_fill* textures RETIRED (delete from RP-13 terrain_texture.json + textures/blocks); BP-02's 266 pw_ramp_*.json come from _staging/ramps231/option-fill-repoint/bp02/blocks/ (only change: material_instances.fill.texture -> the block's own "*" texture). v9 geometry: _staging/ramps231/rp13/models/blocks/pw_ramps8.geo.json + pw_snowcaps_ramps8.geo.json.
- Tier questions (leaves 256? sand 256? dirt 192? logs/bark 192 or 128? ores 192 or 256? smaller normal/MERS test?) are WITH ABS0LUM, unanswered. Do NOT decide; builder must take each as ONE config value.
- Census rerun on bp02-230: scratchpad/tvr_census_230.py (sed copy, BC.BPS bp02-230) -> scratchpad/census_raw_230.json: 3650 keys / 3525 images, IDENTICAL to bp02-229 run (expected: slim removed only pw:var states, no texture refs).
- Reconcile estimate (UNVERIFIED, P1/P8 - must be computed, not subtracted): research 70.01 / 74.75 Mpx minus fills 16.25 Mpx colour -> ~53.8 / ~58.5 Mpx IF both methods counted the fills at 256 px colour-only. Verify by census with an overlay: copy of rp13-101 terrain_texture.json minus pw_fill* keys + bp02-230 with the 266 repoint JSONs (overlay dir in scratchpad, symlink the rest), then rerun group2 + doc's two methods (tvr_plan.py/tvr_tables.py).
## NEXT (exact, supersedes list above for steps 1-5 order)
1. Overlay census (above) -> reconciled Mpx table (both methods) before/after fills removal.
2. Keepers per family by VIEWING contact sheets (bark: keepers per tier so each tier's 5 v-keys stay distinct).
3. Finish repoint map for the 84 single-image keys (lattice g mod proposed; check no-repeat for 8/6 families).
4. Builder tools/texture_tier_231.py: per-class tier = single config values; fills removal step; staging + README + 12-block before/after sheet (VIEW).

## ~04:27 CT 10-07 (slice 3) — NEXT 1-3 DONE
- Overlay (scratch only): scratchpad/ov231/{rp13 (581->333 keys, pw_fill* images hidden), bp02 (bp02-230 symlinks + 266 option-fill-repoint JSONs)}.
- !! FINDING for RAMPS/lead: _staging/ramps231/option-fill-repoint/bp02/blocks repoints ONLY the base component fill; all 266 files still have
  20 permutation-level material_instances.fill = pw_fill* (5320 slots). If RP-13 fills are deleted with these JSONs, every permutation's fill face
  -> missing texture (if v9 geo still has 'fill' faces). My overlay simulated the full repoint (perm fill -> perm '*') in SCRATCH only. Not fixed in staging (not my slice).
- Atlas Mpx (colour tiles, w*min(w,h)), USED scope, cap 67.109:
  census method (tvr_census used_keys_merged): before 70.231 | fills removed 52.799 | + 191-image cut 49.960
  atlas_budget.py method (wrapped, no _docs write; md5 unchanged): before 74.4 | fills removed 57.0 | + cut 54.4 (before+cut only 71.8)
  ALL keys: census 83.945 -> 67.692 -> 64.514; atlas_budget 92.5 -> 76.2 -> 73.1.
  Files: _staging/textures231/census231/ (atlas_231_fills.txt, atlas_231_after_cut.txt, ab_*.json, ab_wrap.py [args: before|after out.json [keepers.json]]).
- Keepers: _staging/textures231/pick_keepers.py (args census_raw.json census_consumers_draft.json out.json sheet_dir) -> keepers/keepers_231.json + keepers/sheets/*.png + keepers/all_0..3.png (ALL VIEWED 04:25).
  Rules: PIN images shown alone by a used single key (non-lattice, non-tier) e.g. cobblestone (pw_hatch_3); seed = most-referenced; then farthest-point on per-family z-scored look features
  (mean/std RGB, 4x4 luminance layout, gradient energy, 8-bin hist). (First attempt with raw-pixel L2 dropped the most distinct tiles — replaced.)
  STAGED override: torchflower = sprout v0-2 / bud v3-5 / bloom v6-8 in ONE random array -> keep 2 per stage (v0,v2,v3,v5,v6,v8).
  Viewed notes: birch bark v1 = near-dup of v0 (dropped, good); hardened_clay all near-identical; spruce bark kept v8/v9 after rerun.
- Repoint map: _staging/textures231/repoint_map.py (args census_raw.json keepers.json out.json) -> keepers/repoint_map_231.json.
  13 gvar lattices re-solved (constraint: cyclic slot distance 1..4 differ = 8 neighbours via x+2z plus slab phase +4); 86 lattice keys change; all no-repeat TRUE
  (crimson/warped nylium SIDE lattices were ALREADY repeating before; now fixed). 10 bark tiers, all 5-distinct. 4 other singles (nearest look). 90 array keys lose paths. 0 problems.
  Total single keys changed 102 (the old '84' was for the placeholder highest-index drop; superseded).
- Census source: scratchpad/census_raw_230.json (before), census_raw_ov.json (fills removed). Tier questions still with Abs0lum -> config values.
## NEXT (exact)
1. Builder tools/texture_tier_231.py: inputs keepers_231.json + repoint_map_231.json + tier config (one value per class: leaves/sand/dirt/logs-bark/ores/layer-scale, all PENDING him);
   rewrites terrain_texture.json per owning pack (RP-04/05/01/10) — arrays drop paths, singles/lattices/tiers repoint; deletes dropped colour+_n+_mer+set json; stages to _staging/textures231/<pack>/.
2. Verify: every terrain key in every staged pack resolves to an existing image; zero BP-02 edits; lattice no-repeat recheck from staged JSON; rerun ab_wrap on staged stack.
3. README + 12-block before/after sheet (VIEW). Tell lead about the option-fill-repoint permutation gap.

## ~04:28 CT 10-07 (slice 4) — RAMP FILL REPOINT DONE (owned now)
- tools/ramp_fill_repoint_231.py <src_blocks> <out> -> _staging/textures231/ramp-blocks/ (266 files, 5320 fill slots base+perm repointed to own '*').
- Verified: 0 'pw_fill' strings; parsed JSON == source except fill.texture (266/266); == _build/bp02-230/blocks ramps except fill (266/266, none missing); every fill == its '*'.
- v9 geo (rp13 pw_ramps8 + pw_snowcaps_ramps8) material_instance names = cut/deck(/snow) only -> NO fill face exists; fill instance is dead but now safe.
- README: _staging/textures231/ramp-blocks/README.md. LEAD: the old option-fill-repoint set had perm fills still = pw_fill* (harmless only because v9 geo has no fill face); use ramp-blocks/ instead.
## NEXT (exact) — builder not started
1. tools/texture_tier_231.py: inputs keepers/keepers_231.json ({family:{now,proposed,seed,pinned,keep[...]}}) + keepers/repoint_map_231.json
   (lattices{fam:{changes{key:[old,new]}}}, bark_tiers{tier:{changes{key:[old,new]}}}, singles{key:[old,new,[]]}, array_keys_touched=90 COUNT only -> builder must drop non-keeper paths from arrays itself)
   + TIER config (leaves/sand/dirt/logs-bark/ores/layer-scale, PENDING him — keep layers == colour size by default).
   Owning packs RP-04 1.3.159 / RP-05 1.3.59 / RP-01 1.3.125 / RP-10 1.3.51 (read from _build, never write there); also apply RP-13 fills removal (248 pw_fill* keys + images).
2. Verify every terrain key resolves in staged stack; zero BP edits besides ramp-blocks; lattice no-repeat recheck; ab_wrap Mpx on staged stack.
3. README + 12-block before/after sheet (VIEW).

## ~08:56 CT 10-07 (slice 5) — BUILDER DONE (clock showed 08:55 after a cp -rs; deadline 04:40 overrun)
- tools/texture_tier_231.py run: staged terrain_texture.json for rp01/04/05/10/13 + <pack>/_DELETE.txt (1673 files, 77.92 MB); report texture_tier_231_report.json. Deterministic (md5 x2).
- Fix made: RP-01 mushroom_* keys are data-value LISTS containing {variations} dicts -> builder strips only inside variations, never shortens indexed lists (aborts if a dropped path is in an indexed slot).
- Counts: single repoints 102 == map; variation-key entries 95 vs map's '90' (unreconciled counting difference; 0 dropped paths still referenced).
- tools/texture_tier_231_verify.py -> verify_231.json: 0 missing everywhere except RP-04 41 PRE-EXISTING (same in base: pw_side_* paths) -> tell lead.
- README _staging/textures231/README.md with overlay order.
## NEXT
1. Run scratchpad stg231/ab_wrap_staged.py after <out.json> (symlink farm ready) to get staged-stack atlas numbers; update README.
2. Reconcile 95 vs 90. 3. 12-block before/after sheet (VIEW). 4. TIER resize step once Abs0lum rules.
