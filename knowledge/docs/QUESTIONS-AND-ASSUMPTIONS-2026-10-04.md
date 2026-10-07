# CIVITAS — open questions and the answers I assumed (D-C554)

Abs0lum's rule (03:23, 10-04): if he is asleep, I assume an answer and keep working, and every question is kept here for
him to confirm or change later. Each entry has: the question (copy-paste ready), the ANSWER I ASSUMED and built on, what
changes if he answers otherwise, and its status.

Status: OPEN = assumed, waiting for him · CONFIRMED · CHANGED (his answer differed; the rework is noted) ·
RESOLVED-BY-EVIDENCE = a question of FACT settled by a test or measurement (his 03:26: answer it firmly and grow from it); the
evidence is quoted. Questions of taste or design stay his: assumed and OPEN.

---

## Q1 — the clipping trapdoor/ladder (his 22:08 witness)
```
Q1: Which screenshot showed the trapdoor/ladder clipping — the sewer hatch on a house's access shaft, a street manhole, or the well? (A picture number or a description is enough.)
```
- ASSUMED: the house's sewer-access hatch, where the hatch's open position overlaps the ladder below it. Not changed
  blind: I'll look into it once I know which hatch it was. The report is taken as true (the witness rule).
- IF OTHERWISE: the fix moves to that structure (the manhole cover or the well).
- STATUS: OPEN

## Q2 — road grades (R5 research vs our ramps)
```
Q2: Historic cart roads climb at most about 1 in 17; our streets climb 1 in 7 and the narrow roads between settlements 1 in 4 (your 4-part ramp). Keep both as they are, or add a gentler "cart road" class for the main road between towns?
```
- ASSUMED: keep 1-in-7 streets and 1-in-4 narrow roads (your ruling); no cart-road class yet.
- IF OTHERWISE: a third road class (1 in 12–17, longer switchbacks) for the roads between settlements.
- STATUS: OPEN

## Q3 — narrow lanes and alleys (R5)
```
Q3: Medieval towns had 5-block side lanes and 2–3-block alleys besides full streets. Do you want those lane/alley classes (with the stair alleys of the stepped town, B3), or only full 13-wide streets plus stairs?
```
- ASSUMED: yes, as part of B3 (stepped town: stair alleys between terraces), after the current program.
- STATUS: OPEN

## Q4 — mob pass G: tiny giants
```
Q4: Some "giant" mobs are based on true-scale small animals (a scorpion is 8 cm), so 2.5x the base makes a "giant scorpion" only 20 cm tall. Keep the rule literal (2.5x, even if still small), or give giants a minimum size?
```
- ASSUMED: literal 2.5x (it matches "I don't want a tiny scorpion to murder me"); giant damage = the base's + 2, and a
  giant smaller than you also gets the small-hostile limits (at most 1 heart, half the attack rate).
- IF OTHERWISE: a minimum giant height (for example 1 block).
- STATUS: OPEN (the full before/after table goes to you before anything ships)

## Q5 — the giant squid without a base
```
Q5: pw:giant_squid_wwa has no smaller version in our packs. Size it at 2.5x the vanilla squid (about 2.4 blocks), or leave it as it is?
```
- ASSUMED: leave it as it is for now and list it in the table.
- STATUS: OPEN

## Q6 — block hardness by tool tier (his 22:50)
```
Q6: You asked to verify or add the hardness scale (weaker tools break certain blocks more slowly) "if it's not already incorporated". It is not in the current packs. Build it after this program as its own pass?
```
- ASSUMED: yes, its own pass after this delivery (it needs your list of block families and tool tiers).
- STATUS: OPEN

## Q7 — where the sewers drain (A0.2)
```
Q7: When both a river (farther away) and a hillside (closer) could take a sewer's water, should it run to the river (the medieval way) or out of the nearest hillside?
```
- ASSUMED: the river (or lake / sea) first, if it lies within 120 blocks; otherwise the nearest hillside within 72;
  otherwise a soakaway pit under the sewer's lowest point.
- STATUS: OPEN

## Q8 — sewer trunks under open ground
```
Q8: Where a sewer trunk runs under open ground (no street above), should it get a manhole cover in the grass every 26 blocks (locked like the street manholes)?
```
- ASSUMED: yes (D-C549), with a light inside the trunk every 12 blocks so nothing spawns there.
- STATUS: OPEN

