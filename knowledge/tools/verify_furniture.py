#!/usr/bin/env python3
"""verify_furniture.py — gate for the furniture ROUND-2 trees (bp02-184 / rp04-138; Markers 0.1.9 unchanged); packages on GATE OPEN."""
import json, re, sys, hashlib, zipfile, subprocess, collections, os, tempfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
import furniture_geo as FG, furniture_render as FR, build_furniture as BF
ROOT = Path("/home/claude"); OUT = Path("/mnt/user-data/outputs"); DATE = "2026-09-22"
BP0, BP1 = ROOT / "_build/bp02-182", ROOT / "_build/bp02-184"; RP0, RP1 = ROOT / "_build/rp04-136", ROOT / "_build/rp04-138"; MK0, MK1 = ROOT / "_build/markers-0.1.8", ROOT / "_build/markers-0.1.9"
BPR1, RPR1 = ROOT / "_build/bp02-183", ROOT / "_build/rp04-137"   # round 1, for the r1 -> r2 diff
import coplanar_audit as CA
def load(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
results = []
def check(name, ok, detail=""):
    results.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"  -> {str(detail)[:400]}"))

# ---- A parse everything new
bad = []
for p in list(BP1.glob("blocks/pw_furn_*.json")) + [BP1 / "entities/pw_seat.json", BP1 / "manifest.json", RP1 / "models/blocks/pw_furniture.geo.json", RP1 / "entity/pw_seat.entity.json",
                                                     RP1 / "models/entity/pw_seat.geo.json", RP1 / "textures/terrain_texture.json", RP1 / "textures/blocks/pw_furn_iron.texture_set.json", RP1 / "manifest.json"]:
    try: load(p)
    except Exception as e: bad.append((str(p), str(e)[:60]))
check("A every new/changed JSON parses (36 blocks, entity x2, geometry x2, terrain, set, manifests x2)", not bad, bad)
# ---- B geometry law
geo = load(RP1 / "models/blocks/pw_furniture.geo.json")["minecraft:geometry"]; ids = [g["description"]["identifier"] for g in geo]
check("B 27 geometries, unique identifiers (11 pieces + 16 table variants)", len(ids) == 27 and len(set(ids)) == 27, ids)
uvbad, boundbad = [], []
for g in geo:
    for c in g["bones"][0]["cubes"]:
        o, s = c["origin"], c["size"]
        if not (-8 <= o[0] and o[0] + s[0] <= 8 and -8 <= o[2] and o[2] + s[2] <= 8 and 0 <= o[1] and o[1] + s[1] <= 30): boundbad.append((g["description"]["identifier"], o, s))
        if "rotation" not in c and o[1] < 16 < o[1] + s[1]: boundbad.append((g["description"]["identifier"], "crosses y=16", o, s))
        for f, u in c["uv"].items():
            (uu, vv), (w, h) = u["uv"], u["uv_size"]
            if not (0 <= uu and uu + w <= 16 + 1e-6 and 0 <= vv and vv + h <= 16 + 1e-6): uvbad.append((g["description"]["identifier"], f, u))
            if u["material_instance"] not in ("board", "post", "end", "iron"): uvbad.append((g["description"]["identifier"], f, "instance", u["material_instance"]))
check("B every uv window lies inside the 16x16 tile (the in-tile uv law) and names a known instance", not uvbad, uvbad[:5])
check("B every cube inside the cell (x/z -8..8, y 0..30) and no unrotated cube crosses y = 16", not boundbad, boundbad[:5])
# table variants: legs / rails per mask
legbad = []
for mask in BF.MASKS:
    boxes = BF.table_variant(mask); legs = sum(1 for b in boxes if b["m"] == "post"); rails = sum(1 for b in boxes if b["m"] == "board" and b["s"][1] == 3)
    n, e, s_, w = mask; exp_rails = 4 - sum(mask); exp_legs = sum(1 for sides in ((n, w), (n, e), (s_, w), (s_, e)) if not any(sides))
    if legs != exp_legs or rails != exp_rails: legbad.append((mask, legs, rails))
