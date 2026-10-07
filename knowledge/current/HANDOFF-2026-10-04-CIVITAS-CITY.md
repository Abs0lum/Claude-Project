# HANDOFF — 2026-10-04 — CIVITAS CITY: BP-02 1.3.219 + RP-04 1.3.158 + Markers BP 0.2.3 + TestRunner 0.5.23

The CURRENT-STATE for the CIVITAS city-planning program (D-C533 … D-C555). Supersedes the 10-03 V6 handoffs for
everything CIVITAS; trees / RECHECK / mobs handoffs stay authoritative for their own packs. Journal: `_logs/decision_journal.md`
D-C533 … D-C555. Ledgers: `_docs/RESULTS-AND-IDEAS-2026-10-04.md` (R-1 … R-4x, every run's failures AND successes with an
idea each) and `_docs/QUESTIONS-AND-ASSUMPTIONS-2026-10-04.md` (Q1 … Q18 with the answer assumed, E1 … E8 settled by
evidence). Design: `_docs/CIVITAS-CITY-PLANNING-DESIGN-2026-10-03.md` (v1.0 … v1.3 addenda, §1 … §32).

## 1. Install
| Pack | Version | Replaces | Note |
|---|---|---|---|
| **BP-02 Tectonic BP** | **1.3.219** | 1.3.218 and every earlier 1.3.2xx | CIVITAS city planning (all of it) + the mob size pass (G) |
| **RP-04 Basic RP** | **1.3.158** | 1.3.156 / 1.3.157 | the walking villager + lead render |
| **PW-Civitas-Markers BP** | **0.2.3** | 0.2.1 | (Markers RP 0.2.2 stays) |
| **PW-TestRunner BP** | **0.5.23** | 0.5.20 … 0.5.22 | lineup **p24 CIVITAS CITY** (9 steps) |
Personal use only (§9). Delivery: gofile folder AR-CIVITAS-CITY-2026-10-04 (https://gofile.io/d/0A7FxIBX), md5 in §6.
Also in Google Drive (his 12:11 ask; from now on the delivery route): My Drive/ClaudeUploads — the same four files, Drive md5 == local (tools/drive_ship.py).

## 2. What is in 1.3.219 (since 1.3.218)
- **Streets and room** — his StreetKit pieces (village width → town width at town I), profiled by ramps; streets grow at
  their ends; PARALLEL side streets (pitch 60/73/47) joined by connectors, BLOCKS closed by cross streets on the grid
  lines; when a hill holds no more parallels, BENCH streets 70–110 out joined by narrow switchback ROADS (1-in-4 four-part
  ramps); stepped hill-town climbing legs. The side-street search runs as a background job; up to 3 waiting plots are
  placed a day; the manor and the civic works go first. Plots never on roads; edge guards (berm / retaining column +
  parapet) where the ground falls away beside a sidewalk.
- **Sewers** — the trench under every street carries running water; drainage NETWORKS with their low points; each low
  point drains by a lined TRUNK (falling 1 per 7, lanterns every 12, trunk manholes) to a grate on a hillside or river
  bank, or into a SOAKAWAY pit; spent exits back-filled. MANHOLES in the sidewalks; covers open only with a REGISTERED
  KEY (sewer keeper + watch posts; never craftable; his test key via `clock keytest` with the civ:tester tag).
- **People** — the census (names, homes, jobs, kin, marriage, births, ageing, deaths, inheritance, moods, rumours,
  learning trust); BODIES for the posts (watch, sewer keeper, surveyor, builders) and one SHOPPER per household (cap 48,
  12 kept for posts); the dead are removed with their records.
- **Walking** — every villager follows ITS OWN invisible lead along the street graph (A* routes, cached) with local
  paths over the real blocks off the graph (ladders climbed rung by rung, half blocks as floors); route heights checked;
  one rescue per walk out of a hole.
- **Real work** — quarrymen mine the pit face block by block (six pit sites around a quarry, then worked out) and carry
  to the chest; woodcutters fell trees, replant by the stump, plant a COPPICE where none stand; builders walk to real
  sites and raise stages layer by layer; skipped days stand in with scripted digging / felling.
- **Market** — bakery and butcher counters filled each morning (or at the first market hour after skipped days);
  each household's shopper buys at midday from the counter it trusts; NEIGHBOURHOOD CENTRES on parallel streets.
- **The watch** — night rounds street to street and BELOW through the sewers between manholes; strikes and chases
  monsters; the sewer keeper by day.
- **Civic works** — midden, latrine, cistern, bathhouse, lamplighter, well-house, infirmary … as stand-in buildings
  until their own designs; SANITATION gates the next tier and weighs on mood and health.
- **Stewardship** — spent pits re-green from their spoil; a 24-wide GREENBELT outside the city wall; the CITY WALL with
  gates at city I.
- **Boundary stones** carried out by the SURVEYOR with the tiers and when streets press on them.
- **Economy** — the ledger (stock, prices, wages, treasury, imports by road or the wandering merchant), builders' crews
  that work off big stages over days, the settlers' wagons carrying the founding plan's bill.
- **The MANOR** (town II): stone ground floor, oak upper storey, spruce hip roof, jib + baize doors, service corridor,
  kitchen, back stair, steward's office, chambers, garrets.
- **Mob size pass (G)** — 59 giants at 2.5× their small kin with reduced damage; 324 small hostiles capped at 2 damage
  and half as often (MOB-PASS-G.md before / after table).

## 3. Verification — proven and not proven (P1)
Server-proven on BDS 1.26.52 (the harness runs a whole ladder village → city I with skipped days, then real time):
| Check | Evidence (run) |
|---|---|
| Town growth: side streets, blocks closed, benches + switchback roads | 45 plots / 9 streets (0.0.25c); 36 plots / 11 streets on a cramped hill (0.0.28) |
| Sewers: running trench, networks, trunks / soakaways, manholes, keys | all low points served (0.0.25c: 8/8); manholes 13/13 standing; keys 7 in the register |
| Walking (own leads) | 0.0.25b 224 arrived / 25 stuck by town I; 0.0.27 316 / 9 by city I (leadDist 4.6) |
| Night watch above and below | 0.0.27: 6 on duty, 3/3 zombies dead in ~40 s; 0.0.28: 7 on duty, 3/3 in < 20 s |
| Civic works stand (stand-ins) | 0.0.27: 8 of 9 due at city I, sanitation 0.89 |
| Real work | 0.0.28: a tree felled, 6 oak logs in the yard's chest; 3 quarry hands at the face; builders at the manor site |
| Manor | placed (0.0.26d at town III; 0.0.28 on the bench), its big stage started; finishing needs glass from the merchant |
| Quarry pit sites | 0.0.28: 4 sites used, not worked out |
| Script cost (profiler) | real time: walk 0.3, watch 0.3–0.6, clock 0.5, keepers 0.02, work 0.2–1.0, schedule 1.3–2.8 ms a tick |
| node tests | streets 28 · road7 25 · people 31 · economy 21 · drain 23 · walk local 11 · route A* 648 · TestRunner mock 348 |
| Market (counters stocked, households buy) | 0.0.29: counters "ok" (11 each), 7 purchases, 0 empty; chests bread 41 / beef 50–51 |
| BDS load gate (all four packs together) | 0 ERROR; banners BP-02 v1.3.219, TestRunner v0.5.23 (p24 11 steps), Markers v0.2.3, CIV-CLOCK 39 staged buildings |
| Final build = build 25j, verified by run 0.0.29 | 36 plots (33 built, 0 bad), census 64 (mood 97), watch 6 on duty / 3 of 3 zombies in < 20 s |

NOT proven / KNOWN OPEN (P1 — these need your PS5 or the next round):
- **Bench → town walking**: the bench road's arrival ramp ends 3–4 blocks ABOVE the bench street (slice at z 304,
  run 0.0.29: ramp q4/q3/q2 at y 81, the sidewalk at 77) — villagers can drop it, not climb it; walkers from a bench
  lean on the one-time rescue (0.0.29 walk test: 5 of 8 stuck). The road planner's arrival height is the next fix (R-51).
  A same-level graph-entry fix is in `tools/bp02_src/pw_civ_walk.js` (nearestLevel) — NOT in the shipped build.
