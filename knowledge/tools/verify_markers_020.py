#!/usr/bin/env python3
"""verify_markers_020.py — gate for PW-Civitas Markers BP/RP v0.2.1 (entity markers + ladder hatch lid probe).
Static checks, the mock-run of pw_markers.js (tools/markers_src/test_markers.mjs against mock_server.mjs), a face-level
same-plane check on the entity geometry, render sheet, packaging."""
import json, re, sys, hashlib, zipfile, subprocess, shutil, tempfile, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, "/home/claude/tools")
import furniture_render as FR, furniture_geo as FG, build_markers_020 as BM
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); A, B = ROOT / "_build/markers-0.1.9", ROOT / "_build/markers-0.2.1"
DATE = "2026-09-22"; SCR = Path("/tmp/claude-0/-home-claude/c0a4a7ef-9c52-560d-ac77-bcf688f4b3d2/scratchpad")
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
res = []
def check(n, ok, d=""): res.append((n, bool(ok))); print(("PASS " if ok else "FAIL ") + n + ("" if ok else f"  -> {str(d)[:400]}"))

BPn, RPn = B / "BP", B / "RP"
NEW_JSON = [BPn / "entities/pw_marker.json", BPn / "entities/pw_hatch_lid.json", BPn / "items/pw_hatch_lid.json", BPn / "manifest.json",
            RPn / "entity/pw_marker.entity.json", RPn / "entity/pw_hatch_lid.entity.json", RPn / "models/entity/pw_markers.geo.json",
            RPn / "render_controllers/pw_markers.render.json", RPn / "textures/item_texture.json", RPn / "texts/languages.json", RPn / "manifest.json"]
bad = []
for p in NEW_JSON:
    try: load(p)
    except Exception as e: bad.append((str(p.relative_to(B)), str(e)[:80]))
check(f"A {len(NEW_JSON)} new/changed JSON files parse", not bad, bad)
# ---- B the frozen icon table: JS == builder
js = (BPn / "scripts/pw_markers.js").read_text(encoding="utf-8")
node = subprocess.run(["node", "--input-type=module", "-e",
    "const s=require('fs')" if False else
    f"import fs from 'node:fs'; const t=fs.readFileSync('{BPn / 'scripts/pw_markers.js'}','utf8'); const g=(n)=>JSON.parse(t.match(new RegExp('export const '+n+' = (\\\\[[^\\\\]]*\\\\]);'))[1]); console.log(JSON.stringify([g('ZONES'),g('STATIONS'),g('PORTS')]));"],
    capture_output=True, text=True)
try: zj, sj, pj = json.loads(node.stdout)
except Exception: zj = sj = pj = None
check("B icon table in pw_markers.js == builder (12 zones, 18 stations, 4 ports, datum = 35; order frozen)", (zj, sj, pj) == (BM.ZONES, BM.STATIONS, BM.PORTS) and len(BM.ICONS) == 35, (node.stderr[:200], zj))
blocks = sorted(p.stem for p in (BPn / "blocks").glob("*.json"))
want_blocks = sorted([("pw_datum" if f == "datum" else f"pw_{f}_{k}") for f, k in BM.ICONS])
check("B every icon has its (still registered) marker block + terrain icon", set(want_blocks) <= set(blocks) and all((RPn / f"textures/blocks/{b}.png").exists() for b in want_blocks), sorted(set(want_blocks) - set(blocks)))
# ---- C BP entities
mk, lid = load(BPn / "entities/pw_marker.json")["minecraft:entity"], load(BPn / "entities/pw_hatch_lid.json")["minecraft:entity"]
cbad = []
for name, ent in (("marker", mk), ("lid", lid)):
    groups = set(ent.get("component_groups", {}))
    def refs(ev):
        out = []
        for part in ([ev] + ev.get("first_valid", []) + ev.get("sequence", [])):
            for k in ("add", "remove"): out += part.get(k, {}).get("component_groups", [])
        return out
    for en, ev in ent["events"].items():
        for g in refs(ev):
            if g not in groups: cbad.append((name, en, "group", g))
        for part in ([ev] + ev.get("first_valid", [])):
            for pk in part.get("set_property", {}):
                if pk not in ent["description"]["properties"]: cbad.append((name, en, "property", pk))
    for comp in ("minecraft:physics", "minecraft:pushable", "minecraft:damage_sensor", "minecraft:persistent", "minecraft:body_rotation_blocked", "minecraft:collision_box"):
        if comp not in ent["components"]: cbad.append((name, "missing", comp))
    if ent["description"].get("is_spawnable") is not False or ent["description"].get("is_summonable") is not True: cbad.append((name, "spawnable/summonable"))
