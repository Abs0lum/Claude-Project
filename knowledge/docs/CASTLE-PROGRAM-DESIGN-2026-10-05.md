# CASTLES, CASTLE-TOWNS AND THE ACADEMY-CASTLE — program design (D-C572, 2026-10-05, for review)

Rulings in force (his 23:02 / 23:11 CT 10-04): C1 = both periods as skins, with FORCED VARIETY (no cookie-cutter towns; a
town may choose its style to upgrade to) · C2 = 256+ grand castle-palaces, built carefully and verified · C3 = both
founding modes (castle-first, and a castle added at tier-up) · C4 = the academy-castle 256×256 or more, lake and forest
edge shaped by the script, summoned where he stands. Standing law: an ORIGINAL academy-castle, never Hogwarts.

What the palace round taught, and the castle program inherits (lessons LC-1005-1..5):
- a script tick has 10 s before the watchdog kills the pack; QuickJS is ~50× slower than V8 — every per-candidate loop
  over thousands of cells must be pre-indexed (chunk sets), and work is spread over ticks with system.runJob;
- `structureManager.place` costs ~40 µs per cell → a stage file must stay under ~150k placed cells (the palace's full
  64×48×64 plot took 8 s; its light plot takes 0.16 s) — ground and sky are the land job's business, not the structure's;
- a Block handle of an unloaded chunk throws on READ, not only on fetch; entities spawn only in TICKING chunks;
- water must be read from the topmost block (a lake at y 108 reads as flat ground); the crown's surveyors (a held
  ticking area) are what lets a site beyond the player's simulation distance be measured at all.

## 1. castlegen.py — one generator, two skins, forced variety

Same base as palacegen (civgen.Building primitives; feet coordinates; markers; stages s0..s4 cut by civ_stages with a
LIGHT s0; pieces of 64×64 placed as one rotated group, one piece per beat). New primitives:
- curtain wall (thickness 2–3, wall-walk, crenellated parapet, arrow loops every 4), round / D-shaped / square towers
  (spiral stair, floors, roof cone or flat with parapet), gatehouse (twin towers, portcullis slot, murder holes, the
  passage with two doors), barbican, moat + drawbridge (water, a bridge piece), keep / donjon (4–5 storeys: undercroft,
  hall, solar, chapel, roof), inner and outer wards, great hall, kitchens, stables, smithy, well, garrison barracks,
  chapel, postern gate, dungeon stair.
- SKIN A "concentric, 13th c." (Beaumaris / Caerphilly type): two rings of curtain, inner higher than outer, D-towers,
  symmetric gatehouses on two sides, no keep (the inner ward's ranges are the lordly rooms), moat on three sides.
- SKIN B "late-medieval palace-block" (Bodiam / Pierrefonds type): one quadrangular curtain with four corner towers and
  a great gatehouse, the lord's palace block against one range (hall, great chamber, chapel with a tracery window,
  lodgings), a tall donjon at one corner, machicolated parapets, a moat with a causeway.
- VARIETY is forced by the seed, not chosen by the model: plan shape (square / rectangle / irregular polygon of 5–7
  sides fitted to the site), tower count and shapes, gatehouse side, keep corner, wall heights (8–12), materials
  (stone bricks / cobble / mossy / andesite mixes; roofs slate / wood / lead-grey), moat yes/no, barbican yes/no, the
  hall's roof type. The town's chosen style (A or B) persists in the settlement state (st.castleStyle) and the next
  castle tier upgrades in that style; two towns in one world never share a seed.
- Sizes: lord's castle 128–160 square (outer moat included); grand castle-palace 224–288 square (the palace program —
  state apartments, long gallery, chapel royal, library, terraced garden — inside the inner ward), the keep 28–36 high.
  Pieces: 64×64 grid, up to 5×5 = 25 pieces; stage files light; placement one piece per beat (≈ 25 beats a stage).

## 2. clock wiring

- Tier ladder: lord's castle at TOWN III (the lord arrives: castle + garrison + steward); grand castle-palace at CITY III
  (the crown's seat; the city-II palace stays for towns that take that road). A town that founds castle-first (mode
  "castle": `/scriptevent pw:clock castle [style] [seed]`) lays the castle on the high ground first and grows the
  town below its gate; a town that reaches town III without one gets the castle at tier-up (as the palace does).
- Site search: as the palace's survey (held ticking area, chunk occupancy, wetness from the topmost block) but
  PREFERRING relief: the castle wants the highest dry knoll within 90–260 of the square with a clear side toward the
  square; the moat wants water nearby but never under the keep.
- Castle-town integration: the city wall (city I) is re-planned to JOIN the castle's curtain (two wall ends meet the
  castle's flank towers; the castle's gate opens into the town); the main street runs gate → square; the market square
  stays below the castle; streets fan from the castle gate. The castle's offices are paid from the treasury (garrison,
  steward, chaplain, farrier, cook) like the palace's.
- Land: the land job clears naturals inside the pieces, fills hollows, cuts the moat (water from the script), raises a
  causeway; terraces as the palace does (one H for the whole group).

## 3. the academy-castle (original design)

