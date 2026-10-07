#!/usr/bin/env python3
"""palace_section_228.py — large cross-sections of the palace model (program 228): roof45 wedges drawn as their real wedge
shape (vertical_half bottom = solid under a slope falling toward cardinal_direction; top = upside-down: solid above, the
underside rising toward cardinal_direction), so the vault and the passage roof can be judged by eye.
Usage: palace_section_228.py OUT.png  (sections: great hall z 63, passage z 40)"""
import sys
sys.path.insert(0, "/home/claude/tools")
from PIL import Image, ImageDraw
import palacegen as PG

S = 14
COLS = {"stone": (150, 150, 155), "plank": (180, 135, 80), "log": (110, 75, 40), "glass": (170, 220, 255), "roof": (130, 85, 50),
        "air": (235, 238, 242), "other": (120, 160, 120), "light": (255, 240, 150)}


def kind(n):
    if n is None or n == "minecraft:air" or n == "minecraft:structure_void": return "air"
    if n.startswith("pw:roof"): return "roof"
    if "glass" in n: return "glass"
    if "log" in n: return "log"
    if "plank" in n or "slab" in n or "stairs" in n: return "plank"
    if "stone" in n or "brick" in n or "cobble" in n: return "stone"
    if "lantern" in n or "light" in n or "torch" in n: return "light"
    return "other"


def section(p, z, x0, x1, f0, f1, title):
    w, h = (x1 - x0 + 1) * S, (f1 - f0 + 1) * S + 24
    im = Image.new("RGB", (w, h), (250, 250, 250))
    d = ImageDraw.Draw(im)
    d.text((4, 4), title, fill=(0, 0, 0))
    for x in range(x0, x1 + 1):
        for f in range(f0, f1 + 1):
            e = p.st.get(x, p.y(f), z)
            n = e[0] if e else None
            st = {k: getattr(v, "value", v) for k, v in (e[1].items() if e else [])}
            X, Y = (x - x0) * S, 24 + (f1 - f) * S
            k = kind(n)
            if k != "roof":
                d.rectangle([X, Y, X + S - 1, Y + S - 1], fill=COLS[k], outline=(200, 200, 205) if k == "air" else (80, 80, 80))
                continue
            d.rectangle([X, Y, X + S - 1, Y + S - 1], fill=COLS["air"], outline=(200, 200, 205))
            cd, half = st.get("minecraft:cardinal_direction", "north"), st.get("minecraft:vertical_half", "bottom")
            low_east = cd == "east"; low_west = cd == "west"
            if "ridge" in n:
                d.polygon([(X, Y + S), (X + S / 2, Y), (X + S, Y + S)], fill=COLS["roof"], outline=(40, 20, 10)); continue
            if not (low_east or low_west):                       # facing along the cut: draw a half block
                d.rectangle([X, Y + S / 2, X + S - 1, Y + S - 1] if half == "bottom" else [X, Y, X + S - 1, Y + S / 2], fill=COLS["roof"]); continue
            if half == "bottom":   # solid below a slope that is LOW on the cardinal side
                pts = [(X, Y + S), (X + S, Y + S), (X + S, Y) if low_west else (X, Y)]
            else:                  # upside-down: solid above, underside HIGH on the cardinal side
                pts = [(X, Y), (X + S, Y), (X + S, Y + S) if low_west else (X, Y + S)]
            d.polygon(pts, fill=COLS["roof"], outline=(40, 20, 10))
    return im


if __name__ == "__main__":
    p = PG.build()
    a = section(p, 63, 60, 84, -1, 30, "great hall, cross-section at z 63 (looking north; x 60..84, feet -1..30)")
    b = section(p, 40, 78, 92, -1, 12, "covered passage, cross-section at z 40 (x 78..92, feet -1..12)")
    out = Image.new("RGB", (a.width + b.width + 20, max(a.height, b.height)), (255, 255, 255))
    out.paste(a, (0, 0)); out.paste(b, (a.width + 20, 0))
    out.save(sys.argv[1])
    print(sys.argv[1], out.size)
