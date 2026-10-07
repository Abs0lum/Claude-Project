# HANDOFF — 2026-10-05 — ROUND 1005: THE PALACE, THE GALLERY, THE CONNOISSEUR'S BOOK (+ castles v0.2 offline)

Authoritative CURRENT-STATE (newest handoff). Supersedes HANDOFF-2026-10-04-ROUND-1004b for ship status; everything in
1004b stays in force (round 1004b's packs are the base of these builds).

## 1. INSTALL SET (Drive: My Drive/ClaudeUploads — md5 in §7)

| pack | version | what it carries | needs |
|---|---|---|---|
| BP-02 AbsolutRealism Tectonic BP | **1.3.223** (replaces 1.3.222: its palace files were saved waterlogged) | the city palace (D-C570) · the gallery: 6,256 pw:art entities, the no-repeat registry, hanging at the furnished stage · the Connoisseur's Book (item + recipe + the texts: 6,256 essays, 1,791 lives) · the well's closed parapet (Q34) · everything in 1.3.220/221 | RP-01 1.3.123, RP-12 1.0.0 (full or LITE) |
| RP-01 AbsolutRealism Tectonic RP | **1.3.123** | the secret painting's four tiles, pw:jib_panel / pw:secret_painting sounds · everything in 1.3.122 | — |
| RP-12 AbsolutRealism Gallery RP | **1.0.0 (NEW)** | 6,256 framed JPEG textures (174 MB), 103 frame geometries, the art render controller, the book's icon and names | — |
| RP-12 AbsolutRealism Gallery **LITE** | 1.0.0 (built, not installed by default) | the same pictures at 128 px per block (56 MB) — his Q36 b: FULL everywhere; LITE only if the phone struggles; never both in one world | — |
| Markers BP 0.2.4 / Markers RP 0.2.3, RP-05 1.3.59, TestRunner BP 0.5.24 | unchanged from 1004b | | |

Order in the world: RP-12 anywhere in the resource stack (it only adds entity textures). Remove BP-02 1.3.220 / 1.3.222 when you
add 1.3.223 (same uuid, higher version — the game offers the swap). Full and LITE RP-12 have different uuids: never both. The gallery was first packaged as "RP-08" (that number is the ITEMS pack): the two RP-08-...-Gallery files on Drive are superseded — delete them; install RP-12.

## 2. WHAT'S NEW

### 2.1 The city palace (D-C570; his P1 city II, P2 life-size "lifelike and grand", P3 jib doors AND painting doors)
- 128 × 128 model (tools/palacegen.py v2) cut into four 64 × 64 pieces (sw se nw ne), five build stages each; laid as ONE
  rotated group with the gatehouse toward the square; the quarters rise in LOCKSTEP as the crown's works (wages from the
  treasury, never waiting for stock; PALACE_STAGE_DAYS 6 / 8 / 8 / 6).
- Rooms: gatehouse + guard room; court of honour with the fountain basin; the corps de logis — entrance hall, grand stair,
  the double-height great hall, council / audience / cabinet with the Tesoretto behind a painting; the hidden spine corridor
  with jib doors and bells; west wing — chancery, treasury + strongroom (behind the painting), judges' room with the
  wardrobe jib panel, bridge of sighs, archive, the prison tower; east wing — household offices, baize door, the two-level
  chapel, apartments and garrets; the service court — kitchen, scullery, larders, bakehouse, little commons, laundry,
  stables, smithy, well. 363 markers, 105 beds, 100 light blocks (v2: in the air of each storey — v1 buried 59 of them in
  the floor courses, and a light block has no collision: holes. LC-1005-10).
- The hidden world: pw:jib_panel (looks like panelling, no collision — walk through it) and pw:secret_painting (a 2 × 2
  gilt canvas on panelling, no collision — the door to the Tesoretto / the strongroom).
