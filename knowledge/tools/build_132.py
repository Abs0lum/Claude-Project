#!/usr/bin/env python3
"""build_132.py — RP-04 v1.3.131 -> v1.3.132: BED textures re-laid to the Bedrock engine layout (option A).

Witness 2026-09-22 13:50 (Abs0lum, 3/3 frames): the Patrix Java-layout bed textures on the engine's one-box
bed (geometry.bed in vanilla models/mobs.json) show a see-through slot at the seam, a 10-row foot half, no
footboard and blanket-textured legs.  Ruling 14:16: A (re-lay the textures), B (geometry override) kept as a
fallback kit.  Change set: textures/entity/bed/<16 colours>.png rewritten in place + silver.png added (the
Bedrock name for light gray) + manifest + ledger.  Everything else byte-identical to .131.
"""
import json, shutil, datetime
from pathlib import Path
import sys
sys.path.insert(0, "/home/claude/tools")
from PIL import Image
from bed_relayout import relayout

ROOT = Path("/home/claude")
SRC, DST = ROOT / "_build/rp04-131", ROOT / "_build/rp04-132"
VER = "1.3.132"; DATE = "2026-09-22"
LOG = ROOT / "_logs/phase_log.md"
COLOURS = ["black", "blue", "brown", "cyan", "gray", "green", "light_blue", "lime", "magenta", "orange", "pink", "purple", "red", "white", "yellow"]
def log(m): LOG.open("a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD 132 — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    bed = DST / "textures/entity/bed"
    for c in COLOURS:
        relayout(Image.open(SRC / f"textures/entity/bed/{c}.png")).save(bed / f"{c}.png", optimize=True)
    # Bedrock names light gray "silver"; Patrix ships light_gray.png (a dead path in Bedrock) -> add silver.png
    relayout(Image.open(SRC / "textures/entity/bed/light_gray.png")).save(bed / "silver.png", optimize=True)
    man = jload(DST / "manifest.json")
    man["header"]["name"] = f"AbsolutRealism Basic RP v{VER}"
    man["header"]["description"] = (f"v{VER} ({DATE}) BED RE-LAYOUT (option A). The engine's bed is ONE 16x32x6 box (geometry.bed, models/mobs.json) "
        f"reading a 32-row mattress strip; Patrix ships Java's two-piece layout with 6 rows of end faces between the pieces "
        f"-> see-through slot at the seam, 10-row foot half, no footboard, blanket legs (witness 13:50). All 16 bed textures "
        f"re-laid to the engine layout (foot sides row -> rows 22..38, footboard -> the foot-end square, legs -> the engine leg "
        f"slots, rails transparent) + silver.png added (Bedrock's name for light gray). Textures/manifest/ledger only; every other "
        f"file byte-identical to v1.3.131. Pair with BP-02 v1.3.182 + RP-02 v2.0.3.")
    man["header"]["version"] = [1, 3, 132]
    for m in man["modules"]: m["version"] = [1, 3, 132]
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; t = led.read_text(encoding="utf-8"); t2 = t.replace("v1.3.131 ·", f"v{VER} ·", 1); assert t2 != t; led.write_text(t2, encoding="utf-8")
    log("tree rp04-132 built: 16 bed textures re-laid + silver.png, manifest + ledger stamped")

if __name__ == "__main__":
    main()
