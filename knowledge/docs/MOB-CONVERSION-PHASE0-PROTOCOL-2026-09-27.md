# MOB CONVERSION — PHASE 0 PROTOCOL + TOOL PROGRAMME v1 (2026-09-27)

Companion to `MOB-CONVERSION-RESEARCH-2026-09-27.md` (§7 proposal). Written after Abs0lum's 16:28 answers: probe session **yes**; **everything fixed if it needs it**; chests/saddles/decor **converted and double-checked, Patrix quality**; bone names = **whatever Bedrock requires, otherwise my discretion**. Status of everything here: **PLAN — nothing built, nothing shipped.** Build starts on a GO.

Evidence tags as in the research doc: `VERIFIED` (vanilla files / witness), `SOURCE` (read in the engine or mod source), `MODEL` (my reading, not yet confirmed).

---

## §0 · The short answer to "what are the tests and what do I need to do?"

The three open items in the research doc were **not all game tests**. Sorting them by where the truth lives:

| Item | Where the truth lives | Who does it | Status |
|---|---|---|---|
| (a) how a JEM part's `translate` / `tx ty tz` compose with the vanilla part | the EMF/OptiFine source (already on disk) | me, no game | **half settled today (§1)** — the static half is `SOURCE`; the animated-variable half is next |
| (b) the vanilla rest pose of parts Patrix does not assign (fox, polar bear, horse, turtle, axolotl) | the vanilla Java model classes; failing that, one Java screenshot per mob | me (source) → you only if source and my evaluator disagree (§4) | open |
| (c) the Z-rotation sign, the rotation ORDER for compound rotations, the x-mirror, animation additivity — **on Bedrock** | your hardware, one probe entity | **you, ~15 minutes, one session (§2)** | open — this is the real Phase 0 game session |

Plus the thing you flagged: some mobs are nearly impossible to observe. That is solved by a **mob witness rig** in the test-runner pack (§3): it builds a glass pen (or a pool), summons the mob inside, holds it still facing south, and tells you where to stand. No hunting, no hills, no chasing a dolphin.

So: **your part of Phase 0 is one probe entity and, later, the rig** — both live in the PW-TestRunner pack (your 03:06 ruling: new test commands go there; it loads last and can use everything).

---

## §1 · What today's source reading settled (item a, static half) — `SOURCE`

