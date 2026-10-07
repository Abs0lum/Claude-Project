# HANDOFF — 2026-10-03 00:48 CT — V6 CIVITAS DELIVERED

Supplement to `HANDOFF-2026-10-03-V6-CIVITAS.md` (the brief + what V6 is). Everything below is delivered; nothing is verified by him yet (P1: the witness round decides).

## Delivery — gofile folder `https://gofile.io/d/DoHcDxGx` (AR-V6-CIVITAS-2026-10-03; stranger check PUBLIC)
| File | Bytes | md5 |
|---|---|---|
| BP-02-AbsolutRealism-Tectonic-BP-v1_3_207.mcpack | 5,504,253 | d7997a6bf1edd71d5168c0a226406f92 |
| RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_45.mcpack | 151,535,001 | f43238f32163d77b0565ced5a06c5799 |
| RP-08-AbsolutRealism-Items-RP-v1_4_14.mcpack | 108,465,777 | 763c35e171863f6506e31b65931fbef8 |
| PW-TestRunner-BP-v0_5_15.mcpack | 310,093 | b8682f5004caf28388f0dd22a2025779 |
| HANDOFF-2026-10-03-V6-CIVITAS.md (the brief) | 8,785 | a8f7ef41a3726901c34d715901e01c38 |
Every archive == its build dir (packager proof), server md5 == local, browser download byte-exact. Build dirs are now FROZEN: bp02-207, rp07-1445, rp08-1414, testrunner-0.5.15.

## Gates passed before shipping
- Server evolution runs 0.0.11 → 0.0.17 (`tools/civ_evo_probe.py`): final gate 0.0.17 — floating 0, stoop failures 0, 0 script errors, two cities + a pier village, roads 103 / 153 cells, state 53,985 chars in chunked properties with 0 failed saves.
- Static: 126 scripts syntax-clean; manifests / versions consistent; recheck fix-round gates (ownership O1 0, animation resolve 0, entity precedence 0 losses, Molang 0, format versions 0); TestRunner mock suite 348/348; land / road / economy / smoothing node tests 14 + 13 + 9 + 2 + 21 all passing.
- BDS load gate: BP-01 1.3.35 + BP-02 1.3.207 + BP-03 1.3.34 + Markers 0.2.1 + TestRunner 0.5.15 together → server started, 0 ERROR.

## Install order on the phone (host) — replaces 1.3.206 / 1.4.44 / 1.4.13 / 0.5.13
RP side unchanged except RP-07 1.4.45 and RP-08 1.4.14. BP side: BP-02 1.3.207; PW-TestRunner BP 0.5.15 at the bottom. Then `/scriptevent pw:test start p22`.

## Open after delivery
- GS-1: two street body cells one block below their profile in the forest village (D-C500) — a per-cell lay log in the next probe; cosmetic.
- His rulings pending: daughters at 170–230 (vs 120–200); anything from the witness round.
- Next work: trees (root blocks → spruce-log census → state migration → falling models → TREEGROW), then the CIVITAS backlog (yard ramps, cross-lanes, wagons, cellars, ruins).