## Q9 — quarter hearts (research answer given 03:15)
```
Q9: Do you want a custom heart bar with quarter hearts (each player sees their own; mobs could show one too)? It means hiding the vanilla hearts, and the HUD files are the part of a pack most likely to break when Minecraft updates.
```
- ASSUMED: not now; damage keeps half-heart steps (the scaling doesn't need the HUD).
- STATUS: OPEN

## Q10 — vines that sway
```
Q10: Vines that move out of the way when you walk through them (your 22:08 "sways out of the way"): the plan is a short bend of the vine (about half a second) while a player passes through it. Build it as its own small pass right after this program, or later?
```
- ASSUMED: backlog (B-VINE-SWAY), its own pass after this program.
- STATUS: RETIRED by his 17:38 ruling ("get rid of the quick vine shake when the character runs into it, but keep the gentle sway") — the touch rustle is off in BP-02 1.3.220; the wind sway stays

## RESOLVED BY EVIDENCE (facts settled by tests; no answer needed from him)
- E1 · Does water flow through an iron-bars grate? NO for a plain grate: the water stops at it (server test, runs 0.0.19–0.0.21).
  YES for a WATERLOGGED grate: 9 of 10 carved outfalls spilled past it. The outfalls waterlog their grates. (RESULTS R-1)
- E2 · Is the street planner's speed-up safe? YES: the faster planProfile gives identical plans to the old one on 183
  random streets over real terrain from run 0.0.19, and runs 2.35x faster under Node (test_profile_speed.mjs). (RESULTS R-4)
- E3 · Why did the towns stop at ~20 plots? The side-street search never got past its first try: its resume point
  forgot which of the three street lengths it was on, and one try takes longer than the time it is given, so every
  call repeated the same try. Found in the code and confirmed by the log timings (140 tries, all 200-280 ms, never a
  finished scan). Fixed for build 25. (RESULTS R-22)
- E4 · Are the stuck villagers walled in? NO: by vanilla-like walking rules, 25 of 26 places where villagers gave up
  are joined to the square on foot (51,415 joined standing places in run 0.0.24's dump). The fault is in how they
  are guided, not in the town. A walk instrument is built to show the mechanism. (RESULTS R-25)
- E5 · Are the bench roads' ramps wrong ("rampBad" in every run)? NO: the dump shows road 1 falling 95.0 → 94.75 →
  94.5 → 94.25 → 94.0 → … → 92.25 → 92.0, a quarter block per cell with no step — the probe expected the quarters one
  cell later. A probe expectation, not a road fault.
- E6 · Why did villagers get stuck walking? They followed each other's guide entities: the follow behaviour accepted
  any guide within 48 blocks. Giving each walker its own numbered guide took the town I count from a handful arrived
  and dozens stuck to 224 arrived / 25 stuck (run 0.0.25b). (RESULTS R-31)
- E7 · Why did the latrine, bathhouse and infirmary never get built? A civic work that found no room when its tier
  came was written to a waiting list that nothing ever read again. Fixed for build 25d. (RESULTS R-36)
- E8 · Why did a new village on a cramped site never get built? Its two founders could build at most 80 blocks a
  day and the day's allowance never carried over, so any stage bigger than 80 blocks waited forever (and without a
  finished house nobody moved in to help). Fixed for build 25f: big stages are worked off over several days. (RESULTS R-41)
- E9 · Why did the shop counters stay empty? The morning stocking tested a "days are being skipped" flag that is only
  refreshed while the clock runs; with the clock paused after a skip it stayed on and the counters were never filled.
  Fixed for build 25j. (RESULTS R-49)

## Q11 — low points in the middle of a street
```
Q11: Where a street dips (a low point in its middle, not at an end), should its sewer drain into a soakaway pit under the street, or should a trunk run out sideways beneath the houses to a hillside or river?
```
- ASSUMED: a soakaway pit under the street. Trunks only leave from dead ends, so the house frontage stays free (a trunk
  under the houses would cut their cellars, which are 15 deep).
- STATUS: OPEN

## Q12 — buildings we don't have yet (civic works, palaces)
```
Q12: The civic works (latrine, cistern, bathhouse, infirmary, hospital, waterworks) and the palace/manor program need buildings we don't have. For now each work uses a stand-in (a small cottage as the latrine, a well as the cistern, a large cottage as the infirmary, a town hall as the hospital). Where should the real ones come from: Medievalism v7's structures, new designs we make together, or something else?
```
- ASSUMED: stand-ins now (they work like the real thing: nobody lives in them, the healer staffs the infirmary), real
  designs in a later building pass. The palace program (D) waits for that pass.
- STATUS: OPEN

## Q13 — the greenbelt
```
Q13: Once a city has its wall, a ring 24 blocks wide outside it stays unbuilt (a greenbelt; benches keep building). Is 24 right, and should farms be allowed in the greenbelt (medieval towns farmed right up to the walls)?
```
- ASSUMED: 24, nothing built in it (farms included) for now.
- STATUS: OPEN

## Q14 — what the watch does to monsters
```
Q14: The watch strikes monsters within 3 blocks (6 damage every second) and chases them within 16 above ground; it wears a light resistance effect on duty. Is that the feel you want, or should the watch only drive monsters off (no kills) / ring a bell for help?
```
- ASSUMED: strikes and chases (monsters only — Utopia-First).
- STATUS: OPEN

## Q15 — when a villager dies in the census
```
Q15: When someone dies of old age in the census, their villager now quietly leaves the world (no death animation, no drops). Do you want a visible end instead (a funeral walk to a graveyard plot, a grave marker), now or later?
```
- ASSUMED: quiet removal now; a graveyard and funerals are a nice later addition (they'd feed the story phase).
- STATUS: OPEN

## Q16 — the manor house (phase D, first piece)
```
Q16: The manor house for town II (MANOR-RENDER / MANOR-PLANS images): stone ground floor, oak upper storey on spruce posts, a big spruce hipped roof, three chimneys; parlour - entrance hall - dining hall in front, a hidden service corridor with jib doors and a green baize door, the back range (kitchen, back stair, steward's office, pantry), chambers upstairs, servants' garrets in the roof. 20 deep x 21 wide (R3's 56 x 44 doesn't fit between two parallel streets). Keep this look, or change it (wings, a porch, a different roof, another palette, bigger)?
```
- ASSUMED: keep it for this delivery; the city and metropolis palaces (R3's 128 x 128 and 256 x 192) need a whole grid
  block of their own and wait for your review of this one.
- STATUS: OPEN

## Q17 — a quarry that is worked out
```
Q17: A quarry now digs at most six pits around itself (behind, beside, further behind); when all six are spent it is "worked out": it stops giving stone, and the town's stone shortage charters a new quarry elsewhere the normal way. The old pits re-green. Should a worked-out quarry instead become something — flooded into a pond, turned into a garden or a lime kiln yard — or stay a green hollow?
```
- ASSUMED: a green hollow (the re-greening that already runs); a pond or garden is a later stewardship item.
- STATUS: OPEN

## Q18 — how many villagers you see walking
```
Q18: Until now only people with a post (watch, sewer keeper, surveyor, builders), shopkeepers and newcomers had bodies; children born in the town and most family members existed only in the census. Now each household also gets a body for its shopper (up to 48 bodies per town). Should EVERY grown person have a body (a busier town, more load on the PS5), or keep this "one walker per household plus the posts" rule?
```
- ASSUMED: one shopper per household plus the posts and the shops (the cap of 48 kept).
- STATUS: OPEN

## CARRIED FROM EARLIER ROUNDS (added 11:2x CT 10-04 at his request: "deliver all unanswered questions")
Renumbered Q19–Q31 so one list holds every open question; the original ids are kept in brackets.
Trees: REVIEW-WEEK-2026-10-03 §5 / HANDOFF-2026-10-03-REVIEW-WINDOW-CLOSE §5 (its question 5, the oak wall recipe,
was answered at 12:21 on 10-03: Option A). City plan: CIVITAS-CITY-PLANNING-DESIGN §9. For each one the current
packs simply keep today's behaviour until he answers.

## Q19 — vanilla trees the engine places itself [review-week 1]
```
Q19: Some biomes grow vanilla trees from engine code that our tree rules cannot reach: grove and snowy peaks, mangrove swamp, swamp, old-growth giant taiga, savanna acacias, flower-forest oaks and fallen trunks. Accept them as they are, convert them with a scripted sweep as chunks load (costs script time), or do nothing for now?
```
- ASSUMED: accept / nothing (today's state).
- MEASURED 10-04 14:3x (server census, one sample per biome): vanilla trees remain in the mangrove swamp (10,247 vanilla
  leaves), grove (3,506), swamp (1,735 — oaks with vines, beside 382 of ours) and old-growth pine taiga (989, beside 947 of
  ours); none in forest, birch, taiga, dark forest, savanna, jungle, flower forest, windswept forest, snowy taiga, snowy slopes,
  meadow, plains. Their vanilla leaves wear RP-05's broken textures (AUDIT-TREES-LEAVES-2026-10-04 §5) — the 10-04 'leaves
  don't work' sighting. Proposal: fix the vanilla leaf textures first (RP-05 1.3.59), then decide this.
- STATUS: OPEN

## Q20 — swamp oaks [review-week 2]
```
Q20: Swamp oaks: keep the vanilla ones (with their vines), or convert them to our trees?
```
- ASSUMED: keep vanilla.
- NOTE 10-04: the swamp oaks are placed by the engine (no rule to override); they are what he saw as 'a faulty oak' beside
  ours. Keeping them means fixing their leaf textures (RP-05 1.3.59); converting them needs a scripted sweep (Q19 b).
- STATUS: OPEN

## Q21 — distance between a town and its daughter [review-week 3]
```
Q21: A town's daughter settlement is founded 170–230 blocks away; your earlier ruling said 120–200. Below about 170 the two founding sites (160 x 160 each) overlap: in run 0.0.11 their streets interleaved and the daughter's wall hit the mother town. Keep 170–230, or shrink the founding site so 120–200 works?
```
- ASSUMED: 170–230 (the shipped value, DAUGHTER_DIST).
- STATUS: OPEN

## Q22 — forest density [review-week 4]
```
Q22: Forest densities follow a Java-like assumption. Keep them? (Read with Q24: today's forests hold about half of what the rules ask for.)
```
- ASSUMED: keep.
- STATUS: OPEN

## Q23 — trees in the grove, snowy slopes and peaks [review-week 6a]
```
Q23: The grove, snowy slopes and alpine peaks have no tree rule of ours. Add one (and keep or convert the grove's own spruces, see Q19)?
```
- ASSUMED: no new rule.
- STATUS: OPEN

## Q24 — the forest-density fix [review-week 6b]
```
Q24: A grass tuft, fern, flower or thin snow layer on the chosen spot makes a tree refuse to grow, so today's forests are about half as dense as the rules ask (cold forests most). A held fix (a 2-block search before each tree) took a test area from 48 to 91 trees. Take it? It would be rebuilt on the current BP-02 as 1.3.220 and measured again, because the trees were resized in 1.3.218.
```
- ASSUMED: hold (today's density).
- STATUS: OPEN (the held build 1.3.215 was made on 1.3.214; its number is never reused)

## Q25 — stray lights already in your world [review-week 7]
```
Q25: Every mob light (blaze, magma cube, glow squid; packs 1.3.194–1.3.212) and every golden-crown light placed before the 1.3.214 fix is still in your world, invisible, with no record left to find it. Add a command that clears light blocks of our four levels (6, 10, 13, 14) within a radius around you, run only when you ask? It would also remove light blocks of those levels that you placed yourself.
```
- ASSUMED: no command yet.
- STATUS: OPEN

## Q26 — trees standing in another tree's crown [review-week 8]
```
Q26: About 1 % of our trees (about 3 % in dense oak forest) stand in another tree's crown. No rule-level fix works (three were measured and rejected). When the lower tree is felled, by you or now by a town's woodcutter, the upper one is left hanging. Options: (a) a check while you play that removes any tree standing on leaves (it removes trees from your world), (b) a design job: a ground test before each tree, like vanilla's "may grow on" list, or (c) accept.
```
- ASSUMED: (c) accept for now (today's state).
- STATUS: OPEN

## Q27 — sewer lighting [city plan S1]
```
Q27: The sewers are lit: a lantern in a wall niche every 12 blocks in the sewer hall, the utility gallery and the trunks, so nothing spawns below and the watch patrols an empty sewer. Keep them lit, or leave them dark so monsters spawn there and the watch has work below?
```
- ASSUMED: lit (built; follows the D-C538 patrols ruling).
- STATUS: OPEN

## Q28 — the stand-in grate [city plan S2]
```
Q28: Until your grate design exists, each sewer exit has waterlogged iron bars as a stand-in (tested: the water flows through them). Iron bars OK, leave the opening empty, or another block?
```
- ASSUMED: waterlogged iron bars (E1).
- STATUS: OPEN

## Q29 — block size between parallel streets [city plan C2]
```
Q29: Parallel streets are 56 blocks apart (centre to centre), which makes city blocks about 43 x 47, the size of real medieval blocks. It was 70 at first, but at 70 most new side streets were too short to get a second junction, so the city blocks never closed. Keep 56, or another number?
```
- ASSUMED: 56 (the shipped GRID_PITCH; the design's first assumption was 60).
- STATUS: OPEN

## Q30 — width of the narrow roads [city plan A4]
```
Q30: The narrow roads (between settlements, and up to the benches on a hill) are 7 wide: a curb, 5 of road, a curb, with no sidewalks or sewer. Keep 7, or another width? (Q2 asks about their slope.)
```
- ASSUMED: 7.
- STATUS: OPEN

## Q31 — the regional look [city plan A8]
```
Q31: Planned (not built yet): each building comes in palette versions (timber, stone, plank...) and a settlement builds the cheapest one with the materials it has delivered, so mountain villages turn stone because stone is cheap there. Is that the rule, or should a fixed biome rule decide the look?
```
- ASSUMED: by delivered cost (not built yet; nothing in the packs depends on it).
- STATUS: OPEN

## Q32 — the manhole's lift [19:06 ruling]
```
Q32: Manhole cover built as you said: closed stays flush; on opening the plate lifts first, then slides over; closing slides back, then drops. I read "raises 1 cube" as 1 px (one sixteenth of a block). Did you mean 1 px, or a bigger lift?
```
- ASSUMED: 1 px (Markers RP 0.2.3 / BP 0.2.4).
- STATUS: ANSWERED a (1 px) — his 08:43 CT 10-05

## Q33 — ramp collision "4 horizontal for every 1 vertical" [18:23]
```
Q33: A custom block in Bedrock carries exactly ONE collision box (an engine limit), so a ramp cannot be built from several thin steps inside one block. Our 1-in-4 ramps (q1..q4) already rise one block over four blocks in 4-px steps, the finest step a 1-in-4 slope can have. Did you mean (a) finer steps inside each block (not possible), (b) a gentler ramp family, 1 in 8, with 2-px steps (new blocks + longer kit pieces), or (c) something else — a screenshot of the ramp you walked would settle it?
```
- ASSUMED: nothing changed this round.
- STATUS: ANSWERED a (fine as built) — his 08:43 CT 10-05

## Q34 — the well over the water [17:38]
```
Q34: The well template's shaft is water-filled from its bottom up to the square's surface (the water sits inside the stone ring at ground level; the wellhead stands on the square). When you say it "sits above the water instead of on it", is the water further down than the ring, or is the whole well standing higher than the ground around it? A screenshot looking down into the well and one from the side would let me match it to the template.
```
- ASSUMED: nothing changed this round.
- STATUS: OPEN — his 08:43 CT 10-05: he believes well screenshots were uploaded earlier and will double-check

## Q35 — the inner-crown look variants (R-55)
```
Q35: 0.7 % of the leaves in the acacia, cherry, mangrove and elder templates (the rescaled / square-trunk sets) touch a trunk but wear a "far" look variant instead of the inner-crown one. A small re-bake pass would fix it (only the look of leaves next to the trunk changes). Run it next round, or leave it?
```
- ASSUMED: leave it (not a visible defect at distance).
- STATUS: ANSWERED b (run the R-55 re-bake next round) — his 08:43 CT 10-05

---
REMINDER (DEFERRAL-N1, his 02:53): abandoned homes, lost assets and the aftermath of unrest are kept for when crime,
discontent and story-driven growth are actively worked on (after you have watched the Utopia-First run).
