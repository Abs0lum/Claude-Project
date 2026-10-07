# PALACE — BP-02 1.3.232, item #21: the Palace II hook (HOOK-PROPOSAL Parts A–D)

**Bottom line:** Parts A–D are in the round-231 source, in `w232-PALACE`. All 35 suites pass (33 old + 2 new) and
`node --check` passes on every script. The hook **fails safe**. Two things are not in this session: the 16 Part C table
entries and the 96 structure files. Without them the clock writes one `[CIV-PALACE]` line and builds the 2 × 2 palace. In a
fake-world probe it picks the same site on the same day as 1.3.231. Applying the proposal as written would have broken two
things, both fixed here:
- **Saved worlds:** every 2 × 2 palace, reserve and survey would have been resized to 256.
- **The survey:** it could never finish measuring a sleeping 256 site with the default ticking slots (probe below).

The owner rulings are implemented. Two lord's beds are filled in one pass. The secret doors stay shut. Only court roles are
moved (teleported). Lore rows are skipped. The rotation helpers are passed in, so there is no circular import.

**Open question for him:** the plan says one-way passages move "public → hidden". All 6 iron doors open from the **hidden**
side, so I made them move hidden → public. One constant flips it (open question 1).

Static checks only rule things **out**. Everything below is "shipped, awaiting verification" until he witnesses it in game.

Deliverables: `out232/PALACE.diff` (md5 `94460ec5`, 1,344 lines, 9 files; it re-applies to the base byte-exact) ·
`out232/PALACE-files/` (tools, generator diff, structure list, probe) · `out232/PALACE.status`.

---

## 1. What changed, where, and why

### Part A: `pw_civ_clock.js` (md5 `051541c9`)
I applied the 12 proposal hunks verbatim first. `patch` reported every hunk at offset +33 with no fuzz, and the applied
`+/-` lines are identical to the proposal's. The snapshot is `PALACE-files/hook-partA-clock.diff`. I then amended them;
every change is in `PALACE-files/clock-amendments-over-proposal.diff`.

| Proposal hunk (230 line → 231 line) | What it does | In 1.3.232 |
|---|---|---|
| 1 `@@-1406` → 1439 | stage log text | **Amended** (clock:1445). The proposal's text gives "row **s** from the gate" for a saved 2 × 2 piece `sw`. `palacePieceLabel(q)` keeps "sw quarter" for old pieces and says "piece 21 (row 2 from the gate)" for PALACE II. |
| 2 `@@-1464` → 1497 | constants, 4 × 4 grid, `palaceGridRot` 3 − j | **Amended into two models** (clock:1500–1530). `PALACE_MODELS = {2: the 1.3.221 palace, 4: PALACE II}`, each with its pieces, grid, family and survey ring (110..320 / 180..440). `palaceGridRot(i, j, r, n)`; n defaults to 2, which is the old law. Size helpers: `palaceNOf` / `palaceSpanOf` / `palaceBox` / `palaceCentre` / `palaceReserveBox` / `palaceReserveFits`. A record without `n` is the 2 × 2 (128). The proposal's global `PALACE_SPAN` is removed (it would have resized every saved palace). |
| 3 `@@-1491` → 1529 | free test, R ring, centring | **Kept**, with the model's span (clock:1706–1745). |
| 4 `@@-1517` → 1555 | holds the quarter where the first sample missed | **Replaced** by the quartered measure (clock:1590–1652, survey 1733–1771). See §1.1. |
| 5 `@@-1540` → 1581 | 68 outside samples, 8 cells out | **Kept**: same positions, moved into `palaceSamples` / `palaceReads.outside`. A test shows the verdict is identical to the one-box measure. |
| 6 `@@-1554` → 1596 | inner wet grid over span | **Kept** (`palaceReads.inner`; same test). |
| 7 `@@-1579` → 1621 | site centre (gate rotation), `palaceDir` | **Kept** with the span (clock:1781). `palaceDir` uses `palaceCentre(record)`, so a legacy record stays +64 (clock:1787). |
| 8 `@@-1596` → 1638 | `reserveBox` | **Amended** to `palaceReserveBox(record)` (clock:1799). A saved 128 reserve keeps its box. |
| 9 `@@-1605` → 1647 | reserve log and chat | **Amended**: the size and centre come from the record (clock:1802–1810). |
| 10 `@@-1615` → 1657 | `placePalace` clash test | **Amended** (clock:1812–1845). The model is checked first. A reserve made for the other model is dropped ("does not fit … the surveyors look again", clock:1819). Pieces come from `PALACE_MODELS[n]`, and `st.palace.n` is recorded. |
| 11 `@@-1633` → 1675 | lay-out log and chat | **Amended**: the size and centre come from the palace. |
| 12 `@@-1667` → 1709 | `palaceWallJob` box | **Amended** to `palaceBox(stp.palace)` (clock:1879). With the proposal's global 256, a saved 2 × 2 palace's retaining walls would have been laid along a 256 box, 128 blocks out into the town, for up to 60 pump passes. |

