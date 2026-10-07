#!/usr/bin/env python3
"""menagerie_sheets.py — D-C349: the per-animal COMPARISON SHEETS (his 20:10 CT 09-30: "a test for which version of each mob I want").

For every COMPARE group in _logs/menagerie_census.json: each distinct version (one per source pack + geometry; sub-species that share a
model show once, with their count) rendered as shipped — the add-on's own geometry file + its default skin, no animation (rest pose) —
from the front-left three-quarter and the side, with a label: source · entity key · skin px · cubes / bones · animations. Our own
StripMine (sf_nba) version, when we have one, is the first row ("OURS NOW").
Output: _docs/menagerie/compare/<NNN>-<animal>.png + _docs/menagerie/compare/INDEX.md; failures listed (never silently dropped)."""
import io, json, re, sys, zipfile, traceback
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML
from equine_compare import bone_affines
from bb_truth import truth_posed_faces
from entity_tex_render import render_entity
from convb_preview3 import camera, FOV

ROOT = Path("/home/claude"); D = ROOT / "_intake/addons-0930"; OUT = ROOT / "_docs/menagerie/compare"; TMP = Path("/tmp/menag_tex")
PACKS = {"AnF": "Animals-and-Fauna.mcaddon", "IFS": "Immersive-Fauna-Savanna-1_5_0.mcaddon", "WA": "World-Animals-Add-on.mcaddon",
         "JP": "jurassic-project-kingdom-of-the-giants.mcaddon", "WS": "wildlife-sanctuary-mobs-plus.mcaddon", "WWA": "wwa-animals-r.mcpack",
         "YSav": "ycreatures-savanna-v1_0_5.mcaddon", "YTri": "ycreaturestrial-rp-v2_0_4.mcpack", "OURS": None}
OURS_RP = [ROOT / "_build/rp07-1431", ROOT / "_build/rp08-148", ROOT / "_build/rp06-1424"]          # where the sf_nba creatures are drawn today (RP-07 1.4.31 + RP-08 1.4.8)
W, H = 330, 270
FALLBACK = []
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 13)
FR = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 11)
COL = {"OURS": (40, 95, 55), "AnF": (90, 60, 120), "WA": (30, 80, 140), "WS": (120, 80, 30), "WWA": (140, 60, 60), "IFS": (60, 110, 110),
       "YSav": (150, 110, 20), "YTri": (100, 100, 100), "JP": (60, 60, 60)}


def members(data, prefix=""):
    try: z = zipfile.ZipFile(io.BytesIO(data))
    except Exception: return
    for i in z.infolist():
        if i.filename.lower().endswith((".mcpack", ".zip", ".mcaddon")): yield from members(z.read(i), prefix + i.filename + "!")
        elif not i.is_dir(): yield prefix + i.filename, z.read(i)


def parse(b):
    try: return ML._parse_json(b.decode("utf-8-sig", "replace"))
    except Exception: return None


