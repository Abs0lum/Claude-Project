#!/usr/bin/env python3
"""purge_harvest.py — the reference harvest behind the dead-weight purge (ruling 17:08 CT, D-C219).

For every RP in the stack (the four rebuilt trees + every other RP zip in STACK-LIST) collect every texture path any JSON
can resolve to:
  * any string anywhere in any *.json that starts with "textures/" (entity/attachable/particle/terrain/item/flipbook/
    texture_set/ui/...) — extension stripped;                                      textures_list.json is EXCLUDED (it is
    a cache of the pack's own files, regenerated after the purge, and would make every file look referenced);
  * texture_set.json values that are bare stems resolve relative to the set's own folder (Bedrock semantics).
Liveness of a texture file in a rebuilt tree = one of
  REF        referenced by any JSON in any pack of the stack;
  VANILLA    its path (stem) exists in the vanilla 1.26.50 resource pack -> it overrides vanilla by name;
  OURS       pw_/am_ (or pw/ am/ folder) — our own authored art, never purged without a ruling (listed if unreferenced);
  COMPANION  <stem>_mer/_normal/_heightmap/_n/_s/_e (+ <stem>.texture_set.json and what it references) of a live stem.
Everything else is a CANDIDATE, classified
  DUP             pixel-identical (or flipH/flipV/rot180) to a live texture anywhere in the four trees;
  CONSUMED        explicit sources of a derived live texture (crop/relayout/convert): the chest halves and the Java-layout
                  chest sources, the conduit canvas, the Java-layout bed normals, ... (CONSUMED table below);
  COMPANION-DEAD  a companion (or texture set) whose base stem is itself a candidate or does not exist;
  UNIQUE          unreferenced Java/Patrix art with no vanilla slot and no live twin — "custom authoring material":
                  KEPT and listed for Abs0lum.
Output: _logs/purge_harvest.json (refs, liveness, classes, sizes) + a printed summary.
"""
import json, re, zipfile, subprocess, collections, hashlib, io, sys
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude"); PACKS = ROOT / "_packs"; VAN = ROOT / "_intake/bedrock-samples"
TREES = {"RP-04": ROOT / "_build/rp04-135", "RP-03": ROOT / "_build/rp03-58", "RP-01": ROOT / "_build/rp01-103", "RP-05": ROOT / "_build/rp05-47"}
OTHER_TREES = {"RP-02": ROOT / "_build/rp02-203"}
TEX_EXT = ("png", "tga", "jpg", "jpeg")
COMP_SUFFIXES = ("_mer", "_mers", "_normal", "_heightmap", "_n", "_s", "_e")
OURS_RE = re.compile(r"(^|/)(pw_|am_|pw/|am/|absolut|abs0lut)", re.I)

def jload_text(t):
    t = t.lstrip("﻿"); t = re.sub(r"//[^\n]*", "", t); t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return json.loads(t)

def strip_ext(p):
    p = p.replace("\\", "/")
    if p.rsplit(".", 1)[-1].lower() in TEX_EXT: p = p.rsplit(".", 1)[0]
    return p

def walk_strings(o, out):
    if isinstance(o, str): out.append(o)
    elif isinstance(o, list):
        for x in o: walk_strings(x, out)
    elif isinstance(o, dict):
        for k, v in o.items(): walk_strings(k, out); walk_strings(v, out)

class Pack:
    def __init__(self, name, files, reader):
        self.name = name; self.files = set(files); self.read = reader
        self.tex = {}          # stem -> file path (first wins)
        for f in sorted(self.files):
            if f.startswith("textures/") and f.rsplit(".", 1)[-1].lower() in TEX_EXT: self.tex.setdefault(f.rsplit(".", 1)[0], f)
        self.refs = collections.defaultdict(set)   # stem -> set(json files referencing it)   (non-texture-set JSON only)
        self.setrefs = {}                            # texture_set.json file -> set(stems it references)  (count only if the set's base is live)
        self.bad_json = []
        for f in sorted(self.files):
            if not f.endswith(".json") or f.endswith("textures_list.json"): continue
            try: o = jload_text(self.read(f))
            except Exception as e: self.bad_json.append((f, str(e)[:80])); continue
            ss = []; walk_strings(o, ss)
            if f.endswith(".texture_set.json"):
                folder = f.rsplit("/", 1)[0]; got = set()
                for s in ss:
                    if s.startswith("textures/"): got.add(strip_ext(s))
                    elif re.fullmatch(r"[A-Za-z0-9_./-]+", s) and not s.startswith("#") and s not in ("minecraft:texture_set", "format_version", "color", "metalness_emissive_roughness", "metalness_emissive_roughness_subsurface", "normal", "heightmap") and not re.fullmatch(r"\d+(\.\d+)*", s):
                        got.add(strip_ext(folder + "/" + s))
                self.setrefs[f] = got
            else:
                for s in ss:
                    if s.startswith("textures/"): self.refs[strip_ext(s)].add(f)