A vast gothic collegiate fortress on a lake cliff at the forest's edge, 256×256 (+ lake and forest shaping to ~384):
founder's hall (hammer-beam roof, tall traceried windows, high table and dais), four scholars' towers each with a common
hall and dormitory stacks, a stair hall of open galleries, library with a reading gallery, lecture halls, an alchemist's
laboratory in the vaults, an observatory tower, chapel, infirmary, refectory and kitchens, a physic garden with
greenhouses, bell tower, gatehouse and viaduct over the ravine, boathouse on the water, stables, cloister, the hidden
passages a building of that age accumulates (jib doors, a priest's hole, a stair behind a bookcase, a tunnel to the
boathouse). Summon: `/scriptevent pw:castle summon academy [seed]` places the pieces around the player (the land job
shapes lake, cliff and forest edge first, over ticks), or `/structure load pw:academy_<piece>` piece by piece.
Implied-function rooms are extrapolated from the collegiate type (porter's lodge, buttery, muniment room, masters'
lodgings, servants' stair, laundry, ice house, dovecote), never from any protected design.

## 3b. v0.2 — "constructed correctly" (his C2), 2026-10-05 08:xx
castlegen v0.2 + tools/castle_verify.py. The verifier floods the model from the cell outside the gate as a 1 × 2 player
(steps of 1 up, drops of 3, doors open, iron bars and panes solid, light blocks and jib panels walk-through, a diagonal
move only where neither flanking column pinches — exactly the engine's 0.6-wide box) and proves eight checks:
R1 every ward cell · R2 every room (≥ 90 % of its standable cells) · R3 every bed · R4 every tower's ground floor and every
floor above it (the spiral works) · R5 ≥ 95 % of the wall-walk, THROUGH the towers · R6 with the gate sealed nothing
inside the curtain is reachable · R7 no room floor cell without a roof · R8 every marker reachable.
What v0.1 lacked (all fixed): no door on any room or tower; the portcullis sealed the gate; the walk dead-ended at every
tower (now a walk floor + openings at the walk level in each tower, and the walk crosses over the gatehouse); the keep's
iron door; the lodgings' partitions sealed each bay (now a corridor on the ward face); the rectangle plan drew its
orientation twice (two rings at 90°); the moat dug under the towers (now dug before them); the square ward fills paved over
the moat on polygon plans (now clipped to the ring); ranges placed by fixed offsets overlapped the keep or stood in the
outer ward of a polygon castle (now the largest inscribed rectangle + a scored search for every range); light blocks
buried in walkable floors (LC-1005-10); diagonal wall-walks one cell wide (LC-CASTLE-1: unwalkable beside a parapet — two
courses now). All eight sheet castles + two grand ones (224) pass. Sheet: CASTLE-VARIETY-SHEET-v0_2.png.
Carry-overs for the clock (§2): a 256+ block ± 8 exceeds one holdable 10 × 10-chunk area (LC-1005-11) → the castle survey
holds two 160-block halves in turn (or walks one window over the block) before a site is accepted; the pieces (up to 25)
place one per beat with every chunk of each piece probed (LC-1005-7).
HIS ANSWERS (08:43 CT 10-05, replacing the D-C554 assumptions): K1 b (moat by seed, water placed by the castle) ·
K2 b (a SEPARATE paid guard body — constable + men-at-arms — recruited over time as the population rises, never an instant
summon) · K3 a (four towers) · K4 c (castle-first settlements grow their castle into the grand castle-palace; the others get
the palace) · K5 a (a paid household: castellan, steward, chaplain, marshal, cooks, grooms) · K6 a (the gate faces the
square) · K7 b (the academy-castle founds itself as the seat of a rare ACADEMY CITY besides the summon) · K8 b (a BDS
villager walk test on top of the offline audit).

Stage cutting (measured 09:5x on B lord 1, written to _staging/civ/castle/mvv_castle_bl1): civ_stages puts a castle's
stone masonry into s0 ("ground" class: stone bricks, cobble) — 236–240k cells per 64 × 64 piece, i.e. the 8-second placement
that trips the watchdog (LC-1005-2). Castles need a HEIGHT-BAND cutter: s0 = ground + feet < 0 (light), s1 = masonry to
feet 4, s2 = masonry to the walk level, s3 = parapets + roofs + caps, s4 = furnishings + markers — every stage ≤ ~60k
cells. Measured: civ_stages + palace_light_s0 --keep-from=-6 gives a 24k-cell s0 per piece (the masonry rides in s0 as
"ground" class — placeable in ~1 s, but the castle would appear whole at the plot stage; the band cutter is the proper
answer). The land job (palaceWallJob + clearing) is reused as is; the moat is dug by the castle's own s0 water cells.

## 4. order of work and gates

1. castlegen v0.1 → v0.2 (both skins, variety by seed, the offline audit) → sheets for his review. DONE 10-05.
2. Blocks the castle needs that the kit lacks (portcullis, drawbridge pieces, arrow-loop block, machicolation) → RP-01.
3. Clock: castle block search (relief-seeking), group placement, lockstep stages, the wall joining the curtain, offices.
4. BDS gate: ladder to town III → castle; to city III → castle-palace; castle-first founding; two seeds ≠ same castle.
5. academygen v1 → renders → summon command → gate (summon on a hill, on a plain, by a lake).
6. Deliver: BP-02 1.3.223+, RP-01 1.3.124+.

Questions for him: K1 moat default (always / only where water is near / never)? K2 should the castle's garrison be
the town watch's upgrade (the watch moves into the castle) or a separate body? K3 the academy's house towers: four
(default) or the number he names?
