# PHASE 0 — SKELETON + ANIMATION CENSUS (check-in 1)

2026-10-01 · source `_docs/standard/SKELETON-CENSUS.json` (735 client entities, RP stack rp06-1424 / rp07-1438 / rp08-148 + vanilla 1.26.50) · tool `tools/skeleton_census.py`

## Body plans

| Plan | Mobs | Patrix | Vanilla | Ours (naturalist) | Ported | Reference rig |
|---|---|---|---|---|---|---|
| quadruped | 201 | 18 | 2 | 34 | 147 | minecraft:cow (Patrix, 29 bones, pw joint chain: pw_neck_base, pw_spine_mid, shoulder/elbow/hip/knee/ankle); polar bear / wolf / horse as size-class checks |
| bird | 148 | 2 | 0 | 23 | 123 | minecraft:parrot (Patrix, 45 bones) = FLIGHT template; minecraft:chicken (Patrix, 34) = ground-bird template |
| object | 72 | 0 | 40 | 29 | 3 | not creatures (boats, minecarts, arrows, armor stand, agent …) — no rig standard; IN p20 / p21 (his P22) |
| insect_flying | 44 | 1 | 0 | 4 | 39 | minecraft:bee (Patrix, 35 bones) |
| insect_walking | 36 | 0 | 0 | 5 | 31 | INTERIM pw:centipede_*_anf (60 bones, many-segment) + spider leg joints |
| humanoid | 35 | 27 | 8 | 0 | 0 | Patrix humanoids (zombie / vindicator / enderman …) — scope question H1 |
| fish | 33 | 4 | 0 | 13 | 16 | minecraft:cod / salmon (Patrix, 19 / 18 bones); tropical + puffer as shape checks |
| snake | 31 | 0 | 0 | 4 | 27 | INTERIM pw:snake_*_anf (17 bones, segmented) skeleton; pw:anaconda_ws animations |
| lizard_croc | 30 | 1 | 0 | 5 | 24 | minecraft:axolotl (Patrix, 25 bones) |
| fantasy | 21 | 12 | 9 | 0 | 0 | Patrix fantasy mobs — scope question H1 |
| biped_ape | 18 | 0 | 0 | 2 | 16 | INTERIM pw:monkey_ws (23 bones) |
| crustacean | 16 | 0 | 0 | 4 | 12 | INTERIM pw:lobster_anf (29 bones) |
| cetacean | 10 | 1 | 0 | 2 | 7 | minecraft:dolphin (Patrix, 16 bones) |
| arachnid | 8 | 1 | 1 | 2 | 4 | minecraft:spider (Patrix, 118 bones, segmented legs) |
| amphibian | 8 | 2 | 0 | 1 | 5 | minecraft:frog (Patrix, 37 bones) |
| pinniped | 8 | 0 | 0 | 2 | 6 | INTERIM sf_nba:walrus (15 bones) |
| cephalopod | 7 | 2 | 0 | 1 | 4 | minecraft:squid (Patrix, 18 bones) |
| turtle | 4 | 1 | 0 | 1 | 2 | minecraft:turtle (Patrix, 20 bones) |
| jellyfish | 3 | 0 | 0 | 2 | 1 | INTERIM sf_nba:jellyfish (17 bones) |
| bat | 1 | 1 | 0 | 0 | 0 | minecraft:bat (Patrix, 9 bones) — also feeds the flight template (membrane wing) |
| macropod | 1 | 0 | 0 | 1 | 0 | INTERIM sf_nba:kangaroo (26 bones; only member) |

Creatures: 663 (735 minus 72 objects). Animation clips: 3,140 (plus 848 controllers, 183 look_at).

## Standard animation-name set per plan (draft — from what the plan's mobs already carry)

