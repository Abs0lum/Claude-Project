# J1 — Java tree rules study (2026-09-30)

**Status:** J1 done; renders sent to Abs0lum. J2 (.mcstructure export with our blocks) is waiting for his shape picks. HYPOTHESIS-grade until he confirms in-game (Source-Trust Law).

## Where the rules came from
- **Java 26.3 server jar**, taken from Mojang's version manifest (sha1 matches).
  - 26.x ships **unobfuscated**: the manifest lists no mappings, and the class names are real.
  - Decompiled with Vineflower 1.11.0 into `_intake/java-26.3-trees/decompiled`: TreeFeature, 12 trunk placers, 14 foliage placers, and the root placers.
- **Vanilla feature JSON (26.4-snapshot-2)** from misode/mcmeta, branch `data-json`, into `_intake/java-26.3-trees/features`.
  - Registry renamed in 26.x: `worldgen/configured_feature` is now `worldgen/feature`.
- **New tree in 26.4-snapshot:** poplar (`orange_poplar`, `red_poplar`, `yellow_poplar`), using `poplar_trunk_placer` + `poplar_foliage_placer`.
- **Licence:** only the rules (steps and numbers) are re-implemented in our own Python. No Mojang code ships in any pack. Personal use (§9).

## Tools
- **`tools/java_trees.py`** — the port.
  - `grow(feature, seed)` returns a World: `{(x,y,z): ("log", axis) | ("leaf", id) | ("root", id)}`.
  - Java semantics are kept:
    - int division truncates toward zero (`jdiv`);
    - `(int)` casts truncate;
    - logs are placed before leaves;
    - leaves only go into air or leaves;
    - the ground (y < 0) is solid.
  - Uses Python's RNG, not Java's Xoroshiro. Every tree follows the Java rules, but seed N is not Java's seed N.
- **`tools/java_trees_render.py`** — writes the sheets to `_docs/trees/j1/J1-<FAMILY>.png`.
  - Orthographic view from the south-east, 30° up, one scale per sheet.
  - For each Java feature: a row of 6 seeds, then the same 6 with the leaves hidden.
  - The BP-02 row is a **MODEL** (legacy BigTree rules + BP-02's numbers), because Bedrock's fancy_trunk source is not public.

## Placer facts (from the source)
- **Fancy oak** (`FancyTrunkPlacer`):
  - height = treeHeight + 2;
  - trunk = floor(0.618 × height);
  - one foliage cluster per y from 0.3 × height up, at distance treeShape × (rand + 0.328);
  - branch base = tip.y − 0.381 × horizontal distance;
  - limbs are stepped voxel lines whose log axis follows the dominant direction;
  - branches below 0.2 × height are trimmed.
- **Acacia** (`ForkingTrunkPlacer`): leans 0–3 steps near the top; a second branch 1–3 steps long in another direction.
- **Cherry** (`CherryTrunkPlacer`):
  - 1–3 branches (3 = a middle trunk continues);
  - each branch goes 1–2 blocks sideways, then random-walks toward an end point 2–4 out, near the top.
  - Foliage: `CherryFoliagePlacer` with hanging leaves.
- **Mangrove** (`UpwardsBranchingTrunkPlacer`):
  - the trunk sits 1–3 blocks up on `MangroveRootPlacer` roots;
  - branch chance per log is 0.5;
  - branches climb diagonally.
- **Dark oak / pale oak** (`DarkOakTrunkPlacer`):
  - 2×2 trunk that leans 0–2 at the top;
  - side stubs 2–4 long around the crown;
  - dark oak foliage is double-trunk rows.
- **Mega spruce / pine** (`GiantTrunkPlacer`) and **mega jungle** (`MegaJungleTrunkPlacer`): 2×2 trunks. Mega jungle adds 5-step angled branches every 2–5 blocks in the upper half.

## Mapping observed (for his picks)
- Java's **2×2 trees** (dark/pale oak, mega spruce/pine, mega jungle) fit our **square ELDERS**.
- Java's **straight trees** (oak, birch, jungle, spruce, pine) have no branches, which fits our **dodecagon young / mature / old**.
- **Fancy oak** is the exception: a straight-family tree with diagonal staircase limbs. It needs a ruling: square limbs, or an elder only.

## Open
- **Validation against real Java** (grow reference trees on a Java server) would need the Minecraft EULA accepted. That is Abs0lum's decision.
- **Backlog, his 16:24 idea:**
  - round elders built from a quarter-round piece rotated four ways;
  - bark that never repeats between neighbouring blocks or levels.
