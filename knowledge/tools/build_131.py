#!/usr/bin/env python3
"""build_131.py — RP-04 v1.3.130 -> v1.3.131 (geometry only; BP-02 .182 and RP-02 .3 unchanged).

Witness 2026-09-22 13:16 (Abs0lum, 7/7 frames):
  1. the hearth has no east/west walls -> add them: 2 cubes thick, outer = the block's material, inner = soot (like the
     chute), front ends = material, tops = the material's top key; the floor's outer faces become the material too.
  2. the flue's x-walls show the interior texture outside and vice versa while the z-walls are right ->
     L-XFACE (witnessed): in custom block geometry the per-face uv key "east" renders on the -x face and "west" on
     the +x face (Bedrock's x-mirrored model space); north/south/up/down are unaffected.  Fix: swap the two.
  3. the fire is too small -> lit flame quads 17 x 16 (y 2..18, corners at the inner wall planes), embers 14 x 9.
"""
import json, re, shutil, sys, datetime
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from homestead_build import box, face, geo, flue_cap_geometry   # noqa: E402

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/rp04-130", ROOT / "_build/rp04-131"
VER = "1.3.131"; DATE = "2026-09-22"
LOG = ROOT / "_logs/phase_log.md"
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD 131 — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

# L-XFACE: the key that renders on the OUTER face of an x-wall
#   low-x wall (x -8..-6): outer face is -x  -> key "east" ; inner (+x) -> "west"
#   high-x wall (x 6..8):  outer face is +x  -> key "west" ; inner (-x) -> "east"
def x_wall(low, y0, y1, z0, z1, outer_inst=None, inner_inst="soot", front=True, back=False, top_inst="top"):
    t = 2
    o = [-8, y0, z0] if low else [8 - t, y0, z0]
    faces = {}
    outer_key, inner_key = ("east", "west") if low else ("west", "east")
    faces[outer_key] = face(z1 - z0, y1 - y0, outer_inst)
    faces[inner_key] = face(z1 - z0, y1 - y0, inner_inst)
    if front: faces["north"] = face(t, y1 - y0, outer_inst)
    if back: faces["south"] = face(t, y1 - y0, outer_inst)
    faces["up"] = face(t, z1 - z0, top_inst)
    if y0 == 0: faces["down"] = face(t, z1 - z0, top_inst)
    return box(o, [t, y1 - y0, z1 - z0], faces)

def hearth_geometry_v2(phase):
    """skin (back wall, 2 cubes) · side walls (2 cubes, L-XFACE) · floor · bed · logs · flames."""
    skin = box([-8, 0, 6], [16, 16, 2], {
        "north": face(16, 16, "soot"), "south": face(16, 16), "east": face(2, 16), "west": face(2, 16),
        "up": face(16, 2, "top"), "down": face(16, 2, "top")})
    # side walls sit on the floor (y 1..16) so no face is coplanar with the floor's outer faces
    walls = [x_wall(True, 1, 16, -8, 6), x_wall(False, 1, 16, -8, 6)]
    floor = box([-8, 0, -8], [16, 1, 14], {
        "up": face(16, 14, "soot"), "north": face(16, 1), "east": face(14, 1), "west": face(14, 1),
        "down": face(16, 14, "top")})
    bed = box([-6, 1, -5], [12, 1, 8], {
        "up": face(12, 8, "bed"), "north": face(12, 1, "bed"), "south": face(12, 1, "bed"), "east": face(8, 1, "bed"), "west": face(8, 1, "bed")})
    bones = [("skin", [skin]), ("walls", walls), ("floor", [floor]), ("bed", [bed])]
    if phase in ("fueled", "lit", "embers"):
        logs = []
        for z0 in (-4.5, -0.5):
            logs.append(box([-6, 2, z0], [12, 3, 3], {
                "north": face(12, 3, "log"), "south": face(12, 3, "log"), "up": face(12, 3, "log"), "down": face(12, 3, "log"),
                "east": face(3, 3, "log_end", 6, 6), "west": face(3, 3, "log_end", 6, 6)}))
        for x0 in (-4.5, -0.5):
            logs.append(box([x0, 5, -7], [3, 3, 12], {
                "east": face(12, 3, "log"), "west": face(12, 3, "log"), "up": face(3, 12, "log"), "down": face(3, 12, "log"),
                "north": face(3, 3, "log_end", 6, 6), "south": face(3, 3, "log_end", 6, 6)}))
        bones.append(("logs", logs))
    if phase in ("lit", "embers"):
        # lit: the fire is the primary element — 17 wide (corners at the inner wall planes x = +-6), y 2..18
        # embers: low licks over the coals — 14 x 9, y 3..12
        w, h, y0 = (17.0, 16.0, 2.0) if phase == "lit" else (14.0, 9.0, 3.0)
        flames = []
        for rot in ([0, 45, 0], [0, -45, 0]):
            flames.append(box([-w / 2, y0, -1], [w, h, 0], {"north": face(16, 16, "flame"), "south": face(16, 16, "flame")},
                              pivot=[0, y0, -1], rotation=rot, inflate=0.01))
        bones.append(("flames", flames))
    return geo(f"geometry.pw_hearth_{phase}", bones, vis=(1.5, 2.0, [0, 1.0, 0]))

