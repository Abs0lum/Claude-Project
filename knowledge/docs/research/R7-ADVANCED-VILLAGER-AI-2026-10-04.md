# R7 — Advanced Villager / NPC AI for CIVITAS (research report)

- **Date:** 2026-10-04 · round 1004b (D-C563, P0 research) · **status: RESEARCH ONLY, nothing built**
- **Scope:**
  - what the best villager/NPC systems do (read at source level where the code is open);
  - the exact Bedrock components and Script API levers;
  - life-sim AI theory sized for 20-60 agents;
  - answers to the open villager problems;
  - a buildable spec.
- **Evidence rule (P1):** every Bedrock claim here is static (docs, typings, vanilla JSON, mod source).
  - **[BDS-TEST]** = prove on the test server before building on it.
  - **[WITNESS]** = must be seen on his hardware.
- **Rulings honoured:**
  - D-C541: no idle villagers; every movement has a purpose.
  - D-C542: real-time work.
  - The walk module's "nothing is ever teleported". Any teleport below is an *option needing his ruling*.
  - D-C562/D-C563: our window for every villager, stricter states, flue avoidance.

---

## 0. Executive summary

- **Root cause of the roaming.** On arrival within 3 blocks, `WALK.cancel()` hands the villager back to the full vanilla `villager_v2` AI.
  - Base goals: `random_stroll` p11, `move_indoors` p6, `move_towards_dwelling_restriction` p11, `pickup_items`, `share_items`.
  - Scheduler-added goals: `explore_outskirts`, `mingle`, `work` (vanilla job-site POIs, which is the station mix-up), `sleep`.
  - **Arrival must hand control to a CIVITAS state group instead.**
- **Every strong system separates travel from action.** F.E.A.R.'s FSM has three states: Goto, Animate, UseSmartObject. MineColonies, Millénaire and MCA all reduce to: pick an activity, walk to an authored spot, act for a bounded time, re-decide.
- **Stations must be data, not vanilla POIs.** Use *position + facing + capacity + hours + what it satisfies*: Sims routing slots, Millénaire building positions, MineColonies tagged sit/stand spots.
- **Vanilla re-injects itself.** 34 of `villager_v2`'s 38 events add schedule or AI groups. Among them, the engine fires `become_<profession>` (14 events) when a villager claims a job site.
  - Guard every one with a `bool_property pw:civ` filter that re-strips instead.
- **Facing a counter or lectern is two calls:**
  - `Entity.lookAt(point)` (stable in our pinned `@minecraft/server` **2.3.0**);
  - a state group with `body_rotation_axis_aligned` + `body_rotation_blocked`. The body locks to the cardinal while `look_at_player` still turns the head.
- **Decision model.**
  - Outside: a small HFSM (WALK / STAND / SIT / TALK / SLEEP / ALARM) with a MineColonies-style interrupt list.
  - Inside: utility over station "advertisements" (Zubek / The Sims), gated by the clock's schedule window (RimWorld).
  - Activities are **committed**: re-decide only at activity end or on an interrupt (The Sims Medieval).
- **Budget.** For 60 bodies, about 11 native calls per tick. That is 0.02 ms on PC and 0.16-0.43 ms on a pessimistic phone (per-call cost assumed), against the 2 ms watchdog slow threshold.
- **Stuck recovery.** A Millénaire leaky-integrator score with a MineColonies-style escalation ladder, adapted to leads with no teleport travel: refresh lead, back up, sidestep, impulse nudge, mark edge bad, re-route, abandon and re-decide.
- **Personal space by placement.** Claims plus a 4-neighbour exclusion (Millénaire), ring slots for gatherings, queue slots at counters, and TekTopia's 12-tiles-per-occupant room rule.

---

## 1. Java mods, concretely

### 1.1 MCA Reborn, source 8.1.11+26.2

