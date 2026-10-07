#!/usr/bin/env python3
"""visible_size.py — D-C284: how big a mob LOOKS, not how big its boxes are.

small_mob_census.py measured the rest bounding box of every cube, so invisible parts counted: fully transparent planes (a
Patrix tail card), parts a render controller only shows sometimes (saddles, chests, collars, the evoker's casting arms), the
April rigs' empty helper boxes. That made a cat "2.3 blocks long". This tool measures the VISIBLE model instead:
  * the entity's default geometry at rest, faces placed with bb_truth (the witnessed Bedrock face placement);
  * every face sampled on a 12 x 12 texel grid against the entity's default texture; only samples with alpha >= 0.5 (the
    alpha-test cut the game uses) count;
  * bones a render controller shows conditionally (part_visibility with anything but a literal true) are left out, with
    their subtrees;
  * x the client entity's scripts.scale (the adult value when it is a baby ternary).
API: measure(pack_root, stem, stack) -> {"h", "l", "w", "max"} in blocks (+ details)."""
import glob, re, sys
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from equine_compare import bone_affines
from bb_truth import truth_posed_faces

ROOT = Path("/home/claude")
VANILLA = ROOT / "_intake/bedrock-samples/resource_pack"
GRID = 12


def jl(p):
    return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))


def find_geometry(roots, ident):
    for root in roots:
        for f in glob.glob(str(Path(root) / "models/entity/**/*.json"), recursive=True):
            try: d = jl(f)
            except Exception: continue
            for g in d.get("minecraft:geometry", []) or []:
                if g["description"]["identifier"] == ident:
                    return g["bones"], g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
            for k, v in d.items():
                if k.split(":")[0] == ident and isinstance(v, dict):
                    return v.get("bones", []), v.get("texturewidth", 64), v.get("textureheight", 64)
    return None


def find_texture(roots, stem):
    for root in roots:
        for ext in (".png", ".tga"):
            p = Path(root) / (stem + ext)
            if p.exists(): return p
    return None


def render_controllers(roots):
    out = {}
    for root in reversed(list(roots)):              # higher packs override lower ones
        for f in glob.glob(str(Path(root) / "render_controllers/*.json")):
            try: out.update(jl(f).get("render_controllers", {}))
            except Exception: pass
    return out


def client_scale(desc):
    s = (desc.get("scripts") or {}).get("scale")
    if s is None: return 1.0
    if isinstance(s, (int, float)): return float(s)
    # D-C291: evaluate a single-level ternary in the everyday ADULT state (q.is_baby 0, q.life_time long past spawn) — the old
    # regex always took the ELSE branch, which is the adult value for 'q.is_baby ? b : a' but 0.0 for the Naturalist
    # 'q.life_time > 0.05 ? 1.0 : 0.0' pop-in guard (beetle / dragonfly / tree frog measured as 0 blocks)
    m0 = re.fullmatch(r"\s*(.+?)\?\s*([-\d.]+)f?\s*:\s*([-\d.]+)f?\s*", str(s))
    if m0:
        cond = re.sub(r"\b(q|query)\.life_time\b", "100", m0.group(1))
        cond = re.sub(r"\b(q|query|v|variable)\.[a-z_]+", "0", cond).replace("&&", " and ").replace("||", " or ")
        cond = cond.replace("!=", " __NE__ ").replace("!", " not ").replace(" __NE__ ", "!=")
        try: return float(m0.group(2)) if eval(cond) else float(m0.group(3))
        except Exception: pass
    m = re.search(r"\?\s*[-\d.]+f?\s*:\s*([-\d.]+)", str(s))
    if m: return float(m.group(1))
    try: return float(str(s).strip().rstrip("f"))
    except ValueError: return 1.0


def conditional_bones(desc, rcs):
    hidden = set()
    for rc in desc.get("render_controllers", []) or []:
        k = rc if isinstance(rc, str) else list(rc)[0]
        for pv in (rcs.get(k, {}).get("part_visibility") or []):
            for bone, expr in pv.items():
                if bone == "*": continue
                if not (expr is True or str(expr).strip().lower() in ("true", "1", "1.0")): hidden.add(bone.lower())
    return hidden


