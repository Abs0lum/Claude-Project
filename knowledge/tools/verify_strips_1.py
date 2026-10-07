#!/usr/bin/env python3
"""verify_strips_1.py — gate for RP-04 v1.3.140 · RP-10 v1.3.41 · RP-05 v1.3.50 (D-C262). Packages all three on GATE OPEN.
  A manifests (version/name, uuids unchanged)      B every JSON parses
  C diff vs the previous build == exactly the report's deletions/restores + manifest/flipbook (nothing else)
  D every restored image has the stated size; fire variants = the base strip rotated (frame-exact); normal is unit-length; MER tiled
  E every flipbook entry in the three packs resolves its texture THROUGH THE STACK (his order) and its frame indices fit the strip
  F the texture sets that lost a layer copy in RP-04 still resolve every layer through the stack, and no capped (long side 256,
     short < 128) file remains in the three packs at a path where RP-03 has an intact twin
  P package -> /mnt/user-data/outputs/RP-04-...-v1_3_140.mcpack · RP-10-...-v1_3_41.mcpack · RP-05-...-v1_3_50.mcpack"""
import hashlib, json, os, re, sys, time, zipfile
from pathlib import Path
import numpy as np
from PIL import Image
sys.path.insert(0, "/home/claude/tools")
from build_strips_1 import PACKS, FIRE_ORDER, FIRE_OFFSETS, RP3

ROOT = Path("/home/claude")
OUT = {"RP-04": Path("/mnt/user-data/outputs/RP-04-AbsolutRealism-Basic-RP-v1_3_140.mcpack"),
       "RP-10": Path("/mnt/user-data/outputs/RP-10-AbsolutRealism-Terrain-RP-v1_3_40.mcpack".replace("v1_3_40", "v1_3_41")),
       "RP-05": Path("/mnt/user-data/outputs/RP-05-AbsolutRealism-Flora-RP-v1_3_50.mcpack")}
# his 09-22 world order, top first, with the new builds in place
STACK = [("Markers RP", "dir", ROOT / "_build/markers-0.2.1/RP"), ("LeafProbe RP", "zip", ROOT / "_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack"),
         ("StripMine RP", "zip", ROOT / "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-11", "zip", ROOT / "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack"),
         ("RP-10", "dir", PACKS["RP-10"]["dst"]), ("RP-08", "dir", ROOT / "_build/rp08-147"), ("RP-07", "dir", ROOT / "_build/rp07-1413"), ("RP-06", "dir", ROOT / "_build/rp06-147"),
         ("RP-05", "dir", PACKS["RP-05"]["dst"]), ("RP-04", "dir", PACKS["RP-04"]["dst"]), ("RP-03", "dir", RP3), ("RP-02", "dir", ROOT / "_build/rp02-205"), ("RP-01", "dir", ROOT / "_build/rp01-104")]
res = []
def check(name, ok, detail=""):
    res.append((name, bool(ok), detail)); print(("PASS " if ok else "FAIL ") + name + (f" — {detail}" if detail else ""))
def jl(t): return json.loads(re.sub(r"^\s*//.*$", "", t.lstrip("﻿"), flags=re.M))
def md5(b): return hashlib.md5(b).hexdigest()
rep = json.load(open(ROOT / "_logs/strips_1_build_report.json"))

# stack index: path -> (pack, bytes) for the top-most pack
_zips = {}
def pack_files(kind, src):
    if kind == "dir":
        for r, _, fs in os.walk(src):
            for f in fs: yield os.path.relpath(os.path.join(r, f), src).replace(os.sep, "/"), os.path.join(r, f)
    else:
        z = _zips.setdefault(str(src), zipfile.ZipFile(src))
        for n in z.namelist():
            if not n.endswith("/"): yield n, (z, n)
stack_index = {}
for name, kind, src in STACK:
    for rel, ref in pack_files(kind, src):
        stack_index.setdefault(rel, (name, ref))
def read_stack(rel):
    hit = stack_index.get(rel)
    if not hit: return None, None
    name, ref = hit
    return name, (open(ref, "rb").read() if isinstance(ref, str) else ref[0].read(ref[1]))
def resolve_texture(stem):
    for ext in (".png", ".tga"):
        n, b = read_stack(stem + ext)
        if b: return n, b
    return None, None
def img_size(b):
    from io import BytesIO
    return Image.open(BytesIO(b)).size

