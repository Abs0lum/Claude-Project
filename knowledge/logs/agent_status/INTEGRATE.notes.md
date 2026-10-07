# INTEGRATE notes (for the next slice) — written slice 1, 04:35 CT 10-07

## Task (verbatim essentials from lead)
Write deterministic builder /home/claude/tools/build_round_231.py producing NEW dirs (never overwrite; refuse if dst exists):
- BP-02 1.3.231 -> _build/bp02-231 (base _build/bp02-230 = SLIM; keep slim: NO pw:var on ramps)
- RP-13 1.0.2   -> _build/rp13-102 (base _build/rp13-101)
- RP-04 1.3.160 -> _build/rp04-160 (base _build/rp04-159)
- RP-01 1.3.126 -> _build/rp01-126 (base _build/rp01-125)
- RP-12 1.0.2   -> _build/rp12-102 (base _build/rp12-101)  [BLOCKS also staged RP-12-LITE frames geo; lite base _build/rp12-101-lite — ask lead / note if a lite 1.0.2 is wanted]
I build only. NO packaging, uploads, BDS. Rules: _logs/agent_brief_1007.md. Backups of edited tools -> _garbage/INTEGRATE-pre/.
After build: tools/geo_ref_check.py on new dirs (0 missing/uppercase/odd); block permutation total BP-02 + Markers vs 65,536;
node --check every script; tools/js_dupcheck.py; all CIVITAS suites (cd tools/bp02_src_228 && for t in tests/*.mjs; do node $t || echo FAIL $t; done).
Disk: check `df` before EACH copy; stop with a note if < 400 MB free.
Final report: contents per pack, md5 of key files, checks, skipped items. Append phase_log line `[HH:MM CT 10-07] INTEGRATE DONE: ...`.

## Inputs (what I learned so far)
1. CIVITAS scripts: tools/bp02_src_228/*.js (45 files) -> copy every .js differing from _build/bp02-230/scripts.
   Reference pattern: tools/build_bp02_228.py (122 lines; line 110 replaces PW_BUILD, line 112 replaces the
   "companion v7 LOADED" banner — DROP that step). Also tools/build_slim_230.py (105 lines) = how 230 was slimmed (read it:
   must not reintroduce pw:var on ramps). Set `const PW_BUILD = "1.3.231";` + next line `globalThis.__PW_BUILD = PW_BUILD;` in main.js.
2. _staging/blocks231/README.md (read fully):
   - RP-12 models/entity/pw_frames.geo.json (md5 abb3fe3d...) replaces; RP-12-LITE copy md5 b7ece78b.
   - RP-04 textures/entity/bed/<16 colours>{,_n,_mers}.png replace (48 files; not light_gray).
   - BP-02 structures/pw/mvv_inn_{a..d}_r1.mcstructure + stages/ (20 s0..s4 + 8 _w/_r) replace.
   - BP-02 scripts/pw_civ_buildings.js (md5 f54228be) = source copy with 4 inn entries swapped -> compare md5 with
     tools/bp02_src_228/pw_civ_buildings.js; if source already has them use source. NOTE: tests/test_shifts.mjs line 304 expects inn beds -> 32 (owner proposal; a failing suite may be from this).
   - BP-02 blocks: pw_jib_panel.json, pw_secret_painting.json, roots/{acacia,cherry,mangrove}_root.json replace.
   - RP-04 textures/terrain_texture.json (md5 24b04dc4...) replaces (adds pw_acacia_log_top_single; 1833->1834 keys).
     CONFLICT RISK: if any other input (ramps/fill removal is RP-13 not RP-04, ok) also touches RP-04 terrain_texture.json, merge by key instead of file replace.
   - BP-02 scripts/pw_companion.js (md5 d0c9a4b7...) — also already edited in tools/bp02_src_228 (verify md5 equal).
   - tools/build_rp12_gallery.py lines 143–144: swap e/w x origins (proposal) — only needed for regeneration; staged geo is used for this build -> note only (do not need to fix for 231) unless lead wants it; if fixed, back up first.
3. _staging/ramps231/README.md (read first 3.5 KB; the rest = final report, read before building):
   - bp02/structures/pw/road/{t,v}_ramp8.mcstructure (md5 e9772f19..., afc222f7...)
   - rp13/models/blocks/pw_ramps8.geo.json (f22b310b...), pw_snowcaps_ramps8.geo.json (dd558d6d...)
   - rp04/models/blocks/pw_ramps.geo.json (113e36cc...), pw_snowcaps.geo.json (fa1f0015...)
   - Ramp BLOCK JSONs: use _staging/textures231/ramp-blocks/*.json (266 files, fill.texture repointed to '*' in base + 20 perms;
     0 'pw_fill'), NOT ramps231/option-fill-repoint. These replace BP-02 blocks/pw_ramp_*.json — CHECK they don't carry
     pw:var (slim 230 removed it) — diff vs _build/bp02-230/blocks: README says parsed identical except fill.texture.
   - Fill removal flag (default ON, ruling D-C1007-R231c @ decision_journal.md line 3982): delete RP-13's 248 pw_fill* keys from
     textures/terrain_texture.json + their files under textures/blocks. Before deleting, grep all new build dirs for 'pw_fill' (must be 0 refs after).
   - PROPOSAL-rampclear.js is NOT a pack file (owner pw_civ_clock.js) — skip.
4. _staging/trees231/README.md (18 KB, NOT yet read): 216 tree structures (MD5SUMS-structures.txt) + RP-01 seamless bark 54 files (MD5SUMS-RP-01-bark.txt).
   _staging/acacia_230/README.md (15 KB, NOT yet read): install via install_acacia_230.py / MD5SUMS — read "install" section; prefer copying files per MD5SUMS over running its installer against _build (installer may target a fixed dir).
5. _staging/skyway230/README.md (16 KB, NOT yet read): option C, subdirs bp/ rp/ src/. Include blocks+geometry. Confirm geo_ref_check.
6. Excluded: _staging/palace231, castle231. textures231 tier output: leave a flag (e.g. --tier-dir, default None) hook.

## Sizes / disk (04:31 CT)
Free 1.4 GB. Base sizes: bp02-230 151M, rp13-101 95M, rp04-159 200M, rp01-125 188M, rp12-101 204M = ~838 MB total.
-> Can't do all 5 copies unless lead frees more. Order by priority: BP-02, RP-13, RP-04, RP-01, RP-12; df before each, stop < 400 MB.
Consider letting the builder do one pack per invocation (--pack bp02 ...) so slices can resume.

## Facts verified (slice 1, after first notes)
- Scripts differing src vs bp02-230: main.js (ONLY the PW_BUILD line: src says "1.3.227"), pw_civ_clock, pw_civ_land, pw_civ_people,
  pw_civ_plan, pw_civ_shop, pw_civ_streets, pw_companion. No NEW scripts. CIV-LAND is still mid-work (B paused 04:31) -> scripts may still move;
  builder must record md5 of every copied script in its output; ideally build after CIV-LAND DONE (ask lead).
- main.js: replace `const PW_BUILD = "1.3.227";` (src value!) -> "1.3.231" + add globalThis line. Builder should regex any version, assert exactly 1 match.
- pw_companion.js staged md5 d0c9a4b7f37b92f212b81f32ca8b840a == src (so src copy covers it).
- pw_civ_buildings.js: src md5 0fb42f19... == bp02-230 (unchanged); staged blocks231 copy f54228be7651e171eea04ccb00643839 has the inn v2 entries
  -> builder: assert src md5 == 0fb42f1930ff0e4f9bab5428fa82ad0f then use the staged copy; if src changed, STOP (needs merge of civ_inn/CIV_BUILDINGS-inn.json).
  Expect tests/test_shifts.mjs line 304 to fail (inn beds 32) only if tests import staged file; tests run on src (src lacks inn v2) -> fine. Check.
- Ramp structures staged t/v_ramp8: 0 'pw:var' bytes. textures231/ramp-blocks: 0 files with pw:var. Still run slim_structure-style check on ALL
  overlaid structures (inns, trees, skyway_test, ramps) — any ramp palette entry with pw:var -> strip (import mcstructure as M, see build_slim_230.py).
- Skyway: NOT in bp02-230 (0 skyway blocks). Install (README §9): BP-02 6 blocks + structures/pw/skyway_test.mcstructure; RP-13 models/blocks/pw_skyway.geo.json,
  textures/blocks/pw_skyway/ (28 files), merge 7 keys of rp/terrain_texture_add.json into RP-13 terrain_texture texture_data,
  RP-13 has NO texts/ -> create texts/en_US.lang + languages.json from staging. md5s listed in README §9 (prefixes).
  Gate: geo_ref_check --bp bp02-231 --rp rp04-160 --rp rp13-102 exit 0; every new terrain key resolves in RP-13.
- Trees231: 216 BP-02 structures/pw/trees/{birch,oak,spruce}_*.mcstructure (MD5SUMS-structures.txt, md5sum -c) + RP-01 54 bark pngs
  _staging/trees231/RP-01/textures/blocks/bark/ (MD5SUMS-RP-01-bark.txt). TREES worker DONE 04:25 (cap v2).
  !! RP-01 falling-tree copies MUST be regenerated for these 216 + 32 acacias: ft_tpl_gen_lite.py <rp_dst> <BP view> --maxb=8 --clusters=12 --runfrom=3 --close=3
  (recipe tools/build_rp01_125.py). _staging/acacia_230/build_rp01_acacia230.py asserts ONLY 32 acacia geos change -> can't use as-is with trees231;
  read it + build_rp01_125.py and do one combined ft_tpl regen over bp02-231's blocks+trees (expect 248 models/entity/ft_tpl/*.geo.json changed);
  keep _docs/fell/ft_tpl_index.json old copy as ft_tpl_index.pre126.json (as acacia script does). Check ft_tpl_gen_lite writes to _docs (side effects!).
- Acacia: 32 files _staging/acacia_230/trees/acacia_00..31.mcstructure (MD5SUMS). BP install = copy into structures/pw/trees/ (or run
  install_acacia_230.py --build _build/bp02-231 --check / then without --check: asserts 512 others + pw_ft_tpl_index.js unchanged — run it BEFORE trees231 overlay, or use its --check only).
  Measure: measure_acacia_230.py <bp02-229 trees> <bp02-231 trees> /dev/null -> expect sky 255->2, ends_open 89->0, stem_same 32.
- RP-13 fill: 248 "pw_fill" keys in textures/terrain_texture.json; 992 files in textures/blocks/ with pw_fill in name (744 unique stems; = png/_mer/_n/texture_set). 
  Fill-removal flag default ON. After removal grep bp02-231 + rp13-102 for 'pw_fill' = 0.
- RP-13 base manifest name "AbsolutRealism Architecture RP v1.0.1" [1,0,1].

## Progress
- Slice 1 (04:30–04:37 CT):
  * Wrote tools/build_round_231.py (md5 4b98fb80a7e2ee40ab2aa80c89455c08). Modes: --check (validates all inputs, writes nothing),
    build (--packs bp02,rp13,rp04,rp01,rp12 [--lite adds rp12lite] [--keep-fills] [--tier-dir DIR]), --post (all checks -> _logs/build_round_231_post.json).
    Existing dst dirs are SKIPPED (never overwritten). A failing pack is renamed <dst>.FAILED. Disk guard: free - du(base) >= 400 MB before each copy.
    Build log: _logs/build_round_231.json (per pack: replaced/added counts, notes, free MB).
  * --check: OK (all README md5s, 3 MD5SUMS files, 266 ramp blocks with 0 pw_fill/pw:var, inn 4+28, bed 48, skyway 28 tex,
    slim law = 0 ramp palette pw:var in every staged structure, src pw_civ_buildings == base 0fb42f19, src companion == staged d0c9a4b7).
  * BUILT (04:35): rp13-102 (replaced 2 ramp geos, added skyway geo + 28 tex + texts/en_US.lang + languages.json, +7 skyway keys,
    removed 248 pw_fill keys + 992 pw_fill files; no 'pw_fill' left in any RP-13 json; 95M -> 32M),
    rp04-160 (2 ramp geos + 48 bed pngs + terrain_texture +1 key [verified: only key pw_acacia_log_top_single added, none changed]),
    rp12-102 (pw_frames.geo.json abb3fe3d). md5: rp13 terrain_texture 614fa435..., rp13 manifest 27e8b030..., rp04 terrain_texture 24b04dc4...,
    rp04 manifest 490009bc..., rp12 frames abb3fe3de64498066ab7b44c5644a492, rp12 manifest fa360f6a...
  * NOT BUILT: bp02-231 (HELD — CIV-LAND item B "ramp8 on mild grades" paused at 04:31, may still edit tools/bp02_src_228; asked the lead
    whether to build now. All CIV-LAND/CIV-PEOPLE staged scripts == src copies as of 04:36). rp01-126 (needs bp02-231). rp12-102-lite (not requested; --lite).
  * Not touched: tools/build_rp12_gallery.py lines 143-144 (not needed for this build; staged geo used) — still a proposal for the lead.

## Next steps (next slice)
1. Get lead's go for BP-02 (or check CIV-LAND status DONE). Then: `python3 tools/build_round_231.py --packs bp02` (runs all suites FIRST and
   aborts if any fail; then node --check + js_dupcheck inside). Then `--packs rp01` (ft_tpl_gen_lite over bp02-231; rewrites
   _docs/fell/ft_tpl_index.json, old kept as ft_tpl_index.pre126.json; asserts only ft_tpl geos / leafatlas / bark / manifest change).
2. `python3 tools/build_round_231.py --post` -> geo_ref_check (bp02-231 + rp04-160, rp13-102, rp01-126, rp12-102), permutations
   (BP-02 + markers-0.2.4-bp vs 65,536; expect ~ 1.3.230's count + skyway 3x20+3x4 = +72), node --check, js_dupcheck, suites, md5s.
3. Acacia measure: `python3 _staging/acacia_230/measure_acacia_230.py _build/bp02-229/structures/pw/trees _build/bp02-231/structures/pw/trees /dev/null | tail -3`
   (expect sky 255->2, ends_open 89->0, stem_same 32).
4. Report + status DONE line + phase_log line.
