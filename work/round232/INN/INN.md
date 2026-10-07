# INN — BP-02 1.3.232: keep the old inn (r1), new mixed-room inn as its own family (r2)

Worker TAG `INN`, GitHub Claude Code session, 2026-10-07. Base: round-231 source
`work/inbox-2026-10-07-1714/bp02-231-src/`; workspace `scratchpad/w232-INN/`. Ruling D-GH1007-INN
(`work/RULINGS-2026-10-07.md`): "Mix of 2- and 4-bed rooms; KEEP existing inns", plus the earlier rule (his 00:23 CT):
beds 1 block apart, at least 6 rooms.

## Bottom line
- **r1 is the 1.3.230 inn again.** The 4 `pw:mvv_inn_{a..d}_r1` entries in `pw_civ_buildings.js` are the 1.3.230 text,
  byte for byte. The 32 old r1 structure files must be copied into the 1.3.232 pack from the 1.3.230 pack. The paths
  and md5s are listed below, and copies are in `INN-files/restore-r1/`.
- **The new inn is `pw:mvv_inn_{a..d}_r2`.** It has 12 rooms per inn: 8 rooms with 2 beds and 4 rooms with 4 beds, 32
  beds in all. Beds are exactly 1 block apart, and every room has its own door. It was generated offline with the
  changed `inn_v2.py`. I read the 32 written structure files back and checked them independently: PASS.
- **Only new plots become r2.** `familyOf` / `skinsOf` now resolve the kind `inn` to r2. A building's family id is
  stored on the building when its plot is laid and is never resolved again, so inns already standing or staged stay r1.
  `short()` / `skinOf()` now accept any `_r<n>`. Without that change an r2 inn would not count as an "inn" (no keeper,
  rota, guests or "Rent a bed").
- **Inn bed counts:** every script reads the count from the inn's own family (`bedsOf(BUILDINGS[b.family].dir)`).
  None is hard-coded, so nothing in the scripts needed changing. New tests show a kept r1 inn lodging 3 guests and an
  r2 inn lodging 31.
- **Tests:** 33/33 suites pass, `node --check` passes on 46/46 scripts. test_inn24 went from 57 to 103 checks;
  test_shifts is 90/90 with the corrected bed line.

---

## 1. Restore r1 (the pre-231 inn)

### 1.1 What 231 changed (230 table vs 231 table, parsed and compared field by field)
Both tables have 43 entries in the same order. **Only the 4 inn entries differ**, in 7 of their 11 fields:

| field | 1.3.230 (r1, kept) | 1.3.231 (r1 name, new building) |
|---|---|---|
| size | [11, 30, 10] | [17, 34, 13] |
| door | [0, 0, 4] | [0, 0, 7] |
| work (stations) | 5 | 6 |
| dir: beds | 4 (`direction` 1, feet 4) | 32 |
| bom s0..s4 | stone 497 · timber 32 + planks 249 · planks 186 + glass 15 + stone 14 · thatch 98 · planks 43 | stone 914 · timber 84 + planks 744 · planks 603 + glass 40 + stone 20 · thatch 203 · planks 111 |
| chests | 2 barrels on the ground floor, 4 chests upstairs, cellar | 3 barrels, cellar |
| art | 8 slots | 8 slots (other places) |
| unchanged | stem, datum_y 15, stages 5, lids [[1,-1,3,1]] | |

### 1.2 What I restored
- `pw_civ_buildings.js`: the 4 r1 entries were replaced as text by the 1.3.230 text (`tools/splice_inn_table.py`,
  json `raw_decode` spans). Checks:
  - each r1 entry's md5 equals the 1.3.230 entry's md5 (a `ada16757`, b `9b389a38`, c `b7a7399d`, d `d0a8ac46`);
  - the other 39 entries equal 231's;
  - the 4 r2 entries equal the generator's JSON;
  - the new table has 47 entries, md5 `7e46aa712c50adc2eed357749c92b059`.
