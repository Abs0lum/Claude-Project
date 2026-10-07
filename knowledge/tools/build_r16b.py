#!/usr/bin/env python3
"""build_r16b.py — R16b (D-C314, his "Go on all" item 2 = the Patrix fidelity round): FreshLX's WHOLE animation on the Patrix
26.2 models (FA-1 method), research sheet _docs/r16b/R16B-RESEARCH.md, port + gates in tools/r16b.py.
  RP-06 1.4.23 (from 1.4.22): HOGLIN, ZOGLIN
  RP-07 1.4.29 (from 1.4.28): FOX, GOAT, CAT, OCELOT (its own geometry.pw_ocelot now: the ocelot JEM is not the cat's),
                              COD, IRON GOLEM (geometry.pw_iron_golem replaces the old custom model; the Patrix crackiness sheets
                              already in the pack become its damage overlays - the old 128 px overlays were drawn for the old model)
Per mob: Converter B bake of the JEM (every top-level part whose t* FreshLX assigns at its runtime pivot; the fox body at Java's
pivot + 90 deg), `animation.pw_<mob>.jem` = every JEM channel as the difference from that rest, the Java seeds + Bedrock queries
at the top of pre_animation (r16b.MOBS), the entity drives only pw_jem (the grafted ar_* / pw_ambient / Mojang animations leave),
render controllers, textures (except the golem overlays), materials and size scripts unchanged. Babies = the adult pose scaled by
the BP, as shipped. verify: verify_r16b.py"""
import json, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import convb_build as CB
import molang_lint as ML
import r16b
import build_rp06_1420 as B6

ROOT = Path("/home/claude")
CHANGED6, ADDED6, REMOVED6 = [], [], []
CHANGED7, ADDED7, REMOVED7 = [], [], []

# label -> (stem, geometry id, the old geometry file to empty first (None = a new id))
SPEC6 = {"hoglin": ("hoglin", "geometry.hoglin.patrix"), "zoglin": ("zoglin", "geometry.zoglin.patrix")}
SPEC7 = {"fox": ("fox", "geometry.pw_fox"), "goat": ("goat", "geometry.pw_goat"), "cat": ("cat", "geometry.pw_cat"),
         "ocelot": ("ocelot", "geometry.pw_ocelot"), "cod": ("cod", "geometry.cod.patrix"), "iron_golem": ("iron_golem", "geometry.pw_iron_golem")}
GOLEM_OVERLAYS = {"cracked_high": "textures/entity/iron_golem/iron_golem_crackiness_high",
                  "cracked_med": "textures/entity/iron_golem/iron_golem_crackiness_medium",
                  "cracked_low": "textures/entity/iron_golem/iron_golem_crackiness_low"}
PORTS = {}          # label -> (bones, init, pre, anim, report) - filled in the pre hooks, read by the gate
CB.NO_LEG_RELOCATE |= {"fox", "goat"}          # their leg1..4 rest pose + pivot are what the port's animation is measured from


def anim_id(m):
    return f"animation.pw_{m}.jem"


def placeholder(dst, ident, files):
    """empty the geometry the job will rebuild (or create it): the binder must not see the old bones (their leg0..3 quadrant rule
    would rename the JEM's leg1..4)"""
    try:
        p, _ = R.geo_file(dst, ident); new = False
    except FileNotFoundError:
        p = dst / f"models/entity/{ident.replace('geometry.', '').replace('.', '_')}.geo.json"; new = True
    R.wj(p, {"format_version": "1.16.0", "minecraft:geometry": [{"description": {"identifier": ident, "texture_width": 64, "texture_height": 64},
                                                                  "bones": [{"name": "placeholder_bone", "pivot": [0, 0, 0], "cubes": []}]}]})
    rel = str(p.relative_to(dst))
    if new: files[1].append(rel)
    return rel, new


