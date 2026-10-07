# FA-1 BUILD SPEC — 2026-09-29 (D-C294 / D-C296)

Scope, from his rulings of 20:57 and 21:2x:
- the FA-1 flyers;
- the warden;
- the other mobs whose Patrix texture sits on Mojang's model (L-UV-LAYOUT);
- predator sizes at adult-male figures;
- runner 0.4.1.

Research sources:
- `_docs/fa/FA0-RESEARCH-SHEET-2026-09-29.md`
- `_docs/sizes/UV-LAYOUT-CENSUS.md`
- `_docs/fa/FA1-PREVIEW-new4.png`

## 1 · Correction before building

**The slime is NOT a UV-layout case.**
- Patrix 1.21.11 has no `slime.jem`, so its slime texture is painted for the vanilla Java slime model.
- Bedrock's `geometry.slime` / `geometry.slime.armor` use the same box UVs as Java: inner (0,16), eyes (32,0) and (32,4), mouth (32,8), outer (0,0).
- The census "holes" were Patrix's design: floating eyeball sprites inside the jelly.
- My sheet drew only the inner geometry, without the outer jelly cube.
- **The slime is dropped from FA-1**; it is already faithful to Patrix 1.21.11.

## 2 · Per-mob plan

- **Texture:** every texture is the Patrix 1.21.11 128x file, the same one the pack ships unless stated.
- **Geometry:** every geometry is a Converter B bake with the `pw_` unshadowable identifier.

### RP-06 1.4.20 (hostile)

