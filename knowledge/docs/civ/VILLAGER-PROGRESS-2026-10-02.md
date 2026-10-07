# CIVITAS: villager and civilian behaviour progress (2026-10-02)

**Question (his 14:13, D-C460):** "How far have we come on the development of our villager/civilian behaviour?"
**Method:** read-only audit. I read `_logs/decision_journal.md` (D-C178 to D-C460), `_logs/phase_log.md`, the CIVITAS design docs and handoffs in `_knowledge/AbsolutRealism-Knowledge-2026-09-29/project-knowledge/`, `_docs/*.md`, and the shipped scripts. For the scripts I used only the newest build of each pack: BP-02 `_build/bp02-205`, Markers `_build/markers-0.2.1` (+ RP `markers-0.2.2-rp`), TestRunner `_build/testrunner-0.5.12`, StripMine BP `stripmine-bp-1313`, BP-01 `bp01-135` and BP-03 `bp03-134`. I also checked `tools/civgen.py` and `tools/civ_src/`.

**Status key:**
- **DESIGNED** means it exists only in a document.
- **BUILT** means code shipped in a pack. It stays "awaiting witness" until he confirms it (P1).
- **WITNESSED** means a journal or handoff line records his in-game confirmation.
- **NOT STARTED** means there is no document section and no code beyond the roadmap line.

## Bottom line

- **No villager behaviour runs today.** I found no script for the folk ledger, day segments, station pathing, hunger, production, stock, purchase or work-week, in any build. The villagers in his world are **vanilla `minecraft:villager_v2` running vanilla AI**, with a different look.
- **The groundwork for that behaviour is mostly built.** Phase 0 is largely done:
  - **Station, zone, port and datum markers.** These are the data the behaviour code will read.
  - **The furnished homestead.** Hearth, flue, dual wall, rafter, furniture, sit seats, and the seat-station registry.
  - **The ladder hatch.**
  - **The structure pipeline.** As of today a generated building carries its markers inside the file and is checked by the dedicated server (BDS) before delivery.
- **Phases 1–9 are DESIGNED only.** The design is large: 11 papers, 278 KB, 2026-08-14/15, plus the STRATEGY-v4 canon. None of it has code.

## Status table

### Phase 0: Foundations

