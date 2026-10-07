#!/usr/bin/env python3
"""ownership_map.py — the OWNERSHIP census over the whole resource-pack stack (D-C264; Abs0lum 23:28 ownership law + 00:25 rulings).

For every file every pack ships, WHO REFERENCES IT?  A "reference" is a registry entry inside a pack that names the file:
  terrain_texture.json / item_texture.json keys, flipbook_textures.json entries, entity + attachable texture maps, particle
  textures, texture_set layers, sound_definitions sound paths — plus the VANILLA registries (bedrock-samples 1.26.50) and the
  engine-implicit directories the engine loads by fixed name (textures/environment, ui, gui, map, misc, painting, colormap,
  models/armor, font, ...).  Global-namespace identifiers (geometry / animation / animation_controller / render_controller /
  particle / fog ids) are collected separately: they merge across packs by id, so a cross-pack id reference is a DEPENDENCY,
  not a duplicate.

Then, per file path, the classes the ownership law needs:
  OWNED        exactly one referencing pack among its holders            -> that pack owns it; other holders' copies are SHADOWS
  MULTI-REF    two or more holder packs reference it from their own registries   -> the conflict zone (his law: one owner;
               L-DEDUP-4: each keeps a copy) — listed by family, differing bytes flagged
  X-PACK       referenced by pack(s) that do not hold it, held elsewhere  -> under L-DEDUP-4 the referencing pack needs the
               copy; under the key-follows-file rule the KEY moves to the holder — listed with the key + holder
  ORPHAN       held, referenced by nothing (our registries, vanilla, engine-implicit all checked)   -> waste
  MISSING      referenced, held by nobody (and not vanilla)               -> dead keys or missing art
Shadows are split into IDENTICAL (safe deletes) and DIFFERING (a decision: which bytes are "more relevant" -> migrate into
the owner, delete the rest; the tool proposes: larger pixel size > has a texture_set > higher pack).

Output: a printed summary + _logs/ownership_map.json (every path with its class, holders, referencing packs, sizes, the
proposal) + per-pack size projections (uncompressed and zip-compressed, from the shipped mcpacks' member sizes) BEFORE and
AFTER the proposal, and the RP-03 + RP-04 merge projection against his 250 rule.
usage: ownership_map.py [--json _logs/ownership_map.json]"""
import collections, hashlib, io, json, os, re, sys, zipfile, zlib
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude")
# top -> bottom (his 09-22 order; TestRunner RP sits on top only while testing)
STACK = [
    ("TestRunner RP 0.2.2", "dir", "_build/testrunner-rp-0.2.2", "/mnt/user-data/outputs/PW-TestRunner-RP-v0_2_2.mcpack"),
    ("Markers RP 0.2.1", "dir", "_build/markers-0.2.1/RP", "/mnt/user-data/outputs/PW-Civitas-Markers-RP-v0_2_1.mcpack"),
    ("LeafProbe RP 0.3.1", "zip", "_intake/stack-rps/PW-LeafProbe-RP-v0_3_1.mcpack", None),
    ("StripMine RP 3.0.1", "zip", "_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack", None),
    ("RP-11 1.3.35", "zip", "_intake/stack-rps/RP-11-AbsolutRealism-Ores-RP-v1_3_35.mcpack", None),
    ("RP-10 1.3.42", "dir", "_build/rp10-142", "/mnt/user-data/outputs/RP-10-AbsolutRealism-Terrain-RP-v1_3_42.mcpack"),
    ("RP-08 1.4.7", "dir", "_build/rp08-147", "/mnt/user-data/outputs/RP-08-AbsolutRealism-Items-RP-v1_4_7.mcpack"),
    ("RP-07 1.4.13", "dir", "_build/rp07-1413", "/mnt/user-data/outputs/RP-07-AbsolutRealism-Neutral-Mobs-RP-v1_4_13.mcpack"),
    ("RP-06 1.4.8", "dir", "_build/rp06-148", "/mnt/user-data/outputs/RP-06-AbsolutRealism-Hostile-Mobs-RP-v1_4_8.mcpack"),
    ("RP-05 1.3.51", "dir", "_build/rp05-51", "/mnt/user-data/outputs/RP-05-AbsolutRealism-Flora-RP-v1_3_51.mcpack"),
    ("RP-04 1.3.141", "dir", "_build/rp04-141", "/mnt/user-data/outputs/RP-04-AbsolutRealism-Basic-RP-v1_3_141.mcpack"),
    ("RP-03 1.3.60", "dir", "_build/rp03-60", "/mnt/user-data/outputs/RP-03-AbsolutRealism-PBR-RP-v1_3_60.mcpack"),
    ("RP-02 2.0.5", "dir", "_build/rp02-205", "/mnt/user-data/outputs/RP-02-AbsolutRealism-Atmospheric-Effects-RP-v2_0_5.mcpack"),
    ("RP-01 1.3.104", "dir", "_build/rp01-104", "/mnt/user-data/outputs/RP-01-AbsolutRealism-Tectonic-RP-v1_3_104.mcpack"),
]
# behaviour packs: reference sources only (texture KEYS via material_instances, geometry ids, particle ids in scripts)
BPS = [
    ("BP-02 1.3.189", "dir", "_build/bp02-189"), ("BP-01 1.3.35", "zip", "/mnt/user-data/outputs/BP-01-AbsolutRealism-Atmospheric-Effects-BP-v1_3_35.mcpack"),
    ("BP-03 1.3.34", "zip", "/mnt/user-data/outputs/BP-03-Abs0lutRealism-Identification-Diagnostics-BP-v1_3_34.mcpack"),
    ("StripMine BP 1.3.3", "dir", "_build/stripmine-bp-133"), ("Markers BP 0.2.1", "dir", "_build/markers-0.2.1/BP"),
    ("TestRunner BP 0.2.2", "dir", "_build/testrunner-0.2.2"), ("LeafProbe BP 0.4.1", "zip", "_intake/stack-bps/PW-LeafProbe-BP-v0_4_1.mcpack"),
    ("WitnessRig BP", "zip", "_intake/stack-bps/PW-WitnessRig-BP-v0_1_0.mcpack"), ("SlabForge BP", "zip", "_intake/stack-bps/PW-SlabForge-Key-BP-v0_1_0.mcpack"),
    ("bridge_companion BP", "zip", "_intake/stack-bps/bridge_companion_BP-v0_1_6.mcpack"),
]
VANILLA_RP = ROOT / "_intake/bedrock-samples/resource_pack"
VANILLA_REG = ROOT / "_intake/vanilla-1.21"          # terrain_texture / item_texture / flipbook_textures / blocks / sound_definitions
SKIP = {"manifest.json", "pack_icon.png", "PW-DEPENDENCIES.md", "README.md", "credits.md", "contents.json", "textures/textures_list.json"}
IMPLICIT_DIRS = ("textures/environment/", "textures/ui/", "textures/gui/", "textures/map/", "textures/misc/", "textures/painting/",
                 "textures/colormap/", "textures/models/armor/", "textures/models/", "font/", "texts/", "ui/", "textures/persona_thumbnails/",
                 "textures/trims/", "textures/particle/particles", "textures/flame_atlas", "textures/forcefield_atlas",
                 "atmospherics/", "lighting/", "water/", "color_grading/", "shadows/", "materials/", "biomes/", "fogs/", "sounds/music/", "textures/items/pw_")
