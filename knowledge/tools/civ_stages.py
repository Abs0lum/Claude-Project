#!/usr/bin/env python3
"""civ_stages.py — task #167 first slice (his TS approval + the economy draft §'buildings evolve through stages'):
cut a finished CIVITAS building file into BUILD STAGES that the village clock places one after another.

  s0 plot      clears the whole box (every cell that is air in the finished building, and every cell a later stage fills,
               becomes air) and lays the ground work: dirt / grass / stone / smooth stone / stone bricks / cobblestone
               (foundation, cellar walls, floor slab, path)
  s1 frame     spruce logs (posts) + the oak-plank FLOORS (a plank layer that covers the inside of the footprint)
  s2 walls     the remaining planks (walls), windows, door, ladder, trapdoor, manhole, hearth, flue + the hatch-lid entity
  s3 roof      every pw:roof* block
  s4 furnished furniture, chests, barrels, beds, lights and every other block left + the station / zone / datum markers
Every stage file has the finished building's size; cells that are not that stage's are STRUCTURE VOID (placing it keeps
what the earlier stages built). Placing s0..s4 in order rebuilds the finished building exactly (checked below, cell by cell).
Usage: civ_stages.py <structure file> <out dir>   (names: <stem>_s0 .. <stem>_s4)"""
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

GROUND = {"minecraft:dirt", "minecraft:grass_block", "minecraft:stone", "minecraft:smooth_stone", "minecraft:stone_bricks",
          "minecraft:cobblestone", "minecraft:gravel", "minecraft:sand", "minecraft:coarse_dirt", "minecraft:farmland",
          "minecraft:grass_path", "minecraft:water"}
WALL_FITTINGS = ("minecraft:glass_pane", "minecraft:wooden_door", "minecraft:spruce_door", "minecraft:ladder", "minecraft:trapdoor",
                 "pw:manhole_cover", "pw:hearth", "pw:flue", "minecraft:glass", "minecraft:fence_gate", "minecraft:oak_fence",
                 "minecraft:spruce_fence", "minecraft:stone_brick_wall", "minecraft:bricks")
STAGES = ["plot", "frame", "walls", "roof", "furnished"]
DATUM_Y = 15                                     # every civgen box: feet 0 at y = 15 (box bottom = feet -15)


def floor_rows(st):
    """y levels whose planks (any wood) cover at least half of the footprint's inside (x, z not on the outer ring)."""
    sx, sy, sz = st.size
    inside = [(x, z) for x in range(1, sx - 1) for z in range(1, sz - 1)]
    rows = set()
    for y in range(sy):
        n = sum(1 for x, z in inside if (st.get(x, y, z) or ("",))[0].endswith("_planks"))
        if n * 2 >= len(inside):
            rows.add(y)
    return rows


def stage_of(name, y, floors):
    """s0 ground work (anything ground-like BELOW grade: foundation, cellar shell, floor course, paths, fields);
    s1 frame (every log + the plank floors); s2 walls and fittings (planks, masonry, glass, doors, ladders, fences,
    hearth, flue); s3 roof (every pw:roof* / crown ring); s4 the rest (furniture, stock, beds, crops, lights)."""
    feet = y - DATUM_Y
    if name in GROUND and feet < 0:
        return 0
    if name.endswith(("_log", "_wood")) or (name.endswith("_planks") and y in floors):
        return 1
    if name.endswith("_planks") or name in GROUND or name.startswith(WALL_FITTINGS):
        return 2
    if name.startswith(("pw:roof", "pw:crown_ring")):
        return 3
    return 4


def cut(src, out_dir):
    st = M.Structure.from_bytes(Path(src).read_bytes())
    sx, sy, sz = st.size
    floors = floor_rows(st)
    stages = [M.Structure(st.size, st.origin) for _ in STAGES]
    for s in stages:
        s.layer_type = st.layer_type
    counts = [0] * len(STAGES)
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                b = st.get(x, y, z)
                if b is None:
                    continue
                name, states, ver = b
                k = 0 if name == "minecraft:air" else stage_of(name, y, floors)
                if k > 0:                                    # the plot stage clears this cell first
                    stages[0].layer0[stages[0].index(x, y, z)] = stages[0]._pal("minecraft:air", {})
                stages[k].layer0[stages[k].index(x, y, z)] = stages[k]._pal(name, states, ver)
                w = st.layer1[st.index(x, y, z)]
                if w >= 0:
                    stages[k].layer1[stages[k].index(x, y, z)] = stages[k]._pal(*st.palette[w])
                counts[k] += 1
    for e in st.entities:
        ident = e.value["identifier"].value
        stages[2 if ident == "pw:hatch_lid" else 4].entities.append(e)
    # proof: s0..s4 in order == the finished building
    for x in range(sx):
        for y in range(sy):
            for z in range(sz):
                cell = None
                for s in stages:
                    k = s.layer0[s.index(x, y, z)]
                    if k >= 0:
                        cell = s.palette[k][:2]
                want = st.get(x, y, z)
                assert (cell is None and want is None) or (cell and want and cell[0] == want[0] and
                                                          {a: (v.type, v.value) for a, v in cell[1].items()} ==
                                                          {a: (v.type, v.value) for a, v in want[1].items()}), (x, y, z)
    stem = Path(src).stem
    out = []
    for i, s in enumerate(stages):
        p = Path(out_dir) / f"{stem}_s{i}.mcstructure"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(s.to_bytes())
        out.append((p.name, STAGES[i], counts[i], len(s.entities)))
    return out, sorted(floors)


if __name__ == "__main__":
    res, floors = cut(sys.argv[1], sys.argv[2])
    print("floor rows", floors)
    for r in res:
        print(r)
