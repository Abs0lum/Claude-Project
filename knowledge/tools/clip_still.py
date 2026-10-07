#!/usr/bin/env python3
"""clip_still.py — one still per (creature, clip, time) from an assembly, textured, side view (camera on the animal's east
side) + front view. Usage: clip_still.py STAGE OUT.png "mob|short|t" ...   (t in seconds of the clip; 'w' = the audit's worst)"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path("/home/claude")
sys.path.insert(0, str(ROOT / "tools"))
import fam_preview as FP  # noqa: E402
import std_convert as S  # noqa: E402
import std_famshare as FS  # noqa: E402
import std_preview as SP  # noqa: E402
import posed_preview as PP  # noqa: E402
import anim_sample as AS  # noqa: E402

SP.W_, SP.H_ = 300, 230


def still(stage, mob, short, t):
    r = FS.Rig(mob, Path(stage))
    aid = r.desc["animations"][short]
    clip = r.an["animations"][aid]
    w, _ = FS.posed(r, clip, t, r.env())
    e = dict(r.env())
    moving = bool(FS.MOVE.search(str(clip.get("anim_time_update", ""))))
    at = t * 2.0 if moving else t
    e.update({"q.anim_time": at, "q.life_time": t, "q.modified_distance_moved": t * 2.0, "q.walk_distance": t * 2.0})
    smp = AS.sample_clip(clip, at, e)
    ch = {b: {k: v for k, v in c.items() if k in ("rotation", "position")} for b, c in smp.items() if b in r.names}
    bones = PP.posed_bones(r.bones, ch, {})
    g = S.jload(r.gf)["minecraft:geometry"][0]
    tw, th = g["description"].get("texture_width", 64), g["description"].get("texture_height", 64)
    tex = FP.tex_of(mob)
    lab = f"{mob.split(':')[1]} {short} t={t:.2f}"
    return [SP.render(bones, tw, th, tex, "east", lab + " east"), SP.render(bones, tw, th, tex, "front", "front")]


if __name__ == "__main__":
    stage, out = sys.argv[1], sys.argv[2]
    rows = []
    for a in sys.argv[3:]:
        mob, short, t = a.split("|")
        tiles = still(stage, mob, short, float(t))
        row = Image.new("RGB", (2 * (SP.W_ + 4), SP.H_), "white")
        for i, im in enumerate(tiles):
            row.paste(im, (i * (SP.W_ + 4), 0))
        rows.append(row)
    img = Image.new("RGB", (rows[0].width * 2 + 8, ((len(rows) + 1) // 2) * (SP.H_ + 4)), "white")
    for i, r in enumerate(rows):
        img.paste(r, ((i % 2) * (rows[0].width + 8), (i // 2) * (SP.H_ + 4)))
    ImageDraw.Draw(img)
    img.save(out)
    print(out, img.size)
