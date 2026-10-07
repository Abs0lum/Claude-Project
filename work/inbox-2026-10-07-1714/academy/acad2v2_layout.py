"""Academy II layout — one source of truth for the plan PNGs, the massing sketch and the overlap/area checks.

Frame (castlegen / civgen): x = depth from the gate side (x 0 = gate, faces the town), z = frontage, both 0..383
(6 x 6 pieces of 64). Rectangles are (x0, z0, x1, z1) inclusive, in blocks (1 block = 1 m).
Levels: G = ground (feet 0; the lake row r5 stands at the quay, feet -12), U = upper (feet 6 typical; towers show a
dormitory floor), B = basement (B1 rooms at feet -7, B2 tunnels at feet -12, sewer trench -13).
"""

SIZE = 384
PIECE = 64

# category -> (fill, outline)
CAT = {
    "wall":     ((120, 110, 100), (60, 55, 50)),
    "cliff":    ((150, 140, 120), (90, 80, 70)),
    "court":    ((236, 232, 214), (190, 184, 160)),
    "garden":   ((205, 228, 190), (140, 170, 120)),
    "tower":    ((196, 170, 140), (110, 85, 60)),
    "hall":     ((232, 196, 140), (140, 100, 50)),
    "learn":    ((190, 210, 236), (80, 110, 160)),
    "lab":      ((214, 196, 230), (120, 90, 150)),
    "lodge":    ((242, 214, 200), (160, 110, 90)),
    "child":    ((250, 226, 150), (170, 140, 40)),
    "service":  ((214, 214, 214), (120, 120, 120)),
    "sacred":   ((226, 200, 226), (140, 90, 140)),
    "gate":     ((200, 180, 160), (100, 80, 60)),
    "water":    ((150, 196, 236), (60, 120, 190)),
    "passage":  ((250, 250, 250), (150, 150, 150)),
    "tunnel":   ((200, 200, 190), (100, 100, 90)),
    "sewer":    ((170, 190, 150), (90, 110, 70)),
    "catacomb": ((180, 170, 160), (90, 80, 70)),
    "secret":   ((255, 214, 240), (200, 0, 140)),
}
CAT_NAMES = {
    "tower": "towers (house towers, central, lake, clock)", "hall": "great hall, kitchens, refectory service",
    "learn": "library, schools, classrooms", "lab": "laboratories, observatory, workshops",
    "lodge": "lodgings (masters, Rector, guests)", "child": "junior school (children's lodging)",
    "service": "service (stables, stores, bothy)", "sacred": "chapel, crypt, infirmary",
    "gate": "gatehouses", "court": "courts, terraces, quay", "garden": "gardens", "water": "water (canal, basin, lake)",
    "wall": "curtain / precinct walls", "cliff": "cliff edge (feet 0 -> -12)", "tunnel": "tunnels (B2, feet -12)",
    "sewer": "sewers (trench feet -13)", "catacomb": "catacombs", "passage": "passages",
    "secret": "secret room / hide",
}

