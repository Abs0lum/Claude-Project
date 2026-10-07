#!/usr/bin/env python3
"""verify_rp07_1412.py — gate for RP-07 v1.4.12 (the P0 wiring build). Static checks rule OUT (P1); the witness rules IN.
Checks (each PASS/FAIL, gate = all PASS):
  E1  every entity JSON parses; identifier is a Bedrock client-entity id (the vanilla 1.21 set); min_engine_version >= 1.21.0
  E2  every texture path in the rewired entities resolves in-pack (png or tga)
  E3  every geometry id resolves in-pack and geometry.pw_* identifiers are unique across models/entity
  E4  every render controller id resolves in-pack; every Texture.x / Geometry.x it names exists on the entity
  E5  material sampler count == RC texture bindings (entity_alphatest 1, tropicalfish 2) — the goat/camel magenta law
  E6  every animation id resolves in-pack (or is a vanilla common/humanoid id); every bone an ar_/pw_ animation
      touches exists in the entity's geometry
  T1  frog textures carry 0 magenta px; zombified_piglin.png is 512x512; pw_cat + pw_chicken copies are 512x256
  A1  ambient v2: body bob amplitude 0.15, tilt 0.6, every root bone carries the bob
  G1  cow/mooshroom pw_ geometry: head parented under body
  R1  textured renders (front/west/top) of every rewired mob -> _design/rp07-1412/preview-*.png (for the witness sheet)
  P1  package -> /mnt/user-data/outputs/RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_12.mcpack; zip integrity; md5
"""
import glob, hashlib, json, os, re, sys, time, zipfile
sys.path.insert(0, "tools")
from PIL import Image, ImageDraw, ImageFont
import numpy as np

DST = "_build/rp07-1412"
OUT = "/mnt/user-data/outputs/RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_12.mcpack"
VANILLA_IDS = {"minecraft:" + os.path.basename(p)[:-len(".entity.json")] for p in glob.glob("_intake/vanilla-1.21/entity/*.entity.json")}
VANILLA_IDS |= {"minecraft:donkey", "minecraft:mule", "minecraft:horse"}   # fetch 404s; ids known good (1.4.11 drew them)
REWIRED = ["wolf", "fox", "panda", "polar_bear", "cat", "ocelot", "goat", "camel", "chicken", "tropicalfish", "zombie_pigman",
           "donkey", "mule", "cow", "mooshroom"]
SAMPLERS = {"entity_alphatest": 1, "tropicalfish": 2}
VANILLA_ANIMS = re.compile(r"^animation\.(common\.look_at_target|humanoid\.|quadruped\.)")
results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    print(("PASS " if ok else "FAIL ") + name + ("" if not detail else " — " + detail))

def jload(p):
    with open(p) as f:
        return json.load(f)

# ---- pack indexes ----------------------------------------------------------------------------------------------
geo_index, geo_dupes = {}, []
for p in glob.glob(f"{DST}/models/entity/*.json"):
    try:
        j = jload(p)
    except Exception:
        continue
    for g in j.get("minecraft:geometry", []):
        i = g["description"]["identifier"]
        if i in geo_index and i.startswith("geometry.pw_"):
            geo_dupes.append(i)
        geo_index.setdefault(i, (p, g))
    for k, v in j.items():
        if k.startswith("geometry.") and isinstance(v, dict):
            geo_index.setdefault(k, (p, v))
rc_index = {}
for p in glob.glob(f"{DST}/render_controllers/*.json"):
    try:
        for k, v in jload(p).get("render_controllers", {}).items():
            rc_index[k] = v
    except Exception:
        pass
anim_index = {}
for p in glob.glob(f"{DST}/animations/*.json"):
    try:
        for k, v in jload(p).get("animations", {}).items():
            anim_index[k] = v
    except Exception:
        pass

def bones_of(gid):
    p, g = geo_index[gid]
    return {b["name"] for b in g.get("bones", [])}

def ver_ok(v):
    try:
        parts = [int(x) for x in str(v).split(".")]
        return parts >= [1, 21, 0]
    except Exception:
        return False

