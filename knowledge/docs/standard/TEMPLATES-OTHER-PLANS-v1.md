# STANDARD RIG TEMPLATES — the other body plans v1 · Phase 1, check-in 2

2026-10-01 · naming language = TEMPLATE-BIRD §1 (his T1, ALL mobs): English snake_case, `_l` / `_r` = the mob's own side (left = +X in the file), numbers outward from the body, **joints** (no cubes, animated) vs **pieces** (cubes, not animated), `_rest` helpers, **bridge** bones only where an engine animation needs a fixed name. S2 = (a). His rulings carried: T4 (split drawn-in parts, empty bones where unmodelled), the "one step past Patrix" principle (T5 / Q1: real joints where the animal has them), Patrix animation quality as the bar. Reference rigs = his R1 / R2 approvals.

Notation: `a → b` = b is a child of a; `[req]` required, `[opt]` optional; `×n` repeated segments numbered 1..n outward.

---

## Insect, flying — reference: Patrix bee (35 bones)
```
body → thorax [req] → head → antenna_l / antenna_r (each antenna_joint → antenna piece) [req where modelled]
     → abdomen_joint → abdomen → stinger [opt]
     → wing_root_l → wing_l (forewing) [req] ; wing_root_hind_l → wing_hind_l [opt: 4-winged insects]
     → leg pairs front / mid / hind: hip_<pair>_l → femur → knee → tibia → ankle → foot [3 pieces per leg]
```
Wings are thin plates on ONE joint each (his F1: insects keep their own wing articulation, no bird hinge). Butterflies / moths: forewing + hindwing per side. Bee legs today = 1 piece → split into femur / tibia / foot (one step past Patrix).

## Insect, walking — interim reference: AnF centipede (60 bones)
```
body → head → antenna_l / _r, mandible_l / _r [opt]
     → segment_1 → segment_2 → … segment_n   (each segment on its own joint segment_joint_k: the body waves)
     → per segment: leg_k_l / leg_k_r (hip → femur → knee → tibia) [2 pieces]
     → abdomen / tail [opt]
```
Ants, beetles, termites: 3 segments (head / thorax / abdomen) + 3 leg pairs; centipedes / millipedes: n segments.

## Arachnid — reference: Patrix spider (118 bones)
```
body → cephalothorax → head (eyes painted) → chelicera_l / _r (fangs) → pedipalp_l / _r [opt]
     → abdomen_joint → abdomen
     → leg_1..4_l / _r: hip → femur → knee → tibia → ankle → tarsus [3 pieces per leg, Patrix already segments them]
```
Scorpions: + tail_joint_1..5 → tail_1..5 → stinger, pincers on pedipalps (claw_l / claw_r with claw_jaw joint).

## Fish — reference: Patrix cod / salmon (19 / 18 bones)
```
body_front → head → jaw_lower [opt]
           → fin_pectoral_l / _r (joint + piece)
           → body_joint → body_rear → tail_joint → tail → tail_fin
           → fin_dorsal, fin_pelvic_l / _r, fin_anal [opt]
```
The swim wave runs head → body_joint → tail_joint (2 bends minimum; long fish (eels, sharks) add body_joint_2..n). Bridges `pw_render_yaw / pw_render_roll` (Patrix fish) stay as bridges.

## Snake — interim reference: AnF snake (17 bones) skeleton + WS anaconda animations
```
body_1 → neck → head → jaw_lower → tongue [opt]
body_1 → body_joint_2 → body_2 → … → tail_joint_n → tail_n   (≥ 8 segments; the AnF boa already has 8)
```
Slither = a travelling sine down the chain (phase per segment). The WS anaconda's motion is ported onto this chain.

## Lizard / crocodilian — reference: Patrix axolotl (25 bones)
```
body (chest) → spine_mid → hips
chest → neck_base → neck → head → jaw_lower [req for crocodilians], gills_l / _r / top (axolotl) [opt]
chest → shoulder_l → upper_arm_l → elbow_l → forearm_l → wrist_l → front_foot_l   (sprawling: legs out sideways)
hips  → hip_l → thigh_l → knee_l → shin_l → ankle_l → hind_foot_l
hips  → tail_joint_1..n → tail_1..n (≥ 3)
```
Legs splay sideways (elbow / knee bend in the horizontal plane) — the difference from the quadruped template.