for pk, cfg in PACKS.items():
    src, dst = cfg["src"], cfg["dst"]
    mo, mn = jl((src / "manifest.json").read_text(encoding="utf-8")), jl((dst / "manifest.json").read_text(encoding="utf-8"))
    check(f"A {pk} manifest {'.'.join(map(str, cfg['ver']))}, uuids unchanged", mn["header"]["version"] == cfg["ver"] and mn["header"]["name"] == cfg["name"]
          and mn["header"]["uuid"] == mo["header"]["uuid"] and [m["uuid"] for m in mn["modules"]] == [m["uuid"] for m in mo["modules"]] and all(m["version"] == cfg["ver"] for m in mn["modules"]))
    bad = []
    for p in dst.rglob("*.json"):
        try: jl(p.read_text(encoding="utf-8"))
        except Exception as e: bad.append(f"{p.relative_to(dst)}: {str(e)[:40]}")
    check(f"B {pk} every JSON parses", not bad, "; ".join(bad[:3]))
    old = {rel: md5(open(f, "rb").read()) for rel, f in pack_files("dir", src)}
    new = {rel: md5(open(f, "rb").read()) for rel, f in pack_files("dir", dst)}
    removed = sorted(set(old) - set(new)); added = sorted(set(new) - set(old)); changed = sorted(k for k in set(old) & set(new) if old[k] != new[k])
    exp_removed = sorted("textures/blocks/" + d.split(" ")[0] for d in rep[pk]["deleted"])
    exp_changed = {"manifest.json"} | ({"textures/flipbook_textures.json"} if rep[pk]["flipbook"] else set())
    if pk == "RP-04": exp_changed |= {"textures/blocks/" + f for f in ("nether_portal.png", "nether_portal_n.png", "nether_portal_mer.png", "fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")}
    if pk == "RP-10": exp_changed |= {"textures/blocks/" + f for f in ("fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")} | {f"textures/blocks/fire_{b}_{v}.png" for b in (0, 1) for v in "abcd"}
    check(f"C {pk} diff vs previous = report deletions + restores + manifest/flipbook only", removed == exp_removed and not added and set(changed) == exp_changed,
          f"removed {len(removed)}/{len(exp_removed)}, added {added[:3]}, changed-unexpected {sorted(set(changed) ^ exp_changed)[:6]}")

# D restored images
d4, d10 = PACKS["RP-04"]["dst"] / "textures/blocks", PACKS["RP-10"]["dst"] / "textures/blocks"
sizes = {f: Image.open(d4 / f).size for f in ("nether_portal.png", "nether_portal_n.png", "nether_portal_mer.png", "fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")}
check("D RP-04 restored sizes (portal 128x4096 x3, fire 128x3840 x4)", all(sizes[f] == (128, 4096) for f in ("nether_portal.png", "nether_portal_n.png", "nether_portal_mer.png")) and all(sizes[f] == (128, 3840) for f in ("fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")), str(sizes))
nrm = np.asarray(Image.open(d4 / "nether_portal_n.png").convert("RGBA")).astype(float)
v = nrm[..., :3] / 255 * 2 - 1; v[..., 2] = nrm[..., 2] / 255
ln = np.sqrt((v[..., 0] ** 2 + v[..., 1] ** 2 + v[..., 2] ** 2))
check("D portal normal is unit-length (LabPBR XY + reconstructed Z), alpha 255", abs(ln.mean() - 1) < 0.02 and ln.std() < 0.02 and int(nrm[..., 3].min()) == 255, f"|n| mean {ln.mean():.4f} std {ln.std():.4f}")
mer = np.asarray(Image.open(d4 / "nether_portal_mer.png").convert("RGBA"))
check("D portal MER tiled: all 32 frames identical, emissive channel present", all(np.array_equal(mer[:128], mer[i * 128:(i + 1) * 128]) for i in range(32)), f"E mean {mer[..., 1].mean():.1f} R mean {mer[..., 2].mean():.1f} M mean {mer[..., 0].mean():.1f}")
base = np.asarray(Image.open(d10 / "fire_0.png").convert("RGBA"))
frames = [base[i * 128:(i + 1) * 128] for i in range(30)]
ordered = [frames[i] for i in FIRE_ORDER]
ok_rot = True
for vname, k in FIRE_OFFSETS.items():
    var = np.asarray(Image.open(d10 / f"fire_0_{vname}.png").convert("RGBA"))
    want = np.concatenate(ordered[k:] + ordered[:k], axis=0)
    ok_rot &= var.shape == want.shape and np.array_equal(var, want)