check("B table join variants: rails = 4 - joined sides, legs only at corners with both sides free (16 masks)", not legbad, legbad)
# ---- C blocks
blocks = {p.stem: load(p) for p in BP1.glob("blocks/pw_furn_*.json")}
check("C 36 furniture blocks (12 pieces x 3 woods)", len(blocks) == 36, len(blocks))
tt = load(RP1 / "textures/terrain_texture.json")["texture_data"]; cbad = []
for name, b in blocks.items():
    mb = b["minecraft:block"]; comps = mb["components"]; piece = name[len("pw_furn_"):]; piece = next(p for p in FG.ORDER if piece.startswith(p))
    gid = comps["minecraft:geometry"]["identifier"]
    if gid not in ids: cbad.append((name, "geometry", gid))
    for inst in ("*", "board", "post", "end", "iron"):
        key = comps["minecraft:material_instances"][inst]["texture"]
        if key not in tt: cbad.append((name, "key", key)); continue
        path = tt[key]["textures"]; path = path if isinstance(path, str) else (path.get("path") if isinstance(path, dict) else None)
        if isinstance(path, str) and not any((RP1 / (path + ext)).exists() for ext in (".png", ".tga")): cbad.append((name, "file", path))
    h = BF.COLLISION[piece]
    if h is None:
        if comps["minecraft:collision_box"] is not False: cbad.append((name, "collision should be false"))
        o, s = comps["minecraft:selection_box"]["origin"], comps["minecraft:selection_box"]["size"]
        if not (-8 <= o[0] and o[0] + s[0] <= 8 and -8 <= o[2] and o[2] + s[2] <= 8 and 0 <= o[1] and o[1] + s[1] <= 16): cbad.append((name, "selection out of cell"))
    elif comps["minecraft:collision_box"]["size"][1] != h: cbad.append((name, "collision height", comps["minecraft:collision_box"]["size"]))
    if piece in BF.SEAT_TOP and comps.get("minecraft:custom_components") != ["pw:seat"]: cbad.append((name, "seat component missing"))
    if piece not in BF.SEAT_TOP and "minecraft:custom_components" in comps: cbad.append((name, "unexpected component"))
    states = mb["description"].get("states", {}); perms = mb["permutations"]
    if piece == "table":
        if set(states) != {"pw:n", "pw:e", "pw:s", "pw:w"} or len(perms) != 15: cbad.append((name, "table states/perms", len(perms)))
        for pm in perms:
            g = pm["components"]["minecraft:geometry"]["identifier"]
            if g not in ids: cbad.append((name, "perm geometry", g))
    else:
        if "minecraft:placement_direction" not in mb["description"].get("traits", {}) or len(perms) != 4: cbad.append((name, "rotation perms", len(perms)))
        if mb["description"]["traits"]["minecraft:placement_direction"]["y_rotation_offset"] != 180: cbad.append((name, "y_rotation_offset"))