def setup(dst, label, stem, ident, files):
    b, tw, th, init, pre, anim, rep = r16b.port(label)
    PORTS[label] = (b, init, pre, anim, rep)
    pa = dst / f"animations/pw_{label}_jem.animation.json"; assert not pa.exists(), pa
    R.wj(pa, {"format_version": "1.8.0", "animations": {anim_id(label): anim}}); files[1].append(str(pa.relative_to(dst)))
    pe = dst / f"entity/{stem}.entity.json"; v = ML._parse_json(pe.read_text(encoding="utf-8"))
    desc = v["minecraft:client_entity"]["description"]
    scale = (desc.get("scripts") or {}).get("scale")
    desc["geometry"] = {"default": ident}
    desc["animations"] = {"pw_jem": anim_id(label)}
    desc.pop("animation_controllers", None)
    desc["scripts"] = {"initialize": init, "pre_animation": pre, "animate": ["pw_jem"], **({"scale": scale} if scale is not None else {})}
    desc["min_engine_version"] = "1.21.0"             # L-ENT-PREC: never tie with vanilla (the golem was unpinned)
    if tuple(int(x) for x in v["format_version"].split(".")) < (1, 10, 0): v["format_version"] = "1.10.0"
    if label == "iron_golem":
        for k, t in GOLEM_OVERLAYS.items():
            assert desc["textures"].get(k), (k, desc["textures"]); assert (dst / f"{t}.png").exists(), t
            desc["textures"][k] = t
    R.wj(pe, v); files[0].append(f"entity/{stem}.entity.json")
    rel, new = placeholder(dst, ident, files)
    if not new: files[0].append(rel)
    return f"{stem}: {ident} + {anim_id(label)} ({len(pre)} statements, {len(anim['bones'])} driven bones; pruned {rep.get('pruned')})"


def hooks(spec, files):
    out = []
    for label, (stem, ident) in spec.items():
        def h(dst, label=label, stem=stem, ident=ident): return setup(dst, label, stem, ident, files)
        h.__name__ = f"setup_{label}"; out.append(h)
    return out


def hierarchy_for(spec):
    def hierarchy(dst):
        """the golem's JEM `root` + the Java renderer bones (cat lie-down roll, cod wiggle + flop, golem walk sway) above the model"""
        out = []
        for label, (stem, ident) in spec.items():
            extra = (["root"] if r16b.MOBS[label].get("root") else []) + r16b.render_names(label)
            if not extra: continue
            p, g = R.geo_file(dst, ident); assert not set(extra) & {b["name"] for b in g["bones"]}
            g["bones"] = r16b.hierarchy(label, g["bones"])
            d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d); out.append(f"{label}: {extra}")
        return "above the model: " + "; ".join(out)
    hierarchy.__name__ = "hierarchy"
    return hierarchy


def carry_locators_for(spec):
    def carry(dst):
        """Mojang's locators (lead ...) onto the same-named bones of the new geometry, same coordinates (D-C301)"""
        out, skipped = {}, []
        for label, (stem, ident) in spec.items():
            van = ML._parse_json((B6.VRP / f"entity/{stem}.entity.json").read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]["geometry"]
            vid = van.get("default")
            p, g = R.geo_file(dst, ident); by = {b["name"]: b for b in g["bones"]}
            try: vb = B6.vgeo(vid)[0]
            except KeyError: skipped.append(f"{label}: no Mojang geometry {vid}"); continue
            for x in vb:
                for loc, xyz in (x.get("locators") or {}).items():
                    if x["name"] not in by: skipped.append(f"{label}:{x['name']}.{loc}"); continue
                    by[x["name"]]["locators"] = {**(by[x["name"]].get("locators") or {}), loc: [float(q) for q in (xyz if isinstance(xyz, list) else xyz.get("offset", [0, 0, 0]))]}
                    out.setdefault(label, []).append(f"{x['name']}.{loc}")
            d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
        return f"locators carried {out}; skipped {skipped}"
    carry.__name__ = "carry_locators"
    return carry


def jobs(spec):
    return [(label, stem, "default", label, label) for label, (stem, ident) in spec.items()]