**Drift: 231 code the proposal did not cover.** The status lines (clock:2801–2805) still used `x0 + 64` and the text
"110–320 blocks out". They now use the palace's own centre and size, and the survey's ring.

**Added beyond the proposal:**
- **FAIL SAFE** (clock:1532–1584). `checkPalaceII(sm, defs, log)` requires all 16 table entries and all 80 stage structures.
  It reads the pack list (`getPackStructureIds`) once. The list is trusted only if it contains the 2 × 2 palace's own
  `pw:stages/mvv_palace_sw_a_r1_s0`, which proves the id form `placeStage` uses. Otherwise, or if the call throws, it asks
  `structureManager.get` for each piece's s0 and s4. It writes exactly one `[CIV-PALACE]` line per session. Nothing throws:
  a missing structure manager or a throwing engine both fall back to the 2 × 2. `palaceModelNow()` caches the result, and
  `pw:clock palace check` asks again.
- **Pumps hold the block by quarter** (clock:2637). Before, the pumps asked for one ticking area per wet piece. For
  PALACE II that is 16 requests a day against `CORE_SLOTS_DEFAULT` 4 (the engine allows 10 areas per world), so the areas
  would keep being released and re-added. Now there is one 144 × 144 area per quarter that holds a wet piece: 4 for
  PALACE II, 1 for the 2 × 2 (it was 4).
- **Part D caller**: heartbeat `palacesecrets`, every 40 ticks, slot 20 of 40 (no other beat runs on that tick), optional,
  budget 5 ms (clock:2022–2045).
- **New command** `/scriptevent pw:clock palace [check | ends [id] | test <id> [ordinary]]` (clock:8398).

#### 1.1 Why the survey is measured quarter by quarter (evidence)
A 256 site plus 8 cells of margin is 272 × 272 = 17 × 17 chunks, and one ticking area holds at most 10 × 10. The proposal
held one quarter a day, but still measured a site only when **every** sample read on the **same** day. The surveyors keep
only one area protected: `coreBusy` (clock:4066 in the base) protects `sv.area` only. The 4 slots (`CORE_SLOTS_DEFAULT`)
are shared with the town's core.

1.3.232 reads each quarter while its area is awake and keeps it in `sv.parts`; the site is judged once all quarters are
in. The day's budget is `PALACE_PER_DAY` = 2 **quarters**. A 2 × 2 site is one quarter, so its old rate of 2 sites a day
is unchanged. A quarter whose chunks are not all loaded is skipped before any block read (`boxLoaded`, which only asks
`isChunkLoaded`).

Probe: `PALACE-files/survey-probe.txt`, produced by `probe_survey.mjs`. It runs the real `palaceSite` on a flat fake world
whose chunks load only inside the ticking areas the clock requests.