check("C blocks: geometry ids exist, all 5 material keys resolve to RP-04 files, collision/selection per ruling, seat component on the 4 seat pieces, table states/perms, rotation table", not cbad, cbad[:6])
# ---- D scripts
r = subprocess.run(["node", "--check", str(BP1 / "scripts/pw_furniture.js")], capture_output=True, text=True); check("D pw_furniture.js syntax (node --check)", r.returncode == 0, r.stderr[:200])
r = subprocess.run(["node", "--check", str(BP1 / "scripts/main.js")], capture_output=True, text=True); check("D main.js syntax (node --check)", r.returncode == 0, r.stderr[:200])
m = (BP1 / "scripts/main.js").read_text(encoding="utf-8"); check("D main.js imports pw_furniture.js exactly once", m.count('import "./pw_furniture.js"') == 1)
# mock-run the module: register the component, place two tables, break one
with tempfile.TemporaryDirectory() as td:
    td = Path(td); (td / "node_modules/@minecraft/server").mkdir(parents=True)
    (td / "node_modules/@minecraft/server/package.json").write_text('{"name":"@minecraft/server","type":"module","main":"index.js"}')
    (td / "node_modules/@minecraft/server/index.js").write_text(r'''
export const _subs = { place: [], brk: [], startup: [] }; export const _log = [];
export const world = { afterEvents: { playerPlaceBlock: { subscribe: (f) => _subs.place.push(f) }, playerBreakBlock: { subscribe: (f) => _subs.brk.push(f) } }, getDimension: () => ({ getEntities: () => [] }) };
export const system = { beforeEvents: { startup: { subscribe: (f) => _subs.startup.push(f) } }, runInterval: (f, t) => 1, run: (f) => f() };
export class BlockPermutation { constructor(id, states) { this.typeId = id; this.states = states; this.type = { id }; } static resolve(id, states) { return new BlockPermutation(id, states); } getState(k) { return this.states[k]; } }
''')
    (td / "pw_furniture.js").write_text((BP1 / "scripts/pw_furniture.js").read_text(encoding="utf-8"))
    (td / "test.mjs").write_text(r'''
import { _subs, BlockPermutation } from "@minecraft/server"; import { SEAT_BLOCKS, TABLE_IDS } from "./pw_furniture.js";
const grid = new Map(); const key = (l) => `${l.x},${l.y},${l.z}`;
const dim = { getBlock: (l) => { const b = grid.get(key(l)); return b || null; }, getEntities: () => [] };
function mk(id, l) { const b = { typeId: id, location: l, dimension: dim, permutation: BlockPermutation.resolve(id, { "pw:n": false, "pw:e": false, "pw:s": false, "pw:w": false }), setPermutation(p) { this.permutation = p; } }; grid.set(key(l), b); return b; }
const reg = {}; _subs.startup.forEach((f) => f({ blockComponentRegistry: { registerCustomComponent: (n, c) => { reg[n] = c; } } }));
let fails = 0; const ok = (c, m) => { if (!c) { fails++; console.log("FAIL " + m); } };
ok(reg["pw:seat"] && typeof reg["pw:seat"].onPlayerInteract === "function", "pw:seat registered with onPlayerInteract");
ok(SEAT_BLOCKS.size === 12 && SEAT_BLOCKS.get("pw:furn_chair_oak") === 10 && SEAT_BLOCKS.get("pw:furn_bench_spruce") === 8, "seat registry 12 entries with heights");
ok(TABLE_IDS.size === 3, "3 table ids");
const a = mk("pw:furn_table_oak", { x: 0, y: 64, z: 0 }); _subs.place.forEach((f) => f({ block: a }));
ok(!a.permutation.getState("pw:n") && !a.permutation.getState("pw:e"), "lone table stays 0000");
const b = mk("pw:furn_table_spruce", { x: 1, y: 64, z: 0 }); _subs.place.forEach((f) => f({ block: b }));
ok(a.permutation.getState("pw:e") === true && b.permutation.getState("pw:w") === true && !b.permutation.getState("pw:e"), "east/west join across woods");
const c = mk("pw:furn_table_oak", { x: 0, y: 64, z: -1 }); _subs.place.forEach((f) => f({ block: c }));
ok(a.permutation.getState("pw:n") === true && c.permutation.getState("pw:s") === true, "north neighbour = z-1 joins n/s");
grid.delete(key({ x: 1, y: 64, z: 0 })); _subs.brk.forEach((f) => f({ block: { location: { x: 1, y: 64, z: 0 }, dimension: dim }, brokenBlockPermutation: b.permutation }));
ok(a.permutation.getState("pw:e") === false && a.permutation.getState("pw:n") === true, "breaking the east table clears e, keeps n");
const chair = mk("pw:furn_chair_oak", { x: 5, y: 64, z: 5 }); _subs.place.forEach((f) => f({ block: chair }));
ok(chair.permutation.getState("pw:n") === false, "non-table placement ignored by the join listener");
console.log(fails === 0 ? "MOCK OK" : `MOCK FAILS ${fails}`); process.exit(fails ? 1 : 0);
''')
    r = subprocess.run(["node", "test.mjs"], cwd=td, capture_output=True, text=True)
    check("D mock-run: pw:seat registers, seat registry 12 x heights, table join n/e/s/w on place + break, cross-wood join", r.returncode == 0 and "MOCK OK" in r.stdout, (r.stdout + r.stderr)[-400:])
