# MOB CONVERSION RESEARCH — 2026-09-27 (D-C255)
**Java (OptiFine CEM / Patrix) → Bedrock: what the engine actually does, why our direct conversion failed, what the shipped mobs deviate by, and a verified path to a conversion tool.** Research only — nothing was built into a pack this turn (Abs0lum 15:25/15:31).

**Status of every claim:** `VERIFIED` = reproduces Mojang's own files or a witness; `SOURCE` = read from an authoritative implementation (Blockbench codec, EMF mod source, OptiFine spec); `MODEL` = our reading of the semantics, matched on ≥1 case, still needs a controlled test; `HYPOTHESIS` = untested.

---

## §0 · The one-paragraph answer

The conversion is a *fixed linear mapping* that we can now state and that Mojang's own vanilla files prove (§2): `pivot = (t.x, −t.y, −t.z)`, `cube = (−(x+w), y, z)`, `rotation = (−rx, −ry, +rz)`, per-face UVs unchanged. The April converter got the pivot and the submodel rules wrong — that alone produces the gaps and "connected incorrectly" parts (§4). The shipped RP-07 mobs were then hand-tuned toward what looked right in-game; measured against the Patrix source they are off by 0.3–13 cubes per part depending on the mob (§5) — "possibly flawed" is confirmed. The second, subtler half of the problem is that Patrix's models are Fresh-Animations-style: their **animations set the rest pose every frame** (§3), so a faithful converter must evaluate the animations at rest (and later translate them to Molang) — the static file alone is not what the player sees. A tool that does both, gated by the vanilla-pair test and by per-mob renders for your eyes, is specified in §7. Better-fidelity levers beyond geometry (PBR on mobs, variants, per-part textures, animation parity) are in §6.

---

## §1 · The engine's rotation law (L-ROT-DIR) — VERIFIED

**File frame.** Bedrock geometry x is mirrored relative to the world: file +x is the entity's **left** (vanilla humanoid `leftArm` pivot `[5, 22, 0]`), y up, −z front. Face names (`north/south/east/west/up/down`) are **world** directions, so per-face UVs copy across without swapping.

**Law.** A bone rotation `[rx, ry, rz]` (degrees) about its pivot, evaluated in file coordinates with ordinary right-handed matrices, is

`v′ = Rz(−rz) · Ry(+ry) · Rx(−rx) · (v − pivot) + pivot`  (X applied first; Blockbench Euler order `ZYX`).

Consequences: `+90` about X puts the cube's local +Y at the **front** (−z) and its local +Z **up** (`y′ = py + (z − pz)`, `z′ = pz − (y − py)`); `+90` about Y turns the front toward file −x (`x′ = px + (z − pz)`, `z′ = pz − (x − px)`); `+rz` tips the top toward file +x.

**Evidence (independent lines):**
1. Vanilla `wolf_armor.geo.json`: tail `[55,0,0]` (cube hangs below its pivot) points **backward** only under this law; body `[90,0,0]` / upperBody `[−90,0,0]` land on the legs only under it.
2. The Java→Bedrock cow: Java `ModelQuadruped` body box `(−6,−10,−7, 12,18,10)` at rotation point `(0,5,2)` with `rotateAngleX = +π/2` was written by Mojang as `origin [−6,11,−5] size [12,18,10] pivot [0,19,2] bind_pose_rotation [90,0,0]` — the same number, and the law reproduces the Java body at y 12–22 (a reflection of y changes the sense of X and Z rotations, not Y).
3. Vanilla llama chests `pivot [5.5,21,3] rot [0,90,0] cube [2.5,13,3]` and horse bags `[0,±90,0]` sit **on** the flank under `+ry`; under `−ry` they end up inside the body or 3 cubes away.
4. Our witnessed cow and wolf geometries sit on their legs under the law and sink 4 cubes into / float 4 cubes above them under the opposite.
5. Blockbench's Bedrock codec (`bedrock.js`, 4.12.4) is exactly this law after its internal x-mirror: it stores `rotation = (−rx_BB, −ry_BB, rz_BB)` and `pivot.x = −x_BB`; conjugating `Rz(rz)Ry(−ry)Rx(−rx)` by the x-reflection gives the law above.
6. His 09-27 09:57 trader-llama screenshot: the neck hangs 7 cubes under the body only under this law (D-C253).

