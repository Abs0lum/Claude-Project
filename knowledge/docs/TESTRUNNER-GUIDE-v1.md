# PW TEST RUNNER — GUIDE v1 (PW-TestRunner BP v0.2.0 + RP v0.2.0 · 2026-09-27 · D-C249 / D-C254 / D-C257)

**v0.2.0 adds PHASE 0** — see the section at the end: `start p0` walks the rotation-law probe and every RP-07 mob in the witness rig. The witness lineup (`start`) is unchanged.
A job-only behaviour pack that walks the witness lineup for you. It sets each step up, tells you what to look at, waits, records your verdict, and leaves a results block in the content log for Claude. Standing home for every future in-game test command.

## Install (once per world)
1. Download `PW-TestRunner-BP-v0_1_2.mcpack` from the delivery folder and open it (it imports like any pack). Updating from 0.1.1: activate 0.1.2, remove 0.1.1 from the world — the saved run carries over (`/scriptevent pw:test resume` if the clicker is missing).
2. World → Edit → **Behavior packs** → **Available** → activate **PW Test Runner BP v0.1.2**.
3. Move it to the **BOTTOM** of the Active list (lowest priority: it can never override our packs; its scripts still see every block, item and entity the other packs register).
4. Cheats ON (already on). Content log GUI ON: Settings → Creator → Enable Content Log GUI.
5. Play. The content log shows `[PW-VERSION] PW Test Runner BP v0.1.2 - 48 steps - /scriptevent pw:test help`.

## A run
1. Stand where you want to test (creative). Type: `/scriptevent pw:test start`
   - It logs a **census** of what the other packs registered (furniture, hearth, slabs, roofs, ramps, seat entity, markers, hatch lid, StripMine firefly) — a missing pack shows here before you look for anything.
   - Daylight and weather cycles are switched **off** for the run (restored at the end).
   - A **CLICKER** (named stick) appears in hotbar slot 9. It cannot be dropped.
2. Each step: a title flashes, the bar at the bottom stays: `5/48 BUSH FIREFLIES AT NIGHT · you are in: forest · tap the clicker`. **`you are in:` is information — the biome you are standing in — never a requirement.** Chat shows the first line of what to look for. Items / time / weather / llamas are set up for you.
3. Look, take screenshots (the step number is on screen), then **tap the clicker in the air** → menu:
   - **PASS** / **FAIL** — records and moves to the next step.
   - **PASS + note** / **FAIL + note** — a text box first ("what did you see?").
   - **Repeat setup** — the time/weather/items again.
   - **Build props here** (firefly steps only) — places a bush 3 blocks ahead and/or spawns 12 fireflies there. Nothing is placed unless you press it.
   - **Skip** · **Back** · **Report so far** · **Stop the run**.
4. Relog any time: the run continues where it was (`/scriptevent pw:test resume` if the clicker is missing).
5. After the last step (or **Stop**): the results block is written and the cycles restored.