def zip_pack(name, path):
    z = zipfile.ZipFile(path); return Pack(name, z.namelist(), lambda p, z=z: z.read(p).decode("utf-8", "replace"))

def tree_pack(name, root):
    root = Path(root); fl = [str(p.relative_to(root)).replace("\\", "/") for p in root.rglob("*") if p.is_file()]
    return Pack(name, fl, lambda p, root=root: (root / p).read_text(encoding="utf-8", errors="replace"))

def vanilla_stems():
    fl = subprocess.run(["git", "-C", str(VAN), "ls-tree", "-r", "--name-only", "HEAD"], capture_output=True, text=True).stdout.split("\n")
    return {p[len("resource_pack/"):].rsplit(".", 1)[0] for p in fl if p.startswith("resource_pack/textures/") and p.rsplit(".", 1)[-1].lower() in TEX_EXT}

def stack_zip_packs():
    out = []
    for line in (PACKS / "STACK-LIST-2026-09-21.txt").read_text().split("\n"):
        m = re.match(r"(RP-\d\d|PW-[A-Za-z]+-RP|PW-Civitas-Markers-RP)", line.strip())
        if not m: continue
        tag = m.group(1)
        if tag in TREES or tag in OTHER_TREES: continue
        cands = [c for c in sorted(PACKS.glob(f"{tag}-*.mcpack")) if c.suffix == ".mcpack"]
        if not cands and tag.startswith("PW-Civitas"): cands = sorted((PACKS / "markers").glob("PW-Civitas-Markers-RP-*.mcpack"))
        if cands: out.append(zip_pack(f"{tag}:{cands[-1].name}", cands[-1]))
        else: print("  (no local copy for", tag, ")")
    return out

def base_of(stem):
    """companion -> (base stem, suffix) or (None, None)."""
    for suf in COMP_SUFFIXES:
        if stem.endswith(suf): return stem[:-len(suf)], suf
    return None, None

def pixel_keys(path):
    """hash of the pixels for identity, flipH, flipV, rot180 (RGBA bytes + size)."""
    try: im = Image.open(path).convert("RGBA")
    except Exception: return {}
    keys = {}
    for tag, t in (("id", im), ("fh", im.transpose(Image.FLIP_LEFT_RIGHT)), ("fv", im.transpose(Image.FLIP_TOP_BOTTOM)), ("r2", im.transpose(Image.ROTATE_180))):
        keys[tag] = hashlib.md5(f"{t.size}".encode() + t.tobytes()).hexdigest()
    return keys

# explicit consumed sources (derived live textures exist under other names / layouts)
CONSUMED = {
    "RP-04": [r"^textures/entity/chest/(normal|trapped|copper|copper_exposed|copper_oxidized|copper_weathered)_(left|right)(_n)?$",   # E2 double halves
              r"^textures/entity/chest/.*_n$",                    # Java-layout normals of converted chests
              r"^textures/entity/bed/.*_n$",                      # Java-layout bed normals (engine layout differs)
              r"^textures/entity/conduit/", r"^textures/entity/decorated_pot/", r"^textures/entity/end_crystal/", r"^textures/entity/bell/",
              r"^textures/entity/armorstand/", r"^textures/entity/banner/", r"^textures/entity/banner_base(_n)?$",
              r"^textures/entity/signs/", r"^textures/entity/boat/", r"^textures/entity/chest_boat/", r"^textures/entity/shulker/light_gray(_n)?$"],
    "RP-03": [r"^textures/blocks/stonecutter_side$"],              # mirrored into stonecutter_other_side in phase 1 (still live itself if vanilla-named)
    "RP-01": [], "RP-05": []}