| Mob | JEM | Motion | Layers / extras | Notes |
|---|---|---|---|---|
| **warden** | 10 parts, 0 lines | vanilla warden animations (emerge, dig, sniff, roar, sonic boom, attack, tendrils); `torso` → `body` | 5 render layers (base, bioluminescent, spots 1/2, heart, tendrils) on ONE geometry; the 5 Patrix layer JEMs are byte-identical | client scale 1.2 kept; hitbox untouched |
| **blaze** | head + 12 sticks, 63 lines | JEM port; the JEM reads the vanilla stick positions → recreate Java `BlazeModel.setupAnim` stick math as Molang (3 rings, radii 9 / 7 / 5, orbit and bob per stick) | — | the head is the Patrix flame mask on a 45° head block |
| **breeze** | head, rods, body, 0 lines; wind = separate `breeze_wind.jem` (3 parts) | vanilla breeze animations | 3 wind geometries (top / mid / bottom) keep vanilla's scrolling render controllers; the eyes layer on the head geometry | texture: Patrix 1.21.11 breeze (256² source) |
| **creaking** | 6 parts, 0 lines | vanilla creaking animations; `body` → `upperBody`, `left_arm` → `leftArm`, … | eyes layer (emissive) | — |
| **endermite** | 4 parts (jointed body), 52 lines | JEM port; the vanilla `section_*` animation is dropped | — | like the silverfish (1.4.15) |
| **vex** | 6 parts, 51 lines | JEM port; the humanoid animations are dropped | `rightItem` / `leftItem` hand points (HPT); charging texture | JEM `frame_counter` guard → 0 |
| **phantom** | 8 parts, 44 lines | JEM port | Patrix eye glow merged into the one texture: eye texels alpha 18 (vanilla's emissive marker on `phantom.tga`), cut-out texels alpha 0, the `phantom` material | `rot_y` → `q.body_y_rotation` |

### RP-07 1.4.26 (passive / neutral)

| Mob | JEM | Motion | Extras | Size |
|---|---|---|---|---|
| **parrot** | 7 parts, 23 bones (two wing sets), 102 lines | JEM port: perch, flight, dance, shoulder, sitting | 5 colours | PER COLOUR: 4 macaws 0.84 m → 0.89 block; grey (African grey) 0.33 m → 0.57 block, via `q.variant` in `scripts.scale` |
| **bat** | 6 parts, 0 lines | vanilla `bat_v2` resting / flying bound (`head` → `Head`, `left_wing` → `leftWing`, `outer_left_wing` → `leftWingTip` …); `feet` unbound (Patrix has none) | — | real size 0.28 m wingspan → 0.56 block |
| **allay** | 6 parts, 52 lines | JEM port | `rightItem` hand point + the vanilla hold / dance switches | fantasy — Java size |
| **sniffer** | 13 parts, 95 lines | vanilla sniffer animations (sniff, dig, search, stand up, happy); the JEM is an ADDITIVE layer over Java's keyframes (reads `body.rx`, `head.*`, `ears.*`) → baked at the neutral pose (JEM animation stripped), additive port deferred | baby: vanilla | — |

## 3 · New JEM parameters

These are added to `jem_anim_port.PARAMS`, each numerically checked.

| JEM parameter | Bedrock mapping |
|---|---|
| `is_riding` | `q.is_riding` |
| `is_sitting` | `q.is_sitting` |
| `is_on_shoulder` | `q.is_riding` (a shoulder parrot rides the player) — the parrot JEM tests shoulder first |
| `time` | `(q.life_time * 20)` |
| `frame_time` | `q.delta_time` |
| `frame_counter` guard | the guarded branch never skips (Bedrock runs `pre_animation` once per frame) |
| `pos_y` | `q.position(1)` |
| `rot_y` | `(q.body_y_rotation * 0.0174533)` (radians) |
| `death_time` | `q.death_ticks` |
| `is_burning` | `q.is_on_fire` |

## 4 · Gates

- **Standing gates:** MLS, ARS, RCV, FMT, RBW, ATT, PREC.
- **Conversion-round gates:** A (changed set), J (strict JSON), K (manifest), B (cubes = bake), L (textures), C (placement), D (joints), E (binds), F (part_visibility), G (frames), H / I (look).
- **HPT:** every item-holding mob has its hand point.
- **JEM numeric:** Molang = JEM on every ported channel.
- **SZL:** the size lock.
- **ULC (new, from `uv_layout_census.py`):** no vanilla-geometry × our-texture pairing left in MISMATCH except accepted rows. The accepted false positives are copper golem eyes, ender crystal and slime.

## 5 · Sizes: predators at adult-male figures (his 21:2x ruling)

- Each figure is sourced, in the same measuring basis as the table.
- **Wolf** stays his R8 calibration.
- **Sharks** stay imposing.
- **Female-larger species** (raptors, sharks, anglerfish) keep the range midpoint, flagged to him — "adult male" would shrink them, against "predators large".

Ships as BP-02 1.3.192 (polar bear 2.6 m → 2.74 blocks) + PW-StripMine BP 1.3.5.

## 6 · Runner 0.4.1, lineup p10

- **Flyers:**
  - pens: tall, roofed;
  - each flyer is shown perched, then flying free.
- **Parrot:** perch, flight, sitting, dance, then shoulder:
  - the runner places a jukebox;
  - the step text carries the disc commands;
  - one colour per variant row.
- **Allay:** handed an item.
- **Vex:** with a sword.
- **Phantom:** at dusk, with fire resistance.
- **Other mobs:** warden, blaze, breeze, creaking, endermite, sniffer.
- **Size rows:** polar bear + wolf reference, bat, parrot colours.
- **Fixes:**
  - a baby that cannot grow up is re-spawned (the skeleton horse has no grow-up event);
  - leftover water / ice in the old rig footprint + margin is removed and logged (R12 flooded pens).

## 7 · Investigation candidate (not in FA-1)

**L-ENT-MERS?** Our RP-06 / RP-07 ship zero entity `texture_set.json`; vanilla ships 750. If a vanilla set (colour + vanilla-layout MERS) pairs with our Patrix colour under Vibrant Visuals, the emissive / metal / roughness would land in the wrong places. Needs a witness probe before any fix.

The fix path is the backlog's "mob MERS from Patrix `_s` via #156".
