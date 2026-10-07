// pw_testrunner_steps.js — the witness lineup as runner steps (PW-TestRunner BP v0.3.1, D-C249).
// v0.1.2: flat-world guidance on the biome-dependent steps (u4, v1, v2, v6); y3 describes the 1.4.11 llama shape.
// Order = HANDOFF §6: S0 log → 0u fireflies → 0v stable API → 0w room smoke → 0x markers → 0y round 2 → 0z furniture
// → 0a purge → 0 E2 → 0b phase 1 → 1–10 homestead.
//
// One step = { id, group, title, body, setup?, props? }
//   setup: run automatically when the step starts (and on "Repeat setup"):
//     { daytime: "noon" | "midnight" }          world.setTimeOfDay
//     { weather: "clear" | "rain" | "thunder" } dimension.setWeather
//     { give: [ "id", ["id", n], ... ] }      ItemStack into the inventory (namespace-less ids are minecraft:)
//     { cmd: [ "give @s bed 1 8", ... ] }     player.runCommand — only for items that need a data value
//     { spawn: ["minecraft:trader_llama", n] } dimension.spawnEntity, n entities 3–5 blocks ahead
//   props: run ONLY when he presses "Build props" (the runner never places blocks on its own):
//     { bush: true }                          a firefly bush 3 blocks ahead (dirt under it if the spot floats)
//     { particles: ["id", n] }                n particles of that effect around the point 3 blocks ahead
// Bodies are shown in the menu form (any length); LOG lines are built by the runner and kept <= 120 characters.

const FURN = ["bench", "stool", "chair", "barrel_seat", "table", "trestle", "shelf", "wall_shelf", "coat_pegs", "cupboard", "dresser", "mantel"];

