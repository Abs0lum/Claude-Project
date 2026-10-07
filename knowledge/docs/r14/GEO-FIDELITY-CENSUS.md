# Geometry fidelity census — shipped vs Patrix JEM (Converter B bake), rest pose

| pack | mob | geometry | verdict | cubes baked / shipped | matched | unmatched baked / shipped | median / max px | top y baked -> shipped |
|---|---|---|---|---|---|---|---|---|
| rp06-1420 | blaze | geometry.pw_blaze | **DIFFERS** | 14 / 14 | 14 | 0 / 0 | 10.11 / 26.43 | 29.27 -> 31.27 (+2.0) |
| rp07-1426 | cat | geometry.pw_cat | **DIFFERS** | 13 / 13 | 13 | 0 / 0 | 2.04 / 8.47 | 10.14 -> 12.26 (+2.11) |
| rp07-1426 | cod | geometry.cod.patrix | **DIFFERS** | 11 / 11 | 4 | 7 / 7 | 3.59 / 3.59 | 7.98 -> 3.0 (-4.98) |
| rp07-1426 | cow | geometry.pw_cow | **DIFFERS** | 15 / 15 | 15 | 0 / 0 | 1.13 / 3.31 | 24.53 -> 24.0 (-0.53) |
| rp06-1420 | drowned | geometry.pw_drowned | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 1.05 | 32.5 -> 32.5 (+0.0) |
| rp07-1426 | fox | geometry.pw_fox | **DIFFERS** | 11 / 10 | 10 | 1 / 0 | 8.38 / 18.62 | 21.5 -> 18.4 (-3.1) |
| rp07-1426 | glow_squid | geometry.glow_squid.patrix | **DIFFERS** | 12 / 12 | 12 | 0 / 0 | 9.0 / 9.0 | 45.0 -> 36.0 (-9.0) |
| rp07-1426 | goat | geometry.pw_goat | **DIFFERS** | 17 / 18 | 12 | 5 / 6 | 6.65 / 14.37 | 25.68 -> 30.76 (+5.08) |
| rp06-1420 | hoglin | geometry.hoglin.patrix | **DIFFERS** | 15 / 14 | 14 | 1 / 0 | 4.53 / 15.95 | 33.66 -> 25.75 (-7.92) |
| rp06-1420 | husk | geometry.pw_husk | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 1.98 | 32.25 -> 32.5 (+0.25) |
| rp06-1420 | illusioner | geometry.illusioner.patrix | **DIFFERS** | 16 / 21 | 11 | 5 / 10 | 0.38 / 1.19 | 33.03 -> 33.0 (-0.03) |
| rp07-1426 | iron_golem | geometry.iron_golem | **DIFFERS** | 23 / 11 | 3 | 20 / 8 | 0.01 / 0.31 | 43.0 -> 43.0 (-0.0) |
| rp07-1426 | ocelot | geometry.pw_cat | **DIFFERS** | 13 / 13 | 13 | 0 / 0 | 2.04 / 8.47 | 10.14 -> 12.26 (+2.11) |
| rp06-1420 | pillager | geometry.pw_pillager | **DIFFERS** | 18 / 24 | 14 | 4 / 10 | 0.32 / 1.18 | 33.0 -> 33.0 (-0.0) |
| rp07-1426 | polar_bear | geometry.pw_polar_bear | **DIFFERS** | 11 / 10 | 9 | 2 / 1 | 4.47 / 15.0 | 19.0 -> 23.0 (+4.0) |
| rp07-1426 | rabbit | geometry.rabbit.patrix | **DIFFERS** | 12 / 12 | 12 | 0 / 0 | 1.68 / 2.19 | 16.6 -> 17.1 (+0.5) |
| rp06-1420 | skeleton | geometry.pw_skeleton | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 0.0 | 32.25 -> 32.5 (+0.25) |
| rp07-1426 | sniffer | geometry.pw_sniffer | **DIFFERS** | 17 / 17 | 14 | 3 / 3 | 6.7 / 8.29 | 39.94 -> 33.3 (-6.64) |
| rp07-1426 | squid | geometry.squid.patrix | **DIFFERS** | 12 / 12 | 12 | 0 / 0 | 9.0 / 9.0 | 45.0 -> 36.0 (-9.0) |
| rp06-1420 | stray | geometry.pw_stray | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 0.0 | 32.25 -> 32.5 (+0.25) |
| rp06-1420 | wither_skeleton | geometry.wither_skeleton.patrix | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 1.02 | 32.25 -> 32.5 (+0.25) |
| rp06-1420 | zoglin | geometry.zoglin.patrix | **DIFFERS** | 15 / 14 | 14 | 1 / 0 | 4.53 / 15.95 | 33.66 -> 25.75 (-7.92) |
| rp06-1420 | zombie | geometry.pw_zombie | **DIFFERS** | 7 / 11 | 3 | 4 / 8 | 0.0 / 0.61 | 32.25 -> 32.5 (+0.25) |
| rp06-1420 | creeper | geometry.creeper.v1.8 | ERROR | FileNotFoundError: geometry.creeper.v1.8 | | | | |
| rp06-1420 | ravager | geometry.ravager | ERROR | FileNotFoundError: geometry.ravager | | | | |
| rp06-1420 | spider | geometry.spider | ERROR | FileNotFoundError: geometry.spider | | | | |
| rp07-1426 | wandering_trader | geometry.villager | ERROR | FileNotFoundError: [Errno 2] No such file or directory: '/home/claude/_intake/patrix-mobs/assets/mi | | | | |
| rp07-1426 | donkey | geometry.pw_donkey | **CLOSE** | 17 / 17 | 17 | 0 / 0 | 0.14 / 1.33 | 37.27 -> 37.18 (-0.09) |
| rp07-1426 | horse | geometry.horse.patrix | **CLOSE** | 15 / 15 | 15 | 0 / 0 | 0.14 / 1.33 | 34.27 -> 34.19 (-0.08) |
| rp07-1426 | llama | geometry.llama.patrix | **CLOSE** | 19 / 19 | 19 | 0 / 0 | 0.0 / 1.41 | 36.5 -> 36.5 (-0.0) |
| rp07-1426 | mooshroom | geometry.pw_mooshroom | **CLOSE** | 21 / 21 | 21 | 0 / 0 | 0.0 / 0.78 | 37.02 -> 37.02 (+0.0) |
| rp07-1426 | mule | geometry.pw_mule | **CLOSE** | 17 / 17 | 17 | 0 / 0 | 0.14 / 1.33 | 37.27 -> 37.18 (-0.09) |
| rp07-1426 | parrot | geometry.pw_parrot | **CLOSE** | 12 / 24 | 12 | 0 / 12 | 0.0 / 0.0 | 15.18 -> 15.18 (+0.0) |
| rp07-1426 | pig | geometry.pig.patrix | **CLOSE** | 10 / 9 | 8 | 2 / 1 | 0.42 / 1.43 | 15.05 -> 15.01 (-0.04) |
| rp07-1426 | sheep | geometry.sheep.patrix | **CLOSE** | 9 / 9 | 9 | 0 / 0 | 0.88 / 1.41 | 22.0 -> 22.0 (-0.0) |
| rp06-1420 | skeleton_horse | geometry.skeleton_horse.patrix | **CLOSE** | 12 / 12 | 12 | 0 / 0 | 0.14 / 1.33 | 31.9 -> 31.82 (-0.08) |
| rp07-1426 | trader_llama | geometry.trader_llama.patrix | **CLOSE** | 19 / 19 | 19 | 0 / 0 | 0.0 / 1.41 | 36.5 -> 36.5 (-0.0) |
| rp06-1420 | vindicator | geometry.pw_vindicator | **CLOSE** | 16 / 24 | 14 | 2 / 10 | 0.55 / 3.41 | 33.0 -> 33.0 (-0.0) |
| rp06-1420 | witch | geometry.pw_witch | **CLOSE** | 15 / 17 | 13 | 2 / 4 | 0.81 / 1.85 | 41.07 -> 41.74 (+0.67) |
| rp07-1426 | wolf | geometry.pw_wolf | **CLOSE** | 13 / 13 | 13 | 0 / 0 | 0.0 / 0.86 | 15.71 -> 15.71 (+0.0) |
| rp06-1420 | zombie_horse | geometry.zombie_horse.patrix | **CLOSE** | 15 / 15 | 15 | 0 / 0 | 0.14 / 1.33 | 34.27 -> 34.19 (-0.08) |
| rp07-1426 | allay | geometry.pw_allay | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 11.29 -> 11.29 (+0.0) |
| rp07-1426 | axolotl | geometry.axolotl.patrix | **MATCH** | 13 / 13 | 13 | 0 / 0 | 0.0 / 0.0 | 10.45 -> 10.45 (+0.0) |
| rp07-1426 | bat | geometry.pw_bat | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 11.49 -> 11.49 (+0.0) |
| rp07-1426 | bee | geometry.bee | **MATCH** | 14 / 14 | 14 | 0 / 0 | 0.0 / 0.0 | 10.24 -> 10.24 (+0.0) |
| rp06-1420 | bogged | geometry.bogged.patrix | **MATCH** | 13 / 13 | 13 | 0 / 0 | 0.0 / 0.0 | 35.92 -> 35.92 (-0.0) |
| rp06-1420 | breeze | geometry.pw_breeze | **MATCH** | 5 / 5 | 5 | 0 / 0 | 0.0 / 0.0 | 28.0 -> 28.0 (+0.0) |
| rp07-1426 | camel | geometry.pw_camel | **MATCH** | 15 / 15 | 15 | 0 / 0 | 0.0 / 0.0 | 45.41 -> 45.41 (+0.0) |
| rp07-1426 | chicken | geometry.pw_chicken | **MATCH** | 17 / 17 | 17 | 0 / 0 | 0.0 / 0.0 | 17.15 -> 17.15 (-0.0) |
| rp06-1420 | creaking | geometry.pw_creaking | **MATCH** | 20 / 20 | 20 | 0 / 0 | 0.0 / 0.0 | 44.0 -> 44.0 (+0.0) |
| rp07-1426 | dolphin | geometry.dolphin.patrix | **MATCH** | 10 / 10 | 10 | 0 / 0 | 0.0 / 0.0 | 10.84 -> 10.84 (-0.0) |
| rp06-1420 | elder_guardian | geometry.elder_guardian.patrix | **MATCH** | 23 / 23 | 23 | 0 / 0 | 0.0 / 0.0 | 19.89 -> 19.89 (+0.0) |
| rp07-1426 | enderman | geometry.pw_enderman | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 46.63 -> 46.63 (-0.0) |
| rp06-1420 | endermite | geometry.pw_endermite | **MATCH** | 7 / 7 | 7 | 0 / 0 | 0.0 / 0.0 | 2.49 -> 2.49 (+0.0) |
| rp07-1426 | frog | geometry.frog.patrix | **MATCH** | 16 / 16 | 16 | 0 / 0 | 0.0 / 0.0 | 7.39 -> 7.39 (-0.0) |
| rp06-1420 | giant | geometry.giant.patrix | **MATCH** | 2 / 2 | 2 | 0 / 0 | 0.0 / 0.0 | 32.25 -> 32.5 (+0.25) |
| rp06-1420 | guardian | geometry.guardian.patrix | **MATCH** | 23 / 23 | 23 | 0 / 0 | 0.0 / 0.0 | 19.89 -> 19.89 (+0.0) |
| rp07-1426 | panda | geometry.pw_panda | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 20.5 -> 20.5 (+0.0) |
| rp06-1420 | phantom | geometry.pw_phantom | **MATCH** | 10 / 10 | 10 | 0 / 0 | 0.0 / 0.0 | 10.54 -> 10.54 (+0.0) |
| rp06-1420 | piglin | geometry.piglin.patrix | **MATCH** | 16 / 16 | 16 | 0 / 0 | 0.0 / 0.0 | 31.5 -> 31.5 (+0.0) |
| rp06-1420 | piglin_brute | geometry.piglin_brute.patrix | **MATCH** | 16 / 16 | 16 | 0 / 0 | 0.0 / 0.0 | 31.2 -> 31.2 (-0.0) |
| rp07-1426 | salmon | geometry.salmon.patrix | **MATCH** | 11 / 11 | 11 | 0 / 0 | 0.0 / 0.0 | 10.98 -> 10.98 (+0.0) |
| rp06-1420 | silverfish | geometry.pw_silverfish | **MATCH** | 21 / 21 | 21 | 0 / 0 | 0.0 / 0.0 | 5.02 -> 5.02 (+0.0) |
| rp07-1426 | tadpole | geometry.tadpole.patrix | **MATCH** | 3 / 3 | 3 | 0 / 0 | 0.0 / 0.0 | 2.48 -> 2.48 (-0.0) |
| rp07-1426 | turtle | geometry.turtle.patrix | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 9.0 -> 9.0 (-0.0) |
| rp06-1420 | vex | geometry.pw_vex | **MATCH** | 9 / 9 | 9 | 0 / 0 | 0.0 / 0.0 | 11.2 -> 11.2 (-0.0) |
| rp06-1420 | warden | geometry.pw_warden | **MATCH** | 18 / 18 | 18 | 0 / 0 | 0.0 / 0.0 | 56.01 -> 56.01 (+0.0) |
