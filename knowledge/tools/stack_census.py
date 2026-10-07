#!/usr/bin/env python3
"""stack_census.py — the SAME-PATH SHADOW census over his resource-pack order (D-C262; L-ENT-SHADOW).
A file at the same path in a higher pack replaces the lower pack's file outright, so every path shipped by two packs with
DIFFERENT bytes is a decision: the top copy wins whether or not it is the better one.  This lists them all, with image sizes,
plus the 'capped strip' census (long side exactly 256, short side < 128 and <= long/3 — the signature of the old
'long side <= 256' resize pass that turned flipbook strips into slivers).
usage: stack_census.py [--json out.json]     (edit ORDER below when his world order changes; top pack first)"""
import collections, hashlib, io, json, os, sys, zipfile
from PIL import Image

ORDER = [("Markers RP 0.2.1", "dir", "_build/markers-0.2.1/RP"), ("LeafProbe RP 0.3.1", "zip", "_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack"),
         ("StripMine RP 3.0.1", "zip", "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack"), ("RP-11 1.3.35", "zip", "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack"),
         ("RP-10 1.3.41", "dir", "_build/rp10-141"), ("RP-08 1.4.7", "dir", "_build/rp08-147"), ("RP-07 1.4.13", "dir", "_build/rp07-1413"), ("RP-06 1.4.7", "dir", "_build/rp06-147"),
         ("RP-05 1.3.50", "dir", "_build/rp05-50"), ("RP-04 1.3.140", "dir", "_build/rp04-140"), ("RP-03 1.3.60", "dir", "_build/rp03-60"), ("RP-02 2.0.5", "dir", "_build/rp02-205"),
         ("RP-01 1.3.104", "dir", "_build/rp01-104")]
SKIP = {"manifest.json", "pack_icon.png", "PW-DEPENDENCIES.md", "README.md"}
MERGED = {"textures/terrain_texture.json", "textures/item_texture.json", "blocks.json", "sounds/sound_definitions.json", "textures/flipbook_textures.json", "textures/textures_list.json", "sounds.json", "biomes_client.json"}

def load(kind, src):
    d = {}
    if kind == "dir":
        for root, _, fs in os.walk(src):
            for f in fs:
                rel = os.path.relpath(os.path.join(root, f), src).replace(os.sep, "/")
                if rel in SKIP or rel.startswith("texts/"): continue
                d[rel] = open(os.path.join(root, f), "rb").read()
    else:
        z = zipfile.ZipFile(src)
        for n in z.namelist():
            if n.endswith("/") or n in SKIP or n.startswith("texts/"): continue
            d[n] = z.read(n)
    return d

def desc(b, path):
    if path.lower().endswith((".png", ".tga", ".jpg")):
        try: w, h = Image.open(io.BytesIO(b)).size; return f"{w}x{h}"
        except Exception: return f"{len(b)}B?"
    return f"{len(b)}B"

def main():
    packs = [(n, load(k, s)) for n, k, s in ORDER]
    for n, d in packs: print(f"{n:20s} {len(d):5d} files")
    paths = collections.defaultdict(list)
    for n, d in packs:
        for p in d: paths[p].append(n)
    shadow, dup, merged = [], 0, []
    for p, ns in paths.items():
        if len(ns) < 2: continue
        blobs = {n: dict(packs)[n][p] for n in ns}
        if len({hashlib.md5(b).hexdigest() for b in blobs.values()}) == 1: dup += 1; continue
        (merged if p in MERGED else shadow).append((p, ns, {n: desc(b, p) for n, b in blobs.items()}))
    capped = collections.defaultdict(list)
    for n, d in packs:
        for p, b in d.items():
            if not p.lower().endswith((".png", ".tga")): continue
            try: w, h = Image.open(io.BytesIO(b)).size
            except Exception: continue
            if max(w, h) == 256 and min(w, h) < 128 and min(w, h) * 3 <= max(w, h): capped[n].append((p, w, h))
    print(f"\nshared paths {sum(1 for ns in paths.values() if len(ns) > 1)}; identical {dup}; DIFFERING {len(shadow)} (+{len(merged)} engine-merged JSONs, no issue)")
    by = collections.Counter((ns[0], ", ".join(ns[1:])) for p, ns, _ in shadow)
    for (w, l), c in by.most_common(): print(f"  {c:5d}  {w} > {l}")
    print("\ncapped strips (long side 256, sliver):")
    for n, l in capped.items(): print(f"  {n}: {len(l)}  e.g. {l[:3]}")
    if "--json" in sys.argv:
        out = sys.argv[sys.argv.index("--json") + 1]
        json.dump({"order": [n for n, _, _ in ORDER], "differing": shadow, "merged_json": [p for p, _, _ in merged], "capped": capped}, open(out, "w"), indent=0)
        print("written", out)

if __name__ == "__main__":
    main()
