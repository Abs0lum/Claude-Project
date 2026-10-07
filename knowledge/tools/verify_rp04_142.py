#!/usr/bin/env python3
"""verify_rp04_142.py — gate for RP-04 v1.3.142 (D-C267).
  A  diff vs v1.3.141 = flipbook_textures.json, terrain_texture.json, textures/blocks/lava_still.png, manifest.json — nothing added/removed
  B  flipbook: exactly one still_lava (lava_still, tpf 10, blend) and one flowing_lava (lava_flow, tpf 1, replicate 2); no dead lava tiles;
     every flipbook entry still points at a file this pack holds; every entry's strip height is a multiple of its width
  C  lava_still.png 128 x 1024 (8 frames) = the Patrix source pixels; lava_flow.png unchanged 128 x 6144 (48 frames)
  D  terrain: the 7 dead lava keys gone, every other key unchanged; no blocks.json / behaviour pack / other RP names a removed key
  E  the lava PBR layers that sit beside the strips have the strip's size (lava_still_mer / _n 128 x 1024) — informational: no
     texture set names them (so no mismatch can reach the renderer)
  F  manifest 1.3.142, uuid kept
Exit 1 on any FAIL."""
import filecmp, glob, json, re, sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path("/home/claude"); OLD, NEW = ROOT / "_build/rp04-141", ROOT / "_build/rp04-142"
PATRIX = ROOT / "_intake/patrix128/pull3/assets/minecraft/textures/block/lava_still.png"
DEAD = ["lava_still", "lava_flow", "lava_still_v1", "lava_still_v2", "lava_still_v3", "lava_still_v4", "lava_still_single"]
results = []


def check(tag, ok, msg):
    results.append((tag, bool(ok), msg)); print(f"{'PASS' if ok else 'FAIL'} {tag}: {msg}")


def files(root):
    return {str(p.relative_to(root)) for p in root.rglob("*") if p.is_file()}


def jl(p):
    return json.loads(re.sub(r"^\s*//.*$", "", Path(p).read_text(encoding="utf-8-sig"), flags=re.M))


def main():
    fo, fn = files(OLD), files(NEW)
    changed = {f for f in fo & fn if not filecmp.cmp(OLD / f, NEW / f, shallow=False)}
    check("A1", fo == fn, f"same file set ({len(fn)})")
    check("A2", changed == {"textures/flipbook_textures.json", "textures/terrain_texture.json", "textures/blocks/lava_still.png", "manifest.json"}, f"changed {sorted(changed)}")
    fb = jl(NEW / "textures/flipbook_textures.json")
    sl = [e for e in fb if e.get("atlas_tile") == "still_lava"]; fl = [e for e in fb if e.get("atlas_tile") == "flowing_lava"]
    check("B1", len(sl) == 1 and sl[0]["flipbook_texture"] == "textures/blocks/lava_still" and sl[0]["ticks_per_frame"] == 10 and sl[0].get("blend_frames") is True, f"still_lava {sl}")
    check("B2", len(fl) == 1 and fl[0]["flipbook_texture"] == "textures/blocks/lava_flow" and fl[0]["ticks_per_frame"] == 1 and fl[0].get("replicate") == 2, f"flowing_lava {fl}")
    check("B3", not [e for e in fb if e.get("atlas_tile") in DEAD], "no dead lava tiles")
    bad = []
    for e in fb:
        p = NEW / (e["flipbook_texture"] + ".png")
        if not p.exists(): bad.append(("missing", e["atlas_tile"])); continue
        w, h = Image.open(p).size
        if h % w: bad.append(("not-square-frames", e["atlas_tile"], (w, h)))
    check("B4", not bad, f"{len(fb)} flipbook entries resolve to files with whole frames" + (f" — {bad}" if bad else ""))
    a = np.asarray(Image.open(NEW / "textures/blocks/lava_still.png").convert("RGB")); b = np.asarray(Image.open(PATRIX).convert("RGB"))
    check("C1", a.shape == (1024, 128, 3) and (a == b).all(), f"lava_still.png {a.shape[1]}x{a.shape[0]} == Patrix source pixels: {(a == b).all() if a.shape == b.shape else False}")
    check("C2", filecmp.cmp(OLD / "textures/blocks/lava_flow.png", NEW / "textures/blocks/lava_flow.png", shallow=False) and Image.open(NEW / "textures/blocks/lava_flow.png").size == (128, 6144), "lava_flow.png unchanged 128x6144 (48 frames)")
    to, tn = jl(OLD / "textures/terrain_texture.json")["texture_data"], jl(NEW / "textures/terrain_texture.json")["texture_data"]
    check("D1", not any(k in tn for k in DEAD) and set(to) - set(tn) == set(DEAD) and all(tn[k] == to[k] for k in tn), f"{len(DEAD)} keys removed, {len(tn)} unchanged")
    refs = []
    for pat in ["_build/rp*-*/blocks.json", "_build/bp0*-18[9]/**/*.json", "_build/bp01-135/**/*.json", "_build/bp03-134/**/*.json", "_build/markers-0.2.1/**/*.json", "_build/testrunner-0.3.1/**/*.json"]:
        for f in glob.glob(str(ROOT / pat), recursive=True):
            if "/rp04-1" in f and "rp04-142" not in f: continue
            t = open(f, encoding="utf-8-sig", errors="replace").read()
            for k in DEAD:
                if f'"{k}"' in t: refs.append((f.replace(str(ROOT) + "/", ""), k))
    check("D2", not refs, f"references to removed keys: {refs[:6]}")
    info = {n: Image.open(NEW / f"textures/blocks/{n}.png").size for n in ("lava_still_mer", "lava_still_n")}
    ts = glob.glob(str(NEW / "textures/blocks/lava*.texture_set.json"))
    check("E", all(s == (128, 1024) for s in info.values()) and not ts, f"PBR layers {info}; texture sets naming lava: {len(ts)}")
    mo, mn = jl(OLD / "manifest.json"), jl(NEW / "manifest.json")
    check("F", mn["header"]["version"] == [1, 3, 142] and mn["header"]["uuid"] == mo["header"]["uuid"], f"version {mn['header']['version']} uuid kept")
    fails = [r for r in results if not r[1]]
    print(f"GATE {'OPEN' if not fails else 'CLOSED'} {len(results) - len(fails)}/{len(results)}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