## Amphibian — reference: Patrix frog (37 bones)
```
body → head → jaw_lower / tongue [opt], eye_l / eye_r [opt]
     → throat (croak sac) [opt]
     → shoulder_l → upper_arm_l → elbow_l → forearm_l → hand_l
     → hip_l → thigh_l → knee_l → shin_l → ankle_l → foot_l   (the long jumping hind leg: 3 pieces)
```
Salamanders / newts use the lizard template.

## Cetacean — reference: Patrix dolphin (16 bones)
```
body_front → head → jaw_lower [opt]
           → flipper_l / _r (joint + piece) ; fin_dorsal
           → body_joint → body_rear → tail_joint → tail → fluke
```
Up-and-down swim (tail fluke beats vertically, unlike fish).

## Pinniped — interim reference: Naturalist walrus (15 bones)
```
body_front → neck → head → tusk_l / _r [opt], whisker pad [opt]
           → fore_flipper_l / _r : shoulder → upper → elbow → flipper
           → body_joint → body_rear → hind_flipper_l / _r : hip → flipper ; tail [opt]
```
Land: humping crawl through body_joint; water: hind flippers sweep.

## Cephalopod — reference: Patrix squid (18 bones)
```
mantle (body) → head → eye_l / _r [opt]
              → arm_1..8 (each arm_joint_k_1 → arm_k_1 → arm_joint_k_2 → arm_k_2 …, ≥ 2 segments) ; tentacle_l / _r (squid: 2 long ones) [opt]
              → fin_l / _r (squid mantle fins) [opt]
```
Patrix squid tentacles are 1 segment with a rest helper → gain a second segment (curl).

## Turtle — reference: Patrix turtle (20 bones)
```
shell (body) → neck_base → neck → head → jaw_lower [opt]
             → flipper / leg front_l / _r : shoulder → upper → elbow → foot
             → hind_l / _r : hip → thigh → knee → foot
             → tail [opt]
```
Sea turtles: front flippers long (2 pieces); tortoises: stubby legs (2 pieces).

## Crustacean — interim reference: AnF lobster (29 bones)
```
body (carapace) → head → antenna_l / _r (2 segments), eye stalks [opt]
                → claw_arm_l → claw_l → claw_jaw_l (the moving pincer half)
                → leg_1..4_l / _r : hip → femur → knee → tibia
                → tail_joint_1..n → tail_1..n → tail_fan (lobster / shrimp) [opt]
```
Crabs: no tail chain; walk sideways.

## Jellyfish — interim reference: Naturalist jellyfish (17 bones)
```
bell (body) → bell_skirt (pulse joint) → tentacle_1..n (each ≥ 2 segments) ; oral_arm_1..4 [opt]
```

## Ape / monkey (biped_ape) — interim reference: WS howler monkey (23 bones)
```
hips → spine_mid → chest → neck → head → jaw_lower [opt]
chest → shoulder_l → upper_arm_l → elbow_l → forearm_l → wrist_l → hand_l
hips  → hip_l → thigh_l → knee_l → shin_l → ankle_l → foot_l
hips  → tail_joint_1..n → tail_1..n [opt: monkeys]
```
Walks on all fours or upright (knuckle-walk pose = animation, not structure).

## Macropod — interim reference: Naturalist kangaroo (26 bones)
```
hips → spine_mid → chest → neck → head → ear_l / _r
chest → shoulder_l → upper_arm_l → elbow_l → forearm_l → paw_l
hips  → hip_l → thigh_l → knee_l → shin_l → ankle_l → foot_l   (long foot; the hop)
hips  → tail_joint_1..3 → tail_1..3 ; pouch [opt]
```

## Bat + phantom
Use the BIRD flight template (his F1): shoulder → inner → elbow → wrist (true hinge) → membrane "primaries" (the finger spans), the folded wing, legs. Membranes let light through (MERS subsurface already set for wings on these plans).

## Humanoid + fantasy (my recommendation, his H1 deferral)
Their rigs are Patrix / vanilla already (the standard itself). They get the naming language (bridges kept for the engine's player-style animations and item points) and animation sharing only — no re-rig. The phantom moves to the bird flight template (F1).