| System | Status | Evidence |
|---|---|---|
| Station markers (`pw:station_*`, 18 roles incl. `seat`) | **BUILT** (entity form). Block form v0.1.x **used in-world** by him | Markers BP **0.2.1** `BP/scripts/pw_markers.js` (STATIONS table, frozen icon numbers 12–29). Entity form since D-C227/D-C229 (09-22). Seat role added in 0.1.9 (D-C223). He used the block form in his cottage r0 (`HANDOFF-09-20-B` census; D-C459). **Correction 18:08 10-02 (D-C472): his r0 file from the Proving Grounds world holds NO station or zone markers (block or entity) and no decor; r1's stations and zones were my layout.** The 09-27 19:11 load was clean with Markers up (phase_log l.275), but that proves loading, not function. Functional lineup **0x** has not been reported. |
| Zone markers (12 kinds, precedence order) | **BUILT** (entity form) | Same file, ZONES table. Zone readings ruled 17:20 09-22 (D-C219) → `CIVITAS-ZONE-TABLE-v1.md`. The one-block-per-cell conflict was witnessed in frames F11–F18 (D-C225 (4)) and fixed by the entity rewrite. The entity form is unwitnessed. |
| Port markers (passage / sewer / stair / well) + datum | **BUILT** | Same file, PORTS and datum. He placed the `pw:port_sewer` and `pw:datum` blocks in cottage r0 (`HANDOFF-09-20-B` l.38). |
| Marker admin (`civ:markers hide/show/migrate/list/check/remove`, `civ:zone close/status`, `civ:station reset`) | **BUILT**, unwitnessed | `pw_markers.js`; D-C227 |
| Frame posts (stagger rule, `pw:frame_cornerpost`, Half-Spur) + `civ:frame reflow` | **BUILT**, unwitnessed | Markers BP `scripts/main.js` FRAME LISTENER v2 (0.1.8, D-C195). The only in-game report was D-C206: geometry errors explained by RP 0.1.7 still being attached. The stagger has never been confirmed. Option B ruling: no posts in saved files (D-C193). `pw:frame_plate` (spec D-C56) was **not found**. |
| Manhole hatch (HATCH LAW: opens only from below, phased slide) | **BUILT**. Placed in-world; behaviour not confirmed | Markers `main.js` `pw:hatch`. Present in his cottage r0. The "survival hatch test" was still pending in `HANDOFF-09-19-FILL-CUT` l.70. |
| Ladder hatch lid (`pw:hatch_lid` entity over a vanilla ladder; PROPOSAL H) | **BUILT** (probe), unwitnessed | Markers 0.2.1 entity + item (D-C227/D-C229). The cottage r1 carries one (D-C459). The fallback H2, script-driven climbing, is pre-approved if the probe fails. |
| Homestead: hearth fuel machine, flue chute, dual wall, rafter | **BUILT + WITNESSED** (hearth lights and burns) | BP-02 `pw_homestead.js` / `_logic.js` / `_materials.js` (since 1.3.178, D-C200; current 1.3.205). **Witnessed:** "F10: hearth works (lit, 3 logs)" (D-C208, 09-22). Hearth wall and flue face defects were witnessed and fixed (D-C212, L-XFACE). |
| Homestead: room smoke, fog, cough | **BUILT**. Witnessed as a FAULT; room fog now OFF | D-C251: stuck `pw:smoke_room` fog witnessed 09-27. Fixed in BP-02 1.3.187 with room FOG off plus a stuck-fog sweep (D-C252). Embers and sparks shipped in 1.3.188 and are unwitnessed (D-C258). |
| Furniture family (12 pieces × oak/spruce/dark oak) | **BUILT + WITNESSED** (renders in-game; round-1 clipping witnessed) | BP-02 `pw_furniture.js` + 36 blocks (1.3.183, D-C223). The witness was 19:46 09-22 (D-C225 (3)). The round-2 fixes (1.3.184, D-C226) are unwitnessed. |
| Sit seats (`pw:seat` rideable entity) + **seat-station registry** (`SEAT_BLOCKS` export) | **BUILT**, unwitnessed | `pw_furniture.js` (D-C223). The sit witness was announced (D-C224) but never recorded. The registry is the first piece of code written explicitly for villager use: "the CIVITAS seat-station registry". |
| Table auto-join | **BUILT**, unwitnessed | `pw_furniture.js` (D-C223) |
| Planks neighbour rule + `reflowPlanks(dim,min,max)` for the CIVITAS placer | **BUILT**, unwitnessed | BP-02 1.3.204 `pw_planks.js` (D-C458) |
| Structure pipeline: `.mcstructure` writer, building generator, verifier | **BUILT**. BDS-verified, **not witnessed** | `tools/mcstructure.py`, `tools/civgen.py`, `tools/civ_pack.py`, `tools/bds_civtest.py`, `tools/civ_src/civ_verify.js` + `pw_civ.js` (D-C459, 10-02). In BDS: file 1344/1344 cells; placement at all 4 rotations 1344/1344 cells + 27/27 marker and hatch entities; hinges turn. |
| First CIVITAS building: `pw:mvv_cottage_s_a_r1` (furnished, stations, zones, datum, ladder hatch, sewer port) | **BUILT**, awaiting witness | BP-02 **1.3.205** `structures/pw/mvv_cottage_s_a_r1.mcstructure`; delivered gofile L8QSjf5Z 19:06Z 10-02. Open items: (a) his r0 keeps the clearance column on the LEFT, while the written law says RIGHT (D-C459 check item); (b) "roofs must truly slope", because my preview drew roof45 as cubes (D-C460). Roster: **1** building of the ~46 types in `CIVITAS-STRUCTURE-PROGRAM-v1` (scope "EVERYTHING", D-C456). |
| In-game structure tests `/scriptevent pw:civ list / verify / place` | **BUILT**, unwitnessed | TestRunner BP **0.5.12** `scripts/pw_civ.js` + `civ_verify.js` + `civ_manifests.js` |
| Proving Ground world | **PARTIAL** (his world exists; the six-premises bench does not) | His Drive `Worlds/PROVING_GROUNDS` (09-28): cottage r0 + 5 road pieces (D-C457). The six placeholder premises with stations (`CIVITAS-BUILD-FUTURE-v1` §1.2) are not built. |
| Construction props (scaffold pole, deck, lashing, sawhorse, brazier, tarp …) | **NOT STARTED** (DESIGNED) | No such blocks among BP-02's 453. Spec: `BUILD-FUTURE-v1` §7 Phase 0; D-C39 |
| `civ_values.json` (species bases, multipliers, catchments) | **NOT STARTED** (DESIGNED) | No file anywhere outside `_bds`. Spec: `BUILD-FUTURE-v1` §7 |

