#!/usr/bin/env python3
"""tree_rescale.py — re-proportion every tree template (D-C525, his 14:15 rulings: TS1 c "mostly a" = crowns smaller,
trunks a little thicker; TS2 a = dark oak low and broad; TS3 = all species). Research: _docs/trees/TREE-PROPORTIONS-
RESEARCH-2026-10-03.md, corrected for the real visible trunk widths (young 0.625 m, mature 0.75, old 0.81 incl. bark).

Each template is RE-SAMPLED from its own cells (nearest neighbour, inverse mapping), so every leaf keeps its saved block
(variant, off, …) and the crown keeps its character:
  * horizontal: about the trunk footprint centre, scale sw (crown width target / current)
  * vertical, piecewise linear: [0, CBH_old] -> [0, CBH_new] (the bare trunk) and [CBH_old, top] -> [CBH_new, H_new]
  * the TRUNK (wood cells over the base footprint) is kept as a continuous column, mapped vertically only
  * branch wood not connected (26-neighbourhood) to the trunk after sampling becomes a leaf (it sat inside the crown)
  * the root cell stays at the template's root (same block, same tpl state); cells below the root are copied unchanged
Usage: tree_rescale.py SRC_TREES_DIR DST_TREES_DIR [--only GLOB] [--dry]
Output: rescaled .mcstructure files + _docs/trees/rescale_report.json. Complexity: O(cells) per template."""
import fnmatch
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

# group -> (crown width factor, new height or None, new crown-base height or None)
TARGETS = {
    "oak_young": (1.00, 9.0, None),
    "oak_mature": (0.75, 15.0, 4.5),
    "oak_old": (0.81, 16.0, None),
    "oak_elder": (0.95, 22.0, None),
    "dark_oak_elder": (0.90, None, None),
    "pale_oak_elder": (0.93, 12.5, None),
    "spruce_young": (0.68, None, None),
    "spruce_mature": (0.68, None, None),
    "spruce_old": (0.68, None, None),
    "spruce_elder": (0.68, None, None),
    "jungle_young": (0.90, None, 5.0),
    "jungle_mature": (0.75, None, 15.0),
    "jungle_old": (0.80, None, 16.0),
    "jungle_elder": (1.00, None, 19.0),
    "acacia": (0.80, 10.0, 6.0),
    "cherry": (0.72, 9.5, None),
    "mangrove": (0.80, 12.0, None),
    "birch_young": (1.0, None, None),
    "birch_mature": (1.0, None, None),
    "birch_old": (1.0, None, None),
}
VOID = ("minecraft:air", "minecraft:structure_void")


def is_leaf(n):
    return n.endswith("_leaves")


def is_root(n):
    """the template's T2 root block (pw:<stem>_root); not minecraft:mangrove_roots."""
    return n.startswith("pw:") and n.endswith("_root")


def is_wood(n):
    return (n.startswith("pw:") and any(n.endswith(s) for s in ("_young", "_mature", "_old", "_elder", "_root"))) \
        or (n.startswith("minecraft:") and n.endswith("_log")) or n == "minecraft:mangrove_roots"


def group_of(stem):
    return stem.rsplit("_", 1)[0]


