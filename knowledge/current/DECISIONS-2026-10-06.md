# Program 228 — Abs0lum's rulings (2026-10-06, 10:15 and 12:20 CT). These override the FIT-MATRIX defaults.

| Topic | Ruling |
|---|---|
| Violence | No raids, militia, war, civ-vs-civ killing for now. BUT civs are not helpless: when the watch/guard is overwhelmed by MONSTERS, civs band together to defeat them. |
| Sickness | No sickness deaths. The sanitation death-chance rule is OFF (flag SANITATION_DEATH=false) — kept in code + documented for later. Sanitation = mood only. |
| Random negatives | None (no random events tables). Deterministic consequences OK. |
| Workshop mood floor | Output never below 50 % (tiers 1.2/1.1/1.0/0.85/0.70, floor 0.50). No full strike. |
| Watch pay | Unpaid + low morale -> walks half his rounds; below the "would resort to crime" morale -> leaves town. MEASURE the crime factors now (no crime enabled). |
| Festivals | Wedding gathering + a feast at each tier-up, on the square at dusk + a MONTHLY holiday festival (game time). |
| Rain | Quarrymen, woodcutters, builders shelter and keep half output. |
| Witnessed deeds | Built, switched OFF until the narrative phase. |
| Coins | Add a SILVER NICKEL coin (alongside gold). |
| Gardens | Fillers only (well, cart, lamp) — no frontage left empty. |
| Weathering | Lived-in houses age too; past a bad enough level the city requires repairs: fines the household and fixes the house. |
| Script API | PS5 is on v26.52 (build 51798898, branch r/26_u5). npm: 2.11.0-beta.1.26.52-stable => stable 2.10.0 is the 1.26.5x line. Upgrade to 2.10.0 after a BDS probe. |
| Tax dial / build priority | Free commands. |
| Trees | Trunk-tip fix for all groups; REMOVE oak elder + pale oak dead limbs; APPLY to pale oak; REMOVE old oak dead leader. Fix the jungle_young doubled root. |
| Castle roofs | Thatch roofs as GABLES with existing thatch pieces. He believes hip blocks are broken for all materials — investigate; if broken, build new hip blocks for all materials (thatch hips later). |
| Palace passage | One-slope roof of our spruce roof blocks. |
| Vaulted ceilings (new idea) | Flip our sloped/ridge roof blocks upside down to make vaulted ceilings; the attic floor levels with the topmost block; a real roof above so the stepped back is never visible. |
| Ramps | Sidewalks use our smooth-stone ramp blocks; expand ramp materials to ALL stones; create an 8-block ramp (rise 1 over 8 — smoothest) and make it PREFERRED; the 4-block set for switchbacks and steeper climbs. |
| Furniture | He asks: packs to download with advanced furniture / a REAL spiral staircase? Unused item/object blocks in packs we already have? Patrix re-skin of good geometry is fine. "Fix everything we can." |
- Spiral stairs: his brief (12:47) — curved outer railing; underside curving up to meet the next flight seamlessly; geometry bent through 4–6 spaces per quarter turn, texture may spill into neighbours; images first, several geometry + Patrix texture attempts. Block format >= 1.21.130 allowed for the spiral blocks ONLY (lock exception).

## 14:07–14:20 CT — save on close + ROLE BEDS (his message + answers)
- **Save on close (his 14:07):** the town already lives in the world's dynamic properties (written every 600 ticks). ADDED in 1.3.228:
  `system.beforeEvents.shutdown` final flush. BDS witness: `[CIV-SAVE] shutdown: final save written (tick 3097)`, --keep-world reload
  continued gen 6 -> 7 with 43 buildings. PS5 close = his witness item.
- **Role beds (his 14:07):** "once our population is getting high enough, we need to prioritize filling empty beds; BUT the beds that are
  filled have to correlate to job or position within the palace and castles … these beds are reserved until those roles are filled."
  Facts today: HOUSEHOLD has no palace/castle; bedsOf(palace pieces) = 0 in CIV_BUILDINGS (palace beds live in palacegen rooms);
  PLACES.BEDS_BASE off; castles not placed by towns.
- **His answers (AskUserQuestion):**
  - Noble apartments / lord's solar: "Town's top families + political representation per district + staff in the servants quarters -
    which ARE the towns best cooks and tradesmen, etc" -> court = top families; ONE representative household per district at the palace;
    servants' quarters staffed by the town's BEST cooks and tradesmen (highest skill), not generic hires.
  - Families: "Families move in too" (option text: only where the room has enough beds — noble apartments; elsewhere single staff live in,
    married staff keep the family home and the role bed stays reserved for a single hire).