def everyday_value(expr):
    """D-C291: a part_visibility expression evaluated in the everyday state — every query / variable false or 0 (awake, not angry,
    not sheared, not tamed, not eating, adult)."""
    e = str(expr)
    e = re.sub(r"q\.property\([^)]*\)", "0", e)
    e = re.sub(r"\b(q|query|v|variable)\.[a-z_]+", "0", e)
    e = e.replace("&&", " and ").replace("||", " or ").replace("!=", " __NE__ ").replace("!", " not ").replace(" __NE__ ", "!=")
    try: return bool(eval(e))
    except Exception: return True


def everyday_rules(desc, roots):
    """[(bone-name glob, hidden?)] from every render controller's part_visibility, in order (later entries win)."""
    rcs = render_controllers(roots); out = []
    for rc in desc.get("render_controllers", []) or []:
        k = rc if isinstance(rc, str) else list(rc)[0]
        for pv in rcs.get(k, {}).get("part_visibility") or []:
            for pat, ex in pv.items(): out.append((pat.lower(), not everyday_value(ex)))
    return out


def measure(pack_root, stem, stack=(), geometry_key="default", texture_key=None, exclude=None, keep_conditional=False, everyday=False):
    """exclude: regex of bone names left out with their subtrees (tails: their rest pose is not the pose you see)."""
    roots = [Path(pack_root)] + [Path(s) for s in stack] + [VANILLA]
    desc = jl(Path(pack_root) / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
    gid = (desc.get("geometry") or {}).get(geometry_key)
    found = find_geometry(roots, gid)
    if not found: return None
    bones, tw, th = found
    tex_map = desc.get("textures") or {}
    tstem = tex_map.get(texture_key) if texture_key else (tex_map.get("default") or next(iter(tex_map.values()), None))
    tp = find_texture(roots, tstem) if tstem else None
    alpha = np.asarray(Image.open(tp).convert("RGBA"))[..., 3] if tp else None
    cond = set() if keep_conditional else conditional_bones(desc, render_controllers(roots))   # D-C291: state-dependent bodies (grizzly)
    if everyday:   # D-C291: part_visibility evaluated in the everyday state (every query false / 0) instead of dropping every conditional part
        import fnmatch
        rules = everyday_rules(desc, roots)
        names = [b["name"] for b in bones]
        cond = set()
        for n in names:
            vis = True
            for pat, hid in rules:
                if fnmatch.fnmatch(n.lower(), pat): vis = not hid
            if not vis: cond.add(n.lower())
    par = {b["name"]: b.get("parent") for b in bones}
    def hidden(n):
        while n:
            if n.lower() in cond or (exclude and re.search(exclude, n, re.I)): return True
            n = par.get(n)
        return False
    keep = [b for b in bones if not hidden(b["name"])]
    faces = truth_posed_faces(bones, tw, th, bone_affines(bones))
    keep_names = {b["name"] for b in keep}
    pts = []
    s = np.linspace(0.02, 0.98, GRID)
    for f in faces:
        if f.bone not in keep_names: continue
        P = np.array(f.pts, float)                       # TL, TR, BR, BL <-> (u0,v0), (u1,v0), (u1,v1), (u0,v1)
        u0, v0, u1, v1 = f.uv
        for a in s:
            for c in s:
                if alpha is not None:
                    h_, w_ = alpha.shape
                    x = int(np.clip((u0 + (u1 - u0) * a) * w_, 0, w_ - 1)); y = int(np.clip((v0 + (v1 - v0) * c) * h_, 0, h_ - 1))
                    if alpha[y, x] < 128: continue
                top = P[0] + (P[1] - P[0]) * a; bot = P[3] + (P[2] - P[3]) * a
                pts.append(top + (bot - top) * c)
    if not pts: return None
    Q = np.array(pts); lo, hi = Q.min(0), Q.max(0); ext = (hi - lo) / 16.0
    cs = client_scale(desc)
    w, h, l = [float(v) * cs for v in ext]
    return {"h": round(h, 3), "l": round(l, 3), "w": round(w, 3), "max": round(max(w, h, l), 3), "client_scale": cs,
            "geometry": gid, "texture": str(tp) if tp else None, "left_out": sorted(cond), "floor": round(float(lo[1]) / 16 * cs, 3)}


if __name__ == "__main__":
    pack = Path(sys.argv[1]); stack = [Path(x) for x in sys.argv[3:]]
    print(measure(pack, sys.argv[2], stack))
