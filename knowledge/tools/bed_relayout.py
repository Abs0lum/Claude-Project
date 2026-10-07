#!/usr/bin/env python3
"""bed_relayout.py — Java (Patrix) bed texture -> Bedrock engine layout (geometry.bed, models/mobs.json).

Java BedModel layout (64-grid):  head piece 16x16x6 at uv (0,0)  -> ends rows 0..6, sides row 6..22
                                 foot piece 16x16x6 at uv (0,22) -> ends rows 22..28, sides row 28..44
                                 legs 3x3x3 at uv (50,0) (50,6) (50,12) (50,18)  (12x6 unwraps)
Bedrock geometry.bed:            ONE box 16x32x6 at uv (0,0)     -> ends rows 0..6, sides row 6..38 (32 rows)
                                 legs 3x3x3 at uv (0,38) (12,38) (0,44) (12,44)
                                 4 rail boxes at uv (38,2) (38,38) (52,6) (44,6) — must stay transparent

Both layouts share the face conventions (checked on vanilla red.png and Patrix orange.png, 2026-09-22):
side strips wood u0..3 / blanket u3..6 (mirrored on the right strip), end faces v grows upward on BOTH end
squares, top strip v grows head -> foot.  So the re-layout is pure region copying — no flips.

Region moves (64-grid units, x scale s for a 64*s texture):
  keep   [0,44] x [0,6]   head end (u 6..22) — but the foot-end square [22,38] x [0,6] is EMPTY in Patrix
  keep   [0,44] x [6,22]  head sides row
  move   [0,44] x [28,44] -> [0,44] x [22,38]   foot sides row becomes mattress rows 16..32
  move   [22,38] x [22,28] -> [22,38] x [0,6]   the footboard end face into the engine's foot-end square
  move   legs (50,0)(50,6)(50,12)(50,18) 12x6 -> (0,38)(12,38)(0,44)(12,44)
  clear  everything else (rails read u 38..64 rows 2..6, u 38..64 rows 38..42, u 44..60 rows 6..35)
"""
from pathlib import Path
from PIL import Image

MOVES = [((0, 0, 44, 6), (0, 0)), ((0, 6, 44, 22), (0, 6)), ((0, 28, 44, 44), (0, 22)), ((22, 22, 38, 28), (22, 0)),
         ((50, 0, 62, 6), (0, 38)), ((50, 6, 62, 12), (12, 38)), ((50, 12, 62, 18), (0, 44)), ((50, 18, 62, 24), (12, 44))]

def relayout(src: Image.Image) -> Image.Image:
    src = src.convert("RGBA")
    assert src.width == src.height and src.width % 64 == 0, src.size
    s = src.width // 64
    out = Image.new("RGBA", src.size, (0, 0, 0, 0))
    for (u0, v0, u1, v1), (du, dv) in MOVES:
        out.paste(src.crop((u0 * s, v0 * s, u1 * s, v1 * s)), (du * s, dv * s))
    # the engine's foot-end square was filled from the footboard above; the Patrix foot-end row 22..28 is not kept
    # (nothing reads it), and the Java seam-face squares are empty in the source so nothing else needs clearing.
    return out

if __name__ == "__main__":
    import sys
    relayout(Image.open(sys.argv[1])).save(sys.argv[2])
