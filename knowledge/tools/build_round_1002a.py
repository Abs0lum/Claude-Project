#!/usr/bin/env python3
"""build_round_1002a.py — ROUND 1002a (his 00:53 rulings): assemble the staged pieces into new build dirs.
  1 OWNERSHIP (tools/own_stage.py -> _docs/blocks/OWN-PLAN.json, _staging/own/):
      BARK  RP-01 trunk keys (young/mature/old/elder) re-pointed to RP-01's own copies textures/blocks/bark/* (+ maps)
      LIB   all 9 species' log/wood bark copied into RP-01 bark/ with maps (his ask: Tectonic holds all bark)
      COPY  RP-04 'dirt' / 'coarse_dirt' keys re-pointed to RP-04's own copies textures/blocks/own/* (+ maps)
      MOVE  167 keys moved to the pack that holds their image + set (removed from the old pack's terrain_texture.json)
      VAN / SKIP are listed only (vanilla keys = normal override, witnessed working).
  2 SAND  RP-04 pw_sand_v1..24: colour unchanged; normal = B + G2 grains; MERS + G2 grains (from _build/sandtest-g2-100)
  3 VINES RP-04 vine_v0..v11 -> 256 colour + own normal + MERS (_staging/vine/rp04)
New build dirs (never rebuilt): rp01-110 rp03-63 rp04-148 rp05-54 rp10-146 rp11-137. Report: _docs/blocks/BUILD-1002A.json."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
JOBS = {"RP-01": ("rp01-109", "rp01-110", [1, 3, 110]), "RP-03": ("rp03-62", "rp03-63", [1, 3, 63]),
        "RP-04": ("rp04-147", "rp04-148", [1, 3, 148]), "RP-05": ("rp05-53", "rp05-54", [1, 3, 54]),
        "RP-10": ("rp10-145", "rp10-146", [1, 3, 46]), "RP-11": ("rp11-136", "rp11-137", [1, 3, 37])}
DESC = {
    "RP-01": "Tree bark ownership: every dodecagon + elder trunk bark now lives in this pack with its own depth (normal) "
             "and shine (MERS) maps (textures/blocks/bark), plus every species' bark; 2 moved keys.",
    "RP-03": "3 terrain keys moved here (their image + maps live here).",
    "RP-04": "Sand B + mineral glint G2 (8 grain directions); vines 256 with their own maps; dirt / coarse dirt keys own "
             "their images + maps; 31 keys moved to the packs holding their images.",
    "RP-05": "12 terrain keys moved here (their image + maps live here); 8 moved out.",
    "RP-10": "134 terrain keys moved here (their image + maps live here).",
    "RP-11": "8 ore keys moved here (their image + maps live here).",
}


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def remap(obj, mapping):
    if isinstance(obj, str):
        return mapping.get(obj, obj)
    if isinstance(obj, list):
        return [remap(x, mapping) for x in obj]
    if isinstance(obj, dict):
        return {k: remap(v, mapping) for k, v in obj.items()}
    return obj


def terrain(pk):
    p = B / JOBS[pk][1] / "textures/terrain_texture.json"
    if p.exists():
        return p, jl(p)
    return p, {"resource_pack_name": f"pw_{pk.lower()}", "texture_name": "atlas.terrain", "padding": 8,
               "num_mip_levels": 4, "texture_data": {}}


def main():
    for pk, (src, dst, _) in JOBS.items():
        assert not (B / dst).exists(), f"never rebuild a build dir: {dst}"
    for pk, (src, dst, _) in JOBS.items():
        shutil.copytree(B / src, B / dst)
    plan = json.loads((ROOT / "_docs/blocks/OWN-PLAN.json").read_text())
    rep = {"files_added": {}, "keys": {}}
    # staged copies
    for key, pk in (("rp01", "RP-01"), ("rp04", "RP-04")):
        root = ROOT / "_staging/own" / key
        n = 0
        for f in root.rglob("*"):
            if f.is_file():
                out = B / JOBS[pk][1] / f.relative_to(root)
                assert not out.exists(), f"would overwrite {out}"
                out.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)
                n += 1
        rep["files_added"][pk] = n
    terr = {pk: terrain(pk) for pk in JOBS}
    # BARK + COPY re-points
    for e in plan["BARK"] + plan["COPY"]:
        pk = e["pack"][:5]
        td = terr[pk][1]["texture_data"]
        assert e["key"] in td, (pk, e["key"])
        td[e["key"]] = remap(td[e["key"]], e["repoint"])
        rep["keys"].setdefault("repointed", []).append(f"{pk}:{e['key']}")
    # MOVE
    for m in plan["MOVE"]:
        a, b = m["from"][:5], m["to"][:5]
        ta, tb = terr[a][1]["texture_data"], terr[b][1]["texture_data"]
        assert m["key"] in ta, (a, m["key"])
        tb[m["key"]] = ta.pop(m["key"])
        rep["keys"].setdefault("moved", []).append(f"{m['key']}: {a} -> {b}")
    for pk, (p, d) in terr.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(d, indent=1))
    # SAND B + G2
    sd = B / "sandtest-g2-100/textures/blocks"
    n = 0
    for f in sd.iterdir():
        if f.name.startswith("pw_sand_v"):
            shutil.copy2(f, B / JOBS["RP-04"][1] / "textures/blocks" / f.name)
            n += 1
    rep["sand_files"] = n
    # VINES
    vd = ROOT / "_staging/vine/rp04/textures/blocks"
    n = 0
    for f in vd.iterdir():
        shutil.copy2(f, B / JOBS["RP-04"][1] / "textures/blocks" / f.name)
        n += 1
    rep["vine_files"] = n
    # manifests
    for pk, (src, dst, ver) in JOBS.items():
        mp = B / dst / "manifest.json"
        m = jl(mp)
        old = ".".join(map(str, m["header"]["version"]))
        m["header"]["version"] = ver
        for mod in m["modules"]:
            mod["version"] = ver
        vs = ".".join(map(str, ver))
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
        m["header"]["description"] = f"v{vs} (2026-10-02) {DESC[pk]} Includes all of v{old}."
        assert "pbr" in (m.get("capabilities") or []), f"{pk} manifest lacks the pbr capability"
        mp.write_text(json.dumps(m, indent=2))
    (ROOT / "_docs/blocks/BUILD-1002A.json").write_text(json.dumps(rep, indent=1))
    print({k: (v if not isinstance(v, dict) else {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()})
           for k, v in rep.items()})


if __name__ == "__main__":
    main()
