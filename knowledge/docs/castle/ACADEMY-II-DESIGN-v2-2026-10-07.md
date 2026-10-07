# ACADEMY II — DESIGN v2 (2026-10-07)

Status: plan stage, design only — nothing built, nothing shipped. Ruling: D-C1006-ACAD2 (decision_journal).
Source of truth: `/home/claude/_staging/castle231/academy2v2/acad2v2_layout.py` (md5 60848e35cf49ba0bfa058298b5584667);
renderer `acad2v2_render.py` (md5 552dbe80ce52e9a8a5e632d3a71bcf83). Images: `/home/claude/_docs/castle/academy2_v2/`.

Frame: x = depth from the gate (x 0 = gate / town side), z = frontage, both 0..383 (6 x 6 pieces of 64). Inclusive rects, 1 block = 1 m.
Levels: G feet 0 · U feet 6 · B1 rooms feet -7 · B2 tunnels feet -12 · sewer trench -13 · quay -12.

## 1. What changed from v1
- v1: a ring of separate ranges round a walled core (inner curtain, dry ditch, clock tower, lake tower).
- v2: **one central building** on the gate–lake axis — Entrance Range → Great Hall → Central Tower — with wings and auxiliary buildings round it, **courts between them**, and **covered cloister walks joining every building**.
- Removed: inner curtain, dry ditch, orangery, sunken observatory, lake tower, clock tower (clock moves into the Central Tower), Guest House ring.
- Added: Forecourt, Scholars' / Masters' Courts, Hall Garth, Library and Chapel Courts, four House Towers with two Dorm Ranges, Ice House (Library Court).
- All 39 secrets re-sited on v2 rooms; each now carries its palace source (`SECRET_SOURCES`). Renamed: 12 Hall Roof Trusses, 30 Infirmary Stove Passage, 31 Matron's Door under the Hangings.
- **Central Tower position is AWAITING Abs0lum's answer** — it stands behind the hall (lake side), x 220-251, z 172-211; not moved.
- overlaps(): G [] · U [] · B [].

## 2. Ground floor (G)
| Room | Category | Rect (x0,z0,x1,z1) | Size (depth x frontage) |
|---|---|---|---|
| FORECOURT | court | (23, 100, 95, 283) | 73 x 184 |
| SCHOLARS' COURT | court | (100, 100, 149, 155) | 50 x 56 |
| MASTERS' COURT | court | (100, 228, 149, 287) | 50 x 60 |
| HALL GARTH | court | (150, 128, 219, 153) | 70 x 26 |
| LIBRARY COURT | court | (256, 100, 305, 170) | 50 x 71 |
| CHAPEL COURT | court | (256, 214, 305, 290) | 50 x 77 |
| Gatehouse | gate | (3, 176, 22, 207) | 20 x 32 |
| Entrance Range | hall | (110, 172, 149, 211) | 40 x 40 |
| GREAT HALL | hall | (150, 156, 219, 227) | 70 x 72 |
| Central Tower | tower | (220, 172, 251, 211) | 32 x 40 |
| Kitchens | hall | (150, 228, 179, 251) | 30 x 24 |
| Schools Wing | learn | (150, 96, 219, 125) | 70 x 30 |
| Laboratories | lab | (220, 96, 251, 125) | 32 x 30 |
| Observatory Wing | lab | (220, 60, 251, 95) | 32 x 36 |
| Library | learn | (256, 60, 305, 99) | 50 x 40 |
| Infirmary | sacred | (220, 228, 251, 251) | 32 x 24 |
| Masters' Lodgings | lodge | (150, 252, 219, 287) | 70 x 36 |
| Rector's Lodge | lodge | (220, 252, 251, 287) | 32 x 36 |
| Chapel | sacred | (260, 292, 303, 325) | 44 x 34 |
| Junior School | child | (100, 300, 149, 340) | 50 x 41 |
| Stables + Stores | service | (24, 20, 39, 95) | 16 x 76 |
| House Tower I | tower | (40, 40, 79, 79) | 40 x 40 |
| Dorm Range I | tower | (80, 40, 99, 79) | 20 x 40 |
| House Tower II | tower | (40, 304, 79, 343) | 40 x 40 |
| Dorm Range II | tower | (80, 304, 99, 343) | 20 x 40 |
| House Tower III | tower | (272, 20, 303, 51) | 32 x 32 |
| House Tower IV | tower | (272, 332, 303, 363) | 32 x 32 |
| Ice House | service | (290, 150, 298, 158) | 9 x 9 |
| Porch Walk | passage | (96, 186, 109, 197) | 14 x 12 |
| Gate Cloister | passage | (96, 80, 99, 291) | 4 x 212 |
| Left Cloister (z0 side) | passage | (100, 96, 255, 99) | 156 x 4 |
| Right Cloister (z383 side) | passage | (100, 288, 255, 291) | 156 x 4 |
| Lake Cloister | passage | (252, 96, 255, 291) | 4 x 196 |
| Walk to T3 | passage | (256, 52, 271, 55) | 16 x 4 |
| Walk to T4 | passage | (256, 328, 271, 331) | 16 x 4 |
| Walk to T1 | passage | (80, 80, 95, 83) | 16 x 4 |
| Walk to T2 | passage | (80, 300, 95, 303) | 16 x 4 |

