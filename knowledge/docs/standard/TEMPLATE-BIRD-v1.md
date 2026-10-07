# STANDARD RIG TEMPLATE — BIRD (flight) v1.1 · Phase 1, check-in 2

**v1.1 (his 03:35 / 03:44 rulings):** T1 naming language = ALL mobs · T2 two-wing system for every flier · T3 = (b) stiff wings split into inner + **3 primaries** · T4 split drawn-in beak / neck / foot, empty bones where unmodelled · **T5 = (b) one step past Patrix: the elbow MOVES and each primary gets its OWN joint** (`primary_base_l_1..3`, each a child of the previous: the tip curls and spreads through the flap) · F2 flight classes (§7).

2026-10-01 · source rig: the Patrix parrot `geometry.pw_parrot` (RP-07 1.4.39, 45 bones), whose flight you judged "visually perfect" (FA-1, D-C309/310). Laws carried in: **TRUE HINGE** (`tools/wing_hinge.py`: an outer wing piece turns only about the line it shares with the inner piece) and the **WING-CONTACT LAW** (your words: "the edges of the wing pieces stay in contact with each other as they flap — true of all flying mobs with similar wings"). Scope (your F1): every bird + **phantom + bat**; ender dragon later (maybe); allay / vex / insects keep their own wings.

S2 = (a): the standard fixes the **bones, pieces, joints, parenting, pivots and names**; detail cubes inside a piece may differ per mob. Fallback (b), identical cube counts, only if animations or orientation run into trouble.

---

## 1 · The naming language (all body plans, not only birds)

| Rule | Example |
|---|---|
| lower_snake_case, English | `wing_inner_l`, never `ala0_1`, `bone10`, `leftWingFly2` |
| side suffix `_l` / `_r` = the **mob's own** left / right (left = +X in model space) | `shoulder_l` |
| numbers count **outward from the body**, starting at 1 | `primary_l_1` (nearest the wrist) … `primary_l_3` |
| **joint** = a bone with no cubes, named by the anatomical joint; animations rotate joints | `shoulder_l`, `elbow_l`, `wrist_l`, `hip_l`, `ankle_l`, `neck_base` |
| **piece** = a bone carrying cubes, named by the body part; a piece is normally NOT animated, its joint is | `wing_inner_l`, `thigh_l`, `foot_l` |
| **rest** helper = a cubeless child of a joint that holds the bind orientation, so the joint's own axes stay clean for animation | `shoulder_l_rest` (Patrix's `left_wing_fly_rot`) |
| **bridge** = a bone kept ONLY because the engine's own animations / item points address it by a fixed name; never part of the tree | `head`, `left_wing`, `right_wing`, `left_leg`, `tail` (the parrot's JEM-name bones) |

## 2 · The bird tree

```
root                                   pivot 0,0,0 (feet on the ground plane)
└─ body                                piece — torso
   ├─ neck_base                        joint — where the neck leaves the body            [required]
   │  └─ neck                          piece                                             [optional: long-necked birds]
   │     └─ head                       joint + piece — skull
   │        ├─ beak                    piece (jaw_lower optional for open-beak calls)    [required]
   │        └─ crest                   piece — comb / crest / plume / wattle             [optional]
   ├─ shoulder_l                       joint — FLIGHT wing root (flap axis)              [required for fliers]
   │  └─ shoulder_l_rest               rest helper (bind orientation)
   │     ├─ wing_inner_l               piece — arm / secondaries (≈ 47 % of the span)
   │     └─ elbow_l                    joint — fold of the wing
   │        └─ wrist_l                 joint — the TRUE HINGE: pivot ON the join line between inner and outer,
   │           │                               turns only about that line's own axis
   │           └─ primary_base_l_1     joint (v1.1, T5 b) — spreads / curls primary 1
   │              ├─ primary_l_1       piece — outer wing (the three primaries ≈ 53 % of the span)
   │              └─ primary_base_l_2  joint — chained on primary 1's base
   │                 ├─ primary_l_2    piece
   │                 └─ primary_base_l_3  joint
   │                    └─ primary_l_3 piece                                          [all 3 required, T3 b]
   ├─ wing_fold_l                      joint — the FOLDED wing shown at rest / walking    [required]
   │  └─ wing_fold_l_rest              rest helper
   │     └─ wing_fold_piece_l          piece
   ├─ hip_l                            joint
   │  └─ thigh_l                       piece (leg)                                      [required]
   │     └─ ankle_l                    joint
   │        └─ foot_l                  piece — foot / talons                            [required]
   ├─ tail_base                        joint
   │  └─ tail                          piece — tail fan (tail_fan_1..n optional)        [required]
   └─ (mirror: shoulder_r … foot_r)
bridge bones (outside the tree, kept only if an engine animation needs them): head, left_wing, right_wing, left_leg, right_leg, tail
```

**Two wing systems, as Patrix built it:** a FLIGHT wing (shoulder → inner + hinge → primaries) shown while flying, and a FOLDED wing shown on the ground — the animation switches which one draws. This is what makes the parrot both fold neatly and flap with depth; the template keeps it.

## 3 · Parrot → standard (the reference mapping — a pure rename, poses unchanged)

