# LESSON CANDIDATES — review window 2026-10-03 (for your approval before they enter FOUNDATION)

Each line is a candidate. It becomes a lesson only with your yes (Lesson Supersession protocol, MANUAL §15). The evidence for each is in the journal entry named.

## Engine and API facts (proven on the server, BDS 1.26.52)
1. **Bedrock flattens block ids** (D-C515). `resolve("minecraft:light_block", {block_light_level: N})` places `minecraft:light_block_N`. The same applies to deadbush, waterlily, grass_path, dirt_with_roots, azalea_leaves_flowered and the terracotta colours. A script must compare ids read from the running engine; a stale string comparison fails silently.
2. **World dynamic properties persist across a restart and are keyed per pack UUID** (D-C511). Never change BP-02's header uuid, or its saved state is orphaned.
3. **`/time set day` moves the absolute clock forward** to the next day and never backwards (D-C515). Timers that use the absolute clock cannot run backwards.
4. **A feature is registered only when a feature rule reaches it** (D-C517). Features that no rule references are invisible to `Dimension.placeFeature`. To test them, use an aggregate feature plus a rule that never fires.
5. **`grounded` (structure template)** requires a solid block under the template's non-void bottom blocks (D-C517 / D-C520).
   - Snow blocks and leaves count as solid.
   - Thin snow layers, grass tufts and ferns do not.
   - So a tree can stand in another tree's crown, and is refused on a grass tuft.
6. **`Dimension.getTopmostBlock` skips snow layers** (D-C518). A surface census must count snow layers explicitly.
7. **Block custom component `onPlace` fires for `/setblock`** with no player present (D-C515). Structure loads fire no place event.

## Method
8. **"Not server-proven" means unknown** (D-C511). Every persistence claim gets its two-run restart probe; every placement change gets the under-root check.
9. **A cleared count is not proof of clearing** (D-C515). Read the cell afterwards.
10. **A mock that models the engine from memory encodes the bug** (D-C515). The mob-light mock passed with the old id.
11. **An unmeasured census axis is a confound waiting** (D-C518). The "snow" zero was really the biome, and the "bare" chunks hid snow layers. Classify by biome before blaming a block.
12. **The pad matrix first** (D-C517). `Dimension.placeFeature` on built pads, with each constraint tested alone, answers a placement question in one run. Do this before any census round.
13. **A long job must re-read the world before it writes** (D-C508, roads).
14. **"Ground" must exclude what we lay ourselves, and a placed surface needs support** (D-C509: gravel falls; a path over a hollow).
15. **A safety wrapper must keep the original call's failure modes** (D-C507, the `_bds` incident).
16. **Never install under a running server** (D-C510).
17. **Clock first:** every stamp comes from the clock at write time, using `tools/plog.sh` and `tools/board_stamp.py`. This window corrected six typed stamps.

## Superseded or corrected claims
- **Trees round 1 claimed "no floating trees".** Corrected: the check looked only for air or water directly under a root. About 1 % of trees stand on leaves (question 8).
- **D-C513 said "snow blocks our trees".** Corrected: the cause is biome coverage plus plants and thin snow layers on the chosen spot (D-C518, D-C519).
