#!/usr/bin/env python3
"""equine_after_sheet.py — the round-4 preview: per equine, PATRIX (target) | NEW (RP-07 1.4.15 / RP-06 1.4.10, in game at rest)
| OLD (1.4.14 / 1.4.9 in game, what his shots showed) — side and front, same cameras. Output _docs/equine/equine_after.png"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw
sys.path.insert(0, "/home/claude/tools")
import equine_compare as ec
from equine_sheet import cam, tile, W, H, FT
from entity_tex_render import render_entity

ROOT = Path("/home/claude")
NEW = {"horse": "_build/rp07-1415", "donkey": "_build/rp07-1415", "mule": "_build/rp07-1415", "zombie_horse": "_build/rp06-1410", "skeleton_horse": "_build/rp06-1410"}


def main():
    rows = []
    for mob in ec.MOBS:
        pb, ptw, pth = ec.patrix_bones(mob)
        ob, otw, oth = ec.our_bones(mob)
        old_abs = {n: [0, 0, 0] for n in ec.MOBS[mob][4]}
        rp, geo, ident, ent, heads = ec.MOBS[mob]
        ec.MOBS[mob] = (NEW[mob], geo, ident, ent, [])
        nb, ntw, nth = ec.our_bones(mob); tex = ec.texture(mob)
        ec.MOBS[mob] = (rp, geo, ident, ent, heads)
        pf = ec.posed_faces(pb, ptw, pth, ec.bone_affines(pb))
        nf = ec.posed_faces(nb, ntw, nth, ec.bone_affines(nb))
        of = ec.posed_faces(ob, otw, oth, ec.bone_affines(ob, abs_rot=old_abs))
        view = "east" if mob == "donkey" else "west"
        e, t = cam(view); ef, tf = cam("front", 64)
        name = mob.replace("_", " ").upper()
        cells = [tile(render_entity(pf, tex, e, t, W, H, fov=60, floor_y=0), f"{name} — PATRIX (target)", "Java: Patrix model + FreshLX rest pose", (22, 90, 52)),
                 tile(render_entity(nf, tex, e, t, W, H, fov=60, floor_y=0), f"{name} — NEW (this round)", "RP-07 1.4.15 / RP-06 1.4.10, in game at rest", (30, 70, 140)),
                 tile(render_entity(of, tex, e, t, W, H, fov=60, floor_y=0), f"{name} — OLD", "what your 09-28 shots showed", (130, 30, 30)),
                 tile(render_entity(pf, tex, ef, tf, W, H, fov=60, floor_y=0), "PATRIX — front", "", (22, 90, 52)),
                 tile(render_entity(nf, tex, ef, tf, W, H, fov=60, floor_y=0), "NEW — front", "", (30, 70, 140))]
        row = Image.new("RGB", (len(cells) * (W + 6) - 6, H), (255, 255, 255))
        for i, c in enumerate(cells): row.paste(c, (i * (W + 6), 0))
        rows.append(row)
    head = Image.new("RGB", (rows[0].width, 56), (20, 24, 32))
    ImageDraw.Draw(head).text((12, 12), "EQUINES — Patrix target (green) · NEW this round (blue) · OLD (red) · 2026-09-28", fill=(255, 255, 255), font=FT)
    sheet = Image.new("RGB", (rows[0].width, 56 + sum(r.height + 8 for r in rows)), (255, 255, 255)); sheet.paste(head, (0, 0)); y = 62
    for r in rows: sheet.paste(r, (0, y)); y += r.height + 8
    out = ROOT / "_docs/equine/equine_after.png"; sheet.save(out); print(out, sheet.size)


if __name__ == "__main__":
    main()
