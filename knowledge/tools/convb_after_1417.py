#!/usr/bin/env python3
"""after-sheet for RP-07 1.4.17 (NEW) vs 1.4.16 (OLD) — floor = ground; columns as convb_after_sheet.py."""
import sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import convb_after_sheet as S
from build_rp07_1417 import CFG
from PIL import Image, ImageDraw
S.OLD, S.NEW = CFG["src"], CFG["dst"]; S.LOOK_STEMS = set(CFG["look"]); S.NEW_V, S.OLD_V = "1.4.17", "1.4.16"
rows = []
for label, stem, gkey, jname, tkey in CFG["jobs"]:
    rows.append(S.row_for(label, stem, gkey)); print("row", label)
head = Image.new("RGB", (rows[0].width, 44), (20, 24, 32))
ImageDraw.Draw(head).text((10, 10), "RP-07 1.4.17 — Converter B round 3 (blue = new, green = new looking left, red = 1.4.16) · floor = ground · 2026-09-28", fill=(255, 255, 255), font=S.FT)
for part in range(0, len(rows), 4):
    chunk = rows[part:part + 4]
    sheet = Image.new("RGB", (rows[0].width, 44 + sum(r.height + 6 for r in chunk)), (255, 255, 255)); sheet.paste(head, (0, 0)); y = 50
    for r in chunk: sheet.paste(r, (0, y)); y += r.height + 6
    sheet.save(S.OUT / f"after_1417_{part // 4 + 1}.png"); print("sheet", part // 4 + 1)