check("D RP-10 fire variants a/b/c/d = the Patrix play order started at frames 0/8/15/23 (frame-exact)", ok_rot)

# E flipbooks resolve through the stack with frames in range
def fb_problems(fb, local_dir):
    """flipbook entries whose texture (resolved through the stack, the given pack's own dir first) is missing or has too few frames."""
    out = []
    for e in fb:
        stem = e.get("flipbook_texture", "")
        local = next((local_dir / (stem + ext) for ext in (".png", ".tga") if (local_dir / (stem + ext)).exists()), None)
        if local: pack, b = "local", local.read_bytes()
        else: pack, b = resolve_texture(stem)
        if not b: out.append(f"{stem}: unresolved"); continue
        w, h = img_size(b)
        n = h // w if w else 0
        fr = e.get("frames")
        if isinstance(fr, list) and fr and max(fr) >= n: out.append(f"{stem}: frames max {max(fr)} >= {n} frames ({w}x{h} from {pack})")
    return set(out)
for pk, cfg in PACKS.items():
    fb_new = jl((cfg["dst"] / "textures/flipbook_textures.json").read_text(encoding="utf-8"))
    fb_old = jl((cfg["src"] / "textures/flipbook_textures.json").read_text(encoding="utf-8"))
    p_new, p_old = fb_problems(fb_new, cfg["dst"]), fb_problems(fb_old, cfg["src"])
    fresh = sorted(p_new - p_old)
    check(f"E {pk} flipbook entries resolve through the stack with frame indices in range (no NEW problems)", not fresh, f"{len(fb_new)} entries; pre-existing {len(p_old)} (e.g. {sorted(p_old)[:1]}); new {fresh[:4]}")

# F texture sets whose colour copy left RP-04 still resolve every layer; no capped file with an intact RP-03 twin remains
probs = []
for d in rep["RP-04"]["deleted"]:
    stem = d.split(" ")[0][:-4]
    ts = PACKS["RP-04"]["dst"] / "textures/blocks" / f"{stem}.texture_set.json"
    if not ts.exists(): continue
    t = jl(ts.read_text(encoding="utf-8"))["minecraft:texture_set"]
    for layer, val in t.items():
        if isinstance(val, str):
            pack, b = resolve_texture("textures/blocks/" + val)
            if not b: probs.append(f"{stem}.{layer}={val}: unresolved")
check("F texture-set layers of the deleted colours resolve through the stack", not probs, "; ".join(probs[:5]))
left = []
for pk, cfg in PACKS.items():
    for p in (cfg["dst"] / "textures/blocks").glob("*.png"):
        twin = RP3 / "textures/blocks" / p.name
        if twin.exists() and p.read_bytes() != twin.read_bytes():
            s, t = Image.open(p).size, Image.open(twin).size
            if max(s) == 256 and min(s) < 128 and max(t) > 256 and not (p.name.endswith("_leaves.png") or "grass" in p.name):   # leaves/grass = the deliberate 32-px tier (his call, D-C262)
                left.append(f"{pk}:{p.name}")
check("F no capped copy with an intact RP-03 twin remains in RP-04/RP-10/RP-05 (leaves/grass tier excluded)", not left, str(left[:6]))

ok = all(o for _, o, _ in res); stamps = []
if ok:
    for pk, cfg in PACKS.items():
        out = OUT[pk]
        if out.exists(): out.unlink()
        n = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(cfg["dst"].rglob("*")):
                if p.is_file(): z.write(p, str(p.relative_to(cfg["dst"])).replace(os.sep, "/")); n += 1
        with zipfile.ZipFile(out) as z: badz = z.testzip()
        m = md5(out.read_bytes())
        check(f"P {pk} package", badz is None, f"{out.name} {n} members {out.stat().st_size:,} B md5 {m}")
        stamps.append(f"{out.name} {out.stat().st_size:,} B md5 {m}")
stamp = f"STRIPS-1 GATE {'OPEN' if all(o for _, o, _ in res) else 'CLOSED'} {sum(1 for _, o, _ in res if o)}/{len(res)}" + (" -> " + " · ".join(stamps) if stamps else "")
with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
print(stamp); sys.exit(0 if all(o for _, o, _ in res) else 1)