- Target: 1.3.229 (after gate 228-3). Plan: tag beds by room role in palacegen/castlegen POI -> CIV_BUILDINGS bedsByRole; reservation;
  job<->bed cross-reference; City III+ empty-bed priority; BEDS_BASE on for houses; `pw:clock beds`.

## 14:21 CT — spiral sizes (his ruling)
"I want to keep all sizes and use them where appropriate - tight defensive towers use the narrow staircase (a), your run-of-the-mill
spiral staircase will use b, and palaces and castles and manors will use the grand (c)."
-> A turret = defensive towers (castle towers, wall towers); B tower = ordinary spiral stairs; C grand = palaces, castles, manors.
Palettes: not yet ruled (iteration 2 shows them again). Generators (palacegen/castlegen/manor) get the mapping when the blocks ship.

## 14:28 CT — the HEADROOM LAW applies to the spiral stairs (his ruling)
"Please make sure the spiral stairs follow the same rules as the previous stair rules; a character needs 3 blocks of coverage to pass
through any slope - their two blocks, and the more above then for every rise o fall of the y axis."
Measured (tools/spiral_gen.py clearance(): every tread sample, lowest solid above, pitched pieces from their lowest corner):
- On the treads: min 49.0 px (A, B) / 51.0 px (C) >= 48 (3 blocks) — the turn above is 4 blocks up, soffit hangs <= 7 px.
- v2 preview VIOLATED it: the landing slab laid over the well left 2.0-2.75 blocks over the turn below. FIX (v3): the head exits
  OUTWARD over the outer edge onto a landing BESIDE the well (rail stops EXIT_W = 18 px of outer edge early, end post there);
  nothing is ever laid over the well; the floor under the first turn is NOT a walk path (generators: fill/fence it, mark no-walk);
  the foot is entered tangentially from the open side (the green sector of the HEADROOM-*.png floor panel).
Generator rules for palacegen/castlegen/manor when the blocks ship: well open floor-to-roof over the footprint; landing outside the
footprint at the head; ceiling >= 3 blocks above the head tread.

## 14:36 CT — "Yes, to all" + palettes delegated ("based on abundancy and class station representation")
PALETTE RULES (my choice under his delegation; applied when the generators place spiral stairs):
- A turret (defensive towers): STONE (polished andesite treads, stone-brick underside/string/post, oak rail) — masonry towers;
  OAK for timber watchtowers (wood abundant, low station).
- B tower (ordinary): the LOCAL WOOD by abundance (oak default; spruce in cold/taiga; later birch/dark oak by biome) for commoners;
  SPRUCE + PLASTER underside for merchant / guild houses (middle station); STONE in stone districts (quarry towns).
- C grand: STONE for palaces and castles (highest station, the durable material); SPRUCE + PLASTER for manors; OAK for a lesser
  manor where stone is scarce.
TEST PACK built: AR Spiral Stairs Test BP/RP 0.0.1 (tools/spiral_pack.py): 8 blocks pw:spiral_stairs_<design>_<palette>
(A stone/oak, B oak/spruce_plaster/stone, C stone/spruce_plaster/oak), block format 1.26.0 (collision arrays), states pw:cell
(B/C), pw:part start|mid|end, pw:hand ccw|cw, cardinal_direction; 912 permutations. Structure pw:spiral_pad (82x11x16):
A stone ccw+cw, B oak ccw+cw, C stone ccw, C spruce_plaster cw, landings beside the wells. BDS 1.26.52 (srv2): 0 errors after the
A fix (a 1-value enum state is refused: "Block State enum array must have more than 1 value"), structure loads.
Independent engine-law render (tools/spiral_pad_render.py): every helix continuous (first pass caught the cw quarters turning the
wrong way: cw ascends by -90 per quarter -> fixed before shipping). Drive ClaudeUploads: BP md5 e1285dd6…, RP md5 5793387e….

## 15:06 CT + answer — the stair exits FORWARD; headroom law = AT LEAST 2 blocks at every point of the ascent
- His 15:06: "I don't want the next floor to come off the side … the floor [extends] from the 'front' (where the last stair lengthways
  position is oriented) of the stair - as all stairs do. That exit can turn into a lengthwise hallway."
- His answer: "As long as it has AT LEAST two blocks at all points during the ascent, it will work; a two block clearance doesn't work
  on Minecraft vanilla because the first stair turns the clearance into 1.5 blocks momentarily" (our treads rise 4 px, not 8);
  turret A: "See my previous answer" -> A exits forward too.