## 3. Covered walk network (G, cat "passage")
- Porch Walk: (96, 186, 109, 197), 14 x 12
- Gate Cloister: (96, 80, 99, 291), 4 x 212
- Left Cloister (z0 side): (100, 96, 255, 99), 156 x 4
- Right Cloister (z383 side): (100, 288, 255, 291), 156 x 4
- Lake Cloister: (252, 96, 255, 291), 4 x 196
- (link strip): (150, 126, 219, 127), 70 x 2
- (link strip): (150, 154, 219, 155), 70 x 2
- Walk to T3: (256, 52, 271, 55), 16 x 4
- Walk to T4: (256, 328, 271, 331), 16 x 4
- Walk to T1: (80, 80, 95, 83), 16 x 4
- Walk to T2: (80, 300, 95, 303), 16 x 4
- The Gate, Left, Right and Lake Cloisters make a closed ring (x 96-255, z 96-291); the Porch Walk joins it to the Entrance Range; four walks reach the House Towers; Walk to T3 is the two-level Covered Bridge (secret 28).

## 4. Upper floor (U, feet 6)
| Room | Category | Rect (x0,z0,x1,z1) | Size (depth x frontage) |
|---|---|---|---|
| Printing House | gate | (3, 176, 22, 191) | 20 x 16 |
| Steward | gate | (3, 192, 22, 207) | 20 x 16 |
| Grooms' loft | service | (24, 20, 39, 95) | 16 x 76 |
| T1 dorm | tower | (40, 40, 79, 79) | 40 x 40 |
| Dorm I upper | tower | (80, 40, 99, 79) | 20 x 40 |
| T2 dorm | tower | (40, 304, 79, 343) | 40 x 40 |
| Dorm II upper | tower | (80, 304, 99, 343) | 20 x 40 |
| T3 dorm | tower | (272, 20, 303, 51) | 32 x 32 |
| T4 dorm | tower | (272, 332, 303, 363) | 32 x 32 |
| Proctors | gate | (110, 172, 129, 191) | 20 x 20 |
| Council | gate | (110, 192, 129, 211) | 20 x 20 |
| Exam Hall | learn | (130, 172, 149, 211) | 20 x 40 |
| GREAT HALL (open roof) | hall | (150, 156, 219, 227) | 70 x 72 |
| LONG GALLERY | learn | (150, 96, 219, 111) | 70 x 16 |
| Drawing Studio | learn | (150, 112, 189, 125) | 40 x 14 |
| Map Room | secret | (190, 112, 197, 125) | 8 x 14 |
| Music (organ loft) | learn | (198, 112, 219, 125) | 22 x 14 |
| Optics + Mechanics | lab | (220, 96, 251, 125) | 32 x 30 |
| Astronomer | lab | (220, 60, 251, 95) | 32 x 36 |
| SCR | tower | (220, 172, 231, 187) | 12 x 16 |
| Exhib. | tower | (240, 172, 251, 187) | 12 x 16 |
| Instr. | tower | (220, 196, 231, 211) | 12 x 16 |
| Clock room | tower | (240, 196, 251, 211) | 12 x 16 |
| Cooks' loft | hall | (150, 228, 179, 251) | 30 x 24 |
| Infirmary nurses | sacred | (220, 228, 251, 251) | 32 x 24 |
| Masters' sets (upper) | lodge | (150, 252, 219, 287) | 70 x 36 |
| Rector bed | lodge | (220, 252, 235, 271) | 16 x 20 |
| Study | lodge | (236, 252, 251, 271) | 16 x 20 |
| Dressing | lodge | (220, 272, 235, 287) | 16 x 16 |
| Oratory | sacred | (236, 272, 247, 287) | 12 x 16 |
| Vice | lodge | (248, 272, 251, 283) | 4 x 12 |
| Supper | secret | (248, 284, 251, 287) | 4 x 4 |
| Tribune | sacred | (260, 292, 303, 299) | 44 x 8 |
| CHAPEL (void) | sacred | (260, 300, 303, 325) | 44 x 26 |
| LIBRARY upper gallery | learn | (256, 60, 305, 91) | 50 x 32 |
| Reading closets | learn | (256, 92, 297, 99) | 42 x 8 |
| Dbl hide | secret | (298, 92, 305, 99) | 8 x 8 |
| Night A | child | (100, 300, 115, 319) | 16 x 20 |
| Night B | child | (116, 300, 131, 319) | 16 x 20 |
| Day Room | child | (132, 300, 149, 319) | 18 x 20 |
| Governess | child | (100, 320, 115, 340) | 16 x 21 |
| Nurses | child | (116, 320, 131, 340) | 16 x 21 |
| Wash | child | (132, 320, 149, 340) | 18 x 21 |
| Covered bridge (upper) | passage | (252, 52, 271, 55) | 20 x 4 |