### Phases 1–9

| Phase / system | Status | Evidence |
|---|---|---|
| **1 Metabolism**: folk ledger | **DESIGNED** | `CIVITAS-STRATEGY-v4` ($-Ledger, monetary constitution), `COMPETITIVE-SOCIETY-v2`, `CADENCE-AND-CONTROL-v1`. No code. |
| 1: six day-segments | **DESIGNED** | `BUILD-FUTURE-v1` §1.2/§7, `CADENCE-AND-CONTROL-v1`, `COMPETITIVE-SOCIETY-v2`. No code. |
| 1: station pathing | **DESIGNED**. The input data is BUILT; the pathing code is NOT | Markers carry the station graph. No code moves any entity to a station. |
| 1: hunger, production, stock, purchase | **DESIGNED** | `STRATEGY-v4`, `COMPETITIVE-SOCIETY-v2`, `LIVING-WORLD-v1`. No code. |
| 1: work-week + shift system | **DESIGNED** | `STRATEGY-v4`, `COMPETITIVE-SOCIETY-v2`, `BUILD-MANIFEST-v2`. No code. |
| **2 The Grain** (9 traits, expectation/surprise → episodes → reward learning → associations → imitation → schemas; cognitive LOD; kill switch) | **DESIGNED** | `LIVING-WORLD-v1` (THE GRAIN), `CADENCE-AND-CONTROL-v1` (traits, LOD). Rulings D-C22/D-C31/D-C33. |
| **3 Lifecycle** (birth, stages, ageing, death, succession, kin, Demographic Governor, Book of Souls) | **DESIGNED** | `CADENCE-AND-CONTROL-v1`, `BUILD-FUTURE-v1` §2 (cohort bulge ~day 85). Hard rule: must not ship before Phase 4 (§7.1). |
| **4 Construction**: stage derivation (S1–S5) | **DESIGNED** | `STRUCTURE-PROGRAM-v1`, `AUTHORING-WORKFLOW-v1` (author endpoints, derive between), `BUILD-FUTURE-v1` §4 (D-C40), D-C193 (stud frame = scaffolding, 3–7 days) |
| 4: `$project`, crews, stalls, ruins | **DESIGNED** | `LIVING-WORLD-v1`, `STRATEGY-v4`, `CAPITAL-AND-CRAFT-v1` |
| 4: the assembler | **PARTIAL**: only the placement step is built | `civ_verify.js placeAndVerify` + `turnHinges` + `pw_planks.reflowPlanks` place, turn and verify a finished building on command. Nothing yet does staged, timed or villager-driven assembly, and there is no stud-frame generator. |
| **5 Society** (fondness, friction, jealousy, gossip/SIR, amends & accountability, social capital, conformity) | **DESIGNED** | `SOCIAL-DYNAMICS-v1`, `INTERACTION-MATRIX-v1`, `BUILD-FUTURE-v1` §5 |
| **6 Economy II** (Three-Hand Law, Role Fission, contracts, catchment competition, value index, decay & the Mender, waste & sanitation) | **DESIGNED** | `COMPETITIVE-SOCIETY-v2`, `CAPITAL-AND-CRAFT-v1`, `THE-TOOL-LADDER-v1`, `CADENCE-AND-CONTROL-v1`. The carpenter trade catalogue exists as content (`CARPENTER-CATALOGUE-v1`). |
| **7 Polity** (contentment, legitimacy, elections, offices, Books, governors, borders) + Stewardship, Homestead Registry | **DESIGNED** | `CADENCE-AND-CONTROL-v1`, `STRATEGY-v4` (Stewardship, Areas, Watch), `BUILD-MANIFEST-v2` |
| **8 Roads & Trade**: freight, landed cost, inter-settlement trade, road risk | **DESIGNED** | `COMPETITIVE-SOCIETY-v2`, `LIVING-WORLD-v1`, `INTERACTION-MATRIX-v1` |
| **9 The Shadow** (necessity crime → cells → `$plot` → hideouts, heat) | **DESIGNED** | `CIVITAS-THE-SHADOW-LAYER-v1` |

### Infrastructure and side programmes

