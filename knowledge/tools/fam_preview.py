#!/usr/bin/env python3
"""fam_preview.py — look at family candidates (P9): per candidate a row of 3 moments (25 / 50 / 75 % of the clip), the SOURCE animal
with its own clip on the left half, the TARGET with the retargeted fam_<kind> copy on the right half; side view (camera on the
animal's east side), textured. Usage: fam_preview.py OUT.png "target_id:kind" ["target_id:kind" …]"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import anim_sample as AS  # noqa: E402
import posed_preview as PP  # noqa: E402
import std_convert as S  # noqa: E402
import std_famshare as FS  # noqa: E402
import std_preview as SP  # noqa: E402

SP.W_, SP.H_ = 220, 190
STAGE = ROOT / "_staging/assembled"
PACKS = [S.Pack(ROOT / "_build" / n) for n in ("rp07-1443", "rp06-1428")]


def tex_of(mob):
    import re
    for P in PACKS:
        if mob in P.entities:
            d = dict(P.entities[mob][1])
            d["textures"] = {k: re.sub(r"\.(png|tga)$", "", v) if isinstance(v, str) else v for k, v in (d.get("textures") or {}).items()}
            return SP.texture_of(P, d)
    raise KeyError(mob)


def frames(rig, clip, env, label, tex, scale=1.0):
    out = []
    L = AS.clip_length(clip)
    g = S.jload(rig.gf)["minecraft:geometry"][0]
    tw, th = g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
    for f in (0.25, 0.5, 0.75):
        e = dict(env)
        e.update({"q.anim_time": L * f, "q.life_time": L * f, "q.modified_distance_moved": L * f})
        smp = AS.sample_clip(clip, L * f, e)
        ch = {b: {k: v for k, v in c.items() if k in ("rotation", "position")} for b, c in smp.items() if b in rig.names}
        bones = PP.posed_bones(rig.bones, ch, {})
        out.append(SP.render(bones, tw, th, tex, "east", f"{label} {int(f * 100)}%"))
    return out


def row(target, kind):
    rows = json.loads((ROOT / "_docs/standard/FAMILY-SHARING.json").read_text())
    r = next(x for x in rows if x["to"] == target and x["kind"] == kind and x["offered"])
    src, tgt = FS.Rig(r["from"], STAGE), FS.Rig(target, STAGE)
    aid = src.desc["animations"][r["from_clip"]]
    res, why = FS.try_retarget(src, tgt, kind, r["from_clip"], aid)
    assert res, why
    c2 = res[0]
    a = frames(src, src.an["animations"][aid], src.env(), f"{r['from'].split(':')[1]} {r['from_clip']}", tex_of(r["from"]))
    b = frames(tgt, c2, tgt.env(), f"{target.split(':')[1]} fam_{kind}", tex_of(target))
    img = Image.new("RGB", (6 * (SP.W_ + 2) + 8, SP.H_), "white")
    for i, t in enumerate(a + b):
        img.paste(t, (i * (SP.W_ + 2) + (8 if i >= 3 else 0), 0))
    ImageDraw.Draw(img).rectangle([3 * (SP.W_ + 2), 0, 3 * (SP.W_ + 2) + 6, SP.H_], fill=(40, 40, 40))
    return img


if __name__ == "__main__":
    rows = [row(*a.rsplit(":", 1)) for a in sys.argv[2:]]
    out = Image.new("RGB", (rows[0].width, len(rows) * (SP.H_ + 3)), "white")
    for i, r in enumerate(rows):
        out.paste(r, (0, i * (SP.H_ + 3)))
    out.save(sys.argv[1])
    print(out.size)
