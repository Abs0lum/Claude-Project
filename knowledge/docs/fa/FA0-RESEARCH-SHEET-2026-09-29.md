# FA-0 RESEARCH SHEET — FLIGHT + AQUATIC (2026-09-29, D-C293) — research only, nothing built

**Sources pulled:**
- **Patrix 26.2 256x mobs zip:** all 178 JEMs, plus the flight and water textures with `_n` / `_s` maps. `_intake/patrix262`, CRC-checked per member.
- **Patrix 1.21.11 128x mobs zip:** 125,709,166 B, md5 68cf3841…. This is the texture base our shipped mobs use; 234 flight / water textures extracted to `_intake/patrix12111_128`.
- **Mojang bedrock-samples 1.26.50:** entity, geometry, animation and render-controller files, plus entity textures (added to the sparse checkout on 09-29).

**Previews:** `_docs/fa/FA0-PREVIEW-{fly1,fly2,water1,water2}.png`, made with `tools/fa_preview.py`.
- Each is the Patrix model as Converter B bakes it, at its rest pose, with the texture our packs use.
- **Ghast "missing tentacles" — solved.** The bake hangs the 7 tentacles from y +1.3 down to −11.3 px, below the model's origin. My preview's floor sat at y 0 and hid them. With the floor under the model they all show (fly2 sheet, redrawn 20:2x).
- **FA-2 must give the ghast and happy ghast a vertical model offset.** Vanilla's tentacle tips end near −1 px; the Patrix bake ends near −11 px, so they need about +10 px, checked against vanilla's hitbox.

## 1 · Every JEM, what drives it

| Mob | Patrix parts | JEM animation lines | Motion source |
|---|---|---|---|
| parrot | 7 parts, 23 bones: two wing sets (folded `*_wing2` / flying `*_wing_fly*`), dance legs, feathers, beak | 102 | JEM (fully procedural: perch, fly, dance, shoulder) |
| bat | head, body, 2 wings + 2 wing tips (+ ear boxes) | 0 | Java code → bind vanilla `bat_v2` resting / flying |
| allay | head, body, arms, 2 three-part wings | 52 | JEM |
| vex | head, body, arms, 2 three-part wings | 51 | JEM |
| phantom | body, head, 2 wings + tips, 2-part tail | 44 | JEM |
| ghast / happy ghast | body + 7 tentacles (+ harness, ropes) | 77 / 86 (+ 40 / 43) | JEM |
| blaze | head + 12 rods | 63 | JEM |
| breeze | head, rods, body (+ wind top / middle / bottom) | 0 | vanilla breeze animations |
| wither | 3 bodies, 3 heads | 0 | vanilla wither animations |
| squid / glow squid | body + 8 tentacles | 0 | port Java SquidModel (tentacle angle) — today a no-op shim |
| cod · salmon · pufferfish ×3 · tropical A/B | fish parts | 28–37 each | JEM |
| turtle · axolotl · frog · tadpole | — | 76 · 102 · 105 · 28 | JEM |
| guardian / elder | body, eye, 3-part tail, 12 spines | 16 | ours (shipped) |
| dolphin | 7 parts | 35 | JEM (fins shipped) |
| nautilus / zombie nautilus (+ armor, saddle, coral) | shell, body, 3 mouth parts | 0 | vanilla nautilus animations |

## 2 · JEM render parameters these mobs use that the port does not map yet

`jem_anim_port.PARAMS` today covers: limb_swing, limb_speed, age, head_yaw, head_pitch, is_alive, is_hurt, hurt_time, swing_progress, is_on_ground, is_in_water, random(id).

| JEM parameter | Used by | Proposed Bedrock mapping | Note |
|---|---|---|---|
| is_riding / is_sitting | parrot, allay, vex, ghast, frog | `q.is_riding` / `q.is_sitting` | |
| is_on_shoulder | parrot | `q.is_riding` (a Bedrock parrot on a shoulder IS riding the player) + `is_riding` → 0 | JEM tests shoulder first |
| is_child | happy ghast, turtle, axolotl, dolphin | `q.is_baby` | |
| is_ridden | happy ghast | `q.has_rider` | |
| time | parrot | `(q.life_time * 20)` (+ the per-entity random) | used only for oscillation phase |
| frame_time | allay, vex, ghast, frog, dolphin | `q.delta_time` | smoothing weights |
| frame_counter | vex, ghast | the `frame_counter == var.frame_counter_prev` guard → 0 | Bedrock runs pre_animation once per frame |
| pos_x / pos_y / pos_z | fish, ghast, allay, vex, tadpole, turtle, frog | `q.position(0/1/2)` | phase offsets |
| rot_y | phantom, ghast, axolotl, tadpole, dolphin | `q.body_y_rotation` → radians | JEM yaw is radians |
| death_time | allay, vex | `q.death_ticks` | |
| is_in_lava / is_burning | ghast / blaze | `q.is_in_lava` / `q.is_on_fire` | |
| player_pos_* | happy ghast (+ harness, ropes) | no client query for the player's position → drop the terms that use it (FA-2 decision) | |

