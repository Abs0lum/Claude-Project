#!/usr/bin/env python3
"""build_rp07_1414.py — RP-07 Neutral Mobs RP v1.4.14 (D-C267): the two vanilla .tga skins that out-ranked RP-06's Patrix skins.

The 09-28 witness (p1 h03 drowned, h06 stray) showed the VANILLA skins although RP-06 is the only pack defining those entities
and the only pack holding textures/entity/zombie/drowned.png (512x512 Patrix) and skeleton/stray.png (512x256 Patrix).
Cause: RP-07 — above RP-06 in the stack — still holds textures/entity/zombie/drowned.tga (64x64 vanilla) and
textures/entity/skeleton/stray.tga (64x32 vanilla). A texture reference has no extension; the top pack that holds the stem in
ANY extension wins, so RP-07's .tga drew. v1.4.13's hostile purge matched .png files only and missed them.
v1.4.14 deletes exactly those two files. Nothing else changes (verify_rp07_1414.py asserts the diff).
RP-07's other 29 .tga files (cat *_tame x12, enderman, zombie_piglin, zombie_villager2 professions x15, spider) are vanilla copies
with no cross-pack collision; they go to the ownership wave (spider.tga sits beside RP-07's own spider.png - a wave item)."""
import json, shutil, time
from pathlib import Path

ROOT = Path("/home/claude")
SRC, DST, VER, DATE = ROOT / "_build/rp07-1413", ROOT / "_build/rp07-1414", "1.4.14", "2026-09-28"
PURGE = ["textures/entity/zombie/drowned.tga", "textures/entity/skeleton/stray.tga"]


def log(m):
    print(m)
    with open(ROOT / "_logs/phase_log.md", "a") as f:
        f.write(f"[{time.strftime('%H:%M')} CT 09-28] BUILD {m}\n")


def main():
    if DST.exists(): shutil.rmtree(DST)
    shutil.copytree(SRC, DST)
    for rel in PURGE:
        p = DST / rel
        if not p.exists(): raise SystemExit(f"expected file missing in 1.4.13: {rel}")
        p.unlink()
    tl = DST / "textures/textures_list.json"
    if tl.exists():
        lst = json.loads(tl.read_text(encoding="utf-8-sig"))
        stems = {r.rsplit(".", 1)[0] for r in PURGE}
        kept = [x for x in lst if x.rsplit(".", 1)[0] not in stems and x not in stems]
        if len(kept) != len(lst): tl.write_text(json.dumps(kept, indent=1), encoding="utf-8")
    man = json.loads((DST / "manifest.json").read_text(encoding="utf-8-sig")); v = [int(x) for x in VER.split(".")]
    man["header"]["version"] = v
    for m in man["modules"]: m["version"] = v
    man["header"]["name"] = f"AbsolutRealism Neutral Mobs RP v{VER}"
    man["header"]["description"] = (
        f"v{VER} ({DATE}) TWO VANILLA SKINS REMOVED (D-C267): textures/entity/zombie/drowned.tga and skeleton/stray.tga (64 px vanilla) sat above "
        "RP-06's 512 px Patrix drowned and stray skins at the same path and won (a texture path has no extension: the top pack holding it in any "
        "format wins). v1.4.13's purge matched .png only. Everything else byte-identical to v1.4.13.")
    (DST / "manifest.json").write_text(json.dumps(man, indent=1), encoding="utf-8")
    log(f"RP-07 v{VER}: removed {', '.join(PURGE)} -> {DST}")


if __name__ == "__main__":
    main()
