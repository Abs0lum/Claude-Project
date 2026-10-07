#!/usr/bin/env python3
"""ft_tpl_gen_lite.py — the LIGHT carbon-copy falling tree (D-C526: RP-01 1.3.120's full copy loaded 606k cubes at boot
and the game closed during the load screen on his hardware). Same frames, bones, lift / turn laws as ft_tpl_gen.py
(imported), but every template is meshed into few boxes:

  * LEAVES: 3D greedy meshing of the template's leaf cells into boxes of at most MAXB blocks a side; each box uses BOX UV
    into a TILED leaf region of the species atlas (the leaf face repeated, holes filled with a shadow green so a merged
    box never shows the sky through its face) -> a 4 x 2 x 3 leaf box shows 4 x 2 x 3 leaf faces at their true scale.
    A box belongs to the bone of its lowest layer (cut visibility per layer, as before).
  * SILHOUETTE: up to CLUSTERS_MAX of the crown's outermost leaves (open upward or sideways) get one upright cluster
    plane each (per-face uv into the cluster tile), so the edge is fuzzy, not a box outline.
  * WOOD: one box per log cell (width = the standing block's width incl. bark panels), box UV into a tiled bark strip
    (per tier) of the same atlas; vertical runs of the trunk ABOVE layer RUN_FROM are merged (the cut never sits there).
One render controller pair as before (trunk + canopy), both now read the SAME species atlas (bark and leaves together).
Usage: ft_tpl_gen_lite.py RP_DIR BP_DIR [--stats]
Complexity: O(cells) per template (greedy meshing is linear in the template's bounding volume)."""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import ft_tpl_gen as F  # noqa: E402   (decode, kind, leaf_table, ry, rnd, tint_ratio, load_geo, WORLD_FACE)

MAXB = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--maxb=")), "4"))   # leaf box edge cap in blocks (tiled region below holds a 4 x 4 x 4 box net)
CLUSTERS_MAX = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--clusters=")), "40"))   # silhouette planes per template
CLOSE_PASSES = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--close=")), "2"))
CLOSE_N = 4
RUN_FROM = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--runfrom=")), "8"))   # trunk cells from this layer up may merge into vertical runs
U = 16                      # uv units per block
LEAF_REG = (0, 0, MAXB * U, MAXB * U)          # tiled leaf region; PER-FACE uv from its corner (a face <= MAXB blocks)
BARK_W = U                  # one bark strip per tier, 16 units wide
BARK_H = MAXB * U           # runs up to MAXB blocks
TIERS = ["young", "mature", "old", "elder"]
BARK_X = LEAF_REG[2]                                                  # bark strips to the right of the leaf region
CLUSTER_UV = (BARK_X + 4 * BARK_W, 0)                                 # one 16 x 16 cluster tile to the right of the bark
ATLAS_W, ATLAS_H, PX = LEAF_REG[2] + 4 * BARK_W + U, max(LEAF_REG[3], BARK_H, U), 4               # 256 x 288 units at 4 px per unit


def tier_of(name):
    for i, t in enumerate(TIERS):
        if f"_{t}" in name:
            return i
    return 1


def greedy_boxes(cells):
    """3D greedy meshing of a set of (x, y, z) cells into boxes (x0, y0, z0, sx, sy, sz), each side <= MAXB."""
    left = set(cells)
    boxes = []
    for c in sorted(cells, key=lambda p: (p[1], p[0], p[2])):
        if c not in left:
            continue
        x0, y0, z0 = c
        sx = 1
        while sx < MAXB and (x0 + sx, y0, z0) in left:
            sx += 1
        sz = 1
        while sz < MAXB and all((x0 + i, y0, z0 + sz) in left for i in range(sx)):
            sz += 1
        sy = 1
        while sy < MAXB and all((x0 + i, y0 + sy, z0 + k) in left for i in range(sx) for k in range(sz)):
            sy += 1
        for i in range(sx):
            for j in range(sy):
                for k in range(sz):
                    left.discard((x0 + i, y0 + j, z0 + k))
        boxes.append((x0, y0, z0, sx, sy, sz))
    return boxes


def file_box(t0, size):
    """template-relative cell box (x0, y0, z0) + (sx, sy, sz) blocks -> entity-file origin/size in units (z mirrored)."""
    x0, y0, z0 = t0
    sx, sy, sz = size
    return [16 * x0 - 8, 16 * y0, -16 * (z0 + sz - 1) - 8], [16 * sx, 16 * sy, 16 * sz]


