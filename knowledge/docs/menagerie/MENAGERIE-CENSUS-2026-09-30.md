# Menagerie census — the true duplicate list + the port list (2026-09-30, D-C349)

Every creature in the 14 add-ons mapped to one English animal group (Portuguese / Spanish names translated, sub-species folded into their animal), then compared with what our packs already have (vanilla + Patrix, StripMine sf_nba). `tools/menagerie_census.py`.

- **COMPARE** (2+ versions to choose from): **115 animals** = A 92 with 2+ add-on versions + B 23 with one add-on version vs our current StripMine (sf_nba) one
- **VANILLA** (a vanilla mob Patrix already covers; add-on versions = possible variant skins): **18**
- **NEW** (only one add-on has it, we don't): **82 animals**
- PROPS (eggs, boats, feeders, items — travel with their creature): 48

## COMPARE

| Animal | Versions (source · key · skin px · cubes/bones) | Ours now |
|---|---|---|
| **aardvark** (A) | WS · aardvark · None px · 12/11<br>WWA · aardvark · 64 px · 12/11<br>YSav · aardvark · 128 px · 23/29 | — |
| **alligator** (B) | AnF · alligator_albino · 112 px · 31/23<br>AnF · alligator_american · 112 px · 31/23<br>AnF · alligator_chinese · 112 px · 31/23 | sf_nba:alligator |
| **ant** (A) | AnF · ant_amazonian · 48 px · 15/22<br>AnF · ant_bullet · 48 px · 15/22<br>AnF · ant_carpenter · 48 px · 15/22<br>AnF · ant_fire · 32 px · 14/20<br>AnF · ant_sahara · 32 px · 14/20<br>AnF · ant_warrior_amazonian · 64 px · 22/23<br>AnF · ant_warrior_bullet · 64 px · 22/23<br>AnF · ant_warrior_carpenter · 64 px · 22/23<br>AnF · ant_warrior_fire · 64 px · 22/23<br>AnF · ant_warrior_sahara · 64 px · 22/23<br>AnF · ant_warrior_yellowcrazy · 64 px · 22/23<br>AnF · ant_yellowcrazy · 32 px · 14/20<br>WA · ant · 128 px · 27/10<br>WS · fire_ant · None px · 13/19<br>WWA · fire_ant · 64 px · 13/19 | sf_nba:ant |
| **anteater** (B) | YTri · tamandua · 128 px · 74/24 | sf_nba:anteater |
| **baboon** (A) | IFS · babuino · 128 px · 29/14<br>WS · baboon · None px · 21/23<br>YSav · baboon · 256 px · 31/27 | — |
| **badger** (B) | AnF · badger · 48 px · 18/16 | sf_nba:badger |
| **bear** (A) | AnF · bear · 112 px · 20/17<br>AnF · bear_grizzly · 112 px · 25/17<br>WA · bear · 256 px · 22/28<br>WA · black_bear · 256 px · 22/28<br>WS · brown_bear · None px · 9/7<br>WWA · brown_bear · 64 px · 9/7<br>YTri · urso · 128 px · 22/12 | sf_nba:black_bear, sf_nba:grizzly_bear |
| **beaver** (A) | AnF · beaver · 48 px · 16/18<br>YTri · castor · 64 px · 8/7 | sf_nba:beaver |
| **beetle** (A) | AnF · beetle_atlas · 80 px · 28/23<br>AnF · beetle_coloradopotato · 48 px · 25/17<br>AnF · beetle_desert · 48 px · 25/17<br>AnF · beetle_elephant · 80 px · 28/23<br>AnF · beetle_hercules · 80 px · 28/23<br>AnF · beetle_mexicanbean · 48 px · 25/17<br>AnF · beetle_mountainpine · 48 px · 25/17<br>AnF · beetle_stag · 80 px · 28/23<br>WWA · bombardier_beetle · 64 px · 11/9 | sf_nba:beetle |
| **blue_jay** (A) | AnF · jay_blue · 48 px · 12/12<br>WA · cyanocitta_cristata · 128 px · 28/25 | sf_nba:bluejay |
| **boar** (A) | AnF · hog_forest · 96 px · 48/43<br>AnF · hog_redriver · 96 px · 48/43<br>AnF · hog_sulawesi · 96 px · 48/43<br>AnF · hog_warthog · 96 px · 48/43<br>AnF · hog_wild · 96 px · 48/43<br>IFS · jabali · 128 px · 13/12<br>WA · boar · 128 px · 40/20<br>YSav · javali · 128 px · 43/31<br>YTri · javali · 128 px · 22/13 | sf_nba:boar |
| **buffalo** (A) | AnF · buffalo_african · 72 px · 26/22<br>AnF · buffalo_forest · 72 px · 26/22<br>AnF · buffalo_water · 72 px · 26/22<br>WA · buffalo · 256 px · 43/10<br>YSav · bufalo · 128 px · 48/33 | — |
| **butterfly** (A) | AnF · butterfly_adonisblue · 80 px · 12/15<br>AnF · butterfly_bluemorpho · 80 px · 12/15<br>AnF · butterfly_crimsonrose · 80 px · 12/15<br>AnF · butterfly_emeraldswallowtail · 80 px · 12/15<br>AnF · butterfly_giantafrican · 80 px · 12/15<br>AnF · butterfly_goliathbirdwing · 80 px · 12/15<br>AnF · butterfly_monarch · 80 px · 12/15<br>AnF · butterfly_queenalexandra · 80 px · 12/15<br>WA · butterfly · 256 px · 9/3<br>WWA · butterfly · 64 px · 7/4 | sf_nba:butterfly |
| **canary** (B) | YTri · canario · 32 px · 11/8 | sf_nba:canary |
| **capuchin** (A) | WA · capuchin_monkeys · 64 px · 16/25<br>WWA · capuchin_monkey · 32 px · 11/13 | — |
| **capybara** (A) | WWA · capybara · 64 px · 8/7<br>YTri · capivara · 64 px · 18/8 | sf_nba:capybara |
| **cassowary** (A) | WWA · cassowary · 64 px · 10/5<br>YTri · casuar · 128 px · 18/8 | — |
| **caterpillar** (B) | AnF · caterpillar_adonisblue · 32 px · 18/13<br>AnF · caterpillar_bluemorpho · 32 px · 18/13<br>AnF · caterpillar_crimsonrose · 32 px · 18/13<br>AnF · caterpillar_emeraldswallowtail · 32 px · 18/13<br>AnF · caterpillar_giantafrican · 32 px · 18/13<br>AnF · caterpillar_goliathbirdwing · 32 px · 18/13<br>AnF · caterpillar_monarch · 32 px · 18/13<br>AnF · caterpillar_queenalexandra · 32 px · 18/13 | sf_nba:caterpillar |
| **catfish** (B) | YSav · cacu · 256 px · 36/31 | sf_nba:catfish |
| **chimpanzee** (A) | WA · chimpanzee · 256 px · 27/14<br>YTri · chimpanze · 64 px · 10/8 | — |
| **coyote** (B) | YTri · coiote · 64 px · 11/9 | sf_nba:coyote |
| **crab** (A) | AnF · crab_blue · 48 px · 27/28<br>AnF · crab_emerald · 48 px · 27/28<br>AnF · crab_king · 48 px · 23/24<br>AnF · crab_spider · 48 px · 25/32<br>AnF · crab_stone · 48 px · 27/28<br>WA · crab · 128 px · 28/26<br>WWA · hermit_crab · 64 px · 19/23<br>YTri · caranguejo · 128 px · 45/29 | sf_nba:crab |
| **cricket** (A) | AnF · cricket_cave · 32 px · 19/17<br>AnF · cricket_greenbush · 32 px · 19/17<br>AnF · cricket_house · 32 px · 19/17<br>AnF · cricket_tobacco · 32 px · 19/17<br>WWA · cricket · 32 px · 11/3 | — |
| **crocodile** (A) | AnF · croc_african · 128 px · 28/23<br>AnF · croc_nile · 128 px · 28/23<br>AnF · croc_saltwater · 128 px · 28/23<br>WA · crocodile · 256 px · 88/16<br>WS · crocodile · None px · 22/14<br>WWA · crocodile · 80 px · 22/14<br>YSav · crocodilo · 256 px · 69/30<br>YTri · crocodilo · 128 px · 66/25 | — |
| **crow** (A) | AnF · crow_carrion · 48 px · 12/12<br>AnF · crow_collared · 48 px · 12/12<br>AnF · crow_hooded · 48 px · 12/12<br>AnF · crow_piping · 48 px · 12/12<br>WWA · crow · 32 px · 8/6 | sf_nba:crow |
| **deer** (A) | AnF · deer_fallow · 64 px · 17/17<br>AnF · deer · 96 px · 19/21<br>AnF · deer_reindeer · 96 px · 19/21<br>AnF · deer_roe · 64 px · 17/17<br>WA · deer · 128 px · 53/20<br>WS · deer · None px · 13/10<br>WWA · deer · 64 px · 13/10<br>YTri · cervof · 128 px · 39/26<br>YTri · cervom · 256 px · 57/43 | sf_nba:deer |
| **desert_owl** (A) | WS · desert_owl · None px · 16/16<br>WWA · desert_owl · 64 px · 16/16 | — |
| **dove** (A) | AnF · dove_collar · 32 px · 11/12<br>AnF · dove_diamond · 32 px · 11/12<br>AnF · dove_green · 32 px · 11/12<br>AnF · dove_mourning · 32 px · 11/12<br>WA · dove · 128 px · 26/26 | — |
| **dragonfly** (B) | AnF · dragonfly_desert · 32 px · 12/13<br>AnF · dragonfly_emerald · 32 px · 12/13<br>AnF · dragonfly_greendarner · 32 px · 12/13<br>AnF · dragonfly_roseateskimmer · 32 px · 12/13<br>AnF · dragonfly_swampdarner · 32 px · 12/13 | sf_nba:dragonfly |
| **duck** (A) | AnF · duck_bali · 32 px · 11/11<br>AnF · duck_goldencascade · 48 px · 11/10<br>AnF · duck_indianrunner · 32 px · 11/11<br>AnF · duck_kingeider · 48 px · 16/10<br>AnF · duck_madagascar · 48 px · 16/10<br>AnF · duck_mallard · 48 px · 16/10<br>AnF · duck_mandarin · 48 px · 16/10<br>AnF · duck_pekin · 48 px · 11/10<br>WA · duck · 128 px · 21/26 | sf_nba:duck |
| **eagle** (A) | AnF · eagle_bald · 64 px · 25/22<br>AnF · eagle_blackhawk · 64 px · 25/22<br>AnF · eagle_crowned · 64 px · 25/22<br>AnF · eagle_golden · 64 px · 25/22<br>AnF · eagle_sea · 64 px · 25/22<br>AnF · eagle_whitetailed · 64 px · 25/22<br>WA · eagle · 128 px · 50/36<br>YSav · aguia_africana · 128 px · 38/25<br>YSav · aguia_pescadora · 128 px · 38/25<br>YTri · aguia · 64 px · 18/11 | sf_nba:eagle |
| **elephant** (A) | AnF · elephant_african · 192 px · 27/20<br>AnF · elephant_asian · 192 px · 27/20<br>IFS · elefante · 128 px · 17/19<br>WA · african_elephant · 512 px · 61/37<br>WA · asian_elephant · 512 px · 46/37<br>WS · elephant · None px · 12/11<br>WWA · elephant · 256 px · 12/11<br>YSav · elefante · 128 px · 57/41<br>YTri · elefante · 128 px · 29/22 | sf_nba:elephant |
| **emu** (A) | WWA · emu · 64 px · 19/10<br>YTri · emu · 128 px · 18/18 | — |
| **fennec** (A) | WWA · fennec · 32 px · 10/14<br>YTri · feneco · 64 px · 10/9 | sf_nba:fennec_fox |
| **ferret** (A) | AnF · ferret_common · 32 px · 14/17<br>WWA · ferret · 64 px · 10/8 | — |
| **firefly** (A) | AnF · firefly · 16 px · 13/19<br>WA · lucienaga · 32 px · 8/15<br>WWA · firefly · 16 px · 1/1 | sf_nba:firefly |
| **flamingo** (A) | AnF · flamingo_american · 48 px · 16/18<br>AnF · flamingo_andean · 48 px · 16/18<br>AnF · flamingo_greater · 48 px · 16/18<br>AnF · flamingo_james · 48 px · 16/18<br>WA · flamingo · 128 px · 23/13<br>WWA · flamingo · 64 px · 11/9 | sf_nba:flamingo |
| **gazelle** (A) | IFS · gacela · 64 px · 13/15<br>WWA · gazelle · 64 px · 14/9<br>YSav · gazela · 128 px · 32/28<br>YSav · gazelaf · 128 px · 32/28 | — |
| **gelada** (A) | WS · gelada · None px · 14/8<br>WWA · gelada · 64 px · 14/8 | — |
| **gila_monster** (A) | WS · gila_monster · None px · 9/10<br>WWA · gila_monster · 128 px · 9/10 | — |
| **giraffe** (A) | AnF · giraffe_masai · 112 px · 29/18<br>AnF · giraffe_nubian · 112 px · 29/18<br>AnF · giraffe_reticulated · 112 px · 29/18<br>AnF · giraffe_southafrican · 112 px · 29/18<br>IFS · jirafa · 128 px · 39/13<br>WA · giraffe · 256 px · 41/17<br>WS · giraffe · None px · 15/13<br>WWA · giraffe · 64 px · 15/13<br>YSav · girafa · 128 px · 53/31<br>YTri · girafa · 256 px · 34/26 | sf_nba:giraffe |
| **gnu** (A) | YSav · gnu · 128 px · 42/28<br>YTri · gnu · 256 px · 73/39 | — |
| **goose** (B) | AnF · goose_barnacle · 64 px · 14/11<br>AnF · goose_canada · 64 px · 14/11<br>AnF · goose_egyptian · 64 px · 14/11<br>AnF · goose_magellan · 64 px · 14/11<br>AnF · goose_roman · 64 px · 14/11 | sf_nba:goose |
| **gorilla** (A) | AnF · gorilla · 80 px · 18/18<br>AnF · gorilla · 80 px · 18/18<br>WA · gorilla · 256 px · 22/11<br>WS · gorilla · None px · 9/10<br>WWA · gorilla · 128 px · 9/10<br>YTri · gorila · 128 px · 23/23 | sf_nba:gorilla |
| **hammerhead_shark** (A) | WA · hammerhead_shark · 512 px · 45/28<br>WWA · hammer · 128 px · 15/11 | sf_nba:hammer_head_shark |
| **hamster** (A) | AnF · hamster_dwarf · 48 px · 11/15<br>AnF · hamster_syrian · 48 px · 11/15<br>WS · hamster · None px · 10/7<br>WWA · hamster · 64 px · 10/7 | sf_nba:hamster |
| **hedgehog** (A) | AnF · hedgehog_desert · 32 px · 23/24<br>AnF · hedgehog_euro · 32 px · 23/24<br>AnF · hedgehog_longeared · 32 px · 23/24<br>AnF · hedgehog_madras · 32 px · 23/24<br>AnF · hedgehog_southafrican · 32 px · 23/24<br>WA · erizo · 64 px · 13/18<br>WWA · hedgehog · 64 px · 12/2 | sf_nba:hedgehog |
| **hippo** (A) | AnF · hippo · 144 px · 26/17<br>WA · hippopotamus · 256 px · 46/16<br>WS · hippo · None px · 9/9<br>WWA · hippo · 128 px · 9/9<br>YSav · hipopotamo · 256 px · 48/28 | sf_nba:hippo |
| **hornbill** (A) | WS · hornbill · None px · 11/10<br>WWA · hornbill · 64 px · 11/10 | — |
| **hummingbird** (A) | WS · hummingbird · None px · 8/8<br>WWA · hummingbird · 32 px · 8/8<br>YTri · beijaflor · 32 px · 10/8 | — |
| **hyena** (A) | AnF · hyena · 48 px · 22/21<br>IFS · hiena · 64 px · 14/8<br>WA · hyenas · 512 px · 31/7<br>WA · hyenas · 512 px · 31/7<br>YSav · hiena · 128 px · 37/32 | sf_nba:hyena, sf_nba:ravenous_hyena |
| **iguana** (A) | AnF · iguana · 64 px · 17/13<br>WA · iguana · 128 px · 44/10 | sf_nba:iguana |
| **jellyfish** (A) | WA · jellyfish_wa · 128 px · 53/50<br>YTri · agua_viva · 128 px · 47/15 | sf_nba:jellyfish, sf_nba:small_jellyfish |
| **kakapo** (B) | WWA · kakapo · 32 px · 10/8 | sf_nba:kakapo |
| **kangaroo** (A) | AnF · kangaroo · 80 px · 27/25<br>WA · kangaroo · 256 px · 30/18<br>WS · kangaroo · None px · 17/13<br>WWA · kangaroo · 128 px · 17/13<br>YTri · canguru · 256 px · 25/28 | sf_nba:kangaroo |
| **kiwi** (A) | WA · kiwi · 128 px · 10/5<br>YTri · kiwi · 32 px · 9/4 | sf_nba:kiwi |
| **komodo_dragon** (A) | WA · komodo_dragon · 256 px · 48/14<br>YTri · komodo · 256 px · 37/35 | sf_nba:komodo_dragon |
| **ladybug** (A) | AnF · ladybug_15spotted · 32 px · 13/20<br>AnF · ladybug_22spotted · 32 px · 13/20<br>AnF · ladybug_7spotted · 32 px · 13/20<br>AnF · ladybug_9spotted · 32 px · 13/20<br>AnF · ladybug_harlequin · 32 px · 13/20<br>WWA · ladybug · 32 px · 10/7 | — |
| **lemur** (A) | AnF · lemur_goldenbamboo · 32 px · 22/21<br>AnF · lemur_mouse · 32 px · 14/17<br>AnF · lemur_mouse · 32 px · 14/17<br>AnF · lemur_redruffed · 32 px · 22/21<br>AnF · lemur_ringtailed · 32 px · 22/21<br>AnF · lemur_sportive · 32 px · 22/21<br>YTri · lemure · 128 px · 46/35 | — |
| **leopard** (A) | AnF · leopard_clouded · 80 px · 31/27<br>AnF · leopard_jungle · 80 px · 31/27<br>AnF · leopard_panther · 80 px · 31/27<br>AnF · leopard_snow · 80 px · 31/27<br>WA · leopard · 256 px · 45/18<br>WA · panther · 256 px · 45/18<br>YSav · leopardo_africano · 256 px · 32/38 | — |
| **lion** (A) | AnF · lioness_african · 80 px · 45/30<br>AnF · lioness_asiatic · 80 px · 44/30<br>AnF · lioness_transvaal · 80 px · 45/30<br>AnF · lion_african · 80 px · 45/30<br>AnF · lion_asiatic · 80 px · 44/30<br>AnF · lion_transvaal · 80 px · 45/30<br>IFS · leon_m · 128 px · 37/27<br>IFS · leon_f · 128 px · 32/27<br>WA · lion · 256 px · 51/28<br>WA · white_lion · 256 px · 51/28<br>WWA · lion · 64 px · 11/12<br>YSav · baby_lion · 128 px · 26/26<br>YSav · leao · 256 px · 46/33<br>YSav · leao_branco · 256 px · 46/33<br>YSav · leoa · 256 px · 30/34<br>YSav · leoa_branca · 256 px · 30/34 | sf_nba:female_lion, sf_nba:lion, sf_nba:male_lion |
| **lizard** (B) | YTri · calango · 64 px · 27/21 | sf_nba:lizard |
| **lynx** (A) | WS · lynx · None px · 14/10<br>WWA · lynx · 64 px · 14/10 | — |
| **mammoth** (B) | WA · mammoth · 512 px · 65/37 | sf_nba:mammoth |
| **meerkat** (A) | AnF · meerkat · 32 px · 12/14<br>WWA · meerkat · 64 px · 10/7<br>YTri · suricato · 64 px · 23/13 | — |
| **mole** (A) | AnF · mole · 32 px · 11/12<br>YTri · toupeira · 128 px · 18/7 | sf_nba:mole |
| **monkey** (A) | AnF · monkey_howler · 48 px · 26/22<br>AnF · monkey_spider · 48 px · 26/22<br>AnF · monkey_squirrel · 48 px · 26/22<br>WS · howler_monkey · None px · 21/23 | sf_nba:monkey |
| **moose** (A) | AnF · moose_alaskan · 96 px · 42/27<br>AnF · moose_canadian · 96 px · 42/27<br>YTri · alcef · 128 px · 36/34<br>YTri · alcem · 128 px · 68/48 | sf_nba:moose |
| **octopus** (A) | AnF · octopus_blueringed · 48 px · 20/24<br>AnF · octopus_common · 48 px · 20/24<br>AnF · octopus_pacificgiant · 48 px · 20/24<br>YTri · polvo · 128 px · 12/13 | sf_nba:octopus |
| **orangutan** (A) | AnF · orangutan · 80 px · 27/16<br>YTri · orangotango · 128 px · 24/24 | — |
| **orca** (A) | WA · orca · 256 px · 15/8<br>WWA · orca · 256 px · 9/9<br>YTri · orca · 256 px · 13/11 | sf_nba:orca |
| **ostrich** (A) | AnF · ostrich · 64 px · 28/16<br>IFS · avestruz · 128 px · 19/10<br>WA · ostrich · 256 px · 30/26<br>WS · ostrich · None px · 10/7<br>WWA · ostrich · 128 px · 10/7<br>YSav · avestruz · 128 px · 46/29 | sf_nba:ostrich |
| **otter** (A) | AnF · otter_river · 48 px · 21/16<br>AnF · otter_sea · 48 px · 21/16<br>AnF · otter_spotted · 48 px · 21/16<br>YTri · lontra · 128 px · 26/24 | sf_nba:otter |
| **owl** (A) | AnF · owl_barn · 48 px · 14/12<br>AnF · owl_snowy · 48 px · 14/12<br>AnF · owl_tawny · 48 px · 14/12<br>YTri · coruja · 128 px · 20/10<br>YTri · suindara · 128 px · 16/12 | sf_nba:owl |
| **peacock** (B) | WWA · peacock · 64 px · 18/8 | sf_nba:peafowl |
| **pelican** (A) | AnF · pelican_americanwhite · 80 px · 20/15<br>AnF · pelican_australian · 80 px · 20/15<br>AnF · pelican · 80 px · 20/15<br>AnF · pelican_greatwhite · 80 px · 20/15<br>WA · pelican · 256 px · 24/17<br>WWA · pelican · 64 px · 11/9 | — |
| **penguin** (A) | AnF · penguin_chinstrap · 32 px · 17/13<br>AnF · penguin_emperor · 48 px · 13/11<br>AnF · penguin_gentoo · 32 px · 17/13<br>AnF · penguin_king · 32 px · 11/11<br>AnF · penguin_macaroni · 32 px · 17/13<br>AnF · penguin_magellanic · 32 px · 17/13<br>AnF · penguin_rockhopper · 32 px · 17/13<br>WA · blue_penguin · 128 px · 13/9<br>WA · emperor_penguin · 128 px · 16/9<br>WA · penguin · 128 px · 16/20<br>WA · penguin_african · 128 px · 13/9<br>WWA · penguin · 64 px · 9/10<br>YTri · imperador · 256 px · 19/13 | sf_nba:emperor_penguin |
| **piranha** (B) | YTri · piranha · 32 px · 10/8 | sf_nba:piranha |
| **platypus** (A) | AnF · platypus · 32 px · 8/12<br>WA · ornitorrinco_original · 128 px · 24/7<br>YTri · ornintorrinco · 32 px · 13/8 | sf_nba:platypus |
| **raccoon** (A) | AnF · raccoon · 48 px · 17/16<br>WA · raccoon · 128 px · 21/10<br>WWA · racoon · 64 px · 10/8 | sf_nba:raccoon |
| **rat** (A) | AnF · rat · 32 px · 9/14<br>AnF · rat · 32 px · 9/14<br>AnF · rat_fancy · 32 px · 9/14<br>AnF · rat_marsh · 32 px · 9/14<br>AnF · rat_pack · 32 px · 9/14<br>WA · rat · 128 px · 21/9 | sf_nba:rat |
| **rattlesnake** (A) | WS · tiger_rattlesnake · None px · 9/11<br>WWA · tiger_rattlesnake · 64 px · 9/11 | sf_nba:rattlesnake |
| **raven** (B) | AnF · raven_common · 48 px · 10/12<br>AnF · raven_whitenecked · 48 px · 10/12 | sf_nba:raven |
| **red_panda** (A) | WA · red_panda · 128 px · 27/21<br>WWA · red_panda · 64 px · 10/10<br>YTri · panda_vermelho · 64 px · 10/7 | sf_nba:red_panda |
| **rhino** (A) | AnF · rhino · 128 px · 29/24<br>AnF · rhino_indian · 128 px · 29/24<br>AnF · rhino_sumatran · 128 px · 29/24<br>AnF · rhino · 128 px · 29/24<br>WA · rhinoceros · 512 px · 114/26<br>WS · rhino · None px · 12/8<br>WWA · rhino · 128 px · 12/8<br>YSav · rinoceronte · 256 px · 38/27 | sf_nba:rhino |
| **river_dolphin** (A) | WA · pink_dolphin · 256 px · 14/10<br>YTri · boto · 64 px · 14/13 | — |
| **robin** (B) | AnF · robin · 32 px · 12/11 | sf_nba:robin |
| **scorpion** (A) | AnF · scorpion_deathstalker · 48 px · 28/24<br>AnF · scorpion_giantdesert · 48 px · 28/24<br>AnF · scorpion_giantforest · 48 px · 28/24<br>AnF · scorpion_indianred · 48 px · 28/24<br>WS · bark_scorpion · None px · 20/18<br>WWA · bark_scorpion · 64 px · 20/18 | sf_nba:desert_scorpion, sf_nba:jungle_scorpion |
| **seagull** (A) | AnF · gull_blackheaded · 32 px · 17/18<br>AnF · gull_bonaparte · 32 px · 17/18<br>AnF · gull_common · 32 px · 17/18<br>AnF · gull_greatblackbacked · 32 px · 17/18<br>AnF · gull_herring · 32 px · 17/18<br>AnF · gull_kittiwake · 32 px · 17/18<br>AnF · gull_lesserblackbacked · 32 px · 17/18<br>WA · seagull · 128 px · 19/16<br>WWA · seagull · 128 px · 10/8 | — |
| **seal** (A) | AnF · seal_common · 64 px · 9/11<br>AnF · seal · 64 px · 9/11<br>AnF · seal_harp · 64 px · 9/11<br>WA · seal · 256 px · 11/8<br>WWA · seal · 64 px · 7/8<br>YTri · foca · 128 px · 22/18 | sf_nba:seal |
| **secretary_bird** (B) | YSav · secretary_bird · 64 px · 25/15 | sf_nba:secretary_bird |
| **shark** (A) | AnF · shark_greatwhite · 96 px · 18/17<br>AnF · shark_hammerhead · 96 px · 18/17<br>AnF · shark_lemon · 64 px · 15/17<br>AnF · shark_tiger · 64 px · 15/17<br>WA · shark · 512 px · 36/28<br>WA · tiger_shark · 512 px · 36/28<br>WA · white_shark · 512 px · 36/28<br>WWA · thresher_shark · 64 px · 11/8<br>YTri · tubarao · 128 px · 12/11 | sf_nba:great_white_shark |
| **shrimp** (A) | WA · shrimp · 128 px · 25/14<br>WWA · bumblebee_shrimp · 64 px · 12/9 | — |
| **skunk** (B) | AnF · skunk · 48 px · 19/17 | sf_nba:skunk |
| **sloth** (B) | YTri · preguica · 256 px · 26/19 | sf_nba:sloth |
| **slug** (B) | AnF · slug_europeanred · 32 px · 6/7<br>AnF · slug_leopard · 32 px · 6/7<br>AnF · slug_spanish · 32 px · 6/7 | sf_nba:slug |
| **snail** (A) | AnF · snail_candycane · 32 px · 6/8<br>AnF · snail_desert · 32 px · 6/8<br>AnF · snail_garden · 32 px · 6/8<br>AnF · snail_giantafrican · 64 px · 11/9<br>AnF · snail_milk · 32 px · 6/8<br>WA · snail · 64 px · 8/1 | sf_nba:snail |
| **snake** (A) | AnF · snake_anaconda_green · 64 px · 15/17<br>AnF · snake_anaconda_yellow · 64 px · 15/17<br>AnF · snake_boa_kenyansand · 64 px · 15/17<br>AnF · snake_cobra_indian · 64 px · 27/21<br>AnF · snake_cobra_king · 64 px · 27/21<br>AnF · snake_corn · 32 px · 10/13<br>AnF · snake_garter_butler · 32 px · 10/13<br>AnF · snake_garter_california · 32 px · 10/13<br>AnF · snake_mamba · 64 px · 12/15<br>AnF · snake_mamba_easterngreen · 64 px · 12/15<br>AnF · snake_milk · 32 px · 10/13<br>AnF · snake_python_greentree · 64 px · 15/17<br>AnF · snake_python_pastel · 64 px · 15/17<br>AnF · snake_python_royal · 64 px · 15/17<br>AnF · snake_rattle_diamondback · 64 px · 27/21<br>AnF · snake_rattle_timber · 64 px · 27/21<br>AnF · snake_viper_blue · 64 px · 27/21<br>AnF · snake_viper_horned · 64 px · 27/21<br>AnF · snake_water · 32 px · 10/13<br>AnF · snake_water_plainbellied · 32 px · 10/13<br>WA · snake · 128 px · 20/14<br>WA · snake_coral · 128 px · 16/14<br>WA · snake_scarlet · 128 px · 16/14 | sf_nba:cave_snake, sf_nba:coral_snake, sf_nba:snake |
| **snapping_turtle** (A) | WWA · snapping_turtle · 64 px · 12/10<br>YTri · tartaruga_alligator · 128 px · 51/22 | — |
| **squirrel** (A) | AnF · squirrel · 48 px · 15/16<br>AnF · squirrel · 48 px · 15/16<br>WA · squirrel · 64 px · 14/8<br>WS · squirrel · None px · 10/8<br>WWA · squirrel · 64 px · 10/8 | sf_nba:squirrel |
| **starfish** (B) | AnF · shellfish_starfish · 24 px · 6/15 | sf_nba:starfish |
| **stingray** (A) | WA · stingray · 128 px · 13/10<br>WWA · manta_ray · 128 px · 12/10<br>YTri · arraia · 128 px · 37/11 | sf_nba:ray |
| **stork** (A) | AnF · stork_adjutant · 64 px · 17/19<br>AnF · stork · 48 px · 17/19<br>AnF · stork_blacknecked · 64 px · 17/19<br>AnF · stork_oriental · 48 px · 17/19<br>AnF · stork_painted · 48 px · 17/19<br>AnF · stork_saddlebilled · 64 px · 17/19<br>AnF · stork · 48 px · 17/19<br>AnF · stork_wood · 48 px · 17/19<br>WA · stork · 128 px · 29/33<br>YSav · marabu · 256 px · 40/34 | — |
| **swan** (A) | AnF · swan · 64 px · 14/12<br>AnF · swan · 64 px · 14/12<br>WWA · swan · 64 px · 11/14<br>YTri · cisne · 64 px · 15/12 | — |
| **tapir** (A) | WS · tapir · None px · 9/8<br>WWA · tapir · 64 px · 9/8<br>YTri · anta · 64 px · 19/9 | — |
| **termite** (A) | AnF · termite · 32 px · 10/15<br>YSav · cupim · 32 px · 10/12 | sf_nba:termite |
| **tiger** (A) | AnF · tiger_bengal · 80 px · 31/27<br>AnF · tiger_siberian · 80 px · 31/27<br>AnF · tiger_southchina · 80 px · 31/27<br>WA · tiger · 256 px · 45/18<br>WA · white_tiger · 256 px · 45/18<br>WS · tiger · None px · 12/10<br>WWA · tiger · 128 px · 12/10 | sf_nba:tiger |
| **tortoise** (A) | AnF · tortoise_desert · 40 px · 7/10<br>AnF · tortoise_greek · 40 px · 7/10<br>WA · land_turtle · 128 px · 15/8<br>WWA · sulcata_turtle · 128 px · 7/8<br>YSav · jabuti · 256 px · 31/20 | sf_nba:tortoise |
| **toucan** (A) | AnF · toucan_aracari · 48 px · 13/12<br>AnF · toucan_channelbilled · 48 px · 13/12<br>AnF · toucan_toco · 48 px · 13/12<br>WA · tucan · 128 px · 24/13<br>YTri · tucano · 64 px · 17/8 | sf_nba:toucan |
| **turkey** (B) | WA · turkey · 128 px · 18/12 | sf_nba:turkey |
| **vulture** (A) | AnF · vulture_king · 48 px · 26/20<br>AnF · vulture_redheaded · 48 px · 26/20<br>WA · vulture · 256 px · 51/38<br>YTri · urubu · 64 px · 16/13 | sf_nba:vulture |
| **walrus** (B) | AnF · walrus · 64 px · 12/12 | sf_nba:walrus |
| **whale** (A) | WA · ballena · 256 px · 20/11<br>WWA · humpback_whale · 256 px · 16/10<br>YTri · baleia · 128 px · 8/8 | sf_nba:whale |
| **yak** (A) | WS · yak · None px · 28/11<br>WWA · yak · 128 px · 28/11 | — |
| **zebra** (A) | AnF · zebra_mountain · 80 px · 21/16<br>AnF · zebra_plains · 80 px · 21/16<br>IFS · zebra · 64 px · 12/14<br>WA · zebra · 256 px · 29/29<br>WWA · zebra · 64 px · 23/22<br>YSav · zebra · 128 px · 33/33<br>YTri · zebra · 128 px · 23/24 | sf_nba:zebra |

## VANILLA (Patrix covers the base mob)

| Animal | Add-on versions |
|---|---|
| bat | 6: AnF:bat_easternred, AnF:bat_fox_bigeared, AnF:bat_fox_golden, AnF:bat_fruit, AnF:bat_fruit_seychelles, AnF:bat_vampire |
| bee | 4: AnF:bee_bumble, AnF:bee_greensweat, AnF:bee_honey, AnF:bee_mason |
| camel | 3: AnF:camel_bactrian, AnF:camel_dromedary, YTri:camelo |
| chicken | 15: AnF:chicken_friesian, AnF:chicken_leghorn, AnF:chicken_minorca, AnF:chicken_plymouthrock, AnF:chicken_rhodeislandred, AnF:chick_friesian, AnF:chick_leghorn, AnF:chick_minorca, AnF:chick_plymouthrock, AnF:chick_rhodeislandred, AnF:rooster_friesian, AnF:rooster_leghorn … |
| cow | 32: AnF:bull_ankole, AnF:bull_ankole_black_spots, AnF:bull_ankole, AnF:bull_ankole_brown_spots, AnF:bull_ankole, AnF:bull_ankole_red_spots, AnF:bull_highland_beige, AnF:bull_highland, AnF:bull_highland, AnF:bull_highland_ginger, AnF:bull_holstein, AnF:bull_holstein … |
| dolphin | 3: AnF:dolphin_bottlenose, AnF:dolphin_commerson, AnF:dolphin_striped |
| frog | 15: AnF:frog_dart_blue, AnF:frog_dart_golden, AnF:frog_desert, AnF:frog_glass_blue, AnF:frog_glass_green, AnF:frog_glass_yellow, AnF:frog_goliath, AnF:frog_horned_amazon, AnF:frog_horned_argentine, AnF:frog_pond, AnF:frog_tree_clown, AnF:frog_tree_green … |
| goat | 12: AnF:goat_dom_blackneck, AnF:goat_dom_golden, AnF:goat_dom_nubian, AnF:goat_dom_sable, AnF:goat_dwarf_nigerian, AnF:goat_dwarf_pygmy, AnF:goat_ibex_alpine, AnF:goat_ibex_iberian, AnF:goat_ibex_nubian, AnF:goat_ibex_walia, AnF:goat_markhor, AnF:goat_wild |
| horse | 16: AnF:horse_clydesdale, AnF:horse_clydesdale_chestnut, AnF:horse_clydesdale_ginger, AnF:horse_fjord_beige, AnF:horse_fjord, AnF:horse_fjord_ginger, AnF:horse_shetland_beige, AnF:horse_shetland, AnF:horse_shetland, AnF:horse_shetland_chestnut, AnF:horse_shetland, AnF:horse_shire_beige … |
| panda | 1: AnF:panda |
| parrot | 16: AnF:parakeet_budgie_blue, AnF:parakeet_budgie_green, AnF:parakeet_budgie_yellow, AnF:parakeet_caique, AnF:parakeet_plumheaded, AnF:parakeet_yellowchevroned, AnF:parrot_africangrey, AnF:parrot_amazon, AnF:parrot_cockatoo, AnF:parrot_conure_golden, AnF:parrot_lovebird_blue, AnF:parrot_lovebird_green … |
| pig | 11: AnF:pig_gloucester, AnF:pig_hampshire, AnF:pig_hereford, AnF:pig_hungarian, AnF:pig_largeblack, AnF:pig_largewhite, AnF:pig_mini, AnF:pig_minispotted, AnF:pig_oxfordsandy, AnF:pig_swabianhall, AnF:pig_vietnamese |
| polar_bear | 1: AnF:bear_polar |
| rabbit | 27: AnF:rabbit_cottontail, AnF:rabbit_cottontail, AnF:rabbit_cottontail, AnF:rabbit_dom, AnF:rabbit_dom_blue, AnF:rabbit_dom, AnF:rabbit_dom_ginger, AnF:rabbit_dom, AnF:rabbit_dom, AnF:rabbit_dom_sand, AnF:rabbit_euro, AnF:rabbit_euro … |
| sheep | 5: AnF:sheep_blackface, AnF:sheep_damara, AnF:sheep_jacob, AnF:sheep_merino, AnF:sheep_suffolk |
| spider | 8: AnF:spider_birdeater, AnF:spider_blackwidow, AnF:spider_desertwolf, AnF:spider_funnelweb, AnF:spider_garden, AnF:spider_huntsman, AnF:spider_mexicanpink, AnF:spider_swamp |
| turtle | 3: AnF:turtle_mud_common, AnF:turtle_mud_yellow, AnF:turtle_sea_leatherback |
| wolf | 4: AnF:wolf_alexander, AnF:wolf_arctic, AnF:wolf, AnF:wolf |

## NEW (port list)

| Animal | Source · keys |
|---|---|
| african_wild_dog | YSav · mabeco |
| alpaca | YTri · alpaca |
| anaconda | WS · anaconda |
| archelon | JP · archel |
| baby_african_eagle | YSav · baby_african_eagle |
| baby_fisher_eagle | YSav · baby_fisher_eagle |
| beluga | YTri · beluga |
| bird_of_paradise | WWA · cendrawasih |
| bison | YTri · bisao |
| bongo | YTri · bongo |
| caiman | YTri · jacare |
| caracal | WA · caracal |
| centipede | AnF · centipede, centipede_common, centipede_desert, centipede_pacificgiant |
| chameleon | AnF · chameleon |
| cheetah | YSav · guepardo |
| clam | AnF · shellfish_clam |
| cobra | YSav · naja |
| cougar | WA · cougar |
| crane | AnF · crane_common, crane_hooden, crane_siberian, crane_whopping |
| dik_dik | YTri · dik_dik |
| dog | AnF · dog_alsatian, dog_lab, dog_lab_chocolate, dog_lab_golden, dog_retriever_golden, dog_retriever |
| earthworm | AnF · earthworm_common, earthworm_gippsland, earthworm_nightcrawler |
| egret | AnF · egret_great, egret_little, egret_reddish |
| fly | AnF · fly_bluebottle, fly_dung, fly_fruit, fly_horse, fly_hover |
| gavial | YTri · gavial |
| gecko | AnF · gecko, gecko_blue, gecko_leopard, gecko_yellow |
| gerbil | AnF · gerbil |
| giant_squid | WWA · gaint_squid |
| grasshopper | AnF · grasshopper |
| hare | AnF · hare_arctic, hare_blacktailed, hare_european, hare_mountain |
| hawk | AnF · hawk, hawk_harrier, hawk_harris, hawk_sparrow |
| heron | AnF · heron_agami, heron, heron_blackcrowned, heron_greatblue, heron_green, heron |
| honey_badger | YSav · ratel |
| hornet | AnF · hornet_asian, hornet_european |
| impala | YSav · impala, impalaf |
| jay | AnF · jay |
| jellyfish_jp | JP · jellyfish |
| jerboa | WWA · jerboa |
| koala | YTri · coala |
| kob | YSav · kobo, kobof |
| lantern_fish | WA · lantern_fish |
| leedsichthys | JP · leed |
| lemming | AnF · lemming_arctic, lemming_bog, lemming_norway, lemming_yellowsteppe |
| lobster | AnF · lobster |
| magpie | AnF · magpie |
| manatee | YTri · peixe_boi |
| mandrill | AnF · mandrill |
| megalodon | JP · meg |
| monitor_lizard | YSav · monitor |
| mosasaurus | JP · mosa, r_mosa |
| moth | AnF · moth_atlas, moth_comet, moth_emperor, moth_gardentiger, moth_giantleopard, moth_gypsy, moth_luna, moth_rosymaple |
| mouse | AnF · mouse_harvest, mouse_house, mouse_jumping, mouse_wood |
| newt | AnF · newt_crested, newt_eastern, newt_emperor, newt_firebelly |
| nyala | YSav · inhala, inhalaf |
| opossum | YTri · gamba |
| oryx | YSav · oryx |
| pangolin | YSav · pangolin |
| pigeon | AnF · pigeon_africanolive, pigeon_passenger, pigeon_rock, pigeon_wood |
| prairie_dog | WWA · prarie_dog |
| puffin | AnF · puffin |
| quetzalcoatlus | JP · fb_quetz, b_quetz |
| roadrunner | WWA · road_runner |
| sable_antelope | YSav · palanca |
| saiga | WWA · saiga |
| scallop | AnF · shellfish_scallop |
| sea_urchin | AnF · shellfish_seaurchin |
| sealion | AnF · sealion |
| serval | YSav · serval |
| shoebill | WWA · shoebill |
| snow_leopard | WA · snow_leopard |
| spinosaurus | JP · spino |
| stick_insect | AnF · stickinsect_goliath |
| stoat | AnF · stoat_british, stoat_irish, stoat_japanese, stoat_russian |
| swordfish | WA · swordfish |
| t_rex | JP · r_rex |
| tern | AnF · tern, tern_caspian, tern_common, tern_crested, tern_fairy, tern_largebilled, tern_sooty |
| tit | AnF · tit_bearded, tit_blue, tit_coal, tit_crested, tit_great, tit_longtailed, tit_marsh, tit_willow |
| titanosaurus | JP · titano |
| toad | AnF · toad_africangiant, toad_canadian, toad_european, toad_indian, toad_yosemite |
| toadfish | WWA · toadfish |
| viper | YSav · vibora |
| wasp | AnF · wasp_paper, wasp_yellowjacket |

## PROPS

AnF:egg_ostrich, AnF:horn_buffalo_e, AnF:horn_bull_e, AnF:horn_deer_e, AnF:horn_elephant_e, AnF:horn_moose_e, AnF:horn_rhino_e, WA:african_penguin_egg, WA:bag_items, WA:blue_penguin_egg, WA:clam, WA:duck_egg, WA:emperor_penguin_egg, WA:ostrich_egg, WA:real_penguin_egg, WA:turkey_egg, WA:village_ice, WA:village_wild, JP:titano_egg, JP:titano_cracked_egg, JP:carnivore_feeder, JP:piscivore_feeder, JP:archelon_feeder, JP:spino_egg, JP:spino_cracked_egg, JP:mosa_egg, JP:fb_quetz_egg, JP:fb_quetz_cracked_egg, JP:r_mosa_egg, JP:archel_egg, JP:archel_cracked_egg, JP:r_rex_egg, JP:r_rex_cracked_egg, JP:banner, JP:hanging_banner, JP:b_quetz_egg, JP:b_quetz_cracked_egg, JP:leed_egg, JP:meg_sac, JP:chair, WWA:beekeeper, YSav:baobab_boat, YSav:baobab_chest_boat, YSav:naja_egg, YSav:naja_spit, YSav:nomad, YSav:safari_car, YSav:vibora_egg
