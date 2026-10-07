# P0 WITNESS READS — 2026-09-27 (Phase 0 run, 176 screenshots, all 35 steps)

**Status:** the complete read of Abs0lum's Phase 0 run (PW-TestRunner 0.2.0, RP-07 1.4.11, extreme_hills, 19:19–19:38 CT). Ledger: **176/176 viewed at full resolution** (`_logs/intake_ledger.md` S001–S176; native crops and literal reads in `_intake/p0-shots/reads.md`). Comparison sheets ("his shot | our file from the same side | my read") in `_design/p0-witness/` (21 sheets, delivered to outputs). Journal D-C259. Companion to `MOB-CONVERSION-RESEARCH-2026-09-27.md` and `MOB-CONVERSION-PHASE0-PROTOCOL-2026-09-27.md`.

**His asks answered here:** (19:49) "thoroughly investigate EVERY screenshot… present me my screenshot with your assumption as an image" → §2 + the sheets; (21:29) "some textures were vanilla, some entirely magenta" → §2 columns *texture drawn* and §3 M2–M4; (21:31) "this ALSO occurred on tests recorded as pass — all need to be checked" → every row of §2 is a read, PASS or FAIL. The log question → §5. **No rerun needed** (PASS meant "shots taken" by design; the REPORT block was complete).

---

## 1 · The probe (q1 / q2) — the rotation law is now witness law

Six shots (191958 top-N, 192004 top-S, 192145 front, 192149 west side, 192156 east side, 192205 top). Every predicted row held, camera facing stated on each read:

| row | prediction (probe faces SOUTH, you look NORTH) | seen |
|---|---|---|
| mirror | RED (file +x) on YOUR RIGHT (= east) | red on the right / east in the top view ✔ |
| T1 Z sign | green bar [0,0,30] leans toward RED | leans east ✔ |
| T2 Y sign | orange bar [0,45,0] free end toward YOU | top view: bar runs to the SOUTH-EAST ✔ |
| T3 X sign | cyan bar [30,0,0] tip DIPS | dips ✔ (front + side) |
| T5 order | magenta [45,45,0] toward you AND to your LEFT | tip south-west and higher ✔ (X applied first) |
| T6 additive | animated: cyan ~60°, green +½ block | ~60° (side read 56°), green +0.61 block ✔ |

**L-ROT-DIR: CONFIRMED in-game.** Nothing in the 31 mob reads contradicts it; every "wrong" mob traces to a file or wiring cause (§3).

---

## 2 · Every mob — what was drawn, from which files, and why

Columns: **geometry drawn** (which file the engine actually used) · **texture drawn** (Patrix / vanilla / magenta) · **verdict** · **mechanism** (§3) · **fix class** (W = wiring only, RP-07 1.4.12; C = re-conversion, P1 tool; R = rig/runner; — = none).