# ------------------------------------------------------------------ GROUND
G = [
    # v2 (D-C1006-ACAD2): ONE central building (great hall + central tower) with connected wings + auxiliary
    # buildings, courts between them, covered cloister walks ("passage") joining everything. Precinct wall only.
    ("wall", (0, 0, 2, 383), ""), ("wall", (0, 0, 319, 2), ""), ("wall", (0, 381, 319, 383), ""),
    ("cliff", (312, 3, 319, 380), "CLIFF"),
    # courts (containers)
    ("court", (23, 100, 95, 283), "FORECOURT"),
    ("court", (100, 100, 149, 155), "SCHOLARS' COURT"),
    ("court", (100, 228, 149, 287), "MASTERS' COURT"),
    ("court", (150, 128, 219, 153), "HALL GARTH"),
    ("court", (256, 100, 305, 170), "LIBRARY COURT"),
    ("court", (256, 214, 305, 290), "CHAPEL COURT"),
    # central building
    ("gate", (3, 176, 22, 207), "Gatehouse"),
    ("hall", (110, 172, 149, 211), "Entrance Range"),
    ("hall", (150, 156, 219, 227), "GREAT HALL"),
    ("tower", (220, 172, 251, 211), "Central Tower"),
    ("hall", (150, 228, 179, 251), "Kitchens"),
    # wings + auxiliary buildings
    ("learn", (150, 96, 219, 125), "Schools Wing"),
    ("lab", (220, 96, 251, 125), "Laboratories"),
    ("lab", (220, 60, 251, 95), "Observatory Wing"),
    ("learn", (256, 60, 305, 99), "Library"),
    ("sacred", (220, 228, 251, 251), "Infirmary"),
    ("lodge", (150, 252, 219, 287), "Masters' Lodgings"),
    ("lodge", (220, 252, 251, 287), "Rector's Lodge"),
    ("sacred", (260, 292, 303, 325), "Chapel"),
    ("child", (100, 300, 149, 340), "Junior School"),
    ("service", (24, 20, 39, 95), "Stables + Stores"),
    ("tower", (40, 40, 79, 79), "House Tower I"), ("tower", (80, 40, 99, 79), "Dorm Range I"),
    ("tower", (40, 304, 79, 343), "House Tower II"), ("tower", (80, 304, 99, 343), "Dorm Range II"),
    ("tower", (272, 20, 303, 51), "House Tower III"),
    ("tower", (272, 332, 303, 363), "House Tower IV"),
    # covered walks / cloisters (passage; exempt from overlap check)
    ("service", (290, 150, 298, 158), "Ice House"),
    ("passage", (96, 186, 109, 197), "Porch Walk"),
    ("passage", (96, 80, 99, 291), "Gate Cloister"),
    ("passage", (100, 96, 255, 99), "Left Cloister (z0 side)"),
    ("passage", (100, 288, 255, 291), "Right Cloister (z383 side)"),
    ("passage", (252, 96, 255, 291), "Lake Cloister"),
    ("passage", (150, 126, 219, 127), ""), ("passage", (150, 154, 219, 155), ""),
    ("passage", (256, 52, 271, 55), "Walk to T3"), ("passage", (256, 328, 271, 331), "Walk to T4"),
    ("passage", (80, 80, 95, 83), "Walk to T1"), ("passage", (80, 300, 95, 303), "Walk to T2"),
]

# ------------------------------------------------------------------ UPPER (feet 6; towers at a dormitory floor) — v2
U = [
    ("wall", (0, 0, 2, 383), ""), ("wall", (0, 0, 319, 2), ""), ("wall", (0, 381, 319, 383), ""),
    ("cliff", (312, 3, 319, 380), "CLIFF"),
    ("gate", (3, 176, 22, 191), "Printing House"), ("gate", (3, 192, 22, 207), "Steward"),
    ("service", (24, 20, 39, 95), "Grooms' loft"),
    ("tower", (40, 40, 79, 79), "T1 dorm"), ("tower", (80, 40, 99, 79), "Dorm I upper"),
    ("tower", (40, 304, 79, 343), "T2 dorm"), ("tower", (80, 304, 99, 343), "Dorm II upper"),
    ("tower", (272, 20, 303, 51), "T3 dorm"), ("tower", (272, 332, 303, 363), "T4 dorm"),
    # Entrance Range upper: Proctors | Council (wardrobe door between) | Exam Hall
    ("gate", (110, 172, 129, 191), "Proctors"), ("gate", (110, 192, 129, 211), "Council"),
    ("learn", (130, 172, 149, 211), "Exam Hall"),
    ("hall", (150, 156, 219, 227), "GREAT HALL (open roof)"),
    # Schools Wing upper
    ("learn", (150, 96, 219, 111), "LONG GALLERY"), ("learn", (150, 112, 189, 125), "Drawing Studio"),
    ("secret", (190, 112, 197, 125), "Map Room"), ("learn", (198, 112, 219, 125), "Music (organ loft)"),
    ("lab", (220, 96, 251, 125), "Optics + Mechanics"), ("lab", (220, 60, 251, 95), "Astronomer"),
    # Central Tower floor: four rooms around the twin-stair void, cross of halls (Chambord)
    ("tower", (220, 172, 231, 187), "SCR"), ("tower", (240, 172, 251, 187), "Exhib."),
    ("tower", (220, 196, 231, 211), "Instr."), ("tower", (240, 196, 251, 211), "Clock room"),
    ("court", (232, 184, 239, 199), ""),
    ("passage", (232, 172, 239, 183), ""), ("passage", (232, 200, 239, 211), ""),
    ("passage", (220, 188, 231, 195), ""), ("passage", (240, 188, 251, 195), ""),
    ("hall", (150, 228, 179, 251), "Cooks' loft"), ("sacred", (220, 228, 251, 251), "Infirmary nurses"),
    ("lodge", (150, 252, 219, 287), "Masters' sets (upper)"),
    # Rector's Lodge upper
    ("lodge", (220, 252, 235, 271), "Rector bed"), ("lodge", (236, 252, 251, 271), "Study"),
    ("lodge", (220, 272, 235, 287), "Dressing"), ("sacred", (236, 272, 247, 287), "Oratory"),
    ("lodge", (248, 272, 251, 283), "Vice"), ("secret", (248, 284, 251, 287), "Supper"),
    ("sacred", (260, 292, 303, 299), "Tribune"), ("sacred", (260, 300, 303, 325), "CHAPEL (void)"),
    ("learn", (256, 60, 305, 91), "LIBRARY upper gallery"), ("learn", (256, 92, 297, 99), "Reading closets"),
    ("secret", (298, 92, 305, 99), "Dbl hide"),
    # Junior School upper = children's lodging (Hampton Court Prince's Lodgings pattern)
    ("child", (100, 300, 115, 319), "Night A"), ("child", (116, 300, 131, 319), "Night B"),
    ("child", (132, 300, 149, 319), "Day Room"), ("child", (100, 320, 115, 340), "Governess"),
    ("child", (116, 320, 131, 340), "Nurses"), ("child", (132, 320, 149, 340), "Wash"),
    ("passage", (252, 52, 271, 55), "Covered bridge (upper)"),
]

