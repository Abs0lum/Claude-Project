#!/usr/bin/env python3
"""ft_tpl_gen.py — the CARBON-COPY falling tree (D-C524, his 10-02 F10 = a + 10-03 14:03 "just fix the entity"):
one entity geometry per tree template, generated from the template's own cells, + one leaf atlas per species.

FRAMES (L-ROT-DIR, confirmed 09-27): entity file x mirrored vs the world (file +x = the entity's LEFT), front = file -z,
a bone rotation [0, ry, 0] = Ry(+ry) right-handed in file coords. Block geometry: file +x renders world west (x-mirror law).
  * template cell offset t (root-relative, as saved = north) -> canonical file position G(t) = 16 * (tx, ty, -tz)
    (cell bottom-centre; this is the entity frame at yaw 0 with the template unturned).
  * a block model rotated by minecraft:transformation [0, θ, 0] (right-handed in WORLD coords) maps into the entity file
    frame by M = A0 · Ry_w(θ) · B = Ry(180 - θ)  (A0 = diag(1,1,-1), B = diag(-1,1,1)) — so every leaf cell's block cubes
    are copied VERBATIM into a bone rotated [0, 180 - θ, 0] whose content is pre-placed at Ry(θ - 180)^-1 ... i.e. the
    cell centre p is stored as Ry(-(180 - θ))·p inside the bone (bone pivot 0,0,0), so after the bone turns it lands at p.
  * the script turns the whole template to the world with bone `turn`: ry = 90·r - yaw  (r = root facing quarter turns,
    yaw = the entity's initialRotation) — derived in this file's self-test (_selftest) and asserted numerically.
  * the cut: the entity spawns at (cut.y + 1); bone `lift` is moved down 16·(cut_rel + 1) by one of the constant
    animations ft_lift_<k> (position channels cannot take q.property arithmetic — engine law), and the layer bones at or
    below the cut are hidden by part_visibility on ft:cut_rel.
Bones: root(pivot 0) > tlift > tturn > w<L> (wood, layer L) / l<L>_<k> (leaves, layer L, bone turn k) ; collar + branch_l/r at root.
Leaf cells fully enclosed by leaves / wood are left out (never visible). Usage: ft_tpl_gen.py RP_DIR BP_DIR [--stats]
Outputs: RP_DIR/models/entity/ft_tpl/<template>.geo.json, RP_DIR/textures/entity/fallingtree/leafatlas_<sp>.png,
         _docs/fell/ft_tpl_index.json (template -> index, used by the BP script). Complexity: O(cells) per template."""
import json
import math
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

DOCS = Path("/home/claude/_docs/fell")
SPECIES_LEAF = ["oak", "spruce", "birch", "jungle", "acacia", "dark_oak", "mangrove", "cherry", "pale_oak"]
TILE_ORDER = ["f0", "f1", "f2", "f3", "f4", "f5", "c0", "c1", "c2", "c3"]
# ATLAS (uv units): the leaf-face tiles f0..f5 are laid out as BOX-UV NETS (64 x 32 units each, every 16 x 16 cell of the net
# filled with the tile, so whichever net cell the engine samples for a face shows the leaf) -> a leaf cube is written as
# {"origin", "size", "uv": [u, v]} (one short entry instead of six face blocks). Nets: 2 per row, 3 rows (0..96); the
# cluster tiles c0..c3 sit in the row below (96..112), 16 x 16 each. 8 px per unit (a 16-unit face = 128 px).
ATLAS_W, ATLAS_H, PX = 128, 112, 8


def tile_uv(tn):
    """uv origin of a tile: an f-tile's NET origin, or a c-tile's square."""
    i = TILE_ORDER.index(tn)
    if tn.startswith("f"):
        return (i % 2) * 64, (i // 2) * 32
    j = i - 6
    return j * 16, 96
MAX_LAYERS = 48
NEIGH = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
# template cell axes: x = east, y = up, z = south (structure cells, as saved = the north-facing template)
WORLD_FACE = {"east": (1, 0, 0), "west": (-1, 0, 0), "up": (0, 1, 0), "down": (0, -1, 0), "south": (0, 0, 1), "north": (0, 0, -1)}
PLANES_MAX = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--planes=")), "6"))


def block_face_world(face, theta):
    """Which WORLD side a block-model face ends up on after the block's transformation [0, θ, 0] (right-handed about +Y,
    world coords: +90 turns east -> north). Face names of block geometry are world-based (L-ROT-DIR / x-mirror law)."""
    if face in ("up", "down"):
        return face
    ring = ["north", "west", "south", "east"]          # +90 right-handed about +Y: east->north->west->south->east
    return ring[(ring.index(face) + int(round(theta / 90))) % 4]


def ry(deg):
    """Right-handed rotation about +Y (file coords), as L-ROT-DIR states bone rotations evaluate."""
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])


