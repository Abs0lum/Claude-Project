# CASTLE DESIGN — COMPLETE INVENTORY (D-C572 continued, 2026-10-06, for review)

Owner's instruction (22:18 CT 10-06): "Castles into the game — design everything we need. Move to immediately with palace 2."
This document is DESIGN ONLY. Nothing was built, placed or changed. Every real-world number below is quoted from a source in §13 (the inventory table is §12);
1 block = 1 m. Where no source was fetched this round, the line says **(design choice)** or **(unverified)**.

Inputs read (read-only):
- `_docs/CASTLE-PROGRAM-DESIGN-2026-10-05.md` — 113 lines / 10,762 B; first line "# CASTLES, CASTLE-TOWNS AND THE ACADEMY-CASTLE — program design (D-C572, 2026-10-05, for review)".
- `_logs/decision_journal.md` (3,906 lines) — D-C572, his K1–K8 answers (08:43 CT 10-05), the WATER law (moat fed and drained like the palace), his 12:20 thatch-gable ruling, the 17:58 catwalk/skyway program, the 18:22 PALACE II brief, the 228 deferrals.
- `tools/castlegen.py` (1,011 lines) and `tools/castle_verify.py` (198 lines); renders `CASTLE-VARIETY-SHEET-v0_2.png`, `mvv_castle_al2-plan-0.png`, `mvv_castle_bl3-plan-0.png`, `mvv_castle_bl3-elevation.png` (viewed in full).
- Kit census: `_build/bp02-228` block identifiers (roof45 / roof63 / hip / pyramidion / gussets / ridge_end / rafter45, spiral stairs A/B/C, hearth, flue, furniture, ramps, angled walls, jib panel, secret painting).

## 0. Rulings this design must satisfy (his, in force)

| Code | Ruling | Where it lands in this design |
|---|---|---|
| C1 | two period skins (A concentric, B palace-block), FORCED VARIETY by seed | §10 variety knobs kept; new knobs listed |
| C2 | 256+ grand castle-palaces, constructed correctly, verified | §9 growth tiers, §11 verifier additions |
| C3 | both founding modes (castle-first, castle at tier-up) | §9: castle-first reserves the GRAND footprint at founding |
| K1 b | moat decided by the castle's seed, water placed by the castle | §5.1 moat = wet / dry / none by seed; wet moat obeys the water law |
| K2 b | a separate PAID guard body (constable + men-at-arms), recruited over time as population rises, never summoned | §7.1 garrison lodging grows in steps; beds exist before men are hired |
| K3 a | four academy towers | §8 |
| K4 c | castle-first settlements grow their castle into a grand castle-palace; others get the palace | §9 |
| K5 a | a paid castle household (castellan, steward, chaplain, marshal, cooks, grooms) | §7.2 a chamber for every office |
| K6 a | the castle gate faces the square | generator gate is always on the x0 side; the clock's rotation points x0 at the square (kept) |
| K7 b | the academy-castle also founds a rare academy city by itself | §8.3 |
| K8 b | BDS villager walk test + offline audit | §11 |
| WATER | water touching a site is fed into a fountain/waterfall structure and down into the sewers; ALL structures include subsurface infrastructure | §6 (every castle piece carries its share of drains, culverts, cellars) |
| 12:20 | castle thatch = GABLES with existing thatch pieces | §7.4 bailey buildings |
| 17:58 | diagonal catwalks/skyways (structures only), "a castle hall with an open floor and a diagonal skyway overhead" | §4.2 great hall |
| 18:22 | enlarge freely; real blueprints down to secret halls, doors, stairs, underground passages | §5.5 secret ways, §6 underground |

## 1. Where the generator stands today (measured 2026-10-06, in memory, nothing written)

All ten castles (the eight sheet castles + A grand 1 + B grand 1) pass all eight R-checks when built from today's `castlegen.py`
and verified in memory. **The 18:42 `CASTLE-VARIETY-SHEET-v0_2.png` is stale**: its headers read "NOT YET" on every row and
"bare 18 / 26 / 33 / 34" on the four B rows, while the current code gives bare 0 on all ten. Regenerate the sheet before he sees it.

Findings from that run that the castle round must carry:

| # | Finding | Evidence | Severity |
|---|---|---|---|
| F1 | **`cut()` drops the far edge of every castle whose width is not a multiple of 64**: `n = sx // 64`, so 144 → 128 covered, 160 → 128, 224 → 192, 288 → 256. A written 160 castle loses its far 32 columns and rows (towers, moat, curtain). | `castlegen.py` l.816–818; measured `size (160, 60, 160) pieces n 2 covers 128` | **P0** — blocks placement |
| F2 | keep_4 reads 93/101 cells reached on every B castle (passes the 90 % bar). Known counting artifact: the C_grand spiral's 8 stair-tread cells inside the well are counted as room floor. | in-memory verify B lord 1, B lord 2 | P1 — fix the count (exclude spiral wells from room rectangles), not the keep |
| F3 | the A_turret spiral finds no clean exits in 2–4 towers per A castle (always the gatehouse flank towers, r = 3) → those towers fall back to the old full-block newel stair. | `notes` of A lord 2/3/4/5, A grand 1, B lord 1/2 | P1 — gatehouse towers need r = 4 or a stair hall (§3.2) |
| F4 | The GRAND size builds exactly the lord program (hall, chapel, lodgings, kitchens, stables) in a bigger box — no palace program yet. | `placed` list identical for lord and grand | P0 for C2/K4 |
| F5 | Total beds: 6 (A) / 8 (B). The guard body (K2) and household (K5) have nowhere to sleep. | `c.beds` | P0 for K2/K5 |
| F6 | The gatehouse "chamber over the gate" is SOLID masonry (`fill(x, 5, z, x, h-3, z, curtain)`), so there is no gate chamber, no murder holes, no winch room. | `castlegen.py` l.403 | P1 |
| F7 | No subsurface infrastructure at all: the box reaches feet −15 but holds only dirt, the moat's cobble bed and a 6-deep well column. | `build()` l.625–627, l.762 | P0 (water law) |
| F8 | B lord wards are ~100 × 100 mostly empty lawn (sheet rows 5–8) — far larger than a real quadrangular castle's court (Bodiam ≈ 24 m). The ranges float in the ward instead of standing against the curtain. | sheet rows 5–8; Bodiam §2 | P1 — re-plan B (§10) |

## 2. The reference castles (what each one teaches this program)

