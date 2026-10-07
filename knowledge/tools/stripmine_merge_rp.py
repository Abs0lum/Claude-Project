#!/usr/bin/env python3
"""stripmine_merge_rp.py — phase 2 of the StripMine dissolve (plan: _docs/stripmine/STRIPMINE-MERGE-CENSUS-2026-10-02.md
§4-§7; his 16:47 'yes for all').

From PW StripMine RP 3.0.1 (the version he has installed):
  RP-07 1.4.44 (from 1.4.43): sounds/sf/** (Naturalist sound files), the sf_nba sound definitions, the Naturalist
          entries of sounds.json, the Naturalist block keys (terrain_texture.json) and blocks.json entries, the 7
          attachables (crab hats, butterfly wings, peacloak), textures_list union.
  RP-08 1.4.13 (from 1.4.12): the Naturalist item icon keys (item_texture.json).
  RP-02 2.0.7 (from 2.0.6): the global Vibrant Visuals files StripMine was the only source of (biomes_client.json,
          pbr/global.json, local_lighting/local_lighting.json, cubemaps/cubemap.json) + its vanilla-path overrides
          (textures/flame_atlas.png) — today's look kept. (Its crack textures are byte-identical to RP-02's own.)
  D4 = carry ONLY the Naturalist (sf_nba) sound entries: StripMine's sounds.json also rewired 61 vanilla mobs and 17 vanilla
  events (player, zombie, thunder, flint-and-steel, block break/place, donkey/mule steps) to blank sounds or to
  'oreville_ans:*' events that exist in NO pack — those are dropped, so vanilla sounds return.
  Archived, not copied: textures/sf/** (byte-identical copies already in RP-06/07/08), materials/entity.material, the
  enderman animation, the nested 'Naturalist Add-On 26.1 BP/' folder, sounds/oreville/** (no definition uses them),
  PROVENANCE.md, PW-DEPENDENCIES.md, manifest.json, pack_icon.png.
Each receiving pack gets PROVENANCE-STRIPMINE.json (every moved file and merged key, with its origin)."""
import hashlib
import json
import re
import shutil
import zipfile
from pathlib import Path

B = Path("/home/claude/_build")
SM = zipfile.ZipFile("/home/claude/_intake/stack-rps/PW-StripMine-RP-v3_0_1.mcpack")
SRC_PACK = "PW StripMine RP 3.0.1"
BUILDS = {"rp07": ("rp07-1443", "rp07-1444", [1, 4, 44]), "rp08": ("rp08-1412", "rp08-1413", [1, 4, 13]),
          "rp02": ("rp02-206", "rp02-207", [2, 0, 7])}
VV_GLOBALS = ["biomes_client.json", "pbr/global.json", "local_lighting/local_lighting.json", "cubemaps/cubemap.json",
              "textures/flame_atlas.png"]   # destroy_stage_0..9 + pixel.png: RP-02 already holds byte-identical copies


def jl(data):
    text = data.decode("utf-8-sig") if isinstance(data, bytes) else data
    return json.loads(re.sub(r"(?m)^\s*//.*$", "", text))


def sha1(data):
    return hashlib.sha1(data).hexdigest()


def is_naturalist(key):
    return key.startswith("sf_nba")


class Provenance:
    def __init__(self):
        self.files, self.keys = [], {}

    def file(self, dest, original, data):
        self.files.append({"dest_path": dest, "source_pack": SRC_PACK, "origin_addon": "Naturalist (sf_nba)"
                           if "sf" in original.split("/") or "attachables" in original else "RealSource (StripMine RP)",
                           "original_path": original, "bytes": len(data), "sha1": sha1(data)})

    def merged(self, file_name, keys):
        self.keys.setdefault(file_name, []).extend(sorted(keys))

    def write(self, folder):
        (folder / "PROVENANCE-STRIPMINE.json").write_text(json.dumps(
            {"note": f"Moved from {SRC_PACK} (his ruling 2026-10-02: StripMine dissolved into our packs, labelled by source).",
             "files": self.files, "merged_keys": self.keys}, indent=1))


def bump(folder, ver, desc):
    mp = folder / "manifest.json"
    man = jl(mp.read_bytes())
    old = ".".join(map(str, man["header"]["version"]))
    man["header"]["version"] = ver
    for mod in man["modules"]:
        mod["version"] = ver
    vs = ".".join(map(str, ver))
    man["header"]["name"] = re.sub(r"v\d+\.\d+\.\d+", "v" + vs, man["header"]["name"])
    man["header"]["description"] = f"v{vs} (2026-10-02) {desc} Includes all of v{old}."
    assert "pbr" in (man.get("capabilities") or []), folder
    mp.write_text(json.dumps(man, indent=2))


def merge_dict(base, extra, label, prov, file_name):
    collisions = sorted(set(base) & set(extra))
    assert not collisions, f"{file_name}: key collision {collisions[:5]}"
    base.update(extra)
    prov.merged(file_name, extra)