## Getting the results to Claude
Settings → Creator → **Content Log History** → **Copy to Clipboard** → paste into the chat (or the Drive). Every runner line starts with `[PW-TEST]`; the block ends with `[PW-TEST] END`. Times in the lines are **UTC** (your phone's screenshot clock is UTC − 5).
Any time later: `/scriptevent pw:test report` re-writes the block from the saved run.

## Commands (`/scriptevent pw:test …`)
`start` · `start!` (restart) · `resume` · `pass [note]` · `fail [note]` · `skip [note]` · `next` (no verdict) · `note <text>` · `back` · `goto <id|n>` · `repeat` · `props` · `report` · `stop` · `list` · `where` · `clear` (empty inventory, creative only) · `reset` (forget the run) · `help`

## The 48 steps (ids)
s0 log on load · **0u** u1 bush by day · u2 bush fireflies at night · u3 VV glow · u4 swamp fireflies · u5 density · u6 old fireflies (memory) · **0v** v1 forest day · v2 forest night · v3 rain · v4 thunder · v5 clear + sky-fog line · v6 no fireflies outside swamps · v7 diag commands · v8 relog in rain · **0w** w1 build the smoke room · w2 smoke fills · w3 smoke clears · **0x** x1 migrate · x2 seat marker in a chair · x3 furniture into a marked cell · x4 hide/show · x5 hatch · **0y** y1 table corner + mantel end · y2 heights · y3 trader llamas · y4 chimney plume · **0z** z1 all 12 pieces · z2 collision · z3 sitting · z4 tables join · **0a** a1 a2 a3 purge checks · **0** e1 E2 · **0b** b1 beds · b2 furnaces/redstone · b3 stone · b4 signs/boats · **1–10** h1 hearth walls · h2 chute · h3 fire · h4 cornerpost probe · h5 ridge caps · h6 ramps + snow · h7 hearth cycle · h8 Santa test · h9 campfire smoke

## Flat world (one biome everywhere — yours is extreme_hills)
Only four steps care about the biome, and each one now says what to expect in a flat world: **u4** swamp fireflies → press **Build props** (the particle itself) and PASS/FAIL the look with a note "props only" (the swamp spawner waits for a real swamp); **v1** forest by day → in extreme_hills expect **wind** (heavy or howling), about one every 30 s; **v2** forest at night → **howling wind + an occasional wolf**; **v6** no fireflies outside swamps → your flat world counts. Everything else is biome-free.

## What it cannot do (v1)
Read other packs' log lines (copy the whole log — it is all there) · see resource packs · find a swamp for you (`/locate biome swamp` + `/tp`; the bar shows your biome) · build the smoke room (v2 candidate).


## PHASE 0 (v0.2.0) — the probe and the mob witness rig (`/scriptevent pw:test start p0`)

**Install (both packs, complete packs):** download `PW-TestRunner-BP-v0_2_0.mcpack` and `PW-TestRunner-RP-v0_2_0.mcpack`, open each so Minecraft imports it. Edit World → **Behavior Packs**: remove the old Test Runner (0.1.x), add **PW Test Runner BP v0.2.0** and keep it at the **BOTTOM** of the active list. **Resource Packs**: add **PW Test Runner RP v0.2.0** at the **TOP** of the active list (it only adds one entity, it overlaps nothing). Your saved run from 0.1.x carries over (same pack uuid).

**Before you start:** an open flat spot in daylight with nothing for ~8 blocks to the north; turn the HUD position readout ON (Settings → Video → Position) so every screenshot carries the coordinates. Face NORTH — **the bar at the bottom shows `facing NORTH`**; use that, not the compass (a compass points to the world spawn, not north).

**The run:** `/scriptevent pw:test start p0` → 35 steps. Every step **sets itself up by itself** the moment it starts (a probe or a mob appears in front of you) and the chat + the clicker menu tell you which screenshots to take. Take them, tap the clicker, **PASS = shots taken** (FAIL + note only if the setup itself was wrong: nothing appeared, the mob escaped, the pen is wrong). The next step clears the previous probe/pen automatically.

| Step | What appears | Screenshots |
|---|---|---|
| q0 | nothing — stand, face north, HUD on | — |
| q1 | the colour chart (`pw:probe`) 3 blocks north at eye height, its yellow nose toward you | **A** front (as you stand) · **B** from the EAST side looking west · **C** from above looking down, crosshair on the yellow nose |
| q2 | the same chart with its animation playing | **D** front |
| r01–r31 | one mob per step, held still in an invisible pen 5 blocks north, facing SOUTH (toward you); the 10 water mobs in a 2-deep pool — look in from outside | **1** front (as you stand, looking north) · **2** left flank (walk to the EAST side, look west) · **3** top (only where the step asks: the five problem mobs + the water mobs) |
| q9 | everything removed, ground restored | — then upload all shots to the Drive (Packs → Screenshots-P0 or any folder — tell Claude the name) and copy the content log |

Order of the mobs: turtle · salmon · pufferfish (step up close to make it puff) · dolphin · cod · axolotl · horse · donkey · mule · wolf · fox · polar bear · goat · panda · rabbit · llama · trader llama · pig · cat · ocelot · sheep · camel · zombified piglin · cow · mooshroom · chicken · frog · tadpole · squid · glow squid · tropical fish.

**What the chart answers (q1/q2)** — compare with `p0-probe-predicted.png`: RED cube on your RIGHT? · GREEN bar's top leaning toward the red side? · ORANGE bar's free end coming toward you? · CYAN bar's tip (pointing at you) dipping DOWN? · MAGENTA bar leaning toward you AND to your left? · animated: CYAN dips twice as far, GREEN half a block higher? Six yes/no answers, or just the four shots.

**Commands that matter here:** `repeat` (rebuild the current probe/pen) · `skip` · `back` · `goto r12` · `stop` (removes the probe and the pen, writes the report) · `reset` (forgets the run, removes everything). If a mob is not where it should be: `repeat`. If a pen is ever left behind (a crash mid-step): start any P0 step or `reset` — the runner remembers every block it replaced and restores it.

**Java later:** only for the five problem mobs and only if the source reading leaves a gap — the protocol §4 has the NoAI recipe.
