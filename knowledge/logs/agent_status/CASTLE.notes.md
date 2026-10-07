# CASTLE notes (slice handoff) — updated 2026-10-07 ~04:21 CT

## Done (castle varieties)
- All 10 castle varieties built + castle_verify all pass; staged in /home/claude/_staging/castle231/ (lord al2..al5/bl* ~1.9 MB tgz each; grand ag1/bg1).
- Renders in /home/claude/_docs/castle/v0_4/ all VIEWED (contact sheets in scratchpad castle_lord_sheet.png / castle_grand_sheet.png).
- FINDINGS to report: (1) bl1 and bl2 ground plans are nearly identical -> variety not distinct enough (cause not yet traced: check seed/params for bl1 vs bl2 in castlegen.py variety table). (2) bg1 outer-bailey pipe joining the sewer trench: NOT yet explained — open item.

## Academy II v2 — state
- Working copies MOVED to /home/claude/_staging/castle231/academy2v2/ (survive scratchpad):
  - acad2v2_layout.py  md5 08a257b864435803dc555c837396ea26  (== v1 acad2_layout.py, NOT yet edited)
  - acad2v2_render.py  md5 216f11c6f57e2b18ee2b906a069e819b  (retargeted: import + OUT only)
  - acad2_layout.py / acad2_render.py = v1 reference copies.
- Format: layout lists G / U / B = [(cat, (x0,z0,x1,z1), label)], MASS = [(x0,z0,x1,z1,h,roof,cat,label)];
  frame x = depth from gate (0 = gate/town side), z = frontage, 0..383, inclusive rects. overlaps(level) checker at end.
  Render imports layout as L; uses L.B_ROUTES for basement routes; CAT/CAT_NAMES legend.
- (resolved) v1 render wrote to _docs/castle with v1 filenames; v2 copy now writes to _docs/castle/academy2_v2/ instead.

## Exact next steps
1. DONE 04:1x: acad2v2_render.py now imports acad2v2_layout and writes to _docs/castle/academy2_v2/ (v1 PNGs safe). Run it from inside academy2v2/ (cd there or PYTHONPATH) so the import resolves.
2. Rewrite G, U, B, MASS (and B_ROUTES) in acad2v2_layout.py per ruling D-C1006-ACAD2 (decision_journal):
   ONE central building (great hall + central tower core) with many connected wings + auxiliary buildings,
   courtyards between them, covered outside walkways/cloisters (cat "passage"/"sacred" thin rects) joining EVERYTHING;
   storybook-school feel, original design. Roles: student dormitories (house towers/wings), classrooms, library,
   great hall, masters' lodgings, Rector, junior school. Every secret grounded in a real palace feature from
   /home/claude/_docs/palace/PALACE-II-RESEARCH-2026-10-06.md (cite the feature per secret in the doc).
3. Run overlaps() for G/U/B -> must be empty; run render; VIEW all 3 plans + massing at full res (state camera facing).
4. Write /home/claude/_docs/castle/ACADEMY-II-DESIGN-v2-2026-10-07.md (what changed vs v1, room schedule, walkway network, secrets table with palace sources, images).
5. Final: status DONE line, phase_log line, report (files + md5, findings bl1/bl2 + bg1 pipe).

## Slice 04:18-04:21 CT
- DONE: G list in acad2v2_layout.py REPLACED with v2 design (md5 bf4d4365e0a21592c3fde8613c43204b). Backup of unedited copy = acad2_layout.py (v1) in same folder.
  Design: gate (x3-22) -> FORECOURT -> Entrance Range -> GREAT HALL (x150-219,z156-227) -> Central Tower (x220-251,z172-211).
  Wings: Schools, Labs, Observatory, Library, Kitchens, Infirmary, Masters' Lodgings, Rector's Lodge, Chapel, Junior School, Stables;
  House Towers I-IV + Dorm Ranges I/II. Courts: Scholars', Masters', Hall Garth, Library, Chapel. Cloister ring x96-255 / z96-291 + walks to each tower.
