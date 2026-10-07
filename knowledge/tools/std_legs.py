#!/usr/bin/env python3
"""std_legs.py — give zero-thickness LEG sheets real thickness (his 12:41 "Yes" + 12:45 method).
A leg piece cube that is a vertical sheet (size 0 along x or z, height > 0) becomes a box:
  thickness t = the sheet's width, capped at 2 px (bird legs: square section); centred on the old sheet plane
  UV -> per-face: the two old visible faces keep their exact texels; the two NEW side faces repeat the FRONT face's
  texels ("bird legs tend to look the same on three sides" — his 12:45); up / down = the front face's top / bottom row.
The front face of a z-sheet is north (the mob's front); of an x-sheet, east.
Gate per cube: the old visible faces' texel rectangles are unchanged (exact), and the box-UV -> per-face conversion
reproduces every face rectangle of an untouched cube (round trip)."""
import copy
import json
import sys
from pathlib import Path

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
from bb_truth import face_uvs  # noqa: E402

LEG_TOKENS = ("hip", "thigh", "knee", "shin", "ankle", "leg", "legs", "thighs", "shins", "tarsus", "calf",
              # 14:25 10-01 P11 fix: AnF raptors keep the vertical tarsus sheet INSIDE foot_* (12 birds were missed);
              # only vertical sheets are thickened (sheet_axis), so flat toe plates on the ground stay as authored
              "foot", "feet", "toe", "toes", "claw", "claws", "talon", "talons")
FACES = ("north", "south", "east", "west", "up", "down")


def to_per_face(rects):
    """face_uvs rectangles (display convention) -> Bedrock per-face uv dict."""
    out = {}
    for f, (u1, v1, u2, v2) in rects.items():
        if f in ("up", "down"):
            out[f] = {"uv": [u2, v2], "uv_size": [u1 - u2, v1 - v2]}
        else:
            out[f] = {"uv": [u1, v1], "uv_size": [u2 - u1, v2 - v1]}
    return out


def is_leg(name):
    return name.split("_")[0] in LEG_TOKENS


def sheet_axis(c):
    s = [abs(x) for x in c["size"]]
    if s[1] <= 0:
        return None
    if s[0] == 0 and s[2] > 0:
        return 0
    if s[2] == 0 and s[0] > 0:
        return 2
    return None


def thicken(c, bone_mirror=False):
    """returns (new cube, report) or (None, None) when the cube is not a vertical sheet."""
    k = sheet_axis(c)
    if k is None or c.get("inflate"):
        return None, None
    mirror = bool(c.get("mirror", bone_mirror))
    s = list(c["size"])
    rects = face_uvs(c.get("uv", [0, 0]), s, mirror)
    other = 2 if k == 0 else 0
    t = min(abs(s[other]), 2.0)
    n = copy.deepcopy(c)
    n["origin"] = list(c["origin"])
    n["origin"][k] = c["origin"][k] - t / 2.0
    n["size"] = list(s)
    n["size"][k] = t
    if k == 2:
        front, back, sides = "north", "south", ("east", "west")
    else:
        front, back, sides = "east", "west", ("north", "south")
    fr = rects[front]
    new = {front: fr, back: rects[back]}
    for sd in sides:
        new[sd] = list(fr)
    u1, v1, u2, v2 = fr
    step = 1 if v2 >= v1 else -1
    new["up"] = [u2, v1 + step, u1, v1]           # the front face's top row (display convention for up / down)
    new["down"] = [u2, v2, u1, v2 - step]          # its bottom row
    n["uv"] = to_per_face(new)
    n.pop("mirror", None)                          # per-face UV carries any flip in its signed sizes
    # gate: the two visible faces keep their texels exactly
    after = face_uvs(n["uv"], n["size"], False)
    ok = all(after[f] == rects[f] for f in (front, back))
    return n, {"axis": "xyz"[k], "thickness": t, "front": front, "faces_kept": ok}


def round_trip_ok(c, bone_mirror=False):
    s = c["size"]
    rects = face_uvs(c.get("uv", [0, 0]), s, bool(c.get("mirror", bone_mirror)))
    return face_uvs(to_per_face(rects), s, False) == rects


def process_geo(geo):
    rows = []
    for b in geo["bones"]:
        if not is_leg(b["name"]) or not b.get("cubes"):
            continue
        for i, c in enumerate(b["cubes"]):
            if isinstance(c.get("uv"), dict):
                continue  # already per-face: not a box sheet we can read the layout of
            n, rep = thicken(c, bool(b.get("mirror", False)))
            if n is None:
                continue
            assert round_trip_ok(c, bool(b.get("mirror", False))), (b["name"], c)
            b["cubes"][i] = n
            rows.append({"bone": b["name"], **rep})
    return rows


def main(stage_root, out_md):
    lines = ["# LEG THICKNESS — zero-thickness leg sheets given real thickness (front texture repeated on the sides)", "",
             "| geometry | bone | sheet axis | thickness px | front face | visible faces kept |", "|---|---|---|---|---|---|"]
    total = bad = 0
    # birds only (his 12:41 / 12:45 ruling is about bird legs); other plans are decided separately
    import std_convert as S
    census = json.loads((ROOT / "_docs/standard/SKELETON-CENSUS.json").read_text())
    birds = {S.slug_of(c["id"]) for c in census if c["body_plan"] in ("bird",)}
    for f in sorted(Path(stage_root).glob("*/models/entity/std/*.geo.json")):
        if f.name.split(".geo.json")[0] not in birds:
            continue
        d = json.loads(f.read_text())
        changed = False
        for g in d["minecraft:geometry"]:
            for r in process_geo(g):
                changed = True
                total += 1
                bad += 0 if r["faces_kept"] else 1
                lines.append(f"| {g['description']['identifier']} | {r['bone']} | {r['axis']} | {r['thickness']} | "
                             f"{r['front']} | {'yes' if r['faces_kept'] else 'NO'} |")
        if changed:
            f.write_text(json.dumps(d, indent=1))
    lines += ["", f"**{total} leg sheets thickened; visible faces changed: {bad}.**"]
    Path(out_md).write_text("\n".join(lines) + "\n")
    print(total, "thickened;", bad, "with changed visible faces")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