def rnd(v, n=3):
    r = round(float(v), n)
    return 0.0 if r == 0 else (int(r) if r == int(r) else r)


# ------------------------------------------------------------------------------------------------ inputs
def load_geo(path, ident):
    for g in json.loads(Path(path).read_text())["minecraft:geometry"]:
        if g["description"]["identifier"] == ident:
            return g
    raise KeyError(ident)


def leaf_table(bp, sp):
    """(variant, off) -> {geo, tex: {material_instance: tile name}, theta} from the leaf block's permutations."""
    blk = json.loads((bp / f"blocks/{sp}_leaves.json").read_text())["minecraft:block"]
    tab = {}
    for p in blk["permutations"]:
        m = re.findall(r"q\.block_state\('pw:(variant|off)'\)\s*==\s*(\d+)", p["condition"])
        key = dict((k, int(v)) for k, v in m)
        c = p["components"]
        mi = c.get("minecraft:material_instances", {})
        tex = {k: re.sub(rf"^pw_leaves2_{sp}_", "", v["texture"]) for k, v in mi.items()}
        theta = (c.get("minecraft:transformation", {}).get("rotation") or [0, 0, 0])[1]
        tab[(key.get("variant", 0), key.get("off", 0))] = {"geo": c["minecraft:geometry"], "tex": tex, "theta": theta}
    return tab


def decode(path):
    t = M.decode(path.read_bytes())
    t = t.plain() if hasattr(t, "plain") else t[1].plain()
    sx, sy, sz = t["size"]
    st = t["structure"]
    pal = st["palette"]["default"]["block_palette"]
    cells = {}
    root = None
    for idx, pi in enumerate(st["block_indices"][0]):
        if pi < 0:
            continue
        e = pal[pi]
        n = e["name"]
        if n in ("minecraft:air", "minecraft:structure_void"):
            continue
        x, y, z = idx // (sy * sz), (idx // sz) % sy, idx % sz
        cells[(x, y, z)] = e
        if n.startswith("pw:") and n.endswith("_root"):
            root = (x, y, z)
    return cells, root


def kind(name):
    if name.endswith("_leaves"):
        return "leaf"
    if re.match(r"^pw:[a-z_]+_(young|mature|old|elder)(_root)?$", name) or re.match(r"^pw:(acacia|cherry|mangrove)_root$", name) \
            or re.match(r"^minecraft:[a-z_]+_log$", name) or name == "minecraft:mangrove_roots":
        return "wood"
    return None


# ------------------------------------------------------------------------------------------------ cubes
SU, SV = ATLAS_W / 16, ATLAS_H / 16      # trunk textures are authored in 16 x 16 uv units; this geometry declares 64 x 48


def wood_cubes(o, width, caps):
    """A log cell for the falling copy. width 16 = full block (elder / vanilla logs / roots); a narrower width = the
    dodecagon read as three boxes turned 0 / 30 / 60 degrees about the cell axis (a 12-sided silhouette in 3 boxes instead
    of the block's 25). caps = which of up / down are open (ends of a trunk run); side faces always drawn."""
    w = width
    faces = ["north", "south", "east", "west"] + [c for c in ("up", "down") if c in caps]
    def uvs():
        return {f: {"uv": [0, 0], "uv_size": [rnd(min(w, 16) * SU), rnd(16 * SV if f not in ("up", "down") else min(w, 16) * SV)]}
                for f in faces}
    base = {"origin": [rnd(o[0] - w / 2), rnd(o[1]), rnd(o[2] - w / 2)], "size": [rnd(w), 16, rnd(w)]}
    if w >= 16:
        return [{**base, "uv": uvs()}]
    out = []
    for a in (0, 30, 60):
        c = {**base, "uv": uvs()}
        if a:
            c["pivot"] = [rnd(o[0]), rnd(o[1]), rnd(o[2])]
            c["rotation"] = [0, a, 0]
        out.append(c)
    return out


