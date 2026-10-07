# ACADEMY II — design programme (D-C1006-ACAD2, 2026-10-06, for review)

**Owner's brief (22:53 CT 10-06):** *"Using the real life palace as a teaching tool, upgrade castle academy to also have Castle academy 2. Larger and more robust — make it more parts if need be. Make it so it's fun to explore; secret rooms — again, with Hogwarts as a platform; but upgraded."*

**Status:** DESIGN ONLY. Nothing is built, placed or changed. No pack, `_build`, `_bds` or `tools` file is touched; no server started.
**Inputs read:** `_docs/palace/PALACE-II-RESEARCH-2026-10-06.md` (359 lines; "# PALACE II — Research Brief: Real Palace Blueprints, Hidden Circulation, Underground Ways, Nurseries"); `_docs/castle/CASTLE-DESIGN-COMPLETE-2026-10-06.md` (557 lines; "# CASTLE DESIGN — COMPLETE INVENTORY (D-C572 continued, 2026-10-06, for review)"); the `tools/castlegen.py` docstring; `_docs/CASTLE-PROGRAM-DESIGN-2026-10-05.md` §3 (the academy-castle); `_logs/decision_journal.md` D-C572, D-C1006-PAL2, D-C1006-ACAD2 and the 228 spiral lessons; the `tools/spiral_site.py` docstring.
**Drawings (this folder):** `ACADEMY-II-PLAN-GROUND.png`, `ACADEMY-II-PLAN-UPPER.png`, `ACADEMY-II-PLAN-BASEMENT.png`, `ACADEMY-II-MASSING.png`. They were drawn from one layout data file (scratchpad `acad2_layout.py`). An automated check found **0 overlapping rooms** on every level. Every drawing was viewed at full resolution and corrected for label and marker collisions.
**How to read it:** "**[SRC: key]**" points to a source in §11. Most keys come from the Palace II research doc; keys marked (castle doc) come from the castle inventory. "**ADAPTED**" means a documented feature has been moved to a new place or use. "**COMPOSITE**" means several documented features are joined in a way that no source shows. "**INVENTION**" means no source backs it. Engine claims marked "**verify**" have not been tested on BDS or PS5. Under P1, they stay "designed, unverified".

---

## 0. Standing law: what keeps this original

