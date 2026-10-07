# HANDOFF — 2026-10-05 — ROUND 1005c: HIS 16:50 REPORT (the crash, the palace finder, paintings + wand, villagers at work, birch trunks, terracing)

Authoritative CURRENT-STATE (newest handoff). Supersedes HANDOFF-2026-10-05-ROUND-1005-PALACE-GALLERY for ship status;
everything in that handoff stays in force (its packs are the base of these builds).

## 1. INSTALL SET (Drive: My Drive/ClaudeUploads — md5 in §6)

| pack | version | what changed | needs |
|---|---|---|---|
| BP-02 AbsolutRealism Tectonic BP | **1.3.224** (replaces 1.3.222 / 1.3.223) | everything in §2 | RP-01 1.3.124, RP-12 1.0.1 |
| RP-01 AbsolutRealism Tectonic RP | **1.3.124** (replaces 1.3.123) | the 72 birch falling-tree copies match the shortened trunk | — |
| RP-12 AbsolutRealism Gallery RP | **1.0.1** (replaces 1.0.0) | paintings face the room, flush to the wall; Curator's Wand + Framed Painting icons and names; the "Talk" button label | — |
| RP-12 Gallery LITE | 1.0.1 (only if the phone struggles; never both) | the same at 128 px per block | — |
| Markers BP 0.2.4 / RP 0.2.3, RP-05 1.3.59, TestRunner BP 0.5.24 | unchanged | | |

Delete from Drive: BP-02 1.3.222 and 1.3.223, RP-01 1.3.123, RP-12 1.0.0 (+LITE), and the two RP-08-…-Gallery files.

## 2. WHAT'S NEW (his 16:50 report, his answers 17:2x: step-else-stilts · broad market · wand drops a framed painting · one build)

### 2.1 The crash past City II — fixed at the cause
- His screenshot: `[Watchdog] Unhandled critical exception of type 'Hang' in behavior pack 'AbsolutRealism Tectonic BP
  v1.3.222'` + `High memory usage detected`. The game stops a pack whose script runs more than ~10 s in one tick.
- Cause: a tier-up laid ALL its plots in one tick (City II = 6–8 s on our PC test server; City III would pass 10 s on any
  device); the palace pumps did ~1 M blocks of /fill in one step and every skipped day started another; a lag "slice" ran
  up to 3 days at once in the same tick as the clock's main beat; the whole state was saved on every beat.
- Now: a tier-up writes a CHARTER and the surveyors lay it out ONE PLOT PER BEAT (a grow answers at once; "still laying out"
  if you grow again before it finishes; status shows "laying out CITY III: 12/41 plots"); a skipped day runs every 10 ticks
  (a skip of 100 days takes ~50 s); one day per call; the state is saved at most every 5 s; the pumps run one job per palace,
  one /fill per tick, never on skipped days, and stop after three dry passes; pictures hang 8 at a time; the palace survey
  measures 2 sites a day; caches are capped; at most two street searches run at once.
- Our test server now runs with a 3-second hang limit (stricter than your device) and the gate climbs past City II to
  CITY III and METROPOLIS. Result: §3.

### 2.2 The palace finder
- When the palace is laid out, everyone gets a chat line: "the Seat of Government is laid out — the palace block's centre is
  at X Y Z, N blocks <direction> of the square. It rises over the next weeks."
