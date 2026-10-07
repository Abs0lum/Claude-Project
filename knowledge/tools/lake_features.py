#!/usr/bin/env python3
"""lake_features.py — his SP2 ruling (16:47 10-02): "yes, plus add lake features". The habitat map has three LAKE classes
(LAKE_TEMPERATE / LAKE_BOREAL / LAKE_WARM = still fresh water inside land biomes); a new world has almost none, so the
lake fish (bass, catfish, pike ...) had nowhere to spawn. This adds natural PONDS to those biomes.

Six pond templates (2 shapes x 3 climates), written with tools/mcstructure.py into BP-02 1.3.206 structures/pw/ponds/:
  temperate  dirt banks, clay + gravel bed, lily pads on ~8 % of the surface
  boreal     gravel + stone bed, no lilies
  warm       sand + mud bed, lily pads on ~12 %
Each pond is SEALED inside its own blocks: every water cell has water or a bank/bed block on all four sides and below,
and the surface ring is grass at the water's level -> a pond never spills, whatever the slope (on a slope the low side
shows a short grass bank).
Placement: before_surface_pass (before trees, so the ground height is the ground, not a canopy); the pond's surface sits
at the ground's top block (query.heightmap = first air above ground); 1 in 24 chunks per template (about 1 pond in 12
chunks per climate); the biome filter is spawn_gen's proven per-biome tag picks for the LAKE profile sets; the structure
may only cut natural ground (block_intersection allowlist) — anything else and the pond is skipped.
Report: _docs/mobs/LAKE-FEATURES-REPORT.json"""
import json
import math
import random
import zlib
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import mcstructure as M  # noqa: E402
import spawn_gen as G  # noqa: E402
from habitat_profiles import LAKE_BOREAL, LAKE_TEMPERATE, LAKE_WARM  # noqa: E402

BP = ROOT / "_build/bp02-206"
CLIMATES = {
    "temperate": {"biomes": LAKE_TEMPERATE, "bank": "minecraft:dirt", "bed": ["minecraft:clay", "minecraft:gravel",
                                                                               "minecraft:dirt"], "lily": 0.08},
    "boreal": {"biomes": LAKE_BOREAL, "bank": "minecraft:dirt", "bed": ["minecraft:gravel", "minecraft:stone",
                                                                         "minecraft:gravel"], "lily": 0.0},
    "warm": {"biomes": LAKE_WARM, "bank": "minecraft:dirt", "bed": ["minecraft:sand", "minecraft:mud", "minecraft:sand"],
             "lily": 0.12},
}
SHAPES = {"a": (9, 7, 2), "b": (13, 10, 3)}       # (length, width, max depth)
ALLOW = ["minecraft:air", "minecraft:grass_block", "minecraft:dirt", "minecraft:coarse_dirt", "minecraft:podzol",
         "minecraft:stone", "minecraft:andesite", "minecraft:diorite", "minecraft:granite", "minecraft:gravel",
         "minecraft:sand", "minecraft:clay", "minecraft:mud", "minecraft:short_grass", "minecraft:tall_grass",
         "minecraft:fern", "minecraft:large_fern", "minecraft:snow_layer", "minecraft:dandelion", "minecraft:poppy",
         "minecraft:moss_block", "minecraft:mycelium", "minecraft:deepslate", "minecraft:tuff", "minecraft:dirt_with_roots"]