- Siting: at CITY II the crown's surveyors look 110..320 from the square for a free, dry, flat 128 × 128 block — a held
  ticking area (block ± 8) lets a site beyond your simulation distance be measured (up to six sites a day). A site is
  DRY when no water or ice stands at or above the floor level inside the block (two sample grids) or 8 cells outside it,
  and no ground 8 cells out rises 16 above the floor (a bowl). If 60 days find no dry site, the least-wet, least-bowl-like
  flat site is taken and the walls hold the water: the land job raises RETAINING WALLS to the water surface around the
  block (the height read from the outside column AND the piece's own edge column — a sleeping outside chunk no longer
  means "no wall"; the wall stands in the margin column outside the block AND in the piece's edge column, one block
  HIGHER than the water's surface, the read climbing through water plants), removes the standing water inside in one
  engine call per slab (a lake is infinite water: a slow drain never wins, LC-1005-14), clears naturals, fills hollows
  under the slab, lays the margin ring; then the PUMPS (60 daily passes: the walls re-checked, then all four quarters
  emptied in one tick) keep the block dry. Measured in the lake experiment: a wall at the surface or above holds a lake
  with 0 regrowth; a closed door holds; a doorway leaks a bounded puddle.
- The harness world is a mountain-lake basin: every candidate within 320 of the square is wet or a bowl. YOUR world's
  terrain decides where the palace stands — see §4 test 4.

### 2.2 The gallery (D-C571; his 21:30 / 21:39 / 22:01: thousands of unique works, every building)
- 6,256 public-domain paintings with CC0 images: National Gallery of Art 2,568 · the Met 3,234 · Cleveland 454; 1200–1900;
  provenance ledger _intake/art/catalogue.json (source, id, artist, title, date, medium, size, licence, URL, credit).
- Every building template has ART SLOTS (an offline wall scan: 376 slots in 43 templates; the palace ~70 per quarter by
  room — chapel religious, great hall and guard rooms history / mythology, council and chancery portraits, kitchens and
  commons still life / genre, garrets landscapes). At the furnished stage the clock hangs unique works (the registry never
  repeats one until the catalogue is spent); older finished buildings get theirs on a 200-tick sweep. Hanging is
  RESUMABLE: a spawn needs a ticking chunk; a building hangs what it can and finishes on a later sweep.
- One entity type per work (pw:art_<key>): facing bones, a hitbox the size of the frame, no gravity / collision / pushing.
  Frames: quarter-block classes, 1 block = 60 cm, period frames (cassetta / baroque gilt / ebony / plain), 256 px per
  block to 4 blocks (1024 px max), JPEG.
- The palace hangs only pre-1800 work (A4); towns hang anything 1200–1900 (his Q37 a).

### 2.3 The Connoisseur's Book (his A2)
- Craft: book + gold nugget (crafting table). Or `/give @s pw:connoisseur_book`.
- Use it ON a picture: title · artist (nationality, dates) · date, medium, size · collection · THE ARTIST (a life) ·
  THE WORK (what is shown) · READING IT (an interpretation — labelled as a reading) · A CRITIQUE (one critic's view) ·
  credit line + the museum's URL. Buttons: more by this artist · works hanging nearby.
- Use it in the air: the catalogue — works hanging nearby, by subject, by artist. An empty-hand tap shows the label.
- Texts: 6,256 essays (the 277 famous ones written with the picture in view and a web check; the rest from the facts,
  the NGA's own visual descriptions and Cleveland's curatorial texts) and 1,791 painters' lives.

### 2.4 The well's parapet (his Q34, 08:47–08:55: "it floats above the water" — the pillar IS a lone stone_brick_wall post)
- Four separate wall posts never read as a parapet (walls only fill in between neighbours). The ring now closes through the
  spruce posts' feet: eight `stone_brick_wall` blocks around the shaft, written WITH their connection states (Bedrock walls
  carry their connections as states and a structure-placed wall is never re-evaluated: corners as posts, sides as straight
  runs — civgen.wall_ring). The water stays flush with the paving inside the ring; the cauldron is the bucket. Template
  mvv_well_a_r1 + its five stages refreshed from the roster staging (build_bp02_221 build 16). Castlegen's ward well uses
  the same ring.

### 2.5 Castles — OFFLINE ONLY this round (D-C572; nothing of it is in 1.3.222)
- tools/castlegen.py v0.2 (two period skins, forced variety by seed, lord 128–160 / grand 224–288) and
  tools/castle_verify.py: an offline walk-audit that floods a castle model from outside the gate like a player and proves
  eight checks (every ward cell · every room · every bed · every tower floor · the wall-walk through the towers · the
  sealed gate keeps everyone out · no bare floor cell · every marker reachable). All eight sheet castles and two grand
  ones pass. Sheet: Drive ClaudeUploads/Sheets/CASTLE-VARIETY-SHEET-v0_2.png (reachable cells tinted green).
- Found on the way (LC-CASTLE-1): a one-wide diagonal wall-walk beside a parapet cannot be walked (the 0.6 player box
  pinches) — diagonal walks are two courses wide now.

## 2.6 1.3.223 — the root cause of the "flooded palace" (15:2x)
- palacegen saved EVERY cell of the four palace pieces and their 20 stage files WATERLOGGED (it passed the block's version
  number where the waterlogged flag goes). Every pane, door, ladder, slab and roof wedge was a hidden spring. Found by a
  5-minute "template or site?" probe (the pieces placed alone, in the air: 353 sources in 10 s). 1.3.223 = 1.3.222 with the
  palace regenerated dry (0 waterlogged cells, asserted by the build); the same probe now shows only the 17 water cells of
  the court fountain's basin. The lake-site theories of runs 9–18 were wrong attributions (lesson CORRECTIONS section).
- Gate 223-1 on the lake site: the palace DRY (1 water cell in 31,744 samples; every pump pass 0 / 0). It also showed a
  defect of build 17's wall check (it read the palace's own edge column — the building — and raised a stone curtain to
  roof height round the block); removed in 223 build 2. Gate 223-2 (= SHIPPED 1.3.223): the palace laid at day 197 on the
  lake site, four quarters in lockstep, DRY (4 sampled water cells in the whole block, from 18–46k in runs 2–18); gallery 347
  pictures, 0 repeats. The verify still differs from the model in ~1 % of sampled cells per quarter: the retaining wall's
  course in the edge column where the hill outside stands above the floor (by design of the stopgap), a few stair rotations
  (known), and on the ne quarter the two outer spruce doors read as air (witness item: are the palace's outer doors there?).

## 3. VERIFICATION (BDS; your eyes still rule — §4)
- Palace gates (221 runs 1–3, 222 runs 1–10): the engine walls hit on the way are lessons (LESSON-CANDIDATES-2026-10-05,
  LC-1005-1..11): the 10 s watchdog with QuickJS loops → light s0 + jobs; ~40 µs per placed cell; Block reads of unloaded
  chunks throw; spawns need TICKING chunks; `structureManager.place` skips unloaded chunks silently → every chunk probed;
  `getTopmostBlock` skips liquids → climb to the surface; a survey samples only inside the area it holds.
- Gallery gates: run 6–8 — 331–334 pictures in 40 buildings, 0 true repeats, the palace 70 × 4 = 280, the test ring 6/6,
  the text module (9.8 MB) loads: "[GALLERY] 6256 works, 1791 artists, 6256 texts, 1791 lives loaded".
- Static: node --check + ESLint clean on the clock and the gallery; every art slot list parses; 6,256 entity JSONs; the
  52 shipped templates hold 239 light blocks, 0 of them holes.

### 3.1 Gate runs 10 and 11 (the shipped build)
- Run 10 (build 11: light fix + survey fix + pumps; probe 0.0.31): the palace LAID at day 197 at (87, 397) rot 2 H 108 after
  a 30-day survey of 37 sites; four quarters in lockstep to furnished; gallery 330 pictures / 0 repeats / ring 6/6; 0 ERROR.
  Retaining walls where the lake stands (sw 334, ne 34 blocks; se 1, nw 0 — lower ground there, 11–14k cells filled); the
  pumps converge (sw 432 → 7197 → 182 cells a pass; se 10077 → 18300 → 6) — the verify ran while two land jobs were still
  running and read 26,667 sampled water cells → probe 0.0.32 waits for a dry read before verifying.
- Run 11 (build 12: + the well's parapet; probe 0.0.32): the well's ring verifies (states kept); palace laid day 197 at the
  same site; lockstep done; the dry loop read 7–9k sampled water cells for 20 days: the nw quarter had 0 retaining blocks —
  its OUTSIDE columns slept at land-job time — and the lake refilled it at ~26k cells a day (LC-1005-13).
- Run 12 (build 13: the wall height from the inside edge column too, re-checked on every pump pass, 60 passes): the walls
  held (nw +331 blocks on a later pass, nothing needed afterwards) and still every quarter refilled 20–27k cells per pass:
  INFINITE WATER — the lake regrows inside faster than a cell-by-cell drain (LC-1005-14).
- Run 13 (build 14: the water removed atomically with /fill … replace): the fills "succeeded" without an exception and
  removed nothing — the quarter's chunks were partly asleep at pump time and `runCommand` reports that only through
  successCount (LC-1005-15). A 10-minute FILLTEST probe proved every /fill form works from a script in a held area and that
  a partial removal regrows in two seconds.
- Run 14 (build 15: the daily pump holds the quarter's area, waits, fills, counts successCount): the fills work (4 slabs
  a pass) and ~8k cells return within seconds — the stages re-open the wall in the piece's edge column where the template
  has its front doors and the carriage arch, and quarters drained minutes apart regrow from each other.
- Run 15 (build 16: the wall also in the margin column OUTSIDE the block, all four quarters drained in one tick): the drain
  is whole and instant, the outside wall rose — one block high, because the margin ring reads dry while the lake begins a
  cell further out and pours over it.
- Run 16 (build 17: the wall takes the highest water surface 1–8 cells out): still wet — the region dump, audited column
  by column (tools/palace_water_audit.py), showed the east wall one block short of the lake's surface (119 under 120):
  the lake stepped over it onto the cornice, fell inside, and the palace's own walls held it like a tank (rooms to the
  ceilings at y 127, a tower to 131); the pumps emptied it every pass and the gap refilled it. His 12:12 rule (one block
  higher than the water) + the LAKE and FLOW experiments (LC-1005-16) settled the mechanics.
- Run 17 (build 18: wall = surface + 1): the +1 wall grew a block every pass (read as its own top; fixed in build 19:
  +1 only over water) and the block stayed wet; the dump's water-surface map showed the inside water (127–135) standing
  ABOVE the outside (120 at the margin, ~90 beyond) — fed from above the box's top. Build 20: the drains reach the
  clearing height (box top + 24 rows), all four quarters in one tick.
- Run 18 (build 20 = SHIPPED): town, gallery (327 pictures, 0 repeats, ring 6/6) and book pass; the palace laid at day
  197 and raised in lockstep; the block STILL reads wet (~3k sampled cells return after every full drain). The mechanism
  at this mountain-lake-and-pond site is NOT found yet — the open item of this round (§6 item 0, D-C573). The walls and
  drains do no harm on a dry site. His 14:00 ruling: believe what we have after run 18; stop AND move water next.

## 4. YOUR TESTS (witness)
1. Load a world with the three packs. Content log: no "Missing referenced" lines for pw:art_* or pw_frame_*. (Expect load
   errors first — send me the content log; the entity count is new ground: 6,256 client entities.)
2. `/scriptevent pw:gallery test 6` — six framed pictures appear around you facing in. LC-GAL-2 (JPEG textures render)
   and LC-GAL-3 (north / west faces not mirrored — look for a reversed signature or text) are decided here.
3. Craft the book (book + gold nugget); tap a picture with it → the essay; tap with an empty hand → the label.
4. Grow a city: `/scriptevent pw:clock village` → `grow` ×8 (to city II) → `skip 40` → the chronicle says "the SEAT OF
   GOVERNMENT is laid out"; `skip 30` more → the quarters rise; walk it (jib doors, the painting door, the first floors —
   no holes). Then `/scriptevent pw:gallery status` — the palace alone should hold ~280 pictures. If the chronicle says
   "the crown's surveyors found no ground" for many days, tell me where the city stands (terrain, water).