def read(path):
    name, root = M.decode(path.read_bytes())
    st = root.value["structure"].value
    sx, sy, sz = [t.value for t in root.value["size"].value]
    l0 = [t.value for t in st["block_indices"].value[0].value]
    pal = st["palette"].value["default"].value["block_palette"].value
    names = [p.value["name"].value for p in pal]
    cells = {}
    for idx, pi in enumerate(l0):
        if pi < 0 or names[pi] in VOID:
            continue
        cells[(idx // (sy * sz), (idx // sz) % sy, idx % sz)] = pi
    return name, root, names, cells


def metrics(cells, names, rootc):
    leaves = [p for p, pi in cells.items() if is_leaf(names[pi])]
    woods = [p for p, pi in cells.items() if is_wood(names[pi])]
    base = rootc[1]
    top = max(p[1] for p in cells)
    per_y = Counter(p[1] for p in leaves)
    crown_y = min((y for y, c in per_y.items() if c >= 4), default=min(per_y) if per_y else base + 1)
    xs = [p[0] for p in leaves] or [0]
    zs = [p[2] for p in leaves] or [0]
    cw = ((max(xs) - min(xs) + 1) + (max(zs) - min(zs) + 1)) / 2
    return {"H": top - base + 1, "CBH": crown_y - base, "CW": cw, "leaves": len(leaves), "woods": len(woods)}


def rescale(path, out_path, dry=False, frame=None):
    name, root, names, cells = read(path)
    rootc = next(p for p, pi in cells.items() if names[pi].startswith("pw:") and names[pi].endswith("_root"))
    grp = group_of(path.stem)
    sw, h_new, cbh_new = TARGETS.get(grp, (1.0, None, None))
    m0 = metrics(cells, names, rootc)
    H0, C0 = m0["H"], max(1, m0["CBH"])
    if frame:                                            # v4 (10-06): the frame of the template's FIRST rescale (D-C525),
        H0, C0 = frame["H"], max(1, frame["CBH"])        # so a regenerated template maps its crown cell for cell
    # a new crown base without a new height SHIFTS the crown down (no stretch: a stretched crown repeats its layers)
    H1 = h_new if h_new else (H0 - (C0 - cbh_new) if cbh_new else H0)
    C1 = cbh_new if cbh_new else min(C0, max(1, round(C0 * H1 / H0)))
    H1, C1 = int(round(H1)), int(round(C1))
    rx, ry_, rz = rootc
    # trunk footprint: wood cells in the root's layer
    # trunk footprint: the root cell, plus (2x2 / 3x3 elders) root-layer wood within 2 cells that carries wood above it
    # (mangrove prop roots and acacia / cherry bends are branches, not the trunk)
    foot = {(rx, rz)}
    if names[cells[rootc]].endswith("_elder_root"):
        foot |= {(p[0], p[2]) for p, pi in cells.items() if p[1] == ry_ and is_wood(names[pi]) and max(abs(p[0] - rx), abs(p[2] - rz)) <= 2
                 and (p[0], ry_ + 1, p[2]) in cells and is_wood(names[cells[(p[0], ry_ + 1, p[2])]])}
    cx = sum(f[0] for f in foot) / len(foot)
    cz = sum(f[1] for f in foot) / len(foot)

    def ymap(yn):
        """new relative y (>= 0) -> old relative y (float)."""
        if yn < C1:
            return yn * C0 / C1
        return C0 + (yn - C1) * (H0 - C0) / max(1, (H1 - C1))

    half = max(max(abs(f[0] - cx) for f in foot), max(abs(f[1] - cz) for f in foot))
    margin = half + 1.0                                  # the ring of leaves hugging the trunk is kept unscaled

    def inv(vn, c):
        """new coordinate -> old coordinate on one horizontal axis: scale by 1/sw beyond the trunk's margin."""
        d = vn - c
        if abs(d) <= margin:
            return vn
        sgn = 1 if d > 0 else -1
        return c + sgn * (margin + (abs(d) - margin) / sw)

    def fwdh(vo, c):
        d = vo - c
        if abs(d) <= margin:
            return vo
        sgn = 1 if d > 0 else -1
        return c + sgn * (margin + (abs(d) - margin) * sw)

    new = {}
    old_rel = {(p[0] - rx, p[1] - ry_, p[2] - rz): pi for p, pi in cells.items()}
    rel_x = [k[0] for k in old_rel]
    rel_z = [k[2] for k in old_rel]
    fx, fz = cx - rx, cz - rz
    nx0 = math.floor(fx + (min(rel_x) - fx) * sw) - 1
    nx1 = math.ceil(fx + (max(rel_x) - fx) * sw) + 1
    nz0 = math.floor(fz + (min(rel_z) - fz) * sw) - 1
    nz1 = math.ceil(fz + (max(rel_z) - fz) * sw) + 1
    for k, pi in old_rel.items():                        # below the root: unchanged
        if k[1] < 0:
            new[k] = pi
    foot_rel = {(f[0] - rx, f[1] - rz) for f in foot}
    for yn in range(0, H1):
        yo = int(round(ymap(yn)))
        for xn in range(nx0, nx1 + 1):
            for zn in range(nz0, nz1 + 1):
                if (xn, zn) in foot_rel:                # the trunk column: vertical map only
                    pi = old_rel.get((xn, yo, zn))
                    if pi is not None:
                        new[(xn, yn, zn)] = pi
                    continue
                xo = int(round(inv(xn, fx)))
                zo = int(round(inv(zn, fz)))
                if (xo, zo) in foot_rel:                # next to the trunk: sample one cell further out (the trunk's own
                    ddx, ddz = xn - fx, zn - fz          # cells are not leaves, so a shrunk crown would open a ring)
                    xo += (ddx > 0.25) - (ddx < -0.25)
                    zo += (ddz > 0.25) - (ddz < -0.25)
                pi = old_rel.get((xo, yo, zo))
                if pi is not None and (xo, zo) not in foot_rel and not is_wood(names[pi]):
                    new[(xn, yn, zn)] = pi           # leaves and the rest: inverse sampling
    # BRANCH WOOD: forward-mapped, and every pair of touching old branch cells is re-joined by a 3D line, so bent trunks
    # (acacia, cherry, mangrove) and branches stay continuous at any scale
    def ymap_fwd(yo):
        if yo < C0:
            return yo * C1 / C0
        return C1 + (yo - C0) * (H1 - C1) / max(1, (H0 - C0))

    def fwd(k):
        if (k[0], k[2]) in foot_rel:
            return (k[0], int(round(ymap_fwd(k[1]))), k[2])
        return (int(round(fwdh(k[0], fx))), int(round(ymap_fwd(k[1]))), int(round(fwdh(k[2], fz))))

    old_wood = {k: pi for k, pi in old_rel.items() if is_wood(names[pi]) and k[1] >= 0}
    for k, pi in old_wood.items():
        a = fwd(k)
        if (k[0], k[2]) not in foot_rel or a not in new:
            new[a] = pi
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    k2 = (k[0] + dx, k[1] + dy, k[2] + dz)
                    if k2 == k or k2 not in old_wood or k2 < k:
                        continue
                    b = fwd(k2)
                    steps = max(abs(b[0] - a[0]), abs(b[1] - a[1]), abs(b[2] - a[2]))
                    # program 228 F5 (STRUCTURE-AUDIT §5): a join that starts at the pw root block fills with the OTHER
                    # (upper) cell's block, so a stretched trunk never gets a second root one block up (jungle_young evens)
                    fill = old_wood[k2] if is_root(names[pi]) else pi
                    for t in range(1, steps):
                        c = tuple(int(round(a[i] + (b[i] - a[i]) * t / steps)) for i in range(3))
                        new[c] = fill
    new[(0, 0, 0)] = old_rel[(0, 0, 0)]                  # the root stays the root
    # branch connectivity: wood not 26-connected to the trunk through wood becomes a leaf (or goes)
    wood = {k for k, pi in new.items() if is_wood(names[pi])}
    seen, stack = set(), [k for k in wood if (k[0], k[2]) in foot_rel]
    seen.update(stack)
    while stack:
        a = stack.pop()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    b = (a[0] + dx, a[1] + dy, a[2] + dz)
                    if b in wood and b not in seen:
                        seen.add(b)
                        stack.append(b)
    orphans = wood - seen
    leaf_pis = Counter(pi for k, pi in new.items() if is_leaf(names[pi]))
    common_leaf = leaf_pis.most_common(1)[0][0] if leaf_pis else None
    converted = dropped = 0
    for k in orphans:
        near = [new[(k[0] + d[0], k[1] + d[1], k[2] + d[2])] for d in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1))
                if (k[0] + d[0], k[1] + d[1], k[2] + d[2]) in new and is_leaf(names[new[(k[0] + d[0], k[1] + d[1], k[2] + d[2])]])]
        if near:
            new[k] = near[0]
            converted += 1
        elif common_leaf is not None and k[1] >= C1:
            new[k] = common_leaf
            converted += 1
        else:
            del new[k]
            dropped += 1
    # bounding box -> new structure
    xs = [k[0] for k in new]
    ys = [k[1] for k in new]
    zs = [k[2] for k in new]
    ox, oy, oz = min(xs), min(ys), min(zs)
    sx, sy, sz = max(xs) - ox + 1, max(ys) - oy + 1, max(zs) - oz + 1
    n = sx * sy * sz
    l0 = [-1] * n
    for k, pi in new.items():
        x, y, z = k[0] - ox, k[1] - oy, k[2] - oz
        l0[(x * sy + y) * sz + z] = pi
    st = root.value["structure"].value
    st["block_indices"] = M.Tag(M.LIST, [M.Tag(M.LIST, [M.Tag(M.INT, v) for v in l0], M.INT),
                                         M.Tag(M.LIST, [M.Tag(M.INT, -1) for _ in range(n)], M.INT)], M.LIST)
    root.value["size"] = M.Tag(M.LIST, [M.Tag(M.INT, sx), M.Tag(M.INT, sy), M.Tag(M.INT, sz)], M.INT)
    bpd = st["palette"].value["default"].value.get("block_position_data")
    if bpd is not None and bpd.value:
        st["palette"].value["default"].value["block_position_data"] = M.Tag(M.COMPOUND, {})
    if not dry:
        out_path.write_bytes(M.encode(root, name))
    newcells = {(k[0] - ox, k[1] - oy, k[2] - oz): pi for k, pi in new.items()}
    m1 = metrics(newcells, names, (-ox, -oy, -oz))
    return {"template": path.stem, "group": grp, "before": m0, "after": m1, "orphan_wood_to_leaf": converted,
            "orphan_wood_dropped": dropped, "had_position_data": bool(bpd is not None and bpd.value)}


