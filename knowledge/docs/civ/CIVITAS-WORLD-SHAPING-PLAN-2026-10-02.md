# CIVITAS — WORLD-SHAPING PROGRAM (his 22:24: "very VERY expansive — it literally creates the actual world; take your time; unconventional methods")
Written 22:4x CT 2026-10-02. Supersedes the street-and-plots view of CIVITAS-VILLAGE-V3-PLAN (that work stands as the
first slice: tiers, skins, terraces, stoops, villagers, economy — all server-verified). This plan makes the settlement
system the civilisation's WORLDGEN: it reads the land, shapes it, and keeps reshaping it as the town lives.
Rulings carried: 20:04 (my call, research-based, no questions → ASSUMPTIONs logged), E1–E7, 22:23 elevation, 22:24 expansive.
Method law for every step: build → BDS probe (numbers) → server-dump render (picture) → report "here is what I see".

## 0 · Principle
A town is not placed on the land; it is grown out of it. Every decision the clock makes is a function of the terrain it
reads (height, slope, water, forest, rock), and every day the town lives it leaves marks on that terrain (pits, clearings,
fields, worn roads, walls). "Unconventional" here means: contour streets instead of straight ones; houses cut into the hill
instead of plots on pads; bridges and cuttings where the land says so; a quarry that really digs, a lumberyard that really
fells (our BIGCANOPY template trees), fields that really grow; a treasury that counts blocks, not just numbers.

## 1 · Read the land (SITE READER)
- Over a 160 × 160 site (the ticking-area law: ≤ 100 chunks): a heightfield (ground y per column, trees/plants/snow skipped),
  a water mask (surface water columns, flood-filled into bodies: pond / lake / river by size and shape), slope (|∇h|),
  forest density (logs + our root blocks per 16 × 16 cell), rock exposure (stone/andesite/granite at the surface), sand/beach.
- Products: `site.h[x][z]`, `site.water`, `site.slope`, `site.forest`, `site.rock`, and a classification per 8 × 8 cell:
  FLAT / GENTLE / STEEP / CLIFF / WATER / SHORE / FOREST / ROCK.
- Site choice (when the player says `found` with no corner, or a daughter settlement is founded): score = flat-ish core
  (for the square) + water within 40 + forest within 60 + rock within 60 − swamp/water share; the best corner inside the area.
- Stored compactly (run-length rows, like the dump) in a dynamic property per settlement; refreshed when the town grows.

## 2 · Streets on contours (the unconventional street)
- The MAIN STREET follows a contour: from the square's knoll, walk east and west keeping |h − h0| ≤ 1, turning up or down
  the slope only when the contour would cross water or a cliff; it may bend (a sequence of segments, each axis-aligned, so
  plots keep their rotations). The street therefore hugs the hillside — terraced into it on the uphill side (cut + clad
  cobblestone face), built up on the downhill side (fill + retaining face).
- CROSS-STREETS climb the slope: straight stairs where the rise is ≤ 1 per 2 cells, SWITCHBACKS (zig-zag ramps with a
  landing every 4 blocks of rise) where steeper. Materials: cobblestone steps now; the pw:ramp_cobble family / stairs once
  witnessed.
- The SQUARE: the flattest 12 × 12 knoll within 30 blocks of the main street's middle; the bell, the well and the town hall
  face it; the market stalls (rung 2 of the Presence Ladder) stand on it on market days.
- Street profiles are SETTLEMENT-LEVEL data (h per column, never touched by plots): a plot's terrace stops at the street
  margin; its stoop climbs from the street's profile height to its floor; a plot whose floor would be more than 3 above the
  street is cut deeper into the hill instead (a house in the hill).
