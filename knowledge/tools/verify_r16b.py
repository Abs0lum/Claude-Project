#!/usr/bin/env python3
"""verify_r16b.py — gate for R16b (build_r16b.py): RP-06 1.4.23 + RP-07 1.4.29. Static checks only rule OUT (P1).
Standing Converter B round gate (convb_round.verify: changed / added sets, strict JSON, manifest, culling boxes, cubes == bake,
texture size, placement, joints, binds, frames, Molang grammar, animation resolution, render-controller visibility, format
sections, read-before-write, attachables) PLUS per ported mob, on the SHIPPED files (geometry, animation, entity scripts):
  N2  Molang == JEM on every driven channel, every state case (rotation <= 0.01 deg, position / scale <= 0.001)
  N3  the shipped rest geometry posed by the shipped animation == the JEM baked at that pose (every cube corner <= 0.01 px)
  W   the entity drives pw_jem only; its pre_animation starts with the Java seeds; scale script + render controllers + textures
      kept (the golem's damage overlays = the Patrix crackiness sheets); min_engine_version 1.21.0"""
import json, math, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import r16b
import build_r16b as BR

ROOT = Path("/home/claude")


def shipped(cfg, label):
    stem, ident = {**BR.SPEC6, **BR.SPEC7}[label]
    dst = cfg["dst"]
    ent = ML._parse_json((dst / f"entity/{stem}.entity.json").read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]
    _, g = R.geo_file(dst, ident)
    anim = R.jl(dst / f"animations/pw_{label}_jem.animation.json")["animations"][BR.anim_id(label)]
    return ent, g, anim


def hook_for(spec):
    def hook(cfg, check):
        for label, (stem, ident) in spec.items():
            ent, g, anim = shipped(cfg, label)
            init, pre = ent["scripts"]["initialize"], ent["scripts"]["pre_animation"]
            r16b.bake(label)                                     # the pivot rule + Java rest seeds the build used
            w2 = r16b.n2(label, init, pre, anim)
            check(f"N2 {label} Molang == JEM ({len(r16b.cases(label))} state cases)", w2["rotation"] <= 0.01 and w2["position"] <= 1e-3 and w2["scale"] <= 1e-3,
                  f"worst rotation {w2['rotation']:.5f} deg, position {w2['position']:.5f} px, scale {w2['scale']:.5f}")
            w3, per = r16b.n3(label, g["bones"], init, pre, anim)
            worst = max(per, key=lambda x: x[0])
            check(f"N3 {label} shipped geometry posed by the shipped animation == the JEM at that pose", w3 <= 0.01,
                  f"worst corner {w3:.4f} px over {len(per)} cases ({worst[2]} cubes compared); worst case {({k: v for k, v in worst[1].items() if k.startswith('_') or k in ('limb_speed', 'is_in_water', 'is_sitting')})}")
            old = ML._parse_json((cfg["src"] / f"entity/{stem}.entity.json").read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]
            seeds = [s for s in pre if s.split("=")[0].strip().startswith(f"v.{r16b.MOBS[label]['prefix']}_") and any(
                s.startswith(f"v.{r16b.MOBS[label]['prefix']}_{part}_") for part in r16b.MOBS[label]["seeds"])]
            want_tex = dict(old["textures"])
            if label == "iron_golem": want_tex.update(BR.GOLEM_OVERLAYS)
            ok = (ent["animations"] == {"pw_jem": BR.anim_id(label)} and ent["scripts"]["animate"] == ["pw_jem"] and "animation_controllers" not in ent
                  and ent["scripts"].get("scale") == (old.get("scripts") or {}).get("scale") and ent["render_controllers"] == old["render_controllers"]
                  and ent["textures"] == want_tex and ent.get("materials") == old.get("materials") and ent.get("min_engine_version") == "1.21.0"
                  and ent["geometry"] == {"default": ident} and len(seeds) >= sum(len(d) for d in r16b.MOBS[label]["seeds"].values()))
            check(f"W {label} entity: pw_jem only, Java seeds first, scale / render controllers / materials kept, textures as planned, mev 1.21.0", ok,
                  f"animate {ent['scripts']['animate']}; scale {ent['scripts'].get('scale')}; seeds {len(seeds)}; textures {'as planned' if ent['textures'] == want_tex else 'DIFFER'}")
    return hook


def main():
    rc = 0
    for cfg, spec in ((BR.CFG6, BR.SPEC6), (BR.CFG7, BR.SPEC7)):
        BR.finish(cfg)
        cfg["verify_hooks"] = [hook_for(spec)]
        if "iron_golem" in spec:
            cfg["textures_changed"] = {"iron_golem": {**ML._parse_json((cfg["src"] / "entity/iron_golem.entity.json").read_text(encoding="utf-8"))["minecraft:client_entity"]["description"]["textures"], **BR.GOLEM_OVERLAYS}}
        files = json.load(open(ROOT / f"_docs/r16b/build_rp0{'6' if cfg is BR.CFG6 else '7'}_files.json"))
        cfg["extra_changed"], cfg["extra_added"], cfg["extra_removed"] = files["changed"], files["added"], files["removed"]
        print(f"\n===== {cfg['dst'].name} =====")
        rc |= R.verify(cfg)
    print(f"\nR16b {'GATE OPEN' if rc == 0 else 'GATE CLOSED'}")
    sys.exit(rc)


if __name__ == "__main__":
    main()