def main():
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    only = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else "*"
    dry = "--dry" in sys.argv
    dst.mkdir(parents=True, exist_ok=True)
    rep = []
    for p in sorted(src.glob("*.mcstructure")):
        if not fnmatch.fnmatch(p.stem, only):
            continue
        rep.append(rescale(p, dst / p.name, dry))
    out = Path("/home/claude/_docs/trees/rescale_report.json")
    out.write_text(json.dumps(rep, indent=1))
    g = defaultdict(list)
    for r in rep:
        g[r["group"]].append(r)
    print(f"{'group':16} {'n':>3}  H before->after   CBH before->after  CW before->after  leaves before->after  orphan->leaf/drop")
    for k, rs in sorted(g.items()):
        av = lambda s, f: sum(r[s][f] for r in rs) / len(rs)  # noqa: E731
        print(f"{k:16} {len(rs):3}  {av('before','H'):5.1f} -> {av('after','H'):5.1f}   {av('before','CBH'):5.1f} -> {av('after','CBH'):5.1f}"
              f"     {av('before','CW'):5.1f} -> {av('after','CW'):5.1f}    {av('before','leaves'):6.0f} -> {av('after','leaves'):6.0f}"
              f"     {sum(r['orphan_wood_to_leaf'] for r in rs)}/{sum(r['orphan_wood_dropped'] for r in rs)}")
    print("position data present in", sum(r["had_position_data"] for r in rep), "templates")


if __name__ == "__main__":
    main()