| Rule | How Academy II meets it |
|---|---|
| Borrow the GENRE, not the book | We use the genre's parts: a great hall, many towers, galleries, a library with a closed stack, odd and moving stairs, hidden rooms, a lake, grounds, a boathouse. We use no names, house names, crests, characters, sports or signature layouts. |
| House identity | There are four house towers. Each takes its name and colours from the **stone it is built in** (the seed's material draw, castle doc §8.1). Houses have no animals, no elements and no founders' names. |
| No signature layouts | No painting guards a dormitory entrance. Painting doors lead only to studies, cabinets and stacks, which is the Palazzo Vecchio pattern. No staircase moves as a whole flight; the moving parts are short turning bridges between galleries (§4.3, S24). There is no forest edge with forbidden-wood lore. |
| Titles | We use real collegiate offices only: Rector, masters, Bursar, Proctors, Porter, Librarian, Governess. |
| Every secret is grounded | Each of the 39 secrets names its documented real model (§10). Inventions are flagged. Myths are used knowingly and labelled as myths (S32). |
| "The real palace as a teaching tool" | Every secret rewards a **Founder's Note**, a written book that tells the true story behind it. Examples: "On 6 October 1789 a queen left her bedchamber by the door on the left of the bed…" for S21, and "The priests at Baddesley Clinton slid down a garderobe shaft into the sewers…" for S27. The player learns real palace history by finding things. |

---

## 1. Footprint and piece grid

**Proposal: 6 × 6 pieces = 384 × 384 blocks (36 pieces). Academy I's 4 × 4 core stays in place, and a one-piece ring is added around it.**

```
          c0 (z 0-63)        c1-c4 (z 64-319)                          c5 (z 320-383)
r0  x 0-63   [corner twr] [stables] [smithy] [GREAT GATEHOUSE + viaduct] [guest house] [corner twr]   OUTER COURT
r1..r4       LABORATORY   +----------------- ACADEMY I CORE (re-placed _t2) ------------+   GARDENS WARD
x 64-319     WARD beyond  | house T1 . inner gate . FIRST COURT . clock twr . house T2 |   physic garden,
             the DRY      | masters | GREAT HALL > CENTRAL TOWER > LIBRARY > LAKE TWR |   orangery, sunken
             DITCH, the   | schools quad . cloister . chapel . infirmary . junior sch.|   observatory, ice
             covered      | house T3 ........ lake walk ........ house greens .. T4   |   house, orchard
             bridge       +------------------------- CLIFF (feet 0 -> -12) ---------------+
r5  x 320-383  QUAY + LAKE TERRACE (feet -12) . boathouse . water-gate canal . outfall cascade . fisher / boat towers
               LAKE beyond x 384 (land job)
```

**Why 6 × 6 and not 5 × 5:**
1. **Growth without moving anything.** Academy I is 4 × 4 (castle doc §10.3). A ring one piece wide around it gives 6 × 6, and every Academy I piece keeps its origin. It is re-placed in place as its `_t2` version, which is the castle doc §9 rule: "same origin, same rotation". A 5 × 5 grid cannot centre a 4 × 4 core. It would need a lopsided ring on two sides only, or Academy I would have to be rebuilt somewhere else.
2. **The programme needs it, measured from the layout file.** Roofed ground floor in the core is 14,392 m². The new ring adds 15,452 m². That ring holds the laboratory ward, the gardens ward with the orangery and sunken observatory, the great gatehouse with its outer court, the stables and guest house, the quay and the boathouse. The upper floors add 23,224 m², the B1 rooms 12,552 m², and the B2 level has 2,042 tunnel and sewer cells plus 2,704 m² of catacombs. A 5 × 5 ring of 9 pieces would have to drop the laboratory ward or the gardens.
3. **The shaping job already plans for about 384.** Academy I's land shaping reaches about 384 (castle doc §8.2). Academy II turns that land into building. The lake and forest edge move out to about 448 (Q1).
4. **The pieces stay well inside engine limits.** The tallest piece is the central tower: 64 high plus a spire, about 88 above the court. With the basement at −15 the box is about −15..90, roughly 105 high, far below the 384 limit. Footprints stay at 64 × 64. 384 is a multiple of 64, but the castlegen `cut()` bug (F1, `n = W // 64`) must still be fixed first, because the same code path cuts this model.

**Engine and clock consequences:**
- 36 pieces × 5 height-band stages (castle doc §10: s0 ground plus feet < 0, s1 masonry to 4, s2 to the walk, s3 roofs and caps, s4 furnishing and markers) gives about 180 placement beats. Each stage stays at or under about 60k cells (LC-1005-2).
- The site survey cannot hold 384 plus the lake in one 10 × 10-chunk area (LC-1005-11). It walks about 3 × 3 windows before accepting a site.
- An academy city must **reserve the final 384 footprint plus the lake band at founding**. This is the castle-first hard requirement in castle doc §9.

**Vertical section (feet over the court; 0 = standing on the court).** This matches the Palace II section so the two share the sewer contract.

| Level | Walking feet | Clear | Use |
|---|---|---|---|
| B2 tunnels | −12 | 4 | tunnel junction, water-gate basin, catacombs, sally and lake tunnels. The quay and the dry-ditch floor are at this level. |
| sewer trench | floor −13 | — | city standard (D-C533 / 1006). Outfall cascade on the quay into the lake. |
| B1 cellars | −7 | 5–6, vaulted | wine cellar, serving room, archive, crypt, lock-up, alchemist's vault, tower laboratories |
| Ground | 0 | 5–6 (halls rise through) | everything on the ground plan |
| Upper | 6 | 5 | everything on the upper plan |
| Attic | 12–15 | 4 | the Leads, armoury, the Junior School schoolroom, roof hides |
| Towers | storeys of 5 | — | house towers 42 plus caps; central 64 plus spire; Lake Tower 48 plus cone; clock 56 |

**Lake level (design):** the surface is at about feet −13, the quay at −12 and the cliff 12 high. These numbers let the B2 tunnels open straight onto the quay and let the sewer outfall drop 1 into the lake. That drop is the waterfall the water law asks for (Q8).

---

## 2. Building list (block sizes are design choices unless a source is named)

### 2.1 The core (Academy I, re-placed `_t2`)

| Building | Rect (x0,z0 → x1,z1) | Size | Contents | Model |
|---|---|---|---|---|
| **Great Hall** | 128,184 → 175,199 | 48 × 16, 18 to the plate | screens and porch at the court end; buttery and pantry; dais and high table at the tower end; open timber roof; minstrels' gallery over the screens; **one diagonal skyway at collar height** (17:58 ruling); flying high table (S17) | grand hall 15–17 × 36–44 (castle doc §4.2); Hampton Court hall 32 × 12 × 14 **[SRC: R3]** |
| **Central Tower** | 184,176 → 215,207 | 32 × 32, 64 plus spire | **four vaulted arms in a cross** on every floor, meeting at an open galleried **stair hall** of 16 × 16; the **Twin Stair** (S23) and three **Turning Bridges** (S24) in the void; corner rooms: Senior Common Room, Exam Hall, Exhibition (gallery paintings), Instrument Cabinet; bell loft at the top | Chambord: "Four rectangular vaulted hallways on each floor form a cross-shape" around the stair **[SRC: CH-X]** |
| **Library** (long gallery) | 216,184 → 279,199 | 64 × 16 | two gallery tiers, reading lecterns; ceiling with a roof space of trusses above it (S12); **Closed Stack** 16 × 16 (S10, S11); Founder's **Scrittoio** 12 × 14 behind a painting (S7); **Studiolo** 8 × 8, windowless and barrel-vaulted (S8); Muniment Archive in the undercroft | Hall of Mirrors 73 × 10.5; Hampton Court gallery 36 × 7 **[SRC: R3 §3]**; Scrittoio and Studiolo **[SRC: PV-P, PV-ST]** |
| **Lake Tower** (observatory) | 288,180 → 311,203 | 24 round, 48 plus cone | the astronomer's lodging; observatory deck with shutters; **Water Stair** to the basin (S33) | Uraniborg instrument rooms (castle doc **[URAN]**); St Thomas's Tower spiral **[SRC: TOL]** |
| **House Towers T1–T4** | corners of the core, 15 × 15 | 42 plus caps | basement laboratory and stores; ground floor common hall with hearth; dormitory floors of **8 rooms around a B spiral** (32 beds in Academy I, 48 after AII-2's two extra floors); top floor tutor and small library; roof deck | Uraniborg loft "eight smaller rooms for students"; basement "alchemical laboratory" (castle doc **[URAN]**) |
| **Inner Gatehouse** (Academy I gate) | 64,180 → 79,203 | 16 × 24 | **ground:** passage, Porter's Lodge, Bursary and strongroom (S20); **upper:** Proctors' Chamber, Masters' Council Chamber, joined by the wardrobe door (S18); **attic:** armoury and the Leads; **B1:** lock-up; the porter's stair inside the 3-thick wall (S3) | Harlech gatehouse with lodging (castle doc **[CW-HARL]**); the Doge's itinerary rooms **[SRC: DP-I]** |
| **First Court** | 80,136 → 127,247 | 48 × 112 | arrival court; porch of the Great Hall | — |
| **Clock and Bell Tower** | 80,234 → 93,247 | 14 × 14, 56 | bell loft; clock room; Clock-Keeper's room at the top (S25) | Louis XV's private room "on the top of the palace" **[SRC: VK]** |
| **Masters' Lodgings** | 80,100 → 127,131 | 48 × 32, 3 floors | 6 sets per floor, each a study and a bedchamber; service spine with jib doors (S1); garderobe tower (S27) | Versailles courtier lodging, Narbonne pattern (R3 §4) |
| **Rector's Lodging** | 160,200 → 183,223 | 24 × 24 | **ground:** hall and dining room; **upper:** bedchamber with an alcove and the bricked-up arch (S16), study, dressing room, **oratory with a window into the chapel** (S15), **supper closet** in a 4 × 4 turret (S14); vice stair to the hall dais (S14) | Holyrood, Hampton Court, El Escorial **[SRC: HOL, HC, ESC]** |
| **Kitchen Tower**, buttery, bakehouse | 128,200 → 155,223 | tower 16 × 16 | two hearths, ovens, louvre; cooks' loft; service tunnel to the serving room under the dais (B1) | Raby kitchen tower; Bodiam's two hearths (castle doc **[CST-RABY][NT-BOD]**) |
| **Chapel** | 156,226 → 187,237 | 32 × 12, 16 high | nave; **tribune** reached from the Rector's lodging (S15); Founders' Crypt beneath (S37) | Krak chapel 21.5 × 8.5 (castle doc **[W-KRAK]**); Versailles tribune **[SRC: research H15]** |
| **Infirmary and Apothecary** | 152,244 → 191,279 | 40 × 20 + 20 × 14 | sick ward of 12 beds; nurses' dormitory above; apothecary with stills | design |
| **Schools Quad** | 184,104 → 255,167 | 72 × 64 around a 40 × 32 court | **Grammar, Rhetoric** (S5), **Logic and Disputation, Arithmetic, Geometry and Maps, Music** (organ loft above), **Languages, Drawing Studio** (above), **Astronomy lecture** (above), **Law**; the **Long Gallery** of 64 × 8 and the **Map Room** (S13) on the upper floor; the **Old Dry Well** in the court (S26) | the medieval arts subjects (general fact, not from the research); Hampton Court Great Gallery **[SRC: R3]** |
| **Cloister** | 200,224 → 263,287 | 64 × 64 | arcaded walks; a **fountain** in the garth whose jet drains by a drop shaft to the sewer (water law); the catacombs lie beneath (B2) | — |
| **Junior School** (children's lodging) | 80,252 → 127,283 | 48 × 32 | **ground:** a watching chamber (the porter-nurse), refectory for juniors, kitchen and laundry. **Upper:** two **night nurseries**, a **day room**, the **Governess's bedchamber** with two hangings (S21), the **nurses' lodging** "within earshot", and a **washing chamber and jakes**. **Attic:** schoolroom, reached by the **Children's Stair** (S22). | Prince Edward's Lodgings 1537 **[SRC: HCN]**; night/day nursery pattern **[SRC: Nursery (room)]** |
| Fellows' Garden, Lake Walk, House Greens | open | — | the house towers' playing greens; the Lake Walk along the cliff top; the head of the **Way from the Lake** (S35) | — |

### 2.2 The ring (Academy II)

| Building | Rect | Size | Contents | Model |
|---|---|---|---|---|
| **Great Gatehouse** and viaduct landing | 4,176 → 27,207 | 24 × 32, 22 | passage with 2 portcullises; guard rooms; **upper:** **Printing House** and the Steward's room; **B1:** guard cellar with the **Countermine** entry (S39) | Uraniborg's gatehouses "held the printing workshop" (castle doc **[URAN]**); St Andrews countermine (castle doc **[UND-STA]**) |
| **Outer Court** | 28,24 → 63,359 | 36 × 336 | arrival and muster; dovecote; laundry | Bodiam dovecote (castle doc) |
| Stables and Smithy; Guest House | x 4–19 | — | grooms' loft; guest house for visiting scholars | castle doc §7.3 |
| **Laboratory Ward**, beyond the **Dry Ditch** | z 0–63 | ditch 12 wide, floor −12 | **Alchemy House** with the Alchemist's Vault beneath (S29); **Natural Philosophy Hall** (mechanics, optics); **Instrument Workshop**; **Assay House and Forge**; Lab Masters' House | Conwy: a "ditch cut into the rock" between wards (castle doc **[W-CONWY]**); Uraniborg alchemical laboratory **[URAN]** |
| **Covered Bridge** over the ditch | 212,40 → 219,67 | 8 wide; span 12 | **two parallel corridors**, the second behind a jib door; a **hidden enclosed passage under the deck** (S28) | Bridge of Sighs: span 11 m, "two separate corridors" **[SRC: BoS]**; Passetto, "two levels" **[SRC: PAS]** |
| **Gardens Ward** | z 320–383 | — | **Physic Garden** and beds; the **Orangery / Greenhouse** (64 × 14, glass) with its **Stove Passage** (S30); the **Sunken Observatory** (S31); the **Ice House** (S32); orchard; gardeners' bothy | Schönbrunn stoking passage **[SRC: SCH]**; Stjerneborg (castle doc **[URAN]**); Hampton Court ice house **[SRC: HCI]** |
| **Quay and Lake Terrace** (feet −12) | x 320–343 | 24 deep | the landing; the **Way from the Lake** stair (S35); the **sewer outfall cascade** | Whitehall river terrace and river gate steps **[SRC: WH]**; Harlech Way from the Sea (castle doc **[CW-HARL]**) |
| **Boathouse** and **Water-Gate Canal** | 348,168 → 379,215; canal z 188–195 | 32 × 48 | boats; the canal runs from the lake through the boathouse to a **barred arch in the cliff** and the **basin under the Lake Tower** (S34) | Tower of London St Thomas's Tower and Traitors' Gate **[SRC: TOL]**; Caernarfon's Eagle Tower "water gate" (castle doc **[W-CAER]**) |
| Fisher and Boat towers | quay corners | 16 × 16 | lake watch; boat store | — |

### 2.3 Underground (basement plan)

- **B1 (−7):**
  - Wine cellar under the hall (Whitehall vaulted wine cellar **[SRC: WH]**).
  - Serving room under the dais (S17).
  - Wet larder.
  - Undercroft of the central tower.
  - Muniment Archive under the library.
  - Founders' Crypt under the chapel (S37).
  - Lock-up under the inner gate (start of S19).
  - Tower laboratories.
  - Alchemist's Vault (S29).
  - Stove cellar of the orangery.
  - Sunken Observatory crypts (−4).
  - Ice-house well, 9 deep × 5 wide.
- **B2 (−12):**
  - The **Tunnel Junction** under the central tower (S36), with three tunnels: to the inner gate (S3), to the Lake Tower basin and water gate (S33, S34), and to the crypt (S37). This follows Dover **[SRC: DOV]**.
  - The **Catacombs** under the cloister (S38).
  - The **dry-well tunnels** (S26): one to the ditch floor as a sally, one to a hidden door on the quay.
  - The **Countermine** (S39).
  - The **Sewer Hide** (S27).
- **Sewers:** a trunk sewer at the trench (−13) runs inside the gate-side and east curtains and out to the **outfall cascade** on the quay. Every building drains by gully or chute to culverts at −6 and then to the trench (castle doc §6.1). The plan shows the trunks only; each building's branch follows castle doc §6.1.
- **Water law:** the lake enters only the water-gate canal and the basin, as structure sources connected to the lake. The cloister fountain jet → basin → drop shaft → culvert → trench → outfall cascade → lake. The ice-house melt drains to the sewer. The orangery's roof cistern overflows to a gully. Outside the canal, basin, fountain jet and well shafts, the source count is 0 (castle doc R10).

---

## 3. The discovery map: 39 secrets

**Tiers:**
- **I = walk-in.** Found by curiosity. These are `pw:jib_panel` or `pw:secret_painting`, both walk-through (BP-02 1.3.221), or a ladder or trapdoor.
- **II = mechanism.** Vanilla redstone, opened with a clue from the Itinerary.
- **III = keyed or deep.** Needs the Rector's Key (S9), a boat, the night, or the B2 network.

**Rewards:**
- **R** = a room. **V** = a view. **S** = a shortcut.
- **B** = a book. That means a Founder's Note on the real precedent, and in some places a gallery work with its essay (RP-12 / BP-02 gallery, "a book from the gallery").
- **K** = a key or item.

**Users** are the household who use the secret day to day (his "1+3" ruling: lord or Rector and family, guards, servants; ordinary civs never route through). All 39 are player discovery content.

| # | Secret | Where | Tier | How it is found (Minecraft terms) | Reward | Users | Real model |
|---|---|---|---|---|---|---|---|
| 1 | **Masters' Spine** | 2-wide service corridor behind the Masters' Lodgings and the First Court ranges | I | Each set's back wall has a **jib door** (`pw:jib_panel`): flat wall, no frame. Walk into it. | S: First Court ↔ Great Hall screens without crossing the court; B | servants (bedmakers, fuel) | Versailles service rooms behind the Queen's apartment; Kerr's separate service routes |
| 2 | **Stoking Passage** | behind the hall dais, the central-tower arm and the library fireplaces | I | The back of a hearth's flue-breast is a jib panel. A cat sleeps in the warm passage. | S: kitchen ↔ library; R: warm nook | servants (stokers) | Schönbrunn: stoves "stoked… from a passage running behind the walls" |
| 3 | **Porter's Stair in the Wall** | inside the inner gatehouse's 3-thick wall | I | The Porter's Lodge's thick wall has a 1-wide jib panel. A straight 1-wide stair runs inside the wall: up to the gate chamber and wall walk, down to B1 and to the B2 tunnel. | S: gate ↔ walls ↔ tunnels | porter, night watch | Palazzo Vecchio: "narrow stone staircase… carved into the thickness of the medieval wall" (Brienne, 1342) |
| 4 | **Mural Passage** | inside the inner curtain at feet 6, linking T1–T4 | I | Each dormitory floor has a linen press whose back is a jib panel. 1 wide × 2 high, lit by loops. | S: all four house towers joined (for the player only; students never route) | night watch rounds | Beaumaris first-floor passages in the inner walls; Hedingham gallery in the wall thickness |
| 5 | **Panelled Carrel** | Rhetoric classroom | I | One bay of oak panelling (`pw:jib_panel`, plank skin) opens onto a 3 × 3 reading room. | R; B (gallery work and essay) | masters | Baddesley Clinton: "a small room with a door hidden in the wood panelling" |
| 6 | **Roof Hide** | T1 attic eaves | I | A trapdoor in a closet ceiling leads into the roof space and a jib panel in the eaves. | R: the students' cache (cake, cookies, a map) | — | Baddesley Clinton: "another [hide] in the roof" |
| 7 | **Founder's Scrittoio** | off the library's lake end | I | One founders' portrait (`pw:secret_painting`, 2 × 2) is walk-through. | R; **K: the Itinerary**, the discovery map book (§4.1) | Librarian | Palazzo Vecchio: Scrittoio "accessible only thanks to passages concealed behind paintings" |
| 8 | **Studiolo** | behind the Scrittoio | II | A **chiseled bookshelf** cupboard. Put the "Studiolo" volume in **slot 4** → comparator → sticky pistons slide a bookshelf pair (**verify**). | R: windowless barrel-vaulted cabinet with curiosity chests (rare minerals, instruments) | Librarian | Studiolo of Francesco I, "part-office, part-laboratory, part-hiding place" |
| 9 | **Secret Drawers and the Rector's Key** | the Scrittoio desk | II | An item frame on the desk holds a compass. Turn it to the "north" rotation (comparator from the frame, **verify**) → a dropper "drawer" ejects the key. | **K: the Rector's Key**, which unlocks Tier III | Rector | Versailles: "numerous secret drawers and compartments" |
| 10 | **Closed Stack** (lectern lock) | 16 × 16 strongroom off the library | II | The reading lectern holds the Library Catalogue. Open it to **the page the Itinerary names** → comparator strength → iron door (lectern comparator output, **verify**). | R: lockers of rare and enchanted books | Librarian | Doge's Chancellery lockers "from 1268"; Tesoretto "hidden compartments" |
| 11 | **Double Hide** | inside the Closed Stack (upper tier) | I + II | An obvious **outer hide** (a jib panel) holds a decoy. The **inner hide** lies behind a second painting at the back of the first. | R; B; the real prize (a rare gallery work) | — | Nicholas Owen: "a more easily discovered outer hiding place, which concealed an inner hiding place" |
| 12 | **Library Roof Trusses** | above the library ceiling | I | One upper-gallery bookcase hides a vanilla ladder (custom blocks cannot be climbable). Walk the trusses to a dormer. | V: over the lake; S to the central tower's arm | — | Palazzo Vecchio: "the vast space above the ceiling… trusses" |
| 13 | **Map Room** (dispatch room) | end of the Long Gallery | I | A jib door in the gallery's end wall | R: the **wall map** of the academy, with item-frame maps; if Q5 = yes, the script marks each secret found; the porters report here | Rector, porters | Versailles: the inner study "the dispatch room, where… he received his spies" |
| 14 | **Rector's Vice Stair and Supper Closet** | hall dais → Rector's bedchamber → 4 × 4 turret closet | I | The tapestry behind the high table is a wool-faced jib panel. A **narrow A spiral** climbs to the bedchamber and the supper closet. | S; R: the closet, with a squint into the hall | Rector, servants | Holyrood "small vice stair"; the supper cabinet "12ft by 12ft"; Hampton Court spiral from the king's bedchamber to the wardrobe |
| 15 | **Oratory Window and Tribune Door** | Rector's oratory → chapel | I | A shutter (jib panel) opens on the chapel altar. A second jib door leads to the tribune. | V: the altar from the Rector's bed; S | Rector | El Escorial: "Philip II could witness from the bed the liturgy"; Versailles chapel tribune (research H15) |
| 16 | **Bricked-up Arch** | Rector's bedchamber alcove | I | A visible blocked arch of **cracked stone bricks**. In survival the player can break it; behind is a closet with lore. At AII-2 the builders open it to the Long Gallery side. | R; B | — | Hampton Court: "a bricked-up doorway… once connected the king's secret lodgings directly with Wolsey's gallery" |
| 17 | **Flying High Table** | dais ↔ B1 serving room | II | The **trapdoor trace** in the dais floor is the hint. A lever in the serving room (or a button under the high table) raises a 3 × 1 table section on sticky pistons. | S: the B1 serving room → service tunnel → wine cellar | servants, at every hall meal | Choisy / Petit Trianon "flying tables"; "Traces of a trapdoor remain in the… parquet" |
| 18 | **Wardrobe Door** | Proctors' Chamber → Masters' Council Chamber | I | The oak press (shelves and barrels) has a walk-through back. | S; R: the council table and its records | Rector, Proctors | Doge's Palace: Inquisitors' room "secret entrance behind a wooden wardrobe" |
| 19 | **Proctors' Way** (secret itinerary) | inner gatehouse, B1 → attic → Council | II | **One-way chain.** Each room's exit opens only by a button hidden *in that room*: lock-up (B1) → narrow stair → Proctors' office → archive → attic armoury → **the Leads** (cells under the lead roof) → two flights down → Council Chamber. | R ×6 in the museum's order; B (the itinerary story) | Proctors | Doge's Palace Secret Itineraries, in the leaflet's order; Piombi under the lead roof |
| 20 | **Bursary Strongroom** | Bursary, inner gatehouse | II | "Pay the toll": drop exactly N gold nuggets on a **weighted pressure plate** in the counting hatch → comparator → the strongroom door (**verify**). | R; K (coin chest, if the coin system allows) | Bursar | Palazzo Vecchio Tesoretto "two hidden doorways" (R3 §2.2); the exchequer counting table (R3). **The toll mechanism is INVENTION.** |
| 21 | **Governess's Doors** | Junior School, Governess's bedchamber | I | **Two hangings, one each side of the bed.** The left one leads to the night nurseries; the right one to the Children's Stair. | S | Governess, nurses | Versailles: "The two doors under hangings on either side of the bed"; the 6 Oct 1789 escape by the left door |
| 22 | **Children's Stair** | Junior School → schoolroom in the attic | I | A cupboard whose back is a jib panel; a B spiral | S; R: schoolroom | children, nurses | Hampton Court: the child one floor below the father; Prince's Lodgings; Versailles Dauphin. **The link stair is design.** |
| 23 | **Twin Stair** | the central tower's stair hall | I | Two narrow A spirals share one core wall pierced with **loopholes**: climbers see each other but never meet. One stair serves the library galleries; the other serves the dormitory bridges and the bell loft. To reach the top you must **change stairs** through the one loophole that is a jib panel. One stair also continues down to B2 (S36). | S; V | everyone (public stair) | Chambord: "two spirals… without ever meeting", "they never come in sight, but by small loopholes". **ADAPTED:** a true double helix needs design D (Q3). |
| 24 | **Turning Bridges** (the moving stairs) | the stair-hall void | II | Three 3-long bridges between the gallery rings retract and extend on sticky pistons when the bell rings each hour. Each hour joins a different pair of galleries, so the route to a room changes during the day. | S (time-dependent); puzzle | everyone | Turning bridge with a counterweight pit (castle doc **[W-DRAW]**); flying-table lift **[VT]**. **Applying this inside a stair hall is INVENTION (the genre feature).** |
| 25 | **Clock-Keeper's Room** | top of the Clock Tower | II | The door at the head of the clock-room stair opens only **at noon and midnight**: a daylight sensor (inverted at midnight) or the bell script. | R: the keeper's bed and the clock works; V | clock keeper | Louis XV's "even more private bedroom in the Petits Cabinets on the top of the palace". **The timed door is INVENTION.** |
| 26 | **Old Dry Well** | Schools Quad | I | The well is dry. A ladder on the inner face goes down to B2 and two tunnels: one to the **dry-ditch floor** (a sally), one to a hidden door on the **quay**. | S: escape to the lake | night watch | Kremlin Tainitskaya: "a secret well inside and a hidden exit to the Moskva River"; Dover sally tunnels |
| 27 | **Garderobe Drop and Sewer Hide** | Masters' garderobe tower → B2 | I | A closet with a trapdoor over a 1 × 1 ladder shaft into the sewer gallery. The **Sewer Hide** (12 × 9) has room for "six or seven". | R; B | servants (sewer keeper) | Baddesley Clinton: priests slid "down… the old garderobe shaft into the house's sewers" |
| 28 | **Covered Bridge: second corridor and lower way** | over the dry ditch | I / III | (a) The bridge has **two parallel corridors**; the second sits behind a jib door. (b) Trapdoors in both abutments open on an **enclosed passage under the deck**. | S: into the Laboratory Ward after the curfew lock | Proctors, lab masters | Bridge of Sighs "two separate corridors"; Passetto "top level… patrol walkway, and underneath… the hidden enclosed escape passage" |
| 29 | **Alchemist's Vault** | under the Alchemy House | II | Put **three potions** in the brewing stand on the master's bench → comparator strength 3 → piston door (**verify**). | R: the vaulted laboratory; K: rare brewing ingredients | lab masters | Uraniborg basement "alchemical laboratory" (castle doc). **The potion lock is INVENTION.** |
| 30 | **Orangery Stove Passage** | behind the orangery's back wall → the Sunken Observatory | I | The gardeners' bothy's fire-door leads into the passage behind the glasshouse stoves, which continues underground to the observatory crypts. | S | gardeners (stokers) | Schönbrunn stoking passage. **Extending it to the observatory is COMPOSITE.** |
| 31 | **Sunken Observatory** | Gardens Ward mounds | III (night) | A garden-pavilion trapdoor. The instrument crypts' **shutters** are trapdoors on an **inverted daylight sensor**, so they open only at night. | R; V: the night sky; B (star chart) | astronomer | Stjerneborg: instruments "placed underground" under shutters / a rotating dome (castle doc **[URAN]**) |
| 32 | **Ice-House Hole** | the ice-house well → sewer | I | The melt-water drain at the bottom of the 9-deep well is a 1 × 2 crawl into the sewer. | S; B (**the Nesvizh myth**, told as a myth) | — | Hampton Court ice house, 9.1 × 4.9 m with a drain. **MYTH INVERTED:** at Nesvizh the melt-water hole was only *believed* to be a secret passage. Here it really is one, and the book says so. |
| 33 | **Water Stair** | the Lake Tower spiral → basin at −12 | III | The spiral passes the astronomer's bedchamber and continues past B1 behind an iron door. The **Rector's Key** works it, through the F4 key law: the hatch opens from above only with the key in hand. | S: to the basin and the boats | Rector, boatman | St Thomas's Tower: "The spiral staircase… goes all the way down to the river" |
| 34 | **Water Gate** | the barred arch in the cliff ↔ canal ↔ boathouse | III (boat) | Row a boat up the canal from the lake. The bars lift by a lever inside, or at dawn when the boatman opens them. | S: arrive by water into B2 | boatman, guards | Tower of London water gate / Traitors' Gate; Caernarfon Eagle Tower basement water gate |
| 35 | **Way from the Lake** | cliff stair, quay ↔ Lake Walk | I | The postern at the top is a jib panel in the terrace parapet. A gated stair is cut down the cliff. | S | fishers, guards | Harlech "Way from the Sea", "a gated and fortified stairway"; Whitehall river gate steps |
| 36 | **Tunnel Junction** (three ways) | B2 under the central tower | III | Reached by the Twin Stair's deeper flight (S23) behind an iron door that the Rector's Key opens. Three tunnels branch from it. | S: the hub of the underground | guards (night rounds) | Dover: "three passages to three towers meet in a junction" |
| 37 | **Founders' Crypt** | B1 under the chapel | I / III | From the chapel, a jib panel behind the altar. From the junction, a stair. Wall niches hold the founders' heart urns. | R; B (founders' histories) | chaplain | Hofburg Augustinian church: the Herzgruft, "the hearts of 54 members of the imperial family" |
| 38 | **Catacombs** | B2 under the cloister | III | Beyond the crypt: a grid of galleries lined with niches, a small labyrinth with an end room. | R: the **Founder's Charter** (completes the Itinerary) | — | **INVENTION / COMPOSITE:** a crypt is documented (Herzgruft); catacomb galleries under a collegiate castle are not documented in our sources (Q9) |
| 39 | **Countermine** | under the great gatehouse front | I | A jib panel in the guard cellar. A low, narrow, twisting gallery (2 high) ends where it meets an "enemy" mine stub. | R; B (the 1546–47 siege story) | — | St Andrews: mine and countermine of 1546–47, "low, narrow, twisting countermine" (castle doc **[UND-STA]**) |

**The 10 best for play:**
- S23 Twin Stair
- S24 Turning Bridges
- S7 Founder's Scrittoio (painting door)
- S10 Closed Stack (lectern lock)
- S11 Double Hide
- S17 Flying High Table
- S19 Proctors' Way
- S21 Governess's Doors
- S34 Water Gate (by boat)
- S31 Sunken Observatory (night-only)

---

## 4. Puzzles and progression (vanilla redstone plus our blocks)

### 4.1 The Itinerary: the spine of discovery
- **Found at S7.** The Itinerary is a written book with **39 numbered entries**. Tier I entries carry a riddle. Tier II entries carry the clue for that lock: a lectern page, a bookshelf slot, a compass rotation, a nugget count, a potion count. Tier III entries are blank until the Rector's Key is found.
- The book is modelled on the Doge's Palace *Itinerari segreti*, a museum route through the secret rooms in a fixed order **[SRC: DP-I]**.
- **Completion** (with the Founder's Charter from S38) opens the bell loft at the top of the central tower for a final view over the lake.
- **Optional scripted layer (Q5, BP-02):**
  - Each secret has a small volume. A check every 20 ticks against player positions sets a per-player dynamic property bit.
  - The actionbar shows: "Secret 12 of 39 — The Wardrobe Door (Doge's Palace, Venice)".
  - The Map Room wall shows the count.
  - Cost: one cheap scan; no new blocks.

### 4.2 Lock types (all vanilla components; every one is "verify on BDS + PS5")

| Lock | Component | Used by | Engine note |
|---|---|---|---|
| Walk-in door | `pw:jib_panel` (plain or wool or plank skin), `pw:secret_painting` 2 × 2 | Tier I | in the kit, walk-through (BP-02 1.3.221) |
| Right page | lectern + comparator (output by page) | S10 | **verify** |
| Right slot | chiseled bookshelf + comparator (last slot used) | S8 | **verify** |
| Right bearing | item frame rotation + comparator | S9 | **verify** (Bedrock frame comparator output) |
| Right weight | weighted pressure plate (item count) | S20 | **verify** item-entity counting |
| Right brew | brewing stand + comparator (bottles) | S29 | **verify** |
| Right hour | daylight sensor, normal and inverted; or the bell script | S25, S31 | daylight sensors cannot read the moon phase |
| Moving bridge | sticky pistons on a clock pulse from the bell | S24, S17 | redstone clock vs script → Q4 |
| The Key | `pw:hatch` + `pw:sewer_key` law F4 (opens from above only with the key in hand) or an iron door + hidden button | Tier III (S33, S36, B2 gates) | F4 build status: confirm |
| Night lock | the curfew bell closes the covered bridge and the Closed Stack (scripted door states) | gives S28, S26, S4 their purpose | Q10 |

### 4.3 The stairs (genre "odd stairs", grounded)
- **Twin Stair (S23):** two **A turret** wells (2 × 2 each, per `spiral_site.py`) side by side in the 16 × 16 stair hall, with a 1-thick shared wall and iron-bar loopholes at each landing.
  - It rises 1 block per quarter turn, which is 4 per turn. Mid-floor exits fall on faces fixed by the level difference (LC-1006-SP 4). `spiral_site.solve` places the exits; nothing is assumed.
  - A **true Chambord double helix** is NOT buildable with A/B/C. The second helix, half a turn above, would pass about 2 blocks over every tread, under the ≥ 2-block headroom law (Palace II §4.8). It needs a new **design D**, 2 blocks of rise per quarter, giving about 4 clear (Q3).
- **Turning Bridges (S24):**
  - Three bridges cross the void between the gallery rings at three heights.
  - Each is a 3-long deck on sticky pistons with a counterweight pit in the gallery floor as a visual cue.
  - Every bell switches which bridges are out. The galleries always stay reachable by the Twin Stair. **No room may ever be reachable only by a bridge** (villager and verifier rule).
- **Secret stairs (S3, S14, S33):** narrow design A, per his 22:4x Palace II answer. S22 uses B because children and nurses walk it daily.

### 4.4 Rewards economy
- **Books:** each secret gives a Founder's Note: the real story and its source (§11).
- **Gallery works:** the Closed Stack, Studiolo, Double Hide and Carrel hang RP-12 works chosen by `pick()` with `palace_ok`. The book item carries each essay.
- **Shortcuts:** shortcuts turn the 384-block campus into a fast network once known.
- **Views:** bell loft, roof trusses, Lake Tower deck, sunken observatory at night.
- **Keys:** the Itinerary and the Rector's Key are found once per world; copies can be made at the Map Room lectern (design).

---

## 5. How the civs use it day to day

**Roles:** use existing role names only; no new names without approval (Q2). Proposed mapping:
- Rector → `lord`
- Masters, Librarian, astronomer, lab masters → `noble`
- Students → `clerk` (medieval university students were clerks)
- Pupils → `child`
- Porter, bedmakers, cooks, gardeners, boatman, grooms, nurses, Governess → `servant`
- Night watch / Proctors' men → `guard`
- Lock-up cells → `cell` (never homes)

| Bell (clock) | Students (`clerk`) | Pupils (`child`) | Masters / Rector | Servants | Guards |
|---|---|---|---|---|---|
| Dawn | rise in the house towers; chapel | nurses wake them (nurses' lodging "within earshot") | chapel tribune (Rector, via S15) | stokers in S2; cooks in the kitchen tower; boatman opens the water gate (S34) | night watch ends; gate opened |
| Morning | lectures in the Schools Quad; library | schoolroom (via S22) | teach; Council (S18 used by the Proctors) | bedmakers in the towers via S1; gardeners in the orangery (S30 stoke) | porter at the inner gate |
| Noon | **dinner in the Great Hall**: the high table rises (S17) | junior refectory | high table | serving room → S17; service tunnel | gate guard |
| Afternoon | laboratories over the covered bridge; greenhouse; library | day room, gardens | laboratories; Rector's study | laundry, stables, boathouse | patrol the outer court |
| Evening | supper in hall; house common halls | night nurseries | Senior Common Room | kitchen | **curfew bell:** bridge and Closed Stack locked |
| Night | sleep (48 per tower at AII-2) | sleep | Rector sleeps (S14 stair to hand) | — | **rounds:** S4 mural passage, S3 porter's stair, the B2 junction (S36), S26 tunnels |

**Walk-graph rules (for BP-02):**
- Students and pupils are ordinary civs and **never route through any secret**.
- Servants route through the service network (S1, S2, S17, S30) because the Kerr / Versailles separation is their real job.
- Guards route through S3, S4, S26 and S36 at night.
- The Rector's private ways (S14, S15) are routed only for the `lord` bed holder.
- Everything else is **no-walk**, player content only.
- Job-station rule (R3 §5.1 rule 7): a station is found only "within 16 blocks and 4 blocks height", so each servant's bed stays on the floor of their station: cooks' loft over the kitchen, grooms' loft over the stables, nurses in the Junior School.
- The `pw_civ_walk` "stairs = half floor" note (LC-1006-SP RETRO) applies before villagers walk indoors on spiral blocks.

**Beds at AII-2 (proposal):**

| Group | Beds |
|---|---|
| Rector (`lord`) | 1 |
| Masters and officers (`noble`) | 18 |
| Students, 4 towers × 48 | 192 |
| Pupils | 24 |
| Governess and nurses | 5 |
| Servants | ≈ 38 |
| Guards | 12 |
| **Total homes** | **≈ 290** |

The infirmary's 12 beds are sick beds, not homes (Q2).

---

## 6. Growth: Academy I → Academy II

| Tier | Clock trigger (academy city, castle-first ladder) | Builds | Secrets open |
|---|---|---|---|
| **AI-1** | founding (the reservation for 384 plus the lake is made **now**) | core 4 × 4: inner gatehouse (as the gate), four house towers (2 dormitory floors), Great Hall, kitchen tower, chapel, First Court, cliff walk, Lake Tower base, B1 cellars | 1, 2, 3, 7, 14, 17, 18, 21, 37 (crypt from the chapel) |
| **AI-2** | town III | towers to full height (4 dormitory floors), library, Schools Quad, cloister, infirmary, Rector's lodging upper floors, clock tower, observatory deck, Junior School (all floors and the attic schoolroom) | 4, 5, 6, 8, 9, 10, 11, 12, 15, 16 (lore only), 22, 25, 26 (to the ditch side only), 27 |
| **AII-1** | city I | **the ring**: great gatehouse + viaduct (the Academy I gate becomes the inner gate, the Beaumaris concentric pattern), outer court, stables, guest house, dry ditch + **Laboratory Ward** + **Covered Bridge**, **Gardens Ward**, **quay terrace + boathouse + water-gate canal** (land pushed out into the lake, the Whitehall riverside terrace model), B2 junction and sewer outfall | 19, 20, 26 (to the quay), 28, 29, 30, 32, 33, 34, 35, 36, 39 |
| **AII-2** | city III | core pieces re-placed `_t2`: **Central Tower with the Twin Stair**, Long Gallery and Map Room, 2 more dormitory floors per tower, bricked arch opened (S16 becomes a passage) | 13, 23, 24 (one bridge), 31, 38 |
| **AII-3** | metropolis | Turning Bridges complete (3), bell loft, the Itinerary completion reward; design D double helix if approved | 24 (all), the final view |

**Real growth anchors:**
- Kenilworth: keep → hall palace → glazed lodgings.
- Alnwick: castle → palace in stages.
- Uraniborg: house first, then Stjerneborg's sunken instruments added later.

All from the castle doc §9 / [URAN].

---

## 7. Drawings

| File | Shows |
|---|---|
| `ACADEMY-II-PLAN-GROUND.png` | feet 0. The 6 × 6 piece grid (r0–r5 / c0–c5). Every room is labelled. Secret routes are magenta dashes with numbered markers. The quay row is shown at −12; the lake lies beyond. |
| `ACADEMY-II-PLAN-UPPER.png` | feet 6. Upper floors; the central tower's cross arms and void; the mural passage ring; the Rector's lodging upper floor; the Junior School nursery floor. |
| `ACADEMY-II-PLAN-BASEMENT.png` | B1 rooms (−7), B2 tunnels (−12), trunk sewers (−13), catacombs, water-gate canal and basin, the outfall. |
| `ACADEMY-II-MASSING.png` | 3/4 view from the gate-side corner: heights, the ditch, the cliff and quay, the lake. Sketch only. |

---

## 8. Integration and engine notes (for the build plan, not decided here)

- **Generator:** this would be `academygen.py`, inheriting castlegen's `Building` and `spiral_site`. Prerequisites:
  - Fix the castlegen `cut()` bug F1.
  - Lay custom-block stairs LAST (LC-1006-SP 3).
  - Never mirror; rotate only (LC-1006-SP 1).
  - Use lowercase ids.
- **Verifier** (castle_verify, castle doc §11): R2 (rooms), R4 (towers), R9 (drains), R10 (sources), R11 (beds), R12 (each secret reachable from both ends and not from the court without passing its door), R13 (piece union). New checks:
  - **R14 bridges:** every gallery is reachable with all turning bridges retracted.
  - **R15 headroom:** ≥ 2 on every secret route.
- **Lighting:** light blocks never sit in walkable floors (LC-1005-10). Secret passages stay dim enough to feel secret but must be lit at ≥ 8 so nothing spawns; the lamplighter rule from F5 applies to B2.
- **Size and placement:** 36 pieces; the survey must walk windows; the TOP is about 90 for the central-tower pieces only.

---

## 9. Open questions for Abs0lum

1. **Q1 Footprint:** 6 × 6 (384, recommended: the ring around Academy I, nothing moves) or 5 × 5 (320, a lopsided ring that drops a ward)? The land reservation grows to about 448 with the lake.
2. **Q2 Roles:** map students → `clerk`, pupils → `child`, masters → `noble`, Rector → `lord`? Or approve new roles `student` / `master`? Are infirmary beds homes or not?
3. **Q3 Twin Stair:** two A spirals with loopholes now (buildable), or commission **design D** for a true Chambord double helix?
4. **Q4 Turning Bridges:** vanilla redstone (local, can break when chunks unload) or a BP-02 script on the bell (reliable)? Should they move every in-game hour?
5. **Q5 Discovery tracking:** a scripted "N of 39" counter and the Map Room marks, or books only (pure vanilla)?
6. **Q6** Is it acceptable to break the bricked-up arch (S16) in survival, or should it be a jib panel?
7. **Q7 Spiral A size:** the brief says "narrow 3 × 3", but `spiral_site.py` defines A_turret as a **2 × 2 well**, about 4 × 4 with its walls. Which is meant?
8. **Q8 Site:** the academy on a 12-high cliff over the lake (water gate, quay and outfall at −12/−13)? This fixes the site search to lake-cliff sites (rare, as K7 b intends).
9. **Q9 Catacombs (S38):** pure invention. Keep them as the labelled finale, or end the Itinerary at the Founders' Crypt (documented)?
10. **Q10 Curfew:** should the curfew bell lock the covered bridge and the Closed Stack at night? This is what gives the secret routes their purpose.

---

## 10. Secret → documented precedent (verification table)

Status: **DOC** = the feature is documented as built here. **ADAPTED** = documented, moved to a new place or use. **COMPOSITE** = documented parts joined in a way no source shows. **INVENTION** = no source; flagged. "Mechanism" = how the Minecraft lock works. Every vanilla redstone lock is a game mechanism and is never claimed as historical.

| # | Secret | Documented precedent (quoted in the research doc) | Source key | Status |
|---|---|---|---|---|
| 1 | Masters' Spine | Versailles: the passage behind the Queen's apartment "had always been a suite of service rooms"; Kerr's service separation (R3 §2.3) | VQ, R3 | ADAPTED |
| 2 | Stoking Passage | Schönbrunn: stoves "stoked… from a passage running behind the walls of the rooms" | SCH | DOC |
| 3 | Porter's Stair in the Wall | Palazzo Vecchio: Brienne stair "carved into the thickness of the medieval wall" | PV-S | ADAPTED (gatehouse, not a palazzo) |
| 4 | Mural Passage | Beaumaris "first-floor passages in the inner walls"; Hedingham gallery | BEAU, HED (castle doc) | DOC |
| 5 | Panelled Carrel | Baddesley Clinton: "a small room with a door hidden in the wood panelling" | BAD | DOC |
| 6 | Roof Hide | Baddesley Clinton: "another [hide] in the roof" | BAD | DOC |
| 7 | Founder's Scrittoio | Scrittoio of Cosimo I "accessible only thanks to passages concealed behind paintings" | PV-P | DOC |
| 8 | Studiolo | Studiolo of Francesco I, barrel-vaulted, "part-hiding place"; Tesoretto hidden compartments | PV-ST, PV-T | DOC room · INVENTION mechanism (chiseled shelf) |
| 9 | Secret Drawers + Key | Versailles king's suite: "numerous secret drawers and compartments" | VK | DOC idea · INVENTION mechanism + the key item |
| 10 | Closed Stack | Doge's Chancellery lockers "from 1268"; Tesoretto | DP-L, PV-T | ADAPTED · INVENTION mechanism (lectern) |
| 11 | Double Hide | Nicholas Owen: outer hide "concealed an inner hiding place" | OWEN | DOC |
| 12 | Library Roof Trusses | Palazzo Vecchio: "the vast space above the ceiling of the Salone… trusses" | PV-P | ADAPTED (library, not the Salone) |
| 13 | Map Room | Versailles inner study, "the dispatch room… received his spies" | VK | ADAPTED · scripted map = INVENTION |
| 14 | Vice Stair + Supper Closet | Holyrood "small vice stair"; supper cabinet "12ft by 12ft"; Hampton Court bedchamber spiral | HOL, HC | DOC |
| 15 | Oratory Window + Tribune | El Escorial bed-to-altar view; Versailles chapel tribune | ESC, research H15 | DOC (Escorial) · tribune PARTIAL (the research doc names it without a direct link) |
| 16 | Bricked-up Arch | Hampton Court "bricked-up doorway" to Wolsey's gallery | HC | DOC · breakable = INVENTION |
| 17 | Flying High Table | Choisy / Petit Trianon "flying tables"; the trapdoor trace | VT | DOC (planned, cancelled 1772: the idea is documented, the working table was never built) |
| 18 | Wardrobe Door | Doge's Inquisitors' "secret entrance behind a wooden wardrobe" | DP-W | DOC |
| 19 | Proctors' Way | Doge's Secret Itineraries, in the leaflet's order; Piombi | DP-I | DOC sequence · ADAPTED to a gatehouse · one-way buttons = INVENTION |
| 20 | Bursary Strongroom | Tesoretto "two hidden doorways"; exchequer counting (R3) | PV-T, R3 | ADAPTED · **toll mechanism INVENTION** |
| 21 | Governess's Doors | Versailles: "two doors under hangings on either side of the bed"; 6 Oct 1789 | VQ | DOC |
| 22 | Children's Stair | Hampton Court (Mary below Henry); Prince's Lodgings; Versailles Dauphin below the King | HC, HCN, Versailles Dauphin | ADAPTED · **link stair = design** (as in Palace II H5) |
| 23 | Twin Stair | Chambord: two spirals "without ever meeting", "by small loopholes" | CH | ADAPTED (side-by-side wells; the true helix needs design D) |
| 24 | Turning Bridges | turning bridge + counterweight pit; flying-table lift | W-DRAW (castle doc), VT | **COMPOSITE / INVENTION** (genre feature; no stair hall with moving bridges is documented) |
| 25 | Clock-Keeper's Room | Louis XV's private bedroom "in the Petits Cabinets on the top of the palace" | VK | ADAPTED room · **timed door INVENTION** |
| 26 | Old Dry Well | Kremlin Tainitskaya: "secret well inside and a hidden exit to the Moskva River"; Dover tunnels | KRM, DOV | DOC |
| 27 | Garderobe Drop + Sewer Hide | Baddesley Clinton: down the garderobe shaft "into the house's sewers", room for "six or seven" | BAD | DOC |
| 28 | Covered Bridge ways | Bridge of Sighs, two corridors, span 11 m; Passetto, two levels | BoS, PAS | COMPOSITE (two documented bridges merged) |
| 29 | Alchemist's Vault | Uraniborg basement "alchemical laboratory" | URAN (castle doc) | DOC room · **potion lock INVENTION** |
| 30 | Orangery Stove Passage | Schönbrunn stoking passage | SCH | ADAPTED · extension to the observatory = COMPOSITE |
| 31 | Sunken Observatory | Stjerneborg: instruments "placed underground" under shutters | URAN (castle doc) | DOC |
| 32 | Ice-House Hole | Hampton Court ice house 9.1 × 4.9 m; Nesvizh melt-water hole taken "to be the entrance to a secret underground passage" | HCI, NES | **MYTH, used knowingly:** at Nesvizh it was a myth; here it is built and labelled as invention |
| 33 | Water Stair | St Thomas's Tower spiral "goes all the way down to the river" | TOL | DOC |
| 34 | Water Gate | St Thomas's Tower water gate / Traitors' Gate; Caernarfon Eagle Tower water gate | TOL, W-CAER (castle doc) | DOC |
| 35 | Way from the Lake | Harlech "Way from the Sea"; Whitehall river gate steps | CW-HARL (castle doc), WH | DOC |
| 36 | Tunnel Junction | Dover: three passages to three towers meeting in a junction | DOV | DOC |
| 37 | Founders' Crypt | Hofburg Herzgruft, "hearts of 54 members of the imperial family" | HOF | ADAPTED (founders, not emperors) |
| 38 | Catacombs | — (a crypt is documented; the galleries are not) | — | **INVENTION** |
| 39 | Countermine | St Andrews mine and countermine 1546–47 | UND-STA (castle doc) | DOC |

**Count:**
- Documented features: 35 of 39, as DOC or ADAPTED (S30 is ADAPTED with a COMPOSITE extension).
- Joined from documented parts: 2 (S24, S28), marked COMPOSITE.
- Myth used knowingly: 1 (S32).
- Pure invention: 1 room (S38).
- Lock mechanisms (vanilla redstone) are inventions throughout, as stated.

**Myths kept OUT** (from research §5): no tunnel to a distant castle or church; no "dozens of invisible doors" counted as fact; no clockwise-stair defensive lore (both hands are allowed; spirals are rotated, never mirrored); no Louis XV mistress elevator; no hidden underground world.

---

## 11. Sources (keys → research docs; every URL is in their own source lists)

From `_docs/palace/PALACE-II-RESEARCH-2026-10-06.md`:
- **VQ:** Google Arts & Culture / Château de Versailles, Tour of the Queen's Chamber; Wikipedia, Petit appartement de la reine
- **VK:** Wikipedia, Petit appartement du roi; Versailles Century, King's private apartments pt 2
- **VT:** Wikipedia, Petit Trianon
- **HC:** Tudor Travel Guide, Henry VIII's lost apartments
- **HCN:** HRP, Uncovering Edward VI's nursery
- **HCI:** Wikipedia, Ice house (building)
- **HOL:** Tudor Travel Guide, Holyroodhouse; RCT, Explore Mary, Queen of Scots' Chambers
- **PV-S / PV-P:** Finestre sull'Arte, Secret Pathways; MUS.E Firenze, Secret passages
- **PV-ST:** Wikipedia, Studiolo of Francesco I
- **PV-T:** R3 §2.2
- **DP-I:** Palazzo Ducale Secret Itineraries leaflets 2019/2020; Wikipedia, Piombi
- **DP-W / DP-L:** Justin Plus Lauren, Doge's Palace Secret Itineraries
- **BoS:** Structurae, Bridge of Sighs
- **CH / CH-X:** Chambord visitor plan 2022; Wikipedia, Château de Chambord
- **TOL:** HRP, Palace secrets: the medieval palace; Wikipedia, Traitors' Gate
- **PAS:** Wikipedia, Passetto di Borgo
- **KRM:** Kremlin Museums, Tainitskaya Tower
- **DOV:** Kent HER MKE111638
- **WH:** British Listed Buildings, Queen Mary's Steps; Stuff About London, wine cellar
- **SCH:** Schönbrunn audio-guide text 2025
- **HOF:** Wikipedia, Augustinian Church, Vienna
- **ESC:** Fascinating Spain, El Escorial
- **BAD:** Wikipedia, Baddesley Clinton
- **OWEN:** Wikipedia, Nicholas Owen
- **NES:** Gallerix, castle dungeons: legend and reality
- **Nursery (room):** Wikipedia
- **R3:** `_docs/civitas_research/R3-PALACES-GREAT-HOUSES.md`

From `_docs/castle/CASTLE-DESIGN-COMPLETE-2026-10-06.md` §13:
- **URAN:** W-URAN, Wikipedia, Uraniborg
- **BEAU:** W-BEAU
- **HED:** W-HED
- **W-CAER**
- **W-CONWY**
- **CW-HARL:** castlewales.com, Harlech
- **UND-STA:** Undiscovered Scotland, St Andrews Castle
- **W-DRAW:** Wikipedia, Drawbridge
- **W-KRAK**
- **CST-RABY**
- **NT-BOD**

Not from the research docs (general facts, used only for non-secret programme content): the medieval curriculum subjects (trivium / quadrivium) and "clerk" as the medieval word for a scholar.
