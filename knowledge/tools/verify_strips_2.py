#!/usr/bin/env python3
"""verify_strips_2.py — gate for RP-04 v1.3.141 · RP-10 v1.3.42 · RP-05 v1.3.51 (D-C263: the L-DEDUP-4-compliant strip repair).
  A manifests   B JSON parses   C diff vs the last INSTALLED versions (.139/.40/.49) = restored strips + portal/fire + flipbook + manifest (+ RP-04 env trio removed)
  D every restored strip is byte-identical to RP-03's intact file and NOT capped; every flipbook entry's source is PACK-LOCAL with frame indices in range (L-DEDUP-4)
  E every terrain_texture entry of the three packs resolves pack-locally (no NEW misses vs the installed version)   P package"""
import hashlib, json, os, re, sys, time, zipfile
from pathlib import Path
from PIL import Image
ROOT = Path("/home/claude"); RP3 = ROOT / "_build/rp03-60"
PK = {"RP-04": ("rp04-139", "rp04-141", [1, 3, 141], "RP-04-AbsolutRealism-Basic-RP-v1_3_141.mcpack"),
      "RP-10": ("rp10-140", "rp10-142", [1, 3, 42], "RP-10-AbsolutRealism-Terrain-RP-v1_3_42.mcpack"),
      "RP-05": ("rp05-49", "rp05-51", [1, 3, 51], "RP-05-AbsolutRealism-Flora-RP-v1_3_51.mcpack")}
rep = json.load(open(ROOT / "_logs/strips_2_build_report.json"))
res = []
def check(n, ok, d=""): res.append((n, bool(ok), d)); print(("PASS " if ok else "FAIL ") + n + (f" — {d}" if d else ""))
def jl(t): return json.loads(re.sub(r"^\s*//.*$", "", t.lstrip("﻿"), flags=re.M))
def md5f(p): return hashlib.md5(Path(p).read_bytes()).hexdigest()
def tree(d): return {str(p.relative_to(d)).replace(os.sep, "/"): md5f(p) for p in Path(d).rglob("*") if p.is_file()}
def local_misses(d):
    """terrain_texture entries + flipbook sources of pack d whose file is not in d (L-DEDUP-4)."""
    d = Path(d); miss = set()
    tt = d / "textures/terrain_texture.json"
    if tt.exists():
        for k, v in jl(tt.read_text(encoding="utf-8"))["texture_data"].items():
            t = v.get("textures"); paths = []
            if isinstance(t, str): paths = [t]
            elif isinstance(t, list): paths = [x if isinstance(x, str) else x.get("path") for x in t]
            elif isinstance(t, dict): paths = [x.get("path") for x in t.get("variations", [])]
            for pth in paths:
                if pth and not any((d / (pth + e)).exists() for e in (".png", ".tga", ".jpg")): miss.add(f"tt:{k}->{pth}")
    fb = d / "textures/flipbook_textures.json"
    if fb.exists():
        for e in jl(fb.read_text(encoding="utf-8")):
            pth = e.get("flipbook_texture", "")
            f = next((d / (pth + x) for x in (".png", ".tga") if (d / (pth + x)).exists()), None)
            if not f: miss.add(f"fb:{pth}"); continue
            w, h = Image.open(f).size; n = h // w if w else 0
            fr = e.get("frames")
            if isinstance(fr, list) and fr and max(fr) >= n: miss.add(f"fb-range:{pth} max {max(fr)} >= {n}")
    return miss