def rp07(prov):
    out = B / BUILDS["rp07"][1]
    names = [n for n in SM.namelist() if not n.endswith("/")]
    for n in names:                                           # Naturalist sound files + attachables
        if n.startswith("sounds/sf/") or n.startswith("attachables/"):
            dest = out / n
            assert not dest.exists(), f"exists: {n}"
            dest.parent.mkdir(parents=True, exist_ok=True)
            data = SM.read(n)
            dest.write_bytes(data)
            prov.file(n, n, data)
    defs_path = out / "sounds/sound_definitions.json"
    defs = jl(defs_path.read_bytes())
    sm_defs = jl(SM.read("sounds/sound_definitions.json"))["sound_definitions"]
    assert all(is_naturalist(k) for k in sm_defs), "non-Naturalist sound definition in StripMine"
    merge_dict(defs["sound_definitions"], sm_defs, "sf_nba", prov, "sounds/sound_definitions.json")
    defs_path.write_text(json.dumps(defs, indent=1))
    sounds_path = out / "sounds.json"
    sounds = jl(sounds_path.read_bytes())
    sm_sounds = jl(SM.read("sounds.json"))
    keep = {k: v for k, v in sm_sounds["entity_sounds"]["entities"].items() if is_naturalist(k)}
    dropped = sorted(k for k in sm_sounds["entity_sounds"]["entities"] if not is_naturalist(k))
    merge_dict(sounds.setdefault("entity_sounds", {}).setdefault("entities", {}), keep, "sf_nba", prov, "sounds.json:entity_sounds")
    inter = {k: v for k, v in sm_sounds.get("interactive_sounds", {}).get("entity_sounds", {}).get("entities", {}).items()
             if is_naturalist(k)}
    if inter:
        merge_dict(sounds.setdefault("interactive_sounds", {}).setdefault("entity_sounds", {}).setdefault("entities", {}),
                   inter, "sf_nba", prov, "sounds.json:interactive_sounds.entity_sounds")
    sounds_path.write_text(json.dumps(sounds, indent=1))
    tt_path = out / "textures/terrain_texture.json"
    sm_tt = jl(SM.read("textures/terrain_texture.json"))
    tt = jl(tt_path.read_bytes()) if tt_path.exists() else {k: v for k, v in sm_tt.items() if k != "texture_data"} | {"texture_data": {}}
    merge_dict(tt["texture_data"], sm_tt["texture_data"], "sf_nba", prov, "textures/terrain_texture.json")
    tt_path.write_text(json.dumps(tt, indent=1))
    bj_path = out / "blocks.json"
    sm_bj = jl(SM.read("blocks.json"))
    bj = jl(bj_path.read_bytes()) if bj_path.exists() else {"format_version": sm_bj.get("format_version", [1, 1, 0])}
    merge_dict(bj, {k: v for k, v in sm_bj.items() if k != "format_version"}, "sf_nba", prov, "blocks.json")
    bj_path.write_text(json.dumps(bj, indent=1))
    tl_path = out / "textures/textures_list.json"
    tl = jl(tl_path.read_bytes())
    extra = [p for p in jl(SM.read("textures/textures_list.json")) if p not in tl]
    tl_path.write_text(json.dumps(tl + extra, indent=1))
    prov.merged("textures/textures_list.json", extra)
    return {"sound_defs": len(sm_defs), "entity_sound_entries_kept": len(keep), "vanilla_overrides_dropped": dropped,
            "terrain_keys": len(sm_tt["texture_data"]), "blocks_json": len(sm_bj) - 1, "textures_list_added": len(extra)}


def rp08(prov):
    out = B / BUILDS["rp08"][1]
    it_path = out / "textures/item_texture.json"
    it = jl(it_path.read_bytes())
    sm_it = jl(SM.read("textures/item_texture.json"))["texture_data"]
    merge_dict(it["texture_data"], sm_it, "sf_nba", prov, "textures/item_texture.json")
    it_path.write_text(json.dumps(it, indent=1))
    return {"item_keys": len(sm_it)}


def rp02(prov):
    out = B / BUILDS["rp02"][1]
    for n in VV_GLOBALS:
        dest = out / n
        assert not dest.exists(), f"exists in RP-02: {n}"
        dest.parent.mkdir(parents=True, exist_ok=True)
        data = SM.read(n)
        dest.write_bytes(data)
        prov.file(n, n, data)
    return {"files": len(VV_GLOBALS)}


def main():
    report = {}
    for key, (src, dst, _) in BUILDS.items():
        assert not (B / dst).exists(), f"never rebuild {dst}"
        shutil.copytree(B / src, B / dst)
    for key, fn, desc in (
            ("rp07", rp07, "StripMine RP merged in: Naturalist sounds + sound list, Naturalist block textures + blocks.json, "
                           "crab hats / butterfly wings / peacloak; StripMine's broken vanilla sound overrides NOT carried "
                           "(vanilla sounds return)."),
            ("rp08", rp08, "StripMine RP merged in: the Naturalist item icons."),
            ("rp02", rp02, "StripMine RP merged in: the global Vibrant Visuals settings (lighting, local lighting, cubemap, "
                           "biome client file), unchanged.")):
        prov = Provenance()
        report[key] = fn(prov)
        folder = B / BUILDS[key][1]
        prov.write(folder)
        bump(folder, BUILDS[key][2], desc)
    Path("/home/claude/_docs/stripmine/BUILD-PHASE2.json").write_text(json.dumps(report, indent=1))
    print(json.dumps({k: {kk: (len(vv) if isinstance(vv, list) else vv) for kk, vv in v.items()} for k, v in report.items()}, indent=1))


if __name__ == "__main__":
    main()