class Pack:
    """every client entity, geometry and skin of one add-on archive"""
    def __init__(self, path):
        if isinstance(path, list):                                       # our own build dirs
            self.files = {f"{d.name}/{p.relative_to(d)}": p.read_bytes() for d in path for p in d.rglob("*") if p.is_file()}
        else:
            self.files = dict(members(path.read_bytes()))
        self.geos, self.ents = {}, {}
        for n, b in self.files.items():
            if not n.endswith(".json"): continue
            d = parse(b)
            if not isinstance(d, dict): continue
            for g in d.get("minecraft:geometry", []) or []:
                desc = g.get("description", {})
                self.geos[desc.get("identifier")] = (g.get("bones", []) or [], desc.get("texture_width", 64), desc.get("texture_height", 64))
            for k, v in d.items():
                if k.startswith("geometry.") and isinstance(v, dict):
                    self.geos[k.split(":")[0]] = (v.get("bones", []) or [], v.get("texturewidth", 64), v.get("textureheight", 64))
            if "minecraft:client_entity" in d:
                desc = d["minecraft:client_entity"].get("description", {})
                self.ents[desc.get("identifier")] = desc
        self.tex = {}
        for n in self.files:
            if n.lower().endswith((".png", ".tga")):
                inner = n.split("!")[-1]
                m = re.search(r"(textures/.*)\.(png|tga)$", inner, re.I)
                if m: self.tex[m.group(1).lower()] = n

    def skin(self, t):
        t = re.sub(r"\.(png|tga)$", "", t.lower())                      # some entities name the file with its extension
        n = self.tex.get(t) or next((v for k, v in self.tex.items() if k.endswith(t.split("textures/")[-1])), None)
        return n

    def model(self, ident):
        desc = self.ents.get(ident)
        if not desc: return None, "client entity not found"
        geos = desc.get("geometry") or {}; texs = desc.get("textures") or {}
        gk = "default" if "default" in geos else next(iter(geos), None)
        tk = "default" if "default" in texs else next(iter(texs), None)
        if not gk or geos[gk] not in self.geos: return None, f"geometry {geos.get(gk) if gk else None} not found"
        if not tk: return None, "no texture"
        sn = self.skin(texs[tk]); data = self.files.get(sn) if sn else None
        if not data:
            for o in (FALLBACK or []):                                   # WS ships no skins: the same SkinsArt files live in WWA
                n2 = o.skin(texs[tk])
                if n2: data = o.files[n2]; break
        if not data: return None, f"skin {texs[tk]} not found"
        bones, tw, th = self.geos[geos[gk]]
        return (geos[gk], bones, tw, th, data), None


def render_one(bones, tw, th, skin_bytes, key):
    TMP.mkdir(exist_ok=True)
    p = TMP / f"{re.sub(r'[^a-z0-9_]', '_', key.lower())}.png"
    Image.open(io.BytesIO(skin_bytes)).convert("RGBA").save(p)
    bones = [dict(b) for b in bones]; seen = set()               # duplicate bone names (WWA whale: a 2nd 'body' parented to 'body'): the
    for b in bones:                                               # game keeps the first; here the copy is renamed so the parent chain ends
        if b.get("name") in seen: b["name"] = b["name"] + "_dup"
        seen.add(b.get("name"))
    faces = truth_posed_faces(bones, tw, th, bone_affines(bones))
    if not faces: raise ValueError("no cubes")
    out = []
    for v in ("front-east", "east"):
        e, t = camera(faces, v); fl = min(0.0, min(q[1] for x in faces for q in x.pts))
        out.append(render_entity(faces, p, e, t, W, H, fov=FOV, floor_y=fl).convert("RGB"))
    return out


def label(src, key, extra, sub):
    im = Image.new("RGB", (2 * W + 4, 36), COL.get(src, (80, 80, 80))); d = ImageDraw.Draw(im)
    d.text((6, 3), f"{'OURS NOW (StripMine)' if src == 'OURS' else src} · {key}{extra}", fill=(255, 255, 255), font=FB)
    d.text((6, 20), sub, fill=(230, 232, 240), font=FR)
    return im