def pond(length, width, max_depth, climate, seed):
    """Irregular ellipse; depth falls off from the centre. Returns (Structure, water cells, depth)."""
    rnd = random.Random(seed)
    c = CLIMATES[climate]
    sx, sz = length + 2, width + 2                # + one bank ring each side
    sy = max_depth + 3                            # seal layer + bed layer + water layers + lily layer (BDS 18:15: a
                                                  # gravel / sand bed at layer 0 fell into a cave below and the pond drained)
    st = M.Structure((sx, sy, sz))
    cx, cz = (sx - 1) / 2, (sz - 1) / 2
    wobble = [rnd.uniform(0.85, 1.1) for _ in range(16)]
    depth = {}
    for x in range(1, sx - 1):
        for z in range(1, sz - 1):
            ang = math.atan2(z - cz, x - cx)
            k = wobble[int((ang + math.pi) / (2 * math.pi) * 16) % 16]
            r = math.hypot((x - cx) / (length / 2 * k), (z - cz) / (width / 2 * k))
            if r < 1.0:
                depth[(x, z)] = max(1, min(max_depth, int(round((1 - r) * max_depth + 0.4))))
    top = max_depth + 1                           # layer index of the water surface (= ground top block in the world)
    for x in range(sx):
        for z in range(sz):
            d = depth.get((x, z))
            if d is None:
                nb = any((x + dx, z + dz) in depth for dx in (-1, 0, 1) for dz in (-1, 0, 1))
                if nb:                            # bank ring: grass at the surface, bank below (seals the sides)
                    st.set(x, top, z, "minecraft:grass_block")
                    for y in range(top - 1, -1, -1):
                        st.set(x, y, z, c["bank"])
                continue
            for y in range(top, top - d, -1):
                st.set(x, y, z, "minecraft:water", {"liquid_depth": M.i(0)})
            st.set(x, top - d, z, rnd.choice(c["bed"]))
            for y in range(top - d - 1, -1, -1):  # below the bed: bank (keeps the box sealed under shallow edges)
                st.set(x, y, z, c["bank"])
            if c["lily"] and d >= 1 and rnd.random() < c["lily"]:
                st.set(x, top + 1, z, "minecraft:waterlily", {"direction": M.i(rnd.randrange(4))})
    st.single_layer = False
    return st, len(depth), top


def sealed(st, top):
    """Every water cell: water / solid on all 4 sides and below (never air or structure void)."""
    sx, sy, sz = st.size
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                b = st.get(x, y, z)
                if not b or b[0] != "minecraft:water":
                    continue
                for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, -1, 0)):
                    nx, ny, nz = x + dx, y + dy, z + dz
                    if not (0 <= nx < sx and 0 <= ny < sy and 0 <= nz < sz):
                        return False
                    nb = st.get(nx, ny, nz)
                    if not nb or nb[0] in ("minecraft:air",):
                        return False
    return True


def main():
    table = G.biome_table()
    sel = G.selectors(table)
    present = {b for b, v in table.items() if v["present"]}
    report = []
    for climate, c in CLIMATES.items():
        target = c["biomes"] & present
        bfilter = G.filter_for(target, sel)
        hit = {b for b in present if G.evaluate(bfilter, table[b]["tags"])}
        assert hit == target, (climate, hit ^ target)
        for shape, (length, width, depth) in SHAPES.items():
            name = f"pond_{climate}_{shape}"
            st, cells, top = pond(length, width, depth, climate, seed=zlib.crc32(name.encode()))
            assert sealed(st, top), name
            sp = BP / "structures/pw/ponds" / f"{name}.mcstructure"
            sp.parent.mkdir(parents=True, exist_ok=True)
            sp.write_bytes(st.to_bytes())
            back = M.Structure.from_bytes(sp.read_bytes())
            assert back.size == st.size and back.layer0 == st.layer0, name
            feat = {"format_version": "1.21.40", "minecraft:structure_template_feature": {
                "description": {"identifier": f"pw:{name}_feature"},
                "structure_name": f"pw:ponds/{name}",
                "adjustment_radius": 0, "facing_direction": "random",
                "constraints": {"block_intersection": {"block_allowlist": ALLOW}}}}
            (BP / "features" / f"{name}_feature.json").write_text(json.dumps(feat, indent=2))
            rule = {"format_version": "1.13.0", "minecraft:feature_rules": {
                "description": {"identifier": f"pw:{name}_rule", "places_feature": f"pw:{name}_feature"},
                "conditions": {"placement_pass": "before_surface_pass", "minecraft:biome_filter": bfilter},
                "distribution": {"iterations": 1, "scatter_chance": {"numerator": 1, "denominator": 24},
                                 "coordinate_eval_order": "zxy",
                                 "x": {"distribution": "uniform", "extent": [0, 15]},
                                 "y": f"q.heightmap(v.worldx, v.worldz) - {top + 1}",
                                 "z": {"distribution": "uniform", "extent": [0, 15]}}}}
            (BP / "feature_rules" / f"{name}_rule.json").write_text(json.dumps(rule, indent=2))
            report.append({"pond": name, "size": st.size, "water_cells": cells, "max_depth": depth,
                           "biomes": sorted(target), "lily": c["lily"]})
            print(name, st.size, "water columns", cells, "biomes", len(target))
    (ROOT / "_docs/mobs/LAKE-FEATURES-REPORT.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