IMPLICIT_FILES = {"blocks.json", "biomes_client.json", "sounds.json", "textures/terrain_texture.json", "textures/item_texture.json",
                  "textures/flipbook_textures.json", "sounds/sound_definitions.json", "splashes.json", "loading_messages.json"}
IMAGE_EXT = (".png", ".tga", ".jpg", ".jpeg")
THEME_OWNER = [   # (regex on path, owner pack prefix) — his rulings; first match wins; only consulted for MULTI-REF ties
    (r"^(particles/|textures/particle/|textures/environment/|fogs/|atmospherics/|lighting/|water/|color_grading/|shadows/|biomes/)", "RP-02"),
    (r"sf_nba", "StripMine RP"),
    (r"^textures/blocks/pw_.*leaves|^textures/blocks/pw_(oak|birch|spruce|jungle|acacia|dark_oak|mangrove|cherry|pale_oak|azalea)_", "RP-01"),
]

def tolerant(t):
    t = t.lstrip("﻿"); t = re.sub(r"//[^\n]*", "", t); t = re.sub(r"/\*.*?\*/", "", t, flags=re.S); t = re.sub(r",(\s*[}\]])", r"\1", t)
    return json.loads(t)

def load_tree(kind, src):
    """rel path -> bytes (and the zip's compressed size when known)."""
    files, csize = {}, {}
    if kind == "dir":
        base = ROOT / src if not str(src).startswith("/") else Path(src)
        for r, _, fs in os.walk(base):
            for f in fs:
                p = Path(r) / f; rel = p.relative_to(base).as_posix()
                files[rel] = p.read_bytes()
    else:
        z = zipfile.ZipFile(ROOT / src if not str(src).startswith("/") else src)
        for i in z.infolist():
            if i.is_dir(): continue
            files[i.filename] = z.read(i.filename); csize[i.filename] = i.compress_size
    return files, csize

