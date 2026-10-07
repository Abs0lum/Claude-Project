# ROSTER SIZE CENSUS — 2026-09-29 (D-C290, his 19:30 ask) — READ-ONLY, nothing resized

Tool: `tools/roster_size_census.py` · measured from the build files RP-07 1.4.25 / RP-06 1.4.18 / RP-08 1.4.8 (+ PW-StripMine BP 1.3.3 scales for sf_nba) against Mojang bedrock-samples 1.26.50 (geometry + textures + BP scales). Sizes are what the game DRAWS at the model's REST pose (visible texels only, adult scale × BP scale). Rest pose ≠ the pose you see for spread wings, hanging tentacles, splayed flippers and legs — those rows say so. **Static measurement = rules out, never rules in (P1): your eye in game decides.**

## Findings for your eye (the short list)

1. **Tropical fish are drawn 30 % bigger than the size curve meant** — 0.64 block vs the 0.49 target. The 09-29 curve set our client scale (0.915) without counting vanilla's behaviour-pack ×1.3 on tropical fish (bedrock-samples tropicalfish.json l.142). Tool gap, not a design choice. Fix option: client scale 0.915 → 0.70 (S).
2. **Squid / glow squid: ours 2.92 blocks tip-to-tip at rest vs vanilla 2.06 (+41 %)** — the Patrix mantle is taller (10×15 px + a 6×7 px tip = 22 px vs vanilla's 12×16×12 = 16 px) and two of its eight tentacles are 20 px (vanilla 18). The size you have seen in game is with the tentacles swimming, not hanging straight; you passed the squid rounds without a size note. Listed, no proposal.
3. **Guardian / elder guardian: +45 % over vanilla in the LARGEST dimension** — that dimension is the Java spike layout you approved ("looks perfect"); measured without the spines and tail, the body is EXACTLY vanilla's (1.00 / 2.35 blocks, checked 19:5x). Listed, no proposal.
4. **Goat +18 % longer than vanilla** (1.82 vs 1.55 blocks head-body, still +18 % with horns, beard and tail left out) — the Patrix goat (you passed it in R2; it was left alone). Listed for a look next time a goat is on screen.
5. **Cow / mooshroom +11–12 %, llama / trader llama +10 % over vanilla** — Patrix bodies; within the range of your approved looks, listed only.
6. **Parrot (FA-1) and bat (FA-1) sit ABOVE the curve** — parrot 0.96 block vs 0.61 target (a macaw is ~0.5 m with tail); bat wingspan 1.17 vs 0.54 (rest pose with wings spread). Both are converted in FA-1 → **their size is decided there** (curve, or vanilla size — your call at the FA-1 preview).
7. **Big real animals are drawn at ~98 % of true scale on the median** (cow 0.80, horse 0.93, dolphin 0.92, camel 0.89, pig 1.08, panda 1.49, goat 1.47, polar bear 1.17). The two high ones (panda, goat) are Mojang's / Patrix's chunky designs; the low ones (cow, llama, skeleton / zombie horse ~0.84) keep vanilla-size hitboxes (the size_rule "option (a)" ruling: resource-pack-only sizing, big mobs wait for hitbox work).
8. **Naturalist (sf_nba) creatures:** most on the StripMine curve; off by ≥ 15 %: lion / male lion / female lion / tiger (+30–58 %), hyena (+26 %), sloth (+37 %) OVER; deer (−25 %), mammoth (−29 %), tortoise (−28 %), hamster (−50 %), firefly (−43 %), crow (−30 %), finch / robin / sparrow (~−19 %) UNDER. Part of the "over" group is a definition slip in the StripMine table: it says "largest dimension incl. tail" but gives lions 2.1 m (head-body; with the tail a lion is ~3 m). The "under" giants were capped at ×1.2 growth by design (hitbox caution).
9. **People-shaped mobs: all within ±7 % of your character's height** except the witch (+30 % — her hat) and the bogged (+17 % — the mushrooms). Husk +13 % = Java's 1.0625 husk scale on purpose.

## Measurement limits (listed so nothing is silently skipped — P11)

armadillo (its body parts are render-controller-conditional → only the head counted) · wither, ghast (scale from a script variable, not evaluated) · slime, magma cube (size from a variant) · blaze (unmeasured) · giant (BP ×6 not in bedrock-samples) · sf_nba dragonfly, tree frog (0 texels passed the alpha cut) · eggs / jars / plushies (not creatures).

## Size-lock gate (SZL) — proposed standing gate from the FA-1 build
Every build re-measures every mob it touches; a visible size that moves > 8 % from the previous build without a planned entry fails the gate. The sizes you like cannot drift by accident.

## Full table
| flag | class | mob | drawn by | measure | drawn (blk) | target / vanilla | ratio | ours ÷ vanilla | basis |
|---|---|---|---|---|---|---|---|---|---|
| ok | FANTASY | minecraft:allay | vanilla-drawn | total | 0.709 |  | 1.0 |  | vanilla Bedrock drawn size |
| unmeasured | FANTASY | minecraft:blaze | vanilla-drawn |  |  |  |  |  | no visible texels / geometry |
| ok | FANTASY | minecraft:breeze | vanilla-drawn | total | 1.095 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:cave_spider | vanilla-drawn | total | 1.662 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:copper_golem | vanilla-drawn | total | 1.499 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:creaking | vanilla-drawn | total | 1.992 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:creeper | ours | total | 1.625 | 1.625 | 1.0 | 1.0 | vanilla Bedrock drawn size |
| LOOK | FANTASY | minecraft:elder_guardian | ours | total | 6.092 | 4.186 | 1.455 | 1.455 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:ender_dragon | vanilla-drawn | total | 8.5 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:enderman | ours | total | 2.915 | 3.054 | 0.954 | 0.954 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:endermite | vanilla-drawn | total | 0.556 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:ghast | vanilla-drawn | total | 7.625 |  | 1.0 |  | vanilla Bedrock drawn size |
| no check | FANTASY | minecraft:giant | ours | total | 0.5 |  |  |  | vanilla Bedrock drawn size |
| no check | FANTASY | minecraft:glow_squid | ours | total | 2.917 |  |  |  | vanilla Bedrock drawn size |
| LOOK | FANTASY | minecraft:guardian | ours | total | 2.592 | 1.781 | 1.455 | 1.455 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:happy_ghast | vanilla-drawn | total | 5.75 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:hoglin | ours | total | 2.584 | 2.589 | 0.998 | 0.998 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:iron_golem | ours | total | 2.695 | 2.688 | 1.003 | 1.003 | vanilla Bedrock drawn size |
| unmeasured | FANTASY | minecraft:magma_cube | vanilla-drawn |  |  |  |  |  | no visible texels / geometry |
| ok | FANTASY | minecraft:nautilus | vanilla-drawn | total | 0.853 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:phantom | vanilla-drawn | total | 2.688 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:ravager | ours | total | 3.619 | 3.537 | 1.023 | 1.023 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:shulker | vanilla-drawn | total | 1.0 |  | 1.0 |  | vanilla Bedrock drawn size |
| LOOK | FANTASY | minecraft:silverfish | ours | total | 0.894 | 1.062 | 0.842 | 0.842 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:slime | vanilla-drawn | total | 0.412 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:sniffer | vanilla-drawn | total | 3.775 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:snow_golem | vanilla-drawn | total | 1.688 |  | 1.0 |  | vanilla Bedrock drawn size |
| minor | FANTASY | minecraft:spider | ours | total | 2.046 | 2.375 | 0.861 | 0.861 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:strider | vanilla-drawn | total | 1.861 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:vex | vanilla-drawn | total | 1.042 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:warden | vanilla-drawn | total | 3.231 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:wither | vanilla-drawn | total | 1.5 |  | 1.0 |  | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:wither_skeleton | ours | total | 2.39 | 2.4 | 0.996 | 0.996 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:zoglin | ours | total | 2.584 | 2.589 | 0.998 | 0.998 | vanilla Bedrock drawn size |
| ok | FANTASY | minecraft:zombie_nautilus | vanilla-drawn | total | 0.853 |  | 1.0 |  | vanilla Bedrock drawn size |
| LOOK | HUMAN | minecraft:bogged | ours | h | 2.188 | 1.875 | 1.167 | 1.094 | player height 1.875 blk |
| ok | HUMAN | minecraft:drowned | ours | h | 2.0 | 1.875 | 1.067 | 0.962 | player height 1.875 blk |
| ok | HUMAN | minecraft:evocation_illager | ours | h | 1.939 | 1.875 | 1.034 | 0.973 | player height 1.875 blk |
| minor | HUMAN | minecraft:husk | ours | h | 2.125 | 1.875 | 1.133 | 1.062 | player height 1.875 blk |
| minor | HUMAN | minecraft:illusioner | ours | h | 2.062 | 1.875 | 1.1 |  | player height 1.875 blk |
| ok | HUMAN | minecraft:piglin | ours | h | 1.989 | 1.875 | 1.061 | 0.995 | player height 1.875 blk |
| ok | HUMAN | minecraft:piglin_brute | ours | h | 1.983 | 1.875 | 1.058 | 0.992 | player height 1.875 blk |
| ok | HUMAN | minecraft:pillager | ours | h | 1.939 | 1.875 | 1.034 | 0.912 | player height 1.875 blk |
| ok | HUMAN | minecraft:skeleton | ours | h | 1.992 | 1.875 | 1.062 | 0.996 | player height 1.875 blk |
| ok | HUMAN | minecraft:stray | ours | h | 1.992 | 1.875 | 1.062 | 0.996 | player height 1.875 blk |
| ok | HUMAN | minecraft:villager_v2 | ours | h | 1.992 | 1.875 | 1.062 | 1.0 | player height 1.875 blk |
| ok | HUMAN | minecraft:vindicator | ours | h | 1.934 | 1.875 | 1.031 | 0.971 | player height 1.875 blk |
| ok | HUMAN | minecraft:wandering_trader | ours | h | 1.992 | 1.875 | 1.062 | 1.0 | player height 1.875 blk |
| LOOK | HUMAN | minecraft:witch | ours | h | 2.446 | 1.875 | 1.305 | 2.407 | player height 1.875 blk |
| ok | HUMAN | minecraft:zombie | ours | h | 2.0 | 1.875 | 1.067 | 1.0 | player height 1.875 blk |
| minor | HUMAN | minecraft:zombie_pigman | ours | h | 2.072 | 1.875 | 1.105 | 1.037 | player height 1.875 blk |
| minor | HUMAN | minecraft:zombie_villager_v2 | ours | h | 2.141 | 1.875 | 1.142 | 1.0 | player height 1.875 blk |
| minor | LARGE | minecraft:camel | ours | l | 2.75 | 3.164 | 0.888 | 1.0 | dromedary 2.2-3.4 m |
| minor | LARGE | minecraft:camel_husk | vanilla-drawn | l | 2.75 | 3.164 | 0.888 |  | = camel |
| minor | LARGE | minecraft:cod | ours | total | 0.932 | 0.844 | 1.128 | 1.009 | Atlantic cod 0.6-1.0 m |
| LOOK | LARGE | minecraft:cow | ours | l | 1.736 | 2.215 | 0.801 | 1.111 | cattle head-body 1.8-2.4 m |
| minor | LARGE | minecraft:dolphin | ours | total | 2.366 | 2.636 | 0.918 | 0.996 | bottlenose dolphin 2-4 m |
| ok | LARGE | minecraft:donkey | ours | l | 1.816 | 1.898 | 0.978 | 0.986 | donkey 1.5-2.0 m |
| ok | LARGE | minecraft:fox | ours | l | 0.685 | 0.685 | 1.022 | 1.096 | red fox 46-90 cm |
| LOOK | LARGE | minecraft:goat | ours | l | 1.818 | 1.265 | 1.469 | 1.175 | domestic goat 1.0-1.5 m |
| ok | LARGE | minecraft:horse | ours | l | 2.296 | 2.531 | 0.927 | 1.085 | horse body 2.2-2.5 m |
| LOOK | LARGE | minecraft:llama | ours | l | 1.65 | 2.004 | 0.841 | 1.1 | llama 1.2-2.25 m |
| LOOK | LARGE | minecraft:mooshroom | ours | l | 1.746 | 2.215 | 0.805 | 1.118 | = cow |
| minor | LARGE | minecraft:mule | ours | l | 1.92 | 2.215 | 0.886 | 0.986 | mule 1.9-2.3 m |
| ok | LARGE | minecraft:ocelot | ours | l | 0.791 | 0.791 | 1.022 | 0.603 | ocelot 55-100 cm |
| LOOK | LARGE | minecraft:panda | ours | l | 2.312 | 1.582 | 1.493 | 1.057 | giant panda 1.2-1.9 m |
| minor | LARGE | minecraft:pig | ours | l | 1.45 | 1.371 | 1.081 | 0.967 | domestic pig 0.9-1.8 m |
| LOOK | LARGE | minecraft:polar_bear | ours | l | 2.525 | 2.215 | 1.165 | 0.886 | polar bear 1.8-2.4 m |
| LOOK | LARGE | minecraft:salmon | ours | total | 1.527 | 0.791 | 1.972 | 0.982 | Atlantic salmon 0.7-0.8 m |
| ok | LARGE | minecraft:sheep | ours | l | 1.266 | 1.265 | 1.023 | 0.917 | domestic sheep 120-180 cm (Merino-type 120-150); 1.20 = his R8 b15 'a tiny bit smaller' (-7.7 %, D-C285) |
| LOOK | LARGE | minecraft:skeleton_horse | ours | l | 2.087 | 2.531 | 0.843 | 0.987 | = horse |
| LOOK | LARGE | minecraft:squid | ours | total | 2.917 | 0.633 | 4.709 | 1.415 | common squid ~0.3 m mantle, ~0.6 m with arms |
| LOOK | LARGE | minecraft:trader_llama | ours | l | 1.65 | 2.004 | 0.841 | 1.1 | = llama |
| LOOK | LARGE | minecraft:turtle | ours | total | 2.328 | 1.16 | 2.051 | 0.828 | green sea turtle 0.8-1.2 m shell + head |
| ok | LARGE | minecraft:wolf | ours | l | 1.508 | 1.508 | 1.022 | 1.206 | grey wolf 105-160 cm; 1.43 = his R8 b15 'a little bigger' (+10 %, D-C285) |
| LOOK | LARGE | minecraft:zombie_horse | ours | l | 2.087 | 2.531 | 0.843 | 0.986 | = horse |
| ok | NBA | sf_nba:alligator | ours | total | 3.499 | 3.5 | 1.0 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:alligator_egg | ours | total | 0.438 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:anglerfish | ours | total | 0.604 | 0.583 | 1.036 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:ant | ours | total | 0.195 | 0.22 | 0.886 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:anteater | ours | total | 3.125 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:badger | ours | total | 0.804 | 0.8 | 1.005 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:bass | ours | total | 0.506 | 0.573 | 0.883 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:beaver | ours | total | 0.997 | 1.0 | 0.997 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:beetle | ours | total | 0.0 | 0.386 | 0.0 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:black_bear | ours | total | 1.376 | 1.6 | 0.86 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:blobfish | ours |  |  |  |  |  | no visible texels / geometry |
| LOOK | NBA | sf_nba:bluejay | ours | total | 0.434 | 0.529 | 0.82 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:bluejay_egg | ours |  |  |  |  |  | no visible texels / geometry |
| LOOK | NBA | sf_nba:boar | ours | total | 1.008 | 1.6 | 0.63 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:budgie | ours | total | 0.443 | 0.488 | 0.908 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:butterfly | ours | total | 0.168 | 0.434 | 0.387 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:cage | ours | total | 0.0 |  |  |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:canary | ours | total | 0.368 | 0.458 | 0.803 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:canary_egg | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:capybara | ours | total | 1.242 | 1.25 | 0.994 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:cardinal | ours | total | 0.42 | 0.507 | 0.828 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:cardinal_egg | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:caterpillar | ours | total | 0.356 | 0.386 | 0.922 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:catfish | ours | total | 0.793 | 0.8 | 0.991 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:cave_snake | ours | total | 1.501 |  |  |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:cave_snake_egg | ours |  |  |  |  |  | no visible texels / geometry |
| minor | NBA | sf_nba:cavefish | ours | total | 0.389 | 0.434 | 0.896 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:clam | ours | total | 1.2 | 1.2 | 1.0 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:cocoa_beans_projectile | ours | total | 0.305 |  |  |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:coral_snake | ours | total | 1.751 |  |  |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:coral_snake_egg | ours |  |  |  |  |  | no visible texels / geometry |
| minor | NBA | sf_nba:coyote | ours | total | 1.004 | 1.1 | 0.913 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:crab | ours | total | 0.495 | 0.498 | 0.994 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:crow | ours | total | 0.41 | 0.583 | 0.703 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:crow_egg | ours |  |  |  |  |  | no visible texels / geometry |
| LOOK | NBA | sf_nba:deer | ours | total | 1.5 | 2.0 | 0.75 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:desert_scorpion | ours | total | 1.188 |  |  |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:dirt_trail | ours | total | 0.946 |  |  |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:dragonfly | ours | total | 0.0 | 0.451 | 0.0 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:duck | ours | total | 0.595 | 0.6 | 0.992 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:duck_egg | ours | total | 0.0 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:eagle | ours | total | 0.832 | 0.9 | 0.924 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:electric_eel | ours | total | 3.594 |  |  |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:elephant | ours | total | 5.759 | 6.5 | 0.886 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:emperor_penguin | ours | total | 1.202 | 1.2 | 1.002 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:emperor_penguin_egg | ours | total | 0.375 |  |  |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:female_lion | ours | total | 3.012 | 1.9 | 1.585 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:fennec_fox | ours | total | 0.705 | 0.7 | 1.007 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:finch | ours | total | 0.375 | 0.465 | 0.806 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:finch_egg | ours |  |  |  |  |  | no visible texels / geometry |
| LOOK | NBA | sf_nba:firefly | ours | total | 0.163 | 0.284 | 0.574 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:firefly_jar | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:flamingo | ours | total | 1.395 | 1.4 | 0.996 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:flying_fish | ours | total | 1.228 |  |  |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:giant_isopod | ours | total | 0.506 | 0.562 | 0.9 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:giant_salamander | ours | total | 1.486 | 1.5 | 0.991 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:giraffe | ours | total | 5.404 | 5.5 | 0.983 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:goose | ours | total | 0.992 | 1.0 | 0.992 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:goose_egg | ours | total | 0.0 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:gorilla | ours | total | 1.688 | 1.7 | 0.993 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:great_white_shark | ours | total | 6.502 |  |  |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:grizzly_bear | ours | total | 1.877 | 2.2 | 0.853 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:hammer_head_shark | ours | total | 6.501 |  |  |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:hamster | ours | total | 0.236 | 0.471 | 0.501 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:hamster_wheel | ours | total | 0.0 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:hedgehog | ours | total | 0.51 | 0.519 | 0.983 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:hippo | ours | total | 3.861 | 3.8 | 1.016 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:hyena | ours | total | 1.89 | 1.5 | 1.26 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:iguana | ours | total | 1.553 | 1.6 | 0.971 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:info_book | ours | total | 3.401 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:jellyfish | ours | total | 0.582 | 0.6 | 0.97 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:jungle_scorpion | ours | total | 2.489 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:kakapo | ours | total | 0.607 | 0.6 | 1.012 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:kangaroo | ours | total | 2.211 | 2.3 | 0.961 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:kiwi | ours | total | 0.585 | 0.583 | 1.003 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:komodo_dragon | ours | total | 2.75 | 2.8 | 0.982 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:lion | ours | total | 2.741 | 2.1 | 1.305 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:lizard | ours | total | 0.537 | 0.536 | 1.002 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:male_lion | ours | total | 3.012 | 2.1 | 1.434 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:mammoth | ours | total | 4.982 | 7.0 | 0.712 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:mole | ours | total | 0.475 | 0.477 | 0.996 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:monkey | ours | total | 0.76 | 0.9 | 0.844 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:moose | ours | total | 3.0 | 3.0 | 1.0 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:moray | ours | total | 3.594 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:octopus | ours | total | 1.585 | 1.5 | 1.057 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:orca | ours | total | 7.508 | 7.5 | 1.001 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:ostrich | ours | total | 2.564 | 2.6 | 0.986 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:ostrich_egg | ours | total | 0.5 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:otter | ours | total | 1.203 | 1.2 | 1.003 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:owl | ours | total | 0.539 | 0.583 | 0.925 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:peafowl | ours | total | 1.277 | 1.5 | 0.851 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:piranha | ours | total | 0.732 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:platypus | ours | total | 0.585 | 0.583 | 1.003 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:plushies | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:raccoon | ours | total | 0.91 | 0.9 | 1.011 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:rat | ours | total | 0.569 | 0.573 | 0.993 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:rattlesnake | ours | total | 1.751 |  |  |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:rattlesnake_egg | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:raven | ours | total | 0.624 | 0.65 | 0.96 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:raven_egg | ours |  |  |  |  |  | no visible texels / geometry |
| no check | NBA | sf_nba:ravenous_hyena | ours | total | 1.89 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:ray | ours | total | 1.99 | 2.0 | 0.995 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:red_panda | ours | total | 1.005 | 1.0 | 1.005 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:reptile_tail | ours | total | 0.469 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:rhino | ours | total | 4.011 | 3.8 | 1.056 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:robin | ours | total | 0.375 | 0.465 | 0.806 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:robin_egg | ours |  |  |  |  |  | no visible texels / geometry |
| ok | NBA | sf_nba:seal | ours | total | 1.806 | 1.8 | 1.003 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:secretary_bird | ours | total | 1.461 | 1.3 | 1.124 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:skunk | ours | total | 0.703 | 0.7 | 1.004 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:sloth | ours | total | 0.82 | 0.6 | 1.367 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:slug | ours | total | 0.435 | 0.434 | 1.002 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:small_jellyfish | ours | total | 0.47 | 0.434 | 1.083 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:snail | ours | total | 0.371 | 0.369 | 1.005 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:snail_egg | ours |  |  |  |  |  | no visible texels / geometry |
| minor | NBA | sf_nba:snake | ours | total | 1.291 | 1.5 | 0.861 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:snake_egg | ours |  |  |  |  |  | no visible texels / geometry |
| LOOK | NBA | sf_nba:sparrow | ours | total | 0.382 | 0.471 | 0.811 |  | StripMine curve (largest dimension) |
| unmeasured | NBA | sf_nba:sparrow_egg | ours |  |  |  |  |  | no visible texels / geometry |
| no check | NBA | sf_nba:spotted_moray | ours | total | 3.594 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:squirrel | ours | total | 0.545 | 0.573 | 0.951 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:starfish | ours | total | 0.484 | 0.519 | 0.933 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:termite | ours | total | 0.246 | 0.258 | 0.953 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:tiger | ours | total | 3.779 | 2.5 | 1.512 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:tortoise | ours | total | 0.858 | 1.2 | 0.715 |  | StripMine curve (largest dimension) |
| no check | NBA | sf_nba:tortoise_egg | ours | total | 0.375 |  |  |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:toucan | ours | total | 0.602 | 0.6 | 1.003 |  | StripMine curve (largest dimension) |
| LOOK | NBA | sf_nba:tree_frog | ours | total | 0.0 | 0.401 | 0.0 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:turkey | ours | total | 1.021 | 1.1 | 0.928 |  | StripMine curve (largest dimension) |
| minor | NBA | sf_nba:vulture | ours | total | 2.812 | 2.6 | 1.082 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:walrus | ours | total | 3.237 | 3.3 | 0.981 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:whale | ours | total | 14.4 | 15.0 | 0.96 |  | StripMine curve (largest dimension) |
| ok | NBA | sf_nba:zebra | ours | total | 2.543 | 2.4 | 1.06 |  | StripMine curve (largest dimension) |
| LOOK | SMALL | minecraft:armadillo | vanilla-drawn | l | 0.125 | 0.592 | 0.211 |  | nine-banded armadillo 0.35-0.57 m |
| ok | SMALL | minecraft:axolotl | ours | total | 0.536 | 0.536 | 1.0 | 0.333 | axolotl 15-45 cm, typically 23 cm (his 9 in) |
| LOOK | SMALL | minecraft:bat | vanilla-drawn | total | 1.173 | 0.544 | 2.156 |  | wingspan 0.2-0.3 m (drawn spread) |
| ok | SMALL | minecraft:bee | ours | total | 0.261 | 0.261 | 1.0 | 0.233 | honey bee worker 12-15 mm |
| ok | SMALL | minecraft:cat | ours | l | 0.606 | 0.606 | 1.0 | 0.462 | house cat 40-50 cm |
| ok | SMALL | minecraft:chicken | ours | h | 0.603 | 0.604 | 0.998 | 0.536 | hen standing 40-50 cm to the comb |
| ok | SMALL | minecraft:frog | ours | total | 0.452 | 0.452 | 1.0 | 0.499 | temperate / cold / warm frogs 6-12 cm snout-vent |
| LOOK | SMALL | minecraft:parrot | ours | total | 0.964 | 0.614 | 1.57 | 1.064 | macaw 0.8 m incl. tail / African grey 0.33 m -> 0.50 |
| ok | SMALL | minecraft:pufferfish | ours | total | 0.56 | 0.578 | 0.969 | 1.258 | pufferfish (Takifugu) 20-50 cm |
| ok | SMALL | minecraft:rabbit | ours | l | 0.592 | 0.592 | 1.0 | 0.748 | European rabbit 34-50 cm |
| ok | SMALL | minecraft:tadpole | ours | total | 0.381 | 0.382 | 0.997 | 0.688 | frog tadpoles 2.5-7 cm before the legs |
| LOOK | SMALL | minecraft:tropicalfish | ours | total | 0.641 | 0.493 | 1.3 |  | reef fish (clownfish, tangs) 10-20 cm |

ORDER inversions (bigger in life drawn >10 % smaller): 56 — almost all involve the rest-pose giants above (squid tentacles, bat wings, turtle flippers, panda) or armadillo (unmeasured); the real ones worth a look: cow / mooshroom / llama / donkey / mule drawn smaller than the panda.
