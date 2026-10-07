# SIZE LAW — REAL LIFE (L-SIZE-REAL, D-C291) — PROPOSED CHANGES, awaiting his decisions

**His law (19:52 CT 09-29):** real animals at REAL-LIFE size (not vanilla); fantasy creatures (squid, guardians, warden …) stay imposing; the warden maybe bigger. Supersedes the size_rule 'option (a) / big mobs wait' rule and the ×1.20 growth cap.

**Curve:** your 5'10" character = 1.875 blocks → **1 m = 1.0546 blocks**; from 60 cm up true scale; under 60 cm a log ramp keeps the tiny visible (1 cm → 0.22 block, 10 cm → 0.45, 30 cm → 0.56). Like with like: head-body for vanilla mammals (tails left out both sides — the rule your wolf / sheep calibrations used), largest dimension for the Naturalist creatures (nose to tail tip, standing height for upright birds, wingspan for spread wings). Within 8 % = left alone.

**Pictures:** `SIZE-LAW-LINEUP-vanilla.png`, `SIZE-LAW-LINEUP-wild.png` (today vs proposed, side-on at one scale next to your character).

**Corrections made while building this table:** lions / tiger / hyena were never oversized — the old StripMine table compared their nose-to-tail-tip model with head-body figures; with like-for-like figures they sit within 9 %. Tropical fish: vanilla's behaviour pack scales them ×1.3, which the 09-29 curve did not count.

**Measurement fixed 20:0x (his 19:58 bear report):** the size tools used to DROP every render-controller-conditional part — the grizzly's and black bear's everyday body, snout and arms, the armadillo's body — which is why the bears looked broken in the first lineup. Parts are now evaluated in the EVERYDAY state (awake, not angry / sheared / tamed / eating, adult); everyday renders `STATE-grizzly_bear.png`, `STATE-black_bear.png`. Still to box-measure before a build: beetle, dragonfly, tree frog (flat / alpha-cut models).

## Decisions for you
1. **How big vanilla farm animals grow:** VISUAL only (resource pack; hitboxes stay vanilla, so pens, 1-block gaps and farms keep working — the cow simply looks 27 % bigger) — or VISUAL + HITBOX (behaviour-pack scale on vanilla mobs; a real-size cow is ~1.14 blocks wide and no longer fits 1-block gaps).
2. **Hostile Naturalist creatures that real life shrinks a lot:** jungle scorpion 2.5 → 0.52 block, desert scorpion 1.19 → 0.49, moray 3.6 → 1.6, spotted moray 3.6 → 1.1, electric eel 3.6 → 2.1, great white 6.5 → 4.9, hammerhead 6.5 → 4.2. Real life, or keep some imposing like the guardians?
3. **Warden:** today 3.23 blocks tall (vanilla). Bigger = +25 % (4.0) or +50 % (4.85) — visual only, its hitbox stays (deep-dark ceilings).