**What this supersedes:** the CONVERSION-STANDARD's §3.1 X/Z sentences, §3.2 rule, §4.2 table (all inverted on X), and its §2.1/§2.3 frame description — tagged in the standard itself (never deleted). Also: `tools/geo_preview.py` / `entity_render.py` negated the Y rotation and composed Z first. RP-04 .138 does ship Y-rotated pieces (angled wall, barrel seat, hearth_lit/embers, seated double/plant, roof_gusset_lower, wall_prism) and Z-rotated ones (roof_hip, pyramidion, ridge_end): the game applied the true law and you accepted them, so nothing shipped is wrong — but their *previews* were mirrored (a 45° wall previewed as −45°). `entity_render.py` is fixed today; `geo_preview.py` is a HIGH backlog item (re-render the angled wall and pyramidion for your eyes).

---

## §2 · CONV-1: the JEM → Bedrock geometry mapping — VERIFIED

Sources: OptiFine `cem_model.txt` / `cem_part.txt` (format), Blockbench `optifine_jem.js` + `bedrock.js` (how the de-facto editor reads and writes both), EMF `EMFPartData.java` / `EMFBoxData.java` (`invertAxis` negates `translate` and `rotate` per axis and mirrors boxes per axis: `c[i] = −c[i] − size[i]`).

For a JEM with `invertAxis: "xy"` (every Patrix JEM, every Blockbench-exported JEM):

| JEM | Bedrock |
|---|---|
| top-level part `translate: t` | `pivot = (t.x, −t.y, −t.z)` |
| box `coordinates: [x, y, z, w, h, d]` (top level: absolute) | `origin = (−(x + w), y, z)`, `size = (w, h, d)` |
| `rotate: r` (degrees) | `rotation = (−r.x, −r.y, +r.z)` |
| `textureOffset: [u, v]` | `uv: [u, v]` (box UV, same layout) |
| `uvNorth/East/South/West/Up/Down: [u1, v1, u2, v2]` | `uv: {north: {uv:[u1,v1], uv_size:[u2−u1, v2−v1]}, …}` — same face names |
| `sizeAdd` | `inflate` |
| `mirrorTexture: "u"` | `mirror: true` |
| submodel `translate` | pivot = translate (absolute at depth 0; depth ≥1: parent pivot + translate); its boxes are **relative to that pivot** (add it before the mapping above); `parent` = the enclosing part/submodel |
| `attach: true` | keep the vanilla part's cubes as well (Bedrock: add the vanilla cubes to the bone, or a second render pass) |
| `scale` | render-controller / bone scale (rare) |