export const STEPS = [
  // ---------------------------------------------------------------- S0
  { id: "s0", group: "LOG", title: "CONTENT LOG ON LOAD",
    body: "Open the content log now (Settings > Creator). Find these lines:\n" +
          "  [PW-VERSION] BP-01 Atmospheric Effects v1.3.35\n  [PW-VERSION] BP-03 Identification Diagnostics v1.3.34\n  [PW-VERSION] PW Test Runner BP v0.3.1\n" +
          "  MARKER-A v1.3.187 (BP-02)\n  [CIVITAS-MARKERS] v0.2.1 markers are entities\n  [pw_furniture] ready - 12 pieces x 3 woods\n" +
          "  [pw_homestead] HOMESTEAD runtime up (cycle 40t, puff 4t, chute 1t, rafters 10t)\n" +
          "PASS = all present and NO errors mentioning firefly, pw:furn_, pw:marker, pw:hatch_lid or texture sets.\n" +
          "(RP-07 base2 / swimming_wing / eye_target_x lines are known - ignore them.)" },

  // ---------------------------------------------------------------- 0u FIREFLY v2
  { id: "u1", group: "0u FIREFLY", title: "BUSH BY DAY",
    body: "Place a firefly bush (4 in your hotbar) and look at it in daylight.\n" +
          "PASS = the sharp Patrix 256 bush, and NO second bush drawn over it.\nBuild props = a bush placed 3 blocks in front of you.",
    setup: [{ daytime: "noon" }, { give: [["firefly_bush", 4]] }], props: [{ bush: true }] },
  { id: "u2", group: "0u FIREFLY", title: "BUSH FIREFLIES AT NIGHT",
    body: "Stand ~4 blocks from a bush for a minute.\nPASS = single small warm lights with a white centre that FLASH (about half a second to a second), " +
          "then go dark for a few seconds, drifting slowly. NOT clusters of balls. NOT faint smudges.\n" +
          "On the bush itself a few resting fireflies, one brighter one moving between them about once a second.\n" +
          "Build props = a bush 3 blocks ahead + 12 bush fireflies spawned around it (RP-10's particle, direct).",
    setup: [{ daytime: "midnight" }], props: [{ bush: true }, { particles: ["minecraft:firefly_particle", 12] }] },
  { id: "u3", group: "0u FIREFLY", title: "VIBRANT VISUALS GLOW ON THE BUSH",
    body: "With Vibrant Visuals ON, look at the bush at night.\nPASS = the bright resting firefly on the bush GLOWS.\n" +
          "FAIL + note 'no glow' if it is drawn but does not glow (that tells me the PBR frames are not animating)." },
  { id: "u4", group: "0u FIREFLY", title: "SWAMP FIREFLIES",
    body: "In a normal world: /locate biome swamp, then /tp @s <x> 120 <z>, fly down, wait a minute at night.\n" +
          "PASS = the same flashing fireflies around you in the open (BP-02's ambient field).\n" +
          "FLAT WORLD (no swamp): press Build props = 12 swamp fireflies spawned in front of you (the particle itself, direct), " +
          "judge the LOOK with PASS/FAIL + note 'props only'. BP-02's spawner stays untested until a real swamp.",
    setup: [{ daytime: "midnight" }], props: [{ particles: ["pw:firefly_ambient", 12] }] },
  { id: "u5", group: "0u FIREFLY", title: "DENSITY",
    body: "Overall, at the bush and in the swamp: too many, too few, or right?\nUse PASS + note or FAIL + note and say which (one knob each: fireflies per emit, life)." },
  { id: "u6", group: "0u FIREFLY", title: "OLD FIREFLIES (memory)",
    body: "From memory, before this update: did the OLD bush fireflies look like picture G reading 1 (faint smudges) or reading 2 (bright dots)?\n" +
          "PASS + note '1' or '2' (or Skip if you don't remember)." },

  // ---------------------------------------------------------------- 0v STABLE-API FIXES
  { id: "v1", group: "0v API", title: "FOREST BY DAY - BIRDS",
    body: "Stand still for about a minute. The bar says which biome you are in - it is information, not a requirement.\n" +
          "In a forest: PASS = bird ambience, one sound every ~30 s on average.\n" +
          "FLAT WORLD (extreme_hills): PASS = WIND (heavy or howling), one every ~30 s. BP-01 never played biome sounds before 1.3.35.",
    setup: [{ daytime: "noon" }, { weather: "clear" }] },
  { id: "v2", group: "0v API", title: "FOREST AT NIGHT - OWLS / CRICKETS",
    body: "Same spot, at night, a minute.\nIn a forest: PASS = owls / crickets now and then.\n" +
          "FLAT WORLD (extreme_hills): PASS = howling wind and now and then a wolf howl.", setup: [{ daytime: "midnight" }] },
  { id: "v3", group: "0v API", title: "RAIN",
    body: "Rain is on. Within ~30 s: rain ambience now and then; leaves drifting out of the canopies move FASTER than in calm weather.\nPASS = both.",
    setup: [{ weather: "rain" }] },
  { id: "v4", group: "0v API", title: "THUNDER",
    body: "Thunder is on. PASS = storm sounds, and the drifting leaves faster still.", setup: [{ weather: "thunder" }] },
  { id: "v5", group: "0v API", title: "CLEAR + THE SKY-FOG LINE",
    body: "Weather is clear again. Open the content log and look for:\n  [AbsolutRealism Sky] fog push failed: pw:ar_sky_...\n" +
          "If it is THERE: PASS + note 'fog line present'.\nIf it is NOT there and the sky turned overcast grey during the rain: PASS + note 'sky worked'.",
    setup: [{ weather: "clear" }] },
  { id: "v6", group: "0v API", title: "NO AMBIENT FIREFLIES OUTSIDE SWAMPS",
    body: "At night, anywhere that is not a swamp (your flat world counts), a minute.\nPASS = NO fireflies around you in the open (bushes still make their own).",
    setup: [{ daytime: "midnight" }] },
  { id: "v7", group: "0v API", title: "DIAG COMMANDS",
    body: "Break any block -> a [BLOCK] id @ x, y, z line.\nType /scriptevent pw:diag verbose -> 'Mode: verbose'; break again -> states + texture hint.\n" +
          "/scriptevent pw:diag off -> silent. /scriptevent pw:diag on.\nPASS = all four behaved." },
  { id: "v8", group: "0v API", title: "LEAVE AND REJOIN DURING RAIN",
    body: "Rain is on. Leave the world, rejoin, then tap the clicker (the run resumes by itself).\nPASS = rain sounds and windy leaves continue after the rejoin.",
    setup: [{ weather: "rain" }] },

  // ---------------------------------------------------------------- 0w ROOM SMOKE
  { id: "w1", group: "0w SMOKE", title: "BUILD THE SMOKE ROOM",
    body: "Items are in your inventory. Build a small closed room with a door; hearth inside; flue blocks stacked above it up through the roof.\n" +
          "Tap the hearth with logs, then with the flint & steel -> lit.\nType /scriptevent pw:home status -> the hearth is listed.\nPASS = built and lit, listed.",
    setup: [{ weather: "clear" }, { give: ["pw:hearth_cobblestone", ["pw:flue_cobblestone", 6], ["oak_log", 16], "flint_and_steel", ["oak_planks", 64], ["oak_door", 2]] }] },
  { id: "w2", group: "0w SMOKE", title: "SMOKE FILLS THE ROOM",
    body: "Put a plank block ON the chimney top (cap it) with the doors shut. Wait ~30 s inside.\n" +
          "PASS = pw:room_smoke fills the room; 'you cough' at 12 or more (the grey room FOG is OFF since BP-02 1.3.187 - report it if you still see one).\n/scriptevent pw:home status shows the smoke level." },
  { id: "w3", group: "0w SMOKE", title: "SMOKE CLEARS",
    body: "Open a door -> the level falls. Remove the plank from the chimney -> it clears.\nPASS = both." },

  // ---------------------------------------------------------------- 0x MARKERS 0.2.1 + HATCH
  { id: "x1", group: "0x MARKERS", title: "MARKERS MIGRATE",
    body: "In the cottage type /scriptevent civ:markers migrate 64.\nPASS = 'migrate r64: N marker blocks -> N entities', and the glyph cubes look as before.\n" +
          "Content log: [CIVITAS-MARKERS] v0.2.1 ... and no errors for pw:marker / pw:hatch_lid." },
  { id: "x2", group: "0x MARKERS", title: "SEAT MARKER INTO A CHAIR",
    body: "Place the chair. Hold the seat marker, SNEAK and tap the chair.\nPASS = the marker cube appears INSIDE the chair's cell and the chair stays.",
    setup: [{ give: ["pw:station_seat", "pw:furn_chair_oak"] }] },
  { id: "x3", group: "0x MARKERS", title: "FURNITURE INTO A MARKED CELL",
    body: "Place a kitchen zone marker on the floor, then place the table INTO that same cell.\nPASS = the table places normally.\n" +
          "If the game refuses: /scriptevent civ:markers hide, try again, and note whether it placed then.",
    setup: [{ give: ["pw:zone_kitchen", "pw:furn_table_oak"] }] },
  { id: "x4", group: "0x MARKERS", title: "HIDE / SHOW",
    body: "/scriptevent civ:markers hide -> every marker gone, and taps reach the furniture underneath.\n/scriptevent civ:markers show -> back.\nPASS = both." },
  { id: "x5", group: "0x MARKERS", title: "LADDER HATCH",
    body: "Ladder in the top cell of a floor opening; put the hatch lid on that ladder.\n" +
          "Closed lid flush with the floor? Walk across it (no fall, no jitter?). Climb up under it (head stops?).\n" +
          "Tap from below -> opens toward the side OPPOSITE the ladder; climb through; tap from above -> closes.\n" +
          "PASS + note which side the open leaf stands on. (/scriptevent civ:hatch turn moves the hinge 90 degrees.)",
    setup: [{ give: [["ladder", 4], "pw:hatch_lid"] }] },

  // ---------------------------------------------------------------- 0y ROUND 2
  { id: "y1", group: "0y ROUND 2", title: "TABLE CORNER + MANTEL END",
    body: "Place the table: leg/apron corner - NO stipple patch, also on a slow pan.\nMantel left end - NO hatched band.\n" +
          "Backs of trestle / barrel seat / shelf / cupboard / dresser steady.\nPASS = all steady.",
    setup: [{ give: [["pw:furn_table_oak", 2], "pw:furn_mantel_oak", "pw:furn_wall_shelf_oak", "pw:furn_trestle_oak", "pw:furn_barrel_seat_oak", "pw:furn_shelf_oak", "pw:furn_cupboard_oak", "pw:furn_dresser_oak"] }] },
  { id: "y2", group: "0y ROUND 2", title: "MANTEL + WALL SHELF HEIGHTS",
    body: "Mantel over a hearth: board top 5 cubes up its cell on two small 2x2 corbels - closer to the fire.\n" +
          "Wall shelf: top at 8 (where the mantel used to be). Look at its SIDES: any flicker? -> FAIL + note 'shelf sides flicker'.\nPASS = heights right, no flicker." },
  { id: "y3", group: "0y ROUND 2", title: "TRADER LLAMAS",
    body: "Four trader llamas were spawned in front of you (Repeat setup spawns four more).\n" +
          "PASS = fur body, blanket, striped leg sleeves; up to four coat colours across them; and with RP-07 1.4.11 the SHAPE of an ordinary llama: " +
          "body resting on the legs, neck rising out of the body, nothing hanging under it. FAIL + note if any part floats or sinks.",
    setup: [{ spawn: ["minecraft:trader_llama", 4] }] },
  { id: "y4", group: "0y ROUND 2", title: "CHIMNEY PLUME",
    body: "With a hearth lit: puffs rise up through the flue; a plume about 8-11 blocks above the chimney top, drifting slightly downwind, fading slowly.\nPASS = seen." },

  // ---------------------------------------------------------------- 0z FURNITURE r1
  { id: "z1", group: "0z FURNITURE", title: "ALL 12 PIECES",
    body: "All 12 oak pieces are in your inventory. Place each one.\nPASS = front faces you; planks / stripped log / end grain / iron where the sheets put them; " +
          "the dresser rack rises into the cell above; the mantel over a hearth sits right on the hearth top.\n(Other woods: /give @s pw:furn_<piece>_spruce or _dark_oak.)",
    setup: [{ give: FURN.map((p) => `pw:furn_${p}_oak`) }] },
  { id: "z2", group: "0z FURNITURE", title: "COLLISION",
    body: "Step onto a bench like a slab; a chair needs a jump; walk through the wall shelf, coat pegs and mantel.\nPASS = all three." },
  { id: "z3", group: "0z FURNITURE", title: "SITTING",
    body: "Empty hand: tap a bench, stool, chair, barrel seat.\nSeat height right (floating / sinking -> note it). Facing: front or backrest (note it). Sneak stands you up; the seat is free again.\nPASS = sits right." },
  { id: "z4", group: "0z FURNITURE", title: "TABLES JOIN",
    body: "Two tables side by side join (shared legs and rails vanish). Three in a row: the middle one legless. Break one -> the neighbour regrows its legs.\nPASS = all three.",
    setup: [{ give: [["pw:furn_table_oak", 3]] }] },

  // ---------------------------------------------------------------- 0a PHASE 1b + PURGE
  { id: "a1", group: "0a PURGE", title: "PURGE CHECK 1 - WOOL, GLASS, RAILS, ANVIL, QUARTZ, CROPS",
    body: "Content log: NO missing-texture or texture-set errors (the purge's real test).\n" +
          "Wool slabs/stairs + light-gray wool and carpet HD; stained glass + pane HD (other colours: /give @s <colour>_stained_glass);\n" +
          "rails x4 powered and unpowered (redstone block given); anvil x3 damage states; quartz pillar / chiseled; crops potatoes, beetroots, cocoa, nether wart, torchflower (bone meal given).\nPASS = all HD, log clean.",
    setup: [{ give: ["light_gray_wool", "light_gray_carpet", "red_stained_glass", "red_stained_glass_pane", "rail", "golden_rail", "detector_rail", "activator_rail", "redstone_block",
                     "anvil", "chipped_anvil", "damaged_anvil", "quartz_pillar", "chiseled_quartz_block", "potato", "beetroot_seeds", "cocoa_beans", "nether_wart", "torchflower_seeds", ["bone_meal", 64]] }] },
  { id: "a2", group: "0a PURGE", title: "PURGE CHECK 2 - NETHER WOODS, CANDLES, ODDS",
    body: "Crimson / warped doors, trapdoors, planks, stems, signs; candle; spawner; cobweb; note block; item frame back; packed ice; honeycomb; honey; slime; wet sponge.\nPASS = all HD.",
    setup: [{ give: ["crimson_door", "crimson_trapdoor", "crimson_planks", "crimson_stem", "crimson_sign", "warped_door", "warped_trapdoor", "warped_planks", "warped_stem", "warped_sign",
                     "candle", "mob_spawner", "web", "noteblock", "frame", "packed_ice", "honeycomb_block", "honey_block", "slime", "wet_sponge"] }] },
  { id: "a3", group: "0a PURGE", title: "PURGE CHECK 3 - SHULKERS, CHESTS, CHAINS, CAMPFIRES, GHAST",
    body: "Shulker box: the top in the inventory icon AND the block top HD. Chest / ender / copper chest inventory icons show the HD chest.\n" +
          "Chains (iron + copper) HD links. Campfire and soul campfire flame = the Patrix fire - does the bigger flame read right on a campfire?\n" +
          "Dried ghast: eyes on the FRONT (facing you), sides not obviously swapped.\nHearth flicker irregular (9 s before it repeats; frozen or wrong frame -> note).\nPASS = all.",
    setup: [{ give: ["undyed_shulker_box", "light_gray_shulker_box", "chest", "ender_chest", "copper_chest", "chain", "copper_chain", "campfire", "soul_campfire", "dried_ghast"] }] },

  // ---------------------------------------------------------------- 0 E2
  { id: "e1", group: "0 E2", title: "E2 - CHESTS, STAND, BELL, BANNERS, CRYSTAL, CONDUIT, POT, CAULDRON",
    body: "Single chest: lid top wood with its band, latch upright on the front, planks upright. Double + trapped double: front/back unchanged, top = plank top. Copper chests HD. Ender chest.\n" +
          "Armor stand HD wood. Bell HD. Banner HD cloth + patterns (loom given): a diagonal pattern shows the SAME diagonal as before.\n" +
          "End crystal. Conduit HD (wind static). Decorated pot HD with patterns. Cauldron + water: water = RP-02 shading.\nPASS = all.",
    setup: [{ give: [["chest", 2], ["trapped_chest", 2], ["copper_chest", 2], "ender_chest", "armor_stand", "bell", "banner", "loom", "end_crystal", "conduit", "decorated_pot", "cauldron", "water_bucket"] }] },

  // ---------------------------------------------------------------- 0b PHASE 1 + BED
  { id: "b1", group: "0b PHASE 1", title: "BEDS",
    body: "Light gray, red, white and black beds given. Place each.\nPASS = continuous blanket over both halves, footboard, wooden legs, no gap (light gray too).",
    setup: [{ cmd: ["give @s bed 1 8", "give @s bed 1 14", "give @s bed 1 0", "give @s bed 1 15"] }] },
  { id: "b2", group: "0b PHASE 1", title: "FURNACES + REDSTONE + DOORS",
    body: "Furnace / blast furnace / smoker OFF fronts HD; dispenser and dropper fronts; repeater and comparator off; observer back; jack-o'-lantern lit face; iron door.\nPASS = all HD.",
    setup: [{ give: ["furnace", "blast_furnace", "smoker", "dispenser", "dropper", "repeater", "comparator", "observer", "lit_pumpkin", "iron_door"] }] },
  { id: "b3", group: "0b PHASE 1", title: "STONE SLABS, STAIRS, BRICKS",
    body: "Sandstone / smooth stone / andesite / granite / diorite slabs and stairs; stone brick variants; nether, red nether, end bricks; prismarine.\nPASS = all HD.",
    setup: [{ give: ["sandstone_slab", "sandstone_stairs", "smooth_stone_slab", "andesite_slab", "andesite_stairs", "granite_slab", "granite_stairs", "diorite_slab", "diorite_stairs",
                     "stone_bricks", "mossy_stone_bricks", "cracked_stone_bricks", "chiseled_stone_bricks", "nether_brick", "red_nether_brick", "end_bricks", "prismarine"] }] },
  { id: "b4", group: "0b PHASE 1", title: "SIGNS, BOATS, SHULKERS, COPPER CHEST",
    body: "Oak sign (standing) and hanging sign; oak boat and chest boat; light-gray + undyed shulkers; copper chest.\n(Other woods: /give @s <wood>_sign, <wood>_boat; bamboo boat = bamboo_raft.)\nPASS = all HD.",
    setup: [{ give: ["oak_sign", "oak_hanging_sign", "oak_boat", "oak_chest_boat", "light_gray_shulker_box", "undyed_shulker_box", "copper_chest"] }] },

  // ---------------------------------------------------------------- 1–10 HOMESTEAD
  { id: "h1", group: "HOMESTEAD", title: "HEARTH WALLS (.131)",
    body: "Place the plank hearth (and the cobble one). PASS = plank side walls on both sides, plank front ends, plank lip at the floor, soot interior;\n" +
          "fueled / lit / embers / spent / cold all carry the walls.",
    setup: [{ give: ["pw:hearth_oak_planks", "pw:hearth_cobblestone", ["pw:flue_oak_planks", 6], ["oak_log", 16], ["charcoal", 8], "flint_and_steel"] }] },
  { id: "h2", group: "HOMESTEAD", title: "CHUTE (FLUE)",
    body: "Flues stacked on the hearth. PASS = planks outside on all four sides, soot inside on all four; the cap rim still there; from inside the bore all four inner faces soot." },
  { id: "h3", group: "HOMESTEAD", title: "FIRE",
    body: "Light the hearth. Does the flame own the interior? Too tall / too wide / too soft (same texture, texels ~1.4x larger)?\nAny lick visible in the bottom of the first chute block?\nPASS + note what you see." },
  { id: "h4", group: "HOMESTEAD", title: "CORNERPOST PROBE (L-XFACE)",
    body: "Place the frame cornerpost. Which corner does the post occupy, compared with the corner you expected?\nPASS + note 'expected' or 'mirrored' (this decides whether box POSITIONS mirror as well as face keys).",
    setup: [{ give: ["pw:frame_cornerpost"] }] },
  { id: "h5", group: "HOMESTEAD", title: "RIDGE CAP CORNERS",
    body: "Ridge caps + ridge ends given. On the cottage (or a test run of ridge): the cap bottom corners and the top course junction - is the streak patch GONE?\nPASS = gone.",
    setup: [{ give: [["pw:roof45_ridge_oak", 8], ["pw:roof_ridge_end_oak", 2], ["pw:roof45_oak", 8]] }] },
  { id: "h6", group: "HOMESTEAD", title: "RAMPS + SNOW TOE",
    body: "Cobble ramps (2_lo, 2_hi, 4_q1..q4) + snow layers given. Q-chain seams: the dotted triangle gone? Snow toe: the filler paints down to the block base (a 2.4 x 1.2 px wedge) - reads wrong?\n" +
          "Look at a ramp seam from BOTH sides. Snow on snow: sparkle above the deck line at the toe?\nPASS + note.",
    setup: [{ give: ["pw:ramp_cobble_2_lo", "pw:ramp_cobble_2_hi", "pw:ramp_cobble_4_q1", "pw:ramp_cobble_4_q2", "pw:ramp_cobble_4_q3", "pw:ramp_cobble_4_q4", ["snow_layer", 16]] }] },
  { id: "h7", group: "HOMESTEAD", title: "HEARTH CYCLE",
    body: "Fuel with logs (grain along), flint & steel -> tall Patrix flame + puffs. Wait for embers (low licks, dim logs). Burn out -> charcoal stays. Add fuel on the charcoal -> logs again.\nPASS = the whole cycle." },
  { id: "h8", group: "HOMESTEAD", title: "CHUTE - THE SANTA TEST",
    body: "Look up from inside the hearth (sky through the bore); from below the flue ring; the cap open; the chimney column from the bore top.\n" +
          "Jump in from the cap top: clamped in the bore, air bar, 1 heart/s after 16 s; heat 1/2 heart/s over coals; fire over a lit hearth.\n" +
          "Walk into a chimney from the side on the roof: pushed back.\nPASS + note anything off." },
  { id: "h9", group: "HOMESTEAD", title: "CAMPFIRE + CHIMNEY SMOKE",
    body: "Vanilla campfire and the chimney column: Patrix smoke on both.\nPASS = both.",
    setup: [{ give: ["campfire", "soul_campfire"] }] },
];

export const STEP_INDEX = Object.fromEntries(STEPS.map((s, i) => [s.id, i]));