def hollow_walls_v2(t=2):
    n = box([-8, 0, -8], [16, 16, t], {"north": face(16, 16), "south": face(16, 16, "soot"), "east": face(t, 16), "west": face(t, 16), "up": face(16, t, "top"), "down": face(16, t, "top")})
    s = box([-8, 0, 8 - t], [16, 16, t], {"south": face(16, 16), "north": face(16, 16, "soot"), "east": face(t, 16), "west": face(t, 16), "up": face(16, t, "top"), "down": face(16, t, "top")})
    # L-XFACE: the low-x wall's outer (-x) face is the "east" key, the high-x wall's outer (+x) face is the "west" key
    w = box([-8, 0, -8 + t], [t, 16, 16 - 2 * t], {"east": face(16, 16), "west": face(16, 16, "soot"), "up": face(t, 16, "top"), "down": face(t, 16, "top")})
    e = box([8 - t, 0, -8 + t], [t, 16, 16 - 2 * t], {"west": face(16, 16), "east": face(16, 16, "soot"), "up": face(t, 16, "top"), "down": face(t, 16, "top")})
    return [n, s, w, e]

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    p = DST / "models/blocks/pw_homestead.geo.json"; doc = jload(p)
    keep = [g for g in doc["minecraft:geometry"] if not (g["description"]["identifier"].startswith("geometry.pw_hearth_") or g["description"]["identifier"] in ("geometry.pw_flue_hollow", "geometry.pw_flue_cap_hollow"))]
    cap_src = flue_cap_geometry(); rim = [b for b in cap_src["bones"] if b["name"] == "rim"][0]["cubes"]
    new = [hearth_geometry_v2(ph) for ph in ("cold", "fueled", "lit", "embers")]
    new.append(geo("geometry.pw_flue_hollow", [("walls", hollow_walls_v2())]))
    new.append(geo("geometry.pw_flue_cap_hollow", [("walls", hollow_walls_v2()), ("rim", rim)], vis=(1.5, 1.5, [0, 0.75, 0])))
    doc["minecraft:geometry"] = keep + new
    jdump(doc, p)
    man = jload(DST / "manifest.json")
    man["header"]["name"] = f"AbsolutRealism Basic RP v{VER}"
    man["header"]["description"] = (f"v{VER} ({DATE}) HEARTH WALLS + BIG FIRE + L-XFACE. Witness 13:16: (1) hearth side walls added (2 cubes, outer = material, "
        f"inner = soot, front ends material, tops = top key; floor outer faces material); (2) flue/cap x-walls: per-face uv 'east' renders on the -x "
        f"face and 'west' on the +x face in Bedrock block geometry (x-mirrored model space, north/south/up/down unaffected) — the two keys swapped so "
        f"the material is outside and the soot inside; (3) lit flame quads 17x16 (y 2..18, corners at the inner wall planes), embers 14x9. "
        f"Geometry file only; every other file byte-identical to v1.3.130. Pair with BP-02 v1.3.182 + RP-02 v2.0.3.")
    man["header"]["version"] = [1, 3, 131]
    for m in man["modules"]: m["version"] = [1, 3, 131]
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; t = led.read_text(encoding="utf-8"); t2 = t.replace("v1.3.130 ·", f"v{VER} ·", 1); assert t2 != t; led.write_text(t2, encoding="utf-8")
    log("tree rp04-131 built: hearth geometries (walls, big flame), flue hollow + cap (L-XFACE swap), manifest + ledger stamped")

if __name__ == "__main__":
    main()
