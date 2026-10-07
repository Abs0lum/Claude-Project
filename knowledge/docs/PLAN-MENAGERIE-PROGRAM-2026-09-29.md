# PLAN — THE MENAGERIE PROGRAM: HUNDREDS OF MOB TYPES (2026-09-29, D-C288) — CONFIRMED

> **RULINGS (Abs0lum, 18:02–18:07 CT 09-29):**
> - "After reviewing the menagerie plan, yes. A-E, with E in its own namespace." → ALL lanes approved: A, V, B, C, D and E (fantasy lane in its OWN namespace).
> - Extinct animals: **IN** (dodo, sabertooth; mammoth already in).
> - Texture method: **YES** — generated coats from our recipes + photo targets, approved by family.
> - Per-biome budget: **NO LIMIT** — "I want them everywhere they would be appropriate - no limit on per biome species." Each species spawns in every biome where it would really live. §5's 10–14 cap is withdrawn. The world-load / performance measurements at each +50 types STAY as measurements, not limits: they tell us if spawn density needs tuning. Total mob counts are still governed by the game's spawn caps and each species' density limit.
> - Not re-asked, taken as the written defaults: homes (Naturalist + Nature's Touch → StripMine; our species → a new pw: Menagerie RP/BP pair); songbirds as the first factory family.

His ask (17:40 CT 09-29): "Let's continue into more mobs. Additionally, I was hoping to have hundreds of different types of mobs. Could you help me make that a reality?"
Answer: yes. The engine and our pipeline can carry it. The limit is how fast we can make good looks and good spawns, not how many ids Bedrock allows.
This plan is how we get there without turning the packs into 250 MB monsters. Confirmed 18:02 CT 09-29; M1 is next.

## 0 · Where we are (counted today, not remembered)

| What | Count | Source |
|---|---|---|
| Client entities in our mob packs (RP-06/07/08) | 196 | `_docs/convb/mob_anim_tally.json` |
| — vanilla ids with our look (Patrix Converter A/B, April, ours) | 63 | same |
| — Naturalist `sf_nba` ids | 133 = about 106 creatures + eggs/props (bird_egg, cage, plushies, info_book …) | same |
| **Distinct creatures today** | **about 170** | |
| Naturalist rigs shared by several species | 13 rigs. 6 songbirds share one bird rig; 4 snakes, 3 eels, 3 lions, 2 sharks, crow/raven and 2 hyenas each share a rig too | geometry census 17:5x |
| Patrix 26.2 mobs zip | 178 JEMs / 93 base mobs; 183 random-look textures on 18 mobs (zombie 24, illager 18, bear 12, squid 12, piglin 12 …) | range-read of its central directory, `_logs/patrix262/mobs_list.txt` |
| Vanilla mobs Patrix 26.2 has and we have NOT converted yet | 22: allay, armadillo, bat, blaze, breeze, camel_husk, cave_spider, creaking, endermite, ghast, happy_ghast, magma_cube, nautilus, parched, phantom, slime, sniffer, strider, vex, warden, wither, zombie_nautilus | same, against our 63 |
| New real species on the Drive, not in our packs | Nature's Touch v2.6 (namespace `mob:`, downloaded and unpacked 18:1x): **lady bug, mosquito, fly, wasp, queen bee** — 5 insects. **CORRECTED 18:1x (P11):** NT 'pike' is a WEAPON (sword-class polearm items), not the fish; NT 'musk' is a MOSS-COVERED ZOMBIE variant (humanoid, converts to zombie), not a musk ox → lane E. Naturalist 26.1 leftovers: dodo_bird + sabertooth_tiger exist as a MODEL + TEXTURE ONLY (no client entity, no animations, no behaviour) → we build those three layers. KC Iron Age: brown_bear, feral_hog (near-duplicates of grizzly / boar) | Drive creature census D-C286, corrected D-C288 |

**The key fact:** Naturalist already scales the way we need. **One rig + a new texture + a size + a behaviour preset + a spawn rule = a new species.** We have the same method on our side: Converter B, size_rule, the gates, the TestRunner rigs.

## 1 · What counts as a "type"

A type is a **distinct entity id** with its own name, spawn egg, spawn rule, size and look, e.g. `pw:snow_leopard`. Colour variants of one id (the 21 lizard skins, Patrix's 24 zombie looks) do not count as types. They multiply the variety you see inside each type, and we use them too.

## 2 · The lanes to hundreds

| Lane | What | Adds types | Effort per type | Notes |
|---|---|---|---|---|
| **A — sources we hold** | Nature's Touch insects: lady bug, mosquito, fly, wasp, queen bee; dodo + sabertooth (extinct — IN) | +5 (+2) | S (insects) / M (dodo, sabertooth: we add entity + animations + behaviour) | third-party content → the StripMine (Realm) pack, personal use |
| **V — vanilla completion** | the 22 unconverted Patrix vanilla mobs (the "flying wave": bat, phantom, allay, vex, ghast, happy ghast, blaze, breeze, wither …) | 0 new types, 22 new looks | M | makes every vanilla mob ours; Patrix porting permitted |
| **B — species on shared rigs** | the Naturalist method at scale: new species on rigs we already have | about +110 | S–M | the bulk of the hundreds; see §3 |
| **C — new rigs** | body plans nobody has given us (crocodilians, mustelids, marsupials, camelids …) | about +40 | M–L | original pw: work; Converter B tools + our own modelling |
| **D — your packs** | any creature add-ons you own and drop on the Drive | varies | S | same census + port pipeline; personal use |
| **E — fantasy (APPROVED, own namespace)** | Nature's Touch extras (musk the moss zombie, cluckshroom, red phantom, ruby turtle, zombified pig …) | varies | S | its own namespace (default `pwf:`), kept apart from the real-world species |

Rough count after lanes A + B + C: **about 170 → about 330 distinct creatures**, and more with D/E.

## 3 · Lane B — the families (first-pass candidate list; you edit it)

| Family (existing rig) | Candidate new species | + |
|---|---|---|
| Songbirds (`sf_nba.bird`) | blue tit, goldfinch, starling, wren, mockingbird, oriole, tanager, bullfinch, swallow, chickadee, warbler, nightingale | 12 |
| Corvids (`sf_nba.corvid`) | magpie, jackdaw | 2 |
| Waterbirds & raptors (duck / goose / eagle / owl / vulture / flamingo rigs) | swan, heron, pelican, stork, crane, hawk, falcon, osprey, barn owl, snowy owl | 10 |
| Snakes (`sf_nba.snake`) | python, king cobra, garter snake, milk snake, green mamba, adder | 6 |
| Lizards (lizard rig) | gecko, anole, skink, monitor (juvenile scale) | 4 |
| Big cats (lion / tiger rigs) | leopard, jaguar, cheetah, snow leopard, cougar | 5 |
| Canids (coyote rig) | jackal, dingo, arctic fox, maned wolf | 4 |
| Deer (deer / moose rigs) | elk, reindeer, red deer, fallow deer, roe deer | 5 |
| Bears (grizzly / black bear rigs) | brown bear, sun bear, spectacled bear | 3 |
| Hoofed (zebra / rhino / boar / cow / goat rigs) | bison, musk ox, water buffalo, yak, warthog, ibex, bighorn sheep, wild boar | 8 |
| Freshwater & sea fish (bass / catfish / piranha / cod / salmon rigs) | trout, perch, pike, carp, sturgeon, tuna, mackerel, sardine, grouper, snapper, barracuda, marlin, angelfish, clownfish, tilapia | 15 |
| Sharks & rays (shark / ray rigs) | tiger shark, whale shark, manta ray, stingray | 4 |
| Insects (butterfly / dragonfly / beetle / firefly rigs) | monarch, swallowtail, luna moth, stag beetle, rhino beetle, bumblebee, grasshopper, cricket, mantis, cicada | 10 |
| Arthropods (crab / scorpion rigs) | hermit crab, lobster, crayfish, tarantula | 4 |
| Small mammals (hamster / rat / squirrel rigs) | mouse, chipmunk, marmot, prairie dog, guinea pig, vole | 6 |
| Primates (monkey / gorilla rigs) | chimpanzee, orangutan, baboon | 3 |
| Marine mammals (seal / walrus / orca / whale rigs) | sea lion, humpback, narwhal, beluga, manatee | 5 |
| **Total** | | **≈ 106** |

(Correction D-C288: Nature's Touch's 'musk' and 'pike' turned out to be a moss zombie and a weapon, so musk ox and pike the fish come only from this lane.)

## 4 · The factory — what makes hundreds possible instead of hand-made one at a time

1. **Species catalog.** One row per species: id · common name · rig · real size (m) · biomes · spawn weight / group size · behaviour preset · texture recipe · sounds · status.
   - It lives as a **spreadsheet you can edit**: add or remove species, move biomes, set rarity.
   - The builder reads it, so the catalog is the source of truth.
2. **Rig library.** About 25 rigs (Naturalist, Patrix and new), each with a bone contract, its animations, a hold point where needed and a size basis.
3. **Behaviour presets (BP).** About 10 archetypes:
   - grazer herd, browser, small critter, stalker predator, pack hunter
   - songbird flock, raptor, waterfowl, fish school, ambient insect
   - Each preset is one BP entity template. A species overrides only its numbers: health, speed, diet, breeding item, prey list.
4. **Texture recipes.** New species on a shared rig need their own coat, painted onto that rig's UV layout.
   - A generator builds the base coat from layers: base colour, countershaded belly, and a pattern mask (stripes, spots, rosettes, barring).
   - Colour targets come from reference photos. Photos are visual targets only; the CC0 rule for production textures stands.
   - You approve each family by eye before it ships (P1: static ≠ runtime).
   - **Honest limit:** generated coats will not match Patrix hand-painted quality on the first pass. The family sheet preview + your witness is where we tune.
5. **Sizes.** `size_rule.py` real-life sizes against your 5'10" character, the same law as today.
6. **Gates** (all standing): MLS · ARS · RCV · FMT · RBW · PREC · **ATT (new, D-C288)**, plus three new ones:
   - a **spawn-rule lint**: every biome filter resolves, and no species has zero biomes;
   - a **catalog gate**: every row is built, and nothing is built that isn't in a row;
   - a **budget gate**: pack size (the per-biome cap was withdrawn by ruling).
7. **Tests.** TestRunner "zoo walk" lineups (8–12 species per step in pens, one screenshot per step) plus a **spawn-census step** (after N minutes in a biome, count what spawned).

## 5 · Budgets (the laws that keep hundreds healthy)

- **Pack size (≤ 250 MB, your law).**
  - Textures dominate. All 1,560 Naturalist textures total 13.3 MB. A shared-rig species is about 0.1–0.3 MB with its baby and variants.
  - So 300 new species is about 30–90 MB, which is one new pack pair with room to spare.
  - Ownership law: original `pw:` species get their own pair, working name **Menagerie RP/BP**. Naturalist- and Nature's-Touch-derived content stays in StripMine (personal use).
- **World load.** More types do not mean more mobs: total animals are set by the game's spawn caps and our density limits.
  - ~~The per-biome budget proposal: 10–14 animal types per biome~~ — WITHDRAWN by ruling: no per-biome cap; every species goes everywhere it would really live (biome filters come from each species' real range).
  - **To measure, not assume:** world-load time and memory on PS5 and on your phone at each +50 types. The runner can time the load and count entities.
- **Sounds.** Naturalist sounds already live in StripMine. New species reuse sound sets by archetype (grazer / songbird / big cat …). Dedicated sounds are a later polish lane.

## 6 · Waves (each one is a normal round: build → gates → delivery → runner lineup → your witness)

| Wave | Content | Types after |
|---|---|---|
| **M1** (approved) | NT insects ×5 → StripMine · dodo + sabertooth (entity + animations + behaviour on the Naturalist tiger / ostrich-class rigs) · NT musk (moss zombie) → lane E namespace · catalog skeleton · (ATT gate: DONE in Round 13) | ≈ 177 (+1 fantasy) |
| **M2 — the factory proof** | songbirds (+12) on the proven bird rig: catalog → texture generator → preset → spawn rule → zoo walk, end to end | ≈ 190 |
| M3–M6 | families in batches of 15–30, in the order you pick (cats · deer · fish · insects · waterbirds …) | ≈ 290 |
| M7+ | Lane C new rigs | ≈ 330+ |
| V (parallel, any time) | vanilla completion: the 22 unconverted Patrix mobs (flying wave first) | 0 new types, 22 new looks |

## 7 · Decisions — ANSWERED 18:02–18:07 (see the rulings at the top)

1. **Homes:** Naturalist + Nature's Touch content → StripMine; our original species → a new `pw:` Menagerie RP/BP pair. OK?
2. **Real-world only**, or a fantasy lane too (own namespace)?
3. **Texture method** for new species: generated coats from our recipes + photo targets, approved by family (recommended). Or a slower hand-authored route for the hero species you name.
4. **First family** after M1 (recommendation: songbirds, because the rig is proven).
5. **Per-biome budget:** 10–14 animal types per biome (recommended), or another number.
6. **Extinct animals** (dodo, sabertooth, mammoth already in): in or out?

## 8 · M1 build spec (D-C288, from the unpacked Nature's Touch v2.6 Hotfix 3 + the Naturalist 26.1 listing)

| Phase | Work | Output |
|---|---|---|
| M1-a | Port the 5 NT insects: BP entity + spawn rules + loot + spawn eggs; RP client entity + geometry + animations + render controllers + textures + sounds + lang. Ids stay `mob:<name>`, the way the Naturalist port kept `sf_nba:`. Spawn biomes come from each insect's real range (no per-biome cap, per ruling). | StripMine BP 1.3.4 + StripMine RP 3.1.0. The ownership wave's Naturalist move takes the next number when it ships (never reuse). |
| M1-b | Dodo + sabertooth: Naturalist 26.1 model + texture, plus our client entity, animations (from the sf_nba tiger / ostrich-class rigs) and behaviour presets (sabertooth = stalker predator; dodo = ground bird), at real sizes. | same packs |
| M1-c | NT musk (moss zombie) → lane E, in its own namespace (default `pwf:` = pw fantasy; any later fantasy species share it). | same packs, own namespace |
| M1-d | Gates (MLS · ARS · RCV · FMT · RBW · ATT · PREC + spawn-rule lint), TestRunner p9 zoo walk (one pen per species, dodo/sabertooth size row next to your 5'10" figure), delivery. | shipped round |
