---
name: overview
description: AbsolutRealism pack suite — purpose, scope, setup, and current state of all active workstreams
sources: [backfill]
aliases: [AbsolutRealism, pw, Abs0lutMedievalism, am, CIVITAS]
---
## Purpose & scope

- [stated] Abs0lum is the sole creative director and developer of AbsolutRealism (namespace `pw:`), a hyper-realistic Minecraft Bedrock resource and behavior pack suite
- [stated] AbsolutRealism is a large-scale port of the Patrix Java texture pack to Bedrock with full Vibrant Visuals (PBR/MERS) compliance
- [stated] Abs0lutMedievalism (namespace `am:`) is a parallel private pack, never distributed — a study and personal-use companion
- [stated] CIVITAS is the long-term creative ambition: a living story-driven settlement system built on top of the pack infrastructure
- [stated] The project spans ~18+ canonical packs: RP-01 through RP-11, BP-01 through BP-05, diagnostic/pilot packs, StripMine house, and CIVITAS marker packs
- [stated] Core project values: photorealistic fidelity, witness-rule discipline (in-game hardware confirmation is truth), plan-first-build-second, and maximum technical depth
- [stated] Utopia-First Doctrine governs CIVITAS: build and prove the correctly-operating society first, with breakdown/failure elements introduced one at a time as witnessed experiments
- [stated] A partner shares the game world and contributes tree-building work; the packs are played by Abs0lum and his live-in girlfriend on their two PlayStations at home
- [stated] Personal-use-only ruling (2026-09-30, "actually, from a few weeks ago"): "We are no longer producing ANYTHING for production. All assets may be used for personal use and we are only creating for personal use from now on"; zero distribution of assets will happen — replaces the earlier production / licence-tier rules
- [stated] Restricted (non-redistributable) assets, e.g. 3D Jungle textures as a stand-in until he buys his own, go straight into the main packs; a separate RESTRICTED-ASSETS swap list (kept on his Drive and by Claude) records which mobs/files use them, so he can later purchase licences and move everything into production if he changes his mind
- [stated] Wants the longest render distance the PlayStation can handle ("the closest to 'distant horizons'" without crashing); plans to upgrade to a PS5 Pro for further loading distance
- [stated] IP standing law: Abs0lum's claimed pw: families (angled walls, vaulted ceilings, auto-transform mechanic, window/glass wall class, gable infill, plank flooring, arch auto-mechanic + keystones, oculus) are documented with pre-Medievalism prior art and homed in pw: for all future development

## Development setup

- [stated] Android phone is the primary testing device; LG UltraPC laptop handles pipeline work; PS5 serves as a second player/control-group tester
- [stated] Claude Max subscription plus a Claude Code installation
- [stated] Syncthing syncs assets between phone and laptop
- [stated] Packs are activated in reverse target order (first-activated = stack bottom)
- [stated] Bedrock engine version v26.32 (internal 1.26.32.2)
- [stated] Third-party content home: PW StripMine RP + BP, canonized as the single home for all third-party content, merged by function (Matched-Set Law) — superseded 2026-10-02: "Put everything from stripmine into appropriate packs we already have; but keep them labeled based on the pack they came from"; creature behaviour goes into BP-02; big packs may later be split into 2 parts labelled by load order; the 250 MB cap is measured on the .mcpack file (Realm rule)
- [stated] StripMine is made only for his Realms world and not for production (2026-09-22); third-party packs he uploads are used mostly for method, and if we can't improve on them, the best parts of all of them go into StripMine to avoid licensing complications
- [stated] Pack-size law (2026-09-28, refined the same night): "250 MB is an absolute maximum" per pack; whether a family is one pack or two is decided by "needs AND future foreseeable conflicts" (earlier wording: over 250 → two packs, under 250 with reasonable room → one)
- [stated] Agreed 2026-09-28: manifest dependencies turned back ON after the ownership dedupe, dependent → owner only

## Current state (as of 2026-08-09 — re-verify before relying on version numbers)

