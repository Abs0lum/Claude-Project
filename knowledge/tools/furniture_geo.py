#!/usr/bin/env python3
"""furniture_geo.py — the pw:furniture family, first medieval set (12 pieces), as Bedrock geometry boxes.

Units: cubes (1/16 block).  Block cell x 0..16, z 0..16, y 0..N (N up to 24 for the dresser).  The FRONT of every
piece is the -z side (z = 0): the block is placed with cardinal_direction + y_rotation_offset 180 (the roof family's
convention), so the front faces the placer.  Material instances: board (planks), post (stripped log side),
end (stripped log end grain), iron (fittings — pegs, handles, hoops).

Each box: dict(o=[x,y,z], s=[w,h,d], m="board", rot=[rx,ry,rz], piv=[px,py,pz], faces={"north":..} optional per-face
material override).  Boxes are authored so that every visible face carries the material the eye expects: planks
along boards, stripped-log round-stock for legs/posts/turned parts, end grain on cut ends.
"""

def B(o, s, m="board", rot=None, piv=None, faces=None):
    d = {"o": list(o), "s": list(s), "m": m}
    if rot: d["rot"] = list(rot); d["piv"] = list(piv) if piv else [o[0] + s[0] / 2, o[1] + s[1] / 2, o[2] + s[2] / 2]
    if faces: d["faces"] = faces
    return d

def legs(h, inset=1, t=2, m="post", xs=(0, 16), zs=(0, 16), into=1):
    """four corner posts; they run `into` cubes up INTO the plane they carry (h = the plane's underside), so no post
    end face is coplanar with the plane's underside — the round-1 previews showed exactly that clipping."""
    out = []
    for x in (xs[0] + inset, xs[1] - inset - t):
        for z in (zs[0] + inset, zs[1] - inset - t):
            out.append(B([x, 0, z], [t, h + into, t], m, faces={"up": "end", "down": "end"}))
    return out

PIECES = {}

# ---- seating / dining ------------------------------------------------------------------------------------------
PIECES["table"] = {"title": "table (dining, 1 cell — auto-joins)", "h": 14, "boxes":
    [B([0, 11.5, 0], [16, 2.5, 16], "board")] +                                            # top (2.5 thick, surface at 14)
    [B([2.5, 9, 1.5], [11, 3, 1]), B([2.5, 9, 13.5], [11, 3, 1]),                          # apron rails BETWEEN the legs, 0.5 behind
     B([1.5, 9, 2.5], [1, 3, 11]), B([13.5, 9, 2.5], [1, 3, 11])] +                         # the leg faces (r2: no shared planes, F01)
    legs(11.5, inset=1, t=2)}

PIECES["bench"] = {"title": "bench (trestle ends)", "h": 8, "boxes":
    [B([0, 5.5, 5], [16, 2.5, 6], "board"),                                                # seat (2.5 thick, surface at 8)
     B([1, 0, 6], [2, 6.5, 4], "board", faces={"up": "end"}), B([13, 0, 6], [2, 6.5, 4], "board", faces={"up": "end"}),   # slab ends, 1 into the seat
     B([3, 2, 7], [10, 2, 2], "board", faces={"east": "end", "west": "end"})]}             # stretcher

PIECES["stool"] = {"title": "stool", "h": 10, "boxes":
    [B([3, 7.5, 3], [10, 2.5, 10], "board")] +
    legs(7.5, inset=4, t=2) +
    [B([6, 3, 4], [4, 1, 1], "post"), B([6, 3, 11], [4, 1, 1], "post")]}                    # rungs

PIECES["chair"] = {"title": "chair (ladder-back; 4 legs, the rear pair continues as the back posts)", "h": 22, "boxes":
    [B([3, 7.5, 3], [10, 2.5, 10], "board"),                                               # seat 10x10, 2.5 thick, surface at 10
     B([3.5, 0, 3.5], [2, 8.5, 2], "post", faces={"up": "end", "down": "end"}), B([10.5, 0, 3.5], [2, 8.5, 2], "post", faces={"up": "end", "down": "end"}),     # front legs (0.5 inside the seat edge, 1 into the seat)
     B([3.5, 0, 10.5], [2, 22, 2], "post", faces={"up": "end", "down": "end"}), B([10.5, 0, 10.5], [2, 22, 2], "post", faces={"up": "end", "down": "end"}),    # rear legs = back posts, one box each
     B([5.5, 14, 11], [5, 2, 1], "board"), B([5.5, 19, 11], [5, 2, 1], "board"),           # slats between the posts
     B([4.5, 4, 3.75], [7, 1, 1.5], "post"), B([4.5, 4, 10.75], [7, 1, 1.5], "post")]}     # front + rear rungs

