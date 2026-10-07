# JEM-to-Bedrock Conversion Standard

> **Methodology reference for the AbsolutRealism mob conversion project.**
> Authored by Abs0lum and Claude (Anthropic) across many witness-test iterations
> on v1.3.34 → v1.3.35 patches 1-8. Documents the technical conventions, gotchas,
> and rules-of-thumb developed for translating OptiFine JEM entity models
> (`.jem`/`.jpm` files) into Bedrock Edition geometry (`.geo.json`).

---

> **SUPERSESSION NOTICE — 2026-09-27 (D-C255, L-ROT-DIR; evaluated at Abs0lum's request 15:17 CT per OPERATING-MANUAL §15).**
> The frame and rotation statements in §2.1, §2.3, §3.1 (X and Z sentences), §3.2 and §4.2 below are **SUPERSEDED BY L-ROT-DIR / CONV-1**
> (full derivation, evidence and the verified mapping: `MOB-CONVERSION-RESEARCH-2026-09-27.md`). The original text is kept unchanged
> and tagged; do not build from it. Verified replacement, in short:
>
> 1. **Bedrock file frame:** x is MIRRORED relative to the world (file +x = the entity's LEFT; vanilla `leftArm` pivots at +5). Face names
>    (north/east/south/west/up/down) are WORLD directions, so per-face UVs copy across unchanged.
> 2. **Rotation law (file coordinates):** a bone rotation `[rx, ry, rz]` about its pivot acts as `Rz(-rz) · Ry(+ry) · Rx(-rx)` with standard
>    right-handed matrices, X applied first (Blockbench Euler order ZYX). Hence `+90` about X puts the cube's local +Y at the FRONT (−z) and
>    its local +Z UP (the exact opposite of the old §3.1/§4.2 text); `+90` about Y turns the front toward file −x; `+rz` tips the top toward
>    file +x. Verified on: vanilla `wolf_armor.geo.json`, the Java→Bedrock cow conversion (`bind_pose_rotation [90,0,0]`), the vanilla llama
>    chests / horse bags `[0,±90,0]`, our witnessed cow/wolf, and his 09-27 trader-llama screenshot.
> 3. **CONV-1 — JEM (`invertAxis: "xy"`, every Patrix and every Blockbench-made JEM) → Bedrock geometry:**
>    `pivot = (t.x, −t.y, −t.z)` for a top-level part (t = `translate`); `cube.origin = (−(c.x + w), c.y, c.z)`, `size = (w, h, d)`
>    (c = box `coordinates`); `rotation = (−r.x, −r.y, +r.z)` (r = `rotate`); `textureOffset` and `uvNorth…uvDown` copy as they are
>    (`uv_size = (u2−u1, v2−v1)`); `sizeAdd → inflate`; `mirrorTexture: "u" → mirror: true`. **Submodels:** pivot = the submodel's own
>    `translate` (absolute at depth 0, added to the parent submodel's pivot deeper); its boxes are RELATIVE to that pivot; same rotation and
>    box rules; parent = the enclosing part/submodel. Proven by reproducing Mojang's own vanilla Bedrock geometries from the vanilla Java
>    models (CEM Template Models): 240 cubes, 192 pivots, 12/12 file rotations across 30 mobs (`tools/r1_jem_vs_bedrock.py`).
> 4. **Old §2.3 "negate Y" and old §3.2 "[-rx, ry, -rz]" are wrong for `invertAxis: "xy"` files** — nothing is negated in y; x is mirrored for
>    BOXES only (not for `translate`); the rotation rule is `(−rx, −ry, +rz)`.
> 5. **Runtime (CEM-RT, from the EMF source + the CEM Template Loader):** each JEM part is a CHILD of the vanilla part of the same name and
>    inherits the vanilla code pose (a quadruped body's +90 X, the head's look) unless the JEM animation assigns `<part>.rx/ry/rz/tx/ty/tz`;
>    animated variables REPLACE the static `translate`/`rotate` values (rx/ry/rz in radians = Java angles = Bedrock degrees; tx/ty/tz = Java
>    rotation-point coordinates: for a root part `pivot_BB = (−tx, 24 − ty, tz)`). The in-game rest pose of a Fresh-Animations-style JEM
>    (Patrix) is therefore the ANIMATED rest pose, not the file's static pose — a converter must evaluate the animations at rest.
> 6. The UV rules of §4.1/§4.3, the joint-pivot rule §5.3, the inflate rule §7.1 and the process rules (§8, §11, §12) are unaffected.

## §1. Why this document exists

Every JEM mob in the Patrix Java mod was authored under a different convention than Bedrock geometries use. A naive coordinate copy produces mobs that are mirrored, upside-down, scaled wrong, or have geometrically-disconnected limbs. This document captures the conversion rules we discovered through ~30 mob conversions across 8 witness-test iterations.

The methodology is empirical: every rule was developed by shipping a build, observing the visual result on real hardware (Android device, in-game), and adjusting. We document both the rules and the diagnostic process so the same approach can be applied to future mob conversions.

---

## §2. Coordinate systems

### §2.1. JEM (OptiFine CEM) convention

> **SUPERSEDED BY L-ROT-DIR / CONV-1 (2026-09-27, D-C255)** — for `invertAxis: "xy"` files the JEM frame IS the world frame (y up, −z front, +x = the entity's right, boxes absolute); see the notice at the top.

OptiFine entity models use a coordinate system where:
- **+X**: right (when facing the entity from its front)
- **+Y**: DOWN (positive Y goes into the ground)
- **+Z**: forward (toward where the mob faces)

Y-being-downward is the most common source of conversion errors. JEM files written without `invertAxis` flags have their Y axis inverted compared to Bedrock.

JEM files may declare `invertAxis: xy` or `invertAxis: yz` etc., which inverts ONE OR MORE axes from the standard JEM convention. After inversion:
- `invertAxis: xy` → X becomes leftward-positive, Y becomes UPWARD-positive (matches Bedrock Y)
- `invertAxis: yz` → Y becomes UPWARD, Z becomes BACKWARD-positive (matches Bedrock Z)
- `invertAxis: y` → Just Y becomes UPWARD (closest to Bedrock convention)

### §2.2. Bedrock geometry convention

Bedrock `.geo.json` uses:
- **+X**: rightward (same as JEM standard)
- **+Y**: UPWARD (opposite of standard JEM Y)
- **+Z**: backward (toward the rear of the mob, since mobs face -Z by default in Bedrock)

The cube origin field is the corner at MINIMUM (X, Y, Z) of the cube. Size extends in +X, +Y, +Z directions. So a cube at `origin: [-4, 0, -5]` with `size: [8, 7, 13]` extends:
- X from -4 to +4 (centered on the entity's centerline)
- Y from 0 to +7 (sitting at the entity's feet, body height of 7 units)
- Z from -5 to +8 (extending behind the entity origin by 5 units, forward by 8)

### §2.3. The Y-axis flip rule

> **SUPERSEDED BY L-ROT-DIR / CONV-1 (2026-09-27, D-C255)** — with `invertAxis: "xy"` nothing is negated in y; `origin_B = (−(c.x + w), c.y, c.z)`, `pivot_B = (t.x, −t.y, −t.z)`.

When converting JEM coords to Bedrock:
- If JEM file has no `invertAxis` declarations: **negate Y for every cube origin and pivot**
- If JEM file has `invertAxis: xy`: **negate X for every cube origin and pivot** (Y already matches Bedrock)
- If JEM file has `invertAxis: yz`: **negate Z for every cube origin and pivot** (Y already matches, Z needs flip)

For SIZE: keep size dimensions positive in Bedrock. If Y is negated, the cube's new Y range is `[-(origin_Y + size_Y), -origin_Y]` — so:
- `new_origin_Y = -(origin_Y + size_Y)` (this is the new minimum Y)
- `new_size_Y = size_Y` (unchanged)

This is reflection across Y=0, expressed as a cube-position transformation.

---

## §3. Rotation conventions

### §3.1. Bedrock uses a LEFT-HANDED rotation convention

> **X and Z sentences SUPERSEDED BY L-ROT-DIR (2026-09-27, D-C255):** +X rotation tips the cube's top toward −Z (the FRONT); +Z tips the top toward file +x (the entity's left). The Y sentence stands (clockwise seen from above, in the world).

This is critical and counterintuitive. In Bedrock:
- Positive X rotation tips the cube's top toward +Z (backward, toward tail)
- Positive Y rotation rotates the cube clockwise when viewed from above (+Y looking down)
- Positive Z rotation tilts the cube's top toward -X (toward the entity's left side)

Negative rotations go the opposite direction.

### §3.2. JEM rotation conversion to Bedrock

> **SUPERSEDED BY CONV-1 (2026-09-27, D-C255):** for `invertAxis: "xy"` the rule is `rotation_B = (−rx, −ry, +rz)`; vanilla-verified (llama chests, cow/pig/sheep bodies, ravager horns, villager brim).

For a JEM rotation `[rx, ry, rz]` with NO axis inversion:
- Bedrock rotation: `[-rx, ry, -rz]` (negate X and Z rotations because Y is inverted)
- This handles the convention difference

For JEM with `invertAxis: xy`:
- Bedrock rotation: `[rx, -ry, -rz]` (negate Y rotation because X is now inverted, negate Z because... actually this is complex)

The practical rule we developed: **after copying rotations, witness-test, and negate any rotation axis whose visual effect is opposite of intended**.

### §3.3. Per-cube rotation vs bone rotation

Bedrock supports rotation at TWO levels:

**Bone-level rotation** (`rotation` field on bone): Affects the bone's cubes AND all child bones. Useful for joint-style rotations like leg swings during walk animation.

**Cube-level rotation** (`rotation` + `pivot` fields on the cube itself): Affects only that cube. Does NOT cascade to siblings or children. Useful for individual cube orientation fixes (like the dolphin/turtle Y-flip in Patch 8).

Cube-level rotation pivot is in MODEL space (absolute coordinates), not relative to the cube's origin. To rotate a cube around its own centroid:
- `pivot: [origin_X + size_X/2, origin_Y + size_Y/2, origin_Z + size_Z/2]`
- `rotation: [degrees_X, degrees_Y, degrees_Z]`

---

## §4. UV mapping conventions

### §4.1. UV space orientation

Bedrock UVs are declared in 2D texture space with:
- **U**: horizontal pixel position (typically left-to-right)
- **V**: vertical pixel position (top-to-bottom in image space)

A face's UV declaration: `{"uv": [u_start, v_start], "uv_size": [u_extent, v_extent]}`.

**Negative `uv_size` values flip the texture sample on that axis.** This is critical:
- Positive U size: texture goes left-to-right on the face
- Negative U size: texture goes right-to-left (mirrored horizontally)
- Positive V size: texture goes top-to-bottom on the face
- Negative V size: texture goes bottom-to-top (mirrored vertically / "upside down")

To flip a texture vertically WITHOUT changing the region:
- Original: `uv: [u, v], uv_size: [su, sv]`
- V-flipped: `uv: [u, v + sv], uv_size: [su, -sv]`

This formula is **self-inverse**: applying it twice returns to the original. We use it for testing whether a face's V orientation is the source of an upside-down appearance.

### §4.2. Face naming under cube rotation

> **Direction table SUPERSEDED BY L-ROT-DIR (2026-09-27, D-C255):** after a `[90,0,0]` bone rotation the cube's local +Y goes to −Z (FRONT), local −Y to +Z (back), local +Z to +Y (UP), local −Z to −Y (down). So the cube's "up" face becomes the world FRONT face and its "south" face the world TOP. The diagnostic rule below still applies with these corrected directions.

When a cube has bone-level OR cube-level rotation, the FACES rotate with the cube. The face named "up" in the geometry JSON corresponds to the cube's LOCAL +Y face, but in world space it may point any direction after rotation.

Example (sheep): the body_cube has `rotation: [90, 0, 0]` on its bone. After this 90° X-rotation:
- Cube's local +Y direction → world +Z (toward back of mob)
- Cube's local -Y direction → world -Z (toward front)
- Cube's local +Z direction → world -Y (down)
- Cube's local -Z direction → world +Y (up)

So the cube's "up" face is now the world REAR face. The cube's "south" face is now the world BOTTOM face. UV mappings assigned to the cube faces follow the faces through rotation.

**Diagnostic rule**: when a witness reports "the X face looks wrong" on a rotated cube, work out which CUBE-LOCAL face corresponds to the WORLD-FRAME direction the witness is looking at. The fix may be on a face whose name doesn't match the witness's description.

### §4.3. The UV inversion problem

Many JEM mobs have textures authored for cubes that will be transformed during conversion. When you copy UVs naively from JEM, the texture region is correct but the face it's applied to may now expect a different orientation.

Common symptoms of UV inversion:
- Texture appears upside-down on a face
- Texture appears mirrored (left/right swap)
- Wrong content shows on a face (e.g., side view on a face that should show belly)

**Diagnostic process for UV problems**:
1. Crop the texture region for the misbehaving face using its declared UV (`uv` and `uv_size`)
2. Visually inspect the cropped region — is it the EXPECTED content for that face?
3. If yes (content correct, orientation wrong): try V-flip via the self-inverse formula
4. If no (content wrong): the JEM author mapped a different texture region to this face; you need to find the correct region in the texture file
5. If face is blank or empty texture region: the JEM author didn't draw that face (often happens with rear/bottom faces); remap to a face that has content, even if it's a duplicate of another face

---

## §5. Bone hierarchy and parent-child relationships

### §5.1. Pivot inheritance rules

In Bedrock geometry:
- Each bone has a `pivot: [X, Y, Z]` in MODEL SPACE (absolute, not relative to parent)
- Each bone may have a `rotation` (Eulerangles in degrees)
- Each bone may have a `parent: "<bone_name>"`

When a parent bone has a rotation:
- The parent's cubes rotate around the parent's pivot
- All CHILD bones inherit the parent's rotation in their rendered position
- The child's declared pivot stays at its absolute model-space coords for declaration purposes, but the child's RENDERED position is transformed by the parent's rotation

This means: if you change a parent bone's rotation, the children move with it visually. If you want a child to stay in the same world position despite the parent rotating, you need to apply an inverse rotation to the child (compounding rotations).

### §5.2. Body-local coordinate computation

When a parent bone has rotation `R`, and you want a child to be at WORLD position `(X', Y', Z')`, you must declare the child's pivot at the BODY-LOCAL position that, when rotated by `R`, lands at `(X', Y', Z')`.

For a `[0, 45, 0]` rotation (like the frog's body):
- Forward transform: `X' = 0.707(X + Z)`, `Z' = 0.707(Z - X)`, Y unchanged
- Inverse transform: `X = 0.707(X' - Z')`, `Z = 0.707(X' + Z')`, Y unchanged

Example (frog right_arm at world position (-1.5, ?, -3.5) after body rotates 45°):
- `X = 0.707(-1.5 - (-3.5)) = 0.707 × 2 = 1.414`
- `Z = 0.707(-1.5 + (-3.5)) = 0.707 × (-5) = -3.536`
- Declare child pivot at `(1.414, ?, -3.536)` in body-local coords

### §5.3. Joint-pivot rule

**A bone's pivot should be at the JOINT location, not the cube's center.** For look-at animations, walk-cycle leg swings, and any rotation that should look like a hinge or joint, the pivot must be at the point where the limb/head meets the body.

Common error: cube is repositioned but pivot is not, causing the bone to rotate around the wrong point. Symptom: head appears to "disconnect" when looking around (Patch 8 fox bug), legs swing around an off-center point.

**Diagnostic**: find the bone's pivot in the geo JSON, compare to the cube's origin/size. The pivot should typically be at one CORNER of the cube (the corner closest to the body or other parent geometry), not at the cube's centroid.

---

## §6. Texture conventions

### §6.1. MERS (4-channel) vs MER (3-channel)

Bedrock supports two texture set formats:
- **MER** (Metalness/Emissive/Roughness), 3-channel: format_version 1.16.100
- **MERS** (Metalness/Emissive/Roughness/Subsurface), 4-channel: format_version 1.21.30

For PBR-enabled mobs, use MERS. Each channel encodes:
- **R**: Metalness (0 = dielectric, 255 = pure metal)
- **G**: Emissive intensity (0 = no glow, 255 = full glow)
- **B**: Roughness (0 = mirror, 255 = matte)
- **A** (subsurface): 0 = no SSS, 255 = max subsurface scattering

For neutral mobs (no subsurface needed), the A channel can be 0 or 255 depending on convention.

### §6.2. Patrix LabPBR → Bedrock MERS conversion

Patrix textures use LabPBR convention with `_n` (normal) and `_s` (specular) suffixes. The `_s` files encode:
- R: smoothness (255 - roughness)
- G: metalness or porosity (depending on value)
- B: subsurface or porosity (depending on value)
- A: emissive

Conversion to Bedrock MERS:
- Bedrock R (metalness) = Patrix G (when G > 64, metal; else 0)
- Bedrock G (emissive) = Patrix A
- Bedrock B (roughness) = 255 - Patrix R (invert smoothness)
- Bedrock A (subsurface) = Patrix B (when value < 64, subsurface percentage; else 0)

This was Lesson #156 from earlier in the project. We use it when converting any Patrix texture set to Bedrock.

### §6.3. Alpha dilation for translucent foliage

Bedrock renders translucent textures with alpha-channel cutoff. If a texture has hard transparent boundaries (alpha = 0 next to alpha = 255), the boundary pixels render incorrectly — they sample the transparent neighbor and produce black artifacts.

Fix: **alpha-dilate** the texture before shipping. Use a Photoshop-like alpha-edge-blur, or a Python script that finds alpha-1 pixels at the edge of alpha-0 regions and replicates the nearest alpha-255 pixel's RGB to the alpha-0 neighbors. This produces smooth alpha boundaries.

Applied to: leaf textures, hair textures, anything with hard alpha edges.

---

## §7. Common conversion gotchas

### §7.1. The "0.01 inflate" rule

Every cube with `size_X = 0`, `size_Y = 0`, or `size_Z = 0` (zero-thickness in some axis) must have an explicit `inflate: 0.01` field. Without it, Bedrock may render the cube as invisible (the texture has zero area).

We use `0.01` as the standard inflate amount because:
- It's small enough to not visibly alter the cube's apparent thickness
- It's large enough to ensure the face is rendered

Exception: chicken leg cubes use `inflate: 0.05` because they're rendered against a slightly-occluding body and need slightly more "push out" to be visible.

This is a STANDING RULE — never ship a cube with zero size in any axis without an inflate.

### §7.2. Mirror flag interactions

The `mirror: true` field on a cube flips the texture mapping on the X axis. Useful for symmetric mob features where left/right share UVs but should look mirrored.

**Trap**: when combined with `rotation: [0, 0, 180]` on the same cube (or its parent bone), the mirror flag may double-flip the X axis, producing apparently unchanged textures while ALSO breaking the rendering on other faces.

**Rule**: if you add cube-level rotation, remove any `mirror: true` flag. Re-evaluate manually after rotation if the X-axis appearance needs adjustment.

### §7.3. Cross-bone material instance bindings

Bedrock's render_controllers and material assignments can reference bones by name (`Material.<bonename>`). If a bone is renamed during conversion (e.g., JEM `left_leg` → Bedrock `leg0`), the material binding must also be renamed. Otherwise the material defaults to `entity_alphatest` (or whatever the default is) and the visual result is wrong.

Lesson #156 from earlier sessions. Always audit bone-name references in:
- `render_controllers/*.render.json`
- `entity/*.entity.json` (materials, animations sections)

### §7.4. The locked dependency strings

Three `@minecraft/server` string dependencies are LOCKED in this project — they MUST NOT be touched during manifest version bumps:
- BP-01 → RP-02 dependency
- BP-05 → RP-09 dependency
- (one more)

These string references are used for cross-pack feature linking. Changing them breaks the dependency graph. Bump the manifest version uniformly across packs EXCEPT these locked references.

---

## §8. Witness-test diagnostic process

### §8.1. The iteration loop

The conversion process is fundamentally iterative:
1. **Apply** a conversion (geometry, UV, animation)
2. **Build** an `.mcpack`
3. **Witness-test** on real hardware (in-game)
4. **Observe** the visual result
5. **Diagnose** discrepancies between observed and expected
6. **Repeat** with adjustments

There is no shortcut. Static analysis (JSON validation, schema checks) is necessary but NOT sufficient. Witness-tested visual confirmation is the only ground truth.

### §8.2. Reading witness reports

The witness (Abs0lum) reports symptoms he observes. **The symptom report is accepted as truth.** His proposed CAUSE is a starting point for investigation, not a conclusion.

If the witness says "the dolphin is upside down":
- **Truth**: the dolphin appears upside down on his hardware
- **NOT-truth**: any cause he speculates (e.g., "the texture is mirrored")

The implementer's job is to investigate the cause from the position "the symptom is real, why is it happening?". The implementer must NOT defend their model against the witness ("but the JSON validates...").

### §8.3. Plan-first execution

For any non-trivial change:
1. **Propose** the change in writing BEFORE making it
2. **Show math** for any coordinate changes
3. **Wait** for witness confirmation that the proposed change matches their intent
4. **Build** only after confirmation

This is especially critical when the witness has used uncertainty language ("I think...", "maybe..."). Their uncertainty doesn't give the implementer more latitude — it requires MORE rigorous investigation and proposal.

### §8.4. Color-coded inspection mode

For mobs with multiple similar parts (e.g., frog limbs that look identical), use **color-coded inspection** to enable precise witness communication:
1. Remap each part's UV faces to a distinct small region of the texture (e.g., 2×2 pixels of a uniform color)
2. Ship the inspection build
3. Witness identifies each part by its visible color
4. Witness gives directional instructions referencing colors ("swap the green one with the dark one")
5. Implementer makes adjustments based on color references
6. Restore original UVs once geometry is correct

Patch 8's frog limbs used this approach. Each limb mapped to a distinct color (green, light, dark, distinct), enabling unambiguous reference.

---

## §9. Specific conversion patterns by mob type

### §9.1. Quadruped land mobs (pig, cow, sheep, horse family, wolf, etc.)

**Bone hierarchy**:
- `body` (root, parent=-)
- `body_cube` (parent=body, contains the main body cube)
- `head` (root or parent=body, depending on convention)
- `head2` (parent=head, contains head cubes)
- `leg0..leg3` (parent=body) for the four legs

**Diagonal leg pairing for walk**: legs 0 and 3 are diagonally paired (in-phase), legs 1 and 2 are the opposite pair (also in-phase with each other, antiphase with 0&3). This produces a natural walk gait.

**Standing rule**: avoid using vanilla `walk` animation reference if it conflicts with custom bone names. Either remove the vanilla `walk` from `scripts.animate` or override its conditional weight.

### §9.2. Biped mobs (chicken, parrot)

**Bone hierarchy**:
- `body` (root)
- `body_cube`
- `head` / `head2` / etc.
- `leg0`, `leg1` (two legs)
- `left_wing`, `right_wing`
- `tail`

**Walk pattern**: legs 0 and 1 are simple antiphase (180° offset). Body roll is added on the same cycle for chicken's characteristic bobbing walk.

**Chicken-specific**: leg cubes need `inflate: 0.05` to avoid being hidden behind the body.

### §9.3. Aquatic mobs (dolphin, turtle, cod, salmon, tropical fish, pufferfish, axolotl)

**Bone hierarchy** (typical):
- `body` (root)
- `body2` (parent=body, contains main body cube)
- `head` (parent=body2)
- `tail`, `tail2`, `tail3` (segmented tail, parent chain)
- `tail_fin` (parent=tail3 or tail2)
- `top_fin`, `right_fin`, `left_fin` (fins, parent=body2)

**The Y-axis flip problem**: Patrix aquatic mobs were authored with `invertAxis: xy` in JEM, which combined with the conversion process can leave the cubes positioned as if upside down in Bedrock. Solution (Patch 8): per-cube `rotation: [0, 0, 180]` with `pivot` at each cube's centroid. UVs left at originals.

**Swim animation**: tail and tail_fin have progressive phase delays to produce undulating wave motion:
- body undulation: `sin(life_time * F)` with no delay
- tail: `sin(life_time * F - 60°)` (60° behind body)
- tail3: `sin(life_time * F - 120°)`
- tail_fin: `sin(life_time * F - 180°)`

### §9.4. Frog (special: rotated body)

**Bone hierarchy**:
- `body` (root, **rotation: [0, 45, 0]** to make square appear diamond from above)
- `body_main` (parent=body, contains main body cube)
- `head`, `head_main`
- `right_arm`, `right_hand`, `left_arm`, `left_hand`
- `right_leg`, `right_foot`, `left_leg`, `left_foot`

**Diamond-body computation**: limbs use body-local coords that produce desired world positions AFTER the 45° rotation. Use the inverse transform from §5.2.

**Limb identification via color**: see §8.4.

---

## §10. Animation conventions

### §10.1. Procedural walk patterns

Standard procedural quadruped walk:
```
"rotation": [
  "math.cos(query.modified_distance_moved * FREQ) * AMPLITUDE * THRESHOLD",
  0,
  0
]
```

Where:
- `FREQ` is the leg-cycle frequency multiplier (radians per unit of distance moved). Typical values: 22-40 for mid-size land mobs, 14-22 for large quadrupeds, 45+ for small/fast mobs.
- `AMPLITUDE` is the maximum leg swing in degrees. Typical 35-50.
- `THRESHOLD` is the activation factor: `math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)` (Patch 8 standard).

For diagonally-paired legs:
- `leg0`, `leg3`: same phase (e.g., `cos(stride)`)
- `leg1`, `leg2`: opposite phase (e.g., `cos(stride + 180°)`)

### §10.2. Idle animation pattern

Standard idle (slow breathing + occasional head twitch):
```
"body": { "position": [0, "math.cos(query.life_time * 1.5) * 0.15", 0] },
"head2": { "rotation": [
  "math.sin(query.life_time * 0.6) * 2.5",
  "math.sin(query.life_time * 0.4) * 4.5",
  0
] }
```

Breathing frequencies typically 0.8-2.5 (slower for larger animals). Amplitudes small (0.1-0.3 for position, 2-5° for head sway).

### §10.3. Activation threshold rule

**Standing rule (Lesson #204)**: All walk animations must activate at FULL amplitude when ANY movement occurs, not scale linearly with move_speed. Use:
```
* math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)
```

This ramps from 0 to 1.0 over the speed range [0, 0.05], so any movement above 0.05 produces full-amplitude animation. Below 0.05, the mob is effectively stopped and idle animation runs instead.

Trigger conditions in `entity.animate` follow the same pattern:
```json
{"ar_walk": "math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"},
{"ar_idle": "1.0 - math.clamp(query.modified_move_speed * 20.0, 0.0, 1.0)"}
```

Walk and idle are mutually exclusive with no overlap zone.

---

## §11. Build pipeline

### §11.1. Standard workspace layout

```
/_build/v1_3_35_rp07/                # Active build workspace
  manifest.json
  pack_icon.png
  animations/        # ar_*.animation.json files (custom)
  entity/            # *.entity.json files (client_entity)
  models/entity/     # *.geo.json files
  render_controllers/
  textures/

/_research/v1_3_35_jem_methodology/   # Patch application scripts
  patch{N}_apply.py                  # Python script for each iteration

/_uploads_v{N}/                       # Witness screenshots from session N
/_deliverables/                       # Shipped .mcpack files + READMEs
```

### §11.2. Patch script structure

Every patch is a Python script following this template:
```python
#!/usr/bin/env python3
"""Patch {N} — {brief description}"""
import json, os
from pathlib import Path

BUILD = Path("/home/claude/_build/{version}")
GEO_DIR = BUILD / "models" / "entity"
ENT_DIR = BUILD / "entity"
ANIM_DIR = BUILD / "animations"

def load(p): ...
def save(p, data): ...
def find_bone(geo, name): ...

# One function per fix
def fix_{mob_name}(): ...

def main():
    fix_dolphin()
    fix_turtle()
    # ... etc

if __name__ == "__main__":
    main()
```

Scripts are **idempotent where possible** (running twice produces the same result). For non-idempotent operations (like UV flips that are self-inverse), document this clearly.

### §11.3. JSON validation gate

Before packaging:
1. Walk every `.json` file in the build directory
2. Attempt to parse with `json.load`
3. Report any failures
4. ABORT package build if any file fails to parse

This catches schema errors, missing commas, etc. before they reach the witness.

### §11.4. mcpack packaging

```bash
cd /_build/{version}/ && \
zip -r -q -X /_deliverables/{name}.mcpack . -x "*.bak"
md5sum /_deliverables/{name}.mcpack > MD5SUMS.txt
```

Use `-X` to exclude extra attributes (cleaner archives). The `*.bak` exclusion catches any backup files left during development.

---

## §12. Quality gate before shipping

For every patch:
1. **JSON validation**: all `.json` files parse cleanly
2. **Bone reference validation**: every bone referenced in animations/entity files exists in the geo
3. **Format version validation**: all `format_version` fields match the locked table in FOUNDATION
4. **Manifest version uniformity**: all 16 packs have the same `[major, minor, patch]` version
5. **MD5 documentation**: every shipped `.mcpack` gets an MD5 in `MD5SUMS.txt`
6. **README documentation**: every shipped patch has a `PATCH{N}-README.md` describing changes
7. **present_files call**: shipped files are presented via the present_files tool

**The status of every ship is "shipped, awaiting witness verification" until the witness confirms visual correctness in-game.** Static checks rule things OUT but cannot rule things IN. Only the witness rules things IN.

---

## §13. Lessons library — applicable to JEM conversion

The full lessons library is in FOUNDATION-v3. JEM-conversion-specific lessons:

- **#77**: JSON-parse success ≠ visual correctness. Witness ground truth supersedes static analysis.
- **#156**: Patrix LabPBR → Bedrock MERS conversion formula.
- **#170**: Use `system.runJob` generators in scripts for tick-budget management.
- **#171**: Use `dimension.getBlocks` with native filter rather than per-block loops.
- **#175**: 0.01 inflate rule for zero-axis cubes (0.05 for chicken legs).
- **#196**: Vanilla `quadruped.walk` animation silently fails when custom bone names don't match. Symptom: "sliding without leg movement."
- **#197**: Diagonal leg pairing for natural walk gait.
- **#198**: Body-rotation inverse-math for child pivot computation.
- **#199**: Child bone rotations compound with parent — subtract parent rotation when authoring child.
- **#200**: For Y-flips of cubes, per-cube `rotation: [0, 0, 180]` with centroid pivot is more reliable than sub-bone rotation OR UV manipulation.
- **#201**: Re-parenting attached decorative cubes to the same bone as the moving parts (e.g., parrot wings).
- **#202**: Vanilla MC ocelot scale is smaller than cat scale; compensate via geometry scaling.
- **#203**: Animation amplitude scaling by `query.modified_move_speed` causes invisible animations at slow speeds. Use `math.clamp(move_speed * 20, 0, 1)` instead.
- **#204**: When witness reports symptom across iterations of UV-only manipulation, the issue is geometric, not textural — apply per-cube rotation.
- **#205**: Bone pivot must be at the JOINT, not the cube centroid, for look-at and rotation animations to behave naturally.
- **#206**: Mob-anatomical-frame direction language: "back" means toward mob's rear, "forward" means toward mob's head — not world-frame.

---

## §14. Acknowledgments

This methodology was developed through extensive collaboration between:
- **Abs0lum** — project author, witness-tester on real hardware, source of all visual feedback
- **FreshLX** — original creator of the Patrix mod, who reviewed the methodology and granted permission for the AbsolutRealism conversion project
- **Claude (Anthropic)** — implementation partner, technical documentation, code authoring

The witness-test iteration process described here is the core methodology. Without on-hardware visual feedback, no amount of static analysis can produce correct mob conversions. The collaboration between author and implementer — both treating the witness data as the ground truth — is what made this work.

---

*End of JEM-to-Bedrock Conversion Standard. See companion documents:*
- *FOUNDATION-v3.md — project identity and full lessons library*
- *ARCHITECTURE-v3.md — technical schema and system architecture*
- *HISTORY-v3.md — release chronicle from v1.0.0 through v1.3.35 patch 8*
- *CURRENT-STATE-v1_3_35-patch8.md — current ship status*
- *OPERATING-MANUAL-v3.md — Claude operating principles for this project*
