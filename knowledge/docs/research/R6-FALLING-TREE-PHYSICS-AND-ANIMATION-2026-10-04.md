# R6 — How a felled tree falls, and how to animate it in Bedrock

**Date:** 2026-10-04 · **Round:** 1004b, P0 research · **Workstream:** BIGCANOPY falling tree (`ft:falling_tree`)

- **Trigger:** Abs0lum, 17:38 CT — trees "fall too far — they clip into the earth"; deep research on method, timing, visuals.
- **Status:** research only; nothing built; every recommendation is *proposed, awaiting witness* (P1).
- **Numbers:** Python, energy integral cross-checked by RK4 (20 m rod from 5°: 4.2410 vs 4.2411 s); code in Appendix B.
- **Conventions:** θ = tilt from vertical (0° upright, 90° flat on level ground, >90° = lying downhill). H = tree height (1 block = 1 m). **Leading edge** = fall-side face of the trunk base; **butt** = cut end; **crown** = leafy top. Directions are relative to the fall, never world axes.

---

## 0. Executive summary

- **Model:** a felled tree is a rigid body on its hinge: θ'' = (g/L_eff)·sin θ, L_eff = I_pivot/(M·h_cm). Uniform rod: L_eff = 2H/3 → θ'' = (3g/2H)·sin θ.
- **Real trees:** tapered trunk + crown → L_eff ≈ 0.50–0.57 H (centre of mass 0.34–0.39 H). A **top-heavy** crown raises L_eff, so the tree falls **slower**.
- **Time from a 5° lean to the ground** ≈ 0.88·√H s (broadleaf): 2.2 s (6 m), 2.8 s (10 m), 3.9 s (20 m), 4.8 s (30 m); a rod takes 2.3–5.2 s.
- **Slow start:** 0.5° → 5° takes 1.8–4.3 s (tilt grows like cosh t/τ) — the creaking lean. From 5°, ~87% of the rotation comes in the second half of the fall. Impact: ~55–150°/s, tip 13–34 m/s, tip acceleration 1.5–1.7 g (loose leaves are left behind).
- **Best simple curve:** θ = 2° + 88°·f^3.85 from 2° at rest (f = t/T): 1.2° rms, within 2° extrapolated downhill to 110°. Ease-in-sine (Panda's/EFT) is 10° off, quad (Dynamic Trees) 7°, cubic (Stardew) 4°. **Never ease out into the impact.**
- **The hinge** (~10% of diameter thick, ≥80% wide) steers until the notch faces close — halfway down for a 45° notch, to the ground for ≥70°. Its tearing fibres are the creak.
- **The butt:** a hinge failing before ~48° throws the butt **back** at the feller (hence the "stump shot"); after ~48° a free butt slides **forwards**; at 70.5° the stump carries no weight. Impact kickback needs an obstacle or another tree (documented ~10 ft).
- **Impact:** crown hits first, branches crush, trunk stops. Restitution e lifts the trunk by e² rad at any height: e = 0.15–0.25 → 1.3–3.6° over 0.35–1.0 s, always **up**.
- **No mid-fall snap:** the falling-chimney moment peaks at H/3 (mgH·sin θ/27); a 20 m tree sees ~3 MPa vs 34–65 MPa green-wood strength. Tops and limbs break **at impact**.
- **Mods:** Dynamic Trees — constant angular acceleration 0.1/h_cm °/tick² (4.75 s for a 10-block tree), trunk-edge pivot, segment collision, elasticity 0.25. Panda's / Enhanced Falling Trees (EFT) — 2.5 s ease-in-sine, 10°/1 s bounce, edge pivot; EFT's README admits "some part of it may fall into the ground". Sable-based mods use real rigid bodies.
- **Resting angle = first contact:** θ_rest = 90° − max_i atan2(G_i + s_i − y_p, x_i). With the crown underside (minus crush) counted, flat ground gives **~81–87°**, top propped — not past 90°.
- **Our entity (Appendix A, static read)** explains the clipping: flat grass gives −101° to −129°, tip 2–3 blocks underground. Three one-block errors stack (script pivot a block above the drawn one; ground = block y, not top face; `grass_block` skipped by an `includes("grass")` test), and the 1.05× overshoot and `rest_angle − 4` "bounce" push further **into** the ground.

---

## 1. Physics of a tree felled at the base

### 1.1 The hinged rigid-body model

- **Equation:** treat trunk + crown as one rigid body on a horizontal hinge axis. Gravity's torque is M·g·h_cm·sin θ, so θ'' = (M·g·h_cm/I_pivot)·sin θ = (g/L_eff)·sin θ. Uniform rod: I = MH²/3, h_cm = H/2 → L_eff = 2H/3 → **θ'' = (3g/2H)·sin θ** ([Varieschi & Kamiya](https://arxiv.org/pdf/physics/0210033); [PhysicsLAB](https://www.physicslab.org/Document.aspx?doctype=3&filename=RotaryMotion_RotationalDynamicsPivotingRods.xml)).
- **Speed:** θ'² = (2g/L_eff)(cos θ₀ − cos θ); for a rod (3g/H)(cos θ₀ − cos θ), as Varieschi & Kamiya give from θ₀ = 0.
- **Time:** t = √(L_eff/2g)·∫dθ/√(cos θ₀ − cos θ) — elliptic-type, no elementary closed form; the angular acceleration "is not constant, but changes with the angle of the tree as it falls" ([Physics Forums](https://www.physicsforums.com/threads/time-for-a-tree-to-fall-after-a-45-degree-wedge-cut.455794/)).
- **Divergence:** time grows without bound as θ₀ → 0 — a perfectly balanced tree never falls. The initial lean sets the clock (§1.4).

### 1.2 Real trees: centre of mass and L_eff

| Model (mass split) | h_cm/H | L_eff/H | Time vs rod |
|---|---|---|---|
| Uniform rod | 0.500 | 0.667 | 1.00 |
| Tapered cone trunk, no crown | 0.250 | 0.400 | 0.77 |
| **Broadleaf:** cone 70% + spherical crown 30% at 0.70 H (r 0.18 H) | 0.385 | 0.574 | 0.93 |
| **Conifer:** cone 75% + crown 25% at 0.60 H (r 0.15 H) | 0.338 | 0.496 | 0.86 |
| **Top-heavy:** cone 50% + crown 50% at 0.75 H | 0.500 | 0.675 | 1.01 |
| Point mass at top (limit) | 1.000 | 1.000 | 1.22 |

- The splits are assumptions bracketing real trees; laser-scanned oaks confirm that adding branches makes "the CoG [shift] significantly towards the branches" ([TLS centroid study](https://www.sciencedirect.com/science/article/pii/S2772375526002182)).
- Time ∝ √L_eff: a crown-heavy tree is ~8% slower than the broadleaf model; a light tapered pole is fastest.
- **In-game, compute L_eff from the template voxels:** I = Σmᵢ(uᵢ² + vᵢ²), h_cm = Σmᵢvᵢ/M (log 1.0, leaf ~0.1–0.15, to tune). Dynamic Trees does the same with radius² weights (§3.1).

### 1.3 Time to ground from a 5° lean

| Model \ height | 6 m | 10 m | 15 m | 20 m | 25 m | 30 m |
|---|---|---|---|---|---|---|
| Uniform rod | 2.32 s | 3.00 | 3.67 | 4.24 | 4.74 | 5.19 |
| Tapered cone, no crown | 1.80 | 2.32 | 2.84 | 3.29 | 3.67 | 4.02 |
| **Broadleaf** | **2.15** | **2.78** | **3.41** | **3.93** | **4.40** | **4.82** |
| Conifer | 2.00 | 2.59 | 3.17 | 3.66 | 4.09 | 4.48 |
| Top-heavy | 2.34 | 3.02 | 3.70 | 4.27 | 4.77 | 5.23 |
| Point mass at top | 2.84 | 3.67 | 4.50 | 5.19 | 5.81 | 6.36 |

**Rule of thumb:** T(5°→90°) = c·√H, with c = 0.949 (rod), 0.879 (broadleaf), 0.819 (conifer).

### 1.4 The slow start: sensitivity to the initial lean

| Rod, start angle | 6 m | 10 m | 15 m | 20 m | 25 m | 30 m |
|---|---|---|---|---|---|---|
| 0.5° | 3.79 s | 4.90 | 6.00 | 6.92 | 7.74 | 8.48 |
| 1° | 3.35 | 4.32 | 5.30 | 6.12 | 6.84 | 7.49 |
| 2° | 2.91 | 3.75 | 4.60 | 5.31 | 5.94 | 6.50 |
| 5° | 2.32 | 3.00 | 3.67 | 4.24 | 4.74 | 5.19 |
| 10° | 1.88 | 2.43 | 2.97 | 3.43 | 3.84 | 4.21 |

- **Lean phase alone (0.5° → 5°):** 1.91 / 2.47 / 3.02 / 3.49 / 3.90 / 4.27 s (rod, 6–30 m); 1.77 / 2.29 / 2.80 / 3.24 / 3.62 / 3.97 s (broadleaf).
- **Why slow:** at small angles tilt grows as θ₀·cosh(t/τ), τ = √(L_eff/g) (0.76 s at 10 m, 1.08 s at 20 m broadleaf); each tenfold growth costs ~3τ, and hinge resistance (§1.6) adds to it.
- **Field note:** "90% of incidents happen within 15 seconds of a tree starting to move" ([TCIA Six-Step](https://tcimag.tcia.org/safety/chainsaw-safety-maintenance/the-six-step-felling-plan/)).

### 1.5 The universal fall curve, impact speed and tip acceleration

**One curve fits every tree.** Because θ'' = (g/L_eff)·sin θ, for a fixed start angle the curve θ(t/T) is the same for every size and mass model; only T changes. From 5° at rest:

| t/T | 0 | 0.10 | 0.20 | 0.30 | 0.40 | 0.50 | 0.60 | 0.70 | 0.80 | 0.85 | 0.90 | 0.95 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| θ | 5.0° | 5.3 | 6.4 | 8.3 | 11.3 | 15.8 | 22.4 | 31.9 | 45.4 | 54.1 | 64.3 | 76.2 | 90.0 |

- **How back-loaded:** at half the fall time the tree is only at 15.8°, with ~87% of the rotation still to come. The last 20% of the time covers half the rotation; the last 5% covers 14°. Impact speed is ~3.5× the average speed. (The 2° start used for animation is tabled in §6.2.)

**Impact (from 5°):**

| ω at impact · tip speed | 6 m | 10 m | 15 m | 20 m | 25 m | 30 m |
|---|---|---|---|---|---|---|
| Rod | 127°/s · 13.3 m/s | 98 · 17.1 | 80 · 21.0 | 69 · 24.2 | 62 · 27.1 | 57 · 29.7 |
| Broadleaf | 137 · 14.3 | 106 · 18.5 | 86 · 22.6 | 75 · 26.1 | 67 · 29.2 | 61 · 32.0 |
| Conifer | 147 · 15.4 | 114 · 19.9 | 93 · 24.3 | 80 · 28.1 | 72 · 31.4 | 66 · 34.4 |

- **The tip outruns gravity:** H·θ'' = (gH/L_eff)·sin θ reaches **1.5 g (rod) / 1.74 g (broadleaf)** at horizontal, exceeding g beyond 42° / 35° — "the top end of the stick falls with acceleration greater than 1 g" ([McDonald (1988)](http://kirkmcd.princeton.edu/examples/ph205set2.pdf)).
- **Follow-through:** from ~35–45° loose leaves and snow trail behind the crown and the thin top bends back, then whips forward when the trunk stops.

### 1.6 The hinge (holding wood)

- **Size:** ≥80% of the diameter long, ~10% thick ([Northern Woodlands](https://northernwoodlands.org/articles/article/hinge_hints)); face cut ~1/3 of the diameter deep ([Hand felling](https://en.wikipedia.org/wiki/Hand_felling)). A back-cut step of 2" or more (a "stump shot") is "an anti-kick step that will prevent a tree from jumping back over the stump toward the faller" ([OSHA glossary](https://www.osha.gov/etools/logging/glossary)).
- **How it works:** front fibres "bend and hold the tree to the stump", back fibres "pull and break" first.
- **When it breaks:** "when the faces of the undercut close" — hence openings of ≥70°. A 45° notch "only allows the hinge wood to control the falling of the tree half way to the ground" ([STIHL Pro Line](https://www.stihlproline.ca/en/arborist/tree-felling-and-the-notch); same in [TCIA Six-Step](https://tcimag.tcia.org/safety/chainsaw-safety-maintenance/the-six-step-felling-plan/)). Standards: conventional ≈45° (Z133.1), open face ">70 degrees" (Z133.3) ([TCIA Advanced](https://tcimag.tcia.org/training/arboriculture-best-practices/advanced-felling-techniques/)).
- **After the break:** "the trunk 'jump[s]' a little"; a Humboldt cut lands the tree "butt first" ([Hand felling](https://en.wikipedia.org/wiki/Hand_felling)).
- **Sound:** "the creaking sound you hear comes from the hinge … where the wood fibres are tearing" ([A Sound Effect — Stuart Ankers](https://www.asoundeffect.com/tree-felling-sound-effects/)).
- **In the game:** no notch exists, but the cues are a creak during the slow lean, an optional crack near 45°, then free fall.

### 1.7 Forces at the pivot: which way the butt goes

For a rod released from vertical, the pivot must supply **F_h = ¾·mg·sin θ·(3cos θ − 2)** horizontally and **N = ¼·mg·(3cos θ − 1)²** vertically (derived here from §1.1; positive F_h pushes the butt forwards, in the fall direction).

| θ | 10° | 20° | 30° | 40° | **48.2°** | 60° | **70.5°** | 80° | 90° |
|---|---|---|---|---|---|---|---|---|---|
| F_h / mg | +0.124 | +0.210 | +0.224 | +0.144 | **0** | −0.325 | −0.707 | −1.092 | −1.500 |
| N / mg | 0.955 | 0.827 | 0.638 | 0.421 | 0.250 | 0.063 | **0** | 0.057 | 0.250 |

- **Before ~48°** the hinge pushes the butt forwards; if it fails early (barber chair, thin hinge) the butt kicks **back** towards the feller — what the stump shot and the 45° escape route guard against.
- **After ~48°** the hinge holds the butt back; a free butt slides **forwards** off the stump (matches "jump a little" and Humboldt "butt first"). At **70.5°** the stump carries no weight.
- **Kickback at impact** needs an obstacle: "Kick–Backs usually occur when the falling tree strikes another standing tree"; one case "kicked back about 10 feet off its stump" ([Oregon Loggers](https://cdn.ymaws.com/oregonloggers.org/resource/collection/5D1E637C-6103-4F54-AE84-6E91EF21BB17/Hazard_Alert_Minimize_Falling_Trees.pdf)). Tops and limbs "ricochet backwards"; danger zone twice the tree height; escape at 45° opposite the fall ([WorkSafe NZ](https://www.worksafe.govt.nz/topic-and-industry/forestry/safe-practice-for-forestry-and-harvesting-operations/part-e-mobile-plant-and-harvesting/21-0-managing-the-risks-manual-tree-felling/); [UGA](https://fieldreport.caes.uga.edu/publications/C1243/chainsaw-safety-preventing-common-tree-felling-accidents/)).
- **In the game:** no kickback by default; the butt may slide forwards off the stump while settling. Kickback only when the trunk lands across an obstacle nearer than its centre of mass (§5.5).

### 1.8 Impact, bounce and settle

- **On open ground:** the crown touches first whenever it sticks out below the trunk line by more than the stump height; limbs bend and snap ("Branches and treetops can break out of a falling tree" — [UAF](https://www.uaf.edu/ces/publications/database/energy/how-to-tree-cutting.php)). The trunk rests on the crushed crown, often top-propped; the butt stays on the stump or slides forwards (§1.7). A small rebound and a longer branch wobble follow (crush ~0.1–0.2 s is an estimate).
- **Rebound model:** if the trunk leaves the ground with a fraction e of its impact angular speed (restitution), then with deceleration g/L_eff and ω² ≈ 2g·cos θ₀/L_eff, the **lift is e²·cos θ₀ rad — independent of height and mass model**. Up-and-down time = 2e·√(2·L_eff·cos θ₀/g).

| e | Rebound | Up + down (10 / 20 / 30 m rod) |
|---|---|---|
| 0.10 | 0.57° | 0.23 / 0.33 / 0.40 s |
| 0.15 | 1.28° | 0.35 / 0.49 / 0.60 s |
| **0.20** | **2.28°** | **0.47 / 0.66 / 0.81 s** |
| 0.25 | 3.57° | 0.58 / 0.82 / 1.01 s |

- **Comparison:** Dynamic Trees uses e = 0.25. Panda's / EFT use a fixed 10° half-sine over 1 s — ~3× the e = 0.25 lift. A second bounce is e² of the first (4% at e = 0.2), i.e. invisible.
- **Recommended:** e ≈ 0.15–0.2 → 1.3–2.3° lift over 0.35–0.65 s, scaled with √H.

### 1.9 What decides the fall direction

- **Lean, load and wind:** lean "can be forward or backward, or left or right"; load is "the collective biomass of the tree, as relates to any lean" ([TCIA Six-Step](https://tcimag.tcia.org/safety/chainsaw-safety-maintenance/the-six-step-felling-plan/)). The hinge steers only within limits: avoid side lean above "10% of the tree height"; front lean above 5% raises barber-chair risk ([TCIA Advanced](https://tcimag.tcia.org/training/arboriculture-best-practices/advanced-felling-techniques/)). "Never fell a tree into or against the wind" ([UAF](https://www.uaf.edu/ces/publications/database/energy/how-to-tree-cutting.php)).
- **The crown offset is a built-in lean:** a centre-of-mass offset δ acts like θ₀ ≈ atan(δ/h_cm) (0.3 m at h_cm 4 m → 4.3°), so a lopsided tree starts sooner and falls toward its heavy side — supporting Abs0lum's rule ("on flat ground the tree falls toward its heavy side"), also used by *Physical Falling Trees* (§3.5), and giving each tree a physical start angle (§6.2).

### 1.10 Barber chair

- **What it is:** a "vertical split of a tree during the falling procedure" ([OSHA](https://www.osha.gov/etools/logging/glossary)) — "The bottom of the tree goes up and the top comes down—like a barber's chair", often from "heavy, front-leaning trees" ([UGA](https://fieldreport.caes.uga.edu/publications/C1243/chainsaw-safety-preventing-common-tree-felling-accidents/)).
- **Recommendation:** a cutting failure, not part of a normal fall — **do not model it**; it would read as a glitch.

---

## 2. The falling-chimney effect: does a falling trunk snap?

- **Mechanics:** bending torque in a falling rod is **τ(x) = mg·x·(l − x)²·sin θ/(4l²)**; "Empirically, most chimneys break near x = 1/3" ([McDonald (1988)](http://kirkmcd.princeton.edu/examples/ph205set2.pdf)). Varieschi & Kamiya: maximum "at exactly one third of the height H"; **leading edge in tension**; shear peaks near the base ([arXiv physics/0210033](https://arxiv.org/pdf/physics/0210033); [Falling Chimney page](https://gvarieschi.lmu.build/chimney/chimney.html)).
- **Toy towers** break at r/H ≈ 0.5 at small angles, ≈ 0.40 at 30–35°; a 24-block tower at r/H ≈ 0.354, "around 20°–25°" ([Toy Blocks and Rotational Physics](https://arxiv.org/pdf/physics/0402119)).
- **Why trees don't:** τ_max = mgH·sin θ/27; mortar has almost no tensile strength, wood is strong in bending. A 20 m tree (cone trunk 0.45 m at the base, ~800 kg/m³ green, 30% crown → ~1.2 t) sees ≤ 8.8 kN·m at ~0.30 m diameter → **≈3.3 MPa**. Green modulus of rupture ([USDA Wood Handbook, Table 4-3a](https://www.fpl.fs.usda.gov/documnts/fplgtr/fplgtr113/ch04.pdf)): Douglas-fir 53 MPa · white oak 57 · red oak 57 · sugar maple 65 · paper birch 44 · white pine 34 · Sitka spruce 34 → a **10–20× margin**.
- **What breaks:** tops and limbs at impact or on other trees ("Tree-to-tree contact can also snap off branches or tops", [WorkSafe NZ](https://www.worksafe.govt.nz/topic-and-industry/forestry/safe-practice-for-forestry-and-harvesting-operations/part-e-mobile-plant-and-harvesting/21-0-managing-the-risks-manual-tree-felling/)); rotten trunks and snags may fail mid-fall (inference, unmeasured).
- **Recommendation:** never snap a living trunk mid-fall. Optional: for trees ≥20 blocks or obstacle landings, detach the top 15–25% 50–100 ms after impact with its own tumble and a snap sound.

---

## 3. How Minecraft implementations animate the fall

### 3.1 Dynamic Trees (Forge/NeoForge) — the reference implementation

Read in full: [FalloverAnimationHandler.java](https://raw.githubusercontent.com/DynamicTreesTeam/DynamicTrees/develop/1.20.1/src/main/java/com/ferreusveritas/dynamictrees/entity/animation/FalloverAnimationHandler.java), AnimationConstants.java and FallingTreeEntity.java ([repository](https://github.com/DynamicTreesTeam/DynamicTrees), branch develop/1.20.1).

- **Handler choice:** cut from below with mass centre y ≥ 1 → **fallover**; other cuts → physics (drop/fling); explosion → blast; fire → burn.
- **Mass centre:** branch blocks weighted by `radius²·64/4096` (cross-section); `height = massCenter.y * 2`.
- **Motion, per tick:** `fallSpeed += 0.2/height; rotation += fallSpeed` (degrees) — a **constant angular acceleration** of 0.1/h_cm °/tick² (40/h_cm °/s²) whatever the angle, i.e. ease-in-quad. It matches physics only at ~5° tilt and is 2–3× too slow near the ground:

| Centre of mass (tree ≈ 2·h_cm) | Time to 90° | Final speed |
|---|---|---|
| 2.5 blocks (5) | 67 ticks = 3.35 s | 54°/s |
| 5 blocks (10) | 95 ticks = 4.75 s | 38°/s |
| 7.5 blocks (15) | 116 ticks = 5.80 s | 31°/s |
| 10 blocks (20) | 134 ticks = 6.70 s | 27°/s |

  (Physics: 2.8–3.9 s and 75–106°/s for 10–20 m broadleaf trees.)
- **Pivot:** `renderTransform` translates by −(cut direction × radius/16), rotates, translates back — the axis sits **on the trunk surface on the fall side** (leading-edge pivot).
- **Collision and bounce:** from tick 10, one small box per trunk segment (half-size 1/16 up to the trunk radius, ≤24 segments). On a hit: end sound, leaf particles, undo the last step, `fallSpeed *= -0.25` (TREE_ELASTICITY); landed when |fallSpeed| < 0.02. Because its acceleration is low, a 10-block tree's first rebound rises ~5.7° over ~2.4 s.
- **Leaf particles:** first hit `fallSpeed×5` per leaf block, capped by config and × e^(−bounces); velocity = angular velocity × leaf height + jitter.
- **Lifecycle:** seeds and leaf drops fall *before* the topple; dies at |rotation| ≥ 160°, on landing, or at tick 120 + trunk height; logs **pop at the cut position**. Damage = wood volume × |fallSpeed| × 3, once.
- **Sound:** start sound at the cut; end sound at first collision; a water-hit sound.
- **Physics handler (drops/flings):** gravity 0.03 blocks/tick², drag ×0.98, random spin, no bounce, 120-tick life.

### 3.2 Panda's Falling Trees (Fabric/NeoForge, 1.20–1.21.10)

Read: [TreeRenderer.kt](https://cdn.jsdelivr.net/gh/ThePandaOliver/Pandas-Falling-Trees@master/src/main/kotlin/client/render/TreeRenderer.kt), AnimationConfig.kt, TreeEntity.kt, GenericTree.kt ([Modrinth](https://modrinth.com/mod/pandas-falling-trees)).

- **Curve:** angle = 90·(1 − cos(πt/2T)), T = `fallAnimLength` 2.5 s for every size — **ease-in-sine**. Final speed 56.5°/s is only 1.57× the average (physics ~3.5×): floaty.
- **Bounce:** upward half-sine of up to **10°** over **1.0 s**.
- **Pivot:** `Vector3f(0, 0, .5f + distance)` — far edge of the trunk on the fall side (2×2 included).
- **Direction, culling:** away from the player, 4 cardinal directions; culling disabled.
- **Sound:** fall sound at tick 1; impact at tick `T·20 − 5` — **250 ms before** the visual hit.
- **After landing:** at 4.0 s (1.5 s lying) items drop at the stump.

### 3.3 Enhanced Falling Trees (EFT; Fabric/Forge/NeoForge, 1.20–26.2)

Read: [README](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/README.md), [TreeRenderer.java](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/common/src/main/java/me/adda/enhanced_falling_trees/client/render/TreeRenderer.java), [GroundUtils.java](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/common/src/main/java/me/adda/enhanced_falling_trees/utils/GroundUtils.java), AnimationConfig.java ([Modrinth](https://modrinth.com/mod/enhanced-falling-trees)).

- **Core:** as Panda's (ease-in-sine, half-sine bounce, edge pivot). Fall / bounce / length: trees 2.5 s / 10° / 1 s; bamboo 1 s / 4° / 0.3 s; cactus 1.5 s / 8° / 0.5 s. Lifetime 4 s.
- **Terrain angle:** per column along the fall line, the highest solid non-leaf block; angle = `atan(index_of_max / max)` — to the **highest** bump (90° + atan(…) for mostly-lower terrain). Eased by `lerp 0.05` **per frame** (frame-rate dependent). Bounce = round(target/10)° ≤ 10. Water: slow lerp and a bobbing sine.
- **Flaw:** the highest bump is not the first contact — a low bump near the stump has a steeper elevation angle and is hit first. The README admits: "Sometimes when a tree falls, some part of it may fall into the ground … just an imitation of physics using simple functions". The correct rule is the **maximum elevation angle** (§5).

### 3.4 Instant fellers and collapses

- **FallingTree (Rakambda):** modes "Instantaneous", "Shift down", "Fall items", "Fall blocks" ([CurseForge](https://www.curseforge.com/minecraft/mc-mods/falling-tree)). The animated modes call `serverLevel.fallBlock(…)` — vanilla falling-block entities dropped straight down or with ±0.2 blocks/tick spread, plus leaves within 5 blocks ([FallingAnimationTreeBreakingHandler.java](https://cdn.jsdelivr.net/gh/Rakambda/FallingTree@26.3.0.2/common/src/main/java/fr/rakambda/fallingtree/common/tree/breaking/FallingAnimationTreeBreakingHandler.java)). A **vertical collapse**, not a hinged topple.
- **Tree Fall (Ion_Forge):** "break the bottom log and it fells the connected trunk, while only clearing leaves that are actually tied to that tree"; no animation described ([CurseForge](https://www.curseforge.com/minecraft/mc-mods/tree-fall)).

### 3.5 Physics engines, plugins and data packs

- **Dynamic Falling Tree** (Fabric 1.21.1): the tree becomes a Sable `ServerSubLevel` (physics-backed blocks); force and torque from the player's position (`impulse_torque 2.0`, `impulse_force 1.5`); BARRIER→AIR swap in one tick against flicker; impact smoke; leaves break after settling ([Modrinth](https://modrinth.com/mod/dynamic-falling-tree); [GitHub](https://github.com/Cukkoo12/dynamic-falling-tree)).
- **Tree Physics** (Sable addon): trees on rooted dirt fall with interactive physics; 111k downloads ([sable-addons.com](https://sable-addons.com/addons/tree-physics)).
- **Physics Trees:** "tilting fall animation with physics-based acceleration"; topples other trees; "Loot drops at the fallen position" ([CurseForge](https://www.curseforge.com/minecraft/mc-mods/physics-trees)).
- **Timbr** (Spigot): FallingBlock entities steered by a "proportional feedback controller"; max 128 logs / 150 leaves ([SpigotMC](https://www.spigotmc.org/resources/timbr.135352/update?update=641327)).
- **Physical Falling Trees** (data pack): "Trees fall to the heavier side"; the model lies "for half a second before transforming into real blocks" ([Modrinth](https://modrinth.com/datapack/physical-falling-trees)).
- **Timber Physics** (data pack): "very taxing for Servers and Clients when big trees are chopped" ([Planet Minecraft](https://www.planetminecraft.com/data-pack/timber-physics-trees-you-chop-will-fall/)).

### 3.6 Bedrock add-ons

- **Tree Physics** (26.30; [MCPEDL](https://mcpedl.com/tree-physics/)): praised ("I didn't expect it to resemble the Java mod … so closely"); complaints: "**Make trees take less time to turn into wood**", trees "fall over and **no sound play**", Realm operators not detected.
- **Tree Fall Add-on** (1.21.20–1.21.50): "all the other logs will automatically fall"; complaint about a crafting requirement ([MCPEDL](https://mcpedl.com/tree-fall-add-on/)).
- **Tree Feller V3:** "the whole tree collapses"; "doesn't work" reports ([MCPEDL](https://mcpedl.com/tree-feller-function-pack/)). **Falling Minerals and Trees:** "all the wooden blocks fall simultaneously" ([9Minecraft](https://www.9minecraft.net/falling-minerals-and-trees-addon-mcpe/)).
- **No Bedrock add-on publishes keyframes, easing or durations** (searched MCPEDL, CurseForge Bedrock, 9Minecraft, web; packages not opened). On published evidence our template-exact "carbon copy" entity is the most advanced Bedrock approach, closest to Dynamic Trees and Panda's.

### 3.7 Outside Minecraft

- **Stardew Valley** ([decompiled Tree.cs](https://raw.githubusercontent.com/veywrn/StardewValley/master/StardewValley/TerrainFeatures/Tree.cs)): `treecrack` at the cut; per frame `shakeRotation += maxShake²`, `maxShake += π/2048` → angle ∝ ~t³ (**ease-in-cubic**), **1.85–2.12 s** at 60 fps, ending ~130°/s; random `leafrustle`; past 90° `treethud`, **90–120 leaf particles** and debris; no bounce.
- **Valheim:** "heavy, chaotic vectors of destruction … a messy domino effect of logs and particles and screenshake" ([PC Gamer](https://www.pcgamer.com/in-valheim-the-trees-punch-back/)).
- **Survival-game survey** ([PC Gamer](https://www.pcgamer.com/chopping-down-trees-in-survival-games-ranked-from-worst-to-least-worst/)): praised The Forest ("a burst of leaves"), H1Z1 ("falls all the way to the ground and there's a thud"), Factorio ("a nice little shower of leaves"); criticised Rust ("pops out of existence"), Ark ("I want to see the body fall"), DayZ ("sort of sinks into the ground").

### 3.8 Side-by-side

| Implementation | Fall time | Curve | Pivot | Terrain | Bounce | After landing |
|---|---|---|---|---|---|---|
| **Physics** (broadleaf, from 5°) | 2.8 s (10 m), 3.9 s (20 m) | θ''∝sin θ ≈ offset power 3.2 | hinge ≈ leading edge | first contact | e 0.15–0.25 → 1.3–3.6° | — |
| Dynamic Trees | 4.75 s (10), 6.7 s (20) | constant α (quad) | trunk surface, fall side | trunk-segment boxes | e = 0.25 | items at the cut |
| Panda's | 2.5 s fixed | ease-in-sine | edge (0.5 + n) | none (90°) | 10°, 1 s half-sine | items at the stump at 4 s |
| EFT | 2.5 s fixed | ease-in-sine | edge × factor | highest bump, lerp 0.05/frame | ≤10°, 1 s | particles; 4 s |
| Stardew | 1.85–2.1 s | ≈ cubic | base | n/a (2D) | none | debris + 90–120 leaves at the thud |
| Physical Falling Trees | n/a | n/a | n/a | n/a | n/a | lies 0.5 s, then blocks |
| Sable mods | simulated | rigid body | simulated | full collision | simulated | settles, leaves break |
| **Ours** (BP-02 1.3.219 / RP-01 1.3.121) | impact 4.6 s fixed | keyed, ≈ physics, 5.6° rms ahead | trunk **centre** | trunk axis only (Appendix A) | 1.05× overshoot + (rest − 4°) | rest 3.5 s → items + litter |

### 3.9 What players praise and complain about

- **Praised:** the whole fall visible; a heavy thud; a leaf burst; chaos (Valheim's dominoes); physics like the Java mod.
- **Complained about:** vanishing or popping; sinking into the ground (DayZ, EFT); **waiting too long for the wood**; no sound; lag on big trees; activation chores.

---

## 4. What makes it look right

### 4.1 The rotation curve

**RMS error of standard easing curves against the physical curve (from 5°, normalised):**

| Curve | RMS error |
|---|---|
| ease-in-sine (Panda's, EFT) | **10.4°** |
| ease-in-quad (Dynamic Trees) | 7.4° |
| ease-in-cubic (Stardew) | 4.1° |
| ease-in-quart | 7.9° |
| ease-in-expo | 13.9° |
| **5° + 85°·f^3.2** | **1.1°** |
| **2° + 88°·f^3.85** (2° start, §6.2) | **1.2°** |

- **Exact keys are cheap:** 12 keys cover the fall (§6.2).
- **No ease-out into the impact.** Guides suggest ease-out "when something is coming to a stop (like a rocket landing)" ([Febucci](https://blog.febucci.com/2018/08/easing-functions/)), but a tree does not brake itself: contact is its fastest instant, and slowing reads as "being lowered".
- **Principles** ([Bloop Animation](https://www.bloopanimation.com/the-12-principles-of-animation/)): **anticipation** (the creaking lean); **slow in**; **follow-through** ("parts … come to rest at different times" — the crown lags, whips at impact, wobbles; leaves trail); **timing** (∝ √H).

### 4.2 The pivot belongs on the leading edge

- **Centre pivot is wrong:** rotating a trunk of half-width r about its centre line moves a leading-face base point to −r·sin θ — the leading half sinks into the stump from the first degree, and at 90° the lower half lies **r below the pivot** (0.5 block for 1×1, 1 block for 2×2).
- **Leading-edge pivot is right:** the whole trunk stays on or above the cut plane at every angle. Dynamic Trees (radius offset), Panda's (0.5 + n) and EFT all do this. Real hinges sit ~1/3 of the diameter behind the front (the face-cut depth); at block scale the leading face is the right approximation.

### 4.3 Stop exactly at the terrain — and let the crown hold the trunk up

- **The rule:** θ_rest = 90° − maxᵢ atan2(Gᵢ + sᵢ − y_p, xᵢ) (§5). On a uniform slope with the pivot at the surface: **90° + β** downhill, **90° − β** uphill.

| Flat ground, pivot on a 1-block stump | θ_rest |
|---|---|
| 9-block trunk, trunk line only (tip touches; crown would be buried) | 96.3° |
| Same tree, crown 1.5 blocks below the trunk line after crushing | **86.8°** |
| Ground-level cut, same crown | 80.5° |
| 20-block trunk, crown support 2 blocks | 87.1° |

- A real felled tree typically lies with its top propped on crushed limbs; the first-contact rule reproduces that look.
- **Other resting angles take about the same time** (fraction of the 90° time: 70° 0.925, 80° 0.964, 100° 1.033, 110° 1.063, 135° 1.132). Scaling a 90° key curve by θ_rest/90 is a fair approximation for 70–110°.

### 4.4 Impact effects: particles, camera shake and sound

**Particles:**
- **Lean:** sawdust at the cut; a few leaves shaken loose.
- **Fall:** leaves shed in proportion to angular speed (Dynamic Trees: `fallSpeed×5` per leaf block, capped).
- **Impact:** dust or dirt where the crown and tip land (the fastest parts) and a thinner line along the trunk; a leaf burst (Stardew: 90–120); wood chips; snow puff on snow; splash on water.
- **After:** drifting leaves that stick where they land and fade (*Falling Leaves*: lifespan 200 ticks, "snap in place … then fade out cleanly" — [FallingLeaves backport](https://github.com/haunterdev/FallingLeaves-1.12.2)).

**Camera shake:**
- **Bedrock:** `camerashake add <player> [intensity 0–4] [seconds] [positional|rotational]`, which players can disable in Accessibility ([Minecraft Wiki](https://minecraft.wiki/w/Commands/camerashake)); experimental `Camera.addShake` sums intensities, capped at 4.0 ([Microsoft Learn](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/camerashakeoptions?view=minecraft-bedrock-experimental&viewFallbackFrom=minecraft-bedrock-stable)).
- **Design** ([Eiserloh, GDC 2016](http://www.mathforgameprogrammers.com/gdc2016/GDC2016_Eiserloh_Squirrel_JuicingYourCameras.pdf)): linearly decaying "trauma", shake = trauma² (or ³), "3D: rotational only", Perlin noise, "like salt".
- **Recommended:** rotational, intensity 0.05–0.3 by tree size, falloff (1 − d/d_max)² with d_max ≈ 1.5 H, 0.3–0.6 s.

**Sound:**
- **Layers:** axe hit; hinge **creak** during the lean; optional **crack** near 45°; rising **whoosh + rustle** in the last ~40%; a low **thud** at contact with **branch snaps** 0–150 ms later; a −10 dB thud at the rebound; twig patter; a rumble tail for big trees.
- **Sync:** audio is detectable from **45 ms early to 125 ms late** (ITU-R BT.1359; EBU R37 asks +40/−60 ms — [Audio-to-video synchronization](https://en.wikipedia.org/wiki/Audio-to-video_synchronization)). Panda's 250 ms lead is outside it.
- **No artificial delay:** ~2.9 ms per block (343 m/s, [Speed of sound](https://en.wikipedia.org/wiki/Speed_of_sound)) is 87 ms at 30 blocks, within tolerance.
- **Method:** start the sample X ms early if its transient is X ms in, so the transient lands on contact; best, fire cues from the animation timeline (§4.7).

### 4.5 Bounce and settle

- **Rebound:** up by 1.3–2.3° (e ≈ 0.15–0.2) over ~0.15–0.3 s, back to the rest angle by ~0.3–0.6 s (scales with √H). **Only upwards** — never past the rest angle.
- **Second rebound:** ≤0.3–0.5° or none (physics: 4% of the first).
- **Crown wobble (overlapping action):** canopy bone ±1.5°, damped, ~2 cycles in 0.6–0.9 s from impact.
- **Optional butt slide (§1.7):** cut end moves 0.3–0.6 block forwards and down off the stump over 0.2–0.3 s.
- **Dust** settles over 1–2 s.

### 4.6 How long the fallen tree should lie

- **Others:** Physical Falling Trees 0.5 s; Panda's/EFT 1.5 s after impact; Stardew instant; Dynamic Trees at landing. Players complain about waiting (§3.6).
- **Recommendation:** hold still **1.0–1.5 s after the rebound ends** (~1.5–2.1 s after impact), then convert crown → butt over 0.3–0.5 s: litter, saplings and loot in the crown zone; log items **along the trunk line** (as Physics Trees), not at the stump — consistent with the ruling "no lying log; logs drop as items".

### 4.7 Bedrock mechanics: what keyframes and Molang can and cannot do

- **Keyframes** ([Microsoft Learn, actor_animation 1.8.0](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/actor_animation.v1.8.0?view=minecraft-bedrock-stable)): `pre`/`post`; `lerp_mode` **`linear` or `catmullrom`**; Molang values; `loop` true/false/`"hold_on_last_frame"`; `anim_time_update` (default `"query.anim_time + query.delta_time"`), `blend_weight`, `start_delay`; `sound_effects`/`particle_effects` **timelines** on locators. Older docs: "only linear interpolation is supported", channels apply "per-channel-additively" ([bedrock.dev](https://bedrock.dev/docs/stable/Animations)).
- **Catmull-Rom overshoots** where neighbouring slopes differ: keys 0.89 → 1.00 → 1.00 overshoot by 4/27 of the 0.055 tangent = 0.8% (0.7° into the ground on a 90° fall). **Keep impact segments linear.**
- **Molang** ([bedrock.dev Molang](https://bedrock.dev/docs/stable/Molang); [Bedrock Wiki](https://wiki.bedrock.dev/visuals/math-based-animations)): `math.ease_in_*`/`ease_out_*` (start, end, 0_to_1), `math.pow`, `math.lerp`, `math.clamp`, trig **in degrees**, `query.anim_time`, `query.delta_time`; entity variables persist. **Can** evaluate a closed form per frame (`2 + 88*math.pow(f, 3.85)`, clamped) and scale speed via `anim_time_update`. **Cannot** sample terrain or collide — **compute θ_rest and the time scale in the server script** and pass them as `client_sync` properties read with `q.property('ns:name')` ([Bedrock Wiki, Entity Properties](https://wiki.bedrock.dev/entities/entity-properties)).
- **Engine law:** `q.property` arithmetic is witnessed to fail in **position** channels; our rotation keys already use `q.property(...) * k` successfully. **Test `q.property` inside `anim_time_update` first**; fallback: 3–4 size classes chosen by the controller.
- **Sync:** server `playSound` (our cues at 82/92 ticks) arrives with network latency; timeline sounds play on the client in step with the pose. Keep server sounds for unpredictable events (an early stop against an obstacle).
- **Culling (a check, not a finding):** `visible_bounds_*` must enclose the **fallen** pose (width ≥ 2·(H + crown radius), height ≥ H + R). `dark_oak_elder_00` declares 29 × 32 — verify a fallen crown is not culled. Panda's simply disables culling.

---

## 5. Terrain interaction: computing the resting angle

### 5.1 Frame and rotation

- **Set-up:** origin at the pivot P (leading bottom edge at the cut plane); f = fall direction, l = lateral.
- **Rotation:** a point (u forwards, v up, w sideways) tilted by θ moves to **x = u·cos θ + v·sin θ**, **y = v·cos θ − u·sin θ** (height above the cut plane).
- **Checks:** the leading face (u = 0) lands flat at 90°; points behind (u < 0) stay above; crown parts in front (u > 0) go **below** the plane — they touch first.

### 5.2 Method A — trunk line plus support offsets (closed form)

```
θ_rest = 90° − max_i atan2( G_i + s_i − y_p , x_i )
```

- **Terms:** Gᵢ = ground top surface at forward distance xᵢ; y_p = pivot height (cut plane); sᵢ = 0 for the trunk's lower face (edge pivot), r_trunk for an axis pivot, crown-underside depth minus crush inside the crown span.
- **Sampling:** ≤0.5-block steps by 3D-DDA so diagonal falls skip no cell ([Amanatides & Woo](http://www.cse.yorku.ca/~amana/research/grid.pdf)); a cell's **near edge** when ground is above the pivot, **far edge** when below; the highest ground across the swept width.
- **First contact = maximum elevation angle, not the highest point:** a 2-block bump 1 block out (63°) is hit before a 5-block hill 10 out (27°) — EFT's error.

### 5.3 Method B — rotate the carbon-copy voxels (recommended)

The falling entity is a template-exact copy, so the script already has every log and leaf cell. Rotate them; stop at the first angle where any part meets the ground.

```js
// Server-side, once at spawn. Units: blocks. P = leading bottom edge of the trunk at the cut plane.
// Tree-local cells: {u (forward from P), v (up from cut plane), w (lateral), kind: "log"|"leaf"}.
const CRUSH = { log: 0.0, leaf: 0.75 };          // how far a part may sink (branches crush); tune by witness
const EPS = 0.03;                                  // keep faces off the ground (z-fighting margin)

function restAngle(dim, P, f, cells) {
  const support = underside(cells);                // per (w, v) row keep the max-u cell; per (w, u) the min-v cell
  const G = corridorHeightmap(dim, P, f,           // ground TOP FACE (relative to cut plane) per 0.5-block x, per w
              maxReach(cells) + 2, crownHalfWidth(cells) + 1);
  let ok = 0;
  for (let deg = 0.5; deg <= 135; deg += 0.5) {
    const c = Math.cos(deg * Math.PI / 180), s = Math.sin(deg * Math.PI / 180);
    for (const p of support) for (const [du, dv] of CORNERS) { // the 4 (u,v) corners of the cell
      const u = p.u + du, v = p.v + dv;
      const x = u * c + v * s, y = v * c - u * s;
      if (x <= 0) continue;                        // behind the pivot: the stump side
      if (y < G.at(x, p.w) - CRUSH[p.kind] + EPS) return refine(ok, deg); // bisect to 0.1°
    }
    ok = deg;
  }
  return 135;                                      // nothing hit within 135°: cliff edge; clamp (§5.5)
}
```

- **Cost:** ~150–250 underside points × 270 steps of pure arithmetic — well under 1 ms. The heightmap (~40 × 9 columns) is built once with `getBlock` scans or `getTopmostBlock`.
- **Bonus outputs:** the exact contact point (for dust), the impact angle, and whether contact is nearer than the centre of mass (§5.5).

### 5.4 Thick trunks, clearance and the ground definition

- **Clearance:** a leading-edge pivot needs **no** trunk offset; an axis pivot needs +r (exactly r/sin θ). Leaves may sink by the crush allowance, logs may not. A 0.02–0.05 block margin prevents z-fighting.
- **Ground** = the **top face** (block y + 1) of the highest blocking block in the column.
  - **Include:** `minecraft:grass_block`, `pw:grass_block`, dirt (incl. coarse, rooted), podzol, mycelium, path, farmland, sand, gravel, stone, ores, snow *blocks*, ice, terracotta, concrete, planks, other trees' logs (as obstacles).
  - **Exclude:** air, leaves (optionally soft obstacles), short/tall grass, ferns, flowers, saplings, vines, snow layers, carpets.
  - **Avoid substring tests:** `includes("grass")` catches `grass_block`. Use exact sets or tags; `pw_civ_walk.js` already guards with `!id.includes("grass_block")`.

### 5.5 Edge cases

- **Water:** rest on the surface plus buoyancy; splash, hit-water sound (as Dynamic Trees), slow bob (as EFT).
- **Contact nearer than the centre of mass:** the tree pivots over the obstacle — continue rotating about the contact (seesaw; the butt lifts back, the one case for kickback) or accept the contact angle.
- **No ground within reach (cliffs):** clamp at 135°; optionally drop or slide.
- **Other trunks, buildings:** stop at contact with a small kickback and a leaf shower.
- **Uphill banks:** rest angles of 60–80° are correct and impact comes earlier (0.925 of the time at 70°).

---

## 6. Recommended specification

### 6.1 Pivot rule

- **Axis:** horizontal, perpendicular to the fall, through **the trunk's leading bottom edge at the cut plane**: P = base centre + r_trunk·f at stump-top height (r 0.5 for 1×1, 1.0 for 2×2, polygon radius for dodecagons).
- **Geometry:** move the root (fall) bone pivot from [0, 0, 0] to that edge — mind the X-mirror and Blockbench sign laws; witness the first side before deriving the rest.
- **One convention:** the script's terrain sampling must use **the same pivot** as the rendered model.

### 6.2 Rotation function

**Universal curve from 2° at rest** (exact physics; the same for every height and species):

| f = t/T | 0 | 0.20 | 0.35 | 0.50 | 0.60 | 0.70 | 0.78 | 0.85 | 0.90 | 0.94 | 0.97 | 1.00 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| θ | 2.0° | 2.9 | 5.1 | 9.8 | 15.4 | 24.2 | 34.6 | 47.3 | 58.9 | 70.0 | 79.5 | 90.0 |
| × of 90° | .022 | .032 | .057 | .109 | .171 | .269 | .385 | .526 | .654 | .778 | .883 | 1.000 |

- **Time scale:** T = c·√H s (2° → 90°), c = **1.10** broadleaf, 1.02 conifer, 1.19 rod-like/crown-heavy. Broadleaf: 6 m 2.70 s · 10 m 3.48 · 15 m 4.27 · 20 m 4.93 · 25 m 5.51 · 30 m 6.03. Per tree: T = 1.101·√(L_eff/0.574) (§1.2). An optional global factor 0.85–1.0 keeps the shape.
- **Closed form (Molang):** θ(f) = 2 + 88·f^3.85 (1.2° rms; 108.3° where physics reaches 110°). **Clamp** with min(θ(f), θ_rest); impact is when θ(f) reaches θ_rest, so uphill/downhill timing falls out.
- **Keyframe alternative:** scale the "× of 90°" row by θ_rest at fixed times (current architecture) — fine for 70–110°; linear near impact.
- **Before the fall:** a 0 → 2° "creak ramp" (ease-in-out, 0.35–0.6 s) ending at zero speed — no hitch.
- **Optional per-tree lean:** start at θ₀ = atan(δ/h_cm), clamped 1–5°, instead of 2°.

### 6.3 Timeline (broadleaf; θ_rest = 90° on open ground — scale the angles by θ_rest/90)

| Phase | 10 m tree | 20 m tree | Pose | Cues |
|---|---|---|---|---|
| **Cut** | 0.00 s | 0.00 s | upright copy spawns over the real tree | axe/break sound; sawdust puff |
| **Hold** | 0.00–0.15 | 0.00–0.15 | 0° | — |
| **Creak ramp** | 0.15–0.60 | 0.15–0.75 | 0 → 2° (ease-in-out) | creak loop from 0.05 s; 3–8 leaves shaken loose |
| **Slow lean** | 0.60–1.82 | 0.75–2.47 | 2 → 5° (physics keys) | creak continues, lower pitch for big trees |
| **Accelerating fall** | 1.82–3.56 | 2.47–4.94 | 5 → 47° | rustle rises; leaves trail from ~35°; optional *crack* at 45° (≈3.52 / ≈4.88 s) |
| **Final fall** | 3.56–4.08 | 4.94–5.68 | 47 → 90° (58.9° at 0.90T, 70.0° at 0.94T, 79.5° at 0.97T) | whoosh peaks in the last 0.5 s |
| **Impact** | **4.08** | **5.68** | θ_rest reached exactly (linear segment) | thud transient on this frame (−0/+40 ms); branch snaps +0–150 ms; dust/leaf burst at crown and tip; rotational shake 0.15×size, 0.35–0.5 s |
| **Rebound up** | 4.08–4.30 | 5.68–5.99 | +2.3° (e = 0.2), ease-out | crown wobble starts (±1.5°, damped) |
| **Rebound down** | 4.30–4.51 | 5.99–6.29 | back to θ_rest, ease-in | second thud, −10 dB |
| **Settle** | 4.51–4.9 | 6.29–6.8 | optional 0.3° micro-bounce; optional butt slide 0.3–0.6 block | twig and leaf patter; dust settles 1–2 s |
| **Rest** | 4.9–6.0 | 6.8–7.9 | still | drifting leaves |
| **Cleanup** | 6.0–6.5 | 7.9–8.4 | crown → butt dissolve | litter, saplings, loot in the crown zone; log items along the trunk line; entity removed |

For other sizes, multiply the slow-lean-to-final-fall span by √(H/10).

### 6.4 Particle and sound cue list

1. **Cut (t = 0):** wood-break particles; axe/break sound.
2. **Creak (0.05 s → impact − 1.0 s):** 2–4 overlapping creak one-shots, louder and slower for big trees, on the animation timeline.
3. **Shaken leaves (lean):** 3–8 leaf particles from the crown edge.
4. **Crack (optional, θ ≈ 45°):** one fibre snap, ~−6 dB vs the thud.
5. **Rustle and whoosh (f ≈ 0.6 → impact):** volume and leaf trails follow angular speed.
6. **Impact (contact frame):** size-scaled thud + branch snaps (+0–150 ms) + leaf crash; dust at the §5.3 contact points in the ground's colour; 40–120 leaves by crown size; wood chips; camera shake within ~1.5 H.
7. **Rebound landing:** soft thud (−10 dB), small dust puff.
8. **Settle (1–2 s):** leaf and twig patter; leaves stick and fade; dust fades.
9. **Cleanup:** litter burst in the crown zone, sapling and loot pops, log items along the fallen trunk.

### 6.5 Witness checklist (each in-game, on the target device)

1. **Flat grass, 9-block oak:** no log or leaf below the grass top; the trunk rests with its top propped (~84–90°).
2. **20–30° downhill slope:** the tree lies along the slope (>90°) without clipping.
3. **Uphill bank:** it stops on the bank, earlier, with nothing inside the bank.
4. **2×2 dark oak:** the base does not sink into the stump in the first degrees.
5. **Timing:** a young birch falls visibly faster than an elder oak, and both start slowly.
6. **Sound:** the thud coincides with contact — never early.
7. **Rebound:** goes **up**, then settles; no dip into the ground.
8. **Cleanup:** logs drop along the trunk line, and the wait does not feel long.

---

## Appendix A — Our `ft:falling_tree` against this research (static read; P1: unverified)

**Files read:**
- `/home/claude/_build/bp02-219/scripts/main.js` — `computeFallAngle` 133–155; `isFallCollider` 159–185; `FALL_KEYS` 184 / `fallAngleAtTime` 209; `pickFallYaw → groundYAt` 860–880; spawn 1430–1450; collision pin 1700–1790.
- `/home/claude/_build/rp01-121/animations/falling_tree.animation.json`.
- `/home/claude/_build/rp01-121/models/entity/ft_tpl/*.geo.json`.

**Candidate mechanisms for "they fall too far — they clip into the earth":**
- **A1 — ground = block y, not top face.** `groundYAt` returns the first blocking block's y and `computeFallAngle` treats it as the surface, which is y + 1: ground reads **1 block low**.
- **A2 — `grass_block` skipped.** `groundYAt` skips ids containing `"grass"`, so `minecraft:grass_block`/`pw:grass_block` count as air: **another block low** on the commonest surface. `isFallCollider` (main.js:163) does the same, so the pin ignores grass. `pw_civ_walk.js:110/301` already guards with `!id.includes("grass_block")`.
- **A3 — script pivot a block above the drawn one.** `computeFallAngle` measures from `stumpPos.y + 1`; the rendered pivot (root [0, 0, 0], seat `[0,−16,0]`, entity at `stump.y + 1`) sits at `stump.y`, the top of the cut block.
- **A4 — combined, on flat ground:** the script uses dY = −4 (grass) or −3 (other surfaces) instead of the true −1. Terminal angle for the trunk axis, with the tip's height relative to the surface in brackets (rendered pivot 1 block above the surface):

| Trunk length | Grass | Dirt/stone | True axis contact |
|---|---|---|---|
| 5 | **128.7°** (−2.12) | 121.0° (−1.57) | 101.3° (+0.02) |
| 9 | **114.0°** (−2.66) | 108.4° (−1.85) | 96.3° (0.00) |
| 14 | **105.9°** (−2.85) | 102.1° (−1.93) | 94.1° (0.00) |
| 20 | **101.3°** (−2.92) | 98.5° (−1.97) | 92.9° (0.00) |

  The crown — beyond the top and 2–4 blocks below the axis — sits deeper still.
- **A5 — only the trunk axis is tested** (d = 2..trunkLen): crown underside, crown beyond the top and trunk radius are ignored. Even correct ground gives 96° with the crown buried; flat ground should give ~81–87° (§4.3).
- **A6 — overshoot and bounce go into the ground:** the fall overshoots to **1.05×** at 4.72 s (~5–6°), and the rest animation's first key is **`rest_angle − 4.0`** — with negative angles, 4° *more* rotation. A rebound must *reduce* |angle| (`rest_angle + k`).
- **A7 — late collision pin:** samples the axis from `pinY = stump.y + 1` (a block high), ignores grass, and stops within 1.5° of an already-buried terminal.
- **A8 — centre pivot:** root pivot [0, 0, 0] dips the leading half of the base into the stump from the first degree; at rest the lower half (0.5/1.0 block) lies below the script's line.
- **A9 — timing (polish):** one curve for all sizes, impact 4.6 s; from 5° it runs 5.6° rms ahead of physics and ends at 66°/s vs ~100°/s for the ~11 m tree it matches — slightly floaty, soft impact.

**Confidence:** A1–A3 and A6–A8 are direct code reads; the exact A4 numbers depend on runtime facts (the meaning of `stump.y`, the surface block).

**One confirming test:** fell one tree on flat grass and read the `[FELL]` summary line (it already prints `angle=`). A value at or below **−100** for a 9–14-block trunk confirms A1–A4.

---

## Appendix B — Reproducible calculation (Python, abridged)

```python
import math
G = 9.81

def fall_time(l_eff, th0_deg, th1_deg=90.0, steps=20000):
    """t = sqrt(L_eff/2g) * integral dθ / sqrt(cos θ0 − cos θ); θ = θ0 + u² removes the singularity."""
    th0, th1 = math.radians(th0_deg), math.radians(th1_deg)
    u_max = math.sqrt(th1 - th0); du = u_max / steps; total = 0.0
    for i in range(steps):
        u = (i + 0.5) * du; th = th0 + u * u
        total += 2 * u / math.sqrt(math.cos(th0) - math.cos(th)) * du
    return math.sqrt(l_eff / (2 * G)) * total

def l_eff_tree(trunk, crown, crown_h, crown_r):
    """Cone trunk (I≈M H²/10, h_cm=H/4) + spherical crown; returns (h_cm/H, L_eff/H)."""
    i = trunk / 10 + crown * (crown_h**2 + 0.4 * crown_r**2)
    mh = trunk / 4 + crown * crown_h
    return mh / (trunk + crown), i / mh

h, le = l_eff_tree(0.70, 0.30, 0.70, 0.18)          # broadleaf: 0.385, 0.574
print(round(fall_time(le * 10, 5.0), 2))             # 2.78 s (10 m, 5° → 90°)
print(round(fall_time(le * 10, 2.0), 2))             # 3.48 s (10 m, 2° → 90°)
# rebound lift for restitution e: e² · cos θ0 rad (height-independent)
print(round(math.degrees(0.2**2 * math.cos(math.radians(5))), 2))   # 2.28°
```

---

## For the main session — Retro-Sweep candidates

- **Hits:** trees/canopy/falling tree — A1–A9 (S/M, HIGH); scripts BP-02 — the `includes("grass")` pattern in `groundYAt`/`isFallCollider` (S, HIGH), scan other ground/collider helpers (S, MED); audio — creak/whoosh/thud into animation timelines (M, MED); tooling — node test of the rest-angle solver on synthetic heightmaps (S, HIGH); lessons — "ground = top face of the highest blocking block; never substring-match `grass`" (S).
- **No-hit list:** terrain caps · redwood biome · mobs (RP-07) · atmospherics/sky/fog · PBR/MERS · custom blocks/permutations · worldgen/features/mcstructures.

---

## Sources

**Physics and wood**
1. [Varieschi & Kamiya — Toy models for the falling chimney (arXiv physics/0210033)](https://arxiv.org/pdf/physics/0210033)
2. [Varieschi — The Falling Chimney web page (LMU)](https://gvarieschi.lmu.build/chimney/chimney.html)
3. [Toy Blocks and Rotational Physics (arXiv physics/0402119)](https://arxiv.org/pdf/physics/0402119)
4. [McDonald — Princeton Ph205 Problem Set 2 (1988), "Falling Chimney"](http://kirkmcd.princeton.edu/examples/ph205set2.pdf)
5. [PhysicsLAB — Rotational Dynamics: Pivoting Rods](https://www.physicslab.org/Document.aspx?doctype=3&filename=RotaryMotion_RotationalDynamicsPivotingRods.xml)
6. [Physics Forums — Time for a tree to fall after a 45-degree wedge cut](https://www.physicsforums.com/threads/time-for-a-tree-to-fall-after-a-45-degree-wedge-cut.455794/)
7. [Model-based estimation of tree centroids and required felling forces (ScienceDirect)](https://www.sciencedirect.com/science/article/pii/S2772375526002182)
8. [USDA FPL Wood Handbook (FPL-GTR-113), ch. 4 Mechanical Properties of Wood](https://www.fpl.fs.usda.gov/documnts/fplgtr/fplgtr113/ch04.pdf)
9. [Speed of sound (Wikipedia)](https://en.wikipedia.org/wiki/Speed_of_sound)

**Felling practice and safety**

10. [Hand felling (Wikipedia)](https://en.wikipedia.org/wiki/Hand_felling)
11. [Northern Woodlands — Hinge Hints](https://northernwoodlands.org/articles/article/hinge_hints)
12. [STIHL Pro Line — Tree Felling and the Notch](https://www.stihlproline.ca/en/arborist/tree-felling-and-the-notch)
13. [TCIA — Advanced Felling Techniques](https://tcimag.tcia.org/training/arboriculture-best-practices/advanced-felling-techniques/)
14. [TCIA — The Six-Step Felling Plan](https://tcimag.tcia.org/safety/chainsaw-safety-maintenance/the-six-step-felling-plan/)
15. [OSHA eTool: Logging — Glossary](https://www.osha.gov/etools/logging/glossary)
16. [USDA Forest Service — saw training glossary](https://www.fs.usda.gov/t-d/pubs/htmlpubs/htm06672805/page07.htm)
17. [UGA Extension — Chainsaw Safety: Preventing Common Tree Felling Accidents](https://fieldreport.caes.uga.edu/publications/C1243/chainsaw-safety-preventing-common-tree-felling-accidents/)
18. [Oregon Loggers — Hazard Alert: Falling Trees That Kick-Back](https://cdn.ymaws.com/oregonloggers.org/resource/collection/5D1E637C-6103-4F54-AE84-6E91EF21BB17/Hazard_Alert_Minimize_Falling_Trees.pdf)
19. [WorkSafe NZ — Managing the risks: manual tree felling](https://www.worksafe.govt.nz/topic-and-industry/forestry/safe-practice-for-forestry-and-harvesting-operations/part-e-mobile-plant-and-harvesting/21-0-managing-the-risks-manual-tree-felling/)
20. [UAF Extension — How To Cut Down a Tree](https://www.uaf.edu/ces/publications/database/energy/how-to-tree-cutting.php)

**Minecraft Java mods, plugins and data packs**

21. [Dynamic Trees — repository](https://github.com/DynamicTreesTeam/DynamicTrees)
22. [Dynamic Trees — FalloverAnimationHandler.java](https://raw.githubusercontent.com/DynamicTreesTeam/DynamicTrees/develop/1.20.1/src/main/java/com/ferreusveritas/dynamictrees/entity/animation/FalloverAnimationHandler.java)
23. [Panda's Falling Trees — Modrinth](https://modrinth.com/mod/pandas-falling-trees)
24. [Panda's Falling Trees — TreeRenderer.kt](https://cdn.jsdelivr.net/gh/ThePandaOliver/Pandas-Falling-Trees@master/src/main/kotlin/client/render/TreeRenderer.kt)
25. [Enhanced Falling Trees — Modrinth](https://modrinth.com/mod/enhanced-falling-trees)
26. [Enhanced Falling Trees — README](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/README.md)
27. [Enhanced Falling Trees — TreeRenderer.java](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/common/src/main/java/me/adda/enhanced_falling_trees/client/render/TreeRenderer.java)
28. [Enhanced Falling Trees — GroundUtils.java](https://raw.githubusercontent.com/addavriance/EnhancedFallingTrees/master/common/src/main/java/me/adda/enhanced_falling_trees/utils/GroundUtils.java)
29. [FallingTree (Rakambda) — CurseForge](https://www.curseforge.com/minecraft/mc-mods/falling-tree)
30. [FallingTree — FallingAnimationTreeBreakingHandler.java](https://cdn.jsdelivr.net/gh/Rakambda/FallingTree@26.3.0.2/common/src/main/java/fr/rakambda/fallingtree/common/tree/breaking/FallingAnimationTreeBreakingHandler.java)
31. [Tree Fall (Ion_Forge) — CurseForge](https://www.curseforge.com/minecraft/mc-mods/tree-fall)
32. [Dynamic Falling Tree — Modrinth](https://modrinth.com/mod/dynamic-falling-tree)
33. [Dynamic Falling Tree — GitHub](https://github.com/Cukkoo12/dynamic-falling-tree)
34. [Tree Physics (Sable addon)](https://sable-addons.com/addons/tree-physics)
35. [Physics Trees — CurseForge](https://www.curseforge.com/minecraft/mc-mods/physics-trees)
36. [Timbr — SpigotMC](https://www.spigotmc.org/resources/timbr.135352/update?update=641327)
37. [Physical Falling Trees — Modrinth data pack](https://modrinth.com/datapack/physical-falling-trees)
38. [Timber Physics — Planet Minecraft](https://www.planetminecraft.com/data-pack/timber-physics-trees-you-chop-will-fall/)
39. [Falling Leaves backport (leaf-particle physics)](https://github.com/haunterdev/FallingLeaves-1.12.2)

**Bedrock add-ons**

40. [Tree Physics — MCPEDL](https://mcpedl.com/tree-physics/)
41. [Tree Fall Add-on — MCPEDL](https://mcpedl.com/tree-fall-add-on/)
42. [Tree Feller Addon V3 — MCPEDL](https://mcpedl.com/tree-feller-function-pack/)
43. [Falling Minerals and Trees Addon — 9Minecraft](https://www.9minecraft.net/falling-minerals-and-trees-addon-mcpe/)

**Other games and design**

44. [Stardew Valley — decompiled Tree.cs](https://raw.githubusercontent.com/veywrn/StardewValley/master/StardewValley/TerrainFeatures/Tree.cs)
45. [PC Gamer — In Valheim, the trees hit back](https://www.pcgamer.com/in-valheim-the-trees-punch-back/)
46. [PC Gamer — Chopping down trees in survival games, ranked](https://www.pcgamer.com/chopping-down-trees-in-survival-games-ranked-from-worst-to-least-worst/)
47. [Eiserloh — Juicing Your Cameras With Math (GDC 2016)](http://www.mathforgameprogrammers.com/gdc2016/GDC2016_Eiserloh_Squirrel_JuicingYourCameras.pdf)
48. [Bloop Animation — The 12 Principles of Animation](https://www.bloopanimation.com/the-12-principles-of-animation/)
49. [Febucci — Easing Functions for Game Animations](https://blog.febucci.com/2018/08/easing-functions/)
50. [A Sound Effect — tree-felling sound effects library (Stuart Ankers)](https://www.asoundeffect.com/tree-felling-sound-effects/)
51. [Audio-to-video synchronization (Wikipedia; ITU-R BT.1359, EBU R37)](https://en.wikipedia.org/wiki/Audio-to-video_synchronization)
52. [Amanatides & Woo — A Fast Voxel Traversal Algorithm for Ray Tracing](http://www.cse.yorku.ca/~amana/research/grid.pdf)

**Bedrock technical**

53. [Microsoft Learn — actor_animation v1.8.0](https://learn.microsoft.com/en-us/minecraft/creator/reference/content/visualreference/actor_animation.v1.8.0?view=minecraft-bedrock-stable)
54. [bedrock.dev — Animations](https://bedrock.dev/docs/stable/Animations)
55. [bedrock.dev — Molang](https://bedrock.dev/docs/stable/Molang)
56. [Bedrock Wiki — Math-based animations](https://wiki.bedrock.dev/visuals/math-based-animations)
57. [Bedrock Wiki — Entity Properties](https://wiki.bedrock.dev/entities/entity-properties)
58. [Minecraft Wiki — /camerashake](https://minecraft.wiki/w/Commands/camerashake)
59. [Microsoft Learn — CameraShakeOptions (Camera.addShake)](https://learn.microsoft.com/en-us/minecraft/creator/scriptapi/minecraft/server/camerashakeoptions?view=minecraft-bedrock-experimental&viewFallbackFrom=minecraft-bedrock-stable)