## 5. Basement (B1 -7 / B2 -12 / sewer -13)
| Room | Category | Rect (x0,z0,x1,z1) | Size (depth x frontage) |
|---|---|---|---|
| Guard cellar | gate | (3, 176, 22, 207) | 20 x 32 |
| T1 cellar | tower | (40, 40, 79, 79) | 40 x 40 |
| T2 cellar | tower | (40, 304, 79, 343) | 40 x 40 |
| T3 cellar | tower | (272, 20, 303, 51) | 32 x 32 |
| T4 cellar | tower | (272, 332, 303, 363) | 32 x 32 |
| Dorm I cellar | service | (80, 40, 95, 59) | 16 x 20 |
| Sewer hide | secret | (84, 62, 95, 72) | 12 x 11 |
| Lock-up (Pozzi) | gate | (110, 172, 129, 191) | 20 x 20 |
| Bursary vault | gate | (110, 192, 129, 211) | 20 x 20 |
| Porters' cellar | hall | (130, 172, 149, 211) | 20 x 40 |
| UNDERCROFT | hall | (150, 156, 189, 227) | 40 x 72 |
| WINE CELLAR | service | (190, 156, 219, 191) | 30 x 36 |
| Serving (under dais) | hall | (190, 192, 219, 227) | 30 x 36 |
| Wet larder | service | (150, 228, 179, 251) | 30 x 24 |
| Schools stores | learn | (150, 96, 219, 125) | 70 x 30 |
| Lab cellar | lab | (220, 96, 251, 125) | 32 x 30 |
| Alchemist's Vault | lab | (220, 60, 251, 95) | 32 x 36 |
| MUNIMENT ARCHIVE | learn | (220, 172, 251, 211) | 32 x 40 |
| Mortuary | sacred | (220, 228, 251, 251) | 32 x 24 |
| Masters' cellars | lodge | (150, 252, 219, 287) | 70 x 36 |
| Rector's cellar | lodge | (220, 252, 251, 287) | 32 x 36 |
| Book cellar | learn | (256, 60, 305, 99) | 50 x 40 |
| FOUNDERS' CRYPT | sacred | (260, 292, 303, 325) | 44 x 34 |
| CATACOMBS | catacomb | (264, 222, 303, 285) | 40 x 64 |
| Junior service floor | child | (100, 300, 149, 340) | 50 x 41 |
| Ice | service | (292, 152, 296, 156) | 5 x 5 |
| Basin | water | (296, 184, 311, 199) | 16 x 16 |
| WATER GATE canal | water | (312, 188, 383, 195) | 72 x 8 |
| Outfall | water | (320, 324, 335, 337) | 16 x 14 |
| QUAY (-12) | court | (320, 16, 343, 187) | 24 x 172 |
- B2 tunnels: gatehouse → junction (x 23-235, z 191-192); junction → basin (z 192-193); junction → crypt (x 236-237 to z 291, then to the crypt at z 299); dry well → quay (x 184-319, z 140-141); ice well → well tunnel.
- Sewers: gate-side main x 97-98 and lake-side main x 253-254 (z 40-331), cross main z 330-331 to the outfall on the quay (Baddesley "sewers run the length of the building").
- Multi-level secret routes (B_ROUTES):
- 26: [(184, 140), (300, 141), (320, 141)]
- 27: [(97, 60), (97, 67), (90, 67)]
- 32: [(294, 154), (294, 141)]
- 33: [(248, 200), (248, 193), (296, 193)]
- 17: [(200, 205), (210, 192)]
- 3: [(20, 206), (23, 192)]
- 20: [(140, 206), (128, 206), (120, 196)]

