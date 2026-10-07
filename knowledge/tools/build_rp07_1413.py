#!/usr/bin/env python3
"""build_rp07_1413.py — RP-07 v1.4.13 (D-C262, Abs0lum 22:42 "fix this immediately. Look for similar issues and fix them as well").
RP-07 1.4.12 sits ABOVE RP-06 in his world order and still ships 64x VANILLA copies of nine hostile-mob textures and nine
vanilla-id hostile geometries on the same paths where RP-06 1.4.7 carries 512x Patrix textures and its own geometry files;
it also ships a 64x768 vanilla campfire_smoke.png over RP-02 2.0.5's Patrix 128x1536 big-smoke strip.  A higher pack's
same-path file replaces the lower pack's outright (L-ENT-SHADOW), so hostile mobs and campfire smoke draw vanilla today.
v1.4.13 deletes exactly those 19 files.  Every one of them is DIFFERENT from the RP-06/RP-02 copy (the identical shared
files that RP-06's 1.4.6 de-triplication left to RP-07 are NOT touched — RP-06 depends on them).  Nothing else changes."""
import json, os, shutil, time
from pathlib import Path
ROOT = Path("/home/claude"); SRC, DST, VER, DATE = ROOT / "_build/rp07-1412", ROOT / "_build/rp07-1413", "1.4.13", "2026-09-27"
PURGE = ["models/entity/drowned.geo.json", "models/entity/evoker.geo.json", "models/entity/husk.geo.json", "models/entity/pillager.geo.json",
         "models/entity/skeleton.geo.json", "models/entity/stray.geo.json", "models/entity/vindicator.geo.json", "models/entity/witch.geo.json",
         "models/entity/zombie.geo.json",
         "textures/entity/creeper/creeper.png", "textures/entity/creeper/creeper_armor.png", "textures/entity/illager/evoker.png",
         "textures/entity/illager/pillager.png", "textures/entity/illager/ravager.png", "textures/entity/skeleton/skeleton.png",
         "textures/entity/skeleton/stray_overlay.png", "textures/entity/zombie/husk.png", "textures/entity/zombie/zombie.png",
         "textures/particle/campfire_smoke.png"]
def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f: f.write(f"[{time.strftime('%H:%M')} CT 09-27] BUILD {m}\n")
if DST.exists(): shutil.rmtree(DST)
shutil.copytree(SRC, DST)
removed = []
for rel in PURGE:
    p = DST / rel
    if not p.exists(): raise SystemExit(f"expected file missing in 1.4.12: {rel}")
    p.unlink(); removed.append(rel)
tl = DST / "textures/textures_list.json"
if tl.exists():
    lst = json.loads(tl.read_text(encoding="utf-8-sig")); stems = {r[:-4] for r in removed if r.endswith(".png")} | set(removed)
    new = [x for x in lst if x not in stems]; tl.write_text(json.dumps(new, indent=1), encoding="utf-8"); pruned = len(lst) - len(new)
else: pruned = 0
man = json.loads((DST / "manifest.json").read_text(encoding="utf-8")); v = [1, 4, 13]
man["header"]["version"] = v; man["modules"][0]["version"] = v; man["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"
man["header"]["description"] = (f"v{VER} ({DATE}) HOSTILE-LEFTOVER PURGE (D-C262): the nine 64x vanilla hostile textures (creeper, creeper_armor, evoker, pillager, "
                                "ravager, skeleton, stray_overlay, husk, zombie) and nine vanilla-id hostile geometry files (drowned/evoker/husk/pillager/skeleton/stray/"
                                "vindicator/witch/zombie) that shadowed RP-06's 512x Patrix files, plus the 64x768 vanilla campfire_smoke.png that shadowed RP-02's "
                                "Patrix smoke strip, are removed. Everything else byte-identical to v1.4.12 (the P0 wiring build).")
(DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
json.dump({"removed": removed, "textures_list_pruned": pruned}, open(ROOT / "_logs/rp07_1413_build_report.json", "w"), indent=1)
log(f"RP-07 v{VER}: {len(removed)} hostile/campfire leftovers removed, textures_list pruned {pruned}, manifest stamped -> {DST}")
