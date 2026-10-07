#!/usr/bin/env python3
"""build_rp07_1419.py — D-C277 (his 09-28 23:34 GO "absolutely fix this and check for similar unseen issues across all mobs").
RP-07 Neutral Mobs RP v1.4.19 from v1.4.18:
  1. WHOLE-MOB SIZE (client-entity scripts.scale; Bedrock draws geometry x client scale x behavior minecraft:scale):
       horse 1.1, donkey 0.87, mule 0.92 — Java HorseRenderer / DonkeyRenderer / MuleRenderer scales (FreshLX root.ty -2.4 / +3 / +2
       = 24(1 - s) exactly; vanilla Bedrock donkey_v3 / mule_v3 carry 0.87 / 0.92). Our entities had none: horse 10 % small,
       donkey 15 % / mule 9 % big (the donkey stood taller than the horse).
       cat: the "0.8" (Java CatRenderer) REMOVED — the vanilla cat BEHAVIOR already scales the adult 0.8 (minecraft:cat_adult), so
       ours drew 0.8 x 0.8 = 0.64 (20 % small). Babies follow: behavior 0.5 (cat 0.4) x the client scale, as in Java.
  2. CONVERTER B (bake + binds + Java parents + frames):
       spider (geometry.spider lives here; the entity is RP-06's): 8 splayed Patrix legs, head with jaws + palps, abdomen; the neck
         part (scaled 0.8 in Java) carries the whole model; hips moved out of the thorax and each foot-anchored leg chain hung from its
         hip so our walk cycles swing whole legs; Root / body / body0 / body1 / head / fangs bound to the matching Patrix parts.
       bee: the Java bone > body tree restored (the Patrix bee lives in `torso`, a CHILD of the randomly-scaled root — median 0.85):
         whole bee 0.85 like Java; wings, feelers and the three leg pairs bound (leg pairs grouped under one bone each).
       tadpole: body at its runtime pivot (+0.5 y, -2 z) and scaled 0.5 (the April build drew it 2x tall).
       zombified piglin (re-bake): the Java head > hat tree — the Patrix head (in the hat part) now carries the FreshLX head tilt
         (8.9 deg forward, 14.9 deg sideways) like Java; 1.4.17 stood it upright.
  manifest 1.4.19, uuid kept. verify: verify_rp07_1419.py."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R

ROOT = Path("/home/claude")
SCALES = {"horse": "1.1", "donkey": "0.87", "mule": "0.92"}
REMOVE_SCALE = {"cat"}


def scale_fixes(dst):
    done = {}
    for stem, s in SCALES.items():
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        assert "scale" not in desc.get("scripts", {}), (stem, desc["scripts"].get("scale"))
        desc.setdefault("scripts", {})["scale"] = s; R.wj(pe, d); done[stem] = s
    for stem in REMOVE_SCALE:
        pe = dst / f"entity/{stem}.entity.json"; d = R.jl(pe); desc = d["minecraft:client_entity"]["description"]
        assert desc["scripts"].get("scale") == "0.8", (stem, desc["scripts"].get("scale"))
        del desc["scripts"]["scale"]; R.wj(pe, d); done[stem] = "removed (behavior 0.8 applies)"
    return done


def verify_scales(cfg, check):
    NEW, OLD = cfg["dst"], cfg["src"]
    rows, ok = [], True
    for stem in list(SCALES) + sorted(REMOVE_SCALE):
        n = R.jl(NEW / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        o = R.jl(OLD / f"entity/{stem}.entity.json")["minecraft:client_entity"]["description"]
        want = SCALES.get(stem)
        got = n.get("scripts", {}).get("scale")
        same_rest = ({k: v for k, v in n.items() if k != "scripts"} == {k: v for k, v in o.items() if k != "scripts"}
                     and {k: v for k, v in n["scripts"].items() if k != "scale"} == {k: v for k, v in o["scripts"].items() if k != "scale"})
        ok &= (got == want) and same_rest
        rows.append(f"{stem} {o.get('scripts', {}).get('scale')} -> {got}{'' if same_rest else ' (OTHER KEYS CHANGED)'}")
    check("S1 whole-mob scales", ok, "; ".join(rows))


CFG = {
    "src": ROOT / "_build/rp07-1418", "dst": ROOT / "_build/rp07-1419", "version": "1.4.19",
    "name": "AbsolutRealism Neutral Mobs RP v1.4.19",
    "desc": ("v1.4.19 (2026-09-29) SIZES + CONVERTER B ROUND 5 (D-C277): horse drawn at Java's 1.1x, donkey 0.87x, mule 0.92x, cat back "
             "to Java's size (was drawn 0.64x); spider, bee and tadpole rebuilt from the Patrix models; zombified piglin head keeps "
             "its Java tilt. Everything else byte-identical to v1.4.18."),
    "jobs": [("spider", "spider", "default", "spider", "default"), ("bee", "bee", "default", "bee", "default"),
             ("tadpole", "tadpole", "default", "tadpole", "default"),
             ("zombified piglin", "zombie_pigman", "default", "zombified_piglin", "default")],
    "entity_src": {"spider": ROOT / "_build/rp06-1411"},
    "look": {},
    "post": [scale_fixes],
    "extra_changed": [f"entity/{s}.entity.json" for s in list(SCALES) + sorted(REMOVE_SCALE)],
    "verify_hooks": [verify_scales],
    "unbound_ok": {"bee": {"eyeball_left", "eyeball_right", "eyelid_left", "eyelid_right"},
                   "zombified piglin": {"leftForearm", "rightForearm", "leftShin", "rightShin"}},
    "placement": {"spider": ("ground",), "bee": ("old",), "tadpole": ("old",), "zombified piglin": ("ground",)},
    "report": ROOT / "_docs/convb/build_1419_report.json",
}

if __name__ == "__main__":
    R.build(CFG)
