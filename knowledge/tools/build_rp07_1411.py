#!/usr/bin/env python3
"""build_rp07_1411.py — RP-07 v1.4.11: the trader llama gets the ORDINARY llama's geometry (D-C253).

Witness (Abs0lum 09:57 09-27): "I see llamas - but they're not geometrically correct. Please reference the llamas
we had that were perfect to correct these."  His screenshot (white + cream trader llamas): a boxy body whose bottom
floats well above four short legs, and the neck box hanging below the body's front with the chest strap on it.

Mechanism (static, matches his screenshot under the engine's rotation convention — see D-C253):
  geometry.trader_llama.patrix (1.4.10) is an OLDER conversion state of the llama:
    body_cube origin [-6,17,1] size [12,18,11] pivot [0,23,2] rot [90,0,0]  ->  world y 22..33, z -10..8
      (the ordinary llama's body_cube origin [-6,16,-8] size [12,16,11] -> y 13..24, z -7..9)
    legs parent None, upper cube [4,6,4] (y 7..13)   (ordinary llama: parent body, upper [4,9,4] -> legs 0..16)
    head pivot [0,21,-6]                             (ordinary llama: [0,24,-6])
  => the body floats 9 cubes above 13-cube legs; the neck (15..33, z -13..-6) hangs 7 below the body and stands
     3 proud of its front; the head pivots 3 low.  Every difference is a regression from the ordinary llama.

Fix: models/entity/trader_llama.geo.json := models/entity/llama.geo.json with the identifier renamed to
geometry.trader_llama.patrix.  Same bones (body/head/head2/snout/ears/legs/pw_* helpers), same UV layout — the
1.4.10 composite trader textures (Patrix body variant + decor) already use the llama layout.  Nothing else changes
(entity file, render controller, animations, textures untouched).
"""
import json, shutil, datetime, hashlib
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/rp07-1410", ROOT / "_build/rp07-1411"
VER = "1.4.11"; DATE = "2026-09-27"
LOG = ROOT / "_logs/phase_log.md"


def log(m):
    print(m); open(LOG, "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-27] BUILD RP-07 {VER} — {m}\n")


def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    geo = jload(SRC / "models/entity/llama.geo.json")
    assert [g["description"]["identifier"] for g in geo["minecraft:geometry"]] == ["geometry.llama.patrix"]
    geo["minecraft:geometry"][0]["description"]["identifier"] = "geometry.trader_llama.patrix"
    jdump(geo, DST / "models/entity/trader_llama.geo.json")
    log("models/entity/trader_llama.geo.json := llama.geo.json (identifier geometry.trader_llama.patrix); md5 " + hashlib.md5((DST / "models/entity/trader_llama.geo.json").read_bytes()).hexdigest()[:8])
    man = jload(DST / "manifest.json"); vv = [int(x) for x in VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"; man["header"]["version"] = vv
    for m in man["modules"]: m["version"] = vv
    man["header"]["description"] = (
        f"v{VER} ({DATE}) TRADER LLAMA GEOMETRY (D-C253, Abs0lum 09:57 'not geometrically correct'): geometry.trader_llama.patrix "
        "was an older conversion state — its body cube landed 9 cubes above the legs (unparented, 3 short) with the head inside it. "
        "Now it is the ordinary llama's geometry (geometry.llama.patrix) under the trader identifier: body y 13-24 on legs 0-16, head "
        "pivot 24, same UV layout as the 1.4.10 composite trader textures. Nothing else touched (v1.4.10 + this geometry + manifest).")
    jdump(man, DST / "manifest.json")
    log(f"manifest v{VER} stamped; _build/rp07-1411 = v1.4.10 + trader_llama.geo.json + manifest")


if __name__ == "__main__":
    main()