def main(only=None):
    cen = json.loads((ROOT / "_logs/menagerie_census.json").read_text())
    OUT.mkdir(parents=True, exist_ok=True)
    packs = {s: Pack(D / f) for s, f in PACKS.items() if f}
    packs["OURS"] = Pack(OURS_RP)
    global FALLBACK; FALLBACK = [packs["WWA"], packs["WA"]]
    index, fails, manifest = [], [], []
    groups = sorted(cen["compare"].items(), key=lambda kv: (kv[1]["kind"], kv[0]))
    for n, (g, rec) in enumerate(groups, 1):
        if only and g not in only: continue
        rows = []
        cands = [{"src": "OURS", "key": i.split(":")[1], "id": i, "px": None, "cubes": None, "bones": None, "anims": []} for i in rec["ours"]] + rec["candidates"]
        seen = {}
        for c in cands:
            pk = packs.get(c["src"])
            try:
                m, why = pk.model(c["id"])
                if m is None: fails.append(f"{g}: {c['src']} {c['key']} — {why}"); continue
                gid = m[0]
                if (c["src"], gid) in seen: seen[(c["src"], gid)]["also"].append(c["key"]); continue
                ims = render_one(m[1], m[2], m[3], m[4], f"{c['src']}_{c['key']}")
                skin_px = Image.open(io.BytesIO(m[4])).size[0]
                ncubes = sum(len(b.get("cubes", []) or []) for b in m[1])
                seen[(c["src"], gid)] = {"c": c, "ims": ims, "also": [], "px": skin_px, "cubes": ncubes, "bones": len(m[1])}
            except Exception as e:
                fails.append(f"{g}: {c['src']} {c['key']} — {type(e).__name__} {str(e)[:80]}")
        if not seen: continue
        for v in seen.values():
            c = v["c"]; extra = f"  (+{len(v['also'])} sharing this model: {', '.join(v['also'][:4])}{'…' if len(v['also']) > 4 else ''})" if v["also"] else ""
            sub = f"skin {v['px']} px · {v['cubes']} cubes / {v['bones']} bones · {', '.join(c.get('anims', [])[:6]) or '—'}"
            row = Image.new("RGB", (2 * W + 4, H + 36), (255, 255, 255))
            row.paste(label(c["src"], c["key"], extra, sub), (0, 0)); row.paste(v["ims"][0], (0, 36)); row.paste(v["ims"][1], (W + 4, 36))
            rows.append(row)
        cols = 2 if len(rows) > 3 else 1
        rw, rh = rows[0].width, rows[0].height
        nr = (len(rows) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (rw + 8), 40 + nr * (rh + 8)), (255, 255, 255))
        d = ImageDraw.Draw(sheet)
        d.text((8, 8), f"{n:03d} {g.upper().replace('_', ' ')} — {len(rows)} version{'s' if len(rows) != 1 else ''} "
                       f"({'2+ add-ons' if rec['kind'] == 'A' else 'one add-on vs ours'}) · rest pose, default skin", fill=(20, 20, 20), font=FB)
        for i, r in enumerate(rows): sheet.paste(r, ((i % cols) * (rw + 8), 40 + (i // cols) * (rh + 8)))
        name = f"{n:03d}-{g}.png"; sheet.save(OUT / name)
        manifest.append({"n": n, "group": g, "kind": rec["kind"], "sheet": name, "versions": [
            {"src": v["c"]["src"], "key": v["c"]["key"], "id": v["c"]["id"], "px": v["px"], "cubes": v["cubes"], "bones": v["bones"],
             "anims": v["c"].get("anims", [])[:8], "also": v["also"]} for v in seen.values()]})
        index.append(f"| {n:03d} | {g} | {rec['kind']} | {len(rows)} | {', '.join(sorted({v['c']['src'] for v in seen.values()}))} | {name} |")
        print(name, len(rows), flush=True)
    L = ["# Comparison sheets — one per animal (D-C349)", "", "A = 2+ add-on versions · B = one add-on version vs our StripMine one. "
         "Rest pose, default skin, front-left three-quarter + side. `tools/menagerie_sheets.py`.", "",
         "| # | Animal | Kind | Versions | Sources | Sheet |", "|---|---|---|---|---|---|"] + index
    L += ["", f"## Not rendered ({len(fails)})", ""] + [f"- {f}" for f in fails]
    (OUT / "INDEX.md").write_text("\n".join(L) + "\n")
    if not only: (ROOT / "_logs/menagerie_sheets.json").write_text(json.dumps({"sheets": manifest, "not_rendered": fails}, indent=1))
    print(len(index), "sheets;", len(fails), "not rendered")


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
