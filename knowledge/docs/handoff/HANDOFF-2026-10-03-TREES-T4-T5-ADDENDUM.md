# HANDOFF ADDENDUM 2 — 2026-10-03 — TREES T4 + T5: BP-02 1.3.209 + PW-TestRunner 0.5.16 (lineup p23)

Supplement to `HANDOFF-2026-10-03-TREES-T2-ADDENDUM.md`. Journal D-C503. Install: BP-02 1.3.209 replaces 1.3.208 (and 207); TestRunner 0.5.16 replaces 0.5.15. RP-01 1.3.118 stays.

## What changed
- **T4 — the exact falling set.** A tree that carries a root (every worldgen and every grown tree) now falls by its TEMPLATE: the clock reads the template (cached), turns its cells about the root by the root's facing, and takes exactly the logs above the cut and the leaves that still hang. A neighbour's wood is never taken; the stump is the template's logs below the cut. The old BFS stays for legacy trees (no root). One switch: `PW_TEMPLATE_FELL`. Mock 26/26 (four facings, neighbour excluded, decayed leaf excluded, higher cut → more stump). **BDS cannot fire a player's break: lineup p23 steps t04/t05/t07 are the proof.**
- **T5 — TREEGROW on the templates.** Saplings grow our templates (young oak/birch/spruce/jungle; acacia/cherry/mangrove; dark/pale oak elders) with the root exactly on the sapling cell (the old code pointed at structures that existed nowhere and put the structure's corner on the sapling); clearance uses the template's own cells; pending saplings survive a reload. BDS: 9/9 species grew on the sapling cell. Test tool: `/scriptevent pw:treegrow plant <x> <y> <z> [sapling id]` (due now) and `/scriptevent pw:treegrow status`.

## Lineup p23 (TestRunner 0.5.16) — `/scriptevent pw:test start p23`
q0 packs + a fresh world or fresh chunks · t01 a fresh forest: every tree ours, none floating, density/mix verdict · t02 a grove: vanilla by design (confirm, note your preference) · t03 break a root (creative): wood sound, drops the log, nothing falls · t04 SURVIVAL chop a worldgen tree with a touching neighbour: the whole tree and only that tree falls, root stays · t05 a branch cut and a stump cut never fell · t06 nine saplings planted around you by the tool: each grows our tree on its cell within a minute · t07 chop a grown one; plant one by hand · q9 upload.

## Open
- Grove and the other engine-internal biomes keep vanilla trees (ruling pending: accept / sweep / weight).
- Densities in forests are first numbers (t01 verdict).
- GS-1 (two street cells, V6) unchanged.
