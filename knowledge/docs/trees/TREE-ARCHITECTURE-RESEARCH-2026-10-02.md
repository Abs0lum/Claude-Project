# TREE-ARCHITECTURE-RESEARCH — real-world form data for voxel tree generation (1 block = 1 m)

- Date: 2026-10-02
- Scope: real tree architecture for nine Minecraft tree families (oak, birch, spruce, jungle, dark oak, pale oak, acacia, cherry, mangrove), three life stages each, translated to block scale.
- Status: research reference only. No code. Every number is either cited inline or tagged **(estimate)**. Block-scale sections are design suggestions derived from the cited numbers, not engine law; they still need witness verification in-game.
- Companion doc: `/home/claude/_docs/trees/branch/BRANCH-GEOMETRY-RESEARCH.md` (what branch directions and thicknesses the engine can draw). This doc says what *shape* to aim for; that doc says what geometry is legal.

## 0 · Conventions and terms

- **DBH** — trunk diameter at breast height (1.3–1.4 m). Girth (circumference) = π × DBH, so a 6 m girth ≈ 1.9 m DBH.
- **HCB** — height to crown base (lowest live branch). **Crown ratio (CR)** = live crown length / total height = (H − HCB) / H.
- **Spread** = crown diameter (edge to edge). **Crown radius** = spread / 2.
- **Open-grown** = no neighbours touching the crown (park, field edge, savanna). **Forest-grown** = closed stand. Open-grown trees are shorter, wider, with low crown bases; forest-grown trees are taller for their diameter, narrower, with high crown bases. Every number below says which it is.
- **Excurrent** = one dominant leader to the top (cone-shaped crowns). **Decurrent** = leader lost or shared among several big limbs (dome / vase / umbrella crowns).
- Branch angle is given as **degrees from the trunk axis** (0° = straight up along the trunk, 90° = horizontal, >90° = pointing below horizontal).
- "Order" of branching: trunk = order 0, scaffold limbs = order 1, their branches = order 2, and so on.

## 1 · Cross-species foundations (use these everywhere)

### 1.1 Architectural models (the "growth rule" behind each species)
- Botanists classify tree architecture with the Hallé–Oldeman models. Relevant ones:
  - **Massart's model** — a single upright (orthotropic) trunk with regular **tiers of horizontal (plagiotropic) branches**. Temperate examples: *Abies, Picea, Sequoia, Cedrus* ([Pfisterer 2000, Modern models in tree architecture](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)). Tropical example: ***Ceiba pentandra*** ([LibreTexts — Architectural Models of Tropical Trees](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)). → spruce and young kapok both build **tiers**.
  - **Rauh's model, "fruit-tree shape"** — all axes grow upward, buds in a spiral, flexible crown. Examples: most *Quercus* (except *Q. rubra/palustris*), *Juglans, Crataegus, Sorbus* ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)). → oaks have no tiers; branches leave the trunk irregularly and turn upward.
  - **Attims' model** — all axes upright, continuous trunk growth. Example: *Rhizophora racemosa* (mangrove) ([LibreTexts](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)).
  - **Nozeran's model** — trunk built by a stack of upright segments, each ending in a whorl of horizontal fan branches. Example: *Theobroma cacao* ([LibreTexts](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)).
- Age rule shared by all broadleaves: "young trees may develop a leader, aged crowns usually are polyarchic" — the hierarchy weakens and many co-equal limbs take over once apical dominance is lost ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)). New shoots from dormant ("sleeping") buds produce sucker-like reiterated mini-crowns — the source of epicormic shoots on old oaks (same source).