def shift_cube(c, off, uv_off=None, tex_of=None):
    """Copy a cube translated by off (and its pivot); remap face uvs into the atlas tile of its material instance."""
    n = {"origin": [rnd(c["origin"][i] + off[i]) for i in range(3)], "size": [rnd(v) for v in c["size"]]}
    if "pivot" in c:
        n["pivot"] = [rnd(c["pivot"][i] + off[i]) for i in range(3)]
    if "rotation" in c and any(c["rotation"]):
        n["rotation"] = [rnd(v) for v in c["rotation"]]
    uv = {}
    for face, f in c["uv"].items():
        tu, tv = (0, 0)
        if tex_of is not None:
            tu, tv = tile_uv(tex_of(f.get("material_instance", "*")))
        uv[face] = {"uv": [rnd(f["uv"][0] + tu), rnd(f["uv"][1] + tv)], "uv_size": [rnd(f["uv_size"][0]), rnd(f["uv_size"][1])]}
    n["uv"] = uv
    return n


# ------------------------------------------------------------------------------------------------ one template
def build(name, cells, root, sp_leaf, leaf_tab, leaf_geos, log_cubes, collar):
    occupied = {p for p, e in cells.items() if kind(e["name"])}
    bones = {}
    stats = {"wood": 0, "leaf": 0, "leaf_culled": 0, "cubes": 0}
    for p, e in sorted(cells.items()):
        k = kind(e["name"])
        if not k:
            continue
        t = (p[0] - root[0], p[1] - root[1], p[2] - root[2])
        layer = t[1]
        if layer < 0 or layer >= MAX_LAYERS:
            continue
        g = np.array([16.0 * t[0], 16.0 * t[1], -16.0 * t[2]])        # canonical file position of the cell bottom-centre
        if k == "wood":
            bname = f"w{layer}"
            b = bones.setdefault(bname, {"name": bname, "parent": "tturn", "pivot": [0, 0, 0], "cubes": []})
            caps = {f for f in ("up", "down") if tuple(p[i] + WORLD_FACE[f][i] for i in range(3)) not in occupied}
            b["cubes"].extend(wood_cubes(g, log_cubes.get(e["name"], 16), caps))
            stats["wood"] += 1
            continue
        if all(tuple(p[i] + d[i] for i in range(3)) in occupied for d in NEIGH):
            stats["leaf_culled"] += 1
            continue
        s = e["states"]
        ent = leaf_tab.get((int(s.get("pw:variant", 0)), int(s.get("pw:off", 0)))) or leaf_tab[(0, 0)]
        bone_rot = (180 - ent["theta"]) % 360
        kq = int(bone_rot // 90)
        bname = f"l{layer}_{kq}"
        b = bones.setdefault(bname, {"name": bname, "parent": "tturn", "pivot": [0, 0, 0], "rotation": [0, bone_rot, 0], "cubes": []})
        inner = ry(-bone_rot) @ g                                        # stored so that Ry(bone_rot)·inner = g
        tex = ent["tex"]
        tex_of = lambda mi, tex=tex: tex.get(mi, tex.get("*"))           # noqa: E731
        # which world sides of this cell are open (no leaf / wood neighbour): only those cube faces are drawn
        open_world = {f for f, d in WORLD_FACE.items() if tuple(p[i] + d[i] for i in range(3)) not in occupied}
        planes = 0
        for c in sorted(leaf_geos[ent["geo"]], key=lambda c: 0 if (c.get("rotation") or [0, 0, 0])[1] else 1):
            is_plane = 0 in [round(v, 6) for v in c["size"]]
            if is_plane:
                # cluster budget (size law): a leaf open on 2+ sides (the crown's edge and corners) keeps PLANES_MAX
                # vertical clusters, a leaf open on one side keeps one
                if planes >= (PLANES_MAX if len(open_world) >= 2 else min(1, PLANES_MAX)):
                    continue
                planes += 1
                b["cubes"].append(shift_cube(c, inner, tex_of=tex_of))
            else:
                if not open_world:
                    continue
                mi = next(iter(c["uv"].values())).get("material_instance", "*")
                b["cubes"].append({"origin": [rnd(c["origin"][i] + inner[i]) for i in range(3)], "size": [rnd(v) for v in c["size"]],
                                   "uv": list(tile_uv(tex_of(mi)))})
        stats["leaf"] += 1
    stats["cubes"] = sum(len(b["cubes"]) for b in bones.values())
    ys = [int(re.match(r"[wl](\d+)", n).group(1)) for n in bones]
    h = (max(ys) + 1) if ys else 1
    xs = [abs(c["origin"][0]) + 32 for b in bones.values() for c in b["cubes"]] or [16]
    zs = [abs(c["origin"][2]) + 32 for b in bones.values() for c in b["cubes"]] or [16]
    vb = math.ceil(2 * max(max(xs), max(zs)) / 16) + 2
    head = [{"name": "root", "pivot": [0, 0, 0]},
            {"name": "tlift", "parent": "root", "pivot": [0, 0, 0]},
            {"name": "tturn", "parent": "tlift", "pivot": [0, 0, 0]},
            {"name": "branch_l", "parent": "root", "pivot": [0, 0, 0]},        # the fall animation also drives these two
            {"name": "branch_r", "parent": "root", "pivot": [0, 0, 0]}]
    if collar:
        head.append({**collar, "parent": "root"})
    geo = {"format_version": "1.12.0", "minecraft:geometry": [{
        "description": {"identifier": f"geometry.ft_tpl.{name}", "texture_width": ATLAS_W, "texture_height": ATLAS_H,
                        "visible_bounds_width": vb, "visible_bounds_height": h * 2 + 4, "visible_bounds_offset": [0, h / 2, 0]},
        "bones": head + [bones[k] for k in sorted(bones, key=lambda n: (int(re.match(r'[wl](\d+)', n).group(1)), n))]}]}
    stats["layers"] = h
    return geo, stats


# ------------------------------------------------------------------------------------------------ textures
def tint_ratio(tex_dir, sp):
    """per-channel factor that turns the grey f0 into the species' pre-tinted *_fall picture (what the old entity showed)."""
    f0 = np.asarray(Image.open(tex_dir / f"{sp}_f0.png").convert("RGBA"), dtype=float)
    fall = np.asarray(Image.open(tex_dir / f"{sp}_fall.png").convert("RGBA"), dtype=float)
    m = (f0[..., 3] > 128) & (fall[..., 3] > 128)
    return np.clip(fall[m][:, :3].mean(0) / np.maximum(f0[m][:, :3].mean(0), 1), 0, 4)


def atlas(tex_dir, sp, out):
    ratio = tint_ratio(tex_dir, sp)
    TILE_PX = 16 * PX
    img = Image.new("RGBA", (ATLAS_W * PX, ATLAS_H * PX), (0, 0, 0, 0))
    for i, tn in enumerate(TILE_ORDER):
        p = tex_dir / f"{sp}_{tn}.png"
        if not p.exists():
            continue
        a = np.asarray(Image.open(p).convert("RGBA").resize((TILE_PX, TILE_PX), Image.LANCZOS), dtype=float)
        a[..., :3] = np.clip(a[..., :3] * ratio, 0, 255)
        tile = Image.fromarray(a.astype(np.uint8), "RGBA")
        u, v = tile_uv(tn)
        cells = [(0, 0), (16, 0), (32, 0), (48, 0), (0, 16), (16, 16), (32, 16), (48, 16)] if tn.startswith("f") else [(0, 0)]
        for du, dv in cells:                                  # every cell of the net carries the leaf (any face mapping is right)
            img.paste(tile, ((u + du) * PX, (v + dv) * PX))
    img.save(out, optimize=True)
    return [round(float(v), 3) for v in ratio]


# ------------------------------------------------------------------------------------------------ self-test of the turn law
def _selftest():
    """ry_turn = 90·r - yaw maps the canonical G(t) to the file position the entity at `yaw` needs for a template turned r."""
    def a_psi(w, psi):
        p = math.radians(psi)
        l = np.array([math.cos(p), 0, math.sin(p)])
        f = np.array([-math.sin(p), 0, math.cos(p)])
        return np.array([w @ l, w[1], -(w @ f)])

    def turn(t, r):
        dx, dy, dz = t
        return {0: (dx, dy, dz), 1: (-dz, dy, dx), 2: (-dx, dy, -dz), 3: (dz, dy, -dx)}[r]

    rng = np.random.default_rng(7)
    for r in range(4):
        for psi in (0, 37, 90, -135, 180, 271.5):
            for _ in range(5):
                t = rng.integers(-9, 9, 3).astype(float)
                g = np.array([t[0], t[1], -t[2]])
                want = a_psi(np.array(turn(t, r), dtype=float), psi)
                got = ry(90 * r - psi) @ g
                assert np.allclose(got, want, atol=1e-9), (r, psi, t, got, want)
    # leaf bone law: M = A0 · Ry_w(θ) · B == Ry(180 - θ)
    a0, b = np.diag([1, 1, -1]), np.diag([-1, 1, 1])
    for th in (0, 90, 180, 270):
        assert np.allclose(a0 @ ry(th) @ b, ry(180 - th), atol=1e-9), th
    return "turn law + leaf bone law: PASS"


def main():
    if "--selftest" in sys.argv:
        print(_selftest())
        return
    rp, bp = Path(sys.argv[1]), Path(sys.argv[2])
    stats_only = "--stats" in sys.argv
    print(_selftest())
    tex_dir = rp / "textures/blocks/pw_leaves2"
    leaf_geo_file = rp / "models/blocks/pw_leaves2.geo.json"
    leaf_geos = {gid: [c for b in load_geo(leaf_geo_file, gid)["bones"] for c in b.get("cubes", [])]
                 for gid in ("geometry.pw_leaves2_full", "geometry.pw_leaves2_cards", "geometry.pw_leaves2_spruce")}
    old = rp / "models/entity"
    old_geos = {}
    for f in old.glob("falling_tree_*.geo.json"):
        for g in json.loads(f.read_text())["minecraft:geometry"]:
            old_geos[g["description"]["identifier"]] = g
    # wood widths from the BLOCK models the template's wood actually uses (BP block -> geometry id -> RP model): the outer
    # face distance of the unrotated cubes (the dodecagon's core + its bark slab), so the copy matches the standing trunk
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
    log_cubes = {bid: min(16, model_w[gid]) for bid, gid in block_geo.items() if gid in model_w and model_w[gid] < 16}
    print("trunk widths (cubes):", {k: v for k, v in sorted(log_cubes.items()) if not k.endswith(("_root", "_stump"))})
    collar = next((dict(b) for b in old_geos["geometry.ft_falling_tree.oak_mature"]["bones"] if b["name"] == "break_collar"), None)
    if collar:
        collar.pop("parent", None)
    leaf_tabs = {sp: leaf_table(bp, sp) for sp in SPECIES_LEAF}
    out_geo = rp / "models/entity/ft_tpl"
    if not stats_only:
        out_geo.mkdir(parents=True, exist_ok=True)
        tints = {sp: atlas(tex_dir, sp, rp / f"textures/entity/fallingtree/leafatlas_{sp}.png") for sp in SPECIES_LEAF}
        print("atlases (tint ratios):", tints)
    index, total_bytes, worst = [], 0, None
    agg = {"wood": 0, "leaf": 0, "leaf_culled": 0, "cubes": 0}
    for p in sorted((bp / "structures/pw/trees").glob("*.mcstructure")):
        name = p.stem
        cells, root = decode(p)
        if not root:
            print("NO ROOT", name)
            continue
        leaf_names = {e["name"] for e in cells.values() if e["name"].endswith("_leaves")}
        sp_leaf = next(iter(leaf_names)).replace("pw:", "").replace("_leaves", "") if leaf_names else "oak"
        geo, st = build(name, cells, root, sp_leaf, leaf_tabs.get(sp_leaf, leaf_tabs["oak"]), leaf_geos, log_cubes, collar)
        txt = json.dumps(geo, separators=(",", ":"))
        total_bytes += len(txt)
        if not worst or len(txt) > worst[1]:
            worst = (name, len(txt), st)
        for k in agg:
            agg[k] += st[k]
        index.append({"name": name, "leaf": sp_leaf, "layers": st["layers"], "bytes": len(txt)})
        if not stats_only:
            (out_geo / f"{name}.geo.json").write_text(txt)
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "ft_tpl_index.json").write_text(json.dumps(index, indent=0))
    print(f"templates {len(index)} · wood cells {agg['wood']} · leaf cells {agg['leaf']} (+{agg['leaf_culled']} enclosed, left out)"
          f" · cubes {agg['cubes']} · geometry {total_bytes / 1e6:.1f} MB · largest {worst[0]} {worst[1] / 1e3:.0f} KB {worst[2]}")


if __name__ == "__main__":
    main()