- **quadruped**: walk, idle, attack, run, setup, baby_transform, sit, lay, jump, sleep
- **bird**: idle, fly, walk, swim, float, attack, sit, baby_idle, baby_walk
- **insect_flying**: idle, fly, walk, crawl, hover, attack
- **insect_walking**: walk, idle, sleep, disappear, appear, hide, unhide, attack
- **humanoid**: move, attack, base, walking, looking, hurt, hurt2, swimming, base_face, death_face, attack_time, walk
- **fish**: swim, attack, idle, flop, walk, setup, move, swim_fast, pw_ambient, bite, flop_sfx
- **snake**: attack, walk, swim, idle, flee, setup, climb, bellied, move, sleep, tongue
- **lizard_croc**: walk, idle, swim, attack, setup, sit, baby_transform
- **fantasy**: pw_jem, move, swim, walk, idle, spikes, move_eye
- **biped_ape**: walk, sit, idle, setup, jump, attack, wolf_sitting, run, casting, celebrating, baby_transform, climb
- **crustacean**: idle, walk, attack, swim
- **cetacean**: move, swim, attack, idle, setup, walk, idle_event, flop
- **arachnid**: walk, idle, attack, run
- **amphibian**: walk, idle, attack, swim, jump, pw_ambient
- **pinniped**: swim, idle, float, bask, attack, walk, sleep
- **cephalopod**: swim, idle, move, rotate, pw_ambient, pw_swim
- **turtle**: walk
- **jellyfish**: idle, swim, idle_event, land
- **bat**: resting, flying
- **macropod**: idle, walk, run, punch_left, punch_right, right_ear_flick

## Edge cases flagged

- Winged mobs outside 'bird': phantom, ender dragon (fantasy), allay, vex (humanoid), butterflies / moths / dragonfly (insect_flying), bat. Flight-standard scope = question F1.
- pw:monkey_ws (biped_ape) stands on all fours in its rest pose — the plan is the skeleton (arms + legs + tail), not the posture.
- The census 'quality' score counts bones driven, channels, keyframes and Molang channels; Molang-procedural rigs (sf_nba) score high. It is a coverage proxy, NOT the Patrix bar — the bar is your eye.
- 2 mobs unmeasured in the size census (pw:centipede_desert_anf parse error, pw:whale_wwa measure timeout) — both ARE in this skeleton census.
- Classifier is token-exact (mammoth ≠ moth, elephant ≠ ant, boar ≠ boa, howler ≠ owl, sparrow ≠ arrow, scalloped ≠ scallop).

## Sheets

- `REF-RIGS-rp07-1438.png` — 14 Patrix reference rigs (parrot, chicken, bat, bee, cow, polar bear, wolf, horse, axolotl, frog, cod, dolphin, squid, turtle)
- `REF-RIG-spider.png` — Patrix spider (geometry RP-07, client entity RP-06)
- `INTERIM-RIGS-rp07-1438.png` — interim references for plans with no Patrix rig (centipede, AnF boa, WS anaconda, WS howler monkey, AnF lobster, sf_nba jellyfish, walrus, kangaroo)

## p20 / p21 (his rulings 02:32 + 02:38) — design notes for Phase 5

- p20 = every entity (663 creatures + 72 objects = 735), versions of one animal side by side. p21 = (a): one step per mob, a row of copies, each copy looping ONE of its animations under a name tag.
- Objects that cannot simply be summoned and stand still — each gets its own handling in the parade design (to be shown at check-in 3):
  - not summonable by command (client-only / block entities): player, bed, decorated_pot, skull, trial_spawner, cushion, npc-style editor entities -> shown via their block / item / spawn-egg form or skipped with a note;
  - fly off or explode: arrow, fireball, small_fireball, dragon_fireball, wither_skull(_dangerous), shulker_bullet, wind_charge / breeze_wind_charge, snowball, egg, ender_pearl, potions, llama_spit, naja_spit, cocoa_beans_projectile, fireworks_rocket, thrown_trident, eye_of_ender_signal, xp_orb -> spawned inside a closed glass cell, re-spawned on a timer;
  - harmful: ender_crystal (explodes when hit), evocation_fang (bites), tnt_minecart -> behind glass, out of reach.