check("C BP entities: events reference existing groups/properties; inert set (no gravity/push/damage, persistent, body rotation blocked); not spawnable, summonable", not cbad, cbad)
fv = lid["events"]["pw:toggle"]["first_valid"]
check("C lid: closed group = is_collidable only; toggle = first_valid [open if pw:open != true, else close]; spawn event adds closed; interact -> pw:toggle",
      lid["component_groups"]["pw:lid_closed"] == {"minecraft:is_collidable": {}} and len(fv) == 2 and fv[0]["filters"] == {"test": "bool_property", "domain": "pw:open", "operator": "!="}
      and fv[0]["set_property"] == {"pw:open": True} and fv[1]["set_property"] == {"pw:open": False} and lid["events"]["minecraft:entity_spawned"]["add"]["component_groups"] == ["pw:lid_closed"]
      and lid["components"]["minecraft:interact"]["interactions"][0]["on_interact"]["event"] == "pw:toggle"
      and lid["components"]["minecraft:collision_box"] == {"width": 1.0, "height": 0.1875})
check("C marker: collision box 0 x 0 (never refuses a block placement); hit box = custom_hit_test in pw:hittable, added at spawn and by show, removed by hide; hide/show set pw:vis",
      mk["components"]["minecraft:collision_box"] == {"width": 0.0, "height": 0.0} and "minecraft:custom_hit_test" in mk["component_groups"]["pw:hittable"]
      and mk["events"]["minecraft:entity_spawned"]["add"]["component_groups"] == ["pw:hittable"] and mk["events"]["pw:hide"]["remove"]["component_groups"] == ["pw:hittable"]
      and mk["events"]["pw:show"]["add"]["component_groups"] == ["pw:hittable"] and mk["events"]["pw:hide"]["set_property"] == {"pw:vis": False} and mk["events"]["pw:show"]["set_property"] == {"pw:vis": True})
item = load(BPn / "items/pw_hatch_lid.json")["minecraft:item"]; itex = load(RPn / "textures/item_texture.json")["texture_data"]
check("C item pw:hatch_lid: icon key resolves to a file", item["components"]["minecraft:icon"]["textures"]["default"] in itex and (RPn / (itex["pw_hatch_lid"]["textures"] + ".png")).exists())
# ---- D RP wiring
geo = {g["description"]["identifier"]: g for g in load(RPn / "models/entity/pw_markers.geo.json")["minecraft:geometry"]}
rcs = load(RPn / "render_controllers/pw_markers.render.json")["render_controllers"]
dbad = []
for cf in ("pw_marker.entity.json", "pw_hatch_lid.entity.json"):
    d = load(RPn / "entity" / cf)["minecraft:client_entity"]["description"]
    for k, t in d["textures"].items():
        if not (RPn / (t + ".png")).exists(): dbad.append((cf, "texture", k, t))
    for gid in d["geometry"].values():
        if gid not in geo: dbad.append((cf, "geometry", gid))
    bones = {b["name"] for gid in d["geometry"].values() if gid in geo for b in geo[gid]["bones"]}
    bp = mk if "marker" in cf else lid; props = set(bp["description"]["properties"])
    for rc in d["render_controllers"]:
        if rc not in rcs: dbad.append((cf, "controller", rc)); continue
        c = rcs[rc]
        for pv in c.get("part_visibility", []):
            for bone, expr in pv.items():
                if bone != "*" and bone not in bones: dbad.append((cf, rc, "bone", bone))
                if isinstance(expr, str):
                    for pr in re.findall(r"query\.property\('([^']+)'\)", expr):
                        if pr not in props: dbad.append((cf, rc, "property", pr))
        for arr in c.get("arrays", {}).get("textures", {}).values():
            for tname in arr:
                if tname.split(".", 1)[1] not in d["textures"]: dbad.append((cf, rc, "array texture", tname))
        for texpr in c["textures"]:
            for pr in re.findall(r"query\.property\('([^']+)'\)", texpr):
                if pr not in props: dbad.append((cf, rc, "texture property", pr))