def main(out_json=ROOT / "_logs/purge_harvest.json", keep_list=None):
    keep_list = set(keep_list or [])
    van = vanilla_stems()
    trees = {k: tree_pack(k, v) for k, v in TREES.items()}
    others = {k: tree_pack(k, v) for k, v in OTHER_TREES.items()}
    zips = stack_zip_packs()
    allpacks = list(trees.values()) + list(others.values()) + zips
    for p in allpacks:
        if p.bad_json: print(f"  !! {p.name}: {len(p.bad_json)} unparsable json (first: {p.bad_json[0]})")
    # global reference map: stem -> {pack: [json...]}
    refs = collections.defaultdict(dict)
    for p in allpacks:
        for stem, js in p.refs.items(): refs[stem][p.name] = sorted(js)
    # liveness per rebuilt tree
    result = {"trees": {}, "refs_total": len(refs)}
    live_pixel_index = {}     # hash -> (tree, stem) of live files, for DUP detection
    per_tree = {}
    for tag, p in trees.items():
        root = TREES[tag]; live = {}; cand = {}
        for stem, f in p.tex.items():
            why = []
            if stem in refs: why.append("REF:" + ",".join(sorted(refs[stem])))
            if stem in van: why.append("VANILLA")
            if OURS_RE.search(stem): why.append("OURS")
            if stem in keep_list: why.append("KEEP")
            if why: live[stem] = why
            else: cand[stem] = None
        # companions of live stems, and whatever a LIVE stem's texture set references, are live too — fixed point
        changed = True
        while changed:
            changed = False
            for stem in list(cand):
                b, suf = base_of(stem)
                if b and b in live: live[stem] = [f"COMPANION({suf}) of {b}"]; del cand[stem]; changed = True
            for setf, got in p.setrefs.items():
                b = setf[:-len(".texture_set.json")]
                if b in live:
                    for s2 in got:
                        if s2 in cand: live[s2] = [f"SET-REF of {b}"]; del cand[s2]; changed = True
        per_tree[tag] = (p, live, cand)
    # pixel index of live files
    print("indexing live pixels ...")
    for tag, (p, live, cand) in per_tree.items():
        for stem in live:
            f = TREES[tag] / p.tex[stem]
            for k, h in pixel_keys(f).items():
                if k == "id": live_pixel_index.setdefault(h, (tag, stem))
    # classify candidates
    for tag, (p, live, cand) in per_tree.items():
        root = TREES[tag]; classes = {}
        cons = [re.compile(x) for x in CONSUMED.get(tag, [])]
        for stem in cand:
            f = root / p.tex[stem]; size = f.stat().st_size
            b, suf = base_of(stem)
            cls = None; note = ""
            if b is not None and (b in cand or b not in p.tex) and not f.name.endswith(".texture_set.json"):
                cls = "COMPANION-DEAD"; note = f"{suf} of {'candidate' if b in cand else 'absent'} {b}"
            if cls is None:
                for rx in cons:
                    if rx.search(stem): cls = "CONSUMED"; note = rx.pattern; break
            if cls is None:
                keys = pixel_keys(f)
                for k, h in keys.items():
                    if h in live_pixel_index:
                        t2, s2 = live_pixel_index[h]; cls = "DUP"; note = f"{k} of {t2}:{s2}"; break
            if cls is None: cls = "UNIQUE"
            classes[stem] = {"file": p.tex[stem], "size": size, "class": cls, "note": note}
        # texture sets without a live base
        dead_sets = []
        for f in p.files:
            if f.endswith(".texture_set.json"):
                stem = f[:-len(".texture_set.json")]
                if stem not in live: dead_sets.append(f)
        # unreferenced OURS + unreferenced vanilla-named (informational)
        ours_unref = sorted(s for s, w in live.items() if "OURS" in w and not any(x.startswith("REF") for x in w))
        result["trees"][tag] = {"textures": len(p.tex), "live": {s: w for s, w in live.items()}, "candidates": classes, "dead_texture_sets": sorted(dead_sets), "ours_unreferenced": ours_unref}
        cnt = collections.Counter(v["class"] for v in classes.values()); sz = collections.Counter()
        for v in classes.values(): sz[v["class"]] += v["size"]
        print(f"{tag}: {len(p.tex)} textures, live {len(live)}, candidates {len(classes)}: " + ", ".join(f"{k} {cnt[k]} ({sz[k]/1e6:.1f} MB)" for k in ("DUP", "CONSUMED", "COMPANION-DEAD", "UNIQUE")) + f"; dead texture sets {len(dead_sets)}; OURS unreferenced {len(ours_unref)}")
    result["refs"] = {k: v for k, v in refs.items()}
    Path(out_json).write_text(json.dumps(result, indent=1))
    return result

if __name__ == "__main__":
    main()