## The table (every real animal; rows within 8 % are kept)
| action | mob | compared | real (m) | today (blk) | real-life target (blk) | factor | basis |
|---|---|---|---|---|---|---|---|
| MEASURE FAILED (flat / alpha) — box measurement needed | sf_nba:beetle | max | 0.06 | 0 | 0.401 | None | beetle ~6 cm |
| MEASURE FAILED (flat / alpha) — box measurement needed | sf_nba:dragonfly | max | 0.12 | 0 | 0.47 | None | dragonfly ~12 cm |
| MEASURE FAILED (flat / alpha) — box measurement needed | sf_nba:tree_frog | max | 0.07 | 0 | 0.416 | None | tree frog ~7 cm |
| grow | minecraft:camel | hb | 3.0 | 2.75 | 3.164 | 1.15 | dromedary 2.2-3.4 m |
| grow | minecraft:cow | hb | 2.1 | 1.736 | 2.215 | 1.276 | cattle head-body 1.8-2.4 m |
| grow | minecraft:dolphin | max | 2.5 | 2.366 | 2.636 | 1.114 | bottlenose 2-4 m |
| grow | minecraft:horse | hb | 2.4 | 2.296 | 2.531 | 1.102 | horse 2.2-2.5 m |
| grow | minecraft:llama | hb | 1.9 | 1.65 | 2.004 | 1.214 | llama 1.2-2.25 m |
| grow | minecraft:mooshroom | hb | 2.1 | 1.746 | 2.215 | 1.268 | = cow |
| grow | minecraft:mule | hb | 2.1 | 1.92 | 2.215 | 1.153 | mule 1.9-2.3 m |
| grow | minecraft:skeleton_horse | hb | 2.4 | 2.087 | 2.531 | 1.213 | = horse |
| grow | minecraft:trader_llama | hb | 1.9 | 1.65 | 2.004 | 1.214 | = llama |
| grow | minecraft:zombie_horse | hb | 2.4 | 2.087 | 2.531 | 1.213 | = horse |
| grow | sf_nba:ant | max | 0.01 | 0.195 | 0.22 | 1.128 | ant ~1 cm |
| grow | sf_nba:badger | max | 0.9 | 0.804 | 0.949 | 1.18 | European badger 0.75-1.05 m with tail |
| grow | sf_nba:bass | max | 0.45 | 0.506 | 0.604 | 1.193 | largemouth bass 0.3-0.6 m |
| grow | sf_nba:beaver | max | 1.1 | 0.997 | 1.16 | 1.164 | beaver 1.0-1.3 m with tail |
| grow | sf_nba:black_bear | max | 1.7 | 1.597 | 1.793 | 1.123 | American black bear 1.5-1.9 m |
| grow | sf_nba:bluejay | max | 0.28 | 0.434 | 0.556 | 1.281 | blue jay 0.25-0.30 m |
| grow | sf_nba:boar | max | 1.6 | 1.008 | 1.687 | 1.674 | wild boar 1.3-2.0 m |
| grow | sf_nba:budgie | max | 0.18 | 0.443 | 0.511 | 1.154 | budgerigar 18 cm |
| grow | sf_nba:butterfly | max | 0.1 | 0.168 | 0.452 | 2.691 | wingspan ~10 cm |
| grow | sf_nba:canary | max | 0.13 | 0.368 | 0.479 | 1.3 | canary 12-14 cm |
| grow | sf_nba:cardinal | max | 0.22 | 0.42 | 0.532 | 1.266 | cardinal 21-23 cm |
| grow | sf_nba:caterpillar | max | 0.06 | 0.356 | 0.401 | 1.125 | caterpillar ~6 cm |
| grow | sf_nba:cavefish | max | 0.1 | 0.389 | 0.452 | 1.162 | blind cavefish ~10 cm |
| grow | sf_nba:coyote | max | 1.3 | 1.004 | 1.371 | 1.365 | coyote 1.0-1.35 m with tail |
| grow | sf_nba:crow | max | 0.45 | 0.41 | 0.604 | 1.473 | crow 0.4-0.53 m |
| grow | sf_nba:eagle | max | 0.9 | 0.832 | 0.949 | 1.141 | bald eagle 0.7-1.0 m |
| grow | sf_nba:elephant | max | 6.5 | 5.759 | 6.855 | 1.19 | African elephant 6-7.5 m |
| grow | sf_nba:finch | max | 0.14 | 0.375 | 0.486 | 1.296 | finch ~14 cm |
| grow | sf_nba:firefly | max | 0.02 | 0.163 | 0.29 | 1.778 | firefly ~2 cm |
| grow | sf_nba:giant_isopod | max | 0.4 | 0.506 | 0.592 | 1.17 | giant isopod 0.19-0.5 m |
| grow | sf_nba:grizzly_bear | max | 2.2 | 1.877 | 2.32 | 1.236 | grizzly 1.8-2.5 m |
| grow | sf_nba:hamster | max | 0.15 | 0.236 | 0.493 | 2.089 | Syrian hamster 13-18 cm |
| grow | sf_nba:iguana | max | 1.6 | 1.553 | 1.687 | 1.086 | green iguana 1.5-1.8 m |
| grow | sf_nba:jellyfish | max | 0.6 | 0.582 | 0.633 | 1.087 | jellyfish ~0.6 m with tentacles |
| grow | sf_nba:kangaroo | max | 2.4 | 2.211 | 2.531 | 1.145 | red kangaroo 2.2-2.6 m with tail |
| grow | sf_nba:lizard | max | 0.3 | 0.334 | 0.563 | 1.685 | lizard ~30 cm |
| grow | sf_nba:mammoth | max | 5.5 | 4.982 | 5.8 | 1.164 | woolly mammoth ~5-5.5 m incl. tusks |
| grow | sf_nba:monkey | max | 0.9 | 0.76 | 0.949 | 1.249 | capuchin ~0.9 m with tail |
| grow | sf_nba:owl | max | 0.5 | 0.539 | 0.614 | 1.14 | owl ~0.5 m |
| grow | sf_nba:peafowl | max | 1.5 | 1.277 | 1.582 | 1.239 | peacock display ~1.5 m |
| grow | sf_nba:raven | max | 0.65 | 0.624 | 0.685 | 1.098 | raven 0.56-0.69 m |
| grow | sf_nba:robin | max | 0.14 | 0.375 | 0.486 | 1.296 | European robin 12.5-14 cm |
| grow | sf_nba:snake | max | 1.5 | 1.291 | 1.582 | 1.225 | rat snake ~1.5 m |
| grow | sf_nba:sparrow | max | 0.15 | 0.382 | 0.493 | 1.291 | sparrow 14-16 cm |
| grow | sf_nba:squirrel | max | 0.45 | 0.545 | 0.604 | 1.108 | grey squirrel ~0.45 m with tail |
| grow | sf_nba:starfish | max | 0.25 | 0.484 | 0.544 | 1.125 | starfish ~25 cm |
| grow | sf_nba:tortoise | max | 1.2 | 0.858 | 1.265 | 1.475 | giant tortoise 1.0-1.5 m |
| grow | sf_nba:turkey | max | 1.1 | 1.021 | 1.16 | 1.136 | wild turkey 1.0-1.25 m |
| grow | sf_nba:whale | max | 15.0 | 14.4 | 15.818 | 1.098 | humpback 14-16 m |
| keep (within 8 %) | minecraft:axolotl | max | 0.23 | 0.536 | 0.536 | 1.0 | axolotl 15-45 cm |
| keep (within 8 %) | minecraft:bee | max | 0.015 | 0.261 | 0.261 | 1.0 | honey bee 12-15 mm |
| keep (within 8 %) | minecraft:cat | hb | 0.46 | 0.606 | 0.606 | 1.0 | house cat 0.4-0.5 m |
| keep (within 8 %) | minecraft:chicken | h | 0.45 | 0.603 | 0.604 | 1.001 | hen standing 0.4-0.5 m |
| keep (within 8 %) | minecraft:donkey | hb | 1.8 | 1.816 | 1.898 | 1.045 | donkey 1.5-2.0 m |
| keep (within 8 %) | minecraft:fox | hb | 0.65 | 0.685 | 0.685 | 1.001 | red fox 0.46-0.9 m |
| keep (within 8 %) | minecraft:frog | max | 0.1 | 0.452 | 0.452 | 1.0 | frogs 6-12 cm |
| keep (within 8 %) | minecraft:ocelot | hb | 0.75 | 0.791 | 0.791 | 1.0 | ocelot 0.55-1.0 m |
| keep (within 8 %) | minecraft:pig | hb | 1.3 | 1.45 | 1.371 | 0.945 | domestic pig 0.9-1.8 m |
| keep (within 8 %) | minecraft:pufferfish | max | 0.35 | 0.56 | 0.578 | 1.033 | pufferfish 0.2-0.5 m |
| keep (within 8 %) | minecraft:rabbit | hb | 0.4 | 0.592 | 0.592 | 1.0 | European rabbit 0.34-0.5 m |
| keep (within 8 %) | minecraft:sheep | hb | 1.2 | 1.266 | 1.265 | 1.0 | his R8 calibration (Merino-type 1.2-1.5) |
| keep (within 8 %) | minecraft:tadpole | max | 0.05 | 0.381 | 0.382 | 1.003 | tadpole 2.5-7 cm |
| keep (within 8 %) | minecraft:wolf | hb | 1.43 | 1.508 | 1.508 | 1.0 | his R8 calibration (grey wolf 1.05-1.6) |
| keep (within 8 %) | sf_nba:alligator | max | 3.5 | 3.499 | 3.691 | 1.055 | American alligator 3.4-4.6 m |
| keep (within 8 %) | sf_nba:anglerfish | max | 0.5 | 0.604 | 0.614 | 1.017 | anglerfish 0.2-1 m |
| keep (within 8 %) | sf_nba:capybara | max | 1.25 | 1.242 | 1.318 | 1.061 | capybara 1.1-1.3 m |
| keep (within 8 %) | sf_nba:catfish | max | 0.8 | 0.793 | 0.844 | 1.064 | channel catfish 0.4-1.3 m |
| keep (within 8 %) | sf_nba:clam | max | 1.2 | 1.2 | 1.265 | 1.055 | giant clam 1.2 m |
| keep (within 8 %) | sf_nba:crab | max | 0.2 | 0.495 | 0.522 | 1.055 | crab ~20 cm |
| keep (within 8 %) | sf_nba:deer | max | 1.9 | 1.922 | 2.004 | 1.042 | white-tailed deer ~1.9 m long / antler height |
| keep (within 8 %) | sf_nba:duck | max | 0.6 | 0.595 | 0.633 | 1.063 | mallard 0.5-0.65 m |
| keep (within 8 %) | sf_nba:emperor_penguin | max | 1.2 | 1.202 | 1.265 | 1.053 | emperor penguin 1.0-1.3 m tall |
| keep (within 8 %) | sf_nba:fennec_fox | max | 0.65 | 0.705 | 0.685 | 0.972 | fennec 0.55-0.7 m with tail |
| keep (within 8 %) | sf_nba:flamingo | max | 1.4 | 1.395 | 1.476 | 1.058 | flamingo 1.2-1.5 m tall |
| keep (within 8 %) | sf_nba:giant_salamander | max | 1.5 | 1.486 | 1.582 | 1.064 | Chinese giant salamander up to 1.8 m |
| keep (within 8 %) | sf_nba:giraffe | max | 5.5 | 5.404 | 5.8 | 1.073 | giraffe 4.3-5.7 m tall |
| keep (within 8 %) | sf_nba:goose | max | 0.9 | 0.992 | 0.949 | 0.957 | Canada goose 0.75-1.1 m |
| keep (within 8 %) | sf_nba:gorilla | max | 1.7 | 1.688 | 1.793 | 1.062 | gorilla 1.6-1.8 m standing |
| keep (within 8 %) | sf_nba:hedgehog | max | 0.25 | 0.51 | 0.544 | 1.068 | hedgehog 20-30 cm |
| keep (within 8 %) | sf_nba:hippo | max | 3.8 | 3.861 | 4.007 | 1.038 | hippo 2.9-5.0 m |
| keep (within 8 %) | sf_nba:hyena | max | 1.7 | 1.89 | 1.793 | 0.949 | spotted hyena ~1.7 m with tail |
| keep (within 8 %) | sf_nba:kakapo | max | 0.6 | 0.607 | 0.633 | 1.042 | kakapo 0.58-0.64 m |
| keep (within 8 %) | sf_nba:kiwi | max | 0.45 | 0.585 | 0.604 | 1.032 | kiwi 0.35-0.55 m |
| keep (within 8 %) | sf_nba:komodo_dragon | max | 2.8 | 2.75 | 2.953 | 1.074 | Komodo 2.6-3.0 m |
| keep (within 8 %) | sf_nba:lion | max | 2.8 | 2.741 | 2.953 | 1.077 | lion 2.4-3.3 m nose to tail tip |
| keep (within 8 %) | sf_nba:male_lion | max | 3.0 | 3.012 | 3.164 | 1.05 | male lion 2.7-3.3 m nose to tail tip |
| keep (within 8 %) | sf_nba:mole | max | 0.16 | 0.475 | 0.499 | 1.052 | mole ~16 cm |
| keep (within 8 %) | sf_nba:moose | max | 3.0 | 3.0 | 3.164 | 1.055 | moose 2.4-3.1 m |
| keep (within 8 %) | sf_nba:octopus | max | 1.5 | 1.585 | 1.582 | 0.998 | common octopus arm span 1-1.5 m |
| keep (within 8 %) | sf_nba:orca | max | 7.5 | 7.508 | 7.909 | 1.053 | orca 6-8 m |
| keep (within 8 %) | sf_nba:ostrich | max | 2.6 | 2.564 | 2.742 | 1.069 | ostrich 2.1-2.8 m tall |
| keep (within 8 %) | sf_nba:otter | max | 1.2 | 1.203 | 1.265 | 1.052 | river otter 1.0-1.3 m with tail |
| keep (within 8 %) | sf_nba:platypus | max | 0.5 | 0.585 | 0.614 | 1.05 | platypus 0.4-0.6 m |
| keep (within 8 %) | sf_nba:raccoon | max | 0.85 | 0.91 | 0.896 | 0.985 | raccoon 0.6-1.05 m with tail |
| keep (within 8 %) | sf_nba:rat | max | 0.4 | 0.569 | 0.592 | 1.04 | brown rat ~0.4 m with tail |
| keep (within 8 %) | sf_nba:ravenous_hyena | max | 1.7 | 1.89 | 1.793 | 0.949 | = hyena |
| keep (within 8 %) | sf_nba:ray | max | 2.0 | 1.99 | 2.109 | 1.06 | stingray disc ~2 m |
| keep (within 8 %) | sf_nba:red_panda | max | 1.0 | 1.005 | 1.055 | 1.049 | red panda ~1 m with tail |
| keep (within 8 %) | sf_nba:rhino | max | 3.8 | 4.143 | 4.007 | 0.967 | white rhino 3.4-4.2 m |
| keep (within 8 %) | sf_nba:seal | max | 1.8 | 1.806 | 1.898 | 1.051 | harbour seal 1.5-1.9 m |
| keep (within 8 %) | sf_nba:secretary_bird | max | 1.3 | 1.461 | 1.371 | 0.938 | secretary bird 1.2-1.5 m tall |
| keep (within 8 %) | sf_nba:skunk | max | 0.7 | 0.703 | 0.738 | 1.05 | striped skunk ~0.7 m with tail |
| keep (within 8 %) | sf_nba:slug | max | 0.1 | 0.435 | 0.452 | 1.039 | slug ~10 cm |
| keep (within 8 %) | sf_nba:small_jellyfish | max | 0.1 | 0.47 | 0.452 | 0.962 | ~10 cm |
| keep (within 8 %) | sf_nba:snail | max | 0.05 | 0.371 | 0.382 | 1.03 | snail ~5 cm |
| keep (within 8 %) | sf_nba:termite | max | 0.015 | 0.246 | 0.261 | 1.06 | termite ~1.5 cm |
| keep (within 8 %) | sf_nba:tiger | max | 3.3 | 3.779 | 3.48 | 0.921 | tiger 2.7-3.9 m nose to tail tip |
| keep (within 8 %) | sf_nba:toucan | max | 0.6 | 0.602 | 0.633 | 1.051 | toco toucan 0.55-0.65 m |
| keep (within 8 %) | sf_nba:vulture | max | 2.6 | 2.812 | 2.742 | 0.975 | vulture wingspan ~2.6 m (spread) |
| keep (within 8 %) | sf_nba:walrus | max | 3.3 | 3.237 | 3.48 | 1.075 | walrus 2.2-3.6 m |
| keep (within 8 %) | sf_nba:zebra | max | 2.4 | 2.543 | 2.531 | 0.995 | zebra 2.2-2.5 m |
| shrink | minecraft:armadillo | hb | 0.4 | 0.982 | 0.592 | 0.603 | nine-banded 0.35-0.57 m |
| shrink | minecraft:bat | max | 0.28 | 1.173 | 0.556 | 0.474 | cave bat wingspan 0.22-0.33 m (posed with spread wings) |
| shrink | minecraft:cod | max | 0.8 | 0.932 | 0.844 | 0.905 | Atlantic cod 0.6-1.0 m |
| shrink | minecraft:goat | hb | 1.2 | 1.818 | 1.265 | 0.696 | domestic goat 1.0-1.5 m |
| shrink | minecraft:panda | hb | 1.5 | 2.312 | 1.582 | 0.684 | giant panda 1.2-1.9 m |
| shrink | minecraft:parrot | max | 0.84 | 0.964 | 0.886 | 0.919 | scarlet macaw 0.81-0.96 m bill to tail tip (the red-blue Patrix parrot) |
| shrink | minecraft:polar_bear | hb | 2.1 | 2.525 | 2.215 | 0.877 | polar bear 1.8-2.4 m |
| shrink | minecraft:salmon | max | 0.75 | 1.527 | 0.791 | 0.518 | Atlantic / sockeye salmon 0.6-0.8 m (the NORMAL size variant) |
| shrink | minecraft:tropicalfish | max | 0.15 | 0.641 | 0.493 | 0.769 | reef fish 0.1-0.2 m |
| shrink | minecraft:turtle | max | 1.4 | 2.328 | 1.476 | 0.634 | green sea turtle: 1.0 m shell, ~1.4 m flipper tip to flipper tip |
| shrink | sf_nba:anteater | max | 2.0 | 3.125 | 2.109 | 0.675 | giant anteater 1.8-2.2 m with tail |
| shrink | sf_nba:cave_snake | max | 0.8 | 1.501 | 0.844 | 0.562 | cave-dwelling snake ~0.8 m |
| shrink | sf_nba:coral_snake | max | 0.8 | 1.751 | 0.844 | 0.482 | coral snake 0.5-0.9 m |
| shrink | sf_nba:desert_scorpion | max | 0.14 | 1.188 | 0.486 | 0.409 | desert hairy scorpion 14 cm |
| shrink | sf_nba:electric_eel | max | 2.0 | 3.594 | 2.109 | 0.587 | electric eel up to 2.5 m |
| shrink | sf_nba:female_lion | max | 2.6 | 3.012 | 2.742 | 0.91 | lioness 2.4-2.8 m nose to tail tip |
| shrink | sf_nba:flying_fish | max | 0.3 | 1.228 | 0.563 | 0.458 | flying fish ~30 cm |
| shrink | sf_nba:great_white_shark | max | 4.6 | 6.502 | 4.851 | 0.746 | great white 3.4-4.9 m typical |
| shrink | sf_nba:hammer_head_shark | max | 4.0 | 6.501 | 4.218 | 0.649 | hammerheads 2.5-6 m |
| shrink | sf_nba:jungle_scorpion | max | 0.2 | 2.489 | 0.522 | 0.21 | emperor scorpion ~20 cm |
| shrink | sf_nba:moray | max | 1.5 | 3.594 | 1.582 | 0.44 | green moray ~1.5 m |
| shrink | sf_nba:piranha | max | 0.3 | 0.732 | 0.563 | 0.769 | red-bellied piranha ~30 cm |
| shrink | sf_nba:rattlesnake | max | 1.2 | 1.751 | 1.265 | 0.723 | western diamondback ~1.2 m |
| shrink | sf_nba:sloth | max | 0.7 | 0.82 | 0.738 | 0.9 | three-toed sloth ~0.6-0.75 m |
| shrink | sf_nba:spotted_moray | max | 1.0 | 3.594 | 1.055 | 0.293 | spotted moray ~1 m |