### 1.2 Crown width from trunk diameter (open / free-growing broadleaves)
- Hemery, Savill & Pryor (2005) fitted crown diameter **K (m) = a + b × DBH (m)** for British broadleaves ([Hemery et al. 2005, PDF](https://benfieldgroup.uk/wp-content/uploads/2021/09/Hemery_et_al_2005_kd_paper.pdf)):

| Species | a | b | r² | K/DBH at 20 cm | at 40 cm | at 60 cm |
|---|---|---|---|---|---|---|
| Oak (*Q. robur* + *Q. petraea*) | 1.717 | 15.616 | 0.911 | 24.2 | 19.9 | 18.5 |
| Birch (*Betula* spp.) | 0.975 | 16.151 | 0.922 | 20.9 | 19.3 | 18.7 |
| Wild cherry (*Prunus avium*) | 1.760 | 15.40 | 0.840 | 24.2 | 19.8 | 18.3 |

- Rule of thumb from the table: **crown diameter ≈ 16 × DBH + 1.5 m**; ratios are higher in young trees and stabilise from ~30 cm DBH (same source).
- Worked values (computed with Python from the equations above):
  - Oak: DBH 0.2 → 4.8 m; 0.5 → 9.5 m; 1.0 → 17.3 m; 1.5 → 25.1 m **(1.5 m is an extrapolation beyond the fitted range — estimate)**.
  - Birch: DBH 0.2 → 4.2 m; 0.3 → 5.8 m; 0.5 → 9.1 m.
  - Cherry (*P. avium*): DBH 0.2 → 4.8 m; 0.5 → 9.5 m.
- The UK woodland allometry dataset uses the same form (CRad = a·DBH^b) and a saturating height curve H = 1.35 + (Hmax − 1.35)(1 − e^(−b·DBH)) ([Scientific Data 2015](https://www.nature.com/articles/sdata20156)) — i.e. height plateaus while crowns keep widening. That is the core reason old trees look **wider, not taller**.

### 1.3 Crown base rises with competition
- Height to crown base increases with competition; "trees of the same diameter or height usually have a larger HCB than that in the sparse stands" (Norway spruce and beech, 19,404 trees) ([PLOS ONE — Modelling HCB of Norway spruce and beech](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0186394)). → open-grown variants must have **low** crown bases; forest variants **high** ones.
- Live crown ratio is the standard forestry measure of this ([Open Oregon — Forest Measurements, Live Crown Ratio](https://openoregon.pressbooks.pub/forestmeasurements/chapter/5-4-live-crown-ratio/)).

### 1.4 Conifer whorls = years
- In whorled conifers, "each whorl of branches and the stem growth immediately above it (up to the next whorl) represent one year of growth" ([Open Oregon — Forest Measurements, Young trees](https://openoregon.pressbooks.pub/forestmeasurements/chapter/4-3-young-trees/)). → **whorl spacing = annual leader growth.**

### 1.5 Old age = retrenchment, not growth
- Ancient phase: the trunk keeps thickening while the crown "becomes smaller, growth is concentrated nearer the trunk"; retrenched crowns are "smaller and closer to the ground" with a "stag-headed appearance" from dead branches standing above new growth ([Woodland Trust — Recognising and categorising ancient and veteran trees](https://www.woodlandtrust.org.uk/media/53779/recognising-and-categorising-ancient-and-other-veteran-trees.pdf)).
- "Oaks shorten with age in order to extend their lifespan" ([Woodland Trust — English oak](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/english-oak/)).

---

## 2 · OAK → *Quercus robur* (English/pedunculate oak) and *Quercus alba* (white oak)

**Why these:** vanilla oak is the generic broadleaf; *Q. robur* is the archetypal European park/field oak, *Q. alba* the North American equivalent. Both follow Rauh's "fruit-tree" model (§1.1).

### 2.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young / pole (20–40 yr) | 6–15 m **(estimate)** | 0.1–0.3 m **(estimate)** | 3.3–6.4 m (Hemery eq. at 0.1–0.3 m) | open: 1–2 m; forest: 3–6 m **(estimate)** | single leader still present |
| Mature (80–250 yr) | *Q. robur* 20–40 m ([Woodland Trust](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/english-oak/)); "up to 30 m" ([Forestry England](https://www.forestryengland.uk/tree-species/english-oak)). *Q. alba* 18–24 m ([Minnesota DNR](https://www.dnr.state.mn.us/trees/white-oak.html)), 18–30 m ([UF/IFAS ST541](https://ask.ifas.ufl.edu/publication/ST541)) | *Q. alba* 0.6–0.9 m ([MN DNR](https://www.dnr.state.mn.us/trees/white-oak.html)); *Q. robur* 0.6–1.4 m **(estimate)** | *Q. alba* 15–24 m ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST541)); Hemery eq. 9.5–17 m at DBH 0.5–1.0 m | open: 2–5 m (CR 0.75–0.9); forest: 8–15 m (CR 0.35–0.55) **(estimate)** | broad, spreading |
| Old / veteran (300 yr+) | shorter than mature — crown retrenched (§1.5); 15–25 m **(estimate)** | girth > 4.5 m recording threshold (DBH > 1.4 m); "most chronologically ancient oak are greater than 6 m in girth" (DBH > 1.9 m), up to 10 m+ girth (DBH ≈ 3.2 m) ([Woodland Trust ATI — oak guide](https://ati.woodlandtrust.org.uk/how-to-record/species-guides/oak/)) | 20–30 m before retrenchment, shrinking after **(estimate)** | 2–4 m open **(estimate)** | ancient characteristics from ~300 yr; chronologically ancient from 400 yr; lifespan up to 1,000 yr, 600 typical ([ATI oak guide](https://ati.woodlandtrust.org.uk/how-to-record/species-guides/oak/)) |

- Ratios (open-grown mature): spread/height ≈ 0.8–1.2; *Q. alba* catalogue values give 50–80 ft spread on 60–100 ft height = 0.8 ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST541)). Forest-grown: spread/height ≈ 0.35–0.5 **(estimate)**.

### 2.2 Growth habit
- Young: excurrent, single leader. Mature: becomes **decurrent** — the leader is lost among several co-dominant limbs ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf), polyarchic old crowns).
- Open-grown *Q. alba*: "rugged, irregular crowns that are wide spreading, with a stocky bole"; forest-grown: "upright and oval" ([Virginia Tech Dendrology — white oak](https://dendro.cnre.vt.edu/dendrology/syllabus/factsheet.cfm?ID=35)). Open-grown limbs "spread irregularly from the main trunk"; forest trees branch more vertically ([MN DNR](https://www.dnr.state.mn.us/trees/white-oak.html)).
- Trunk forks (open-grown): main fork at 0.15–0.35 × H (3–8 m on a 20–25 m tree) **(estimate)**.
- Primary scaffold limbs: 3–6, rarely >8 **(estimate)**.
- Insertion angles: upper scaffolds 30–50° from trunk, rising; middle 50–70°; lowest open-grown limbs 70–90° (near horizontal) and long, often dipping then turning up at the ends **(estimate)**. Limb paths are **sinuous/kinked** — oak shoots stop and restart from clustered end buds, so each year's segment changes direction slightly **(estimate — based on Rauh model spiral buds; no numeric source found)**.

### 2.3 Branch orders and taper
- Visible orders: 3 in young trees, 4–5 in mature crowns **(estimate)**.
- Primary limb length ≈ 0.7–1.0 × crown radius (lowest limbs reach the crown edge, upper limbs reach 0.5–0.7 × radius before splitting) **(estimate)**.
- Limb spacing up the trunk: irregular, 1–3 m between scaffolds; no whorls **(estimate)**.
- Diameter taper: a scaffold limb leaving the trunk is ~0.3–0.6 × trunk DBH **(estimate)**.

### 2.4 Silhouette and foliage
- Young: ovoid / egg. Mature open-grown: broad dome, roughly as wide as tall, lobed outline ("broad and spreading crown with sturdy branches beneath" — [Woodland Trust](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/english-oak/)). Forest: narrow oval.
- Foliage is an **outer shell 1.5–3 m thick in clumps** around each limb end, with visible gaps between clumps where limbs diverge; the interior near the trunk is mostly bare wood **(estimate)**.

### 2.5 Distinctive features
- Stocky bole with root flare; heavy low limbs on open-grown trees ([VT Dendrology](https://dendro.cnre.vt.edu/dendrology/syllabus/factsheet.cfm?ID=35)).
- Epicormic shoots (sprouts from dormant buds) along the trunk and big limbs after release or damage ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)).
- *Q. alba* bark: "whitish, scaly, and flaking in irregular blocks or plates with age" ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST541)). Also a source for pale oak (§7).

### 2.6 Block-scale translation
- **Young oak:** 7–12 blocks tall, 1-block trunk (or thin custom geometry), crown base at 2–3 blocks, crown radius 2–3, ovoid; 1 leader + 3–5 short side limbs at 45–60°.
- **Mature oak (open-grown):** 16–24 blocks tall, trunk 1–2 blocks wide (2×2 above DBH ~1.5 m only), main fork at 4–7 blocks, **3–5 scaffold limbs** at 40–80° from vertical, crown radius **7–11 blocks** (spread ≈ 0.8–1.1 × height), crown base 3–5 blocks. Leaf clumps of radius 2–3 at limb ends, with 1–2 block gaps between clumps.
- **Mature oak (forest-grown variant):** 20–28 blocks tall, crown base 9–14 blocks, crown radius 4–6.
- **Old oak:** 14–20 blocks tall (shorter than mature), 2×2 or 3×3 trunk, crown radius 8–12 but with 1–3 dead stag-head limbs poking 2–4 blocks above the live crown (§7 for full veteran treatment).
- **Vary across 16 variants:** (1) number of scaffolds 3–6; (2) fork height 0.15–0.35 × H; (3) spread/height 0.7–1.2; (4) azimuth asymmetry (one heavy side, §11).

---

## 3 · BIRCH → *Betula pendula* (silver birch) and *Betula papyrifera* (paper birch)

**Why these:** white-barked birches; *B. pendula* gives the slender drooping European form, *B. papyrifera* the North American (often multi-stem) form.

### 3.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young (5–20 yr) | 4–12 m **(estimate)**; paper birch "grows rapidly", ~20 cm DBH after 30 yr ([Silvics of North America — paper birch](https://www.forestasyst.org/hardwoods/papyrifera.htm)) | 0.05–0.2 m | 2.6–4.2 m (Hemery eq. at 0.1–0.2 m) | open: 0.5–2 m; forest: 3–6 m **(estimate)** | narrow cone |
| Mature (30–70 yr) | *B. pendula* up to 30 m, usually ~15 m ([First Nature](https://www.first-nature.com/trees/betula-pendula.php)); 30 m max ([Woodland Trust — silver birch](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/)). Paper birch mature stands average 21 m ([Silvics](https://www.forestasyst.org/hardwoods/papyrifera.htm)) | paper birch 0.25–0.30 m average in stands, occasionally > 0.76 m (same source) | 4.8–9.1 m (Hemery eq. at 0.25–0.5 m) → spread/H ≈ 0.3–0.5 | open: 2–4 m (CR 0.7–0.85); forest: 8–12 m (CR 0.35–0.5) **(estimate)** | light canopy |
| Old (70+ yr) | similar to mature, top thinning | 0.4–0.6 m **(estimate)** | 8–11 m **(estimate)** | rising | short-lived: *B. pendula* 80–100 yr ([First Nature](https://www.first-nature.com/trees/betula-pendula.php)), up to 150 ([EUFORGEN](https://www.euforgen.org/species/betula-pendula)); paper birch matures 60–70 yr, few live beyond 140–200 ([Silvics](https://www.forestasyst.org/hardwoods/papyrifera.htm)) |

### 3.2 Growth habit
- Excurrent in youth and middle age: "a single trunk with attractive pendulous branches" ([First Nature](https://www.first-nature.com/trees/betula-pendula.php)). Leader weakens late; old crowns become irregular **(estimate)**.
- Paper birch: crown "narrow, oval-shaped" in forest, "pyramid-shaped" in the open, "often with many stems" ([BC Ministry of Forests — Paper birch](https://www.for.gov.bc.ca/hfd/library/documents/treebook/paperbirch.htm)); prolific stump sprouting produces clumps ([Silvics](https://www.forestasyst.org/hardwoods/papyrifera.htm)).
- Branch angles: main branches **ascending at 30–50°** from the trunk, the twigs and outer branches **hanging** ("elegant, drooping branches" — [Woodland Trust](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/)). The arc is: up and out from the trunk, then curving over so the outer third hangs **(angles: estimate)**.
- Scaffolds: no large scaffolds — many (10–25) thin, roughly similar branches along the upper 2/3 of the trunk **(estimate)**.

### 3.3 Branch orders and taper
- Visible orders: 2–3. Branches are thin relative to trunk (≤ 0.2 × DBH) **(estimate)**.
- Primary branch length ≈ crown radius at mid-crown; short near the top → slim cone or narrow oval **(estimate)**.
- Spacing: 0.3–0.8 m apart, spiral, no whorls **(estimate)**.

### 3.4 Silhouette and foliage
- Narrow cone (young) → narrow oval / column with a rounded or slightly ragged top (mature). Width/height 0.3–0.5.
- "Light canopy" ([Woodland Trust](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/)): foliage is **sparse and see-through**, in hanging curtains on branch tips; small gaps everywhere rather than big holes **(estimate for the voxel interpretation)**.

### 3.5 Distinctive features
- Bark: white, peeling "like tissue paper", becoming "black and rugged at the base" with "dark, diamond-shaped fissures" as trees mature ([Woodland Trust](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/)); "diamond-shaped black protrusions on the lower trunk" ([First Nature](https://www.first-nature.com/trees/betula-pendula.php)). Paper birch bark peels in papery strips, inner bark orange, turns black with age ([BC MoF](https://www.for.gov.bc.ca/hfd/library/documents/treebook/paperbirch.htm)).
- Slight trunk lean and gentle S-curve are common in pioneer stands **(estimate)**.
- Multi-stem clumps of 2–5 stems from one base (paper birch) ([BC MoF](https://www.for.gov.bc.ca/hfd/library/documents/treebook/paperbirch.htm); stem count estimate).

### 3.6 Block-scale translation
- **Young birch:** 6–9 blocks, 1-block (or thinner) trunk, crown base 2 blocks, radius 1–2, slim cone.
- **Mature birch:** 14–20 blocks, crown base 4–7 (open) or 9–12 (forest), **radius 3–4** (never wider than ~0.5 × height), many short branches, outer leaf blocks hanging 1–2 blocks below each branch tip.
- **Old birch:** 16–22 blocks, bark texture switches to black-fissured on the lowest 2–4 blocks, top 2–3 blocks sparse/dead, crown slightly lopsided.
- **Vary:** (1) single vs 2–4 stems (paper-birch clumps, maybe 4 of 16 variants); (2) trunk lean 0–8° and S-curve; (3) crown base height; (4) droop strength of outer branches.

---

## 4 · SPRUCE → *Picea abies* (Norway spruce), compared with *P. glauca* (white) and *P. engelmannii* (Engelmann)

**Why Norway spruce:** the archetypal Christmas-tree spruce with the most pronounced drooping branchlets; white and Engelmann span the narrow-crowned alternatives. Architecture is **Massart's model** — single straight trunk, regular tiers ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)).

### 4.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young (5–25 yr) | 2–15 m; can grow "up to 1 m per year for the first 25 years under good conditions" ([Wikipedia — Picea abies](https://en.wikipedia.org/wiki/Picea_abies)) | 0.05–0.25 m **(estimate)** | ≈ 0.5 × H open-grown **(estimate from catalogue ratios below)** | **open: 0–0.5 m** — live branches at ground level **(estimate)**; forest: rising quickly | "stiffly conical" when young ([Virginia Tech HORT-20](https://www.pubs.ext.vt.edu/HORT/HORT-20/HORT-20.html)) |
| Mature (30–120 yr) | forest 35–55 m ([Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)), 40–60 m ([Trees and Shrubs Online](https://www.treesandshrubsonline.org/articles/picea/picea-abies/)); open-grown/landscape 12–18 m ([Morton Arboretum](https://mortonarb.org/plant-and-protect/trees-and-plants/norway-spruce/)), ~18 m ([VT HORT-20](https://www.pubs.ext.vt.edu/HORT/HORT-20/HORT-20.html)), 23–30 m ("75 feet in 50 years", [Iowa State](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)) | 1–1.5 m in old forest trees ([Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)); 0.4–0.8 m typical mature open **(estimate)** | landscape: 7.6–9 m on 12–18 m ([Morton](https://mortonarb.org/plant-and-protect/trees-and-plants/norway-spruce/)); 9 m on 18 m ([VT](https://www.pubs.ext.vt.edu/HORT/HORT-20/HORT-20.html)); 12–15 m on 23–30 m ([Iowa State](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)) → **spread/H = 0.5–0.6 open-grown** | **open: 0–2 m** (CR 0.9–1.0); forest: 0.4–0.6 × H (CR 0.4–0.6) **(estimate)** | conical |
| Old (150–300+ yr) | 30–50 m forest; growth "becomes slower once over 20 m" ([Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)) | 1–1.5 m, "1.5–2 m dbh would seem to be a maximum" ([TSO](https://www.treesandshrubsonline.org/articles/picea/picea-abies/)) | slightly wider; top blunter **(estimate)** | open trees often lose shaded lowest whorls → 1–4 m **(estimate)** | life to ~300 yr in native range; oldest ring-dated individual 532 yr ([Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)) |

Comparison species:
- *P. glauca*: 15–30 m, trunk to 1 m; crown "narrow conical" young, "columnar with a conical top in older trees" ([Wikipedia — Picea glauca](https://en.wikipedia.org/wiki/Picea_glauca)); "broad, conical crown" with "long, stout branches" ([MN DNR — white spruce](https://www.dnr.state.mn.us/trees/white-spruce.html)); mature height 15–30 m ([USDA Woody Plant Seed Manual — Picea](https://www.fs.usda.gov/nsl/Wpsm/Picea.pdf)).
- *P. engelmannii*: occasionally > 50 m, "dense, symmetrical, narrow, spire-like crown; lower branches sloping downward", "long, narrow crowns", self-prunes less than subalpine fir ([BC silvics — Engelmann spruce](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/tree-species-selection/silvics_se.pdf)); 25–30 m typical ([USDA WPSM](https://www.fs.usda.gov/nsl/Wpsm/Picea.pdf)). Spread/H ≈ 0.2–0.3 **(estimate)** — the narrowest of the three.

### 4.2 How low the crown reaches (the key spruce fact)
- Spruces are poor self-pruners when not shaded. In black spruce, branches are "distributed from ground to crown" and dead lower branches "are usually retained" ([USFS FEIS — Picea mariana](https://www.fs.usda.gov/database/feis/plants/tree/picmar/all.html)); Engelmann self-prunes less than its fir associate ([BC silvics](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/tree-species-selection/silvics_se.pdf)).
- Lowest branches of spruce can be pressed to the ground and root there (layering): Old Tjikko's "low-lying branches" are pushed "to ground level, where they take root" ([Wikipedia — Old Tjikko](https://en.wikipedia.org/wiki/Old_Tjikko)).
- Crown base only rises through **shading by neighbours** (§1.3 — [PLOS ONE HCB model](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0186394)).
- **Working numbers (estimate, consistent with the above):** open-grown young/mature Norway spruce: lowest live whorl 0–1 m above ground; because those branches droop, their **tips rest on or within ~0.5 m of the ground**. Open-grown old trees: 0–2 m (shaded lowest whorls may die). Forest-grown: crown base 40–60% of height, the bare stem below carrying dead branch stubs.

### 4.3 Tiers, whorls, branch angle and droop
- Whorl spacing = annual height growth (§1.4). Vigorous young Norway spruce: up to ~1 m/yr ([Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)); average over 50 years ≈ 0.46 m/yr (75 ft in 50 yr — [Iowa State](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)). So **whorls every 0.3–1.0 m**, widest-spaced in the vigorous middle of the trunk and tightening near the top of old trees (0.1–0.3 m) and on stressed trees **(spacing range at extremes: estimate)**.
- Branches per whorl: 4–6 main branches plus smaller **interwhorl** branches between whorls **(estimate; whorl count per whorl not found in a fetched source)**. Branch count per whorl falls as trees get more slender (higher H/D ratio) ([2007 study — branch models for Norway spruce at wide spacings, abstract](https://www.sciencedirect.com/science/article/abs/pii/S0378112707000357)).
- Angles: "Branches short and stout, the upper level or ascending, the lower drooping" ([Conifers.org — Picea abies](https://www.conifers.org/pi/Picea_abies.php)). First-order branches "soon spreading horizontally or bowed downward"; second-order branches "somewhat to extremely pendulous, more so with age" ([TSO](https://www.treesandshrubsonline.org/articles/picea/picea-abies/)). Measured branching angles in young spruce crowns 40–70° ([study: crown architecture of young Norway spruce](https://www.researchgate.net/publication/331178478_Crown_architecture_and_structural_development_of_young_Norway_spruce_trees_Picea_abies_Karst_A_basis_for_more_realistic_growth_modelling)).
- **Angle profile by height (estimate, built from the qualitative statements above):** top 1/5 of crown: 45–70° from trunk (ascending); middle: ~80–95° (level); bottom 1/3: 95–120° (out then down) with the outer half of each branch bowing further down and the very tip often curling slightly upward ("drooping branches with upturned ends" is documented for black spruce — [FEIS](https://www.fs.usda.gov/database/feis/plants/tree/picmar/all.html); for Norway spruce it is an estimate).
- **The stepped "out and down" look:** each tier = a ring of near-horizontal primary branches from one whorl, with pendulous second-order branchlets hanging as a curtain below them ("secondary branches hang from the primary horizontal branches" — [VT HORT-20](https://www.pubs.ext.vt.edu/HORT/HORT-20/HORT-20.html); "pyramidal with branches that hang down" — [Iowa State](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)). The outer edge of each tier sits lower than its point of attachment; the next tier up starts above, leaving a dark shadow band — that alternation is the visible step **(geometry: estimate)**.
- Lower branches of old trees: long twigs that "hang down and sway in the wind" ([Utah State Tree Browser](https://extension.usu.edu/treebrowser/catalog/spruce-norway)).

### 4.4 Branch orders, lengths, silhouette
- Visible orders: 2–3 (primary branches, pendulous secondaries, tertiary twigs). In the young-spruce study most growth units were order 1–2 (26.7% order 1, 52.8% order 2) ([young Norway spruce crown study](https://www.researchgate.net/publication/331178478_Crown_architecture_and_structural_development_of_young_Norway_spruce_trees_Picea_abies_Karst_A_basis_for_more_realistic_growth_modelling)).
- Primary branch length at a given height ≈ crown radius at that height; **radius grows almost linearly from 0 at the tip to its max in the lowest third** → a straight-sided cone for young/mature trees; old trees bulge slightly in the lower half and blunt the top **(estimate)**. "Crown conic" ([Conifers.org](https://www.conifers.org/pi/Picea_abies.php)).
- Silhouette proportions: Norway open-grown width/height 0.5–0.6 (cited ratios §4.1); white spruce slightly narrower and more columnar when old; Engelmann a narrow spire (≈0.2–0.3, estimate).
- Foliage: dense on the outer and upper surface of each tier, hollow and dark near the trunk (inner shoots shaded out); needles mostly on the upper side of shoots ([Iowa State](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)) **(hollow-interior statement: estimate)**.

### 4.5 Distinctive features
- Perfectly straight single trunk; very rarely forked except after leader damage **(estimate)**.
- Long hanging cones (9–17 cm, longest of any spruce — [Wikipedia](https://en.wikipedia.org/wiki/Picea_abies)) in the upper crown.
- Old bark grey-brown and scaly ([Conifers.org](https://www.conifers.org/pi/Picea_abies.php)); rapid taper above the base on the largest trees (same source).
- Dead lower branch stubs on forest-grown trees ([FEIS](https://www.fs.usda.gov/database/feis/plants/tree/picmar/all.html) for the genus pattern).

### 4.6 Block-scale translation
- At 1 m blocks, one annual whorl (0.3–1 m) is at or below block size. Recommended: **draw one visible tier per 1 block on young trees (whorls ~1 m) and per 2 blocks on mature/old trees**, each tier being several merged annual whorls **(design estimate)**.
- **Young spruce (open):** 6–10 blocks tall, lowest tier at **block 0–1** (touching or one above ground), bottom radius 2–3 blocks (≈0.3–0.5 × H), tier every 1 block, radius shrinking ~1 block per 2–3 tiers, single leader 1–2 blocks above the top tier.
- **Mature Norway spruce (open):** 20–30 blocks tall, lowest branches **0–2 blocks up**, bottom tier tips resting **on the ground or 1 block above**, tiers every **2 blocks**, bottom radius **5–7 blocks** (spread ≈ 0.5 × H) tapering linearly to 0. Each tier: horizontal for the inner half, dropping 1 block at the outer half (lower third of crown: drop 1–2 blocks), top 1/5 tiers angled upward.
- **Mature spruce (forest variant):** 28–38 blocks, crown base 12–20 blocks with bare log + 1-block dead stubs below, bottom radius 3–4.
- **Old spruce:** 30–40 blocks, trunk 2×2, radius 6–8, top 3–5 blocks blunter/rounded, 1–3 lowest tiers dead or missing on one side, lower tiers drop 2 blocks at the tips (more pendulous with age).
- **Engelmann-style narrow variant:** spread ≈ 0.25 × H (e.g. 28 tall, radius 3–4).
- **Vary:** (1) spread/height ratio 0.25–0.6 (narrow Engelmann → broad Norway); (2) crown base 0–2 (open) vs 0.4–0.6 × H (forest); (3) tier spacing 1–3 blocks and droop strength; (4) top form (sharp leader vs blunt/damaged double leader on 1–2 of 16).

---

## 5 · JUNGLE → tropical emergents (*Ceiba pentandra*, Dipterocarpaceae) + understorey cacao (*Theobroma cacao*)

**Why:** Minecraft's giant jungle tree matches a rainforest emergent (tall clean bole, crown above the canopy, buttresses); its cocoa pods match cacao, which grows as a small understorey tree. Use emergents for "mature/old" and cacao-like form for "young/small jungle" variants.

### 5.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young / understorey | Cacao: trunk grows to ~1.5 m then forms a **jorquette** — "3–5 lateral branches" at "approximately 45 degrees" ([Wikipedia — Jorquette](https://en.wikipedia.org/wiki/Jorquette)). Young emergents: 5–20 m pole with tiered horizontal branches (Massart model) **(heights estimate)** | 0.1–0.3 m **(estimate)** | narrow, 3–6 m **(estimate)** | cacao: 1.5 m; pole emergent: 0.4–0.6 × H **(estimate)** | young *Ceiba* trunks carry "short, sharp prickles" ([ICRAF Agroforestree — Ceiba](https://apps.worldagroforestry.org/treedb/AFTPDFS/Ceiba_pentandra.PDF)) |
| Mature emergent | Dipterocarps "typically 40–70 m, some over 80 m"; record 93.0 m ([Wikipedia — Dipterocarpaceae](https://en.wikipedia.org/wiki/Dipterocarpaceae)); *Shorea leprosula* to 54 m ([Useful Tropical Plants](https://tropical.theferns.info/viewtropical.php?id=Shorea+leprosula)); kapok 24–40 m in a typical large specimen ([Dimensions.com — Kapok](https://www.dimensions.com/element/kapok-large-ceiba-pentandra)) | *S. leprosula* to 1.61 m ([UTP](https://tropical.theferns.info/viewtropical.php?id=Shorea+leprosula)); *Ceiba* often up to 3 m above buttresses ([Wikipedia — Ceiba pentandra](https://en.wikipedia.org/wiki/Ceiba_pentandra)) | kapok 10.7–22.9 m on 24–40 m (≈0.45–0.6 × H) ([Dimensions.com](https://www.dimensions.com/element/kapok-large-ceiba-pentandra)) | *S. leprosula* bole "free of branches for up to 35 m" on 54 m → **HCB ≈ 0.65 × H** ([UTP](https://tropical.theferns.info/viewtropical.php?id=Shorea+leprosula)) | "wide, umbrella-shaped crown" (*Shorea*) |
| Old / giant | *Ceiba* verified 60.4 m ([Wikipedia](https://en.wikipedia.org/wiki/Ceiba_pentandra)) | *Ceiba* to 5.8 m above buttresses (same) | *Ceiba* canopy "as much as 60 m" wide (extreme) (same) | 0.55–0.7 × H **(estimate)** | 4–6 major limbs, each up to 1.8 m thick (same) |

### 5.2 Growth habit
- Young emergents: excurrent, tiered (Massart for *Ceiba* — [LibreTexts](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)); lower tiers are shed as the tree climbs through the canopy, leaving a long clean bole **(shedding: estimate, consistent with the 35 m clear bole cited)**.
- Mature: the leader breaks up at crown base into **4–6 massive limbs** ([Wikipedia — Ceiba](https://en.wikipedia.org/wiki/Ceiba_pentandra)) that rise at 30–50° then spread to near-horizontal, giving an "almost horizontal, spreading crown" / "pagoda-shaped" outline ([TopTropicals — Ceiba](https://toptropicals.com/html/toptropicals/articles/trees/Ceiba-pentandra.htm)) **(angles: estimate)**.
- Cacao: Nozeran model — after the jorquette, an upright "chupon" shoot can rise from below it and form a second jorquette higher up, stacking tiers ([Wikipedia — Jorquette](https://en.wikipedia.org/wiki/Jorquette); [LibreTexts](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)).

### 5.3 Branch orders and taper
- Visible orders on emergents: 3–4. Primary limbs are huge (up to 1.8 m thick on *Ceiba* — [Wikipedia](https://en.wikipedia.org/wiki/Ceiba_pentandra)) and run 0.6–0.9 × crown radius before splitting into a fan of smaller branches that carry the foliage **(ratio: estimate)**.
- Crown depth is shallow relative to height: crown occupies the top 0.3–0.45 × H **(estimate from the 0.65 clear-bole ratio)**.

### 5.4 Silhouette and foliage
- Umbrella / flattened dome ("broccoli" or "cauliflower" clumps): several separate dense foliage clumps, one per major limb, with gaps between clumps; crown width/depth ≈ 1.5–3 **(estimate)**.
- *Ceiba* is "leafless for a long period" with "a light crown" ([ICRAF](https://apps.worldagroforestry.org/treedb/AFTPDFS/Ceiba_pentandra.PDF)) — optional sparse/dry-season variant.
- Limbs are often "laden with epiphytes" ([TopTropicals](https://toptropicals.com/html/toptropicals/articles/trees/Ceiba-pentandra.htm)) → vines/moss on limbs.

### 5.5 Buttresses (key feature)
- Buttresses reach "up to 9 metres" up the trunk ([Wikipedia — Buttress root](https://en.wikipedia.org/wiki/Buttress_root)); in large *Ceiba* they can be seen "12 to 15 m" up the trunk and extend "as much as 20 m" outward (extremes) ([Wikipedia — Ceiba](https://en.wikipedia.org/wiki/Ceiba_pentandra)). *Shorea leprosula*: "stout buttresses up to 2 m high" ([UTP](https://tropical.theferns.info/viewtropical.php?id=Shorea+leprosula)).
- Buttressing scales with size: in a 20 ha dipterocarp plot, <1% of trees 10–200 mm DBH were buttressed vs. a large share of the biggest trees; 95% of species reaching > 500 mm DBH had buttresses ([Journal of Plant Ecology — Buttress trees in Xishuangbanna](https://academic.oup.com/jpe/article/6/2/187/921212)). → **no buttresses on young variants; always on mature/old.**
- Shape: thin vertical plank fins, 3–6 per tree, triangular in side view (tall at the trunk, sloping to the ground), often slightly sinuous in plan **(count and shape: estimate)**.

### 5.6 Block-scale translation
- **Young jungle (cacao-like):** 4–7 blocks; trunk 1 block to ~2 blocks then a jorquette of 3–5 branches at 45° fanning out to radius 2–3; optional chupon continuing 2–3 blocks to a second fan; cocoa on trunk/branches.
- **Pole emergent:** 12–20 blocks, 1-block trunk, 3–5 small horizontal tiers in the top half, radius 2–3, no buttresses.
- **Mature emergent:** 30–45 blocks; 2×2 trunk; clear bole to **0.6–0.7 × H** (20–30 blocks); **4–6 limbs** from the crown base rising 3–6 blocks and reaching out 6–10 blocks; leaf clumps radius 3–4 per limb, total crown radius 9–13, crown depth 8–12; **buttress fins 3–5 blocks up the trunk and 3–5 blocks out**, 4–6 fins.
- **Old giant:** 40–55 blocks, 3×3 trunk, buttresses 5–8 up and 5–8 out, crown radius 12–18, one or two broken/dead limbs, vines.
- **Vary:** (1) clear-bole ratio 0.55–0.72; (2) limb count 4–6 and their azimuths; (3) buttress count/size; (4) crown flatness (dome vs umbrella).

---

## 6 · DARK OAK → *Quercus virginiana* (southern live oak), alternative: open-grown parkland *Q. robur*

**Justification:** the vanilla dark oak is a thick, low tree with a broad, dense, dark canopy (roofed forest). Among real oaks, live oak is the best match: open-grown trees ~20 m tall with a limb spread of nearly 27 m ([Wikipedia — Quercus virginiana](https://en.wikipedia.org/wiki/Quercus_virginiana)), i.e. **wider than tall**, with "a very dense" crown that keeps leaves nearly year-round (same source), and huge trunks (Angel Oak 8.5 m girth; Duffie Oak 9.42 m girth — same source). Dark evergreen-looking foliage matches the "dark" palette. Parkland English oak is the fallback if a European look is wanted.

### 6.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young (10–40 yr) | 6–12 m **(estimate)** | 0.2–0.5 m **(estimate)** | ≈ height to 1.3 × H **(estimate)** | 1–2 m | often multi-trunk from the start |
| Mature (60–200 yr) | open-grown ~20 m ([Wikipedia](https://en.wikipedia.org/wiki/Quercus_virginiana)); 18–24 m ([UF/IFAS ST564](https://ask.ifas.ufl.edu/publication/ST564)) | > 1.8 m possible ("may exceed six feet" — [UF/IFAS](https://ask.ifas.ufl.edu/publication/ST564)) | ~27 m ([Wikipedia](https://en.wikipedia.org/wiki/Quercus_virginiana)); 18–37 m ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST564)) → **spread/H ≈ 1.0–1.5** | 1–3 m; lowest limbs can touch the ground (below) | "spreading, round", "dense" crown |
| Old (300 yr+) | 15–20 m **(estimate)** | 2.7–3.0 m (girth 8.5–9.4 m — [Wikipedia](https://en.wikipedia.org/wiki/Quercus_virginiana)) | 30–45 m **(estimate)** | ~0–2 m (limbs resting on ground) | veteran features as §7 |

### 6.2 Growth habit
- Decurrent from early on; multiple "sinuously curved trunks and branches"; narrow-angled co-dominant stems are common enough that arborists prune to remove them ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST564)).
- Trunk forks low: 1–4 m (often below 2 m) into 2–5 massive leaders **(estimate)**.
- Lower limbs: "often sweep down towards the ground before curving up again" and "can grow at severe angles" ([Wikipedia](https://en.wikipedia.org/wiki/Quercus_virginiana)) → limb angles 60–110° from trunk, long, near-horizontal, the longest limbs reaching 0.9–1.0 × crown radius **(angles: estimate)**.

### 6.3 Branch orders, silhouette, foliage
- Visible orders: 4–5 in mature crowns **(estimate)**.
- Silhouette: low, wide **dome**, often flat-bottomed; width 1.0–1.5 × height. In a closed "roofed" stand, crowns interlock at a flat-ish top and the space below is dark and open **(estimate)**.
- Foliage: **dense, filled** dome with few holes; outer shell 2–4 m thick **(estimate)**. Epiphytes (Spanish moss, resurrection fern) hang from limbs in the real species ([NWF — Southern Live Oak](https://www.nwf.org/Educational-Resources/Wildlife-Guide/Plants-and-Fungi/Southern-Live-Oak), not fetched — general knowledge, **estimate**).
- "Large surface roots" ([UF/IFAS](https://ask.ifas.ufl.edu/publication/ST564)) → exposed root flare.

### 6.4 Block-scale translation
- **Young dark oak:** 6–9 blocks, 1–2 trunks, radius 3–4, crown base 2.
- **Mature dark oak:** 12–18 blocks tall, **2×2 trunk splitting at 2–4 blocks** into 2–4 thick leaders, **crown radius 8–12** (spread ≥ height), dense dome 6–9 blocks deep, crown base 2–3; 1–2 low limbs dipping to within 1 block of the ground before curving up; exposed roots radiating 2–4 blocks.
- **Old dark oak:** 14–20 blocks, 3×3 trunk, radius 12–18 (limited by build budget), a few limbs resting on the ground, hollow at base on some variants.
- **Vary:** (1) spread/height 1.0–1.5; (2) number of leaders 2–5 and fork height; (3) number of ground-sweeping limbs 0–3; (4) dome flatness.

---

## 7 · PALE OAK → veteran/ancient oak (*Q. robur* veteran, *Q. alba* old growth)

**Justification:** "pale" + gnarled + eerie maps to a veteran oak: *Q. alba* supplies pale, whitish, plated bark ([UF/IFAS ST541](https://ask.ifas.ufl.edu/publication/ST541); "pale gray" — [MN DNR](https://www.dnr.state.mn.us/trees/white-oak.html)); ancient *Q. robur* supplies the hollowing, retrenchment and dead wood documented by the UK veteran-tree guidance.

### 7.1 Dimensions
- Young/mature pale oak: use the oak tables (§2.1) with *Q. alba* values (18–30 m, spread 15–24 m, DBH 0.6–0.9 m).
- Veteran/ancient: DBH 1.4–3.2 m (girth 4.5–10 m+) ([ATI oak guide](https://ati.woodlandtrust.org.uk/how-to-record/species-guides/oak/)); height reduced — ancient crowns are "smaller and closer to the ground" ([Woodland Trust — Recognising ancient trees](https://www.woodlandtrust.org.uk/media/53779/recognising-and-categorising-ancient-and-other-veteran-trees.pdf)); working value **0.5–0.75 × former mature height** **(estimate)**; girth ≥ 6 m for most chronologically ancient oaks but only ~3.5 m in woodland-grown or former pollards (ATI). Ancient features from ~300 yr; lifespan 600–1,000 yr (ATI).

### 7.2 Veteran features (from the Woodland Trust / ATI guidance)
- **Crown retrenchment** — "episodic shrinking of the outer crown and changes to crown shape" ([WT guidance](https://www.woodlandtrust.org.uk/media/53779/recognising-and-categorising-ancient-and-other-veteran-trees.pdf)). The old top dies back; a new, lower crown forms from shoots closer to the trunk.
- **Stag-headed** — dead limbs left standing above the new live crown (same).
- **Functional units** — the trunk splits into independent columns of live bark and wood, each feeding its own section of crown (same).
- **Heart rot and hollowing**, "major trunk cavities or progressive hollowing" ([ATI](https://ati.woodlandtrust.org.uk/how-to-record/species-guides/oak/)).
- **Dead wood** — "large quantities of dead wood in the canopy", bark loss, decay holes, rot-holes, woodpecker holes, fungal brackets (ATI; WT guidance).
- **Epicormic sprouting** from dormant buds on trunk and limbs ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)).
- Crown: polyarchic, no leader (same).

### 7.3 Silhouette and foliage
- Low, broad, broken dome; live foliage in **separate patches** around each functional unit and epicormic cluster; large holes; bare grey dead limbs projecting 2–6 m beyond and above the live shell **(estimate)**.
- Trunk: very short and fat (height to first limb 2–4 m), fluted/buttressed base, often leaning or split **(estimate)**.

### 7.4 Block-scale translation
- **Young pale oak:** as young oak (§2.6), pale bark, slightly crooked leader.
- **Mature pale oak:** as mature open oak, 15–20 blocks, pale bark, 1 dead limb.
- **Veteran pale oak:** 10–16 blocks tall, **2×2 or 3×3 trunk** with an open hollow (1×1 or 2×2 cavity) visible from one side at the base or a split into 2–3 columns, first limbs at 2–4 blocks; live crown radius 5–9 sitting **low**; 2–4 bare dead "stag" limbs (log-only, no leaves) rising 2–5 blocks above the leaves; epicormic leaf tufts directly on the trunk; 20–40% of crown volume missing as holes.
- **Vary:** (1) retrenchment depth (live crown top at 0.5–0.8 × max height); (2) number of dead stag limbs 1–4; (3) hollow type (none / base cavity / split trunk / full-height hollow); (4) lean 0–15°.

---

## 8 · ACACIA → *Vachellia tortilis* (umbrella thorn), subsp. *heteracantha* / *spirocarpa*

**Why:** the umbrella thorn is the flat-topped savanna tree; FAO notes the flat crown is characteristic enough to earn the common name ([FAO — Acacia taxonomy manual](https://www.fao.org/4/q2934e/q2934e05.htm)).

### 8.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young | 1–4 m; "shrubby", thickly covered in straight white spines ([The Namibian — Meet the Trees](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)); growth "rather slow" — 0.8 m in four years ([SANBI PlantZAfrica](https://pza.sanbi.org/vachellia-tortilis)) | 0.05–0.15 m **(estimate)** | ≈ height **(estimate)** | ~0.3–1 m | bushy, multi-stem is common ([Winrock fact sheet](https://winrock.org/factnet/fact-net-fact-sheets/acacia-tortilis-fodder-tree-for-desert-sands/)) |
| Middle-aged | 4–8 m **(estimate)** | 0.15–0.3 m **(estimate)** | 1–1.5 × H **(estimate)** | 1.5–2.5 m **(estimate)** | "large rounded crowns" ([The Namibian](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)) |
| Mature | 5–20 m in nature ([SANBI](https://pza.sanbi.org/vachellia-tortilis)); "1.5–18 m high, occasionally to 21 m"; subsp. *spirocarpa* 2–21 m, *heteracantha* to 15 m ([FAO](https://www.fao.org/4/q2934e/q2934e05.htm)) | 0.3–0.7 m **(estimate)** | cultivated trees 3–5 m tall with "a spread of 8–13 m" ([SANBI](https://pza.sanbi.org/vachellia-tortilis)) → **spread/H ≈ 1.5–3** | 0.5–0.75 × H **(estimate)** | "spreading, flat crown" ([The Namibian](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)) |
| Old | as mature; crown flatter, some dead limbs **(estimate)** | | | | |

- Subspecies differences: *raddiana* has a "more or less rounded crown"; *tortilis* is a 2–6 m small tree with flattened crown; *spirocarpa* and *heteracantha* have "flattened spreading crown" ([FAO](https://www.fao.org/4/q2934e/q2934e05.htm)). *heteracantha* is "smaller and often without a spreading crown" ([Wikipedia — Vachellia tortilis](https://en.wikipedia.org/wiki/Vachellia_tortilis)) — i.e. not every individual is a perfect umbrella.

### 8.2 Growth habit
- Decurrent. The trunk (single in *heteracantha* — [The Namibian](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)) **forks low**, at 0.5–3 m, into 2–5 ascending limbs **(estimate)**.
- Limbs rise at 20–45° from vertical, often diverging in a V/fan, then fork repeatedly; the final branches bend outward to **horizontal** at the crown top so all foliage lies in one thin layer **(estimate)**. The top is shaped by browsing and wind; flat tops are associated with browsing from below and light competition in open savanna (mechanism: **estimate** — the UAE study on canopy architecture was not accessible: [Unusual canopy architecture in V. tortilis, UAE](https://www.researchgate.net/publication/271141335_Unusual_canopy_architecture_in_the_umbrella_thorn_acacia_Vachellia_tortilis_Acacia_tortilis_in_the_United_Arab_Emirates)).
- Bark "deeply fissured", coming off in long strips ([The Namibian](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)).

### 8.3 Branch orders and silhouette
- Visible orders: 3–5 (many forkings); limbs zig-zag slightly at each fork **(estimate)**.
- Silhouette: **umbrella / table** — a flat or very slightly domed top layer 1–3 m deep **(estimate)**, wider than the tree is tall, with an open, bare-limbed space underneath.
- Foliage: fine and see-through (tiny bipinnate leaves), forming a thin flat mat with the top surface almost level; edges sometimes droop slightly **(estimate)**.
- Roots: deep taproot on sand; on shallow soils surface roots extend "over twice the width of the crown" ([Winrock](https://winrock.org/factnet/fact-net-fact-sheets/acacia-tortilis-fodder-tree-for-desert-sands/)).

### 8.4 Block-scale translation
- **Young acacia:** 2–4 blocks, multi-stem bush, rounded radius 1–2.
- **Middle acacia:** 5–7 blocks, single trunk forking at 1–2 blocks into 2–3 limbs, rounded crown radius 3–4.
- **Mature acacia:** 7–12 blocks tall, trunk 1 block, **fork at 1–3 blocks into 2–4 limbs** leaning out 25–45° from vertical, flat canopy **1–2 blocks thick** at the top, **radius 5–9** (spread 1.5–2× height), canopy underside 5–9 blocks up.
- **Old acacia:** 9–14 blocks, 2 main leaners, canopy split into 2–3 flat plates at slightly different heights, one dead limb.
- **Vary:** (1) fork height and limb count; (2) spread/height 1.2–2.5; (3) flat vs slightly domed top (raddiana-type rounded on 2–3 of 16); (4) number of separate canopy plates 1–3.

---

## 9 · CHERRY → *Prunus × yedoensis* ('Somei-yoshino') and *Prunus serrulata* (Japanese flowering cherries)

**Why:** the vanilla cherry is the ornamental sakura; Yoshino is the classic large, spreading sakura; *P. serrulata* cultivars ('Kanzan') give the upright vase form.

### 9.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young (3–15 yr) | 3–6 m **(estimate)** | 0.05–0.2 m | 2.5–4.8 m (*P. avium* eq. at 0.05–0.2 m, [Hemery](https://benfieldgroup.uk/wp-content/uploads/2021/09/Hemery_et_al_2005_kd_paper.pdf); proxy species) | 1–1.8 m **(estimate)** | upright vase |
| Mature (20–50 yr) | Yoshino 9–12 m ([Missouri Botanical Garden](https://www.missouribotanicalgarden.org/PlantFinder/PlantFinderDetails.aspx?taxonid=286608)); *P. serrulata* 4.6–7.6 m ([NC State Extension](https://plants.ces.ncsu.edu/plants/prunus-serrulata)) | 0.3–0.6 m **(estimate)** | Yoshino 9–12 m (= height); *P. serrulata* 4.6–7.6 m (= height) (same sources) → **spread/H ≈ 1.0, up to ~1.5 for old Yoshino (estimate)** | 1.2–2.5 m **(estimate)** | "spreading, broad-rounded, open crown" (MBG) |
| Old (60 yr+) | 8–12 m, wider than tall **(estimate)** | 0.6–1.0 m **(estimate)** | 12–20 m **(estimate)** | 1–2 m; long limbs may sag lower | urban Yoshino useful life ~60–80 yr; oldest recorded 146 yr ([tree-doctor article, note.com](https://note.com/miscanthus_0604/n/n66ce7d05a545?hl=en-US) — **secondary source**). *P. serrulata* cultivars "usually short-lived", 15–20 yr average in US landscapes ([NC State](https://plants.ces.ncsu.edu/plants/prunus-serrulata)) |

### 9.2 Growth habit
- Decurrent. Short trunk forking at **1–2 m** into **3–5 scaffolds** **(estimate)**.
- Young: scaffolds rise steeply (20–40° from vertical), giving the **vase** ('Kanzan' "upright, vase-shaped" — [NC State](https://plants.ces.ncsu.edu/plants/prunus-serrulata)).
- Mature/old Yoshino: scaffolds arch outward; outer halves become near **horizontal** and, on old trees, sag slightly downward under their weight, producing a broad umbrella **(estimate)**. The form list for *P. serrulata* includes "vase, spreading, horizontal, rounded" ([NC State](https://plants.ces.ncsu.edu/plants/prunus-serrulata)).
- Weak wood, prone to trunk splitting ([NC State](https://plants.ces.ncsu.edu/plants/prunus-serrulata)).

### 9.3 Branch orders, silhouette, foliage
- Visible orders: 3–4; long horizontal secondary branches carry dense short spurs **(estimate)**.
- Silhouette: young = narrow vase (wider at top than bottom); mature = broad rounded umbrella, width ≈ height; old = wide flattened umbrella, width > height.
- Foliage/blossom: **concentrated along the upper side and ends of horizontal branches**, forming layered clouds with clear gaps between layers; "abundant flower volume on single branches" ([note.com](https://note.com/miscanthus_0604/n/n66ce7d05a545?hl=en-US)) **(layering: estimate)**.

### 9.4 Distinctive features
- Glossy red-brown to grey bark with **horizontal lenticel stripes** ([NC State](https://plants.ces.ncsu.edu/plants/prunus-serrulata)).
- Old trees: heart rot after major branch loss, hollow trunks, major stems with irreparable rot; shallow exposed roots ([note.com](https://note.com/miscanthus_0604/n/n66ce7d05a545?hl=en-US)).
- Old Japanese specimen trees often have long limbs supported on props **(estimate — cultural practice, not sourced here)**.

### 9.5 Block-scale translation
- **Young cherry:** 4–6 blocks, trunk forks at 1–2 blocks into 3 steep scaffolds, crown radius 2–3, vase.
- **Mature cherry:** 8–11 blocks tall, fork at 2 blocks, **3–5 scaffolds** rising 3–4 blocks then bending out to near-horizontal, **radius 5–6** (spread ≈ height), blossom clouds 2–3 blocks thick in 2 layers with a 1-block gap.
- **Old cherry:** 9–12 blocks tall, **radius 7–10** (spread > height), lowest limbs sag to 2–3 blocks above ground, a hollow or split trunk on some variants, 1 dead limb.
- **Vary:** (1) scaffold count 3–5 and their spread angle (vase ↔ umbrella); (2) spread/height 0.8–1.6; (3) blossom layer count 1–3; (4) sag amount on outer limbs.

---

## 10 · MANGROVE → *Rhizophora mangle* (red mangrove)

**Why:** the vanilla mangrove's arching root cage matches the red mangrove's prop roots (rhizophores). Architecture: Attims' model (*Rhizophora*) — all axes upright, continuous growth ([LibreTexts](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)).

### 10.1 Dimensions

| Stage | Height | DBH | Spread | HCB | Notes |
|---|---|---|---|---|---|
| Young | 0.5–3 m; established from a propagule 30–60 cm long that "falls like a dart and sticks upright in the mud" ([Useful Tropical Plants — R. mangle](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)) | < 0.1 m | ≈ height **(estimate)** | ~0.5 m | first 1–3 prop roots **(estimate)** |
| Mature | commonly ~6 m, up to 24 m ([Wikipedia — R. mangle](https://en.wikipedia.org/wiki/Rhizophora_mangle)); 5–20 m, occasionally 30 m ([UTP](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)); 8–12 m on exposed coasts ([Costa Rica Tree Atlas](https://costaricatreeatlas.org/en/trees/mangle-rojo)) | 0.2–0.7 m, occasionally 0.9 m ([UTP](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)) | ≈ 0.7–1.2 × H **(estimate)** | 0.3–0.5 × H above the root cage **(estimate)** | "round-topped, bushy" crown (UTP); "dense and rounded" (CR Tree Atlas) |
| Old / tall | 15–25 m in sheltered forests **(estimate from cited max)** | 0.5–0.9 m | | high, forest-like | rhizophore count and height scale up with tree size (below) |

### 10.2 Prop roots (rhizophores) — the key feature
- Stilt roots are "branched, curved, and arching", "2–4.5 m tall when growing in salt water" ([UTP](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)).
- Measured on *R. mangle* ("Root biomechanics in *Rhizophora mangle*… flying buttresses" — [ResearchGate abstract](https://www.researchgate.net/publication/272296788_Root_biomechanics_in_Rhizophora_mangle_Anatomy_morphology_and_ecology_of_mangrove's_flying_buttresses)):
  - rhizophores attach up to **10–33% of tree height**;
  - maximum rhizophore height 0.30–5.30 m (**mean 1.27 m**); length 0.08–5.60 m (**mean 1.13 m**);
  - **1–14 rhizophores per tree**, scaling with basal area, height and crown area;
  - branching is sympodial, **up to six orders**, "each order showing reduced height and increased horizontal spread" → first-order roots leave the trunk high and steep; each later order starts from the previous arch, lower and flatter, stepping outward.
- Aerial roots also "descend from the trunk and lower branches into the water or mud" ([Costa Rica Tree Atlas](https://costaricatreeatlas.org/en/trees/mangle-rojo)) — straight drop roots from limbs.
- Function: support in soft mud and oxygen intake through lenticels (same source; [Wikipedia](https://en.wikipedia.org/wiki/Rhizophora_mangle)).

### 10.3 Growth habit and crown
- Trunk: short and often indistinct above the root cage — the "trunk" may start 1–3 m above the mud, standing on its arches **(estimate)**. Upper branches ascend at 30–60° from vertical **(estimate)**.
- Crown: rounded, bushy, dense, leaves clustered at branch ends (leathery 7.6–12.7 cm leaves — [Wikipedia](https://en.wikipedia.org/wiki/Rhizophora_mangle); clustering: **estimate**); hanging propagules 8–30 cm before drop ([UTP](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)).
- In stands, crowns merge into a continuous rounded canopy; open-edge trees are wider and lower **(estimate)**.

### 10.4 Block-scale translation
- **Young mangrove:** 2–4 blocks, 2–4 prop roots arching from 1–2 blocks up the stem to 1–2 blocks out, small round crown radius 1–2.
- **Mature mangrove:** 8–14 blocks tall; prop roots start **2–4 blocks up the trunk** (≈ 0.1–0.33 × H), **6–12 roots**, first-order arches reach 2–3 blocks out, second/third-order arches step another 1–2 blocks out and lower each time (total root cage radius 3–6); 2–4 straight drop roots from lower limbs; rounded dense crown radius 4–6 starting ~5–7 blocks up.
- **Old mangrove:** 14–20 blocks, root cage 5–8 blocks across, 10–14 first-order roots, more drop roots, crown radius 6–8, slightly flattened.
- **Vary:** (1) root count and root-cage radius; (2) root start height 0.1–0.33 × H; (3) number of drop roots from limbs 0–5; (4) lean (mangroves on banks lean toward the water — **estimate**).

---

## 11 · How to vary individuals without breaking species character

### 11.1 Real causes of individual difference
- **Competition / crowding** raises the crown base and narrows the crown (§1.3, [PLOS ONE HCB model](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0186394)); open-grown trees are wider and lower-branched (oak: [VT Dendrology](https://dendro.cnre.vt.edu/dendrology/syllabus/factsheet.cfm?ID=35); birch: [BC MoF](https://www.for.gov.bc.ca/hfd/library/documents/treebook/paperbirch.htm)). Crowns also become **one-sided**, growing away from neighbours toward the gap **(estimate)**.
- **Light (phototropism)**: trunks lean and limbs lengthen toward the brightest side (forest edge, river, clearing); the shaded side keeps shorter limbs and loses its lowest branches first **(estimate)**.
- **Wind**: on exposed sites crowns are shorter and lopsided downwind ("flagging"), trunks lean downwind; mangroves are smaller on exposed coasts (8–12 m vs 20–30 m — [Costa Rica Tree Atlas](https://costaricatreeatlas.org/en/trees/mangle-rojo)); spruce and pines near treeline become low shrubby forms that layer from ground branches ([Old Tjikko](https://en.wikipedia.org/wiki/Old_Tjikko)).
- **Damage**: broken leaders → 2–3 replacement leaders (spruce "double top"; oak becomes decurrent earlier); storm-broken limbs leave stubs and holes; heart rot after big limb loss (cherry — [note.com](https://note.com/miscanthus_0604/n/n66ce7d05a545?hl=en-US)); old-age retrenchment and stag-heads ([Woodland Trust guidance](https://www.woodlandtrust.org.uk/media/53779/recognising-and-categorising-ancient-and-other-veteran-trees.pdf)).
- **Reiteration**: dormant-bud shoots (epicormics, suckers) produce mini-crowns on trunks and old limbs ([Pfisterer 2000](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)).
- **Genetics/subspecies**: Norway spruce varies in branchlet hang (weeping vs stiff) ([TSO](https://www.treesandshrubsonline.org/articles/picea/picea-abies/)); umbrella thorn varies from flat to rounded crowns by subspecies ([FAO](https://www.fao.org/4/q2934e/q2934e05.htm)).

### 11.2 Rules that keep species character (invariants — never vary these)
- **Spruce:** single straight leader (max 1–2 of 16 with a damaged double top), conical outline with radius decreasing upward, tiered structure, low crown on open-grown variants.
- **Birch:** slender (spread ≤ ~0.5 × H), many thin branches, hanging outer twigs, white bark with black base.
- **Oak:** decurrent mature crown, thick sinuous scaffolds, spread ≈ height when open-grown, clumped foliage with gaps.
- **Dark oak:** wider than tall, very dense dome, low thick multi-leader trunk.
- **Pale oak:** low retrenched crown, dead stag limbs, pale bark, hollowing.
- **Jungle emergent:** long clean bole (≥ 0.55 × H), crown confined to the top, buttresses on all large variants.
- **Acacia:** low fork, ascending limbs, flat thin top, spread > height.
- **Cherry:** short trunk, 3–5 scaffolds, vase → umbrella, foliage in layers along horizontal limbs.
- **Mangrove:** arching prop roots from 10–33% of height, rounded dense crown.

### 11.3 Recommended variation recipe for a 16-variant set (design suggestion)
- Split into life stages, e.g. 4 young / 8 mature / 4 old, or whatever the generator budget allows.
- For each variant, draw parameters from a **seeded** distribution inside the species band (not uniform min–max: use a centred distribution so most variants look typical and 1–2 are extreme).
- Always vary:
  1. **Size** (height within the stage band; crown width follows from height via the species spread/H ratio, with ±15% noise).
  2. **Crown-base height** (open vs forest-grown; spruce 0–2 vs 0.4–0.6 × H).
  3. **Asymmetry vector**: one azimuth "light side" — limbs on that side +20–40% longer, opposite side −20–30%; trunk lean 0–8° toward it (0–15° for veteran trees) **(estimate)**.
  4. **Structural count** (scaffold/limb/root count) and fork height.
- Then add 0–2 **damage events** per old variant (dead limb, broken top, hollow, missing tier), and 0–1 per mature variant.
- Check each finished variant against the invariant list (§11.2) before accepting it.

---

## 12 · Quick reference — block-scale numbers (1 block = 1 m)

| Species | Stage | Height | Trunk | Crown base | Crown radius | Signature |
|---|---|---|---|---|---|---|
| Oak (open) | mature | 16–24 | 1–2 | 3–5 | 7–11 | fork 4–7, 3–5 scaffolds |
| Birch | mature | 14–20 | 1 | 4–7 (open) | 3–4 | slim, hanging tips |
| Spruce (Norway, open) | mature | 20–30 | 1–2 | **0–2** | **5–7 at base → 0** | tier every 2, tips drop 1–2 |
| Spruce (Engelmann-style) | mature | 24–32 | 1–2 | 0–2 | 3–4 | narrow spire |
| Jungle emergent | mature | 30–45 | 2×2 | 0.6–0.7 × H | 9–13 | 4–6 limbs, buttresses 3–5 up/out |
| Jungle cacao-type | young | 4–7 | 1 | ~2 | 2–3 | 3–5 branch jorquette at 45° |
| Dark oak | mature | 12–18 | 2×2 | 2–3 | 8–12 | wider than tall, dense dome |
| Pale oak | veteran | 10–16 | 2×2–3×3 | 2–4 | 5–9 | stag limbs, hollow |
| Acacia | mature | 7–12 | 1 | 5–9 | 5–9 | fork 1–3, flat 1–2-thick top |
| Cherry | mature | 8–11 | 1 | 2 | 5–6 | vase → umbrella, 2 blossom layers |
| Mangrove | mature | 8–14 | 1 | ~5–7 | 4–6 | 6–12 prop roots from 2–4 up |

---

## Sources

- [Pfisterer 2000 — Modern models in tree architecture as a helpful tool for natural pruning (PDF)](https://www.arboritecture.org/pdf/pfisterer/modern-models-in-tree-architecture-as-a-helpful-tool-for-natural-pruning-pfisterer-2000.pdf)
- [Biology LibreTexts — Architectural Models of Tropical Trees: Illustrated Key](https://bio.libretexts.org/Bookshelves/Evolutionary_Developmental_Biology/Key_to_the_Diversity_and_History_of_Life_(Shipunov)/04:_Geography_of_Life/4.02:_Architectural_Models_of_Tropical_Trees-_Illustrated_Key)
- [Hemery, Savill & Pryor 2005 — Applications of the crown diameter–stem diameter relationship (PDF)](https://benfieldgroup.uk/wp-content/uploads/2021/09/Hemery_et_al_2005_kd_paper.pdf)
- [Scientific Data 2015 — Allometry and growth of eight tree taxa in UK woodlands (Scientific Data)](https://www.nature.com/articles/sdata20156)
- [PLOS ONE — Modelling individual tree height to crown base of Norway spruce and European beech](https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0186394)
- [Open Oregon — Forest Measurements: Live Crown Ratio](https://openoregon.pressbooks.pub/forestmeasurements/chapter/5-4-live-crown-ratio/)
- [Open Oregon — Forest Measurements: Young trees (whorl counting)](https://openoregon.pressbooks.pub/forestmeasurements/chapter/4-3-young-trees/)
- [Woodland Trust — Recognising and categorising ancient and other veteran trees (PDF)](https://www.woodlandtrust.org.uk/media/53779/recognising-and-categorising-ancient-and-other-veteran-trees.pdf)
- [Woodland Trust Ancient Tree Inventory — Oak species guide](https://ati.woodlandtrust.org.uk/how-to-record/species-guides/oak/)
- [Woodland Trust — English oak](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/english-oak/)
- [Forestry England — English oak](https://www.forestryengland.uk/tree-species/english-oak)
- [Virginia Tech Dendrology — White oak](https://dendro.cnre.vt.edu/dendrology/syllabus/factsheet.cfm?ID=35)
- [Minnesota DNR — White oak](https://www.dnr.state.mn.us/trees/white-oak.html)
- [UF/IFAS ST541 — Quercus alba](https://ask.ifas.ufl.edu/publication/ST541)
- [UF/IFAS ST564 — Quercus virginiana](https://ask.ifas.ufl.edu/publication/ST564)
- [Wikipedia — Quercus virginiana](https://en.wikipedia.org/wiki/Quercus_virginiana)
- [Woodland Trust — Silver birch](https://www.woodlandtrust.org.uk/trees-woods-and-wildlife/british-trees/a-z-of-british-trees/silver-birch/)
- [First Nature — Betula pendula](https://www.first-nature.com/trees/betula-pendula.php)
- [EUFORGEN — Betula pendula](https://www.euforgen.org/species/betula-pendula)
- [Silvics of North America (Forest*A*Syst mirror) — Betula papyrifera](https://www.forestasyst.org/hardwoods/papyrifera.htm)
- [BC Ministry of Forests Tree Book — Paper birch](https://www.for.gov.bc.ca/hfd/library/documents/treebook/paperbirch.htm)
- [Conifers.org — Picea abies](https://www.conifers.org/pi/Picea_abies.php)
- [Trees and Shrubs Online — Picea abies](https://www.treesandshrubsonline.org/articles/picea/picea-abies/)
- [Wikipedia — Picea abies](https://en.wikipedia.org/wiki/Picea_abies)
- [Morton Arboretum — Norway spruce](https://mortonarb.org/plant-and-protect/trees-and-plants/norway-spruce/)
- [Iowa State Extension — Norway spruce](https://naturalresources.extension.iastate.edu/forestry/iowa_trees/trees/norway_spruce.html)
- [Virginia Tech HORT-20 — Norway spruce](https://www.pubs.ext.vt.edu/HORT/HORT-20/HORT-20.html)
- [Utah State Tree Browser — Norway spruce](https://extension.usu.edu/treebrowser/catalog/spruce-norway)
- [Crown architecture and structural development of young Norway spruce (ResearchGate)](https://www.researchgate.net/publication/331178478_Crown_architecture_and_structural_development_of_young_Norway_spruce_trees_Picea_abies_Karst_A_basis_for_more_realistic_growth_modelling)
- [Modelling branch characteristics of Norway spruce from wide spacings (abstract)](https://www.sciencedirect.com/science/article/abs/pii/S0378112707000357)
- [USDA Woody Plant Seed Manual — Picea (PDF)](https://www.fs.usda.gov/nsl/Wpsm/Picea.pdf)
- [Wikipedia — Picea glauca](https://en.wikipedia.org/wiki/Picea_glauca)
- [Minnesota DNR — White spruce](https://www.dnr.state.mn.us/trees/white-spruce.html)
- [BC silvics — Engelmann spruce (PDF)](https://www2.gov.bc.ca/assets/gov/farming-natural-resources-and-industry/forestry/tree-species-selection/silvics_se.pdf)
- [USFS FEIS — Picea mariana](https://www.fs.usda.gov/database/feis/plants/tree/picmar/all.html)
- [Wikipedia — Old Tjikko](https://en.wikipedia.org/wiki/Old_Tjikko)
- [Wikipedia — Ceiba pentandra](https://en.wikipedia.org/wiki/Ceiba_pentandra)
- [ICRAF Agroforestree Database — Ceiba pentandra (PDF)](https://apps.worldagroforestry.org/treedb/AFTPDFS/Ceiba_pentandra.PDF)
- [TopTropicals — Ceiba pentandra](https://toptropicals.com/html/toptropicals/articles/trees/Ceiba-pentandra.htm)
- [Dimensions.com — Kapok (Large)](https://www.dimensions.com/element/kapok-large-ceiba-pentandra)
- [Wikipedia — Dipterocarpaceae](https://en.wikipedia.org/wiki/Dipterocarpaceae)
- [Useful Tropical Plants — Shorea leprosula](https://tropical.theferns.info/viewtropical.php?id=Shorea+leprosula)
- [Wikipedia — Buttress root](https://en.wikipedia.org/wiki/Buttress_root)
- [Journal of Plant Ecology — Buttress trees in a 20-ha dipterocarp rainforest, Xishuangbanna](https://academic.oup.com/jpe/article/6/2/187/921212)
- [Wikipedia — Jorquette (Theobroma cacao)](https://en.wikipedia.org/wiki/Jorquette)
- [SANBI PlantZAfrica — Vachellia tortilis](https://pza.sanbi.org/vachellia-tortilis)
- [FAO — Manual on taxonomy of Acacia species (A. tortilis)](https://www.fao.org/4/q2934e/q2934e05.htm)
- [The Namibian — Meet the Trees: Umbrella thorn](https://www.namibian.com.na/meet-the-trees-umbrella-thorn-acacia-tortilis-subsp-heteracantha/)
- [Winrock International — Acacia tortilis fact sheet](https://winrock.org/factnet/fact-net-fact-sheets/acacia-tortilis-fodder-tree-for-desert-sands/)
- [Wikipedia — Vachellia tortilis](https://en.wikipedia.org/wiki/Vachellia_tortilis)
- [ResearchGate — Unusual canopy architecture in Vachellia tortilis, UAE (not accessible; cited for existence only)](https://www.researchgate.net/publication/271141335_Unusual_canopy_architecture_in_the_umbrella_thorn_acacia_Vachellia_tortilis_Acacia_tortilis_in_the_United_Arab_Emirates)
- [Missouri Botanical Garden — Prunus × yedoensis](https://www.missouribotanicalgarden.org/PlantFinder/PlantFinderDetails.aspx?taxonid=286608)
- [NC State Extension — Prunus serrulata](https://plants.ces.ncsu.edu/plants/prunus-serrulata)
- [note.com (Japanese tree doctor) — Is Somei-yoshino short-lived? (secondary source)](https://note.com/miscanthus_0604/n/n66ce7d05a545?hl=en-US)
- [Wikipedia — Rhizophora mangle](https://en.wikipedia.org/wiki/Rhizophora_mangle)
- [Useful Tropical Plants — Rhizophora mangle](https://tropical.theferns.info/viewtropical.php?id=Rhizophora+mangle)
- [Costa Rica Tree Atlas — Red mangrove](https://costaricatreeatlas.org/en/trees/mangle-rojo)
- [Root biomechanics in Rhizophora mangle (abstract)](https://www.researchgate.net/publication/272296788_Root_biomechanics_in_Rhizophora_mangle_Anatomy_morphology_and_ecology_of_mangrove's_flying_buttresses)
- [National Wildlife Federation — Southern live oak (not fetched; epiphyte note only)](https://www.nwf.org/Educational-Resources/Wildlife-Guide/Plants-and-Fungi/Southern-Live-Oak)