| Run | Accepted | Max areas held | Max topmost reads in one day |
|---|---|---|---|
| 1.3.232, PALACE II, 2 / 3 / 4 slots | day 5 / 5 / 5 | 2 / 3 / 4 | 416 / 418 / 418 |
| HOOK-PROPOSAL Part A as written, 2 / 3 slots | **never (60 days)** | 2 / 3 | 1,086 / 1,760 |
| HOOK-PROPOSAL Part A as written, 4 slots | day 5 | 4 | **3,639** |
| 1.3.231, 2 × 2 | day 2, site 52 −58 | — | 481 |
| 1.3.232 fallback, 2 × 2 | day 2, the **same site** | — | 228 |

A loaded PALACE II site therefore takes 2 survey days. The town III → city II window is about 130 days.

### Part B: `pw_civ_court_data.js` (md5 `132d0e6c`)
`PALACE_BEDS = { ...PALACE_BEDS_1, ...PALACE_BEDS_2 }`. PALACE_BEDS_1 is the 2 × 2 table, unchanged. PALACE_BEDS_2 is the
inbox data keyed "00".."33". The keys never collide.

The proposal replaced the table. That would have emptied every saved 2 × 2 court: `bedsOfPiece("sw")` returns `{}`, so
every member is released the next census day.

PALACE II beds: lord 2 (pieces 21 and 22), noble 16, guard 26, clerk 12, servant 201, child 36, cell 8.

### Part C: table entries (not in this session)
`palace2_buildings_entries.json` (1.2 MB) is generated in the cloud workspace from the piece manifests, and it is not in
the mirror. Without it, the clock in this source finds no `pw:mvv_palace2_*` entries, logs "missing 00 (table) …" and
builds the 2 × 2. This is tested against the real `CIV_BUILDINGS`.

Merge tool for the build: `PALACE-files/palace2_merge_buildings.py`. It adds or replaces exactly the 16 keys and keeps the
4 old entries. It validates each entry (stem, size [64, 50, 64], datum_y 15, stages 5, door, lists, a 5-stage bom) and
refuses to write on any problem. A second run writes the same bytes, and the existing 43 entries come out byte-identical.
Its test is `PALACE-files/test_palace2_merge.py`: **12/12** on synthetic entries.

I also loaded a merged synthetic table into the clock:
- table merged and all 80 structures listed: PALACE II ("checked by pack list");
- table merged and no structures: the 2 × 2, with 16 pieces missing.

### Part D: `pw_civ_palace_secrets.js` (new, md5 `42907e16`) + `pw_civ_palace_secrets_data.js` (new, 41 rows, md5 `7e8701c6`)
- **Pure logic.** `palaceCellToWorld` maps a model cell [x, f, z] to the world cell [x0 + gi·64 + lx, H + f, z0 + gj·64 + lz].
  The y convention is now verified from the source: palacegen2.py:16–17 defines "feet 0 = the paving"; light_s0 uses
  `feet = y − 15`; `placePalace` sets `y = H − datum_y` with datum_y 15. Also `pieceOf`, `passageEnds` and `secretMoves`.
- **Rotation helpers** (`rotXZ`, `palaceGridRot`) are **passed in**. The module imports neither the clock nor
  `@minecraft/server`.
- **The rule:**
  - Roles that may use passages: lord, noble, child, guard, servant. Never clerk, cell or ordinary civs.
  - A civ is moved only when it stands within 1.5 blocks of an end and its goal (the walk's target, which is its bed or
    station) is **strictly** nearer the other end.
  - At most one move per civ per pass: the one that brings him nearest his goal.
  - Both pieces holding the passage must be finished, and the arrival cell plus the cell above must be air.
- **Directions:**
  - Two-way passages (disguised, hidden) work both ways, as the approved plan says ("and back the other way"). A
    hidden-mode space is unreachable from the gate by design, so one-way-in would trap a civ.
  - **One-way passages move only from the side their iron door opens from** (`ONEWAY_FROM = "hidden"`; see open question 1).
  - Lore rows (H16) and rows without a hidden end (H14) are skipped.