| Castle | Real numbers (sourced) | Blocks | Lesson for us |
|---|---|---|---|
| **Beaumaris** (concentric, 1295–) | inner curtain "36-foot (11 m) high and 15.5-foot (4.7 m) thick"; walls ~"18.3 metres (60 ft)" apart; inner ward "0.75-acre (0.30 ha)"; "164 arrow slits", ~300 firing positions; north gatehouse hall "70 feet (21 m) by 25 feet (7.6 m)", two storeys, "two sets of five, large windows"; first-floor passages in the inner walls; built to host "two substantial households"; chapel built into a tower; the Gate next the Sea [W-BEAU][WH-BEAU] | inner curtain 11 h × 5 thick; outer ward 18 wide; inner ward ≈ 55 × 55; gatehouse hall 21 × 8 | skin A's arithmetic: 55 + 2×5 + 2×18 + 2×3 + 2×6 moat ≈ 140 → a 192 box leaves room for barbican, dock and sluice. The lord lives in the GATEHOUSES (no keep). |
| **Caernarfon** | King's Gate: "two drawbridges, … five doors and under six portcullises, and … a right-angle turn"; "numerous arrow loops and murder holes"; great hall "30.5 metres (100 ft)"; northern towers "four storeys including a basement"; Eagle Tower basement "water gate"; town walls "734 m … eight towers and two … gatehouses", gap-backed with removable wooden bridges; chapel of St Mary built into the town defences at a corner tower [W-CAER][W-CAERTW] | gate passage with a 90° turn; hall 30 long; towers 4 storeys | the gate is a sequence of obstacles; the water gate is a tower basement; the castle and town wall are one system |
| **Conwy** | eight towers "70-foot (21 m) tall"; inner and outer ward split by a cross-wall with "a drawbridge and a gate, protected by a ditch cut into the rock"; two barbicans (the east one enclosed the garden); postern to a river dock; great hall + chapel "sitting on top of the cellars", stone arches of the 1340s; inner-ward towers carry watch turrets; well "91-foot (28 m) deep", spring-fed; garrison "30 soldiers, including 15 crossbowmen, supported by a carpenter, chaplain, blacksmith, engineer and a stonemason" [W-CONWY]. Town walls "1.3 km", "21 towers and three gatehouses", gap-backed towers with removable bridges, wall-walk carried on corbels, "twelve medieval latrines", the walls "emerge from Conwy Castle", "124 burgage tenements" by 1312, a postern and Lower Gate to the quay [W-CONWYTW] | towers 21; garrison 30 + 5 trades; well 28 (exceeds our −15 box → §6.4) | the lord-castle garrison number; cellars under the hall; the town wall springs from the castle's flank towers |
| **Harlech** | gatehouse: "seven obstacles, including three portcullises", guardrooms, "murder holes directly above"; constable on the first floor, distinguished guests above; inner ward: "great hall and kitchen", "chapel and bakehouse", "granary and a second hall"; the Way from the Sea, "a gated and fortified stairway plunging almost 200 ft" [CW-HARL] | gatehouse = lodging block; sea stair ~60 | the residential gatehouse; the sally stair as a lifeline |
| **Bodiam** (palace-block, 1385) | quadrangle, "no keep, … chambers built around the outer defensive walls"; round corner towers, square mid towers; towers "three storeys"; moat "about 5 ft (1.5 m) deep but 7 ft (2.1 m) … in the southeast corner", "supplied by several springs"; island "the Octagon", a barbican, an L-shaped bridge, drawbridges; gatehouse "three wooden portcullises", vaulted passage "pierced with murder holes", gun-loops; "28 toilets drained directly into the moat"; great hall "24 by 40 feet (7.3 by 12.2 m)"; well in the SW tower basement [W-BOD]; kitchen with "a huge roasting hearth in the south wall and a second hearth in the north, inset with bread or pastry ovens"; chapel with an oratory above; postern tower "with its own drawbridge"; a dovecote in a tower [NT-BOD]; courtyard "roughly 80 feet square", domestic ranges two storeys against the curtain [TR-BOD] | court ≈ 24 × 24; hall 7 × 12; moat 2 deep | **skin B is a compact quadrangle** whose whole castle fits ONE 64 piece; the moat is a lake around it |
| **Krak des Chevaliers** | outer circuit "9 metres (30 ft) high"; glacis on the weak side; inner towers square, outer towers round; four round towers lodged the knights, "about 60"; garrison "around 2,000"; bent entrance corridor "137 metres (450 ft)" with murder-holes; machicolations; chapel "21.5 metres (71 ft) long and 8.5 metres (28 ft) wide", barrel vault; open cistern fed by an aqueduct "both as a moat and water supply"; vaulted storage/stabling; a postern added c. 1250s [W-KRAK] | outer wall 9; chapel 21 × 9 | knights lodge IN towers; the cistern-moat (our water law, historically); the long bent entrance |
| **Vincennes donjon** | "52 meters"; walls "more than three meters thick"; "16.2 meters on each side"; "six floors", "a single, slender central column"; corner turrets "6.6 meters"; a tower with "latrines on every floor"; its own wall and wet moat; well on the ground floor; enclosure "1100 meters and nine towers", "40 to 42 metres high"; chapel 1379 [MED-VINC] | donjon 16 × 16, walls 3, 6 storeys | the grand-tier donjon; a latrine tower; the keep's own chemise and moat |
| **Dover Great Tower** | "83ft high, … corner towers rising 12ft higher … walls up to 21ft thick"; two chapels; spiral stairs in the NE and SW corners; "a well 289ft deep" and "lead pipes distributing water sourced from rainwater gutters"; inner curtain "14 square towers and two gatehouses" [CL-DOVER]; 13th-c. tunnels "linked the spur redan and St Johns tower to the northern entrance" [KENT-DOVER] | keep 25 h, turrets +4, walls up to 6 | mural chambers + chapels in the wall thickness; rainwater → cistern piping; a real documented underground passage |
| **Hedingham keep** | "53 ft (16 m)" × "about 58 ft (18 m)"; "more than 70 ft (21 m)" + turrets "15 to 25 ft"; walls "11 ft (3.4 m)" base / "10 ft (3.0 m)" top; "five floors including the Great or Banqueting Hall with a large fireplace and a central arch extending two storeys" [W-HED] | keep 16 × 18 × 21 (+5–8 turrets), walls 3 | the two-storey hall inside a keep with a spanning arch — the precedent for our open hall |
| **Warwick** | Caesar's Tower "40 metres", quatrefoil; Guy's Tower "29 metres" [WAR]; the Caesar's Tower "oubliette" judged "the remnants of a latrine" [W-DUNG] | 40 / 29 | grand-tier tall towers; myth flag |
| **Alnwick** | barbican completed by 1475; 1750 "a grand palace in the fashionable Gothic style" (Adam, Brown); 1854–65 Salvin's Prudhoe Tower and Great Kitchen; State Rooms [ALN] | — | castle → palace growth in documented stages |
| **Kenilworth** | 1120s "castle, park, mere and priory"; John of Gaunt's 1370s palace: "the great hall was the widest roofed space in England after Westminster Hall"; mere "half a mile across"; Leicester's Building, "large glazed windows" [EH-KEN] | — | tiered growth: keep → hall palace → Elizabethan glass lodgings |
| **Raby** | hall house first, kitchen tower after 1373 sized like Durham's kitchen, "domed ceiling"; western expansion 1381–88 made it concentric [CST-RABY] | — | a separate kitchen TOWER; growth by additions |
| **Caerphilly** | lakes = "the most elaborate water defences in all Britain"; South Dam "152 metres (499 ft) long"; sluice gates guarded by "Felton's Tower"; north dam with three towers that "may have supported the castle's stables"; 30 acres; concentric; gatehouse with portcullises and murder-holes [W-CAERPH] | dam 152 | **the sluice tower** = our moat overflow → cascade → sewer |
| **Malbork** | "21ha", "three separate castles–the High, Middle and Lower … separated by multiple dry moats"; "approximately 3,000" brothers; a royal residence 1457–1772; the Great Refectory [W-MAL] | — | dry moats between wards; a castle complex that became a royal seat |
| **Carcassonne** | "3 kilometres … double surrounding walls … 52 towers"; Roman towers "about 14 metres tall", "spaced from 18 to 30 metres apart"; barbican and moat 1240–50; the Château Comtal inside the Cité; Viollet-le-Duc's slate roofs criticised as northern [W-CARC] | tower spacing 18–30 | **tower spacing rule**; a castle inside a walled town |
| **Hohenzollern** | approach: "winding zwinger turns four times and terminates in the bastions"; Eagle Gate "and its attached drawbridge"; palace "in a u-shape that ends with Protestant and Catholic chapels", sitting "on top of the old casemates"; towers aligned to the four bastions [W-HOHEN] | — | the hairpin approach ramp (our ramp kit); a palace built on the old castle's outline |
| **Chambord** | "128 metres (420 ft) of façade", 56 m; "a central keep with four bastion towers"; "Four rectangular vaulted hallways on each floor form a cross-shape"; "440 rooms, 282 fireplaces, and 84 staircases"; the open double spiral "illuminated from above by a sort of light house"; castle layout with moat as decoration [W-CHAM] | façade 128 | the castle-palace: keep form, cross corridors, a grand double stair, a roofscape |
| **Neuschwanstein** | gatehouse "flanked by two stair towers"; lower and upper courtyard; Palas "five-story"; Rectangular Tower "45 meters"; northern stair tower "65 metres"; Knights' House joined to tower and gatehouse "by means of a continuous gallery"; Bower; Throne Hall "20 by 12 metres … height of 13 metres", on the third and fourth floors; Singers' Hall "27-by-10-metre"; "more than 200 interior rooms" planned, ~15 finished; warm water, flushing toilets, hot-air heating, "service lift" kitchen → dining [W-NEU] | throne hall 20 × 12 × 13 | the palace-like grand castle; a gallery linking buildings; the service lift = our servants' stair/dumb-waiter |
| **Uraniborg** (academy precedent) | main house "square, about 15 meters on a side", two semicircular towers; main floor four rooms; loft "subdivided into eight smaller rooms for students"; basement "alchemical laboratory … and storage"; north tower kitchens, south tower library; planned wall "75 meters on a side and 5.5 metres high"; gatehouses held the printing workshop and the prison; Stjerneborg instruments "placed underground" under shutters / a rotating dome; "upwards of thirty" assistants [W-URAN] | house 15 × 15; 8 student rooms per loft | the academy tower program (§8) |