5. Memory / stutter when a new room's pictures first render (LC-GAL-1, lazy texture loading) — PS5 first, then the phone.
6. Pictures in ordinary houses (cottages 2, inns 8, manors 16): are they at eye level, never on the floor, never clipping a
   window or a door?

## 5. QUESTIONS — answered 08:43 CT 10-05 (his file, 63 lines)
Q36 b (FULL RP-12 everywhere; LITE only if the phone struggles) · Q37 a (towns hang 1200–1900) · A3 a · K1 b (moat by
seed) · K2 b (a separate paid guard body recruited over time, never summoned) · K3 a (four towers) · K4 c · K5 a (paid
household) · K6 a (gate to the square) · K7 b (the academy also founds a rare academy city) · K8 b (BDS walk test) ·
Q32 a · Q33 a · Q35 b (R-55 re-bake next round). Q34 answered 08:55 (the lone wall post) — fixed in this build (§2.4).

## 6. DOCKET (next = round 1006, BP-02 1.3.223)
0. D-C573 WATER IS MOVED, NOT STOPPED (his 13:56 law): a pond or lake touching a site is captured into a designed
   cascade / fountain / grotto in the grounds and channelled down to the sewer level and out the outfall; palaces get
   several sewer entrances (court drains, kitchen and stable yards, the well, the basin's overflow); EVERY template gets
   a drain line under its floor to the street's trench (the well's shaft is the model). The retaining walls + the atomic
   drain in 1.3.222 are the stopgap that keeps a palace dry until this is built. Built together with the castles' sewers.
