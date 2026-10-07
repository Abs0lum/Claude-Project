# STANDARD RIG TEMPLATE — QUADRUPED v1 · Phase 1, check-in 2 (four-legged)

2026-10-01 · his rulings: **Q1 = (b)** real leg joints, one step past Patrix (09:52, "if it doesn't seem difficult … pursue b"); **Q2** the empty placeholder `pw_*` joint bones are removed (0 references anywhere outside 27 RP-07 model files — census D-C367). Naming language = TEMPLATE-BIRD §1 (his T1: ALL mobs). S2 = (a): bones / pieces / joints / names / pivots standard, detail cubes free.

Reference look + motion: the Patrix cow (`geometry.pw_cow`) and its walk; size checks polar bear / wolf / horse (his R1). Reference leg STRUCTURE (Patrix has none — 17 of 18 Patrix quadrupeds have one-piece legs): the ported rigs that already bend — YSav African wild dog (front 3 pieces, hind 4), AnF hyena (hind thigh → shin → foot).

## 1 · The tree

```
root                                   pivot 0,0,0
└─ body                                piece — torso (Patrix body_cube)                   [required]
   ├─ spine_mid                        joint — bend between chest and hips              [optional: long bodies — weasels, crocodilian-like mammals]
   ├─ neck_base                        joint                                            [required]
   │  └─ neck                          piece                                            [required when the model has one]
   │     └─ head                       joint + piece
   │        ├─ snout                   piece (muzzle / nose)                            [required]
   │        │  └─ jaw_lower            joint + piece — open mouth                        [optional]
   │        ├─ ear_l / ear_r           joint + piece                                    [required where modelled]
   │        ├─ horn_l / horn_r         piece (antler_l / antler_r, tusk_l / tusk_r)     [optional]
   │        └─ mane_top                piece                                            [optional]
   ├─ shoulder_l                       joint — top of the front leg (Patrix leg1's pivot)
   │  └─ upper_arm_l                   piece (≈ 43 % of the leg)
   │     └─ elbow_l                    joint
   │        └─ forearm_l               piece (≈ 43 %)
   │           └─ wrist_l              joint (knee of a horse's front leg)
   │              └─ front_foot_l      piece — hoof / paw (≈ 14 %)
   ├─ hip_l                            joint — top of the hind leg (Patrix leg3's pivot)
   │  └─ thigh_l                       piece (≈ 35 %)
   │     └─ knee_l                     joint (stifle)
   │        └─ shin_l                  piece (≈ 35 %)
   │           └─ hock_l               joint (ankle)
   │              └─ hind_foot_l       piece — metatarsus + hoof / paw (≈ 30 %)
   ├─ tail_base                        joint
   │  └─ tail_1 … tail_n               pieces, each on its own joint tail_joint_2..n      [≥ 1]
   ├─ (mirror _r)
   └─ detail pieces on body: udder, mane, hump, saddle points (unchanged)
bridge bones (outside the tree, only where an engine animation / item point needs them): head, body, leg0, leg1, leg2, leg3
   (vanilla order: leg0 = front RIGHT, leg1 = front LEFT, leg2 = hind RIGHT, leg3 = hind LEFT — verified on geometry.pw_cow pivots)
```

Each one-piece Patrix leg is cut along its length at the ratios above (front 43 / 43 / 14, hind 35 / 35 / 30, from the wild dog's measured pieces and real anatomy); the box UV is turned into per-face UV first, so every texel stays exactly where it is on the screen — the Phase 2 gate renders before / after and compares pixels.

## 2 · Joint and pivot rules

1. Every joint's pivot sits on the anatomical joint: the shoulder / hip at the top of the leg (Patrix's leg pivot), the elbow / knee at the cut between upper and lower piece, the wrist / hock at the cut above the foot.
2. Pieces touch across every joint (no floating pieces, no gaps through the walk — the WING-CONTACT idea applied to legs).
3. Bend directions follow anatomy: the elbow and front wrist fold backward-up (toward the tail) … NOTE the horse's front "knee" is the wrist; the hind knee folds forward, the hock backward.
4. Animations rotate joints, never pieces. Patrix's walk keeps its shoulder / hip swing exactly; the new joints add the bend (elbow / wrist / knee / hock flex in the swing phase, straight in the stance phase).

## 3 · Where the four-legged roster stands (leg pieces per leg, from the rig census)

| Source | 1 piece | 2 | 3 | 4 |
|---|---|---|---|---|
| Patrix | 17 | 1 (rabbit) | – | – |
| Ours (Naturalist) | 31 | 3 | – | – |
| Ported | 63 | 35 | 7 (AnF) | 41 (YSav) |

Ported multi-piece legs are mapped onto the template, not rebuilt: e.g. the wild dog's `leg3 → leg3a → leg3b → leg3c → leg3d` becomes `hip_l → thigh_l → knee_l → shin_l → hock_l → hind_foot_l` (its extra toe piece stays a detail piece under `hind_foot_l`). Pivots that sit far from their joint (the wild dog's `leg0a` pivot is at ground height) are moved onto the joint in Phase 2 — the bind pose is kept identical, only the rotation centre moves.

## 4 · Removed in the conversion (his Q2)

`pw_neck_base, pw_spine_mid, pw_shoulder_l/r, pw_elbow_l/r, pw_hip_l/r, pw_knee_l/r, pw_ankle_fl/fr/rl/rr` in 27 RP-07 models (cubeless leaves, all at the leg top, referenced nowhere). Their real counterparts are the new joints above.