def zip_sizes(mcpack):
    if not mcpack or not Path(mcpack).exists(): return {}
    return {i.filename: i.compress_size for i in zipfile.ZipFile(mcpack).infolist() if not i.is_dir()}

def norm(p):
    p = p.replace("\\", "/").lstrip("/")
    for e in IMAGE_EXT + (".json", ".ogg", ".fsb", ".wav"):
        if p.lower().endswith(e): p = p[: -len(e)]; break
    return p

def walk_paths(obj, out):
    """collect every texture path string in a terrain/item texture value (str | list | {path} | {variations:[{path}]})."""
    if isinstance(obj, str): out.add(norm(obj))
    elif isinstance(obj, list):
        for x in obj: walk_paths(x, out)
    elif isinstance(obj, dict):
        if "path" in obj: walk_paths(obj["path"], out)
        if "variations" in obj: walk_paths(obj["variations"], out)
        if "textures" in obj: walk_paths(obj["textures"], out)

def collect_refs(files, name):
    """returns dict: path_refs {normpath: set(kinds)}, keys_defined {terrainkey|itemkey}, ids_defined, ids_referenced, key_refs"""
    R = {"paths": collections.defaultdict(set), "keys": {}, "item_keys": {}, "ids_def": collections.defaultdict(set),
         "ids_ref": collections.defaultdict(set), "key_refs": set(), "item_key_refs": set(), "errors": []}
    def J(rel):
        try: return tolerant(files[rel].decode("utf-8", "replace"))
        except Exception as e: R["errors"].append(f"{rel}: {str(e)[:60]}"); return None
    for rel in files:
        low = rel.lower()
        if rel == "textures/terrain_texture.json" or rel == "textures/item_texture.json":
            j = J(rel)
            if not j: continue
            bucket = R["keys"] if "terrain" in rel else R["item_keys"]
            for k, v in (j.get("texture_data") or {}).items():
                s = set(); walk_paths(v, s); bucket[k] = sorted(s)
                for p in s: R["paths"][p].add("terrain_key:" + k if "terrain" in rel else "item_key:" + k)
        elif rel == "textures/flipbook_textures.json":
            j = J(rel)
            if not isinstance(j, list): continue
            for e in j:
                if isinstance(e, dict) and e.get("flipbook_texture"):
                    R["paths"][norm(e["flipbook_texture"])].add("flipbook:" + str(e.get("atlas_tile")))
                    R["keys"].setdefault(e.get("atlas_tile"), [norm(e["flipbook_texture"])])
        elif rel == "blocks.json":
            j = J(rel)
            if not j: continue
            for b, v in j.items():
                if not isinstance(v, dict): continue
                t = v.get("textures")
                if isinstance(t, str): R["key_refs"].add(t)
                elif isinstance(t, dict):
                    for x in t.values():
                        if isinstance(x, str): R["key_refs"].add(x)
                if v.get("carried_textures"):
                    ct = v["carried_textures"]
                    if isinstance(ct, str): R["key_refs"].add(ct)
                    elif isinstance(ct, dict): R["key_refs"].update(x for x in ct.values() if isinstance(x, str))
        elif rel == "sounds/sound_definitions.json":
            j = J(rel)
            if not j: continue
            defs = j.get("sound_definitions", j)
            for sid, v in defs.items():
                if not isinstance(v, dict): continue
                R["ids_def"]["sound"].add(sid)
                for s in v.get("sounds", []):
                    p = s if isinstance(s, str) else (s.get("name") if isinstance(s, dict) else None)
                    if p: R["paths"][norm(p)].add("sound:" + sid)
        elif rel == "biomes_client.json":
            j = J(rel)
            if j:
                for b, v in (j.get("biomes") or {}).items():
                    if isinstance(v, dict) and v.get("fog_identifier"): R["ids_ref"]["fog"].add(v["fog_identifier"])
        elif low.startswith("fogs/") and low.endswith(".json"):
            j = J(rel)
            if j and "minecraft:fog_settings" in j: R["ids_def"]["fog"].add(j["minecraft:fog_settings"]["description"]["identifier"])
        elif (low.startswith("entity/") or low.startswith("attachables/")) and low.endswith(".json"):
            j = J(rel)
            if not j: continue
            d = (j.get("minecraft:client_entity") or j.get("minecraft:attachable") or {}).get("description", {})
            ident = d.get("identifier", rel)
            R["ids_def"]["entity" if low.startswith("entity/") else "attachable"].add(ident)
            for k, v in (d.get("textures") or {}).items():
                if isinstance(v, str): R["paths"][norm(v)].add(f"entity:{ident}:{k}")
            for k, v in (d.get("geometry") or {}).items():
                if isinstance(v, str): R["ids_ref"]["geometry"].add(v)
            for k, v in (d.get("animations") or {}).items():
                if isinstance(v, str): R["ids_ref"]["animation" if v.startswith("animation.") else "controller"].add(v)
            for e in d.get("animation_controllers") or []:
                if isinstance(e, dict):
                    for v in e.values():
                        if isinstance(v, str): R["ids_ref"]["controller"].add(v)
            for e in d.get("render_controllers") or []:
                if isinstance(e, str): R["ids_ref"]["render_controller"].add(e)
                elif isinstance(e, dict): R["ids_ref"]["render_controller"].update(e.keys())
            for k, v in (d.get("particle_effects") or {}).items():
                if isinstance(v, str): R["ids_ref"]["particle"].add(v)
            for k, v in (d.get("sound_effects") or {}).items():
                if isinstance(v, str): R["ids_ref"]["sound"].add(v)
            se = d.get("spawn_egg") or {}
            if isinstance(se, dict) and se.get("texture"): R["item_key_refs"].add(se["texture"])
        elif low.startswith("particles/") and low.endswith(".json"):
            j = J(rel)
            if not j: continue
            pe = j.get("particle_effect", {}); d = pe.get("description", {})
            if d.get("identifier"): R["ids_def"]["particle"].add(d["identifier"])
            tex = (d.get("basic_render_parameters") or {}).get("texture")
            if isinstance(tex, str): R["paths"][norm(tex)].add("particle:" + str(d.get("identifier")))
        elif low.endswith(".texture_set.json"):
            j = J(rel)
            if not j: continue
            ts = j.get("minecraft:texture_set", {}); base = rel.rsplit("/", 1)[0] if "/" in rel else ""
            for layer, v in ts.items():
                if isinstance(v, str) and not v.startswith("#"):
                    R["paths"][norm(base + "/" + v if base else v)].add("texture_set:" + layer + ":" + rel)
            # the set itself is loaded by the engine next to its colour file: colour's path = set's stem
            R["paths"][norm(rel[: -len(".texture_set.json")])].add("texture_set_self:" + rel)
        elif low.startswith("animations/") and low.endswith(".json"):
            j = J(rel)
            if j:
                for a in (j.get("animations") or {}): R["ids_def"]["animation"].add(a)
        elif low.startswith("animation_controllers/") and low.endswith(".json"):
            j = J(rel)
            if j:
                for a in (j.get("animation_controllers") or {}): R["ids_def"]["controller"].add(a)
        elif low.startswith("render_controllers/") and low.endswith(".json"):
            j = J(rel)
            if j:
                for a in (j.get("render_controllers") or {}): R["ids_def"]["render_controller"].add(a)
        elif low.startswith("models/") and low.endswith(".json"):
            j = J(rel)
            if not j: continue
            if isinstance(j.get("minecraft:geometry"), list):
                for g in j["minecraft:geometry"]:
                    gid = (g.get("description") or {}).get("identifier")
                    if gid: R["ids_def"]["geometry"].add(gid.split(":")[0])
            else:
                for k in j:
                    if k.startswith("geometry."): R["ids_def"]["geometry"].add(k.split(":")[0])
    return R