| step | mob | his verdict | geometry drawn | texture drawn | verdict | mech | fix |
|---|---|---|---|---|---|---|---|
| r01 | turtle | PASS | ours `turtle.patrix` — flat 3-slab shell, plate flippers, **zero rotations** | Patrix | shape is a flattened reconstruction, not the dome | M5 | C |
| r02 | salmon | PASS | ours `salmon.patrix` | Patrix | faithful, right way up (small-variant scale) | — | — |
| r03 | pufferfish | PASS | ours small/medium/large | Patrix | faithful (calm + puffed) | — | — |
| r04 | dolphin | PASS | ours `dolphin.patrix` | Patrix | faithful | — | — |
| r05 | cod | PASS | ours `cod.patrix` | Patrix | faithful (small variant) | — | — |
| r06 | axolotl | PASS | ours `axolotl.patrix` — **leg plates ABOVE the body** (y 1..7 vs body −2..2) + duplicate leg bones | Patrix | file defect (Y inversion missed on the legs) | M5 | C |
| r07 | horse | PASS | ours `horse.patrix` at 0.5 scale (**a foal** — random baby spawn) | Patrix | coherent; adult unseen | rig | R |
| r08 | donkey | PASS | ours `donkey.patrix` | Patrix | **chest boxes always visible** (no `part_visibility`) | M1 | W |
| r09 | mule | PASS | ours `mule.patrix` (foal) | Patrix | chests always visible | M1 | W |
| r10 | wolf | PASS | **`geometry.wolf_anim`** (vanilla-shaped foreign model; `wolf.patrix` unused) | Patrix 512×256 `wolf.png` read through 64×32 UVs → one eye on the face, plain snout | 4 missing animations in the log | M1 | W |
| r11 | fox | PASS | **`geometry.fox_fa`** — body cube unrotated (stands on end), tail floating; `fox.patrix` unused | Patrix | wolf animation set borrowed | M1 | W |
| r12 | polar bear | PASS | **`geometry.polarbear.bma2`** (vanilla-shaped); `polar_bear.patrix` unused | **VANILLA** (`textures/entity/polarbear` is not in RP-07; `bear/polarbear.png` unused) | plain white vanilla bear | M1 | W |
| r13 | goat | PASS | `geometry.goat_fa` (a vanilla-llama copy) | **MAGENTA** from every side (4/4 shots) | material/RC mismatch | M2 | W |
| r14 | panda | PASS | `geometry.panda_fa` — body unrotated (upright block), head hanging off the front; `panda.patrix` unused | Patrix | polar-bear animations | M1 | W |
| r15 | rabbit | PASS | ours `rabbit.patrix` | Patrix | faithful | — | — |
| r16 | llama | PASS | ours `llama.patrix` | Patrix | faithful | — | — |
| r17 | trader llama | PASS | ours (1.4.11) | Patrix + blanket/strap | **1.4.11 fix confirmed** | — | — |
| r18 | pig | PASS | ours `pig.patrix` | Patrix | faithful (body yaw swung in the pen) | — | R |
| r19 | cat | PASS | **`geometry.cat`** (vanilla-shaped 64×32; `cat.patrix` unused) | Patrix 512 calico (UV-compatible, so it looks right) | tame textures are `.tga` referenced as `.png` | M1 | W |
| r20 | ocelot | PASS | `geometry.cat` | Patrix 512 ocelot | as the cat | M1 | W |
| r21 | sheep | PASS | ours `sheep.patrix` + wool | Patrix | faithful | — | — |
| r22 | camel | FAIL "magenta?" | `geometry.camel_fa` (llama copy) | **MAGENTA** 6/6 shots | as the goat | M2 | W |
| r23 | zombified piglin | FAIL "invisible" | **never spawned**: `RIG spawn FAILED minecraft:zombie_pigman: EntitySpawnError: Attempting to spawn a hostile m…` | — | hostile spawns blocked in the world (Peaceful / setting); AND our id is dead (`zombified_piglin` vs Bedrock `zombie_pigman`) | M3 + rig | W + R |
| r24 | cow | FAIL "not married" | ours `cow.patrix` | Patrix | faithful to the file (neck block under the head's rear, udder rear-underneath) — **which joint?** (sheet) | M5? | ask |
| r25 | mooshroom | FAIL "same as cow" | ours `mooshroom.patrix` | Patrix | faithful (head 1 cube below the body top) | M5? | ask |
| r26 | chicken | FAIL "vanilla textures" | **vanilla** cold-variant BABY geometry | **VANILLA** 64×32 cold art | our definition is bypassed (min_engine_version tie) | M4 | W |
| r27 | frog | FAIL "old issues" | ours `frog.patrix` — body slab missing its −45 Y (head has it), loose hand/foot plates | Patrix **with N/E/S/W magenta marker tiles painted in all 3 textures** | our own labelling leftovers | M5 | W + C |
| r28 | tadpole | FAIL "vanilla" | ours `tadpole.patrix` | Patrix (tapered tail) | faithful — Patrix's tadpole IS the vanilla silhouette | — | — |
| r29 | squid | FAIL "fill in the blanks" | ours: one body cube + **8 tentacles at one origin/pivot** (a single post); vanilla's fan animations replaced by empty shims | Patrix | placeholder file | M5 | C |
| r30 | glow squid | FAIL "same" | as the squid | Patrix | placeholder file | M5 | C |
| r31 | tropical fish | FAIL | **vanilla `geometry.tropicalfish_b`** | our greyscale 128× Patrix sheets **tinted by vanilla** (blue/red) | our id is dead (`tropical_fish` vs `tropicalfish`) | M3 | W |

Counts: faithful-and-Patrix 11 (r02 r03 r04 r05 r15 r16 r17 r18 r21 r28 + r07 as a foal) · wiring faults 13 (r08 r09 r10 r11 r12 r13 r14 r19 r20 r22 r23 r26 r31) · file/conversion defects 5 (r01 r06 r27 r29 r30) · to confirm with him 2 (r24 r25).

---

## 3 · The five mechanism families (none is the rotation law)

**M1 — wiring: the client entity points at the wrong assets.** Old vanilla-copy `*.entity.json` files (format 1.8/1.10) name vanilla-era geometry ids (`geometry.wolf_anim`, `fox_fa`, `panda_fa`, `polarbear.bma2`, `geometry.cat`) while the Patrix conversions (`wolf.patrix`, `fox.patrix`, `panda.patrix`, `polar_bear.patrix`, `cat.patrix`) sit unused in the same pack. The polar bear's texture path (`textures/entity/polarbear`) does not exist in RP-07, so the stack resolves it to vanilla's 128×64 art. Wolf/fox reference nine animations no pack provides (the log's `can't find` lines). Donkey/mule RCs lack `part_visibility` for `chest*`.

**M2 — material vs render controller.** `goat.entity.json` and `camel.entity.json` are copies of vanilla `llama.entity.json` (llama.v1.8 animations, eyebrown/Mouth/chest bones, material **`llama`**). Vanilla's llama material samples three textures (its RC binds `Array.base[...]`, a decor texture and `Texture.decor_none`); the vanilla `controller.render.goat` / `.camel` they point at bind ONE (`Texture.default`). Unbound samplers draw the engine's magenta placeholder → the whole mob is magenta. Our llama (material `entity_alphatest`, one binding) is fine. *Inferred from the RC bindings + the observation (entity.material is not in bedrock-samples); the 1.4.12 witness settles it.*

**M3 — dead identifiers.** Bedrock's ids are `minecraft:tropicalfish` and `minecraft:zombie_pigman`; ours are `tropical_fish` / `zombified_piglin` → our definitions never bind. The tropical fish is then vanilla's definition drawing vanilla's B geometry and **tinting our greyscale 128× Patrix sheets** (they sit on vanilla's paths) with the two-colour system = the blocky red/blue fish in his 8 shots. The piglin never spawned in this run (hostile spawns blocked); when it does, RP-06's `zombie_pigman` definition will draw.

**M4 — definition precedence (chicken).** What was drawn is vanilla's COLD variant (extreme_hills is a cold-variant biome), a BABY (head as tall as the body = vanilla's baby geometry) with vanilla 64×32 cold art (texel test; beige beak + red wattle match the vanilla render, not the Patrix cold sheet — sheet r26). Our `chicken.entity.json` has no climate logic (it would have drawn the temperate white Patrix chicken), so vanilla's definition is the one in effect although RP-07 is attached. Both files carry `min_engine_version 1.12.0`; every RP-07 definition that DID win carries `1.21.0` (cow, pig, sheep, llama, …) or none (wolf, cat, fox — classic override). Candidate rule: an equal `min_engine_version` loses to vanilla's. Fix: `1.21.0` + a rebuilt chicken on the 1.21.70 climate scheme with the three Patrix chicken geometries already in the pack.

**M5 — conversion / reconstruction defects in files that ARE in effect.** Turtle (flat, no rotations), axolotl (legs above the body), frog (body slab lacks Patrix's −45 Y; loose hand/foot plates; **magenta N/E/S/W marker tiles painted into all three frog textures — 1,013 px each**), squid + glow squid (8 co-located tentacles, empty `squid.move/rotate` shims → one post), cow/mooshroom (faithful; the neck block under the head's rear is the Patrix placement — waiting for his pointer).

Also found (P11 census of the stack, `_logs/p0_rp07_shadowing.json`): RP-06 1.4.6 and RP-08 1.4.6 both ship vanilla-copy `models/entity/{cat,chicken,llama,panda_fa,polar_bear,wolf}.geo.json` and 64×32 cat/chicken PNGs on RP-07's paths. The calico cat drew at 512× (texel test), so RP-07 is above them in his current order — but any reorder flips the cat/chicken art. Dead weight to purge.

---

## 4 · What to do about it (for his GO — nothing built tonight)

**A. RP-07 1.4.12 — wiring build (13 mobs, no re-conversion, one pack):** donkey/mule `part_visibility {chest*: query.is_chested}` · wolf/fox/panda/polar bear/cat/ocelot → their shipped `.patrix` geometries + own RCs + textures (wolf 18 Patrix variants; cat tame `.tga` → `.png`) + the missing animations dropped · goat/camel → material `entity_alphatest` + `goat.patrix` / `camel.patrix` + `controller.render.pw_goat/pw_camel` (already in the pack) · chicken → `min_engine_version 1.21.0`, the 1.21.70 climate pre_animation, `geometry.chicken.patrix` / `warm_chicken.patrix` / `cold_chicken.patrix`, textures on RP-07-only paths · tropical fish → `minecraft:tropicalfish` + the two-colour RC (`query.color`/`query.color2`) over the 14 Patrix greyscale sheets + Patrix a/b geometry · zombified piglin → `minecraft:zombie_pigman` · frog textures → marker tiles removed. Gate additions (verify_rp07): ids ∈ Bedrock's set, every texture path resolves inside the pack, material sampler count == RC bindings, `min_engine_version ≥ 1.21.0`, a textured render of every P0 mob from the three rig views.

**B. P1 converter (the tool programme, research doc §7):** first feed turtle, axolotl, frog, squid, glow squid; then the >5-cube-offset set from the R2 audit (horse, donkey, mule, pufferfish m/l, polar bear, salmon, wolf).

**C. TestRunner 0.2.1:** spawn ADULTS (`minecraft:ageable_grow_up` after spawn), print spawn failures on the bar ("hostile spawns are off — set Easy for this step"), re-melt ice in the pool every tick, drop the big step title 1 s after step start (it covered 2/3 of the front shots), verdict semantics **PASS = looks Patrix AND coherent**, quick tags `vanilla?` / `magenta?` / `parts?`.

**D. BP-02 1.3.189:** BIGCANOPY-STATS cadence 100 t → 1200 t + `/scriptevent pw:stats off` (the log flood).

**E. RP-06 / RP-08:** purge the vanilla-copy mob files that shadow RP-07 by pack order.

---

## 5 · The log question

The content-log panel copies about 200 lines; everything older scrolls out. The runner's REPORT block is regenerated from saved state on demand, so **`/scriptevent pw:test report` right before "Copy to Clipboard"** always gives the complete block — nothing was lost this run (#01–#35 were all present). The flood is BP-02's `BIGCANOPY-STATS` line every 5 s (D above); the runner's own lines are already one per event. Bundling the runner's lines further would hide the per-step `RIG …` line that told us the piglin never spawned — keep those.

---

## 6 · Questions for Abs0lum

1. **Cow / mooshroom "not married to parent sibling correctly"** — on sheet r24, is it (a) the neck block hanging under the head's rear, (b) the head's top flush with the body top, (c) something else? Point at it and I re-derive that joint from the Patrix rest pose.
2. **Tadpole "vanilla"** — the shape (a box head + a fin tail) is Patrix's own design; the 128× art is what drew (sheet r28). Do you want a richer tadpole than Patrix ships, or is this closed?
3. **GO for A (RP-07 1.4.12 wiring) + C (runner 0.2.1) + D (BP-02 stats)?** They are independent of the converter and turn 13 mobs Patrix-quality in one pack; the converter (B) then handles the five real conversion defects.
4. Hostile spawns: the piglin step needs the world on Easy (or a spawn rule that allows hostiles); say which and the runner will say so on the bar.
