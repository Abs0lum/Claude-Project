#!/usr/bin/env python3
"""build_rp13_100.py — RP-13 AbsolutRealism Architecture RP 1.0.0 (program 228, 2026-10-06). His standing rule: "250 MB is an
absolute maximum [per pack]. Separate based on needs AND future foreseeable conflicts." RP-04 with the 8-block ramps came to
283 MB, so the ARCHITECTURE kit's new parts get their own pack:
  - the 8-BLOCK RAMP geometry (pw_ramps8 + snowcaps) and the 16 new ramp stones' tiles + PBR maps (tools/ramp_v8.py staging);
  - the SPIRAL STAIRS (A turret, B tower, C grand): geometry + the 18 palette textures + MER / normal (tools/spiral_pack.py --main).
Only new files and new terrain keys (no key shared with RP-04 — asserted), so its order against RP-04 does not matter.
Needs: nothing. Used by: BP-02 1.3.228 (the ramp and spiral blocks)."""
import json
import shutil
from pathlib import Path

B = Path("/home/claude/_build")
DST = B / "rp13-100"
SRCS = [Path("/home/claude/_staging/ramps228/rp"), Path("/home/claude/_staging/spiral228/rp")]
UU = {"h": "68c26682-7f65-414f-a775-a26a9fee208b", "m": "1b9a33b1-714b-4503-bad8-b7ccf02e8d13"}


def main():
    if DST.exists():
        raise SystemExit(f"never rebuild {DST}")
    (DST / "textures").mkdir(parents=True)
    tt = {"resource_pack_name": "pw_architecture", "texture_name": "atlas.terrain", "padding": 8, "num_mip_levels": 4, "texture_data": {}}
    rp04 = json.loads((B / "rp04-159/textures/terrain_texture.json").read_text(encoding="utf-8-sig"))["texture_data"]
    n = 0
    for src in SRCS:
        for f in sorted((src / "models/blocks").glob("*.json")) + sorted((src / "textures/blocks").rglob("*.*")):
            rel = f.relative_to(src)
            assert not (DST / rel).exists(), f"two sources give {rel}"
            (DST / rel).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, DST / rel)
            n += 1
        add = json.loads((src / "terrain_texture_add.json").read_text())
        clash = [k for k in add if k in tt["texture_data"] or k in rp04]
        assert not clash, f"terrain keys already defined: {clash[:5]}"
        tt["texture_data"].update(add)
    (DST / "textures/terrain_texture.json").write_text(json.dumps(tt, indent=1))
    shutil.copy2(B / "rp04-159/pack_icon.png", DST / "pack_icon.png")
    m = {"format_version": 2,
         "header": {"name": "AbsolutRealism Architecture RP v1.0.0", "uuid": UU["h"], "version": [1, 0, 0], "min_engine_version": [1, 21, 120],
                    "description": "v1.0.0 (2026-10-06) the ARCHITECTURE kit's new parts: the 8-block street ramp in 19 stones + the spiral stairs "
                                   "(A turret, B tower, C grand; stone / oak / spruce + plaster). Split from RP-04 (his 250 MB rule). Needs BP-02 1.3.228. Personal use."},
         "modules": [{"description": "AbsolutRealism Architecture resource module", "type": "resources", "uuid": UU["m"], "version": [1, 0, 0]}],
         "capabilities": ["pbr"], "metadata": {"authors": ["Abs0lum"], "product_type": "addon"}}
    (DST / "manifest.json").write_text(json.dumps(m, indent=1))
    print(f"DONE {DST}: {n} files, {len(tt['texture_data'])} terrain keys")


if __name__ == "__main__":
    main()