for pk, (old, new, ver, outname) in PK.items():
    o, n = ROOT / "_build" / old, ROOT / "_build" / new
    mo, mn = jl((o / "manifest.json").read_text(encoding="utf-8")), jl((n / "manifest.json").read_text(encoding="utf-8"))
    check(f"A {pk} manifest {'.'.join(map(str, ver))}, uuids unchanged", mn["header"]["version"] == ver and mn["header"]["uuid"] == mo["header"]["uuid"] and all(m["version"] == ver for m in mn["modules"]))
    bad = [str(p.relative_to(n)) for p in n.rglob("*.json") if not (lambda p: (jl(p.read_text(encoding="utf-8")) or True))(p)] if False else []
    for p in n.rglob("*.json"):
        try: jl(p.read_text(encoding="utf-8"))
        except Exception as e: bad.append(f"{p.relative_to(n)}: {str(e)[:30]}")
    check(f"B {pk} every JSON parses", not bad, "; ".join(bad[:3]))
    to, tn = tree(o), tree(n)
    removed = sorted(set(to) - set(tn)); added = sorted(set(tn) - set(to)); changed = sorted(k for k in set(to) & set(tn) if to[k] != tn[k])
    exp_changed = {"textures/blocks/" + f for f in rep[pk]["restored"]} | {"manifest.json"}
    exp_removed = set()
    if pk == "RP-04": exp_changed |= {"textures/blocks/" + f for f in ("nether_portal.png", "nether_portal_n.png", "nether_portal_mer.png", "fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")} | {"textures/flipbook_textures.json"}; exp_removed = {"textures/environment/sun.png", "textures/environment/moon_phases.png", "textures/environment/clouds.png"}
    if pk == "RP-10": exp_changed |= {"textures/blocks/" + f for f in ("fire_0.png", "fire_1.png", "soul_fire_0.png", "soul_fire_1.png")} | {f"textures/blocks/fire_{b}_{v}.png" for b in (0, 1) for v in "abcd"} | {"textures/flipbook_textures.json"}
    check(f"C {pk} diff vs installed = restored strips (+portal/fire/flipbook) + manifest; removed = {sorted(exp_removed) or 'nothing'}", set(changed) == exp_changed and set(removed) == exp_removed and not added, f"unexpected changed {sorted(set(changed) ^ exp_changed)[:5]}, removed {removed}, added {added[:3]}")
    probs = []
    for f in rep[pk]["restored"]:
        p = n / "textures/blocks" / f
        if md5f(p) != md5f(RP3 / "textures/blocks" / f): probs.append(f"{f}: not RP-03's bytes")
        w, h = Image.open(p).size
        if max(w, h) == 256 and min(w, h) < 128: probs.append(f"{f}: still capped {w}x{h}")
    check(f"D {pk} restored strips == RP-03 bytes and intact ({len(rep[pk]['restored'])})", not probs, "; ".join(probs[:4]))
    m_old, m_new = local_misses(o), local_misses(n)
    fresh = sorted(m_new - m_old); fixed = sorted(m_old - m_new)
    check(f"E {pk} L-DEDUP-4: no NEW pack-local misses in terrain_texture/flipbook (installed version had {len(m_old)})", not fresh, f"new {fresh[:4]}; fixed by this build {len(fixed)}")
ok = all(o for _, o, _ in res); stamps = []
if ok:
    for pk, (old, new, ver, outname) in PK.items():
        out = Path("/mnt/user-data/outputs") / outname
        if out.exists(): out.unlink()
        n = ROOT / "_build" / new; cnt = 0
        with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
            for p in sorted(n.rglob("*")):
                if p.is_file(): z.write(p, str(p.relative_to(n)).replace(os.sep, "/")); cnt += 1
        with zipfile.ZipFile(out) as z: badz = z.testzip()
        check(f"P {pk} package", badz is None, f"{outname} {cnt} members {out.stat().st_size:,} B md5 {md5f(out)}")
        stamps.append(f"{outname} {out.stat().st_size:,} B md5 {md5f(out)}")
stamp = f"STRIPS-2 GATE {'OPEN' if all(o for _, o, _ in res) else 'CLOSED'} {sum(1 for _, o, _ in res if o)}/{len(res)}" + (" -> " + " · ".join(stamps) if stamps else "")
with open(ROOT / "_logs/phase_log.md", "a") as fh: fh.write(f"[{time.strftime('%H:%M')} CT 09-27] VERIFY {stamp}\n")
print(stamp); sys.exit(0 if all(o for _, o, _ in res) else 1)