check("D RP: every client texture resolves; geometry ids exist; controllers exist; part_visibility bones exist; molang properties are declared in the BP", not dbad, dbad[:6])
rc_icon = rcs["controller.render.pw_marker_icon"]["arrays"]["textures"]["Array.icons"]; rc_num = rcs["controller.render.pw_marker_num"]["arrays"]["textures"]["Array.nums"]
tex_m = load(RPn / "entity/pw_marker.entity.json")["minecraft:client_entity"]["description"]["textures"]
order_ok = all(tex_m[f"icon_{i}"].endswith("/" + ("pw_datum" if f == "datum" else f"pw_{f}_{k}")) for i, (f, k) in enumerate(BM.ICONS))
check("D icon array = the frozen table order (35) and number array 0..63 (64)", len(rc_icon) == 35 and len(rc_num) == 64 and order_ok)
lang = (RPn / "texts/en_US.lang").read_text(encoding="utf-8")
check("D lang: item + interact text + 35 marker block names", "item.pw:hatch_lid.name=" in lang and "action.interact.pw_hatch=" in lang and all(f"tile.{('pw:datum' if f == 'datum' else f'pw:{f}_{k}')}.name=" in lang for f, k in BM.ICONS))
# ---- E scripts
for f in ("pw_markers.js", "main.js"):
    r = subprocess.run(["node", "--check", str(BPn / "scripts" / f)], capture_output=True, text=True); check(f"E {f} syntax (node --check)", r.returncode == 0, r.stderr[:200])
m = (BPn / "scripts/main.js").read_text(encoding="utf-8")
check("E main.js imports pw_markers.js once; the v0.1.x zone/station BLOCK listeners are gone; manhole hatch + frame listener intact",
      m.count('import "./pw_markers.js"') == 1 and 'id.startsWith("pw:zone_")' not in m and 'id.startsWith("pw:station_")' not in m
      and 'registerCustomComponent("pw:hatch"' in m and "FRAME LISTENER v2" in m and "civ:frame" in m)
imports = set(re.findall(r"import \{([^}]*)\} from \"@minecraft/server\"", js)[0].replace(" ", "").split(","))
typings = (SCR / "mcs/package/index.d.ts").read_text(encoding="utf-8")
missing = [n for n in imports if not re.search(rf"export (declare )?(class|enum|const) {n}\b", typings)]
check("E every @minecraft/server import in pw_markers.js exists in the 2.0.0 typings", not missing, missing)
api = ["playerInteractWithBlock", "entityHitEntity", "dataDrivenEntityTrigger", "entityLoad", "entitySpawn", "playerPlaceBlock", "playerBreakBlock", "scriptEventReceive",
       "getEntitiesAtBlockLocation", "spawnEntity", "setProperty", "getProperty", "triggerEvent", "setRotation", "getBlocks", "getBlockLocationIterator", "heightRange",
       "isSneaking", "selectedSlotIndex", "getGameMode", "setDynamicProperty", "getDynamicProperty", "addTag", "playSound", "spawnItem", "setActionBar", "isFirstEvent", "blockFace"]
used_missing = [a for a in api if a in js and a not in typings]
check(f"E every engine member the script touches ({len([a for a in api if a in js])}) exists in the 2.0.0 typings (no beta-only calls such as Block.isSolid)", not used_missing and "isSolid" not in js, used_missing)
with tempfile.TemporaryDirectory() as td:
    td = Path(td); mod = td / "node_modules/@minecraft/server"; mod.mkdir(parents=True)
    shutil.copy(ROOT / "tools/markers_src/mock_server.mjs", mod / "index.mjs")
    (mod / "package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.mjs","exports":"./index.mjs"}')
    (td / "package.json").write_text('{"type":"module"}')
    shutil.copy(BPn / "scripts/pw_markers.js", td / "pw_markers.js"); shutil.copy(ROOT / "tools/markers_src/test_markers.mjs", td / "test_markers.mjs")
    r = subprocess.run(["node", "test_markers.mjs", str(BPn)], cwd=td, capture_output=True, text=True)
    mm = re.search(r"MOCK OK (\d+)", r.stdout)
    check(f"E mock-run (stub server applying the BP's own data-driven events): {mm.group(1) if mm else '?'} assertions — placement intercept, sneak = own cell, numbering, rings, fallback, survival consume, hide/show, hit-remove, migrate, list/check/remove, lid place/refuse/hinge x4/toggle/turn/flip/remove/ladder-break, entityLoad",
          r.returncode == 0 and mm and int(mm.group(1)) >= 50, (r.stdout + r.stderr)[-500:])
