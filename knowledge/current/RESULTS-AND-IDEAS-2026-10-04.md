# CIVITAS — what every run taught us, and the ideas it suggests (D-C554)

His 03:23: "We grow as humans based on the knowledge we gain from our failures." Every test run's result, failure or
success, goes here: what happened, the mechanism behind it, what it teaches, and the IDEA it suggests. An idea inside
the approved scope gets built and marked BUILT; anything beyond it is a RECOMMENDATION for him.

---

## R-1 · Water and grates (the bars experiment, runs 0.0.19–0.0.21) — a FAILURE that taught the rule
- WHAT: a water channel with a plain iron-bars block in it: the water stops at the bars (`water, iron_bars, air, air…`).
  The same with a spruce fence. But every carved sewer outfall whose bars were set WATERLOGGED spilled water past the
  grate (9 of 10 exits in 0.0.19: water beyond the grate).
- MECHANISM: on Bedrock, flowing water does not flow INTO bars or fences, but a waterlogged block holds water and
  spreads it to the open side.
- TEACHES: a grate at a sewer mouth must be waterlogged when it is placed; water will never find its way in later.
- IDEA (RECOMMENDATION): any grate or door block you design for the sewers should be waterloggable, and the outfall code
  should waterlog it. Same rule for future fountains, mill races and canal locks.

## R-2 · Every dead end had its own outfall (0.0.19: 13 exits for 7 streets) — a design gap he named (D-C547)
- WHAT: 13 outfall records for 7 streets; street 1 alone had 4, two of them for dead ends that had already been grown
  over (the record was written after the street grew, so it was never cleared); their tunnels stayed open outside the
  new street.
- MECHANISM: the outfall op was queued per dead end and run later; growth removed only the records that existed then.
- TEACHES: a sewer is ONE network with low points, not a set of ends; stale records come from decisions queued behind
  changes that invalidate them.
- IDEA (BUILT in A0.2): one "drain" decision per settlement, re-solved after every change, replacing any pending one;
  exits only at the network's low points (water > hillside > soakaway); redundant tunnels back-filled.

