#!/usr/bin/env python3
"""road_kit.py — the CIVITAS ROAD KIT from Abs0lum's own StreetKit pieces (his 17:37 / 18:01 rulings, D-C529/D-C530).

Inputs  (his files): _intake/structures-2026-10-02/pw_road_st13_{straight_3,straight_3_access,ramp_7,cross_13,dead_13}.mcstructure
        + the ELBOW piece cut from his proving-ground world copy (_intake/oldworld-1003/A, box x -40..-28 y 177..191 z -68..-56)
Outputs (_docs/road_kit/, copied into BP-02 structures/pw/road/ by the BP build):
  town width (7 road, his blueprint):   t_straight1  t_access3  t_ramp7  t_cross13  t_dead13  t_elbow13  t_tee13
  village width (5 road, R3 = a):       v_straight1  v_access3  v_ramp7  v_cross13  v_dead13  v_elbow13  v_tee13
  every piece keeps his substructure byte-for-byte below the surface (y < 13); only the surface (y >= 13) of the village
  pieces is remapped: verge (grass) | sidewalk 2 | curb | road 5 | curb | sidewalk 2 | verge. So widening a village street
  to a town street = placing the town piece over it (nothing below changes).
Native orientation of every piece (file coordinates): travel along x, width along z (0..12). Openings:
  straight/access/ramp: x faces · cross: all four · dead: -z face only · elbow: -z and +x · tee: -z, +z and +x (-x closed)
  ramp: climbs ONE block from x0 (sidewalk block y14) to x6 (y15); its file is 16 tall.
Snow (his proving ground is snowy) is stripped: snow_layer -> air, pw:snow -> 0.
Usage: road_kit.py [--render]"""
import pickle
import sys
from pathlib import Path

sys.path.insert(0, "/home/claude/tools")
import mcstructure as M  # noqa: E402

IN = Path("/home/claude/_intake/structures-2026-10-02")
WORLD_A = Path("/home/claude/_intake/oldworld-1003/A_blocks.pkl")
OUT = Path("/home/claude/_docs/road_kit")
ELBOW_BOX = (-40, 177, -68, -28, 191, -56)
SURFACE_Y = 13                       # y >= 13 is the street surface (road block row y13, sidewalk/curb row y14, ramp y15)
V = None                             # the verge marker in the village width map
# village column -> town column (width axis); V = verge (grass at sidewalk level)
VMAP = [V, 0, 1, 2, 3, 4, 6, 8, 9, 10, 11, 12, V]
GRASSABLE = {"minecraft:smooth_stone": "minecraft:grass_block", "minecraft:stone_brick_stairs": "minecraft:grass_block"}   # a curb in a verge cell (the dead end's corner curbs) is verge too


def load(name):
    return M.Structure.from_bytes((IN / f"pw_road_st13_{name}.mcstructure").read_bytes())


def strip_snow(st):
    """snow_layer cells -> air; every pw:snow state -> 0 (same tag type)."""
    air = st._pal("minecraft:air", {})
    remap = {}
    for k, (n, states, ver) in enumerate(list(st.palette)):
        if n == "minecraft:snow_layer":
            remap[k] = air
        elif "pw:snow" in states:
            ns = dict(states)
            ns["pw:snow"] = M.Tag(states["pw:snow"].type, 0)
            remap[k] = st._pal(n, ns, ver)
    st.layer0 = [remap.get(v, v) for v in st.layer0]
    return st


def copy_box(src, x0, x1, keep_y=None):
    """a new Structure of src's x slices x0..x1 (inclusive)."""
    sx, sy, sz = src.size
    out = M.Structure((x1 - x0 + 1, sy, sz))
    for x in range(x0, x1 + 1):
        for y in range(sy):
            for z in range(sz):
                p = src.get(x, y, z)
                if p:
                    out.set(x - x0, y, z, p[0], p[1])
    return out


def clone(src):
    return copy_box(src, 0, src.size[0] - 1)


def typed_states(states):
    """world_cut gives plain values; the engine wants typed tags: *_bit / bool -> byte, int -> int, str -> string."""
    out = {}
    for k, v in states.items():
        if isinstance(v, bool) or k.endswith("_bit"):
            out[k] = M.b(int(v))
        elif isinstance(v, int):
            out[k] = M.i(v)
        else:
            out[k] = M.s(v)
    return out


def elbow_from_world():
    blocks = pickle.load(open(WORLD_A, "rb"))
    x0, y0, z0, x1, y1, z1 = ELBOW_BOX
    st = M.Structure((x1 - x0 + 1, y1 - y0 + 1, z1 - z0 + 1))
    for x in range(x0, x1 + 1):
        for y in range(y0, y1 + 1):
            for z in range(z0, z1 + 1):
                v = blocks.get((x, y, z))
                name, states = v if v else ("air", {})
                if ":" not in name:
                    name = "minecraft:" + name
                st.set(x - x0, y - y0, z - z0, name, typed_states(states))
    return st