1. CASTLES in the clock: the castle at town III (castle-first founding mode + castle added to a grown town), the grand
   castle-palace at city III, the survey in two held halves (a 256 block exceeds one 10 × 10-chunk area), kit blocks
   (portcullis, machicolation), the garrison as a paid body recruited over time (K2 b), the castle household (K5 a),
   academygen (original academy-castle 256+, the summon AND the rare academy city, K7 b), the BDS walk test (K8 b). Design:
   CASTLE-PROGRAM-DESIGN-2026-10-05.md.
2. The grand castle-palace program inside the inner ward (the palace's ranges: great chamber, council, chancery, lodgings
   ranges, the chapel royal) — castlegen "grand" still lays the lord's program on a bigger plot.
3. Public servants in the palace (treasurer, chancery clerks, constable, porter, steward, cooks, guards) as paid offices.
4. A template-wide "hole census" (light blocks / no-collision blocks in walkable courses) in the verification suite (S).
5. The R-55 inner-crown re-bake (his Q35 b); R-57 root-block texture-array warnings; the probe's lectern manifest; the
   pace A/B run; texture sets for vanilla leaf keys under VV; the secret painting could carry a real famous work.

## 7. DELIVERY (Drive ClaudeUploads; md5 == local, verified twice)
| file | bytes | md5 |
|---|---|---|
| **BP-02-AbsolutRealism-Tectonic-BP-v1_3_223.mcpack** | 13,303,441 | 909db86a7f7778b1f29c6e0c571aec42 |
| RP-01-AbsolutRealism-Tectonic-RP-v1_3_123.mcpack | 138,767,246 | 9b1f512f1e45a56fe837147712ee8221 |
| RP-12-AbsolutRealism-Gallery-RP-v1_0_0.mcpack | 174,492,818 | c4e08e51fba13bfb313bd6347a7c2048 |
| RP-12-AbsolutRealism-Gallery-LITE-RP-v1_0_0.mcpack (optional, never with the full one) | 55,621,987 | 018fd464ecb7af13cc8ba06a5c755c0d |
| Sheets: CASTLE-VARIETY-SHEET-v0_2.png (ClaudeUploads/Sheets) | 110,791 | 87478a7860d1cb3ebf9c8518d44518c2 |
Superseded on Drive (delete): BP-02-AbsolutRealism-Tectonic-BP-v1_3_222.mcpack (waterlogged palace + the stone curtain),
RP-08-AbsolutRealism-Gallery-RP-v1_0_0.mcpack and RP-08-AbsolutRealism-Gallery-LITE-RP-v1_0_0.mcpack.

## 8. FILES
tools/palacegen.py (v2) · tools/palace_light_s0.py · tools/build_palace_blocks.py · tools/build_bp02_221.py (build 24) ·
tools/build_bp02_222.py (build 20) · tools/bp02_src/pw_gallery.js · tools/art_harvest.py · tools/art_catalogue.py ·
tools/art_slots.py · tools/art_essays.py (+ _intake/art/essays/PROMPT-*.md) · tools/build_rp12_gallery.py ·
tools/castlegen.py (v0.2) · tools/castle_verify.py · tools/civgen.py (wall_ring) · tools/civ_roster.py (the well) ·
tools/palace_water_audit.py · tools/filltest_probe.py · tools/laketest_probe.py · tools/flowtest_probe.py · tools/build_rp12_gallery.py ·
tools/kit_village_probe_030.py / _031.py / _032.py ·
tools/package_round_1005.py · _docs/LESSON-CANDIDATES-2026-10-05.md · _docs/CASTLE-PROGRAM-DESIGN-2026-10-05.md ·
_docs/GALLERY-SYSTEM-2026-10-05.md · _docs/palace/GALLERY-CENSUS.md · _logs/decision_journal.md (D-C570..D-C572)
