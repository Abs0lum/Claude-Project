---
name: engine-laws
description: Witnessed Bedrock engine laws and technical lessons for the pw:/am: pack suite — read before authoring blocks, geometry, or textures
sources: [backfill]
aliases: [standing laws, witnessed laws]
---
## Standing engine laws (witnessed)

- [stated] Selection-box y≥0 engine law
- [stated] Permutation-material law: permutations replace material instances wholesale
- [stated] Block geometry ≤30px cap
- [stated] alpha_masked_tint rejected at 1.21.80
- [stated] TDZ law for top-level loops
- [stated] L-TEX-KEYMETA: metadata keys bind at key level, not path level
- [stated] L-DEDUP-1: suite-wide corpus scan required before any asset deletion (cross-pack references are invisible to single-pack scans)
- [stated] L-DEDUP-4: registry entry members, flipbook sources, and texture_set layers must all resolve pack-locally
- [stated] L-PKG-1: mcaddon = zip of mcpack files, not zip of extracted folders
- [stated] L-ICON-1: vanilla legacy file naming traps — Java-named overrides fail for item arrays and block terrain textures
- [stated] L-ROT-1: +θ is the engine X-rotation convention for block cubes; offline rasterizers validate hypotheses only
- [stated] L-SCHEMA-1: consult Microsoft Learn before declaring JSON structures malformed
- [stated] L-VV-1: Bedrock VV uses `*_vv.png`; always update both standard and `_vv` variants
- [stated] `q.property` arithmetic fails in animation position channels (returns 0); use constants and part_visibility molang instead
- [stated] 4-value MERS inline arrays are valid; 3-value is forbidden
- [stated] Matched-Set Law: all pw resource packs activate together, with no engine enforcement
- [stated] `minecraft:geometry` component is mandatory for all custom blocks since format version 1.21.80
- [stated] Blockbench Sign Law (codec-extracted): Bedrock X mirrors to Blockbench, X/Y rotations negate, Z passes, pivot X-only flip
- [stated] `replace_biomes` tie-break is deterministic/order-independent — contradicts Lesson #135 "last-loaded wins"; needs verification
- [stated] Entity trunk material is the legacy opaque "entity" material — prime candidate for bark rendering lighter under VV despite pixel parity
- [stated] Custom-block material_instances take one texture per key — variation arrays are flattened to "un-weighted" and only the first is used (vanilla block keys do accept variations); per-face variance on custom blocks is done with permutation-bound single keys (lattice-offset gvar keys)
- [stated] A block-state enum array may hold at most 16 values; larger ranges are split across two states (e.g. idx 0–15 × ring 0–3)
- [stated] World::getDynamicProperty cannot be used in early execution — defer ledger loads with system.run one tick after boot
- [stated] Laptop (Bedrock Launcher) worlds copy active packs into the world folder at creation (behavior_packs/<Pack>(1)); a global pack update does not reach an existing world until the pack is removed and re-activated in that world's settings — or the world is recreated

## Process laws