def bp_refs(files):
    """behaviour-pack references: terrain KEYS (material_instances), geometry ids (blocks), particle ids (scripts + entities)."""
    R = {"key_refs": set(), "item_key_refs": set(), "ids_ref": collections.defaultdict(set), "block_ids": set(), "entity_ids": set()}
    for rel, b in files.items():
        low = rel.lower()
        if low.startswith("blocks/") and low.endswith(".json"):
            try: j = tolerant(b.decode("utf-8", "replace"))
            except Exception: continue
            blk = j.get("minecraft:block", {}); R["block_ids"].add(blk.get("description", {}).get("identifier"))
            def comps(c):
                if not isinstance(c, dict): return
                mi = c.get("minecraft:material_instances") or {}
                for v in mi.values():
                    if isinstance(v, dict) and isinstance(v.get("texture"), str): R["key_refs"].add(v["texture"])
                    elif isinstance(v, str): R["key_refs"].add(v)
                g = c.get("minecraft:geometry")
                if isinstance(g, str): R["ids_ref"]["geometry"].add(g.split(":")[0])
                elif isinstance(g, dict) and isinstance(g.get("identifier"), str): R["ids_ref"]["geometry"].add(g["identifier"].split(":")[0])
            comps(blk.get("components"))
            for p in blk.get("permutations") or []: comps(p.get("components"))
        elif low.startswith("entities/") and low.endswith(".json"):
            try: j = tolerant(b.decode("utf-8", "replace"))
            except Exception: continue
            R["entity_ids"].add(j.get("minecraft:entity", {}).get("description", {}).get("identifier"))
        elif low.startswith("items/") and low.endswith(".json"):
            try: j = tolerant(b.decode("utf-8", "replace"))
            except Exception: continue
            comps = j.get("minecraft:item", {}).get("components", {})
            ic = comps.get("minecraft:icon")
            if isinstance(ic, str): R["item_key_refs"].add(ic)
            elif isinstance(ic, dict):
                t = ic.get("textures", {});
                if isinstance(t, dict): R["item_key_refs"].update(v for v in t.values() if isinstance(v, str))
                elif isinstance(ic.get("texture"), str): R["item_key_refs"].add(ic["texture"])
        elif low.startswith("scripts/") and low.endswith(".js"):
            t = b.decode("utf-8", "replace")
            for m in re.finditer(r"""spawnParticle\(\s*["']([a-z0-9_:.]+)["']""", t): R["ids_ref"]["particle"].add(m.group(1))
            for m in re.finditer(r"""["'](pw:[a-z0-9_]+)["']""", t): R["ids_ref"]["pw_id"].add(m.group(1))
    return R

