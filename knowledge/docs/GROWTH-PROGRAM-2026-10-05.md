# CIVITAS GROWTH PROGRAM — to Metropolis III (2026-10-05, his 20:01 / 20:35 / 20:36 / his choice "Unlock + lanes + taller rebuilds")

## 0. The mechanism (measured — gate runs 224-2 and 225-diag1, the harness site)

**The charter.** The plan asks for **76 lots at Town III and about 380 at Metropolis III** (12 at the founding plus the tier additions).

**What happened:**
- The town reached 34 lots at Town III and 45 at Metropolis I.
- At Town III the streets had **2,330 cells of street side**, but only **605 (26 %) were legal frontage.** The rest went to:
  - ramps (7 cells each, about one every 13–17 cells on rolling land)
  - dead ends (13 cells each)
  - junction windows (13 cells of every 56, on both sides of every street)
  - tees
- The frontage census: of the positions where a medium cottage could start, **0 were free from village on**. Existing lots and their margins took 92 of them, the sewer-hatch spacing rule 82, and hatches in windows 8.
- So every lot after the founding came only from a NEW street. New streets mostly failed:
  - In one pass, 32 windows were tried with 2,977 profile plans.
  - 231 of those were impossible under the 15-block drop rule, which is checked at the worst column.
- The land itself is the root cause. Bedrock's terrain rises steeply and briefly, and **add-ons cannot change its shape.** Mojang's documentation: custom biomes only paint the surface and the climate; `overworld_height` no longer does anything.

## 1. 1.3.225 — THE STREETS UNLOCKED (built; gate 225-1 running)

- **Houses front ramps.** A house may front a run of flat and ramp cells that rises at most 1. Its floor sits at the highest sidewalk, with a step at the door.
- **Unused junction windows are returned.** A window that 3 side-street searches could not open becomes house frontage again.
- **Every home reaches the sewer (his 20:36).**
  - A house with room for its own hatch gets the access piece.
  - Every other house gets a **branch**: 4 cells of the corridor's side wall cut at its shaft, from floor − 11 to floor − 8. That joins the cellar gallery (template y 3..6) to the sewer hall (z 4..8, y 3..6 under every straight and ramp cell, measured from the kit files).
  - A re-laid piece is cut again.
  - `pw:clock sewers` counts the houses that reach the hall; the gate requires all of them.
- **Fishermen (his 20:35).**
  - Shore spots are surveyed from village II: water at least 2 deep, a standable shore cell within 112 blocks of the square.
  - One fisherman per spot, plus one per 8 households, at most 6.
  - Fishermen fish in work hours. FISH is a ledger good (the "fishery"), and the market buys cod, salmon and tropical fish.
- **Early gate reading (village):** 475 cells of frontage (it was 139); 23 more medium cottages fit (it was 0).

## 2. 1.3.226 — LAND: the survey, and BUILDING WITH THE LAND (his 20:48: no levelling — San Francisco / Atlanta)

1. **`/scriptevent pw:clock survey [radius]`** (his 20:48: confirmed). It reads the loaded land around him in an 8-block grid and scores each candidate centre by its gentle area within 64 blocks (slope ≤ 3 per 8 cells, no water). It names the best three sites: distance, direction, area and relief.
2. **The Seattle earthworks are DROPPED** (his 20:48). The town builds with the rises and falls:
   - **Hillside houses (San Francisco).** On a slope a house may step DOWN the hill: the door at street level, the lower storeys below it, or a garden terrace behind. This replaces cutting the slope flat (the existing stilts and podium cases are the start of this).
   - **The city in a forest (Atlanta, "City in a Forest").** Clearing stops at a plot's own box plus its margin. Trees between lanes and behind houses are kept. Streets and lanes are planted from the park-tree system.

## 2b. THE CORE AND THE OUTSKIRTS (his 20:48 — the concentric pattern of urban land use)

- Businesses and their housing gather around the square: shops, inns, workshops, the market, with the owner living above. Homes are sited outward, and the newest homes go to the edge (the contour lanes in the hills).
- As the core grows, an old cottage next to it is CONVERTED. The household moves to a new home on the outskirts, and the lot becomes a business parcel: a shop-house, a workshop or an inn, built taller (this replaces the "taller rebuilds" of §5).
- Districts follow from this on their own: the market core, a craft ring, then the homes in the hills. The DISTRICT table already seeds this; conversion makes it change over time.

## 3. 1.3.227 — CONTOUR LANES

- On slopes the town grows by **lanes**: narrow roads 5–7 wide that keep one level along a contour.
  - Built as straight legs of 14–42 cells joined by elbows.
  - They follow the contour within ±3 using the existing narrow-road machinery (roads7).
- Houses stand on both sides. A lane house's floor is the lane's level.
- Its sewer is a lane drain joined to the nearest street sewer by a trunk. ALL homes reach a sewer, as he ruled.
- Lanes stack one house-height apart (9–12 blocks), with stepped terraces between them (lifts of 3).
- Lanes join by **stair streets** (one every 60–80 blocks of lane; 3 wide; a landing every 6 risers) and by the existing switchback roads.
- The R5 model: Pittsburgh's and Cincinnati's city steps, Providence's Benefit Street.

## 4. 1.3.228 — CASTLES IN THE CLOCK (his 19:48 "castles … finishing to metropolis 3")

- The lord's castle at Town III; the grand castle-palace at City III.
- Built from castlegen.py and CASTLE-PROGRAM-DESIGN-2026-10-05: forced variety, a survey in held areas, one piece per beat, a moat and grounds.
- The water laws from R10 apply:
  - The moat is inert water, placed after its rim is solid.
  - The grounds are sealed before they are drained, with a single `/fill`.
  - Court drains run to the sewer (D-C573).

## 5. 1.3.229+ — CONVERSIONS (taller rebuilds, folded into §2b)

- New townhouse and tenement templates (civgen): 2–4 storeys, 5–8 frontage, deep lots.
- From City II, a cottage on a central street is rebuilt taller on its own lot. Each rebuild counts toward the tier's charter at its household size.
- Cities densify before they spread (R5 §1.5: area grows as population^0.71–0.79).

## 6. The gate for each round

- The probe climbs to METROPOLIS III with a census after every skip.
- Pass conditions:
  - no Hang
  - no memory warning
  - no tick slower than 1 s
  - every finished house reaches the sewer
  - lots meet the charter, or the census names what blocks them
