#!/usr/bin/env python3
"""jem_convert.py — RESEARCH implementation of CONV-1: OptiFine JEM (invertAxis "xy") -> Bedrock geometry bones, with an
optional REST-POSE bake for Fresh-Animations-style JEMs whose animations assign tx/ty/tz/rx/ry/rz every frame.
(D-C255. Not a shipping tool yet — the tool proposal in MOB-CONVERSION-RESEARCH-2026-09-27 builds on this.)

Frames (all verified in r1_jem_vs_bedrock.py against Mojang's own vanilla pairs):
  BB  = the world frame Blockbench uses (x = the entity's RIGHT, y up, -z = front)
  JEM (invertAxis xy): top-level part `translate` = -pivot_BB (all three); its boxes are ABSOLUTE BB coordinates.
       submodel `translate` = +pivot_BB (absolute at depth 0, relative to the parent submodel from depth 1); its boxes are
       relative to its own pivot.  `rotate` = BB rotation (degrees).  sizeAdd = inflate.  mirrorTexture "u" = mirror.
  Bedrock file frame = BB with x mirrored: pivot_B = (-x, y, z); cube origin_B = (-(x + w), y, z); rotation_B = (-rx, -ry, +rz);
       face names are world-based so per-face uv keys copy across unchanged (uvNorth -> north, ...).
CEM animation variables (Ewan Howell's CEM Template Loader reference implementation, matched against our own
witness-accepted cow): rx/ry/rz are Java radians (BB rotation += (-rx, -ry, +rz) in degrees); tx/ty/tz are Java
rotation-point coordinates: root part -> pivot_BB = (-tx, 24 - ty, tz); depth-1 submodel -> (-tx, -ty, tz) absolute;
deeper -> (-tx, -ty, tz) relative to the parent pivot.  Boxes ride with their bone's pivot; unassigned children ride
with the parent.
"""
import json, math, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
from cem_eval import rest_pose

FACES = ("north", "east", "south", "west", "up", "down")