## 3. Fortification elements

### 3.1 Curtain walls, wall-walks, crenellation

| Element | Real | Blocks (design) | Piece | castlegen HAS | MISSING |
|---|---|---|---|---|---|
| Outer curtain | Krak 9 m high [W-KRAK]; Beaumaris outer lower than inner [W-BEAU] | 8–10 high (keep), **3 thick** | edge pieces | `wall_segment` h 8–10, thick 2 (A) / 3 (B) | A outer thick 2 → 3 (a 2-wide walk + parapet) |
| Inner curtain | Beaumaris 11 h × 4.7 thick, first-floor passages inside [W-BEAU] | 12–16 high, **5 thick**: outer skin 1, a **1 × 2 mural passage at feet 4–5** (loops out, garderobes off it), walk 3 wide on top | centre/edge | thick 3, solid | the mural passage, garderobe recesses, 5 thick |
| Wall-walk | Conwy town wall-walk carried on corbels, "flat, relatively wide" [W-CONWYTW] | ≥ 2 wide on straights, 3 on diagonals (LC-CASTLE-1 already) | — | yes (dressed walk at h−2, lit) | corbelled overhang variant (needs a corbel block or slab-on-stair trick) |
| Crenellation | crenel "typically one-third the width of the adjacent merlon" [W-BATT] | **merlon 3 : crenel 1** (now 1 : 1); merlon top 2 above the walk, crenel sill 1 + bottom slab | — | merlon/slab alternating every cell | the 3 : 1 rhythm; an arrow slit in every second merlon |
| Arrow loops | Beaumaris 164 slits in the outer curtain [W-BEAU] | 1-wide × 2-high slits every 4–5 cells at the mural passage and at walk level | — | 1-cell holes every 5 (`i % 5 == 2`), 1 high | a cross-slit block (RP-01) or iron-bar-backed slit; 2 high |
| Machicolations | "openings between the supporting corbels"; in England "usually restricted to the gateway, as in … Conwy" [W-MACH] | box machicolation (bretèche) over every gate; continuous on skin B towers (French type) | gate pieces | none (docstring claims B has them; the code lays none) | a corbel + floor-gap pattern, 1 out from the parapet; needs a corbel block |
| Hoardings | timber galleries (Carcassonne reconstruction) [W-CARC] | optional seasonal timber gallery on A outer towers | — | none | low priority |
| Glacis / talus | Krak's sloping glacis on the weak side [W-KRAK] | 63° roof-family masonry (pw:roof63 stone) at the curtain foot on the uphill side | edge | none | needs a stone roof63 skin (design choice) |

### 3.2 Towers

