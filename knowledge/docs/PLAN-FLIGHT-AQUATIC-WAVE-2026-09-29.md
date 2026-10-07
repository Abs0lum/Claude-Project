# PLAN — FLIGHT + AQUATIC WAVE (2026-09-29, D-C290) — PROPOSED, awaiting Abs0lum's GO

**His order (19:24 CT 09-29):** "I'm giving a go for all of this now, RIGHT AFTER, we finish flight and aquatic mobs."
So the sequence is:
1. **This wave** — flight + aquatic mobs (the "next wave" proposed in handoff §2ae / §2af, never built because Rounds 10–13 went to witness fixes).
2. **Hand-point + wolf round** (GO given; formerly called "Round 14"): hand points on piglin / brute / zombie / husk / drowned / zombified piglin, wolf baby fix, zombie-horse baby scale, gates HPT + BSC, runner 0.4.0 + p9.
3. **Baby Wave** (GO given): the 50 Patrix 26.2 baby models, as a Menagerie lane-V extension.

Version numbers are given out at build time and never reused, so the hand-point round will take whatever RP-06 / RP-07 numbers come after this wave.

## 1 · Scope (my reading — his to correct)

"Flight and aquatic mobs" = every VANILLA flying mob and every VANILLA water mob gets the Patrix Java model and Java-faithful motion. The known gaps get fixed too. New real-world species (the Menagerie's fish, waterbirds, songbirds) are NOT in this wave; they stay in the Menagerie waves M2+.

### Flying — state of RP-06 1.4.18 / RP-07 1.4.25 (census 19:4x)
| Mob | Ours now | Patrix 26.2 JEMs | Owner pack (ownership law) |
|---|---|---|---|
| parrot | vanilla-shaped `geometry.parrot`; every animation a shim (no flap, no dance, no sit) | parrot (+ the two Patrix wing sets) | RP-07 |
| bat | vanilla | bat | RP-07 |
| allay | vanilla | allay | RP-07 |
| vex | vanilla | vex | RP-06 |
| phantom | vanilla | phantom | RP-06 |
| ghast | vanilla | ghast | RP-06 |
| happy ghast | vanilla | happy_ghast, _harness, _ropes (+ _baby → Baby Wave) | RP-07 |
| blaze | vanilla | blaze | RP-06 |
| breeze | vanilla | breeze, breeze_wind | RP-06 |
| wither | vanilla | wither | RP-06 |
| bee | ours, real animations | bee (+ bee_baby → Baby Wave) | RP-07, check only |

### Aquatic — state (census 19:4x)
| Mob | Gap |
|---|---|
| squid, glow squid | tilt FIXED + witnessed (d03); tentacle motion still shimmed (`move` / `swim` → no-op) |
| cod, salmon, pufferfish | `swim` shimmed → no tail wag |
| pufferfish | the small size (backlog) |
| tropical fish | A fin gap; pattern layers A/B (Patrix `tropical_fish_pattern_a/_b`) not used |
| turtle | tail gap; `swim` / `walk` shimmed (check whether AR's own animations cover them) |
| axolotl, frog | `swim` / `walk` / `jump` shimmed (same check) |
| tadpole | `swim` points at a missing id |
| guardian | the "quiver" (backlog) |
| dolphin | own animations: re-check only |
| nautilus, zombie nautilus | vanilla; Patrix has nautilus (+ armor, saddle) and zombie_nautilus (+ coral) |

## 2 · Method (all proven tools)
- **Model:** Converter B (`convb.py` / `convb_build.py` / `convb_round.py`), which bakes the Patrix JEM with vanilla part pivots, binds and frames. Water mobs are baked in the in-water branch (`convb.AQUATIC`, L-BAKE-WET).
- **Motion:** `jem2molang.py` ports the Patrix JEM animation expressions to Molang, checked against the JEM (SP3-style check). For wing / fin poses that Java writes in code: `RUNTIME_POSE` entries (bat wings, phantom wings, parrot flight).
- **Standing gates on every build:** MLS · ARS · RCV · FMT · RBW · ATT · PREC. New gates are added when a round teaches one.
- **Witness:** each round ships a TestRunner lineup:
  - flyers get a tall roofed pen (and a free-flight step);
  - water mobs get the ice-proof pool;
  - side, front and top shots on every mob.

## 3 · Rounds
| Round | Content | Delivers |
|---|---|---|
| **FA-0 research** (no build) | For every mob: read the Patrix JEM (parts, animation expressions, texture + `_n`/`_s`), the vanilla client entity + animations + render controller, the attachables / RC quirks; pick the owner pack; plan the runner rigs. Output: a per-mob sheet + a preview image per model (bb_truth). | preview sheet to him |
| **FA-1 small flyers** | parrot (rebuild + flight wings + dance / sit), bat, allay, vex, phantom | RP-06 + RP-07 + runner lineup |
| **FA-2 big flyers** | ghast, happy ghast (+ harness, ropes), blaze, breeze (+ wind), wither | RP-06 + RP-07 + runner lineup |
| **FA-3 water** | squid / glow squid tentacles, fish swim (cod, salmon, pufferfish, tropical fish), axolotl / frog / turtle / tadpole motion, pufferfish small, tropical fish fin + patterns, turtle tail, guardian quiver, nautilus + zombie nautilus | RP-06 + RP-07 + runner lineup |

## 4 · One recommendation (his call)
The runner's grow-up / age-log fix (part of the hand-point round) is folded into FA-1's runner build. The flight and water lineups spawn mobs that can roll babies (turtles, axolotls, dolphins, happy ghasts), and the same slip that shrank the e03 wolf would muddy these witness rounds. The rest of the hand-point round stays where he put it.

## 5 · Standing constraints
- Ownership law (who owns which id).
- 250 MB pack ceiling.
- CC0 / Patrix texture sources.
- Witness rule; P9 / P10 intake.
- The licence stance in the custom instructions §9 stays in force until he edits it. His 19:24 remark "we're no longer worried about license issues" is logged, not applied.