Every new mapping gets the numeric check: Molang against the JEM evaluator at sampled inputs, per channel.

## 3 · Vanilla side (bedrock-samples 1.26.50)

- **parrot:**
  - Vanilla animations: moving, base, dance, sitting, flying, standing, look_at; render controller `controller.render.parrot`.
  - Ours today: vanilla-shaped geometry, every animation a no-op shim.
  - Plan: the JEM port replaces all of them.
  - 5 colour variants (Patrix textures: red_blue, blue, green, yellow_blue, grey).
- **bat:**
  - `geometry.bat_v2`: Head, ears, body, feet, wings + wing tips. Vanilla animations `animation.bat.resting` / `flying`.
  - Patrix bat parts map one-to-one onto them, except feet (none in Patrix, so allowed unbound).
  - A 512² bat texture is already in RP-07, drawn on the vanilla model.
- **allay:** holds items (`enable_attachables`, `rightItem` bone). The Patrix model has no hand point, so one is needed (the HPT lesson from R11).
- **vex:**
  - Holds a sword on `rightItem`. The Patrix model has no item bones, so it needs `rightItem` / `leftItem`.
  - Vanilla draws it with humanoid animations; the JEM port replaces them.
  - Also has a charging texture (`vex_charging.png`).
- **phantom:**
  - `geometry.phantom` with a base-pose controller.
  - Vanilla Bedrock draws the phantom from ONE texture with the `phantom` material (entity file: materials default `phantom`, one texture); the eye glow comes from that material, not from a second layer.
  - Java / Patrix instead ship a separate `phantom_eyes.png` overlay. FA-1 task: carry the Patrix eye glow into Bedrock's one-texture form, the way the material expects it. How the `phantom` material reads the glow (alpha channel or other) gets checked in the material definition before building.

## 4 · Owner packs (ownership law)

- **RP-07:** parrot, bat, allay, happy ghast, nautilus, and every passive water mob.
- **RP-06:** vex, phantom, ghast, blaze, breeze, wither, zombie nautilus, guardians.

## 5 · Sizes (L-SIZE-REAL)

**Real animals, on the curve:**

| Mob | Real size | Target | Today | Change |
|---|---|---|---|---|
| parrot | macaw 0.84 m bill to tail | 0.89 block | 0.96 | ×0.92 |
| bat | wingspan 0.28 m | 0.56 block | vanilla 1.17 at rest, wings spread | ×0.47 |

The grey parrot variant is an African grey (0.33 m → 0.57 block). A per-variant scale (`q.variant` in `scripts.scale`) is possible — his call.

**Fantasy** (allay, vex, phantom, ghasts, blaze, breeze, wither): stay at their Java / vanilla size.

## 6 · Proposed FA-1 build (small flyers) — awaiting GO

**RP-07 1.4.26:**
- parrot: Patrix model plus the full JEM motion port (perch, flight with the second wing set, dance, shoulder, sitting); 5 colours; size on the curve.
- bat: Patrix model with vanilla `bat_v2` resting / flying bound to it; size on the curve.
- allay: Patrix model plus the JEM motion port, and a `rightItem` hand point.

**RP-06 1.4.20:**
- vex: Patrix model plus the JEM motion port, `rightItem` / `leftItem` hand points, and the charging texture.
  - phantom: Patrix model plus the JEM motion port, and the Patrix eye glow carried into the one-texture form (§3).

**Gates:**
- the standing gates (MLS · ARS · RCV · FMT · RBW · ATT · PREC);
- HPT (every mob that holds items has a hand point);
- the JEM-vs-Molang numeric check on every ported channel;
- SZL (size lock) from this build on.

**TestRunner 0.4.1, lineup p10.** Each flyer gets a tall roofed pen: perched, then flying (free steps), plus:
- parrot tamed + dancing next to a jukebox the runner places (parrots dance to a playing jukebox; if the runner can't start a disc, he drops one in);
- allay handed an item;
- vex with its sword;
- phantom at dusk with fire resistance.

**Order after FA-1:** FA-2 big flyers (ghast offset, happy ghast `player_pos` decision), then FA-3 water.
