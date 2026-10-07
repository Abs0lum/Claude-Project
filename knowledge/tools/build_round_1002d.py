#!/usr/bin/env python3
"""build_round_1002d.py — SIZE CAP FIX (his standing rule: "250 MB is an absolute maximum" per pack; RP-01 Tectonic is
the growth area for pw: custom-block files). RP-04 1.3.148 packaged at 254 MB and 1.3.149 at 310 MB -> both over.
  RP-04 1.3.150 (from 1.3.149): plank-grid tiles, keys, names and block sounds MOVE to RP-01; the dirt / coarse_dirt
         'own' copies (textures/blocks/own, 13 MB) and the two keys MOVE to RP-10 Terrain.
  RP-01 1.3.112 (from 1.3.111): textures/blocks/pw_planks (176 tiles + maps), the 176 pw_planks_* keys, block sounds,
         en_US names — pack-local with the BP-02 1.3.201 grid blocks (pw: custom blocks live in Tectonic).
  RP-10 1.3.48 (from 1.3.47): keys 'dirt' + 'coarse_dirt' now defined here, pointing at RP-10's own 15 dirt / 15 coarse
         dirt variants (256, with maps) + the base dirt / coarse_dirt picture copied from RP-04 into textures/blocks/own
         with its set + layers (key, images and sets in ONE pack).
Removed files go to _garbage by the never-delete hook (the source build dirs keep them too)."""
import json
import re
import shutil
from pathlib import Path

ROOT = Path("/home/claude")
B = ROOT / "_build"
JOBS = {"RP-04": ("rp04-149", "rp04-150", [1, 3, 150]), "RP-01": ("rp01-111", "rp01-112", [1, 3, 112]),
        "RP-10": ("rp10-147", "rp10-148", [1, 3, 48])}
DESC = {"RP-04": "Size cap: plank-grid textures moved to RP-01 Tectonic and dirt / coarse dirt to RP-10 Terrain (pack back "
                 "under 250 MB).",
        "RP-01": "Plank grids: Patrix 256 planks, 16 tiles per species (11 species) with depth + shine maps, for BP-02 1.3.201 "
                 "(moved here from RP-04: pw: custom blocks live in Tectonic).",
        "RP-10": "Dirt + coarse dirt: their texture names now live here with all their pictures and maps (moved from RP-04)."}


def jl(p):
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", p.read_text(encoding="utf-8-sig")))


def jw(p, d):
    p.write_text(json.dumps(d, indent=1))


def main():
    for pk, (s, d, _) in JOBS.items():
        assert not (B / d).exists(), f"never rebuild {d}"
    for pk, (s, d, _) in JOBS.items():
        shutil.copytree(B / s, B / d)
    r4, r1, r10 = (B / JOBS[k][1] for k in ("RP-04", "RP-01", "RP-10"))
    rep = {}
    # planks -> RP-01
    shutil.move(str(r4 / "textures/blocks/pw_planks"), str(r1 / "textures/blocks/pw_planks"))
    t4 = jl(r4 / "textures/terrain_texture.json")
    t1 = jl(r1 / "textures/terrain_texture.json")
    plank_keys = [k for k in t4["texture_data"] if k.startswith("pw_planks_")]
    assert len(plank_keys) == 176 and not set(plank_keys) & set(t1["texture_data"])
    for k in plank_keys:
        t1["texture_data"][k] = t4["texture_data"].pop(k)
    rep["plank keys moved"] = len(plank_keys)
    b4, b1 = jl(r4 / "blocks.json"), jl(r1 / "blocks.json")
    for k in [k for k in b4 if k.endswith("_planks_grid")]:
        b1[k] = b4.pop(k)
    jw(r4 / "blocks.json", b4)
    jw(r1 / "blocks.json", b1)
    l4 = (r4 / "texts/en_US.lang").read_text(encoding="utf-8").splitlines(keepends=True)
    moved = [ln for ln in l4 if "_planks_grid.name=" in ln]
    assert len(moved) == 11
    (r4 / "texts/en_US.lang").write_text("".join(ln for ln in l4 if ln not in moved), encoding="utf-8")
    l1 = (r1 / "texts/en_US.lang").read_text(encoding="utf-8")
    (r1 / "texts/en_US.lang").write_text(l1 + ("" if l1.endswith("\n") else "\n") + "".join(moved), encoding="utf-8")
    # dirt / coarse_dirt -> RP-10
    t10 = jl(r10 / "textures/terrain_texture.json")
    own10 = r10 / "textures/blocks/own"
    own10.mkdir(parents=True, exist_ok=True)
    src4 = B / "rp04-147/textures/blocks"
    for key in ("dirt", "coarse_dirt"):
        d = t4["texture_data"].pop(key)
        ts = json.loads((src4 / f"{key}.texture_set.json").read_text())["minecraft:texture_set"]
        for f in [key] + [v for k, v in ts.items() if k != "color"]:
            shutil.copy2(next(src4 / (f + e) for e in (".png", ".tga") if (src4 / (f + e)).exists()), own10)
        (own10 / f"{key}.texture_set.json").write_text(json.dumps({"format_version": "1.21.30", "minecraft:texture_set": ts},
                                                                   indent=1))
        for v in d["textures"]["variations"]:
            stem = v["path"].rsplit("/", 1)[1]
            v["path"] = f"textures/blocks/own/{key}" if stem == key else f"textures/blocks/{stem}"
            img = r10 / (v["path"] + ".png")
            assert img.exists() or (r10 / (v["path"] + ".tga")).exists(), v["path"]
            assert (r10 / (v["path"] + ".texture_set.json")).exists(), v["path"]
        assert key not in t10["texture_data"]
        t10["texture_data"][key] = d
    shutil.move(str(r4 / "textures/blocks/own"), str(ROOT / "_garbage" / "rp04-150-own-moved"))
    jw(r4 / "textures/terrain_texture.json", t4)
    jw(r1 / "textures/terrain_texture.json", t1)
    jw(r10 / "textures/terrain_texture.json", t10)
    for pk, (s, d, ver) in JOBS.items():
        mp = B / d / "manifest.json"
        m = jl(mp)
        old = ".".join(map(str, m["header"]["version"]))
        m["header"]["version"] = ver
        for mod in m["modules"]:
            mod["version"] = ver
        vs = ".".join(map(str, ver))
        m["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, m["header"]["name"])
        m["header"]["description"] = f"v{vs} (2026-10-02) {DESC[pk]} Includes all of v{old}."
        assert "pbr" in (m.get("capabilities") or [])
        mp.write_text(json.dumps(m, indent=2))
    print(rep, {pk: f"{sum(f.stat().st_size for f in (B / d).rglob('*') if f.is_file()) / 2**20:.1f} MiB"
                for pk, (s, d, v) in JOBS.items()})


if __name__ == "__main__":
    main()