## 6. Secrets — each tied to a documented palace feature
| # | Secret | Level | Marker (x,z) | Room | Palace feature (PALACE-II-RESEARCH-2026-10-06) |
|---|---|---|---|---|---|
| 1 | Masters' Spine (jib doors) | G | (184, 270) | Masters' Lodgings | Versailles - service rooms behind the Queen's apartment / hidden spine H1 (S1.1, S4.5) |
| 2 | Stoking Passage | G | (200, 124) | Schools Wing | Schonbrunn - stoves stoked from a passage behind the walls (S1.7) |
| 3 | Porter's Stair in the Wall | G | (12, 206) | Gatehouse | Palazzo Vecchio - Brienne stair carved into the thickness of the wall (S1.4) |
| 4 | Mural Passage | U | (1, 120) | wall | Passetto di Borgo - patrol walk above, hidden passage below (S1.7) |
| 5 | Panelled Carrel | G | (262, 96) | Library | Baddesley Clinton - small room with a door hidden in the panelling (S1.7) |
| 6 | Roof Hide (T1 attic) | U | (44, 44) | T1 dorm | Baddesley Clinton - hide in the roof (S1.7) |
| 7 | Founder's Scrittoio | G | (244, 282) | Rector's Lodge | Palazzo Vecchio - Scrittoio reached only through passages behind paintings (S1.4) |
| 8 | Studiolo | G | (246, 120) | Laboratories | Palazzo Vecchio - Studiolo, part-office part-laboratory part-hiding place (S1.4) |
| 9 | Secret Drawers + Rector's Key | G | (228, 258) | Rector's Lodge | Versailles - King's private suite with numerous secret drawers (S1.1) |
| 10 | Closed Stack (lectern lock) | G | (300, 64) | Library | Palazzo Vecchio - Tesoretto, hidden compartments + two hidden doorways (S1.4) |
| 11 | Double Hide | U | (302, 96) | Dbl hide | Nicholas Owen - outer hide concealing an inner hide (S1.7) |
| 12 | Hall Roof Trusses | U | (185, 192) | GREAT HALL (open roof) | Palazzo Vecchio - truss space above the Salone dei Cinquecento (S1.4) |
| 13 | Map Room (dispatch room) | U | (194, 118) | Map Room | Versailles - Louis XV's dispatch room for spies (S1.1) |
| 14 | Rector's Vice Stair + Supper Closet | U | (250, 286) | Supper | Holyroodhouse - small vice stair + 12 ft supper closet (S1.3) |
| 15 | Oratory Window + Tribune Door | U | (270, 296) | Tribune | Tower of London - oratory in the bedchamber; Versailles tribune (S1.7, H15) |
| 16 | Bricked-up Arch | U | (220, 262) | Rector bed | Hampton Court - bricked-up doorway to Wolsey's gallery (S1.2) |
| 17 | Flying High Table | G | (210, 192) | GREAT HALL | Petit Trianon - flying table / trapdoor in the parquet (S1.1) |
| 18 | Wardrobe Door (Proctors -> Council) | U | (120, 191) | Proctors | Doge's Palace - Inquisitors' secret entrance behind a wooden wardrobe (S1.5) |
| 19 | Proctors' Way (itinerary) | U | (114, 176) | Proctors | Doge's Palace - Secret Itineraries, Pozzi -> chancellery -> Piombi (S1.5) |
| 20 | Bursary Strongroom (weighing toll) | G | (140, 206) | Entrance Range | Palazzo Vecchio - Tesoretto strongroom (S1.4) |
| 21 | Governess's Doors | U | (108, 320) | Governess | Versailles - the Queen's doors under the hangings; Governess's apartments (S1.1) |
| 22 | Children's Stair | U | (146, 316) | Day Room | Hampton Court - child lodged one floor below the parent (S1.2, H5) |
| 23 | Twin Stair | U | (236, 192) | court | Chambord - double-helix stair, two flights that never meet (S1.6) |
| 24 | Turning Bridges | U | (236, 186) | court | Chambord - four vaulted halls in a cross round the stair; loopholes (S1.6) |
| 25 | Clock-Keeper's Room | U | (250, 210) | Clock room | Versailles - Louis XV's private room in the Petits Cabinets at the top (S1.1) |
| 26 | Old Dry Well | G | (184, 140) | HALL GARTH | Moscow Kremlin - Tainitskaya secret well + hidden exit to the river (S1.7) |
| 27 | Garderobe Drop + Sewer Hide | U | (90, 68) | Dorm I upper | Baddesley Clinton - garderobe shaft into the sewers, 6-7 people (S1.7) |
| 28 | Covered Bridge: 2nd corridor + lower way | G | (264, 54) | Walk to T3 | Bridge of Sighs two corridors (S1.5); Passetto two levels (S1.7) |
| 29 | Alchemist's Vault | B | (236, 78) | Alchemist's Vault | Nesvizh - utility dungeons and secret passages (S1.7) |
| 30 | Infirmary Stove Passage | G | (236, 249) | Infirmary | Schonbrunn - stoking passage behind the walls (S1.7) |
| 31 | Matron's Door under the Hangings | G | (236, 240) | Infirmary | Versailles - doors under hangings beside the bed to the private rooms (S1.1) |
| 32 | Ice-House Hole | G | (294, 154) | LIBRARY COURT, Ice House | Hampton Court ice house (S1.2); Nesvizh icehouse hole taken for a passage (S1.7) |
| 33 | Water Stair | G | (248, 200) | Central Tower | Tower of London - St Thomas's Tower stair down to the river (S1.7) |
| 34 | Water Gate | B | (376, 191) | WATER GATE canal | Tower of London - water gate / Traitors' Gate (S1.7) |
| 35 | Way from the Lake | G | (316, 141) | CLIFF | Moscow Kremlin - Tainitskaya hidden exit to the Moskva (S1.7) |
| 36 | Tunnel Junction (three ways) | B | (236, 192) | MUNIMENT ARCHIVE | Dover Castle - three passages meeting in a junction (S1.7) |
| 37 | Founders' Crypt | B | (282, 308) | FOUNDERS' CRYPT | Habsburg Herzgruft / chapel crypt passage U2 (S4.6) |
| 38 | Catacombs | B | (284, 258) | CATACOMBS | Nesvizh - dungeons (S1.7); catacomb extent is design |
| 39 | Countermine | B | (12, 180) | Guard cellar | Dover Castle - tunnels built after the 1216 siege (S1.7) |

