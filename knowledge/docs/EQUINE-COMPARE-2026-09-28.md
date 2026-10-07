# EQUINE FAMILY — Patrix target vs ours in game (2026-09-28, D-C268)

**Trigger:** Abs0lum 18:36 — horse, mule/donkey (+ "another similar mob"): "all of the parts, oriented incorrectly, mispositioned, not connected in a way that looks natural". Llamas/camels: assembled correctly, other issues (to be listed by him).

**Status:** GO 19:20 → BUILT and SHIPPED as RP-07 1.4.15 (horse, donkey, mule) + RP-06 1.4.10 (zombie horse, skeleton horse), gate 37/37, awaiting his in-game witness (lineup 0P4). Correction: the donkey/mule chest fix was already in RP-07 1.4.12. After-sheet: `_docs/equine/equine_after.png`.

## Reference — what it should look like
- Patrix 32x (Modrinth / CurseForge): the mobs use "custom mob animation from FreshLX" (EMF + ETF + Fresh Animations). A Patrix showcase thumbnail (YouTube GaPoVjtQIE4) shows the horse's head angled down and forward, continuing the line of the neck, with two ears on top.
- Ground truth: the Patrix JEM plus FreshLX's CEM animations at rest, evaluated by `tools/cem_eval.py` with the **vanilla per-frame seeds** (neck ty 4, tz -12, rx 30°; body rx 0). Without the seeds the JEM reads `neck.ty = 0`, decides the horse is rearing (`var.rearing = 0.5`) and bakes a half-rear.
- Patrix rest rig (all five equines): body → neck2 (pivot 0, 18.7, -6.7; leaning 31.5° forward) → neck box, head2 (≈0° relative, so the head **rides the neck**, nose 29° down) → muzzle / ears (+8° back; donkey and mule ears splayed ±15°) / forelock; mane on the neck's back; tail 13°.

## Ours (RP-07 1.4.14 / RP-06 1.4.9) — the three mechanisms
The in-game prediction (`tools/equine_compare.py`) reproduces his shots 124030 (horse), 124101 (donkey), 124118 (mule).

1. **Position:** the neck/head group sits 7–13 px forward of Patrix (horse skull +11.9 px, muzzle +12.3, ears +13.1; mule skull 7 px low as well). The ears are 1 px apart centre-to-centre, so they overlap into one block (Patrix: 3 px, with a 1 px gap; donkey/mule splayed ±15°). The mane is 1.2 px deep and half-buried in the neck, so it reads as no mane. The neck is 14 texture rows tall (Patrix 12).
2. **Orientation:** `head` runs a look-at with `relative_to: {rotation: entity}` (vanilla `animation.common.look_at_target`; the horse's own `animation.horse.pw.headtrack` also on `head2`), and it sits under a neck rotated 30°. The engine resets the head's world orientation to level and throws away the neck's lean; the extra −10° on head2/snout then tips the donkey's nose up by 10–20°. The Patrix nose points 29° down. Pitch error: +29° (horse, zombie horse), +39° (donkey, mule).
3. **Structure:** the skeleton horse has no neck (the two Patrix vertebra cubes are missing), so the head floats level at chest height.

Census: bones with a relative-to-entity look under a rotated ancestor are exactly horse, donkey, mule and zombie horse, plus dolphin and frog. Llama, trader llama and camel have none, which fits his "assembled correctly".

## Proposed fix (awaiting GO)
- **Converter B, equine family:** build each geometry from its Patrix JEM (CONV-1 + seeded rest bake). The posture is baked in (neck lean, head on the neck, ears, splay, tail); the legs keep the static stance. Our bone names stay, so the existing animations and render controllers still bind. Per-face UVs come from the JEM.
- **Look-at:** a parent-relative look on the neck and head (FreshLX split: neck ry = clamp(yaw/2, ±20°), neck rx += pitch/1.5, head ry = clamp(yaw/6, ±15°)). It replaces the relative-to-entity look on the five entities; the shared vanilla animation is not edited.
- **Versions:** RP-07 1.4.15 (horse, donkey, mule) and RP-06 1.4.10 (zombie horse, skeleton horse). The ownership wave moves to RP-07 1.4.16 / RP-06 1.4.11.
- **Gate:** every cube within 0.01 px of the Patrix rest bake; UVs equal to the JEM; every animation/render-controller bone resolves; no relative-to-entity bone under a rotated ancestor; a render sheet. Then his in-game witness.

## Retro-sweep hits (backlog)
- Dolphin and frog have the same rotated-ancestor look-at.
- 62 Patrix JEMs read vanilla-only part values, so every rest bake must be seeded. Re-check the earlier bakes for the ty-readers: sheep, sniffer, blaze, magma cube.
- Add a verify gate: no relative-to-entity bone under a rotated ancestor.
- Re-read the p0 rows scored "married" on corner contact only.

Tools: `tools/equine_compare.py`, `tools/equine_sheet.py`; `cem_eval.rest_pose` and `jem_convert.bake_rest2` gained `seeds=`.
Sheet: `_docs/equine/equine_family_compare.png`; numbers: `_docs/equine/numbers.txt`.