# ------------------------------------------------------------------ BASEMENT (B1 rooms -7, B2 tunnels -12, sewer -13) — v2
B = [
    ("cliff", (312, 3, 319, 380), "CLIFF"),
    ("gate", (3, 176, 22, 207), "Guard cellar"),
    ("tower", (40, 40, 79, 79), "T1 cellar"), ("tower", (40, 304, 79, 343), "T2 cellar"),
    ("tower", (272, 20, 303, 51), "T3 cellar"), ("tower", (272, 332, 303, 363), "T4 cellar"),
    ("service", (80, 40, 95, 59), "Dorm I cellar"), ("secret", (84, 62, 95, 72), "Sewer hide"),
    ("gate", (110, 172, 129, 191), "Lock-up (Pozzi)"), ("gate", (110, 192, 129, 211), "Bursary vault"),
    ("hall", (130, 172, 149, 211), "Porters' cellar"),
    ("hall", (150, 156, 189, 227), "UNDERCROFT"), ("service", (190, 156, 219, 191), "WINE CELLAR"),
    ("hall", (190, 192, 219, 227), "Serving (under dais)"),
    ("service", (150, 228, 179, 251), "Wet larder"),
    ("learn", (150, 96, 219, 125), "Schools stores"),
    ("lab", (220, 96, 251, 125), "Lab cellar"), ("lab", (220, 60, 251, 95), "Alchemist's Vault"),
    ("learn", (220, 172, 251, 211), "MUNIMENT ARCHIVE"),
    ("sacred", (220, 228, 251, 251), "Mortuary"),
    ("lodge", (150, 252, 219, 287), "Masters' cellars"), ("lodge", (220, 252, 251, 287), "Rector's cellar"),
    ("learn", (256, 60, 305, 99), "Book cellar"),
    ("sacred", (260, 292, 303, 325), "FOUNDERS' CRYPT"),
    ("catacomb", (264, 222, 303, 285), "CATACOMBS"),
    ("child", (100, 300, 149, 340), "Junior service floor"),
    ("service", (292, 152, 296, 156), "Ice"),
    # B2 tunnels (feet -12)
    ("tunnel", (23, 191, 235, 192), ""),                                   # gatehouse -> junction
    ("tunnel", (236, 192, 295, 193), ""),                                  # junction -> basin
    ("tunnel", (236, 193, 237, 291), ""), ("tunnel", (236, 290, 282, 291), ""), ("tunnel", (281, 290, 282, 299), ""),  # -> crypt
    ("tunnel", (184, 140, 319, 141), ""),                                  # dry well -> lake quay
    ("tunnel", (293, 142, 294, 154), ""),                                  # ice well -> well tunnel
    ("water", (296, 184, 311, 199), "Basin"),
    ("water", (312, 188, 383, 195), "WATER GATE canal"),
    # sewers (trench -13): gate-side and lake-side mains, cross main to the outfall
    ("sewer", (97, 40, 98, 331), ""), ("sewer", (253, 40, 254, 331), ""), ("sewer", (97, 330, 319, 331), ""),
    ("water", (320, 324, 335, 337), "Outfall"),
    ("court", (320, 16, 343, 187), "QUAY (-12)"), ("court", (320, 196, 343, 367), ""),
]