Notes: 38 Catacombs — the dungeons are documented (Nesvizh) but the catacomb extent is **design**. 22 Children's Stair — the stacking (child below parent) is documented; the stair link itself is **design** (research H5). Every secret stays "design, awaiting witness" until built and seen in game.

## 7. Massing (MASS)
| Box | Rect | Height | Roof |
|---|---|---|---|
| - (wall) | (0,0,2,383) | 9 | flat |
| - (wall) | (0,0,319,2) | 9 | flat |
| - (wall) | (0,381,319,383) | 9 | flat |
| Gatehouse (gate) | (3,176,22,207) | 22 | flat |
| Stables (service) | (24,20,39,95) | 8 | gable_z |
| House T-I (tower) | (40,40,79,79) | 34 | spire |
| - (tower) | (80,40,99,79) | 16 | gable_z |
| House T-II (tower) | (40,304,79,343) | 34 | spire |
| - (tower) | (80,304,99,343) | 16 | gable_z |
| House T-III (tower) | (272,20,303,51) | 34 | spire |
| House T-IV (tower) | (272,332,303,363) | 34 | spire |
| Entrance Range (hall) | (110,172,149,211) | 16 | gable_x |
| Great Hall (hall) | (150,156,219,227) | 24 | gable_x |
| Central Tower (tower) | (220,172,251,211) | 60 | spire |
| Kitchens (hall) | (150,228,179,251) | 12 | gable_x |
| Schools Wing (learn) | (150,96,219,125) | 14 | gable_x |
| Labs (lab) | (220,96,251,125) | 13 | gable_z |
| - (lab) | (220,60,251,95) | 14 | gable_z |
| Observatory (lab) | (228,64,243,79) | 30 | cone |
| Library (learn) | (256,60,305,99) | 18 | gable_x |
| Infirmary (sacred) | (220,228,251,251) | 12 | gable_z |
| Masters (lodge) | (150,252,219,287) | 15 | gable_x |
| Rector (lodge) | (220,252,251,287) | 17 | gable_z |
| - (lodge) | (248,284,251,287) | 22 | cone |
| Chapel (sacred) | (260,292,303,325) | 20 | gable_x |
| Junior School (child) | (100,300,149,340) | 13 | gable_x |
| - (service) | (290,150,298,158) | 4 | cone |
| Cloister (passage) | (96,80,99,291) | 5 | flat |
| - (passage) | (100,96,255,99) | 5 | flat |
| - (passage) | (100,288,255,291) | 5 | flat |
| - (passage) | (252,96,255,291) | 5 | flat |
| - (passage) | (96,186,109,197) | 5 | flat |
| Covered Bridge (passage) | (256,52,271,55) | 9 | gable_z |
| - (passage) | (256,328,271,331) | 5 | flat |
| - (passage) | (80,80,95,83) | 5 | flat |
| - (passage) | (80,300,95,303) | 5 | flat |

## 8. Images (all viewed)
- `ACADEMY-II-PLAN-GROUND.png` — top-down; gate side (x 0) at the top, z 0 at the left, cliff and lake at the bottom.
- `ACADEMY-II-PLAN-UPPER.png` — same view.
- `ACADEMY-II-PLAN-BASEMENT.png` — same view; quay and water-gate canal below the cliff.
- `ACADEMY-II-MASSING.png` — 3/4 view; viewer at the gate side, looking toward the lake.

## 9. Open items
- Central Tower position (at the crossing vs behind the hall) — Abs0lum's ruling.
- Massing label "Quay (feet -12)" leader lands near the Central Tower (cosmetic).
- Labels too small to print: Supper closet (4 x 4), upper Covered bridge (markers show them).