def build(name, cells, root, sp_leaf, leaf_tab, leaf_geos, widths, collar):
    occupied = {p for p, e in cells.items() if F.kind(e["name"])}
    rel = {(p[0] - root[0], p[1] - root[1], p[2] - root[2]): e for p, e in cells.items() if F.kind(e["name"])}
    leaves = {k for k, e in rel.items() if F.kind(e["name"]) == "leaf" and 0 <= k[1] < F.MAX_LAYERS}
    woods = {k: e for k, e in rel.items() if F.kind(e["name"]) == "wood" and 0 <= k[1] < F.MAX_LAYERS}
    bones = {}

    def bone(nm, rot=None):
        b = bones.setdefault(nm, {"name": nm, "parent": "tturn", "pivot": [0, 0, 0], "cubes": []})
        if rot:
            b["rotation"] = rot
        return b

    # leaves: enclosed cells still take part in meshing (they make the boxes bigger, never visible); CLOSING passes fill
    # crown holes (an air cell with >= CLOSE_N leaf / wood neighbours of 6 counts as leaf for the mesh) -> bigger boxes
    mesh = set(leaves)
    solid = set(rel)
    for _ in range(CLOSE_PASSES):
        add = set()
        xs = [k[0] for k in mesh] or [0]
        zs = [k[2] for k in mesh] or [0]
        ysl = [k[1] for k in mesh] or [0]
        for x in range(min(xs), max(xs) + 1):
            for y in range(min(ysl), max(ysl) + 1):
                for z in range(min(zs), max(zs) + 1):
                    c = (x, y, z)
                    if c in mesh or c in solid:
                        continue
                    n = sum((x + d[0], y + d[1], z + d[2]) in mesh or (x + d[0], y + d[1], z + d[2]) in solid for d in F.NEIGH)
                    if n >= CLOSE_N:
                        add.add(c)
        if not add:
            break
        mesh |= add
    for (x0, y0, z0, sx, sy, sz) in greedy_boxes(mesh):
        o, s = file_box((x0, y0, z0), (sx, sy, sz))
        fw = {"north": (s[0], s[1]), "south": (s[0], s[1]), "east": (s[2], s[1]), "west": (s[2], s[1]), "up": (s[0], s[2]), "down": (s[0], s[2])}
        bone(f"l{y0}_0")["cubes"].append({"origin": o, "size": s,
                                          "uv": {f: {"uv": [LEAF_REG[0], LEAF_REG[1]], "uv_size": [a, b]} for f, (a, b) in fw.items()}})
    # silhouette clusters: outermost leaves open up / sideways, spread evenly
    edge = [k for k in sorted(leaves) if any((k[0] + d[0], k[1] + d[1], k[2] + d[2]) not in {c for c in rel}
                                              for d in ((0, 1, 0), (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1)))]
    step = max(1, math.ceil(len(edge) / CLUSTERS_MAX))
    plane = next((c for c in leaf_geos["geometry.pw_leaves2_full"] if 0 in [round(v, 6) for v in c["size"]]
                  and (c.get("rotation") or [0, 0, 0])[1]), None)
    for k in edge[::step][:CLUSTERS_MAX]:
        g = np.array([16.0 * k[0], 16.0 * k[1], -16.0 * k[2]])
        c = F.shift_cube({**plane, "uv": {f: {**v, "material_instance": "x"} for f, v in plane["uv"].items()}}, g,
                         tex_of=lambda mi: "c0")
        for f in c["uv"].values():                                   # point the face at the cluster tile of this atlas
            u0, v0 = f["uv"]
            tu, tv = F.tile_uv("c0")
            f["uv"] = [u0 - tu + CLUSTER_UV[0], v0 - tv + CLUSTER_UV[1]]
        bone(f"l{k[1]}_0")["cubes"].append(c)
    # wood: one box per cell; the trunk column above RUN_FROM merges into vertical runs
    done = set()
    for k in sorted(woods, key=lambda p: (p[0], p[2], p[1])):
        if k in done:
            continue
        e = woods[k]
        w = min(16, widths.get(e["name"], 16))
        run = 1
        if k[1] >= RUN_FROM:
            while run < 2 * MAXB and (k[0], k[1] + run, k[2]) in woods and woods[(k[0], k[1] + run, k[2])]["name"] == e["name"]:
                run += 1
        for j in range(run):
            done.add((k[0], k[1] + j, k[2]))
        g = (16 * k[0], 16 * k[1], -16 * k[2])
        bark_u = BARK_X + tier_of(e["name"]) * BARK_W
        side = {"uv": [bark_u, 0], "uv_size": [F.rnd(w), 16 * run]}
        cap = {"uv": [bark_u, 0], "uv_size": [F.rnd(w), F.rnd(w)]}
        bone(f"w{k[1]}")["cubes"].append({"origin": [F.rnd(g[0] - w / 2), g[1], F.rnd(g[2] - w / 2)], "size": [F.rnd(w), 16 * run, F.rnd(w)],
                                          "uv": {"north": side, "south": side, "east": side, "west": side, "up": cap, "down": cap}})
    n_cubes = sum(len(b["cubes"]) for b in bones.values())
    ys = [int(''.join(ch for ch in n[1:].split('_')[0])) for n in bones]
    h = (max(ys) + 1) if ys else 1
    ext = max([abs(c["origin"][0]) + c["size"][0] for b in bones.values() for c in b["cubes"]] +
              [abs(c["origin"][2]) + c["size"][2] for b in bones.values() for c in b["cubes"]] + [16])
    # 1004b (D-C563 / R6 §6.1): the fall hinge is the ROOT COLUMN's leading face (file -x, the side the fall animation tips
    # toward), not the axis — pivot x = -(width of the layer-1 wood box over the root cell) / 2; the pivot's y stays 0 (the
    # model's base = the stump top after the -16 seat shift). A 2x2 elder pivots on its root column's face (8 px).
    w_root = 16
    for k, e in woods.items():
        if k[0] == 0 and k[2] == 0 and k[1] == 1:
            w_root = min(16, widths.get(e["name"], 16))
            break
    head = [{"name": "root", "pivot": [-F.rnd(w_root / 2), 0, 0]},
            {"name": "tlift", "parent": "root", "pivot": [0, 0, 0]},
            {"name": "tturn", "parent": "tlift", "pivot": [0, 0, 0]},
            {"name": "branch_l", "parent": "root", "pivot": [0, 0, 0]},
            {"name": "branch_r", "parent": "root", "pivot": [0, 0, 0]}]
    if collar:
        head.append({**collar, "parent": "root"})
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.ft_tpl.{name}", "texture_width": ATLAS_W, "texture_height": ATLAS_H,
                        "visible_bounds_width": math.ceil(2 * ext / 16) + 2, "visible_bounds_height": h * 2 + 4,
                        "visible_bounds_offset": [0, h / 2, 0]},
        "bones": head + list(bones.values())}]}
    return geo, {"cubes": n_cubes, "leaves": len(leaves), "wood": len(woods), "layers": h}


