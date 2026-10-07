# Round 1002n — changes waiting for the complete-set delivery (#170)
Undelivered build dirs carrying them (never rebuilt once delivered):
- BP-02 1.3.206: StripMine BP merged (D-C4xx) · biome fixes 206 + 206b · 557 generated spawn rules (groups fixed, ants on hills,
  7 no-rule creatures, despawn on 160) · tiny-mobs round (186 neutral, 59 Giant twins, 34 size fixes) · 6 pond features.
- RP-07 1.4.44: StripMine RP merged · 59 Giant client entities + lang + sounds · creature normal maps (staged, apply pending N1/N2).
- RP-08 1.4.13: StripMine icons · creature normals (staged).
- RP-02 2.0.7: StripMine VV globals · 115 long ambience sounds "stream": true (PS5 sound-load candidate fix, D-C475).
- RP-11 1.3.40 / RP-04 1.3.156 / RP-03 1.3.67: ore round + roof cut-outs restored (r1002m) · RP-04/RP-03 creature normals (staged).
- New dirs needed at apply time: RP-06 1.4.29 (5 normals; 1.4.28 delivered), RP-01 1.3.117 (leaf-litter sets; 1.3.116 bytes uploaded).
Manifest descriptions to be written from this list at packaging.

## #174 / #175 (19:0x–19:4x CT) — roof pieces + all-block placement census
- RP-04 1.3.156: roof_hip (Z-board sign, x-mirror = NW corner, hair faces), roof_pyramidion (rebuilt: 4 half-scale hips + cap, pointed), gussets (side-triangle uv 64->16), pw_fill_tri*(4) hard alpha, crown_ring -> crown_ring_straight + crown_ring_corner (outer lip, flush corner), rafter45 slope sign, pw_snowcaps 72 uv windows inside the texture.
- BP-02 1.3.206: roof63_upper permutation map = lower's; crown_ring blocks select geometry by pw:ring_form; pw_companion.js v7 (Rule A outer corners + HIP_FACE n->NW; Rule B hipped-end detection both orders; Rule C cap one level up; Rule G corner facings + outward on closure; Rule D front neighbour; Rule E WALL_CORNER_FACE n->N+E + both orders); structures s1 gusset fold, s2 hipped roof 7x5, s4 plain gable, roof_kit 46x5x11.
- Tools: roof_audit, roof_heightfield, roof_seams, roof_fix_174, block_placement_census, placement_fix_175, facings_sheet; civ_render transformation law fixed (D-C487) + bone_visibility.
- Outputs: ROOF-KIT-BEFORE-AFTER.png, ROOF-KIT.png, BLOCK-FACINGS-1..3.png.
- Witness items: load pw:roof_kit (6 assemblies); place hips/ridge/ring by hand for Rules A/B/C/G; room walls for D/E; rafter under a roof45; ramp snow caps at level 3-4.