Source: [repository](https://github.com/Luke100000/minecraft-comes-alive)

- **Architecture.** Mojang's Brain with replaced task lists ([VillagerTasksMCA](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/brain/VillagerTasksMCA.java)).
  - Extra activities `CHORE` and `GRIEVE`.
  - Schedules `default / night_owl / guard / night_guard / guest` ([SchedulesMCA](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/SchedulesMCA.java)). Night owls are chosen at random (`nightOwlChance` 0.5).
  - In 26.x, schedules are `EnvironmentAttribute<Activity>`: Java moved schedules into data-driven attributes. The activity model is unchanged.
- **How it stops wandering.**
  - Move state is `MOVE`, `STAY` or `FOLLOW`. `STAY` is a CORE task ([StayTask](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/brain/tasks/StayTask.java)) that stops navigation and erases `WALK_TARGET` **every tick** unless panicking.
  - **Lesson:** a state that *lacks* movement goals beats fighting them.
- **Idle weights.** IDLE is a weighted `RunOne`:
  - talk to a female or male villager within 8 blocks (2 each), cat (1), village-bound stroll (1), walk to look target (1), jump on bed (1), `DoNothing(30-60 t)` (1).
  - Before it, `EnterFavoredBuildingTask` (priority 1) sends the villager to its mood's building.
  - Full look: cat 8, villager 2, player 2, other mob categories 1, nothing 2.
  - Busy (minimal) look: villager 2, player 2, nothing 8.
- **Mood drives place.** Seven moods across -15..+15 ([MoodGroup](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/MoodGroup.java)).
  - Depressed and sad villagers go to the **inn**; unhappy ones to the **music store**.
  - 15 personalities ([Personality](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/relationship/Personality.java)), for example sensitive (double heart loss), greedy (finds less on chores), extroverted / introverted.
  - Interaction fatigue decays every 4800 ticks.
- **Entering buildings** ([EnterBuildingTask](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/brain/tasks/EnterBuildingTask.java)).
  - Up to 16 random cells inside the building box (2-block margin).
  - Accepted only if the cell **cannot see the sky**, is a stable destination, and is collision-free.
  - Its own TODO: "positions are too random… should be floor only". That is the argument for authored stations.
- **Anti-stuck** ([WanderOrTeleportToTargetTask](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/brain/tasks/WanderOrTeleportToTargetTask.java)).
  - Path checks **staggered by `entityId % 7`**.
  - If the target is more than `villagerMinTeleportationDistance` (128, compared as squared distance) away, teleport to a cell within ±3 x/z, ±1 y that is WALKABLE, collision-free and not on the blacklist.
  - **Off by default** (`allowVillagerTeleporting=false`, [Config](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/Config.java)). Bed walks use `villagerPathfindingDistance` 80.
  - [PathfindingBlacklist](https://github.com/Luke100000/minecraft-comes-alive/blob/8.1.11%2B26.2/common/src/main/java/net/conczin/mca/entity/ai/navigation/PathfindingBlacklist.java): config blocks and tags treated as special collision. This is our flue problem, solved Java-side.
- **Chores.** CHOP / FISH / HARVEST / HUNT, player-assigned, run as their own activity.

### 1.2 Millénaire, source 6.0.2_2

Source: [repository](https://github.com/Kinniken/Millenaire)

- **Goal model.** `setNextGoal` takes the **highest `priority(villager)`** among goals that `isPossible()`, re-run when a goal ends ([MillVillager](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/MillVillager.java)). A [Goal](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/goal/Goal.java) supplies:

  | Part | Purpose |
  |---|---|
  | `isPossible()` | Day/night, stock limits, `maxSimultaneousInBuilding` / `Total` |
  | `leasure` flag | Leisure goals **abort the moment any work goal becomes possible** |
  | `getDestination()` | A point, building or entity |
  | `range()` | Default 3 |
  | `actionDuration()` | Default 500 ms |
  | `stopMovingWhileWorking()`, `shouldVillagerLieDown()` | Pin or lie down while acting |
  | `lookAtGoal()` / `lookAtPlayer()` | Where to look |
  | `allowRandomMoves()` | Default **false** |
  | `nextGoal()` | Chains goals |
  | `stuckDelay()` / `stuckAction()` | Per-goal stuck handling |

- **Goals are data files.** [makebread.txt](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/millenaire/goals/genericcrafting/makebread.txt): `buildingTag=bakery`, `priority=50`, `duration=5000`, `heldItems=wheat,bread`, `input=wheat,9`, `output=bread,3`, `buildinglimit=bread,10`, `maxsimultaneousinbuilding=1`. This is a ready template for CIVITAS station records.
- **Authored positions.** Each building has `sleepingPos / sellingPos / craftingPos / defendingPos / shelterPos / pathStartPos / leasurePos` ([BuildingResManager](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/building/BuildingResManager.java)).
  - Fallbacks: crafting to selling to sleeping.
  - Plus lists of chests, furnaces, stalls and fishing spots.
- **Pair conversations** ([GoalGoChat](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/goal/leasure/GoalGoChat.java)).
  - Finds a villager whose goal is "socialise" within 5 blocks and **takes over the partner's goal**.
  - Assigns dialogue roles 1 and 2.
  - **Only one subtitled dialogue per 5-block area.**
  - Range 2, `lookAtGoal`, priority 10.
  - [GoalGoSocialise](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/goal/leasure/GoalGoSocialise.java): walk to a leisure building's `leasurePos` (range 5, 10 s).
- **Bedless sleep** ([GoalSleep](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/goal/GoalSleep.java)).
  - Searches ±5 blocks for a bed foot block that no housemate has as their *destination* (a claim by intention).
  - Otherwise uses a **floor spot**: solid block, 2 air above, a **roof**, a second cell along the bed axis, and **no other villager's destination on the cell or its 4 neighbours**.
  - Then `shouldVillagerLieDown`.
- **Pathing.**
  - A village pathing surface with cached paths ([PathingBinary](https://github.com/Kinniken/Millenaire/blob/6.0.2_2/mill/org/millenaire/common/pathing/PathingBinary.java)).
  - JPS A* with per-goal tolerances.
- **Two-tier stuck detection** (in MillVillager):

  | Tier | Measure | Score | Action |
  |---|---|---|---|
  | Long-distance | Horizontal distance to destination | +1 per tick if not falling, else -1 | Above **3000**: jump within 4 blocks of the destination |
  | Local | Distance to the next path node | **+4** if not falling, else -1 | Above **30**: repath; above **100**: hop to the next node (doorframes) |

- **Speech.** Only when a player is within 3 blocks; 30 s cooldown.

### 1.3 TekTopia

Source: [wiki](https://sites.google.com/view/tektopia)

- **Task layers** ([Profession AI](https://sites.google.com/view/tektopia/home/mechanics/profession-ai)):
  - permanent: storage, eat, sleep;
  - universal: library, and tavern for adults;
  - profession tasks, toggled per villager.
- **Hunger follows activity** ([Hunger](https://sites.google.com/view/tektopia/home/mechanics/hunger)).
  - Walking: a 1/50 chance per tick of -1. Teacher: -1 per position change (about every 400 ticks).
  - Crafts cost by skill (bread -5 at skill 1, -2 at skill 100).
- **Happiness from probabilistic events** ([Happiness](https://sites.google.com/view/tektopia/home/mechanics/happiness)).
  - Waking +10..30; tavern sitting +1 at 1/120 per tick; home chair at night +6; damage -8; seeing a death -25..-40.
  - Work sadness is throttled to once per 200 ticks with a 1/3 chance.
- **Homes** ([Homes](https://sites.google.com/view/tektopia/home/structures/homes)).
  - One claimed bed each; always the same house.
  - **Staggered sleep times.** Guards and clerics sleep by day.
- **Overcrowding** ([Overcrowding](https://sites.google.com/view/tektopia/home/mechanics/overcrowding)).
  - **12 floor tiles per occupant**; furniture counts as tiles.
  - The penalty reaches -5 at 6 tiles per occupant; low ceilings also count.
  - Applied once per entry into the structure.

### 1.4 MineColonies, `version/main`

Source: [repository](https://github.com/ldtteam/minecolonies)

- **Priority state selection** ([CitizenAI](https://github.com/ldtteam/minecolonies/blob/version/main/src/main/java/com/minecolonies/core/entity/ai/workers/CitizenAI.java)). `decideAiTask` runs every **10 ticks**. The order:
  1. guard special case
  2. sick at hospital
  3. raid: go indoors
  4. night: SLEEP (holds 15 s if already asleep, a hysteresis)
  5. sick
  6. EAT (saturation thresholds)
  7. mourn
  8. rain: IDLE
  9. WORK, unless the citizen has leisure time
  10. IDLE

  States: `IDLE, FLEE, EATING, SICK, SLEEP, MOURN, WORK, WORKING, INACTIVE`.
- **Tick-rate state machine** ([TickRateStateMachine](https://github.com/ldtteam/minecolonies/blob/version/main/src/main/java/com/minecolonies/api/entity/ai/statemachine/tickratestatemachine/TickRateStateMachine.java)).
  - Transitions are checked in order AI_BLOCKING, then EVENT, then STATE_BLOCKING, then the current state's. The first one that fires ends the tick.
  - **Each transition has its own tick rate** (eat 20, idle decide 100, sleep walk 30).
  - A `slownessFactor` stretches all rates when TPS falls.
- **Leisure with authored seats** ([EntityAICitizenWander](https://github.com/ldtteam/minecolonies/blob/version/main/src/main/java/com/minecolonies/core/entity/ai/minimal/EntityAICitizenWander.java)).
  - IDLE `decide` every 100 ticks with a **5%** chance to visit a random leisure site.
  - It picks blueprint-tagged `sitting / sit_in / sit_out / stand_in / stand_out` spots, preferring inside in rain.
  - Seats are occupancy-checked. The citizen **rides an invisible `SittingEntity` for 30 s**.
  - Leaves at 1/300 per 20-tick check (about 5 minutes).
  - Restaurants rotate `getNextSittingPosition` ([EntityAIEatTask](https://github.com/ldtteam/minecolonies/blob/version/main/src/main/java/com/minecolonies/core/entity/ai/minimal/EntityAIEatTask.java)).
- **Stuck escalation** ([PathingStuckHandler](https://github.com/ldtteam/minecolonies/blob/version/main/src/main/java/com/minecolonies/core/entity/pathfinding/navigation/PathingStuckHandler.java)).
  - Checked every 10 ticks. "Stuck" = the next-node index has not advanced. Progress on 5 or more nodes resets.
  - Levels:

    | Level | Action |
    |---|---|
    | -5..-1 | Skip a node |
    | 0 | Clear and recalculate (200-tick delay) |
    | 1+ | Walk 20-40 blocks away in a rotating direction |
    | 2 | Teleport 6 nodes along the path (optional) |
    | 3-5 | Ladders or leaf bridges |
    | Later | Break blocks |

  - Global timeout: same destination for more than max(120 s, 7 ticks per block × distance) teleports to the destination.

### 1.5 Guard Villagers · 1.6 Human Companions · 1.7 Custom NPCs

- **Guard Villagers 4.0.4** ([Guard.java](https://github.com/seymourimadeit/guardvillagers/blob/4.0.4/src/main/java/tallestegg/guardvillagers/common/entities/Guard.java)):
  - `WalkBackToCheckPointGoal` (p3) returns the guard to a player-set post whenever its navigation is idle.
  - `GuardLookAtAndStopMovingWhenBeingTheInteractionTarget` takes MOVE and LOOK while a villager talks to it.
  - Village-bound patrol goals around workstations.
- **Human Companions** ([Java](https://github.com/justinwon777/HumanCompanions)):
  - follow / patrol / guard, plus a "sit" freeze;
  - `PatrolGoal` rejects random points beyond `radius` of the post ([PatrolGoal](https://github.com/justinwon777/HumanCompanions/blob/master/forge%201.16.5/src/main/java/com/github/justinwon777/humancompanions/entity/ai/PatrolGoal.java)); `MoveBackToPatrolGoal` tethers it home.
  - The [Bedrock port](https://www.curseforge.com/minecraft-bedrock/addons/human-companions) cycles follow → defend (stationary) → patrol (village-bound) → rest (sleeps in a free bed at night), with no vanilla entity edits.
- **Custom NPCs** ([INPCAi](https://github.com/Noppes/CustomNPCsAPI/blob/master/noppes/npcs/api/entity/data/INPCAi.java), [AnimationType](https://github.com/Noppes/CustomNPCsAPI/blob/master/noppes/npcs/api/constants/AnimationType.java)):
  - `movingType`: Standing / Wandering (1-50) / MovingPath (looping or backtracking, pauses);
  - `standingType`: RotateBody / NoRotation / Stalking / HeadRotation;
  - `stopOnInteract`, `returnsHome`, `sheltersFrom`;
  - poses: SIT, SLEEP, CROUCH, POINT, WAVE, BOW, YES, NO, …
  - This is the de-facto checklist for a "stand here" state.

### 1.8 Smaller mods in the brief

- [Easy Villagers](https://github.com/henkelmax/easy-villagers): villagers as items and blocks (trader, auto-trader, breeder, farmer) "to reduce lag". Proof that trading need not involve the mob's AI.
- [Villager Names](https://modrinth.com/mod/villager-names-serilum): 5000+ names plus custom lists. The profession appears on the **trade screen**, not in the name.
- [Better Villagers](https://modrinth.com/project/phtli6HJ): only per-block path penalties. The Java twin of `preferred_path` / `blocks_to_avoid`.
- [Villager Fix](https://www.curseforge.com/minecraft/mc-mods/villager-fix): only `mobGriefing` independence for farming.

### 1.9 Synthesis

| Technique | Who | CIVITAS equivalent |
|---|---|---|
| Activity → walk → act for a bounded time → re-decide | Millénaire, MineColonies, F.E.A.R., Sims | WALK (lead) → STAND/SIT/TALK/SLEEP with `until` |
| Authored positions with facing | Millénaire, MineColonies tags, Sims routing slots | Station registry from templates |
| Claim by intention | Millénaire, TekTopia | `claims` map checked before choosing |
| Leisure yields to work | Millénaire `leasure` | `leisure` flag; a duty window interrupts |
| Per-transition rates; TPS slowness factor | MineColonies | Staggered think; cadence stretch when `PROF` is over budget |
| Stuck score + escalation | Millénaire, MineColonies, MCA, vanilla | §3.6 ladder without teleport travel |
| Hold still by removing movement | MCA STAY, Custom NPCs Standing | STAND group: no strolls, axis-locked body |

---

## 2. Vanilla villager AI

### 2.1 Java Edition: the Brain

Sources: [Mob AI](https://minecraft.wiki/w/Mob_AI), [Villager](https://minecraft.wiki/w/Villager), decompiled 1.21.4 via [extracted_minecraft_data](https://github.com/extremeheat/extracted_minecraft_data/blob/client1.21.4/client/net/minecraft/world/entity/ai/behavior/VillagerGoalPackages.java)

- **Brain loop.** Memories can carry a TTL; sensors run every **20 ticks** with a random offset. Each tick: forget memories, run sensors, start behaviours by priority, tick the running ones.
- **Schedules** ([Schedule](https://github.com/extremeheat/extracted_minecraft_data/blob/client1.21.4/client/net/minecraft/world/entity/schedule/Schedule.java)):
  - `VILLAGER_DEFAULT`: 10 IDLE, 2000 WORK, 9000 MEET, 11000 IDLE, 12000 REST.
  - `VILLAGER_BABY`: 10 IDLE, 3000 PLAY, 6000 IDLE, 10000 PLAY, 12000 REST.
- **Core.** Swim, InteractWithDoor, LookAtTargetSink(45-90 t), PanicTrigger, WakeUp, ReactToBell, ValidateNearbyPoi (p0); MoveToTargetSink (p1); AcquirePoi job (p6), GoToPotentialJobSite (p7), YieldJobSite (p8); AcquirePoi bed and meeting point (p10).
- **Work.** A `RunOne`:
  - WorkAtPoi **7**
  - StrollAroundPoi(job, ≤4) 2
  - StrollToPoi(job, 1, ≤10) 5
  - StrollToPoiList(secondary sites) 5
  - Harvest 2/5, Bonemeal 4/7 (farmer / other)
  - Plus `SetWalkTargetFromBlockMemory(job, close 9, tooFar 100, tooLong 1200)`.
- **WorkAtPoi** ([source](https://github.com/extremeheat/extracted_minecraft_data/blob/client1.21.4/client/net/minecraft/world/entity/ai/behavior/WorkAtPoi.java)):
  - checks every **300 ticks** with a **50%** chance;
  - needs the villager within **1.73** blocks of the site;
  - sets `LOOK_TARGET` to the block (vanilla's "face the station"), plays the work sound and restocks;
  - **there is no work animation in vanilla.**
- **Strolls.**
  - StrollToPoi re-targets every 80 ticks.
  - StrollAroundPoi picks 8 × 6 every **180** ticks.
  - VillageBoundRandomStroll uses **10 × 7**.
  - InsideBrownianWalk takes 1-block steps indoors.
- **Meet, rest, idle.**
  - MEET: walk to the bell (close 6), then StrollAroundPoi(40) or **SocializeAtBell**. The latter fires at 1/100 per tick within 4 blocks, picks the nearest villager within about 5.7 blocks, walks to 1 block at speed 0.3, and both look at each other.
  - REST: home (close 1, 150, 1200), then SleepInBed (2 blocks; 100-tick cooldown after being woken).
  - IDLE `RunOne`: talk 2, breed 1, cat 1, stroll 1, walk to look target 1, jump on bed 1, nothing(30-60) 1.
- **Vanilla anti-stuck** ([MoveToTargetSink](https://github.com/extremeheat/extracted_minecraft_data/blob/client1.21.4/client/net/minecraft/world/entity/ai/behavior/MoveToTargetSink.java)).
  - When stuck: a random 0-39 tick cooldown, then retry.
  - Unreachable: set `CANT_REACH_WALK_TARGET_SINCE`, walk to an intermediate random point (10 × 7) toward the goal, and **release the POI** after `tooLong`.
  - AcquirePoi scans 48 blocks and backs off unreachable POIs (+40-tick steps).
- **POI claiming.**
  - Java: 48-block sphere; full claim within 2 blocks.
  - **Bedrock:** villagers share a list of unclaimed sites within **16 × 4 blocks**. A jobless villager *with a bed* takes the first one "regardless of the distance or accessibility" (wiki).
  - That is exactly how lecterns, anvils and smokers inside CIVITAS buildings get claimed.
- **Gossip** (per 20 minutes): trading +4 / -2 / cap 25; cure major +20 / 0 / 20 (permanent); minor negative +25 / -20 / 200; major negative +25 / -10 / 100. A ready decay model for our census rumours.

### 2.2 Bedrock Edition: `villager_v2`

Source: [bedrock-samples villager_v2.json](https://github.com/Mojang/bedrock-samples/blob/main/behavior_pack/entities/villager_v2.json) (format 1.26.20)

**Base goals (present on CIVITAS villagers today):**

| Goal | Priority | Parameters | Moves them? |
|---|---|---|---|
| float | 0 | — | yes (water) |
| hide | 0 | `poi_type: bed`, duration 30 | **yes** (bell, raid) |
| panic | 1 | speed 0.6 | yes |
| trade_with_player | 2 | — | stops navigation |
| avoid_mob_type | 4 | — | yes |
| pickup_items | 4 | max_dist 3 | **yes** |
| move_indoors | 6 | speed 0.8 | **yes** |
| look_at_trading_player | 7 | — | head only |
| look_at_player | 9 | — | head only |
| share_items | 10 | — | **yes** |
| random_stroll | 11 | speed 0.6 (xz 10 / y 7 / interval 120 defaults) | **yes** |
| move_towards_dwelling_restriction | 11 | — | **yes** |

**The scheduler.** It lives in groups (`basic_`, `work_`, `farmer_`, `fisher_`, `librarian_`, `jobless_`, `child_schedule`).
- `min_delay_secs` 0 and `max_delay_secs` 10, so every switch is jittered up to 10 s.
- Windows use `hourly_clock_time`, where 0 = sunrise.
- Workers: work 0-8000, gather 8000-10000, work 10000-11000, home 11000-12000, bed 12000-24000.
- Unemployed: the same with *wander* in place of work.

**What each schedule event adds:**

| Event | Adds |
|---|---|
| work | `behavior.work` p7: `active_time` 250, `goal_cooldown` 200, speed 0.5, `on_arrival: minecraft:resupply_trades` |
| gather | `mingle` p7: duration 30, cooldown 10, distance 2 |
| wander | `explore_outskirts` p9: `explore_dist` 6, `max_wait_time` 10 |
| bed | `sleep` p3: collider 1 × 0.3, y-offset 0.6 |
| home | **nothing**, so only the base goals act |

**Paths.** The `adult` group carries `preferred_path`:
- `default_block_cost` 3, `jump_cost` 20, `max_fall_blocks` 1;
- `grass_path` 0, 139 stone-like blocks 1, **beds and job-site blocks 50**;
- CIVITAS `pw:` road blocks are unlisted, so they cost 3, the same as grass.

**Re-injection.** 34 of 38 events add schedule or AI groups. The engine-fired ones are the dangerous kind:
- `become_<profession>` ×14 (job-site claim), which adds `work_schedule` and its siblings;
- `ageable_grow_up`, `entity_spawned`, `spawn_from_village`, `entity_born`, `entity_transformed`.

`make_and_receive_love` (`make_love` p5 / `receive_love` p6) is added by **30** events: every schedule event except bed and play, every `become_*`, and the spawn and grow-up events. Vanilla breeding would create babies outside the census.

### 2.3 Bedrock component reference

All rows come from Microsoft Learn sources ([MicrosoftDocs/minecraft-creator](https://github.com/MicrosoftDocs/minecraft-creator)), fetched 2026-10-04. Defaults are in brackets.

| Component | Parameters [default] / note |
|---|---|
| [random_stroll](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_random_stroll) | `interval` [120] = "a 1/interval chance to choose this goal"; `xz_dist` [10], `y_dist` [7], at least 1 each |
| [work](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_work) | `active_time`, `goal_cooldown`, `can_work_in_rain`, `on_arrival`, `speed_multiplier` [0.5]. Targets **vanilla job-site POIs**. |
| [sleep](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_sleep) | `sleep_collider_height/width`, `sleep_y_offset`, `timeout_cooldown` [8]. Needs an owned bed. |
| [explore_outskirts](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_explore_outskirts) / [mingle](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_mingle) / [move_to_village](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_village) | Village-bound wandering, bell mingling, travel to a village. Need `dweller`. |
| [move_indoors](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_indoors) / [hide](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_hide) | `speed_multiplier` [0.8], `timeout_cooldown` [8] / `poi_type` (bed, jobsite, meeting_area), `duration` |
| [look_at_player](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_look_at_player) / [look_at_entity](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_look_at_entity) | `look_distance` [8], `look_time` {2, 4}, `probability` [0.02], angles [360]. look_at_entity rotates **the head bone only**; 1.26 replaced `min/max_look_time` with `look_time`. |
| [random_look_around](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_random_look_around) / [_and_sit](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_random_look_around_and_sit) | `look_time` {20, 40}, `probability` [0.02] / look counts 1-2; needs a sit animation |
| [follow_mob](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_follow_mob) | `search_range`, `stop_distance` [2], `speed_multiplier`, `preferred_actor_type`, `filters`, `use_home_position_restriction`. Ours: 0.8 / 1.1, filtered on `pw:slot`. |
| [move_to_block](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_block) | `target_blocks`, `target_block_filters`, `target_selection_method` (nearest/random), `target_offset`, `goal_radius` [0.5], `tick_interval` [20], `stay_duration`, `on_reach`, `on_stay_completed`. Cannot address one villager's station. |
| [move_to_poi](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_to_poi) | `poi_type` |
| [home](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_home) + [move_towards_home_restriction](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_towards_home_restriction) | `restriction_radius`, `restriction_type` (none / random_movement / all_movement; format 1.21.40+), `home_block_list`. Home is saved "when the entity is spawned". |
| [dweller](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_dweller) + [move_towards_dwelling_restriction](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_move_towards_dwelling_restriction) | `can_find_poi`, `can_migrate`, `dwelling_role`, `preferred_profession`, `update_interval_base/variant` (vanilla 60 / 40). The POI-claiming engine. |
| [timer_flag_1](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_timer_flag_1) (also 2, 3) | `duration_range`, `cooldown_range`, `on_start`, `on_end`. `query.timer_flag_1` is true while running. An engine-side timed act. |
| [stay_near_noteblock](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_stay_near_noteblock) | `listen_time` [30], `start/stop_distance` [10/2]. Allay-style beacon; crude. |
| [panic](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_panic) / [trade_with_player](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitygoals/minecraftbehavior_trade_with_player) | `damage_sources`, `force`, `ignore_mob_damage` / `max_distance_from_player` [8]; "stops the mob's navigation" |
| [navigation.walk](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Reference/Content/EntityReference/Examples/EntityComponents/minecraftComponent_navigation.walk.md) | `avoid_water/sun/portals/damage_blocks`, `can_open_doors`, `can_pass_doors` [true], `can_open_iron_doors`, `can_jump`, `can_path_over_water`, `is_amphibious`, `using_door_annotation`, **`blocks_to_avoid`**: ids or `{ "tags": "query.any_tag('…')" }`. The vanilla breeze avoids `query.any_tag('trapdoors')`. |
| [preferred_path](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_preferred_path) | `default_block_cost`, `jump_cost`, `max_fall_blocks`, `preferred_path_blocks` [{`blocks`: names or `{name, states, tags}`, `cost`}] |
| [pushable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_pushable) | Split in **1.26.10** into `pushable_by_block` and `pushable_by_entity`. Our villager already uses the pair. |
| [leashable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_leashable) | `presets` [{`filter`, `soft_distance`: "starts pathfinding toward the leash holder", `spring_type`}]. The rope renders. |
| [rideable](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_rideable) | `family_types`, `seats` [{`position`, `lock_rider_rotation`, `rotate_rider_by`}], `on_rider_enter_event` / `exit` (1.21.80) |
| [body_rotation_blocked](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_body_rotation_blocked) (1.20.80), [body_rotation_axis_aligned](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_body_rotation_axis_aligned), [body_rotation_always_follows_head](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_body_rotation_always_follows_head) (1.21.90), [rotation_locked_to_vehicle](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_rotation_locked_to_vehicle) (1.21.130) | axis_aligned + blocked: "align to the nearest cardinal direction and remain fixed in that orientation" |
| [scheduler](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/entitycomponents/minecraftcomponent_scheduler) | `min/max_delay_secs`, `scheduled_events`. Filters: [hourly_clock_time](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/filters/hourly_clock_time) (0-24000), `clock_time`, `is_daytime`. |

**Two engine rules that shape the design:**
- **Deferred events.** Event effects "are not applied to the entity until the entity ticks on the server side" ([Entity Events](https://learn.microsoft.com/en-us/minecraft/creator/documents/entityevents)). Likewise `setProperty` "is not applied until the next tick".
- **Last group wins.** "If a currently active component group has the same component inside it, it will be overwritten by the group most recently added" ([bedrock.wiki Entity Events](https://wiki.bedrock.dev/entities/entity-events)).
  - Whether removing that group restores a base copy is undocumented. **[BDS-TEST H1]**
  - Rule until proven: no movement-critical component in both base and a group. Each state group carries its own full copy.

---

## 3. Bedrock techniques for precise control

### 3.1 Every known way to walk a mob somewhere

| Method | Precision | Script cost | Verdict |
|---|---|---|---|
| **Lead + `follow_mob`** (ours: `pw:lead`, int `pw:slot` filter, 48 slots) | ~1 block | 1 lead move per walker per 10 ticks | **Keep.** 0.0.25b: 224 arrived / 25 stuck; 0.0.25c city: 723 / 105. |
| Marker + `nearest_attackable_target` (`must_see: false`) + `melee_attack` (`require_complete_path`) + `target_nearby_sensor` `on_inside_range` for arrival ([bedrock.wiki Entity Movement](https://wiki.bedrock.dev/entities/entity-movement)) | ~1 block | 1 marker move | Gives an **engine arrival event**. Hostile posture risk. **[BDS-TEST]** only if needed. |
| `move_to_block` on marker blocks | Nearest match | 0 | Good for "any free bench"; not for one villager's counter |
| `move_to_poi` / `work` / `sleep` | Vanilla | 0 | **The mix-up mechanism.** Avoid. |
| Leash presets (`leashTo`) | Rope | Low | Visible rope. No. |
| `tp ^^^0.1` stepping (bedrock.wiki tip) | Exact | 20 teleports per second per villager | Violates "nothing teleported". No. |
| GameTest `Test.walkTo` ([Learn](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server-gametest/test?view=minecraft-bedrock-experimental)) | Exact | — | Only inside a running test. No. |

Lead entity build per [bedrock.wiki Dummy Entities](https://wiki.bedrock.dev/entities/dummy-entities): no damage, not pushable, tiny collision, no gravity. `pw:lead` already matches.

### 3.2 Script API levers

All verified in the **2.3.0** typings (BP-02's pin) from [npm](https://www.npmjs.com/package/@minecraft/server); latest stable is 2.10.0.

| Lever | Use |
|---|---|
| `lookAt(target)` | Pitch = head tilt, yaw = **body** ([Entity](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/entity)) |
| `setRotation({x, y})` | Direct pitch / yaw |
| `teleport(loc, {facingLocation, rotation, keepVelocity, checkForBlocks})`, `tryTeleport()` | `tryTeleport` returns false when blocked or unloaded ([TeleportOptions](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/teleportoptions)) |
| `applyImpulse`, `applyKnockback`, `clearVelocity` | Teleport-free nudges |
| `triggerEvent` / `setProperty` | Both apply on the entity's next tick |
| Entity properties | Up to **32** per type; enums **≤16** values of ≤32 characters ([properties doc](https://github.com/MicrosoftDocs/minecraft-creator/blob/main/creator/Documents/IntroductionToEntityProperties.md)); `client_sync` needed for the RP ([bedrock.wiki](https://wiki.bedrock.dev/entities/entity-properties)) |
| `playAnimation(name, {controller, nextState, blendOutTime, stopExpression, players})` | The animation must exist in the RP |
| `EntityRideableComponent.addRider`, `EntityLeashableComponent.leashTo`, `getComponent('minecraft:movement').setCurrentValue()` | Seating, leashing, pinning |
| `world.beforeEvents.playerInteractWithEntity` with `cancel = true` | Blocks the vanilla trade UI ([Learn](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/playerinteractwithentitybeforeevent)) |
| `world.afterEvents.dataDrivenEntityTrigger` | Observe engine-fired events (catch `become_*`) |
| `system.runJob` | "every generator … at least 1 iteration every tick" ([system run guide](https://learn.microsoft.com/en-us/minecraft/creator/documents/systemrunguide)) |

**Watchdog** ([bedrock.wiki](https://wiki.bedrock.dev/scripting/script-watchdog)): slow above **2 ms** average, spike **100 ms**, hang **3000 ms**. Brain target: ≤ 0.5 ms per tick on average.

### 3.3 Component groups and events: patterns that work

1. **Exclusive switch.** Each state event removes *all* civ state groups and adds one. Never read back in the same tick (deferral).
2. **Strip once, guard forever.** The enrol event strips the vanilla AI. Every vanilla event that can re-add it becomes a guarded `sequence` (fragment):

```json
"minecraft:become_librarian": {
  "sequence": [
    { "filters": { "test": "bool_property", "domain": "pw:civ", "value": true }, "trigger": "pw:civ_resync" },
    { "filters": { "test": "bool_property", "domain": "pw:civ", "value": false },
      "add":    { "component_groups": [ "…vanilla adds, copied verbatim…" ] },
      "remove": { "component_groups": [ "…vanilla removes, copied verbatim…" ] } }
  ]
}
```

   - The branches are mutually exclusive, so "sequence entries are not exclusive" is harmless.
   - Use a **property** (defined in the file, Molang-readable, [filter doc](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/entityreference/examples/filters/bool_property)) for the guard. Tags stay the query keys (`civ:person:N`).
3. **Backstop.** `dataDrivenEntityTrigger` on `minecraft:become_*` for civ bodies fires `pw:civ_resync` and logs the slip.
4. **Navigation per state.** Each state group carries its own full `navigation.walk`. Street legs use `can_open_doors: false`; legs into a permitted building use `true`. Doors become permissions.
5. **Engine timers.** `timer_flag_1` (`duration_range`, `on_end`) gives work-cycle cadence with no script ticks, and feeds `query.timer_flag_1` to the RP.

### 3.4 Poses and "using a station"

- One client-synced enum `pw:act` with 16 values:
  - `none, work, hammer, stir, read, write, sell, chop, pick, carry, sweep, pray, talk, sit, lie, nod`.
  - The RP controller has one state per value (transition `q.property('pw:act') == 'hammer'`) and loops arm and head bones.
  - Or skip the controller: `playAnimation('animation.villager.pw_hammer', {stopExpression: "q.property('pw:act') != 'hammer'"})`.
- **Zero-RP fallback (hypothesis):** alternate two `lookAt` targets ±0.35 block in height every 10-20 ticks to make the head nod while `body_rotation_blocked` holds the body. **[BDS-TEST/WITNESS H7]**
- Add the existing work sounds and particles, and an optional held tool through `runCommand('replaceitem entity @s slot.weapon.mainhand 0 <item>')`. **[BDS-TEST H6]**

### 3.5 Time-of-day: script clock, not `minecraft:scheduler`

- The vanilla scheduler is jittered 0-10 s and knows nothing of stations, census or Sunday rest.
- **Civ villagers get no scheduler.** The clock's windows drive them (today `SCHED.work [1000, 11000]`, `dusk [11000, 13000]`; R5 adds dawn-to-dusk and Sunday rest).
- Stagger every window edge per person by ±600 ticks derived from the person id, as TekTopia staggers sleep, so the town never moves on one tick.

### 3.6 Anti-stuck ladder for lead walkers (no teleport travel)

**Detect.** On each think (20 ticks):
- `progress = prevDist − dist`, where `dist` is measured to the **current route cell**.
- `stuck += progress < 0.25 ? 4 : −1`, clamped at 0 or above (Millénaire).

**Escalate:**

| Score | Action | Analogue |
|---|---|---|
| ≥ 8 | Re-place the lead on the current cell; check doors | MineColonies level 0 |
| ≥ 16 | Back the lead up 1 cell, then return (re-take the corner) | Millénaire local repath |
| ≥ 24 | **Sidestep:** lead 1 block perpendicular for one beat | MineColonies "move away", scaled down |
| ≥ 32 | **Nudge:** `clearVelocity` + `applyImpulse` ≈ 0.12 toward the next cell (+0.42 y for a step) **[H5]** | Doorframe hop without a teleport |
| ≥ 40 | Edge marked **bad for 1 village day**; re-route | Vanilla retry / `CANT_REACH` |
| ≥ 60, or 600 t without net progress | **Abandon:** release the claim, station on a 5-minute cooldown, re-decide | Vanilla POI release |
| Option (his ruling) | `tryTeleport` ≤ 1 block onto the next cell, a "settle" | Millénaire hop above 100 |

Log the cause of each escalation (`below / above / level / door / crowd / edge`), extending the existing `stuckBy` counters.

---

## 4. Needs and utility AI for 20-60 agents

### 4.1 Choosing the architecture

| Approach | Fit at our scale | References |
|---|---|---|
| FSM / HFSM | Cheap and debuggable; maps onto component groups | [Dill](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter05_Structural_Architecture_Common_Tricks_of_the_Trade.pdf); F.E.A.R.: "only three states… Goto, Animate, and UseSmartObject" ([Orkin](https://www.gamedevs.org/uploads/three-states-plan-ai-of-fear.pdf)) |
| Behaviour tree | Reactive, but re-ticking trees per body per tick wastes JS time | [Francis](https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter09_Overcoming_Pitfalls_in_Behavior_Tree_Design.pdf); [Bungie on Halo AI](https://www.gamedeveloper.com/game-platforms/in-depth-bungie-on-eight-years-of-i-halo-i-ai) |
| Utility / needs | Emergent and tunable; needs inertia | [Zubek](https://robert.zubek.net/publications/Needs-based-AI-draft.pdf); [Graham](https://www.gameaipro.com/GameAIPro/GameAIPro_Chapter09_An_Introduction_to_Utility_Theory.pdf); [Lewis](https://www.gameaipro.com/GameAIPro3/GameAIPro3_Chapter13_Choosing_Effective_Utility-Based_Considerations.pdf) |
| GOAP / HTN | Overkill; our chains are fixed recipes | Orkin |
| Schedule-gated needs | Timetable blocks gate which needs may fire | RimWorld [JobGiver_GetRest](https://github.com/josh-m/RW-Decompile/blob/master/RimWorld/JobGiver_GetRest.cs) |

**Verdict.**
- An HFSM of engine states with an interrupt list.
- Utility over advertisements inside it, gated by the schedule window.
- **Committed activities.** Graham: "On The Sims Medieval, a Sim would only attempt to make a decision when their interaction queue was empty."
- Fixed recipe chains, like Millénaire `nextGoal`.

### 4.2 Needs (three)

- **energy** (0-100). About -4.5 per waking hour, +12 per sleeping hour.
  - Thresholds **28 / 14**, from RimWorld `ThreshTired 0.28`, `ThreshVeryTired 0.14` ([Need_Rest](https://github.com/josh-m/RW-Decompile/blob/master/RimWorld/Need_Rest.cs)).
  - RimWorld's rest priority is 8 inside an "Anything" block below 0.3, 0 in a "Work" block, and in a "Sleep" block below `FallAsleepMaxLevel` 0.75.
- **hunger.** About -3 per hour, faster during labour (TekTopia). "Hungry" and "urgent" sit at 80% and 40% of the want-to-eat level ([Need_Food](https://github.com/josh-m/RW-Decompile/blob/master/RimWorld/Need_Food.cs)).
- **social.** About -2 per hour, scaled by personality. Filled by TALK, the inn and church.
- **duty** (pseudo-need). Inside a work window, the person's own station advertises duty +60.
- **Lazy decay.** Store `{value, tick}` and compute on think.
- **D-C541.** Needs only choose *which purposeful activity* fills non-duty time (eat, rest at a home chair, talk at the square, pray, read). They never create aimless time.

### 4.3 Stations as advertisements

Each station advertises what it satisfies. Objects "advertise a set of action/reward tuples" (Zubek), and "routing slots" put the actor on the right spot and facing ([Forbus & Wright](https://users.cs.northwestern.edu/~forbus/c95-gd/2001/Programming%20Objects%20in%20The%20Sims.pdf)). [Stardew schedule points](https://stardewvalleywiki.com/Modding:Schedule_data) carry the same shape: `<time> [location] <x> <y> [facing] [animation]`.

```js
{ key: "b42:counter:0", building: 42, kind: "sell",          // work|sell|read|sit|sleep|eat|talk|pray|gather|queue
  pos: {x, y, z}, yaw: 90, faceAt: {x, y: y + 1.2, z},        // feet cell + what to look at
  cap: 1, queue: [{x, y, z, yaw}],                             // service slot + waiting slots
  hours: [1000, 11000], roles: { job: 42 },                    // open window; who may use it
  ad: { duty: 60, social: 5, energy: -2 },                     // advertised deltas
  act: "sell", dur: [1200, 2400], leisure: false }             // pw:act; committed ticks
```

### 4.4 Scoring

- **Attenuated need delta (Zubek):** `score = Σₙ [Aₙ(needₙ) − Aₙ(min(100, needₙ + adₙ))] + duty·W(window)`, with piecewise-linear `Aₙ`.
- **Multiplicative vetoes, cheapest first (Lewis):** closed, role mismatch, full, cooldown.
- **Inertia** ×1.15 on the previous station (Graham §9.7), plus cooldowns.
- **Mild distance** `1/(1 + d/48)`. Zubek warns strong distance attenuation causes "bird in hand" behaviour.
- **Personality multipliers per need**, from the census.
- **Weighted pick from the top 3** (Zubek: "a good compromise between … predictability … and not … unpleasantly deterministic").

### 4.5 Occupancy, queues, personal space

- **Claims** (`st.claims`) by intention at decision time, released on abandon or end.
- **Queues.** If a station is full, take a queue slot facing it. If the queue is full, the score is 0 and the next activity wins.
- **Cells** (`st.cells`). A free stand cell has **no other claim on itself or its 4 neighbours** (Millénaire). Reynolds' separation ("maintain a certain separation distance from others", [Steering Behaviors](https://www.red3d.com/cwr/papers/1999/gdc99steer.pdf)) becomes a placement constraint with zero per-tick cost.
- **Gatherings** (dusk square, church, inn): ring slots at radius 3 / 4.5 / 6, spaced at least 1.6 blocks apart, facing the centre.
- **Rooms.** TekTopia's 12 tiles per occupant: a full room stops advertising.

### 4.6 Micro-behaviours (only inside a committed activity)

- **Glance:** `look_at_player` (look_distance 6, probability 0.03).
- **Turn:** every 40-100 ticks, re-face the station or briefly `lookAt` a neighbour (vanilla LookAtTargetSink lasts 45-90 ticks).
- **Shift:** one 1-block step to a free neighbour slot every 30-60 s while queueing or gathering.
- **Sit** on `pw:seat_v` (§5.4). **Gesture** through `pw:act`.

### 4.7 Pair conversations

Millénaire GoalGoChat combined with vanilla SocializeAtBell:
1. Scan each settlement every 100 ticks for leisure or gather bodies with social below 70, no pair cooldown, within 6 blocks of each other.
2. The initiator **locks** the partner: its activity is dropped and its claim transferred.
3. Both walk to free cells 2 blocks apart, `lookAt` each other's eyes (y + 1.62), and set `pw:act = "talk"`.
4. 6-15 s. Social +12..+20 is granted **on completion** (Zubek: rewards come from finishing, so interruptions earn nothing).
5. They exchange one census rumour, like vanilla gossip. **One** subtitle per 8-block area, shown as an action-bar line to players within 6 blocks.
6. Pair cooldown 3-6 minutes.

### 4.8 Decision loop (pseudo-code)

```js
const THINK = 20;                                             // each body thinks once per second, staggered
system.runInterval(prof("brain", () => {
  const t = system.currentTick;
  for (const st of settlementsWithBodies()) {
    const bodies = bodyCache(st, t);                          // ONE getEntities per settlement per 20 t, shared by all modules
    for (const b of bodies) if ((b.slot + t) % THINK === 0) think(st, b, t);
  }
}), 1);

function think(st, b, t) {
  const v = b.entity; if (!v.isValid) return dropBody(st, b);
  const p = v.location;
  decayNeeds(b, t);                                           // lazy
  const irq = interrupt(st, b, p, t);                         // ALARM > window edge > need crisis
  if (irq) return begin(st, b, irq, t);
  switch (b.state) {
    case "WALK":  return tickWalk(st, b, p, t);               // route, stuck ladder, arrival -> enter(act)
    case "TALK":  if (!b.partner?.entity?.isValid) return finish(st, b, t);
    // falls through
    case "STAND": case "SIT": case "SLEEP":
      if (dist2(p, b.anchor) > 2.25) return recover(st, b, p, t);  // displaced > 1.5 (panic, push, water)
      if (t >= b.act.until) return finish(st, b, t);                // reward here, then decide()
      return micro(st, b, t);                                       // glance / turn / shift, rate-limited
  }
}

function decide(st, b, t) {                                    // only at activity end or interrupt
  const win = windowOf(st, t, b.offset);
  const top = [];
  for (const a of candidates(st, b, win)) {                    // open, role-matched, off cooldown
    if (!slotFree(st, a)) continue;
    let s = 0;
    for (const n of NEEDS) s += A[n](b.needs[n]) - A[n](Math.min(100, b.needs[n] + (a.ad[n] || 0)));
    s += (a.ad.duty || 0) * dutyWeight(win, b);
    s *= persona(b, a) / (1 + a.walk / 48);
    if (a.key === b.lastKey) s *= 1.15;
    if (s > 0) keepTop3(top, s, a);
  }
  const pick = weightedPick(top) || homeFallback(st, b);
  claim(st, pick, b, t);
  return begin(st, b, { kind: "go", station: pick }, t);       // WALK; on arrival STAND|SIT|SLEEP
}
```

### 4.9 Per-tick cost

The model was computed in Python. Counts are exact for the design; per-call cost is assumed and should be replaced with `PROF` data.

| Item (60 bodies) | Per tick | Calls each |
|---|---|---|
| Thinks | 3.0 | 2 |
| Lead updates (1/3 walking, every 10 t) | 2.0 | 2 |
| Micro-actions (2/3 standing, every ~70 t) | 0.57 | 1 |
| Decisions (60 s activities) | 0.05 | 3, plus 72 multiply-adds |
| Pair-scan distance checks | 1.05 | 0 (cached) |
| Body cache | 0.05 | 1 |
| **Total** | — | **≈ 10.8** |

- At an assumed 2 / 15 / 40 µs per call: **0.02 / 0.16 / 0.43 ms per tick**, against the 2 ms watchdog slow threshold.
- At 40 µs, the 0.5 ms budget holds up to about 69 bodies.
- The real hot spots stay in route and leg building (the profiler's 100-400 ms bursts). Move them into `runJob`.

---

## 5. Specific answers

### 5.1 Stop the wandering between tasks

- **Mechanism today.** `WALK.cancel()` at 3 blocks; the vanilla goals in §2.2 resume.
- **Fix.** Arrival **enters a civ state group with no stroll goals**. Remove vanilla goals; do not out-prioritise them.
- **Movement 0 vs removing goals.**
  - Removing goals stops self-initiated travel but keeps panic and avoidance (safety).
  - `movement` 0 freezes *all* locomotion, including fleeing; goals still run and can still turn the body.
  - Use movement 0 only for SLEEP and pinned scripted moments.

| Still moves them | Answer |
|---|---|
| `panic` p1, `avoid_mob_type` p4 | Keep. The anchor displacement check (> 1.5) re-walks them back. |
| `float`, water currents | Keep `float`; same recovery; keep stations out of water (flood fix). |
| `pushable_by_entity` | **Loose states only** (WALK). STAND / SIT / TALK / SLEEP omit it and add `knockback_resistance` 1.0. |
| `hide` p0 (`poi_type: bed`) | Move to `vanilla_ai`. Use the script ALARM state instead (home by lead, STAND inside). |
| `move_towards_dwelling_restriction` | Remove for civ (cities exceed vanilla village bounds). |
| `trade_with_player` | Remove for civ. Cancel every civ interaction in `beforeEvents` (counter or talk window). |
| Scheduler + `become_*` events | Strip all `*_schedule` groups at enrol, then the §3.3 guards. |
| `dweller` (`can_find_poi`) | Keep the component (profession skins are entangled). Add `can_find_poi: false` and `can_migrate: false` in a civ group **[H2]**, with the guard as backstop. |

### 5.2 Keep them out of wrong buildings and rooms

1. **Tag avoidance:** `blocks_to_avoid: [{ "tags": "query.any_tag('pw_no_villager')" }]`.
   - Tag every `pw:flue_*`, hearth, chimney cap, well shaft and private-room threshold. This replaces a 53-id list. **[H8]**
   - Mirror it in the script A* blocked set, because the lead is placed by script.
2. **Doors as permissions:** `can_open_doors` only in WALK legs whose destination the person may enter (home, workplace, shop as customer, inn, church).
   - Private rooms sit behind doors those states cannot open, or behind trapdoor or gate thresholds (villagers cannot open trapdoors, fence gates or iron doors, per the wiki).
3. **Cheaper streets:** CIVITAS road and sidewalk blocks at `preferred_path` cost 0-1 (by tag), `default_block_cost` ≈ 4, beds and job sites 50.
4. **Zone check per think:** a body inside a building it has no business in, and not walking to a permitted station, gets `recover()` toward the nearest permitted exit.
5. **Flue (D-C562):** the engine path is covered by (1) and the lead path by the script blocked set. The player hazard law is untouched.

### 5.3 Face a block, lectern or counter

```js
v.lookAt(station.faceAt);            // yaw -> body, pitch -> head (2.3.0 stable)
v.triggerEvent("pw:civ_stand");      // adds body_rotation_axis_aligned + body_rotation_blocked
```

- The body snaps to the cardinal and stays; the head stays free, so `look_at_player` greets customers. Station yaws should be cardinal (counters and lecterns are).
- **Off-cardinal spots** (ring slots): `body_rotation_blocked` alone after `lookAt`. **[H3]**
- `teleport(sameLoc, {facingLocation})` also works but is a teleport call; prefer `lookAt`.
- A look-marker with `look_at_entity` turns only the head bone.
- **Lectern (D-C562):** the speaker's station `faceAt` = the lectern top, so the villager faces the book however the block is rotated. The block facing itself is fixed in the template / `fixDirections`.

### 5.4 Sleep without vanilla beds (and sit)

- Do not use `behavior.sleep`: it needs owned vanilla beds and the dwelling, the systems we are removing.
- **SLEEP state:**
  1. Claim a bed station (`kind: "sleep"`, head cell, yaw).
  2. Walk there by lead, then `lookAt` along the bed axis.
  3. `pw:civ_sleep` holds: `movement` 0, `collision_box` 0.6 × 0.3 (like vanilla's `sleep_collider_height` 0.3), no `pushable_by_entity`, `body_rotation_blocked`, no look goals.
  4. `pw:act = "lie"` drives an RP lie animation adapted from [bedrock.wiki Sleeping Entities](https://wiki.bedrock.dev/entities/sleeping-entities) (body −90° plus offset).
- **Precision.** The lead stops within about 0.8 block. Exactly-on-the-mattress needs a ≤ 0.75-block `tryTeleport` settle, **which is a teleport and needs his ruling**. Otherwise the pose plays where the villager stopped.
- **No free bed:** use the Millénaire floor rule (solid floor, 2 air above, roof, second cell along the yaw, 4-neighbour exclusion).
- **Wake** on the person's staggered window edge, on damage (a `damage_sensor` event in the group, as bedrock.wiki does), or on ALARM.
- **Sitting:** `pw:seat_v` = `pw:seat` with `family_types: ["villager"]`, plus `rideable.addRider(villager)` and `rotation_locked_to_vehicle` in the SIT group **[H4]**. MineColonies seats citizens the same way, on an invisible `SittingEntity`.

### 5.5 Visibly "use" a station

- Map station kinds to `pw:act` (§3.4):
  - counter `sell` (gestures, nod at the customer), lectern `read`, anvil `hammer` (arm arc every 0.6 s);
  - oven `stir`, desk `write`, quarry face `pick`, stump `chop`, altar `pray`.
- Add the existing sounds and particles at the act's rhythm, plus an optional held tool.
- Optional engine cadence: `timer_flag_1` (`duration_range` [8, 14]) whose `on_end` fires `pw:act_cycle`, observed via `dataDrivenEntityTrigger`.
- **D-C542:** the act *is* the work. A block, loaf or sale happens only on an act tick of a body at the face, oven or counter.

---

## 6. Recommended specification

### 6.1 State machine

```
                        ┌──────── interrupt: hostile ≤10 / bell / fire ────────┐
                        ▼                                                      │
 [ENROL] ─► DECIDE ─► WALK(lead) ─arrive─► STAND(act) ┐                        │
             ▲  ▲       │  ▲                SIT(act)  ├─ displaced>1.5 ─► WALK │
             │  │       │  └─stuck ladder─┘ TALK(pair)│                        │
             │  │       └─ abandon(≥60) ─► DECIDE      SLEEP(lie) ┘            │
             │  └──────── until reached / pair ends / window edge ─────────────┤
             └──────────────────── ALARM (walk home, STAND inside) ◄───────────┘
```

- **No aimless IDLE** (D-C541). Free time is a leisure activity at a leisure station.
- WORK = STAND or SIT at a duty station with a work act. QUEUE = STAND at a queue slot.

### 6.2 Group layout (`villager_v2` override)

**BASE** (every villager):
- type_family, health, breathable, nameable, inventory, equipment, mark_variant, physics, `jump.static`, `movement.basic`, `can_climb`, `movement` 0.5, `annotation.open_door`;
- `float` p0, `panic` p1, `avoid_mob_type` p4, `look_at_player` p9;
- `pushable_by_block`, `damage_sensor`, `persistent`, `conditional_bandwidth_optimization`;
- the default `navigation.walk`.

**`minecraft:vanilla_ai`** (moved out of base; added on every vanilla spawn path; never on civ):
- `random_stroll`, `move_indoors`, `move_towards_dwelling_restriction`, `hide` + `minecraft:hide`, `trade_with_player`, `look_at_trading_player`, `pickup_items`, `share_items`, `pushable_by_entity`.

| Civ group | Contents | When |
|---|---|---|
| `pw:civ_base` | `preferred_path` (civ roads by tag 0, default 4, jump 20, beds and job sites 50); `dweller` override `can_find_poi: false`, `can_migrate: false` **[H2]**; `random_look_around` p10 | Always (civ) |
| `pw:civ_walk` / `pw:civ_walk_in` | Full `navigation.walk` civ profile (`blocks_to_avoid` tag `pw_no_villager`; `can_open_doors` false / true); `pushable_by_entity` | WALK legs |
| `pw:lead_N` (existing 48 + generic) | `follow_mob` p0 filtered on `pw:slot`; movement 0.5 | WALK |
| `pw:civ_stand` | `body_rotation_axis_aligned`, `body_rotation_blocked`, `knockback_resistance` 1.0, `navigation.walk` (no doors) | STAND / QUEUE / WORK |
| `pw:civ_talk` | `body_rotation_blocked`, `knockback_resistance` 1.0 | TALK |
| `pw:civ_sit` | `rotation_locked_to_vehicle`, `knockback_resistance` 1.0 | SIT |
| `pw:civ_sleep` | `movement` 0, `collision_box` 0.6 × 0.3, `body_rotation_blocked`, `damage_sensor` (wake) | SLEEP |

**Properties** (`villager_v2` has none today): `pw:civ` (bool, false); `pw:act` (enum, 16, `client_sync`); optionally `pw:mood` (int 0-4, `client_sync`).

### 6.3 Events

| Event | Action |
|---|---|
| `pw:civ_enroll` | Remove `vanilla_ai`, all `*_schedule`, `work_schedule_*`, `wander/gather/home/bed/play_schedule_villager`, `job_specific_goals`, `make_and_receive_love`, `trade_resupply_component_group`. Add `pw:civ_base` + `pw:civ_stand`. `set_property {pw:civ: true}`. |
| `pw:civ_resync` | The same removals only. Used by guarded events. |
| `pw:civ_state_walk / walk_in / stand / talk / sit / sleep` | Remove every other state group; add one. |
| `pw:lead_on_N` / `pw:lead_off` | Existing. Fire with walk / walk_in. |
| `pw:civ_release` | Un-enrol: civ groups out; `vanilla_ai`, `basic_schedule`, `jobless_schedule` in; `pw:civ` false. |
| Guarded vanilla events | Every vanilla event that can add schedule or AI groups gets the §3.3 guard: `become_*` ×14, `ageable_grow_up`, `entity_spawned`, `spawn_from_village`, `entity_born`, `entity_transformed`, `spawn_*`, `schedule_*`, `resupply_trades`. Vanilla spawn paths also **add `minecraft:vanilla_ai`**, so wild villagers keep vanilla life. |

### 6.4 Script cadence

| Loop | Period | Note |
|---|---|---|
| Brain think | every tick, stagger `(slot + t) % 20` | Once per second per body |
| Lead update | 10 t per walker | Existing BEAT |
| Decide | Event-driven | Activity end / interrupt / staggered window edge |
| Pair scan | 100 t per settlement | O(k²), k ≤ 20 |
| Clock sync | 100 t (existing beat) | Becomes the window publisher; stops `WALK.send` for brain-owned bodies |
| Station registry | On building completion | `system.runJob` |
| Profiler gate | 200 t | If `PROF.brain` > 0.5 ms per tick, set THINK = 40 (MineColonies `slownessFactor`) |

### 6.5 Data per villager

The runtime Map is keyed by entity id. The persisted subset goes in one dynamic property, ≤ 160 B.

```js
{ pid: 17, eid: "-4294967291", st: 3, slot: 33, state: "STAND", since: 182400, offset: -240,
  act: { kind: "sell", key: "b42:counter:0", until: 184800, leisure: false, reward: { duty: 60, social: 5 } },
  anchor: { x: 101.5, y: 64, z: -22.5, yaw: 90, face: { x: 102.5, y: 65.2, z: -22.5 } },
  needs: { energy: 71, hunger: 54, social: 38, t: 182400 }, persona: { social: 1.3, pray: 1.0, hunger: 1.0 },
  cooldown: { "b9:bench:2": 190000 }, lastKey: "b42:counter:0",
  walk: { route: [], i: 7, prevDist: 3.1, stuck: 0, cause: null }, partner: null }
```

**Per settlement:** `stations`, `claims`, `cells`, `queues`, `roomLoad` (12-tile rule), `badEdges` (with expiry).

### 6.6 Implementation order (each step ends with a BDS check and a witness check)

1. **P0, stop the leaks (the D-C562 items).**
   - `vanilla_ai` refactor, enrol/resync, guarded events, `pw:civ` / `pw:act`.
   - Interaction cancel for every civ body.
   - Flue tag avoidance plus the script blocked set.
   - *BDS, 3 village days:* zero `become_*` slips (via `dataDrivenEntityTrigger`); zero vanilla UIs; no body more than 2 blocks from its anchor for more than 10 s while not walking; no body in a flue cell.
   - *Witness:* "they stay where they were sent; no emerald screen".
2. **P1, stations.**
   - Registry from templates with facing, claims and queues; `lookAt` + axis-aligned STAND; counter service + queue; lectern `faceAt`.
   - *BDS:* keeper yaw within 5° of the station after 1 minute; no adjacent claimed cells.
3. **P2, life.** Micro-behaviours, `pw:seat_v`, pair talks with rumours, dusk ring slots, staggered windows.
   - *Witness:* "a crowd, not a clump".
4. **P3, needs and utility.** Lazy needs, adverts, decide loop with inertia and cooldowns, personality. SLEEP with the custom lie pose (RP change, Matched-Set Law).
5. **P4, robustness.** Stuck ladder with causes, bad-edge memory, profiler gate. The walk test reports the escalation level reached per walk.

### 6.7 Hypotheses to prove first (P1)

| # | Hypothesis | Test |
|---|---|---|
| H1 | Removing a group that overrode a base component does not restore the base copy | BDS: base nav vs group nav, remove the group, probe `getComponent` |
| H2 | `can_find_poi: false` in a civ group stops job-site claims | BDS: civ body plus a free lectern within 16 blocks, 2 days |
| H3 | axis_aligned + blocked hold on `villager_v2`; blocked alone keeps a non-cardinal `lookAt` yaw | BDS plus a witness screenshot (camera facing declared, P9) |
| H4 | `addRider` seats a villager on `pw:seat_v` with a seated pose | BDS plus witness |
| H5 | A small `applyImpulse` clears doorframe snags without a visible hop | Walk test, 1-wide door, 3 crossing walkers |
| H6 | A `replaceitem` main-hand item renders on `villager_v2` outside trades | Witness |
| H7 | Alternating `lookAt` pitch reads as a nod under `body_rotation_blocked` | Witness |
| H8 | Tag-based `blocks_to_avoid` honours custom block tags | BDS path test beside a tagged flue |

---

## 7. Retro-sweep input (for the decision journal; nothing implemented)

Qualifying event: external artifacts studied (MCA, Millénaire, MineColonies, TekTopia, Guard Villagers, Human Companions, Custom NPCs, vanilla `villager_v2`, Script API 2.3.0 typings).

- **scripts BP-02:**
  - Stuck ladder with causes (M, HIGH).
  - One shared body cache across schedule, work, watch and shop (S, MED); `handsCache` already does this for work.
  - Staggered per-person windows (S, MED).
  - `runJob` for leg building (M, HIGH).
- **custom blocks:** a `pw_no_villager` tag on flue, hearth, cap and well-shaft blocks (S, HIGH; L-DEDUP-1 corpus scan first); a `pw_road` tag for `preferred_path` (S, MED).
- **mobs / villager RP:** `pw:act` controller and lie pose (M, MED, Matched-Set Law).
- **worldgen / mcstructures:** authored station markers (counter, lectern, bench, bed head) in building templates (M, HIGH).
- **build / verification tooling:** walk test plus escalation level, anchor drift, adjacent-cell violations and `become_*` slips (S, HIGH).
- **documentation / lessons:**
  - Candidate "arrival hands control to a CIVITAS state, never back to vanilla AI".
  - Candidate "vanilla events re-inject AI; guard them with `bool_property pw:civ`".
- **NO-HIT (walked):** terrain caps, trees/canopy/falling-tree, redwood biome, atmospherics/sky/fog, PBR/MERS textures, audio.

---

## Appendix A — Source index

Every source is cited inline where it is used; 120 unique links. This index lists the roots. Repositories were read at the named tag or branch.

| Group | Sources |
|---|---|
| Bedrock official | [MicrosoftDocs/minecraft-creator](https://github.com/MicrosoftDocs/minecraft-creator) (Learn sources for goals, components, filters and the Script API, fetched 2026-10-04); [@minecraft/server](https://www.npmjs.com/package/@minecraft/server) (2.3.0 and 2.10.0 typings); [bedrock-samples](https://github.com/Mojang/bedrock-samples) |
| bedrock.wiki | Entity Movement, Dummy Entities, Entity Events, Sleeping Entities, Entity Properties, Script Watchdog ([wiki.bedrock.dev](https://wiki.bedrock.dev/entities/entity-movement)) |
| Bedrock add-ons | Human Companions (CurseForge); [Smart Villager](https://mcpedl.com/smart-villager-addon/), [Hardworking Villagers](https://mcpedl.com/hardworking-villagers/) (schedule edits only), [Villager+](https://mcpedl.com/villager-plus/) (MCPEDL; no technical detail public) |
| Java mods (source) | [MCA Reborn](https://github.com/Luke100000/minecraft-comes-alive) 8.1.11+26.2; [Millénaire](https://github.com/Kinniken/Millenaire) 6.0.2_2; [MineColonies](https://github.com/ldtteam/minecolonies) version/main; [Guard Villagers](https://github.com/seymourimadeit/guardvillagers) 4.0.4; [Human Companions](https://github.com/justinwon777/HumanCompanions); [Custom NPCs API](https://github.com/Noppes/CustomNPCsAPI) |
| Java mods (pages) | TekTopia wiki (Hunger, Happiness, Profession AI, Overcrowding, Homes); Easy Villagers; Villager Names; Better Villagers; Villager Fix |
| Vanilla Java | [Minecraft Wiki](https://minecraft.wiki/w/Villager) (Villager, Mob AI); decompiled 1.21.4 ([extracted_minecraft_data](https://github.com/extremeheat/extracted_minecraft_data)) |
| AI design | Zubek; Forbus & Wright; Game AI Pro (Graham, Lewis, Dill, Francis); Orkin; Bungie/Halo; Reynolds; RimWorld decompile ([RW-Decompile](https://github.com/josh-m/RW-Decompile); [JobGiver_WanderColony](https://github.com/josh-m/RW-Decompile/blob/master/RimWorld/JobGiver_WanderColony.cs): radius 7, 125-200 ticks between wanders); Stardew schedule data |

## Appendix B — Project context consulted (bytes / lines / first line)

| File | Bytes | Lines | First line / notes |
|---|---|---|---|
| `_logs/phase_log.md` | 420,558 | 2,051 | `# PHASE LOG — session 2026-09-20-C …` (tail read) |
| `_logs/decision_journal.md` | 962,734 | 3,338 | `# DECISION JOURNAL — session 2026-09-20-C` (read D-C541, D-C542, D-C557…D-C563) |
| `_intake/bedrock-samples/.../villager_v2.json` | 121,348 | 4,345 | `{` |
| `_build/bp02-219/entities/villager_v2.json` | 174,258 | 8,622 | `{`. Diff vs vanilla: only the 49 `pw:lead*` groups and their events were added; the base still holds the full vanilla AI. |
| `pw_lead.json` / `pw_seat.json` | 1,201 / 1,195 | 64 / 66 | `{` (`pw_seat` `family_types: ["player"]`) |
| `tools/bp02_src/pw_civ_walk.js` | 30,946 | 461 | `// pw_civ_walk.js — CIVITAS WALKING (C2.1; D-C541 "no idle villagers", D-C542 "real time")…` |
| `tools/bp02_src/pw_civ_clock.js` | 352,565 | 5,404 | `// pw_civ_clock.js — CIVITAS VILLAGE CLOCK + TIME TOOL (BP-02 v1.3.219)…` (schedule loop lines 5,180-5,404) |
| `tools/bp02_src/pw_civ_people.js` | 23,608 | 332 | `// pw_civ_people.js — CIVITAS people v1 (D-C536…` |
| `_build/bp02-219/manifest.json` | 2,005 | 57 | `@minecraft/server` 2.3.0, `@minecraft/server-ui` 2.0.0 |