# ---- E1..E6 per entity ------------------------------------------------------------------------------------------
for mob in REWIRED:
    p = f"{DST}/entity/{mob}.entity.json"
    try:
        d = jload(p)["minecraft:client_entity"]["description"]
    except Exception as e:
        check(f"E1 {mob} parses", False, str(e)); continue
    ident = d["identifier"]
    check(f"E1 {mob} id+engine", ident in VANILLA_IDS and ver_ok(d.get("min_engine_version")), f"{ident} mev={d.get('min_engine_version')}")
    # E2 textures
    missing = [k for k, t in d["textures"].items() if not (os.path.exists(f"{DST}/{t}.png") or os.path.exists(f"{DST}/{t}.tga"))]
    check(f"E2 {mob} textures resolve", not missing, f"{len(d['textures'])} paths" + (f"; MISSING {missing}" if missing else ""))
    # E3 geometries
    gmiss = [k for k, g in d["geometry"].items() if g not in geo_index]
    check(f"E3 {mob} geometries resolve", not gmiss, f"{sorted(set(d['geometry'].values()))}" + (f"; MISSING {gmiss}" if gmiss else ""))
    # E4 / E5 render controllers
    for rc in d["render_controllers"]:
        rcid = rc if isinstance(rc, str) else list(rc.keys())[0]
        body = rc_index.get(rcid)
        if body is None:
            check(f"E4 {mob} rc {rcid}", False, "not in pack"); continue
        blob = json.dumps(body)
        tex_refs = set(re.findall(r"Texture\.([A-Za-z0-9_]+)", blob))
        geo_refs = set(re.findall(r"Geometry\.([A-Za-z0-9_]+)", blob))
        bad_t = [t for t in tex_refs if t not in d["textures"]]
        bad_g = [g for g in geo_refs if g not in d["geometry"]]
        check(f"E4 {mob} rc {rcid} refs", not bad_t and not bad_g, f"{len(tex_refs)} Texture refs, {len(geo_refs)} Geometry refs" + (f"; BAD {bad_t + bad_g}" if bad_t or bad_g else ""))
        mat = d["materials"]["default"]
        want = SAMPLERS.get(mat)
        nbind = len(body.get("textures", []))
        check(f"E5 {mob} samplers", want is not None and nbind == want, f"material {mat} expects {want}, RC binds {nbind}")
    # E6 animations + bones
    bset = set()
    for gid in d["geometry"].values():      # union over every geometry the entity can draw (fish typeA/typeB)
        if gid in geo_index:
            bset |= bones_of(gid)
    amiss, bmiss = [], []
    for key, aid in d["animations"].items():
        if aid in anim_index:
            if key.startswith("ar_") or key in ("pw_ambient", "look_at_target", "tail", "setup", "baby_scaling"):
                for b in anim_index[aid].get("bones", {}):
                    if b not in bset and b != "placeholder_bone":
                        bmiss.append(f"{aid}:{b}")
        elif not VANILLA_ANIMS.match(aid):
            amiss.append(aid)
    check(f"E6 {mob} animations", not amiss and not bmiss, f"{len(d['animations'])} ids" + (f"; MISSING {amiss}" if amiss else "") + (f"; BONES {bmiss}" if bmiss else ""))

check("E3 geometry.pw_* unique", not geo_dupes, str(geo_dupes) if geo_dupes else f"{len([g for g in geo_index if g.startswith('geometry.pw_')])} pw_ ids")

# ---- T1 textures --------------------------------------------------------------------------------------------------
def magenta(p):
    a = np.asarray(Image.open(p).convert("RGBA"))
    return int(((a[..., 0] > 200) & (a[..., 1] < 60) & (a[..., 2] > 200) & (a[..., 3] > 0)).sum())
mag = {f: magenta(f"{DST}/textures/entity/frog/{f}") for f in ["cold_frog.png", "frog_temperate.png", "frog_warm.png"]}
check("T1 frog magenta == 0", all(v == 0 for v in mag.values()), str(mag))
pig = Image.open(f"{DST}/textures/entity/piglin/zombified_piglin.png").size
check("T1 piglin 512x512", pig == (512, 512), str(pig))
sizes = {os.path.basename(p): Image.open(p).size for p in glob.glob(f"{DST}/textures/entity/pw_cat/*.png") + glob.glob(f"{DST}/textures/entity/pw_chicken/*.png")}
check("T1 pw_cat/pw_chicken 512x256", len(sizes) == 15 and all(s == (512, 256) for s in sizes.values()), f"{len(sizes)} files")

# ---- A1 ambient v2 ----------------------------------------------------------------------------------------------
for mob in ["wolf", "fox", "panda", "polar_bear", "cat", "ocelot", "goat", "camel", "chicken", "cow", "mooshroom"]:
    a = anim_index.get(f"animation.pw_{mob}.ambient")
    if not a:
        check(f"A1 {mob} ambient v2", False, "missing"); continue
    b = a["bones"]
    bob = b["body"]["position"][1]
    tilt = b["body"]["rotation"][0]
    ok = bob.startswith("(0.15*math.sin(") and tilt.startswith("(0.6*math.sin(")
    gkey = "pw_cat" if mob in ("cat", "ocelot") else f"pw_{mob}"
    p, g = geo_index[f"geometry.{gkey}"]
    roots = [x["name"] for x in g["bones"] if x.get("parent") is None and x["name"] != "body" and not x["name"].startswith("pw_")]
    carry = [r for r in roots if r in b and bob in str(b[r].get("position", ""))]
    check(f"A1 {mob} ambient v2", ok and len(carry) == len(roots), f"bob={bob[:22]}.. tilt={tilt[:21]}.. roots {carry}/{roots}")