- overlaps(): G [] U [] B [] (U/B still v1 content). Render ran OK -> _docs/castle/academy2_v2/ (4 PNGs).
- VIEWED ground plan (top-down; gate side x0 at TOP of image, cliff/lake at bottom; z runs left->right). Findings:
  a) FIXED 04:2x (renamed Gate/Left/Right/Lake Cloister; md5 below) — was: cloister NAMES wrong for the drawn side: "West Cloister" (x96-99) is the gate-side (top) strip; "North Cloister" (z96-99) is the LEFT strip;
     "South" = right strip; "East" (x252-255) = cliff-side (bottom) strip. Rename to Gate/Left(z0)/Right(z383)/Lake cloisters or use anatomical terms.
  b) SECRETS dict coordinates are still v1 -> markers 3,20,28,29,30,31,32,33,35 float in empty ground/forecourt. Must re-site every secret onto v2 rooms
     and ground each in PALACE-II-RESEARCH (cite feature).
  c) Central Tower sits BEHIND the hall (lake side), not at the crossing — consider moving it to a crossing (e.g. between hall and Entrance Range) if Abs0lum wants a true central tower.
## Next (in order)
1. Rename cloister labels; re-site SECRETS (+ B_ROUTES) to v2 rooms.
2. Rewrite U (upper: dormitory floors in house towers/dorm ranges, library gallery, hall roof, covered bridges) and B (cellars under hall/kitchens, tunnels, sewer) to match G.
3. Rewrite MASS (massing currently v1 -> view after rewrite).
4. overlaps() all levels; render; VIEW all 4 PNGs (state facing); write _docs/castle/ACADEMY-II-DESIGN-v2-2026-10-07.md.
5. Carry open findings: bl1/bl2 near-identical (trace castlegen.py variety table), bg1 outer-bailey pipe join.
- acad2v2_layout.py md5 after cloister rename: 333615384785560de0b208c54fa9ef01