# containers that may legally overlap their contents
CONTAINERS = {"court", "wall", "cliff", "garden"}

# ------------------------------------------------------------------ secrets: id -> (name, level, (x, z) marker, route)
# v2: every secret sits in a v2 room; the palace source for each is in SECRET_SOURCES (PALACE-II-RESEARCH-2026-10-06).
SECRETS = {
    1: ("Masters' Spine (jib doors)", "G", (184, 270), [(152, 270), (218, 270)]),
    2: ("Stoking Passage", "G", (200, 124), [(152, 124), (218, 124), (236, 124)]),
    3: ("Porter's Stair in the Wall", "G", (12, 206), [(5, 206), (20, 206)]),
    4: ("Mural Passage", "U", (1, 120), [(311, 1), (1, 1), (1, 382), (311, 382)]),
    5: ("Panelled Carrel", "G", (262, 96), []),
    6: ("Roof Hide (T1 attic)", "U", (44, 44), []),
    7: ("Founder's Scrittoio", "G", (244, 282), [(236, 282), (244, 282)]),
    8: ("Studiolo", "G", (246, 120), [(236, 120), (246, 120)]),
    9: ("Secret Drawers + Rector's Key", "G", (228, 258), []),
    10: ("Closed Stack (lectern lock)", "G", (300, 64), [(290, 72), (300, 64)]),
    11: ("Double Hide", "U", (302, 96), []),
    12: ("Hall Roof Trusses", "U", (185, 192), [(152, 192), (218, 192)]),
    13: ("Map Room (dispatch room)", "U", (194, 118), [(194, 110), (194, 113)]),
    14: ("Rector's Vice Stair + Supper Closet", "U", (250, 286), [(244, 262), (250, 276), (250, 286)]),
    15: ("Oratory Window + Tribune Door", "U", (270, 296), [(242, 280), (256, 292), (270, 296)]),
    16: ("Bricked-up Arch", "U", (220, 262), []),
    17: ("Flying High Table", "G", (210, 192), []),
    18: ("Wardrobe Door (Proctors -> Council)", "U", (120, 191), []),
    19: ("Proctors' Way (itinerary)", "U", (114, 176), [(114, 176), (126, 176), (126, 190)]),
    20: ("Bursary Strongroom (weighing toll)", "G", (140, 206), []),
    21: ("Governess's Doors", "U", (108, 320), [(108, 326), (108, 316), (120, 320)]),
    22: ("Children's Stair", "U", (146, 316), [(146, 338), (146, 316)]),
    23: ("Twin Stair", "U", (236, 192), []),
    24: ("Turning Bridges", "U", (236, 186), [(233, 186), (238, 197)]),
    25: ("Clock-Keeper's Room", "U", (250, 210), []),
    26: ("Old Dry Well", "G", (184, 140), []),
    27: ("Garderobe Drop + Sewer Hide", "U", (90, 68), []),
    28: ("Covered Bridge: 2nd corridor + lower way", "G", (264, 54), [(252, 54), (272, 54)]),
    29: ("Alchemist's Vault", "B", (236, 78), []),
    30: ("Infirmary Stove Passage", "G", (236, 249), [(222, 249), (250, 249)]),
    31: ("Matron's Door under the Hangings", "G", (236, 240), []),
    32: ("Ice-House Hole", "G", (294, 154), []),
    33: ("Water Stair", "G", (248, 200), []),
    34: ("Water Gate", "B", (376, 191), [(383, 191), (312, 191), (304, 191)]),
    35: ("Way from the Lake", "G", (316, 141), [(305, 141), (319, 141)]),
    36: ("Tunnel Junction (three ways)", "B", (236, 192), []),
    37: ("Founders' Crypt", "B", (282, 308), [(282, 299), (282, 308)]),
    38: ("Catacombs", "B", (284, 258), []),
    39: ("Countermine", "B", (12, 180), [(12, 180), (12, 178), (16, 166), (10, 156), (16, 146), (11, 138)]),
}