| Patrix parrot bone | Standard | Kind |
|---|---|---|
| `body` | `body` | piece |
| `head2` | `head` | joint + piece |
| `beak` | `beak` | piece |
| `feathers` | `crest` | piece |
| `left_wing_fly` | `shoulder_l` | joint |
| `left_wing_fly_rot` | `shoulder_l_rest` | rest |
| `bone2` (3 × 5.4 × 1.1) | `wing_inner_l` | piece |
| `left_wing_fly2` | `elbow_l` | joint |
| `left_wing_fly2_hinge` | `wrist_l` | joint — true hinge |
| `bone10` / `bone11` / `bone12` (3 × 6 / 4.8 / 6) | `primary_l_1` / `_2` / `_3` | pieces |
| `left_wing2` → `left_wing_rotation` → `left_wing_rotation2` → `bone5` | `wing_fold_l` → `wing_fold_l_rest` → (`_rest2`) → `wing_fold_piece_l` | joint / rest / piece |
| `left_leg2` | `hip_l` + `thigh_l` (one bone today: pivot = hip, carries the leg cube) | joint + piece |
| `left_foot2` | `ankle_l` + `foot_l` (likewise) | joint + piece |
| `tail2` → `bone7` | `tail_base` → `tail` | joint → piece |
| `head`, `left_wing`, `right_wing`, `left_leg`, `left_foot`, `right_leg`, `right_foot`, `tail`, `*_jem`, `Created_by_FreshLX_for_Patrix` | bridge bones (JEM / vanilla names) — kept as bridges; the leg / foot bridge cubes are checked in Phase 2 (they may be hidden duplicates) | bridge |

The parrot needs NO cube change — only names. Phase 2's gate proves it: the renamed rig must render pixel-identical in every animation frame.

## 4 · Joint and pivot rules

1. A joint's pivot sits ON the anatomical joint: `shoulder` where the wing meets the body, `wrist` ON the shared edge of the inner and outer pieces (true hinge), `hip` at the top of the leg, `ankle` at the foot.
2. A piece's inner edge touches its joint's pivot (no floating pieces: the WING-CONTACT LAW as a bind-pose rule).
3. WING-CONTACT through motion: measured with `tools/wing_contact.py` over a full flap at every flight scale — the gap between neighbouring wing pieces stays ≈ 0 px.
4. Rotation order and sign follow the engine law L-ROT-DIR (witnessed on the probe, P0); animations rotate JOINTS, not pieces.

## 5 · Where the 150 winged / bird-like mobs stand today (`tools/standard_bird_map.py` → `BIRD-RIG-MAP.json`)

| Class | Count | What Phase 2 does |
|---|---|---|
| TEMPLATE-READY — wing already ≥ 2 joints and ≥ 2 pieces (parrot, bat, phantom, 26 AnF birds with 4-segment wings, WA blue jay / dove / duck / eagle / toucan, YSav black eagle + ostrich, sf_nba eagle + vulture) | 38 | rename + re-parent onto the tree; check the hinge is TRUE and the contact law holds |
| SPLIT-NEEDED — one stiff wing plate | 109 | cut each wing plate at ≈ 47 / 53 (the parrot's inner / outer ratio) into `wing_inner` + `primary_1`, insert `shoulder` / `elbow` / `wrist`, re-map the UVs so the texture stays exactly where it is |
| NO-WINGS-FOUND — model has no wing bones (AnF ostrich, YTri cassowary, Naturalist kiwi) | 3 | ground-bird tree only (no flight wing) |

Other gaps: 108 have no `neck` bone, 104 no separate `foot`, 46 no `beak` bone, 18 no `tail`. Where a piece is missing as a bone but drawn as cubes inside another piece (a beak modelled inside the head), Phase 2 splits those cubes into their own piece; where it is not modelled at all, the bone is created empty (animations can still address it).

## 6 · How the Patrix parrot actually moves its flight wing (from its own Molang; his 03:44 question)

Phase p = q.life_time × 20 × 2π / 7 → **one flap = 7 ticks = 0.35 s**; m = q.modified_move_speed (0 hovering … 1 full speed).

| Joint | Motion | Range |
|---|---|---|
| shoulder — flap (ry) | −50 · sin p | ±50° |
| shoulder — sweep (rz) | −(30 − 15m) · sin(p − m) | ±30° hovering, ±15° at speed |
| shoulder — **pitch / twist** (rx) | 40(1 − m) + 20 · cos p | ±20°, a quarter cycle out of step with the flap → the wing changes its angle of attack through the stroke |
| wrist hinge (ry) | 10 + 70 · cos p | −60° … +80° (folds on the upstroke, opens on the downstroke) |
| elbow (rx) | −5 − (7 + 10 · cos(p + 36°)) · m | ±10° in forward flight, still when hovering |
| shoulder rest helper | scale y 1.2, z 1.5 | constant (an enlargement, not a motion) |

The standard flight animation keeps these motions (Patrix quality is the bar) and adds the T5 (b) primary joints on top.

## 7 · Flight classes (his F2, 03:44 GO)

| Class | Mobs |
|---|---|
| FLIGHT (standard flight wing + animation) | every bird with a fly animation + barn owl, owl, pelican ×4, swan, toucan ×2, duck, goose, flamingo, secretary bird; phantom + bat |
| FLUTTER (chicken-style: fast bee-like flap, brief hang time with no lift, then it gives up and drops) | chicken, turkey, peafowl, kakapo |
| NO FLIGHT (wings stay folded) | ostrich ×4, emu, cassowary, kiwi, emperor penguin |
| not yet | baby African black eagle (does not fly as a baby) |
| own Patrix flight | parrot (the reference itself) |