# ---- storage --------------------------------------------------------------------------------------------------
PIECES["shelf"] = {"title": "shelf (standing, open front)", "h": 16, "boxes":
    [B([0, 0, 3], [2, 16, 12], "board", faces={"up": "end"}), B([14, 0, 3], [2, 16, 12], "board", faces={"up": "end"}),
     B([2, 0, 3], [12, 1.5, 12]), B([2, 5, 3], [12, 1.5, 11]), B([2, 10, 3], [12, 1.5, 11]), B([2, 14.5, 3], [12, 1.5, 12]),
     B([2, 1.5, 14], [12, 13, 1])]}                                                        # back, between bottom and top (r2: no shared planes)

PIECES["wall_shelf"] = {"title": "wall shelf (on the +z wall; top at 8 = the r1 mantel height, ruling 19:46)", "h": 8, "boxes":
    [B([0, 6.5, 10], [16, 1.5, 6], "board"),
     B([1, 3, 11], [2, 4.5, 5], "post", faces={"down": "end"}), B([13, 3, 11], [2, 4.5, 5], "post", faces={"down": "end"})]}   # brackets 1 into the board

PIECES["cupboard"] = {"title": "cupboard (two doors)", "h": 16, "boxes":
    [B([0, 0, 3], [2, 16, 13], "board", faces={"up": "end"}), B([14, 0, 3], [2, 16, 13], "board", faces={"up": "end"}),
     B([2, 14.5, 3], [12, 1.5, 13]), B([2, 0, 3], [12, 1.5, 13]), B([2, 1.5, 15], [12, 13, 1]),
     B([2, 1.5, 2], [5.5, 13, 1]), B([8.5, 1.5, 2], [5.5, 13, 1]),                        # doors
     B([6.5, 7, 1], [1, 2, 1], "iron"), B([8.5, 7, 1], [1, 2, 1], "iron")]}               # handles

PIECES["dresser"] = {"title": "dresser (sideboard + plate rack, 1.5 blocks)", "h": 24, "boxes":
    [B([0, 0, 4], [2, 10, 12], "board"), B([14, 0, 4], [2, 10, 12], "board"), B([2, 0, 4], [12, 1, 12]), B([2, 1, 15], [12, 9, 1]),
     B([2, 1, 3], [5.5, 5, 1]), B([8.5, 1, 3], [5.5, 5, 1]),                              # doors
     B([2, 6.5, 3], [5.5, 3, 1]), B([8.5, 6.5, 3], [5.5, 3, 1]),                          # drawer fronts
     B([4.5, 7.5, 2], [1, 1, 1], "iron"), B([10.5, 7.5, 2], [1, 1, 1], "iron"), B([6.5, 3, 2], [1, 2, 1], "iron"), B([8.5, 3, 2], [1, 2, 1], "iron"),
     B([0, 10, 3], [16, 1.5, 13]),                                                         # counter top
     B([0, 11.5, 15], [16, 11, 1]), B([0, 11.5, 11], [1, 11, 4]), B([15, 11.5, 11], [1, 11, 4]),   # rack back + sides, up to the cornice
     B([1, 15, 11], [14, 1.5, 4]), B([1, 20, 11], [14, 1.5, 4]), B([0, 22.5, 10], [16, 1.5, 6])]}   # plate shelves + cornice

# ---- fittings -------------------------------------------------------------------------------------------------
PIECES["trestle"] = {"title": "trestle (A-frame table support)", "h": 14, "boxes":
    [B([0, 11.5, 7], [16, 2.5, 2], "board", faces={"east": "end", "west": "end"}),         # top rail (legs pivot 1 cube inside it)
     B([3, 0, 7], [2, 13, 2], "post", rot=[22, 0, 0], piv=[4, 13, 8]), B([3.5, 0, 7], [2, 13, 2], "post", rot=[-22, 0, 0], piv=[4.5, 13, 8]),
     B([11, 0, 7], [2, 13, 2], "post", rot=[22, 0, 0], piv=[12, 13, 8]), B([10.5, 0, 7], [2, 13, 2], "post", rot=[-22, 0, 0], piv=[11.5, 13, 8]),   # r2: pairs half-lapped 0.5
     B([2, 5, 7], [12, 1.5, 2], "board", faces={"east": "end", "west": "end"})]}           # stretcher