# ---- F diff hygiene
def th(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
for sub, want_changed, want_added in (
        ("BP", {"scripts/main.js", "manifest.json", "PW-DEPENDENCIES.md"}, {"scripts/pw_markers.js", "entities/pw_marker.json", "entities/pw_hatch_lid.json", "items/pw_hatch_lid.json"}),
        ("RP", {"manifest.json", "PW-DEPENDENCIES.md"}, {"entity/pw_marker.entity.json", "entity/pw_hatch_lid.entity.json", "models/entity/pw_markers.geo.json", "render_controllers/pw_markers.render.json",
                                                         "textures/entity/pw_hatch_lid.png", "textures/items/pw_hatch_lid.png", "textures/item_texture.json", "texts/en_US.lang", "texts/languages.json"})):
    h0, h1 = th(A / sub), th(B / sub); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}; added = set(h1) - set(h0); removed = set(h0) - set(h1)
    check(f"F {sub} diff vs 0.1.9 (0.2.1): changed {sorted(ch)}, +{len(added)} files, nothing removed (all 38 marker/frame/hatch blocks byte-identical)", ch == want_changed and added == want_added and not removed, (sorted(ch), sorted(added), sorted(removed)))
for sub in ("BP", "RP"):
    a, b = load(A / sub / "manifest.json")["header"], load(B / sub / "manifest.json")["header"]
    check(f"F {sub} manifest v0.2.1 + stamp, uuid unchanged", b["version"] == [0, 2, 1] and b["description"].startswith(f"v0.2.1 ({DATE})") and a["uuid"] == b["uuid"])
# ---- G same-plane faces inside each visibility set of the entity geometry (L-COPLANAR-1 at face level)
def faces_of(cube_):
    o, s = cube_["origin"], cube_["size"]; x0, y0, z0 = o; x1, y1, z1 = x0 + s[0], y0 + s[1], z0 + s[2]
    planes = {"west": (0, x0, (y0, y1, z0, z1)), "east": (0, x1, (y0, y1, z0, z1)), "down": (1, y0, (x0, x1, z0, z1)), "up": (1, y1, (x0, x1, z0, z1)),
              "north": (2, z0, (x0, x1, y0, y1)), "south": (2, z1, (x0, x1, y0, y1))}
    return [(k,) + planes[k] for k in cube_["uv"]]
def overlap(a, b): return max(0, min(a[1], b[1]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[2], b[2]))
def same_plane(bones):
    fs = [(bn, f) for bn in bones for c in bones[bn] for f in faces_of(c)]; hits = []
    for i in range(len(fs)):
        for j in range(i + 1, len(fs)):
            (b1, (k1, ax1, v1, r1)), (b2, (k2, ax2, v2, r2)) = fs[i], fs[j]
            if k1 == k2 and ax1 == ax2 and abs(v1 - v2) < 1e-6 and overlap(r1, r2) > 0.01: hits.append((b1, k1, b2))
    return hits
gm = {b["name"]: b["cubes"] for b in geo["geometry.pw_marker_entity"]["bones"]}; gl = {b["name"]: b["cubes"] for b in geo["geometry.pw_hatch_lid"]["bones"]}
sets = [{"zone_top": gm["zone_top"], "zone_sides": gm["zone_sides"]}, {"station": gm["station"]}, {"port": gm["port"]}, {"closed": gl["closed"]}] + [{b: gl[b]} for b in ("leaf_pz", "leaf_px", "leaf_nz", "leaf_nx")]
gh = [h for s_ in sets for h in same_plane(s_)]
check("G no same-plane same-facing faces within any set of bones shown together (zone icon + number share one box on DISJOINT faces)", not gh, gh[:4])
leaf_ok = gl["leaf_pz"][0]["origin"][2] + gl["leaf_pz"][0]["size"][2] == 8 and gl["leaf_nz"][0]["origin"][2] == -8 and gl["leaf_px"][0]["origin"][0] + gl["leaf_px"][0]["size"][0] == 8 and gl["leaf_nx"][0]["origin"][0] == -8
leaf_span = all(c["origin"][1] == -13 and c["origin"][1] + c["size"][1] == 3 for b in ("leaf_pz", "leaf_px", "leaf_nz", "leaf_nx") for c in gl[b])
check("G lid: closed plate y 0..3 (= cell y 0.8125..1.0, top flush with the floor above); each open leaf 3 thick against its cell edge, spanning the whole cell (y -13..3)",
      gl["closed"][0]["origin"] == [-8, 0, -8] and gl["closed"][0]["size"] == [16, 3, 16] and leaf_ok and leaf_span)

