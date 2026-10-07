# HANDOFF — 2026-10-03 — LIGHT-BLOCK FIX: BP-02 1.3.214 + TestRunner 0.5.20

SUPPLEMENT to `HANDOFF-2026-10-03-REVIEW-WINDOW-1003e-f.md` (that document is still the source for everything not listed here). Journal D-C514 / D-C515. Found during the review window, while I was checking which saved data survives a server restart.

## Install (replaces the earlier numbers)
| Pack | Version | Replaces |
|---|---|---|
| **BP-02 Tectonic BP** | **1.3.214** | 1.3.207 … 1.3.212. **1.3.213 was never delivered** — it is held for your question 6, and its number is never reused |
| **PW-TestRunner BP** | **0.5.20** | 0.5.19 (the only change: the p22 / p23 setup texts name 1.3.214) |
| RP-01 1.3.118 · RP-07 1.4.45 · RP-08 1.4.14 · all the rest | unchanged | |

Content log after loading: `[PW-VERSION] BP-02 v1.3.214`, `[TREEGROW] BOOT v1.3.214`, `PW Test Runner BP v0.5.20`, `[CIV-CLOCK] village clock loaded — 38 staged building(s)`. **Your tests: p22 (CIVITAS) and p23 (TREES).** Apart from the light fix, 1.3.214 is identical to 1.3.212.

## The defect
Bedrock 1.26 gives the light block a separate id for each brightness level: the block placed for level 13 reports `minecraft:light_block_13`. Two of our systems remove their light only when the block reads exactly `minecraft:light_block`:
- the **mob lights** (blaze 13, magma cube 10, glow squid 6; added in 1.3.194 on 09-30);
- the **golden-crown light** (level 14, two blocks above the wearer; in BP-02 since August).

That check never matched. Both systems reported the light as removed and left it in place, so **every light they placed stayed in the world**. Once its record was dropped, nothing could find it again.

## Proof on the server
Three server runs on one saved world, restarting between each run:
1. **Run A** (a test-only copy of BP-02) placed a level-13 light in air and a level-6 light in a water source, and listed both in the mob-light record. That is the state the game leaves behind if it closes while a blaze is near you.
2. **Run B** used **your exact 1.3.212**. It dropped both records, but **both light blocks stayed** — 130 ticks later in run B, and again after a further restart in run C.
3. The same test on **1.3.214**: by the first read, 70 ticks after start, both lights were gone. The air cell was air again, and the water cell was a plain source again.

The mob-light unit test had passed the bug because it was written with the old id. It now uses the ids the server reports: 1.3.212 fails 6 of its 14 checks (the bug reproduced), and 1.3.214 passes 14/14.

## Not proven here — your eyes
- **Golden crown.** It needs a player wearing it, and the test server has none. The fix is the same one-line check that is proven above. To check it: wear the crown at night, walk 20 blocks, and look back. No light should stay behind you.
- **Mob lights in play.** In a dark place, let a blaze or magma cube move around near you, then look at the cells it left. They should be dark.
- **Lights already in your world** (placed while 1.3.194 – 1.3.212 were installed) stay: no record of them exists anymore. **Question 7:** should I add a command that clears light blocks of our four levels (6, 10, 13 and 14) within a radius around you, run only when you ask? It would also remove light blocks of those levels that you placed yourself.

## Also proven during this check (no changes needed)
- **Hearth ledger survives restarts.** Lit, fueled and removed hearths all came back correctly. A lit hearth turned to embers 30 ticks after its stored end time, and the embers lasted twice the burn time, as ruled. A hearth placed by command registers without a player.
- **Weather cache survives restarts.**
- **`/time set day` moves the world clock forward** to the next day and never backwards, so hearth, sapling and village timers cannot run backwards.
- **Sapling growth** ("6 pending sapling(s) restored") and the **CIVITAS clock and snapshot** were already proven earlier in the window.
- **Furniture has no saved ledger.** Seats are temporary and table joins are stored in the blocks themselves. My earlier "furniture ledger" item was a mistake.

## Sweep for the same kind of bug
`tools/flatten_sweep.py` checked every `minecraft:` id in our scripts against the server's own block, item and entity lists. Results are in `_docs/recheck/W2-FLATTEN-SWEEP.json`.
- **The light-block bug** is the only one that damages your world.
- **Cosmetic:** flowering azalea leaves use the id `azalea_leaves_flowered`, which the tree-felling code does not recognize as leaves. After you fell an azalea tree they float until they decay.
- **Minor list gaps:** some blocks are missing from the lists the slab smoothing, ground and felling code use to recognize plants or ground.
- **Third-party:** the Naturalist add-on's own scripts use about 15 older ids. Those are their code, as shipped.

All of these are in the backlog and none were changed.

## Gates (all passed)
- Two-run light test A2 → B2 on 1.3.214.
- Unit tests: mob light v2 14/14 (v1 14/14), TestRunner 348/348, homestead fog 11/11.
- Sapling restart test on 1.3.214: "6 pending sapling(s) restored".
- Load checks:
  - 1.3.214 + 0.5.20: 0 ERROR.
  - Full play stack (BP-01 1.3.35 + BP-02 1.3.214 + BP-03 1.3.34 + Markers 0.2.1 + TestRunner 0.5.20): 0 ERROR, every banner present.
- The archive was compared against the build folder, and no test code is in it.

## Files (gofile folder DoHcDxGx)
| File | Bytes | md5 |
|---|---|---|
| BP-02-AbsolutRealism-Tectonic-BP-v1_3_214.mcpack | 5,539,702 | a368dcd6b02169499395e5b0ff27358f |
| PW-TestRunner-BP-v0_5_20.mcpack | 313,451 | 2461c3cc8bcd2973e881393e59fb9b5a |

Next numbers: BP-02 1.3.215 (if you take question 6, the snow fix goes on top of 1.3.214) · TestRunner 0.5.21.