def img_dims(b):
    try: return Image.open(io.BytesIO(b)).size
    except Exception: return None

def main():
    out_json = sys.argv[sys.argv.index("--json") + 1] if "--json" in sys.argv else str(ROOT / "_logs/ownership_map.json")
    packs, sizes, refs = [], {}, {}
    for name, kind, src, mcpack in STACK:
        files, csz = load_tree(kind, src)
        if not csz: csz = zip_sizes(mcpack)
        packs.append((name, files)); sizes[name] = csz; refs[name] = collect_refs(files, name)
        print(f"{name:22s} {len(files):5d} files  {sum(len(b) for b in files.values())/1e6:7.1f} MB raw  zip-sizes {'yes' if csz else 'NO'}  errors {len(refs[name]['errors'])}")
    # vanilla: registries + entity/particle/attachable references from bedrock-samples
    van_files, _ = load_tree("dir", str(VANILLA_RP))
    for f in ("terrain_texture.json", "item_texture.json", "flipbook_textures.json"):
        van_files["textures/" + f] = (VANILLA_REG / f).read_bytes()
    van_files["blocks.json"] = (VANILLA_REG / "blocks.json").read_bytes(); van_files["sounds/sound_definitions.json"] = (VANILLA_REG / "sound_definitions.json").read_bytes()
    VR = collect_refs(van_files, "vanilla"); refs["vanilla"] = VR
    print(f"vanilla refs: {len(VR['paths'])} paths, {len(VR['keys'])} terrain keys, {len(VR['item_keys'])} item keys, ids {{k: len(v) for k,v in VR['ids_def'].items()}}")
    BR = {}
    for name, kind, src in BPS:
        try: files, _ = load_tree(kind, src)
        except Exception as e: print("BP skip", name, e); continue
        BR[name] = bp_refs(files)
    # key -> referencing sources (RP blocks.json + BP material_instances + entity spawn eggs + BP items)
    key_refs = collections.defaultdict(set); item_key_refs = collections.defaultdict(set)
    for n, R in refs.items():
        for k in R["key_refs"]: key_refs[k].add(n)
        for k in R["item_key_refs"]: item_key_refs[k].add(n)
    for n, R in BR.items():
        for k in R["key_refs"]: key_refs[k].add(n)
        for k in R["item_key_refs"]: item_key_refs[k].add(n)
    # which pack's key definition WINS for each terrain key (top pack first)
    key_owner, item_key_owner = {}, {}
    for name, _ in packs:
        for k in refs[name]["keys"]: key_owner.setdefault(k, name)
        for k in refs[name]["item_keys"]: item_key_owner.setdefault(k, name)
    for k in VR["keys"]: key_owner.setdefault(k, "vanilla")
    for k in VR["item_keys"]: item_key_owner.setdefault(k, "vanilla")
    # ---- per path classification
    holders = collections.defaultdict(dict)       # path -> {pack: bytes}
    for name, files in packs:
        for rel, b in files.items():
            if rel in SKIP or rel.startswith("texts/"): continue
            holders[norm(rel)][name] = (rel, b)
    def implicit(rel):
        return rel in IMPLICIT_FILES or any(rel.startswith(d) for d in IMPLICIT_DIRS) or rel.endswith((".material", ".lang", ".fsb", ".ogg", ".ttf", ".json"))
    rows = []
    for p, hs in holders.items():
        rel0 = next(iter(hs.values()))[0]
        referencing = {n for n, R in refs.items() if p in R["paths"] and n != "vanilla"}
        van = p in VR["paths"]
        imp = implicit(rel0)
        digests = {n: hashlib.md5(b).hexdigest() for n, (r, b) in hs.items()}
        identical = len(set(digests.values())) == 1
        # who references it through a LIVE key (their key wins the merge) vs a dead key (out-ranked by a higher pack's same key)
        live_ref = set()
        for n in referencing:
            kinds = refs[n]["paths"][p]
            for k in kinds:
                if k.startswith("terrain_key:") or k.startswith("flipbook:"):
                    key = k.split(":", 1)[1]
                    if key_owner.get(key) == n: live_ref.add(n)
                elif k.startswith("item_key:"):
                    key = k.split(":", 1)[1]
                    if item_key_owner.get(key) == n: live_ref.add(n)
                else: live_ref.add(n)          # entity / particle / texture_set / sound refs are not key-merged
        holders_ref = live_ref & set(hs)
        if not referencing and not van and not imp: cls = "ORPHAN"
        elif not referencing and (van or imp): cls = "VANILLA/ENGINE-REF"
        elif len(holders_ref) == 1: cls = "OWNED"
        elif len(holders_ref) >= 2: cls = "MULTI-REF"
        elif holders_ref == set() and live_ref: cls = "X-PACK"           # referenced only by non-holders
        else: cls = "DEAD-KEY-ONLY"                                       # referenced only through out-ranked keys
        dims = {n: img_dims(b) for n, (r, b) in hs.items()} if rel0.lower().endswith(IMAGE_EXT) else {}
        owner = None
        if cls == "OWNED": owner = next(iter(holders_ref))
        elif cls in ("MULTI-REF", "VANILLA/ENGINE-REF", "DEAD-KEY-ONLY"):
            for rx, o in THEME_OWNER:
                if re.search(rx, p):
                    cand = [n for n in hs if n.startswith(o)]
                    if cand: owner = cand[0]; break
            if owner is None:
                # propose: larger image > has texture_set > higher pack (first in stack order)
                order = [n for n, _ in packs]
                def score(n):
                    d = dims.get(n); ts = (norm(hs[n][0]) + ".texture_set" ) in refs[n]["paths"] or any(k.startswith("texture_set_self") for k in refs[n]["paths"].get(p, ()))
                    return ((d[0] * d[1]) if d else 0, 1 if ts else 0, -order.index(n))
                owner = max(hs, key=score)
        rows.append({"path": p, "file": rel0, "class": cls, "holders": sorted(hs), "identical": identical, "referencing": sorted(referencing),
                     "live_referencing": sorted(live_ref), "vanilla_ref": van, "implicit": imp, "dims": {n: list(d) if d else None for n, d in dims.items()},
                     "bytes": {n: len(b) for n, (r, b) in hs.items()}, "zip": {n: sizes[n].get(hs[n][0], 0) for n in hs}, "owner": owner,
                     "ref_kinds": {n: sorted(refs[n]["paths"][p])[:6] for n in referencing}})
    # texture sets follow their colour file's owner; a set whose colour file is an ORPHAN is an orphan too
    by_path = {r["path"]: r for r in rows}
    for r in rows:
        if r["file"].endswith(".texture_set.json"):
            col = by_path.get(r["path"][: -len(".texture_set")])
            if col is None: r["class"] = "ORPHAN"; r["owner"] = None
            else: r["class"] = "TEXTURE-SET(" + col["class"] + ")"; r["owner"] = col["owner"]; r["colour_class"] = col["class"]
    # MISSING: referenced by our registries, held by nobody (and not a vanilla path)
    missing = []
    van_paths = set(VR["paths"]) | {norm(r) for r in van_files}
    for n, R in refs.items():
        if n == "vanilla": continue
        for p, kinds in R["paths"].items():
            if p not in holders and p not in van_paths and not p.endswith(".texture_set"):
                missing.append({"path": p, "pack": n, "kinds": sorted(kinds)[:4]})
    # ids: definitions vs references across packs -> dependency edges
    id_def = collections.defaultdict(lambda: collections.defaultdict(set))
    for n, R in refs.items():
        for kind, ids in R["ids_def"].items():
            for i in ids: id_def[kind][i].add(n)
    edges = collections.Counter(); unresolved = collections.defaultdict(list)
    for n, R in list(refs.items()) + [(n, {"ids_ref": B["ids_ref"], "ids_def": {}}) for n, B in BR.items()]:
        if n == "vanilla": continue
        for kind, ids in R["ids_ref"].items():
            if kind == "pw_id": continue
            for i in ids:
                defs = id_def[kind].get(i, set())
                if n in defs: continue
                if defs - {"vanilla"}:
                    for d in defs - {"vanilla"}: edges[(n, d, kind + ("" if "vanilla" not in defs else " (soft: vanilla defines it too)"))] += 1
                elif "vanilla" in defs: continue
                else: unresolved[n].append((kind, i))
    # ---- summaries
    C = collections.Counter(r["class"] for r in rows)
    print("\nCLASSES:", dict(C))
    def mb(x): return f"{x/1e6:.1f} MB"
    # shadows: for OWNED/MULTI-REF/etc, every holder that is not the owner
    shadow_ident = collections.Counter(); shadow_diff = collections.Counter(); shadow_bytes = collections.Counter()
    for r in rows:
        if r["class"] in ("ORPHAN",): continue
        for h in r["holders"]:
            if h != r["owner"] and r["owner"]:
                (shadow_ident if r["identical"] else shadow_diff)[(h, r["owner"])] += 1; shadow_bytes[h] += r["bytes"][h]
    print("\nIDENTICAL SHADOWS (holder > owner): safe deletes")
    for (h, o), c in shadow_ident.most_common(20): print(f"  {c:5d}  {h}  (owner {o})")
    print("DIFFERING SHADOWS (holder > owner): decisions")
    for (h, o), c in shadow_diff.most_common(20): print(f"  {c:5d}  {h}  (owner {o})")
    print("\nORPHANS by pack:")
    orph = collections.defaultdict(lambda: [0, 0])
    for r in rows:
        if r["class"] == "ORPHAN":
            for h in r["holders"]: orph[h][0] += 1; orph[h][1] += r["bytes"][h]
    for h, (c, b) in sorted(orph.items(), key=lambda x: -x[1][1]): print(f"  {c:5d} files {mb(b):>10s}  {h}")
    print("\nX-PACK (referenced by a pack that does not hold it):")
    xp = collections.Counter()
    for r in rows:
        if r["class"] == "X-PACK":
            for n in r["live_referencing"]: xp[(n, "+".join(r["holders"]))] += 1
    for (n, hs), c in xp.most_common(): print(f"  {c:5d}  {n} -> held by {hs}")
    print(f"\nMISSING (referenced, held by nobody, not vanilla): {len(missing)}")
    by = collections.Counter(m["pack"] for m in missing)
    for n, c in by.most_common(): print(f"  {c:5d}  {n}   e.g. {[m['path'] for m in missing if m['pack']==n][:3]}")
    print("\nMULTI-REF (two holders both reference it from live registries):")
    mr = collections.Counter()
    for r in rows:
        if r["class"] == "MULTI-REF": mr[("+".join(sorted(set(r['live_referencing']) & set(r['holders']))), "identical" if r["identical"] else "DIFFERING")] += 1
    for k, c in mr.most_common(): print(f"  {c:5d}  {k}")
    print("\nID DEPENDENCY EDGES (referencing pack -> defining pack, kind): count")
    for (a, b, k), c in sorted(edges.items(), key=lambda x: -x[1]): print(f"  {c:5d}  {a} -> {b}  [{k}]")
    print("\nUNRESOLVED ids (not defined anywhere incl. vanilla):")
    for n, l in unresolved.items(): print(f"  {n}: {len(l)}  e.g. {l[:4]}")
    C = collections.Counter(r["class"] for r in rows)
    print("\nCLASSES (after texture-set attribution):", dict(C))
    # ---- size projection: keep only owner copies (+ VANILLA/ENGINE-REF & X-PACK stay with their holders for now), drop ORPHANs and shadows
    proj = collections.defaultdict(lambda: [0, 0, 0, 0])   # pack -> [raw_before, zip_before, raw_after, zip_after]
    for name, files in packs:
        for rel, b in files.items():
            proj[name][0] += len(b); proj[name][1] += sizes[name].get(rel, int(len(b) * 0.98))
    for r in rows:
        for h in r["holders"]:
            keep = (r["class"] == "ORPHAN" and False) or (r["owner"] == h) or (r["class"] in ("X-PACK",) )
            if keep: proj[h][2] += r["bytes"][h]; proj[h][3] += r["zip"][h] or int(r["bytes"][h] * 0.98)
    for name, files in packs:   # non-classified files (manifest, texts, SKIP) stay
        for rel, b in files.items():
            if rel in SKIP or rel.startswith("texts/"): proj[name][2] += len(b); proj[name][3] += sizes[name].get(rel, len(b))
    print("\nSIZE PROJECTION (before -> after the proposal; raw / zip):")
    for n, (rb, zb, ra, za) in proj.items(): print(f"  {n:22s} {mb(rb):>9s} / {mb(zb):>9s}  ->  {mb(ra):>9s} / {mb(za):>9s}")
    m34 = [0, 0]
    for r in rows:
        for h in r["holders"]:
            if h.startswith(("RP-03", "RP-04")) and (r["owner"] == h or r["class"] == "X-PACK"): m34[0] += r["bytes"][h]; m34[1] += r["zip"][h] or int(r["bytes"][h] * 0.98)
    print(f"\nRP-03 + RP-04 MERGED (owner copies only, orphans + shadows gone): {mb(m34[0])} raw / {mb(m34[1])} zip   (his rule: one pack iff < 250 with reasonable room)")
    json.dump({"rows": rows, "missing": missing, "edges": [[a, b, k, c] for (a, b, k), c in edges.items()], "unresolved": {n: l for n, l in unresolved.items()},
               "projection": proj, "merged_rp03_rp04": m34, "classes": dict(C), "key_owner_counts": dict(collections.Counter(key_owner.values()))}, open(out_json, "w"), indent=0)
    print("written", out_json)

if __name__ == "__main__":
    main()