## Slice 04:21-04:3x CT
- DONE: U, B, MASS, SECRETS, B_ROUTES rewritten for the v2 ground plan; new SECRET_SOURCES dict (id -> palace feature + section of PALACE-II-RESEARCH). Ice House (290,150,298,158) added to G (Library Court).
- Every secret marker checked inside a v2 room (39 = Countermine marker moved into Guard cellar (12,180)). 30 renamed Infirmary Stove Passage, 31 Matron's Door under the Hangings, 12 Hall Roof Trusses (were v1 orangery/sunken obs/library trusses).
- overlaps(): G [] U [] B []. acad2v2_layout.py md5 60848e35cf49ba0bfa058298b5584667.
- acad2v2_render.py: stale v1 text replaced (notes, subtitles, massing labels), dry-ditch fill disabled. md5 552dbe80ce52e9a8a5e632d3a71bcf83.
- All 4 PNGs re-rendered + VIEWED (plans top-down, gate side x0 at top, z0 left; massing viewer at gate side looking toward the lake).
- Viewed findings: massing label "Quay (feet -12)" leader lands near the Central Tower (label placed at x332 z120; cosmetic). Supper closet (4x4) and upper covered-bridge labels too small to print (markers show them).
- Central Tower still at x220-251 z172-211 (AWAITING Abs0lum's ruling).
## Next
1. Write /home/claude/_docs/castle/ACADEMY-II-DESIGN-v2-2026-10-07.md (changes vs v1, room schedule, walkway network, secrets table from SECRET_SOURCES, images).
2. Carry open findings: bl1/bl2 near-identical (castlegen.py variety table), bg1 outer-bailey pipe join.

- 04:2x DONE: design doc written /home/claude/_docs/castle/ACADEMY-II-DESIGN-v2-2026-10-07.md md5 6f09c24ba609fa56354a8436f85bd87f. Remaining open: Central Tower ruling; bl1/bl2 near-identical (castlegen.py variety table); bg1 outer-bailey pipe join; cosmetic Quay label in massing.

## Slice 04:27-04:35 CT (fresh slice) — findings, NO files changed
- bl1/bl2 TRACED: not a seed bug (rng = seed*7919 + skin*104729 + len(size) -> distinct streams). Skin B lord box is FIXED at 192 and
  the ground-plan draws have few options (plan 4, quad 3, keep_corner 4, moat dry/wet/none). bl1 and bl2 drew the SAME combo:
  square / quad 60 / keep corner 0 / dry ditch (differ only in tower shape round vs square, curtain 8/13 vs 9/13, lake_w 12 vs 9, roof).
  Real gap: docstring promises "FORCED VARIETY by seed" but NOTHING enforces it (no distinctness check in VARIETIES). Fix = decision fork
  (re-roll bl2 changes a shipped seed's character, against the "a seed keeps its character" rule) -> NOT applied; needs lead/Abs0lum ruling.
  Options: (a) swap bl2 -> next seed whose (plan,quad,keep_corner,moat_kind) differs from all others; (b) add a plan-signature distinctness
  check + test in VARIETIES; (c) keep, accept.
- bg1 pipe EXPLAINED: it is the SLUICE CULVERT (lake overflow, Caerphilly law), real and connected, not a drawing artefact.
  sluice lip (175,-1,82) -> race 8 -> basin (175,-6,73) w/ fountain -> drop shaft (175,-14,72) -> culvert at trench level (-14..-13)
  straight along z at x=175 to rear_z=128 (code castlegen.py ~L1696-1702: lpath((sx,sz),(sx,outfall_z),"z")).
  In-memory build flood-fill from the drop shaft at F_TRENCH reaches 372 trench cells incl. outfall (255,-14,128) and junction (0,-14,128).
- Disk 1.3 GB free; nothing regenerated; _staging/castle231 untouched.

## Slice 04:30-04:32 CT — lead ruling (a)+(b) APPLIED
- tools/castlegen.py: added plan_signature(v) = (plan, quad, keep_corner, moat_kind) + variety_collisions(); VARIETIES bl2 -> ("B","lord",5).
  md5 before d996c611bdb49e147250f7d3e4c96c7a (backup _garbage/castlegen.py.pre-bl2-*), after 7d20f3a07e9b6debd0e2f0432ddae755.
- NEW tools/test_castle_varieties.py (3 tests). RED on old table: collision (B lord 1, B lord 2, ('square',60,0,'dry')). GREEN after swap.
- Seed search: B lord 3,4 already used; seed 5 = first distinct: ('rect',56,3,'none'), square towers, curtain 9/14, mossy stone, thatch.
- Old bl2 (dir + tgz) moved to _garbage/CASTLE-pre/. New mvv_castle_bl5.tgz 1970296 B md5 bd51008b4192c95957a0d2eb4aaf0ed3 (64 files), raw dropped via pack_castle.
- castle_verify: CONSTRUCTED CORRECTLY (ward 20907/20907, rooms 42/42, beds 40/40, leaks 0, drains 79/79, R13 609737/609737/0).
- Renders _docs/castle/v0_4/mvv_castle_bl5-*.png; VIEWED plan-0 + under (top-down, gate side at top). vs bl1: no ditch ring, square towers,
  keep at lower-right (bl1 upper-right), well-head below keep. plan='rect' acts on the OUTER curtain for skin B (ring_points: inset d=int(192*0.08)=15 on the gate-rear axis): seen in the plan as outer ring top edge ~y65px / bottom ~y510px vs bl1 ~20/~555 (3 px/block -> ~15 blocks each side). Inner quad is always square (56 here vs 60).
- Elevation VIEWED (from the gate side): mossy-green curtain, 6 capped outer towers, central gate pair, keep rising behind right of centre. NOT done: plan-8/plan-13 not viewed; CASTLE-VARIETY-SHEET not regenerated (needs --all); stale bl2 PNGs still in v0_4/.
