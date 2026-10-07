# HANDOFF — ROUND 1005d: the town GROWS (2026-10-05, 19:4x → 22:xx CT)

**Authoritative CURRENT-STATE for CIVITAS after this round.** Earlier handoffs of 10-05 still hold for everything not named here.

## 0. What he asked for (verbatim intent)

- **19:45 – 19:48:** Check Haubna's Physics Mod. Keep all previous work going. Kelly's water and the other water (RealSource) are how we made OUR water. Most important: *"the city growing, the civs staying where they're supposed to, and the castles and palaces finishing to metropolis 3 — which means we need a firm understanding of water and all of its capabilities…"*
- **20:01:** RealSource and Kelly's stay. Fix the city growth; rethinking the layouts is OK.
- **20:35:**
  - Understand water *fully*.
  - The terrain doesn't give cities room to sprawl.
  - Add fishermen.
- **20:36:** Shared hatches are approved *only if ALL homes reach the sewers underground*.
- **20:48:**
  - Survey command: yes.
  - Seattle-style levelling: NO. Build WITH the land (San Francisco hillsides, Atlanta's "City in a Forest").
  - Businesses central, homes pushed outward, old houses converted to business parcels, which leads to districts.
  - Contour lanes: yes.
- **21:51 (witness, on 1.3.224):** *"the content log and the messages say things are happening, but nothing is developing."*

## 1. Delivered

| Pack | Version | Status |
|---|---|---|
| BP-02 Tectonic | **1.3.226** (build 3) | gate 226-2 → see §4 |
| RP-01 | 1.3.124 | unchanged (delivered 19:5x) |
| RP-12 Gallery (+LITE) | 1.0.1 | unchanged (delivered 19:5x) |

1.3.225 was never shipped on its own. Everything in it is inside 1.3.226.

## 2. What is new in 1.3.226

1. **Construction no longer freezes (his 21:51).**
   - What was wrong: a stage handed to the builders on a real-time day advanced only while a builder villager stood within 6 blocks of it. Skipped days froze it completely.
   - Now: the whole town crew (the ledger's builders × 40 blocks a day) works every labour site every day, real or skipped, shared across the sites. Bodies at the site add their own work on top.
2. **Street frontage unlocked.**
   - Houses may front ramps (rise ≤ 1 along the front; the floor sits at the highest point).
   - A cross-street gap that 3 side-street searches could not open is given back to the houses.
3. **Every home reaches the sewer (his 20:36).**
   - A house gets its own hatch where there is room.
   - Otherwise it gets a **branch**: 4 cells cut through the corridor wall, from its cellar gallery to the sewer hall. The rows line up on flats and on ramps (checked against the kit files).
   - Lane houses get a branch to the **lane gallery** under their lane.
4. **Contour lanes.** A home with no room on the streets gets a lot on a lane:
   - The lane is 7 wide, keeps ONE level, follows the hillside contour from a street's dead end, and turns at right angles.
   - It has no kerbs (doors open onto it).
   - Its sewer gallery joins the dead end's hall.
5. **Land survey.** `/scriptevent pw:clock survey [radius]` names the 3 gentlest sites in the loaded land (relief ≤ 40).
6. **Business in the centre, homes outward (his 20:48).**
   - Homes fill the outermost streets first, from their far ends inward.
   - From town II, a business whose lot would fall outside the core (60–180 blocks by tier) may buy the nearest finished home inside the core. The family is re-homed (to the edge of town) and the house comes down. At most one conversion a day.
7. **The crown reserves its land from town III.**
   - The palace survey runs until a site is accepted, and the block is closed to houses and lanes.
   - At city II the palace is laid there at once.
   - This fixes gate 225-1, where the spreading town took every site and no palace was laid in 80 days.
8. **Fishermen.**
   - Shore spots are found from village II.
   - Fishermen fish in work hours (splash and sound) and wear the vanilla fisherman's clothes.
   - FISH is a ledger good, and the market buys cod, salmon and tropical fish.
9. **New commands:**
   - `/scriptevent pw:clock frontage [house]`: how many more houses fit, and what refuses the rest.
   - `/scriptevent pw:clock sewers`: how many finished houses reach the sewer.
   - `/scriptevent pw:clock survey`.
10. **Speed work** (gate 225-1 saw ticks of 2.4 s):
    - The day's planning (leftover lots, civic works, centres, block closing) runs on its own tick.
    - The lot-search sets are cached and the plot boxes indexed by chunk.
    - A skipped day's world work (pit, fell, harvest) runs as a background job.
    - The sewer-outfall survey takes one candidate per tick.
    - Slow kit ops are named in the log.

## 3. Research delivered this round

- **R9 §8:** Haubna Physics Mod 3.2.5 ("All rights reserved", Java 25, MC 26.3). GPU PBF liquids, FFT ocean, ripple wave equation. What carries over to Bedrock: splashes, ripple rings, shore-aware extras, `minecraft:buoyant` floating logs.
- **R10:** the Bedrock water reference, W1–W18, every row measured on BDS. The key laws:
  - Script/command `water` is inert until a neighbour changes; `flowing_water` is live.
  - Structures keep a dry interior, but water comes back through openings.
  - Seal first, then drain once.
  - Water flow costs nothing; our scripts around it do.
  - Still sources freeze at altitude.
  - `popped`/`broken` need a collision box.
  - The API's `canBeDestroyedByLiquidSpread` is wrong. Use the measured list.
- **GROWTH-PROGRAM-2026-10-05.md:** the measured mechanism and the plan: lanes, hillside houses, the core and its conversions, castles.
- **RESTRICTED-ASSETS:** W1 (RealSource `water.json`) and W2 (Kelly's `water_flow_grey` maps) recorded.

## 4. Gate results

- **225-diag1 (the old law):** frontage 26 %; 0 free positions from village on.
- **225-1 (to city II).** Lots by tier, with the old law in brackets:

  | Tier | 225-1 | Old law |
  |---|---|---|
  | Village III | 30 | 28 |
  | Town I | 44 | 27 |
  | Town III | 69 | 34 |
  | City I | 80 | 37 |

  Sewers: 55 of 55 linked. **Palace: not laid** (fixed in 226). Worst tick 2.4 s (worked on in 226).
- **226-1 (build 2, to the palace):**
  - Town III reached 76 lots, which meets the charter.
  - The palace was laid at once from the reserve.
  - The survey works (best site 9,408 m² gentle, relief 10). Its #3 site had relief 244, so a relief cap was added.
  - QuickJS rejected build 1 over a duplicate global; `js_dupcheck` now runs on every build.
- **226-2 (build 3, probe 0.0.38):**
  - **Real time: 7,226 ticks at speed 20 → 8 stage rises; builder sites advancing.**
  - **Correction (told to him 23:3x):** after shipping, the climb hit a **3,170 ms watchdog hang at City II (150 buildings)**, right after the probe's `plots` step. The watchdog interrupted it inside the Naturalist add-on's `entity/Kakapo.js`. 18–23 MB a minute of dynamic properties were being saved. On PS5 (10 s limit) this is a stutter, not a crash.

## 4b. The 226-2 hang: profiled, fixed in 1.3.227

**Method.** `pw_prof.js` (a BDS-only diagnostic, never shipped) wraps every scheduled callback, job step and event handler and charges its time to the place that registered it. It ran on the kept 226-2 world with the hangprobe.

**PROF1 (1.3.226 as shipped):** worst tick 1,324 ms; 96 ticks over 250 ms in about 15 minutes. Script time per 1,200 ticks:

| Script | Time | Cause |
|---|---|---|
| `Kakapo.js` | 5.3 s | walked EVERY entity every tick |
| schedule beat | 4.2 s (max 1,090 ms) | at market hours, finding each household's shopper scanned the whole census for every civ; building lists scanned per civ; up to 6 route searches |
| flutter | 4.1 s | 18 entity queries every 2 ticks |
| work | 2.4 s | hands cache: `PEOPLE.byId` per villager |
| shop | 1.8 s | |
| save | 1.7 s | every 100 ticks |
| walk sweep | 1.6 s | `lead_off` triggered on every idle civ |
| deer | 1.7 s | |

**The mechanism:** no single culprit. The schedule beat at work start or market time, a 284 ms walk-graph rebuild, route searches of up to 422 ms, the per-tick add-on loops and a save could all land in one tick. Kakapo was only where the watchdog interrupted. (The exact 3.17 s tick was not reproduced; the best replay was 1,324 ms. The fixes bound every contributor.)

**The saved town:** 3,621,793 characters. 3.09 million of them were TRUST entries: 63,959, of which 62,587 were opinions of ex-friends that nothing reads, plus 162 dead people still holding opinions.

**1.3.227 fixes:**
- The schedule is a job, with a per-pass context: buildings by id, a shopper map, open shops, labour sites.
- `PEOPLE.byId` is indexed.
- Routing:
  - route planning shares 40 ms a tick;
  - the walk graph is built as a job, labelled into connected pieces;
  - A* uses number keys with a deeper-first tie-break, and a long search continues as a job.
- Walk sweep: `lead_off` only for civs still tagged `civ:led`.
- Shops: one lookup per keeper; the anchor is renewed only when low; at most 2 hires a beat.
- Work: face searches share 40 ms a beat.
- The occupancy test uses number keys and a box grid.
- Cores: op anchors are read once per tick.
- Census: rumour spreading uses sets.
- Add-on loops: Kakapo keeps only kakapos (every 10 ticks); deer every 4 ticks (chances ×4); flutter tracks its birds.
- Saves every 600 ticks.
- People diet: the dead keep no opinions, neutral idle entries are forgotten, opinions go with the friendship, 4 decimals. One 24-day skip: 3.62 M → 2.15 M characters.
- The double navigation on rat / hedgehog / giant rat is removed.
- New command: `pw:clock statesize`. The tier-work slow line now names its step.

**PROF4 → PROF9:** worst non-diagnostic tick 442 → 258 ms in normal play. Skips still show lag slices of about 0.5 s, plan days of about 0.5 s and one tier step of 910 ms; these go to the next round.

**Tests:**

| Suite | Result |
|---|---|
| route | 468/468 |
| occupied | 97,680/97,680 |
| diet | 8/8 |
| frontage | 12/12 |
| lanes | 14/14 |
| market | 16/16 |

**Gate 227-1** (fresh world, probe 0.0.39 with `statesize` at every tier, hang limit 3 s): running from 00:17 CT 10-06.

## 5. His test steps (1.3.226)

1. **Install.**
   - Open the Drive folder ClaudeUploads and download `BP-02-AbsolutRealism-Tectonic-BP-v1_3_226.mcpack`.
   - Open it so Minecraft imports it.
   - In the world: Settings → Behavior Packs → Active. Replace BP-02 1.3.224 with 1.3.226. Keep RP-01 1.3.124 and RP-12 1.0.1.
2. **Pick land.** Stand where you'd like a city and type `/scriptevent pw:clock survey`. Fly to site 1 and type `/scriptevent pw:clock village`.
3. **Grow.**
   - `/scriptevent pw:clock speed 20`, then play or wait.
   - Or use `grow` and `skip 30` as before.
   - Each skip line should now name stages rising ("#9 cottage_m -> frame").
4. **Check the town.** Type each of these and screenshot the answer:
   - `/scriptevent pw:clock frontage` (where houses still fit)
   - `/scriptevent pw:clock sewers` (every house linked?)
   - `/scriptevent pw:clock status` (palace reserve line from town III)
5. **Watch for:**
   - houses rising on ramps (a one-block step at the door)
   - lanes on the hillsides with houses on both sides
   - fishermen on the shore
   - a chat line from the crown reserving its land
6. **If anything stalls:** `/scriptevent pw:clock log`, and screenshot it.

## 6. Backlog (next rounds)

- **His 00:18 (10-06): after he uploads the 11 manual downloads to Drive ClaudeUploads/Civ-Mods-Reference/manual, write the REPORT: everything usable from the civ mods and how to implement each in CIVITAS.** 87 files are already there (index: README-CIV-MODS-REFERENCE.md).
- Skip-path spikes (1.3.227 gate): lag slices of about 0.5 s (census + economy); plan days of about 0.5 s (town-hall slot searches with stilts, conversions); a 910 ms tier step (now labelled in the log).
- The saved town is still about 2 MB after the diet: knows 160 K, buildings 83 K, streets 30 K. Consider per-section saves (only changed parts).

- Castles in the clock (castlegen: the lord's castle at town III, the grand castle-palace at city III), with the water laws.
- Hillside houses: SF-style walk-out cellars on podium / embankment lots (windows and a door in the exposed cellar face).
- Atlanta canopy: planted street and lane trees; clearing kept to the plot box.
- Stair streets between stacked lanes; lanes at other levels.
- Lane planner: depart from released windows and lane ends, not only dead ends.
- The outfall survey's own cost (one candidate can take 1.4 s): make planOutfall2 a job.
- The pw:giant_rat_wa and pw:hedgehog_wa double navigation (his content log, again).
- His content log also shows `wolf_sitting` and `ground` animation errors (RP-07). Investigate.
