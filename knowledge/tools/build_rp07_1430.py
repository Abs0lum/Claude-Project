#!/usr/bin/env python3
"""build_rp07_1430.py — RP-07 Neutral Mobs RP v1.4.30 from v1.4.29 (D-C315, his "if we can fix it, I want to fix it"): the FOX's
Java renderer move. FoxRenderer.setupRotations pitches the whole fox by its xRot while pouncing and while faceplanted in snow; the
R16b port lacked it (the only pw_jem mob that did — census D-C315). Now: `pw_render` above the model at the entity origin,
pitch = Mojang's own approximations (pounce: vertical speed * -7 deg, latched from wiggle / stalk like Mojang's fox controller;
stuck in snow: 60 deg). Everything else byte-identical to 1.4.29. HELD with his p13 results (rides with any p13 fixes).
verify: verify_rp07_1430.py"""
import json, shutil, sys, time
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_round as R
import molang_lint as ML
import r16b
import build_r16b as BR

ROOT = Path("/home/claude")
SRC, DST, VER = ROOT / "_build/rp07-1429", ROOT / "_build/rp07-1430", "1.4.30"
FILES = {"anim": "animations/pw_fox_jem.animation.json", "entity": "entity/fox.entity.json"}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD rp07-1430: {m}\n")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    b, tw, th, init, pre, anim, rep = r16b.port("fox")
    R.wj(DST / FILES["anim"], {"format_version": "1.8.0", "animations": {BR.anim_id("fox"): anim}})
    pe = DST / FILES["entity"]; v = ML._parse_json(pe.read_text(encoding="utf-8")); desc = v["minecraft:client_entity"]["description"]
    desc["scripts"]["initialize"], desc["scripts"]["pre_animation"] = init, pre
    R.wj(pe, v)
    p, g = R.geo_file(DST, "geometry.pw_fox"); names = {x["name"] for x in g["bones"]}
    assert "pw_render" not in names
    g["bones"] = r16b.hierarchy("fox", g["bones"])
    d = R.jl(p); d["minecraft:geometry"] = [g]; R.wj(p, d)
    log(f"fox: {BR.anim_id('fox')} ({len(pre)} statements, {len(anim['bones'])} driven bones incl. pw_render); geometry.pw_fox + pw_render at the origin")
    mp = DST / "manifest.json"; m = R.jl(mp); vv = [int(x) for x in VER.split(".")]
    m["header"]["version"] = vv
    for mod in m["modules"]: mod["version"] = vv
    m["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"
    m["header"]["description"] = (f"v{VER} (2026-09-30) the fox tilts its whole body into a pounce (nose up on the leap, down on the drop) and "
                                  "nose-down when stuck in snow, as Java's renderer does. Includes all of 1.4.29.")
    R.wj(mp, m)
    log(f"manifest {VER}; geometry file {p.name}")


if __name__ == "__main__":
    main()