- Paths harden with use: grass path → gravel at village II → cobblestone at town (worn by the villagers' days).

## 3 · Houses in the hill, terraces, fields
- Uphill plots: the structure's own air cuts the hill; the margin behind the back wall is cut to the slab level and clad
  (cobblestone retaining face, 1 block thick, as high as the cut). The back rooms sit in the hillside; the roof emerges.
- Downhill plots: terrace fill (cobblestone ring, dirt core) to the slab; the exposed face is the terrace wall.
- Split-level (ASSUMPTION, later): where the street behind is ≥ 4 lower, the cellar (feet −5..−1) opens onto it as a
  lower shop front — a second door cut into the cellar wall.
- FIELDS on the gentlest slope: strips 4 wide along the contour, each strip one block higher than the last, retaining
  walls (cobblestone) between strips, farmland + water channels + wheat; the strips multiply as the farm's tier rises.

## 4 · Bridges and cuttings
- Where a street's course meets a gully (drop ≥ 3 over ≤ 12 cells) → a timber bridge: planks deck at the street's grade,
  log piers every 4 cells down to ground/water, fence rails. Where it meets a rise (≥ 3 within 8 cells) → a cutting:
  the street keeps its grade, the sides are clad cobblestone walls (and when the rise is ≥ 6 → a short tunnel, 3 high,
  stone-brick lining, lanterns).
- Over water ≤ 16 wide: the same bridge on piers; wider water: the street turns.

## 5 · The town changes the land over time (the living mark)
- QUARRY: a pit that deepens — each tier removes a bowl of stone (radius +2, depth +2) leaving 1-block ledges (a stepped
  pit), stone counted into the ledger (stone stock = blocks dug); ladders/stairs down one side.
- LUMBERYARD: a clearing that spreads — each tier fells the nearest template trees (logs + leaves removed, pw stump blocks
  left, the roots' tpl decoded → timber = logs felled, counted into the ledger); saplings replanted at village II+.
- FARMS: terraced strips planted (wheat on farmland; growth read daily → grain = harvested wheat, re-planted).
- ROADS harden (above); at CITY: a town WALL (stone brick, 4 high, walkway) around the built extent with GATES where streets
  leave, and a KEEP (town_hall skin "keep": stone walls, a tower) on the highest point inside.
- RUINS: a shop closed for 60 days loses its roof (stage 3 reversed), then its walls — the land takes it back.

## 6 · Between settlements (the world fills itself)
- A prosperous town (prosperity ≥ 0.9 for 30 days, population ≥ 24) founds a DAUGHTER settlement: the site reader scores
  corners 120–200 blocks away (needs water + flat core), the road is cut first (A* over the heightfield: cost = length +
  4·slope + 40·water, bridges where the path crosses water ≤ 16, cuttings where it crosses rises), then the daughter is
  founded as a village with the mother as its trade partner (haulage days = road length / 40).
- Prices converge along roads (economy draft §1.2); a broken road (the player digs it) reopens the gap — a Thread.
- Wagons: a chest-carrying donkey walks the road between the two squares once a day (engine navigation along the road =
  a chain of goal entities every 16 blocks, the slot mechanism of V4b); a wandering-trader-style arrival at the square.

## 7 · The economy reads the world
- Timber stock += logs actually felled by the lumberyard's clearing; stone += blocks actually dug by the quarry; grain +=
  wheat actually harvested; fish += from the dock (barrel = fisherman); hides/meat from the cattle farm's animals (cows
  actually kept in the paddock: spawned at village II, bred by the farmer).
- The Presence Ladder across settlements (E1 all five rungs): supplier (contract line in both ledgers) → stand (a stall
  structure on the host square on market days) → agent (a lectern in the host inn) → branch (a shop plot in the host town
  with the source's sign) → franchise (host-owned; break-away = a Thread, E2 yes).
- Coin + emeralds (E5 c): `buy`/`sell` at the market (built); a CIVITAS coin item later; the town hall exchanges.
- Threads (E6 all three channels): the chronicle (built) + notice board (lectern pages) + villagers who know you (name tags
  + fondness tags) — side stories from the simulation (break-away, shortage, closure, inheritance).

## 8 · Build order (each step: probe + render + report; nothing skipped)
1. SITE READER + settlement-level street profiles + contour main street + cross-stairs (replaces the straight street).
2. Houses in the hill (uphill cut + cladding), terraced fields, the square on the knoll.
3. Bridges and cuttings along streets.
4. Living marks: quarry pit, lumberyard clearing (fells template trees — joins the tree program), fields planted, roads harden.
5. Water: docks, boats, fisherman; cattle in the paddock.
6. City: wall, gates, keep; ruins for the long-closed.
7. Daughter settlements + A* roads + bridges; prices along roads; wagons.
8. Threads channels (notice board, villagers who know you); the ladder's visible rungs (stalls, signs).
Then V6 ship (lineup, brief v4, BP-02 1.3.207 + fix round) — or earlier if he wants to witness a slice.