## R-3 · Walking at scale (0.0.21, to city I) — a mixed result, under investigation
- WHAT: by city I: 19 walks arrived, 94 counted stuck, 22 walking, 10 villagers more than 8 blocks from their lead
  (the average distance was 60 blocks, pulled up by a quarryman walking 250 blocks "direct" across country to the
  mother town's quarry near the daughter). In 0.0.19 (town I) it was 9 arrived, 0 stuck.
- MECHANISM (first reading; to be confirmed): (a) routes only follow the walk graph inside a settlement, so a trip
  between settlements, or to a quarry outside the streets, goes "direct" and the vanilla pathfinder gives up;
  (b) villagers inside a plot, behind a fence or below the street level lose the lead when it is 9 blocks above them.
- IDEA: (in scope, C2) the walk graph gains the narrow roads to the quarry/lumberyard and between settlements; a work
  site farther than a day's walk gets its own lodging (a quarry hut) instead of a daily commute; the stuck count is
  split by cause in the status so each cause can be fixed.

## R-4 · Why the runs take so long: the side-street planner held the server (0.0.19 AND 0.0.21) — a FAILURE, now measured
- WHAT: in both runs, 214–218 side-street attempts took 1.2 s each (up to 1.7 s); a carried day ("lag slice") took
  2.5 s on average (up to 3.4 s), 120+ times; the server's other work (walkers, builders) waited during each one.
- MECHANISM: each attempt profiled a 153-cell street at 7 fixed junction heights x 2 grid options = 14 dynamic-programming
  passes per half; the budget check (40 ms) sat only between halves, so one half could never be cut short; and each
  pass re-computed every cell's cost about 60 times (each ramp re-read 7 cells, each dead end 13).
- TEACHES: a time budget only works if it is checked where the time is actually spent; and a "what does it cost here"
  value asked 60 times should be computed once.
- FIX (BUILT for 0.0.22): (1) planProfile builds per-cell cost tables once (identical results on 183 real-terrain
  streets; 2.35x faster in Node, more on the game's slower engine); (2) the side street tries ONE profile at the land's
  own junction height first, and the 14-height loop only when that fails.
- IDEA (RECOMMENDATION): every planner gets a per-call timing line in the status (calls, total ms, worst ms) so a slow one
  shows up in the first run, not after several; and the harness reports the server's ticks per second, which is the
  number you'd feel in-game.

## R-5 · Manholes: 8 laid, 0 standing (0.0.21) — a FAILURE
- WHAT: the probe found smooth stone where each of the 8 covers should be, and no ladders below.
- MECHANISM: when the village became a town, every street piece was laid again at the town width, including the
  access pieces under the manholes; nothing cut the shafts again afterwards.
- TEACHES: anything carved INTO a kit piece after it is placed (manholes, sewer exits, the well drain) has to be
  re-applied whenever that piece is placed again, not only once.
- FIX (BUILT for build 23): a laid manhole is cut again after any piece is placed over it (the sewer exits and the well
  drain already worked this way).
- IDEA (RECOMMENDATION): one "after-placement" registry for every carving, so a new kind of carving can't forget this.

## R-6 · Seven villagers trapped in a hollow beside a sidewalk (0.0.17–0.0.21, the same spot every run) — a FAILURE
- WHAT: a natural hollow 6 deep at x 308–312, z 424–425, right beside the street's sidewalk and cottage #14. Villagers
  stepped off the sidewalk into it and could not climb out; their leads waited 8 blocks above them; dozens of the 295
  stuck walks came from here.
- MECHANISM: the street prep cut hills ABOVE the sidewalk and clad uphill faces, but never touched ground falling away
  BELOW the edge.
- FIX (BUILT for build 22): a guarded downhill edge — a drop of 2–3 is filled level with the sidewalk; a deeper drop (to
  16) gets a stone-brick retaining wall up to the sidewalk with a cobblestone-wall parapet; never across a junction.
- IDEA (RECOMMENDATION): the same guard for the narrow roads' shoulders (the green-corridor fences already do this
  between towns) and for the far face of dead ends that no road continues from.

## R-7 · The daughter town was founded on top of the mother's west bench (every run with benches) — a FAILURE
- WHAT: the daughter's square (138, 293) overlapped the mother's farm #22; the mother's bench households commuted
  ~270 blocks to the quarry and lumberyard each day (the "direct" walks that never arrived).
- MECHANISM: the daughter's bearing was random, at 170–230 blocks from the mother's square; the benches (70–110 out,
  streets up to 100 long) reach just as far.
- FIX (BUILT for build 22): 12 bearings and two distances are searched for land with no other settlement's square,
  street, building or boundary ring within 70; if there is none, the settlers wait and the chronicle says so.
- IDEA (RECOMMENDATION): where the mother's bench and a daughter want the same valley, that is a natural land dispute
  (B4) — a later story hook rather than something the planner silently avoids.

## R-8 · The founders all died together; no child was ever born (0.0.21: 52 people -> 31) — a FAILURE of the model
- WHAT: 24 couples, 0 children; deaths clustered at days 130–168.
- MECHANISM: every founder arrived aged 20–44; births need a free place at home, and homes were always full (each
  household fills its house, and newcomers took every free place that opened).
- FIX (BUILT for build 23; 29/29 node checks): households arrive with two adults (20–59) and children (0–14); a family
  home may be crowded by 2 children; grown children move out to free rooms; newcomers only take a home with two free
  places (one stays for a cradle). Over 600 days in three seeds the town now holds steady at 20–34 people on 28
  places, with 49–59 births, 27–43 moving out, and nobody leaving unhappy.
- IDEA (RECOMMENDATION): crowded homes are a planning signal — the council should order a new cottage when the town is
  crowded rather than only at tier-ups (the C2.4 "council chooses the next work" from D-C550).

## R-9 · Real-time work produced nothing (0.0.21: 2 hands, 0 blocks mined in 200 s; the labour site 0 of 376) — a FAILURE
- WHAT: the quarryman stayed "walking to the face", the woodcutter "idle"; the builders never arrived at site #23.
- MECHANISM (as far as the evidence goes): (a) the quarry face sat below the walk graph and the walk went "direct"
  (fixed in the post-21 source: reachable faces with a standing cell, and walk v2's straight lines off the graph);
  (b) site #23 was on the mother's far west bench, inside the daughter (R-7); (c) only the keeper works a workshop (the
  household's other hands are not yet sent).
- NEXT: build 22's work phase is the check; per-worker detail (state, distance to face, walk mode) added to the status
  for build 23.

## R-10 · Run 0.0.22: the speed fix worked — a SUCCESS, measured
- WHAT: the whole ladder to city I and the bench took 18 minutes (0.0.21: 30). Side-street plans averaged 225 ms
  (was 1,247 ms), a carried day 381 ms (was 2,505 ms), the slowest planner call 683 ms (was 3,447 ms).
- TEACHES: R-4's two fixes (cost tables, one free-height try first) were the bulk of the server's lag.
- IDEA: the same table trick fits the lattice road planner (it re-reads cells per heading); not urgent now.

## R-11 · Manholes now stand after the town-width resurfacing (0.0.22: 8 of 8) — a SUCCESS (R-5's fix confirmed)
- WHAT: cover on the sidewalk, 11 ladder rungs, stone bricks at the sewer floor, on all 8.

## R-12 · Sewer exits v2 on the server (0.0.22) — mostly a SUCCESS
- WHAT: network 1 (4 streets) had 7 low points → 4 hillside trunks + 5 soakaway pits (including the bench's 2);
  3 of the 4 trunk mouths spill water past their grates; every soakaway pit holds water over its gravel. The one dry
  mouth opens onto a stone-brick structure (something else stands right in front of it).
- NEXT (BUILT for 23): low points inside a street (valleys) always drain to a soakaway; trunks never run through house
  frontage (the 16 cells beside a flat stretch).
- IDEA (RECOMMENDATION): a mouth that doesn't spill should be re-surveyed the next day (one more cell, or a turn).

## R-13 · The boundary stones froze growth (0.0.22: 87 plots waiting at city I, 22 placed; 0.0.21 had 29) — a FAILURE
- WHAT: the founding ring had to be 160 wide for the long main street; the tier influences below the city (112–144)
  were all smaller, so the stones never moved between village and town III, and the streets could not grow past them.
- FIX (BUILT for 23): each tier carries the ring at least 32 further out, and a street or side street held back by
  the stones three times makes the council send the surveyor out one more step (16). The ring now follows need.
- TEACHES: a limit that starts out larger than its own schedule silently becomes a ceiling; growth rules should be
  relative ("+N per tier"), not absolute tables.

## R-14 · The keepers left their village (0.0.22: Kari of the quarry, Finn of the farm, in week 2) — a FAILURE
- WHAT: a grain shortage (−30 mood) and having no home in the census (−20) drove the keepers under the leaving mark.
- FIX (BUILT for 23): a keeper lives at the shop (the rooms above the counter).
- IDEA (RECOMMENDATION): a shortage should first raise prices and send the council to the merchant before it moves
  people out; leaving after 10 hungry days is fast for a village where everyone knows everyone.

## R-15 · Real-time work still produced nothing (0.0.22: 1 hand, the quarryman at his station) — a FAILURE, two causes
- WHAT: the only hand was the keeper; his straight line to the pit ran through his own quarry's back wall; he ended
  standing on the quarry's ladder.
- FIX (BUILT for 23): walk v3 — off the street graph a villager follows a LOCAL PATH over the real blocks (a step of
  1 at most, feet and head free, doors allowed, fences and walls not; 7/7 node checks: round a house, in by its door,
  down the pit's benches, through the gap in a fence). And the census workers of a quarry or lumberyard now work
  beside the keeper.

## R-16 · The early-village stall (0.0.22 and 0.0.23: 3 of 11 buildings finished between day 20 and day 44) — a CASCADE
- WHAT: plots stopped at 11 (0.0.21: 14 → 22); the founding houses waited "for 1 builder" for 20 days; with no houses
  finished nobody moved in (census 3), mood sank, the keepers left.
- MECHANISM (three links): (1) the boundary ring kept the first BENCH out until town I (bench streets carried 8+ plots
  each in 0.0.21); (2) fewer planned cottages meant fewer of the town's own builders (planned households × workers per
  person − shops = 0) and no inn yet to lodge hired hands → the builder budget was 0 → nothing finished; (3) nothing
  finished → no households → no builders. The slot counters proved it: 3,393 slot refusals were plot overlaps (the
  streets were simply full), 0 were tunnels.
- FIX (BUILT for 24): benches beyond the stones make the council send the surveyor out (as streets already do); the
  settlers always keep a crew of 2 builders (the founders build their own town).
- TEACHES: the economy's bootstrap had a zero fixed point that only good luck with the land avoided; every "need X to
  make X" loop needs a floor.
- IDEA (RECOMMENDATION): a self-check in the clock — if no stage has advanced for 10 days while plots wait, log WHY
  in plain words on the notice board (stone? builders? wages?) so a stall is visible in-game too.

## R-17 · The watch's first night (0.0.23) — a SUCCESS with three counting bugs
- WHAT: 7 on duty (6 watch + the sewer keeper), 2 went below (cover unlocked with their registered keys, shaft climbed,
  one round turned back and walked to its shaft), 20 monsters seen, 14 blows struck; the three zombies let loose on the
  square were gone within 20 seconds. The register shows 7 keys (1 sewer keeper + 6 watch), each with its custody line.
- BUGS (FIXED for 24): kills counted 0 (the blow's tick still saw the zombie alive → now counted on the death event);
  a watchman removed by the census stayed in the status as "?" (now forgotten); a stop was rarely counted (2.5 blocks
  < the walk's own 2.6 arrival → re-sent forever; now 3.2).
- IDEA (RECOMMENDATION): the kills / seen ratio per night is the "spawn pressure" — when it rises, the council could
  add a watch post or a lamp before the next tier asks for it.

## R-18 · The quarry was worked out before anyone could work it (0.0.23) — a FAILURE of the harness/real-time hand-off
- WHAT: the keeper stood idle all morning: no face. The skipped days had dug the whole pit (2,173 blocks, radius 16 —
  over the cap of 14 — and 8 deep), and a pit at its caps never offered another face.
- FIX (BUILT for 24): one pit law for the scripted days and the hands (capped radius / depth); a pit worked out at its
  caps makes way for the NEXT pit beside it; the spent pit joins the re-greening list and its whole floor returns to
  grass and wild flowers, cell by cell, from the spoil (F2).

## R-19 · Ladders trapped villagers (0.0.23: 23 stuck walks) — a FAILURE
- WHAT: the quarryman in his quarry's own stepped pit (ladders down to −6) and a cottager in a loft ladder.
- FIX (BUILT for 24): the local path can go up and down ladder columns, and the walker CLIMBS them rung by rung
  (scripted, in its own column — the engine's villagers don't path on ladders); 9/9 node checks incl. out of a walled
  pit by its ladder.

## R-20 · Nobody shopped (0.0.23: market empty) — a design slip
- WHAT: only jobless people shopped, and every grown person held a station.
- FIX (BUILT for 24): each household's SHOPPER is its first grown member who keeps no shop and stands no watch.

## R-21 · Other measurements from 0.0.23 (SUCCESSES unless said)
- Manholes 8/8 standing. Bodies: 7 post holders embodied, 10 of the dead removed with their records. A first child
  born (the lifecycle change). Sanitation 0.67 at city I: the latrine, bathhouse and infirmary stand-ins found no plot
  (the town was short of room — R-16), so the tier gate would hold a naturally growing town at city I until they stand.
- The neighbourhood centre opened on the parallel street (its well finished; its two shops found no room).
- The quarry rim re-greened 20 cells; the boundary ring grew 160 → 352 (per tier + on demand).

---
# Run 0.0.24 (build 24, 04:25–04:47) — what it taught

## R-22 · Only ONE side street ever opened, in six runs — a FAILURE, found and answered by evidence (E3)
- WHAT: from 0.0.19 to 0.0.24 every town stopped at 19–29 plots with 70–88 plots it could not place (19 at city I in
  0.0.24, 5 of them wells). The log showed 140 side-street attempts, every one 200–280 ms, and never the message a
  finished scan writes ("no side street could open").
- CAUSE (code + timing, no room for error): the side-street scan keeps a cursor so a long search can continue on the
  next call. It remembered the job and the offset, but not the HALF (70 / 55 / 40). One half takes ~200 ms on this
  hill, the budget is 40 ms, so every call planned the same first half of the same job and stopped: the scan never saw
  a second half, a second offset or a second job. The first side street (day 0) succeeded only because its first half
  fit.
- FIX (BUILT for 25): the cursor is (job, offset, half); a full scan that opens nothing rests 3 days (lifted at once
  when the boundary stones move); the scan's reasons are in the status (`side`).
- IDEA: every "budgeted" search in the clock (benches, blocks, roads) should carry its cursor to the innermost loop
  that can outlast the budget — the same trap may sit in other planners. Worth one audit pass.

## R-23 · A butcher's shop stood on the bench road (0.0.24) — a FAILURE (seen in the dump)
- WHAT: road 1's last 6 cells read as air under a stone floor at 196 66–68 343–348. The dump showed a 7 × 8 house —
  butcher #15 on stilts — standing across the 7-wide road where it meets the bench street.
- CAUSE: a plot's veto knew plots, tunnels, streets and older streets, but not the narrow roads.
- FIX (BUILT for 25): the roads (7 wide, every cell ±3) are in the plot veto (counted as `road`); a street end that a
  bench road leaves from no longer grows over the road.

## R-24 · The quarry walked away — four pits worked out, the fifth 124 blocks off (0.0.24) — a FAILURE
- WHAT: the accelerated days opened pit after pit, each 31 blocks further behind the quarry; the hand never reached the
  fifth (stood in his own quarry's ladder, "could not reach 411 375 / 433 372 / 483 372").
- CAUSE: R-18's fix worked as written; the "next pit beside it" only ever went further OUT, and a pit on falling
  land was "worked out" quickly (its top taken from its first column).
- FIX (BUILT for 25): six pit SITES around the quarry (behind, beside, further behind), each judged before it opens —
  no plot or street in it, the most rock above its floor (its top = the median ground, not one column); one change a
  day at most; all six spent → the quarry is WORKED OUT (no more stone from it, a chronicle line; the shortage charters
  a new quarry the normal way). A face the hand cannot reach in 6 walks rests 5 minutes (review #7).
- IDEA (RECOMMENDATION): a worked-out quarry could become a pond or a garden plot (real towns flooded their pits) —
  a later stewardship item, needs your taste.

## R-25 · Walking: 78 stuck for 12 arrived (0.0.24) — the land is NOT the cause (E4)
- WHAT: stuckBy level 52, below 14, direct 10, above 2. The chronicle's "could not reach" lines: 15 for the square,
  14 for the quarryman in his ladder, the rest for doors.
- EVIDENCE: an offline connectivity check (vanilla-like rules: a step up of 1, a drop of 3, fences/walls 1.5 high,
  slabs/stairs/ramps as half floors, ladders) over 0.0.24's block dump: from the square, 51,415 standing places are
  joined, and 25 of 26 stuck places are among them (the 26th is inside a fence). So a villager COULD walk from where it
  stopped to where it was sent: the fault is in the GUIDANCE (the route, the lead, the follow), not the land.
- A small finding on the way: the square's walk target is its centre cell — the well's wall. Harmless (arrival counts
  within 2.6), noted.
- INSTRUMENT (BUILT for 25): `clock walktest` — up to 8 villagers sent to the square / the farthest door / a door on
  another street, each traced every 2 s (place, the block at its feet, its lead, its path index), and every stall
  writes the 5 × 5 × 4 blocks around the walker and the blocks at its next 6 waypoints. The next run's stalls will show
  the mechanism instead of a guess.
- ALSO (BUILT): the local path treats bottom slabs, upright stairs, ramp quarters and bench seats as half floors (the
  walker stands in that cell). Checked: the old rule passed the same street tests (it stood ON them as full blocks),
  so this is accuracy, not the cure.

## R-26 · No purchase at all (0.0.24) — a FAILURE of the shopper rule
- WHAT: market null for the whole midday.
- CAUSE: only villagers with a body run the schedule; bodies go to the posts (watch, keeper, surveyor, builders) and the
  immigrants. A household whose first grown member had no body never shopped — and births/grown children never got
  bodies.
- FIX (BUILT for 25): the shopper is the household's first grown member WITH a body; each household without one gets a
  body for its shopper (after the posts, 3 a day, the cap of 48 kept); the day's shopping goals are counted
  (`marketTry`) so a quiet market says whether anyone set out.

## R-27 · Builders: a crew of 2 sent to a site 100+ blocks away on the bench, never arrived (0.0.24)
- Same walking fault as R-25 (the bench is reached by a 231-cell switchback road). No separate fix until the walk
  instrument reports.

## R-28 · SUCCESSES in 0.0.24
- The night watch: 6 on duty, 2 below ground with keys, kills now counted (2 of 3 zombies dead in 4 minutes; the third
  out of reach of the rounds). 7 keys in the register.
- Manholes 8/8, sewer lamps 32, three drainage networks (7 + 2 low points served; 1 asked).
- Bodies: 18 walking, 9 made, 13 of the dead removed. Two children born by town II; grown children looking for work.
- The boundary ring followed the tiers 160 → 352 with the surveyor; no disputes.
- Speed: the whole ladder to city I in 22 minutes, no hang, no watchdog.

## R-29 · Review fixes applied for 25 (the independent review, 04:0x)
- #2 sewer ops never run on sleeping chunks (they waited, then ran anyway after 80 beats); the back-fill waits for every
  cell of its trunk. #6 the woodcutter's search: rings at step 1 (the step-2 grid missed odd cells — his own saplings),
  900 cells a call, an empty sweep rests. #9 a stale civ:working tag is swept (it froze villagers out of the schedule
  after a reload). #10 pits: one change a day, six sites (R-24). #13 one walker's error no longer stops every walker's
  beat. #15 the outfall mouth extension obeys the same veto as its plan. #16 the bench asks the surveyor out only when no
  bench lay inside the stones.

---
# Runs 0.0.25 / 0.0.25b (builds 25 / 25b, 05:04–05:33) — what they taught

## R-30 · The town froze at day 6: a review fix met a silent engine refusal (0.0.25) — a FAILURE, mine
- WHAT: the founding's sewer surveys waited for their land to wake, forever; the probe waited for the queue.
- CAUSE: the ticking areas that keep distant land awake were 160 blocks wide, which is 10 chunks only when the box
  starts on a chunk edge; otherwise 11 × 11 = 121 chunks, over the engine's 100-chunk limit, and the engine refused the
  area without an error. Before the review fix, a sleeping sewer job was forced to run after 80 beats — so it had been
  running on land that was not loaded (the very fault the review named) and hiding the refusal.
- FIX (BUILT 25b): areas on chunk edges, at most 10 × 10 chunks, the engine's refusal detected and logged; a sewer job
  whose land stays asleep for 600 beats steps out of the queue (parked) and comes back every 3 days.
- LESSON CANDIDATE: "a guard that never fires can hide a deeper fault: when removing a forced fallback, first check
  that the normal path ever succeeds."

## R-31 · WALKING FIXED: villagers followed each other's leads (0.0.25b) — a SUCCESS (E6)
- RESULT: by town I, 224 walks arrived and 25 stuck (0.0.24: 12 arrived / 78 stuck over the whole ladder).
- CAUSE: the follow behaviour took ANY lead within 48 blocks; with a dozen villagers walking at once (watch, keepers,
  builders, shoppers) many chased another villager's carrot — 0.0.24's walkers stood 16–33 blocks from their own leads.
  It also explains the history: 0.0.19 (few walkers at once) had 0 stuck; each new office that walked made it worse.
- FIX: each walker holds a SLOT (48 = the embodied cap); its lead carries the slot as a property and the villager's
  follow group accepts only the lead whose slot matches (48 follow groups generated at build time). Leads no walk owns
  (after a reload) are removed every 10 s, and idle villagers get "lead off" again.
- IDEA (RECOMMENDATION): the same pairing trick (a slot property + matching filter) can make any "follow / guard / go
  to" behaviour personal — e.g. a watchman escorting a particular villager, or a child following its own parent.

## R-32 · Ticking slots kept "busy" by jobs they could not serve (0.0.25b) — a FAILURE (fixed for 25c)
- WHAT: four sewer surveys inside areas too small to wake them (their survey box is 145 blocks) counted as work IN
  those areas, so the areas were never released, and no area that could wake them was ever granted. Parking broke the
  jam after ~30 s each time.
- FIX (BUILT 25c): a job keeps an area busy only when the area covers the whole box that job needs.

## R-33 · The side-street search moved one step a day (0.0.25b) — fixed for 25c
- WHAT: with the cursor fixed (R-22) the search advanced, but only when a leftover plot tried for room (once a day),
  each try planning one half (~200 ms).
- FIX (BUILT 25c): the ROOM SEARCH runs in the background — every 10 ticks while days are skipped, every 3 s in real
  time — for any town with plots waiting; up to 3 waiting plots are placed a day when room exists. The block-closing
  search got the same cursor (the R-22 audit).

---
# Run 0.0.25c (build 25c, 05:33–06:2x) — what it taught

## R-34 · The town grew again — a SUCCESS (the side-street search fixes)
- 45 plots at city I, all 45 built; census 97–100 (52 married, 4 children); 9 streets (2 side streets opened, a block
  closed, 2 benches); manholes 13/13 standing; 2 drainage networks, 8 low points all served. 0.0.24 had 19 plots.
- But 59 plots still wait for room (the town wanted ~104 by city I), and the site differs from 0.0.24's (a square at
  y 87 instead of y 95): the founding read the land after the ticking areas changed shape — the site choice depends on
  which chunks happen to be loaded. RECOMMENDATION: read the founding site from the site field only (not live blocks),
  so the same seed always gives the same town (a later item; it makes runs comparable).

## R-35 · Walking: 723 arrived / 105 stuck over the whole ladder — a SUCCESS, with two causes left (the walk instrument)
- The traces: walkers keep 3–5 blocks from their own lead (leadDist 4.5; 0.0.24: 16–33).
- STALL CAUSE 1 (from the stall dumps): on the bench roads the route cells' heights were 1–2 BELOW the road surface —
  the lead sat inside the cobblestone and the follower stood still under it. FIX (built for 25d): a route cell's height
  is checked against the blocks the first time the lead goes there (the standing place within 3).
- STALL CAUSE 2: a villager on a lower street was joined to the graph cell of the street 4 blocks ABOVE her (the nearest
  in x / z) and stood at the foot of its retaining wall. FIX (built for 25d): the nearest graph cell is chosen by height
  too (within 2 of the walker's feet first).
- STALL CAUSE 3: a villager stepped off a sidewalk into a two-deep hollow beside a road's retaining wall and could not
  jump out. FIX (built for 25d): a walker with no progress for 30 s is helped ONCE onto its current route cell (counted
  as `rescues`). IDEA: the hollow itself is a land-shaping gap (the edge guard covers street edges, not road edges) —
  the road layer should get the same guard.
- The walk test's 8 walks were long (300–480 cells from the bench to the far side of town): 1 arrived, 3 stuck, 4 still
  walking at 2400 ticks. Villagers walk ~1.8 blocks/s — the vanilla pace.

## R-36 · The civic works were never retried — a FAILURE found by reading the code (E7)
- WHAT: the latrine, bathhouse and infirmary never stood in any run; sanitation stuck at 0.67.
- CAUSE: at a tier-up the civic works were laid out LAST (after every old leftover and every new house took the room),
  and a work without room went to a list nothing ever read again.
- FIX (built for 25d): the tier's civic works are laid out FIRST; a civic work without room is retried every day before
  the leftover houses; the room search also runs for them; the leftovers go by rank (prestige — the manor, the hall —
  then shops, edge trades, homes).

## R-37 · Nobody bought anything — because the counters were empty (0.0.25c) — the shopper fix WORKED
- 23 shoppers set out (182 trips), 11 households reached a counter, 0 bought: the counters are stocked on a REAL
  morning only, and the town came out of skipped days mid-morning. FIX (built for 25d): the first market hour of a day
  stocks the counters if the morning did not.

## R-38 · The quarry "worked out" at town III with 2 pits; the woodcutters found no trees — FAILURES
- Quarry: 4 of its 6 pit sites were rejected because their land was ASLEEP (unread columns counted as "no rock").
  FIX (built for 25d): a site on sleeping land is asked for (a ticking area) and waited for; worked out only when every
  site was SEEN spent.
- Lumberyards: 2 yards, 1 tree felled in the whole run, the hands idle. Not yet diagnosed — the yards' search radius
  (52 at city I) may hold no trees on this site, or the town's own plots/streets cover them. INVESTIGATION CANDIDATE:
  count logs within the radius in the dump; if the land is bare, a lumberyard should plant a coppice (saplings in rows)
  before it can fell — the real practice.

## R-39 · The server ran at ~14 TPS in the real-time phase (0.0.25c) — a WARNING for the PS5
- 25 s of game ticks took ~35 s of wall time with ~100 people, ~60 bodies, 24 walking at once, the watch, the work.
- INSTRUMENT (built for 25d): every interval of the clock, walk, work, watch and shop modules adds its milliseconds to
  a shared profiler; the status carries it, so the next run says which part costs what per tick.

## R-40 · Ranking the waiting plots starved the founding (0.0.26, stopped at village II) — a FAILURE, mine
- WHAT: one building finished by village II; timber 8, bread 0, prosperity 0 five days running.
- CAUSE: I ranked the waiting plots prestige → shops → edge trades → homes, to get the manor built. But the founding's
  own leftovers include its FARM, QUARRY and LUMBERYARD (the "edge" trades), which the plan had in a deliberate order:
  the inn, the butcher and the smithy took the room first and the village never got its producers — no timber, no stone,
  no bread, nothing built.
- FIX (build 25e): only the MANOR moves to the front; everything else keeps the plan's order.
- LESSON CANDIDATE: "a queue that an earlier design ordered on purpose is not mine to re-rank wholesale — promote the one
  item that needs it."

## R-41 · A cramped founding deadlocked: no stage bigger than the founders' day was ever built (0.0.26b) — a FAILURE (E8)
- WHAT: on this run's site only 2 plots fit at the founding; by village II one building stood, census 0.
- CAUSE (the code, no room for error): a stage is built only when its blocks fit in the day's builder budget, and the
  budget is reset every day — it never carries over. The founders' crew (2 × 40 = 80 blocks a day) could never start the
  farm (82), the cottage (86) or the bakery (127); with no house finished nobody moved in, so the crew never grew. Earlier
  sites happened to give the founding small first stages and newcomers early.
- FIX (build 25f): a crew with its whole day free takes on a stage bigger than its day and works it off over the next
  days (the excess is a debt taken from the next days' budgets).
- IDEA: the run-to-run variation of the founding site (R-34) turned out USEFUL — a cramped site exposed a deadlock the
  roomy ones hid. Keep varying sites deliberately (a list of seeds / sites per run), and keep one fixed site for
  comparisons.

## R-42 · The settlers' wagons carried too little on a cramped site (0.0.26c) — fixed
- WHAT: with the build-debt fix the founders worked, but timber, stone, planks and glass were short for weeks: the
  wagons carried the bill of the 2 plots that fit at the founding, not of the 6 still waiting for room.
- FIX (build 25g): the wagons carry the bill of the whole founding plan. RESULT (0.0.26d so far): village built with 4
  plots finished and 5 people, village II built 10 of 19, census 12, mood 93 — the cramped site recovers.

## R-43 · The profiler's first read (0.0.26d, village → town III) — where the script time goes
- Per tick, averaged over each step: the kit queue 2.5–13 ms (placing street pieces and houses — skipped days only),
  the WORK beat 11–15 ms during the town I steps (the woodcutters' tree search: 900 ground columns a call), the KEEPERS'
  beat 1.5–5 ms (every keeper away from its station re-planned a breadth-first route over ~20,000 street cells every
  5 s), the SCHEDULE 1–4 ms (100–400 ms bursts every 5 s: every villager that set out planned its route and its
  off-graph legs in the same beat). The walk beat, the watch and the clock itself: under 0.4 ms.
- The server ran 8–13 TPS throughout — but in steps where my scripts used ~9 ms a tick it still ran 7.7 TPS: most of the
  lag on this machine is NOT the scripts (structure placement, chunk loading for the ticking areas, ~60 vanilla
  villager AIs). That part needs the PS5 itself to judge.
- FIXES (build 25h): routes by A* with a cache of the last 300 (648/648 checks: same lengths as the old search, valid,
  copies); the tree search 200 columns a call; the coppice search once per yard every 10 s; the workshop hands read once
  a tick for all workshops; at most 6 new walks per schedule beat; the local leg search 1,500 expansions.

---
# Run 0.0.27 (build 25h, 06:58–07:35) — the cramped site, end to end

## R-44 · SUCCESSES
- THE NIGHT WATCH WORKS AGAIN: 6 on duty, rounds above and BELOW (4 below), 25 sightings, 14 strikes, 3 kills — all three
  zombies dead within ~40 s (0.0.25c had 0 on duty: R-35's body cap). Keys 7 in the register.
- THE CIVIC WORKS STAND: 8 of 9 due at city I (latrine, cistern, bathhouse, well-house, midden, lamplighter …), only the
  infirmary missing; sanitation 0.89 (every earlier run: 0.43–0.67). E7's fix verified.
- A neighbourhood centre on the parallel street (the retry). Walking: 316 arrived / 9 stuck / 27 rescues by city I
  (leadDist 4.6); the walk test 4 arrived / 2 stuck / 2 still walking (0.0.25c: 1 / 3 / 4).
- The cramped site grew to 35 plots (29 built), census 42, 11 streets incl. a bench; 0 bad verifications.
- The keepers' beat fell from 1.5–5 ms a tick to 0.01–0.7 (A* routes + cache).
- REAL-TIME TPS (the work phase, 20 TPS nominal): 19.2–19.5 when the scripts used 2.6–4 ms a tick.

## R-45 · FAILURES (fixed for build 25i)
- The MANOR (#24) was placed at town III but its 1,146-block stage never started: the "whole free day" rule never saw a
  whole free day (small stages took a little first). Now a stage bigger than the crew's whole day starts on any day with
  work left and no debt. It then waited for 56 timber (the woodcutter's yard is bare: the coppice was planted, 4 saplings).
- The quarry worked out after ONE pit: on the crowded hill every other site touched a street or a plot (2 % allowed).
  Now each site is tried at radius 14 and then 8, with up to 12 % of its columns taken (the dig skips them).
- The WORK beat still cost 5–14 ms a tick in real time and pulled the server to ~15.5 TPS: every search built the
  town's occupied set anew (~100,000 string entries). Now built once per change of the town, at most every 20 s.
- The COUNTERS: the first market hour stocked them without an error and shoppers still found nothing (10 households,
  109 trips). Not understood yet → INSTRUMENTED: every stocking records per shop n or why not (nochest / unloaded /
  noinv / full) into the status; the probe reads the bakery and butcher chests; at least 4 items a stocking.

---
# Run 0.0.28 (build 25i, 07:35–08:1x) — the cramped site again, with the 25i fixes

## R-46 · SUCCESSES so far
- The MANOR's 1,103-block stage started (the big-stage rule) and waited only for GLASS (3 short at city I — glass comes
  only with the wandering merchant: RECOMMENDATION, a glassworks trade in the charter list).
- The QUARRY kept digging: 4 pit sites opened, not worked out (the radius-8 fallback and 12 % allowance).
- The WORK beat: 0.16–1.0 ms a tick (was 5–15) — the occupied set is cached.
- City I: 36 plots (33 built), census 68–69, 6 children, 11 streets, civic works 7 of 9 (sanitation 0.78), a centre.

## R-47 · FAILURE: the walk test on a NEW bench — 0 of 8 arrived (0.0.28)
- The test villagers stood on the bench founded at the last step; the walk graph already held the bench's planned
  streets and road before they were laid — the leads floated over bare hillside (stall dumps: waypoints with air below).
- FIX (build 25j): the walk graph leaves out the cells of street pieces and road stretches still in the queue (access
  pieces excepted — they re-lay a laid street), rebuilt as the queue shrinks.

## R-48 · 0.0.28 real time — the FIRST REAL WORK (a SUCCESS)
- The woodcutter felled a tree and put 6 oak logs into the lumberyard's chest (the probe opened it: `oak_log 6`) — the
  first real-time output of any run. Three quarry hands walked the 160 blocks from the bench to the pit on its 4th site
  and struck the face. The builders reached the manor's site and worked it (labour 500 of 8,824).
- The night watch: 7 on duty, all 3 zombies dead before the first 20-s sample.
- The plan view (`_docs/CITY-PLAN-0.0.28.png`): three parallel streets closed into blocks by cross streets, the city
  wall ring around them, the bench with the MANOR plot and the switchback roads to the west, the quarry pits at the
  east edge.

## R-49 · The counters were never stocked — found (E9)
- CAUSE (code + run record: the bakery and both butchers were finished and open, the counters' record stayed null): the
  market gate tested `s.accelNow`, which is refreshed only when the clock advances days — the harness PAUSES the clock
  for its checks (and so may he), so the last skip's "true" stayed and the gate never opened.
- FIX (build 25j): the gate reads the skip itself (`accelLeft`); the gate's inputs are recorded (`marketGate`).

---
# Run 0.0.29 (build 25j, 08:09–08:4x)

## R-50 · THE MARKET WORKS (E9 verified) — a SUCCESS
- At the market hour the counters were stocked (bakery 11 loaves, two butchers 11 cuts each: "ok"), and households
  BOUGHT: 3 → 4 → 7 purchases, 0 "found nothing". The chests afterwards: bread 41, cooked beef 50 and 51.
- The gate's record showed the cause plainly: `accelNow` still true (the clock paused after the skip), `accelLeft` 0.

## R-51 · Bench → town walks still stall (0.0.29 walk test: 5 stuck of 8 by 2,100 ticks) — OPEN, two mechanisms seen
- A villager below a road on its embankment was joined to the road cell 5 blocks over her head (the nearest
  same-level cell lay ~10 blocks away) → FIX in source for the next build (a same-level cell within 24 first).
- Where the bench road meets the bench street the stall dumps show a 3-block step (road end at y 81, street at 78): a
  villager can drop it but not climb it. INVESTIGATION: the road's last cells vs the bench street's sidewalk height
  (walkcon over the dump will say whether the bench is joined to the town on foot at all).

## R-52 · 14:4x — the 'leaves don't work' sighting = vanilla swamp oaks in RP-05's broken leaf textures (AUDIT-TREES-LEAVES-2026-10-04)
- WHAT HAPPENED: his new seed put the village beside a swamp; the engine's own swamp oaks (minecraft:oak_log, vines) stand among
  our oaks; their leaves take RP-05's `leaves_oak` 32 x 256 strip with no flipbook entry -> frame 0 only (32 texels per face) and
  black under alpha 0 -> black cubes at the opaque distance. Mangroves: 128-px textures with black alpha 0 -> black canopies.
- LESSON CANDIDATES: (1) every vanilla leaf key in the stack must resolve to a SQUARE texture (a strip needs its flipbook entry or
  only frame 0 survives, L-ATLAS-SQUARE); (2) the colour under alpha 0 is what the opaque pass shows — fill it light, never black;
  (3) a biome census must also run on the seed in question (bds_load seed option) — one sample per biome found no vanilla oaks
  anywhere our rules run, but the engine's swamps are real.
- IDEA: RP-05 1.3.59 = square 256 vanilla leaf textures cut from our pw_leaves2 face art (tint-ready) for all 11 keys (S/M).
- IDEA: a `pw:fell test` scriptevent or a visible chat line when a break is skipped for Creative, so a tester in Creative is
  told why nothing fell (S).
## R-53 · the 10-03 note 'the runtime leaf scanner converted them' was wrong
- No code converts leaves either way; the flower forest's 64 vanilla oak logs are 15 fallen trunks; savanna's acacia logs are
  our acacias' square trunks. Corrected in the journal.

## R-54 · the flat-ground fall rule (his F7, v1.3.206) never ran — the slope mode always won
- `pickFallYaw` measured each direction's "drop" from the LOWEST FALLING LOG's y (stumpPos.y), not from the ground under the
  stump: on flat ground every direction read a 2-4 block drop, `maxAbsDrop >= 1` switched the scorer to slope mode, all drops
  tied, and the first sample (east) or the least obstacles won. The heavy-side / away-from-the-chopper tiebreak was dead code.
- FIX (BP-02 1.3.220): the drop is measured from the ground top under the stump; flat ground now scores 0 -> the F7 rule runs.
- LESSON CANDIDATE: a mode switch on an ABSOLUTE measurement needs a baseline from the same reader (here: ground vs ground).

## R-55 · the leaf look rule (variant 5/6 at wood contact) is missing on 0.7 % of the template leaves
- 1,609 of 229,918 leaf cells that touch wood wear a far-look variant (0-4): acacia 189, cherry 153, mangrove 448, dark_oak_elder
  150, oak_elder 127, pale_oak_elder 98, spruce_elder 439 — the rescaled (D-C525) and square-trunk groups, where re-sampling moved
  leaves next to wood after the variants were baked. The 24-per-age dodecagon sets (oak/spruce/birch/jungle young-old) are clean.
- IDEA: a re-bake pass (tools, S) that re-runs leaf_look on those 7 groups' wood-touching cells; visual gain small (inner-crown
  look only). Awaiting his word.

## R-56 · the Phase-6 fall-direction sign, closed by law (D-C565)
- L-ROT-DIR (verified 09-27) + the fall animation's NEGATIVE z rotation => the trunk tips toward file -x = the entity's RIGHT =
  world (-cos yaw, -sin yaw). The script's (-cos yaw, +sin yaw) was a reflection across x: a south/north pick rendered dead
  opposite, a diagonal a quarter turn off — the July witness exactly. One constant (FALL_Z_SIGN) now carries the law; +1 restores
  the old convention if the witness disagrees. The carbon-copy turn law (D-C524) already used the right frame.
- WITNESS TEST (one fell): the [FELL] line now prints the compass direction ("dir yaw=90 N"); the trunk must lie that way and the
  logs drop along it.