# ---- E ledger / lang / diff hygiene
led = (BP1 / "PW-DEPENDENCIES.md").read_text(encoding="utf-8"); rows = set(re.findall(r'^\|(\w+)\|`([^`]+)`\|$', led, re.M))
h = hashlib.sha256(json.dumps(sorted([list(r) for r in rows])).encode()).hexdigest()[:16]
check("E BP ledger needs-hash consistent and carries the furniture rows", f"needs-hash `{h}`" in led and {("geometry", "geometry.pw_furn_chair"), ("geometry", "geometry.pw_furn_table_1111"), ("terrain_key", "pw_furn_iron"), ("entity", "pw:seat")} <= rows, h)
lang = (RP1 / "texts/en_US.lang").read_text(encoding="utf-8")
check("E RP-04 lang has the 36 tile names + seat", all(f"tile.pw:furn_{p}_{w}.name=" in lang for p in FG.ORDER for w in BF.WOODS) and "entity.pw:seat.name=" in lang)
def tree_hashes(root): return {str(p.relative_to(root)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in root.rglob("*") if p.is_file()}
h0, h1 = tree_hashes(BP0), tree_hashes(BP1); changed = {k for k in h0 if k in h1 and h0[k] != h1[k]}; added = set(h1) - set(h0); removed = set(h0) - set(h1)
check(f"E BP-02 diff: +{len(added)} files (36 blocks, entity, script), changed only manifest/main.js/ledger, nothing removed", not removed and changed == {"manifest.json", "scripts/main.js", "PW-DEPENDENCIES.md"} and len(added) == 38, (sorted(changed), len(added), sorted(removed)[:3]))
h0, h1 = tree_hashes(RP0), tree_hashes(RP1); changed = {k for k in h0 if k in h1 and h0[k] != h1[k]}; added = set(h1) - set(h0); removed = set(h0) - set(h1)
check(f"E RP-04 diff: +{len(added)} files, changed only manifest/terrain/lang/textures_list/ledger, nothing removed", not removed and changed <= {"manifest.json", "textures/terrain_texture.json", "texts/en_US.lang", "textures/textures_list.json", "PW-DEPENDENCIES.md"} and len(added) == 7, (sorted(changed), sorted(added)))
tl = load(RP1 / "textures/textures_list.json"); actual = sorted({str(q.relative_to(RP1)).replace("\\", "/").rsplit(".", 1)[0] for q in RP1.rglob("*") if q.is_file() and q.suffix.lower() in (".png", ".tga", ".jpg", ".jpeg") and str(q.relative_to(RP1)).startswith("textures/")})
check("E RP-04 textures_list.json == tree", tl == actual, (len(tl), len(actual)))
for tag, dst, ver in (("BP-02", BP1, "1.3.184"), ("RP-04", RP1, "1.3.138")):
    man = load(dst / "manifest.json"); check(f"E {tag} manifest v{ver} + description stamp", man["header"]["version"] == [int(x) for x in ver.split(".")] and man["header"]["description"].startswith(f"v{ver} ({DATE})"))
# ---- G round 2 (witness 19:46)
def geo_boxes(g):
    out = []
    for c in g["bones"][0]["cubes"]:
        b = {"o": [c["origin"][0] + 8, c["origin"][1], c["origin"][2] + 8], "s": list(c["size"]), "m": "board"}
        if "rotation" in c: b["rot"] = list(c["rotation"]); b["piv"] = [c["pivot"][0] + 8, c["pivot"][1], c["pivot"][2] + 8]
        out.append(b)
    return out
shipped = {}
for g in geo:
    gid = g["description"]["identifier"].split("pw_furn_")[1]
    shipped[("table#" + gid.split("_")[1]) if gid.startswith("table_") else gid] = geo_boxes(g)
res = CA.gate(shipped); exposed = {k: v for k, v in res.items() if v}
check(f"G L-COPLANAR-1 on the SHIPPED geometry (27, split cubes, rotations): 0 exposed same-plane same-facing face pairs", not exposed, {k: v[:3] for k, v in list(exposed.items())[:4]})
rmbad = [(n, i, b["minecraft:block"]["components"]["minecraft:material_instances"][i].get("render_method")) for n, b in blocks.items() for i in ("*", "board", "post", "end", "iron")
         if b["minecraft:block"]["components"]["minecraft:material_instances"][i].get("render_method") != "alpha_test_single_sided"]
check("G render_method alpha_test_single_sided on all 5 instances x 36 blocks (alpha_test disables backface culling; textures opaque)", not rmbad, rmbad[:4])
def top_of(gname): return max(b["o"][1] + b["s"][1] for b in shipped[gname])
man_b = shipped["mantel"]; corb = [b for b in man_b if b["s"][0] == 2 and b["s"][2] == 2]
check("G mantel: board top 5 (down 3 cubes from 8), two corbels 2x2 cubes standing on the cell floor", abs(top_of("mantel") - 5) < 1e-6 and len(corb) == 2 and all(b["o"][1] == 0 for b in corb), (top_of("mantel"), [(b["o"], b["s"]) for b in man_b]))
check("G wall shelf: top 8 (= the r1 mantel height)", abs(top_of("wall_shelf") - 8) < 1e-6, top_of("wall_shelf"))
selbad = []
for n, b in blocks.items():
    piece = next(p for p in FG.ORDER if n[len("pw_furn_"):].startswith(p))
    if piece in BF.SELECTION:
        sb = b["minecraft:block"]["components"]["minecraft:selection_box"]; o, sz = BF.SELECTION[piece]
        top = sb["origin"][1] + sb["size"][1]
        if sb["origin"] != o or sb["size"] != sz or abs(top - top_of(piece if piece != "table" else "table#0000")) > 0.5: selbad.append((n, sb))
check("G wall-piece selection boxes follow the lowered geometry (tops within 0.5 cube)", not selbad, selbad[:3])
h0, h1 = tree_hashes(BPR1), tree_hashes(BP1); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
led_ok = (BPR1 / "PW-DEPENDENCIES.md").read_text(encoding="utf-8").replace("v1.3.183 ·", "v1.3.184 ·", 1) == (BP1 / "PW-DEPENDENCIES.md").read_text(encoding="utf-8")
check("G r1 -> r2 BP diff: only the 36 block files + manifest (+ ledger version stamp, same needs-hash) changed, nothing added/removed", set(h0) == set(h1) and ch - {"manifest.json", "PW-DEPENDENCIES.md"} <= {f"blocks/pw_furn_{p}_{w}.json" for p in FG.ORDER for w in BF.WOODS} and "manifest.json" in ch and led_ok, (sorted(ch)[:5], len(ch), led_ok))
h0, h1 = tree_hashes(RPR1), tree_hashes(RP1); ch = {k for k in h0 if k in h1 and h0[k] != h1[k]}
check("G r1 -> r2 RP diff: only models/blocks/pw_furniture.geo.json + manifest (+ ledger stamp) changed", set(h0) == set(h1) and ch <= {"models/blocks/pw_furniture.geo.json", "manifest.json", "PW-DEPENDENCIES.md"} and "models/blocks/pw_furniture.geo.json" in ch, sorted(ch))
# ---- F render parity: the SHIPPED geometry (split cubes, in-tile uv windows) rendered through the preview renderer must match the authoring boxes
def faces_from_geo(g, mats):
    """faces from the exported cubes: the uv window as the game will sample it (u..u+w, v..v+h inside the tile)."""
    out = []
    for c in g["bones"][0]["cubes"]:
        o = [c["origin"][0] + 8, c["origin"][1], c["origin"][2] + 8]; s = c["size"]
        b = {"o": o, "s": s, "m": "board", "faces": {f: c["uv"][f]["material_instance"] for f in c["uv"]}}
        if "rotation" in c: b["rot"] = c["rotation"]; b["piv"] = [c["pivot"][0] + 8, c["pivot"][1], c["pivot"][2] + 8]
        # rebuild with the exported uv windows instead of world-projected coordinates
        x0, y0, z0 = o; x1, y1, z1 = o[0] + s[0], o[1] + s[1], o[2] + s[2]
        P = {"a": [x0, y0, z0], "b": [x1, y0, z0], "c": [x1, y1, z0], "d": [x0, y1, z0], "e": [x0, y0, z1], "f": [x1, y0, z1], "g": [x1, y1, z1], "h": [x0, y1, z1]}
        Fk = {"north": ["a", "b", "c", "d"], "south": ["f", "e", "h", "g"], "west": ["e", "a", "d", "h"], "east": ["b", "f", "g", "c"], "up": ["d", "c", "g", "h"], "down": ["e", "f", "b", "a"]}
        piv, rot = b.get("piv", [0, 0, 0]), b.get("rot", [0, 0, 0])
        for name, keys in Fk.items():
            u, v = c["uv"][name]["uv"]; w, h = c["uv"][name]["uv_size"]; inst = c["uv"][name]["material_instance"]
            pts = [FR.rot_transform(P[k], piv, rot) if "rot" in b else P[k] for k in keys]
            # corner uv in the window: the face corner order matches (u,v),(u+w,v),(u+w,v+h),(u,v+h) for the exporter's orientation
            win = [(u, v + h), (u + w, v + h), (u + w, v), (u, v)] if name in ("north", "south", "east", "west") else [(u, v), (u + w, v), (u + w, v + h), (u, v + h)]
            if name == "down": win = [(u, v + h), (u + w, v + h), (u + w, v), (u, v)]
            for sp, su in FR.subdivide(pts, win): out.append((name, mats[inst], sp, su))
    return out
mats = {**FR.WOODS["oak"], "iron": FR.IRON}
par = []
for gname, piece_boxes in (("geometry.pw_furn_chair", FG.PIECES["chair"]["boxes"]), ("geometry.pw_furn_dresser", FG.PIECES["dresser"]["boxes"]), ("geometry.pw_furn_table_0000", BF.table_variant((0, 0, 0, 0))), ("geometry.pw_furn_barrel_seat", FG.PIECES["barrel_seat"]["boxes"])):
    g = next(x for x in geo if x["description"]["identifier"] == gname); h_ = max(b["o"][1] + b["s"][1] for b in piece_boxes)
    cam = FR.Camera((-12, 26, -26), (8, h_ / 2 + 1, 8), 240, 240, 42)
    a = FR.render([f for b in piece_boxes for f in FR.box_faces(b, mats, piece_boxes)], cam); bimg = FR.render(faces_from_geo(g, mats), cam)
    A = np.array(a.resize((60, 60), Image.BOX)).astype(float); Bm = np.array(bimg.resize((60, 60), Image.BOX)).astype(float)
    d = np.abs(A[..., :3] - Bm[..., :3]).mean()          # structure/colour at 4-cube resolution: split boxes, material instances, uv windows
    par.append((gname.split("pw_furn_")[1], round(float(d), 2)))
    Image.fromarray(np.concatenate([np.array(a), np.array(bimg)], axis=1)).save(ROOT / f"_design/furniture/parity_{gname.split('pw_furn_')[1]}.png")
check(f"F shipped-geometry render parity vs the authoring boxes at 4-cube resolution (mean |diff| per piece {par}; < 8 = same picture)", all(d < 8 for _, d in par), par)
failed = [n for n, ok, _ in results if not ok]
if failed: print(f"\nGATE CLOSED — {failed}"); sys.exit(1)
outs = []
for dst, outname in ((BP1, "BP-02-AbsolutRealism-Tectonic-BP-v1_3_184.mcpack"), (RP1, "RP-04-AbsolutRealism-Basic-RP-v1_3_138.mcpack")):
    out = OUT / outname
    if out.exists(): out.unlink()
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as z:
        for p in sorted(dst.rglob("*")):
            if p.is_file(): z.write(p, str(p.relative_to(dst)).replace("\\", "/"))
    with zipfile.ZipFile(out) as z: zh = {n: hashlib.md5(z.read(n)).hexdigest() for n in z.namelist() if not n.endswith("/")}
    th = {str(p.relative_to(dst)).replace("\\", "/"): hashlib.md5(p.read_bytes()).hexdigest() for p in dst.rglob("*") if p.is_file()}
    assert zh == th, "zip content mismatch"
    outs.append((outname, out.stat().st_size, hashlib.md5(out.read_bytes()).hexdigest()))
print(f"\nGATE OPEN — {len(results)} checks passed")
for n, sz, md in outs: print(f"  {n} {sz:,} B md5 {md}")
json.dump({"checks": len(results), "outputs": outs}, open(ROOT / "_logs/v1_furniture_gate.json", "w"), indent=1)
