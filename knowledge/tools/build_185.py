#!/usr/bin/env python3
"""build_185.py — BP-02 v1.3.185: the room-smoke wall test (D-C228, Abs0lum 20:51 "Fix the found along the way").
BP-02 v1.3.184 + scripts/pw_homestead.js + scripts/pw_homestead_logic.js from tools/homestead_src (roomFor now uses
L.floodRoom + L.smokePasses — stable API — instead of the beta-only Block.isSolid) + manifest + ledger stamp.
Everything else byte-identical.  RP side unchanged (still pairs with RP-04 v1.3.138 + RP-02 v2.0.4)."""
import json, shutil, datetime
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST = ROOT / "_build/bp02-184", ROOT / "_build/bp02-185"; VER = "1.3.185"; DATE = "2026-09-22"
HS = ROOT / "tools/homestead_src"
def log(m):
    print(m); open(ROOT / "_logs/phase_log.md", "a").write(f"[{datetime.datetime.now().strftime('%H:%M')} CT 09-22] BUILD BP-02 {VER} — {m}\n")
def jload(p): return json.loads(Path(p).read_text(encoding="utf-8-sig"))
def jdump(o, p): Path(p).write_text(json.dumps(o, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    for f in ("pw_homestead.js", "pw_homestead_logic.js"):
        shutil.copy(HS / f, DST / "scripts" / f)
    log("scripts/pw_homestead.js + pw_homestead_logic.js <- tools/homestead_src (roomFor -> L.floodRoom + L.smokePasses; no Block.isSolid)")
    man = jload(DST / "manifest.json"); vv = [int(x) for x in VER.split(".")]
    man["header"]["name"] = f"AbsolutRealism Tectonic BP v{VER}"; man["header"]["version"] = vv
    for m in man["modules"]: m["version"] = vv
    man["header"]["description"] = (f"v{VER} ({DATE}) ROOM SMOKE WORKS (D-C228, Abs0lum 20:51 'fix the found along the way'): the hearth's room test used Block.isSolid, "
        "which the stable @minecraft/server 2.0.0 this pack pins does not have (beta only) — every wall read 'not solid', every room 'open', so a blocked chimney "
        "never filled the room with smoke. Now: walls = any block except air, OPEN doors/trapdoors/fence gates, thin fittings (torches, carpets, signs, rails, "
        "buttons, plates, banners, candles, lanterns, frames, ladders, vines, redstone, snow layers, pots, rods, chains, heads), furniture, rafters and old marker "
        "blocks; the manhole passes only while open. 21 unit tests incl. the regression. Everything else byte-identical to v1.3.184. "
        "Requires RP-04 v1.3.138 (furniture geometry / iron / seat entity); pair with RP-02 v2.0.4.")
    jdump(man, DST / "manifest.json")
    led = DST / "PW-DEPENDENCIES.md"; t = led.read_text(encoding="utf-8"); assert "v1.3.184 ·" in t
    led.write_text(t.replace("v1.3.184 ·", f"v{VER} ·", 1), encoding="utf-8")
    log(f"manifest + ledger stamp v{VER}")

if __name__ == "__main__":
    main()