# palace feature each secret is modelled on (section of PALACE-II-RESEARCH-2026-10-06.md)
SECRET_SOURCES = {
    1: "Versailles - service rooms behind the Queen's apartment / hidden spine H1 (S1.1, S4.5)",
    2: "Schonbrunn - stoves stoked from a passage behind the walls (S1.7)",
    3: "Palazzo Vecchio - Brienne stair carved into the thickness of the wall (S1.4)",
    4: "Passetto di Borgo - patrol walk above, hidden passage below (S1.7)",
    5: "Baddesley Clinton - small room with a door hidden in the panelling (S1.7)",
    6: "Baddesley Clinton - hide in the roof (S1.7)",
    7: "Palazzo Vecchio - Scrittoio reached only through passages behind paintings (S1.4)",
    8: "Palazzo Vecchio - Studiolo, part-office part-laboratory part-hiding place (S1.4)",
    9: "Versailles - King's private suite with numerous secret drawers (S1.1)",
    10: "Palazzo Vecchio - Tesoretto, hidden compartments + two hidden doorways (S1.4)",
    11: "Nicholas Owen - outer hide concealing an inner hide (S1.7)",
    12: "Palazzo Vecchio - truss space above the Salone dei Cinquecento (S1.4)",
    13: "Versailles - Louis XV's dispatch room for spies (S1.1)",
    14: "Holyroodhouse - small vice stair + 12 ft supper closet (S1.3)",
    15: "Tower of London - oratory in the bedchamber; Versailles tribune (S1.7, H15)",
    16: "Hampton Court - bricked-up doorway to Wolsey's gallery (S1.2)",
    17: "Petit Trianon - flying table / trapdoor in the parquet (S1.1)",
    18: "Doge's Palace - Inquisitors' secret entrance behind a wooden wardrobe (S1.5)",
    19: "Doge's Palace - Secret Itineraries, Pozzi -> chancellery -> Piombi (S1.5)",
    20: "Palazzo Vecchio - Tesoretto strongroom (S1.4)",
    21: "Versailles - the Queen's doors under the hangings; Governess's apartments (S1.1)",
    22: "Hampton Court - child lodged one floor below the parent (S1.2, H5)",
    23: "Chambord - double-helix stair, two flights that never meet (S1.6)",
    24: "Chambord - four vaulted halls in a cross round the stair; loopholes (S1.6)",
    25: "Versailles - Louis XV's private room in the Petits Cabinets at the top (S1.1)",
    26: "Moscow Kremlin - Tainitskaya secret well + hidden exit to the river (S1.7)",
    27: "Baddesley Clinton - garderobe shaft into the sewers, 6-7 people (S1.7)",
    28: "Bridge of Sighs two corridors (S1.5); Passetto two levels (S1.7)",
    29: "Nesvizh - utility dungeons and secret passages (S1.7)",
    30: "Schonbrunn - stoking passage behind the walls (S1.7)",
    31: "Versailles - doors under hangings beside the bed to the private rooms (S1.1)",
    32: "Hampton Court ice house (S1.2); Nesvizh icehouse hole taken for a passage (S1.7)",
    33: "Tower of London - St Thomas's Tower stair down to the river (S1.7)",
    34: "Tower of London - water gate / Traitors' Gate (S1.7)",
    35: "Moscow Kremlin - Tainitskaya hidden exit to the Moskva (S1.7)",
    36: "Dover Castle - three passages meeting in a junction (S1.7)",
    37: "Habsburg Herzgruft / chapel crypt passage U2 (S4.6)",
    38: "Nesvizh - dungeons (S1.7); catacomb extent is design",
    39: "Dover Castle - tunnels built after the 1216 siege (S1.7)",
}