| System | Status | Evidence |
|---|---|---|
| Streets: road kit | **BUILT + WITNESSED** | PW-StreetKit BP **0.1.4** (11 `.mcstructure` + 6 `/function pw/street_*`, no scripts): "witnessed correct (street_row3/row5/cross + *_clear)" (`HANDOFF-SESSION-2026-09-19-FILL-CUT` l.12). He also authored 5 road-piece structures (cross_13, dead_13, straight_3, straight_3_access, ramp_7) on Drive (D-C456). Road spec v3: `BUILD-PLAN-2026-09-07`. The plan to absorb StreetKit into BP-02 is queued (D-C240). |
| Sewer: section −14, trunk 7×5, branch 3×3, shaft, manhole, sewer port | **PARTIAL**: built by hand in his cottage plus marker blocks; the kit is DESIGNED | `BUILD-PLAN-2026-09-07` (section), `STRATEGY-v4` / `BUILD-MANIFEST-v2` (sewer kit: cove block, trunk, junction chambers, round ports). Built so far: `pw:manhole_cover`, `pw:port_sewer`, and the shaft + port in cottage r0/r1. There are no cove or trunk blocks and no sewer structures. |
| **Citizen Registry pilot** (names / surname / epithet / foreman on villagers via dynamic properties) | **NOT STARTED** (queued 08-21) | `HANDOFF-SESSION-2026-08-21-PIGFIX-BBMODEL-BRIDGE` l.36/l.40 ("Registry pilot = advised move #2"; queued cut). Its source is the study of *Villagers Can Build* (`STUDY-LESSONS-v1` Classroom B: `nachito:villager_given_name` etc.). No code in any build, and no journal entry after 08-21. |

## Villager and civilian entities that exist today

- **No custom villager, folk or citizen entity exists.** I searched entity identifiers in BP-02, BP-01, BP-03 and the 1,109 StripMine BP entities: none match villager, folk, citizen, npc, guard or human.
- **None of our BPs overrides a vanilla villager.** `minecraft:villager_v2`, `minecraft:wandering_trader` and `minecraft:zombie_villager_v2` therefore run Mojang's own AI. That includes vanilla professions, beds and workstations.
- **Their look is ours.** These are client-side files only:
  - RP-07 **1.4.43** `entity/villager.entity.json` and `wandering_trader.entity.json`: `geometry.villager` (64×64) with 23 animations (walk, run, panic, sleep, swim, special idles, nose yaw …). The 08-21 handoff calls this rig "VA villagers" (protected).
  - RP-06 **1.4.28** `zombie_villager_v2.entity.json`.
- **CIVITAS entities that do exist are infrastructure, not people:**
  - `pw:marker` (Markers BP 0.2.1)
  - `pw:hatch_lid` (Markers BP 0.2.1)
  - `pw:seat` (BP-02, invisible rideable seat)
- **A known interaction gap:** "villager farming AI" with our `pw:grass_block` family is listed as a remaining gap in BP-02 `pw_ground.js` l.276.
- `GuardVillager9.mcaddon` (third-party) sits on his Drive (`DRIVE-LEDGER-2026-08-23-v1` l.94). It is not ported into any pack.

## Notes

1. **Where the work stands.** The CIVITAS roadmap (`BUILD-FUTURE-v1` §7) sets the Phase 1 witness milestone as "16 villagers eat, work, rest and trade for 10 days without intervention." Nothing toward that milestone is coded. The nearest built pieces are:
   - the station data the pathing will read: the marker entities and `SEAT_BLOCKS`;
   - a world where it could be tested: the Proving Ground, still without its six premises.
2. **The keystone the roadmap named is done.** Its first recommendation was the station marker ("build this first, it unlocks everything"). That marker is built and evolved into entities. Behaviour code can now read stations from any saved building, including buildings rotated at load, which BDS proved on 10-02.
3. **Missing doc.** D-C456's plan is cited in `civgen.py` as `CIVITAS-STRUCTURE-BUILD-PLAN-2026-10-02`. No file by that name exists on disk or in outputs, so the plan lives only in chat and D-C456/D-C459.
4. **Witness backlog for CIVITAS pieces, all shipped and awaiting him:**
   - Markers 0.2.1 marker placement, hide/show and migrate (lineup 0x)
   - the ladder hatch lid probe
   - the frame-post stagger
   - furniture round 2
   - sit seats and table auto-join
   - hearth embers and sparks (1.3.188)
   - planks neighbour rule (1.3.204)
   - the cottage r1 pilot and `pw:civ` commands (1.3.205 / TestRunner 0.5.12)
5. **Sequencing law still in force** (`BUILD-FUTURE-v1` §7.1): Lifecycle (3) must not ship before Construction (4). The assembler is the scale gate. STRATEGY-v4 §12 discipline: MVV first, metabolism closed and witnessed on hardware, then one mechanism at a time.
