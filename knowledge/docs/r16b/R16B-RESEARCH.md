# R16b — PATRIX FIDELITY PORTS · research sheet (2026-09-30, D-C314)

Scope (his "Go on all", item 2, D-C309): fox, goat, cat, ocelot, cod, iron golem, hoglin, zoglin onto their Patrix 26.2
JEMs **with FreshLX's whole animation** (FA-1 method: Converter B bake + `jem_anim_port.port` + Java seeds + numeric gate N2
+ posed previews). Texture fit already proven (1d: fox 0.98 · cat/ocelot 0.97 · cod 0.88 · hoglin 0.96 · zoglin 0.94 ·
goat 0.86 · iron golem 1.00 vs the shipped geometry's 0.76) → **no texture changes**; render controllers, textures, size
scripts (`scale`) and BP sizes stay as shipped.

## Owner packs and what is shipped now

| mob | pack | shipped geometry | shipped motion |
|---|---|---|---|
| fox | RP-07 1.4.28 | geometry.pw_fox (Patrix, wired R10, + pw_* articulation bones) | ar_walk / ar_idle / pw_ambient / fox headtrack (grafted) |
| goat | RP-07 | geometry.pw_goat (same kind) | ar_walk / ar_idle / ar_ram / pw_ambient |
| cat, ocelot | RP-07 | geometry.pw_cat (shared) | ar_walk / ar_idle / pw_ambient (+ tail flick on the cat) |
| cod | RP-07 | geometry.cod.patrix | fish flop + ar_swim / ar_flop / pw_ambient |
| iron golem | RP-07 | geometry.iron_golem = an OLD custom model (root / golem_anchor / limb_arm_l …, NOT Patrix) | Mojang's golem animations |
| hoglin, zoglin | RP-06 1.4.22 | geometry.hoglin.patrix / zoglin.patrix | quadruped walk + look_at |

## Per mob: what the JEM reads from Java (seeds) and how Bedrock supplies it

Read-before-write census (a JEM expression that reads a vanilla part channel before any JEM line assigns it sees the value
Java's own model wrote THIS frame — OptiFine semantics, D-C299):

| mob | channels read from Java | Java source of the value | Bedrock seed |
|---|---|---|---|
| fox | body.rx / ry / rz (+ the body's pivot moves) | FoxModel.setupAnim: rest body (0,16,-6) rx 90°; crouch rx +6°, y + crouchAmount (0→3, +0.2/tick); sleep rz −90°, y +5; sit rx 30°, y −7, z +3; crouch ry = cos(age)·0.01; **sleep hides the 4 legs** | q.is_stalking / q.is_sleeping / q.is_sitting (Mojang's own fox controller uses exactly these) → body rx/ry/rz/tx/ty/tz + leg visibility DRIVEN (extra_driven) |
| hoglin, zoglin | head.rx (attack) | HoglinModel: head.xRot = lerp(h, 50°, −20°), h = 1 − abs(10 − 2·ticksLeft)/10 | v.attack_time (Mojang's hoglin reads it): h = 1 − abs(2·t − 1) while t > 0 |
| cod | tail.ry | CodModel: tail.yRot = −f·0.45·sin(0.6·age), f = 1 in water, 1.5 on land | q.is_in_water, q.life_time |
| cat, ocelot | head rx/ry/rz, the 4 legs rx/ry, tail.rx, tail2.rx — only in the LYING-DOWN branch (var.sleep = head.rz ≠ 0) | FelineModel lie-down: head rz −72.8°, ry +72.8°; legs rx −72.8° / −27° / −22.9° / +28.6°; tail1 0.8, tail2 −0.4 rad | v.state == 4 (Mojang's cat controller: 0 sneak, 1 sprint, 2 sit, 3 walk, 4 lie down) |
| goat | head.rx (ram), left/right_horn.visible | GoatModel: head.xRot = rammingXHeadRot when ≠ 0; horns = hasLeft/RightHorn | v.should_bow_head (Mojang: sin(t·90)·37.3°) · v.goat_has_left/right_horn (Mojang's goat render controller) |
| iron golem | right/left_arm.rx, right/left_leg.rx | IronGolemModel: attack arms −2 + 1.5·tri(ticks, 10); flower right arm −0.8 + 0.025·tri(tick, 70), left 0; walk arms (−0.2 ± 1.5·tri(limbSwing, 13))·speed; legs ∓1.5·tri(limbSwing, 13)·speed | v.attack_animation_tick / v.offer_flower_tick (Mojang's golem reads them) + limb swing; the ARMS' x-rotation is Java's (the JEM never writes it) → DRIVEN |

## Render parameters → Bedrock

| JEM | Bedrock | note |
|---|---|---|
| is_child | **0.0** | babies stay the adult pose scaled by the BP, as shipped now (the JEM's own child maths would shrink them twice) |
| frame_time / frame_counter / pos_x,y,z | q.delta_time / q.life_time / q.position(0,1,2) | PX_COMMON |
| is_sitting · is_riding · is_tamed · health · max_health | q.is_sitting · q.is_riding · q.is_tamed · q.health · q.max_health | |
| is_sneaking / is_sprinting (cat, ocelot) | (v.state ?? 3) == 0 / == 1 | Mojang's cat state |
| is_aggressive (golem) | q.has_target | |
| rule_index (goat: 2 = standing on grass → nibbles, 3 = on wheat/hay) | **2.0 while on the ground** | no block-below query for entities in a resource pack → the goat may nibble on stone too (ASK him) |
| rot_y (golem) | only copied to an unused variable | 0.0 |

## Extra per mob
- **fox**: Mojang's fox holds items on a `held_item` bone under the head; the Patrix fox gets one at the snout (the JEM moves the vanilla head part exactly for Java's held-item layer).
- **iron golem**: new id `geometry.pw_iron_golem` (the old custom model stays in the file set untouched until the port is witnessed? NO — replaced in the entity; the old file kept only if another entity reads it).
- the grafted animations (ar_*, pw_ambient) leave these entities; `pw_jem` alone drives them (as parrot / allay / vex in FA-1).

## Risks called out
1. Cat / ocelot rely on Mojang's `variable.state` (engine-set, read by Mojang's own cat controller). If it is not set on his PS5 the cats never sneak / sprint / lie down but still walk, sit and idle.
2. The goat nibble on non-grass (rule_index) — his call.
3. Babies: scaled adults (unchanged behaviour).