# ---- H render sheet (model space is left-handed: world = (x, y, -z) about the entity origin)
BIG = SCR / "mk_tex"; BIG.mkdir(exist_ok=True)
def reg(stem_, path, scale):
    im = Image.open(path).convert("RGBA"); im = im.resize((im.width * scale, im.height * scale), Image.NEAREST) if scale > 1 else im
    out = BIG / f"{stem_}.png"; im.save(out); FR.EXTRA_TEX[stem_] = str(out); FR._tex.pop(stem_, None); return stem_
reg("m_lid", RPn / "textures/entity/pw_hatch_lid.png", 1); reg("m_ladder", ROOT / "_build/rp03-59/textures/blocks/ladder.png", 1)
reg("m_floor", ROOT / "_build/rp04-138/textures/blocks/oak_planks_v0.png", 1)
FR_ORDER = {"north": (["a", "b", "c", "d"], lambda p: (p[0], -p[1])), "south": (["f", "e", "h", "g"], lambda p: (-p[0], -p[1])),
            "west": (["e", "a", "d", "h"], lambda p: (p[2], -p[1])), "east": (["b", "f", "g", "c"], lambda p: (-p[2], -p[1])),
            "up": (["d", "c", "g", "h"], lambda p: (p[0], p[2])), "down": (["e", "f", "b", "a"], lambda p: (p[0], -p[2]))}
def ent_faces(cubes, stem_of_face, origin):
    """entity cubes -> renderer faces in WORLD cubes: mirror z (left-handed model space), offset by the entity origin; each face shows its full uv window"""
    out = []
    for c in cubes:
        o, s = c["origin"], c["size"]; x0, y0, z0 = o; x1, y1, z1 = x0 + s[0], y0 + s[1], z0 + s[2]
        P = {"a": [x0, y0, z0], "b": [x1, y0, z0], "c": [x1, y1, z0], "d": [x0, y1, z0], "e": [x0, y0, z1], "f": [x1, y0, z1], "g": [x1, y1, z1], "h": [x0, y1, z1]}
        for name, win in c["uv"].items():
            keys, uvf = FR_ORDER[name]; U = [uvf(P[k]) for k in keys]
            us, vs = [u for u, _ in U], [v for _, v in U]
            (u0, v0), (w, h) = win["uv"], win["uv_size"]
            uvs = [(u0 + w * ((u - min(us)) / ((max(us) - min(us)) or 1)), v0 + h * ((v - min(vs)) / ((max(vs) - min(vs)) or 1))) for u, v in U]
            pts = [[P[k][0] + origin[0], P[k][1] + origin[1], -P[k][2] + origin[2]] for k in keys]
            wname = {"north": "south", "south": "north"}.get(name, name)
            pts, uvs = pts[::-1], uvs[::-1]                                      # the mirror flips the winding: restore outward order
            for sp, su in FR.subdivide(pts, uvs, 8): out.append((wname, stem_of_face(name), sp, su))
    return out
def cube_faces(o, s, stem_, faces=("north", "south", "east", "west", "up", "down")):
    b = {"o": o, "s": s, "m": "x"}; return [f for f in FR.box_faces(b, {"x": stem_}) if f[0] in faces]
def floor_ring():
    out = []
    for cx in (-16, 0, 16):
        for cz in (-16, 0, 16):
            if cx == 0 and cz == 0: continue
            out += cube_faces([cx, 0, cz], [16, 16, 16], "m_floor", ("up", "north", "south", "east", "west"))
    return out
def ladder(hinge):   # the ladder hangs on the wall OPPOSITE the hinge; drawn as a 1-cube slab carrying the ladder texture
    side = (hinge + 2) % 4
    box = {0: ([0, -16, 0], [16, 32, 1]), 1: ([15, -16, 0], [1, 32, 16]), 2: ([0, -16, 15], [16, 32, 1]), 3: ([0, -16, 0], [1, 32, 16])}[side]
    face = {0: "south", 1: "west", 2: "north", 3: "east"}[side]
    return cube_faces(box[0], box[1], "m_ladder", (face,))