def load_json(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def face_uv(box):
    out = {}
    for f in FACES:
        v = box.get("uv" + f.capitalize())
        if v: out[f] = {"uv": [v[0], v[1]], "uv_size": [v[2] - v[0], v[3] - v[1]]}
    return out or None


def jem_tree(model):
    """Bones in the BB frame: [{name, parent, depth, pivot, rotation, mirror, inflate?, boxes:[{from,size,uv,inflate}], attach, scale}]"""
    bones = []

    def mk(name, parent, depth, pivot, rot, mirror, boxes, box_offset, extra):
        b = {"name": name, "parent": parent, "depth": depth, "pivot": list(pivot), "rotation": list(rot), "mirror": mirror, "boxes": [], **extra}
        for box in boxes or []:
            c = box.get("coordinates")
            if not c: continue
            b["boxes"].append({"from": [c[0] + box_offset[0], c[1] + box_offset[1], c[2] + box_offset[2]], "size": [c[3], c[4], c[5]],
                               "inflate": box.get("sizeAdd", 0) or 0, "uv": face_uv(box) or (list(box["textureOffset"]) if box.get("textureOffset") else None)})
        bones.append(b); return b

    for part in model.get("models", []):
        if not isinstance(part, dict): continue
        name = part.get("part") or part.get("id")
        t = part.get("translate", [0, 0, 0]); pivot = [-t[0], -t[1], -t[2]]
        top = mk(name, None, 0, pivot, part.get("rotate", [0, 0, 0]), "u" in (part.get("mirrorTexture") or ""), part.get("boxes"), [0, 0, 0],
                 {"attach": bool(part.get("attach")), "scale": part.get("scale", 1.0), "part": name})

        def sub(submodels, parent, depth, parent_pivot):
            for i, sm in enumerate(submodels or []):
                tr = list(sm.get("translate", [0, 0, 0]))
                if depth >= 1: tr = [tr[k] + parent_pivot[k] for k in range(3)]
                o = tr if "translate" in sm else (parent_pivot if depth >= 1 else [0, 0, 0])
                b = mk(sm.get("id") or f"{name}_sub_{i}", parent["name"], depth + 1, o, sm.get("rotate", [0, 0, 0]), "u" in (sm.get("mirrorTexture") or ""), sm.get("boxes"), o, {"part": name})
                sub(sm.get("submodels"), b, depth + 1, o)
        sub(part.get("submodels"), top, 0, pivot)
    return bones


def bake_rest(bones, jem, params=None):
    """Apply the animations' rest values (tx/ty/tz/rx/ry/rz) to the BB bones. Returns a new bone list + the ctx."""
    ctx, errors = rest_pose(jem, params)
    by = {b["name"]: b for b in bones}
    out = [dict(b, pivot=list(b["pivot"]), rotation=list(b["rotation"]), boxes=[dict(x, **{"from": list(x["from"])}) for x in b["boxes"]]) for b in bones]
    outby = {b["name"]: b for b in out}
    # process in depth order so parents move first
    for b in sorted(out, key=lambda b: b["depth"]):
        st = ctx.models.get(b["name"])
        assigned = set()
        for part in jem.get("models", []):
            for block in part.get("animations", []) or []:
                for k in block:
                    m, _, a = k.rpartition(".")
                    if m == b["name"] or (m == "this" and (part.get("part") or part.get("id")) == b["name"]): assigned.add(a)
        old_pivot = list(by[b["name"]]["pivot"])
        # parent motion (children ride with the parent unless they set their own absolute t*)
        par = outby.get(b["parent"]) if b["parent"] else None
        if par is not None:
            dp = [par["pivot"][k] - by[par["name"]]["pivot"][k] for k in range(3)]
        else: dp = [0, 0, 0]
        new_pivot = [old_pivot[k] + dp[k] for k in range(3)]
        if st and assigned & {"tx", "ty", "tz"}:
            tx, ty, tz = st["tx"], st["ty"], st["tz"]
            if b["depth"] == 0: abs_p = [-tx, 24 - ty, tz]
            elif b["depth"] == 1: abs_p = [-tx, -ty, tz]
            else:
                pp = outby[b["parent"]]["pivot"]; abs_p = [pp[0] - tx, pp[1] - ty, pp[2] + tz]
            for k, a in enumerate(("tx", "ty", "tz")):
                if a in assigned: new_pivot[k] = abs_p[k]
        b["pivot"] = new_pivot
        d = [new_pivot[k] - old_pivot[k] for k in range(3)]
        for x in b["boxes"]: x["from"] = [x["from"][k] + d[k] for k in range(3)]
        if st and assigned & {"rx", "ry", "rz"}:
            add = [-math.degrees(st["rx"]) if "rx" in assigned else 0, -math.degrees(st["ry"]) if "ry" in assigned else 0, math.degrees(st["rz"]) if "rz" in assigned else 0]
            b["rotation"] = [b["rotation"][k] + add[k] for k in range(3)]
    return out, ctx, errors


TPL = None
def vanilla_template(mob):
    """The vanilla Java model in JEM form (CEM Template Models v5.0.3) — gives each vanilla part's pivot + rest rotation."""
    global TPL
    if TPL is None:
        TPL = json.load(open("/home/claude/_intake/cem-templates/cem_template_models.json"))["models"]
    key = {"puffer_fish_big": "pufferfish_big", "puffer_fish_medium": "pufferfish_medium", "puffer_fish_small": "pufferfish_small"}.get(mob, mob)
    for k in (key, key.replace("_baby", ""), key.split("_")[0]):
        if k in TPL: return json.loads(TPL[k]["model"])
    return None


def bake_rest2(jem, mob, params=None, seeds=None):
    """CEM-RT model (D-C255): every top-level JEM part is a CHILD of the vanilla part of the same name.
    Bedrock bone per vanilla part V: pivot = the vanilla pivot (template translate -> -pivot), rotation = the vanilla rest
    rotation (template rotate), unless the JEM animation assigns <part>.r*/t* (REPLACE).  The custom part's boxes are
    absolute (its frame is the entity origin).  Submodels are child bones with pivot = translate (absolute at depth 0,
    relative deeper) and rotation = static rotate REPLACED by the animated value where assigned."""
    ctx, errors = rest_pose(jem, params, seeds=seeds)
    tpl = vanilla_template(mob)
    tparts = {}
    if tpl:
        for pt in tpl.get("models", []):
            if isinstance(pt, dict): tparts[pt.get("part") or pt.get("id")] = pt
    assigned = {}
    for part in jem.get("models", []):
        pname = part.get("part") or part.get("id")
        for block in part.get("animations", []) or []:
            for k in block:
                m, _, a = k.rpartition("."); m = pname if m in ("this", "part") else m.split(":")[-1]
                assigned.setdefault(m, set()).add(a)
    bones = []
    for part in jem.get("models", []):
        if not isinstance(part, dict): continue
        name = part.get("part") or part.get("id")
        tp = tparts.get(name)
        if tp is not None:
            tt = tp.get("translate", [0, 0, 0]); vpiv = [-tt[0], -tt[1], -tt[2]]; vrot = list(tp.get("rotate", [0, 0, 0]))
        else:
            t = part.get("translate", [0, 0, 0]); vpiv = [-t[0], -t[1], -t[2]]; vrot = [0, 0, 0]
        st = ctx.models.get(name); asg = assigned.get(name, set())
        if st:
            if asg & {"tx", "ty", "tz"}:
                ap = [-st["tx"], 24 - st["ty"], st["tz"]]
                for k, a in enumerate(("tx", "ty", "tz")):
                    if a in asg: vpiv[k] = ap[k]
            rep = [-math.degrees(st["rx"]), -math.degrees(st["ry"]), math.degrees(st["rz"])]
            for k, a in enumerate(("rx", "ry", "rz")):
                if a in asg: vrot[k] = rep[k]
        vb = {"name": name, "parent": None, "depth": 0, "pivot": vpiv, "rotation": vrot, "mirror": "u" in (part.get("mirrorTexture") or ""), "boxes": [], "part": name, "attach": bool(part.get("attach")), "scale": part.get("scale", 1.0)}
        for box in part.get("boxes", []) or []:
            c = box.get("coordinates")
            if c: vb["boxes"].append({"from": [c[0], c[1], c[2]], "size": [c[3], c[4], c[5]], "inflate": box.get("sizeAdd", 0) or 0, "uv": face_uv(box) or (list(box["textureOffset"]) if box.get("textureOffset") else None)})
        bones.append(vb)

        def sub(submodels, parent, depth, parent_pivot):
            for i, sm in enumerate(submodels or []):
                sid = sm.get("id") or f"{name}_sub_{i}"
                tr = list(sm.get("translate", [0, 0, 0]))
                if depth >= 1: tr = [tr[k] + parent_pivot[k] for k in range(3)]
                o = tr if "translate" in sm else (parent_pivot if depth >= 1 else [0, 0, 0])
                rot = list(sm.get("rotate", [0, 0, 0]))
                st = ctx.models.get(sid); asg = assigned.get(sid, set())
                if st:
                    if asg & {"tx", "ty", "tz"}:
                        if depth == 0: ap = [-st["tx"], -st["ty"], st["tz"]]
                        else: ap = [parent_pivot[0] - st["tx"], parent_pivot[1] - st["ty"], parent_pivot[2] + st["tz"]]
                        for k, a in enumerate(("tx", "ty", "tz")):
                            if a in asg: o[k] = ap[k]
                    rep = [-math.degrees(st["rx"]), -math.degrees(st["ry"]), math.degrees(st["rz"])]
                    for k, a in enumerate(("rx", "ry", "rz")):
                        if a in asg: rot[k] = rep[k]
                b = {"name": sid, "parent": parent["name"], "depth": depth + 1, "pivot": o, "rotation": rot, "mirror": "u" in (sm.get("mirrorTexture") or ""), "boxes": [], "part": name}
                for box in sm.get("boxes", []) or []:
                    c = box.get("coordinates")
                    if c: b["boxes"].append({"from": [c[0] + o[0], c[1] + o[1], c[2] + o[2]], "size": [c[3], c[4], c[5]], "inflate": box.get("sizeAdd", 0) or 0, "uv": face_uv(box) or (list(box["textureOffset"]) if box.get("textureOffset") else None)})
                bones.append(b)
                sub(sm.get("submodels"), b, depth + 1, o)
        sub(part.get("submodels"), vb, 0, vpiv)
    return bones, ctx, errors


def bedrock_uv(uv):
    """D-C278: per-face UV, JEM -> Bedrock. Blockbench imports a JEM face straight into its display uv [u1, v1, u2, v2]; its
    Bedrock codec writes N/E/S/W as uv [u1, v1] + size [u2-u1, v2-v1] but UP/DOWN turned 180 deg: uv [u2, v2] + size
    [u1-u2, v1-v2] (bedrock.js compileCube / parseCube). Before D-C278 every up/down face was copied literally, so the game
    drew it turned 180 deg (chicken/frog toes backwards, panda rump upside down, tropical-fish bottom fins off the belly)."""
    if not isinstance(uv, dict): return uv
    out = {}
    for k, f in uv.items():
        if k in ("up", "down") and isinstance(f, dict) and "uv_size" in f:
            (a, b), (w, h) = f["uv"], f["uv_size"]
            out[k] = {**f, "uv": [a + w, b + h], "uv_size": [-w, -h]}
        else:
            out[k] = f
    return out


def to_bedrock(bones):
    """BB bones -> Bedrock bones (file frame)."""
    out = []
    for b in bones:
        o = b["pivot"]
        nb = {"name": b["name"], "parent": b["parent"], "pivot": [-o[0], o[1], o[2]], "rotation": [-b["rotation"][0], -b["rotation"][1], b["rotation"][2]], "cubes": []}
        if b.get("mirror"): nb["mirror"] = True
        for x in b["boxes"]:
            f, s = x["from"], x["size"]
            c = {"origin": [-(f[0] + s[0]), f[1], f[2]], "size": list(s)}
            if x["inflate"]: c["inflate"] = x["inflate"]
            if x["uv"] is not None: c["uv"] = bedrock_uv(x["uv"])
            nb["cubes"].append(c)
        out.append(nb)
    return out


def convert(jem, rest=True, params=None, mob=None, mode=2):
    bones = jem_tree(jem)
    ctx = errors = None
    if rest and mode == 2 and mob: bones, ctx, errors = bake_rest2(jem, mob, params)
    elif rest: bones, ctx, errors = bake_rest(bones, jem, params)
    return to_bedrock(bones), ctx, errors


if __name__ == "__main__":
    jem = load_json(sys.argv[1])
    bones, ctx, errors = convert(jem, rest=("--static" not in sys.argv))
    for b in bones:
        if b["cubes"] or any(b["rotation"]): print(f"{b['name']:22s} parent={str(b['parent']):16s} pivot={[round(v, 2) for v in b['pivot']]} rot={[round(v, 1) for v in b['rotation']]} cubes={[([round(v, 2) for v in c['origin']], c['size']) for c in b['cubes']][:2]}")
    if errors: print("ERRORS", errors)