**Proof (`tools/r1_jem_vs_bedrock.py`):** the vanilla Java models in JEM form (Ewan Howell's CEM Template Models v5.0.3, 224 models — the templates every CEM author starts from) converted with CONV-1 and matched cube-by-cube against Mojang's vanilla Bedrock geometries (bedrock-samples 1.26.50.4): **240 cubes reproduced, 192 pivots exact, 12/12 rotations exact** where Mojang keeps the rotation in the geometry (pig, sheep ×2, cow, llama incl. both chests `[0,−90]→[0,90]`, turtle ×2, panda, ravager horns `[−60]→[60]`, zombie-villager brim `[90]→[−90]`), including submodel cases (sheep/panda `rotation` submodels, turtle `body_rotation`, armadillo `head_rotation`). Every other rotation-sign triple fails; leaving x unmirrored loses 10 cubes and 19 pivots. Mobs that did NOT match are the ones Mojang re-authored for Bedrock (fox, cat, horse v3, dolphin, cod, salmon, axolotl, goat, rabbit, parrot, camel, bee, allay, squid, bat, phantom, ghast…) — for those, *Bedrock vanilla ≠ Java vanilla*, which is exactly why a faithful Java conversion is worth having.

**Where vanilla hides its rotations** (`animation.llama.setup = "-this"`, `cow.setup`): the modern vanilla files carry no body rotation and let a setup animation apply it; our pack shims those animations to no-ops, so for OUR mobs the geometry must carry every static rotation. Unchanged practice, now understood.

---

## §3 · CEM-RT: what the JEM means at runtime — SOURCE / MODEL

From the EMF source (the open-source, Fresh-Animations-compatible CEM implementation) and the CEM Template Loader (the animation previewer everyone uses):

1. **Hierarchy.** Each JEM top-level part becomes a **child of the vanilla part** of the same name (`EMFModelPartRoot.addAndSetVariantOfJem`); with `attach: false` the vanilla cubes are removed, the vanilla part's transform stays. The vanilla part keeps whatever its code sets every frame — the quadruped body's `+π/2`, the head's look-at, the walk cycle on legs — **unless** the JEM animation assigns `<part>.rx/ry/rz/tx/ty/tz`, which overrides it (`SOURCE`).
2. **Replace, don't add.** Animated `tx…rz` SET the ModelPart fields the static `translate`/`rotate` initialised (`EMFModelOrRenderVariable.setValue → modelPart.xRot = value`) — REPLACE semantics (`SOURCE`). This is why the vanilla templates carry `rotate: [−90,0,0]` **and** `"this.rx": 0` on quadruped bodies (the editor sees the static pose; in-game the vanilla parent supplies the rotation and the custom part's own is zeroed), and why the Patrix cow's `udder.rx = pi/2 + …` next to `rotate: [−90,0,0]` is the same angle twice, not 180°.
3. **Units and signs.** `rx/ry/rz` are Java radians (= Bedrock degrees / 57.3, same sign as the Bedrock file); `tx/ty/tz` are Java rotation-point coordinates: root part → `pivot_BB = (−tx, 24 − ty, tz)`; depth-1 submodel → `(−tx, −ty, tz)` absolute; deeper → relative to the parent (`MODEL`, from the Template Loader; matched on one witness case: our cow's body sits at Patrix's animated `body.tz = 1`, not the file's 2).
4. **Rest pose = animated pose.** Patrix animations assign positions and rotations unconditionally (`head2.ty = −17.5 + …`, `leg1.ty = 24 + …`); at rest (still, on the ground, day, adult) they leave a slightly splayed idle stance and part offsets of up to 1–2 cubes from the static file. `tools/cem_eval.py` evaluates the CEM expression language (all Patrix expressions parse; `var.*` recurrences iterated to a fixed point); `tools/jem_convert.py` bakes the rest pose with the vanilla-parent + REPLACE model.

**What the bake gets right and wrong today** (contact sheet `_design/mob-conversion-audit-sheet-2026-09-27.png`, column B): coherent for cow, llama, wolf, cat, pig, sheep, dolphin; **wrong** for fox, polar bear, horse, turtle, axolotl — their vanilla parts have code-set rest transforms (positions, not just rotations) that the CEM templates' static `rotate` does not carry. → controlled-test list in §7.

---

## §4 · Why the direct conversion failed last time — VERIFIED (from the recovered script)

`convert_mobs (conflict 2026-04-22-22-49-32).py` (Drive, recovered today; the Gemini-era converter):

| what it did | what is right | effect you saw |
|---|---|---|
| `pivot = (−t.x, t.y, t.z)` | `(t.x, −t.y, −t.z)` | every pivot mirrored in x and flipped in y/z (cow head pivot at y = −20, z = +8): every rotated bone (bodies, tails, ears, fins) swung about the wrong point — **vertical gaps, bodies floating or sunk, parts "connected incorrectly"** |
| submodel `translate` treated like a top-level one; boxes of submodels treated as absolute | submodel boxes are relative to the submodel pivot; translates accumulate from depth 1 | every submodel (Patrix uses them for every head, body, tail) landed offset from its parent — **horizontal gaps** |
| looked for `box["faces"]` | JEM uses `uvNorth…uvDown` | per-face UVs dropped → wrong texture regions ("wildly visually incorrect") |
| JPM submodels flattened into the parent | keep them as child bones | pivots lost |
| `rotation = (−rx, −ry, rz)` | correct | — |

All four are mechanical and are now specified (§2). The failure was never an unknowable engine quirk.

---

## §5 · Audit of the shipped RP-07 mobs — VERIFIED numbers, MODEL for the rest column

Method (`tools/r2_patrix_audit.py`): the Patrix 1.21.11 128× mobs JEMs (152 files, pulled from the Drive archive by range-read) converted with CONV-1, compared with `geometry.<mob>.patrix` in RP-07 1.4.10: exact cube reproduction (position + size), and the mean/max distance between same-size cubes in the rendered pose (cube = 1/16 block). "rest" = the CEM-RT bake (§3, model-dependent).

```
mob                    cubes P/O exact  static mean/max  rest mean/max noSize
axolotl                  17/17       0     5.2/15.5       18.2/24.2         0
camel                    15/15      14     0.3/3.0         0.2/3.1          0
cat                      13/13       7     0.6/2.1         2.2/8.0          0
chicken                  17/17       0     1.1/1.4         1.3/1.6          4
cod                      11/11       0     2.8/9.0         4.0/8.7          0
cold_chicken             18/17       0     1.2/1.4         1.2/1.5          5
cow                      15/15       0     1.6/3.2         1.6/3.3          0
dolphin                  10/10       0     4.0/7.3         6.6/8.5          0
donkey                   17/17       8     6.9/22.8        6.6/17.8         2
fox                      11/10       0     5.1/7.2         5.4/9.4          1
frog                     17/12       0     1.6/2.5         1.2/2.2         12
glow_squid               12/9        0       -/-             -/-           12
goat                     17/18       0     4.6/7.1         5.3/8.3          7
horse                    15/15       8     7.8/22.7        7.5/18.5         2
llama                    21/19       6     0.5/1.6         1.4/2.0         11
mooshroom                21/15       2     1.3/2.5         1.3/3.3          6
mule                     17/17       8     6.4/21.4        6.7/19.7         1
ocelot                   13/15       0       -/-             -/-           13
panda                     9/9        1     4.0/7.4         4.0/7.4          0
pig                      10/9        3     0.4/1.0         0.5/1.4          3
polar_bear               11/10       4     7.1/15.0        7.0/15.0         2
pufferfish_large         14/14       0     7.7/13.0        7.4/13.4         0
pufferfish_medium        12/12       0     6.6/9.0         5.4/8.2          0
pufferfish_small          4/4        0     2.0/2.0         2.1/4.2          0
rabbit                   12/12       2     1.9/3.6         2.6/4.3          0
salmon                   11/11       0     6.3/15.5       12.7/16.6         0
sheep                     9/9        1     0.8/1.4         0.9/1.4          0
sheep_wool                6/6        5     0.3/1.6         0.8/1.6          0
squid                    12/9        0       -/-             -/-           12
tadpole                   3/3        0     1.8/1.8         1.5/2.0          0
trader_llama             21/19       8     3.3/11.2        3.0/7.9          2   (1.4.10; 1.4.11 = the llama row)
turtle                    9/9        0    12.5/12.6       17.8/18.4         6
warm_chicken             17/17       0     1.2/1.4         1.2/1.5          4
wolf                     13/13       0     6.4/11.0        6.5/11.3         1
zombified_piglin         16/16       6     0.4/1.7         0.9/2.6          8
```

Reading it: **≤ 1 cube** (approximations the witness rounds converged on): camel, sheep_wool, pig, zombified_piglin, llama, cat, sheep. **1–2:** the chickens, mooshroom, cow, frog, tadpole, rabbit, small pufferfish. **2–5** (parts in the wrong place): cod, dolphin, panda, goat, fox, axolotl, (trader llama before today). **> 5** (a different shape): salmon, wolf, mule, donkey, medium/large pufferfish, polar bear, horse, turtle. **No same-size cubes at all:** ocelot, squid, glow squid (different cube sizes = different models). "noSize" counts Patrix cubes with no same-size cube in ours (fur shells, chests, the frog's tongue/eyes).

Concrete errors found by inspection (cow, llama in detail): the cow's **udder is at the front of the body and unrotated** (Patrix: rear, horizontal); the llama/trader **chests are missing** (Patrix models them; visibility is animated); **ear bones are named mirrored** (our `right_ear` sits on the entity's left — cosmetic until an asymmetric animation); the llama's **legs were lengthened** 0–13 → 0–16 and the body raised to meet them (Patrix: body 11–22 on 13-cube legs); the turtle's parts are **spread with gaps**; the dolphin's part order differs. RP-06 (hostile) could not be audited — its build directory is not in this sandbox (backlog).

**Verdict:** your instinct is right. The shipped conversions are witness-converged approximations, not conversions; the ones ≤ 1 cube are fine to keep until the tool exists, the rest should be regenerated by the tool and witnessed as a family.

---

## §6 · Better ways to recreate Java mobs and textures on Bedrock — research

What Bedrock can do, mapped to what Patrix/Java needs (sources: Microsoft Learn Vibrant Visuals docs, the Molang query reference, the Bedrock geometry/animation formats we already ship):

1. **Geometry fidelity: cube-exact.** Bedrock's geometry format is a superset of what JEM needs (box UV, per-face UV, per-cube pivot/rotation, inflate, mirror, hierarchy, `poly_mesh` for non-box shapes — not needed, Patrix is boxes). With CONV-1 every Patrix mob can be reproduced to the cube, including the fur shells, chests, saddles and decor layers as bones. Texture resolution is free: `texture_width/height` = the JEM `textureSize` (128×64) while the PNG is 1024×512 — already how we ship.
2. **Textures: PBR on mobs is supported.** Vibrant Visuals: "you can now set PBR textures for not just blocks but entities, mobs, particles, and items… add them to the correct folder: textures/entity" (Microsoft Learn, Vibrant Visuals resource packs). So Patrix's `_n`/`_s` LabPBR maps convert per Lesson #156 into MERS + normal texture sets next to each entity texture — the same pipeline as blocks, per variant texture. Emissive eyes (Patrix `_s` alpha) become the MERS E channel. (The April converter's MER formula — metal = G > 0.9, roughness = (1−R)², heightmap from the normal alpha — is NOT #156; do not reuse it.)
3. **Variants and randomness.** Patrix's random models (`cow2.jem` + `.properties`) and per-biome textures map to Bedrock render-controller arrays (`Array.variants[query.variant]` / `query.mark_variant` / `query.skin_id`) driven by BP components (`minecraft:variant` + spawn-time random groups). Already the pattern in RP-07 (`controller.render.pw_llama`).
4. **Per-part textures and layers.** A JEM part may carry its own `texture` (decor, wool, armor layers); Bedrock renders one texture per render-controller pass, so layers become additional render controllers with `part_visibility` on the layer bones — the trader decor/carpet case (done as composites today; controllers are the faithful way and keep the decor colours).
5. **Animation parity.** CEM expressions translate to Molang almost 1:1: same operators, `sin/cos` (Molang in **degrees** — L-MOLANG-DEG: every CEM `sin(x)` becomes `math.sin(x*57.2958)`), `clamp/min/max/abs/floor/…`, `if(c,a,b) → c ? a : b` (chains → nested), `random(id) → variable seeded once in pre_animation`, `var.x → variable.x` (persistent per entity), `torad/todeg → *0.01745 / *57.2958`. Parameters: `limb_swing → query.modified_distance_moved` (same units: vanilla's `cos(q.modified_distance_moved*38.17)*80` is Java's `cos(limbSwing*0.6662)*1.4 rad`), `limb_speed → query.modified_move_speed`, `age → query.life_time*20`, `head_pitch/head_yaw → query.target_x_rotation/target_y_rotation` (degrees, already), `is_child → query.is_baby`, `is_in_water`, `is_on_ground`, `hurt_time → query.hurt_time`, `is_sitting`, `is_angry`, `is_sneaking`, `is_sprinting`, `is_tamed`, `is_burning → query.is_on_fire`, `is_wet → query.is_in_water_or_rain`, `is_ridden → query.is_ridden`(verify), `swing_progress → query.attack_time`(verify), `day_time → query.time_of_day*24000`, `frame_time → query.delta_time`. Bedrock animation rotation is **additive to the bind pose**, CEM is **replace** — so the tool must emit `(animated − rest)` per channel, with the bind pose set to the rest pose (§3). `visible → part_visibility` in a render controller (Molang), `render.shadow_size` → BP `minecraft:scale`/shadow. Not portable: `player_pos_*` (no Bedrock query for the viewer), `rule_index`, `print`.
6. **Existing tools — none we can adopt as-is.** Blockbench (JEM import → Bedrock export) encodes exactly CONV-1 but converts only the static pose and no animations, needs a GUI, and mis-parents when a JEM relies on vanilla parents; the CEM Template Loader previews CEM animations but exports none; EMF is a Java runtime. There is no public JEM→Bedrock *animation* converter; community "Fresh Animations for Bedrock" packs are hand-made. So the tool is ours to build — and now specifiable.

---

## §7 · Proposal — the AbsolutRealism Mob Conversion Tool (`jem2bedrock`) and Standard v2 — FOR APPROVAL, NOT BUILT

**Principle:** the tool is proven against **ground truth we do not control** (Mojang's vanilla pairs) before it touches a Patrix mob, and every Patrix mob it emits comes with a render sheet for your eyes before it ships.

**Phase 0 — controlled tests of the runtime model (needs your game, ~1 session).** A tiny probe pack (job-only, like the runner) showing one mob's bones with colour-coded faces to settle the three `MODEL` items: (a) submodel `tx/ty/tz` depth semantics, (b) the vanilla rest transforms of parts the templates cannot express (fox head/body, polar bear, horse neck/head, turtle shell, axolotl), (c) the Z-rotation sign on a real Z-rotated bone. Each becomes a `VERIFIED` line in Standard v2.

**Phase 1 — geometry converter (static + rest bake).** `jem2bedrock.py`: JEM → CONV-1 → rest bake (§3) → `geometry.<mob>.patrix` with our bone-name conventions (documented map: `leg1..4 → leg0..3`, `*_rotation` → `*_cube`, ears named by the entity's own side). Gate A: the vanilla-pair test (`r1`, must stay 240/192/12). Gate B: pose sanity (body on legs, head attached, no floating cube > 2 cubes from any neighbour). Gate C: a contact sheet per mob (static | rest | previous ship) for witness.

**Phase 2 — animation translator.** CEM expression AST → Molang (§6.5), `var.*` → `variable.*` initialised in `pre_animation`, delta-from-rest emission, one Bedrock animation per JEM part group; `visible` → render-controller `part_visibility`. Gate: `molang_eval.py` replays both languages at 20 sampled states (rest, walk, run, child, water, hurt) and the joint angles agree within 1°.

**Phase 3 — textures.** LabPBR → MERS per #156 for every entity texture set, texture-set JSON per variant; decor/armor layers as render-controller passes.

**Phase 4 — re-conversion of RP-07 (then RP-06) by family**, worst-first from §5: aquatics (turtle, salmon, pufferfish ×3, dolphin, cod, axolotl), equines (horse, donkey, mule), wolf/fox/polar bear, then the ≤ 1-cube set last (or never, your call). Each family ships as a normal complete-pack release with its sheet and lineup items.

**Standard v2 outline** (replaces the superseded parts; keeps §4.1/§4.3 UV rules, §5.3, §7.1, §8, §11, §12): frames & law (§1 here), CONV-1 table (§2), CEM-RT (§3), the CEM→Molang map (§6.5), bone-naming map, the gates, and a "how to add a mob" recipe.

---

## §8 · Open questions for you
1. Phase 0 needs your hardware for ~1 session (the probe pack) — before or after the current lineup?
2. Families: agree with worst-first (aquatics → equines → wolf/fox/bear → the rest)? Anything you want untouched because you like it as is?
3. Chests, saddles, decor, armor layers: convert them (faithful) or keep omitting (simpler)?
4. Bone naming: keep our `leg0..3 / body_cube` convention (so BP-side animations keep working) or adopt Patrix's names (easier diffing)?

---

## §9 · Files
Tools (research): `tools/r1_jem_vs_bedrock.py` (vanilla-pair experiment), `tools/r2_patrix_audit.py` (audit), `tools/cem_eval.py` (CEM expression evaluator), `tools/jem_convert.py` (CONV-1 + rest bake prototype), `tools/entity_render.py` (perspective renderer, law fixed). Intake: `_intake/cem-spec/` (OptiFine specs), `_intake/blockbench/` (codecs 4.12.4), `_intake/cem-templates/` (CEM Template Models v5.0.3 + plugin), `_intake/emf/` (EMF source files), `_intake/patrix-mobs/` (152 Patrix JEMs), `_intake/genesis/convert_mobs_2026-04-22.py`. Figures: `_design/mob-conversion-audit-sheet-2026-09-27.png`. Logs: `_logs/r2_patrix_audit_v2.json`.

Sources: OptiFine CEM docs (sp614x/optifine `cem_model.txt`, `cem_part.txt`, `cem_animation.txt`); Blockbench 4.12.4 `js/io/formats/optifine_jem.js`, `bedrock.js`, `js/outliner/cube.js` (ZYX); Ewan Howell CEM Template Loader + `cem_template_models.json` v5.0.3; Traben `Entity_Model_Features` (`EMFPartData`, `EMFBoxData`, `EMFModelPartRoot`, `EMFModelOrRenderVariable`); Mojang `bedrock-samples` 1.26.50.4 models + `llama.animation.json`; Microsoft Learn — Vibrant Visuals resource packs, Molang query functions.