- **World wrapper** `runPalaceSecrets(st, deps)`. It calls only `entity.teleport`, then cancels the walk so the schedule
  re-sends the civ from the new side. It writes one `[CIV-PALACE] secret <id>: <name> (<role>) <from> -> <to> end at x y z`
  line per move. It never writes a block or runs a command; the tests use a proxy that records any write, plus a source scan.
- **Data generator** `PALACE-files/palace2_secrets_js.py`. The generator diff `palace2_hookdata.py.diff` emits the same
  module and the merged court data; I ran it on synthetic manifests and its output equals this source's two data files.
- **`pw_civ_walk.js:547`**: new `targetOf(v)`, which returns the walker's target or null.

### At least 2 lord beds (D-GH1007-LORDBEDS)
**`pw_civ_court.js:131` was the bug.** It admitted **one** lord per pass. With PALACE II's two lord beds, the next top
families became nobles on that same pass, and a family already at court is never a candidate again. So in a small town the
second lord's bed stayed empty for good.

Red run: 16 pieces and 3 couples gave "lords admitted in one pass: 1 … free 1".

**Fix:** every free lord's bed is filled, top families first (court.js:131–134). The top family goes to piece 21 (the lord's
state bedchamber), the next to piece 22 (the consort's). Both are kept the next day. A saved 2 × 2 palace still seats one
lord.

Every code path I checked handles two or more beds:
- `courtPlan`;
- the `beds` command (it counts per role);
- the secrets module (each lord's own goal);
- the generator, which now asserts at least 2 lord beds.

---

## 2. Tests added or changed
- **`tests/test_palace_secrets.mjs`, 61 checks:**
  - data: 41 rows, mode counts, MAY_USE, ONEWAY_FROM;
  - rotations 0/90/180/270: all 81 ends equal the whole 256 model rotated with `rotXZ`. A hand-computed asymmetric cell (H12
    hidden 145/−12/73 → 1145/58/−427, 1182/58/−355, 1110/58/−318, 1073/58/−390). U5 crosses pieces 22 → 21;
  - usable passages: 39 (lore skipped); an unfinished piece shuts its passage;
  - role filter: 5 roles move; clerk, cell and ordinary civs do not;
  - nearer-end rule: wrong side, no goal, 3 blocks away, equidistant;
  - two-way back (H7a); one-way H10 plus U1, U4b, H6b, H6c, U3 move only hidden → public; lore H16 / H14;
  - blocked arrival cell; the best of two ends in reach (H7b / H7c);
  - **two lords heading to their own beds:**
    - at the same spot, lord A (bed in 21) takes U5 and lord B (bed in 22) does not;
    - in the spine, A uses the H1 bedchamber door and B uses H3, each landing within 4 blocks of his own bed;
  - decisions identical at every rotation;
  - wrapper: teleport only, walk cancelled, doors never opened (write proxy), one log line, blocked end, the 2 × 2 palace
    has no passages;
  - the module source contains no block write and no clock or engine import.
- **`tests/test_palace_hook.mjs`, 123 checks:**
  - models, grid == whole-model rotation (n 2 and 4, all rotations), legacy span / box / centre / reserve / labels;
  - FAIL SAFE: 80 required ids; table missing / one piece / one stage; pack list / unconfirmed list / no list / throwing
    engine / no manager; the real table falls back; the session line is written once;
  - quarters and 10-chunk boxes at every alignment;
  - quartered verdict == the proposal's one-box measure (2 spans × 4 seeds);
  - liveness with one held area: the proposal's rule never completes;
  - the day's budget;
  - **the real `palaceSite`**: a sleeping PALACE II site is accepted by day 6 with 2 slots and ≤ 420 reads a day; the 2 × 2
    on day 2; a saved 2 × 2 survey restarts for 256, with a chronicle line;
  - court data keys and totals; two lords in one pass, each in his own piece; stable the next day; the 2 × 2 seats one lord.
- **`tests/test_court.mjs`**: one import line changed. Its whole-table assertions ("96 role beds", "one children's bed per
  apartment") are about the 2 × 2 table, so they now read `PALACE_BEDS_1`, which is byte-identical to the old
  `PALACE_BEDS`. 37/37.
- Red before green (`PALACE-red.txt`): both new suites, run against the unchanged 231 source, fail (the module and exports
  are missing), and the lord red run there shows "1 lord a pass, 1 free".

---

## 3. Structure files the build must include (`PALACE-files/PALACE-STRUCTURES.txt`)
- **REQUIRED, 80 files.** The hook asks for every one; `placeStage` places `pw:stages/<stem>_s<k>`.
  `structures/pw/stages/mvv_palace2_<r><c>_a_r1_s<k>.mcstructure` for r, c in 0..3 and k in 0..4.
- **RECOMMENDED, 16 files.** No script places them; they are for `/structure load` and the BDS pack checks, as for the old
  palace. `structures/pw/mvv_palace2_<r><c>_a_r1.mcstructure`.
- **KEEP, 24 files already in BP-02**, for saved 2 × 2 palaces and the fallback:
  `structures/pw/mvv_palace_{sw,se,nw,ne}_a_r1.mcstructure` plus their `stages/…_s0..s4`.
- **Do not ship:** `*_s0_full` (already deleted) and `manifests/*.json`.
- No `_r` / `_w` files are needed: palace pieces are civic, so `hhOf` = 0 and they are never weathered or repaired.
- **Size:** the PALACE README gives about 158 MB (structures 29 + stages 129). BP-02 1.3.230 unpacks to 122.8 MB in 11,719
  files (measured from the 1.3.230 mcpack), so together about **281 MB** (open question 5).

---

## 4. In-game tests (only he can confirm these)
1. **Fail-safe, in a build without the PALACE II files or table:** `/scriptevent pw:clock palace` replies "palace model
   now: the 2 × 2 palace … PALACE II is not complete in this pack (checked by …): missing 00 (…) …". The content log shows
   the `[CIV-PALACE]` line once. Nothing crashes.
2. **Complete build:** `/scriptevent pw:clock palace check` replies "PALACE II … 16 pieces + their stage structures are in
   the pack (checked by **pack list**)". If it says "checked by get", the pack list's id form differs from `placeStage`'s.
   It still works, but tell me.
3. **Survey** (a town at town III+, e.g. via `pw:clock grow`): the status shows "measuring 256 × 256 sites 180–440 blocks
   out". The content log shows `ticking area civN: palace site survey (R from the square, quarter qq)`, one quarter a day.
   The chronicle shows "the crown RESERVES its land — a 256 × 256 block". A saved town that already reserved 128 shows "does
   not fit … the surveyors look again" at city II.
4. **Placement** (city II): "the palace block (256 × 256)"; 16 pieces rise together; status "PALACE: centre … (4 × 4
   pieces)". Watch the day-step time and the PS5's memory during placement: each piece is placed whole in one tick, as the
   old palace was.
5. **Court:** once the pieces are finished, `/scriptevent pw:clock beds` shows "lord: 2 of 2". The chronicle shows two "…
   moved into the palace — the lord's bedchamber" lines.
6. **Secret passages (Part D witness test):**
   - `/scriptevent pw:clock palace ends H1` lists the coordinates.
   - `/scriptevent pw:clock palace test H1-LORD`: a court member is put at the public end with a goal beyond the other end.
     Within 2 s expect `[CIV-PALACE] secret H1-LORD'S STATE BEDCHAMBER: <name> (<role>) public -> hidden end …`, then
     "WAS moved … as the rule says".
   - `… palace test H1-LORD ordinary`: expect "was NOT moved … as the rule says".
   - `… palace test H10`: the one-way Bridge of Sighs, expect a hidden → public move.
   - Each time, look at the jib panel or iron door: it must stay **shut**.
7. **Saved world with a 2 × 2 palace:** the status still says "2 × 2 pieces" with the same centre, and `beds` is unchanged.

---

## 5. Open questions and decisions for him
1. **One-way direction** (a contradiction between the plan's text and the data). The approved plan says one-way passages
   move "public → hidden". In all 6 one-way rows the iron door's button side (`iron_gate(inside=…)`) is the **hidden** end:
   palacegen2.py:451 U1, :464 U4b, :511 H6c, :1397 H6b, :1509 H10 ("nobody comes back this way"), :1938 U3. I implemented
   the door's direction, hidden → public. `ONEWAY_FROM = "public"` in pw_civ_palace_secrets.js flips it. Which does he want?
2. **Two lord beds = two lord households** (top family in 21, next in 22). The alternative reading is one lord couple
   spread over the lord's and the consort's bedchambers; that would need a court change (one household on two beds).
3. **Court night place.** A court member walks to his piece's "inside the door" cell, piece-local (2, 32) at feet 0. That is
   the existing CIVITAS night place, and it is not his role bed (lords' beds are on the noble floor, f 6). Follow-up:
   palace2_hookdata could emit each piece's role-bed cells (the manifests' `bed_roles`), and the court's night goal would
   use them. The passage rule would then serve real beds without any change (it reads the walk's target).
4. **Children.** PALACE II has 36 children's beds for 18 apartments (2 per apartment; a nursery for 4), but
   `COURT.kidsMax` stays 2, so a couple with 3–4 children still does not fit. Raise it?
5. **Pack size.** About 281 MB if PALACE II ships inside BP-02 (the 250 MB rule is written for resource packs). The hook
   only asks for `pw:stages/...` ids, so the 96 files could ship in a companion behaviour pack; if that pack is absent, the
   fallback builds the 2 × 2.
6. **Ticking slots.** PALACE II pumps want up to 4 quarter areas, and the default is 4 slots shared with the town. Suggest
   `/scriptevent pw:clock tickslots 6` for a PALACE II town (the engine allows 10).
7. **Marginal moves.** The literal "strictly nearer" rule moves a court member through a jib door whenever his goal lies on
   the other side of the wall, even for a fraction of a block's gain. A minimum gain (e.g. 1 block) is one constant; I did
   not add it because it was not ruled.

## 6. Not fixed (pre-existing, flagged)
- The pumps' "3 dry passes end the pumps" check counts sleeping chunks as dry; this is the same for the old palace. After
  the pumps stop, pieces build only while their chunks are loaded (status: "N piece(s) waiting for their chunks").
- `STATION_WAGE["palace"]` and `SPIRIT_PTS["palace"]` use the exact key "palace". Both "palace_sw" and "palace2_00" miss
  them, so behaviour is unchanged (this is the proposal's own CHECK note).
- If a world laid PALACE II and later loads a BP-02 without the table entries, `short(b)` throws for those pieces. That is a
  downgrade case; never ship PALACE II and then remove Part C.

---

## 7. Final full test run (`run_civ_tests.sh w232-PALACE`; `node --check` on every script, exit 0)
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
test_inn24: test_inn24: 57/57 passed
test_landclock: test_landclock: 25/25 passed
test_lanes: test_lanes: 14/14 passed (lane 101 cells, 5 legs, turns 4)
test_leisure: test_leisure: 27/27 passed
test_market: 16/16 passed
test_names: test_names: 48/48 passed
test_needs: test_needs: 80/80 passed
test_occupied: test_occupied: 97680/97680 passed
test_palace_hook: test_palace_hook: 123/123 passed
test_palace_secrets: test_palace_secrets: 61/61 passed
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
exit 0
```
Tool test: `python3 PALACE-files/test_palace2_merge.py <231 pw_civ_buildings.js> <workdir>` → 12/12 passed.
