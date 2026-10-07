# HANDOFF — 2026-10-01 — STANDARD ROUND shipped for the full mob parade

**Authoritative CURRENT-STATE as of 2026-10-01 afternoon (CT).** Appends to HISTORY after the 09-30 handoffs.

**REVISION 2 (17:29 CT 10-01) — supersedes the Ship status table below for what is INSTALLED now.**

### Installed now (his log 4, 16:49: ZERO errors — all content-log fix rounds CONFIRMED on his hardware)
Latest of each pack, newest delivery first (each delivery = its own gofile folder; server md5 == local; browser byte-exact):

| Pack | Version | md5 | Delivered |
|---|---|---|---|
| RP-07 Neutral Mobs | 1.4.43 | 5d73a45d | qJvSDvKf (16:4x) — blobfish `lead` locator on the shared bone |
| RP-06 Hostile Mobs | 1.4.28 | 5908753b | 46dcyikV (15:59), re-sent in qJvSDvKf (his phone import had been short) |
| RP-04 Basic | 1.3.144 | fa8b335c | qJvSDvKf — header name version fixed |
| PW-TestRunner BP | 0.5.11 | 59ca06fd | qJvSDvKf |
| PW-TestRunner RP | 0.7.1 | 772f9284 | 46dcyikV |
| RP-08 Items 1.4.9 · BP-02 1.3.200 · StripMine BP 1.3.12 | — | (table below) | 5WX4Qu29 (14:51) |

Content-log fix rounds (logs 1–3 -> 0 errors in log 4): empty-bone clips -> zero-rotation key; 8 birds on format 1.8.0 ->
animation controllers; armor_offset.default_neck clashes -> explicit locators removed + a bone named `head` only in one place
per entity (L-HEAD-LOCATOR, CONFIRMED); 12 RP-06 SF creatures were never converted (pose gate passed vacuously) ->
std_convert.Pack.ABOVE (animation ids resolve to the topmost pack, CONFIRMED); blobfish lead; RP-04 name. Standing static
gates added to build_std_round: FMT · EMPTY · EMPTY_FILE · UNCONVERTED · LOCATOR v3 · MANIFEST_NAME · per-entity NWR
(L-NWR-ENTITY: variables are per entity; the pack-level lint was blind).

### p22 — in preparation (his 16:51: "resume work towards preparing p22 and completing / researching backlogged items")
Layered on the frozen base (never edited by a layer): `assemble_std.py --fam --parade` = share -> **sharefix** -> **fam** -> **parade**.
- **fam** (std_famshare): anatomy families (69), a creature lacking a motion its family has is OFFERED the best relative's clip
  as an extra `fam_<kind>`, retargeted in the world. 17:0x–17:2x redesign after FAM-PREVIEW-2/3 (mechanism D-C420): every
  shared bone solved in the world incl. inherited motion; trunk = source pivot displacement x scale; **attach-follow**
  (L-ATTACH candidate: the standard rig hangs limbs / head / tail off cubeless joints, so attachment = rest geometry; parts
  follow the part they touch, ranked by deepest shared joint; wing pieces excluded); low-pose lock for sit / sleep (trunk height
  ratio from the source, legs / tails swing out of the ground, then lift); **FIT gate**: refused when the body misses the
  source's height by > 10 % of the animal's height (cat on the lion's lie 33 % refused; gelada sit / deer lie 14 % refused —
  threshold = his call when he sees previews).
- **sharefix** (std_sharefix, NEW): the p21 share layer had no attachment check — audit 46 / 242 shared_ clips loose > 1 px
  (P21-SHARED-LOOSE.md sent to him 17:29; 6 of 8 worst confirmed broken by render SHARED-LOOSE-1.png). p22: loose copies are
  rebaked through the family retarget or dropped (dry run 196 OK / 14 rebaked / 32 dropped).
- **parade** (std_parade, NEW): treadmill copies `parade_<short>` of movement-driven clips for the pens (253 clips / 120
  creatures, dry run) — p21's "FROZEN HERE = skip" becomes visible motion.
- **whale_wwa standardized** (duplicate `body` -> body_2, rig midline x = 2 handled, 36 / 0); plans group re-frozen (256).
- **snow_layer warning**: mechanism found (data-driven material reads terrain key `snow`); p22 fix staged: RP-10 `snow` ->
  single path snow_v0 (what the layer draws today).
- Checked, no change (his eye: WING-ROOT-CHECK.png, SHOEBILL-SEAM-CHECK.png sent 17:21): eagle wing-root overlap (hidden
  inside the body) and shoebill 0.24 px seam (not visible at 3x).
- Sniffer locator exception CONFIRMED by log 4.
- Tool hygiene: report_merge (partial runs no longer overwrite 5 reports); never-delete hook for every Python tool
  (usercustomize; escape PW_ALLOW_DELETE=1 only with his approval); TZ=America/Chicago in the shell profile.

