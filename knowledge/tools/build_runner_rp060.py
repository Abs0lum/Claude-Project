#!/usr/bin/env python3
"""build_runner_rp060.py — PW-TestRunner RP v0.6.0 + the pw:cullprobe block (D-C350, the p17 CULLING PROBE).

Question (Microsoft's culling-rule docs are silent on it): when a block is turned by minecraft:transformation (our leaf looks use
quarter turns), does its culling rule turn with it? The probe is a full cube whose six faces each carry their own colour + letter
(N red, E blue, S yellow, W green, U white, D black), state pw:q 0-3 = rotation [0, 90q, 0], and ONE culling definition:
cull the EAST face when the east neighbour is the same block, cull the SOUTH face likewise (the rule we want for the leaves).
In pairs of equal q the answer is visible at a glance: a hole on an outer side = the rule does not turn with the block.
RP v0.6.0 = RP v0.5.0 (the 256 test leaves) + geometry.pw_cullprobe + 6 tiles + block_culling/pw_cullprobe.json.
Block JSON -> _build/cullprobe-blocks/pw_cullprobe.json (copied into the runner BP by build_testrunner.py)."""
import json, shutil, time
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/home/claude")
SRC, RP, VER = ROOT / "_build/testrunner-rp-0.5.0", ROOT / "_build/testrunner-rp-0.6.0", [0, 6, 0]
BLK = ROOT / "_build/cullprobe-blocks"
FACES = {"north": ("N", (200, 40, 40)), "east": ("E", (40, 80, 210)), "south": ("S", (230, 200, 30)), "west": ("W", (40, 160, 60)),
         "up": ("U", (240, 240, 240)), "down": ("D", (25, 25, 25))}


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT {time.strftime('%m-%d')}] BUILD runner RP 0.6.0: {m}\n")


def main():
    if RP.exists(): shutil.rmtree(RP)
    shutil.copytree(SRC, RP)
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    tdir = RP / "textures/blocks/pw_cullprobe"; tdir.mkdir(parents=True, exist_ok=True)
    ttp = RP / "textures/terrain_texture.json"; tdoc = json.loads(ttp.read_text(encoding="utf-8-sig"))
    for face, (letter, col) in FACES.items():
        im = Image.new("RGBA", (64, 64), col + (255,)); d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 63, 63], outline=(0, 0, 0, 255), width=2)
        ink = (0, 0, 0, 255) if sum(col) > 400 else (255, 255, 255, 255)
        d.text((32, 32), letter, fill=ink, font=font, anchor="mm")
        im.save(tdir / f"{face}.png")
        tdoc["texture_data"][f"pw_cullprobe_{face}"] = {"textures": f"textures/blocks/pw_cullprobe/{face}"}
    ttp.write_text(json.dumps(tdoc, indent=1))
    geo = {"format_version": "1.21.0", "minecraft:geometry": [{
        "description": {"identifier": "geometry.pw_cullprobe", "texture_width": 16, "texture_height": 16,
                        "visible_bounds_width": 2, "visible_bounds_height": 2, "visible_bounds_offset": [0, 0.5, 0]},
        "bones": [{"name": "probe", "pivot": [0, 0, 0], "cubes": [{"origin": [-8, 0, -8], "size": [16, 16, 16],
                   "uv": {f: {"uv": [0, 0], "uv_size": [16, 16], "material_instance": f"p_{f}"} for f in FACES}}]}]}]}
    (RP / "models/blocks").mkdir(parents=True, exist_ok=True)
    (RP / "models/blocks/pw_cullprobe.geo.json").write_text(json.dumps(geo, indent=1))
    cull = {"format_version": "1.21.80", "minecraft:block_culling_rules": {
        "description": {"identifier": "pw:culling.cullprobe"},
        "rules": [{"direction": d, "condition": "same_block", "geometry_part": {"bone": "probe", "cube": 0, "face": d}} for d in ("east", "south")]}}
    (RP / "block_culling").mkdir(exist_ok=True)
    (RP / "block_culling/pw_cullprobe.json").write_text(json.dumps(cull, indent=1))
    bj = RP / "blocks.json"; bjd = json.loads(bj.read_text(encoding="utf-8-sig")); bjd["pw:cullprobe"] = {"sound": "stone"}
    bj.write_text(json.dumps(bjd, indent=1))
    lang = RP / "texts/en_US.lang"; lang.write_text(lang.read_text(encoding="utf-8").rstrip("\n") + "\ntile.pw:cullprobe.name=Culling Probe (test)\n", encoding="utf-8")
    man = RP / "manifest.json"; m = json.loads(man.read_text(encoding="utf-8-sig"))
    m["header"]["version"] = VER; m["header"]["name"] = "PW Test Runner RP v0.6.0"
    for mod in m["modules"]: mod["version"] = VER
    m["header"]["description"] = ("v0.6.0 (2026-09-30) TEST RUNNER RP — adds the CULLING PROBE for p17 (pw:cullprobe: a cube with one colour + "
        "letter per face and an east/south same-block culling rule, turned 0-3 quarter turns). Plus everything of v0.5.0 (the 256 test leaves, "
        "the pilot leaves, pw:probe, the XPACK keys). Declares Vibrant Visuals (pbr). Job-only: attach at the TOP of the Resource Packs list while testing.")
    man.write_text(json.dumps(m, indent=1))
    # the block (behaviour side)
    if BLK.exists(): shutil.rmtree(BLK)
    BLK.mkdir(parents=True)
    blk = {"format_version": "1.21.80", "minecraft:block": {
        "description": {"identifier": "pw:cullprobe", "menu_category": {"category": "construction"}, "states": {"pw:q": [0, 1, 2, 3]}},
        "components": {
            "minecraft:geometry": {"identifier": "geometry.pw_cullprobe", "culling": "pw:culling.cullprobe"},
            "minecraft:material_instances": {"*": {"texture": "pw_cullprobe_up", "render_method": "opaque"},
                                             **{f"p_{f}": {"texture": f"pw_cullprobe_{f}", "render_method": "opaque"} for f in FACES}},
            "minecraft:destructible_by_mining": {"seconds_to_destroy": 0.2}, "minecraft:destructible_by_explosion": {"explosion_resistance": 1},
            "minecraft:light_dampening": 15},
        "permutations": [{"condition": f"q.block_state('pw:q') == {q}", "components": {"minecraft:transformation": {"rotation": [0, 90 * q, 0]}}}
                         for q in (1, 2, 3)]}}
    (BLK / "pw_cullprobe.json").write_text(json.dumps(blk, indent=1))
    log("pw:cullprobe geometry + 6 face tiles + block_culling/pw_cullprobe.json (east/south, same_block); block JSON -> _build/cullprobe-blocks")


if __name__ == "__main__":
    main()