def lid_scene(hinge, opened):
    bone = BM.HINGE_BONE[hinge] if opened else "closed"
    return floor_ring() + ladder(hinge) + ent_faces(gl[bone], lambda n: "m_lid", (8, 13, 8))
cell = 240
try: font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
except Exception: font = ImageFont.load_default()
cam = FR.Camera((-12, 40, 46), (8, 2, 8), cell, cell, 44)   # south-west, above: north = away from the camera, east = right
panels = [("closed (hinge N) - walk on it", lid_scene(0, False))] + [(f"open, hinge {n} - ladder on the {o} wall", lid_scene(h, True)) for h, n, o in ((0, "N", "S"), (1, "E", "W"), (2, "S", "N"), (3, "W", "E"))]
# markers: a zone corner (kitchen #3) on the floor, and a seat station INSIDE a chair's cell
icon_stem = lambda i: reg(f"m_icon_{i}", RPn / f"textures/blocks/{'pw_datum' if BM.ICONS[i][0] == 'datum' else 'pw_' + BM.ICONS[i][0] + '_' + BM.ICONS[i][1]}.png", 8)
num_stem = lambda n: reg(f"m_num_{n}", RPn / f"textures/blocks/pw_num_{n}.png", 8)
mz = ent_faces(gm["zone_top"], lambda n: icon_stem(4), (8, 0, 8)) + ent_faces(gm["zone_sides"], lambda n: num_stem(3), (8, 0, 8))
ms = ent_faces(gm["station"], lambda n: icon_stem(25), (8, 0, 8))
chair = [f for b in FG.PIECES["chair"]["boxes"] for f in FR.box_faces(b, {**FR.WOODS["oak"], "iron": FR.IRON}, FG.PIECES["chair"]["boxes"])]
mcam = FR.Camera((-10, 22, -22), (8, 5, 8), cell, cell, 40)
mpanels = [("zone corner: kitchen #3", FR.scene_faces({}, wall=False) + mz, mcam), ("seat station INSIDE a chair's cell", FR.scene_faces({}, wall=False) + chair + ms, mcam),
           ("port (stair) - icon all faces", FR.scene_faces({}, wall=False) + ent_faces(gm["port"], lambda n: icon_stem(32), (8, 0, 8)), mcam)]
W = 5 * (cell + 6) + 6; H = 2 * (cell + 40) + 40
sheet = Image.new("RGBA", (W, H), (18, 18, 20, 255)); d = ImageDraw.Draw(sheet)
for i, (lab, faces) in enumerate(panels):
    x = 6 + i * (cell + 6); sheet.paste(FR.render(faces, cam), (x, 22)); d.text((x + 3, 22 + cell + 3), lab, fill=(230, 230, 230, 255), font=font)
for i, (lab, faces, c) in enumerate(mpanels):
    x = 6 + i * (cell + 6); y = 22 + cell + 40; sheet.paste(FR.render(faces, c), (x, y)); d.text((x + 3, y + cell + 3), lab, fill=(230, 230, 230, 255), font=font)
d.text((6, 4), "Markers v0.2.1 — ladder hatch lid (Patrix trapdoor; viewed from the south-west, above) and entity markers. North = away from the camera.", fill=(255, 220, 140, 255), font=font)
d.text((6 + 3 * (cell + 6), 22 + cell + 60), "hinge = the side the ladder FACES (opposite the ladder)\nmodel space is left-handed: world = (x, y, -z)\nwrong side in game? /scriptevent civ:hatch flip (or turn)", fill=(200, 200, 200, 255), font=font)
sheet.save(OUT / "markers-v0_2_1-preview.png")
check("H preview sheet rendered (lid closed + 4 open hinges with the ladder opposite; zone corner, seat station inside a chair, port)", (OUT / "markers-v0_2_1-preview.png").exists())

if any(not ok for _, ok in res): print("GATE CLOSED"); sys.exit(1)
outs = []
for sub, name in (("BP", "PW-Civitas-Markers-BP-v0_2_1.mcpack"), ("RP", "PW-Civitas-Markers-RP-v0_2_1.mcpack")):
    out = OUT / name
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted((B / sub).rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(B / sub)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    assert zh == th(B / sub)
    outs.append((name, out.stat().st_size, hashlib.md5(out.read_bytes()).hexdigest()))
print(f"\nGATE OPEN — {len(res)} checks")
for n, sz, md in outs: print(f"  {n} {sz:,} B md5 {md}")
