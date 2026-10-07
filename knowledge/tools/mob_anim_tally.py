#!/usr/bin/env python3
"""mob_anim_tally.py — D-C283 (his 13:01 "a tally of all of our mobs and animations and whether we can reference better
animations to mobs that are using lesser quality animations").

For every client entity our resource packs define (RP-06 1.4.15, RP-07 1.4.21, RP-08 1.4.8 builds), one row:
  model   where its default geometry comes from:
          CONVERTER-B (Patrix JEM, rebuilt by Converter B: identifiers in any build_*_report.json) · CONVERTER-A (a .patrix / pw_
          geometry never rebuilt by B) · APRIL (the April 2026 v1.8 rigs: Root/upper_body hierarchy or *.v1.8 ids) ·
          SF_NBA (the Naturalist-style creature pack) · VANILLA (not defined in our packs: the game's own)
  anims   every animation id in its map, classed: JEM-FULL (a whole Patrix animation ported: jem_anim_port) · JEM-PARTIAL (walk terms
          only: pw_spider.walk) · PW (our hand-made: look, steer, squid pulse, ambient) · APRIL · SF_NBA · VANILLA
  jem     the Patrix JEM that belongs to it, and how rich its animation is (assignment count; FreshLX writes Fresh-Animations-style
          idle/walk/look/hurt/death motion)
  upgrade what a switch to the full Patrix animation needs: READY (model already Converter B from that JEM: port only, S) ·
          REBUILD+PORT (model must be rebuilt by Converter B first, M) · NONE (no Patrix JEM, or already full)
Output: _docs/convb/mob_anim_tally.json + .csv"""
import csv, glob, json, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import molang_lint as ML

ROOT = Path("/home/claude")
PACKS = [("RP-06", ROOT / "_build/rp06-1415"), ("RP-07", ROOT / "_build/rp07-1421"), ("RP-08", ROOT / "_build/rp08-148")]
VAN = ROOT / "_intake/bedrock-samples/resource_pack"
CEM = ROOT / "_intake/patrix-mobs/assets/minecraft/optifine/cem"
JEM_OF = {"villager_v2": "villager", "zombie_villager_v2": "zombie_villager", "zombie_pigman": "zombified_piglin",
          "evocation_illager": "evoker", "tropicalfish": "tropical_fish_a", "pufferfish": "puffer_fish_big",
          "magma_cube": "magma_cube", "vindicator": "vindicator", "wither_skeleton": "wither_skeleton"}


def load(p):
    try: return ML._parse_json(Path(p).read_text(encoding="utf-8-sig"))
    except Exception: return None


def jem_richness(stem):
    f = CEM / f"{stem}.jem"
    if not f.exists(): return None
    d = load(f) or {}
    n = sum(len(a) for m in d.get("models", []) for a in (m.get("animations") or []))
    parts = len({k.split(".")[0] for m in d.get("models", []) for a in (m.get("animations") or []) for k in a
                 if "." in k and not k.startswith(("var.", "varb.", "render."))})
    return {"jem": stem, "assignments": n, "parts_animated": parts}