- [stated] Witness Rule is supreme: in-game hardware confirmation is truth; Claude investigates causes rather than defending code
- [stated] Source-Trust Law: genesis-era and non-canonical documents are hypothesis sources only
- [stated] Evidence-Exhaustion Gate (P10): per-item UNVIEWED/VIEWED ledger must be quoted before any synthesis
- [stated] Cartesian Premise Audit (P11): excluded search spaces must be marked CENSUSED or EXCLUSION-VERIFIED before any absence conclusion
- [stated] Perspective-Check (P9 rule 6): camera facing declared before any orientation read
- [stated] DEP-MANIFEST LAW: dependency manifest injection tracked via depscan.py
- [stated] D-101: completion log lines go inside gated Python only — structurally unreachable on gate failure
- [stated] Suite-gated packaging: zips built only after the verification suite passes in the same script
- [stated] Description-stamp law: every manifest description carries a unique version/date/headline
- [stated] Integrity marker: custom instructions end with a specific marker line; absence signals truncation
- [stated] X-mirror law for block geometry: model +x renders world west (north/−z is honest); Orientation Law for directional blocks: facing = direction of ascent (tall half / high end on the facing side; vanilla weirdo_direction 0 east, 1 west, 2 south, 3 north), applied after the mirror — witness the first placement before deriving siblings
- [stated] Custom blocks get a single collision box (y≥0) and player movement steps by half-blocks (0.5 auto-steps, 1.0 needs a jump); a 1.0 rise inside one cell always jumps — sloped visuals use stepped collision under the auto-step threshold
- [stated] Road rule for sloped boards (differs from the roof eave): the board TOP is the diagonal, flush with both courses; the underside buries into the solid course below where nothing renders; stepped courses and side fill bands kiss the underside line
- [stated] Atlas Budget Law: the terrain atlas is capped at one 8192² sheet (67 Mpx); when the referenced block textures exceed it the engine silently halves every texture under memory pressure (frame-wide 16px look that comes and goes) — block textures are capped at 256px suite-wide and the referenced total is kept under ~60 Mpx (next lever: 16-variant terrain families to 192px)
- [stated] Block geometry must touch its own unit cube on every axis (a cap dropped wholly below the cell is refused) — use an invisible in-cell anchor cube; vanilla weather only ever forms one 2px snow layer, so custom snow caps track the deepest neighbouring vanilla layer rather than piling independently; snow on vanilla partial blocks (stairs, bottom slabs) is done with collision-free overlay cap blocks in the cell above, never by replacing the vanilla block (which would lose its two-box physics)
- [stated] Thin alpha-quad "gable fill" side pieces on slopes failed four orientation witnesses in a row; sloped road pieces are built from full-width axis-aligned tooth columns (1px rise per 2px or 4px run) with sliced UVs — solid sides by construction, no engine axis convention to get wrong
- [stated] Structure Load Distance Law: /structure load targets beyond the phone's loaded area (~64 blocks) answer "placement request has been queued" and never place — loads are always issued within a few blocks of the player (commands and the assembler alike); the structure block's preview thumbnail misrepresents non-square pieces and is not a witness; rotation arguments (0/90) rotate the whole box correctly, so one file per piece suffices
- [stated] Crop-cut law for slope blocks: seam and corner defects on sloped blocks (ridge corner edges, cap-block underside corners as seen from E/W/N/S, gables) are corrected by cropping the face textures — rectangle to trapezoid along one straight line — with the block geometry left exactly as it is; this procedure applies to every slope block already in the suite and to any created in the future
- [stated] Save-box law for building structures (ruling 2026-09-20): the saved box is the building's exact prism plus one column of clearance on the RIGHT side as judged from the street facing the building; Y always runs from the fixed subsurface-infrastructure depth to street level consistently, then is extended to fit the building's height (street-kit pieces stay exact prisms)
- [stated] Box-contains-filled-areas law (ruling 2026-09-21, companion to the crop-cut law): geometry may run any invisible (alpha-0) length past the block boundary as long as its invisible pieces carry no collision; the collision AND selection box should contain exactly the filled (visible) areas — the bounding box of the visible solid, clamped to the cell — applied to the whole roof family (straight 45/63 and hip → full cell; ridge/ridge-end/cap → their visible height), gussets/ramps/angled walls pending
- [stated] (witness 2026-09-30) Custom leaf blocks with render_method alpha_test DO cast shadows under Vibrant Visuals ("They throw shadows. Alpha_test works for shadows.")
- [stated] Stair headroom (ruling 2026-10-06): a climb needs AT LEAST two blocks of clearance at every point of the ascent; vanilla stairs need three because their half-block first step momentarily leaves 1.5. Every stair, spiral included, exits FORWARD (along its last step) onto a floor in front, which may continue as a lengthwise hallway — never off the side; a stair that falls short of the floor gets a stair piece at the floor's first edge
- [stated] Spiral stair sizes (ruling 2026-10-06): narrow turret (A) for tight defensive towers, standard (B) for ordinary spiral stairs, grand (C) for palaces, castles and manors; materials chosen by local abundance and the class/station of the building (left to Claude)
