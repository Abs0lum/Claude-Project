#!/usr/bin/env python3
"""build_fix_round_1002.py — the RECHECK-WEEK fix round (RECHECK-WEEK-2026-10-02 §A), three new build dirs from the frozen ones:
  RP-07 1.4.45 (from rp07-1444): A1 cave spider std file gets min_engine_version 1.21.0 (vanilla's 1.8.0 no longer wins);
                                 A2 its terrain_texture.json (13 sf_nba block keys whose images live in RP-08) is retired to
                                 _docs/blocks/retired_rp07_terrain_texture.json; A3 walrus idle_event + whale baby_tilt_lerp
                                 dangling animation names removed; description lead + PW-DEPENDENCIES stamp updated.
  RP-08 1.4.14 (from rp08-1413): A2 takes the 13 keys into its terrain_texture.json (keys + images + sets in ONE pack).
  TestRunner 0.5.14 (from testrunner-0.5.13): A6 RUNNER_VERSION == manifest, + a packaging assert in verify.
Never touches the frozen dirs. Prints a checklist; the recheck gates (recheck_r2/r4/r6) are the proof afterwards."""
import json
import re
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
SRC7, DST7 = B / "rp07-1444", B / "rp07-1445"
SRC8, DST8 = B / "rp08-1413", B / "rp08-1414"
SRCT, DSTT = B / "testrunner-0.5.13", B / "testrunner-0.5.14"
DOCS = Path("/home/claude/_docs/blocks")


def bump_manifest(d, old, new, lead):
    m = json.loads((d / "manifest.json").read_text(encoding="utf-8-sig"))
    m["header"]["version"] = new
    m["header"]["name"] = m["header"]["name"].replace(".".join(map(str, old)), ".".join(map(str, new)))
    desc = m["header"].get("description", "")
    desc = re.sub(r"^v[0-9.]+ \([^)]*\)", "", desc).lstrip(" :—-")
    m["header"]["description"] = f"v{'.'.join(map(str, new))} (2026-10-02) {lead} Includes all of v{'.'.join(map(str, old))}: {desc}"[:1000]
    for mod in m.get("modules", []):
        mod["version"] = new
    (d / "manifest.json").write_text(json.dumps(m, indent=1))
    dep = d / "PW-DEPENDENCIES.md"
    if dep.exists():
        t = dep.read_text()
        t = re.sub(r"v?\d+\.\d+\.\d+", lambda mm: "v" + ".".join(map(str, new)) if mm.group(0).lstrip("v") == ".".join(map(str, old)) else mm.group(0), t, count=1)
        dep.write_text(t)


def main():
    for src, dst in ((SRC7, DST7), (SRC8, DST8), (SRCT, DSTT)):
        if dst.exists():
            raise SystemExit(f"never rebuild {dst}")
        shutil.copytree(src, dst)
    log = []
    # ---- RP-07 1.4.45
    cs = DST7 / "entity/std/minecraft_cave_spider.entity.json"
    d = json.loads(cs.read_text(encoding="utf-8-sig"))
    d["minecraft:client_entity"]["description"]["min_engine_version"] = "1.21.0"
    cs.write_text(json.dumps(d, indent=1))
    log.append("A1 cave_spider min_engine_version 1.21.0")
    tt = DST7 / "textures/terrain_texture.json"
    keys7 = json.loads(tt.read_text(encoding="utf-8-sig"))
    DOCS.mkdir(parents=True, exist_ok=True)
    (DOCS / "retired_rp07_terrain_texture.json").write_text(json.dumps(keys7, indent=1))
    tt.unlink()
    log.append(f"A2 RP-07 terrain_texture.json retired ({len(keys7['texture_data'])} keys)")
    for ent, key in (("walrus", "idle_event"), ("whale", "baby_tilt_lerp")):
        p = DST7 / f"entity/{ent}.entity.json"
        e = json.loads(p.read_text(encoding="utf-8-sig"))
        an = e["minecraft:client_entity"]["description"]["animations"]
        assert key in an, (ent, key)
        del an[key]
        p.write_text(json.dumps(e, indent=1))
        log.append(f"A3 {ent}: animations.{key} removed")
    bump_manifest(DST7, [1, 4, 44], [1, 4, 45], "RECHECK FIX ROUND: our cave spider now wins over vanilla (engine-version pin); the 13 Naturalist block texture keys moved to RP-08 (one-pack ownership); walrus/whale dangling animation names removed.")
    # ---- RP-08 1.4.14
    tt8 = DST8 / "textures/terrain_texture.json"
    keys8 = json.loads(tt8.read_text(encoding="utf-8-sig"))
    for k, v in keys7["texture_data"].items():
        assert k not in keys8["texture_data"], k
        keys8["texture_data"][k] = v
        # the images must exist in RP-08
        paths = v["textures"] if isinstance(v["textures"], list) else [v["textures"]]
        for pth in paths:
            pth = pth if isinstance(pth, str) else pth["path"]
            assert (DST8 / f"{pth}.png").exists(), pth
    tt8.write_text(json.dumps(keys8, indent=1))
    log.append(f"A2 RP-08 terrain_texture.json +{len(keys7['texture_data'])} keys (images verified present)")
    bump_manifest(DST8, [1, 4, 13], [1, 4, 14], "RECHECK FIX ROUND: the 13 Naturalist block texture keys (ant hill, chrysalis, shellstone family, starfish) now live here with their images and texture sets.")
    # ---- TestRunner 0.5.14
    pr = DSTT / "scripts/pw_testrunner.js"
    t = pr.read_text()
    assert 'export const RUNNER_VERSION = "0.5.11";' in t
    t = t.replace('export const RUNNER_VERSION = "0.5.11";', 'export const RUNNER_VERSION = "0.5.14";   // the version-flag law: == manifest (packager assert)')
    pr.write_text(t)
    bump_manifest(DSTT, [0, 5, 13], [0, 5, 14], "RECHECK FIX ROUND: the boot banner carries the shipped version (was stuck at 0.5.11).")
    log.append("A6 RUNNER_VERSION 0.5.14 == manifest")
    for line in log:
        print("DONE", line)


if __name__ == "__main__":
    main()