def octagon(cx, cz, y0, h, R, m, top_step=0.0, lift=0.0):
    """an octagonal prism from four bands through the centre (width across flats W, band thickness = side length).
    r2: the four bands overlap in the middle, so equal heights put four faces in one plane (z-fight). top_step lowers
    band k's top by k*top_step; lift raises band k by k*lift (both ends) — 0.1 cube keeps the planes apart."""
    import math
    W = 2 * R * math.cos(math.radians(22.5)); s = 2 * R * math.sin(math.radians(22.5))
    out = []
    for i, ang in enumerate((0, 45, 90, 135)):
        yk = y0 + i * lift; hk = h - i * top_step
        out.append(B([cx - W / 2, yk, cz - s / 2], [W, hk, s], m, rot=[0, ang, 0], piv=[cx, yk + hk / 2, cz], faces={"up": "end", "down": "end"}))
    return out

PIECES["barrel_seat"] = {"title": "barrel seat (octagonal cask)", "h": 10, "boxes":
    octagon(8, 8, 0, 10, 5.5, "board", top_step=0.1) + octagon(8, 8, 2, 1, 5.8, "iron", lift=0.1) + octagon(8, 8, 7, 1, 5.8, "iron", lift=0.1)}

PIECES["coat_pegs"] = {"title": "coat pegs (on the +z wall)", "h": 14, "boxes":
    [B([0, 11, 15], [16, 3, 1], "board"),
     B([3, 12, 12], [1, 1, 3.5], "post", rot=[15, 0, 0], piv=[3.5, 12.5, 15.5], faces={"north": "end"}),     # pegs run 0.5 into the board
     B([7.5, 12, 12], [1, 1, 3.5], "post", rot=[15, 0, 0], piv=[8, 12.5, 15.5], faces={"north": "end"}),
     B([12, 12, 12], [1, 1, 3.5], "post", rot=[15, 0, 0], piv=[12.5, 12.5, 15.5], faces={"north": "end"})]}

PIECES["mantel"] = {"title": "mantel (low in its cell: placed over the hearth, the corbels stand on the hearth top)", "h": 5, "boxes":
    [B([0, 2.5, 11], [16, 2.5, 5], "board"),                                               # shelf, top at 5 (ruling 19:46: board down 3 cubes from 8)
     B([1, 0, 14], [2, 3.5, 2], "post", faces={"down": "end"}), B([13, 0, 14], [2, 3.5, 2], "post", faces={"down": "end"}),     # corbels 2x2 (ruling 19:46), inset 1 from the ends, 1 into the shelf
     B([0, 1.5, 10], [16, 1, 1], "board")]}                                                # nosing

ORDER = ["table", "bench", "stool", "chair", "shelf", "wall_shelf", "cupboard", "dresser", "trestle", "barrel_seat", "coat_pegs", "mantel"]

def to_bedrock_geometry(name, piece, ident_prefix="geometry.pw_furn_"):
    """Bedrock 1.16.0 block geometry with per-face material instances (uv from the box projection, 16 = one block)."""
    cubes = []
    for b in piece["boxes"]:
        o, s = b["o"], b["s"]; m = b["m"]; f = b.get("faces", {})
        uv = {}
        for face in ("north", "south", "east", "west", "up", "down"):
            inst = f.get(face, m)
            if face in ("north", "south"): u, v, w, h = o[0], 16 - o[1] - s[1], s[0], s[1]
            elif face in ("east", "west"): u, v, w, h = o[2], 16 - o[1] - s[1], s[2], s[1]
            else: u, v, w, h = o[0], o[2], s[0], s[2]
            uv[face] = {"uv": [u % 16, v % 16], "uv_size": [w, h], "material_instance": inst}
        c = {"origin": [o[0] - 8, o[1], o[2] - 8], "size": s, "uv": uv}
        if "rot" in b: c["rotation"] = b["rot"]; c["pivot"] = [b["piv"][0] - 8, b["piv"][1], b["piv"][2] - 8]
        cubes.append(c)
    return {"description": {"identifier": ident_prefix + name, "texture_width": 16, "texture_height": 16, "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0, 0.75, 0]},
            "bones": [{"name": "piece", "pivot": [0, 0, 0], "cubes": cubes}]}

if __name__ == "__main__":
    import json
    doc = {"format_version": "1.16.0", "minecraft:geometry": [to_bedrock_geometry(n, PIECES[n]) for n in ORDER]}
    print(json.dumps(doc)[:400]); print(sum(len(PIECES[n]["boxes"]) for n in ORDER), "boxes")
