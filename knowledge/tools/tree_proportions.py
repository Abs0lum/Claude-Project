#!/usr/bin/env python3
"""tree_proportions.py — measure every tree template's shape (10-03, his 13:57 ask: "trees a little tall, canopy too large,
canopy way high on a skinny trunk — research sizing and scaling").

For each .mcstructure in BP-02 structures/pw/trees it reports, in BLOCKS:
  H      total height (lowest trunk cell to the top leaf)
  CBH    crown-base height: height of the lowest leaf cell above the trunk base (the bare-trunk length)
  CL     crown length = H - CBH
  CW     crown width: mean of the x and z extents of the leaves
  TW     trunk width at the base (cells of wood in the lowest wood layer, as an edge length)
  ratios CR = CL/H (crown ratio), CW/H, H/TW (slenderness)
plus the block names in the palette (which leaf blocks the template uses).
Usage: tree_proportions.py [GLOB]   -> table on stdout + _docs/tree_proportions.json
Complexity: O(cells) per template."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

TREES = Path("/home/claude/_build/bp02-216/structures/pw/trees")
OUT = Path("/home/claude/_docs/tree_proportions.json")


def is_leaf(name):
    return "leaves" in name or "leaf" in name


def is_wood(name):
    """Every non-air, non-leaf block in a tree template is wood (pw:oak_mature etc. carry no _log suffix)."""
    return not is_leaf(name) and name not in ("minecraft:air", "minecraft:structure_void") and "vine" not in name \
        and "propagule" not in name and "bee_nest" not in name and "snow" not in name


def measure(path):
    """Return the shape metrics of one template (dict)."""
    root = M.decode(path.read_bytes())
    t = root.plain() if hasattr(root, "plain") else root
    if isinstance(t, tuple):
        t = t[1].plain()
    sx, sy, sz = t["size"]
    st = t["structure"]
    layer = st["block_indices"][0]
    pal = st["palette"]["default"]["block_palette"]
    names = [p["name"] for p in pal]
    leaves, woods = [], []
    for idx, pi in enumerate(layer):
        if pi < 0:
            continue
        n = names[pi]
        x = idx // (sy * sz)
        y = (idx // sz) % sy
        z = idx % sz
        if is_leaf(n):
            leaves.append((x, y, z))
        elif is_wood(n):
            woods.append((x, y, z))
    if not woods or not leaves:
        return None
    base = min(w[1] for w in woods)
    top = max(max(l[1] for l in leaves), max(w[1] for w in woods))
    height = top - base + 1
    # crown base: the lowest layer where leaves make a real ring (>= 4 leaf cells), not a single stray leaf
    per_y = Counter(l[1] for l in leaves)
    crown_y = min((y for y, c in per_y.items() if c >= 4), default=min(per_y))
    cbh = crown_y - base
    xs = [l[0] for l in leaves]
    zs = [l[2] for l in leaves]
    cw = ((max(xs) - min(xs) + 1) + (max(zs) - min(zs) + 1)) / 2
    base_cells = sum(1 for w in woods if w[1] == base)
    tw = math.sqrt(base_cells)
    pal_count = Counter(names[pi] for pi in layer if pi >= 0)
    return {"template": path.stem, "H": height, "CBH": cbh, "CL": height - cbh, "CW": round(cw, 1),
            "TW": round(tw, 2), "CR": round((height - cbh) / height, 2), "CW_H": round(cw / height, 2),
            "H_TW": round(height / tw, 1), "leaves": len(leaves), "logs": len(woods),
            "blocks": dict(pal_count.most_common(8))}


def main():
    pat = sys.argv[1] if len(sys.argv) > 1 else "*.mcstructure"
    rows = [r for r in (measure(p) for p in sorted(TREES.glob(pat))) if r]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rows, indent=1))
    groups = defaultdict(list)
    for r in rows:
        key = r["template"].rsplit("_", 1)[0]
        groups[key].append(r)
    print(f"{'group':18} {'n':>3} {'H':>5} {'CBH':>5} {'CL':>5} {'CW':>5} {'TW':>5} {'CR':>5} {'CW/H':>5} {'H/TW':>6} {'leaves':>7}")
    for k, g in sorted(groups.items()):
        av = lambda f: sum(r[f] for r in g) / len(g)  # noqa: E731
        print(f"{k:18} {len(g):3} {av('H'):5.1f} {av('CBH'):5.1f} {av('CL'):5.1f} {av('CW'):5.1f} {av('TW'):5.2f} "
              f"{av('CR'):5.2f} {av('CW_H'):5.2f} {av('H_TW'):6.1f} {av('leaves'):7.0f}")


if __name__ == "__main__":
    main()