- **Structure files to restore in the 1.3.232 pack.** Copy these from `scratchpad/bp02-230/` (BP-02 1.3.230, manifest
  [1,3,230]) into the same paths. They replace round 231's big-inn files under the r1 names. Copies are in
  `out232/INN-files/restore-r1/BP-02/` (copy md5 equals the pack's md5, 32/32), with `MD5SUMS-r1-from-1.3.230.txt`:

```
7584639f106cef48163603e425405d0d  structures/pw/mvv_inn_a_r1.mcstructure
42c8391fb15c140f43e5c64972507fc1  structures/pw/mvv_inn_b_r1.mcstructure
f48a299a1984c81cb83e0267cd760641  structures/pw/mvv_inn_c_r1.mcstructure
dd26ea2a296a2e9e23001d65cfa6401e  structures/pw/mvv_inn_d_r1.mcstructure
5a39c63a9c4cc2f6099f1737739f0e45  structures/pw/stages/mvv_inn_a_r1_r.mcstructure
9e61be4264a7599484d7f56321f44632  structures/pw/stages/mvv_inn_a_r1_s0.mcstructure
da0fa0a491ffb50558bacda35127ab29  structures/pw/stages/mvv_inn_a_r1_s1.mcstructure
e96e28bbab1f079ad7aa7839e3a9292e  structures/pw/stages/mvv_inn_a_r1_s2.mcstructure
0c80178c46802e9c91f12d983ea66eca  structures/pw/stages/mvv_inn_a_r1_s3.mcstructure
4eb334d4ec282cca3d96f7c764cd111f  structures/pw/stages/mvv_inn_a_r1_s4.mcstructure
0df6781d8b7dd353ac2bf8ac76b1727f  structures/pw/stages/mvv_inn_a_r1_w.mcstructure
5a39c63a9c4cc2f6099f1737739f0e45  structures/pw/stages/mvv_inn_b_r1_r.mcstructure
9e61be4264a7599484d7f56321f44632  structures/pw/stages/mvv_inn_b_r1_s0.mcstructure
8761b722f626ac8f059edb161211615c  structures/pw/stages/mvv_inn_b_r1_s1.mcstructure
ada441796c657987c1a005c43d0c12e9  structures/pw/stages/mvv_inn_b_r1_s2.mcstructure
ff357b78898a59fdd48b7c076523f116  structures/pw/stages/mvv_inn_b_r1_s3.mcstructure
d36cd0cb603c5e461dad936173f12816  structures/pw/stages/mvv_inn_b_r1_s4.mcstructure
0df6781d8b7dd353ac2bf8ac76b1727f  structures/pw/stages/mvv_inn_b_r1_w.mcstructure
5a39c63a9c4cc2f6099f1737739f0e45  structures/pw/stages/mvv_inn_c_r1_r.mcstructure
9e61be4264a7599484d7f56321f44632  structures/pw/stages/mvv_inn_c_r1_s0.mcstructure
44e217d0b8f8eb3a02bb1ca0b714ccf2  structures/pw/stages/mvv_inn_c_r1_s1.mcstructure
efb0d8c01bb1c5020b8a05da18a8f7ce  structures/pw/stages/mvv_inn_c_r1_s2.mcstructure
ff357b78898a59fdd48b7c076523f116  structures/pw/stages/mvv_inn_c_r1_s3.mcstructure
dce50c14dffdffd218209bcc519123ed  structures/pw/stages/mvv_inn_c_r1_s4.mcstructure
0df6781d8b7dd353ac2bf8ac76b1727f  structures/pw/stages/mvv_inn_c_r1_w.mcstructure
5a39c63a9c4cc2f6099f1737739f0e45  structures/pw/stages/mvv_inn_d_r1_r.mcstructure
9e61be4264a7599484d7f56321f44632  structures/pw/stages/mvv_inn_d_r1_s0.mcstructure
ccd489244df098209949dca1624f84bf  structures/pw/stages/mvv_inn_d_r1_s1.mcstructure
4f167403ec8ca4492538cbb252dda27e  structures/pw/stages/mvv_inn_d_r1_s2.mcstructure
0c80178c46802e9c91f12d983ea66eca  structures/pw/stages/mvv_inn_d_r1_s3.mcstructure
d36cd0cb603c5e461dad936173f12816  structures/pw/stages/mvv_inn_d_r1_s4.mcstructure
0df6781d8b7dd353ac2bf8ac76b1727f  structures/pw/stages/mvv_inn_d_r1_w.mcstructure
```

- Read back from the 230 files: every r1 template is 11×30×10 with 8 bed cells (4 beds), which matches the restored
  table.
- **Pre-existing in 1.3.230 (left as it shipped):** the table's s0 bill says stone 497, but the files count 496. The
  1.3.219 build patched the files after the table was made: it opened the sewer port at x 0, feet −12/−11, at the shaft
  column (`build_bp02_219.py` l.82–90). Every 230 building file carries that patch (bakery, cottage_m, town_hall and
  manor checked against a fresh regeneration). I restored the 230 pair (table + files) unchanged.

## 2. The new family r2 (mixed rooms)

### 2.1 Naming (the house convention)
- Naming law `pw:<tier>_<type>_<variant>_r<n>`, from AUTHORING-WORKFLOW-v1 as summarised in
  `knowledge/logs/decision_journal.md:2522` (D-C456).
- The handoff already named the alternative "keep old (`r2` family)"
  (`knowledge/current/HANDOFF-2026-10-07-1130.md:158`), and the ruling says "new inn = a new structure family (r2)".
- Skins keep the variant slot (`_a.._d_`), so the ids are `pw:mvv_inn_{a,b,c,d}_r2`. Stages follow the same pattern:
  `pw:stages/mvv_inn_X_r2_s0..s4`, `_w`, `_r`.

### 2.2 Final rooms/beds table (both guest floors identical, feet 4 and feet 8)
Shown from above: north (local −z) at the top, the street (x = 0) on the left. The shell is unchanged from round 231:
17 deep × 12 front, door at z 7, taproom, cellar, ladder at x 15 z 6.

| side | room (x span) | beds | bed head x | door (x, wall z) | partition east of it |
|---|---|---|---|---|---|
| north z 2..4 | x 1..7 | **4** | 1, 3, 5, 7 | (4, 5) | spruce log x 8 |
| north | x 9..11 | **2** | 9, 11 | (10, 5) | spruce log x 12 (new) |
| north | x 13..15 | **2** | 13, 15 | (14, 5) | outer wall |
| south z 9..11 | x 1..3 | **2** | 1, 3 | (2, 8) | spruce log x 4 (new) |
| south | x 5..7 | **2** | 5, 7 | (6, 8) | spruce log x 8 |
| south | x 9..15 | **4** | 9, 11, 13, 15 | (12, 8) | outer wall |

**Per inn: 2 floors × 6 rooms = 12 rooms = 4 × 4-bed + 8 × 2-bed = 32 guest beds.** Round 231 had 8 rooms × 4 beds,
also 32.
- Bed cells are exactly round 231's: heads against the outer wall, foot one cell in, aisle at the foot.
- A 2-bed room is half of a 4-bed room's span, divided by a log partition in the free column between its 2nd and 3rd
  bed.
- Changes from round 231: 4 partition columns (+36 timber), 4 more doors, 4 fewer windows (the partition columns), and
  4 more lights (one per room).

**ASSUMPTION (232):** the mix splits the beds evenly (16 in 4-bed rooms, 16 in 2-bed rooms) and both floors are the
same. The ruling does not give a ratio, so his confirmation is needed (see §6).

### 2.3 Generator changes (`INN-inn_v2.py.diff`, `INN-civ_variants.py.diff`)
- `inn_v2.py`:
  - `SIDE_ROOMS` table (x0, x1, beds) per side, plus `SIDE_DOOR` and `SIDE_BED`.
  - `guest_floor` lays partitions, doors, beds, windows and lights per room.
  - `inn2(name="pw:mvv_inn_a_r2")`.
  - `check_rooms` is now the stricter ruling test: ≥ 6 rooms; every room exactly its planned 2 or 4 beds; both sizes
    present; heads exactly 2 apart with no bed in the gap; a full-height partition between rooms; a door per room;
    ladder and corridors clear.
  - `main()` prints the rooms table and uses r2 names.
  - md5 `ffd3684c…`.
- `civ_variants.py`, one line: `b.name.replace("_a_r1", f"_{skin}_r1")` → `re.sub(r"_a_(r\d+)$", rf"_{skin}_\1", …)`.
  Mechanism: with the old line, `pw:mvv_inn_a_r2` never matched, so skins b, c and d would all have been written as
  `mvv_inn_a_r2` and overwritten each other (checked). Names for every r1 building are unchanged. md5 `5d17a5f9…`.
- No other tool changed: `civ_roster`, `civgen`, `civ_stages`, `civ_village_data`, `art_slots`, `weather_overlays`,
  `mcstructure` and `build_bp02_219` are byte-identical to `knowledge/tools/`.

### 2.4 Running offline (it runs here)
`tools/run_inn_offline.py TOOLS_DIR STAGE_ROOT TEMPLATE [--sewer-port]` imports the copies in `$W/tools/` and
re-points only the module globals that hold `/home/claude/...` paths.
- **Missing input:** civgen's `tools/civ_templates/engine_entities_probe.nbt` is not in the mirror. civgen only
  deep-copies one `pw:marker` and one `pw:hatch_lid` compound from it, then overwrites Pos, UniqueID, Tags,
  definitions and properties. The runner takes those two compounds from the 1.3.230 `mvv_inn_a_r1.mcstructure`, which
  civgen itself cloned from that probe.
- **Proof the substitute is faithful:** the unmodified round-231 `inn_v2.py` run this way reproduces the 4 shipped 231
  table entries byte for byte (4/4 entries, all 11 fields).
- **`--sewer-port`:** applies the 1.3.219 law to the written r2 files (`build_bp02_219.fix_structure`, imported
  unchanged). The law: "the shaft's street-side opening reaches down to the gallery floor (local x0, y3–y4 opened) in
  every template and stage".
  - Every 230 building carries it.
  - Round 231 copied the inn v2 files from staging without it (`build_round_231.py` l.333–336, a plain `put`).
  - Result: 16 port cells (4 skins × template + s0 × 2 cells), 0 door cells. The r2 table's bom is pre-patch, the same
    convention as every 230 entry (s0 +1 smooth stone).
- Outputs in `out232/INN-files/`:
  - `BP-02/structures/pw/mvv_inn_{a..d}_r2.mcstructure` and `stages/mvv_inn_{a..d}_r2_{s0..s4,w,r}` (32 files, md5 in
    `MD5SUMS-r2.txt`)
  - `civ_inn/CIV_BUILDINGS-inn.json` and manifests
  - `renders/INN-V2-PLAN-f{-5,0,4,8,12}.png`
  - `scripts/pw_civ_buildings.js` (the spliced table)
  - `tools/` (the changed and new tools)
  - `VERIFY-r2.txt`

### 2.5 Read-back verification (`tools/verify_inn_r2.py`, independent of `SIDE_ROOMS`) → `INN-files/VERIFY-r2.txt`
For each skin's finished file, and for its stages s0..s4 re-assembled:
- every bed cell pairs with its head or foot;
- rooms are found by flood fill of the open cells on each guest floor, with walls, logs, doors and glass as borders;
- room sizes, head spacing, the gap cells clear at feet f..f+2, one door per room, and a `bed` station marker on each
  of the 32 heads.

Result, all 4 skins: **32 heads, 12 rooms (8 × 2-bed, 4 × 4-bed), stages == finished, 32 markers on heads → PASS;
rooms identical across skins.** The plan renders f4 and f8 were viewed at full resolution. Literally: north row beds at
x 1,3,5,7 | log x 8 | 9,11 | log x 12 | 13,15; south row 1,3 | log x 4 | 5,7 | log x 8 | 9,11,13,15; doors at
(4,5) (10,5) (14,5) (2,8) (6,8) (12,8); ladder at (15,6).

## 3. The planner: r2 for NEW inns only

### 3.1 Mechanism (base 231, file:line in the workspace)
- Every planner path picks a family for a new plot through `familyOf(kind, skin)` and `skinsOf(kind)`
  (`pw_civ_clock.js:2621`, `:2636`). These had a fixed `_r1` (base l.2613–2616, 2621).
- Call sites, all of them new plots:
  - founding: 2661–2662, 3074–3075, 4644–4650, 5361–5362
  - tier charter: 2001–2008
  - leftovers / civic: 2348–2350, 2380–2382, 2399–2400
  - shortage charter: 2316–2317
  - trade branch: 7812–7813
  - immigrate: 8337–8338
  - `plot` / `plotat`: 8266
  - planning and bill reads: 1983, 2163, 7088, 8177, 8223
- The id lands on the building record (`{ id, family, … }`, e.g. l.1951, 2667, 3085) and is saved as a string inside
  the building objects (`pw_civ_save.js` groups buildings by settlement and has no family codec). No code re-resolves
  `b.family`. There is no upgrade or renovation path; `grep -i "upgrad|renovat|\.family ="` finds only `c.family` for a
  leftover cursor that has not been laid yet.
- So a revision table read by `familyOf`/`skinsOf` makes new inns r2 and leaves standing or staged r1 inns as they are.
  The condition is that the r1 entries and files stay in the pack, which §1 ensures.
- `short()` and `skinOf()` (`:2518–2519`) stripped only `_[a-z]_r1$`. For an r2 stem, `short()` would return
  `inn_a_r2`. `short()` has 75 call sites, including HOUSEHOLD, the shop's `TRADE[...]` keeper hire, the INN24 rota and
  guests, "Rent a bed", the economy's `kind === "inn"` sales, and DISTRICT. An r2 inn would have been invisible to all
  of them. `kindOfFamily` (l.4943) and l.4581 already used `_r\d+$`.

### 3.2 Changes (`pw_civ_clock.js`, each marked `// 1.3.232 (#INN)`)
- l.2518–2519: `short` / `skinOf` now use `_r\d+$`.
- l.2520: `revTag(b)` shows `" r2"` for a family past r1. The status line (l.2604) now reads `#N inn/a r2`; every r1
  line is unchanged. This exists for the in-game check.
- l.2612: `const NEW_REV = { inn: 2 }`. l.2615: `revOf(nm)` reads NEW_REV (also for `inn_b`), and falls back to 1 when
  `pw:mvv_<kind>_a_r<n>` is missing from the table, so a plot is never laid for a family that does not exist.
- l.2621 / 2636: `familyOf` and `skinsOf` use `_r${revOf(kind)}`. An explicit id such as `pw:mvv_inn_b_r1` is still
  taken as given, so `plot pw:mvv_inn_a_r1` still lays the old inn.
- l.8176: `prio` accepts r1 or r2 ids.

### 3.3 Inn bed counts (rota, "Rent a bed", lodging)
| user | file:line | source of the count | change |
|---|---|---|---|
| tonight's guests + bill | `pw_civ_shop.js:303` (innNight; def = `API.BUILDINGS[inn.family]`, l.101) | `bedsOf(def.dir)` | none; per family |
| clock restGoal (homeless → inn bed) | `pw_civ_clock.js:8709` | `bedsOf(BUILDINGS[inn.family].dir)` | none |
| homeRoom capacity | `pw_civ_clock.js:898/908` | `bedsOfFamily(b.family)` (only with `PLACES.BEDS_BASE`, off) | none |
| inn room for the unhappy | `pw_civ_clock.js:8753` | `INN.perStation × work` (stations: r1 5, r2 6) | none |
| rota / cover hiring | `pw_civ_people.js:1153–1190` | staff count and the inn's vacancies (from `work`) | none |
| "Rent a bed" | `pw_civ_shop.js:285` | no bed count: price `INN24.bedP` (24 p), "any free bed upstairs" | none (see §6 e) |
| `bedsOf` | `pw_civ_people.js:1260` | bed cells / 2 | none |

## 4. Tests (TDD: written first; red on the base, green after)
- On the base: test_inn24 **61/78** with 17 new checks failing (r1 ≠ 230, no r2, `familyOf("inn")` gave r1, `short`
  of r2); test_shifts **89/90**.
- `tests/test_shifts.mjs` j (l.304): beds cottage_s 1, **inn r1 4 (kept), inn r2 32 (new)**, manor 11.
- `tests/test_inn24.mjs`:
  - **§8, the table:** each r1 entry's md5 equals 1.3.230; r1 is 11×10, door z 4, 5 stations, 4 beds. r2 exists per
    skin. From the table's own directional cells (bed pairs, log partitions, doors): 32 beds; ≥ 6 rooms, each 2 or 4
    beds, both sizes present; exactly 8 × 2-bed + 4 × 4-bed; neighbours 2 apart; a door per room; the 17×13 shell.
  - **§9, the family choice:** `NEW_REV`, `short`, `skinOf`, `revTag`, `revOf`, `familyOf` and `skinsOf` are cut from
    `pw_civ_clock.js` and run against the real table. A new inn gets r2 for any skin; the skins are counted in r2; an
    explicit r1 id is kept; every other kind gets r1; `short()` gives "inn" for both revisions and strips the revision
    from all 47 families; `revTag`; a table without r2 falls back to r1.
  - **§10, beds per family:** `innNight` with the real defs, 41 people, 1 resident: r1 gives 3 guests (3 × 24 p), r2
    gives 31 (31 × 24 p).
  - Total 57 → **103** checks.

## 5. For the 1.3.232 packager
1. Scripts: `pw_civ_buildings.js` (md5 `7e46aa71…`, 482,515 B), `pw_civ_clock.js` (this item's hunks), tests.
   `INN.diff` covers the 4 files. The table line is 480 KB, so the diff holds the whole old and new line; the same
   table is also in `INN-files/scripts/`.
2. Structures:
   - restore the 32 r1 files above from bp02-230 (they replace round 231's);
   - add the 32 r2 files from `INN-files/BP-02/structures/pw/` (`MD5SUMS-r2.txt`).
   - Do NOT re-run round 231's inn step (`build_round_231.py` l.294–296/333–336 globs `mvv_inn_*_r1` from blocks231).
3. No new blocks or states, so the permutation count does not change. Block ids are all lowercase vanilla/`pw:`.
   No RP change.
4. The other 1.3.232 items also edit `pw_civ_clock.js`. My hunks are local: l.2518–2520, 2604, 2608–2639, 8176.

## 6. Open questions / what only he can confirm
a. **Did 1.3.231 ever run in a world of his (PS5, phone or Realm) where an inn was laid or built under 231?**
   - If yes: that inn has the id `pw:mvv_inn_X_r1` but the 231 shape (17×13, 32 beds). In 1.3.232 the r1 table
     describes the small inn (door z 4 instead of z 7, stations, 4 beds).
   - Worse, a council repair (`_r` overlay) or a restore would place the small inn's stone over the big one. The r1
     cellar walls at x 10 and z 9 would close across the big inn's cellar.
   - If no world ran 231 with an inn, nothing is needed. If one did, a migration for those inns is a separate item; I
     wrote no speculative code.
b. **The mix:** is an even split (16 beds in 4-bed rooms, 16 in 2-bed rooms, 8 + 4 rooms) and the same layout on both
   floors right? Or would he prefer e.g. one floor of 2-bed rooms and one floor of 4-bed rooms?
c. **Ladders or real stairs** inside the inn (open since handoff 1130 §5). r2 keeps round 231's ladder at x 15 z 6.
d. Edge case: a plot the clock chose but had not laid at the moment of the update keeps r1 and would still build the
   old inn. That is a tier charter `st.tierWork`, laid one item per kit beat, or a leftover cursor `st.leftCursor`
   mid-search. Both windows are seconds long. Leftover names (`st.leftover`) resolve at lay time, so they get r2.
e. "Rent a bed" never checks for a free bed (pre-existing since 231). At a kept r1 inn, with 4 beds and 3 homeless
   guests a night, the player is told "any free bed upstairs" when the beds are virtually all taken. Physical beds are
   free because the guests stand inside the door. Should "Rent a bed" say "full" when beds − residents − guests ≤ 0?
f. New inns are bigger (17×13 instead of 11×10; the bill for s1..s4 is about 1,845 units instead of 637). This holds
   for the founding village's inn too, so it needs a bigger lot and bigger founding wagons. Round 231 was the same for
   every inn.

### In-game test (his PS5; static checks only rule things out)
Use a COPY of a world that has an old inn. `skip` advances every town in the world.
```
/scriptevent pw:clock status
```
→ every existing inn reads `#N inn/<skin> (…)` with **no** ` r2`. Walk in: the 11×10 two-storey inn, 4 beds upstairs,
as before 1.3.231.

Then stand on open flat ground (the plot starts 2 blocks east of you):
```
/scriptevent pw:clock plot inn
/scriptevent pw:clock skip 7
/scriptevent pw:clock status
```
→ the reply names `pw:mvv_inn_a_r2`, and status shows `#M inn/a r2 … furnished`. Climb the ladder at the back (x 15).
On each guest floor you should see 6 doors off the corridor. Stand in the corridor facing the street door (the front),
with your back to the ladder:
- on your RIGHT: one 4-bed room nearest the street, then two 2-bed rooms toward the ladder;
- on your LEFT: two 2-bed rooms nearest the street, then one 4-bed room toward the ladder;
- in every room, one block of floor between beds.

(Facing declared: you face local −x, toward the street. With no rotation that is world west, so your right is north,
local −z, the z 2..4 side. A rotated plot turns the whole inn, and the left/right read holds because structures are
never mirrored.)

Optional: `/scriptevent pw:clock plot pw:mvv_inn_a_r1` still lays the old inn.

---

## 7. Final full test run (`work/test-harness/run_civ_tests.sh $W`; `node --check` on every script, 46/46, no SYNTAX FAIL; rc 0)
```
test_alarm: test_alarm (b): 17 pass, 0 fail
test_band: test_band: 51/51 passed
test_beat: test_beat: 116/116 passed
test_canopy: test_canopy: 5/5 passed
test_coins: test_coins: 810/810 passed
test_court: test_court: 37/37 passed
test_diet: test_diet: 8/8 passed
test_doorramp: 14/14 PASS
test_econ228: test_econ228: 1195/1195 passed
test_fell: test_fell: 31/31 passed
test_frontage: test_frontage: 12/12 passed (houses: ramp-aware 13, flat-only 0, cesspit 13, ramps 13)
test_households: test_households: 95/95 passed
test_hygiene: test_hygiene: 15/15 passed
test_inn24: test_inn24: 103/103 passed
test_landclock: test_landclock: 25/25 passed
test_lanes: test_lanes: 14/14 passed (lane 101 cells, 5 legs, turns 4)
test_leisure: test_leisure: 27/27 passed
test_market: 16/16 passed
test_names: test_names: 48/48 passed
test_needs: test_needs: 80/80 passed
test_occupied: test_occupied: 97680/97680 passed
test_plan: test_plan: 37/37 passed
test_plateau: test_plateau: 76/76 passed
test_player: test_player: 71/71 passed
test_ramp8: test_ramp8: 7/7 passed
test_rampclear: rampclear force: 9 pass, 0 fail
test_route: test_route: 468/468 passed
test_save: test_save: 40/40 passed
test_shifts: test_shifts: 90/90 passed
test_survey: test_survey: 25/25 passed
test_talk: test_talk: 48/48 passed
test_watch: test_watch: 15/15 passed
test_why: test_why: 33/33 passed
rc=0
```