| Element | Real | Blocks | HAS | MISSING |
|---|---|---|---|---|
| Spacing | Carcassonne Roman towers 18–30 m apart [W-CARC] | ≤ 32 along any curtain run (flanking fire) | corners + mids only (spacing up to ~70 on a 160 side) | towers by run length, not by a count |
| Height | Conwy 21 [W-CONWY]; Vincennes enclosure 40–42 [MED-VINC]; Warwick 29 / 40 [WAR] | lord: curtain + 6 to + 8 (19–24); grand: up to 40 | outer `outer_h + 5`, inner `inner_h + 6` | grand heights |
| Storeys | Caernarfon northern towers "four storeys including a basement" [W-CAER]; Bodiam towers three storeys [W-BOD] | basement (feet −5..−1, store / cistern / prison), ground, 2 floors, roof | floors every 5, no basement | basements |
| Shapes | round / D / square (Beaumaris D-towers; Bodiam round corners + square mids; Krak square inner + round outer) | keep all three; B: round corners + **square mid towers** (Bodiam) | round / d / square per castle | mixed shapes per castle (corners vs mids) |
| Gap-backed towers | town-wall towers open at the back with removable timber bridges (Conwy, Caernarfon) [W-CONWYTW][W-CAERTW] | town-wall towers only (the clock's city wall): open back + a plank bridge cell | n/a (clock) | a town-wall tower template |
| Stair turret / caphouse | Conwy inner towers carry watch turrets [W-CONWY]; Dover spiral stairs in two corners [CL-DOVER] | A_turret spiral + caphouse (built 228); watch turret on inner towers (1 r-1 cylinder +4) | `spiral2(... caphouse=True)` | watch turrets; gatehouse towers r 3 → 4 so the A_turret fits (F3) |
| Caps | conical roofs are a later/French/restoration look (Viollet-le-Duc's slate cones criticised at Carcassonne [W-CARC]) | seed: flat lead roof + parapet (default English), or cone (French) | square HIP over a round tower when `tower_caps` | **cone/spire block set** (or roof63 + pyramidion composition), thatch never on towers |

### 3.3 Gatehouse

Real sequence (Caernarfon King's Gate): 2 drawbridges, 5 doors, 6 portcullises, 90° turn, loops and murder holes [W-CAER];
Harlech: 7 obstacles incl. 3 portcullises, guardrooms, constable's lodging above [CW-HARL]; Bodiam: 3 wooden portcullises,
vaulted passage with murder holes, gun-loops [W-BOD][NT-BOD]; Beaumaris north gatehouse hall 21 × 7.6 m [W-BEAU].

| Part | Blocks (design) | HAS | MISSING |
|---|---|---|---|
| Passage | 4 wide × 5 high × 9–11 deep (curtain 5 + gate block) | 4 × 5 × 7 | depth to the new curtain thickness |
| Drawbridge pit | turning bridge "counterweights … sink into a pit in the gate-passage" [W-DRAW]: a 4 × 3 × 3 pit at the outer end, the bridge deck lowered over it (planks on the pit edge) | none (cobble causeway) | the pit + deck; gaff slots above the arch (bascule type, Herstmonceux [W-DRAW]) as decoration |
| Portcullises | 2 (lord) / 3 (grand): grooves = a 1-deep slot in both passage walls; raised = bars in the chamber above | 1, raised (bars in the top 2 cells) | the groove slot; the 2nd/3rd portcullis; a portcullis block (raised / lowered states) in RP-01 |
| Doors | outer leaves behind the 1st portcullis; inner leaves at the ward end | inner leaves only | outer leaves |
| Murder holes | a row of 1 × 1 openings in the passage vault every 3 cells, under the gate chamber floor | none (chamber is solid, F6) | the vault + holes (iron bars or a grate block over them so villagers do not fall) |
| Guard rooms | one each side of the passage, door off the passage, loops into it (Harlech) | the porter's seat marker only | rooms + doors + loops |
| Gate chamber / winch room | over the passage: the portcullis winch, the murder-hole floor | solid fill | a room (F6) |
| Constable's / lord's lodging | floors over the chamber (Harlech constable; Beaumaris gatehouse hall) | none | 1–2 storeys of lodging over the gate (A: the lord's apartments live here) |
| Bent entry | Caernarfon 90° turn; Krak 137 m vaulted bent ramp | straight | seed: straight / one 90° turn (grand) |

### 3.4 Barbican, bridges, approach

| Part | Real | Blocks | HAS | MISSING |
|---|---|---|---|---|
| Barbican | Bodiam: barbican on a square island, the Octagon island, L-shaped bridge [W-BOD][TR-BOD]; Conwy two barbicans (east = garden) [W-CONWY]; Alnwick barbican 1475 [ALN]; Carcassonne 1240–50 [W-CARC] | a walled forecourt 16–24 × 12–16 in front of the gate, its own gate passage (1 portcullis), side walls 6–8 high with a walk | two r = 2 stub towers, no door, + a cobble strip | the forecourt, its gate, its walk |
| Bridges | L-shaped / zigzag timber bridge across a wide moat (Bodiam) | seed: straight causeway / L-bridge via an island | straight causeway | the L-bridge + island |
| Approach ramp | Hohenzollern zwinger "turns four times" [W-HOHEN] | castle on a knoll: a switchback of the 8-block ramp (preferred, 228) up to the barbican | none (land job only) | the approach as a piece of the castle group (gate-side pieces) |

### 3.5 Moat (K1 b, water law)

| Variant | Real | Blocks | Seed rule (design choice) |
|---|---|---|---|
| Wet moat | Bodiam 1.5–2.1 m deep, spring-fed [W-BOD]; Beaumaris moat (width not found this round) | 5–7 wide, water 2 deep over a 1-deep bed (now 5 wide, 3 deep) | `moat = wet` when the seed says moat AND the site survey finds water within 24 (feeds it) — else the castle places its own sources (K1 b) |
| Dry ditch | Conwy rock-cut ditch between the wards [W-CONWY]; Malbork dry moats [W-MAL] | 5–7 wide, 4–6 deep, grass bottom, steep faces (ramp-kit sides) | `moat = dry` on hill sites (the knoll) |
| Lake | Caerphilly lakes, dams 152 m, sluice tower [W-CAERPH]; Kenilworth mere [EH-KEN] | grand tier only, where the land job already holds a lake | the academy-castle (§8) |
| None | — | — | seed |

HAS: `moat(ring_cells, width=5, depth=3)` water sources + cobble bed, dug before the towers. MISSING: the dry and lake variants,
**the feed and the overflow** (§6.2), the moat's walk-around berm (2 wide between curtain foot and water — "Gunners Walk" type at
Beaumaris; width unverified).

### 3.6 Postern, sally port, water gate

| Real | Blocks | HAS | MISSING |
|---|---|---|---|
| Conwy postern down to a river dock [W-CONWY]; Harlech Way from the Sea, ~200 ft fortified stair [CW-HARL]; Beaumaris Gate next the Sea [W-BEAU]; Bodiam postern tower with its own drawbridge [NT-BOD]; Caernarfon Eagle Tower water gate in the basement [W-CAER]; Krak postern c. 1250 [W-KRAK] | every castle: one postern on the side opposite the gate (1-wide door, 1 portcullis, its own small bridge over the moat); where the site falls to water: a stair to a dock (the "sea stair") | none | all of it; R6 must seal the postern too |

## 4. Residential and service buildings

### 4.1 Keep / donjon (skin B, and every grand tier)

| Real | Blocks (design) | HAS (`keep()`) | MISSING |
|---|---|---|---|
| Vincennes 16.2 m square, 52 m, walls > 3 m, 6 floors, central column, corner turrets 6.6 m, latrine tower every floor, well ground floor, own chemise + moat [MED-VINC] | grand: 19 square, 36–44 high, walls 3, 6–7 storeys, corner turrets r 3 rising +5 | 15/19 square, `inner_h + 14` high (27–30), walls 2, storeys of 5, C_grand spiral centre, wooden double door at ground | walls 3; corner turrets; latrine turret |
| Hedingham 16 × 18 m, 21 m + turrets, walls 3.4 m, five floors, hall two storeys with a central arch [W-HED] | lord: 15–17 square, 24–28 high; **the hall storey is double height (9 clear)** with a mural gallery at mid-height; a transverse arch (stone stairs inverted / the 18:22 "flipped roof blocks" vault idea) | uniform 4-clear storeys | the double-height hall; the gallery; the arch |
| Dover: walls up to 6.4 m, two chapels and chambers in the wall thickness, spiral stairs in two corners, a deep well and lead pipes [CL-DOVER] | mural chambers 2 × 3 in the 3-thick walls (chapel / oratory / garderobe / bedchamber) | none | mural rooms |
| Keep entrance at first floor via a forebuilding (Norman keeps; Dover's forebuilding stair) **(unverified this round — Dover forebuilding not fetched)** | a forebuilding stair against the ward face up to the hall storey | ground-floor double door | optional by seed |
| Basement / well | Vincennes well on the ground floor; Bodiam well in a tower basement | a basement storey feet −5..−1 (stores, the well head, the cistern) | keep base is SOLID −3..−1 | basement |

Storey program (lord keep, bottom → top): basement stores + well; ground: guard room / store; 1st: great chamber of state (double
height, mural gallery); 3rd: solar + bedchamber (lord's household beds); 4th: chapel + chaplain's room; roof: walk + caphouse +
watch turret. Grand keep adds the treasury (behind a jib door) and the lord's private stair (B_tower spiral) to the solar.

### 4.2 Great hall (open roof + the diagonal skyway)

Real: hall "between one and a half and three times as long as it was wide, and also higher than it was wide", dais, screens
passage with two openings to buttery and pantry (R3 §1, local `civitas_research/R3-PALACES-GREAT-HOUSES.md`); Bodiam 7.3 × 12.2 m
[W-BOD]; Caernarfon 30.5 m long [W-CAER]; Conwy hall on cellars with stone diaphragm arches [W-CONWY]; Kenilworth "widest roofed
space in England after Westminster Hall" [EH-KEN]; Westminster's timber arches span ~18 m (R3).

| | Blocks (design) | HAS (`hall()`) | MISSING |
|---|---|---|---|
| Size | lord 11–13 wide × 26–32 long × 12–14 to the wall plate; grand 15–17 × 36–44 × 16 | 21 deep × 25 wide (lord, interior 19 × 23) × 10 — **wider than it is high, a 21-cell roof span (Westminster-class)** | re-proportion: 1 : 2.5, span ≤ 13 lord / 17 grand |
| Floor | open floor (no aisles) — what he asked for | open | — |
| Roof | OPEN timber roof to the ridge: trusses (rafter45 + spruce posts) every 4, no ceiling; the roof deck of roof45 above | hip roof directly on the walls (no visible trusses) | trusses; collar beams |
| Skyway | **no medieval precedent for a diagonal bridge across a hall** — the nearest are the minstrels' gallery over the screens and Hedingham-type galleries in the wall thickness [W-HED]. Design: a 2-wide mural gallery along both long walls at feet 7–8; ONE 45° skyway (the catwalk program's pieces, 17:58) across the hall at collar height from the gallery's upper-end corner to the lower-end corner opposite, crossing over the open floor; rails both sides | none | depends on the catwalk block set (queued program) — until then a straight cross-bridge at the screens end (minstrels' gallery) |
| Ends | dais 1 high at the upper end + the lord's door to the solar/great chamber; screens passage 2 wide at the lower end, two doors → buttery, pantry; the kitchen passage between them | dais 3 deep; double doors on the ward face | screens, buttery, pantry, kitchen passage, the dais door |
| Heat / light | central hearth + louvre, or wall fireplaces (pw:hearth + flue); tall windows both sides | windows, lanterns, light blocks | hearth + louvre |
| Below | cellars under the hall (Conwy) — §6.3 | smooth stone on dirt | cellars |

### 4.3 Lodgings ranges

Bodiam's domestic ranges were two storeys built against the curtain [TR-BOD]; Beaumaris was planned for two households [W-BEAU].
HAS: `lodgings()` — a free-standing range, corridor on the ward face, bays with one bed each, 2 storeys, C_grand/B spiral, hip roof.
MISSING: ranges BUILT AGAINST the curtain (share its wall; windows only on the ward face, loops outward), one bed per bay → 2–3
beds per chamber for retainers, garderobe recesses into the curtain behind each chamber, a stair at each end.

### 4.4 Kitchen, bakehouse, buttery, pantry, larder

Real: Bodiam kitchen with two hearths and bread ovens [NT-BOD]; Raby's separate kitchen tower with a domed roof [CST-RABY];
Harlech's bakehouse and granary in the ward [CW-HARL]; Alnwick's Great Kitchen (Salvin) [ALN]; Neuschwanstein's service lift to the
dining room [W-NEU].
Blocks: lord kitchen 9 × 13 × 8 with 2 hearths + ovens, a louvre, a drain gully to the sewer (§6.2), the passage to the screens;
grand: a kitchen TOWER 13 × 13 with a pyramidion roof and a central louvre; bakehouse 7 × 9; buttery + pantry 4 × 5 each;
larder/wet larder in the cellar.
HAS: `kitchens()` 13 × 15 × 6, one hearth + flue, barrels, table, a counter station, hip roof. MISSING: second hearth / oven,
the screens link, bakehouse, buttery, pantry, drain.

### 4.5 Chapel

Real: Krak 21.5 × 8.5 m barrel vault [W-KRAK]; Bodiam chapel with an oratory above [NT-BOD]; Beaumaris chapel in a tower
[W-BEAU]; Dover two chapels in the keep [CL-DOVER]; Vincennes' Sainte-Chapelle-type chapel 1379 [MED-VINC].
Blocks: lord 19–21 × 9 × 10; grand chapel royal 25–29 × 11 × 14 with a gallery (the lord's pew) reached from the apartments.
HAS: `chapel()` 17 × 13 × 8 (near square). MISSING: the long proportion, a vault (the 18:22 flipped-roof idea), the chaplain's
room, the oratory / lord's gallery.

### 4.6 Wells and cisterns

Real: Conwy 28 m spring-fed [W-CONWY]; Dover 88 m (289 ft) + rain gutters → lead pipes [CL-DOVER]; Krak's aqueduct-fed open cistern
[W-KRAK]; Bodiam's well in a tower basement [W-BOD]; Vincennes' well in the donjon [MED-VINC].
HAS: one well in the ward centre: a 1 × 1 water column feet −6..−1, a cobble ring. MISSING: the shaft to the sewer level (D-C533
well template law: lined 1 × 1 shaft from the well bottom to the trench level); a second well in the keep basement (B / grand); a
roof-water cistern under the inner ward (4 × 4 × 3, fed by downpipes from the hall roof valleys — Dover's principle; design choice).

## 5. Hidden ways and the prison

(The garrison, household and bailey are §7.)

### 5.5 Secret passages (documented) and how ours are built

| Real, documented | Our form |
|---|---|
| Dover: 13th-c. tunnels linking the spur and St John's Tower to the northern entrance, built after the 1216 siege [KENT-DOVER] | a SALLY TUNNEL: from the keep basement (or an A inner tower basement) under the ward and the curtain at feet −8..−6 (1 wide × 2 high, lit), rising by a B_tower spiral to the postern's outer face or a hidden door in the moat berm |
| St Andrews: mine and countermine of 1546–47 ("low, narrow, twisting countermine") [UND-STA] | grand tier: a countermine gallery under the gate front — a curiosity passage with a jib-panel entry |
| Versailles / Palazzo Vecchio / Hampton Court jib doors, private stairs (R3 §2.2, local) | the lord's private B_tower stair from the solar to the chapel gallery and to the keep basement; jib panels (`pw:jib_panel`) and the secret painting (`pw:secret_painting`) — both in the kit, unused by castles |
| Mural passages (Beaumaris / Caernarfon first-floor passages) [W-BEAU] | the inner curtain's mural passage (§3.1) doubles as the hidden way between towers |

### 5.6 Dungeon, prison, oubliette — flag the myths

- "dungeon" = donjon, the keep; castle prisons "often served only a temporary need", "simply a single plain room with a heavy door or
  accessible only from a hatchway"; "Many chambers described as dungeons or oubliettes were in fact water-cisterns or even latrines";
  their number "is often exaggerated to interest tourists"; Warwick's Caesar's Tower chamber is judged a latrine [W-DUNG].
- REAL bottle dungeon: St Andrews, "a bottle shaped pit dug 22ft down into the rock below the Sea Tower", entered by a trap door in
  the tower vault [UND-STA].
- Ours: a LOCK-UP in the gatehouse ground floor (iron door, the constable's custody — he is "responsible for the prisoners", R3
  §4) on every castle; ONE bottle pit (−7..−1, 3 wide at the bottom, a 1 × 1 neck with a trapdoor) only in grand castles, labelled
  as a curiosity. CIVITAS has no crime and no violence today (his 10:15 drop list) → no gameplay; the room is architecture.

## 6. Subsurface infrastructure (the WATER law; "ALL of our structures include subsurface infrastructure")

The box already reaches feet −15. Levels (design): −1 paving / floors · −2..−5 cellars, basements, cistern · −6..−9 tunnels and
culverts · −13 the sewer trench (city standard, the street trench level, D-C533 / the 1006 water design) · −14 trench bed.

### 6.1 What every castle piece carries

| Item | Where | Blocks |
|---|---|---|
| Ward drains | every 16 × 16 of paved ward: a 1 × 1 gully (iron-bar or copper-grate cover) → a 1-wide culvert at −6 falling to the trench | grate + stone-brick lined culvert |
| Garderobe shafts | each garderobe recess (curtain, keep turret, lodgings): a 1 × 1 chute in the wall thickness down to −6 → culvert. Historically they "drained directly into the moat" (Bodiam's 28) [W-BOD] or into cesspools "cleaned by servants" [UO-GARD] — **we route them to the sewer** (water law; the moat stays clean) | chute = air shaft in the masonry; seat = pw:furn_stool stand-in or a new seat block |
| Kitchen drain | the kitchen court's sewer entrance (palace law: "kitchen court" listed) | gully + culvert |
| Stable-yard drain | the stables' gully | gully + culvert |
| Well shaft | D-C533: lined 1 × 1 shaft of sources from the well bottom to the trench level | as the well template |
| Cistern | inner ward, −2..−4, 4 × 4, fed by downpipes; overflow to a culvert | water sources + overflow lip |
| Trench | a ring trench at −13 under the ward edge, joined to the town's street trench at the gate (K6: the gate faces the square, so the town trench meets the castle trench under the gate passage) | as the street trench |
| Outfall | the castle's own outfall where the ground falls away (a dry-ditch face or the lake side) | as the city outfall |

### 6.2 The moat as captured water (Caerphilly's sluice, Krak's cistern-moat)

The CASCADE TEST (15:0x 10-05) proved: a dammed body + a 1–2 wide lip feeds a stepped race forever, steady, without new sources
(98 flowing, 0 sources; a closed trench backs up nothing). Design for every wet moat:
1. The moat is placed as sources (K1 b) in s0, as now.
2. A **SLUICE TOWER** (Felton's Tower precedent [W-CAERPH]) on the moat's downhill corner: a 1-wide lip through the counterscarp at
   water level → a 3-step stone race → a basin with a fountain jet (the "fountain/waterfall structure") → a 1 × 1 drop shaft →
   culvert at −13 → the castle trench → the outfall.
3. Where the site survey finds a pond/lake/stream touching the castle block, its lip feeds the MOAT's upstream end (the water law's
   capture) through a lined race; the moat overflow is the sluice above.
4. Dry moat castles still carry the drop shaft for rainwater in the ditch bottom (a gully every 24).

### 6.3 Cellars and basements

Conwy's great hall and chapel stood "on top of the cellars" [W-CONWY]; Krak's vaulted space below served as storage and stabling
[W-KRAK]. Design: a vaulted cellar under the hall (−5..−2, 3 clear, reached from the buttery stair), the keep basement, tower
basements (stores; one is the lock-up's lower cell in grand castles), the cistern. All are rooms in the verifier (R2) and roofed
by definition (R7 passes).

### 6.4 Engine limits that shape the underground

- The structure box bottom is −15; a Conwy-depth well (28) cannot be one piece's content → the well shaft ends at the trench (−13)
  as the city's wells do; depth is implied.
- Water in a structure file is placed as sources; flowing water exists only by the engine; drains must therefore be EMPTY channels
  with a source only where the design wants one (the fountain jet). The verifier (R10, §11) checks the count of sources outside the
  moat / cistern / well = 0.
- The 1006 sewer design's trench level is the contract; the castle never invents its own level.

## 7. Garrison, household and bailey buildings

### 7.1 The paid guard body (K2 b) — lodged the medieval way

Real: medieval troops were billeted; purpose-built barracks begin in the 18th century ("Berwick Barracks … begun in 1717"; a
company "of some sixty men, four to a room, two to a bed", quadrangles round a parade ground) [W-BARR]. Inside castles the garrison
lodged in towers and gatehouses: Krak's knights lived in four round towers, ~60 [W-KRAK]; Conwy's first garrison was 30 soldiers incl.
15 crossbowmen + carpenter, chaplain, blacksmith, engineer, stonemason [W-CONWY].
So the castle gets **garrison lodgings, not a barracks block**:

| Step (as population rises, K2) | Men (design choice, Conwy / Krak anchored) | Where they sleep |
|---|---|---|
| G1 lord's castle laid | constable + 6 | the gatehouse: constable's lodging over the gate; 6 bunks in the two guard rooms' upper floors |
| G2 | + 12 (= 19) | tower floors: each r 3 tower floor holds 2 beds, r 4 holds 4 (4 towers × 1 floor) |
| G3 | + 11 (= 30, Conwy) | a two-storey garrison range against the outer curtain (A: in the outer ward; B: the base court) with a mess hall, armoury, 12 beds |
| G4 grand | → 60 (Krak's knights) | the new ring's towers + a second range; a muster yard (the outer ward) |

Beds are built at tier time; men are recruited by the clock against the population thresholds — empty beds are normal.
HAS: no garrison beds. MISSING: all four steps, the armoury (barrels / item frames), the mess, the guard-room stations (markers).

### 7.2 The household (K5 a) — a chamber for every office

| Office | Room (design) | Piece |
|---|---|---|
| Castellan / constable | over the gatehouse (Harlech) | gate piece |
| Steward | chamber off the screens passage + a muniment/counting room (lectern) | hall piece |
| Chaplain | room beside / over the chapel (Bodiam's oratory) | chapel piece |
| Marshal | room over the stables' end | bailey piece |
| Cooks (2) | loft over the kitchen | kitchen piece |
| Grooms (2–4) | hayloft over the stables | bailey piece |
| Lord + family (+ children's beds, 18:22) | keep solar (B) / gatehouse apartments (A) | keep / gate piece |
HAS: the lord's 2 beds (B keep), lodgings' 4–6 beds. MISSING: every office chamber above.

### 7.3 Stables, smithy and the working bailey

Real: Conwy's garrison came with a blacksmith, carpenter, engineer and mason [W-CONWY]; Caerphilly's north dam "may have supported
the castle's stables" [W-CAERPH]; Alnwick's Stable Court and riding school (listing title [HE-ALN]); Harlech's granary and bakehouse
[CW-HARL]; Bodiam's dovecote in a tower [NT-BOD]; Guédelon's working site with a communal oven, mill and gardens [W-GUED].

| Building | Blocks (design) | HAS | MISSING |
|---|---|---|---|
| Stables | 9 × 21 lean-to against the curtain, stalls 2 × 3, hay loft (grooms), drain | `stables()` 11 × 15 plank box, hay + fences, thatch gable | lean-to form, stalls, loft, drain |
| Smithy | 7 × 9, open front, pw:hearth + anvil + water trough, drain | none | all |
| Carpenter / mason lodge | 7 × 11 open shed | none | all (also the castle's repair crew → weathering law) |
| Granary | 7 × 11 on a raised floor (staddle stones = stone walls stubs) | none | all |
| Bakehouse / brewhouse | 7 × 9 each, an oven | none | all |
| Dovecote | a round 5-wide tower with nest-box walls (or inside a mid tower, Bodiam) | none | all |
| Well-house / horse trough | — | ward well | trough fed from the cistern overflow |

### 7.4 Thatch-gabled buildings (his 12:20)

All bailey timber buildings take `roof_gable(..., "thatch")` (roof45_thatch + roof45_ridge_thatch; gable ends in the curtain stone
or in plank/plaster for timber buildings). Never on towers, never hipped (no thatch hip exists; "thatch hips later"). Note: the
historic basis for thatch inside castle baileys was NOT verified this round — this is his ruling, applied as a style choice.

## 8. The academy towers and the academy-castle (K3 a = four; K7 b)

Standing law: an ORIGINAL academy-castle, never Hogwarts. Precedent used: Uraniborg's research-house program [W-URAN] + the collegiate
rooms already listed in the 10-05 design (§3 there).

### 8.1 One academy tower (×4, each with its own house colour/material from the seed)

| Level | Program (Uraniborg-derived) | Blocks |
|---|---|---|
| −5..−2 | basement: laboratory (Uraniborg's "alchemical laboratory") + stores | 13 × 13 vaulted |
| ground | common hall (hearth, tables) + the porter's seat | 13 × 13 × 6 |
| 1–4 | dormitory floors: 8 small rooms each (Uraniborg's loft "eight smaller rooms for students"), a B_tower spiral in the core | 4 storeys × 4 clear |
| 5 | masters' / tutors' chamber + a small library (Uraniborg's south tower library) | 13 × 13 |
| roof | observatory deck with a domed/shuttered instrument room (Stjerneborg) | caphouse + parapet |
Footprint: round r 7 (15 across, = Uraniborg's 15 m house) or square 15; height 36–42. One tower = 32 beds. Each tower sits in its
own quadrant piece of the academy group.

### 8.2 The academy-castle group

256 × 256 core (4 × 4 pieces) + land shaping to ~384 (lake, cliff, forest edge — land job only, no structure cells): founder's hall
(the open-roof hall of §4.2 at grand size, with the skyway), the four towers at the quadrants, library + reading gallery, lecture
halls, refectory + kitchen tower, chapel, infirmary, gatehouse + viaduct, boathouse on the lake (the water gate), cloister, physic
garden, bell tower; hidden ways (jib panel, secret painting, the boathouse tunnel = the sally tunnel of §5.5). Water: the lake is the
moat-lake (§3.5) with its sluice → cascade in the cloister garden → sewers.

### 8.3 The academy city (K7 b)

Founded by the clock as a rare settlement whose seat IS the academy-castle (castle-first founding mode with `style = academy`);
growth follows the castle-first ladder (§9) with the academy towers as its tier markers. Frequency: rare (design choice: at most
one per world, only on a lake-cliff site).

## 9. Growth: from lord's castle to grand castle-palace (K4 c, C3)

Documented growth paths: Kenilworth (keep 1120s → Gaunt's hall palace 1370s → Leicester's glazed lodgings) [EH-KEN]; Alnwick
(1138 castle → towers + curtain from 1309 → barbican 1475 → Gothic palace 1750 → Salvin 1854–65) [ALN]; Raby (hall house → kitchen
tower 1373 → concentric 1381–88) [CST-RABY]; Vincennes (hunting lodge → donjon 1350–70 → 1,100 m enclosure, nine towers, chapel)
[MED-VINC]; Malbork (order castle → royal residence) [W-MAL]; Hohenzollern (palace on the old outline atop the casemates)
[W-HOHEN]; Chambord and Neuschwanstein as the end state (keep form, cross corridors, grand stair, throne/singers' halls, galleries,
service lift) [W-CHAM][W-NEU].

| Tier (clock) | Castle state | What is ADDED (pieces) | Real anchor |
|---|---|---|---|
| CT1 town III (or founding, castle-first) | lord's castle, centred in the RESERVED grand box | the 3 × 3 core pieces | Conwy / Bodiam / Beaumaris |
| CT2 city I | the town wall joins the castle's flank towers; barbican; garrison G3; bailey complete | the gate-side ring pieces (barbican, approach ramp) + the town-wall junction | Conwy / Caernarfon walls |
| CT3 city III — **grand castle-palace** | the inner ward rebuilt as a palace: state apartments in enfilade, long gallery, chapel royal, library, great hall at grand size with the open roof + skyway; keep heightened (corner turrets, latrine turret); a new outer ring (bastions or a second curtain) with gardens | the remaining ring pieces + core pieces RE-PLACED as their palace versions (`_t3`) | Kenilworth / Alnwick / Vincennes |
| CT4 metropolis | roofscape and towers of the palace-castle: cones/spires (French skin), a grand double spiral stair hall (Chambord), a throne hall 20 × 12 × 13 (Neuschwanstein), a gallery joining the buildings | core pieces `_t4`; no new footprint | Chambord / Neuschwanstein / Hohenzollern |

**Hard requirement:** a castle-first town must reserve the FINAL footprint at founding (site search for the 320 box + moat), so the
grand tier never collides with the town that grew below the gate. A town that gets its castle at tier-up (not castle-first) builds
the lord castle only and takes the PALACE road (K4 c) — it needs only the 192 reservation.

Rebuilding a core piece = placing its tier version over the old one (same origin, same rotation). Furniture/markers are re-laid by
the tier version; villager homes inside are restored per the 21:39 weathering-reset rule.

## 10. Recommended piece layout per castle variety

Fix F1 first. Then snap every castle to a multiple of 64 and CENTRE the content on the piece grid so the ward is a whole piece.
Height band cutter (10-05 §3b: s0 ground + feet < 0 · s1 masonry to feet 4 · s2 to the walk · s3 parapets/roofs/caps · s4
furnishings + markers, each ≤ ~60k cells) applies to every piece. The underground (§6) rides in s0 (it is "ground + feet < 0").

### 10.1 Skin A — concentric lord's castle: **192 × 192, 3 × 3 = 9 pieces** (now 128–160)

```
            x0 = gate side (faces the square, K6)
   +-----------+-----------+-----------+
   | A00 outer | A01 GATE  | A02 outer |   A01: outer + inner gatehouses, barbican, drawbridge pit, bridge, approach ramp
   | corner    | front     | corner    |        foot, the town trench junction, constable's lodging, lock-up
   +-----------+-----------+-----------+
   | A10 flank | A11 INNER | A12 flank |   A11: the 55 × 55 inner ward (Beaumaris 0.30 ha) + the inner curtain's inner
   | outer ward| WARD      | outer ward|        face: hall (on cellars), kitchen, chapel, lodgings against the curtain,
   | bailey    |           | bailey    |        well + cistern, ward drains. The lord lives in the inner gatehouse (A01).
   +-----------+-----------+-----------+   A10/A12: outer ward 18 wide (Beaumaris) — stables, smithy, granary, garrison
   | A20 outer | A21 REAR  | A22 outer |        range (G3), the flank D-towers, mural passage, moat side.
   | corner    | postern   | corner    |   A21: the rear inner D-tower, the POSTERN + water gate / sea stair, the
   +-----------+-----------+-----------+        sally tunnel's exit; A20/A22: corner towers, moat corners, the SLUICE TOWER on
                                              the downhill corner (seed picks which).
```
Grand A (CT3): **320 × 320, 5 × 5 = 25 pieces** — the 3 × 3 core in the middle (re-placed as `_t3`), a 16-piece ring: new outer
curtain with bastions (Hohenzollern / Carcassonne lists), gardens and the long gallery in the old outer ward, annexes (guard &
prison, commons, riding school) in the ring's corners.

### 10.2 Skin B — palace-block lord's castle: **192 × 192, 3 × 3 = 9 pieces** (re-planned, F8)

```
   +-----------+-----------+-----------+
   | B00 moat  | B01 BRIDGE| B02 moat  |   B01: the barbican island + Octagon island + L-bridge (Bodiam), drawbridge
   | + base    | barbican  | + base    |        pits, the approach; B00/B02: the moat-lake + the base court's front
   +-----------+-----------+-----------+
   | B10 BASE  | B11 THE   | B12 BASE  |   B11: the WHOLE quadrangle in ONE piece (Bodiam-scale): curtain 56 × 56,
   | COURT     | QUADRANGLE| COURT     |        court ~26 × 26, ranges 2 storeys against all four curtains (hall 9 × 18,
   | stables,  | (castle)  | garrison, |        great chamber, chapel + oratory, kitchen with 2 hearths, lodgings),
   | smithy    |           | granary   |        round corner towers + square mid towers, the gatehouse (3 portcullises,
   +-----------+-----------+-----------+        murder holes), the postern with its own drawbridge, the donjon at one corner
   | B20 moat  | B21 moat  | B22 moat  |        (Hedingham-size 16 × 16), garderobe shafts → culverts. B10/B12: base court
   | sluice    | postern   | gardens   |        (Raby/Kenilworth) — stables, smithy, garrison range, bakehouse, granary,
   +-----------+-----------+-----------+        thatch gables. B2x: moat-lake, sluice tower, postern bridge, gardens.
```
Grand B (CT3): **320 × 320, 5 × 5 = 25** — the quadrangle piece becomes the palace's inner court (re-placed `_t3`), the base courts
become the state wing and gallery wing (Chambord's keep-and-wings), the ring holds the new curtain, chapel royal, stables court,
guard & prison annex, gardens.

### 10.3 The academy-castle: **256 × 256, 4 × 4 = 16 pieces** + land shaping to ~384 (no structure cells beyond 256)

Quadrant pieces Q00/Q03/Q30/Q33 each hold one academy tower (§8.1); the centre 2 × 2 (Q11/Q12/Q21/Q22) holds founder's hall, the
stair hall, library, refectory + kitchen tower, cloister; the gate-side edge holds the gatehouse + viaduct; the lake-side edge holds
the boathouse, water gate and the sluice cascade.

### 10.4 Box heights

lord TOP 44 (keep), grand TOP 60–70 (Vincennes-class keep 36–44 + caps; a Neuschwanstein-type stair tower would need ~65 — design
choice: cap grand towers at 56 so pieces stay ≤ 64 × 86 × 64 and the band cutter keeps stages ≤ 60k cells). Bottom stays −15.

## 11. Verification additions (castle_verify.py — design only)

| Check | What it proves |
|---|---|
| R2 fix | room floor rectangles exclude spiral wells (closes the keep_4 8-cell artifact, F2) |
| R4 | gatehouse flank towers use the A_turret spiral (no fallback newel) — F3 |
| R6+ | with the gate AND the postern sealed nothing inside the curtain is reachable |
| R9 drains | every gully, garderobe chute, kitchen and stable drain connects by empty channel to the trench at −13, and the trench reaches the outfall |
| R10 water | sources only in moat / cistern / well shaft / fountain jet; 0 elsewhere (the "waterlog" class of bug, 10-05) |
| R11 beds | beds ≥ the tier's garrison step + household + family (§7) |
| R12 hidden | every secret passage is reachable from both ends; not reachable from the ward without passing a jib panel / painting |
| R13 pieces | the union of the written pieces equals the model (catches F1) |
| BDS walk (K8) | villagers path gate → ward → hall → keep/gatehouse lodging → wall-walk; the guard body's stations reachable |

## 12. Inventory table — everything the castle program needs

Priority: **P0** blocks "castles into the game"; **P1** needed for "constructed correctly / to scale"; **P2** later or optional.
"Kit" = a new RP-01/BP-02 block is required.

| # | Element | Real basis | Block dims | Piece (A / B) | castlegen HAS | MISSING | Pri |
|---|---|---|---|---|---|---|---|
| 1 | Piece cut | engine 64 × 64 | multiple of 64, centred | all | `cut()` floor division | ceil / centred cut (F1) | P0 |
| 2 | Height band stages | LC-1005-2 | ≤ 60k cells / stage | all | designed, not built | cutter | P0 |
| 3 | Grand footprint reservation | K4 c | 320 + moat | clock | none | site search for 320 | P0 |
| 4 | Underground levels, drains, trench, outfall | water law | §6 | every piece | none | all | P0 |
| 5 | Moat feed + sluice tower + cascade | Caerphilly, cascade test | §6.2 | A2x / B2x | wet moat sources | feed, overflow, cascade, dry + lake variants | P0 |
| 6 | Garrison lodgings G1–G4 | Conwy 30, Krak 60, Berwick | §7.1 | A01/A1x / B10/B12 | 0 beds | all | P0 |
| 7 | Household chambers | K5 | §7.2 | all | lord 2 beds | 6 offices | P0 |
| 8 | Grand palace program | Kenilworth, Alnwick, Chambord | §9 | core `_t3` | lord program only | all (shares PALACE II room builder) | P0 |
| 9 | Gatehouse true form | Caernarfon, Harlech, Bodiam | §3.3 | A01 / B11 | passage, 1 raised portcullis, twin towers | chamber, murder holes, grooves, 2–3 portcullises, guard rooms, lodging, pit | P1 |
| 10 | Drawbridge (turning bridge + pit) | Drawbridge article | 4 × 3 × 3 pit | A01 / B01 | causeway | pit, deck; Kit: deck/gaff/chain | P1 |
| 11 | Barbican + L-bridge + island | Bodiam, Conwy, Alnwick | 16–24 × 12–16 | A01 / B01 | 2 stubs | forecourt, gate, island, bridge | P1 |
| 12 | Postern / sally port / water gate | Conwy, Harlech, Bodiam, Beaumaris, Krak | 1-wide door + portcullis + bridge | A21 / B21 | none | all | P1 |
| 13 | Curtain thickness + mural passage + garderobes | Beaumaris, Bodiam 28 | 3 outer / 5 inner | edges | 2–3 solid | passage, recesses, chutes | P1 |
| 14 | Crenel 3 : 1, slits in merlons | Battlement | merlon 3, crenel 1 | edges | 1 : 1 | rhythm, slits | P1 |
| 15 | Tower spacing ≤ 32, storeys + basement, watch turrets | Carcassonne, Caernarfon, Conwy | §3.2 | edges | corners + mids | spacing rule, basements, turrets; gatehouse towers r 4 (F3) | P1 |
| 16 | Keep: walls 3, corner turrets, double-height hall + gallery, mural rooms, basement + well, latrine turret | Vincennes, Hedingham, Dover | §4.1 | B11 / grand core | 15/19 square, walls 2, uniform storeys, C spiral | listed | P1 |
| 17 | Great hall proportion, screens/buttery/pantry, open trusses, gallery, **diagonal skyway** | R3, Bodiam, Caernarfon, Hedingham | 11–13 × 26–32 lord | A11 / B11 | 21 × 25 box, hip roof, dais | listed; skyway needs the catwalk set (Kit) | P1 |
| 18 | Lodgings against the curtain | Bodiam | §4.3 | A11 / B11 | free-standing range | re-plan | P1 |
| 19 | Kitchen (2 hearths, ovens), bakehouse, buttery, pantry, kitchen tower (grand) | Bodiam, Raby, Harlech | §4.4 | A11 / B11 | 1 hearth box | listed | P1 |
| 20 | Chapel proportion, oratory, chaplain | Krak, Bodiam | 19–21 × 9 | A11 / B11 | 17 × 13 | listed | P1 |
| 21 | Well shaft to trench, keep well, cistern | Conwy, Dover, Krak, D-C533 | §4.6 | A11 / B11 | 6-deep column | listed | P1 |
| 22 | Bailey: stables (lean-to + loft), smithy, lodge, granary, bakehouse, dovecote — thatch gables | Conwy trades, Harlech, Bodiam, Alnwick | §7.3 | A1x / B10,B12 | stables box | 5 buildings + re-plan | P1 |
| 23 | B re-plan: compact quadrangle in one piece + base courts | Bodiam, Raby | §10.2 | B11 | 100-wide empty ward | re-plan (F8) | P1 |
| 24 | Academy tower ×4 + academy group | Uraniborg | §8 | academy Q pieces | none (academygen not started) | all | P1 |
| 25 | Secret ways: sally tunnel, lord's private stair, jib doors, countermine (grand) | Dover, St Andrews, R3 | §5.5 | A11→A21 / B11→B21 | jib/painting blocks exist, unused | all | P1 |
| 26 | Lock-up + bottle pit (grand), myths flagged | Dungeon article, St Andrews | §5.6 | A01 / B11 | none | all | P2 |
| 27 | Machicolations / bretèche | Machicolation, Krak, Conwy | 1-out corbel | gates, B towers | none | Kit: corbel; pattern | P2 |
| 28 | Cone / spire caps (French skin, CT4) | Carcassonne restoration | r-matched | towers | square hip caps | Kit: cone set (or roof63 + pyramidion) | P2 |
| 29 | Portcullis block (raised / lowered), cross arrow-slit block | Bodiam, Caernarfon | 1-cell | gates, walls | iron bars | Kit | P2 |
| 30 | Town-wall junction + gap-backed town towers with plank bridges | Conwy, Caernarfon walls | §3.2 | clock (city wall) | none | template + clock | P2 |
| 31 | Approach ramp switchbacks (8-block ramp preferred) | Hohenzollern | ramp kit | A01 / B01 | none | piece content | P2 |
| 32 | Glacis on the weak side | Krak | roof63 stone | edges | none | Kit: stone roof63 skin | P2 |
| 33 | Verifier R9–R13 + R2/R4 fixes | — | §11 | — | R1–R8 | listed | P0 (R13) / P1 |
| 34 | Regenerate the variety sheet | stale 18:42 PNG | — | — | stale headers | regenerate | P1 |

## 13. Sources

Fetched this round (quotes above come from these pages):
- [W-BEAU] Beaumaris Castle — Wikipedia: https://en.wikipedia.org/wiki/Beaumaris_Castle
- [WH-BEAU] Beaumaris Castle — World History Encyclopedia: https://worldhistory.org/Beaumaris_Castle
- [W-CAER] Caernarfon Castle — Wikipedia: https://en.wikipedia.org/wiki/Caernarfon_Castle
- [W-CAERTW] Caernarfon town walls — Wikipedia: https://en.wikipedia.org/wiki/Caernarfon_town_walls
- [W-CONWY] Conwy Castle — Wikipedia: https://en.wikipedia.org/wiki/Conwy_Castle
- [W-CONWYTW] Conwy town walls — Wikipedia: https://en.wikipedia.org/wiki/Conwy_town_walls
- [CW-HARL] Harlech Castle — castlewales.com: https://castlewales.com/harlech.html
- [W-BOD] Bodiam Castle — Wikipedia: https://en.wikipedia.org/wiki/Bodiam_Castle
- [NT-BOD] Exploring Bodiam Castle — National Trust: https://nationaltrust.org.uk/visit/sussex/bodiam-castle/exploring-bodiam-castle
- [TR-BOD] Bodiam Castle — timeref.com: https://timeref.com/places/bodiam_castle.htm
- [W-KRAK] Krak des Chevaliers — Wikipedia: https://en.wikipedia.org/wiki/Krak_des_Chevaliers
- [MED-VINC] Château de Vincennes — medieval.eu: https://www.medieval.eu/chateau-de-vincennes/
- [CL-DOVER] The Great Tower at Dover Castle — Country Life: https://www.countrylife.co.uk/out-and-about/the-great-tower-at-dover-castle-248464?lazyload=0
- [KENT-DOVER] Medieval tunnels beneath the Spur Redan, Dover Castle — Kent HER MKE111638: https://heritage.kent.gov.uk/Monument/MKE111638
- [W-HED] Hedingham Castle — Wikipedia: https://en.wikipedia.org/wiki/Hedingham_Castle
- [WAR] Towers & Ramparts — Warwick Castle: https://www.warwick-castle.com/explore/things-to-do/attractions/towers-ramparts/
- [ALN] Castle history — Alnwick Castle: https://alnwickcastle.com/explore/history/castle-history
- [HE-ALN] The Castle, Stable Court and Covered Riding School (listing) — Historic England: https://www.historicengland.org.uk/listing/the-list/list-entry/1371308 (title only, not fetched)
- [EH-KEN] Significance of Kenilworth Castle — English Heritage: https://www.english-heritage.org.uk/visit/places/kenilworth-castle/history-and-stories/history/significance/
- [CST-RABY] The Medieval Development of Raby Castle — Castle Studies Trust: https://castlestudiestrust.org/blog/?p=2190
- [W-CAERPH] Caerphilly Castle — Wikipedia: https://en.wikipedia.org/wiki/Caerphilly_Castle
- [W-MAL] Malbork Castle — Wikipedia: https://en.wikipedia.org/wiki/Malbork_Castle
- [W-CARC] Cité de Carcassonne — Wikipedia: https://en.wikipedia.org/wiki/Cit%C3%A9_de_Carcassonne
- [W-HOHEN] Hohenzollern Castle — Wikipedia: https://en.wikipedia.org/wiki/Hohenzollern_Castle
- [W-CHAM] Château de Chambord — Wikipedia: https://en.wikipedia.org/wiki/Ch%C3%A2teau_de_Chambord
- [W-NEU] Neuschwanstein Castle — Wikipedia: https://en.wikipedia.org/wiki/Neuschwanstein_Castle
- [W-URAN] Uraniborg — Wikipedia: https://en.wikipedia.org/wiki/Uraniborg
- [W-BATT] Battlement — Wikipedia: https://en.wikipedia.org/wiki/Battlement
- [W-MACH] Machicolation — Wikipedia: https://en.wikipedia.org/wiki/Machicolation
- [W-DRAW] Drawbridge — Wikipedia: https://en.wikipedia.org/wiki/Drawbridge
- [W-DUNG] Dungeon — Wikipedia: https://en.wikipedia.org/wiki/Dungeon
- [UND-STA] St Andrews Castle — Undiscovered Scotland: https://www.undiscoveredscotland.co.uk/standrews/standrewscastle/
- [W-BARR] Barracks — Wikipedia: https://en.wikipedia.org/wiki/Barracks
- [UO-GARD] Garderobes of castles in medieval England — University of Oregon blog: https://blogs.uoregon.edu/wc75/2021/02/01/garderobes-of-castle-in-medieval-england
- [W-GUED] Guédelon Castle — Wikipedia: https://en.wikipedia.org/wiki/Gu%C3%A9delon_Castle
- [W-BAST] Bastide — Wikipedia: https://en.wikipedia.org/wiki/Bastide — grid of insulae, central market square with arcades
  (couverts), church "almost never on the central square", house lots "8 m (26 ft) by 24 m (79 ft)", streets "6–10 m", alleys
  "2–2.5 m" to "5–6 m", "Almost 700 bastides … between 1222 … and 1372", most first unwalled. (Used for §9's town below the gate:
  the CIVITAS street width 7 and plot depths already sit inside these ranges.)

Local (project) sources: `_docs/civitas_research/R3-PALACES-GREAT-HOUSES.md` (hall proportion, jib doors, documented secret
passages, constable/steward/porter roles); `_docs/CIVITAS-CITY-PLANNING-DESIGN-2026-10-03.md` §6 (well shaft + trench law);
`_logs/decision_journal.md` (rulings).

NOT verified this round (stated as design choices above): Beaumaris moat width and the "Gunners Walk" width; Dover's forebuilding;
Malbork's dansker latrine tower; Pierrefonds' plan (page held no plan data); thatch inside castle baileys; typical tower diameters.