From `EMFModelPartRoot.addAndSetVariantOfJem` + `EMFModelPartCustom` + `EMFPartData.prepare` + `EMFBoxData.prepare` (EMF is the open-source, Fresh-Animations-compatible CEM renderer; it reproduces OptiFine's visible results for the whole JEM corpus, so its maths is the reference we can read):

1. Every JEM top-level part becomes a **child ModelPart of the vanilla part of the same name**; with `attach:false` the vanilla cubes are removed, the vanilla transform (rotation point + its code-set rotation) **stays** and is applied first.
2. The custom part's own transform is `x,y,z = (−t.x, −t.y, +t.z)` and `rot = (−rx, −ry, +rz)·π/180` (invertAxis `xy`), applied **in the vanilla parent's rotated frame**. Boxes are relative to the custom part's origin after the same inversion (`x → −x−w`, `y → −y−h`).
3. Checked by hand on two vanilla template parts (numbers, Java coordinates, y down):
   - **cow body**: vanilla origin (0,5,2) rot +π/2 · template translate [0,−19,−2] → child offset (0,19,−2) → rotated by the parent's π/2 → origin (0,7,21); box [−6,11,−5,12,18,10] → y −29..−11, z −5..5 → rotated → **y 2..12, z −8..10 = the vanilla body exactly**, PROVIDED the custom part's own static +π/2 is cancelled at runtime (`this.rx = 0`, which is exactly what the Patrix polar bear writes — and why the cow's `body.rx = torad(…)` and the wolf's `body.rx = if(…, pi/2)` assign the angle outright: REPLACE semantics, the vanilla parent adds nothing but its π/2 when the JEM leaves `rx` alone).
   - **cow leg1**: vanilla origin (−4,12,7) · template translate [−4,−12,−7] → child offset (4,12,−7) → origin (0,24,0) — the custom part's origin lands on the **entity origin at ground level**, which is why Blockbench box coordinates are "absolute": under this composition they are.
4. Consequence for the tool (Phase 1): the rest bake must model the tree as *vanilla part (its rest transform) → custom part (static translate/rotate, REPLACED per axis by any animated `tx…rz`)*, not "static file + additive animation". `jem_convert.bake_rest2` already does this for rotations; the **positions** path (`tx ty tz` on a child whose parent is rotated) is the half I still have to read in `EMFModelOrRenderVariable` / `ModelPartVariableFactory` — no game needed. That reading is what will fix the fox / polar bear / horse / turtle / axolotl bakes (their JEMs assign `head.ty`, `leg1.ty = 24 + …` etc. under rotated or offset parents).

Compound rotations are real in Patrix (98 static parts in 24 mobs; 1,132 parts get two- or three-axis runtime rotation), so the Bedrock rotation ORDER (T5 below) is not academic.

---

## §2 · The Bedrock probe — your session (`pw:probe`) — PLAN

**Home:** PW-TestRunner BP **0.2.0** (adds the probe entity + the commands) and a new job-only **PW-TestRunner RP 0.2.0** (the probe's geometry, texture, animation, render controller — an entity needs an RP half; this pair is the same shape as Markers BP/RP). Attach both only for the job, the RP at the top of the RP list, the BP at the bottom of the BP list. Nothing touches the current packs.

**The probe entity `pw:probe`:** floats (no gravity, no AI, no movement, cannot be pushed or hurt, persistent), summoned by the runner **3 blocks north of you at eye height, facing SOUTH (toward you)**. Its geometry is a small "law chart", every bone a different solid colour from a colour-chart texture:

| Bone | What it is | Rotation in the file | What the verified law predicts (you stand south of it, looking north at its face) |
|---|---|---|---|
| `nose` | YELLOW flat cube on the model's front (file −z) | none | you see the yellow nose facing you — this fixes "front" |
| `left_mark` / `right_mark` | RED cube on file +x, BLUE cube on file −x | none | **T4 mirror:** RED on the **east** side = **your right**; BLUE on your left |
| `zbar` | GREEN vertical bar, pivot at its base | `[0, 0, 30]` | **T1 Z sign:** the bar's top leans **toward the red side (your right)** |
| `ybar` | ORANGE horizontal bar from the pivot toward file +x (the red side) | `[0, 45, 0]` | **T2 Y sign:** the bar's free end swings **forward, toward you**, at 45° |
| `xbar` | CYAN horizontal bar from the pivot toward the front (−z), pointing at you | `[30, 0, 0]` | **T3 X sign:** the tip pointing at you **dips down** |
| `cbar` | MAGENTA vertical bar, pivot at its base | `[45, 45, 0]` | **T5 order (X first, then Y):** the top leans **toward you AND toward the blue side (your left)**. If Bedrock applied Y first, it would lean toward you only, with no sideways lean |
| (variant `pw:t6`) | the same probe with an animation playing: `xbar` rotation `[30,0,0]` + `zbar` position `[0,8,0]` | animation | **T6 additivity:** the cyan tip dips **twice as far** (60° instead of 30°) and the green bar sits **half a block higher**. If the cyan dip is unchanged, animations REPLACE instead of add |

Each row has exactly two possible outcomes; you tell me which one you saw. That is the whole session.

**What you do (step by step):**
1. Install the two 0.2.0 packs (complete packs; 0.1.x runner removed; the saved runner state carries over — same UUID).
2. Flat world, daytime, an open spot. Stand still. Face NORTH (the sun rises on your right in the morning; or use the runner's readout — it prints your facing).
3. `/scriptevent pw:test probe` → the probe appears 3 blocks in front of you at eye height, facing you. The chat prints the six questions.
4. Screenshot **A**: as you stand (front view). Screenshot **B**: walk to the **east** side, look west at it. Screenshot **C**: fly straight above it and look down (put your crosshair on the yellow nose first so I know the facing). Three screenshots, full resolution.
5. `/scriptevent pw:test probe anim` → the animated variant replaces it. Screenshot **D** from the front.
6. Answer T1–T6 in one line each ("T1 right", "T2 toward me", …) — or just send the four shots and I read them (P9: I state what I see literally before interpreting).
7. `/scriptevent pw:test probe clear` removes it.
Fallback without the runner command: `/summon pw:probe ~ ~1 ~-3 0 0` (yRot 0 = facing south) and `/summon pw:probe ~ ~1 ~-3 0 0 pw:t6` for the animated one; `/kill @e[type=pw:probe]`.

**What I do with the answers:** T1–T6 become `VERIFIED` lines in Standard v2 §1 (today T1/T5/T6 are Blockbench-codec / documentation evidence only; T2/T3/T4 already have vanilla-file proof and get their first in-game confirmation). Any inversion flips one sign in `entity_render.transform` / `geo_preview.transform` and the converter, and every render sheet is regenerated before any mob ships.

---

## §3 · The mob witness rig (`pw:test rig`) — the answer to "impossible to observe" — PLAN

Same pack (PW-TestRunner BP 0.2.0). Purpose: put ANY mob where you can see it, still, facing a known direction, in the light, at eye level — so a conversion can be judged from three straight-on shots (P9 needs a declared facing; the rig makes the facing a fact).

- `/scriptevent pw:test rig <mob>` → builds a **5×5 glass pen, 3 high, floor of the block you stand on**, 4 blocks north of you; summons `minecraft:<mob>` at the pen's centre facing SOUTH; every tick teleports it back to the centre with rotation 0 (it cannot wander or turn; walk animations stay at rest because it never moves); prints the three camera spots (south side at eye height = front; east side = its left flank; above = top-down).
- `/scriptevent pw:test rig <mob> water` → the same pen filled with water 2 deep (glass walls keep it), for dolphin, turtle, cod, salmon, pufferfish, tropical fish, axolotl, squid, glow squid, frog/tadpole. You look in through the glass from outside at eye level — no diving, no drowning mobs.
- `/scriptevent pw:test rig <mob> baby` → summons the baby variant (`minecraft:entity_born` spawn event) for the `is_child` poses.
- `/scriptevent pw:test rig clear` → kills the rigged mob (tag `pw_rig`) and removes the pen (restores the blocks it replaced).
- Spawn events for non-default looks (a trader llama with a chest, a saddled pig/horse, a sheared sheep, a cat variant) are extra words: `rig llama chest`, `rig horse saddle`, `rig cat 3` — the rig adds the matching `spawn_event` / equips via commands; the exact list is the Phase 4 lineup's business, one row per look.
- Cost: the rig is ~200 lines of runner script (pen build/restore, hold loop, name→id table, water/baby/looks flags). Mobs that must be in water are held in the pool; mobs that fly (bat, parrot, bee, allay) are held mid-pen.

With the rig, the Phase 4 lineup for a re-converted family is: rig → 3 shots per mob (front / left / top) → PASS/FAIL in the runner. Nothing is "impossible to observe" any more; the rig never needs the wild mob at all.

---

## §4 · Java ground truth — only where needed

For the rest pose (item b) the order of evidence is: vanilla model source → my evaluator (`cem_eval.py` + `jem_convert.bake_rest2`) → **a Java screenshot when the two disagree**. If you have Java Edition with Patrix (+ OptiFine or EMF) on the laptop, the recipe is the same rig idea by hand:
- a flat creative world, `/summon minecraft:<mob> ~ ~ ~3 {NoAI:1b}` (NoAI freezes it in the rest pose; for water mobs dig a 3×3×2 pool first), stand south of it, F5 off, three straight-on shots (front / left flank / top-down), same as §2 step 4.
- That is the only "observation" Phase 0 can ask of Java, and only for the five problem mobs (fox, polar bear, horse, turtle, axolotl) — and only if the source reading leaves a gap. If you do not have Java, say so and I settle (b) from source alone and flag the residual `MODEL` lines.

---

## §5 · The tool programme with your answers folded in — PLAN

**Your four answers → decisions:**
1. **Probe session: yes** → Phase 0 = §2 (+ §3 rig) built first, one delivery: PW-TestRunner BP 0.2.0 + RP 0.2.0.
2. **Everything fixed if it needs it** → Phase 4 covers **every** RP-07 patrix geometry (39) and then RP-06 (hostile mobs; its build dir is not on disk — I pull the 1.4.6 pack from your Drive copy first and audit it the same way), worst-first by the §5 audit numbers: aquatics (turtle, salmon, pufferfish ×3, dolphin, cod, axolotl) → equines (horse, donkey, mule) → wolf / fox / polar bear → goat, panda, rabbit → the ≤ 1-cube set (llama, pig, cat, sheep, camel, zombified piglin) last — those are re-emitted by the tool too so that every mob has the same provenance, but they ship only if the sheet shows a visible difference.
3. **Convert and double-check all layers, Patrix quality** → the converter takes the whole JEM set per mob: `<mob>.jem` + `<mob>_baby`, `_saddle`, `_chest`, `_decor`, `_armor`, `_collar`, `*_layer` files (Patrix ships 152 JEMs + 22 `.properties`); each extra layer becomes a render-controller pass with `part_visibility` driven by the Bedrock query that matches the Java condition (`query.is_chested`, `query.is_saddled`, `query.is_sheared`, `query.has_armor`, variant/mark colours), and the sheet shows every layer on and off.
4. **Bone names: Bedrock requirements first, otherwise mine** → the rule: a bone keeps the vanilla Bedrock name when a vanilla system addresses it by name — `head` (look-at, lead attachment), `body` (riding/lead offsets, the `-this` shim), `leg0..leg3` (quadruped.walk), `rightArm/leftArm/rightLeg/leftLeg/rightItem/leftItem` (humanoid/illager item holding), `tail`/`mane`/`neck` where vanilla animations touch them, chest bones `chest1/chest2` (llama), `saddle`, `bag1/bag2` (horse); everything else keeps the Patrix name so a diff against the JEM is readable. The map is written per mob in the tool's output and in Standard v2.

**Phases (from the research doc, unchanged except where the answers touch them):**
- **P0 probe + rig** (S/M, your session) → verified sign/order/mirror/additivity lines.
- **P1 `jem2bedrock.py`** geometry + rest bake (M): gates A (vanilla pairs stay 240/192/12) · B (pose sanity) · C (contact sheet per mob: static | rest | current ship | new).
- **P2 animation translator** (L): CEM → Molang, replay gate ±1° on 20 sampled states; the rig lets you witness walk/idle on the real mob afterwards.
- **P3 textures** (M): LabPBR `_n/_s` → MERS per #156, texture sets per variant, decor layers.
- **P4 re-conversion** by family, complete-pack releases (RP-07 1.5.x, then RP-06), each with its sheet and its rig lineup rows.

**Standing rules that apply:** complete packs only (22:32); pack-home law (the runner pair is the one sanctioned exception); Patrix Java porting permitted; CC0 for anything authored; every claim `shipped, awaiting verification` until you confirm.

---

## §6 · What I need from you to start

1. **GO for P0** — PW-TestRunner BP 0.2.0 + RP 0.2.0 (probe + rig). Or "probe only" if you want the rig later.
2. **Java on the laptop: yes / no?** (only changes §4; no is fine.)
3. Nothing else — P1–P4 run after P0's answers, plan-first per phase as usual.