- SUPERSEDES the 14:28 reading (3 blocks; side exit). Built in Spiral Test 0.0.3: no side opening; rail ends at its natural end post;
  the floor in front covers the first quarter ahead of the head (2.75 -> 2.0 blocks over the turn below = legal) and runs on as a
  hallway beyond the well; the SECOND quarter ahead must stay open (1.0 block over the turn below) — the stairwell opening in a
  floor is three quarters of the well. Measured (clearance(), HEAD_MIN 32 px): every design, both hands: min 2.00 on the ascent,
  0 samples below the law.

## 16:22 CT — ENGINE PROBE (BDS 1.26.52, srv2; tools/bds2_rot_probe.py) — spiral blocks under /structure load
- Rotation ROTATES a custom block's `minecraft:cardinal_direction` (placement_direction trait) like vanilla: south ->
  90_degrees west, 180 north, 270 east (90_degrees = clockwise from above). Our transformation table (south 0, east 90,
  north 180, west 270, right-handed) stays consistent: a rotated building keeps its stairs whole.
- Mirror does NOT touch the custom `pw:hand` state (mirror x turned south -> north, mirror z kept south) -> a MIRRORED
  structure would break a spiral's chirality. RULE: structures holding spiral blocks are rotated, never mirrored.
- Block identifiers come back LOWERCASED at runtime (pw:spiral_stairs_A_turret_stone -> pw:spiral_stairs_a_turret_stone).
  RULE: the main-pack spiral ids are lowercase (pw:spiral_stairs_a_turret_stone …).

## 16:30 CT — his answers (AskUserQuestion): spirals in the generators
- MID FLOORS: "Doorway beside the step" — a spiral passing through a storey lets people off through an opening in the
  outer side at the step that is level with that floor (the quarter there is an END piece: its rail stops at its end post;
  the next quarter is a START piece with its newel post); only the TOP floor gets the forward exit (floor in front).
- PALACE SIZES: C grand in the main towers (prison tower, gatehouse tower), B tower for the back / service stairs.
- (standing, 14:21) castles + manors: C; tight defensive towers: A.

## 17:52–17:58 CT — his messages
- CHILDREN'S BEDS: "yes, add childrens' beds. I trust your structural changes but I still want to approve the images."
  -> 12 children's beds (11 apartments of state + the lord's chamber); renders _docs/program228/beds/CHILD-BEDS-v3.png sent;
  structures staged in _staging/palace_childbeds, installed only after his approval. Court rule: a couple + up to 2 children.
- DIAGONAL CATWALKS (his idea, structures only, never player items): 45-degree bridges 1-2 wide over open halls, a set of
  4-6 pieces (a: pieces filling the neighbour cells; b: pieces reaching into neighbours). My analysis: transformation rotates
  in 90-degree steps only, so the 45 degrees live in the geometry; geometry may reach ~22 px into neighbours but COLLISION
  may not leave its cell -> (a) is the base (centre piece, side wedge, end transition, rail/open edge state; 2-wide adds a
  wider wedge). CONFIRMED (17:58): queued as ITS OWN PROGRAM right after this combined release; images first (a castle
  hall with an open floor and a diagonal skyway overhead).
- STATUS TICKS (17:53): an update on all background tasks every 5 minutes (send_later chain in this session).

## 18:0x–18:22 CT — palace spirals reworked + PALACE II (his messages)
- 18:0x "Rework rooms now": all 10 palace stair sites laid with our spiral blocks (tools/spiral_site.py solver: every
  mid-floor door + top landing on walkable floor): gatehouse A turret (ground -> lodge 6) + C grand (6 -> 16); prison tower C
  (laid after the wings: the wing's floor fill opened the tower to 6 x 6); 5 back stairs B (wells widened over panel lines,
  attic masonry cleared in the well + one row only, under the roof); little commons B in a new stair hall (z 61..68: the last
  lodging gives way); coach house B. The east back stair took the cabinet's jib door: a new cabinet door one row north; the
  stair's doorway opens into the cabinet (the private stair). Envelope check: 0 newly sky-exposed cells.
- New spiral piece "door" (16:30 rule made real): a head whose rail stops at exit_theta so the outer face beside the step is
  open (collision gap >= 10 px, numerically checked for 3 designs x 2 hands x 4 facings).
- 18:22: "We can enlarge our palaces and castles to make room for our changes, and even entire new rooms for children's
  beds… blueprinted off of real palaces — all the way down to the secret hallways and doors and secret staircases and
  underground passages — everything." -> PALACE II program queued after this release (with the catwalks), images first.