# Basement-only routes (B2) for secrets that live on several levels; int keys get a marker at the last point
B_ROUTES = {
    26: [(184, 140), (300, 141), (320, 141)],    # dry well -> hidden exit on the lake quay
    27: [(97, 60), (97, 67), (90, 67)],          # sewer main -> sewer hide under the garderobe drop
    32: [(294, 154), (294, 141)],                # ice-house hole -> well tunnel
    33: [(248, 200), (248, 193), (296, 193)],    # water stair foot -> basin
    17: [(200, 205), (210, 192)],                # serving room -> lift under the dais
    3: [(20, 206), (23, 192)],                   # porter's stair foot -> gate tunnel
    20: [(140, 206), (128, 206), (120, 196)],    # bursary strongroom -> bursary vault / lock-up
}

# ------------------------------------------------------------------ massing boxes (x0, z0, x1, z1, height, roof, cat, label) — v2
# roof: flat | gable_x | gable_z | spire | cone (spire = pyramidal cap of +cap)
MASS = [
    (0, 0, 2, 383, 9, "flat", "wall", None), (0, 0, 319, 2, 9, "flat", "wall", None), (0, 381, 319, 383, 9, "flat", "wall", None),
    (3, 176, 22, 207, 22, "flat", "gate", "Gatehouse"),
    (24, 20, 39, 95, 8, "gable_z", "service", "Stables"),
    (40, 40, 79, 79, 34, "spire", "tower", "House T-I"), (80, 40, 99, 79, 16, "gable_z", "tower", None),
    (40, 304, 79, 343, 34, "spire", "tower", "House T-II"), (80, 304, 99, 343, 16, "gable_z", "tower", None),
    (272, 20, 303, 51, 34, "spire", "tower", "House T-III"), (272, 332, 303, 363, 34, "spire", "tower", "House T-IV"),
    (110, 172, 149, 211, 16, "gable_x", "hall", "Entrance Range"),
    (150, 156, 219, 227, 24, "gable_x", "hall", "Great Hall"),
    (220, 172, 251, 211, 60, "spire", "tower", "Central Tower"),
    (150, 228, 179, 251, 12, "gable_x", "hall", "Kitchens"),
    (150, 96, 219, 125, 14, "gable_x", "learn", "Schools Wing"),
    (220, 96, 251, 125, 13, "gable_z", "lab", "Labs"),
    (220, 60, 251, 95, 14, "gable_z", "lab", None), (228, 64, 243, 79, 30, "cone", "lab", "Observatory"),
    (256, 60, 305, 99, 18, "gable_x", "learn", "Library"),
    (220, 228, 251, 251, 12, "gable_z", "sacred", "Infirmary"),
    (150, 252, 219, 287, 15, "gable_x", "lodge", "Masters"),
    (220, 252, 251, 287, 17, "gable_z", "lodge", "Rector"), (248, 284, 251, 287, 22, "cone", "lodge", None),
    (260, 292, 303, 325, 20, "gable_x", "sacred", "Chapel"),
    (100, 300, 149, 340, 13, "gable_x", "child", "Junior School"),
    (290, 150, 298, 158, 4, "cone", "service", None),
    (96, 80, 99, 291, 5, "flat", "passage", "Cloister"), (100, 96, 255, 99, 5, "flat", "passage", None),
    (100, 288, 255, 291, 5, "flat", "passage", None), (252, 96, 255, 291, 5, "flat", "passage", None),
    (96, 186, 109, 197, 5, "flat", "passage", None),
    (256, 52, 271, 55, 9, "gable_z", "passage", "Covered Bridge"), (256, 328, 271, 331, 5, "flat", "passage", None),
    (80, 80, 95, 83, 5, "flat", "passage", None), (80, 300, 95, 303, 5, "flat", "passage", None),
]


def overlaps(level):
    """pairs of non-container rectangles on one level that overlap (illegal double-booking of a cell)"""
    bad = []
    rs = [(c, r, l) for (c, r, l) in level if c not in CONTAINERS and c not in ("passage", "tunnel", "sewer", "water")]
    for i in range(len(rs)):
        for j in range(i + 1, len(rs)):
            a, b = rs[i][1], rs[j][1]
            if a[0] <= b[2] and b[0] <= a[2] and a[1] <= b[3] and b[1] <= a[3]:
                bad.append((rs[i][2] or rs[i][0], a, rs[j][2] or rs[j][0], b))
    return bad