def atlas(rp, tex_dir, sp, trunk_paths, out):
    """species atlas: tiled opaque leaf region, tiled bark strips per tier, one cluster tile."""
    ratio = F.tint_ratio(tex_dir, sp)
    img = Image.new("RGBA", (ATLAS_W * PX, ATLAS_H * PX), (0, 0, 0, 0))
    tile = 16 * PX
    f0 = np.asarray(Image.open(tex_dir / f"{sp}_f0.png").convert("RGBA").resize((tile, tile), Image.LANCZOS), dtype=float)
    f0[..., :3] = np.clip(f0[..., :3] * ratio, 0, 255)
    solid = f0[f0[..., 3] > 128][:, :3].mean(0) * 0.55                       # shadow green behind the leaf cut-outs
    a = f0[..., 3:4] / 255.0
    opaque = np.concatenate([f0[..., :3] * a + solid * (1 - a), np.full(f0.shape[:2] + (1,), 255.0)], axis=2)
    leaf = Image.fromarray(opaque.astype(np.uint8), "RGBA")
    for x in range(0, LEAF_REG[2], 16):
        for y in range(0, LEAF_REG[3], 16):
            img.paste(leaf, ((LEAF_REG[0] + x) * PX, (LEAF_REG[1] + y) * PX))
    tint = np.array([0.82, 0.79, 0.74])                                       # the old trunk RC colour, baked in
    for i, tp in enumerate(trunk_paths):
        if not tp or not tp.exists():
            continue
        b = np.asarray(Image.open(tp).convert("RGBA").resize((tile, tile), Image.LANCZOS), dtype=float)
        b[..., :3] = np.clip(b[..., :3] * tint, 0, 255)
        bark = Image.fromarray(b.astype(np.uint8), "RGBA")
        for y in range(0, BARK_H, 16):
            img.paste(bark, ((BARK_X + i * BARK_W) * PX, y * PX))
    c0 = np.asarray(Image.open(tex_dir / f"{sp}_c0.png").convert("RGBA").resize((tile, tile), Image.LANCZOS), dtype=float)
    c0[..., :3] = np.clip(c0[..., :3] * ratio, 0, 255)
    img.paste(Image.fromarray(c0.astype(np.uint8), "RGBA"), (CLUSTER_UV[0] * PX, CLUSTER_UV[1] * PX))
    img.save(out, optimize=True)