def exempt(spec):
    return {label: {x["name"] for x in r16b.bake(label)[0]} | {"root"} | set(r16b.render_names(label)) for label in spec}


PLACEMENT = {"hoglin": ("ground",), "zoglin": ("ground",), "fox": ("ground",), "goat": ("ground",), "cat": ("ground",), "ocelot": ("ground",),
             "cod": ("old",), "iron_golem": ("ground",)}

CFG6 = {
    "src": ROOT / "_build/rp06-1422", "dst": ROOT / "_build/rp06-1423", "version": "1.4.23",
    "name": "AbsolutRealism Hostile Mobs RP v1.4.23",
    "desc": ("v1.4.23 (2026-09-30) R16b: the hoglin and zoglin move with the Patrix model's own animation (walk / run, head sniffing, ear "
             "flicks, the charge). Includes all of 1.4.22."),
    "pre": hooks(SPEC6, (CHANGED6, ADDED6)), "jobs": jobs(SPEC6), "look": {}, "frame_exempt": None, "unbound_ok": {"hoglin": set(), "zoglin": set()},
    "placement": {k: PLACEMENT[k] for k in SPEC6}, "post": [carry_locators_for(SPEC6)],
    "ground_tol": {m: (-1.2, "FreshLX's idle legs tilt 2 deg + splay: a toe corner sinks 1.09 px, exactly as the JEM places it in Java (N3)") for m in ("hoglin", "zoglin")}, "extra_changed": CHANGED6, "extra_added": ADDED6,
    "extra_removed": REMOVED6, "ars_tag": "RP-06", "ars_stack": [ROOT / "_build/rp07-1428"], "verify_hooks": [],
    "report": ROOT / "_docs/r16b/build_rp06_1423_report.json",
}
CFG7 = {
    "src": ROOT / "_build/rp07-1428", "dst": ROOT / "_build/rp07-1429", "version": "1.4.29",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.29",
    "desc": ("v1.4.29 (2026-09-30) R16b: the fox, goat, cat, ocelot, cod and iron golem move with their Patrix models' own animation "
             "(fox sit / sleep / stalk, cat sit / lie down / sneak / sprint, goat ram / jump / nibble, the golem's weighty walk, "
             "flower offer and attack; the golem's cracks follow its new model). Includes all of 1.4.28."),
    "pre": hooks(SPEC7, (CHANGED7, ADDED7)), "jobs": jobs(SPEC7), "look": {}, "frame_exempt": None,
    "unbound_ok": {k: set(r16b.render_names(k)) | ({"root"} if r16b.MOBS[k].get("root") else set()) for k in SPEC7},
    "placement": {k: PLACEMENT[k] for k in SPEC7}, "post": [hierarchy_for(SPEC7), carry_locators_for(SPEC7)],
    "extra_changed": CHANGED7, "extra_added": ADDED7, "extra_removed": REMOVED7,
    "textures_changed": {"iron_golem": None}, "ars_tag": "RP-07", "ars_stack": [ROOT / "_build/rp06-1423"], "verify_hooks": [],
    "report": ROOT / "_docs/r16b/build_rp07_1429_report.json",
}


def finish(cfg):
    cfg["frame_exempt"] = exempt({j[0]: None for j in cfg["jobs"]})


if __name__ == "__main__":
    (ROOT / "_docs/r16b").mkdir(parents=True, exist_ok=True)
    which = sys.argv[1:] or ["6", "7"]
    for tag, cfg in (("6", CFG6), ("7", CFG7)):
        if tag not in which: continue
        finish(cfg)
        R.build(cfg)
        ch, ad, rm = (CHANGED6, ADDED6, REMOVED6) if tag == "6" else (CHANGED7, ADDED7, REMOVED7)
        json.dump({"changed": sorted(set(ch)), "added": sorted(set(ad)), "removed": rm, "ports": {k: v[4].get("pruned") for k, v in PORTS.items()}},
                  open(ROOT / f"_docs/r16b/build_rp0{tag}_files.json", "w"), indent=1)
