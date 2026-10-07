# HANDOFF ADDENDUM — 2026-10-03 — TREES T2b/T2c: BP-02 1.3.208 + RP-01 1.3.118

Supplement to `HANDOFF-2026-10-03-V6-CIVITAS.md` / `-DELIVERED.md`. Journal D-C502 (+ P-4 and the sounds). Install over V6: BP-02 1.3.208 replaces 1.3.207; RP-01 1.3.118 replaces 1.3.117. Everything else of V6 stays.

## What changed (and why — every item server-proven, witness pending: P1)
1. **Roots for the square species.** acacia / cherry / mangrove trunks are vanilla logs, so they had no root block to carry the template index + rotation. New `pw:acacia_root`, `pw:cherry_root`, `pw:mangrove_root` (a full cube on the vanilla log's own textures; same loot / hardness) at the base of all 96 templates; the felling rules know them (mock 14/14; BDS: 36/36 placements at 4 rotations read back right).
2. **No more floating trees.** The tree rules placed templates at a random height with an allowlist that permits air: a census found roots standing on air and on water (this is in V6 / 1.3.207 too). Now every template feature is `grounded` + `unburied` and every tree rule places at the ground.
3. **Forests are ours.** Vanilla's overworld trees come from "legacy" feature rules (engine code behind a JSON rule). The 17 of them are now overridden by identifier so taiga, mega taiga, forests, birch forests, flower forest, windswept forest, plains, savanna, snowy tundra, jungles and wooded badlands grow OUR templates, at Java-like densities (my ASSUMPTION — say what looks wrong: too dense / too sparse / wrong mix). Six mixes: forest oak 4 : birch 1 · flower forest 1 : 1 · windswept spruce 1 : oak 1 · mega taiga elder 1 : old 2 : mature 2 · savanna acacia 4 : oak 1 · jungle 10 : giant 1 (+ bushes).
4. **Root sounds.** None of the 20 root blocks had a sound: wood (cherry wood for cherry) now.
5. **P-4 save migration proven safe**: removing a block state keeps saved blocks and their remaining states (40/40). Not in this build; it clears the way for the leaf-state simplification.

## Known and open
- **Grove (and likely snowy slopes, cherry grove, mangrove swamp, pale garden, meadow) keep vanilla trees**: their trees are engine-internal; no rule, feature or biome JSON reaches them (three probes). Your ruling: accept there / a scripted sweep near the player / make our biomes dominate. Assumed: accept, census the others next.
- Densities above are first numbers.
- GS-1 (two street cells in the forest village, V6) unchanged.

## What to look at (no lineup needed — walk a fresh area with 1.3.208)
A taiga or forest you have not loaded before: trees everywhere ours (dodecagon trunks, our leaves), none floating, roots at the base (break one: it drops the log and the tree falls as before); an acacia / cherry / mangrove: chop the bottom log — it falls whole. A grove (snowy mountain): vanilla spruces, by design for now.
