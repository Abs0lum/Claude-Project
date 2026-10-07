#!/usr/bin/env python3
"""size_rule.py — D-C284: the real-size RELATIONSHIP for the passive + neutral mobs our resource packs draw (his 12:40 rulings:
the 09-27 curve, "whatever you recommend"; his character = 5'10" is the yardstick; option (a): size through the resource pack
only, hitboxes stay vanilla — hostile mobs later, with their hitboxes).

THE CURVE (the 09-27 StripMine rule, re-anchored on his character):
  the player is drawn 1.875 blocks tall (32 px model x 0.9375) = 5'10" = 1.778 m  ->  K = 1.875 / 1.778 = 1.0546 blocks per metre
  real >= 0.60 m : blocks = K x real                                    (true scale)
  real <  0.60 m : blocks = 0.22 + (0.60 K - 0.22) x ln(real / 1 cm) / ln(60)   (the log ramp: a 1-cm ant stays visible at 0.22)
WHAT IS MEASURED (visible_size.py: only texels the game draws, conditional parts left out):
  mammals: head-body length (nose to rump; tails left out — their rest pose is not the pose you see, and zoology quotes
           head-body without the tail) · fish / amphibians / insects: total length · the chicken: standing height
REAL SIZES: typical adult figures (head-body for mammals) — see REAL below with the range each was taken from.
WHO CHANGES NOW: every mob under 0.60 m real (the "smaller mobs" of his 11:41 note) + fox / wolf / sheep (his in-game note).
  Changes smaller than 8 % are left alone; growth is capped at x1.20 (the 09-27 rule). Larger mobs wait for option (b): a
  visual enlargement without a matching hitbox would poke through fences and walls.
API: game_blocks(real_m), plan(pack, stack) -> rows"""
import math, re, sys
from pathlib import Path
sys.path.insert(0, "/home/claude/tools")
import visible_size as V
import molang_lint as ML

K = 1.875 / 1.778
R0, RMIN, FLOOR = 0.60, 0.01, 0.22
DEADBAND, MAX_UP = 0.08, 1.20
TAIL = r"tail"

# stem: (real metres, what is measured, the range / source basis)
REAL = {
    "bee":          (0.015, "total", "honey bee worker 12-15 mm"),
    "axolotl":      (0.23,  "total", "axolotl 15-45 cm, typically 23 cm (his 9 in)"),
    "tadpole":      (0.05,  "total", "frog tadpoles 2.5-7 cm before the legs"),
    "frog":         (0.10,  "total", "temperate / cold / warm frogs 6-12 cm snout-vent"),
    "pufferfish":   (0.35,  "total", "pufferfish (Takifugu) 20-50 cm"),
    "tropicalfish": (0.15,  "total", "reef fish (clownfish, tangs) 10-20 cm"),
    "chicken":      (0.45,  "height", "hen standing 40-50 cm to the comb"),
    "rabbit":       (0.40,  "head-body", "European rabbit 34-50 cm"),
    "cat":          (0.46,  "head-body", "house cat 40-50 cm"),
    "ocelot":       (0.75,  "head-body", "ocelot 55-100 cm"),
    "fox":          (0.65,  "head-body", "red fox 46-90 cm"),
    "wolf":         (1.43,  "head-body", "grey wolf 105-160 cm; 1.43 = his R8 b15 'a little bigger' (+10 %, D-C285)"),
    "sheep":        (1.20,  "head-body", "domestic sheep 120-180 cm (Merino-type 120-150); 1.20 = his R8 b15 'a tiny bit smaller' (-7.7 %, D-C285)"),
}


def game_blocks(real):
    if real >= R0: return K * real
    return FLOOR + (R0 * K - FLOOR) * math.log(max(real, RMIN) / RMIN) / math.log(R0 / RMIN)


def current(pack, stem, stack, what):
    if what == "head-body":
        m = V.measure(pack, stem, stack, exclude=TAIL); return m["l"], m
    m = V.measure(pack, stem, stack)
    return (m["h"] if what == "height" else max(m["l"], m["w"], m["h"])), m


def plan(pack, stack, force=()):
    """force = stems his witness asked to change (D-C285 b15: wolf 'a little bigger', sheep 'a tiny bit smaller'): the 8 % deadband
    (meant to stop churn from measurement noise) does not apply to an explicit request."""
    rows = []
    for stem, (real, what, basis) in REAL.items():
        cur, m = current(pack, stem, stack, what)
        target = game_blocks(real); raw = target / cur
        # D-C285: the x1.20 growth cap is on the MODEL's original size (client scale 1.0), not per round — 1.4.21 took the
        # pufferfish to 1.2 and a re-plan would have compounded it to 1.44
        f = min(raw, max(1.0, MAX_UP / float(m["client_scale"] or 1.0))) if raw > 1 else raw
        keep = abs(f - 1.0) < (0.005 if stem in force else DEADBAND)
        act = ("keep (within 8 %)" if keep else ("grow" + (" (capped x1.20)" if raw > f + 1e-9 else "") if f > 1 else "shrink")
               + (" (his request)" if stem in force else ""))
        if act.startswith("keep"): f = 1.0
        rows.append({"stem": stem, "real_m": real, "measured": what, "basis": basis, "current_blocks": round(cur, 3),
                     "target_blocks": round(target, 3), "factor": round(f, 3), "action": act, "old_client_scale": m["client_scale"],
                     "new_client_scale": round(m["client_scale"] * f, 3)})
    return rows


def scaled_script(old, factor):
    """the client entity's scripts.scale times the factor, keeping a baby ternary intact."""
    if old is None: return f"{factor:.3f}"
    if isinstance(old, (int, float)): return f"{float(old) * factor:.3f}"
    s = str(old).strip()
    try: return f"{float(s.rstrip('f')) * factor:.3f}"
    except ValueError: return f"({s}) * {factor:.3f}"


if __name__ == "__main__":
    R7 = Path("/home/claude/_build/rp07-1420")
    st = [Path("/home/claude/_build/rp08-148"), Path("/home/claude/_build/rp06-1415"), Path("/home/claude/_build/rp05-51")]
    print(f"K = {K:.4f} blocks per metre (5'10\" = 1.875 blocks)")
    for r in plan(R7, st):
        print(f"{r['stem']:12} real {r['real_m']:5.3f} m ({r['measured']:9}) now {r['current_blocks']:5.2f} blk -> {r['target_blocks']:5.2f} "
              f"x{r['factor']:5.3f} {r['action']:22} client scale {r['old_client_scale']} -> {r['new_client_scale']}")