# ---- G1 --------------------------------------------------------------------------------------------------------
for mob in ["cow", "mooshroom"]:
    p, g = geo_index[f"geometry.pw_{mob}"]
    par = {x["name"]: x.get("parent") for x in g["bones"]}
    check(f"G1 {mob} head under body", par.get("head") == "body", f"head.parent={par.get('head')}")

# ---- R1 renders ------------------------------------------------------------------------------------------------
import entity_tex_render as E
os.makedirs("_design/rp07-1412", exist_ok=True)
F = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 13)
FB = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 15)
W, H = 300, 230
rows = []
for mob in REWIRED:
    d = jload(f"{DST}/entity/{mob}.entity.json")["minecraft:client_entity"]["description"]
    gid = d["geometry"].get("default") or list(d["geometry"].values())[0]
    tex = d["textures"].get("default") or list(d["textures"].values())[0]
    texp = f"{DST}/{tex}.png" if os.path.exists(f"{DST}/{tex}.png") else f"{DST}/{tex}.tga"
    gpath = geo_index[gid][0]
    try:
        faces = E.load_entity_faces(gpath, gid)
        ims = []
        for view in ["front", "west", "top"]:
            eye, tgt = E.frame_camera(faces, view)
            ims.append(E.render_entity(faces, texp, eye, tgt, W, H, fov=45, bg=(214, 224, 236), floor_y=0))
        rows.append((mob, gid, tex, ims, ""))
    except Exception as e:
        rows.append((mob, gid, tex, None, repr(e)[:80]))
bad = [r for r in rows if r[3] is None]
check("R1 renders", not bad, f"{len(rows) - len(bad)}/{len(rows)} rendered" + (f"; {[(r[0], r[4]) for r in bad]}" if bad else ""))
half = (len(rows) + 1) // 2
for n, chunk in enumerate([rows[:half], rows[half:]], 1):
    sheet = Image.new("RGB", (3 * W + 4 * 12 + 360, 48 + len(chunk) * (H + 14)), (242, 242, 244))
    dr = ImageDraw.Draw(sheet)
    dr.text((12, 10), f"RP-07 1.4.12 wiring preview {n}/2 — geometry x default texture from the pack (front / west / top), verified rotation law, mob facing SOUTH", font=FB, fill=(20, 20, 20))
    y = 40
    for mob, gid, tex, ims, err in chunk:
        x = 12
        if ims:
            for im in ims:
                sheet.paste(im, (x, y)); x += W + 12
        dr.text((x, y + 6), mob, font=FB, fill=(20, 20, 20))
        dr.text((x, y + 28), gid, font=F, fill=(60, 60, 60))
        dr.text((x, y + 46), tex, font=F, fill=(60, 60, 60))
        if err:
            dr.text((x, y + 64), err, font=F, fill=(160, 20, 20))
        y += H + 14
    sheet.save(f"_design/rp07-1412/preview-{n}.png")

# ---- P1 package ------------------------------------------------------------------------------------------------
gate = all(ok for _, ok, _ in results)
if gate:
    if os.path.exists(OUT):
        os.remove(OUT)
    n = 0
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(DST):
            for f in files:
                full = os.path.join(root, f)
                z.write(full, os.path.relpath(full, DST)); n += 1
    with zipfile.ZipFile(OUT) as z:
        badz = z.testzip()
    md5 = hashlib.md5(open(OUT, "rb").read()).hexdigest()
    size = os.path.getsize(OUT)
    check("P1 package", badz is None, f"{n} members, {size:,} B, md5 {md5}")
    stamp = f"RP-07 1.4.12 GATE OPEN {sum(1 for _, ok, _ in results if ok)}/{len(results)} -> {os.path.basename(OUT)} {size:,} B md5 {md5} ({n} members)"
else:
    stamp = f"RP-07 1.4.12 GATE CLOSED {sum(1 for _, ok, _ in results if ok)}/{len(results)}: " + "; ".join(n for n, ok, d in results if not ok)
with open("_logs/phase_log.md", "a") as f:
    f.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
json.dump([{"check": n, "ok": ok, "detail": d} for n, ok, d in results], open("_logs/v1_4_12_gate.json", "w"), indent=1)
print(stamp)
sys.exit(0 if gate else 1)