def main():
    rp, bp = Path(sys.argv[1]), Path(sys.argv[2])
    stats_only = "--stats" in sys.argv
    print(F._selftest())
    tex_dir = rp / "textures/blocks/pw_leaves2"
    leaf_geos = {gid: [c for b in F.load_geo(rp / "models/blocks/pw_leaves2.geo.json", gid)["bones"] for c in b.get("cubes", [])]
                 for gid in ("geometry.pw_leaves2_full",)}
    # standing trunk widths incl. bark panels (same law as ft_tpl_gen)
    block_geo = {}
    for f in (bp / "blocks").rglob("*.json"):
        try:
            blk = json.loads(f.read_text())["minecraft:block"]
        except Exception:
            continue
        g = blk["components"].get("minecraft:geometry")
        block_geo[blk["description"]["identifier"]] = g if isinstance(g, str) else (g or {}).get("identifier")
    model_w = {}
    for f in (rp / "models/blocks").glob("*.geo.json"):
        try:
            for g in json.loads(f.read_text())["minecraft:geometry"]:
                cs = [c for b in g["bones"] for c in b.get("cubes", []) if not any((c.get("rotation") or [0, 0, 0]))]
                if cs:
                    model_w[g["description"]["identifier"]] = 2 * max(max(abs(c["origin"][0]), abs(c["origin"][0] + c["size"][0]),
                                                                            abs(c["origin"][2]), abs(c["origin"][2] + c["size"][2])) for c in cs)
        except Exception:
            continue
    widths = {bid: min(16, model_w[gid]) for bid, gid in block_geo.items() if gid in model_w}
    old_geos = {}
    for f in (rp / "models/entity").glob("falling_tree_*.geo.json"):
        for g in json.loads(f.read_text())["minecraft:geometry"]:
            old_geos[g["description"]["identifier"]] = g
    collar = next((dict(b) for b in old_geos["geometry.ft_falling_tree.oak_mature"]["bones"] if b["name"] == "break_collar"), None)
    if collar:
        collar.pop("parent", None)
    ent = json.loads((rp / "entity/falling_tree.json").read_text())["minecraft:client_entity"]["description"]["textures"]
    if not stats_only:
        for sp in F.SPECIES_LEAF:
            wood_sp = {"pale_oak": "pale_oak"}.get(sp, sp)
            paths = [rp / (ent.get(f"trunk_{wood_sp}_{t}", "") + ".png") if ent.get(f"trunk_{wood_sp}_{t}") else None for t in TIERS]
            atlas(rp, tex_dir, sp, paths, rp / f"textures/entity/fallingtree/leafatlas_{sp}.png")
    out_geo = rp / "models/entity/ft_tpl"
    index, tot, worst = [], 0, None
    agg = {"cubes": 0, "leaves": 0, "wood": 0}
    for p in sorted((bp / "structures/pw/trees").glob("*.mcstructure")):
        cells, root = F.decode(p)
        if not root:
            continue
        leaf_names = {e["name"] for e in cells.values() if e["name"].endswith("_leaves")}
        sp_leaf = next(iter(leaf_names)).replace("pw:", "").replace("_leaves", "") if leaf_names else "oak"
        geo, st = build(p.stem, cells, root, sp_leaf, None, leaf_geos, widths, collar)
        txt = json.dumps(geo, separators=(",", ":"))
        tot += len(txt)
        for k in agg:
            agg[k] += st[k]
        if not worst or st["cubes"] > worst[1]:
            worst = (p.stem, st["cubes"])
        index.append({"name": p.stem, "leaf": sp_leaf, "layers": st["layers"], "bytes": len(txt)})
        if not stats_only:
            (out_geo / f"{p.stem}.geo.json").write_text(txt)
    F.DOCS.mkdir(parents=True, exist_ok=True)
    (F.DOCS / "ft_tpl_index.json").write_text(json.dumps(index, indent=0))
    print(f"LITE templates {len(index)} · leaf cells {agg['leaves']} · wood cells {agg['wood']} · CUBES {agg['cubes']} "
          f"(avg {agg['cubes'] / max(1, len(index)):.0f}, max {worst}) · geometry {tot / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