def main():
    cb_ids = set()
    for f in glob.glob(str(ROOT / "_docs/convb/build_*report.json")):
        for r in (load(f) or {}).values():
            if isinstance(r, dict) and r.get("identifier"): cb_ids.add(r["identifier"])
    geo_src, anim_def = {}, {}
    for tag, root in PACKS:
        for f in glob.glob(str(root / "models/entity/**/*.json"), recursive=True):
            d = load(f) or {}
            for g in d.get("minecraft:geometry", []) or []:
                ident = g["description"]["identifier"]; names = {b["name"] for b in g.get("bones", [])}
                geo_src.setdefault(ident, (tag, names, Path(f).name))
            for k, v in d.items():
                if k.startswith("geometry.") and isinstance(v, dict): geo_src.setdefault(k.split(":")[0], (tag, {b["name"] for b in v.get("bones", [])}, Path(f).name))
        for f in glob.glob(str(root / "animations/**/*.json"), recursive=True):
            for k in ((load(f) or {}).get("animations") or {}): anim_def.setdefault(k, (tag, Path(f).name))
    van_anims = set()
    for f in glob.glob(str(VAN / "animations/*.json")):
        van_anims |= set(((load(f) or {}).get("animations") or {}).keys())

    def model_class(ident):
        if ident in cb_ids: return "CONVERTER-B"
        if ident not in geo_src: return "VANILLA"
        tag, names, fname = geo_src[ident]
        if "sf_nba" in ident or "sf_nba" in fname: return "SF_NBA"
        if ".patrix" in ident or ident.startswith("geometry.pw_"): return "CONVERTER-A"
        if "v1.8" in ident or {"Root", "upper_body"} <= names: return "APRIL"
        return "OURS-OTHER"

    def anim_class(aid):
        if aid.startswith("controller."): return None
        if aid == "animation.pw_spider.walk": return "JEM-PARTIAL"
        if aid in ("animation.pw_silverfish.jem", "animation.pw_enderman.jaw"): return "JEM-FULL" if "silverfish" in aid else "JEM-PART(jaw)"
        if ".pw_" in aid or aid.startswith("animation.pw_") or ".pw." in aid: return "PW"
        if "sf_nba" in aid: return "SF_NBA"
        if aid in anim_def:
            f = anim_def[aid][1]
            if "v1.8" in aid or "v1.8" in f or re.search(r"\.(base|walking|angry_|attack_time|facial)", aid): return "APRIL"
            return "OURS" if aid not in van_anims else "VANILLA(override)"
        return "VANILLA" if aid in van_anims else "MISSING"

    rows = []
    for tag, root in PACKS:
        for f in sorted(glob.glob(str(root / "entity/*.json"))):
            d = load(f) or {}
            desc = (d.get("minecraft:client_entity") or {}).get("description") or {}
            ident = desc.get("identifier")
            if not ident: continue
            geo = (desc.get("geometry") or {}).get("default") or next(iter((desc.get("geometry") or {}).values()), "")
            amap = desc.get("animations") or {}
            classes = {}
            for short, aid in amap.items():
                c = anim_class(aid)
                if c: classes.setdefault(c, []).append(short)
            stem = ident.split(":")[1]
            jem = jem_richness(JEM_OF.get(stem, stem)) if ident.startswith("minecraft:") else None
            mc = model_class(geo)
            full = "JEM-FULL" in classes
            if not jem or full: up = "NONE"
            elif mc == "CONVERTER-B": up = "READY (port only, S)"
            else: up = "REBUILD+PORT (M)"
            rows.append({"pack": tag, "entity": ident, "model": mc, "geometry": geo,
                         "anims": {k: sorted(v) for k, v in sorted(classes.items())},
                         "n_anims": sum(len(v) for v in classes.values()),
                         "jem": jem["jem"] if jem else "", "jem_assignments": jem["assignments"] if jem else 0,
                         "jem_parts_animated": jem["parts_animated"] if jem else 0, "upgrade": up})
    json.dump(rows, open(ROOT / "_docs/convb/mob_anim_tally.json", "w"), indent=1)
    with open(ROOT / "_docs/convb/mob_anim_tally.csv", "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["pack", "entity", "model source", "animation sources (short names)", "Patrix JEM", "JEM assignments",
                    "JEM parts animated", "upgrade path"])
        for r in rows:
            w.writerow([r["pack"], r["entity"], r["model"], "; ".join(f"{k}: {len(v)}" for k, v in r["anims"].items()),
                        r["jem"], r["jem_assignments"], r["jem_parts_animated"], r["upgrade"]])
    from collections import Counter
    print("entities:", len(rows))
    print("model sources:", Counter(r["model"] for r in rows))
    print("upgrade:", Counter(r["upgrade"] for r in rows))
    for r in rows:
        if r["entity"].startswith("minecraft:"):
            print(f"{r['pack']} {r['entity']:28} {r['model']:12} {', '.join(f'{k}:{len(v)}' for k, v in r['anims'].items()):55} "
                  f"{r['jem']:18} {r['jem_assignments']:4} {r['upgrade']}")


if __name__ == "__main__":
    main()
