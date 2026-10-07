# CIVITAS — STRUCTURE BUILD PLAN (2026-10-02)
**Status: APPROVED by his 13:31 answers. Phase A + B done, pilot delivered (gofile L8QSjf5Z), awaiting his look.**
Request (his 13:12): Claude builds EVERY structure — minimum village (MVV), MVV during renovation, village v2, town v1, town v1 during upgrade, town v2, city v1 — furnished, with stations, zones and datum, and he confirms each with an in-game scriptevent test. After he confirms the buildings, the villager scripts come next.

## His rulings (13:12 / 13:31)
- **+1 rule:** footprint +1 on x and z (cottage S 5x7 -> 6x8). Heights: his own (already adjusted, as in his r0).
- **Ladder hatch** (`pw:hatch_lid` entity on the top ladder) replaces the trapdoor.
- **Canonical palette** accepted (oak/spruce frame, stone footing, plank walls, roof); other looks = palette swaps or new builds later.
- **Roster:** cottages + bakery, butcher, smithy, inn, town hall, wheat farm, cattle farm, lumberyard, quarry, well — plus their upgraded versions per community tier. **Every building slightly different from the last, in layout AND in how fancy it looks** — individuality per villager.
- **Markers:** his preference = inside the structure; Claude's call -> inside the file (proven in BDS).
- **Furnish + zones + stations:** Claude does it.

## Standing rules this plan follows
- **Save-box law:** exact prism + one clearance column; vertical = fixed subsurface depth + building height; door = front, faces the street; datum = vertical zero. CHECK ITEM: his r0 keeps the clearance column on the LEFT seen from the street; the written law says RIGHT — asked.
- **Section -14 (as built in r0):** basement -5..-2, floor course -6 with `pw:manhole_cover`, shaft ladder -12..-7, `port_sewer` at -10, foundation -13/-12 smooth stone, box bottom -15.
- **Option B:** no frame posts in saved buildings.
- **Naming:** `pw:<tier>_<type>_<variant>_r<rung>`.
- **Endpoints authored, everything between derived** (construction S1-S5, renovation stages).

## Tooling built (Phase B)
- `tools/mcstructure.py` — typed NBT read/write; byte-identical on 14/14 existing files.
- `tools/civgen.py` — building generator (`Building` + `cottage()`), markers as engine-format entities.
- `tools/civ_src/civ_verify.js` + `pw_civ.js` — `/scriptevent pw:civ list | verify <name> | place <name> [0|90|180|270]` (TestRunner BP 0.5.12); the same checks run in the workspace Bedrock Dedicated Server before delivery (`tools/bds_civtest.py`, `tools/civ_pack.py`).
- `tools/civ_preview.py` — review sheet (3D, cut, section, plans with markers).
- Engine facts proven in BDS: rotation turns vanilla + trait states, not custom states or entity properties (placer turns hatch hinges); markers inside the file survive all 4 rotations and duplicate placements; a ladder needs a solid block behind it.

## Phases
A Inputs — DONE (world PROVING_GROUNDS: only `pw:mvv_cottage_s_a_r0`; 5 road pieces).
B Tooling — DONE.
C Pilot — DELIVERED: `pw:mvv_cottage_s_a_r1` in BP-02 1.3.205 (gofile L8QSjf5Z). Gate: his look + test.
D MVV set (each building unique) -> renovation states (derived).
E Village v2 · F Town v1 / upgrading / v2 · G City v1 — each tier confirmed before the next.

## Trees (his 13:31, parallel workstream)
16 unique structures per square-log species with fancy branches; 16 variants per dodecagon species, canopy only (spruce low, out-and-down tiers). Research done: `_docs/trees/TREE-ARCHITECTURE-RESEARCH-2026-10-02.md` (workspace). Open: T1 which species are square-log, T2 16 total vs per age, T3 order.
