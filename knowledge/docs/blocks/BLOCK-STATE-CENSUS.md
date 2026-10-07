# Block-state census — 2026-09-30 (his GO, D-C309 item 5)

The load log: `World with over 65536 block permutations may degrade performance. Current world has 66346 permutations.`

Our custom blocks: **471 blocks, 64,728 permutations** (states x traits), = 97.6% of the game's count -> the warning counts the custom blocks (the rest ~1,618 = packs outside this census).

| family | blocks | permutations | share |
|---|---|---|---|
| leaves | 12 | 48,390 | 74.8% |
| slabs / stairs | 106 | 6,660 | 10.3% |
| walls | 56 | 3,548 | 5.5% |
| ground / stone | 23 | 2,900 | 4.5% |
| other | 97 | 1,688 | 2.6% |
| homestead | 108 | 1,174 | 1.8% |
| furniture | 36 | 180 | 0.3% |
| roof pieces | 24 | 164 | 0.3% |
| plants | 9 | 24 | 0.0% |

**The 9 leaf blocks (pw:<wood>_leaves) = 48,384 (75%)** — 5,376 each = variant 7 x rseed 2 x section 3 x exposure 2 x section_rolled 2 x far 2 x open_n 2 x open_e 2 x open_s 2 x open_w 2.

| leaf state | values | what reads it (BP-02 1.3.193) | verdict |
|---|---|---|---|
| pw:variant | 7 | the block's 7 permutation rules (which leaf model/texture draws) | NEEDED |
| pw:rseed | 2 | the randomizer: 'already randomized' mark | needed by the scanner |
| pw:section | 3 | variant pool choice (section x exposure) | needed |
| pw:exposure | 2 | variant pool choice | needed |
| pw:section_rolled | 2 | scanner: 'already marked' + the reverse-randomizer clears it | needed |
| **pw:far** | 2 | **nothing** — never read, never written (the 'far' idea became variant 0 = opaque) | **DEAD** |
| **pw:open_n/e/s/w** | 2 x 2 x 2 x 2 | **written** by the scanner (air on each side), **never read** by any rule or script | **write-only** |

Cut options (his pick):
- drop pw:far -> leaves 24,192 -> world ~42,154
- drop open_n/e/s/w -> leaves 3,024 -> world ~20,986
- drop both -> leaves 1,512 -> world ~19,474

Risk: leaf blocks already placed in a world carry the removed states; the engine has to map them onto the new definition. Test in a COPY of the test world before the Realm.