- **The manor finishing**: its 1,103-block stage waits for GLASS, which only the wandering merchant brings (idea: a
  glassworks trade). The manor itself is placed and prepared.
- **The lumberyard** on bare land plants a coppice; real felling seen once (0.0.28, 6 logs). Quarry hands mined in
  0.0.28 (0 counted in 0.0.29's window).
- **Frame rate on the PS5**: the harness server ran ~19.5 TPS in real time when the scripts were light (2.6–4 ms a
  tick); the schedule and work beats now 1–3 ms a tick. The ~60 vanilla villager AIs are the engine's cost — your PS5
  is the judge (Q18 decides how many bodies).
- **The neighbourhood market's own shops** (B2) on the parallel street: the well opened, its bakery / butcher wait
  for room on a crowded street.

## 4. Questions for you (copy-paste blocks in the QUESTIONS file; the assumed answers are built)
All 18 are open (each has a copy-paste block and the answer assumed — the build follows the assumption):
Q1 the clipping trapdoor / ladder (needs your screenshot) · Q2 road grades · Q3 narrow lanes and stair alleys · Q4 tiny
giants in the size pass · Q5 the giant squid without a base · Q6 block hardness by tool tier · Q7 where the sewers drain ·
Q8 sewer trunks under open ground · Q9 quarter hearts · Q10 vines that sway · Q11 low points in mid-street · Q12 civic
works and palaces without designs · Q13 the greenbelt · Q14 what the watch does to monsters · Q15 a villager's death in
the census · Q16 the manor's look · Q17 a worked-out quarry · Q18 how many villagers walk (bodies).
Settled by evidence (no answer needed): E1 … E9.
Added 11:2x CT (his ask for every unanswered question): Q19–Q31 carried from earlier rounds — trees (REVIEW-WEEK §5: Q19 vanilla
trees, Q20 swamp oaks, Q21 daughter distance, Q22 densities, Q23 grove/peaks rules, Q24 the density fix, Q25 stray lights,
Q26 trees in crowns) and the city plan's §9 (Q27 sewer lighting, Q28 the stand-in grate, Q29 block size, Q30 narrow-road
width, Q31 the regional look). 31 open in all.