- [stated] Authoritative state = newest-dated HANDOFF doc in project knowledge
- [stated] Pack versions as of 2026-09-29 (his gofile folder, asked to correct the lag): RP-07 1.4.24, RP-06 1.4.17, RP-08 1.4.8, PW-TestRunner BP 0.3.8 / RP 0.3.0, RP-04 1.3.142 (the 08-09 set — BP-02 v1.3.83, RP-04 v1.3.62 … — is long superseded; newest HANDOFF + his folder decide). BranchAlign retired
- [stated] SlabForge / slab smoother: offline pre-pass pipeline (`slabforge_offline.py`) built and self-tested; PW-Pregen BP v0.1.0 automates chunk generation via spectator grid-hop; dry-run verified (placed, bridged, slope_skips, vegetation counts confirmed)
- [stated] Flora variants wave: 15 species at 8 weighted variations each shipped; grass skirt authored into Patrix side variants
- [stated] Mob assets: de-triplication across RP-06/07/08 completed
- [stated] CIVITAS markers: PW-Civitas-Markers BP+RP v0.1.1 shipped with `pw:datum`, `pw:port_*` family, station index listener, `pw:manhole_cover` (six skins, phased slide animation)
- [stated] CIVITAS infrastructure planning: Road Spec v3 locked, full vertical section confirmed; Port Law, Hatch Law, Slab Law, Clearance Law all recorded; PROVING GROUND flat world created (Tunnelers' Dream preset)
- [stated] PROVING GROUND datum y=173 (sidewalk surface = feet 0); street straight built and its as-built section adopted as canon: a 2-clear service gallery (linemen/electric, doored from the same building shaft as the sewer) above a 13-wide sewer hall with merged side lanes (the old separate branch tunnels are dropped), raised centre vault, 2-deep centre channel; laws: no dirt ceilings ever; sewers are narrative/story infrastructure only (villagers don't use them as plumbing); jobs Sewer Surveyor and Line Surveyor added beside the Roadwright for damage patrol/repair; canonical street palette smooth-stone sidewalks, stone-brick stairs, cobble road; master save of the straight then the 5-slice ramp and the crossroads are the next pieces
- [stated] Mob geometry / StripMine extrapolation: five animation grafts shipped (ocelot←cat, fox←wolf, panda←polar bear, camel+goat←llama); parrot flight fixed; Directional Awareness system shipped for leaves
- [stated] UV-Contract Linter built and run suite-wide: 676 overshoots, 139 undershoots, 848,583 theft pixels mapped
- [stated] Pig derotation rebuild proposed as the correct fix for east face gap and upside-down rump — not yet executed
- [stated] AbsolutRealism Bridge: Phase 3 running; v0.3.x shipped with glob-based phase directory discovery, staleness alarm, sub-tick deduplication, and WebSocket keepalive
- [stated] Bridge Phase 5 (ring-buffer video capture, Witness Axe, MCP v0.3) approved in principle, gated on outstanding pack work

## On the horizon (open items — re-verify status)

- [stated] Pig derotation rebuild: unrotated body cube with per-face `uv_rotation` — retires the rotated-cube workaround class; cures east face gap and upside-down rump natively
- [stated] CIVITAS datum table needs Abs0lum's y-value from PROVING GROUND Position readout to complete
- [stated] CIVITAS street + building infrastructure: foundations laid; full assembler/carver pipeline, substructure authoring, and Structure Unit completion loop are next build phases
- [stated] BP-02 `FALL_PEAK_TICKS = 44` recommended as an addition to the timing-assert family in the next BP-02 build (no other constant changes required)
- [stated] F5 (medium_tree_impact 695ms) held for Bridge video capture adjudication
- [stated] UV-Contract Linter findings remediation flagged: wolf (15 white faces), cat/ocelot (near-total overshoot), frog (13 orphan art blobs)
- [stated] Phase 5 Bridge gated on pack-thread completion
- [stated] Orphaned maps purge (~59.5 MB documented) awaiting approval to execute
- [stated] HISTORY-v4 synthesis pending; Wave 2 document deletions blocked until it completes (11 handoff/SKY-era documents are the sole record of the v1.2.37–v1.3.33 era)
- [stated] Ramps: he wants the gradual 14° q1–q4 ramp family (not the steeper 2-block ramps) as the standard — the gradual lift serves his future plan to create a horse-drawn wagon or carriage
- [stated] CIVITAS structure save-box law (his ruling): a building's saved box is its exact prism plus one column of clearance on the RIGHT side as seen standing on the street facing the building; its vertical extent is always the same fixed depth of subsurface infrastructure below street level plus the building's height — never world-specific coordinates, so structures work at any y and any rotation; the door is the front and faces the nearest street; the datum is the vertical zero, measuring above and below
- [stated] Wants ladders and trapdoors to be able to share one block cell when the trapdoor's hinge is opposite the ladder ("fixes many problems with ladders"); doors have the same can't-share-the-empty-space issue but it matters less
- [stated] CIVITAS construction ruling (option B): saved buildings contain no frame posts; the stud frame of `pw:frame_post` + `pw:frame_cornerpost` is the scaffolding that stands where a new building or an upgrade goes and is replaced by the walls over 3–7 days, after which the building becomes operable and a villager inhabits or works it. Frame rule he designed: a plain post's spurs go "every other" (never north+south at one level, alternating up and down and along a run); the cornerpost is free to spur in any directions and takes corners and junctions
- [stated] Wants to break down haubna's Physics Mod (Pro) to see what can be used and invent Bedrock port methods for its features (2026-09-29); has a Patreon membership for Patrix and downloads its updates
- [stated] (2026-09-30) Wants the "Pokemon catching" pack and the "Jurassic era" pack he uploaded to Drive kept in their own dedicated pack he can easily add and remove — a "dinosaurs and Pokemon catching style" fun element, not part of the main packs
- [stated] (2026-09-30) Asked for a twice-weekly scheduled Bedrock changelog watch (alpha_test / blend / _to_opaque / shadows / light_dampening / texture streaming) that messages him only when something relevant appears — created as a scheduled task (Mon + Thu mornings, his time); his long-term goal is Patrix Java-style alpha_test leaves that cast shadows

- [stated] (2026-10-02) CIVITAS structures: wants Claude to build every structure (minimum village, MVV in renovation, village v2, town v1, town v1 during upgrade, town v2, city v1), furnished with zones and stations, and he confirms each via an in-game scriptevent test; after he confirms the buildings, the villager scripts come next. Markers should be part of the structures (saved inside the file). Sizing rule: Claude's buildings tend to be too short/small — add +1 to roof level height and to the x and z floor dimensions
- [stated] (2026-10-02) Plank grid idea: neighbour-continuation ("only places next to") — a newly placed plank takes its grid tile from the older adjacent plank and never re-permutes; older planks never change when new ones are placed
- [stated] (2026-10-02) CIVITAS buildings: minimum-village roster (homes + bakery, butcher, smithy, inn, town hall, wheat farm, cattle farm, lumberyard, quarry, well) plus upgraded versions per community tier; every building slightly different from the last in layout AND fanciness, to express each villager's individuality; the ladder-hatch replaces trapdoors in buildings; canonical palette (oak frame, stone footing, plank walls, thatch/roof) accepted, other looks can be built later
- [stated] (2026-10-02) Trees: wants 16 unique tree structures per square-log species with fancy branches, based on real-life tree structure, and 16 variants per dodecagon species with no branches but accurate canopies (spruce canopy reaching much lower, out-and-down stepped); oak and birch wanted too despite being basic-looking
- [stated] (2026-10-02) CIVITAS vision: the villager / "world evolving" aspect is to be a major part of his game and a tool for the story-driven part he will add later; villages must operate, grow and evolve autonomously so his involvement is unnecessary; village dramas act as optional side quests he can join or ignore, and they continue their narrative either way; wants to develop competing markets, businesses represented in other towns (stands, branches, franchises) and their economic effects in depth; village progress runs on in-game time
- [stated] (2026-10-02) Standing art pick: when choosing between texture sources, "always pick Patrix" (exception he chose: Stratum's quartz chips for nether quartz ore, since Patrix draws it as bones)
- [stated] (2026-10-02) Realism principle: sometimes a mob or block's "purpose" is split into two categories — e.g. small mobs at real-life size are neutral/friendly and there for realism, with separate larger, easy-to-see hostile twins (rarer spawns) for encounters; wants every mob to spawn somewhere it plausibly lives so all can eventually be found by exploring