- `/scriptevent pw:clock status` → right under your settlement's line: `PALACE: centre X Y Z (N blocks south-east of the
  square) · plot` (or, while the surveyors search: days, sites measured, the best so far).
- What you'll see at first: the plot stage is ground work only (a levelled 128 × 128 block); the four quarters rise in
  lockstep over ~28 village days (6 + 8 + 8 + 6).

### 2.3 Paintings face the room, flush (RP-12 1.0.1) + the Curator's Wand
- Mechanism: the game draws an entity model turned 180° at yaw 0; the frame models assumed it wasn't — the picture slab sat
  on the room side of its block with its painted face toward the wall (0.94 block of gap: you could stand in it). Fixed in the
  resource pack: paintings already hanging in your world fix themselves when you install RP-12 1.0.1.
- **Curator's Wand** (crafting table: a gold ingot diagonally above a stick — or `/give @s pw:curators_wand`): HIT a painting
  (or use the wand on it) → it comes off the wall and drops a **Framed Painting** (the same work; its title and artist in the
  item's description).
- **Framed Painting**: hold it and use it on the SIDE of a solid block → the work hangs there, facing out of that wall
  (floors and ceilings refuse). The item is used up; the Connoisseur's Book still reads it.

### 2.4 Villagers at work, selling for gold coins
- Why they stood at the well: the "go to the square" goal was a single point 6½ blocks into the square — inside the well —
  for everyone without a job site in work hours and for EVERYONE at dusk.
- Now: each person has its own cell on a ring around the square (33 cells, clear of the well and the stall), and through the
  day they rotate between their yard, their ring cell, their neighbourhood centre, shop fronts — and the inn at dusk. Rain
  sends anyone without indoor work home.
- **The market clerk**: every settlement's square gets a stall (two barrels, a lantern post) at its corner and a MARKET CLERK
  on duty in work hours (game time 1000–11000). Talk to the clerk ("Talk" button / use): SELL anything on the broad list
  (all logs incl. our tree logs, planks, stone kinds, wheat / carrots / potatoes / beetroot / hay, bread, raw and cooked meat
  and fish, leather, wool, iron, bone / bone meal, glass, sand, iron tools; and for coin only: gold ingots / nuggets / raw gold,
  diamonds, coal, copper, lapis, redstone, quartz, amethyst, string, feathers, eggs, honeycomb, ink, apples, melons, pumpkins,
  sugar cane, berries) — one button per kind you carry, the whole amount at once, paid in gold coins from the town's
  treasury; BUY what the town has in stock.
  - Prices: the market pays 60 % of the town's live price; a shop pays 75 % for its own goods. A stack of 64 oak logs =
    38 coins at the market, 48 at the lumberyard. A diamond = 40 coins, a gold ingot = 8.
- Shop keepers: a failed hire is retried every minute; keepers stand at their counters in work hours (their window: buy +
  sell) and go up to their rooms after hours. **Selling to a shop paid 12× too much before (pennies paid as coins) — fixed.**
- Every civ now shows a "Talk" button (phones / consoles needed an interaction to send the tap at all).

### 2.5 Birch trunks end at the crown (his 16:50)
- The trunk now ends ONE block into the bottom of the crown (it ran to the top; old birches even had a dead tip at the top
  row). The crowns themselves are unchanged (same shapes); the hidden trunk column inside the crown is leaves.
- The leaf-strip rule changed with it: leaves turn to litter only when their WHOLE cluster no longer touches a log (the old
  6-step rule already stripped ~18 % of an old birch whenever a log nearby was cut — the "bare pole").
- New trees only: birches already standing in explored chunks keep their old trunks.

### 2.6 Terracing — build up only over 15, else follow the land, else stilts
- Research basis (R5 + R1 §4): retaining walls 3–4 high at most; taller retention in LIFTS with setbacks; streets follow the
  contours; per-house: small drops make a podium, larger ones stepped terraces.
- Rules now in the code:
  1. Ground is built up under a plot only where the WORST column drops 15 or less, and the fill steps DOWN outward in lifts
     of 3 (grass top, a cobblestone face, dirt below) — no more single 15–40-block faces.
  2. A street is judged by its WORST column (it was the median: ridges with 20–40-block edges passed). No street,
     embankment or dry-land bridge pier over a drop of more than 15; the street's downhill edge is one lift of stone brick
     over a stepped embankment.
  3. Beyond 15, the plot slides along its street and tries the other streets ("step"); only when nothing fits anywhere may it
     stand on stilts, over a drop of 24 at most (your answer: step, else stilts).
  4. Ground that cannot be read (unloaded) is never accepted (the cliff-edge houses came through that hole) — the plot waits.
  5. Parallel streets try 8 spacings (was 3) to find their own contour; climbing legs name their first blocked cell.
- Known limit: the founding main street may relax rule 2 once if no side of the square allows it (a settlement must stand);
  the palace's margin ring is not yet stepped (backlog).

## 3. VERIFICATION
Gate 224-2 (our test server, the harness's mountain-lake site, **script hang limit set to 3 s** — stricter than your device's 10 s):
- **No Hang anywhere in BP-02**, no "High memory usage" line, from founding through village I–III, town I–III, city I–II
  (the palace), **CITY III and METROPOLIS I** (grow + skip 24 each). Worst single tick: 1,003 ms (one palace-survey day at
  City II); typical slow lines 300–800 ms (a day's step while skipping). Before: 6–8 s in one tick at City II.
- A grow is now laid out over beats: CITY III took 45 s of real time, the following skip 24 took 37 s.
- Palace laid at day ~197, the four quarters furnished in lockstep, the block DRY (1 water cell in 31,744 samples).
- Villagers (work hours and dusk): **0 of 36 within 4 blocks of the well**, 36 villagers on 36 different cells; the Market
  Clerk 1.8 blocks from the stall in work hours, lodged 67 blocks away at dusk; the stall built (barrels + lantern); 14 keepers.
- Gallery: pictures hang 8 at a time (84 in the town at check time; the palace's continue on the sweep).
- Note: the harness site is a full basin — every tier after city added only 1 plot (landRejects ~7,000, mostly 'plot' and
  'road' overlaps): growth past city on cramped land is the next round's main problem (with the water programme).
- Run 224-1 found a 3-second hang in OUR TEST PACK's world dump (fixed in probe 0.0.34), not in BP-02.

## 4. YOUR Use a NEW world for tests 1–4 (birches and towns are made when chunks/towns are first built); your current world is fine
for test 5 (paintings already hanging fix themselves).

**Before you start (once):** on Drive (My Drive → ClaudeUploads) download BP-02 1.3.224, RP-01 1.3.124 and RP-12 1.0.1
(not LITE unless the phone struggles). Open each file → Minecraft imports it. In the world's settings → Behavior Packs: remove
BP-02 1.3.222/1.3.223 and activate 1.3.224; Resource Packs: swap RP-01 to 1.3.124 and RP-12 to 1.0.1. The content log must
show `[PW-VERSION] BP-02 v1.3.224`.

1. **No crash past City II.**
   - Found a village (`/scriptevent pw:clock village`), then alternate `/scriptevent pw:clock grow` and
     `/scriptevent pw:clock skip 24` up to CITY III and METROPOLIS.
   - Expect: after a grow, chat says "… (N plots being laid out)"; a second grow too soon answers "still laying out … (12/41
     plots)"; a skip of 24 days takes about 12 seconds of real time. No "Watchdog … Hang" line; the game never closes.
   - Tell me: the largest "slow: … took N ms" you see in the content log, and the tier you reached.
2. **The palace.** At CITY II watch chat for "the Seat of Government is laid out — … centre is at X Y Z, … of the square";
   `/scriptevent pw:clock status` shows a PALACE line under your settlement. Fly to the centre: a levelled 128 × 128 block
   that rises in stages. Tell me what you see there after another `skip 24`.
3. **Villagers and the market.**
   - At midday (`/time set 3000`), stand on the square: a stall (two barrels, a lantern post) at one corner with
     "<name> the Market Clerk" behind it. Tap / use the clerk → the market window.
   - Sell: carry a stack of logs and some cobblestone; each kind is one button ("Sell 64 oak log — 38 coins"). Coins appear in
     your inventory. Buy something back.
   - Shops: visit a bakery / butcher / smithy in work hours — the keeper stands at the counter; their window sells and buys.
   - Spread: count how many villagers stand at the well vs elsewhere at midday and at dusk (`/time set 11500`). In rain they
     should head indoors.
   - Tell me if any civ shows no "Talk" button, or a clerk/keeper is missing.
4. **Birches.** In a birch forest of the new world, look up into a few trees (young, tall, old): the white trunk should stop
   about one block into the bottom of the crown. Cut a log of a nearby tree: the birch's leaves must NOT turn to litter.
   Fell a birch: the falling copy shows the short trunk.
5. **Paintings + wand.**
   - In any finished building: the pictures face the room and sit flat on the wall (no gap to stand in). Please take one
     straight-on screenshot of a picture on a north–south wall (one that faces east or west) and one on an east–west wall —
     that settles a rule for entity models (LC-1005-20).
   - Craft the Curator's Wand (a gold ingot diagonally above a stick) or `/give @s pw:curators_wand`. Hit a painting → it
     drops a Framed Painting (its title in the item text). Use the Framed Painting on the side of a wall → it hangs there,
     facing you. A floor or ceiling refuses.
6. **Terracing.** Found a village on hilly ground and grow to TOWN III. Expect: no house or street on a wall of more than ~15
   blocks; slopes below houses and streets step down in 3-block lifts with grass tops; a few houses on stilts only where
   nothing else fit. Screenshots of the steepest spot, please. (one world, these packs; your eyes rule)
Use a NEW world for tests 1–4 (birches and towns are made when chunks/towns are first built); your current world is fine
for test 5 (paintings already hanging fix themselves).

**Before you start (once):** on Drive (My Drive → ClaudeUploads) download BP-02 1.3.224, RP-01 1.3.124 and RP-12 1.0.1
(not LITE unless the phone struggles). Open each file → Minecraft imports it. In the world's settings → Behavior Packs: remove
BP-02 1.3.222/1.3.223 and activate 1.3.224; Resource Packs: swap RP-01 to 1.3.124 and RP-12 to 1.0.1. The content log must
show `[PW-VERSION] BP-02 v1.3.224`.

1. **No crash past City II.**
   - Found a village (`/scriptevent pw:clock village`), then alternate `/scriptevent pw:clock grow` and
     `/scriptevent pw:clock skip 24` up to CITY III and METROPOLIS.
   - Expect: after a grow, chat says "… (N plots being laid out)"; a second grow too soon answers "still laying out … (12/41
     plots)"; a skip of 24 days takes about 12 seconds of real time. No "Watchdog … Hang" line; the game never closes.
   - Tell me: the largest "slow: … took N ms" you see in the content log, and the tier you reached.
2. **The palace.** At CITY II watch chat for "the Seat of Government is laid out — … centre is at X Y Z, … of the square";
   `/scriptevent pw:clock status` shows a PALACE line under your settlement. Fly to the centre: a levelled 128 × 128 block
   that rises in stages. Tell me what you see there after another `skip 24`.
3. **Villagers and the market.**
   - At midday (`/time set 3000`), stand on the square: a stall (two barrels, a lantern post) at one corner with
     "<name> the Market Clerk" behind it. Tap / use the clerk → the market window.
   - Sell: carry a stack of logs and some cobblestone; each kind is one button ("Sell 64 oak log — 38 coins"). Coins appear in
     your inventory. Buy something back.
   - Shops: visit a bakery / butcher / smithy in work hours — the keeper stands at the counter; their window sells and buys.
   - Spread: count how many villagers stand at the well vs elsewhere at midday and at dusk (`/time set 11500`). In rain they
     should head indoors.
   - Tell me if any civ shows no "Talk" button, or a clerk/keeper is missing.
4. **Birches.** In a birch forest of the new world, look up into a few trees (young, tall, old): the white trunk should stop
   about one block into the bottom of the crown. Cut a log of a nearby tree: the birch's leaves must NOT turn to litter.
   Fell a birch: the falling copy shows the short trunk.
5. **Paintings + wand.**
   - In any finished building: the pictures face the room and sit flat on the wall (no gap to stand in). Please take one
     straight-on screenshot of a picture on a north–south wall (one that faces east or west) and one on an east–west wall —
     that settles a rule for entity models (LC-1005-20).
   - Craft the Curator's Wand (a gold ingot diagonally above a stick) or `/give @s pw:curators_wand`. Hit a painting → it
     drops a Framed Painting (its title in the item text). Use the Framed Painting on the side of a wall → it hangs there,
     facing you. A floor or ceiling refuses.
6. **Terracing.** Found a village on hilly ground and grow to TOWN III. Expect: no house or street on a wall of more than ~15
   blocks; slopes below houses and streets step down in 3-block lifts with grass tops; a few houses on stilts only where
   nothing else fit. Screenshots of the steepest spot, please.

## 5. BACKLOG (new this round)
- The palace margin ring: stepped lifts like the houses (M). Periodic leaf-decay sweep: switch to the cluster rule before it is
  ever re-enabled (S). Other species: do oak / spruce / jungle show the trunk through the crown too? (ask). pw:giant_rat_wa has
  two navigation components (his log line 77) (S). Contour streets proper (multi-segment kit streets on walkContour) (L).
- Still open from 1005: the water programme (cascades, sewer entrances, drains under every structure); castles v0.2 in game.

## 6. FILES (md5)
| file | bytes | md5 |
|---|---|---|
| BP-02-AbsolutRealism-Tectonic-BP-v1_3_224.mcpack | 13,313,520 | 3517811ec00cb66322486b1b8915404e |
| RP-01-AbsolutRealism-Tectonic-RP-v1_3_124.mcpack | 138,766,334 | dd947a3c1ee841c8771c56a9eb2a8173 |
| RP-12-AbsolutRealism-Gallery-RP-v1_0_1.mcpack | 174,493,859 | a593d6afe81f1efe7cdcb18f03fc8e49 |
| RP-12-AbsolutRealism-Gallery-LITE-RP-v1_0_1.mcpack | 55,623,006 | c0af3f71ce370d1893d88d2f9a8733aa |