def tee_from(cross, dead):
    """T junction: the cross with its -x arm closed by the dead end's closed rows (x0..2, every y)."""
    t = clone(cross)
    sx, sy, sz = cross.size
    for x in range(3):
        for y in range(sy):
            for z in range(sz):
                p = dead.get(x, y, z)
                if p:
                    t.set(x, y, z, p[0], p[1])
    return t


def face_open(st, face):
    """is the street open (road block at the middle of the face) on this face? face in -x +x -z +z."""
    sx, sy, sz = st.size
    cell = {"-x": (0, sz // 2), "+x": (sx - 1, sz // 2), "-z": (sx // 2, 0), "+z": (sx // 2, sz - 1)}[face]
    p = st.get(cell[0], SURFACE_Y, cell[1])
    return bool(p) and (p[0] == "minecraft:cobblestone" or p[0].startswith("pw:ramp_cobble"))


def villageify(st, two_d):
    """the village width surface: remap y >= 13 along z (and along x for 13 x 13 pieces); verge cells turn sidewalk
    stone into grass. A verge row on an OPEN face stays the street's own profile (only its corner cells are verge)."""
    sx, sy, sz = st.size
    out = clone(st)
    xo = {f: face_open(st, f) for f in ("-x", "+x")}
    zo = {f: face_open(st, f) for f in ("-z", "+z")}
    for x in range(sx):
        for z in range(sz):
            vz = VMAP[z]
            tz = 0 if (vz is V and z == 0) else 12 if vz is V else vz
            if two_d:
                vx = VMAP[x]
                tx = 0 if (vx is V and x == 0) else 12 if vx is V else vx
            else:
                vx, tx = 0, x
            x_verge = two_d and vx is V
            z_verge = vz is V
            # grass: a verge on a CLOSED face is a whole verge row; on an open face only where the other axis is verge too
            grass = False
            if z_verge and (not zo["-z" if z == 0 else "+z"] or (two_d and x_verge) or not two_d):
                grass = True
            if two_d and x_verge and (not xo["-x" if x == 0 else "+x"] or z_verge):
                grass = True
            for y in range(SURFACE_Y, sy):
                p = st.get(tx, y, tz)
                if p is None:
                    out.layer0[out.index(x, y, z)] = -1
                    continue
                name, states = p[0], p[1]
                if grass and name in GRASSABLE:
                    name, states = GRASSABLE[name], {}
                out.set(x, y, z, name, states)
    return out


def write(st, name):
    OUT.mkdir(parents=True, exist_ok=True)
    st.origin = (0, 0, 0)
    (OUT / f"{name}.mcstructure").write_bytes(st.to_bytes())
    return name


def surface_text(st, y_rows=(13, 14, 15)):
    """a top-down text view of the surface rows (x rows, z columns), highest non-air block at y >= 13."""
    sx, sy, sz = st.size
    ab = {"minecraft:cobblestone": "c", "minecraft:smooth_stone": "s", "minecraft:stone_brick_stairs": "t", "minecraft:grass_block": "g",
          "minecraft:dirt": "d", "minecraft:stone_bricks": "B", "minecraft:smooth_stone_slab": "_", "minecraft:stone_brick_slab": "-"}
    rows = []
    for x in range(sx):
        r = ""
        for z in range(sz):
            ch = " "
            for y in range(sy - 1, SURFACE_Y - 1, -1):
                p = st.get(x, y, z)
                if p and p[0] != "minecraft:air":
                    ch = ab.get(p[0], "r" if "ramp" in p[0] else "?")
                    break
            r += ch
        rows.append(f"x{x:2d} {r}")
    return "\n".join(rows)


def main():
    straight3 = strip_snow(load("straight_3"))
    access3 = strip_snow(load("straight_3_access"))
    ramp7 = strip_snow(load("ramp_7"))
    cross13 = strip_snow(load("cross_13"))
    dead13 = strip_snow(load("dead_13"))
    elbow13 = strip_snow(elbow_from_world())
    tee13 = tee_from(cross13, dead13)
    town = {"straight1": copy_box(straight3, 0, 0), "access3": access3, "ramp7": ramp7, "cross13": cross13,
            "dead13": dead13, "elbow13": elbow13, "tee13": tee13}
    report = []
    for k, st in town.items():
        write(st, f"t_{k}")
        vill = villageify(st, two_d=st.size[0] == 13)
        write(vill, f"v_{k}")
        report.append(f"== t_{k} {st.size}  open: " + " ".join(f for f in ("-x", "+x", "-z", "+z") if face_open(st, f)))
        report.append(surface_text(st))
        report.append(f"== v_{k}")
        report.append(surface_text(vill))
    (OUT / "KIT-SURFACES.txt").write_text("\n".join(report) + "\n")
    print("\n".join(report))


if __name__ == "__main__":
    main()
