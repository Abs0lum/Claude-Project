#!/usr/bin/env python3
"""build_rp04_142.py — RP-04 Basic RP v1.3.142: LAVA TIMING (D-C267; the 09-28 witness b04 "animation just a bit slow").

Mechanism (files + Patrix source): the lava block's liquid renderer uses the vanilla atlas tiles `still_lava` and `flowing_lava`
(vanilla flipbook: still tpf 16, flow tpf 10 replicate 2). RP-04 registered its lava under `lava_still` / `lava_flow` (+ four
`lava_still_v1..v4` variation tiles and `lava_still_single`) — names nothing uses, so vanilla's timing ran on our files: the
48-frame flow at 10 ticks a frame = a 24 s cycle, and the still lava a 1-frame 128 x 128 (static).
The Patrix 1.21.11 128x source (range-read from Patrix_1.21.11_128x_basic.zip): lava_flow.png.mcmeta frametime 1 (48 frames ->
2.4 s); lava_still.png 128 x 1024 = 8 frames, frametime 10, interpolate (4 s, blended).
v1.3.142:
  - flipbook: `flowing_lava` -> textures/blocks/lava_flow, 1 tick a frame, replicate 2 (as vanilla's entry); `still_lava` ->
    textures/blocks/lava_still, 10 ticks a frame, blend_frames (the Patrix interpolate)
  - textures/blocks/lava_still.png <- the Patrix 8-frame strip (128 x 1024). The flow strip is unchanged (128 x 6144, the look he passed)
  - the dead registry entries are removed: terrain keys lava_still / lava_flow / lava_still_v1..v4 / lava_still_single and their
    flipbook tiles (no blocks.json, behaviour pack or other pack names them). Their files stay (orphans -> the ownership wave's archive)
  - NOT changed: no texture sets are added (vanilla 1.26 ships lava texture sets naming lava_*_mers / lava_*_normal; lava PBR is a
    separate decision) and the campfire logs (Patrix has no campfire-log texture — an authoring job for a later round)
Everything else byte-identical to v1.3.141 (verify_rp04_142.py asserts the diff)."""
import json, shutil, time
from pathlib import Path
from PIL import Image

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/rp04-141", ROOT / "_build/rp04-142", "1.3.142", "2026-09-28"
PATRIX = ROOT / "_intake/patrix128/pull3/assets/minecraft/textures/block"
DEAD_KEYS = ["lava_still", "lava_flow", "lava_still_v1", "lava_still_v2", "lava_still_v3", "lava_still_v4", "lava_still_single"]
DEAD_TILES = ["lava_still", "lava_flow", "lava_still_v1", "lava_still_v2", "lava_still_v3", "lava_still_v4"]
NEW_TILES = [
    {"flipbook_texture": "textures/blocks/lava_still", "atlas_tile": "still_lava", "ticks_per_frame": 10, "blend_frames": True},
    {"flipbook_texture": "textures/blocks/lava_flow", "atlas_tile": "flowing_lava", "ticks_per_frame": 1, "replicate": 2},
]


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {m}\n")


def main():
    mc_still = json.loads((PATRIX / "lava_still.png.mcmeta").read_text())["animation"]
    mc_flow = json.loads((PATRIX / "lava_flow.png.mcmeta").read_text())["animation"]
    assert mc_still.get("frametime") == 10 and mc_still.get("interpolate") is True and mc_flow.get("frametime") == 1, (mc_still, mc_flow)
    src = Image.open(PATRIX / "lava_still.png")
    assert src.size == (128, 1024), src.size
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    # the still strip
    src.convert("RGB").save(DST / "textures/blocks/lava_still.png", optimize=True)
    # flipbook
    fp = DST / "textures/flipbook_textures.json"
    fb = json.loads(fp.read_text(encoding="utf-8-sig"))
    before = len(fb)
    fb = [e for e in fb if e.get("atlas_tile") not in DEAD_TILES and e.get("atlas_tile") not in ("still_lava", "flowing_lava")]
    assert before - len(fb) == len(DEAD_TILES), (before, len(fb))
    fb += NEW_TILES
    fp.write_text(json.dumps(fb, indent=1), encoding="utf-8")
    # terrain keys
    tp = DST / "textures/terrain_texture.json"
    tt = json.loads(tp.read_text(encoding="utf-8-sig"))
    for k in DEAD_KEYS:
        assert k in tt["texture_data"], k
        del tt["texture_data"][k]
    tp.write_text(json.dumps(tt, indent=1), encoding="utf-8")
    # manifest
    mp = DST / "manifest.json"; man = json.loads(mp.read_text(encoding="utf-8-sig")); v = [int(x) for x in VER.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    man["header"]["name"] = f"AbsolutRealism Basic RP v{VER}"
    man["header"]["description"] = (
        f"v{VER} ({DATE}) LAVA TIMING (D-C267): the lava flipbooks now use the tile names the lava block actually reads (still_lava / "
        "flowing_lava) with the Patrix timing — the flow cycles in 2.4 s (was 24 s under vanilla's timing) and still lava is the Patrix "
        "8-frame animated strip (was one static frame). The unused lava_still / lava_flow / lava_still_v1-v4 / lava_still_single entries are "
        "removed. Everything else byte-identical to v1.3.141.")
    mp.write_text(json.dumps(man, indent=1), encoding="utf-8")
    log(f"RP-04 v{VER}: still_lava (8 frames, tpf 10, blend) + flowing_lava (tpf 1, replicate 2) flipbooks; lava_still.png <- Patrix 128x1024; "
        f"{len(DEAD_KEYS)} dead keys + {len(DEAD_TILES)} dead tiles removed -> {DST}")


if __name__ == "__main__":
    main()
