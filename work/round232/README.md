# ROUND 232 — BP-02 1.3.232 source (GitHub Claude Code session, 2026-10-07)

Source only: **nothing here is packaged or witnessed.** The pack is built in the cloud workspace (it holds `_build/bp02-231`
and the staged structures); this folder is the hand-over.

## 1. How `bp02-232-src/` was made
Base = the shipped round-231 source `work/inbox-2026-10-07-1714/bp02-231-src/` (33 suites green). Four worker patches applied
in this order, each first verified alone on a fresh base:

| Order | Patch | Items | Files |
|---|---|---|---|
| 1 | `INN/INN.diff` | #14 rev: existing inns KEPT (r1 = the 1.3.230 inn, byte-exact entries), new inns = `pw:mvv_inn_{a..d}_r2` (12 rooms: 8×2 + 4×4 beds = 32, 1-block gaps) | pw_civ_buildings.js, pw_civ_clock.js, tests/test_shifts.mjs, tests/test_inn24.mjs |
| 2 | `RAMP/RAMP.diff` | #7 plateau cutMax/fillMax **9** (+ per-template box-clear cap) · #5 road 8-part ramps `pw:ramp_cobble_8_e1..e8` laid block by block (bench roads, gate stubs; climbing/band legs stay 4-part; `ROAD4_EXTRA = 48`) | pw_civ_clock.js, pw_civ_plan.js, pw_civ_streets.js, tests (plateau, roadramp8 + fixture) |
| 3 | `PALACE/PALACE.diff` | #21 Palace II hook (Parts A–C amended: saved 2×2 palaces keep their model, quarter-at-a-time survey, fail-safe to 2×2 when any of 16 entries / 80 stage structures is missing) + Part D `pw_civ_palace_secrets.js` (doors stay shut; lord/noble/child/guard/servant moved only when nearer; lore skipped) + ≥2 lord beds filled per pass | pw_civ_clock.js, pw_civ_court.js, pw_civ_court_data.js, pw_civ_palace_secrets(.js/_data.js), pw_civ_walk.js, tests (court, palace_hook, palace_secrets) |
| 4 | `HOMES/HOMES.diff` | #29 FAMILY ROOM rule (families whose beds can't sleep them take / swap into a home that can; ≤ 2 families a day; `FAMILY.on`) + `/scriptevent pw:clock homes` · #28 crossroads first (`PLAN.crossFirst`) | pw_civ_people.js, pw_civ_clock.js, pw_civ_plan.js, tests (homes, cross) |

Manual merge fixes (the only edits not from a worker diff):
1. `pw_civ_clock.js` header: HOMES hunk #1 (two comment lines documenting `homes`) collided with PALACE's comment in the
   same spot → inserted after the PALACE lines. Comment only.
2. `tests/test_homes.mjs:64`: HOMES measured the 231 inn (32 beds); after INN the r1 inn has 4 and r2 has 32 → the
   assertion now checks both. Test-only.

Result: **38/38 suites fully pass**, `node --check` clean on every script (`MERGED-TESTS.txt`; runner
`work/test-harness/run_civ_tests.sh`, strict: a suite counts only when every check passes). Script md5s:
`MD5SUMS-scripts-232.txt`.

## 2. What the 1.3.232 BUILD needs besides these scripts
| What | Where | Note |
|---|---|---|
| Copy every `*.js` of `bp02-232-src/` (not `tests/`, not `main.packed-231.js`) over `_build/bp02-232/scripts/` (copied from bp02-231) | here | `main.js` source differs from the packed 231 one only by the build stamp — keep the builder's stamping |
| New inn r2: 32 structures | `INN/files/BP-02/structures/pw/` (+ `MD5SUMS-r2.txt`) | `structures/pw/mvv_inn_{a..d}_r2.mcstructure` + `stages/` |
| Restore the r1 inn: 32 structures from BP-02 1.3.230 | `INN/files/restore-r1/` (+ `MD5SUMS-r1-from-1.3.230.txt`) | overwrite the 231 r1 files |
| PALACE II: 80 stage structures (required) + 16 finished (recommended) + 16 table entries | cloud `_staging/palace231/` | merge entries with `PALACE/files/palace2_merge_buildings.py`; list in `PALACE/files/PALACE-STRUCTURES.txt`; **~158 MB** — see question P3. Without them the build is still safe (2×2 fallback). |
| Cottage loft beds (#29 structures) | `HOMES/HOMES-tools-civgen.diff`, `HOMES-tools-civ_roster.diff` | design only; regenerate `cottage_s`/`cottage_m` ONLY after his answer (H3) |
| Generator diffs | `INN/INN-inn_v2.py.diff`, `INN/INN-civ_variants.py.diff`, `PALACE/files/palace2_hookdata.py.diff`, `ACAD/ACAD-acad2v2_layout.py.diff` | apply to `tools/` in the workspace |
| Manifest | header + modules → [1, 3, 232]; @minecraft/* string deps untouched (H-53) | builder refuses to reuse a version |
| Gates | BDS gate + `gate_check.py`, `geo_ref_check.py`, permutation count (SLIM stays), `js_dupcheck`, all suites | then package, md5-verified Drive upload, sync |

## 3. In-game tests (for the checklist)
- Inn: `/scriptevent pw:clock plot inn` → `skip 7` → `status` names `pw:mvv_inn_a_r2`; existing inns unchanged (no " r2").
- Roads: `/scriptevent pw:clock bench` (chronicle "(N 8-part ramp(s), M 4-part)"), `/scriptevent pw:clock roadramps` (lists
  each ramp, type, facing) — only roads planned after the update.
- Plateaus: `/scriptevent pw:clock frontage cottage_m` on a hill town.
- Palace: `/scriptevent pw:clock palace check`, `… palace ends`, `… palace test H1-LORD`, then `… palace test H1-LORD ordinary`.
- Homes: `/scriptevent pw:clock homes` (beds vs families, today's family moves).

## 4. Open questions (answers outrank this text)
INN: did 1.3.231 ever lay an inn in a kept world (would need a one-time repair) · room mix 8×2 + 4×4 OK · ladders or stairs ·
"Rent a bed" says "full"? · RAMP: dial 48 (or 12/24) · bench roads + gate stubs = "roads", climbing legs = "switchbacks"? ·
keep the box-clear cap? · PALACE: one-way direction (doors open hidden→public) · two lord households or one couple · ship
PALACE II inside BP-02 (~281 MB) or a companion BP · children cap 2 · ACAD: Q-A..Q-D (`ACAD/ACAD.md` §9) + Q1–Q10
(`ACAD/ACAD-UPGRADE.md` §7) · HOMES: Q1–Q7 (`HOMES/HOMES.md` §7).