## 5. Reminders
- DEFERRAL-N1 (his 02:53): abandoned homes, lost assets and the aftermath of unrest wait for the crime / discontent /
  narrative work, after he has watched the Utopia-First run.
- Lesson candidates (for the ledger): resumable budgeted searches persist every loop index (E3); a guard that never
  fires can hide a deeper fault (R-30); do not re-rank a deliberately ordered queue wholesale (R-40); kill by PID only
  (pkill -f matched my own shell once, 06:5x).

## 6. Files
Delivery folder: **AR-CIVITAS-CITY-2026-10-04 — https://gofile.io/d/0A7FxIBX** (each file: server md5 == local, a
browser download byte-exact, Molang lint 0 errors).
| File | Bytes | md5 |
|---|---|---|
| BP-02-AbsolutRealism-Tectonic-BP-v1_3_219.mcpack | 5,568,965 | fde7fceade87b38c6a71d7050f469865 |
| RP-04-AbsolutRealism-Basic-RP-v1_3_158.mcpack | 192,432,718 | c7567219e962e73a1999d9f0265ae5de |
| PW-Civitas-Markers-BP-v0_2_3.mcpack | 47,278 | 887cb748888f708f87e679d122a4f837 |
| PW-TestRunner-BP-v0_5_23.mcpack | 318,979 | 2cbe100a0554769317ce75d1b479cd67 |
Documents (sent in chat and in project knowledge): this handoff · RESULTS-AND-IDEAS-2026-10-04 · QUESTIONS-AND-
ASSUMPTIONS-2026-10-04 · LESSON-CANDIDATES-2026-10-04 · CIVITAS-CITY-PLANNING-DESIGN (v1.3) · MOB-PASS-G.md (the size
pass before / after) · CITY-PLAN-0.0.25c.png and CITY-PLAN-0.0.28.png (plan views) · MANOR-RENDER / MANOR-PLANS.
Test: `/scriptevent pw:test start p24` (TestRunner 0.5.23) — nine steps from the founding to the size pass.
Tools new this round: `tools/garbage_tar_to_drive.py` (used, approved flow) · `tools/profwrap.py` (the profiler wrap) ·
the walk instrument (`clock walktest`) · `walkcon.py` / `dumpgrid.py` (scratch: offline walk connectivity over a dump) ·
`tools/build_testrunner_0523.py` · `tools/package_round_1004.py` · `tools/bp02_src/test_route.mjs`.