### Open questions for him (not yet asked — batched)
1. Cube-box unification: what "unified cube boxes" means to him (UV style / inflate / mirror / rotations / zero-thickness limbs).
2. Authoring motions for the 1,064 family gaps no relative has (waders eat / sleep / call / attack, lemurs …) — OK to start?
3. Recipe conflict pw:room_wall vs pw:wall_oak_planks (same 3-plank column) — which keeps the pattern?
4. FIT threshold for family sit / lie copies (10 % now).

## Ship status (14:51 delivery — superseded by REVISION 2 above where versions differ)
SHIPPED, AWAITING HIS VERIFICATION (P1: static gates only rule out). One gofile folder `std-round-2026-10-01` (5WX4Qu29 — all 8 PASS: Molang 0 errors, server md5 == local, browser byte-exact, stranger check PUBLIC):

| Pack | Version | md5 | Notes |
|---|---|---|---|
| RP-07 Neutral Mobs | 1.4.40 | 0b078864 | standard round (590 creatures replaced in place + 3 vanilla added under entity/std) + 1.4.38 size law v2 + 1.4.39 MERS |
| RP-06 Hostile Mobs | 1.4.26 | f461cee3 | standard round (14) + 1.4.25 MERS |
| RP-08 Items | 1.4.9 | 39b78f37 | MERS round (held since 09-30); NO std change -> no 1.4.10 |
| RP-04 Basic | 1.3.143 | ba34de5c | MERS round (held) |
| BP-02 Tectonic | 1.3.200 | 0cd54ae2 | scripts/pw_flutter.js (J3 = d) |
| PW-StripMine BP | 1.3.12 | bd51c27e | size law v2 (held) |
| PW-TestRunner BP | 0.5.8 | edb56abc | lineups p20 (309 steps / 714 entities, 21 unsafe listed), p21 (1,343 steps), bump |
| PW-TestRunner RP | 0.7.0 | 790711de | pw:nbump |

Gates: std_groups guard PASS (607 creatures, 5 frozen groups, sharing 241 / 241) · build gate 0 JSON errors (3 vanilla-style
`//` comment files counted as info), 0 duplicate ids, 0 unresolved std refs, staged vs built 0 mismatches · BDS 1.26.52.3:
BP-02 + StripMine + Runner BP load with 0 errors · runner tests 344 / 344 · every p21 play id resolves (6 unresolvable clips
dropped and named: P21-NOT-SHOWN.md) · RESTRICTED-ASSETS +39 (X1, S1–S38) workspace + Drive (md5 35e3dbf4).
Install guide: outputs/INSTALL-STD-ROUND-2026-10-01.md (phone setup, PS5 joins, test in a COPY of the test world).

## What the standard round is
- All mobs: his T1 naming language; quadrupeds 201 / 201 with real leg joints (Q1 cuts); other plans 256 / 258
  (pw:whale_wwa kept as authored: two bones named `body`); humanoid + fantasy keep their own rigs (H1).
- Birds: flight v2 (level / unlevel joints, track slide D-C391, stretch), flutter (6 fowl), fold at rest for the 26
  spread-resting AnF birds (collapse joints, W timing, J8–J13), leg thickness (front texture on the sides; 12 raptors' foot-bone
  sheets added 14:25 — P11 gap: std_legs read leg-named bones only).
- Species sharing: 241 clips, 38 species, same species only (his 12:51 rule); EXTRA clips `shared_<kind>`, played only in p21.

## Rulings this session (verbatim sources in the decision journal D-C38x–D-C408)
J1–J13; D1 = b; 12:51 species-correct sharing; 13:06 slide; 13:34 rest ↔ unfold; J12 hawks lean 28°; 14:26 hawks must not
rise above the body -> mechanism: collapse slide overshot 1 px per joint (projected length 6 vs hinge spacing 5) -> slide = hinge
spacing (all 26); J13 = b (eagles / vultures keep tips over the rump).
**Standing process rules (his 14:35 + 14:41):** build in GROUPS, freeze each finished group, assemble at the end with a guard
(tools/std_groups.py freeze / check; build_std_round refuses on a failed guard). NEVER delete: discard = move into
`_garbage/<UTC stamp>/<original path>` (tools/discard.sh; bds_load.py and package_std_round.py follow it). When the workspace
allowance gets tight, garbage goes to his Drive (copy -> md5 verify -> then off the workspace).

## Pending verification (his witness)
p20 / p21 / bump on his hardware: flight / flutter / fold look, leg joins, shared_ keep / drop picks.

## Backlog
- (REV 2: measured 17:1x — hidden overlap, image to him) Wing-root sweep: the root front corner dips ~1.4 px into the body during the sweep (G3 non-zero on owl_ytri, hummingbird,
  YSav eagle, SF vulture) — trade-off reported, not fixed.
- (REV 2: shoebill checked, not visible; whale_wwa standardized for p22.)
- 123 older tools still contain delete calls (mostly trimming fresh build copies) — retrofit to discard when next touched.
- Time labels: I mislabelled times repeatedly this session; old packager logged UTC hours as "CT" (fixed in the new packager).
